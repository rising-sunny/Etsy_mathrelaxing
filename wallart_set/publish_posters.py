"""
publish_posters.py — turn a wall-art collection/palette into a set of physical
matte-poster products on Printify, published to the connected Etsy shop as
DRAFTS. Reuses the existing printify client (blueprint 282 / provider 99).

Each design is uploaded in three ratios (2:3, 3:4, 4:5) and each poster size is
placed on the matching-ratio art so nothing is cropped oddly.

    WALLART_MODULE=designs_geo WALLART_PALETTE=mono python wallart_set/publish_posters.py
    (run from repo root)
"""
import os
import sys
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "printify"))
import printify_publish as pf   # noqa: E402

BLUEPRINT, PROVIDER = 282, 99

# variant_id -> retail price (cents). Costs (probed): 11x14 5.92 · 12x16 9.95 ·
# 12x18 9.27 · 16x20 10.75 · 16x24 11.78 · 18x24 10.60 · 20x30 12.37 ·
# 24x36 15.78 · 30x40 33.79 — all comfortably below these prices.
PRICES = {
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
# which uploaded ratio each size should print from
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],   # 12x18, 16x24, 20x30, 24x36
    "3x4": [101110, 43144, 101118],         # 12x16, 18x24, 30x40
    "4x5": [43141, 43135],                  # 16x20, 11x14 (~4:5)
}

HOOK = {
    "penrose": "An aperiodic Penrose tiling — a pattern of two rhombi that fills the plane and never exactly repeats, built on the golden ratio.",
    "truchet": "Truchet tiles — a single arc tile dropped at random in four rotations, flowing into an endless maze of curves.",
    "girih": "An eight-fold Islamic girih star grid, the geometry behind centuries of tilework.",
    "rhombille": "A rhombille tiling — rhombi that lock into a field of three-dimensional cubes.",
    "sierpinski": "The Sierpinski triangle — a triangle endlessly subdivided into smaller triangles, a self-similar fractal.",
    "flower": "The Flower of Life — the overlapping-circle lattice at the heart of sacred geometry.",
}
COMMON_TAGS = ["geometric poster", "black and white art", "minimalist poster",
               "math wall art", "line art print", "scandinavian art",
               "abstract poster", "modern wall art", "geometric wall art",
               "tessellation art"]
EXTRA_TAGS = {
    "penrose": ["penrose tiling", "aperiodic art", "physics gift"],
    "truchet": ["pattern print", "op art", "black white decor"],
    "girih": ["islamic art", "star pattern", "sacred geometry"],
    "rhombille": ["isometric art", "3d cube art", "op art"],
    "sierpinski": ["fractal art", "sierpinski", "math gift"],
    "flower": ["sacred geometry", "flower of life", "mandala art"],
}


def poster_meta(designs, name):
    title = designs.DESIGNS[name]["title"]
    lt = (f"{title} Poster | Black and White Geometric Wall Art | "
          f"Minimalist Math Line Art Print | Scandinavian Decor")
    assert len(lt) <= 140, f"title too long ({len(lt)}): {lt}"
    tags = (COMMON_TAGS + EXTRA_TAGS[name])[:13]
    desc = (f"{title} — a printed geometric wall art poster.\n\n{HOOK[name]} "
            "Part of the Geometric Tilings series: classic tessellations drawn "
            "true from their mathematics as clean black-and-white line art.\n\n"
            "• Matte poster, 210gsm, giclee-quality\n"
            "• Printed to order and shipped to you — multiple sizes\n"
            "• Charcoal line work on a warm ivory ground\n"
            "• Frame not included\n\nPrinted on demand. Ships worldwide.")
    return lt, desc, tags


def create_multi(title, description, image_ids, tags):
    """image_ids: {ratio: image_id}. Builds one print_area group per ratio."""
    variants = [{"id": vid, "price": p, "is_enabled": True} for vid, p in PRICES.items()]
    print_areas = [{
        "variant_ids": GROUPS[ratio],
        "placeholders": [{"position": "front",
                          "images": [{"id": image_ids[ratio], "x": 0.5, "y": 0.5,
                                      "scale": 1, "angle": 0}]}],
    } for ratio in GROUPS]
    payload = {"title": title, "description": description, "blueprint_id": BLUEPRINT,
               "print_provider_id": PROVIDER, "variants": variants,
               "print_areas": print_areas, "tags": tags}
    return pf._req("POST", f"/shops/{pf.SHOP_ID}/products.json", payload)


def main():
    designs = importlib.import_module(os.environ.get("WALLART_MODULE", "designs_geo"))
    pal = os.environ.get("WALLART_PALETTE", "mono")
    prints = os.path.join(HERE, "out", designs.COLLECTION, pal, "prints")

    created = []
    for name in designs.ORDER:
        print(f"\n=== {designs.DESIGNS[name]['title']} ===")
        image_ids = {}
        for ratio in GROUPS:
            path = os.path.join(prints, f"{name}_{ratio}.jpg")
            image_ids[ratio] = pf.upload_image(path, f"{designs.SLUG}_{name}_{ratio}.jpg")
        title, desc, tags = poster_meta(designs, name)
        prod = create_multi(title, desc, image_ids, tags)
        pf.margin_report(prod)
        pub = pf.publish_product(prod["id"])
        created.append((name, prod["id"]))
        print(f"  created {prod['id']} + published to Etsy (draft)")

    print("\n=== DONE ===")
    for name, pid in created:
        print(f"  {name:12s} Printify product {pid}")


if __name__ == "__main__":
    main()
