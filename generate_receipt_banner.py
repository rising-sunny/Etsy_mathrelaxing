"""
generate_receipt_banner.py — MathRelaxing's Etsy "receipt banner" (the small
760x100px image Etsy shows on the thank-you/receipt page after checkout).

Replaces the previous stock-photo-style purple texture with an on-brand
banner: dark navy background, a woven field of harmonic sine curves (a
motif drawn to fit THIS exact 7.6:1 wide strip, rather than a square
attractor squeezed into it) fading in gold behind the logo, and the
existing copy.

Usage:
  python generate_receipt_banner.py
Output:
  receipt_banner.png  (exactly 760x100px)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.collections as mcoll
from matplotlib.colors import to_rgb

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "receipt_banner.png")

W_PX, H_PX = 760, 100
DPI = 100
W_IN, H_IN = W_PX / DPI, H_PX / DPI

BG = "#0d1120"


# ── Harmonic weave: a handful of sine curves running the full width, each
# with its own frequency/amplitude/phase, drawn as LineCollections so each
# one can fade out (via a per-segment alpha) toward the right, where the
# logo/text sit. Built for THIS 7.6:1 strip -- x runs edge to edge, y stays
# a small fraction of the (short) banner height by construction. ─────────────
def harmonic_weave(n_curves=8, seed=5):
    rng = np.random.default_rng(seed)
    gold = np.array(to_rgb(brand.GOLD))
    t = np.linspace(0, W_IN, 500)
    collections = []
    for i in range(n_curves):
        freq = rng.uniform(1.3, 3.6)
        phase = rng.uniform(0, 2 * np.pi)
        amp = rng.uniform(0.08, 0.30) * H_IN
        centre = H_IN * rng.uniform(0.35, 0.65)
        lw = rng.uniform(0.6, 1.4)
        base_alpha = rng.uniform(0.22, 0.5)

        y = centre + amp * np.sin(2 * np.pi * freq * t / W_IN + phase)
        pts = np.array([t, y]).T.reshape(-1, 1, 2)
        segs = np.concatenate([pts[:-1], pts[1:]], axis=1)

        # fade from full strength on the left (behind/around the logo) to
        # ~0 by the time the text starts on the right
        fade = np.clip(1.0 - (t[:-1] / W_IN) * 1.5, 0, 1)
        colors = np.zeros((len(segs), 4))
        colors[:, :3] = gold
        colors[:, 3] = base_alpha * fade

        lc = mcoll.LineCollection(segs, colors=colors, linewidths=lw, zorder=1)
        collections.append(lc)
    return collections


def build():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

    for lc in harmonic_weave():
        ax.add_collection(lc)

    # thin gold rule near the bottom, brand-style separation
    ax.add_patch(plt.Rectangle((0, 0.06), W_IN, 0.022, color=brand.GOLD,
                                alpha=0.55, zorder=2))

    # logo, left side
    logo = mpimg.imread(brand.LOGO_PATH)
    lh = 0.62
    lw = lh * logo.shape[1] / logo.shape[0]
    cx, cy = 0.5 + lw / 2, H_IN / 2 + 0.03
    ax.imshow(logo, extent=(cx - lw / 2, cx + lw / 2, cy - lh / 2, cy + lh / 2),
              zorder=5)

    # copy, right of the logo
    text_x = cx + lw / 2 + 0.18
    ax.text(text_x, H_IN / 2 + 0.22, "Thank you for your order",
            ha="left", va="center", fontsize=14.5, color=brand.CREAM,
            zorder=5, **brand.SERIF_BOLD)
    ax.text(text_x, H_IN / 2 - 0.14,
            "Every design is generated with code — mathematics made visible",
            ha="left", va="center", fontsize=8.2, color=brand.GOLD,
            style="italic", zorder=5, **brand.SERIF)

    fig.savefig(OUT, dpi=DPI, facecolor=BG)
    plt.close(fig)
    print(f"Guardado: {OUT}")


if __name__ == "__main__":
    build()
