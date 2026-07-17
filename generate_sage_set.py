"""
generate_sage_set.py — Sage Green / Neutral Abstract print set (full SKU)
=========================================================================
Quiet-luxury gallery posters: sage, cream, stone, warm taupe.
Japandi / soft abstract — intentional negative space, layered forms.

  python generate_sage_set.py
  python generate_sage_set.py --preview-only
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
OUT = BASE / "sage_set"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"

DPI_PRINT = 300
DPI_PREVIEW = 160
JPEG_Q_LARGE = 82
JPEG_Q_STD = 88
SUPERSAMPLE = 2

# Curated sizes that pack under Etsy (dense art-friendly)
SIZES = {
    "2x3_24x36": (24.0, 36.0),
    "3x4_18x24": (18.0, 24.0),
    "4x5_16x20": (16.0, 20.0),
    "2x3_12x18": (12.0, 18.0),
    "A4": (8.27, 11.69),
    # extras generated for completeness; pack script may subset
    "3x4_12x16": (12.0, 16.0),
    "5x7_10x14": (10.0, 14.0),
    "A3": (11.69, 16.54),
}
LARGE_KEYS = {"2x3_24x36", "3x4_18x24", "4x5_16x20"}
PACK_SIZES = {"2x3_24x36", "3x4_18x24", "4x5_16x20", "2x3_12x18", "A4"}

# Quiet luxury palette
CREAM = (245, 241, 232)
CREAM_WARM = (238, 232, 220)
SAGE = (138, 158, 138)
SAGE_DEEP = (98, 120, 102)
SAGE_SOFT = (170, 184, 168)
STONE = (180, 172, 160)
STONE_DK = (120, 112, 100)
TAUPE = (160, 140, 122)
CLAY = (186, 150, 128)
INK = (48, 52, 48)
SOFT = (110, 108, 100)
GOLD = (176, 158, 110)
WHITE = (252, 250, 246)


def _ensure():
    for d in (OUT, PRINTS, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)


def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"])
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, max(8, int(size)))
            except OSError:
                pass
    return ImageFont.load_default()


def _px(inches, dpi):
    return max(1, int(round(inches * dpi)))


def _finish(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img = ImageEnhance.Color(img).enhance(1.03)
    img = ImageEnhance.Sharpness(img).enhance(1.05)
    return img


def _wash(img, top, bot):
    """Vertical cream→warm wash."""
    d = ImageDraw.Draw(img)
    W, H = img.size
    for y in range(H):
        t = y / max(1, H - 1)
        col = tuple(int(a + (b - a) * t) for a, b in zip(top, bot))
        d.line([(0, y), (W, y)], fill=col)


def _soft_ellipse(d, box, fill, outline=None, ow=1):
    d.ellipse(box, fill=fill, outline=outline, width=ow if outline else 0)


def _corner_marks(d, W, H, m, arm, color, w):
    for path in [
        [(m, m + arm), (m, m), (m + arm, m)],
        [(W - m - arm, m), (W - m, m), (W - m, m + arm)],
        [(m, H - m - arm), (m, H - m), (m + arm, H - m)],
        [(W - m - arm, H - m), (W - m, H - m), (W - m, H - m - arm)],
    ]:
        d.line(path, fill=color, width=max(1, w))


def _texture_lines(d, x0, y0, x1, y1, color, n, rng, w=1):
    """Fine parallel hatch — paper/print craft texture in a region."""
    for i in range(n):
        t = i / max(1, n - 1)
        y = y0 + (y1 - y0) * t + rng.uniform(-1, 1)
        d.line([(x0, y), (x1, y)], fill=color, width=max(1, w))


def _organic_blob(d, cx, cy, rx, ry, fill, n=28, seed=0, rot=0):
    """Soft irregular organic oval (artistic, not perfect)."""
    rng = random.Random(seed)
    pts = []
    for i in range(n):
        a = math.radians(rot + i * (360 / n))
        jitter = 0.88 + 0.18 * rng.random()
        x = cx + rx * jitter * math.cos(a)
        y = cy + ry * jitter * math.sin(a)
        pts.append((x, y))
    d.polygon(pts, fill=fill)


def _ring_stack(d, cx, cy, radii, colors, widths):
    for r, col, w in zip(radii, colors, widths):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, w))


# ── Six compositions — lethal artistic edition ────────────────────────────────

def poster_01_balance_forms(W, H):
    """Monumental disc, spine, layered bars — quiet luxury with depth."""
    img = Image.new("RGB", (W, H), CREAM)
    _wash(img, CREAM, CREAM_WARM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(101)
    hair = max(1, u // 900)
    mid = max(2, u // 450)

    # soft diagonal wash plane
    for i in range(40):
        t = i / 39
        y = int(H * (0.55 + 0.2 * t))
        col = (
            int(CREAM[0] - 6 * t),
            int(CREAM[1] - 4 * t),
            int(CREAM[2] - 3 * t),
        )
        d.line([(0, y), (W, y)], fill=col)

    # background ghost disc
    r_g = int(u * 0.38)
    cx, cy = int(W * 0.34), int(H * 0.36)
    d.ellipse([cx - r_g, cy - r_g, cx + r_g, cy + r_g], fill=(236, 232, 222))

    # main sage disc — layered
    r = int(u * 0.30)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SAGE)
    d.ellipse([cx - int(r * 0.82), cy - int(r * 0.82), cx + int(r * 0.82), cy + int(r * 0.82)], fill=SAGE_SOFT)
    d.ellipse([cx - int(r * 0.55), cy - int(r * 0.55), cx + int(r * 0.55), cy + int(r * 0.55)],
              outline=SAGE_DEEP, width=mid)
    d.ellipse([cx - int(r * 0.28), cy - int(r * 0.28), cx + int(r * 0.28), cy + int(r * 0.28)], fill=CREAM)
    d.ellipse([cx - int(r * 0.12), cy - int(r * 0.12), cx + int(r * 0.12), cy + int(r * 0.12)], fill=GOLD)

    # constellation of micro marks (curated, not random noise)
    for i, (fx, fy) in enumerate([
        (0.12, 0.14), (0.18, 0.11), (0.22, 0.18), (0.15, 0.22),
        (0.48, 0.12), (0.52, 0.16), (0.44, 0.20), (0.55, 0.10),
        (0.28, 0.08), (0.35, 0.13),
    ]):
        rr = u * (0.003 + (i % 3) * 0.0015)
        d.ellipse([W * fx - rr, H * fy - rr, W * fx + rr, H * fy + rr], fill=SAGE_DEEP if i % 2 else STONE_DK)

    # deep spine with modular windows
    bx0, bx1 = int(W * 0.64), int(W * 0.76)
    d.rectangle([bx0, int(H * 0.10), bx1, int(H * 0.82)], fill=SAGE_DEEP)
    # nested cream + gold modules
    d.rectangle([bx0 + int(u * 0.02), int(H * 0.16), bx1 - int(u * 0.02), int(H * 0.28)], fill=CREAM)
    d.rectangle([bx0 + int(u * 0.02), int(H * 0.32), bx1 - int(u * 0.02), int(H * 0.355)], fill=GOLD)
    d.rectangle([bx0 + int(u * 0.02), int(H * 0.38), bx1 - int(u * 0.02), int(H * 0.39)], fill=STONE)
    # small stacked ticks
    for k, yy in enumerate([0.44, 0.48, 0.52]):
        d.rectangle([bx0 + int(u * 0.025), int(H * yy), bx0 + int(u * 0.025) + int(u * 0.035), int(H * yy) + hair * 3],
                    fill=(CREAM, CLAY, GOLD)[k])

    # clay horizontal mass — overlapping disc + spine
    d.rectangle([int(W * 0.10), int(H * 0.58), int(W * 0.82), int(H * 0.72)], fill=CLAY)
    # inner cream cut
    d.rectangle([int(W * 0.14), int(H * 0.62), int(W * 0.42), int(H * 0.68)], fill=CREAM_WARM)
    # thin stone rules under
    d.rectangle([int(W * 0.10), int(H * 0.76), int(W * 0.82), int(H * 0.768)], fill=STONE_DK)
    d.rectangle([int(W * 0.10), int(H * 0.785), int(W * 0.55), int(H * 0.79)], fill=SAGE)

    # ink accent square + micro
    s = int(u * 0.038)
    d.rectangle([int(W * 0.84), int(H * 0.64), int(W * 0.84) + s, int(H * 0.64) + s], fill=INK)
    d.rectangle([int(W * 0.84) + s + hair * 3, int(H * 0.64), int(W * 0.84) + s + hair * 3 + s // 2,
                 int(H * 0.64) + s // 2], fill=GOLD)

    # thin vertical index left
    d.rectangle([int(W * 0.08), int(H * 0.12), int(W * 0.085), int(H * 0.42)], fill=INK)
    d.rectangle([int(W * 0.08), int(H * 0.12), int(W * 0.16), int(H * 0.128)], fill=INK)

    _corner_marks(d, W, H, int(u * 0.045), int(u * 0.028), STONE_DK, mid)
    return img


def poster_02_stacked_horizon(W, H):
    """Layered landscape abstract — bands, occlusions, floating orbits."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 500)

    # irregular organic horizon layers (not flat slabs only)
    layers = [
        (0.00, 0.18, CREAM, None),
        (0.15, 0.34, SAGE_SOFT, 0.02),
        (0.30, 0.48, SAGE, 0.025),
        (0.45, 0.58, STONE, 0.015),
        (0.55, 0.72, SAGE_DEEP, 0.02),
        (0.70, 0.88, CLAY, 0.018),
        (0.85, 1.00, CREAM_WARM, None),
    ]
    for y0, y1, col, wave in layers:
        if wave is None:
            d.rectangle([0, int(H * y0), W, int(H * y1)], fill=col)
        else:
            # wavy top edge
            pts = [(0, H)]
            for k in range(50):
                t = k / 49
                x = W * t
                y = H * (y0 + wave * math.sin(t * math.pi * 3 + y0 * 10))
                pts.append((x, y))
            pts += [(W, H), (0, H)]
            # fill from wavy line to bottom of band
            band = []
            for k in range(50):
                t = k / 49
                x = W * t
                ytop = H * (y0 + wave * math.sin(t * math.pi * 3 + y0 * 10))
                band.append((x, ytop))
            for k in range(49, -1, -1):
                t = k / 49
                x = W * t
                ybot = H * (y1 + (wave * 0.3) * math.sin(t * math.pi * 2))
                band.append((x, ybot))
            d.polygon(band, fill=col)

    # floating multi-orbit circle
    r = int(u * 0.15)
    cx, cy = int(W * 0.58), int(H * 0.46)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM)
    _ring_stack(
        d, cx, cy,
        [int(r * 0.85), int(r * 0.62), int(r * 0.38), int(r * 0.18)],
        [SAGE_DEEP, SAGE, STONE_DK, GOLD],
        [mid, mid, hair * 2, mid],
    )
    d.ellipse([cx - int(r * 0.08), cy - int(r * 0.08), cx + int(r * 0.08), cy + int(r * 0.08)], fill=SAGE_DEEP)

    # secondary smaller orbit left
    r2 = int(u * 0.06)
    cx2, cy2 = int(W * 0.28), int(H * 0.38)
    d.ellipse([cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2], outline=CREAM, width=mid)
    d.ellipse([cx2 - int(r2 * 0.4), cy2 - int(r2 * 0.4), cx2 + int(r2 * 0.4), cy2 + int(r2 * 0.4)], fill=GOLD)

    # gold horizon rule
    d.rectangle([int(W * 0.08), int(H * 0.58), int(W * 0.92), int(H * 0.585)], fill=GOLD)
    d.rectangle([int(W * 0.08), int(H * 0.595), int(W * 0.40), int(H * 0.598)], fill=INK)

    # L-bracket top-left + clay chip
    d.rectangle([int(W * 0.10), int(H * 0.08), int(W * 0.105), int(H * 0.22)], fill=INK)
    d.rectangle([int(W * 0.10), int(H * 0.08), int(W * 0.22), int(H * 0.086)], fill=INK)
    s = int(u * 0.05)
    d.rectangle([int(W * 0.78), int(H * 0.12), int(W * 0.78) + s, int(H * 0.12) + s], fill=CLAY)
    d.rectangle([int(W * 0.78) + s // 4, int(H * 0.12) + s // 4,
                 int(W * 0.78) + 3 * s // 4, int(H * 0.12) + 3 * s // 4], fill=CREAM)

    # texture hatch in deep band
    _texture_lines(d, int(W * 0.1), int(H * 0.62), int(W * 0.5), int(H * 0.70),
                   (80, 100, 85), 12, random.Random(7), hair)
    return img


def poster_03_arch_still(W, H):
    """Architectural still life — nested arches, columns, clay altar."""
    img = Image.new("RGB", (W, H), CREAM_WARM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 480)

    # left vertical field — split panels
    d.rectangle([0, 0, int(W * 0.30), H], fill=SAGE_SOFT)
    d.rectangle([0, int(H * 0.42), int(W * 0.30), H], fill=SAGE)
    d.rectangle([int(W * 0.30), 0, int(W * 0.305), H], fill=STONE_DK)
    # subtle hatch on left
    _texture_lines(d, int(W * 0.04), int(H * 0.1), int(W * 0.26), int(H * 0.38),
                   (150, 168, 150), 18, random.Random(3), hair)

    # nested arches
    d.pieslice([int(W * 0.18), int(H * 0.12), int(W * 0.98), int(H * 0.88)], 180, 360, fill=SAGE_DEEP)
    d.pieslice([int(W * 0.26), int(H * 0.20), int(W * 0.90), int(H * 0.80)], 180, 360, fill=SAGE)
    d.pieslice([int(W * 0.34), int(H * 0.28), int(W * 0.82), int(H * 0.72)], 180, 360, fill=CREAM)
    # arch thickness lines
    d.arc([int(W * 0.26), int(H * 0.20), int(W * 0.90), int(H * 0.80)], 200, 340, fill=CREAM, width=mid)
    # floor / plinth
    d.rectangle([int(W * 0.30), int(H * 0.54), int(W * 0.98), int(H * 0.575)], fill=STONE_DK)
    d.rectangle([int(W * 0.30), int(H * 0.575), int(W * 0.98), int(H * 0.59)], fill=STONE)

    # clay altar block with nested modules
    d.rectangle([int(W * 0.68), int(H * 0.60), int(W * 0.90), int(H * 0.90)], fill=CLAY)
    d.rectangle([int(W * 0.72), int(H * 0.66), int(W * 0.86), int(H * 0.72)], fill=CREAM)
    d.rectangle([int(W * 0.72), int(H * 0.76), int(W * 0.86), int(H * 0.775)], fill=SAGE_DEEP)
    d.ellipse([int(W * 0.76), int(H * 0.80), int(W * 0.82), int(H * 0.86)], fill=GOLD)

    # floating gold bead in arch void
    r = int(u * 0.032)
    d.ellipse([int(W * 0.48) - r, int(H * 0.40) - r, int(W * 0.48) + r, int(H * 0.40) + r], fill=GOLD)
    d.ellipse([int(W * 0.48) - r // 2, int(H * 0.40) - r // 2, int(W * 0.48) + r // 2, int(H * 0.40) + r // 2],
              fill=CREAM)

    # small stone column accents
    d.rectangle([int(W * 0.38), int(H * 0.62), int(W * 0.42), int(H * 0.88)], fill=STONE)
    d.rectangle([int(W * 0.38), int(H * 0.62), int(W * 0.42), int(H * 0.64)], fill=SAGE_DEEP)

    m = int(u * 0.038)
    d.rectangle([m, m, W - m, H - m], outline=STONE_DK, width=mid)
    d.rectangle([m + mid * 2, m + mid * 2, W - m - mid * 2, H - m - mid * 2], outline=SAGE, width=hair)
    return img


def poster_04_rings_field(W, H):
    """Orbital field — multi-center rings, eclipses, index marks."""
    img = Image.new("RGB", (W, H), CREAM)
    _wash(img, CREAM, (242, 238, 228))
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 480)

    # faint grid of dots
    rng = random.Random(44)
    step = max(20, u // 28)
    for y in range(int(H * 0.08), int(H * 0.9), step):
        for x in range(int(W * 0.08), int(W * 0.92), step):
            if rng.random() > 0.55:
                rr = max(1, u // 500)
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 214, 200))

    # primary orbital system
    cx, cy = int(W * 0.46), int(H * 0.42)
    # filled soft aura
    d.ellipse([cx - int(u * 0.40), cy - int(u * 0.40), cx + int(u * 0.40), cy + int(u * 0.40)], fill=(238, 234, 224))
    for i, (frac, col, w) in enumerate([
        (0.38, SAGE_SOFT, mid * 2),
        (0.32, SAGE, mid * 2),
        (0.26, SAGE_DEEP, mid),
        (0.20, STONE_DK, mid),
        (0.14, SAGE, mid),
        (0.09, GOLD, mid),
        (0.05, SAGE_DEEP, mid),
    ]):
        r = int(u * frac)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, w))
    d.ellipse([cx - int(u * 0.025), cy - int(u * 0.025), cx + int(u * 0.025), cy + int(u * 0.025)], fill=SAGE_DEEP)

    # crescent / eclipse cut
    r_e = int(u * 0.11)
    ex, ey = int(W * 0.62), int(H * 0.28)
    d.ellipse([ex - r_e, ey - r_e, ex + r_e, ey + r_e], fill=SAGE)
    d.ellipse([ex - int(r_e * 0.55), ey - int(r_e * 0.7), ex + int(r_e * 0.85), ey + int(r_e * 0.5)], fill=CREAM)

    # secondary system bottom-right
    cx2, cy2 = int(W * 0.72), int(H * 0.72)
    r2 = int(u * 0.12)
    d.ellipse([cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2], fill=CLAY)
    d.ellipse([cx2 - int(r2 * 0.7), cy2 - int(r2 * 0.7), cx2 + int(r2 * 0.7), cy2 + int(r2 * 0.7)],
              outline=CREAM, width=mid)
    d.ellipse([cx2 - int(r2 * 0.35), cy2 - int(r2 * 0.35), cx2 + int(r2 * 0.35), cy2 + int(r2 * 0.35)], fill=CREAM)
    d.ellipse([cx2 - int(r2 * 0.12), cy2 - int(r2 * 0.12), cx2 + int(r2 * 0.12), cy2 + int(r2 * 0.12)], fill=GOLD)

    # orbital arc connecting centers
    d.arc([int(W * 0.25), int(H * 0.25), int(W * 0.85), int(H * 0.85)], 20, 120, fill=STONE_DK, width=hair * 2)

    # index bars
    d.rectangle([int(W * 0.10), int(H * 0.88), int(W * 0.42), int(H * 0.892)], fill=STONE_DK)
    d.rectangle([int(W * 0.45), int(H * 0.88), int(W * 0.58), int(H * 0.892)], fill=SAGE)
    d.rectangle([int(W * 0.61), int(H * 0.88), int(W * 0.68), int(H * 0.892)], fill=GOLD)

    m = int(u * 0.042)
    d.rectangle([m, m, W - m, H - m], outline=STONE, width=mid)
    return img


