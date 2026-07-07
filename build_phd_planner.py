# /// script
# dependencies = [
#   "pymupdf==1.23.26",
#   "matplotlib",
# ]
# ///
"""
build_phd_planner.py — The PhD & Dissertation Planner (Academic Digital Planner)
================================================================================
Genera un planificador digital undated enfocado en el ciclo de vida completo
de un doctorado / tesis: roadmap plurianual con Gantt, tracker de progreso por
capitulo, log de lectura de papers (con cita + resumen), bitacora de reuniones
con director/comite, sprints semanales de investigacion, resumen mensual,
deadlines de conferencias/envios y prep de examen de calificacion + defensa.

Nicho validado via la API de Etsy: "phd planner digital" tiene solo ~189
listings activos pero el top (Ultimate PhD Planner Pack, $6.50) acumula 1.272
favs / ~39.7k vistas -> demanda real, poca oferta. Ninguno de los planners
actuales de MathRelaxing (life/stem_focus/stem_notebook/quantified_self) cubre
especificamente el ciclo doctoral.

Mismo motor/estilo que build_quantified_self.py (planner_framework.DigitalPlanner,
landscape 4:3, paleta navy/gold/cream de marca).

Salida en phd_planner/:
  PhD_Dissertation_Planner.pdf
  previews/...
"""

import os
import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import brand
from planner_framework import DigitalPlanner

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "phd_planner")
PREV = os.path.join(OUT, "previews")
PDF_PATH = os.path.join(OUT, "PhD_Dissertation_Planner.pdf")

# Landscape 4:3 (same as quantified_self / life planner)
PW, PH = 792.0, 612.0

# Brand palette (parsed from brand.py hex)
NAVY = (0.07, 0.09, 0.18)
GOLD = tuple(int(brand.GOLD[i:i+2], 16) / 255 for i in (1, 3, 5))
CREAM = tuple(int(brand.CREAM[i:i+2], 16) / 255 for i in (1, 3, 5))
MUTED = (0.55, 0.57, 0.62)
LINE = (0.82, 0.82, 0.84)
GRID = (0.90, 0.90, 0.92)
ACCENT = (0.2, 0.55, 0.62)  # muted teal, used sparingly for progress fills


