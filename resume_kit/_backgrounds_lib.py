"""
Elegant semi-transparent background plates for Editorial resumes.
Used as behind-text watermarks in Word + free PNG style pack for buyers.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw

# Letter @ 150 dpi for light DOCX embeds
W, H = 1275, 1650  # 8.5 x 11 in


def _rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def style_cream_veil() -> Image.Image:
    """Soft cream wash — quiet paper elegance."""
    img = Image.new("RGBA", (W, H), (248, 244, 235, 0))
    d = ImageDraw.Draw(img)
    # gentle vertical gradient veil
    for y in range(H):
        t = y / H
        a = int(18 + 22 * math.sin(t * math.pi))  # peak mid-page, still faint
        d.line([(0, y), (W, y)], fill=(248, 244, 235, a))
    # soft corner vignettes gold
    for r in range(280, 0, -2):
        a = int(12 * (1 - r / 280))
        d.ellipse([-r, -r, r, r], outline=(201, 162, 75, a))
        d.ellipse([W - r, H - r, W + r, H + r], outline=(201, 162, 75, a))
    return img


def style_scientific_grid() -> Image.Image:
    """Whisper of graph paper — MathRelaxing signature."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # cream wash base
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(248, 244, 235, 28))
    step = 22
    major = step * 4
    for x in range(0, W, step):
        a = 22 if x % major == 0 else 12
        d.line([(x, 0), (x, H)], fill=(18, 23, 46, a))
    for y in range(0, H, step):
        a = 22 if y % major == 0 else 12
        d.line([(0, y), (W, y)], fill=(18, 23, 46, a))
    return img


def style_gold_geometry() -> Image.Image:
    """Thin geometric corner frames + soft gold arcs."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(248, 244, 235, 22))
    m = 55
    gold = (201, 162, 75, 55)
    gold_soft = (201, 162, 75, 28)
    # corner L marks
    for ox, oy, sx, sy in [
        (m, m, 1, 1),
        (W - m, m, -1, 1),
        (m, H - m, 1, -1),
        (W - m, H - m, -1, -1),
    ]:
        d.line([(ox, oy), (ox + sx * 90, oy)], fill=gold, width=2)
        d.line([(ox, oy), (ox, oy + sy * 90)], fill=gold, width=2)
        d.line([(ox + sx * 20, oy + sy * 20), (ox + sx * 70, oy + sy * 20)], fill=gold_soft, width=1)
        d.line([(ox + sx * 20, oy + sy * 20), (ox + sx * 20, oy + sy * 70)], fill=gold_soft, width=1)
    # faint center circle
    cx, cy = W // 2, int(H * 0.42)
    for r, a in [(420, 14), (280, 18), (140, 22)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(201, 162, 75, a), width=1)
    return img


def style_phi_whisper() -> Image.Image:
    """Ultra-faint golden spiral — mathematical elegance."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(248, 244, 235, 20))
    cx, cy = W // 2, int(H * 0.48)
    phi = (1 + math.sqrt(5)) / 2
    pts = []
    for i in range(0, 720):
        th = math.radians(i * 0.85)
        r = 4 * math.exp(0.12 * th / phi)
        if r > min(W, H) * 0.42:
            break
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    if len(pts) > 2:
        d.line(pts, fill=(201, 162, 75, 32), width=2)
    # soft outer ring
    r = int(min(W, H) * 0.38)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(18, 23, 46, 16), width=1)
    return img


def style_navy_edge() -> Image.Image:
    """Soft left navy edge + cream field — editorial column cue."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(248, 244, 235, 26))
    band = 48
    for x in range(band):
        a = int(40 * (1 - x / band))
        d.line([(x, 0), (x, H)], fill=(18, 23, 46, a))
    # gold hairline
    d.line([(band + 4, 80), (band + 4, H - 80)], fill=(201, 162, 75, 70), width=2)
    # top/bottom gold rules
    d.line([(band + 24, 70), (W - 60, 70)], fill=(201, 162, 75, 40), width=1)
    d.line([(band + 24, H - 70), (W - 60, H - 70)], fill=(201, 162, 75, 40), width=1)
    return img


STYLES = {
    "cream_veil": ("Cream Veil", style_cream_veil),
    "scientific_grid": ("Scientific Grid", style_scientific_grid),
    "gold_geometry": ("Gold Geometry", style_gold_geometry),
    "phi_whisper": ("Phi Whisper", style_phi_whisper),
    "navy_edge": ("Navy Edge", style_navy_edge),
}


def write_all(out_dir: str) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for key, (label, fn) in STYLES.items():
        path = os.path.join(out_dir, f"bg_{key}.png")
        fn().save(path, "PNG")
        paths[key] = path
        print(f"  bg {key} → {path}")
    # style guide contact sheet
    thumbs = []
    for key, (label, fn) in STYLES.items():
        im = fn().convert("RGBA")
        im.thumbnail((220, 285), Image.Resampling.LANCZOS)
        # composite on cream for visibility
        card = Image.new("RGB", (240, 320), (248, 244, 235))
        card.paste(im, (10, 10), im)
        thumbs.append((label, card))
    sheet = Image.new("RGB", (1280, 380), (18, 23, 46))
    from PIL import ImageDraw, ImageFont

    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "georgia.ttf"), 18)
    except OSError:
        font = ImageFont.load_default()
    d.text((30, 16), "Background styles (semi-transparent) — pick one for Editorial resumes", font=font, fill=(248, 244, 235))
    x = 30
    for label, card in thumbs:
        sheet.paste(card, (x, 50))
        d.text((x + 10, 340), label, font=font, fill=(201, 162, 75))
        x += 250
    sheet_path = os.path.join(out_dir, "_styles_contact_sheet.jpg")
    sheet.save(sheet_path, quality=90)
    print(f"  contact sheet → {sheet_path}")
    return paths
