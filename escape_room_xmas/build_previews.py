"""Etsy listing images (2000x2000) for the Christmas Escape Room, composited from
the real rendered pages in out/_Letter (page 0 cover, 3-10 puzzles, 11 vault,
12 hint cards, 13 answer key, 14 certificate)."""
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "advent_stem"))
import generate_advent as G
from build_previews import bg, place, banner, S

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
    place(c, pg(11), 760, (1080, 500), angle=-8)
    place(c, pg(6), 760, (140, 450), angle=6)
    place(c, pg(0), 840, (580, 330))
    pill(d, "8 PUZZLES  ·  AGES 8-13  ·  PRINTABLE", 1780)
    return c


def how():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "How the Game Works", "a party game for 1-6 players · 45-60 minutes")
    steps = [("Solve the 8 puzzles", "each one gives a number from 1 to 26", 3),
             ("Decode the letters", "the Workshop Decoder turns numbers into letters", 11),
             ("Open the vault", "the 8 letters spell the secret password", 14)]
    for i, (h, t, n) in enumerate(steps):
        y = 430 + i * 500
        place(c, pg(n), 330, (200, y))
        d.ellipse((640, y + 60, 780, y + 200), fill=G.RED)
        G_t = str(i + 1); f = G.font("cinzel", 90)
        d.text((710 - d.textlength(G_t, font=f) / 2, y + 70), G_t, font=f, fill=G.CREAM)
        d.text((830, y + 70), h, font=G.font("cinzel", 72), fill=G.NAVY)
        d.text((830, y + 175), t, font=G.font("semi", 44), fill=G.INK)
    return c


def puzzles():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "8 Christmas Puzzles", "patterns · logic · balance scales · magic squares · codes")
    w = 420
    for i in range(8):
        r, col = divmod(i, 4)
        place(c, pg(3 + i), w, (90 + col * 470, 400 + r * 700))
    pill(d, "Sequences, logic and real math thinking", 1800, fill=G.PINE, size=52)
    return c


def closeup():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Hands-On Brain Teasers", "every answer checked and verified")
    place(c, pg(6), 900, (90, 420), angle=3)
    place(c, pg(8), 900, (1010, 440), angle=-3)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "16 pages · US Letter + A4")
    items = [(1, "Host guide"), (2, "Mission briefing"), (3, "8 puzzles"),
             (12, "Cut-out hint cards"), (13, "Answer key"), (14, "Certificate")]
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
    banner(d, "Crack the Vault, Save Christmas", "finish with a certificate for every elf")
    place(c, pg(11), 860, (130, 460), angle=4)
    place(c, pg(14), 860, (1010, 460), angle=-4)
    pill(d, "INSTANT DOWNLOAD  ·  PRINT AT HOME", 1780)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, how, puzzles, closeup, inside, finale), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
