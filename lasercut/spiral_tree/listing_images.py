"""Guide + listing images (3D stacked render) for the golden spiral trees."""
import importlib.util
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.affinity import rotate

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import build_tree as T  # noqa: E402


def _load(name, rel):
    sys.path.insert(0, os.path.join(ROOT, "lasercut", rel))
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "lasercut", rel, "package_and_images.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ORN = _load("orn_pkg2", "ornaments_3d")
scene, band, wood = ORN.scene, ORN.band, ORN.wood
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def render_tree(kind, H_px, seed=1, gap_mm=10.0, tilt=0.34):
    """Stacked layers, each rotated so its tick faces the same way → golden spiral."""
    ppm = H_px / (T.N * gap_mm + 60)
    W_px = int(2 * (T.R_MAX + 8) * ppm)
    img = Image.new("RGBA", (W_px, H_px + 40), (0, 0, 0, 0))
    cx = W_px / 2
    base_y = H_px - 18 * ppm
    tex = wood(W_px, H_px + 40, (210, 166, 110), seed, scale=0.6).convert("RGBA")
    edge_col = (120, 80, 40, 255)
    d = ImageDraw.Draw(img)
    # base disc
    rb = 62 * ppm
    for off, col in ((10, edge_col), (0, None)):
        box_ = [cx - rb, base_y - rb * tilt + off, cx + rb, base_y + rb * tilt + off]
        if col:
            d.ellipse(box_, fill=col)
        else:
            m = Image.new("L", img.size, 0)
            ImageDraw.Draw(m).ellipse(box_, fill=255)
            img.paste(tex, (0, 0), m)
    # dowel
    top_y = base_y - T.N * gap_mm * ppm - 10 * ppm
    d.rectangle([cx - 3 * ppm, top_y, cx + 3 * ppm, base_y], fill=(150, 104, 58, 255))
    for k in range(T.N):
        piece, _, r = T.layer(kind, k, 6.0)
        g = rotate(piece, -k * T.GOLDEN, origin=(0, 0))
        y0 = base_y - (k + 1) * gap_mm * ppm
        pts = [(cx + x * ppm, y0 - y * ppm * tilt) for x, y in g.exterior.coords]
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.paste((90, 58, 28, 255), (0, int(3 * ppm)), m)  # thickness edge
        img.alpha_composite(sh)
        layer_tex = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer_tex.paste(tex, (0, 0), m)
        img.alpha_composite(layer_tex)
        for hole in g.interiors:
            ImageDraw.Draw(img).polygon([(cx + x * ppm, y0 - y * ppm * tilt) for x, y in hole.coords],
                                        fill=(70, 44, 20, 255))
    # topper (upright)
    star = T.O.star_curve(16, 5, 0.5)
    ty = top_y - 6 * ppm
    ImageDraw.Draw(img).polygon([(cx + x * ppm, ty - y * ppm) for x, y in star.exterior.coords], fill=(222, 182, 110, 255),
                                outline=(120, 80, 40, 255))
    return img.crop(img.getbbox())


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)


def guide():
    from reportlab.lib.colors import HexColor, black
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(ROOT, "lulu_books", "assets", "fonts", "Cinzel-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Body", SANS))
    path = os.path.join(T.DIST, "MathRelaxing_Golden_Spiral_Tree_Guide.pdf")
    W, H = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(path, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 22)
    c.drawCentredString(W / 2, H - 0.75 * inch, "Golden Spiral Christmas Trees")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(W / 2, H - 1.05 * inch, "3 designs · 16 layers on the golden angle · laser cut files · guide")
    y = H - 1.75 * inch
    blocks = [
        ("You need", ["Any 3 mm sheet (plywood, MDF, acrylic): no slots, so thickness does not matter",
                      "A wooden dowel, 6 mm or 8 mm (pick the matching folder), about 25 cm long",
                      "Wood glue for the base discs (optional elsewhere)"]),
        ("Build", ["1. Glue the 3 base discs together (the solid one at the bottom) and push in the dowel",
                   "2. Draw a straight pencil line down the dowel",
                   "3. Thread layer 1 (largest) with its engraved tick on the line, then 2–3 spacer rings",
                   "4. Repeat for layers 2…16 in order, every tick on the line, same number of spacers",
                   "5. Finish with the star topper. The points now spiral by 137.5°, the golden angle"]),
        ("Why it looks like nature", ["Each layer is turned 137.5° from the one below, the same angle sunflowers",
                                      "and pine cones use to pack seeds. No two points ever line up"]),
        ("Files", ["Star, Koch snowflake and honeycomb hexagon trees, for 6 mm and 8 mm dowels",
                   "Red hairline = cut, black fill = engrave (tick + layer number). Engrave first",
                   "Sheets fit a 480 × 280 mm bed. Tree is about 22 cm tall with the topper"]),
    ]
    for head, lines in blocks:
        c.setFillColor(navy)
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y -= 18
        c.setFillColor(black)
        c.setFont("Body", 10.5)
        for ln in lines:
            c.drawString(M + 12, y, ("• " if not ln[0].isdigit() else "") + ln)
            y -= 15
        y -= 10
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(W / 2, 0.5 * inch, "© MathRelaxing. For personal use only. Not for redistribution or resale.")
    c.save()
    return path


