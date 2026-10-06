"""Etsy listing images (2000x2000) for the Tangram Puzzle Pack, from the Letter PDF pages
and the catalogue geometry."""
import os, sys, json, importlib.util
import fitz
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(REPO, "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
place, S = _ap.place, _ap.S
OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)
NAVY = (24, 36, 64); CREAM = (250, 246, 238); YEL = (240, 200, 70); SIL = (30, 40, 66)
PIECE = {"L1": (196, 64, 60), "L2": (232, 150, 52), "M": (240, 200, 70), "S1": (70, 150, 100),
         "S2": (60, 130, 190), "SQ": (120, 90, 170), "PA": (220, 100, 150)}
LV = {1: (70, 150, 100), 2: (60, 130, 190), 3: (196, 64, 60), 4: (196, 152, 64)}
CAT = json.load(open(os.path.join(HERE, "catalog.json"))); BY = {r["name"]: r for r in CAT}
DOC = fitz.open(os.path.join(HERE, "out", "Tangram_Puzzles_Letter.pdf"))


def pg(n):
    pix = DOC[n].get_pixmap(dpi=150)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def find(title):
    for i, p in enumerate(DOC):
        if title in p.get_text():
            return i
    raise KeyError(title)


def bg(dark=False):
    return Image.new("RGB", (S, S), NAVY if dark else CREAM)


def banner(d, t, sub=None, y=80, dark=False):
    f = G.font("cinzel", 92); d.text(((S - d.textlength(t, font=f)) / 2, y), t, font=f, fill=CREAM if dark else NAVY)
    if sub:
        s = G.font("semi", 48); d.text(((S - d.textlength(sub, font=s)) / 2, y + 125), sub, font=s, fill=YEL if dark else (110, 106, 100))


def pill(d, text, y, fill=(196, 64, 60), size=54):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 130), radius=65, fill=fill)
    d.text(((S - w) / 2, y + 32), text, font=f, fill=CREAM)


def draw(d, r, cx, cy, size, solved=False, lines=0, fill=SIL):
    s = size / max(r["w"], r["h"], 3.2); ox = cx - r["w"] * s / 2; oy = cy + r["h"] * s / 2
    tr = lambda pts: [(ox + x * s, oy - y * s) for x, y in pts]
    if solved:
        for n, pts in r["pieces"]:
            d.polygon(tr(pts), fill=PIECE[n], outline=(255, 255, 255), width=max(2, int(size / 90)))
        return
    for ring in r["outline"]:
        d.polygon(tr(ring), fill=fill)
    if lines:
        for n, pts in r["pieces"]:
            if lines == 1 or n in ("L1", "L2"):
                q = tr(pts); d.line(q + [q[0]], fill=(255, 255, 255), width=3)


def hero():
    c = bg(True); d = ImageDraw.Draw(c)
    place(c, pg(2), 760, (1110, 430), angle=-7)
    place(c, pg(find("Walking Cat")), 760, (130, 420), angle=7)
    place(c, pg(0), 860, (570, 260))
    pill(d, "50 TANGRAM PUZZLES  ·  PRINTABLE", 1790)
    return c


