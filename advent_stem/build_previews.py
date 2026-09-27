"""Etsy listing images (2000x2000) for the STEM Advent Calendar, composited from
the real rendered pages in out/_Letter."""
import os
from PIL import Image, ImageDraw, ImageFilter
import generate_advent as G

HERE = os.path.dirname(os.path.abspath(__file__))
PG = os.path.join(HERE, "out", "_Letter")
OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)
S = 2000
BG_TOP, BG_BOT = (244, 238, 226), (226, 216, 198)


def bg():
    im = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / S
        d.line((0, y, S, y), fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(BG_TOP, BG_BOT)))
    return im


def pg(n):
    return Image.open(os.path.join(PG, f"p{n:02d}.jpg")).convert("RGB")


def place(canvas, img, w, xy, angle=0, shadow=True):
    im = img.copy(); im.thumbnail((w, w * 2))
    if angle:
        im = im.convert("RGBA").rotate(angle, expand=True, resample=Image.BICUBIC)
    else:
        im = im.convert("RGBA")
    x, y = xy
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        a = im.split()[-1].point(lambda p: 90 if p > 10 else 0)
        sh.paste((30, 24, 18, 255), (x + 18, y + 26), a)
        canvas.paste(sh.filter(ImageFilter.GaussianBlur(22)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
    canvas.paste(im, (x, y), im)


def banner(d, text, sub=None, y=90):
    f = G.font("cinzel", 96)
    d.text(((S - d.textlength(text, font=f)) / 2, y), text, font=f, fill=G.NAVY)
    if sub:
        s = G.font("semi", 50)
        d.text(((S - d.textlength(sub, font=s)) / 2, y + 125), sub, font=s, fill=G.RED)


def hero():
    c = bg(); d = ImageDraw.Draw(c)
    place(c, pg(3), 760, (1080, 520), angle=-8)
    place(c, pg(2), 760, (140, 470), angle=5)
    place(c, pg(0), 820, (590, 360))
    d.rounded_rectangle((520, 1780, 1480, 1920), radius=70, fill=G.RED)
    t = "24 DAYS  ·  PRINTABLE"; f = G.font("bold", 58)
    d.text(((S - d.textlength(t, font=f)) / 2, 1812), t, font=f, fill=G.CREAM)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "12 pages · US Letter + A4")
    items = [(0, "Cover"), (1, "How to use"), (2, "Calendar board"),
             (3, "24 day cards"), (9, "Answer key"), (11, "Terms")]
    w = 520
    for i, (n, lab) in enumerate(items):
        r, col = divmod(i, 3)
        x = 130 + col * 600; y = 400 + r * 790
        place(c, pg(n), w, (x, y))
        f = G.font("semi", 44)
        d.text((x + (w - d.textlength(lab, font=f)) / 2, y + 690), lab, font=f, fill=G.INK)
    return c


def cards_close():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "A New Discovery Every Day", "Puzzles · Experiments · Facts")
    sheet = pg(5)
    W, H = sheet.size
    left = sheet.crop((0, 0, W // 2, H // 2)); right = sheet.crop((W // 2, H // 2, W, H))
    place(c, left, 820, (150, 420), angle=3)
    place(c, right, 820, (1030, 480), angle=-3)
    return c


def board_img():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Countdown Calendar Board", "Colour a door each day")
    place(c, pg(2), 1150, (425, 380))
    return c


def details():
    c = Image.new("RGB", (S, S), G.NAVY); d = ImageDraw.Draw(c)
    import random
    rnd = random.Random(3)
    for _ in range(60):
        G.snowflake(d, rnd.randint(0, S), rnd.randint(0, S), rnd.choice((12, 20, 30)), (60, 78, 112), w=3)
    f = G.font("cinzel", 100)
    t = "Everything You Get"; d.text(((S - d.textlength(t, font=f)) / 2, 170), t, font=f, fill=G.CREAM)
    n = {k: sum(1 for x in G.DAYS if x[0] == k) for k in ("PUZZLE", "EXPERIMENT", "FACT")}
    rows = [("24", "daily STEM cards"), (str(n["PUZZLE"]), "logic & math puzzles"),
            (str(n["EXPERIMENT"]), "kitchen-safe experiments"), (str(n["FACT"]), "mind-blowing science facts"), ("1", "hangable countdown board"),
            ("24", "worked answers in the key"), ("2", "sizes: US Letter + A4")]
    nf = G.font("cinzel", 96); tf = G.font("body", 62)
    y = 420
    for n, t in rows:
        d.ellipse((330, y, 470, y + 140), fill=G.GOLD)
        d.text((400 - d.textlength(n, font=nf) / 2, y + 12), n, font=nf, fill=G.NAVY)
        d.text((530, y + 34), t, font=tf, fill=G.CREAM); y += 190
    return c


def ages():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Perfect For", None, y=180)
    items = ["Families counting down to Christmas", "Homeschool December units",
             "Classroom morning work & early finishers", "Curious kids ages 8–14",
             "A screen-free holiday tradition"]
    f = G.font("body", 70); y = 480
    for t in items:
        G.snowflake(d, 330, y + 42, 40, G.RED, w=6)
        d.text((420, y), t, font=f, fill=G.INK); y += 210
    d.rounded_rectangle((420, 1650, 1580, 1820), radius=85, fill=G.PINE)
    t = "Instant download · print at home"; s = G.font("bold", 56)
    d.text(((S - d.textlength(t, font=s)) / 2, 1705), t, font=s, fill=G.CREAM)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, inside, cards_close, board_img, details, ages), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg")
        fn().save(p, quality=90); print("wrote", p)
