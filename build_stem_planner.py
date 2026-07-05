"""
build_stem_planner.py — STEM Focus Planner MVP (undated, hyperlinked)
=======================================================================
Genera un planificador digital sin fecha, orientado STEM, con navegación
hipervinculada para GoodNotes / Notability. Producto de prueba — pensado
para quedar como borrador en Etsy.

Salida en stem_planner/:
  STEM_Focus_Planner.pdf
  previews/stem_planner_preview_1_hero.jpg
  previews/stem_planner_preview_2_sections.jpg
  previews/stem_planner_preview_3_stem.jpg
  previews/stem_planner_preview_4_nav.jpg
"""

import os
import math

import fitz  # PyMuPDF

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "stem_planner")
PREV = os.path.join(OUT, "previews")
PDF_PATH = os.path.join(OUT, "STEM_Focus_Planner_v3.pdf")

# Landscape 4:3-ish (letter horizontal)
PW, PH = 792.0, 612.0

# Brand colours as fitz tuples (0–1)
GOLD = tuple(int(brand.GOLD[i:i+2], 16) / 255 for i in (1, 3, 5))
CREAM = tuple(int(brand.CREAM[i:i+2], 16) / 255 for i in (1, 3, 5))
NAVY = (0.07, 0.09, 0.18)
MUTED = (0.55, 0.57, 0.62)
LINE = (0.82, 0.82, 0.84)
GRID = (0.90, 0.90, 0.92)

SECTIONS = [
    ("Index", "index"),
    ("Yearly", "yearly"),
    ("Monthly", "monthly"),
    ("Weekly", "weekly"),
    ("Daily", "daily"),
    ("Research Log", "research"),
    ("Problem Cornell", "cornell"),
    ("Habit Grid", "habits"),
    ("Project Plan", "project"),
    ("Lab Notes", "lab"),
    ("Data Analysis", "data"),
    ("Literature Review", "litreview"),
    ("Meeting Notes", "meeting"),
    ("Graph Notes", "graph"),
    ("Dot Grid", "dotgrid"),
    ("Formula Reference", "formula"),
]


def _page_map():
    """Return ordered list of (label, kind) for every PDF page after index."""
    pages = []
    pages.append(("Yearly Overview", "yearly"))
    for i in range(6):
        pages.append((f"Monthly {i + 1}", "monthly"))
    for i in range(6):
        pages.append((f"Week {i + 1}", "weekly"))
    for i in range(10):
        pages.append((f"Day {i + 1}", "daily"))
    pages += [
        ("Research Log", "research"),
        ("Problem Cornell", "cornell"),
        ("Habit Grid", "habits"),
        ("Project Plan", "project"),
        ("Lab Notes", "lab"),
        ("Data Analysis", "data"),
        ("Literature Review", "litreview"),
        ("Meeting Notes", "meeting"),
        ("Graph Notes", "graph"),
        ("Dot Grid", "dotgrid"),
        ("Formula Reference", "formula"),
    ]
    return pages


