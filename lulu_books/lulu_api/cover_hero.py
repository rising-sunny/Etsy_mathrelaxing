"""
cover_hero.py — artwork helpers for the book COVER (not the interior).

Renders a vivid "stained-glass" mandala from the same mathematical curves
used inside the book, but tuned for a cover: bold colored regions, no dot
field / frame / brand text, transparent background so it floats on a
gradient. Also a smooth gradient-background helper. Print resolution PNGs.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union
from shapely.strtree import STRtree
from PIL import Image

from generate_one_per_family import (  # noqa: E402
    circle_curve, rose, hypotrochoid, lissajous, hypocycloid, epicycloid,
    lemniscate_bernoulli, _close,
)

# Saturated palette that pops on a dark background (vs. the soft interior pastels)
VIVID = ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF",
         "#B983FF", "#FF9F45", "#4DD0E1", "#F06595"]

# A rich, symmetric composition for the hero medallion
DEFAULT_HERO = [
    circle_curve(8.0),
    rose(k=7, a=7.4),
    hypotrochoid(R=8, r=3, d=5),
    hypotrochoid(R=9, r=4, d=6),
    rose(k=5, a=4.2),
    circle_curve(2.2),
]


def _graph_color(polys, palette):
    """Greedy Welsh-Powell so adjacent regions get different colors."""
    N = len(polys)
    adj = [set() for _ in range(N)]
    if N:
        tree = STRtree(polys)
        for i, p in enumerate(polys):
            for j in tree.query(p.buffer(0.05)):
                j = int(j)
                if j <= i:
                    continue
                inter = p.boundary.intersection(polys[j].boundary)
                try:
                    ln = inter.length
                except Exception:
                    ln = 0.0
                if not inter.is_empty and ln > 1e-3:
                    adj[i].add(j)
                    adj[j].add(i)
    usage = [0] * len(palette)
    cidx = [-1] * N
    for i in sorted(range(N), key=lambda i: -len(adj[i])):
        forb = {cidx[j] for j in adj[i] if cidx[j] >= 0}
        allow = [c for c in range(len(palette)) if c not in forb] or list(range(len(palette)))
        chosen = min(allow, key=lambda c: (usage[c], c))
        cidx[i] = chosen
        usage[chosen] += 1
    return cidx


def render_hero(out_png, side_in, dpi=300, curves=None, palette=VIVID,
                line_color="#1A1A1A", line_w=1.7, pad=0.94, min_area=0.02):
    """Square, transparent PNG of a vivid colored mandala."""
    curves = DEFAULT_HERO if curves is None else curves
    all_pts = np.vstack(curves)
    xmin, ymin = all_pts.min(0)
    xmax, ymax = all_pts.max(0)
    cx0, cy0 = (xmin + xmax) / 2, (ymin + ymax) / 2
    s = min(side_in / (xmax - xmin), side_in / (ymax - ymin)) * pad

    def fit(p):
        o = np.empty_like(p)
        o[:, 0] = (p[:, 0] - cx0) * s
        o[:, 1] = (p[:, 1] - cy0) * s
        return o

    fcurves = [fit(c) for c in curves]
    merged = unary_union([LineString(c) for c in fcurves])
    polys = [p for p in polygonize(merged) if p.area >= min_area]
    cidx = _graph_color(polys, palette)

    fig = plt.figure(figsize=(side_in, side_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-side_in / 2, side_in / 2)
    ax.set_ylim(-side_in / 2, side_in / 2)
    ax.set_aspect("equal")
    ax.axis("off")
    for i, p in enumerate(polys):
        if p.geom_type != "Polygon":
            continue
        ax.add_patch(MplPolygon(list(p.exterior.coords), closed=True,
                                facecolor=palette[cidx[i]], edgecolor="none"))
    for c in fcurves:
        ax.plot(c[:, 0], c[:, 1], color=line_color, lw=line_w,
                solid_capstyle="round", solid_joinstyle="round")
    fig.savefig(out_png, dpi=dpi, transparent=True)
    plt.close(fig)
    return out_png


def make_gradient(out_png, w_px, h_px, top_rgb, bot_rgb, diagonal=0.3):
    """Smooth diagonal gradient. rgb tuples are 0..1 floats."""
    top = np.array(top_rgb, float)
    bot = np.array(bot_rgb, float)
    yy = np.linspace(0, 1, h_px)[:, None]
    xx = np.linspace(0, 1, w_px)[None, :]
    t = yy * (1 - diagonal) + xx * diagonal
    t = (t - t.min()) / (t.max() - t.min())
    img = top[None, None, :] * (1 - t[..., None]) + bot[None, None, :] * t[..., None]
    Image.fromarray((img * 255).astype("uint8"), "RGB").save(out_png)
    return out_png


def make_pattern(out_png, w_in, h_in, dpi=200, color="white", alpha=0.075,
                 spacing_in=1.65, motif_r=0.62, lw=0.8):
    """Transparent tile-pattern of faint mathematical roses, to texture the
    background. Two alternating motifs, slight per-cell rotation."""
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_in)
    ax.set_ylim(0, h_in)
    ax.set_aspect("equal")
    ax.axis("off")
    motif_a = rose(k=6, a=motif_r)
    motif_b = rose(k=5, a=motif_r)
    nx = int(w_in / spacing_in) + 3
    ny = int(h_in / (spacing_in * 0.92)) + 3
    idx = 0
    for iy in range(ny):
        for ix in range(nx):
            cx = ix * spacing_in + (spacing_in / 2 if iy % 2 else 0) - spacing_in / 2
            cy = iy * spacing_in * 0.92 - spacing_in / 2
            rot = np.deg2rad((idx * 31) % 360)
            m = motif_a if (ix + iy) % 2 == 0 else motif_b
            c, s = np.cos(rot), np.sin(rot)
            x = cx + c * m[:, 0] - s * m[:, 1]
            y = cy + s * m[:, 0] + c * m[:, 1]
            ax.plot(x, y, color=color, lw=lw, alpha=alpha, solid_capstyle="round")
            idx += 1
    fig.savefig(out_png, dpi=dpi, transparent=True)
    plt.close(fig)
    return out_png
