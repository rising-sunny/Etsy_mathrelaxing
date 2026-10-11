"""Listing images + guide for the 24-day advent ornament calendar."""
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "ornaments_3d"))
sys.path.insert(0, HERE)
import build_advent as A  # noqa: E402  (patches build_ornaments.design with day1..day24)
import build_ornaments as B  # noqa: E402

spec = importlib.util.spec_from_file_location("orn_pkg", os.path.join(ROOT, "lasercut", "ornaments_3d", "package_and_images.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P.B.design = A.advent_design  # the renderer's own import of build_ornaments

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANSB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
OUT = os.path.join(HERE, "listing")


def guide():
    from reportlab.lib.colors import HexColor, black
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(ROOT, "lulu_books", "assets", "fonts", "Cinzel-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Body", SANS))
    path = os.path.join(A.DIST, "MathRelaxing_Advent_Ornaments_Guide.pdf")
    W, H = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(path, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 22)
    c.drawCentredString(W / 2, H - 0.75 * inch, "Mathematical Advent Ornaments")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(W / 2, H - 1.05 * inch, "24 numbered slot-together ornaments · one for every day of December")
    y = H - 1.75 * inch
    blocks = [
        ("How it works", ["Hang one ornament on the tree every day from December 1 to 24",
                          "Or tie them to a branch, garland or wreath as a countdown, numbers facing out",
                          "Each ornament: piece A (slot from top) + piece B (slot from bottom, day number engraved)"]),
        ("Files", ["Folders 3mm / 1-8in / 4mm: slots sized exactly to that material",
                   "3 sheets per thickness (fit a 480 × 280 mm bed) + single-day files",
                   "Red hairline = cut, black fill = engrave (day number). Engrave first, then cut",
                   "Ornaments are about 75 mm tall with a hanging hole"]),
        ("Ideas", ["Hide a small treat or note in a bag tied to each ornament",
                   "Paint the numbers gold, or cut in two woods and mix pieces A and B",
                   "Keep them: a math ornament set that grows every year"]),
    ]
    for head, lines in blocks:
        c.setFillColor(navy)
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y -= 18
        c.setFillColor(black)
        c.setFont("Body", 10.5)
        for ln in lines:
            c.drawString(M + 12, y, "• " + ln)
            y -= 15
        y -= 10
    c.setFillColor(navy)
    c.setFont("Cinzel", 13)
    c.drawString(M, y, "The 24 days")
    y -= 18
    c.setFont("Body", 10)
    c.setFillColor(black)
    for d, (label, _, _) in enumerate(A.DAYS, start=1):
        col, row = (d - 1) // 12, (d - 1) % 12
        c.drawString(M + 12 + col * 3.2 * inch, y - row * 14, f"{d:>2}. {label}")
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(W / 2, 0.5 * inch, "© MathRelaxing. For personal use only. Not for redistribution or resale.")
    c.save()
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    print(guide())
    S = 2000
    fnum = ImageFont.truetype(SANSB, 36)
    # 1 hero: 24 hanging, 6 × 4
    im = P.scene(S, 31)
    P.band(im, S, "ADVENT ORNAMENT CALENDAR", "24 numbered math ornaments · laser cut SVG · DXF")
    for d in range(1, 25):
        k = d - 1
        x, y = 200 + (k % 6) * 320, 250 + (k // 6) * 380
        o = P.ornament_3d(f"day{d}", 270, 36, seed=d)
        P.hang(im, o, x, y, string_top=y - 40)
        dr = ImageDraw.Draw(im)
        w = dr.textlength(str(d), font=fnum)
        dr.ellipse([x - 26, y + o.height + 6, x + 26, y + o.height + 58], fill=(201, 162, 75))
        dr.text((x - w / 2, y + o.height + 12), str(d), font=fnum, fill=(19, 25, 46))
    im.convert("RGB").save(os.path.join(OUT, "01_hero.jpg"), quality=92)
    # 2 close-up trio
    im = P.scene(S, 32)
    P.band(im, S, "ONE ORNAMENT EVERY DAY", "December 1 to 24 · a new mathematical shape each morning")
    for d, x, y, sz in ((1, 430, 520, 640), (24, 1000, 330, 860), (12, 1580, 560, 640)):
        P.hang(im, P.ornament_3d(f"day{d}", sz, 38, d), x, y)
    im.convert("RGB").save(os.path.join(OUT, "02_trio.jpg"), quality=92)
    # 3 flat pieces with engraved number
    im = P.scene(S, 33)
    P.band(im, S, "NUMBERED & SLOT-TOGETHER", "day number engraved on piece B · no glue")
    a, _, _ = A.day_piece(24, 3.0, "A")
    b, eng, _ = A.day_piece(24, 3.0, "B")
    pa, pb = P.piece_img(a, 6.2, 4), P.piece_img(b, 6.2, 9, 0.9)
    db = ImageDraw.Draw(pb)
    for g in getattr(eng, "geoms", [eng]):
        T = lambda r: [((x + 50) * 6.2, (52 - y) * 6.2) for x, y in r]
        db.polygon(T(g.exterior.coords), fill=(60, 32, 12, 255))
        for r in g.interiors:
            db.polygon(T(r.coords), fill=(190, 150, 98, 255))
    im.alpha_composite(pa, (20, 420))
    im.alpha_composite(pb, (20 + pa.width - 60, 420))
    d0 = ImageDraw.Draw(im)
    fl = ImageFont.truetype(SANS, 54)
    d0.text((300, 1120), "A", font=fl, fill=(248, 244, 235))
    d0.text((300 + pa.width - 60, 1120), "B", font=fl, fill=(248, 244, 235))
    P.hang(im, P.ornament_3d("day24", 560, 40, 4), 1700, 560)
    im.convert("RGB").save(os.path.join(OUT, "03_pieces.jpg"), quality=92)
    # 4 specs
    im = P.scene(S, 34)
    P.band(im, S, "READY FOR YOUR LASER", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["24 ornaments, each a different math shape", "3 thicknesses: 3 mm · 1/8\" · 4 mm",
             "3 cut sheets per thickness (480 × 280 mm)", "Single-day files included",
             "Red = cut · black = engraved day number", "About 75 mm tall, hanging hole included",
             "Every piece verified as one solid part", "Guide with countdown ideas"]
    f = ImageFont.truetype(SANS, 56)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(specs):
        d.text((200, 330 + i * 165), "■", font=f, fill=(222, 186, 110))
        d.text((290, 330 + i * 165), t, font=f, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(OUT, "04_specs.jpg"), quality=92)
    # 5 names grid (flat B pieces with numbers)
    im = P.scene(S, 35)
    P.band(im, S, "FRACTALS · TILINGS · ROSES · GOLDEN ANGLE", "Koch · Sierpinski · Voronoi · Apollonian · girih · honeycomb")
    f2 = ImageFont.truetype(SANS, 26)
    for dd in range(1, 25):
        k = dd - 1
        b, eng, _ = A.day_piece(dd, 3.0, "B")
        pb = P.piece_img(b, 2.6, dd, 0.95)
        db = ImageDraw.Draw(pb)
        for g in getattr(eng, "geoms", [eng]):
            T = lambda r: [((x + 50) * 2.6, (52 - y) * 2.6) for x, y in r]
            db.polygon(T(g.exterior.coords), fill=(60, 32, 12, 255))
            for r in g.interiors:
                db.polygon(T(r.coords), fill=(190, 150, 98, 255))
        x, y = 40 + (k % 6) * 325, 250 + (k // 6) * 375
        im.alpha_composite(pb, (x, y))
        dr = ImageDraw.Draw(im)
        lab = A.DAYS[k][0]
        w = dr.textlength(lab, font=f2)
        dr.text((x + pb.width / 2 - w / 2, y + pb.height - 8), lab, font=f2, fill=(222, 186, 110))
    im.convert("RGB").save(os.path.join(OUT, "05_all24.jpg"), quality=92)
    print("listing ->", OUT)


if __name__ == "__main__":
    main()
