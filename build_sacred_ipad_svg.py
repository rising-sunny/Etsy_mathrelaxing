"""
build_sacred_ipad_svg.py — Interactive SVG edition of Sacred Geometry CBN
=========================================================================
Migrates the (inactive) "Sacred Geometry Color by Number iPad Pages"
listing from static PNG/PDF pages to the interactive Safari-SVG format
used by Voronoi Gardens & Spiral Tilings (template_ipad_svg_bundle).

Unlike Voronoi (parametric cells) the original Sacred Geometry art was a
raster/PDF pipeline, so there were no vector polygons to reuse. Here the
designs are regenerated PARAMETRICALLY as low-poly sacred mandalas:
k-fold-symmetric seed points (rose windows, Flower-of-Life hex lattices,
nested star rings, phyllotaxis) are Delaunay-triangulated into clean
triangular cells — the literal "low poly" look — clipped to a disk and
coloured with a k-fold-symmetric rule so the mandala reads as symmetric.

Because everything is true vector, the buyer gets infinite crisp zoom.

  python build_sacred_ipad_svg.py            # full 50-design bundle
  python build_sacred_ipad_svg.py --sample   # 4 designs -> /tmp preview grid
"""
import os
import sys
import math
import numpy as np
import shapely.geometry
from scipy.spatial import Delaunay

from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle

# ── Geometry constants (match the Voronoi SVG coordinate convention) ──────────
RDISK = 250.0                 # design disk radius; coords centred at (0,0)

# ── Sacred-geometry palette (jewel + metallic tones, hex) ─────────────────────
SACRED_PALETTE = [
    "#c9a24b", "#e0be6a", "#a5772e", "#6b4f1d",   # golds / bronze
    "#4a7ba6", "#2e5a86", "#7fb0aa", "#356c78",   # blues / teals
    "#8d6bcf", "#5a3fa0", "#b48ad4", "#3d2f6a",   # violets
    "#c95a41", "#e07850", "#a83e3e", "#e8a24a",   # warm terracotta / amber
    "#5a8f5a", "#356b45", "#8fbf7f", "#26332c",   # greens / forest
    "#d9d7cf", "#b0a99a", "#ece9df", "#4a556b",   # neutrals / slate
]

PALETTE_N = len(SACRED_PALETTE)

# ── k-fold-symmetric seed generators (all centred at origin) ──────────────────

def _rose(k, rings, seed):
    """Concentric rose window: k points per ring, alternating phase, denser out."""
    rng = np.random.default_rng(seed)
    pts = [(0.0, 0.0)]
    for ri in range(1, rings + 1):
        r = RDISK * (ri / (rings + 0.3))
        r *= 1 + rng.uniform(-0.012, 0.012)              # symmetric ring jitter
        phase = (ri % 2) * (math.pi / k)
        kk = k * (1 if ri < rings * 0.6 else 2)          # more density outside
        for j in range(kk):
            a = phase + 2 * math.pi * j / kk
            pts.append((r * math.cos(a), r * math.sin(a)))
    return np.array(pts)

def _mandala(k, rings, seed):
    """k-fold mandala: seeds at fixed fractions of the fundamental wedge."""
    rng = np.random.default_rng(seed)
    wedge = 2 * math.pi / k
    pts = [(0.0, 0.0)]
    for ri in range(rings):
        r = RDISK * ((ri + 0.6) / (rings + 0.5)) ** 0.95
        r *= 1 + rng.uniform(-0.012, 0.012)
        fracs = [0.5] if ri % 2 == 0 else [0.27, 0.73]
        if ri == rings - 1:
            fracs = [0.18, 0.5, 0.82]
        for f in fracs:
            a0 = f * wedge
            for j in range(k):
                a = a0 + j * wedge
                pts.append((r * math.cos(a), r * math.sin(a)))
    return np.array(pts)

def _flower_of_life(rings, seed):
    """Flower-of-Life hex lattice: circle centres on a triangular lattice,
    kept inside the disk. Delaunay of a hex lattice gives equilateral low-poly."""
    step = RDISK / (rings + 0.5)
    pts = []
    for i in range(-rings - 1, rings + 2):
        for j in range(-rings - 1, rings + 2):
            x = step * (i + 0.5 * j)
            y = step * (math.sqrt(3) / 2) * j
            if x * x + y * y <= (RDISK * 1.001) ** 2:
                pts.append((x, y))
    return np.array(pts)

def _nested_stars(k, rings, seed):
    """Nested rotating k-gons (star-of-David style layering)."""
    pts = [(0.0, 0.0)]
    for ri in range(1, rings + 1):
        r = RDISK * (ri / (rings + 0.3))
        rot = (ri % 2) * (math.pi / k)                   # alternate orientation
        for j in range(k):
            a = rot + 2 * math.pi * j / k
            pts.append((r * math.cos(a), r * math.sin(a)))
            # midpoint seed on each edge to enrich the triangulation
            a2 = rot + 2 * math.pi * (j + 0.5) / k
            r2 = r * 0.86
            pts.append((r2 * math.cos(a2), r2 * math.sin(a2)))
    return np.array(pts)

