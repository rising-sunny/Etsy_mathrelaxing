"""
build_history_poster_assets.py — packaging for "History of Calculus"
======================================================================
Takes the finished poster master (history_of_calculus/history_of_calculus_v2_preview.png,
3600x5100 @ 300dpi, native ratio ~0.706 = ISO A-series) and builds:

  history_of_calculus/prints/*.jpg        — A4, A3 and native 12x17in masters
  history_of_calculus/History_of_Calculus_Math_Wall_Art.zip
  history_of_calculus/previews/*.jpg      — Etsy listing images

  python build_history_poster_assets.py
"""
import os
import zipfile

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "history_of_calculus")
MASTER = os.path.join(OUT, "history_of_calculus_v2_preview.png")
PRINTS = os.path.join(OUT, "prints"); os.makedirs(PRINTS, exist_ok=True)
PREVIEWS = os.path.join(OUT, "previews"); os.makedirs(PREVIEWS, exist_ok=True)
AF = os.path.join(BASE, "lulu_books", "assets", "fonts")

DARK = "#0d0f12"
CREAM = "#f0ece0"
SUB = "#8f8a78"
GOLD = "#c9a24b"
LINE = "#2c2a24"
CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RALEWAY = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RALEWAY_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")

DPI = 300
SIZES = {
    "12x17in": (12.0, 17.0),
    "A3": (11.69, 16.54),
    "A4": (8.27, 11.69),
}

README = """History of Calculus — Math Wall Art
MathRelaxing timeline poster

Nine milestones in the history of calculus, from Archimedes' method of
exhaustion to Robinson's nonstandard analysis — each paired with a bespoke
diagram and its defining equation. Dark, gold-linework editorial plate.

WHAT YOU GET
High-resolution JPG prints at 300 dpi, portrait / ISO-A ratio:
  • 12x17 in (signature size)
  • ISO A3
  • ISO A4

Print at home, a print shop, or online lab. Matte black frame recommended.
Frame not included. Personal use only.

© MathRelaxing
"""


def build_prints():
    master = Image.open(MASTER).convert("RGB")
    paths = []
    for label, (w_in, h_in) in SIZES.items():
        w_px, h_px = round(w_in * DPI), round(h_in * DPI)
        img = master.resize((w_px, h_px), Image.LANCZOS)
        p = os.path.join(PRINTS, f"history_of_calculus_{label}_300dpi.jpg")
        img.save(p, "JPEG", quality=92, dpi=(DPI, DPI))
        paths.append(p)
        print("print:", label, img.size, f"{os.path.getsize(p)//1024}KB")
    return paths


def build_zip(print_paths):
    zpath = os.path.join(OUT, "History_of_Calculus_Math_Wall_Art.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", README)
        for p in print_paths:
            z.write(p, os.path.basename(p))
    print("zip:", zpath, f"{os.path.getsize(zpath)//1024//1024}MB")
    return zpath


def build_previews():
    master = Image.open(MASTER).convert("RGB")
    w, h = master.size

    hero = master.resize((round(1400 * w / h), 1400), Image.LANCZOS)
    hero.save(os.path.join(PREVIEWS, "history_of_calculus_preview_1_hero.jpg"), quality=92)

    top = master.crop((0, 0, w, round(h * 0.34)))
    top = top.resize((round(1500 * top.width / top.height), 1500), Image.LANCZOS)
    top.save(os.path.join(PREVIEWS, "history_of_calculus_preview_2_detail_top.jpg"), quality=92)

    bot = master.crop((0, round(h * 0.80), w, h))
    bot = bot.resize((round(1500 * bot.width / bot.height), 1500), Image.LANCZOS)
    bot.save(os.path.join(PREVIEWS, "history_of_calculus_preview_3_detail_bottom.jpg"), quality=92)

    build_included_card()


def build_included_card():
    fig = plt.figure(figsize=(10, 8), dpi=150)
    fig.patch.set_facecolor(DARK)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(DARK); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.text(0.08, 0.86, "WHAT'S INCLUDED", fontsize=26, color=GOLD, fontproperties=CINZEL_R)
    ax.plot([0.08, 0.32], [0.80, 0.80], color=GOLD, lw=1.2)

    ax.text(0.08, 0.68, "History of Calculus", fontsize=30, color=CREAM, fontproperties=CINZEL)
    ax.text(0.08, 0.605, "A nine-milestone timeline plate, Archimedes to Robinson",
            fontsize=13.5, color=SUB, fontproperties=RALEWAY_I)

    rows = [
        ("12 × 17 in", "signature size, 300 dpi JPG"),
        ("ISO A3", "11.69 × 16.54 in, 300 dpi JPG"),
        ("ISO A4", "8.27 × 11.69 in, 300 dpi JPG"),
    ]
    y = 0.46
    for size, note in rows:
        ax.plot([0.08], [y + 0.012], "o", color=GOLD, ms=7, mec=DARK, mew=1.0)
        ax.text(0.115, y, size, fontsize=17, color=CREAM, fontproperties=CINZEL_R, va="center")
        ax.text(0.40, y, note, fontsize=12.5, color=SUB, fontproperties=RALEWAY, va="center")
        y -= 0.11

    ax.plot([0.08, 0.92], [0.10, 0.10], color=LINE, lw=1.0)
    ax.text(0.08, 0.055, "Instant digital download — no physical item ships. Personal use only.",
            fontsize=11.5, color=SUB, fontproperties=RALEWAY_I)
    ax.text(0.92, 0.055, "MathRelaxing", fontsize=12, color=GOLD, ha="right",
            fontproperties=CINZEL_R)

    p = os.path.join(PREVIEWS, "history_of_calculus_preview_4_included.jpg")
    fig.savefig(p, facecolor=DARK, pil_kwargs={"quality": 92})
    plt.close(fig)
    print("included card:", p)


if __name__ == "__main__":
    prints = build_prints()
    build_zip(prints)
    build_previews()
    print("DONE")
