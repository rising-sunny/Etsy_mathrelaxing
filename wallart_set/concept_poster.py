"""
concept_poster.py — "Mathematical Concept Posters": each poster is a real
scientific plate (a genuine diagram + data + a terse, human caption), not
decorative AI-style art. Deliberately technical typography (sans / mono) on a
pale lab-paper ground — the opposite of the cream+serif look that reads as AI.

First plate: the harmonic series (modes of a vibrating string). Layout is
proportional so it renders cleanly at any aspect ratio.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image
import io

SANS = font_manager.FontProperties(family="DejaVu Sans")
MONO = font_manager.FontProperties(family="DejaVu Sans Mono")

PAPER = "#eef0ec"
INK = "#1c1e1c"
SUB = "#5c625c"
ACC = "#9a5236"
GRIDC = "#dadfd9"

# fixed-inch margins (keep labels from clipping across ratios)
ML, MR, MT, MB = 1.75, 1.20, 1.45, 1.95

NAMES = ["fundamental", "2nd harmonic", "3rd harmonic", "4th harmonic",
         "5th harmonic", "6th harmonic", "7th harmonic", "8th harmonic"]
LAM = ["2L", "L", "2L/3", "L/2", "2L/5", "L/3", "2L/7", "L/4"]


def render_harmonic(W, H, dpi=110):
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(PAPER); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H)

    # faint engineering grid
    for gx in np.arange(0.5, W, 0.5):
        ax.plot([gx, gx], [0.4, H - 0.4], color=GRIDC, lw=0.4, zorder=0)
    for gy in np.arange(0.5, H, 0.5):
        ax.plot([0.4, W - 0.4], [gy, gy], color=GRIDC, lw=0.4, zorder=0)

    # header
    ax.text(ML - 1.1, H - 0.85, "MODES OF A VIBRATING STRING", fontproperties=SANS,
            fontsize=W * 2.25, color=INK, weight="bold")
    ax.text(ML - 1.1, H - 1.16, "THE HARMONIC SERIES   ·   1, 1/2, 1/3, 1/4, …",
            fontproperties=MONO, fontsize=W * 1.25, color=ACC)
    ax.text(W - MR + 0.5, H - 0.88, "FIG. 1", fontproperties=MONO, fontsize=W * 1.15,
            color=SUB, ha="right")
    ax.plot([ML - 1.1, W - MR + 0.5], [H - 1.34, H - 1.34], color=INK, lw=0.8)

    # body: eight modes stacked
    x = np.linspace(0, 1, 700)
    x0 = ML
    L = W - ML - MR
    top = H - MT - 0.35
    bot = MB + 0.25
    N = 8
    step = (top - bot) / (N - 1)
    A = step * 0.42
    for i in range(N):
        n = i + 1
        yb = top - i * step
        ax.plot([x0, x0 + L], [yb, yb], color=SUB, lw=0.5)
        ax.plot(x0 + x * L, yb + A * np.sin(n * np.pi * x), color=INK, lw=1.3)
        ax.plot(x0 + x * L, yb - A * np.sin(n * np.pi * x), color=INK, lw=1.3, alpha=0.32)
        nodes = np.arange(0, n + 1) / n
        ax.scatter(x0 + nodes * L, [yb] * len(nodes), s=W * 1.4, color=ACC, zorder=5)
        ax.text(x0 - 0.16, yb, f"{n}", fontproperties=MONO, fontsize=W * 1.5, color=INK,
                ha="right", va="center")
        ax.text(x0 - 0.42, yb, NAMES[i], fontproperties=SANS, fontsize=W * 0.95, color=SUB,
                ha="right", va="center")
        ax.text(x0 + L + 0.12, yb, f"λ = {LAM[i]}", fontproperties=MONO, fontsize=W * 1.05,
                color=SUB, va="center")

    # footer caption — human voice, one real fact
    note = ("A plucked string sounds all of these at once. Their wavelengths are L, L/2, L/3, …\n"
            "— the harmonic series. The sum 1 + 1/2 + 1/3 + … never settles: it passes every\n"
            "value, however slowly. Reaching a total of just 100 takes about 1.5 × 10⁴³ terms.")
    ax.plot([x0, W - MR + 0.5], [MB - 0.25, MB - 0.25], color=GRIDC, lw=0.8)
    ax.text(x0, MB - 0.5, note, fontproperties=SANS, fontsize=W * 1.05, color=INK,
            va="top", linespacing=1.6)
    ax.text(W - MR + 0.5, 0.42, "∑ 1/n  →  ∞", fontproperties=MONO, fontsize=W * 1.5,
            color=ACC, ha="right")
    return fig


def to_pil(fig, dpi=110):
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor=PAPER, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGB")


if __name__ == "__main__":
    # verify at two ratios
    for tag, (w, h) in {"4x5": (8, 10), "2x3": (8, 12)}.items():
        to_pil(render_harmonic(w, h)).save(
            f"/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/wallart/plate_{tag}.png")
    print("verify plates saved")
