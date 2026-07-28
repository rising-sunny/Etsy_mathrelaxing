"""
package_brain_games.py — buyer deliverable + Etsy listing images
================================================================
Takes the rendered pages in out/pages/ (produced by generate_brain_games.py)
and builds:
  - a short styled Print Guide PDF
  - the buyer ZIP (the full puzzle book PDF + the guide)
  - 5 Etsy listing images (listing/*.jpg) in the MathRelaxing editorial style

  python generate_brain_games.py   # first, to render out/pages + the PDF
  python package_brain_games.py
"""
from __future__ import annotations
import glob, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import img2pdf

import generate_brain_games as G
from generate_brain_games import hx, F, DISP, HEAD, BODY, ITAL, W, H

BASE = Path(__file__).resolve().parent
OUT = BASE / "out"
PAGES = OUT / "pages"
DEL = BASE / "deliverable"; DEL.mkdir(exist_ok=True)
LST = BASE / "listing"; LST.mkdir(exist_ok=True)

PAPER, INK, INK_SOFT, MUTED = G.PAPER, G.INK, G.INK_SOFT, G.MUTED
ACCENT, GRID = G.ACCENT, G.GRID
PDF_NAME = "MathRelaxing_Brain_Games.pdf"
DPI = 300


def page_img(n):
    return Image.open(PAGES / f"p{n:02d}.jpg").convert("RGB")


def bg(S, top=(246, 243, 234), bot=(232, 227, 216)):
    import numpy as np
    g = np.linspace(0, 1, S)[:, None]; a = np.zeros((S, S, 3), np.uint8)
    for i in range(3):
        a[:, :, i] = (top[i]*(1-g) + bot[i]*g).astype(np.uint8)
    return Image.fromarray(a)


def shadow(canvas, x, y, w, h, blur=16, dark=(60, 66, 74), op=95):
    sh = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(sh).rectangle((x+8, y+12, x+w+8, y+h+12), fill=op)
    canvas.paste(Image.new("RGB", canvas.size, dark), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))


def paste_page(canvas, n, cx, cy, target_h, crop=None):
    im = page_img(n)
    if crop:
        im = im.crop(crop)
    scale = target_h / im.height
    w = int(im.width*scale); h = int(im.height*scale)
    im = im.resize((w, h), Image.LANCZOS)
    x = cx - w//2; y = cy - h//2
    shadow(canvas, x, y, w, h)
    canvas.paste(im, (x, y))
    ImageDraw.Draw(canvas).rectangle((x, y, x+w-1, y+h-1), outline=hx("#d8d2c4"), width=2)
    return x, y, w, h


