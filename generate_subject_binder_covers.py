"""
generate_subject_binder_covers.py — STEM Subject Binder Covers (BTS digital)

Scientific-plate aesthetic (cream + navy + gold). US Letter + A4 printable covers
plus spine labels. Instant-download ZIP for Etsy.

  python generate_subject_binder_covers.py
  python generate_subject_binder_covers.py --preview-only
  python generate_subject_binder_covers.py --upload   # create Etsy draft
"""
from __future__ import annotations

import argparse
import math
import os
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from matplotlib.collections import LineCollection
from PIL import Image
from scipy import stats
from scipy.integrate import odeint  # pendulum + damped oscillator
from scipy.special import jv  # Bessel J_ν

BASE = Path(__file__).resolve().parent
OUT = BASE / "subject_binder_covers"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"
SPINES = OUT / "spines"

# Plate palette (equation-plate family)
CREAM = "#F4F1EA"
INK = "#1A1A1A"
SUB = "#555555"
GOLD = "#c9a24b"
NAVY = "#12172d"
LINE = "#C8C2B4"
TEAL = "#1A7A8A"

DPI = 300
# inches
LETTER = (8.5, 11.0)
A4 = (8.27, 11.69)

# subject_key, display title, short tag, latex formula, theme accent
SUBJECTS = [
    ("mathematics", "MATHEMATICS", "MATH", r"$e^{i\pi}+1=0$", "#1A7A8A"),
    ("algebra", "ALGEBRA", "ALG", r"$ax^{2}+bx+c=0$", "#2E5A88"),
    ("geometry", "GEOMETRY", "GEO", r"$a^{2}+b^{2}=c^{2}$", "#3D6B4F"),
    ("calculus", "CALCULUS", "CALC", r"$\dfrac{d}{dx}f(x)$", "#6B3D5C"),
    ("physics", "PHYSICS", "PHYS", r"$E=mc^{2}$", "#8B4513"),
    ("chemistry", "CHEMISTRY", "CHEM", r"$PV=nRT$", "#2F6F6F"),
    ("biology", "BIOLOGY", "BIO", r"$A{-}T,\ C{-}G$", "#3F6B3A"),
    ("computer_science", "COMPUTER SCIENCE", "CS", r"$O(n\log n)$", "#1F3A5F"),
    ("statistics", "STATISTICS", "STATS", r"$\mathcal{N}(\mu,\sigma^{2})$", "#5C4A2E"),
    ("engineering", "ENGINEERING", "ENG", r"$F=ma$", "#4A4A4A"),
    ("lab", "LAB NOTEBOOK", "LAB", r"$p\mathrm{H}=-\log_{10}[H^{+}]$", "#5A3A2A"),
    ("stem", "STEM", "STEM", r"$\nabla\cdot\mathbf{F}=\rho$", "#C9A24B"),
]


def _local_to_page(ax, cx, cy, r, u, v):
    """Map local coords in [-1,1]² (aspect equal) into page inches around (cx,cy)."""
    return cx + u * r, cy + v * r


