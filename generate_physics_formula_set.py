"""
generate_physics_formula_set.py — Physics Formula Poster Set of 6
=================================================================
Elegant dark-observatory scientific plates. Strict vertical zoning so
text, equations and graphics never collide:

  ┌─────────────────────────────────────┐  100
  │ HEADER  title · FIG · subtitle        │  88–100
  │ rule                                  │
  │ GRAPH  (nested axes, pad from edges)  │  28–84
  │ CAPTION  short prose                  │  20–27
  │ FOOTER  key formulae (max 3)          │   6–18
  └─────────────────────────────────────┘   0

  python generate_physics_formula_set.py
  python generate_physics_formula_set.py --preview-only
  python generate_physics_formula_set.py --only kinematics,energy
"""
from __future__ import annotations

import argparse
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "special_plates" / "physics_formula_set"

# Dark observatory (field_poster / platonic family)
BG = "#0a0c12"
PANEL = "#11141d"
LINE = "#2b3242"
INK = "#e9ecf5"
SUB = "#828aa0"
MUTED = "#5c6478"
ACC = "#6fc9d8"
GOLD = "#e8c98a"
EDGE = "#c8cdd8"

DPI_PRINT = 300
DPI_PREVIEW = 140
SIZES = {
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
    "5x7": (10.0, 14.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
}

SANS = font_manager.FontProperties(family="DejaVu Sans")
SERIF = font_manager.FontProperties(family="DejaVu Serif")
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"
plt.rcParams["axes.unicode_minus"] = False

# Zone fractions in figure height (from bottom)
Z_FOOTER_TOP = 0.18
Z_CAPTION_TOP = 0.26
Z_GRAPH_BOT = 0.28
Z_GRAPH_TOP = 0.82
Z_HEADER_BOT = 0.86


def _fs(fig_w: float, frac: float) -> float:
    return max(6.5, fig_w * 72 * frac)


def _new_fig(w: float, h: float, dpi: int):
    fig = plt.figure(figsize=(w, h), dpi=dpi, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_facecolor(BG)
    # outer frame
    ax.add_patch(
        Rectangle(
            (0.035, 0.028),
            0.93,
            0.944,
            fill=False,
            edgecolor=LINE,
            lw=0.9,
            zorder=2,
        )
    )
    # subtle corner ticks
    for (x0, y0, dx, dy) in (
        (0.035, 0.028, 0.025, 0),
        (0.035, 0.028, 0, 0.02),
        (0.965, 0.028, -0.025, 0),
        (0.965, 0.028, 0, 0.02),
        (0.035, 0.972, 0.025, 0),
        (0.035, 0.972, 0, -0.02),
        (0.965, 0.972, -0.025, 0),
        (0.965, 0.972, 0, -0.02),
    ):
        ax.plot([x0, x0 + dx], [y0, y0 + dy], color=GOLD, lw=1.0, solid_capstyle="butt", zorder=3)
    return fig, ax


def _header(ax, title: str, fig_label: str, subtitle: str, fig_w: float):
    ax.text(
        0.06,
        0.945,
        title.upper(),
        fontproperties=SANS,
        fontsize=_fs(fig_w, 0.028),
        color=INK,
        ha="left",
        va="center",
        zorder=5,
    )
    ax.text(
        0.94,
        0.945,
        fig_label,
        fontproperties=SANS,
        fontsize=_fs(fig_w, 0.012),
        color=MUTED,
        ha="right",
        va="center",
        zorder=5,
    )
    ax.text(
        0.06,
        0.905,
        subtitle,
        fontproperties=SERIF,
        fontsize=_fs(fig_w, 0.0115),
        color=GOLD,
        ha="left",
        va="center",
        zorder=5,
        style="italic",
    )
    ax.plot([0.06, 0.94], [0.875, 0.875], color=LINE, lw=0.85, zorder=4)


def _caption(ax, text: str, fig_w: float):
    # single block in caption zone — wrap manually with short lines
    ax.text(
        0.06,
        0.235,
        text,
        fontproperties=SANS,
        fontsize=_fs(fig_w, 0.0092),
        color=SUB,
        ha="left",
        va="top",
        zorder=5,
        linespacing=1.45,
    )


def _footer_eqs(ax, items: list[tuple[str, str]], fig_w: float):
    """items: list of (latex_or_mathtext, plain_label). Max 3, spaced evenly."""
    n = min(3, len(items))
    xs = [0.06, 0.50, 0.94] if n == 3 else ([0.06, 0.94] if n == 2 else [0.50])
    has = ["left", "center", "right"] if n == 3 else (["left", "right"] if n == 2 else ["center"])
    for i in range(n):
        eq, lab = items[i]
        ax.text(
            xs[i],
            0.125,
            eq,
            fontsize=_fs(fig_w, 0.014 if has[i] == "center" else 0.013),
            color=INK if has[i] == "center" else (ACC if has[i] == "right" else SUB),
            ha=has[i],
            va="center",
            zorder=5,
        )
        ax.text(
            xs[i],
            0.078,
            lab,
            fontproperties=SANS,
            fontsize=_fs(fig_w, 0.0078),
            color=MUTED,
            ha=has[i],
            va="center",
            zorder=5,
        )


def _graph_axes(fig, left=0.12, right=0.88, bot=Z_GRAPH_BOT, top=Z_GRAPH_TOP):
    """Nested axes strictly inside the graph band — no chrome on plate axes."""
    a = fig.add_axes([left, bot, right - left, top - bot], zorder=3)
    a.set_facecolor(PANEL)
    for sp in a.spines.values():
        sp.set_color(LINE)
        sp.set_linewidth(0.8)
    a.tick_params(colors=MUTED, labelsize=7, length=3, width=0.6)
    a.set_facecolor(PANEL)
    return a


def fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_rgb(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 91):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(
        str(path), "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path.name}  ({path.stat().st_size / 1024:.0f} KB)")


# ── Plate 1: Kinematics ───────────────────────────────────────────────────────

def compose_kinematics(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Kinematics", "FIG. 01", "Motion under constant acceleration", w)
    a = _graph_axes(fig)
    t = np.linspace(0, 4.0, 400)
    # s = ut + ½at² with u=0, a=1.5 → parabola
    s = 0.5 * 1.5 * t**2
    v = 1.5 * t
    a.plot(t, s, color=ACC, lw=2.0, solid_capstyle="round", label=r"$s(t)$", zorder=4)
    a.plot(t, v, color=GOLD, lw=1.6, ls="--", solid_capstyle="round", label=r"$v(t)$", zorder=4)
    a.set_xlim(0, 4.05)
    a.set_ylim(0, max(s.max(), v.max()) * 1.12)
    a.set_xlabel("time  $t$", color=MUTED, fontsize=8)
    a.set_ylabel("displacement / velocity", color=MUTED, fontsize=8)
    leg = a.legend(
        loc="upper left",
        frameon=True,
        fancybox=False,
        edgecolor=LINE,
        facecolor=BG,
        labelcolor=INK,
        fontsize=8,
        borderpad=0.5,
    )
    leg.get_frame().set_linewidth(0.6)
    a.grid(True, color=LINE, lw=0.4, alpha=0.55)
    # annotation well clear of curves (upper-right free zone)
    # annotation in free upper-right band (above both curves)
    a.text(
        3.55,
        s.max() * 1.05,
        r"$a=\mathrm{const}$",
        fontsize=9,
        color=SUB,
        ha="center",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec=LINE, lw=0.6),
        zorder=6,
        clip_on=False,
    )
    _caption(
        ax,
        "Position grows as $t^{2}$ while velocity grows linearly when acceleration is constant.\n"
        "The three equations of motion close the description of uniform accelerated motion.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$v=u+at$", "velocity"),
            (r"$s=ut+\frac{1}{2}at^{2}$", "displacement"),
            (r"$v^{2}=u^{2}+2as$", "timeless form"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Plate 2: Energy ───────────────────────────────────────────────────────────

def compose_energy(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Energy", "FIG. 02", "Mechanical energy of a vertical spring–mass", w)
    a = _graph_axes(fig)
    x = np.linspace(-1.6, 1.6, 400)
    k, m, A = 2.0, 1.0, 1.4
    omega = np.sqrt(k / m)
    # potential U = ½kx², kinetic for SHO at amplitude A: K = ½k(A²−x²)
    U = 0.5 * k * x**2
    K = 0.5 * k * (A**2 - x**2)
    K = np.clip(K, 0, None)
    E = 0.5 * k * A**2
    a.fill_between(x, 0, U, color=GOLD, alpha=0.18, zorder=2)
    a.fill_between(x, U, E, where=(K > 0), color=ACC, alpha=0.15, zorder=2)
    a.plot(x, U, color=GOLD, lw=2.0, label=r"$U=\frac{1}{2}kx^{2}$", zorder=4)
    a.plot(x, np.full_like(x, E), color=INK, lw=1.2, ls=":", label=r"$E$", zorder=3)
    a.plot([-A, A], [0, 0], color=LINE, lw=0.8, zorder=1)
    a.plot([-A, -A], [0, E], color=MUTED, lw=0.7, ls="--", zorder=2)
    a.plot([A, A], [0, E], color=MUTED, lw=0.7, ls="--", zorder=2)
    a.set_xlim(-1.75, 1.75)
    a.set_ylim(0, E * 1.22)
    a.set_xlabel("displacement  $x$", color=MUTED, fontsize=8)
    a.set_ylabel("energy", color=MUTED, fontsize=8)
    leg = a.legend(loc="upper center", frameon=True, fancybox=False, edgecolor=LINE, facecolor=BG, labelcolor=INK, fontsize=8)
    leg.get_frame().set_linewidth(0.6)
    a.grid(True, color=LINE, lw=0.4, alpha=0.5)
    # labels in free corners
    a.text(0.0, E * 0.92, r"$E=K+U$", color=INK, ha="center", va="top", fontsize=9, zorder=5)
    a.text(-1.35, E * 0.18, r"$U$", color=GOLD, fontsize=9, ha="center")
    a.text(0.0, E * 0.55, r"$K$", color=ACC, fontsize=9, ha="center")
    _caption(
        ax,
        "In the absence of dissipation, kinetic and potential energy trade places while their sum $E$ is fixed.\n"
        "The parabolic potential of a Hookean spring is the archetype of conservative forces.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$K=\frac{1}{2}mv^{2}$", "kinetic"),
            (r"$U=\frac{1}{2}kx^{2}$", "elastic potential"),
            (r"$E=K+U$", "conservation"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Plate 3: Momentum ─────────────────────────────────────────────────────────

def compose_momentum(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Momentum", "FIG. 03", "1-D elastic collision of equal masses", w)
    a = _graph_axes(fig, left=0.10, right=0.90)
    a.set_xlim(0, 10)
    a.set_ylim(0, 4)
    a.set_aspect("equal")
    a.set_xticks([])
    a.set_yticks([])
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_facecolor(PANEL)

    def ball(cx, cy, r, color, label, vx_label, side="above"):
        circ = Circle((cx, cy), r, facecolor=color, edgecolor=EDGE, lw=1.2, alpha=0.9, zorder=4)
        a.add_patch(circ)
        a.text(cx, cy, label, color=BG, ha="center", va="center", fontsize=10, fontweight="bold", zorder=5)
        ly = cy + r + 0.28 if side == "above" else cy - r - 0.28
        a.text(cx, ly, vx_label, color=SUB, ha="center", va="center", fontsize=8, zorder=5)

    # before
    a.text(2.5, 3.55, "BEFORE", color=MUTED, ha="center", fontsize=8)
    ball(1.6, 2.2, 0.45, ACC, "1", r"$v$", "above")
    ball(3.5, 2.2, 0.45, GOLD, "2", r"$0$", "above")
    a.annotate(
        "",
        xy=(2.35, 2.2),
        xytext=(1.95, 2.2),
        arrowprops=dict(arrowstyle="->", color=ACC, lw=1.4),
        zorder=6,
    )
    # divider
    a.plot([5, 5], [0.4, 3.6], color=LINE, lw=0.9, ls="--", zorder=2)
    # after equal-mass elastic: velocities exchange
    a.text(7.5, 3.55, "AFTER", color=MUTED, ha="center", fontsize=8)
    ball(6.5, 2.2, 0.45, ACC, "1", r"$0$", "above")
    ball(8.4, 2.2, 0.45, GOLD, "2", r"$v$", "above")
    a.annotate(
        "",
        xy=(9.05, 2.2),
        xytext=(8.65, 2.2),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.4),
        zorder=6,
    )
    a.text(
        5.0,
        0.7,
        r"equal mass, elastic  $\Rightarrow$  velocities exchange",
        color=SUB,
        ha="center",
        fontsize=8,
    )
    _caption(
        ax,
        "Momentum $\\mathbf{p}=m\\mathbf{v}$ is conserved when net external impulse vanishes.\n"
        "For equal masses in a 1-D elastic collision, the particles simply trade velocities.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$\mathbf{p}=m\mathbf{v}$", "momentum"),
            (r"$\sum\mathbf{p}_{i}=\mathrm{const}$", "isolation"),
            (r"$J=\int F\,dt=\Delta p$", "impulse"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Plate 4: Electromagnetism (Maxwell summary) ───────────────────────────────

def compose_maxwell(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Electromagnetism", "FIG. 04", "Maxwell’s equations in differential form", w)

    # Four elegant panels in graph zone — no overlapping text
    panels = [
        (0.08, 0.56, 0.40, 0.24, r"$\nabla\cdot\mathbf{E}=\dfrac{\rho}{\varepsilon_{0}}$", "Gauss (electric)", ACC),
        (0.52, 0.56, 0.40, 0.24, r"$\nabla\cdot\mathbf{B}=0$", "Gauss (magnetic)", GOLD),
        (0.08, 0.30, 0.40, 0.24, r"$\nabla\times\mathbf{E}=-\dfrac{\partial\mathbf{B}}{\partial t}$", "Faraday", GOLD),
        (0.52, 0.30, 0.40, 0.24, r"$\nabla\times\mathbf{B}=\mu_{0}\mathbf{J}+\mu_{0}\varepsilon_{0}\dfrac{\partial\mathbf{E}}{\partial t}$", "Ampère–Maxwell", ACC),
    ]
    for x, y, ww, hh, eq, lab, col in panels:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                ww,
                hh,
                boxstyle="round,pad=0.012,rounding_size=0.02",
                facecolor=PANEL,
                edgecolor=LINE,
                lw=0.9,
                zorder=3,
            )
        )
        # equation centered in upper 60% of card
        ax.text(
            x + ww / 2,
            y + hh * 0.58,
            eq,
            ha="center",
            va="center",
            fontsize=_fs(w, 0.0135),
            color=INK,
            zorder=5,
        )
        ax.text(
            x + ww / 2,
            y + hh * 0.18,
            lab,
            ha="center",
            va="center",
            fontproperties=SANS,
            fontsize=_fs(w, 0.0085),
            color=col,
            zorder=5,
        )

    _caption(
        ax,
        "Four equations unite electricity, magnetism, and light. Charge sources electric flux;\n"
        "there are no magnetic monopoles; changing fields generate curls — and radiation.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$c=1/\sqrt{\mu_{0}\varepsilon_{0}}$", "speed of light"),
            (r"$\mathbf{F}=q(\mathbf{E}+\mathbf{v}\times\mathbf{B})$", "Lorentz force"),
            (r"$\nabla\cdot\mathbf{B}=0$", "no monopoles"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Plate 5: Waves ────────────────────────────────────────────────────────────

def compose_waves(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Waves", "FIG. 05", "Traveling harmonic wave  ·  $y=A\\sin(kx-\\omega t)$", w)
    a = _graph_axes(fig)
    x = np.linspace(0, 4 * np.pi, 600)
    A = 1.0
    # two snapshots in time — clear phase shift, legend outside data clutter
    y0 = A * np.sin(x)
    y1 = A * np.sin(x - 0.85)
    a.plot(x, y0, color=ACC, lw=2.0, label=r"$t=0$", zorder=4)
    a.plot(x, y1, color=GOLD, lw=1.7, ls="--", label=r"$t>0$", zorder=4)
    # wavelength bracket in a quiet region (top of first crest)
    x1, x2 = np.pi / 2, np.pi / 2 + 2 * np.pi
    yb = 1.28
    a.annotate(
        "",
        xy=(x2, yb),
        xytext=(x1, yb),
        arrowprops=dict(arrowstyle="<->", color=SUB, lw=1.0),
        zorder=5,
    )
    a.text((x1 + x2) / 2, yb + 0.12, r"$\lambda$", color=SUB, ha="center", va="bottom", fontsize=10)
    # amplitude
    a.annotate(
        "",
        xy=(np.pi / 2, A),
        xytext=(np.pi / 2, 0),
        arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.9),
        zorder=5,
    )
    a.text(np.pi / 2 + 0.25, A / 2, r"$A$", color=MUTED, ha="left", va="center", fontsize=9)
    a.axhline(0, color=LINE, lw=0.7, zorder=1)
    a.set_xlim(0, 4 * np.pi)
    a.set_ylim(-1.55, 1.65)
    a.set_xlabel(r"position  $x$", color=MUTED, fontsize=8)
    a.set_ylabel(r"displacement  $y$", color=MUTED, fontsize=8)
    a.set_xticks([0, np.pi, 2 * np.pi, 3 * np.pi, 4 * np.pi])
    a.set_xticklabels([r"$0$", r"$\pi$", r"$2\pi$", r"$3\pi$", r"$4\pi$"], color=MUTED)
    leg = a.legend(loc="lower right", frameon=True, fancybox=False, edgecolor=LINE, facecolor=BG, labelcolor=INK, fontsize=8)
    leg.get_frame().set_linewidth(0.6)
    a.grid(True, color=LINE, lw=0.35, alpha=0.5)
    _caption(
        ax,
        "A pure tone is a sinusoid in space and time. Wavelength $\\lambda$, frequency $f$ and speed $v$\n"
        "are bound by $v=f\\lambda$. The same form describes sound, light envelopes, and water waves.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$v=f\lambda$", "wave speed"),
            (r"$k=2\pi/\lambda$", "wave number"),
            (r"$\omega=2\pi f$", "angular frequency"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Plate 6: Thermodynamics ───────────────────────────────────────────────────

def compose_thermo(w: float, h: float, dpi: int) -> Image.Image:
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, "Thermodynamics", "FIG. 06", "Ideal-gas isotherms on the $P$–$V$ plane", w)
    a = _graph_axes(fig)
    V = np.linspace(0.55, 4.2, 300)
    # isotherms PV = const
    for i, C in enumerate([1.2, 2.0, 3.0, 4.2]):
        P = C / V
        col = ACC if i == 2 else (GOLD if i % 2 else SUB)
        lw = 2.0 if i == 2 else 1.35
        a.plot(V, P, color=col, lw=lw, solid_capstyle="round", zorder=3 + i)
        # label at right free edge, staggered vertically
        a.text(
            4.05,
            C / 4.05,
            rf"$T_{i+1}$",
            color=col,
            fontsize=8,
            ha="left",
            va="center",
            zorder=5,
        )
    a.set_xlim(0.4, 4.5)
    a.set_ylim(0.2, 5.2)
    a.set_xlabel(r"volume  $V$", color=MUTED, fontsize=8)
    a.set_ylabel(r"pressure  $P$", color=MUTED, fontsize=8)
    a.grid(True, color=LINE, lw=0.35, alpha=0.5)
    a.text(
        1.4,
        4.5,
        r"$PV=nRT$",
        color=INK,
        fontsize=11,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec=LINE, lw=0.7),
        zorder=6,
    )
    _caption(
        ax,
        "On an ideal-gas isotherm, pressure falls as $1/V$. Higher curves are hotter.\n"
        "The first law tracks energy; the second law ranks the direction of natural change.",
        w,
    )
    _footer_eqs(
        ax,
        [
            (r"$PV=nRT$", "ideal gas"),
            (r"$\Delta U=Q-W$", "first law"),
            (r"$\Delta S\geq 0$", "second law (isolated)"),
        ],
        w,
    )
    return fig_to_image(fig)


# ── Catalog ───────────────────────────────────────────────────────────────────

@dataclass
class Plate:
    slug: str
    title: str
    compose: callable


PLATES: list[Plate] = [
    Plate("kinematics", "Kinematics", compose_kinematics),
    Plate("energy", "Energy", compose_energy),
    Plate("momentum", "Momentum", compose_momentum),
    Plate("electromagnetism", "Electromagnetism", compose_maxwell),
    Plate("waves", "Waves", compose_waves),
    Plate("thermodynamics", "Thermodynamics", compose_thermo),
]


def render_plate(plate: Plate, size_name: str, dpi: int) -> Image.Image:
    w, h = SIZES[size_name]
    return plate.compose(w, h, dpi)


def build_prints(only: set[str] | None, preview_only: bool):
    prints_dir = OUT / "prints"
    previews_dir = OUT / "previews"
    prints_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)

    plates = [p for p in PLATES if only is None or p.slug in only]
    print_paths: list[Path] = []

    for plate in plates:
        print(f"\n=== {plate.slug} ===")
        if not preview_only:
            for size in ("2x3", "A4"):
                img = render_plate(plate, size, DPI_PRINT)
                path = prints_dir / f"{plate.slug}_{size}_300dpi.jpg"
                save_rgb(img, path, DPI_PRINT)
                print_paths.append(path)
        # always a plate preview
        img = render_plate(plate, "2x3", DPI_PREVIEW)
        save_rgb(img, previews_dir / f"{plate.slug}_plate.jpg", DPI_PREVIEW, quality=88)

    return plates, print_paths


def build_set_previews(plates: list[Plate]):
    """Hero collage + included list + 4 plate crops for Etsy."""
    prev = OUT / "previews"
    prev.mkdir(parents=True, exist_ok=True)
    plate_imgs = []
    for p in plates:
        path = prev / f"{p.slug}_plate.jpg"
        if path.is_file():
            plate_imgs.append(Image.open(path).convert("RGB"))

    # 1 hero 2000×2000
    W = H = 2000
    canvas = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 52)
        font_s = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    draw.rectangle([0, 0, W, 210], fill=(8, 10, 16))
    draw.text((W // 2, 70), "PHYSICS FORMULA SET", fill=(233, 236, 245), font=font, anchor="mt")
    draw.text((W // 2, 140), "6 elegant scientific plates  ·  MathRelaxing", fill=(140, 150, 175), font=font_s, anchor="mt")

    cols, rows = 3, 2
    pad = 28
    top = 240
    gw = (W - pad * (cols + 1)) // cols
    gh = (H - top - pad * (rows + 1)) // rows
    for i, im in enumerate(plate_imgs[:6]):
        r, c = divmod(i, cols)
        x = pad + c * (gw + pad)
        y = top + pad + r * (gh + pad)
        thumb = im.copy()
        thumb.thumbnail((gw, gh), Image.Resampling.LANCZOS)
        canvas.paste(thumb, (x + (gw - thumb.width) // 2, y + (gh - thumb.height) // 2))
    hero = prev / "physics_formula_preview_1_hero.jpg"
    canvas.save(hero, quality=90)
    print(f"  wrote {hero.name}")

    # 2 included
    card = Image.new("RGB", (2000, 2000), (245, 242, 235))
    d = ImageDraw.Draw(card)
    d.text((100, 90), "What's included", fill=(20, 24, 36), font=font)
    lines = [
        "1. Kinematics — constant acceleration",
        "2. Energy — spring–mass conservation",
        "3. Momentum — elastic collision",
        "4. Electromagnetism — Maxwell’s four laws",
        "5. Waves — traveling harmonic wave",
        "6. Thermodynamics — ideal-gas isotherms",
        "",
        "Each plate: multi-ratio print files @ 300 dpi",
        "Dark observatory aesthetic · LaTeX equations",
        "Set price: $11.99",
    ]
    y = 220
    for line in lines:
        d.text((120, y), line, fill=(40, 44, 58), font=font_s)
        y += 58
    included = prev / "physics_formula_preview_2_included.jpg"
    card.save(included, quality=90)
    print(f"  wrote {included.name}")

    # 3–6 detail crops of first four plates
    for i, im in enumerate(plate_imgs[:4], start=3):
        # center crop square-ish
        tw, th = im.size
        side = min(tw, th)
        left = (tw - side) // 2
        topc = int(th * 0.12)
        crop = im.crop((left, topc, left + side, min(topc + side, th)))
        crop = crop.resize((1600, 1600), Image.Resampling.LANCZOS)
        path = prev / f"physics_formula_preview_{i}_eq.jpg"
        crop.save(path, quality=90)
        print(f"  wrote {path.name}")


def build_zip(print_paths: list[Path]):
    zpath = OUT / "Physics_Formula_Poster_Set_of_6.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        readme = (
            "MathRelaxing — Physics Formula Poster Set of 6\n"
            "=============================================\n"
            "Print-ready JPG files at 300 dpi (2×3 and A4 per design).\n"
            "Personal use only. Not for redistribution.\n"
            "https://www.etsy.com/shop/TheMathRelaxing\n"
        )
        zf.writestr("README.txt", readme)
        for p in print_paths:
            zf.write(p, f"prints/{p.name}")
    print(f"\nZIP {zpath.name} ({zpath.stat().st_size / 1024:.0f} KB)")
    return zpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--only", type=str, default="", help="comma slugs")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()} or None

    print("Physics Formula Set — elegant dark observatory plates")
    plates, print_paths = build_prints(only, args.preview_only)
    build_set_previews(plates if only is None else plates)
    if not args.preview_only and print_paths:
        build_zip(print_paths)
    print("\nDone →", OUT)


if __name__ == "__main__":
    main()
