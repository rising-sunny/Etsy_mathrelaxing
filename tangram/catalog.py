"""
Builds the final puzzle catalogue (out/catalog.json): 50 tangram silhouettes, each with a
verified 7-piece solution, in four levels.

  python catalog.py
"""
import os, json, warnings
warnings.filterwarnings("ignore")
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
import grid, solver, classics
from engine import silhouette, PIECES

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")

GRID = {
    "House": [".ba.", "b##a", ".##.", ".##."],
    "Sailboat": [".ba..", "b##a.", "c###d"],
    "Rocket": [".ba.", ".##.", ".##.", "b##a"],
    "Pine Tree": [".ba.", "b##a", ".ba.", "b##a"],
    "Crown": ["a..b", "#ab#", "####"],
    "Hammer": ["####", ".##.", ".##."],
    "Mushroom": ["b##a", "c##d", ".##."],
    "Chair": ["##", "#.", "###", "#.#"],
    "Gem": ["####", "c##d", ".cd."],
    "Viking Ship": ["a...b", "#a.b#", "c###d"],
    "Lamp": ["b##a", ".##.", "b##a"],
    "Hourglass": ["c##d", ".##.", "b##a"],
}
# picked by eye from the edge-to-edge generator (index into cands.json, seed 11, n 6000)
RANDOM = {
    "Sleigh": 230, "Christmas Stocking": 93, "Teapot": 116, "Goblet": 163, "Jug": 117, "Duckling": 21,
    "Duck": 143, "Angelfish": 179, "Whale": 156, "Horse": 78, "Walking Cat": 52, "Heron": 238,
    "Kangaroo": 231, "Sitting Man": 234, "Seahorse": 124, "Steamboat": 241, "Goose": 252,
    "Number Two": 259, "Dog": 301, "Truck": 245, "Race Car": 255, "Squirrel": 312, "Rabbit": 141,
}
MEDIUM = ["Cat", "Rabbit", "Fish", "Sleigh", "Christmas Stocking", "Teapot", "Goblet", "Jug", "Duck",
          "Whale", "Walking Cat", "Steamboat", "Truck"]
HARD = ["Duckling", "Angelfish", "Horse", "Heron", "Kangaroo", "Sitting Man", "Seahorse", "Goose",
        "Number Two", "Dog", "Race Car", "Squirrel"]
TYPE2NAME = {"L": ["L1", "L2"], "S": ["S1", "S2"], "M": ["M"], "SQ": ["SQ"], "PA": ["PA"]}


def from_solver(sol):
    used = {k: list(v) for k, v in TYPE2NAME.items()}
    return [(used[t].pop(0), q) for t, rot, flip, q in sol]


def normalize(placed):
    u = silhouette(placed); mx, my = u.bounds[0], u.bounds[1]
    return [(n, affinity.translate(g, -mx, -my)) for n, g in placed]


def check(placed):
    names = sorted(n for n, _ in placed); assert names == sorted(PIECES), names
    for i, (a, g) in enumerate(placed):
        for b, h in placed[i + 1:]:
            assert g.intersection(h).area < 1e-6, (a, b)
    for n, g in placed:
        assert abs(g.area - Polygon(PIECES[n]).area) < 1e-6


def record(name, level, placed):
    placed = normalize(placed); check(placed)
    if level == 4 and silhouette(placed).bounds[3] > silhouette(placed).bounds[2] + 1e-6:
        placed = normalize([(n, affinity.rotate(g, 90, origin=(0, 0))) for n, g in placed])
    sil = silhouette(placed).simplify(1e-6)
    geoms = list(getattr(sil, "geoms", [sil]))
    return {"name": name, "level": level,
            "pieces": [[n, [[round(x, 6), round(y, 6)] for x, y in list(g.exterior.coords)[:-1]]] for n, g in placed],
            "outline": [[[round(x, 6), round(y, 6)] for x, y in list(g.exterior.coords)[:-1]] for g in geoms],
            "w": round(sil.bounds[2], 4), "h": round(sil.bounds[3], 4)}


def canon(p):
    """Congruence key: smallest sorted vertex list over the 16 rotations/reflections by 45 degrees."""
    best = None
    for fl in (1, -1):
        for r in range(8):
            q = affinity.rotate(affinity.scale(p, fl, 1, origin=(0, 0)), 45 * r, origin=(0, 0))
            q = affinity.translate(q, -q.bounds[0], -q.bounds[1])
            k = tuple(sorted((round(x, 4) + 0.0, round(y, 4) + 0.0) for x, y in list(q.exterior.coords)[:-1]))
            best = k if best is None or k < best else best
    return best


def main():
    cat = []
    for nm, rows in GRID.items():
        sol = solver.solve(grid.parse(rows)); assert sol, nm
        cat.append(record(nm, 1, from_solver(sol[0])))
    C = json.load(open(os.path.join(OUT, "cands.json")))
    figs = {}
    for nm, fn in classics.FIGS.items():
        figs[nm] = fn().placed()
    for nm, i in RANDOM.items():
        figs[nm] = [(n, Polygon(pts)) for n, pts in C[i]["placed"]]
    for nm in MEDIUM:
        cat.append(record(nm, 2, figs[nm]))
    for nm in HARD:
        cat.append(record(nm, 3, figs[nm]))
    conv = solver.convex_candidates(); seen = set(); k = 0
    names = {3: "Triangle", 4: "Quadrilateral", 5: "Pentagon", 6: "Hexagon"}
    shapes = []
    for c in conv:
        s = solver.solve(c)
        if not s:
            continue
        sig = canon(c)
        if sig in seen:
            continue
        seen.add(sig); shapes.append((len(c.exterior.coords) - 1, c.length, s[0]))
    shapes.sort(key=lambda t: (t[0], t[1]))
    from collections import Counter
    cnt = Counter(); tot = Counter(t[0] for t in shapes)
    for nv, _, s in shapes:
        cnt[nv] += 1
        nm = f"Convex {names[nv]}" + (f" {cnt[nv]}" if tot[nv] > 1 else "")
        cat.append(record(nm, 4, from_solver(s)))
    json.dump(cat, open(os.path.join(HERE, "catalog.json"), "w"), indent=0)
    from collections import Counter as C2
    print(len(cat), "puzzles", dict(C2(r["level"] for r in cat)))
    print("max w/h:", max(r["w"] for r in cat), max(r["h"] for r in cat))
    big = sorted(cat, key=lambda r: -max(r["w"], r["h"]))[:6]
    print([(r["name"], r["w"], r["h"]) for r in big])


if __name__ == "__main__":
    main()
