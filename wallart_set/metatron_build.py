"""
metatron_build.py — prints + Etsy listing previews for Metatron's Cube.

    python metatron_build.py
    python metatron_build.py mono atelier
    python metatron_build.py navy_gold solid
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import metatron_cube as mc

HERE = Path(__file__).resolve().parent
PAL = (sys.argv[1] if len(sys.argv) > 1 else "mono")
STYLE = (sys.argv[2] if len(sys.argv) > 2 else "atelier")
mc.use_palette(PAL)

BASE = HERE / "out" / "metatron" / f"{PAL}_{STYLE}"
PRINTS = BASE / "prints"
LST = BASE / "listing"
for d in (PRINTS, LST):
    d.mkdir(parents=True, exist_ok=True)

SLUG = "Metatrons_Cube"
TITLE = "Metatron's Cube"
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
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_prints():
    for tag, (w, h) in RATIO_PX.items():
        im = mc.render_image(w, h, palette=PAL, style=STYLE)
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
Ultra-precise Metatron's Cube: Fruit of Life centres, full wireframe,
and solid faces (star tetrahedron / Merkaba + isometric cube rhombi).

Drawn from real geometry — not AI, not clip art.

Includes 5 aspect ratios @ 300 DPI:
  2:3  3:4  4:5  5:7  ISO/A

Personal use only. Not for resale or redistribution.
""",
        )
    print(f"  zip {zpath.name} ({zpath.stat().st_size / 1e6:.2f} MB)")


def _plate(h=1350):
    w = int(h * 4 / 5)
    return mc.render_image(w, h, palette=PAL, style=STYLE)


