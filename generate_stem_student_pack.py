"""
generate_stem_student_pack.py — Cornell Notes + Lab Report + Syllabus (STEM)

Scientific-plate printable pack for BTS / college / lab courses.
US Letter + A4, no brand logo on student pages.

  python generate_stem_student_pack.py
  python generate_stem_student_pack.py --upload
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "stem_student_pack"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"

CREAM = "#F4F1EA"
INK = "#1A1A1A"
SUB = "#555555"
TEAL = "#1A7A8A"
LINE = "#C8C2B4"
GOLD = "#c9a24b"
RULE = "#B0A898"

DPI = 300
LETTER = (8.5, 11.0)
A4 = (8.27, 11.69)


def _fig(size, dpi=DPI):
    W, H = size
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_facecolor(CREAM)
    ax.axis("off")
    return fig, ax, W, H


def _frame(ax, W, H, m=0.4):
    ax.add_patch(Rectangle((m, m), W - 2 * m, H - 2 * m, fill=False, ec=LINE, lw=1.2))


def _header(ax, W, H, title: str, subtitle: str = ""):
    ax.text(W / 2, H - 0.55, title, ha="center", va="center",
            fontsize=14, fontfamily="serif", fontweight="bold", color=INK)
    if subtitle:
        ax.text(W / 2, H - 0.85, subtitle, ha="center", va="center",
                fontsize=8, fontfamily="sans-serif", color=TEAL)
    ax.plot([0.7, W - 0.7], [H - 1.05, H - 1.05], color=LINE, lw=1.0)


def _lines(ax, x0, x1, y0, y1, spacing=0.28, color=RULE, lw=0.55):
    y = y0
    while y >= y1:
        ax.plot([x0, x1], [y, y], color=color, lw=lw)
        y -= spacing


def _label(ax, x, y, text, size=7.5, color=SUB):
    ax.text(x, y, text, ha="left", va="center", fontsize=size,
            fontfamily="sans-serif", color=color)


def _box(ax, x, y, w, h, title=None):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=LINE, lw=0.9))
    if title:
        ax.text(x + 0.08, y + h - 0.18, title, ha="left", va="center",
                fontsize=7.5, fontfamily="sans-serif", fontweight="bold", color=TEAL)


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor=CREAM)
    plt.close(fig)


# ── Cornell Notes ────────────────────────────────────────────────────────────

def _write_field(ax, x0, x1, y_label, label, line_gap=0.32):
    """Label above a long write-on underline (room for handwriting)."""
    _label(ax, x0, y_label, label, size=7.5)
    y_line = y_label - line_gap
    ax.plot([x0, x1], [y_line, y_line], color=RULE, lw=0.9)
    return y_line


def cornell_page(size=LETTER, path=None, page_label="CORNELL NOTES"):
    """Classic Cornell layout: cue | notes, summary strip at bottom."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, page_label, "STEM  ·  LECTURE / READING  ·  US Letter & A4")

    # Generous meta block: labels ABOVE long underlines (not cramped on one baseline)
    left_m, right_m = 0.55, W - 0.55
    cue_w = 2.35
    mid = left_m + cue_w
    y_meta = H - 1.35
    # Course/topic takes ~70% width; date ~28%
    gap = 0.25
    x_split = left_m + 0.70 * (right_m - left_m)
    _write_field(ax, left_m, x_split - gap / 2, y_meta, "COURSE / TOPIC", line_gap=0.38)
    _write_field(ax, x_split + gap / 2, right_m, y_meta, "DATE", line_gap=0.38)

    top = y_meta - 0.70  # clear space under write lines before notes grid
    bottom = 1.55

    y_notes_top = top
    y_sum_top = bottom + 0.95

    # vertical divider cue | notes
    ax.plot([mid, mid], [y_sum_top, y_notes_top], color=LINE, lw=1.1)
    # horizontal above summary
    ax.plot([left_m, right_m], [y_sum_top, y_sum_top], color=LINE, lw=1.1)

    # section titles
    ax.text((left_m + mid) / 2, y_notes_top - 0.18, "CUES / QUESTIONS", ha="center",
            fontsize=7, fontfamily="sans-serif", fontweight="bold", color=TEAL)
    ax.text((mid + right_m) / 2, y_notes_top - 0.18, "NOTES", ha="center",
            fontsize=7, fontfamily="sans-serif", fontweight="bold", color=TEAL)
    ax.text(W / 2, y_sum_top - 0.18, "SUMMARY  (2–3 sentences after class)", ha="center",
            fontsize=7, fontfamily="sans-serif", fontweight="bold", color=TEAL)

    # ruled lines
    _lines(ax, left_m + 0.08, mid - 0.08, y_notes_top - 0.4, y_sum_top + 0.12, spacing=0.30)
    _lines(ax, mid + 0.08, right_m - 0.08, y_notes_top - 0.4, y_sum_top + 0.12, spacing=0.30)
    _lines(ax, left_m + 0.08, right_m - 0.08, y_sum_top - 0.4, bottom + 0.15, spacing=0.30)

    # tiny how-to footer
    ax.text(W / 2, 0.7, "During class → Notes  ·  After class → Cues  ·  End of week → Summary",
            ha="center", fontsize=6.5, color=SUB, fontfamily="sans-serif")

    if path:
        save(fig, path)
    else:
        plt.close(fig)
    return path


