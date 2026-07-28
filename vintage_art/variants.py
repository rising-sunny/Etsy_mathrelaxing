"""
variants.py — variant contact sheets for Maurer rose + Phyllotaxis
==================================================================
Each parametric family swept across parameters -> pick favourites for a set.

    python vintage_art/variants.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
CREAM = "#f1ece1"
INK = (0.16, 0.11, 0.07)
GOLD = (0.647, 0.494, 0.204)


def _grid(title, fname, draw, params):
    fig, axes = plt.subplots(3, 3, figsize=(12, 12.7))
    fig.patch.set_facecolor(CREAM)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.945, bottom=0.02,
                        wspace=0.07, hspace=0.14)
    fig.text(0.5, 0.975, title, ha="center", color=INK,
             family="serif", fontsize=18, weight="bold")
    for ax, p in zip(axes.ravel(), params):
        ax.set_facecolor(CREAM)
        label = draw(ax, p)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#cfc7b3"); s.set_linewidth(0.8)
        ax.set_title(label, color=INK, family="serif", fontsize=12, pad=5)
    out = OUT / fname
    fig.savefig(out, dpi=140, facecolor=CREAM); plt.close(fig)
    print("  ->", out.name)


def maurer(ax, p):
    n, d = p
    k = np.arange(0, 361)
    th = np.radians(k * d)
    r = np.sin(n * th)
    ax.plot(r * np.cos(th), r * np.sin(th), color=INK, lw=0.35, alpha=0.55)
    tt = np.linspace(0, 2 * np.pi, 1600)
    rr = np.sin(n * tt)
    ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=GOLD, lw=1.1, alpha=0.85)
    m = 1.05
    ax.set_xlim(-m, m); ax.set_ylim(-m, m)
    return f"n={n}  d={d}"


def phyllo(ax, p):
    ang_deg, seeds, gold_step = p
    i = np.arange(1, seeds + 1)
    ga = np.radians(ang_deg)
    r = np.sqrt(i)
    th = i * ga
    x, y = r * np.cos(th), r * np.sin(th)
    sizes = 1.0 + 9 * (i / seeds) ** 1.3
    gmask = (i % gold_step == 0)
    ax.scatter(x[~gmask], y[~gmask], s=sizes[~gmask], c=[INK], alpha=0.8, edgecolors="none")
    ax.scatter(x[gmask], y[gmask], s=sizes[gmask], c=[GOLD], alpha=0.85, edgecolors="none")
    m = np.sqrt(seeds) * 1.05
    ax.set_xlim(-m, m); ax.set_ylim(-m, m)
    return f"{ang_deg}°"


MAURER = [(2, 39), (3, 79), (4, 31), (5, 97), (6, 71),
          (7, 19), (8, 47), (11, 53), (13, 37)]

PHYLLO = [(137.508, 1600, 5), (137.3, 1600, 5), (137.7, 1600, 5),
          (137.508, 1600, 8), (137.1, 1600, 6), (138.0, 1600, 5),
          (99.501, 1600, 5), (137.508, 700, 4), (77.955, 1600, 6)]


if __name__ == "__main__":
    _grid("MAURER ROSE · variants", "variants_maurer.jpg", maurer, MAURER)
    _grid("PHYLLOTAXIS · variants", "variants_phyllotaxis.jpg", phyllo, PHYLLO)
    print("DONE")