def hero():
    # Square listing hero — art centered on cream with title band
    side = 1600
    art = mc.render_image(1200, 1500, palette=PAL, style=STYLE)
    bg = Image.new("RGB", (side, side), tuple(int(mc.BG.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)))
    # soft outer frame
    d = ImageDraw.Draw(bg)
    ink = tuple(int(mc._P["ink"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    gold = tuple(int(mc._P.get("node", mc._P["ink"]).lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    d.text((side // 2, 70), "SACRED GEOMETRY", font=_font(22, bold=True), fill=gold, anchor="mt")
    d.text((side // 2, 110), "Metatron's Cube", font=_font(48, bold=True, serif=True), fill=ink, anchor="mt")
    d.text((side // 2, 175), "Wire + solid faces  ·  drawn from real mathematics",
           font=_font(20), fill=ink, anchor="mt")
    ax = (side - art.width) // 2
    ay = 210
    bg.paste(art, (ax, ay))
    d.rectangle([0, side - 90, side, side], fill=ink)
    d.text((side // 2, side - 45), "Instant digital download  ·  5 aspect ratios  ·  300 DPI",
           font=_font(20), fill=tuple(int(mc.BG.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)), anchor="mm")
    bg.save(LST / "01_hero.jpg", quality=93)
    print("  01 hero")


def detail():
    im = mc.render_image(2000, 2500, palette=PAL, style=STYLE)
    w, h = im.size
    # crop centre-upper for wire density
    crop = im.crop((int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.62)))
    crop = crop.resize((1600, int(1600 * crop.height / crop.width)), Image.Resampling.LANCZOS)
    # pad to square
    side = 1600
    canvas = Image.new("RGB", (side, side), crop.getpixel((10, 10)))
    canvas.paste(crop, (0, (side - crop.height) // 2))
    canvas.save(LST / "02_detail.jpg", quality=93)
    print("  02 detail")


def framed():
    plate = _plate(1200)
    W, H = 2000, 1600
    wall = Image.new("RGB", (W, H), (214, 208, 198))
    # subtle gradient
    arr = np.array(wall)
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


def layers_card():
    """What's in the geometry — educational listing image."""
    side = 1600
    bg_c = tuple(int(mc.BG.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    ink = tuple(int(mc._P["ink"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    soft = tuple(min(255, c + 40) for c in ink)
    im = Image.new("RGB", (side, side), bg_c)
    d = ImageDraw.Draw(im)
    d.text((side // 2, 70), "Built in layers", font=_font(40, bold=True, serif=True), fill=ink, anchor="mt")
    items = [
        ("01", "Fruit of Life", "13 equal circles — exact centres"),
        ("02", "Full wireframe", "Every centre connected to every other"),
        ("03", "Star tetrahedron", "Merkaba — two solid equilateral faces"),
        ("04", "Cube rhombi", "Isometric cube faces from the hexagon"),
        ("05", "Nodes + outer ring", "13 vertices · containing circle"),
    ]
    y = 180
    for n, t, s in items:
        d.rounded_rectangle([120, y, side - 120, y + 200], radius=18, outline=ink, width=2)
        d.ellipse([160, y + 50, 260, y + 150], outline=ink, width=3)
        d.text((210, y + 100), n, font=_font(28, bold=True), fill=ink, anchor="mm")
        d.text((300, y + 70), t, font=_font(32, bold=True, serif=True), fill=ink, anchor="lt")
        d.text((300, y + 120), s, font=_font(22), fill=soft, anchor="lt")
        y += 230
    im.save(LST / "04_layers.jpg", quality=92)
    print("  04 layers")


def included():
    side = 1600
    bg_c = tuple(int(mc.BG.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    ink = tuple(int(mc._P["ink"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    im = Image.new("RGB", (side, side), bg_c)
    d = ImageDraw.Draw(im)
    d.text((side // 2, 80), "What's included", font=_font(42, bold=True, serif=True), fill=ink, anchor="mt")
    # five ratio thumbs
    labs = [("2:3", 2 / 3), ("3:4", 3 / 4), ("4:5", 4 / 5), ("5:7", 5 / 7), ("ISO", 1 / 1.414)]
    xs = [160, 420, 700, 980, 1240]
    for (lab, a), x in zip(labs, xs):
        th = 520
        tw = int(th * a)
        thumb = mc.render_image(tw, th, palette=PAL, style=STYLE)
        # scale down
        th2 = 380
        tw2 = int(th2 * a)
        thumb = thumb.resize((tw2, th2), Image.Resampling.LANCZOS)
        px = x - tw2 // 2
        py = 220
        # thin frame
        d.rectangle([px - 4, py - 4, px + tw2 + 4, py + th2 + 4], outline=ink, width=2)
        im.paste(thumb, (px, py))
        d.text((x, py + th2 + 40), lab, font=_font(22, bold=True), fill=ink, anchor="mt")
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
    im.save(LST / "05_included.jpg", quality=92)
    print("  05 included")


def how_to():
    side = 1600
    bg_c = tuple(int(mc.BG.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    ink = tuple(int(mc._P["ink"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    im = Image.new("RGB", (side, side), bg_c)
    d = ImageDraw.Draw(im)
    d.text((side // 2, 90), "How it works", font=_font(42, bold=True, serif=True), fill=ink, anchor="mt")
    steps = [
        ("1", "Download", "ZIP arrives instantly after purchase"),
        ("2", "Choose ratio", "2:3 · 3:4 · 4:5 · 5:7 · ISO/A"),
        ("3", "Print", "Home, local shop, or online lab"),
        ("4", "Frame & hang", "Mat optional — looks sharp either way"),
    ]
    y = 240
    for n, t, s in steps:
        d.ellipse([140, y, 240, y + 100], outline=ink, width=3)
        d.text((190, y + 50), n, font=_font(34, bold=True), fill=ink, anchor="mm")
        d.text((290, y + 25), t, font=_font(34, bold=True, serif=True), fill=ink, anchor="lt")
        d.text((290, y + 80), s, font=_font(24), fill=ink, anchor="lt")
        y += 280
    im.save(LST / "06_howto.jpg", quality=92)
    print("  06 howto")


def main():
    print(f"Metatron's Cube  [{PAL} / {STYLE}]")
    print("prints…")
    build_prints()
    print("listing…")
    hero()
    detail()
    framed()
    layers_card()
    included()
    how_to()
    print("DONE →", BASE)


if __name__ == "__main__":
    main()
