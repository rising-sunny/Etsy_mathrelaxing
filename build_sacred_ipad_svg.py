"""
build_sacred_ipad_svg.py — Interactive SVG edition of Sacred Geometry CBN
=========================================================================
Migrates the (inactive) "Sacred Geometry Color by Number iPad Pages"
listing to the interactive Safari-SVG format (template_ipad_svg_bundle),
KEEPING the original product's defining feature: a low-poly **3D** feel.

The original Sacred Geometry & Topology art is a set of 50 three-dimensional
mathematical surfaces (tori, Möbius bands, helicoids, seashells, faceted
spheres — from lulu_books/core/math_meshes.py) rendered as low-poly 3D
color-by-number: the numbers follow the LIGHTING of each facet, so colouring
1→8 (shadow→highlight) reveals a shaded three-dimensional form.

This rebuild reproduces that in true vector SVG:
  • get_mesh(idx) gives the 3D triangle mesh
  • each face is rotated to a camera view, orthographically projected to 2D,
    and back-face culled (front sheet only → a clean, non-overlapping SVG)
  • face intensity = normal · light  →  shade index into an 8-step
    dark→light palette, so tapping the numbers paints the 3D shading
Because it is SVG the buyer gets infinite crisp zoom.

  python build_sacred_ipad_svg.py            # full 50-design bundle
  python build_sacred_ipad_svg.py --sample   # 5 designs -> /tmp preview grid
"""
import os
import sys
import math
import numpy as np
import shapely.geometry

sys.path.append(os.path.join(os.path.dirname(__file__), "lulu_books", "core"))
from math_meshes import (gen_torus, gen_mobius, gen_seashell,
                         gen_sphere_bumpy, add_noise)

from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle


# ── The 50 designs — curated toward the families that read as clean low-poly
#    3D after front-face culling (closed tori & faceted spheres), plus twisted
#    Möbius bands and a few golden-spiral seashells for topological variety. ──
def _designs():
    ds = []
    # 22 tori (Torus Topology)
    for i in range(22):
        ds.append(dict(kind="torus", title=f"Torus Topology {i+1}",
                       R=1.0 + (i % 3) * 0.18, r=0.30 + (i % 3) * 0.06,
                       u=22 + (i % 6) * 2, v=11 + (i % 3), tw=(i % 4 == 3),
                       noise=0.016, seed=i))
    # 22 faceted spheres (Geometric Gem)
    for i in range(22):
        ds.append(dict(kind="sphere", title=f"Geometric Gem {i+1}",
                       bumps=2 + (i % 5), depth=0.12 + (i % 5) * 0.035,
                       u=20 + (i % 5) * 2, v=16 + (i % 3) * 2,
                       noise=0.018, seed=100 + i))
    # 6 Möbius bands (wider so the twisted 3D band reads clearly)
    for i in range(6):
        ds.append(dict(kind="mobius", title=f"Möbius Band {i+1}",
                       twists=1 + (i % 3), w=0.6, u=34 + (i % 4) * 2, v=9,
                       noise=0.012, seed=200 + i))
    return ds[:50]

DESIGNS = _designs()


def get_mesh(idx):
    """Curated replacement for math_meshes.get_mesh: returns (verts, faces, title)."""
    d = DESIGNS[idx]
    if d["kind"] == "torus":
        verts, faces = gen_torus(R=d["R"], r=d["r"], u_steps=d["u"],
                                 v_steps=d["v"], twists=1 if d["tw"] else 0)
    elif d["kind"] == "sphere":
        verts, faces = gen_sphere_bumpy(bumps=d["bumps"], bump_depth=d["depth"],
                                        u_steps=d["u"], v_steps=d["v"])
    elif d["kind"] == "mobius":
        verts, faces = gen_mobius(w=d.get("w", 0.4), u_steps=d["u"],
                                  v_steps=d["v"], twists=d["twists"])
    else:
        verts, faces = gen_seashell(u_steps=d["u"], v_steps=d["v"])
    verts = add_noise(verts, d["noise"], seed=d["seed"])
    return verts, faces, d["title"]

RDISK = 250.0                     # design half-size; coords centred at (0,0)
N_SHADES = 8                      # palette steps (shadow -> highlight)

# ── 8-step luminance ramp: deep navy shadow → gold → cream highlight.
#    Strictly increasing lightness so pure shade variation reads as 3D form,
#    with a subtle navy→gold hue drift for a lit "sacred gem" look. ────────────
SACRED_PALETTE = [
    "#0d1124",   # 1  deepest shadow (brand navy)
    "#1b2440",   # 2
    "#2f3d64",   # 3
    "#4a5570",   # 4
    "#7a7360",   # 5  (turn toward gold in the mid-tones)
    "#a98d4e",   # 6
    "#d0ab5f",   # 7
    "#f2e6c4",   # 8  highlight (cream/gold)
]
PALETTE_N = len(SACRED_PALETTE)

