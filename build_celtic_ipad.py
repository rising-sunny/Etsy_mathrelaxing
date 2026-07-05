"""
build_celtic_ipad.py — Celtic Knot iPad Edition (thin config over the template)
=============================================================================
All the bundle assembly + branding lives in template_ipad_bundle.py / brand.py.
This file only supplies what is specific to Celtic Knot:
  • the design renderer (reused from generate_celtic_knots.py)
  • the Celtic Procreate palette
  • the two showcase PNGs (line-art + coloured), whose colouring logic is
    product-specific (fat coloured centreline under the black ribbon outlines).
"""

import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import brand
import generate_celtic_knots as gk
import template_ipad_bundle as tib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "ipad_celtic")
PNG_DIR = os.path.join(OUT, "_png")
os.makedirs(PNG_DIR, exist_ok=True)

CELTIC_FILLS = ["#2e6b4f", "#3f8f6b", "#2f7d7b", "#c9a24b", "#b9762f",
                "#9c3b2e", "#6b4a8a", "#31597f"]

PALETTE = [
    "#0b3d2e", "#14563d", "#2e6b4f", "#3f8f6b", "#6bb191", "#a9d6bf",
    "#1f5c5a", "#2f7d7b", "#59a6a1", "#0d2b45", "#25507a", "#4f7fae",
    "#7aa7cf", "#3c2a52", "#5d4581", "#8f74b0", "#7a1f2b", "#a83c33",
    "#c76a3a", "#e0a15a", "#c9a24b", "#e6cf7e", "#4a3520", "#6e4b28",
    "#8a5a2b", "#b98a4e", "#2b2b2b", "#5a5a5a", "#d9cbb2", "#f2e9da",
]

CFG = tib.BundleConfig(
    out_dir=OUT,
    prefix="CelticKnot",
    edition="Celtic Knot Mathematics",
    subtitle_line="Celtic Knot Mathematics   ·   50 Woven Interlace Designs",
    design_word="woven bands",
    palette_name="MathRelaxing — Celtic Knot",
    palette_hexes=PALETTE,
    n_designs=50,
    included=[
        "50 unique woven Celtic knot designs",
        "Hyperlinked PDF index for GoodNotes & Notability",
        "50 transparent PNGs (300 dpi) for Procreate",
        "Procreate palette  ·  30 curated swatches",
        "'How to use on iPad' quick guide",
        "Instant download  ·  personal use",
    ],
)


# ── product-specific coloured showcase (fat colour fill under black ribbons) ──
def _draw_colored_symmetric(ax, x0, y0, w, h, rows, cols, seed, cross_prob=0.42):
    cell = min(w / cols, h / rows)
    ox = x0 + (w - cell * cols) / 2
    oy = y0 + (h - cell * rows) / 2
    band = cell * gk.BAND_RATIO
    flw = 1.85 * band * 72.0
    base = {}
    for i in range(rows):
        for j in range(cols):
            ci, cj = min(i, rows - 1 - i), min(j, cols - 1 - j)
            if (ci, cj) not in base:
                base[(ci, cj)] = (
                    gk._pick_tile(random.Random(seed + ci * 131 + cj * 17), cross_prob),
                    CELTIC_FILLS[(ci * 3 + cj * 5) % len(CELTIC_FILLS)])
            t, fill = base[(ci, cj)]
            if (i != ci) ^ (j != cj):
                t = gk._MIRROR[t]
            cxL, cxR = ox + j * cell, ox + (j + 1) * cell
            cyB, cyT = oy + i * cell, oy + (i + 1) * cell
            R = cell / 2
            if t == 0:
                gk._add_arc(ax, (cxL, cyT), cell, cell, 0, 270, 360, flw, fill, zorder=1)
                gk._add_arc(ax, (cxR, cyB), cell, cell, 0, 90, 180, flw, fill, zorder=1)
            elif t == 1:
                gk._add_arc(ax, (cxR, cyT), cell, cell, 0, 180, 270, flw, fill, zorder=1)
                gk._add_arc(ax, (cxL, cyB), cell, cell, 0, 0, 90, flw, fill, zorder=1)
            else:
                mx, my = (cxL + cxR) / 2, (cyB + cyT) / 2
                brk = band + cell * 0.11
                if (i + j) % 2 == 0:
                    gk._add_line(ax, (mx, cyB), (mx, cyT), flw, fill, zorder=1)
                    gk._add_line(ax, (cxL, my), (mx - brk, my), flw, fill, zorder=1)
                    gk._add_line(ax, (mx + brk, my), (cxR, my), flw, fill, zorder=1)
                else:
                    gk._add_line(ax, (cxL, my), (cxR, my), flw, fill, zorder=1)
                    gk._add_line(ax, (mx, cyB), (mx, my - brk), flw, fill, zorder=1)
                    gk._add_line(ax, (mx, my + brk), (mx, cyT), flw, fill, zorder=1)
            gk._emit_tile(ax, t, cxL, cxR, cyB, cyT, i, j, 1.6, "black", zorder=3)


def render_showcase(colored, path, size_in=6.0, seed=1210, rows=10, cols=10):
    fig = plt.figure(figsize=(size_in, size_in))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, size_in); ax.set_ylim(0, size_in); ax.set_aspect("equal")
    m = 0.35
    if colored:
        _draw_colored_symmetric(ax, m, m, size_in - 2 * m, size_in - 2 * m, rows, cols, seed)
    else:
        gk.draw_symmetric_knot(ax, m, m, size_in - 2 * m, size_in - 2 * m,
                                rows=rows, cols=cols, seed=seed, cross_prob=0.42, lw=1.6)
    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)


def main():
    line_png = os.path.join(PNG_DIR, "_showcase_line.png")
    colored_png = os.path.join(PNG_DIR, "_showcase_colored.png")
    render_showcase(False, line_png)
    render_showcase(True, colored_png)
    tib.build(CFG, gk.render_design, line_png, colored_png)


if __name__ == "__main__":
    main()
