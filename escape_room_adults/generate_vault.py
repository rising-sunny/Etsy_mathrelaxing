"""
Printable Escape Room for Adults — "The Mathematician's Vault".

Nine classic puzzles hidden in Professor Elias Hartmann's study. Each answer is a number
1-26 that the decoder (A=1 ... Z=26) turns into a letter; the nine letters spell the
vault password LOGARITHM. Every answer is checked in code below.
US Letter + A4 PDFs at 300 DPI.

  python generate_vault.py
"""
import os, sys, math, itertools
from PIL import Image, ImageDraw
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
from generate_advent import font, wrap, draw_par

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
DPI = 300
PAPER = (244, 236, 218); INK = (40, 34, 30); SEPIA = (120, 90, 56); NAVY = (26, 36, 62); GOLD = (184, 140, 62)
OX = (128, 40, 36); SOFT = (232, 222, 198); SUB = (110, 98, 84)
PASSWORD = "LOGARITHM"


def a1z26(n):
    return chr(64 + n)


# ------------------------------------------------------------------ puzzle data + verification
PLAIN = "THE FIRST NUMBER IS TWELVE"
CIPHER = "".join(chr((ord(c) - 65 + 3) % 26 + 65) if c.isalpha() else c for c in PLAIN)
DURER = [[16, 3, 2, 13], [5, 10, 11, 8], [9, 6, 7, 12], [4, None, 14, 1]]  # missing 15
LOGIC_CLUES = [
    "The number theorist has the highest office number.",
    "Boris has the lowest office number.",
    "Clara's office is not number 5, and she is not the algebraist.",
    "The algebraist's office number is exactly 2 more than the geometer's.",
    "Ada is not the topologist, and neither is Boris.",
    "Ada's office number is higher than Dmitri's.",
]
LAMPS = "01001"


def verify():
    # 1 Caesar
    dec = "".join(chr((ord(c) - 65 - 3) % 26 + 65) if c.isalpha() else c for c in CIPHER)
    assert dec == PLAIN and "TWELVE" in dec; a1 = 12
    # 2 Durer magic square
    full = [[15 if v is None else v for v in r] for r in DURER]
    assert all(sum(r) == 34 for r in full) and all(sum(full[i][j] for i in range(4)) == 34 for j in range(4))
    assert sum(full[i][i] for i in range(4)) == 34 and sum(full[i][3 - i] for i in range(4)) == 34; a2 = 15
    # 3 logic grid (unique solution)
    names = ["Ada", "Boris", "Clara", "Dmitri"]; offs = [3, 5, 7, 11]; fields = ["Algebra", "Topology", "Number Theory", "Geometry"]
    sols = []
    for o in itertools.permutations(offs):
        for f in itertools.permutations(fields):
            O = dict(zip(names, o)); F = dict(zip(names, f)); inv = {v: k for k, v in F.items()}
            if (O[inv["Number Theory"]] == 11 and O["Boris"] == 3 and O["Clara"] != 5 and F["Clara"] != "Algebra"
                    and O[inv["Algebra"]] == O[inv["Geometry"]] + 2 and F["Ada"] != "Topology" and F["Boris"] != "Topology"
                    and O["Ada"] > O["Dmitri"]):
                sols.append(O[inv["Topology"]])
    assert sols == [7]; a3 = 7
    # 4 symbol equations: tri + circ = 5, circ + sq = 9, tri + sq = 6
    s = [(t, c, q) for t in range(1, 27) for c in range(1, 27) for q in range(1, 27) if t + c == 5 and c + q == 9 and t + q == 6]
    assert s == [(1, 4, 5)]; a4 = 1
    # 5 hexagonal prism edges
    a5 = 6 * 3; assert a5 == 18
    # 6 binary lamps
    a6 = int(LAMPS, 2); assert a6 == 9
    # 7 Roman numerals MMXXVII - MMVII
    a7 = 2027 - 2007; assert a7 == 20
    # 8 SEND + MORE = MONEY -> R
    sol = [p for p in itertools.permutations(range(10), 8) if p[0] and p[4] and
           (1000 * p[0] + 100 * p[1] + 10 * p[2] + p[3]) + (1000 * p[4] + 100 * p[5] + 10 * p[6] + p[1]) ==
           10000 * p[4] + 1000 * p[5] + 100 * p[2] + 10 * p[1] + p[7]]
    assert len(sol) == 1; a8 = sol[0][6]; assert a8 == 8
    # 9 Fibonacci rabbits, month 7
    f = [1, 1]
    while len(f) < 7:
        f.append(f[-1] + f[-2])
    a9 = f[6]; assert a9 == 13
    ans = [a1, a2, a3, a4, a5, a6, a7, a8, a9]
    assert "".join(a1z26(a) for a in ans) == PASSWORD
    return ans