def cornell_guide(size=LETTER, path=None):
    """One-page method guide."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "CORNELL METHOD  ·  QUICK GUIDE", "How to use these pages for STEM courses")

    y = H - 1.5
    steps = [
        ("1. RECORD", "In the large NOTES column, capture definitions, derivations, diagrams, and examples during lecture or while reading."),
        ("2. REDUCE", "Within 24 hours, write CUES: keywords, formulas to recall, and questions that the notes answer."),
        ("3. RECITE", "Cover the notes column. Use only the cues to restate the material out loud or on a blank page."),
        ("4. REFLECT", "Mark hard spots. Link ideas to prior units (e.g. “uses chain rule from Calc I”)."),
        ("5. REVIEW", "Write a short SUMMARY at the bottom. Revisit cues before quizzes."),
        ("STEM TIP", "Reserve the right margin of NOTES for formula boxes or unit checks (SI, sig figs)."),
    ]
    for title, body in steps:
        ax.text(0.7, y, title, ha="left", va="top", fontsize=9, fontfamily="sans-serif",
                fontweight="bold", color=TEAL)
        # simple wrap
        words = body.split()
        line, lines = "", []
        for w in words:
            trial = (line + " " + w).strip()
            if len(trial) > 78:
                lines.append(line)
                line = w
            else:
                line = trial
        if line:
            lines.append(line)
        yy = y - 0.28
        for ln in lines:
            ax.text(0.7, yy, ln, ha="left", va="top", fontsize=8.5, fontfamily="serif", color=INK)
            yy -= 0.28
        y -= 1.25

    ax.text(W / 2, 0.75, "Print multiple blank Cornell pages and keep this guide at the front of your binder.",
            ha="center", fontsize=7.5, color=SUB)
    if path:
        save(fig, path)
    else:
        plt.close(fig)


# ── Lab Report ───────────────────────────────────────────────────────────────

def lab_page_1(size=LETTER, path=None):
    """Title, purpose, background, hypothesis."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "LAB REPORT", "STEM  ·  EXPERIMENT DOCUMENTATION")

    y = H - 1.35
    # Full-width write fields: label above, long underline below
    for lab in (
        "EXPERIMENT TITLE",
        "COURSE / SECTION",
        "NAME(S)",
        "DATE / LAB PARTNER",
    ):
        _write_field(ax, 0.65, W - 0.65, y, lab, line_gap=0.40)
        y -= 0.72

    sections = [
        ("1. PURPOSE / OBJECTIVE", 1.15),
        ("2. BACKGROUND / THEORY  (key equations, prior knowledge)", 1.55),
        ("3. HYPOTHESIS  (if–then, measurable)", 1.15),
        ("4. VARIABLES", 1.35),
    ]
    for title, h in sections:
        _box(ax, 0.55, y - h, W - 1.1, h, title)
        if "VARIABLES" in title:
            # label left, long write line to the right (handwriting room)
            for i, lab in enumerate(("Independent:", "Dependent:", "Controlled:")):
                yy = y - 0.48 - i * 0.38
                ax.text(0.72, yy + 0.12, lab, ha="left", va="center", fontsize=7.5,
                        fontfamily="sans-serif", color=SUB)
                ax.plot([1.95, W - 0.75], [yy, yy], color=RULE, lw=0.85)
        else:
            _lines(ax, 0.7, W - 0.75, y - 0.45, y - h + 0.15, spacing=0.32)
        y -= h + 0.12

    if path:
        save(fig, path)
    else:
        plt.close(fig)


