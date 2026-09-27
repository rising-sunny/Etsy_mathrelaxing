"""Create the STEM Advent Calendar as a DRAFT digital Etsy listing
(taxonomy 6098 Advent Calendars), with 6 preview images and the Letter + A4 PDFs.

  python create_listing.py
"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager

TITLE = ("STEM Advent Calendar Printable, 24 Days of Math and Science Puzzles, "
         "Experiments and Facts for Kids, Christmas Countdown Activity")
PRICE = 14.99
TAXONOMY = 6098  # Paper & Party Supplies > Calendars & Planners > Advent Calendars
TAGS = ["stem advent calendar", "math advent calendar", "advent calendar kids",
        "christmas countdown", "printable advent", "science activities", "stem activities",
        "christmas math", "homeschool advent", "math puzzles kids", "december activity",
        "holiday stem", "christmas printable"]

DESC = """Count down to Christmas with a new math or science discovery every day.

INSTANT DOWNLOAD
This is a digital file — nothing is shipped. Print at home as soon as payment clears, and re-download any time from You > Purchases and reviews.

WHAT IT IS
A printable STEM advent calendar with 24 daily cards, one for each day from 1 to 24 December. Each card is one of three kinds:
- PUZZLE — a logic or math challenge to think through (answers at the back)
- EXPERIMENT — a quick, kitchen-safe mini experiment
- FACT — a true, surprising science idea with a tiny hands-on activity

A few examples: how many gifts are there in all Twelve Days of Christmas? Why do raisins dance in fizzy water? How can salt let you "fish" an ice cube out with a string? Why does a pine cone hide Fibonacci numbers? And the grand finale on Christmas Eve: decode a secret message.

WHAT'S INCLUDED (12 pages, US Letter AND A4)
- Cover page
- How-to-use page with card types and safety notes
- Hangable 24-door countdown board to colour in, one door a day
- 24 day cards, 4 per page, with cut lines and space to write answers, record observations or draw
- Full answer key with a short explanation for every card
- Terms of use

HOW TO USE
1. Print the board and hang it up.
2. Print the cards (card stock works best), cut them out and stack them — or tuck one into each pocket of a real advent calendar.
3. Open one card a day, then colour that day's door on the board.

PERFECT FOR
Families counting down to Christmas, homeschool December units, classroom morning work and early finishers, and curious kids aged about 8 to 14. A screen-free holiday tradition.

SAFETY
Experiments use everyday kitchen materials and are designed for children with an adult nearby. Warm water only, never boiling, and the materials are not for eating.

TERMS OF USE
For personal, family and single-classroom use. Print as many copies as your own household or class needs. Please do not resell, share the file or post it anywhere the public can download it. Every puzzle, fact and illustration is original work by MathRelaxing; answers were checked by hand. If you ever spot an error, send a message here on Etsy and a corrected file will be sent free.

Thanks for visiting MathRelaxing."""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"STEM_Advent_Calendar_{name}.pdf"))
    print(f"\nDRAFT listing {lid}: https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