# ─────────────────────────────────────────────────────────────────────────
# DRAWING UTILS  (shared visual language with build_quantified_self.py)
# ─────────────────────────────────────────────────────────────────────────
def _header(page, title, subtitle=None):
    page.draw_rect(fitz.Rect(0, PH - 52, PW, PH), color=None, fill=NAVY)
    page.insert_textbox(fitz.Rect(40, PH - 44, PW - 24, PH - 10),
                        title, fontsize=16, fontname="times-bold",
                        color=CREAM, align=0)
    if subtitle:
        page.insert_textbox(fitz.Rect(PW - 300, PH - 40, PW - 20, PH - 14),
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


def _label(page, x, y, text, size=9, color=MUTED, align=0, font="times-italic"):
    page.insert_textbox(fitz.Rect(x, y, x + 260, y + 14), text,
                        fontsize=size, fontname=font, color=color, align=align)


def _box(page, rect, label=None):
    page.draw_rect(rect, color=LINE, width=0.7)
    if label:
        # label sits in a small band at the top of the box
        page.draw_rect(fitz.Rect(rect.x0, rect.y1 - 20, rect.x1, rect.y1),
                       color=LINE, fill=GRID, width=0.5)
        page.insert_textbox(fitz.Rect(rect.x0 + 6, rect.y1 - 18, rect.x1 - 6, rect.y1 - 4),
                            label, fontsize=8, fontname="helv", color=NAVY, align=0)


def _checkbox(page, x, y, size=10):
    page.draw_rect(fitz.Rect(x, y, x + size, y + size), color=MUTED, width=0.7)


def draw_background(page, is_index):
    if not is_index:
        _footer(page)


# ─────────────────────────────────────────────────────────────────────────
# INDEX / DASHBOARD
# ─────────────────────────────────────────────────────────────────────────
def render_index(page, targets):
    page.draw_rect(fitz.Rect(0, PH - 158, PW, PH), color=None, fill=NAVY)
    page.draw_rect(fitz.Rect(0, PH - 158, PW, PH - 156), color=None, fill=GOLD)

    page.insert_textbox(fitz.Rect(0, PH - 150, PW, PH - 96),
                        "PhD & DISSERTATION PLANNER", fontsize=23, fontname="times-bold",
                        color=CREAM, align=1)
    page.insert_textbox(fitz.Rect(0, PH - 92, PW, PH - 64),
                        "AN UNDATED ACADEMIC PLANNER FROM PROPOSAL TO DEFENSE", fontsize=10,
                        fontname="times-italic", color=GOLD, align=1)

    _footer(page)

    sections_def = [
        ("roadmap", "Research Roadmap", "Multi-year Gantt of milestones (4 pages)"),
        ("chapters", "Chapter Progress", "Draft/revise status for every chapter"),
        ("reading", "Literature Log", "Paper citations, summaries & relevance"),
        ("meetings", "Advisor Meetings", "Agenda, decisions & action items"),
        ("weekly", "Weekly Research", "Priorities, writing goals & time blocks (52)"),
        ("monthly", "Monthly Overview", "Objectives & progress review (12)"),
        ("deadlines", "Conferences & Deadlines", "Submissions, travel & funding"),
        ("defense", "Exams & Defense", "Qualifying-exam & defense prep"),
        ("notes", "Research Notes", "Dot-grid pages for freeform notes"),
    ]

    x_col = [70, PW / 2 + 20]
    y_start = 120
    row_gap = 78

    for i, (key, title, desc) in enumerate(sections_def):
        col = i % 2
        row = i // 2
        x = x_col[col]
        y = y_start + row * row_gap

        rect = fitz.Rect(x, y - 26, x + 300, y + 30)
        page.draw_rect(rect, color=LINE, fill=(0.98, 0.98, 0.98), width=0.5)
        page.insert_textbox(fitz.Rect(x + 15, y - 24, x + 290, y + 0), title,
                            fontsize=12, fontname="times-bold", color=NAVY)
        page.insert_textbox(fitz.Rect(x + 15, y + 4, x + 290, y + 26), desc,
                            fontsize=8, fontname="helv", color=MUTED)
        if key in targets:
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect,
                              "page": targets[key], "to": fitz.Point(0, 0)})


# ─────────────────────────────────────────────────────────────────────────
# SECTIONS
# ─────────────────────────────────────────────────────────────────────────
def render_roadmap(page, index):
    _header(page, f"RESEARCH ROADMAP - YEAR {index}", "MILESTONE GANTT")

    phases = ["Coursework", "Literature Review", "Proposal / Prospectus",
              "Data Collection", "Analysis", "Writing", "Revisions", "Defense Prep"]
    # Gantt grid: rows = phases, cols = 12 months
    x0, y0 = 190, PH - 90
    row_h = (PH - 130 - 40) / len(phases)
    col_w = (PW - 60 - x0) / 12

    # month header
    for m in range(12):
        cx = x0 + m * col_w
        _vline(page, cx, 40, y0, color=GRID, width=0.4)
        page.insert_textbox(fitz.Rect(cx, y0 + 2, cx + col_w, y0 + 16),
                            f"M{m+1}", fontsize=7, fontname="helv", color=MUTED, align=1)
    _vline(page, x0 + 12 * col_w, 40, y0, color=GRID, width=0.4)

    for r, phase in enumerate(phases):
        ry = y0 - (r + 1) * row_h
        _hline(page, ry + row_h, x0, x0 + 12 * col_w, color=GRID, width=0.4)
        page.insert_textbox(fitz.Rect(40, ry + row_h / 2 - 7, x0 - 8, ry + row_h / 2 + 7),
                            phase, fontsize=8.5, fontname="times-roman", color=NAVY, align=2)
    _hline(page, y0, x0, x0 + 12 * col_w, color=GRID, width=0.4)
    _label(page, 40, 20, "Shade the months each phase is active. Mark key milestones with a star.",
           size=8)


