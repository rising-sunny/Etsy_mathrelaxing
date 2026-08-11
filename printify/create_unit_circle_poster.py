"""
create_unit_circle_poster.py — POD matte poster for the Unit Circle plate.

Chosen from the shop data rather than taste: the Unit Circle print is tied
for the most-viewed listing in the shop (109 views), is one of only nine
organic sales, and had no physical counterpart. A trig reference is also the
kind of thing buyers want hanging on a classroom or dorm wall rather than
sitting in a downloads folder.

Deliberately publishes ONLY the standalone Unit Circle poster, not the
"Trigonometry Poster Set of 6" that also contains it -- the set has 3 views
against the standalone's 109, and doubling up would repeat the keyword
self-cannibalisation the shop audit flagged.

Print files come from unit_circle/build_unit_circle_pod.py.

  python printify/create_unit_circle_poster.py          # create + publish
  python printify/create_unit_circle_poster.py create   # Printify only
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

OUT_JSON = HERE / "unit_circle_poster_created.json"
PRINTS = ROOT / "unit_circle" / "pod_products"

POSTER_PRICES = {
    43135: 1500, 101110: 1800, 43138: 1800, 43141: 2400, 101113: 2400,
    43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900,
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

TITLE = ("Unit Circle Poster, Trigonometry Reference | Math Classroom Wall Art, "
         "Radians Degrees Sin Cos | Matte Print")

TAGS = ["unit circle", "trigonometry poster", "matte poster", "math wall art",
        "classroom decor", "math teacher gift", "trig reference", "stem wall art",
        "educational poster", "student gift", "algebra poster", "geometry art",
        "study room decor"]

DESCRIPTION = (
    "The Unit Circle — a matte reference poster of the trigonometry chart every "
    "student ends up redrawing from memory, typeset properly in LaTeX "
    "(Computer Modern) rather than clip art or AI.\n\n"
    "Every special angle from 0 to 330 degrees, each with its radian measure and "
    "exact (cos, sin) coordinates, plus the 45-degree reference triangle and the "
    "key identities along the bottom.\n\n"
    "• Museum-grade matte poster, printed to order\n"
    "• Portrait sizes from 11x14 up to 24x36 in\n"
    "• Warm graph-paper ground with ink linework and rust accents\n"
    "• Reads clearly from across a classroom at 18x24 and up\n"
    "• Ships from a local print partner, ready to frame (frame not included)\n\n"
    "© MathRelaxing"
)


def create():
    assert len(TITLE) <= 140, f"title too long ({len(TITLE)})"
    image_ids = {}
    for ratio in ("2x3", "3x4", "4x5"):
        path = PRINTS / f"unit_circle_{ratio}.jpg"
        if not path.is_file():
            raise FileNotFoundError(path)
        image_ids[ratio] = pp.upload_image(str(path), f"unit_circle_{ratio}.jpg")
        time.sleep(0.4)

    variants = [{"id": vid, "price": p, "is_enabled": True} for vid, p in POSTER_PRICES.items()]
    print_areas = []
    for ratio, vids in GROUPS.items():
        print_areas.append({
            "variant_ids": vids,
            "placeholders": [{"position": "front", "images": [
                {"id": image_ids[ratio], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
        })
    payload = {
        "title": TITLE, "description": DESCRIPTION,
        "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants, "print_areas": print_areas, "tags": TAGS[:13],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    pid = prod.get("id")
    print(f"  Printify product: {pid}")
    pp.margin_report(prod)
    row = [{"key": "unit_circle", "printify_id": pid, "title": TITLE}]
    OUT_JSON.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def publish(created=None):
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for row in created:
        pp.publish_product(row["printify_id"])
        print(f"  published {row['key']}")

    # Printify's publish is ASYNCHRONOUS -- the Etsy listing appeared ~60-80s
    # after the call returned in earlier runs, so poll rather than take one
    # early reading (which previously reported a false "nothing went live").
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
