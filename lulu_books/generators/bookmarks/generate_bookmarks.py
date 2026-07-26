"""Exclusive vertical bookmark designs for MathRelaxing — composed for the tall
2x6 in format (not crops of the book plates). Same identity as the art book:
black/cream backgrounds, gold accents, Cinzel/Raleway type, CM mathtext, ∞ logo.

Trim 2x6 in + 0.125 bleed -> 2.25 x 6.25 in @ 300 DPI = 675 x 1875 px.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "math_gallery"))
import mini_book as MB

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")

DPI = 300
TRIMW, TRIMH = 2.0, 6.0
BLEED = 0.125
W_IN, H_IN = TRIMW + 2 * BLEED, TRIMH + 2 * BLEED       # 2.25 x 6.25
PAPER, INK, SUB, ACC, DARK, GOLD = MB.PAPER, MB.INK, MB.SUB, MB.ACC, MB.DARK, MB.GOLD
CMAP = MB.CMAP
CINZEL, CINZEL_R, RALEWAY, RALEWAY_I = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I


def grad(ax, x, y, cmap=CMAP, lw=1.2, alpha=1.0):
    x = np.asarray(x, float); y = np.asarray(y, float)
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    good = ~np.isnan(segs).any(axis=(1, 2))       # drop segments touching a gap
    segs = segs[good]
    lc = LineCollection(segs, cmap=cmap, linewidth=lw, alpha=alpha)
    lc.set_array(np.linspace(0, 1, len(segs)))
    ax.add_collection(lc)
    ax.set_xlim(np.nanmin(x), np.nanmax(x)); ax.set_ylim(np.nanmin(y), np.nanmax(y))


# ── art motifs (each fills its art axes; framed for a tall box) ───────────────
def a_golden(ax):
    th = np.linspace(0, 6.3 * np.pi, 5000)
    r = np.exp(0.152 * th)
    x, y = r * np.cos(th), r * np.sin(th)
    grad(ax, x, y, lw=1.9)
    ax.set_aspect("equal")


def a_lemniscate(ax):
    th = np.linspace(0, 2 * np.pi, 4000)
    c = np.cos(2 * th)
    m = c >= 0
    r = np.sqrt(np.where(m, c, 0))
    x, y = r * np.cos(th), r * np.sin(th)
    x[~m] = np.nan; y[~m] = np.nan
    grad(ax, x, y, lw=1.8)
    ax.set_aspect("equal")


def a_heart(ax):
    t = np.linspace(0, 2 * np.pi, 3000)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    grad(ax, x, y, lw=1.9)
    ax.set_aspect("equal")


def a_phyllotaxis(ax):
    n = np.arange(1, 620)
    a = np.deg2rad(137.507)
    r = np.sqrt(n)
    x, y = r * np.cos(n * a), r * np.sin(n * a)
    ax.scatter(x, y, c=n, cmap=CMAP, s=6.5, linewidths=0)
    ax.set_aspect("equal")


def a_wave(ax):
    x = np.linspace(-1, 1, 800)
    N = 11
    cols = CMAP(np.linspace(0, 1, N))
    for i in range(N):
        yc = np.linspace(-0.92, 0.92, N)[i]
        k = 2 + i * 0.55
        y = yc + 0.075 * np.sin(k * np.pi * x + i * 0.7)
        ax.plot(x, y, color=cols[i], lw=1.5)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.set_aspect("auto")


def a_rose(ax):
    k = 7 / 1
    th = np.linspace(0, 2 * np.pi, 6000)
    r = np.cos(k * th)
    x, y = r * np.cos(th), r * np.sin(th)
    grad(ax, x, y, lw=1.0)
    ax.set_aspect("equal")


def a_harmono(ax):
    t = np.linspace(0, 70, 30000)
    d = np.exp(-0.007 * t)
    x = d * (np.sin(2.01 * t + 0.3) + 0.6 * np.sin(5.98 * t))
    y = d * (np.sin(1.49 * t) + 0.7 * np.sin(3.99 * t + 1.1))
    grad(ax, x, y, lw=0.7)
    ax.set_aspect("equal")


def a_lissajous(ax):
    t = np.linspace(0, 2 * np.pi, 4000)
    x = np.sin(3 * t + np.pi / 2)
    y = np.sin(4 * t)
    grad(ax, x, y, lw=1.3)
    ax.set_aspect("equal")


def a_butterfly(ax):
    t = np.linspace(0, 12 * np.pi, 8000)
    r = np.exp(np.sin(t)) - 2 * np.cos(4 * t) + np.sin((2 * t - np.pi) / 24) ** 5
    x, y = r * np.sin(t), r * np.cos(t)
    grad(ax, x, y, lw=0.9)
    ax.set_aspect("equal")


def a_euler(ax):
    th = np.linspace(0, 2 * np.pi, 2000)
    ax.plot(np.cos(th), np.sin(th), color=GOLD, lw=1.4)
    # radius sweeping to e^{i pi} = -1
    sp = np.linspace(0, np.pi, 400)
    grad(ax, 0.995 * np.cos(sp), 0.995 * np.sin(sp), lw=3.0)
    ax.scatter([-1, 1], [0, 0], s=14, color=[GOLD, "#e76f51"], zorder=5)
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal")


DESIGNS = [
    ("golden",   "The Golden Spiral",   r"$r = a\,e^{b\theta}$",         "cream", a_golden,     "growth, self-similar"),
    ("rose",     "The Rose Curve",      r"$r = \cos(k\theta)$",          "dark",  a_rose,       "petals from an angle"),
    ("euler",    "Euler's Identity",    r"$e^{i\pi} + 1 = 0$",           "dark",  a_euler,      "the most beautiful equation"),
    ("lissajous","The Lissajous Figure",r"$x=\sin at,\ \ y=\sin bt$",    "cream", a_lissajous,  "two oscillations"),
    ("harmono",  "The Harmonograph",    r"$x = e^{-dt}\sin(\omega t)$",  "dark",  a_harmono,    "a pendulum's song"),
    ("butterfly","The Butterfly Curve", r"$r = e^{\sin t} - 2\cos 4t$",  "cream", a_butterfly,  "Fay's transcendental"),
    ("lemniscate","The Lemniscate",     r"$r^{2} = a^{2}\cos 2\theta$",  "dark",  a_lemniscate, "the sign of infinity"),
    ("heart",    "The Heart Curve",     r"$x = 16\sin^{3} t$",           "cream", a_heart,      "mathematics, with love"),
    ("phyllotaxis","Phyllotaxis",       r"$\theta = n\cdot 137.5^{\circ}$","dark",a_phyllotaxis,"the sunflower's angle"),
    ("wave",     "The Standing Wave",   r"$y = \sin(n\pi x)$",           "cream", a_wave,       "harmonics in a string"),
]


def build_one(key, title, eq, theme, art, tagline):
    dark = theme == "dark"
    bg = DARK if dark else PAPER
    fg = "#f0e9da" if dark else INK
    subc = "#b9b3a4" if dark else SUB
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    fig.patch.set_facecolor(bg)
    base = fig.add_axes([0, 0, 1, 1]); base.set_facecolor(bg); base.axis("off")
    base.set_xlim(0, 1); base.set_ylim(0, 1)

    # art box (tall, upper portion)
    ax = fig.add_axes([0.11, 0.345, 0.78, 0.585]); ax.axis("off")
    art(ax)

    cx = 0.5
    # gold rule under the art
    base.plot([cx - 0.24, cx + 0.24], [0.305, 0.305], color=GOLD, lw=1.2)
    ts = 13.5 * min(1.0, 15.5 / len(title))       # auto-fit long titles to width
    base.text(cx, 0.255, title, fontproperties=CINZEL, fontsize=ts, color=fg,
              ha="center", va="center")
    base.text(cx, 0.195, eq, fontsize=15, color=GOLD, ha="center", va="center")
    base.text(cx, 0.145, tagline, fontproperties=RALEWAY_I, fontsize=8.5, color=subc,
              ha="center", va="center")
    base.plot([cx - 0.10, cx + 0.10], [0.108, 0.108], color=GOLD, lw=0.7, alpha=0.7)

    png = os.path.join(OUT, f"bm_{key}.png")
    fig.savefig(png, dpi=DPI, facecolor=bg)
    plt.close(fig)

    # ∞ logo as the sole, discreet signature (mode B — no wordmark)
    im = Image.open(png).convert("RGB")
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.crop((0, 0, logo.width, int(logo.height * 0.76)))
    lw = int(im.width * 0.135); lh = int(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
    lx = im.width // 2 - lw // 2
    ly = int(im.height * (1 - 0.052)) - lh // 2
    im.paste(logo, (lx, ly), logo.split()[3])
    im.save(png)
    return png


def build_all():
    paths = []
    for d in DESIGNS:
        p = build_one(*d)
        print("  ", os.path.basename(p))
        paths.append(p)
    return paths


def contact(paths):
    ims = [Image.open(p) for p in paths]
    w, h = ims[0].size
    pad = 40
    C = Image.new("RGB", (len(ims) * w + (len(ims) + 1) * pad, h + 2 * pad), (228, 224, 216))
    for i, im in enumerate(ims):
        C.paste(im, (pad + i * (w + pad), pad))
    cp = os.path.join(OUT, "contact.jpg")
    C.save(cp, quality=90)
    return cp


if __name__ == "__main__":
    ps = build_all()
    print(contact(ps))
