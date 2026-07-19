"""
sticker_love.py — "All You Need Is LOVE" math sticker. Four equations whose
graphs spell L-O-V-E, typeset in Computer Modern. Clean square design that
reads at 3-4 inches (kiss-cut sticker). Transparent-ready white art on a soft
rounded card. Brand terracotta curves.

    python sticker_love.py
"""
import io
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from PIL import Image

plt.rcParams["mathtext.fontset"] = "cm"
SANS = font_manager.FontProperties(family="DejaVu Sans")
PAPER = "#faf7f1"; INK = "#20201e"; SUB = "#8a8478"; RED = "#b5493a"
HERE = os.path.dirname(os.path.abspath(__file__))

# the four letters: (equation, plotter(ax))  — each mini-graph draws a letter
def L(ax):
    x = np.linspace(0.32, 3.0, 300); ax.plot(x, 1 / x, color=RED, lw=2.6)
    ax.set_xlim(0, 3.1); ax.set_ylim(0, 3.1)


def O(ax):
    t = np.linspace(0, 2 * np.pi, 240)
    ax.plot(3 * np.cos(t), 3 * np.sin(t), color=RED, lw=2.6)
    ax.set_xlim(-3.4, 3.4); ax.set_ylim(-3.4, 3.4)


def V(ax):
    x = np.linspace(-1.5, 1.5, 200); ax.plot(x, np.abs(-2 * x), color=RED, lw=2.6)
    ax.set_xlim(-1.7, 1.7); ax.set_ylim(0, 3.1)


def E(ax):
    y = np.linspace(0, 3 * np.pi, 400)
    ax.plot(-3 * np.abs(np.sin(y)), y, color=RED, lw=2.6)
    ax.set_xlim(-3.4, 0.3); ax.set_ylim(0, 3 * np.pi)


ROWS = [
    (r"$y = \dfrac{1}{x}$", L),
    (r"$x^{2} + y^{2} = 9$", O),
    (r"$y = |\!-\!2x|$", V),
    (r"$x = -3\,|\sin y|$", E),
]


def render(W=6.0, dpi=300, card=True):
    fig = plt.figure(figsize=(W, W), dpi=dpi)
    fig.patch.set_alpha(0)                       # transparent outside the card
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    if card:
        ax.add_patch(FancyBboxPatch((0.045, 0.045), 0.91, 0.91,
                     boxstyle="round,pad=0.0,rounding_size=0.06",
                     facecolor=PAPER, edgecolor="#e7e0d4", lw=1.4))
    ax.text(0.5, 0.885, "ALL YOU NEED IS", ha="center", va="center",
            fontproperties=SANS, fontsize=W * 3.4, color=INK, weight="bold")
    # four rows: equation (left) + letter-graph (right)
    ys = [0.70, 0.545, 0.39, 0.235]
    for (eq, plotter), yc in zip(ROWS, ys):
        ax.text(0.30, yc, eq, ha="center", va="center", fontsize=W * 4.0, color=INK)
        gx, gw = 0.585, 0.20
        gax = fig.add_axes([gx, yc - 0.075, gw, 0.15]); gax.axis("off")
        gax.set_aspect("equal"); plotter(gax)
    return fig


def to_pil(fig, dpi=300):
    b = io.BytesIO(); fig.savefig(b, format="png", transparent=True, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGBA")


if __name__ == "__main__":
    im = to_pil(render(dpi=300))
    out = os.path.join(HERE, "out", "sticker")
    os.makedirs(out, exist_ok=True)
    im.save(os.path.join(out, "love_sticker.png"))
    # preview on a neutral background so the white card is visible
    bg = Image.new("RGBA", im.size, (140, 140, 146, 255)); bg.alpha_composite(im)
    p = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/sticker_love.png"
    bg.convert("RGB").save(p)
    print("saved", p, im.size)
