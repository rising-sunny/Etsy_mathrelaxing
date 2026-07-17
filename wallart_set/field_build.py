"""
field_build.py — deliverables + Etsy listing images for the premium physics
field plates (dark line). Renders the 6 fields in 5 aspect ratios @300 DPI,
builds per-field and set ZIPs, and the listing photos (dark aesthetic).

    python field_build.py
"""
import os
import zipfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import field_poster as fp

FIELDS = ["quantum", "blackhole", "relativity", "electromagnetism", "thermodynamics", "mechanics"]
SLUG = {"quantum": "QuantumMechanics", "blackhole": "BlackHoles", "relativity": "SpecialRelativity",
        "electromagnetism": "Electromagnetism", "thermodynamics": "Thermodynamics",
        "mechanics": "ClassicalMechanics"}
RATIOS = {"2x3": 2/3, "3x4": 3/4, "4x5": 4/5, "5x7": 5/7, "ISO": 1/np.sqrt(2)}
BASE_W = 10.0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "field")
BG, INK, SUB, ACC, LINE = fp.BG, fp.INK, fp.SUB, fp.ACC, fp.LINE
_SANS = font_manager.findfont(fp.SANS)
_MONO = font_manager.findfont(fp.MONO)


def font(path, sz):
    return ImageFont.truetype(path, sz)


def _title(f):
    return fp.FIELDS[f]["title"].title()


def prints_all():
    pdir = os.path.join(OUT, "prints"); os.makedirs(pdir, exist_ok=True)
    for f in FIELDS:
        for tag, a in RATIOS.items():
            fig = fp.render(f, BASE_W, BASE_W / a, dpi=300)
            fig.savefig(os.path.join(pdir, f"{f}_{tag}.jpg"), facecolor=BG, dpi=300)
            plt.close(fig)
        print("  prints", f)
    return pdir


