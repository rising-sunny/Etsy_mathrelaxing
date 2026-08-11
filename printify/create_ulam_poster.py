"""
create_ulam_poster.py — POD matte poster for the Ulam Spiral plate.

Picked from shop data: 30 views (third-highest among designs with no physical
counterpart), a single design rather than a set, and almost entirely visual --
a dot field with emergent diagonals. The shop's only physical sale so far
(Penrose Tiling, $26) was likewise a purely visual geometric design, which is
a reason to try this one, not proof of anything at n=1.

Print files come from wallart_set/build_ulam_pod.py.

  python printify/create_ulam_poster.py          # create + publish
  python printify/create_ulam_poster.py create   # Printify only
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import printify_publish as pp  # noqa: E402

OUT_JSON = HERE / "ulam_poster_created.json"
PRINTS = ROOT / "wallart_set" / "ulam_pod"

POSTER_PRICES = {
    43135: 1500, 101110: 1800, 43138: 1800, 43141: 2400, 101113: 2400,
    43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900,
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

TITLE = ("Ulam Spiral Poster, Prime Numbers | Minimalist Math Wall Art, Black and White "
         "Number Theory | Matte Print")

TAGS = ["ulam spiral", "prime numbers", "matte poster", "math wall art",
        "minimalist poster", "number theory", "black and white art", "stem wall art",
        "office wall art", "math teacher gift", "geometric print", "nerd gift",
        "study room decor"]

DESCRIPTION = (
    "The Ulam Spiral — a matte wall-art poster of one of mathematics' strangest "
    "pictures, computed from scratch rather than traced or AI-generated.\n\n"
    "Write the whole numbers in a square spiral and mark every prime. They refuse "
    "to scatter evenly: instead they crowd onto diagonal lines, the tracks of "
    "simple quadratics like n² + n + 41. Over 63,000 numbers are plotted here, "
    "every prime among them found by sieve. Nobody has a formula that catches "
    "them all.\n\n"
    "• Museum-grade matte poster, printed to order\n"
    "• Portrait sizes from 11x14 up to 24x36 in\n"
    "• Minimal black-on-warm-white, reads as abstract texture from across a room\n"
    "• Ships from a local print partner, ready to frame (frame not included)\n\n"
    "© MathRelaxing"
)


def create():
    assert len(TITLE) <= 140, f"title too long ({len(TITLE)})"
    image_ids = {}
    for ratio in ("2x3", "3x4", "4x5"):
        path = PRINTS / f"ulam_spiral_{ratio}.jpg"
        if not path.is_file():
            raise FileNotFoundError(path)
        image_ids[ratio] = pp.upload_image(str(path), f"ulam_spiral_{ratio}.jpg")
        time.sleep(0.4)

    variants = [{"id": vid, "price": p, "is_enabled": True} for vid, p in POSTER_PRICES.items()]
    print_areas = []
    for ratio, vids in GROUPS.items():
        print_areas.append({
            "variant_ids": vids,
            "placeholders": [{"position": "front", "images": [
                {"id": image_ids[ratio], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
        })
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", {
        "title": TITLE, "description": DESCRIPTION,
        "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants, "print_areas": print_areas, "tags": TAGS[:13],
    })
    pid = prod.get("id")
    print(f"  Printify product: {pid}")
    pp.margin_report(prod)
    row = [{"key": "ulam_spiral", "printify_id": pid, "title": TITLE}]
    OUT_JSON.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def publish(created=None):
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for row in created:
        pp.publish_product(row["printify_id"])
        print(f"  published {row['key']}")

    # Printify's publish is ASYNCHRONOUS (~60-80s to appear on Etsy), so poll
    # rather than take one early reading -- an early check previously reported
    # a false "nothing went live".
    print("\n=== verifying Etsy state (polling) ===")
    from etsy_manager import EtsyManager
    m = EtsyManager()
    shop_id = m.get_shop_id()
    wanted = {r["title"] for r in created}
    for attempt in range(10):
        time.sleep(20)
        for state in ("active", "draft", "inactive"):
            r = m.make_request("GET", f"/shops/{shop_id}/listings?state={state}&limit=100")
            for l in r.get("results", []):
                if l["title"] in wanted:
                    print(f"  {state} | {l['listing_id']} | {l['title'][:56]}")
                    return created
        print(f"  intento {attempt + 1}: aun no aparece")
    print("  WARNING: no apareció en Etsy dentro del tiempo de espera")
    return created


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "create":
        create()
    elif cmd == "publish":
        publish()
    else:
        publish(create())
    print("\nDONE")
