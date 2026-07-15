"""
generate_schrodinger_equation.py — Schrödinger Equation scientific-plate wall art
=================================================================================
Matches the MathRelaxing physics-plate language (Maxwell, Black Hole):
  cream graph paper · bold title · rust accents · educational caption · multi-ratio ZIP

  python generate_schrodinger_equation.py
  python generate_schrodinger_equation.py --preview-only
"""
from __future__ import annotations

import argparse
import os
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "schrodinger_equation")
PRINTS = os.path.join(OUT, "prints")
PREVIEWS = os.path.join(OUT, "previews")

# Palette — match Maxwell / Black Hole plates
CREAM = "#F4F1EA"
GRID = "#E4E0D6"
INK = "#1A1A1A"
INK_SOFT = "#4A4A4A"
RUST = "#B85C38"
RUST_SOFT = "#C4785A"
LINE_DARK = "#2C2C2C"

DPI_PRINT = 300
DPI_PREVIEW = 150

# Aspect ratios Maxwell ships: 2:3, 3:4, 4:5, 5:7, ISO/A
# (width_in, height_in) portrait prints
SIZES = {
    "2x3": (12.0, 18.0),   # 2:3
    "3x4": (12.0, 16.0),   # 3:4
    "4x5": (16.0, 20.0),   # 4:5
    "5x7": (10.0, 14.0),   # 5:7
    "A4": (8.27, 11.69),   # ISO
    "A3": (11.69, 16.54),  # ISO large
}


