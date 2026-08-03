"""
generate_history_poster.py — "History of Calculus" timeline poster (PILOT)
===========================================================================
A vertical timeline poster in the house "scientific plate" style (warm
cream paper, ink serif type, rust accent) rather than the cool blue/white
of the reference image the shop owner found on social media. Nine
milestones from Archimedes to Robinson's nonstandard analysis, each paired
with a small bespoke diagram and its defining equation. Built to validate
the "History of X" timeline-poster format before committing to a series.

  python generate_history_poster.py
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "history_of_calculus")
os.makedirs(OUT, exist_ok=True)

CREAM = "#f4f1ea"
INK = "#1a1a1a"
INK_SOFT = "#5a564e"
INK_FAINT = "#9a948a"
RUST = "#b85c38"
RUST_SOFT = "#c4785a"
LINE = "#dad3c3"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["STIXGeneral", "DejaVu Serif", "Times New Roman", "Georgia"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
})

W, H = 12.0, 17.0
DPI = 200


# ---------------------------------------------------------------- diagrams
def draw_archimedes(ax):
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), color=INK_FAINT, lw=1.1, ls=(0, (1, 2)))
    for n, col, a in [(6, INK_FAINT, 0.55), (12, RUST_SOFT, 0.75), (48, RUST, 1.0)]:
        ang = np.linspace(0, 2 * np.pi, n + 1)
        ax.plot(np.cos(ang), np.sin(ang), color=col, lw=1.3, alpha=a)
    ax.annotate("", xy=(0.92, 0.92), xytext=(0.55, 0.55),
                arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=1.1))
    ax.text(0.98, 0.98, r"$n\to\infty$", fontsize=13, color=INK_SOFT, ha="left", va="bottom")
    ax.set_xlim(-1.35, 1.7); ax.set_ylim(-1.35, 1.35); ax.set_aspect("equal"); ax.axis("off")


def draw_fermat(ax):
    x = np.linspace(-2.2, 2.2, 400)
    y = -0.22 * x**2 + 1.1
    ax.plot(x, y, color=INK, lw=1.6)
    ax.axhline(1.1, color=RUST, lw=1.3)
    e = 0.55
    ax.plot([0, e], [1.1, 1.1 - 0.22 * e**2], color=INK_SOFT, lw=1.0, ls=(0, (3, 2)))
    ax.plot([0], [1.1], "o", color=RUST, ms=6, zorder=5)
    ax.plot([e], [1.1 - 0.22 * e**2], "o", color=INK_SOFT, ms=4.5, zorder=5)
    ax.text(0, 1.28, "max", fontsize=11, color=INK_SOFT, ha="center")
    ax.text(e + 0.06, 1.1 - 0.22 * e**2 - 0.05, "$e$", fontsize=13, color=INK_SOFT, ha="left", va="top")
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.3, 1.5); ax.axis("off")


def draw_newton(ax):
    t = np.linspace(0, 2.4, 400)
    x = 0.5 * t**2
    ax.plot(t, x, color=INK, lw=1.6)
    t0 = 1.55; x0 = 0.5 * t0**2; slope = t0
    tt = np.linspace(t0 - 0.55, t0 + 0.55, 2)
    ax.plot(tt, x0 + slope * (tt - t0), color=RUST, lw=1.6)
    ax.plot([t0], [x0], "o", color=RUST, ms=6, zorder=5)
    ax.annotate("", xy=(t0 + 0.5, x0 + slope * 0.5 + 0.35), xytext=(t0, x0),
                arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=1.0))
    ax.text(t0 + 0.55, x0 + slope * 0.5 + 0.4, r"$\dot{x}$", fontsize=15, color=INK_SOFT)
    ax.text(0.1, 2.6, "$x(t)$", fontsize=12, color=INK_SOFT)
    ax.set_xlim(-0.15, 2.7); ax.set_ylim(-0.2, 3.1); ax.axis("off")


def draw_leibniz(ax):
    x = np.linspace(-2.3, 2.3, 400)
    y = 0.28 * x + 0.055 * x**2 + 0.6
    ax.plot(x, y, color=INK, lw=1.6)
    x0 = 0.3; y0 = 0.28 * x0 + 0.055 * x0**2 + 0.6
    dx, dy = 1.0, 0.28 * 1.0 + 0.055 * (2 * x0 * 1.0)
    ax.plot([x0, x0 + dx], [y0, y0], color=RUST_SOFT, lw=1.3)
    ax.plot([x0 + dx, x0 + dx], [y0, y0 + dy], color=RUST_SOFT, lw=1.3)
    ax.plot([x0, x0 + dx], [y0, y0 + dy], color=RUST, lw=1.6)
    ax.text(x0 + dx / 2, y0 - 0.16, "$dx$", fontsize=13, color=INK_SOFT, ha="center")
    ax.text(x0 + dx + 0.08, y0 + dy / 2, "$dy$", fontsize=13, color=INK_SOFT, va="center")
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-0.6, 2.4); ax.axis("off")


def draw_cauchy(ax):
    x = np.linspace(-2.4, 2.4, 400)
    y = 0.5 * np.tanh(1.3 * x) + 1.1
    ax.plot(x, y, color=INK, lw=1.6)
    a, L = 0.0, 1.1
    eps, delta = 0.28, 0.42
    ax.axhspan(L - eps, L + eps, color=RUST, alpha=0.12)
    ax.axvspan(a - delta, a + delta, color=INK_SOFT, alpha=0.08)
    ax.axhline(L, color=RUST_SOFT, lw=0.9, ls=(0, (2, 2)))
    ax.axvline(a, color=INK_FAINT, lw=0.9, ls=(0, (2, 2)))
    ax.plot([a], [L], "o", color=RUST, ms=5.5, zorder=5)
    ax.text(a, L + eps + 0.08, r"$L+\varepsilon$", fontsize=10.5, color=INK_SOFT, ha="center")
    ax.text(a + delta + 0.06, 0.35, r"$a+\delta$", fontsize=10.5, color=INK_SOFT)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(0.3, 1.9); ax.axis("off")


def draw_riemann(ax):
    f = lambda x: 0.9 + 0.55 * np.sin(1.15 * x) + 0.12 * x
    x = np.linspace(-2.3, 2.3, 400)
    ax.plot(x, f(x), color=INK, lw=1.6, zorder=4)
    edges = np.linspace(-2.1, 2.1, 13)
    for i in range(len(edges) - 1):
        xm = (edges[i] + edges[i + 1]) / 2
        h = f(xm)
        ax.add_patch(Rectangle((edges[i], 0), edges[i + 1] - edges[i], h,
                                facecolor=RUST, edgecolor=INK, lw=0.5, alpha=0.38))
    ax.axhline(0, color=INK_FAINT, lw=0.9)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.15, 2.0); ax.axis("off")


def draw_weierstrass(ax):
    x = np.linspace(-2.3, 2.3, 1600)
    a, b, N = 0.5, 6.0, 7
    y = sum(a**n * np.cos(b**n * np.pi * x) for n in range(N))
    y = 0.55 * y / np.max(np.abs(y)) + 1.0
    ax.plot(x, y, color=RUST, lw=0.55)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(0.2, 1.8); ax.axis("off")


def draw_lebesgue(ax):
    f = lambda x: 1.0 + 0.5 * np.sin(1.3 * x) + 0.35 * np.sin(2.6 * x + 0.6)
    x = np.linspace(-2.3, 2.3, 500)
    ax.plot(x, f(x), color=INK, lw=1.6, zorder=4)
    levels = np.linspace(0.35, 1.75, 7)
    rng = np.random.default_rng(3)
    for lv in levels:
        idx = np.where(np.diff(np.sign(f(x) - lv)))[0]
        if len(idx) == 0:
            continue
        ax.axhline(lv, color=INK_FAINT, lw=0.6, ls=(0, (1, 2)), zorder=1)
        for xi in x[idx]:
            ax.plot([xi], [lv], "o", color=RUST, ms=3.2, zorder=5)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(0.15, 2.05); ax.axis("off")


def draw_robinson(ax):
    ax.axhline(0, color=INK, lw=1.5)
    for x in [-2, -1, 0, 1, 2]:
        ax.plot([x], [0], "|", color=INK, ms=10, mew=1.3)
        ax.text(x, -0.28, str(x), fontsize=10.5, color=INK_SOFT, ha="center")
    circ = Circle((1, 0), 0.3, facecolor="none", edgecolor=RUST, lw=1.1, ls=(0, (2, 2)))
    ax.add_patch(circ)
    rng = np.random.default_rng(7)
    pts = 1 + rng.normal(0, 0.05, 14)
    ax.plot(pts, np.zeros_like(pts), "o", color=RUST, ms=3.2, alpha=0.85, zorder=5)
    ax.annotate("monad", xy=(1.22, 0.13), xytext=(1.7, 0.55),
                arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.9),
                fontsize=11, color=INK_SOFT, style="italic")
    ax.set_xlim(-2.6, 2.6); ax.set_ylim(-0.6, 0.9); ax.axis("off")


MILESTONES = [
    ("c. 250 BCE", "ARCHIMEDES", "METHOD OF EXHAUSTION",
     r"$A=\lim_{n\to\infty}A_n$", draw_archimedes),
    ("1636", "PIERRE DE FERMAT", "MAXIMA, MINIMA & TANGENTS",
     r"$f(x+e)\ \mathrm{adæq}\ f(x)$", draw_fermat),
    ("1666", "ISAAC NEWTON", "THE METHOD OF FLUXIONS",
     r"$\dot{x}=\frac{dx}{dt}$", draw_newton),
    ("1675", "GOTTFRIED LEIBNIZ", "DIFFERENTIAL NOTATION",
     r"$\int y\,dx,\quad \frac{dy}{dx}$", draw_leibniz),
    ("1821", "AUGUSTIN-LOUIS CAUCHY", "RIGOROUS LIMITS",
     r"$\lim_{x\to a}f(x)=L$", draw_cauchy),
    ("1854", "BERNHARD RIEMANN", "THE RIEMANN INTEGRAL",
     r"$\int_a^b f\,dx=\lim_{\|\Delta\|\to0}\sum_i f(x_i^*)\Delta x_i$", draw_riemann),
    ("1872", "KARL WEIERSTRASS", "A CONTINUOUS, NOWHERE-SMOOTH MONSTER",
     r"$f(x)=\sum_{n=0}^{\infty}a^n\cos(b^n\pi x)$", draw_weierstrass),
    ("1902", "HENRI LEBESGUE", "MEASURE & INTEGRATION",
     r"$\int f\,d\mu$", draw_lebesgue),
    ("1960s AND BEYOND", "ABRAHAM ROBINSON", "NONSTANDARD ANALYSIS",
     r"$\varepsilon\neq0,\ \varepsilon\approx0$", draw_robinson),
]


def build():
    n = len(MILESTONES)
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_facecolor(CREAM)
    gs = fig.add_gridspec(
        nrows=n + 2, ncols=3,
        height_ratios=[1.9] + [1.0] * n + [0.7],
        width_ratios=[0.30, 0.44, 0.26],
        left=0.09, right=0.95, top=0.965, bottom=0.03,
        hspace=0.28, wspace=0.02,
    )

    ax_title = fig.add_subplot(gs[0, :]); ax_title.axis("off"); ax_title.set_facecolor(CREAM)
    ax_title.text(0.5, 0.62, "HISTORY OF", fontsize=30, color=INK, ha="center",
                  va="center", fontweight="normal", family="serif")
    ax_title.text(0.5, 0.30, "CALCULUS", fontsize=44, color=INK, ha="center",
                  va="center", fontweight="bold", family="serif")
    ax_title.plot([0.30, 0.70], [0.06, 0.06], color=RUST, lw=1.4, transform=ax_title.transAxes)
    ax_title.set_xlim(0, 1); ax_title.set_ylim(0, 1)

    row_axes = []
    for i, (year, name, label, eq, drawfn) in enumerate(MILESTONES):
        r = i + 1
        ax_txt = fig.add_subplot(gs[r, 0]); ax_txt.axis("off"); ax_txt.set_facecolor(CREAM)
        ax_txt.set_xlim(0, 1); ax_txt.set_ylim(0, 1)
        ax_txt.text(0.18, 0.66, year, fontsize=14.5, color=INK, ha="left", va="center",
                    fontweight="bold")
        ax_txt.text(0.18, 0.46, name, fontsize=10.5, color=RUST, ha="left", va="center",
                    fontweight="bold")
        ax_txt.text(0.18, 0.32, label, fontsize=7.6, color=INK_SOFT, ha="left", va="center",
                    style="normal")

        ax_d = fig.add_subplot(gs[r, 1]); ax_d.set_facecolor(CREAM)
        drawfn(ax_d)

        ax_eq = fig.add_subplot(gs[r, 2]); ax_eq.axis("off"); ax_eq.set_facecolor(CREAM)
        ax_eq.set_xlim(0, 1); ax_eq.set_ylim(0, 1)
        ax_eq.text(0.06, 0.5, eq, fontsize=13.5, color=INK, ha="left", va="center")
        row_axes.append(ax_txt)

    ax_foot = fig.add_subplot(gs[-1, :]); ax_foot.axis("off"); ax_foot.set_facecolor(CREAM)
    ax_foot.set_xlim(0, 1); ax_foot.set_ylim(0, 1)
    ax_foot.plot([0.09, 0.91], [0.85, 0.85], color=LINE, lw=1.0)
    ax_foot.text(0.5, 0.35, "Four thousand years of rigor, from exhaustion to infinitesimals.",
                 fontsize=11, color=INK_SOFT, ha="center", style="italic")
    ax_foot.text(0.5, 0.05, "MathRelaxing", fontsize=10.5, color=INK_FAINT, ha="center")

    # timeline rule + dots, drawn in figure coordinates over column 0
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
        overlay.plot([x_dot], [yc], "o", color=RUST, ms=8, mec=CREAM, mew=1.6, zorder=11)

    out_png = os.path.join(OUT, "history_of_calculus_preview.png")
    fig.savefig(out_png, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out_png)


if __name__ == "__main__":
    build()
