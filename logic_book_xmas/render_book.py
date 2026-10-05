"""
Vector PDF layout (PyMuPDF) for "Christmas Logic Puzzles" — 101 puzzles with
solutions, US Letter + A4. Reads out/puzzles.json (run puzzles.py first).

  python render_book.py
"""
import os, json, math
import fitz
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out")
AF = os.path.join(REPO, "lulu_books", "assets", "fonts")
FD = os.path.join(OUT, "fonts"); os.makedirs(FD, exist_ok=True)


def c(rgb):
    return tuple(v / 255 for v in rgb)


NAVY = c((24, 36, 64)); RED = c((170, 38, 52)); PINE = c((33, 92, 72)); GOLD = c((196, 152, 64))
INK = c((36, 36, 40)); SUB = c((110, 106, 100)); LINE = c((205, 198, 184)); SOFT = c((246, 241, 230))
CREAM = c((250, 246, 238)); WHITE = (1, 1, 1); PALE = c((236, 242, 238))


def static_fonts():
    out = {}
    for name, w in (("body", 500), ("bold", 700), ("light", 400)):
        p = os.path.join(FD, f"Raleway-{name}.ttf")
        if not os.path.exists(p):
            f = TTFont(os.path.join(AF, "Raleway.ttf"))
            instancer.instantiateVariableFont(f, {"wght": w}, inplace=True)
            f.save(p)
        out[name] = p
    out["title"] = os.path.join(AF, "Cinzel-SemiBold.ttf")
    out["title_r"] = os.path.join(AF, "Cinzel.ttf")
    return out


FONTS = static_fonts()
FOBJ = {k: fitz.Font(fontfile=v) for k, v in FONTS.items()}


class Book:
    def __init__(self, W, H, data):
        self.doc = fitz.open(); self.W, self.H = W, H; self.data = data
        self.m = 0.075 * W
        self.pageno = 0

    # -------------------------------------------------------- primitives
    def page(self, section=None, color=NAVY, number=True):
        p = self.doc.new_page(width=self.W, height=self.H)
        for k, v in FONTS.items():
            p.insert_font(fontname=k, fontfile=v)
        self.pageno += 1
        if section:
            p.draw_rect(fitz.Rect(0, 0, self.W, 6), color=None, fill=color)
            self.text(p, self.m, 30, section.upper(), "bold", 8.5, color)
            snow(p, self.W - self.m - 6, 27, 6, GOLD, 0.8)
        if number:
            self.ctext(p, self.W / 2, self.H - 24, str(self.pageno), "body", 9, SUB)
        return p

    def text(self, p, x, y, s, f, size, col=INK):
        p.insert_text((x, y), s, fontname=f, fontsize=size, color=col)

    def tlen(self, s, f, size):
        return FOBJ[f].text_length(s, fontsize=size)

    def ctext(self, p, cx, y, s, f, size, col=INK):
        self.text(p, cx - self.tlen(s, f, size) / 2, y, s, f, size, col)

    def wrap(self, s, f, size, width):
        out = []
        for para in s.split("\n"):
            line = ""
            for w in para.split(" "):
                t = (line + " " + w).strip()
                if self.tlen(t, f, size) <= width:
                    line = t
                else:
                    out.append(line); line = w
            out.append(line)
        return out

    def para(self, p, x, y, s, f, size, width, col=INK, lh=1.4):
        for ln in self.wrap(s, f, size, width):
            self.text(p, x, y, ln, f, size, col); y += size * lh
        return y

    def heading(self, p, y, title, sub=None, col=NAVY):
        self.text(p, self.m, y, title, "title", 24, col)
        if sub:
            self.text(p, self.m, y + 20, sub, "body", 10, SUB)
        return y + (40 if sub else 22)

    def save(self, path):
        self.doc.save(path, deflate=True, garbage=3)


def snow(p, cx, cy, r, col, w=1.0):
    sh = p.new_shape()
    for k in range(6):
        a = math.pi / 3 * k
        sh.draw_line((cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a)))
        for t in (0.5,):
            bx, by = cx + r * t * math.cos(a), cy + r * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.pi / 4
                sh.draw_line((bx, by), (bx + r * 0.3 * math.cos(b), by + r * 0.3 * math.sin(b)))
    sh.finish(color=col, width=w, lineCap=1); sh.commit()


