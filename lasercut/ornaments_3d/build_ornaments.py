"""
build_ornaments.py — 3D slot-together Christmas ornaments (laser cut SVG/DXF/PDF).

Each ornament = two identical silhouettes: piece A slotted from the top to the
centre, piece B from the bottom; they interlock at 90°. A solid spine runs
along the slot axis, decorative cut-outs (generated from mathematical
patterns) keep a minimum web to the outline, the spine and each other, and
every piece is asserted to be ONE connected polygon.

  python lasercut/ornaments_3d/build_ornaments.py
"""
from __future__ import annotations

import math
import os
import random

import ezdxf
import numpy as np
import shapely.geometry
from shapely.affinity import rotate, scale, translate
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
WEB = 2.6           # mm, minimum material between cut-outs / to edges
SPINE_WEB = 3.5     # mm, solid material each side of the slot
HANG_D = 3.6        # mm hanging hole
THICKNESSES = {"3mm": 3.0, "1-8in": 3.175, "4mm": 4.0}
CUT = "#FF0000"
H = 92.0            # mm nominal height of the body


# ── Outlines ─────────────────────────────────────────────────────────────────
def koch_snowflake(R, level=3):
    pts = [(R * math.cos(math.radians(90 + 120 * i)), R * math.sin(math.radians(90 + 120 * i))) for i in range(3)]
    for _ in range(level):
        new = []
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            dx, dy = (x2 - x1) / 3, (y2 - y1) / 3
            a, b = (x1 + dx, y1 + dy), (x1 + 2 * dx, y1 + 2 * dy)
            px = a[0] + dx * 0.5 + dy * math.sqrt(3) / 2
            py = a[1] + dy * 0.5 - dx * math.sqrt(3) / 2
            new += [(x1, y1), a, (px, py), b]
        pts = new
    return Polygon(pts)


def bauble(R):
    body = Point(0, 0).buffer(R, 128)
    cap = box(-7, R - 2, 7, R + 7)
    return unary_union([body, cap])


def star_curve(R, k=5, amp=0.28):
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    r = R * (1 + amp * np.cos(k * (th - np.pi / 2))) / (1 + amp)
    return Polygon(np.c_[r * np.cos(th), r * np.sin(th)])


def octagram(R):
    sq = box(-R / math.sqrt(2), -R / math.sqrt(2), R / math.sqrt(2), R / math.sqrt(2))
    return unary_union([rotate(sq, 22.5), rotate(sq, 67.5)])


def tree(R):
    tri = Polygon([(0, R), (-R * 0.9, -R * 0.62), (R * 0.9, -R * 0.62)])
    trunk = box(-7, -R * 0.62 - 11, 7, -R * 0.62 + 1)
    return unary_union([tri, trunk]), tri


# ── Cut-out patterns ─────────────────────────────────────────────────────────
def hexagon(cx, cy, r, rot=30):
    return Polygon([(cx + r * math.cos(math.radians(rot + 60 * i)), cy + r * math.sin(math.radians(rot + 60 * i)))
                    for i in range(6)])


def pat_koch(outline):
    holes = []
    for k in range(6):
        a = math.radians(30 + 60 * k)
        holes.append(translate(scale(koch_snowflake(9, 2), 1, 1), 24 * math.cos(a), 24 * math.sin(a)))
        a2 = math.radians(60 * k)
        holes.append(hexagon(33 * math.cos(a2), 33 * math.sin(a2), 3.6, rot=0))
    holes.append(koch_snowflake(13, 2))
    return holes


def pat_sierpinski(tri, depth=4):
    holes = []

    def rec(p, d):
        if d == 0:
            return
        a, b, c = p
        ab, bc, ca = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2),
                      ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)]
        holes.append(Polygon([ab, bc, ca]))
        rec((a, ab, ca), d - 1)
        rec((ab, b, bc), d - 1)
        rec((ca, bc, c), d - 1)

    rec(list(tri.exterior.coords)[:3], depth)
    return holes


def pat_voronoi(R, seed=7):
    rng = random.Random(seed)
    pts = []
    while len(pts) < 70:
        x, y = rng.uniform(-R, R), rng.uniform(-R, R)
        if x * x + y * y < (R * 1.1) ** 2 and all(math.dist((x, y), q) > 7.5 for q in pts):
            pts.append((x, y))
    from shapely.ops import voronoi_diagram
    vd = voronoi_diagram(shapely.geometry.MultiPoint(pts), envelope=box(-2 * R, -2 * R, 2 * R, 2 * R))
    return [g.simplify(0.05) for g in vd.geoms]


def pat_phyllotaxis(R):
    holes, ga = [], math.radians(137.507764)
    for n in range(1, 400):
        r = 4.3 * math.sqrt(n)
        if r > R:
            break
        rad = 0.9 + 1.35 * r / R
        holes.append(Point(r * math.cos(n * ga), r * math.sin(n * ga)).buffer(rad + WEB / 2, 24))
    return holes


