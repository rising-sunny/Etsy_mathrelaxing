"""Upload a single equation-plate product as an Etsy draft; patch listing_id.

    python _upload_normal_distribution.py [slug]   # defaults to normal_distribution_print
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS, check_product_files

SLUG = sys.argv[1] if len(sys.argv) > 1 else "normal_distribution_print"


def patch_listing_id(slug: str, listing_id: int):
    path = Path(__file__).resolve().parent / "products_catalog.py"
    text = path.read_text(encoding="utf-8")
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
    prod = PRODUCTS[SLUG]
    print(f"=== {SLUG} @ ${prod['price']:.2f} ===")
    print(f"  title ({len(prod['title'])} chars): {prod['title']}")
    assert len(prod["title"]) <= 140, "title too long"
    if not check_product_files(SLUG):
        raise SystemExit("missing files")
    lid = m.create_full_product(
        title=prod["title"],
        description=prod["description"],
        price=prod["price"],
        taxonomy_id=prod["taxonomy_id"],
        image_paths=prod["images"],
        digital_file_paths=prod["files"],
        tags=prod.get("tags"),
    )
    try:
        m.update_listing_price(lid, prod["price"])
    except Exception as e:
        print(f"  price verify warn: {e}")
    patch_listing_id(SLUG, lid)
    print(f"  DRAFT https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
