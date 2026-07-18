"""
publish_listing.py — create the Etsy DRAFT for a collection+palette wall-art set.
Copy lives in each collection module's LISTINGS. Draft only; activation manual.

    WALLART_MODULE=designs_geo WALLART_PALETTE=mono python wallart_set/publish_listing.py
    (run from the repo root so etsy_token.json resolves)
"""
import os
import sys
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import etsy_manager

HERE = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_ID = 2078   # Art & Collectibles > Prints > Digital Prints
IMG_ORDER = ["01_hero_gallery", "02_room", "04_included", "03_detail", "05_sizes", "06_how"]
RATIOS = ["2x3", "3x4", "4x5", "5x7", "ISO"]


def main():
    designs = importlib.import_module(os.environ.get("WALLART_MODULE", "designs"))
    pal = os.environ.get("WALLART_PALETTE", "earth")
    cfg = designs.LISTINGS[pal]
    base = os.path.join(HERE, "out", designs.COLLECTION, pal)
    images = [os.path.join(base, "listing", f"{n}.jpg") for n in IMG_ORDER]
    files = [os.path.join(base, "zips", f"{designs.SLUG}_{pal}_{r}.zip") for r in RATIOS]

    assert len(cfg["title"]) <= 140, f"title too long: {len(cfg['title'])}"
    assert cfg["title"].count("&") <= 1, "more than one & in title"
    assert len(cfg["tags"]) <= 13 and all(len(t) <= 20 for t in cfg["tags"]), "tag limits"
    for f in images + files:
        assert os.path.exists(f), f"missing {f}"

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(cfg["title"], cfg["description"], cfg["price"],
                                 TAXONOMY_ID, is_digital=True, tags=cfg["tags"])
    for rank, img in enumerate(images, start=1):
        m.upload_listing_image(lid, img, rank=rank)
    for f in files:
        m.upload_listing_file(lid, f)
    print(f"\nDRAFT [{designs.COLLECTION}/{pal}] creado: {lid}  "
          f"(${cfg['price']}, {len(images)} imagenes, {len(files)} zips)")
    print(f"title chars: {len(cfg['title'])}")
    return lid


if __name__ == "__main__":
    main()
