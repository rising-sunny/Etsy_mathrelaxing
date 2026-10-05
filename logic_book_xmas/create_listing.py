"""Create the Christmas Logic Puzzles book as a DRAFT digital Etsy listing (taxonomy
12626 Word & Number Puzzles) with 7 preview images and the US Letter + A4 PDFs."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Christmas Logic Puzzle Book for Adults and Teens, 101 Printable Brain Teasers, Sudoku, Nonograms, "
         "Cryptograms, Mazes with Solutions")
PRICE = 9.99
TAXONOMY = 12626
SECTION = 60740209  # Christmas
TAGS = ["christmas puzzles", "logic puzzles", "brain teasers", "christmas sudoku", "puzzle book adults",
        "nonogram puzzles", "cryptogram puzzles", "printable puzzles", "christmas activity", "christmas mazes",
        "puzzle book teens", "stocking stuffer", "holiday puzzles"]

DESC = f"""101 Christmas logic puzzles for teens and adults in one printable book, with every solution included. Cozy puzzling for the holidays, a quiet activity for the family gathering, or a last-minute digital gift.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Download, print the pages you want and start solving.

WHAT'S INSIDE (75 pages, US Letter and A4)
- 30 Sudoku: 10 easy, 10 medium, 10 hard
- 12 Futoshiki (5 x 5 inequality puzzles)
- 10 Nonograms (picture logic) that reveal Christmas pictures: tree, bell, snowman, gift, candy cane, stocking, star, gingerbread man, ornament and mitten
- 6 Logic Grid stories: elves' workshop, cookie exchange, reindeer flights, Secret Santa, lights contest and holiday train
- 15 Cryptograms with Christmas and math quotes from public-domain classics (Dickens, Alcott, Longfellow, Shakespeare and more)
- 8 Christmas-shaped mazes: tree, ornament, star, snowman, gift box, bell, stocking and gingerbread house
- 20 Christmas math brain teasers
- How-to-play guide and contents page
- Full solutions for all 101 puzzles, with every brain teaser explained

QUALITY YOU CAN TRUST
Every puzzle was generated and checked by computer to have exactly one solution, and every nonogram can be solved by logic alone, without guessing.

GREAT FOR
- Holiday downtime and travel
- Family puzzle evenings and Christmas parties
- Middle and high school classrooms in December
- Puzzle lovers who want something festive

DETAILS
- Ages 12 and up
- Crisp vector PDF that prints sharply at any size
- Black-and-white friendly puzzle pages with festive color accents

For personal, family and single-classroom use. Please do not resell or share the file.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"Christmas_Logic_Puzzles_{name}.pdf"))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
