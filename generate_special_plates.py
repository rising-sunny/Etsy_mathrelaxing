"""
generate_special_plates.py — Special-function scientific plates (scipy)
=======================================================================
Singles + Special Functions Wall Art Set of 6 (distinct from Famous Equations
and from Physics Field Equations set):

  1. bessel_functions       — cylinder waves J_n
  2. hermite_qho            — Hermite / harmonic oscillator
  3. legendre_polynomials   — Legendre P_n (multipoles)
  4. mandelbrot_zoom        — Mandelbrot detail (single only; not in set)
  5. laguerre_polynomials   — Laguerre L_n
  6. chebyshev_polynomials  — Chebyshev T_n
  7. airy_functions         — Airy Ai / Bi turning points

Set of 6 = 1,2,3,5,6,7 (no Mandelbrot — avoids Famous Equations fractal overlap)

Style: same cream graph paper + LaTeX family as generate_equation_plates.py

  python generate_special_plates.py
  python generate_special_plates.py --only laguerre_polynomials,chebyshev_polynomials,airy_functions
  python generate_special_plates.py --set-only
  python generate_special_plates.py --no-latex
"""
from __future__ import annotations

import argparse
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import special as sp

# Reuse plate chrome from equation series
from generate_equation_plates import (
    CREAM,
    DPI_PREVIEW,
    DPI_PRINT,
    GRID,
    INK,
    INK_FAINT,
    INK_SOFT,
    LINE_DARK,
    RUST,
    SIZES,
    IT,
    SF,
    SFb,
    _caption,
    _footer_eqs,
    _fs,
    _header,
    _new_plate,
    _open_axes,
    configure_matplotlib,
    fig_to_image,
    save_rgb,
)
import generate_equation_plates as gep

BASE = Path(__file__).resolve().parent
OUT_ROOT = BASE / "special_plates"


# ── 1. Bessel J0, J1, J2 ──────────────────────────────────────────────────────

