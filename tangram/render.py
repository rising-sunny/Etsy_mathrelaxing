"""
Vector PDF (PyMuPDF) for "Tangram Puzzles": printable pieces, 45 actual-size silhouettes in
four levels, a progress tracker, solutions and a math page. US Letter + A4.
Reads catalog.json (run catalog.py first).

  python render.py   -> out/Tangram_Puzzles_Letter.pdf, out/Tangram_Puzzles_A4.pdf
"""
import os, json, math
import fitz
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
AF = os.path.join(REPO, "lulu_books", "assets", "fonts")
FD = os.path.join(OUT, "fonts"); os.makedirs(FD, exist_ok=True)
U = 2.5 / 2.54 * 72          # one unit (small-triangle leg) = 2.5 cm, so the square side is 7.07 cm


def c(rgb):
    return tuple(v / 255 for v in rgb)


NAVY = c((24, 36, 64)); INK = c((36, 36, 40)); SUB = c((110, 106, 100)); CREAM = c((250, 246, 238))
LINE = c((205, 198, 184)); WHITE = (1, 1, 1); SIL = c((30, 40, 66))
PIECE = {"L1": (196, 64, 60), "L2": (232, 150, 52), "M": (240, 200, 70), "S1": (70, 150, 100),
         "S2": (60, 130, 190), "SQ": (120, 90, 170), "PA": (220, 100, 150)}
PIECE = {k: c(v) for k, v in PIECE.items()}
LEVELS = {1: ("Level 1", "Warm-Up", c((70, 150, 100)), "The lines show where every piece goes. Just match the shapes."),
          2: ("Level 2", "Explorer", c((60, 130, 190)), "Dashed lines show the two large triangles. The rest is up to you."),
          3: ("Level 3", "Master", c((196, 64, 60)), "Silhouette only. Use all seven pieces, no overlaps."),
          4: ("Level 4", "The 13 Convex Shapes", c((196, 152, 64)), "Silhouette only. These are the hardest of all.")}


def static_fonts():
    out = {}
    for name, w in (("body", 500), ("bold", 700), ("semi", 600)):
        p = os.path.join(FD, f"Raleway-{name}.ttf")
        if not os.path.exists(p):
            f = TTFont(os.path.join(AF, "Raleway.ttf"))
            instancer.instantiateVariableFont(f, {"wght": w}, inplace=True)
            f.save(p)
        out[name] = p
    out["title"] = os.path.join(AF, "Cinzel-SemiBold.ttf")
    return out


FONTS = static_fonts()
FOBJ = {k: fitz.Font(fontfile=v) for k, v in FONTS.items()}


class Book:
    def __init__(self, W, H, cat):
        self.doc = fitz.open(); self.W, self.H = W, H; self.cat = cat
        self.m = 0.07 * W; self.pageno = 0

    def page(self, band=None, label=None, number=True):
        p = self.doc.new_page(width=self.W, height=self.H)
        for k, v in FONTS.items():
            p.insert_font(fontname=k, fontfile=v)
        self.pageno += 1
        if band:
            p.draw_rect(fitz.Rect(0, 0, self.W, 7), color=None, fill=band)
            if label:
                self.text(p, self.m, 32, label.upper(), "bold", 8.5, band)
        if number:
            self.ctext(p, self.W / 2, self.H - 22, str(self.pageno), "body", 9, SUB)
        return p

    def text(self, p, x, y, s, f, size, col=INK):
        p.insert_text((x, y), s, fontname=f, fontsize=size, color=col)

    def tlen(self, s, f, size):
        return FOBJ[f].text_length(s, fontsize=size)

    def ctext(self, p, cx, y, s, f, size, col=INK):
        self.text(p, cx - self.tlen(s, f, size) / 2, y, s, f, size, col)

    def rtext(self, p, x, y, s, f, size, col=INK):
        self.text(p, x - self.tlen(s, f, size), y, s, f, size, col)

    def wrap(self, s, f, size, width):
        out = []
        for para in s.split("\n"):
            line = ""
            for w in para.split(" "):
                t = (line + " " + w).strip()
                if self.tlen(t, f, size) > width and line:
                    out.append(line); line = w
                else:
                    line = t
            out.append(line)
        return out

    def para(self, p, x, y, s, f, size, width, col=INK, lead=1.45):
        for ln in self.wrap(s, f, size, width):
            if ln:
                self.text(p, x, y, ln, f, size, col)
            y += size * lead
        return y

    def save(self, path):
        self.doc.save(path, deflate=True, garbage=3)


