"""
STEM Advent Calendar — "24 Days of Math & Science" printable.

One card per day (puzzle / kitchen-safe mini-experiment / mind-blowing fact),
a hangable 24-door calendar board, instructions, a full answer key and terms.
Renders US Letter and A4 PDFs at 300 DPI.

  python generate_advent.py          # -> out/STEM_Advent_Calendar_{Letter,A4}.pdf
"""
import os, math
from PIL import Image, ImageDraw, ImageFont
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
AF = os.path.join(REPO, "lulu_books", "assets", "fonts")
DPI = 300

CREAM = (250, 246, 238); NAVY = (24, 36, 64); RED = (170, 38, 52); PINE = (33, 92, 72)
GOLD = (196, 152, 64); INK = (36, 36, 40); SUB = (104, 100, 94); LINE = (222, 214, 198)
TYPE_COL = {"PUZZLE": NAVY, "EXPERIMENT": PINE, "FACT": RED}


def font(kind, size):
    if kind == "cinzel":
        return ImageFont.truetype(f"{AF}/Cinzel-SemiBold.ttf", size)
    if kind == "cinzel_r":
        return ImageFont.truetype(f"{AF}/Cinzel.ttf", size)
    f = ImageFont.truetype(f"{AF}/Raleway.ttf", size)
    f.set_variation_by_name({"body": "Medium", "bold": "Bold", "semi": "SemiBold", "light": "Regular"}[kind])
    return f


def wrap(d, text, f, width):
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) <= width:
                line = t
            else:
                out.append(line); line = w
        out.append(line)
    return out


def draw_par(d, xy, text, f, width, fill=INK, lh=1.38):
    x, y = xy
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def snowflake(d, cx, cy, r, col, w=4):
    for k in range(6):
        a = math.pi / 3 * k
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        d.line((cx, cy, x2, y2), fill=col, width=w)
        for t in (0.45, 0.7):
            bx, by = cx + r * t * math.cos(a), cy + r * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.pi / 4
                d.line((bx, by, bx + r * 0.22 * math.cos(b), by + r * 0.22 * math.sin(b)), fill=col, width=w)


