"""
build_mockups.py — listing images for the Etsy printable wall-art set:
  01 hero gallery wall (3x2 framed on a plaster wall)
  02 styled room scene (framed set over a console + plant)
  03 detail trio (three prints framed larger)
  04 what's included (6 designs, named)
  05 sizes & ratios chart
  06 how it works (instant download)
All output ~2000px JPGs into out/listing/.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter

import designs
from render import render
from designs import DESIGNS

PAL = os.environ.get("WALLART_PALETTE", "earth")
designs.use_palette(PAL)

HERE = os.path.dirname(os.path.abspath(__file__))
LST = os.path.join(HERE, "out", PAL, "listing")
os.makedirs(LST, exist_ok=True)

NAMES = ["maurer", "phyllotaxis", "hilbert", "cardioid", "euler", "fern"]
TITLES = {n: DESIGNS[n]["title"] for n in NAMES}
SUB = {
    "maurer": "Maurer rose · r = sin(6θ)",
    "phyllotaxis": "Golden angle · 137.5°",
    "hilbert": "Space-filling curve",
    "cardioid": "Modular circle · ×2",
    "euler": "Clothoid · Fresnel integrals",
    "fern": "Iterated function system",
}
WALL_TOP = (222, 214, 200)
WALL_BOT = (208, 199, 185)
SERIF = font_manager.FontProperties(family="DejaVu Serif")


def plaster(w, h):
    g = np.linspace(0, 1, h)[:, None]
    arr = np.zeros((h, w, 3), np.uint8)
    for i in range(3):
        arr[:, :, i] = (WALL_TOP[i] * (1 - g) + WALL_BOT[i] * g).astype(np.uint8)
    noise = (np.random.default_rng(3).normal(0, 2.2, (h, w, 1))).astype(np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def framed(name, print_h=900, frame_col=(38, 35, 31)):
    pw = int(print_h * 4 / 5)
    art = render(name, pw, print_h)
    mat = int(pw * 0.075)
    fr = int(pw * 0.02)
    mat_im = Image.new("RGB", (pw + 2 * mat, print_h + 2 * mat), "#faf6ec")
    mat_im.paste(art, (mat, mat))
    card = Image.new("RGB", (mat_im.width + 2 * fr, mat_im.height + 2 * fr), frame_col)
    card.paste(mat_im, (fr, fr))
    return card


def drop(canvas, card, x, y, blur=16, off=(16, 20), alpha=95):
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [40, 40, 40 + card.width, 40 + card.height], fill=(45, 38, 30, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(sh, (x - 40 + off[0], y - 40 + off[1]), sh)
    canvas.paste(card, (x, y))


def hero():
    cards = [framed(n, 880) for n in NAMES]
    cw, ch = cards[0].size
    gap, margin = 64, 150
    W = 3 * cw + 2 * gap + 2 * margin
    H = 2 * ch + gap + 2 * margin
    wall = plaster(W, H)
    for i, card in enumerate(cards):
        r, c = divmod(i, 3)
        x = margin + c * (cw + gap)
        y = margin + r * (ch + gap)
        drop(wall, card, x, y)
    wall.save(os.path.join(LST, "01_hero_gallery.jpg"), quality=90)
    print("01 hero", wall.size)


def room():
    W, H = 2200, 1650
    wall = plaster(W, H).convert("RGB")
    # floor band
    fl = int(H * 0.80)
    floor = Image.new("RGB", (W, H - fl), (196, 184, 166))
    wall.paste(floor, (0, fl))
    d = ImageDraw.Draw(wall)
    d.line([(0, fl), (W, fl)], fill=(180, 168, 150), width=3)
    # console table
    tx0, tx1, ty = int(W*0.30), int(W*0.70), fl
    d.rectangle([tx0, ty-14, tx1, ty-4], fill=(120, 96, 74))          # top
    d.rectangle([tx0+30, ty-4, tx0+50, H-40], fill=(120, 96, 74))     # legs
    d.rectangle([tx1-50, ty-4, tx1-30, H-40], fill=(120, 96, 74))
    # simple plant in a pot (left of console)
    px = tx0 - 70
    d.rectangle([px-38, ty-150, px+2, ty-14], fill=(150, 120, 96))    # pot
    rng = np.random.default_rng(5)
    for _ in range(26):
        ang = rng.uniform(-1.15, 1.15)
        ln = rng.uniform(120, 230)
        ex = px-18 + np.sin(ang)*ln
        ey = ty-150 - np.cos(ang)*ln
        d.line([(px-18, ty-150), (ex, ey)], fill=(126, 144, 112), width=4)
    # framed trio above console
    trio = ["cardioid", "phyllotaxis", "euler"]
    cards = [framed(n, 620) for n in trio]
    cw, ch = cards[0].size
    gap = 48
    total = 3*cw + 2*gap
    x0 = (W - total)//2
    y0 = int(H*0.16)
    for i, card in enumerate(cards):
        drop(wall, card, x0 + i*(cw+gap), y0, blur=20, off=(12, 18))
    wall.save(os.path.join(LST, "02_room.jpg"), quality=90)
    print("02 room", wall.size)


def detail_trio():
    trio = ["maurer", "fern", "hilbert"]
    cards = [framed(n, 1150) for n in trio]
    cw, ch = cards[0].size
    gap, margin = 70, 130
    W = 3*cw + 2*gap + 2*margin
    H = ch + 2*margin
    wall = plaster(W, H)
    for i, card in enumerate(cards):
        drop(wall, card, margin + i*(cw+gap), margin)
    wall.save(os.path.join(LST, "03_detail.jpg"), quality=90)
    print("03 detail", wall.size)


def included():
    fig = plt.figure(figsize=(16, 12), dpi=125)
    fig.patch.set_facecolor(designs.BG)
    fig.suptitle("Six original designs — drawn from real mathematics",
                 y=0.98, fontproperties=SERIF, fontsize=26, color="#3a3733")
    for i, n in enumerate(NAMES):
        ax = fig.add_subplot(2, 3, i + 1)
        ax.set_facecolor(designs.BG)
        ax.axis("off")
        ax.set_aspect("equal")
        xs, ys = DESIGNS[n]["fn"](ax, lw_scale=1.6)
        xs, ys = np.asarray(xs), np.asarray(ys)
        cx, cy = (xs.min()+xs.max())/2, (ys.min()+ys.max())/2
        hx = max((xs.max()-xs.min())/2, 1e-6)*1.2
        hy = max((ys.max()-ys.min())/2, 1e-6)*1.2
        hh = max(hy, hx/0.8); ww = hh*0.8
        ax.set_xlim(cx-ww, cx+ww); ax.set_ylim(cy-hh*1.18, cy+hh*1.18)
        ax.set_title(f"{TITLES[n]}\n{SUB[n]}", fontproperties=SERIF,
                     fontsize=14, color="#4a463f", pad=8, linespacing=1.4)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.85, bottom=0.03,
                        wspace=0.12, hspace=0.40)
    fig.savefig(os.path.join(LST, "04_included.jpg"), facecolor=designs.BG)
    plt.close(fig)
    print("04 included")


def sizes_chart():
    ratios = [
        ("2:3", 2/3, ["4×6", "8×12", "12×18", "16×24", "20×30", "24×36"]),
        ("3:4", 3/4, ["6×8", "9×12", "12×16", "18×24"]),
        ("4:5", 4/5, ["8×10", "16×20", "24×30"]),
        ("5:7", 5/7, ["5×7", "10×14", "15×21"]),
        ("ISO/A", 1/np.sqrt(2), ["A5", "A4", "A3", "A2", "A1"]),
    ]
    fig = plt.figure(figsize=(16, 11), dpi=125)
    fig.patch.set_facecolor(designs.BG)
    fig.suptitle("Five aspect ratios included — print almost any size",
                 y=0.95, fontproperties=SERIF, fontsize=25, color="#3a3733")
    fig.text(0.5, 0.885, "Each of the 6 designs comes in all five ratios · 300 DPI · inches",
             ha="center", fontproperties=SERIF, fontsize=14, color="#6b6458")
    for i, (lab, a, sizes) in enumerate(ratios):
        ax = fig.add_subplot(1, 5, i + 1)
        ax.set_facecolor(designs.BG); ax.axis("off"); ax.set_aspect("equal")
        w = a; h = 1.0
        ax.add_patch(plt.Rectangle((-w/2, -h/2), w, h, fill=False,
                     edgecolor=designs.accent(), lw=2.2))
        ax.text(0, 0.62, lab, ha="center", fontproperties=SERIF, fontsize=17,
                color="#4a463f")
        ax.text(0, -0.66, "\n".join(sizes), ha="center", va="top",
                fontproperties=SERIF, fontsize=12.5, color="#6b6458", linespacing=1.6)
        ax.set_xlim(-0.6, 0.6); ax.set_ylim(-1.15, 0.85)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.84, bottom=0.05)
    fig.savefig(os.path.join(LST, "05_sizes.jpg"), facecolor=designs.BG)
    plt.close(fig)
    print("05 sizes")


def how_it_works():
    fig = plt.figure(figsize=(16, 11), dpi=125)
    fig.patch.set_facecolor(designs.BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.text(0.5, 0.9, "How it works", ha="center", fontproperties=SERIF,
            fontsize=30, color="#3a3733")
    steps = [
        ("1", "Buy & download instantly", "No physical item is shipped — your files are ready the moment you check out."),
        ("2", "Pick your size & ratio", "Choose from five aspect ratios; each design is 300 DPI, ready to print."),
        ("3", "Print anywhere", "At home, a local print shop, or an online service like Printful or a photo lab."),
        ("4", "Frame & enjoy", "Trim to your frame and hang. Colours may vary slightly by screen & printer."),
    ]
    y = 0.72
    for num, head, body in steps:
        ax.add_patch(plt.Circle((0.12, y), 0.045, color=designs.accent()))
        ax.text(0.12, y, num, ha="center", va="center", color=designs.BG,
                fontproperties=SERIF, fontsize=22)
        ax.text(0.20, y+0.02, head, va="center", fontproperties=SERIF,
                fontsize=20, color="#3a3733")
        ax.text(0.20, y-0.055, body, va="center", fontproperties=SERIF,
                fontsize=14, color="#6b6458")
        y -= 0.17
    ax.text(0.5, 0.05, "Instant digital download · for personal use",
            ha="center", fontproperties=SERIF, fontsize=13, color="#8a8478")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.savefig(os.path.join(LST, "06_how.jpg"), facecolor=designs.BG)
    plt.close(fig)
    print("06 how")


if __name__ == "__main__":
    hero()
    room()
    detail_trio()
    included()
    sizes_chart()
    how_it_works()
    print("mockups done")