# ---------------------------------------------------------------- geometry helpers
def poly(p, pts, fill=None, stroke=None, width=1.0, dashes=None, join=1):
    sh = p.new_shape(); sh.draw_polyline([fitz.Point(*q) for q in pts] + [fitz.Point(*pts[0])])
    sh.finish(fill=fill, color=stroke, width=width, dashes=dashes, lineJoin=join, closePath=True); sh.commit()


def place(pts, ox, oy, s):
    """unit coordinates (y up) -> page points, origin at (ox, oy) = bottom-left of the figure."""
    return [(ox + x * s, oy - y * s) for x, y in pts]


def draw_silhouette(p, rec, ox, oy, s, level, bg=WHITE):
    for ring in rec["outline"]:
        poly(p, place(ring, ox, oy, s), fill=SIL, stroke=SIL, width=0.6)
    for ring in rec.get("holes", []):
        poly(p, place(ring, ox, oy, s), fill=bg, stroke=None)
    if level == 1:
        for n, pts in rec["pieces"]:
            poly(p, place(pts, ox, oy, s), stroke=WHITE, width=1.3)
    elif level == 2:
        for n, pts in rec["pieces"]:
            if n in ("L1", "L2"):
                poly(p, place(pts, ox, oy, s), stroke=WHITE, width=1.2, dashes="[5 4] 0")


def draw_solution(p, rec, ox, oy, s, lw=0.7):
    for n, pts in rec["pieces"]:
        poly(p, place(pts, ox, oy, s), fill=PIECE[n], stroke=WHITE, width=lw)


def square_set():
    """The seven pieces in the classic 2*sqrt(2) square (from the convex 'square' solution), axis-aligned."""
    for r in json.load(open(os.path.join(HERE, "catalog.json"))):
        if r["level"] == 4:
            u = unary_union([Polygon(q) for _, q in r["pieces"]])
            if len(u.simplify(1e-6).exterior.coords) == 5 and abs(u.length - 8 * math.sqrt(2)) < 1e-6:
                pcs = [(n, affinity.rotate(Polygon(q), 45, origin=(0, 0))) for n, q in r["pieces"]]
                uu = unary_union([g for _, g in pcs]); mx, my = uu.bounds[:2]
                return [(n, affinity.translate(g, -mx, -my)) for n, g in pcs]
    raise RuntimeError("square not found")


# ---------------------------------------------------------------- pages
def cover(B):
    p = B.page(number=False); W, H = B.W, B.H
    p.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=CREAM)
    p.draw_rect(fitz.Rect(0, 0, W, H * 0.30), color=None, fill=NAVY)
    B.ctext(p, W / 2, H * 0.115, "TANGRAM", "title", 64, WHITE)
    B.ctext(p, W / 2, H * 0.175, "PUZZLE PACK", "title", 26, c((240, 200, 70)))
    B.ctext(p, W / 2, H * 0.235, "45 actual-size silhouettes  ·  printable pieces  ·  all solutions", "semi", 12.5, WHITE)
    cat = {r["name"]: r for r in B.cat}
    hero = cat["Cat"]; s = min(0.36 * H / hero["h"], 0.46 * W / hero["w"])
    ox = W * 0.29 - hero["w"] * s / 2; oy = H * 0.81
    draw_solution(p, hero, ox, oy, s, lw=2)
    sil = cat["Fish"]; s2 = 0.16 * H / sil["h"]
    draw_silhouette(p, sil, W * 0.60, H * 0.56, s2, 3)
    sil2 = cat["Sleigh"]; s3 = 0.10 * H / sil2["h"]
    draw_silhouette(p, sil2, W * 0.58, H * 0.79, s3, 3)
    p.draw_rect(fitz.Rect(0, H * 0.86, W, H), color=None, fill=NAVY)
    B.ctext(p, W / 2, H * 0.905, "7 PIECES  ·  4 LEVELS  ·  AGES 5 TO 105", "bold", 13, WHITE)
    B.ctext(p, W / 2, H * 0.945, "MathRelaxing", "title", 15, c((240, 200, 70)))


