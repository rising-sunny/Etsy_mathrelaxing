# /// script
# dependencies = [
#   "pymupdf==1.23.26",
#   "matplotlib",
# ]
# ///
"""
build_quantified_self.py — The Quantified Self Journal (Data Analytics Planner)
=============================================================================
Genera un planificador digital enfocado en tracking de datos, gráficas
de hábitos, scatter plots y metodologías ágiles (sprints).

Salida en quantified_self/:
  Quantified_Self_Journal.pdf
  previews/...
"""

import os
import math
import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

import brand
from planner_framework import DigitalPlanner

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "quantified_self")
PREV = os.path.join(OUT, "previews")
PDF_PATH = os.path.join(OUT, "Quantified_Self_Journal.pdf")

# Landscape
PW, PH = 792.0, 612.0

# Colors
NAVY = (0.07, 0.09, 0.18)
GOLD = tuple(int(brand.GOLD[i:i+2], 16) / 255 for i in (1, 3, 5))
CREAM = tuple(int(brand.CREAM[i:i+2], 16) / 255 for i in (1, 3, 5))
MUTED = (0.55, 0.57, 0.62)
LINE = (0.82, 0.82, 0.84)
GRID = (0.90, 0.90, 0.92)
ACCENT = (0.2, 0.7, 0.7) # Muted teal for data graphs

# ─────────────────────────────────────────────────────────────────────────
# DRAWING UTILS
# ─────────────────────────────────────────────────────────────────────────
def _header(page, title, subtitle=None):
    page.draw_rect(fitz.Rect(0, PH - 52, PW, PH), color=None, fill=NAVY)
    page.insert_textbox(fitz.Rect(40, PH - 44, PW - 24, PH - 10),
                        title, fontsize=16, fontname="times-bold",
                        color=CREAM, align=0)
    if subtitle:
        page.insert_textbox(fitz.Rect(PW - 260, PH - 40, PW - 20, PH - 14),
                            subtitle, fontsize=9, fontname="times-italic",
                            color=GOLD, align=2)

def _footer(page):
    band = 28
    page.draw_rect(fitz.Rect(0, 0, PW, band), color=None, fill=(0, 0, 0))
    if os.path.exists(brand.LOGO_PATH):
        logo_h = band * 0.72
        page.insert_image(fitz.Rect(PW / 2 - 48, 3, PW / 2 + 48, 3 + logo_h),
                          filename=brand.LOGO_PATH, keep_proportion=True)
    page.insert_textbox(fitz.Rect(PW - 120, 6, PW - 12, 22),
                        brand.STORE, fontsize=7, color=MUTED, align=2)

def _hline(page, y, x0=36, x1=None, color=LINE, width=0.6):
    x1 = x1 or PW - 36
    page.draw_line(fitz.Point(x0, y), fitz.Point(x1, y), color=color, width=width)
    
def _vline(page, x, y0, y1, color=LINE, width=0.6):
    page.draw_line(fitz.Point(x, y0), fitz.Point(x, y1), color=color, width=width)

def _label(page, x, y, text, size=9, color=MUTED, align=0):
    page.insert_textbox(fitz.Rect(x, y, x + 200, y + 14), text,
                        fontsize=size, fontname="times-italic", color=color, align=align)

def _box(page, rect, label=None):
    page.draw_rect(rect, color=LINE, width=0.7)
    if label:
        _label(page, rect.x0 + 6, rect.y1 - 16, label, size=8)

def _grid(page, x0, y0, w, h, cols, rows, spacing):
    for c in range(cols + 1):
        x = x0 + c * spacing
        if x > x0 + w: break
        _vline(page, x, y0, y0 + h, color=GRID, width=0.35)
    for r in range(rows + 1):
        y = y0 + r * spacing
        if y > y0 + h: break
        _hline(page, y, x0, x0 + w, color=GRID, width=0.35)

def draw_background(page, is_index):
    if is_index:
        pass
    else:
        _footer(page)