ANS = verify()


# ------------------------------------------------------------------ page helpers
def new(size):
    im = Image.new("RGB", size, PAPER); d = ImageDraw.Draw(im)
    return im, d


def frame(d, W, H, col=SEPIA):
    m = int(W * 0.035)
    d.rectangle((m, m, W - m, H - m), outline=col, width=8)
    d.rectangle((m + 22, m + 22, W - m - 22, H - m - 22), outline=col, width=3)
    for x, y in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
        d.regular_polygon((x, y, 26), 4, rotation=45, fill=PAPER, outline=GOLD, width=6)


def ctext(d, cx, y, s, f, fill=INK):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def lock_box(d, W, H, n):
    y = H - int(H * 0.17); x0 = int(W * 0.09); x1 = W - int(W * 0.09)
    d.rounded_rectangle((x0, y, x1, y + int(H * 0.105)), radius=20, fill=NAVY)
    d.text((x0 + 50, y + 34), f"LOCK {n}  ·  your answer", font=font("bold", int(W * 0.022)), fill=PAPER)
    bw = int(W * 0.075)
    for k in range(2):
        bx = x0 + 60 + k * (bw + 30); d.rounded_rectangle((bx, y + 100, bx + bw, y + 100 + bw * 0.9), radius=10, fill=PAPER)
    d.text((x0 + 60 + 2 * (bw + 30) + 30, y + 120), "=", font=font("cinzel", int(W * 0.05)), fill=GOLD)
    lx = x0 + 60 + 2 * (bw + 30) + 140
    d.rounded_rectangle((lx, y + 100, lx + bw, y + 100 + bw * 0.9), radius=10, fill=GOLD)
    d.text((lx + bw + 40, y + 115), "decoder letter\n(A=1 ... Z=26)", font=font("body", int(W * 0.018)), fill=PAPER)


def puzzle_page(size, n, title, story, draw_fn, question):
    im, d = new(size); W, H = size
    frame(d, W, H)
    d.text((int(W * 0.09), int(H * 0.06)), f"EXHIBIT {n} OF 9", font=font("bold", int(W * 0.018)), fill=OX)
    d.text((int(W * 0.09), int(H * 0.06) + 70), title, font=font("cinzel", int(W * 0.05)), fill=NAVY)
    y = draw_par(d, (int(W * 0.09), int(H * 0.06) + 230), story, font("body", int(W * 0.021)), int(W * 0.82), fill=INK)
    draw_fn(d, (int(W * 0.09), y + 40, W - int(W * 0.09), int(H * 0.66)), W)
    d.rounded_rectangle((int(W * 0.09), int(H * 0.68), W - int(W * 0.09), int(H * 0.79)), radius=18, fill=SOFT)
    draw_par(d, (int(W * 0.09) + 40, int(H * 0.68) + 40), question, font("bold", int(W * 0.023)), int(W * 0.74), fill=NAVY)
    lock_box(d, W, H, n)
    return im


