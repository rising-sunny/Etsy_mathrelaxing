"""Create the Geometric 3D Paper Ornaments pack as a DRAFT digital Etsy listing (taxonomy
6343 Patterns & Blueprints) with 7 images, both PDFs and the SVG zip."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Geometric 3D Paper Ornament Templates, 12 Printable Polyhedra and Moravian Star, Christmas Paper Craft, "
         "Dodecahedron Kepler Star")
PRICE = 6.99
TAXONOMY = 6343
SECTION = 60740209  # Christmas
TAGS = ["paper ornaments", "3d paper ornament", "moravian star", "polyhedra template", "dodecahedron",
        "geometric ornament", "christmas papercraft", "paper star template", "platonic solids", "math christmas",
        "printable ornament", "diy ornament", "3d star template"]

DESC = f"""Fold your own geometric Christmas ornaments: 12 printable 3D paper templates, from a simple tetrahedron to Kepler's star and the 26-point Moravian Advent star. Every net is computed from exact geometry, printed at real size and ready to cut, fold and glue.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Print on card stock at home and start folding the same day.

THE 12 ORNAMENTS (finished size 8-12 cm / 3-5 in)
Platonic solids: tetrahedron, cube, octahedron, dodecahedron, icosahedron
Archimedean solids: cuboctahedron, truncated octahedron, rhombicuboctahedron, truncated icosahedron (the classic football)
Christmas stars: stella octangula (8 points), Kepler's star / small stellated dodecahedron (12 golden-triangle points), Moravian star (26 points)

WHAT YOU GET
- Geometric_Paper_Ornaments_Letter.pdf and Geometric_Paper_Ornaments_A4.pdf (40 pages each)
- Colour templates in red, green, gold and navy with a snowflake on every face
- The same templates in plain white for coloured, kraft or metallic card
- Clear cut lines, dashed fold lines and grey glue tabs
- A 2 cm / 1 inch scale bar on every page to check the print size
- Step-by-step instructions and tips for the stars
- "The math behind the ornaments": Platonic solids, Euler's formula, Archimedean solids, Kepler's star and the golden ratio
- Geometric_Paper_Ornaments_SVG.zip: real-size SVG files (mm) with separate print, score and cut layers, compatible with Cricut and Silhouette cutting machines

DIFFICULTY
From easy (tetrahedron, cube, octahedron: great first projects and fun with kids) to advanced (football, Kepler and Moravian stars). Each model takes about 20-90 minutes.

YOU WILL NEED
Card stock 160-250 gsm (65-110 lb), ruler, scissors or craft knife, an empty ballpoint pen for scoring, glue stick or craft glue, and thread or ribbon to hang.

GREAT FOR
- Christmas tree decorations and garlands
- Advent crafts with kids and teens
- Math classrooms in December (geometry, nets, Euler's formula)
- Gift toppers and table decorations

For personal, family and single-classroom use. Please do not resell the files or the finished ornaments, or share the files.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    out = os.path.join(HERE, "out")
    files = [os.path.join(out, f) for f in ("Geometric_Paper_Ornaments_Letter.pdf", "Geometric_Paper_Ornaments_A4.pdf",
                                            "Geometric_Paper_Ornaments_SVG.zip")]
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
