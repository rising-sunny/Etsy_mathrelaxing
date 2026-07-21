"""
make_lorenz_promo.py — square promo video for the Lorenz "Butterfly Effect"
sticker. The attractor traces itself out (the butterfly forming), then an end
card with the CTA. Matches the sticker's soft-card style.

    python make_lorenz_promo.py   ->  out/sticker/lorenz_promo.mp4
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from scipy.integrate import odeint

SANS = font_manager.FontProperties(family="DejaVu Sans")
PAPER = "#faf7f1"; INK = "#20201e"; SUB = "#8a8478"; RED = "#b5493a"
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24


def lorenz(s, t):
    x, y, z = s
    return [10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z]


T = np.linspace(0, 45, 11000)
SOL = odeint(lorenz, [1.0, 1.0, 1.0], T)
X, Z = SOL[:, 0], SOL[:, 2]

T_TITLE = 18
DRAW_START = 20
DRAW_FRAMES = 250
END_START = DRAW_START + DRAW_FRAMES + 8
N = END_START + 80


def build():
    W = 8.0
    fig = plt.figure(figsize=(W, W), dpi=135); fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.045, 0.045), 0.91, 0.91, boxstyle="round,pad=0,rounding_size=0.06",
                 facecolor=PAPER, edgecolor="#e7e0d4", lw=1.6))
    title = ax.text(0.5, 0.90, "THE BUTTERFLY EFFECT", ha="center", va="center", fontproperties=SANS,
                    fontsize=W * 2.6, color=INK, weight="bold", alpha=0)
    # attractor axes (centre)
    gax = fig.add_axes([0.10, 0.16, 0.80, 0.66]); gax.axis("off"); gax.set_aspect("auto")
    gax.set_xlim(X.min() - 2, X.max() + 2); gax.set_ylim(Z.min() - 2, Z.max() + 3)
    (line,) = gax.plot([], [], color=RED, lw=0.7, alpha=0.9)
    (head,) = gax.plot([], [], marker="o", ms=5, color="#8f2f22")
    end1 = ax.text(0.5, 0.135, "", ha="center", va="center", fontproperties=SANS, fontsize=W * 1.5, color=SUB, alpha=0)
    end2 = ax.text(0.5, 0.085, "", ha="center", va="center", fontproperties=SANS, fontsize=W * 1.7, color=RED, alpha=0)

    def frame(f):
        title.set_alpha(min(1, f / T_TITLE))
        prog = np.clip((f - DRAW_START) / DRAW_FRAMES, 0, 1)
        k = max(2, int(prog * len(X)))
        line.set_data(X[:k], Z[:k])
        if prog < 1:
            head.set_data([X[k - 1]], [Z[k - 1]])
        else:
            head.set_data([], [])
        if f >= END_START:
            a = np.clip((f - END_START) / 16, 0, 1)
            end1.set_text("a tiny change, a different world"); end1.set_alpha(a)
            end2.set_text("Shop it on Etsy  ·  MathRelaxing"); end2.set_alpha(a)
        return [title, line, head, end1, end2]

    anim = animation.FuncAnimation(fig, frame, frames=N, interval=1000 / FPS, blit=False)
    out = os.path.join(HERE, "out", "sticker", "lorenz_promo.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    writer = animation.FFMpegWriter(fps=FPS, bitrate=4000, codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
    anim.save(out, writer=writer, dpi=135)
    plt.close(fig)
    print("saved", out, f"({N} frames, {N/FPS:.1f}s)")
    return out


if __name__ == "__main__":
    build()
