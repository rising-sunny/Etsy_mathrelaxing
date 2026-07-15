"""
generate_lab_notebook.py — STEM Lab Notebook (printable + GoodNotes)
====================================================================
eRank pick: lab notebook printable — ~98 searches, ~55 competition, ~99% CTR.

Portrait US Letter (8.5x11 in). Hyperlinked index + side tabs for iPad apps.
PyMuPDF coords: origin top-left, y increases downward.

  python generate_lab_notebook.py
  python generate_lab_notebook.py --preview-only
"""
from __future__ import annotations

import argparse
import math
import os

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "lab_notebook")
PREV = os.path.join(OUT, "previews")
PDF_PATH = os.path.join(OUT, "STEM_Lab_Notebook.pdf")

# US Letter portrait (points) — origin top-left, y down
PW, PH = 612.0, 792.0

GOLD = tuple(int(brand.GOLD[i : i + 2], 16) / 255 for i in (1, 3, 5))
CREAM = tuple(int(brand.CREAM[i : i + 2], 16) / 255 for i in (1, 3, 5))
NAVY = (0.07, 0.09, 0.18)
INK = (0.12, 0.12, 0.14)
MUTED = (0.45, 0.46, 0.50)
LINE = (0.78, 0.78, 0.80)
GRID = (0.88, 0.88, 0.90)
SOFT = (0.96, 0.95, 0.93)

ML, MR = 40.0, 48.0  # right margin leaves room for side tabs
HEADER_H = 44.0
FOOTER_H = 28.0
CONTENT_TOP = HEADER_H + 12  # ~56
CONTENT_BOT = PH - FOOTER_H - 8  # ~756

PLAN = [
    ("cover", "Cover", 1, "cover"),
    ("index", "Index", 1, "index"),
    ("howto", "How to use", 1, "howto"),
    ("experiment", "Experiment log", 12, "experiment"),
    ("data", "Data table", 6, "data"),
    ("obs", "Observation sketch", 5, "observation"),
    ("graph", "Graph paper 5 mm", 5, "graph"),
    ("dot", "Dot grid", 3, "dot"),
    ("chem", "Chemistry notes", 3, "chem"),
    ("phys", "Physics notes", 3, "phys"),
    ("bio", "Biology notes", 3, "bio"),
    ("inventory", "Lab inventory", 2, "inventory"),
    ("lined", "Lined notes", 3, "lined"),
]


def _header(page, title: str, subtitle: str | None = None):
    page.draw_rect(fitz.Rect(0, 0, PW, HEADER_H), color=None, fill=NAVY)
    page.draw_rect(fitz.Rect(0, HEADER_H, PW, HEADER_H + 2), color=None, fill=GOLD)
    page.insert_textbox(
        fitz.Rect(ML, 10, PW - MR - 100, HEADER_H - 6),
        title,
        fontsize=13,
        fontname="times-bold",
        color=CREAM,
        align=0,
    )
    if subtitle:
        page.insert_textbox(
            fitz.Rect(PW - MR - 170, 14, PW - MR - 4, HEADER_H - 6),
            subtitle,
            fontsize=8,
            fontname="times-italic",
            color=GOLD,
            align=2,
        )


def _footer_min(page, page_num: int | None = None):
    y0 = PH - FOOTER_H
    page.draw_line(fitz.Point(ML, y0), fitz.Point(PW - MR, y0), color=LINE, width=0.5)
    page.insert_textbox(
        fitz.Rect(ML, y0 + 6, PW / 2, PH - 6),
        "MathRelaxing  |  STEM Lab Notebook",
        fontsize=7,
        fontname="helv",
        color=MUTED,
        align=0,
    )
    if page_num is not None:
        page.insert_textbox(
            fitz.Rect(PW / 2, y0 + 6, PW - MR, PH - 6),
            str(page_num),
            fontsize=7,
            fontname="helv",
            color=MUTED,
            align=2,
        )


def _field_line(page, x0, y, x1, label, label_w=70):
    """Horizontal fill-in line; y is baseline of the line."""
    page.insert_textbox(
        fitz.Rect(x0, y - 11, x0 + label_w, y + 3),
        label,
        fontsize=8,
        fontname="times-bold",
        color=NAVY,
        align=0,
    )
    page.draw_line(fitz.Point(x0 + label_w + 2, y), fitz.Point(x1, y), color=LINE, width=0.7)