# ------------------------------------------------------------------ puzzle graphics
def g_caesar(d, a, W):
    x0, y0, x1, y1 = a; cx = (x0 + x1) / 2
    d.rectangle((cx - 300, y0 + 10, cx + 300, y0 + 130), fill=(110, 80, 50)); d.rectangle((cx - 60, y0 + 50, cx + 60, y0 + 80), fill=GOLD)
    ctext(d, cx, y0 + 140, "the brass label on the drawer reads:  III", font("semi", 46), SEPIA)
    py = y0 + 260
    d.rectangle((x0 + 60, py, x1 - 60, py + 520), fill=(250, 246, 234), outline=SEPIA, width=4)
    f = font("bold", 118); words = CIPHER.split(" "); lines = [" ".join(words[:2]), " ".join(words[2:4]), words[4]]
    for i, ln in enumerate(lines):
        ctext(d, cx, py + 50 + i * 155, ln, f, INK)


def g_durer(d, a, W):
    x0, y0, x1, y1 = a; s = min(x1 - x0, y1 - y0) * 0.9; c = s / 4; gx = (x0 + x1 - s) / 2; gy = y0 + (y1 - y0 - s) / 2
    f = font("cinzel", int(c * 0.42))
    for r in range(4):
        for k in range(4):
            bx, by = gx + k * c, gy + r * c
            d.rectangle((bx, by, bx + c, by + c), outline=SEPIA, width=6, fill=(250, 246, 234))
            v = DURER[r][k]; s_ = "?" if v is None else str(v)
            ctext(d, bx + c / 2, by + c / 2 - f.size * 0.62, s_, f, OX if v is None else INK)


def g_logic(d, a, W):
    x0, y0, x1, y1 = a; y = y0 + 20
    f = font("body", int(W * 0.026))
    fs = font("semi", int(W * 0.024))
    for s_ in ("Offices: 3, 5, 7 and 11", "Colleagues: Ada, Boris, Clara, Dmitri", "Fields: Algebra, Topology, Number Theory, Geometry"):
        d.text((x0, y), s_, font=fs, fill=SEPIA); y += 85
    y += 40
    for i, cl in enumerate(LOGIC_CLUES, 1):
        d.text((x0, y), f"{i}.", font=font("bold", int(W * 0.026)), fill=OX)
        y = draw_par(d, (x0 + 70, y), cl, f, x1 - x0 - 70, fill=INK) + 26


def shape(d, kind, cx, cy, r, col):
    if kind == "tri":
        d.polygon([(cx, cy - r), (cx - r * 0.95, cy + r * 0.75), (cx + r * 0.95, cy + r * 0.75)], fill=col)
    elif kind == "circ":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    else:
        d.rectangle((cx - r * 0.85, cy - r * 0.85, cx + r * 0.85, cy + r * 0.85), fill=col)


def g_symbols(d, a, W):
    x0, y0, x1, y1 = a; f = font("cinzel", 150); r = 85
    rows = [("tri", "circ", "5"), ("circ", "sq", "9"), ("tri", "sq", "6")]
    cols = {"tri": OX, "circ": NAVY, "sq": GOLD}
    for i, (p, q, s) in enumerate(rows):
        cy = y0 + 150 + i * 300; cx = (x0 + x1) / 2 - 450
        shape(d, p, cx, cy, r, cols[p]); d.text((cx + 140, cy - 95), "+", font=f, fill=INK)
        shape(d, q, cx + 390, cy, r, cols[q]); d.text((cx + 530, cy - 95), "=", font=f, fill=INK)
        d.text((cx + 720, cy - 95), s, font=f, fill=INK)


def g_prism(d, a, W):
    x0, y0, x1, y1 = a; cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    L = 1500; R = 250; tilt = 0.45
    hexf = [(math.cos(math.pi / 3 * k + math.pi / 6) * R, math.sin(math.pi / 3 * k + math.pi / 6) * R) for k in range(6)]
    A = [(cx - L / 2 + x * tilt, cy + y) for x, y in hexf]; B = [(cx + L / 2 + x * tilt, cy + y) for x, y in hexf]
    for k in range(6):
        d.line((A[k], B[k]), fill=SEPIA, width=5)
    d.polygon(B, fill=(232, 196, 100), outline=SEPIA); d.line(B + [B[0]], fill=SEPIA, width=6)
    d.line(A + [A[0]], fill=SEPIA, width=6)
    ctext(d, cx, y1 - 70, "(a new, unsharpened hexagonal pencil)", font("light", 42), SUB)


