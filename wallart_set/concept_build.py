"""
concept_build.py — deliverables + listing images for the Harmonic Series
scientific-plate poster. 5 aspect ratios @300 DPI, a delivery ZIP, and the
Etsy listing photos (all in the plate's technical lab-paper aesthetic).
"""
import io
import os
import zipfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter

import concept_poster as cp

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", "concept", "harmonic")
PRINTS = os.path.join(BASE, "prints")
LST = os.path.join(BASE, "listing")
for d in (PRINTS, LST):
    os.makedirs(d, exist_ok=True)
SANS = cp.SANS; MONO = cp.MONO
PAPER, INK, SUB, ACC = cp.PAPER, cp.INK, cp.SUB, cp.ACC

RATIOS = {"2x3": 2/3, "3x4": 3/4, "4x5": 4/5, "5x7": 5/7, "ISO": 1/np.sqrt(2)}
BASE_W = 10.0            # all ratios share width -> identical layout


def build_prints():
    for tag, a in RATIOS.items():
        H = BASE_W / a
        fig = cp.render_harmonic(BASE_W, H, dpi=300)
        fig.savefig(os.path.join(PRINTS, f"HarmonicSeries_{tag}.jpg"),
                    facecolor=PAPER, dpi=300)
        plt.close(fig)
    zpath = os.path.join(BASE, "HarmonicSeries_prints.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for tag in RATIOS:
            z.write(os.path.join(PRINTS, f"HarmonicSeries_{tag}.jpg"),
                    f"HarmonicSeries_{tag}.jpg")
        z.writestr("READ-ME.txt",
                   "HARMONIC SERIES - Modes of a Vibrating String\n"
                   "5 aspect ratios, 300 DPI. Personal use only.\n"
                   "Every line is computed from the physics - not AI, not clip art.\n")
    print("prints + zip", f"{os.path.getsize(zpath)/1e6:.2f} MB")


def _plate_img(dpi=150):
    return cp.to_pil(cp.render_harmonic(BASE_W, BASE_W / (4/5), dpi=dpi), dpi=dpi)


def hero():
    _plate_img(dpi=160).save(os.path.join(LST, "01_hero.jpg"), quality=92)
    print("01 hero")


def detail():
    im = _plate_img(dpi=200)
    w, h = im.size
    crop = im.crop((int(w*0.02), int(h*0.14), int(w*0.98), int(h*0.44)))
    crop.save(os.path.join(LST, "02_detail.jpg"), quality=92)
    print("02 detail")


def framed():
    plate = _plate_img(dpi=150)
    W, H = 2000, 1600
    wall = Image.new("RGB", (W, H), (214, 208, 198))
    ph = 1180
    pw = int(plate.width * ph / plate.height)
    plate = plate.resize((pw, ph))
    mat = 34; fr = 20
    card = Image.new("RGB", (pw + 2*mat + 2*fr, ph + 2*mat + 2*fr), (30, 28, 25))
    inner = Image.new("RGB", (pw + 2*mat, ph + 2*mat), "#f7f6f2")
    inner.paste(plate, (mat, mat)); card.paste(inner, (fr, fr))
    x = (W - card.width)//2; y = (H - card.height)//2
    sh = Image.new("RGBA", (card.width+80, card.height+80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 44, 40+card.width, 44+card.height], fill=(40, 38, 34, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    wall.paste(sh, (x-40+14, y-40+18), sh); wall.paste(card, (x, y))
    wall.save(os.path.join(LST, "03_framed.jpg"), quality=90)
    print("03 framed")


def _card(path, draw_fn):
    fig = plt.figure(figsize=(12.8, 10.24), dpi=125)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    draw_fn(ax)
    fig.savefig(path, facecolor=PAPER); plt.close(fig)


def sizes():
    def d(ax):
        ax.text(0.5, 0.9, "FIVE ASPECT RATIOS INCLUDED", ha="center", fontproperties=SANS,
                fontsize=24, color=INK, weight="bold")
        ax.text(0.5, 0.83, "300 DPI  ·  print small or large", ha="center",
                fontproperties=MONO, fontsize=13, color=ACC)
        labs = [("2:3", 2/3, "4×6 · 12×18 · 24×36"), ("3:4", 3/4, "9×12 · 18×24"),
                ("4:5", 4/5, "8×10 · 16×20"), ("5:7", 5/7, "5×7 · 15×21"),
                ("ISO/A", 1/np.sqrt(2), "A4 · A3 · A2")]
        for i, (lab, a, sz) in enumerate(labs):
            cx = 0.1 + i*0.2
            w = 0.06; h = w/a
            ax.add_patch(plt.Rectangle((cx-w/2, 0.5-h/2), w, h, fill=False,
                         edgecolor=INK, lw=1.6, transform=ax.transAxes))
            ax.text(cx, 0.5+h/2+0.04, lab, ha="center", fontproperties=MONO, fontsize=14, color=INK)
            ax.text(cx, 0.5-h/2-0.06, sz, ha="center", va="top", fontproperties=SANS,
                    fontsize=9.5, color=SUB)
        ax.text(0.5, 0.12, "Instant digital download  ·  for personal use", ha="center",
                fontproperties=SANS, fontsize=12, color=SUB)
    _card(os.path.join(LST, "04_sizes.jpg"), d)
    print("04 sizes")


def note():
    def d(ax):
        ax.text(0.5, 0.82, "DRAWN FROM THE REAL PHYSICS", ha="center", fontproperties=SANS,
                fontsize=25, color=INK, weight="bold")
        lines = ["Every wave on this plate is computed from the equation of a",
                 "vibrating string — node by node, harmonic by harmonic.",
                 "",
                 "No stock images. No AI. No clip art.",
                 "",
                 "A real diagram of a real idea, made to hang on a wall."]
        y = 0.66
        for t in lines:
            ax.text(0.5, y, t, ha="center", fontproperties=SANS, fontsize=15,
                    color=INK if "No AI" not in t else ACC)
            y -= 0.075
        ax.text(0.5, 0.1, "∑ 1/n  →  ∞", ha="center", fontproperties=MONO, fontsize=16, color=ACC)
    _card(os.path.join(LST, "05_note.jpg"), d)
    print("05 note")


if __name__ == "__main__":
    build_prints()
    hero(); detail(); framed(); sizes(); note()
    print("DONE ->", BASE)