def _header(page, title, subtitle=None):
    page.draw_rect(fitz.Rect(0, PH - 52, PW, PH), color=None, fill=NAVY)
    page.insert_textbox(fitz.Rect(24, PH - 44, PW - 24, PH - 10),
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


def _label(page, x, y, text, size=9, color=MUTED):
    page.insert_textbox(fitz.Rect(x, y, x + 200, y + 14), text,
                        fontsize=size, fontname="times-italic", color=color)


def _box(page, rect, label=None):
    page.draw_rect(rect, color=LINE, width=0.7)
    if label:
        _label(page, rect.x0 + 6, rect.y1 - 16, label, size=8)


def _grid(page, x0, y0, w, h, cols, rows, spacing):
    for c in range(cols + 1):
        x = x0 + c * spacing
        if x > x0 + w:
            break
        page.draw_line(fitz.Point(x, y0), fitz.Point(x, y0 + h), color=GRID, width=0.35)
    for r in range(rows + 1):
        y = y0 + r * spacing
        if y > y0 + h:
            break
        page.draw_line(fitz.Point(x0, y), fitz.Point(x0 + w, y), color=GRID, width=0.35)


def _draw_index(page, targets):
    # Header navy con decoración dorada
    page.draw_rect(fitz.Rect(0, PH - 120, PW, PH), color=None, fill=NAVY)

    # Línea decorativa dorada en el header
    page.draw_rect(fitz.Rect(0, PH - 120, PW, PH - 118), color=None, fill=GOLD)

    # Título principal elegante
    page.insert_textbox(fitz.Rect(0, PH - 105, PW, PH - 65),
                        "STEM Focus Planner", fontsize=30, fontname="times-bold",
                        color=CREAM, align=1)

    # Subtítulo \u2014 Unicode middle dot instead of HTML entity
    page.insert_textbox(fitz.Rect(0, PH - 58, PW, PH - 38),
                        "Undated \u00b7 Hyperlinked \u00b7 GoodNotes & Notability",
                        fontsize=10, fontname="times-italic", color=GOLD, align=1)

    # --- Grid de botones (3 columnas para 15 secciones) ---
    cols, gap = 3, 10
    btn_w = (PW - 72 - gap * (cols - 1)) / cols
    btn_h = 28
    row_gap = 8
    y_top = PH - 140  # top of first button row

    for i, (label, _kind) in enumerate(SECTIONS[1:], start=1):
        col = (i - 1) % cols
        row = (i - 1) // cols
        x = 36 + col * (btn_w + gap)
        y = y_top - row * (btn_h + row_gap)
        rect = fitz.Rect(x, y - btn_h, x + btn_w, y)

        # Sombra sutil
        page.draw_rect(fitz.Rect(x + 1.5, y - btn_h + 1.5, x + btn_w + 1.5, y + 1.5),
                        color=None, width=0, fill=(0.85, 0.85, 0.85))
        page.draw_rect(rect, color=GOLD, width=1.2, fill=(1, 1, 1))

        page.insert_textbox(rect, label, fontsize=10, fontname="times-bold",
                            color=NAVY, align=1)
        if i < len(targets):
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect,
                              "page": targets[i], "to": fitz.Point(0, 0)})

    # --- Features Card ---
    box_w = 480
    box_h = 200
    box_x = (PW - box_w) / 2
    box_y = 65

    # Card shadow
    page.draw_rect(fitz.Rect(box_x + 3, box_y + 3, box_x + box_w + 3, box_y + box_h + 3),
                   color=None, width=0, fill=(0.87, 0.86, 0.83))
    # Card background
    page.draw_rect(fitz.Rect(box_x, box_y, box_x + box_w, box_y + box_h),
                   color=GOLD, width=1, fill=(1, 1, 1))

    # Card Title
    page.insert_textbox(fitz.Rect(0, box_y + 20, PW, box_y + 45),
                        "S T E M   F O C U S   P L A N N E R", fontsize=14, fontname="times-bold",
                        color=NAVY, align=1)
    page.draw_line(fitz.Point(PW/2 - 40, box_y + 40), fitz.Point(PW/2 + 40, box_y + 40), color=GOLD, width=1)

    features = [
        "Six undated monthly spreads + six weekly + ten daily layouts",
        "Five STEM templates: research log, Cornell, habits, project, grids",
        "Four academic templates: lab notes, data analysis, lit review, meeting",
        "Formula reference page + 14 math stickers included",
        "Tap any button or side tab to navigate instantly",
    ]

    y = box_y + 60
    for feature in features:
        page.draw_circle(fitz.Point(PW/2 - 180, y + 6), 2.5, color=GOLD, fill=GOLD)
        page.insert_textbox(fitz.Rect(PW/2 - 162, y, PW, y + 20), feature,
                            fontsize=11, fontname="times-roman", color=NAVY)
        y += 24

    # Mensaje final
    page.insert_textbox(fitz.Rect(0, y + 6, PW, y + 26),
                        "Designed for analytical minds",
                        fontsize=10, fontname="times-italic", color=MUTED, align=1)

    _footer(page)