def _box(page, rect, fill=None):
    page.draw_rect(rect, color=LINE, width=0.7, fill=fill)


def _ruled_area(page, rect, spacing=15):
    y = rect.y0 + spacing
    while y < rect.y1 - 3:
        page.draw_line(
            fitz.Point(rect.x0 + 4, y),
            fitz.Point(rect.x1 - 4, y),
            color=GRID,
            width=0.4,
        )
        y += spacing


def _graph(page, rect, mm=5.0):
    step = mm * 72 / 25.4
    x = rect.x0
    while x <= rect.x1 + 0.1:
        page.draw_line(fitz.Point(x, rect.y0), fitz.Point(x, rect.y1), color=GRID, width=0.35)
        x += step
    y = rect.y0
    while y <= rect.y1 + 0.1:
        page.draw_line(fitz.Point(rect.x0, y), fitz.Point(rect.x1, y), color=GRID, width=0.35)
        y += step
    page.draw_rect(rect, color=LINE, width=0.7)


def _dot_grid(page, rect, step=14):
    x = rect.x0 + step / 2
    while x < rect.x1:
        y = rect.y0 + step / 2
        while y < rect.y1:
            page.draw_circle(fitz.Point(x, y), 0.7, color=GRID, fill=GRID)
            y += step
        x += step
    page.draw_rect(rect, color=LINE, width=0.6)


def _checkbox(page, x, y, size=9):
    page.draw_rect(fitz.Rect(x, y, x + size, y + size), color=LINE, width=0.8)


def _section_label(page, x, y, text):
    # insert_text uses baseline; y is top of line box
    page.insert_text(
        fitz.Point(x, y + 10),
        text,
        fontsize=9,
        fontname="times-bold",
        color=NAVY,
    )


# ── Cover background motif ───────────────────────────────────────────────────

def _cover_motif(page):
    """Semi-transparent scientific design behind cover typography."""
    cx, cy = PW / 2, PH * 0.42
    # faint engineering grid
    step = 28
    for x in range(0, int(PW) + step, step):
        page.draw_line(
            fitz.Point(x, 50),
            fitz.Point(x, PH - 40),
            color=GOLD,
            width=0.35,
            stroke_opacity=0.07,
        )
    for y in range(50, int(PH) - 30, step):
        page.draw_line(
            fitz.Point(20, y),
            fitz.Point(PW - 20, y),
            color=GOLD,
            width=0.35,
            stroke_opacity=0.07,
        )

    # concentric orbital rings
    for r, op in ((70, 0.10), (110, 0.08), (155, 0.06), (210, 0.045)):
        page.draw_circle(
            fitz.Point(cx, cy),
            r,
            color=GOLD,
            width=0.9,
            stroke_opacity=op,
        )

    # molecule-like nodes + bonds (hexagonal benzene-ish + arms)
    nodes = []
    # central hexagon
    R = 48
    for i in range(6):
        a = math.pi / 6 + i * math.pi / 3
        nodes.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    # outer satellite atoms
    for i, (a, d) in enumerate(
        ((0.4, 95), (1.5, 100), (2.6, 90), (3.8, 105), (5.0, 92))
    ):
        nodes.append((cx + d * math.cos(a), cy + d * math.sin(a)))

    # bonds (faint)
    bonds = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),
        (0, 6), (2, 7), (3, 8), (4, 9), (5, 10),
    ]
    for i, j in bonds:
        if i < len(nodes) and j < len(nodes):
            page.draw_line(
                fitz.Point(*nodes[i]),
                fitz.Point(*nodes[j]),
                color=CREAM,
                width=1.1,
                stroke_opacity=0.10,
            )
    for x, y in nodes:
        page.draw_circle(
            fitz.Point(x, y),
            4.2,
            color=GOLD,
            fill=GOLD,
            width=0,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        page.draw_circle(
            fitz.Point(x, y),
            4.2,
            color=GOLD,
            width=0.7,
            stroke_opacity=0.18,
        )

    # corner flourishes (partial arcs)
    for (ox, oy, a0, a1) in (
        (40, 80, 0, 90),
        (PW - 40, 80, 90, 180),
        (40, PH - 60, 270, 360),
        (PW - 40, PH - 60, 180, 270),
    ):
        page.draw_circle(
            fitz.Point(ox, oy),
            55,
            color=GOLD,
            width=0.6,
            stroke_opacity=0.09,
        )


def _center_text(page, y, text, fontsize, fontname, color, opacity=1.0):
    tw = fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)
    # insert_text does not take opacity; use TextWriter for opacity when needed
    if opacity >= 0.99:
        page.insert_text(
            fitz.Point((PW - tw) / 2, y),
            text,
            fontsize=fontsize,
            fontname=fontname,
            color=color,
        )
    else:
        twr = fitz.TextWriter(page.rect, opacity=opacity)
        twr.append(
            fitz.Point((PW - tw) / 2, y),
            text,
            fontsize=fontsize,
            fontname=fontname,
        )
        twr.write_text(page, color=color)


