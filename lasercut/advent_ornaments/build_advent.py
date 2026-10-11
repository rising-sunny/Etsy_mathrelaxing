"""
build_advent.py — 24-day advent calendar of slot-together math ornaments (laser SVG/DXF).

Reuses the verified ornament engine (lasercut/ornaments_3d/build_ornaments.py):
24 outline × pattern combinations at 75 mm, each piece asserted single-part,
and the day number engraved (black fill) on piece B's solid spine.

  python lasercut/advent_ornaments/build_advent.py
"""
from __future__ import annotations

import os
import sys
import zipfile

import ezdxf
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from shapely.affinity import rotate, scale, translate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "ornaments_3d"))
import build_ornaments as B  # noqa: E402

OUT = os.path.join(HERE, "out")
DIST = os.path.join(HERE, "dist")
R = 37.5  # 75 mm ornaments
CUT, ENGRAVE = "#FF0000", "#000000"
_orig_design = B.design


def voronoi(r, seed):
    """B.pat_voronoi always wants 70 cells (fits 92 mm); scale the count to the size, cap the tries."""
    import math
    import random
    from shapely.geometry import MultiPoint
    from shapely.ops import voronoi_diagram
    rng = random.Random(seed)
    want, pts, tries = int(70 * (r / 42.3) ** 2), [], 0
    while len(pts) < want and tries < 20000:
        tries += 1
        x, y = rng.uniform(-r, r), rng.uniform(-r, r)
        if x * x + y * y < (r * 1.1) ** 2 and all(math.dist((x, y), q) > 7.5 for q in pts):
            pts.append((x, y))
    vd = voronoi_diagram(MultiPoint(pts), envelope=box(-2 * r, -2 * r, 2 * r, 2 * r))
    return [g.simplify(0.05) for g in vd.geoms]


def hexagram(r):
    t1 = Polygon([(0, r), (-r * 0.866, -r / 2), (r * 0.866, -r / 2)])
    return unary_union([t1, rotate(t1, 180, origin=(0, 0))])


DAYS = [  # (label, outline, pattern)
    ("Koch Snowflake", lambda: B.koch_snowflake(R), lambda o: B.pat_koch(o)),
    ("Sierpinski Tree", lambda: B.tree(R)[0], lambda o: B.pat_sierpinski(B.tree(R)[1])),
    ("Voronoi Bauble", lambda: B.bauble(R * 0.92), lambda o: voronoi(R * 0.92, 7)),
    ("Golden Angle Bauble", lambda: B.bauble(R * 0.92), lambda o: B.pat_phyllotaxis(R * 0.92)),
    ("Honeycomb Bauble", lambda: B.bauble(R * 0.92), lambda o: B.pat_honeycomb(R * 0.92)),
    ("Apollonian Bauble", lambda: B.bauble(R * 0.92), lambda o: B.pat_apollonian(R * 0.92 - B.WEB)),
    ("Five-Fold Rose", lambda: B.star_curve(R, 5), lambda o: B.pat_petals(R, 5)),
    ("Girih Star", lambda: B.octagram(R), lambda o: B.pat_octagram(R)),
    ("Six-Fold Rose", lambda: B.star_curve(R, 6), lambda o: B.pat_petals(R, 6)),
    ("Seven-Fold Rose", lambda: B.star_curve(R, 7), lambda o: B.pat_petals(R, 7)),
    ("Eight-Fold Rose", lambda: B.star_curve(R, 8, 0.22), lambda o: B.pat_petals(R, 8)),
    ("Hexagram Honeycomb", lambda: hexagram(R), lambda o: B.pat_honeycomb(R)),
    ("Golden Snowflake", lambda: B.koch_snowflake(R), lambda o: B.pat_phyllotaxis(R)),
    ("Golden Tree", lambda: B.tree(R)[0], lambda o: B.pat_phyllotaxis(R)),
    ("Honeycomb Tree", lambda: B.tree(R)[0], lambda o: B.pat_honeycomb(R)),
    ("Voronoi Tree", lambda: B.tree(R)[0], lambda o: voronoi(R, 11)),
    ("Golden Girih", lambda: B.octagram(R), lambda o: B.pat_phyllotaxis(R)),
    ("Voronoi Rose", lambda: B.star_curve(R, 5), lambda o: voronoi(R, 5)),
    ("Petal Bauble", lambda: B.bauble(R * 0.92), lambda o: B.pat_petals(R * 0.9, 6)),
    ("Voronoi Hexagram", lambda: hexagram(R), lambda o: voronoi(R, 13)),
    ("Honeycomb Snowflake", lambda: B.koch_snowflake(R), lambda o: B.pat_honeycomb(R)),
    ("Honeycomb Girih", lambda: B.octagram(R), lambda o: B.pat_honeycomb(R)),
    ("Golden Rose", lambda: B.star_curve(R, 6), lambda o: B.pat_phyllotaxis(R)),
    ("Christmas Star", lambda: B.star_curve(R, 5, 0.45), lambda o: B.pat_phyllotaxis(R)),
]


def advent_design(name):
    if name.startswith("day"):
        label, fo, fp = DAYS[int(name[3:]) - 1]
        o = fo()
        return o, fp(o)
    return _orig_design(name)


B.design = advent_design  # build_piece / renderers resolve designs through B.design