def _draw_monthly(page, n):
    _header(page, f"Monthly Overview  ·  Spread {n}", "undated")
    page.insert_textbox(fitz.Rect(36, PH - 88, 220, PH - 68), "Month:",
                        fontsize=11, fontname="times-bold", color=NAVY)
    page.draw_line(fitz.Point(100, PH - 72), fitz.Point(280, PH - 72), color=GOLD, width=1.2)

    cal_x, cal_y, cell = 36, 120, 34
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, d in enumerate(days):
        page.insert_textbox(fitz.Rect(cal_x + i * cell, PH - 108, cal_x + (i + 1) * cell, PH - 92),
                            d, fontsize=7, fontname="times-bold", color=MUTED, align=1)
    for r in range(5):
        for c in range(7):
            rect = fitz.Rect(cal_x + c * cell, cal_y + r * cell,
                             cal_x + (c + 1) * cell - 2, cal_y + (r + 1) * cell - 2)
            page.draw_rect(rect, color=GRID, width=0.5)
            page.draw_circle(fitz.Point(rect.x0 + 8, rect.y1 - 8), 2.5, color=GOLD, fill=GOLD)

    right_x = cal_x + 7 * cell + 24
    _label(page, right_x, PH - 108, "Monthly goals")
    _box(page, fitz.Rect(right_x, 280, PW - 36, PH - 118))
    _label(page, right_x, 260, "Key dates & deadlines")
    _box(page, fitz.Rect(right_x, 120, PW - 36, 250))
    _footer(page)


def _draw_weekly(page, n):
    _header(page, f"Weekly Plan  ·  Week {n}", "undated")
    cols = 7
    cw = (PW - 72 - 6 * 6) / cols
    y_top, y_bot = 130, PH - 130
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, d in enumerate(days):
        x = 36 + i * (cw + 6)
        page.insert_textbox(fitz.Rect(x, y_bot + 4, x + cw, y_bot + 18),
                            d, fontsize=8, fontname="times-bold", color=GOLD, align=1)
        _box(page, fitz.Rect(x, y_top, x + cw, y_bot))

    _label(page, 36, y_top - 22, "Weekly focus equation / theme")
    page.draw_line(fitz.Point(36, y_top - 8), fitz.Point(PW - 36, y_top - 8), color=GOLD, width=0.8)
    _label(page, 36, 92, "Notes & derivations")
    _box(page, fitz.Rect(36, 36, PW - 36, 86))
    _footer(page)


def _draw_daily(page, n):
    _header(page, f"Daily Focus  ·  Day {n}", "undated")
    page.insert_textbox(fitz.Rect(36, PH - 88, 120, PH - 68), "Date:",
                        fontsize=10, fontname="times-bold", color=NAVY)
    page.draw_line(fitz.Point(90, PH - 72), fitz.Point(220, PH - 72), color=GOLD, width=1)

    _label(page, 36, PH - 108, "Top 3 priorities")
    for i in range(3):
        y = PH - 128 - i * 18
        page.draw_circle(fitz.Point(44, y + 6), 4, color=GOLD, width=0.8)
        _hline(page, y, x0=56)

    left_w = 130
    t0 = 36
    for hour in range(6, 22):
        y = PH - 200 - (hour - 6) * 22
        if y < 40:
            break
        page.insert_textbox(fitz.Rect(36, y, 60, y + 14),
                            f"{hour:02d}:00", fontsize=7, color=MUTED)
        _hline(page, y + 10, x0=72, x1=36 + left_w)

    notes = fitz.Rect(36 + left_w + 16, 36, PW - 36, PH - 200)
    _box(page, notes, "Notes · sketches · equations")
    _grid(page, notes.x0 + 8, notes.y0 + 8, notes.width - 16, notes.height - 24, 24, 18, 14)
    _footer(page)


