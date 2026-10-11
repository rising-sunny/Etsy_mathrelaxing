"""
build_tree.py — Golden-spiral Christmas tree (laser SVG/DXF + guide + listing images).

16 layers shrinking from 150 mm to 24 mm, threaded on a dowel with spacer rings.
Layer k carries an engraved tick at k·137.508° and its stack number: line the
ticks up along a pencil line on the dowel and the layers fall on the golden
spiral. No slots → independent of material thickness; only the dowel size
matters (6 mm and 8 mm versions).

  python lasercut/spiral_tree/build_tree.py
"""
from __future__ import annotations

import math
import os
import sys
import zipfile

import ezdxf
from shapely.affinity import rotate, scale, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "ornaments_3d"))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "advent_ornaments"))
import build_ornaments as O  # noqa: E402
from build_advent import number_glyph  # noqa: E402

OUT = os.path.join(HERE, "out")
DIST = os.path.join(HERE, "dist")
LIST = os.path.join(HERE, "listing")
GOLDEN = 137.507764
N = 16
R_MAX, R_MIN = 75.0, 14.0
DOWELS = {"6mm": 6.0, "8mm": 8.0}
CUT, ENGRAVE = "#FF0000", "#000000"
VARIANTS = {"star": "Golden Star Tree", "koch": "Koch Snowflake Tree", "hex": "Honeycomb Hexagon Tree"}


def layer_outline(kind, r):
    if kind == "star":
        return O.star_curve(r, 5, 0.42 if r > 30 else 0.2)  # shallow valleys keep room for the tick
    if kind == "koch":
        return O.koch_snowflake(r, 3 if r > 30 else 2)
    if kind == "hex":
        return O.hexagon(0, 0, r, rot=90)
    raise KeyError(kind)


def tick(k, r_in, r_out, w=0.9):
    a = math.radians(k * GOLDEN)
    return LineString([(r_in * math.cos(a), r_in * math.sin(a)),
                       (r_out * math.cos(a), r_out * math.sin(a))]).buffer(w / 2, cap_style=2)


def layer(kind, k, dowel):
    r = R_MAX - (R_MAX - R_MIN) * k / (N - 1)
    o = layer_outline(kind, r)
    hole = Point(0, 0).buffer(dowel / 2 + 0.15, 48)
    piece = o.difference(hole)
    if r > 34:  # decorative golden-angle dots on the big layers
        dots = []
        for n in range(1, 400):
            rr = 3.9 * math.sqrt(n) + dowel
            if rr > r * 0.62:
                break
            dots.append(Point(rr * math.cos(math.radians(n * GOLDEN)), rr * math.sin(math.radians(n * GOLDEN))).buffer(1.4, 20))
        keep = [d for d in dots if d.distance(Point(0, 0)) > dowel / 2 + 9 and piece.buffer(-2.6).contains(d)]
        piece = piece.difference(unary_union(keep)) if keep else piece
    eng = tick(k, dowel / 2 + 1.2, dowel / 2 + 6.5)
    num = number_glyph(k + 1, 3.6 if r > 20 else 2.8)
    a = math.radians(k * GOLDEN + 180)
    num = translate(num, (dowel / 2 + 5.5) * math.cos(a), (dowel / 2 + 5.5) * math.sin(a))
    eng = unary_union([eng, num])
    assert piece.geom_type == "Polygon", f"{kind} layer {k} falls apart"
    if not piece.buffer(-0.3).contains(eng):
        eng = tick(k, dowel / 2 + 1.2, dowel / 2 + 5.0)  # tiny top layers: tick only
        assert piece.buffer(-0.3).contains(eng), f"{kind} layer {k}: tick does not fit"
    return piece, eng, r