def poster_05_grid_calm(W, H):
    """Curated modular study — each cell a miniature composition."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 500)

    # header
    d.rectangle([0, 0, W, int(H * 0.11)], fill=SAGE_DEEP)
    d.text((W // 2, int(H * 0.045)), "FORM  ·  SPACE  ·  CALM", font=_font(max(12, u * 0.022), True),
           fill=CREAM, anchor="mm")
    d.text((W // 2, int(H * 0.08)), "MODULAR STUDY", font=_font(max(9, u * 0.014)), fill=GOLD, anchor="mm")

    margin = int(u * 0.07)
    top = int(H * 0.14)
    bot = int(H * 0.07)
    cols, rows = 3, 4
    gap = int(u * 0.018)
    cw = (W - 2 * margin - (cols - 1) * gap) // cols
    ch = (H - top - bot - (rows - 1) * gap) // rows

    # richer cell programs
    cells = [
        (SAGE, "orbit"),
        (CREAM, "ladder"),
        (STONE, "nest_sq"),
        (CREAM, "eclipse"),
        (SAGE_DEEP, "halo"),
        (CLAY, "window"),
        (SAGE_SOFT, "triad"),
        (CREAM, "pulse"),
        (SAGE, "slice"),
        (CREAM, "axis"),
        (STONE_DK, "seed"),
        (SAGE_SOFT, "split_ring"),
    ]
    i = 0
    for r in range(rows):
        for c in range(cols):
            x = margin + c * (cw + gap)
            y = top + r * (ch + gap)
            bg, motif = cells[i]
            d.rectangle([x, y, x + cw, y + ch], fill=bg)
            if bg == CREAM:
                d.rectangle([x, y, x + cw, y + ch], outline=SAGE, width=hair * 2)
            cx, cy = x + cw // 2, y + ch // 2
            s = min(cw, ch) // 3
            pad = min(cw, ch) // 6

            if motif == "orbit":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
                d.ellipse([cx - int(s * 0.65), cy - int(s * 0.65), cx + int(s * 0.65), cy + int(s * 0.65)],
                          outline=SAGE_DEEP, width=max(2, s // 8))
                d.ellipse([cx - s // 4, cy - s // 4, cx + s // 4, cy + s // 4], fill=GOLD)
            elif motif == "ladder":
                for k in range(4):
                    yy = y + pad + k * (ch - 2 * pad) // 3
                    d.rectangle([x + pad, yy, x + cw - pad, yy + max(2, hair * 2)], fill=SAGE_DEEP)
                d.rectangle([cx - hair, y + pad, cx + hair, y + ch - pad], fill=STONE_DK)
            elif motif == "nest_sq":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
                d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=SAGE_DEEP)
                d.rectangle([cx - s // 5, cy - s // 5, cx + s // 5, cy + s // 5], fill=GOLD)
            elif motif == "eclipse":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=SAGE)
                d.ellipse([cx - s // 3, cy - s, cx + s, cy + s // 2], fill=CREAM)
            elif motif == "halo":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=SAGE_SOFT)
                d.ellipse([cx - int(s * 0.55), cy - int(s * 0.55), cx + int(s * 0.55), cy + int(s * 0.55)], fill=CREAM)
                d.ellipse([cx - s // 4, cy - s // 4, cx + s // 4, cy + s // 4], fill=CLAY)
            elif motif == "window":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
                d.rectangle([cx - s, cy - hair, cx + s, cy + hair], fill=SAGE_DEEP)
                d.rectangle([cx - hair, cy - s, cx + hair, cy + s], fill=SAGE_DEEP)
            elif motif == "triad":
                for j, (dx, dy) in enumerate([(-0.35, 0.2), (0.35, 0.2), (0, -0.35)]):
                    col = (CREAM, GOLD, SAGE_DEEP)[j]
                    d.ellipse([cx + dx * s * 2 - s // 3, cy + dy * s * 2 - s // 3,
                               cx + dx * s * 2 + s // 3, cy + dy * s * 2 + s // 3], fill=col)
            elif motif == "pulse":
                for k, frac in enumerate([1.0, 0.65, 0.35]):
                    rr = int(s * frac)
                    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                              outline=SAGE_DEEP if k < 2 else GOLD, width=max(2, s // 10))
            elif motif == "slice":
                d.pieslice([cx - s, cy - s, cx + s, cy + s], 200, 40, fill=CREAM)
                d.pieslice([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], 20, 160, fill=GOLD)
            elif motif == "axis":
                t = max(3, s // 5)
                d.rectangle([cx - t, y + pad, cx + t, y + ch - pad], fill=SAGE_DEEP)
                d.rectangle([x + pad, cy - t, x + cw - pad, cy + t], fill=SAGE_DEEP)
                d.ellipse([cx - s // 3, cy - s // 3, cx + s // 3, cy + s // 3], fill=CLAY)
            elif motif == "seed":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=SAGE_SOFT)
                d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=CREAM)
                d.ellipse([cx - s // 6, cy - s // 6, cx + s // 6, cy + s // 6], fill=GOLD)
            elif motif == "split_ring":
                d.rectangle([x, y, x + cw // 2, y + ch], fill=SAGE)
                d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=CREAM, width=max(3, s // 6))
                d.ellipse([cx - s // 3, cy - s // 3, cx + s // 3, cy + s // 3], fill=CREAM)
            i += 1

    d.rectangle([margin, H - int(H * 0.04), W - margin, H - int(H * 0.035)], fill=SAGE_DEEP)
    return img


def poster_06_path_stone(W, H):
    """Zen path — organic field, graded stones, river line, moon."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    hair = max(1, u // 900)
    mid = max(2, u // 480)
    rng = random.Random(66)

    # layered organic sage fields (blobs)
    _organic_blob(d, int(W * 0.75), int(H * 0.22), u * 0.42, u * 0.32, SAGE_SOFT, seed=1)
    _organic_blob(d, int(W * 0.70), int(H * 0.28), u * 0.32, u * 0.26, SAGE, seed=2)
    _organic_blob(d, int(W * 0.82), int(H * 0.18), u * 0.18, u * 0.15, SAGE_DEEP, seed=3)

    # lower ground
    d.rectangle([0, int(H * 0.68), W, H], fill=CREAM_WARM)
    # soft horizon wave
    pts = []
    for k in range(60):
        t = k / 59
        pts.append((W * t, H * (0.66 + 0.025 * math.sin(t * math.pi * 4))))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=STONE)

    # river / path curve
    path = []
    for k in range(50):
        t = k / 49
        x = W * (0.12 + 0.75 * t)
        y = H * (0.22 + 0.58 * t + 0.04 * math.sin(t * math.pi * 2.5))
        path.append((x, y))
    d.line(path, fill=SAGE_DEEP, width=max(2, mid))
    # parallel soft path
    path2 = [(x + u * 0.012, y + u * 0.008) for x, y in path]
    d.line(path2, fill=STONE_DK, width=hair)

    # graded stepping stones along path
    for i in range(12):
        t = (i + 0.5) / 12
        x = W * (0.12 + 0.75 * t)
        y = H * (0.22 + 0.58 * t + 0.04 * math.sin(t * math.pi * 2.5))
        rx = u * (0.035 + 0.025 * math.sin(i * 1.7))
        ry = rx * rng.uniform(0.72, 0.95)
        # color progression
        if i % 4 == 0:
            col = CLAY
        elif i % 3 == 0:
            col = STONE_DK
        else:
            col = STONE
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=col)
        # highlight + rim
        d.ellipse([x - rx * 0.45, y - ry * 0.55, x + rx * 0.05, y - ry * 0.05],
                  fill=tuple(min(255, c + 22) for c in col))
        d.ellipse([x - rx, y - ry, x + rx, y + ry], outline=SAGE_DEEP if i % 2 else STONE_DK, width=hair)

    # moon / sun disc upper path
    r = int(u * 0.055)
    mx, my = int(W * 0.82), int(H * 0.16)
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=GOLD)
    d.ellipse([mx - int(r * 0.55), my - int(r * 0.55), mx + int(r * 0.55), my + int(r * 0.55)], fill=CREAM)
    d.ellipse([mx - int(r * 0.2), my - int(r * 0.2), mx + int(r * 0.2), my + int(r * 0.2)], fill=GOLD)

    # small satellite stones near moon
    for j, (dx, dy) in enumerate([(-0.08, 0.04), (-0.05, -0.06), (0.06, 0.05)]):
        rr = u * 0.015
        d.ellipse([mx + W * dx - rr, my + H * dy - rr, mx + W * dx + rr, my + H * dy + rr],
                  fill=STONE if j else CLAY)

    # micro botanical marks (abstract stems)
    for i in range(5):
        x0 = W * (0.15 + i * 0.08)
        y0 = H * 0.78
        d.line([(x0, y0), (x0 + u * 0.01, y0 - u * 0.06)], fill=SAGE, width=hair)
        d.ellipse([x0 + u * 0.005, y0 - u * 0.07, x0 + u * 0.02, y0 - u * 0.055], fill=SAGE_DEEP)

    m = int(u * 0.04)
    d.rectangle([m, m, W - m, H - m], outline=SAGE_DEEP, width=mid)
    _corner_marks(d, W, H, m + mid, int(u * 0.025), STONE_DK, hair * 2)
    return img


