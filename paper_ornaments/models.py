"""
The 12 ornaments: solids + stars, face colouring, 3D models (for renders) and the
2D pieces to print (nets / star points) at real size in centimetres.
"""
import math
import numpy as np
import nets as N

TARGET_D = 9.0  # finished ornament diameter (cm) for the solids
PAL = ["red", "pine", "gold", "navy"]

SOLIDS = [  # (name, group, difficulty 1-3)
    ("Tetrahedron", "Platonic", 1), ("Cube", "Platonic", 1), ("Octahedron", "Platonic", 1),
    ("Dodecahedron", "Platonic", 2), ("Icosahedron", "Platonic", 2),
    ("Cuboctahedron", "Archimedean", 2), ("Truncated Octahedron", "Archimedean", 2),
    ("Rhombicuboctahedron", "Archimedean", 3), ("Truncated Icosahedron", "Archimedean", 3),
]
STARS = [("Stella Octangula", "Star", 2), ("Kepler Star", "Star", 3), ("Moravian Star", "Star", 3)]


def colour_faces(faces):
    adj, _ = N._adjacency(faces)
    col = {}
    # faces with the same number of sides share a colour family when possible
    for fi in sorted(range(len(faces)), key=lambda i: -len(adj[i])):
        used = {col[o] for o, _ in adj[fi] if o in col}
        pref = [c for c in range(len(PAL)) if c not in used]
        col[fi] = pref[(len(faces[fi]) + fi) % len(pref)] if pref else 0
    return [PAL[col[i]] for i in range(len(faces))]


def _face_frame(V, f):
    P = V[f]; c = P.mean(axis=0); n = np.cross(P[1] - P[0], P[2] - P[0]); n /= np.linalg.norm(n)
    if np.dot(n, c) < 0:
        n = -n
    return c, n


def solid(name, group, diff, page_aspect):
    V, F = N.polyhedron(name)
    net = N.unfold(V, F, aspect=page_aspect)
    cols = colour_faces(F)
    R = max(np.linalg.norm(V, axis=1))
    edge_cm = TARGET_D / (2 * R)
    f, e, v = N.euler(F)
    return {"name": name, "group": group, "diff": diff, "edge_cm": edge_cm, "fev": (f, e, v),
            "pieces": [{"net": net, "colors": cols, "count": 1, "label": f"{name} - 1 piece"}],
            "model3d": [(V[fc], cols[i]) for i, fc in enumerate(F)], "diameter_cm": TARGET_D}


def star(name, diff, page_aspect):
    if name == "Stella Octangula":
        core, spikes = "Octahedron", lambda nsides: 1.0  # regular tetrahedra on every face
        target = 10.0; pal = ["gold", "red"]
    elif name == "Kepler Star":
        core, spikes = "Dodecahedron", lambda nsides: N.PHI  # golden-triangle points
        target = 11.0; pal = ["gold", "red", "pine"]
    else:
        core = "Rhombicuboctahedron"; target = 12.0; pal = ["gold", "red"]
    V, F = N.polyhedron(core)
    # spike lateral edge per face type
    Lmap = {}
    if name == "Moravian Star":
        tips = {}
        for f in F:
            c, n = _face_frame(V, f)
            r_in = np.dot(c, n); r_c = np.linalg.norm(V[f[0]] - c)
            tips.setdefault(len(f), (r_in, r_c))
        R_tip = tips[4][0] + 2.4
        for k, (r_in, r_c) in tips.items():
            h = R_tip - r_in; Lmap[k] = math.hypot(h, r_c)
    else:
        for f in F:
            Lmap[len(f)] = spikes(len(f))
    def face_col(i, f):
        if name == "Moravian Star":
            return "gold" if len(f) == 4 else "red"
        if name == "Kepler Star":
            return pal[i % 3]
        return pal[i % 2]

    # 3D model with spikes
    model = []; tipR = 0
    for i, f in enumerate(F):
        c, n = _face_frame(V, f)
        r_c = np.linalg.norm(V[f[0]] - c); L = Lmap[len(f)]
        h = math.sqrt(max(L * L - r_c * r_c, 1e-9)); apex = c + n * h
        tipR = max(tipR, np.linalg.norm(apex))
        for k in range(len(f)):
            model.append((np.array([V[f[k]], V[f[(k + 1) % len(f)]], apex]), face_col(i, f)))
    edge_cm = target / (2 * tipR)
    corenet = N.unfold(V, F, aspect=page_aspect)
    pieces = [{"net": corenet, "colors": ["cream"] * len(F), "count": 1, "label": f"Core ({core}) - 1 piece"}]
    kinds = {}
    for i, f in enumerate(F):
        kinds.setdefault(len(f), []).append(i)
    for nsides, idx in sorted(kinds.items(), key=lambda t: -t[0]):
        sn = N.spike_net(nsides, Lmap[nsides])
        cols_used = [face_col(i, F[i]) for i in idx]
        shape = {3: "triangle", 4: "square", 5: "pentagon"}[nsides]
        pieces.append({"net": sn, "spike_colors": cols_used, "count": len(idx),
                       "label": f"Points on {shape} faces - make {len(idx)}"})
    f, e, v = N.euler(F)
    return {"name": name, "group": "Star", "diff": diff, "edge_cm": edge_cm, "fev": None, "core": core,
            "pieces": pieces, "model3d": model, "diameter_cm": target, "spikes": Lmap}


def all_models(page_aspect=0.78):
    out = [solid(n, g, d, page_aspect) for n, g, d in SOLIDS]
    out += [star(n, d, page_aspect) for n, _, d in STARS]
    return out


if __name__ == "__main__":
    for m in all_models():
        print(f"{m['name']:22s} edge {m['edge_cm']:.2f} cm  pieces {[p['count'] for p in m['pieces']]}")
