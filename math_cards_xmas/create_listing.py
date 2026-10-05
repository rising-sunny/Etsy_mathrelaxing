"""Create the Math Christmas Cards as a DRAFT digital Etsy listing (taxonomy 1273
Christmas Cards) with 5 images, both PDFs and the PNG fronts zip."""
import os, sys, glob, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Math Christmas Cards Printable, 12 Funny Math Pun Holiday Cards, Pi Tree, Fractal, Fibonacci, "
         "Gift for Math Teacher or Nerd")
PRICE = 5.99
TAXONOMY = 1273
SECTION = 60740209  # Christmas
TAGS = ["math christmas card", "math pun card", "pi christmas card", "nerdy christmas", "math teacher card",
        "science christmas", "geek christmas card", "printable card", "fractal christmas", "christmas card set",
        "funny christmas card", "stem christmas", "math lover gift"]

DESC = f"""12 printable Christmas cards for people who love math: every front is a pun with generative art made from real mathematics, and the back of each card explains the math behind it.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Print at home or at a print shop, or send the fronts digitally.

THE 12 CARDS
1. Have a Tree-mendous Christmas: a fractal tree with 2,048 branch tips
2. Let It Snow, Recursively: the Koch snowflake
3. O Pi-ne Tree: a Christmas tree made of the digits of pi
4. Have a Golden Holiday: a wreath built with the golden angle (Fibonacci)
5. Merry Christmas at every scale: a Sierpinski triangle tree
6. Merry X-mas (solve for x): a chalkboard tree drawn by an inequality
7. The 12 Days of Christmas = 364 gifts: triangular and tetrahedral numbers
8. The Shortest Path to Christmas: Santa vs. the Traveling Salesman Problem
9. Have a Well-Rounded Christmas: Lissajous curve ornaments
10. No Two Alike: six-fold snowflake symmetry
11. Merry Christmas: string lights that spell JOY in binary
12. Have a Prime New Year: 2027 is a prime number

WHAT YOU GET
- Math_Christmas_Cards_Letter.pdf and Math_Christmas_Cards_A4.pdf: each card as an outside page (front + back with the math explained) and an inside page with a message and a signature line, with crop marks
- Math_Christmas_Cards_PNG_Fronts.zip: all 12 fronts as 5 x 7 in, 300 dpi PNG images to send by text, email or social media
- A printing guide

SIZE
5 x 7 in folded card (10 x 7 in flat), fits a standard A7 envelope (5.25 x 7.25 in). Prints on US Letter or A4 card stock, double-sided.

PERFECT FOR
- Math teachers, students, engineers, programmers and scientists
- Classroom holiday cards
- Office cards for the data team
- Anyone who smiles at a good pun

For personal use: print as many cards as you want to send yourself. Please do not resell or share the files.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    out = os.path.join(HERE, "out")
    files = [os.path.join(out, f) for f in ("Math_Christmas_Cards_Letter.pdf", "Math_Christmas_Cards_A4.pdf",
                                            "Math_Christmas_Cards_PNG_Fronts.zip")]
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(out, "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for p in files:
        m.upload_listing_file(lid, p)
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
