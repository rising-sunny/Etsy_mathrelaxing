"""
Math Christmas Cards — 12 printable 5 x 7 in folding cards, each with a math pun and
generative art from real mathematics. The back of every card explains its math.

Outputs (out/):
  Math_Christmas_Cards_Letter.pdf / _A4.pdf  (2 pages per card: outside + inside,
                                               print double-sided, flip on short edge)
  fronts/NN_name.png                          (1500 x 2100 px fronts to send digitally)

  python generate_cards.py
"""
import os, sys, math, random, itertools
from PIL import Image, ImageDraw, ImageFilter
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem")); sys.path.insert(0, os.path.join(REPO, "logic_book_xmas"))
from generate_advent import font, wrap, CREAM, NAVY, RED, PINE, GOLD, INK, SUB
from render_book import FONTS, FOBJ

OUT = os.path.join(HERE, "out"); FR = os.path.join(OUT, "fronts")
os.makedirs(FR, exist_ok=True)
W, H = 1500, 2100           # 5 x 7 in at 300 dpi
SS = 2                      # supersampling
NIGHT = (22, 32, 58); CHALK = (40, 62, 52); ICE = (214, 232, 245); BROWN = (120, 82, 52)
LEAF = [(33, 92, 72), (52, 128, 92), (78, 150, 104), (28, 76, 60)]


def canvas(bg):
    im = Image.new("RGB", (W * SS, H * SS), bg)
    return im, ImageDraw.Draw(im)


def finish(im):
    return im.resize((W, H), Image.LANCZOS)


def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def F(kind, px):
    return font(kind, int(px * SS))


def title(d, lines, y, color, sizes, kinds=None, gap=1.12):
    kinds = kinds or ["cinzel"] * len(lines)
    for s, sz, k in zip(lines, sizes, kinds):
        f = F(k, sz); ctext(d, W * SS / 2, y * SS, s, f, color); y += sz * gap
    return y


def star(d, cx, cy, r, col, k=5):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / k),
            cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / k)) for i in range(2 * k)]
    d.polygon(pts, fill=col)


def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


# ------------------------------------------------------------------ 1 fractal tree
def c_tree():
    im, d = canvas(CREAM); rnd = random.Random(4)
    tips = []
    def br(x, y, ang, L, depth):
        if depth == 0:
            tips.append((x, y)); return
        x2, y2 = x + L * math.cos(ang), y - L * math.sin(ang)
        t = 1 - depth / 11
        d.line((x, y, x2, y2), fill=lerp(BROWN, PINE, min(1, t * 1.6)), width=max(2, int(depth ** 1.55 * SS * 0.9)))
        for s in (-1, 1):
            br(x2, y2, ang + s * math.radians(27 + rnd.uniform(-4, 4)), L * rnd.uniform(0.72, 0.78), depth - 1)
    br(W * SS / 2, 1480 * SS, math.pi / 2, 250 * SS, 11)
    for x, y in rnd.sample(tips, 90):
        r = rnd.choice((9, 11, 13)) * SS
        d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice([RED, GOLD, RED, (210, 70, 70)]))
    title(d, ["Have a", "Tree-mendous", "Christmas"], 1560, PINE, [70, 118, 92])
    return finish(im)


# ------------------------------------------------------------------ 2 Koch snowflake
def koch_pts(cx, cy, R, n):
    pts = [(cx + R * math.cos(math.radians(90 + 120 * k)), cy - R * math.sin(math.radians(90 + 120 * k))) for k in range(3)]
    for _ in range(n):
        new = []
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            dx, dy = (x2 - x1) / 3, (y2 - y1) / 3
            a = (x1 + dx, y1 + dy); b = (x1 + 2 * dx, y1 + 2 * dy)
            ang = math.pi / 3
            px = a[0] + dx * math.cos(ang) - dy * math.sin(ang); py = a[1] + dx * math.sin(ang) + dy * math.cos(ang)
            new += [(x1, y1), a, (px, py), b]
        pts = new
    return pts