def g_lamps(d, a, W):
    x0, y0, x1, y1 = a; n = len(LAMPS); sp = (x1 - x0) / n; cy = (y0 + y1) / 2
    for i, b in enumerate(LAMPS):
        cx = x0 + sp * (i + 0.5)
        d.line((cx, cy + 40, cx, cy + 230), fill=SEPIA, width=10); d.rectangle((cx - 70, cy + 230, cx + 70, cy + 250), fill=SEPIA)
        shade = [(cx - 110, cy + 40), (cx + 110, cy + 40), (cx + 60, cy - 110), (cx - 60, cy - 110)]
        if b == "1":
            d.ellipse((cx - 150, cy - 160, cx + 150, cy + 150), fill=(250, 232, 170))
            d.polygon(shade, fill=(236, 190, 80))
        else:
            d.polygon(shade, fill=(150, 140, 126))
    ctext(d, (x0 + x1) / 2, y1 - 60, "the professor read his five desk lamps from left to right", font("light", 40), SUB)


def g_roman(d, a, W):
    x0, y0, x1, y1 = a; d.rectangle((x0 + 40, y0 + 20, x1 - 40, y1 - 40), fill=(46, 62, 54), outline=(110, 80, 50), width=20)
    cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    ctext(d, cx, cy - 160, "MMXXVII", font("cinzel", 130), (236, 236, 226))
    ctext(d, cx, cy - 10, "-  MMVII", font("cinzel", 130), (236, 236, 226))
    d.line((cx - 380, cy + 160, cx + 380, cy + 160), fill=(236, 236, 226), width=8)
    ctext(d, cx, cy + 180, "?", font("cinzel", 130), (240, 210, 120))


def g_send(d, a, W):
    x0, y0, x1, y1 = a; f = font("cinzel", 140); xr = (x0 + x1) / 2 + 330; y = y0 + 40
    for s in ("SEND", "+ MORE"):
        d.text((xr - d.textlength(s, font=f), y), s, font=f, fill=INK); y += 170
    d.line((xr - 640, y + 10, xr, y + 10), fill=INK, width=8)
    d.text((xr - d.textlength("MONEY", font=f), y + 30), "MONEY", font=f, fill=OX)


def g_rabbits(d, a, W):
    x0, y0, x1, y1 = a; f = font("semi", 60); fb = font("bold", 52)
    months = ["Month", "1", "2", "3", "4", "5", "6", "7"]; pairs = ["Pairs", "1", "1", "2", "3", "", "", "?"]
    cw = (x1 - x0) / 8; ty = y0 + 60
    for i, (m, p) in enumerate(zip(months, pairs)):
        x = x0 + i * cw
        d.rectangle((x, ty, x + cw, ty + 150), outline=SEPIA, width=4, fill=SOFT if i == 0 else (250, 246, 234))
        d.rectangle((x, ty + 150, x + cw, ty + 300), outline=SEPIA, width=4, fill=SOFT if i == 0 else (250, 246, 234))
        ctext(d, x + cw / 2, ty + 42, m, fb if i == 0 else f, INK)
        ctext(d, x + cw / 2, ty + 192, p, fb if i == 0 else f, OX if p == "?" else INK)
    for k in range(5):
        x = x0 + 120 + k * 260; y = y1 - 220
        d.ellipse((x, y, x + 120, y + 90), fill=(200, 188, 168)); d.ellipse((x + 90, y - 40, x + 160, y + 30), fill=(200, 188, 168))
        d.ellipse((x + 100, y - 120, x + 125, y - 20), fill=(200, 188, 168)); d.ellipse((x + 128, y - 110, x + 153, y - 20), fill=(200, 188, 168))


