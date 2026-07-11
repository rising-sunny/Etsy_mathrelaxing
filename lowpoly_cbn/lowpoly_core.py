"""
lowpoly_core.py — headless "geometric color-by-number" generator.

Extracted and cleaned from the desktop Tkinter tool (ingramspark_kdp_video.py):
no GUI, no CMYK/print-book pipeline. Takes ONE full-colour source image and
produces digital, Etsy-ready deliverables:

  * <name>_coloring.png  — the printable page: white cells, grid outlines,
    a number in every cell, and a numbered colour legend.
  * <name>_colored.png   — the solution (cells filled with their colour) + legend.
  * <name>_coloring.pdf  — the coloring page as a single 300 dpi US-Letter PDF.

Fixes vs the original: numbers are now drawn for triangular and hexagonal
tilings too (the original only numbered squares); nearest-colour matching and
font loading are robust and dependency-light (PIL + numpy + scikit-learn).

    from lowpoly_core import generate_cbn
    generate_cbn("art.png", "out/", poly_type="triangular", side_length=46, num_colors=12)
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DPI = 300
LETTER_PX = (int(8.5 * DPI), int(11 * DPI))   # 2550 x 3300


def _font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def quantize(image, num_colors):
    """Adaptive colour reduction (PIL median-cut). Returns (quantized RGB image,
    palette Nx3 int) ordered light->dark so legend numbers read nicely."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    pal_img = image.quantize(colors=num_colors, method=Image.MEDIANCUT, dither=Image.NONE)
    raw = pal_img.getpalette()[: num_colors * 3]
    palette = np.array(raw, int).reshape(-1, 3)
    lum = palette @ np.array([0.299, 0.587, 0.114])
    order = np.argsort(-lum)
    palette = palette[order]
    return image.quantize(colors=num_colors, method=Image.MEDIANCUT,
                          dither=Image.NONE).convert("RGB"), palette


def _nearest_number(color, palette):
    d = np.sum((palette.astype(int) - np.array(color[:3], int)) ** 2, axis=1)
    return int(np.argmin(d)) + 1


def _centered_text(draw, text, cx, cy, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=font, fill=fill)


def _draw_legend(draw, palette, x, y, max_w, sw=64, gap=26, font=None):
    font = font or _font(40)
    cx = x
    cy = y
    for i, col in enumerate(palette, start=1):
        label = str(i)
        lb = draw.textbbox((0, 0), label, font=font)
        cell_w = sw + 14 + (lb[2] - lb[0]) + gap
        if cx + cell_w > x + max_w:
            cx = x
            cy += sw + gap
        draw.rectangle([cx, cy, cx + sw, cy + sw], fill=tuple(int(c) for c in col),
                       outline=(60, 60, 60), width=3)
        _centered_text(draw, label, cx + sw + 14 + (lb[2] - lb[0]) / 2, cy + sw / 2,
                       font, (30, 30, 30))
        cx += cell_w
    return cy + sw


