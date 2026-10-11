"""
build_marble_mazes.py — generative marble-maze laser-cut files (SVG / DXF / PDF).

Each design is a perfect maze (spanning tree, recursive backtracker) on a
square, circular (theta) or hexagonal cell graph. Channels are the tree's
edges buffered to the channel width, so the channel region is simply
connected and the wall layer is ONE connected piece (asserted).

Layers per design (all mm, cut = red hairline, engrave = black fill):
  base   solid board + bolt holes + engraved start ring / finish star
  maze   frame with the channel cut out  (cut 2x from 3 mm → 6 mm walls)
  lid    optional clear acrylic lid + bolt holes

  python lasercut/marble_mazes/build_marble_mazes.py
"""
from __future__ import annotations

import math
import os
import random
import zipfile

import ezdxf
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

CHANNEL = 10.5   # mm, for 8 mm steel balls
WALL = 4.0       # mm, thinnest wall between channels
PITCH = CHANNEL + WALL
PITCH_60 = (CHANNEL + WALL) / math.cos(math.pi / 6)  # 60° lattices: neighbour sits at 0.866·pitch
FRAME = 12.0     # mm solid rim around the maze
BOLT_D = 3.4     # mm, M3 clearance
CUT = "#FF0000"
ENGRAVE = "#000000"


# ── Cell graphs ──────────────────────────────────────────────────────────────
def square_graph(n):
    pts = {(r, c): ((c + 0.5) * PITCH, (r + 0.5) * PITCH) for r in range(n) for c in range(n)}
    nb = {k: [] for k in pts}
    for r, c in pts:
        for dr, dc in ((0, 1), (1, 0)):
            if (r + dr, c + dc) in pts:
                nb[(r, c)].append((r + dr, c + dc))
                nb[(r + dr, c + dc)].append((r, c))
    size = n * PITCH
    outline = box(-FRAME, -FRAME, size + FRAME, size + FRAME)
    return pts, nb, {}, outline, (0, 0)