def star_pts(cx, cy, R, r, k=5):
    return [fitz.Point(cx + (R if i % 2 == 0 else r) * math.cos(-math.pi / 2 + i * math.pi / k),
                       cy + (R if i % 2 == 0 else r) * math.sin(-math.pi / 2 + i * math.pi / k)) for i in range(2 * k)]


# ================================================================ SUDOKU
def draw_sudoku(B, p, x0, y0, size, grid, sol=None):
    cs = size / 9; sh = p.new_shape()
    for i in range(10):
        if i % 3:
            sh.draw_line((x0, y0 + i * cs), (x0 + size, y0 + i * cs)); sh.draw_line((x0 + i * cs, y0), (x0 + i * cs, y0 + size))
    sh.finish(color=LINE, width=0.6)
    for i in range(0, 10, 3):
        sh.draw_line((x0, y0 + i * cs), (x0 + size, y0 + i * cs)); sh.draw_line((x0 + i * cs, y0), (x0 + i * cs, y0 + size))
    sh.finish(color=NAVY, width=1.6 if size > 150 else 1.0); sh.commit()
    fs = cs * 0.55
    for i in range(81):
        r, cc = divmod(i, 9); v = grid[i]
        if v:
            B.ctext(p, x0 + cc * cs + cs / 2, y0 + r * cs + cs * 0.7, str(v), "bold", fs, NAVY)
        elif sol:
            B.ctext(p, x0 + cc * cs + cs / 2, y0 + r * cs + cs * 0.7, str(sol[i]), "light", fs, RED)


def sudoku_pages(B, start_no):
    S = B.data["sudoku"]; nums = []
    lvl_name = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
    for k in range(0, len(S), 2):
        p = B.page("Sudoku", RED)
        if k == 0:
            y = B.heading(p, 64, "Sudoku", "Fill every row, column and 3 x 3 box with the digits 1 to 9.", RED)
        size = min(B.W - 2 * B.m, (B.H - 150) / 2 - 40) * 0.92
        for j in range(2):
            s = S[k + j]; n = start_no + k + j
            yb = 104 + j * (B.H - 130) / 2
            B.text(p, (B.W - size) / 2, yb + 4, f"Puzzle {n}", "bold", 11, RED)
            B.text(p, (B.W + size) / 2 - B.tlen(lvl_name[s["level"]], "body", 10), yb + 4, lvl_name[s["level"]], "body", 10, SUB)
            draw_sudoku(B, p, (B.W - size) / 2, yb + 12, size, s["grid"])
            nums.append(n)
    return nums


# ================================================================ FUTOSHIKI
def chevron(sh, cx, cy, d, s):
    """d: 'L' means '<' (left smaller), 'R' '>' , 'U' '^' (top smaller), 'D' 'v'."""
    if d == "R":
        pts = [(cx - s / 2, cy - s / 2), (cx + s / 2, cy), (cx - s / 2, cy + s / 2)]
    elif d == "L":
        pts = [(cx + s / 2, cy - s / 2), (cx - s / 2, cy), (cx + s / 2, cy + s / 2)]
    elif d == "D":
        pts = [(cx - s / 2, cy - s / 2), (cx, cy + s / 2), (cx + s / 2, cy - s / 2)]
    else:
        pts = [(cx - s / 2, cy + s / 2), (cx, cy - s / 2), (cx + s / 2, cy + s / 2)]
    sh.draw_polyline(pts)


def draw_futoshiki(B, p, x0, y0, size, f, show_sol=False):
    n = f["n"]; cs = size / (n + (n - 1) * 0.5); gap = cs * 0.5
    sh = p.new_shape()
    pos = lambda r, cc: (x0 + cc * (cs + gap), y0 + r * (cs + gap))
    for r in range(n):
        for cc in range(n):
            x, y = pos(r, cc); sh.draw_rect(fitz.Rect(x, y, x + cs, y + cs))
    sh.finish(color=NAVY, width=1.2 if size > 150 else 0.7, fill=WHITE)
    for a, b in f["ineq"]:
        (ar, ac), (br, bc) = a, b  # a > b
        if ar == br:
            x, y = pos(ar, min(ac, bc)); cx, cy = x + cs + gap / 2, y + cs / 2
            chevron(sh, cx, cy, "R" if ac < bc else "L", gap * 0.55)
        else:
            x, y = pos(min(ar, br), ac); cx, cy = x + cs / 2, y + cs + gap / 2
            chevron(sh, cx, cy, "D" if ar < br else "U", gap * 0.55)
    sh.finish(color=RED, width=1.6 if size > 150 else 0.9, closePath=False); sh.commit()
    gv = {(r, cc): v for r, cc, v in f["givens"]}
    for r in range(n):
        for cc in range(n):
            x, y = pos(r, cc)
            if (r, cc) in gv:
                B.ctext(p, x + cs / 2, y + cs * 0.7, str(gv[(r, cc)]), "bold", cs * 0.55, NAVY)
            elif show_sol:
                B.ctext(p, x + cs / 2, y + cs * 0.7, str(f["sol"][r][cc]), "light", cs * 0.55, RED)