def _draw_motif(ax, key: str, cx: float, cy: float, r: float, color: str):
    """
    Subject motifs via numpy/scipy — mathematically defined curves/fields.
    Local coordinates (u,v) live in ~[-1,1]; mapped to page inches.
    """
    def xy(u, v):
        return _local_to_page(ax, cx, cy, r, u, v)

    def plot_uv(u, v, **kw):
        X, Y = xy(np.asarray(u), np.asarray(v))
        ax.plot(X, Y, **kw)

    # ── MATHEMATICS: unit circle + rhodonea r = cos(3θ) + angle π/3 ──
    if key == "mathematics":
        th = np.linspace(0, 2 * np.pi, 500)
        plot_uv(np.cos(th), np.sin(th), color=color, lw=1.6)
        # rose r=a cos(3θ) — 3 petals when n odd
        a = 0.55
        rr = a * np.cos(3 * th)
        plot_uv(rr * np.cos(th), rr * np.sin(th), color=TEAL, lw=1.5, alpha=0.95)
        # axes
        plot_uv([-1.15, 1.15], [0, 0], color=LINE, lw=0.7)
        plot_uv([0, 0], [-1.15, 1.15], color=LINE, lw=0.7)
        theta = np.pi / 3
        plot_uv([0, np.cos(theta)], [0, np.sin(theta)], color=GOLD, lw=1.8)
        ax.scatter(*xy(np.cos(theta), np.sin(theta)), s=22, c=GOLD, zorder=5, edgecolors="none")
        # ticks every 30°
        for k in range(12):
            a0 = k * np.pi / 6
            plot_uv([0.92 * np.cos(a0), np.cos(a0)], [0.92 * np.sin(a0), np.sin(a0)],
                    color=INK, lw=1.1)

    # ── ALGEBRA: quadratic y = x² − 1 with roots ±1 and vertex ──
    elif key == "algebra":
        x = np.linspace(-1.35, 1.35, 400)
        y = x ** 2 - 1.0  # roots at ±1, vertex (0,-1)
        # scale into frame
        ys = 0.55 * y  # visual scale
        plot_uv([-1.4, 1.4], [0, 0], color=LINE, lw=0.8)
        plot_uv([0, 0], [-1.1, 1.1], color=LINE, lw=0.8)
        plot_uv(x, ys, color=color, lw=2.0)
        # mark roots and vertex
        for rx in (-1.0, 1.0):
            ax.scatter(*xy(rx, 0), s=28, c=GOLD, zorder=5, edgecolors="none")
        ax.scatter(*xy(0, 0.55 * (-1)), s=28, c=TEAL, zorder=5, edgecolors="none")
        # dashed verticals at roots
        for rx in (-1.0, 1.0):
            plot_uv([rx, rx], [-0.08, 0.08], color=GOLD, lw=1.2)

    # ── GEOMETRY: right triangle 3-4-5 with true circumcircle ──
    elif key == "geometry":
        # legs 3,4 hypotenuse 5 — scale so hypotenuse ~ 1.6 in local units
        s = 1.55 / 5.0
        A = np.array([0.0, 0.0])
        B = np.array([3.0 * s, 0.0])
        C = np.array([0.0, 4.0 * s])
        # shift to center of circumcenter (midpoint of hypotenuse for right triangle)
        mid = 0.5 * (B + C)
        A, B, C = A - mid, B - mid, C - mid
        R = np.linalg.norm(B - A)  # wait: circumradius of right triangle = hyp/2
        R = 0.5 * 5.0 * s
        for P, Q in ((A, B), (B, C), (C, A)):
            plot_uv([P[0], Q[0]], [P[1], Q[1]], color=color, lw=1.9)
        th = np.linspace(0, 2 * np.pi, 300)
        plot_uv(R * np.cos(th), R * np.sin(th), color=TEAL, lw=1.2, alpha=0.85)
        # right-angle mark at A
        leg = 0.12
        plot_uv([A[0] + leg, A[0] + leg, A[0]], [A[1], A[1] + leg, A[1] + leg],
                color=GOLD, lw=1.2)
        for P in (A, B, C):
            ax.scatter(*xy(P[0], P[1]), s=20, c=INK, zorder=5, edgecolors="none")

    # ── CALCULUS: f(x)=sin(x)e^{-x/6} and numerical derivative ──
    elif key == "calculus":
        x = np.linspace(-np.pi, np.pi, 400)
        f = np.sin(x) * np.exp(-x / 6.0)
        # central difference derivative
        df = np.gradient(f, x)
        # map x,f into local frame
        u = x / np.pi  # [-1,1]
        v_f = 0.55 * f
        v_df = 0.35 * df
        plot_uv([-1.15, 1.15], [0, 0], color=LINE, lw=0.7)
        plot_uv([0, 0], [-1.0, 1.0], color=LINE, lw=0.7)
        plot_uv(u, v_f, color=color, lw=2.0, label="f")
        plot_uv(u, v_df, color=TEAL, lw=1.4, alpha=0.9, label="f'")
        # tangent at x=0: f(0)=0, f'(0)=1
        plot_uv([-0.35, 0.35], [-0.35 * 0.35, 0.35 * 0.35], color=GOLD, lw=1.3, ls="--")

    # ── PHYSICS: pendulum phase portrait (scipy odeint) ──
    elif key == "physics":
        def pend(y, t):
            th, w = y
            return [w, -np.sin(th)]  # θ'' + sin(θ) = 0

        t = np.linspace(0, 24, 600)
        for E in np.linspace(0.2, 2.4, 7):
            # energy E = 0.5 w^2 - cos(th); start at th=0 with w=sqrt(2(E+1))
            w0 = np.sqrt(max(0.0, 2 * (E + 1.0)))
            sol = odeint(pend, [0.0, w0], t)
            th, w = sol[:, 0], sol[:, 1]
            # wrap theta lightly for display
            u = np.clip(th / np.pi, -1.2, 1.2) * 0.85
            v = np.clip(w / 3.0, -1.1, 1.1) * 0.85
            plot_uv(u, v, color=color, lw=1.0, alpha=0.75)
        # separatrix approx E=1 from th=-pi..pi
        ths = np.linspace(-np.pi, np.pi, 200)
        w_sep = np.sqrt(2 * (1 + np.cos(ths)))  # E=1 → 0.5w^2 - cos = 1 → 0.5w^2 = 1+cos
        plot_uv(0.85 * ths / np.pi, 0.85 * w_sep / 3.0, color=GOLD, lw=1.5)
        plot_uv(0.85 * ths / np.pi, -0.85 * w_sep / 3.0, color=GOLD, lw=1.5)
        plot_uv([-1.1, 1.1], [0, 0], color=LINE, lw=0.6)

    # ── CHEMISTRY: regular benzene (C6H6) hexagon + inscribed ──
    elif key == "chemistry":
        # regular hexagon vertices (bond length visual)
        ang = np.linspace(0, 2 * np.pi, 7)
        # carbon ring radius 0.75
        R = 0.78
        plot_uv(R * np.cos(ang), R * np.sin(ang), color=color, lw=2.0)
        # alternating double-bond emphasis (second hex slightly inset)
        ang2 = ang + np.pi / 6  # rotate 30° for aromatic circle convention
        # aromatic circle (Kekulé abstraction)
        th = np.linspace(0, 2 * np.pi, 200)
        plot_uv(0.42 * np.cos(th), 0.42 * np.sin(th), color=TEAL, lw=1.4)
        # H stubs outward
        for k in range(6):
            a = 2 * np.pi * k / 6
            plot_uv([R * np.cos(a), 1.05 * np.cos(a)], [R * np.sin(a), 1.05 * np.sin(a)],
                    color=color, lw=1.2)
        for k in range(6):
            a = 2 * np.pi * k / 6
            ax.scatter(*xy(R * np.cos(a), R * np.sin(a)), s=26, c=color, zorder=5, edgecolors="none")

    # ── BIOLOGY: parametric double helix (correct base-pair rungs) ──
    elif key == "biology":
        # helix: (a cos t, b t, a sin t) projected to 2D as (a cos t, b t) and phase-shifted
        t = np.linspace(0, 4 * np.pi, 500)
        a, b = 0.38, 1.0 / (4 * np.pi)  # vertical span ~1
        u1, v1 = a * np.cos(t), b * t - 0.5
        u2, v2 = a * np.cos(t + np.pi), b * t - 0.5  # opposite strand (π phase)
        plot_uv(u1, v1, color=color, lw=1.8)
        plot_uv(u2, v2, color=TEAL, lw=1.8)
        # base pairs at regular intervals (true connectors between strands)
        for k in range(0, len(t), 28):
            plot_uv([u1[k], u2[k]], [v1[k], v2[k]], color=LINE, lw=0.9, alpha=0.85)

    # ── COMPUTER SCIENCE: complete binary tree, level-order layout ──
    elif key == "computer_science":
        # nodes 1..15 (4 levels) heap indexing
        positions = {}
        for i in range(1, 16):
            level = int(math.floor(math.log2(i)))
            index_in_level = i - 2 ** level
            count_level = 2 ** level
            # u in [-1,1], v from top
            u = -1.0 + (index_in_level + 0.5) * (2.0 / count_level)
            v = 0.95 - level * 0.55
            positions[i] = (u * 0.95, v * 0.55)
        for i in range(1, 16):
            left, right = 2 * i, 2 * i + 1
            if left in positions:
                plot_uv([positions[i][0], positions[left][0]],
                        [positions[i][1], positions[left][1]], color=color, lw=1.2)
            if right in positions:
                plot_uv([positions[i][0], positions[right][0]],
                        [positions[i][1], positions[right][1]], color=color, lw=1.2)
        for i, (u, v) in positions.items():
            ax.scatter(*xy(u, v), s=32 if i == 1 else 22, c=color if i > 1 else GOLD,
                       zorder=5, edgecolors="none")

    # ── STATISTICS: scipy.stats.norm PDF + shaded ±1σ ──
    elif key == "statistics":
        x = np.linspace(-3.5, 3.5, 400)
        pdf = stats.norm.pdf(x, loc=0, scale=1)
        u = x / 3.5
        v = pdf / stats.norm.pdf(0) * 0.95  # peak ~1 local
        plot_uv([-1.1, 1.1], [0, 0], color=LINE, lw=0.7)
        plot_uv(u, v, color=color, lw=2.0)
        # shade ±1σ
        mask = (x >= -1) & (x <= 1)
        Xu, Yv = xy(u[mask], v[mask])
        base = xy(u[mask], np.zeros_like(v[mask]))[1]
        ax.fill_between(Xu, base, Yv, color=TEAL, alpha=0.25)
        for s in (-1, 0, 1):
            plot_uv([s / 3.5, s / 3.5], [0, stats.norm.pdf(s) / stats.norm.pdf(0) * 0.95],
                    color=GOLD if s != 0 else LINE, lw=1.0, ls="--" if s else "-")

    # ── ENGINEERING: damped harmonic oscillator (scipy odeint) ──
    elif key == "engineering":
        def sho(y, t, zeta=0.15, w0=1.0):
            x, v = y
            return [v, -2 * zeta * w0 * v - w0 ** 2 * x]

        t = np.linspace(0, 18, 500)
        sol = odeint(sho, [1.0, 0.0], t)
        x = sol[:, 0]
        u = (t / t[-1]) * 2 - 1  # [-1,1]
        v = 0.75 * x
        plot_uv([-1.1, 1.1], [0, 0], color=LINE, lw=0.7)
        plot_uv(u, v, color=color, lw=1.9)
        # envelope ±e^{-ζωt} (approx for underdamped)
        env = np.exp(-0.15 * t)
        plot_uv(u, 0.75 * env, color=TEAL, lw=1.0, ls="--", alpha=0.8)
        plot_uv(u, -0.75 * env, color=TEAL, lw=1.0, ls="--", alpha=0.8)

    # ── LAB: titration-like sigmoid (logistic) + equivalence mark ──
    elif key == "lab":
        # pH vs volume abstract: logistic curve (common textbook shape)
        vol = np.linspace(0, 1, 300)
        # pH = pKa + log10(progress); smooth step around equivalence
        ph = 3.5 + 7.0 / (1 + np.exp(-18 * (vol - 0.52)))
        u = vol * 2 - 1
        v = (ph - 7) / 7  # center ~0
        plot_uv([-1.1, 1.1], [0, 0], color=LINE, lw=0.6)
        plot_uv([-1.1, -1.1], [-1.0, 1.0], color=LINE, lw=0.6)  # y-axis feel
        plot_uv(u, v * 0.9, color=color, lw=2.0)
        # equivalence point
        ax.scatter(*xy(0.52 * 2 - 1, ((3.5 + 3.5) - 7) / 7 * 0.9), s=30, c=GOLD, zorder=5, edgecolors="none")
        plot_uv([0.52 * 2 - 1, 0.52 * 2 - 1], [-0.9, 0.9], color=GOLD, lw=0.9, ls=":", alpha=0.8)

    # ── STEM: Bessel J0, J1, J2 (scipy.special) ──
    else:  # stem
        x = np.linspace(0.0, 12.0, 400)
        for nu, col, lw in [(0, color, 1.8), (1, TEAL, 1.4), (2, GOLD, 1.2)]:
            y = jv(nu, x)
            u = x / 12.0 * 2 - 1
            v = 0.85 * y
            plot_uv(u, v, color=col, lw=lw, alpha=0.95)
        plot_uv([-1.1, 1.1], [0, 0], color=LINE, lw=0.7)


