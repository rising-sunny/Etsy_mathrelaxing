"""Guide PDF + listing images for the living hinge library."""
import importlib.util
import os

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import build_hinges as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
CINZEL = os.path.join(ROOT, "lulu_books", "assets", "fonts", "Cinzel-SemiBold.ttf")
LIST = os.path.join(HERE, "listing")


def _load(name, rel):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "lasercut", rel))  # the helper imports its own builder
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "lasercut", rel, "package_and_images.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_maze = _load("maze_pkg", "marble_mazes")
bg, band, wood = _maze.bg, _maze.band, _maze.wood


def guide():
    pdfmetrics.registerFont(TTFont("Cinzel", CINZEL))
    pdfmetrics.registerFont(TTFont("Body", SANS))
    path = os.path.join(B.DIST, "MathRelaxing_Living_Hinge_Guide.pdf")
    W, H = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(path, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 24)
    c.drawCentredString(W / 2, H - 0.75 * inch, "Living Hinge Library")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(W / 2, H - 1.05 * inch, "30 patterns · 10 families × 3 flex levels · 2 projects")
    y = H - 1.75 * inch
    blocks = [
        ("Folders", ["swatches/  120 × 50 mm test strips: cut one in your material before a project",
                     "tiles/     100 × 100 mm hinge fields: paste into your design and clip to the bend zone",
                     "projects/  cuff bracelet and a pencil cup (3 mm) ready to cut"]),
        ("Flex levels", ["firm: gentle curves, stiffest   ·   medium: everyday boxes   ·   soft: tight radii",
                         "Bends happen across the slits: orient slits parallel to the fold line",
                         "Serpentine is the softest; Cross bends both ways; Honeycomb is decorative flex"]),
        ("Material", ["Best in 3 mm birch plywood or MDF; 2 mm for very tight bends",
                      "Acrylic is brittle: use only the firm patterns and a large radius",
                      "Run the swatch first, then pick the level that bends to your radius"]),
        ("Laser tips", ["All slits are single red cut lines (no fill). Kerf ~0.1–0.2 mm",
                        "Every pattern keeps ≥ 0.9 mm between slits and never touches the strip edge",
                        "Cut hinge slits before the outline so the part does not move"]),
    ]
    for head, lines in blocks:
        c.setFillColor(navy)
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y -= 18
        c.setFillColor(black)
        c.setFont("Body", 10.2)
        for ln in lines:
            c.drawString(M + 12, y, "• " + ln)
            y -= 15
        y -= 10
    c.setFillColor(navy)
    c.setFont("Cinzel", 13)
    c.drawString(M, y, "Index")
    y -= 18
    c.setFillColor(black)
    c.setFont("Body", 9.5)
    k = 0
    for fam in B.FAMILIES:
        names = []
        for lv in B.LEVELS:
            k += 1
            names.append(f"{k:02d} {lv}")
        c.drawString(M + 12, y, f"{fam:<12}" + "     ".join(names))
        y -= 13
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(W / 2, 0.5 * inch, "© MathRelaxing. For personal use only. Not for redistribution or resale.")
    c.save()
    return path


def strip_img(outline, slits, ppm, seed, bounds=None):
    x0, y0, x1, y1 = bounds or outline.bounds
    Wp, Hp = int((x1 - x0) * ppm) + 8, int((y1 - y0) * ppm) + 8
    T = lambda cs: [((x - x0) * ppm + 4, (y1 - y) * ppm + 4) for x, y in cs]
    m = Image.new("L", (Wp, Hp), 0)
    ImageDraw.Draw(m).polygon(T(outline.exterior.coords), fill=255)
    for r in outline.interiors:
        ImageDraw.Draw(m).polygon(T(r.coords), fill=0)
    out = Image.new("RGBA", (Wp, Hp), (0, 0, 0, 0))
    out.paste(wood(Wp, Hp, (214, 172, 118), seed, scale=0.5), (0, 0), m)
    d = ImageDraw.Draw(out)
    for s in slits:
        for g in getattr(s, "geoms", [s]):
            d.line(T(g.coords), fill=(52, 28, 10, 255), width=max(2, int(ppm * 0.35)))
    return out


