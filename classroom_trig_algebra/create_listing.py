"""Create the Trig & Algebra Classroom Poster Set as a DRAFT digital Etsy listing (taxonomy 2078)."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Trig and Algebra Classroom Posters Set of 10, Unit Circle, SOHCAHTOA, Quadratic Formula, Exponent Rules, "
         "Math Classroom Decor")
PRICE = 12.99
TAXONOMY = 2078
SECTION = 60537999  # Education
TAGS = ["math posters", "math classroom decor", "unit circle poster", "trig posters", "algebra posters",
        "sohcahtoa poster", "quadratic formula", "exponent rules", "math classroom", "high school math",
        "math teacher gift", "classroom posters", "trigonometry"]

DESC = f"""Trig & Algebra Classroom Poster Set: 10 bright, colour-coded math posters designed for a real classroom wall. Clear titles, big formulas and simple diagrams that students can read from the back row.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Print at home, at school or at any print shop.

THE 10 POSTERS
1. The Unit Circle: every angle in degrees and radians, with exact coordinates
2. SOH CAH TOA: colour-coded opposite, adjacent and hypotenuse
3. Special Right Triangles: 45-45-90, 30-60-90 and a table of exact values
4. Trig Identities: reciprocal, quotient, Pythagorean, double angle, sum and difference, even/odd
5. Graphs of Trig Functions: sine, cosine and tangent with period and asymptotes
6. Law of Sines & Law of Cosines: when to use each, plus the triangle area formula
7. Order of Operations: PEMDAS steps with a worked example
8. Slope & Linear Equations: slope formula, rise over run, the three forms of a line, four kinds of slope
9. The Quadratic Formula: with the vertex and the discriminant explained
10. Laws of Exponents: eight rules, each with an example

PRINT ANY SIZE (5 vector PDF files, 10 pages each)
- 18 x 24 in poster
- 11 x 17 in (tabloid) and A3
- US Letter and A4
Vector files stay perfectly sharp at every size. Every formula is typeset like a textbook.

GREAT FOR
Algebra 1 & 2, Geometry, Precalculus and Trigonometry classrooms, math bulletin boards, tutoring rooms, homeschool walls and student binders.

For use in your own classroom or home. Please do not resell or share the files.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS), (len(TITLE), [t for t in TAGS if len(t) > 20])
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("18x24", "11x17", "A3", "Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", "pdf", f"Trig_Algebra_Classroom_Posters_{name}.pdf"))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
