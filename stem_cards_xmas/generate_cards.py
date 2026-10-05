"""
Christmas STEM Challenge Cards — 24 hands-on build / science / motion / math
challenges for classrooms and families (ages 6-12).

Pages: cover, teacher guide, engineering design process poster, materials
checklist, 24 challenge cards (4 per page, cut apart), design journal, data
sheet, challenge-tracker tree, certificate and terms. US Letter + A4 at 300 DPI.

  python generate_cards.py
"""
import os, sys, math, random
from PIL import Image, ImageDraw
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
sys.path.insert(0, os.path.join(REPO, "escape_room_xmas"))
from generate_advent import font, wrap, draw_par, snowflake, CREAM, NAVY, RED, PINE, GOLD, INK, SUB, LINE
from generate_escape import tree, star, gift, ctext, new, frame, text_page

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
DPI = 300
CAT = {"BUILD": RED, "SCIENCE": PINE, "MOTION": NAVY, "MATH": GOLD}

# (category, title, challenge, you need, test it, level up)
CARDS = [
    ("BUILD", "Gumdrop Tree Tower",
     "Build the tallest Christmas-tree tower you can. It must stand on its own for 10 seconds.",
     "20 gumdrops or mini marshmallows, 30 toothpicks, ruler",
     "Measure the height of your tower in centimeters.",
     "Balance a paper star on the top without the tower falling."),
    ("BUILD", "Candy Cane Bridge",
     "Build a paper bridge between two books placed 20 cm apart.",
     "2 sheets of paper, 30 cm of tape, 2 books, coins or candy canes",
     "Add weight one piece at a time. How much does it hold before it sags to the table?",
     "Build it again using only ONE sheet of paper."),
    ("MOTION", "Ornament Parachute",
     "Design a parachute that makes a plastic ornament fall as slowly as possible.",
     "tissue paper or a plastic bag, string, tape, a plastic ornament, timer",
     "Drop it from the same height 3 times. Time each fall and find the average.",
     "Make your parachute land on a paper target."),
    ("MOTION", "Sleigh Ramp",
     "Build a ramp that sends a toy car 'sleigh' as far as possible.",
     "cardboard, books, a toy car, tape, measuring tape",
     "Measure from the end of the ramp to where the sleigh stops.",
     "Try 3 different ramp heights. Record and compare the distances."),
    ("MOTION", "Santa's Zip Line",
     "Make a carrier that slides a small toy Santa down a string zip line.",
     "string, a paper cup, paper clips, a straw, tape, a small toy",
     "Tie the string from high to low. Time the trip from top to bottom.",
     "Carry 2 toys at once without dropping them."),
    ("MOTION", "Elf Catapult",
     "Build a catapult that launches a pom-pom into a stocking or a box.",
     "7 craft sticks, 4 rubber bands, a plastic spoon, pom-poms",
     "10 launches. Score 1 point for each pom-pom that lands inside.",
     "Move the target 50 cm further away and beat your score."),
    ("MATH", "Snowflake Symmetry",
     "Fold and cut a paper snowflake with exactly 6 lines of symmetry, just like a real one.",
     "square paper, scissors, pencil, ruler",
     "Open it up and draw all of its lines of symmetry in pencil.",
     "Real snowflakes always have 6 arms. Find out why."),
    ("BUILD", "Paper Chain Challenge",
     "Make the longest paper chain you can from ONE sheet of paper.",
     "1 sheet of paper, scissors, tape or a glue stick, measuring tape",
     "Estimate the length first. Then measure the finished chain.",
     "How close was your estimate? Can you make it longer?"),
    ("MATH", "Perfect Present Box",
     "Draw a net, cut it out and fold it into a cube gift box with a lid.",
     "card stock, ruler, pencil, scissors, tape, 10 wrapped candies",
     "The box must close with all 10 candies inside.",
     "Find 2 different cube nets that work. (There are 11 in total!)"),
    ("BUILD", "Reindeer Stable",
     "Build a stable with a roof using only index cards. A toy reindeer must fit inside.",
     "10 index cards, 30 cm of tape, a small toy",
     "Place a book on the roof. Does the stable hold it?",
     "Build it with no tape at all, only folds and cuts."),
    ("SCIENCE", "Floating Gift Boat",
     "Make a foil boat that carries as many 'gold coins' as possible.",
     "one 20 x 20 cm piece of foil, coins, a bowl of water",
     "Add coins one at a time until it sinks. Count them.",
     "Change the shape of your boat and beat your record."),
    ("SCIENCE", "Candy Cane Melt",
     "Which water dissolves a candy cane fastest: cold, warm or hot?",
     "3 small candy canes, 3 cups, water, timer (a grown-up handles the hot water)",
     "Predict first. Then time how long each candy cane takes to dissolve.",
     "Try stirring one cup. Does it change the result?"),
    ("SCIENCE", "Static Snow",
     "Use a balloon to lift tiny paper snowflakes without touching them.",
     "a balloon, tissue-paper confetti, a wool sweater or your hair",
     "Rub the balloon, then count how many snowflakes you lift in one go.",
     "Can you make a snowflake 'dance' across the table?"),
    ("SCIENCE", "Save the Snowman",
     "Keep an ice-cube 'snowman' from melting for as long as possible.",
     "ice cubes, cups, cloth, foil, paper, cotton balls",
     "Check every 10 minutes. The last snowman still frozen wins.",
     "Explain why your insulation worked better than the others."),
    ("MATH", "Gumdrop Shapes",
     "Build a cube, a square pyramid and a triangular prism.",
     "gumdrops or mini marshmallows, toothpicks",
     "Count the faces, edges and corners of each shape. Record them in a table.",
     "Check: faces + corners - edges = 2 for every shape. (Euler's formula!)"),
    ("SCIENCE", "Balancing Elf",
     "Make a paper elf that balances on its nose on the tip of your finger.",
     "card stock, scissors, 2 coins or paper clips, tape",
     "Tape the weights to the elf's hands and balance it on a fingertip or pencil.",
     "Can it balance on the rim of a cup? Explain why it works."),
    ("MOTION", "Chimney Marble Drop",
     "Build a marble run so 'Santa' (a marble) takes as LONG as possible to come down the chimney.",
     "paper-towel tubes, cardboard, tape, a marble, timer",
     "Time the marble's trip. The longest time wins.",
     "Make the marble change direction at least 3 times."),
    ("BUILD", "Strong Columns",
     "Which paper column holds the most books: a circle, a square or a triangle?",
     "3 sheets of paper, tape, light books",
     "Stack books one at a time on each column. Record the results.",
     "Build a table with 4 paper legs that holds a stack of books."),
    ("SCIENCE", "Jingle Bell Band",
     "Make an instrument that can play at least 3 different notes.",
     "rubber bands, a box or tub, cups, water, straws",
     "Play a short tune, like the start of 'Jingle Bells'.",
     "Explain what makes a note higher or lower."),
    ("SCIENCE", "Snow Globe Science",
     "Make a snow globe and test how fast the 'snow' falls.",
     "a jar with a lid, water, glitter, dish soap or glycerin, timer",
     "Time the glitter falling in plain water, then with soap or glycerin added.",
     "Which liquid makes the slowest snow? Why?"),
    ("MATH", "Binary Ornament",
     "Spell your initials in binary code with beads to make an ornament.",
     "a pipe cleaner, beads in 2 colors",
     "Letter to number (A=1 ... Z=26), then to binary with place values 16, 8, 4, 2, 1. Dark bead = 1, light bead = 0.",
     "Encode NOEL and ask a friend to decode it."),
    ("BUILD", "Cup Christmas Tree",
     "Build the tallest Christmas tree you can from cups and cards.",
     "20 paper or plastic cups, 10 index cards, measuring tape",
     "It must stand for 10 seconds. Then measure it.",
     "Team of two: each builder may use only one hand."),
    ("SCIENCE", "Rudolph's Shadow",
     "Make a reindeer shadow puppet and change the size of its shadow.",
     "card stock, scissors, a stick, a flashlight, a wall, ruler",
     "Measure the shadow's height with the light at 3 different distances.",
     "Draw a graph: distance from the light vs. shadow height."),
    ("BUILD", "Earthquake Gingerbread House",
     "Build a gingerbread house that survives a 10-second 'earthquake'.",
     "graham crackers or card stock, frosting or tape, a tray",
     "Shake the tray gently for 10 seconds. Is your house still standing?",
     "Add a second floor and test it again."),
]
assert len(CARDS) == 24
STEPS = [("Ask", "What is the problem? What are the rules?"),
         ("Imagine", "Brainstorm lots of ideas."),
         ("Plan", "Draw your design and pick materials."),
         ("Create", "Build it following your plan."),
         ("Test", "Try it out and measure the results."),
         ("Improve", "What could work better? Change it!")]


