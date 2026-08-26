"""
generate_celestial.py — "Celestial Mathematics" generative art line.

A completely different aesthetic from Neo Deco: deep night-sky grounds with fine
gold/cream astronomical linework, every plate computed from real math —
- Orbits    : an orrery of elliptical planetary orbits
- Lunar     : the synodic month, phases drawn from the illuminated fraction
- Resonance : a harmonograph / orbital-resonance rose (Lissajous family)

Etsy signal: "celestial mathematical art" score 69.5, only ~98 competitors,
100% our generative moat. Output 2:3 masters at 2400x3600 (8x12in @300).

  python generate_celestial.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
from matplotlib.collections import LineCollection

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)
AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")

SKY_TOP, SKY_BOT = "#0c1230", "#05070f"     # night-sky gradient
GOLD = "#d7b45a"
GOLD_HI = "#f0dCa0"
CREAM = "#ece4d0"
FAINT = "#6a6f88"
INK = "#05070f"

CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RAL = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RAL_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")

W, H, DPI = 2400, 3600, 300


def new_plate(seed=0):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # vertical sky gradient
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    top = np.array([int(SKY_TOP[i:i+2], 16) for i in (1, 3, 5)]) / 255
    bot = np.array([int(SKY_BOT[i:i+2], 16) for i in (1, 3, 5)]) / 255
    cols = bot * grad + top * (1 - grad)
    ax.imshow(cols.reshape(-1, 1, 3), extent=[0, 1, 0, 1], aspect="auto", zorder=0)
    # star field
    rng = np.random.default_rng(seed)
    n = 380
    sx, sy = rng.random(n), rng.random(n)
    mag = rng.random(n) ** 3
    ax.scatter(sx, sy, s=mag * 9 + 0.3, c="white", alpha=0.5, linewidths=0, zorder=1)
    bright = rng.random(24)
    ax.scatter(rng.random(24), rng.random(24), s=bright * 26 + 6, c=GOLD_HI,
               alpha=0.7, linewidths=0, zorder=1)
    # thin gold frame
    m = 0.05
    ax.plot([m, 1-m, 1-m, m, m], [m, m, 1-m, 1-m, m], color=GOLD, lw=1.2, zorder=6)
    return fig, ax


def title(ax, t, sub, fig_no):
    ax.text(0.5, 0.115, t, fontproperties=CINZEL, fontsize=30, color=CREAM, ha="center")
    ax.plot([0.34, 0.66], [0.098, 0.098], color=GOLD, lw=1.0)
    ax.text(0.5, 0.072, sub, fontproperties=RAL_I, fontsize=11.5, color=FAINT, ha="center")
    ax.text(0.5, 0.93, tracked(fig_no), fontproperties=RAL, fontsize=10.5, color=GOLD, ha="center")


def tracked(s):
    return "  ".join(s)


# ---------------------------------------------------------------- 1 · ORBITS
def plate_orbits():
    fig, ax = new_plate(seed=7)
    cx, cy = 0.5, 0.56
    # central sun with glow
    for r, a in [(0.055, 0.10), (0.040, 0.18), (0.028, 0.5)]:
        ax.add_patch(Circle((cx, cy), r, color=GOLD_HI, alpha=a, zorder=3))
    ax.add_patch(Circle((cx, cy), 0.020, color=GOLD_HI, zorder=4))
    rng = np.random.default_rng(3)
    radii = np.linspace(0.10, 0.40, 7)
    for i, rr in enumerate(radii):
        ecc = 0.10 + 0.06 * rng.random()
        b = rr * (1 - ecc)
        tilt = np.radians(rng.uniform(-18, 18))
        t = np.linspace(0, 2*np.pi, 400)
        ex, ey = rr*np.cos(t), b*np.sin(t)
        x = cx + ex*np.cos(tilt) - ey*np.sin(tilt)
        y = cy + ex*np.sin(tilt) + ey*np.cos(tilt)
        ax.plot(x, y, color=GOLD, lw=0.9, alpha=0.72, zorder=2)
        # planet on the orbit
        k = rng.integers(0, 400)
        pr = 0.006 + 0.011 * rng.random()
        ax.add_patch(Circle((x[k], y[k]), pr, color=CREAM, zorder=4,
                             ec=GOLD_HI, lw=0.8))
    title(ax, "ORBITS", "elliptical paths of a mechanical heaven", "FIG · I")
    return fig


# ---------------------------------------------------------------- 2 · LUNAR
def moon(ax, cx, cy, r, phase):
    """draw a moon at illuminated `phase` in [0,1] (0=new,.5=full,1=new)."""
    ax.add_patch(Circle((cx, cy), r, color="#11152e", ec=FAINT, lw=0.7, zorder=2))
    # illuminated fraction & shape via terminator ellipse
    th = np.linspace(-np.pi/2, np.pi/2, 100)
    limb_x = r*np.cos(th); limb_y = r*np.sin(th)
    k = np.cos(2*np.pi*phase)            # terminator half-width factor (-1..1)
    term_x = k*r*np.cos(th)
    waxing = phase < 0.5
    if waxing:
        xs = np.concatenate([limb_x, term_x[::-1]])
    else:
        xs = np.concatenate([-limb_x, -term_x[::-1]])
    ys = np.concatenate([limb_y, limb_y[::-1]])
    ax.add_patch(PathPatch(Path(np.column_stack([cx+xs, cy+ys])),
                           facecolor=CREAM, edgecolor="none", zorder=3))
    ax.add_patch(Circle((cx, cy), r, fill=False, ec=GOLD, lw=0.8, zorder=4))


def plate_lunar():
    fig, ax = new_plate(seed=19)
    names = ["New", "Waxing\nCrescent", "First\nQuarter", "Waxing\nGibbous",
             "Full", "Waning\nGibbous", "Last\nQuarter", "Waning\nCrescent"]
    phases = [0.0, 0.15, 0.25, 0.37, 0.5, 0.63, 0.75, 0.87]
    cols, rows = 4, 2
    x0, x1 = 0.16, 0.84
    ys = [0.66, 0.40]
    xs = np.linspace(x0, x1, cols)
    r = 0.066
    for i, (ph, nm) in enumerate(zip(phases, names)):
        c, rr = i % cols, i // cols
        moon(ax, xs[c], ys[rr], r, ph)
        ax.text(xs[c], ys[rr] - r - 0.028, nm, fontproperties=RAL, fontsize=8.5,
                color=FAINT, ha="center", va="top")
    title(ax, "LUNAR PHASES", "the synodic month · 29.53 days", "FIG · II")
    return fig


# ------------------------------------------------------------- 3 · RESONANCE
def plate_resonance():
    fig, ax = new_plate(seed=42)
    cx, cy = 0.5, 0.56
    # damped harmonograph (two pendulums per axis)
    t = np.linspace(0, 60, 9000)
    d = 0.0055
    x = (np.sin(2.0*t + 0.3)*np.exp(-d*t) + np.sin(3.01*t)*np.exp(-d*t)) * 0.5
    y = (np.sin(2.99*t)*np.exp(-d*t) + np.sin(4.0*t + 1.2)*np.exp(-d*t)) * 0.5
    x = cx + x*0.38; y = cy + y*0.38
    pts = np.column_stack([x, y]).reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    # gold gradient along the curve
    c = np.linspace(0, 1, len(segs))
    lc = LineCollection(segs, cmap="YlOrBr_r", array=c, lw=0.8, alpha=0.9, zorder=2)
    ax.add_collection(lc)
    ax.add_patch(Circle((cx, cy), 0.010, color=GOLD_HI, zorder=4))
    title(ax, "RESONANCE", "a harmonograph of commensurate orbits", "FIG · III")
    return fig


def build():
    for name, fn in [("01_orbits", plate_orbits), ("02_lunar", plate_lunar),
                     ("03_resonance", plate_resonance)]:
        print("rendering", name)
        fig = fn()
        fig.savefig(os.path.join(MAST, f"{name}.png"), dpi=DPI,
                    facecolor=INK, pil_kwargs={"quality": 95})
        plt.close(fig)


if __name__ == "__main__":
    build()
