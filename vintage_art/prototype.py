"""
prototype.py — Vintage math ART studies (decorative, no labels/equations)
=========================================================================
Two directions rendered from code (the moat: real math, not stock/AI):

  1. harmonograph  — sepia ink on aged ivory  (Victorian parlour art, 1890s)
  2. guilloche     — gold on black            (banknote / watch-dial engraving)

    python vintage_art/prototype.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
GOLD = (0.788, 0.635, 0.294)     # #c9a24b
SEPIA = (0.24, 0.145, 0.08)

rng = np.random.default_rng(7)


def _paper(ax, tone=(0.93, 0.905, 0.835)):
    """Aged ivory ground: base tone + fibre noise + foxing specks + vignette."""
    N = 900
    base = np.ones((N, N, 3)) * np.array(tone)
    # fibre grain
    grain = rng.normal(0, 1, (N, N))
    grain = (grain - grain.min()) / (grain.max() - grain.min())
    base *= (0.965 + 0.05 * grain)[..., None]
    # foxing specks (warm brown blotches)
    yy, xx = np.mgrid[0:N, 0:N]
    for _ in range(40):
        cx, cy = rng.uniform(0, N, 2); r = rng.uniform(4, 16)
        d = ((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2
        blot = np.exp(-d) * rng.uniform(0.05, 0.14)
        base *= (1 - blot[..., None] * np.array([0.35, 0.45, 0.6]))
    # vignette — warm sepia edge, not muddy gray
    r = np.sqrt((xx - N / 2) ** 2 + (yy - N / 2) ** 2) / (N / 2)
    vig = np.clip(1 - 0.22 * r ** 2.6, 0, 1)[..., None]
    edge = np.array([0.62, 0.55, 0.44])
    base = base * vig + edge * (1 - vig) * 0.55
    ax.imshow(np.clip(base, 0, 1), extent=(-1.25, 1.25, -1.25, 1.25), zorder=0)


def harmonograph():
    fig = plt.figure(figsize=(8, 8), dpi=250)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_aspect("equal")
    _paper(ax)

    t = np.linspace(0, 110 * np.pi, 150000)
    # lateral harmonograph: two pendulums per axis, slight detune + slow damping
    f = [2.001, 3.0, 3.001, 1.998]
    p = [np.pi / 2, 0, np.pi / 4, 0]
    d = [0.0016, 0.0019, 0.0017, 0.0018]
    x = (0.55 * np.sin(f[0] * t + p[0]) * np.exp(-d[0] * t) +
         0.45 * np.sin(f[1] * t + p[1]) * np.exp(-d[1] * t))
    y = (0.55 * np.sin(f[2] * t + p[2]) * np.exp(-d[2] * t) +
         0.45 * np.sin(f[3] * t + p[3]) * np.exp(-d[3] * t))
    ax.plot(x, y, color=SEPIA, lw=0.35, alpha=0.55, solid_capstyle="round")

    # subtle double-line plate ring (decorative, not scientific)
    th = np.linspace(0, 2 * np.pi, 400)
    for rr, a in ((1.16, 0.5), (1.13, 0.35)):
        ax.plot(rr * np.cos(th), rr * np.sin(th), color=SEPIA, lw=0.7, alpha=a)

    out = OUT / "study_harmonograph.jpg"
    fig.savefig(out, dpi=250, facecolor=(0.93, 0.905, 0.835)); plt.close(fig)
    print("  ->", out.name)


def guilloche():
    fig = plt.figure(figsize=(8, 8), dpi=250)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_aspect("equal")
    fig.patch.set_facecolor("#0b0b0d"); ax.set_facecolor("#0b0b0d")

    # engine-turned guilloche: one continuous line per band. A half-integer
    # scallop count makes each loop precess, braiding the rosette. Nested bands
    # with different lobe counts interfere into the classic banknote weave.
    #        (R,     amp,   lobes,  loops)
    bands = [(1.06, 0.075, 60.5, 42),
             (0.84, 0.065, 46.5, 42),
             (0.60, 0.055, 34.5, 42),
             (0.37, 0.045, 22.5, 42),
             (0.17, 0.030, 12.5, 36)]
    for R, a, n, P in bands:
        th = np.linspace(0, 2 * np.pi * P, 160000)
        rad = R + a * np.cos(n * th)
        ax.plot(rad * np.cos(th), rad * np.sin(th),
                color=GOLD, lw=0.18, alpha=0.5, solid_capstyle="round")
    # crisp framing circles
    tc = np.linspace(0, 2 * np.pi, 800)
    for rr, a in ((1.17, 0.75), (1.15, 0.5), (0.075, 0.8)):
        ax.plot(rr * np.cos(tc), rr * np.sin(tc), color=GOLD, lw=0.6, alpha=a)

    out = OUT / "study_guilloche.jpg"
    fig.savefig(out, dpi=250, facecolor="#0b0b0d"); plt.close(fig)
    print("  ->", out.name)


if __name__ == "__main__":
    harmonograph()
    guilloche()
    print("DONE")
