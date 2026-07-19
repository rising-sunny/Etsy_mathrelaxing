"""
sticker_pack.py — a coordinated pack of math stickers (kiss-cut). Same clean
soft-card style as the LOVE sticker: Computer-Modern math, brand terracotta
curves, no wordmark. Each design is computed from real mathematics.

Designs: love, euler, golden, pi, schrodinger, lorenz.

    python sticker_pack.py
"""
import io
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from scipy.integrate import odeint
from PIL import Image

import sticker_love

plt.rcParams["mathtext.fontset"] = "cm"
SANS = font_manager.FontProperties(family="DejaVu Sans")
PAPER = "#faf7f1"; INK = "#20201e"; SUB = "#8a8478"; RED = "#b5493a"
HERE = os.path.dirname(os.path.abspath(__file__))


def _fig(W=6.0, dpi=300):
    fig = plt.figure(figsize=(W, W), dpi=dpi); fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.045, 0.045), 0.91, 0.91,
                 boxstyle="round,pad=0.0,rounding_size=0.06",
                 facecolor=PAPER, edgecolor="#e7e0d4", lw=1.4))
    return fig, ax


def _inset(fig, cx, cy, w, h):
    a = fig.add_axes([cx - w / 2, cy - h / 2, w, h]); a.axis("off"); a.set_aspect("equal")
    return a


def _title(ax, s, W, y=0.87):
    ax.text(0.5, y, s, ha="center", va="center", fontproperties=SANS,
            fontsize=W * 2.1, color=INK, weight="bold")


def _cap(ax, s, W, y=0.15):
    ax.text(0.5, y, s, ha="center", va="center", fontproperties=SANS,
            fontsize=W * 1.35, color=SUB)


# ---- designs ----------------------------------------------------------------
def d_euler(fig, ax, W):
    _title(ax, "THE MOST BEAUTIFUL EQUATION", W, y=0.865)
    a = _inset(fig, 0.5, 0.60, 0.42, 0.42)
    th = np.linspace(0, np.pi, 160)
    a.add_patch(plt.Circle((0, 0), 1, fill=False, edgecolor=INK, lw=1.6))
    a.plot(np.cos(th), np.sin(th), color=RED, lw=3.0)
    a.plot([-1.4, 1.4], [0, 0], color=SUB, lw=0.8); a.plot([0, 0], [-1.4, 1.4], color=SUB, lw=0.8)
    for px, lab in [(1, "1"), (-1, "-1")]:
        a.scatter([px], [0], s=W * 2.2, color=INK, zorder=5)
    a.set_xlim(-1.5, 1.5); a.set_ylim(-1.5, 1.5)
    ax.text(0.5, 0.30, r"$e^{i\pi} + 1 = 0$", ha="center", va="center", fontsize=W * 5.2, color=INK)


def d_golden(fig, ax, W):
    _title(ax, "THE GOLDEN RATIO", W, y=0.865)
    a = _inset(fig, 0.5, 0.55, 0.56, 0.56)
    phi = (1 + 5 ** 0.5) / 2
    b = np.log(phi) / (np.pi / 2)
    th = np.linspace(0, 4.4 * np.pi, 1200)
    r = np.exp(b * th) * 0.02
    a.plot(r * np.cos(th), r * np.sin(th), color=RED, lw=3.0)
    m = np.max(np.abs(np.column_stack([r * np.cos(th), r * np.sin(th)])))
    a.set_xlim(-m, m); a.set_ylim(-m, m)
    ax.text(0.5, 0.185, r"$\varphi = 1.6180339\ldots$", ha="center", va="center",
            fontsize=W * 3.4, color=INK)


def d_pi(fig, ax, W):
    _title(ax, "π  DAY", W, y=0.865)
    a = _inset(fig, 0.5, 0.585, 0.40, 0.40)
    a.add_patch(plt.Circle((0, 0), 1, fill=False, edgecolor=RED, lw=3.0))
    a.plot([-1, 1], [0, 0], color=SUB, lw=1.0, ls=(0, (4, 3)))
    a.set_xlim(-1.25, 1.25); a.set_ylim(-1.25, 1.25)
    ax.text(0.5, 0.585, r"$\pi$", ha="center", va="center", fontsize=W * 7.5, color=INK)
    ax.text(0.5, 0.235, "3.14159 26535", ha="center", va="center", fontproperties=SANS,
            fontsize=W * 2.2, color=INK)
    ax.text(0.5, 0.16, "89793 23846 …", ha="center", va="center", fontproperties=SANS,
            fontsize=W * 1.7, color=SUB)


def d_schrodinger(fig, ax, W):
    _title(ax, "SCHRÖDINGER", W, y=0.865)
    ax.text(0.5, 0.60, r"$i\hbar\,\dfrac{\partial \psi}{\partial t} = \hat{H}\psi$",
            ha="center", va="center", fontsize=W * 5.0, color=INK)
    a = _inset(fig, 0.5, 0.28, 0.62, 0.20); a.set_aspect("auto")
    x = np.linspace(-4, 4, 500)
    env = np.exp(-x ** 2 / 4.5)
    a.plot(x, env * np.cos(4 * x), color=RED, lw=2.4)
    a.plot(x, env, color=SUB, lw=0.8, ls=(0, (3, 3))); a.plot(x, -env, color=SUB, lw=0.8, ls=(0, (3, 3)))
    a.set_xlim(-4.2, 4.2); a.set_ylim(-1.2, 1.2)


def d_lorenz(fig, ax, W):
    _title(ax, "THE BUTTERFLY EFFECT", W, y=0.865)
    a = _inset(fig, 0.5, 0.50, 0.72, 0.56); a.set_aspect("auto")

    def f(s, t):
        x, y, z = s
        return [10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z]
    t = np.linspace(0, 40, 9000)
    sol = odeint(f, [1.0, 1.0, 1.0], t)
    a.plot(sol[:, 0], sol[:, 2], color=RED, lw=0.5, alpha=0.9)
    a.axis("off")
    ax.text(0.5, 0.155, "a tiny change, a different world", ha="center", va="center",
            fontproperties=SANS, fontsize=W * 1.35, color=SUB)


DESIGNS = {"euler": d_euler, "golden": d_golden, "pi": d_pi,
           "schrodinger": d_schrodinger, "lorenz": d_lorenz}


def render(name, W=6.0, dpi=300):
    if name == "love":
        return sticker_love.render(W=W, dpi=dpi)
    fig, ax = _fig(W, dpi)
    DESIGNS[name](fig, ax, W)
    return fig


def to_pil(fig, dpi=300):
    b = io.BytesIO(); fig.savefig(b, format="png", transparent=True, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGBA")


ALL = ["love", "euler", "golden", "pi", "schrodinger", "lorenz"]

if __name__ == "__main__":
    out = os.path.join(HERE, "out", "sticker")
    os.makedirs(out, exist_ok=True)
    tiles = []
    for n in ALL:
        im = to_pil(render(n, dpi=300))
        im.save(os.path.join(out, f"{n}.png"))
        bg = Image.new("RGBA", im.size, (150, 150, 156, 255)); bg.alpha_composite(im)
        tiles.append(bg.convert("RGB"))
    tw = 460; tiles = [t.resize((tw, tw)) for t in tiles]
    pad = 14; cols = 3; rows = 2
    sheet = Image.new("RGB", (cols * tw + pad * (cols + 1), rows * tw + pad * (rows + 1)), "#5a5a60")
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet.paste(t, (pad + c * (tw + pad), pad + r * (tw + pad)))
    p = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/sticker_pack.png"
    sheet.save(p); print("saved", p, sheet.size)
