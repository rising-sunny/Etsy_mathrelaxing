"""
template_ipad_bundle.py — reusable builder for MathRelaxing iPad editions
=============================================================================
Assembles the fixed 5-file GoodNotes/Notability/Procreate bundle + the 3 navy
preview photos, identically for every product. A concrete iPad edition supplies:

  • cfg                  — names, palette, copy (see BundleConfig)
  • render_design_fig(n) — fn -> portrait 8.5x11 line-art Figure of design n
  • showcase_line_png    — path to a line-art showcase PNG (transparent)
  • showcase_colored_png — path to a COLOURED showcase PNG (transparent)
                            (the colouring is product-specific, so the product
                             renders these two and hands over the paths)

Produces, in cfg.out_dir:
  <Prefix>_iPad_GoodNotes.pdf         (hyperlinked: 3 index pages + 50 designs)
  <Prefix>_Procreate_PNG_part1.zip    (designs 1..25, transparent 300 dpi)
  <Prefix>_Procreate_PNG_part2.zip    (designs 26..50)
  <Prefix>.swatches                   (30-colour Procreate palette)
  How_to_use_on_iPad.pdf
  previews/ipad_preview_1_hero.jpg
  previews/ipad_preview_2_included.jpg
  previews/ipad_preview_3_twoways.jpg

The promo mp4 is built separately (per-product colour-reveal animation) with
brand.encode_mp4 — see build_celtic_ipad_video.py as the reference.
"""

import os
import math
from dataclasses import dataclass, field
from typing import Callable, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch
import fitz  # PyMuPDF

import brand

DEFAULT_INCLUDED = [
    "50 unique designs",
    "Hyperlinked PDF index for GoodNotes & Notability",
    "50 transparent PNGs (300 dpi) for Procreate",
    "Procreate palette  ·  30 curated swatches",
    "'How to use on iPad' quick guide",
    "Instant download  ·  personal use",
]


@dataclass
class BundleConfig:
    out_dir: str                      # e.g. .../ipad_celtic
    prefix: str                       # file basename, e.g. "CelticKnot"
    edition: str                      # e.g. "Celtic Knot Mathematics"
    subtitle_line: str                # hero subtitle, e.g. "Celtic Knot Mathematics   ·   50 Woven Interlace Designs"
    design_word: str                  # e.g. "woven Celtic bands"
    palette_name: str                 # e.g. "MathRelaxing — Celtic Knot"
    palette_hexes: List[str] = field(default_factory=list)
    n_designs: int = 50
    included: List[str] = field(default_factory=lambda: list(DEFAULT_INCLUDED))


def _png_dir(cfg):
    d = os.path.join(cfg.out_dir, "_png")
    os.makedirs(d, exist_ok=True)
    return d


# ── transparent line-art PNGs ────────────────────────────────────────────────
def render_pngs(cfg, render_design_fig, reuse=True):
    d = _png_dir(cfg)
    paths = []
    for n in range(1, cfg.n_designs + 1):
        p = os.path.join(d, f"{cfg.prefix}_{n:02d}.png")
        if not (reuse and os.path.exists(p)):
            fig = render_design_fig(n)
            fig.savefig(p, dpi=300, transparent=True)
            plt.close(fig)
        paths.append(p)
    return paths