def c_koch():
    im, d = canvas(NIGHT); rnd = random.Random(7)
    for _ in range(26):
        x, y, r = rnd.uniform(0, W * SS), rnd.uniform(0, H * SS * 0.95), rnd.uniform(18, 60) * SS
        q = koch_pts(x, y, r, 3); d.line(q + [q[0]], fill=(70, 90, 130), width=2 * SS)
    big = koch_pts(W * SS / 2, 900 * SS, 560 * SS, 5)
    d.polygon(big, fill=(40, 60, 100))
    d.line(big + [big[0]], fill=ICE, width=6 * SS)
    title(d, ["Let It Snow,", "Recursively"], 1600, GOLD, [104, 104])
    return finish(im)


# ------------------------------------------------------------------ 3 pi pine tree
def pi_digits(n):
    def arctan_inv(x, unity):
        s = t = unity // x; x2 = x * x; k = 1; sign = -1
        while t:
            t //= x2; k += 2; s += sign * (t // k); sign = -sign
        return s
    unity = 10 ** (n + 10)
    p = 4 * (4 * arctan_inv(5, unity) - arctan_inv(239, unity))
    return str(p)[:n]


def c_pi():
    im, d = canvas(CREAM); rnd = random.Random(3)
    digits = pi_digits(1400); k = 0
    f = F("bold", 30); cw = 30 * SS * 0.72; lh = 30 * SS * 1.02
    top, bot = 230 * SS, 1430 * SS; cx = W * SS / 2
    y = top
    while y < bot:
        half = (y - top) / (bot - top) * 560 * SS + 20 * SS
        n = max(1, int(2 * half / cw))
        x = cx - n * cw / 2
        for j in range(n):
            ch = digits[k % len(digits)]; k += 1
            col = rnd.choice([RED, GOLD]) if rnd.random() < 0.09 else rnd.choice(LEAF)
            d.text((x + j * cw, y), ch, font=f, fill=col)
        y += lh
    for yy in range(int(y), int(y + 150 * SS), int(lh)):
        for j in range(4):
            d.text((cx - 2 * cw + j * cw, yy), digits[k % len(digits)], font=f, fill=BROWN); k += 1
    star(d, cx, top - 70 * SS, 70 * SS, GOLD)
    title(d, ["O Pi-ne Tree"], 1660, PINE, [128])
    ctext(d, cx, 1820 * SS, "Merry Christmas", F("semi", 58), RED)
    return finish(im)


# ------------------------------------------------------------------ 4 Fibonacci wreath
def c_fib():
    im, d = canvas(CREAM); rnd = random.Random(9)
    cx, cy = W * SS / 2, 820 * SS; ga = math.pi * (3 - 5 ** 0.5)
    for i in range(1, 2400):
        r = 15.5 * SS * math.sqrt(i)
        if r < 330 * SS or r > 640 * SS:
            continue
        a = i * ga; x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        rr = (7 + 9 * (1 - abs(r - 485 * SS) / (155 * SS))) * SS
        col = RED if i % 13 == 0 else GOLD if i % 21 == 0 else LEAF[i % 4]
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    # bow
    bx, by = cx, cy + 590 * SS
    d.polygon([(bx, by), (bx - 150 * SS, by - 80 * SS), (bx - 150 * SS, by + 80 * SS)], fill=RED)
    d.polygon([(bx, by), (bx + 150 * SS, by - 80 * SS), (bx + 150 * SS, by + 80 * SS)], fill=RED)
    d.polygon([(bx - 20 * SS, by), (bx - 90 * SS, by + 220 * SS), (bx - 40 * SS, by + 200 * SS)], fill=(150, 30, 44))
    d.polygon([(bx + 20 * SS, by), (bx + 90 * SS, by + 220 * SS), (bx + 40 * SS, by + 200 * SS)], fill=(150, 30, 44))
    d.ellipse((bx - 34 * SS, by - 34 * SS, bx + 34 * SS, by + 34 * SS), fill=(150, 30, 44))
    title(d, ["Have a", "Golden Holiday"], 1720, PINE, [74, 112])
    return finish(im)


