"""Upload equation plate singles + set as Etsy drafts; save listing_ids to catalog."""
from __future__ import annotations

import re
from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS, check_product_files

SLUGS = [
    "euler_identity_print",
    "mandelbrot_set_print",
    "famous_equations_set",
]


def patch_listing_id(slug: str, listing_id: int):
    path = Path(__file__).resolve().parent / "products_catalog.py"
    text = path.read_text(encoding="utf-8")
    # Replace "listing_id": None inside the slug block (first occurrence after key)
    pattern = re.compile(
        rf'("{re.escape(slug)}"\s*:\s*\{{[\s\S]{{0,2500}}?"listing_id"\s*:\s*)None',
        re.MULTILINE,
    )
    new_text, n = pattern.subn(rf"\g<1>{listing_id}", text, count=1)
    if n:
        path.write_text(new_text, encoding="utf-8")
        print(f"  catalog listing_id={listing_id}")
    else:
        print(f"  WARN: could not write listing_id for {slug}")


def main():
    m = EtsyManager()
    for slug in SLUGS:
        prod = PRODUCTS[slug]
        print(f"\n=== {slug} @ ${prod['price']:.2f} ===")
        if not check_product_files(slug):
            continue
        lid = m.create_full_product(
            title=prod["title"],
            description=prod["description"],
            price=prod["price"],
            taxonomy_id=prod["taxonomy_id"],
            image_paths=prod["images"],
            digital_file_paths=prod["files"],
            tags=prod.get("tags"),
        )
        # Ensure inventory price stuck
        try:
            m.update_listing_price(lid, prod["price"])
        except Exception as e:
            print(f"  price verify warn: {e}")
        patch_listing_id(slug, lid)
        print(f"  DRAFT https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