def how_to(B):
    p = B.page(NAVY, "How to play")
    y = 80; B.text(p, B.m, y, "How to Play", "title", 26, NAVY); y += 32
    rules = [("Use all seven pieces.", "Every silhouette in this pack is made from the complete set: 2 large triangles, "
              "1 medium triangle, 2 small triangles, 1 square and 1 parallelogram."),
             ("No overlaps.", "Pieces lie flat and touch only along their edges or corners."),
             ("Turn and flip freely.", "You may rotate any piece and flip it over. The parallelogram is the only piece "
              "that changes shape when flipped, so try both sides!"),
             ("Build it on top.", "Every silhouette is printed at the same size as the pieces on pages 3 and 4, so you "
              "can lay the pieces directly on the page and cover the shape exactly.")]
    for t, d in rules:
        B.text(p, B.m, y, t, "bold", 12.5, NAVY); y += 17
        y = B.para(p, B.m, y, d, "body", 11, B.W - 2 * B.m) + 8
    y += 6; B.text(p, B.m, y, "Four levels", "title", 18, NAVY); y += 24
    for lv, (a, b, col, d) in LEVELS.items():
        p.draw_rect(fitz.Rect(B.m, y - 11, B.m + 14, y + 3), color=None, fill=col)
        B.text(p, B.m + 22, y, f"{a}: {b}", "bold", 11.5, col)
        y = B.para(p, B.m + 22, y + 16, d, "body", 10.5, B.W - 2 * B.m - 22) + 6
    y += 6; B.text(p, B.m, y, "Printing tips", "title", 18, NAVY); y += 22
    y = B.para(p, B.m, y, "Print at 100% / Actual size (not 'fit to page') so the pieces match the silhouettes. "
               "Use cardstock for the pieces, or glue the page onto a cereal box before cutting. Laminate the "
               "puzzle pages and they can be played again and again. A checklist on page "
               f"{B.tracker_page} lets you tick off every shape you solve.", "body", 11, B.W - 2 * B.m)


def pieces_page(B, color):
    p = B.page(NAVY, "Your tangram pieces")
    B.text(p, B.m, 70, "Cut-Out Pieces" + ("" if color else "  (to colour)"), "title", 22, NAVY)
    B.text(p, B.m, 90, "Two complete sets. Print at 100%, cut along the outer lines." if color else
           "Print on coloured cardstock, or colour each piece yourself, then cut out.", "body", 10.5, SUB)
    pcs = square_set(); S = 2 * math.sqrt(2); cxu = cyu = S / 2; gap = 0.16
    for k in range(2):
        oy = 120 + (k + 1) * (B.H - 170) / 2 - 18; ox = B.W / 2 - (S * (1 + gap * 2)) * U / 2 + gap * S * U
        for n, g in pcs:
            cx, cy = g.centroid.x, g.centroid.y
            gg = affinity.translate(g, (cx - cxu) * gap * 1.5, (cy - cyu) * gap * 1.5)
            pts = place(list(gg.exterior.coords)[:-1], ox, oy, U)
            poly(p, pts, fill=PIECE[n] if color else WHITE, stroke=INK, width=0.9)
            ctr = gg.centroid; px, py = ox + ctr.x * U, oy - ctr.y * U
            lab = {"L1": "large", "L2": "large", "M": "medium", "S1": "small", "S2": "small", "SQ": "square", "PA": "parallelogram"}[n]
            fs = 7 if n != "PA" else 5.5
            B.ctext(p, px, py + 2.5, lab, "semi", fs, WHITE if color else SUB)