# ------------------------------------------------------------------ 5 Sierpinski tree
def c_sier():
    im, d = canvas(CREAM)
    def tri(a, b, c, n):
        if n == 0:
            d.polygon([a, b, c], fill=LEAF[(int(a[0]) // 7 + int(a[1]) // 11) % 4]); return
        ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2); ca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
        tri(a, ab, ca, n - 1); tri(ab, b, bc, n - 1); tri(ca, bc, c, n - 1)
    cx = W * SS / 2
    A, B, C = (cx, 260 * SS), (cx - 620 * SS, 1330 * SS), (cx + 620 * SS, 1330 * SS)
    tri(A, B, C, 6)
    d.rectangle((cx - 70 * SS, 1330 * SS, cx + 70 * SS, 1460 * SS), fill=BROWN)
    star(d, cx, 220 * SS, 80 * SS, GOLD)
    # a few ornaments in the holes
    rnd = random.Random(2)
    for _ in range(14):
        t = rnd.uniform(0.15, 0.95); u = rnd.uniform(-0.45, 0.45) * t
        x = cx + u * 1240 * SS; y = 260 * SS + t * 1070 * SS
        d.ellipse((x - 14 * SS, y - 14 * SS, x + 14 * SS, y + 14 * SS), fill=rnd.choice([RED, GOLD]))
    title(d, ["Merry Christmas"], 1600, PINE, [118])
    ctext(d, cx, 1770 * SS, "holiday cheer at every scale", F("semi", 52), RED)
    return finish(im)


# ------------------------------------------------------------------ 6 solve for X-mas
def c_xmas():
    im, d = canvas(CHALK); rnd = random.Random(5)
    ch = (236, 240, 232)
    for _ in range(2500):  # chalk dust
        x, y = rnd.uniform(0, W * SS), rnd.uniform(0, H * SS)
        d.point((x, y), fill=(60, 84, 72))
    d.rectangle((40 * SS, 40 * SS, W * SS - 40 * SS, H * SS - 40 * SS), outline=(150, 112, 70), width=28 * SS)
    cx, oy = W * SS / 2, 1180 * SS
    # axes
    d.line((180 * SS, oy, W * SS - 180 * SS, oy), fill=ch, width=5 * SS)
    d.line((cx, oy + 160 * SS, cx, 230 * SS), fill=ch, width=5 * SS)
    for t in range(-5, 6):
        x = cx + t * 110 * SS; d.line((x, oy - 12 * SS, x, oy + 12 * SS), fill=ch, width=4 * SS)
    # tree region  y <= 8 - 1.6|x| for |x| <= 5, stepped, plus trunk
    pts = []
    for i in range(-50, 51):
        x = i / 10; y = max(0, 8 - 1.6 * abs(x)); pts.append((cx + x * 110 * SS, oy - y * 110 * SS))
    d.polygon(pts, fill=(64, 120, 86))
    d.line(pts, fill=ch, width=6 * SS)
    d.rectangle((cx - 40 * SS, oy, cx + 40 * SS, oy + 110 * SS), fill=BROWN)
    star(d, cx, oy - 8 * 110 * SS, 55 * SS, GOLD)
    d.text((cx + 260 * SS, 420 * SS), "y ≤ 8 - 1.6|x|".replace("≤", "<"), font=F("semi", 48), fill=ch)
    title(d, ["Merry X-mas"], 1430, ch, [132])
    ctext(d, cx, 1610 * SS, "(solve for x)", F("semi", 64), (240, 214, 140))
    return finish(im)


# ------------------------------------------------------------------ 7 twelve days = 364 gifts
def c_364():
    im, d = canvas(CREAM); rnd = random.Random(12)
    cx = W * SS / 2; s = 76 * SS; top = 330 * SS
    cols = [RED, PINE, GOLD, NAVY]
    for r in range(12):
        n = r + 1; y = top + r * (s + 8 * SS)
        for j in range(n):
            x = cx - n * (s + 8 * SS) / 2 + j * (s + 8 * SS)
            col = cols[(r + j) % 4]
            d.rectangle((x, y, x + s, y + s), fill=col)
            d.rectangle((x + s / 2 - 6 * SS, y, x + s / 2 + 6 * SS, y + s), fill=CREAM if col != GOLD else RED)
            d.rectangle((x, y + s / 2 - 6 * SS, x + s, y + s / 2 + 6 * SS), fill=CREAM if col != GOLD else RED)
    ctext(d, cx, 140 * SS, "THE 12 DAYS OF CHRISTMAS", F("cinzel", 66), PINE)
    title(d, ["364 gifts"], 1420, RED, [150])
    ctext(d, cx, 1620 * SS, "1 + 3 + 6 + 10 + ... + 78 = 364", F("semi", 54), PINE)
    ctext(d, cx, 1720 * SS, "Merry Christmas", F("cinzel", 76), PINE)
    return finish(im)


# ------------------------------------------------------------------ 8 Santa's route (TSP)
def tour_len(P, t):
    return sum(math.dist(P[t[i]], P[t[(i + 1) % len(t)]]) for i in range(len(t)))


def two_opt(P, t):
    improved = True
    while improved:
        improved = False
        for i in range(1, len(t) - 1):
            for j in range(i + 1, len(t)):
                a, b, c_, d_ = P[t[i - 1]], P[t[i]], P[t[j]], P[t[(j + 1) % len(t)]]
                if math.dist(a, c_) + math.dist(b, d_) < math.dist(a, b) + math.dist(c_, d_) - 1e-9:
                    t[i:j + 1] = reversed(t[i:j + 1]); improved = True
    return t


def c_tsp():
    im, d = canvas(NIGHT); rnd = random.Random(21)
    for _ in range(300):
        x, y = rnd.uniform(0, W * SS), rnd.uniform(0, H * SS); r = rnd.choice((2, 3, 4)) * SS
        d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 140, 180))
    P = [(rnd.uniform(200, 1300) * SS, rnd.uniform(250, 1300) * SS) for _ in range(28)]
    t = list(range(len(P)))  # nearest neighbour then 2-opt
    cur = 0; left = set(t[1:]); tour = [0]
    while left:
        nxt = min(left, key=lambda j: math.dist(P[cur], P[j])); tour.append(nxt); left.remove(nxt); cur = nxt
    tour = two_opt(P, tour)
    pts = [P[i] for i in tour] + [P[tour[0]]]
    for i in range(len(pts) - 1):  # dashed gold route
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]; L = math.dist(pts[i], pts[i + 1]); n = int(L / (26 * SS))
        for k in range(0, n, 2):
            a, b = k / n, min(1, (k + 1) / n)
            d.line((x1 + (x2 - x1) * a, y1 + (y2 - y1) * a, x1 + (x2 - x1) * b, y1 + (y2 - y1) * b), fill=GOLD, width=7 * SS)
    for i, (x, y) in enumerate(P):  # houses
        s = 26 * SS
        d.rectangle((x - s, y - s * 0.4, x + s, y + s), fill=(236, 224, 200))
        d.polygon([(x - s * 1.25, y - s * 0.35), (x, y - s * 1.35), (x + s * 1.25, y - s * 0.35)], fill=RED)
        d.rectangle((x - s * 0.3, y + s * 0.15, x + s * 0.3, y + s * 0.65), fill=(255, 210, 110))
    x, y = P[tour[0]]
    star(d, x, y - 80 * SS, 44 * SS, GOLD)
    title(d, ["The Shortest Path", "to Christmas"], 1500, CREAM, [100, 100])
    ctext(d, W * SS / 2, 1760 * SS, "Santa vs. the Traveling Salesman Problem", F("semi", 50), GOLD)
    return finish(im)