PUZZLES = [
    ("The Locked Drawer", "A note in the professor's drawer is written in a cipher once used by Julius Caesar: every letter has been shifted the same number of places along the alphabet.",
     g_caesar, "Decode the note. Which number does it give you?"),
    ("The Engraver's Square", "A copy of Albrecht Dürer's 1514 engraving Melencolia I hangs above the fireplace. In its corner is a magic square: every row, column and diagonal adds to the same total. One cell has been scratched out.",
     g_durer, "Which number belongs in the scratched-out cell?"),
    ("The Faculty Corridor", "Four colleagues of the professor have offices on the same corridor. Each has a different office number and a different field.",
     g_logic, "Which office number belongs to the topologist?"),
    ("The Symbol Ledger", "In his ledger the professor replaced numbers with symbols. Each symbol stands for a positive whole number.",
     g_symbols, "What number does the red triangle stand for?"),
    ("The Pencil Jar", "Every pencil in the professor's jar is a perfect hexagonal prism. He liked to count things that most people never notice.",
     g_prism, "How many edges does one unsharpened hexagonal pencil have?"),
    ("The Desk Lamps", "The professor never wrote his codes down. Instead he left his desk lamps on or off, lit = 1 and dark = 0, and read them as a binary number.",
     g_lamps, "Which number do the five lamps show?"),
    ("The Chalkboard", "On the chalkboard, the last calculation the professor wrote before he left, in Roman numerals.",
     g_roman, "What is the result, written as an ordinary number?"),
    ("The Famous Telegram", "A framed telegram from 1924 hangs by the door. Each letter stands for a different digit, and no number starts with 0.",
     g_send, "Which digit does the letter R stand for?"),
    ("The Rabbit Problem", "Leonardo of Pisa (Fibonacci) asked in 1202: a newborn pair of rabbits matures after one month, and from then on every mature pair has a new pair each month. Nobody dies.",
     g_rabbits, "Starting with one newborn pair in month 1, how many pairs are there in month 7?"),
]
HINTS = [
    "Shift every letter 3 places BACK: W becomes T, K becomes H.",
    "Find the magic total from a complete row first (16 + 3 + 2 + 13).",
    "Boris has office 3 and the number theorist has 11. Who could be the algebraist?",
    "Add all three equations: you get 2 x (triangle + circle + square).",
    "Count the edges of each hexagonal end, then the long edges along the sides.",
    "Binary place values from the right are 1, 2, 4, 8, 16.",
    "MMXXVII is 2027. What is MMVII?",
    "M must be 1 (it is a carried digit), so O is 0 and S is 9.",
    "Each month's total is the sum of the previous two months.",
]
EXPLAIN = [
    "Shifting back 3 turns the note into THE FIRST NUMBER IS TWELVE.",
    "Every line adds to 34. Bottom row: 4 + ? + 14 + 1 = 34, so ? = 15.",
    "Only one arrangement fits all six clues: Boris 3 Geometry, Dmitri 5 Algebra, Clara 7 Topology, Ada 11 Number Theory.",
    "Adding gives 2(t + c + s) = 20, so t + c + s = 10. Then t = 10 - 9 = 1.",
    "Two hexagons with 6 edges each (12) plus 6 long edges: 18.",
    "01001 in binary is 8 + 1 = 9.",
    "2027 - 2007 = 20.",
    "9567 + 1085 = 10652, so R = 8.",
    "1, 1, 2, 3, 5, 8, 13: the Fibonacci numbers.",
]
assert len(PUZZLES) == len(HINTS) == len(EXPLAIN) == 9


