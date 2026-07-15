"""
generate_schrodinger_equation.py — Schrödinger Equation scientific-plate wall art
=================================================================================
Scientific-plate style (Maxwell / Black Hole family):
  cream graph paper · serif titles · true LaTeX equations (MiKTeX) · elegant modes

Requires: matplotlib, numpy, pillow, and a working LaTeX (MiKTeX / TeX Live).

  python generate_schrodinger_equation.py
  python generate_schrodinger_equation.py --preview-only
  python generate_schrodinger_equation.py --no-latex   # mathtext fallback
"""
from __future__ import annotations

import argparse
import os
import shutil
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.gridspec import GridSpec
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "schrodinger_equation")
PRINTS = os.path.join(OUT, "prints")
PREVIEWS = os.path.join(OUT, "previews")

# Palette — match Maxwell / Black Hole plates
CREAM = "#F4F1EA"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#555555"
INK_FAINT = "#8A857C"
RUST = "#B85C38"
RUST_SOFT = "#C4785A"
RUST_FILL = "#B85C38"
LINE_DARK = "#222222"
WELL_BG = "#FBF9F4"

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

# Global: whether usetex is active for this run
_USE_LATEX = False


def configure_matplotlib(use_latex: bool = True) -> bool:
    """
    Prefer true LaTeX (Computer Modern) when a TeX engine is available.
    Falls back to matplotlib mathtext + STIX / DejaVu Serif.
    Returns True if usetex is on.
    """
    global _USE_LATEX
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
                    "axes.formatter.use_mathtext": True,
                    "text.latex.preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{bm}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{helvet}
