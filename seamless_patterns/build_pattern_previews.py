"""
build_pattern_previews.py — Etsy listing images for the seamless pattern pack.

Thumbnails come from the tiles that actually ship, and the proof sheet is a
real 3x3 repeat rather than a mock-up: the one thing this listing claims is
that the tiles tile, so the buyer should be able to see it.

  python seamless_patterns/build_pattern_previews.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_seamless_pack as B  # noqa: E402

OUT = HERE / "previews"
OUT.mkdir(exist_ok=True)
TILES = HERE / "out"

AF = ROOT / "lulu_books" / "assets" / "fonts"
CINZEL = str(AF / "Cinzel-SemiBold.ttf")
RALEWAY = str(AF / "Raleway.ttf")
RALEWAY_I = str(AF / "Raleway-Italic.ttf")

CREAM = (245, 242, 234)
INK = (38, 35, 30)
SOFT = (122, 116, 104)
RUST = (176, 88, 56)
LINE = (214, 207, 192)
S = 2000


def F_(path, size):
    return ImageFont.truetype(path, size)


def tiled(slug, reps, box, folder="PNG"):
    """A pattern repeated reps x reps, scaled into box."""
    t = Image.open(TILES / folder / f"{slug}.png").convert("RGB")
    small = t.resize((max(1, box // reps), max(1, box // reps)), Image.LANCZOS)
    m = Image.new("RGB", (box, box), "white")
    for i in range(reps):
        for j in range(reps):
            m.paste(small, (i * small.width, j * small.height))
    return m


def header(d, title, sub, h=250):
    d.rectangle([0, 0, S, h], fill=INK)
    d.text((S // 2, h * 0.31), title, font=F_(CINZEL, 74), fill=CREAM, anchor="mm")
    d.text((S // 2, h * 0.67), sub, font=F_(RALEWAY, 38), fill=(198, 190, 175), anchor="mm")


def hero():
    c = Image.new("RGB", (S, S), CREAM)
    picks = ["celtic_classic", "star_classic", "arcs_ribbon",
             "circles_classic", "celtic_lattice", "star_twelvepoint",
             "arcs_classic", "circles_bold", "celtic_bold"]
    # 3 cells + 2 gaps must clear the header and still fit: 300 + 3*560 + 2*26
    # came to 2032 on a 2000 px canvas and clipped the bottom row.
    gap, top = 26, 290
    cell = (S - top - 2 * gap - 24) // 3
    for i, slug in enumerate(picks):
        r, col = divmod(i, 3)
        img = tiled(slug, 2, cell)
        x = (S - 3 * cell - 2 * gap) // 2 + col * (cell + gap)
        y = top + r * (cell + gap)
        c.paste(img, (x, y))
        ImageDraw.Draw(c).rectangle([x, y, x + cell - 1, y + cell - 1],
                                    outline=LINE, width=3)
    d = ImageDraw.Draw(c)
    header(d, "SEAMLESS PATTERN PACK", "24 geometric repeats  ·  PNG + SVG  ·  commercial use")
    c.save(OUT / "01_hero.jpg", "JPEG", quality=92)


def all_24():
    c = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(c)
    header(d, "ALL 24 PATTERNS", "four families  ·  six weights and scales each")
    cell, gap, top = 290, 14, 300
    for i, (_, slug, *_rest) in enumerate(B.DESIGNS):
        r, col = divmod(i, 6)
        img = tiled(slug, 2, cell)
        x = (S - 6 * cell - 5 * gap) // 2 + col * (cell + gap)
        y = top + r * (cell + gap)
        c.paste(img, (x, y))
        d.rectangle([x, y, x + cell - 1, y + cell - 1], outline=LINE, width=2)
    c.save(OUT / "02_all_patterns.jpg", "JPEG", quality=92)


def proof():
    """The claim, shown: one tile repeated, with the joins marked."""
    c = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(c)
    header(d, "NO VISIBLE JOIN", "every tile is computed to repeat exactly")
    box, top = 1500, 330
    x0 = (S - box) // 2
    c.paste(tiled("celtic_classic", 3, box), (x0, top))
    d.rectangle([x0, top, x0 + box - 1, top + box - 1], outline=LINE, width=3)
    third = box // 3
    for k in (1, 2):                       # where the tiles meet
        for a, b in (((x0 + k * third, top), (x0 + k * third, top + box)),
                     ((x0, top + k * third), (x0 + box, top + k * third))):
            d.line([a, b], fill=RUST, width=2)
    d.text((S // 2, top + box + 62),
           "red lines mark where the tiles meet — the pattern runs straight through",
           font=F_(RALEWAY_I, 34), fill=SOFT, anchor="mm")
    c.save(OUT / "03_seamless_proof.jpg", "JPEG", quality=92)


def colourways():
    c = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(c)
    header(d, "FOUR COLOURWAYS", "indigo  ·  terracotta  ·  sage  ·  gold on ink")
    names = ["indigo", "terracotta", "sage", "gold"]
    cell, gap, top = 780, 30, 320
    for i, pal in enumerate(names):
        r, col = divmod(i, 2)
        img = tiled(f"celtic_classic_{pal}", 2, cell, folder="colourways")
        x = (S - 2 * cell - gap) // 2 + col * (cell + gap)
        y = top + r * (cell + gap)
        c.paste(img, (x, y))
        d.rectangle([x, y, x + cell - 1, y + cell - 1], outline=LINE, width=3)
        d.text((x + cell // 2, y + cell + 22), pal.upper(),
               font=F_(RALEWAY, 30), fill=SOFT, anchor="ma")
    c.save(OUT / "04_colourways.jpg", "JPEG", quality=92)


def included():
    c = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(c)
    header(d, "WHAT'S INCLUDED", "one instant download  ·  97 files")
    rows = [
        ("24", "Seamless PNG tiles", "3000 x 3000 px, 300 dpi, white ground"),
        ("24", "Transparent PNG tiles", "drop straight onto any background colour"),
        ("24", "SVG vectors", "every stroke editable — recolour, rescale, redraw"),
        ("24", "Colourway PNGs", "six patterns in indigo, terracotta, sage and gold"),
        ("1", "Usage guide", "Photoshop, Illustrator, Procreate, Canva, sublimation"),
    ]
    y = 380
    for num, title, sub in rows:
        d.ellipse([150, y, 150 + 104, y + 104], fill=RUST)
        d.text((202, y + 52), num, font=F_(CINZEL, 44), fill=CREAM, anchor="mm")
        d.text((300, y + 22), title, font=F_(CINZEL, 46), fill=INK)
        d.text((300, y + 78), sub, font=F_(RALEWAY_I, 31), fill=SOFT)
        y += 150
    d.rectangle([150, y + 30, S - 150, y + 36], fill=LINE)
    d.text((S // 2, y + 108), "COMMERCIAL USE INCLUDED",
           font=F_(CINZEL, 52), fill=RUST, anchor="mm")
    d.text((S // 2, y + 186),
           "sell what you make with them — fabric, wrapping, tumblers, stationery",
           font=F_(RALEWAY, 33), fill=SOFT, anchor="mm")
    d.text((S // 2, y + 240), "(the pattern files themselves may not be resold)",
           font=F_(RALEWAY_I, 29), fill=SOFT, anchor="mm")
    c.save(OUT / "05_included.jpg", "JPEG", quality=92)


def main():
    hero(); all_24(); proof(); colourways(); included()
    for p in sorted(OUT.glob("*.jpg")):
        print("  ", p.name)


if __name__ == "__main__":
    main()
