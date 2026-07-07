"""
generate_receipt_banner.py — MathRelaxing's Etsy "receipt banner" (the small
760x100px image Etsy shows on the thank-you/receipt page after checkout).

Replaces the previous stock-photo-style purple texture with an on-brand
banner: dark navy background, a faint De Jong attractor (the same chaotic
math motif used in the DeJongAttractor print) rendered in gold as a subtle
watermark, the MathRelaxing logo, and the existing copy.

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
from matplotlib.colors import to_rgb

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "receipt_banner.png")

W_PX, H_PX = 760, 100
DPI = 100
W_IN, H_IN = W_PX / DPI, H_PX / DPI

BG = "#0d1120"

# ── De Jong attractor, low-res density field used as a faint watermark ─────
def dejong_field(nx=760, ny=100, n_points=90_000, warmup=40, iters=160, seed=11):
    a, b, c, d = 1.641, 1.902, 0.316, 1.525
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=n_points).astype(np.float32)
    y = rng.uniform(-1, 1, size=n_points).astype(np.float32)
    for _ in range(warmup):
        x, y = np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)
    xs = np.empty(n_points * iters, dtype=np.float32)
    ys = np.empty(n_points * iters, dtype=np.float32)
    for i in range(iters):
        x, y = np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)
        xs[i * n_points:(i + 1) * n_points] = x
        ys[i * n_points:(i + 1) * n_points] = y
    hist, _, _ = np.histogram2d(xs, ys, bins=(nx, ny),
                                 range=[[xs.min(), xs.max()], [ys.min(), ys.max()]])
    hist = hist.T
    hist = np.log1p(hist)
    hist /= hist.max()
    hist = hist ** 1.7  # suppress the faint haze, keep only the crisp filaments
    return hist


def build():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

    # faint gold attractor texture across the whole strip -- alpha-only field
    # (colour stays a flat GOLD, density only ever controls opacity) so it
    # reads as crisp fine filaments instead of a translucent brown wash.
    field = dejong_field()
    gold = np.array(to_rgb(brand.GOLD))
    rgba = np.zeros((*field.shape, 4))
    rgba[..., :3] = gold
    # fade the field out from left to right so it stays a backdrop behind the
    # logo and never competes with the text sitting on the right two-thirds
    fade = np.clip(1.0 - np.linspace(0, 1, field.shape[1]) * 1.35, 0, 1)
    rgba[..., 3] = np.clip(field * 0.95 * fade[None, :], 0, 1)
    ax.imshow(rgba, extent=(0, W_IN, 0, H_IN), origin="lower",
              zorder=1, aspect="auto")

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