# ── Pages ────────────────────────────────────────────────────────────────────

def draw_cover(page):
    page.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=NAVY)
    _cover_motif(page)

    # Soft vignette bands (top / bottom darken for text legibility)
    page.draw_rect(
        fitz.Rect(0, 0, PW, 120),
        color=None,
        fill=NAVY,
        fill_opacity=0.35,
    )
    page.draw_rect(
        fitz.Rect(0, PH - 100, PW, PH),
        color=None,
        fill=NAVY,
        fill_opacity=0.4,
    )

    # Logo band top
    page.draw_rect(fitz.Rect(0, 0, PW, 42), color=None, fill=(0, 0, 0))
    if os.path.exists(brand.LOGO_PATH):
        page.insert_image(
            fitz.Rect(PW / 2 - 55, 6, PW / 2 + 55, 36),
            filename=brand.LOGO_PATH,
            keep_proportion=True,
        )

    # Elegant serif title (times is a built-in PDF font)
    _center_text(page, 118, "STEM LAB", 36, "times-bold", CREAM)
    _center_text(page, 168, "NOTEBOOK", 36, "times-bold", CREAM)

    # Gold hairline + italic subtitle
    page.draw_line(
        fitz.Point(PW / 2 - 70, 188),
        fitz.Point(PW / 2 + 70, 188),
        color=GOLD,
        width=0.9,
    )
    _center_text(
        page, 210, "Printable  ·  GoodNotes  ·  Notability", 11, "times-italic", GOLD
    )

    # Motto card — double frame, refined
    box = fitz.Rect(PW / 2 - 115, 245, PW / 2 + 115, 348)
    page.draw_rect(box, color=GOLD, width=0.9, stroke_opacity=0.85)
    page.draw_rect(
        fitz.Rect(box.x0 + 5, box.y0 + 5, box.x1 - 5, box.y1 - 5),
        color=GOLD,
        width=0.45,
        stroke_opacity=0.55,
    )
    for i, line in enumerate(
        ["hypothesis", "experiment", "data  ·  insight"]
    ):
        _center_text(page, 278 + i * 24, line, 12, "times-italic", CREAM)

    # Feature list — serif, generous tracking feel
    features = [
        "Scientific method experiment logs",
        "Data tables, graph paper, observation pages",
        "Chemistry, Physics & Biology sections",
        "Hyperlinked index & side tabs for iPad",
        "Undated — reuse and duplicate forever",
    ]
    y = 400
    for f in features:
        page.draw_circle(
            fitz.Point(ML + 36, y + 2),
            2.0,
            color=GOLD,
            fill=GOLD,
            width=0,
        )
        page.insert_text(
            fitz.Point(ML + 52, y + 5),
            f,
            fontsize=11,
            fontname="times-roman",
            color=CREAM,
        )
        y += 30


def draw_index(page, targets: dict[str, int]):
    _header(page, "STEM Lab Notebook", "tap a section to jump")
    page.insert_textbox(
        fitz.Rect(ML, CONTENT_TOP, PW - MR, CONTENT_TOP + 28),
        "Contents",
        fontsize=18,
        fontname="times-bold",
        color=NAVY,
        align=0,
    )

    items = [(sid, lab, n) for sid, lab, n, _k in PLAN if sid not in ("cover", "index")]
    y = CONTENT_TOP + 40
    for i, (sid, lab, n) in enumerate(items):
        count_txt = f"{n} page{'s' if n != 1 else ''}"
        row = fitz.Rect(ML, y, PW - MR, y + 26)
        if i % 2 == 0:
            page.draw_rect(row, color=None, fill=SOFT)
        page.insert_textbox(
            fitz.Rect(ML + 10, y + 4, PW / 2 + 40, y + 22),
            lab,
            fontsize=11,
            fontname="times-bold",
            color=NAVY,
            align=0,
        )
        page.insert_textbox(
            fitz.Rect(PW / 2 + 40, y + 4, PW - MR - 10, y + 22),
            count_txt,
            fontsize=9,
            fontname="times-italic",
            color=MUTED,
            align=2,
        )
        if sid in targets:
            page.insert_link(
                {
                    "kind": fitz.LINK_GOTO,
                    "from": row,
                    "page": targets[sid],
                    "to": fitz.Point(0, 0),
                }
            )
        y += 28

    page.insert_textbox(
        fitz.Rect(ML, y + 20, PW - MR, y + 70),
        "Tip: In GoodNotes or Notability, tap any row above or a side tab to jump.\n"
        "Duplicate any page as many times as you need — the notebook is undated.",
        fontsize=9,
        fontname="times-italic",
        color=MUTED,
        align=0,
    )
    _footer_min(page)


