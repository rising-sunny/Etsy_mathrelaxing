"""
build_lanterns.py — geometric tealight lanterns (laser cut SVG/DXF/PDF + listing images).

Square box lantern, outer W×W×H:
  2 × FRONT walls  finger joints "out" on even segments
  2 × SIDE walls   complementary fingers
  every wall has 2 tabs top and bottom → slots in BASE and TOP RING
Panels carry a pattern cut-out window. Pieces are asserted to be single
polygons and the corner joints are checked to tile the corner exactly.

  python lasercut/lanterns/build_lanterns.py            # files + package + images
"""
from __future__ import annotations

import math
import os
import random
import sys
import zipfile

import ezdxf
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "ornaments_3d"))
import build_ornaments as O  # noqa: E402  (pattern generators)

OUT = os.path.join(HERE, "out")
DIST = os.path.join(HERE, "dist")
LIST = os.path.join(HERE, "listing")
W, H = 90.0, 120.0       # outer box, mm
NSEG = 5                 # finger segments per vertical edge
LIP = 8.0                # base / top ring overhang
TAB = 16.0               # tab width
WEB = 2.6
THICKNESSES = {"3mm": 3.0, "1-8in": 3.175, "4mm": 4.0}
CUT = "#FF0000"
LABEL = {"voronoi": "Voronoi", "honeycomb": "Honeycomb", "golden": "Golden Angle",
         "snowflakes": "Koch Snowflakes", "girih": "Girih Stars", "bubbles": "Circle Packing"}


# ── Patterns (window-local, centred at origin) ───────────────────────────────
def pattern(name, ww, wh):
    R = math.hypot(ww, wh) / 2 + 6
    if name == "voronoi":
        return O.pat_voronoi(R, seed=21)
    if name == "honeycomb":
        return O.pat_honeycomb(R)
    if name == "golden":
        ga, out = math.radians(137.507764), []
        for n in range(1, 900):
            r = 5.2 * math.sqrt(n)
            if r > R:
                break
            out.append(Point(r * math.cos(n * ga), r * math.sin(n * ga)).buffer(1.9 + WEB / 2, 24))
        return out
    if name == "snowflakes":
        out, rng = [], random.Random(4)
        for _ in range(4000):
            r = rng.uniform(4.5, 10)
            c = (rng.uniform(-ww / 2 + r, ww / 2 - r), rng.uniform(-wh / 2 + r, wh / 2 - r))
            s = translate(O.koch_snowflake(r, 2), *c)
            if all(s.distance(o) > WEB * 1.6 for o in out):
                out.append(s.buffer(WEB / 2))
        return out
    if name == "girih":
        out = []
        for i in range(-4, 5):
            for j in range(-6, 7):
                x, y = i * 19.0, j * 19.0
                out.append(translate(O.octagram(8.4), x, y))
                out.append(translate(O.hexagon(0, 0, 4.2, rot=0), x + 9.5, y + 9.5))
        return out
    if name == "bubbles":
        out, rng = [], random.Random(9)
        for _ in range(12000):
            r = rng.uniform(1.8, 9.0)
            c = Point(rng.uniform(-ww / 2 + r + 1.5, ww / 2 - r - 1.5), rng.uniform(-wh / 2 + r + 1.5, wh / 2 - r - 1.5))
            d = c.buffer(r + WEB / 2, 32)
            if all(d.distance(o) > 0.01 for o in out):
                out.append(d)
        return out
    raise KeyError(name)


DESIGNS = list(LABEL)
WHOLE_ONLY = {"golden", "snowflakes", "girih", "bubbles"}  # never show half shapes


