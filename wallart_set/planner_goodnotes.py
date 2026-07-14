"""
planner_goodnotes.py — a fully hyperlinked digital planner for GoodNotes /
Notability / any PDF app. Undated (reusable every year). Every page carries a
right-edge month tab strip and a top nav; tapping jumps with real PDF GOTO
links (PyMuPDF). Pages are vector — crisp at any zoom, tiny file.

Structure (undated):
  cover · year-at-a-glance (12 mini calendars) · 12 monthly pages ·
  5 weekly pages per month (60) · 6 note pages (brand grid papers)

    python planner_goodnotes.py
"""
import io
import os
import fitz
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

import gridpaper as gp
import designs_geo

PAL = os.environ.get("PLANNER_PALETTE", "earth")
EDITION = os.environ.get("PLANNER_EDITION", PAL)
gp.use_palette(PAL)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", "planner", EDITION)
os.makedirs(BASE, exist_ok=True)
SERIF = font_manager.FontProperties(family="DejaVu Serif")
PAPER, GRID, ACC, TXT = gp.PAPER, gp.GRID, gp.ACC, gp.TXT

W, H = gp.LETTER
ML, MT, MB = 0.85, 1.15, 0.65           # content margins (right edge = tab strip)
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WKD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NWEEK = 5                                 # weekly pages per month

# ----- page-index map --------------------------------------------------------
COVER, YEAR, MONTH0 = 0, 1, 2
WEEK0 = MONTH0 + 12                       # 14
NOTES0 = WEEK0 + 12 * NWEEK               # 74
NOTE_STYLES = [s for s in ["Dot Grid", "Square Grid", "Cornell Notes",
                           "Ruled Notes", "Isometric", "Penrose Grid"]
               if s in gp.STYLES][:6]
NPAGES = NOTES0 + len(NOTE_STYLES)


def month_page(i):
    return MONTH0 + i


def week_page(i, w):
    return WEEK0 + i * NWEEK + w


def note_page(j):
    return NOTES0 + j


# ----- figure / pdf helpers --------------------------------------------------
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


# ----- right-edge month tab strip --------------------------------------------
TAB_X0, TAB_X1 = W - 0.58, W - 0.12
TAB_TOP, TAB_BOT = H - 1.05, 0.55


def draw_tabs(ax, active):
    """12 month tabs; returns [(target_page, rect_inches)]."""
    links = []
    th = (TAB_TOP - TAB_BOT) / 12
    for i in range(12):
        y1 = TAB_TOP - i * th
        y0 = y1 - th + 0.06
        act = (i == active)
        ax.add_patch(FancyBboxPatch((TAB_X0, y0), TAB_X1 - TAB_X0, y1 - y0,
                     boxstyle="round,pad=0.01,rounding_size=0.05", linewidth=0.8,
                     edgecolor=ACC if act else GRID, facecolor=ACC if act else PAPER))
        ax.text((TAB_X0 + TAB_X1) / 2, (y0 + y1) / 2, ABBR[i], ha="center", va="center",
                rotation=90, fontproperties=SERIF, fontsize=8,
                color="#fbf8f1" if act else TXT)
        links.append((month_page(i), (TAB_X0, y0, TAB_X1, y1)))
    return links


def top_nav(ax, back=None):
    """Right-aligned 'Year · Notes' (+ optional back link). Returns links."""
    links = []
    x = TAB_X0 - 0.15
    for label, target in [("Notes", NOTES0), ("Year", YEAR)]:
        ax.text(x, H - 0.62, label, ha="right", va="center", fontproperties=SERIF,
                fontsize=11, color=ACC)
        w = 0.62
        links.append((target, (x - w, H - 0.78, x, H - 0.46)))
        x -= (w + 0.2)
    if back is not None:
        tgt, txt = back
        ax.text(ML, H - 1.02, txt, ha="left", va="center", fontproperties=SERIF,
                fontsize=11, color=ACC)
        links.append((tgt, (ML - 0.05, H - 1.16, ML + 1.6, H - 0.88)))
    return links


# ----- calendar grid ---------------------------------------------------------
def calendar(ax, x0, x1, ytop, ybot, header=True, faint=False):
    cols, rows = 7, 6
    cw = (x1 - x0) / cols
    hh = 0.30 if header else 0.0
    gtop = ytop - hh
    ch = (gtop - ybot) / rows
    lc = GRID
    if header:
        for c in range(cols):
            ax.text(x0 + (c + 0.5) * cw, ytop - hh * 0.5, WKD[c] if cw > 0.35 else WKD[c][0],
                    ha="center", va="center", fontproperties=SERIF,
                    fontsize=9 if cw > 0.5 else 6, color=ACC)
    for r in range(rows + 1):
        y = gtop - r * ch
        ax.plot([x0, x1], [y, y], color=lc, lw=0.6)
    for c in range(cols + 1):
        x = x0 + c * cw
        ax.plot([x, x], [ybot, gtop], color=lc, lw=0.6)
    if not faint:                          # tiny date corner in each cell
        for r in range(rows):
            for c in range(cols):
                ax.text(x0 + c * cw + 0.06, gtop - r * ch - 0.06, "",
                        fontproperties=SERIF, fontsize=6, color=GRID, va="top")


