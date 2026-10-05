"""Etsy listing images (2000x2000) for the Math Christmas Cards."""
import os, sys, glob, importlib.util
import fitz
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(REPO, "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
bg, place, banner, S = _ap.bg, _ap.place, _ap.banner, _ap.S

OUT = os.path.join(HERE, "out"); PREV = os.path.join(OUT, "previews"); os.makedirs(PREV, exist_ok=True)
FRONTS = sorted(glob.glob(os.path.join(OUT, "fronts", "*.png")))
DOC = fitz.open(os.path.join(OUT, "Math_Christmas_Cards_Letter.pdf"))


def front(i, w):
    im = Image.open(FRONTS[i]).convert("RGB"); return im.resize((w, int(w * 1.4)), Image.LANCZOS)


def pg(n, dpi=150):
    pix = DOC[n].get_pixmap(dpi=dpi); return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def pill(d, text, y, fill=G.RED, size=56):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 136), radius=68, fill=fill)
    d.text(((S - w) / 2, y + 34), text, font=f, fill=G.CREAM)


def hero():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "12 Math Christmas Cards", "printable 5 x 7 folding cards · real mathematics, made beautiful", y=60)
    w = 360; gx = (S - 4 * w - 3 * 60) // 2
    for i in range(12):
        r, col = divmod(i, 4)
        place(c, front(i, w), w, (gx + col * (w + 60), 300 + r * 545))
    return c


def fan():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Puns + Real Math", "fractals, pi, Fibonacci, binary, primes and more")
    place(c, front(1, 680), 680, (80, 500), angle=8)
    place(c, front(10, 680), 680, (1130, 500), angle=-8)
    place(c, front(2, 820), 820, (590, 380))
    return c


def back_inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "The Math Is on the Back", "every card explains its mathematics, with a message inside")
    out = pg(1); ins = pg(2)
    W, H = out.size; box = lambda im: im.crop((int(W * 0.03), int(H * 0.08), int(W * 0.97), int(H * 0.92)))
    place(c, box(out), 1300, (330, 390), angle=2)
    place(c, box(ins), 1300, (370, 1040), angle=-2)
    return c


def phone():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Print It or Send It", "PNG fronts included to share by text, email or social media")
    place(c, front(7, 700), 700, (180, 520), angle=5)
    # phone
    px, py, pw, ph = 1060, 420, 680, 1360
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=90, fill=(20, 22, 28))
    scr = front(10, pw - 70); c.paste(scr.resize((pw - 70, ph - 120)), (px + 35, py + 60))
    d.rounded_rectangle((px + pw / 2 - 90, py + 22, px + pw / 2 + 90, py + 44), radius=11, fill=(45, 48, 56))
    return c


def contents():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What You Get", "instant download · US Letter + A4")
    place(c, pg(0), 900, (100, 480), angle=2)
    rows = ["12 card designs", "Front, inside message & back", "The math explained on every card",
            "Print-ready 5 x 7 in (fits A7 envelopes)", "Crop marks + printing guide", "12 PNG fronts to send digitally",
            "Print as many as you need"]
    f = G.font("semi", 48); y = 560
    for t in rows:
        d.ellipse((1080, y + 14, 1110, y + 44), fill=G.GOLD)
        d.text((1135, y), t, font=f, fill=G.NAVY); y += 140
    pill(d, "PERFECT FOR MATH TEACHERS & NERDS", 1800, fill=G.PINE, size=50)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, fan, back_inside, phone, contents), 1):
        p = os.path.join(PREV, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