# ---------------------------------------------------------------- content
# (type, title, body, answer)
DAYS = [
    ("FACT", "Six-Sided Snow",
     "Every snowflake has six arms. Water molecules lock together into a hexagonal "
     "(six-sided) ice lattice, so the crystal grows six-fold symmetric.\n"
     "TRY IT: Fold a square of paper in half, then into thirds (like a cone), cut "
     "notches along the edges and unfold your own six-armed snowflake.",
     "Water ice forms a hexagonal lattice, so snow crystals have 6-fold symmetry."),
    ("PUZZLE", "The Twelve Days",
     "In the song, your true love gives 1 gift on day 1, 1+2 gifts on day 2, "
     "1+2+3 on day 3 ... all the way to day 12.\nHow many gifts in total?",
     "364. Each day n brings 1+2+...+n gifts; adding days 1 to 12 gives 364 — almost one per day of the year!"),
    ("EXPERIMENT", "Frost Crystals",
     "With an adult: stir Epsom salt into warm water until no more dissolves. "
     "Paint it onto dark paper and leave it somewhere warm overnight.\n"
     "In the morning, look closely: what shapes did the crystals grow into?",
     "As the water evaporates the dissolved salt comes out of solution and grows needle-like crystals."),
    ("PUZZLE", "Party Handshakes",
     "10 guests arrive at a holiday party. Everyone shakes hands with everyone "
     "else exactly once.\nHow many handshakes happen?",
     "45. Each of 10 people shakes 9 hands = 90, but each handshake is counted twice: 90 / 2 = 45."),
    ("FACT", "The One-Sided Loop",
     "A Möbius strip has only ONE side and ONE edge.\n"
     "TRY IT: Take a strip of paper, give one end a half-twist and tape the ends "
     "together. Draw a line down the middle without lifting your pencil — you will "
     "cover 'both' sides! Now cut along your line... surprise!",
     "Cutting a Möbius strip down the middle gives one longer loop (with two twists), not two loops."),
    ("PUZZLE", "Present Pyramid",
     "Gifts are stacked in a square pyramid: 1 box on top, a 2×2 layer under it, "
     "then 3×3, then 4×4 on the bottom.\nHow many boxes are in the pile?",
     "30 boxes: 1 + 4 + 9 + 16 = 30."),
    ("EXPERIMENT", "Dancing Raisins",
     "Drop a few raisins into a clear glass of fizzy water and watch.\n"
     "Why do they sink, rise, and sink again?",
     "Gas bubbles stick to the rough raisins and lift them; at the top the bubbles pop and the raisins sink again."),
    ("FACT", "Pine-Cone Numbers",
     "Look at the bottom of a pine cone: its scales form spirals going two ways. "
     "Count them — you will usually find 8 one way and 13 the other.\n"
     "8 and 13 are Fibonacci numbers: 1, 1, 2, 3, 5, 8, 13, 21 ...",
     "Pine cones (and sunflowers) grow in Fibonacci spirals — packing that nature finds efficient."),
    ("PUZZLE", "Cookie Dough",
     "A round cookie cutter has a radius of 3 cm.\nWhat is the area of one cookie? "
     "(Use A = π r², with π ≈ 3.14.)",
     "About 28.3 cm²: 3.14 × 3 × 3 = 28.26."),
    ("EXPERIMENT", "Ice Fishing",
     "Put an ice cube on a plate and lay a piece of string across the top. "
     "Sprinkle a pinch of salt on it and wait 30 seconds.\nNow lift the string. What happens?",
     "The salt melts a little ice, then it refreezes around the string — so you can lift the cube!"),
    ("PUZZLE", "Magic Square",
     "Place the numbers 1 to 9 in a 3×3 grid so that every row, every column and "
     "both diagonals add up to 15.\nHint: 5 goes in the middle.",
     "2 7 6 / 9 5 1 / 4 3 8 (or any rotation or reflection)."),
    ("FACT", "Sunlight's Journey",
     "Light travels about 300,000 km every second. Sunlight takes about 500 seconds "
     "(8 min 20 s) to reach Earth.\nCAN YOU WORK IT OUT: how far away is the Sun?",
     "About 150,000,000 km: 500 × 300,000 = 150,000,000."),
    ("PUZZLE", "Wrapping Paper",
     "A gift box measures 20 cm × 10 cm × 5 cm.\nWhat is the least amount of paper "
     "(total surface area) needed to cover it with no overlap?",
     "700 cm²: 2 × (20×10 + 20×5 + 10×5) = 2 × 350 = 700."),
    ("EXPERIMENT", "Bending Water",
     "Rub a balloon on your hair or a wool sweater. Turn on a tap to a thin, "
     "steady stream and slowly bring the balloon close — without touching.",
     "The balloon collects static charge, which attracts the water and bends the stream."),
    ("PUZZLE", "What Comes Next?",
     "1, 1, 2, 3, 5, 8, ?\nFind the next number. BONUS: divide each number by the "
     "one before it (8 ÷ 5, 13 ÷ 8 ...). What do you notice?",
     "13 (each number is the sum of the two before). The ratios approach 1.618... — the golden ratio."),
    ("FACT", "A Never-Before Shuffle",
     "A deck of 52 cards can be arranged in 52! ways — about 8 followed by 67 zeros. "
     "That is more than the number of atoms on Earth.\n"
     "So if you shuffle well, your order has almost certainly never existed before!",
     "52! ≈ 8 × 10^67 arrangements, far more than ~10^50 atoms making up the Earth."),
    ("EXPERIMENT", "Holiday Rainbow Glass",
     "Slowly pour, in this order, into a tall clear glass: honey, dish soap, water "
     "coloured red or green, then vegetable oil. Pour gently down the side.",
     "Liquids of different density form layers: the densest (honey) sinks, the lightest (oil) floats on top."),
    ("PUZZLE", "Clock Angles",
     "At 3:00 the hands of a clock make a 90° angle.\nWhat angle do they make at 10:00?",
     "60°. Each hour mark is 360° ÷ 12 = 30°, and 10:00 is 2 hour marks from 12: 2 × 30° = 60°."),
    ("FACT", "The Shortest Day",
     "Around 21 December the Northern Hemisphere has its shortest day, because "
     "Earth's axis is tilted about 23.4°.\nTRY IT: shine a torch on an orange tilted "
     "on a pencil and turn it slowly. Which half gets more light?",
     "The tilt points the Northern Hemisphere away from the Sun in December: shorter days and colder weather."),
    ("PUZZLE", "Ornament Draw",
     "A box holds 3 red and 2 green ornaments. Without looking you pick one.\n"
     "What is the probability it is green?",
     "2/5 (40%): 2 green out of 5 ornaments in total."),
    ("EXPERIMENT", "Candy Cane Race",
     "Put one small candy cane in a cup of warm water and another in a cup of "
     "cold water at the same time.\nPredict first: which dissolves faster? Time them!",
     "The warm one: faster-moving water molecules break the sugar apart more quickly."),
    ("PUZZLE", "One-Stroke Envelope",
     "Can you draw a house-shaped envelope (a square with an X inside and a roof on top) "
     "without lifting your pencil or going over any line twice?\nWhere must you start?",
     "Yes — start at one of the two bottom corners. They are the only points where an odd number of lines meet."),
    ("FACT", "Fold to the Moon",
     "A sheet of paper is about 0.1 mm thick. Each fold doubles the thickness.\n"
     "If you could fold it 42 times, it would be about 440,000 km thick — past the Moon!",
     "0.1 mm × 2^42 ≈ 440,000 km; the Moon is about 384,000 km away. Doubling grows astonishingly fast."),
    ("PUZZLE", "The Secret Message",
     "Julius Caesar hid messages by shifting every letter 3 places along the "
     "alphabet (A→D, B→E ...).\nDecode:  PHUUB FKULVWPDV",
     "MERRY CHRISTMAS — shift every letter 3 places back."),
]
assert len(DAYS) == 24