# ----- pages -----------------------------------------------------------------
def page_cover():
    fig, ax = _fig()
    designs_geo.use_palette("earth")
    _, xs, ys, circles, _ = designs_geo.data("flower")
    cx, cy = W / 2, H / 2 + 0.6
    cs = np.array(circles); sc = 2.4 / cs[:, 2].max() * 0.34
    for x, y, r in circles:
        ax.add_patch(plt.Circle((cx + x * sc, cy + y * sc), r * sc, fill=False,
                                 edgecolor=GRID, lw=0.5, alpha=0.85))
    ax.text(W / 2, 3.0, "The Relaxing Planner", ha="center", fontproperties=SERIF,
            fontsize=32, color=TXT)
    ax.text(W / 2, 2.5, "Undated · Hyperlinked · GoodNotes & iPad", ha="center",
            fontproperties=SERIF, fontsize=14, color=ACC)
    # "open" button → year
    ax.add_patch(FancyBboxPatch((W / 2 - 0.9, 1.5), 1.8, 0.5,
                 boxstyle="round,pad=0.02,rounding_size=0.08", linewidth=1.0,
                 edgecolor=ACC, facecolor=PAPER))
    ax.text(W / 2, 1.75, "Open  ▸", ha="center", va="center", fontproperties=SERIF,
            fontsize=13, color=ACC)
    ax.text(W / 2, 0.8, "M A T H R E L A X I N G", ha="center", fontproperties=SERIF,
            fontsize=10, color=ACC)
    links = [(YEAR, (W / 2 - 0.9, 1.5, W / 2 + 0.9, 2.0))]
    return _pdf_bytes(fig), links


def page_year():
    fig, ax = _fig()
    ax.text(ML, H - 0.75, "Year at a Glance", fontproperties=SERIF, fontsize=24, color=TXT)
    ax.text(ML, H - 1.1, "20 ____", fontproperties=SERIF, fontsize=13, color=ACC)
    links = draw_tabs(ax, active=-1) + top_nav(ax)
    cols, rows = 3, 4
    gx0, gx1 = ML, TAB_X0 - 0.2
    gy0, gy1 = MB, H - 1.35
    cw = (gx1 - gx0) / cols
    chh = (gy1 - gy0) / rows
    for i in range(12):
        r, c = divmod(i, cols)
        bx = gx0 + c * cw
        by = gy1 - (r + 1) * chh
        pad = 0.14
        ax.text(bx + pad, by + chh - 0.16, MONTHS[i], fontproperties=SERIF,
                fontsize=11, color=ACC)
        calendar(ax, bx + pad, bx + cw - pad, by + chh - 0.34, by + pad,
                 header=False, faint=True)
        links.append((month_page(i), (bx, by, bx + cw, by + chh)))
    return _pdf_bytes(fig), links


def page_month(i):
    fig, ax = _fig()
    ax.text(ML, H - 0.72, MONTHS[i].upper(), fontproperties=SERIF, fontsize=26, color=TXT)
    ax.text(ML + 0.02, H - 1.02, "20 ____", fontproperties=SERIF, fontsize=12, color=ACC)
    links = draw_tabs(ax, active=i) + top_nav(ax)
    # calendar
    cal_top = H - 1.35
    cal_bot = 3.0
    calendar(ax, ML, TAB_X0 - 0.2, cal_top, cal_bot, header=True)
    # weekly buttons
    ax.text(ML, cal_bot - 0.4, "Weekly pages", fontproperties=SERIF, fontsize=12, color=TXT)
    bw = (TAB_X0 - 0.2 - ML - (NWEEK - 1) * 0.15) / NWEEK
    for w in range(NWEEK):
        bx = ML + w * (bw + 0.15)
        by = cal_bot - 1.15
        ax.add_patch(FancyBboxPatch((bx, by), bw, 0.55,
                     boxstyle="round,pad=0.02,rounding_size=0.06", linewidth=0.9,
                     edgecolor=ACC, facecolor=PAPER))
        ax.text(bx + bw / 2, by + 0.275, f"Week {w+1}", ha="center", va="center",
                fontproperties=SERIF, fontsize=11, color=ACC)
        links.append((week_page(i, w), (bx, by, bx + bw, by + 0.55)))
    # notes lines
    ax.text(ML, cal_bot - 1.5, "Notes & goals", fontproperties=SERIF, fontsize=12, color=TXT)
    for k in range(4):
        yy = cal_bot - 1.85 - k * 0.42
        ax.plot([ML, TAB_X0 - 0.2], [yy, yy], color=GRID, lw=0.6)
    return _pdf_bytes(fig), links


