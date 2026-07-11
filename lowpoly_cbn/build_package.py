"""
build_package.py — assemble the polished MathRelaxing color-by-number book,
styled to match the other coloring-book PDFs (brand.cover / brand.about_page:
dark themed cover with a gold emblem, serif "THE MATHEMATICS" intro, black
footer band + infinity logo, white interior design pages).

Book structure (all pages US-Letter portrait, 300 dpi):
  1  themed cover                    (brand.cover)
  2  THE MATHEMATICS  (intro)        (brand.about_page)
  3  HOW TO COLOR                    (house-style page)
  4..  N geometric color-by-number pages (one per generative-art piece)
  ..   SOLUTIONS divider + N full-colour solutions
  last back cover                    (house-style dark page)

Also writes a square listing cover JPG and design preview JPGs.

    python build_package.py     # -> pkg_out/MathColorByNumber_Vol1.pdf (+ jpg previews)
"""
import io
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from PIL import Image

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

import art_gallery
from lowpoly_core import generate_cbn, LETTER_PX

HERE = os.path.dirname(os.path.abspath(__file__))
THEME = "#181a2f"          # deep indigo — complements the rainbow art
TITLE = "GEOMETRIC"
SUBTITLE = "Color by Number"
TAGLINE = "A Coloring Book of Generative Math Art"

ABOUT = (
    "Every design in this book is a piece of mathematics rendered in colour.\n\n"
    "The smooth rainbow pages are domain colourings of complex functions: at each\n"
    "point of the plane the function's phase becomes a hue and its magnitude a\n"
    "brightness, so the zeros and poles bloom into petals and whirlpools.\n\n"
    "The sharp-edged pages are Newton fractals — the basins of attraction of\n"
    "Newton's root-finding method. Points are coloured by which root they fall\n"
    "into, and the border between basins is infinitely intricate.\n\n"
    "Each image is then broken into a low-poly triangular mosaic and numbered, so\n"
    "colouring it rebuilds the original mathematical artwork facet by facet."
)

HOWTO_STEPS = [
    ("1.  Read the key", "Every number in the COLOR KEY maps to one colour. Use pencils,"
     " markers or gel pens — anything you like."),
    ("2.  Fill by number", "Colour each triangle with the shade that matches its number."
     " Working one number at a time is the most relaxing way."),
    ("3.  Watch it emerge", "As the facets fill in, the underlying fractal or complex-function"
     " artwork appears. The last page of each set is the full-colour solution."),
    ("4.  Print settings", "Print at 100% / 'Actual size' on US Letter. Matte paper and a light"
     " touch keep the printed numbers from showing through."),
]


# ── gold low-poly emblem for the cover ───────────────────────────────────────
def emblem(ax, cx, cy, r, n=4):
    A = np.array([cx, cy + r])
    B = np.array([cx - r * 0.866, cy - r * 0.5])
    C = np.array([cx + r * 0.866, cy - r * 0.5])

    def P(i, j):
        return A + (B - A) * (i / n) + (C - A) * (j / n)
    for i in range(n):
        for j in range(n - i):
            up = [P(i, j), P(i + 1, j), P(i, j + 1)]
            cen = np.mean(up, axis=0)
            a = 0.10 + 0.55 * (1 - np.hypot(*(cen - [cx, cy])) / r)
            ax.add_patch(Polygon(up, closed=True, facecolor=brand.GOLD, alpha=max(0, a),
                                 edgecolor=brand.GOLD, lw=0.8, zorder=4))
            if i + j < n - 1:
                dn = [P(i + 1, j), P(i, j + 1), P(i + 1, j + 1)]
                ax.add_patch(Polygon(dn, closed=True, facecolor="none",
                                     edgecolor=brand.GOLD, lw=0.8, zorder=4))


