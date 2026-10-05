"""
Christmas Escape Room for Kids — "The Great Workshop Lockdown".

8 math & logic puzzles; each answer is a number 1-26 that the Workshop Decoder
(A=1 ... Z=26) turns into a letter. The 8 letters spell the vault password.
Includes host guide, mission briefing, final vault, hint cards, answer key,
certificate and terms. US Letter + A4 PDFs at 300 DPI.

  python generate_escape.py
"""
import os, sys, math
from PIL import Image, ImageDraw
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
from generate_advent import font, wrap, draw_par, snowflake, CREAM, NAVY, RED, PINE, GOLD, INK, SUB, LINE

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
DPI = 300
SOFTG = (232, 240, 234); SOFTR = (247, 230, 230)
PASSWORD = "PRESENTS"


def a1z26(n):
    return chr(ord("A") + n - 1)


# ------------------------------------------------------------------ puzzle maths
def p1_answer():
    seq = [1, 2, 4, 7, 11]
    return seq[-1] + (seq[-1] - seq[-2]) + 1          # differences 1,2,3,4,5 -> 16


def p2_answer():
    sols = [n for n in range(1, 30) if n % 3 == 0 and n % 4 == 2 and n % 5 == 3]
    assert len(sols) == 1
    return sols[0]                                   # 18


def p3_answer():
    snowman = 3                                      # 1 snowman = 3 stars
    return snowman + 2                               # tree = snowman + 2 stars = 5


MAGIC = [[12, 17, 16], [None, 15, 11], [14, 13, 18]]


def p4_answer():
    total = sum(MAGIC[0])
    x = total - MAGIC[1][1] - MAGIC[1][2]
    full = [[x if v is None else v for v in r] for r in MAGIC]
    assert all(sum(r) == total for r in full)
    assert all(sum(full[r][c] for r in range(3)) == total for c in range(3))
    assert full[0][0] + full[1][1] + full[2][2] == total and full[0][2] + full[1][1] + full[2][0] == total
    return x                                         # 19


def p5_answer():
    # bottom [2, X, 3]; middle [2+X, X+3]; top 2X+5 = 15
    return (15 - 5) // 2                             # 5


EDGES = {("North Pole", "Pine Hill"): 5, ("North Pole", "Ice Lake"): 3, ("Pine Hill", "Snow Fort"): 4,
         ("Ice Lake", "Snow Fort"): 6, ("Pine Hill", "Town"): 9, ("Snow Fort", "Town"): 5, ("Ice Lake", "Town"): 12}


def p6_answer():
    import heapq
    g = {}
    for (a, b), w in EDGES.items():
        g.setdefault(a, []).append((b, w)); g.setdefault(b, []).append((a, w))
    dist = {"North Pole": 0}; pq = [(0, "North Pole")]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e9): continue
        for v, w in g[u]:
            if d + w < dist.get(v, 1e9):
                dist[v] = d + w; heapq.heappush(pq, (d + w, v))
    return dist["Town"]                              # 14


def p7_answer():
    return (36 + 4) // 2                             # 20


CIPHER = [14, 9, 14, 5, 20, 5, 5, 14]                # N I N E T E E N


def p8_answer():
    word = "".join(a1z26(n) for n in CIPHER)
    assert word == "NINETEEN"
    return 19


ANS = [p1_answer(), p2_answer(), p3_answer(), p4_answer(), p5_answer(), p6_answer(), p7_answer(), p8_answer()]
assert "".join(a1z26(a) for a in ANS) == PASSWORD, ANS


# ------------------------------------------------------------------ drawing primitives
def tree(d, cx, by, h, col=PINE):
    w = h * 0.7
    for k in range(3):
        top = by - h + k * h * 0.22; base = by - h * 0.25 - (2 - k) * h * 0.18
        ww = w * (0.55 + 0.22 * k)
        d.polygon([(cx, top), (cx - ww / 2, base), (cx + ww / 2, base)], fill=col)
    d.rectangle((cx - h * 0.06, by - h * 0.25, cx + h * 0.06, by), fill=(120, 80, 50))
    star(d, cx, by - h - h * 0.02, h * 0.09, GOLD)


