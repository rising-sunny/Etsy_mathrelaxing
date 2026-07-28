"""
gallery.py — contact sheet of mathematical-art forms (decorative studies)
=========================================================================
Nine generative families rendered ink-on-cream so they read as one collection.
All parametric -> each can spawn dozens of unique variants.

    python vintage_art/gallery.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
CREAM = "#f1ece1"
INK = "#2a2118"
GOLD = "#9c7b33"
rng = np.random.default_rng(3)


def de_jong(ax):
    a, b, c, d = -2.24, 0.99, -1.65, 1.72
    n = 220000
    x = np.zeros(n); y = np.zeros(n)
    for i in range(1, n):
        x[i] = np.sin(a * y[i-1]) - np.cos(b * x[i-1])
        y[i] = np.sin(c * x[i-1]) - np.cos(d * y[i-1])
    ax.scatter(x, y, s=0.05, c=INK, alpha=0.25, edgecolors="none", marker=".")
    return "De Jong attractor"


def clifford(ax):
    a, b, c, d = -1.4, 1.6, 1.0, 0.7
    n = 220000
    x = np.zeros(n); y = np.zeros(n)
    for i in range(1, n):
        x[i] = np.sin(a * y[i-1]) + c * np.cos(a * x[i-1])
        y[i] = np.sin(b * x[i-1]) + d * np.cos(b * y[i-1])
    ax.scatter(x, y, s=0.05, c=INK, alpha=0.22, edgecolors="none", marker=".")
    return "Clifford attractor"


def maurer_rose(ax):
    n, d = 6, 71
    k = np.arange(0, 361)
    theta = np.radians(k * d)
    r = np.sin(n * theta)
    ax.plot(r * np.cos(theta), r * np.sin(theta), color=INK, lw=0.5, alpha=0.85)
    tt = np.linspace(0, 2 * np.pi, 1000)
    rr = np.sin(n * tt)
    ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=GOLD, lw=0.8, alpha=0.7)
    return "Maurer rose"


def phyllotaxis(ax):
    n = 1400
    i = np.arange(n)
    ga = np.pi * (3 - np.sqrt(5))
    r = np.sqrt(i)
    th = i * ga
    sizes = 0.6 + 6 * (i / n)
    ax.scatter(r * np.cos(th), r * np.sin(th), s=sizes, c=INK, alpha=0.8,
               edgecolors="none")
    return "Phyllotaxis"


def lissajous(ax):
    t = np.linspace(0, 2 * np.pi, 4000)
    a, b, delta = 5, 4, np.pi / 2
    ax.plot(np.sin(a * t + delta), np.sin(b * t), color=INK, lw=0.8, alpha=0.9)
    return "Lissajous"


def hypotrochoid(ax):
    R, r, d = 5.0, 3.0, 5.0
    t = np.linspace(0, 2 * np.pi * 3, 6000)
    x = (R - r) * np.cos(t) + d * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - d * np.sin((R - r) / r * t)
    ax.plot(x, y, color=INK, lw=0.6, alpha=0.9)
    return "Spirograph"


def superformula(ax):
    def sf(phi, m, n1, n2, n3, a=1, b=1):
        t1 = np.abs(np.cos(m * phi / 4) / a) ** n2
        t2 = np.abs(np.sin(m * phi / 4) / b) ** n3
        return (t1 + t2) ** (-1 / n1)
    phi = np.linspace(0, 2 * np.pi, 4000)
    for i, (m, n1, n2, n3) in enumerate([(7, 0.2, 1.7, 1.7), (12, 0.3, 0.5, 0.5)]):
        rr = sf(phi, m, n1, n2, n3)
        col = INK if i == 0 else GOLD
        ax.plot(rr * np.cos(phi), rr * np.sin(phi), color=col, lw=0.7, alpha=0.85)
    return "Superformula"


def epicycles(ax):
    # square-wave Fourier orbit: sum of rotating vectors, trace the tip
    t = np.linspace(0, 2 * np.pi, 8000)
    x = np.zeros_like(t); y = np.zeros_like(t)
    for k in range(1, 16):
        h = 2 * k - 1
        x += (1 / h) * np.cos(h * t)
        y += (1 / h) * np.sin(h * t)
    ax.plot(x, y, color=INK, lw=0.7, alpha=0.9)
    return "Fourier epicycles"


def chladni(ax):
    n, m = 5, 3
    g = np.linspace(0, 1, 600)
    X, Y = np.meshgrid(g, g)
    Z = (np.cos(n * np.pi * X) * np.cos(m * np.pi * Y) -
         np.cos(m * np.pi * X) * np.cos(n * np.pi * Y))
    ax.contour(X, Y, Z, levels=[0], colors=[INK], linewidths=0.7)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return "Chladni plate"


PANELS = [de_jong, clifford, maurer_rose, phyllotaxis, lissajous,
          hypotrochoid, superformula, epicycles, chladni]


def build():
    fig, axes = plt.subplots(3, 3, figsize=(12, 12.8))
    fig.patch.set_facecolor(CREAM)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.03,
                        wspace=0.08, hspace=0.16)
    fig.text(0.5, 0.97, "MATHEMATICAL ART · form studies", ha="center",
             color=INK, family="serif", fontsize=18, weight="bold")
    for ax, fn in zip(axes.ravel(), PANELS):
        ax.set_facecolor(CREAM)
        name = fn(ax)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#c9c0ac"); s.set_linewidth(0.8)
        ax.set_title(name, color=INK, family="serif", fontsize=12, pad=6)
    out = OUT / "gallery_contact_sheet.jpg"
    fig.savefig(out, dpi=150, facecolor=CREAM); plt.close(fig)
    print("  ->", out.name)


if __name__ == "__main__":
    build()
    print("DONE")