def _iter_cells(poly_type, art_w, art_h, s):
    """Yield (points, sample_xy) for each tile fully inside the art box."""
    if poly_type == "square":
        for y in range(0, art_h - s + 1, s):
            for x in range(0, art_w - s + 1, s):
                pts = [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]
                yield pts, (x + s / 2, y + s / 2)
    elif poly_type == "triangular":
        # proper tessellation: each horizontal strip is height th; triangles of
        # base s are placed every s/2, alternating point-up / point-down so they
        # interlock with no gaps.
        th = s * math.sqrt(3) / 2
        half = s / 2
        rows = int(art_h / th) + 1
        cols = int(art_w / half) + 1
        for r in range(rows):
            y = r * th
            for i in range(cols):
                left = i * half
                if (i + r) % 2 == 0:                       # point-up
                    pts = [(left, y + th), (left + s, y + th), (left + half, y)]
                else:                                       # point-down
                    pts = [(left, y), (left + s, y), (left + half, y + th)]
                if min(p[0] for p in pts) >= 0 and max(p[0] for p in pts) <= art_w \
                   and min(p[1] for p in pts) >= 0 and max(p[1] for p in pts) <= art_h:
                    cx = sum(p[0] for p in pts) / 3
                    cy = sum(p[1] for p in pts) / 3
                    yield pts, (cx, cy)
    elif poly_type == "hexagonal":
        hw = math.sqrt(3) * s
        vert = s * 1.5
        rows = int(art_h / vert) + 2
        cols = int(art_w / hw) + 2
        for r in range(rows):
            for q in range(cols):
                cx = q * hw + (hw / 2 if r % 2 else 0)
                cy = r * vert
                pts = [(cx + s * math.cos(math.radians(30 + 60 * i)),
                        cy + s * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
                if min(p[0] for p in pts) >= 0 and max(p[0] for p in pts) <= art_w \
                   and min(p[1] for p in pts) >= 0 and max(p[1] for p in pts) <= art_h:
                    yield pts, (cx, cy)
    else:
        raise ValueError("poly_type must be square|triangular|hexagonal")


def generate_cbn(src_path, out_dir, poly_type="triangular", side_length=46,
                 num_colors=12, page_px=LETTER_PX, margin=110, legend_gap=70,
                 title="MathRelaxing  ·  Color by Number"):
    os.makedirs(out_dir, exist_ok=True)
    src = Image.open(src_path).convert("RGB")
    quant, palette = quantize(src, num_colors)

    page_w, page_h = page_px
    # reserve space: top title, side margins, bottom legend
    title_h = 130
    legend_rows_guess = max(1, math.ceil(num_colors / 8))
    legend_h = 60 + legend_rows_guess * (64 + 26) + 40
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin - title_h - legend_h - legend_gap

    ar = quant.width / quant.height
    if avail_w / avail_h > ar:      # height-bound
        art_h = avail_h
        art_w = int(art_h * ar)
    else:                            # width-bound
        art_w = avail_w
        art_h = int(art_w / ar)
    art = quant.resize((art_w, art_h), Image.Resampling.LANCZOS)
    art_px = np.asarray(art)

    off_x = (page_w - art_w) // 2
    off_y = margin + title_h

    coloring = Image.new("RGB", page_px, "white")
    colored = Image.new("RGB", page_px, "white")
    dc = ImageDraw.Draw(coloring)
    dk = ImageDraw.Draw(colored)

    grid_rgb = (165, 165, 165)
    num_font = _font(max(14, int(side_length * (0.42 if poly_type != "triangular" else 0.34))))
    num_rgb = (95, 95, 95)

    ncells = 0
    for pts, (sx, sy) in _iter_cells(poly_type, art_w, art_h, side_length):
        ix = min(art_w - 1, max(0, int(sx)))
        iy = min(art_h - 1, max(0, int(sy)))
        color = tuple(int(c) for c in art_px[iy, ix])
        n = _nearest_number(color, palette)
        shifted = [(off_x + px, off_y + py) for px, py in pts]
        dc.polygon(shifted, fill="white", outline=grid_rgb)
        _centered_text(dc, str(n), off_x + sx, off_y + sy, num_font, num_rgb)
        dk.polygon(shifted, fill=color)
        ncells += 1

    # title
    tf = _font(64)
    _centered_text(dc, title, page_w / 2, margin + title_h / 2 - 10, tf, (40, 40, 40))
    _centered_text(dk, title, page_w / 2, margin + title_h / 2 - 10, tf, (40, 40, 40))

    # legend
    ly = off_y + art_h + legend_gap
    _draw_legend(dc, palette, margin, ly, avail_w, font=_font(40))
    _draw_legend(dk, palette, margin, ly, avail_w, font=_font(40))

    base = os.path.splitext(os.path.basename(src_path))[0]
    p_color = os.path.join(out_dir, f"{base}_coloring.png")
    p_sol = os.path.join(out_dir, f"{base}_colored.png")
    p_pdf = os.path.join(out_dir, f"{base}_coloring.pdf")
    coloring.save(p_color, dpi=(DPI, DPI))
    colored.save(p_sol, dpi=(DPI, DPI))
    coloring.save(p_pdf, "PDF", resolution=DPI)
    return {"coloring": p_color, "colored": p_sol, "pdf": p_pdf,
            "cells": ncells, "colors": num_colors, "art_size": (art_w, art_h)}


if __name__ == "__main__":
    import sys
    src = sys.argv[1]
    info = generate_cbn(src, os.path.join(os.path.dirname(__file__), "out"))
    print(info)