# ------------------------------------------------------------------ other pages
def cover(size):
    im, d = new(size); W, H = size
    d.rectangle((0, 0, W, H), fill=NAVY)
    m = int(W * 0.05); d.rectangle((m, m, W - m, H - m), outline=GOLD, width=6)
    cx, cy, R = W / 2, H * 0.34, W * 0.23  # vault dial
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(58, 70, 98), outline=GOLD, width=16)
    for k in range(60):
        a = 2 * math.pi * k / 60; r1 = R * (0.80 if k % 5 else 0.72)
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + R * 0.92 * math.cos(a), cy + R * 0.92 * math.sin(a)), fill=GOLD, width=5)
    d.ellipse((cx - R * 0.45, cy - R * 0.45, cx + R * 0.45, cy + R * 0.45), fill=(36, 46, 72), outline=GOLD, width=10)
    ctext(d, cx, cy - R * 0.3, "π", font("bold", int(R * 0.55)), GOLD)
    ctext(d, W / 2, H * 0.60, "THE MATHEMATICIAN'S", font("cinzel", int(W * 0.058)), PAPER)
    ctext(d, W / 2, H * 0.60 + W * 0.08, "VAULT", font("cinzel", int(W * 0.12)), GOLD)
    ctext(d, W / 2, H * 0.60 + W * 0.25, "A printable escape room for adults", font("semi", int(W * 0.032)), PAPER)
    ctext(d, W / 2, H * 0.86, "9 puzzles  ·  2-6 players  ·  60-90 minutes", font("body", int(W * 0.025)), (210, 214, 226))
    ctext(d, W / 2, H * 0.92, "MathRelaxing", font("cinzel_r", int(W * 0.024)), GOLD)
    return im


def text_page(size, title, blocks, col=NAVY):
    im, d = new(size); W, H = size; frame(d, W, H)
    d.text((int(W * 0.09), int(H * 0.07)), title, font=font("cinzel", int(W * 0.05)), fill=col)
    y = int(H * 0.07) + int(W * 0.09)
    for head, body in blocks:
        if head:
            d.text((int(W * 0.09), y), head, font=font("bold", int(W * 0.027)), fill=OX); y += int(W * 0.045)
        y = draw_par(d, (int(W * 0.09), y), body, font("body", int(W * 0.021)), int(W * 0.82), fill=INK) + int(W * 0.03)
    return im


def host_guide(size):
    return text_page(size, "Host Guide", [
        ("What you need", "A printer, pencils, scissors for the hint cards, a timer and a little scrap paper. Optional: an envelope or small box as 'the vault' with a treat or a bottle inside."),
        ("Setting up", "Print the professor's letter, the nine exhibits and the vault page. Cut out the hint cards and keep them, with the answer key, away from the players. Hide the exhibits around the room, or lay them on a table face down."),
        ("How it works", "Each exhibit opens one lock with a number from 1 to 26. Players turn every number into a letter with the decoder (A=1 ... Z=26). The nine letters, in lock order, spell the password that opens the vault. If the letters form a real word, every answer is right."),
        ("Players and time", "2 to 6 adults or teens. Allow 60 to 90 minutes. The puzzles can be solved in any order, so a big group can split up."),
        ("Hints", "Hand out a hint card when a team has been stuck for about 10 minutes. For a tougher game, every hint adds 5 minutes to the final time."),
    ])


def letter(size):
    im = text_page(size, "A Letter from the Professor", [
        ("", "My dear friends,\n\nIf you are reading this, I have finally gone to count the stars in person. Everything I owned of value is locked in the vault behind my desk, and I have left it to whoever can open it.\n\nThe password is a single word, the one word I loved most. I have hidden it, one letter at a time, in nine exhibits around this study: a note, a painting, my colleagues, my ledger, my pencils, my lamps, my chalkboard, a telegram and an old problem about rabbits.\n\nSolve each one, turn each number into its letter, and the vault is yours. Work together, argue freely, and do not peek at the answers. I always said the fun is in the struggle.\n\nWith affection and a little mischief,\n\nProf. Elias Hartmann"),
    ], NAVY)
    d = ImageDraw.Draw(im); W, H = size
    d.rounded_rectangle((int(W * 0.25), int(H * 0.82), int(W * 0.75), int(H * 0.90)), radius=20, fill=NAVY)
    ctext(d, W / 2, int(H * 0.835), "START TIME  __ : __", font("bold", int(W * 0.03)), PAPER)
    return im


