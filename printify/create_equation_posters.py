"""
create_equation_posters.py — POD matte posters for the Famous Equations line.

Physical counterpart to the "Famous Equations Wall Art Set of 6" digital
bundle (listing 4540082607) -- the shop's only design bought by more than one
distinct organic customer, and physical sales net ~5.5x a digital download.

6 designs, each a matte poster (blueprint 282 / provider 99, ratios
2:3 / 3:4 / 4:5), published to the Etsy-connected shop via Printify.
Print files come from equation_plates/build_equation_pod_prints.py.

  python printify/create_equation_posters.py          # create + publish
  python printify/create_equation_posters.py create   # Printify only
  python printify/create_equation_posters.py publish  # publish existing from JSON
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

OUT_JSON = HERE / "equation_posters_created.json"
PRINTS = ROOT / "equation_plates" / "pod_products"

# Same size ladder / price points as the vintage + Turing POD lines.
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

TAGS_BASE = ["matte poster", "math wall art", "science poster", "physics poster",
             "equation art", "stem wall art", "classroom decor", "teacher gift",
             "office wall art", "nerd gift", "educational poster"]


def desc(name, blurb):
    return (
        f"{name} — a matte wall-art poster of an original, hand-coded scientific "
        f"plate. Every curve is computed from the real mathematics and typeset in "
        f"LaTeX (Computer Modern), not clip art or AI.\n\n{blurb}\n\n"
        "• Museum-grade matte poster, printed to order\n"
        "• Portrait sizes from 11x14 up to 24x36 in\n"
        "• Warm graph-paper ground with ink linework and rust accents\n"
        "• Ships from a local print partner, ready to frame (frame not included)\n\n"
        f"{COPYRIGHT}"
    )


DESIGNS = [
    ("fourier_series", "The Shape of Waves",
     "Fourier Series Poster, Square Wave Harmonics | Math Wall Art, LaTeX Scientific Plate | Matte Classroom Science Print",
     "Any periodic signal is a sum of pure sinusoids. Four partial sums build a square "
     "wave, and the Gibbs overshoot at the jump never quite vanishes.",
     ["fourier series", "signal processing"]),
    ("wave_equation", "The Traveling Wave",
     "Wave Equation Poster, Standing Waves on a String | Physics Wall Art, LaTeX Scientific Plate | Matte Science Print",
     "The wave equation links acceleration in time to curvature in space. On a fixed "
     "string, only discrete modes fit -- the harmonics of music.",
     ["wave equation", "standing waves"]),
    ("dirac_equation", "Matter and Antimatter",
     "Dirac Equation Poster, Matter and Antimatter | Quantum Physics Wall Art, LaTeX Plate | Matte Science Print",
     "Dirac united special relativity with quantum mechanics for the electron. The "
     "negative-energy solutions predicted antimatter, later found in the positron.",
     ["dirac equation", "quantum physics art"]),
    ("navier_stokes", "The Equations of Flow",
     "Navier-Stokes Poster, Fluid Dynamics Streamlines | Physics Wall Art, LaTeX Plate | Matte Engineering Print",
     "Navier-Stokes describes how velocity and pressure evolve in a viscous fluid. From "
     "airplane wings to blood flow -- and still unsolved in full generality.",
     ["navier stokes", "fluid dynamics art"]),
    ("euler_identity", "The Most Beautiful Equation",
     "Euler's Identity Poster, e^ipi+1=0 Complex Plane | Math Wall Art, LaTeX Plate | Matte Science Print",
     "Euler's formula links exp, trig, and geometry. At theta = pi the five fundamental "
     "constants meet in one identity: 0, 1, i, e and pi.",
     ["eulers identity", "complex numbers"]),
    ("mandelbrot_set", "The Geometry of Chaos",
     "Mandelbrot Set Poster, Fractal Chaos Theory | Math Wall Art, LaTeX Scientific Plate | Matte Science Print",
     "Iterate z -> z^2 + c from zero. If the orbit stays bounded, c is in the set: a "
     "simple rule with an infinite coastline.",
     ["mandelbrot set", "fractal art"]),
]


def build_products():
    prods = []
    for slug, name, title, blurb, extra_tags in DESIGNS:
        pd = PRINTS / slug
        files = {r: pd / f"{slug}_{r}.jpg" for r in ("2x3", "3x4", "4x5")}
        for f in files.values():
            if not f.is_file():
                raise FileNotFoundError(f)
        assert len(title) <= 140, f"title too long ({len(title)}): {title}"
        tags = (extra_tags + TAGS_BASE)[:13]
        prods.append({"key": slug, "name": name, "title": title,
                      "desc": desc(name, blurb), "tags": tags, "files": files})
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
            image_ids[ratio] = pp.upload_image(str(path), f"eq_{p['key']}_{ratio}.jpg")
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
    """Publish to Etsy, then pull anything that came back ACTIVE down to an
    unpublished state. Printify's publish_product() is documented to create
    Etsy DRAFTS, but on this shop it has twice produced live listings instead,
    so this verifies rather than trusting the documented behaviour."""
    if created is None:
        created = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    for row in created:
        print(f"\n=== PUBLISH {row['key']} ({row['printify_id']}) ===")
        try:
            pp.publish_product(row["printify_id"])
            print("  published")
        except Exception as e:
            print(f"  publish ERROR: {e}")
        time.sleep(1.2)

    # Printify's publish is ASYNCHRONOUS -- the Etsy listing showed up ~60-80s
    # after the publish call returned. Checking immediately reports a false
    # "none went active", so poll instead of taking one early reading.
    print("\n=== verifying Etsy state (polling, publish is async) ===")
    from etsy_manager import EtsyManager
    m = EtsyManager()
    shop_id = m.get_shop_id()
    wanted = {r["title"] for r in created}
    seen = {}
    for attempt in range(10):
        time.sleep(20)
        for state in ("active", "draft", "inactive"):
            r = m.make_request("GET", f"/shops/{shop_id}/listings?state={state}&limit=100")
            for l in r.get("results", []):
                if l["title"] in wanted:
                    seen[l["listing_id"]] = (state, l["title"])
        print(f"  intento {attempt + 1}: {len(seen)}/{len(wanted)} encontrados")
        if len(seen) >= len(wanted):
            break
    for lid, (state, title) in seen.items():
        print(f"  {state:8s} | {lid} | {title[:52]}")
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