POSTERS = [
    ("01_balance_forms", "Balance Forms", poster_01_balance_forms),
    ("02_stacked_horizon", "Stacked Horizon", poster_02_stacked_horizon),
    ("03_arch_still", "Arch Still", poster_03_arch_still),
    ("04_rings_field", "Rings Field", poster_04_rings_field),
    ("05_grid_calm", "Grid Calm", poster_05_grid_calm),
    ("06_path_stone", "Path Stone", poster_06_path_stone),
]


def render_print(fn, w_in, h_in, dpi=DPI_PRINT, supersample=SUPERSAMPLE):
    ss = max(1, int(supersample))
    if dpi <= DPI_PREVIEW:
        ss = 1
    W_hi, H_hi = _px(w_in, dpi * ss), _px(h_in, dpi * ss)
    if W_hi * H_hi > 90_000_000 and ss > 1:
        ss = 1
        W_hi, H_hi = _px(w_in, dpi), _px(h_in, dpi)
    raw = fn(W_hi, H_hi)
    W, H = _px(w_in, dpi), _px(h_in, dpi)
    if ss > 1 and raw.size != (W, H):
        raw = raw.resize((W, H), Image.Resampling.LANCZOS)
    return _finish(raw)


def save_jpg(img, path: Path, dpi=DPI_PRINT, quality=90):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=quality, dpi=(dpi, dpi), optimize=True, progressive=True, subsampling=2)
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {path.relative_to(OUT)}  ({mb:.2f} MB, {img.width}×{img.height})")


