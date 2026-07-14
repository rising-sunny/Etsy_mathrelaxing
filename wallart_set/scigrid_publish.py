"""
scigrid_publish.py — create the Etsy DRAFT for the Engineering & Science Graph
Paper bundle (8 technical grids). Title avoids ^, = and + and uses <=1 '&'.

    python wallart_set/scigrid_publish.py     (run from repo root)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
EDITION = os.environ.get("SCIGRID_EDITION", "earth")
TAX = 2078
PRICE = 3.49
SLUG = "EngineeringScienceGraphPaper"

TITLE = ("Engineering Graph Paper Bundle | 8 STEM Grids: Log-Log, Semi-Log, Millimeter, "
         "Polar, Cartesian | Printable GoodNotes Digital Download")
TAGS = ["graph paper", "engineering paper", "log log paper", "semi log paper", "stem printable",
        "math graph paper", "polar graph paper", "millimeter paper", "cartesian plane",
        "goodnotes paper", "printable paper", "digital download", "science paper"]

DESC = (
    "Engineering & Science Graph Paper — 8 technical grids the way STEM actually needs them.\n\n"
    "Not decorative paper: real log-log and semi-log grids with labelled decades, a numbered "
    "Cartesian plane, engineering 5x5, true millimeter paper, polar in degrees, log-polar and "
    "isometric 3D. Every grid is computed to scale — perfect for lab reports, physics, calculus, "
    "engineering sketches and data plots.\n\n"
    "8 GRIDS INCLUDED\n"
    "- Engineering 5x5      - Millimeter (mm)\n"
    "- Log-Log              - Semi-Log\n"
    "- Cartesian plane      - Polar (degrees)\n"
    "- Log-Polar            - Isometric 3D\n\n"
    "WHAT YOU GET (instant download)\n"
    "- US Letter + A4 vector PDF (crisp at any print size)\n"
    "- 300 DPI PNG of every grid for GoodNotes, Notability or any iPad note app\n"
    "- Delivered as one ZIP\n\n"
    "Print at home or import to your tablet. For personal use; not for resale or redistribution.\n\n"
    "(c) MathRelaxing"
)


def main():
    base = os.path.join(HERE, "out", "scigrid", EDITION)
    imgs = [os.path.join(base, "listing", f"{n}.jpg")
            for n in ["01_hero", "02_ipad", "03_closeups", "04_included", "05_how"]]
    zip_ = os.path.join(base, f"{SLUG}_{EDITION}.zip")
    assert len(TITLE) <= 140 and TITLE.count("&") <= 1 and not any(c in TITLE for c in "^=+"), len(TITLE)
    assert len(TAGS) <= 13 and all(len(t) <= 20 for t in TAGS), max(len(t) for t in TAGS)
    for f in imgs + [zip_]:
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
    retry(lambda: m.upload_listing_file(lid, zip_))
    print(f"DRAFT [scigrid]: {lid}  (${PRICE})  title={len(TITLE)}  tags={len(TAGS)}")


if __name__ == "__main__":
    main()
