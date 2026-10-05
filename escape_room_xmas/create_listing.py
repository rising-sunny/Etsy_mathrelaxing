"""Create the Christmas Escape Room as a DRAFT digital Etsy listing (taxonomy 1350
Party Games) with 6 preview images and the US Letter + A4 PDFs."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Christmas Escape Room for Kids, Printable Holiday Puzzle Game, Family Christmas Party Activity, "
         "Logic Brain Teasers Ages 8-13")
PRICE = 9.99
TAXONOMY = 1350
TAGS = ["christmas escape", "escape room kids", "christmas party game", "printable escape", "holiday activity",
        "christmas puzzles", "family game night", "kids christmas game", "brain teasers kids", "classroom christmas",
        "logic puzzles kids", "christmas printable", "escape room game"]

DESC = f"""The Great Workshop Lockdown: a printable Christmas escape room for kids, families and classrooms. The Snow-Lock computer has frozen Santa's toy vault, and only a team of clever elves can crack the code before Santa leaves!

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Download, print at home and play the same day.

HOW IT WORKS
- Players solve 8 Christmas puzzles. Each answer is a number from 1 to 26.
- The Workshop Decoder turns every number into a letter.
- The 8 letters spell the secret password that opens the vault.
If the letters make a real word, the team knows they got everything right, so the game checks itself.

THE 8 PUZZLES
1. Candy Cane Code: number patterns
2. Mrs. Claus's Cookie Jar: logic and remainders
3. The Toy Scales: balance puzzles
4. The Magic Ornaments: magic square
5. The Gift Pyramid: addition pyramid
6. Santa's Sleigh Route: shortest path
7. Jingle & Jangle: age riddle
8. The Frozen Message: number code

WHAT'S INCLUDED (16 pages, US Letter and A4)
- Cover and host guide with setup tips
- Mission briefing with a start-time box
- 8 full-page puzzles, each with its own lock box
- Vault page with the decoder and password boxes
- 8 cut-out hint cards
- Answer key with a short explanation for every puzzle
- Certificate of Official Elf Engineering
- Terms of use

DETAILS
- Ages 8-13; younger children can play with a grown-up
- 1 to 6 players per printed set
- Takes about 45-60 minutes
- Every answer has been checked and verified
- Works for Christmas parties, family game night, classroom holiday parties and homeschool

HOW TO USE
1. Download both PDFs from your Etsy purchases and choose US Letter or A4.
2. Print the pages and cut out the hint cards.
3. Hide the puzzles around the room or hand them out one at a time, then start the timer!

For personal, family and single-classroom use. Please do not resell or share the file.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"Christmas_Escape_Room_{name}.pdf"))
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])}")


if __name__ == "__main__":
    main()
