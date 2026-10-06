"""
Tangram engine: the 7 pieces, rigid placements (45-degree rotations + flip), random
edge-to-edge assembly with overlap checks, silhouette scoring and convexity.

Units: the small triangle has legs of length 1; the full tangram square has area 8.
Every generated figure is built from the 7 pieces, so a solution always exists.
"""
import math, random, json
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

R2 = math.sqrt(2)
# canonical pieces (area): L,L = 2 each? no: small=0.5, medium=1, large=2, square=1, para=1 -> total 8
PIECES = {
    "L1": [(0, 0), (2, 0), (0, 2)],
    "L2": [(0, 0), (2, 0), (0, 2)],
    "M":  [(0, 0), (R2, 0), (0, R2)],
    "S1": [(0, 0), (1, 0), (0, 1)],
    "S2": [(0, 0), (1, 0), (0, 1)],
    "SQ": [(0, 0), (1, 0), (1, 1), (0, 1)],
    "PA": [(0, 0), (1, 0), (2, 1), (1, 1)],
}
ORDER = ["L1", "L2", "M", "SQ", "PA", "S1", "S2"]
COLORS = {"L1": (196, 64, 60), "L2": (232, 150, 52), "M": (240, 200, 70), "S1": (70, 150, 100),
          "S2": (60, 130, 190), "SQ": (120, 90, 170), "PA": (220, 100, 150)}
assert abs(sum(Polygon(p).area for p in PIECES.values()) - 8) < 1e-9


def place(name, rot, flip, dx, dy):
    p = Polygon(PIECES[name])
    if flip:
        p = affinity.scale(p, xfact=-1, yfact=1, origin=(0, 0))
    p = affinity.rotate(p, 45 * rot, origin=(0, 0))
    return affinity.translate(p, dx, dy)


def snap(p, nd=6):
    return Polygon([(round(x, nd), round(y, nd)) for x, y in p.exterior.coords])


def overlaps(p, others, eps=1e-6):
    return any(p.intersection(o).area > eps for o in others)


def touches_enough(p, others, minlen=0.45):
    return sum(p.boundary.intersection(o.boundary).length for o in others) >= minlen


def build(rng, tries=400):
    """Random edge-to-edge assembly of all 7 pieces. Returns list of (name, Polygon) or None."""
    names = ORDER[:]; rng.shuffle(names)
    placed = [(names[0], place(names[0], rng.randrange(8), 0, 0, 0))]
    for nm in names[1:]:
        ok = False
        for _ in range(tries):
            rot = rng.randrange(8); flip = rng.randrange(2) if nm == "PA" else 0
            base = place(nm, rot, flip, 0, 0)
            _, anchor = rng.choice(placed)
            av = rng.choice(list(anchor.exterior.coords)[:-1]); pv = rng.choice(list(base.exterior.coords)[:-1])
            cand = snap(affinity.translate(base, av[0] - pv[0], av[1] - pv[1]))
            others = [q for _, q in placed]
            if overlaps(cand, others) or not touches_enough(cand, others):
                continue
            placed.append((nm, cand)); ok = True; break
        if not ok:
            return None
    return placed


def silhouette(placed):
    u = unary_union([q.buffer(1e-7, join_style=2) for _, q in placed]).buffer(-1e-7, join_style=2)
    return u


def clean_poly(u, tol=1e-4):
    if u.geom_type != "Polygon" or len(u.interiors) > 0:
        return None
    return u.simplify(tol)


def n_vertices(p):
    return len(p.exterior.coords) - 1


def is_convex(p):
    return abs(p.convex_hull.area - p.area) < 1e-6


def mirror_symmetry(p):
    """Best overlap ratio with its own mirror image about a vertical or diagonal axis (1 = symmetric)."""
    c = p.centroid; best = 0
    for ang in range(0, 180, 45):
        q = affinity.rotate(affinity.scale(affinity.rotate(p, -ang, origin=c), xfact=-1, yfact=1, origin=c), ang, origin=c)
        best = max(best, p.intersection(q).area / p.area)
    return best


def compactness(p):
    return 4 * math.pi * p.area / p.length ** 2


def normalize(placed):
    """Rotate/translate so the figure sits upright-ish and starts at the origin (for rendering)."""
    u = silhouette(placed)
    minx, miny, maxx, maxy = u.bounds
    return [(n, affinity.translate(q, -minx, -miny)) for n, q in placed]


def signature(p):
    """Congruence signature: sorted side lengths and turning angles (rounded), rotation/mirror invariant."""
    pts = list(p.exterior.coords)[:-1]; n = len(pts)
    sides = [round(math.dist(pts[i], pts[(i + 1) % n]), 3) for i in range(n)]
    angs = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (a[0] - b[0], a[1] - b[1]); v2 = (c[0] - b[0], c[1] - b[1])
        angs.append(round(math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])) % 360))
    seq = list(zip(sides, angs))
    cands = []
    for s in (seq, [(sides[(n - i) % n], (360 - angs[(n - i) % n]) % 360) for i in range(n)]):
        for k in range(n):
            cands.append(tuple(s[k:] + s[:k]))
    return min(cands)


def generate(n_samples, seed=1):
    rng = random.Random(seed); out = []
    for i in range(n_samples):
        pl = build(rng)
        if not pl:
            continue
        p = clean_poly(silhouette(pl))
        if p is None:
            continue
        out.append({"placed": [(nm, list(q.exterior.coords)[:-1]) for nm, q in pl], "poly": list(p.exterior.coords)[:-1],
                    "nv": n_vertices(p), "convex": is_convex(p), "sym": round(mirror_symmetry(p), 3),
                    "compact": round(compactness(p), 3), "sig": signature(p)})
    return out


if __name__ == "__main__":
    import time
    t = time.time(); res = generate(3000, seed=7)
    conv = {r["sig"] for r in res if r["convex"]}
    print(len(res), "figures in", round(time.time() - t, 1), "s;", "convex distinct:", len(conv),
          "symmetric:", sum(r["sym"] > 0.999 for r in res))