def star(d, cx, cy, r, col=GOLD):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45; a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)


def snowman(d, cx, by, h):
    r1, r2 = h * 0.27, h * 0.19
    d.ellipse((cx - r1, by - 2 * r1, cx + r1, by), fill=(255, 255, 255), outline=NAVY, width=5)
    d.ellipse((cx - r2, by - 2 * r1 - 2 * r2 + 8, cx + r2, by - 2 * r1 + 8), fill=(255, 255, 255), outline=NAVY, width=5)
    hy = by - 2 * r1 - 2 * r2 + 8
    d.rectangle((cx - r2 * 0.7, hy - r2 * 0.9, cx + r2 * 0.7, hy - 4), fill=NAVY)
    d.rectangle((cx - r2 * 1.0, hy - 10, cx + r2 * 1.0, hy + 4), fill=NAVY)
    d.polygon([(cx, hy + r2), (cx + r2 * 0.8, hy + r2 * 1.15), (cx, hy + r2 * 1.3)], fill=(232, 120, 40))


def gift(d, x0, y0, x1, y1, col=RED, rib=GOLD):
    d.rectangle((x0, y0, x1, y1), fill=col)
    cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    d.rectangle((cx - 10, y0, cx + 10, y1), fill=rib); d.rectangle((x0, cy - 10, x1, cy + 10), fill=rib)


def cookie(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(205, 150, 90), outline=(150, 100, 55), width=4)
    for a in (0.5, 2.1, 3.7, 5.0):
        d.ellipse((cx + r * 0.5 * math.cos(a) - 7, cy + r * 0.5 * math.sin(a) - 7,
                   cx + r * 0.5 * math.cos(a) + 7, cy + r * 0.5 * math.sin(a) + 7), fill=(90, 55, 30))


def ctext(d, cx, y, s, f, fill=INK):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


# ------------------------------------------------------------------ page frame
def new(size):
    W, H = size
    im = Image.new("RGB", size, CREAM)
    return im, ImageDraw.Draw(im)


def frame(d, W, H, col=RED):
    m = int(W * 0.035)
    d.rectangle((m, m, W - m, H - m), outline=col, width=10)
    # candy-cane corners
    for x, y in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=CREAM, outline=col, width=8)
        snowflake(d, x, y, 18, GOLD, w=3)


def lock_box(d, W, H, n):
    y = H - int(H * 0.17); x0 = int(W * 0.09); x1 = W - int(W * 0.09)
    d.rounded_rectangle((x0, y, x1, y + int(H * 0.105)), radius=30, fill=NAVY)
    f = font("bold", int(W * 0.022)); d.text((x0 + 50, y + 34), f"LOCK {n}  ·  enter the code", font=f, fill=CREAM)
    bw = int(W * 0.075)
    for k in range(2):
        bx = x0 + 60 + k * (bw + 30); by = y + 100
        d.rounded_rectangle((bx, by, bx + bw, by + bw * 0.9), radius=14, fill=CREAM)
    d.text((x0 + 60 + 2 * (bw + 30) + 30, y + 120), "=", font=font("cinzel", int(W * 0.05)), fill=GOLD)
    lx = x0 + 60 + 2 * (bw + 30) + 140
    d.rounded_rectangle((lx, y + 100, lx + bw, y + 100 + bw * 0.9), radius=14, fill=GOLD)
    d.text((lx + bw + 40, y + 115), "decoder letter\n(A=1 ... Z=26)", font=font("body", int(W * 0.018)), fill=CREAM)


def puzzle_page(size, n, title, story, draw_fn, question):
    im, d = new(size); W, H = size
    frame(d, W, H)
    d.rounded_rectangle((int(W * 0.09), int(H * 0.06), int(W * 0.36), int(H * 0.06) + 90), radius=45, fill=RED)
    ctext(d, int(W * 0.225), int(H * 0.06) + 18, f"PUZZLE {n} of 8", font("bold", 46), CREAM)
    d.text((int(W * 0.09), int(H * 0.06) + 130), title, font=font("cinzel", int(W * 0.052)), fill=NAVY)
    y = draw_par(d, (int(W * 0.09), int(H * 0.06) + 290), story, font("body", int(W * 0.022)), int(W * 0.82))
    area = (int(W * 0.09), y + 40, W - int(W * 0.09), int(H * 0.66))
    draw_fn(d, area, W)
    d.rounded_rectangle((int(W * 0.09), int(H * 0.68), W - int(W * 0.09), int(H * 0.79)), radius=26, fill=SOFTG)
    draw_par(d, (int(W * 0.09) + 40, int(H * 0.68) + 40), question, font("bold", int(W * 0.024)), int(W * 0.74), fill=PINE)
    lock_box(d, W, H, n)
    return im


