"""Create the Christmas STEM Challenge Cards as a DRAFT digital Etsy listing
(taxonomy 12471 Worksheets) with 6 preview images and the US Letter + A4 PDFs."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Christmas STEM Challenge Cards, 24 Printable Holiday STEM Activities for Kids, Classroom Engineering "
         "Challenges with Design Journal")
PRICE = 6.99
TAXONOMY = 12471
SECTION = 60740209  # Christmas
TAGS = ["christmas stem", "stem challenge cards", "stem activities", "christmas classroom", "holiday stem",
        "engineering for kids", "stem task cards", "december activities", "homeschool christmas",
        "christmas science", "kids stem printable", "christmas activity", "steam activities"]

DESC = f"""24 hands-on Christmas STEM challenge cards that turn tape, paper, cups and candy canes into real engineering, science, motion and math investigations. Perfect for December classrooms, homeschool, holiday parties and snowy afternoons at home.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Download, print and start building the same day.

WHAT'S ON EVERY CARD
- The challenge
- What you need (simple household and classroom materials)
- Test it: how to measure and compare the results
- Level Up: an extra challenge for fast finishers

THE 24 CHALLENGES
Build: Gumdrop Tree Tower, Candy Cane Bridge, Paper Chain Challenge, Reindeer Stable, Strong Columns, Cup Christmas Tree, Earthquake Gingerbread House
Science: Floating Gift Boat, Candy Cane Melt, Static Snow, Save the Snowman, Balancing Elf, Jingle Bell Band, Snow Globe Science, Rudolph's Shadow
Motion: Ornament Parachute, Sleigh Ramp, Santa's Zip Line, Elf Catapult, Chimney Marble Drop
Math: Snowflake Symmetry, Perfect Present Box, Gumdrop Shapes, Binary Ornament

WHAT'S INCLUDED (15 pages, US Letter and A4)
- Cover and teacher & parent guide
- Engineering design process poster (ask, imagine, plan, create, test, improve)
- Materials checklist
- 24 challenge cards, 4 per page, ready to cut
- Design journal page and data sheet with a graph grid
- "My Challenge Tree" tracker: color an ornament for every challenge
- Christmas STEM Engineer certificate

IDEAS FOR USE
- A December countdown: one card a day
- STEM stations for a class Christmas party
- Early-finisher or indoor-recess activities
- Family challenges over the winter break

DETAILS
- Ages 6-12; younger children can work in pairs with an adult
- Most challenges take 20-45 minutes
- Tip: print the card pages on card stock

For personal, family and single-classroom use. Please do not resell or share the file.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"Christmas_STEM_Challenge_Cards_{name}.pdf"))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
