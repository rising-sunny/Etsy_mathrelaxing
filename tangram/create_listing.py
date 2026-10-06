"""Create the Tangram Puzzle Pack as a DRAFT digital Etsy listing (section Puzzles)."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Tangram Puzzles Printable, 45 Actual-Size Tangram Cards with Pieces and Solutions, "
         "Math Puzzle for Kids, Homeschool Geometry")
PRICE = 5.99
TAXONOMY = 12626
SECTION = 60521322  # Puzzles
TAGS = ["tangram", "tangram printable", "tangram puzzles", "tangram cards", "math puzzles kids",
        "geometry activity", "homeschool math", "shape puzzles", "quiet time activity", "kids puzzle game",
        "stem activity", "logic puzzles kids", "brain teasers"]

DESC = f"""Tangram Puzzle Pack: 45 actual-size tangram silhouettes with printable pieces and full-colour solutions. Print, cut out the seven pieces, and lay them right on the page to cover each shape.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. US Letter and A4 versions are included.

WHAT'S INCLUDED (about 40 pages)
- How-to-play guide and printing tips
- 2 sets of colour cut-out pieces + 1 set to colour or print on cardstock
- 45 silhouettes printed at the same size as the pieces
- Progress checklist for all 45 shapes
- Colour solutions for every puzzle
- "The Math Inside" page: fractions, area, angles and square roots with tangram pieces

FOUR LEVELS
- Level 1, Warm-Up (11): every piece outline is shown, perfect for young children
- Level 2, Explorer (11): only the two large triangles are shown
- Level 3, Master (10): silhouette only
- Level 4, The 13 Convex Shapes (13): in 1942 two mathematicians proved that the seven tangram pieces can make exactly 13 convex shapes. All 13 are here, with a short, kid-friendly explanation of the theorem

SHAPES YOU'LL BUILD
Cat, fish, rabbit, swan, chicken, elephant, camel, horse, whale, goose, teapot, sleigh, Christmas stocking, Christmas ornament, pine tree, castle, rocket, house, the number 2 and more.

EVERY PUZZLE HAS A SOLUTION
Each silhouette was built by a computer program that fits the seven real pieces together, then checked for overlaps, so every puzzle is guaranteed to be solvable.

GREAT FOR
Homeschool and classroom geometry, math centers, quiet time, road trips, busy bags and family game night. Ages 5 and up (Levels 3 and 4 challenge adults too).

TIPS
Print at 100% / Actual size so the pieces match the silhouettes. Laminate the puzzle pages to reuse them with dry-erase markers or real tangram sets of the same size (square side 7.07 cm / 2.78 in).

For personal, family and single-classroom use. Please do not resell or share the file.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS), (len(TITLE), [t for t in TAGS if len(t) > 20])
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"Tangram_Puzzles_{name}.pdf"))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
