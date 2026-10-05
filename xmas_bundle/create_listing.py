"""Create the 4-in-1 Christmas bundle as a DRAFT digital Etsy listing with the
bundle images and the 5 delivery files built by build_bundle.py."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from etsy_manager import EtsyManager
import brand
from build_bundle import PRICE, TOTAL, pack

TITLE = ("Christmas Printable Bundle, STEM Advent Calendar, Kids Escape Room, STEM Challenge Cards, "
         "Logic Puzzle Book, Holiday Activities")
TAXONOMY = 12471
SECTION = 60740209  # Christmas
TAGS = ["christmas bundle", "christmas printable", "christmas activity", "stem advent", "escape room kids",
        "stem challenge cards", "logic puzzles", "christmas puzzles", "holiday activities", "classroom christmas",
        "homeschool bundle", "family game night", "december activities"]

DESC = f"""Four Christmas printables in one download: a whole December of puzzles, science and games for kids, teens and adults. Bought separately they cost ${TOTAL:.2f}; in this bundle you get all four for ${PRICE:.2f}.

INSTANT DOWNLOAD
This is a digital product; nothing is shipped. Every product comes in US Letter and A4.

WHAT'S INCLUDED

1. STEM Advent Calendar (12 pages)
24 daily cards with math puzzles, kitchen science experiments and mind-blowing facts, a calendar board and an answer key. Ages 6-12.

2. Christmas Escape Room for Kids (16 pages)
"The Great Workshop Lockdown": 8 math and logic puzzles whose answers spell the vault password, with a host guide, hint cards, answer key and certificate. Ages 8-13.

3. Christmas STEM Challenge Cards (15 pages)
24 hands-on build, science, motion and math challenges with an engineering design poster, design journal, data sheet, challenge tracker and certificate. Ages 6-12.

4. Christmas Logic Puzzle Book (75 pages)
101 puzzles for teens and adults: sudoku, futoshiki, nonograms, logic grids, cryptograms, Christmas-shaped mazes and brain teasers, with full solutions.

YOUR FILES
- STEM_Advent_Calendar.zip
- Christmas_Escape_Room.zip
- Christmas_STEM_Challenge_Cards_Letter.pdf and Christmas_STEM_Challenge_Cards_A4.pdf
- Logic_Puzzle_Book.zip
Each ZIP holds the US Letter and A4 PDFs of that product. On a phone or tablet, open ZIP files with the built-in Files app; on a computer just double-click them.

HOW TO GET THEM
After purchase go to You > Purchases and reviews > Download files. You can download them again any time.

PERFECT FOR
- A December countdown at home
- Classroom holiday parties and the last week before winter break
- Homeschool families
- Family game nights over the holidays

For personal, family and single-classroom use. Please do not resell or share the files.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    files = pack()
    assert len(files) == 5
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for p in files:
        m.upload_listing_file(lid, p)
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    f = m.make_request('GET', f'/shops/{m.get_shop_id()}/listings/{lid}/files')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} files={f['count']} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
