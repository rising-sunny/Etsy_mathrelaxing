"""
generate_teacher_data_binder.py — STEM Teacher Data Binder (printable PDF)

Professional classroom organization pack with scientific-plate aesthetic.
Uses ReportLab (forms/tables) + Matplotlib/SciPy (cover art).

  python generate_teacher_data_binder.py
  python generate_teacher_data_binder.py --upload
"""
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "teacher_data_binder"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"

CREAM = HexColor("#F4F1EA")
INK = HexColor("#1A1A1A")
SUB = HexColor("#555555")
TEAL = HexColor("#1A7A8A")
LINE = HexColor("#C8C2B4")
GOLD = HexColor("#C9A24B")
RULE = HexColor("#B0A898")

# try register fonts
for name, path in [
    ("Georgia", r"C:\Windows\Fonts\georgia.ttf"),
    ("Georgia-Bold", r"C:\Windows\Fonts\georgiab.ttf"),
    ("Arial", r"C:\Windows\Fonts\arial.ttf"),
    ("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"),
]:
    if Path(path).is_file():
        try:
            pdfmetrics.registerFont(TTFont(name, path))
        except Exception:
            pass

SERIF = "Georgia" if "Georgia" in pdfmetrics.getRegisteredFontNames() else "Times-Roman"
SERIF_B = "Georgia-Bold" if "Georgia-Bold" in pdfmetrics.getRegisteredFontNames() else "Times-Bold"
SANS = "Arial" if "Arial" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
SANS_B = "Arial-Bold" if "Arial-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"


HEADER_BAND = HexColor("#E8F0F1")  # soft teal wash
HEADER_ROW = HexColor("#D5E6E8")

# Plate margin: outer frame sits here. Header band must stay strictly inside.
FRAME_M = 0.48 * inch
FRAME_GAP = 5  # pts between outer and inner frame lines


def _draw_frame(c, W, H, m=None):
    """Double plate frame + corner ticks. Draw LAST so nothing overpaints it."""
    m = FRAME_M if m is None else m
    c.setStrokeColor(LINE)
    c.setLineWidth(1.35)
    c.rect(m, m, W - 2 * m, H - 2 * m, fill=0, stroke=1)
    c.setLineWidth(0.55)
    c.rect(m + FRAME_GAP, m + FRAME_GAP, W - 2 * m - 2 * FRAME_GAP, H - 2 * m - 2 * FRAME_GAP, fill=0, stroke=1)
    # corner ticks (scientific plate detail) — sit on outer frame corners
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.1)
    tick = 11
    for cx, cy, dx, dy in [
        (m, H - m, 1, -1), (W - m, H - m, -1, -1),
        (m, m, 1, 1), (W - m, m, -1, 1),
    ]:
        c.line(cx, cy, cx + dx * tick, cy)
        c.line(cx, cy, cx, cy + dy * tick)


def _page_setup(c: canvas.Canvas, pagesize, draw_frame=True):
    """Cream background; optionally frame (cover pages). Content pages defer frame to _header."""
    W, H = pagesize
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    m = FRAME_M
    if draw_frame:
        _draw_frame(c, W, H, m)
    return W, H, m


def _header(c, W, H, title: str, subtitle: str = "", page_tag: str = "", m=None) -> float:
    """
    Title band INSIDE the inner plate frame, then frame on top so borders
    never get covered (fixes band bleeding past the double border).

    Returns y coordinate where page content should begin (below header rules).
    """
    m = FRAME_M if m is None else m
    # Inset from outer frame so band sits fully inside the INNER frame line
    inset = m + FRAME_GAP + 1.5
    band_top = H - inset
    band_h = 0.62 * inch
    band_bot = band_top - band_h
    c.setFillColor(HEADER_BAND)
    c.rect(inset, band_bot, W - 2 * inset, band_h, fill=1, stroke=0)

    # Title + subtitle centered in the band
    c.setFillColor(INK)
    c.setFont(SERIF_B, 12.5)
    title_y = band_top - 0.24 * inch
    c.drawCentredString(W / 2, title_y, title)
    if subtitle:
        c.setFillColor(TEAL)
        c.setFont(SANS, 7.5)
        c.drawCentredString(W / 2, title_y - 0.17 * inch, subtitle)

    # Teal + hairline rules just under the band (still inside plate)
    rule_y = band_bot - 0.05 * inch
    rule_x0 = inset + 0.12 * inch
    rule_x1 = W - inset - 0.12 * inch
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.4)
    c.line(rule_x0, rule_y, rule_x1, rule_y)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(rule_x0, rule_y - 3.0, rule_x1, rule_y - 3.0)

    if page_tag:
        c.setFillColor(SUB)
        c.setFont(SANS, 6.5)
        # keep tag inside the band, clear of the corner tick
        c.drawRightString(W - inset - 6, band_top - 11, page_tag)

    # Frame last — clean double border over the band edges
    _draw_frame(c, W, H, m)

    # Content starts below the double rule with a small breathing gap
    content_top = rule_y - 3.0 - 0.18 * inch
    return content_top


