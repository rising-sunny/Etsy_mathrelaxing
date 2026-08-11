"""
generate_equation_plates.py — Scientific-plate wall art series (6 singles + set)
================================================================================
Style family: Maxwell / Schrödinger / Unit Circle
  cream graph paper · serif + LaTeX · rust accent · multi-ratio 300 dpi

Designs:
  1. fourier_series   — Math Wall Art | Fourier Series
  2. wave_equation    — Physics Wall Art | Wave Equation
  3. dirac_equation   — Physics Wall Art | Dirac Equation
  4. navier_stokes    — Physics Wall Art | Navier–Stokes
  5. euler_identity   — Math Wall Art | Euler's Identity
  6. mandelbrot_set   — Math Wall Art | Mandelbrot Set

Also packs Famous Equations Set of 6 (bundle listing).

  python generate_equation_plates.py
  python generate_equation_plates.py --only fourier_series,euler_identity
  python generate_equation_plates.py --preview-only
  python generate_equation_plates.py --no-latex
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT_ROOT = BASE / "equation_plates"

# Palette — Maxwell / Schrödinger family
CREAM = "#F4F1EA"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#555555"
INK_FAINT = "#8A857C"
RUST = "#B85C38"
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

_USE_LATEX = False


# ── Shared infrastructure ─────────────────────────────────────────────────────

def configure_matplotlib(use_latex: bool = True) -> bool:
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
                    "text.latex.preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{bm}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{helvet}
""",
                }
            )
            fig = plt.figure(figsize=(1, 1))
            fig.text(0.5, 0.5, r"$e^{i\pi}$")
            fig.canvas.draw()
            plt.close(fig)
            _USE_LATEX = True
            print("  math rendering: LaTeX (Computer Modern)")
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
    _USE_LATEX = False
    print("  math rendering: mathtext STIX")
    return False


def SF(s: str) -> str:
    """Sans-serif display text (Helvetica via LaTeX, plain otherwise)."""
    if _USE_LATEX:
        # escape common specials for latex text mode
        t = (
            s.replace("\\", r"\textbackslash{}")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("–", "--")
            .replace("—", "---")
            .replace("'", r"\textquotesingle{}")
        )
        # allow manual latex fragments marked with « »
        return r"\textsf{" + t + "}"
    return s


def SFb(s: str) -> str:
    if _USE_LATEX:
        t = (
            s.replace("&", r"\&")
            .replace("%", r"\%")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("–", "--")
            .replace("—", "---")
        )
        return r"\textsf{\textbf{" + t + "}}"
    return s


def IT(s: str) -> str:
    if _USE_LATEX:
        return r"\textit{" + s + "}"
    return s


def _fs(fig_w_in: float, frac: float) -> float:
    return max(7.0, fig_w_in * 72 * frac)


def _draw_graph_paper(ax, xmin=0, xmax=100, ymin=0, ymax=100, major=5.0, minor=1.25):
    for x in np.arange(xmin, xmax + minor * 0.5, minor):
        ax.axvline(x, color=GRID_FINE, lw=0.35, zorder=0)
    for y in np.arange(ymin, ymax + minor * 0.5, minor):
        ax.axhline(y, color=GRID_FINE, lw=0.35, zorder=0)
    for x in np.arange(xmin, xmax + major * 0.5, major):
        ax.axvline(x, color=GRID, lw=0.55, zorder=0)
    for y in np.arange(ymin, ymax + major * 0.5, major):
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def _new_plate(width_in: float, height_in: float, dpi: int):
    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax)
    margin = 3.0
    ax.add_patch(
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
    return fig, ax


def _header(ax, title: str, fig_label: str, subtitle_left: str, subtitle_math: str, fig_w: float):
    ax.text(6.2, 93.2, SFb(title), fontsize=_fs(fig_w, 0.034), color=INK, va="center", ha="left", zorder=5)
    ax.text(93.8, 93.2, SF(fig_label), fontsize=_fs(fig_w, 0.014), color=INK_SOFT, va="center", ha="right", zorder=5)
    # subtitle: plain + math
    if _USE_LATEX:
        sub = SF(subtitle_left) + r"  $\cdot$  " + subtitle_math
    else:
        sub = f"{subtitle_left}  ·  {subtitle_math}"
    ax.text(6.2, 88.6, sub, fontsize=_fs(fig_w, 0.0125), color=RUST, va="center", ha="left", zorder=5)
    ax.plot([6.2, 93.8], [85.8, 85.8], color=INK, lw=0.85, solid_capstyle="butt", zorder=5)


def _caption(ax, lines: list[str], y0: float, fig_w: float):
    y = y0
    for line in lines:
        ax.text(6.2, y, line if _USE_LATEX else line.replace(r"\textit{", "").replace("}", "").replace(r"\cdot", "·"),
                fontsize=_fs(fig_w, 0.0108), color=INK_SOFT, ha="left", va="top", zorder=5)
        y -= 2.5


def _footer_eqs(ax, left, mid, right, fig_w: float, y_eq=11.0, y_lab=8.0):
    for x, ha, eq, lab in (
        (6.2, "left", left[0], left[1]),
        (50, "center", mid[0], mid[1]),
        (93.8, "right", right[0], right[1]),
    ):
        ax.text(x, y_eq, eq, fontsize=_fs(fig_w, 0.0135 if ha == "center" else 0.0145),
                color=INK if ha == "center" else (RUST if ha == "right" else INK_SOFT),
                ha=ha, va="center", zorder=5)
        ax.text(x, y_lab, SF(lab) if _USE_LATEX else lab,
                fontsize=_fs(fig_w, 0.0085), color=INK_FAINT, ha=ha, va="center", zorder=5)


def fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_rgb(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 90):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(
        str(path), "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path.name}  ({path.stat().st_size / 1024:.0f} KB)")


def _open_axes(fig, rect, fig_w):
    """Nested axes with no chrome — Schrödinger open-plate style."""
    a = fig.add_axes(rect, zorder=3)
    a.set_facecolor("none")
    a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])
    a.tick_params(length=0)
    a.set_clip_on(False)
    return a


def _square_wave_partial(x: np.ndarray, n_terms: int) -> np.ndarray:
    """Odd-harmonic square-wave partial sum on [-π, π]."""
    s = np.zeros_like(x)
    for k in range(n_terms):
        n_odd = 2 * k + 1
        s += np.sin(n_odd * x) / n_odd
    return (4.0 / np.pi) * s


# ── Design 1: Fourier Series ──────────────────────────────────────────────────