# ── listing images ────────────────────────────────────────────────────────────
def li_hero():
    S = 2000; c = bg(S); d = ImageDraw.Draw(c)
    d.text((S//2, 150), "BRAIN GAMES", font=F("Cinzel-SemiBold.ttf", 92), fill=hx(INK), anchor="mm")
    d.text((S//2, 246), "A printable puzzle book — Sudoku · Mazes · STEM word searches",
           font=ITAL(38), fill=hx(INK_SOFT), anchor="mm")
    d.line([(S//2-320, 316), (S//2+320, 316)], fill=hx(ACCENT), width=3)
    # three overlapping page cards: maze, word search, sudoku on top
    th = 1180
    paste_page(c, 9, int(S*0.30), int(S*0.60), th)      # a maze page
    paste_page(c, 15, int(S*0.70), int(S*0.60), th)     # a word search page
    paste_page(c, 3, int(S*0.50), int(S*0.56), th+60)   # sudoku page on top
    d.text((S//2, S-70), "MathRelaxing", font=HEAD(40), fill=hx(INK), anchor="mm")
    c.save(LST / "01_hero.jpg", quality=92); print("li 01_hero")


def li_showcase(n, fname, title, sub):
    S = 2000; c = bg(S); d = ImageDraw.Draw(c)
    d.text((S//2, 150), title, font=DISP(64), fill=hx(INK), anchor="mm")
    d.text((S//2, 232), sub, font=ITAL(36), fill=hx(INK_SOFT), anchor="mm")
    d.line([(S//2-240, 300), (S//2+240, 300)], fill=hx(ACCENT), width=3)
    paste_page(c, n, S//2, int(S*0.585), int(S*0.66))
    d.text((S//2, S-70), "MathRelaxing", font=HEAD(38), fill=hx(INK), anchor="mm")
    c.save(LST / fname, quality=92); print("li", fname)


def li_included():
    S = 2000; c = bg(S, (247, 244, 237), (236, 231, 221)); d = ImageDraw.Draw(c)
    d.text((S//2, 210), "WHAT YOU GET", font=DISP(80), fill=hx(INK), anchor="mm")
    d.line([(S//2-230, 300), (S//2+230, 300)], fill=hx(ACCENT), width=3)
    items = ["12 Sudoku puzzles — Easy, Medium & Hard",
             "6 hand-crafted mazes, increasing in size",
             "4 STEM word searches — math, science, space",
             "Full answer keys for every puzzle",
             "22-page book · US Letter · 300 DPI print quality",
             "Instant download — print at home, forever",
             "For classrooms, road trips, quiet time"]
    y = 430
    for it in items:
        d.ellipse((S//2-560, y+16, S//2-534, y+42), fill=hx(ACCENT))
        d.text((S//2-505, y), it, font=BODY(46), fill=hx("#3a3d34"), anchor="lm"); y += 96
    d.text((S//2, S-130), "MathRelaxing", font=HEAD(42), fill=hx(INK), anchor="mm")
    c.save(LST / "05_included.jpg", quality=92); print("li 05_included")


def build_listing_images():
    li_hero()
    li_showcase(3, "02_sudoku.jpg", "SUDOKU", "Easy to hard — every puzzle has one unique solution")
    li_showcase(11, "03_mazes.jpg", "MAZES", "Six clean, solvable labyrinths that grow with you")
    li_showcase(15, "04_wordsearch.jpg", "WORD SEARCH", "STEM themes — mathematics, science, geometry, space")
    li_included()


# ── print guide + zip ─────────────────────────────────────────────────────────
def build_guide():
    c = Image.new("RGB", (W, H), hx(PAPER)); d = ImageDraw.Draw(c)
    cx = W//2
    d.text((cx, 300), "BRAIN GAMES", font=DISP(64), fill=hx(INK), anchor="mm")
    d.text((cx, 384), "Printable Puzzle Book — Quick Guide", font=ITAL(38), fill=hx(INK_SOFT), anchor="mm")
    d.line([(cx-260, 452), (cx+260, 452)], fill=hx(ACCENT), width=3)
    body = [
        ("WHAT'S INSIDE", [
            "- 22-page puzzle book (single PDF), US Letter, 300 DPI",
            "- 12 Sudoku (easy / medium / hard), 6 mazes, 4 STEM word searches",
            "- Full answer keys for every puzzle at the back",
        ]),
        ("HOW TO PRINT", [
            "1. Open MathRelaxing_Brain_Games.pdf in any PDF reader.",
            "2. Print the pages you want at 100% / 'Actual size'.",
            "3. Plain paper is fine; black & white prints perfectly.",
            "4. Reprint any page as many times as you like.",
        ]),
        ("HOW TO PLAY", [
            "- Sudoku: fill the grid so 1-9 appear once per row, column and box.",
            "- Mazes: draw a path from the entrance to the exit.",
            "- Word search: find each listed word (across, down and diagonal).",
        ]),
        ("NOTES", [
            "- For personal & classroom use. Digital download - nothing is shipped.",
            "- Answer keys are the last pages - print only the puzzles to keep them a secret.",
        ]),
    ]
    y = 560
    for head, lines in body:
        d.text((240, y), head, font=DISP(40), fill=hx(ACCENT)); y += 80
        for ln in lines:
            d.text((260, y), ln, font=BODY(33), fill=hx("#403c34")); y += 60
        y += 44
    d.text((cx, H-150), "Made by MathRelaxing", font=HEAD(34), fill=hx(INK), anchor="mm")
    png = DEL / "_guide.png"; c.save(png)
    pdf = DEL / "Print_Guide.pdf"
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert([str(png)], layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    png.unlink(); print("guide ->", pdf.name)


def build_zip():
    z = BASE / "MathRelaxing_Brain_Games.zip"
    if z.exists():
        z.unlink()
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUT / PDF_NAME, PDF_NAME)
        zf.write(DEL / "Print_Guide.pdf", "Print_Guide.pdf")
    print(f"ZIP -> {z.name} ({z.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    build_listing_images(); build_guide(); build_zip()
    print("DONE")