def _label_line(c, x, y, w, label: str, gap=13):
    """Label above a generous write-on underline."""
    c.setFillColor(SUB)
    c.setFont(SANS_B, 7)
    c.drawString(x, y + gap, label)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.95)
    c.line(x, y, x + w, y)
    return y - 30


def _section_box(c, x, y, w, h, title: str):
    """y = top of box; returns bottom y. Title sits on a soft header strip."""
    c.setStrokeColor(LINE)
    c.setLineWidth(0.95)
    c.rect(x, y - h, w, h, fill=0, stroke=1)
    # title strip
    strip_h = 16
    c.setFillColor(HEADER_BAND)
    c.rect(x + 0.5, y - strip_h, w - 1, strip_h - 0.5, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.setFont(SANS_B, 7.5)
    c.drawString(x + 8, y - 11, title)
    return y - h


def _ruled(c, x, y_top, w, y_bot, spacing=16):
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    y = y_top
    while y > y_bot:
        c.line(x, y, x + w, y)
        y -= spacing


def _table(c, x, y, col_ws, rows, row_h=16, header=None, number_rows=False):
    """Draw polished table; y is TOP. Returns bottom y."""
    total_w = sum(col_ws)
    n = rows + (1 if header else 0)
    # header fill
    if header:
        c.setFillColor(HEADER_ROW)
        c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
    # subtle zebra rows
    c.setFillColor(HexColor("#F9F7F2"))
    start = 1 if header else 0
    for i in range(start, n):
        if (i - start) % 2 == 1:
            c.rect(x, y - (i + 1) * row_h, total_w, row_h, fill=1, stroke=0)
    # outer + grid
    c.setStrokeColor(LINE)
    c.setLineWidth(0.85)
    c.rect(x, y - n * row_h, total_w, n * row_h, fill=0, stroke=1)
    c.setLineWidth(0.45)
    for i in range(1, n):
        yy = y - i * row_h
        c.line(x, yy, x + total_w, yy)
    xx = x
    for w in col_ws[:-1]:
        xx += w
        c.line(xx, y, xx, y - n * row_h)
    if header:
        c.setFillColor(TEAL)
        c.setFont(SANS_B, 7)
        xx = x
        for i, h in enumerate(header):
            c.drawString(xx + 4, y - row_h + 5, h)
            xx += col_ws[i]
    if number_rows:
        c.setFillColor(SUB)
        c.setFont(SANS, 6.5)
        for i in range(rows):
            yy = y - (1 if header else 0) * row_h - (i + 1) * row_h + 5
            c.drawCentredString(x + col_ws[0] / 2, yy, str(i + 1))
    return y - n * row_h


# ── Cover art (matplotlib + numpy) ───────────────────────────────────────────

def make_cover_png(pagesize_name: str, out_path: Path):
    W_in, H_in = (8.5, 11.0) if pagesize_name == "letter" else (8.27, 11.69)
    fig = plt.figure(figsize=(W_in, H_in), dpi=200)
    fig.patch.set_facecolor("#F4F1EA")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("#F4F1EA")
    ax.add_patch(plt.Rectangle((0.05, 0.05), 0.90, 0.90, fill=False, ec="#C8C2B4", lw=1.4))

    # subtle network / graph motif (classroom connections)
    rng = np.random.default_rng(7)
    n = 18
    pts = rng.uniform(0.2, 0.8, size=(n, 2))
    pts[:, 1] = pts[:, 1] * 0.35 + 0.40  # cluster mid-upper
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(pts[i] - pts[j]) < 0.18:
                ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]],
                        color="#1A7A8A", lw=0.7, alpha=0.35)
    ax.scatter(pts[:, 0], pts[:, 1], s=18, c="#1A7A8A", alpha=0.7, zorder=3)

    ax.text(0.5, 0.82, "TEACHER DATA BINDER", ha="center", va="center",
            fontsize=18, fontfamily="serif", fontweight="bold", color="#1A1A1A")
    ax.text(0.5, 0.76, "STEM  ·  CLASSROOM ORGANIZATION  ·  2026–2027",
            ha="center", fontsize=9, color="#1A7A8A")
    ax.plot([0.25, 0.75], [0.72, 0.72], color="#C8C2B4", lw=1.0)

    items = [
        "Roster 24-student + Roster 32-student",
        "Attendance 24 + 32 students",
        "Grade / assignment logs",
        "Parent communication",
        "Behavior & conference notes",
        "Standards / accommodations",
        "Seating chart & weekly plan",
    ]
    y = 0.38
    for it in items:
        ax.text(0.5, y, f"·  {it}", ha="center", fontsize=10, color="#1A1A1A", fontfamily="serif")
        y -= 0.045

    ax.text(0.5, 0.10, "Printable PDF  ·  US Letter & A4", ha="center", fontsize=8, color="#555555")
    fig.savefig(out_path, dpi=200, facecolor="#F4F1EA")
    plt.close(fig)


