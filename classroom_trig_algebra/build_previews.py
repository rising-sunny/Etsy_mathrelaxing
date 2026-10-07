"""Etsy listing images (2000x2000) for the Trig & Algebra Classroom Poster Set."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from posters import POSTERS

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
PNG = os.path.join(OUT, "png"); PV = os.path.join(OUT, "previews"); os.makedirs(PV, exist_ok=True)
FD = os.path.join(HERE, "fonts"); S = 2000
INK = (43, 45, 66); WALL = (236, 230, 218)
ACC = [(61, 133, 214), (239, 111, 108), (76, 175, 110), (149, 98, 204), (31, 163, 155), (243, 146, 55),
       (229, 83, 75), (88, 102, 196), (226, 104, 159), (233, 181, 47)]


def F(n, s):
    return ImageFont.truetype(os.path.join(FD, n), s)


def poster(i, w):
    im = Image.open(sorted(os.path.join(PNG, f) for f in os.listdir(PNG))[i]).convert("RGB")
    return im.resize((w, int(w * 4 / 3)), Image.LANCZOS)


def hang(c, im, x, y, blur=22, off=(10, 18)):
    sh = Image.new("L", c.size, 0); sh.paste(Image.new("L", im.size, 120), (x + off[0], y + off[1]))
    c.paste((60, 50, 40), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur))); c.paste(im, (x, y))


def ctext(d, y, s, f, fill):
    d.text(((S - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)


def pill(d, s, y, fill, size=58):
    f = F("Fredoka-700.ttf", size); w = d.textlength(s, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 130), radius=65, fill=fill)
    d.text(((S - w) / 2, y + 28), s, font=f, fill=(255, 255, 255))


def hero():
    c = Image.new("RGB", (S, S), WALL); d = ImageDraw.Draw(c)
    for y in range(1520, S):
        d.line((0, y, S, y), fill=(196, 168, 128))                     # wood ledge / floor band
    d.rectangle((0, 1500, S, 1530), fill=(150, 116, 80))
    ctext(d, 80, "Trig & Algebra", F("Fredoka-700.ttf", 150), INK)
    ctext(d, 260, "10 classroom posters  ·  print any size", F("Nunito-800.ttf", 58), (110, 104, 96))
    for i, w, x, y in ((1, 470, 70, 560), (8, 470, 1460, 560), (0, 700, 650, 420)):
        hang(c, poster(i, w), x, y, blur=28, off=(14, 24))
    pill(d, "UNIT CIRCLE · SOHCAHTOA · QUADRATIC · +7 MORE", 1700, (61, 133, 214), 48)
    return c


def grid():
    c = Image.new("RGB", (S, S), (250, 247, 240)); d = ImageDraw.Draw(c)
    ctext(d, 70, "All 10 Posters", F("Fredoka-700.ttf", 130), INK)
    w = 340
    for i in range(10):
        r, q = divmod(i, 5); x = 65 + q * 380; y = 290 + r * 640
        hang(c, poster(i, w), x, y, blur=14, off=(6, 10))
    pill(d, "COLOUR-CODED  ·  EASY TO READ FROM THE BACK ROW", 1760, (149, 98, 204), 44)
    return c


def closeup(i, title, sub, col):
    c = Image.new("RGB", (S, S), (250, 247, 240)); d = ImageDraw.Draw(c)
    ctext(d, 70, title, F("Fredoka-700.ttf", 120), INK); ctext(d, 220, sub, F("Nunito-800.ttf", 50), col)
    hang(c, poster(i, 1180), 410, 330, blur=30, off=(16, 26))
    return c


def sizes():
    c = Image.new("RGB", (S, S), (250, 247, 240)); d = ImageDraw.Draw(c)
    ctext(d, 70, "Print Any Size", F("Fredoka-700.ttf", 130), INK)
    ctext(d, 230, "vector PDF  ·  crisp at every size", F("Nunito-800.ttf", 52), (31, 163, 155))
    for k, (lab, w) in enumerate((("18 x 24 in", 640), ("11 x 17 in / A3", 470), ("Letter / A4", 340))):
        x = [120, 860, 1440][k]; y = 1600 - int(w * 4 / 3)
        hang(c, poster(k + 4, w), x, y)
        f = F("Fredoka-700.ttf", 54); d.text((x + w / 2 - d.textlength(lab, font=f) / 2, 1650), lab, font=f, fill=INK)
    return c


def included():
    c = Image.new("RGB", (S, S), (250, 247, 240)); d = ImageDraw.Draw(c)
    ctext(d, 70, "What's Included", F("Fredoka-700.ttf", 130), INK)
    titles = ["The Unit Circle", "SOH CAH TOA", "Special Right Triangles", "Trig Identities", "Graphs of Trig Functions",
              "Law of Sines & Cosines", "Order of Operations", "Slope & Linear Equations", "The Quadratic Formula", "Laws of Exponents"]
    f = F("Nunito-800.ttf", 56)
    for i, t in enumerate(titles):
        y = 290 + i * 112; d.rounded_rectangle((300, y, 380, y + 80), radius=24, fill=ACC[i])
        d.text((340 - d.textlength(str(i + 1), font=F("Fredoka-700.ttf", 50)) / 2, y + 8), str(i + 1), font=F("Fredoka-700.ttf", 50), fill="white")
        d.text((420, y + 6), t, font=f, fill=INK)
    ctext(d, 1460, "5 PDF files: 18x24 · 11x17 · A3 · Letter · A4", F("Nunito-800.ttf", 52), (110, 104, 96))
    pill(d, "INSTANT DOWNLOAD", 1600, (229, 83, 75))
    return c


if __name__ == "__main__":
    pages = [hero(), grid(), closeup(0, "The Unit Circle", "degrees, radians and coordinates", (61, 133, 214)),
             closeup(8, "The Quadratic Formula", "with the discriminant explained", (226, 104, 159)),
             closeup(1, "SOH CAH TOA", "colour-coded sides and ratios", (239, 111, 108)), sizes(), included()]
    for i, im in enumerate(pages, 1):
        im.save(os.path.join(PV, f"{i:02d}.jpg"), quality=90)
    sh = Image.new("RGB", (4 * 500, 2 * 500), "white")
    for i, im in enumerate(pages):
        sh.paste(im.resize((500, 500)), ((i % 4) * 500, (i // 4) * 500))
    sh.save(os.path.join(OUT, "previews_contact.jpg"), quality=88)