def generate_prints(preview_only=False):
    _ensure()
    if preview_only:
        print("=== Prints skipped ===")
        return
    if PRINTS.exists():
        shutil.rmtree(PRINTS)
    PRINTS.mkdir(parents=True, exist_ok=True)
    print(f"=== Sage neutral prints @ {DPI_PRINT} dpi ===")
    for slug, title, fn in POSTERS:
        folder = PRINTS / slug
        folder.mkdir(parents=True, exist_ok=True)
        print(f"-- {title}")
        for size_name, (w_in, h_in) in SIZES.items():
            img = render_print(fn, w_in, h_in, DPI_PRINT)
            q = JPEG_Q_LARGE if size_name in LARGE_KEYS else JPEG_Q_STD
            save_jpg(img, folder / f"{slug}_{size_name}_{DPI_PRINT}dpi.jpg", DPI_PRINT, q)


def _mockup_frame(poster, canvas=1600):
    S = canvas
    img = Image.new("RGB", (S, S), (232, 228, 220))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(232 - 6 * t), int(228 - 5 * t), int(220 - 4 * t)))
    d.rectangle([0, int(S * 0.80), S, S], fill=(70, 68, 62))
    pw = int(S * 0.40)
    ph = int(pw * poster.height / poster.width)
    poster = poster.resize((pw, ph), Image.Resampling.LANCZOS)
    px, py = (S - pw) // 2, int(S * 0.10)
    frame = max(18, S // 70)
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [px - frame + 14, py - frame + 18, px + pw + frame + 14, py + ph + frame + 18], fill=(0, 0, 0, 65)
    )
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px - frame, py - frame, px + pw + frame, py + ph + frame], fill=(40, 40, 38))
    d.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], fill=CREAM)
    img.paste(poster, (px, py))
    return img