def decoder_strip(d, x0, y, x1):
    cw = (x1 - x0) / 13; f1 = font("bold", 40); f2 = font("body", 30)
    for r in range(2):
        for k in range(13):
            n = r * 13 + k + 1; bx = x0 + k * cw; by = y + r * 130
            d.rectangle((bx, by, bx + cw, by + 120), outline=SEPIA, width=3, fill=(250, 246, 234))
            ctext(d, bx + cw / 2, by + 12, chr(64 + n), f1, OX); ctext(d, bx + cw / 2, by + 70, str(n), f2, INK)


def vault(size):
    im, d = new(size); W, H = size; frame(d, W, H, GOLD)
    ctext(d, W / 2, int(H * 0.06), "THE VAULT", font("cinzel", int(W * 0.07)), NAVY)
    ctext(d, W / 2, int(H * 0.06) + int(W * 0.1), "Turn each code into its letter. The nine letters open the vault.", font("semi", int(W * 0.022)), OX)
    x0, x1 = int(W * 0.09), W - int(W * 0.09)
    decoder_strip(d, x0, int(H * 0.17), x1)
    n = 9; gap = 20; bw = (x1 - x0 - (n - 1) * gap) / n; y = int(H * 0.32)
    for i in range(n):
        bx = x0 + i * (bw + gap)
        ctext(d, bx + bw / 2, y, f"Lock {i + 1}", font("bold", 32), SUB)
        d.rounded_rectangle((bx, y + 55, bx + bw, y + 55 + bw * 0.85), radius=12, outline=NAVY, width=5, fill=(250, 246, 234))
        d.rounded_rectangle((bx, y + 110 + bw, bx + bw, y + 110 + 2 * bw), radius=12, fill=GOLD)
    cx, cy, R = W / 2, int(H * 0.66), int(W * 0.18)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(58, 70, 98), outline=GOLD, width=14)
    for k in range(40):
        a = 2 * math.pi * k / 40
        d.line((cx + R * 0.75 * math.cos(a), cy + R * 0.75 * math.sin(a), cx + R * 0.92 * math.cos(a), cy + R * 0.92 * math.sin(a)), fill=GOLD, width=5)
    ctext(d, cx, cy - R * 0.35, "π", font("bold", int(R * 0.6)), GOLD)
    d.rounded_rectangle((int(W * 0.12), int(H * 0.83), W - int(W * 0.12), int(H * 0.92)), radius=24, fill=NAVY)
    ctext(d, W / 2, int(H * 0.85), "PASSWORD:  _  _  _  _  _  _  _  _  _", font("bold", int(W * 0.034)), PAPER)
    return im


def hints_page(size):
    im, d = new(size); W, H = size
    d.text((int(W * 0.06), int(H * 0.03)), "Hint Cards  ·  cut along the dotted lines", font=font("bold", int(W * 0.026)), fill=NAVY)
    mx, my = int(W * 0.05), int(H * 0.07); cw, ch = (W - 2 * mx) / 3, (H - my - int(H * 0.03)) / 3
    for i, h in enumerate(HINTS):
        r, c = divmod(i, 3); x0, y0 = mx + c * cw, my + r * ch
        for x in range(int(x0), int(x0 + cw), 26):
            d.line((x, y0, x + 12, y0), fill=SUB, width=2); d.line((x, y0 + ch, x + 12, y0 + ch), fill=SUB, width=2)
        for y in range(int(y0), int(y0 + ch), 26):
            d.line((x0, y, x0, y + 12), fill=SUB, width=2); d.line((x0 + cw, y, x0 + cw, y + 12), fill=SUB, width=2)
        d.rounded_rectangle((x0 + 24, y0 + 24, x0 + cw - 24, y0 + ch - 24), radius=16, fill=SOFT)
        d.text((x0 + 60, y0 + 60), f"HINT · EXHIBIT {i + 1}", font=font("bold", 40), fill=OX)
        draw_par(d, (x0 + 60, y0 + 140), h, font("body", 40), cw - 120, fill=INK)
    return im


