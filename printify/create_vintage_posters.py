"""
create_vintage_posters.py — POD matte posters for the Vintage Math Art line.

6 curated designs (3 Maurer Rose + 3 Phyllotaxis), each a matte poster
(blueprint 282 / provider 99, ratios 2:3 / 3:4 / 4:5), published to Etsy as
drafts via Printify.

  python printify/create_vintage_posters.py          # create + publish
  python printify/create_vintage_posters.py create    # Printify only
  python printify/create_vintage_posters.py publish    # publish existing from JSON
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

OUT_JSON = HERE / "vintage_posters_created.json"
PRINTS = ROOT / "vintage_art" / "products"

POSTER_PRICES = {
    43135: 1500, 101110: 1800, 43138: 1800, 43141: 2400, 101113: 2400,
    43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900,
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

COPYRIGHT = "© MathRelaxing"


def desc(name, blurb):
    return (
        f"{name} — a matte wall-art poster of original, hand-coded mathematical "
        f"line art (no AI, no stock images).\n\n{blurb}\n\n"
        "• Museum-grade matte poster, printed to order\n"
        "• Portrait sizes from 11x14 up to 24x36 in\n"
        "• Gold-and-ink design on a warm, aged-ivory ground\n"
        "• Ships from a local print partner, ready to frame (frame not included)\n\n"
        f"{COPYRIGHT}"
    )


MAURER_BLURB = ("A Maurer rose is the hidden figure that appears when you connect points "
                "around a rose curve with straight lines — an intricate lattice that reads "
                "like antique string art or an engraved compass rose.")
PHYLLO_BLURB = ("Phyllotaxis is the golden-angle spiral nature uses to pack sunflower seeds "
                "— thousands of points settling into gold-and-ink Fibonacci spirals.")

TAGS_MAURER = ["matte poster", "geometric wall art", "math wall art", "sacred geometry",
               "vintage wall art", "line art poster", "gold wall art", "dark academia",
               "mandala poster", "mathematical art", "office wall art", "living room art",
               "string art print"]
TAGS_PHYLLO = ["matte poster", "botanical wall art", "math wall art", "sacred geometry",
               "vintage wall art", "spiral wall art", "gold wall art", "dark academia",
               "golden ratio art", "mathematical art", "office wall art", "living room art",
               "fibonacci art"]

DESIGNS = [
    ("maurer_rose", 2, "Maurer Rose · Trefoil",
     "Maurer Rose Poster, Trefoil Rosette | Vintage Geometric Line Art, Gold & Ink | Sacred Geometry Matte Wall Art Print",
     MAURER_BLURB, TAGS_MAURER),
    ("maurer_rose", 4, "Maurer Rose · Twelve-Point Rosette",
     "Maurer Rose Poster, Twelve-Point Rosette | Vintage Geometric Line Art, Gold & Ink | Sacred Geometry Matte Wall Art Print",
     MAURER_BLURB, TAGS_MAURER),
    ("maurer_rose", 6, "Maurer Rose · Star",
     "Maurer Rose Poster, Geometric Star | Vintage Line Art, Gold & Ink | Sacred Geometry Matte Wall Art Print",
     MAURER_BLURB, TAGS_MAURER),
    ("phyllotaxis", 1, "Phyllotaxis · Golden Bloom",
     "Phyllotaxis Poster, Golden Ratio Sunflower | Vintage Botanical Math Art, Gold & Ink | Fibonacci Matte Wall Art Print",
     PHYLLO_BLURB, TAGS_PHYLLO),
    ("phyllotaxis", 3, "Phyllotaxis · Spiral Bloom",
     "Phyllotaxis Poster, Golden Ratio Spiral | Vintage Botanical Math Art, Gold & Ink | Fibonacci Matte Wall Art Print",
     PHYLLO_BLURB, TAGS_PHYLLO),
    ("phyllotaxis", 4, "Phyllotaxis · Fibonacci Spiral",
     "Phyllotaxis Poster, Fibonacci Spiral | Vintage Botanical Math Wall Art, Gold & Ink | Golden Ratio Matte Print",
     PHYLLO_BLURB, TAGS_PHYLLO),
]


def build_products():
    prods = []
    for slug, idx, name, title, blurb, tags in DESIGNS:
        pd = PRINTS / slug / "prints"
        files = {r: pd / f"{slug}_{idx:02d}_{r}.jpg" for r in ("2x3", "3x4", "4x5")}
        for f in files.values():
            if not f.is_file():
                raise FileNotFoundError(f)
        prods.append({"key": f"{slug}_{idx:02d}", "name": name, "title": title,
                      "desc": desc(name, blurb), "tags": tags, "files": files})
    return prods


def create_multi_poster(title, description, image_ids, tags):
    variants = [{"id": vid, "price": p, "is_enabled": True} for vid, p in POSTER_PRICES.items()]
    print_areas = []
    for ratio, vids in GROUPS.items():
        print_areas.append({
            "variant_ids": vids,
            "placeholders": [{"position": "front", "images": [
                {"id": image_ids[ratio], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
        })
    payload = {
        "title": title, "description": description,
        "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants, "print_areas": print_areas, "tags": tags[:13],
    }
    return pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)


def create_all():
    created = []
    for p in build_products():
        print(f"\n=== CREATE {p['key']} :: {p['title'][:55]}... ===")
        assert len(p["title"]) <= 140, f"title too long ({len(p['title'])})"
        image_ids = {}
        for ratio, path in p["files"].items():
            image_ids[ratio] = pp.upload_image(str(path), f"{p['key']}_{ratio}.jpg")
            time.sleep(0.4)
        prod = create_multi_poster(p["title"], p["desc"], image_ids, p["tags"])
        pid = prod.get("id")
        print(f"  Printify product: {pid}")
        try:
            pp.margin_report(prod)
        except Exception as e:
            print(f"  margin_report warn: {e}")
        created.append({"key": p["key"], "printify_id": pid, "title": p["title"]})
        time.sleep(0.5)
    OUT_JSON.write_text(json.dumps(created, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_JSON}")
    return created


def publish_all(created=None):
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for row in created:
        pid = row["printify_id"]
        print(f"\n=== PUBLISH {row['key']} ({pid}) ===")
        try:
            pp.publish_product(pid)
            print("  published -> Etsy draft")
        except Exception as e:
            print(f"  publish ERROR: {e}")
        time.sleep(0.5)
    return created


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "create":
        create_all()
    elif cmd == "publish":
        publish_all()
    else:
        publish_all(create_all())
    print("\nDONE")