def build_previews():
    _ensure()
    print("=== Sage listing previews ===")
    masters = []
    for slug, title, fn in POSTERS:
        masters.append((slug, title, render_print(fn, 8.0, 12.0, DPI_PREVIEW)))

    S = 1600
    hero = _mockup_frame(masters[0][2], S)
    d = ImageDraw.Draw(hero)
    d.rectangle([0, 1480, S, S], fill=SAGE_DEEP)
    d.text((S // 2, 1515), "SAGE GREEN NEUTRAL PRINT SET", font=_font(26, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 1560), "6 abstract posters  ·  quiet luxury  ·  300 dpi", font=_font(15), fill=GOLD, anchor="mt")
    save_jpg(hero, PREVIEWS / "sage_preview_1_hero.jpg", DPI_PREVIEW, 92)

    set_img = Image.new("RGB", (S, S), (236, 232, 224))
    d = ImageDraw.Draw(set_img)
    d.rectangle([0, int(S * 0.78), S, S], fill=(60, 58, 52))
    d.text((S // 2, 55), "SET OF 6  ·  NEUTRAL GALLERY", font=_font(28, True), fill=SAGE_DEEP, anchor="mt")
    d.text((S // 2, 100), "Sage · cream · stone · quiet luxury", font=_font(16), fill=SOFT, anchor="mt")
    chosen = [0, 1, 3]
    pw, gap = 340, 48
    total = 3 * pw + 2 * gap
    x0 = (S - total) // 2
    y0 = 180
    for i, idx in enumerate(chosen):
        pimg = masters[idx][2]
        ph = int(pw * pimg.height / pimg.width)
        pimg = pimg.resize((pw, ph), Image.Resampling.LANCZOS)
        x = x0 + i * (pw + gap)
        d.rectangle([x - 14, y0 - 14, x + pw + 14, y0 + ph + 14], fill=(32, 32, 30))
        d.rectangle([x - 5, y0 - 5, x + pw + 5, y0 + ph + 5], fill=CREAM)
        set_img.paste(pimg, (x, y0))
        d = ImageDraw.Draw(set_img)
    d.rectangle([0, S - 90, S, S], fill=SAGE_DEEP)
    d.text((S // 2, S - 45), "MathRelaxing  ·  Sage Neutral Abstract Set", font=_font(18), fill=GOLD, anchor="mm")
    save_jpg(set_img, PREVIEWS / "sage_preview_2_set.jpg", DPI_PREVIEW, 92)

    incl = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, S, 160], fill=SAGE_DEEP)
    d.text((S // 2, 55), "WHAT'S INCLUDED", font=_font(34, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 110), "Instant download  ·  print at home or shop", font=_font(18), fill=GOLD, anchor="mt")
    items = [
        ("6", "Abstract posters", "Sage neutral quiet luxury", SAGE, CREAM),
        ("5", "Print sizes", "Up to 24×36 in @ 300 dpi", CLAY, CREAM),
        ("300", "DPI masters", "Print-shop ready JPG", GOLD, INK),
        ("1", "ZIP pack", "Folders + README", SAGE_DEEP, CREAM),
    ]
    y = 220
    for num, title, sub, bubble, ink in items:
        d.ellipse([120, y, 220, y + 100], fill=bubble)
        d.text((170, y + 50), num, font=_font(26, True), fill=ink, anchor="mm")
        d.text((260, y + 30), title, font=_font(28, True), fill=INK, anchor="lt")
        d.text((260, y + 70), sub, font=_font(18), fill=SOFT, anchor="lt")
        y += 140
    d.rectangle([100, 820, S - 100, 830], fill=GOLD)
    d.text((S // 2, 900), "Palette: sage · cream · stone · clay · soft gold", font=_font(18), fill=SAGE_DEEP, anchor="mt")
    tw, gap = 200, 20
    total = 6 * tw + 5 * gap
    x0 = (S - total) // 2
    yy = 1000
    for i, (_, _, m) in enumerate(masters):
        th = int(tw * m.height / m.width)
        incl.paste(m.resize((tw, th), Image.Resampling.LANCZOS), (x0 + i * (tw + gap), yy))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, S - 70, S, S], fill=SAGE_DEEP)
    d.text((S // 2, S - 35), "Original compositions  ·  MathRelaxing", font=_font(15), fill=CREAM, anchor="mm")
    save_jpg(incl, PREVIEWS / "sage_preview_3_included.jpg", DPI_PREVIEW, 92)

    for i, (slug, title, m) in enumerate(masters):
        plate = Image.new("RGB", (S, S), CREAM)
        scale = min(int(S * 0.55) / m.width, int(S * 0.82) / m.height)
        pw, ph = int(m.width * scale), int(m.height * scale)
        pimg = m.resize((pw, ph), Image.Resampling.LANCZOS)
        px, py = (S - pw) // 2, int(S * 0.08)
        plate.paste(pimg, (px, py))
        d = ImageDraw.Draw(plate)
        d.rectangle([0, S - 100, S, S], fill=SAGE_DEEP)
        d.text((S // 2, S - 60), f"{i + 1:02d}  ·  {title.upper()}", font=_font(20, True), fill=GOLD, anchor="mm")
        d.text((S // 2, S - 30), "MathRelaxing Sage Neutral Set", font=_font(14), fill=CREAM, anchor="mm")
        short = slug.split("_", 1)[1]
        save_jpg(plate, PREVIEWS / f"sage_preview_{i + 4}_{short}.jpg", DPI_PREVIEW, 92)

    grid = Image.new("RGB", (S, S), SAGE_DEEP)
    d = ImageDraw.Draw(grid)
    d.text((S // 2, 40), "ALL 6 DESIGNS", font=_font(30, True), fill=CREAM, anchor="mt")
    d.rectangle([S // 2 - 60, 85, S // 2 + 60, 88], fill=GOLD)
    tw, th = 420, 630
    gapx, gapy = 40, 50
    x0 = (S - 3 * tw - 2 * gapx) // 2
    y0 = 120
    for i, (_, title, m) in enumerate(masters):
        c, r = i % 3, i // 3
        x = x0 + c * (tw + gapx)
        y = y0 + r * (th + gapy)
        d.rectangle([x - 3, y - 3, x + tw + 3, y + th + 3], fill=GOLD)
        grid.paste(m.resize((tw, th), Image.Resampling.LANCZOS), (x, y))
        d = ImageDraw.Draw(grid)
        d.text((x + tw // 2, y + th + 14), title.upper(), font=_font(13, True), fill=GOLD, anchor="mt")
    d.rectangle([0, S - 60, S, S], fill=(30, 40, 32))
    d.text((S // 2, S - 30), "Digital download  ·  up to 24×36  ·  300 dpi", font=_font(15), fill=CREAM, anchor="mm")
    save_jpg(grid, PREVIEWS / "sage_preview_10_all.jpg", DPI_PREVIEW, 92)
    print(f"  previews → {PREVIEWS}")


README = """MathRelaxing — Sage Green Neutral Abstract Print Set
=====================================================
6 original quiet-luxury abstract posters (sage / cream / stone).

PRINTS
  01_balance_forms
  02_stacked_horizon
  03_arch_still
  04_rings_field
  05_grid_calm
  06_path_stone

SIZES @ 300 dpi (in download packs)
  24×36, 18×24, 16×20, 12×18, A4

Scale 24×36 down for other frames. Matte paper looks best.
Personal use only. © MathRelaxing
"""


def build_zip():
    """Single combined if under limit; else 2 packs of 3 designs."""
    print("=== Sage ZIP(s) ===")
    zip_all = OUT / "MathRelaxing_Sage_Neutral_Print_Set.zip"
    zip_a = OUT / "MathRelaxing_Sage_Neutral_Pack_A.zip"
    zip_b = OUT / "MathRelaxing_Sage_Neutral_Pack_B.zip"
    for p in (zip_all, zip_a, zip_b):
        if p.exists():
            p.unlink()

    def pack(path, slugs):
        n = 0
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("README.txt", README)
            for slug, _, _ in POSTERS:
                if slugs and slug not in slugs:
                    continue
                folder = PRINTS / slug
                if not folder.is_dir():
                    continue
                for f in sorted(folder.glob("*.jpg")):
                    sk = f.stem[len(slug) + 1 : -len(f"_{DPI_PRINT}dpi")]
                    if sk not in PACK_SIZES:
                        continue
                    zf.write(f, f"{slug}/{f.name}")
                    n += 1
        mb = path.stat().st_size / (1024 * 1024)
        print(f"  {path.name} ({mb:.1f} MB, {n} files)")
        return mb

    mb = pack(zip_all, None)
    if mb <= 19.0:
        print("  Single ZIP under limit")
        return [zip_all]
    print("  Split Pack A (01-03) + Pack B (04-06)")
    if zip_all.exists():
        zip_all.unlink()
    a = [p[0] for p in POSTERS[:3]]
    b = [p[0] for p in POSTERS[3:]]
    pack(zip_a, a)
    pack(zip_b, b)
    return [zip_a, zip_b]


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