# ------------------------------------------------------------------ puzzle graphics
def g1(d, a, W):
    x0, y0, x1, y1 = a; seq = ["1", "2", "4", "7", "11", "?"]
    bw = (x1 - x0 - 5 * 30) / 6; cy = (y0 + y1) / 2
    for i, s in enumerate(seq):
        bx = x0 + i * (bw + 30)
        d.rounded_rectangle((bx, cy - bw * 0.6, bx + bw, cy + bw * 0.6), radius=24, fill=(255, 255, 255), outline=RED, width=10)
        for k in range(4):  # candy stripes on top edge
            sx = bx + 20 + k * (bw - 40) / 3
            d.line((sx, cy - bw * 0.6 + 4, sx + 30, cy - bw * 0.6 + 34), fill=RED, width=10)
        ctext(d, bx + bw / 2, cy - 55, s, font("cinzel", 110), RED if s == "?" else NAVY)


def g2(d, a, W):
    x0, y0, x1, y1 = a; cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    jw, jh = 520, 560
    d.rounded_rectangle((cx - jw / 2, cy - jh / 2 + 60, cx + jw / 2, cy + jh / 2), radius=70, outline=NAVY, width=10, fill=(250, 250, 255))
    d.rectangle((cx - jw / 2 + 60, cy - jh / 2, cx + jw / 2 - 60, cy - jh / 2 + 70), fill=RED)
    for i in range(12):
        r, c = divmod(i, 4)
        cookie(d, cx - 180 + c * 120, cy - 60 + r * 120, 48)
    ctext(d, cx, cy - jh / 2 + 8, "COOKIES", font("bold", 40), CREAM)
    # the drawn cookies are decoration only: a big "?" label makes clear the count is unknown
    d.ellipse((cx - 130, cy - 70, cx + 130, cy + 190), fill=(255, 255, 255), outline=RED, width=10)
    ctext(d, cx, cy - 40, "?", font("cinzel", 210), RED)


def scale(d, cx, by, left, right, W):
    d.line((cx, by, cx, by - 330), fill=NAVY, width=12)
    d.line((cx - 330, by - 330, cx + 330, by - 330), fill=NAVY, width=12)
    d.polygon([(cx - 70, by), (cx + 70, by), (cx, by - 50)], fill=NAVY)
    for side, items in ((-1, left), (1, right)):
        px = cx + side * 330
        d.line((px, by - 330, px, by - 190), fill=NAVY, width=5)
        d.arc((px - 170, by - 290, px + 170, by - 150), 0, 180, fill=NAVY, width=10)
        n = len(items); sp = 110
        for k, it in enumerate(items):
            ix = px + (k - (n - 1) / 2) * sp
            if it == "tree": tree(d, ix, by - 205, 180)
            elif it == "snow": snowman(d, ix, by - 205, 190)
            else: star(d, ix, by - 250, 48)


def g3(d, a, W):
    x0, y0, x1, y1 = a; h = y1 - y0
    f = font("bold", 46)
    d.text((x0, y0), "Scale A", font=f, fill=RED); scale(d, (x0 + x1) / 2, y0 + h * 0.48, ["tree"], ["snow", "star", "star"], W)
    d.text((x0, y0 + h * 0.52), "Scale B", font=f, fill=RED); scale(d, (x0 + x1) / 2, y1 - 10, ["snow"], ["star", "star", "star"], W)


