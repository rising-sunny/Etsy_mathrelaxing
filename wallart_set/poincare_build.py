"""
poincare_build.py — prints + Etsy listing previews for Poincaré disk tiling.

    python poincare_build.py
    python poincare_build.py mono atelier
    python poincare_build.py mono wire 3 7 5
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import poincare_disc as pd

HERE = Path(__file__).resolve().parent
PAL = sys.argv[1] if len(sys.argv) > 1 else "mono"
# wire = light gallery line art (default). atelier = whisper fills.
STYLE = sys.argv[2] if len(sys.argv) > 2 else "wire"
# Default {7,3} depth 3 — classic Poincaré disk that fills to the rim
P_GON = int(sys.argv[3]) if len(sys.argv) > 3 else 7
Q_VERT = int(sys.argv[4]) if len(sys.argv) > 4 else 3
DEPTH = int(sys.argv[5]) if len(sys.argv) > 5 else 3

pd.use_palette(PAL)

TAG = f"{P_GON}_{Q_VERT}"
BASE = HERE / "out" / "poincare" / f"{PAL}_{STYLE}_{TAG}"
PRINTS = BASE / "prints"
LST = BASE / "listing"
for d in (PRINTS, LST):
    d.mkdir(parents=True, exist_ok=True)

SLUG = f"Poincare_Disk_{P_GON}_{Q_VERT}"
TITLE = f"Poincaré Disk {{{P_GON},{Q_VERT}}}"
RATIO_PX = {
    "2x3": (4800, 7200),
    "3x4": (5400, 7200),
    "4x5": (4800, 6000),
    "5x7": (4500, 6300),
    "ISO": (4961, 7016),
}


def _font(size, bold=False, serif=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    if serif:
        names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    else:
        names = ["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    for n in names:
        path = os.path.join(windir, "Fonts", n)
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _hex(c):
    return tuple(int(c.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))


def _render(w, h):
    return pd.render_image(
        w, h, palette=PAL, style=STYLE, p=P_GON, q=Q_VERT, depth=DEPTH,
    )


def build_prints():
    for tag, (w, h) in RATIO_PX.items():
        im = _render(w, h)
        path = PRINTS / f"{SLUG}_{tag}.jpg"
        im.save(path, quality=94, dpi=(300, 300))
        print("  print", path.name, im.size)
    zpath = BASE / f"{SLUG}_prints.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for tag in RATIO_PX:
            z.write(PRINTS / f"{SLUG}_{tag}.jpg", f"{SLUG}_{tag}.jpg")
        z.writestr(
            "READ-ME.txt",
            f"""{TITLE} — MathRelaxing
================================
Hyperbolic tiling {{{P_GON},{Q_VERT}}} in the Poincaré disk model.
Every edge is a true geodesic (circular arc orthogonal to the boundary).
Drawn from real non-Euclidean geometry — not AI, not clip art.

Includes 5 aspect ratios @ 300 DPI:
  2:3  3:4  4:5  5:7  ISO/A