def futoshiki_pages(B, start_no):
    F = B.data["futoshiki"]; nums = []
    for k in range(0, len(F), 2):
        p = B.page("Futoshiki", PINE)
        if k == 0:
            B.heading(p, 64, "Futoshiki", "Fill each row and column with 1 to 5. The arrows point to the smaller number.", PINE)
        size = (B.H - 150) / 2 - 70
        for j in range(2):
            n = start_no + k + j; yb = 100 + j * (B.H - 120) / 2
            B.text(p, (B.W - size) / 2, yb + 4, f"Puzzle {n}", "bold", 11, PINE)
            draw_futoshiki(B, p, (B.W - size) / 2, yb + 20, size, F[k + j])
            nums.append(n)
    return nums


# ================================================================ NONOGRAM
def draw_nonogram(B, p, x0, y0, cs, nn, solved=False, clues=True):
    R, C = len(nn["grid"]), len(nn["grid"][0])
    fs = cs * 0.5
    rw = max(len(r) for r in nn["rows"]) * cs * 0.62 if clues else 0
    ch = max(len(c_) for c_ in nn["cols"]) * cs * 0.72 if clues else 0
    gx, gy = x0 + rw, y0 + ch
    if clues:
        for r, cl in enumerate(nn["rows"]):
            s = "  ".join(str(v) for v in cl)
            if r % 2 == 0:
                p.draw_rect(fitz.Rect(x0, gy + r * cs, gx, gy + (r + 1) * cs), color=None, fill=SOFT)
            B.text(p, gx - 6 - B.tlen(s, "bold", fs), gy + r * cs + cs * 0.68, s, "bold", fs, NAVY)
        for cc, cl in enumerate(nn["cols"]):
            if cc % 2 == 0:
                p.draw_rect(fitz.Rect(gx + cc * cs, y0, gx + (cc + 1) * cs, gy), color=None, fill=SOFT)
            for k, v in enumerate(reversed(cl)):
                B.ctext(p, gx + cc * cs + cs / 2, gy - 6 - k * cs * 0.72, str(v), "bold", fs, NAVY)
    if solved:
        sh = p.new_shape()
        for r in range(R):
            for cc in range(C):
                if nn["grid"][r][cc]:
                    sh.draw_rect(fitz.Rect(gx + cc * cs, gy + r * cs, gx + (cc + 1) * cs, gy + (r + 1) * cs))
        sh.finish(color=None, fill=NAVY); sh.commit()
    sh = p.new_shape()
    for i in range(R + 1):
        sh.draw_line((gx, gy + i * cs), (gx + C * cs, gy + i * cs))
    for i in range(C + 1):
        sh.draw_line((gx + i * cs, gy), (gx + i * cs, gy + R * cs))
    sh.finish(color=LINE, width=0.5)
    for i in range(0, R + 1, 5):
        sh.draw_line((gx, gy + i * cs), (gx + C * cs, gy + i * cs))
    for i in range(0, C + 1, 5):
        sh.draw_line((gx + i * cs, gy), (gx + i * cs, gy + R * cs))
    sh.finish(color=NAVY, width=1.2 if cs > 10 else 0.6); sh.commit()
    return rw + C * cs, ch + R * cs


def nonogram_pages(B, start_no):
    nums = []
    for k, nn in enumerate(B.data["nonogram"]):
        p = B.page("Nonograms", NAVY); n = start_no + k
        y = 64
        if k == 0:
            y = B.heading(p, 64, "Nonograms", "Shade the cells. The numbers give the runs of shaded cells in each row and column, in order.", NAVY)
        else:
            y = B.heading(p, 64, "Nonogram", None, NAVY)
        B.text(p, B.m, y + 6, f"Puzzle {n}  ·  a hidden Christmas picture", "bold", 11, RED)
        cs = (B.W - 2 * B.m) / 15 * 0.74
        rw = max(len(r) for r in nn["rows"]) * cs * 0.62; C = len(nn["grid"][0])
        x0 = (B.W - (rw + C * cs)) / 2
        draw_nonogram(B, p, x0, y + 30, cs, nn)
        nums.append(n)
    return nums


