"""
generate_islamic_geometry.py — MathRelaxing "Islamic Star Geometry" generator
==============================================================================
Genera proceduralmente 50 disenos de rosetones geometricos islamicos (girih)
mediante un algoritmo de malla polar: anillos concentricos de puntos con
simetria rotacional de orden n, donde anillos alternos reciben una modulacion
de radio alternante (+/-) que produce las puntas de estrella caracteristicas
de la geometria islamica (octagramas, decagramas, dodecagramas...). La malla
se triangula/cuadricula en facetas numeradas — mismo formato "color by number"
que Sacred Geometry, tema matematico distinto (simetria radial discreta en
vez de mallas 3D proyectadas).

Salida:
  islamic_geometry_digital.pdf     — PDF de 52 paginas, 8.5x11in, listo para imprimir
  islamic_geometry_cover.jpg       — portada cuadrada (2000x2000, estilo de marca)
  islamic_geometry_page_01..07.jpg — paginas de muestra para el listing
"""

import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon
from matplotlib.backends.backend_pdf import PdfPages
import colorsys

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 8.5, 11.0
LOGO_PATH = os.path.join(BASE, "mathrelaxing_logo.png")

BG_DARK = "#0d0a14"
GOLD = "#c9a24b"
CREAM = "#f2e9da"
NUM_BANDS = 8

# 10 base hues cycled across the 50 designs (independent of family), giving
# page-to-page palette variety the same way the Sacred Geometry book does.
HUES = [0.58, 0.92, 0.75, 0.38, 0.08, 0.02, 0.68, 0.14, 0.86, 0.48]


def hue_palette(hue, n=NUM_BANDS):
    """n evenly-spaced shades of one hue, light -> dark (matches the
    monochrome legend-bar convention used by every MathRelaxing coloring book)."""
    colors = []
    for k in range(n):
        t = k / (n - 1)
        light = 0.93 - 0.07 * t
        sat = 0.22 + 0.62 * t
        val = 0.98 - 0.55 * t
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        colors.append((r, g, b))
        _ = light  # (kept for readability of the intent; hsv already encodes it)
    return colors


# ─────────────────────────────────────────────────────────────────────────
# Rosette geometry
# ─────────────────────────────────────────────────────────────────────────
def build_rosette_cells(n, rings, R_max, amp_base, twist, seed):
    """Returns a list of (poly_pts[(x,y)...], band) for one n-fold symmetric
    star rosette. Odd-numbered rings (1-indexed) get an alternating +/-
    radius modulation -> star points; even rings stay plain -> connecting
    bands. Consecutive rings are twisted by a small constant angle so the
    quad strip reads as an interlaced weave rather than a flat grid."""
    rng = np.random.default_rng(seed)
    ring_pts = []
    for r in range(rings):
        base_r = R_max * ((r + 1) / rings) ** 0.88
        star = (r % 2 == 0)
        amp = amp_base if star else 0.0
        jitter = rng.uniform(0.98, 1.02)
        twist_off = twist * r
        idx = np.arange(n)
        theta = 2 * np.pi * idx / n + twist_off
        mult = 1.0 + amp * np.where(idx % 2 == 0, 1.0, -1.0)
        radius = base_r * jitter * mult
        xs = radius * np.cos(theta)
        ys = radius * np.sin(theta)
        ring_pts.append(list(zip(xs, ys)))

    cells = []  # (points, ring_index, i)
    # fan: center -> ring 0
    for i in range(n):
        pts = [(0.0, 0.0), ring_pts[0][i], ring_pts[0][(i + 1) % n]]
        cells.append((pts, 0, i))
    # quads between consecutive rings
    for r in range(rings - 1):
        for i in range(n):
            pts = [ring_pts[r][i], ring_pts[r][(i + 1) % n],
                   ring_pts[r + 1][(i + 1) % n], ring_pts[r + 1][i]]
            cells.append((pts, r + 1, i))

    out = []
    for pts, r, i in cells:
        h = (hash((seed, r, i)) % 1000) / 1000.0
        band = int(np.clip((r + 0.5) / rings * NUM_BANDS + (h - 0.5) * 2.2, 0, NUM_BANDS - 1))
        out.append((pts, band))
    return out


