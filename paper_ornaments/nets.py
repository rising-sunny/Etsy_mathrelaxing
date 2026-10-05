"""
Exact polyhedra + automatic unfolding into printable nets.

  polyhedron(name)            -> (V, faces) with edge length 1, faces CCW seen from outside
  unfold(V, faces, ...)       -> best non-overlapping net (face polygons in 2D, fold edges)
  add_tabs(net)               -> glue tabs on every cut edge, checked against overlaps
  spike_net(n, L)             -> open pyramid "point" for stars (n-gon base, lateral edge L)

Everything is in edge-length units; the renderer scales to the page.
"""
import math, random, itertools
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity

PHI = (1 + 5 ** 0.5) / 2


# ------------------------------------------------------------------ solids
def _perms(v, signs=True, cyclic=False):
    out = set()
    base = [tuple(v)] if not cyclic else [(v[0], v[1], v[2]), (v[1], v[2], v[0]), (v[2], v[0], v[1])]
    perms = base if cyclic else list(itertools.permutations(v))
    for p in perms:
        for s in itertools.product(*[(1, -1) if x else (1,) for x in p]):
            out.add(tuple(a * b for a, b in zip(p, s)))
    return list(out)


POINTS = {
    "Tetrahedron": [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
    "Cube": _perms((1, 1, 1)),
    "Octahedron": _perms((1, 0, 0)),
    "Dodecahedron": _perms((1, 1, 1)) + _perms((0, 1 / PHI, PHI), cyclic=True),
    "Icosahedron": _perms((0, 1, PHI), cyclic=True),
    "Cuboctahedron": _perms((1, 1, 0)),
    "Truncated Octahedron": _perms((0, 1, 2)),
    "Rhombicuboctahedron": _perms((1, 1, 1 + 2 ** 0.5)),
    "Truncated Icosahedron": _perms((0, 1, 3 * PHI), cyclic=True) + _perms((1, 2 + PHI, 2 * PHI), cyclic=True)
                             + _perms((PHI, 2, 2 * PHI + 1), cyclic=True),
}


def polyhedron(name):
    P = np.array(POINTS[name], float)
    hull = ConvexHull(P)
    groups = {}
    for simplex, eq in zip(hull.simplices, hull.equations):
        key = tuple(np.round(eq, 6))
        groups.setdefault(key, set()).update(simplex.tolist())
    faces = []
    for key, idx in groups.items():
        n = np.array(key[:3]); idx = list(idx)
        c = P[idx].mean(axis=0)
        u = P[idx[0]] - c; u /= np.linalg.norm(u); v = np.cross(n, u)
        ang = [math.atan2(np.dot(P[i] - c, v), np.dot(P[i] - c, u)) for i in idx]
        faces.append([i for _, i in sorted(zip(ang, idx))])  # CCW about outward normal
    # scale to edge length 1
    e = min(np.linalg.norm(P[f[0]] - P[f[1]]) for f in faces)
    used = sorted({i for f in faces for i in f})
    remap = {o: k for k, o in enumerate(used)}
    V = P[used] / e
    faces = [[remap[i] for i in f] for f in faces]
    return V, faces


def euler(faces):
    E = {tuple(sorted((f[i], f[(i + 1) % len(f)]))) for f in faces for i in range(len(f))}
    Vn = len({i for f in faces for i in f})
    return len(faces), len(E), Vn


# ------------------------------------------------------------------ unfolding
def _local2d(V, f):
    P = V[f]; c = P.mean(axis=0)
    n = np.cross(P[1] - P[0], P[2] - P[0]); n /= np.linalg.norm(n)
    if np.dot(n, c) < 0:
        n = -n
    u = P[1] - P[0]; u /= np.linalg.norm(u); v = np.cross(n, u)
    return np.array([[np.dot(p - P[0], u), np.dot(p - P[0], v)] for p in P])


def _adjacency(faces):
    edge_faces = {}
    for fi, f in enumerate(faces):
        for i in range(len(f)):
            e = tuple(sorted((f[i], f[(i + 1) % len(f)])))
            edge_faces.setdefault(e, []).append(fi)
    adj = {fi: [] for fi in range(len(faces))}
    for e, fs in edge_faces.items():
        a, b = fs
        adj[a].append((b, e)); adj[b].append((a, e))
    return adj, edge_faces


def _place(V, faces, tree_order):
    """tree_order: list of (child, parent, edge) with root first (parent None)."""
    loc = {}
    pos = {}  # face -> {vertex: 2D}
    for child, parent, e in tree_order:
        L = _local2d(V, faces[child]); f = faces[child]
        if parent is None:
            pos[child] = {v: L[k] for k, v in enumerate(f)}
            continue
        a, b = e
        ka, kb = f.index(a), f.index(b)
        pa, pb = pos[parent][a], pos[parent][b]
        la, lb = L[ka], L[kb]
        ang = math.atan2(*(pb - pa)[::-1]) - math.atan2(*(lb - la)[::-1])
        R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        pos[child] = {v: R @ (L[k] - la) + pa for k, v in enumerate(f)}
    return pos


def _overlaps(polys, tol=1e-6):
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            if polys[i].intersection(polys[j]).area > tol:
                return True
    return False


def _best_rotation(points, aspect):
    """Rotation angle that minimises the scale-limiting dimension for a page of given aspect (w/h)."""
    best = None
    for deg in range(0, 180, 2):
        a = math.radians(deg); c, s = math.cos(a), math.sin(a)
        xs = points[:, 0] * c - points[:, 1] * s; ys = points[:, 0] * s + points[:, 1] * c
        w, h = xs.ptp() if hasattr(xs, "ptp") else np.ptp(xs), np.ptp(ys)
        k = max(w / aspect, h)  # height-equivalent size
        if best is None or k < best[0]:
            best = (k, deg)
    return best


def unfold(V, faces, aspect=0.8, tries=600, seed=1):
    adj, edge_faces = _adjacency(faces)
    rnd = random.Random(seed)
    cands = []
    for t in range(tries):
        root = rnd.randrange(len(faces))
        seen = {root}; order = [(root, None, None)]
        frontier = [root]
        mode = t % 3  # 0 BFS, 1 DFS, 2 random
        while frontier:
            if mode == 0:
                cur = frontier.pop(0)
            elif mode == 1:
                cur = frontier.pop()
            else:
                cur = frontier.pop(rnd.randrange(len(frontier)))
            nb = adj[cur][:]; rnd.shuffle(nb)
            for (o, e) in nb:
                if o not in seen:
                    seen.add(o); order.append((o, cur, e)); frontier.append(o)
        pos = _place(V, faces, order)
        polys = [Polygon([pos[fi][v] for v in faces[fi]]) for fi in range(len(faces))]
        if _overlaps(polys):
            continue
        pts = np.array([p for fi in pos for p in pos[fi].values()])
        k, deg = _best_rotation(pts, aspect)
        cands.append((k, t, deg, order, pos))
    if not cands:
        raise RuntimeError("no non-overlapping unfolding found")
    cands.sort(key=lambda c: (c[0], c[1]))
    for k, _, deg, order, pos in cands:
        net = _finish(faces, edge_faces, deg, order, pos)
        try:
            net = add_tabs(net)
        except RuntimeError:
            continue
        net = compact_rotation(net, aspect)
        return net
    raise RuntimeError("no unfolding with room for tabs")


def _finish(faces, edge_faces, deg, order, pos):
    a = math.radians(deg); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    pos = {fi: {v: R @ p for v, p in d.items()} for fi, d in pos.items()}
    folds = [(fi, par, e) for fi, par, e in order if par is not None]
    tree_edges = {e for _, _, e in folds}
    cuts = [(e, fs) for e, fs in edge_faces.items() if e not in tree_edges]
    face_polys = [[tuple(pos[fi][v]) for v in faces[fi]] for fi in range(len(faces))]
    fold_segs = [(tuple(pos[fi][e[0]]), tuple(pos[fi][e[1]])) for fi, _, e in folds]
    return {"faces": face_polys, "folds": fold_segs, "cuts": cuts, "pos": pos, "face_idx": faces}


def _tab(p, q, inward_ref, w, taper):
    """Trapezoid tab on segment p-q, on the side away from inward_ref."""
    p, q = np.array(p), np.array(q); d = q - p; L = np.linalg.norm(d); d /= L
    n = np.array([-d[1], d[0]])
    if np.dot(np.array(inward_ref) - p, n) > 0:
        n = -n
    off = w / math.tan(math.radians(taper))
    off = min(off, L * 0.4)
    return [tuple(p), tuple(q), tuple(q - d * off + n * w), tuple(p + d * off + n * w)]


def add_tabs(net, w=0.22):
    polys = [Polygon(f) for f in net["faces"]]
    occupied = unary_union(polys)
    tabs = []
    for e, (fa, fb) in net["cuts"]:
        placed = False
        for fi in (fa, fb):
            p, q = net["pos"][fi][e[0]], net["pos"][fi][e[1]]
            cen = np.mean(net["faces"][fi], axis=0)
            for ww, taper in ((w, 45), (w, 32), (w * 0.7, 28), (w * 0.5, 24)):
                t = Polygon(_tab(p, q, cen, ww, taper))
                if t.intersection(occupied).area < 1e-6:
                    tabs.append(list(t.exterior.coords)[:-1]); occupied = occupied.union(t); placed = True
                    break
            if placed:
                break
        if not placed:  # trimmed tab: cut back wherever it would touch another piece
            for fi in (fa, fb):
                p, q = net["pos"][fi][e[0]], net["pos"][fi][e[1]]
                cen = np.mean(net["faces"][fi], axis=0)
                t = Polygon(_tab(p, q, cen, w * 0.8, 40))
                others = unary_union([pl for k, pl in enumerate(polys) if k != fi] + [Polygon(x) for x in tabs])
                cl = t.difference(others.buffer(0.03))
                if cl.geom_type == "MultiPolygon":
                    cl = max(cl.geoms, key=lambda g: g.area)
                if not cl.is_empty and cl.area >= 0.2 * t.area and cl.distance(LineString([p, q]).interpolate(0.5, normalized=True)) < 1e-6:
                    cl = cl.simplify(0.002)
                    tabs.append(list(cl.exterior.coords)[:-1]); occupied = occupied.union(cl); placed = True
                    break
        if not placed:
            raise RuntimeError("tab could not be placed")
    net["tabs"] = tabs
    return net


# ------------------------------------------------------------------ star points
def spike_net(n, L, s=1.0, tab_w=0.22):
    """Open n-sided pyramid: n isosceles triangles (base s, sides L) fanned around the apex,
    one side glue tab and base tabs that glue onto the core face."""
    th = 2 * math.asin(s / (2 * L))
    assert n * th < 2 * math.pi
    apex = np.array([0.0, 0.0])
    rim = [apex + L * np.array([math.cos(k * th), math.sin(k * th)]) for k in range(n + 1)]
    faces = [[tuple(apex), tuple(rim[k]), tuple(rim[k + 1])] for k in range(n)]
    folds = [(tuple(apex), tuple(rim[k])) for k in range(1, n)]
    tabs = []
    for k in range(n):  # base tabs
        cen = np.mean(faces[k], axis=0)
        tabs.append(_tab(rim[k], rim[k + 1], cen, tab_w * 0.9, 55))
        folds.append((tuple(rim[k]), tuple(rim[k + 1])))
    cen = np.mean(faces[-1], axis=0)  # side glue tab on the last lateral edge
    tabs.append(_tab(apex, rim[n], cen, tab_w, 70))
    folds.append((tuple(apex), tuple(rim[n])))
    return {"faces": faces, "folds": folds, "tabs": tabs}


def outline(net):
    return unary_union([Polygon(f) for f in net["faces"]] + [Polygon(t) for t in net["tabs"]])


def bounds(net):
    pts = np.array([p for f in net["faces"] + net["tabs"] for p in f])
    return pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()


def rotate_net(net, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    R = lambda p: (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
    out = dict(net)
    out["faces"] = [[R(p) for p in f] for f in net["faces"]]
    out["tabs"] = [[R(p) for p in t] for t in net["tabs"]]
    out["folds"] = [(R(a_), R(b_)) for a_, b_ in net["folds"]]
    return out


def compact_rotation(net, aspect):
    pts = np.array([p for f in net["faces"] + net["tabs"] for p in f])
    k, deg = _best_rotation(pts, aspect)
    return rotate_net(net, deg)


if __name__ == "__main__":
    for name in POINTS:
        V, F = polyhedron(name)
        f, e, v = euler(F)
        net = unfold(V, F)
        x0, y0, x1, y1 = bounds(net)
        print(f"{name:24s} F={f:2d} E={e:2d} V={v:2d}  F-E+V={f - e + v}  net {x1 - x0:5.2f} x {y1 - y0:5.2f} edges")
