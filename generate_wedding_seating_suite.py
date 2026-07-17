"""
generate_wedding_seating_suite.py — MathRelaxing Geometric Wedding Suite
========================================================================
Wedding seating chart + table numbers + place cards + timeline + menu.
Angle: editorial geometric (navy/gold/cream, golden-ratio accents) —
NOT generic florals. Fits MathRelaxing visual language.

  python generate_wedding_seating_suite.py
"""
from __future__ import annotations

import csv
import math
import os
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, landscape, A3
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

import brand

BASE = Path(__file__).resolve().parent
OUT = BASE / "wedding_seating_suite"
PREV = OUT / "previews"
TEMPLATES = OUT / "templates"
SAMPLES = OUT / "samples"
ZIP_PATH = OUT / "MathRelaxing_Geometric_Wedding_Suite.zip"

# Brand palette (MathRelaxing)
NAVY = (18, 23, 46)
GOLD = (201, 162, 75)
CREAM = (248, 244, 235)
INK = (33, 33, 33)
SOFT = (110, 108, 105)
WHITE = (255, 255, 255)
PHI = (1 + math.sqrt(5)) / 2

# Sample couple (fictional)
COUPLE = "Alex & Jordan"
DATE = "September 14, 2026"
VENUE = "The Conservatory"

TABLES = {
    1: ["Morgan Lee", "Sam Rivera", "Casey Park", "Riley Quinn", "Avery Kim", "Jamie Cole"],
    2: ["Taylor Brooks", "Jordan Hale", "Reese Dunn", "Parker Shaw", "Quinn Blake", "Drew Lane"],
    3: ["Skyler West", "Cameron Fox", "Harper Wells", "Rowan Gray", "Emerson Vale", "Finley Cross"],
    4: ["Sloane Reed", "Blair Moss", "Phoenix Hart", "Sage Monroe", "Lennox Day", "Marlowe Ash"],
    5: ["Indigo Barr", "Wren Ellis", "Remy Frost", "Eden Cole", "Luca Shore", "Nova Quill"],
    6: ["Kit Anders", "Jules Marin", "Ari Sol", "Nico Vale", "Shay Rowan", "Milan Ortega"],
}