# ─────────────────────────────────────────────────────────────────────────
# SECTIONS
# ─────────────────────────────────────────────────────────────────────────
def render_index(page, targets):
    page.draw_rect(fitz.Rect(0, PH - 158, PW, PH), color=None, fill=NAVY)
    page.draw_rect(fitz.Rect(0, PH - 158, PW, PH - 156), color=None, fill=GOLD)

    # Title/subtitle boxes sized >=2x fontsize tall so PyMuPDF actually renders them
    # (a shorter box silently drops the text instead of raising an error).
    page.insert_textbox(fitz.Rect(0, PH - 152, PW, PH - 94),
                        "THE QUANTIFIED SELF", fontsize=24, fontname="times-bold",
                        color=CREAM, align=1)
    page.insert_textbox(fitz.Rect(0, PH - 92, PW, PH - 64),
                        "A DATA-DRIVEN DIGITAL JOURNAL", fontsize=10, fontname="times-italic",
                        color=GOLD, align=1)

    _footer(page)

    # Sections links
    x_col = [80, PW/2 + 30]
    y_start = 130
    row_gap = 100

    sections_def = [
        ("yearly", "Yearly Heatmap Tracker", "365-day visualization of a core habit"),
        ("monthly", "Monthly Analytics", "Goals, scatter plots & bar charts (12 Months)"),
        ("weekly", "Weekly Sprints", "Agile Kanban boards and timeboxing (52 Weeks)"),
        ("daily", "Daily Logs", "Pomodoro trackers and detailed focus blocks (31 Days)"),
        ("data", "Data & Notes", "Isometric and dotted grids for freeform data")
    ]

    for i, (key, title, desc) in enumerate(sections_def):
        col = i % 2
        row = i // 2
        x = x_col[col]
        y = y_start + row * row_gap

        rect = fitz.Rect(x, y-28, x+300, y+38)
        page.draw_rect(rect, color=LINE, fill=(0.98, 0.98, 0.98), width=0.5)

        page.insert_textbox(fitz.Rect(x+15, y-26, x+290, y+4), title, fontsize=12, fontname="times-bold", color=NAVY)
        page.insert_textbox(fitz.Rect(x+15, y+8, x+290, y+34), desc, fontsize=8, fontname="helv", color=MUTED)

        if key in targets:
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": targets[key], "to": fitz.Point(0,0)})

def render_yearly(page, index):
    _header(page, "YEARLY HEATMAP", "365-DAY TRACKER")
    
    # Draw GitHub style contribution graph
    _label(page, 40, PH - 80, "CORE HABIT TRACKER (YEAR AT A GLANCE)", size=10, color=NAVY)
    
    x0, y0 = 40, PH - 250
    box_size = 10
    gap = 2
    spacing = box_size + gap

    # 52 weeks (cols) x 7 days (rows). box_size/gap sized so 53 columns from x0
    # fit inside the page width (PW=792) with margin to spare - the old 12/3
    # sizing ran the grid ~40pt past the right edge and clipped the last weeks.
    for w in range(53):
        for d in range(7):
            bx = x0 + w * spacing
            by = y0 - d * spacing
            page.draw_rect(fitz.Rect(bx, by, bx+box_size, by+box_size), color=LINE, width=0.5, fill=GRID)

    # Key
    kx, ky = x0 + 52*spacing + box_size + 30, y0 - 8*spacing
    _label(page, kx - 40, ky, "Intensity:")
    for i in range(5):
        page.draw_rect(fitz.Rect(kx + i*15, ky-2, kx + i*15 + 10, ky+8), color=LINE, width=0.5, fill=(0.9, 0.9, 0.9) if i==0 else (0.2+0.1*i, 0.7-0.1*i, 0.7-0.1*i))

def render_monthly(page, index):
    _header(page, f"MONTH {index} ANALYTICS", "DATA & GOALS")
    
    # Left Column: Goals & Metrics
    _box(page, fitz.Rect(40, 50, 300, PH - 80), "MONTHLY OKRs (Objectives & Key Results)")
    for y in range(90, int(PH) - 100, 32):
        _hline(page, y, 50, 290)

    # Right Column: Graphs
    # Bar chart area
    _box(page, fitz.Rect(320, PH - 250, PW - 40, PH - 80), "HABIT FREQUENCY (BAR CHART)")
    _grid(page, 340, PH-230, PW-400, 130, 10, 5, 26)

    # Scatter plot area (Sleep vs Mood) - x-axis along the bottom, y-axis on the
    # left, meeting at the bottom-left corner (a plain L, not the old inverted
    # layout that had the "x-axis" running along the top of the box).
    _box(page, fitz.Rect(320, 50, PW - 40, PH - 270), "SLEEP VS MOOD (SCATTER PLOT)")
    ax_x0, ax_x1 = 360, PW - 60
    ax_top, ax_bottom = 70, PH - 292
    _vline(page, ax_x0, ax_top, ax_bottom, color=NAVY, width=1)
    _hline(page, ax_bottom, ax_x0, ax_x1, color=NAVY, width=1)
    _label(page, ax_x0 + 5, ax_top - 2, "Mood (1-10)", size=8)
    _label(page, ax_x1 - 130, ax_bottom + 4, "Hours of Sleep ->", size=8)

