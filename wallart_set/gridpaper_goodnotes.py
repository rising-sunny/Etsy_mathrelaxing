"""
gridpaper_goodnotes.py — a hyperlinked GoodNotes/Notability notebook of the
Aesthetic Grid Paper: cover + contents + 10 tabbed sections. Every page carries
a right-edge tab strip; tapping a tab jumps to that section (real PDF GOTO
links, added with PyMuPDF). Pages are vector (crisp + tiny file).

    python gridpaper_goodnotes.py
"""
import io
import os
import math
import fitz
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyBboxPatch

import gridpaper as gp
import designs_geo

PAL = os.environ.get("GRIDPAPER_PALETTE", "earth")
EDITION = os.environ.get("GRIDPAPER_EDITION", PAL)
_feat = os.environ.get("GRIDPAPER_FEATURED")
gp.use_palette(PAL)
if _feat:
    gp.set_featured(*_feat.split("|"))

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", "gridpaper", EDITION)
os.makedirs(BASE, exist_ok=True)
SERIF = font_manager.FontProperties(family="DejaVu Serif")
PAPER, GRID, ACC, TXT = gp.PAPER, gp.GRID, gp.ACC, gp.TXT

W, H = gp.LETTER
PER = 4                                  # template pages per section
_ABBREV = {"Square Grid": "Square", "Dot Grid": "Dot", "Isometric": "Iso",
           "Triangular": "Tri", "Hexagonal": "Hex", "Ruled Notes": "Ruled",
           "Cornell Notes": "Cornell", "Penrose Grid": "Penrose", "Polar Grid": "Polar",
           "Sketch + Notes": "Sketch", "Flower of Life": "Flower", "Golden Spiral": "Spiral",
           "Maurer Rose": "Maurer", "Barnsley Fern": "Fern", "Sierpinski": "Sierp"}
TABS = [(lbl, _ABBREV.get(lbl, lbl.split()[0])) for lbl in gp.ORDER]
N = len(TABS)

# page index helpers
COVER, CONTENTS = 0, 1
def sec_start(i):                        # first page of section i
    return CONTENTS + 1 + i * PER


def _fig():
    fig = plt.figure(figsize=(W, H), dpi=100)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(PAPER); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    return fig, ax


def _pdf_bytes(fig):
    b = io.BytesIO(); fig.savefig(b, format="pdf", facecolor=PAPER)
    plt.close(fig); b.seek(0)
    return b.read()


# tab strip: returns list of (target_page, rect_inches) for link placement
TAB_X0, TAB_X1 = W - 0.60, W - 0.12
TOP = H - 1.2
BOT = 0.5


def draw_tabs(ax, active):
    links = []
    # contents tab at very top
    ch = 0.5
    _tab(ax, TOP, TOP - ch, "Contents", active=False, small=True)
    links.append((CONTENTS, (TAB_X0, TOP - ch, TAB_X1, TOP)))
    top2 = TOP - ch - 0.08
    th = (top2 - BOT) / N
    for i, (full, ab) in enumerate(TABS):
        y1 = top2 - i * th
        y0 = y1 - th + 0.06
        _tab(ax, y1, y0, ab, active=(i == active))
        links.append((sec_start(i), (TAB_X0, y0, TAB_X1, y1)))
    return links


def _tab(ax, y1, y0, label, active, small=False):
    fc = ACC if active else PAPER
    ec = ACC if active else GRID
    ax.add_patch(FancyBboxPatch((TAB_X0, y0), TAB_X1 - TAB_X0, y1 - y0,
                 boxstyle="round,pad=0.01,rounding_size=0.05", linewidth=0.8,
                 edgecolor=ec, facecolor=fc, mutation_aspect=1))
    ax.text((TAB_X0 + TAB_X1) / 2, (y0 + y1) / 2, label, ha="center", va="center",
            rotation=90, fontproperties=SERIF,
            fontsize=8 if not small else 7,
            color=("#fbf8f1" if active else TXT))


