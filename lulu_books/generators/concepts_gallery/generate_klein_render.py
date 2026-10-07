"""
generate_klein_render.py — pyvista/VTK wireframe render of a Klein bottle.

Standalone script (must run under xvfb-run for headless OpenGL). The classic
"figure-8" immersion of the Klein bottle in R^3, drawn as a dense net of thin
glossy contour lines (many rings around the tube + many lines along its
length) rather than a solid shaded surface -- an engraved-wireframe look,
consistent with the rest of the shop's fine-line style.

  xvfb-run -a python3 generate_klein_render.py <out.png> [w] [h]
"""
import sys
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

RUST = "#b85c38"
INK = "#1a1a1a"
GOLD = "#e2b13c"


def klein_point(u, v):
    r = 4 * (1 - np.cos(u) / 2)
    x1 = 6 * np.cos(u) * (1 + np.sin(u)) + r * np.cos(u) * np.cos(v)
    y1 = 16 * np.sin(u) + r * np.sin(u) * np.cos(v)
    x2 = 6 * np.cos(u) * (1 + np.sin(u)) + r * np.cos(v + np.pi)
    y2 = 16 * np.sin(u)
    front = u < np.pi
    x = np.where(front, x1, x2)
    y = np.where(front, y1, y2)
    z = r * np.sin(v)
    return x, y, z


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


def render(out_path, w=4200, h=3400):
    scale = 1.0 / 16.0
    lut = [INK, "#7a4428", RUST, GOLD]

    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")

    # rings: many lines of constant u, tracing v = 0..2pi (the tube cross-section)
    n_rings = 90
    v = np.linspace(0, 2 * np.pi, 90, endpoint=True)
    for i, u0 in enumerate(np.linspace(0.0001, 2 * np.pi - 0.0001, n_rings)):
        x, y, z = klein_point(np.full_like(v, u0), v)
        pts = np.stack([x, y, z], axis=-1) * scale
        line = pv.lines_from_points(pts, close=True).tube(radius=0.0032)
        color = _lerp_cmap(lut, i / (n_rings - 1))
        pl.add_mesh(line, color=color, smooth_shading=True,
                    specular=0.6, specular_power=22, ambient=0.35, diffuse=0.75)

    # lengthwise strands: many lines of constant v, tracing u = 0..2pi (the length)
    n_strands = 26
    u = np.linspace(0.0001, 2 * np.pi - 0.0001, 260)
    for j, v0 in enumerate(np.linspace(0, 2 * np.pi, n_strands, endpoint=False)):
        x, y, z = klein_point(u, np.full_like(u, v0))
        pts = np.stack([x, y, z], axis=-1) * scale
        line = pv.lines_from_points(pts).tube(radius=0.0026)
        color = _lerp_cmap(lut, 0.5 + 0.45 * np.sin(v0))
        pl.add_mesh(line, color=color, smooth_shading=True, opacity=0.7,
                    specular=0.5, specular_power=18, ambient=0.35, diffuse=0.7)

    try:
        pl.enable_ssao(radius=0.35, bias=0.02)
    except Exception:
        pass

    pl.camera.up = (0, 1, 0)
    pl.camera.position = (3.6, 1.0, 2.0)
    pl.camera.focal_point = (0, 0.05, 0)
    pl.reset_camera()
    pl.camera.zoom(0.9)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "klein_render.png"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4200
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 3400
    render(out, w, h)
