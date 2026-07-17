"""
generate_bauhaus_set.py — Bauhaus geometric wall-art print set (full SKU)
=========================================================================
6 gallery-grade compositions × large-poster 300 dpi masters + previews + ZIP.

Designed for BIG prints (up to 24×36 in / A1) at true 300 dpi.
Edges are supersampled for clean poster-scale geometry.

  python generate_bauhaus_set.py
  python generate_bauhaus_set.py --preview-only
  python generate_bauhaus_set.py --no-zip
"""
from __future__ import annotations

import argparse
import math
import os
import random
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

BASE = Path(__file__).resolve().parent
OUT = BASE / "bauhaus_set"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"
ZIP_PATH = OUT / "MathRelaxing_Bauhaus_Print_Set.zip"
ZIP_LARGE = OUT / "MathRelaxing_Bauhaus_LargePoster.zip"
ZIP_STD = OUT / "MathRelaxing_Bauhaus_Standard.zip"

DPI_PRINT = 300
DPI_PREVIEW = 160
# Flat geometric art compresses best without film grain (grain → 10× ZIP size).
JPEG_Q_LARGE = 88
JPEG_Q_STD = 90
SUPERSAMPLE = 2  # render 2× then LANCZOS downscale when memory allows

# Physical sizes (inches) @ 300 dpi — large poster masters + home/standard
# Name encodes ratio + physical size for print shops.
SIZES = {
    # ── Large poster (print shop / oversized frames) ──
    "2x3_24x36": (24.0, 36.0),   # 7200×10800 px — classic big poster
    "3x4_18x24": (18.0, 24.0),   # 5400×7200 px
    "4x5_24x30": (24.0, 30.0),   # 7200×9000 px
    "5x7_20x28": (20.0, 28.0),   # 6000×8400 px
    "A1": (23.39, 33.11),        # ISO A1
    "A2": (16.54, 23.39),        # ISO A2
    # ── Standard / home printer ──
    "2x3_12x18": (12.0, 18.0),
    "3x4_12x16": (12.0, 16.0),
    "4x5_16x20": (16.0, 20.0),
    "5x7_10x14": (10.0, 14.0),
    "A3": (11.69, 16.54),
    "A4": (8.27, 11.69),
}

LARGE_KEYS = {"2x3_24x36", "3x4_18x24", "4x5_24x30", "5x7_20x28", "A1", "A2"}
STD_KEYS = {"2x3_12x18", "3x4_12x16", "4x5_16x20", "5x7_10x14", "A3", "A4"}

# Palette
NAVY = (16, 22, 48)
NAVY_DEEP = (10, 14, 32)
CREAM = (249, 245, 236)
GOLD = (196, 158, 72)
GOLD_LIGHT = (214, 182, 108)
RED = (192, 48, 42)
RED_DEEP = (148, 32, 30)
BLUE = (38, 82, 152)
BLACK = (18, 18, 20)
SOFT = (88, 86, 82)
WHITE = (255, 255, 255)


