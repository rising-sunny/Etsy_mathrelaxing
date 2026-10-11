"""
build_hinges.py — Living hinge pattern library (laser cut SVG/DXF) + 2 projects.

10 families × 3 flex levels = 30 patterns. Each pattern ships as
  swatches/NN_family_level.svg   120×50 mm test strip (outline + hinge zone)
  tiles/NN_family_level.svg      100×100 mm hinge field to paste into designs
Hinge slits are open polylines (single cut lines). Safety checks: slits never
touch each other or the strip outline, and the strip minus the (kerf-buffered)
slits stays ONE piece.

  python lasercut/living_hinges/build_hinges.py
"""
from __future__ import annotations

import math
import os
import zipfile

import ezdxf
import numpy as np
from shapely.affinity import translate
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DIST = os.path.join(HERE, "dist")
CUT = "#FF0000"
KERF = 0.15
MIN_GAP = 0.9            # mm between any two slits / slit and outline

# flex level → (pitch along bend direction, slit length, bridge)
LEVELS = {"firm": (2.4, 14.0, 4.0), "medium": (1.8, 18.0, 3.0), "soft": (1.4, 22.0, 2.4)}


def staggered(field, pitch, length, bridge, shape_fn):
    """Columns of slits perpendicular to the bend; alternate columns offset by half a period."""
    x0, y0, x1, y1 = field
    period = length + bridge
    out = []
    i = 0
    x = x0 + pitch / 2
    while x < x1 - pitch / 4:
        off = 0 if i % 2 == 0 else period / 2
        y = y0 - period + off + bridge
        while y < y1:
            a, b = max(y, y0 + bridge), min(y + length, y1 - bridge)
            if b - a > 2.5:
                out.append(shape_fn(x, a, b, pitch))
            y += period
        x += pitch
        i += 1
    return out


def straight(x, a, b, p):
    return LineString([(x, a), (x, b)])


def wave(x, a, b, p):
    t = np.linspace(a, b, 40)
    return LineString(np.c_[x + p * 0.28 * np.sin((t - a) / (b - a) * 2 * np.pi), t])


def zigzag(x, a, b, p):
    n = max(2, int((b - a) / 3))
    ys = np.linspace(a, b, n + 1)
    return LineString([(x + (p * 0.25 if k % 2 else -p * 0.25), y) for k, y in enumerate(ys)])


def arc(x, a, b, p):
    t = np.linspace(-1, 1, 30)
    return LineString(np.c_[x + p * 0.3 * (1 - t ** 2), (a + b) / 2 + t * (b - a) / 2])


FAMILIES = {}


def fam(name):
    def deco(f):
        FAMILIES[name] = f
        return f
    return deco


@fam("lattice")
def f_lattice(field, p, L, br):
    return staggered(field, p, L, br, straight)


@fam("wave")
def f_wave(field, p, L, br):
    return staggered(field, p * 1.25, L, br, wave)


@fam("zigzag")
def f_zigzag(field, p, L, br):
    return staggered(field, p * 1.3, L, br, zigzag)


@fam("arcs")
def f_arcs(field, p, L, br):
    return staggered(field, p * 1.2, L, br, arc)


@fam("brick")
def f_brick(field, p, L, br):
    """I-beam slits: a long slit with short perpendicular caps."""
    def ibeam(x, a, b, pp):
        c = pp * 0.25  # caps of neighbouring columns can meet at the field edge
        return MultiLineString([[(x, a), (x, b)], [(x - c, a), (x + c, a)], [(x - c, b), (x + c, b)]])
    base = staggered(field, p * 1.6, L, br, ibeam)
    return base


@fam("serpentine")
def f_serpentine(field, p, L, br):
    """Switchback: one long meandering slit — the softest hinge."""
    x0, y0, x1, y1 = field
    pts, k = [], 0
    for x in np.arange(x0 + p, x1 - p / 2, p * 1.5):
        ya, yb = (y0 + br, y1 - br) if k % 2 == 0 else (y1 - br, y0 + br)
        pts += [(x, ya), (x, yb)]
        k += 1
    return [LineString(pts)]