# ------------------------------------------------------------------ icons
def flask(d, cx, cy, s, col):
    d.rectangle((cx - s * 0.12, cy - s * 0.5, cx + s * 0.12, cy - s * 0.1), outline=col, width=max(3, int(s * 0.06)))
    d.polygon([(cx - s * 0.12, cy - s * 0.1), (cx - s * 0.42, cy + s * 0.45), (cx + s * 0.42, cy + s * 0.45),
               (cx + s * 0.12, cy - s * 0.1)], fill=col)
    d.ellipse((cx - s * 0.12, cy + s * 0.15, cx, cy + s * 0.27), fill=CREAM)
    d.ellipse((cx + s * 0.08, cy + s * 0.25, cx + s * 0.18, cy + s * 0.35), fill=CREAM)


def sled(d, cx, cy, s, col):
    w = max(3, int(s * 0.07))
    d.rounded_rectangle((cx - s * 0.4, cy - s * 0.25, cx + s * 0.3, cy + s * 0.05), radius=int(s * 0.08), fill=col)
    d.line((cx - s * 0.45, cy + s * 0.28, cx + s * 0.35, cy + s * 0.28), fill=col, width=w)
    d.arc((cx + s * 0.2, cy + s * 0.02, cx + s * 0.5, cy + s * 0.32), 270, 90, fill=col, width=w)
    for x in (-0.25, 0.15):
        d.line((cx + s * x, cy + s * 0.05, cx + s * x, cy + s * 0.28), fill=col, width=w)
    for k in range(3):  # speed lines
        y = cy - s * 0.18 + k * s * 0.12
        d.line((cx - s * 0.9, y, cx - s * 0.55, y), fill=col, width=w)


