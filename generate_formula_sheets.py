"""
generate_formula_sheets.py — STEM formula reference plates (printable)
======================================================================
Four scientific-plate formula sheets. Each sheet carries its own Palette, so a
title can be re-skinned without touching the shared render/preview code:

  1. Differential & Integral Calculus   (CREAM_PAL — cream paper · rust accent)
  2. Linear Algebra                      (CREAM_PAL)
  3. Vector Calculus                     (CREAM_PAL)
  4. Physics                             (BLUEPRINT_PAL — navy blueprint · white/cyan)

Each listing: multi-ratio JPG prints (300 dpi) + PDF letter + ZIP + Etsy previews.

  python generate_formula_sheets.py
  python generate_formula_sheets.py --only calc
  python generate_formula_sheets.py --only linalg
  python generate_formula_sheets.py --only vector
  python generate_formula_sheets.py --only physics
"""
from __future__ import annotations

import argparse
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
OUT = BASE / "formula_sheets"

# Palette — match equation plates / unit circle family
CREAM = "#F4F1EA"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#3A3834"
INK_FAINT = "#6E6A63"
RUST = "#B85C38"
PANEL = "#FFFcf7"


@dataclass
class Palette:
    """All colors for one sheet's look, so sheets can be re-skinned per-title
    without touching the shared render/preview code."""
    bg: str
    grid: str
    grid_fine: str
    ink: str
    ink_soft: str
    ink_faint: str
    accent: str
    panel: str
    frame_outer: str
    frame_inner: str
    header_edge: str
    divider: str
    footer_line: str
    paper_label: str  # e.g. "Cream graph paper" / "Blueprint grid"
    # preview RGB tuples
    prev_bg: tuple          # main preview background
    prev_text: tuple        # main text on prev_bg
    prev_dark: tuple        # "what's included" contrast-card background
    prev_ink_on_dark: tuple # light text drawn on prev_dark card
    prev_card: tuple        # small card fill (preview 5)
    prev_card_edge: tuple   # small card outline
    accent_rgb: tuple
    muted_rgb: tuple


# Original cream + rust "scientific plate" (calc / linalg / vector).
CREAM_PAL = Palette(
    bg=CREAM, grid=GRID, grid_fine=GRID_FINE, ink=INK, ink_soft=INK_SOFT,
    ink_faint=INK_FAINT, accent=RUST, panel=PANEL,
    frame_outer="#D0C9BC", frame_inner="#E0DBD0", header_edge="#DDD7CC",
    divider="#D8D2C6", footer_line="#C8C2B6",
    paper_label="Cream graph paper",
    prev_bg=(244, 241, 234), prev_text=(26, 26, 26),
    prev_dark=(26, 26, 26), prev_ink_on_dark=(244, 241, 234),
    prev_card=(255, 252, 247), prev_card_edge=(230, 226, 216),
    accent_rgb=(184, 92, 56), muted_rgb=(85, 85, 85),
)

# Blueprint navy — white/cyan on deep blue, engineering-drawing feel.
BLUEPRINT_PAL = Palette(
    bg="#0E2C4E", grid="#2C4E73", grid_fine="#1E3E60",
    ink="#EAF2FB", ink_soft="#C9DDF0", ink_faint="#8FB0CE",
    accent="#67B7E8", panel="#153A61",
    frame_outer="#3A5F86", frame_inner="#264C71", header_edge="#3A5F86",
    divider="#2C4E73", footer_line="#3A5F86",
    paper_label="Blueprint grid",
    prev_bg=(14, 44, 78), prev_text=(234, 242, 251),
    prev_dark=(9, 28, 50), prev_ink_on_dark=(234, 242, 251),
    prev_card=(21, 58, 97), prev_card_edge=(58, 95, 134),
    accent_rgb=(103, 183, 232), muted_rgb=(143, 176, 206),
)

plt.rcParams.update(
    {
        "text.usetex": False,
        "mathtext.fontset": "cm",
        "mathtext.rm": "serif",
        "font.family": "serif",
        "axes.unicode_minus": False,
    }
)

DPI_PRINT = 300
DPI_PREV = 150

# print sizes for wall/desk (inches)
SIZES = {
    "letter": (8.5, 11.0),
    "A4": (8.27, 11.69),
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
}


