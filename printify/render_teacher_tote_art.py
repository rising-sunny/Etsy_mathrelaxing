"""
Exclusive transparent tote art — no brand mark, bold type, richer math graphic.

  python printify/render_teacher_tote_art.py
"""
from __future__ import annotations

import io
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "_tote_art")


def _font(sz: int, bold: bool = False):
    # Prefer heavy faces for print contrast on fabric
    if bold:
        cands = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            r"C:\Windows\Fonts\georgiab.ttf",
        ]
    else:
        cands = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\georgia.ttf",
        ]
    for p in cands:
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _draw_spaced(draw, text, y, fnt, fill, canvas_w, tracking=0.22):
    chars = list(text)
    widths = [fnt.getlength(c) for c in chars]
    gap = fnt.getlength("M") * tracking
    total = sum(widths) + gap * max(0, len(chars) - 1)
    x = (canvas_w - total) / 2
    for i, c in enumerate(chars):
        # slight stroke for fabric readability: draw offsets
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (0, 0)):
            draw.text((x + dx, y + dy), c, font=fnt, fill=fill)
        x += widths[i] + gap


def _math_graphic(size: int) -> Image.Image:
    """
    Dense computed graphic: unit circle + angle + sine projection + rose curve.
    Transparent bg, dark heavy strokes — reads on sand/white canvas.
    """
    dpi = 320
    fig_w = size / dpi
    fig = plt.figure(figsize=(fig_w, fig_w), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.88])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.patch.set_alpha(0.0)
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.55, 1.55)

    ink = "#0B0D12"
    teal = "#0E5F6B"
    rust = "#9A4A28"

    # outer guide ring
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color=ink, lw=3.2, solid_capstyle="round")
    # inner ring
    ax.plot(0.72 * np.cos(th), 0.72 * np.sin(th), color=teal, lw=1.8, alpha=0.85)

    # axes
    ax.plot([-1.35, 1.35], [0, 0], color=ink, lw=1.6, alpha=0.75)
    ax.plot([0, 0], [-1.35, 1.35], color=ink, lw=1.6, alpha=0.75)

    # angle θ = π/3
    theta = np.pi / 3
    # sector fill (subtle)
    sec = np.linspace(0, theta, 80)
    ax.fill(
        np.concatenate([[0], np.cos(sec), [0]]),
        np.concatenate([[0], np.sin(sec), [0]]),
        color=teal,
        alpha=0.12,
    )
    # radius
    ax.plot([0, np.cos(theta)], [0, np.sin(theta)], color=rust, lw=3.0, solid_capstyle="round")
    # point on circle
    ax.scatter([np.cos(theta)], [np.sin(theta)], s=55, c=rust, zorder=5, edgecolors="none")
    # dashed projections
    ax.plot(
        [np.cos(theta), np.cos(theta)],
        [0, np.sin(theta)],
        color=ink,
        lw=1.4,
        ls=(0, (4, 3)),
        alpha=0.7,
    )
    ax.plot(
        [0, np.cos(theta)],
        [np.sin(theta), np.sin(theta)],
        color=ink,
        lw=1.4,
        ls=(0, (4, 3)),
        alpha=0.7,
    )

    # rhodonea / rose r = cos(3θ) — denser math interest
    t2 = np.linspace(0, 2 * np.pi, 800)
    r = 0.38 * np.cos(3 * t2)
    ax.plot(
        r * np.cos(t2),
        r * np.sin(t2),
        color=teal,
        lw=2.2,
        alpha=0.9,
        solid_capstyle="round",
    )

    # tick marks on circle (every 30°)
    for k in range(12):
        a = k * np.pi / 6
        ax.plot(
            [0.94 * np.cos(a), np.cos(a)],
            [0.94 * np.sin(a), np.sin(a)],
            color=ink,
            lw=2.0,
            solid_capstyle="round",
        )

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=True,
        facecolor="none",
        edgecolor="none",
        pad_inches=0,
    )
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def _equation_layer(width_px: int) -> Image.Image:
    """Bold Euler identity — heavy CM mathtext, transparent."""
    plt.rcParams["mathtext.fontset"] = "cm"
    fig = plt.figure(figsize=(11, 2.4), dpi=340)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.patch.set_alpha(0.0)
    # draw twice slightly offset for "weight" on fabric
    for dx, dy, col, z in (
        (0.0015, -0.008, "#0B0D12", 1),
        (0.0, 0.0, "#0B0D12", 2),
    ):
        ax.text(
            0.5 + dx,
            0.52 + dy,
            r"$e^{i\pi}+1=0$",
            fontsize=86,
            ha="center",
            va="center",
            color=col,
            zorder=z,
        )
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=340,
        transparent=True,
        facecolor="none",
        edgecolor="none",
        bbox_inches="tight",
        pad_inches=0.12,
    )
    plt.close(fig)
    buf.seek(0)
    eq = Image.open(buf).convert("RGBA")
    # boost alpha of dark pixels for print punch
    arr = np.array(eq).astype(np.float32)
    a = arr[:, :, 3:4] / 255.0
    # darken RGB toward black where alpha present
    arr[:, :, :3] = arr[:, :, :3] * 0.15  # push toward near-black
    arr[:, :, 3] = np.clip(arr[:, :, 3] * 1.15, 0, 255)
    eq = Image.fromarray(arr.astype(np.uint8), "RGBA")
    h = int(eq.height * width_px / eq.width)
    return eq.resize((width_px, h), Image.Resampling.LANCZOS)


