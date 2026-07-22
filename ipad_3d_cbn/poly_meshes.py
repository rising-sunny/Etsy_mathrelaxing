"""
poly_meshes.py — polyhedra & subdivided meshes for the 3D color-by-number app.
Provides triangle meshes (vertices + triangular faces) for the Platonic solids,
a geodesic sphere, plus the parametric surfaces from math_meshes (torus, gem,
Möbius). Each figure is subdivided to land ~60-200 colourable triangular cells.
"""
import os
import sys
import math
import numpy as np

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lulu_books", "core"))
from math_meshes import gen_torus, gen_sphere_bumpy, gen_mobius, add_noise

PHI = (1 + math.sqrt(5)) / 2


def _norm(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


# ── Base Platonic triangle meshes ─────────────────────────────────────────────

def tetrahedron():
    v = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    f = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
    return v, f


def octahedron():
    v = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    f = [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
         [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]]
    return v, f


def cube():
    v = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    # 6 quad faces -> 12 triangles (CCW outward)
    quads = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
             [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    f = []
    for q in quads:
        f.append([q[0], q[1], q[2]]); f.append([q[0], q[2], q[3]])
    return v, f


def icosahedron():
    v = np.array([
        [-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0],
        [0, -1, PHI], [0, 1, PHI], [0, -1, -PHI], [0, 1, -PHI],
        [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1]], float)
    f = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
         [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
         [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
         [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    return v, f


def dodecahedron():
    """Dual of the icosahedron: face-centroids become vertices; each icosa
    vertex becomes a pentagon, triangulated by a centroid fan."""
    iv, iff = icosahedron()
    cents = _norm([np.mean([iv[i] for i in fa], axis=0) for fa in iff])
    verts = list(cents)
    faces = []
    for vi in range(len(iv)):
        adj = [fi for fi, fa in enumerate(iff) if vi in fa]           # 5 faces
        pts = np.array([cents[fi] for fi in adj])
        c = pts.mean(axis=0)
        nrm = _norm(iv[vi])
        # order the 5 face-centroids by angle around the vertex normal
        ref = _norm(pts[0] - c)
        b = np.cross(nrm, ref)
        ang = [math.atan2(np.dot(p - c, b), np.dot(p - c, ref)) for p in pts]
        order = [adj[k] for k in np.argsort(ang)]
        ci = len(verts); verts.append(c)                             # pentagon centroid
        for k in range(5):
            faces.append([order[k], order[(k + 1) % 5], ci])
    return np.array(verts, float), faces


# ── Subdivision ───────────────────────────────────────────────────────────────

def subdivide(verts, faces, n=1, project=False):
    verts = [np.asarray(v, float) for v in verts]
    if project:                                   # put base verts on the unit sphere too
        verts = [v / np.linalg.norm(v) for v in verts]
    for _ in range(n):
        mid = {}
        new_faces = []

        def midpoint(a, b):
            key = (min(a, b), max(a, b))
            if key not in mid:
                m = (verts[a] + verts[b]) / 2
                if project:
                    m = m / np.linalg.norm(m)
                mid[key] = len(verts); verts.append(m)
            return mid[key]
        for (a, b, c) in faces:
            ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
            new_faces += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
        faces = new_faces
    return np.array(verts, float), faces


# ── The figure library (name, verts, faces, scale-to-unit) ───────────────────

def _from_grid(verts_flat, tris_from_gridfn):
    pass


def figure_library():
    figs = []

    def add(name, v, f):
        v = np.asarray(v, float)
        v = v - v.mean(axis=0)
        v = v / np.abs(v).max()
        figs.append((name, v, f))

    # ── led by the COMPLEX, richly-faceted figures (best lighting payoff) ──
    v, f = subdivide(*icosahedron(), n=2, project=True); add("Geodesic Sphere", v, f)  # 320
    vg, fg = gen_sphere_bumpy(bumps=6, bump_depth=0.09, u_steps=15, v_steps=12)
    add("Faceted Gem", add_noise(vg, 0.005, seed=2), fg)                    # ~336, convex crystal
    vt, ft = gen_torus(R=1.0, r=0.42, u_steps=15, v_steps=9)
    add("Torus", add_noise(vt, 0.015, seed=1), ft)                          # ~252
    v, f = dodecahedron();                        add("Dodecahedron", v, f)  # 60
    v, f = subdivide(*icosahedron(), n=1);        add("Icosahedron", v, f)   # 80
    v, f = subdivide(*octahedron(), n=2);         add("Octahedron", v, f)    # 128
    v, f = subdivide(*cube(), n=2);               add("Cube", v, f)          # 192
    v, f = subdivide(*tetrahedron(), n=2);        add("Tetrahedron", v, f)   # 64
    return figs


if __name__ == "__main__":
    for name, v, f in figure_library():
        print(f"{name:18} verts={len(v):4d} faces={len(f)}")
