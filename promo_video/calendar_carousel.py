"""
Instagram carousel (1080 x 1350, 4:5) for the 2027 Mathematical Art Calendar:
cover (study photo + hook), six slides with two months each, CTA.

  python calendar_carousel.py   -> out/carousel_calendar/01.jpg ... 08.jpg
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from calendar_promo import font, NAVY, GOLD, CREAM, MONTHS, CAL
from ornament_carousel import gradient, ctext, W, H

OUT = os.path.join(HERE, "out", "carousel_calendar"); os.makedirs(OUT, exist_ok=True)
FORMULA = ["z² + c", "k to 2k on a circle", "4 random affine maps", "137.5° golden angle", "the butterfly effect",
           "two damped pendulums", "seahorse valley", "Newton's method, z⁵ = 1", "17 paper folds",
           "sin and cos, iterated", "split in two, 13 times", "Descartes' circle theorem"]


def art(i, w):
    im = Image.open(os.path.join(CAL, "out", f"{i + 1:02d}_{MONTHS[i][1]}_raw.jpg")).convert("RGB")
    return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)


def label(d, x, y, month, name):
    f1 = font("bold", 34); f2 = font("semi", 34)
    w = d.textlength(month, font=f1) + d.textlength("  " + name, font=f2) + 50
    d.rounded_rectangle((x, y, x + w, y + 62), radius=31, fill=(8, 12, 28))
    d.text((x + 25, y + 12), month, font=f1, fill=GOLD)
    d.text((x + 25 + d.textlength(month, font=f1), y + 12), "  " + name, font=f2, fill=CREAM)


def cover():
    im = Image.open(os.path.join(CAL, "ai_mockups", "calendar_study_hero.jpg")).convert("RGB")
    band = 400; ph = H - band
    s = max(W / im.width, ph / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = (im.width - W) // 2; y0 = (im.height - ph) // 2
    f = gradient(); f.paste(im.crop((x0, y0, x0 + W, y0 + ph)), (0, band)); d = ImageDraw.Draw(f)
    ctext(d, 50, "This calendar", font("cinzel", 80), CREAM)
    ctext(d, 145, "was drawn by", font("cinzel", 80), CREAM)
    ctext(d, 245, "EQUATIONS", font("cinzel", 118), GOLD)
    d.rounded_rectangle((W - 330, H - 120, W - 40, H - 50), radius=35, fill=(8, 12, 28))
    d.text((W - 300, H - 108), "swipe  >>", font=font("bold", 42), fill=CREAM)
    return f


def pair(k):
    f = gradient(); d = ImageDraw.Draw(f); aw = 790
    for j in range(2):
        i = 2 * k + j; a = art(i, aw); x = 60; y = 38 + j * (a.height + 36)
        sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((x + 14, y + 22, x + aw + 14, y + a.height + 22), fill=150)
        f.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(20))); f.paste(a, (x, y))
        d = ImageDraw.Draw(f); label(d, x + 24, y + 24, MONTHS[i][0], MONTHS[i][2])
        fb = font("semi", 30); s = FORMULA[i]; tw = d.textlength(s, font=fb)
        d.rounded_rectangle((x + aw - tw - 64, y + a.height - 76, x + aw - 20, y + a.height - 22), radius=27, fill=(8, 12, 28))
        d.text((x + aw - tw - 42, y + a.height - 67), s, font=fb, fill=(235, 235, 240))
    d.text((W - 160, 50), f"{k + 2}/8", font=font("bold", 40), fill=GOLD)
    for j, s in enumerate(("12", "months", "12", "equations")):
        ff = font("cinzel", 64) if j % 2 == 0 else font("semi", 30)
        d.text((W - 125 - d.textlength(s, font=ff) / 2 + 20, 520 + j * 70 + (j // 2) * 60), s, font=ff, fill=GOLD if j % 2 == 0 else CREAM)
    return f


def cta():
    f = gradient(); d = ImageDraw.Draw(f)
    ctext(d, 70, "The 2027", font("cinzel", 84), GOLD)
    ctext(d, 170, "Mathematical Art Calendar", font("cinzel", 62), CREAM)
    cv = Image.open(os.path.join(CAL, "out", "00_cover.jpg")).convert("RGB").resize((900, 700), Image.LANCZOS)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((104, 302, 1004, 1002), fill=160)
    f.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(22))); f.paste(cv, (90, 280)); d = ImageDraw.Draw(f)
    ctext(d, 1030, "11 x 8.5 in  ·  14 x 11.5 in  ·  spiral bound", font("semi", 44), CREAM)
    ctext(d, 1110, "MathRelaxing on Etsy", font("cinzel", 66), GOLD)
    ctext(d, 1205, "Shop the link in bio", font("bold", 52), CREAM)
    return f


if __name__ == "__main__":
    slides = [cover()] + [pair(k) for k in range(6)] + [cta()]
    for i, im in enumerate(slides, 1):
        im.save(os.path.join(OUT, f"{i:02d}.jpg"), quality=93)
    print(len(slides), "slides")
