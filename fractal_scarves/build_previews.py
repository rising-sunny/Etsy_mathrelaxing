"""Listing images (2000x2000) for each fractal scarf: styled flat lay, detail crop, collection, sizes."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fractals import DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); PV = os.path.join(OUT, "previews"); os.makedirs(PV, exist_ok=True)
FD = os.path.join(HERE, "..", "science_stickers", "fonts"); S = 2000
INK = (29, 39, 66); CREAM = (247, 241, 230); GOLD = (178, 132, 52)
Image.MAX_IMAGE_PIXELS = None


def F(n, s):
    return ImageFont.truetype(os.path.join(FD, n), s)


def bg():
    im = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / S; d.line((0, y, S, y), fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((250, 246, 238), (232, 224, 210))))
    return im


def ctext(d, y, s, f, fill):
    d.text(((S - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)


def drop(canvas, im, xy, blur=40, off=(18, 30), alpha=110):
    sh = Image.new("L", canvas.size, 0); m = Image.new("L", im.size, alpha)
    sh.paste(m, (xy[0] + off[0], xy[1] + off[1])); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste((40, 32, 24), (0, 0), sh); canvas.paste(im, xy)


def styled(key, prev):
    name = DESIGNS[key][0]; c = bg(); d = ImageDraw.Draw(c)
    im = prev.resize((1380, 1380), Image.LANCZOS).rotate(-6, resample=Image.BICUBIC, expand=True, fillcolor=CREAM)
    mask = Image.new("L", (1380, 1380), 255).rotate(-6, resample=Image.BICUBIC, expand=True)
    sh = Image.new("L", c.size, 0); sh.paste(mask.point(lambda v: v * 0.45), (330 + 20, 330 + 36)); sh = sh.filter(ImageFilter.GaussianBlur(40))
    c.paste((40, 32, 24), (0, 0), sh); c.paste(im, (330, 330), mask)
    ctext(d, 90, name, F("Fraunces-800.ttf", 120), INK)
    ctext(d, 240, "chiffon fractal scarf  ·  25\" or 50\" square", F("Inter-700.ttf", 46), GOLD)
    return c


def detail(key, full):
    name, blurb = DESIGNS[key][0], DESIGNS[key][1]; c = bg(); d = ImageDraw.Draw(c)
    W = full.width; cx, cy = int(W * 0.36), int(W * 0.40); r = int(W * 0.09)
    crop = full.crop((cx - r, cy - r, cx + r, cy + r)).resize((1500, 1500), Image.LANCZOS)
    drop(c, crop, (250, 330))
    ctext(d, 90, "Every Detail Is Real Math", F("Fraunces-800.ttf", 110), INK)
    ctext(d, 230, f"{blurb}, computed at 9000 x 9000 px", F("Inter-700.ttf", 42), GOLD)
    return c


def collection(prevs):
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, "The Fractal Scarf Collection", F("Fraunces-800.ttf", 104), INK)
    ctext(d, 230, "six designs  ·  each one a famous piece of mathematics", F("Inter-700.ttf", 42), GOLD)
    for i, (k, p) in enumerate(prevs.items()):
        r, q = divmod(i, 3); im = p.resize((540, 540), Image.LANCZOS); x, y = 110 + q * 610, 380 + r * 760
        drop(c, im, (x, y), blur=24, off=(10, 18))
        t = DESIGNS[k][0]; f = F("Inter-700.ttf", 40); d.text((x + 270 - d.textlength(t, font=f) / 2, y + 570), t, font=f, fill=INK)
    return c


def sizes(prev):
    c = bg(); d = ImageDraw.Draw(c)
    ctext(d, 90, "Two Sizes", F("Fraunces-800.ttf", 120), INK)
    ctext(d, 240, "light, sheer poly chiffon  ·  black stitched edges", F("Inter-700.ttf", 44), GOLD)
    big = prev.resize((1000, 1000), Image.LANCZOS); small = prev.resize((500, 500), Image.LANCZOS)
    drop(c, big, (180, 520)); drop(c, small, (1320, 1020))
    f = F("Inter-800.ttf", 56); f2 = F("Inter-500.ttf", 40)
    for x, y, a, b in ((680, 1560, '50" x 50"', "shawl · wrap · sarong"), (1570, 1560, '25" x 25"', "neck scarf · bandana · bag")):
        d.text((x - d.textlength(a, font=f) / 2, y), a, font=f, fill=INK); d.text((x - d.textlength(b, font=f2) / 2, y + 80), b, font=f2, fill=(110, 100, 90))
    return c


if __name__ == "__main__":
    prevs = {k: Image.open(os.path.join(OUT, "preview", f"{k}.jpg")).convert("RGB") for k in DESIGNS}
    collection(prevs).save(os.path.join(PV, "collection.jpg"), quality=90)
    for k in DESIGNS:
        full = Image.open(os.path.join(OUT, "final", f"{k}.jpg")).convert("RGB")
        styled(k, prevs[k]).save(os.path.join(PV, f"{k}_1_styled.jpg"), quality=90)
        detail(k, full).save(os.path.join(PV, f"{k}_2_detail.jpg"), quality=90)
        sizes(prevs[k]).save(os.path.join(PV, f"{k}_3_sizes.jpg"), quality=90)
        print("ok", k)