def _draw_graph_paper(ax, xmin, xmax, ymin, ymax, step=1.0):
    """Subtle engineering-grid background (data coords)."""
    for x in np.arange(xmin, xmax + step * 0.5, step):
        ax.axvline(x, color=GRID, lw=0.55, zorder=0)
    for y in np.arange(ymin, ymax + step * 0.5, step):
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def compose_plate(width_in: float, height_in: float, dpi: int = DPI_PRINT) -> Image.Image:
    """
    Scientific plate: particle-in-a-box modes ψₙ + |ψ|² under the
    time-dependent Schrödinger equation branding.
    """
    fig_w, fig_h = width_in, height_in
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)

    # Graph paper (whole plate)
    _draw_graph_paper(ax, 0, 100, 0, 100, step=2.5)

    # Outer soft margin frame
    margin = 3.2
    ax.add_patch(
        Rectangle(
            (margin, margin),
            100 - 2 * margin,
            100 - 2 * margin,
            fill=False,
            edgecolor=GRID,
            lw=1.0,
            zorder=1,
        )
    )

    # ── Header ──────────────────────────────────────────────────────────────
    title_y = 92.5
    ax.text(
        6.5,
        title_y,
        "THE SHAPE OF PROBABILITY",
        fontsize=_fs(fig_w, 0.042),
        fontweight="bold",
        fontfamily="sans-serif",
        color=INK,
        va="center",
        ha="left",
        zorder=5,
    )
    ax.text(
        93.5,
        title_y,
        "FIG. 1",
        fontsize=_fs(fig_w, 0.018),
        fontfamily="sans-serif",
        color=INK_SOFT,
        va="center",
        ha="right",
        zorder=5,
    )

    # Subtitle line
    ax.text(
        6.5,
        88.2,
        r"SCHRÖDINGER EQUATION  ·  $i\hbar\,\partial\psi/\partial t = \hat{H}\psi$",
        fontsize=_fs(fig_w, 0.016),
        fontfamily="sans-serif",
        color=RUST,
        va="center",
        ha="left",
        zorder=5,
    )
    # Rule under header
    ax.plot([6.5, 93.5], [85.5, 85.5], color=INK, lw=0.9, solid_capstyle="butt", zorder=5)

    # ── Main diagram: infinite square well modes n=1,2,3 ────────────────────
    # Layout in plate % coords — three panels side by side
    panel_bottom = 28.0
    panel_top = 80.0
    panel_h = panel_top - panel_bottom
    gap = 2.2
    left0 = 7.5
    right0 = 92.5
    usable_w = right0 - left0
    n_panels = 3
    pw = (usable_w - gap * (n_panels - 1)) / n_panels

    L = 1.0  # well width (dimensionless)
    x = np.linspace(0, L, 400)

    modes = [
        (1, "n = 1", "ground state"),
        (2, "n = 2", "first excited"),
        (3, "n = 3", "second excited"),
    ]

    for i, (n, label, sub) in enumerate(modes):
        x0 = left0 + i * (pw + gap)
        # Panel axes as inset in figure fractions
        # Convert plate % → figure fraction (axes is full figure)
        # We'll draw in data coords of main ax using transformed local coords.

        # Local box for this panel
        bx0, by0 = x0, panel_bottom
        bw, bh = pw, panel_h

        # Subtle panel fill
        ax.add_patch(
            FancyBboxPatch(
                (bx0, by0),
                bw,
                bh,
                boxstyle="round,pad=0.15,rounding_size=0.4",
                facecolor=CREAM,
                edgecolor=GRID,
                lw=0.8,
                zorder=2,
            )
        )

        # Well walls
        wall_lw = max(1.2, fig_w * 0.06)
        y_well_bot = by0 + bh * 0.12
        y_well_top = by0 + bh * 0.78
        x_left = bx0 + bw * 0.12
        x_right = bx0 + bw * 0.88
        well_w = x_right - x_left
        well_h = y_well_top - y_well_bot

        # Floor of well
        ax.plot(
            [x_left, x_right],
            [y_well_bot, y_well_bot],
            color=LINE_DARK,
            lw=wall_lw,
            zorder=4,
        )
        # Walls
        ax.plot(
            [x_left, x_left],
            [y_well_bot, y_well_top],
            color=LINE_DARK,
            lw=wall_lw,
            zorder=4,
        )
        ax.plot(
            [x_right, x_right],
            [y_well_bot, y_well_top],
            color=LINE_DARK,
            lw=wall_lw,
            zorder=4,
        )

        # Wavefunction ψ_n(x) = √(2/L) sin(nπx/L)
        psi = np.sqrt(2.0 / L) * np.sin(n * np.pi * x / L)
        # Normalize visual amplitude to ~35% of well height
        amp = well_h * 0.38
        y_base = y_well_bot + well_h * 0.48  # center line for ψ
        xs = x_left + x * well_w
        ys = y_base + (psi / np.max(np.abs(psi))) * amp

        # |ψ|² as filled bars under zero of probability axis (bottom third of well)
        prob = psi ** 2
        prob_n = prob / np.max(prob)
        y_prob0 = y_well_bot + well_h * 0.02
        y_prob_h = well_h * 0.22

        # Draw |ψ|² as a continuous fill (probability density)
        ys_prob = y_prob0 + prob_n * y_prob_h
        ax.fill_between(
            xs,
            y_prob0,
            ys_prob,
            color=RUST,
            alpha=0.22,
            zorder=3,
            linewidth=0,
        )
        ax.plot(xs, ys_prob, color=RUST_SOFT, lw=1.0, zorder=3)

        # ψ curve
        ax.plot(xs, ys, color=LINE_DARK, lw=1.8, zorder=5, solid_capstyle="round")
        # zero line for ψ
        ax.plot(
            [x_left, x_right],
            [y_base, y_base],
            color=INK_SOFT,
            lw=0.5,
            ls=(0, (2, 2)),
            zorder=3,
            alpha=0.55,
        )

        # Labels
        ax.text(
            bx0 + bw * 0.5,
            by0 + bh * 0.92,
            label,
            fontsize=_fs(fig_w, 0.015),
            fontweight="bold",
            fontfamily="sans-serif",
            color=INK,
            ha="center",
            va="center",
            zorder=5,
        )
        ax.text(
            bx0 + bw * 0.5,
            by0 + bh * 0.86,
            sub,
            fontsize=_fs(fig_w, 0.011),
            fontfamily="sans-serif",
            color=INK_SOFT,
            ha="center",
            va="center",
            zorder=5,
        )

        # ψ and |ψ|² annotations on first panel only
        if i == 0:
            ax.text(
                x_right + bw * 0.02,
                y_base + amp * 0.55,
                r"$\psi$",
                fontsize=_fs(fig_w, 0.013),
                color=LINE_DARK,
                ha="left",
                va="center",
                zorder=5,
            )
            ax.text(
                x_right + bw * 0.02,
                y_prob0 + y_prob_h * 0.7,
                r"$|\psi|^2$",
                fontsize=_fs(fig_w, 0.011),
                color=RUST,
                ha="left",
                va="center",
                zorder=5,
            )

        # Energy label E_n ∝ n²
        ax.text(
            bx0 + bw * 0.5,
            by0 + bh * 0.05,
            rf"$E_{n} \propto n^{{2}}$",
            fontsize=_fs(fig_w, 0.012),
            fontfamily="sans-serif",
            color=RUST,
            ha="center",
            va="center",
            zorder=5,
        )

    # Well label under panels
    ax.text(
        50,
        25.5,
        "particle in a one-dimensional box  ·  infinite square well",
        fontsize=_fs(fig_w, 0.011),
        fontfamily="sans-serif",
        color=INK_SOFT,
        ha="center",
        va="center",
        style="italic",
        zorder=5,
    )

    # ── Caption ─────────────────────────────────────────────────────────────
    caption = (
        "The Schrödinger equation says a particle is a wave of probability ψ. "
        "Squaring it gives |\u03c8|\u00b2 — the chance of finding the particle at each place. "
        "In a box the allowed waves are standing modes: higher n, more nodes, higher energy."
    )
    # Manual wrap for consistent plate look
    wrapped = _wrap(caption, width=88)
    y_cap = 20.5
    for line in wrapped:
        ax.text(
            6.5,
            y_cap,
            line,
            fontsize=_fs(fig_w, 0.0125),
            fontfamily="sans-serif",
            color=INK_SOFT,
            ha="left",
            va="top",
            zorder=5,
        )
        y_cap -= 2.35

    # Key equation bottom-right
    ax.text(
        93.5,
        8.5,
        r"$i\hbar\,\partial\psi/\partial t = \hat{H}\psi$",
        fontsize=_fs(fig_w, 0.016),
        fontfamily="sans-serif",
        color=RUST,
        ha="right",
        va="center",
        zorder=5,
    )
    ax.text(
        93.5,
        6.0,
        "time-dependent form",
        fontsize=_fs(fig_w, 0.0095),
        fontfamily="sans-serif",
        color=INK_SOFT,
        ha="right",
        va="center",
        zorder=5,
    )

    # Stationary form hint bottom-left
    ax.text(
        6.5,
        8.5,
        r"$\hat{H}\psi = E\psi$",
        fontsize=_fs(fig_w, 0.014),
        fontfamily="sans-serif",
        color=INK_SOFT,
        ha="left",
        va="center",
        zorder=5,
    )
    ax.text(
        6.5,
        6.0,
        "stationary states",
        fontsize=_fs(fig_w, 0.0095),
        fontfamily="sans-serif",
        color=INK_SOFT,
        ha="left",
        va="center",
        zorder=5,
    )

    # Rasterize
    fig.canvas.draw()
    w_px, h_px = fig.canvas.get_width_height()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def _fs(fig_w_in: float, frac: float) -> float:
    """Font size in points roughly proportional to figure width."""
    return max(7.0, fig_w_in * 72 * frac)


