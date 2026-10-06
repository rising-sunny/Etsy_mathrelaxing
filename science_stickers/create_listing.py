"""Create the digital Science Sticker Collection as a DRAFT Etsy listing (taxonomy 1326 Stickers)."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Science Stickers Printable, 24 Physics Chemistry Math Sticker Pack, Cricut Print Then Cut, "
         "GoodNotes Digital Stickers, Nerdy Gift")
PRICE = 4.99
TAXONOMY = 1326
SECTION = 60537999  # Education
TAGS = ["science stickers", "physics stickers", "chemistry stickers", "math stickers", "nerdy stickers",
        "printable stickers", "digital stickers", "goodnotes stickers", "cricut stickers", "stem stickers",
        "teacher stickers", "science gift", "planner stickers"]

DESC = f"""Science Sticker Collection: 24 printable stickers for people who love physics, chemistry and math. Every design is original vector artwork with a clean, modern look and a white die-cut border.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Use the stickers three ways: print them on sticker paper, cut them with a Cricut (Print Then Cut), or drop them into GoodNotes, Notability and other digital planners.

PHYSICS (8)
Atom, E = mc², Schrödinger's Cat, Black Hole, Ringed Planet, Newton's Cradle, Good Vibrations, Prism

CHEMISTRY (8)
Erlenmeyer Flask, Caffeine (with the real molecule), Dopamine, Serotonin, Genius in element tiles (Ge Ni U S), DNA, Test Tubes, Stay Positive

MATH (8)
Pi (with real digits), Golden Spiral, Mandelbrot Set, Fibonacci Sunflower, Euler's Identity, Sierpinski Triangle, Infinity, Pythagoras

WHAT'S INCLUDED (zip + PDF)
- 24 PNG stickers with white cut border, transparent background
- 24 borderless PNG stickers for digital planners and GoodNotes
- 3 Cricut Print Then Cut sheets (6.75 x 9.25 in, 300 dpi)
- Printable PDF in US Letter and A4 (instructions + 3 sticker sheets)

Every molecule is drawn from its real chemical structure, and every equation is set like a textbook. Great for laptops, water bottles, planners, lab notebooks, classroom rewards and teacher gifts.

For personal use. Please do not resell or share the files.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS), (len(TITLE), [t for t in TAGS if len(t) > 20])
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    D = os.path.join(HERE, "out", "digital")
    for f in ("Science_Stickers_PNG.zip", "Science_Stickers_Printable_Letter.pdf", "Science_Stickers_Printable_A4.pdf"):
        m.upload_listing_file(lid, os.path.join(D, f))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