def render_chapters(page, index):
    _header(page, "DISSERTATION CHAPTERS", "DRAFT & REVISION TRACKER")

    # Table: chapter | target words | draft | revised | to advisor | approved
    cols = ["Chapter / Section", "Target", "Draft", "Revised", "Sent", "Approved"]
    col_x = [40, 300, 380, 460, 540, 620, PW - 40]
    header_y = PH - 78
    page.draw_rect(fitz.Rect(40, header_y, PW - 40, header_y + 22), color=LINE, fill=GRID, width=0.5)
    for c, name in enumerate(cols):
        page.insert_textbox(fitz.Rect(col_x[c] + 4, header_y + 4, col_x[c + 1], header_y + 20),
                            name, fontsize=8.5, fontname="helv", color=NAVY,
                            align=0 if c == 0 else 1)

    rows = 14
    row_h = (header_y - 45) / rows
    for r in range(rows):
        ry = header_y - (r + 1) * row_h
        _hline(page, ry, 40, PW - 40, color=GRID, width=0.4)
        # checkbox columns (Draft, Revised, Sent, Approved -> cols 2..5)
        for c in range(2, 6):
            cx = (col_x[c] + col_x[c + 1]) / 2 - 5
            _checkbox(page, cx, ry + row_h / 2 - 5)
    for c in range(1, 6):
        _vline(page, col_x[c], 45, header_y, color=GRID, width=0.4)
    page.draw_rect(fitz.Rect(40, 45, PW - 40, header_y), color=LINE, width=0.7)


def render_reading(page, index):
    _header(page, f"LITERATURE LOG - {index}", "PAPERS & CITATIONS")

    # 3 paper cards per page
    n = 3
    gap = 10
    card_h = (PH - 100 - (n - 1) * gap) / n
    top = PH - 76
    for i in range(n):
        cy1 = top - i * (card_h + gap)
        cy0 = cy1 - card_h
        page.draw_rect(fitz.Rect(40, cy0, PW - 40, cy1), color=LINE, width=0.7)
        # citation line
        _label(page, 48, cy1 - 16, "Author(s), Year, Title, Journal / Venue:", size=8, color=NAVY)
        _hline(page, cy1 - 30, 52, PW - 52, color=GRID, width=0.5)
        # key finding / relevance
        _label(page, 48, cy1 - 44, "Key finding / relevance to my work:", size=8, color=NAVY)
        _hline(page, cy1 - 58, 52, PW - 52, color=GRID, width=0.5)
        _hline(page, cy1 - 74, 52, PW - 52, color=GRID, width=0.5)
        # tags + rating (draw the rating circles directly -- the base14 fonts
        # have no ○ glyph, so a literal "○ ○ ○" would render as "? ? ?")
        _label(page, 48, cy0 + 6, "Themes / tags:", size=8, color=MUTED)
        _label(page, PW - 250, cy0 + 6, "Relevance:", size=9, color=MUTED)
        for k in range(5):
            page.draw_circle(fitz.Point(PW - 185 + k * 16, cy0 + 13), 4,
                             color=MUTED, width=0.7)