def extras(dowel):
    """Base (3 stacked discs → stable), 40 spacer rings, star topper with blind socket ring."""
    base = [Point(0, 0).buffer(62, 96).difference(Point(0, 0).buffer(dowel / 2 + 0.15, 48)) for _ in range(2)]
    base.append(Point(0, 0).buffer(62, 96))  # bottom disc: no hole (dowel stands on it)
    spacer = Point(0, 0).buffer(dowel / 2 + 4.5, 48).difference(Point(0, 0).buffer(dowel / 2 + 0.15, 48))
    topper = O.star_curve(16, 5, 0.5).difference(Point(0, 0).buffer(dowel / 2 + 0.15, 48))
    return base, [spacer] * 40, [topper, topper]


def pack(items, maxw=480, maxh=280, gap=4):
    sheets, cur, x, y, rowh = [], [], 0.0, 0.0, 0.0
    for geom, eng in items:
        x0, y0, x1, y1 = geom.bounds
        w, h = x1 - x0, y1 - y0
        if x + w > maxw:
            x, y, rowh = 0.0, y + rowh + gap, 0.0
        if y + h > maxh:
            sheets.append(cur)
            cur, x, y, rowh = [], 0.0, 0.0, 0.0
        dx, dy = x - x0, -(y + h) - y0 + maxh
        cur.append((translate(geom, dx, dy), translate(eng, dx, dy) if eng is not None else None))
        x += w + gap
        rowh = max(rowh, h)
    if cur:
        sheets.append(cur)
    return sheets


def rings_of(g):
    if g.geom_type == "MultiPolygon":
        for p in g.geoms:
            yield from rings_of(p)
        return
    yield list(g.exterior.coords)
    for r in g.interiors:
        yield list(r.coords)


def write_sheet(items, path_svg, path_dxf, note):
    cut, eng = [], []
    for g, e in items:
        cut += list(rings_of(g))
        if e is not None and not e.is_empty:
            eng += list(rings_of(e))
    ys = [y for r in cut for _, y in r]
    xs = [x for r in cut for x, _ in r]
    W, H = max(xs) + 4, max(ys) + 4
    fmt = lambda r: "M " + " L ".join(f"{x + 2:.3f},{H - y - 2:.3f}" for x, y in r) + " Z"
    body = [f'<path d="{fmt(r)}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for r in cut]
    if eng:
        body.append(f'<path d="{" ".join(fmt(r) for r in eng)}" fill="{ENGRAVE}" fill-rule="evenodd" stroke="none"/>')
    with open(path_svg, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" '
                f'viewBox="0 0 {W:.2f} {H:.2f}">\n<!-- {note} -->\n' + "\n".join(body) + "\n</svg>\n")
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=7)
    for r in cut:
        doc.modelspace().add_lwpolyline(r, close=True, dxfattribs={"layer": "CUT"})
    for r in eng:
        doc.modelspace().add_lwpolyline(r, close=True, dxfattribs={"layer": "ENGRAVE"})
    doc.saveas(path_dxf)


def build_files():
    os.makedirs(DIST, exist_ok=True)
    for kind, label in VARIANTS.items():
        for dkey, dw in DOWELS.items():
            items = [layer(kind, k, dw)[:2] for k in range(N)]
            base, spacers, topper = extras(dw)
            items += [(g, None) for g in base + topper + spacers]
            items.sort(key=lambda it: -(it[0].bounds[3] - it[0].bounds[1]))
            sheets = pack(items)
            d = os.path.join(OUT, f"dowel_{dkey}")
            os.makedirs(d, exist_ok=True)
            for i, sh in enumerate(sheets, 1):
                write_sheet(sh, os.path.join(d, f"{kind}_tree_sheet{i}_{dkey}.svg"),
                            os.path.join(d, f"{kind}_tree_sheet{i}_{dkey}.dxf"),
                            f"MathRelaxing {label} · dowel {dw} mm · sheet {i}/{len(sheets)} · red = cut, black = engrave")
            print(f"{label:<24} dowel {dkey}: {len(items)} parts on {len(sheets)} sheets")
    z = os.path.join(DIST, "MathRelaxing_Golden_Spiral_Trees_SVG_DXF.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                zf.write(os.path.join(root, fn), os.path.join(os.path.relpath(root, OUT), fn))
    print(f"zip {os.path.getsize(z) // 1024} KB")


if __name__ == "__main__":
    build_files()