# ── PDF pages ────────────────────────────────────────────────────────────────

def page_cover_pdf(c, pagesize, label="US Letter"):
    W, H, m = _page_setup(c, pagesize)
    # top wash
    c.setFillColor(HEADER_BAND)
    c.rect(m + 8, H * 0.58, W - 2 * m - 16, H * 0.28, fill=1, stroke=0)

    c.setFillColor(INK)
    c.setFont(SERIF_B, 22)
    c.drawCentredString(W / 2, H * 0.78, "TEACHER DATA BINDER")
    c.setFillColor(TEAL)
    c.setFont(SANS_B, 9)
    c.drawCentredString(W / 2, H * 0.735, "STEM  ·  CLASSROOM ORGANIZATION  ·  2026–2027")
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(W * 0.28, H * 0.71, W * 0.72, H * 0.71)

    # two-column contents for cleaner layout
    items_l = [
        "Class information",
        "Roster — 24 students",
        "Roster — 32 students",
        "Attendance grids (×2)",
        "Grade / assignment logs",
    ]
    items_r = [
        "Parent communication log",
        "Behavior & interventions",
        "Accommodations tracker",
        "Standards checklist",
        "Seating chart & weekly plan",
    ]
    y0 = H * 0.58
    c.setFillColor(INK)
    c.setFont(SERIF, 10)
    for i, it in enumerate(items_l):
        c.drawString(W * 0.18, y0 - i * 20, f"·  {it}")
    for i, it in enumerate(items_r):
        c.drawString(W * 0.52, y0 - i * 20, f"·  {it}")

    c.setFillColor(SUB)
    c.setFont(SANS, 8)
    c.drawCentredString(W / 2, H * 0.30, "Also: conference notes  ·  key contacts")
    c.drawCentredString(W / 2, 0.78 * inch, f"Printable PDF  ·  {label}  ·  write by hand or annotate digitally")

    y = H * 0.22
    _label_line(c, 1.15 * inch, y, W - 2.3 * inch, "TEACHER NAME", gap=12)
    _label_line(c, 1.15 * inch, y - 34, W - 2.3 * inch, "SCHOOL / YEAR", gap=12)
    c.showPage()