def icon(d, cat, cx, cy, s, col):
    if cat == "BUILD":
        tree(d, cx, cy + s * 0.48, s * 0.95, col)
    elif cat == "SCIENCE":
        flask(d, cx, cy, s, col)
    elif cat == "MOTION":
        sled(d, cx + s * 0.15, cy, s, col)
    else:
        snowflake(d, cx, cy, s * 0.48, col, w=max(3, int(s * 0.06)))


# ------------------------------------------------------------------ cards
def card(d, box, n, c, W):
    cat, title, chal, need, test, lvl = c
    x0, y0, x1, y1 = box; col = CAT[cat]
    pad = int(W * 0.022); cw = x1 - x0
    d.rounded_rectangle(box, radius=34, fill=(255, 255, 255), outline=col, width=8)
    bh = int(cw * 0.2)
    d.rounded_rectangle((x0, y0, x1, y0 + bh), radius=34, fill=col)
    d.rectangle((x0, y0 + bh - 40, x1, y0 + bh), fill=col)
    r = bh * 0.36; cx = x0 + pad + r; cy = y0 + bh / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CREAM)
    ctext(d, cx, cy - r * 0.62, str(n), font("cinzel", int(r * 0.95)), col)
    d.text((cx + r + 30, cy - int(W * 0.013)), cat, font=font("bold", int(W * 0.019)), fill=CREAM)
    icon(d, cat, x1 - pad - bh * 0.4, cy, bh * 0.6, CREAM)
    tx = x0 + pad; tw = cw - 2 * pad
    y = y0 + bh + int(W * 0.018)
    tf = font("cinzel", int(W * 0.033))
    for ln in wrap(d, title, tf, tw):
        d.text((tx, y), ln, font=tf, fill=NAVY); y += int(tf.size * 1.2)
    y += int(W * 0.008)
    bf = font("body", int(W * 0.0205)); lf = font("bold", int(W * 0.0175))
    for lab, txt in (("THE CHALLENGE", chal), ("YOU NEED", need), ("TEST IT", test)):
        d.text((tx, y), lab, font=lf, fill=col if cat != "MATH" else (150, 112, 40)); y += int(lf.size * 1.5)
        y = draw_par(d, (tx, y), txt, bf, tw, lh=1.32) + int(W * 0.012)
    # level-up strip pinned to the bottom
    lines = wrap(d, lvl, bf, tw - 40)
    lh = int(bf.size * 1.32)
    ly = y1 - pad - len(lines) * lh - int(lf.size * 1.5) - 30
    assert ly > y, f"card {n} text overflow"
    d.rounded_rectangle((x0 + pad - 14, ly - 18, x1 - pad + 14, y1 - pad + 6), radius=20, fill=(246, 240, 226))
    star(d, tx + 18, ly + lf.size * 0.55, lf.size * 0.65, GOLD)
    d.text((tx + 46, ly), "LEVEL UP", font=lf, fill=(150, 112, 40))
    draw_par(d, (tx + 6, ly + int(lf.size * 1.5)), lvl, bf, tw - 40, lh=1.32)