def draw_howto(page):
    _header(page, "How to use", "a short guide")

    # Intro line
    page.insert_text(
        fitz.Point(ML, CONTENT_TOP + 18),
        "Five ways to get the most from this notebook.",
        fontsize=11,
        fontname="times-italic",
        color=MUTED,
    )
    # gold rule under intro
    page.draw_line(
        fitz.Point(ML, CONTENT_TOP + 28),
        fitz.Point(ML + 160, CONTENT_TOP + 28),
        color=GOLD,
        width=0.8,
    )

    blocks = [
        (
            "01",
            "Print",
            "Print on letter paper (8.5 × 11 in). Double-sided is optional. "
            "Three-hole punch or spiral-bind for a durable lab book.",
        ),
        (
            "02",
            "Digital on iPad",
            "Import the PDF into GoodNotes, Notability, or any PDF app. "
            "Tap the Index or side tabs to jump. Duplicate pages for each new run.",
        ),
        (
            "03",
            "Experiment log",
            "One full scientific-method template per page: title, date, hypothesis, "
            "materials, procedure, observations, data, conclusion, and next steps.",
        ),
        (
            "04",
            "Data & graph",
            "Use Data Table pages for raw numbers; graph paper for plots and sketches. "
            "Observation pages combine notes with drawing space.",
        ),
        (
            "05",
            "Subject sections",
            "Chemistry (structures + notes), Physics (equations + free-body space), "
            "and Biology (observation + diagram). Switch with the side tabs.",
        ),
    ]

    y = CONTENT_TOP + 48
    card_h = 108
    gap = 10
    for num, title, body in blocks:
        card = fitz.Rect(ML, y, PW - MR, y + card_h)
        # soft card background
        page.draw_rect(card, color=None, fill=SOFT)
        # left gold accent bar
        page.draw_rect(
            fitz.Rect(card.x0, card.y0, card.x0 + 3.5, card.y1),
            color=None,
            fill=GOLD,
        )
        # subtle outer rule
        page.draw_rect(card, color=LINE, width=0.45)

        # number
        page.insert_text(
            fitz.Point(card.x0 + 18, card.y0 + 28),
            num,
            fontsize=16,
            fontname="times-bold",
            color=GOLD,
        )
        # title
        page.insert_text(
            fitz.Point(card.x0 + 52, card.y0 + 28),
            title,
            fontsize=13,
            fontname="times-bold",
            color=NAVY,
        )
        # body
        page.insert_textbox(
            fitz.Rect(card.x0 + 18, card.y0 + 40, card.x1 - 16, card.y1 - 10),
            body,
            fontsize=10,
            fontname="times-roman",
            color=INK,
            align=0,
        )
        y += card_h + gap

    _footer_min(page)


def draw_experiment(page, n: int, page_num: int):
    _header(page, f"Experiment log  |  #{n}", "scientific method")
    y = CONTENT_TOP + 8
    _field_line(page, ML, y, PW / 2 - 8, "Title", 36)
    _field_line(page, PW / 2 + 8, y, PW - MR, "Date", 32)
    y += 22
    _field_line(page, ML, y, PW / 2 - 8, "Lab / course", 58)
    _field_line(page, PW / 2 + 8, y, PW - MR, "Partners", 48)
    y += 18

    # Remaining height for 6 sections
    avail = CONTENT_BOT - y - 4
    weights = [1.0, 1.0, 1.35, 1.1, 1.2, 1.0]
    total_w = sum(weights)
    label_h = 14
    gap = 6
    usable = avail - len(weights) * (label_h + gap)
    heights = [usable * w / total_w for w in weights]
    labels = [
        "1  Hypothesis / question",
        "2  Materials and equipment",
        "3  Procedure",
        "4  Observations",
        "5  Data / results",
        "6  Conclusion and next steps",
    ]
    for label, h in zip(labels, heights):
        _section_label(page, ML, y, label)
        y += label_h
        rect = fitz.Rect(ML, y, PW - MR, y + h)
        _box(page, rect)
        _ruled_area(page, rect, spacing=14)
        y = rect.y1 + gap
    _footer_min(page, page_num)


