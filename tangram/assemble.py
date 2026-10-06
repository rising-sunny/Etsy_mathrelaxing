"""
Edge-to-edge random assembly: every new piece shares a full edge (or its whole shorter edge)
with the figure built so far, aligned at a vertex. Produces silhouettes that read as
figures (animals, people, objects) far more often than vertex-to-vertex placement.
"""
import math, random
from shapely.geometry import Polygon
from shapely import affinity
from shapely.geometry.polygon import orient
from engine import PIECES, ORDER, silhouette, clean_poly, is_convex, compactness

EPS = 1e-6


def edges(p):
    c = list(p.exterior.coords)[:-1]
    return [(c[i], c[(i + 1) % len(c)]) for i in range(len(c))]


def ang(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def variants(name):
    out = []
    for flip in ((0, 1) if name == "PA" else (0,)):
        for rot in range(8):
            p = Polygon(PIECES[name])
            if flip:
                p = affinity.scale(p, xfact=-1, yfact=1, origin=(0, 0))
            out.append(affinity.rotate(p, 45 * rot, origin=(0, 0)))
    return out


VAR = {n: variants(n) for n in PIECES}


def snap(p):
    return Polygon([(round(x, 7), round(y, 7)) for x, y in p.exterior.coords])


def candidates(name, fig_poly, others):
    """All placements of piece `name` whose edge lies along an edge of the current outline."""
    out = []
    for (a, b) in edges(orient(fig_poly, 1.0)):
        la = math.dist(a, b); da = ang(a, b)
        for v in VAR[name]:
            for (p, q) in edges(v):
                lp = math.dist(p, q)
                if lp > la + EPS:
                    continue
                dd = (ang(p, q) - da) % 360
                if abs(dd - 180) > 1e-3:
                    continue  # new edge must run antiparallel to the outline edge (q->p along a->b)
                for anchor, pt in ((a, q), (b, p)):
                    c = snap(affinity.translate(v, anchor[0] - pt[0], anchor[1] - pt[1]))
                    if any(c.intersection(o).area > EPS for o in others):
                        continue
                    out.append(c)
    return out


def build(rng, order=None):
    names = order or ORDER[:]
    if order is None:
        rng.shuffle(names)
    first = snap(rng.choice(VAR[names[0]]))
    placed = [(names[0], first)]
    for nm in names[1:]:
        fig = silhouette(placed)
        if fig.geom_type != "Polygon":
            return None
        cands = candidates(nm, fig, [q for _, q in placed])
        if not cands:
            return None
        placed.append((nm, rng.choice(cands)))
    return placed


def generate(n, seed=1):
    rng = random.Random(seed); out = []
    for _ in range(n):
        pl = build(rng)
        if not pl:
            continue
        p = clean_poly(silhouette(pl))
        if p is None or is_convex(p):
            continue
        out.append((pl, p))
    return out


if __name__ == "__main__":
    import time
    t = time.time(); r = generate(500, 3)
    print(len(r), "figures", round(time.time() - t, 1), "s")
