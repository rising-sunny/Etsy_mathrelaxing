"""
generate_brain_games.py — MathRelaxing printable Brain Games pack
================================================================
Algorithmically generates a printable puzzle book (US Letter, 300 dpi) with
answer keys: Sudoku (easy/medium/hard, unique solutions), mazes (with the
solution path), and STEM word searches. Rendered with PIL, assembled to a
print-ready PDF via img2pdf, plus a ZIP and Etsy listing images.

  python generate_brain_games.py
"""
from __future__ import annotations
import os, random, zipfile
from pathlib import Path
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf

BASE = Path(__file__).resolve().parent
OUT = BASE / "out"; OUT.mkdir(exist_ok=True)
FONTS = BASE.parent / "lulu_books" / "assets" / "fonts"

W, H = 2550, 3300
MX, MY = 200, 210
PAPER = "#F6F3EA"; INK = "#1c2b3a"; INK_SOFT = "#3c4a58"; MUTED = "#8a8577"
GRID = "#c7cdd4"; GRIDBOLD = "#1c2b3a"; ACCENT = "#b0862f"; PANEL = "#FCFAF3"

def hx(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
def F(name, size): return ImageFont.truetype(str(FONTS / name), size)
def DISP(s): return F("Cinzel-SemiBold.ttf", s)
def HEAD(s): return F("Cinzel.ttf", s)
def BODY(s): return F("Raleway.ttf", s)
def ITAL(s): return F("Raleway-Italic.ttf", s)


# ══════════════════════════ SUDOKU ══════════════════════════
def _sudoku_full():
    g = [[0]*9 for _ in range(9)]
    def ok(r, c, v):
        if any(g[r][x] == v for x in range(9)): return False
        if any(g[x][c] == v for x in range(9)): return False
        br, bc = 3*(r//3), 3*(c//3)
        return all(g[br+i][bc+j] != v for i in range(3) for j in range(3))
    def fill(p=0):
        if p == 81: return True
        r, c = divmod(p, 9)
        vals = list(range(1, 10)); random.shuffle(vals)
        for v in vals:
            if ok(r, c, v):
                g[r][c] = v
                if fill(p+1): return True
                g[r][c] = 0
        return False
    fill(); return g


def _count_solutions(g, limit=2):
    empt = [(r, c) for r in range(9) for c in range(9) if g[r][c] == 0]
    cnt = 0
    def ok(r, c, v):
        if any(g[r][x] == v for x in range(9)): return False
        if any(g[x][c] == v for x in range(9)): return False
        br, bc = 3*(r//3), 3*(c//3)
        return all(g[br+i][bc+j] != v for i in range(3) for j in range(3))
    def bt(i=0):
        nonlocal cnt
        if cnt >= limit: return
        if i == len(empt):
            cnt += 1; return
        r, c = empt[i]
        for v in range(1, 10):
            if ok(r, c, v):
                g[r][c] = v; bt(i+1); g[r][c] = 0
    bt(); return cnt


def make_sudoku(clues=36):
    full = _sudoku_full()
    puz = [row[:] for row in full]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    filled = 81
    for (r, c) in cells:
        if filled <= clues: break
        saved = puz[r][c]
        puz[r][c] = 0
        g2 = [row[:] for row in puz]
        if _count_solutions(g2, 2) != 1:
            puz[r][c] = saved            # keep — removal broke uniqueness
        else:
            filled -= 1
    return puz, full


def draw_sudoku(im, d, x0, y0, side, puz, sol=None, accent_given=True):
    cell = side // 9
    # subtle given-cell shading + solution digits (for answer key)
    for r in range(9):
        for c in range(9):
            cx, cy = x0 + c*cell, y0 + r*cell
            v = puz[r][c]
            if v:
                if accent_given:
                    d.rectangle((cx, cy, cx+cell, cy+cell), fill=hx(PANEL))
                d.text((cx+cell//2, cy+cell//2), str(v), font=BODY(int(cell*0.62)),
                       fill=hx(INK), anchor="mm")
            elif sol is not None:
                d.text((cx+cell//2, cy+cell//2), str(sol[r][c]), font=BODY(int(cell*0.6)),
                       fill=hx(ACCENT), anchor="mm")
    for i in range(10):
        w = 5 if i % 3 == 0 else 2
        col = hx(GRIDBOLD) if i % 3 == 0 else hx(GRID)
        d.line((x0+i*cell, y0, x0+i*cell, y0+9*cell), fill=col, width=w)
        d.line((x0, y0+i*cell, x0+9*cell, y0+i*cell), fill=col, width=w)


# ══════════════════════════ MAZE ══════════════════════════
def make_maze(cols, rows, seed=None):
    if seed is not None: random.seed(seed)
    # walls[r][c] = [top,right,bottom,left] present
    wall = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    vis = [[False]*cols for _ in range(rows)]
    stack = [(0, 0)]; vis[0][0] = True
    while stack:
        r, c = stack[-1]
        nb = []
        if r > 0 and not vis[r-1][c]: nb.append((r-1, c, 0, 2))
        if c < cols-1 and not vis[r][c+1]: nb.append((r, c+1, 1, 3))
        if r < rows-1 and not vis[r+1][c]: nb.append((r+1, c, 2, 0))
        if c > 0 and not vis[r][c-1]: nb.append((r, c-1, 3, 1))
        if nb:
            nr, nc, wa, wb = random.choice(nb)
            wall[r][c][wa] = False; wall[nr][nc][wb] = False
            vis[nr][nc] = True; stack.append((nr, nc))
        else:
            stack.pop()
    return wall


def solve_maze(wall, cols, rows):
    start, end = (0, 0), (rows-1, cols-1)
    prev = {start: None}; q = deque([start])
    while q:
        r, c = q.popleft()
        if (r, c) == end: break
        moves = []
        if not wall[r][c][0]: moves.append((r-1, c))
        if not wall[r][c][1]: moves.append((r, c+1))
        if not wall[r][c][2]: moves.append((r+1, c))
        if not wall[r][c][3]: moves.append((r, c-1))
        for m in moves:
            if m not in prev:
                prev[m] = (r, c); q.append(m)
    path = []; cur = end
    while cur is not None:
        path.append(cur); cur = prev.get(cur)
    return path[::-1]


def draw_maze(d, x0, y0, size, cols, rows, wall, path=None):
    cell = size // max(cols, rows)
    ox = x0 + (size - cell*cols)//2; oy = y0 + (size - cell*rows)//2
    if path:
        pts = [(ox + c*cell + cell//2, oy + r*cell + cell//2) for (r, c) in path]
        d.line(pts, fill=hx(ACCENT), width=max(3, cell//6), joint="curve")
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c*cell, oy + r*cell
            if wall[r][c][0]: d.line((x, y, x+cell, y), fill=hx(INK), width=3)
            if wall[r][c][3]: d.line((x, y, x, y+cell), fill=hx(INK), width=3)
    d.line((ox, oy+rows*cell, ox+cols*cell, oy+rows*cell), fill=hx(INK), width=3)
    d.line((ox+cols*cell, oy, ox+cols*cell, oy+rows*cell), fill=hx(INK), width=3)
    # entrance (top-left) & exit (bottom-right) openings
    d.rectangle((ox+3, oy-6, ox+cell-3, oy+3), fill=hx(PAPER))
    d.rectangle((ox+(cols-1)*cell+3, oy+rows*cell-3, ox+cols*cell-3, oy+rows*cell+6), fill=hx(PAPER))


# ══════════════════════════ WORD SEARCH ══════════════════════════
WS_THEMES = {
    "Mathematics": ["ALGEBRA", "GEOMETRY", "FRACTION", "INTEGER", "EQUATION", "POLYGON",
                    "PRIME", "MATRIX", "VECTOR", "RADIUS", "TANGENT", "PROOF"],
    "Science": ["ATOM", "ENERGY", "GRAVITY", "MOLECULE", "PHOTON", "GENOME",
                "NEURON", "PLASMA", "ORBIT", "FUSION", "ENZYME", "QUARK"],
    "Geometry": ["TRIANGLE", "CIRCLE", "SQUARE", "HEXAGON", "SPHERE", "ANGLE",
                 "VERTEX", "PRISM", "CONE", "CHORD", "ARC", "AREA"],
    "Space": ["GALAXY", "COMET", "NEBULA", "PLANET", "METEOR", "COSMOS",
              "ECLIPSE", "GRAVITY", "ORBIT", "STAR", "LUNAR", "SOLAR"],
}
DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]


def make_wordsearch(words, n=14):
    grid = [[None]*n for _ in range(n)]
    placed = []
    for w in sorted(words, key=len, reverse=True):
        for _ in range(300):
            dr, dc = random.choice(DIRS)
            r0 = random.randrange(n); c0 = random.randrange(n)
            r1, c1 = r0 + dr*(len(w)-1), c0 + dc*(len(w)-1)
            if not (0 <= r1 < n and 0 <= c1 < n): continue
            cells = [(r0+dr*i, c0+dc*i) for i in range(len(w))]
            if all(grid[r][c] in (None, w[i]) for i, (r, c) in enumerate(cells)):
                for i, (r, c) in enumerate(cells): grid[r][c] = w[i]
                placed.append((w, cells)); break
    for r in range(n):
        for c in range(n):
            if grid[r][c] is None:
                grid[r][c] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return grid, placed


def draw_wordsearch(d, x0, y0, size, grid, words, placed=None):
    n = len(grid); cell = size // n
    if placed:
        for (w, cells) in placed:
            (r0, c0), (r1, c1) = cells[0], cells[-1]
            p0 = (x0+c0*cell+cell//2, y0+r0*cell+cell//2)
            p1 = (x0+c1*cell+cell//2, y0+r1*cell+cell//2)
            d.line((p0, p1), fill=hx(ACCENT)+(0,), width=1)  # placeholder (overdrawn below)
            d.line((p0, p1), fill=hx(ACCENT), width=max(6, cell//4))
    for r in range(n):
        for c in range(n):
            d.text((x0+c*cell+cell//2, y0+r*cell+cell//2), grid[r][c],
                   font=BODY(int(cell*0.5)), fill=hx(INK), anchor="mm")


# ══════════════════════════ PAGES ══════════════════════════
def page():
    im = Image.new("RGB", (W, H), hx(PAPER)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 70, W-70, H-70), radius=26, outline=hx(GRID), width=3)
    return im, d


def header(d, kicker, title):
    d.text((MX, MY+40), kicker.upper(), font=BODY(30), fill=hx(ACCENT), anchor="lm")
    d.text((MX, MY+110), title, font=DISP(84), fill=hx(INK), anchor="lm")
    d.line((MX, MY+180, MX+430, MY+180), fill=hx(ACCENT), width=6)


def footer(d, label):
    d.line((MX, H-165, W-MX, H-165), fill=hx(GRID), width=2)
    d.text((MX, H-128), "MATHRELAXING  ·  BRAIN GAMES", font=BODY(28), fill=hx(MUTED), anchor="lm")
    d.text((W-MX, H-128), label, font=BODY(28), fill=hx(MUTED), anchor="rm")


def p_cover():
    im, d = page(); cx = W//2
    d.text((cx, 560), "A   P R I N T A B L E   P U Z Z L E   B O O K", font=BODY(34), fill=hx(ACCENT), anchor="mm")
    d.line((cx-330, 620, cx+330, 620), fill=hx(ACCENT), width=3)
    d.text((cx, 940), "Brain", font=DISP(210), fill=hx(INK), anchor="mm")
    d.text((cx, 1150), "Games", font=DISP(210), fill=hx(INK), anchor="mm")
    d.text((cx, 1360), "Sudoku · Mazes · Word Searches — with answer keys", font=ITAL(44), fill=hx(INK_SOFT), anchor="mm")
    # a little sudoku motif
    demo, _ = make_sudoku(40)
    draw_sudoku(im, d, cx-360, 1560, 720, demo)
    d.text((cx, H-330), "For all ages · Print at home · US Letter", font=BODY(34), fill=hx(INK_SOFT), anchor="mm")
    d.text((cx, H-270), "MathRelaxing", font=HEAD(40), fill=hx(INK), anchor="mm")
    return im


def p_howto():
    im, d = page(); header(d, "How to play", "The Rules")
    y = MY+280
    rules = [
        ("Sudoku", "Fill the grid so every row, every column and every 3×3 box contains the digits 1–9, with no repeats."),
        ("Mazes", "Find a path from the opening at the top-left to the exit at the bottom-right."),
        ("Word Search", "Find every listed word hidden in the grid — horizontally, vertically or diagonally, forwards or backwards."),
    ]
    for name, txt in rules:
        d.text((MX, y), name, font=DISP(52), fill=hx(ACCENT), anchor="lm"); y += 72
        for line in _wrap(d, txt, BODY(38), W-2*MX):
            d.text((MX, y), line, font=BODY(38), fill=hx(INK_SOFT), anchor="lm"); y += 58
        y += 60
    d.text((MX, y+20), "Answer keys for every puzzle are at the back of the book.",
           font=ITAL(38), fill=hx(INK), anchor="lm")
    footer(d, "How to play")
    return im


def _wrap(d, text, font, maxw):
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def p_sudoku_pair(puzzles, idx, label):
    """two sudoku per page"""
    im, d = page(); header(d, "Sudoku", label)
    positions = [(MX+40, MY+300), (MX+40, MY+300+1180)]
    side = 1040
    for (puz, meta), (x0, y0) in zip(puzzles, positions):
        d.text((x0, y0-56), f"Puzzle {meta['n']}  ·  {meta['diff']}", font=BODY(38), fill=hx(INK), anchor="lm")
        draw_sudoku(im, d, (W-side)//2, y0, side, puz)
    footer(d, label)
    return im


def p_maze(wall, cols, rows, n, label):
    im, d = page(); header(d, "Maze", label)
    d.text((MX, MY+230), f"Maze {n}  ·  {cols}×{rows}", font=BODY(38), fill=hx(INK), anchor="lm")
    draw_maze(d, (W-2100)//2, MY+320, 2100, cols, rows, wall)
    footer(d, label)
    return im


def p_wordsearch(grid, words, theme, n, label):
    im, d = page(); header(d, "Word Search", theme)
    d.text((MX, MY+230), f"Puzzle {n}  ·  find {len(words)} words", font=BODY(38), fill=hx(INK), anchor="lm")
    size = 1500; x0 = (W-size)//2; y0 = MY+320
    draw_wordsearch(d, x0, y0, size, grid, words)
    # word list
    d.rounded_rectangle((MX, y0+size+70, W-MX, y0+size+70+430), radius=18, fill=hx(PANEL), outline=hx(GRID), width=3)
    wy = y0+size+130; col_w = (W-2*MX-120)//3
    for i, w in enumerate(sorted(words)):
        wx = MX+60 + (i % 3)*col_w
        d.text((wx, wy + (i//3)*74), w.title(), font=BODY(40), fill=hx(INK_SOFT), anchor="lm")
    footer(d, theme)
    return im


def p_solutions_sudoku(items, label):
    im, d = page(); header(d, "Answer key", "Sudoku")
    xs = [(W//2-540-40), (W//2+40)]; side = 540; yrow = MY+320
    for i, (puz, full, meta) in enumerate(items):
        col = i % 2; row = i // 2
        x0 = xs[col]; y0 = yrow + row*(side+150)
        d.text((x0, y0-46), f"Puzzle {meta['n']}", font=BODY(30), fill=hx(INK), anchor="lm")
        draw_sudoku(im, d, x0, y0, side, puz, sol=full)
    footer(d, "Answer key")
    return im


def p_solutions_maze(items, label):
    im, d = page(); header(d, "Answer key", "Mazes")
    size = 640; xs = [W//2-size-40, W//2+40]; yrow = MY+320
    for i, (wall, cols, rows, path, n) in enumerate(items):
        col = i % 2; row = i // 2
        x0 = xs[col]; y0 = yrow + row*(size+130)
        d.text((x0+20, y0-40), f"Maze {n}", font=BODY(30), fill=hx(INK), anchor="lm")
        draw_maze(d, x0, y0, size, cols, rows, wall, path=path)
    footer(d, "Answer key")
    return im


def p_solutions_ws(items, label):
    im, d = page(); header(d, "Answer key", "Word Search")
    size = 700; xs = [W//2-size-40, W//2+40]; yrow = MY+320
    for i, (grid, placed, theme, n) in enumerate(items):
        col = i % 2; row = i // 2
        x0 = xs[col]; y0 = yrow + row*(size+140)
        d.text((x0+20, y0-40), f"{theme} ({n})", font=BODY(28), fill=hx(INK), anchor="lm")
        draw_wordsearch(d, x0, y0, size, grid, [w for w, _ in placed], placed=placed)
    footer(d, "Answer key")
    return im


def build(seed=7):
    random.seed(seed)
    pages = [p_cover(), p_howto()]

    # ---- Sudoku: 12 puzzles (4 easy/med/hard) ----
    diffs = [("Easy", 40)]*4 + [("Medium", 32)]*4 + [("Hard", 26)]*4
    sud = []
    for i, (dname, clues) in enumerate(diffs, 1):
        puz, full = make_sudoku(clues)
        sud.append((puz, full, {"n": i, "diff": dname}))
    for i in range(0, len(sud), 2):
        pair = [(sud[i][0], sud[i][2]), (sud[i+1][0], sud[i+1][2])]
        pages.append(p_sudoku_pair(pair, i, f"{sud[i][2]['diff']}"))

    # ---- Mazes: 6 ----
    mazes = []
    for i, (cols, rows) in enumerate([(18, 24), (18, 24), (22, 28), (22, 28), (26, 34), (26, 34)], 1):
        wall = make_maze(cols, rows, seed=seed*10+i)
        path = solve_maze(wall, cols, rows)
        mazes.append((wall, cols, rows, path, i))
        pages.append(p_maze(wall, cols, rows, i, f"Maze {i}"))

    # ---- Word searches: 4 themes ----
    ws = []
    for i, (theme, words) in enumerate(WS_THEMES.items(), 1):
        grid, placed = make_wordsearch(words, n=14)
        ws.append((grid, placed, theme, i))
        pages.append(p_wordsearch(grid, [w for w, _ in placed], theme, i, theme))

    # ---- Solutions ----
    for i in range(0, len(sud), 6):
        pages.append(p_solutions_sudoku(sud[i:i+6], "Sudoku"))
    pages.append(p_solutions_maze(mazes[:6], "Mazes"))
    pages.append(p_solutions_ws(ws, "Word Search"))
    return pages


def save_pdf(pages):
    pdir = OUT / "pages"; pdir.mkdir(exist_ok=True)
    for old in pdir.glob("*.jpg"): old.unlink()
    paths = []
    for i, im in enumerate(pages, 1):
        p = pdir / f"p{i:02d}.jpg"; im.convert("RGB").save(p, "JPEG", quality=90, dpi=(300, 300)); paths.append(p)
    pdf = OUT / "MathRelaxing_Brain_Games.pdf"
    layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in paths], layout_fun=layout))
    print(f"  PDF {pdf.name} ({pdf.stat().st_size//1024} KB, {len(pages)} pages)")
    return pdf, paths


if __name__ == "__main__":
    print("=== MathRelaxing Brain Games ===")
    pgs = build()
    save_pdf(pgs)
    print("DONE →", OUT)