def lab_page_2(size=LETTER, path=None):
    """Materials, procedure, safety."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "LAB REPORT  ·  METHODS", "Materials · Procedure · Safety")

    y = H - 1.35
    _box(ax, 0.55, y - 2.0, W - 1.1, 2.0, "5. MATERIALS & EQUIPMENT")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.85, spacing=0.28)
    y -= 2.15

    _box(ax, 0.55, y - 4.2, W - 1.1, 4.2, "6. PROCEDURE  (numbered steps; enough detail to replicate)")
    for i in range(1, 11):
        yy = y - 0.4 - (i - 1) * 0.36
        ax.text(0.75, yy, f"{i}.", fontsize=8, color=TEAL, fontfamily="sans-serif")
        ax.plot([1.05, W - 0.75], [yy, yy], color=RULE, lw=0.55)
    y -= 4.35

    _box(ax, 0.55, y - 1.35, W - 1.1, 1.35, "7. SAFETY NOTES / PPE")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.2, spacing=0.28)

    if path:
        save(fig, path)
    else:
        plt.close(fig)


def lab_page_3(size=LETTER, path=None):
    """Data table + graph space."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "LAB REPORT  ·  DATA", "Tables · Observations · Graph")

    y = H - 1.35
    _box(ax, 0.55, y - 3.6, W - 1.1, 3.6, "8. DATA TABLE  (include units & uncertainty if known)")
    # grid table
    x0, x1 = 0.7, W - 0.75
    y0, y1 = y - 0.5, y - 3.4
    cols, rows = 5, 9
    for i in range(cols + 1):
        x = x0 + i * (x1 - x0) / cols
        ax.plot([x, x], [y1, y0], color=LINE, lw=0.6)
    for j in range(rows + 1):
        yy = y0 - j * (y0 - y1) / rows
        ax.plot([x0, x1], [yy, yy], color=LINE, lw=0.6)
    y -= 3.75

    _box(ax, 0.55, y - 1.2, W - 1.1, 1.2, "9. QUALITATIVE OBSERVATIONS")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.05, spacing=0.28)
    y -= 1.35

    _box(ax, 0.55, y - 3.5, W - 1.1, 3.5, "10. GRAPH / FIGURE  (label axes, units, title)")
    # empty plot frame
    ax.add_patch(Rectangle((0.9, y - 3.25), W - 1.8, 2.7, fill=False, ec=LINE, lw=0.9))
    ax.text(W / 2, y - 1.9, "attach printed graph or sketch here", ha="center",
            fontsize=8, color=SUB, style="italic")

    if path:
        save(fig, path)
    else:
        plt.close(fig)


