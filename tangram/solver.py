"""
Exact tangram solver: given a target silhouette (shapely Polygon, small-triangle legs = 1),
find a placement of the 7 pieces that tiles it, by depth-first search on the
lowest-leftmost uncovered corner (the piece covering that corner must have it as its own
lowest-leftmost vertex, so each orientation gives exactly one candidate position).
Also enumerates the convex tangram shapes (Wang & Hsiung, 1942: there are 13).
"""
import math, itertools
from shapely.geometry import Polygon
from shapely import affinity
from engine import PIECES

EPS = 1e-6
COUNTS = {"L": 2, "M": 1, "S": 2, "SQ": 1, "PA": 1}
BASE = {"L": PIECES["L1"], "M": PIECES["M"], "S": PIECES["S1"], "SQ": PIECES["SQ"], "PA": PIECES["PA"]}


def key(pt):
    return (round(pt[1], 5), round(pt[0], 5))


def orientations(t):
    seen, out = set(), []
    for flip in ((0, 1) if t == "PA" else (0,)):
        for rot in range(8):
            p = Polygon(BASE[t])
            if flip:
                p = affinity.scale(p, xfact=-1, yfact=1, origin=(0, 0))
            p = affinity.rotate(p, 45 * rot, origin=(0, 0))
            pts = list(p.exterior.coords)[:-1]
            mn = min(pts, key=key)
            q = affinity.translate(p, -mn[0], -mn[1])
            sig = tuple(sorted((round(x, 5), round(y, 5)) for x, y in list(q.exterior.coords)[:-1]))
            if sig in seen:
                continue
            seen.add(sig); out.append((rot, flip, q))
    return out


ORIENT = {t: orientations(t) for t in COUNTS}


def corner(region):
    geoms = getattr(region, "geoms", [region])
    pts = [c for g in geoms for ring in [g.exterior] + list(g.interiors) for c in ring.coords]
    return min(pts, key=key)


def solve(target, limit=1):
    sols = []
    counts = dict(COUNTS)

    def rec(region, placed):
        if region.area < EPS:
            sols.append(list(placed)); return len(sols) >= limit
        c = corner(region)
        for t in COUNTS:
            if counts[t] == 0:
                continue
            for rot, flip, q in ORIENT[t]:
                cand = affinity.translate(q, c[0], c[1])
                if cand.difference(region).area > EPS:
                    continue
                rest = region.difference(cand)
                rest = rest.buffer(1e-9, join_style=2).buffer(-1e-9, join_style=2) if rest.area > EPS else rest
                counts[t] -= 1; placed.append((t, rot, flip, cand))
                done = rec(rest, placed)
                placed.pop(); counts[t] += 1
                if done:
                    return True
        return False

    if abs(target.area - 8) > 1e-4:
        return []
    rec(target, [])
    return sols


def convex_candidates():
    """Convex lattice polygons with edges in the 4 tangram directions, integer vertices, area 8."""
    out = {}
    from engine import signature
    R = range(0, 9)
    for a, b in itertools.product(range(1, 9), repeat=2):
        for p in range(0, a + b + 1):
            for q in range(p + 1, a + b + 1):
                for r in range(-b, a + 1):
                    for s in range(r + 1, a + 1):
                        box = Polygon([(0, 0), (a, 0), (a, b), (0, b)])
                        big = 50
                        hp = [Polygon([(-big, p + big), (p + big, -big), (big * 3, big * 3)]),   # x+y >= p
                              Polygon([(-big, q + big), (q + big, -big), (-big * 3, -big * 3)]),  # x+y <= q
                              Polygon([(r - big, -big), (r + big, big), (big * 3, -big * 3)]),    # x-y >= r
                              Polygon([(s - big, -big), (s + big, big), (-big * 3, big * 3)])]    # x-y <= s
                        poly = box
                        for h in hp:
                            poly = poly.intersection(h)
                        if poly.is_empty or abs(poly.area - 8) > 1e-6 or poly.geom_type != "Polygon":
                            continue
                        mnx, mny, mxx, mxy = poly.bounds
                        if abs(mnx) > EPS or abs(mny) > EPS or abs(mxx - a) > EPS or abs(mxy - b) > EPS:
                            continue
                        poly = poly.simplify(1e-9)
                        out.setdefault(signature(poly), poly)
    return list(out.values())


if __name__ == "__main__":
    import time
    t = time.time(); cands = convex_candidates()
    print(len(cands), "convex lattice candidates", round(time.time() - t, 1), "s")
    ok = 0
    for c in cands:
        s = solve(c)
        ok += bool(s)
        print(len(c.exterior.coords) - 1, "sides", "SOLVED" if s else "-")
    print("tangram-convex:", ok)