def render_meetings(page, index):
    _header(page, f"ADVISOR MEETING - {index}", "AGENDA & ACTION ITEMS")

    _label(page, 40, PH - 74, "Date:", size=9, color=NAVY)
    _hline(page, PH - 78, 80, 260, color=GRID)
    _label(page, 290, PH - 74, "Attendees:", size=9, color=NAVY)
    _hline(page, PH - 78, 360, PW - 40, color=GRID)

    # Left: discussion / notes ; Right: action items + next meeting
    _box(page, fitz.Rect(40, 50, PW / 2 - 8, PH - 92), "DISCUSSION & FEEDBACK")
    for y in range(80, int(PH) - 110, 24):
        _hline(page, y, 50, PW / 2 - 18, color=GRID, width=0.5)

    _box(page, fitz.Rect(PW / 2 + 8, 150, PW - 40, PH - 92), "ACTION ITEMS (BEFORE NEXT MEETING)")
    for y in range(180, int(PH) - 110, 26):
        _checkbox(page, PW / 2 + 18, y)
        _hline(page, y + 4, PW / 2 + 34, PW - 52, color=GRID, width=0.5)

    _box(page, fitz.Rect(PW / 2 + 8, 50, PW - 40, 140), "DECISIONS & NEXT MEETING DATE")
    for y in range(74, 130, 24):
        _hline(page, y, PW / 2 + 18, PW - 52, color=GRID, width=0.5)


def render_weekly(page, index):
    _header(page, f"RESEARCH WEEK {index}", "PRIORITIES & WRITING GOALS")

    # Top 3 priorities
    _box(page, fitz.Rect(40, PH - 200, 300, PH - 78), "TOP 3 PRIORITIES THIS WEEK")
    for i in range(3):
        y = PH - 120 - i * 34
        _checkbox(page, 52, y)
        _hline(page, y + 4, 70, 288, color=GRID, width=0.5)

    # Writing goal tracker (words / day)
    _box(page, fitz.Rect(40, 50, 300, PH - 212), "DAILY WRITING TRACKER (WORDS)")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, d in enumerate(days):
        y = PH - 250 - i * 26
        _label(page, 52, y, d, size=9, color=NAVY)
        _hline(page, y - 2, 100, 288, color=GRID, width=0.5)

    # Right: 7-day task planner
    _box(page, fitz.Rect(320, 50, PW - 40, PH - 78), "WEEKLY RESEARCH TASKS")
    for i, d in enumerate(days):
        y = PH - 108 - i * 62
        _label(page, 332, y, d.upper(), size=9, color=ACCENT, font="helv")
        _hline(page, y - 6, 332, PW - 52, color=GRID, width=0.5)
        _hline(page, y - 26, 332, PW - 52, color=GRID, width=0.5)


def render_monthly(page, index):
    _header(page, f"MONTH {index} OVERVIEW", "OBJECTIVES & REVIEW")

    # Left: objectives
    _box(page, fitz.Rect(40, 50, 300, PH - 78), "OBJECTIVES THIS MONTH")
    for i in range(8):
        y = PH - 108 - i * 44
        _checkbox(page, 52, y)
        _hline(page, y + 4, 70, 288, color=GRID, width=0.5)

    # Right top: milestones hit
    _box(page, fitz.Rect(320, PH - 250, PW - 40, PH - 78), "MILESTONES REACHED")
    for y in range(int(PH) - 110, int(PH) - 245, -26):
        _checkbox(page, 332, y)
        _hline(page, y + 4, 348, PW - 52, color=GRID, width=0.5)

    # Right bottom: reflection
    _box(page, fitz.Rect(320, 50, PW - 40, PH - 262), "REVIEW: WHAT MOVED THE THESIS FORWARD?")
    for y in range(80, int(PH) - 285, 24):
        _hline(page, y, 332, PW - 52, color=GRID, width=0.5)


def render_deadlines(page, index):
    _header(page, "CONFERENCES & DEADLINES", "SUBMISSIONS · TRAVEL · FUNDING")

    cols = ["Event / Venue", "Type", "Deadline", "Submitted", "Status"]
    col_x = [40, 340, 470, 570, 660, PW - 40]
    header_y = PH - 78
    page.draw_rect(fitz.Rect(40, header_y, PW - 40, header_y + 22), color=LINE, fill=GRID, width=0.5)
    for c, name in enumerate(cols):
        page.insert_textbox(fitz.Rect(col_x[c] + 4, header_y + 4, col_x[c + 1], header_y + 20),
                            name, fontsize=8.5, fontname="helv", color=NAVY,
                            align=0 if c == 0 else 1)
    rows = 16
    row_h = (header_y - 45) / rows
    for r in range(rows):
        ry = header_y - (r + 1) * row_h
        _hline(page, ry, 40, PW - 40, color=GRID, width=0.4)
        cx = (col_x[3] + col_x[4]) / 2 - 5
        _checkbox(page, cx, ry + row_h / 2 - 5)
    for c in range(1, 5):
        _vline(page, col_x[c], 45, header_y, color=GRID, width=0.4)
    page.draw_rect(fitz.Rect(40, 45, PW - 40, header_y), color=LINE, width=0.7)