def compose_fourier(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax,
        "THE SHAPE OF WAVES",
        "FIG. 1",
        "FOURIER SERIES",
        r"$f(x)=\dfrac{a_0}{2}+\sum(a_n\cos nx+b_n\sin nx)$" if _USE_LATEX
        else r"$f(x)=\frac{a_0}{2}+\sum(a_n\cos nx+b_n\sin nx)$",
        fig_w,
    )

    terms_list = [1, 3, 7, 31]
    left, right = 0.07, 0.93
    bottom, top = 0.32, 0.83
    gap = 0.028
    n_panels = len(terms_list)
    col_w = (right - left - (n_panels - 1) * gap) / n_panels
    # dense sampling; avoid exact ±π for clean Gibbs
    x = np.linspace(-np.pi + 1e-4, np.pi - 1e-4, 2400)

    for i, N in enumerate(terms_list):
        x0 = left + i * (col_w + gap)
        a = _open_axes(fig, [x0, bottom, col_w, top - bottom], fig_w)
        a.set_xlim(-np.pi, np.pi)
        a.set_ylim(-1.45, 1.55)

        # target amplitude guides (±1 of ideal square wave)
        a.axhline(1.0, color=RUST, lw=0.7, ls=(0, (2.5, 2.2)), alpha=0.35, zorder=1)
        a.axhline(-1.0, color=RUST, lw=0.7, ls=(0, (2.5, 2.2)), alpha=0.35, zorder=1)

        s = _square_wave_partial(x, N)
        # soft lobe fill
        a.fill_between(x, 0, s, color=RUST, alpha=0.12, zorder=3, linewidth=0)
        a.plot(x, s, color=LINE_DARK, lw=2.05, solid_capstyle="round",
               solid_joinstyle="round", zorder=5, antialiased=True)
        a.axhline(0, color=INK_FAINT, lw=0.55, ls=(0, (1.2, 2.0)), zorder=2)

        a.text(0.5, 1.07, rf"$N={N}$", transform=a.transAxes, ha="center", va="bottom",
               fontsize=_fs(fig_w, 0.0135), color=INK, clip_on=False)
        labels = {1: "fundamental", 3: "3 harmonics", 7: "7 harmonics", 31: "near square"}
        a.text(0.5, -0.10, SF(labels.get(N, "partial sum")) if _USE_LATEX else labels.get(N, "partial sum"),
               transform=a.transAxes, ha="center", va="top",
               fontsize=_fs(fig_w, 0.009), color=INK_SOFT, clip_on=False)

    # y=26.8 put this strapline at the exact height of the per-panel labels
    # (panels bottom at 0.32 fig, labels -0.10 axes below -> ~26.9 data), so
    # it printed straight through "3 harmonics"/"7 harmonics". 24.8 drops it
    # into the clear band between those labels and the caption block (22.8).
    ax.text(
        50, 24.8,
        IT(r"odd harmonics build a square wave  $\cdot$  Gibbs ringing at the jump")
        if _USE_LATEX else "odd harmonics build a square wave  ·  Gibbs ringing at the jump",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", va="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Any periodic signal is a sum of pure sinusoids --- Fourier's great idea." if _USE_LATEX
            else "Any periodic signal is a sum of pure sinusoids — Fourier's great idea.",
            r"More terms sharpen the edges; the overshoot at jumps never fully vanishes (Gibbs).",
            r"Used in audio, imaging, quantum mechanics, and every digital filter.",
        ],
        22.8,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$b_n=\dfrac{4}{n\pi}$" if _USE_LATEX else r"$b_n=\frac{4}{n\pi}$", "odd harmonics"),
        (r"$f_N=\dfrac{4}{\pi}\sum_{k=0}^{N-1}\dfrac{\sin((2k+1)x)}{2k+1}$" if _USE_LATEX
         else r"$f_N=\frac{4}{\pi}\sum\frac{\sin((2k+1)x)}{2k+1}$", "square-wave series"),
        (r"$N\to\infty$", "convergence"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 2: Wave Equation ───────────────────────────────────────────────────

def compose_wave(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE TRAVELING WAVE", "FIG. 2", "WAVE EQUATION",
        r"$\dfrac{\partial^{2}u}{\partial t^{2}}=c^{2}\,\dfrac{\partial^{2}u}{\partial x^{2}}$" if _USE_LATEX
        else r"$\frac{\partial^2 u}{\partial t^2}=c^2\frac{\partial^2 u}{\partial x^2}$",
        fig_w,
    )

    modes = [(1, "fundamental"), (2, "second harmonic"), (3, "third harmonic")]
    left, right = 0.08, 0.92
    # dual band: upper standing wave, lower envelope energy cue
    gap = 0.045
    n = len(modes)
    col_w = (right - left - (n - 1) * gap) / n
    x = np.linspace(0, 1, 900)

    for i, (m, name) in enumerate(modes):
        x0 = left + i * (col_w + gap)
        # upper: displacement
        a = _open_axes(fig, [x0, 0.48, col_w, 0.34], fig_w)
        a.set_xlim(-0.06, 1.06)
        a.set_ylim(-1.45, 1.45)
        wall_kw = dict(color=LINE_DARK, lw=1.55, solid_capstyle="projecting", zorder=6)
        a.plot([0, 0], [-1.25, 1.25], **wall_kw)
        a.plot([1, 1], [-1.25, 1.25], **wall_kw)
        # cap ticks (fixed ends)
        for xw in (0.0, 1.0):
            a.plot([xw - 0.03, xw + 0.03], [1.25, 1.25], color=LINE_DARK, lw=1.55, zorder=6)
        a.axhline(0, color=INK_FAINT, lw=0.55, ls=(0, (1.5, 2)), zorder=1)
        env = np.sin(m * np.pi * x)
        a.fill_between(x, -np.abs(env), np.abs(env), color=RUST, alpha=0.12, zorder=2, lw=0)
        a.plot(x, env, color=LINE_DARK, lw=2.15, zorder=4, solid_capstyle="round", antialiased=True)
        a.plot(x, -env, color=RUST, lw=1.35, alpha=0.65, zorder=3, solid_capstyle="round")
        for k in range(1, m):
            a.plot(k / m, 0, "o", color=RUST, ms=4.0, zorder=7, markeredgewidth=0)
        a.text(0.5, 1.08, rf"$n={m}$", transform=a.transAxes, ha="center",
               fontsize=_fs(fig_w, 0.0135), color=INK, clip_on=False)
        a.text(1.04, 0.88, r"$u$", transform=a.transAxes, ha="left",
               fontsize=_fs(fig_w, 0.011), color=LINE_DARK, clip_on=False)

        # lower: time-averaged intensity ∝ envelope²
        b = _open_axes(fig, [x0, 0.30, col_w, 0.14], fig_w)
        b.set_xlim(-0.06, 1.06)
        b.set_ylim(-0.08, 1.25)
        inten = env ** 2
        b.plot([0, 0], [0, 1.15], **wall_kw)
        b.plot([1, 1], [0, 1.15], **wall_kw)
        b.plot([0, 1], [0, 0], color=LINE_DARK, lw=1.1, zorder=6)
        b.fill_between(x, 0, inten, color=RUST, alpha=0.22, zorder=3, lw=0)
        b.plot(x, inten, color=RUST, lw=1.7, zorder=4, solid_capstyle="round")
        b.text(1.04, 0.75, r"$\langle u^{2}\rangle$" if _USE_LATEX else r"$\langle u^2\rangle$",
               transform=b.transAxes, ha="left", fontsize=_fs(fig_w, 0.010), color=RUST, clip_on=False)
        b.text(0.5, -0.38, SF(name) if _USE_LATEX else name, transform=b.transAxes,
               ha="center", fontsize=_fs(fig_w, 0.0095), color=INK_SOFT, clip_on=False)

    ax.text(
        50, 25.5,
        IT(r"standing waves on a fixed string  $\cdot$  nodes and antinodes")
        if _USE_LATEX else "standing waves on a fixed string  ·  nodes and antinodes",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"The wave equation links acceleration in time to curvature in space.",
            r"On a string fixed at both ends, only discrete modes fit --- the harmonics of music.",
            r"Same mathematics: light, sound, quantum wells, and vibrating plates.",
        ],
        21.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$u(0,t)=u(L,t)=0$", "boundary conditions"),
        (r"$u_n=\sin\!\left(\dfrac{n\pi x}{L}\right)\cos(\omega_n t)$" if _USE_LATEX
         else r"$u_n=\sin(\frac{n\pi x}{L})\cos(\omega_n t)$", "standing-wave solutions"),
        (r"$\omega_n=n\pi c/L$", "dispersion"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 3: Dirac Equation ──────────────────────────────────────────────────

def compose_dirac(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "MATTER AND ANTIMATTER", "FIG. 3", "DIRAC EQUATION",
        r"$(i\gamma^{\mu}\partial_{\mu}-m)\psi=0$" if _USE_LATEX
        else r"$(i\gamma^\mu\partial_\mu - m)\psi=0$",
        fig_w,
    )

    a = fig.add_axes([0.14, 0.33, 0.72, 0.48], zorder=3)
    a.set_facecolor("none")
    a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])
    a.set_xlim(-3.4, 3.4)
    a.set_ylim(-3.7, 3.7)

    # custom axes cross
    a.axhline(0, color=INK_FAINT, lw=0.85, zorder=1)
    a.axvline(0, color=INK_FAINT, lw=0.85, zorder=1)
    # axis tips
    a.annotate("", xy=(3.35, 0), xytext=(3.0, 0),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.9), zorder=2)
    a.annotate("", xy=(0, 3.55), xytext=(0, 3.2),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.9), zorder=2)
    a.text(3.2, -0.35, r"$p$", color=INK_SOFT, fontsize=_fs(fig_w, 0.012), ha="center")
    a.text(0.2, 3.45, r"$E$", color=INK_SOFT, fontsize=_fs(fig_w, 0.012), ha="left")

    p = np.linspace(-3.2, 3.2, 800)
    mass = 1.0
    E = np.sqrt(p ** 2 + mass ** 2)
    # mass-gap band
    a.fill_between(p, -mass, mass, color=RUST, alpha=0.10, zorder=0, lw=0)
    a.plot(p, np.full_like(p, mass), color=RUST, lw=0.85, ls=(0, (2.5, 2.0)), zorder=2, alpha=0.7)
    a.plot(p, np.full_like(p, -mass), color=RUST, lw=0.85, ls=(0, (2.5, 2.0)), zorder=2, alpha=0.7)
    # continua
    a.plot(p, E, color=LINE_DARK, lw=2.35, solid_capstyle="round", zorder=4, antialiased=True)
    a.plot(p, -E, color=RUST, lw=2.35, solid_capstyle="round", zorder=4, antialiased=True)
    # rest-mass points
    a.plot(0, mass, "o", color=LINE_DARK, ms=5.5, zorder=6, markeredgewidth=0)
    a.plot(0, -mass, "o", color=RUST, ms=5.5, zorder=6, markeredgewidth=0)
    a.text(0.35, mass + 0.28, r"$+mc^{2}$" if _USE_LATEX else r"$+mc^2$",
           color=LINE_DARK, fontsize=_fs(fig_w, 0.012))
    a.text(0.35, -mass - 0.45, r"$-mc^{2}$" if _USE_LATEX else r"$-mc^2$",
           color=RUST, fontsize=_fs(fig_w, 0.012))
    a.text(2.55, 2.55, SF("particles") if _USE_LATEX else "particles",
           color=LINE_DARK, fontsize=_fs(fig_w, 0.011), ha="center")
    a.text(2.55, -2.55, SF("antiparticles") if _USE_LATEX else "antiparticles",
           color=RUST, fontsize=_fs(fig_w, 0.011), ha="center")
    a.text(-3.1, 0.25, SF("mass gap") if _USE_LATEX else "mass gap",
           color=RUST, fontsize=_fs(fig_w, 0.010), ha="left", va="bottom", alpha=0.9)

    ax.text(
        50, 27.0,
        IT(r"Dirac sea  $\cdot$  positive \& negative energy continua  $\cdot$  mass gap $2mc^{2}$")
        if _USE_LATEX else "Dirac sea  ·  positive & negative energy continua  ·  mass gap 2mc²",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Dirac united special relativity with quantum mechanics for the electron.",
            r"Negative-energy solutions predicted antimatter --- later found as the positron.",
            r"The same algebra gives spin-$\tfrac{1}{2}$ as a geometric necessity.",
        ] if _USE_LATEX else [
            "Dirac united special relativity with quantum mechanics for the electron.",
            "Negative-energy solutions predicted antimatter — later found as the positron.",
            "The same algebra gives spin-1/2 as a geometric necessity.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$E=\pm\sqrt{p^{2}c^{2}+m^{2}c^{4}}$" if _USE_LATEX else r"$E=\pm\sqrt{p^2c^2+m^2c^4}$", "dispersion"),
        (r"$(i\hbar\gamma^{\mu}\partial_{\mu}-mc)\psi=0$" if _USE_LATEX else r"$(i\hbar\gamma^\mu\partial_\mu-mc)\psi=0$", "covariant form"),
        (r"$e^{+},\;e^{-}$", "pair creation"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 4: Navier–Stokes ───────────────────────────────────────────────────

def compose_navier(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE EQUATIONS OF FLOW", "FIG. 4", "NAVIER--STOKES" if _USE_LATEX else "NAVIER-STOKES",
        r"$\rho(\partial_t\mathbf{u}+\mathbf{u}\cdot\nabla\mathbf{u})=-\nabla p+\mu\nabla^{2}\mathbf{u}+\mathbf{f}$"
        if _USE_LATEX else r"$\rho(\partial_t u+u\cdot\nabla u)=-\nabla p+\mu\nabla^2 u+f$",
        fig_w,
    )

    a = fig.add_axes([0.09, 0.30, 0.82, 0.50], zorder=3)
    a.set_facecolor("none")
    a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])
    a.set_aspect("equal")

    # Potential flow past a cylinder: high-res stream function + streamplot
    U_inf, R = 1.0, 0.72
    ny, nx = 320, 480
    Y, X = np.mgrid[-2.05:2.05:ny * 1j, -3.1:3.1:nx * 1j]
    r2 = np.maximum(X ** 2 + Y ** 2, 1e-12)
    r = np.sqrt(r2)
    # velocity from dipole + freestream (outside cylinder)
    # u = U(1 - R²/r² cos 2θ) = U(1 - R²(x²-y²)/r⁴)
    # v = -U R²/r² sin 2θ = -2 U R² xy / r⁴
    u = U_inf * (1.0 - (R ** 2) * (X ** 2 - Y ** 2) / (r2 ** 2))
    v = U_inf * (-2.0 * (R ** 2) * X * Y / (r2 ** 2))
    inside = r2 < (R * 1.02) ** 2
    u = np.where(inside, np.nan, u)
    v = np.where(inside, np.nan, v)

    # speed wash (cream → soft clay) via custom colormap
    from matplotlib.colors import LinearSegmentedColormap
    speed = np.sqrt(np.nan_to_num(u) ** 2 + np.nan_to_num(v) ** 2)
    speed = np.ma.array(speed, mask=inside)
    flow_cmap = LinearSegmentedColormap.from_list(
        "flow", ["#F4F1EA", "#EDE6DC", "#E0D2C4", "#D2B9A4", "#C49A7A"]
    )
    a.contourf(X, Y, speed, levels=16, cmap=flow_cmap, zorder=1, antialiased=True)

    # streamlines via streamplot (specialized matplotlib fluid viz)
    # seed density tuned for plate clarity
    strm = a.streamplot(
        X, Y, u, v,
        color=LINE_DARK,
        linewidth=1.05,
        density=1.35,
        arrowsize=0.7,
        arrowstyle="->",
        minlength=0.12,
        maxlength=6.0,
        zorder=3,
    )
    # streamline collection styling
    try:
        strm.lines.set_alpha(0.92)
        strm.arrows.set_alpha(0.85)
        strm.arrows.set_color(LINE_DARK)
    except Exception:
        pass

    # cylinder body
    circ = Circle((0, 0), R, facecolor=CREAM, edgecolor=RUST, lw=2.15, zorder=5)
    a.add_patch(circ)
    # stagnation points
    for sx in (-R, R):
        a.plot(sx, 0, "o", color=RUST, ms=4.0, zorder=7, markeredgewidth=0)

    # freestream direction cue
    for yb in (-1.55, 1.55):
        a.annotate(
            "",
            xy=(2.75, yb),
            xytext=(2.15, yb),
            arrowprops=dict(arrowstyle="->", color=RUST, lw=1.35),
            zorder=6,
        )
    a.set_xlim(-3.1, 3.1)
    a.set_ylim(-2.05, 2.05)
    a.text(
        0.5, 1.045,
        SF("potential flow past a cylinder  ·  streamlines and speed wash") if _USE_LATEX
        else "potential flow past a cylinder  ·  streamlines and speed wash",
        transform=a.transAxes, ha="center", color=INK_SOFT,
        fontsize=_fs(fig_w, 0.010), clip_on=False,
    )

    ax.text(
        50, 26.5,
        IT(r"incompressible continuum mechanics  $\cdot$  Millennium Prize problem in 3D")
        if _USE_LATEX else "incompressible continuum mechanics  ·  Millennium Prize problem in 3D",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Navier--Stokes describe how velocity and pressure evolve in a viscous fluid." if _USE_LATEX
            else "Navier-Stokes describe how velocity and pressure evolve in a viscous fluid.",
            r"From airplane wings to blood flow --- and still unsolved in full mathematical generality.",
            r"Ideal streamlines shown; viscosity adds boundary layers, separation, and drag.",
        ],
        22.2,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$\nabla\cdot\mathbf{u}=0$", "incompressibility"),
        (r"$\mathrm{Re}=\dfrac{\rho U L}{\mu}$" if _USE_LATEX else r"$\mathrm{Re}=\rho UL/\mu$", "Reynolds number"),
        (r"$\partial_t\mathbf{u}+\cdots$", "momentum balance"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 5: Euler's Identity ────────────────────────────────────────────────

def compose_euler(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE MOST BEAUTIFUL EQUATION", "FIG. 5", "EULER'S IDENTITY",
        r"$e^{i\pi}+1=0$",
        fig_w,
    )

    a = fig.add_axes([0.16, 0.30, 0.68, 0.52], zorder=3)
    a.set_facecolor("none")
    a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])
    a.set_aspect("equal")
    a.set_xlim(-1.65, 1.65)
    a.set_ylim(-1.45, 1.55)

    # axes
    a.axhline(0, color=INK_FAINT, lw=0.85, zorder=1)
    a.axvline(0, color=INK_FAINT, lw=0.85, zorder=1)
    a.annotate("", xy=(1.55, 0), xytext=(1.35, 0),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.9), zorder=2)
    a.annotate("", xy=(0, 1.45), xytext=(0, 1.25),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.9), zorder=2)
    a.text(1.48, -0.22, r"$\mathrm{Re}$", color=INK_SOFT, fontsize=_fs(fig_w, 0.011))
    a.text(0.12, 1.38, r"$\mathrm{Im}$", color=INK_SOFT, fontsize=_fs(fig_w, 0.011))

    # unit circle
    th = np.linspace(0, 2 * np.pi, 600)
    a.plot(np.cos(th), np.sin(th), color=LINE_DARK, lw=1.9, zorder=3, solid_capstyle="round")

    # filled wedge 0 → π (upper semicircle highlight)
    th2 = np.linspace(0, np.pi, 240)
    wedge_x = np.concatenate([[0], np.cos(th2), [0]])
    wedge_y = np.concatenate([[0], np.sin(th2), [0]])
    a.fill(wedge_x, wedge_y, color=RUST, alpha=0.08, zorder=2)
    a.plot(np.cos(th2), np.sin(th2), color=RUST, lw=2.7, zorder=4, solid_capstyle="round")

    # sample rays
    for ang, lab, col in [
        (np.pi / 2, r"$i$", LINE_DARK),
        (np.pi / 3, r"$e^{i\pi/3}$", LINE_DARK),
        (np.pi, r"$e^{i\pi}=-1$", RUST),
    ]:
        a.plot([0, np.cos(ang)], [0, np.sin(ang)], color=col, lw=1.35, zorder=5)
        a.plot(np.cos(ang), np.sin(ang), "o", color=RUST if ang == np.pi else LINE_DARK,
               ms=5.2, zorder=6, markeredgewidth=0)
        rx, ry = np.cos(ang) * 1.22, np.sin(ang) * 1.22
        if ang == np.pi:
            rx, ry = -1.38, 0.18
        a.text(rx, ry, lab, color=col, fontsize=_fs(fig_w, 0.012), ha="center", va="center")

    # unit labels
    a.text(1.12, -0.22, r"$1$", color=INK_SOFT, fontsize=_fs(fig_w, 0.012))
    a.text(-1.28, -0.22, r"$-1$", color=INK_SOFT, fontsize=_fs(fig_w, 0.012))
    a.text(0.12, 1.12, r"$i$", color=INK_SOFT, fontsize=_fs(fig_w, 0.012))
    a.text(0.42, 0.42, r"$|z|=1$", color=INK_SOFT, fontsize=_fs(fig_w, 0.011))
    # angle mark
    a.text(0.28, 0.12, r"$\pi$", color=RUST, fontsize=_fs(fig_w, 0.013), ha="center")

    ax.text(
        50, 26.0,
        IT(r"unit circle in the complex plane  $\cdot$  rotation is multiplication by $e^{i\theta}$")
        if _USE_LATEX else "unit circle in the complex plane  ·  rotation is multiplication by e^{iθ}",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Euler's formula $e^{i\theta}=\cos\theta+i\sin\theta$ links exp, trig, and geometry." if _USE_LATEX
            else "Euler's formula e^{iθ}=cosθ+i sinθ links exp, trig, and geometry.",
            r"At $\theta=\pi$: five fundamental constants meet in one identity." if _USE_LATEX
            else "At θ=π: five fundamental constants meet in one identity.",
            r"$0,\;1,\;e,\;i,\;\pi$ --- arithmetic, algebra, analysis, geometry." if _USE_LATEX
            else "0, 1, e, i, π — arithmetic, algebra, analysis, geometry.",
        ],
        21.8,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$e^{i\theta}=\cos\theta+i\sin\theta$", "Euler's formula"),
        (r"$e^{i\pi}+1=0$", "the identity"),
        (r"$i^{2}=-1$", "imaginary unit"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 6: Mandelbrot Set ──────────────────────────────────────────────────

def _mandelbrot_smooth(xmin, xmax, ymin, ymax, width, height, max_iter=160):
    """
    Continuous-potential Mandelbrot (smooth escape-time).
    Uses vectorized numpy; fractional iteration removes blocky bands.
    """
    xs = np.linspace(xmin, xmax, width, dtype=np.float64)
    ys = np.linspace(ymin, ymax, height, dtype=np.float64)
    X, Y = np.meshgrid(xs, ys)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    # escape iteration index (float for smooth coloring)
    escape = np.zeros(C.shape, dtype=np.float64)
    active = np.ones(C.shape, dtype=bool)
    for n in range(max_iter):
        Z[active] = Z[active] ** 2 + C[active]
        escaped_now = active & (np.abs(Z) > 2.0)
        if np.any(escaped_now):
            # continuous iteration count (Renormalized)
            z_esc = Z[escaped_now]
            # nu = n + 1 - log2(log|z|)
            with np.errstate(divide="ignore", invalid="ignore"):
                log_mod = np.log(np.maximum(np.abs(z_esc), 1e-16))
                nu = n + 1.0 - np.log(log_mod) / np.log(2.0)
            escape[escaped_now] = np.clip(nu, 0, max_iter)
            active[escaped_now] = False
        if not np.any(active):
            break
    # remaining active → interior
    escape[active] = max_iter
    return escape, max_iter


def compose_mandelbrot(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE GEOMETRY OF CHAOS", "FIG. 6", "MANDELBROT SET",
        r"$z_{n+1}=z_n^{2}+c$" if _USE_LATEX else r"$z_{n+1}=z_n^2+c$",
        fig_w,
    )

    a = fig.add_axes([0.11, 0.30, 0.78, 0.50], zorder=3)
    a.set_facecolor(CREAM)
    for sp in a.spines.values():
        sp.set_color(INK_FAINT)
        sp.set_linewidth(0.85)
    a.set_xticks([])
    a.set_yticks([])

    # higher res for print; continuous coloring
    px = 900 if dpi >= 200 else 560
    py = int(px * 1.15 / 2.0)  # match aspect of window
    # classic view
    xmin, xmax = -2.20, 0.80
    ymin, ymax = -1.20, 1.20
    py = int(px * (ymax - ymin) / (xmax - xmin))
    escape, max_iter = _mandelbrot_smooth(xmin, xmax, ymin, ymax, px, py, max_iter=140)

    # scientific cream / ink / rust palette
    rgb = np.zeros((*escape.shape, 3), dtype=np.float64)
    inside = escape >= (max_iter - 0.5)
    outside = ~inside
    rgb[inside] = (0.10, 0.10, 0.11)

    # exterior: map smooth escape → cream body + rust near boundary
    t = np.zeros_like(escape)
    t[outside] = np.clip(escape[outside] / float(max_iter), 0.0, 1.0)
    # base cream → soft stone
    rgb[outside, 0] = 0.957 - 0.22 * t[outside]
    rgb[outside, 1] = 0.945 - 0.28 * t[outside]
    rgb[outside, 2] = 0.918 - 0.25 * t[outside]
    # rust filaments: high iteration near boundary
    near = outside & (escape > 8)
    te = np.clip((escape[near] - 8.0) / max(1.0, (max_iter - 8.0)), 0, 1)
    w = te ** 0.55
    rgb[near, 0] = (1 - w) * rgb[near, 0] + w * 0.72
    rgb[near, 1] = (1 - w) * rgb[near, 1] + w * 0.36
    rgb[near, 2] = (1 - w) * rgb[near, 2] + w * 0.22

    a.imshow(
        np.clip(rgb, 0, 1),
        extent=[xmin, xmax, ymin, ymax],
        origin="lower",
        interpolation="bicubic",
        zorder=2,
        aspect="equal",
    )
    a.set_xlim(xmin, xmax)
    a.set_ylim(ymin, ymax)
    a.text(
        0.02, 0.96,
        r"$c\in\mathbb{C}$" if _USE_LATEX else r"$c \in \mathbb{C}$",
        transform=a.transAxes, color=CREAM, fontsize=_fs(fig_w, 0.011), va="top",
        bbox=dict(boxstyle="round,pad=0.28", fc=INK, ec="none", alpha=0.62),
    )

    ax.text(
        50, 26.5,
        IT(r"smooth escape-time portrait  $\cdot$  connectedness locus of quadratic maps")
        if _USE_LATEX else "smooth escape-time portrait  ·  connectedness locus of quadratic maps",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Iterate $z\mapsto z^{2}+c$ from $z=0$. If the orbit stays bounded, $c$ is in the set." if _USE_LATEX
            else "Iterate z→z²+c from z=0. If the orbit stays bounded, c is in the set.",
            r"Simple rule, infinite coastline --- a cornerstone of complex dynamics.",
            r"Boundary points encode chaotic Julia sets; the cardioid holds period-1 bulbs.",
        ],
        22.2,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$z_0=0$", "critical orbit"),
        (r"$z_{n+1}=z_n^{2}+c$" if _USE_LATEX else r"$z_{n+1}=z_n^2+c$", "quadratic map"),
        (r"$|z|\le 2$", "escape radius"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Catalog of designs ────────────────────────────────────────────────────────

# ── Design 7: Normal Distribution ─────────────────────────────────────────────

def compose_gaussian(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE BELL CURVE", "FIG. 7", "NORMAL DISTRIBUTION",
        r"$f(x)=\dfrac{1}{\sigma\sqrt{2\pi}}\,e^{-(x-\mu)^2/2\sigma^2}$",
        fig_w,
    )

    a = fig.add_axes([0.12, 0.35, 0.76, 0.45], zorder=3)
    a.set_facecolor("none")
    a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])
    a.set_xlim(-4.2, 4.2)
    a.set_ylim(-0.055, 0.45)

    x = np.linspace(-4, 4, 900)
    peak = 1.0 / np.sqrt(2 * np.pi)
    y = peak * np.exp(-x ** 2 / 2)

    # nested shaded bands (cumulative alpha -> darker center)
    for lo, hi, al in ((-3, 3, 0.05), (-2, 2, 0.08), (-1, 1, 0.16)):
        m = (x >= lo) & (x <= hi)
        a.fill_between(x[m], 0, y[m], color=RUST, alpha=al, lw=0, zorder=2)

    # baseline + curve
    a.axhline(0, color=INK_FAINT, lw=0.85, zorder=1)
    a.plot(x, y, color=LINE_DARK, lw=2.2, zorder=4, solid_capstyle="round")

    # sigma verticals + axis labels
    labels = {-3: r"$\mu\!-\!3\sigma$", -2: r"$\mu\!-\!2\sigma$", -1: r"$\mu\!-\!\sigma$",
              0: r"$\mu$", 1: r"$\mu\!+\!\sigma$", 2: r"$\mu\!+\!2\sigma$", 3: r"$\mu\!+\!3\sigma$"}
    for k, lab in labels.items():
        yk = peak * np.exp(-k ** 2 / 2)
        a.plot([k, k], [0, yk], color=(INK_SOFT if k == 0 else INK_FAINT),
               lw=(1.0 if k == 0 else 0.8), ls=("-" if k == 0 else (0, (2, 2))), zorder=3)
        a.text(k, -0.028, lab, ha="center", va="top",
               fontsize=_fs(fig_w, 0.0105), color=INK_SOFT)

    # peak label
    a.text(0.13, peak * 1.02, r"$\dfrac{1}{\sigma\sqrt{2\pi}}$",
           ha="left", va="bottom", fontsize=_fs(fig_w, 0.011), color=INK_SOFT)

    # per-band percentages (the classic diagram)
    band_pct = [(-0.5, r"$34.1\%$", 0.075, RUST), (0.5, r"$34.1\%$", 0.075, RUST),
                (-1.5, r"$13.6\%$", 0.032, INK_SOFT), (1.5, r"$13.6\%$", 0.032, INK_SOFT),
                (-2.5, r"$2.1\%$", 0.013, INK_SOFT), (2.5, r"$2.1\%$", 0.013, INK_SOFT)]
    for cx, pct, yy, col in band_pct:
        a.text(cx, yy, pct, ha="center", va="bottom", fontsize=_fs(fig_w, 0.0095), color=col)

    ax.text(
        50, 27.0,
        IT(r"the 68--95--99.7 rule  $\cdot$  area under the curve is probability")
        if _USE_LATEX else "the 68–95–99.7 rule  ·  area under the curve is probability",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"The Gaussian peaks at the mean $\mu$; its width is set by $\sigma$." if _USE_LATEX
            else "The Gaussian peaks at the mean μ; its width is set by σ.",
            r"$\approx\!68\%$ of values fall within $\pm\sigma$, $95\%$ within $\pm2\sigma$, $99.7\%$ within $\pm3\sigma$." if _USE_LATEX
            else "≈68% of values fall within ±σ, 95% within ±2σ, 99.7% within ±3σ.",
            r"The Central Limit Theorem makes it nature's default distribution." if _USE_LATEX
            else "The Central Limit Theorem makes it nature's default distribution.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$X\sim\mathcal{N}(\mu,\sigma^{2})$", "normal distribution"),
        (r"$\int_{-\infty}^{\infty}\!f(x)\,dx=1$", "total probability"),
        ("68 – 95 – 99.7", "empirical rule"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 8: Koch Snowflake ───────────────────────────────────────────────────

def _koch_snowflake(order: int):
    """Closed polygon (complex points) for a Koch snowflake at a given order."""
    p1, p2, p3 = 0j, 1 + 0j, 0.5 + 1j * np.sqrt(3) / 2
    pts = [p1, p2, p3, p1]
    for _ in range(order):
        new_pts = [pts[0]]
        for i in range(len(pts) - 1):
            a0, a1 = pts[i], pts[i + 1]
            s = (a1 - a0) / 3
            a = a0 + s
            b = a0 + 2 * s
            peak = a + s * np.exp(1j * np.pi / 3)
            new_pts += [a, peak, b, a1]
        pts = new_pts
    arr = np.array(pts)
    return arr.real, arr.imag


def compose_koch(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "THE INFINITE COASTLINE", "FIG. 8", "KOCH SNOWFLAKE",
        r"$N_n=3\cdot4^{\,n}$",
        fig_w,
    )

    orders = [0, 1, 2, 3]
    labels = {0: "n = 0", 1: "n = 1", 2: "n = 2", 3: "n = 3"}
    captions = {0: "the triangle", 1: "first bump", 2: "taking shape", 3: "the snowflake"}
    left, right = 0.08, 0.92
    band_bottom, band_top = 0.32, 0.83
    gap_h, gap_v = 0.03, 0.11
    col_w = (right - left - gap_h) / 2
    row_h = (band_top - band_bottom - gap_v) / 2

    # snowflake data spans ~1.16 x 1.12 (roughly square) -- size each panel's
    # box to the tighter of the two available dimensions so "equal" aspect
    # fills it with minimal dead space, then centre the 2x2 block.
    data_w, data_h = 1.16, 1.12
    side_in = min(col_w * width_in, row_h * height_in * (data_w / data_h))
    panel_w = side_in / width_in
    panel_h = side_in * (data_h / data_w) / height_in
    block_w = 2 * panel_w + gap_h
    block_h = 2 * panel_h + gap_v
    x_start = left + ((right - left) - block_w) / 2
    y_start = band_bottom + (band_top - band_bottom - block_h) / 2

    for i, n in enumerate(orders):
        r, c = divmod(i, 2)
        x0 = x_start + c * (panel_w + gap_h)
        y0 = y_start + (1 - r) * (panel_h + gap_v)
        a = _open_axes(fig, [x0, y0, panel_w, panel_h], fig_w)
        xs, ys = _koch_snowflake(n)
        a.set_aspect("equal")
        a.set_xlim(-0.08, 1.08)
        a.set_ylim(-0.10, 1.02)
        a.fill(xs, ys, color=RUST, alpha=0.12, zorder=2, linewidth=0)
        a.plot(xs, ys, color=LINE_DARK, lw=2.0, solid_capstyle="round",
               solid_joinstyle="round", zorder=4, antialiased=True)

        a.text(0.5, 1.06, labels[n], transform=a.transAxes, ha="center", va="bottom",
               fontsize=_fs(fig_w, 0.0145), color=INK, clip_on=False)
        a.text(0.5, -0.10, SF(captions[n]) if _USE_LATEX else captions[n],
               transform=a.transAxes, ha="center", va="top",
               fontsize=_fs(fig_w, 0.0095), color=INK_SOFT, clip_on=False)

    ax.text(
        50, 26.8,
        IT(r"each side splits into four, each a third the length  $\cdot$  self-similar forever")
        if _USE_LATEX else "each side splits into four, each a third the length  ·  self-similar forever",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", va="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Devised by Helge von Koch in 1904 --- one of the first fractal curves ever drawn." if _USE_LATEX
            else "Devised by Helge von Koch in 1904 — one of the first fractal curves ever drawn.",
            r"The perimeter grows without bound, yet it encloses a finite area." if _USE_LATEX
            else "The perimeter grows without bound, yet it encloses a finite area.",
            r"A continuous curve that is nowhere smooth --- Mandelbrot's model for a coastline." if _USE_LATEX
            else "A continuous curve that is nowhere smooth — Mandelbrot's model for a coastline.",
        ],
        22.8,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$P_n=3s\!\left(\dfrac{4}{3}\right)^{\!n}\!\to\infty$" if _USE_LATEX
         else r"$P_n=3s(4/3)^n\to\infty$", "perimeter diverges"),
        (r"$A_\infty=\dfrac{2\sqrt{3}}{5}\,s^{2}$" if _USE_LATEX
         else r"$A_\infty=\frac{2\sqrt{3}}{5}s^2$", "area stays finite"),
        (r"$D=\dfrac{\ln 4}{\ln 3}\approx1.26$" if _USE_LATEX
         else r"$D=\ln4/\ln3\approx1.26$", "fractal dimension"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 9: Möbius Strip ─────────────────────────────────────────────────────

_MOBIUS_RENDER_SCRIPT = BASE / "attractor_prints" / "generate_mobius_render.py"
_MOBIUS_RENDER_CACHE = OUT_ROOT / "mobius_strip" / "_pv_render.png"


def _mobius_render_image() -> Image.Image:
    """Real 3D Phong/PBR-shaded render (pyvista/VTK, off-screen via xvfb-run):
    smooth per-vertex shading, specular gloss, and a glossy gold tube tracing
    the strip's single boundary edge. Rendered once and cached -- rebuilding
    the plate at any size just reloads the same PNG."""
    if not _MOBIUS_RENDER_CACHE.exists():
        _MOBIUS_RENDER_CACHE.parent.mkdir(parents=True, exist_ok=True)
        print("  rendering Mobius strip via pyvista (xvfb-run, one-time)...")
        subprocess.run(
            ["xvfb-run", "-a", "python3", str(_MOBIUS_RENDER_SCRIPT),
             str(_MOBIUS_RENDER_CACHE), "4200", "3400"],
            check=True,
        )
    return Image.open(_MOBIUS_RENDER_CACHE).convert("RGBA")


def compose_mobius(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "ONE SURFACE, ONE EDGE", "FIG. 9", "MOBIUS STRIP" if not _USE_LATEX else "M\\\"OBIUS STRIP",
        r"$u\to u+2\pi\ \Rightarrow\ v\to-v$",
        fig_w,
    )

    a = fig.add_axes([0.10, 0.30, 0.80, 0.53], zorder=3)
    a.set_facecolor("none"); a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([]); a.set_yticks([])
    a.set_aspect("equal")

    render_img = _mobius_render_image()
    iw, ih = render_img.size
    a.imshow(np.asarray(render_img), extent=(0, iw, 0, ih), zorder=3)
    a.set_xlim(0, iw); a.set_ylim(0, ih)

    ax.text(
        50, 27.0,
        IT(r"a strip with a half-twist  $\cdot$  cut it along the middle and see what happens")
        if _USE_LATEX else "a strip with a half-twist  ·  cut it along the middle and see what happens",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", va="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"A one-sided, one-edged surface --- there is no `inside' or `outside'." if _USE_LATEX
            else "A one-sided, one-edged surface — there is no 'inside' or 'outside'.",
            r"Trace a finger along it and you visit both `faces' without lifting the pen." if _USE_LATEX
            else "Trace a finger along it and you visit both 'faces' without lifting the pen.",
            r"Discovered independently by M\"obius and Listing in 1858." if _USE_LATEX
            else "Discovered independently by Möbius and Listing in 1858.",
        ],
        22.8,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$\mathbf{r}(u,v)$", "parametrization"),
        (r"$\chi=0$", "Euler characteristic"),
        ("1 side · 1 edge", "non-orientable"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Design 10: Tesseract ────────────────────────────────────────────────────────

_TESSERACT_RENDER_SCRIPT = BASE / "attractor_prints" / "generate_tesseract_render.py"
_TESSERACT_RENDER_CACHE = OUT_ROOT / "tesseract" / "_pv_render.png"


def _tesseract_render_image() -> Image.Image:
    """Real 3D render (pyvista/VTK, off-screen via xvfb-run) of a tesseract:
    16 vertices, genuinely rotated in 4D (not a static cube-in-a-cube diagram),
    then perspective-projected 4D->3D. Colour stands in for the axis we can't
    draw -- gold is near in the 4th dimension, ink is far. Rendered once and
    cached, same pattern as the Mobius strip's pyvista render."""
    if not _TESSERACT_RENDER_CACHE.exists():
        _TESSERACT_RENDER_CACHE.parent.mkdir(parents=True, exist_ok=True)
        print("  rendering tesseract via pyvista (xvfb-run, one-time)...")
        subprocess.run(
            ["xvfb-run", "-a", "python3", str(_TESSERACT_RENDER_SCRIPT),
             str(_TESSERACT_RENDER_CACHE), "4200", "3400"],
            check=True,
        )
    return Image.open(_TESSERACT_RENDER_CACHE).convert("RGBA")


def compose_tesseract(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    _header(
        ax, "A SHADOW OF FOUR DIMENSIONS", "FIG. 10", "TESSERACT",
        r"$\{\pm1\}^{4}$",
        fig_w,
    )

    a = fig.add_axes([0.10, 0.30, 0.80, 0.53], zorder=3)
    a.set_facecolor("none"); a.patch.set_alpha(0)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_xticks([]); a.set_yticks([])
    a.set_aspect("equal")

    render_img = _tesseract_render_image()
    iw, ih = render_img.size
    a.imshow(np.asarray(render_img), extent=(0, iw, 0, ih), zorder=3)
    a.set_xlim(0, iw); a.set_ylim(0, ih)

    ax.text(
        50, 27.0,
        IT(r"a cube has 8 vertices in 3 dimensions  $\cdot$  a tesseract has 16 in four")
        if _USE_LATEX else "a cube has 8 vertices in 3 dimensions  ·  a tesseract has 16 in four",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", va="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"What you see is a shadow --- a 3D projection of a 4D object, the way a cube casts a 2D shadow." if _USE_LATEX
            else "What you see is a shadow — a 3D projection of a 4D object, the way a cube casts a 2D shadow.",
            r"Color stands in for the axis we cannot draw: gold is near in the fourth dimension, ink is far." if _USE_LATEX
            else "Color stands in for the axis we cannot draw: gold is near in the fourth dimension, ink is far.",
            r"Popularized as the `hypercube' --- 4D geometry with real uses in relativity and data science." if _USE_LATEX
            else "Popularized as the 'hypercube' — 4D geometry with real uses in relativity and data science.",
        ],
        22.8,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$V=16$", "vertices"),
        (r"$E=32$", "edges"),
        (r"$F=24$", "square faces"),
        fig_w,
    )
    return fig_to_image(fig)


@dataclass
class Design:
    slug: str
    folder: str
    title_line: str  # display on plate already in compose
    listing_prefix: str  # "Math Wall Art" or "Physics Wall Art"
    concept: str
    tags: list[str]
    seo_title: str
    description_blurb: str
    compose: callable
    zip_name: str
    fig_theme: str


DESIGNS: list[Design] = [
    Design(
        slug="fourier_series",
        folder="fourier_series",
        title_line="Fourier Series",
        listing_prefix="Math Wall Art",
        concept="Fourier Series",
        tags=[
            "math wall art",
            "fourier series",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "calculus art",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "signal processing",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Fourier Series Print | Square Wave Harmonics "
            "STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate showing a square wave built from Fourier partial sums "
            "(N = 1, 3, 7, 25). Cream graph paper, LaTeX equations, rust accent."
        ),
        compose=compose_fourier,
        zip_name="Fourier_Series_Math_Wall_Art.zip",
        fig_theme="square-wave harmonics",
    ),
    Design(
        slug="wave_equation",
        folder="wave_equation",
        title_line="Wave Equation",
        listing_prefix="Physics Wall Art",
        concept="Wave Equation",
        tags=[
            "physics wall art",
            "wave equation",
            "physics poster",
            "stem wall art",
            "science poster",
            "math wall art",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "standing waves",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Wave Equation Print | Standing Waves on a String "
            "STEM Science Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the 1D wave equation with standing-wave modes n = 1, 2, 3. "
            "Nodes, antinodes, and the classical string — LaTeX typography."
        ),
        compose=compose_wave,
        zip_name="Wave_Equation_Physics_Wall_Art.zip",
        fig_theme="standing-wave modes",
    ),
    Design(
        slug="dirac_equation",
        folder="dirac_equation",
        title_line="Dirac Equation",
        listing_prefix="Physics Wall Art",
        concept="Dirac Equation",
        tags=[
            "physics wall art",
            "dirac equation",
            "quantum physics art",
            "physics poster",
            "antimatter art",
            "stem wall art",
            "science poster",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "relativity art",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Dirac Equation Print | Matter Antimatter "
            "Relativistic Quantum Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Dirac equation with the ± energy–momentum continuum, "
            "mass gap, and antimatter interpretation."
        ),
        compose=compose_dirac,
        zip_name="Dirac_Equation_Physics_Wall_Art.zip",
        fig_theme="energy-momentum continuum",
    ),
    Design(
        slug="navier_stokes",
        folder="navier_stokes",
        title_line="Navier-Stokes",
        listing_prefix="Physics Wall Art",
        concept="Navier-Stokes Equations",
        tags=[
            "physics wall art",
            "navier stokes",
            "fluid dynamics art",
            "physics poster",
            "stem wall art",
            "science poster",
            "math wall art",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "engineering art",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Navier-Stokes Equations Print | Fluid Dynamics "
            "Streamlines STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Navier–Stokes equations with potential flow "
            "streamlines past a cylinder — continuum mechanics as gallery art."
        ),
        compose=compose_navier,
        zip_name="Navier_Stokes_Physics_Wall_Art.zip",
        fig_theme="cylinder streamlines",
    ),
    Design(
        slug="euler_identity",
        folder="euler_identity",
        title_line="Euler Identity",
        listing_prefix="Math Wall Art",
        concept="Euler's Identity",
        tags=[
            "math wall art",
            "eulers identity",
            "euler formula",
            "mathematics poster",
            "complex numbers",
            "stem wall art",
            "science poster",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "classroom decor",
        ],
        seo_title=(
            "Math Wall Art | Euler's Identity Print | e^(iπ)+1=0 Complex Plane "
            "STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Euler's identity on the complex unit circle — "
            "the most beautiful equation as minimal wall art."
        ),
        compose=compose_euler,
        zip_name="Euler_Identity_Math_Wall_Art.zip",
        fig_theme="complex unit circle",
    ),
    Design(
        slug="mandelbrot_set",
        folder="mandelbrot_set",
        title_line="Mandelbrot Set",
        listing_prefix="Math Wall Art",
        concept="Mandelbrot Set",
        tags=[
            "math wall art",
            "mandelbrot set",
            "fractal art",
            "mathematics poster",
            "chaos theory",
            "stem wall art",
            "generative art",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "complex dynamics",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Mandelbrot Set Print | Fractal Chaos Theory "
            "Complex Dynamics STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Mandelbrot set with the quadratic map "
            "z→z²+c — cream/ink/rust escape-time portrait, not neon fractal kitsch."
        ),
        compose=compose_mandelbrot,
        zip_name="Mandelbrot_Set_Math_Wall_Art.zip",
        fig_theme="escape-time Mandelbrot",
    ),
    Design(
        slug="normal_distribution",
        folder="normal_distribution",
        title_line="Normal Distribution",
        listing_prefix="Math Wall Art",
        concept="Normal Distribution",
        tags=[
            "math wall art",
            "normal distribution",
            "statistics poster",
            "bell curve",
            "data science art",
            "stem wall art",
            "science poster",
            "educational poster",
            "classroom decor",
            "digital download",
            "teacher gift",
            "gaussian curve",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Normal Distribution Print | Bell Curve Gaussian "
            "Statistics Data Science STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Gaussian bell curve with the 68-95-99.7 rule "
            "and standard-deviation bands. Cream graph paper, LaTeX equations, rust accent."
        ),
        compose=compose_gaussian,
        zip_name="Normal_Distribution_Math_Wall_Art.zip",
        fig_theme="Gaussian bell curve",
    ),
    Design(
        slug="koch_snowflake",
        folder="koch_snowflake",
        title_line="Koch Snowflake",
        listing_prefix="Math Wall Art",
        concept="Koch Snowflake",
        tags=[
            "math wall art",
            "koch snowflake",
            "fractal art",
            "mathematics poster",
            "geometry poster",
            "stem wall art",
            "science poster",
            "educational poster",
            "classroom decor",
            "digital download",
            "teacher gift",
            "generative art",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Koch Snowflake Print | Fractal Geometry "
            "Infinite Perimeter STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Koch snowflake's recursive construction (n=0..3) — "
            "infinite perimeter, finite area. Cream graph paper, LaTeX equations, rust accent."
        ),
        compose=compose_koch,
        zip_name="Koch_Snowflake_Math_Wall_Art.zip",
        fig_theme="Koch snowflake recursion",
    ),
    Design(
        slug="mobius_strip",
        folder="mobius_strip",
        title_line="Mobius Strip",
        listing_prefix="Math Wall Art",
        concept="Mobius Strip",
        tags=[
            "math wall art",
            "mobius strip",
            "topology art",
            "mathematics poster",
            "geometry poster",
            "stem wall art",
            "science poster",
            "educational poster",
            "classroom decor",
            "digital download",
            "teacher gift",
            "conceptual art",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Mobius Strip Print | Topology One-Sided Surface "
            "Conceptual STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the Mobius strip — a shaded 3D rendering of the one-sided, "
            "one-edged surface with its single boundary traced in rust. Cream graph paper, "
            "LaTeX equations."
        ),
        compose=compose_mobius,
        zip_name="Mobius_Strip_Math_Wall_Art.zip",
        fig_theme="Mobius strip topology",
    ),
    Design(
        slug="tesseract",
        folder="tesseract",
        title_line="Tesseract",
        listing_prefix="Math Wall Art",
        concept="Tesseract",
        tags=[
            "math wall art",
            "tesseract",
            "hypercube",
            "fourth dimension",
            "mathematics poster",
            "geometry poster",
            "stem wall art",
            "science poster",
            "classroom decor",
            "digital download",
            "teacher gift",
            "conceptual art",
            "math print",
        ],
        seo_title=(
            "Math Wall Art | Tesseract Print | 4D Hypercube Fourth Dimension "
            "Conceptual STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of the tesseract — a real 3D-rendered shadow of a rotating 4D "
            "hypercube, colour-coded by depth along the axis we cannot draw. Cream graph paper, "
            "LaTeX equations."
        ),
        compose=compose_tesseract,
        zip_name="Tesseract_Math_Wall_Art.zip",
        fig_theme="Tesseract / 4D hypercube",
    ),
]


def compose_equation_card(design: Design, width_in=10.0, height_in=8.0, dpi=DPI_PREVIEW) -> Image.Image:
    """Clean equation-focused listing image."""
    fig, ax = _new_plate(width_in, height_in, dpi)
    eqs = {
        "fourier_series": r"$f(x)=\sum c_n e^{inx}$",
        "wave_equation": r"$\partial_{tt}u=c^{2}\partial_{xx}u$" if _USE_LATEX else r"$\partial_{tt}u=c^2\partial_{xx}u$",
        "dirac_equation": r"$(i\gamma^{\mu}\partial_{\mu}-m)\psi=0$" if _USE_LATEX else r"$(i\gamma^\mu\partial_\mu-m)\psi=0$",
        "navier_stokes": r"$\rho D_t\mathbf{u}=-\nabla p+\mu\nabla^{2}\mathbf{u}$" if _USE_LATEX else r"$\rho D_t u=-\nabla p+\mu\nabla^2 u$",
        "euler_identity": r"$e^{i\pi}+1=0$",
        "mandelbrot_set": r"$z_{n+1}=z_n^{2}+c$" if _USE_LATEX else r"$z_{n+1}=z_n^2+c$",
        "normal_distribution": r"$f(x)=\dfrac{1}{\sigma\sqrt{2\pi}}\,e^{-(x-\mu)^2/2\sigma^2}$",
        "koch_snowflake": r"$N_n=3\cdot4^{\,n}$",
        "mobius_strip": r"$u\to u+2\pi\ \Rightarrow\ v\to-v$",
        "tesseract": r"$\{\pm1\}^{4}$",
    }
    ax.text(50, 72, SFb(design.concept.upper()), fontsize=_fs(width_in, 0.026), color=INK, ha="center")
    ax.text(50, 52, eqs[design.slug], fontsize=_fs(width_in, 0.040), color=RUST, ha="center", va="center")
    ax.text(50, 34, SF(design.listing_prefix + "  ·  scientific plate") if _USE_LATEX
            else design.listing_prefix + "  ·  scientific plate",
            fontsize=_fs(width_in, 0.013), color=INK_SOFT, ha="center")
    ax.text(50, 22, SF("MathRelaxing") if _USE_LATEX else "MathRelaxing",
            fontsize=_fs(width_in, 0.012), color=INK_FAINT, ha="center")
    return fig_to_image(fig)


def build_design(design: Design, preview_only: bool = False):
    out = OUT_ROOT / design.folder
    prints = out / "prints"
    previews = out / "previews"
    out.mkdir(parents=True, exist_ok=True)
    prints.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)

    print(f"\n=== {design.slug} ===")

    if not preview_only:
        for name, (w, h) in SIZES.items():
            print(f"  print {name} ({w}×{h} @ {DPI_PRINT}dpi)…")
            img = design.compose(w, h, DPI_PRINT)
            save_rgb(img, prints / f"{design.slug}_{name}_{DPI_PRINT}dpi.jpg", DPI_PRINT, 90)

        zip_path = out / design.zip_name
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "README.txt",
                f"""{design.concept} — {design.listing_prefix}
MathRelaxing scientific plate

{design.description_blurb}

WHAT YOU GET
High-resolution JPG prints at 300 dpi:
  • 2:3  (12×18 in)
  • 3:4  (12×16 in)
  • 4:5  (16×20 in)
  • 5:7  (10×14 in)
  • ISO A4 and A3

Print at home, a print shop, or online lab. Matte paper looks best.
Frame not included. Personal use only.

© MathRelaxing
""",
            )
            for fn in sorted(prints.glob("*.jpg")):
                zf.write(fn, arcname=fn.name)
        mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  ZIP {zip_path.name} ({mb:.1f} MB)")

    # Previews
    print("  previews…")
    hero = design.compose(10.0, 12.5, DPI_PREVIEW)
    save_rgb(hero, previews / f"{design.slug}_preview_1_hero.jpg", DPI_PREVIEW, 92)

    detail = design.compose(14.0, 10.0, DPI_PREVIEW)
    dw, dh = detail.size
    crop = detail.crop((int(dw * 0.05), int(dh * 0.14), int(dw * 0.95), int(dh * 0.72)))
    side = max(crop.size)
    pad = Image.new("RGB", (side, int(side * 0.85)), (244, 241, 234))
    pad.paste(crop, ((pad.size[0] - crop.size[0]) // 2, (pad.size[1] - crop.size[1]) // 2))
    save_rgb(pad, previews / f"{design.slug}_preview_2_detail.jpg", DPI_PREVIEW, 92)

    # included card
    fig, ax = _new_plate(10, 10, DPI_PREVIEW)
    ax.text(55, 78, SFb("included"), fontsize=24, color=INK, ha="left")
    lines = [
        "1 scientific-plate print",
        design.concept,
        design.fig_theme,
        "",
        "Aspect ratios:",
        "2:3 · 3:4 · 4:5 · 5:7",
        "ISO A4 · A3",
        "",
        "300 dpi JPG · ZIP",
        "equations in LaTeX",
        "",
        "Best on matte paper",
        "Instant download",
    ]
    y = 68
    for line in lines:
        ax.text(55, y, SF(line) if _USE_LATEX else line, fontsize=12.5, color=INK_SOFT, ha="left")
        y -= 4.0
    base = fig_to_image(fig)
    mini = design.compose(5.0, 7.0, DPI_PREVIEW)
    mini = mini.resize((int(base.size[0] * 0.44), int(base.size[1] * 0.70)), Image.Resampling.LANCZOS)
    base.paste(mini, (int(base.size[0] * 0.05), int(base.size[1] * 0.14)))
    save_rgb(base, previews / f"{design.slug}_preview_3_included.jpg", DPI_PREVIEW, 92)

    plate = design.compose(8.0, 10.0, DPI_PREVIEW)
    save_rgb(plate, previews / f"{design.slug}_preview_4_plate.jpg", DPI_PREVIEW, 92)

    eq = compose_equation_card(design)
    save_rgb(eq, previews / f"{design.slug}_preview_5_equation.jpg", DPI_PREVIEW, 92)


def build_set_bundle(designs: list[Design], preview_only: bool = False):
    """Famous Equations / Math-Physics plate set of 6."""
    out = OUT_ROOT / "famous_equations_set"
    prints = out / "prints"
    previews = out / "previews"
    out.mkdir(parents=True, exist_ok=True)
    prints.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)
    print("\n=== famous_equations_set (bundle) ===")

    if not preview_only:
        # One large print per design (2x3 master) into set folder
        for d in designs:
            src = OUT_ROOT / d.folder / "prints" / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg"
            if src.exists():
                dest = prints / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg"
                shutil.copy2(src, dest)
            else:
                print(f"  render missing single for set: {d.slug}")
                img = d.compose(12.0, 18.0, DPI_PRINT)
                save_rgb(img, prints / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg", DPI_PRINT, 90)
            # also copy A4 for convenience
            src_a4 = OUT_ROOT / d.folder / "prints" / f"{d.slug}_A4_{DPI_PRINT}dpi.jpg"
            if src_a4.exists():
                shutil.copy2(src_a4, prints / f"{d.slug}_A4_{DPI_PRINT}dpi.jpg")

        zip_path = out / "Famous_Equations_Wall_Art_Set_of_6.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "README.txt",
                """Famous Equations — Wall Art Set of 6
MathRelaxing scientific plates

Six gallery prints in one download:
  1. Fourier Series — square-wave harmonics
  2. Wave Equation — standing modes on a string
  3. Dirac Equation — matter & antimatter continuum
  4. Navier–Stokes — flow past a cylinder
  5. Euler's Identity — complex unit circle
  6. Mandelbrot Set — geometry of chaos

Each design includes 2:3 (12×18) and A4 masters at 300 dpi.
Matte paper recommended. Personal use only.

© MathRelaxing
""",
            )
            for fn in sorted(prints.glob("*.jpg")):
                zf.write(fn, arcname=fn.name)
        mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  ZIP {zip_path.name} ({mb:.1f} MB)")
        if mb > 19.5:
            print("  WARNING: near Etsy 20MB limit — consider dropping A4 from set")

    # Hero grid 2×3
    thumbs = []
    for d in designs:
        p = OUT_ROOT / d.folder / "previews" / f"{d.slug}_preview_4_plate.jpg"
        if p.exists():
            thumbs.append(Image.open(p).convert("RGB"))
        else:
            thumbs.append(d.compose(6, 8, DPI_PREVIEW))

    # 3×2 grid on cream
    cell_w, cell_h = 360, 450
    gap = 16
    cols, rows = 3, 2
    W = cols * cell_w + (cols + 1) * gap
    H = rows * cell_h + (rows + 1) * gap + 100
    grid = Image.new("RGB", (W, H), (244, 241, 234))
    draw = ImageDraw.Draw(grid)
    try:
        font = ImageFont.truetype("georgia.ttf", 28)
        font_s = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        font_s = font
    draw.text((W // 2, 28), "FAMOUS EQUATIONS  ·  SET OF 6", font=font, fill=(26, 26, 26), anchor="mt")
    draw.text((W // 2, 62), "Scientific plates  ·  math & physics wall art", font=font_s, fill=(184, 92, 56), anchor="mt")
    for i, im in enumerate(thumbs[:6]):
        c, r = i % cols, i // cols
        th = im.copy()
        th.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        x = gap + c * (cell_w + gap) + (cell_w - th.width) // 2
        y = 90 + gap + r * (cell_h + gap) + (cell_h - th.height) // 2
        # thin frame
        draw.rectangle([x - 3, y - 3, x + th.width + 3, y + th.height + 3], outline=(26, 26, 26), width=2)
        grid.paste(th, (x, y))
    # pad to square-ish for Etsy
    side = max(W, H)
    canvas = Image.new("RGB", (side, side), (244, 241, 234))
    canvas.paste(grid, ((side - W) // 2, (side - H) // 2))
    save_rgb(canvas, previews / "famous_equations_preview_1_hero.jpg", DPI_PREVIEW, 92)

    # included
    incl = Image.new("RGB", (1200, 1200), (244, 241, 234))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, 1200, 140], fill=(26, 26, 26))
    d.text((600, 50), "WHAT'S INCLUDED", font=font, fill=(244, 241, 234), anchor="mt")
    d.text((600, 95), "6 scientific plates  ·  multi-size masters", font=font_s, fill=(184, 92, 56), anchor="mt")
    names = [
        "Fourier Series", "Wave Equation", "Dirac Equation",
        "Navier–Stokes", "Euler's Identity", "Mandelbrot Set",
    ]
    y = 200
    for i, name in enumerate(names):
        d.ellipse([120, y, 200, y + 70], fill=(184, 92, 56))
        d.text((160, y + 35), str(i + 1), font=font_s, fill=(244, 241, 234), anchor="mm")
        d.text((230, y + 35), name, font=font, fill=(26, 26, 26), anchor="lm")
        y += 100
    d.text((600, 1100), "300 dpi  ·  Instant download  ·  MathRelaxing", font=font_s, fill=(85, 85, 85), anchor="mt")
    save_rgb(incl, previews / "famous_equations_preview_2_included.jpg", DPI_PREVIEW, 92)

    # strip of equations
    for i, dsgn in enumerate(designs[:4]):
        eq = compose_equation_card(dsgn, 8, 6, DPI_PREVIEW)
        save_rgb(eq, previews / f"famous_equations_preview_{i+3}_eq.jpg", DPI_PREVIEW, 92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, default="", help="comma-separated slugs")
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--skip-set", action="store_true")
    args = ap.parse_args()

    print("=== Equation scientific plates series ===")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    designs = DESIGNS
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        designs = [d for d in DESIGNS if d.slug in want]
        if not designs:
            raise SystemExit(f"No designs matched {want}")

    for d in designs:
        build_design(d, preview_only=args.preview_only)

    if not args.skip_set:
        # set needs all six ideally
        all_d = DESIGNS if not args.only else designs
        if len(all_d) >= 6 or not args.only:
            build_set_bundle(DESIGNS, preview_only=args.preview_only)
        else:
            print("  skip set (need full series)")

    print("\nDONE →", OUT_ROOT)


if __name__ == "__main__":
    main()