def render(size: int = 3600) -> Image.Image:
    S = size
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    INK = (11, 13, 18, 255)
    TEAL = (14, 95, 107, 255)

    # ── title ──
    f_title = _font(max(28, int(S * 0.048)), bold=True)
    _draw_spaced(d, "MATH TEACHER", int(S * 0.06), f_title, INK, S, tracking=0.20)

    # thick rule
    cx = S // 2
    rw = int(S * 0.14)
    y_rule = int(S * 0.13)
    for t in range(5):
        d.line([(cx - rw, y_rule + t), (cx + rw, y_rule + t)], fill=TEAL, width=1)

    # ── rich math graphic ──
    g = _math_graphic(int(S * 0.72))
    # ensure graphic is punchy
    g = ImageEnhance.Contrast(g).enhance(1.15)
    gx = (S - g.width) // 2
    gy = int(S * 0.15)
    im.paste(g, (gx, gy), g)

    # ── equation under graphic ──
    eq = _equation_layer(int(S * 0.78))
    eq_x = (S - eq.width) // 2
    eq_y = int(S * 0.78)
    # clamp if overflow
    if eq_y + eq.height > S - int(S * 0.04):
        eq_y = S - eq.height - int(S * 0.04)
    im.paste(eq, (eq_x, eq_y), eq)

    # light unsharp for edge definition on fabric
    # only sharpen RGB with alpha preserved
    rgb = im.convert("RGB")
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))
    out = rgb.convert("RGBA")
    out.putalpha(im.split()[-1])
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    im = render(3600)
    master = os.path.join(OUT_DIR, "math_teacher_tote_exclusive.png")
    im.save(master, "PNG")
    print("master", master)

    for size, name in [
        (1800, "math_teacher_tote_exclusive_1800.png"),
        (3000, "math_teacher_tote_exclusive_3000.png"),
    ]:
        im.resize((size, size), Image.Resampling.LANCZOS).save(
            os.path.join(OUT_DIR, name), "PNG"
        )
        print("saved", name)

    for bg_col, name in [
        ((232, 220, 200), "preview_on_sahara.png"),
        ((248, 248, 246), "preview_on_white.png"),
        ((28, 28, 30), "preview_on_black.png"),
    ]:
        bg = Image.new("RGBA", im.size, (*bg_col, 255))
        comp = Image.alpha_composite(bg, im)
        comp.convert("RGB").resize((1000, 1000), Image.Resampling.LANCZOS).save(
            os.path.join(OUT_DIR, name), "JPEG", quality=93
        )
        print("preview", name)


if __name__ == "__main__":
    main()