@dataclass
class Sheet:
    slug: str
    code: str
    title: str
    subtitle: str
    plate: str
    sections: list[tuple[str, list[tuple[str, str]]]]  # (section title, [(eq, note), ...])
    palette: "Palette | None" = None  # None -> CREAM_PAL (family default)


# ── content ──────────────────────────────────────────────────────────────────

CALC = Sheet(
    slug="calculus_formula_sheet",
    code="CALC",
    title="Calculus Formula Sheet",
    subtitle="Differential & Integral Calculus  ·  Reference Plate",
    plate="PLATE C-01",
    sections=[
        (
            "Limits & Continuity",
            [
                (r"$\lim_{x\to a}f(x)=L$", "definition (informal)"),
                (r"$\lim_{x\to 0}\frac{\sin x}{x}=1$", "standard limit"),
                (r"$\lim_{x\to 0}\frac{1-\cos x}{x}=0$", "standard limit"),
                (r"$\lim_{x\to\infty}\!\left(1+\frac{1}{x}\right)^{x}=e$", "definition of e"),
            ],
        ),
        (
            "Derivatives",
            [
                # Prime notation: flatter than stacked d/dx — avoids collisions
                (r"$(x^{n})'=nx^{n-1}$", "power rule"),
                (r"$(e^{x})'=e^{x}$", "exp"),
                (r"$(\ln x)'=\frac{1}{x}$", "log"),
                (r"$(\sin x)'=\cos x$", "trig"),
                (r"$(\cos x)'=-\sin x$", "trig"),
                (r"$(\tan x)'=\sec^{2}x$", "trig"),
                (r"$(fg)'=f'g+fg'$", "product"),
                (r"$\left(\frac{f}{g}\right)'=\frac{f'g-fg'}{g^{2}}$", "quotient"),
                (r"$\left(f(g(x))\right)'=f'(g(x))\,g'(x)$", "chain rule"),
                (r"$(\arcsin x)'=\frac{1}{\sqrt{1-x^{2}}}$", "inverse trig"),
                (r"$(\arctan x)'=\frac{1}{1+x^{2}}$", "inverse trig"),
            ],
        ),
        (
            "Integrals",
            [
                # \; after integrand keeps ∫ from kissing the next glyph
                (r"$\int x^{n}\;dx=\frac{x^{n+1}}{n+1}+C\quad(n\neq -1)$", "power"),
                (r"$\int\frac{1}{x}\;dx=\ln|x|+C$", "log"),
                (r"$\int e^{x}\;dx=e^{x}+C$", "exp"),
                (r"$\int\sin x\;dx=-\cos x+C$", "trig"),
                (r"$\int\cos x\;dx=\sin x+C$", "trig"),
                (r"$\int\sec^{2}x\;dx=\tan x+C$", "trig"),
                (r"$\int\frac{1}{1+x^{2}}\;dx=\arctan x+C$", "arctan"),
                (r"$\int\frac{1}{\sqrt{1-x^{2}}}\;dx=\arcsin x+C$", "arcsin"),
                (r"$\int u\;dv=uv-\int v\;du$", "parts"),
            ],
        ),
        (
            "FTC & Applications",
            [
                (r"$\frac{d}{dx}\int_{a}^{x}f(t)\;dt=f(x)$", "FTC I"),
                (r"$\int_{a}^{b}f(x)\;dx=F(b)-F(a)$", "FTC II"),
                (r"$V=\pi\int_{a}^{b}[R(x)]^{2}\;dx$", "disk"),
                (r"$L=\int_{a}^{b}\sqrt{1+[f'(x)]^{2}}\;dx$", "arc length"),
            ],
        ),
        (
            "Series (quick)",
            [
                (r"$e^{x}=\sum_{n=0}^{\infty}\frac{x^{n}}{n!}$", "Taylor exp"),
                (r"$\sin x=\sum_{n=0}^{\infty}\frac{(-1)^{n}x^{2n+1}}{(2n+1)!}$", "Taylor sin"),
                (r"$\frac{1}{1-x}=\sum_{n=0}^{\infty}x^{n}\quad(|x|<1)$", "geometric"),
            ],
        ),
    ],
)