def gallery():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "50 Shapes to Build", "animals · objects · Christmas · the 13 convex shapes")
    names = ["Cat", "Fish", "Sleigh", "Christmas Stocking", "Teapot", "Rabbit", "Goose", "Seahorse",
             "Horse", "Kangaroo", "Heron", "Walking Cat", "Steamboat", "Number Two", "Goblet", "Dog", "Pine Tree", "Rocket",
             "House", "Sailboat"]
    cols, rows = 5, 4; cw = 360; ch = 395
    for k, n in enumerate(names):
        cx = 100 + cw / 2 + (k % cols) * cw; cy = 450 + (k // cols) * ch
        draw(d, BY[n], cx, cy, 270)
        f = G.font("semi", 32); d.text((cx - d.textlength(n, font=f) / 2, cy + 150), n, font=f, fill=(90, 86, 80))
    return c


def levels():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Four Levels", "from first-timers to tangram masters")
    cols = [(1, "House", "WARM-UP", "every line shown"), (2, "Cat", "EXPLORER", "large triangles shown"),
            (3, "Kangaroo", "MASTER", "silhouette only"), (4, "Convex Hexagon 1", "CONVEX", "the hardest 13")]
    for i, (lv, n, t, sub) in enumerate(cols):
        x0 = 70 + i * 470; d.rounded_rectangle((x0, 400, x0 + 430, 1500), radius=36, fill=(255, 255, 255))
        d.rounded_rectangle((x0, 400, x0 + 430, 520), radius=36, fill=LV[lv]); d.rectangle((x0, 480, x0 + 430, 520), fill=LV[lv])
        f = G.font("bold", 44); d.text((x0 + 215 - d.textlength(t, font=f) / 2, 432), t, font=f, fill=(255, 255, 255))
        draw(d, BY[n], x0 + 215, 900, 340, lines=lv if lv < 3 else 0)
        f = G.font("semi", 34); d.text((x0 + 215 - d.textlength(sub, font=f) / 2, 1380), sub, font=f, fill=(90, 86, 80))
    f = G.font("semi", 50); t = "12  +  13  +  12  +  13  =  50 puzzles"
    d.text(((S - d.textlength(t, font=f)) / 2, 1640), t, font=f, fill=NAVY)
    return c


def actual_size():
    c = bg(True); d = ImageDraw.Draw(c)
    banner(d, "Actual Size", "lay the pieces right on the page", dark=True)
    place(c, pg(2), 800, (140, 420), angle=-4)
    place(c, pg(find("Christmas Stocking")), 800, (1060, 420), angle=4)
    pill(d, "PRINT · CUT · PLAY · LAMINATE TO REUSE", 1780, fill=(60, 130, 190), size=50)
    return c


def solutions():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Every Solution Included", "each shape was built by computer from the 7 real pieces")
    pairs = ["Sleigh", "Seahorse", "Teapot", "Horse"]
    for i, n in enumerate(pairs):
        y = 470 + i * 360
        draw(d, BY[n], 560, y + 140, 300); draw(d, BY[n], 1440, y + 140, 300, solved=True)
        f = G.font("semi", 36); d.text((1000 - d.textlength(n, font=f) / 2, y + 120), n, font=f, fill=(90, 86, 80))
    f = G.font("bold", 40)
    for x, t in ((560, "PUZZLE"), (1440, "SOLUTION")):
        d.text((x - d.textlength(t, font=f) / 2, 380), t, font=f, fill=NAVY)
    return c


def convex():
    c = bg(True); d = ImageDraw.Draw(c)
    banner(d, "Only Thirteen", "the convex shapes a tangram can make (proved in 1942)", dark=True)
    recs = [r for r in CAT if r["level"] == 4]
    for k, r in enumerate(recs):
        row = k // 5 if k < 10 else 2; col = k % 5 if k < 10 else k - 10 + 1
        cx = 260 + col * 370; cy = 560 + row * 430
        draw(d, r, cx, cy, 300, solved=(k % 2 == 0), fill=CREAM)
    pill(d, "A REAL MATH THEOREM TO SOLVE BY HAND", 1790, fill=(196, 152, 64), size=50)
    return c


def included():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Included", "instant download · US Letter + A4")
    items = ["2 sets of colour cut-out pieces", "1 page of pieces to colour", "How-to-play guide",
             "50 actual-size silhouettes in 4 levels", "Intro to the 13 convex shapes", "Progress checklist",
             "Colour solutions for all 50", "The math inside: fractions, area, √2", "40+ pages, PDF"]
    f = G.font("semi", 54)
    for i, t in enumerate(items):
        y = 430 + i * 145; d.ellipse((330, y + 8, 380, y + 58), fill=LV[1 + i % 4]); d.text((420, y), t, font=f, fill=NAVY)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, gallery, levels, actual_size, solutions, convex, included), 1):
        fn().save(os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"), quality=90)
    print("ok", sorted(os.listdir(OUT)))
