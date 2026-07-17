"""
build_bauhaus_video.py — Etsy promo MP4 for Bauhaus Print Set
=============================================================
Silent gallery promo (~12s, 1080², 30fps):
  title → Ken Burns cycle through 6 posters → set grid → end card

  python build_bauhaus_video.py
"""
from __future__ import annotations

import math
import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

import brand
import generate_bauhaus_set as bh

BASE = Path(__file__).resolve().parent
OUT = BASE / "bauhaus_set"
FRAMES = OUT / "_video_frames"
VIDEO = OUT / "Bauhaus_Print_Set_promo.mp4"

S = 1080
FPS = 30
DURATION = 12.0  # Etsy-friendly 5–15s
N = int(DURATION * FPS)

NAVY = bh.NAVY
NAVY_DEEP = bh.NAVY_DEEP
CREAM = bh.CREAM
GOLD = bh.GOLD
RED = bh.RED
BLUE = bh.BLUE
SOFT = bh.SOFT


def _font(size, bold=False):
    return bh._font(size, bold)


def _serif(size, bold=False):
    return bh._serif(size, bold)


def _lerp(a, b, t):
    return a + (b - a) * t


def _ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _poster_master(slug_idx: int, w_in=6.0, h_in=9.0, dpi=180) -> Image.Image:
    _slug, _title, fn = bh.POSTERS[slug_idx]
    return bh.render_print(fn, w_in, h_in, dpi)


def _bg(color=NAVY_DEEP) -> Image.Image:
    return Image.new("RGB", (S, S), color)


