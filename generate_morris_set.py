"""
generate_morris_set.py — William Morris–inspired botanical print set (full SKU)
==============================================================================
Arts & Crafts botanical wall art: 6 original compositions inspired by Morris
motifs (willow, strawberry garden, trellis rose, pimpernel, honeysuckle, acanthus).
Public-domain-era style; original drawings (not scanned wallpapers).

Large-poster 300 dpi + standard sizes + listing previews + ZIP.

  python generate_morris_set.py
  python generate_morris_set.py --preview-only
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
OUT = BASE / "morris_set"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"
ZIP_PATH = OUT / "MathRelaxing_Morris_Botanical_Print_Set.zip"
ZIP_LARGE_A = OUT / "MathRelaxing_Morris_LargePoster_A.zip"  # designs 01–03
ZIP_LARGE_B = OUT / "MathRelaxing_Morris_LargePoster_B.zip"  # designs 04–06
ZIP_STD = OUT / "MathRelaxing_Morris_Standard.zip"
LARGE_KEYS = {"2x3_24x36", "3x4_18x24", "4x5_24x30", "5x7_20x28", "A1", "A2"}
STD_KEYS = {"2x3_12x18", "3x4_12x16", "4x5_16x20", "5x7_10x14", "A3", "A4"}

DPI_PRINT = 300
DPI_PREVIEW = 160
# Dense botanical art compresses larger — keep large masters under Etsy packs
JPEG_Q_LARGE = 70
JPEG_Q_STD = 82
SUPERSAMPLE = 2

SIZES = {
    "2x3_24x36": (24.0, 36.0),
    "3x4_18x24": (18.0, 24.0),
    "4x5_24x30": (24.0, 30.0),
    "5x7_20x28": (20.0, 28.0),
    "A1": (23.39, 33.11),
    "A2": (16.54, 23.39),
    "2x3_12x18": (12.0, 18.0),
    "3x4_12x16": (12.0, 16.0),
    "4x5_16x20": (16.0, 20.0),
    "5x7_10x14": (10.0, 14.0),
    "A3": (11.69, 16.54),
    "A4": (8.27, 11.69),
}
LARGE_KEYS = {"2x3_24x36", "3x4_18x24", "4x5_24x30", "5x7_20x28", "A1", "A2"}

# Morris-inspired palette
CREAM = (244, 236, 218)
CREAM_WARM = (236, 226, 205)
INDIGO = (28, 48, 78)
INDIGO_DEEP = (18, 32, 55)
SAGE = (98, 128, 96)
LEAF = (58, 102, 72)
LEAF_DK = (40, 72, 52)
STEM = (72, 58, 40)
RUST = (158, 68, 52)
BERRY = (170, 52, 58)
ROSE = (186, 118, 118)
OCHRE = (186, 148, 72)
INK = (32, 36, 42)
SOFT = (110, 100, 88)
GOLD = (176, 142, 70)


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
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.06)
    img = ImageEnhance.Sharpness(img).enhance(1.04)
    return img


def _border(d, W, H, m, color=INK, w=3):
    d.rectangle([m, m, W - m, H - m], outline=color, width=max(1, w))
    gap = max(4, m // 6)
    d.rectangle([m + gap, m + gap, W - m - gap, H - m - gap], outline=color, width=max(1, w // 2))


def _poly(d, pts, fill, outline=None, ow=1):
    if len(pts) < 3:
        return
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=max(1, ow))


def _leaf(d, cx, cy, length, width, angle_deg, fill, outline=None, outline_w=1, lobes=0):
    """Pointed / willow leaf. lobes>0 adds soft serration for denser Morris read."""
    ang = math.radians(angle_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    n = 36
    for i in range(n):
        t = 2 * math.pi * i / n
        # base teardrop
        rx = width * math.sin(t) * (0.55 + 0.45 * abs(math.sin(t / 2)))
        ry = length * (0.5 - 0.5 * math.cos(t))
        if lobes and abs(rx) > 1e-6:
            rx *= 1.0 + 0.12 * math.sin(lobes * t)
        # tip along +angle (down-ish in image coords via rotation)
        x = cx + rx * ca - (ry - length * 0.12) * sa
        y = cy + rx * sa + (ry - length * 0.12) * ca
        pts.append((x, y))
    _poly(d, pts, fill, outline, outline_w)
    # midrib
    tip_x = cx - length * 0.78 * sa
    tip_y = cy + length * 0.78 * ca
    d.line([(cx, cy), (tip_x, tip_y)], fill=outline or LEAF_DK, width=max(1, outline_w))
    # secondary veins
    if length > 12:
        for f in (0.35, 0.55, 0.72):
            mx = cx + (tip_x - cx) * f
            my = cy + (tip_y - cy) * f
            vx, vy = (tip_x - cx) * 0.12, (tip_y - cy) * 0.12
            # perpendicular
            px, py = -vy * 0.9, vx * 0.9
            d.line([(mx, my), (mx + px, my + py)], fill=outline or LEAF_DK, width=max(1, outline_w // 2 or 1))
            d.line([(mx, my), (mx - px, my - py)], fill=outline or LEAF_DK, width=max(1, outline_w // 2 or 1))


def _stem(d, points, color=STEM, width=3):
    if len(points) < 2:
        return
    d.line(points, fill=color, width=max(1, width), joint="curve")


def _rose(d, cx, cy, r, petal_col, center_col, outline=None, rot=0, layers=3):
    """Layered rose — denser than simple petal circles."""
    ow = max(1, int(r // 14) or 1)
    for layer in range(layers, 0, -1):
        pr = r * (0.45 + 0.22 * layer)
        n = 5 + layer
        for i in range(n):
            a = math.radians(rot + i * (360 / n) + layer * 12)
            px = cx + pr * 0.42 * math.cos(a)
            py = cy + pr * 0.42 * math.sin(a)
            rr = pr * (0.38 + 0.06 * layer)
            # slight color deepen per layer
            col = tuple(max(0, min(255, int(c * (0.88 + 0.04 * layer)))) for c in petal_col)
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col, outline=outline, width=ow if outline else 0)
    d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=center_col)
    d.ellipse([cx - r * 0.10, cy - r * 0.10, cx + r * 0.10, cy + r * 0.10], fill=OCHRE)


def _blossom(d, cx, cy, r, petal_col, center_col, petals=5, rot=0, outline=None):
    ow = max(1, int(r // 16) or 1)
    for i in range(petals):
        a = math.radians(rot + i * (360 / petals))
        px = cx + r * 0.52 * math.cos(a)
        py = cy + r * 0.52 * math.sin(a)
        d.ellipse([px - r * 0.42, py - r * 0.42, px + r * 0.42, py + r * 0.42],
                  fill=petal_col, outline=outline, width=ow if outline else 0)
    d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28], fill=center_col)


def _strawberry(d, cx, cy, r, col=BERRY):
    """Strawberry with seeds + sepal crown."""
    d.ellipse([cx - r * 0.7, cy - r * 0.55, cx + r * 0.7, cy + r * 0.85], fill=col)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.05, cy + r * 0.05],
              fill=(min(255, col[0] + 35), min(255, col[1] + 25), min(255, col[2] + 25)))
    rng = random.Random(int(cx * 7 + cy * 3) % 9973)
    for _ in range(max(4, int(r // 2))):
        sx = cx + rng.uniform(-0.45, 0.45) * r
        sy = cy + rng.uniform(-0.25, 0.55) * r
        sr = max(1.2, r * 0.07)
        d.ellipse([sx - sr, sy - sr * 0.7, sx + sr, sy + sr * 0.7], fill=OCHRE)
    for i in range(5):
        _leaf(d, cx, cy - r * 0.5, r * 0.55, r * 0.18, -90 + i * 72, LEAF, LEAF_DK, 1)


def _bird(d, cx, cy, scale, facing=1, body=INDIGO, breast=ROSE, beak=OCHRE, wing=None):
    """Thrush-like bird with wing bars — Morris garden motif."""
    s = scale
    wing = wing or LEAF_DK
    # tail feathers
    d.polygon([
        (cx - 1.15 * s * facing if facing == 1 else cx + 1.15 * s,
         cy),
        (cx - facing * 2.0 * s, cy - 0.45 * s),
        (cx - facing * 1.85 * s, cy + 0.05 * s),
        (cx - facing * 1.95 * s, cy + 0.4 * s),
        (cx - facing * 1.0 * s, cy + 0.35 * s),
    ], fill=body)
    # body
    d.ellipse([cx - 1.15 * s, cy - 0.65 * s, cx + 0.95 * s, cy + 0.85 * s], fill=body)
    # breast
    d.ellipse([cx - 0.35 * s, cy - 0.15 * s, cx + 0.75 * s, cy + 0.7 * s], fill=breast)
    # wing
    d.ellipse([cx - 0.85 * s, cy - 0.4 * s, cx + 0.35 * s, cy + 0.4 * s], fill=wing)
    d.arc([cx - 0.75 * s, cy - 0.3 * s, cx + 0.2 * s, cy + 0.3 * s], 200, 340, fill=CREAM, width=max(1, int(s // 12)))
    # head
    hx = cx + facing * 0.55 * s
    d.ellipse([hx - 0.55 * s, cy - 1.15 * s, hx + 0.55 * s, cy - 0.05 * s], fill=body)
    # beak
    bx = hx + facing * 0.5 * s
    d.polygon([
        (bx, cy - 0.6 * s),
        (bx + facing * 0.55 * s, cy - 0.42 * s),
        (bx, cy - 0.28 * s),
    ], fill=beak)
    # eye
    ex = hx + facing * 0.12 * s
    d.ellipse([ex - 0.1 * s, cy - 0.8 * s, ex + 0.1 * s, cy - 0.6 * s], fill=CREAM)
    d.ellipse([ex - 0.05 * s, cy - 0.76 * s, ex + 0.05 * s, cy - 0.66 * s], fill=INK)
    # feet
    d.line([(cx + 0.1 * s, cy + 0.8 * s), (cx + 0.15 * s, cy + 1.05 * s)], fill=beak, width=max(1, int(s // 14)))
    d.line([(cx + 0.35 * s, cy + 0.75 * s), (cx + 0.45 * s, cy + 1.0 * s)], fill=beak, width=max(1, int(s // 14)))


def _fill_dots(d, W, H, m, color, spacing, r, rng):
    """Subtle background scatter (block-print texture)."""
    y = m
    while y < H - m:
        x = m + (0 if int(y / spacing) % 2 == 0 else spacing // 2)
        while x < W - m:
            if rng.random() > 0.35:
                d.ellipse([x - r, y - r, x + r, y + r], fill=color)
            x += spacing
        y += spacing


def _vine_path(x0, y0, x1, y1, amp, waves, n=48, phase=0.0):
    pts = []
    for k in range(n):
        t = k / (n - 1)
        x = x0 + (x1 - x0) * t + amp * math.sin(t * math.pi * waves + phase)
        y = y0 + (y1 - y0) * t
        pts.append((x, y))
    return pts


# ── Six compositions — lethal density ─────────────────────────────────────────

def poster_01_willow(W, H):
    """Willow Boughs — dense interlaced willow leaves (Morris Willow spirit)."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(101)
    ow = max(1, u // 700)

    # warm paper vignette
    for y in range(H):
        t = abs(y / H - 0.5) * 2
        if t > 0.7:
            f = (t - 0.7) / 0.3
            col = (int(CREAM[0] - 10 * f), int(CREAM[1] - 8 * f), int(CREAM[2] - 6 * f))
            d.line([(0, y), (W, y)], fill=col)

    _fill_dots(d, W, H, int(u * 0.05), (228, 220, 200), max(10, u // 55), max(1, u // 500), rng)

    # background soft willow layer (lighter, behind)
    for si in range(14):
        x0 = W * (0.02 + si * 0.07)
        pts = _vine_path(x0, H * 0.02, x0 + W * 0.02, H * 0.98, W * 0.055, 2.2, 55, si * 0.9)
        _stem(d, pts, (160, 170, 140), max(1, u // 500))
        for k in range(1, len(pts) - 1, 1):
            if k % 2:
                continue
            x, y = pts[k]
            side = 1 if (k + si) % 4 < 2 else -1
            L = u * rng.uniform(0.04, 0.07)
            _leaf(d, x, y, L, L * 0.26, 55 * side + rng.uniform(-15, 15),
                  (140, 165, 120), (100, 125, 95), 1, lobes=0)

    # foreground dark willow stems — denser
    for si in range(9):
        x0 = W * (0.08 + si * 0.105)
        pts = _vine_path(x0, H * 0.03, x0 - W * 0.01, H * 0.97, W * 0.07, 1.8, 60, si * 1.3)
        _stem(d, pts, STEM if si % 2 == 0 else LEAF_DK, max(2, u // 260))
        for k in range(1, len(pts) - 1):
            x, y = pts[k]
            side = 1 if k % 2 == 0 else -1
            # opposite pair every other node
            L = u * rng.uniform(0.055, 0.095)
            col = LEAF if rng.random() > 0.4 else SAGE
            _leaf(d, x, y, L, L * 0.28, 48 * side + rng.uniform(-18, 18) + si * 3,
                  col, LEAF_DK, ow, lobes=3)
            if k % 3 == 0:
                L2 = L * 0.7
                _leaf(d, x, y, L2, L2 * 0.25, 100 * side + rng.uniform(-10, 10),
                      SAGE if col == LEAF else LEAF, LEAF_DK, ow)

    # interlacing cross-stems
    for si in range(5):
        y0 = H * (0.15 + si * 0.16)
        pts = _vine_path(W * 0.05, y0, W * 0.95, y0 + H * 0.04, H * 0.03, 3, 40, si)
        _stem(d, pts, (90, 75, 55), max(1, u // 400))
        for k in range(2, len(pts) - 2, 2):
            x, y = pts[k]
            _leaf(d, x, y, u * 0.05, u * 0.014, rng.uniform(-30, 30), LEAF, LEAF_DK, ow)

    _border(d, W, H, int(u * 0.038), INK, max(2, u // 480))
    return img


def poster_02_strawberry(W, H):
    """Strawberry Garden — indigo field thrushes, berries, dense foliage."""
    img = Image.new("RGB", (W, H), INDIGO_DEEP)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(202)
    ow = max(1, u // 800)

    # indigo depth wash
    for y in range(0, H, max(1, H // 500)):
        t = y / H
        col = (
            int(INDIGO_DEEP[0] + 14 * math.sin(t * 5)),
            int(INDIGO_DEEP[1] + 18 * math.sin(t * 4 + 0.5)),
            int(INDIGO_DEEP[2] + 10 * math.cos(t * 3)),
        )
        d.line([(0, y), (W, y)], fill=col)

    # soft secondary leaves filling field
    for _ in range(int(180 * (W * H) / (1200 * 1800))):
        x, y = rng.uniform(W * 0.06, W * 0.94), rng.uniform(H * 0.06, H * 0.94)
        _leaf(d, x, y, u * rng.uniform(0.025, 0.05), u * 0.012,
              rng.uniform(0, 360), (35, 70, 55), (25, 50, 40), 1)

    # dense vine columns
    for vi in range(12):
        x0 = W * (0.05 + vi * 0.08)
        pts = _vine_path(x0, H * 0.02, x0 + W * 0.015, H * 0.98, W * 0.04, 3.5 + vi % 3, 70, vi * 0.7)
        _stem(d, pts, (50, 100, 75), max(2, u // 300))
        for k in range(1, len(pts) - 1, 1):
            x, y = pts[k]
            side = 1 if k % 2 == 0 else -1
            _leaf(d, x, y, u * rng.uniform(0.04, 0.065), u * 0.015,
                  70 * side + rng.uniform(-25, 25), (65, 125, 85), (30, 70, 50), ow, lobes=2)
            if k % 4 == 0:
                _strawberry(d, x + side * u * 0.02, y + u * 0.01, u * rng.uniform(0.014, 0.022))
            if k % 6 == 0:
                _blossom(d, x - side * u * 0.022, y, u * 0.016, ROSE, OCHRE, 5, rng.uniform(0, 40), CREAM)
            if k % 9 == 0:
                _blossom(d, x + side * u * 0.03, y - u * 0.01, u * 0.012, CREAM, OCHRE, 5, 10, (200, 190, 170))

    # thrushes on vines
    _bird(d, W * 0.28, H * 0.26, u * 0.075, facing=1, body=(45, 75, 110), breast=(210, 150, 120), wing=(30, 55, 70))
    _bird(d, W * 0.70, H * 0.48, u * 0.07, facing=-1, body=(40, 85, 70), breast=ROSE, wing=(25, 55, 45))
    _bird(d, W * 0.42, H * 0.72, u * 0.06, facing=1, body=(55, 70, 95), breast=(200, 160, 100), wing=LEAF_DK)
    _bird(d, W * 0.78, H * 0.22, u * 0.05, facing=-1, body=INDIGO, breast=(180, 100, 90), wing=(50, 70, 90))

    m = int(u * 0.042)
    d.rectangle([m, m, W - m, H - m], outline=OCHRE, width=max(2, u // 420))
    d.rectangle([m + max(5, m // 4), m + max(5, m // 4), W - m - max(5, m // 4), H - m - max(5, m // 4)],
                outline=CREAM, width=max(1, u // 700))
    return img


def poster_03_trellis(W, H):
    """Trellis Rose — diamond lattice fully clothed in roses & foliage."""
    img = Image.new("RGB", (W, H), CREAM_WARM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(303)
    ow = max(1, u // 750)

    # soft ground tint
    _fill_dots(d, W, H, int(u * 0.04), (220, 210, 190), max(12, u // 50), max(1, u // 450), rng)

    step = int(u * 0.095)
    # diamond trellis
    for y in range(-step, H + step, step):
        for x in range(-step, W + step, step):
            d.line([(x, y + step // 2), (x + step // 2, y), (x + step, y + step // 2),
                    (x + step // 2, y + step), (x, y + step // 2)],
                   fill=(95, 78, 58), width=max(1, u // 550))

    # fill every diamond intersection + midpoints
    for y in range(0, H + step, step // 2):
        for x in range(0, W + step, step // 2):
            # skip some for rhythm
            if (x // (step // 2) + y // (step // 2)) % 3 == 0:
                continue
            r = u * rng.uniform(0.03, 0.048)
            col = ROSE if (x + y) // step % 2 == 0 else RUST
            if rng.random() > 0.55:
                col = (200, 130, 130) if col == ROSE else (170, 90, 70)
            _rose(d, x, y, r, col, OCHRE, STEM, rng.uniform(0, 40), layers=3)
            for j in range(5):
                _leaf(d, x, y, u * rng.uniform(0.035, 0.055), u * 0.012,
                      j * 72 + rng.uniform(-8, 8), LEAF if j % 2 == 0 else SAGE, LEAF_DK, ow, lobes=2)

    # climbing stems over lattice
    for si in range(6):
        pts = _vine_path(W * (0.1 + si * 0.15), H * 0.98, W * (0.12 + si * 0.15), H * 0.02,
                         W * 0.045, 4, 50, si)
        _stem(d, pts, LEAF_DK, max(2, u // 350))
        for k in range(2, len(pts) - 2, 2):
            x, y = pts[k]
            _leaf(d, x, y, u * 0.045, u * 0.013, rng.uniform(-80, 80), LEAF, LEAF_DK, ow)

    _border(d, W, H, int(u * 0.038), INK, max(2, u // 480))
    return img


def poster_04_pimpernel(W, H):
    """Pimpernel Field — continuous scrolling all-over floral (not a sparse grid)."""
    bg = (235, 230, 212)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(404)
    ow = max(1, u // 800)

    # meandering vines covering entire field
    for vi in range(16):
        y0 = H * (-0.05 + vi * 0.07)
        pts = _vine_path(W * 0.0, y0, W * 1.0, y0 + H * 0.08, H * 0.045, 5 + vi % 3, 80, vi * 0.8)
        _stem(d, pts, STEM if vi % 2 == 0 else LEAF_DK, max(2, u // 380))
        for k in range(1, len(pts) - 1, 1):
            x, y = pts[k]
            if y < 0 or y > H:
                continue
            side = 1 if k % 2 == 0 else -1
            kind = (k + vi * 3) % 7
            if kind in (0, 1):
                _leaf(d, x, y, u * 0.048, u * 0.014, 55 * side + rng.uniform(-20, 20),
                      LEAF if kind == 0 else SAGE, LEAF_DK, ow, lobes=3)
            elif kind == 2:
                _blossom(d, x + side * u * 0.015, y, u * 0.022, ROSE, OCHRE, 5, rng.uniform(0, 50), STEM)
            elif kind == 3:
                _blossom(d, x, y, u * 0.02, RUST, CREAM, 6, rng.uniform(0, 30), STEM)
            elif kind == 4:
                _blossom(d, x, y, u * 0.018, OCHRE, RUST, 5, 15, STEM)
            elif kind == 5:
                _strawberry(d, x, y, u * 0.016)
            else:
                for j in range(3):
                    _leaf(d, x, y, u * 0.035, u * 0.01, j * 40 * side, LEAF, LEAF_DK, ow)

    # vertical counter-vines for interlacing
    for vi in range(8):
        x0 = W * (0.08 + vi * 0.12)
        pts = _vine_path(x0, 0, x0, H, W * 0.04, 3, 55, vi)
        _stem(d, pts, (85, 70, 50), max(1, u // 450))
        for k in range(2, len(pts) - 2, 3):
            x, y = pts[k]
            _blossom(d, x, y, u * 0.015, ROSE if k % 2 == 0 else (200, 170, 100), OCHRE, 5, 0, None)
            _leaf(d, x, y, u * 0.04, u * 0.012, rng.uniform(0, 360), SAGE, LEAF_DK, ow)

    # indigo frame band
    m = int(u * 0.05)
    d.rectangle([0, 0, W, m], fill=INDIGO)
    d.rectangle([0, H - m, W, H], fill=INDIGO)
    d.rectangle([0, 0, m, H], fill=INDIGO)
    d.rectangle([W - m, 0, W, H], fill=INDIGO)
    # corner flourishes on frame
    for ox, oy, a0 in [(0.08, 0.08, 45), (0.92, 0.08, 135), (0.92, 0.92, 225), (0.08, 0.92, 315)]:
        for j in range(3):
            _leaf(d, W * ox, H * oy, u * 0.06, u * 0.018, a0 + j * 25, OCHRE, CREAM, ow)
    d.rectangle([m // 2, m // 2, W - m // 2, H - m // 2], outline=OCHRE, width=max(2, u // 480))
    return img


def poster_05_honeysuckle(W, H):
    """Honeysuckle — dense intertwining vines, tube blooms, full coverage."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(505)
    ow = max(1, u // 750)

    _fill_dots(d, W, H, int(u * 0.04), (230, 222, 200), max(14, u // 48), max(1, u // 500), rng)

    def vine(x0, phase, amp, leaf_scale=1.0, bloom_every=4):
        pts = _vine_path(x0, H * 0.01, x0 + W * 0.02, H * 0.99, amp, 2.6, 75, phase)
        _stem(d, pts, STEM, max(3, u // 240))
        # secondary thin stem
        pts2 = [(p[0] + u * 0.012, p[1]) for p in pts]
        _stem(d, pts2, LEAF_DK, max(1, u // 400))
        for k in range(1, len(pts) - 1):
            x, y = pts[k]
            side = 1 if k % 2 == 0 else -1
            L = u * rng.uniform(0.05, 0.08) * leaf_scale
            _leaf(d, x, y, L, L * 0.28, 52 * side + math.sin(k * 0.4) * 25,
                  LEAF if k % 3 else SAGE, LEAF_DK, ow, lobes=2)
            if k % bloom_every == 0:
                ang = 90 * side + rng.uniform(-25, 25)
                br = u * rng.uniform(0.02, 0.032)
                rad = math.radians(ang)
                bx = x + br * 1.6 * math.cos(rad)
                by = y + br * 1.6 * math.sin(rad)
                col = OCHRE if rng.random() > 0.45 else ROSE
                # tube + flared mouth
                d.ellipse([bx - br * 1.1, by - br * 0.45, bx + br * 1.1, by + br * 0.45], fill=col)
                d.ellipse([bx - br * 0.55, by - br * 0.55, bx + br * 0.55, by + br * 0.55], fill=CREAM)
                d.ellipse([bx - br * 0.25, by - br * 0.25, bx + br * 0.25, by + br * 0.25], fill=col)
                # connecting tube from stem
                d.line([(x, y), (bx, by)], fill=col, width=max(2, int(br // 3)))

    # many overlapping vines
    vine(W * 0.10, 0.0, W * 0.07, 1.0, 3)
    vine(W * 0.22, 1.1, W * 0.08, 0.95, 4)
    vine(W * 0.36, 2.0, W * 0.075, 1.05, 3)
    vine(W * 0.50, 0.6, W * 0.09, 1.0, 4)
    vine(W * 0.64, 1.7, W * 0.08, 0.9, 3)
    vine(W * 0.78, 2.5, W * 0.07, 1.0, 4)
    vine(W * 0.90, 0.3, W * 0.06, 0.85, 5)

    # horizontal weaving vines
    for hi in range(4):
        y0 = H * (0.18 + hi * 0.2)
        pts = _vine_path(W * 0.02, y0, W * 0.98, y0 + H * 0.03, H * 0.025, 4, 45, hi)
        _stem(d, pts, (100, 85, 60), max(2, u // 380))
        for k in range(2, len(pts) - 2, 2):
            x, y = pts[k]
            _leaf(d, x, y, u * 0.04, u * 0.012, rng.uniform(-40, 40), LEAF, LEAF_DK, ow)

    _border(d, W, H, int(u * 0.036), INK, max(2, u // 500))
    return img


def poster_06_acanthus(W, H):
    """Acanthus Scroll — formal indigo border, dense cream scroll field."""
    img = Image.new("RGB", (W, H), INDIGO)
    d = ImageDraw.Draw(img)
    u = min(W, H)
    rng = random.Random(606)
    ow = max(1, u // 700)
    cx, cy = W // 2, H // 2

    # indigo frame: dense leaf border around edges
    for i in range(36):
        t = i / 36
        # top
        _leaf(d, W * t, H * 0.04, u * 0.055, u * 0.016, 180 + rng.uniform(-15, 15),
              (50, 80, 110), OCHRE, ow, lobes=3)
        # bottom
        _leaf(d, W * t, H * 0.96, u * 0.055, u * 0.016, 0 + rng.uniform(-15, 15),
              (50, 80, 110), OCHRE, ow, lobes=3)
    for i in range(40):
        t = i / 40
        _leaf(d, W * 0.04, H * t, u * 0.05, u * 0.015, 90 + rng.uniform(-15, 15),
              (45, 75, 105), OCHRE, ow, lobes=3)
        _leaf(d, W * 0.96, H * t, u * 0.05, u * 0.015, -90 + rng.uniform(-15, 15),
              (45, 75, 105), OCHRE, ow, lobes=3)

    m = int(u * 0.10)
    d.rectangle([m, m, W - m, H - m], fill=CREAM)
    d.rectangle([m, m, W - m, H - m], outline=OCHRE, width=max(3, u // 380))
    g = max(6, m // 8)
    d.rectangle([m + g, m + g, W - m - g, H - m - g], outline=STEM, width=max(1, u // 700))

    # fill cream with concentric scroll rings of leaves
    for ring in range(8, 0, -1):
        rad = u * (0.08 + ring * 0.045)
        n = 10 + ring * 2
        for i in range(n):
            a = i * (360 / n) + ring * 8
            ang = math.radians(a)
            lx = cx + math.cos(ang) * rad * 0.55
            ly = cy + math.sin(ang) * rad * 0.55
            # keep inside cream panel
            if lx < m + g * 2 or lx > W - m - g * 2 or ly < m + g * 2 or ly > H - m - g * 2:
                continue
            col = LEAF if (i + ring) % 2 == 0 else SAGE
            if ring <= 2:
                col = RUST if i % 2 == 0 else ROSE
            _leaf(d, lx, ly, u * (0.055 + ring * 0.006), u * 0.018,
                  a + 90, col, LEAF_DK, ow, lobes=4)
            if ring >= 4 and i % 3 == 0:
                _blossom(d, lx + math.cos(ang) * u * 0.03, ly + math.sin(ang) * u * 0.03,
                         u * 0.016, ROSE if i % 2 == 0 else OCHRE, CREAM, 5, a, STEM)

    # heavy corner acanthus fans
    for ox, oy, a0 in [
        (m + u * 0.12, m + u * 0.12, 45),
        (W - m - u * 0.12, m + u * 0.12, 135),
        (W - m - u * 0.12, H - m - u * 0.12, 225),
        (m + u * 0.12, H - m - u * 0.12, 315),
    ]:
        for j in range(9):
            _leaf(d, ox, oy, u * (0.06 + j * 0.014), u * 0.024,
                  a0 + j * 12 - 20, LEAF if j % 2 == 0 else SAGE, LEAF_DK, ow, lobes=4)

    # center medallion
    r = u * 0.11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INDIGO)
    d.ellipse([cx - r * 0.88, cy - r * 0.88, cx + r * 0.88, cy + r * 0.88], outline=OCHRE, width=max(2, u // 400))
    d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72], fill=(35, 55, 85))
    for i in range(12):
        _leaf(d, cx, cy, u * 0.08, u * 0.02, i * 30, OCHRE, CREAM, ow, lobes=2)
    _rose(d, cx, cy, u * 0.055, ROSE, OCHRE, CREAM, 0, layers=3)

    d.rectangle([int(u * 0.035), int(u * 0.035), W - int(u * 0.035), H - int(u * 0.035)],
                outline=OCHRE, width=max(2, u // 420))
    return img


POSTERS = [
    ("01_willow_boughs", "Willow Boughs", poster_01_willow),
    ("02_strawberry_garden", "Strawberry Garden", poster_02_strawberry),
    ("03_trellis_rose", "Trellis Rose", poster_03_trellis),
    ("04_pimpernel_field", "Pimpernel Field", poster_04_pimpernel),
    ("05_honeysuckle", "Honeysuckle", poster_05_honeysuckle),
    ("06_acanthus_scroll", "Acanthus Scroll", poster_06_acanthus),
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
    print(f"=== Morris botanical prints @ {DPI_PRINT} dpi ===")
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
    img = Image.new("RGB", (S, S), (234, 228, 218))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(234 - 8 * t), int(228 - 6 * t), int(218 - 5 * t)))
    d.rectangle([0, int(S * 0.80), S, S], fill=(52, 44, 38))
    pw = int(S * 0.40)
    ph = int(pw * poster.height / poster.width)
    poster = poster.resize((pw, ph), Image.Resampling.LANCZOS)
    px, py = (S - pw) // 2, int(S * 0.10)
    frame = max(18, S // 70)
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([px - frame + 14, py - frame + 18, px + pw + frame + 14, py + ph + frame + 18], fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px - frame, py - frame, px + pw + frame, py + ph + frame], fill=(28, 24, 20))
    d.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], fill=CREAM)
    img.paste(poster, (px, py))
    return img


def build_previews():
    _ensure()
    print("=== Morris listing previews ===")
    masters = []
    for slug, title, fn in POSTERS:
        masters.append((slug, title, render_print(fn, 8.0, 12.0, DPI_PREVIEW)))

    S = 1600
    # 1 hero
    hero = _mockup_frame(masters[1][2], S)  # strawberry garden — strongest Morris read
    d = ImageDraw.Draw(hero)
    d.rectangle([0, 1480, S, S], fill=INDIGO_DEEP)
    d.text((S // 2, 1515), "WILLIAM MORRIS–INSPIRED PRINT SET", font=_font(26, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 1560), "6 botanical posters  ·  up to 24×36 in  ·  300 dpi", font=_font(15), fill=OCHRE, anchor="mt")
    save_jpg(hero, PREVIEWS / "morris_preview_1_hero.jpg", DPI_PREVIEW, 92)

    # 2 set of 3
    set_img = Image.new("RGB", (S, S), (238, 232, 220))
    d = ImageDraw.Draw(set_img)
    d.rectangle([0, int(S * 0.78), S, S], fill=(48, 40, 34))
    d.text((S // 2, 60), "SET OF 6  ·  ARTS & CRAFTS", font=_font(28, True), fill=INDIGO, anchor="mt")
    d.text((S // 2, 105), "Botanical gallery wall", font=_font(16), fill=SOFT, anchor="mt")
    chosen = [0, 1, 2]
    pw, gap = 340, 48
    total = 3 * pw + 2 * gap
    x0 = (S - total) // 2
    y0 = 180
    for i, idx in enumerate(chosen):
        pimg = masters[idx][2]
        ph = int(pw * pimg.height / pimg.width)
        pimg = pimg.resize((pw, ph), Image.Resampling.LANCZOS)
        x = x0 + i * (pw + gap)
        d.rectangle([x - 14, y0 - 14, x + pw + 14, y0 + ph + 14], fill=(24, 20, 18))
        d.rectangle([x - 5, y0 - 5, x + pw + 5, y0 + ph + 5], fill=CREAM)
        set_img.paste(pimg, (x, y0))
        d = ImageDraw.Draw(set_img)
    d.rectangle([0, S - 90, S, S], fill=INDIGO_DEEP)
    d.text((S // 2, S - 45), "MathRelaxing  ·  Morris Botanical Set", font=_font(18), fill=OCHRE, anchor="mm")
    save_jpg(set_img, PREVIEWS / "morris_preview_2_set.jpg", DPI_PREVIEW, 92)

    # 3 included
    incl = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, S, 160], fill=INDIGO)
    d.text((S // 2, 55), "WHAT'S INCLUDED", font=_font(34, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 110), "Instant download  ·  print at home or shop", font=_font(18), fill=OCHRE, anchor="mt")
    items = [
        ("6", "Botanical posters", "Arts & Crafts inspired designs", RUST, CREAM),
        ("12", "Print sizes", "Up to 24×36 in + A1 large poster", LEAF, CREAM),
        ("300", "DPI masters", "True 300 dpi — print-shop ready", OCHRE, INDIGO),
        ("1", "ZIP download", "Folders per design + README", INDIGO, CREAM),
    ]
    y = 220
    for num, title, sub, bubble, ink in items:
        d.ellipse([120, y, 220, y + 100], fill=bubble)
        d.text((170, y + 50), num, font=_font(28, True), fill=ink, anchor="mm")
        d.text((260, y + 30), title, font=_font(28, True), fill=INDIGO, anchor="lt")
        d.text((260, y + 70), sub, font=_font(18), fill=SOFT, anchor="lt")
        y += 140
    d.rectangle([100, 820, S - 100, 830], fill=OCHRE)
    d.text((S // 2, 900), "Willow · Strawberry garden · Trellis rose · Pimpernel · Honeysuckle · Acanthus",
           font=_font(16), fill=INDIGO, anchor="mt")
    tw = 200
    gap = 20
    total = 6 * tw + 5 * gap
    x0 = (S - total) // 2
    yy = 1000
    for i, (_, _, m) in enumerate(masters):
        th = int(tw * m.height / m.width)
        incl.paste(m.resize((tw, th), Image.Resampling.LANCZOS), (x0 + i * (tw + gap), yy))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, S - 70, S, S], fill=INDIGO_DEEP)
    d.text((S // 2, S - 35), "Original compositions  ·  Morris-inspired  ·  personal use", font=_font(15), fill=CREAM, anchor="mm")
    save_jpg(incl, PREVIEWS / "morris_preview_3_included.jpg", DPI_PREVIEW, 92)

    # 4-9 individuals
    for i, (slug, title, m) in enumerate(masters):
        plate = Image.new("RGB", (S, S), CREAM)
        max_h, max_w = int(S * 0.82), int(S * 0.55)
        scale = min(max_w / m.width, max_h / m.height)
        pw, ph = int(m.width * scale), int(m.height * scale)
        pimg = m.resize((pw, ph), Image.Resampling.LANCZOS)
        px, py = (S - pw) // 2, int(S * 0.08)
        sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([px + 8, py + 10, px + pw + 8, py + ph + 10], fill=(0, 0, 0, 35))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        plate = Image.alpha_composite(plate.convert("RGBA"), sh).convert("RGB")
        plate.paste(pimg, (px, py))
        d = ImageDraw.Draw(plate)
        d.rectangle([0, S - 100, S, S], fill=INDIGO)
        d.text((S // 2, S - 60), f"{i + 1:02d}  ·  {title.upper()}", font=_font(20, True), fill=OCHRE, anchor="mm")
        d.text((S // 2, S - 30), "MathRelaxing Morris Botanical Set", font=_font(14), fill=CREAM, anchor="mm")
        short = slug.split("_", 1)[1]
        save_jpg(plate, PREVIEWS / f"morris_preview_{i + 4}_{short}.jpg", DPI_PREVIEW, 92)

    # 10 all
    grid = Image.new("RGB", (S, S), INDIGO_DEEP)
    d = ImageDraw.Draw(grid)
    d.text((S // 2, 40), "ALL 6 DESIGNS", font=_font(30, True), fill=CREAM, anchor="mt")
    d.rectangle([S // 2 - 60, 85, S // 2 + 60, 88], fill=OCHRE)
    tw, th = 420, 630
    gapx, gapy = 40, 50
    x0 = (S - 3 * tw - 2 * gapx) // 2
    y0 = 120
    for i, (_, title, m) in enumerate(masters):
        c, r = i % 3, i // 3
        x = x0 + c * (tw + gapx)
        y = y0 + r * (th + gapy)
        d.rectangle([x - 3, y - 3, x + tw + 3, y + th + 3], fill=OCHRE)
        grid.paste(m.resize((tw, th), Image.Resampling.LANCZOS), (x, y))
        d = ImageDraw.Draw(grid)
        d.text((x + tw // 2, y + th + 14), title.upper(), font=_font(13, True), fill=OCHRE, anchor="mt")
    d.rectangle([0, S - 60, S, S], fill=(10, 16, 28))
    d.text((S // 2, S - 30), "Digital download  ·  up to 24×36 / A1  ·  300 dpi", font=_font(15), fill=CREAM, anchor="mm")
    save_jpg(grid, PREVIEWS / "morris_preview_10_all.jpg", DPI_PREVIEW, 92)
    print(f"  previews → {PREVIEWS}")


README = """MathRelaxing — William Morris–Inspired Botanical Print Set
==========================================================

6 original Arts & Crafts botanical posters inspired by the spirit of
William Morris (public-domain era style). Original compositions — not scans.

PRINTS
  01_willow_boughs
  02_strawberry_garden
  03_trellis_rose
  04_pimpernel_field
  05_honeysuckle
  06_acanthus_scroll

LARGE POSTER @ 300 dpi
  24×36, 18×24, 24×30, 20×28, A1, A2

STANDARD / HOME @ 300 dpi
  12×18, 12×16, 16×20, 10×14, A3, A4

Scale large files down for smaller frames. Matte paper recommended.

Personal use only. Not for resale or redistribution.
© MathRelaxing
"""


def _zip_pack(path: Path, slugs: list[str] | None, size_keys: set[str] | None, label: str):
    if path.exists():
        path.unlink()
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README)
        for slug, _, _ in POSTERS:
            if slugs is not None and slug not in slugs:
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
                n += 1
    mb = path.stat().st_size / (1024 * 1024)
    print(f"  {label}: {path.name} ({mb:.1f} MB, {n} files)")
    if mb > 19.5:
        print(f"  WARNING: {path.name} over Etsy ~20MB")
    return mb


def build_zip():
    """Etsy ~20MB/file, max 5 files — dense botanical needs 5 packs."""
    print("=== Morris ZIP(s) — 5 packs ===")
    packs = [
        (OUT / "MathRelaxing_Morris_Large_01_02.zip",
         ["01_willow_boughs", "02_strawberry_garden"], LARGE_KEYS, "L 01-02"),
        (OUT / "MathRelaxing_Morris_Large_03_04.zip",
         ["03_trellis_rose", "04_pimpernel_field"], LARGE_KEYS, "L 03-04"),
        (OUT / "MathRelaxing_Morris_Large_05_06.zip",
         ["05_honeysuckle", "06_acanthus_scroll"], LARGE_KEYS, "L 05-06"),
        (OUT / "MathRelaxing_Morris_Standard_A.zip",
         ["01_willow_boughs", "02_strawberry_garden", "03_trellis_rose"], STD_KEYS, "S 01-03"),
        (OUT / "MathRelaxing_Morris_Standard_B.zip",
         ["04_pimpernel_field", "05_honeysuckle", "06_acanthus_scroll"], STD_KEYS, "S 04-06"),
    ]
    out_paths = []
    for path, slugs, keys, label in packs:
        _zip_pack(path, slugs, keys, label)
        out_paths.append(path)
    return out_paths


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