@fam("diamond")
def f_diamond(field, p, L, br):
    x0, y0, x1, y1 = field
    out, h = [], L * 0.55
    cols = int((x1 - x0) / (p * 1.7))
    for i in range(cols):
        x = x0 + (i + 0.5) * (x1 - x0) / cols
        off = 0 if i % 2 == 0 else (h + br) / 2
        y = y0 + br + off
        while y + h < y1 - br:
            out.append(LineString([(x, y), (x + p * 0.45, y + h / 2), (x, y + h)]))
            y += h + br
    return out


@fam("cross")
def f_cross(field, p, L, br):
    """Plus-shaped slits: bends both ways (compound curves)."""
    x0, y0, x1, y1 = field
    s = max(4.2, L * 0.42)
    out, j = [], 0
    y = y0 + s / 2 + br
    while y < y1 - s / 2 - br:
        x = x0 + s / 2 + br + (0 if j % 2 == 0 else (s + br) / 2)
        while x < x1 - s / 2 - br:
            out.append(MultiLineString([[(x - s / 2, y), (x + s / 2, y)], [(x, y - s / 2), (x, y + s / 2)]]))
            x += s + br
        y += (s + br) / 2
        j += 1
    return out


@fam("honeycomb")
def f_honeycomb(field, p, L, br):
    """Open hexagon outlines (each missing two sides) in a staggered grid."""
    x0, y0, x1, y1 = field
    r = max(3.2, L * 0.28)
    out, row = [], 0
    y = y0 + r + br
    while y < y1 - r - br:
        x = x0 + r + br + (0 if row % 2 == 0 else r * 1.05)
        while x < x1 - r - br:
            pts = [(x + r * math.cos(math.radians(30 + 60 * k)), y + r * math.sin(math.radians(30 + 60 * k)))
                   for k in range(5)]
            out.append(LineString(pts))
            x += r * 2.1 + br * 0.6
        y += r * 1.5 + br * 0.5
        row += 1
    return out


@fam("ellipse")
def f_ellipse(field, p, L, br):
    def half_ellipse(x, a, b, pp):
        t = np.linspace(0, np.pi, 30)
        return LineString(np.c_[x + pp * 0.32 * np.sin(t), a + (b - a) * (1 - np.cos(t)) / 2])
    return staggered(field, p * 1.4, L, br, half_ellipse)


# ── checks / writers ─────────────────────────────────────────────────────────
def check(slits, outline):
    lines = list(slits)  # whole slits: parts of one slit may touch each other
    tree = STRtree(lines)
    for i, ln in enumerate(lines):
        for j in tree.query(ln.buffer(MIN_GAP)):
            if j != i and ln.distance(lines[j]) < MIN_GAP:
                raise AssertionError("slits too close")
        if outline is not None and ln.distance(outline.exterior) < MIN_GAP:
            raise AssertionError("slit touches outline")
    if outline is not None:
        mat = outline.difference(unary_union([ln.buffer(KERF / 2) for ln in lines]))
        assert mat.geom_type == "Polygon", "strip falls apart"
    return len(lines)


def svg_doc(polys, lines, w, h, note):
    paths = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            paths.append("M " + " L ".join(f"{x:.3f},{h - y:.3f}" for x, y in ring.coords) + " Z")
    for ln in lines:
        for g in getattr(ln, "geoms", [ln]):
            paths.append("M " + " L ".join(f"{x:.3f},{h - y:.3f}" for x, y in g.coords))
    body = "\n".join(f'<path d="{p}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for p in paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">\n'
            f"<!-- {note} -->\n{body}\n</svg>\n")


def dxf_doc(polys, lines, path):
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    msp = doc.modelspace()
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            msp.add_lwpolyline(list(ring.coords), close=True, dxfattribs={"layer": "CUT"})
    for ln in lines:
        for g in getattr(ln, "geoms", [ln]):
            msp.add_lwpolyline(list(g.coords), dxfattribs={"layer": "CUT"})
    doc.saveas(path)