def render_defense(page, index):
    if index == 1:
        _header(page, "QUALIFYING / COMPREHENSIVE EXAM", "PREP CHECKLIST")
        _box(page, fitz.Rect(40, 50, PW / 2 - 8, PH - 78), "READING LIST & TOPICS")
        for y in range(80, int(PH) - 100, 24):
            _checkbox(page, 52, y)
            _hline(page, y + 4, 70, PW / 2 - 18, color=GRID, width=0.5)
        _box(page, fitz.Rect(PW / 2 + 8, 50, PW - 40, PH - 78), "LIKELY QUESTIONS & GAPS")
        for y in range(80, int(PH) - 100, 24):
            _hline(page, y, PW / 2 + 18, PW - 52, color=GRID, width=0.5)
    else:
        _header(page, "DISSERTATION DEFENSE", "FINAL PREP")
        _box(page, fitz.Rect(40, 50, PW / 2 - 8, PH - 78), "DEFENSE CHECKLIST")
        items = ["Committee scheduled", "Room / video link booked",
                 "Slides drafted", "Slides rehearsed (timed)", "Handouts printed",
                 "Anticipated questions prepared", "Forms submitted to grad school",
                 "Final formatting check", "Practice talk delivered"]
        for i, it in enumerate(items):
            y = PH - 100 - i * 30
            _checkbox(page, 52, y)
            _label(page, 70, y - 2, it, size=9, color=NAVY, font="times-roman")
        _box(page, fitz.Rect(PW / 2 + 8, 50, PW - 40, PH - 78), "ANTICIPATED QUESTIONS & ANSWERS")
        for y in range(80, int(PH) - 100, 24):
            _hline(page, y, PW / 2 + 18, PW - 52, color=GRID, width=0.5)


def render_notes(page, index):
    _header(page, f"RESEARCH NOTES {index}", "DOT GRID")
    for x in range(55, int(PW) - 45, 16):
        for y in range(45, int(PH) - 70, 16):
            page.draw_circle(fitz.Point(x, y), 0.5, color=MUTED, fill=MUTED)


# ─────────────────────────────────────────────────────────────────────────
# PREVIEWS
# ─────────────────────────────────────────────────────────────────────────
def _render_page_png(page_num, out_path):
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    pix = page.get_pixmap(dpi=150)
    pix.save(out_path)
    doc.close()


# section first-page indices (index page is 0). Derived from add_section order
# below: roadmap starts at 1. Kept as a dict so previews don't hard-code magic
# numbers that silently drift if section sizes change.
SECTION_START = {}


def _canvas():
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(brand.IPAD_NAVY)
    ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    return fig, ax


def _framed(ax, png, extent, lw=1.2):
    ax.imshow(mpimg.imread(png), extent=extent, zorder=3)
    x0, x1, y0, y1 = extent
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                               edgecolor=brand.GOLD, lw=lw, zorder=4))