""",
                    "pgf.texsystem": "pdflatex",
                }
            )
            # Probe LaTeX once (catches missing packages early)
            fig = plt.figure(figsize=(1, 1))
            fig.text(0.5, 0.5, r"$i\hbar$")
            fig.canvas.draw()
            plt.close(fig)
            _USE_LATEX = True
            print("  math rendering: LaTeX (usetex / Computer Modern)")
            return True
        except Exception as exc:
            print(f"  LaTeX probe failed ({exc}); falling back to mathtext")
            plt.rcParams["text.usetex"] = False

    plt.rcParams.update(
        {
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "DejaVu Serif", "Times New Roman", "Georgia"],
            "mathtext.fontset": "stix",  # closest to LaTeX without TeX
            "axes.unicode_minus": False,
        }
    )
    _USE_LATEX = False
    print("  math rendering: mathtext STIX (LaTeX-like, no TeX engine)")
    return False


def L(s: str) -> str:
    """
    Normalize math strings: with usetex leave as-is; without, keep $...$ mathtext.
    Pass full strings including non-math for plain text.
    """
    return s


def _draw_graph_paper(ax, xmin, xmax, ymin, ymax, major=5.0, minor=1.25):
    """Subtle engineering grid (major + faint minor)."""
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


def _psi(n: int, x: np.ndarray, L: float = 1.0) -> np.ndarray:
    return np.sqrt(2.0 / L) * np.sin(n * np.pi * x / L)


def _draw_mode_panel(ax_psi, ax_prob, n: int, label: str, sub: str, fig_w: float):
    """
    Elegant dual-axis panel (open plate, no card chrome):
      top  — wavefunction ψ_n(x) with zero line + infinite walls
      bottom — probability density |ψ|² as filled curve
    """
    Lbox = 1.0
    x = np.linspace(0, Lbox, 800)
    psi = _psi(n, x, Lbox)
    prob = psi ** 2

    psi_n = psi / np.max(np.abs(psi))
    prob_n = prob / np.max(prob)

    for a in (ax_psi, ax_prob):
        a.set_facecolor("none")  # open on cream graph paper
        a.patch.set_alpha(0.0)
        a.set_xlim(-0.06, 1.10)
        for spine in a.spines.values():
            spine.set_visible(False)
        a.set_xticks([])
        a.set_yticks([])
        a.tick_params(length=0)
        a.set_clip_on(False)

    ax_psi.set_ylim(-1.42, 1.42)

    # Infinite square-well walls (open style — walls only, no card frame)
    wall_kw = dict(color=LINE_DARK, lw=1.55, solid_capstyle="projecting", zorder=6)
    y_top, y_bot = 1.28, -1.28
    ax_psi.plot([0, 0], [y_bot, y_top], **wall_kw)
    ax_psi.plot([1, 1], [y_bot, y_top], **wall_kw)
    # small outward ticks at top of walls (infinite V → ∞ cue)
    tick = 0.045
    for xw in (0.0, 1.0):
        ax_psi.plot([xw - tick, xw + tick], [y_top, y_top], color=LINE_DARK, lw=1.55, zorder=6)

    # Zero line for ψ
    ax_psi.axhline(0, color=INK_FAINT, lw=0.65, ls=(0, (1.2, 2.0)), zorder=2, xmin=0.05, xmax=0.88)

    # ψ curve
    ax_psi.plot(
        x,
        psi_n,
        color=LINE_DARK,
        lw=2.15,
        solid_capstyle="round",
        solid_joinstyle="round",
        zorder=5,
        antialiased=True,
    )
    # node markers
    if n > 1:
        for k in range(1, n):
            xn = k / n
            ax_psi.plot(
                xn, 0, "o", color=RUST, ms=3.4, zorder=7,
                markeredgewidth=0, clip_on=False,
            )

    ax_psi.text(
        0.5,
        1.18,
        rf"$n = {n}$",
        transform=ax_psi.transAxes,
        ha="center",
        va="bottom",
        fontsize=_fs(fig_w, 0.014),
        color=INK,
        clip_on=False,
    )
    ax_psi.text(
        0.5,
        1.05,
        r"\textit{" + sub + "}",
        transform=ax_psi.transAxes,
        ha="center",
        va="bottom",
        fontsize=_fs(fig_w, 0.0095),
        color=INK_SOFT,
        clip_on=False,
    )
    ax_psi.text(
        1.02,
        0.88,
        r"$\psi$",
        transform=ax_psi.transAxes,
        ha="left",
        va="center",
        fontsize=_fs(fig_w, 0.012),
        color=LINE_DARK,
        clip_on=False,
    )

    # ── Probability density ─────────────────────────────────────────────────
    ax_prob.set_ylim(-0.08, 1.28)
    ax_prob.plot([0, 0], [0, 1.18], **wall_kw)
    ax_prob.plot([1, 1], [0, 1.18], **wall_kw)
    ax_prob.plot([0, 1], [0, 0], color=LINE_DARK, lw=1.15, zorder=6, solid_capstyle="butt")

    ax_prob.fill_between(
        x, 0, prob_n,
        color=RUST, alpha=0.20, linewidth=0, zorder=3, antialiased=True,
    )
    ax_prob.plot(
        x, prob_n,
        color=RUST, lw=1.65, solid_capstyle="round", zorder=4, antialiased=True,
    )
    ax_prob.text(
        1.02,
        0.78,
        r"$|\psi|^{2}$",
        transform=ax_prob.transAxes,
        ha="left",
        va="center",
        fontsize=_fs(fig_w, 0.0105),
        color=RUST,
        clip_on=False,
    )
    # Energy under each column (clear of center band label)
    ax_prob.text(
        0.5,
        -0.28,
        rf"$E_{{{n}}}\propto n^{{2}}$",
        transform=ax_prob.transAxes,
        ha="center",
        va="top",
        fontsize=_fs(fig_w, 0.011),
        color=RUST,
        clip_on=False,
    )


def compose_plate(width_in: float, height_in: float, dpi: int = DPI_PRINT) -> Image.Image:
    """
    Full scientific plate with nested axes for true curve quality + LaTeX math.
    Layout (figure fractions, top→bottom):
      header · rule · 3 mode columns (ψ + |ψ|²) · caption · key equations
    """
    fig_w, fig_h = width_in, height_in
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)

    # Background plate axes (grid + typography only)
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

    # ── Header (plate coordinates) ──────────────────────────────────────────
    # Bold Helvetica via LaTeX for Maxwell-like display title
    ax_bg.text(
        6.2,
        93.2,
        r"\textsf{\textbf{THE SHAPE OF PROBABILITY}}",
        fontsize=_fs(fig_w, 0.038),
        color=INK,
        va="center",
        ha="left",
        zorder=5,
    )
    ax_bg.text(
        93.8,
        93.2,
        r"\textsf{FIG.\ 1}",
        fontsize=_fs(fig_w, 0.015),
        color=INK_SOFT,
        va="center",
        ha="right",
        zorder=5,
    )

    # Subtitle — true LaTeX equation (Computer Modern)
    ax_bg.text(
        6.2,
        88.8,
        r"\textsf{SCHR\"ODINGER EQUATION}"
        r"  $\cdot$  "
        r"$i\hbar\,\dfrac{\partial\psi}{\partial t}=\hat{H}\psi$",
        fontsize=_fs(fig_w, 0.0135),
        color=RUST,
        va="center",
        ha="left",
        zorder=5,
    )
    ax_bg.plot([6.2, 93.8], [86.0, 86.0], color=INK, lw=0.85, solid_capstyle="butt", zorder=5)

    # ── Mode panels ─────────────────────────────────────────────────────────
    modes = [
        (1, "ground state"),
        (2, "first excited"),
        (3, "second excited"),
    ]
    left, right = 0.075, 0.925
    # Raise panels slightly; leave room under for energy + band label
    bottom_panels, top_panels = 0.34, 0.83
    width_total = right - left
    gap = 0.04
    col_w = (width_total - 2 * gap) / 3.0
    for i, (n, sub) in enumerate(modes):
        x0 = left + i * (col_w + gap)
        band = top_panels - bottom_panels
        h_psi = band * 0.56
        h_prob = band * 0.26
        gap_inner = band * 0.08
        y_prob = bottom_panels
        y_psi = bottom_panels + h_prob + gap_inner

        ax_psi = fig.add_axes([x0, y_psi, col_w, h_psi], zorder=3)
        ax_prob = fig.add_axes([x0, y_prob, col_w, h_prob], zorder=3)
        _draw_mode_panel(ax_psi, ax_prob, n, f"n={n}", sub, fig_w)

    # Band label — below energy labels so they don't collide
    ax_bg.text(
        50,
        27.8,
        r"\textit{particle in a one-dimensional box  $\cdot$  infinite square well}",
        fontsize=_fs(fig_w, 0.010),
        color=INK_SOFT,
        ha="center",
        va="center",
        zorder=5,
    )

    # ── Caption ─────────────────────────────────────────────────────────────
    caption_lines = [
        r"The Schr\"odinger equation says a particle is a wave of probability $\psi$.",
        r"Squaring it gives $|\psi|^{2}$ --- the chance of finding the particle at each place.",
        r"In a box the allowed waves are standing modes: higher $n$, more nodes, higher energy.",
    ]
    y_cap = 23.2
    for line in caption_lines:
        ax_bg.text(
            6.2,
            y_cap,
            line,
            fontsize=_fs(fig_w, 0.0112),
            color=INK_SOFT,
            ha="left",
            va="top",
            zorder=5,
        )
        y_cap -= 2.55

    # ── Key equations (footer) ──────────────────────────────────────────────
    ax_bg.text(
        6.2,
        11.0,
        r"$\hat{H}\psi = E\psi$",
        fontsize=_fs(fig_w, 0.016),
        color=INK_SOFT,
        ha="left",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        6.2,
        8.0,
        r"\textsf{stationary states}",
        fontsize=_fs(fig_w, 0.0088),
        color=INK_FAINT,
        ha="left",
        va="center",
        zorder=5,
    )

    ax_bg.text(
        50,
        11.0,
        r"$\displaystyle\psi_n(x)=\sqrt{\dfrac{2}{L}}\,"
        r"\sin\!\left(\dfrac{n\pi x}{L}\right)$",
        fontsize=_fs(fig_w, 0.0135),
        color=INK,
        ha="center",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        50,
        8.0,
        r"\textsf{eigenfunctions of the infinite well}",
        fontsize=_fs(fig_w, 0.0088),
        color=INK_FAINT,
        ha="center",
        va="center",
        zorder=5,
    )

    ax_bg.text(
        93.8,
        11.0,
        r"$i\hbar\,\dfrac{\partial\psi}{\partial t}=\hat{H}\psi$",
        fontsize=_fs(fig_w, 0.015),
        color=RUST,
        ha="right",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        93.8,
        8.0,
        r"\textsf{time-dependent form}",
        fontsize=_fs(fig_w, 0.0088),
        color=INK_FAINT,
        ha="right",
        va="center",
        zorder=5,
    )

    # Rasterize to RGB
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def compose_equation_card(width_in: float, height_in: float, dpi: int = DPI_PREVIEW) -> Image.Image:
    """Clean equation-only listing image with display LaTeX."""
    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, major=5.0, minor=1.25)

    ax.text(
        50,
        72,
        r"\textsf{\textbf{THE SCHR\"ODINGER EQUATION}}",
        fontsize=_fs(width_in, 0.026),
        color=INK,
        ha="center",
    )
    ax.text(
        50,
        54,
        r"$i\hbar\,\dfrac{\partial\psi}{\partial t} = \hat{H}\psi$",
        fontsize=_fs(width_in, 0.042),
        color=RUST,
        ha="center",
        va="center",
    )
    ax.text(
        50,
        38,
        r"\textsf{time-dependent form  $\cdot$  quantum mechanics}",
        fontsize=_fs(width_in, 0.013),
        color=INK_SOFT,
        ha="center",
    )
    ax.text(
        50,
        26,
        r"stationary states:\quad $\hat{H}\psi = E\psi$",
        fontsize=_fs(width_in, 0.018),
        color=INK_SOFT,
        ha="center",
    )
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


def build_prints():
    os.makedirs(PRINTS, exist_ok=True)
    for name, (w, h) in SIZES.items():
        print(f"print {name} ({w}×{h} in @ {DPI_PRINT} dpi)…")
        img = compose_plate(w, h, dpi=DPI_PRINT)
        path = os.path.join(PRINTS, f"schrodinger_equation_{name}_{DPI_PRINT}dpi.jpg")
        save_rgb(img, path, DPI_PRINT, quality=90)


def build_zip():
    zip_path = os.path.join(OUT, "Schrodinger_Equation_Physics_Wall_Art.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            """Schrödinger Equation — Physics Wall Art
