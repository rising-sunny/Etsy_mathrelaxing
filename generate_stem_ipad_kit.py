"""
generate_stem_ipad_kit.py — STEM Study OS stickers for iPad / GoodNotes
======================================================================
Digital accessory pack (no physical inventory):
  · 60+ PNG stickers (transparent) for GoodNotes / Notability / Procreate
  · Printable sticker sheet (optional)
  · 6 Etsy listing previews
  · ZIP deliverable

Aesthetic: editorial navy · cream · bronze (matches formula sheets / planners).
Positioning: "iPad accessories" digital lane from market research.

  python generate_stem_ipad_kit.py
"""
from __future__ import annotations

import math
import os
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
OUT = BASE / "stem_ipad_kit"
STICKERS = OUT / "stickers" / "png"
BY_MOD = OUT / "stickers" / "by_module"
SHEETS = OUT / "sheets"
PREVIEWS = OUT / "previews"
ZIP_PATH = OUT / "STEM_Study_OS_iPad_Stickers.zip"

# Palette
NAVY = (18, 23, 46)
NAVY2 = (28, 36, 68)
CREAM = (248, 244, 235)
GOLD = (154, 123, 79)
GOLD_LT = (201, 162, 75)
INK = (26, 26, 26)
SOFT = (92, 90, 86)
WHITE = (255, 255, 255)
SAGE = (90, 120, 100)
ROSE = (160, 90, 90)
BLUE = (70, 110, 150)
CLAY = (160, 120, 90)

S = 512  # sticker canvas


def _ensure():
    for d in (OUT, STICKERS, BY_MOD, SHEETS, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold=False, serif=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    if serif:
        names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    else:
        names = ["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _rr(draw, box, r, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def _shadow_pill(draw, box, r=28):
    # soft outer ring
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6], radius=r, fill=(0, 0, 0, 40))


def save_sticker(img: Image.Image, slug: str, module: str):
    img = img.convert("RGBA")
    path = STICKERS / f"{slug}.png"
    img.save(path)
    mod_dir = BY_MOD / module
    mod_dir.mkdir(parents=True, exist_ok=True)
    img.save(mod_dir / f"{slug}.png")
    return path


# ── sticker builders ─────────────────────────────────────────────────────────

