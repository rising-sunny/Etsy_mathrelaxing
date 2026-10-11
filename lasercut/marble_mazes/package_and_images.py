"""Package the marble-maze files (ZIP + 1:1 PDF templates + assembly guide) and
render the Etsy listing images (wood mock-ups)."""
import math
import os
import random
import zipfile

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.colors import HexColor, black, red
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import build_marble_mazes as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DIST = os.path.join(HERE, "dist")
LIST = os.path.join(HERE, "listing")
FONTS = os.path.join(ROOT, "lulu_books", "assets", "fonts")
COPYRIGHT = "© MathRelaxing. For personal use only. Not for redistribution or resale."
LABEL = {"square_easy": "Square · Easy", "square_hard": "Square · Hard", "circle_easy": "Circle · Easy",
         "circle_hard": "Circle · Hard", "hex_easy": "Hexagon · Easy", "hex_hard": "Hexagon · Hard"}


def designs():
    return [B.build_design(n, g(), s, seed) for n, g, s, seed in B.DESIGNS]


# ── Files ────────────────────────────────────────────────────────────────────
def make_zip():
    path = os.path.join(DIST, "MathRelaxing_Marble_Mazes_SVG_DXF.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(B.OUT):
            for f in sorted(files):
                z.write(os.path.join(root, f), os.path.join(os.path.relpath(root, B.OUT), f))
    return path


def make_templates(ds):
    path = os.path.join(DIST, "MathRelaxing_Marble_Mazes_PDF_Templates_1to1.pdf")
    c = canvas.Canvas(path)
    for d in ds:
        minx, miny, maxx, maxy = d["outline"].bounds
        for layer in ("base", "maze", "lid"):
            w, h = (maxx - minx + 30) * mm, (maxy - miny + 40) * mm
            c.setPageSize((w, h))
            ox, oy = (15 - minx) * mm, (25 - miny) * mm
            cut, eng = B.layer_parts(d, layer)
            c.setStrokeColor(red)
            c.setLineWidth(0.25)
            for r in cut:
                p = c.beginPath()
                p.moveTo(ox + r[0][0] * mm, oy + r[0][1] * mm)
                for x, y in r[1:]:
                    p.lineTo(ox + x * mm, oy + y * mm)
                p.close()
                c.drawPath(p, stroke=1, fill=0)
            c.setFillColor(black)
            for e in eng:
                p = c.beginPath()
                for r in B.rings_of(e):
                    p.moveTo(ox + r[0][0] * mm, oy + r[0][1] * mm)
                    for x, y in r[1:]:
                        p.lineTo(ox + x * mm, oy + y * mm)
                    p.close()
                c.drawPath(p, stroke=0, fill=1, fillMode=0)
            c.setStrokeColor(black)
            c.rect(5 * mm, 5 * mm, 50 * mm, 10 * mm)  # calibration bar
            c.setFont("Helvetica", 7)
            c.setFillColor(black)
            c.drawString(58 * mm, 8 * mm, f"50 mm calibration bar · {LABEL[d['name']]} · {layer.upper()} "
                                          f"{'(cut 2×)' if layer == 'maze' else ''} · print at 100%")
            c.showPage()
    c.save()
    return path


def make_guide(ds):
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(FONTS, "Cinzel-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Body", "LiberationSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("BodyB", "LiberationSans-Bold.ttf"))
    path = os.path.join(DIST, "MathRelaxing_Marble_Mazes_Assembly_Guide.pdf")
    W, H = LETTER
    M = 0.75 * inch
    c = canvas.Canvas(path, pagesize=LETTER)
    navy, gold = HexColor("#13192e"), HexColor("#c9a24b")
    c.setFillColor(navy)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f8f4eb"))
    c.setFont("Cinzel", 24)
    c.drawCentredString(W / 2, H - 0.75 * inch, "Marble Maze Collection")
    c.setFillColor(gold)
    c.setFont("Body", 11)
    c.drawCentredString(W / 2, H - 1.05 * inch, "6 generative labyrinths · laser cut files · assembly guide")
    y = H - 1.75 * inch
    blocks = [
        ("What you need", ["3 mm plywood or MDF (base + 2 maze layers per design)",
                           "Optional: 2–3 mm clear acrylic for the lid",
                           "One 8 mm steel ball (bearing ball)",
                           "4 × M3 bolts, 12–16 mm, with nuts (or wood glue instead of bolts)"]),
        ("Files", ["Each design has 3 layers: BASE, MAZE, LID (SVG + DXF, millimetres)",
                   "Red hairline = cut  ·  black fill = engrave (start ring and finish star)",
                   "PDF templates are 1:1. Check the 50 mm calibration bar before cutting",
                   "Largest board is 279 mm: every design fits a 280 mm bed (rotate the hexagons if needed)"]),
        ("Assembly (bottom → top)", ["1. BASE: engrave first, then cut",
                                     "2. MAZE: cut twice from 3 mm and stack (6 mm walls for an 8 mm ball)",
                                     "3. Glue the maze layers to the base, aligning the bolt holes",
                                     "4. Drop the ball on the start ring, add the clear LID and bolt the corners"]),
        ("Other ball sizes", ["Channels are 10.5 mm, walls 4 mm. For a 6 mm ball scale the files to 80%",
                              "and use 2 × 3 mm maze layers (or one 4–5 mm layer)",
                              "Do not scale below 75%: walls get thinner than 3 mm"]),
        ("Tips", ["Run a small test cut to dial in power/speed for your material",
                  "Every maze is a perfect maze: exactly one route from start to finish, no loops",
                  "The finish is the cell farthest from the start, for the longest possible route"]),
    ]
    for head, lines in blocks:
        c.setFillColor(navy)
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y -= 18
        c.setFillColor(black)
        c.setFont("Body", 10.5)
        for ln in lines:
            c.drawString(M + 12, y, "• " + ln if not ln[:2].rstrip(".").isdigit() else ln)
            y -= 15
        y -= 10
    c.setFont("Cinzel", 13)
    c.setFillColor(navy)
    c.drawString(M, y, "The six designs")
    y -= 18
    c.setFont("Body", 10)
    c.setFillColor(black)
    for d in ds:
        minx, miny, maxx, maxy = d["outline"].bounds
        c.drawString(M + 12, y, f"{LABEL[d['name']]:<18}  {maxx - minx:.0f} × {maxy - miny:.0f} mm   ·   "
                                f"{d['edges']} cells   ·   solution path {d['steps']} cells")
        y -= 14
    c.setFont("Body", 8)
    c.setFillColor(HexColor("#6b6458"))
    c.drawCentredString(W / 2, 0.5 * inch, COPYRIGHT)
    c.save()
    return path


# ── Wood render ──────────────────────────────────────────────────────────────
def wood(w, h, base, seed, scale=1.0):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    warp = np.zeros((h, w))
    for k in range(4):
        f = rng.uniform(1, 4)
        warp += np.sin(2 * np.pi * (f * x + rng.uniform())) * rng.uniform(0.01, 0.04)
    rings = np.sin((y + warp) * 2 * np.pi * 38 * scale + np.sin(x * 9 + rng.uniform() * 6) * 0.8)
    fine = rng.normal(0, 1, (h, w // 4 + 1)).repeat(4, axis=1)[:, :w]
    v = 0.86 + 0.07 * rings + 0.025 * fine
    arr = np.clip(np.array(base)[None, None, :] * v[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def render_board(d, px, seed=1):
    minx, miny, maxx, maxy = d["outline"].bounds
    span = max(maxx - minx, maxy - miny)
    sc = px / (span + 10)
    W = H = px

    def T(coords):
        return [((x - minx) * sc + (W - (maxx - minx) * sc) / 2, (maxy - y) * sc + (H - (maxy - miny) * sc) / 2)
                for x, y in coords]

    def mask_of(geom):
        m = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(m)
        for i, r in enumerate(B.rings_of(geom)):
            dr.polygon(T(r), fill=255 if i == 0 or geom.geom_type == "MultiPolygon" else 0)
        if geom.geom_type == "Polygon":
            for r in geom.interiors:
                dr.polygon(T(list(r.coords)), fill=0)
        return m

    outline_m = mask_of(d["outline"])
    chan_m = mask_of(d["channel"])
    top = wood(W, H, (214, 170, 116), seed)
    floor = wood(W, H, (176, 128, 80), seed + 7, scale=0.8)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # board drop shadow
    sh = outline_m.filter(ImageFilter.GaussianBlur(px / 60))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (int(px / 80), int(px / 50)), sh)
    img = Image.alpha_composite(img, shadow)
    img.paste(floor.convert("RGBA"), (0, 0), outline_m)
    walls_m = ImageChops.subtract(outline_m, chan_m)
    # inner shadow cast by walls into the channel
    cast = walls_m.filter(ImageFilter.GaussianBlur(px / 160)).transform(
        (W, H), Image.AFFINE, (1, 0, -px / 260, 0, 1, -px / 200))
    cast = ImageChops.multiply(cast, chan_m).point(lambda v: int(v * 0.55))
    img.paste((40, 22, 8, 255), (0, 0), cast)
    # burned edge + wall tops
    edge = walls_m.filter(ImageFilter.MaxFilter(3))
    img.paste((92, 58, 30, 255), (0, 0), ImageChops.subtract(edge, walls_m))
    img.paste(top.convert("RGBA"), (0, 0), walls_m)
    dr = ImageDraw.Draw(img)
    for h in d["holes"]:
        cx, cy = T([h.centroid.coords[0]])[0]
        r = 4.2 * sc
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 155), outline=(90, 90, 95), width=max(1, int(sc / 2)))
    for e in d["engrave"]:
        for i, r in enumerate(B.rings_of(e)):
            dr.polygon(T(r), fill=(70, 40, 18) if i == 0 else None)
        if e.geom_type == "Polygon" and e.interiors:
            for r in e.interiors:
                dr.polygon(T(list(r.coords)), fill=(176, 128, 80))
    # steel ball at start
    bx, by = T([d["start"]])[0]
    br = 4.0 * sc
    ball = Image.new("RGBA", (int(br * 2 + 4), int(br * 2 + 4)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ball)
    for k in range(int(br), 0, -1):
        t = k / br
        g = int(70 + 170 * (1 - t) ** 1.4)
        off = (1 - t) * br * 0.35
        bd.ellipse([2 + br - k - off, 2 + br - k - off, 2 + br + k - off, 2 + br + k - off], fill=(g, g, g + 5, 255))
    img.alpha_composite(ball, (int(bx - br - 2), int(by - br - 2)))
    return img


def bg(S, seed=3):
    im = Image.new("RGB", (S, S), (32, 36, 44))
    noise = np.random.default_rng(seed).normal(0, 6, (S // 4, S // 4))
    n = Image.fromarray(np.clip(32 + noise, 0, 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
    return Image.merge("RGB", (n, n.point(lambda v: v + 4), n.point(lambda v: v + 12)))


def band(im, S, title, sub):
    d = ImageDraw.Draw(im)
    d.rectangle([0, S - 170, S, S], fill=(0, 0, 0))
    logo = Image.open(os.path.join(ROOT, "mathrelaxing_logo.png")).convert("RGBA")
    logo.thumbnail((420, 130))
    im.paste(logo, ((S - logo.width) // 2, S - 170 + (170 - logo.height) // 2), logo)
    f1 = ImageFont.truetype(os.path.join(FONTS, "Cinzel-SemiBold.ttf"), 84)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 46)
    for txt, f, y, col in ((title, f1, 50, (248, 244, 235)), (sub, f2, 158, (201, 162, 75))):
        w = d.textlength(txt, font=f)
        d.text(((S - w) / 2, y), txt, font=f, fill=col)


def listing_images(ds):
    os.makedirs(LIST, exist_ok=True)
    S = 2000
    by = {d["name"]: d for d in ds}
    # 1 hero
    im = bg(S)
    band(im, S, "MARBLE MAZE LASER FILES", "6 generative labyrinths · SVG · DXF · PDF")
    im.paste(render_board(by["circle_hard"], 1420, 2), (290, 250), render_board(by["circle_hard"], 1420, 2))
    im.save(os.path.join(LIST, "01_hero.jpg"), quality=92)
    # 2 all six
    im = bg(S, 4)
    band(im, S, "SIX DESIGNS, TWO LEVELS", "square · circle · hexagon  —  easy and hard")
    for k, d in enumerate(ds):
        b = render_board(d, 560, k + 3)
        im.paste(b, (70 + (k % 3) * 630, 280 + (k // 3) * 760), b)
        f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
        dr = ImageDraw.Draw(im)
        w = dr.textlength(LABEL[d["name"]], font=f)
        dr.text((70 + (k % 3) * 630 + 280 - w / 2, 850 + (k // 3) * 760), LABEL[d["name"]], font=f, fill=(201, 162, 75))
    im.save(os.path.join(LIST, "02_all_six.jpg"), quality=92)
    # 3 layers
    im = bg(S, 5)
    band(im, S, "3 LAYERS, EASY BUILD", "base + maze (cut 2×) + optional clear lid")
    d = by["square_easy"]
    b = render_board(d, 900, 9)
    base = render_board(dict(d, channel=d["channel"].buffer(-100)), 900, 9) if False else None
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 50)
    im.paste(b, (120, 420), b)
    steps = ["1  Engrave + cut the BASE", "2  Cut the MAZE twice (3 mm)", "3  Glue the layers",
             "4  Drop in an 8 mm steel ball", "5  Clear acrylic LID + 4 M3 bolts"]
    for i, t in enumerate(steps):
        dr.text((1080, 520 + i * 180), t, font=f, fill=(248, 244, 235))
    im.save(os.path.join(LIST, "03_layers.jpg"), quality=92)
    # 4 specs
    im = bg(S, 6)
    band(im, S, "MADE FOR YOUR LASER", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["Fits a 280 mm (11\") bed — every design", "3 mm plywood, MDF or acrylic",
             "10.5 mm channels · 4 mm walls · 8 mm ball", "Red = cut  ·  black = engrave",
             "SVG + DXF in millimetres", "1:1 PDF templates with calibration bar",
             "Assembly guide + scaling for 6 mm balls", "Every maze: one unique solution path"]
    f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 56)
    for i, t in enumerate(specs):
        dr = ImageDraw.Draw(im)
        dr.text((230, 330 + i * 165), "■", font=f, fill=(201, 162, 75))
        dr.text((320, 330 + i * 165), t, font=f, fill=(248, 244, 235))
    im.save(os.path.join(LIST, "04_specs.jpg"), quality=92)
    # 5 hex detail
    im = bg(S, 7)
    band(im, S, "MATHEMATICAL LABYRINTHS", "perfect mazes, generated with code")
    b = render_board(by["hex_hard"], 1500, 11)
    im.paste(b, (250, 230), b)
    im.save(os.path.join(LIST, "05_hex.jpg"), quality=92)


def main():
    os.makedirs(DIST, exist_ok=True)
    B.main()
    ds = designs()
    for f in (make_zip(), make_templates(ds), make_guide(ds)):
        print(f"{os.path.getsize(f) // 1024:>6} KB  {os.path.basename(f)}")
    listing_images(ds)
    print("listing images ->", LIST)


if __name__ == "__main__":
    main()