def puzzle_pages(B, recs, start_no):
    """Lay out puzzles one or two per page, at actual size."""
    nums = {}; i = 0; no = start_no
    avail = B.H - 150
    while i < len(recs):
        group = [recs[i]]
        if i + 1 < len(recs) and (recs[i]["h"] + recs[i + 1]["h"]) * U + 110 <= avail:
            group.append(recs[i + 1])
        lv = group[0]["level"]; a, b, col, hint = LEVELS[lv]
        p = B.page(col, f"{a} · {b}")
        B.rtext(p, B.W - B.m, 32, hint, "body", 8.5, SUB)
        slot = avail / len(group)
        for k, r in enumerate(group):
            top = 60 + k * slot
            B.text(p, B.m, top + 18, f"{no}", "title", 20, col)
            B.text(p, B.m + B.tlen(str(no), "title", 20) + 10, top + 17, r["name"] if lv < 4 else r["name"].replace("Convex ", ""), "bold", 13, INK)
            p.draw_rect(fitz.Rect(B.W - B.m - 12, top + 6, B.W - B.m, top + 18), color=SUB, width=0.8)
            B.rtext(p, B.W - B.m - 18, top + 16, "solved", "body", 8.5, SUB)
            ox = B.W / 2 - r["w"] * U / 2
            oy = top + 30 + (slot - 30) / 2 + r["h"] * U / 2
            draw_silhouette(p, r, ox, oy, U, lv)
            nums[r["name"]] = no; no += 1
        i += len(group)
    return nums


