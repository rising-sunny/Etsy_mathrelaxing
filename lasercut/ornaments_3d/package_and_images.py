"""Package the 3D ornament files (ZIP + 1:1 PDF + guide) and render listing images."""
import math
import os
import random
import sys
import zipfile

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.colors import HexColor, black, red
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import build_ornaments as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lasercut", "marble_mazes"))
from package_and_images import wood  # noqa: E402  (shared procedural wood texture)

DIST = os.path.join(HERE, "dist")
LIST = os.path.join(HERE, "listing")
FONTS = os.path.join(ROOT, "lulu_books", "assets", "fonts")
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
COPYRIGHT = "© MathRelaxing. For personal use only. Not for redistribution or resale."


def make_zip():
    path = os.path.join(DIST, "MathRelaxing_3D_Ornaments_SVG_DXF.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(B.OUT):
            for f in sorted(files):
                z.write(os.path.join(root, f), os.path.join(os.path.relpath(root, B.OUT), f))
    return path


def make_templates():
    path = os.path.join(DIST, "MathRelaxing_3D_Ornaments_PDF_Templates_1to1.pdf")
    W, H = LETTER
    c = canvas.Canvas(path, pagesize=LETTER)
    for tkey, t in B.THICKNESSES.items():
        for k, name in enumerate(B.DESIGNS):
            if k % 2 == 0:
                c.setFont("Helvetica", 8)
                c.drawString(0.5 * inch, 0.35 * inch, f"Material {t} mm · print at 100% · 50 mm calibration bar →")
                c.rect(3.6 * inch, 0.3 * inch, 50 * mm, 4 * mm)
            a, _ = B.build_piece(name, t, "A")
            b, _ = B.build_piece(name, t, "B")
            oy = H - (1.0 + 4.9 * (k % 2)) * inch - 50 * mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0.5 * inch, oy + 52 * mm, f"{B.LABEL[name]} · {t} mm · A (slot from top) / B (slot from bottom)")
            for j, g in enumerate((a, b)):
                ox = 0.5 * inch + (50 + j * 100) * mm
                c.setStrokeColor(red)
                c.setLineWidth(0.25)
                for r in B.rings_of(g):
                    p = c.beginPath()
                    p.moveTo(ox + r[0][0] * mm, oy + r[0][1] * mm)
                    for x, y in r[1:]:
                        p.lineTo(ox + x * mm, oy + y * mm)
                    p.close()
                    c.drawPath(p, stroke=1, fill=0)
            c.setStrokeColor(black)
            if k % 2 == 1 or k == len(B.DESIGNS) - 1:
                c.showPage()
    c.save()
    return path


def make_guide():
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(FONTS, "Cinzel-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Body", SANS))
    path = os.path.join(DIST, "MathRelaxing_3D_Ornaments_Guide.pdf")
    W, H = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(path, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 24)
    c.drawCentredString(W / 2, H - 0.75 * inch, "Mathematical 3D Ornaments")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(W / 2, H - 1.05 * inch, "8 slot-together designs · laser cut files · guide")
    y = H - 1.75 * inch
    blocks = [
        ("Choose your thickness", ["Folders 3mm / 1-8in / 4mm: the slot width matches that material exactly",
                                   "Measure your sheet with calipers and pick the closest folder",
                                   "Too tight? Scale the file to 101%. Too loose? Use the next folder down"]),
        ("Cut", ["Red hairline = cut. Every file holds piece A (left) and piece B (right)",
                 "Cut the small inside shapes before the outline (most software does this automatically)",
                 "Each ornament is about 80–92 mm tall; the PDF templates are 1:1 with a calibration bar"]),
        ("Assemble", ["Slide piece B (slot from the bottom) down onto piece A (slot from the top) at 90°",
                      "Push until the top and bottom edges line up. No glue needed in most woods",
                      "Thread ribbon or twine through the hole at the top of piece B"]),
        ("Ideas", ["Plywood, MDF, mirror or coloured acrylic, or 3 mm cardboard for a test",
                   "Engrave a name or year on the spine for personalised gifts",
                   "Paint the cut-out edges gold or white before assembling"]),
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
    c.drawString(M, y, "The designs")
    y -= 18
    c.setFillColor(black)
    c.setFont("Body", 10)
    notes = {"koch_snowflake": "the Koch curve, a fractal of infinite perimeter",
             "sierpinski_tree": "Sierpinski's triangle, holes within holes",
             "voronoi_bauble": "a Voronoi diagram: cells of nearest points",
             "golden_bauble": "seeds placed at the golden angle, 137.5°",
             "honeycomb_bauble": "the hexagonal tiling, nature's most efficient grid",
             "apollonian_bauble": "Apollonian gasket of mutually tangent circles",
             "pentagram_star": "a five-fold rose curve r = 1 + a·cos 5θ",
             "girih_star": "an eight-pointed girih star from Islamic geometry"}
    for name in B.DESIGNS:
        c.drawString(M + 12, y, f"{B.LABEL[name]} — {notes[name]}")
        y -= 14
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(W / 2, 0.5 * inch, COPYRIGHT)
    c.save()
    return path


# ── 3D render ────────────────────────────────────────────────────────────────
def piece_img(g, px_per_mm, seed, tint=1.0):
    minx, miny, maxx, maxy = -50, -52, 50, 52
    W, H = int((maxx - minx) * px_per_mm), int((maxy - miny) * px_per_mm)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    T = lambda r: [((x - minx) * px_per_mm, (maxy - y) * px_per_mm) for x, y in r]
    d.polygon(T(g.exterior.coords), fill=255)
    for r in g.interiors:
        d.polygon(T(r.coords), fill=0)
    tex = wood(W, H, (int(206 * tint), int(160 * tint), int(104 * tint)), seed, scale=0.35)
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(3)), m.filter(ImageFilter.MinFilter(3)))
    tex.paste((70, 40, 18), (0, 0), edge)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(tex, (0, 0), m)
    return out