def draw_data(page, n: int, page_num: int):
    _header(page, f"Data table  |  #{n}", "record raw measurements")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Experiment / trial", 90)
    y += 22
    _field_line(page, ML, y, PW / 2 - 8, "Date", 32)
    _field_line(page, PW / 2 + 8, y, PW - MR, "Units", 36)
    y += 16

    table = fitz.Rect(ML, y, PW - MR, CONTENT_BOT)
    cols, rows = 6, 18
    cw = table.width / cols
    rh = table.height / rows
    page.draw_rect(
        fitz.Rect(table.x0, table.y0, table.x1, table.y0 + rh),
        color=None,
        fill=SOFT,
    )
    for c in range(cols + 1):
        x = table.x0 + c * cw
        page.draw_line(fitz.Point(x, table.y0), fitz.Point(x, table.y1), color=LINE, width=0.5)
    for r in range(rows + 1):
        yy = table.y0 + r * rh
        page.draw_line(fitz.Point(table.x0, yy), fitz.Point(table.x1, yy), color=LINE, width=0.5)
    headers = ["#", "Var A", "Var B", "Var C", "Var D", "Notes"]
    for c, name in enumerate(headers):
        page.insert_textbox(
            fitz.Rect(table.x0 + c * cw, table.y0 + 3, table.x0 + (c + 1) * cw, table.y0 + rh - 2),
            name,
            fontsize=7,
            fontname="times-bold",
            color=MUTED,
            align=1,
        )
    _footer_min(page, page_num)


def draw_observation(page, n: int, page_num: int):
    _header(page, f"Observation and sketch  |  #{n}", "see · note · draw")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Subject / sample", 80)
    y += 16
    mid = (y + CONTENT_BOT) / 2
    left = fitz.Rect(ML, y + 16, PW / 2 - 6, mid - 4)
    right = fitz.Rect(PW / 2 + 6, y + 16, PW - MR, mid - 4)
    bottom = fitz.Rect(ML, mid + 18, PW - MR, CONTENT_BOT)
    _section_label(page, left.x0, y, "Notes")
    _section_label(page, right.x0, y, "Sketch")
    _box(page, left)
    _ruled_area(page, left, 15)
    _graph(page, right, mm=5)
    _section_label(page, bottom.x0, mid + 2, "Additional observations / labels")
    _box(page, bottom)
    _ruled_area(page, bottom, 15)
    _footer_min(page, page_num)


def draw_graph_page(page, n: int, page_num: int):
    _header(page, f"Graph paper  |  5 mm  |  #{n}", "plot · design · calculate")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW / 2 - 8, "Title", 36)
    _field_line(page, PW / 2 + 8, y, PW - MR, "Date", 32)
    y += 14
    _graph(page, fitz.Rect(ML, y, PW - MR, CONTENT_BOT), mm=5)
    _footer_min(page, page_num)


def draw_dot_page(page, n: int, page_num: int):
    _header(page, f"Dot grid  |  #{n}", "flexible notes and diagrams")
    _dot_grid(page, fitz.Rect(ML, CONTENT_TOP + 4, PW - MR, CONTENT_BOT), step=14)
    _footer_min(page, page_num)


def draw_chem(page, n: int, page_num: int):
    _header(page, f"Chemistry notes  |  #{n}", "reactions · structures · yields")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Topic / reaction", 80)
    y += 14
    _section_label(page, ML, y, "Reaction / equation")
    y += 14
    eq = fitz.Rect(ML, y, PW - MR, y + 70)
    _box(page, eq, fill=SOFT)
    y = eq.y1 + 8
    left = fitz.Rect(ML, y + 14, PW / 2 - 6, CONTENT_BOT)
    right = fitz.Rect(PW / 2 + 6, y + 14, PW - MR, CONTENT_BOT)
    _section_label(page, left.x0, y, "Notes · conditions · safety")
    _section_label(page, right.x0, y, "Structure / mechanism sketch")
    _box(page, left)
    _ruled_area(page, left, 14)
    _graph(page, right, mm=5)
    _footer_min(page, page_num)


