"""
generate_tesseract_render.py — pyvista/VTK render of a tesseract (4D hypercube).

Standalone script (must run under xvfb-run for headless OpenGL) that produces
a single high-resolution transparent PNG: the 16 vertices of a tesseract
{-1,1}^4, rotated in 4D (simultaneous xw- and yw-plane rotations, a genuine
4D "double rotation," not a static cube-in-a-cube schematic), perspective-
projected 4D->3D, then rendered as glossy tubes/spheres. Colour stands in for
the axis we cannot draw: each edge/vertex is coloured by its rotated
w-coordinate (ink = far in the 4th dimension, gold = near).

  xvfb-run -a python3 attractor_prints/generate_tesseract_render.py <out.png> [w] [h]
"""
import itertools
import sys
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

RUST = "#b85c38"
INK = "#1a1a1a"
GOLD = "#e2b13c"


def rot4(dims, angle):
    """4x4 rotation matrix in the plane spanned by dims=(i,j)."""
    i, j = dims
    m = np.eye(4)
    c, s = np.cos(angle), np.sin(angle)
    m[i, i] = c; m[i, j] = -s
    m[j, i] = s; m[j, j] = c
    return m


def rot3_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot3_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def build_tesseract():
    verts4 = np.array(list(itertools.product([-1.0, 1.0], repeat=4)))  # (16,4)
    idx = {v: i for i, v in enumerate(map(tuple, verts4))}
    edges = []
    for i, v in enumerate(verts4):
        for k in range(4):
            w = v.copy(); w[k] *= -1
            j = idx[tuple(w)]
            if j > i:
                edges.append((i, j))

    # genuine 4D double rotation: mix w into both x and y by different angles
    M = rot4((0, 3), np.radians(18)) @ rot4((1, 3), np.radians(24))
    rv = verts4 @ M.T  # rotated 4D coords

    # perspective 4D -> 3D: camera sits at w=+d looking toward the origin
    d = 5.5
    scale = d / (d - rv[:, 3])
    pts3 = rv[:, :3] * scale[:, None]

    # a pleasing 3D view angle
    R3 = rot3_z(np.radians(24)) @ rot3_x(np.radians(18))
    pts3 = pts3 @ R3.T

    wdepth = rv[:, 3]  # rotated w -- our stand-in "4th axis" colour cue
    return pts3, edges, wdepth


def render(out_path, w=4200, h=3400):
    pts, edges, wdepth = build_tesseract()
    wn = (wdepth - wdepth.min()) / (wdepth.max() - wdepth.min() + 1e-9)

    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")

    lut = [INK, "#7a4428", RUST, GOLD]
    for (i, j) in edges:
        line = pv.Line(pts[i], pts[j])
        tube = line.tube(radius=0.028)
        t = float((wn[i] + wn[j]) / 2)
        color = _lerp_cmap(lut, t)
        pl.add_mesh(tube, color=color, smooth_shading=True,
                    specular=0.55, specular_power=20, ambient=0.32, diffuse=0.8)

    for k, p in enumerate(pts):
        sphere = pv.Sphere(radius=0.075, center=p)
        color = _lerp_cmap(lut, float(wn[k]))
        pl.add_mesh(sphere, color=color, smooth_shading=True,
                    specular=0.9, specular_power=30, ambient=0.32, diffuse=0.75)

    try:
        pl.enable_ssao(radius=0.35, bias=0.02)
    except Exception:
        pass
    try:
        pl.enable_shadows()
    except Exception:
        pass

    pl.view_isometric()
    pl.camera.azimuth = 30
    pl.camera.elevation = 15
    pl.camera.zoom(1.5)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


def _lerp_cmap(colors_hex, t):
    t = min(max(t, 0.0), 1.0)
    n = len(colors_hex)
    seg = t * (n - 1)
    i = min(int(seg), n - 2)
    f = seg - i
    c0 = np.array([int(colors_hex[i][k:k+2], 16) for k in (1, 3, 5)])
    c1 = np.array([int(colors_hex[i+1][k:k+2], 16) for k in (1, 3, 5)])
    c = c0 + (c1 - c0) * f
    return tuple((c / 255.0).tolist())


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "tesseract_render.png"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4200
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 3400
    render(out, w, h)