# ================================================================ LOGIC GRID
def logic_pages(B, start_no):
    nums = []
    for k, L in enumerate(B.data["logic"]):
        p = B.page("Logic Grids", GOLD); n = start_no + k
        y = B.heading(p, 64, "Logic Grid" if k else "Logic Grids",
                      "Use the clues to match everything. Mark X for 'no' and a dot for 'yes' in the grid." if k == 0 else None, NAVY)
        B.text(p, B.m, y + 6, f"Puzzle {n}  ·  {L['title']}", "bold", 12, RED)
        y = B.para(p, B.m, y + 26, L["intro"], "body", 10.5, B.W - 2 * B.m, INK)
        y += 4
        for i, cl in enumerate(L["clues"]):
            B.text(p, B.m, y, f"{i + 1}.", "bold", 10.5, GOLD)
            y = B.para(p, B.m + 18, y, cl, "body", 10.5, B.W - 2 * B.m - 18, INK, lh=1.35) + 3
        # grid: rows = people + cat2 ; cols = cat1 + cat2
        cats = list(L["cats"]); c1, c2 = cats[0], cats[1]
        A = L["people"]; X = L["cats"][c1]; Y = L["cats"][c2]; nn = len(A)
        cs = min(34 if nn == 4 else 28, (B.W - 2 * B.m - 110) / (2 * nn))
        lw = 92; hh = 78
        gx = (B.W - (lw + 2 * nn * cs)) / 2 + lw; gy = y + 14 + hh
        sh = p.new_shape()
        for bx, by in ((0, 0), (nn, 0), (0, nn)):
            for i in range(nn + 1):
                sh.draw_line((gx + bx * cs, gy + (by + i) * cs), (gx + (bx + nn) * cs, gy + (by + i) * cs))
                sh.draw_line((gx + (bx + i) * cs, gy + by * cs), (gx + (bx + i) * cs, gy + (by + nn) * cs))
        sh.finish(color=LINE, width=0.6)
        for bx, by in ((0, 0), (nn, 0), (0, nn)):
            sh.draw_rect(fitz.Rect(gx + bx * cs, gy + by * cs, gx + (bx + nn) * cs, gy + (by + nn) * cs))
        sh.finish(color=NAVY, width=1.3); sh.commit()
        for i, s in enumerate(A + Y):
            B.text(p, gx - 6 - B.tlen(s, "body", 9), gy + i * cs + cs * 0.65, s, "body", 9, INK)
        for j, s in enumerate(X + Y):
            p.insert_text((gx + j * cs + cs * 0.68, gy - 6), s, fontname="body", fontsize=9, color=INK, rotate=90)
        B.ctext(p, gx + nn * cs / 2, gy - hh - 4, c1.upper(), "bold", 8.5, RED)
        B.ctext(p, gx + nn * cs * 1.5, gy - hh - 4, c2.upper(), "bold", 8.5, RED)
        # answer table
        ty = gy + 2 * nn * cs + 26
        if ty + (nn + 1) * 18 < B.H - 40:
            tx = B.m; cw = (B.W - 2 * B.m) / 3
            B.text(p, tx, ty, "Answer", "bold", 10, NAVY); ty += 8
            for r in range(nn + 1):
                for j, head in enumerate(["Name" if k != 4 else "House", c1, c2]):
                    rect = fitz.Rect(tx + j * cw, ty + r * 18, tx + (j + 1) * cw, ty + (r + 1) * 18)
                    p.draw_rect(rect, color=LINE, width=0.6, fill=SOFT if r == 0 else None)
                    if r == 0:
                        B.text(p, rect.x0 + 6, rect.y0 + 12.5, head, "bold", 9, NAVY)
                    elif j == 0:
                        B.text(p, rect.x0 + 6, rect.y0 + 12.5, A[r - 1], "body", 9, INK)
        nums.append(n)
    return nums