def main():
    os.makedirs(T.LIST, exist_ok=True)
    print(guide())
    S = 2000
    trees = {k: render_tree(k, 1500, i + 1) for i, k in enumerate(T.VARIANTS)}
    # 1 hero
    im = scene(S, 41)
    band(im, S, "GOLDEN SPIRAL CHRISTMAS TREE", "laser cut SVG · DXF · layers turn by the golden angle 137.5°")
    t = fit(trees["star"], 1300, 1500)
    im.alpha_composite(t, ((S - t.width) // 2, 1810 - t.height))
    im.convert("RGB").save(os.path.join(T.LIST, "01_hero.jpg"), quality=92)
    # 2 three designs
    im = scene(S, 42)
    band(im, S, "THREE DESIGNS", "golden star · Koch snowflake · honeycomb hexagon")
    f = ImageFont.truetype(SANS, 44)
    for i, (k, lab) in enumerate(T.VARIANTS.items()):
        t = fit(trees[k], 600, 1300)
        x = 60 + i * 640 + (600 - t.width) // 2
        im.alpha_composite(t, (x, 1700 - t.height))
        dr = ImageDraw.Draw(im)
        w = dr.textlength(lab, font=f)
        dr.text((60 + i * 640 + 300 - w / 2, 1730), lab, font=f, fill=(222, 186, 110))
    im.convert("RGB").save(os.path.join(T.LIST, "02_three.jpg"), quality=92)
    # 3 the golden angle trick (layer with tick, top view)
    im = scene(S, 43)
    band(im, S, "LINE UP THE TICKS", "each layer is engraved with its golden-angle mark and number")
    dr = ImageDraw.Draw(im)
    for i, k in enumerate((0, 1, 2)):
        piece, eng, r = T.layer("koch", k, 6.0)
        sc = 4.6
        ox, oy = 360 + i * 640, 800
        dr.polygon([(ox + x * sc, oy - y * sc) for x, y in piece.exterior.coords], fill=(214, 172, 116))
        for h in piece.interiors:
            dr.polygon([(ox + x * sc, oy - y * sc) for x, y in h.coords], fill=(20, 30, 28))
        for g in getattr(eng, "geoms", [eng]):
            dr.polygon([(ox + x * sc, oy - y * sc) for x, y in g.exterior.coords], fill=(50, 26, 8))
    dr.text((260, 1250), "layer 1: 0°          layer 2: 137.5°          layer 3: 275°",
            font=ImageFont.truetype(SANS, 52), fill=(248, 244, 235))
    dr.text((260, 1360), "Ticks on one line  →  points spiral like a sunflower",
            font=ImageFont.truetype(SANS, 52), fill=(222, 186, 110))
    im.convert("RGB").save(os.path.join(T.LIST, "03_ticks.jpg"), quality=92)
    # 4 specs
    im = scene(S, 44)
    band(im, S, "EASY BUILD, ANY THICKNESS", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["3 trees: golden star · Koch snowflake · hexagon", "16 layers from 150 mm to 28 mm + star topper",
             "No slots: works with any 3 mm sheet", "Versions for 6 mm and 8 mm dowels",
             "Engraved ticks: the spiral sets itself", "Sheets fit 480 × 280 mm · SVG + DXF",
             "About 22 cm tall with the topper", "Guide: build steps + the math behind it"]
    f3 = ImageFont.truetype(SANS, 56)
    dr = ImageDraw.Draw(im)
    for i, tx in enumerate(specs):
        dr.text((200, 330 + i * 165), "■", font=f3, fill=(222, 186, 110))
        dr.text((290, 330 + i * 165), tx, font=f3, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(T.LIST, "04_specs.jpg"), quality=92)
    # 5 koch close-up
    im = scene(S, 45)
    band(im, S, "KOCH SNOWFLAKE TREE", "sixteen fractal snowflakes on a golden spiral")
    t = fit(trees["koch"], 1300, 1500)
    im.alpha_composite(t, ((S - t.width) // 2, 1810 - t.height))
    im.convert("RGB").save(os.path.join(T.LIST, "05_koch.jpg"), quality=92)
    print("listing ->", T.LIST)


if __name__ == "__main__":
    main()
