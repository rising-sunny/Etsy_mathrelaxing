"""
build_atelier_previews.py — Rich listing mockups for Atelier Resume Kit
=======================================================================
Generates 10 square previews (1500²) reflecting the expanded kit.

  python build_atelier_previews.py
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
OUT = BASE / "resume_luxe_kit" / "previews"
BG = BASE / "resume_luxe_kit" / "backgrounds"

NAVY = (18, 23, 46)
GOLD = (201, 162, 75)
CREAM = (248, 244, 235)
INK = (26, 26, 26)
SOFT = (92, 90, 86)
WHITE = (255, 255, 255)
DESK = (228, 224, 216)

S = 2000


def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _sans(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=93, optimize=True)
    print(f"  {name}")
    return path


def _shadow_page(base: Image.Image, x, y, w, h, blur=18, off=16):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([x + off, y + off, x + w + off, y + h + off], fill=(0, 0, 0, 100))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert("RGBA"), sh).convert("RGB")


def _mini_atelier(d, x, y, w, h, label=None):
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=NAVY, width=2)
    cx = x + w // 2
    d.text((cx, y + int(h * 0.06)), "C E L I N E   M O R A", font=_font(max(11, int(w * 0.055)), True), fill=NAVY, anchor="mt")
    ly = y + int(h * 0.12)
    d.line([(cx - w * 0.22, ly), (cx + w * 0.22, ly)], fill=GOLD, width=1)
    d.line([(cx - w * 0.22, ly + 5), (cx + w * 0.22, ly + 5)], fill=GOLD, width=2)
    d.text((cx, ly + 18), "Applied Research Lead", font=_sans(max(9, int(w * 0.035))), fill=GOLD, anchor="mt")
    yy = y + int(h * 0.22)
    for title, n in [("PROFILE", 2), ("EXPERIENCE", 4), ("EDUCATION", 2)]:
        d.text((x + w * 0.1, yy), title, font=_font(max(9, int(w * 0.032)), True), fill=NAVY, anchor="lt")
        yy += int(h * 0.035)
        d.line([(x + w * 0.1, yy), (x + w * 0.9, yy)], fill=GOLD, width=1)
        yy += int(h * 0.02)
        for _ in range(n):
            d.rectangle([x + w * 0.1, yy, x + w * 0.9, yy + max(4, int(h * 0.012))], fill=(220, 215, 205))
            yy += int(h * 0.03)
        yy += int(h * 0.02)
    if label:
        d.text((cx, y + h + 28), label, font=_sans(14, True), fill=GOLD, anchor="mt")


def _mini_gallery(d, x, y, w, h, label=None):
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=NAVY, width=2)
    d.rectangle([x + 16, y + 18, x + w - 16, y + 26], fill=GOLD)
    d.text((x + 22, y + 45), "CELINE MORA", font=_font(max(14, int(w * 0.07)), True), fill=NAVY, anchor="lt")
    d.text((x + 22, y + 80), "Applied Research Lead", font=_sans(max(10, int(w * 0.04))), fill=GOLD, anchor="lt")
    yy = y + 120
    for title in ["▸ SUMMARY", "▸ EXPERIENCE", "▸ EDUCATION"]:
        d.text((x + 22, yy), title, font=_font(max(10, int(w * 0.035)), True), fill=NAVY, anchor="lt")
        yy += int(h * 0.04)
        d.line([(x + 22, yy), (x + w - 22, yy)], fill=NAVY, width=1)
        yy += 12
        for _ in range(3):
            d.rectangle([x + 22, yy, x + w - 22, yy + 8], fill=(220, 215, 205))
            yy += 22
        yy += 10
    if label:
        d.text((x + w // 2, y + h + 28), label, font=_sans(14, True), fill=GOLD, anchor="mt")


def _footer(d, text, bg=NAVY):
    d.rectangle([0, S - 100, S, S], fill=bg)
    d.text((S // 2, S - 50), text, font=_sans(18), fill=GOLD, anchor="mm")


def p1_hero():
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "ATELIER", font=_sans(15, True), fill=GOLD, anchor="mt")
    d.text((S // 2, 110), "Resume Kit", font=_font(48, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 185), "5 layouts  ·  5 background styles  ·  full application set", font=_sans(17), fill=GOLD, anchor="mt")
    pw, ph = 780, 1020
    px, py = (S - pw) // 2, 260
    img = _shadow_page(img, px, py, pw, ph)
    d = ImageDraw.Draw(img)
    _mini_atelier(d, px, py, pw, ph)
    _footer(d, "MathRelaxing  ·  Quiet luxury on the page")
    return _save(img, "luxe_preview_01_hero.jpg")


def p2_layouts():
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "Five layout systems", font=_font(36, True), fill=NAVY, anchor="mt")
    d.text((S // 2, 115), "One persona  ·  distinct presence", font=_sans(16), fill=GOLD, anchor="mt")
    labels = ["Atelier", "Gallery", "Manuscript", "Architect", "ATS"]
    cw, ch = 320, 1200
    gap = 28
    total = 5 * cw + 4 * gap
    x0 = (S - total) // 2
    y0 = 180
    for i, lab in enumerate(labels):
        x = x0 + i * (cw + gap)
        if i == 0:
            _mini_atelier(d, x, y0, cw, ch)
        elif i == 1:
            _mini_gallery(d, x, y0, cw, ch)
        elif i == 2:
            d.rectangle([x, y0, x + cw, y0 + ch], fill=CREAM, outline=NAVY, width=2)
            d.text((x + cw // 2, y0 + 50), "CELINE MORA", font=_font(16, True), fill=NAVY, anchor="mt")
            d.text((x + cw // 2, y0 + 90), "—  ·  —", font=_font(12), fill=GOLD, anchor="mt")
            yy = y0 + 140
            for _ in range(14):
                d.rectangle([x + 30, yy, x + cw - 30, yy + 8], fill=(220, 215, 205))
                yy += 28
        elif i == 3:
            d.rectangle([x, y0, x + cw, y0 + ch], fill=CREAM, outline=NAVY, width=2)
            d.line([(x + 20, y0 + 30), (x + cw - 20, y0 + 30)], fill=GOLD, width=3)
            d.line([(x + 20, y0 + 38), (x + cw - 20, y0 + 38)], fill=NAVY, width=2)
            d.text((x + 24, y0 + 60), "CELINE", font=_font(22, True), fill=NAVY, anchor="lt")
            d.text((x + 24, y0 + 100), "MORA", font=_font(22, True), fill=NAVY, anchor="lt")
            yy = y0 + 180
            for _ in range(12):
                d.rectangle([x + 24, yy, x + cw - 24, yy + 8], fill=(220, 215, 205))
                yy += 30
        else:
            d.rectangle([x, y0, x + cw, y0 + ch], fill=WHITE, outline=SOFT, width=2)
            d.text((x + cw // 2, y0 + 50), "CELINE MORA", font=_sans(15, True), fill=INK, anchor="mt")
            d.text((x + cw // 2, y0 + 85), "Research Lead | Strategy", font=_sans(11), fill=SOFT, anchor="mt")
            yy = y0 + 130
            for _ in range(14):
                d.rectangle([x + 28, yy, x + cw - 28, yy + 7], fill=(230, 230, 230))
                yy += 26
        d.text((x + cw // 2, y0 + ch + 35), lab.upper(), font=_sans(13, True), fill=GOLD, anchor="mt")
    _footer(d, "Atelier · Gallery · Manuscript · Architect · ATS", NAVY)
    return _save(img, "luxe_preview_02_layouts.jpg")


def p3_styles():
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 60), "Atelier background styles", font=_font(34, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 120), "Semi-transparent plates already inside the Word files", font=_sans(16), fill=GOLD, anchor="mt")
    styles = [
        ("cream_veil", "Cream Veil"),
        ("scientific_grid", "Scientific Grid"),
        ("gold_geometry", "Gold Geometry"),
        ("phi_whisper", "Phi Whisper"),
        ("navy_edge", "Navy Edge"),
    ]
    tw, th = 320, 480
    gap = 36
    total = 5 * tw + 4 * gap
    x0 = (S - total) // 2
    y0 = 220
    for i, (key, label) in enumerate(styles):
        x = x0 + i * (tw + gap)
        card = Image.new("RGB", (tw, th), CREAM)
        bg_path = BG / f"bg_{key}.png"
        if bg_path.is_file():
            bg = Image.open(bg_path).convert("RGBA")
            bg = bg.resize((tw - 16, th - 70), Image.Resampling.LANCZOS)
            base = Image.new("RGBA", (tw - 16, th - 70), (*CREAM, 255))
            base = Image.alpha_composite(base, bg)
            card.paste(base.convert("RGB"), (8, 8))
        cd = ImageDraw.Draw(card)
        # mini name on top of style
        cd.text((tw // 2, 40), "C E L I N E", font=_font(14, True), fill=NAVY, anchor="mt")
        cd.line([(40, 70), (tw - 40, 70)], fill=GOLD, width=2)
        cd.text((tw // 2, th - 32), label, font=_sans(13, True), fill=NAVY, anchor="mm")
        img.paste(card, (x, y0))
        d = ImageDraw.Draw(img)
    d.rectangle([0, S - 280, S, S], fill=(10, 12, 26))
    d.text((S // 2, S - 220), "Plus free PNG pack to restyle in Word", font=_sans(18), fill=GOLD, anchor="mt")
    d.text((S // 2, S - 150), "Cream Veil  ·  Scientific Grid  ·  Gold Geometry", font=_sans(16), fill=CREAM, anchor="mt")
    d.text((S // 2, S - 100), "Phi Whisper  ·  Navy Edge", font=_sans(16), fill=CREAM, anchor="mt")
    return _save(img, "luxe_preview_03_styles.jpg")


def p4_application():
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 60), "Full application set", font=_font(38, True), fill=NAVY, anchor="mt")
    d.text((S // 2, 125), "Everything that travels with the resume", font=_sans(17), fill=GOLD, anchor="mt")
    pieces = [
        ("01", "Cover letter", "Atelier header\nmatching tone"),
        ("02", "References", "Three polished\nreference slots"),
        ("03", "Thank-you note", "Post-interview\nemail draft"),
        ("04", "LinkedIn pack", "Headline + About\nready to paste"),
        ("05", "Portfolio", "One-pager of\nselected work"),
        ("06", "How-to PDF", "Layouts guide\n& workflow"),
    ]
    cw, ch = 560, 440
    gap = 40
    x0 = (S - 3 * cw - 2 * gap) // 2
    y0 = 200
    for i, (num, title, sub) in enumerate(pieces):
        c, r = i % 3, i // 3
        x = x0 + c * (cw + gap)
        y = y0 + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14, fill=NAVY)
        d.ellipse([x + 36, y + 36, x + 110, y + 110], outline=GOLD, width=3)
        d.text((x + 73, y + 73), num, font=_font(18, True), fill=GOLD, anchor="mm")
        d.text((x + 40, y + 150), title, font=_font(28, True), fill=CREAM, anchor="lt")
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 40, y + 230 + j * 40), line, font=_sans(18), fill=GOLD, anchor="lt")
    _footer(d, "Blank + filled SAMPLE for every major document")
    return _save(img, "luxe_preview_04_application.jpg")


def p5_detail_skills():
    img = Image.new("RGB", (S, S), DESK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([160, 220, 1840, 1580], radius=12, fill=CREAM)
    d.text((1000, 320), "C E L I N E   M O R A", font=_font(40, True), fill=NAVY, anchor="mt")
    d.line([(620, 420), (1380, 420)], fill=GOLD, width=1)
    d.line([(620, 432), (1380, 432)], fill=GOLD, width=3)
    d.text((1000, 480), "Applied Research Lead  ·  Product Strategy", font=_font(20), fill=GOLD, anchor="mt")
    d.text((1000, 560), "celine.mora@email.com  ·  New York, NY", font=_sans(15), fill=SOFT, anchor="mt")
    # skills cards
    cards = [
        ("CORE", "Causal inference\nExperimentation\nBayesian modeling"),
        ("TOOLS", "Python  ·  SQL  ·  R\nStan  ·  dbt\nTableau  ·  Looker"),
        ("LEAD", "Research ops\nNarrative design\nMentorship"),
    ]
    cw = 420
    gap = 40
    x0 = (S - 3 * cw - 2 * gap) // 2
    for i, (lab, body) in enumerate(cards):
        x = x0 + i * (cw + gap)
        y = 700
        d.rounded_rectangle([x, y, x + cw, y + 520], radius=10, outline=NAVY, width=2)
        d.text((x + cw // 2, y + 40), lab, font=_sans(16, True), fill=GOLD, anchor="mt")
        for j, line in enumerate(body.split("\n")):
            d.text((x + cw // 2, y + 120 + j * 50), line, font=_sans(18), fill=NAVY, anchor="mt")
    _footer(d, "Layered capabilities — not a single skills dump")
    return _save(img, "luxe_preview_05_skills.jpg")


def p6_blank_vs_sample():
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 60), "Template  →  Sample", font=_font(36, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 125), "Every major file ships blank + filled", font=_sans(17), fill=GOLD, anchor="mt")
    # left blank
    for i, (title, lines) in enumerate(
        [
            ("TEMPLATE", ["YOUR FULL NAME", "Target Role  ·  Focus", "Outcome with metric.", "Degree  ·  School"]),
            ("SAMPLE", ["CELINE MORA", "Applied Research Lead", "+9% activation · $18M ARR", "Ph.D. Columbia"]),
        ]
    ):
        x = 140 + i * 900
        d.rounded_rectangle([x, 220, x + 820, 1600], radius=12, fill=CREAM)
        d.text((x + 410, 280), title, font=_sans(16, True), fill=GOLD, anchor="mt")
        d.ellipse([x + 340, 340, x + 480, 480], outline=GOLD, width=3)
        d.text((x + 410, 410), "A" if i == 1 else "?", font=_font(36, True), fill=NAVY, anchor="mm")
        yy = 540
        for line in lines:
            col = NAVY if i == 1 else SOFT
            d.text((x + 410, yy), line, font=_font(20, True) if yy == 540 else _sans(18), fill=col, anchor="mt")
            yy += 70
            d.line([(x + 120, yy - 20), (x + 700, yy - 20)], fill=(220, 215, 205), width=1)
    _footer(d, "Learn the rhythm from SAMPLE  ·  personalize TEMPLATE", (8, 10, 22))
    return _save(img, "luxe_preview_06_blank_sample.jpg")


def p7_manuscript_architect():
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "Two more editorial voices", font=_font(34, True), fill=NAVY, anchor="mt")
    # manuscript
    x, y, w, h = 120, 180, 820, 1400
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=NAVY, width=2)
    d.text((x + w // 2, y + 60), "CELINE MORA", font=_font(26, True), fill=NAVY, anchor="mt")
    d.text((x + w // 2, y + 120), "—  ·  —", font=_font(16), fill=GOLD, anchor="mt")
    d.text((x + w // 2, y + 170), "Applied Research Lead", font=_font(14), fill=SOFT, anchor="mt")
    yy = y + 260
    for sec in ["·  PROFILE  ·", "·  EXPERIENCE  ·", "·  EDUCATION  ·"]:
        d.text((x + w // 2, yy), sec, font=_font(13, True), fill=NAVY, anchor="mt")
        yy += 40
        for _ in range(4):
            d.rectangle([x + 80, yy, x + w - 80, yy + 8], fill=(220, 215, 205))
            yy += 28
        yy += 30
    d.text((x + w // 2, y + h + 40), "MANUSCRIPT", font=_sans(16, True), fill=GOLD, anchor="mt")
    # architect
    x = 1060
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=NAVY, width=2)
    d.line([(x + 40, y + 40), (x + w - 40, y + 40)], fill=GOLD, width=3)
    d.line([(x + 40, y + 50), (x + w - 40, y + 50)], fill=NAVY, width=2)
    d.text((x + 50, y + 80), "CELINE", font=_font(36, True), fill=NAVY, anchor="lt")
    d.text((x + 50, y + 140), "MORA", font=_font(36, True), fill=NAVY, anchor="lt")
    d.text((x + 50, y + 220), "Applied Research Lead  ·  Product Strategy", font=_sans(14), fill=GOLD, anchor="lt")
    yy = y + 300
    for sec in ["PROFILE", "CAPABILITIES", "EXPERIENCE"]:
        d.text((x + 50, yy), sec, font=_font(14, True), fill=NAVY, anchor="lt")
        yy += 28
        d.line([(x + 50, yy), (x + 280, yy)], fill=GOLD, width=2)
        yy += 20
        for _ in range(4):
            d.rectangle([x + 50, yy, x + w - 50, yy + 9], fill=(220, 215, 205))
            yy += 28
        yy += 24
    d.text((x + w // 2, y + h + 40), "ARCHITECT", font=_sans(16, True), fill=GOLD, anchor="mt")
    _footer(d, "Literary calm  ·  Geometric modern")
    return _save(img, "luxe_preview_07_more_layouts.jpg")


def p8_file_inventory():
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "What's in the ZIP", font=_font(40, True), fill=CREAM, anchor="mt")
    cols = [
        (
            "Resumes",
            [
                "Atelier blank + sample",
                "Gallery blank + sample",
                "Manuscript blank + sample",
                "Architect blank + sample",
                "ATS blank + sample",
                "5× Atelier style variants",
            ],
        ),
        (
            "Application",
            [
                "Cover letter",
                "References",
                "Thank-you note",
                "LinkedIn pack",
                "Portfolio one-pager",
                "All with SAMPLE files",
            ],
        ),
        (
            "Extras",
            [
                "Background PNG pack",
                "Styles contact sheet",
                "How-to PDF",
                "Sample resume PDF",
                "Celine Mora persona",
                "Word .docx editable",
            ],
        ),
    ]
    cw = 540
    gap = 40
    x0 = (S - 3 * cw - 2 * gap) // 2
    for i, (head, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        d.rounded_rectangle([x, 200, x + cw, 1650], radius=14, fill=(28, 34, 58), outline=GOLD, width=1)
        d.text((x + cw // 2, 260), head.upper(), font=_sans(18, True), fill=GOLD, anchor="mt")
        yy = 360
        for item in items:
            d.ellipse([x + 50, yy + 6, x + 70, yy + 26], outline=GOLD, width=2)
            d.text((x + 95, yy), item, font=_sans(18), fill=CREAM, anchor="lt")
            yy += 70
    _footer(d, "20+ Word documents  ·  ready to personalize", (8, 10, 22))
    return _save(img, "luxe_preview_08_inventory.jpg")


def p9_use_cases():
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "When to use which", font=_font(38, True), fill=NAVY, anchor="mt")
    rows = [
        ("Atelier", "Email PDF · senior / research · maximum polish"),
        ("Gallery", "Product · design-adjacent · modern left align"),
        ("Manuscript", "Writing-forward · academic-adjacent · classic"),
        ("Architect", "Bold modern brands · geometric confidence"),
        ("ATS", "Workday / Greenhouse / LinkedIn Easy Apply"),
        ("Styles", "Swap background plate without redesigning type"),
    ]
    y = 200
    for title, body in rows:
        d.rounded_rectangle([140, y, S - 140, y + 220], radius=12, outline=NAVY, width=2)
        d.rectangle([140, y, 200, y + 220], fill=GOLD)
        d.text((240, y + 50), title, font=_font(26, True), fill=NAVY, anchor="lt")
        d.text((240, y + 120), body, font=_sans(20), fill=SOFT, anchor="lt")
        y += 250
    _footer(d, "Match the system to the room you're walking into")
    return _save(img, "luxe_preview_09_usecases.jpg")


def p10_value():
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 90), "Premium kit, complete system", font=_font(36, True), fill=CREAM, anchor="mt")
    stats = [
        ("20+", "Word files"),
        ("5", "Layouts"),
        ("5", "BG styles"),
        ("6", "App pieces"),
        ("2", "PDFs"),
        ("$12.99", "One price"),
    ]
    for i, (n, lab) in enumerate(stats):
        c, r = i % 3, i // 3
        x = 160 + c * 580
        y = 280 + r * 520
        d.rounded_rectangle([x, y, x + 520, y + 440], radius=16, outline=GOLD, width=2)
        d.text((x + 260, y + 130), n, font=_font(56, True), fill=GOLD, anchor="mt")
        d.text((x + 260, y + 280), lab, font=_sans(22), fill=CREAM, anchor="mt")
    _footer(d, "MathRelaxing Atelier  ·  Not a single blank page", (8, 10, 22))
    return _save(img, "luxe_preview_10_value.jpg")


def main():
    print("Building 10 Atelier previews…")
    paths = [
        p1_hero(),
        p2_layouts(),
        p3_styles(),
        p4_application(),
        p5_detail_skills(),
        p6_blank_vs_sample(),
        p7_manuscript_architect(),
        p8_file_inventory(),
        p9_use_cases(),
        p10_value(),
    ]
    # remove obsolete preview names to avoid confusion
    for old in OUT.glob("luxe_preview_*.jpg"):
        if old not in paths and old.name.startswith("luxe_preview_") and not old.name[14:16].isdigit():
            # keep only numbered 01-10 style - delete old unnumbered leftovers carefully
            pass
    for old_name in [
        "luxe_preview_1_hero.jpg",
        "luxe_preview_2_layouts.jpg",
        "luxe_preview_3_included.jpg",
        "luxe_preview_3_styles.jpg",
        "luxe_preview_4_detail.jpg",
        "luxe_preview_4_set.jpg",
        "luxe_preview_5_detail.jpg",
        "luxe_preview_5_features.jpg",
        "luxe_preview_6_value.jpg",
    ]:
        p = OUT / old_name
        if p.exists():
            p.unlink()
            print(f"  removed old {old_name}")
    print(f"OK {len(paths)} previews → {OUT}")


if __name__ == "__main__":
    main()
