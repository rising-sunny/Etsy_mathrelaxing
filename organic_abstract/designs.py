"""
designs.py — the six plates of the "Computed Organic" abstract set.

Every outline is a plotted curve: a truncated Fourier series in polar
coordinates, or Gielis' superformula. Nothing is drawn freehand, which is the
one claim the crowded hand-drawn corner of this category cannot make.

Palettes give each plate its own ground rather than recolouring one scheme, so
the set covers a navy, a cream, a forest, a black, a clay and a plum room.
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Polygon

import organic_engine as O

PALETTES = {
    "midnight": ("#141a3a", ["#e8613c", "#f2a33c", "#f5d76e", "#5aa88a", "#7fc4d6", "#e88fa8", "#f3e6d0"]),
    "bone":     ("#f0e9dc", ["#c2512f", "#e0913f", "#7d9b6a", "#3f5f6b", "#d4a6a0", "#2e2a26", "#e8c86a"]),
    "forest":   ("#16281f", ["#e5b45c", "#d97b5a", "#f0e2c8", "#8fae7d", "#4a7a6a", "#c9738c", "#efd9a8"]),
    "carbon":   ("#0d0d0f", ["#ff5c39", "#ffc93c", "#3ddc97", "#4aa8ff", "#ff7bd5", "#f5f2ea", "#9b7bff"]),
    "clay":     ("#c8724c", ["#1d3a52", "#f0e4d0", "#3f7d6e", "#e8b04b", "#8c2f2a", "#d9c3a5", "#2b2b2b"]),
    "plum":     ("#2a1730", ["#f2a5b8", "#e8c86a", "#79c2a8", "#c98bd9", "#f5ece0", "#e0663f", "#8f6bd4"]),
}

DESIGNS = [
    dict(slug="reef",     title="Reef",     pal="midnight", seed=31, n=(9, 12)),
    dict(slug="terrace",  title="Terrace",  pal="bone",     seed=32, n=(9, 12)),
    dict(slug="canopy",   title="Canopy",   pal="forest",   seed=57, n=(9, 12)),
    dict(slug="neon",     title="Neon",     pal="carbon",   seed=44, n=(9, 12)),
    dict(slug="kiln",     title="Kiln",     pal="clay",     seed=19, n=(8, 11)),
    dict(slug="dusk",     title="Dusk",     pal="plum",     seed=66, n=(9, 12)),
]


def render(design, w_in, h_in, dpi=300):
    """One plate, full bleed, no text."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ground, cols = PALETTES[design["pal"]]
    rng = np.random.default_rng(design["seed"])
    vh = 1.0
    vw = vh * (w_in / h_in)
    view = (-vw, -vh, vw, vh)

    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-vw, vw)
    ax.set_ylim(-vh, vh)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(ground)
    ax.set_facecolor(ground)

    order = rng.permutation(len(cols))
    lo, hi = design["n"]
    for i in range(int(rng.integers(lo, hi))):
        kind = rng.random()
        if kind < 0.20:
            # n1 high rounds the superformula off. Low values gave spiky
            # cartoon stars that read as clip art beside the organic shapes.
            pts = O.superformula(m=int(rng.choice([3, 4, 5, 6])), n1=rng.uniform(1.4, 3.0),
                                 n2=rng.uniform(0.7, 1.6), n3=rng.uniform(0.7, 1.6))
            sq = rng.uniform(0.75, 1.2)
        elif kind < 0.50:
            # few lobes, hard squash -> the long flowing wave forms
            pts = O.fourier_blob(rng, lobes=(2, 3), rough=rng.uniform(0.30, 0.48))
            sq = rng.uniform(0.30, 0.48)
        else:
            pts = O.fourier_blob(rng, lobes=(2, int(rng.integers(3, 6))), rough=rng.uniform(0.20, 0.38))
            sq = rng.uniform(0.75, 1.25)

        p = O.place(pts, rng.uniform(-vw * 0.95, vw * 0.95), rng.uniform(-vh * 0.92, vh * 0.92),
                    rng.uniform(0.42, 0.82) * vh, rng.uniform(0, np.pi), sq)
        poly = Polygon(p, facecolor=cols[order[i % len(cols)]], edgecolor="none", zorder=2 + i)
        ax.add_patch(poly)

        if rng.random() < 0.32:
            d = O.dots_in(p, view, 0.062 * vh)
            if len(d):
                ax.scatter(d[:, 0], d[:, 1], s=3.0 * (w_in / 4.0), color=ground,
                           zorder=2 + i + 0.5, linewidths=0)
    return fig