def ornament_3d(name, size, theta=38, seed=1):
    t = 3.0
    a, _ = B.build_piece(name, t, "A")
    b, _ = B.build_piece(name, t, "B")
    ppm = size / 104
    A = piece_img(a, ppm, seed, 1.0)
    Bm = piece_img(b, ppm, seed + 5, 0.78)
    W, H = A.size
    cx = W // 2
    ca, sa = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    canvas_ = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def half(img, right, k, flip):
        part = img.crop((cx, 0, W, H)) if right else img.crop((0, 0, cx, H))
        if flip:
            part = part.transpose(Image.FLIP_LEFT_RIGHT)
        w = max(1, int(part.width * k))
        return part.resize((w, H), Image.LANCZOS)

    # back → front: A(-) , B(-) , A(+) , B(+)
    an = half(A, False, ca, False)
    canvas_.alpha_composite(an, (cx - an.width, 0))
    bn = half(Bm, False, sa, True)
    canvas_.alpha_composite(bn, (cx, 0))
    ap = half(A, True, ca, False)
    canvas_.alpha_composite(ap, (cx, 0))
    bp = half(Bm, True, sa, True)
    canvas_.alpha_composite(bp, (cx - bp.width, 0))
    return canvas_


def scene(S, seed):
    rng = random.Random(seed)
    yy = np.linspace(0, 1, S)[:, None]
    base = np.array([16, 34, 30]) * (1 - yy[..., None] * 0.4) + np.array([10, 14, 26]) * yy[..., None] * 0.4
    im = Image.fromarray(np.repeat(base, S, axis=1).astype(np.uint8))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(46):
        x, y, r = rng.uniform(0, S), rng.uniform(0, S * 0.9), rng.uniform(25, 90)
        col = rng.choice([(255, 196, 110), (255, 220, 160), (240, 170, 90), (255, 240, 210)])
        gd.ellipse([x - r, y - r, x + r, y + r], fill=col + (rng.randint(40, 95),))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    im = im.convert("RGBA")
    im.alpha_composite(glow)
    return im


def hang(im, orn, x, y, string_top=0):
    d = ImageDraw.Draw(im)
    d.line([(x, string_top), (x, y + orn.height * 0.06)], fill=(212, 175, 95, 255), width=4)
    sh = Image.new("RGBA", orn.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), (0, 0), orn.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(sh, (int(x - orn.width / 2 + 18), int(y + 22)))
    im.alpha_composite(orn, (int(x - orn.width / 2), int(y)))


