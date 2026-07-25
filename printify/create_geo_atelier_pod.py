"""
create_geo_atelier_pod.py — POD matte posters for Metatron + Poincaré digital art.

Uses Printify blueprint 282 (Matte Vertical Posters) / provider 99, multi-ratio
print areas (2:3, 3:4, 4:5), then publishes each product to the connected Etsy shop.

  python printify/create_geo_atelier_pod.py          # create + publish
  python printify/create_geo_atelier_pod.py create   # Printify only
  python printify/create_geo_atelier_pod.py publish  # publish existing from JSON
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

OUT_JSON = HERE / "geo_atelier_pod_created.json"

# Same ladder as wallart_set/publish_posters.py + batch_wave12
POSTER_PRICES = {
    43135: 1500,   # 11x14
    101110: 1800,  # 12x16
    43138: 1800,   # 12x18
    43141: 2400,   # 16x20
    101113: 2400,  # 16x24
    43144: 2600,   # 18x24
    43147: 3200,   # 20x30
    43150: 3900,   # 24x36
    101118: 5900,  # 30x40
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

PRODUCTS = [
    {
        "key": "metatron_cube",
        "folder": ROOT / "wallart_set" / "out" / "metatron" / "mono_atelier" / "prints",
        "files": {
            "2x3": "Metatrons_Cube_2x3.jpg",
            "3x4": "Metatrons_Cube_3x4.jpg",
            "4x5": "Metatrons_Cube_4x5.jpg",
        },
        "title": (
            "Metatron's Cube Poster | Sacred Geometry Wall Art | "
            "Black White Minimalist Line Art Print"
        ),
        "desc": (
            "Metatron's Cube — ultra-precise sacred geometry wall art, printed on demand.\n\n"
            "Built from the Fruit of Life: 13 equal circles, every centre connected, "
            "with solid faces for the star tetrahedron (Merkaba) and isometric cube rhombi. "
            "Charcoal line work on warm ivory — not AI, not clip art.\n\n"
            "• Matte poster, printed to order\n"
            "• Multiple sizes (11×14 up to 30×40)\n"
            "• Minimalist / Scandinavian gallery look\n"
            "• Frame not included\n\n"
            "Ships worldwide via print-on-demand. "
            "MathRelaxing — every design is drawn from real mathematics."
        ),
        "tags": [
            "metatron cube",
            "sacred geometry",
            "geometric wall art",
            "math wall art",
            "line art print",
            "minimalist poster",
            "black and white art",
            "scandinavian art",
            "flower of life",
            "math poster",
            "office wall art",
            "modern wall art",
            "geometric poster",
        ],
    },
    {
        "key": "poincare_disk",
        "folder": ROOT / "wallart_set" / "out" / "poincare" / "mono_wire_7_3" / "prints",
        "files": {
            "2x3": "Poincare_Disk_7_3_2x3.jpg",
            "3x4": "Poincare_Disk_7_3_3x4.jpg",
            "4x5": "Poincare_Disk_7_3_4x5.jpg",
        },
        "title": (
            "Poincaré Disk Poster | Hyperbolic Geometry Wall Art | "
            "Non-Euclidean Math Tessellation Print"
        ),
        "desc": (
            "Poincaré Disk — hyperbolic tiling {7,3} as fine line-art wall art, "
            "printed on demand.\n\n"
            "The open unit disk models the hyperbolic plane. Every edge is a true "
            "geodesic (circular arc orthogonal to the boundary). Tiles shrink toward "
            "the circle at infinity. Light charcoal on warm ivory — gallery-ready, not AI.\n\n"
            "• Matte poster, printed to order\n"
            "• Multiple sizes (11×14 up to 30×40)\n"
            "• Escher-family non-Euclidean geometry\n"
            "• Frame not included\n\n"
            "Ships worldwide via print-on-demand. "
            "MathRelaxing — computed from real non-Euclidean geometry."
        ),
        "tags": [
            "poincare disk",
            "hyperbolic geometry",
            "math wall art",
            "non euclidean",
            "geometric wall art",
            "tessellation art",
            "escher style",
            "math poster",
            "line art print",
            "minimalist poster",
            "science poster",
            "office wall art",
            "geometric poster",
        ],
    },
]


def create_multi_poster(title, description, image_ids: dict, tags: list):
    variants = [
        {"id": vid, "price": p, "is_enabled": True} for vid, p in POSTER_PRICES.items()
    ]
    print_areas = []
    for ratio, vids in GROUPS.items():
        print_areas.append(
            {
                "variant_ids": vids,
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_ids[ratio],
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
    payload = {
        "title": title,
        "description": description,
        "blueprint_id": pp.BLUEPRINT_MATTE,
        "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants,
        "print_areas": print_areas,
        "tags": tags[:13],
    }
    return pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)


def create_all() -> list[dict]:
    created = []
    for p in PRODUCTS:
        print(f"\n=== CREATE {p['key']} ===")
        assert len(p["title"]) <= 140, f"title too long: {len(p['title'])}"
        image_ids = {}
        for ratio, fname in p["files"].items():
            path = p["folder"] / fname
            if not path.is_file():
                raise FileNotFoundError(path)
            image_ids[ratio] = pp.upload_image(str(path), f"{p['key']}_{ratio}.jpg")
            time.sleep(0.4)
        prod = create_multi_poster(p["title"], p["desc"], image_ids, p["tags"])
        pid = prod.get("id")
        print(f"  Printify product: {pid}")
        pp.margin_report(prod)
        created.append(
            {
                "key": p["key"],
                "printify_id": pid,
                "title": p["title"],
                "blueprint": 282,
            }
        )
        time.sleep(0.5)
    OUT_JSON.write_text(json.dumps(created, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_JSON}")
    return created


def publish_all(created: list[dict] | None = None) -> list[dict]:
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    results = []
    for row in created:
        pid = row["printify_id"]
        print(f"\n=== PUBLISH {row['key']}  {pid} ===")
        res = pp.publish_product(pid)
        print("  publish response:", json.dumps(res)[:300] if res else "{}")
        # poll external etsy id
        etsy_id = None
        for attempt in range(12):
            time.sleep(3)
            prod = pp.get_product(pid)
            ext = prod.get("external") or {}
            etsy_id = ext.get("id") or ext.get("handle")
            if etsy_id:
                print(f"  Etsy listing id: {etsy_id}")
                break
            print(f"  waiting external… ({attempt+1})")
        row = dict(row)
        row["etsy_listing_id"] = etsy_id
        row["published"] = True
        results.append(row)
    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_JSON}")
    return results


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "create":
        create_all()
    elif cmd == "publish":
        publish_all()
    else:
        created = create_all()
        publish_all(created)
        print("\nDONE — POD products created and published to Etsy (check shop drafts/active).")


if __name__ == "__main__":
    main()