def lab_page_4(size=LETTER, path=None):
    """Analysis, error, conclusion."""
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "LAB REPORT  ·  ANALYSIS & CONCLUSION", "Calculations · Error · Discussion")

    y = H - 1.35
    blocks = [
        ("11. SAMPLE CALCULATIONS  (show formulas, substitute values, units)", 2.4),
        ("12. ERROR ANALYSIS  (% error, sources of systematic / random error)", 1.6),
        ("13. DISCUSSION  (does data support hypothesis? anomalies?)", 2.0),
        ("14. CONCLUSION  (answer the purpose in 3–5 sentences)", 1.5),
        ("15. REFERENCES", 1.0),
    ]
    for title, h in blocks:
        _box(ax, 0.55, y - h, W - 1.1, h, title)
        _lines(ax, 0.7, W - 0.75, y - 0.45, y - h + 0.12, spacing=0.28)
        y -= h + 0.12

    if path:
        save(fig, path)
    else:
        plt.close(fig)


# ── Syllabus ─────────────────────────────────────────────────────────────────

def syllabus_page_1(size=LETTER, path=None):
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "COURSE SYLLABUS", "STEM  ·  SEMESTER TEMPLATE  ·  EDITABLE BY HAND OR PDF ANNOTATION")

    y = H - 1.35
    for lab in [
        "COURSE TITLE",
        "COURSE CODE / SECTION",
        "TERM / YEAR",
        "INSTRUCTOR",
        "EMAIL / OFFICE",
        "OFFICE HOURS",
        "CLASS MEETING TIME / ROOM",
    ]:
        _write_field(ax, 0.65, W - 0.65, y, lab, line_gap=0.38)
        y -= 0.68

    _box(ax, 0.55, y - 1.8, W - 1.1, 1.8, "COURSE DESCRIPTION")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.65, spacing=0.28)
    y -= 1.95

    _box(ax, 0.55, y - 2.0, W - 1.1, 2.0, "LEARNING OBJECTIVES  (by end of course, students will be able to…)")
    for i in range(1, 6):
        yy = y - 0.4 - (i - 1) * 0.32
        ax.text(0.75, yy, f"{i}.", fontsize=8, color=TEAL)
        ax.plot([1.05, W - 0.75], [yy, yy], color=RULE, lw=0.55)
    y -= 2.15

    _box(ax, 0.55, y - 1.6, W - 1.1, 1.6, "PREREQUISITES / COREQUISITES")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.45, spacing=0.28)

    if path:
        save(fig, path)
    else:
        plt.close(fig)


def syllabus_page_2(size=LETTER, path=None):
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "SYLLABUS  ·  MATERIALS & GRADING", "Texts · Tools · Assessment weights")

    y = H - 1.35
    _box(ax, 0.55, y - 2.2, W - 1.1, 2.2, "REQUIRED MATERIALS  (textbook, calculator, lab notebook, software…)")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 2.05, spacing=0.28)
    y -= 2.35

    _box(ax, 0.55, y - 3.4, W - 1.1, 3.4, "GRADING BREAKDOWN")
    # table header
    x0, x1 = 0.7, W - 0.75
    headers = ["COMPONENT", "% WEIGHT", "NOTES"]
    col_w = [(x1 - x0) * 0.4, (x1 - x0) * 0.2, (x1 - x0) * 0.4]
    yy = y - 0.45
    x = x0
    for h, w in zip(headers, col_w):
        ax.text(x + 0.05, yy, h, fontsize=7, fontweight="bold", color=TEAL, fontfamily="sans-serif")
        x += w
    ax.plot([x0, x1], [yy - 0.12, yy - 0.12], color=LINE, lw=0.8)
    for i in range(8):
        row_y = yy - 0.35 - i * 0.32
        ax.plot([x0, x1], [row_y, row_y], color=RULE, lw=0.5)
        x = x0
        for w in col_w[:-1]:
            x += w
            ax.plot([x, x], [row_y, yy - 0.12], color=LINE, lw=0.4)
    y -= 3.55

    _box(ax, 0.55, y - 2.0, W - 1.1, 2.0, "GRADE SCALE  (e.g. A 90–100, B 80–89, …)")
    _lines(ax, 0.7, W - 0.75, y - 0.45, y - 1.85, spacing=0.28)

    if path:
        save(fig, path)
    else:
        plt.close(fig)


