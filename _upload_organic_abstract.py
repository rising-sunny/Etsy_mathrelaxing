"""Upload the 'Computed Organic Abstract' listing; save listing_id.

Creates it as a draft, but expect it to go live on its own: this shop's drafts
have flipped to active a few minutes after upload, apparently once Etsy finishes
processing the attached file. The STEM kit read `draft` on the check straight
after creation and was active by the next time anything looked. Treat the upload
itself as publishing, and verify the state afterwards rather than trusting the
reading taken at creation time.
"""
from __future__ import annotations

import re
from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS, check_product_files

SLUG = "organic_abstract"


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
        print(f"  WARN: no pude escribir listing_id para {slug}")


def main():
    m = EtsyManager()
    prod = PRODUCTS[SLUG]
    print(f"\n=== {SLUG} @ ${prod['price']:.2f} ===")
    if not check_product_files(SLUG):
        return
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
        print(f"  price warn: {e}")
    patch_listing_id(SLUG, lid)

    # Verify what actually landed: price, state, image ranks and the digital
    # file. Image ranks in particular have duplicated silently before.
    shop_id = m.get_shop_id()
    l = m.make_request("GET", f"/listings/{lid}")
    print(f"\n  state={l.get('state')}  price={l.get('price')}  qty={l.get('quantity')}")
    imgs = m.make_request("GET", f"/listings/{lid}/images").get("results", [])
    ranks = [i["rank"] for i in imgs]
    print(f"  imagenes={len(imgs)} ranks={ranks} {'OK' if ranks == sorted(set(ranks)) else 'DUPLICADOS'}")
    files = m.make_request("GET", f"/shops/{shop_id}/listings/{lid}/files").get("results", [])
    for f in files:
        # Etsy devuelve filesize ya formateado ("8.77 MB"), no en bytes.
        print(f"  archivo: {f.get('filename')}  {f.get('filesize')}")
    print(f"\n  DRAFT https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