# ------------------------------------------------------------------ 9 Lissajous ornaments
def c_liss():
    im, d = canvas(CREAM)
    specs = [(330, 640, 230, 3, 2, RED), (750, 860, 290, 5, 4, PINE), (1170, 560, 210, 3, 4, GOLD)]
    for x, y, r, a, b, col in specs:
        d.line((x * SS, 0, x * SS, (y - r - 40) * SS), fill=SUB, width=4 * SS)
    for x, y, r, a, b, col in specs:
        X, Y, R = x * SS, y * SS, r * SS
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=(255, 255, 255), outline=col, width=10 * SS)
        d.rectangle((X - 34 * SS, Y - R - 50 * SS, X + 34 * SS, Y - R + 6 * SS), fill=GOLD)
        pts = [(X + R * 0.8 * math.sin(a * t + math.pi / 2), Y + R * 0.8 * math.sin(b * t)) for t in
               [k * 2 * math.pi / 1600 for k in range(1601)]]
        d.line(pts, fill=col, width=7 * SS, joint="curve")
    title(d, ["Have a", "Well-Rounded", "Christmas"], 1340, NAVY, [74, 120, 96])
    return finish(im)


# ------------------------------------------------------------------ 10 six-fold snowflakes
def flake(d, cx, cy, R, rnd, col, w):
    arms = []
    def branch(x, y, ang, L, depth):
        x2, y2 = x + L * math.cos(ang), y + L * math.sin(ang); arms.append(((x, y), (x2, y2)))
        if depth:
            for t in (0.4, 0.7):
                bx, by = x + (x2 - x) * t, y + (y2 - y) * t
                for s in (-1, 1):
                    branch(bx, by, ang + s * math.pi / 3, L * rnd.uniform(0.25, 0.42), depth - 1)
    branch(0, 0, 0, R, 2)
    for k in range(6):
        a = k * math.pi / 3; ca, sa = math.cos(a), math.sin(a)
        for (x1, y1), (x2, y2) in arms:
            d.line((cx + x1 * ca - y1 * sa, cy + x1 * sa + y1 * ca, cx + x2 * ca - y2 * sa, cy + x2 * sa + y2 * ca), fill=col, width=w)