def g4(d, a, W):
    x0, y0, x1, y1 = a; s = min(x1 - x0, y1 - y0) * 0.92; gx = (x0 + x1 - s) / 2; gy = y0 + (y1 - y0 - s) / 2
    c = s / 3; f = font("cinzel", int(c * 0.42))
    for r in range(3):
        for k in range(3):
            bx, by = gx + k * c, gy + r * c
            d.ellipse((bx + 18, by + 18, bx + c - 18, by + c - 18), fill=(255, 255, 255), outline=[RED, PINE, GOLD][(r + k) % 3], width=12)
            d.rectangle((bx + c / 2 - 20, by + 4, bx + c / 2 + 20, by + 30), fill=GOLD)
            v = MAGIC[r][k]; s_ = "X" if v is None else str(v)
            ctext(d, bx + c / 2, by + c / 2 - f.size * 0.62, s_, f, RED if v is None else NAVY)


def g5(d, a, W):
    x0, y0, x1, y1 = a; cx = (x0 + x1) / 2
    bw, bh = 330, 190; base_y = y1 - bh - 10
    rows = [["2", "X", "3"], ["", ""], ["15"]]
    cols = [RED, PINE, GOLD]
    for r, row in enumerate(rows):
        n = len(row); y = base_y - r * (bh + 20)
        for k, s in enumerate(row):
            bx = cx + (k - (n - 1) / 2) * (bw + 20) - bw / 2
            gift(d, bx, y, bx + bw, y + bh, cols[(r + k) % 3], CREAM if cols[(r + k) % 3] == GOLD else GOLD)
            if s:
                d.rounded_rectangle((bx + bw / 2 - 90, y + bh / 2 - 60, bx + bw / 2 + 90, y + bh / 2 + 60), radius=20, fill=(255, 255, 255))
                ctext(d, bx + bw / 2, y + bh / 2 - 52, s, font("cinzel", 90), RED if s == "X" else NAVY)


POS = {"North Pole": (0.10, 0.50), "Pine Hill": (0.38, 0.18), "Ice Lake": (0.38, 0.84),
       "Snow Fort": (0.62, 0.50), "Town": (0.90, 0.50)}


def g6(d, a, W):
    x0, y0, x1, y1 = a
    P = {k: (x0 + v[0] * (x1 - x0), y0 + v[1] * (y1 - y0)) for k, v in POS.items()}
    for (u, v), w in EDGES.items():
        (ax, ay), (bx, by) = P[u], P[v]
        d.line((ax, ay, bx, by), fill=SUB, width=8)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        d.ellipse((mx - 46, my - 46, mx + 46, my + 46), fill=GOLD)
        ctext(d, mx, my - 34, str(w), font("bold", 54), NAVY)
    for k, (px, py) in P.items():
        col = RED if k in ("North Pole", "Town") else PINE
        d.ellipse((px - 62, py - 62, px + 62, py + 62), fill=col, outline=CREAM, width=8)
        snowflake(d, px, py, 32, CREAM, w=4)
        ctext(d, px, py + 72, k, font("bold", 40), NAVY)


def g7(d, a, W):
    x0, y0, x1, y1 = a
    for i, (name, col) in enumerate((("Jingle", RED), ("Jangle", PINE))):
        cx = x0 + (x1 - x0) * (0.3 + 0.4 * i); by = y1 - 80
        d.ellipse((cx - 150, by - 420, cx + 150, by - 120), fill=(250, 214, 180), outline=NAVY, width=6)
        d.polygon([(cx - 170, by - 360), (cx + 170, by - 360), (cx + 60, by - 640)], fill=col)
        d.ellipse((cx + 30, by - 680, cx + 100, by - 610), fill=(255, 255, 255))
        for ex in (-55, 55):
            d.ellipse((cx + ex - 16, by - 290, cx + ex + 16, by - 258), fill=NAVY)
        d.arc((cx - 60, by - 250, cx + 60, by - 170), 20, 160, fill=NAVY, width=8)
        d.rounded_rectangle((cx - 170, by - 110, cx + 170, by), radius=24, fill=col)
        ctext(d, cx, by - 92, name, font("bold", 56), CREAM)