# ================================================================ CRYPTOGRAM
def crypto_block(B, p, x0, y0, width, cr, n, sol=False):
    B.text(p, x0, y0, f"Puzzle {n}", "bold", 11, RED)
    hint = f"Hint: {cr['hint'][0]} = {cr['hint'][1]}"
    B.text(p, x0 + width - B.tlen(hint, "body", 9.5), y0, hint, "body", 9.5, SUB)
    cw = 15.5; y = y0 + 22
    words = cr["enc"].split(" "); plain = cr["plain"].split(" ")
    x = x0
    for w, pw in zip(words, plain):
        ww = len(w) * cw
        if x + ww > x0 + width:
            x = x0; y += 38
        for ch, pc in zip(w, pw):
            if ch.isalpha():
                p.draw_line((x + 1.5, y + 14), (x + cw - 1.5, y + 14), color=NAVY, width=0.7)
                if ch == cr["hint"][0] or sol:
                    B.ctext(p, x + cw / 2, y + 12, pc, "bold", 11, RED if sol else PINE)
                B.ctext(p, x + cw / 2, y + 27, ch, "body", 9.5, NAVY)
            else:
                B.ctext(p, x + cw / 2, y + 12, ch, "bold", 11, NAVY)
            x += cw
        x += cw * 0.6
    B.text(p, x0, y + 46, f"- {cr['who']}", "light", 9, SUB)
    return y + 60


def crypto_pages(B, start_no):
    nums = []; C = B.data["crypto"]
    for k in range(0, len(C), 3):
        p = B.page("Cryptograms", RED)
        y = 64
        if k == 0:
            y = B.heading(p, 64, "Cryptograms", "Each letter stands for another letter. Crack the code to reveal a Christmas or math quote.", RED) + 10
        else:
            y = 60
        for j in range(3):
            if k + j < len(C):
                y = crypto_block(B, p, B.m, y + 10, B.W - 2 * B.m, C[k + j], start_no + k + j) + 6
                nums.append(start_no + k + j)
    return nums


# ================================================================ MAZE
def draw_maze(B, p, x0, y0, size, mz, solution=False):
    n = mz["n"]; cs = size / n
    cells = {tuple(t) for t in mz["cells"]}; links = {frozenset((tuple(a), tuple(b))) for a, b in mz["links"]}
    st, en = tuple(mz["start"]), tuple(mz["end"])
    sh = p.new_shape()
    for (r, cc) in cells:
        x, y = x0 + cc * cs, y0 + r * cs
        for (dr, dcc, seg) in ((-1, 0, ((x, y), (x + cs, y))), (1, 0, ((x, y + cs), (x + cs, y + cs))),
                               (0, -1, ((x, y), (x, y + cs))), (0, 1, ((x + cs, y), (x + cs, y + cs)))):
            nb = (r + dr, cc + dcc)
            if (r, cc) == st and dr == -1 or (r, cc) == en and dr == 1:
                continue
            if nb in cells and frozenset(((r, cc), nb)) in links:
                continue
            if nb in cells and (nb[0], nb[1]) < (r, cc):
                continue  # inner wall drawn once
            sh.draw_line(*seg)
    sh.finish(color=NAVY, width=1.6 if size > 200 else 0.7, lineCap=1); sh.commit()
    if solution:
        pts = [fitz.Point(x0 + cc * cs + cs / 2, y0 + r * cs + cs / 2) for r, cc in mz["path"]]
        p.draw_polyline(pts, color=RED, width=1.4 if size > 200 else 1.0)
    return cs


def maze_pages(B, start_no):
    nums = []
    for k, mz in enumerate(B.data["maze"]):
        p = B.page("Mazes", PINE); n = start_no + k
        y = B.heading(p, 64, "Mazes" if k == 0 else "Maze",
                      "Enter at the top and find the one path to the exit at the bottom." if k == 0 else None, PINE)
        B.text(p, B.m, y + 6, f"Puzzle {n}  ·  {mz['name']}", "bold", 11, RED)
        size = min(B.W - 2 * B.m, B.H - y - 120)
        x0 = (B.W - size) / 2; y0 = y + 40
        cs = draw_maze(B, p, x0, y0, size, mz)
        st, en = mz["start"], mz["end"]
        B.ctext(p, x0 + st[1] * cs + cs / 2, y0 + st[0] * cs - 8, "START", "bold", 8, PINE)
        p.draw_polyline(star_pts(x0 + st[1] * cs + cs / 2, y0 + st[0] * cs - 24, 7, 3), color=None, fill=GOLD, closePath=True)
        B.ctext(p, x0 + en[1] * cs + cs / 2, y0 + (en[0] + 1) * cs + 14, "EXIT", "bold", 8, RED)
        nums.append(n)
    return nums


