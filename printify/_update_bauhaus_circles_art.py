"""
Re-upload fixed Circles & Bars art and update Printify product + republish to Etsy.
Product: Bauhaus Poster | Geometric Wall Art Circles and Bars | ...
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import printify_publish as pp  # noqa: E402
from batch_wave12_create import GROUPS  # noqa: E402

ROOT = HERE.parent
PRODUCT_ID = "6a5bf199f45e269c8f0106f0"
FOLDER = ROOT / "bauhaus_set" / "prints" / "01_circles_bars"
FILES = {
    "2x3": "01_circles_bars_2x3_12x18_300dpi.jpg",
    "3x4": "01_circles_bars_3x4_12x16_300dpi.jpg",
    "4x5": "01_circles_bars_4x5_16x20_300dpi.jpg",
}


def main():
    print("=== GET product", PRODUCT_ID)
    prod = pp.get_product(PRODUCT_ID)
    print("  title:", prod.get("title"))
    print("  variants enabled:", sum(1 for v in prod.get("variants", []) if v.get("is_enabled")))

    print("\n=== UPLOAD fixed art")
    image_ids = {}
    for ratio, fname in FILES.items():
        path = FOLDER / fname
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        image_ids[ratio] = pp.upload_image(str(path), f"bauhaus_circles_fixed_{ratio}.jpg")

    # Preserve existing print_area groups (Printify requires every variant listed).
    # Map group index → art ratio used at creation: 0=2x3, 1=3x4, 2=4x5 (catch-all).
    ratio_by_group = {0: "2x3", 1: "3x4", 2: "4x5"}
    print_areas = []
    for i, pa in enumerate(prod.get("print_areas") or []):
        ratio = ratio_by_group.get(i, "4x5")
        img_id = image_ids[ratio]
        print_areas.append(
            {
                "variant_ids": pa["variant_ids"],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": img_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0,
                            }
                        ],
                    }
                ],
            }
        )
        print(f"  group {i} ratio={ratio} vids={len(pa['variant_ids'])} img={img_id}")

    # Keep existing variant enablement/prices
    variants = [
        {
            "id": v["id"],
            "price": v["price"],
            "is_enabled": bool(v.get("is_enabled")),
        }
        for v in prod.get("variants", [])
    ]

    payload = {
        "title": prod.get("title"),
        "description": prod.get("description"),
        "tags": prod.get("tags") or [],
        "variants": variants,
        "print_areas": print_areas,
    }

    print("\n=== PUT update print areas")
    updated = pp._req("PUT", f"/shops/{pp.SHOP_ID}/products/{PRODUCT_ID}.json", payload)
    print("  updated id:", updated.get("id") or PRODUCT_ID)
    print("  images on product:", len(updated.get("images") or prod.get("images") or []))

    print("\n=== PUBLISH to Etsy (sync images)")
    pub = pp.publish_product(PRODUCT_ID)
    print("  publish response:", json.dumps(pub)[:400])
    print("DONE")


if __name__ == "__main__":
    main()