def write_pair(folder, stem, polys, lines, w, h, note):
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    with open(os.path.join(OUT, folder, stem + ".svg"), "w") as f:
        f.write(svg_doc(polys, lines, w, h, note))
    dxf_doc(polys, lines, os.path.join(OUT, folder, stem + ".dxf"))


def safe(fname, field, p, L, br, outline):
    """Generate a pattern, widening the pitch 8% at a time until every check passes."""
    for k in range(14):
        slits = FAMILIES[fname](field, p * 1.08 ** k, L, br)
        try:
            return slits, check(slits, outline), k
        except AssertionError:
            continue
    raise AssertionError(f"{fname}: could not satisfy spacing")


def swatch(fname, level):
    p, L, br = LEVELS[level]
    outline = Polygon(box(0, 0, 120, 50).exterior.coords)
    slits, n, k = safe(fname, (20, 2.5, 100, 47.5), p, L, br, outline)
    return outline, slits, n, k


def tile(fname, level):
    p, L, br = LEVELS[level]
    return safe(fname, (0, 0, 100, 100), p, L, br, None)[0]


# ── projects ─────────────────────────────────────────────────────────────────
def cuff():
    outline = box(0, 0, 165, 38).buffer(6, join_style=1).buffer(-6, join_style=1)
    outline = translate(outline, 6, 6)
    slits = safe("wave", (22, 9, 155, 41), *LEVELS["soft"], outline)[0]
    return outline, slits


def pencil_cup(t=3.0, d=70.0, h=90.0):
    L = math.pi * (d + t)
    band = box(0, 0, L, h)
    knob = Point(L, h / 2).buffer(6, 48).union(box(L - 3, h / 2 - 3.5, L + 2, h / 2 + 3.5))
    socket = Point(0, h / 2).buffer(6.15, 48).union(box(-2, h / 2 - 3.65, 3.2, h / 2 + 3.65))
    band = band.union(knob).difference(socket)
    band = translate(band, 10, 6)
    slits = safe("lattice", (24, 9, L - 2, h + 3), *LEVELS["medium"], band)[0]
    base = translate(Point(0, 0).buffer(d / 2, 128), d / 2 + 10, -d / 2 - 6)
    return band, slits, base


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    k = 0
    total = 0
    for fname in FAMILIES:
        for level in LEVELS:
            k += 1
            stem = f"{k:02d}_{fname}_{level}"
            outline, slits, n, widened = swatch(fname, level)
            write_pair("swatches", stem, [outline], slits, 120, 50,
                       f"MathRelaxing living hinge · {fname} · {level} · 120x50 mm test strip · red = cut")
            tl = tile(fname, level)
            write_pair("tiles", stem, [], tl, 100, 100,
                       f"MathRelaxing living hinge · {fname} · {level} · 100x100 mm field to clip into designs")
            total += n
            print(f"{stem:<24} slits={n:>4}  pitch widened {1.08 ** widened - 1:4.0%}")
    c_out, c_sl = cuff()
    write_pair("projects", "cuff_bracelet", [c_out], c_sl, 190, 50, "Living hinge cuff bracelet · 3 mm plywood")
    band, sl, base = pencil_cup()
    bx = band.bounds
    write_pair("projects", "pencil_cup_3mm", [band, translate(base, 0, 200)], sl, round(bx[2] + 12), 300,
               "Living hinge pencil cup · 3 mm · band wraps the base disc, puzzle joint closes the seam")
    z = os.path.join(DIST, "MathRelaxing_Living_Hinge_Library_SVG_DXF.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                zf.write(os.path.join(root, fn), os.path.join(os.path.relpath(root, OUT), fn))
    print(f"{k} patterns, {total} slits checked; zip {os.path.getsize(z) // 1024} KB")


if __name__ == "__main__":
    main()
