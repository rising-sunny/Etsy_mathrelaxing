"""Christmas bundle: packs the 4 Christmas products into <=5 Etsy digital files
(each <20 MB) and builds the bundle listing images from the products' own images."""
import os, sys, zipfile, importlib.util
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(REPO, "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
bg, place, banner, S = _ap.bg, _ap.place, _ap.banner, _ap.S

OUT = os.path.join(HERE, "out"); FILES = os.path.join(OUT, "files"); PREV = os.path.join(OUT, "previews")
for d in (FILES, PREV):
    os.makedirs(d, exist_ok=True)
R = lambda *p: os.path.join(REPO, *p)
LIMIT = 20 * 1000 * 1000

PRODUCTS = [  # (name, price, pdfs, ai hero, inside preview, cover page jpg/pdf)
    ("STEM Advent Calendar", 14.99, [R("advent_stem/out/STEM_Advent_Calendar_Letter.pdf"), R("advent_stem/out/STEM_Advent_Calendar_A4.pdf")],
     R("advent_stem/ai_mockups/advent_kitchen_hero.jpg"), R("advent_stem/out/previews/02_inside.jpg")),
    ("Christmas Escape Room", 9.99, [R("escape_room_xmas/out/Christmas_Escape_Room_Letter.pdf"), R("escape_room_xmas/out/Christmas_Escape_Room_A4.pdf")],
     R("escape_room_xmas/ai_mockups/escape_livingroom_hero.jpg"), R("escape_room_xmas/out/previews/05_inside.jpg")),
    ("STEM Challenge Cards", 6.99, [R("stem_cards_xmas/out/Christmas_STEM_Challenge_Cards_Letter.pdf"), R("stem_cards_xmas/out/Christmas_STEM_Challenge_Cards_A4.pdf")],
     R("stem_cards_xmas/ai_mockups/stem_cards_classroom_hero.jpg"), R("stem_cards_xmas/out/previews/05_inside.jpg")),
    ("Logic Puzzle Book", 9.99, [R("logic_book_xmas/out/Christmas_Logic_Puzzles_Letter.pdf"), R("logic_book_xmas/out/Christmas_Logic_Puzzles_A4.pdf")],
     R("logic_book_xmas/ai_mockups/logic_book_fireside_hero.jpg"), R("logic_book_xmas/out/previews/06_inside.jpg")),
]
PRICE = 29.99
TOTAL = sum(p[1] for p in PRODUCTS)


def pack():
    out = []
    for name, _, pdfs, _, _ in PRODUCTS:
        size = sum(os.path.getsize(p) for p in pdfs)
        if size < LIMIT * 0.97:
            z = os.path.join(FILES, name.replace(" ", "_") + ".zip")
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                for p in pdfs:
                    zf.write(p, os.path.basename(p))
            out.append(z)
        else:  # too big together: ship the two PDFs separately
            out += pdfs
    assert len(out) <= 5 and all(os.path.getsize(p) < LIMIT for p in out)
    for p in out:
        print(f"{os.path.getsize(p) / 1e6:5.1f} MB  {os.path.basename(p)}")
    return out


def square(path):
    im = Image.open(path).convert("RGB"); w, h = im.size; k = min(w, h)
    return im.crop(((w - k) // 2, (h - k) // 2, (w + k) // 2, (h + k) // 2))


def label(d, cx, y, text, size=46, fill=G.NAVY):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle((cx - w / 2 - 34, y, cx + w / 2 + 34, y + size + 40), radius=(size + 40) // 2, fill=(255, 255, 255))
    d.text((cx - w / 2, y + 18), text, font=f, fill=fill)


def hero():
    c = Image.new("RGB", (S, S), G.CREAM); d = ImageDraw.Draw(c)
    t = 985; g = 30
    for i, p in enumerate(PRODUCTS):
        r, col = divmod(i, 2)
        im = square(p[3]).resize((t, t), Image.LANCZOS)
        c.paste(im, (col * (t + g), r * (t + g)))
        label(d, col * (t + g) + t / 2, r * (t + g) + (30 if r == 0 else t - 120), p[0])
    # centre badge
    cx = cy = S / 2; rr = 280
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=G.RED, outline=G.CREAM, width=16)
    for s, f, dy, col in (("4-in-1", G.font("cinzel", 96), -200, G.CREAM), ("CHRISTMAS", G.font("cinzel", 74), -80, G.CREAM),
                          ("BUNDLE", G.font("cinzel", 74), 10, G.GOLD), (f"SAVE {round((1 - PRICE / TOTAL) * 100)}%", G.font("bold", 66), 120, G.CREAM)):
        d.text((cx - d.textlength(s, font=f) / 2, cy + dy), s, font=f, fill=col)
    return c


def included():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "4 Printables, 1 Download", f"${TOTAL:.2f} separately  ·  ${PRICE:.2f} in this bundle")
    w = 860
    for i, p in enumerate(PRODUCTS):
        r, col = divmod(i, 2)
        x = 120 + col * 920; y = 380 + r * 760
        im = square(p[3]).resize((w, w), Image.LANCZOS)
        im = im.crop((0, int(w * 0.14), w, int(w * 0.86)))
        place(c, im, w, (x, y))
        f = G.font("semi", 46); s = f"{p[0]}  ·  ${p[1]:.2f}"
        d.text((x + (w - d.textlength(s, font=f)) / 2, y + im.height * w / im.width + 30), s, font=f, fill=G.INK)
    return c


def details():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Everything You Get", "instant download · US Letter + A4 for every product")
    rows = [("STEM Advent Calendar", "24 daily puzzles, experiments & facts + answer key"),
            ("Christmas Escape Room", "8 puzzles, vault password, hint cards, certificate"),
            ("STEM Challenge Cards", "24 build & science challenges + design journal"),
            ("Logic Puzzle Book", "101 puzzles for teens & adults + full solutions")]
    y = 420
    for i, (h, t) in enumerate(rows):
        col = [G.RED, G.PINE, G.NAVY, G.GOLD][i]
        d.rounded_rectangle((150, y, 1850, y + 250), radius=40, fill=(255, 255, 255), outline=col, width=8)
        d.ellipse((200, y + 55, 340, y + 195), fill=col)
        s = str(i + 1); f = G.font("cinzel", 84)
        d.text((270 - d.textlength(s, font=f) / 2, y + 68), s, font=f, fill=G.CREAM)
        d.text((390, y + 50), h, font=G.font("cinzel", 66), fill=G.NAVY)
        d.text((390, y + 150), t, font=G.font("body", 46), fill=G.INK)
        y += 300
    f = G.font("semi", 48); s = "Kids 6-13  ·  Teens  ·  Adults  ·  Classroom  ·  Family"
    d.text(((S - d.textlength(s, font=f)) / 2, 1660), s, font=f, fill=G.RED)
    return c


def build_images():
    imgs = [("01_hero", hero()), ("02_included", included()), ("03_details", details())]
    for i, p in enumerate(PRODUCTS):
        imgs.append((f"{i + 4:02d}_inside_{i + 1}", Image.open(p[4]).convert("RGB")))
    for n, im in imgs:
        im.save(os.path.join(PREV, n + ".jpg"), quality=90); print("wrote", n)


if __name__ == "__main__":
    pack()
    build_images()