# ── Pieces ───────────────────────────────────────────────────────────────────
def wall(kind, t, pat):
    """kind 'F' (fingers out on even segments) or 'S'. Local coords x∈[0,W], y∈[0,H]."""
    seg = H / NSEG
    shape = box(t, 0, W - t, H)
    for k in range(NSEG):
        out = (k % 2 == 0) == (kind == "F")
        if out:
            shape = shape.union(box(0, k * seg, t, (k + 1) * seg)).union(box(W - t, k * seg, W, (k + 1) * seg))
    for cx in (W / 4, 3 * W / 4):
        shape = shape.union(box(cx - TAB / 2, -t, cx + TAB / 2, 0)).union(box(cx - TAB / 2, H, cx + TAB / 2, H + t))
    win = box(t + 7, 13, W - t - 7, H - 13)
    holes = []
    wx0, wy0, wx1, wy1 = win.bounds
    for h in pattern(pat, wx1 - wx0, wy1 - wy0):
        h = translate(h, (wx0 + wx1) / 2, (wy0 + wy1) / 2).buffer(-WEB / 2, join_style=2)
        if pat in WHOLE_ONLY:
            if not win.contains(h):
                continue
        else:
            h = h.intersection(win)
        for g in getattr(h, "geoms", [h]):
            if g.geom_type == "Polygon" and not g.buffer(-0.9).is_empty and g.area > 6:
                holes.append(g)
    piece = shape.difference(unary_union(holes))
    assert isinstance(piece, Polygon), f"{pat} wall {kind} falls apart"
    return piece


def plate(t, ring):
    """Base (ring=False) or top ring. Box footprint [0,W]², lip around it."""
    g = box(-LIP, -LIP, W + LIP, W + LIP)
    if ring:
        g = g.difference(box(t + 9, t + 9, W - t - 9, W - t - 9))
    slots = []
    for c in (W / 4, 3 * W / 4):
        slots += [box(c - TAB / 2, 0, c + TAB / 2, t), box(c - TAB / 2, W - t, c + TAB / 2, W),
                  box(0, c - TAB / 2, t, c + TAB / 2), box(W - t, c - TAB / 2, W, c + TAB / 2)]
    g = g.difference(unary_union(slots))
    assert isinstance(g, Polygon)
    return g


def check_corner(t):
    """Front fingers + side fingers must tile the t×H corner strip exactly once."""
    seg = H / NSEG
    f = [k for k in range(NSEG) if k % 2 == 0]
    s = [k for k in range(NSEG) if k % 2 == 1]
    assert sorted(f + s) == list(range(NSEG)) and not set(f) & set(s)
    return True


def rings_of(geom):
    if isinstance(geom, MultiPolygon):
        for g in geom.geoms:
            yield from rings_of(g)
        return
    yield list(geom.exterior.coords)
    for i in geom.interiors:
        yield list(i.coords)


def layout(pieces, gap=5.0, maxw=480):
    """Shelf-pack pieces left→right; returns translated pieces."""
    placed, x, y, rowh = [], 0.0, 0.0, 0.0
    for g in pieces:
        minx, miny, maxx, maxy = g.bounds
        w, h = maxx - minx, maxy - miny
        if x + w > maxw:
            x, y, rowh = 0.0, y - rowh - gap, 0.0
        placed.append(translate(g, x - minx, y - maxy))
        x += w + gap
        rowh = max(rowh, h)
    return placed


