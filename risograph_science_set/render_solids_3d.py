"""
render_solids_3d.py — real 3D flat-shaded renders of the five Platonic solids
for the "Five Solids" riso specimen plate.

Two-pass render from the SAME transformed vertices so the layers align
pixel-for-pixel:
  - "tone" pass: matte white faces (ConvexHull-triangulated) under a single
    light -> per-face shading becomes the ink-density map (halftone layer).
  - "line" pass: the same opaque white solid (as a pure occluder, no visible
    edges of its own -- a triangulated cube would otherwise show its
    triangulation diagonal) PLUS a separate mesh built only from the true
    polyhedron edges (nearest-neighbour distance, not hull triangulation),
    rendered as flat ink tubes. VTK's own depth test hides the parts of
    those tubes that fall behind the solid -- real occlusion, no manual
    hidden-line dashing. A chroma-key in post strips the white fill.

  xvfb-run -a python3 render_solids_3d.py
"""
import os

import numpy as np
import pyvista as pv
from PIL import Image
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist, squareform

pv.OFF_SCREEN = True
BASE = os.path.dirname(os.path.abspath(__file__))
INK = (28, 26, 23)


def solid_vertices(name):
    phi = (1 + 5 ** 0.5) / 2
    if name == "tetra":
        v = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    elif name == "cube":
        v = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    elif name == "octa":
        v = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    elif name == "dodeca":
        v = [[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        for a in (-1, 1):
            for c in (-1, 1):
                v.append([0, a / phi, c * phi])
                v.append([a / phi, c * phi, 0])
                v.append([c * phi, 0, a / phi])
        v = np.array(v, float)
    else:  # icosa
        v = []
        for a in (-1, 1):
            for c in (-1, 1):
                v.append([0, a, c * phi])
                v.append([a, c * phi, 0])
                v.append([c * phi, 0, a])
        v = np.array(v, float)
    return v / np.max(np.linalg.norm(v, axis=1))


def true_edges(v):
    D = squareform(pdist(v))
    np.fill_diagonal(D, np.inf)
    dmin = D.min()
    return [(i, j) for i in range(len(v)) for j in range(i + 1, len(v)) if D[i, j] <= dmin * 1.05]


def make_mesh(name):
    v = solid_vertices(name)
    hull = ConvexHull(v)
    faces = np.hstack([np.full((len(hull.simplices), 1), 3), hull.simplices]).astype(np.int64)
    mesh = pv.PolyData(v, faces)
    mesh = mesh.compute_normals(auto_orient_normals=True)
    return mesh, true_edges(v)


LAYOUT = [
    ("tetra", (-2.65, 1.35), 1.05),
    ("cube", (0.0, 1.35), 1.0),
    ("octa", (2.65, 1.35), 1.05),
    ("dodeca", (-1.35, -1.55), 1.05),
    ("icosa", (1.35, -1.55), 1.05),
]


def build_scene():
    solids, edge_tubes = [], []
    for i, (name, (cx, cy), scale) in enumerate(LAYOUT):
        mesh, edges = make_mesh(name)
        mesh.rotate_x(24, inplace=True)
        mesh.rotate_y(34 + i * 6, inplace=True)
        mesh.points *= scale
        mesh.points[:, 0] += cx
        mesh.points[:, 1] += cy
        solids.append(mesh)

        pts = mesh.points
        edge_radius = 0.022 * scale
        tubes = [pv.Line(pts[a], pts[b]).tube(radius=edge_radius, n_sides=14) for a, b in edges]
        merged = tubes[0]
        for t in tubes[1:]:
            merged = merged.merge(t)
        edge_tubes.append(merged)
    return solids, edge_tubes


def render_pass(solids, edge_tubes, mode, px=2000):
    pl = pv.Plotter(off_screen=True, window_size=(px, px), lighting="none")
    pl.set_background("white")
    pl.enable_parallel_projection()
    if mode == "tone":
        for m in solids:
            pl.add_mesh(m, color="white", show_edges=False, smooth_shading=False,
                        ambient=0.30, diffuse=0.95, specular=0.0)
        pl.add_light(pv.Light(position=(6, 8, 10), focal_point=(0, 0, 0), color="white",
                               intensity=1.0, light_type="scenelight"))
        pl.add_light(pv.Light(position=(-6, -4, 6), focal_point=(0, 0, 0), color="white",
                               intensity=0.35, light_type="scenelight"))
    else:
        for m in solids:
            pl.add_mesh(m, color="white", show_edges=False, ambient=1.0, diffuse=0.0, specular=0.0)
        for e in edge_tubes:
            pl.add_mesh(e, color=INK, ambient=1.0, diffuse=0.0, specular=0.0)
    pl.camera_position = "xy"
    pl.reset_camera()
    img = pl.screenshot(transparent_background=True, return_img=True)
    pl.close()
    return img


def main():
    solids, edge_tubes = build_scene()
    tone = render_pass(solids, edge_tubes, "tone").astype(np.float32)
    line = render_pass(solids, edge_tubes, "line").astype(np.float32)

    alpha_sil = tone[..., 3]
    lum = tone[..., :3].mean(axis=-1)
    ink = np.clip(1.0 - lum / 255.0, 0.0, 1.0)
    ink = 0.12 + 0.55 * ink
    out_alpha = np.where(alpha_sil > 10, ink * 255, 0).astype(np.uint8)
    tone_out = np.zeros((*ink.shape, 4), dtype=np.uint8)
    tone_out[..., 3] = out_alpha
    Image.fromarray(tone_out, "RGBA").save(os.path.join(BASE, "_solids_tone.png"))

    rgb = line[..., :3]
    dist_white = np.linalg.norm(rgb - 255, axis=-1)
    is_ink = (dist_white > 40) & (line[..., 3] > 10)
    line_out = np.zeros((*is_ink.shape, 4), dtype=np.uint8)
    line_out[is_ink, 0:3] = INK
    line_out[is_ink, 3] = 255
    Image.fromarray(line_out, "RGBA").save(os.path.join(BASE, "_solids_line.png"))
    print("wrote _solids_tone.png, _solids_line.png")


if __name__ == "__main__":
    main()