def render_weekly(page, index):
    _header(page, f"SPRINT {index}", "WEEKLY KANBAN & TIMEBOXING")
    
    # Kanban Board
    _label(page, 40, PH - 80, "SPRINT BACKLOG / KANBAN", size=10, color=NAVY)
    col_w = (PW - 80) / 3
    header_h = 24
    for i, title in enumerate(["TO DO", "IN PROGRESS", "DONE"]):
        cx = 40 + i * col_w
        _box(page, fitz.Rect(cx, 50, cx + col_w - 10, PH - 90))
        # Column header band at the TOP of the column (the old version put this
        # strip at the bottom, and its 15pt height was too short for fontsize=9
        # text to render at all - both are fixed here).
        page.draw_rect(fitz.Rect(cx, 50, cx + col_w - 10, 50 + header_h), color=LINE, fill=GRID)
        page.insert_textbox(fitz.Rect(cx, 50, cx + col_w - 10, 50 + header_h), title,
                            fontsize=9, fontname="helv", color=NAVY, align=1)

        # Draw lines inside columns, below the header band
        for y in range(int(50 + header_h + 15), int(PH - 100), 25):
            _hline(page, y, cx + 5, cx + col_w - 15)

def render_daily(page, index):
    _header(page, f"DAILY LOG {index}", "POMODORO & FOCUS TRACKER")
    
    # Schedule - hours run 6:00 (top) -> 21:00 (bottom), chronological top-to-
    # bottom (the old formula listed them 21:00 -> 6:00, i.e. backwards).
    _box(page, fitz.Rect(40, 50, 250, PH - 80), "TIMEBOXING (HOURLY)")
    for i in range(16):
        y = 95 + i * 25
        _hline(page, y, 50, 240)
        _label(page, 55, y + 2, f"{i+6}:00")

    # Pomodoros
    _box(page, fitz.Rect(270, PH - 180, PW - 40, PH - 80), "POMODORO TRACKER (25min Blocks)")
    px, py = 290, PH - 120
    for row in range(3):
        for col in range(12):
            page.draw_rect(fitz.Rect(px + col*28, py - row*28, px + col*28 + 20, py - row*28 + 20), color=LINE, width=1, fill=GRID)

    # Metrics - listed top-to-bottom as Energy Level, Mood, Steps, Water, Deep
    # Work Hours, spread across the full box height instead of being crammed
    # into its bottom third.
    _box(page, fitz.Rect(270, 50, PW - 40, PH - 200), "DAILY METRICS & DATA ENTRY")
    metrics = ["Deep Work Hours", "Water (L)", "Steps / Exercise", "Mood (1-10)", "Energy Level"]
    n = len(metrics)
    for i, m in enumerate(metrics):
        my = 95 + (n - 1 - i) * 55
        _hline(page, my, 290, PW - 60)
        _label(page, 295, my + 4, m)

