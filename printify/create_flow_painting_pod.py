"""
create_flow_painting_pod.py — POD matte posters for the flow-field "painting" line.

Each design is a single art piece, native 3:4 domain (30x40) -> only the 3x4
size group (12x16, 18x24, 30x40) is offered. Matte poster (blueprint 282 /
provider 99), published to Etsy as a draft.

  python printify/create_flow_painting_pod.py <slug>          # create + publish
  python printify/create_flow_painting_pod.py <slug> create   # Printify only
  python printify/create_flow_painting_pod.py <slug> publish  # publish existing from JSON
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

ATTR = ROOT / "attractor_prints"

# Only the 3x4 size group -- the aspect every piece in this line is rendered in.
POSTER_PRICES_3X4 = {101110: 1800, 43144: 2600, 101118: 5900}  # 12x16, 18x24, 30x40

DESIGNS = {
    "verdigris": {
        "art": ATTR / "flow_painting" / "flowpainting_verdigris_print.jpg",
        "title": (
            "Abstract Flow Field Painting | Verdigris Green Generative Art Canvas | "
            "Mathematical Wall Art Poster, Modern Gallery Print"
        ),
        "desc": (
            "An original abstract painting generated entirely from mathematics — no AI, no stock "
            "imagery. Thousands of flow lines trace a hand-placed field of vortices, a source, and "
            "a sink, building silky, wood-grain sweeps of teal-green light on black.\n\n"
            "• Museum-grade matte poster, printed to order\n"
            "• Portrait sizes: 12x16, 18x24, 30x40 in\n"
            "• Verdigris palette — teal-green patina glow on a near-black ground\n"
            "• Ships from a local print partner, ready to frame (frame not included)\n\n"
            "A striking centerpiece for a living room, office, or gallery wall.\n\n"
            "© MathRelaxing"
        ),
        "tags": ["abstract painting", "flow field art", "generative art", "green wall art",
                 "modern art print", "math wall art", "gallery wall art", "living room art",
                 "office wall art", "algorithmic art", "large wall art", "code art",
                 "contemporary art print"],
    },
    "vortexeye": {
        "art": ATTR / "flow_painting_vortexeye" / "flowpainting_roseash_print.jpg",
        "title": (
            "Abstract Vortex Painting | Wine Burgundy Generative Art Canvas | "
            "Mathematical Wall Art Poster, Moody Gallery Print"
        ),
        "desc": (
            "An original abstract painting generated entirely from mathematics — no AI, no stock "
            "imagery. Thousands of flow lines spiral toward a single dominant eye, a deep wine-red "
            "sweep of light pierced by a glowing rose-pink ring, on a near-black ground.\n\n"
            "• Museum-grade matte poster, printed to order\n"
            "• Portrait sizes: 12x16, 18x24, 30x40 in\n"
            "• Wine / burgundy palette — moody, jewel-toned glow\n"
            "• Ships from a local print partner, ready to frame (frame not included)\n\n"
            "A bold, moody centerpiece for a living room, bedroom, or gallery wall.\n\n"
            "© MathRelaxing"
        ),
        "tags": ["abstract painting", "flow field art", "generative art", "burgundy wall art",
                 "modern art print", "math wall art", "gallery wall art", "living room art",
                 "moody wall art", "algorithmic art", "large wall art", "code art",
                 "contemporary art print"],
    },
    "domaincolor": {
        "art": ATTR / "domain_coloring" / "domaincoloring_iridescent_print.jpg",
        "title": (
            "Abstract Iridescent Painting | Jewel Tone Complex Math Art Canvas | "
            "Mathematical Wall Art Poster, Opal Gallery Print"
        ),
        "desc": (
            "An original abstract painting generated entirely from mathematics — no AI, no stock "
            "imagery. Every pixel is colored by a single complex function: its angle sets the hue, "
            "its magnitude sets soft concentric shells of light, tracing rosettes of indigo, "
            "magenta, and amber across a deep jewel-toned ground — like polished opal or abalone "
            "shell.\n\n"
            "• Museum-grade matte poster, printed to order\n"
            "• Portrait sizes: 12x16, 18x24, 30x40 in\n"
            "• Full-color jewel-tone palette — indigo, violet, magenta, rose, amber\n"
            "• Ships from a local print partner, ready to frame (frame not included)\n\n"
            "A vivid, elegant centerpiece for a living room, office, or gallery wall.\n\n"
            "© MathRelaxing"
        ),
        "tags": ["abstract painting", "complex analysis art", "iridescent wall art", "generative art",
                 "jewel tone decor", "math wall art", "gallery wall art", "living room art",
                 "opal wall art", "algorithmic art", "large wall art", "code art",
                 "contemporary art print"],
    },
}


def create(slug: str):
    cfg = DESIGNS[slug]
    art = cfg["art"]
    if not art.is_file():
        raise FileNotFoundError(art)
    assert len(cfg["title"]) <= 140, f"title too long ({len(cfg['title'])})"
    image_id = pp.upload_image(str(art), f"flowpainting_{slug}_3x4.jpg")
    time.sleep(0.4)

    variants = [{"id": vid, "price": price, "is_enabled": True}
                for vid, price in POSTER_PRICES_3X4.items()]
    print_areas = [{
        "variant_ids": list(POSTER_PRICES_3X4.keys()),
        "placeholders": [{"position": "front", "images": [
            {"id": image_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}],
    }]
    payload = {
        "title": cfg["title"], "description": cfg["desc"],
        "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants, "print_areas": print_areas, "tags": cfg["tags"][:13],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    pid = prod.get("id")
    print(f"  Printify product: {pid}")
    try:
        pp.margin_report(prod)
    except Exception as e:
        print(f"  margin_report warn: {e}")
    row = {"key": f"flow_painting_{slug}", "printify_id": pid, "title": cfg["title"]}
    out_json = HERE / f"flow_painting_pod_{slug}_created.json"
    out_json.write_text(json.dumps([row], indent=2), encoding="utf-8")
    return [row], out_json


def publish(slug: str, created=None, out_json=None):
    out_json = out_json or HERE / f"flow_painting_pod_{slug}_created.json"
    if created is None:
        created = json.loads(out_json.read_text(encoding="utf-8"))
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
    if len(sys.argv) < 2 or sys.argv[1] not in DESIGNS:
        raise SystemExit(f"usage: create_flow_painting_pod.py <{'|'.join(DESIGNS)}> [create|publish]")
    slug = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else "all"
    if cmd == "create":
        create(slug)
    elif cmd == "publish":
        publish(slug)
    else:
        rows, out_json = create(slug)
        publish(slug, rows, out_json)
    print("\nDONE")
