"""
posterset_build.py — deliverables + listing images for a GALLERY POSTER SET
(6 scientific-plate prints sold together). Rides the 2026 "gallery wall set"
trend and back-to-school classroom demand. Reuses the physics / maths plate
engines. Pick the set with SET env (physics | math).

    SET=physics python posterset_build.py
"""
import os
import zipfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import physics_poster as physics
import concept_poster as maths

SET = os.environ.get("SET", "physics")
CFG = {
    "physics": {"mod": physics, "name": "Physics",
                "keys": ["relativity", "blackhole", "quantum", "maxwell", "planck", "gravity"],
                "slug": "PhysicsPosterSet"},
    "math": {"mod": maths, "name": "Mathematics",
             "keys": ["golden", "euler", "pi", "fourier", "ulam", "harmonic"],
             "slug": "MathPosterSet"},
}[SET]
MOD, SET_NAME, KEYS, SLUG = CFG["mod"], CFG["name"], CFG["keys"], CFG["slug"]

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", "posterset", SET)
PRINTS = os.path.join(BASE, "prints")
LST = os.path.join(BASE, "listing")
for d in (PRINTS, LST):
    os.makedirs(d, exist_ok=True)
PAPER, INK, SUB, ACC = maths.PAPER, maths.INK, maths.SUB, maths.ACC
SERIF = font_manager.FontProperties(family="DejaVu Serif")
_FONT = font_manager.findfont(SERIF)

RATIOS = {"2x3": 2/3, "3x4": 3/4, "4x5": 4/5, "5x7": 5/7, "ISO": 1/np.sqrt(2)}
BASE_W = 10.0


def font(sz):
    return ImageFont.truetype(_FONT, sz)


def plate(key, dpi=150, a=4/5):
    return MOD.to_pil(MOD.render(key, BASE_W, BASE_W / a, dpi=dpi), dpi=dpi)


def build_prints():
    for key in KEYS:
        for tag, a in RATIOS.items():
            fig = MOD.render(key, BASE_W, BASE_W / a, dpi=300)
            fig.savefig(os.path.join(PRINTS, f"{key}_{tag}.jpg"), facecolor=PAPER, dpi=300)
            plt.close(fig)
    zpath = os.path.join(BASE, f"{SLUG}_prints.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for key in KEYS:
            for tag in RATIOS:
                z.write(os.path.join(PRINTS, f"{key}_{tag}.jpg"), f"{key}/{key}_{tag}.jpg")
        z.writestr("READ-ME.txt",
                   f"{SET_NAME} Poster Set - MathRelaxing\n"
                   f"6 scientific-plate prints, each in 5 aspect ratios (2:3, 3:4, 4:5, 5:7, ISO/A) at 300 DPI.\n"
                   "Every mark is computed from the mathematics - not AI, not clip art.\n"
                   "Personal use only; not for resale or redistribution.\n")
    print("prints + zip", f"{os.path.getsize(zpath)/1e6:.2f} MB")


def img_gallery():
    ths = [plate(k, dpi=120) for k in KEYS]
    tw = 380
    ths = [t.resize((tw, int(t.height * tw / t.width))) for t in ths]
    th = ths[0].height
    cols, rows = 3, 2
    pad, top = 28, 200
    W = cols * tw + pad * (cols + 1)
    H = top + rows * th + pad * (rows + 1)
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for i, t in enumerate(ths):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad); y = top + pad + r * (th + pad)
        im.paste(t, (x, y)); d.rectangle([x, y, x + tw - 1, y + th - 1], outline="#d8dcd4")
    tt = f"{SET_NAME} Poster Set"
    f = font(76); w = d.textlength(tt, font=f); d.text(((W - w) / 2, 55), tt, fill=INK, font=f)
    sub = "Set of 6 · scientific-plate art prints · 5 sizes each · 300 DPI"
    f2 = font(32); w2 = d.textlength(sub, font=f2); d.text(((W - w2) / 2, 145), sub, fill=ACC, font=f2)
    im.save(os.path.join(LST, "01_gallery.jpg"), quality=92); print("01 gallery")