def c_flakes():
    im, d = canvas(NIGHT); rnd = random.Random(31)
    for x, y, r in ((750, 760, 470), (290, 300, 160), (1230, 330, 150), (250, 1250, 130), (1260, 1230, 170), (760, 1420, 90)):
        flake(d, x * SS, y * SS, r * SS, random.Random(rnd.random()), ICE if r > 300 else (170, 196, 230), max(4, int(r / 40)) * SS)
    title(d, ["No Two Alike"], 1580, GOLD, [122])
    ctext(d, W * SS / 2, 1760 * SS, "Happy Holidays", F("semi", 62), CREAM)
    return finish(im)


# ------------------------------------------------------------------ 11 JOY in binary lights
def c_binary():
    im, d = canvas((18, 24, 40))
    bits = ["01001010", "01001111", "01011001"]
    colors = [(255, 90, 90), (255, 200, 80), (110, 220, 140), (120, 180, 255)]
    glow = Image.new("RGB", im.size, (0, 0, 0)); g = ImageDraw.Draw(glow)
    for r, byte in enumerate(bits):
        y0 = (380 + r * 420) * SS
        wire = [(x * SS, y0 + 60 * SS * math.sin(x / 1500 * math.pi * 2 + r)) for x in range(80, 1430, 10)]
        d.line(wire, fill=(70, 90, 70), width=6 * SS)
        for j, bit in enumerate(byte):
            x = (200 + j * 158) * SS; y = y0 + 60 * SS * math.sin(x / SS / 1500 * math.pi * 2 + r)
            d.rectangle((x - 16 * SS, y - 6 * SS, x + 16 * SS, y + 26 * SS), fill=(90, 96, 90))
            col = colors[(r * 8 + j) % 4]
            if bit == "1":
                g.ellipse((x - 90 * SS, y - 30 * SS, x + 90 * SS, y + 150 * SS), fill=tuple(int(v * 0.55) for v in col))
                d.ellipse((x - 34 * SS, y + 20 * SS, x + 34 * SS, y + 120 * SS), fill=col)
            else:
                d.ellipse((x - 34 * SS, y + 20 * SS, x + 34 * SS, y + 120 * SS), fill=(52, 58, 72))
    glow = glow.filter(ImageFilter.GaussianBlur(40 * SS))
    im = Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(im, dtype=int) + __import__("numpy").asarray(glow, dtype=int), 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    title(d, ["Merry Christmas"], 1600, CREAM, [112])
    ctext(d, W * SS / 2, 1770 * SS, "the lights spell a message in binary", F("semi", 50), GOLD)
    return finish(im)


