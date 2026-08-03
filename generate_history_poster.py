"""
generate_history_poster.py — "History of Calculus" timeline poster (PILOT v2)
==============================================================================
Dark, premium redesign of the pilot: black ground, gold linework with a soft
bloom pass (PIL), Cinzel/Raleway type from the coffee-table-book system
(lulu_books/assets/fonts) instead of the plain-serif "scientific plate"
house style used in v1. Same nine milestones, elegant gradient-line diagrams
that echo the book's DARK-background plates (Euler, Mobius, Klein).

  python generate_history_poster.py
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Rectangle
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "history_of_calculus")
os.makedirs(OUT, exist_ok=True)
AF = os.path.join(BASE, "lulu_books", "assets", "fonts")

DARK = "#0d0f12"
CREAM = "#f0ece0"
SUB = "#8f8a78"
GOLD = "#c9a24b"
GOLD_HI = "#f3dfa0"
BRONZE = "#7a5a2a"
LINE = "#2c2a24"

CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RALEWAY = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RALEWAY_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")

plt.rcParams.update({"mathtext.fontset": "stix", "axes.unicode_minus": False})

GOLD_CMAP = LinearSegmentedColormap.from_list("gold", [BRONZE, GOLD, GOLD_HI])

# Per-milestone accent palettes -- structural elements (title, timeline, names)
# stay gold throughout; only the diagram linework varies row to row.
PALETTES = {
    "gold": dict(cmap=GOLD_CMAP, mid=GOLD, hi=GOLD_HI, deep=BRONZE),
    "rose": dict(cmap=LinearSegmentedColormap.from_list("rose", ["#4a1f30", "#b8547a", "#f0c4d8"]),
                 mid="#b8547a", hi="#f0c4d8", deep="#4a1f30"),
    "teal": dict(cmap=LinearSegmentedColormap.from_list("teal", ["#173f3a", "#4f9e8f", "#c3ede2"]),
                 mid="#4f9e8f", hi="#c3ede2", deep="#173f3a"),
    "blue": dict(cmap=LinearSegmentedColormap.from_list("blue", ["#1c2c47", "#5a7fae", "#c8ddf5"]),
                 mid="#5a7fae", hi="#c8ddf5", deep="#1c2c47"),
}

W, H = 12.0, 17.0
DPI = 300

GLOW = lambda lw=1.8, c=GOLD, a=0.30, extra=2.4: [
    pe.Stroke(linewidth=lw + extra, foreground=c, alpha=a), pe.Normal()]


def tracked(s, thin=1):
    """Insert thin-space letter tracking for a more elegant, poster-style caps line."""
    return (" " * thin).join(s)


def grad_line(ax, x, y, cmap=GOLD_CMAP, lw=1.9, alpha=1.0, zorder=4, glow=True, glow_color=None):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, alpha=alpha, linewidths=lw, zorder=zorder,
                         capstyle="round")
    lc.set_array(np.linspace(0, 1, len(x)))
    if glow:
        lc.set_path_effects(GLOW(lw=lw, c=glow_color or GOLD, a=0.25))
    ax.add_collection(lc)


# ---------------------------------------------------------------- diagrams
def draw_archimedes(ax, pal=PALETTES["gold"]):
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), color=SUB, lw=1.0, ls=(0, (1, 2)), alpha=0.7)
    for n, col, a, lw in [(6, SUB, 0.6, 1.0), (12, pal["deep"], 0.85, 1.2)]:
        ang = np.linspace(0, 2 * np.pi, n + 1)
        ax.plot(np.cos(ang), np.sin(ang), color=col, lw=lw, alpha=a)
    ang = np.linspace(0, 2 * np.pi, 49)
    grad_line(ax, np.cos(ang), np.sin(ang), cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    ax.annotate("", xy=(0.92, 0.92), xytext=(0.55, 0.55),
                arrowprops=dict(arrowstyle="->", color=CREAM, lw=1.0))
    ax.text(0.98, 0.98, r"$n\to\infty$", fontsize=13, color=CREAM, ha="left", va="bottom")
    ax.set_xlim(-1.22, 1.55); ax.set_ylim(-1.22, 1.22); ax.set_aspect("equal"); ax.axis("off")


def draw_fermat(ax, pal=PALETTES["gold"]):
    x = np.linspace(-2.2, 2.2, 400)
    y = -0.22 * x**2 + 1.1
    grad_line(ax, x, y, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    ax.axhline(1.1, color=pal["mid"], lw=1.2, alpha=0.9, path_effects=GLOW(lw=1.2, c=pal["mid"], a=0.25))
    e = 0.55
    ax.plot([0, e], [1.1, 1.1 - 0.22 * e**2], color=SUB, lw=1.0, ls=(0, (3, 2)))
    ax.plot([0], [1.1], "o", color=pal["hi"], ms=6, zorder=5, mec=DARK, mew=0.8)
    ax.plot([e], [1.1 - 0.22 * e**2], "o", color=SUB, ms=4.5, zorder=5)
    ax.text(0, 1.28, "max", fontsize=11, color=CREAM, ha="center", fontproperties=RALEWAY_I)
    ax.text(e + 0.06, 1.1 - 0.22 * e**2 - 0.05, "$e$", fontsize=13, color=CREAM, ha="left", va="top")
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.3, 1.5); ax.axis("off")


def draw_newton(ax, pal=PALETTES["gold"]):
    t = np.linspace(0, 2.4, 400)
    x = 0.5 * t**2
    grad_line(ax, t, x, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    t0 = 1.55; x0 = 0.5 * t0**2; slope = t0
    tt = np.linspace(t0 - 0.55, t0 + 0.55, 2)
    ax.plot(tt, x0 + slope * (tt - t0), color=pal["mid"], lw=1.6, path_effects=GLOW(c=pal["mid"]))
    ax.plot([t0], [x0], "o", color=pal["hi"], ms=6, zorder=5, mec=DARK, mew=0.8)
    ax.annotate("", xy=(t0 + 0.5, x0 + slope * 0.5 + 0.35), xytext=(t0, x0),
                arrowprops=dict(arrowstyle="->", color=CREAM, lw=1.0))
    ax.text(t0 + 0.55, x0 + slope * 0.5 + 0.4, r"$\dot{x}$", fontsize=15, color=CREAM)
    ax.text(0.1, 2.6, "$x(t)$", fontsize=12, color=SUB)
    ax.set_xlim(-0.15, 2.7); ax.set_ylim(-0.2, 3.1); ax.axis("off")


def draw_leibniz(ax, pal=PALETTES["gold"]):
    x = np.linspace(-2.3, 2.3, 400)
    y = 0.28 * x + 0.055 * x**2 + 0.6
    grad_line(ax, x, y, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    x0 = 0.3; y0 = 0.28 * x0 + 0.055 * x0**2 + 0.6
    dx, dy = 1.0, 0.28 * 1.0 + 0.055 * (2 * x0 * 1.0)
    ax.plot([x0, x0 + dx], [y0, y0], color=pal["deep"], lw=1.3)
    ax.plot([x0 + dx, x0 + dx], [y0, y0 + dy], color=pal["deep"], lw=1.3)
    ax.plot([x0, x0 + dx], [y0, y0 + dy], color=pal["mid"], lw=1.7, path_effects=GLOW(c=pal["mid"]))
    ax.text(x0 + dx / 2, y0 - 0.16, "$dx$", fontsize=13, color=CREAM, ha="center")
    ax.text(x0 + dx + 0.08, y0 + dy / 2, "$dy$", fontsize=13, color=CREAM, va="center")
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-0.6, 2.4); ax.axis("off")


def draw_cauchy(ax, pal=PALETTES["gold"]):
    x = np.linspace(-2.4, 2.4, 400)
    y = 0.5 * np.tanh(1.3 * x) + 1.1
    grad_line(ax, x, y, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    a, L = 0.0, 1.1
    eps, delta = 0.28, 0.42
    ax.axhspan(L - eps, L + eps, color=pal["mid"], alpha=0.10)
    ax.axvspan(a - delta, a + delta, color=SUB, alpha=0.10)
    ax.axhline(L, color=pal["mid"], lw=0.9, ls=(0, (2, 2)), alpha=0.8)
    ax.axvline(a, color=SUB, lw=0.9, ls=(0, (2, 2)), alpha=0.8)
    ax.plot([a], [L], "o", color=pal["hi"], ms=5.5, zorder=5, mec=DARK, mew=0.8)
    ax.text(a, L + eps + 0.08, r"$L+\varepsilon$", fontsize=10.5, color=CREAM, ha="center")
    ax.text(a + delta + 0.06, 0.35, r"$a+\delta$", fontsize=10.5, color=CREAM)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(0.3, 1.9); ax.axis("off")


def draw_riemann(ax, pal=PALETTES["gold"]):
    f = lambda x: 0.9 + 0.55 * np.sin(1.15 * x) + 0.12 * x
    x = np.linspace(-2.3, 2.3, 400)
    grad_line(ax, x, f(x), cmap=pal["cmap"], lw=1.7, zorder=6, glow_color=pal["mid"])
    edges = np.linspace(-2.1, 2.1, 13)
    hmax = max(f((edges[i] + edges[i + 1]) / 2) for i in range(len(edges) - 1))
    for i in range(len(edges) - 1):
        xm = (edges[i] + edges[i + 1]) / 2
        h = f(xm)
        col = pal["cmap"](0.25 + 0.6 * h / hmax)
        ax.add_patch(Rectangle((edges[i], 0), edges[i + 1] - edges[i], h,
                                facecolor=col, edgecolor=DARK, lw=0.6, alpha=0.55, zorder=3))
    ax.axhline(0, color=SUB, lw=0.9)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.15, 2.0); ax.axis("off")


def draw_weierstrass(ax, pal=PALETTES["gold"]):
    x = np.linspace(-2.3, 2.3, 1600)
    a, b, N = 0.5, 6.0, 7
    y = sum(a**n * np.cos(b**n * np.pi * x) for n in range(N))
    y = 0.55 * y / np.max(np.abs(y)) + 1.0
    grad_line(ax, x, y, cmap=pal["cmap"], lw=0.6, glow=False)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(0.2, 1.8); ax.axis("off")


def draw_lebesgue(ax, pal=PALETTES["gold"]):
    f = lambda x: 1.0 + 0.5 * np.sin(1.3 * x) + 0.35 * np.sin(2.6 * x + 0.6)
    x = np.linspace(-2.3, 2.3, 500)
    grad_line(ax, x, f(x), cmap=pal["cmap"], lw=1.7, zorder=6, glow_color=pal["mid"])
    levels = np.linspace(0.35, 1.75, 7)
    for lv in levels:
        idx = np.where(np.diff(np.sign(f(x) - lv)))[0]
        if len(idx) == 0:
            continue
        ax.axhline(lv, color=SUB, lw=0.55, ls=(0, (1, 2)), zorder=1, alpha=0.6)
        for xi in x[idx]:
            ax.plot([xi], [lv], "o", color=pal["hi"], ms=3.4, zorder=5, mec=DARK, mew=0.5)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(0.15, 2.05); ax.axis("off")


def draw_robinson(ax, pal=PALETTES["gold"]):
    ax.axhline(0, color=CREAM, lw=1.3)
    for x in [-2, -1, 0, 1, 2]:
        ax.plot([x], [0], "|", color=CREAM, ms=10, mew=1.2)
        ax.text(x, -0.28, str(x), fontsize=10.5, color=SUB, ha="center")
    circ = Circle((1, 0), 0.3, facecolor="none", edgecolor=pal["mid"], lw=1.1, ls=(0, (2, 2)),
                  path_effects=GLOW(lw=1.1, c=pal["mid"], a=0.3))
    ax.add_patch(circ)
    rng = np.random.default_rng(7)
    pts = 1 + rng.normal(0, 0.05, 14)
    ax.plot(pts, np.zeros_like(pts), "o", color=pal["hi"], ms=3.2, alpha=0.9, zorder=5, mec=DARK, mew=0.4)
    ax.annotate("monad", xy=(1.22, 0.13), xytext=(1.7, 0.55),
                arrowprops=dict(arrowstyle="->", color=SUB, lw=0.9),
                fontsize=11, color=CREAM, fontproperties=RALEWAY_I)
    ax.set_xlim(-2.6, 2.6); ax.set_ylim(-0.6, 0.9); ax.set_aspect("equal"); ax.axis("off")


MILESTONES = [
    ("c. 250 BCE", "ARCHIMEDES", "METHOD OF EXHAUSTION",
     r"$A=\lim_{n\to\infty}A_n$", "gold", draw_archimedes),
    ("1636", "PIERRE DE FERMAT", "MAXIMA, MINIMA & TANGENTS",
     r"$f(x_0+e)\approx f(x_0)$", "rose", draw_fermat),
    ("1666", "ISAAC NEWTON", "THE METHOD OF FLUXIONS",
     r"$\dot{x}=\frac{dx}{dt}$", "teal", draw_newton),
    ("1675", "GOTTFRIED LEIBNIZ", "DIFFERENTIAL NOTATION",
     r"$\int y\,dx,\quad \frac{dy}{dx}$", "rose", draw_leibniz),
    ("1821", "AUGUSTIN-LOUIS CAUCHY", "RIGOROUS LIMITS",
     r"$\lim_{x\to a}f(x)=L$", "blue", draw_cauchy),
    ("1854", "BERNHARD RIEMANN", "THE RIEMANN INTEGRAL",
     r"$\int_a^b f\,dx=\lim_{\|\Delta\|\to0}\sum_i f(x_i^*)\Delta x_i$", "gold", draw_riemann),
    ("1872", "KARL WEIERSTRASS", "A CONTINUOUS, NOWHERE-SMOOTH MONSTER",
     r"$f(x)=\sum_{n=0}^{\infty}a^n\cos(b^n\pi x)$", "teal", draw_weierstrass),
    ("1902", "HENRI LEBESGUE", "MEASURE & INTEGRATION",
     r"$\int f\,d\mu$", "blue", draw_lebesgue),
    ("1960s AND BEYOND", "ABRAHAM ROBINSON", "NONSTANDARD ANALYSIS",
     r"$\varepsilon\neq0,\ \varepsilon\approx0$", "gold", draw_robinson),
]


def build():
    n = len(MILESTONES)
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_facecolor(DARK)
    gs = fig.add_gridspec(
        nrows=n + 2, ncols=3,
        height_ratios=[1.65] + [1.0] * n + [0.7],
        width_ratios=[0.30, 0.44, 0.26],
        left=0.09, right=0.95, top=0.965, bottom=0.03,
        hspace=0.28, wspace=0.02,
    )

    ax_title = fig.add_subplot(gs[0, :]); ax_title.axis("off"); ax_title.set_facecolor(DARK)
    ax_title.text(0.5, 0.80, tracked("HISTORY OF", 1), fontsize=23, color=CREAM, ha="center",
                  va="center", fontproperties=CINZEL_R)
    ax_title.text(0.5, 0.555, tracked("CALCULUS", 1), fontsize=48, color=GOLD, ha="center",
                  va="center", fontproperties=CINZEL, path_effects=GLOW(lw=0.5, a=0.35, extra=3.5))
    ax_title.plot([0.40, 0.60], [0.335, 0.335], color=GOLD, lw=1.0, alpha=0.85)
    ax_title.text(0.5, 0.18, tracked("FROM ARCHIMEDES TO THE INFINITESIMAL", 1), fontsize=11.5,
                  color=SUB, ha="center", va="center", fontproperties=RALEWAY_I)
    ax_title.plot([0.09, 0.91], [0.02, 0.02], color=LINE, lw=1.0)
    ax_title.set_xlim(0, 1); ax_title.set_ylim(0, 1)

    for i, (year, name, label, eq, palkey, drawfn) in enumerate(MILESTONES):
        r = i + 1
        ax_txt = fig.add_subplot(gs[r, 0]); ax_txt.axis("off"); ax_txt.set_facecolor(DARK)
        ax_txt.set_xlim(0, 1); ax_txt.set_ylim(0, 1)
        ax_txt.text(0.18, 0.66, year, fontsize=14, color=CREAM, ha="left", va="center",
                    fontproperties=CINZEL_R)
        ax_txt.text(0.18, 0.46, name, fontsize=10.5, color=GOLD, ha="left", va="center",
                    fontproperties=CINZEL_R)
        ax_txt.text(0.18, 0.30, label, fontsize=7.4, color=SUB, ha="left", va="center",
                    fontproperties=RALEWAY)

        ax_d = fig.add_subplot(gs[r, 1]); ax_d.set_facecolor(DARK)
        drawfn(ax_d, PALETTES[palkey])

        ax_eq = fig.add_subplot(gs[r, 2]); ax_eq.axis("off"); ax_eq.set_facecolor(DARK)
        ax_eq.set_xlim(0, 1); ax_eq.set_ylim(0, 1)
        ax_eq.text(0.06, 0.5, eq, fontsize=13, color=CREAM, ha="left", va="center")

    ax_foot = fig.add_subplot(gs[-1, :]); ax_foot.axis("off"); ax_foot.set_facecolor(DARK)
    ax_foot.set_xlim(0, 1); ax_foot.set_ylim(0, 1)
    ax_foot.plot([0.09, 0.91], [0.85, 0.85], color=LINE, lw=1.0)
    ax_foot.text(0.5, 0.35, "Four thousand years of rigor, from exhaustion to infinitesimals.",
                 fontsize=11, color=SUB, ha="center", fontproperties=RALEWAY_I)
    ax_foot.text(0.5, 0.05, "MathRelaxing", fontsize=11, color=GOLD, ha="center",
                 fontproperties=CINZEL_R)

    positions = gs.get_grid_positions(fig)
    bottoms, tops, lefts, rights = positions
    x_dot = lefts[0] + 0.028
    y_top = tops[1]
    y_bot = bottoms[-2]
    overlay = fig.add_axes([0, 0, 1, 1]); overlay.axis("off"); overlay.set_zorder(10)
    overlay.set_xlim(0, 1); overlay.set_ylim(0, 1)
    overlay.plot([x_dot, x_dot], [y_bot, y_top], color=LINE, lw=1.6, solid_capstyle="round")
    for i in range(n):
        yc = (bottoms[i + 1] + tops[i + 1]) / 2
        overlay.plot([x_dot], [yc], "o", color=GOLD, ms=7.5, mec=DARK, mew=1.4, zorder=11,
                     path_effects=GLOW(lw=0, a=0.4, extra=6))

    raw_png = os.path.join(OUT, "_history_of_calculus_raw.png")
    fig.savefig(raw_png, facecolor=DARK)
    plt.close(fig)

    img = Image.open(raw_png).convert("RGB")
    bloomed = add_bloom(img, blur_radius=round(10 * DPI / 200))
    out_png = os.path.join(OUT, "history_of_calculus_v2_preview.png")
    bloomed.save(out_png)
    print("wrote", out_png)


def add_bloom(img: Image.Image, threshold=150, blur_radius=10, intensity=0.55) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    lum = arr.mean(axis=2)
    mask = np.clip((lum - threshold) / max(1, 255 - threshold), 0, 1)
    bright = (arr * mask[..., None]).astype(np.uint8)
    blurred = Image.fromarray(bright).filter(ImageFilter.GaussianBlur(blur_radius))
    out = arr + np.asarray(blurred).astype(np.float32) * intensity
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    build()