LINALG = Sheet(
    slug="linear_algebra_formula_sheet",
    code="LINALG",
    title="Linear Algebra Formula Sheet",
    subtitle="Vectors · Matrices · Eigenvalues  ·  Reference Plate",
    plate="PLATE LA-01",
    sections=[
        (
            "Vectors",
            [
                (r"$\mathbf{u}\cdot\mathbf{v}=\|\mathbf{u}\|\,\|\mathbf{v}\|\cos\theta$", "dot product"),
                (r"$\|\mathbf{u}\times\mathbf{v}\|=\|\mathbf{u}\|\,\|\mathbf{v}\|\sin\theta$", "cross (3D)"),
                (r"$\mathrm{proj}_{\mathbf{v}}\mathbf{u}=\dfrac{\mathbf{u}\cdot\mathbf{v}}{\mathbf{v}\cdot\mathbf{v}}\,\mathbf{v}$", "projection"),
                (r"$\|\mathbf{u}+\mathbf{v}\|^2=\|\mathbf{u}\|^2+\|\mathbf{v}\|^2+2\mathbf{u}\cdot\mathbf{v}$", "expansion"),
            ],
        ),
        (
            "Matrix Algebra",
            [
                (r"$(AB)C=A(BC),\quad A(B+C)=AB+AC$", "associative / distributive"),
                (r"$(AB)^{T}=B^{T}A^{T},\quad (AB)^{-1}=B^{-1}A^{-1}$", "transpose / inverse"),
                (r"$A\mathbf{x}=\mathbf{b}\ \Rightarrow\ \mathbf{x}=A^{-1}\mathbf{b}$", "if $A$ invertible"),
                (r"$I_n A=A I_n=A$", "identity"),
            ],
        ),
        (
            "Determinants & Inverse (2x2)",
            [
                (r"$\det A=ad-bc\quad(2\times 2)$", "2x2 det"),
                (r"$A^{-1}=\frac{1}{ad-bc}\,\mathrm{adj}(A)$", "2x2 inverse"),
                (r"$\det(AB)=\det A\cdot\det B$", "multiplicative"),
                (r"$\det(A^{T})=\det A,\quad \det(A^{-1})=1/\det A$", "properties"),
            ],
        ),
        (
            "Systems & Rank",
            [
                (r"$A\mathbf{x}=\mathbf{b}$ has solution iff $\mathbf{b}\in\mathrm{Col}(A)$", "consistency"),
                (r"$\mathrm{rank}(A)=\dim\mathrm{Col}(A)=\dim\mathrm{Row}(A)$", "rank"),
                (r"$\mathrm{nullity}(A)=n-\mathrm{rank}(A)$", "rank–nullity"),
                (r"$A$ invertible $\Leftrightarrow$ $\det A\neq 0$ $\Leftrightarrow$ full rank", "equivalences"),
            ],
        ),
        (
            "Eigenvalues",
            [
                (r"$A\mathbf{v}=\lambda\mathbf{v},\quad \mathbf{v}\neq\mathbf{0}$", "definition"),
                (r"$\det(A-\lambda I)=0$", "characteristic equation"),
                (r"$\mathrm{tr}(A)=\sum\lambda_i,\quad \det(A)=\prod\lambda_i$", "trace / det"),
                (r"$A=PDP^{-1}$ if diagonalizable", "diagonalization"),
                (r"$A^{T}A$ SPD $\Rightarrow$ real nonnegative eigenvalues", "spectral (hint)"),
            ],
        ),
        (
            "Orthogonality",
            [
                (r"$Q^{T}Q=I\ \Rightarrow\ Q^{-1}=Q^{T}$", "orthogonal matrix"),
                (r"$\|\ Q\mathbf{x}\ \|=\|\mathbf{x}\|$", "preserves length"),
            ],
        ),
    ],
)

