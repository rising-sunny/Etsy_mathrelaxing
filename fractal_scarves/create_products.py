"""
Fractal scarves on Printify: blueprint 264 "Poly Scarf", provider 48 (Colorway),
poly chiffon 25" and 50" (dye-sublimation). Artwork: out/final/<key>.jpg (9000 px).

  python create_products.py --dry [keys]  # create only, print costs
  python create_products.py [keys]        # create + publish to Etsy
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "printify")); sys.path.insert(0, HERE)
import printify_publish as pp
from fractals import DESIGNS

BP, PROV = 264, 48
VARIANTS = {42318: 3900, 42319: 6400}      # chiffon 25" , chiffon 50"  (price in cents)
STATE = os.path.join(HERE, "products.json")
TAGS = ["fractal scarf", "math scarf", "{tag}", "chiffon scarf", "square scarf", "math teacher gift", "science gift",
        "mathematician gift", "art scarf", "fractal art", "neck scarf", "gift for her", "math lover gift"]
TITLE = "{name} Fractal Scarf, {what} Chiffon Square Scarf, Math Art Gift for Teacher, Scientist or Mathematician"
DESC = """{name}: a sheer chiffon square scarf printed with {blurb}, framed like a classic carré.

The artwork is computed from the mathematics itself, pixel by pixel, at very high resolution, then finished with a fine gold-line border and a small signature. Not AI, not clip art: real mathematics turned into wearable art.

- 100% polyester chiffon, light, airy and sheer
- Two sizes: 25" x 25" (neck scarf / bandana) and 50" x 50" (shawl / wrap)
- Vivid dye-sublimation print, black stitched edges
- Printed and shipped to order by our print partner

A one-of-a-kind gift for math teachers, scientists, engineers, programmers and anyone who loves art and numbers. Designed by MathRelaxing."""
WHAT = {"midnight_mandelbrot": "Mandelbrot Set", "coral_julia": "Julia Set", "stained_glass": "Newton Fractal",
        "seahorse_valley": "Mandelbrot Zoom", "zircon_lyapunov": "Lyapunov Fractal", "golden_angle": "Golden Ratio"}
TAG3 = {"midnight_mandelbrot": "mandelbrot", "coral_julia": "julia set", "stained_glass": "newton fractal",
        "seahorse_valley": "mandelbrot", "zircon_lyapunov": "lyapunov fractal", "golden_angle": "golden ratio"}


def create(key):
    name, blurb = DESIGNS[key][0], DESIGNS[key][1]
    img = pp.upload_image(os.path.join(HERE, "out", "final", f"{key}.jpg"), file_name=f"scarf_{key}.jpg")
    title = TITLE.format(name=name, what=WHAT[key])
    if len(title) > 140:
        title = f"{name} Fractal Scarf, {WHAT[key]} Chiffon Square Scarf, Math Art Gift for Teacher or Scientist"
    payload = {
        "title": title[:140], "description": DESC.format(name=name, blurb=blurb),
        "blueprint_id": BP, "print_provider_id": PROV,
        "variants": [{"id": v, "price": p, "is_enabled": True} for v, p in VARIANTS.items()],
        "print_areas": [{"variant_ids": list(VARIANTS), "placeholders": [
            {"position": "front", "images": [{"id": img, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}],
        "tags": [t.format(tag=TAG3[key]) for t in TAGS],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    costs = {v["title"]: (v["cost"], v["price"]) for v in prod["variants"] if v["id"] in VARIANTS}
    print(f"  {key}: product {prod['id']}  " + "  ".join(f"{t}: cost ${c / 100:.2f} price ${p / 100:.2f}" for t, (c, p) in costs.items()))
    return prod["id"]


def main():
    args = sys.argv[1:]; dry = "--dry" in args; only = [a for a in args if not a.startswith("--")]
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    for key in DESIGNS:
        if only and key not in only:
            continue
        if key not in state:
            state[key] = {"pid": create(key)}; json.dump(state, open(STATE, "w"), indent=1)
        if not dry and not state[key].get("published"):
            pp.publish_product(state[key]["pid"]); state[key]["published"] = True
            json.dump(state, open(STATE, "w"), indent=1); print(f"  {key}: publish requested")
    if not dry:
        for key, st in state.items():
            if only and key not in only:
                continue
            for _ in range(50):
                p = pp.get_product(st["pid"])
                if not p.get("is_locked") and (p.get("external") or {}).get("id"):
                    break
                time.sleep(6)
            st["etsy"] = (p.get("external") or {}).get("id"); print(f"  {key}: etsy listing {st['etsy']}")
        json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