# ── house-style helper pages ─────────────────────────────────────────────────
def _fig_to_pil(fig, facecolor):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, facecolor=facecolor)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def howto_page():
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
    ax.text(4.25, 10.0, "HOW TO COLOR", ha="center", fontsize=20, **brand.SERIF_BOLD)
    ax.plot([2.9, 5.6], [9.72, 9.72], color=brand.GOLD, lw=1.2)
    y = 8.7
    for head, body in HOWTO_STEPS:
        ax.text(1.0, y, head, ha="left", fontsize=13.5, color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(1.0, y - 0.42, body, ha="left", va="top", fontsize=11, wrap=True,
                **brand.SERIF)
        y -= 1.65
    ax.text(4.25, 0.65, brand.COPYRIGHT, ha="center", fontsize=9, color="#666666")
    return _fig_to_pil(fig, "white")


def divider_page():
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
    ax.text(4.25, 6.2, "SOLUTIONS", ha="center", fontsize=30, **brand.SERIF_BOLD)
    ax.plot([3.1, 5.4], [5.75, 5.75], color=brand.GOLD, lw=1.4)
    ax.text(4.25, 5.2, "A full-colour reference for every design.", ha="center",
            fontsize=12.5, color="#555555", **brand.SERIF)
    return _fig_to_pil(fig, "white")


def back_cover():
    W, H = 8.5, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    fig.patch.set_facecolor(THEME); ax.set_facecolor(THEME)
    band_h = 1.6
    emblem(ax, W / 2, H * 0.66, 0.9)
    ax.text(W / 2, H * 0.44, "Colour the mathematics.", ha="center",
            fontsize=17, color=brand.CREAM, style="italic", **brand.SERIF)
    ax.text(W / 2, H * 0.36,
            "Domain colourings & Newton fractals,\nbroken into low-poly facets to colour by number.",
            ha="center", fontsize=11.5, color=brand.GOLD, **brand.SERIF, linespacing=1.6)
    ax.text(W / 2, band_h + 0.5, brand.STORE, ha="center", fontsize=11, color=brand.CREAM, **brand.SERIF)
    ax.text(W / 2, band_h + 0.16, brand.COPYRIGHT, ha="center", fontsize=7.5, color="#8a8ca0")
    brand.footer_band(ax, W, band_h)
    return _fig_to_pil(fig, THEME)


def build(out_dir=None):
    out_dir = out_dir or os.path.join(HERE, "pkg_out")
    os.makedirs(out_dir, exist_ok=True)
    pieces = art_gallery.build_all(os.path.join(HERE, "pkg_src"))
    N = len(pieces)

    cover_pil = _fig_to_pil(brand.cover(THEME, emblem, TITLE, SUBTITLE, TAGLINE,
                                        f"{N} Generative Art Designs", square=False), THEME)
    about_pil = _fig_to_pil(brand.about_page("THE MATHEMATICS", ABOUT), "white")

    coloring_pages, colored_pages, preview_paths = [], [], []
    for k, p in enumerate(pieces, 1):
        info = generate_cbn(p["src"], out_dir, poly_type="triangular",
                            side_length=p["side"], num_colors=p["colors"],
                            title=p["title"], subtitle=p.get("desc"),
                            page_label=f"Design {k} of {N}")
        coloring_pages.append(info["coloring_img"])
        colored_pages.append(info["colored_img"])
        print(f"  {p['title']:22} {info['cells']:>5} cells, {p['colors']} colors")
        if k in (1, 5, 6):
            pv = os.path.join(out_dir, f"preview_page_{k}.jpg")
            info["coloring_img"].save(pv, quality=90); preview_paths.append(pv)

    pages = ([cover_pil, about_pil, howto_page()] + coloring_pages +
             [divider_page()] + colored_pages + [back_cover()])
    pdf_path = os.path.join(out_dir, "MathColorByNumber_Vol1.pdf")
    pages[0].save(pdf_path, "PDF", save_all=True, append_images=pages[1:], resolution=300)

    # square listing cover
    sq = brand.cover(THEME, emblem, TITLE, SUBTITLE, TAGLINE,
                     f"{N} Generative Art Designs", square=True)
    sq.savefig(os.path.join(out_dir, "listing_cover.jpg"), dpi=200, facecolor=THEME)
    plt.close(sq)

    print(f"\nPDF: {pdf_path}  ({len(pages)} pages, {os.path.getsize(pdf_path)/1e6:.1f} MB)")
    return pdf_path


if __name__ == "__main__":
    build()