def _phyllotaxis(n, seed):
    """Golden-angle spiral (sunflower) — organic sacred spiral."""
    golden = math.radians(137.50776405)
    spread = RDISK / math.sqrt(n)
    pts = [(0.0, 0.0)]
    for i in range(1, n):
        r = spread * math.sqrt(i)
        a = i * golden
        pts.append((r * math.cos(a), r * math.sin(a)))
    return np.array(pts)


# ── The 50 designs (name, generator, k for colour symmetry) ───────────────────

def _designs():
    ks = [6, 8, 12, 5, 10, 9, 7, 16]
    ds = []
    # Rose windows (12)
    for i in range(12):
        k = ks[i % len(ks)]
        ds.append(dict(kind="rose", k=k, rings=5 + i % 3, seed=100 + i))
    # k-fold mandalas (12)
    for i in range(12):
        k = ks[(i + 3) % len(ks)]
        ds.append(dict(kind="mandala", k=k, rings=5 + i % 4, seed=200 + i))
    # Flower of Life hex lattices (8) — 6-fold by construction
    for i in range(8):
        ds.append(dict(kind="flower", k=6, rings=4 + i % 4, seed=300 + i))
    # Nested star rings (10)
    for i in range(10):
        k = ks[(i + 1) % len(ks)]
        ds.append(dict(kind="nested", k=k, rings=5 + i % 3, seed=400 + i))
    # Phyllotaxis spirals (8)
    for i in range(8):
        ds.append(dict(kind="phyllo", k=8, n=140 + 25 * (i % 4), seed=500 + i))
    return ds[:50]

DESIGNS = _designs()

_GEN = {"rose": _rose, "mandala": _mandala, "nested": _nested_stars}


def _seeds(d):
    if d["kind"] == "flower":
        return _flower_of_life(d["rings"], d["seed"])
    if d["kind"] == "phyllo":
        return _phyllotaxis(d["n"], d["seed"])
    return _GEN[d["kind"]](d["k"], d["rings"], d["seed"])


def get_polygons(n):
    """For design n (1-based) → list of {"poly": Polygon, "color_idx": int}."""
    d = DESIGNS[n - 1]
    k = d["k"]
    pts = _seeds(d)
    # Delaunay (joggle a hair to avoid cocircular degeneracies from the rings)
    tri = Delaunay(pts, qhull_options="QJ")
    disk = shapely.geometry.Point(0, 0).buffer(RDISK, resolution=128)
    wedge = 2 * math.pi / k
    n_ring = 6
    cells = []
    for simplex in tri.simplices:
        poly = shapely.geometry.Polygon(pts[simplex])
        if not poly.is_valid:
            poly = poly.buffer(0)
        clipped = poly.intersection(disk)
        if clipped.is_empty or clipped.area < 2.0:
            continue
        # colour by a k-fold-symmetric rule: fold centroid angle into one wedge
        c = poly.centroid
        r = math.hypot(c.x, c.y)
        theta = math.atan2(c.y, c.x) % wedge
        ring_band = min(n_ring - 1, int(r / RDISK * n_ring))
        ang_band = int(theta / wedge * 3)                # 3 bands per wedge
        color_idx = (ring_band * 5 + ang_band * 2 + d["seed"]) % PALETTE_N
        # "dist" (centroid radius) is unused by the SVG framework but lets the
        # preview builder colour cells centre-outward.
        cells.append({"poly": clipped, "color_idx": color_idx, "dist": r})
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
        # quick visual check: render 4 designs to an SVG-ish PNG grid via matplotlib
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MPoly
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        fig.patch.set_facecolor("#0d1124")
        picks = [1, 16, 30, 45]
        for ax, npick in zip(axes.ravel(), picks):
            ax.set_facecolor("#0d1124"); ax.set_xlim(-RDISK, RDISK)
            ax.set_ylim(-RDISK, RDISK); ax.set_aspect("equal"); ax.axis("off")
            for cell in get_polygons(npick):
                g = cell["poly"]
                geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
                for gm in geoms:
                    xy = np.array(gm.exterior.coords)
                    ax.add_patch(MPoly(xy, closed=True,
                                 facecolor=SACRED_PALETTE[cell["color_idx"]],
                                 edgecolor="#1A1D24", linewidth=0.4))
            ax.set_title(f"#{npick}  {DESIGNS[npick-1]['kind']}", color="#c9a24b")
        fig.savefig("/tmp/sacred_svg_sample.png", facecolor="#0d1124", dpi=90)
        print("wrote /tmp/sacred_svg_sample.png")
    else:
        build_svg_bundle(CFG, get_polygons)
