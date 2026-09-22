"""
build_listing_images.py — Etsy listing images for the Better Buy unit-rates PDF.

The three source graphics came from the TPT upload and are WEBP, which Etsy
does not accept (JPG, PNG or GIF only), so they are converted here. They are
also 1254 px square; Etsy's floor is 1000 px but it recommends 2000 px so the
zoom view stays sharp, and this artwork is flat vector-style so it takes the
resample cleanly.

Two further images are built from the actual PDF pages. Three images is thin
for Etsy, and page thumbnails do something the graphics cannot: show the buyer
the real thing rather than a claim about it.

  python better_buy/build_listing_images.py
"""
from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = Path("/tmp/claude-0/-home-user-Etsy-mathrelaxing/"
           "e24b7ec7-cf86-5f97-890f-aa4cef39fee4/images")
PDF = HERE / "Better_Buy_Unit_Rates.pdf"
OUT = HERE / "listing_images"

# sampled from the supplied graphics so the new images match them exactly
NAVY = (18, 43, 82)
ORANGE = (244, 127, 36)
PAPER = (255, 255, 255)
GREY = (120, 126, 136)
S = 2000

AF = ROOT / "lulu_books" / "assets" / "fonts"


def F_(name, size):
    return ImageFont.truetype(str(AF / name), size)


def convert_sources():
    """WEBP -> JPG at 2000 px. Etsy rejects WEBP outright."""
    order = [("2.webp", "01_hero.jpg"), ("1.webp", "02_whats_included.jpg"),
             ("3.webp", "03_sample_pages.jpg")]
    for src, dst in order:
        im = Image.open(SRC / src).convert("RGB").resize((S, S), Image.LANCZOS)
        im.save(OUT / dst, "JPEG", quality=94, subsampling=0)
        print("  ", dst, im.size)


def page_png(doc, i, height):
    p = doc[i]
    zoom = height / p.rect.height
    pm = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)


def header(d, title, sub):
    d.rectangle([0, 0, S, 300], fill=NAVY)
    d.text((S // 2, 96), "MATHRELAXING", font=F_("Raleway.ttf", 40),
           fill=ORANGE, anchor="mm")
    d.text((S // 2, 178), title, font=F_("Cinzel-SemiBold.ttf", 82),
           fill=PAPER, anchor="mm")
    d.text((S // 2, 252), sub, font=F_("Raleway.ttf", 38), fill=(196, 206, 222),
           anchor="mm")


def inside_the_pdf(doc):
    """Six real pages, so the buyer sees the resource, not a promise."""
    c = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(c)
    header(d, "INSIDE THE PDF", "15 pages  ·  US Letter  ·  answer keys included")
    picks = [(0, "Cover"), (2, "Worked example"), (4, "Level 1"),
             (6, "Level 2"), (8, "$20 challenge"), (10, "Answer key")]
    gap, top, lab = 34, 360, 74
    # Size the page by BOTH axes. Deriving height from width alone gave two
    # rows of 804 px, which overran the 2000 px canvas by 46 px and pushed the
    # bottom row's captions off the image entirely.
    ch = (S - top - 2 * lab - gap) // 2
    cw = int(ch * 8.5 / 11)
    for i, (pg, label) in enumerate(picks):
        r, col = divmod(i, 3)
        im = page_png(doc, pg, ch)
        im.thumbnail((cw, ch), Image.LANCZOS)
        x = (S - 3 * cw - 2 * gap) // 2 + col * (cw + gap) + (cw - im.width) // 2
        y = top + r * (ch + lab)
        c.paste(im, (x, y))
        d.rectangle([x, y, x + im.width - 1, y + im.height - 1], outline=(214, 218, 226), width=3)
        d.text((x + im.width // 2, y + im.height + 18), label,
               font=F_("Raleway.ttf", 32), fill=GREY, anchor="ma")
    c.save(OUT / "04_inside_the_pdf.jpg", "JPEG", quality=93, subsampling=0)
    print("   04_inside_the_pdf.jpg")


def answer_keys(doc):
    """A key page at readable size -- the thing teachers actually check for."""
    c = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(c)
    header(d, "ANSWER KEYS", "every rate worked out, not just the letter")
    im = page_png(doc, 12, S - 480)
    im.thumbnail((S - 260, S - 480), Image.LANCZOS)
    x = (S - im.width) // 2
    c.paste(im, (x, 350))
    d.rectangle([x, 350, x + im.width - 1, 350 + im.height - 1],
                outline=(214, 218, 226), width=3)
    d.rectangle([0, S - 108, S, S], fill=ORANGE)
    d.text((S // 2, S - 54), "TEACHER GUIDE + SUGGESTED SCORING INCLUDED",
           font=F_("Raleway.ttf", 44), fill=PAPER, anchor="mm")
    c.save(OUT / "05_answer_keys.jpg", "JPEG", quality=93, subsampling=0)
    print("   05_answer_keys.jpg")


def main():
    OUT.mkdir(exist_ok=True)
    convert_sources()
    doc = pymupdf.open(PDF)
    inside_the_pdf(doc)
    answer_keys(doc)


if __name__ == "__main__":
    main()
