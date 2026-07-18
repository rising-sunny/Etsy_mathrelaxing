"""
Hero monumental posters for physical POD (Printify).
Direction B: full-width cascade / one monumental diagram, minimal type.

  Fourier  — square-wave reconstruction N=1→63
  Euler    — unit circle + e^{iθ} spiral trail
  Wave     — standing-wave modes n=1→5

  python equation_plates/generate_hero_posters.py
  python equation_plates/generate_hero_posters.py --only fourier
  python equation_plates/generate_hero_posters.py --preview-only
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent
OUT = BASE / "_hero_pod"

CREAM = "#F4F1EA"
INK = "#1A1A1A"
INK_SOFT = "#5A564E"
INK_FAINT = "#9A948A"
RUST = "#B85C38"
RUST_SOFT = "#C47858"
LINE = "#222222"

DPI = 300
# Printify ratio masters (inches) — match existing upload filenames
SIZES = {
    "2x3": (12.0, 18.0),   # 12×18 → also covers 16×24, 20×30, 24×36 via scale
    "3x4": (12.0, 16.0),   # 12×16 → 18×24, 30×40
    "4x5": (16.0, 20.0),   # 16×20 → 11×14
}

PREVIEW_SIZE = (10.0, 15.0)
PREVIEW_DPI = 140


def fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf).convert("RGB")
    plt.close(fig)
    return img


def save_jpg(img: Image.Image, path: Path, dpi: int = DPI, quality: int = 92):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=quality, dpi=(dpi, dpi), optimize=True, progressive=True)
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {path.relative_to(OUT.parent)}  ({mb:.2f} MB, {img.width}×{img.height})")


def square_partial(x: np.ndarray, n_terms: int) -> np.ndarray:
    s = np.zeros_like(x, dtype=float)
    for k in range(n_terms):
        n = 2 * k + 1
        s += np.sin(n * x) / n
    return (4.0 / np.pi) * s


def square_ideal(x: np.ndarray) -> np.ndarray:
    return np.where(np.sin(x) >= 0, 1.0, -1.0)


def standing_mode(x: np.ndarray, n: int, phase: float = 0.0) -> np.ndarray:
    """sin(n π x) * cos(phase) envelope style on [0,1]."""
    return np.sin(n * np.pi * x) * np.cos(phase)


# ── Fourier ───────────────────────────────────────────────────────────────────

def compose_fourier(w_in: float, h_in: float, dpi: int) -> Image.Image:
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi, facecolor=CREAM)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(CREAM)

    # rules
    ax.plot([0.08, 0.92], [0.955, 0.955], color=INK, lw=1.35 * (w_in / 12),
            transform=ax.transAxes, clip_on=False)
    ax.plot([0.08, 0.92], [0.055, 0.055], color=INK, lw=1.35 * (w_in / 12),
            transform=ax.transAxes, clip_on=False)

    fs_title = max(22, 48 * (w_in / 12))
    fs_eq = max(9, 15 * (w_in / 12))
    fs_body = max(8, 12 * (w_in / 12))
    fs_n = max(8, 11 * (w_in / 12))

    fig.text(0.08, 0.925, "FOURIER", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.868, "SERIES", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.812,
             r"$f_N(x)=\frac{4}{\pi}\sum_{k=0}^{N-1}\frac{\sin((2k+1)x)}{2k+1}$",
             fontsize=fs_eq, color=RUST, ha="left", va="top")

    x = np.linspace(-np.pi + 1e-4, np.pi - 1e-4, 2800)
    ideal = square_ideal(x)
    Ns = [1, 3, 7, 15, 63]
    top, bot = 0.76, 0.155
    gap = 0.016
    h_each = (top - bot - gap * (len(Ns) - 1)) / len(Ns)
    lw_base = max(1.2, 2.2 * (w_in / 12))

    for i, N in enumerate(Ns):
        y0 = top - (i + 1) * h_each - i * gap
        axp = fig.add_axes([0.08, y0, 0.74, h_each * 0.90])
        axp.set_facecolor("none")
        axp.set_xlim(-np.pi, np.pi)
        axp.set_ylim(-1.42, 1.42)
        axp.axis("off")
        s = square_partial(x, N)
        axp.plot(x, ideal, color=RUST, lw=lw_base * 0.45, alpha=0.12, ls=(0, (3, 2)), zorder=1)
        axp.fill_between(x, 0, s, color=RUST, alpha=0.11 if N < 63 else 0.15, zorder=2, lw=0)
        col = INK if N >= 7 else RUST
        lw = lw_base * (1.25 if N == 63 else 0.95)
        axp.plot(x, s, color=col, lw=lw, alpha=0.95, zorder=3, solid_capstyle="round")
        axp.axhline(0, color=INK, lw=0.4, alpha=0.12, zorder=0)
        fig.text(0.86, y0 + h_each * 0.35, f"N = {N}",
                 fontsize=fs_n * (1.1 if N == 63 else 1.0),
                 color=INK if N == 63 else (RUST if N <= 3 else INK_SOFT),
                 fontfamily="serif", ha="left", va="center",
                 fontweight="bold" if N == 63 else "normal")

    fig.text(0.08, 0.115, "Any periodic signal is a sum of pure sinusoids.",
             fontsize=fs_body, color=INK_SOFT, fontfamily="serif", ha="left")
    fig.text(0.08, 0.072, "MathRelaxing", fontsize=fs_body, color=INK,
             fontfamily="serif", ha="left")
    fig.text(0.92, 0.072, r"square wave  ·  $N\rightarrow\infty$",
             fontsize=fs_body * 0.95, color=INK_SOFT, fontfamily="serif", ha="right")
    return fig_to_image(fig)


# ── Euler ─────────────────────────────────────────────────────────────────────

def compose_euler(w_in: float, h_in: float, dpi: int) -> Image.Image:
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi, facecolor=CREAM)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(CREAM)

    lw = max(1.0, 1.3 * (w_in / 12))
    ax.plot([0.08, 0.92], [0.955, 0.955], color=INK, lw=lw, transform=ax.transAxes, clip_on=False)
    ax.plot([0.08, 0.92], [0.055, 0.055], color=INK, lw=lw, transform=ax.transAxes, clip_on=False)

    fs_title = max(22, 48 * (w_in / 12))
    fs_eq = max(11, 18 * (w_in / 12))
    fs_body = max(8, 12 * (w_in / 12))
    fs_lab = max(8, 11 * (w_in / 12))

    fig.text(0.08, 0.925, "EULER", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.868, "IDENTITY", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.812, r"$e^{i\pi}+1=0$",
             fontsize=fs_eq, color=RUST, ha="left", va="top")

    # Monumental complex plane
    a = fig.add_axes([0.12, 0.18, 0.76, 0.58])
    a.set_facecolor("none")
    a.set_aspect("equal")
    a.set_xlim(-1.75, 1.75)
    a.set_ylim(-1.55, 1.65)
    a.axis("off")

    # faint grid rings
    for r in (0.5, 1.0, 1.5):
        th = np.linspace(0, 2 * np.pi, 400)
        a.plot(r * np.cos(th), r * np.sin(th), color=INK_FAINT, lw=0.6, alpha=0.35, zorder=1)
    # axes
    a.axhline(0, color=INK_FAINT, lw=1.0, zorder=2)
    a.axvline(0, color=INK_FAINT, lw=1.0, zorder=2)
    a.annotate("", xy=(1.65, 0), xytext=(1.45, 0),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=1.1), zorder=3)
    a.annotate("", xy=(0, 1.55), xytext=(0, 1.35),
               arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=1.1), zorder=3)
    a.text(1.55, -0.18, r"$\mathrm{Re}$", color=INK_SOFT, fontsize=fs_lab)
    a.text(0.10, 1.48, r"$\mathrm{Im}$", color=INK_SOFT, fontsize=fs_lab)

    # Archimedean-ish phase trail: points e^{iθ} for θ in [0, π] with density
    th_spiral = np.linspace(0, np.pi, 120)
    # also show ghost full circle trail lightly for 0..2π
    th_full = np.linspace(0, 2 * np.pi, 500)
    a.plot(np.cos(th_full), np.sin(th_full), color=LINE, lw=max(1.5, 2.2 * w_in / 12),
           zorder=4, solid_capstyle="round")

    # filled upper semicircle (0→π)
    th_u = np.linspace(0, np.pi, 300)
    a.fill(np.concatenate([[0], np.cos(th_u), [0]]),
           np.concatenate([[0], np.sin(th_u), [0]]),
           color=RUST, alpha=0.10, zorder=3)
    a.plot(np.cos(th_u), np.sin(th_u), color=RUST, lw=max(2.0, 3.0 * w_in / 12),
           zorder=5, solid_capstyle="round")

    # ray trail: dense ticks along arc (monumental detail)
    for t in np.linspace(0, np.pi, 13):
        a.plot([0, np.cos(t)], [0, np.sin(t)], color=RUST, lw=0.55, alpha=0.18, zorder=3)

    # key points
    marks = [
        (0, r"$1$", INK, 1.18, -0.22),
        (np.pi / 2, r"$i$", INK, 0.12, 1.22),
        (np.pi, r"$-1$", RUST, -1.38, 0.16),
        (2 * np.pi / 3, r"$e^{i 2\pi/3}$", INK_SOFT, -0.55, 1.18),
        (np.pi / 3, r"$e^{i\pi/3}$", INK_SOFT, 0.72, 1.05),
    ]
    for ang, lab, col, tx, ty in marks:
        a.plot([0, np.cos(ang)], [0, np.sin(ang)], color=col, lw=1.4, zorder=6, alpha=0.85)
        a.plot(np.cos(ang), np.sin(ang), "o", color=col, ms=max(5, 7 * w_in / 12),
               zorder=7, markeredgewidth=0)
        a.text(tx, ty, lab, color=col, fontsize=fs_lab, ha="center", va="center")

    a.text(0.32, 0.14, r"$\pi$", color=RUST, fontsize=fs_lab * 1.15, ha="center")
    a.text(0.55, -0.45, r"$|z|=1$", color=INK_SOFT, fontsize=fs_lab * 0.95, ha="center")

    fig.text(0.08, 0.115, "Five constants in one identity — arithmetic meets geometry.",
             fontsize=fs_body, color=INK_SOFT, fontfamily="serif", ha="left")
    fig.text(0.08, 0.072, "MathRelaxing", fontsize=fs_body, color=INK,
             fontfamily="serif", ha="left")
    fig.text(0.92, 0.072, r"$e^{i\theta}=\cos\theta+i\sin\theta$",
             fontsize=fs_body * 0.95, color=INK_SOFT, fontfamily="serif", ha="right")
    return fig_to_image(fig)


# ── Wave equation ─────────────────────────────────────────────────────────────

def compose_wave(w_in: float, h_in: float, dpi: int) -> Image.Image:
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi, facecolor=CREAM)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(CREAM)

    lw = max(1.0, 1.3 * (w_in / 12))
    ax.plot([0.08, 0.92], [0.955, 0.955], color=INK, lw=lw, transform=ax.transAxes, clip_on=False)
    ax.plot([0.08, 0.92], [0.055, 0.055], color=INK, lw=lw, transform=ax.transAxes, clip_on=False)

    fs_title = max(20, 44 * (w_in / 12))
    fs_eq = max(9, 14 * (w_in / 12))
    fs_body = max(8, 12 * (w_in / 12))
    fs_n = max(8, 11 * (w_in / 12))

    fig.text(0.08, 0.925, "WAVE", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.868, "EQUATION", fontsize=fs_title, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.812,
             r"$\dfrac{\partial^2 u}{\partial t^2}=c^2\dfrac{\partial^2 u}{\partial x^2}$",
             fontsize=fs_eq, color=RUST, ha="left", va="top")

    # Standing modes cascade n=1..5 — each panel shows mode + ghost envelope ±
    x = np.linspace(0, 1, 2000)
    modes = [1, 2, 3, 4, 5]
    top, bot = 0.76, 0.155
    gap = 0.014
    h_each = (top - bot - gap * (len(modes) - 1)) / len(modes)
    lw_base = max(1.2, 2.1 * (w_in / 12))

    for i, n in enumerate(modes):
        y0 = top - (i + 1) * h_each - i * gap
        axp = fig.add_axes([0.10, y0, 0.70, h_each * 0.90])
        axp.set_facecolor("none")
        axp.set_xlim(0, 1)
        axp.set_ylim(-1.35, 1.35)
        axp.axis("off")
        # fixed ends
        y = standing_mode(x, n, phase=0.0)
        y2 = standing_mode(x, n, phase=np.pi)  # opposite phase ghost
        axp.fill_between(x, y2, y, color=RUST, alpha=0.10, zorder=2, lw=0)
        axp.plot(x, y, color=INK if n >= 3 else RUST, lw=lw_base * (1.15 if n == 1 else 1.0),
                 zorder=4, solid_capstyle="round")
        axp.plot(x, y2, color=RUST, lw=lw_base * 0.75, alpha=0.55, zorder=3,
                 solid_capstyle="round")
        # end posts
        axp.plot([0, 0], [-1.2, 1.2], color=INK, lw=lw_base * 0.9, zorder=5)
        axp.plot([1, 1], [-1.2, 1.2], color=INK, lw=lw_base * 0.9, zorder=5)
        axp.axhline(0, color=INK, lw=0.4, alpha=0.15, zorder=1)
        # nodes as dots
        for k in range(1, n):
            nx = k / n
            axp.plot(nx, 0, "o", color=RUST, ms=max(3, 4.5 * w_in / 12), zorder=6, markeredgewidth=0)

        fig.text(0.84, y0 + h_each * 0.35, f"n = {n}",
                 fontsize=fs_n * (1.05 if n == 1 else 1.0),
                 color=RUST if n == 1 else (INK if n >= 4 else INK_SOFT),
                 fontfamily="serif", ha="left", va="center",
                 fontweight="bold" if n in (1, 5) else "normal")

    fig.text(0.08, 0.115, "On a string fixed at both ends, only discrete modes fit.",
             fontsize=fs_body, color=INK_SOFT, fontfamily="serif", ha="left")
    fig.text(0.08, 0.072, "MathRelaxing", fontsize=fs_body, color=INK,
             fontfamily="serif", ha="left")
    fig.text(0.92, 0.072, r"$u_n=\sin(n\pi x/L)\,\cos(\omega_n t)$",
             fontsize=fs_body * 0.9, color=INK_SOFT, fontfamily="serif", ha="right")
    return fig_to_image(fig)


DESIGNS = {
    "fourier": ("fourier_series", "Fourier Series", compose_fourier),
    "euler": ("euler_identity", "Euler Identity", compose_euler),
    "wave": ("wave_equation", "Wave Equation", compose_wave),
}


def render_all(only: set[str] | None = None, preview_only: bool = False):
    OUT.mkdir(parents=True, exist_ok=True)
    keys = [k for k in DESIGNS if only is None or k in only]
    for key in keys:
        slug, title, fn = DESIGNS[key]
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {title} (hero monumental) ===")

        # listing preview
        prev = fn(*PREVIEW_SIZE, PREVIEW_DPI)
        save_jpg(prev, folder / f"{slug}_hero_preview.jpg", PREVIEW_DPI, 92)

        if preview_only:
            continue

        for size_name, (w_in, h_in) in SIZES.items():
            print(f"  rendering {size_name} @ {DPI} dpi …")
            img = fn(w_in, h_in, DPI)
            # filenames match Printify upload convention
            path = folder / f"{slug}_{size_name}_300dpi.jpg"
            save_jpg(img, path, DPI, 91)

    print("\nDONE →", OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, default="",
                    help="comma list: fourier,euler,wave")
    ap.add_argument("--preview-only", action="store_true")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()} or None
    if only:
        bad = only - set(DESIGNS)
        if bad:
            raise SystemExit(f"unknown keys: {bad}")
    render_all(only=only, preview_only=args.preview_only)


if __name__ == "__main__":
    main()
