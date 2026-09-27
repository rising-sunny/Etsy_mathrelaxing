"""Create the 2027 STEM Planner as a DRAFT digital Etsy listing (taxonomy 12476
Planner Templates) with 6 preview images and the Monday + Sunday start PDFs."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("2027 Digital Planner for Students, Hyperlinked STEM Planner for GoodNotes and Notability, "
         "Dated Weekly and Monthly Academic Planner")
PRICE = 11.99
TAXONOMY = 12476
TAGS = ["2027 digital planner", "2027 student planner", "goodnotes planner", "stem planner",
        "academic planner", "hyperlinked planner", "notability planner", "college planner",
        "ipad planner", "study planner", "grad school planner", "weekly planner 2027", "semester planner"]

DESC = f"""A dated 2027 digital planner built for STEM students and researchers — every page hyperlinked, every tool you actually use for classes, labs and exams.

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Import the PDF into GoodNotes, Notability, Xodo, Noteshelf or any PDF annotation app and start planning right away.

WHAT'S INSIDE (100 pages, landscape)
- Cover, index and "how to navigate" guide
- 2027 goals and year at a glance
- Spring and Fall semester planners (courses, credits, exam dates, key deadlines)
- 12 monthly calendars (January to December 2027) with focus and deadline columns
- 12 monthly habit trackers with monthly reflection
- 53 weekly spreads covering every day of 2027, with top 3 priorities, study-hours tracker and notes
- Assignment tracker, exam planner, grade and GPA tracker
- Study session log (25-minute focus blocks), project planner
- Lab notebook (method + observations beside a graph grid)
- Reading and research log, Cornell notes, formula sheet
- Graph paper, dot grid and lined note pages

HYPERLINKED
Side tabs on every page jump to the index, year, any of the 12 months, the tools and the notes. On a month page, tap any date to open that week's spread; week pages have previous / next links, and each month links to its habit tracker. Over 2,000 links in total.

TWO VERSIONS INCLUDED
- Monday start
- Sunday start

HOW TO USE
1. Download both PDFs from your Etsy purchases.
2. Open your preferred version in your note-taking app (use "Import" or "Open in").
3. Use it in read-only / hyperlink mode to jump around, and write with your stylus.
4. Duplicate the notes, lab or Cornell pages whenever you need more.

Works best on iPad and Android tablets. It can also be printed, although the hyperlinks only work digitally.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Monday", "Sunday"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"2027_STEM_Planner_{name}_Start.pdf"))
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])}")


if __name__ == "__main__":
    main()