def syllabus_page_3(size=LETTER, path=None):
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H)
    _header(ax, W, H, "SYLLABUS  ·  POLICIES & SCHEDULE", "Attendance · Integrity · Weekly plan")

    y = H - 1.35
    for title, h in [
        ("ATTENDANCE & PARTICIPATION", 1.15),
        ("LATE WORK / MAKE-UP POLICY", 1.15),
        ("ACADEMIC INTEGRITY", 1.15),
        ("ACCOMMODATIONS / SUPPORT RESOURCES", 1.15),
    ]:
        _box(ax, 0.55, y - h, W - 1.1, h, title)
        _lines(ax, 0.7, W - 0.75, y - 0.45, y - h + 0.12, spacing=0.28)
        y -= h + 0.1

    _box(ax, 0.55, y - 3.5, W - 1.1, 3.5, "WEEKLY / UNIT SCHEDULE  (topic · reading · due dates)")
    x0, x1 = 0.7, W - 0.75
    yy0 = y - 0.45
    # header row
    for label, xf in [("WEEK", 0.08), ("TOPIC", 0.35), ("READING / LAB", 0.65), ("DUE", 0.9)]:
        ax.text(x0 + (x1 - x0) * xf, yy0, label, fontsize=6.5, fontweight="bold", color=TEAL)
    ax.plot([x0, x1], [yy0 - 0.12, yy0 - 0.12], color=LINE, lw=0.7)
    for i in range(10):
        row_y = yy0 - 0.28 - i * 0.28
        ax.plot([x0, x1], [row_y, row_y], color=RULE, lw=0.45)

    if path:
        save(fig, path)
    else:
        plt.close(fig)


# ── Cover sheet for pack ─────────────────────────────────────────────────────

def pack_cover(size=LETTER, path=None):
    fig, ax, W, H = _fig(size)
    _frame(ax, W, H, m=0.45)
    ax.text(W / 2, H - 1.4, "STEM STUDENT PACK", ha="center", fontsize=18,
            fontfamily="serif", fontweight="bold", color=INK)
    ax.text(W / 2, H - 1.85, "Cornell Notes  ·  Lab Report  ·  Syllabus", ha="center",
            fontsize=11, color=TEAL, fontfamily="sans-serif")
    ax.plot([W * 0.25, W * 0.75], [H - 2.15, H - 2.15], color=LINE, lw=1.2)

    # small motif: simple axes + sine
    cx, cy, r = W / 2, H * 0.55, 1.3
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(cx + 0.9 * r * (t / (2 * np.pi) * 2 - 1), cy + 0.35 * r * np.sin(t),
            color=TEAL, lw=1.6)
    ax.plot([cx - r, cx + r], [cy, cy], color=LINE, lw=0.7)
    ax.plot([cx, cx], [cy - 0.7 * r, cy + 0.7 * r], color=LINE, lw=0.7)

    items = [
        "Cornell notes pages + method guide",
        "4-page lab report structure (purpose → conclusion)",
        "3-page course syllabus template",
        "US Letter and A4  ·  300 DPI printables",
    ]
    y = H * 0.32
    for it in items:
        ax.text(W / 2, y, f"·  {it}", ha="center", fontsize=10, color=INK, fontfamily="serif")
        y -= 0.38

    ax.text(W / 2, 0.9, "2026 — 2027  ·  BACK TO SCHOOL / COLLEGE", ha="center",
            fontsize=8, color=SUB)
    if path:
        save(fig, path)
    else:
        plt.close(fig)