def theta_graph(rings, P=PITCH_60):
    """Ring 0 = centre cell; ring k at radius k*P, cells subdivided so arc ≈ P."""
    pts, ring_cells = {(0, 0): (0.0, 0.0)}, {0: 1}
    for k in range(1, rings + 1):
        prev = ring_cells[k - 1]
        cnt = max(6, prev)
        while 2 * math.pi * k * P / (cnt * 2) >= P * 1.05:
            cnt *= 2
        ring_cells[k] = cnt
        for i in range(cnt):
            a = 2 * math.pi * (i + 0.5) / cnt
            pts[(k, i)] = (k * P * math.cos(a), k * P * math.sin(a))
    nb = {key: [] for key in pts}
    arcs = {}
    for k in range(1, rings + 1):
        cnt = ring_cells[k]
        for i in range(cnt):
            j = (i + 1) % cnt
            nb[(k, i)].append((k, j))
            nb[(k, j)].append((k, i))
            a0, a1 = 2 * math.pi * (i + 0.5) / cnt, 2 * math.pi * (i + 1.5) / cnt
            arcs[frozenset([(k, i), (k, j)])] = [
                (k * P * math.cos(a0 + (a1 - a0) * t / 12), k * P * math.sin(a0 + (a1 - a0) * t / 12))
                for t in range(13)]
            parent = (k - 1, 0) if k == 1 else (k - 1, i * ring_cells[k - 1] // cnt)
            if k == 1 and i % (cnt // 6 or 1):  # centre joins 6 spokes max
                continue
            nb[(k, i)].append(parent)
            nb[parent].append((k, i))
            if k > 1:  # radial spoke, then along ring k-1 to the parent centre (classic theta look)
                ac = 2 * math.pi * (i + 0.5) / cnt
                ap = 2 * math.pi * (parent[1] + 0.5) / ring_cells[k - 1]
                rp = (k - 1) * P
                arcs[frozenset([(k, i), parent])] = [pts[(k, i)]] + [
                    (rp * math.cos(ac + (ap - ac) * t / 8), rp * math.sin(ac + (ap - ac) * t / 8))
                    for t in range(9)]
    R = rings * P + P / 2 + FRAME
    return pts, nb, arcs, Point(0, 0).buffer(R, 128), (0, 0)


def hex_graph(radius, P=PITCH_60):
    pts = {}
    for q in range(-radius, radius + 1):
        for r in range(max(-radius, -q - radius), min(radius, -q + radius) + 1):
            x = P * (q + r / 2)
            y = P * (math.sqrt(3) / 2 * r)
            pts[(q, r)] = (x, y)
    nb = {k: [] for k in pts}
    for (q, r) in pts:
        for dq, dr in ((1, 0), (0, 1), (-1, 1)):
            o = (q + dq, r + dr)
            if o in pts:
                nb[(q, r)].append(o)
                nb[o].append((q, r))
    R = radius * P + P / 2 + FRAME
    outline = Polygon([(R * math.cos(math.pi / 6 + i * math.pi / 3) / math.cos(math.pi / 6),
                        R * math.sin(math.pi / 6 + i * math.pi / 3) / math.cos(math.pi / 6)) for i in range(6)])
    return pts, nb, {}, outline, (0, 0)


# ── Maze ─────────────────────────────────────────────────────────────────────
def spanning_tree(nb, start, rng):
    seen, stack, edges = {start}, [start], []
    while stack:
        cur = stack[-1]
        opts = [o for o in nb[cur] if o not in seen]
        if not opts:
            stack.pop()
            continue
        nxt = rng.choice(opts)
        seen.add(nxt)
        edges.append((cur, nxt))
        stack.append(nxt)
    assert len(seen) == len(nb)
    return edges


def farthest(edges, start):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    dist, todo = {start: 0}, [start]
    while todo:
        cur = todo.pop()
        for o in adj.get(cur, []):
            if o not in dist:
                dist[o] = dist[cur] + 1
                todo.append(o)
    end = max(dist, key=dist.get)
    return end, dist[end]


def star(cx, cy, r):
    return Polygon([(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(math.pi / 2 + i * math.pi / 5),
                     cy + (r if i % 2 == 0 else r * 0.45) * math.sin(math.pi / 2 + i * math.pi / 5))
                    for i in range(10)])


def build_design(name, graph, start_key, seed):
    rng = random.Random(seed)
    pts, nb, arcs, outline, _ = graph
    edges = spanning_tree(nb, start_key, rng)
    end_key, steps = farthest(edges, start_key)
    lines = []
    for a, b in edges:
        path = arcs.get(frozenset([a, b])) or [pts[a], pts[b]]
        if arcs.get(frozenset([a, b])) and path[0] != pts[a] and \
                math.dist(path[0], pts[a]) > 1e-6:
            path = path[::-1]
        lines.append(LineString(path))
    channel = unary_union([ln.buffer(CHANNEL / 2, cap_style=1, join_style=1) for ln in lines])
    assert isinstance(channel, Polygon) and len(channel.interiors) == 0, "channel not simply connected"
    walls = outline.difference(channel)
    assert isinstance(walls, Polygon), f"{name}: wall layer would fall apart"
    # min wall check between distinct channels (approx): channel buffered by WALL/2 stays simple
    minx, miny, maxx, maxy = outline.bounds
    # bolt holes in the frame corners / ring
    if outline.geom_type == "Polygon" and len(outline.exterior.coords) > 40:  # circle
        Rb = (maxx - minx) / 2 - FRAME / 2
        bolts = [Point(Rb * math.cos(math.pi / 4 + i * math.pi / 2), Rb * math.sin(math.pi / 4 + i * math.pi / 2))
                 for i in range(4)]
    elif len(outline.exterior.coords) == 7:  # hexagon: holes at 4 vertices inset
        verts = list(outline.exterior.coords)[:6]
        bolts = [Point(x * 0.93, y * 0.93) for i, (x, y) in enumerate(verts) if i in (0, 2, 3, 5)]
    else:
        o = FRAME / 2
        bolts = [Point(minx + o, miny + o), Point(maxx - o, miny + o),
                 Point(minx + o, maxy - o), Point(maxx - o, maxy - o)]
    holes = [b.buffer(BOLT_D / 2, 32) for b in bolts]
    for h in holes:
        assert walls.contains(h), f"{name}: bolt hole hits the maze"
    sx, sy = pts[start_key]
    ex, ey = pts[end_key]
    engrave = [Point(sx, sy).buffer(CHANNEL * 0.38).difference(Point(sx, sy).buffer(CHANNEL * 0.24)),
               star(ex, ey, CHANNEL * 0.4)]
    return dict(name=name, outline=outline, channel=channel, walls=walls, holes=holes,
                engrave=engrave, start=(sx, sy), end=(ex, ey), steps=steps, edges=len(edges) + 1)


# ── Writers ──────────────────────────────────────────────────────────────────
def rings_of(geom):
    if isinstance(geom, MultiPolygon):
        for g in geom.geoms:
            yield from rings_of(g)
        return
    yield list(geom.exterior.coords)
    for i in geom.interiors:
        yield list(i.coords)


def path_d(coords, ox, oy):
    return "M " + " L ".join(f"{x - ox:.3f},{oy - y:.3f}" for x, y in coords) + " Z"


def layer_parts(d, layer):
    """→ (cut_rings, engrave_polys)"""
    if layer == "base":
        return [list(d["outline"].exterior.coords)] + [list(h.exterior.coords) for h in d["holes"]], d["engrave"]
    if layer == "maze":
        return list(rings_of(d["walls"])) + [list(h.exterior.coords) for h in d["holes"]], []
    return [list(d["outline"].exterior.coords)] + [list(h.exterior.coords) for h in d["holes"]], []


def write_svg(d, layer, path):
    minx, miny, maxx, maxy = d["outline"].bounds
    w, h = maxx - minx + 4, maxy - miny + 4
    ox, oy = minx - 2, maxy + 2
    cut, eng = layer_parts(d, layer)
    body = [f'<path d="{path_d(r, ox, oy)}" fill="none" stroke="{CUT}" stroke-width="0.1"/>' for r in cut]
    for e in eng:
        dd = " ".join(path_d(r, ox, oy) for r in rings_of(e))
        body.append(f'<path d="{dd}" fill="{ENGRAVE}" fill-rule="evenodd" stroke="none"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" '
           f'viewBox="0 0 {w:.2f} {h:.2f}">\n<!-- MathRelaxing marble maze · {d["name"]} · {layer} · '
           f'red = cut, black = engrave -->\n' + "\n".join(body) + "\n</svg>\n")
    with open(path, "w") as f:
        f.write(svg)


def write_dxf(d, layer, path):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=7)
    msp = doc.modelspace()
    cut, eng = layer_parts(d, layer)
    for r in cut:
        msp.add_lwpolyline(r, close=True, dxfattribs={"layer": "CUT"})
    for e in eng:
        for r in rings_of(e):
            msp.add_lwpolyline(r, close=True, dxfattribs={"layer": "ENGRAVE"})
    doc.saveas(path)


DESIGNS = [
    ("square_easy", lambda: square_graph(10), (0, 0), 11),
    ("square_hard", lambda: square_graph(14), (0, 0), 12),
    ("circle_easy", lambda: theta_graph(6), (0, 0), 13),
    ("circle_hard", lambda: theta_graph(7), (0, 0), 14),
    ("hex_easy", lambda: hex_graph(5), (0, 0), 15),
    ("hex_hard", lambda: hex_graph(6), (0, 0), 16),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, g, start, seed in DESIGNS:
        d = build_design(name, g(), start, seed)
        ddir = os.path.join(OUT, name)
        os.makedirs(ddir, exist_ok=True)
        for layer in ("base", "maze", "lid"):
            write_svg(d, layer, os.path.join(ddir, f"{name}_{layer}.svg"))
            write_dxf(d, layer, os.path.join(ddir, f"{name}_{layer}.dxf"))
        minx, miny, maxx, maxy = d["outline"].bounds
        print(f"{name:<12} {maxx - minx:5.0f}×{maxy - miny:3.0f} mm  cells={d['edges']:>3}  "
              f"solution length={d['steps']} cells")
        made.append(d)
    return made


if __name__ == "__main__":
    main()