def _draw_research(page):
    _header(page, "Research Log", "STEM")
    fields = ["Title / topic", "Hypothesis", "Method", "Observations", "Results", "Next steps"]
    y = 60
    for f in fields:
        _label(page, 36, y, f)
        h = 48 if f in ("Observations", "Results") else 28
        _box(page, fitz.Rect(36, y + 16, PW - 36, y + 16 + h))
        y += h + 26
    _footer(page)


def _draw_cornell(page):
    _header(page, "Problem-Solving Cornell", "STEM")
    top = fitz.Rect(36, 60, PW - 36, 120)
    cue = fitz.Rect(36, 130, 200, PH - 130)
    notes = fitz.Rect(210, 130, PW - 36, PH - 130)
    summary = fitz.Rect(36, PH - 120, PW - 36, PH - 60)
    _box(page, top, "Problem statement / given data")
    _box(page, cue, "Cues \u00b7 formulas")
    _box(page, notes, "Work \u00b7 derivations")
    _box(page, summary, "Summary \u00b7 solution")
    _footer(page)


def _draw_habits(page):
    _header(page, "Habit Grid", "52 weeks \u00b7 undated")
    x0 = 60
    cw = (PW - 120) / 7
    y = 55
    for i, d in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        page.insert_textbox(fitz.Rect(x0 + i * cw, y, x0 + (i + 1) * cw, y + 10),
                            d, fontsize=8, fontname="times-bold", color=GOLD, align=1)
    y += 14
    for w in range(52):
        page.insert_textbox(fitz.Rect(36, y - 4, 52, y + 10),
                            f"W{w + 1}", fontsize=6, color=MUTED)
        for c in range(7):
            rect = fitz.Rect(x0 + c * cw + 1, y - 4, x0 + (c + 1) * cw - 1, y + 4)
            page.draw_rect(rect, color=GRID, width=0.4)
        y += 8.9  # spacing to fit 52 weeks
    _label(page, 36, PH - 50, "Fill a cell when the habit is done \u2014 track any metric, any year.")
    _footer(page)


def _draw_project(page):
    _header(page, "Project Planner", "STEM")
    _label(page, 36, PH - 88, "Project name")
    page.draw_line(fitz.Point(130, PH - 82), fitz.Point(PW - 36, PH - 82), color=GOLD, width=0.8)

    _label(page, 36, PH - 68, "Milestones")
    mx = 36
    for i in range(5):
        page.draw_circle(fitz.Point(mx + 8, PH - 54), 5, color=GOLD, fill=GOLD)
        page.insert_textbox(fitz.Rect(mx + 18, PH - 62, mx + 120, PH - 46),
                            f"M{i + 1}", fontsize=8, color=MUTED)
        if i < 4:
            page.draw_line(fitz.Point(mx + 120, PH - 54), fitz.Point(mx + 160, PH - 54), color=LINE, width=0.6)
        mx += 148

    col_w = (PW - 78) / 2
    _label(page, 36, PH - 36, "Tasks")
    _box(page, fitz.Rect(36, PH - 22, 36 + col_w, 130))
    _label(page, 36 + col_w + 6, PH - 36, "Resources & references")
    _box(page, fitz.Rect(36 + col_w + 6, PH - 22, PW - 36, 130))

    _label(page, 36, 112, "Notes")
    _box(page, fitz.Rect(36, 36, PW - 36, 108))
    _footer(page)


def _draw_graph(page):
    _header(page, "Graph Paper Notes", "STEM")
    _grid(page, 36, 36, PW - 72, PH - 100, 30, 22, 12)
    _footer(page)


def _draw_dotgrid(page):
    _header(page, "Dot Grid Notes", "STEM")
    x0, y0, sp = 40, 40, 16
    cols = int((PW - 80) / sp)
    rows = int((PH - 100) / sp)
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c * sp
            cy = y0 + r * sp
            page.draw_circle(fitz.Point(cx, cy), 1.2, color=GRID, fill=GRID)
    _footer(page)


