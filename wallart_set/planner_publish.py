"""
planner_publish.py — Etsy DRAFT for the Relaxing Planner bundle: 2026-2027
academic (dated) + undated, hyperlinked GoodNotes/iPad. Two PDF files + 5
listing images. Title avoids ^, = and + and uses <=1 '&'.

    python wallart_set/planner_publish.py     (run from repo root)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
TAX = 2078
PRICE = 7.99

TITLE = ("2026-2027 Academic Digital Planner Bundle | Hyperlinked GoodNotes iPad Planner "
         "| Dated plus Undated | Student Weekly | Instant Download")
TAGS = ["digital planner", "goodnotes planner", "academic planner", "2026 2027 planner",
        "student planner", "ipad planner", "undated planner", "hyperlinked planner",
        "weekly planner", "teacher planner", "notability planner", "planner bundle",
        "digital download"]

DESC = (
    "The Relaxing Planner - a fully hyperlinked digital planner for GoodNotes, Notability "
    "and any PDF app on iPad or tablet. You get BOTH versions:\n\n"
    "- 2026-2027 ACADEMIC (dated): real month calendars, August 2026 through July 2027\n"
    "- UNDATED: reuse it every year, forever\n\n"
    "FULLY HYPERLINKED\n"
    "- Month tabs down every page - tap to jump straight there\n"
    "- Year to Month to Week, all interlinked (1,200+ real PDF links)\n"
    "- Top navigation to Year and Notes on every page\n\n"
    "WHAT'S INSIDE (80 pages each)\n"
    "- Cover and year-at-a-glance\n"
    "- 12 monthly spreads with a full calendar\n"
    "- 60 weekly pages (day rows, priorities, dot notes)\n"
    "- 6 note papers (dot, square, Cornell, ruled, isometric, Penrose)\n\n"
    "Vector pages - crisp at any zoom, tiny file. Portrait, US Letter proportions.\n\n"
    "INSTANT DOWNLOAD - two PDF files. For personal use; not for resale or redistribution.\n"
    "A tablet and a note app (GoodNotes / Notability) are recommended.\n\n"
    "(c) MathRelaxing"
)

FILES = [
    os.path.join(HERE, "out", "planner", "academic-2026-2027",
                 "RelaxingPlanner_Academic_2026-2027_GoodNotes.pdf"),
    os.path.join(HERE, "out", "planner", "earth",
                 "RelaxingPlanner_earth_GoodNotes.pdf"),
]


def main():
    imgs = [os.path.join(HERE, "out", "planner", "listing", f"{n}.jpg")
            for n in ["01_hero", "02_ipad", "03_pages", "04_features", "05_how"]]
    assert len(TITLE) <= 140 and TITLE.count("&") <= 1 and not any(c in TITLE for c in "^=+"), len(TITLE)
    assert len(TAGS) <= 13 and all(len(t) <= 20 for t in TAGS), max(len(t) for t in TAGS)
    for f in imgs + FILES:
        assert os.path.exists(f), f

    def retry(fn, tries=5):
        for k in range(tries):
            try:
                return fn()
            except Exception as e:
                print("  retry", k, str(e)[:70]); time.sleep(1.5 * (k + 1))
        raise RuntimeError("upload failed after retries")

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAX, is_digital=True, tags=TAGS)
    for r, im in enumerate(imgs, 1):
        retry(lambda im=im, r=r: m.upload_listing_image(lid, im, rank=r))
        time.sleep(0.6)
    for f in FILES:
        retry(lambda f=f: m.upload_listing_file(lid, f))
        time.sleep(0.6)
    print(f"DRAFT [planner]: {lid}  (${PRICE})  title={len(TITLE)}  files={len(FILES)}")


if __name__ == "__main__":
    main()