# ================================================================ TEASERS
def teaser_pages(B, start_no):
    nums = []; T = B.data["teaser"]
    for k in range(0, len(T), 4):
        p = B.page("Brain Teasers", GOLD)
        y = 64
        if k == 0:
            y = B.heading(p, 64, "Brain Teasers", "Christmas math riddles. Use the space to work them out.", NAVY) + 4
        else:
            y = 56
        step = (B.H - y - 40) / 4
        for j in range(4):
            if k + j >= len(T):
                break
            t, q, _ = T[k + j]; n = start_no + k + j; yy = y + j * step + 10
            B.text(p, B.m, yy, f"Puzzle {n}  ·  {t}", "bold", 11, RED)
            yb = B.para(p, B.m, yy + 18, q, "body", 10.5, B.W - 2 * B.m, INK)
            sh = p.new_shape()
            for ly in range(int(yb + 18), int(yy + step - 22), 20):
                sh.draw_line((B.m, ly), (B.W - B.m, ly))
            sh.finish(color=LINE, width=0.5, dashes="[1 3] 0"); sh.commit()
            nums.append(n)
    return nums


# ================================================================ FRONT MATTER
def cover(B):
    p = B.page(number=False)
    W, H = B.W, B.H
    p.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=NAVY)
    import random
    rnd = random.Random(3)
    for _ in range(60):
        snow(p, rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice((3, 5, 7)), c((60, 76, 110)), 0.8)
    # pixel-art tree from nonogram 1
    g = B.data["nonogram"][0]["grid"]; cs = W * 0.026
    gx = (W - 15 * cs) / 2; gy = H * 0.08
    sh = p.new_shape()
    for r in range(15):
        for cc in range(15):
            if g[r][cc]:
                sh.draw_rect(fitz.Rect(gx + cc * cs + 0.6, gy + r * cs + 0.6, gx + (cc + 1) * cs - 0.6, gy + (r + 1) * cs - 0.6))
    sh.finish(color=None, fill=c((52, 140, 104))); sh.commit()
    p.draw_polyline(star_pts(gx + 7.5 * cs, gy - cs * 0.4, cs * 1.3, cs * 0.55), color=None, fill=GOLD, closePath=True)
    # mini sudoku strip
    y = gy + 15 * cs + 30
    B.ctext(p, W / 2, y + 36, "CHRISTMAS", "title", W * 0.085, CREAM)
    B.ctext(p, W / 2, y + 36 + W * 0.095, "LOGIC PUZZLES", "title", W * 0.075, GOLD)
    B.ctext(p, W / 2, y + 36 + W * 0.165, "101 brain teasers for teens & adults", "body", W * 0.032, CREAM)
    types = "Sudoku  ·  Futoshiki  ·  Nonograms  ·  Logic Grids  ·  Cryptograms  ·  Mazes  ·  Brain Teasers"
    B.ctext(p, W / 2, H * 0.80, types, "body", W * 0.0175, c((210, 216, 230)))
    B.ctext(p, W / 2, H * 0.84, "Full solutions included", "bold", W * 0.02, GOLD)
    B.ctext(p, W / 2, H * 0.95, "MathRelaxing", "title_r", W * 0.022, c((210, 216, 230)))