def _ensure():
    for d in (OUT, PRINTS, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf"]
        if bold
        else ["arial.ttf", "segoeui.ttf", "calibri.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, max(8, int(size)))
            except OSError:
                pass
    return ImageFont.load_default()


def _serif(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, max(8, int(size)))
            except OSError:
                pass
    return ImageFont.load_default()


def _paper_grain(img: Image.Image, amount: float = 0.025) -> Image.Image:
    """Subtle paper grain — light enough for large posters, still print-tactile."""
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    rng = np.random.default_rng(42)
    # Fine grain; slight blur so it doesn't posterize as digital noise at 300dpi
    noise = rng.normal(0, 8.0, size=arr.shape[:2]).astype(np.float32)
    # box blur 3×3 via simple average (cheap)
    pad = np.pad(noise, 1, mode="edge")
    noise = (
        pad[0:-2, 0:-2] + pad[0:-2, 1:-1] + pad[0:-2, 2:]
        + pad[1:-1, 0:-2] + pad[1:-1, 1:-1] + pad[1:-1, 2:]
        + pad[2:, 0:-2] + pad[2:, 1:-1] + pad[2:, 2:]
    ) / 9.0
    noise = np.stack([noise, noise, noise], axis=-1)
    out = np.clip(arr + noise * amount * 40.0, 0, 255)
    return Image.fromarray(out.astype(np.uint8))


def _finish(img: Image.Image, grain: bool = False) -> Image.Image:
    # No grain on print masters — keeps 24×36 JPG ~1–2MB (Etsy digital limit).
    # Grain is optional for screen previews only.
    if grain:
        img = _paper_grain(img, 0.028)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img = ImageEnhance.Sharpness(img).enhance(1.06)
    return img


def _corner_marks(d: ImageDraw.ImageDraw, W: int, H: int, m: float, arm: float, color=NAVY, w: int = 2):
    m, arm = int(m), int(arm)
    paths = [
        [(m, m + arm), (m, m), (m + arm, m)],
        [(W - m - arm, m), (W - m, m), (W - m, m + arm)],
        [(m, H - m - arm), (m, H - m), (m + arm, H - m)],
        [(W - m - arm, H - m), (W - m, H - m), (W - m, H - m - arm)],
    ]
    for path in paths:
        d.line(path, fill=color, width=max(1, w))


def _px(inches: float, dpi: int) -> int:
    return max(1, int(round(inches * dpi)))


# ── Compositions (W, H in pixels) ─────────────────────────────────────────────

def poster_01_circles_bars(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 450)

    for y in range(int(H * 0.62), H):
        t = (y - H * 0.62) / max(1, H * 0.38)
        col = (int(CREAM[0] - 6 * t), int(CREAM[1] - 5 * t), int(CREAM[2] - 4 * t))
        d.line([(0, y), (W, y)], fill=col)

    r = int(u * 0.325)
    cx, cy = int(W * 0.30), int(H * 0.325)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    # nested precision rings (read at poster distance)
    d.ellipse([cx - r + int(u * 0.014), cy - r + int(u * 0.014),
               cx + r - int(u * 0.014), cy + r - int(u * 0.014)], outline=RED_DEEP, width=mid)
    d.ellipse([cx - r + int(u * 0.045), cy - r + int(u * 0.045),
               cx + r - int(u * 0.045), cy + r - int(u * 0.045)], outline=RED_DEEP, width=hair)
    # micro cream arc highlight (top-left of disc)
    d.arc([cx - r + int(u * 0.06), cy - r + int(u * 0.06),
           cx + r - int(u * 0.06), cy + r - int(u * 0.06)], 200, 250, fill=CREAM, width=hair)

    bar_x0, bar_x1 = int(W * 0.675), int(W * 0.787)
    d.rectangle([bar_x0, int(H * 0.067), bar_x1, int(H * 0.875)], fill=NAVY)
    # spine module stack
    d.rectangle([bar_x0 + int(u * 0.022), int(H * 0.142), bar_x1 - int(u * 0.022), int(H * 0.192)], fill=CREAM)
    d.rectangle([bar_x0 + int(u * 0.022), int(H * 0.208), bar_x1 - int(u * 0.022), int(H * 0.233)], fill=GOLD)
    d.rectangle([bar_x0 + int(u * 0.022), int(H * 0.248), bar_x1 - int(u * 0.022), int(H * 0.248) + hair * 2], fill=CREAM)
    # micro squares along spine
    ms = max(4, u // 80)
    for k, yy in enumerate([0.30, 0.34, 0.38]):
        col = (CREAM, RED, GOLD)[k]
        d.rectangle([bar_x0 + int(u * 0.035), int(H * yy),
                     bar_x0 + int(u * 0.035) + ms, int(H * yy) + ms], fill=col)

    d.rectangle([int(W * 0.087), int(H * 0.575), int(W * 0.825), int(H * 0.675)], fill=BLUE)
    # blue bar inner hairline
    d.rectangle([int(W * 0.087), int(H * 0.575), int(W * 0.825), int(H * 0.575) + hair], fill=NAVY_DEEP)
    d.rectangle([int(W * 0.087), int(H * 0.692), int(W * 0.825), int(H * 0.698)], fill=GOLD)
    d.rectangle([int(W * 0.087), int(H * 0.705), int(W * 0.825), int(H * 0.705) + hair], fill=NAVY)

    s = int(u * 0.044)
    d.rectangle([bar_x0 - int(u * 0.056), int(H * 0.733), bar_x0 - int(u * 0.012), int(H * 0.733) + s], fill=BLACK)
    d.rectangle([bar_x0 - int(u * 0.056) + hair * 2, int(H * 0.733) + hair * 2,
                 bar_x0 - int(u * 0.012) - hair * 2, int(H * 0.733) + s - hair * 2], outline=GOLD, width=hair)

    # index L + blue disc
    d.rectangle([int(W * 0.087), int(H * 0.067), int(W * 0.162), int(H * 0.072)], fill=NAVY)
    d.rectangle([int(W * 0.087), int(H * 0.067), int(W * 0.095), int(H * 0.117)], fill=NAVY)
    br = int(u * 0.019)
    d.ellipse([int(W * 0.175), int(H * 0.070), int(W * 0.175) + 2 * br, int(H * 0.070) + 2 * br], fill=BLUE)
    d.ellipse([int(W * 0.175) + br // 3, int(H * 0.070) + br // 3,
               int(W * 0.175) + 2 * br - br // 3, int(H * 0.070) + 2 * br - br // 3], outline=CREAM, width=hair)

    # baseline tick marks (print-shop craft detail)
    base_y = int(H * 0.92)
    for i in range(8):
        x = int(W * (0.10 + i * 0.09))
        htick = mid if i % 2 == 0 else hair
        d.rectangle([x, base_y, x + hair * 2, base_y + htick * 6], fill=NAVY)

    _corner_marks(d, W, H, m=u * 0.04, arm=u * 0.025, color=NAVY, w=max(2, u // 700))
    return img


def poster_02_triangles(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    d = ImageDraw.Draw(img)
    u = min(W, H)

    d.rectangle([int(W * 0.075), int(H * 0.075), int(W * 0.925), int(H * 0.078)], fill=GOLD)
    d.rectangle([int(W * 0.075), int(H * 0.917), int(W * 0.925), int(H * 0.920)], fill=GOLD_LIGHT)

    d.polygon([(int(W * 0.087), int(H * 0.825)), (int(W * 0.50), int(H * 0.133)),
               (int(W * 0.912), int(H * 0.825))], fill=CREAM)
    d.polygon([(int(W * 0.137), int(H * 0.200)), (int(W * 0.737), int(H * 0.200)),
               (int(W * 0.437), int(H * 0.617))], fill=RED)
    d.polygon([(int(W * 0.312), int(H * 0.258)), (int(W * 0.562), int(H * 0.258)),
               (int(W * 0.437), int(H * 0.458))], fill=NAVY_DEEP)

    cr = int(u * 0.10)
    cx, cy = int(W * 0.437), int(H * 0.392)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=BLUE)
    d.ellipse([cx - int(cr * 0.88), cy - int(cr * 0.88), cx + int(cr * 0.88), cy + int(cr * 0.88)],
              outline=GOLD, width=max(3, u // 250))
    d.ellipse([cx - int(cr * 0.75), cy - int(cr * 0.75), cx + int(cr * 0.75), cy + int(cr * 0.75)],
              outline=GOLD_LIGHT, width=max(1, u // 700))
    d.ellipse([cx - int(cr * 0.62), cy - int(cr * 0.62), cx + int(cr * 0.62), cy + int(cr * 0.62)],
              outline=CREAM, width=max(1, u // 800))
    d.ellipse([cx - int(cr * 0.28), cy - int(cr * 0.28), cx + int(cr * 0.28), cy + int(cr * 0.28)],
              fill=NAVY_DEEP)

    d.rectangle([int(W * 0.498), int(H * 0.083), int(W * 0.502), int(H * 0.792)], fill=CREAM)
    # index ticks on center line
    for k in range(6):
        yy = int(H * (0.15 + k * 0.10))
        d.rectangle([int(W * 0.492), yy, int(W * 0.508), yy + max(1, u // 600)], fill=GOLD)

    yb = int(H * 0.875)
    th = max(3, u // 400)
    d.rectangle([int(W * 0.125), yb, int(W * 0.225), yb + th], fill=CREAM)
    d.rectangle([int(W * 0.237), yb, int(W * 0.275), yb + th], fill=RED)
    d.rectangle([int(W * 0.287), yb, int(W * 0.387), yb + th], fill=GOLD)
    d.rectangle([int(W * 0.400), yb, int(W * 0.430), yb + th], fill=BLUE)
    return img


def poster_03_grid_modules(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)

    header_h = int(H * 0.083)
    d.rectangle([0, 0, W, header_h], fill=NAVY)
    d.text((W // 2, int(header_h * 0.38)), "FORM  ·  COLOR  ·  BALANCE",
           font=_font(max(14, u * 0.028), True), fill=CREAM, anchor="mt")
    d.text((W // 2, int(header_h * 0.65)), "MODULAR STUDY  N° 03",
           font=_font(max(10, u * 0.016)), fill=GOLD, anchor="mt")

    margin_x = int(W * 0.062)
    margin_top = int(H * 0.108)
    margin_bot = int(H * 0.058)
    cols, rows = 3, 4
    gap = int(u * 0.014)
    usable_w = W - 2 * margin_x - (cols - 1) * gap
    usable_h = H - margin_top - margin_bot - (rows - 1) * gap
    cw = usable_w // cols
    ch = usable_h // rows

    cells = [
        (NAVY, "circle_red"), (CREAM, "tri_navy"), (BLUE, "square_cream"),
        (CREAM, "bar_h_gold"), (RED, "circle_cream"), (NAVY, "tri_gold"),
        (GOLD, "bar_v_navy"), (CREAM, "ring_blue"), (BLUE, "split_red"),
        (NAVY, "square_gold"), (CREAM, "cross_navy"), (RED, "dual_circles"),
    ]

    i = 0
    for r in range(rows):
        for c in range(cols):
            x = margin_x + c * (cw + gap)
            y = margin_top + r * (ch + gap)
            bg, motif = cells[i]
            d.rectangle([x, y, x + cw, y + ch], fill=bg)
            if bg == CREAM:
                d.rectangle([x, y, x + cw, y + ch], outline=NAVY, width=max(1, u // 800))

            pad = int(min(cw, ch) * 0.18)
            ix0, iy0 = x + pad, y + pad
            ix1, iy1 = x + cw - pad, y + ch - pad
            cx, cy = x + cw // 2, y + ch // 2
            s = min(cw, ch) // 2 - pad

            if motif == "circle_red":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=RED)
            elif motif == "tri_navy":
                d.polygon([(cx, iy0), (ix1, iy1), (ix0, iy1)], fill=NAVY)
            elif motif == "square_cream":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
            elif motif == "bar_h_gold":
                bh = max(4, ch // 18)
                d.rectangle([ix0, cy - bh, ix1, cy + bh], fill=GOLD)
                d.rectangle([ix0, cy + bh * 2, ix1, cy + bh * 2 + max(2, bh // 2)], fill=NAVY)
            elif motif == "circle_cream":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
            elif motif == "tri_gold":
                d.polygon([(ix0, iy0), (ix1, iy0), (cx, iy1)], fill=GOLD)
            elif motif == "bar_v_navy":
                bw = max(4, cw // 16)
                d.rectangle([cx - bw, iy0, cx + bw, iy1], fill=NAVY)
                rr = s // 2
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=CREAM)
            elif motif == "ring_blue":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=BLUE, width=max(4, s // 6))
                d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=RED)
            elif motif == "split_red":
                d.rectangle([x, y, x + cw // 2, y + ch], fill=RED)
                d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=CREAM)
            elif motif == "square_gold":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=GOLD)
                d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=NAVY)
            elif motif == "cross_navy":
                t = max(4, s // 6)
                d.rectangle([cx - t, iy0, cx + t, iy1], fill=NAVY)
                d.rectangle([ix0, cy - t, ix1, cy + t], fill=NAVY)
                rr = max(6, s // 4)
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=GOLD)
            elif motif == "dual_circles":
                d.ellipse([ix0, cy - s // 2, ix0 + s, cy + s // 2], fill=CREAM)
                d.ellipse([ix1 - s, cy - s // 2, ix1, cy + s // 2], fill=NAVY)
            i += 1

    d.rectangle([margin_x, H - int(H * 0.037), W - margin_x, H - int(H * 0.035)], fill=NAVY)
    return img


def poster_04_arcs(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    m = int(u * 0.035)
    d.rectangle([m, m, W - m, H - m], outline=NAVY, width=max(2, u // 500))

    # navy arc mass (upper)
    d.pieslice([int(-W * 0.175), int(H * 0.05), int(W * 0.612), int(H * 0.575)], 280, 20, fill=NAVY)
    d.ellipse([int(W * 0.10), int(H * 0.217), int(W * 0.325), int(H * 0.367)], fill=CREAM)
    br = int(u * 0.037)
    d.ellipse([int(W * 0.175) - br, int(H * 0.267) - br, int(W * 0.175) + br, int(H * 0.267) + br], fill=BLUE)

    # blue lower arc
    d.pieslice([int(W * 0.30), int(H * 0.375), int(W * 1.11), int(H * 0.917)], 160, 280, fill=BLUE)

    # red panel
    d.rectangle([int(W * 0.70), int(H * 0.083), int(W * 0.887), int(H * 0.383)], fill=RED)
    d.rectangle([int(W * 0.725), int(H * 0.117), int(W * 0.862), int(H * 0.125)], fill=GOLD)
    sq = int(u * 0.087)
    sx, sy = int(W * 0.75), int(H * 0.167)
    d.rectangle([sx, sy, sx + sq, sy + sq], fill=CREAM)
    ir = int(sq * 0.28)
    d.ellipse([sx + sq // 2 - ir, sy + sq // 2 - ir, sx + sq // 2 + ir, sy + sq // 2 + ir], fill=NAVY)

    # gold ring bottom-left
    gr = int(u * 0.087)
    gx, gy = int(W * 0.212), int(H * 0.758)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=GOLD)
    d.ellipse([gx - int(gr * 0.55), gy - int(gr * 0.55), gx + int(gr * 0.55), gy + int(gr * 0.55)], fill=CREAM)

    # navy spine
    d.rectangle([int(W * 0.075), int(H * 0.50), int(W * 0.925), int(H * 0.517)], fill=NAVY_DEEP)

    d.rectangle([int(W * 0.80), int(H * 0.067), int(W * 0.887), int(H * 0.072)], fill=NAVY)
    d.rectangle([int(W * 0.88), int(H * 0.067), int(W * 0.887), int(H * 0.117)], fill=NAVY)
    return img


def poster_05_type_form(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    d = ImageDraw.Draw(img)
    u = min(W, H)

    m = int(u * 0.05)
    d.rectangle([m, m, W - m, H - m], fill=CREAM)

    # left red spine
    d.rectangle([m, m, int(W * 0.20), int(H * 0.533)], fill=RED)
    d.rectangle([m, m, int(W * 0.20), int(H * 0.067)], fill=GOLD)
    d.rectangle([int(W * 0.075), int(H * 0.167), int(W * 0.175), int(H * 0.173)], fill=CREAM)
    d.rectangle([int(W * 0.075), int(H * 0.188), int(W * 0.137), int(H * 0.194)], fill=NAVY)

    # blue circle
    cr = int(u * 0.125)
    cx, cy = int(W * 0.737), int(H * 0.200)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=BLUE)
    d.ellipse([cx - int(cr * 0.60), cy - int(cr * 0.60), cx + int(cr * 0.60), cy + int(cr * 0.60)],
              outline=CREAM, width=max(2, u // 400))

    # type
    tx = int(W * 0.237)
    d.text((tx, int(H * 0.133)), "FORM", font=_font(max(36, u * 0.075), True), fill=NAVY, anchor="lt")
    d.text((tx, int(H * 0.200)), "FOLLOWS", font=_font(max(18, u * 0.030), True), fill=SOFT, anchor="lt")
    d.text((tx, int(H * 0.233)), "FUNCTION", font=_font(max(20, u * 0.035), True), fill=NAVY, anchor="lt")
    d.rectangle([tx, int(H * 0.275), int(W * 0.562), int(H * 0.278)], fill=NAVY)

    # gold bar
    d.rectangle([tx, int(H * 0.383), int(W * 0.862), int(H * 0.450)], fill=GOLD)
    d.text((tx + int(u * 0.012), int(H * 0.404)), "1919  →  FORM",
           font=_font(max(12, u * 0.017), True), fill=NAVY, anchor="lt")

    # micro squares
    sq = int(u * 0.037)
    d.rectangle([int(W * 0.737), int(H * 0.300), int(W * 0.737) + sq, int(H * 0.300) + sq], fill=NAVY)
    d.rectangle([int(W * 0.812), int(H * 0.300), int(W * 0.812) + int(sq * 0.6), int(H * 0.300) + int(sq * 0.6)], fill=RED)

    # bottom navy panel
    by = int(H * 0.55)
    d.rectangle([m, by, W - m, H - m], fill=NAVY)
    d.polygon([(int(W * 0.125), int(H * 0.875)), (int(W * 0.35), int(H * 0.617)),
               (int(W * 0.575), int(H * 0.875))], fill=CREAM)
    rr = int(u * 0.087)
    d.ellipse([int(W * 0.625) - rr, int(H * 0.692) - rr, int(W * 0.625) + rr, int(H * 0.692) + rr], fill=RED)
    d.rectangle([int(W * 0.625), int(H * 0.783), int(W * 0.90), int(H * 0.808)], fill=GOLD)
    d.rectangle([int(W * 0.85), int(H * 0.617), int(W * 0.912), int(H * 0.875)], fill=BLUE)
    d.rectangle([int(W * 0.862), int(H * 0.667), int(W * 0.90), int(H * 0.70)], fill=CREAM)
    return img


def poster_06_balance(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)

    col_w = int(W * 0.325)
    d.rectangle([0, 0, col_w, H], fill=NAVY)

    cr = int(u * 0.087)
    cx, cy = int(col_w * 0.50), int(H * 0.192)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=CREAM)
    d.ellipse([cx - int(cr * 0.64), cy - int(cr * 0.64), cx + int(cr * 0.64), cy + int(cr * 0.64)],
              outline=BLUE, width=max(3, u // 160))
    d.ellipse([cx - int(cr * 0.36), cy - int(cr * 0.36), cx + int(cr * 0.36), cy + int(cr * 0.36)], fill=GOLD)

    d.rectangle([int(col_w * 0.19), int(H * 0.583), int(col_w * 0.81), int(H * 0.600)], fill=CREAM)
    d.rectangle([int(col_w * 0.19), int(H * 0.617), int(col_w * 0.54), int(H * 0.625)], fill=RED)
    d.rectangle([int(col_w * 0.19), int(H * 0.642), int(col_w * 0.69), int(H * 0.647)], fill=GOLD)

    # red disc right
    rr = int(u * 0.225)
    rx, ry = int(W * 0.625), int(H * 0.225)
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=RED)
    sq = int(u * 0.075)
    d.rectangle([int(W * 0.737), int(H * 0.092), int(W * 0.737) + sq, int(H * 0.092) + sq], fill=NAVY)
    d.rectangle([int(W * 0.762), int(H * 0.108), int(W * 0.762) + int(sq * 0.6), int(H * 0.108) + int(sq * 0.6)], fill=CREAM)

    # blue rect
    d.rectangle([int(W * 0.45), int(H * 0.408), int(W * 0.80), int(H * 0.567)], fill=BLUE)
    d.rectangle([int(W * 0.45), int(H * 0.467), int(W * 0.80), int(H * 0.483)], fill=CREAM)
    d.rectangle([int(W * 0.675), int(H * 0.408), int(W * 0.70), int(H * 0.567)], fill=GOLD)

    # gold beam lock
    d.rectangle([0, int(H * 0.467), W, int(H * 0.483)], fill=GOLD)
    d.rectangle([0, int(H * 0.467), col_w, int(H * 0.483)], fill=NAVY)
    d.rectangle([0, int(H * 0.473), col_w, int(H * 0.477)], fill=CREAM)

    # gold triangle bottom
    d.polygon([(int(W * 0.437), int(H * 0.875)), (int(W * 0.737), int(H * 0.617)),
               (int(W * 0.925), int(H * 0.875))], fill=GOLD)
    d.polygon([(int(W * 0.562), int(H * 0.875)), (int(W * 0.737), int(H * 0.717)),
               (int(W * 0.912), int(H * 0.875))], fill=NAVY)

    mk = int(u * 0.045)
    arm = int(u * 0.03)
    d.line([(W - mk, mk), (W - mk - arm, mk)], fill=NAVY, width=max(2, u // 700))
    d.line([(W - mk, mk), (W - mk, mk + arm)], fill=NAVY, width=max(2, u // 700))
    d.line([(W - mk, H - mk), (W - mk - arm, H - mk)], fill=NAVY, width=max(2, u // 700))
    d.line([(W - mk, H - mk), (W - mk, H - mk - arm)], fill=NAVY, width=max(2, u // 700))
    return img


POSTERS = [
    ("01_circles_bars", "Circles & Bars", poster_01_circles_bars),
    ("02_triangles", "Triangles", poster_02_triangles),
    ("03_grid_modules", "Grid Modules", poster_03_grid_modules),
    ("04_arcs", "Arcs", poster_04_arcs),
    ("05_form_type", "Form & Type", poster_05_type_form),
    ("06_balance", "Balance", poster_06_balance),
]


def render_print(
    fn,
    w_in: float,
    h_in: float,
    dpi: int = DPI_PRINT,
    supersample: int = SUPERSAMPLE,
) -> Image.Image:
    """
    Render at supersample× resolution, then LANCZOS downscale to target dpi.
    Produces clean antialiased geometry that holds up on large posters.
    """
    ss = max(1, int(supersample))
    if dpi <= DPI_PREVIEW:
        ss = 1  # previews: skip heavy supersample
    W_hi = _px(w_in, dpi * ss)
    H_hi = _px(h_in, dpi * ss)
    # Cap supersample memory for huge posters (24×36 @ 2× = ~155MP)
    max_px = 90_000_000
    if W_hi * H_hi > max_px and ss > 1:
        ss = 1
        W_hi, H_hi = _px(w_in, dpi), _px(h_in, dpi)
        print(f"    (ss off for {w_in}×{h_in} — pixel cap)")
    raw = fn(W_hi, H_hi)
    W, H = _px(w_in, dpi), _px(h_in, dpi)
    if ss > 1 and (raw.size != (W, H)):
        raw = raw.resize((W, H), Image.Resampling.LANCZOS)
    # grain only for low-res preview renders
    return _finish(raw, grain=(dpi <= DPI_PREVIEW))


def save_jpg(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 90):
    path.parent.mkdir(parents=True, exist_ok=True)
    # 4:2:0 is fine for posters; smaller files, still sharp on solid geometry
    img.save(
        path,
        "JPEG",
        quality=quality,
        dpi=(dpi, dpi),
        optimize=True,
        progressive=True,
        subsampling=2,
    )
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {path.relative_to(OUT)}  ({mb:.2f} MB, {img.width}×{img.height})")


def generate_prints(preview_only: bool = False):
    _ensure()
    if preview_only:
        print("=== Prints skipped (--preview-only) ===")
        return
    # clean old print sizes so ZIP doesn't mix generations
    if PRINTS.exists():
        shutil.rmtree(PRINTS)
    PRINTS.mkdir(parents=True, exist_ok=True)

    print(f"=== Bauhaus LARGE POSTER prints @ {DPI_PRINT} dpi (ss={SUPERSAMPLE}) ===")
    for slug, title, fn in POSTERS:
        folder = PRINTS / slug
        folder.mkdir(parents=True, exist_ok=True)
        print(f"-- {title}")
        for size_name, (w_in, h_in) in SIZES.items():
            img = render_print(fn, w_in, h_in, DPI_PRINT)
            path = folder / f"{slug}_{size_name}_{DPI_PRINT}dpi.jpg"
            q = JPEG_Q_LARGE if size_name in LARGE_KEYS else JPEG_Q_STD
            save_jpg(img, path, DPI_PRINT, q)


# ── Listing previews ──────────────────────────────────────────────────────────

def _mockup_frame(poster: Image.Image, canvas: int = 1600) -> Image.Image:
    """Single framed poster on warm wall — listing photo."""
    S = canvas
    img = Image.new("RGB", (S, S), (235, 230, 222))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(236 - 10 * t), int(231 - 8 * t), int(222 - 6 * t)))
    d.rectangle([0, int(S * 0.80), S, S], fill=(48, 44, 40))
    d.rectangle([0, int(S * 0.80), S, int(S * 0.80) + 3], fill=(70, 64, 58))

    pw = int(S * 0.40)
    ph = int(pw * poster.height / poster.width)
    poster = poster.resize((pw, ph), Image.Resampling.LANCZOS)
    px, py = (S - pw) // 2, int(S * 0.10)
    frame = max(18, S // 70)

    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [px - frame + 14, py - frame + 18, px + pw + frame + 14, py + ph + frame + 18],
        fill=(0, 0, 0, 75),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px - frame, py - frame, px + pw + frame, py + ph + frame], fill=(22, 22, 24))
    d.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], fill=CREAM)
    img.paste(poster, (px, py))
    return img


def build_previews():
    _ensure()
    print("=== Bauhaus listing previews ===")
    # render masters at preview dpi for speed
    masters = []
    for slug, title, fn in POSTERS:
        # 2:3 @ preview dpi, ~8x12
        img = render_print(fn, 8.0, 12.0, DPI_PREVIEW)
        masters.append((slug, title, img))

    # 1 hero — mockup poster 01
    hero = _mockup_frame(masters[0][2], 1600)
    d = ImageDraw.Draw(hero)
    d.rectangle([0, 1480, 1600, 1600], fill=NAVY_DEEP)
    d.text((800, 1520), "BAUHAUS GEOMETRIC PRINT SET", font=_serif(28, True), fill=CREAM, anchor="mt")
    d.text((800, 1565), "6 posters  ·  up to 24×36 in  ·  300 dpi large-format", font=_font(16), fill=GOLD, anchor="mt")
    save_jpg(hero, PREVIEWS / "bauhaus_preview_1_hero.jpg", DPI_PREVIEW, 92)

    # 2 set of 3 mockup
    S = 1600
    set_img = Image.new("RGB", (S, S), (238, 233, 226))
    d = ImageDraw.Draw(set_img)
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(238 - 8 * t), int(233 - 6 * t), int(226 - 5 * t)))
    d.rectangle([0, int(S * 0.78), S, S], fill=(42, 38, 34))
    chosen = [0, 1, 5]
    pw, gap = 340, 48
    total = 3 * pw + 2 * gap
    x0 = (S - total) // 2
    y0 = 200
    d.text((S // 2, 70), "SET OF 6  ·  GALLERY GEOMETRIC", font=_serif(26, True), fill=NAVY, anchor="mt")
    d.text((S // 2, 115), "Mix, match, and frame your wall", font=_font(16), fill=SOFT, anchor="mt")
    for i, idx in enumerate(chosen):
        pimg = masters[idx][2]
        ph = int(pw * pimg.height / pimg.width)
        pimg = pimg.resize((pw, ph), Image.Resampling.LANCZOS)
        x = x0 + i * (pw + gap)
        d.rectangle([x - 14, y0 - 14, x + pw + 14, y0 + ph + 14], fill=(20, 20, 22))
        d.rectangle([x - 5, y0 - 5, x + pw + 5, y0 + ph + 5], fill=CREAM)
        set_img.paste(pimg, (x, y0))
        d = ImageDraw.Draw(set_img)
    d.rectangle([0, S - 90, S, S], fill=NAVY_DEEP)
    d.text((S // 2, S - 45), "MathRelaxing  ·  Bauhaus Print Set", font=_font(18), fill=GOLD, anchor="mm")
    save_jpg(set_img, PREVIEWS / "bauhaus_preview_2_set.jpg", DPI_PREVIEW, 92)

    # 3 what's included
    incl = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, S, 160], fill=NAVY)
    d.text((S // 2, 55), "WHAT'S INCLUDED", font=_serif(34, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 110), "Instant download  ·  print at home or shop", font=_font(18), fill=GOLD, anchor="mt")

    items = [
        ("6", "Original posters", "Geometric Bauhaus compositions", RED, CREAM),
        ("12", "Print sizes", "Up to 24×36 in + A1 large poster", BLUE, CREAM),
        ("300", "DPI masters", "True 300 dpi — print-shop ready", GOLD, NAVY),
        ("1", "ZIP download", "Large + standard sizes included", NAVY, CREAM),
    ]
    y = 220
    for num, title, sub, bubble, ink in items:
        d.ellipse([120, y, 220, y + 100], fill=bubble)
        d.text((170, y + 50), num, font=_font(28, True), fill=ink, anchor="mm")
        d.text((260, y + 30), title, font=_font(28, True), fill=NAVY, anchor="lt")
        d.text((260, y + 70), sub, font=_font(18), fill=SOFT, anchor="lt")
        y += 140

    d.rectangle([100, 820, S - 100, 830], fill=GOLD)
    d.text((S // 2, 900), "Palette: navy · cream · gold · Bauhaus red & blue", font=_font(20), fill=NAVY, anchor="mt")
    d.text((S // 2, 960), "Personal use  ·  MathRelaxing", font=_font(16), fill=SOFT, anchor="mt")
    # mini strip of all 6
    tw = 200
    gap = 20
    total = 6 * tw + 5 * gap
    x0 = (S - total) // 2
    yy = 1100
    for i, (_, _, m) in enumerate(masters):
        th = int(tw * m.height / m.width)
        thumb = m.resize((tw, th), Image.Resampling.LANCZOS)
        incl.paste(thumb, (x0 + i * (tw + gap), yy))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, S - 70, S, S], fill=NAVY_DEEP)
    d.text((S // 2, S - 35), "No physical product ships", font=_font(16), fill=CREAM, anchor="mm")
    save_jpg(incl, PREVIEWS / "bauhaus_preview_3_included.jpg", DPI_PREVIEW, 92)

    # 4–9 individual posters (clean plate on cream, not mockup — buyers see the art)
    for i, (slug, title, m) in enumerate(masters):
        plate = Image.new("RGB", (S, S), CREAM)
        # fit poster with margin
        max_h = int(S * 0.82)
        max_w = int(S * 0.55)
        scale = min(max_w / m.width, max_h / m.height)
        pw, ph = int(m.width * scale), int(m.height * scale)
        pimg = m.resize((pw, ph), Image.Resampling.LANCZOS)
        px, py = (S - pw) // 2, int(S * 0.08)
        # subtle shadow
        sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([px + 8, py + 10, px + pw + 8, py + ph + 10], fill=(0, 0, 0, 40))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        plate = Image.alpha_composite(plate.convert("RGBA"), sh).convert("RGB")
        plate.paste(pimg, (px, py))
        d = ImageDraw.Draw(plate)
        d.rectangle([0, S - 100, S, S], fill=NAVY)
        d.text((S // 2, S - 60), f"{i + 1:02d}  ·  {title.upper()}", font=_font(22, True), fill=GOLD, anchor="mm")
        d.text((S // 2, S - 30), "MathRelaxing Bauhaus Set", font=_font(14), fill=CREAM, anchor="mm")
        save_jpg(plate, PREVIEWS / f"bauhaus_preview_{i + 4}_{slug.split('_', 1)[1]}.jpg", DPI_PREVIEW, 92)

    # contact style overview as optional 10th
    grid = Image.new("RGB", (S, S), NAVY_DEEP)
    d = ImageDraw.Draw(grid)
    d.text((S // 2, 40), "ALL 6 DESIGNS", font=_serif(30, True), fill=CREAM, anchor="mt")
    d.rectangle([S // 2 - 60, 85, S // 2 + 60, 88], fill=GOLD)
    tw, th = 420, 630
    gapx, gapy = 40, 50
    x0 = (S - 3 * tw - 2 * gapx) // 2
    y0 = 120
    for i, (_, title, m) in enumerate(masters):
        c, r = i % 3, i // 3
        x = x0 + c * (tw + gapx)
        y = y0 + r * (th + gapy)
        thumb = m.resize((tw, th), Image.Resampling.LANCZOS)
        d.rectangle([x - 3, y - 3, x + tw + 3, y + th + 3], fill=GOLD)
        grid.paste(thumb, (x, y))
        d = ImageDraw.Draw(grid)
        d.text((x + tw // 2, y + th + 14), title.upper(), font=_font(14, True), fill=GOLD, anchor="mt")
    d.rectangle([0, S - 60, S, S], fill=(6, 8, 18))
    d.text((S // 2, S - 30), "Digital download  ·  up to 24×36 / A1  ·  300 dpi", font=_font(15), fill=CREAM, anchor="mm")
    save_jpg(grid, PREVIEWS / "bauhaus_preview_10_all.jpg", DPI_PREVIEW, 92)
    print(f"  previews → {PREVIEWS}")


README_TXT = """MathRelaxing — Bauhaus Geometric Print Set
==========================================

6 original geometric wall-art posters inspired by Bauhaus form, color, and balance.
Built for LARGE poster printing at true 300 dpi (print-shop ready).

PRINTS (folders)
  01_circles_bars
  02_triangles
  03_grid_modules
  04_arcs
  05_form_type
  06_balance

LARGE POSTER SIZES (print shop / oversized frames) — 300 dpi
  2x3_24x36  →  24×36 in   (7200×10800 px)
  3x4_18x24  →  18×24 in
  4x5_24x30  →  24×30 in
  5x7_20x28  →  20×28 in
  A1         →  594×841 mm
  A2         →  420×594 mm

STANDARD / HOME PRINTER — 300 dpi
  2x3_12x18  →  12×18 in
  3x4_12x16  →  12×16 in
  4x5_16x20  →  16×20 in
  5x7_10x14  →  10×14 in
  A3 / A4

You can scale a large file DOWN for smaller frames (never upscale a small file).

PRINT TIPS
  • Matte or lightly textured paper looks best
  • For 24×36 / A1: use a print shop (not most home printers)
  • Colors: navy, cream, gold, Bauhaus red & blue
  • Files are high-quality JPG, 300 dpi, chroma-sharp

Personal use only. Not for resale or redistribution.
© MathRelaxing
"""


def _zip_subset(path: Path, size_keys: set[str] | None, label: str):
    if path.exists():
        path.unlink()
    count = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README_TXT)
        for slug, _title, _fn in POSTERS:
            folder = PRINTS / slug
            if not folder.is_dir():
                continue
            for f in sorted(folder.glob("*.jpg")):
                # filename: slug_SIZEKEY_300dpi.jpg
                mid = f.stem  # e.g. 01_circles_bars_2x3_24x36_300dpi
                # extract size key between last slug_ and _300dpi
                if not mid.endswith(f"_{DPI_PRINT}dpi"):
                    continue
                core = mid[: -len(f"_{DPI_PRINT}dpi")]
                # core = slug_sizekey → sizekey is after slug_
                if not core.startswith(slug + "_"):
                    continue
                size_key = core[len(slug) + 1 :]
                if size_keys is not None and size_key not in size_keys:
                    continue
                zf.write(f, arcname=f"{slug}/{f.name}")
                count += 1
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {label}: {path.name} ({mb:.1f} MB, {count} files)")
    if mb > 19.5:
        print(f"  WARNING: {path.name} near/over Etsy ~20MB limit")
    return mb, count


def _zip_designs(path: Path, slugs: list[str], size_keys: set[str] | None, label: str):
    if path.exists():
        path.unlink()
    count = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README_TXT)
        for slug, _title, _fn in POSTERS:
            if slug not in slugs:
                continue
            folder = PRINTS / slug
            if not folder.is_dir():
                continue
            for f in sorted(folder.glob("*.jpg")):
                mid = f.stem
                if not mid.endswith(f"_{DPI_PRINT}dpi"):
                    continue
                core = mid[: -len(f"_{DPI_PRINT}dpi")]
                if not core.startswith(slug + "_"):
                    continue
                size_key = core[len(slug) + 1 :]
                if size_keys is not None and size_key not in size_keys:
                    continue
                zf.write(f, arcname=f"{slug}/{f.name}")
                count += 1
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {label}: {path.name} ({mb:.1f} MB, {count} files)")
    if mb > 19.5:
        print(f"  WARNING: {path.name} over Etsy ~20MB — split further or lower JPEG_Q")
    return mb, count


def build_zip():
    """
    Etsy digital files ~20MB each, max 5 files.
    Pack strategy after compress:
      1) try one combined ZIP
      2) else Large (01-03) + Large (04-06) + Standard (all)
    """
    print("=== Bauhaus ZIP(s) ===")
    for p in (ZIP_PATH, ZIP_LARGE, ZIP_STD,
              OUT / "MathRelaxing_Bauhaus_LargePoster_A.zip",
              OUT / "MathRelaxing_Bauhaus_LargePoster_B.zip"):
        if p.exists():
            p.unlink()

    mb_all, _ = _zip_subset(ZIP_PATH, None, "COMBINED")
    if mb_all <= 19.0:
        print("  Single combined ZIP under limit — good")
        return [ZIP_PATH]

    print("  Combined too big → split packs")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    paths = []
    a = OUT / "MathRelaxing_Bauhaus_LargePoster_A.zip"
    b = OUT / "MathRelaxing_Bauhaus_LargePoster_B.zip"
    _zip_designs(a, ["01_circles_bars", "02_triangles", "03_grid_modules"], LARGE_KEYS, "LARGE A (01-03)")
    _zip_designs(b, ["04_arcs", "05_form_type", "06_balance"], LARGE_KEYS, "LARGE B (04-06)")
    _zip_subset(ZIP_STD, STD_KEYS, "STANDARD (all designs)")
    paths = [a, b, ZIP_STD]
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()

    _ensure()
    generate_prints(preview_only=args.preview_only)
    build_previews()
    if not args.preview_only and not args.no_zip:
        build_zip()
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