def card_pages(size):
    W, H = size; pages = []
    m = int(W * 0.045); g = int(W * 0.03)
    cw, ch = (W - 2 * m - g) / 2, (H - 2 * m - g) / 2
    for p in range(6):
        im, d = new(size)
        for i in range(4):
            r, c = divmod(i, 2)
            x0, y0 = m + c * (cw + g), m + r * (ch + g)
            n = p * 4 + i + 1
            card(d, (int(x0), int(y0), int(x0 + cw), int(y0 + ch)), n, CARDS[n - 1], W)
        # dashed cut guides
        for x in range(0, W, 30):
            d.line((x, H / 2, x + 14, H / 2), fill=LINE, width=3)
        for y in range(0, H, 30):
            d.line((W / 2, y, W / 2, y + 14), fill=LINE, width=3)
        pages.append(im)
    return pages


# ------------------------------------------------------------------ other pages
def cover(size):
    im, d = new(size); W, H = size
    d.rectangle((0, 0, W, H), fill=NAVY)
    rnd = random.Random(8)
    for _ in range(70):
        snowflake(d, rnd.randint(0, W), rnd.randint(0, H), rnd.choice((10, 16, 24)), (60, 76, 110), w=3)
    # four category tiles
    s = W * 0.26; gap = W * 0.04; gx = (W - 2 * s - gap) / 2; gy = H * 0.1
    for i, cat in enumerate(("BUILD", "SCIENCE", "MOTION", "MATH")):
        r, c = divmod(i, 2)
        x0, y0 = gx + c * (s + gap), gy + r * (s + gap)
        d.rounded_rectangle((x0, y0, x0 + s, y0 + s), radius=50, fill=CAT[cat] if cat != "MOTION" else (52, 78, 128))
        icon(d, cat, x0 + s / 2, y0 + s * 0.42, s * 0.5, CREAM)
        ctext(d, x0 + s / 2, y0 + s * 0.76, cat, font("bold", int(W * 0.03)), CREAM)
    y = gy + 2 * s + gap + H * 0.05
    ctext(d, W / 2, y, "CHRISTMAS", font("cinzel", int(W * 0.08)), CREAM)
    ctext(d, W / 2, y + W * 0.1, "STEM CHALLENGES", font("cinzel", int(W * 0.072)), GOLD)
    ctext(d, W / 2, y + W * 0.205, "24 hands-on challenge cards", font("semi", int(W * 0.036)), CREAM)
    ctext(d, W / 2, H * 0.89, "ages 6-12  ·  classroom & home  ·  design journal included", font("body", int(W * 0.024)), (210, 216, 230))
    ctext(d, W / 2, H * 0.94, "MathRelaxing", font("cinzel_r", int(W * 0.024)), (210, 216, 230))
    return im