def intro(B):
    p = B.page("Welcome", NAVY)
    y = B.heading(p, 70, "How to Play", None, NAVY) + 8
    rules = [
        ("Sudoku (30)", "Fill every row, column and 3 x 3 box with the digits 1 to 9, each exactly once. Puzzles go from easy to hard.", RED),
        ("Futoshiki (12)", "Fill each row and column of the 5 x 5 grid with 1 to 5. The arrows between cells point to the smaller number, like < and >.", PINE),
        ("Nonograms (10)", "Shade cells to reveal a Christmas picture. The numbers beside each row and above each column give, in order, the lengths of the runs of shaded cells. Every picture can be solved by logic alone, without guessing.", NAVY),
        ("Logic Grids (6)", "Match the people with their items using the clues. Mark X in a cell for 'no' and a dot for 'yes'; every row and column of each block has exactly one 'yes'.", GOLD),
        ("Cryptograms (15)", "Each letter has been swapped for a different letter, the same way throughout the puzzle. One letter is given as a hint. Use word shapes and common letters to crack the quote.", RED),
        ("Mazes (8)", "Find the single path from START to EXIT through a Christmas-shaped maze.", PINE),
        ("Brain Teasers (20)", "Christmas math riddles: some need arithmetic, some need a clever idea. Every answer is explained in the solutions.", NAVY),
    ]
    for t, s, col in rules:
        p.draw_rect(fitz.Rect(B.m, y - 10, B.m + 4, y + 30), color=None, fill=col)
        B.text(p, B.m + 14, y, t, "bold", 12, col)
        y = B.para(p, B.m + 14, y + 16, s, "body", 10.5, B.W - 2 * B.m - 14) + 14
    y += 6
    B.para(p, B.m, y, "Tip: print the pages you want and solve in pencil. Every puzzle has exactly one solution, and all "
                      "solutions are at the back of the book. Merry Christmas and happy puzzling!", "light", 10.5, B.W - 2 * B.m, SUB)


def contents(B, sections):
    p = B.page("Contents", NAVY)
    y = B.heading(p, 70, "Contents", None, NAVY) + 16
    for name, pg, rng, col in sections:
        B.text(p, B.m, y, name, "bold", 13, col)
        B.text(p, B.m + 190, y, rng, "body", 11, SUB)
        s = f"page {pg}"; B.text(p, B.W - B.m - B.tlen(s, "body", 11), y, s, "body", 11, INK)
        p.draw_line((B.m, y + 9), (B.W - B.m, y + 9), color=LINE, width=0.5)
        y += 34


# ================================================================ SOLUTIONS
def solutions(B, nums):
    D = B.data
    gw = B.W - 2 * B.m
    # sudoku 6 per page
    S = D["sudoku"]; first = B.pageno + 1
    for k in range(0, len(S), 6):
        p = B.page("Solutions", RED)
        if k == 0:
            B.heading(p, 64, "Solutions", None, NAVY)
        size = min(gw / 2 * 0.74, (B.H - 120) / 3 - 34)
        for j in range(6):
            if k + j >= len(S):
                break
            r, cc = divmod(j, 2)
            x = B.m + cc * gw / 2 + (gw / 2 - size) / 2; y = 100 + r * (size + 32)
            B.text(p, x, y - 6, f"Puzzle {nums['sudoku'][k + j]}", "bold", 9.5, RED)
            draw_sudoku(B, p, x, y, size, S[k + j]["grid"], S[k + j]["sol"])
    # futoshiki 6 per page
    F = D["futoshiki"]
    for k in range(0, len(F), 6):
        p = B.page("Solutions", PINE)
        size = gw / 2 * 0.6
        for j in range(6):
            if k + j >= len(F):
                break
            r, cc = divmod(j, 2)
            x = B.m + cc * gw / 2 + (gw / 2 - size) / 2; y = 90 + r * (size + 60)
            B.text(p, x, y - 8, f"Puzzle {nums['futoshiki'][k + j]}", "bold", 9.5, PINE)
            draw_futoshiki(B, p, x, y, size, F[k + j], show_sol=True)
    # nonograms 4 per page (pictures, no clues)
    NN = D["nonogram"]
    for k in range(0, len(NN), 6):
        p = B.page("Solutions", NAVY)
        cs = gw / 2 * 0.5 / 15
        for j in range(6):
            if k + j >= len(NN):
                break
            r, cc = divmod(j, 2)
            x = B.m + cc * gw / 2 + (gw / 2 - 15 * cs) / 2; y = 90 + r * (15 * cs + 60)
            B.text(p, x, y - 8, f"Puzzle {nums['nonogram'][k + j]}  ·  {NN[k + j]['name']}", "bold", 9.5, NAVY)
            draw_nonogram(B, p, x, y, cs, NN[k + j], solved=True, clues=False)
    # logic grids (text)
    L = D["logic"]
    p = B.page("Solutions", GOLD); y = 70
    for j, lg in enumerate(L):
        if y > B.H - 150:
            p = B.page("Solutions", GOLD); y = 70
        B.text(p, B.m, y, f"Puzzle {nums['logic'][j]}  ·  {lg['title']}", "bold", 11, RED); y += 18
        cats = list(lg["cats"])
        for person in lg["people"]:
            s = f"{person}:  " + ",  ".join(lg["sol"][cat][person] for cat in cats)
            B.text(p, B.m + 12, y, s, "body", 10.5, INK); y += 15
        y += 14
    # cryptograms
    C = D["crypto"]; p = B.page("Solutions", RED); y = 70
    for j, cr in enumerate(C):
        lines = B.wrap(cr["plain"].capitalize(), "body", 10.5, gw - 12)
        if y + 18 + len(lines) * 15 > B.H - 50:
            p = B.page("Solutions", RED); y = 70
        B.text(p, B.m, y, f"Puzzle {nums['crypto'][j]}", "bold", 11, RED); y += 16
        y = B.para(p, B.m + 12, y, f"\"{cr['plain']}\" - {cr['who']}", "body", 10, gw - 12, INK, lh=1.35) + 10
    # mazes 4 per page
    M = D["maze"]
    for k in range(0, len(M), 4):
        p = B.page("Solutions", PINE)
        size = gw / 2 * 0.86
        for j in range(4):
            r, cc = divmod(j, 2)
            x = B.m + cc * gw / 2 + (gw / 2 - size) / 2; y = 80 + r * (size + 60)
            B.text(p, x, y - 10, f"Puzzle {nums['maze'][k + j]}  ·  {M[k + j]['name']}", "bold", 9.5, PINE)
            draw_maze(B, p, x, y, size, M[k + j], solution=True)
    # teasers
    T = D["teaser"]; p = B.page("Solutions", GOLD); y = 70
    for j, (t, _, a) in enumerate(T):
        lines = B.wrap(a, "body", 10.5, gw - 12)
        if y + 20 + len(lines) * 15 > B.H - 50:
            p = B.page("Solutions", GOLD); y = 70
        B.text(p, B.m, y, f"Puzzle {nums['teaser'][j]}  ·  {t}", "bold", 11, RED); y += 16
        y = B.para(p, B.m + 12, y, a, "body", 10.5, gw - 12, INK, lh=1.35) + 12
    return first


