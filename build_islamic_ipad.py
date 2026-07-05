"""
build_islamic_ipad.py — MathRelaxing "Islamic Star Geometry — iPad Edition"
=============================================================================
Genera el bundle de 5 archivos para el listing iPad, reutilizando el motor
de rosetones de generate_islamic_geometry.py:

  ipad_islamic/
    IslamicGeometry_iPad_GoodNotes.pdf      — PDF hipervinculado (indice + 50)
    IslamicGeometry_Procreate_PNG_part1.zip — PNGs transparentes 1..25 (300 dpi)
    IslamicGeometry_Procreate_PNG_part2.zip — PNGs transparentes 26..50
    IslamicGeometry.swatches                — paleta Procreate (30 colores)
    How_to_use_on_iPad.pdf                  — guia 1 pagina
    previews/ipad_preview_1_hero.jpg
    previews/ipad_preview_2_included.jpg
    previews/ipad_preview_3_twoways.jpg
"""

import os
import json
import math
import zipfile
import colorsys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

import fitz  # PyMuPDF

import generate_islamic_geometry as ig

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "ipad_islamic")
PREV = os.path.join(OUT, "previews")
PNG_DIR = os.path.join(OUT, "_png")
os.makedirs(PREV, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

NAVY = "#12172d"
GOLD = "#c7ad7c"
CREAM = "#f2e9da"
TEAL = "#7fb0aa"


# ── 1. Render the 50 numbered designs as transparent PNGs ───────────────────
def render_all_pngs(plan, reuse=True):
    paths = []
    for d in plan:
        n = d["design_no"]
        p = os.path.join(PNG_DIR, f"IslamicGeometry_{n:02d}.png")
        if not (reuse and os.path.exists(p)):
            fig = ig.design_page(n, d["title"], d["n"], d["rings"], d["amp_base"],
                                  d["twist"], d["seed"], d["hue"], mode="numbered",
                                  transparent=True)
            fig.savefig(p, dpi=300, transparent=True)
            plt.close(fig)
        paths.append(p)
        if n % 10 == 0:
            print(f"  ...{n}/50 PNGs")
    return paths


# ── 2. Split PNGs into two ZIPs ──────────────────────────────────────────────
def build_zips(png_paths):
    z1 = os.path.join(OUT, "IslamicGeometry_Procreate_PNG_part1.zip")
    z2 = os.path.join(OUT, "IslamicGeometry_Procreate_PNG_part2.zip")
    with zipfile.ZipFile(z1, "w", zipfile.ZIP_DEFLATED) as z:
        for p in png_paths[:25]:
            z.write(p, os.path.basename(p))
    with zipfile.ZipFile(z2, "w", zipfile.ZIP_DEFLATED) as z:
        for p in png_paths[25:]:
            z.write(p, os.path.basename(p))
    print("  ZIPs listos")


# ── 3. Procreate .swatches palette (3 shades x 10 hues = 30 colors) ─────────
def build_swatches():
    swatches = []
    for hue in ig.HUES:
        for t in (0.15, 0.5, 0.85):
            sat = 0.22 + 0.62 * t
            val = 0.98 - 0.55 * t
            swatches.append({"hue": round(hue, 4), "saturation": round(sat, 4),
                              "brightness": round(val, 4), "alpha": 1, "colorSpace": 0})
    data = [{"name": "MathRelaxing — Islamic Star Geometry", "swatches": swatches}]
    path = os.path.join(OUT, "IslamicGeometry.swatches")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Swatches.json", json.dumps(data))
    print("  .swatches listo")


# ── 4. Hyperlinked GoodNotes PDF ─────────────────────────────────────────────
def build_goodnotes_pdf(png_paths):
    PW, PH = 612.0, 792.0  # US Letter @72dpi
    per_page = 20          # 4 cols x 5 rows of thumbnails
    n_index = math.ceil(len(png_paths) / per_page)
    doc = fitz.open()

    for _ in range(n_index + len(png_paths)):
        doc.new_page(width=PW, height=PH)

    for idx, png in enumerate(png_paths):
        page = doc[n_index + idx]
        page.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=(1, 1, 1))
        margin = 26
        page.insert_image(fitz.Rect(margin, margin, PW - margin, PH - margin),
                          filename=png, keep_proportion=True)

    for ip in range(n_index):
        page = doc[ip]
        page.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=(1, 1, 1))
        title = "Islamic Star Geometry" if ip == 0 else "Index (cont.)"
        page.insert_textbox(fitz.Rect(0, 30, PW, 70), title,
                            fontsize=20, fontname="times-bold", align=1)
        if ip == 0:
            page.insert_textbox(fitz.Rect(0, 62, PW, 84),
                                "Tap any design to jump straight to it",
                                fontsize=10, fontname="times-italic", align=1)
        cols, rows = 4, 5
        m_top, m_side, gap = 96, 46, 16
        cw = (PW - 2 * m_side - (cols - 1) * gap) / cols
        ch = (PH - m_top - 40 - (rows - 1) * gap) / rows
        start = ip * per_page
        for k in range(per_page):
            idx = start + k
            if idx >= len(png_paths):
                break
            r, c = divmod(k, cols)
            x = m_side + c * (cw + gap)
            y = m_top + r * (ch + gap)
            rect = fitz.Rect(x, y, x + cw, y + ch)
            page.insert_image(rect, filename=png_paths[idx], keep_proportion=True)
            page.draw_rect(rect, color=(0.8, 0.8, 0.8), width=0.5)
            page.insert_textbox(fitz.Rect(x, y + ch - 12, x + cw, y + ch),
                                f"{idx + 1}", fontsize=7, align=1, color=(0.4, 0.4, 0.4))
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect,
                              "page": n_index + idx, "to": fitz.Point(0, 0)})

    out = os.path.join(OUT, "IslamicGeometry_iPad_GoodNotes.pdf")
    doc.save(out, deflate=True, garbage=4)
    doc.close()
    print(f"  GoodNotes PDF listo ({n_index} indice + {len(png_paths)} disenos)")