def compose_bessel(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "WAVES IN A CIRCLE",
        "FIG. 7",
        "BESSEL FUNCTIONS",
        r"$x^{2}y''+xy'+(x^{2}-n^{2})y=0$" if use_tex else r"$x^2 y''+xy'+(x^2-n^2)y=0$",
        fig_w,
    )

    # Three panels J0, J1, J2 with zeros marked
    orders = [0, 1, 2]
    labels = ["fundamental radial", "dipole mode", "quadrupole mode"]
    left, right = 0.08, 0.92
    bottom, top = 0.34, 0.83
    gap = 0.04
    n = len(orders)
    col_w = (right - left - (n - 1) * gap) / n
    x = np.linspace(0.0, 14.0, 1200)

    for i, (nu, lab) in enumerate(zip(orders, labels)):
        x0 = left + i * (col_w + gap)
        a = _open_axes(fig, [x0, bottom, col_w, top - bottom], fig_w)
        y = sp.jv(nu, x)
        a.set_xlim(0, 14)
        a.set_ylim(-0.55, 1.15)
        a.axhline(0, color=INK_FAINT, lw=0.55, ls=(0, (1.2, 2)), zorder=1)
        a.fill_between(x, 0, y, where=(y >= 0), color=RUST, alpha=0.12, lw=0, zorder=2)
        a.fill_between(x, 0, y, where=(y < 0), color=LINE_DARK, alpha=0.06, lw=0, zorder=2)
        a.plot(x, y, color=LINE_DARK, lw=2.1, solid_capstyle="round", zorder=4, antialiased=True)
        # first few positive zeros
        zeros = sp.jn_zeros(nu, 4)
        for z in zeros:
            if z <= 14:
                a.plot(z, 0, "o", color=RUST, ms=3.8, zorder=6, markeredgewidth=0)
        a.text(0.5, 1.08, rf"$J_{{{nu}}}(x)$", transform=a.transAxes, ha="center",
               fontsize=_fs(fig_w, 0.015), color=INK, clip_on=False)
        a.text(0.5, -0.12, SF(lab) if use_tex else lab, transform=a.transAxes, ha="center",
               fontsize=_fs(fig_w, 0.009), color=INK_SOFT, clip_on=False)

    ax.text(
        50, 27.5,
        IT(r"cylindrical waves  $\cdot$  drum modes  $\cdot$  zeros of $J_n$")
        if use_tex else "cylindrical waves  ·  drum modes  ·  zeros of Jn",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Bessel functions solve the radial wave equation in polar coordinates.",
            r"The zeros of $J_n$ set the allowed frequencies of a circular drum." if use_tex
            else "The zeros of Jn set the allowed frequencies of a circular drum.",
            r"They appear in optics, antennas, quantum wells, and heat flow in cylinders.",
        ],
        23.0,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$J_n(x)=\sum_{k=0}^{\infty}\dfrac{(-1)^k}{k!\,(n+k)!}\left(\dfrac{x}{2}\right)^{n+2k}$"
         if use_tex else r"$J_n$ series", "power series"),
        (r"$\nabla^{2}\psi+k^{2}\psi=0$" if use_tex else r"$\nabla^2\psi+k^2\psi=0$", "Helmholtz (polar)"),
        (r"$J_n(j_{n,s})=0$", "drum zeros"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 2. Hermite / quantum harmonic oscillator ──────────────────────────────────

def compose_hermite(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "THE QUANTUM SPRING",
        "FIG. 8",
        "HERMITE  /  HARMONIC OSCILLATOR",
        r"$-\dfrac{\hbar^{2}}{2m}\psi''+\tfrac{1}{2}m\omega^{2}x^{2}\psi=E\psi$"
        if use_tex else r"$-\frac{\hbar^2}{2m}\psi''+\frac12 m\omega^2 x^2\psi=E\psi$",
        fig_w,
    )

    # ψ_n for n=0,1,2,3 — physicist's Hermite with Gaussian
    modes = [0, 1, 2, 3]
    left, right = 0.07, 0.93
    gap = 0.028
    n = len(modes)
    col_w = (right - left - (n - 1) * gap) / n
    xi = np.linspace(-4.2, 4.2, 900)

    def psi_n(n_q: int, x: np.ndarray) -> np.ndarray:
        # ψ_n(ξ) ∝ H_n(ξ) e^{-ξ²/2}  (dimensionless)
        H = sp.eval_hermite(n_q, x)
        raw = H * np.exp(-0.5 * x ** 2)
        # normalize max abs for display
        m = np.max(np.abs(raw)) or 1.0
        return raw / m

    for i, n_q in enumerate(modes):
        x0 = left + i * (col_w + gap)
        # upper: wavefunction
        a = _open_axes(fig, [x0, 0.48, col_w, 0.34], fig_w)
        y = psi_n(n_q, xi)
        a.set_xlim(-4.2, 4.2)
        a.set_ylim(-1.35, 1.45)
        a.axhline(0, color=INK_FAINT, lw=0.55, ls=(0, (1.2, 2)), zorder=1)
        # parabolic well cue
        well = 0.08 * xi ** 2 - 1.15
        a.plot(xi, well, color=INK_FAINT, lw=0.7, alpha=0.5, zorder=1)
        a.fill_between(xi, 0, y, color=RUST, alpha=0.12, lw=0, zorder=2)
        a.plot(xi, y, color=LINE_DARK, lw=2.0, solid_capstyle="round", zorder=4, antialiased=True)
        a.text(0.5, 1.08, rf"$n={n_q}$", transform=a.transAxes, ha="center",
               fontsize=_fs(fig_w, 0.013), color=INK, clip_on=False)
        a.text(1.02, 0.88, r"$\psi$", transform=a.transAxes, ha="left",
               fontsize=_fs(fig_w, 0.011), color=LINE_DARK, clip_on=False)

        # lower: probability
        b = _open_axes(fig, [x0, 0.30, col_w, 0.14], fig_w)
        prob = y ** 2
        b.set_xlim(-4.2, 4.2)
        b.set_ylim(-0.05, 1.15)
        b.fill_between(xi, 0, prob, color=RUST, alpha=0.22, lw=0, zorder=2)
        b.plot(xi, prob, color=RUST, lw=1.65, zorder=3, solid_capstyle="round")
        b.plot([-4.2, 4.2], [0, 0], color=LINE_DARK, lw=0.9, zorder=4)
        b.text(1.02, 0.75, r"$|\psi|^{2}$" if use_tex else r"$|\psi|^2$",
               transform=b.transAxes, ha="left", fontsize=_fs(fig_w, 0.010), color=RUST, clip_on=False)
        b.text(0.5, -0.42,
               rf"$E_{{{n_q}}}=\hbar\omega({n_q}+\tfrac{{1}}{{2}})$" if use_tex
               else rf"$E_{n_q}=\hbar\omega({n_q}+1/2)$",
               transform=b.transAxes, ha="center", fontsize=_fs(fig_w, 0.0095),
               color=RUST, clip_on=False)

    ax.text(
        50, 25.2,
        IT(r"physicist's Hermite  $\cdot$  Gaussian ground state  $\cdot$  even/odd parity")
        if use_tex else "physicist's Hermite  ·  Gaussian ground state  ·  even/odd parity",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"The quantum harmonic oscillator is solved by Hermite polynomials times a Gaussian.",
            r"Energies are equally spaced: zero-point energy $\tfrac{1}{2}\hbar\omega$ never vanishes." if use_tex
            else "Energies are equally spaced: zero-point energy never vanishes.",
            r"The same ladder operators structure photons, phonons, and molecular vibrations.",
        ],
        21.2,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$H_n'=2n H_{n-1}$", "Hermite recurrence"),
        (r"$\psi_n\propto H_n(\xi)\,e^{-\xi^{2}/2}$" if use_tex else r"$\psi_n\propto H_n e^{-\xi^2/2}$", "stationary states"),
        (r"$E_n=\hbar\omega(n+\tfrac{1}{2})$" if use_tex else r"$E_n=\hbar\omega(n+1/2)$", "spectrum"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 3. Legendre polynomials ───────────────────────────────────────────────────

def compose_legendre(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "POLYNOMIALS ON THE SPHERE",
        "FIG. 9",
        "LEGENDRE POLYNOMIALS",
        r"$(1-x^{2})y''-2xy'+n(n+1)y=0$" if use_tex else r"$(1-x^2)y''-2xy'+n(n+1)y=0$",
        fig_w,
    )

    degrees = [0, 1, 2, 3, 4]
    left, right = 0.08, 0.92
    bottom, top = 0.34, 0.82
    # single wide axes with all curves + side legend feel via color weight
    a = _open_axes(fig, [left, bottom, right - left, top - bottom], fig_w)
    x = np.linspace(-1.0, 1.0, 800)
    a.set_xlim(-1.05, 1.05)
    a.set_ylim(-1.25, 1.35)
    a.axhline(0, color=INK_FAINT, lw=0.55, zorder=1)
    a.axvline(0, color=INK_FAINT, lw=0.45, zorder=1)
    # domain ends
    a.plot([-1, -1], [-1.15, 1.2], color=LINE_DARK, lw=1.2, zorder=3)
    a.plot([1, 1], [-1.15, 1.2], color=LINE_DARK, lw=1.2, zorder=3)

    # line weights: higher n slightly thinner, alternate ink/rust emphasis
    for n in degrees:
        y = sp.eval_legendre(n, x)
        col = LINE_DARK if n % 2 == 0 else RUST
        lw = 2.15 - 0.12 * n
        a.plot(x, y, color=col, lw=lw, solid_capstyle="round", zorder=4 + n, antialiased=True,
               label=rf"$P_{{{n}}}$")
        # label at right edge
        a.text(1.08, y[-1], rf"$P_{{{n}}}$", color=col, fontsize=_fs(fig_w, 0.012),
               ha="left", va="center", clip_on=False)

    a.text(0.5, 1.06, SF("orthogonal on $[-1,1]$  ·  multipole moments") if use_tex
           else "orthogonal on [-1,1]  ·  multipole moments",
           transform=a.transAxes, ha="center", fontsize=_fs(fig_w, 0.011), color=INK_SOFT, clip_on=False)
    a.text(0.0, -0.12, r"$x=\cos\theta$", transform=a.transAxes, ha="left",
           fontsize=_fs(fig_w, 0.010), color=INK_FAINT, clip_on=False)

    ax.text(
        50, 27.0,
        IT(r"associated with spherical harmonics $Y_{\ell}^{m}$  $\cdot$  gravity, electrostatics, QM")
        if use_tex else "associated with spherical harmonics  ·  gravity, electrostatics, QM",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Legendre polynomials are orthogonal on the interval $[-1,1]$." if use_tex
            else "Legendre polynomials are orthogonal on the interval [-1,1].",
            r"They expand axisymmetric fields: gravity, electrostatics, and quantum angular momentum.",
            r"With $\phi$ dependence they become the associated Legendre family behind $Y_\ell^m$." if use_tex
            else "With phi dependence they become the associated Legendre family behind spherical harmonics.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$\displaystyle\int_{-1}^{1}P_n P_m\,dx=\dfrac{2}{2n+1}\delta_{nm}$"
         if use_tex else r"$\int P_n P_m=\frac{2}{2n+1}\delta_{nm}$", "orthogonality"),
        (r"$P_n(x)=\dfrac{1}{2^n n!}\dfrac{d^n}{dx^n}(x^{2}-1)^n$" if use_tex
         else r"$P_n$ Rodrigues", "Rodrigues formula"),
        (r"$Y_{\ell}^{m}\propto P_{\ell}^{m}$" if use_tex else r"$Y_l^m \propto P$", "spherical harmonics"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 4. Mandelbrot zoom (seahorse valley-ish) ──────────────────────────────────

def _mandelbrot_smooth(xmin, xmax, ymin, ymax, width, height, max_iter=220):
    xs = np.linspace(xmin, xmax, width, dtype=np.float64)
    ys = np.linspace(ymin, ymax, height, dtype=np.float64)
    X, Y = np.meshgrid(xs, ys)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    escape = np.zeros(C.shape, dtype=np.float64)
    active = np.ones(C.shape, dtype=bool)
    for n in range(max_iter):
        Z[active] = Z[active] ** 2 + C[active]
        escaped_now = active & (np.abs(Z) > 2.0)
        if np.any(escaped_now):
            z_esc = Z[escaped_now]
            with np.errstate(divide="ignore", invalid="ignore"):
                log_mod = np.log(np.maximum(np.abs(z_esc), 1e-16))
                nu = n + 1.0 - np.log(log_mod) / np.log(2.0)
            escape[escaped_now] = np.clip(nu, 0, max_iter)
            active[escaped_now] = False
        if not np.any(active):
            break
    escape[active] = max_iter
    return escape, max_iter


def compose_mandelbrot_zoom(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "INFINITE COASTLINE",
        "FIG. 10",
        "MANDELBROT  /  DETAIL ZOOM",
        r"$z_{n+1}=z_n^{2}+c$" if use_tex else r"$z_{n+1}=z_n^2+c$",
        fig_w,
    )

    a = fig.add_axes([0.11, 0.30, 0.78, 0.50], zorder=3)
    a.set_facecolor(CREAM)
    for sp in a.spines.values():
        sp.set_color(INK_FAINT)
        sp.set_linewidth(0.85)
    a.set_xticks([])
    a.set_yticks([])

    # Seahorse valley / period-2 bulb filament region (classic zoom)
    # Center near -0.75 + 0.1i, moderate zoom
    cx, cy = -0.743643887037151, 0.131825904205312
    span = 0.0125
    xmin, xmax = cx - span * 1.15, cx + span * 1.15
    ymin, ymax = cy - span, cy + span

    px = 960 if dpi >= 200 else 620
    py = int(px * (ymax - ymin) / (xmax - xmin))
    escape, max_iter = _mandelbrot_smooth(xmin, xmax, ymin, ymax, px, py, max_iter=240)

    rgb = np.zeros((*escape.shape, 3), dtype=np.float64)
    inside = escape >= (max_iter - 0.5)
    outside = ~inside
    rgb[inside] = (0.09, 0.09, 0.10)
    t = np.zeros_like(escape)
    t[outside] = np.clip(escape[outside] / float(max_iter), 0.0, 1.0)
    rgb[outside, 0] = 0.957 - 0.18 * t[outside]
    rgb[outside, 1] = 0.945 - 0.26 * t[outside]
    rgb[outside, 2] = 0.918 - 0.22 * t[outside]
    near = outside & (escape > 12)
    te = np.clip((escape[near] - 12.0) / max(1.0, max_iter - 12.0), 0, 1)
    w = te ** 0.45
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
        SF("detail zoom  ·  seahorse valley") if use_tex else "detail zoom  ·  seahorse valley",
        transform=a.transAxes, color=CREAM, fontsize=_fs(fig_w, 0.010), va="top",
        bbox=dict(boxstyle="round,pad=0.28", fc=INK, ec="none", alpha=0.62),
    )
    # scale bar-ish annotation
    a.text(
        0.98, 0.04,
        r"$\sim 10^{-2}$ in $c$-plane" if use_tex else "~0.01 in c-plane",
        transform=a.transAxes, ha="right", va="bottom", color=INK_SOFT,
        fontsize=_fs(fig_w, 0.009),
        bbox=dict(boxstyle="round,pad=0.2", fc=CREAM, ec=GRID, alpha=0.85),
    )

    ax.text(
        50, 26.5,
        IT(r"smooth escape-time  $\cdot$  self-similar filaments  $\cdot$  same $z\mapsto z^{2}+c$")
        if use_tex else "smooth escape-time  ·  self-similar filaments  ·  same quadratic map",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"A deep zoom into the Mandelbrot boundary reveals infinite filigree.",
            r"The rule is still $z\mapsto z^{2}+c$ --- complexity comes from iteration, not from the formula." if use_tex
            else "The rule is still z→z²+c — complexity comes from iteration, not from the formula.",
            r"Companion plate to the full-set portrait (classic cardioid view).",
        ],
        22.2,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$c\approx -0.744+0.132\,i$", "zoom center"),
        (r"$z_{n+1}=z_n^{2}+c$" if use_tex else r"$z_{n+1}=z_n^2+c$", "quadratic map"),
        (r"$|z|\le 2$", "escape radius"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 5. Laguerre polynomials ───────────────────────────────────────────────────

def compose_laguerre(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "POLYNOMIALS ON THE HALF-LINE",
        "FIG. 11",
        "LAGUERRE POLYNOMIALS",
        r"$xy''+(1-x)y'+ny=0$" if use_tex else r"$xy''+(1-x)y'+ny=0$",
        fig_w,
    )

    degrees = [0, 1, 2, 3, 4]
    a = _open_axes(fig, [0.10, 0.34, 0.80, 0.48], fig_w)
    x = np.linspace(0.0, 10.0, 900)
    a.set_xlim(0, 10)
    a.set_ylim(-4.2, 6.5)
    a.axhline(0, color=INK_FAINT, lw=0.55, zorder=1)
    for n in degrees:
        y = sp.eval_laguerre(n, x)
        col = LINE_DARK if n % 2 == 0 else RUST
        lw = 2.15 - 0.12 * n
        a.plot(x, y, color=col, lw=lw, solid_capstyle="round", zorder=4 + n, antialiased=True)
        # label near right edge where curve remains readable
        yi = float(y[-1])
        a.text(10.15, yi, rf"$L_{{{n}}}$", color=col, fontsize=_fs(fig_w, 0.012),
               ha="left", va="center", clip_on=False)

    a.text(
        0.5, 1.06,
        SF(r"orthogonal on $[0,\infty)$ with weight $e^{-x}$") if use_tex
        else "orthogonal on [0,∞) with weight e^{-x}",
        transform=a.transAxes, ha="center", fontsize=_fs(fig_w, 0.011), color=INK_SOFT, clip_on=False,
    )
    a.text(0.0, -0.12, r"$x$", transform=a.transAxes, ha="left",
           fontsize=_fs(fig_w, 0.010), color=INK_FAINT, clip_on=False)

    ax.text(
        50, 27.0,
        IT(r"associated Laguerre  $\cdot$  hydrogen radial  $\cdot$  Gauss–Laguerre quadrature")
        if use_tex else "associated Laguerre  ·  hydrogen radial  ·  Gauss–Laguerre quadrature",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Laguerre polynomials are orthogonal on the half-line with weight $e^{-x}$." if use_tex
            else "Laguerre polynomials are orthogonal on the half-line with weight e^{-x}.",
            r"Associated Laguerre functions build the radial hydrogen wavefunctions.",
            r"They also drive Gauss–Laguerre quadrature and exponential-decay expansions.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$L_n(x)=\sum_{k=0}^{n}\dfrac{(-1)^k}{k!}\binom{n}{k}x^{k}$"
         if use_tex else r"$L_n$ explicit sum", "Rodrigues / sum"),
        (r"$\int_0^{\infty}L_n L_m e^{-x}\,dx=\delta_{nm}$" if use_tex
         else r"$\int L_n L_m e^{-x}=\delta_{nm}$", "orthogonality"),
        (r"$R_{nl}\propto L_{n-\ell-1}^{2\ell+1}$" if use_tex else r"$R_{nl}\propto L$", "H radial link"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 6. Chebyshev polynomials ──────────────────────────────────────────────────

def compose_chebyshev(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "MINIMAX OSCILLATION",
        "FIG. 12",
        "CHEBYSHEV POLYNOMIALS",
        r"$T_n(\cos\theta)=\cos(n\theta)$" if use_tex else r"$T_n(\cos\theta)=\cos(n\theta)$",
        fig_w,
    )

    degrees = [0, 1, 2, 3, 4, 5]
    a = _open_axes(fig, [0.10, 0.34, 0.80, 0.48], fig_w)
    x = np.linspace(-1.0, 1.0, 900)
    a.set_xlim(-1.05, 1.05)
    a.set_ylim(-1.35, 1.45)
    a.axhline(0, color=INK_FAINT, lw=0.55, zorder=1)
    a.axvline(0, color=INK_FAINT, lw=0.45, zorder=1)
    a.plot([-1, -1], [-1.2, 1.2], color=LINE_DARK, lw=1.1, zorder=3)
    a.plot([1, 1], [-1.2, 1.2], color=LINE_DARK, lw=1.1, zorder=3)
    for n in degrees:
        y = sp.eval_chebyt(n, x)
        col = LINE_DARK if n % 2 == 0 else RUST
        lw = 2.0 - 0.1 * n
        a.plot(x, y, color=col, lw=lw, solid_capstyle="round", zorder=4 + n, antialiased=True)
        a.text(1.08, float(y[-1]), rf"$T_{{{n}}}$", color=col, fontsize=_fs(fig_w, 0.011),
               ha="left", va="center", clip_on=False)

    a.text(
        0.5, 1.06,
        SF(r"equioscillation  ·  best uniform approximation") if use_tex
        else "equioscillation  ·  best uniform approximation",
        transform=a.transAxes, ha="center", fontsize=_fs(fig_w, 0.011), color=INK_SOFT, clip_on=False,
    )
    a.text(0.0, -0.12, r"$x\in[-1,1]$", transform=a.transAxes, ha="left",
           fontsize=_fs(fig_w, 0.010), color=INK_FAINT, clip_on=False)

    ax.text(
        50, 27.0,
        IT(r"Clenshaw–Curtis  $\cdot$  spectral methods  $\cdot$  filter design")
        if use_tex else "Clenshaw–Curtis  ·  spectral methods  ·  filter design",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Chebyshev polynomials $T_n$ oscillate between $-1$ and $1$ with equal ripple." if use_tex
            else "Chebyshev polynomials Tn oscillate between -1 and 1 with equal ripple.",
            r"Among monic polynomials they minimize the maximum norm on $[-1,1]$." if use_tex
            else "Among monic polynomials they minimize the maximum norm on [-1,1].",
            r"Foundations of polynomial approximation, Chebyshev economization, and spectral PDE solvers.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$T_{n+1}=2xT_n-T_{n-1}$", "recurrence"),
        (r"$T_n(\cos\theta)=\cos(n\theta)$", "trig identity"),
        (r"$\|p\|_\infty\ge 2^{1-n}$" if use_tex else r"minimax bound", "minimax"),
        fig_w,
    )
    return fig_to_image(fig)


# ── 7. Airy functions ─────────────────────────────────────────────────────────

def compose_airy(width_in: float, height_in: float, dpi: int) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    fig_w = width_in
    use_tex = gep._USE_LATEX
    _header(
        ax,
        "TURNING POINTS",
        "FIG. 13",
        "AIRY FUNCTIONS",
        r"$y''-xy=0$" if use_tex else r"$y''-xy=0$",
        fig_w,
    )

    a = _open_axes(fig, [0.10, 0.34, 0.80, 0.48], fig_w)
    x = np.linspace(-12.0, 6.0, 1400)
    ai, aip, bi, bip = sp.airy(x)
    a.set_xlim(-12, 6)
    a.set_ylim(-0.65, 1.15)
    a.axhline(0, color=INK_FAINT, lw=0.55, zorder=1)
    a.axvline(0, color=INK_FAINT, lw=0.55, ls=(0, (1.2, 2)), zorder=1)
    # oscillatory region cue
    a.axvspan(-12, 0, color=RUST, alpha=0.04, zorder=0)
    a.axvspan(0, 6, color=LINE_DARK, alpha=0.03, zorder=0)
    a.plot(x, ai, color=LINE_DARK, lw=2.2, solid_capstyle="round", zorder=4, label=r"$\mathrm{Ai}$")
    a.plot(x, bi, color=RUST, lw=2.0, solid_capstyle="round", zorder=4, label=r"$\mathrm{Bi}$")
    a.text(0.12, 0.92, r"$\mathrm{Ai}(x)$", transform=a.transAxes, color=LINE_DARK,
           fontsize=_fs(fig_w, 0.014), ha="left", va="top")
    a.text(0.12, 0.82, r"$\mathrm{Bi}(x)$", transform=a.transAxes, color=RUST,
           fontsize=_fs(fig_w, 0.014), ha="left", va="top")
    a.text(0.22, 0.12, SF("oscillatory") if use_tex else "oscillatory",
           transform=a.transAxes, color=INK_SOFT, fontsize=_fs(fig_w, 0.010))
    a.text(0.72, 0.12, SF("exponential") if use_tex else "exponential",
           transform=a.transAxes, color=INK_SOFT, fontsize=_fs(fig_w, 0.010))

    ax.text(
        50, 27.0,
        IT(r"WKB connection  $\cdot$  caustics  $\cdot$  quantum turning points")
        if use_tex else "WKB connection  ·  caustics  ·  quantum turning points",
        fontsize=_fs(fig_w, 0.010), color=INK_SOFT, ha="center", zorder=5,
    )
    _caption(
        ax,
        [
            r"Airy functions solve $y''=xy$ — the model equation at a linear turning point." if use_tex
            else "Airy functions solve y''=xy — the model equation at a linear turning point.",
            r"Ai oscillates for $x<0$ and decays for $x>0$; Bi grows on the right." if use_tex
            else "Ai oscillates for x<0 and decays for x>0; Bi grows on the right.",
            r"They stitch WKB solutions across caustics in optics, quantum mechanics, and fluid edges.",
        ],
        22.5,
        fig_w,
    )
    _footer_eqs(
        ax,
        (r"$y''-xy=0$", "Airy equation"),
        (r"$\mathrm{Ai}(x),\ \mathrm{Bi}(x)$", "standard pair"),
        (r"$\mathrm{Ai}(x)\sim\dfrac{e^{-\zeta}}{2\sqrt{\pi}\,x^{1/4}}$" if use_tex
         else r"Ai asymptotic", "x→+∞"),
        fig_w,
    )
    return fig_to_image(fig)


# ── Catalog ───────────────────────────────────────────────────────────────────

@dataclass
class Design:
    slug: str
    folder: str
    concept: str
    listing_prefix: str
    tags: list[str]
    seo_title: str
    description_blurb: str
    compose: callable
    zip_name: str
    fig_theme: str


DESIGNS: list[Design] = [
    Design(
        slug="bessel_functions",
        folder="bessel_functions",
        concept="Bessel Functions",
        listing_prefix="Physics Wall Art",
        tags=[
            "physics wall art",
            "bessel function",
            "math wall art",
            "stem wall art",
            "science poster",
            "mathematics poster",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "wave equation",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Bessel Functions Print | Circular Drum Modes "
            "Jn STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Bessel functions J0, J1, J2 with zeros marked — "
            "cylindrical waves and circular drum modes. Cream graph paper, LaTeX, scipy."
        ),
        compose=compose_bessel,
        zip_name="Bessel_Functions_Physics_Wall_Art.zip",
        fig_theme="Jn curves + zeros",
    ),
    Design(
        slug="hermite_qho",
        folder="hermite_qho",
        concept="Hermite Quantum Oscillator",
        listing_prefix="Physics Wall Art",
        tags=[
            "physics wall art",
            "quantum physics art",
            "harmonic oscillator",
            "math wall art",
            "stem wall art",
            "science poster",
            "hermite polynomial",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "quantum mechanics",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Quantum Harmonic Oscillator Print | Hermite "
            "Wavefunctions STEM Science Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of quantum harmonic oscillator states n=0..3 — "
            "Hermite × Gaussian ψ and |ψ|². Energies E=ℏω(n+1/2). LaTeX + scipy."
        ),
        compose=compose_hermite,
        zip_name="Hermite_QHO_Physics_Wall_Art.zip",
        fig_theme="wavefunctions and probability",
    ),
    Design(
        slug="legendre_polynomials",
        folder="legendre_polynomials",
        concept="Legendre Polynomials",
        listing_prefix="Math Wall Art",
        tags=[
            "math wall art",
            "legendre polynomial",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "spherical harmonics",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "physics wall art",
        ],
        seo_title=(
            "Math Wall Art | Legendre Polynomials Print | Orthogonal Polynomials "
            "Spherical STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Legendre polynomials P0..P4 on [-1,1] — "
            "orthogonal basis for multipoles and spherical harmonics. LaTeX + scipy."
        ),
        compose=compose_legendre,
        zip_name="Legendre_Polynomials_Math_Wall_Art.zip",
        fig_theme="Pn family on [-1,1]",
    ),
    Design(
        slug="mandelbrot_zoom",
        folder="mandelbrot_zoom",
        concept="Mandelbrot Detail Zoom",
        listing_prefix="Math Wall Art",
        tags=[
            "math wall art",
            "mandelbrot set",
            "fractal art",
            "chaos theory",
            "mathematics poster",
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
            "Math Wall Art | Mandelbrot Zoom Print | Seahorse Valley Fractal "
            "Detail Chaos STEM Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate: deep Mandelbrot zoom (seahorse valley) with smooth "
            "escape-time coloring — companion to the classic full-set portrait."
        ),
        compose=compose_mandelbrot_zoom,
        zip_name="Mandelbrot_Zoom_Math_Wall_Art.zip",
        fig_theme="seahorse valley detail",
    ),
    Design(
        slug="laguerre_polynomials",
        folder="laguerre_polynomials",
        concept="Laguerre Polynomials",
        listing_prefix="Math Wall Art",
        tags=[
            "math wall art",
            "laguerre polynomial",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "orthogonal polynomial",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "physics wall art",
        ],
        seo_title=(
            "Math Wall Art | Laguerre Polynomials Print | Orthogonal Polynomials "
            "Half-Line STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Laguerre polynomials L0..L4 on [0,∞) — "
            "orthogonal basis for radial expansions and Gauss–Laguerre. LaTeX + scipy."
        ),
        compose=compose_laguerre,
        zip_name="Laguerre_Polynomials_Math_Wall_Art.zip",
        fig_theme="Ln family on [0,∞)",
    ),
    Design(
        slug="chebyshev_polynomials",
        folder="chebyshev_polynomials",
        concept="Chebyshev Polynomials",
        listing_prefix="Math Wall Art",
        tags=[
            "math wall art",
            "chebyshev polynomial",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "approximation theory",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "science wall art",
        ],
        seo_title=(
            "Math Wall Art | Chebyshev Polynomials Print | Minimax Approximation "
            "Tn STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Chebyshev polynomials T0..T5 — equioscillation "
            "and best uniform approximation on [-1,1]. LaTeX + scipy."
        ),
        compose=compose_chebyshev,
        zip_name="Chebyshev_Polynomials_Math_Wall_Art.zip",
        fig_theme="Tn equioscillation",
    ),
    Design(
        slug="airy_functions",
        folder="airy_functions",
        concept="Airy Functions",
        listing_prefix="Physics Wall Art",
        tags=[
            "physics wall art",
            "airy function",
            "math wall art",
            "stem wall art",
            "science poster",
            "mathematics poster",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "wave equation",
            "science wall art",
        ],
        seo_title=(
            "Physics Wall Art | Airy Functions Print | Turning Points Ai Bi "
            "STEM Mathematics Poster (Digital Download)"
        ),
        description_blurb=(
            "Scientific plate of Airy Ai and Bi — oscillatory left, exponential right. "
            "Model equation for linear turning points / WKB. LaTeX + scipy."
        ),
        compose=compose_airy,
        zip_name="Airy_Functions_Physics_Wall_Art.zip",
        fig_theme="Ai / Bi turning point",
    ),
]

# Plates for the Special Functions gallery set (NOT Mandelbrot — different product line)
SET_SLUGS = [
    "bessel_functions",
    "hermite_qho",
    "legendre_polynomials",
    "laguerre_polynomials",
    "chebyshev_polynomials",
    "airy_functions",
]


def compose_equation_card(design: Design, width_in=10.0, height_in=8.0, dpi=DPI_PREVIEW) -> Image.Image:
    fig, ax = _new_plate(width_in, height_in, dpi)
    eqs = {
        "bessel_functions": r"$J_n(x)$",
        "hermite_qho": r"$\psi_n\propto H_n e^{-\xi^{2}/2}$" if gep._USE_LATEX else r"$\psi_n\propto H_n e^{-\xi^2/2}$",
        "legendre_polynomials": r"$P_n(x)$",
        "mandelbrot_zoom": r"$z_{n+1}=z_n^{2}+c$" if gep._USE_LATEX else r"$z_{n+1}=z_n^2+c$",
        "laguerre_polynomials": r"$L_n(x)$",
        "chebyshev_polynomials": r"$T_n(x)$",
        "airy_functions": r"$\mathrm{Ai}(x),\ \mathrm{Bi}(x)$",
    }
    ax.text(50, 72, SFb(design.concept.upper()), fontsize=_fs(width_in, 0.024), color=INK, ha="center")
    ax.text(50, 52, eqs[design.slug], fontsize=_fs(width_in, 0.038), color=RUST, ha="center", va="center")
    ax.text(50, 34, SF(design.listing_prefix + "  ·  scientific plate") if gep._USE_LATEX
            else design.listing_prefix + "  ·  scientific plate",
            fontsize=_fs(width_in, 0.013), color=INK_SOFT, ha="center")
    ax.text(50, 22, SF("MathRelaxing") if gep._USE_LATEX else "MathRelaxing",
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
        "LaTeX + scipy.special",
        "",
        "Best on matte paper",
        "Instant download",
    ]
    y = 68
    for line in lines:
        ax.text(55, y, SF(line) if gep._USE_LATEX else line, fontsize=12.5, color=INK_SOFT, ha="left")
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


def build_special_functions_set(preview_only: bool = False):
    """Special Functions wall art set of 6 — distinct from Famous Equations / Field Physics."""
    by_slug = {d.slug: d for d in DESIGNS}
    designs = [by_slug[s] for s in SET_SLUGS]
    out = OUT_ROOT / "special_functions_set"
    prints = out / "prints"
    previews = out / "previews"
    out.mkdir(parents=True, exist_ok=True)
    prints.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)
    print("\n=== special_functions_set (bundle) ===")

    names = [
        "Bessel Functions",
        "Hermite / QHO",
        "Legendre Polynomials",
        "Laguerre Polynomials",
        "Chebyshev Polynomials",
        "Airy Functions",
    ]

    if not preview_only:
        for d in designs:
            src = OUT_ROOT / d.folder / "prints" / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg"
            if src.exists():
                shutil.copy2(src, prints / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg")
            else:
                print(f"  render missing single for set: {d.slug}")
                img = d.compose(12.0, 18.0, DPI_PRINT)
                save_rgb(img, prints / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg", DPI_PRINT, 90)
            src_a4 = OUT_ROOT / d.folder / "prints" / f"{d.slug}_A4_{DPI_PRINT}dpi.jpg"
            if src_a4.exists():
                shutil.copy2(src_a4, prints / f"{d.slug}_A4_{DPI_PRINT}dpi.jpg")
            else:
                img = d.compose(8.27, 11.69, DPI_PRINT)
                save_rgb(img, prints / f"{d.slug}_A4_{DPI_PRINT}dpi.jpg", DPI_PRINT, 90)

        zip_path = out / "Special_Functions_Wall_Art_Set_of_6.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "README.txt",
                """Special Functions — Wall Art Set of 6
MathRelaxing scientific plates

Six gallery prints in one download:
  1. Bessel Functions — circular drum modes Jn
  2. Hermite / Quantum Harmonic Oscillator — Hn wavefunctions
  3. Legendre Polynomials — multipoles on [-1,1]
  4. Laguerre Polynomials — half-line orthogonal basis
  5. Chebyshev Polynomials — minimax / equioscillation
  6. Airy Functions — turning points Ai & Bi

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
            print("  WARNING: near Etsy 20MB limit — drop A4 from set if needed")

    # Hero 3×2 grid
    thumbs = []
    for d in designs:
        p = OUT_ROOT / d.folder / "previews" / f"{d.slug}_preview_4_plate.jpg"
        if p.exists():
            thumbs.append(Image.open(p).convert("RGB"))
        else:
            thumbs.append(d.compose(6, 8, DPI_PREVIEW))

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
    draw.text((W // 2, 28), "SPECIAL FUNCTIONS  ·  SET OF 6", font=font, fill=(26, 26, 26), anchor="mt")
    draw.text(
        (W // 2, 62),
        "Scientific plates  ·  Bessel Hermite Legendre Laguerre Chebyshev Airy",
        font=font_s, fill=(184, 92, 56), anchor="mt",
    )
    for i, im in enumerate(thumbs[:6]):
        c, r = i % cols, i // cols
        th = im.copy()
        th.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        x = gap + c * (cell_w + gap) + (cell_w - th.width) // 2
        y = 90 + gap + r * (cell_h + gap) + (cell_h - th.height) // 2
        draw.rectangle([x - 3, y - 3, x + th.width + 3, y + th.height + 3], outline=(26, 26, 26), width=2)
        grid.paste(th, (x, y))
    side = max(W, H)
    canvas = Image.new("RGB", (side, side), (244, 241, 234))
    canvas.paste(grid, ((side - W) // 2, (side - H) // 2))
    save_rgb(canvas, previews / "special_functions_preview_1_hero.jpg", DPI_PREVIEW, 92)

    incl = Image.new("RGB", (1200, 1200), (244, 241, 234))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, 1200, 140], fill=(26, 26, 26))
    d.text((600, 50), "WHAT'S INCLUDED", font=font, fill=(244, 241, 234), anchor="mt")
    d.text((600, 95), "6 scientific plates  ·  multi-size masters", font=font_s, fill=(184, 92, 56), anchor="mt")
    y = 200
    for i, name in enumerate(names):
        d.ellipse([120, y, 200, y + 70], fill=(184, 92, 56))
        d.text((160, y + 35), str(i + 1), font=font_s, fill=(244, 241, 234), anchor="mm")
        d.text((230, y + 35), name, font=font, fill=(26, 26, 26), anchor="lm")
        y += 100
    d.text((600, 1100), "300 dpi  ·  Instant download  ·  MathRelaxing", font=font_s, fill=(85, 85, 85), anchor="mt")
    save_rgb(incl, previews / "special_functions_preview_2_included.jpg", DPI_PREVIEW, 92)

    for i, dsgn in enumerate(designs[:4]):
        eq = compose_equation_card(dsgn, 8, 6, DPI_PREVIEW)
        save_rgb(eq, previews / f"special_functions_preview_{i + 3}_eq.jpg", DPI_PREVIEW, 92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, default="")
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--set-only", action="store_true", help="Only pack the Special Functions set of 6")
    ap.add_argument("--skip-set", action="store_true")
    args = ap.parse_args()

    print("=== Special-function scientific plates (scipy) ===")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    if args.set_only:
        by_slug = {d.slug: d for d in DESIGNS}
        new_slugs = {"laguerre_polynomials", "chebyshev_polynomials", "airy_functions"}
        for slug in SET_SLUGS:
            d = by_slug[slug]
            has_print = (OUT_ROOT / d.folder / "prints" / f"{d.slug}_2x3_{DPI_PRINT}dpi.jpg").exists()
            if slug in new_slugs or not has_print:
                build_design(d, preview_only=args.preview_only)
        build_special_functions_set(preview_only=args.preview_only)
        print("\nDONE →", OUT_ROOT)
        return

    designs = DESIGNS
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        designs = [d for d in DESIGNS if d.slug in want]
        if not designs:
            raise SystemExit(f"No designs matched {want}")

    for d in designs:
        build_design(d, preview_only=args.preview_only)

    if not args.skip_set and not args.only:
        build_special_functions_set(preview_only=args.preview_only)
    elif not args.skip_set and args.only:
        # pack set if all members present or requested subset includes them
        build_special_functions_set(preview_only=args.preview_only)

    print("\nDONE →", OUT_ROOT)


if __name__ == "__main__":
    main()
