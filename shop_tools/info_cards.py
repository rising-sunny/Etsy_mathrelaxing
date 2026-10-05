"""Branded info cards (2000x2000) appended to listings that have few photos:
  digital_how.jpg   — instant-download "how it works"
  physical_how.jpg  — made-to-order "how it works"
  brand.jpg         — "real mathematics, made beautiful" brand story
"""
import os, sys, math, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)
import brand

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
AF = os.path.join(REPO, "lulu_books", "assets", "fonts")
S = 2000
NAVY = (18, 23, 45); CREAM = (248, 244, 235); GOLD = (201, 162, 75); SOFT = (150, 160, 190)


def font(kind, size):
    if kind == "title":
        return ImageFont.truetype(f"{AF}/Cinzel-SemiBold.ttf", size)
    f = ImageFont.truetype(f"{AF}/Raleway.ttf", size)
    f.set_variation_by_name({"body": "Medium", "bold": "Bold", "light": "Regular"}[kind])
    return f


def base():
    c = Image.new("RGB", (S, S), NAVY); d = ImageDraw.Draw(c)
    rnd = random.Random(11)
    for _ in range(55):  # faint golden-spiral dots, on brand
        x, y = rnd.randint(0, S), rnd.randint(0, S - 160)
        d.ellipse((x, y, x + 5, y + 5), fill=(40, 50, 84))
    d.rectangle((0, S - 160, S, S), fill=(0, 0, 0))
    logo = Image.open(brand.LOGO_PATH).convert("RGBA"); logo.thumbnail((380, 130))
    c.paste(logo, ((S - logo.width) // 2, S - 80 - logo.height // 2), logo)
    return c, d


def centered(d, y, text, f, fill):
    d.text(((S - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def steps_card(title, sub, steps, foot, name):
    c, d = base()
    centered(d, 190, title, font("title", 120), CREAM)
    centered(d, 345, sub, font("light", 54), GOLD)
    y = 560
    for i, (h, t) in enumerate(steps, 1):
        d.ellipse((260, y, 420, y + 160), outline=GOLD, width=8)
        n = str(i); nf = font("title", 92)
        d.text((340 - d.textlength(n, font=nf) / 2, y + 22), n, font=nf, fill=GOLD)
        d.text((480, y + 12), h, font=font("bold", 66), fill=CREAM)
        d.text((480, y + 96), t, font=font("body", 46), fill=SOFT)
        y += 300
    centered(d, S - 300, foot, font("body", 46), GOLD)
    c.save(os.path.join(OUT, name), quality=90)


def brand_card():
    c, d = base()
    # golden spiral (quarter arcs growing by phi)
    phi = (1 + 5 ** 0.5) / 2; cx, cy, r = 1000, 640, 10.2
    pts = []
    for k in range(8):
        a0 = k * math.pi / 2
        for t in range(0, 91, 3):
            a = a0 + math.radians(t); rr = r * phi ** (k + t / 90)
            pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.line(pts, fill=GOLD, width=7)
    centered(d, 1180, "Real Mathematics,", font("title", 104), CREAM)
    centered(d, 1310, "Made Beautiful", font("title", 104), CREAM)
    lines = ["Every artwork is computed from its own equation —",
             "no AI art, no clip-art, nothing traced by hand."]
    for i, t in enumerate(lines):
        centered(d, 1490 + i * 72, t, font("body", 50), SOFT)
    centered(d, 1680, "Designed in our small studio by MathRelaxing", font("light", 44), GOLD)
    c.save(os.path.join(OUT, "brand.jpg"), quality=90)


if __name__ == "__main__":
    steps_card("Instant Download", "nothing is shipped — start right away",
               [("Purchase", "checkout as usual on Etsy"),
                ("Download", "You › Purchases and reviews › Download files"),
                ("Print or use", "at home, a local print shop, or on your device")],
               "Re-download any time  ·  questions? message us on Etsy", "digital_how.jpg")
    steps_card("Made to Order", "printed just for you",
               [("Order", "choose your size or option above"),
                ("We print it", "produced on demand by our print partner"),
                ("Delivered", "shipped to your door with tracking")],
               "Questions or problems? Message us here on Etsy", "physical_how.jpg")
    brand_card()
    print("cards:", sorted(os.listdir(OUT)))