def convex_intro(B):
    p = B.page(LEVELS[4][2], "Level 4 · The 13 convex shapes")
    y = 80; B.text(p, B.m, y, "Only Thirteen", "title", 26, NAVY); y += 30
    y = B.para(p, B.m, y,
               "A shape is convex when it has no dents: a straight line between any two of its points stays inside "
               "the shape. Squares, triangles and rectangles are convex; a star is not.\n\n"
               "How many different convex shapes can the seven tangram pieces make? In 1942 two mathematicians at "
               "the National University of Chekiang, Fu Traing Wang and Chuan-Chih Hsiung, proved that the answer "
               "is exactly 13: one triangle, six quadrilaterals, two pentagons and four hexagons.\n\n"
               "Their trick: every tangram piece can be cut into small isosceles right triangles (16 in total), so "
               "a convex tangram must be a convex shape made of 16 of those triangles. There are only 20 such shapes, "
               "and 7 of them cannot be covered by the real pieces.\n\n"
               "We re-checked the theorem by computer for this pack: a search program tried every convex shape built "
               "from 16 small triangles and found a tangram solution for exactly 13. They are the next 13 puzzles. "
               "Can you solve them all?", "body", 11.5, B.W - 2 * B.m)
    # thumbnails of the 13 shapes
    recs = [r for r in B.cat if r["level"] == 4]; cols = 5; tw = (B.W - 2 * B.m) / cols; s = tw * 0.8 / 6
    y += 20
    for k, r in enumerate(recs):
        cx = B.m + (k % cols) * tw + tw / 2; base = y + (k // cols) * (tw * 0.62) + tw * 0.45
        draw_silhouette(p, r, cx - r["w"] * s / 2, base, s, 3)


def tracker(B, nums):
    p = B.page(NAVY, "Progress tracker")
    B.text(p, B.m, 80, "My Tangram Checklist", "title", 24, NAVY)
    B.text(p, B.m, 100, "Tick each shape when you solve it. Write the date if you like!", "body", 10.5, SUB)
    names = sorted(nums, key=lambda n: nums[n]); cols = 2; rows = math.ceil(len(names) / cols)
    cw = (B.W - 2 * B.m) / cols; rh = (B.H - 170) / rows; lv = {r["name"]: r["level"] for r in B.cat}
    for k, n in enumerate(names):
        x = B.m + (k // rows) * cw; y = 125 + (k % rows) * rh
        col = LEVELS[lv[n]][2]
        p.draw_rect(fitz.Rect(x, y, x + 10, y + 10), color=col, width=1)
        B.text(p, x + 18, y + 9, f"{nums[n]}. {n}", "body", 10, INK)
        p.draw_line((x + cw - 75, y + 10), (x + cw - 15, y + 10), color=LINE, width=0.6)


def solutions(B, nums):
    recs = sorted(B.cat, key=lambda r: nums[r["name"]]); per = 12; cols = 3; rows = 4; first = B.pageno + 1
    for s0 in range(0, len(recs), per):
        p = B.page(NAVY, "Solutions")
        cw = (B.W - 2 * B.m) / cols; rh = (B.H - 110) / rows
        for k, r in enumerate(recs[s0:s0 + per]):
            x0 = B.m + (k % cols) * cw; y0 = 50 + (k // cols) * rh
            s = min((cw - 20) / 6, (rh - 40) / 5.6)
            B.text(p, x0 + 4, y0 + 12, f"{nums[r['name']]}. {r['name']}", "semi", 9, INK)
            draw_solution(p, r, x0 + cw / 2 - r["w"] * s / 2, y0 + 22 + (rh - 30) / 2 + r["h"] * s / 2, s)
    return first


def math_page(B):
    p = B.page(NAVY, "The math inside")
    y = 80; B.text(p, B.m, y, "The Math Inside a Tangram", "title", 22, NAVY); y += 30
    y = B.para(p, B.m, y,
               "Tangram is a geometry lab you can hold in your hand. Here are a few things to discover with your pieces.",
               "body", 11.5, B.W - 2 * B.m) + 10
    items = [("Fractions", "Cut the big square into 16 small triangles and every piece is a whole number of them: "
              "each large triangle is 4 (1/4 of the square), the medium triangle, the square and the parallelogram are 2 "
              "each (1/8), and each small triangle is 1 (1/16). Check it: 4+4+2+2+2+1+1 = 16."),
             ("Same area, different shapes", "The medium triangle, the square and the parallelogram look different but "
              "have exactly the same area. Can you prove it by covering each one with the two small triangles?"),
             ("Square roots", "If the short side of a small triangle is 1, its long side is the square root of 2 "
              "(about 1.414), by Pythagoras: 1² + 1² = 2. The big square has side 2√2, about 2.83. Your pieces use "
              "only four lengths: 1, √2, 2 and 2√2."),
             ("Angles", "Every corner of every piece is 45°, 90° or 135°. That is why the pieces fit together so "
              "neatly, and why every figure in this pack has edges in just four directions."),
             ("Area never changes", "Every silhouette in this pack, from the cat to the sleigh, has exactly the same "
              "area: the area of the big square. Shapes can look bigger or smaller, but the area is always 8 small squares."),
             ("Make your own", "Invent a new figure, trace around it, and challenge a friend to solve your silhouette. "
              "Every figure in this pack was built by a computer program fitting the real seven pieces together, "
              "so every puzzle is guaranteed to have a solution.")]
    for t, d in items:
        B.text(p, B.m, y, t, "bold", 12.5, NAVY); y += 17
        y = B.para(p, B.m, y, d, "body", 10.8, B.W - 2 * B.m) + 9


def terms(B):
    p = B.page(NAVY, "Terms of use")
    y = 80; B.text(p, B.m, y, "Terms of Use", "title", 22, NAVY); y += 30
    B.para(p, B.m, y, "For personal use, family use and use in a single classroom. Print as many copies as you need for "
                      "yourself, your household or your own class.\n\nPlease do not resell, share the file, or post it "
                      "anywhere the public can download it.\n\nEvery silhouette was assembled from the seven real pieces "
                      "and checked by computer, so each one has at least one solution (yours may differ from the one "
                      "shown, and that's fine!). If you ever spot a problem, send a message through the shop and a "
                      "corrected file will be sent free.\n\nHappy puzzling!\n\n(c) MathRelaxing", "body", 11, B.W - 2 * B.m)


def build(name, W, H):
    cat = json.load(open(os.path.join(HERE, "catalog.json")))
    by = {lv: [r for r in cat if r["level"] == lv] for lv in (1, 2, 3, 4)}
    tracker_page = 0
    for final in (False, True):
        B = Book(W, H, cat); B.tracker_page = tracker_page
        cover(B); how_to(B); pieces_page(B, True); pieces_page(B, False)
        nums = {}; no = 1
        for lv in (1, 2, 3, 4):
            if lv == 4:
                convex_intro(B)
            n = puzzle_pages(B, by[lv], no); nums.update(n); no += len(n)
        tracker_page = B.pageno + 1
        tracker(B, nums); solutions(B, nums); math_page(B); terms(B)
    path = os.path.join(OUT, f"Tangram_Puzzles_{name}.pdf"); B.save(path)
    print(f"{name}: {B.pageno} pages, {len(nums)} puzzles, {os.path.getsize(path) // 1024} KB")
    return path


if __name__ == "__main__":
    build("Letter", 612, 792)
    build("A4", 595.3, 841.9)