def _two_up(out_name, title, left_png, right_png, sub=None):
    """Two page shots side by side under a title band — big and legible."""
    fig, ax = _canvas()
    ax.text(5, 7.35, title, ha="center", va="center", fontsize=22,
            color=brand.CREAM, **brand.SERIF)
    if sub:
        ax.text(5, 6.75, sub, ha="center", va="center", fontsize=12.5,
                color=brand.GOLD, **brand.SANS)
    # 4:3 page -> width/height = 1.29; height 4.0 -> width ~5.16 too wide for
    # two, so use height 3.6 -> width 4.65, gap between
    h = 3.7; w = h * (PW / PH)
    y0 = 1.9
    _framed(ax, left_png, [0.35, 0.35 + w, y0, y0 + h])
    _framed(ax, right_png, [9.65 - w, 9.65, y0, y0 + h])
    brand.ipad_logo(ax, 5, 1.0, 1.1)
    fig.savefig(os.path.join(PREV, out_name), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def _one_up(out_name, title, png, sub=None):
    """A single page shot, large and centered."""
    fig, ax = _canvas()
    ax.text(5, 7.35, title, ha="center", va="center", fontsize=22,
            color=brand.CREAM, **brand.SERIF)
    if sub:
        ax.text(5, 6.75, sub, ha="center", va="center", fontsize=12.5,
                color=brand.GOLD, **brand.SANS)
    h = 4.6; w = h * (PW / PH)
    _framed(ax, png, [5 - w / 2, 5 + w / 2, 1.55, 1.55 + h], lw=1.5)
    brand.ipad_logo(ax, 5, 0.85, 1.0)
    fig.savefig(os.path.join(PREV, out_name), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def build_previews():
    os.makedirs(PREV, exist_ok=True)

    # render every page we want to feature to a PNG mock
    mocks = {}
    for key, pnum in {
        "idx": 0,
        "road": SECTION_START["roadmap"],
        "chap": SECTION_START["chapters"],
        "read": SECTION_START["reading"],
        "mtg": SECTION_START["meetings"],
        "week": SECTION_START["weekly"],
        "mon": SECTION_START["monthly"],
        "dl": SECTION_START["deadlines"],
        "qual": SECTION_START["defense"],
        "def": SECTION_START["defense"] + 1,
        "note": SECTION_START["notes"],
    }.items():
        m = os.path.join(PREV, f"_{key}.png")
        _render_page_png(pnum, m)
        mocks[key] = m

    # 1. Hero (title + dashboard)
    fig, ax = _canvas()
    brand.ipad_logo(ax, 5, 1, 1.5)
    ax.text(5, 6.9, "PhD & DISSERTATION PLANNER", ha="center", va="center",
            fontsize=27, color=brand.CREAM, **brand.SERIF)
    ax.text(5, 6.4, "Undated Academic Planner for GoodNotes & Notability",
            ha="center", va="center", fontsize=15, color=brand.GOLD, **brand.SANS)
    _framed(ax, mocks["idx"], [2, 8, 2, 5.7], lw=2)
    fig.savefig(os.path.join(PREV, "phd_preview_1_hero.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

    # 2. "What's included" summary card — so the buyer sees the full scope
    fig, ax = _canvas()
    ax.text(5, 7.3, "136 HYPERLINKED PAGES", ha="center", va="center",
            fontsize=26, color=brand.CREAM, **brand.SERIF)
    ax.text(5, 6.75, "Everything from first proposal to final defense",
            ha="center", va="center", fontsize=13, color=brand.GOLD, **brand.SANS)
    rows = [
        ("Research Roadmap", "4 multi-year milestone Gantt charts"),
        ("Chapter Progress Tracker", "draft / revised / sent / approved"),
        ("Literature Log", "72 cards: citation, finding, relevance"),
        ("Advisor & Committee Log", "24 agenda + action-item logs"),
        ("Weekly Research Pages", "52 weeks: priorities & writing"),
        ("Monthly Overviews", "12 months: objectives & review"),
        ("Conferences & Deadlines", "submissions, travel & funding"),
        ("Exams & Defense Prep", "qualifying exam + defense list"),
        ("Research Notes", "12 dot-grid pages"),
    ]
    y = 5.85
    for name, desc in rows:
        ax.add_patch(plt.Rectangle((1.4, y - 0.06), 0.16, 0.16, color=brand.GOLD, zorder=3))
        ax.text(1.75, y + 0.02, name, ha="left", va="center", fontsize=12,
                color=brand.CREAM, **brand.SERIF)
        ax.text(6.0, y + 0.02, desc, ha="left", va="center", fontsize=10,
                color=(0.72, 0.74, 0.8), **brand.SANS)
        y -= 0.58
    brand.ipad_logo(ax, 5, 0.55, 1.0)
    fig.savefig(os.path.join(PREV, "phd_preview_2_included.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

    # 3..7 — each real section, big and legible
    _two_up("phd_preview_3_roadmap.jpg", "PLAN THE WHOLE JOURNEY",
            mocks["road"], mocks["chap"],
            sub="Multi-year roadmap  ·  chapter-by-chapter progress")
    _two_up("phd_preview_4_literature.jpg", "NEVER LOSE A PAPER AGAIN",
            mocks["read"], mocks["mtg"],
            sub="Literature log  ·  advisor meeting notes")
    _two_up("phd_preview_5_weekly.jpg", "STAY ON TRACK EVERY WEEK",
            mocks["week"], mocks["mon"],
            sub="Weekly research pages  ·  monthly review")
    _two_up("phd_preview_6_defense.jpg", "FROM DEADLINES TO DEFENSE",
            mocks["dl"], mocks["def"],
            sub="Conference deadlines  ·  defense checklist")

    # 8. Navigation & compatibility card
    fig, ax = _canvas()
    ax.text(5, 7.3, "TAP TO JUMP ANYWHERE", ha="center", va="center",
            fontsize=24, color=brand.CREAM, **brand.SERIF)
    ax.text(5, 6.75, "Every page is hyperlinked — side tabs on all 136 pages",
            ha="center", va="center", fontsize=12.5, color=brand.GOLD, **brand.SANS)
    _framed(ax, mocks["idx"], [1.2, 5.0, 2.7, 5.15])
    _framed(ax, mocks["note"], [5.2, 9.0, 2.7, 5.15])
    ax.text(5, 2.15, "Works in GoodNotes · Notability · Xodo · Penly · any PDF app",
            ha="center", va="center", fontsize=11.5, color=(0.72, 0.74, 0.8), **brand.SANS)
    ax.text(5, 1.75, "iPad · Android · Windows tablets   |   Undated — start any day",
            ha="center", va="center", fontsize=11.5, color=(0.72, 0.74, 0.8), **brand.SANS)
    brand.ipad_logo(ax, 5, 0.85, 1.0)
    fig.savefig(os.path.join(PREV, "phd_preview_7_navigation.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

    print(f"Previews creados en {PREV}/")


# ─────────────────────────────────────────────────────────────────────────
def build_pdf():
    os.makedirs(OUT, exist_ok=True)
    planner = DigitalPlanner(width=PW, height=PH, theme={
        "bg": (1, 1, 1),
        "tab_bg": NAVY,
        "tab_bg_alt": (0.1, 0.12, 0.22),
        "tab_text": CREAM,
        "home_bg": GOLD,
        "home_text": NAVY,
    })
    planner.set_background_renderer(draw_background)
    planner.set_index_renderer(render_index)

    sections = [
        ("roadmap", "MAP", 4, render_roadmap),
        ("chapters", "CHP", 2, render_chapters),
        ("reading", "LIT", 24, render_reading),
        ("meetings", "MTG", 24, render_meetings),
        ("weekly", "WK", 52, render_weekly),
        ("monthly", "MO", 12, render_monthly),
        ("deadlines", "DL", 3, render_deadlines),
        ("defense", "DEF", 2, render_defense),
        ("notes", "NTE", 12, render_notes),
    ]
    # record first-page indices for previews (index page = 0, sections follow)
    cur = 1
    for kind, abbr, n, renderer in sections:
        SECTION_START[kind] = cur
        cur += n
        planner.add_section(kind, abbr, n, renderer)

    planner.build(PDF_PATH)


def main():
    build_pdf()
    build_previews()
    print("\nCompletado. Ahora actualiza products_catalog.py y ejecuta "
          "python products_catalog.py upload phd_planner")


if __name__ == "__main__":
    main()