def guide(size):
    return text_page(size, "Teacher & Parent Guide", [
        ("What this is", "24 Christmas challenge cards that turn everyday materials into engineering, science, motion and "
                         "math investigations. Each card has a challenge, a materials list, a way to test the result and "
                         "a Level Up for fast finishers."),
        ("How to use the cards", "Print the card pages on card stock and cut along the dotted lines. Use one card a day as a "
                                 "December countdown, set up stations for a class party, or let children pick a card on a "
                                 "snowy afternoon. Most challenges take 20-45 minutes."),
        ("The design journal", "Print one journal page per challenge. Children follow the engineering design process: ask, "
                               "imagine, plan, create, test and improve. The data sheet is for recording measurements and "
                               "comparing trials."),
        ("Ages and groups", "Designed for ages 6-12. Younger children work well in pairs with an adult; older children can "
                            "compete in teams and use the Level Up as the real challenge."),
        ("Safety", "An adult should handle hot water, scissors for young children and anything with small parts. Food "
                   "items in the challenges are for building, not for eating afterwards."),
        ("Track progress", "Color an ornament on the challenge tree each time a card is completed. Finish all 24 to earn "
                           "the Christmas STEM Engineer certificate!"),
    ])


def process(size):
    im, d = new(size); W, H = size
    frame(d, W, H, PINE)
    ctext(d, W / 2, int(H * 0.07), "The Engineering", font("cinzel", int(W * 0.058)), NAVY)
    ctext(d, W / 2, int(H * 0.07) + int(W * 0.075), "Design Process", font("cinzel", int(W * 0.058)), NAVY)
    cx, cy, R = W / 2, H * 0.465, W * 0.23
    cols = [RED, PINE, GOLD, NAVY, RED, PINE]
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=LINE, width=14)
    snowflake(d, cx, cy, W * 0.07, GOLD, w=8)
    r = W * 0.09
    for k, (t, _) in enumerate(STEPS):
        a = -math.pi / 2 + k * math.pi / 3
        px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        d.ellipse((px - r, py - r, px + r, py + r), fill=cols[k], outline=CREAM, width=10)
        ctext(d, px, py - r * 0.6, str(k + 1), font("cinzel", int(r * 0.5)), CREAM)
        ctext(d, px, py + r * 0.02, t, font("bold", int(W * 0.026)), CREAM)
    # legend: 2 columns x 3 rows
    y0 = H * 0.725; cw = W * 0.41; lx = [W * 0.09, W * 0.09 + cw + W * 0.0]
    for k, (t, s_) in enumerate(STEPS):
        c, rr = divmod(k, 3)
        x = lx[c]; y = y0 + rr * H * 0.07
        d.ellipse((x, y, x + 70, y + 70), fill=cols[k])
        ctext(d, x + 35, y + 8, str(k + 1), font("bold", 44), CREAM)
        d.text((x + 95, y - 4), t, font=font("bold", int(W * 0.022)), fill=NAVY)
        draw_par(d, (x + 95, y + int(W * 0.03)), s_, font("body", int(W * 0.018)), cw - 120, fill=INK)
    return im