def draw_phys(page, n: int, page_num: int):
    _header(page, f"Physics notes  |  #{n}", "derive · measure · check units")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Topic / system", 80)
    y += 14
    mid = (y + CONTENT_BOT) / 2
    left = fitz.Rect(ML, y + 14, PW / 2 - 6, mid - 4)
    right = fitz.Rect(PW / 2 + 6, y + 14, PW - MR, mid - 4)
    bottom = fitz.Rect(ML, mid + 18, PW - MR, CONTENT_BOT)
    _section_label(page, left.x0, y, "Given / find / equations")
    _section_label(page, right.x0, y, "Free-body / diagram")
    _box(page, left)
    _ruled_area(page, left, 14)
    _graph(page, right, mm=5)
    _section_label(page, bottom.x0, mid + 2, "Worked solution · unit check · result")
    _box(page, bottom)
    _ruled_area(page, bottom, 14)
    _footer_min(page, page_num)


def draw_bio(page, n: int, page_num: int):
    _header(page, f"Biology notes  |  #{n}", "observe · classify · explain")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Organism / system / topic", 110)
    y += 14
    left = fitz.Rect(ML, y + 14, PW / 2 - 6, CONTENT_BOT)
    right = fitz.Rect(PW / 2 + 6, y + 14, PW - MR, CONTENT_BOT)
    _section_label(page, left.x0, y, "Notes · key terms · process")
    _section_label(page, right.x0, y, "Diagram / microscope sketch")
    _box(page, left)
    _ruled_area(page, left, 14)
    _graph(page, right, mm=5)
    _footer_min(page, page_num)


def draw_inventory(page, n: int, page_num: int):
    _header(page, f"Lab inventory and checklist  |  #{n}", "equipment · reagents · safety")
    y = CONTENT_TOP + 8
    page.insert_textbox(
        fitz.Rect(ML, y, PW - MR, y + 16),
        "Pre-lab safety checklist",
        fontsize=10,
        fontname="times-bold",
        color=NAVY,
    )
    y += 22
    items = [
        "Goggles / PPE available",
        "Fume hood / ventilation checked",
        "Spill kit / eyewash location known",
        "Waste disposal plan noted",
        "Equipment calibrated / zeroed",
    ]
    for it in items:
        _checkbox(page, ML, y)
        page.insert_textbox(
            fitz.Rect(ML + 16, y - 1, PW - MR, y + 12),
            it,
            fontsize=9,
            fontname="times-roman",
            color=INK,
        )
        y += 20

    y += 12
    page.insert_textbox(
        fitz.Rect(ML, y, PW - MR, y + 16),
        "Inventory log",
        fontsize=10,
        fontname="times-bold",
        color=NAVY,
    )
    y += 18
    table = fitz.Rect(ML, y, PW - MR, CONTENT_BOT)
    cols, rows = 4, 12
    cw, rh = table.width / cols, table.height / rows
    headers = ["Item", "Qty", "Location", "Notes"]
    page.draw_rect(
        fitz.Rect(table.x0, table.y0, table.x1, table.y0 + rh),
        color=None,
        fill=SOFT,
    )
    for c in range(cols + 1):
        x = table.x0 + c * cw
        page.draw_line(fitz.Point(x, table.y0), fitz.Point(x, table.y1), color=LINE, width=0.5)
    for r in range(rows + 1):
        yy = table.y0 + r * rh
        page.draw_line(fitz.Point(table.x0, yy), fitz.Point(table.x1, yy), color=LINE, width=0.5)
    for c, h in enumerate(headers):
        page.insert_textbox(
            fitz.Rect(table.x0 + c * cw, table.y0 + 3, table.x0 + (c + 1) * cw, table.y0 + rh - 2),
            h,
            fontsize=8,
            fontname="times-bold",
            color=MUTED,
            align=1,
        )
    _footer_min(page, page_num)