def _framed_poster(poster: Image.Image, scale: float = 1.0, max_h: float = 0.72) -> Image.Image:
    """Poster with black frame + soft shadow on transparent-ish composite onto navy later."""
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ph = int(S * max_h * scale)
    pw = int(ph * poster.width / poster.height)
    p = poster.resize((pw, ph), Image.Resampling.LANCZOS).convert("RGBA")
    frame = max(10, S // 90)
    mat = 6
    outer_w, outer_h = pw + 2 * (frame + mat), ph + 2 * (frame + mat)
    px = (S - outer_w) // 2
    py = int(S * 0.12) + int((S * 0.72 - outer_h) // 2)

    # shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [px + 12, py + 16, px + outer_w + 12, py + outer_h + 16],
        fill=(0, 0, 0, 90),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas, sh)

    d = ImageDraw.Draw(canvas)
    d.rectangle([px, py, px + outer_w, py + outer_h], fill=(20, 20, 22, 255))
    d.rectangle(
        [px + frame, py + frame, px + outer_w - frame, py + outer_h - frame],
        fill=(*CREAM, 255),
    )
    canvas.paste(p, (px + frame + mat, py + frame + mat), p)
    return canvas


def _title_card(t: float) -> Image.Image:
    """t 0..1 fade in."""
    img = _bg()
    d = ImageDraw.Draw(img)
    alpha = _ease_in_out(min(1.0, t * 1.4))

    # geometric micro accents
    d.ellipse([S // 2 - 40, 180, S // 2 + 40, 260], outline=RED, width=4)
    d.rectangle([S // 2 - 120, 320, S // 2 - 100, 500], fill=BLUE)
    d.polygon([(S // 2 + 80, 500), (S // 2 + 160, 320), (S // 2 + 240, 500)], fill=GOLD)

    # fade via blend with navy
    overlay = Image.new("RGB", (S, S), NAVY_DEEP)
    d2 = ImageDraw.Draw(overlay)
    d2.text((S // 2, 560), "BAUHAUS", font=_serif(72, True), fill=CREAM, anchor="mt")
    d2.rectangle([S // 2 - 80, 650, S // 2 + 80, 654], fill=GOLD)
    d2.text((S // 2, 690), "GEOMETRIC PRINT SET", font=_font(28, True), fill=GOLD, anchor="mt")
    d2.text((S // 2, 760), "6 posters  ·  multi-size  ·  300 dpi", font=_font(20), fill=SOFT, anchor="mt")
    d2.text((S // 2, 920), "MathRelaxing", font=_font(18), fill=CREAM, anchor="mt")

    # blend accents layer
    base = Image.blend(img, Image.new("RGB", (S, S), NAVY_DEEP), 0.35)
    return Image.blend(Image.new("RGB", (S, S), NAVY_DEEP), Image.blend(base, overlay, 0.85), alpha)


def _poster_scene(poster: Image.Image, title: str, local_t: float, n: int, total: int) -> Image.Image:
    """
    local_t 0..1 within this poster's slot.
    Ken Burns: slight scale up + fade in/out at edges.
    """
    img = _bg((18, 20, 36))
    # soft floor band
    d = ImageDraw.Draw(img)
    for y in range(int(S * 0.78), S):
        tt = (y - S * 0.78) / (S * 0.22)
        col = (int(18 + 8 * tt), int(18 + 6 * tt), int(22 + 4 * tt))
        d.line([(0, y), (S, y)], fill=col)

    # Ken Burns scale 1.0 → 1.06
    sc = 1.0 + 0.06 * _ease_in_out(local_t)
    layer = _framed_poster(poster, scale=sc, max_h=0.68)
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    d = ImageDraw.Draw(img)
    # fade edges
    fade_in = _ease_in_out(min(1.0, local_t / 0.12))
    fade_out = _ease_in_out(min(1.0, (1.0 - local_t) / 0.12))
    edge = min(fade_in, fade_out)

    # bottom caption
    d.rectangle([0, S - 110, S, S], fill=NAVY_DEEP)
    d.text((S // 2, S - 72), f"{n:02d}  ·  {title.upper()}", font=_font(22, True), fill=GOLD, anchor="mt")
    d.text((S // 2, S - 38), f"{n} of {total}", font=_font(14), fill=SOFT, anchor="mt")

    if edge < 0.999:
        return Image.blend(Image.new("RGB", (S, S), NAVY_DEEP), img, edge)
    return img


def _grid_scene(posters: list[Image.Image], titles: list[str], t: float) -> Image.Image:
    """All 6 appear with staggered pop-in."""
    img = _bg()
    d = ImageDraw.Draw(img)
    d.text((S // 2, 48), "ALL 6 DESIGNS", font=_serif(32, True), fill=CREAM, anchor="mt")
    d.rectangle([S // 2 - 50, 95, S // 2 + 50, 98], fill=GOLD)

    tw, th = 280, 420
    gapx, gapy = 28, 36
    total_w = 3 * tw + 2 * gapx
    x0 = (S - total_w) // 2
    y0 = 130

    for i, (p, title) in enumerate(zip(posters, titles)):
        # stagger reveal
        start = i * 0.08
        local = _ease_in_out(max(0.0, min(1.0, (t - start) / 0.25)))
        if local <= 0:
            continue
        c, r = i % 3, i // 3
        x = x0 + c * (tw + gapx)
        y = y0 + r * (th + gapy)
        # slight scale from 0.9 → 1.0
        sc = 0.9 + 0.1 * local
        pw, ph = int(tw * sc), int(th * sc)
        thumb = p.resize((pw, ph), Image.Resampling.LANCZOS)
        ox = x + (tw - pw) // 2
        oy = y + (th - ph) // 2
        # gold frame
        d.rectangle([ox - 3, oy - 3, ox + pw + 3, oy + ph + 3], fill=GOLD)
        img.paste(thumb, (ox, oy))
        d = ImageDraw.Draw(img)
        if local > 0.7:
            d.text((x + tw // 2, y + th + 12), title.upper()[:14], font=_font(12, True), fill=GOLD, anchor="mt")

    d.rectangle([0, S - 70, S, S], fill=(6, 8, 18))
    d.text((S // 2, S - 35), "Instant download  ·  6 ratios  ·  300 dpi", font=_font(16), fill=CREAM, anchor="mm")

    fade = _ease_in_out(min(1.0, t / 0.1))
    return Image.blend(Image.new("RGB", (S, S), NAVY_DEEP), img, fade)


def _end_card(t: float) -> Image.Image:
    img = _bg()
    d = ImageDraw.Draw(img)
    # Bauhaus-ish end composition
    d.ellipse([S // 2 - 200, 220, S // 2 - 40, 380], fill=RED)
    d.rectangle([S // 2 + 40, 220, S // 2 + 120, 520], fill=NAVY)
    d.rectangle([S // 2 - 200, 420, S // 2 + 200, 480], fill=BLUE)
    d.rectangle([S // 2 - 200, 500, S // 2 + 200, 512], fill=GOLD)

    d.text((S // 2, 620), "BAUHAUS PRINT SET", font=_serif(40, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 690), "Digital Download  ·  Multi-size  ·  300 dpi", font=_font(20), fill=GOLD, anchor="mt")
    d.text((S // 2, 760), "MathRelaxing", font=_font(20), fill=SOFT, anchor="mt")

    alpha = _ease_in_out(min(1.0, t * 2))
    return Image.blend(Image.new("RGB", (S, S), NAVY_DEEP), img, alpha)


def build_frames():
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True, exist_ok=True)

    print("Rendering poster masters...")
    posters = []
    titles = []
    for i, (slug, title, fn) in enumerate(bh.POSTERS):
        posters.append(_poster_master(i))
        titles.append(title)
        print(f"  master {i + 1}/6 {title}")

    # Timeline (seconds)
    # 0.0–1.4 title
    # 1.4–9.2 six posters (~1.3s each)
    # 9.2–11.0 grid
    # 11.0–12.0 end
    T_TITLE = 1.4
    T_POSTERS_START = 1.4
    T_POSTERS_END = 9.2
    T_GRID_END = 11.0
    T_END = 12.0
    n_posters = 6
    slot = (T_POSTERS_END - T_POSTERS_START) / n_posters

    print(f"Building {N} frames @ {FPS}fps ({DURATION}s)...")
    for i in range(N):
        t = i / FPS
        if t < T_TITLE:
            frame = _title_card(t / T_TITLE)
        elif t < T_POSTERS_END:
            rel = t - T_POSTERS_START
            idx = min(n_posters - 1, int(rel / slot))
            local = (rel - idx * slot) / slot
            frame = _poster_scene(posters[idx], titles[idx], local, idx + 1, n_posters)
        elif t < T_GRID_END:
            frame = _grid_scene(posters, titles, (t - T_POSTERS_END) / (T_GRID_END - T_POSTERS_END))
        else:
            frame = _end_card((t - T_GRID_END) / (T_END - T_GRID_END))

        path = FRAMES / f"f_{i:04d}.png"
        frame.save(path, "PNG")
        if i % 30 == 0:
            print(f"  frame {i}/{N} t={t:.1f}s")

    return N


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_frames()
    print("Encoding MP4...")
    brand.encode_mp4(str(FRAMES), str(VIDEO), fps=FPS, pattern="f_%04d.png", crf=20, cleanup=True)
    mb = VIDEO.stat().st_size / (1024 * 1024)
    print(f"Video listo: {VIDEO} ({mb:.1f} MB)")
    print("Duration ~12s · 1080x1080 · silent · Etsy-ready")


if __name__ == "__main__":
    main()