Personal use only. Not for resale or redistribution.
""",
        )
    print(f"  zip {zpath.name} ({zpath.stat().st_size / 1e6:.2f} MB)")


def hero():
    side = 1600
    art = _render(1200, 1500)
    bg = Image.new("RGB", (side, side), _hex(pd.BG))
    d = ImageDraw.Draw(bg)
    ink = _hex(pd._P["ink"])
    d.text((side // 2, 70), "NON-EUCLIDEAN GEOMETRY", font=_font(20, bold=True), fill=ink, anchor="mt")
    d.text((side // 2, 110), "Poincaré Disk", font=_font(48, bold=True, serif=True), fill=ink, anchor="mt")
    d.text(
        (side // 2, 175),
        f"Hyperbolic tiling {{{P_GON},{Q_VERT}}}  ·  drawn from real mathematics",
        font=_font(20), fill=ink, anchor="mt",
    )
    ax = (side - art.width) // 2
    bg.paste(art, (ax, 200))
    d.rectangle([0, side - 90, side, side], fill=ink)
    d.text(
        (side // 2, side - 45),
        "Instant digital download  ·  5 aspect ratios  ·  300 DPI",
        font=_font(20), fill=_hex(pd.BG), anchor="mm",
    )
    bg.save(LST / "01_hero.jpg", quality=93)
    print("  01 hero")


def detail():
    im = _render(2000, 2500)
    w, h = im.size
    crop = im.crop((int(w * 0.08), int(h * 0.12), int(w * 0.92), int(h * 0.55)))
    crop = crop.resize((1600, int(1600 * crop.height / crop.width)), Image.Resampling.LANCZOS)
    side = 1600
    canvas = Image.new("RGB", (side, side), crop.getpixel((10, 10)))
    canvas.paste(crop, (0, (side - crop.height) // 2))
    canvas.save(LST / "02_detail.jpg", quality=93)
    print("  02 detail")


def framed():
    plate = _render(int(1200 * 4 / 5), 1200)
    W, H = 2000, 1600
    arr = np.zeros((H, W, 3), np.uint8)
    g = np.linspace(0, 1, H)[:, None]
    for i, (a, b) in enumerate(zip((222, 214, 200), (200, 193, 182))):
        arr[:, :, i] = (a * (1 - g) + b * g).astype(np.uint8)
    wall = Image.fromarray(arr)
    ph = 1180
    pw = int(plate.width * ph / plate.height)
    plate = plate.resize((pw, ph), Image.Resampling.LANCZOS)
    mat, fr = 36, 22
    card = Image.new("RGB", (pw + 2 * mat + 2 * fr, ph + 2 * mat + 2 * fr), (30, 28, 25))
    inner = Image.new("RGB", (pw + 2 * mat, ph + 2 * mat), "#f7f6f2")
    inner.paste(plate, (mat, mat))
    card.paste(inner, (fr, fr))
    x = (W - card.width) // 2
    y = (H - card.height) // 2
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 44, 40 + card.width, 44 + card.height], fill=(40, 38, 34, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    wall.paste(sh, (x - 40 + 14, y - 40 + 18), sh)
    wall.paste(card, (x, y))
    wall.save(LST / "03_framed.jpg", quality=92)
    print("  03 framed")


def math_card():
    side = 1600
    bg = Image.new("RGB", (side, side), _hex(pd.BG))
    d = ImageDraw.Draw(bg)
    ink = _hex(pd._P["ink"])
    d.text((side // 2, 70), "What you are looking at", font=_font(36, bold=True, serif=True), fill=ink, anchor="mt")
    items = [
        ("01", "Poincaré disk", "The open unit disk models the hyperbolic plane"),
        ("02", f"Tiling {{{P_GON},{Q_VERT}}}", f"{P_GON}-gons, {Q_VERT} meeting at each vertex"),
        ("03", "Geodesic edges", "Arcs orthogonal to the boundary = “straight” lines"),
        ("04", "Infinite to the rim", "Tiles shrink toward the circle at infinity"),
        ("05", "Code, not AI", "Recursive reflection of a regular polygon"),
    ]
    y = 170
    for n, t, s in items:
        d.rounded_rectangle([120, y, side - 120, y + 200], radius=18, outline=ink, width=2)
        d.ellipse([160, y + 50, 260, y + 150], outline=ink, width=3)
        d.text((210, y + 100), n, font=_font(28, bold=True), fill=ink, anchor="mm")
        d.text((300, y + 70), t, font=_font(30, bold=True, serif=True), fill=ink, anchor="lt")
        d.text((300, y + 120), s, font=_font(22), fill=ink, anchor="lt")
        y += 230
    bg.save(LST / "04_math.jpg", quality=92)
    print("  04 math")


def included():
    side = 1600
    bg = Image.new("RGB", (side, side), _hex(pd.BG))
    d = ImageDraw.Draw(bg)
    ink = _hex(pd._P["ink"])
    d.text((side // 2, 80), "What's included", font=_font(42, bold=True, serif=True), fill=ink, anchor="mt")
    labs = [("2:3", 2 / 3), ("3:4", 3 / 4), ("4:5", 4 / 5), ("5:7", 5 / 7), ("ISO", 1 / 1.414)]
    xs = [160, 420, 700, 980, 1240]
    for (lab, a), x in zip(labs, xs):
        th = 380
        tw = max(40, int(th * a))
        thumb = _render(tw, th)
        px = x - tw // 2
        py = 220
        d.rectangle([px - 4, py - 4, px + tw + 4, py + th + 4], outline=ink, width=2)
        bg.paste(thumb, (px, py))
        d.text((x, py + th + 40), lab, font=_font(22, bold=True), fill=ink, anchor="mt")
    lines = [
        "5 high-resolution JPGs · 300 DPI",
        "Print small desk frames or large gallery pieces",
        "Instant download — no physical item ships",
    ]
    y = 720
    for line in lines:
        d.rounded_rectangle([180, y, side - 180, y + 110], radius=14, outline=ink, width=2)
        d.text((side // 2, y + 55), line, font=_font(26), fill=ink, anchor="mm")
        y += 140
    bg.save(LST / "05_included.jpg", quality=92)
    print("  05 included")


def how_to():
    side = 1600
    bg = Image.new("RGB", (side, side), _hex(pd.BG))
    d = ImageDraw.Draw(bg)
    ink = _hex(pd._P["ink"])
    d.text((side // 2, 90), "How it works", font=_font(42, bold=True, serif=True), fill=ink, anchor="mt")
    steps = [
        ("1", "Download", "ZIP arrives instantly after purchase"),
        ("2", "Choose ratio", "2:3 · 3:4 · 4:5 · 5:7 · ISO/A"),
        ("3", "Print", "Home, local shop, or online lab"),
        ("4", "Frame & hang", "Mat optional — the disk centers itself"),
    ]
    y = 240
    for n, t, s in steps:
        d.ellipse([140, y, 240, y + 100], outline=ink, width=3)
        d.text((190, y + 50), n, font=_font(34, bold=True), fill=ink, anchor="mm")
        d.text((290, y + 25), t, font=_font(34, bold=True, serif=True), fill=ink, anchor="lt")
        d.text((290, y + 80), s, font=_font(24), fill=ink, anchor="lt")
        y += 280
    bg.save(LST / "06_howto.jpg", quality=92)
    print("  06 howto")


def main():
    print(f"Poincaré Disk {{{P_GON},{Q_VERT}}}  [{PAL} / {STYLE}] depth={DEPTH}")
    print("prints…")
    build_prints()
    print("listing…")
    hero()
    detail()
    framed()
    math_card()
    included()
    how_to()
    print("DONE →", BASE)


if __name__ == "__main__":
    main()