MathRelaxing scientific plate

THE SHAPE OF PROBABILITY
Particle in a one-dimensional box (infinite square well):
wavefunctions ψ_n and probability densities |ψ|² for n = 1, 2, 3.
Equations rendered with LaTeX (Computer Modern).

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
            if fn.lower().endswith((".jpg", ".jpeg", ".png")):
                zf.write(os.path.join(PRINTS, fn), arcname=fn)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"ZIP: {zip_path}  ({size_mb:.1f} MB)")
    if size_mb > 19.5:
        print("WARNING: ZIP near Etsy 20MB digital-file limit.")
    return zip_path


def build_previews():
    os.makedirs(PREVIEWS, exist_ok=True)

    print("preview 1 hero…")
    hero = compose_plate(10.0, 12.5, dpi=DPI_PREVIEW)
    save_rgb(hero, os.path.join(PREVIEWS, "schrodinger_preview_1_hero.jpg"), DPI_PREVIEW, 92)

    print("preview 2 detail…")
    detail = compose_plate(14.0, 10.0, dpi=DPI_PREVIEW)
    dw, dh = detail.size
    # crop the three mode panels band
    crop = detail.crop((int(dw * 0.04), int(dh * 0.16), int(dw * 0.96), int(dh * 0.74)))
    side = max(crop.size)
    pad = Image.new("RGB", (side, int(side * 0.85)), (244, 241, 234))
    pad.paste(crop, ((pad.size[0] - crop.size[0]) // 2, (pad.size[1] - crop.size[1]) // 2))
    save_rgb(pad, os.path.join(PREVIEWS, "schrodinger_preview_2_detail.jpg"), DPI_PREVIEW, 92)

    print("preview 3 included…")
    # left plate + right included card
    fig = plt.figure(figsize=(10, 10), dpi=DPI_PREVIEW, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, major=5.0, minor=1.25)
    ax.text(55, 78, r"\textsf{\textbf{included}}", fontsize=24, color=INK, ha="left")
    lines = [
        r"1 scientific-plate print",
        r"Schr\"odinger equation",
        r"particle-in-a-box modes",
        r"",
        r"Aspect ratios:",
        r"2:3 $\cdot$ 3:4 $\cdot$ 4:5 $\cdot$ 5:7",
        r"ISO A4 $\cdot$ A3",
        r"",
        r"300 dpi JPG $\cdot$ ZIP",
        r"equations in \LaTeX{}",
        r"",
        r"Best on matte paper",
        r"Instant download",
    ]
    y = 68
    for line in lines:
        ax.text(55, y, line, fontsize=12.5, color=INK_SOFT, ha="left")
        y -= 4.0
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    base = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    mini = compose_plate(5.0, 7.0, dpi=DPI_PREVIEW)
    mini = mini.resize((int(base.size[0] * 0.44), int(base.size[1] * 0.70)), Image.Resampling.LANCZOS)
    base.paste(mini, (int(base.size[0] * 0.05), int(base.size[1] * 0.14)))
    save_rgb(base, os.path.join(PREVIEWS, "schrodinger_preview_3_included.jpg"), DPI_PREVIEW, 92)

    print("preview 4 plate…")
    plate = compose_plate(8.0, 10.0, dpi=DPI_PREVIEW)
    save_rgb(plate, os.path.join(PREVIEWS, "schrodinger_preview_4_plate.jpg"), DPI_PREVIEW, 92)

    print("preview 5 equation…")
    eq = compose_equation_card(10.0, 8.0, dpi=DPI_PREVIEW)
    save_rgb(eq, os.path.join(PREVIEWS, "schrodinger_preview_5_equation.jpg"), DPI_PREVIEW, 92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-latex", action="store_true", help="Force mathtext STIX fallback")
    args = ap.parse_args()

    print("=== Schrödinger Equation physics plate ===")
    os.makedirs(OUT, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    if not args.preview_only:
        build_prints()
        build_zip()
    build_previews()
    print("done.")


if __name__ == "__main__":
    main()