def g8(d, a, W):
    x0, y0, x1, y1 = a; n = len(CIPHER); bw = (x1 - x0 - (n - 1) * 20) / n; cy = (y0 + y1) / 2 - 120
    for i, v in enumerate(CIPHER):
        bx = x0 + i * (bw + 20)
        d.rounded_rectangle((bx, cy - bw * 0.7, bx + bw, cy + bw * 0.7), radius=20, fill=NAVY)
        ctext(d, bx + bw / 2, cy - 60, str(v), font("cinzel", 96), GOLD)
        d.rounded_rectangle((bx + 10, cy + bw * 0.8, bx + bw - 10, cy + bw * 0.8 + bw * 0.9), radius=12, outline=NAVY, width=6, fill=(255, 255, 255))
    decoder_strip(d, x0, y1 - 210, x1)


def decoder_strip(d, x0, y, x1):
    n = 26; w = (x1 - x0) / 13
    for i in range(n):
        r, c = divmod(i, 13)
        bx, by = x0 + c * w, y + r * 105
        d.rectangle((bx, by, bx + w, by + 100), outline=SUB, width=3, fill=(255, 255, 255))
        ctext(d, bx + w / 2, by + 6, chr(65 + i), font("bold", 42), RED)
        ctext(d, bx + w / 2, by + 54, str(i + 1), font("body", 36), NAVY)


PUZZLES = [
    ("Candy Cane Code",
     "The candy-cane machine prints a secret number pattern on every cane. The last cane came out blank!",
     g1, "Look at how the numbers grow. What number belongs on the last candy cane?"),
    ("Mrs. Claus's Cookie Jar",
     "Mrs. Claus baked fewer than 30 cookies. Shared equally between 3 elves, none are left over. Between 4 elves, 2 are "
     "left over. Between 5 elves, 3 are left over.",
     g2, "How many cookies are in the jar?"),
    ("The Toy Scales",
     "The elves weigh decorations on the workshop scales. Both scales below are perfectly balanced.",
     g3, "How many stars would balance ONE Christmas tree?"),
    ("The Magic Ornaments",
     "In this magic square of ornaments, every row, every column and both diagonals add up to the SAME total.",
     g4, "What number is hidden on ornament X?"),
    ("The Gift Pyramid",
     "Each gift in the pyramid shows the SUM of the two gifts directly underneath it. The bottom row has one gift we can't read.",
     g5, "Which number is on gift X?"),
    ("Santa's Sleigh Route",
     "Santa must fly from the North Pole to Town before midnight. The numbers show how many minutes each path takes.",
     g6, "What is the SHORTEST possible trip, in minutes?"),
    ("Jingle & Jangle",
     "Elf Jingle is 4 years older than Elf Jangle. Together, their ages add up to 36.",
     g7, "How old is Jingle?"),
    ("The Frozen Message",
     "A message froze on the workshop screen as numbers. Use the decoder (A=1, B=2 ... Z=26) to turn each number into a letter.",
     g8, "The message spells a NUMBER. What is it? (write it as digits)"),
]

HINTS = ["The gaps between the numbers grow by 1 each time: +1, +2, +3 ...",
         "List the numbers under 30 that 3 divides exactly. Then test the other two rules.",
         "In Scale A, swap the snowman for the 3 stars from Scale B.",
         "The top row is complete: add it up to find the magic total.",
         "Write the middle gifts as 2+X and X+3. Add them to get the top gift.",
         "Add up the minutes along each possible path. Pick the smallest total.",
         "If they were the same age, together they'd be 36 − 4 = 32.",
         "N is 14, I is 9 ... read the whole word!"]

EXPLAIN = ["Differences 1, 2, 3, 4, so the next one is +5: 11 + 5 = 16.",
           "Multiples of 3 below 30 that leave 3 when divided by 5: 3 and 18. Only 18 leaves 2 when divided by 4.",
           "Snowman = 3 stars, so tree = 3 + 2 = 5 stars.",
           "Top row: 12 + 17 + 16 = 45. Middle row: X + 15 + 11 = 45, so X = 19.",
           "Middle gifts 2+X and X+3 add up to 2X + 5 = 15, so X = 5.",
           "Fastest trips all take 14 minutes (e.g. North Pole - Pine Hill - Town, 5 + 9).",
           "36 − 4 = 32, 32 ÷ 2 = 16 for Jangle, so Jingle is 16 + 4 = 20.",
           "14-9-14-5-20-5-5-14 spells NINETEEN, so the code is 19."]