def build_zips(cfg, png_paths):
    import zipfile
    half = len(png_paths) // 2
    for part, chunk in ((1, png_paths[:half]), (2, png_paths[half:])):
        z = os.path.join(cfg.out_dir, f"{cfg.prefix}_Procreate_PNG_part{part}.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in chunk:
                zf.write(p, os.path.basename(p))


# ── hyperlinked GoodNotes PDF ────────────────────────────────────────────────
def build_goodnotes_pdf(cfg, png_paths):
    PW, PH = 612.0, 792.0
    per_page = 20
    n_index = math.ceil(len(png_paths) / per_page)
    doc = fitz.open()
    for _ in range(n_index + len(png_paths)):
        doc.new_page(width=PW, height=PH)

    for idx, png in enumerate(png_paths):
        page = doc[n_index + idx]
        page.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=(1, 1, 1))
        m = 26
        page.insert_image(fitz.Rect(m, m, PW - m, PH - m), filename=png, keep_proportion=True)

    for ip in range(n_index):
        page = doc[ip]
        page.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=(1, 1, 1))
        head = cfg.edition if ip == 0 else "Index (cont.)"
        page.insert_textbox(fitz.Rect(0, 30, PW, 70), head, fontsize=20,
                            fontname="times-bold", align=1)
        if ip == 0:
            page.insert_textbox(fitz.Rect(0, 62, PW, 84),
                                "Tap any design to jump straight to it",
                                fontsize=10, fontname="times-italic", align=1)
        cols, rows = 4, 5
        m_top, m_side, gap = 96, 46, 16
        cw = (PW - 2 * m_side - (cols - 1) * gap) / cols
        ch = (PH - m_top - 40 - (rows - 1) * gap) / rows
        for k in range(per_page):
            idx = ip * per_page + k
            if idx >= len(png_paths):
                break
            r, c = divmod(k, cols)
            x = m_side + c * (cw + gap); y = m_top + r * (ch + gap)
            rect = fitz.Rect(x, y, x + cw, y + ch)
            page.insert_image(rect, filename=png_paths[idx], keep_proportion=True)
            page.draw_rect(rect, color=(0.8, 0.8, 0.8), width=0.5)
            page.insert_textbox(fitz.Rect(x, y + ch - 12, x + cw, y + ch), f"{idx + 1}",
                                fontsize=7, align=1, color=(0.4, 0.4, 0.4))
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect,
                              "page": n_index + idx, "to": fitz.Point(0, 0)})

    doc.save(os.path.join(cfg.out_dir, f"{cfg.prefix}_iPad_GoodNotes.pdf"),
             deflate=True, garbage=4)
    doc.close()


# ── how-to guide ─────────────────────────────────────────────────────────────
def build_howto(cfg):
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
    fig.patch.set_facecolor(brand.IPAD_NAVY); ax.set_facecolor(brand.IPAD_NAVY)
    ax.text(4.25, 9.9, "Coloring on Your iPad", ha="center", fontsize=26,
            color=brand.CREAM, **brand.SERIF)
    ax.text(4.25, 9.35, f"{cfg.edition}  ·  iPad Edition", ha="center",
            fontsize=13, style="italic", color=brand.GOLD, **brand.SERIF)
    blocks = [
        ("In GoodNotes or Notability",
         "Open the PDF and tap any thumbnail in the index to jump straight to a\n"
         "design. Color directly on top of the line art with any brush — it stays\n"
         "crisp underneath. Duplicate a page to color it again."),
        ("In Procreate",
         "Import a transparent PNG from the ZIP. Add a new layer BELOW the line\n"
         f"art and paint there, so the {cfg.design_word} always stay on top. Load\n"
         f"{cfg.prefix}.swatches for a ready-made palette (30 colors)."),
        ("Tips",
         "• Use the color-fill / ColorDrop tool to flood whole sections.\n"
         "• Everything is reusable forever — color each design as often as you like."),
    ]
    y = 8.3
    for head, body in blocks:
        ax.text(0.9, y, head, ha="left", fontsize=15, color=brand.GOLD, **brand.SERIF)
        ax.text(0.9, y - 0.35, body, ha="left", va="top", fontsize=11.5,
                color=brand.CREAM, linespacing=1.6)
        y -= 2.0
    ax.text(4.25, 0.6, f"© MathRelaxing  ·  {brand.STORE}  ·  personal use only",
            ha="center", fontsize=9, color="#8a8fa0")
    fig.savefig(os.path.join(cfg.out_dir, "How_to_use_on_iPad.pdf"), facecolor=brand.IPAD_NAVY)
    plt.close(fig)