def band(im, S, title, sub):
    d = ImageDraw.Draw(im)
    d.rectangle([0, S - 170, S, S], fill=(0, 0, 0, 255))
    logo = Image.open(os.path.join(ROOT, "mathrelaxing_logo.png")).convert("RGBA")
    logo.thumbnail((420, 130))
    im.alpha_composite(logo, ((S - logo.width) // 2, S - 170 + (170 - logo.height) // 2))
    f1 = ImageFont.truetype(os.path.join(FONTS, "Cinzel-SemiBold.ttf"), 80)
    f2 = ImageFont.truetype(SANS, 46)
    for txt, f, y, col in ((title, f1, 50, (248, 244, 235)), (sub, f2, 152, (222, 186, 110))):
        w = d.textlength(txt, font=f)
        d.text(((S - w) / 2, y), txt, font=f, fill=col)


def listing_images():
    os.makedirs(LIST, exist_ok=True)
    S = 2000
    # 1 hero: three hanging
    im = scene(S, 1)
    band(im, S, "3D CHRISTMAS ORNAMENTS", "8 mathematical designs · laser cut SVG · DXF · PDF")
    for name, x, y, sz, th in (("koch_snowflake", 460, 520, 720, 35), ("voronoi_bauble", 1020, 300, 860, 42),
                               ("sierpinski_tree", 1560, 620, 700, 30)):
        hang(im, ornament_3d(name, sz, th), x, y)
    im.convert("RGB").save(os.path.join(LIST, "01_hero.jpg"), quality=92)
    # 2 all eight
    im = scene(S, 2)
    band(im, S, "EIGHT DESIGNS", "fractals · tilings · circle packings · golden angle")
    f = ImageFont.truetype(SANS, 38)
    for k, name in enumerate(B.DESIGNS):
        x, y = 260 + (k % 4) * 493, 300 + (k // 4) * 760
        o = ornament_3d(name, 470, 36, seed=k)
        hang(im, o, x, y, string_top=y - 60)
        d = ImageDraw.Draw(im)
        w = d.textlength(B.LABEL[name], font=f)
        d.text((x - w / 2, y + o.height + 40), B.LABEL[name], font=f, fill=(222, 186, 110))
    im.convert("RGB").save(os.path.join(LIST, "02_all_eight.jpg"), quality=92)
    # 3 how it works: flat pieces + assembled
    im = scene(S, 3)
    band(im, S, "TWO PIECES, ONE SLOT", "slide B onto A at 90° · no glue needed")
    a, _ = B.build_piece("golden_bauble", 3.0, "A")
    b, _ = B.build_piece("golden_bauble", 3.0, "B")
    pa, pb = piece_img(a, 6.5, 4), piece_img(b, 6.5, 9, 0.9)
    im.alpha_composite(pa, (40, 330))
    im.alpha_composite(pb, (40 + pa.width - 60, 330))
    hang(im, ornament_3d("golden_bauble", 760, 40, 4), 1580, 520)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(SANS, 54)
    for t, x in (("A", 360), ("B", 360 + pa.width - 60)):
        d.text((x, 1060), t, font=f, fill=(248, 244, 235))
    d.text((1180, 1350), "→  assembled", font=f, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(LIST, "03_how.jpg"), quality=92)
    # 4 specs
    im = scene(S, 4)
    band(im, S, "READY FOR YOUR LASER", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["8 designs × 3 thicknesses: 3 mm · 1/8\" · 4 mm", "Slot sized exactly to your material",
             "About 80–92 mm tall, hanging hole included", "Red = cut · SVG + DXF in millimetres",
             "1:1 PDF templates with calibration bar", "Every piece verified as one solid part",
             "Guide: fit, assembly, finishing ideas", "Perfect for handmade gifts and gift tags"]
    f = ImageFont.truetype(SANS, 56)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(specs):
        d.text((220, 330 + i * 165), "■", font=f, fill=(222, 186, 110))
        d.text((310, 330 + i * 165), t, font=f, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(LIST, "04_specs.jpg"), quality=92)
    # 5 close-up
    im = scene(S, 5)
    band(im, S, "FRACTAL SNOWFLAKE", "the Koch curve, cut in wood")
    hang(im, ornament_3d("koch_snowflake", 1450, 40, 7), S // 2, 260)
    im.convert("RGB").save(os.path.join(LIST, "05_koch.jpg"), quality=92)


def main():
    os.makedirs(DIST, exist_ok=True)
    B.main()
    for f in (make_zip(), make_templates(), make_guide()):
        print(f"{os.path.getsize(f) // 1024:>6} KB  {os.path.basename(f)}")
    listing_images()
    print("listing ->", LIST)


if __name__ == "__main__":
    main()
