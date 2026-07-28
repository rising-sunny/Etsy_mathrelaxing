"""
posters.py — poster-quality vintage studies: Maurer rose + Phyllotaxis
======================================================================
Decorative code art on aged ivory (sepia ink + gold accent, plate ring).

    python vintage_art/posters.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
IVORY = (0.937, 0.912, 0.842)
INK = (0.16, 0.11, 0.07)
GOLD = (0.647, 0.494, 0.204)
rng = np.random.default_rng(11)


def paper(ax, lim):
    """Aged ivory ground: fibre grain + foxing + warm vignette."""
    N = 1000
    base = np.ones((N, N, 3)) * np.array(IVORY)
    grain = rng.normal(0, 1, (N, N))
    grain = (grain - grain.min()) / (grain.max() - grain.min())
    base *= (0.965 + 0.05 * grain)[..., None]
    yy, xx = np.mgrid[0:N, 0:N]
    for _ in range(46):
        cx, cy = rng.uniform(0, N, 2); r = rng.uniform(4, 15)
        blot = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2) * rng.uniform(0.05, 0.13)
        base *= (1 - blot[..., None] * np.array([0.35, 0.45, 0.6]))
    rr = np.sqrt((xx - N / 2) ** 2 + (yy - N / 2) ** 2) / (N / 2)
    vig = np.clip(1 - 0.20 * rr ** 2.6, 0, 1)[..., None]
    edge = np.array([0.62, 0.55, 0.44])
    base = base * vig + edge * (1 - vig) * 0.5
    ax.imshow(np.clip(base, 0, 1), extent=(-lim, lim, -lim, lim), zorder=0)


def plate_ring(ax, r0):
    th = np.linspace(0, 2 * np.pi, 600)
    for rr, a in ((r0, 0.55), (r0 * 0.975, 0.38)):
        ax.plot(rr * np.cos(th), rr * np.sin(th), color=INK, lw=0.8, alpha=a, zorder=5)


def _fig(lim):
    fig = plt.figure(figsize=(8, 8), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    return fig, ax


def maurer_rose():
    lim = 1.28
    fig, ax = _fig(lim); paper(ax, lim)
    n, d = 6, 71
    # Maurer web: 361 chords stepping d degrees around r = sin(nθ)
    k = np.arange(0, 361)
    theta = np.radians(k * d)
    r = np.sin(n * theta)
    ax.plot(r * np.cos(theta), r * np.sin(theta), color=INK, lw=0.35, alpha=0.6, zorder=3)
    # smooth rose outline in gold on top
    tt = np.linspace(0, 2 * np.pi, 2000)
    rr = np.sin(n * tt)
    ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=GOLD, lw=1.2, alpha=0.85, zorder=4)
    plate_ring(ax, 1.2)
    out = OUT / "poster_maurer_rose.jpg"
    fig.savefig(out, dpi=300, facecolor=IVORY); plt.close(fig)
    print("  ->", out.name)


def phyllotaxis():
    lim = 1.28
    fig, ax = _fig(lim); paper(ax, lim)
    n = 2600
    i = np.arange(1, n + 1)
    ga = np.pi * (3 - np.sqrt(5))          # golden angle
    scale = 1.06 / np.sqrt(n)
    r = scale * np.sqrt(i)
    th = i * ga
    x, y = r * np.cos(th), r * np.sin(th)
    sizes = 0.5 + 11 * (i / n) ** 1.3       # florets grow outward
    # every 5th seed in gold -> subtle parastichy shimmer
    gold_mask = (i % 5 == 0)
    ax.scatter(x[~gold_mask], y[~gold_mask], s=sizes[~gold_mask], c=[INK],
               alpha=0.82, edgecolors="none", zorder=3)
    ax.scatter(x[gold_mask], y[gold_mask], s=sizes[gold_mask], c=[GOLD],
               alpha=0.85, edgecolors="none", zorder=4)
    plate_ring(ax, 1.2)
    out = OUT / "poster_phyllotaxis.jpg"
    fig.savefig(out, dpi=300, facecolor=IVORY); plt.close(fig)
    print("  ->", out.name)


if __name__ == "__main__":
    maurer_rose()
    phyllotaxis()
    print("DONE")