def page_class_info(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "CLASS INFORMATION", "Section overview  ·  fill by hand or PDF annotate", m=m)
    # label sits above the line — start a bit lower so first label is clear of rules
    y -= 0.06 * inch
    x, w = 0.7 * inch, W - 1.4 * inch
    for lab in [
        "COURSE / SUBJECT",
        "PERIOD / SECTION",
        "ROOM",
        "SCHOOL YEAR",
        "MEETING DAYS / TIMES",
        "TEXTBOOK / PLATFORM",
        "TA / CO-TEACHER",
    ]:
        y = _label_line(c, x, y, w, lab, gap=12)
    y -= 8
    bot = _section_box(c, x, y, w, 2.2 * inch, "CLASS NORMS / EXPECTATIONS")
    _ruled(c, x + 8, y - 22, w - 16, bot + 8, spacing=16)
    y = bot - 14
    bot = _section_box(c, x, y, w, 2.0 * inch, "IMPORTANT LINKS / CODES  (LMS, join codes, office hours)")
    _ruled(c, x + 8, y - 22, w - 16, bot + 8, spacing=16)
    c.showPage()


def page_roster(c, pagesize, n_rows=24):
    """
    Two designed sizes:
      24 rows — more writing room per student (smaller classes)
      32 rows — denser (larger classes / extras)
    """
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    size_note = "more space per row" if n_rows <= 24 else "larger class / extra seats"
    y = _header(
        c, W, H,
        f"CLASS ROSTER  ·  {n_rows} STUDENTS",
        f"{size_note}  ·  leave blanks for adds  ·  print a second copy if needed",
        page_tag=f"{n_rows}-row",
        m=m,
    )
    x = 0.62 * inch
    usable_h = y - 0.72 * inch
    # header + rows
    row_h = min(20, usable_h / (n_rows + 1))
    row_h = max(13.5, row_h)
    col_ws = [0.38 * inch, 2.55 * inch, 2.15 * inch]
    col_ws.append(max(1.3 * inch, W - 1.24 * inch - sum(col_ws)))
    _table(
        c, x, y, col_ws, n_rows, row_h=row_h,
        header=["#", "STUDENT NAME", "ID / EMAIL", "NOTES"],
        number_rows=True,
    )
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(
        x, 0.52 * inch,
        f"This page holds {n_rows} students. Also included: the {'32' if n_rows <= 24 else '24'}-row version.",
    )
    c.showPage()


def page_attendance(
    c,
    pagesize,
    month_label="MONTH: ____________________  YEAR: ________",
    n_rows=24,
):
    """
    Two sizes (matches roster):
      24 rows — roomier writing
      32 rows — larger classes
    """
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    size_note = "more space per row" if n_rows <= 24 else "larger class / extra seats"
    y = _header(
        c, W, H,
        f"ATTENDANCE GRID  ·  {n_rows} STUDENTS",
        f"{month_label}  ·  {size_note}",
        page_tag=f"{n_rows}-row",
        m=m,
    )
    x = 0.55 * inch
    # name + 20 day columns; row height scales to fit
    name_w = 1.55 * inch if n_rows > 24 else 1.7 * inch
    days = 20
    day_w = (W - 1.1 * inch - name_w) / days
    col_ws = [name_w] + [day_w] * days
    headers = ["NAME"] + [str(i) for i in range(1, days + 1)]
    usable_h = y - 0.78 * inch
    row_h = min(16.5 if n_rows <= 24 else 14.0, usable_h / (n_rows + 1))
    row_h = max(11.5, row_h)
    bot = _table(c, x, y, col_ws, n_rows, row_h=row_h, header=headers)
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(
        x, bot - 14,
        f"Codes:  / present   A absent   T tardy   E excused   ·  "
        f"{n_rows} students — also included: the {'32' if n_rows <= 24 else '24'}-row grid.",
    )
    c.showPage()