def _draw_yearly(page):
    _header(page, "Yearly Overview", "undated")
    page.insert_textbox(fitz.Rect(36, PH - 88, 140, PH - 68), "Year:",
                        fontsize=11, fontname="times-bold", color=NAVY)
    page.draw_line(fitz.Point(90, PH - 72), fitz.Point(220, PH - 72), color=GOLD, width=1.2)
    
    # Quarterly breakdown
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    q_width = (PW - 72) / 4
    for i, q in enumerate(quarters):
        x = 36 + i * q_width
        page.insert_textbox(fitz.Rect(x, PH - 108, x + q_width, PH - 92),
                            q, fontsize=10, fontname="times-bold", color=GOLD, align=1)
        _box(page, fitz.Rect(x, 120, x + q_width - 6, PH - 118))
    
    _label(page, 36, 92, "Yearly goals & major milestones")
    _footer(page)


def _draw_lab(page):
    _header(page, "Lab Notes", "STEM")
    fields = ["Experiment title", "Objective", "Materials", "Procedure", "Data collected", "Analysis", "Conclusions"]
    y = 60  # start below footer (top of page)
    for f in fields:
        _label(page, 36, y, f)
        h = 50 if f in ("Procedure", "Data collected", "Analysis") else 30
        _box(page, fitz.Rect(36, y + 16, PW - 36, y + 16 + h))
        y += h + 26
    _footer(page)


def _draw_data(page):
    _header(page, "Data Analysis", "STEM")
    _label(page, 36, 60, "Dataset description")
    _box(page, fitz.Rect(36, 76, PW - 36, 106))

    _label(page, 36, 116, "Variables / parameters")
    _box(page, fitz.Rect(36, 132, PW - 36, 350))

    _label(page, 36, 360, "Observations & patterns")
    _box(page, fitz.Rect(36, 376, PW - 36, 440))

    _label(page, 36, 450, "Statistical analysis")
    _box(page, fitz.Rect(36, 466, PW - 36, PH - 60))
    _footer(page)


def _draw_litreview(page):
    _header(page, "Literature Review", "STEM")
    _label(page, 36, 60, "Paper / article title")
    _box(page, fitz.Rect(36, 76, PW - 36, 106))

    _label(page, 36, 116, "Authors & year")
    _box(page, fitz.Rect(36, 132, PW - 36, 156))

    _label(page, 36, 166, "Key findings")
    _box(page, fitz.Rect(36, 182, PW - 36, 340))

    _label(page, 36, 350, "Methodology")
    _box(page, fitz.Rect(36, 366, PW - 36, 460))

    _label(page, 36, 470, "Relevance to your research")
    _box(page, fitz.Rect(36, 486, PW - 36, PH - 60))
    _footer(page)


def _draw_meeting(page):
    _header(page, "Meeting Notes", "STEM")
    _label(page, 36, 60, "Date & time")
    _box(page, fitz.Rect(36, 76, 200, 106))

    _label(page, 220, 60, "Attendees")
    _box(page, fitz.Rect(220, 76, PW - 36, 106))

    _label(page, 36, 116, "Agenda items")
    _box(page, fitz.Rect(36, 132, PW - 36, 310))

    _label(page, 36, 320, "Discussion points")
    _box(page, fitz.Rect(36, 336, PW - 36, 440))

    _label(page, 36, 450, "Action items · deadlines")
    _box(page, fitz.Rect(36, 466, PW - 36, PH - 60))
    _footer(page)


def _draw_formula(page):
    _header(page, "Formula Reference", "STEM")
    categories = [
        ("Algebra", "Quadratic formula, factoring, exponents"),
        ("Calculus", "Derivatives, integrals, limits"),
        ("Trigonometry", "Identities, unit circle, laws"),
        ("Statistics", "Mean, variance, probability"),
        ("Physics", "Newton's laws, energy, waves"),
    ]

    y = 60  # start below footer bar (top of page)
    for cat, desc in categories:
        _label(page, 36, y, cat)
        page.insert_textbox(fitz.Rect(150, y, PW - 36, y + 14),
                            desc, fontsize=8, color=MUTED)
        _box(page, fitz.Rect(36, y + 16, PW - 36, y + 70))
        y += 82

    _label(page, 36, y, "Add your own formulas below")
    _box(page, fitz.Rect(36, y + 16, PW - 36, PH - 60))
    _footer(page)


