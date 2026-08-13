"""
build_kit_previews.py — Etsy listing images for the STEM Student Study Kit.

A bundle lives or dies on whether the buyer can see what they get, so every
thumbnail here is pulled from the actual shipped ZIP rather than mocked up --
if a page changes, the preview changes with it.

  python stem_study_kit/build_kit_previews.py
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ZIP = HERE / "STEM_Student_Complete_Study_Kit.zip"
OUT = HERE / "previews"
OUT.mkdir(exist_ok=True)

AF = ROOT / "lulu_books" / "assets" / "fonts"
CINZEL = str(AF / "Cinzel-SemiBold.ttf")
RALEWAY = str(AF / "Raleway.ttf")
RALEWAY_I = str(AF / "Raleway-Italic.ttf")

CREAM = (245, 242, 234)
PAPER = (252, 250, 245)
INK = (38, 35, 30)
SOFT = (122, 116, 104)
RUST = (176, 88, 56)
LINE = (214, 207, 192)

S = 2000  # square listing images


def F(path, size):
    return ImageFont.truetype(path, size)


def load(zf, name, box):
    """Thumbnail a page from the zip, letterboxed into box (w,h) on paper."""
    img = Image.open(io.BytesIO(zf.read(name))).convert("RGB")
    img.thumbnail(box, Image.LANCZOS)
    cell = Image.new("RGB", box, PAPER)
    cell.paste(img, ((box[0] - img.width) // 2, (box[1] - img.height) // 2))
    return cell


def framed(cell, pad=8):
    out = Image.new("RGB", (cell.width + pad * 2, cell.height + pad * 2), PAPER)
    out.paste(cell, (pad, pad))
    ImageDraw.Draw(out).rectangle([0, 0, out.width - 1, out.height - 1], outline=LINE, width=3)
    return out


def header(d, title, sub):
    d.rectangle([0, 0, S, 250], fill=INK)
    d.text((S // 2, 78), title, font=F(CINZEL, 76), fill=CREAM, anchor="mm")
    d.text((S // 2, 168), sub, font=F(RALEWAY, 40), fill=(198, 190, 175), anchor="mm")


def grid_sheet(zf, names, cols, title, sub, fname):
    canvas = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(canvas)
    header(d, title, sub)
    rows = (len(names) + cols - 1) // cols
    gap = 34
    head_h = 250
    # Constrain the cell by BOTH axes. Sizing on width alone (cw * 1.35) made
    # three rows taller than the canvas, so the grid ran off the bottom and
    # the first row covered the header.
    cw = (S - gap * (cols + 1)) // cols
    ch_fit = (S - head_h - gap * (rows + 1)) // rows
    ch = min(int(cw * 1.35), ch_fit)
    grid_h = rows * ch + (rows + 1) * gap
    top = head_h + (S - head_h - grid_h) // 2 + gap
    for i, n in enumerate(names):
        r, c = divmod(i, cols)
        cell = framed(load(zf, n, (cw - 16, ch - 16)))
        x = gap + c * (cw + gap) + (cw - cell.width) // 2
        y = top + r * (ch + gap) + (ch - cell.height) // 2
        canvas.paste(cell, (x, y))
    canvas.save(OUT / fname, "JPEG", quality=92)
    print("  ", fname)


def included_sheet(zf):
    canvas = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(canvas)
    header(d, "WHAT'S INCLUDED", "one instant download  ·  A4 and US Letter")
    names = zf.namelist()

    def n_in(prefix, ext=None):
        return sum(1 for x in names if x.startswith(prefix) and (ext is None or x.lower().endswith(ext)))

    rows = [
        ("4", "Formula sheets", "calculus · linear algebra · vector calculus · physics"),
        ("1", "Unit circle reference", "every special angle, degrees and radians"),
        ("10", "Grid paper styles", "square · dot · isometric · hexagonal · Cornell · log-log · polar"),
        ("2", "Notebooks", "STEM lab notebook and mixed-grid problem notebook"),
        (str(n_in("05_Cornell")), "Cornell, lab and syllabus pages", "note pages, lab reports, term planners"),
        (str(n_in("06_Binder")), "Binder covers and spines", "maths · physics · chemistry · biology and more"),
        ("1", "STEM focus planner", "undated weekly planning, habit and research logs"),
        (str(n_in("07_Planner/stickers")), "Maths stickers", "PNG, for digital planners or printing"),
    ]
    y = 340
    for num, title, sub in rows:
        d.ellipse([120, y, 120 + 104, y + 104], fill=RUST)
        d.text((172, y + 52), num, font=F(CINZEL, 44 if len(num) < 3 else 34), fill=CREAM, anchor="mm")
        d.text((272, y + 24), title, font=F(CINZEL, 46), fill=INK)
        d.text((272, y + 80), sub, font=F(RALEWAY_I, 32), fill=SOFT)
        y += 148

    d.rectangle([120, y + 16, S - 120, y + 22], fill=LINE)
    d.text((S // 2, y + 84), "300 dpi  ·  print at home or a copy shop  ·  nothing is dated",
           font=F(RALEWAY, 34), fill=SOFT, anchor="mm")
    canvas.save(OUT / "02_included.jpg", "JPEG", quality=92)
    print("   02_included.jpg")


def main():
    with zipfile.ZipFile(ZIP) as zf:
        names = zf.namelist()

        def pick(prefix, n, ext=(".jpg",)):
            """Every printable ships as an A4/US Letter pair that looks
            near-identical, so show only one of each -- otherwise the grids
            fill up with visual duplicates."""
            got = [x for x in sorted(names)
                   if x.startswith(prefix) and x.lower().endswith(ext)
                   and "_us_letter" not in x.lower() and not x.lower().endswith("_letter.jpg")]
            return got[:n]

        def pick_each(prefix, stems):
            """One page per named stem. Alphabetical order buries the variety
            in folder 05 -- six near-identical cornell_blank_* pages sort ahead
            of the lab reports and syllabus pages, so a plain pick() showed the
            buyer the same ruled page six times under a title promising three
            different things."""
            out = []
            for s in stems:
                hit = [x for x in sorted(names)
                       if x.startswith(f"{prefix}/{s}") and x.endswith("_A4.jpg")]
                if not hit:
                    raise KeyError(f"{prefix}/{s}*_A4.jpg no está en el ZIP")
                out.append(hit[0])
            return out

        NOTES = ["cornell_guide", "cornell_blank_01", "lab_report_01_front",
                 "lab_report_03_data", "syllabus_01_overview", "syllabus_02_grading"]

        hero = (pick("01_Formula_Sheets", 3) + pick("02_Reference", 1)
                + pick_each("05_Cornell_Lab_Syllabus",
                            ["cornell_blank_01", "lab_report_02_methods", "syllabus_01_overview"])
                + pick("06_Binder_Covers", 2))
        grid_sheet(zf, hero[:9], 3,
                   "STEM STUDENT STUDY KIT", "formula sheets · grids · notebooks · planners",
                   "01_hero.jpg")

        included_sheet(zf)

        grid_sheet(zf, [x for x in sorted(names)
                        if x.startswith("01_Formula_Sheets") and x.endswith("_A4.jpg")], 2,
                   "FORMULA SHEETS", "calculus · linear algebra · vector calculus · physics",
                   "03_formula_sheets.jpg")

        grid_sheet(zf, pick_each("05_Cornell_Lab_Syllabus", NOTES), 3,
                   "CORNELL · LAB · SYLLABUS", "note pages, lab reports and term planners",
                   "04_notes_labs.jpg")

        grid_sheet(zf, pick("06_Binder_Covers", 6), 3,
                   "BINDER COVERS", "one for every STEM subject, A4 and US Letter",
                   "05_binder_covers.jpg")


if __name__ == "__main__":
    main()
