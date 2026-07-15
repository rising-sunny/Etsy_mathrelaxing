"""
generate_unit_circle.py — Unit Circle scientific-plate (test images)
====================================================================
MathRelaxing Maxwell / Schrödinger family:
  cream graph paper · serif / STIX math · rust accents · classroom wall art

  python generate_unit_circle.py              # plate + previews (test set)
  python generate_unit_circle.py --preview-only
  python generate_unit_circle.py --full        # also multi-size prints + zip
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Arc
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "unit_circle")
PRINTS = os.path.join(OUT, "prints")
PREVIEWS = os.path.join(OUT, "previews")

# Palette — match Schrödinger / Maxwell plates
CREAM = "#F4F1EA"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#555555"
INK_FAINT = "#8A857C"
RUST = "#B85C38"
RUST_SOFT = "#C4785A"
LINE_DARK = "#222222"

DPI_PRINT = 300
DPI_PREVIEW = 150

SIZES = {
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
    "5x7": (10.0, 14.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
}

# Special angles (degrees) labeled on the circle
ANGLE_DEGS = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]

# Exact coordinate labels for common angles (mathtext)
COORDS = {
    0: r"$(1,\,0)$",
    30: r"$\left(\dfrac{\sqrt{3}}{2},\,\dfrac{1}{2}\right)$",
    45: r"$\left(\dfrac{\sqrt{2}}{2},\,\dfrac{\sqrt{2}}{2}\right)$",
    60: r"$\left(\dfrac{1}{2},\,\dfrac{\sqrt{3}}{2}\right)$",
    90: r"$(0,\,1)$",
    120: r"$\left(-\dfrac{1}{2},\,\dfrac{\sqrt{3}}{2}\right)$",
    135: r"$\left(-\dfrac{\sqrt{2}}{2},\,\dfrac{\sqrt{2}}{2}\right)$",
    150: r"$\left(-\dfrac{\sqrt{3}}{2},\,\dfrac{1}{2}\right)$",
    180: r"$(-1,\,0)$",
    210: r"$\left(-\dfrac{\sqrt{3}}{2},\,-\dfrac{1}{2}\right)$",
    225: r"$\left(-\dfrac{\sqrt{2}}{2},\,-\dfrac{\sqrt{2}}{2}\right)$",
    240: r"$\left(-\dfrac{1}{2},\,-\dfrac{\sqrt{3}}{2}\right)$",
    270: r"$(0,\,-1)$",
    300: r"$\left(\dfrac{1}{2},\,-\dfrac{\sqrt{3}}{2}\right)$",
    315: r"$\left(\dfrac{\sqrt{2}}{2},\,-\dfrac{\sqrt{2}}{2}\right)$",
    330: r"$\left(\dfrac{\sqrt{3}}{2},\,-\dfrac{1}{2}\right)$",
}


def configure_matplotlib(use_latex: bool = True) -> bool:
    has_tex = bool(shutil.which("latex") or shutil.which("pdflatex"))
    use_latex = use_latex and has_tex
    if use_latex:
        try:
            plt.rcParams.update(
                {
                    "text.usetex": True,
                    "font.family": "serif",
                    "font.serif": ["Computer Modern Roman", "cmr10", "Times New Roman"],
                    "mathtext.fontset": "cm",
                    "axes.unicode_minus": False,
                    "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}",
                }
            )
            fig = plt.figure(figsize=(1, 1))
            fig.text(0.5, 0.5, r"$\pi$")
            fig.canvas.draw()
            plt.close(fig)
            print("  math rendering: LaTeX")
            return True
        except Exception as exc:
            print(f"  LaTeX probe failed ({exc}); mathtext fallback")
            plt.rcParams["text.usetex"] = False

    plt.rcParams.update(
        {
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "DejaVu Serif", "Times New Roman", "Georgia"],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
        }
    )
    print("  math rendering: mathtext STIX")
    return False


def _draw_graph_paper(ax, xmin, xmax, ymin, ymax, major=5.0, minor=1.25):
    for x in np.arange(xmin, xmax + minor * 0.5, minor):
        ax.axvline(x, color=GRID_FINE, lw=0.35, zorder=0)
    for y in np.arange(ymin, ymax + minor * 0.5, minor):
        ax.axhline(y, color=GRID_FINE, lw=0.35, zorder=0)
    for x in np.arange(xmin, xmax + major * 0.5, major):
        ax.axvline(x, color=GRID, lw=0.55, zorder=0)
    for y in np.arange(ymin, ymax + major * 0.5, major):
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def _fs(fig_w_in: float, frac: float) -> float:
    return max(7.0, fig_w_in * 72 * frac)


def _deg_to_rad_label(deg: int) -> str:
    # compact radian fractions
    table = {
        0: r"$0$",
        30: r"$\frac{\pi}{6}$",
        45: r"$\frac{\pi}{4}$",
        60: r"$\frac{\pi}{3}$",
        90: r"$\frac{\pi}{2}$",
        120: r"$\frac{2\pi}{3}$",
        135: r"$\frac{3\pi}{4}$",
        150: r"$\frac{5\pi}{6}$",
        180: r"$\pi$",
        210: r"$\frac{7\pi}{6}$",
        225: r"$\frac{5\pi}{4}$",
        240: r"$\frac{4\pi}{3}$",
        270: r"$\frac{3\pi}{2}$",
        300: r"$\frac{5\pi}{3}$",
        315: r"$\frac{7\pi}{4}$",
        330: r"$\frac{11\pi}{6}$",
    }
    return table.get(deg, rf"${deg}^\circ$")


def _fig_to_rgb(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_rgb(img: Image.Image, path: str, dpi: int = DPI_PRINT, quality: int = 90):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.convert("RGB").save(
        path, "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path}  ({os.path.getsize(path) / 1024:.0f} KB)")


def _draw_unit_circle(ax_circ, fig_w: float, show_coords: bool = True, highlight_45: bool = True):
    """
    Draw the unit circle in data coords centered at origin, radius 1.
    ax_circ must already have equal aspect and limits ~[-1.55, 1.55].
    """
    ax_circ.set_facecolor("none")
    ax_circ.patch.set_alpha(0.0)
    for sp in ax_circ.spines.values():
        sp.set_visible(False)
    ax_circ.set_xticks([])
    ax_circ.set_yticks([])
    ax_circ.set_xlim(-1.62, 1.62)
    ax_circ.set_ylim(-1.62, 1.62)
    ax_circ.set_aspect("equal")
    ax_circ.set_clip_on(False)

    # axes
    ax_circ.axhline(0, color=LINE_DARK, lw=1.15, zorder=2)
    ax_circ.axvline(0, color=LINE_DARK, lw=1.15, zorder=2)
    # arrow tips
    ax_circ.annotate(
        "",
        xy=(1.55, 0),
        xytext=(1.42, 0),
        arrowprops=dict(arrowstyle="-|>", color=LINE_DARK, lw=1.1),
        zorder=3,
    )
    ax_circ.annotate(
        "",
        xy=(0, 1.55),
        xytext=(0, 1.42),
        arrowprops=dict(arrowstyle="-|>", color=LINE_DARK, lw=1.1),
        zorder=3,
    )
    ax_circ.text(1.58, -0.08, r"$x$", fontsize=_fs(fig_w, 0.012), color=INK, ha="left", va="top")
    ax_circ.text(0.06, 1.55, r"$y$", fontsize=_fs(fig_w, 0.012), color=INK, ha="left", va="bottom")

    # unit circle
    circ = Circle((0, 0), 1.0, fill=False, edgecolor=LINE_DARK, lw=2.0, zorder=4)
    ax_circ.add_patch(circ)

    # quadrant labels (subtle)
    q_fs = _fs(fig_w, 0.008)
    ax_circ.text(0.42, 0.42, r"I", fontsize=q_fs, color=INK_FAINT, ha="center", va="center", zorder=3)
    ax_circ.text(-0.42, 0.42, r"II", fontsize=q_fs, color=INK_FAINT, ha="center", va="center", zorder=3)
    ax_circ.text(-0.42, -0.42, r"III", fontsize=q_fs, color=INK_FAINT, ha="center", va="center", zorder=3)
    ax_circ.text(0.42, -0.42, r"IV", fontsize=q_fs, color=INK_FAINT, ha="center", va="center", zorder=3)

    # rays + angle labels + points
    for deg in ANGLE_DEGS:
        th = math.radians(deg)
        c, s = math.cos(th), math.sin(th)
        # ray
        ax_circ.plot([0, c], [0, s], color=INK_FAINT, lw=0.65, zorder=3, solid_capstyle="round")
        # point
        ax_circ.plot(c, s, "o", color=RUST if deg in (0, 45, 90, 180, 270) else LINE_DARK,
                    ms=4.2 if deg % 90 == 0 else 3.2, zorder=6, markeredgewidth=0)

        # angle labels just outside the circle
        r_lab = 1.18
        lx, ly = r_lab * c, r_lab * s
        # small radial push for crowded axes angles
        if deg in (0, 180):
            ly -= 0.06
        if deg == 90:
            lx += 0.04
        if deg == 270:
            lx += 0.04
        ax_circ.text(
            lx, ly,
            _deg_to_rad_label(deg),
            fontsize=_fs(fig_w, 0.0095),
            color=INK,
            ha="center",
            va="center",
            zorder=7,
        )
        # degree under rad for major angles only
        if deg % 45 == 0:
            ax_circ.text(
                1.32 * c, 1.32 * s - (0.02 if deg not in (90, 270) else 0),
                rf"${deg}^{{\circ}}$",
                fontsize=_fs(fig_w, 0.0075),
                color=INK_SOFT,
                ha="center",
                va="center",
                zorder=7,
            )

        if show_coords and deg in (0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330):
            # place coordinates further out, only for cardinal + 45-family to reduce clutter
            if deg in (0, 45, 90, 135, 180, 225, 270, 315) or deg in (30, 60, 120, 150, 210, 240, 300, 330):
                # skip dense 30/60 family outer coords if too crowded — show only cardinals+45 in tight mode
                if show_coords == "major" and deg not in (0, 45, 90, 135, 180, 225, 270, 315):
                    continue
                r_c = 1.48
                # pull axis-aligned labels off the axes a bit
                cx, cy = r_c * c, r_c * s
                if deg == 0:
                    cx, cy = 1.48, -0.22
                elif deg == 90:
                    cx, cy = 0.28, 1.48
                elif deg == 180:
                    cx, cy = -1.48, -0.22
                elif deg == 270:
                    cx, cy = 0.28, -1.48
                # only major coords to keep plate readable
                if deg in (0, 45, 90, 135, 180, 225, 270, 315):
                    ax_circ.text(
                        cx, cy,
                        COORDS[deg],
                        fontsize=_fs(fig_w, 0.0072),
                        color=INK_SOFT,
                        ha="center",
                        va="center",
                        zorder=7,
                    )

    # highlight 45° reference triangle
    if highlight_45:
        th = math.radians(45)
        c, s = math.cos(th), math.sin(th)
        ax_circ.plot([0, c, c, 0], [0, 0, s, 0], color=RUST, lw=1.35, zorder=5, solid_capstyle="round")
        ax_circ.plot([c, c], [0, s], color=RUST, lw=1.35, zorder=5)
        # right-angle marker
        m = 0.08
        ax_circ.plot([c - m, c - m, c], [0, m, m], color=RUST, lw=0.9, zorder=5)
        ax_circ.text(c * 0.52, -0.12, r"$\cos\theta$", fontsize=_fs(fig_w, 0.009), color=RUST, ha="center")
        ax_circ.text(c + 0.12, s * 0.45, r"$\sin\theta$", fontsize=_fs(fig_w, 0.009), color=RUST, ha="left", va="center")
        # angle arc at origin for θ
        arc = Arc((0, 0), 0.45, 0.45, angle=0, theta1=0, theta2=45, color=RUST, lw=1.1, zorder=5)
        ax_circ.add_patch(arc)
        ax_circ.text(0.28, 0.10, r"$\theta$", fontsize=_fs(fig_w, 0.011), color=RUST, ha="center", va="center")

    # origin
    ax_circ.plot(0, 0, "o", color=LINE_DARK, ms=3.5, zorder=6, markeredgewidth=0)
    ax_circ.text(-0.08, -0.12, r"$O$", fontsize=_fs(fig_w, 0.009), color=INK_SOFT, ha="right", va="top")

    # radius label
    ax_circ.annotate(
        r"$r=1$",
        xy=(0.55, 0.55),
        xytext=(0.75, 0.88),
        fontsize=_fs(fig_w, 0.0095),
        color=INK_SOFT,
        arrowprops=dict(arrowstyle="-", color=INK_FAINT, lw=0.7),
        zorder=7,
    )


def compose_plate(width_in: float, height_in: float, dpi: int = DPI_PRINT) -> Image.Image:
    """Full scientific plate: header + unit circle + identities footer."""
    fig_w, fig_h = width_in, height_in
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)

    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 100)
    ax_bg.set_ylim(0, 100)
    ax_bg.set_axis_off()
    ax_bg.set_facecolor(CREAM)
    _draw_graph_paper(ax_bg, 0, 100, 0, 100, major=5.0, minor=1.25)

    margin = 3.0
    ax_bg.add_patch(
        Rectangle(
            (margin, margin),
            100 - 2 * margin,
            100 - 2 * margin,
            fill=False,
            edgecolor=GRID,
            lw=0.9,
            zorder=1,
        )
    )

    # Header
    ax_bg.text(
        6.2,
        93.5,
        r"THE UNIT CIRCLE",
        fontsize=_fs(fig_w, 0.040),
        color=INK,
        va="center",
        ha="left",
        fontweight="bold",
        zorder=5,
        family="sans-serif",
    )
    ax_bg.text(
        93.8,
        93.5,
        r"FIG. 1",
        fontsize=_fs(fig_w, 0.015),
        color=INK_SOFT,
        va="center",
        ha="right",
        zorder=5,
        family="sans-serif",
    )
    ax_bg.text(
        6.2,
        89.0,
        r"TRIGONOMETRY  $\cdot$  $x=\cos\theta$,\; $y=\sin\theta$  $\cdot$  $x^{2}+y^{2}=1$",
        fontsize=_fs(fig_w, 0.013),
        color=RUST,
        va="center",
        ha="left",
        zorder=5,
    )
    ax_bg.plot([6.2, 93.8], [86.2, 86.2], color=INK, lw=0.85, solid_capstyle="butt", zorder=5)

    # Circle panel (figure fraction)
    # Leave room for header top and footer identities
    ax_circ = fig.add_axes([0.10, 0.22, 0.80, 0.58], zorder=2)
    _draw_unit_circle(ax_circ, fig_w, show_coords=True, highlight_45=True)

    # Footer identities
    ax_bg.plot([6.2, 93.8], [18.5, 18.5], color=INK, lw=0.55, zorder=5)
    ax_bg.text(
        6.2,
        15.2,
        r"KEY IDENTITIES",
        fontsize=_fs(fig_w, 0.011),
        color=INK,
        ha="left",
        va="center",
        fontweight="bold",
        family="sans-serif",
        zorder=5,
    )
    ax_bg.text(
        6.2,
        11.5,
        r"$\sin^{2}\theta+\cos^{2}\theta=1$"
        r"  $\quad$  "
        r"$\tan\theta=\dfrac{\sin\theta}{\cos\theta}$"
        r"  $\quad$  "
        r"$\cos\theta=\sin\!\left(\dfrac{\pi}{2}-\theta\right)$",
        fontsize=_fs(fig_w, 0.012),
        color=INK_SOFT,
        ha="left",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        6.2,
        7.5,
        r"point on the circle:\; $(\cos\theta,\;\sin\theta)$"
        r"  $\quad\cdot\quad$  "
        r"radians  $\leftrightarrow$  degrees:\; $\pi=180^{\circ}$",
        fontsize=_fs(fig_w, 0.011),
        color=INK_SOFT,
        ha="left",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        93.8,
        7.5,
        r"MathRelaxing",
        fontsize=_fs(fig_w, 0.009),
        color=INK_FAINT,
        ha="right",
        va="center",
        style="italic",
        zorder=5,
    )

    return _fig_to_rgb(fig)


def compose_square_listing(size_in: float = 8.0, dpi: int = DPI_PREVIEW) -> Image.Image:
    """Square 1:1 listing photo — cropped plate look for Etsy."""
    fig_w = size_in
    fig = plt.figure(figsize=(fig_w, fig_w), dpi=dpi, facecolor=CREAM)
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 100)
    ax_bg.set_ylim(0, 100)
    ax_bg.set_axis_off()
    ax_bg.set_facecolor(CREAM)
    _draw_graph_paper(ax_bg, 0, 100, 0, 100, major=5.0, minor=1.25)

    ax_bg.text(
        50,
        93,
        r"THE UNIT CIRCLE",
        fontsize=_fs(fig_w, 0.036),
        color=INK,
        ha="center",
        va="center",
        fontweight="bold",
        family="sans-serif",
        zorder=5,
    )
    ax_bg.text(
        50,
        87.5,
        r"$(\cos\theta,\;\sin\theta)$",
        fontsize=_fs(fig_w, 0.016),
        color=RUST,
        ha="center",
        va="center",
        zorder=5,
    )
    ax_bg.plot([12, 88], [84, 84], color=INK, lw=0.8, zorder=5)

    ax_circ = fig.add_axes([0.08, 0.08, 0.84, 0.72], zorder=2)
    _draw_unit_circle(ax_circ, fig_w, show_coords=True, highlight_45=True)
    return _fig_to_rgb(fig)


def compose_detail_crop(dpi: int = DPI_PREVIEW) -> Image.Image:
    """Wide crop focused on the 45° triangle and first quadrant."""
    fig_w, fig_h = 12.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 100)
    ax_bg.set_ylim(0, 100)
    ax_bg.set_axis_off()
    ax_bg.set_facecolor(CREAM)
    _draw_graph_paper(ax_bg, 0, 100, 0, 100, major=5.0, minor=1.25)

    ax_bg.text(
        6,
        92,
        r"DETAIL  ·  REFERENCE ANGLE $\theta=45^{\circ}$",
        fontsize=_fs(fig_w, 0.022),
        color=INK,
        ha="left",
        fontweight="bold",
        family="sans-serif",
        zorder=5,
    )
    ax_bg.text(
        6,
        86,
        r"$\cos\frac{\pi}{4}=\sin\frac{\pi}{4}=\frac{\sqrt{2}}{2}$"
        r"  $\quad$  "
        r"right triangle on the unit circle",
        fontsize=_fs(fig_w, 0.014),
        color=RUST,
        ha="left",
        zorder=5,
    )

    ax_circ = fig.add_axes([0.12, 0.08, 0.76, 0.70], zorder=2)
    # zoom first quadrant-ish
    ax_circ.set_facecolor("none")
    ax_circ.patch.set_alpha(0.0)
    for sp in ax_circ.spines.values():
        sp.set_visible(False)
    ax_circ.set_xticks([])
    ax_circ.set_yticks([])
    ax_circ.set_xlim(-0.15, 1.35)
    ax_circ.set_ylim(-0.15, 1.25)
    ax_circ.set_aspect("equal")

    ax_circ.axhline(0, color=LINE_DARK, lw=1.2, zorder=2)
    ax_circ.axvline(0, color=LINE_DARK, lw=1.2, zorder=2)
    circ = Circle((0, 0), 1.0, fill=False, edgecolor=LINE_DARK, lw=2.2, zorder=4)
    ax_circ.add_patch(circ)

    for deg in [0, 30, 45, 60, 90]:
        th = math.radians(deg)
        c, s = math.cos(th), math.sin(th)
        ax_circ.plot([0, c], [0, s], color=INK_FAINT, lw=0.8, zorder=3)
        ax_circ.plot(c, s, "o", color=RUST if deg == 45 else LINE_DARK, ms=5 if deg == 45 else 3.5, zorder=6)
        ax_circ.text(
            1.12 * c + 0.02,
            1.12 * s + 0.02,
            _deg_to_rad_label(deg) + rf"  $({deg}^{{\circ}})$",
            fontsize=_fs(fig_w, 0.012),
            color=INK,
            ha="left" if deg != 90 else "center",
            va="bottom" if deg != 0 else "top",
            zorder=7,
        )
        if deg in (0, 45, 90):
            ax_circ.text(
                1.22 * c + (0.08 if deg == 90 else 0),
                1.22 * s - (0.08 if deg == 0 else 0),
                COORDS[deg],
                fontsize=_fs(fig_w, 0.011),
                color=INK_SOFT,
                zorder=7,
            )

    th = math.radians(45)
    c, s = math.cos(th), math.sin(th)
    ax_circ.plot([0, c, c, 0], [0, 0, s, 0], color=RUST, lw=1.8, zorder=5)
    ax_circ.plot([c, c], [0, s], color=RUST, lw=1.8, zorder=5)
    m = 0.06
    ax_circ.plot([c - m, c - m, c], [0, m, m], color=RUST, lw=1.0, zorder=5)
    ax_circ.text(c * 0.5, -0.08, r"$\cos\theta$", fontsize=_fs(fig_w, 0.014), color=RUST, ha="center")
    ax_circ.text(c + 0.06, s * 0.5, r"$\sin\theta$", fontsize=_fs(fig_w, 0.014), color=RUST, ha="left")
    arc = Arc((0, 0), 0.4, 0.4, angle=0, theta1=0, theta2=45, color=RUST, lw=1.4, zorder=5)
    ax_circ.add_patch(arc)
    ax_circ.text(0.22, 0.08, r"$\theta$", fontsize=_fs(fig_w, 0.016), color=RUST)

    return _fig_to_rgb(fig)


def compose_included_card(dpi: int = DPI_PREVIEW) -> Image.Image:
    fig = plt.figure(figsize=(10, 10), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, major=5.0, minor=1.25)

    ax.text(52, 82, "included", fontsize=26, color=INK, ha="left", fontweight="bold", family="sans-serif")
    lines = [
        "1 scientific-plate print",
        "Unit circle · radians & degrees",
        "exact coordinates at key angles",
        "",
        "Aspect ratios:",
        "2:3  ·  3:4  ·  4:5  ·  5:7",
        "ISO A4  ·  A3",
        "",
        "300 dpi JPG  ·  ZIP",
        "classroom · study · dorm",
        "",
        "Best on matte paper",
        "Instant download",
    ]
    y = 72
    for line in lines:
        ax.text(52, y, line, fontsize=13, color=INK_SOFT, ha="left")
        y -= 4.2

    base = _fig_to_rgb(fig)
    mini = compose_plate(5.0, 7.0, dpi=dpi)
    mini = mini.resize(
        (int(base.size[0] * 0.42), int(base.size[1] * 0.68)),
        Image.Resampling.LANCZOS,
    )
    base.paste(mini, (int(base.size[0] * 0.05), int(base.size[1] * 0.16)))
    return base


def compose_table_card(width_in: float = 10.0, height_in: float = 8.0, dpi: int = DPI_PREVIEW) -> Image.Image:
    """Reference table of special angles — secondary listing image."""
    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, major=5.0, minor=1.25)

    ax.text(
        50, 92,
        "SPECIAL ANGLES",
        fontsize=_fs(width_in, 0.028),
        color=INK,
        ha="center",
        fontweight="bold",
        family="sans-serif",
    )
    ax.text(
        50, 86,
        r"exact values on the unit circle",
        fontsize=_fs(width_in, 0.014),
        color=RUST,
        ha="center",
    )
    ax.plot([12, 88], [82, 82], color=INK, lw=0.7)

    # table headers
    headers = [r"$\theta^{\circ}$", r"$\theta$ rad", r"$\sin\theta$", r"$\cos\theta$", r"$\tan\theta$"]
    rows = [
        (r"$0$", r"$0$", r"$0$", r"$1$", r"$0$"),
        (r"$30$", r"$\pi/6$", r"$1/2$", r"$\sqrt{3}/2$", r"$1/\sqrt{3}$"),
        (r"$45$", r"$\pi/4$", r"$\sqrt{2}/2$", r"$\sqrt{2}/2$", r"$1$"),
        (r"$60$", r"$\pi/3$", r"$\sqrt{3}/2$", r"$1/2$", r"$\sqrt{3}$"),
        (r"$90$", r"$\pi/2$", r"$1$", r"$0$", r"—"),
        (r"$180$", r"$\pi$", r"$0$", r"$-1$", r"$0$"),
        (r"$270$", r"$3\pi/2$", r"$-1$", r"$0$", r"—"),
        (r"$360$", r"$2\pi$", r"$0$", r"$1$", r"$0$"),
    ]
    cols_x = [14, 30, 48, 66, 84]
    y = 76
    for i, h in enumerate(headers):
        ax.text(cols_x[i], y, h, fontsize=_fs(width_in, 0.014), color=RUST, ha="center", fontweight="bold")
    y = 70
    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            ax.add_patch(Rectangle((8, y - 2.2), 84, 5.2, facecolor="#EFEBE3", edgecolor="none", zorder=1))
        for i, cell in enumerate(row):
            ax.text(cols_x[i], y, cell, fontsize=_fs(width_in, 0.013), color=INK, ha="center", zorder=2)
        y -= 6.5

    ax.text(
        50, 8,
        r"$\sin^{2}\theta+\cos^{2}\theta=1$  ·  MathRelaxing",
        fontsize=_fs(width_in, 0.012),
        color=INK_FAINT,
        ha="center",
    )
    return _fig_to_rgb(fig)


def build_test_images():
    """Generate a small test pack for review (not full print run)."""
    os.makedirs(PREVIEWS, exist_ok=True)
    os.makedirs(PRINTS, exist_ok=True)

    print("1/6 plate hero (portrait)…")
    hero = compose_plate(10.0, 12.5, dpi=DPI_PREVIEW)
    save_rgb(hero, os.path.join(PREVIEWS, "unit_circle_preview_1_hero.jpg"), DPI_PREVIEW, 92)

    print("2/6 square listing…")
    sq = compose_square_listing(8.0, dpi=DPI_PREVIEW)
    save_rgb(sq, os.path.join(PREVIEWS, "unit_circle_preview_2_square.jpg"), DPI_PREVIEW, 92)
    # also root-level listing cover convenience
    save_rgb(sq, os.path.join(OUT, "unit_circle_cover.jpg"), DPI_PREVIEW, 92)

    print("3/6 detail 45°…")
    det = compose_detail_crop(dpi=DPI_PREVIEW)
    save_rgb(det, os.path.join(PREVIEWS, "unit_circle_preview_3_detail.jpg"), DPI_PREVIEW, 92)

    print("4/6 included…")
    inc = compose_included_card(dpi=DPI_PREVIEW)
    save_rgb(inc, os.path.join(PREVIEWS, "unit_circle_preview_4_included.jpg"), DPI_PREVIEW, 92)

    print("5/6 special-angle table…")
    tab = compose_table_card(dpi=DPI_PREVIEW)
    save_rgb(tab, os.path.join(PREVIEWS, "unit_circle_preview_5_table.jpg"), DPI_PREVIEW, 92)

    print("6/6 print sample A4 @ 200 dpi…")
    plate_a4 = compose_plate(8.27, 11.69, dpi=200)
    save_rgb(plate_a4, os.path.join(PRINTS, "unit_circle_A4_test_200dpi.jpg"), 200, 90)

    print("done test pack.")


def build_prints():
    os.makedirs(PRINTS, exist_ok=True)
    for name, (w, h) in SIZES.items():
        print(f"print {name} ({w}×{h} in @ {DPI_PRINT} dpi)…")
        img = compose_plate(w, h, dpi=DPI_PRINT)
        path = os.path.join(PRINTS, f"unit_circle_{name}_{DPI_PRINT}dpi.jpg")
        save_rgb(img, path, DPI_PRINT, quality=90)


def build_zip():
    zip_path = os.path.join(OUT, "Unit_Circle_Math_Wall_Art.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            """Unit Circle — Math Wall Art