# ---------------------------------------------------------------- pages
def page(size):
    W, H = size
    im = Image.new("RGB", (W, H), CREAM)
    return im, ImageDraw.Draw(im)


def border(d, W, H, m):
    d.rectangle((m, m, W - m, H - m), outline=GOLD, width=4)
    d.rectangle((m + 18, m + 18, W - m - 18, H - m - 18), outline=LINE, width=2)


def cover(size):
    im, d = page(size); W, H = size
    d.rectangle((0, 0, W, H), fill=NAVY)
    # snow field
    import random
    rnd = random.Random(7)
    for _ in range(90):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        r = rnd.choice((10, 16, 24, 36))
        snowflake(d, x, y, r, (70, 88, 124), w=3)
    snowflake(d, W // 2, int(H * 0.30), int(W * 0.16), GOLD, w=10)
    c = font("cinzel", int(W * 0.075))
    for i, t in enumerate(("STEM", "ADVENT", "CALENDAR")):
        tw = d.textlength(t, font=c)
        d.text(((W - tw) / 2, H * 0.47 + i * W * 0.095), t, font=c, fill=(250, 246, 238))
    s = font("semi", int(W * 0.03))
    t = "24 Days of Math & Science"
    d.text(((W - d.textlength(t, font=s)) / 2, H * 0.78), t, font=s, fill=GOLD)
    s2 = font("body", int(W * 0.021))
    t2 = "Puzzles  ·  Kitchen Experiments  ·  Mind-Blowing Facts"
    d.text(((W - d.textlength(t2, font=s2)) / 2, H * 0.83), t2, font=s2, fill=(214, 220, 232))
    s3 = font("cinzel_r", int(W * 0.022))
    t3 = "MathRelaxing"
    d.text(((W - d.textlength(t3, font=s3)) / 2, H * 0.92), t3, font=s3, fill=(214, 220, 232))
    return im


def how_to(size):
    im, d = page(size); W, H = size; m = int(W * 0.07)
    border(d, W, H, m // 2)
    y = m + 40
    d.text((m + 30, y), "How to Use", font=font("cinzel", int(W * 0.05)), fill=NAVY); y += int(W * 0.09)
    body = font("body", int(W * 0.026))
    steps = [
        ("1", "Print the calendar board and hang it on a wall or the fridge."),
        ("2", "Print the 24 day cards on card stock, cut along the dotted lines and "
              "stack them in order (or hide one in each pocket of a real advent calendar)."),
        ("3", "Each day from 1 to 24 December, open one card. Some are PUZZLES to solve, some "
              "are EXPERIMENTS to try with things from the kitchen, and some are FACTS to amaze."),
        ("4", "Colour in that day's door on the board when you finish."),
        ("5", "Check your answers with the answer key at the back — no peeking early!"),
    ]
    for n, t in steps:
        d.ellipse((m + 30, y, m + 30 + 64, y + 64), fill=RED)
        nf = font("bold", 38); d.text((m + 62 - d.textlength(n, font=nf) / 2, y + 8), n, font=nf, fill=CREAM)
        y = draw_par(d, (m + 130, y + 4), t, body, W - 2 * m - 160) + 40
    y += 20
    d.text((m + 30, y), "Card types", font=font("cinzel", int(W * 0.032)), fill=NAVY); y += int(W * 0.06)
    for k, v in (("PUZZLE", "think it through — answer at the back"),
                 ("EXPERIMENT", "safe, simple, kitchen materials"),
                 ("FACT", "a true, surprising idea + a tiny activity")):
        pill(d, m + 30, y, k, scale=1.3); d.text((m + 360, y + 10), v, font=body, fill=INK); y += 105
    y += 30
    safety = ("Safety: experiments are designed for children with an adult nearby. "
              "Warm water only (never boiling), and do not eat the experiment materials.")
    y = draw_par(d, (m + 30, y), safety, font("light", int(W * 0.021)), W - 2 * m - 60, fill=SUB)
    cy = (y + H - m) // 2
    snowflake(d, W // 2, cy, int(min(W * 0.11, (H - m - y) * 0.35)), GOLD, w=8)
    return im


def pill(d, x, y, kind, scale=1.0):
    f = font("bold", int(30 * scale))
    tw = d.textlength(kind, font=f)
    h = int(58 * scale)
    d.rounded_rectangle((x, y, x + tw + 44 * scale, y + h), radius=h // 2, fill=TYPE_COL[kind])
    d.text((x + 22 * scale, y + (h - f.size) / 2 - 3), kind, font=f, fill=CREAM)


def board(size):
    im, d = page(size); W, H = size; m = int(W * 0.06)
    border(d, W, H, m // 2)
    tf = font("cinzel", int(W * 0.055))
    t = "STEM ADVENT"
    d.text(((W - d.textlength(t, font=tf)) / 2, m + 30), t, font=tf, fill=NAVY)
    sf = font("semi", int(W * 0.022)); t2 = "Colour a door each day you complete a card"
    d.text(((W - d.textlength(t2, font=sf)) / 2, m + 30 + W * 0.075), t2, font=sf, fill=SUB)
    cols, rows = 4, 6
    gx0, gy0 = m + 40, m + int(W * 0.17)
    gw, gh = W - 2 * (m + 40), H - gy0 - m - 60
    cw, ch = gw / cols, gh / rows
    order = [3, 17, 9, 22, 12, 1, 20, 7, 15, 24, 5, 11, 18, 2, 14, 8, 23, 10, 6, 19, 13, 21, 4, 16]
    palette = [NAVY, RED, PINE]
    nf = font("cinzel", int(min(cw, ch) * 0.42))
    for i, n in enumerate(order):
        r, c = divmod(i, cols)
        x0, y0 = gx0 + c * cw + 12, gy0 + r * ch + 12
        x1, y1 = x0 + cw - 24, y0 + ch - 24
        col = palette[(r + c) % 3]
        d.rounded_rectangle((x0, y0, x1, y1), radius=26, outline=col, width=7)
        snowflake(d, x1 - 44, y0 + 44, 22, GOLD, w=3)
        s = str(n); tw = d.textlength(s, font=nf)
        d.text(((x0 + x1 - tw) / 2, (y0 + y1) / 2 - nf.size * 0.62), s, font=nf, fill=col)
    return im


def card(d, box, day, kind, title, body, W):
    x0, y0, x1, y1 = box
    # dashed cut line
    for x in range(int(x0), int(x1), 26):
        d.line((x, y0, x + 12, y0), fill=(180, 172, 158), width=2); d.line((x, y1, x + 12, y1), fill=(180, 172, 158), width=2)
    for y in range(int(y0), int(y1), 26):
        d.line((x0, y, x0, y + 12), fill=(180, 172, 158), width=2); d.line((x1, y, x1, y + 12), fill=(180, 172, 158), width=2)
    p = 46; ix0, iy0, ix1 = x0 + p, y0 + p, x1 - p
    col = TYPE_COL[kind]
    d.rounded_rectangle((ix0 - 10, iy0 - 10, ix1 + 10, y1 - p + 10), radius=30, outline=col, width=5)
    # day badge
    bd = 175
    d.ellipse((ix0 + 10, iy0 + 10, ix0 + 10 + bd, iy0 + 10 + bd), fill=col)
    nf = font("cinzel", 96); s = str(day)
    d.text((ix0 + 10 + (bd - d.textlength(s, font=nf)) / 2, iy0 + 10 + bd / 2 - 66), s, font=nf, fill=CREAM)
    pill(d, ix0 + 215, iy0 + 30, kind, scale=1.25)
    dl = font("semi", 34); d.text((ix0 + 218, iy0 + 118), "DECEMBER", font=dl, fill=SUB)
    snowflake(d, ix1 - 60, iy0 + 85, 42, GOLD, w=5)
    tf = font("cinzel", 68)
    y = draw_par(d, (ix0 + 14, iy0 + 225), title, tf, ix1 - ix0 - 28, fill=INK, lh=1.12) + 14
    d.line((ix0 + 14, y, ix0 + 170, y), fill=GOLD, width=5); y += 34
    bf = font("body", 46)
    y = draw_par(d, (ix0 + 14, y), body, bf, ix1 - ix0 - 28, fill=INK, lh=1.32) + 30
    # writing / drawing area fills the rest of the card
    yb = y1 - p - 30
    if yb - y > 150:
        label = {"PUZZLE": "My answer:", "EXPERIMENT": "What I observed:", "FACT": "Draw it:"}[kind]
        lf = font("semi", 36)
        d.text((ix0 + 14, y), label, font=lf, fill=col); y += 62
        if title == "Magic Square":
            g = min(ix1 - ix0 - 28, yb - y) * 0.9; gx = (ix0 + ix1 - g) / 2
            for k in range(4):
                d.line((gx, y + k * g / 3, gx + g, y + k * g / 3), fill=NAVY, width=4)
                d.line((gx + k * g / 3, y, gx + k * g / 3, y + g), fill=NAVY, width=4)
            c = font("cinzel", int(g / 5)); t = "5"
            d.text((gx + g / 2 - d.textlength(t, font=c) / 2, y + g / 2 - c.size * 0.62), t, font=c, fill=SUB)
        elif kind == "FACT":
            d.rounded_rectangle((ix0 + 14, y, ix1 - 14, yb), radius=18, outline=LINE, width=3)
        else:
            ly = y + 58
            while ly < yb:
                d.line((ix0 + 14, ly, ix1 - 14, ly), fill=LINE, width=3); ly += 72


def card_pages(size):
    W, H = size
    pages = []
    for p in range(6):
        im, d = page(size)
        mx, my = int(W * 0.03), int(H * 0.03)
        cw, ch = (W - 2 * mx) / 2, (H - 2 * my) / 2
        for k in range(4):
            i = p * 4 + k
            r, c = divmod(k, 2)
            box = (mx + c * cw, my + r * ch, mx + (c + 1) * cw, my + (r + 1) * ch)
            kind, title, body, _ = DAYS[i]
            card(d, box, i + 1, kind, title, body, W)
        pages.append(im)
    return pages


def answer_pages(size):
    W, H = size; m = int(W * 0.07)
    pages, i = [], 0
    while i < 24:
        im, d = page(size); border(d, W, H, m // 2)
        d.text((m + 30, m + 30), "Answer Key", font=font("cinzel", int(W * 0.05)), fill=NAVY)
        y = m + 30 + int(W * 0.09)
        bf = font("body", int(W * 0.019)); hf = font("bold", int(W * 0.02))
        while i < 24:
            kind, title, _, ans = DAYS[i]
            need = 60 + len(wrap(d, ans, bf, W - 2 * m - 200)) * int(bf.size * 1.38) + 34
            if y + need > H - m - 20:
                break
            d.ellipse((m + 30, y, m + 30 + 70, y + 70), fill=TYPE_COL[kind])
            s = str(i + 1); nf = font("bold", 34)
            d.text((m + 65 - d.textlength(s, font=nf) / 2, y + 13), s, font=nf, fill=CREAM)
            d.text((m + 130, y + 2), title, font=hf, fill=INK)
            y = draw_par(d, (m + 130, y + 2 + int(hf.size * 1.5)), ans, bf, W - 2 * m - 200, fill=INK) + 34
            i += 1
        pages.append(im)
    return pages


def terms(size):
    im, d = page(size); W, H = size; m = int(W * 0.08)
    border(d, W, H, m // 2)
    y = m + 40
    d.text((m + 30, y), "Terms of Use", font=font("cinzel", int(W * 0.045)), fill=NAVY); y += int(W * 0.09)
    txt = ("For personal, family and single-classroom use. Print as many copies as your own "
           "household or class needs.\n\nPlease do not resell, share the file, or post it anywhere "
           "the public can download it.\n\nEvery puzzle, fact and illustration in this calendar is "
           "original work by MathRelaxing. The answers were checked by hand; if you ever spot an "
           "error, send a message through the shop and a corrected file will be sent free.\n\n"
           "Happy counting down — and happy discovering!")
    draw_par(d, (m + 30, y), txt, font("body", int(W * 0.022)), W - 2 * m - 60)
    return im


def build(name, inches):
    size = (int(inches[0] * DPI), int(inches[1] * DPI))
    pages = [cover(size), how_to(size), board(size)] + card_pages(size) + answer_pages(size) + [terms(size)]
    tmp = os.path.join(OUT, f"_{name}"); os.makedirs(tmp, exist_ok=True)
    paths = []
    for k, im in enumerate(pages):
        p = os.path.join(tmp, f"p{k:02d}.jpg"); im.save(p, quality=92, dpi=(DPI, DPI)); paths.append(p)
    pdf = os.path.join(OUT, f"STEM_Advent_Calendar_{name}.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print(f"{name}: {len(pages)} pages, {os.path.getsize(pdf)//1024} KB")
    return pdf


if __name__ == "__main__":
    build("Letter", (8.5, 11))
    build("A4", (8.27, 11.69))