def zip_field(f, pdir):
    fdir = os.path.join(OUT, f); os.makedirs(fdir, exist_ok=True)
    z = os.path.join(fdir, f"{SLUG[f]}_prints.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zz:
        for tag in RATIOS:
            zz.write(os.path.join(pdir, f"{f}_{tag}.jpg"), f"{SLUG[f]}_{tag}.jpg")
        zz.writestr("READ-ME.txt",
                    f"{_title(f)} — MathRelaxing field plate\n"
                    "5 aspect ratios (2:3, 3:4, 4:5, 5:7, ISO/A) at 300 DPI.\n"
                    "Every graphic is computed from the physics — not AI, not clip art.\n"
                    "Personal use only; not for resale or redistribution.\n")
    return z


def zip_set(pdir):
    sdir = os.path.join(OUT, "set"); os.makedirs(sdir, exist_ok=True)
    z = os.path.join(sdir, "PhysicsFieldCollection_prints.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zz:
        for f in FIELDS:
            for tag in RATIOS:
                zz.write(os.path.join(pdir, f"{f}_{tag}.jpg"), f"{f}/{SLUG[f]}_{tag}.jpg")
        zz.writestr("READ-ME.txt",
                    "PHYSICS FIELD COLLECTION — 6 plates, MathRelaxing\n"
                    "Quantum mechanics, black holes, special relativity, electromagnetism,\n"
                    "thermodynamics and classical mechanics. Each in 5 aspect ratios at 300 DPI.\n"
                    "Every graphic is computed from the physics — not AI, not clip art.\n")
    return z


def _plate(f, dpi=150):
    return fp.to_pil(fp.render(f, BASE_W, BASE_W / (4/5), dpi=dpi), dpi=dpi)


def hero(f, fdir):
    _plate(f, dpi=160).save(os.path.join(fdir, "01_hero.jpg"), quality=92)


def framed(f, fdir):
    plate = _plate(f, dpi=150)
    W, H = 2000, 1600
    wall = Image.new("RGB", (W, H), (152, 150, 156))       # cool gallery gray
    ph = 1230; pw = int(plate.width * ph / plate.height); plate = plate.resize((pw, ph))
    fr = 18
    card = Image.new("RGB", (pw + 2*fr, ph + 2*fr), (12, 12, 15))  # thin black frame
    card.paste(plate, (fr, fr))
    x = (W - card.width)//2; y = (H - card.height)//2
    sh = Image.new("RGBA", (card.width+80, card.height+80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 46, 40+card.width, 46+card.height], fill=(20, 20, 24, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    wall.paste(sh, (x-40+12, y-40+20), sh); wall.paste(card, (x, y))
    wall.save(os.path.join(fdir, "02_framed.jpg"), quality=90)


def detail(f, fdir):
    im = _plate(f, dpi=200); w, h = im.size
    im.crop((int(w*0.05), int(h*0.05), int(w*0.95), int(h*0.42))).save(
        os.path.join(fdir, "03_detail.jpg"), quality=92)


def _card(path, draw_fn):
    fig = plt.figure(figsize=(12.8, 10.24), dpi=125); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    draw_fn(ax); fig.savefig(path, facecolor=BG); plt.close(fig)


def sizes(f, fdir):
    def d(ax):
        ax.text(0.5, 0.9, "FIVE ASPECT RATIOS INCLUDED", ha="center", fontproperties=fp.SANS,
                fontsize=24, color=INK, weight="bold")
        ax.text(0.5, 0.83, "300 DPI  ·  print small or large", ha="center", fontproperties=fp.MONO,
                fontsize=13, color=ACC)
        labs = [("2:3", 2/3, "4×6 · 12×18 · 24×36"), ("3:4", 3/4, "9×12 · 18×24"),
                ("4:5", 4/5, "8×10 · 16×20"), ("5:7", 5/7, "5×7 · 15×21"),
                ("ISO/A", 1/np.sqrt(2), "A4 · A3 · A2")]
        for i, (lab, a, sz) in enumerate(labs):
            cx = 0.1 + i*0.2; w = 0.06; h = w/a
            ax.add_patch(plt.Rectangle((cx-w/2, 0.5-h/2), w, h, fill=False, edgecolor=INK, lw=1.6))
            ax.text(cx, 0.5+h/2+0.04, lab, ha="center", fontproperties=fp.MONO, fontsize=14, color=INK)
            ax.text(cx, 0.5-h/2-0.06, sz, ha="center", va="top", fontproperties=fp.SANS, fontsize=9.5, color=SUB)
        ax.text(0.5, 0.12, "Instant digital download  ·  for personal use", ha="center",
                fontproperties=fp.SANS, fontsize=12, color=SUB)
    _card(os.path.join(fdir, "04_sizes.jpg"), d)


def note(f, fdir):
    def d(ax):
        ax.text(0.5, 0.80, "DRAWN FROM THE REAL PHYSICS", ha="center", fontproperties=fp.SANS,
                fontsize=23, color=INK, weight="bold")
        lines = ["Every graphic on this plate is computed from the physics",
                 "itself — the equations, solved and plotted.", "",
                 "No stock images. No AI. No clip art.", "",
                 "A serious plate for a classroom, lab, office or study."]
        y = 0.64
        for t in lines:
            ax.text(0.5, y, t, ha="center", fontproperties=fp.SANS, fontsize=15,
                    color=ACC if "No AI" in t else INK); y -= 0.072
        ax.text(0.5, 0.1, "M A T H R E L A X I N G", ha="center", fontproperties=fp.MONO,
                fontsize=14, color=ACC)
    _card(os.path.join(fdir, "05_note.jpg"), d)


# --- set listing images ------------------------------------------------------
def set_gallery(sdir):
    ims = [_plate(f, dpi=95) for f in FIELDS]
    tw = 360; ims = [i.resize((tw, int(i.height * tw / i.width))) for i in ims]
    th = ims[0].height; pad, top = 28, 200
    W = 3*tw + pad*4; H = top + 2*th + pad*3
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for i, t in enumerate(ims):
        r, c = divmod(i, 3)
        x = pad + c*(tw+pad); y = top + pad + r*(th+pad)
        im.paste(t, (x, y)); d.rectangle([x, y, x+tw-1, y+th-1], outline=LINE)
    fb = font(_SANS, 74); tt = "Physics Field Collection"
    w = d.textlength(tt, font=fb); d.text(((W-w)/2, 58), tt, fill=INK, font=fb)
    fs = font(_MONO, 30); sub = "6 field plates · scientific art prints · 5 sizes each · 300 DPI"
    w2 = d.textlength(sub, font=fs); d.text(((W-w2)/2, 150), sub, fill=ACC, font=fs)
    im.save(os.path.join(sdir, "01_gallery.jpg"), quality=92)


def set_framed(sdir):
    picks = ["quantum", "blackhole", "mechanics"]
    W, H = 2200, 1500
    wall = Image.new("RGB", (W, H), (152, 150, 156))
    cards = []
    ph = 1080
    for f in picks:
        p = _plate(f, dpi=150); pw = int(p.width * ph / p.height); p = p.resize((pw, ph))
        fr = 15; card = Image.new("RGB", (pw+2*fr, ph+2*fr), (12, 12, 15)); card.paste(p, (fr, fr))
        cards.append(card)
    gap = 60; total = sum(c.width for c in cards) + gap*(len(cards)-1)
    x = (W-total)//2; y = (H-cards[0].height)//2
    for card in cards:
        sh = Image.new("RGBA", (card.width+80, card.height+80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([40, 48, 40+card.width, 48+card.height], fill=(20, 20, 24, 105))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        wall.paste(sh, (x-40+12, y-40+22), sh); wall.paste(card, (x, y)); x += card.width + gap
    wall.save(os.path.join(sdir, "02_framed.jpg"), quality=90)


def set_included(sdir):
    def d(ax):
        ax.text(0.5, 0.9, "The Collection — 6 field plates", ha="center",
                fontproperties=fp.SANS, fontsize=26, color=INK, weight="bold")
        for i, f in enumerate(FIELDS):
            r, c = divmod(i, 2)
            ax.text(0.1 + c*0.5, 0.74 - r*0.13, f"·  {_title(f)}", fontproperties=fp.SANS,
                    fontsize=18, color=INK)
        ax.text(0.5, 0.16, "Each in 5 aspect ratios (2:3, 3:4, 4:5, 5:7, ISO/A) · 300 DPI",
                ha="center", fontproperties=fp.MONO, fontsize=14, color=ACC)
        ax.text(0.5, 0.09, "Instant digital download · print small or large · for personal use",
                ha="center", fontproperties=fp.SANS, fontsize=12, color=SUB)
    _card(os.path.join(sdir, "03_included.jpg"), d)


if __name__ == "__main__":
    print("prints:"); pdir = prints_all()
    print("zips + per-field listing:")
    for f in FIELDS:
        zip_field(f, pdir)
        fdir = os.path.join(OUT, f, "listing"); os.makedirs(fdir, exist_ok=True)
        hero(f, fdir); framed(f, fdir); detail(f, fdir); sizes(f, fdir); note(f, fdir)
        print("  listing", f)
    print("set:")
    sdir = os.path.join(OUT, "set"); os.makedirs(sdir, exist_ok=True)
    zip_set(pdir)
    lset = os.path.join(sdir, "listing"); os.makedirs(lset, exist_ok=True)
    set_gallery(lset); set_framed(lset); set_included(lset)
    sizes("set", lset); note("set", lset)
    print("DONE ->", OUT)
