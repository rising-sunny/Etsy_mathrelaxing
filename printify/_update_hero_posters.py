"""
Upload hero-monumental art and update Printify products (Fourier, Euler, Wave).
Preserves existing print_area variant groups; republishes to Etsy.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import printify_publish as pp  # noqa: E402

HERO = ROOT / "equation_plates" / "_hero_pod"

PRODUCTS = [
    {
        "key": "fourier",
        "printify_id": "6a5bf0f381cebb5bdd03a737",
        "slug": "fourier_series",
        "files": {
            "2x3": "fourier_series_2x3_300dpi.jpg",
            "3x4": "fourier_series_3x4_300dpi.jpg",
            "4x5": "fourier_series_4x5_300dpi.jpg",
        },
    },
    {
        "key": "euler",
        "printify_id": "6a5bf105dde591a5200a7d9d",
        "slug": "euler_identity",
        "files": {
            "2x3": "euler_identity_2x3_300dpi.jpg",
            "3x4": "euler_identity_3x4_300dpi.jpg",
            "4x5": "euler_identity_4x5_300dpi.jpg",
        },
    },
    {
        "key": "wave",
        "printify_id": "6a5bf113dde591a5200a7da6",
        "slug": "wave_equation",
        "files": {
            "2x3": "wave_equation_2x3_300dpi.jpg",
            "3x4": "wave_equation_3x4_300dpi.jpg",
            "4x5": "wave_equation_4x5_300dpi.jpg",
        },
    },
]

# Creation order of print_area groups: 0=2x3, 1=3x4, 2=4x5 (catch-all remainder)
RATIO_BY_GROUP = {0: "2x3", 1: "3x4", 2: "4x5"}


def update_one(spec: dict) -> dict:
    pid = spec["printify_id"]
    folder = HERO / spec["slug"]
    print(f"\n=== {spec['key']}  {pid} ===")
    prod = pp.get_product(pid)
    print("  title:", (prod.get("title") or "")[:70])
    n_areas = len(prod.get("print_areas") or [])
    print("  print_areas:", n_areas, "variants:", len(prod.get("variants") or []))

    image_ids = {}
    for ratio, fname in spec["files"].items():
        path = folder / fname
        if not path.is_file():
            raise FileNotFoundError(path)
        image_ids[ratio] = pp.upload_image(str(path), f"{spec['key']}_hero_{ratio}.jpg")
        time.sleep(0.3)

    print_areas = []
    for i, pa in enumerate(prod.get("print_areas") or []):
        ratio = RATIO_BY_GROUP.get(i, "4x5")
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
        print(f"  group {i} → {ratio} ({len(pa['variant_ids'])} variants) img={img_id}")

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
    updated = pp._req("PUT", f"/shops/{pp.SHOP_ID}/products/{pid}.json", payload)
    print("  PUT ok id=", updated.get("id") or pid)

    pub = pp.publish_product(pid)
    print("  publish:", json.dumps(pub)[:200] if pub else "{}")
    return {"key": spec["key"], "printify_id": pid, "ok": True}


def main():
    results = []
    for spec in PRODUCTS:
        try:
            results.append(update_one(spec))
        except Exception as e:
            print(f"  FAIL {spec['key']}: {e}")
            results.append({"key": spec["key"], "ok": False, "error": str(e)[:300]})
        time.sleep(0.5)
    ok = sum(1 for r in results if r.get("ok"))
    print(f"\nDONE ok={ok}/{len(results)}")
    for r in results:
        print(" ", r)


if __name__ == "__main__":
    main()