# ------------------------------------------------------------------ other pages
def cover(size):
    im, d = new(size); W, H = size
    d.rectangle((0, 0, W, H), fill=NAVY)
    import random
    rnd = random.Random(5)
    for _ in range(70):
        snowflake(d, rnd.randint(0, W), rnd.randint(0, H), rnd.choice((10, 16, 24)), (60, 76, 110), w=3)
    # vault door
    cx, cy, R = W / 2, H * 0.36, W * 0.24
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(196, 160, 82), outline=(120, 92, 40), width=18)
    d.ellipse((cx - R * 0.72, cy - R * 0.72, cx + R * 0.72, cy + R * 0.72), outline=(120, 92, 40), width=12)
    for k in range(8):
        a = k * math.pi / 4
        d.line((cx, cy, cx + R * 0.6 * math.cos(a), cy + R * 0.6 * math.sin(a)), fill=(120, 92, 40), width=16)
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=RED)
    snowflake(d, cx, cy, 46, CREAM, w=6)
    ctext(d, W / 2, H * 0.60, "CHRISTMAS", font("cinzel", int(W * 0.08)), CREAM)
    ctext(d, W / 2, H * 0.60 + W * 0.095, "ESCAPE ROOM", font("cinzel", int(W * 0.08)), GOLD)
    ctext(d, W / 2, H * 0.60 + W * 0.21, "The Great Workshop Lockdown", font("semi", int(W * 0.036)), CREAM)
    ctext(d, W / 2, H * 0.83, "8 math & logic puzzles  ·  ages 8-13  ·  45-60 minutes", font("body", int(W * 0.024)), (210, 216, 230))
    ctext(d, W / 2, H * 0.92, "MathRelaxing", font("cinzel_r", int(W * 0.024)), (210, 216, 230))
    return im


def text_page(size, title, blocks, col=NAVY):
    im, d = new(size); W, H = size
    frame(d, W, H, PINE)
    d.text((int(W * 0.09), int(H * 0.07)), title, font=font("cinzel", int(W * 0.05)), fill=col)
    y = int(H * 0.07) + int(W * 0.09)
    for head, body in blocks:
        if head:
            d.text((int(W * 0.09), y), head, font=font("bold", int(W * 0.028)), fill=RED); y += int(W * 0.045)
        y = draw_par(d, (int(W * 0.09), y), body, font("body", int(W * 0.022)), int(W * 0.82)) + int(W * 0.03)
    return im


def host_guide(size):
    return text_page(size, "Host Guide", [
        ("What you need", "Printer, pencils, scissors (for the hint cards) and a timer. Optional: an envelope or "
                          "box with a small treat to be 'the vault'."),
        ("Before the game", "Print the mission briefing, the 8 puzzles and the vault page. Cut out the hint cards and keep "
                            "them (and the answer key!) with you. Hide each puzzle somewhere around the room, or hand them "
                            "out one at a time."),
        ("How it works", "Each puzzle opens a lock with a number from 1 to 26. Players turn that number into a letter with the "
                         "Workshop Decoder (A=1, B=2 ... Z=26). The 8 letters spell the password that opens the vault. If "
                         "the letters make a real word, they got everything right!"),
        ("Players & time", "1 to 6 players, ages 8-13 (younger children can play with a grown-up). Allow 45-60 minutes."),
        ("Hints", "Give a hint card when a team is stuck for about 5 minutes. For a challenge, each hint costs 2 minutes."),
    ])


def briefing(size):
    im = text_page(size, "Mission Briefing", [
        ("", "TOP SECRET — for Elf Engineers in training only."),
        ("Christmas Eve, 11:00 pm", "Disaster! The Snow-Lock computer in Santa's workshop has frozen and locked the toy vault "
                                    "— with ALL the presents inside. Santa leaves in one hour."),
        ("Your mission", "Solve the 8 puzzles hidden around the workshop. Each one gives you a code. Turn every code into a "
                         "letter with the Workshop Decoder, then type the secret password into the vault to unlock it."),
        ("Rules", "Work as a team. Write your answers in the lock boxes. You can ask for a hint, but every elf knows the best "
                  "engineers try first!"),
    ], RED)
    d = ImageDraw.Draw(im); W, H = size
    d.rounded_rectangle((int(W * 0.25), int(H * 0.80), int(W * 0.75), int(H * 0.90)), radius=40, fill=NAVY)
    ctext(d, W / 2, int(H * 0.815), "START TIME  __ : __", font("bold", int(W * 0.03)), CREAM)
    return im