def page_gradebook(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "GRADE / ASSIGNMENT LOG", "Record scores by assignment  ·  use one sheet per unit or category", m=m)
    x = 0.55 * inch
    # assignment header fields
    y_fields = y - 0.04 * inch
    _label_line(c, x, y_fields, 2.8 * inch, "UNIT / CATEGORY", gap=11)
    _label_line(c, x + 3.0 * inch, y_fields, 2.5 * inch, "MAX POINTS", gap=11)
    y = y_fields - 0.38 * inch
    name_w = 1.8 * inch
    n_asg = 10
    asg_w = (W - 1.1 * inch - name_w) / n_asg
    col_ws = [name_w] + [asg_w] * n_asg
    headers = ["STUDENT"] + [f"A{i}" for i in range(1, n_asg + 1)]
    bot = _table(c, x, y, col_ws, 20, row_h=15, header=headers)
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(x, bot - 14, "Label A1–A10 below (assignment names / dates):")
    yy = bot - 32
    for i in range(1, 6):
        c.setFillColor(TEAL)
        c.setFont(SANS_B, 7)
        c.drawString(x, yy, f"A{i}")
        c.setStrokeColor(RULE)
        c.line(x + 16, yy, x + 3.2 * inch, yy)
        c.setFillColor(TEAL)
        c.drawString(x + 3.4 * inch, yy, f"A{i+5}")
        c.line(x + 3.4 * inch + 16, yy, W - 0.6 * inch, yy)
        yy -= 16
    c.showPage()


def page_parent_log(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "PARENT / GUARDIAN COMMUNICATION LOG", "Calls · emails · conferences", m=m)
    x = 0.6 * inch
    w = W - 1.2 * inch
    col_ws = [0.85 * inch, 1.7 * inch, 0.9 * inch, w - 3.45 * inch]
    _table(c, x, y, col_ws, 18, row_h=22, header=["DATE", "STUDENT", "METHOD", "NOTES / FOLLOW-UP"])
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(x, 0.55 * inch, "Method ideas: call · email · in-person · LMS message · note home")
    c.showPage()


def page_behavior(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "BEHAVIOR & INTERVENTION NOTES", "Objective notes  ·  date · context · action", m=m)
    x = 0.6 * inch
    w = W - 1.2 * inch
    for _ in range(5):
        h = 1.45 * inch
        _section_box(c, x, y, w, h, "DATE _____________   STUDENT _______________________________")
        _ruled(c, x + 8, y - 28, w - 16, y - h + 10, spacing=15)
        y -= h + 10
    c.showPage()


def page_accommodations(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "ACCOMMODATIONS / SUPPORT TRACKER", "Confidential — store securely  ·  IEP / 504 / classroom supports", m=m)
    x = 0.6 * inch
    w = W - 1.2 * inch
    col_ws = [1.9 * inch, 2.4 * inch, w - 4.3 * inch]
    _table(c, x, y, col_ws, 16, row_h=20, header=["STUDENT", "SUPPORT / ACCOMMODATION", "NOTES"])
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(x, 0.55 * inch, "Examples: extended time · preferential seating · calculator · breaks · scribe · quiet room")
    c.showPage()


def page_standards(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "STANDARDS / SKILLS CHECKLIST", "Track mastery by standard or learning target", m=m)
    x = 0.65 * inch
    y = _label_line(c, x, y - 0.04 * inch, W - 1.3 * inch, "UNIT / STANDARD SET", gap=11)
    y -= 6
    col_ws = [0.9 * inch, 3.2 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, W - 1.3 * inch - 6.2 * inch]
    # simplify columns
    col_ws = [1.0 * inch, 3.4 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch]
    # pad last if needed
    used = sum(col_ws)
    if used < W - 1.3 * inch:
        col_ws.append(W - 1.3 * inch - used)
        header = ["CODE", "SKILL / STANDARD", "INTRO", "PRAC", "MAST"]
    else:
        header = ["CODE", "SKILL / STANDARD", "INTRO", "PRAC", "MAST"]
    _table(c, x, y, col_ws[:5], 18, row_h=17, header=header)
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(x, 0.55 * inch, "Mark: blank = not taught   / = introduced   + = practicing   ★ = mastered  (or your own key)")
    c.showPage()