def number_glyph(n, height=6.2):
    tp = TextPath((0, 0), str(n), size=10, prop=FontProperties(family="DejaVu Sans", weight="bold"))
    polys = []
    for poly in tp.to_polygons():
        if len(poly) >= 3:
            polys.append(Polygon(poly))
    # even-odd: outer contours minus counters (holes of 0, 4, 6, 8, 9)
    polys.sort(key=lambda p: -p.area)
    g = Polygon()
    for p in polys:
        g = g.symmetric_difference(p)
    x0, y0, x1, y1 = g.bounds
    g = scale(g, height / (y1 - y0), height / (y1 - y0), origin=(x0, y0))
    x0, y0, x1, y1 = g.bounds
    return translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)


def day_piece(d, t, which):
    piece, n = B.build_piece(f"day{d}", t, which)
    eng = None
    if which == "B":
        o, _ = advent_design(f"day{d}")
        y0, y1 = B.axis_extent(o)
        mid = (y0 + y1) / 2
        hole_y = max(p.centroid.y for p in [Polygon(r.coords) for r in piece.interiors]
                     if abs(p.centroid.x) < 0.5 and p.area < 12)
        cy = (hole_y - B.HANG_D / 2 + mid) / 2
        eng = translate(number_glyph(d), 0, cy)
        if not piece.buffer(-0.6).contains(eng):  # fall back to the lower half of piece A's spine area
            eng = translate(number_glyph(d, 5.0), 0, cy)
        assert piece.buffer(-0.4).contains(eng), f"day {d}: number does not fit on the spine"
    return piece, eng, n


def svg_for(items, w, h, ox, oy, note):
    paths = []
    for geom, kind in items:
        for r in B.rings_of(geom):
            d = "M " + " L ".join(f"{x - ox:.3f},{oy - y:.3f}" for x, y in r) + " Z"
            paths.append((d, kind))
    body = []
    eng = " ".join(d for d, k in paths if k == "eng")
    body += [f'<path d="{d}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for d, k in paths if k == "cut"]
    if eng:
        body.append(f'<path d="{eng}" fill="{ENGRAVE}" fill-rule="evenodd" stroke="none"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" '
            f'viewBox="0 0 {w:.2f} {h:.2f}">\n<!-- {note} -->\n' + "\n".join(body) + "\n</svg>\n")


def dxf_for(items, path):
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=7)
    for geom, kind in items:
        for r in B.rings_of(geom):
            doc.modelspace().add_lwpolyline(r, close=True, dxfattribs={"layer": "CUT" if kind == "cut" else "ENGRAVE"})
    doc.saveas(path)


def main():
    os.makedirs(DIST, exist_ok=True)
    for tkey, t in B.THICKNESSES.items():
        sheet_items, sheet_no, x, y, rowh = [], 1, 0.0, 0.0, 0.0
        tdir = os.path.join(OUT, tkey)
        os.makedirs(os.path.join(tdir, "single_days"), exist_ok=True)

        def flush():
            nonlocal sheet_items, sheet_no
            if not sheet_items:
                return
            allg = unary_union([g for g, _ in sheet_items])
            gx0, gy0, gx1, gy1 = allg.bounds
            note = f"MathRelaxing advent ornaments · sheet {sheet_no} · {t} mm · red = cut, black = engrave"
            with open(os.path.join(tdir, f"advent_sheet{sheet_no}_{tkey}.svg"), "w") as f:
                f.write(svg_for(sheet_items, gx1 - gx0 + 4, gy1 - gy0 + 4, gx0 - 2, gy1 + 2, note))
            dxf_for(sheet_items, os.path.join(tdir, f"advent_sheet{sheet_no}_{tkey}.dxf"))
            sheet_items, sheet_no = [], sheet_no + 1

        for d in range(1, 25):
            a, _, n = day_piece(d, t, "A")
            b, eng, _ = day_piece(d, t, "B")
            w = a.bounds[2] - a.bounds[0]
            pair = [(a, "cut"), (translate(b, w + 4, 0), "cut"), (translate(eng, w + 4, 0), "eng")]
            # single-day file
            allg = unary_union([g for g, _ in pair])
            gx0, gy0, gx1, gy1 = allg.bounds
            with open(os.path.join(tdir, "single_days", f"day{d:02d}_{tkey}.svg"), "w") as f:
                f.write(svg_for(pair, gx1 - gx0 + 4, gy1 - gy0 + 4, gx0 - 2, gy1 + 2,
                                f"Day {d} · {DAYS[d - 1][0]} · {t} mm"))
            dxf_for(pair, os.path.join(tdir, "single_days", f"day{d:02d}_{tkey}.dxf"))
            # sheet packing: 3 pairs per row, 3 rows per 480×280 sheet
            pw, ph = gx1 - gx0, gy1 - gy0
            if x + pw > 480:
                x, y, rowh = 0.0, y - rowh - 6, 0.0
            if -y + ph > 280:
                flush()
                x, y, rowh = 0.0, 0.0, 0.0
            sheet_items += [(translate(g, x - gx0, y - gy1), k) for g, k in pair]
            x += pw + 6
            rowh = max(rowh, ph)
            if tkey == "3mm":
                print(f"day {d:>2} {DAYS[d - 1][0]:<20} cut-outs={n:>3}  web A={B.min_web(a):.1f} mm")
        flush()
        print(f"{tkey}: {sheet_no - 1} sheets")
    z = os.path.join(DIST, "MathRelaxing_Advent_Ornaments_SVG_DXF.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                zf.write(os.path.join(root, fn), os.path.join(os.path.relpath(root, OUT), fn))
    print(f"zip {os.path.getsize(z) // 1024} KB")


if __name__ == "__main__":
    main()