def centroid(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def draw_rosette(ax, cx, cy, R_max, n, rings, amp_base, twist, seed, hue,
                  mode="numbered", accent_every=11):
    """mode: 'numbered' (white cells, black edge, gray number, few colored
    accents) or 'colored' (every cell filled — solution / showcase art)."""
    cells = build_rosette_cells(n, rings, R_max, amp_base, twist, seed)
    palette = hue_palette(hue)
    for k, (pts, band) in enumerate(cells):
        xy = [(cx + x, cy + y) for x, y in pts]
        color = palette[band]
        if mode == "colored" or (mode == "numbered" and k % accent_every == 0):
            face = color
        else:
            face = "none"
        ax.add_patch(Polygon(xy, closed=True, facecolor=face,
                              edgecolor="black", linewidth=1.05, zorder=2))
        if mode == "numbered":
            tx, ty = centroid(xy)
            ax.text(tx, ty, str(band + 1), fontsize=8.2, ha="center", va="center",
                    color="#888888", zorder=3)
    return palette


def legend_bar(ax, x0, y0, w, h, palette):
    seg = w / len(palette)
    for k, color in enumerate(palette):
        x = x0 + k * seg
        ax.add_patch(plt.Rectangle((x, y0), seg, h, facecolor=color,
                                    edgecolor="white", linewidth=0.6, zorder=2))
        text_color = "white" if k >= len(palette) // 2 else "#333333"
        ax.text(x + seg / 2, y0 + h / 2, str(k + 1), ha="center", va="center",
                fontsize=11, color=text_color, zorder=3)


# ─────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────
def new_page(bg=None):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect("equal")
    ax.axis("off")
    if bg:
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
    return fig, ax


def design_page(design_no, title, n, rings, amp_base, twist, seed, hue,
                 mode="numbered", transparent=False):
    fig, ax = new_page()
    if transparent:
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
    cx, cy = PAGE_W / 2, PAGE_H / 2 + 0.55
    R_max = 2.7
    palette = draw_rosette(ax, cx, cy, R_max, n, rings, amp_base, twist, seed, hue, mode=mode)
    if mode == "numbered":
        ax.text(PAGE_W / 2, 1.05, f"{design_no}. {title}", ha="center", va="center",
                fontsize=13, family="serif")
        legend_bar(ax, 0.85, 0.28, PAGE_W - 1.7, 0.42, palette)
    return fig


def cover_square():
    S = 8.0
    fig = plt.figure(figsize=(S, S))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, S)
    ax.set_ylim(0, S)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)

    draw_rosette(ax, S / 2, S / 2 + 0.7, 2.3, 12, 6, 0.28, 0.09, 4242, 0.10, mode="colored")

    footer_h = 1.45
    ax.add_patch(plt.Rectangle((0, 0), S, footer_h, color="black", zorder=4))
    ax.text(S / 2, 3.35, "ISLAMIC STAR", ha="center", va="center",
            fontsize=32, fontweight="bold", family="serif", color=CREAM, zorder=5)
    ax.text(S / 2, 2.75, "GEOMETRY", ha="center", va="center",
            fontsize=24, family="serif", color=GOLD, zorder=5)
    ax.text(S / 2, 2.1, "A Color-by-Number Journey", ha="center", va="center",
            fontsize=13, style="italic", color=CREAM, zorder=5)
    ax.text(S / 2, 1.6, "50 Geometric Star Rosette Designs", ha="center", va="center",
            fontsize=11.5, color=GOLD, zorder=5)

    logo = mpimg.imread(LOGO_PATH)
    logo_h = 0.98
    logo_w = logo_h * logo.shape[1] / logo.shape[0]
    cx, cy = S / 2, footer_h * 0.5
    ax.imshow(logo, extent=(cx - logo_w / 2, cx + logo_w / 2, cy - logo_h / 2, cy + logo_h / 2),
              zorder=6, aspect="auto")
    return fig


def cover_page():
    fig, ax = new_page(bg=BG_DARK)
    footer_h = 1.5
    draw_rosette(ax, PAGE_W / 2, 7.7, 2.4, 12, 6, 0.28, 0.09, 4242, 0.10, mode="colored")
    ax.add_patch(plt.Rectangle((0, 0), PAGE_W, footer_h, color="black", zorder=4))
    ax.text(PAGE_W / 2, 3.7, "ISLAMIC STAR GEOMETRY", ha="center", va="center",
            fontsize=27, fontweight="bold", family="serif", color=CREAM, zorder=5)
    ax.text(PAGE_W / 2, 3.05, "A Color-by-Number Journey", ha="center", va="center",
            fontsize=13, style="italic", color=CREAM, zorder=5)
    ax.text(PAGE_W / 2, 2.55, "50 Geometric Star Rosette Designs", ha="center", va="center",
            fontsize=12, color=GOLD, zorder=5)
    logo = mpimg.imread(LOGO_PATH)
    logo_w, logo_h = 3.0, 3.0 * logo.shape[0] / logo.shape[1]
    cx, cy = PAGE_W / 2, 0.75
    ax.imshow(logo, extent=(cx - logo_w / 2, cx + logo_w / 2, cy - logo_h / 2, cy + logo_h / 2),
              zorder=6, aspect="auto")
    return fig


