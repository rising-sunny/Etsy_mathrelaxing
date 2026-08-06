"""
generate_polyhedron_render.py — pyvista/VTK render of an icosahedron
(Euler's polyhedron formula: V - E + F = 2).

Standalone script (must run under xvfb-run for headless OpenGL). Glossy
tubes for edges + spheres for vertices, same technique as the tesseract
render -- a line/wireframe object, not a solid.

  xvfb-run -a python3 generate_polyhedron_render.py <out.png> [w] [h]
"""
import sys
import itertools
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

RUST = "#b85c38"
INK = "#1a1a1a"
GOLD = "#e2b13c"


def icosahedron():
    phi = (1 + np.sqrt(5)) / 2
    verts = []
    for a, b in itertools.product([-1, 1], [-phi, phi]):
        verts.append((0, a, b))
        verts.append((a, b, 0))
        verts.append((b, 0, a))
    verts = np.array(verts)
    verts /= np.linalg.norm(verts[0])  # normalize to unit circumradius

    n = len(verts)
    dists = np.linalg.norm(verts[:, None, :] - verts[None, :, :], axis=-1)
    short = np.sort(np.unique(np.round(dists[dists > 1e-6], 4)))[0]
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)
             if abs(dists[i, j] - short) < 1e-3]
    return verts, edges


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
    pts, edges = icosahedron()
    lut = [INK, "#7a4428", RUST, GOLD]
    depth = pts[:, 1]  # colour cue by height, echoing the tesseract's depth idea
    dn = (depth - depth.min()) / (depth.max() - depth.min() + 1e-9)

    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")

    for (i, j) in edges:
        tube = pv.Line(pts[i], pts[j]).tube(radius=0.024)
        color = _lerp_cmap(lut, float((dn[i] + dn[j]) / 2))
        pl.add_mesh(tube, color=color, smooth_shading=True,
                    specular=0.55, specular_power=20, ambient=0.32, diffuse=0.8)
    for k, p in enumerate(pts):
        sphere = pv.Sphere(radius=0.065, center=p)
        color = _lerp_cmap(lut, float(dn[k]))
        pl.add_mesh(sphere, color=color, smooth_shading=True,
                    specular=0.9, specular_power=30, ambient=0.32, diffuse=0.75)

    try:
        pl.enable_ssao(radius=0.3, bias=0.02)
    except Exception:
        pass
    try:
        pl.enable_shadows()
    except Exception:
        pass

    pl.view_isometric()
    pl.camera.azimuth = 18
    pl.camera.elevation = 10
    pl.camera.zoom(1.3)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "polyhedron_render.png"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4200
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 3400
    render(out, w, h)