def pat_honeycomb(R):
    holes, s = [], 7.4
    for q in range(-12, 13):
        for r in range(-12, 13):
            x, y = s * (q + r / 2), s * math.sqrt(3) / 2 * r
            if x * x + y * y < (R + s) ** 2:
                holes.append(hexagon(x, y, s / math.sqrt(3)))
    return holes


def pat_apollonian(R, rmin=1.8):
    """Apollonian gasket inside a circle of radius R (Descartes, complex form)."""
    circles = []
    k0 = -1 / R
    r1 = R / (1 + 2 / math.sqrt(3))
    ks = [1 / r1] * 3
    zs = [complex((R - r1) * math.cos(math.radians(90 + 120 * i)), (R - r1) * math.sin(math.radians(90 + 120 * i)))
          for i in range(3)]
    for k, z in zip(ks, zs):
        circles.append((z, 1 / k))
    start = [((k0, 0j), (ks[0], zs[0]), (ks[1], zs[1]), (ks[2], zs[2]))]
    stack = []
    # inner central circle
    kc = ks[0] * 3 + 2 * math.sqrt(3 * ks[0] ** 2)
    circles.append((0j, 1 / kc))
    for i in range(3):
        a, b = (ks[i], zs[i]), (ks[(i + 1) % 3], zs[(i + 1) % 3])
        stack.append(((k0, 0j), a, b))
        stack.append(((kc, 0j), a, b))
    while stack:
        (k1, z1), (k2, z2), (k3, z3) = stack.pop()
        k4 = k1 + k2 + k3 + 2 * math.sqrt(abs(k1 * k2 + k2 * k3 + k3 * k1))
        if 1 / k4 < rmin:
            continue
        s = k1 * z1 + k2 * z2 + k3 * z3
        root = 2 * np.sqrt(k1 * k2 * z1 * z2 + k2 * k3 * z2 * z3 + k1 * k3 * z1 * z3)
        cands = [(s + root) / k4, (s - root) / k4]
        # tangency with signed radii (outer circle has negative curvature): |z - zi| = |1/ki + 1/k4|
        z4 = min(cands, key=lambda z: sum(abs(abs(z - zi) - abs(1 / ki + 1 / k4))
                                          for ki, zi in ((k1, z1), (k2, z2), (k3, z3))))
        circles.append((z4, 1 / k4))
        for pair in (((k1, z1), (k2, z2)), ((k2, z2), (k3, z3)), ((k1, z1), (k3, z3))):
            stack.append((pair[0], pair[1], (k4, z4)))
    return [Point(z.real, z.imag).buffer(r, 48) for z, r in circles]


def pat_petals(R, k=5):
    holes = []
    for i in range(k):
        a = 90 + 360 / k * i
        e = scale(Point(0, 0).buffer(1, 48), 5.2, 12.5)
        holes.append(translate(rotate(e, a - 90, origin=(0, 0)), 0.52 * R * math.cos(math.radians(a)),
                               0.52 * R * math.sin(math.radians(a))))
        b = a + 180 / k
        holes.append(Point(0.42 * R * math.cos(math.radians(b)), 0.42 * R * math.sin(math.radians(b))).buffer(3.2, 32))
        holes.append(Point(0.22 * R * math.cos(math.radians(a)), 0.22 * R * math.sin(math.radians(a))).buffer(2.4, 32))
    return holes


def pat_octagram(R):
    holes = []
    kite = Polygon([(0, 0), (4.2, 9), (0, 20), (-4.2, 9)])
    for i in range(8):
        holes.append(rotate(translate(kite, 0, R * 0.22), 45 * i + 22.5, origin=(0, 0)))
        holes.append(rotate(hexagon(0, R * 0.62, 3.2, rot=0), 45 * i, origin=(0, 0)))
    return holes


# ── Assembly ─────────────────────────────────────────────────────────────────
def design(name):
    R = H / 2
    if name == "koch_snowflake":
        o = koch_snowflake(R)
        return o, pat_koch(o)
    if name == "sierpinski_tree":
        o, tri = tree(R)
        return o, pat_sierpinski(tri)
    if name == "voronoi_bauble":
        return bauble(R * 0.92), pat_voronoi(R * 0.92)
    if name == "golden_bauble":
        return bauble(R * 0.92), pat_phyllotaxis(R * 0.92)
    if name == "honeycomb_bauble":
        return bauble(R * 0.92), pat_honeycomb(R * 0.92)
    if name == "apollonian_bauble":
        o = bauble(R * 0.92)
        return o, pat_apollonian(R * 0.92 - WEB)
    if name == "pentagram_star":
        o = star_curve(R)
        return o, pat_petals(R)
    if name == "girih_star":
        o = octagram(R)
        return o, pat_octagram(R)
    raise KeyError(name)


