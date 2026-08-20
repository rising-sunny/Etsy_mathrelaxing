"""
create_organic_posters.py — POD matte posters for the Computed Organic line.

6 designs (see organic_abstract/organic_engine.py), each a matte poster
(blueprint 282 / provider 99, ratios 2:3 / 3:4 / 4:5) -- the physical
counterpart to the digital "organic_abstract" set.

No maths keywords at all here. This line competes in mid-century / boho decor,
where the buyer is choosing by colour and room; that the outlines are Fourier
curves is a reason the work is original, not a search term anyone types.

  python printify/create_organic_posters.py          # create + publish
  python printify/create_organic_posters.py create   # Printify only
  python printify/create_organic_posters.py publish  # publish from JSON
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

OUT_JSON = HERE / "organic_posters_created.json"
PRINTS = ROOT / "organic_abstract" / "pod"

POSTER_PRICES = {
    43135: 1500, 101110: 1800, 43138: 1800, 43141: 2400, 101113: 2400,
    43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900,
}
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

TAGS_BASE = ["abstract wall art", "organic shapes", "mid century modern", "boho wall art",
             "matisse style", "colorful wall art", "modern wall art", "matte poster",
             "gallery wall art", "living room art", "eclectic decor", "abstract poster"]


def desc(name, blurb):
    return (
        f"{name} \u2014 a matte abstract poster in which every shape is a plotted curve "
        "rather than a drawing.\n\n"
        "Each outline is a truncated Fourier series in polar coordinates \u2014 the "
        "amplitudes fall off with harmonic number, so the curve is band-limited and comes "
        "out smooth by construction \u2014 or Gielis' superformula, the equation that "
        "yields petals, shells and rounded polygons from four exponents. The dot textures "
        f"are real lattices clipped to the outlines, not overlays.\n\n{blurb}\n\n"
        "\u2022 Museum-grade matte poster, printed to order\n"
        "\u2022 Portrait sizes from 11x14 up to 24x36 in\n"
        "\u2022 Full bleed, no text printed on the art\n"
        "\u2022 Ships from a local print partner, ready to frame (frame not included)\n\n"
        "\u00a9 MathRelaxing"
    )


DESIGNS = [
    ("reef", "Reef",
     "Abstract Organic Shapes Poster, Reef | Mid Century Modern Wall Art, Navy Coral and Gold | Matisse Style Cut Out Print",
     "Midnight blue ground with coral, gold and teal forms overlapping.", "navy wall art"),
    ("terrace", "Terrace",
     "Abstract Organic Shapes Poster, Terrace | Mid Century Modern Wall Art, Bone and Terracotta | Neutral Boho Print",
     "Bone and terracotta, the quiet one \u2014 warm neutrals with a sage counterpoint.", "neutral wall art"),
    ("canopy", "Canopy",
     "Abstract Organic Shapes Poster, Canopy | Mid Century Modern Wall Art, Forest Green and Ochre | Botanical Abstract Print",
     "Deep forest ground with ochre, blush and cream shapes.", "green wall art"),
    ("neon", "Neon",
     "Abstract Organic Shapes Poster, Neon | Mid Century Modern Wall Art, Black and Electric Brights | Bold Maximalist Print",
     "Black ground with electric green, orange and blue \u2014 the loud one.", "bold wall art"),
    ("kiln", "Kiln",
     "Abstract Organic Shapes Poster, Kiln | Mid Century Modern Wall Art, Warm Clay and Navy | Earthy Terracotta Print",
     "Warm clay ground with navy, cream and burnt red.", "terracotta decor"),
    ("dusk", "Dusk",
     "Abstract Organic Shapes Poster, Dusk | Mid Century Modern Wall Art, Plum Peach and Mint | Moody Abstract Print",
     "Plum ground with peach, gold and mint.", "plum wall art"),
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
    try:
        from etsy_manager import EtsyManager
        m = EtsyManager()
    except Exception as e:
        # etsy_token.json is gitignored and does not survive a container
        # rebuild. Printify publishes through its own Etsy connection, so the
        # posters still go live -- only this read-back check is unavailable.
        print(f"  sin token de Etsy, no puedo verificar aqui ({e})")
        print("  revisa el shop manager: los productos si se publicaron via Printify")
        return created
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