def img_framed():
    """A gallery wall: three framed plates side by side."""
    picks = KEYS[:3]
    W, H = 2200, 1500
    wall = Image.new("RGB", (W, H), (216, 210, 200))
    ph = 1050
    xs = []
    cards = []
    for k in picks:
        p = plate(k, dpi=150)
        pw = int(p.width * ph / p.height)
        p = p.resize((pw, ph))
        mat, fr = 30, 16
        card = Image.new("RGB", (pw + 2*mat + 2*fr, ph + 2*mat + 2*fr), (32, 30, 27))
        inner = Image.new("RGB", (pw + 2*mat, ph + 2*mat), "#f7f6f2")
        inner.paste(p, (mat, mat)); card.paste(inner, (fr, fr))
        cards.append(card)
    gap = 60
    total = sum(c.width for c in cards) + gap * (len(cards) - 1)
    x = (W - total) // 2
    y = (H - cards[0].height) // 2
    for card in cards:
        sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([40, 46, 40 + card.width, 46 + card.height], fill=(40, 38, 34, 85))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        wall.paste(sh, (x - 40 + 12, y - 40 + 20), sh)
        wall.paste(card, (x, y))
        x += card.width + gap
    wall.save(os.path.join(LST, "02_framed.jpg"), quality=90); print("02 framed")


def img_closeups():
    picks = KEYS[:4]
    ths = [plate(k, dpi=170) for k in picks]
    tw = 560
    ths = [t.resize((tw, int(t.height * tw / t.width))) for t in ths]
    th = ths[0].height; pad = 22
    W = 2 * tw + pad * 3; H = 2 * th + pad * 3
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for i, t in enumerate(ths):
        r, c = divmod(i, 2)
        x = pad + c * (tw + pad); y = pad + r * (th + pad)
        im.paste(t, (x, y)); d.rectangle([x, y, x + tw - 1, y + th - 1], outline="#d8dcd4")
    im.save(os.path.join(LST, "03_closeups.jpg"), quality=92); print("03 closeups")


def img_included():
    fig = plt.figure(figsize=(12.8, 10.24), dpi=125); fig.patch.set_facecolor(PAPER)
    fig.text(0.5, 0.9, f"The {SET_NAME} Set — 6 prints", ha="center",
             fontproperties=SERIF, fontsize=27, color=INK)
    titles = [MOD.CONCEPTS[k]["title"].title() for k in KEYS]
    for i, t in enumerate(titles):
        r, c = divmod(i, 2)
        fig.text(0.1 + c * 0.5, 0.74 - r * 0.13, f"·  {t}", fontproperties=SERIF,
                 fontsize=18, color="#3a3733")
    fig.text(0.5, 0.16, "Each in 5 aspect ratios (2:3, 3:4, 4:5, 5:7, ISO/A) · 300 DPI",
             ha="center", fontproperties=SERIF, fontsize=15, color=ACC)
    fig.text(0.5, 0.09, "Instant digital download · print small or large · for personal use",
             ha="center", fontproperties=SERIF, fontsize=12, color=SUB)
    fig.savefig(os.path.join(LST, "04_included.jpg"), facecolor=PAPER); plt.close(fig)
    print("04 included")


def img_note():
    fig = plt.figure(figsize=(12.8, 10.24), dpi=125); fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.82, "DRAWN FROM THE REAL SCIENCE", ha="center", fontproperties=SERIF,
            fontsize=25, color=INK, weight="bold")
    lines = ["Every plate in this set is computed from the mathematics itself —",
             "the equations, solved and plotted.", "",
             "No stock images. No AI. No clip art.", "",
             "A coordinated gallery set for a classroom, office or study."]
    y = 0.66
    for t in lines:
        ax.text(0.5, y, t, ha="center", fontproperties=SERIF, fontsize=15,
                color=ACC if "No AI" in t else INK); y -= 0.075
    ax.text(0.5, 0.1, "M A T H R E L A X I N G", ha="center", fontproperties=SERIF,
            fontsize=13, color=ACC)
    fig.savefig(os.path.join(LST, "05_note.jpg"), facecolor=PAPER); plt.close(fig)
    print("05 note")


if __name__ == "__main__":
    build_prints()
    img_gallery(); img_framed(); img_closeups(); img_included(); img_note()
    print(f"DONE [{SET}] ->", BASE)