DESIGNS = ["koch_snowflake", "sierpinski_tree", "voronoi_bauble", "golden_bauble",
           "honeycomb_bauble", "apollonian_bauble", "pentagram_star", "girih_star"]
LABEL = {"koch_snowflake": "Koch Snowflake", "sierpinski_tree": "Sierpinski Tree",
         "voronoi_bauble": "Voronoi Bauble", "golden_bauble": "Golden Angle Bauble",
         "honeycomb_bauble": "Honeycomb Bauble", "apollonian_bauble": "Apollonian Bauble",
         "pentagram_star": "Five-Fold Star", "girih_star": "Girih Star"}


def axis_extent(outline):
    minx, miny, maxx, maxy = outline.bounds
    seg = outline.intersection(box(-0.01, miny - 1, 0.01, maxy + 1))
    _, y0, _, y1 = seg.bounds
    return y0, y1


def build_piece(name, t, which):
    outline, pattern = design(name)
    y0, y1 = axis_extent(outline)
    mid = (y0 + y1) / 2
    spine = box(-t / 2 - SPINE_WEB, y0 - 1, t / 2 + SPINE_WEB, y1 + 1)
    inner = outline.buffer(-WEB, join_style=2)
    holes = []
    for h in pattern:
        h = h.buffer(-WEB / 2, join_style=2)
        if h.is_empty:
            continue
        h = h.intersection(inner).difference(spine)
        for g in getattr(h, "geoms", [h]):
            if g.geom_type == "Polygon" and not g.buffer(-0.9).is_empty and g.area > 6:
                holes.append(g)
    piece = outline.difference(unary_union(holes)) if holes else outline
    if which == "A":
        slot = box(-t / 2, mid, t / 2, y1 + 1)
    else:
        slot = box(-t / 2, y0 - 1, t / 2, mid)
    piece = piece.difference(slot)
    if which == "B":  # hanging hole: highest point on the spine where the body is ≥ 12 mm wide
        yy = y1 - 4.2
        while outline.intersection(box(-50, yy - 0.01, 50, yy + 0.01)).bounds[2] - \
                outline.intersection(box(-50, yy - 0.01, 50, yy + 0.01)).bounds[0] < 12:
            yy -= 0.5
        piece = piece.difference(Point(0, yy).buffer(HANG_D / 2, 32))
    assert isinstance(piece, Polygon), f"{name} {which}: piece falls apart"
    return piece, len(holes)


def rings_of(geom):
    if isinstance(geom, MultiPolygon):
        for g in geom.geoms:
            yield from rings_of(g)
        return
    yield list(geom.exterior.coords)
    for i in geom.interiors:
        yield list(i.coords)


def write(name, tkey, t):
    a, n = build_piece(name, t, "A")
    b, _ = build_piece(name, t, "B")
    minx, miny, maxx, maxy = a.bounds
    w = maxx - minx
    b = translate(b, w + 6, 0)
    both = [a, b]
    gx0, gy0, gx1, gy1 = unary_union(both).bounds
    W, Hh = gx1 - gx0 + 4, gy1 - gy0 + 4
    ox, oy = gx0 - 2, gy1 + 2
    ddir = os.path.join(OUT, tkey)
    os.makedirs(ddir, exist_ok=True)
    paths = []
    for g in both:
        for r in rings_of(g):
            paths.append("M " + " L ".join(f"{x - ox:.3f},{oy - y:.3f}" for x, y in r) + " Z")
    body = "\n".join(f'<path d="{p}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for p in paths)
    with open(os.path.join(ddir, f"{name}_{tkey}.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{Hh:.2f}mm" '
                f'viewBox="0 0 {W:.2f} {Hh:.2f}">\n<!-- MathRelaxing 3D ornament · {LABEL[name]} · '
                f'material {t} mm · red = cut · left = piece A (slot from top), right = piece B -->\n'
                f'{body}\n</svg>\n')
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    for g in both:
        for r in rings_of(g):
            doc.modelspace().add_lwpolyline(r, close=True, dxfattribs={"layer": "CUT"})
    doc.saveas(os.path.join(ddir, f"{name}_{tkey}.dxf"))
    return a, translate(b, -(w + 6), 0), n


def min_web(piece):
    """Smallest material width ≈ 2 × the erosion radius at which the piece splits."""
    lo, hi = 0.2, 4.0
    for _ in range(18):
        m = (lo + hi) / 2
        g = piece.buffer(-m)
        if g.is_empty or g.geom_type == "MultiPolygon":
            hi = m
        else:
            lo = m
    return 2 * lo


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in DESIGNS:
        for tkey, t in THICKNESSES.items():
            a, b, n = write(name, tkey, t)
        minx, miny, maxx, maxy = a.bounds
        print(f"{LABEL[name]:<20} {maxx - minx:5.1f}×{maxy - miny:5.1f} mm  cut-outs={n:>3}  "
              f"min web A={min_web(a):.1f} B={min_web(b):.1f} mm")


if __name__ == "__main__":
    main()
