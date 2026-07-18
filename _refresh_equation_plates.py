"""Replace images + digital files on equation plate drafts after redesign."""
from __future__ import annotations

from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS

SLUGS = [
    "fourier_series_print",
    "wave_equation_print",
    "dirac_equation_print",
    "navier_stokes_print",
    "euler_identity_print",
    "mandelbrot_set_print",
    "famous_equations_set",
]


def money(p) -> float:
    if isinstance(p, dict):
        return p["amount"] / p["divisor"]
    return float(p or 0)


def main():
    m = EtsyManager()
    shop = m.get_shop_id()
    for slug in SLUGS:
        prod = PRODUCTS[slug]
        lid = prod.get("listing_id")
        if not lid:
            print(f"SKIP {slug}: no listing_id")
            continue
        print(f"\n=== {slug} lid={lid} ===")

        # images: delete all but last, upload new, delete leftover
        imgs = m.make_request("GET", f"/listings/{lid}/images").get("results") or []
        for im in imgs[:-1]:
            try:
                m.delete_listing_image(lid, im["listing_image_id"])
            except Exception as e:
                print(f"  del img warn: {e}")
        for rank, path in enumerate(prod["images"], start=1):
            if Path(path).exists():
                m.upload_listing_image(lid, path, rank=rank)
        # remove any leftover beyond new set
        imgs2 = m.make_request("GET", f"/listings/{lid}/images").get("results") or []
        keep = set()
        by_rank = {}
        for im in imgs2:
            r = int(im.get("rank") or 0)
            if 1 <= r <= len(prod["images"]):
                by_rank[r] = im
        for im in by_rank.values():
            keep.add(im["listing_image_id"])
        for im in imgs2:
            iid = im["listing_image_id"]
            if iid not in keep:
                try:
                    m.delete_listing_image(lid, iid)
                except Exception as e:
                    print(f"  leftover img: {e}")

        # digital file
        try:
            files = m.make_request("GET", f"/shops/{shop}/listings/{lid}/files").get("results") or []
        except Exception:
            files = []
        for f in files:
            fid = f.get("listing_file_id")
            if fid:
                try:
                    m.delete_listing_file(lid, fid)
                except Exception as e:
                    print(f"  del file warn: {e}")
        for path in prod["files"]:
            if Path(path).exists():
                m.upload_listing_file(lid, path)

        # keep price
        try:
            m.update_listing_price(lid, prod["price"])
        except Exception as e:
            print(f"  price warn: {e}")

        check = m.make_request("GET", f"/listings/{lid}")
        print(f"  OK price=${money(check.get('price')):.2f} imgs={len(prod['images'])}")


if __name__ == "__main__":
    main()