def main():
    os.makedirs(LIST, exist_ok=True)
    print(guide())
    S = 2000
    f = ImageFont.truetype(SANS, 34)
    # 1 hero: fan of strips
    im = bg(S, 21).convert("RGBA")
    band(im, S, "LIVING HINGE SVG LIBRARY", "30 flexible patterns + 2 projects · SVG · DXF")
    picks = [("lattice", "medium"), ("wave", "soft"), ("serpentine", "medium"), ("cross", "medium"),
             ("arcs", "soft"), ("diamond", "medium")]
    for k, (fam, lv) in enumerate(picks):
        o, sl, _, _ = B.swatch(fam, lv)
        st = strip_img(o, sl, 7.4, k)
        im.alpha_composite(st, (90 + (k % 2) * (st.width + 60), 290 + (k // 2) * (st.height + 95)))
    im.convert("RGB").save(os.path.join(LIST, "01_hero.jpg"), quality=92)
    # 2 & 3 all 30 swatches (15 per image)
    fams = list(B.FAMILIES)
    for part in range(2):
        im = bg(S, 22 + part).convert("RGBA")
        band(im, S, "10 FAMILIES × 3 FLEX LEVELS", f"patterns {part * 15 + 1}–{part * 15 + 15} · firm · medium · soft")
        for r, fam in enumerate(fams[part * 5:(part + 1) * 5]):
            for cidx, lv in enumerate(B.LEVELS):
                o, sl, _, _ = B.swatch(fam, lv)
                st = strip_img(o, sl, 5.0, r * 3 + cidx)
                x, y = 70 + cidx * 640, 280 + r * 300
                im.alpha_composite(st, (x, y))
                d = ImageDraw.Draw(im)
                n = fams.index(fam) * 3 + cidx + 1
                d.text((x + 4, y + st.height + 8), f"{n:02d}  {fam} · {lv}", font=f, fill=(222, 186, 110))
        im.convert("RGB").save(os.path.join(LIST, f"0{2 + part}_patterns_{part + 1}.jpg"), quality=92)
    # 4 projects
    im = bg(S, 25).convert("RGBA")
    band(im, S, "2 READY PROJECTS", "cuff bracelet · pencil cup with puzzle seam")
    co, csl = B.cuff()
    st = strip_img(co, csl, 9.5, 3)
    im.alpha_composite(st, ((S - st.width) // 2, 300))
    bd, bsl, base = B.pencil_cup()
    st2 = strip_img(bd, bsl, 6.4, 5)
    im.alpha_composite(st2, ((S - st2.width) // 2, 860))
    d = ImageDraw.Draw(im)
    f2 = ImageFont.truetype(SANS, 46)
    d.text((140, 760), "Cuff bracelet · 165 mm, soft wave hinge", font=f2, fill=(248, 244, 235))
    d.text((140, 1500), "Pencil cup · Ø70 × 90 mm, wraps a base disc, puzzle-joint seam", font=f2, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(LIST, "04_projects.jpg"), quality=92)
    # 5 specs
    im = bg(S, 26).convert("RGBA")
    band(im, S, "BEND PLYWOOD LIKE FABRIC", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["30 patterns: 10 families × firm / medium / soft", "120 × 50 mm test swatch for every pattern",
             "100 × 100 mm tiles to paste into your designs", "2 projects: cuff bracelet + pencil cup",
             "Single red cut lines · SVG + DXF in mm", "≥ 0.9 mm between slits, verified by code",
             "Guide: orientation, materials, flex levels", "Best in 2–3 mm plywood or MDF"]
    f3 = ImageFont.truetype(SANS, 56)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(specs):
        d.text((200, 330 + i * 165), "■", font=f3, fill=(222, 186, 110))
        d.text((290, 330 + i * 165), t, font=f3, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(LIST, "05_specs.jpg"), quality=92)
    print("listing ->", LIST)


if __name__ == "__main__":
    main()
