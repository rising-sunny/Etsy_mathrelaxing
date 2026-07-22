"""
build_listing.py — Etsy listing photos for the Geometric Color-by-Number book,
in the MathRelaxing look (indigo theme, gold serif, infinity footer). Run after
build_package.py (reads the per-page images it left in pkg_out/).

  -> pkg_out/listing/listing_1_hero.jpg ... listing_6_included.jpg
"""
import os
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyArrowPatch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand
import art_gallery

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pkg_out")
LST = os.path.join(OUT, "listing")
THEME = "#181a2f"
CROP = (150, 340, 2400, 2590)            # clean 2250² mosaic region of a page


def _fig():
    fig = plt.figure(figsize=(10, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    fig.patch.set_facecolor(THEME); ax.set_facecolor(THEME)
    return fig, ax


def _art(key, kind="colored"):
    im = mpimg.imread(os.path.join(OUT, f"src_{key}_{kind}.png"))
    return im[CROP[1]:CROP[3], CROP[0]:CROP[2]]


def _save(fig, name):
    fig.savefig(os.path.join(LST, name), dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(name)


def hero():
    # reuse the square cover, upscaled
    sq = brand.cover(THEME, __import__("build_package").emblem, "GEOMETRIC",
                     "Color by Number", "A Coloring Book of Generative Math Art",
                     "20 Generative Art Designs", square=True)
    sq.savefig(os.path.join(LST, "listing_1_hero.jpg"), dpi=250, facecolor=THEME)
    plt.close(sq); print("listing_1_hero.jpg")


def grid(keys):
    fig, ax = _fig()
    ax.text(5, 9.55, "20 Generative Art Designs", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 9.0, "domain colourings · Newton fractals · Julia sets", ha="center",
            fontsize=15, color=brand.GOLD, **brand.SERIF)
    cols, rows = 5, 4
    x0, x1, y0, y1 = 0.5, 9.5, 1.7, 8.6
    cw = (x1 - x0) / cols; ch = (y1 - y0) / rows
    for i, k in enumerate(keys[:cols * rows]):
        r, c = divmod(i, cols)
        cx = x0 + c * cw + cw / 2
        cy = y1 - (r * ch + ch / 2)
        s = min(cw, ch) * 0.44
        ax.imshow(_art(k), extent=(cx - s, cx + s, cy - s, cy + s), zorder=3)
    brand.footer_band(ax, 10, 1.3)
    _save(fig, "listing_2_grid.jpg")


def sample(key, kind, heading, sub, name):
    fig, ax = _fig()
    ax.text(5, 9.4, heading, ha="center", fontsize=32, color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.85, sub, ha="center", fontsize=15, color=brand.GOLD, **brand.SERIF)
    ax.imshow(_art(key, kind), extent=(1.7, 8.3, 1.7, 8.3), zorder=3)
    ax.add_patch(plt.Rectangle((1.7, 1.7), 6.6, 6.6, fill=False, edgecolor=brand.GOLD, lw=1.5, zorder=4))
    brand.footer_band(ax, 10, 1.3)
    _save(fig, name)


def before_after(key):
    fig, ax = _fig()
    ax.text(5, 9.4, "Color by the Numbers", ha="center", fontsize=32,
            color=brand.CREAM, **brand.SERIF_BOLD)
    ax.imshow(_art(key, "coloring"), extent=(0.6, 4.4, 3.4, 7.2), zorder=3)
    ax.imshow(_art(key, "colored"), extent=(5.6, 9.4, 3.4, 7.2), zorder=3)
    ax.text(2.5, 3.05, "numbered page", ha="center", fontsize=13, color=brand.GOLD, **brand.SERIF)
    ax.text(7.5, 3.05, "your finished art", ha="center", fontsize=13, color=brand.GOLD, **brand.SERIF)
    ax.add_patch(FancyArrowPatch((4.55, 5.3), (5.45, 5.3), arrowstyle="-|>",
                 mutation_scale=26, color=brand.CREAM, lw=2.5, zorder=5))
    brand.footer_band(ax, 10, 1.3)
    _save(fig, "listing_5_beforeafter.jpg")


def included():
    fig, ax = _fig()
    ax.text(5, 9.2, "What's Included", ha="center", fontsize=34, color=brand.CREAM, **brand.SERIF_BOLD)
    items = [
        "20 low-poly color-by-number pages",
        "20 full-colour solution pages",
        '"The Mathematics" & "How to Color" guides',
        "US Letter, 300 dpi print-ready PDF",
        "Instant digital download — print at home",
        "Original generative math art (fractals & complex maps)",
    ]
    y = 7.7
    for it in items:
        ax.text(1.4, y, "◆", ha="left", fontsize=15, color=brand.GOLD, **brand.SERIF)
        ax.text(2.0, y, it, ha="left", fontsize=17, color=brand.CREAM, **brand.SERIF)
        y -= 0.92
    brand.footer_band(ax, 10, 1.3)
    _save(fig, "listing_6_included.jpg")


if __name__ == "__main__":
    os.makedirs(LST, exist_ok=True)
    keys = [m["key"] for m in art_gallery.build_all(os.path.join(HERE, "pkg_src"))]
    hero()
    grid(keys)
    sample("newton5", "colored", "Full-Colour Solutions", "every design solved for you", "listing_3_solution.jpg")
    sample("hexafoil", "coloring", "20 Pages to Color", "one number per facet — just fill them in", "listing_4_coloring.jpg")
    before_after("julia_dendrite")
    included()
    print("listing images ->", LST)