def vault(size):
    im, d = new(size); W, H = size
    frame(d, W, H, GOLD)
    ctext(d, W / 2, int(H * 0.06), "THE VAULT", font("cinzel", int(W * 0.07)), NAVY)
    ctext(d, W / 2, int(H * 0.06) + int(W * 0.1), "Turn each code into a letter to find the password", font("semi", int(W * 0.024)), RED)
    x0, x1 = int(W * 0.09), W - int(W * 0.09)
    decoder_strip(d, x0, int(H * 0.17), x1)
    bw = (x1 - x0 - 7 * 24) / 8; y = int(H * 0.30)
    for i in range(8):
        bx = x0 + i * (bw + 24)
        ctext(d, bx + bw / 2, y, f"Lock {i + 1}", font("bold", 36), SUB)
        d.rounded_rectangle((bx, y + 60, bx + bw, y + 60 + bw * 0.8), radius=16, outline=NAVY, width=6, fill=(255, 255, 255))
        ctext(d, bx + bw / 2, y + 60 + bw * 0.85, "code", font("body", 30), SUB)
        d.rounded_rectangle((bx, y + 120 + bw * 0.9, bx + bw, y + 120 + bw * 1.9), radius=16, fill=GOLD)
        ctext(d, bx + bw / 2, y + 125 + bw * 1.9, "letter", font("body", 30), SUB)
    # vault door
    cx, cy, R = W / 2, int(H * 0.66), int(W * 0.2)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(196, 160, 82), outline=(120, 92, 40), width=14)
    for k in range(8):
        a = k * math.pi / 4
        d.line((cx, cy, cx + R * 0.6 * math.cos(a), cy + R * 0.6 * math.sin(a)), fill=(120, 92, 40), width=12)
    d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), fill=RED)
    d.rounded_rectangle((int(W * 0.15), int(H * 0.83), W - int(W * 0.15), int(H * 0.92)), radius=30, fill=NAVY)
    ctext(d, W / 2, int(H * 0.845), "PASSWORD:  _  _  _  _  _  _  _  _", font("bold", int(W * 0.036)), CREAM)
    return im


def hints_page(size):
    im, d = new(size); W, H = size
    d.text((int(W * 0.06), int(H * 0.03)), "Hint Cards  ·  cut along the dotted lines", font=font("bold", int(W * 0.026)), fill=NAVY)
    mx, my = int(W * 0.05), int(H * 0.07)
    cw, ch = (W - 2 * mx) / 2, (H - my - int(H * 0.03)) / 4
    for i, h in enumerate(HINTS):
        r, c = divmod(i, 2)
        x0, y0 = mx + c * cw, my + r * ch
        for x in range(int(x0), int(x0 + cw), 26):
            d.line((x, y0, x + 12, y0), fill=SUB, width=2); d.line((x, y0 + ch, x + 12, y0 + ch), fill=SUB, width=2)
        for y in range(int(y0), int(y0 + ch), 26):
            d.line((x0, y, x0, y + 12), fill=SUB, width=2); d.line((x0 + cw, y, x0 + cw, y + 12), fill=SUB, width=2)
        d.rounded_rectangle((x0 + 30, y0 + 30, x0 + cw - 30, y0 + ch - 30), radius=24, fill=SOFTR)
        d.text((x0 + 70, y0 + 60), f"HINT · PUZZLE {i + 1}", font=font("bold", 44), fill=RED)
        draw_par(d, (x0 + 70, y0 + 140), h, font("body", 44), cw - 140)
    return im


