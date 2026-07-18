"""
Three design-direction mockups for Fourier Series physical poster.
Does NOT touch Printify / production prints — preview only.

  A  plate_v2        — denser scientific plate (same family, more substance)
  B  hero_monumental — one huge diagram, minimal type
  C  blueprint_navy  — engineering/dark wall art

  python equation_plates/_fourier_direction_mockups.py
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT = Path(__file__).resolve().parent / "_direction_mockups"
OUT.mkdir(parents=True, exist_ok=True)

# ── palettes ──────────────────────────────────────────────────────────────────
CREAM = "#F4F1EA"
GRID = "#E0DBD0"
INK = "#1A1A1A"
INK_SOFT = "#5A564E"
RUST = "#B85C38"
RUST_SOFT = "#C47858"
NAVY = "#0E1628"
NAVY_MID = "#1A2740"
CYAN = "#7EB8C9"
CREAM_LINE = "#E8E2D4"
GOLD = "#C4A058"


def _font(size: int, bold: bool = False):
    windir = __import__("os").environ.get("WINDIR", r"C:\Windows")
    names = (
        ["georgia.ttf", "times.ttf", "timesbd.ttf"] if bold
        else ["georgia.ttf", "times.ttf", "arial.ttf"]
    )
    if bold:
        names = ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf", "georgia.ttf"]
    for n in names:
        p = Path(windir) / "Fonts" / n
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                pass
    return ImageFont.load_default()


def _sans(size: int, bold: bool = False):
    windir = __import__("os").environ.get("WINDIR", r"C:\Windows")
    names = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for n in names:
        p = Path(windir) / "Fonts" / n
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                pass
    return ImageFont.load_default()


def square_partial(x: np.ndarray, n_terms: int) -> np.ndarray:
    s = np.zeros_like(x, dtype=float)
    for k in range(n_terms):
        n = 2 * k + 1
        s += np.sin(n * x) / n
    return (4 / np.pi) * s


def square_ideal(x: np.ndarray) -> np.ndarray:
    return np.where(np.sin(x) >= 0, 1.0, -1.0)


def fig_to_pil(fig) -> Image.Image:
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf).convert("RGB")
    plt.close(fig)
    return img


# ── A · Plate v2 ──────────────────────────────────────────────────────────────

def mockup_plate_v2(W: int = 1400, H: int = 2100) -> Image.Image:
    """Denser scientific plate: reconstruction row + spectrum + Gibbs zoom."""
    dpi = 150
    fig_w, fig_h = W / dpi, H / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)
    fig.patch.set_facecolor(CREAM)

    # outer margins in figure coords
    # Header
    fig.text(0.07, 0.955, "THE SHAPE OF WAVES", fontsize=28, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.93, 0.955, "FIG. 1 · v2", fontsize=11, color=INK_SOFT,
             fontfamily="serif", ha="right", va="top")
    fig.text(0.07, 0.922,
             r"FOURIER SERIES  ·  $f(x)=\frac{a_0}{2}+\sum(a_n\cos nx+b_n\sin nx)$",
             fontsize=11, color=RUST, fontfamily="serif", ha="left", va="top")
    # rule
    ax_rule = fig.add_axes([0.07, 0.905, 0.86, 0.004])
    ax_rule.set_xlim(0, 1)
    ax_rule.set_ylim(0, 1)
    ax_rule.axis("off")
    ax_rule.axhline(0.5, color=INK, lw=1.6)

    x = np.linspace(-np.pi, np.pi, 1200)
    Ns = [1, 3, 7, 31]
    labels = ["N = 1", "N = 3", "N = 7", "N = 31"]

    # Row 1: four partial sums denser
    for i, (N, lab) in enumerate(zip(Ns, labels)):
        left = 0.07 + i * 0.225
        ax = fig.add_axes([left, 0.62, 0.205, 0.24])
        ax.set_facecolor(CREAM)
        # fine grid
        ax.set_xticks(np.linspace(-np.pi, np.pi, 9), minor=True)
        ax.set_yticks(np.linspace(-1.5, 1.5, 7), minor=True)
        ax.grid(True, which="minor", color=GRID, lw=0.5)
        ax.set_xlim(-np.pi, np.pi)
        ax.set_ylim(-1.55, 1.55)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.axhline(0, color=INK, lw=0.6, alpha=0.35)
        ax.axhline(1, color=RUST, lw=0.7, ls=(0, (2, 2)), alpha=0.4)
        ax.axhline(-1, color=RUST, lw=0.7, ls=(0, (2, 2)), alpha=0.4)
        s = square_partial(x, N)
        ideal = square_ideal(x)
        ax.fill_between(x, 0, s, color=RUST, alpha=0.14, zorder=2)
        ax.plot(x, ideal, color=INK, lw=0.9, alpha=0.18, zorder=1)
        ax.plot(x, s, color=INK, lw=2.0, zorder=3, solid_capstyle="round")
        ax.set_title(lab, fontsize=10, color=INK, pad=6, fontfamily="serif")

    fig.text(0.50, 0.595,
             "odd harmonics build a square wave  ·  Gibbs ringing never fully vanishes",
             fontsize=9, color=INK_SOFT, ha="center", fontfamily="serif", style="italic")

    # Row 2 left: coefficient spectrum (stem)
    ax_sp = fig.add_axes([0.07, 0.30, 0.40, 0.24])
    ax_sp.set_facecolor(CREAM)
    ax_sp.set_xticks(np.arange(0, 17, 2), minor=False)
    ax_sp.set_yticks(np.linspace(0, 1.4, 5), minor=True)
    ax_sp.grid(True, which="both", color=GRID, lw=0.5)
    ax_sp.set_xlim(0, 16.5)
    ax_sp.set_ylim(0, 1.45)
    for sp in ax_sp.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(0.8)
    ns = np.arange(1, 16, 2)
    bs = 4 / (np.pi * ns)
    ax_sp.vlines(ns, 0, bs, color=INK, lw=2.2, zorder=3)
    ax_sp.scatter(ns, bs, s=36, color=RUST, zorder=4, edgecolors="none")
    ax_sp.tick_params(labelsize=8, colors=INK_SOFT)
    ax_sp.set_xlabel(r"harmonic $n$ (odd)", fontsize=9, color=INK_SOFT, labelpad=4)
    ax_sp.set_ylabel(r"$|b_n| = 4/(n\pi)$", fontsize=9, color=INK_SOFT, labelpad=4)
    ax_sp.set_title("SPECTRUM OF ODD HARMONICS", fontsize=10, color=INK,
                    fontfamily="serif", pad=8, loc="left")

    # Row 2 right: Gibbs zoom near jump
    ax_g = fig.add_axes([0.53, 0.30, 0.40, 0.24])
    ax_g.set_facecolor(CREAM)
    ax_g.grid(True, color=GRID, lw=0.5)
    xz = np.linspace(0.05, 1.2, 800)
    for N, alpha, lw in [(7, 0.35, 1.2), (15, 0.55, 1.5), (63, 1.0, 2.0)]:
        s = square_partial(xz, N)
        ax_g.plot(xz, s, color=INK if N == 63 else RUST, lw=lw, alpha=alpha, zorder=3)
    ax_g.axhline(1, color=RUST, lw=0.8, ls=(0, (2, 2)), alpha=0.45)
    ax_g.axvline(0, color=INK, lw=0.6, alpha=0.3)
    ax_g.set_xlim(0.05, 1.2)
    ax_g.set_ylim(-0.2, 1.35)
    for sp in ax_g.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(0.8)
    ax_g.tick_params(labelsize=8, colors=INK_SOFT)
    ax_g.set_title("GIBBS PHENOMENON  ·  jump zoom", fontsize=10, color=INK,
                   fontfamily="serif", pad=8, loc="left")
    ax_g.text(0.98, 0.08, "N=7 · 15 · 63", transform=ax_g.transAxes,
              ha="right", fontsize=8, color=INK_SOFT, fontfamily="serif")

    # Formula cartouches
    boxes = [
        (0.07, r"$b_n=\dfrac{4}{n\pi}$", "odd coefficients"),
        (0.36, r"$f_N=\dfrac{4}{\pi}\sum_{k=0}^{N-1}\dfrac{\sin((2k+1)x)}{2k+1}$", "partial sum"),
        (0.70, r"$N\rightarrow\infty$", "pointwise almost everywhere"),
    ]
    for x0, math_s, cap in boxes:
        axb = fig.add_axes([x0, 0.12, 0.26, 0.12])
        axb.set_xlim(0, 1)
        axb.set_ylim(0, 1)
        axb.axis("off")
        axb.add_patch(FancyBboxPatch((0.02, 0.15), 0.96, 0.72,
                                     boxstyle="round,pad=0.02,rounding_size=0.04",
                                     facecolor="#EFEBE3", edgecolor=GRID, lw=1.0))
        axb.text(0.5, 0.58, math_s, ha="center", va="center", fontsize=11, color=INK)
        axb.text(0.5, 0.22, cap, ha="center", va="center", fontsize=8, color=RUST,
                 fontfamily="serif")

    fig.text(0.50, 0.055,
             "Any periodic signal is a sum of pure sinusoids — Fourier's idea.\n"
             "Used in audio, imaging, quantum mechanics, and every digital filter.",
             fontsize=9, color=INK_SOFT, ha="center", va="top", fontfamily="serif",
             linespacing=1.45)
    fig.text(0.50, 0.018, "MathRelaxing  ·  scientific plate study",
             fontsize=8, color=INK_SOFT, ha="center", fontfamily="serif", alpha=0.7)

    return fig_to_pil(fig)


# ── B · Hero monumental ───────────────────────────────────────────────────────

def mockup_hero_monumental(W: int = 1400, H: int = 2100) -> Image.Image:
    """One cascade of full-width reconstructions — wall presence, minimal type."""
    dpi = 150
    fig_w, fig_h = W / dpi, H / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)
    fig.patch.set_facecolor(CREAM)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(CREAM)
    ax.plot([0.08, 0.92], [0.955, 0.955], color=INK, lw=1.4, transform=ax.transAxes, clip_on=False)
    ax.plot([0.08, 0.92], [0.055, 0.055], color=INK, lw=1.4, transform=ax.transAxes, clip_on=False)

    # Monumental title
    fig.text(0.08, 0.925, "FOURIER", fontsize=48, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.868, "SERIES", fontsize=48, fontweight="bold",
             color=INK, fontfamily="serif", ha="left", va="top")
    fig.text(0.08, 0.815,
             r"$f_N(x)=\frac{4}{\pi}\sum_{k=0}^{N-1}\frac{\sin((2k+1)x)}{2k+1}$",
             fontsize=15, color=RUST, ha="left", va="top")

    x = np.linspace(-np.pi, np.pi, 2000)
    ideal = square_ideal(x)
    Ns = [1, 3, 7, 15, 63]
    # full-width cascade in lower 2/3
    top, bot = 0.76, 0.16
    gap = 0.018
    h_each = (top - bot - gap * (len(Ns) - 1)) / len(Ns)

    for i, N in enumerate(Ns):
        y0 = top - (i + 1) * h_each - i * gap
        axp = fig.add_axes([0.08, y0, 0.76, h_each * 0.90])
        axp.set_facecolor("none")
        axp.set_xlim(-np.pi, np.pi)
        axp.set_ylim(-1.45, 1.45)
        axp.axis("off")
        s = square_partial(x, N)
        # ghost ideal square
        axp.plot(x, ideal, color=RUST, lw=1.0, alpha=0.12, ls=(0, (3, 2)), zorder=1)
        axp.fill_between(x, 0, s, color=RUST, alpha=0.10 if N < 63 else 0.14, zorder=2)
        col = INK if N == 63 else (RUST if N <= 3 else INK)
        lw = 2.6 if N == 63 else (1.9 if N >= 7 else 2.1)
        axp.plot(x, s, color=col, lw=lw, alpha=0.95 if N == 63 else 0.85,
                 zorder=3, solid_capstyle="round")
        axp.axhline(0, color=INK, lw=0.5, alpha=0.15, zorder=0)
        # N label
        fig.text(0.88, y0 + h_each * 0.35, f"N = {N}",
                 fontsize=12 if N == 63 else 11,
                 color=INK if N == 63 else (RUST if N <= 3 else INK_SOFT),
                 fontfamily="serif", ha="left", va="center",
                 fontweight="bold" if N == 63 else "normal")

    fig.text(0.08, 0.12, "Any periodic signal is a sum of pure sinusoids.",
             fontsize=13, color=INK_SOFT, fontfamily="serif", ha="left")
    fig.text(0.08, 0.075, "MathRelaxing", fontsize=12, color=INK, fontfamily="serif", ha="left")
    fig.text(0.92, 0.075, "square wave  ·  N → ∞", fontsize=11, color=INK_SOFT,
             fontfamily="serif", ha="right")

    return fig_to_pil(fig)


# ── C · Blueprint navy ────────────────────────────────────────────────────────

def mockup_blueprint_navy(W: int = 1400, H: int = 2100) -> Image.Image:
    """Engineering blueprint aesthetic — navy field, cyan/cream ink."""
    dpi = 150
    fig_w, fig_h = W / dpi, H / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=NAVY)
    fig.patch.set_facecolor(NAVY)

    # blueprint grid
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis("off")
    ax_bg.set_facecolor(NAVY)
    for x in np.linspace(0.04, 0.96, 25):
        ax_bg.axvline(x, color=NAVY_MID, lw=0.6, alpha=0.9)
    for y in np.linspace(0.04, 0.96, 37):
        ax_bg.axhline(y, color=NAVY_MID, lw=0.6, alpha=0.9)
    # major grid
    for x in np.linspace(0.04, 0.96, 7):
        ax_bg.axvline(x, color="#243352", lw=1.0, alpha=0.8)
    for y in np.linspace(0.04, 0.96, 10):
        ax_bg.axhline(y, color="#243352", lw=1.0, alpha=0.8)

    # title block (blueprint style)
    fig.text(0.07, 0.94, "MATHRELAXING  ·  ANALYTIC DRAWING",
             fontsize=9, color=CYAN, fontfamily="sans-serif", ha="left",
             fontweight="bold", alpha=0.85)
    fig.text(0.07, 0.90, "FOURIER SERIES",
             fontsize=26, color=CREAM_LINE, fontfamily="sans-serif", ha="left",
             fontweight="bold")
    fig.text(0.07, 0.865, "SQUARE-WAVE RECONSTRUCTION  ·  DWG-FS-01",
             fontsize=10, color=GOLD, fontfamily="sans-serif", ha="left")
    fig.text(0.93, 0.90, "SHEET 1/1",
             fontsize=10, color=CYAN, fontfamily="sans-serif", ha="right", alpha=0.8)

    # main reconstruction cascade (vertical stack of N)
    x = np.linspace(-np.pi, np.pi, 1400)
    Ns = [1, 3, 7, 15, 63]
    n_panels = len(Ns)
    top, bot = 0.78, 0.22
    gap = 0.012
    h_each = (top - bot - gap * (n_panels - 1)) / n_panels

    for i, N in enumerate(Ns):
        y0 = top - (i + 1) * h_each - i * gap
        ax = fig.add_axes([0.10, y0, 0.72, h_each * 0.92])
        ax.set_facecolor("none")
        ax.set_xlim(-np.pi, np.pi)
        ax.set_ylim(-1.45, 1.45)
        ax.axis("off")
        s = square_partial(x, N)
        ideal = square_ideal(x)
        ax.plot(x, ideal, color=CYAN, lw=0.8, alpha=0.15)
        ax.fill_between(x, 0, s, color=CYAN, alpha=0.08)
        col = CREAM_LINE if N == 63 else CYAN
        ax.plot(x, s, color=col, lw=1.8 if N < 63 else 2.3, solid_capstyle="round")
        ax.axhline(0, color=CYAN, lw=0.4, alpha=0.25)
        # N callout
        fig.text(0.84, y0 + h_each * 0.4, f"N={N}",
                 fontsize=11, color=GOLD if N == 63 else CYAN,
                 fontfamily="sans-serif", ha="left", va="center",
                 fontweight="bold" if N == 63 else "normal")

    # side formula rail
    fig.text(0.10, 0.165,
             r"$f_N=\frac{4}{\pi}\sum_{k=0}^{N-1}\frac{\sin((2k+1)x)}{2k+1}"
             r"\qquad b_n=\frac{4}{n\pi}\ (n\ \mathrm{odd})"
             r"\qquad N\rightarrow\infty$",
             fontsize=11, color=CREAM_LINE, ha="left", va="top")

    # title block corner (classic blueprint cartouche)
    axc = fig.add_axes([0.55, 0.04, 0.38, 0.10])
    axc.set_xlim(0, 1)
    axc.set_ylim(0, 1)
    axc.axis("off")
    axc.add_patch(Rectangle((0, 0), 1, 1, fill=False, edgecolor=CYAN, lw=1.2))
    axc.add_patch(Rectangle((0.02, 0.08), 0.96, 0.84, fill=False, edgecolor=CYAN, lw=0.6))
    axc.text(0.05, 0.70, "PROJECT", fontsize=7, color=CYAN, ha="left", alpha=0.7)
    axc.text(0.05, 0.42, "FOURIER — PERIODIC ANALYSIS", fontsize=9, color=CREAM_LINE, ha="left")
    axc.text(0.05, 0.18, "SCALE: WALL  ·  REV: DIRECTION C", fontsize=7, color=GOLD, ha="left")

    fig.text(0.10, 0.06, "MathRelaxing", fontsize=10, color=CYAN, ha="left", alpha=0.85)

    return fig_to_pil(fig)


def _label_strip(img: Image.Image, letter: str, title: str, subtitle: str) -> Image.Image:
    """Add bottom direction label for comparison."""
    W, H = img.size
    strip_h = 90
    out = Image.new("RGB", (W, H + strip_h), (18, 18, 20))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((40, H + 22), f"DIRECTION {letter}", font=_sans(18, True), fill=GOLD)
    d.text((40, H + 50), title, font=_sans(22, True), fill=(240, 236, 228))
    d.text((W - 40, H + 45), subtitle, font=_sans(14), fill=(160, 155, 145), anchor="rm")
    return out


def contact_sheet(imgs: list[Image.Image], labels: list[str]) -> Image.Image:
    """Side-by-side comparison at reduced height."""
    # normalize height
    target_h = 900
    resized = []
    for im in imgs:
        r = target_h / im.height
        resized.append(im.resize((int(im.width * r), target_h), Image.Resampling.LANCZOS))
    gap = 24
    tw = sum(i.width for i in resized) + gap * (len(resized) - 1) + 48
    th = target_h + 120
    sheet = Image.new("RGB", (tw, th), (22, 22, 26))
    d = ImageDraw.Draw(sheet)
    d.text((24, 28), "FOURIER SERIES  ·  three directions for physical poster",
           font=_sans(22, True), fill=(240, 236, 228))
    d.text((24, 60), "MathRelaxing  ·  design study (not live on Printify yet)",
           font=_sans(14), fill=(140, 135, 125))
    x = 24
    for im, lab in zip(resized, labels):
        sheet.paste(im, (x, 100))
        d.text((x + 8, th - 28), lab, font=_sans(13, True), fill=GOLD)
        x += im.width + gap
    return sheet


def main():
    print("=== Fourier direction mockups ===")
    a = mockup_plate_v2()
    a_l = _label_strip(a, "A", "Scientific plate v2", "denser · same family")
    path_a = OUT / "dir_A_plate_v2.jpg"
    a_l.save(path_a, "JPEG", quality=92, optimize=True)
    print(f"  {path_a.name}  {a_l.size}")

    b = mockup_hero_monumental()
    b_l = _label_strip(b, "B", "Hero monumental", "one diagram · wall presence")
    path_b = OUT / "dir_B_hero_monumental.jpg"
    b_l.save(path_b, "JPEG", quality=92, optimize=True)
    print(f"  {path_b.name}  {b_l.size}")

    c = mockup_blueprint_navy()
    c_l = _label_strip(c, "C", "Blueprint navy", "engineering · dark wall")
    path_c = OUT / "dir_C_blueprint_navy.jpg"
    c_l.save(path_c, "JPEG", quality=92, optimize=True)
    print(f"  {path_c.name}  {c_l.size}")

    # also save clean versions without strip (for pure art judgment)
    a.save(OUT / "dir_A_plate_v2_clean.jpg", "JPEG", quality=93, optimize=True)
    b.save(OUT / "dir_B_hero_monumental_clean.jpg", "JPEG", quality=93, optimize=True)
    c.save(OUT / "dir_C_blueprint_navy_clean.jpg", "JPEG", quality=93, optimize=True)

    sheet = contact_sheet([a, b, c], ["A · plate v2", "B · hero monumental", "C · blueprint navy"])
    path_s = OUT / "dir_contact_sheet.jpg"
    sheet.save(path_s, "JPEG", quality=90, optimize=True)
    print(f"  {path_s.name}  {sheet.size}")
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
