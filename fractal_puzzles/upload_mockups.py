"""Replace the flat-only Printify images on each fractal puzzle Etsy listing
with the new puzzle mockups (studio product shot, wood-table lifestyle, flat).

  python upload_mockups.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager

OUT = os.path.join(HERE, "mockups")

# slug -> Etsy listing id
LISTINGS = {
    "julia_dense": 4577917562,      # Julia Filament
    "julia_pinwheel": 4577917696,   # Julia Pinwheel
    "chaos_6": 4577901321,          # 6 Magnets
    "chaos_5": 4577917902,          # 5 Magnets
}


def main():
    m = EtsyManager()
    shop_id = m.get_shop_id()
    for slug, lid in LISTINGS.items():
        print(f"\n=== {slug} -> {lid} ===")
        # existing images
        cur = m.make_request('GET', f'/listings/{lid}/images')
        ids = [im['listing_image_id'] for im in cur.get('results', [])]
        print("  existentes:", ids)
        # upload new mockups first (ranks 1..3), then delete old ones
        for rank, suffix in enumerate([1, 2, 3], start=1):
            path = os.path.join(OUT, f"{slug}_{suffix}.jpg")
            m.upload_listing_image(lid, path, rank=rank)
        for iid in ids:
            m.delete_listing_image(lid, iid)
        print(f"  hecho: {lid}")


if __name__ == "__main__":
    main()
