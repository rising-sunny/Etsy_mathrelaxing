"""
lowpoly_core.py — headless "geometric color-by-number" generator.

Extracted and cleaned from the desktop Tkinter tool (ingramspark_kdp_video.py):
no GUI, no CMYK/print-book pipeline. Takes ONE full-colour source image and
produces digital, Etsy-ready deliverables styled to match the MathRelaxing
coloring books (serif titles, gold rules, "COLOR KEY" legend):

  * <name>_coloring.png  — printable page: title, tessellated numbered cells,
    numbered colour key, page label.
  * <name>_colored.png   — the full-colour solution.
  * <name>_coloring.pdf  — the coloring page as a single 300 dpi US-Letter PDF.

Fixes vs the original: numbers are drawn for triangular/hexagonal tilings too
(original numbered squares only) and the triangular tiling is a true gap-free
tessellation (original left diamond gaps). Uses PIL median-cut quantization.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DPI = 300
LETTER_PX = (int(8.5 * DPI), int(11 * DPI))   # 2550 x 3300
GOLD = (201, 162, 75)
INK = (38, 38, 38)
GRID = (170, 170, 170)
NUM = (110, 110, 110)


def _font(size, bold=True, serif=False):
    if serif:
        names = ("DejaVuSerif-Bold.ttf",) if bold else ("DejaVuSerif.ttf",)
    else:
        names = ("DejaVuSans-Bold.ttf", "arialbd.ttf", "arial.ttf") if bold else \
                ("DejaVuSans.ttf", "arial.ttf")
    for n in names:
        try:
            return ImageFont.truetype(n, size)
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


def _centered(draw, text, cx, cy, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=font, fill=fill)


def _draw_key(draw, palette, cx, top, max_w):
    """Centered numbered colour key with a small serif heading."""
    head = _font(40, serif=True)
    _centered(draw, "COLOR KEY", cx, top, head, GOLD)
    sw, pad, gap = 60, 12, 46
    lf = _font(38, serif=True)
    # lay swatches out centered, wrapping rows
    items = []
    for i, col in enumerate(palette, 1):
        lb = draw.textbbox((0, 0), str(i), font=lf)
        items.append((str(i), tuple(int(c) for c in col), sw + pad + (lb[2] - lb[0])))
    rows, cur, cw = [], [], 0
    for it in items:
        w = it[2] + gap
        if cw + w > max_w and cur:
            rows.append((cur, cw)); cur, cw = [], 0
        cur.append(it); cw += w
    if cur:
        rows.append((cur, cw))
    y = top + 60
    for row, rw in rows:
        x = cx - (rw - gap) / 2
        for label, col, w in row:
            draw.rectangle([x, y, x + sw, y + sw], fill=col, outline=(70, 70, 70), width=3)
            lb = draw.textbbox((0, 0), label, font=lf)
            _centered(draw, label, x + sw + pad + (lb[2] - lb[0]) / 2, y + sw / 2, lf, INK)
            x += w + gap
        y += sw + 30
    return y


def _iter_cells(poly_type, art_w, art_h, s):
    if poly_type == "square":
        for y in range(0, art_h - s + 1, s):
            for x in range(0, art_w - s + 1, s):
                pts = [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]
                yield pts, (x + s / 2, y + s / 2)
    elif poly_type == "triangular":
        th = s * math.sqrt(3) / 2
        half = s / 2
        rows = int(art_h / th) + 1
        cols = int(art_w / half) + 1
        for r in range(rows):
            y = r * th
            for i in range(cols):
                left = i * half
                if (i + r) % 2 == 0:
                    pts = [(left, y + th), (left + s, y + th), (left + half, y)]
                else:
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


def _page(page_px, title, subtitle, page_label):
    """Blank branded page with serif title, gold rule, subtitle, page label.
    Returns (image, draw, content_top_y, content_bottom_y)."""
    img = Image.new("RGB", page_px, "white")
    d = ImageDraw.Draw(img)
    W, H = page_px
    _centered(d, title, W / 2, 150, _font(66, serif=True), INK)
    d.line([(W / 2 - 320, 232), (W / 2 + 320, 232)], fill=GOLD, width=4)
    if subtitle:
        _centered(d, subtitle, W / 2, 285, _font(34, bold=False, serif=True), (120, 120, 120))
    if page_label:
        _centered(d, page_label, W / 2, H - 90, _font(30, serif=True), (150, 150, 150))
    top = 340 if subtitle else 300
    return img, d, top, H - 150


def generate_cbn(src_path, out_dir, poly_type="triangular", side_length=46,
                 num_colors=12, page_px=LETTER_PX, margin=150,
                 title="Color by Number", subtitle=None, page_label=None):
    os.makedirs(out_dir, exist_ok=True)
    src = Image.open(src_path).convert("RGB")
    quant, palette = quantize(src, num_colors)
    page_w, page_h = page_px

    legend_rows = max(1, math.ceil(num_colors / 8))
    legend_h = 60 + 60 + legend_rows * (60 + 30) + 30
    gap = 70

    coloring, dc, top, bottom = _page(page_px, title, subtitle, page_label)
    colored, dk, _, _ = _page(page_px, title, subtitle, page_label)

    avail_w = page_w - 2 * margin
    avail_h = (bottom - legend_h - gap) - top
    ar = quant.width / quant.height
    if avail_w / avail_h > ar:
        art_h = int(avail_h); art_w = int(art_h * ar)
    else:
        art_w = int(avail_w); art_h = int(art_w / ar)
    art = quant.resize((art_w, art_h), Image.Resampling.LANCZOS)
    art_px = np.asarray(art)

    off_x = (page_w - art_w) // 2
    off_y = top
    num_font = _font(max(14, int(side_length * (0.42 if poly_type != "triangular" else 0.34))))

    ncells = 0
    for pts, (sx, sy) in _iter_cells(poly_type, art_w, art_h, side_length):
        ix = min(art_w - 1, max(0, int(sx)))
        iy = min(art_h - 1, max(0, int(sy)))
        color = tuple(int(c) for c in art_px[iy, ix])
        n = _nearest_number(color, palette)
        shifted = [(off_x + px, off_y + py) for px, py in pts]
        dc.polygon(shifted, fill="white", outline=GRID)
        _centered(dc, str(n), off_x + sx, off_y + sy, num_font, NUM)
        dk.polygon(shifted, fill=color)
        ncells += 1

    key_top = off_y + art_h + gap
    _draw_key(dc, palette, page_w / 2, key_top, avail_w)
    _draw_key(dk, palette, page_w / 2, key_top, avail_w)

    base = os.path.splitext(os.path.basename(src_path))[0]
    p_color = os.path.join(out_dir, f"{base}_coloring.png")
    p_sol = os.path.join(out_dir, f"{base}_colored.png")
    p_pdf = os.path.join(out_dir, f"{base}_coloring.pdf")
    coloring.save(p_color, dpi=(DPI, DPI))
    colored.save(p_sol, dpi=(DPI, DPI))
    coloring.save(p_pdf, "PDF", resolution=DPI)
    return {"coloring": p_color, "colored": p_sol, "pdf": p_pdf,
            "cells": ncells, "colors": num_colors, "art_size": (art_w, art_h),
            "coloring_img": coloring, "colored_img": colored}


if __name__ == "__main__":
    import sys
    print(generate_cbn(sys.argv[1], os.path.join(os.path.dirname(__file__), "out")))