def materials(size):
    im, d = new(size); W, H = size
    frame(d, W, H, RED)
    d.text((int(W * 0.09), int(H * 0.07)), "Materials Checklist", font=font("cinzel", int(W * 0.05)), fill=NAVY)
    draw_par(d, (int(W * 0.09), int(H * 0.07) + int(W * 0.075)),
             "Most of these are already at home or in the classroom. Tick them off as you collect them.",
             font("body", int(W * 0.021)), int(W * 0.82), fill=SUB)
    groups = [("Paper & card", ["printer paper", "card stock", "index cards", "tissue paper", "paper cups",
                                "paper-towel tubes", "cardboard", "aluminum foil"]),
              ("Craft supplies", ["tape", "glue stick", "scissors", "string", "rubber bands", "craft sticks",
                                  "paper clips", "straws", "pipe cleaners", "beads (2 colors)", "pom-poms", "glitter"]),
              ("Kitchen", ["gumdrops or mini marshmallows", "toothpicks", "candy canes", "graham crackers",
                           "frosting", "ice cubes", "cups and a bowl", "dish soap or glycerin", "jar with a lid"]),
              ("Tools & extras", ["ruler", "measuring tape", "timer", "flashlight", "balloon", "coins", "marble",
                                  "toy car", "small toys", "plastic ornament", "plastic spoon", "light books"])]
    colx = [int(W * 0.09), int(W * 0.52)]; y0 = int(H * 0.2)
    ys = [y0, y0]
    for i, (g, items) in enumerate(groups):
        c = i % 2; x = colx[c]; y = ys[c]
        d.text((x, y), g, font=font("bold", int(W * 0.026)), fill=RED); y += int(W * 0.045)
        for it in items:
            s = int(W * 0.022)
            d.rounded_rectangle((x, y + 6, x + s, y + 6 + s), radius=6, outline=NAVY, width=4)
            d.text((x + s + 24, y), it, font=font("body", int(W * 0.021)), fill=INK); y += int(W * 0.036)
        ys[c] = y + int(W * 0.04)
    return im


def journal(size):
    im, d = new(size); W, H = size
    frame(d, W, H, NAVY)
    m = int(W * 0.09); x1 = W - m
    d.text((m, int(H * 0.06)), "Design Journal", font=font("cinzel", int(W * 0.05)), fill=NAVY)
    f = font("bold", int(W * 0.021)); bf = font("body", int(W * 0.02))
    y = int(H * 0.06) + int(W * 0.08)
    d.text((m, y), "Name: ____________________    Challenge #: ____    Date: __________", font=bf, fill=INK)
    y += int(W * 0.06)
    blocks = [("1  ASK", "What do I need to do? What are the rules?", 0.07),
              ("2  IMAGINE & PLAN", "Draw and label your design. List your materials.", 0.24),
              ("3  CREATE & TEST", "What happened when you tested it? Write your measurements.", 0.11),
              ("4  IMPROVE", "What did you change? Did it work better?", 0.09)]
    cols = [RED, PINE, GOLD, NAVY]
    for (h, q, frac), col in zip(blocks, cols):
        bh = int(H * frac)
        d.rounded_rectangle((m, y, x1, y + bh + 90), radius=24, outline=col, width=6, fill=(255, 255, 255))
        d.rounded_rectangle((m, y, m + int(W * 0.32), y + 70), radius=24, fill=col)
        d.text((m + 30, y + 14), h, font=f, fill=CREAM)
        d.text((m + int(W * 0.34), y + 18), q, font=font("body", int(W * 0.017)), fill=SUB)
        if "PLAN" in h:  # dot grid for sketching
            for gx in range(m + 40, x1 - 20, 60):
                for gy in range(y + 110, y + bh + 70, 60):
                    d.ellipse((gx - 3, gy - 3, gx + 3, gy + 3), fill=LINE)
        else:
            for ly in range(y + 150, y + bh + 70, 80):
                d.line((m + 40, ly, x1 - 40, ly), fill=LINE, width=3)
        y += bh + 90 + int(H * 0.018)
    stars = "How did I do?"
    d.text((m, y + 10), stars, font=f, fill=NAVY)
    for k in range(5):
        star(d, m + int(W * 0.25) + k * 90, y + 32, 34, LINE)
    return im