def render_data(page, index):
    _header(page, f"DATA & NOTES {index}", "ISOMETRIC & DOT GRID")
    
    # Split page: half isometric, half dot grid
    _box(page, fitz.Rect(40, 50, PW/2 - 10, PH - 80), "ISOMETRIC GRID")
    # Simulate isometric dots
    for x in range(50, int(PW/2) - 10, 20):
        for y in range(60, int(PH) - 90, 15):
            offset = 10 if (y//15)%2==0 else 0
            page.draw_circle(fitz.Point(x + offset, y), 0.5, color=MUTED, fill=MUTED)
            
    _box(page, fitz.Rect(PW/2 + 10, 50, PW - 40, PH - 80), "DOT GRID")
    for x in range(int(PW/2) + 25, int(PW) - 50, 15):
        for y in range(60, int(PH) - 90, 15):
            page.draw_circle(fitz.Point(x, y), 0.5, color=MUTED, fill=MUTED)

# ─────────────────────────────────────────────────────────────────────────
# PREVIEWS (using matplotlib)
# ─────────────────────────────────────────────────────────────────────────
def _render_page_png(page_num, out_path):
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    pix = page.get_pixmap(dpi=150)
    pix.save(out_path)
    doc.close()

def build_previews():
    os.makedirs(PREV, exist_ok=True)
    
    mock_idx = os.path.join(PREV, "_idx.png")
    mock_yer = os.path.join(PREV, "_yer.png")
    mock_mon = os.path.join(PREV, "_mon.png")
    mock_wek = os.path.join(PREV, "_wek.png")
    
    _render_page_png(0, mock_idx)
    _render_page_png(1, mock_yer)
    _render_page_png(3, mock_mon)
    _render_page_png(15, mock_wek)
    
    # 1. Hero
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(brand.IPAD_NAVY)
    ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 8)

    brand.ipad_logo(ax, 5, 1, 1.5)
    ax.text(5, 6.8, "THE QUANTIFIED SELF JOURNAL", ha="center", va="center", fontsize=28, color=brand.CREAM, **brand.SERIF)
    ax.text(5, 6.3, "Data-Driven Digital Planner for GoodNotes", ha="center", va="center", fontsize=16, color=brand.GOLD, **brand.SANS)
    
    img = mpimg.imread(mock_idx)
    ax.imshow(img, extent=[2, 8, 2, 5.5], zorder=3)
    ax.add_patch(plt.Rectangle((2, 2), 6, 3.5, fill=False, edgecolor=brand.GOLD, lw=2, zorder=4))
    
    fig.savefig(os.path.join(PREV, "qs_preview_1_hero.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)
    
    # 2. Analytics Pages
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(brand.IPAD_NAVY)
    ax.axis("off")
    # Without pinning the view, each unrelated imshow() call below re-fits the
    # axes to just that image (default aspect="equal" autoscale), so the final
    # view ended up matching only the LAST image drawn and everything else
    # (title text, first mockup, gold borders) fell outside it and vanished.
    ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    ax.text(5, 7.2, "DATA-DRIVEN TRACKING", ha="center", va="center", fontsize=24, color=brand.CREAM, **brand.SERIF)
    
    img_yer = mpimg.imread(mock_yer)
    ax.imshow(img_yer, extent=[1, 4.5, 2, 6], zorder=3)
    ax.add_patch(plt.Rectangle((1, 2), 3.5, 4, fill=False, edgecolor=brand.GOLD, lw=1, zorder=4))
    
    img_mon = mpimg.imread(mock_mon)
    ax.imshow(img_mon, extent=[5.5, 9, 2, 6], zorder=3)
    ax.add_patch(plt.Rectangle((5.5, 2), 3.5, 4, fill=False, edgecolor=brand.GOLD, lw=1, zorder=4))
    
    brand.ipad_logo(ax, 5, 1, 1.2)
    fig.savefig(os.path.join(PREV, "qs_preview_2_analytics.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

    # 3. Sprints
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(brand.IPAD_NAVY)
    ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    ax.text(5, 7.2, "AGILE SPRINT PLANNING", ha="center", va="center", fontsize=24, color=brand.CREAM, **brand.SERIF)
    
    img_wek = mpimg.imread(mock_wek)
    ax.imshow(img_wek, extent=[2, 8, 2, 6], zorder=3)
    ax.add_patch(plt.Rectangle((2, 2), 6, 4, fill=False, edgecolor=brand.GOLD, lw=1, zorder=4))
    
    brand.ipad_logo(ax, 5, 1, 1.2)
    fig.savefig(os.path.join(PREV, "qs_preview_3_sprints.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)
    
    print(f"Previews creados en {PREV}/")


def build_pdf():
    os.makedirs(OUT, exist_ok=True)
    planner = DigitalPlanner(width=PW, height=PH, theme={
        "bg": (1, 1, 1),
        "tab_bg": NAVY,
        "tab_bg_alt": (0.1, 0.12, 0.22),
        "tab_text": CREAM,
        "home_bg": GOLD,
        "home_text": NAVY
    })
    planner.set_background_renderer(draw_background)
    planner.set_index_renderer(render_index)
    planner.add_section("yearly", "YER", 1, render_yearly)
    planner.add_section("monthly", "MON", 12, render_monthly)
    planner.add_section("weekly", "WEK", 52, render_weekly)
    planner.add_section("daily", "DAY", 31, render_daily)
    planner.add_section("data", "DAT", 10, render_data)
    
    planner.build(PDF_PATH)

def main():
    build_pdf()
    build_previews()
    print("\nCompletado. Ahora actualiza products_catalog.py y ejecuta uv run products_catalog.py upload quantified_self_planner")

if __name__ == "__main__":
    main()
