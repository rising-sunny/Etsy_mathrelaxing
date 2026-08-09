"""
update_turing_posters_images.py — swap in the chrome-free art on the 6
already-created Turing Patterns Printify products (the first render had a
title/caption/border baked into the image; the client wants pure design).

Re-uploads the 3 ratio images per design, PUTs new print_areas onto the
existing product (keeps the same Printify product id / Etsy listing),
then re-publishes so Etsy picks up the new images. Since the previous
publish_product() call unexpectedly activated the listings instead of
leaving them as drafts, this re-checks state after publishing and pulls
any listing that went active back to Etsy's "edit" (unpublished) state.

  python printify/update_turing_posters_images.py
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import printify_publish as pp  # noqa: E402
from create_turing_posters import GROUPS, DESIGNS, PRINTS  # noqa: E402
import json

from etsy_manager import EtsyManager  # noqa: E402

CREATED = json.loads((HERE / "turing_posters_created.json").read_text(encoding="utf-8"))
BY_KEY = {row["key"]: row["printify_id"] for row in CREATED}

# Etsy listing ids gathered after the first publish (see session record)
ETSY_LISTING_IDS = {
    "leopard_rosettes": 4552496574,
    "pufferfish_mesh": 4552496606,
    "brain_coral": 4552496636,
    "tiger_current": 4552496666,
    "fingerprint_whorl": 4552484155,
    "cuttlefish_static": 4552484195,
}


def main():
    for slug, name, title, blurb, footer_tag, tags in DESIGNS:
        pid = BY_KEY[slug]
        print(f"\n=== UPDATE {slug} (printify {pid}) ===")
        pd = PRINTS / slug
        image_ids = {}
        for ratio in ("2x3", "3x4", "4x5"):
            path = pd / f"{slug}_{ratio}.jpg"
            image_ids[ratio] = pp.upload_image(str(path), f"{slug}_{ratio}_v2.jpg")
            time.sleep(0.4)

        # PUT validates that *every* variant on the product (including the
        # square/other sizes we left disabled at creation) is covered by some
        # print_area's variant_ids -- not just our 9 enabled poster sizes.
        # Round-trip the product's own current variants unchanged, and fold
        # any variant id our GROUPS dict doesn't mention into the 3x4 area
        # (harmless: those variants are disabled, never actually printed).
        current = pp.get_product(pid)
        variants_payload = [{"id": v["id"], "price": v["price"], "is_enabled": v["is_enabled"]}
                             for v in current["variants"]]
        all_variant_ids = [v["id"] for v in current["variants"]]
        covered = {vid for vids in GROUPS.values() for vid in vids}
        leftover = [vid for vid in all_variant_ids if vid not in covered]

        print_areas = []
        for ratio, vids in GROUPS.items():
            vids = vids + leftover if ratio == "3x4" else vids
            print_areas.append({
                "variant_ids": vids,
                "placeholders": [{"position": "front", "images": [
                    {"id": image_ids[ratio], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
            })
        pp.update_product(pid, {"variants": variants_payload, "print_areas": print_areas})
        print("  print_areas updated")
        time.sleep(0.5)

        pp.publish_product(pid)
        print("  re-published")
        time.sleep(1.5)

    print("\n=== verifying Etsy state, pulling back anything that went active ===")
    m = EtsyManager()
    for slug, lid in ETSY_LISTING_IDS.items():
        r = m.make_request("GET", f"/listings/{lid}")
        state = r.get("state")
        print(f"  {slug} ({lid}): {state}")
        if state == "active":
            m.update_listing(lid, state="inactive")
            print("    -> pulled back to edit/inactive")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