def data_sheet(size):
    im, d = new(size); W, H = size
    frame(d, W, H, PINE)
    m = int(W * 0.09); x1 = W - m
    d.text((m, int(H * 0.06)), "Data Sheet", font=font("cinzel", int(W * 0.05)), fill=NAVY)
    bf = font("body", int(W * 0.02))
    y = int(H * 0.06) + int(W * 0.08)
    d.text((m, y), "Challenge: ______________________________   My prediction: ______________", font=bf, fill=INK)
    y += int(W * 0.07)
    heads = ["Trial", "What I changed", "Measurement", "Notes"]
    fr = [0.12, 0.38, 0.22, 0.28]
    xs = [m]
    for f_ in fr:
        xs.append(xs[-1] + (x1 - m) * f_)
    rh = int(H * 0.05)
    d.rectangle((m, y, x1, y + rh), fill=PINE)
    for i, h in enumerate(heads):
        d.text((xs[i] + 20, y + 30), h, font=font("bold", int(W * 0.019)), fill=CREAM)
    for r in range(1, 9):
        yy = y + r * rh
        d.rectangle((m, yy, x1, yy + rh), outline=LINE, width=3, fill=(255, 255, 255) if r % 2 else (244, 249, 246))
        ctext(d, (xs[0] + xs[1]) / 2, yy + 28, str(r), font("bold", int(W * 0.02)), PINE)
    for x in xs[1:-1]:
        d.line((x, y, x, y + 9 * rh), fill=LINE, width=3)
    # bar-graph grid
    gy = y + 9 * rh + int(H * 0.04)
    d.text((m, gy), "Graph my results", font=font("bold", int(W * 0.024)), fill=RED)
    gy += int(W * 0.05); gb = H - int(H * 0.08)
    for k in range(0, int(gb - gy) + 1, 50):
        d.line((m + 80, gy + k, x1, gy + k), fill=LINE, width=2)
    for k in range(0, int(x1 - m - 80) + 1, 50):
        d.line((m + 80 + k, gy, m + 80 + k, gb), fill=LINE, width=2)
    d.line((m + 80, gy, m + 80, gb), fill=NAVY, width=6); d.line((m + 80, gb, x1, gb), fill=NAVY, width=6)
    return im


def tracker(size):
    im, d = new(size); W, H = size
    frame(d, W, H, GOLD)
    ctext(d, W / 2, int(H * 0.06), "My Challenge Tree", font("cinzel", int(W * 0.058)), NAVY)
    ctext(d, W / 2, int(H * 0.06) + int(W * 0.08), "Color an ornament for every challenge you complete",
          font("semi", int(W * 0.024)), RED)
    # big tree made of 6 rows of ornaments: 1,2,3,4,6,8 = 24
    top, bot = H * 0.2, H * 0.84; cx = W / 2
    d.polygon([(cx, top), (cx - W * 0.4, bot), (cx + W * 0.4, bot)], fill=(214, 232, 220))
    d.rectangle((cx - W * 0.05, bot, cx + W * 0.05, bot + H * 0.06), fill=(150, 110, 70))
    star(d, cx, top - 10, W * 0.06, GOLD)
    rows = [1, 2, 3, 5, 6, 7]; n = 1
    for i, k in enumerate(rows):
        y = top + (bot - top) * (0.14 + i * 0.155)
        half = (y - top) / (bot - top) * W * 0.4 * 0.86
        for j in range(k):
            x = cx if k == 1 else cx - half + j * 2 * half / (k - 1)
            r = W * 0.04
            d.line((x, y - r - 18, x, y - r), fill=SUB, width=4)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=[RED, PINE, GOLD, NAVY][n % 4], width=8)
            ctext(d, x, y - r * 0.55, str(n), font("bold", int(r * 0.9)), NAVY)
            n += 1
    assert n == 25
    return im