def page_seating(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "SEATING CHART", "Sketch desks or label cells  ·  front of room at top", m=m)
    x = 0.7 * inch
    # board
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.2)
    c.rect(x, y - 0.35 * inch, W - 1.4 * inch, 0.35 * inch, fill=0, stroke=1)
    c.setFillColor(TEAL)
    c.setFont(SANS_B, 8)
    c.drawCentredString(W / 2, y - 0.22 * inch, "FRONT / BOARD")
    # grid 5x6 desks
    y0 = y - 0.55 * inch
    cols, rows = 5, 6
    cell_w = (W - 1.4 * inch) / cols
    cell_h = (y0 - 1.1 * inch) / rows
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    for r in range(rows):
        for col in range(cols):
            cx = x + col * cell_w
            cy = y0 - (r + 1) * cell_h
            c.roundRect(cx + 4, cy + 4, cell_w - 8, cell_h - 8, 4, fill=0, stroke=1)
    c.setFillColor(SUB)
    c.setFont(SANS, 7)
    c.drawString(x, 0.7 * inch, "Version / date: ____________________    Room: ____________________")
    c.showPage()


def page_weekly(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "WEEKLY PLANNER", "Mon–Fri overview  ·  objectives · homework · notes", m=m)
    x = 0.6 * inch
    y = _label_line(c, x, y - 0.04 * inch, 3.5 * inch, "WEEK OF", gap=11)
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    box_h = (y - 0.7 * inch - 4 * 8) / 5
    for day in days:
        bot = _section_box(c, x, y, W - 1.2 * inch, box_h, day)
        _ruled(c, x + 8, y - 20, W - 1.2 * inch - 16, bot + 6, spacing=14)
        y = bot - 8
    c.showPage()


def page_conferences(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "CONFERENCE NOTES", "Student · family · goals · next steps", m=m)
    x = 0.6 * inch
    w = W - 1.2 * inch
    for _ in range(3):
        h = 2.5 * inch
        _section_box(c, x, y, w, h, "DATE ________  STUDENT ________________  FAMILY CONTACT ________________")
        c.setFillColor(SUB)
        c.setFont(SANS, 7)
        c.drawString(x + 8, y - 28, "Strengths:")
        c.setStrokeColor(RULE)
        c.line(x + 55, y - 28, x + w - 12, y - 28)
        c.drawString(x + 8, y - 48, "Concerns / goals:")
        c.line(x + 85, y - 48, x + w - 12, y - 48)
        c.drawString(x + 8, y - 68, "Next steps:")
        _ruled(c, x + 8, y - 85, w - 16, y - h + 12, spacing=15)
        y -= h + 12
    c.showPage()


def page_contacts(c, pagesize):
    W, H, m = _page_setup(c, pagesize, draw_frame=False)
    y = _header(c, W, H, "EMERGENCY & KEY CONTACTS", "Office · counseling · admin · specialists", m=m)
    y -= 0.06 * inch
    x = 0.65 * inch
    w = W - 1.3 * inch
    for lab in [
        "MAIN OFFICE",
        "ATTENDANCE OFFICE",
        "COUNSELOR",
        "ADMIN / AP",
        "NURSE",
        "SPECIAL ED / CASE MANAGER",
        "IT / LMS SUPPORT",
        "DEPT CHAIR",
    ]:
        y = _label_line(c, x, y, w, lab + "  —  name / phone / email", gap=12)
    y -= 10
    bot = _section_box(c, x, y, w, 2.4 * inch, "OTHER NOTES")
    _ruled(c, x + 8, y - 22, w - 16, bot + 8, spacing=16)
    c.showPage()


def build_pdf(pagesize, path: Path, label: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=pagesize)
    page_cover_pdf(c, pagesize, label)
    page_class_info(c, pagesize)
    # two roster sizes
    page_roster(c, pagesize, n_rows=24)
    page_roster(c, pagesize, n_rows=32)
    # two attendance sizes × 2 months
    page_attendance(c, pagesize, n_rows=24)
    page_attendance(c, pagesize, n_rows=32)
    page_attendance(
        c, pagesize,
        month_label="MONTH: ____________________  YEAR: ________  (extra month)",
        n_rows=24,
    )
    page_attendance(
        c, pagesize,
        month_label="MONTH: ____________________  YEAR: ________  (extra month)",
        n_rows=32,
    )
    page_gradebook(c, pagesize)
    page_gradebook(c, pagesize)
    page_parent_log(c, pagesize)
    page_behavior(c, pagesize)
    page_accommodations(c, pagesize)
    page_standards(c, pagesize)
    page_seating(c, pagesize)
    page_weekly(c, pagesize)
    page_conferences(c, pagesize)
    page_contacts(c, pagesize)
    c.save()
    print("PDF", path)