VECTOR = Sheet(
    slug="vector_calculus_formula_sheet",
    code="VECT",
    title="Vector Calculus Formula Sheet",
    subtitle="Grad · Div · Curl · Line & Surface Integrals",
    plate="PLATE VC-01",
    sections=[
        (
            "Operators",
            [
                (r"$\nabla f=\left(\dfrac{\partial f}{\partial x},\dfrac{\partial f}{\partial y},\dfrac{\partial f}{\partial z}\right)$", "gradient"),
                (r"$\nabla\cdot\mathbf{F}=\dfrac{\partial P}{\partial x}+\dfrac{\partial Q}{\partial y}+\dfrac{\partial R}{\partial z}$", "divergence"),
                (r"$\nabla\times\mathbf{F}=\left(\partial_y R-\partial_z Q,\;\partial_z P-\partial_x R,\;\partial_x Q-\partial_y P\right)$", "curl"),
                (r"$\nabla^2 f=\nabla\cdot(\nabla f)$", "Laplacian"),
            ],
        ),
        (
            "Identities",
            [
                (r"$\nabla\times(\nabla f)=\mathbf{0}$", "curl of grad"),
                (r"$\nabla\cdot(\nabla\times\mathbf{F})=0$", "div of curl"),
                (r"$\nabla\cdot(f\mathbf{F})=f(\nabla\cdot\mathbf{F})+\nabla f\cdot\mathbf{F}$", "product"),
                (r"$\nabla\times(f\mathbf{F})=f(\nabla\times\mathbf{F})+\nabla f\times\mathbf{F}$", "product"),
            ],
        ),
        (
            "Line Integrals",
            [
                (r"$\int_{C} f\,ds=\int_{a}^{b} f(\mathbf{r}(t))\,\|\mathbf{r}'(t)\|\,dt$", "scalar"),
                (r"$\int_{C}\mathbf{F}\cdot d\mathbf{r}=\int_{a}^{b}\mathbf{F}(\mathbf{r})\cdot\mathbf{r}'\,dt$", "vector"),
                (r"$\mathbf{F}=\nabla f\Rightarrow\int_{C}\mathbf{F}\cdot d\mathbf{r}=f(B)-f(A)$", "conservative"),
            ],
        ),
        (
            "Green · Stokes · Divergence",
            [
                (r"$\oint_{\partial D}\!P\,dx+Q\,dy=\iint_{D}\!\left(\partial_{x}Q-\partial_{y}P\right)dA$", "Green"),
                (r"$\oint_{\partial S}\mathbf{F}\cdot d\mathbf{r}=\iint_{S}(\nabla\times\mathbf{F})\cdot d\mathbf{S}$", "Stokes"),
                (r"$\oiint_{\partial E}\mathbf{F}\cdot d\mathbf{S}=\iiint_{E}(\nabla\cdot\mathbf{F})\,dV$", "Divergence"),
            ],
        ),
        (
            "Surface Integrals",
            [
                (r"$\iint_{S} f\,dS=\iint_{D} f(\mathbf{r})\,\|\mathbf{r}_{u}\times\mathbf{r}_{v}\|\,du\,dv$", "scalar"),
                (r"$\iint_{S}\mathbf{F}\cdot d\mathbf{S}=\iint_{D}\mathbf{F}\cdot(\mathbf{r}_{u}\times\mathbf{r}_{v})\,du\,dv$", "flux"),
            ],
        ),
        (
            "Cylindrical / Spherical (quick)",
            [
                (r"$x=\rho\cos\theta,\ y=\rho\sin\theta,\ z=z$", "cylindrical"),
                (r"$x=\rho\sin\phi\cos\theta,\ y=\rho\sin\phi\sin\theta,\ z=\rho\cos\phi$", "spherical"),
                (r"$dV=\rho\,d\rho\,d\theta\,dz\ \ /\ \ \rho^2\sin\phi\,d\rho\,d\phi\,d\theta$", "Jacobians"),
            ],
        ),
    ],
)

