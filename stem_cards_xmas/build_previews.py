"""Etsy listing images (2000x2000) for the Christmas STEM Challenge Cards, composited
from the real rendered pages in out/_Letter (0 cover, 1 guide, 2 process, 3 materials,
4-9 card pages, 10 journal, 11 data sheet, 12 tracker, 13 certificate)."""
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "advent_stem"))
sys.path.insert(0, HERE)
import generate_advent as G
import importlib.util
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(HERE, "..", "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
bg, place, banner, S = _ap.bg, _ap.place, _ap.banner, _ap.S
from generate_cards import CARDS, CAT

PG = os.path.join(HERE, "out", "_Letter")
OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)


def pg(n):
    return Image.open(os.path.join(PG, f"p{n:02d}.jpg")).convert("RGB")


def pill(d, text, y, fill=G.RED, size=58):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 140), radius=70, fill=fill)
    d.text(((S - w) / 2, y + 36), text, font=f, fill=G.CREAM)


def hero():
    c = bg(); d = ImageDraw.Draw(c)
    place(c, pg(7), 760, (1080, 500), angle=-8)
    place(c, pg(4), 760, (140, 450), angle=6)
    place(c, pg(0), 840, (580, 330))
    pill(d, "24 CARDS  ·  AGES 6-12  ·  PRINTABLE", 1780)
    return c


def card_close():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Hands-On Challenge Cards", "challenge · materials · test · level up")
    im = pg(4); W, H = im.size
    half = im.crop((0, 0, W, H // 2))
    place(c, half, 1800, (100, 560))
    return c


def all24():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "24 Christmas Challenges", "build · science · motion · math")
    f = G.font("semi", 42); nf = G.font("bold", 36)
    for i, card in enumerate(CARDS):
        col, r = divmod(i, 12)
        x = 140 + col * 900; y = 400 + r * 112
        cc = CAT[card[0]]
        d.ellipse((x, y, x + 74, y + 74), fill=cc)
        t = str(i + 1); d.text((x + 37 - d.textlength(t, font=nf) / 2, y + 16), t, font=nf, fill=G.CREAM)
        d.text((x + 100, y + 10), card[1], font=f, fill=G.NAVY)
    return c


def process():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Think Like an Engineer", "design-process poster + design journal + data sheet")
    place(c, pg(2), 640, (90, 470), angle=4)
    place(c, pg(10), 640, (690, 430))
    place(c, pg(11), 640, (1280, 470), angle=-4)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "15 pages · US Letter + A4")
    items = [(1, "Teacher guide"), (3, "Materials checklist"), (5, "6 pages of cards"),
             (10, "Design journal"), (12, "Challenge tree"), (13, "Certificate")]
    w = 520
    for i, (n, lab) in enumerate(items):
        r, col = divmod(i, 3)
        x = 130 + col * 600; y = 400 + r * 790
        place(c, pg(n), w, (x, y))
        f = G.font("semi", 44)
        d.text((x + (w - d.textlength(lab, font=f)) / 2, y + 690), lab, font=f, fill=G.INK)
    return c


def finale():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "A December STEM Countdown", "color an ornament for every challenge")
    place(c, pg(12), 860, (130, 460), angle=4)
    place(c, pg(13), 860, (1010, 460), angle=-4)
    pill(d, "CLASSROOM  ·  HOMESCHOOL  ·  FAMILY", 1780)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, card_close, all24, process, inside, finale), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
