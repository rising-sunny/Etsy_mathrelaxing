"""
create_spiral_posters.py — POD matte posters for the Spiral Tilings line.

6 designs (see spiral_wall/spiral_engine.py), each a matte poster
(blueprint 282 / provider 99, ratios 2:3 / 3:4 / 4:5) -- the physical
counterpart to the digital "spiral_tilings_wall" set.

Keywords lean geometric / boho / op-art rather than maths, because that is
where this artwork competes: it reads as a Southwestern textile long before it
reads as a tiling, and the shop already has fifty listings fighting over
"math wall art".

  python printify/create_spiral_posters.py          # create + publish
  python printify/create_spiral_posters.py create   # Printify only
  python printify/create_spiral_posters.py publish  # publish from JSON
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))   # etsy_manager vive en la raiz
import printify_publish as pp  # noqa: E402

OUT_JSON = HERE / "spiral_posters_created.json"
PRINTS = ROOT / "spiral_wall" / "pod"

POSTER_PRICES = {
    43135: 1500, 101110: 1800, 43138: 1800, 43141: 2400, 101113: 2400,
    43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900,
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

TAGS_BASE = ["spiral wall art", "geometric print", "op art print", "boho wall art",
             "matte poster", "abstract poster", "mid century art", "tessellation art",
             "gallery wall art", "office wall art", "living room art", "math wall art"]


def desc(name, blurb):
    return (
        f"{name} — a matte wall-art poster of a spiral tiling, computed from scratch "
        "rather than drawn or AI-generated.\n\n"
        "One tile shape repeats so that every piece stays the same size while the whole "
        "plane winds around a centre. Rings of constant thickness are cut into pieces "
        "whose count grows with the radius, and a zigzag of constant pitch along each "
        "ring boundary lets rings holding different numbers of pieces still lock "
        "together. Those surplus pieces per ring are what curl the pattern into arms, "
        "and the colour follows the same modular count — the arithmetic is what you "
        f"are looking at.\n\n{blurb}\n\n"
        "• Museum-grade matte poster, printed to order\n"
        "• Portrait sizes from 11x14 up to 24x36 in\n"
        "• Full bleed, no text printed on the art\n"
        "• Ships from a local print partner, ready to frame (frame not included)\n\n"
        "© MathRelaxing"
    )


DESIGNS = [
    ("vortex", "Vortex",
     "Spiral Tiling Poster, Vortex | Geometric Op Art Print, Teal and Rust | Boho Southwestern Wall Art, Matte",
     "Deep teal opening into rust and sand, a slow six-arm sweep.", "teal wall art"),
    ("helix", "Helix",
     "Spiral Tiling Poster, Helix | Geometric Op Art Print, Indigo and Amber | Mid Century Modern Wall Art, Matte",
     "Indigo and amber wound tight, jewel-like toward the centre.", "indigo wall art"),
    ("radiant", "Radiant",
     "Spiral Tiling Poster, Radiant | Geometric Op Art Print, Terracotta and Clay | Southwestern Wall Art, Matte",
     "Dense terracotta and clay bands with a sage counterpoint.", "terracotta decor"),
    ("corona", "Corona",
     "Spiral Tiling Poster, Corona | Geometric Op Art Print, Forest Green and Ochre | Boho Wall Art, Matte",
     "Forest green rings edged in ochre — the calm one of the set.", "green wall art"),
    ("drift", "Drift",
     "Spiral Tiling Poster, Drift | Geometric Op Art Print, Plum and Gold | Abstract Modern Wall Art, Matte",
     "Plum and gold with the centre carried off the page, so the arms read as an open field.",
     "plum wall art"),
    ("pinwheel", "Pinwheel",
     "Spiral Tiling Poster, Pinwheel | Black and White Op Art Print | Monochrome Geometric Wall Art, Matte",
     "High-contrast monochrome — the structure with the colour taken away.", "black white art"),
]


def build():
    out = []
    for slug, name, title, blurb, extra in DESIGNS:
        assert len(title) <= 140, f"title too long ({len(title)}): {title}"
        files = {r: PRINTS / slug / f"{slug}_{r}.jpg" for r in ("2x3", "3x4", "4x5")}
        for f in files.values():
            if not f.is_file():
                raise FileNotFoundError(f)
        out.append({"key": slug, "title": title, "desc": desc(name, blurb),
                    "tags": (TAGS_BASE + [extra])[:13], "files": files})
    return out


def create_all():
    created = []
    for p in build():
        print(f"\n=== CREATE {p['key']} :: {p['title'][:52]}... ===")
        image_ids = {}
        for ratio, path in p["files"].items():
            image_ids[ratio] = pp.upload_image(str(path), f"{p['key']}_{ratio}.jpg")
            time.sleep(0.4)
        variants = [{"id": v, "price": c, "is_enabled": True} for v, c in POSTER_PRICES.items()]
        print_areas = [{"variant_ids": vids,
                        "placeholders": [{"position": "front", "images": [
                            {"id": image_ids[r], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}
                       for r, vids in GROUPS.items()]
        prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", {
            "title": p["title"], "description": p["desc"],
            "blueprint_id": pp.BLUEPRINT_MATTE, "print_provider_id": pp.PROVIDER_CHOICE,
            "variants": variants, "print_areas": print_areas, "tags": p["tags"]})
        pid = prod.get("id")
        print(f"  Printify product: {pid}")
        try:
            pp.margin_report(prod)
        except Exception as e:
            print(f"  margin_report warn: {e}")
        created.append({"key": p["key"], "printify_id": pid, "title": p["title"]})
        time.sleep(0.5)
    OUT_JSON.write_text(json.dumps(created, indent=2), encoding="utf-8")
    return created


def publish_all(created=None):
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for row in created:
        try:
            pp.publish_product(row["printify_id"])
            print(f"  published {row['key']}")
        except Exception as e:
            print(f"  publish ERROR {row['key']}: {e}")
        time.sleep(0.5)

    # Printify's publish is ASYNCHRONOUS (~60-80 s before the Etsy listing
    # exists), so poll instead of taking one early reading -- an early check
    # once reported a false "nothing went live" on this shop.
    print("\n=== verificando en Etsy (polling) ===")
    from etsy_manager import EtsyManager
    m = EtsyManager()
    shop_id = m.get_shop_id()
    wanted = {r["title"]: r["key"] for r in created}
    seen = {}
    for attempt in range(12):
        time.sleep(20)
        for state in ("active", "draft", "inactive"):
            r = m.make_request("GET", f"/shops/{shop_id}/listings?state={state}&limit=100")
            for l in r.get("results", []):
                if l["title"] in wanted and l["title"] not in seen:
                    seen[l["title"]] = (state, l["listing_id"])
                    print(f"  {state:8s} {l['listing_id']}  {wanted[l['title']]}")
        if len(seen) == len(wanted):
            break
        print(f"  intento {attempt + 1}: {len(seen)}/{len(wanted)}")
    if len(seen) < len(wanted):
        print(f"  WARNING: solo aparecieron {len(seen)}/{len(wanted)}")
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