PHYS = Sheet(
    slug="physics_formula_sheet",
    code="PHYS",
    title="Physics Formula Sheet",
    subtitle="Mechanics · Thermo · E&M · Waves · Modern",
    plate="PLATE PH-01",
    palette=BLUEPRINT_PAL,
    sections=[
        (
            "Mechanics",
            [
                (r"$v=v_{0}+at$", "kinematics"),
                (r"$x=x_{0}+v_{0}t+\frac{1}{2}at^{2}$", "kinematics"),
                (r"$v^{2}=v_{0}^{2}+2a\,\Delta x$", "kinematics"),
                (r"$R=\dfrac{v_{0}^{2}\sin 2\theta}{g}$", "projectile range"),
                (r"$\mathbf{F}=m\mathbf{a},\quad \sum\mathbf{F}=0$", "Newton II / equilibrium"),
                (r"$f=\mu N$", "friction"),
            ],
        ),
        (
            "Energy & Momentum",
            [
                (r"$W=Fd\cos\theta$", "work"),
                (r"$K=\frac{1}{2}mv^{2},\quad U_{g}=mgh$", "kinetic / potential"),
                (r"$U_{s}=\frac{1}{2}kx^{2}$", "spring"),
                (r"$K_{i}+U_{i}=K_{f}+U_{f}$", "conservation"),
                (r"$P=\dfrac{W}{t}=Fv$", "power"),
                (r"$\mathbf{p}=m\mathbf{v},\quad \mathbf{J}=\Delta\mathbf{p}$", "momentum / impulse"),
            ],
        ),
        (
            "Rotation & Gravity",
            [
                (r"$\tau=rF\sin\theta=I\alpha$", "torque"),
                (r"$L=I\omega,\quad K=\frac{1}{2}I\omega^{2}$", "angular"),
                (r"$v=r\omega$", "rolling"),
                (r"$a_{c}=\dfrac{v^{2}}{r}=\omega^{2}r$", "centripetal"),
                (r"$F=G\dfrac{m_{1}m_{2}}{r^{2}},\quad g=\dfrac{GM}{r^{2}}$", "gravitation"),
                (r"$T=2\pi\sqrt{\dfrac{\ell}{g}}$", "pendulum"),
            ],
        ),
        (
            "Thermodynamics",
            [
                (r"$PV=nRT$", "ideal gas"),
                (r"$Q=mc\,\Delta T$", "heat"),
                (r"$\Delta U=Q-W$", "first law"),
                (r"$\eta=1-\dfrac{T_{c}}{T_{h}}$", "Carnot"),
            ],
        ),
        (
            "Electricity & Magnetism",
            [
                (r"$F=\dfrac{1}{4\pi\epsilon_{0}}\dfrac{q_{1}q_{2}}{r^{2}}$", "Coulomb"),
                (r"$E=\dfrac{F}{q},\quad V=\dfrac{U}{q}$", "field / potential"),
                (r"$V=IR,\quad P=IV$", "Ohm / power"),
                (r"$C=\dfrac{Q}{V},\quad U=\frac{1}{2}CV^{2}$", "capacitance"),
                (r"$F=qvB\sin\theta,\quad F=BIL$", "magnetic force"),
                (r"$\varepsilon=-\dfrac{d\Phi_{B}}{dt}$", "Faraday"),
            ],
        ),
        (
            "Waves · Optics · Modern",
            [
                (r"$v=f\lambda,\quad T=\dfrac{1}{f}$", "wave / period"),
                (r"$f_{n}=\dfrac{nv}{2L}$", "harmonics"),
                (r"$\dfrac{1}{f}=\dfrac{1}{d_{o}}+\dfrac{1}{d_{i}}$", "thin lens"),
                (r"$n_{1}\sin\theta_{1}=n_{2}\sin\theta_{2}$", "Snell"),
                (r"$E=hf=\dfrac{hc}{\lambda}$", "photon"),
                (r"$E=mc^{2},\quad \lambda=\dfrac{h}{p}$", "relativity / de Broglie"),
            ],
        ),
        (
            "Constants (SI)",
            [
                (r"$c=3.00\times10^{8}\ \mathrm{m/s}$", "speed of light"),
                (r"$g=9.81\ \mathrm{m/s^{2}}$", "gravity (Earth)"),
                (r"$G=6.67\times10^{-11}\ \mathrm{N\,m^{2}/kg^{2}}$", "gravitation"),
                (r"$h=6.63\times10^{-34}\ \mathrm{J\,s}$", "Planck"),
                (r"$k_{B}=1.38\times10^{-23}\ \mathrm{J/K}$", "Boltzmann"),
            ],
        ),
    ],
)

SHEETS = {"calc": CALC, "linalg": LINALG, "vector": VECTOR, "physics": PHYS}


# ── drawing ──────────────────────────────────────────────────────────────────

def _graph_paper(ax, pal: Palette, xmin=0, xmax=100, ymin=0, ymax=100):
    for x in np.arange(xmin, xmax + 0.01, 1.25):
        ax.axvline(x, color=pal.grid_fine, lw=0.3, zorder=0)
    for y in np.arange(ymin, ymax + 0.01, 1.25):
        ax.axhline(y, color=pal.grid_fine, lw=0.3, zorder=0)
    for x in np.arange(xmin, xmax + 0.01, 5):
        ax.axvline(x, color=pal.grid, lw=0.5, zorder=0)
    for y in np.arange(ymin, ymax + 0.01, 5):
        ax.axhline(y, color=pal.grid, lw=0.5, zorder=0)


