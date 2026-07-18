"""
render_labeled_magnet.py — overlay the generating equation on a fractal magnet.
Makes the magnet read as "math art": the fractal + the exact formula that
produced it, set in Computer Modern (LaTeX). Reusable across the magnet series.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

matplotlib.rcParams["mathtext.fontset"] = "cm"

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = "#e7c977"
CREAM = "#f6efdd"

# design -> (source png, small-caps name, equation, constant line)
LABELS = {
    "Amethyst_Julia": dict(
        src="Amethyst_Julia_1800.png",
        name="J U L I A   S E T",
        eq=r"$z_{n+1} = z_n^{2} + c$",
        const=r"$c = 0.285 + 0.01\,i$"),
}


def render(key, out=None):
    spec = LABELS[key]
    img = Image.open(os.path.join(HERE, spec["src"])).convert("RGB")
    W, H = img.size
    dpi = 200
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.imshow(np.asarray(img), extent=(0, 1, 0, 1), aspect="auto")

    # soft dark gradient strip along the bottom for legibility (dark at y=0,
    # fading smoothly to fully clear at the top of the band -> no hard seam)
    grad = np.linspace(0, 1, 256)[:, None]        # row0=0 (top), row255=1 (bottom)
    band = np.zeros((256, 4, 4))
    band[..., 3] = grad * 0.62                     # alpha: clear on top, dark at base
    ax.imshow(band, extent=(0, 1, 0.0, 0.40), aspect="auto", zorder=2,
              interpolation="bilinear")

    ax.text(0.5, 0.185, spec["name"], color=GOLD, ha="center", va="center",
            fontsize=9.5, family="sans-serif", zorder=3)
    ax.text(0.5, 0.115, spec["eq"], color=CREAM, ha="center", va="center",
            fontsize=19, zorder=3)
    ax.text(0.5, 0.045, spec["const"], color=(0.85, 0.83, 0.90), ha="center", va="center",
            fontsize=11.5, zorder=3)

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    out = out or os.path.join(HERE, key + "_labeled.png")
    fig.savefig(out, dpi=dpi); plt.close(fig)
    print("saved", out)
    return out


if __name__ == "__main__":
    render("Amethyst_Julia")