# ------------------------------------------------------------------ 12 prime new year
def c_prime():
    im, d = canvas(NIGHT); rnd = random.Random(27)
    for cx, cy, R, col in ((360, 420, 260, GOLD), (1120, 360, 300, (255, 120, 120)), (760, 700, 220, ICE), (300, 980, 160, (140, 220, 160)), (1210, 960, 190, GOLD)):
        n = rnd.choice((29, 31, 37, 41))  # primes
        for k in range(n):
            a = 2 * math.pi * k / n
            for t0, t1 in ((0.25, 0.75), (0.82, 0.95)):
                d.line((cx * SS + R * SS * t0 * math.cos(a), cy * SS + R * SS * t0 * math.sin(a),
                        cx * SS + R * SS * t1 * math.cos(a), cy * SS + R * SS * t1 * math.sin(a)), fill=col, width=4 * SS)
    ctext(d, W * SS / 2, 1080 * SS, "2027", F("cinzel", 330), GOLD)
    title(d, ["Have a Prime", "New Year"], 1530, CREAM, [104, 104])
    ctext(d, W * SS / 2, 1790 * SS, "2027 is a prime number", F("semi", 54), GOLD)
    return finish(im)


CARDS = [
    ("tree", c_tree, "Fractal Tree",
     "May your joy branch out in every direction.\nMerry Christmas!",
     "This tree is a fractal: every branch splits into two smaller copies of itself, eleven times over, giving 2,048 tips. Real trees, rivers and lungs grow with the same kind of branching."),
    ("koch", c_koch, "Koch Snowflake",
     "Wishing you a season of infinite joy.\nMerry Christmas!",
     "The Koch snowflake: replace the middle third of every edge with a small triangle, and repeat forever. Its perimeter grows without limit, yet the area it encloses stays finite: exactly 8/5 of the starting triangle."),
    ("pi", c_pi, "O Pi-ne Tree",
     "Wishing you an irrationally happy Christmas\nand a never-ending New Year!",
     "This tree is built from the first digits of pi, 3.14159..., read row by row from the top. Pi is irrational: its digits go on forever without repeating, so the tree could keep growing indefinitely."),
    ("fibonacci", c_fib, "Golden Wreath",
     "Wishing you a holiday season in perfect proportion.",
     "Each leaf of the wreath is turned by the golden angle, about 137.5 degrees, from the one before, the same rule sunflowers and pine cones follow. Count the spirals and you will find Fibonacci numbers."),
    ("sierpinski", c_sier, "Sierpinski Tree",
     "May your Christmas be merry at every scale!",
     "The Sierpinski triangle: cut the middle out of a triangle, then do the same to the three triangles that remain, again and again. Every part is a smaller copy of the whole."),
    ("xmas", c_xmas, "Solve for X-mas",
     "x = all the joy in the world.\nMerry Christmas!",
     "The tree on the chalkboard is the region of the plane where y is at most 8 - 1.6|x|: two straight lines meeting at the top make the triangle, and the absolute value |x| makes it symmetric."),
    ("364", c_364, "Twelve Days, 364 Gifts",
     "Almost one gift for every day of the year.\nMerry Christmas!",
     "In the song, day n brings 1 + 2 + ... + n gifts, a triangular number (the twelfth day alone brings 78, the triangle on the front). Adding all twelve gives the tetrahedral number 364."),
    ("santa_route", c_tsp, "Santa's Shortest Path",
     "Hope Santa finds the shortest path to your house!\nMerry Christmas!",
     "Visiting every house once by the shortest route is the famous Traveling Salesman Problem. Nobody knows a fast method that always finds the best tour; this one was found with the nearest-neighbour rule and 2-opt improvements."),
    ("lissajous", c_liss, "Well-Rounded Christmas",
     "Wishing you harmony, rhythm and joy this Christmas.",
     "Each ornament is a Lissajous curve, traced by two vibrations at right angles. Frequencies in the ratio 3:2, 5:4 and 3:4 give these three patterns; you can see them on an oscilloscope."),
    ("snowflakes", c_flakes, "No Two Alike",
     "Unique, just like you.\nHappy Holidays!",
     "Every snowflake has six-fold symmetry because water molecules lock into a hexagonal crystal lattice. The arms grow the same way because they meet the same temperature and humidity at the same time."),
    ("binary", c_binary, "Joy in Binary",
     "The lights say JOY in binary.\nWishing you a merry Christmas, bit by bit!",
     "Read each string of 8 lights as a byte: lit = 1, dark = 0. 01001010 = 74 = J, 01001111 = 79 = O and 01011001 = 89 = Y in ASCII, the code computers use for text."),
    ("prime_2027", c_prime, "Prime New Year",
     "Wishing you a prime year,\ndivisible only by joy and you!",
     "2027 is prime: no whole number other than 1 and 2027 divides it. To check, it is enough to try the primes up to 45, since 45 x 45 = 2025. The fireworks have prime numbers of rays too."),
]