def page_week(i, w):
    fig, ax = _fig()
    ax.text(ML, H - 0.72, f"{MONTHS[i]} · Week {w+1}", fontproperties=SERIF,
            fontsize=20, color=TXT)
    links = draw_tabs(ax, active=i) + top_nav(ax, back=(month_page(i), "◂ " + ABBR[i]))
    # 7 day rows on the left, a to-do / notes column on the right
    day_x0 = ML
    day_x1 = TAB_X0 - 2.35
    col_x0 = day_x1 + 0.25
    col_x1 = TAB_X0 - 0.2
    top = H - 1.25
    bot = MB
    dh = (top - bot) / 7
    for d in range(7):
        y1 = top - d * dh
        y0 = y1 - dh
        ax.plot([day_x0, day_x1], [y0, y0], color=GRID, lw=0.6)
        ax.text(day_x0 + 0.04, y1 - 0.16, WKD[d], fontproperties=SERIF,
                fontsize=11, color=ACC)
        for ln in range(1, 3):             # faint writing lines
            yy = y1 - 0.16 - ln * ((dh - 0.2) / 3)
            ax.plot([day_x0 + 0.7, day_x1], [yy, yy], color=GRID, lw=0.4, alpha=0.7)
    ax.plot([day_x0, day_x1], [top, top], color=GRID, lw=0.6)
    # side column: priorities (checkboxes) then dot area
    ax.text(col_x0, top - 0.05, "Priorities", fontproperties=SERIF, fontsize=12, color=TXT)
    for k in range(5):
        yy = top - 0.45 - k * 0.4
        ax.add_patch(plt.Rectangle((col_x0, yy - 0.12), 0.16, 0.16, fill=False,
                     edgecolor=ACC, lw=0.8))
        ax.plot([col_x0 + 0.3, col_x1], [yy - 0.12, yy - 0.12], color=GRID, lw=0.5)
    ax.text(col_x0, top - 2.9, "Notes", fontproperties=SERIF, fontsize=12, color=TXT)
    # dot grid in the remaining side space
    dy0 = bot; dy1 = top - 3.2
    sp = 0.24
    yy = dy1
    while yy > dy0:
        xx = col_x0
        while xx < col_x1:
            ax.plot([xx], [yy], marker=".", ms=1.4, color=GRID)
            xx += sp
        yy -= sp
    return _pdf_bytes(fig), links


def page_note(j):
    style = NOTE_STYLES[j]
    fig, ax = _fig()
    gp.header(ax, style, W, H)
    box = (ML, TAB_X0 - 0.2, MB, H - MT)
    gp.STYLES[style](ax, box)
    links = draw_tabs(ax, active=-1) + top_nav(ax)
    return _pdf_bytes(fig), links


# ----- assemble --------------------------------------------------------------
def build():
    pages = [page_cover(), page_year()]
    for i in range(12):
        pages.append(page_month(i))
    for i in range(12):
        for w in range(NWEEK):
            pages.append(page_week(i, w))
    for j in range(len(NOTE_STYLES)):
        pages.append(page_note(j))
    assert len(pages) == NPAGES, (len(pages), NPAGES)

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

    out = os.path.join(BASE, f"RelaxingPlanner_{EDITION}_GoodNotes.pdf")
    doc.save(out, deflate=True)
    doc.close()
    print(f"planner: {out}  ({os.path.getsize(out)/1e6:.2f} MB, {NPAGES} pages)")
    return out


if __name__ == "__main__":
    out = build()
    from PIL import Image
    doc = fitz.open(out)
    picks = [COVER, YEAR, MONTH0, WEEK0, NOTES0]
    thumbs = []
    for pno in picks:
        pix = doc[pno].get_pixmap(dpi=90)
        thumbs.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    tw = 300
    thumbs = [t.resize((tw, int(t.height * tw / t.width))) for t in thumbs]
    th = thumbs[0].height
    sheet = Image.new("RGB", (len(thumbs) * (tw + 10) + 10, th + 20), "#fff")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (10 + i * (tw + 10), 10))
    p = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/planner_check.png"
    sheet.save(p)
    print("verify montage:", p)
