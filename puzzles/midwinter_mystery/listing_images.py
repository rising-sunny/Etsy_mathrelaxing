"""Etsy listing images (2000x2000) for The Midwinter Theorem, rendered from the Letter PDF."""
import os
import random

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PDF = os.path.join(HERE, "out", "Midwinter_Theorem_Mystery_Advent_Letter.pdf")
OUT = os.path.join(HERE, "listing")
FONTS = os.path.join(ROOT, "lulu_books", "assets", "fonts")
NAVY, GOLD, CREAM, WINE = (19, 25, 46), (201, 162, 75), (248, 244, 235), (90, 26, 36)
S = 2000
BAND = 170


def font(name, size):
    path = {"cinzel": os.path.join(FONTS, "Cinzel-SemiBold.ttf"),
            "sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "sansb": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"}[name]
    return ImageFont.truetype(path, size)


def page(doc, i, width):
    pix = doc[i].get_pixmap(dpi=200)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def canvas():
    im = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(im)
    rng = random.Random(5)
    for _ in range(260):
        x, y, r = rng.uniform(0, S), rng.uniform(0, S - BAND), rng.uniform(1, 3.2)
        c = int(rng.uniform(90, 230))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 10)))
    d.rectangle([0, S - BAND, S, S], fill=(0, 0, 0))
    logo = Image.open(os.path.join(ROOT, "mathrelaxing_logo.png")).convert("RGBA")
    logo.thumbnail((440, BAND - 40))
    im.paste(logo, ((S - logo.width) // 2, S - BAND + (BAND - logo.height) // 2), logo)
    return im


def paste_shadow(base, im, xy, angle=0):
    im = im.convert("RGBA")
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    mask = im.split()[3].point(lambda a: 150 if a else 0)
    sh.paste((0, 0, 0, 255), (40, 40), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    base.paste(sh, (xy[0] - 25, xy[1] - 15), sh)
    base.paste(im, xy, im)


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((S - w) / 2, y), text, font=f, fill=fill)


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(PDF)
    n = len(doc)

    # 1 hero
    im = canvas()
    d = ImageDraw.Draw(im)
    centered(d, 70, "PRINTABLE MURDER MYSTERY", font("cinzel", 92), CREAM)
    centered(d, 180, "ADVENT CALENDAR FOR ADULTS", font("cinzel", 70), GOLD)
    paste_shadow(im, page(doc, 0, 760), (150, 360), angle=4)
    paste_shadow(im, page(doc, 12, 760), (1040, 400), angle=-4)
    centered(d, 1560, "24 logic puzzles  ·  36 suspects  ·  1 killer", font("sans", 58), CREAM)
    centered(d, 1650, "Instant download  ·  US Letter + A4", font("sans", 46), GOLD)
    im.save(os.path.join(OUT, "01_hero.jpg"), quality=92)

    # 2 how it works
    im = canvas()
    d = ImageDraw.Draw(im)
    centered(d, 70, "HOW IT WORKS", font("cinzel", 96), CREAM)
    paste_shadow(im, page(doc, 5, 900), (100, 250))
    steps = [("1", "Read the day's", "journal entry"), ("2", "Solve the logic", "puzzle"),
             ("3", "The starred number", "picks the true clue"), ("4", "Cross off", "suspects"),
             ("5", "Christmas Eve:", "one name remains")]
    y = 330
    for num, a, b in steps:
        d.ellipse([1090, y, 1190, y + 100], fill=GOLD)
        w = d.textlength(num, font=font("sansb", 60))
        d.text((1140 - w / 2, y + 16), num, font=font("sansb", 60), fill=NAVY)
        d.text((1230, y + 2), a, font=font("sans", 52), fill=CREAM)
        d.text((1230, y + 58), b, font=font("sans", 44), fill=GOLD)
        y += 250
    im.save(os.path.join(OUT, "02_how_it_works.jpg"), quality=92)

    # 3 puzzle variety
    im = canvas()
    d = ImageDraw.Draw(im)
    centered(d, 70, "3 PUZZLE TYPES, GROWING HARDER", font("cinzel", 74), CREAM)
    centered(d, 170, "Sudoku  ·  Futoshiki  ·  Skyscrapers  —  every one has a unique solution",
             font("sans", 44), GOLD)
    for k, i in enumerate((10, 12, 14)):
        paste_shadow(im, page(doc, i, 560), (90 + k * 620, 330 + (k % 2) * 60), angle=(k - 1) * -3)
    im.save(os.path.join(OUT, "03_puzzles.jpg"), quality=92)

    # 4 cast + tracker
    im = canvas()
    d = ImageDraw.Draw(im)
    centered(d, 70, "MEET THE 36 SUSPECTS", font("cinzel", 92), CREAM)
    centered(d, 180, "Every guest has an alibi. Only one is lying.", font("sans", 48), GOLD)
    paste_shadow(im, page(doc, 2, 820), (120, 330), angle=3)
    paste_shadow(im, page(doc, 4, 820), (1060, 360), angle=-3)
    im.save(os.path.join(OUT, "04_cast.jpg"), quality=92)

    # 5 what's included
    im = canvas()
    d = ImageDraw.Draw(im)
    centered(d, 90, "WHAT'S INCLUDED", font("cinzel", 96), CREAM)
    items = [f"{n}-page printable PDF  (US Letter + A4)", "How-to-play guide",
             "36 suspect profile cards", "Suspect elimination tracker",
             "24 daily journal entries + puzzles", "Sealed Final Reveal page",
             "Full solutions for every puzzle", "Print at home  ·  play solo, as a couple or family"]
    y = 330
    for t in items:
        d.text((300, y), "★", font=ImageFont.truetype("DejaVuSans.ttf", 56), fill=GOLD)
        d.text((390, y + 4), t, font=font("sans", 58), fill=CREAM)
        y += 140
    im.save(os.path.join(OUT, "05_included.jpg"), quality=92)
    print("listing images ->", OUT)


if __name__ == "__main__":
    main()
