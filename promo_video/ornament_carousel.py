"""
Instagram carousel (1080 x 1350, 4:5) for the fractal ceramic ornaments:
cover (tree photo + hook), one slide per ornament (front + back + one math fact), CTA.

  python ornament_carousel.py   -> out/carousel_ornaments/01.jpg ... 08.jpg
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from ornament_promo import disc, ORN
from calendar_promo import font, NAVY, GOLD, CREAM

W, H = 1080, 1350
OUT = os.path.join(HERE, "out", "carousel_ornaments"); os.makedirs(OUT, exist_ok=True)
SLIDES = [
    ("mandelbrot", "Mandelbrot Set", ["Every point c where z² + c", "never escapes to infinity."]),
    ("koch", "Koch Snowflake", ["An infinitely long edge", "around a finite area."]),
    ("julia", "Julia Set", ["The same rule z² + c,", "with c = -0.8 + 0.156i."]),
    ("pi", "Pi Spiral", ["Over 1,000 digits of π:", "they never end, never repeat."]),
    ("golden", "Golden Angle", ["Each dot turns 137.5°,", "so Fibonacci spirals appear."]),
    ("tree", "Fractal Tree", ["Every branch splits in two,", "eleven times: 2,048 tips."]),
]


def ctext(d, y, s, f, fill, cx=W / 2):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def gradient(top=(28, 40, 76), bot=(10, 14, 30)):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top) * (1 - g) + np.array(bot) * g) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8))


def paste_disc(base, im, x, y, shadow=True, cord=120):
    if shadow:
        d = im.width; sh = Image.new("L", base.size, 0)
        ImageDraw.Draw(sh).ellipse((x + 18, y + 30, x + d + 18, y + d + 30), fill=150)
        base.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(26)))
    base.paste(im, (x, y), im)
    ImageDraw.Draw(base).ellipse((x, y, x + im.width - 1, y + im.width - 1), outline=(226, 220, 205), width=max(3, im.width // 140))
    ImageDraw.Draw(base).line((x + im.width / 2, y - cord, x + im.width / 2, y + im.width * 0.07), fill=(214, 176, 92), width=5)


def cover():
    im = Image.open(os.path.join(ORN, "ai_mockups", "fractal_ornaments_tree.jpg")).convert("RGB")
    band = 400; ph = H - band
    s_ = max(W / im.width, ph / im.height); im = im.resize((int(im.width * s_), int(im.height * s_)), Image.LANCZOS)
    x0 = (im.width - W) // 2; y0 = (im.height - ph) // 2
    f = gradient((28, 40, 76), (14, 20, 42)); f.paste(im.crop((x0, y0, x0 + W, y0 + ph)), (0, band))
    d = ImageDraw.Draw(f)
    ctext(d, 50, "These ornaments", font("cinzel", 80), CREAM)
    ctext(d, 145, "were drawn by", font("cinzel", 80), CREAM)
    ctext(d, 245, "EQUATIONS", font("cinzel", 118), GOLD)
    d.rounded_rectangle((W - 330, H - 120, W - 40, H - 50), radius=35, fill=(8, 12, 28))
    d.text((W - 300, H - 108), "swipe  >>", font=font("bold", 42), fill=CREAM)
    return f


def ornament(i, key, name, fact):
    f = gradient(); d = ImageDraw.Draw(f)
    d.text((60, 60), f"{i} / 6", font=font("bold", 40), fill=GOLD)
    ctext(d, 120, name, font("cinzel", 92), CREAM)
    paste_disc(f, disc(key, "front", 700), 90, 360)
    paste_disc(f, disc(key, "back", 380), 640, 720, cord=0)
    d = ImageDraw.Draw(f)
    d.text((130, 1080), "FRONT", font=font("bold", 34), fill=GOLD); d.text((760, 1120), "BACK", font=font("bold", 34), fill=GOLD)
    for k, s in enumerate(fact):
        ctext(d, 1185 + k * 60, s, font("semi", 46), CREAM)
    return f


def cta():
    f = gradient(); d = ImageDraw.Draw(f)
    ctext(d, 90, "6 fractal ornaments", font("cinzel", 80), CREAM)
    ctext(d, 190, "ceramic · printed on both sides", font("semi", 46), GOLD)
    s = 300
    for i, (key, *_r) in enumerate(SLIDES):
        r, c = divmod(i, 3); x = 75 + c * (s + 40); y = 330 + r * (s + 70)
        paste_disc(f, disc(key, "front", s), x, y, shadow=False, cord=30)
    d = ImageDraw.Draw(f)
    ctext(d, 1080, "MathRelaxing on Etsy", font("cinzel", 70), GOLD)
    ctext(d, 1180, "Shop the link in bio", font("bold", 54), CREAM)
    return f


if __name__ == "__main__":
    slides = [cover()] + [ornament(i + 1, *s) for i, s in enumerate(SLIDES)] + [cta()]
    for i, im in enumerate(slides, 1):
        im.save(os.path.join(OUT, f"{i:02d}.jpg"), quality=93)
    print(len(slides), "slides")