def answer_key(size):
    im, d = new(size); W, H = size
    frame(d, W, H, NAVY)
    d.text((int(W * 0.09), int(H * 0.06)), "Answer Key (for the host)", font=font("cinzel", int(W * 0.042)), fill=NAVY)
    y = int(H * 0.06) + int(W * 0.085)
    for i, (t, e) in enumerate(zip(PUZZLES, EXPLAIN)):
        a = ANS[i]
        d.ellipse((int(W * 0.09), y, int(W * 0.09) + 90, y + 90), fill=RED)
        ctext(d, int(W * 0.09) + 45, y + 18, str(i + 1), font("bold", 46), CREAM)
        d.text((int(W * 0.09) + 120, y + 4), f"{t[0]}  —  code {a} = {a1z26(a)}", font=font("bold", int(W * 0.022)), fill=NAVY)
        y = draw_par(d, (int(W * 0.09) + 120, y + 70), e, font("body", int(W * 0.019)), int(W * 0.7)) + 40
    d.rounded_rectangle((int(W * 0.09), y + 10, W - int(W * 0.09), y + 150), radius=30, fill=NAVY)
    ctext(d, W / 2, y + 50, f"Vault password:  {PASSWORD}", font("bold", int(W * 0.034)), GOLD)
    return im


def certificate(size):
    im, d = new(size); W, H = size
    frame(d, W, H, GOLD)
    d.rectangle((int(W * 0.08), int(H * 0.08), W - int(W * 0.08), H - int(H * 0.08)), outline=RED, width=4)
    ctext(d, W / 2, int(H * 0.16), "CERTIFICATE", font("cinzel", int(W * 0.075)), NAVY)
    ctext(d, W / 2, int(H * 0.16) + int(W * 0.1), "of Official Elf Engineering", font("semi", int(W * 0.032)), RED)
    snowflake(d, W / 2, int(H * 0.40), int(W * 0.1), GOLD, w=10)
    ctext(d, W / 2, int(H * 0.52), "This certifies that", font("body", int(W * 0.026)), SUB)
    d.line((int(W * 0.2), int(H * 0.60), W - int(W * 0.2), int(H * 0.60)), fill=NAVY, width=4)
    ctext(d, W / 2, int(H * 0.63), "cracked the Snow-Lock, opened the toy vault", font("body", int(W * 0.026)), INK)
    ctext(d, W / 2, int(H * 0.63) + int(W * 0.045), "and saved Christmas!", font("body", int(W * 0.026)), INK)
    ctext(d, W / 2, int(H * 0.76), "Escape time:  ____ minutes", font("bold", int(W * 0.028)), NAVY)
    ctext(d, W / 2, int(H * 0.84), "Signed, Santa's Workshop", font("cinzel_r", int(W * 0.026)), RED)
    return im


def terms(size):
    return text_page(size, "Terms of Use", [
        ("", "For personal, family and single-classroom use. Print as many copies as your own household, party or class "
             "needs.\n\nPlease do not resell, share the file, or post it anywhere the public can download it.\n\n"
             "Every puzzle and illustration is original work by MathRelaxing, and every answer was checked. If you ever "
             "spot a problem, send a message through the shop and a corrected file will be sent free.\n\nMerry Christmas "
             "— and happy escaping!"),
    ])


def build(name, inches):
    size = (int(inches[0] * DPI), int(inches[1] * DPI))
    pages = [cover(size), host_guide(size), briefing(size)]
    pages += [puzzle_page(size, i + 1, *p) for i, p in enumerate(PUZZLES)]
    pages += [vault(size), hints_page(size), answer_key(size), certificate(size), terms(size)]
    tmp = os.path.join(OUT, f"_{name}"); os.makedirs(tmp, exist_ok=True)
    paths = []
    for k, im in enumerate(pages):
        p = os.path.join(tmp, f"p{k:02d}.jpg"); im.save(p, quality=92, dpi=(DPI, DPI)); paths.append(p)
    pdf = os.path.join(OUT, f"Christmas_Escape_Room_{name}.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print(f"{name}: {len(pages)} pages, {os.path.getsize(pdf)//1024} KB  answers={ANS} -> {PASSWORD}")


if __name__ == "__main__":
    build("Letter", (8.5, 11))
    build("A4", (8.27, 11.69))