def render_all():
    PRINTS.mkdir(parents=True, exist_ok=True)
    sizes = [("US_Letter", LETTER), ("A4", A4)]
    for tag, size in sizes:
        pack_cover(size, PRINTS / f"00_pack_cover_{tag}.jpg")
        cornell_guide(size, PRINTS / f"cornell_guide_{tag}.jpg")
        for n in (1, 2, 3):
            cornell_page(size, PRINTS / f"cornell_blank_{n:02d}_{tag}.jpg")
        lab_page_1(size, PRINTS / f"lab_report_01_front_{tag}.jpg")
        lab_page_2(size, PRINTS / f"lab_report_02_methods_{tag}.jpg")
        lab_page_3(size, PRINTS / f"lab_report_03_data_{tag}.jpg")
        lab_page_4(size, PRINTS / f"lab_report_04_analysis_{tag}.jpg")
        syllabus_page_1(size, PRINTS / f"syllabus_01_overview_{tag}.jpg")
        syllabus_page_2(size, PRINTS / f"syllabus_02_grading_{tag}.jpg")
        syllabus_page_3(size, PRINTS / f"syllabus_03_policies_{tag}.jpg")
        print("rendered", tag)
    # extra blank cornell for volume (same as blank but numbered 04-06)
    for tag, size in sizes:
        for n in (4, 5, 6):
            cornell_page(size, PRINTS / f"cornell_blank_{n:02d}_{tag}.jpg")