DRAWERS = {
    "yearly": lambda p, _n: _draw_yearly(p),
    "monthly": _draw_monthly,
    "weekly": _draw_weekly,
    "daily": _draw_daily,
    "research": lambda p, _n: _draw_research(p),
    "cornell": lambda p, _n: _draw_cornell(p),
    "habits": lambda p, _n: _draw_habits(p),
    "project": lambda p, _n: _draw_project(p),
    "lab": lambda p, _n: _draw_lab(p),
    "data": lambda p, _n: _draw_data(p),
    "litreview": lambda p, _n: _draw_litreview(p),
    "meeting": lambda p, _n: _draw_meeting(p),
    "graph": lambda p, _n: _draw_graph(p),
    "dotgrid": lambda p, _n: _draw_dotgrid(p),
    "formula": lambda p, _n: _draw_formula(p),
}

def _draw_background(page, is_grid_page=False):
    page.draw_rect(page.rect, color=None, fill=CREAM)
    if not is_grid_page:
        grid_color = (0.94, 0.91, 0.86)  # Even lighter/more transparent look
        step = 32
        # Draw from below footer to above header (remember Y=0 is top)
        for x in range(0, int(PW), step):
            for y in range(30, int(PH - 55), step):
                page.draw_circle(fitz.Point(x, y), 0.7, color=grid_color, fill=grid_color)

def build_pdf():
    os.makedirs(OUT, exist_ok=True)
    content = _page_map()
    doc = fitz.open()
    # page 0 = index; pages 1.. = content
    for i in range(1 + len(content)):
        page = doc.new_page(width=PW, height=PH)
        is_grid = (i > 0 and content[i-1][1] in ("graph", "dotgrid"))
        _draw_background(page, is_grid)

    # Calculate section first pages dynamically
    section_first_page = {}
    current_page = 1
    for label, kind in content:
        if kind not in section_first_page:
            section_first_page[kind] = current_page
        current_page += 1

    # Index links: section button i -> page i (1-based in SECTIONS skips index itself)
    targets = [0] + [section_first_page.get(k, 1) for _, k in SECTIONS[1:]]
    _draw_index(doc[0], targets)

    counters = {"monthly": 0, "weekly": 0, "daily": 0}
    for i, (label, kind) in enumerate(content, start=1):
        page = doc[i]
        n = counters.get(kind, 0) + 1
        counters[kind] = n
        DRAWERS[kind](page, n)

    # Tab strip on every content page (left edge quick-nav back to index + sections)
    tab_abbrs = {
        "graph": "GRA", "dotgrid": "DOT", "formula": "FOR", "data": "DAT",
        "litreview": "LIT", "meeting": "MTG", "habits": "HAB", "project": "PRJ",
        "lab": "LAB", "research": "RES", "cornell": "COR", "yearly": "YRL",
        "monthly": "MON", "weekly": "WKL"
    }
    for i in range(1, len(content) + 1):
        page = doc[i]
        tab_h = 18
        tab_w = 24
        y = PH - 40
        for j, (slabel, kind) in enumerate(SECTIONS[1:]):
            rect = fitz.Rect(0, y - j * (tab_h + 2), tab_w, y - j * (tab_h + 2) + tab_h)
            page.draw_rect(rect, color=GOLD, fill=NAVY if j % 2 == 0 else (0.12, 0.14, 0.26))
            
            abbr = tab_abbrs.get(kind, kind[:3].upper())
            text_rect = fitz.Rect(0, rect.y0 + 3, tab_w, rect.y1)
            page.insert_textbox(text_rect, abbr, fontsize=7, fontname="times-bold", color=GOLD, align=1)
            
            tp = section_first_page.get(kind, 1)
            page.insert_link({"kind": fitz.LINK_GOTO, "from": rect,
                              "page": tp, "to": fitz.Point(0, 0)})
        # Home tab
        home = fitz.Rect(0, PH - 28, tab_w, PH - 8)
        page.draw_rect(home, color=CREAM, fill=(0, 0, 0))
        page.insert_textbox(fitz.Rect(0, home.y0 + 3, tab_w, home.y1), "IDX", fontsize=7, fontname="times-bold", color=CREAM, align=1)
        page.insert_link({"kind": fitz.LINK_GOTO, "from": home,
                          "page": 0, "to": fitz.Point(0, 0)})

    doc.save(PDF_PATH, deflate=True, garbage=4)
    doc.close()
    print(f"PDF -> {PDF_PATH}  ({1 + len(content)} pages)")