def draw_lined(page, n: int, page_num: int):
    _header(page, f"Lined notes  |  #{n}", "general lab notes")
    y = CONTENT_TOP + 10
    _field_line(page, ML, y, PW - MR, "Topic", 36)
    y += 12
    rect = fitz.Rect(ML, y, PW - MR, CONTENT_BOT)
    _box(page, rect)
    _ruled_area(page, rect, 18)
    _footer_min(page, page_num)


def draw_tabs(page, sections_first: list[tuple[str, int]], current_sid: str | None):
    tabs = [
        ("IDX", "index"),
        ("EXP", "experiment"),
        ("DAT", "data"),
        ("OBS", "obs"),
        ("GRP", "graph"),
        ("CHM", "chem"),
        ("PHY", "phys"),
        ("BIO", "bio"),
        ("INV", "inventory"),
    ]
    tab_w, tab_h, gap = 22, 28, 3
    y = HEADER_H + 20
    for abbr, sid in tabs:
        rect = fitz.Rect(PW - tab_w, y, PW - 1, y + tab_h)
        active = sid == current_sid
        fill = GOLD if active else NAVY
        text_c = NAVY if active else CREAM
        page.draw_rect(rect, color=None, fill=fill)
        page.insert_textbox(rect, abbr, fontsize=6, fontname="helv", color=text_c, align=1)
        target = next((p for s, p in sections_first if s == sid), None)
        if target is not None:
            page.insert_link(
                {
                    "kind": fitz.LINK_GOTO,
                    "from": rect,
                    "page": target,
                    "to": fitz.Point(0, 0),
                }
            )
        y += tab_h + gap


def build_pdf() -> str:
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open()

    pages_meta: list[tuple[str, str, str, int]] = []
    for sid, lab, count, kind in PLAN:
        for i in range(count):
            pages_meta.append((sid, lab, kind, i + 1))

    for _ in pages_meta:
        doc.new_page(width=PW, height=PH)

    section_first: dict[str, int] = {}
    for i, (sid, _lab, _kind, _n) in enumerate(pages_meta):
        if sid not in section_first:
            section_first[sid] = i
    sections_first_list = list(section_first.items())

    for i, (sid, lab, kind, n) in enumerate(pages_meta):
        page = doc[i]
        page_num = i + 1
        if kind == "cover":
            draw_cover(page)
        elif kind == "index":
            draw_index(page, section_first)
            draw_tabs(page, sections_first_list, "index")
        elif kind == "howto":
            draw_howto(page)
            draw_tabs(page, sections_first_list, None)
        elif kind == "experiment":
            draw_experiment(page, n, page_num)
            draw_tabs(page, sections_first_list, "experiment")
        elif kind == "data":
            draw_data(page, n, page_num)
            draw_tabs(page, sections_first_list, "data")
        elif kind == "observation":
            draw_observation(page, n, page_num)
            draw_tabs(page, sections_first_list, "obs")
        elif kind == "graph":
            draw_graph_page(page, n, page_num)
            draw_tabs(page, sections_first_list, "graph")
        elif kind == "dot":
            draw_dot_page(page, n, page_num)
            draw_tabs(page, sections_first_list, "graph")
        elif kind == "chem":
            draw_chem(page, n, page_num)
            draw_tabs(page, sections_first_list, "chem")
        elif kind == "phys":
            draw_phys(page, n, page_num)
            draw_tabs(page, sections_first_list, "phys")
        elif kind == "bio":
            draw_bio(page, n, page_num)
            draw_tabs(page, sections_first_list, "bio")
        elif kind == "inventory":
            draw_inventory(page, n, page_num)
            draw_tabs(page, sections_first_list, "inventory")
        elif kind == "lined":
            draw_lined(page, n, page_num)
            draw_tabs(page, sections_first_list, None)

    doc.save(PDF_PATH, deflate=True, garbage=4)
    n_pages = len(doc)
    doc.close()
    print(f"PDF: {PDF_PATH}  ({n_pages} pages)")
    return PDF_PATH