def certificate(size):
    im, d = new(size); W, H = size
    frame(d, W, H, GOLD)
    d.rectangle((int(W * 0.08), int(H * 0.08), W - int(W * 0.08), H - int(H * 0.08)), outline=PINE, width=4)
    ctext(d, W / 2, int(H * 0.15), "CERTIFICATE", font("cinzel", int(W * 0.075)), NAVY)
    ctext(d, W / 2, int(H * 0.15) + int(W * 0.1), "Christmas STEM Engineer", font("semi", int(W * 0.036)), RED)
    for i, cat in enumerate(("BUILD", "SCIENCE", "MOTION", "MATH")):
        x = W * (0.29 + i * 0.14)
        icon(d, cat, x, H * 0.38, W * 0.08, CAT[cat])
    ctext(d, W / 2, int(H * 0.48), "This certifies that", font("body", int(W * 0.026)), SUB)
    d.line((int(W * 0.2), int(H * 0.56), W - int(W * 0.2), int(H * 0.56)), fill=NAVY, width=4)
    ctext(d, W / 2, int(H * 0.59), "completed the Christmas STEM Challenges", font("body", int(W * 0.026)), INK)
    ctext(d, W / 2, int(H * 0.59) + int(W * 0.045), "and showed the skills of a true engineer!", font("body", int(W * 0.026)), INK)
    ctext(d, W / 2, int(H * 0.73), "Challenges completed:  ____ / 24", font("bold", int(W * 0.028)), NAVY)
    d.line((int(W * 0.16), int(H * 0.84), int(W * 0.44), int(H * 0.84)), fill=NAVY, width=3)
    d.line((int(W * 0.56), int(H * 0.84), int(W * 0.84), int(H * 0.84)), fill=NAVY, width=3)
    ctext(d, W * 0.30, int(H * 0.85), "Date", font("body", int(W * 0.02)), SUB)
    ctext(d, W * 0.70, int(H * 0.85), "Signed", font("body", int(W * 0.02)), SUB)
    return im


def terms(size):
    return text_page(size, "Terms of Use", [
        ("", "For personal, family and single-classroom use. Print as many copies as your own household or class needs.\n\n"
             "Please do not resell, share the file, or post it anywhere the public can download it. Teachers: one "
             "purchase covers one classroom.\n\nAll challenges and illustrations are original work by MathRelaxing. If "
             "you ever spot a problem, send a message through the shop and a corrected file will be sent free.\n\n"
             "Merry Christmas and happy building!"),
    ])


def build(name, inches):
    size = (int(inches[0] * DPI), int(inches[1] * DPI))
    pages = [cover(size), guide(size), process(size), materials(size)]
    pages += card_pages(size)
    pages += [journal(size), data_sheet(size), tracker(size), certificate(size), terms(size)]
    tmp = os.path.join(OUT, f"_{name}"); os.makedirs(tmp, exist_ok=True)
    paths = []
    for k, im in enumerate(pages):
        p = os.path.join(tmp, f"p{k:02d}.jpg"); im.save(p, quality=92, dpi=(DPI, DPI)); paths.append(p)
    pdf = os.path.join(OUT, f"Christmas_STEM_Challenge_Cards_{name}.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print(f"{name}: {len(pages)} pages, {os.path.getsize(pdf)//1024} KB")


if __name__ == "__main__":
    build("Letter", (8.5, 11))
    build("A4", (8.27, 11.69))