# ── 5. How-to guide (1 page) ─────────────────────────────────────────────────
def build_howto():
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.text(4.25, 9.9, "Coloring on Your iPad", ha="center", fontsize=26,
            family="serif", color=CREAM)
    ax.text(4.25, 9.35, "Islamic Star Geometry  ·  iPad Edition",
            ha="center", fontsize=13, style="italic", color=GOLD)
    blocks = [
        ("In GoodNotes or Notability",
         "Open the PDF and tap any thumbnail in the index to jump straight to a\n"
         "design. Color directly on top of the numbered facets with any brush —\n"
         "the line art and numbers stay crisp underneath. Duplicate a page to\n"
         "color it again."),
        ("In Procreate",
         "Import a transparent PNG from the ZIP. Add a new layer BELOW the line\n"
         "art and paint there, so the black outlines and numbers always stay on\n"
         "top. Load IslamicGeometry.swatches for a ready-made palette (30 colors)."),
        ("Tips",
         "• Use the color-fill / ColorDrop tool to flood whole numbered facets.\n"
         "• Match each number to the legend bar at the bottom of the page.\n"
         "• Everything is reusable forever — color each design as often as you like."),
    ]
    y = 8.3
    for head, body in blocks:
        ax.text(0.9, y, head, ha="left", fontsize=15, family="serif", color=GOLD)
        ax.text(0.9, y - 0.35, body, ha="left", va="top", fontsize=11.5,
                color=CREAM, linespacing=1.6)
        y -= 2.0
    ax.text(4.25, 0.6, "© MathRelaxing  ·  mathrelaxing.store  ·  personal use only",
            ha="center", fontsize=9, color="#8a8fa0")
    out = os.path.join(OUT, "How_to_use_on_iPad.pdf")
    fig.savefig(out, facecolor=NAVY)
    plt.close(fig)
    print("  How-to PDF listo")


# ── coloured showcase design (for previews) ──────────────────────────────────
def render_showcase(colored, path, size_in=6.0):
    fig = plt.figure(figsize=(size_in, size_in))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, size_in); ax.set_ylim(0, size_in); ax.set_aspect("equal")
    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
    m = 0.3
    R_max = (size_in - 2 * m) / 2 * 0.72
    mode = "colored" if colored else "numbered"
    ig.draw_rosette(ax, size_in / 2, size_in / 2, R_max, 12, 5, 0.24, 0.06,
                     4242, 0.58, mode=mode)
    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)


# ── 6. Preview images ────────────────────────────────────────────────────────
def _ipad_frame(ax, cx, cy, w, h):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=0.22", fill=True,
                 facecolor="#0c0e16", edgecolor="#3a3f52", lw=2, zorder=2))
    sm = 0.16
    ax.add_patch(FancyBboxPatch((cx - w / 2 + sm, cy - h / 2 + sm),
                 w - 2 * sm, h - 2 * sm, boxstyle="round,pad=0,rounding_size=0.05",
                 fill=True, facecolor="white", edgecolor="none", zorder=2.5))
    return (cx - w / 2 + sm, cy - h / 2 + sm, w - 2 * sm, h - 2 * sm)


def _logo(ax, cx, cy, w):
    logo = mpimg.imread(ig.LOGO_PATH)
    lh = w * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(cx - w / 2, cx + w / 2, cy - lh / 2, cy + lh / 2), zorder=5)