# camera light (upper-left, toward viewer) and view axis
_LIGHT = np.array([-0.45, 0.55, 0.75]); _LIGHT = _LIGHT / np.linalg.norm(_LIGHT)


def _rot(ax, ay):
    """Rotation: pitch ax about X then yaw ay about Y."""
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    return Ry @ Rx


def get_polygons(n):
    """For design n (1-based) → list of {"poly", "color_idx", "dist"}.
    A low-poly 3D surface, front-face-culled and shaded by facet lighting."""
    idx = n - 1
    verts, faces, _title = get_mesh(idx)
    verts = np.asarray(verts, dtype=float)
    verts = verts - verts.mean(axis=0)
    m = np.abs(verts).max()
    if m > 0:
        verts = verts / m                      # normalise to ~unit cube

    # per-design camera so the 50 look varied
    ax = math.radians(24 + (idx % 5) * 6)
    ay = math.radians((idx * 37) % 360)
    vv = verts @ _rot(ax, ay).T                # rotated into view space

    # fit projected extent to the disk
    ext = np.abs(vv[:, :2]).max()
    scale = (RDISK * 0.92) / ext if ext > 0 else 1.0

    faces_kept = []
    for f in faces:
        v0, v1, v2 = vv[f[0]], vv[f[1]], vv[f[2]]
        nrm = np.cross(v1 - v0, v2 - v0)
        nl = np.linalg.norm(nrm)
        if nl < 1e-9:
            continue
        nrm = nrm / nl
        if nrm[2] <= 0.08:                     # cull back + thin silhouette slivers
            continue
        intensity = max(0.04, float(np.dot(nrm, _LIGHT)))
        z = (v0[2] + v1[2] + v2[2]) / 3.0
        faces_kept.append((z, intensity, (v0[:2], v1[:2], v2[:2])))

    if not faces_kept:
        return []

    ints = np.array([fi for _, fi, _ in faces_kept])
    lo, hi = ints.min(), ints.max()
    # painter's order: far first so nearer facets sit on top in the SVG
    faces_kept.sort(key=lambda t: t[0])

    cells = []
    for z, inten, tri in faces_kept:
        t = (inten - lo) / (hi - lo + 1e-6)
        t = t ** 0.72                          # gamma: open up the shadows
        cidx = min(N_SHADES - 1, int(t * N_SHADES))
        pts = [(float(p[0]) * scale, float(p[1]) * scale) for p in tri]
        # sliver filter: skip near-degenerate thin triangles (silhouette /
        # pole spikes) — an equilateral has area ≈ 0.43·L²; keep only chunky ones
        e = [math.dist(pts[a], pts[b]) for a, b in ((0, 1), (1, 2), (2, 0))]
        L = max(e)
        area2 = abs((pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])
                    - (pts[2][0]-pts[0][0])*(pts[1][1]-pts[0][1])) / 2.0
        if L < 1e-6 or area2 < 0.07 * L * L:
            continue
        poly = shapely.geometry.Polygon(pts)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.area < 3.0:
            continue
        c = poly.centroid
        cells.append({"poly": poly, "color_idx": cidx,
                      "dist": math.hypot(c.x, c.y)})
    return cells


CFG = SvgBundleConfig(
    out_dir="ipad_sacred_cbn_svg",
    prefix="SacredGeometry_CBN",
    title="Sacred Geometry",
    palette=SACRED_PALETTE,
    n_designs=50,
    stroke_color="#1A1D24",
    font_min=1.0,
    font_max=16.0,
)


if __name__ == "__main__":
    if "--sample" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MPoly
        picks = [3, 20, 30, 44, 47]
        fig, axes = plt.subplots(1, 5, figsize=(20, 4.2))
        fig.patch.set_facecolor("#0d1124")
        for ax, npick in zip(axes, picks):
            ax.set_facecolor("#0d1124"); ax.set_xlim(-RDISK, RDISK)
            ax.set_ylim(-RDISK, RDISK); ax.set_aspect("equal"); ax.axis("off")
            cells = get_polygons(npick)
            for cell in cells:
                g = cell["poly"]
                geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
                for gm in geoms:
                    xy = np.array(gm.exterior.coords)
                    ax.add_patch(MPoly(xy, closed=True,
                                 facecolor=SACRED_PALETTE[cell["color_idx"]],
                                 edgecolor="#1A1D24", linewidth=0.3))
            _, _, title = get_mesh(npick - 1)
            ax.set_title(f"#{npick} {title}", color="#c9a24b", fontsize=10)
        fig.savefig("/tmp/sacred_3d_sample.png", facecolor="#0d1124", dpi=90,
                    bbox_inches="tight")
        print("wrote /tmp/sacred_3d_sample.png")
    else:
        build_svg_bundle(CFG, get_polygons)
