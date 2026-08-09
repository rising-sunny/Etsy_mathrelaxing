"""
create_turing_posters.py — POD matte posters for the Turing Patterns line.

6 designs (Gray-Scott reaction-diffusion simulations, see
turing_patterns_set/generate_turing_field.py), each a matte poster
(blueprint 282 / provider 99, ratios 2:3 / 3:4 / 4:5), published to Etsy
as drafts via Printify -- physical counterpart to the digital
"turing_patterns_set" download listing.

  python printify/create_turing_posters.py          # create + publish
  python printify/create_turing_posters.py create    # Printify only
  python printify/create_turing_posters.py publish   # publish existing from JSON
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

OUT_JSON = HERE / "turing_posters_created.json"
PRINTS = ROOT / "turing_patterns_set" / "products"

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


def desc(name, blurb, footer_tag):
    return (
        f"{name} — a matte wall-art poster of an actual Gray-Scott reaction-diffusion "
        f"simulation (Alan Turing's 1952 morphogenesis equations, run in code -- not a "
        f"decorative texture).\n\n{blurb}\n\n"
        "• Museum-grade matte poster, printed to order\n"
        "• Portrait sizes from 11x14 up to 24x36 in\n"
        f"• {footer_tag}, dark ground, gold linework\n"
        "• Ships from a local print partner, ready to frame (frame not included)\n\n"
        f"{COPYRIGHT}"
    )


TAGS_BASE = ["matte poster", "turing pattern", "reaction diffusion", "math wall art",
             "science poster", "dark academia", "biology art", "moody wall art",
             "gallery wall art", "office wall art", "science teacher gift", "nerd gift"]

DESIGNS = [
    ("leopard_rosettes", "Leopard Rosettes",
     "Turing Pattern Poster, Leopard Rosettes | Reaction-Diffusion Math Art, Gold & Black | Dark Academia Science Wall Art",
     "Self-replicating spots, the same instability behind a real leopard's coat, in warm amber and gold.",
     "Amber & black", TAGS_BASE + ["leopard print art"]),
    ("pufferfish_mesh", "Pufferfish Mesh",
     "Turing Pattern Poster, Pufferfish Mesh | Reaction-Diffusion Math Art, Teal & Black | Dark Academia Science Wall Art",
     "A dense field of Turing holes in deep teal and cyan -- the same mesh that patterns a pufferfish's skin.",
     "Teal & black", TAGS_BASE + ["teal wall art"]),
    ("brain_coral", "Brain Coral",
     "Turing Pattern Poster, Brain Coral | Reaction-Diffusion Math Art, Coral & Black | Dark Academia Science Wall Art",
     "A labyrinthine growth pattern in coral pink and burnt orange, the same maze that ridges real brain coral.",
     "Coral & black", TAGS_BASE + ["coral wall art"]),
    ("tiger_current", "Tiger Current",
     "Turing Pattern Poster, Tiger Current | Reaction-Diffusion Math Art, Amber & Black | Dark Academia Science Wall Art",
     "Restless traveling stripes in burnt orange and black -- the reaction-diffusion model behind a tiger's coat.",
     "Burnt orange & black", TAGS_BASE + ["tiger print poster"]),
    ("fingerprint_whorl", "Fingerprint Whorl",
     "Turing Pattern Poster, Fingerprint Whorl | Reaction-Diffusion Math Art, Steel Blue & Black | Dark Academia Science Wall Art",
     "A dense, tight maze in steel blue and silver -- the same instability that ridges a human fingertip.",
     "Steel blue & black", TAGS_BASE + ["forensic art print"]),
    ("cuttlefish_static", "Cuttlefish Static",
     "Turing Pattern Poster, Cuttlefish Static | Reaction-Diffusion Math Art, Violet & Black | Dark Academia Science Wall Art",
     "Spots caught mid-collapse in violet and magenta -- the chemical equivalent of a cuttlefish shifting camouflage.",
     "Violet & black", TAGS_BASE + ["violet wall art"]),
]


def build_products():
    prods = []
    for slug, name, title, blurb, footer_tag, tags in DESIGNS:
        pd = PRINTS / slug
        files = {r: pd / f"{slug}_{r}.jpg" for r in ("2x3", "3x4", "4x5")}
        for f in files.values():
            if not f.is_file():
                raise FileNotFoundError(f)
        assert len(title) <= 140, f"title too long ({len(title)}): {title}"
        prods.append({"key": slug, "name": name, "title": title,
                      "desc": desc(name, blurb, footer_tag), "tags": tags[:13], "files": files})
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