# ------------------------------------------------------------------ PDF (5 x 7 card, two per sheet side)
def build_pdf(name, PW, PH):
    doc = fitz.open(); IN = 72
    cw, chh = 5 * IN, 7 * IN               # one panel
    sx = (PW - 2 * cw) / 2; sy = (PH - chh) / 2  # spread = 10 x 7 in centred, landscape
    def marks(p):
        for x in (sx, sx + cw, sx + 2 * cw):
            p.draw_line((x, sy - 22), (x, sy - 6), color=(0.5, 0.5, 0.5), width=0.5)
            p.draw_line((x, sy + chh + 6), (x, sy + chh + 22), color=(0.5, 0.5, 0.5), width=0.5)
        for y in (sy, sy + chh):
            p.draw_line((sx - 22, y), (sx - 6, y), color=(0.5, 0.5, 0.5), width=0.5)
            p.draw_line((sx + 2 * cw + 6, y), (sx + 2 * cw + 22, y), color=(0.5, 0.5, 0.5), width=0.5)
    def tx(p, x, y, s, f, size, col):
        p.insert_text((x, y), s, fontname=f, fontsize=size, color=col)
    def ctx(p, cx, y, s, f, size, col):
        tx(p, cx - FOBJ[f].text_length(s, fontsize=size) / 2, y, s, f, size, col)
    def para(p, x, y, s, f, size, width, col, lh=1.45):
        for line in s.split("\n"):
            words, cur = line.split(" "), ""
            for w in words:
                t = (cur + " " + w).strip()
                if FOBJ[f].text_length(t, fontsize=size) <= width:
                    cur = t
                else:
                    tx(p, x, y, cur, f, size, col); y += size * lh; cur = w
            tx(p, x, y, cur, f, size, col); y += size * lh
        return y
    cc = lambda rgb: tuple(v / 255 for v in rgb)
    # cover + how-to page
    p = doc.new_page(width=PW, height=PH)
    for k, v in FONTS.items():
        p.insert_font(fontname=k, fontfile=v)
    p.draw_rect(fitz.Rect(0, 0, PW, PH), color=None, fill=cc(NAVY))
    ctx(p, PW / 2, 70, "MATH CHRISTMAS CARDS", "title", 30, cc(CREAM))
    ctx(p, PW / 2, 96, "12 printable 5 x 7 in folding cards  ·  real mathematics, made beautiful", "body", 11, cc(GOLD))
    tw = (PW - 80) / 6
    for i, (key, _, _, _, _) in enumerate(CARDS):
        r, col = divmod(i, 6)
        rect = fitz.Rect(40 + col * tw + 6, 120 + r * (tw * 1.4 + 14), 40 + (col + 1) * tw - 6, 120 + r * (tw * 1.4 + 14) + (tw - 12) * 1.4)
        p.insert_image(rect, filename=os.path.join(FR, f"{i + 1:02d}_{key}.png"))
    y = 120 + 2 * (tw * 1.4 + 14) + 18
    for line in ("HOW TO PRINT", ):
        tx(p, 40, y, line, "bold", 11, cc(GOLD)); y += 18
    steps = ("Each card has two pages: OUTSIDE (back + front) and INSIDE (your message). Print double-sided on "
             "card stock, landscape, 'flip on short edge', at 100% / actual size. No duplex printer? Print the outside "
             "page, put the sheet back in the tray and print the inside page on the reverse.\n"
             "Cut along the corner marks (10 x 7 in), score the middle and fold. Fits a standard A7 (5.25 x 7.25 in) envelope.\n"
             "Want to send one digitally? The 'fronts' folder has every front as a PNG image.")
    para(p, 40, y, steps, "body", 9.5, PW - 80, cc(CREAM))
    for i, (key, fn, ttl, inside, back) in enumerate(CARDS):
        # OUTSIDE: left = back, right = front
        p = doc.new_page(width=PW, height=PH)
        for k, v in FONTS.items():
            p.insert_font(fontname=k, fontfile=v)
        p.insert_image(fitz.Rect(sx + cw, sy, sx + 2 * cw, sy + chh), filename=os.path.join(FR, f"{i + 1:02d}_{key}.png"))
        bx = sx + 0.55 * IN; bw = cw - 1.1 * IN
        ctx(p, sx + cw / 2, sy + 2.2 * IN, "THE MATH ON THE FRONT", "bold", 9, cc(RED))
        para(p, bx, sy + 2.55 * IN, back, "body", 10, bw, cc(INK))
        ctx(p, sx + cw / 2, sy + chh - 0.75 * IN, "MathRelaxing", "title_r", 11, cc(NAVY))
        ctx(p, sx + cw / 2, sy + chh - 0.55 * IN, "real mathematics, made beautiful", "light", 8, cc(SUB))
        marks(p)
        tx(p, 24, PH - 18, f"Card {i + 1} of 12 - {ttl} - OUTSIDE (print this side first)", "body", 7.5, (0.5, 0.5, 0.5))
        # INSIDE: right panel message
        p = doc.new_page(width=PW, height=PH)
        for k, v in FONTS.items():
            p.insert_font(fontname=k, fontfile=v)
        lines = inside.split("\n"); y0 = sy + chh * 0.42
        for j, ln in enumerate(lines):
            ctx(p, sx + cw * 1.5, y0 + j * 26, ln, "title" if j == len(lines) - 1 and len(lines) > 1 else "body",
                17 if j == len(lines) - 1 and len(lines) > 1 else 13.5, cc(PINE if j == len(lines) - 1 else INK))
        sn = sy + chh * 0.72
        p.draw_line((sx + cw + 1.0 * IN, sn), (sx + 2 * cw - 1.0 * IN, sn), color=cc((205, 198, 184)), width=0.6)
        ctx(p, sx + cw * 1.5, sn + 14, "with love from", "light", 8.5, cc(SUB))
        marks(p)
        tx(p, 24, PH - 18, f"Card {i + 1} of 12 - {ttl} - INSIDE (print on the back of the outside page)", "body", 7.5, (0.5, 0.5, 0.5))
    path = os.path.join(OUT, f"Math_Christmas_Cards_{name}.pdf")
    doc.save(path, deflate=True, garbage=3)
    print(f"{name}: {len(doc)} pages, {os.path.getsize(path) // 1024} KB")
    return path


if __name__ == "__main__":
    for i, (key, fn, *_rest) in enumerate(CARDS):
        p = os.path.join(FR, f"{i + 1:02d}_{key}.png")
        fn().save(p, dpi=(300, 300)); print("front", p)
    build_pdf("Letter", 792, 612)
    build_pdf("A4", 841.9, 595.3)
