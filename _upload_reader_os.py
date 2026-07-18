"""Refresh Reader OS draft listing with upgraded assets + iPad-first copy."""
from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS

KEY = "reader_os_stickers"


def main():
    p = PRODUCTS[KEY]
    lid = p["listing_id"]
    m = EtsyManager()

    print("=== Update listing copy ===")
    m.update_listing(
        lid,
        title=p["title"],
        description=p["description"],
        tags=p["tags"],
    )

    print("=== Refresh images ===")
    imgs = m.make_request("GET", f"/listings/{lid}/images")
    images = imgs.get("results") or imgs.get("images") or []
    print(f"  payload keys: {list(imgs.keys()) if isinstance(imgs, dict) else type(imgs)}")
    print(f"  count: {len(images)}")
    for im in images:
        iid = im.get("listing_image_id") or im.get("image_id")
        if iid:
            try:
                m.delete_listing_image(lid, iid)
            except Exception as e:
                print(f"  skip delete image {iid}: {e}")

    for rank, path in enumerate(p["images"], start=1):
        if Path(path).exists():
            m.upload_listing_image(lid, path, rank=rank)
        else:
            print(f"  MISSING {path}")

    print("=== Cleanup leftover old images (keep only new ranks) ===")
    shop_id = m.get_shop_id()
    imgs = m.make_request("GET", f"/listings/{lid}/images")
    images = imgs.get("results") or []
    # Keep the 6 we just uploaded (highest listing_image_ids / ranks 1-6).
    # Delete any extras with rank > 6 or old ones beyond first 6 by rank.
    keep_ids = set()
    by_rank = {}
    for im in images:
        r = im.get("rank")
        if r is not None and 1 <= int(r) <= 6:
            # prefer newest if duplicates
            by_rank[int(r)] = im
    for im in by_rank.values():
        keep_ids.add(im.get("listing_image_id"))
    for im in images:
        iid = im.get("listing_image_id")
        if iid and iid not in keep_ids:
            try:
                m.delete_listing_image(lid, iid)
            except Exception as e:
                print(f"  skip delete leftover {iid}: {e}")

    print("=== Refresh digital file ===")
    files = m.make_request("GET", f"/shops/{shop_id}/listings/{lid}/files")
    fl = files.get("results") or files.get("files") or []
    print(f"  files count: {len(fl)}")
    for f in fl:
        fid = f.get("listing_file_id") or f.get("file_id")
        if fid:
            try:
                m.delete_listing_file(lid, fid)
            except Exception as e:
                print(f"  skip delete file {fid}: {e}")

    for path in p["files"]:
        if Path(path).exists():
            m.upload_listing_file(lid, path)
        else:
            print(f"  MISSING {path}")

    print("DONE listing", lid)


if __name__ == "__main__":
    main()