# ── the 3 preview photos ─────────────────────────────────────────────────────
def _prev_dir(cfg):
    d = os.path.join(cfg.out_dir, "previews")
    os.makedirs(d, exist_ok=True)
    return d


def preview_hero(cfg, colored_png):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.35, "Coloring Book for iPad", ha="center", fontsize=38,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.75, cfg.subtitle_line, ha="center", fontsize=15,
            style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    brand.ipad_frame(ax, 5, 4.9, 4.6, 6.0)
    img = mpimg.imread(colored_png); side = 5.5 * 0.92
    ax.imshow(img, extent=(5 - side / 2, 5 + side / 2, 4.9 - side / 2, 4.9 + side / 2), zorder=3)
    ax.text(5, 1.15, "GoodNotes  ·  Notability  ·  Procreate", ha="center",
            fontsize=15, color=brand.IPAD_TEAL)
    brand.ipad_logo(ax, 5, 0.55, 1.5)
    fig.savefig(os.path.join(_prev_dir(cfg), "ipad_preview_1_hero.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def preview_included(cfg):
    fig, ax = brand.ipad_fig()
    ax.add_patch(plt.Rectangle((0, 9.85), 10, 0.15, color=brand.GOLD, zorder=2))
    ax.text(5, 9.1, "Everything Included", ha="center", fontsize=36,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.55, f"{cfg.edition}  ·  iPad Edition", ha="center",
            fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    y = 7.2
    for it in cfg.included:
        ax.add_patch(FancyBboxPatch((1.15, y - 0.28), 0.56, 0.56,
                     boxstyle="round,pad=0,rounding_size=0.1", facecolor="#1e2440",
                     edgecolor="none", zorder=2))
        ax.text(1.43, y, "✔", ha="center", va="center", fontsize=20, color=brand.GOLD, zorder=3)
        ax.text(2.05, y, it, ha="left", va="center", fontsize=17, color="#d7d9e2")
        y -= 0.92
    brand.ipad_logo(ax, 5, 0.6, 1.4)
    fig.savefig(os.path.join(_prev_dir(cfg), "ipad_preview_2_included.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def preview_twoways(cfg, line_png, colored_png):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.25, "Two Ways to Color", ha="center", fontsize=36,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.7, "however you love to work on your iPad", ha="center",
            fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    for cx, png, label, sub in [
        (2.75, line_png, "GoodNotes", "color on top with Apple Pencil"),
        (7.25, colored_png, "Procreate", "color beneath the line art"),
    ]:
        ax.add_patch(FancyBboxPatch((cx - 1.95, 4.2), 3.9, 3.9,
                     boxstyle="round,pad=0,rounding_size=0.06", facecolor="white",
                     edgecolor="none", zorder=2))
        ax.imshow(mpimg.imread(png), extent=(cx - 1.8, cx + 1.8, 4.35, 7.95), zorder=3)
        ax.text(cx, 3.6, label, ha="center", fontsize=20, color=brand.IPAD_TEAL, **brand.SERIF)
        ax.text(cx, 3.2, sub, ha="center", fontsize=12, color="#b9bccb")
    brand.ipad_logo(ax, 5, 0.7, 1.4)
    fig.savefig(os.path.join(_prev_dir(cfg), "ipad_preview_3_twoways.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


# ── orchestrator ─────────────────────────────────────────────────────────────
def build(cfg, render_design_fig, showcase_line_png, showcase_colored_png):
    os.makedirs(cfg.out_dir, exist_ok=True)
    pngs = render_pngs(cfg, render_design_fig)
    build_zips(cfg, pngs)
    brand.swatches_file(os.path.join(cfg.out_dir, f"{cfg.prefix}.swatches"),
                        cfg.palette_name, cfg.palette_hexes)
    build_goodnotes_pdf(cfg, pngs)
    build_howto(cfg)
    preview_hero(cfg, showcase_colored_png)
    preview_included(cfg)
    preview_twoways(cfg, showcase_line_png, showcase_colored_png)
    print(f"[{cfg.prefix}] bundle iPad completo en {cfg.out_dir}")