def render_cover(subject, size=LETTER, path: Path | None = None, dpi=DPI):
    key, title, short, formula, accent = subject
    W, H = size
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_facecolor(CREAM)
    ax.axis("off")

    # outer plate frame
    m = 0.35
    ax.add_patch(Rectangle((m, m), W - 2 * m, H - 2 * m, fill=False, ec=LINE, lw=1.4))
    ax.add_patch(Rectangle((m + 0.08, m + 0.08), W - 2 * m - 0.16, H - 2 * m - 0.16, fill=False, ec=LINE, lw=0.6))

    # top rule + label
    ax.text(W / 2, H - 0.85, "SUBJECT BINDER COVER", ha="center", va="center",
            fontsize=9, color=TEAL, fontfamily="sans-serif", fontweight="bold",
            )
    ax.plot([1.2, W - 1.2], [H - 1.15, H - 1.15], color=LINE, lw=1.0)

    # motif (larger — no footer logo reclaiming space)
    _draw_motif(ax, key, W / 2, H * 0.56, min(W, H) * 0.22, accent)

    # title
    ax.text(W / 2, H * 0.30, title, ha="center", va="center",
            fontsize=22 if len(title) < 14 else 17, color=INK,
            fontfamily="serif", fontweight="bold")
    ax.plot([W * 0.28, W * 0.72], [H * 0.255, H * 0.255], color=accent, lw=1.6)

    # formula
    ax.text(W / 2, H * 0.20, formula, ha="center", va="center", fontsize=15, color=INK)

    # school year chip (no brand logo — product is classroom-facing)
    ax.text(W / 2, H * 0.11, "2026 — 2027  ·  SCHOOL YEAR", ha="center", va="center",
            fontsize=9, color=SUB, fontfamily="sans-serif")

    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=dpi, facecolor=CREAM)
    plt.close(fig)
    return path