def _font(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"]
        if bold
        else ["georgia.ttf", "times.ttf", "arial.ttf"]
    )
    for n in names:
        path = os.path.join(windir, "Fonts", n)
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _pdf_page_to_image(pdf_path: str, page_index: int, zoom: float = 1.6) -> Image.Image:
    doc = fitz.open(pdf_path)
    page = doc[min(page_index, len(doc) - 1)]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def build_previews(pdf_path: str):
    os.makedirs(PREV, exist_ok=True)
    # layout: 0 cover, 1 index, 2 howto, 3..14 exp, 15..20 data, ...
    cover = _pdf_page_to_image(pdf_path, 0, zoom=1.9)
    exp = _pdf_page_to_image(pdf_path, 3, zoom=1.7)
    data = _pdf_page_to_image(pdf_path, 15, zoom=1.7)
    graph = _pdf_page_to_image(pdf_path, 26, zoom=1.7)
    chem = _pdf_page_to_image(pdf_path, 34, zoom=1.7)

    def save(img: Image.Image, name: str):
        path = os.path.join(PREV, name)
        img.convert("RGB").save(path, "JPEG", quality=90, optimize=True)
        print(f"  preview {path}")

    # 1 Hero square
    side = 1200
    hero = Image.new("RGB", (side, side), (18, 23, 46))
    c = cover.copy()
    c.thumbnail((int(side * 0.58), int(side * 0.72)), Image.Resampling.LANCZOS)
    hero.paste(c, ((side - c.width) // 2, int(side * 0.06)))
    draw = ImageDraw.Draw(hero)
    draw.rectangle([0, int(side * 0.80), side, side], fill=(18, 23, 46))
    # center titles roughly
    title = "STEM Lab Notebook"
    sub = "printable  |  GoodNotes  |  scientific method"
    # simple center using textbbox
    ft, fs = _font(40, bold=True), _font(20)
    bb = draw.textbbox((0, 0), title, font=ft)
    draw.text(((side - (bb[2] - bb[0])) // 2, int(side * 0.84)), title, font=ft, fill=(248, 244, 235))
    bb2 = draw.textbbox((0, 0), sub, font=fs)
    draw.text(((side - (bb2[2] - bb2[0])) // 2, int(side * 0.91)), sub, font=fs, fill=(201, 162, 75))
    save(hero, "lab_notebook_preview_1_hero.jpg")

    # 2 Pages
    spread = Image.new("RGB", (1400, 1000), (244, 241, 234))
    e = exp.copy()
    e.thumbnail((580, 780), Image.Resampling.LANCZOS)
    d = data.copy()
    d.thumbnail((580, 780), Image.Resampling.LANCZOS)
    spread.paste(e, (80, 100))
    spread.paste(d, (740, 100))
    dr = ImageDraw.Draw(spread)
    dr.text((80, 40), "inside the notebook", font=_font(28, bold=True), fill=(26, 26, 26))
    dr.text((80, 900), "Experiment log", font=_font(18), fill=(85, 85, 85))
    dr.text((740, 900), "Data table", font=_font(18), fill=(85, 85, 85))
    save(spread, "lab_notebook_preview_2_pages.jpg")

    # 3 Included
    card = Image.new("RGB", (1200, 1200), (244, 241, 234))
    mini = cover.copy()
    mini.thumbnail((480, 640), Image.Resampling.LANCZOS)
    card.paste(mini, (60, 200))
    dr = ImageDraw.Draw(card)
    dr.text((580, 180), "included", font=_font(36, bold=True), fill=(26, 26, 26))
    lines = [
        "48-page STEM Lab Notebook",
        "Scientific method experiment logs",
        "Data tables + observation pages",
        "5 mm graph paper + dot grid",
        "Chemistry, Physics, Biology",
        "Lab inventory checklist",
        "Hyperlinked index + side tabs",
        "Printable US Letter PDF",
        "GoodNotes and Notability ready",
        "",
        "Instant digital download",
    ]
    y = 260
    for line in lines:
        dr.text((580, y), line, font=_font(22), fill=(70, 70, 70))
        y += 42
    save(card, "lab_notebook_preview_3_included.jpg")

    # 4-6 full pages
    def save_page(img, name):
        w = 1000
        h = int(w * img.height / img.width)
        save(img.resize((w, h), Image.Resampling.LANCZOS), name)

    save_page(exp, "lab_notebook_preview_4_experiment.jpg")
    save_page(graph, "lab_notebook_preview_5_graph.jpg")
    save_page(chem, "lab_notebook_preview_6_chemistry.jpg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    args = ap.parse_args()
    print("=== STEM Lab Notebook ===")
    os.makedirs(OUT, exist_ok=True)
    if args.preview_only and os.path.isfile(PDF_PATH):
        pdf = PDF_PATH
    else:
        pdf = build_pdf()
    build_previews(pdf)
    print("done.")


if __name__ == "__main__":
    main()