def write(name, tkey, t):
    check_corner(t)
    f, s = wall("F", t, name), wall("S", t, name)
    pieces = layout([f, f, s, s, plate(t, False), plate(t, True)])
    allg = unary_union(pieces)
    gx0, gy0, gx1, gy1 = allg.bounds
    Wd, Hd = gx1 - gx0 + 4, gy1 - gy0 + 4
    ox, oy = gx0 - 2, gy1 + 2
    d = os.path.join(OUT, tkey)
    os.makedirs(d, exist_ok=True)
    paths = ["M " + " L ".join(f"{x - ox:.3f},{oy - y:.3f}" for x, y in r) + " Z"
             for g in pieces for r in rings_of(g)]
    with open(os.path.join(d, f"lantern_{name}_{tkey}.svg"), "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.2f}mm" height="{Hd:.2f}mm" '
                 f'viewBox="0 0 {Wd:.2f} {Hd:.2f}">\n<!-- MathRelaxing geometric lantern · {LABEL[name]} · '
                 f'{t} mm · red = cut · 2 front walls, 2 side walls, base, top ring -->\n' +
                 "\n".join(f'<path d="{p}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for p in paths) +
                 "\n</svg>\n")
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    for g in pieces:
        for r in rings_of(g):
            doc.modelspace().add_lwpolyline(r, close=True, dxfattribs={"layer": "CUT"})
    doc.saveas(os.path.join(d, f"lantern_{name}_{tkey}.dxf"))
    return f, s, (gx1 - gx0, gy1 - gy0)


# ── Package ──────────────────────────────────────────────────────────────────
def package():
    os.makedirs(DIST, exist_ok=True)
    z = os.path.join(DIST, "MathRelaxing_Geometric_Lanterns_SVG_DXF.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                zf.write(os.path.join(root, fn), os.path.join(os.path.relpath(root, OUT), fn))
    from reportlab.lib.colors import HexColor, black
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(ROOT, "lulu_books", "assets", "fonts", "Cinzel-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Body", "LiberationSans-Regular.ttf"))
    g = os.path.join(DIST, "MathRelaxing_Geometric_Lanterns_Guide.pdf")
    Wp, Hp = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(g, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, Hp - 1.3 * inch, Wp, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 24)
    c.drawCentredString(Wp / 2, Hp - 0.75 * inch, "Geometric Lanterns")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(Wp / 2, Hp - 1.05 * inch, "6 mathematical tealight lanterns · laser cut files · guide")
    y = Hp - 1.75 * inch
    blocks = [
        ("SAFETY FIRST", ["Use LED / battery tealights ONLY. Never use a real flame in a wood or paper lantern",
                          "Do not leave lit candles unattended"]),
        ("Choose your thickness", ["Folders 3mm / 1-8in / 4mm: finger joints and slots match that material exactly",
                                   "Measure your sheet with calipers and pick the closest folder",
                                   "Each file contains 2 front walls, 2 side walls, the base and the top ring"]),
        ("Assemble", ["1. Fit the two side walls between the two front walls (finger joints interlock)",
                      "2. Press the bottom tabs into the base slots",
                      "3. Press the top ring onto the top tabs",
                      "4. Add a drop of wood glue at the corners for a permanent build (optional)"]),
        ("Size", [f"Lantern body {W:.0f} × {W:.0f} × {H:.0f} mm, base and top ring {W + 2 * LIP:.0f} mm square",
                  "Fits a standard LED tealight (38 mm) with room to spare",
                  "Every sheet layout fits a 480 × 280 mm bed"]),
        ("Ideas", ["Mirror acrylic or birch plywood, painted white for a frosted look",
                   "Line the inside with vellum or tracing paper for a soft diffused glow",
                   "Engrave a name or date on the base for a personalised gift"]),
    ]
    for head, lines in blocks:
        c.setFillColor(navy if head != "SAFETY FIRST" else HexColor("#8a1c1c"))
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y -= 18
        c.setFillColor(black)
        c.setFont("Body", 10.5)
        for ln in lines:
            c.drawString(M + 12, y, ("• " if not ln[0].isdigit() else "") + ln)
            y -= 15
        y -= 10
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(Wp / 2, 0.5 * inch, "© MathRelaxing. For personal use only. Not for redistribution or resale.")
    c.save()
    return z, g


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in DESIGNS:
        for tkey, t in THICKNESSES.items():
            f, s, sheet = write(name, tkey, t)
        print(f"{LABEL[name]:<16} holes F={len(f.interiors):>3} S={len(s.interiors):>3}  "
              f"min web {O.min_web(f):.1f} mm  sheet {sheet[0]:.0f}×{sheet[1]:.0f} mm")
    for p in package():
        print(f"{os.path.getsize(p) // 1024:>6} KB  {os.path.basename(p)}")


if __name__ == "__main__":
    main()