def _wrap(text: str, width: int = 90) -> list[str]:
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = (" ".join(cur + [w])) if cur else w
        if len(trial) <= width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def save_rgb(img: Image.Image, path: str, dpi: int = DPI_PRINT, quality: int = 88):
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
        save_rgb(img, path, DPI_PRINT, quality=88)


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
        print("WARNING: ZIP near Etsy 20MB digital-file limit — lower JPEG quality.")
    return zip_path


def build_previews():
    os.makedirs(PREVIEWS, exist_ok=True)

    # 1 Hero — square-ish crop of plate branding
    print("preview 1 hero…")
    hero = compose_plate(10.0, 12.5, dpi=DPI_PREVIEW)
    # crop top branding + main diagram
    W, H = hero.size
    # full plate as hero (slightly tighter top)
    save_rgb(
        hero,
        os.path.join(PREVIEWS, "schrodinger_preview_1_hero.jpg"),
        DPI_PREVIEW,
        quality=90,
    )

    # 2 Close-up of n=2 panel area (detail)
    print("preview 2 detail…")
    detail = compose_plate(14.0, 10.0, dpi=DPI_PREVIEW)
    # center crop
    dw, dh = detail.size
    crop = detail.crop((int(dw * 0.05), int(dh * 0.18), int(dw * 0.95), int(dh * 0.78)))
    # pad to square-ish on cream
    side = max(crop.size)
    pad = Image.new("RGB", (side, side), (244, 241, 234))
    pad.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    save_rgb(
        pad,
        os.path.join(PREVIEWS, "schrodinger_preview_2_detail.jpg"),
        DPI_PREVIEW,
        quality=90,
    )

    # 3 Included / sizes card
    print("preview 3 included…")
    card_w, card_h = 10 * DPI_PREVIEW, 10 * DPI_PREVIEW
    card = Image.new("RGB", (card_w, card_h), (244, 241, 234))
    # left: mini plate
    mini = compose_plate(5.0, 7.0, dpi=DPI_PREVIEW)
    mini = mini.resize((int(card_w * 0.44), int(card_h * 0.70)), Image.Resampling.LANCZOS)
    card.paste(mini, (int(card_w * 0.05), int(card_h * 0.14)))
    # right text via matplotlib overlay
    fig = plt.figure(figsize=(10, 10), dpi=DPI_PREVIEW, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, step=2.5)
    ax.text(55, 78, "included", fontsize=28, fontweight="bold", color=INK, ha="left")
    lines = [
        "1 scientific-plate print",
        "Schrödinger equation",
        "particle-in-a-box modes",
        "",
        "Aspect ratios:",
        "2:3 · 3:4 · 4:5 · 5:7",
        "ISO A4 · A3",
        "",
        "300 dpi JPG · ZIP",
        "",
        "Best on matte paper",
        "Instant download",
    ]
    y = 68
    for line in lines:
        ax.text(55, y, line, fontsize=14, color=INK_SOFT, ha="left", fontfamily="sans-serif")
        y -= 4.2
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    base = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    # composite mini plate onto left of base
    base.paste(mini, (int(card_w * 0.05), int(card_h * 0.14)))
    save_rgb(
        base,
        os.path.join(PREVIEWS, "schrodinger_preview_3_included.jpg"),
        DPI_PREVIEW,
        quality=90,
    )

    # 4 Full plate again (listing image 4)
    print("preview 4 plate…")
    plate = compose_plate(8.0, 10.0, dpi=DPI_PREVIEW)
    save_rgb(
        plate,
        os.path.join(PREVIEWS, "schrodinger_preview_4_plate.jpg"),
        DPI_PREVIEW,
        quality=90,
    )

    # 5 Equation callout
    print("preview 5 equation…")
    fig = plt.figure(figsize=(10, 8), dpi=DPI_PREVIEW, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _draw_graph_paper(ax, 0, 100, 0, 100, step=2.5)
    ax.text(
        50,
        68,
        "THE SCHRÖDINGER EQUATION",
        fontsize=18,
        fontweight="bold",
        color=INK,
        ha="center",
        fontfamily="sans-serif",
    )
    ax.text(
        50,
        52,
        r"$i\hbar\,\dfrac{\partial\psi}{\partial t} = \hat{H}\psi$",
        fontsize=28,
        color=RUST,
        ha="center",
        va="center",
    )
    ax.text(
        50,
        36,
        "time-dependent form  ·  quantum mechanics",
        fontsize=12,
        color=INK_SOFT,
        ha="center",
        fontfamily="sans-serif",
    )
    ax.text(
        50,
        26,
        r"stationary:  $\hat{H}\psi = E\psi$",
        fontsize=14,
        color=INK_SOFT,
        ha="center",
    )
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    eq = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    save_rgb(
        eq,
        os.path.join(PREVIEWS, "schrodinger_preview_5_equation.jpg"),
        DPI_PREVIEW,
        quality=90,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    args = ap.parse_args()

    print("=== Schrödinger Equation physics plate ===")
    os.makedirs(OUT, exist_ok=True)

    if not args.preview_only:
        build_prints()
        build_zip()
    build_previews()
    print("done.")


if __name__ == "__main__":
    main()