def preview_hero(colored_png):
    fig = plt.figure(figsize=(10, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.text(5, 9.35, "Coloring Book for iPad", ha="center",
            fontsize=38, family="serif", color=CREAM)
    ax.text(5, 8.75, "Islamic Star Geometry   ·   50 Star Rosette Designs",
            ha="center", fontsize=15, style="italic", color=GOLD)
    sx, sy, sw, sh = _ipad_frame(ax, 5, 4.9, 4.6, 6.0)
    img = mpimg.imread(colored_png)
    side = min(sw, sh) * 0.92
    ax.imshow(img, extent=(5 - side / 2, 5 + side / 2, 4.9 - side / 2, 4.9 + side / 2), zorder=3)
    ax.text(5, 1.15, "GoodNotes  ·  Notability  ·  Procreate", ha="center",
            fontsize=15, color=TEAL)
    _logo(ax, 5, 0.55, 1.5)
    fig.savefig(os.path.join(PREV, "ipad_preview_1_hero.jpg"), dpi=200, facecolor=NAVY)
    plt.close(fig)


def preview_included():
    fig = plt.figure(figsize=(10, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.add_patch(plt.Rectangle((0, 9.85), 10, 0.15, color=GOLD, zorder=2))
    ax.text(5, 9.1, "Everything Included", ha="center",
            fontsize=36, family="serif", color=CREAM)
    ax.text(5, 8.55, "Islamic Star Geometry  ·  iPad Edition", ha="center",
            fontsize=14, style="italic", color=GOLD)
    items = [
        "50 unique geometric star rosette designs",
        "Hyperlinked PDF index for GoodNotes & Notability",
        "50 transparent PNGs (300 dpi) for Procreate",
        "Procreate palette  ·  30 curated swatches",
        "'How to use on iPad' quick guide",
        "Instant download  ·  personal use",
    ]
    y = 7.2
    for it in items:
        ax.add_patch(FancyBboxPatch((1.15, y - 0.28), 0.56, 0.56,
                     boxstyle="round,pad=0,rounding_size=0.1", facecolor="#1e2440",
                     edgecolor="none", zorder=2))
        ax.text(1.43, y, "✔", ha="center", va="center", fontsize=20, color=GOLD, zorder=3)
        ax.text(2.05, y, it, ha="left", va="center", fontsize=17, color="#d7d9e2")
        y -= 0.92
    _logo(ax, 5, 0.6, 1.4)
    fig.savefig(os.path.join(PREV, "ipad_preview_2_included.jpg"), dpi=200, facecolor=NAVY)
    plt.close(fig)


def preview_twoways(line_png, colored_png):
    fig = plt.figure(figsize=(10, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.text(5, 9.25, "Two Ways to Color", ha="center",
            fontsize=36, family="serif", color=CREAM)
    ax.text(5, 8.7, "however you love to work on your iPad", ha="center",
            fontsize=14, style="italic", color=GOLD)
    for cx, png, label, sub, col in [
        (2.75, line_png, "GoodNotes", "color on top with Apple Pencil", TEAL),
        (7.25, colored_png, "Procreate", "color beneath the numbered facets", TEAL),
    ]:
        ax.add_patch(FancyBboxPatch((cx - 1.95, 4.2), 3.9, 3.9,
                     boxstyle="round,pad=0,rounding_size=0.06", facecolor="white",
                     edgecolor="none", zorder=2))
        img = mpimg.imread(png)
        ax.imshow(img, extent=(cx - 1.8, cx + 1.8, 4.35, 7.95), zorder=3)
        ax.text(cx, 3.6, label, ha="center", fontsize=20, family="serif", color=TEAL)
        ax.text(cx, 3.2, sub, ha="center", fontsize=12, color="#b9bccb")
    _logo(ax, 5, 0.7, 1.4)
    fig.savefig(os.path.join(PREV, "ipad_preview_3_twoways.jpg"), dpi=200, facecolor=NAVY)
    plt.close(fig)


def main():
    plan = ig.build_plan()
    print("Renderizando 50 disenos...")
    pngs = render_all_pngs(plan)
    build_zips(pngs)
    build_swatches()
    build_goodnotes_pdf(pngs)
    build_howto()

    print("Previews...")
    line_png = os.path.join(PNG_DIR, "_showcase_line.png")
    colored_png = os.path.join(PNG_DIR, "_showcase_colored.png")
    render_showcase(False, line_png)
    render_showcase(True, colored_png)
    preview_hero(colored_png)
    preview_included()
    preview_twoways(line_png, colored_png)
    print("\nBundle iPad completo en:", OUT)


if __name__ == "__main__":
    main()