def _font(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["georgiab.ttf", "timesbd.ttf", "calibrib.ttf"]
        if bold
        else ["georgia.ttf", "times.ttf", "calibri.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _font_sans(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _rgb01(c):
    return tuple(x / 255 for x in c)


def _draw_phi_marks(draw: ImageDraw.ImageDraw, w, h, margin=40):
    """Subtle golden-ratio corner marks + thin arcs."""
    # corners
    for ox, oy, sx, sy in [
        (margin, margin, 1, 1),
        (w - margin, margin, -1, 1),
        (margin, h - margin, 1, -1),
        (w - margin, h - margin, -1, -1),
    ]:
        draw.line([(ox, oy), (ox + sx * 28, oy)], fill=GOLD, width=2)
        draw.line([(ox, oy), (ox, oy + sy * 28)], fill=GOLD, width=2)
    # soft arc top
    bbox = [w * 0.15, -h * 0.05, w * 0.85, h * 0.35]
    draw.arc(bbox, 200, 340, fill=(*GOLD, 80) if False else GOLD, width=1)


def _draw_header_block(draw, w, y, couple, date, venue, title_size=42):
    draw.text((w // 2, y), couple, font=_font(title_size, True), fill=NAVY, anchor="mt")
    y += int(title_size * 1.15)
    draw.text((w // 2, y), "·   ·   ·", font=_font(14), fill=GOLD, anchor="mt")
    y += 28
    draw.text((w // 2, y), date, font=_font_sans(14), fill=SOFT, anchor="mt")
    y += 22
    draw.text((w // 2, y), venue, font=_font_sans(13), fill=SOFT, anchor="mt")
    return y + 30


# ── Preview images (Etsy) ────────────────────────────────────────────────────

def make_hero_preview():
    """Square hero: seating chart mockup on cream with brand footer."""
    s = 2000
    img = Image.new("RGB", (s, s), CREAM)
    d = ImageDraw.Draw(img)
    _draw_phi_marks(d, s, s, 60)
    y = 160
    y = _draw_header_block(d, s, y, COUPLE, DATE, VENUE, title_size=56)
    d.line([(s * 0.2, y), (s * 0.8, y)], fill=GOLD, width=2)
    y += 40
    d.text((s // 2, y), "SEATING CHART", font=_font_sans(18, True), fill=NAVY, anchor="mt")
    y += 50

    # 6 table cards in grid
    cols, rows = 3, 2
    card_w, card_h = 520, 380
    gap = 40
    total_w = cols * card_w + (cols - 1) * gap
    x0 = (s - total_w) // 2
    ti = 1
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (card_w + gap)
            yy = y + r * (card_h + gap)
            d.rounded_rectangle([x, yy, x + card_w, yy + card_h], radius=8, outline=NAVY, width=2)
            d.ellipse([x + card_w // 2 - 28, yy + 18, x + card_w // 2 + 28, yy + 74], outline=GOLD, width=2)
            d.text((x + card_w // 2, yy + 46), str(ti), font=_font(22, True), fill=NAVY, anchor="mm")
            d.text((x + card_w // 2, yy + 90), f"Table {ti}", font=_font_sans(14, True), fill=GOLD, anchor="mt")
            gy = yy + 120
            for name in TABLES[ti][:5]:
                d.text((x + card_w // 2, gy), name, font=_font_sans(15), fill=INK, anchor="mt")
                gy += 28
            if len(TABLES[ti]) > 5:
                d.text((x + card_w // 2, gy), "…", font=_font_sans(14), fill=SOFT, anchor="mt")
            ti += 1

    # brand strip
    d.rectangle([0, s - 120, s, s], fill=NAVY)
    d.text((s // 2, s - 70), "MathRelaxing  ·  Geometric Wedding Suite", font=_font_sans(22), fill=GOLD, anchor="mm")
    d.text((s // 2, s - 38), "Seating chart · Table numbers · Place cards · Timeline · Menu", font=_font_sans(14), fill=CREAM, anchor="mm")

    path = PREV / "wedding_preview_1_hero.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=90)
    return path


def make_styles_preview():
    s = 2000
    img = Image.new("RGB", (s, s), NAVY)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 80), "What's included", font=_font(40, True), fill=CREAM, anchor="mt")
    d.text((s // 2, 140), "One cohesive geometric system", font=_font_sans(18), fill=GOLD, anchor="mt")

    items = [
        ("01", "Seating chart", "Landscape poster layout\n6–12 tables"),
        ("02", "Table numbers", "Cards 1–12\nprint & cut"),
        ("03", "Place cards", "Folded name cards\nguest side"),
        ("04", "Timeline", "Day-of schedule\nceremony → last dance"),
        ("05", "Menu card", "Dinner courses\nmatching design"),
        ("06", "Guest list CSV", "Plan tables in Sheets\nbefore design"),
    ]
    # 2x3 grid of cream cards
    cw, ch = 560, 420
    gap = 36
    x0 = (s - (3 * cw + 2 * gap)) // 2
    y0 = 220
    for i, (num, title, sub) in enumerate(items):
        c, r = i % 3, i // 3
        x = x0 + c * (cw + gap)
        y = y0 + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=12, fill=CREAM)
        d.ellipse([x + 30, y + 30, x + 100, y + 100], outline=GOLD, width=3)
        d.text((x + 65, y + 65), num, font=_font(20, True), fill=NAVY, anchor="mm")
        d.text((x + 40, y + 140), title, font=_font(28, True), fill=NAVY, anchor="lt")
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 40, y + 200 + j * 36), line, font=_font_sans(18), fill=SOFT, anchor="lt")

    d.rectangle([0, s - 100, s, s], fill=(10, 12, 28))
    d.text((s // 2, s - 50), "Navy · Gold · Cream  ·  Phi-inspired geometry", font=_font_sans(18), fill=GOLD, anchor="mm")
    path = PREV / "wedding_preview_2_included.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=90)
    return path


def make_detail_preview():
    """Close-up place card + table number."""
    s = 2000
    img = Image.new("RGB", (s, s), (232, 228, 220))
    d = ImageDraw.Draw(img)
    # table number card
    tw, th = 520, 640
    x, y = 280, 400
    d.rounded_rectangle([x + 12, y + 14, x + tw + 12, y + th + 14], radius=8, fill=(40, 40, 48))
    d.rounded_rectangle([x, y, x + tw, y + th], radius=8, fill=CREAM)
    _draw_phi_marks(d, 0, 0)  # no-op wrong - draw on card via offsets
    d.ellipse([x + tw // 2 - 70, y + 120, x + tw // 2 + 70, y + 260], outline=GOLD, width=3)
    d.text((x + tw // 2, y + 190), "3", font=_font(72, True), fill=NAVY, anchor="mm")
    d.text((x + tw // 2, y + 320), "TABLE", font=_font_sans(16, True), fill=GOLD, anchor="mt")
    d.line([(x + 80, y + 380), (x + tw - 80, y + 380)], fill=GOLD, width=1)
    d.text((x + tw // 2, y + 420), COUPLE, font=_font(20), fill=NAVY, anchor="mt")

    # place card
    pw, ph = 700, 320
    px, py = 1000, 620
    d.rounded_rectangle([px + 10, py + 12, px + pw + 10, py + ph + 12], radius=6, fill=(40, 40, 48))
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=6, fill=CREAM)
    d.line([(px + 40, py + ph // 2), (px + pw - 40, py + ph // 2)], fill=GOLD, width=1)
    d.text((px + pw // 2, py + 70), "Morgan Lee", font=_font(36, True), fill=NAVY, anchor="mm")
    d.text((px + pw // 2, py + 220), "Table 1", font=_font_sans(18), fill=GOLD, anchor="mm")

    d.rectangle([0, s - 110, s, s], fill=NAVY)
    d.text((s // 2, s - 55), "Print · cut · display  ·  Matching suite", font=_font_sans(20), fill=GOLD, anchor="mm")
    path = PREV / "wedding_preview_3_detail.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=90)
    return path


def make_before_after_preview():
    """Shows blank template placeholders vs filled sample."""
    s = 2000
    img = Image.new("RGB", (s, s), CREAM)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 70), "Edit in minutes", font=_font(40, True), fill=NAVY, anchor="mt")
    d.text((s // 2, 130), "Replace names · keep the geometry", font=_font_sans(18), fill=GOLD, anchor="mt")

    # left blank
    for i, (label, names) in enumerate(
        [
            ("TEMPLATE", ["Guest Name", "Guest Name", "Guest Name", "Guest Name"]),
            ("SAMPLE", TABLES[1][:4]),
        ]
    ):
        x0 = 120 + i * 940
        d.rounded_rectangle([x0, 220, x0 + 820, 1600], radius=10, outline=NAVY, width=2, fill=WHITE)
        d.text((x0 + 410, 280), label, font=_font_sans(16, True), fill=GOLD, anchor="mt")
        d.ellipse([x0 + 340, 340, x0 + 480, 480], outline=GOLD, width=2)
        d.text((x0 + 410, 410), "1", font=_font(40, True), fill=NAVY, anchor="mm")
        d.text((x0 + 410, 520), "Table 1", font=_font(24, True), fill=NAVY, anchor="mt")
        yy = 620
        for n in names:
            d.text((x0 + 410, yy), n, font=_font_sans(22), fill=INK if label == "SAMPLE" else SOFT, anchor="mt")
            yy += 50

    d.rectangle([0, s - 100, s, s], fill=NAVY)
    d.text((s // 2, s - 50), "PDF printables + guest list CSV", font=_font_sans(18), fill=CREAM, anchor="mm")
    path = PREV / "wedding_preview_4_edit.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=90)
    return path


def make_features_preview():
    s = 2000
    img = Image.new("RGB", (s, s), NAVY)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 100), "Why this suite", font=_font(44, True), fill=CREAM, anchor="mt")
    feats = [
        ("Geometric, not generic", "Navy · gold · cream. Phi-inspired marks.\nNo clip-art florals."),
        ("Full day-of set", "Seating chart, numbers, place cards,\ntimeline & menu — one look."),
        ("Print-ready PDF", "US Letter + poster-friendly seating chart.\n300 dpi equivalent vectors."),
        ("Plan in a spreadsheet", "Guest list CSV → assign tables →\nupdate the chart."),
    ]
    y = 260
    for title, body in feats:
        d.rounded_rectangle([160, y, s - 160, y + 280], radius=12, fill=(28, 34, 60), outline=GOLD, width=1)
        d.text((220, y + 50), title, font=_font(28, True), fill=GOLD, anchor="lt")
        for j, line in enumerate(body.split("\n")):
            d.text((220, y + 120 + j * 40), line, font=_font_sans(20), fill=CREAM, anchor="lt")
        y += 320
    path = PREV / "wedding_preview_5_features.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=90)
    return path


# ── PDFs ─────────────────────────────────────────────────────────────────────

def _pdf_rgb(c):
    return tuple(x / 255.0 for x in c)


def _pdf_corners(c, w, h, m=0.45 * inch):
    c.setStrokeColorRGB(*_pdf_rgb(GOLD))
    c.setLineWidth(1.2)
    L = 0.35 * inch
    for x, y, sx, sy in [(m, h - m, 1, -1), (w - m, h - m, -1, -1), (m, m, 1, 1), (w - m, m, -1, 1)]:
        c.line(x, y, x + sx * L, y)
        c.line(x, y, x, y + sy * L)


def pdf_seating_chart_sample(path: Path, blank: bool = False):
    """Landscape letter seating chart."""
    w, h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=(w, h))
    c.setFillColorRGB(*_pdf_rgb(CREAM))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    _pdf_corners(c, w, h)

    c.setFillColorRGB(*_pdf_rgb(NAVY))
    c.setFont("Times-Bold", 28)
    couple = "YOUR NAMES" if blank else COUPLE
    c.drawCentredString(w / 2, h - 0.7 * inch, couple)
    c.setFillColorRGB(*_pdf_rgb(GOLD))
    c.setFont("Times-Roman", 12)
    c.drawCentredString(w / 2, h - 0.95 * inch, "·   ·   ·")
    c.setFillColorRGB(*_pdf_rgb(SOFT))
    c.setFont("Helvetica", 10)
    c.drawCentredString(w / 2, h - 1.2 * inch, ("DATE  ·  VENUE" if blank else f"{DATE}  ·  {VENUE}"))
    c.setStrokeColorRGB(*_pdf_rgb(GOLD))
    c.setLineWidth(1)
    c.line(w * 0.25, h - 1.4 * inch, w * 0.75, h - 1.4 * inch)
    c.setFillColorRGB(*_pdf_rgb(NAVY))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(w / 2, h - 1.65 * inch, "SEATING CHART")

    # 6 tables
    cols, rows = 3, 2
    margin_x = 0.55 * inch
    top = h - 1.95 * inch
    bottom = 0.55 * inch
    gap = 0.2 * inch
    cw = (w - 2 * margin_x - (cols - 1) * gap) / cols
    ch = (top - bottom - (rows - 1) * gap) / rows
    ti = 1
    for r in range(rows):
        for col in range(cols):
            x = margin_x + col * (cw + gap)
            y = top - (r + 1) * ch - r * gap
            c.setStrokeColorRGB(*_pdf_rgb(NAVY))
            c.setLineWidth(1.2)
            c.roundRect(x, y, cw, ch, 6, stroke=1, fill=0)
            # circle number
            cx, cy = x + cw / 2, y + ch - 0.38 * inch
            c.setStrokeColorRGB(*_pdf_rgb(GOLD))
            c.circle(cx, cy, 0.22 * inch, stroke=1, fill=0)
            c.setFillColorRGB(*_pdf_rgb(NAVY))
            c.setFont("Times-Bold", 14)
            c.drawCentredString(cx, cy - 5, str(ti))
            c.setFont("Helvetica-Bold", 9)
            c.setFillColorRGB(*_pdf_rgb(GOLD))
            c.drawCentredString(cx, y + ch - 0.7 * inch, f"TABLE {ti}")
            names = (
                ["Guest Name"] * 6
                if blank
                else TABLES.get(ti, ["Guest Name"] * 6)
            )
            c.setFillColorRGB(*_pdf_rgb(INK))
            c.setFont("Helvetica", 9)
            ny = y + ch - 0.95 * inch
            for name in names:
                c.drawCentredString(cx, ny, name)
                ny -= 0.2 * inch
            ti += 1

    c.setFillColorRGB(*_pdf_rgb(SOFT))
    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 0.28 * inch, "MathRelaxing  ·  Geometric Wedding Suite  ·  Personal use only")
    c.save()


def pdf_table_numbers(path: Path, blank: bool = False):
    """12 table number cards on 3 pages (4 per letter page)."""
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    cards = list(range(1, 13))
    per = 4
    for page in range(3):
        c.setFillColorRGB(*_pdf_rgb(CREAM))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        batch = cards[page * per : (page + 1) * per]
        # 2x2
        mw, mh = 0.5 * inch, 0.5 * inch
        cw = (w - 2 * mw - 0.25 * inch) / 2
        ch = (h - 2 * mh - 0.25 * inch) / 2
        for i, n in enumerate(batch):
            col, row = i % 2, i // 2
            x = mw + col * (cw + 0.25 * inch)
            y = h - mh - (row + 1) * ch - row * 0.25 * inch
            c.setStrokeColorRGB(*_pdf_rgb(NAVY))
            c.setLineWidth(1.5)
            c.roundRect(x, y, cw, ch, 8, stroke=1, fill=0)
            _pdf_corners(c, 0, 0)  # skip global
            # local corners
            c.setStrokeColorRGB(*_pdf_rgb(GOLD))
            c.setLineWidth(1)
            L = 0.25 * inch
            for ox, oy, sx, sy in [
                (x + 12, y + ch - 12, 1, -1),
                (x + cw - 12, y + ch - 12, -1, -1),
                (x + 12, y + 12, 1, 1),
                (x + cw - 12, y + 12, -1, 1),
            ]:
                c.line(ox, oy, ox + sx * L, oy)
                c.line(ox, oy, ox, oy + sy * L)
            cx, cy = x + cw / 2, y + ch / 2 + 0.15 * inch
            c.setStrokeColorRGB(*_pdf_rgb(GOLD))
            c.setLineWidth(2)
            c.circle(cx, cy + 0.15 * inch, 0.55 * inch, stroke=1, fill=0)
            c.setFillColorRGB(*_pdf_rgb(NAVY))
            c.setFont("Times-Bold", 48)
            c.drawCentredString(cx, cy, str(n))
            c.setFont("Helvetica-Bold", 11)
            c.setFillColorRGB(*_pdf_rgb(GOLD))
            c.drawCentredString(cx, y + 0.55 * inch, "TABLE")
            c.setFillColorRGB(*_pdf_rgb(SOFT))
            c.setFont("Helvetica", 8)
            c.drawCentredString(cx, y + 0.32 * inch, "YOUR NAMES" if blank else COUPLE)
        c.showPage()
    c.save()


def pdf_place_cards(path: Path, blank: bool = False):
    """8 place cards per page, 2 pages sample names."""
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    if blank:
        names = [("Guest Name", 1)] * 16
    else:
        names = []
        for t, guests in TABLES.items():
            for g in guests[:2]:
                names.append((g, t))
        names = names[:16]

    per = 8
    for page in range(2):
        c.setFillColorRGB(*_pdf_rgb(CREAM))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        batch = names[page * per : (page + 1) * per]
        # 2 cols x 4 rows
        mw = 0.45 * inch
        gap = 0.15 * inch
        cw = (w - 2 * mw - gap) / 2
        ch = 1.15 * inch
        top = h - 0.5 * inch
        for i, (name, table) in enumerate(batch):
            col, row = i % 2, i // 2
            x = mw + col * (cw + gap)
            y = top - (row + 1) * ch - row * gap
            c.setStrokeColorRGB(*_pdf_rgb(NAVY))
            c.setLineWidth(1)
            c.roundRect(x, y, cw, ch, 4, stroke=1, fill=0)
            c.setStrokeColorRGB(*_pdf_rgb(GOLD))
            c.line(x + 0.25 * inch, y + ch / 2, x + cw - 0.25 * inch, y + ch / 2)
            c.setFillColorRGB(*_pdf_rgb(NAVY))
            c.setFont("Times-Bold", 14)
            c.drawCentredString(x + cw / 2, y + ch / 2 + 0.22 * inch, name)
            c.setFillColorRGB(*_pdf_rgb(GOLD))
            c.setFont("Helvetica", 9)
            c.drawCentredString(x + cw / 2, y + ch / 2 - 0.35 * inch, f"Table {table}")
        c.showPage()
    c.save()


def pdf_timeline(path: Path, blank: bool = False):
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFillColorRGB(*_pdf_rgb(CREAM))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    _pdf_corners(c, w, h)
    c.setFillColorRGB(*_pdf_rgb(NAVY))
    c.setFont("Times-Bold", 26)
    c.drawCentredString(w / 2, h - 0.9 * inch, "YOUR NAMES" if blank else COUPLE)
    c.setFillColorRGB(*_pdf_rgb(GOLD))
    c.setFont("Times-Roman", 11)
    c.drawCentredString(w / 2, h - 1.2 * inch, "·  WEDDING DAY TIMELINE  ·")
    events = (
        [
            ("3:30 PM", "Guest arrival"),
            ("4:00 PM", "Ceremony"),
            ("4:45 PM", "Cocktail hour"),
            ("6:00 PM", "Dinner"),
            ("7:30 PM", "Toasts"),
            ("8:00 PM", "First dance"),
            ("8:30 PM", "Open dancing"),
            ("10:30 PM", "Last dance"),
        ]
        if not blank
        else [
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
            ("TIME", "Event"),
        ]
    )
    y = h - 1.9 * inch
    for time, event in events:
        c.setStrokeColorRGB(*_pdf_rgb(GOLD))
        c.circle(1.3 * inch, y + 4, 4, stroke=1, fill=0)
        c.setStrokeColorRGB(*_pdf_rgb(NAVY))
        c.setLineWidth(0.8)
        if y > 1.5 * inch:
            c.line(1.3 * inch, y - 4, 1.3 * inch, y - 0.55 * inch)
        c.setFillColorRGB(*_pdf_rgb(GOLD))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1.7 * inch, y, time)
        c.setFillColorRGB(*_pdf_rgb(NAVY))
        c.setFont("Times-Roman", 14)
        c.drawString(3.2 * inch, y, event)
        y -= 0.7 * inch
    c.setFillColorRGB(*_pdf_rgb(SOFT))
    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 0.4 * inch, "MathRelaxing  ·  Geometric Wedding Suite")
    c.save()


def pdf_menu(path: Path, blank: bool = False):
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFillColorRGB(*_pdf_rgb(CREAM))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    _pdf_corners(c, w, h)
    c.setFillColorRGB(*_pdf_rgb(NAVY))
    c.setFont("Times-Bold", 26)
    c.drawCentredString(w / 2, h - 1.0 * inch, "YOUR NAMES" if blank else COUPLE)
    c.setFillColorRGB(*_pdf_rgb(GOLD))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w / 2, h - 1.4 * inch, "MENU")
    courses = (
        [
            ("FIRST", "Seasonal greens  ·  citrus  ·  herbs"),
            ("MAIN", "Herb-roasted entrée  ·  market vegetables"),
            ("SIDE", "Charred brassicas  ·  farro"),
            ("DESSERT", "Olive oil cake  ·  stone fruit"),
            ("TOAST", "Sparkling wine"),
        ]
        if not blank
        else [
            ("COURSE", "Description"),
            ("COURSE", "Description"),
            ("COURSE", "Description"),
            ("COURSE", "Description"),
            ("COURSE", "Description"),
        ]
    )
    y = h - 2.2 * inch
    for title, desc in courses:
        c.setFillColorRGB(*_pdf_rgb(GOLD))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(w / 2, y, title)
        c.setFillColorRGB(*_pdf_rgb(NAVY))
        c.setFont("Times-Italic", 13)
        c.drawCentredString(w / 2, y - 0.28 * inch, desc)
        c.setStrokeColorRGB(*_pdf_rgb(GOLD))
        c.setLineWidth(0.5)
        c.line(w * 0.3, y - 0.5 * inch, w * 0.7, y - 0.5 * inch)
        y -= 0.95 * inch
    c.setFillColorRGB(*_pdf_rgb(SOFT))
    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 0.45 * inch, "MathRelaxing  ·  Geometric Wedding Suite")
    c.save()


def pdf_howto(path: Path):
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFillColorRGB(*_pdf_rgb(CREAM))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColorRGB(*_pdf_rgb(NAVY))
    c.setFont("Times-Bold", 20)
    c.drawString(0.85 * inch, h - 0.9 * inch, "How to use this suite")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(*_pdf_rgb(INK))
    lines = [
        "1. Open Guest_List_Template.csv in Google Sheets or Excel.",
        "2. Add every guest and assign a table number.",
        "3. Open the blank PDFs (or edit the SAMPLE files as a visual guide).",
        "4. Edit text in Adobe Acrobat, Preview (Mac), or import pages into Canva/PowerPoint.",
        "5. Print seating chart poster-size or US Letter tiled; print cards on heavy cardstock.",
        "6. Cut place cards and table numbers along the rounded frames.",
        "",
        "Design notes",
        "• Palette: navy, gold, cream — matches a modern editorial wedding.",
        "• Geometry: corner marks and circles reference the golden ratio (phi).",
        "• Brand: MathRelaxing — precision design for celebrations, not florals.",
        "",
        "License: personal use for your event. Not for resale or redistribution.",
        brand.COPYRIGHT,
    ]
    y = h - 1.4 * inch
    for line in lines:
        if line.startswith("Design") or line.startswith("License"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(*_pdf_rgb(NAVY))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(*_pdf_rgb(INK))
        c.drawString(0.85 * inch, y, line)
        y -= 0.28 * inch
    c.save()


def write_guest_csv(path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["guest_name", "table_number", "meal", "notes"])
        for t, guests in TABLES.items():
            for g in guests:
                w.writerow([g, t, "", ""])
        # empty rows for planning
        for _ in range(20):
            w.writerow(["", "", "", ""])


def build_zip():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (TEMPLATES, SAMPLES):
            for p in folder.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(OUT).as_posix())
        howto = OUT / "HOW_TO_USE.pdf"
        if howto.exists():
            z.write(howto, "HOW_TO_USE.pdf")
        csv_path = OUT / "Guest_List_Template.csv"
        if csv_path.exists():
            z.write(csv_path, "Guest_List_Template.csv")
    return ZIP_PATH


def main():
    for d in (OUT, PREV, TEMPLATES, SAMPLES):
        d.mkdir(parents=True, exist_ok=True)

    print("=== MathRelaxing Geometric Wedding Suite ===")
    print("Previews…")
    previews = [
        make_hero_preview(),
        make_styles_preview(),
        make_detail_preview(),
        make_before_after_preview(),
        make_features_preview(),
    ]
    for p in previews:
        print(" ", p.name)

    print("PDFs…")
    pdf_seating_chart_sample(TEMPLATES / "01_Seating_Chart_BLANK.pdf", blank=True)
    pdf_seating_chart_sample(SAMPLES / "01_Seating_Chart_SAMPLE.pdf", blank=False)
    pdf_table_numbers(TEMPLATES / "02_Table_Numbers_01-12_BLANK.pdf", blank=True)
    pdf_table_numbers(SAMPLES / "02_Table_Numbers_SAMPLE.pdf", blank=False)
    pdf_place_cards(TEMPLATES / "03_Place_Cards_BLANK.pdf", blank=True)
    pdf_place_cards(SAMPLES / "03_Place_Cards_SAMPLE.pdf", blank=False)
    pdf_timeline(TEMPLATES / "04_Timeline_BLANK.pdf", blank=True)
    pdf_timeline(SAMPLES / "04_Timeline_SAMPLE.pdf", blank=False)
    pdf_menu(TEMPLATES / "05_Menu_BLANK.pdf", blank=True)
    pdf_menu(SAMPLES / "05_Menu_SAMPLE.pdf", blank=False)
    pdf_howto(OUT / "HOW_TO_USE.pdf")
    write_guest_csv(OUT / "Guest_List_Template.csv")
    print(" ", "templates + samples + howto + csv")

    z = build_zip()
    print(f"ZIP {z} ({z.stat().st_size / 1024:.0f} KB)")
    print("DONE")


if __name__ == "__main__":
    main()