# ── Etsy preview images (iPad navy scaffold) ─────────────────────────────────
def _render_page_png(page_num, out_path):
    """Rasterize one PDF page for preview mockups."""
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(out_path)
    doc.close()


def _prev_hero(mock_png):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.35, "STEM Focus Planner", ha="center", fontsize=36,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.75, "Undated  \u00b7  Hyperlinked  \u00b7  iPad & GoodNotes",
            ha="center", fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    brand.ipad_frame(ax, 5, 4.85, 5.2, 3.9)
    img = mpimg.imread(mock_png)
    ax.imshow(img, extent=(2.0, 8.0, 3.2, 6.5), zorder=3, aspect="auto")
    ax.text(5, 1.15, "GoodNotes  \u00b7  Notability  \u00b7  Any PDF app",
            ha="center", fontsize=14, color=brand.IPAD_TEAL)
    brand.ipad_logo(ax, 5, 0.55, 1.5)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_1_hero.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def _prev_sections():
    fig, ax = brand.ipad_fig()
    ax.add_patch(plt.Rectangle((0, 9.85), 10, 0.15, color=brand.GOLD, zorder=2))
    ax.text(5, 9.1, "What's Inside", ha="center", fontsize=36,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.55, "35 hyperlinked pages  \u00b7  cream & gold aesthetic",
            ha="center", fontsize=13, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    items = [
        "6 monthly spreads + 6 weekly + 10 daily layouts",
        "Research log, Cornell notes & project planner",
        "Lab notes, data analysis & literature review",
        "52-week habit grid (any year)",
        "Formula reference + graph & dot grids",
        "14 mathematical stickers included",
        "Side-tab navigation on every page",
    ]
    y = 7.15
    for it in items:
        ax.add_patch(FancyBboxPatch((1.1, y - 0.28), 0.56, 0.56,
                     boxstyle="round,pad=0,rounding_size=0.1", facecolor="#1e2440",
                     edgecolor="none", zorder=2))
        ax.text(1.38, y, "\u2714", ha="center", va="center", fontsize=18, color=brand.GOLD, zorder=3)
        ax.text(2.0, y, it, ha="left", va="center", fontsize=14, color="#d7d9e2")
        y -= 0.88
    brand.ipad_logo(ax, 5, 0.6, 1.4)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_2_sections.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def _prev_stem(mock_research, mock_cornell):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.2, "Built for STEM Minds", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.65, "research \u00b7 derive \u00b7 track \u00b7 plan",
            ha="center", fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    brand.ipad_frame(ax, 3.2, 4.6, 3.6, 2.7)
    brand.ipad_frame(ax, 6.8, 4.6, 3.6, 2.7)
    img_r = mpimg.imread(mock_research)
    ax.imshow(img_r, extent=(1.3, 5.1, 3.35, 5.85), zorder=3, aspect="auto")
    img_c = mpimg.imread(mock_cornell)
    ax.imshow(img_c, extent=(4.9, 8.7, 3.35, 5.85), zorder=3, aspect="auto")
    ax.text(3.2, 2.85, "Research Log", ha="center", fontsize=15, color=brand.IPAD_TEAL, **brand.SERIF)
    ax.text(6.8, 2.85, "Cornell Notes", ha="center", fontsize=15, color=brand.IPAD_TEAL, **brand.SERIF)
    ax.text(5, 1.1, "MathRelaxing cream & gold aesthetic",
            ha="center", fontsize=13, color="#b9bccb")
    brand.ipad_logo(ax, 5, 0.55, 1.35)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_3_stem.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def _prev_nav():
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.15, "Tap to Navigate", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.6, "index buttons + side tabs on every page",
            ha="center", fontsize=13, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    tab_labels = ["MON", "WEE", "DAI", "RES", "COR", "HAB", "PRJ", "LAB"]
    tab_y_start = 7.4
    for i, lbl in enumerate(tab_labels):
        y = tab_y_start - i * 0.62
        ax.add_patch(FancyBboxPatch((0.35, y - 0.2), 0.9, 0.42,
                     boxstyle="round,pad=0,rounding_size=0.06",
                     facecolor=brand.GOLD if i % 2 == 0 else brand.IPAD_NAVY,
                     edgecolor=brand.GOLD, lw=1.2, zorder=2))
        ax.text(0.80, y, lbl, ha="center", va="center",
                fontsize=7, fontweight="bold",
                color=brand.CREAM if i % 2 else brand.GOLD, zorder=3)
    # Home tab
    ax.add_patch(FancyBboxPatch((0.35, tab_y_start - 8 * 0.62 - 0.2), 0.9, 0.42,
                 boxstyle="round,pad=0,rounding_size=0.06",
                 facecolor="black", edgecolor=brand.CREAM, lw=1.2, zorder=2))
    ax.text(0.80, tab_y_start - 8 * 0.62, "HOME", ha="center", va="center",
            fontsize=7, fontweight="bold", color=brand.CREAM, zorder=3)
    # Main content area
    ax.add_patch(FancyBboxPatch((1.6, 1.2), 7.2, 7.2,
                 boxstyle="round,pad=0,rounding_size=0.06", facecolor="white",
                 edgecolor="#3a3f52", lw=2, zorder=1))
    ax.text(5.2, 7.5, "STEM Focus Planner", ha="center", fontsize=18,
            color=brand.IPAD_NAVY, **brand.SERIF_BOLD)
    nav_items = ["Yearly", "Monthly", "Weekly", "Daily", "Research", "Cornell",
                 "Habits", "Project"]
    for j, txt in enumerate(nav_items):
        ax.add_patch(FancyBboxPatch((2.0, 6.6 - j * 0.65), 5.4, 0.48,
                     boxstyle="round,pad=0,rounding_size=0.04", facecolor="#f8f6f2",
                     edgecolor=brand.GOLD, lw=1, zorder=2))
        ax.text(4.7, 6.84 - j * 0.65, txt, ha="center", va="center",
                fontsize=11, color=brand.IPAD_NAVY, **brand.SERIF)
    brand.ipad_logo(ax, 5, 0.55, 1.35)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_4_nav.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)


def build_previews():
    os.makedirs(PREV, exist_ok=True)
    mock_index = os.path.join(PREV, "_mock_index.png")
    mock_research = os.path.join(PREV, "_mock_research.png")
    mock_cornell = os.path.join(PREV, "_mock_cornell.png")
    # page 0=index, 24=research, 25=cornell
    _render_page_png(0, mock_index)
    _render_page_png(24, mock_research)
    _render_page_png(25, mock_cornell)
    _prev_hero(mock_index)
    _prev_sections()
    _prev_stem(mock_research, mock_cornell)
    _prev_nav()
    print(f"Previews -> {PREV}/")


def main():
    build_pdf()
    build_previews()
    print("\nListo. Sube con:  python products_catalog.py upload stem_focus_planner")


if __name__ == "__main__":
    main()
