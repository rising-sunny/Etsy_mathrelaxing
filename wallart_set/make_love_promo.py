"""
make_love_promo.py — a short square promo video for the LOVE math sticker.
The four equations fade in one by one and their graphs draw themselves,
spelling L-O-V-E, then an end card with the shop CTA.

    python make_love_promo.py   ->  out/sticker/love_promo.mp4
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

plt.rcParams["mathtext.fontset"] = "cm"
SANS = font_manager.FontProperties(family="DejaVu Sans")
PAPER = "#faf7f1"; INK = "#20201e"; SUB = "#8a8478"; RED = "#b5493a"
HERE = os.path.dirname(os.path.abspath(__file__))

FPS = 24
# full curves (x, y) for each letter, in draw order
xL = np.linspace(0.32, 3.0, 260); L = (xL, 1 / xL, (0, 3.1), (0, 3.1))
tO = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 240); O = (3 * np.cos(tO), 3 * np.sin(tO), (-3.4, 3.4), (-3.4, 3.4))
xV = np.linspace(-1.5, 1.5, 200); V = (xV, np.abs(-2 * xV), (-1.7, 1.7), (0, 3.1))
yE = np.linspace(0, 3 * np.pi, 360); E = (-3 * np.abs(np.sin(yE)), yE, (-3.4, 0.3), (0, 3 * np.pi))
CURVES = [L, O, V, E]
EQS = [r"$y = \dfrac{1}{x}$", r"$x^{2}+y^{2}=9$", r"$y = |\!-\!2x|$", r"$x = -3\,|\sin y|$"]
YS = [0.70, 0.545, 0.39, 0.235]

# timeline (frames)
T_TITLE = 18
L_START = 22
L_DRAW = 40          # frames to draw one letter
L_GAP = 52           # spacing between letters' starts
END_START = L_START + 4 * L_GAP + 10
N = END_START + 78


def build():
    W = 8.0
    fig = plt.figure(figsize=(W, W), dpi=135)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.045, 0.045), 0.91, 0.91, boxstyle="round,pad=0,rounding_size=0.06",
                 facecolor=PAPER, edgecolor="#e7e0d4", lw=1.6))
    title = ax.text(0.5, 0.885, "ALL YOU NEED IS", ha="center", va="center", fontproperties=SANS,
                    fontsize=W * 3.4, color=INK, weight="bold", alpha=0)
    eqtexts, lines, gaxes = [], [], []
    for (eq, yc, (xx, yy, xl, yl)) in zip(EQS, YS, CURVES):
        t = ax.text(0.30, yc, eq, ha="center", va="center", fontsize=W * 4.0, color=INK, alpha=0)
        eqtexts.append(t)
        gax = fig.add_axes([0.585 - 0.10, yc - 0.075, 0.20, 0.15]); gax.axis("off"); gax.set_aspect("equal")
        gax.set_xlim(*xl); gax.set_ylim(*yl)
        (ln,) = gax.plot([], [], color=RED, lw=3.0, solid_capstyle="round")
        lines.append(ln); gaxes.append(gax)
    end1 = ax.text(0.5, 0.13, "", ha="center", va="center", fontproperties=SANS, fontsize=W * 1.9, color=RED, alpha=0)

    def frame(f):
        title.set_alpha(min(1, f / T_TITLE))
        for i in range(4):
            s = L_START + i * L_GAP
            eqtexts[i].set_alpha(np.clip((f - s + 6) / 12, 0, 1))
            prog = np.clip((f - s) / L_DRAW, 0, 1)
            xx, yy = CURVES[i][0], CURVES[i][1]
            k = max(2, int(prog * len(xx)))
            lines[i].set_data(xx[:k], yy[:k])
        if f >= END_START:
            end1.set_text("Shop it on Etsy  ·  MathRelaxing")
            end1.set_alpha(np.clip((f - END_START) / 16, 0, 1))
        return [title, end1, *eqtexts, *lines]

    anim = animation.FuncAnimation(fig, frame, frames=N, interval=1000 / FPS, blit=False)
    out = os.path.join(HERE, "out", "sticker", "love_promo.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    writer = animation.FFMpegWriter(fps=FPS, bitrate=4000, codec="libx264",
                                    extra_args=["-pix_fmt", "yuv420p"])
    anim.save(out, writer=writer, dpi=135)
    plt.close(fig)
    print("saved", out, f"({N} frames, {N/FPS:.1f}s)")
    return out


if __name__ == "__main__":
    build()
