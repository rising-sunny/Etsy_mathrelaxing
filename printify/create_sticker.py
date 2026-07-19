"""
create_sticker.py — create a kiss-cut sticker product on Printify from a design
PNG, read the real per-variant cost, and report margins. Leaves it as a Printify
DRAFT (does not push to Etsy until we confirm pricing).

    python create_sticker.py <design.png> "<title>"
"""
import os
import sys
import time
import printify_publish as P

BLUEPRINT_STICKER = 400        # Kiss-Cut Stickers
PROVIDER = 99                  # Printify Choice

# retail price (cents) by sticker size keyword
RETAIL = {'3"': 399, '4"': 499, '5.5"': 599, '6"': 699, '5.83"': 599}


def req(path, tries=10, delay=3):
    for k in range(tries):
        try:
            return P._req("GET", path)
        except Exception as e:
            if k == tries - 1:
                raise
            print(f"  ..throttled ({str(e)[-30:]}), retry {k+1}/{tries}")
            time.sleep(delay * (k + 1))


def pick_price(title):
    for kw, cents in RETAIL.items():
        if kw in title:
            return cents
    return 499


def main(design, title):
    print("1) fetch variants (blueprint 400 / provider 99)…")
    v = req(f"/catalog/blueprints/{BLUEPRINT_STICKER}/print_providers/{PROVIDER}/variants.json")
    variants = v["variants"]
    pos = variants[0].get("placeholders", [{}])[0].get("position", "front")
    print(f"   {len(variants)} variants · placeholder position = '{pos}'")
    sizes = {x["id"]: x.get("title", "") for x in variants}
    for vid, t in sizes.items():
        print(f"     {vid}  {t}")

    print("2) upload design…")
    img_id = P.upload_image(design, file_name=os.path.basename(design))

    print("3) create product (draft on Printify)…")
    sizes_prices = {vid: pick_price(t) for vid, t in sizes.items()}
    payload = {
        "title": title,
        "description": DESC,
        "blueprint_id": BLUEPRINT_STICKER,
        "print_provider_id": PROVIDER,
        "variants": [{"id": vid, "price": pr, "is_enabled": True} for vid, pr in sizes_prices.items()],
        "print_areas": [{
            "variant_ids": list(sizes_prices.keys()),
            "placeholders": [{"position": pos,
                              "images": [{"id": img_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
        }],
        "tags": TAGS,
    }
    res = P._req("POST", f"/shops/{P.SHOP_ID}/products.json", payload)
    pid = res["id"]
    print(f"   product id = {pid}")

    print("4) read real costs / margins…")
    prod = P.get_product(pid)
    P.margin_report(prod)
    print(f"\nDONE. Printify draft product {pid}. Publish to Etsy with publish_product('{pid}') when ready.")
    return pid


DESC = ("Math art kiss-cut sticker. Durable, water-resistant vinyl with a kiss-cut around the design — "
        "peel and stick on a laptop, water bottle, notebook or phone.\n\n"
        "The design is drawn from real mathematics. A fun, geeky gift for a mathematician, physicist, "
        "teacher or student.")
TAGS = ["math sticker", "science sticker", "laptop sticker", "math gift", "nerd sticker",
        "water bottle sticker", "teacher gift", "kiss cut sticker", "geeky sticker", "stem gift",
        "equation sticker", "vinyl sticker", "math art"]


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
