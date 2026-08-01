"""
create_flow_painting_pod.py — POD matte poster for the new flow-field "painting".

Single design (Verdigris), native 3:4 domain (30x40) -> only the 3x4 size
group (12x16, 18x24, 30x40) is offered, matching the one rendered aspect.
Matte poster (blueprint 282 / provider 99), published to Etsy as a draft.

  python printify/create_flow_painting_pod.py          # create + publish
  python printify/create_flow_painting_pod.py create   # Printify only
  python printify/create_flow_painting_pod.py publish  # publish existing from JSON
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

OUT_JSON = HERE / "flow_painting_pod_created.json"
ART = ROOT / "attractor_prints" / "flow_painting" / "flowpainting_verdigris_print.jpg"

# Only the 3x4 size group -- the one aspect this piece is rendered in.
POSTER_PRICES_3X4 = {101110: 1800, 43144: 2600, 101118: 5900}  # 12x16, 18x24, 30x40

TITLE = (
    "Abstract Flow Field Painting | Verdigris Green Generative Art Canvas | "
    "Mathematical Wall Art Poster, Modern Gallery Print"
)
DESC = (
    "An original abstract painting generated entirely from mathematics — no AI, no stock imagery. "
    "Thousands of flow lines trace a hand-placed field of vortices, a source, and a sink, building "
    "silky, wood-grain sweeps of teal-green light on black.\n\n"
    "• Museum-grade matte poster, printed to order\n"
    "• Portrait sizes: 12x16, 18x24, 30x40 in\n"
    "• Verdigris palette — teal-green patina glow on a near-black ground\n"
    "• Ships from a local print partner, ready to frame (frame not included)\n\n"
    "A striking centerpiece for a living room, office, or gallery wall.\n\n"
    "© MathRelaxing"
)
TAGS = ["abstract painting", "flow field art", "generative art", "green wall art",
        "modern art print", "math wall art", "gallery wall art", "living room art",
        "office wall art", "algorithmic art", "large wall art", "code art",
        "contemporary art print"]


def create():
    if not ART.is_file():
        raise FileNotFoundError(ART)
    assert len(TITLE) <= 140, f"title too long ({len(TITLE)})"
    image_id = pp.upload_image(str(ART), "flowpainting_verdigris_3x4.jpg")
    time.sleep(0.4)

    variants = [{"id": vid, "price": price, "is_enabled": True}
                for vid, price in POSTER_PRICES_3X4.items()]
    print_areas = [{
        "variant_ids": list(POSTER_PRICES_3X4.keys()),
        "placeholders": [{"position": "front", "images": [
            {"id": image_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
    }]
    payload = {
        "title": TITLE, "description": DESC,
        "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants, "print_areas": print_areas, "tags": TAGS[:13],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    pid = prod.get("id")
    print(f"  Printify product: {pid}")
    try:
        pp.margin_report(prod)
    except Exception as e:
        print(f"  margin_report warn: {e}")
    row = {"key": "flow_painting_verdigris", "printify_id": pid, "title": TITLE}
    OUT_JSON.write_text(json.dumps([row], indent=2), encoding="utf-8")
    return [row]


def publish(created=None):
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
