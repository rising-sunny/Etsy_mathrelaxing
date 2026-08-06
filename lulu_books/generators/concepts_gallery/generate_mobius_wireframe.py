"""
generate_mobius_wireframe.py — pyvista/VTK wireframe render of a Mobius strip
for the book (distinct from the solid-shaded FIG.9 equation-plate version):
a dense net of thin glossy contour lines (many cross-strands + many
lengthwise strands), matching the Klein bottle's wireframe treatment.

  xvfb-run -a python3 generate_mobius_wireframe.py <out.png> [w] [h]
"""
import sys
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

RUST = "#b85c38"
INK = "#1a1a1a"
GOLD = "#e2b13c"


def mobius_point(u, v, R=1.0, width=0.62):
    half = width / 2 * v * np.cos(u / 2)
    x = (R + half) * np.cos(u)
    y = (R + half) * np.sin(u)
    z = (width / 2 * v) * np.sin(u / 2)
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
    lut = [INK, "#7a4428", RUST, GOLD]
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")

    # cross-strands: constant u, spanning v=-1..1 (the strip's width)
    n_cross = 110
    v = np.linspace(-1, 1, 2)
    for i, u0 in enumerate(np.linspace(0, 2 * np.pi, n_cross, endpoint=True)):
        x, y, z = mobius_point(u0, v)
        pts = np.stack([x, y, z], axis=-1)
        line = pv.lines_from_points(pts).tube(radius=0.006)
        color = _lerp_cmap(lut, i / (n_cross - 1))
        pl.add_mesh(line, color=color, smooth_shading=True,
                    specular=0.6, specular_power=22, ambient=0.35, diffuse=0.75)

    # lengthwise strands: constant v, spanning u=0..2pi (the twisting flow)
    n_len = 15
    u = np.linspace(0, 2 * np.pi, 300)
    for j, v0 in enumerate(np.linspace(-1, 1, n_len)):
        x, y, z = mobius_point(u, v0)
        pts = np.stack([x, y, z], axis=-1)
        line = pv.lines_from_points(pts).tube(radius=0.005)
        color = _lerp_cmap(lut, 0.5 + 0.45 * v0)
        pl.add_mesh(line, color=color, smooth_shading=True, opacity=0.75,
                    specular=0.5, specular_power=18, ambient=0.35, diffuse=0.7)

    # the single boundary edge, in gold, a touch bolder than the rest
    for v0 in (-1, 1):
        x, y, z = mobius_point(u, v0)
        pts = np.stack([x, y, z], axis=-1)
        line = pv.lines_from_points(pts).tube(radius=0.011)
        pl.add_mesh(line, color=GOLD, smooth_shading=True,
                    specular=0.9, specular_power=30, ambient=0.35, diffuse=0.7)

    try:
        pl.enable_ssao(radius=0.3, bias=0.02)
    except Exception:
        pass

    pl.view_isometric()
    pl.camera.azimuth = 18
    pl.camera.elevation = -12
    pl.camera.zoom(1.4)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mobius_wireframe.png"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4200
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 3400
    render(out, w, h)