def _eq_fontsize(width_in: float, eq: str) -> float:
    """Scale equation font so dense lines stay readable without collisions."""
    base = width_in * 1.05  # slightly smaller base = more air
    if len(eq) > 70:
        return base * 0.80
    if len(eq) > 50:
        return base * 0.88
    if r"\int" in eq or r"\dfrac" in eq or r"\frac" in eq or r"\sum" in eq:
        return base * 0.94
    return base


def _data_bbox_height(ax, fig, artist) -> float:
    """Height of a text artist in data coordinates."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = artist.get_window_extent(renderer=renderer)
    # transform display → data
    inv = ax.transData.inverted()
    (x0, y0) = inv.transform((bbox.x0, bbox.y0))
    (x1, y1) = inv.transform((bbox.x1, bbox.y1))
    return abs(y1 - y0), abs(x1 - x0)


def render_sheet(sheet: Sheet, width_in: float, height_in: float, dpi: int = DPI_PRINT) -> Image.Image:
    """
    Professional two-column layout with *measured* row heights so math
    never overlaps notes or the next equation.
    """
    pal = sheet.palette or CREAM_PAL
    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=pal.bg)
    # slightly larger margins for print crop safety
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.set_facecolor(pal.bg)
    _graph_paper(ax, pal)

    # outer double frame (editorial)
    m = 3.2
    ax.add_patch(
        Rectangle((m, m), 100 - 2 * m, 100 - 2 * m, fill=False, edgecolor=pal.frame_outer, lw=1.1, zorder=1)
    )
    ax.add_patch(
        Rectangle((m + 0.7, m + 0.7), 100 - 2 * m - 1.4, 100 - 2 * m - 1.4, fill=False, edgecolor=pal.frame_inner, lw=0.5, zorder=1)
    )

    # header — clean band
    ax.add_patch(
        FancyBboxPatch(
            (5.0, 91.0), 90.0, 5.6,
            boxstyle="square,pad=0",
            facecolor=pal.panel,
            edgecolor=pal.header_edge,
            lw=0.7,
            zorder=2,
        )
    )
    # accent bar under header
    ax.add_patch(Rectangle((5.0, 90.55), 90.0, 0.38, facecolor=pal.accent, edgecolor="none", zorder=3))

    title_fs = width_in * 1.95
    ax.text(6.8, 94.55, sheet.title, fontsize=title_fs, color=pal.ink, fontweight="bold",
            va="center", ha="left", zorder=5, fontfamily="serif")
    ax.text(93.2, 94.55, sheet.plate, fontsize=width_in * 0.88, color=pal.ink_faint,
            va="center", ha="right", zorder=5, fontfamily="sans-serif")
    ax.text(6.8, 92.0, sheet.subtitle, fontsize=width_in * 0.90, color=pal.accent,
            va="center", ha="left", zorder=5, fontfamily="serif", style="italic")

    # content region
    y_top = 88.8
    y_bot = 7.2
    gutter = 50.0  # vertical split
    col_pad = 1.2

    left_box = (5.8, gutter - col_pad)   # x0, x1
    right_box = (gutter + col_pad, 94.2)

    sections = sheet.sections
    n = len(sections)
    # balance columns by item count (not section count) for even fill
    total_items = sum(len(items) for _, items in sections)
    target = total_items / 2
    left_secs, right_secs = [], []
    running = 0
    for sec in sections:
        if running < target or not left_secs:
            left_secs.append(sec)
            running += len(sec[1]) + 1  # +1 section weight
        else:
            right_secs.append(sec)

    # soft column divider
    ax.plot([gutter, gutter], [y_bot + 0.3, 89.5], color=pal.divider, lw=0.85, zorder=2)

    def draw_column(secs, x0, x1, y_start):
        """
        Draw sections with measured heights.
        Layout per row (professional, no collisions):
            [equation full column width]
            [small italic note underneath, left]
            [breathing gap]
        """
        y = y_start
        col_w = x1 - x0

        for sec_title, items in secs:
            if y < y_bot + 6:
                break

            # section header + rule
            hdr = ax.text(
                x0, y, sec_title.upper(),
                fontsize=width_in * 0.86,
                color=pal.accent,
                fontweight="bold",
                va="top",
                ha="left",
                zorder=5,
                fontfamily="sans-serif",
            )
            h_hdr, _ = _data_bbox_height(ax, fig, hdr)
            y -= h_hdr + 0.45
            ax.plot([x0, x1], [y + 0.12, y + 0.12], color=pal.accent, lw=0.7, alpha=0.75, zorder=4)
            y -= 0.85

            for eq, note in items:
                if y < y_bot + 3.2:
                    break

                fs = _eq_fontsize(width_in, eq)
                # pad left so ∫ stems never kiss the frame / previous glyphs
                t_eq = ax.text(
                    x0 + 0.55, y, eq,
                    fontsize=fs,
                    color=pal.ink,
                    va="top",
                    ha="left",
                    zorder=5,
                )
                h_eq, w_eq = _data_bbox_height(ax, fig, t_eq)

                # if equation is wider than column, shrink once and remeasure
                if w_eq > col_w - 1.2:
                    t_eq.set_fontsize(fs * 0.88)
                    h_eq, w_eq = _data_bbox_height(ax, fig, t_eq)

                # No per-line notes under equations — they caused visual clutter
                # and false "collisions". Section headers organize content.
                # (note kept in data model for future caption modes.)
                _ = note

                row_h = max(h_eq, 1.9)
                if any(tok in eq for tok in (r"\int", r"\sum", r"\frac", r"\partial", r"\iint", r"\oint", r"\oiint")):
                    gap = 1.35  # room for integral tails / fraction depth
                else:
                    gap = 1.05
                y -= row_h + gap

            y -= 1.35  # section gap
        return y

    # need an initial draw for renderer before measuring — create a dummy
    fig.canvas.draw()

    draw_column(left_secs, left_box[0], left_box[1], y_top)
    draw_column(right_secs, right_box[0], right_box[1], y_top)

    # footer
    ax.plot([6.0, 94.0], [5.9, 5.9], color=pal.footer_line, lw=0.7, zorder=5)
    ax.text(
        6.8, 4.2,
        f"{sheet.code}   ·   Formula reference   ·   Personal study use",
        fontsize=width_in * 0.72,
        color=pal.ink_faint,
        va="center",
        ha="left",
        zorder=5,
        fontfamily="sans-serif",
    )
    ax.text(
        93.2, 4.2,
        "Letter  ·  A4  ·  wall sizes in download",
        fontsize=width_in * 0.72,
        color=pal.ink_faint,
        va="center",
        ha="right",
        zorder=5,
        fontfamily="sans-serif",
    )

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_jpg(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 92):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(path), "JPEG", quality=quality, optimize=True, dpi=(dpi, dpi))
    print(f"  {path.name}  ({path.stat().st_size // 1024} KB)")


def _font(size: int, bold=False):
    cands = [
        r"C:\Windows\Fonts\georgiab.ttf" if bold else r"C:\Windows\Fonts\georgia.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in cands:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_previews(sheet: Sheet, letter_img: Image.Image, folder: Path) -> list[Path]:
    prev = folder / "previews"
    prev.mkdir(parents=True, exist_ok=True)
    paths = []
    S = 2000
    pal = sheet.palette or CREAM_PAL
    ivory, charcoal = pal.prev_bg, pal.prev_dark
    rust, muted = pal.accent_rgb, pal.muted_rgb

    # hero: page mock
    canvas = Image.new("RGB", (S, S), ivory)
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, 70), sheet.title.upper(), font=_font(28, True), fill=rust, anchor="mt")
    d.text((S // 2, 120), "Printable formula reference  ·  US Letter + wall sizes", font=_font(22), fill=muted, anchor="mt")
    # fit letter page
    pg = letter_img.copy()
    max_h = 1600
    scale = max_h / pg.height
    pg = pg.resize((int(pg.width * scale), max_h), Image.Resampling.LANCZOS)
    x = (S - pg.width) // 2
    y = 200
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([x + 12, y + 16, x + pg.width + 12, y + pg.height + 16], fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), sh).convert("RGB")
    canvas.paste(pg, (x, y))
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, S - 55), "Instant download  ·  300 dpi prints", font=_font(20), fill=muted, anchor="mt")
    p1 = prev / f"{sheet.slug}_preview_1_hero.jpg"
    canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p1, quality=92)
    paths.append(p1)

    # square crop of plate center
    sq = letter_img.copy()
    w, h = sq.size
    side = min(w, h)
    sq = sq.crop(((w - side) // 2, int(h * 0.08), (w - side) // 2 + side, int(h * 0.08) + side))
    sq = sq.resize((1500, 1500), Image.Resampling.LANCZOS)
    p2 = prev / f"{sheet.slug}_preview_2_square.jpg"
    sq.save(p2, quality=92)
    paths.append(p2)

    # detail crop (upper formulas)
    det = letter_img.copy()
    w, h = det.size
    det = det.crop((0, 0, w, int(h * 0.55))).resize((1500, int(1500 * 0.55 / 1)), Image.Resampling.LANCZOS)
    # pad to square
    canvas = Image.new("RGB", (1500, 1500), pal.prev_bg)
    canvas.paste(det, (0, (1500 - det.height) // 2))
    p3 = prev / f"{sheet.slug}_preview_3_detail.jpg"
    canvas.save(p3, quality=92)
    paths.append(p3)

    # included card
    canvas = Image.new("RGB", (S, S), charcoal)
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, 120), "What's included", font=_font(44, True), fill=pal.prev_ink_on_dark, anchor="mt")
    items = [
        "Printable formula plate (PDF-ready JPG)",
        "Multiple aspect ratios @ 300 dpi",
        "US Letter / A4 desk sizes",
        "Large wall sizes (12×18, 12×16, 16×20)",
        "Instant digital download",
    ]
    y = 320
    for it in items:
        d.rounded_rectangle([180, y, S - 180, y + 160], radius=12, outline=rust, width=2)
        d.text((260, y + 80), it, font=_font(28), fill=pal.prev_ink_on_dark, anchor="lm")
        y += 200
    p4 = prev / f"{sheet.slug}_preview_4_included.jpg"
    canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p4, quality=92)
    paths.append(p4)

    # classroom / study context text
    canvas = Image.new("RGB", (S, S), pal.prev_bg)
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, 100), "Study · Exam prep · Classroom wall", font=_font(36, True), fill=pal.prev_text, anchor="mt")
    d.line([(S // 2 - 80, 170), (S // 2 + 80, 170)], fill=rust, width=3)
    blurb = [
        "Clean scientific-plate layout",
        f"{pal.paper_label} · LaTeX-style math",
        "Grouped by topic for quick lookup",
        "Print large for the wall or letter for your desk",
    ]
    y = 280
    for b in blurb:
        d.rounded_rectangle([200, y, S - 200, y + 220], radius=14, fill=pal.prev_card, outline=pal.prev_card_edge, width=2)
        d.text((S // 2, y + 110), b, font=_font(30), fill=pal.prev_text, anchor="mm")
        y += 260
    p5 = prev / f"{sheet.slug}_preview_5_use.jpg"
    canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p5, quality=92)
    paths.append(p5)

    print(f"  {len(paths)} previews")
    return paths


def build_one(sheet: Sheet) -> dict:
    folder = OUT / sheet.slug
    prints = folder / "prints"
    prints.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {sheet.title} ===")

    # letter master for previews + pdf-ish deliverable
    letter = render_sheet(sheet, *SIZES["letter"], dpi=DPI_PRINT)
    save_jpg(letter, prints / f"{sheet.slug}_letter_300dpi.jpg")

    for name, (w, h) in SIZES.items():
        if name == "letter":
            continue
        img = render_sheet(sheet, w, h, dpi=DPI_PRINT)
        save_jpg(img, prints / f"{sheet.slug}_{name}_300dpi.jpg")

    make_previews(sheet, letter, folder)

    # ZIP
    zip_path = folder / f"{sheet.slug.replace('_', ' ').title().replace(' ', '_')}.zip"
    # cleaner name
    zip_path = folder / f"{sheet.slug}_prints.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(prints.glob("*.jpg")):
            z.write(f, f"prints/{f.name}")
        z.writestr(
            "READ_ME.txt",
            f"""{sheet.title}
{sheet.subtitle}
{sheet.plate}

INCLUDED
  prints/  — JPG masters @ 300 dpi (letter, A4, 2:3, 3:4, 4:5)

PRINTING
  · Letter / A4 for desk reference
  · Larger ratios for wall / classroom
  · Matte paper recommended

Personal study use. Not for redistribution or resale.
""",
        )
    print(f"  ZIP {zip_path.name} ({zip_path.stat().st_size // 1024} KB)")
    return {"sheet": sheet, "folder": folder, "zip": zip_path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(SHEETS.keys()), action="append")
    args = ap.parse_args()
    keys = args.only or list(SHEETS.keys())
    OUT.mkdir(parents=True, exist_ok=True)
    for k in keys:
        build_one(SHEETS[k])
    print("\nDONE →", OUT)


if __name__ == "__main__":
    main()
