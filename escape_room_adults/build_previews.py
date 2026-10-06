"""Etsy listing images (2000x2000) for The Mathematician's Vault, from the rendered pages
(0 cover, 1 host guide, 2 letter, 3-11 exhibits, 12 vault, 13 hints, 14 answer key, 15 certificate)."""
import os, sys, importlib.util
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(REPO, "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
place, S = _ap.place, _ap.S
PG = os.path.join(HERE, "out", "_Letter"); OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)
NAVY = (26, 36, 62); GOLD = (184, 140, 62); PAPER = (244, 236, 218); OX = (128, 40, 36)


def pg(n):
    return Image.open(os.path.join(PG, f"p{n:02d}.jpg")).convert("RGB")


def bg(dark=False):
    c = Image.new("RGB", (S, S), NAVY if dark else (232, 222, 200)); d = ImageDraw.Draw(c)
    if not dark:
        for y in range(S):
            t = y / S; d.line((0, y, S, y), fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((240, 232, 214), (214, 200, 172))))
    return c


def banner(d, t, sub=None, y=80, dark=False):
    f = G.font("cinzel", 96); d.text(((S - d.textlength(t, font=f)) / 2, y), t, font=f, fill=PAPER if dark else NAVY)
    if sub:
        s = G.font("semi", 50); d.text(((S - d.textlength(sub, font=s)) / 2, y + 125), sub, font=s, fill=GOLD if dark else OX)


def pill(d, text, y, fill=OX, size=54):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 136), radius=68, fill=fill)
    d.text(((S - w) / 2, y + 34), text, font=f, fill=PAPER)


def hero():
    c = bg(True); d = ImageDraw.Draw(c)
    place(c, pg(4), 760, (1090, 470), angle=-8)
    place(c, pg(10), 760, (130, 430), angle=7)
    place(c, pg(0), 840, (580, 300))
    pill(d, "ESCAPE ROOM FOR ADULTS  ·  PRINTABLE", 1790)
    return c


def how():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "How the Game Works", "2-6 players  ·  60-90 minutes  ·  solve in any order")
    steps = [("Read the letter", "the professor hid his password in his study", 2),
             ("Solve 9 exhibits", "ciphers, logic, magic squares, binary, a telegram", 5),
             ("Open the vault", "each answer is a letter of the password", 12)]
    for i, (h, t, n) in enumerate(steps):
        y = 430 + i * 500; place(c, pg(n), 330, (200, y))
        d.ellipse((640, y + 60, 780, y + 200), fill=OX); s = str(i + 1); f = G.font("cinzel", 90)
        d.text((710 - d.textlength(s, font=f) / 2, y + 70), s, font=f, fill=PAPER)
        d.text((830, y + 70), h, font=G.font("cinzel", 72), fill=NAVY)
        d.text((830, y + 175), t, font=G.font("semi", 44), fill=(60, 50, 44))
    return c


def exhibits():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "9 Classic Puzzles", "Caesar cipher · Dürer's magic square · SEND + MORE = MONEY · Fibonacci", y=60)
    w = 420
    for i in range(9):
        r, col = divmod(i, 3); place(c, pg(3 + i), w, (230 + col * 560, 300 + r * 560))
    return c


def closeup():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Real Brain Teasers", "every answer checked by computer to be unique")
    place(c, pg(5), 900, (90, 420), angle=3); place(c, pg(10), 900, (1010, 440), angle=-3)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "17 pages · US Letter + A4")
    items = [(1, "Host guide"), (2, "The professor's letter"), (3, "9 exhibits"), (13, "Cut-out hint cards"),
             (12, "The vault"), (15, "Certificate")]
    w = 520
    for i, (n, lab) in enumerate(items):
        r, col = divmod(i, 3); x = 130 + col * 600; y = 400 + r * 790
        place(c, pg(n), w, (x, y)); f = G.font("semi", 44)
        d.text((x + (w - d.textlength(lab, font=f)) / 2, y + 690), lab, font=f, fill=NAVY)
    return c


def finale():
    c = bg(True); d = ImageDraw.Draw(c)
    banner(d, "Crack the Vault", "nine letters, one password", dark=True)
    place(c, pg(12), 860, (130, 460), angle=4); place(c, pg(15), 860, (1010, 460), angle=-4)
    pill(d, "GAME NIGHT · DATE NIGHT · MATH CLUB", 1790)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, how, exhibits, closeup, inside, finale), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
