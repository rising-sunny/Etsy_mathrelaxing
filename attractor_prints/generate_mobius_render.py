"""
generate_mobius_render.py — pyvista/VTK render of the Mobius strip.

Standalone script (must run under xvfb-run for headless OpenGL) that produces
a single high-resolution transparent PNG: a smooth Phong/PBR-shaded 3D
surface with specular highlights, plus a glossy gold tube tracing the single
continuous boundary edge. generate_equation_plates.py's compose_mobius()
shells out to this script (via xvfb-run) the first time it needs the image,
then reuses the cached PNG on every subsequent build.

  xvfb-run -a python3 attractor_prints/generate_mobius_render.py <out.png> [w] [h]
"""
import sys
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

RUST = "#b85c38"
INK = "#1a1a1a"
GOLD = "#e2b13c"


def build_mesh(R=1.0, width=0.62, n_u=360, n_v=32):
    u = np.linspace(0, 2 * np.pi, n_u, endpoint=True)
    v = np.linspace(-1, 1, n_v)
    U, V = np.meshgrid(u, v, indexing="ij")
    half = width / 2 * V * np.cos(U / 2)
    X = (R + half) * np.cos(U)
    Y = (R + half) * np.sin(U)
    Z = (width / 2 * V) * np.sin(U / 2)
    pts = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)

    faces = []
    for i in range(n_u - 1):
        for j in range(n_v - 1):
            a = i * n_v + j
            b = (i + 1) * n_v + j
            c = (i + 1) * n_v + (j + 1)
            d = i * n_v + (j + 1)
            faces += [4, a, b, c, d]
    mesh = pv.PolyData(pts, np.array(faces))
    mesh["vparam"] = np.abs(V.reshape(-1))
    mesh.compute_normals(inplace=True, auto_orient_normals=False, consistent_normals=False)

    pts_grid = pts.reshape(n_u, n_v, 3)
    boundary = np.concatenate([pts_grid[:, 0], pts_grid[::-1, -1]])
    tube = pv.lines_from_points(boundary).tube(radius=0.014)
    return mesh, tube


def render(out_path, w=4200, h=3400):
    mesh, tube = build_mesh()
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")
    pl.add_mesh(mesh, scalars="vparam", cmap=[INK, "#7a4428", RUST], show_scalar_bar=False,
                smooth_shading=True, specular=0.5, specular_power=16, ambient=0.34, diffuse=0.8)
    pl.add_mesh(tube, color=GOLD, smooth_shading=True, specular=0.9, specular_power=30, ambient=0.3)
    try:
        pl.enable_ssao(radius=0.3, bias=0.02)
    except Exception:
        pass
    try:
        pl.enable_shadows()
    except Exception:
        pass
    pl.view_isometric()
    pl.camera.azimuth = 20
    pl.camera.elevation = -8
    pl.camera.zoom(1.25)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mobius_render.png"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4200
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 3400
    render(out, w, h)