def render_spine(subject, path: Path, height_in=11.0, width_in=1.5, dpi=DPI):
    """Vertical spine insert for 1–2\" binders (printable strip)."""
    key, title, short, formula, accent = subject
    W, H = width_in, height_in
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_facecolor(CREAM)
    ax.axis("off")
    ax.add_patch(Rectangle((0.08, 0.15), W - 0.16, H - 0.3, fill=False, ec=LINE, lw=1.0))
    # rotated text along spine
    ax.text(W / 2, H / 2, short, ha="center", va="center", rotation=90,
            fontsize=14, fontfamily="serif", fontweight="bold", color=INK)
    ax.text(W / 2, 0.45, "26–27", ha="center", va="center", rotation=90,
            fontsize=7, color=SUB, fontfamily="sans-serif")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=CREAM)
    plt.close(fig)


def build_previews():
    """Etsy listing images from rendered letter covers."""
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    # 1 hero collage 3x4
    paths = sorted(PRINTS.glob("*_US_Letter.jpg"))
    if not paths:
        return
    imgs = [Image.open(p).convert("RGB") for p in paths[:12]]
    # resize each to same height
    th = 900
    tiles = []
    for im in imgs:
        w = int(im.width * th / im.height)
        tiles.append(im.resize((w, th), Image.Resampling.LANCZOS))
    # grid 3 cols
    cols, rows = 3, 4
    pad = 24
    tw = tiles[0].width
    W = cols * tw + (cols + 1) * pad
    H = rows * th + (rows + 1) * pad + 120
    canvas = Image.new("RGB", (W, H), (244, 241, 234))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 42)
        font_s = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    d.text((W // 2, 40), "STEM Subject Binder Covers", fill=(26, 26, 26), font=font, anchor="mt")
    d.text((W // 2, 90), "12 subjects · US Letter + A4 · printable", fill=(26, 122, 138), font=font_s, anchor="mt")
    for i, tile in enumerate(tiles[:12]):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = 120 + pad + r * (th + pad)
        canvas.paste(tile, (x, y))
    canvas.save(PREVIEWS / "01_hero_grid.jpg", quality=92)

    # 2 single close-up
    imgs[0].save(PREVIEWS / "02_detail_math.jpg", quality=92)
    # 3 second subject
    if len(imgs) > 4:
        imgs[4].save(PREVIEWS / "03_detail_physics.jpg", quality=92)
    # 4 included list card
    fig = plt.figure(figsize=(10, 8), dpi=140)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    ax.axis("off")
    ax.text(0.5, 0.92, "WHAT'S INCLUDED", ha="center", fontsize=22, fontweight="bold", color=INK)
    ax.text(0.5, 0.86, "12 STEM subject binder covers", ha="center", fontsize=13, color=TEAL)
    for i, s in enumerate(SUBJECTS):
        r, c = divmod(i, 2)
        ax.text(0.12 + c * 0.45, 0.76 - r * 0.055, f"·  {s[1].title()}", fontsize=12, color=INK)
    ax.text(0.5, 0.18, "Each cover in US Letter + A4  ·  300 DPI JPG", ha="center", fontsize=11, color=SUB)
    ax.text(0.5, 0.12, "Plus printable spine labels", ha="center", fontsize=11, color=SUB)
    ax.text(0.5, 0.05, "scientific plate style  ·  printable classroom set", ha="center", fontsize=10, color=GOLD)
    fig.savefig(PREVIEWS / "04_included.jpg", dpi=140, facecolor=CREAM)
    plt.close(fig)

    # 5 sizes note
    fig = plt.figure(figsize=(10, 8), dpi=140)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    ax.axis("off")
    ax.text(0.5, 0.75, "PRINT ATROOM-READY", ha="center", fontsize=20, fontweight="bold", color=INK)
    ax.text(0.5, 0.62, "US Letter  8.5 × 11 in", ha="center", fontsize=16, color=INK)
    ax.text(0.5, 0.54, "A4  210 × 297 mm", ha="center", fontsize=16, color=INK)
    ax.text(0.5, 0.40, "300 DPI  ·  insert in clear binder pocket", ha="center", fontsize=12, color=TEAL)
    ax.text(0.5, 0.28, "For teachers, students & homeschool", ha="center", fontsize=12, color=SUB)
    fig.savefig(PREVIEWS / "05_print_sizes.jpg", dpi=140, facecolor=CREAM)
    plt.close(fig)
    print("previews ->", PREVIEWS)


def build_zip() -> Path:
    zpath = OUT / "STEM_Subject_Binder_Covers.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PRINTS.glob("*.jpg")):
            z.write(p, f"covers/{p.name}")
        for p in sorted(SPINES.glob("*.jpg")):
            z.write(p, f"spines/{p.name}")
        z.writestr(
            "READ-ME.txt",
            "STEM SUBJECT BINDER COVERS — MathRelaxing\n"
            "========================================\n"
            "12 subjects × US Letter + A4 @ 300 DPI\n"
            "Plus spine label strips for each subject.\n\n"
            "Print at 100% scale (actual size). Insert into the clear front pocket\n"
            "of a 3-ring binder. Spine strips: trim and slide into the spine pocket.\n\n"
            "Subjects: Mathematics, Algebra, Geometry, Calculus, Physics, Chemistry,\n"
            "Biology, Computer Science, Statistics, Engineering, Lab Notebook, STEM.\n\n"
            "For personal use only. Not for redistribution or resale.\n",
        )
    print("ZIP ->", zpath, f"({zpath.stat().st_size/1e6:.2f} MB)")
    return zpath


def upload_draft(zpath: Path):
    from etsy_manager import EtsyManager

    m = EtsyManager()
    # SEO from eRank (research/binder_seo*_erank_bulk.csv):
    # primary: "printable binder covers" (avg ~127, KD 71)
    # parent: "binder covers" (~110); BTS parent: "back to school printable" (~2398)
    title = (
        "Printable Binder Covers | STEM Subject Binder Covers Math Physics Chemistry "
        "| Teacher Binder Spines | Back to School"
    )
    assert len(title) <= 140
    tags = [
        "binder covers",
        "printable binders",
        "teacher binder",
        "subject binders",
        "back to school",
        "classroom binder",
        "binder inserts",
        "math binder cover",
        "teacher printable",
        "school binder",
        "homeschool printable",
        "stem printable",
        "binder spines",
    ]
    assert all(len(t) <= 20 for t in tags), [(t, len(t)) for t in tags if len(t) > 20]
    desc = (
        "Printable binder covers for STEM subjects — a clean scientific-plate set for teacher "
        "binders, student binders, and classroom organization this back to school season.\n\n"
        "Unlike floral or cartoon covers, these subject binder covers use real math and science "
        "formulas with coordinated geometry motifs. Printable binder covers + spine labels included.\n\n"
        "WHAT YOU GET (instant download)\n"
        "• 12 STEM subject binder covers\n"
        "  Mathematics · Algebra · Geometry · Calculus · Physics · Chemistry\n"
        "  Biology · Computer Science · Statistics · Engineering · Lab · STEM\n"
        "• Each cover in US Letter (8.5×11 in) and A4\n"
        "• Matching binder spine labels / inserts\n"
        "• 300 DPI JPG — print at home or a copy shop\n\n"
        "HOW TO USE\n"
        "Print at 100% scale. Slide into the clear front pocket of a 3-ring binder. "
        "Trim spine labels for the spine pocket.\n\n"
        "Perfect for teacher binder organization, subject binders, homeschool systems, "
        "and back to school classroom setup.\n\n"
        "For personal use only. Not for redistribution or resale."
    )
    images = sorted(PREVIEWS.glob("*.jpg"))
    print("Creating Etsy DRAFT…")
    # Paper > Stationery > Templates > Planner Templates (verified in products_catalog)
    taxonomy_id = 12476
    listing_id = m.create_full_product(
        title=title,
        description=desc,
        price=4.99,
        taxonomy_id=taxonomy_id,
        image_paths=[str(p) for p in images],
        digital_file_paths=[str(zpath)],
        tags=tags,
    )
    print("listing_id", listing_id)
    return listing_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--upload", action="store_true", help="Create Etsy draft listing")
    args = ap.parse_args()

    PRINTS.mkdir(parents=True, exist_ok=True)
    SPINES.mkdir(parents=True, exist_ok=True)

    if not args.preview_only:
        print("Rendering covers…")
        for s in SUBJECTS:
            key = s[0]
            render_cover(s, LETTER, PRINTS / f"{key}_US_Letter.jpg")
            render_cover(s, A4, PRINTS / f"{key}_A4.jpg")
            render_spine(s, SPINES / f"{key}_spine.jpg")
            print(" ", s[1])
        zpath = build_zip()
    else:
        zpath = OUT / "STEM_Subject_Binder_Covers.zip"

    build_previews()
    if args.upload:
        if not zpath.is_file():
            raise SystemExit("ZIP missing — run without --preview-only first")
        upload_draft(zpath)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
