"""
publish_sticker_batch.py — create + publish the remaining math stickers to Etsy
via Printify, then fix tags / who_made / production partner on each Etsy listing.

    python publish_sticker_batch.py
"""
import os
import time
import printify_publish as P
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import etsy_manager

BP = 400          # Kiss-Cut Stickers
PROV = 99         # Printify Choice
PARTNER = 5727366  # "Printify" production partner (Etsy)
SDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set", "out", "sticker")

DESC = ("Math art kiss-cut sticker. Durable, water-resistant vinyl with a kiss-cut around the design — "
        "peel and stick on a laptop, water bottle, notebook or phone.\n\n"
        "The design is drawn from real mathematics. A fun, geeky gift for a mathematician, physicist, "
        "teacher or student.")

DESIGNS = {
    "euler": ("Eulers Identity Math Sticker | The Most Beautiful Equation | Kiss-Cut Vinyl Decal | Nerdy Math Physics Gift",
              ["eulers identity", "math sticker", "science sticker", "laptop sticker", "kiss cut sticker",
               "physics sticker", "math gift", "nerd sticker", "stem gift", "vinyl sticker",
               "equation sticker", "teacher gift", "math art"]),
    "golden": ("Golden Ratio Sticker | Fibonacci Spiral Phi Math Decal | Kiss-Cut Vinyl | Math Lover Gift | Laptop Water Bottle",
               ["golden ratio", "fibonacci sticker", "math sticker", "science sticker", "laptop sticker",
                "kiss cut sticker", "phi sticker", "nerd sticker", "stem gift", "vinyl sticker",
                "spiral sticker", "teacher gift", "math art"]),
    "pi": ("Pi Day Math Sticker | Circle Number 3.14 Decal | Kiss-Cut Vinyl | Math Teacher Gift | Laptop Water Bottle Sticker",
           ["pi day sticker", "math sticker", "science sticker", "laptop sticker", "kiss cut sticker",
            "pi sticker", "math teacher gift", "nerd sticker", "stem gift", "vinyl sticker",
            "number sticker", "math gift", "math art"]),
    "schrodinger": ("Schrodinger Equation Sticker | Quantum Physics Wave Decal | Kiss-Cut Vinyl | Physics Nerd Gift | Science Sticker",
                    ["quantum physics", "physics sticker", "science sticker", "laptop sticker", "kiss cut sticker",
                     "schrodinger", "nerd sticker", "stem gift", "vinyl sticker", "equation sticker",
                     "physics gift", "teacher gift", "science gift"]),
    "lorenz": ("Lorenz Attractor Sticker | Butterfly Effect Chaos Theory Decal | Kiss-Cut Vinyl | Math Physics Science Gift",
               ["chaos theory", "butterfly effect", "math sticker", "science sticker", "laptop sticker",
                "kiss cut sticker", "physics sticker", "nerd sticker", "stem gift", "vinyl sticker",
                "lorenz attractor", "math gift", "science gift"]),
}

VARIANTS = [{"id": 45748, "price": 399, "is_enabled": False},   # 2" off
            {"id": 45750, "price": 399, "is_enabled": True},    # 3"
            {"id": 45752, "price": 499, "is_enabled": True},    # 4"
            {"id": 45754, "price": 699, "is_enabled": True}]    # 6"


def make(name, title, tags):
    png = os.path.join(SDIR, f"{name}.png")
    assert os.path.exists(png), png
    img = P.upload_image(png, file_name=f"{name}.png")
    payload = {"title": title, "description": DESC, "blueprint_id": BP, "print_provider_id": PROV,
               "variants": VARIANTS,
               "print_areas": [{"variant_ids": [v["id"] for v in VARIANTS],
                                "placeholders": [{"position": "front",
                                                  "images": [{"id": img, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}],
               "tags": tags}
    pid = P._req("POST", f"/shops/{P.SHOP_ID}/products.json", payload)["id"]
    P.publish_product(pid)
    ext = None
    for _ in range(12):
        time.sleep(12)
        pr = P.get_product(pid)
        if pr.get("external"):
            ext = pr["external"]; break
    return pid, ext


def fix_etsy(lid, tags):
    m = etsy_manager.EtsyManager(); sid = m.get_shop_id()
    try:
        m.update_listing(lid, tags=tags)
    except Exception as e:
        print("   tags err", str(e)[:60])
    try:
        m.make_request("PATCH", f"/shops/{sid}/listings/{lid}", json_body=True,
                       payload={"who_made": "someone_else", "when_made": "made_to_order",
                                "is_supply": False, "production_partner_ids": [PARTNER]})
    except Exception as e:
        print("   who_made err", str(e)[:60])
    r = m.make_request("GET", f"/listings/{lid}")
    return len(r.get("tags") or []), r.get("who_made"), r.get("production_partner_ids")


def main():
    only = set(sys.argv[1:])
    results = []
    for name, (title, tags) in DESIGNS.items():
        if only and name not in only:
            continue
        print(f"\n=== {name} ===")
        pid, ext = make(name, title, tags)
        if not ext:
            print(f"   published but no external yet (pid={pid})")
            results.append((name, pid, None, None)); continue
        lid = ext["id"]
        ntags, who, ppids = fix_etsy(lid, tags)
        print(f"   etsy={lid}  tags={ntags}  who_made={who}  partners={ppids}")
        results.append((name, pid, lid, ppids))
    print("\n==== SUMMARY ====")
    for name, pid, lid, ppids in results:
        print(f"  {name:12} etsy={lid}  partner={'ok' if ppids else 'MANUAL'}")


if __name__ == "__main__":
    main()