def answer_key(size):
    im, d = new(size); W, H = size; frame(d, W, H, NAVY)
    d.text((int(W * 0.09), int(H * 0.06)), "Answer Key (for the host)", font=font("cinzel", int(W * 0.042)), fill=NAVY)
    y = int(H * 0.06) + int(W * 0.08)
    for i, (t, e) in enumerate(zip(PUZZLES, EXPLAIN)):
        a = ANS[i]
        d.ellipse((int(W * 0.09), y, int(W * 0.09) + 80, y + 80), fill=OX)
        ctext(d, int(W * 0.09) + 40, y + 14, str(i + 1), font("bold", 42), PAPER)
        d.text((int(W * 0.09) + 110, y + 2), f"{t[0]}  —  {a} = {a1z26(a)}", font=font("bold", int(W * 0.021)), fill=NAVY)
        y = draw_par(d, (int(W * 0.09) + 110, y + 64), e, font("body", int(W * 0.0185)), int(W * 0.72), fill=INK) + 32
    d.rounded_rectangle((int(W * 0.09), y + 10, W - int(W * 0.09), y + 150), radius=24, fill=NAVY)
    ctext(d, W / 2, y + 50, f"Vault password:  {PASSWORD}", font("bold", int(W * 0.034)), GOLD)
    return im


def certificate(size):
    im, d = new(size); W, H = size; frame(d, W, H, GOLD)
    ctext(d, W / 2, int(H * 0.16), "THE VAULT IS OPEN", font("cinzel", int(W * 0.062)), NAVY)
    ctext(d, W / 2, int(H * 0.16) + int(W * 0.1), "Certificate of Mathematical Ingenuity", font("semi", int(W * 0.03)), OX)
    cx, cy, R = W / 2, int(H * 0.36), int(W * 0.09)  # small vault dial instead of the password (no spoilers)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(58, 70, 98), outline=GOLD, width=10)
    ctext(d, cx, cy - R * 0.42, "π", font("bold", int(R * 0.75)), GOLD)
    ctext(d, W / 2, int(H * 0.48), "This certifies that", font("body", int(W * 0.026)), SUB)
    for k in range(3):
        d.line((int(W * 0.18), int(H * (0.56 + k * 0.05)), W - int(W * 0.18), int(H * (0.56 + k * 0.05))), fill=NAVY, width=3)
    ctext(d, W / 2, int(H * 0.72), "solved the nine exhibits and opened Professor Hartmann's vault", font("body", int(W * 0.024)), INK)
    ctext(d, W / 2, int(H * 0.80), "Escape time:  ____ minutes      Hints used:  ____", font("bold", int(W * 0.026)), NAVY)
    return im


def terms(size):
    return text_page(size, "Terms of Use", [("", "For personal use, family use and use in a single classroom. Print as many copies as your own household, party or class needs.\n\nPlease do not resell, share the file, or post it anywhere the public can download it.\n\nProfessor Elias Hartmann is a fictional character. Every puzzle and illustration is original work by MathRelaxing, and every answer was checked by computer. If you ever spot a problem, send a message through the shop and a corrected file will be sent free.\n\nGood luck, and enjoy the struggle!")])


def build(name, inches):
    size = (int(inches[0] * DPI), int(inches[1] * DPI))
    pages = [cover(size), host_guide(size), letter(size)]
    pages += [puzzle_page(size, i + 1, *p) for i, p in enumerate(PUZZLES)]
    pages += [vault(size), hints_page(size), answer_key(size), certificate(size), terms(size)]
    tmp = os.path.join(OUT, f"_{name}"); os.makedirs(tmp, exist_ok=True); paths = []
    for k, im in enumerate(pages):
        p = os.path.join(tmp, f"p{k:02d}.jpg"); im.save(p, quality=90, dpi=(DPI, DPI)); paths.append(p)
    pdf = os.path.join(OUT, f"Mathematicians_Vault_Escape_Room_{name}.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print(f"{name}: {len(pages)} pages, {os.path.getsize(pdf) // 1024} KB  answers={ANS} -> {PASSWORD}")


if __name__ == "__main__":
    build("Letter", (8.5, 11))
    build("A4", (8.27, 11.69))