def about_page():
    fig, ax = new_page()
    ax.text(PAGE_W / 2, 10.0, "THE MATHEMATICS", ha="center", fontsize=20,
            fontweight="bold", family="serif")
    body = (
        "Every rosette in this book is built the same way real Islamic\n"
        "geometric artisans laid out star patterns — with a compass and a\n"
        "grid of concentric circles, formalized here as an algorithm.\n\n"
        "Points are placed on concentric rings around a center, evenly spaced\n"
        "by rotational symmetry of order n (8, 9, 10, 12 or 16-fold). Every\n"
        "other ring receives an alternating outward/inward radius shift,\n"
        "which turns a plain ring of points into a sharp n-pointed star.\n"
        "Consecutive rings are rotated by a small twist angle, so the bands\n"
        "between them read as an interlaced weave rather than a flat grid.\n\n"
        "The resulting mesh of triangles and quadrilaterals is numbered by\n"
        "distance from the center — an outward gradient across 8 tones of a\n"
        "single hue, the same numbering convention used across every\n"
        "MathRelaxing color-by-number book.\n\n"
        "Ten star families appear — Octagram, Decagram, Dodecagram,\n"
        "Hexagram, Enneagram and more — each explored across five variations\n"
        "in ring count, twist and star sharpness."
    )
    ax.text(PAGE_W / 2, 8.9, body, ha="center", va="top", fontsize=11.5,
            linespacing=1.9, family="serif")
    ax.text(PAGE_W / 2, 0.65, "© MathRelaxing. For personal use only. Not for redistribution or resale.",
            ha="center", va="center", fontsize=9, color="#666666")
    return fig


def howto_page():
    fig, ax = new_page()
    ax.text(1.0, 10.0, "How to colour", ha="left", fontsize=20, family="serif")
    lines = [
        "1. Match the numbers in the cells to the colour legend at the bottom",
        "    of the page.",
        "2. Relax and enjoy the star pattern emerge from flat facets!",
        "3. A few accent cells have been pre-coloured for your convenience.",
        "",
        "Use any pens, pencils, or markers. Slip a spare sheet behind the page",
        "if using wet markers.",
    ]
    y = 9.35
    for line in lines:
        ax.text(1.0, y, line, ha="left", va="top", fontsize=12, family="sans-serif")
        y -= 0.32
    return fig


# ─────────────────────────────────────────────────────────────────────────
# 50-design plan: 10 star families x 5 variants each
# ─────────────────────────────────────────────────────────────────────────
FAMILIES = [
    ("Octagram Rosette", 8),
    ("Decagram Star", 10),
    ("Dodecagram Mandala", 12),
    ("Hexagram Lattice", 6),
    ("Enneagram Weave", 9),
    ("Sixteen-Point Star", 16),
    ("Girih Burst", 10),
    ("Rub el Hizb Star", 8),
    ("Khatam Weave", 12),
    ("Isfahan Rosette", 9),
]


def build_plan():
    plan = []
    for fam_idx, (name, n) in enumerate(FAMILIES):
        for v in range(5):
            design_no = fam_idx * 5 + v + 1
            rings = 3 + (v % 4)                      # 3..6
            amp_base = 0.18 + 0.06 * (v % 3)          # star sharpness (capped, safe within page margins)
            twist = (0.10 + 0.05 * (v % 2)) * (1 if v % 2 == 0 else -1)
            twist *= math.pi / n * 0.55               # keep well inside safe bound
            seed = 3000 + design_no * 13
            hue = HUES[design_no % len(HUES)]
            title = f"{name} {v + 1}"
            plan.append({
                "design_no": design_no, "title": title, "n": n, "rings": rings,
                "amp_base": amp_base, "twist": twist, "seed": seed, "hue": hue,
            })
    return plan


def main():
    plan = build_plan()
    pdf_path = os.path.join(BASE, "islamic_geometry_digital.pdf")
    preview_specs = [1, 6, 15, 24, 33, 42, 48]
    preview_figs = {}

    with PdfPages(pdf_path) as pdf:
        fig = cover_page()
        pdf.savefig(fig)
        plt.close(fig)

        preview_figs["cover"] = cover_square()

        fig = about_page()
        pdf.savefig(fig)
        plt.close(fig)

        fig = howto_page()
        pdf.savefig(fig)
        plt.close(fig)

        for d in plan:
            fig = design_page(d["design_no"], d["title"], d["n"], d["rings"],
                               d["amp_base"], d["twist"], d["seed"], d["hue"])
            pdf.savefig(fig)
            if d["design_no"] in preview_specs:
                preview_figs[f"page_{d['design_no']:02d}"] = fig
            else:
                plt.close(fig)
            if d["design_no"] % 10 == 0:
                print(f"  ...{d['design_no']}/50 paginas")

    order = ["cover"] + [f"page_{n:02d}" for n in preview_specs]
    for idx, key in enumerate(order):
        fig = preview_figs[key]
        name = "islamic_geometry_cover.jpg" if key == "cover" else f"islamic_geometry_page_{idx:02d}.jpg"
        fig.savefig(os.path.join(BASE, name), dpi=150, facecolor=fig.get_facecolor())
        plt.close(fig)

    print(f"PDF generado: {pdf_path}  ({3 + len(plan)} paginas)")
    print("Previews guardados:", order)


if __name__ == "__main__":
    main()
