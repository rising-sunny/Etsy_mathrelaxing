"""
build_spiral_assets.py — print files, ZIP and listing previews for the
"Spiral Tilings" wall-art set.

Sizes follow the Turing set already in the shop (9x11.5 in and 11x14 in at
300 dpi), so the two sets pack and price consistently.

  python spiral_wall/build_spiral_assets.py
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import designs as D  # noqa: E402

PRINTS = HERE / "prints"
PREV = HERE / "previews"
ZIP_NAME = "Spiral_Tilings_Wall_Art_Set_of_6.zip"
SIZES = [(9.0, 11.5), (11.0, 14.0)]
DPI = 300

AF = ROOT / "lulu_books" / "assets" / "fonts"
CINZEL, RALEWAY = str(AF / "Cinzel-SemiBold.ttf"), str(AF / "Raleway.ttf")
RALEWAY_I = str(AF / "Raleway-Italic.ttf")
CREAM, INK, SOFT, LINE = (245, 242, 234), (38, 35, 30), (122, 116, 104), (214, 207, 192)
S = 2000

README = """SPIRAL TILINGS - Wall Art Set of 6
MathRelaxing

Six prints of a spiral tiling: a single tile shape, repeated so that every
piece stays the same size while the whole plane winds around a centre.

Rings of constant thickness are cut into pieces whose count grows with the
radius, so the tiles never stretch. The zigzag on each ring boundary keeps a
constant pitch measured along the arc, which is what lets rings with different
piece counts still lock together. Those surplus pieces per ring are exactly
what curl the pattern into spiral arms, and the colour follows the same
modular count -- so what you see is the arithmetic, not a filter.

01 Vortex     teal and rust        02 Helix     indigo and amber
03 Radiant    terracotta and clay  04 Corona    forest and ochre
05 Drift      plum and gold        06 Pinwheel  monochrome

WHAT'S INCLUDED
  Each design at 9 x 11.5 in and 11 x 14 in, 300 dpi JPG.
  Both fit standard frames; print at home, at a copy shop or online.

This is a DIGITAL download - nothing is shipped.
(c) MathRelaxing. Personal use only. Not for redistribution or resale.
"""


def build_prints():
    PRINTS.mkdir(exist_ok=True)
    made = []
    for i, d in enumerate(D.DESIGNS, 1):
        for w, h in SIZES:
            fig = D.render(d, w, h, dpi=DPI)
            tag = f"{w:g}x{h:g}in".replace(".0", "")
            out = PRINTS / f"{i:02d}_{d['slug']}_{tag}_300dpi.jpg"
            fig.savefig(out, dpi=DPI, pil_kwargs={"quality": 90})
            plt.close(fig)
            made.append(out)
            print(f"  {out.name}  {Image.open(out).size}")
    return made


def build_zip(files):
    out = HERE / ZIP_NAME
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", README)
        for f in files:
            z.write(f, f.name)
    mb = out.stat().st_size / 1e6
    print(f"\n{ZIP_NAME}: {mb:.1f} MB, {len(files) + 1} archivos")
    if mb > 19.5:
        print("  WARNING: cerca del limite de 20 MB de Etsy")
    return out


def F_(p, s):
    return ImageFont.truetype(p, s)


def _thumb(slug, box):
    src = next(PRINTS.glob(f"*_{slug}_9x11.5in_300dpi.jpg"))
    im = Image.open(src).convert("RGB")
    im.thumbnail(box, Image.LANCZOS)
    return im


def build_previews():
    PREV.mkdir(exist_ok=True)
    # 01 hero: all six, 3 x 2
    c = Image.new("RGB", (S, S), CREAM)
    d_ = ImageDraw.Draw(c)
    d_.rectangle([0, 0, S, 250], fill=INK)
    d_.text((S // 2, 78), "SPIRAL TILINGS", font=F_(CINZEL, 76), fill=CREAM, anchor="mm")
    d_.text((S // 2, 168), "set of 6  ·  one tile, wound around a centre",
            font=F_(RALEWAY, 38), fill=(198, 190, 175), anchor="mm")
    gap, top = 30, 300
    cw = (S - 4 * gap) // 3
    ch = min(int(cw * 1.278), (S - top - 3 * gap) // 2)
    for i, dd in enumerate(D.DESIGNS):
        r, col = divmod(i, 3)
        im = _thumb(dd["slug"], (cw, ch))
        x = gap + col * (cw + gap) + (cw - im.width) // 2
        y = top + r * (ch + gap)
        c.paste(im, (x, y))
        d_.rectangle([x, y, x + im.width - 1, y + im.height - 1], outline=LINE, width=2)
    c.save(PREV / "01_hero.jpg", "JPEG", quality=92)

    # 02..04 single-design showcases
    for n, slug in ((2, "vortex"), (3, "helix"), (4, "drift")):
        c = Image.new("RGB", (S, S), CREAM)
        im = _thumb(slug, (int(S * 0.74), int(S * 0.86)))
        c.paste(im, ((S - im.width) // 2, (S - im.height) // 2 - 30))
        dd = ImageDraw.Draw(c)
        dd.rectangle([(S - im.width) // 2, (S - im.height) // 2 - 30,
                      (S + im.width) // 2 - 1, (S - im.height) // 2 - 30 + im.height - 1],
                     outline=LINE, width=3)
        title = next(x["title"] for x in D.DESIGNS if x["slug"] == slug)
        dd.text((S // 2, S - 96), title.upper(), font=F_(CINZEL, 54), fill=INK, anchor="mm")
        dd.text((S // 2, S - 42), "9 x 11.5 in  ·  11 x 14 in  ·  300 dpi",
                font=F_(RALEWAY_I, 32), fill=SOFT, anchor="mm")
        c.save(PREV / f"{n:02d}_{slug}.jpg", "JPEG", quality=92)

    # 05 what's included
    c = Image.new("RGB", (S, S), CREAM)
    dd = ImageDraw.Draw(c)
    dd.rectangle([0, 0, S, 250], fill=INK)
    dd.text((S // 2, 78), "WHAT'S INCLUDED", font=F_(CINZEL, 74), fill=CREAM, anchor="mm")
    dd.text((S // 2, 168), "one instant download  ·  12 files",
            font=F_(RALEWAY, 38), fill=(198, 190, 175), anchor="mm")
    rows = [("6", "Original designs", "vortex · helix · radiant · corona · drift · pinwheel"),
            ("2", "Sizes for each", "9 x 11.5 in and 11 x 14 in, both standard frame sizes"),
            ("300", "DPI", "sharp at full size — print at home or a copy shop"),
            ("0", "Text on the art", "nothing printed over the pattern")]
    y = 400
    for num, t1, t2 in rows:
        dd.ellipse([150, y, 150 + 104, y + 104], fill=(176, 88, 56))
        dd.text((202, y + 52), num, font=F_(CINZEL, 44 if len(num) < 3 else 34),
                fill=CREAM, anchor="mm")
        dd.text((300, y + 22), t1, font=F_(CINZEL, 46), fill=INK)
        dd.text((300, y + 78), t2, font=F_(RALEWAY_I, 31), fill=SOFT)
        y += 160
    dd.text((S // 2, y + 70), "computed from scratch — not AI, not a stock texture",
            font=F_(RALEWAY, 34), fill=SOFT, anchor="mm")
    c.save(PREV / "05_included.jpg", "JPEG", quality=92)
    for p in sorted(PREV.glob("*.jpg")):
        print("  ", p.name)


def main():
    files = build_prints()
    build_zip(files)
    build_previews()


if __name__ == "__main__":
    main()