def build_previews(pdf_letter: Path):
    """Rasterize first pages via matplotlib/PIL mock from cover + simple cards."""
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    cover_png = PREVIEWS / "_cover_render.png"
    make_cover_png("letter", cover_png)

    # hero
    cover = Image.open(cover_png).convert("RGB")
    cover.resize((1000, int(1000 * 11 / 8.5)), Image.Resampling.LANCZOS).save(
        PREVIEWS / "01_hero_cover.jpg", quality=92
    )

    # generate preview pages by drawing simplified PIL versions of key sheets
    def sheet_preview(title: str, lines: list[str], name: str):
        im = Image.new("RGB", (850, 1100), (244, 241, 234))
        d = ImageDraw.Draw(im)
        try:
            f = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 28)
            fs = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
            fb = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)
        except Exception:
            f = fs = fb = ImageFont.load_default()
        d.rectangle([30, 30, 820, 1070], outline=(200, 194, 180), width=2)
        d.text((425, 70), title, fill=(26, 26, 26), font=f, anchor="mt")
        d.line([(80, 110), (770, 110)], fill=(200, 194, 180), width=1)
        y = 160
        for ln in lines:
            d.text((70, y), ln, fill=(26, 122, 138) if ln.isupper() or ln.endswith(":") else (26, 26, 26),
                   font=fb if ln.endswith(":") or ln.isupper() else fs)
            y += 36
            if not ln.endswith(":"):
                d.line([(70, y - 8), (780, y - 8)], fill=(176, 168, 152), width=1)
                y += 10
        im.save(PREVIEWS / name, quality=92)

    sheet_preview("CLASS ROSTER", ["Two sizes included:", "· 24-student roster (roomier rows)",
                                   "· 32-student roster (larger classes)",
                                   "Columns: # · Name · ID/Email · Notes"], "02_roster.jpg")
    sheet_preview("ATTENDANCE GRID", ["Two sizes included:", "· 24-student grid (roomier rows)",
                                      "· 32-student grid (larger classes)",
                                      "NAME + days 1–20 · Codes: / A T E · extra month pages"], "03_attendance.jpg")
    sheet_preview("GRADE LOG", ["STUDENT + A1–A10 scores", "Unit / category header",
                                "Assignment key at bottom"], "04_grades.jpg")
    sheet_preview("PARENT LOG", ["DATE · STUDENT · METHOD · NOTES", "Follow-up tracking"], "05_parent.jpg")
    sheet_preview("SEATING CHART", ["FRONT / BOARD", "5×6 desk grid", "Version / date field"], "06_seating.jpg")

    # included card
    im = Image.new("RGB", (1100, 900), (244, 241, 234))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 32)
        fs = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
    except Exception:
        f = fs = ImageFont.load_default()
    d.text((550, 60), "WHAT'S INCLUDED", fill=(26, 26, 26), font=f, anchor="mt")
    items = [
        "Cover + class information",
        "Roster 24-student + Roster 32-student",
        "Attendance 24 + 32 (×2 months each)",
        "Grade logs ×2",
        "Parent communication log",
        "Behavior / intervention notes",
        "Accommodations tracker",
        "Standards checklist",
        "Seating chart + weekly planner",
        "Conference notes + key contacts",
        "US Letter PDF + A4 PDF",
    ]
    y = 140
    for it in items:
        d.text((550, y), f"·  {it}", fill=(26, 26, 26), font=fs, anchor="mt")
        y += 55
    im.save(PREVIEWS / "07_included.jpg", quality=92)
    print("previews ->", PREVIEWS)


