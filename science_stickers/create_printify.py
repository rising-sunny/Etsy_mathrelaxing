"""
Physical kiss-cut sticker sheets on Printify (blueprint 5372 "Kiss-Cut Sticker Sheet", provider 99,
A5 white). Sticker layer = transparent artwork (the printer adds the 0.12" white border and cuts);
background layer = cream sheet with the set title.

  python create_printify.py --dry     # create products only (no publish), print cost
  python create_printify.py           # create + publish to Etsy
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "printify")); sys.path.insert(0, HERE)
import printify_publish as pp

BP, PROV, VAR = 5372, 99, 244806
PRICE = 999  # cents
PFY = os.path.join(HERE, "out", "printify")
STATE = os.path.join(HERE, "printify_products.json")
SETS = {
    "physics": ("Physics", "an atom, E = mc², Schrödinger's cat, a black hole, a ringed planet, Newton's cradle, a sine wave and a prism"),
    "chemistry": ("Chemistry", "an Erlenmeyer flask, the caffeine, dopamine and serotonin molecules, GENIUS in element tiles, DNA, test tubes and a proton"),
    "math": ("Math", "pi with its digits, the golden spiral, the Mandelbrot set, a Fibonacci sunflower, Euler's identity, the Sierpinski triangle, infinity and Pythagoras"),
}
TAGS = ["science stickers", "{g} stickers", "sticker sheet", "nerdy stickers", "stem stickers", "teacher stickers",
        "science gift", "{g} teacher gift", "laptop stickers", "planner stickers", "kiss cut stickers", "geek stickers", "{g} gift"]
TITLE = "{G} Sticker Sheet, 8 Science Stickers, Nerdy Laptop & Planner Stickers, Gift for {G} Teacher or Student"
DESC = """{G} sticker sheet with 8 kiss-cut stickers: {items}.

Original vector artwork by MathRelaxing: clean lines, warm colours and real science (every molecule is drawn from its true structure and every equation is set like a textbook).

- 1 sheet, 5.83 x 8.27 in (A5), 8 kiss-cut stickers
- Glossy white vinyl film, each sticker with a white border
- Easy peel, for laptops, planners, notebooks, water bottles (indoor use)
- Printed and shipped to order by our print partner

A great little gift for science teachers, students, lab partners and anyone who loves {g}."""


def create(key):
    G, items = SETS[key]; g = G.lower()
    sid = pp.upload_image(os.path.join(PFY, f"{key}_stickers.png"), file_name=f"stickers_{key}.png")
    bid = pp.upload_image(os.path.join(PFY, f"{key}_background.png"), file_name=f"stickers_{key}_bg.png")
    payload = {
        "title": TITLE.format(G=G)[:140], "description": DESC.format(G=G, g=g, items=items),
        "blueprint_id": BP, "print_provider_id": PROV,
        "variants": [{"id": VAR, "price": PRICE, "is_enabled": True}],
        "print_areas": [{"variant_ids": [VAR], "placeholders": [
            {"position": "default", "images": [{"id": sid, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]},
            {"position": "background", "images": [{"id": bid, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]},
        ]}],
        "tags": [t.format(g=g) for t in TAGS],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    v = [x for x in prod["variants"] if x["id"] == VAR][0]
    print(f"  {key}: product {prod['id']}  cost ${v['cost'] / 100:.2f}  price ${v['price'] / 100:.2f}")
    return prod["id"], v["cost"]


def refresh(key, pid):
    """Re-upload artwork for an existing product (keeps title, price, tags)."""
    sid = pp.upload_image(os.path.join(PFY, f"{key}_stickers.png"), file_name=f"stickers_{key}.png")
    bid = pp.upload_image(os.path.join(PFY, f"{key}_background.png"), file_name=f"stickers_{key}_bg.png")
    pp._req("PUT", f"/shops/{pp.SHOP_ID}/products/{pid}.json", {"print_areas": [{"variant_ids": [VAR], "placeholders": [
        {"position": "default", "images": [{"id": sid, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]},
        {"position": "background", "images": [{"id": bid, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]})
    print(f"  {key}: artwork refreshed")


def main():
    dry = "--dry" in sys.argv
    if "--refresh" in sys.argv:
        for key, st in json.load(open(STATE)).items():
            refresh(key, st["pid"])
        return
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    for key in SETS:
        if key not in state:
            pid, cost = create(key); state[key] = {"pid": pid, "cost": cost}
            json.dump(state, open(STATE, "w"), indent=1)
        if not dry and not state[key].get("published"):
            pp.publish_product(state[key]["pid"]); state[key]["published"] = True; print(f"  {key}: publish requested")
            json.dump(state, open(STATE, "w"), indent=1)
    if not dry:
        for key, st in state.items():
            for _ in range(40):
                p = pp.get_product(st["pid"])
                if not p.get("is_locked") and (p.get("external") or {}).get("id"):
                    break
                time.sleep(6)
            st["etsy"] = (p.get("external") or {}).get("id"); print(f"  {key}: etsy listing {st['etsy']}")
        json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