MathRelaxing scientific plate

THE UNIT CIRCLE
Radians, degrees, and exact coordinates at special angles.
Key identities for trigonometry reference.

WHAT YOU GET
High-resolution JPG prints at 300 dpi, multiple aspect ratios:
  • 2:3  (12×18 in)
  • 3:4  (12×16 in)
  • 4:5  (16×20 in)
  • 5:7  (10×14 in)
  • ISO A4 and A3

Print at home, a print shop, or an online lab. Matte / textured paper looks best.
Frame not included. For personal use only.

© MathRelaxing
""",
        )
        for fn in sorted(os.listdir(PRINTS)):
            if fn.lower().endswith((".jpg", ".jpeg", ".png")) and "test" not in fn.lower():
                zf.write(os.path.join(PRINTS, fn), arcname=fn)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"ZIP: {zip_path}  ({size_mb:.1f} MB)")
    return zip_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true", help="Only listing previews")
    ap.add_argument("--full", action="store_true", help="Full multi-size 300dpi prints + zip")
    ap.add_argument("--no-latex", action="store_true")
    args = ap.parse_args()

    print("=== Unit Circle scientific plate (test) ===")
    os.makedirs(OUT, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    if args.full:
        build_prints()
        build_zip()
        build_test_images()
    elif args.preview_only:
        # lighter subset
        os.makedirs(PREVIEWS, exist_ok=True)
        print("square listing…")
        sq = compose_square_listing(8.0, dpi=DPI_PREVIEW)
        save_rgb(sq, os.path.join(PREVIEWS, "unit_circle_preview_2_square.jpg"), DPI_PREVIEW, 92)
        print("hero…")
        hero = compose_plate(10.0, 12.5, dpi=DPI_PREVIEW)
        save_rgb(hero, os.path.join(PREVIEWS, "unit_circle_preview_1_hero.jpg"), DPI_PREVIEW, 92)
    else:
        build_test_images()

    print("output dir:", OUT)


if __name__ == "__main__":
    main()