def build_zip(pdfs: list[Path]) -> Path:
    zpath = OUT / "Teacher_Data_Binder_STEM_2026_2027.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pdfs:
            z.write(p, p.name)
        z.writestr(
            "READ-ME.txt",
            "TEACHER DATA BINDER — STEM Classroom Organization\n"
            "================================================\n\n"
            "FILES\n"
            "  Teacher_Data_Binder_US_Letter.pdf\n"
            "  Teacher_Data_Binder_A4.pdf\n\n"
            "Print the size that matches your binder inserts. Write by hand or annotate in a PDF app.\n"
            "Roster & attendance: use the 24-row pages for smaller classes (more writing room)\n"
            "or the 32-row pages for larger classes. Extra month pages included for both sizes.\n"
            "Accommodations page may contain sensitive info — store securely.\n\n"
            "For personal / classroom use. Not for resale of the digital files.\n",
        )
    print("ZIP", zpath, f"({zpath.stat().st_size/1e6:.2f} MB)")
    return zpath


def upload_draft(zpath: Path):
    from etsy_manager import EtsyManager

    title = (
        "Teacher Data Binder Printable | Classroom Organization Roster Attendance "
        "Gradebook | STEM Teacher Planner Insert | Back to School"
    )
    if len(title) > 140:
        title = title[:140]
    tags = [
        "teacher data binder",   # 19
        "teacher binder",        # 14
        "classroom organizer",   # 19
        "gradebook printable",   # 19
        "attendance sheet",      # 16
        "teacher printable",     # 17
        "back to school",        # 14
        "roster template",       # 15
        "parent communication",  # 20
        "seating chart",         # 13
        "homeschool binder",     # 16
        "stem teacher",          # 12
        "lesson planner",        # 14
    ]
    assert all(len(t) <= 20 for t in tags), [(t, len(t)) for t in tags if len(t) > 20]

    desc = (
        "Teacher data binder printable — a complete classroom organization system for STEM and "
        "secondary teachers: roster, attendance, grades, parent log, accommodations, seating chart, "
        "and more.\n\n"
        "WHAT YOU GET (instant download)\n"
        "• US Letter PDF + A4 PDF\n"
        "• Cover & class information\n"
        "• Class roster — 24-student (roomier) AND 32-student (larger class)\n"
        "• Attendance grids — 24-student AND 32-student (2 months each)\n"
        "• Grade / assignment logs (2)\n"
        "• Parent / guardian communication log\n"
        "• Behavior & intervention notes\n"
        "• Accommodations / support tracker\n"
        "• Standards / skills checklist\n"
        "• Seating chart\n"
        "• Weekly planner\n"
        "• Conference notes\n"
        "• Key contacts page\n\n"
        "Clean scientific-plate aesthetic (cream, teal, navy). Print and write by hand, or annotate "
        "digitally. Perfect for back to school setup.\n\n"
        "For personal / classroom use. Not for resale of the digital files."
    )

    images = sorted(PREVIEWS.glob("*.jpg"))
    # prefer numbered
    ordered = []
    for name in ["01_hero_cover.jpg", "02_roster.jpg", "03_attendance.jpg", "04_grades.jpg",
                 "05_parent.jpg", "06_seating.jpg", "07_included.jpg"]:
        p = PREVIEWS / name
        if p.exists():
            ordered.append(p)
    for p in images:
        if p not in ordered:
            ordered.append(p)

    m = EtsyManager()
    lid = m.create_full_product(
        title=title,
        description=desc,
        price=6.99,
        taxonomy_id=12476,
        image_paths=[str(p) for p in ordered[:10]],
        digital_file_paths=[str(zpath)],
        tags=tags,
    )
    print("listing_id", lid)
    return lid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()

    PRINTS.mkdir(parents=True, exist_ok=True)
    pdf_letter = PRINTS / "Teacher_Data_Binder_US_Letter.pdf"
    pdf_a4 = PRINTS / "Teacher_Data_Binder_A4.pdf"
    print("Building PDFs (ReportLab)…")
    build_pdf(letter, pdf_letter, "US Letter")
    build_pdf(A4, pdf_a4, "A4")
    build_previews(pdf_letter)
    zpath = build_zip([pdf_letter, pdf_a4])
    if args.upload:
        upload_draft(zpath)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