def terms(B):
    p = B.page("Terms of Use", NAVY)
    y = B.heading(p, 70, "Terms of Use", None, NAVY) + 12
    B.para(p, B.m, y, "For personal use, family use and use in a single classroom. Print as many copies as you need for "
                      "yourself, your household or your own class.\n\nPlease do not resell, share the file, or post it "
                      "anywhere the public can download it.\n\nEvery puzzle in this book was generated and checked by "
                      "computer to have exactly one solution. The quotes in the cryptograms are from public-domain works. "
                      "If you ever spot a problem, send a message through the shop and a corrected file will be sent free."
                      "\n\nMerry Christmas and happy puzzling!\n\n(c) MathRelaxing", "body", 11, B.W - 2 * B.m)


def build(name, W, H):
    data = json.load(open(os.path.join(OUT, "puzzles.json")))
    # first pass to learn page numbers of sections, second pass to draw with the real contents
    for final in (False, True):
        B = Book(W, H, data)
        cover(B); intro(B)
        if final:
            contents(B, SECTIONS)
        else:
            B.page()
        sec = []; nums = {}; no = 1
        for key, fn, title, col in (("sudoku", sudoku_pages, "Sudoku", RED), ("futoshiki", futoshiki_pages, "Futoshiki", PINE),
                                    ("nonogram", nonogram_pages, "Nonograms", NAVY), ("logic", logic_pages, "Logic Grids", GOLD),
                                    ("crypto", crypto_pages, "Cryptograms", RED), ("maze", maze_pages, "Mazes", PINE),
                                    ("teaser", teaser_pages, "Brain Teasers", NAVY)):
            pg = B.pageno + 1
            nums[key] = fn(B, no)
            sec.append((title, pg, f"puzzles {nums[key][0]}-{nums[key][-1]}", col)); no = nums[key][-1] + 1
        spg = solutions(B, nums)
        sec.append(("Solutions", spg, "all 101 puzzles", INK))
        terms(B)
        SECTIONS = sec
    assert no - 1 == 101, no
    path = os.path.join(OUT, f"Christmas_Logic_Puzzles_{name}.pdf")
    B.save(path)
    print(f"{name}: {B.pageno} pages, {os.path.getsize(path) // 1024} KB")
    return path


if __name__ == "__main__":
    build("Letter", 612, 792)
    build("A4", 595.3, 841.9)