def build_previews():
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    # hero: three page types side by side
    picks = [
        PRINTS / "cornell_blank_01_US_Letter.jpg",
        PRINTS / "lab_report_01_front_US_Letter.jpg",
        PRINTS / "syllabus_01_overview_US_Letter.jpg",
    ]
    imgs = [Image.open(p).convert("RGB") for p in picks if p.exists()]
    if len(imgs) == 3:
        th = 1100
        tiles = [im.resize((int(im.width * th / im.height), th), Image.Resampling.LANCZOS) for im in imgs]
        pad = 28
        W = sum(t.width for t in tiles) + pad * 4
        H = th + 160
        canvas = Image.new("RGB", (W, H), (244, 241, 234))
        d = ImageDraw.Draw(canvas)
        try:
            f = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 40)
            fs = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 20)
        except Exception:
            f = fs = ImageFont.load_default()
        d.text((W // 2, 36), "STEM Student Pack", fill=(26, 26, 26), font=f, anchor="mt")
        d.text((W // 2, 90), "Cornell Notes  ·  Lab Report  ·  Syllabus", fill=(26, 122, 138), font=fs, anchor="mt")
        x = pad
        for t in tiles:
            canvas.paste(t, (x, 130))
            x += t.width + pad
        canvas.save(PREVIEWS / "01_hero.jpg", quality=92)

    for src, name in [
        ("cornell_blank_01_US_Letter.jpg", "02_cornell_detail.jpg"),
        ("lab_report_03_data_US_Letter.jpg", "03_lab_data_detail.jpg"),
        ("syllabus_02_grading_US_Letter.jpg", "04_syllabus_detail.jpg"),
        ("00_pack_cover_US_Letter.jpg", "05_pack_cover.jpg"),
    ]:
        p = PRINTS / src
        if p.exists():
            Image.open(p).convert("RGB").save(PREVIEWS / name, quality=92)

    # included card
    fig, ax, W, H = _fig((10, 8), dpi=140)
    ax.text(0.5, 0.9, "WHAT'S INCLUDED", ha="center", fontsize=20, fontweight="bold",
            color=INK, transform=ax.transAxes)
    lines = [
        "· Cornell method guide + 6 blank Cornell pages (Letter & A4)",
        "· Lab report: 4 pages (purpose → methods → data → analysis)",
        "· Course syllabus: 3 pages (overview → grading → policies)",
        "· Print-ready 300 DPI JPG",
        "· Scientific plate aesthetic for STEM courses",
    ]
    for i, L in enumerate(lines):
        ax.text(0.5, 0.72 - i * 0.1, L, ha="center", fontsize=12, color=INK, transform=ax.transAxes)
    ax.text(0.5, 0.12, "Instant download  ·  for students, teachers & TAs", ha="center",
            fontsize=10, color=SUB, transform=ax.transAxes)
    fig.savefig(PREVIEWS / "06_included.jpg", dpi=140, facecolor=CREAM)
    plt.close(fig)
    print("previews ->", PREVIEWS)


def build_zip() -> Path:
    zpath = OUT / "STEM_Student_Pack_Cornell_Lab_Syllabus.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PRINTS.glob("*.jpg")):
            # folder by type
            name = p.name
            if name.startswith("cornell"):
                folder = "01_cornell_notes"
            elif name.startswith("lab_"):
                folder = "02_lab_report"
            elif name.startswith("syllabus"):
                folder = "03_syllabus"
            else:
                folder = "00_pack"
            z.write(p, f"{folder}/{name}")
        z.writestr(
            "READ-ME.txt",
            "STEM STUDENT PACK — Cornell Notes + Lab Report + Syllabus\n"
            "=========================================================\n\n"
            "CONTENTS\n"
            "  01_cornell_notes/   method guide + blank Cornell pages\n"
            "  02_lab_report/      4-page lab report structure\n"
            "  03_syllabus/        3-page course syllabus template\n"
            "  00_pack/            pack cover sheet\n\n"
            "Each page is provided in US Letter and A4 at 300 DPI (JPG).\n"
            "Print at 100% scale. Annotate by hand or in a PDF app.\n\n"
            "For personal / classroom use. Not for resale or redistribution.\n",
        )
    print("ZIP ->", zpath, f"({zpath.stat().st_size/1e6:.2f} MB)")
    return zpath


def upload_draft(zpath: Path):
    from etsy_manager import EtsyManager

    # SEO: lead with cornell notes template (high fav history) + lab + syllabus
    title = (
        "Cornell Notes Template Printable | Lab Report Template | Syllabus Template "
        "STEM Student Pack | Back to School College"
    )
    if len(title) > 140:
        title = title[:140]
    tags = [
        "cornell notes",          # 13
        "lab report template",    # 19
        "syllabus template",      # 17
        "cornell notes template", # 21 TOO LONG
    ]
    tags = [
        "cornell notes",
        "lab report template",
        "syllabus template",
        "study template",
        "student printable",
        "college printable",
        "back to school",
        "stem printable",
        "note taking",
        "teacher printable",
        "homeschool printable",
        "lecture notes",
        "academic template",
    ]
    assert all(len(t) <= 20 for t in tags), [(t, len(t)) for t in tags if len(t) > 20]

    desc = (
        "STEM student pack: Cornell notes template, lab report template, and course syllabus "
        "template — printable scientific-plate pages for lecture, lab, and course planning.\n\n"
        "WHAT YOU GET (instant download)\n"
        "• Cornell notes method guide + blank Cornell pages\n"
        "• Lab report structure (purpose, methods, data tables, analysis, conclusion)\n"
        "• Course syllabus template (overview, grading, policies, weekly schedule)\n"
        "• US Letter and A4 · 300 DPI JPG\n\n"
        "Designed for high school, college, and STEM courses. Print and write by hand, or import "
        "into GoodNotes / Notability / PDF annotation apps.\n\n"
        "Perfect for back to school, exam prep, and lab courses.\n\n"
        "For personal / classroom use. Not for resale or redistribution."
    )

    images = sorted(PREVIEWS.glob("*.jpg"))
    m = EtsyManager()
    listing_id = m.create_full_product(
        title=title,
        description=desc,
        price=5.99,
        taxonomy_id=12476,  # planner/templates family
        image_paths=[str(p) for p in images],
        digital_file_paths=[str(zpath)],
        tags=tags,
    )
    print("listing_id", listing_id)
    return listing_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()
    print("Rendering pack…")
    render_all()
    zpath = build_zip()
    build_previews()
    if args.upload:
        upload_draft(zpath)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