def page_grid(style, active, page_no):
    fig, ax = _fig()
    gp.header(ax, style, W, H)
    box = (gp.ML, TAB_X0 - 0.15, gp.MB, H - gp.MT)     # content clears the tabs
    gp.STYLES[style](ax, box)
    links = draw_tabs(ax, active)
    ax.text(gp.ML, 0.3, f"{page_no}", fontproperties=SERIF, fontsize=8, color=GRID)
    return _pdf_bytes(fig), links


def page_cover():
    fig, ax = _fig()
    designs_geo.use_palette("earth")
    _, xs, ys, circles, _ = designs_geo.data("flower")
    cx, cy, R = W / 2, H / 2 + 0.4, 2.4
    cs = np.array(circles); sc = R / cs[:, 2].max() * 0.32
    for x, y, r in circles:
        ax.add_patch(plt.Circle((cx + x * sc, cy + y * sc), r * sc, fill=False,
                                 edgecolor=GRID, lw=0.5, alpha=0.8))
    ax.text(W / 2, 2.6, "Aesthetic Grid Notebook", ha="center", fontproperties=SERIF,
            fontsize=30, color=TXT)
    ax.text(W / 2, 2.1, "Hyperlinked · 10 tabbed sections", ha="center",
            fontproperties=SERIF, fontsize=15, color=ACC)
    ax.text(W / 2, 0.9, "M A T H R E L A X I N G", ha="center", fontproperties=SERIF,
            fontsize=11, color=ACC)
    return _pdf_bytes(fig)


def page_contents():
    fig, ax = _fig()
    ax.text(W / 2, H - 1.3, "Contents", ha="center", fontproperties=SERIF,
            fontsize=26, color=TXT)
    links = []
    y = H - 2.4
    for i, (full, ab) in enumerate(TABS):
        ax.text(1.4, y, f"{i+1:>2}", fontproperties=SERIF, fontsize=15, color=ACC)
        ax.text(2.0, y, full, fontproperties=SERIF, fontsize=17, color="#4a463f")
        ax.plot([2.0, W - 1.4], [y - 0.12, y - 0.12], color=GRID, lw=0.5)
        links.append((sec_start(i), (1.2, y - 0.18, W - 1.2, y + 0.18)))
        y -= 0.62
    return _pdf_bytes(fig), links


def build():
    # pass 1: collect every page's (pdf_bytes, links) in order
    pages = [(page_cover(), [])]
    cbytes, clinks = page_contents()
    pages.append((cbytes, clinks))
    for i, (full, ab) in enumerate(TABS):
        for p in range(PER):
            pages.append(page_grid(full, i, p + 1))

    # pass 2a: create all pages, then 2b: add links (all targets now exist)
    doc = fitz.open()
    for pdf_bytes, _ in pages:
        src = fitz.open("pdf", pdf_bytes)
        page = doc.new_page(width=W * 72, height=H * 72)
        page.show_pdf_page(page.rect, src, 0)
    for pno, (_, links) in enumerate(pages):
        page = doc[pno]
        for target, (x0, y0, x1, y1) in links:
            rect = fitz.Rect(x0 * 72, (H - y1) * 72, x1 * 72, (H - y0) * 72)
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": target})

    out = os.path.join(BASE, f"AestheticGridNotebook_{EDITION}_GoodNotes.pdf")
    doc.save(out, deflate=True)
    doc.close()
    print(f"notebook: {out}  ({os.path.getsize(out)/1e6:.2f} MB, {COVER + CONTENTS + 1 + N*PER} pages)")
    return out


if __name__ == "__main__":
    out = build()
    # verify: render cover, contents, first section page to a montage
    doc = fitz.open(out)
    from PIL import Image
    thumbs = []
    for pno in (0, 1, 2, 6):
        pix = doc[pno].get_pixmap(dpi=90)
        thumbs.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    tw = 360
    thumbs = [t.resize((tw, int(t.height * tw / t.width))) for t in thumbs]
    th = thumbs[0].height
    sheet = Image.new("RGB", (4 * tw + 50, th + 20), "#fff")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (10 + i * (tw + 10), 10))
    sheet.save("/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/wallart/goodnotes_check.png")
    print("verify montage saved")
