"""
generate_science_fair_kit.py — printable Science Fair Project Display Kit
========================================================================
A clean STEM kit (navy + teal on white) to plan and dress a tri-fold science
fair board. Built with PIL at 300 dpi, assembled to a print-ready PDF via
img2pdf, with Etsy previews. Fonts: Cinzel (display) + Raleway (body/UI).

Deliverables (science_fair_kit/):
  prints/    one 300 dpi JPG per page
  Science_Fair_Project_Kit.pdf     combined print-ready PDF
  previews/  5 Etsy listing previews
  science_fair_kit_prints.zip

  python generate_science_fair_kit.py
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
OUT = BASE / "science_fair_kit"
FONTS = BASE / "lulu_books" / "assets" / "fonts"

DPI = 300
W, H = 2550, 3300          # US Letter @ 300 dpi
MX, MY = 190, 200          # page margins

# Palette — clean STEM: white paper, navy ink, teal accent
PAPER = "#FFFFFF"
TINT = "#F3F7FA"           # faint panel tint
INK = "#16324E"            # navy headings / text
INK_SOFT = "#38536E"
MUTED = "#8296A8"
ACCENT = "#0E7C86"         # deep teal
ACCENT_SOFT = "#4FA9B0"
LINE = "#C7D3DE"           # write-on rules
GRID = "#E4EBF1"


def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


# cached fonts
def F(kind, size):
    return font({"disp": "Cinzel-SemiBold.ttf", "head": "Cinzel.ttf",
                 "body": "Raleway.ttf", "ital": "Raleway-Italic.ttf"}[kind], size)


def page():
    im = Image.new("RGB", (W, H), hx(PAPER))
    d = ImageDraw.Draw(im)
    # thin editorial frame
    d.rounded_rectangle((70, 70, W - 70, H - 70), radius=28, outline=hx(GRID), width=3)
    return im, d


def center_text(d, cx, y, text, fnt, fill, spacing=0, anchor_mm=True):
    if spacing:
        widths = [d.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=fnt, fill=fill, anchor="lm" if anchor_mm else "la")
            x += w + spacing
    else:
        d.text((cx, y), text, font=fnt, fill=fill, anchor="mm" if anchor_mm else "la")


def footer(d, label):
    d.line((MX, H - 165, W - MX, H - 165), fill=hx(LINE), width=2)
    d.text((MX, H - 130), "SCIENCE FAIR PROJECT KIT", font=F("body", 30), fill=hx(MUTED), anchor="lm")
    d.text((W - MX, H - 130), label, font=F("body", 30), fill=hx(MUTED), anchor="rm")


def lines(d, x0, x1, y0, n, gap=96):
    for i in range(n):
        yy = y0 + i * gap
        d.line((x0, yy, x1, yy), fill=hx(LINE), width=2)
    return y0 + (n - 1) * gap


def section_title(d, title, sub=None, y=MY + 60):
    d.text((MX, y), title.upper(), font=F("disp", 92), fill=hx(INK), anchor="lm")
    d.line((MX, y + 78, MX + 430, y + 78), fill=hx(ACCENT), width=8)
    if sub:
        d.text((MX, y + 128), sub, font=F("ital", 40), fill=hx(ACCENT), anchor="lm")
    return y + (196 if sub else 150)


# ── pages ─────────────────────────────────────────────────────────────────────

def p_cover():
    im, d = page()
    cx = W // 2
    # top eyebrow
    center_text(d, cx, 520, "MATH · SCIENCE · DISCOVERY", F("body", 40), hx(ACCENT), spacing=18)
    d.line((cx - 250, 585, cx + 250, 585), fill=hx(ACCENT), width=4)
    # title
    center_text(d, cx, 850, "SCIENCE FAIR", F("disp", 210), hx(INK))
    center_text(d, cx, 1075, "PROJECT KIT", F("disp", 132), hx(ACCENT))
    center_text(d, cx, 1230, "Printable display-board headers, labels & planning pages",
                F("ital", 46), hx(INK_SOFT))

    # flask motif (simple, on-brand geometric)
    fx, fy = cx, 1780
    d.polygon([(fx - 60, fy - 230), (fx - 60, fy - 70), (fx - 200, fy + 150),
               (fx + 200, fy + 150), (fx + 60, fy - 70), (fx + 60, fy - 230)],
              outline=hx(INK), width=8)
    d.line((fx - 95, fy - 230, fx + 95, fy - 230), fill=hx(INK), width=8)
    d.polygon([(fx - 128, fy + 55), (fx + 128, fy + 55), (fx + 200, fy + 150),
               (fx - 200, fy + 150)], fill=hx(ACCENT_SOFT))
    for bx, by, r in [(fx - 40, fy + 100, 14), (fx + 55, fy + 115, 10), (fx + 10, fy + 70, 8)]:
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=hx(PAPER))

    # name plate
    py = 2180
    d.rounded_rectangle((MX + 120, py, W - MX - 120, py + 300), radius=22,
                        fill=hx(TINT), outline=hx(LINE), width=3)
    d.text((MX + 200, py + 95), "Name", font=F("body", 40), fill=hx(MUTED), anchor="lm")
    d.line((MX + 200, py + 150, W - MX - 200, py + 150), fill=hx(LINE), width=2)
    d.text((MX + 200, py + 220), "Grade / Class", font=F("body", 40), fill=hx(MUTED), anchor="lm")
    d.line((MX + 620, py + 220, W - MX - 200, py + 220), fill=hx(LINE), width=2)

    center_text(d, cx, 2760, "Instant download · Print at home or school · US Letter",
                F("body", 34), hx(MUTED))
    return im


def p_how():
    im, d = page()
    y = section_title(d, "How to use this kit", "Six steps from blank board to blue ribbon")
    steps = [
        ("Plan", "Fill in the planning pages — question, hypothesis, method, data, conclusion."),
        ("Print", "Print the header cards and labels on white or colored paper."),
        ("Cut", "Trim each header card along the rounded edge."),
        ("Arrange", "Lay out sections on your tri-fold board before gluing."),
        ("Mount", "Glue headers and your printed results in reading order."),
        ("Present", "Add your name plate and practice explaining each section."),
    ]
    yy = y + 70
    for i, (t, s) in enumerate(steps, 1):
        d.ellipse((MX, yy, MX + 96, yy + 96), fill=hx(ACCENT))
        d.text((MX + 48, yy + 48), str(i), font=F("disp", 54), fill=hx(PAPER), anchor="mm")
        d.text((MX + 150, yy + 12), t, font=F("disp", 52), fill=hx(INK), anchor="lm")
        d.text((MX + 150, yy + 72), s, font=F("body", 38), fill=hx(INK_SOFT), anchor="lm")
        yy += 220

    # included box
    by = yy + 20
    d.rounded_rectangle((MX, by, W - MX, by + 470), radius=22, fill=hx(TINT), outline=hx(LINE), width=3)
    d.text((MX + 70, by + 70), "What's included", font=F("disp", 54), fill=hx(INK), anchor="lm")
    inc = [
        "12 display-board header cards (Question → Bibliography)",
        "8 fill-in planning pages (method, variables, data table…)",
        "Project checklist + name plate",
        "Print-ready PDF, US Letter · 300 dpi",
    ]
    iy = by + 175
    for it in inc:
        d.ellipse((MX + 75, iy - 8, MX + 99, iy + 16), fill=hx(ACCENT))
        d.text((MX + 140, iy + 4), it, font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
        iy += 74
    footer(d, "How to use")
    return im


def header_card(d, x0, y0, x1, y1, label, note):
    d.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=hx(ACCENT))
    d.rounded_rectangle((x0 + 14, y0 + 14, x1 - 14, y1 - 14), radius=18, outline=hx(PAPER), width=4)
    cx = (x0 + x1) // 2
    center_text(d, cx, (y0 + y1) // 2 - 18, label.upper(), F("disp", 108), hx(PAPER))
    center_text(d, cx, (y0 + y1) // 2 + 78, note, F("body", 34), hx("#DCEEF0"))


def p_headers(pairs, page_label):
    im, d = page()
    section_title(d, "Board headers", "Cut out and mount along the top of each section")
    y0 = MY + 300
    card_h = 900
    gap = 120
    for i, (label, note) in enumerate(pairs):
        yy = y0 + i * (card_h + gap)
        header_card(d, MX, yy, W - MX, yy + card_h, label, note)
    footer(d, page_label)
    return im


def worksheet(title, sub, build):
    im, d = page()
    y = section_title(d, title, sub)
    build(d, y + 60)
    footer(d, "Planning page")
    return im


def ws_question(d, y):
    d.text((MX, y), "What are you trying to find out? Write it as one clear question.",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, y + 140, 5, gap=118)
    yy = y + 830
    d.text((MX, yy), "Why is this interesting or useful?", font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, yy + 140, 5, gap=118)
    yy += 830
    d.text((MX, yy), "Keywords to research", font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, yy + 140, 6, gap=118)


def ws_hypothesis(d, y):
    d.text((MX, y), "If … then … because …", font=F("ital", 46), fill=hx(ACCENT), anchor="lm")
    box(d, MX, y + 100, W - MX, y + 720, "My hypothesis")
    yy = y + 830
    d.text((MX, yy), "What do you predict will happen, and why?", font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, yy + 140, 11, gap=118)


def ws_variables(d, y):
    cols = [("Independent", "What I change"), ("Dependent", "What I measure"),
            ("Controlled", "What I keep the same")]
    bw = (W - 2 * MX - 2 * 60) // 3
    ch = 2440
    for i, (t, s) in enumerate(cols):
        x0 = MX + i * (bw + 60)
        d.rounded_rectangle((x0, y, x0 + bw, y + ch), radius=20, fill=hx(TINT), outline=hx(LINE), width=3)
        d.rounded_rectangle((x0, y, x0 + bw, y + 120), radius=20, fill=hx(ACCENT))
        d.rectangle((x0, y + 60, x0 + bw, y + 120), fill=hx(ACCENT))
        center_text(d, x0 + bw // 2, y + 62, t.upper(), F("disp", 46), hx(PAPER))
        d.text((x0 + bw // 2, y + 165), s, font=F("ital", 34), fill=hx(ACCENT), anchor="mm")
        k = 0
        while y + 300 + k * 118 < y + ch - 60:
            yy = y + 300 + k * 118
            d.line((x0 + 40, yy, x0 + bw - 40, yy), fill=hx(LINE), width=2)
            k += 1


def ws_materials(d, y):
    d.text((MX, y), "List everything you need. Check items off as you gather them.",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    yy = y + 170
    colw = (W - 2 * MX) // 2
    for c in range(2):
        for r in range(15):
            bx = MX + c * colw
            by = yy + r * 158
            d.rounded_rectangle((bx, by, bx + 54, by + 54), radius=8, outline=hx(ACCENT), width=4)
            d.line((bx + 90, by + 54, bx + colw - 80, by + 54), fill=hx(LINE), width=2)


def ws_procedure(d, y):
    d.text((MX, y), "Write each step in order. Anyone should be able to repeat it.",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    yy = y + 160
    for i in range(1, 11):
        d.ellipse((MX, yy, MX + 70, yy + 70), outline=hx(ACCENT), width=5)
        d.text((MX + 35, yy + 35), str(i), font=F("disp", 40), fill=hx(ACCENT), anchor="mm")
        d.line((MX + 110, yy + 70, W - MX, yy + 70), fill=hx(LINE), width=2)
        d.line((MX + 110, yy + 168, W - MX, yy + 168), fill=hx(LINE), width=2)
        yy += 248


def ws_data(d, y):
    d.text((MX, y), "Record your measurements. Repeat trials for reliable results.",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    yy = y + 160
    rows, colspec = 14, ["Trial", "Condition", "Measurement", "Notes"]
    tw = W - 2 * MX
    cw = [tw * 0.14, tw * 0.28, tw * 0.28, tw * 0.30]
    rh = 150
    # header
    x = MX
    d.rounded_rectangle((MX, yy, MX + tw, yy + rh), radius=14, fill=hx(ACCENT))
    for j, name in enumerate(colspec):
        d.text((x + cw[j] / 2, yy + rh / 2, ), name, font=F("disp", 40), fill=hx(PAPER), anchor="mm")
        x += cw[j]
    # grid
    for r in range(rows):
        ry = yy + rh + r * rh
        d.rectangle((MX, ry, MX + tw, ry + rh), outline=hx(LINE), width=2)
        x = MX
        for j in range(len(colspec)):
            d.line((x, ry, x, ry + rh), fill=hx(LINE), width=2)
            x += cw[j]


def ws_results(d, y):
    d.text((MX, y), "Graph your data. Label both axes and give the graph a title.",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    gx0, gy0, gx1, gy1 = MX, y + 160, W - MX, H - 320
    d.rectangle((gx0, gy0, gx1, gy1), outline=hx(INK), width=4)
    step = 90
    xx = gx0 + step
    while xx < gx1:
        d.line((xx, gy0, xx, gy1), fill=hx(GRID), width=2); xx += step
    yy = gy0 + step
    while yy < gy1:
        d.line((gx0, yy, gx1, yy), fill=hx(GRID), width=2); yy += step
    d.text(((gx0 + gx1) // 2, gy1 + 60), "x-axis", font=F("body", 36), fill=hx(MUTED), anchor="mm")


def box(d, x0, y0, x1, y1, label):
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=hx(TINT), outline=hx(LINE), width=3)
    d.text((x0 + 40, y0 + 45), label, font=F("body", 34), fill=hx(MUTED), anchor="lm")
    for i in range(1, 4):
        yy = y0 + 45 + i * ((y1 - y0 - 45) / 4)
        d.line((x0 + 40, yy, x1 - 40, yy), fill=hx(LINE), width=2)


def ws_conclusion(d, y):
    d.text((MX, y), "Was your hypothesis supported? What did you learn?",
           font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, y + 140, 8, gap=118)
    yy = y + 1230
    d.text((MX, yy), "What would you do differently or try next?", font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    lines(d, MX, W - MX, yy + 140, 8, gap=118)


def ws_checklist(d, y):
    d.text((MX, y), "Tick each piece off before the fair.", font=F("body", 40), fill=hx(INK_SOFT), anchor="lm")
    items = [
        "Chose a testable question", "Wrote a clear hypothesis",
        "Listed variables (independent / dependent / controlled)",
        "Gathered all materials", "Wrote a repeatable procedure",
        "Ran trials and recorded data", "Made a graph of results",
        "Wrote the conclusion", "Cited sources / bibliography",
        "Printed and mounted all headers", "Added name & class plate",
        "Practiced my presentation",
    ]
    yy = y + 150
    for it in items:
        d.rounded_rectangle((MX, yy, MX + 58, yy + 58), radius=10, outline=hx(ACCENT), width=5)
        d.text((MX + 100, yy + 29), it, font=F("body", 44), fill=hx(INK), anchor="lm")
        yy += 118


def build_pages():
    pages = [
        p_cover(),
        p_how(),
        p_headers([("Question", "The problem I investigated"),
                   ("Hypothesis", "My prediction")], "Headers 1/6"),
        p_headers([("Materials", "What I used"),
                   ("Procedure", "How I did it")], "Headers 2/6"),
        p_headers([("Variables", "What I changed & measured"),
                   ("Data", "My measurements")], "Headers 3/6"),
        p_headers([("Results", "What the data show"),
                   ("Analysis", "What it means")], "Headers 4/6"),
        p_headers([("Conclusion", "What I found out"),
                   ("Abstract", "Project summary")], "Headers 5/6"),
        p_headers([("Bibliography", "My sources"),
                   ("Acknowledgments", "Who helped me")], "Headers 6/6"),
        worksheet("Research Question", "Start here", ws_question),
        worksheet("Hypothesis", "Your best prediction", ws_hypothesis),
        worksheet("Variables", "Keep it a fair test", ws_variables),
        worksheet("Materials", "Everything you need", ws_materials),
        worksheet("Procedure", "Step by step", ws_procedure),
        worksheet("Data Table", "Record your trials", ws_data),
        worksheet("Results", "Graph your data", ws_results),
        worksheet("Conclusion", "What you learned", ws_conclusion),
        worksheet("Project Checklist", "Ready for the fair?", ws_checklist),
    ]
    return pages


def save_prints(pages):
    pdir = OUT / "prints"
    pdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, im in enumerate(pages, 1):
        p = pdir / f"science_fair_kit_{i:02d}.jpg"
        im.convert("RGB").save(p, "JPEG", quality=92, dpi=(DPI, DPI))
        paths.append(p)
    print(f"  {len(paths)} page JPGs")
    return paths


def build_pdf(jpg_paths):
    pdf = OUT / "Science_Fair_Project_Kit.pdf"
    layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in jpg_paths], layout_fun=layout))
    print(f"  PDF {pdf.name} ({pdf.stat().st_size // 1024} KB)")
    return pdf


def make_previews(pages):
    prev = OUT / "previews"
    prev.mkdir(parents=True, exist_ok=True)
    S = 2000
    bg, navy, teal, muted = (243, 247, 250), hx(INK), hx(ACCENT), hx(MUTED)
    paths = []

    def pfont(sz, disp=False):
        return font("Cinzel-SemiBold.ttf" if disp else "Raleway.ttf", sz)

    def mock(page_img, title, subtitle, fname, shadow=True):
        canvas = Image.new("RGB", (S, S), bg)
        d = ImageDraw.Draw(canvas)
        d.text((S // 2, 78), title, font=pfont(46, True), fill=teal, anchor="mt")
        d.text((S // 2, 150), subtitle, font=pfont(30), fill=muted, anchor="mt")
        pg = page_img.copy()
        scale = 1520 / pg.height
        pg = pg.resize((int(pg.width * scale), 1520), Image.Resampling.LANCZOS)
        x, y = (S - pg.width) // 2, 230
        if shadow:
            sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rectangle([x + 14, y + 18, x + pg.width + 14, y + pg.height + 18], fill=(0, 0, 0, 80))
            sh = sh.filter(ImageFilter.GaussianBlur(20))
            canvas = Image.alpha_composite(canvas.convert("RGBA"), sh).convert("RGB")
        canvas.paste(pg, (x, y))
        ImageDraw.Draw(canvas).text((S // 2, S - 60), "Instant download · US Letter · 300 dpi",
                                    font=pfont(28), fill=muted, anchor="mt")
        p = prev / fname
        canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
        paths.append(p)

    # 1 hero (cover), 2 headers, 3 a worksheet
    mock(pages[0], "SCIENCE FAIR PROJECT KIT", "Printable headers, labels & planning pages",
         "science_fair_kit_preview_1_hero.jpg")
    mock(pages[2], "DISPLAY-BOARD HEADERS", "Cut out & mount — 12 sections included",
         "science_fair_kit_preview_2_headers.jpg")
    mock(pages[12], "PLANNING PAGES", "Question · hypothesis · method · data · results",
         "science_fair_kit_preview_3_worksheet.jpg")

    # 4 what's included card (teal)
    canvas = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, 130), "What's included", font=pfont(52, True), fill=(255, 255, 255), anchor="mt")
    items = ["12 display-board header cards", "8 fill-in planning pages",
             "Project checklist + name plate", "Print-ready PDF · US Letter · 300 dpi",
             "Instant digital download"]
    y = 330
    for it in items:
        d.rounded_rectangle([190, y, S - 190, y + 160], radius=14, outline=teal, width=3)
        d.text((270, y + 80), it, font=pfont(30), fill=(233, 242, 245), anchor="lm")
        y += 200
    p = prev / "science_fair_kit_preview_4_included.jpg"
    canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 5 grid of thumbnails
    canvas = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(canvas)
    d.text((S // 2, 90), "17-page printable kit", font=pfont(44, True), fill=navy, anchor="mt")
    thumbs = [pages[0], pages[2], pages[8], pages[10], pages[13], pages[16]]
    tw = 560
    x0, y0, gap = (S - 3 * tw - 2 * 60) // 2, 250, 60
    for i, tp in enumerate(thumbs):
        gx = x0 + (i % 3) * (tw + gap)
        gy = y0 + (i // 3) * (int(tw * 11 / 8.5) + gap)
        th = tp.resize((tw, int(tw * 11 / 8.5)), Image.Resampling.LANCZOS)
        canvas.paste(th, (gx, gy))
        d.rectangle((gx, gy, gx + tw, gy + int(tw * 11 / 8.5)), outline=hx(LINE), width=3)
    p = prev / "science_fair_kit_preview_5_pages.jpg"
    canvas.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)
    print(f"  {len(paths)} previews")
    return paths


def build_zip(pdf, jpgs):
    z = OUT / "science_fair_kit_prints.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf, pdf.name)
        zf.writestr("READ_ME.txt",
                    "Science Fair Project Kit\n\n"
                    "INCLUDED\n  Science_Fair_Project_Kit.pdf — 17 pages, US Letter, 300 dpi\n\n"
                    "PRINTING\n  Print on white or light card. Headers look great on colored paper.\n"
                    "  Trim header cards along the rounded edge and mount on your tri-fold board.\n\n"
                    "Personal / single-classroom use. Not for redistribution or resale.\n")
    print(f"  ZIP {z.name} ({z.stat().st_size // 1024} KB)")
    return z


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("=== Science Fair Project Kit ===")
    pages = build_pages()
    jpgs = save_prints(pages)
    pdf = build_pdf(jpgs)
    make_previews(pages)
    build_zip(pdf, jpgs)
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
