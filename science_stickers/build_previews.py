"""Etsy listing images (2000x2000) for the digital Science Sticker Collection."""
import os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from designs import DESIGNS
from lib import die_cut

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); ART = os.path.join(OUT, "art"); PV = os.path.join(OUT, "previews"); os.makedirs(PV, exist_ok=True)
S = 2000; FD = os.path.join(HERE, "fonts")
INK = (29, 39, 66); CREAM = (251, 245, 233); GOLD = (196, 140, 50); CORAL = (226, 105, 79); TEAL = (42, 157, 143); NAVY = (36, 50, 89)
_CACHE = {}


def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def shadowed(n, w, rot=0):
    if n not in _CACHE:
        _CACHE[n] = die_cut(Image.open(os.path.join(ART, f"{n}.png")), shadow=True)
    im = _CACHE[n].copy(); im.thumbnail((w, w), Image.LANCZOS)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else im


def bg(col=(236, 230, 218)):
    im = Image.new("RGB", (S, S), col); d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / S; d.line((0, y, S, y), fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((242, 237, 227), col)))
    return im.convert("RGBA")


def ctext(d, y, s, f, fill):
    d.text(((S - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)


def pill(d, s, y, fill=CORAL, size=54):
    f = F("Inter-800.ttf", size); w = d.textlength(s, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 130), radius=65, fill=fill)
    d.text(((S - w) / 2, y + 30), s, font=f, fill=CREAM)


def hero():
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, "Science Stickers", F("Fraunces-800.ttf", 150), INK)
    ctext(d, 280, "24 printable designs  ·  physics  ·  chemistry  ·  math", F("Inter-700.ttf", 50), GOLD)
    rnd = random.Random(4); names = list(DESIGNS)
    slots = [(240 + k * 380 + (r % 2) * 0, 520 + r * 315) for r in range(4) for k in range(5)]
    rnd.shuffle(names)
    for (x, y), n in zip(slots, names):
        im = shadowed(n, 320, rnd.uniform(-8, 8)); c.alpha_composite(im, (int(x - im.width / 2 + rnd.uniform(-15, 15)), int(y - im.height / 2 + rnd.uniform(-10, 10))))
    pill(d, "PRINT  ·  CRICUT  ·  GOODNOTES", 1800)
    return c


def theme(group, title, sub, col):
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, title, F("Fraunces-800.ttf", 140), INK); ctext(d, 270, sub, F("Inter-700.ttf", 48), col)
    ns = [n for n, (g, t, f) in DESIGNS.items() if g == group]
    for i, n in enumerate(ns):
        r, k = divmod(i, 4); im = shadowed(n, 420)
        x = 260 + k * 490 - im.width / 2; y = 680 + r * 620 - im.height / 2
        c.alpha_composite(im, (int(x), int(y)))
        t = DESIGNS[n][1].replace("Ge Ni U S", "Genius"); f = F("Inter-700.ttf", 38)
        d.text((260 + k * 490 - d.textlength(t, font=f) / 2, 935 + r * 620), t, font=f, fill=(110, 100, 90))
    pill(d, f"8 {title.split()[0].upper()} STICKERS", 1800, fill=col)
    return c


def tablet(c, x, y, w, h):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x, y, x + w, y + h), radius=60, fill=(40, 42, 50))
    d.rounded_rectangle((x + 40, y + 40, x + w - 40, y + h - 40), radius=20, fill=(253, 251, 246))
    for yy in range(y + 120, y + h - 60, 46):
        d.line((x + 90, yy, x + w - 90, yy), fill=(214, 224, 236), width=3)
    d.text((x + 90, y + 60), "Physics notes", font=F("Fraunces-600i.ttf", 52), fill=INK)
    for n, (fx, fy, s, r) in zip(("atom", "emc2", "schrodinger", "pi_badge", "dna"),
                                ((0.72, 0.18, 250, 8), (0.25, 0.55, 300, -5), (0.70, 0.62, 270, 6), (0.30, 0.83, 210, -8), (0.78, 0.86, 190, 10))):
        im = shadowed(n, s, r); c.alpha_composite(im, (int(x + fx * w - im.width / 2), int(y + fy * h - im.height / 2)))


def how():
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, "Three Ways to Use Them", F("Fraunces-800.ttf", 120), INK)
    tablet(c, 520, 300, 960, 1250)
    steps = [("PRINT", "on sticker paper", 330, 1640), ("CRICUT", "print then cut sheets", 1000, 1640), ("GOODNOTES", "digital stickers", 1670, 1640)]
    for t, s_, x, y in steps:
        f = F("Inter-800.ttf", 54); f2 = F("Inter-500.ttf", 38)
        d.text((x - d.textlength(t, font=f) / 2, y), t, font=f, fill=CORAL)
        d.text((x - d.textlength(s_, font=f2) / 2, y + 80), s_, font=f2, fill=INK)
    for n, xy, r in (("flask", (90, 700), -6), ("caffeine", (1560, 650), 6), ("golden", (110, 1150), 4), ("planet", (1560, 1130), -5)):
        im = shadowed(n, 340, r); c.alpha_composite(im, xy)
    return c


def included():
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, "What's Included", F("Fraunces-800.ttf", 130), INK)
    ctext(d, 270, "instant download", F("Inter-700.ttf", 48), GOLD)
    items = ["24 stickers with white cut border (PNG)", "24 borderless stickers for GoodNotes (PNG)", "3 Cricut Print Then Cut sheets",
             "Printable PDF, US Letter + A4", "Transparent backgrounds, 300+ dpi", "Physics · Chemistry · Math sets"]
    f = F("Inter-700.ttf", 54)
    for i, t in enumerate(items):
        y = 470 + i * 150; d.ellipse((260, y + 10, 316, y + 66), fill=(CORAL, TEAL, GOLD)[i % 3]); d.text((360, y), t, font=f, fill=INK)
    for k, n in enumerate(("black_hole", "genius", "sunflower", "euler")):
        im = shadowed(n, 380, (-6, 4, -3, 6)[k]); c.alpha_composite(im, (int(170 + k * 430), 1430))
    return c


if __name__ == "__main__":
    pages = [hero(), theme("physics", "Physics Stickers", "atoms · black holes · Schrödinger's cat", NAVY),
             theme("chemistry", "Chemistry Stickers", "molecules · flasks · the elements", TEAL),
             theme("math", "Math Stickers", "π · fractals · the golden ratio", GOLD), how(), included()]
    for i, im in enumerate(pages, 1):
        im.convert("RGB").save(os.path.join(PV, f"{i:02d}.jpg"), quality=90)
    sh = Image.new("RGB", (3 * 600, 2 * 600))
    for i, im in enumerate(pages):
        sh.paste(im.convert("RGB").resize((600, 600)), ((i % 3) * 600, (i // 3) * 600))
    sh.save(os.path.join(OUT, "previews_contact.jpg"))
    print("ok")