def pill(label: str, bg, fg, slug: str, module: str, sub: str | None = None):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # white die-cut border
    margin = 48
    box = [margin, S // 2 - 70, S - margin, S // 2 + 70]
    d.rounded_rectangle([box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10], radius=40, fill=WHITE)
    d.rounded_rectangle(box, radius=34, fill=bg)
    f = _font(42 if len(label) < 14 else 34, bold=True)
    d.text((S // 2, S // 2 - (12 if sub else 0)), label, font=f, fill=fg, anchor="mm")
    if sub:
        d.text((S // 2, S // 2 + 28), sub, font=_font(20), fill=fg, anchor="mm")
    return save_sticker(img, slug, module)


def chip(label: str, bg, fg, slug: str, module: str):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # oval chip
    box = [60, S // 2 - 55, S - 60, S // 2 + 55]
    d.ellipse([box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8], fill=WHITE)
    d.ellipse(box, fill=bg)
    fs = 36 if len(label) < 12 else 28 if len(label) < 18 else 22
    d.text((S // 2, S // 2), label, font=_font(fs, bold=True), fill=fg, anchor="mm")
    return save_sticker(img, slug, module)


def symbol_badge(text: str, slug: str, module: str = "symbols"):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # cream circle + navy ring
    d.ellipse([70, 70, S - 70, S - 70], fill=WHITE)
    d.ellipse([88, 88, S - 88, S - 88], fill=CREAM)
    d.ellipse([88, 88, S - 88, S - 88], outline=GOLD, width=6)
    # math-ish size
    fs = 160 if len(text) == 1 else 100 if len(text) < 3 else 72
    d.text((S // 2, S // 2 + 8), text, font=_font(fs, bold=True, serif=True), fill=NAVY, anchor="mm")
    return save_sticker(img, slug, module)


def tab(label: str, slug: str, module: str = "tabs"):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # vertical-ish planner tab
    box = [S // 2 - 90, 80, S // 2 + 90, S - 80]
    d.rounded_rectangle([box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8], radius=28, fill=WHITE)
    d.rounded_rectangle(box, radius=22, fill=NAVY)
    d.rectangle([box[0], box[1], box[0] + 14, box[3]], fill=GOLD)
    d.text((S // 2 + 4, S // 2), label, font=_font(36, bold=True), fill=CREAM, anchor="mm")
    return save_sticker(img, slug, module)


def progress_ring(pct: int, slug: str):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, R, w = S // 2, S // 2, 160, 28
    d.ellipse([cx - R - 12, cy - R - 12, cx + R + 12, cy + R + 12], fill=WHITE)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(220, 215, 205), width=w)
    # arc
    if pct > 0:
        # PIL arcs: 0 is 3 o'clock, degrees counter-clockwise; we want from 12 o'clock
        start = -90
        end = -90 + int(360 * pct / 100)
        d.arc([cx - R, cy - R, cx + R, cy + R], start=start, end=end, fill=GOLD, width=w)
    d.text((cx, cy), f"{pct}%", font=_font(56, bold=True), fill=NAVY, anchor="mm")
    return save_sticker(img, slug, "progress")


def note_flag(label: str, slug: str, color=ROSE):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # flag shape
    pts = [
        (80, 100),
        (S - 80, 100),
        (S - 80, S - 140),
        (S // 2, S - 80),
        (80, S - 140),
    ]
    d.polygon([(p[0] + 4, p[1] + 6) for p in pts], fill=(0, 0, 0, 35))
    d.polygon(pts, fill=WHITE)
    inner = [(100, 118), (S - 100, 118), (S - 100, S - 160), (S // 2, S - 110), (100, S - 160)]
    d.polygon(inner, fill=color)
    d.text((S // 2, S // 2 - 10), label, font=_font(32 if len(label) < 12 else 26, bold=True), fill=CREAM, anchor="mm")
    return save_sticker(img, slug, "notes")


def build_all_stickers() -> list[Path]:
    paths = []
    # Status pills
    for slug, label, bg, fg in [
        ("status_studying", "Studying", NAVY, CREAM),
        ("status_exam_week", "Exam Week", ROSE, CREAM),
        ("status_problem_set", "Problem Set", BLUE, CREAM),
        ("status_lab_day", "Lab Day", SAGE, CREAM),
        ("status_office_hours", "Office Hours", CLAY, CREAM),
        ("status_done", "Done ✓", SAGE, CREAM),
        ("status_review", "Review", GOLD, NAVY),
        ("status_stuck", "Stuck", ROSE, CREAM),
        ("status_breakthrough", "Breakthrough", GOLD_LT, NAVY),
        ("status_group_study", "Group Study", BLUE, CREAM),
    ]:
        paths.append(pill(label, bg, fg, slug, "status"))

    # Subjects
    for slug, label, bg in [
        ("subj_calculus", "Calculus", NAVY),
        ("subj_linalg", "Linear Algebra", NAVY2),
        ("subj_vector", "Vector Calc", BLUE),
        ("subj_physics", "Physics", ROSE),
        ("subj_chemistry", "Chemistry", SAGE),
        ("subj_cs", "Computer Sci", CLAY),
        ("subj_stats", "Statistics", GOLD),
        ("subj_biology", "Biology", SAGE),
    ]:
        paths.append(chip(label, bg, CREAM if bg != GOLD else NAVY, slug, "subjects"))

    # Symbols
    for text, slug in [
        ("π", "sym_pi"),
        ("∫", "sym_integral"),
        ("Σ", "sym_sigma"),
        ("∞", "sym_infinity"),
        ("√", "sym_sqrt"),
        ("Δ", "sym_delta"),
        ("∇", "sym_nabla"),
        ("θ", "sym_theta"),
        ("λ", "sym_lambda"),
        ("≈", "sym_approx"),
        ("≠", "sym_neq"),
        ("∈", "sym_in"),
    ]:
        paths.append(symbol_badge(text, slug))

    # Progress
    for p in (0, 10, 25, 50, 75, 90, 100):
        paths.append(progress_ring(p, f"progress_{p}"))

    # Notes / annotation
    for label, slug, col in [
        ("Important", "note_important", ROSE),
        ("Formula", "note_formula", NAVY),
        ("Theorem", "note_theorem", GOLD),
        ("Prove later", "note_prove", CLAY),
        ("Check work", "note_check", SAGE),
        ("Counterex.", "note_counter", ROSE),
        ("Definition", "note_def", BLUE),
        ("Example", "note_example", NAVY2),
    ]:
        paths.append(note_flag(label, slug, col))

    # Energy / mood chips
    for slug, label, bg in [
        ("mood_focused", "Focused", NAVY),
        ("mood_coffee", "Coffee first", CLAY),
        ("mood_deep_work", "Deep work", NAVY2),
        ("mood_brain_fog", "Brain fog", SOFT),
        ("mood_flow", "In flow", SAGE),
        ("mood_deadline", "Deadline", ROSE),
    ]:
        paths.append(chip(label, bg, CREAM, slug, "mood"))

    # Planner tabs
    for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        paths.append(tab(day, f"tab_{day.lower()}", "tabs"))
    for w in range(1, 9):
        paths.append(tab(f"W{w}", f"tab_w{w}", "tabs"))

    # Mini utility
    for slug, label, bg in [
        ("util_due_today", "Due today", ROSE),
        ("util_due_week", "Due this week", GOLD),
        ("util_no_class", "No class", SAGE),
        ("util_office", "OH booked", BLUE),
        ("util_midterm", "Midterm", ROSE),
        ("util_final", "Final", NAVY),
    ]:
        paths.append(pill(label, bg, CREAM if bg != GOLD else NAVY, slug, "utility"))

    print(f"  {len(paths)} stickers")
    return paths


def build_sheet(paths: list[Path]):
    """Contact sheet of all stickers for print / listing."""
    cols = 8
    cell = 220
    pad = 20
    n = len(paths)
    rows = math.ceil(n / cols)
    W = cols * cell + (cols + 1) * pad
    H = rows * cell + (rows + 1) * pad + 80
    sheet = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((W // 2, 36), "STEM Study OS  ·  Sticker Sheet", font=_font(32, bold=True, serif=True), fill=NAVY, anchor="mm")
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        im = Image.open(p).convert("RGBA").resize((cell - 16, cell - 16), Image.Resampling.LANCZOS)
        x = pad + c * (cell + pad) + 8
        y = 80 + pad + r * (cell + pad) + 8
        # white tile
        d.rounded_rectangle([x - 4, y - 4, x + cell - 20, y + cell - 20], radius=16, fill=WHITE)
        sheet.paste(im, (x, y), im)
    out = SHEETS / "STEM_Study_OS_All_Stickers_Sheet.png"
    sheet.save(out)
    sheet.convert("RGB").save(SHEETS / "STEM_Study_OS_All_Stickers_Sheet.jpg", quality=92)
    print("  sheet", out.name)
    return out


def make_previews(sticker_paths: list[Path], sheet_path: Path):
    paths = []
    Sq = 1500

    # 1 hero
    img = Image.new("RGB", (Sq, Sq), NAVY)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 90), "STEM STUDY OS", font=_font(28, bold=True), fill=GOLD, anchor="mt")
    d.text((Sq // 2, 150), "iPad Stickers for GoodNotes", font=_font(48, bold=True, serif=True), fill=CREAM, anchor="mt")
    d.text((Sq // 2, 230), "Procreate  ·  Notability  ·  Digital planner", font=_font(24), fill=GOLD_LT, anchor="mt")
    # scatter sample stickers
    samples = sticker_paths[:: max(1, len(sticker_paths) // 12)][:12]
    positions = [
        (120, 320), (420, 300), (720, 340), (1020, 310),
        (180, 620), (480, 650), (780, 600), (1080, 640),
        (250, 920), (550, 900), (850, 940), (1150, 910),
    ]
    for i, (sp, pos) in enumerate(zip(samples, positions)):
        im = Image.open(sp).convert("RGBA").resize((280, 280), Image.Resampling.LANCZOS)
        img.paste(im, pos, im)
    d.rectangle([0, Sq - 100, Sq, Sq], fill=(12, 16, 32))
    d.text((Sq // 2, Sq - 50), "60+ stickers  ·  Instant download  ·  Transparent PNG", font=_font(22), fill=GOLD, anchor="mm")
    p = PREVIEWS / "stem_ipad_preview_1_hero.jpg"
    img.save(p, quality=92)
    paths.append(p)

    # 2 ipad mock frame
    img = Image.new("RGB", (Sq, Sq), CREAM)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 60), "Made for digital notebooks", font=_font(36, bold=True, serif=True), fill=NAVY, anchor="mt")
    # fake ipad
    frame = [180, 160, Sq - 180, Sq - 140]
    d.rounded_rectangle(frame, radius=40, fill=INK)
    d.rounded_rectangle([frame[0] + 18, frame[1] + 18, frame[2] - 18, frame[3] - 18], radius=28, fill=(245, 242, 235))
    # notebook lines
    for y in range(frame[1] + 80, frame[3] - 40, 36):
        d.line([(frame[0] + 50, y), (frame[2] - 50, y)], fill=(220, 215, 205), width=2)
    # stick stickers on "page"
    for i, sp in enumerate(sticker_paths[0:8]):
        im = Image.open(sp).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
        x = frame[0] + 60 + (i % 4) * 200
        y = frame[1] + 100 + (i // 4) * 280
        img.paste(im, (x, y), im)
    p = PREVIEWS / "stem_ipad_preview_2_ipad.jpg"
    img.save(p, quality=92)
    paths.append(p)

    # 3 modules
    img = Image.new("RGB", (Sq, Sq), CREAM)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 70), "Modules included", font=_font(42, bold=True, serif=True), fill=NAVY, anchor="mt")
    modules = [
        ("Status", "Studying, exams, lab…"),
        ("Subjects", "Calc, Physics, CS…"),
        ("Symbols", "π ∫ Σ ∞ ∇ θ"),
        ("Progress", "0% → 100% rings"),
        ("Notes", "Theorem, prove later…"),
        ("Tabs", "Days + weeks"),
    ]
    for i, (title, sub) in enumerate(modules):
        c, r = i % 2, i // 2
        x = 80 + c * 700
        y = 200 + r * 380
        d.rounded_rectangle([x, y, x + 640, y + 320], radius=20, fill=NAVY)
        d.text((x + 40, y + 100), title, font=_font(40, bold=True, serif=True), fill=GOLD, anchor="lt")
        d.text((x + 40, y + 180), sub, font=_font(26), fill=CREAM, anchor="lt")
    p = PREVIEWS / "stem_ipad_preview_3_modules.jpg"
    img.save(p, quality=92)
    paths.append(p)

    # 4 sheet
    img = Image.new("RGB", (Sq, Sq), CREAM)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 50), "Full sticker sheet", font=_font(36, bold=True, serif=True), fill=NAVY, anchor="mt")
    sh = Image.open(sheet_path).convert("RGB")
    sh.thumbnail((Sq - 120, Sq - 200), Image.Resampling.LANCZOS)
    img.paste(sh, ((Sq - sh.width) // 2, 120))
    p = PREVIEWS / "stem_ipad_preview_4_sheet.jpg"
    img.save(p, quality=92)
    paths.append(p)

    # 5 included
    img = Image.new("RGB", (Sq, Sq), NAVY)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 100), "What's included", font=_font(44, bold=True, serif=True), fill=CREAM, anchor="mt")
    items = [
        "60+ transparent PNG stickers",
        "Organized by module folders",
        "Printable contact sheet",
        "GoodNotes / Notability / Procreate ready",
        "Instant digital download (ZIP)",
    ]
    y = 280
    for it in items:
        d.rounded_rectangle([140, y, Sq - 140, y + 140], radius=16, outline=GOLD, width=3)
        d.text((200, y + 70), it, font=_font(28), fill=CREAM, anchor="lm")
        y += 180
    p = PREVIEWS / "stem_ipad_preview_5_included.jpg"
    img.save(p, quality=92)
    paths.append(p)

    # 6 howto
    img = Image.new("RGB", (Sq, Sq), CREAM)
    d = ImageDraw.Draw(img)
    d.text((Sq // 2, 80), "How to use", font=_font(44, bold=True, serif=True), fill=NAVY, anchor="mt")
    steps = [
        ("1", "Download ZIP", "Unzip on Mac / PC / iPad Files"),
        ("2", "Import PNGs", "GoodNotes Elements or Photos"),
        ("3", "Stamp freely", "Resize, rotate, layer on notes"),
        ("4", "Study better", "Track status, subjects, progress"),
    ]
    for i, (n, t, s) in enumerate(steps):
        y = 220 + i * 280
        d.ellipse([120, y, 220, y + 100], outline=GOLD, width=4)
        d.text((170, y + 50), n, font=_font(36, bold=True), fill=GOLD, anchor="mm")
        d.text((280, y + 30), t, font=_font(34, bold=True, serif=True), fill=NAVY, anchor="lt")
        d.text((280, y + 90), s, font=_font(26), fill=SOFT, anchor="lt")
    p = PREVIEWS / "stem_ipad_preview_6_howto.jpg"
    img.save(p, quality=92)
    paths.append(p)

    print(f"  {len(paths)} previews")
    return paths


def build_zip(sticker_paths: list[Path]):
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sticker_paths:
            z.write(p, f"PNG_individual/{p.name}")
        # by module
        for mod in BY_MOD.iterdir():
            if mod.is_dir():
                for p in mod.glob("*.png"):
                    z.write(p, f"PNG_by_module/{mod.name}/{p.name}")
        for p in SHEETS.glob("*"):
            z.write(p, f"Sheets/{p.name}")
        z.writestr(
            "READ_ME.txt",
            """STEM Study OS — iPad Stickers
================================

Transparent PNG stickers for digital notebooks.

INCLUDED
  PNG_individual/     all stickers flat
  PNG_by_module/      status, subjects, symbols, progress, notes, mood, tabs, utility
  Sheets/             printable contact sheet

APPS
  GoodNotes, Notability, Procreate, Freeform, Notes, Keynote…

HOW TO IMPORT (GoodNotes)
  1. Unzip the download
  2. Elements → + → Import images
  3. Select PNGs (or a whole module folder)

Personal use. Not for redistribution or resale.
""",
        )
    print("ZIP", ZIP_PATH, f"({ZIP_PATH.stat().st_size // 1024} KB)")


def main():
    _ensure()
    print("Building STEM Study OS iPad stickers…")
    stickers = build_all_stickers()
    sheet = build_sheet(stickers)
    make_previews(stickers, sheet)
    build_zip(stickers)
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
