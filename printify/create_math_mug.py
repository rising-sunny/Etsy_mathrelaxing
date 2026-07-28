"""
create_math_mug.py — MUG-NATIVE math mugs for MathRelaxing (Printify → Etsy)
============================================================================
Creates the three seamless-wrap math mugs (unrolled · fourier · harmonics) on
the Accent Coffee Mug (blueprint 635 / provider 99 Printify Choice), Navy accent,
11oz + 15oz. Printify auto-generates the professional mockups; we download the
defaults for the Etsy listing and publish as an Etsy DRAFT.

  python printify/create_math_mug.py art             # (re)render wraps only
  python printify/create_math_mug.py create <key|all>  # upload + create product(s)
  python printify/create_math_mug.py mockups <product_id>  # download mockups
  python printify/create_math_mug.py publish <product_id>  # push to Etsy (draft)

Does NOT publish to Etsy unless you pass `publish`.
"""
from __future__ import annotations
import os, sys, json, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mug_designs as MD           # wrap renderers (no token needed)
import printify_publish as pp      # Printify client (needs token)

BLUEPRINT = 635                    # Accent Coffee Mug (11, 15oz)
PROVIDER = 99                      # Printify Choice
# Navy accent variants (body white, handle/rim/interior navy — matches the ink)
VARIANTS = {72182: 1899, 105885: 2199}   # 11oz $18.99 · 15oz $21.99 (tune after cost)
POSITION = "front"                 # single 360° wrap print area
MOCK = os.path.join(HERE, "_mug_art")


# ── SEO copy per design (Etsy title ≤140 chars, ≤1 '&'; 13 tags ≤20 chars) ─────
def _desc(hook, body_lines):
    return (
        f"{hook}\n\n"
        "This is not a slap-on graphic. The art is drawn for the cylinder: the "
        "curve wraps the whole way around, so one full turn of the mug is one full "
        "cycle of the math — it meets itself seamlessly behind the handle.\n\n"
        + "\n".join(body_lines) + "\n\n"
        "WHAT YOU GET\n"
        "• Ceramic accent mug — white body, navy handle & interior\n"
        "• Sizes: 11oz and 15oz · dishwasher & microwave safe\n"
        "• 360° wraparound design, printed edge to edge\n"
        "• Print-on-demand — made fresh when you order\n\n"
        "GREAT FOR\n"
        "• Gift for a mathematician, physicist, engineer or teacher\n"
        "• STEM student, professor, science lover\n"
        "• A calm, clever mug for the desk or the morning coffee\n\n"
        "MathRelaxing — math & science art written in code, not AI clipart."
    )


DESIGNS = {
    "unrolled": {
        "title": ("Sine Wave Math Mug | Unit Circle Trigonometry Coffee Mug | "
                  "Gift for Math Teacher Student Mathematician (11oz, 15oz)"),
        "description": _desc(
            "Sine wave coffee mug — the unit circle unrolled into one full wave around the cup.",
            ["THE MATH",
             "• The unit circle on the left unrolls into y = sin θ",
             "• The wave spans exactly one period, 0 to 2π, around the mug",
             "• Turn the mug and you walk through one full turn of trigonometry"]),
        "tags": ["math mug", "sine wave", "trigonometry gift", "math teacher gift",
                 "unit circle", "mathematician gift", "math student gift", "stem gift",
                 "science mug", "nerdy mug", "calculus gift", "geek gift", "teacher mug"],
    },
    "fourier": {
        "title": ("Fourier Series Math Mug | Square Wave Harmonics Physics Coffee Mug | "
                  "Gift for Engineer Physicist Mathematician (11oz, 15oz)"),
        "description": _desc(
            "Fourier series coffee mug — a square wave built from its harmonics, wrapping the cup.",
            ["THE MATH",
             "• A square wave summed from its odd harmonics (sin x + sin3x/3 + …)",
             "• The famous Gibbs ripple, with the ideal square in gold",
             "• One fundamental period wraps seamlessly around the mug"]),
        "tags": ["fourier series", "engineer gift", "physics mug", "math mug",
                 "signal processing", "gift for engineer", "stem gift", "science mug",
                 "nerdy mug", "physicist gift", "mathematician gift", "dsp gift", "teacher mug"],
    },
    "harmonics": {
        "title": ("Standing Wave Harmonics Mug | Physics of Music Vibrating String Coffee Mug | "
                  "Gift for Physicist Musician Teacher (11oz, 15oz)"),
        "description": _desc(
            "Harmonics coffee mug — the first five modes of a vibrating string, wrapping the cup.",
            ["THE MATH",
             "• The 1st–5th standing-wave modes of a vibrating string",
             "• Nodes marked in gold; each mode is a pure harmonic",
             "• The modes close on themselves at the handle — a seamless wrap"]),
        "tags": ["physics mug", "harmonics", "wave physics", "music physics",
                 "gift for physicist", "standing wave", "science mug", "math mug",
                 "stem gift", "musician gift", "acoustics gift", "teacher mug", "nerdy mug"],
    },
}


def render_all_art():
    for k in DESIGNS:
        MD.DESIGNS[k]()
    print("wraps ready in", MD.OUT)


def _wrap_path(key):
    p = os.path.join(MD.OUT, f"mug_{key}_wrap.png")
    if not os.path.isfile(p):
        MD.DESIGNS[key]()
    return p


def create_one(key):
    d = DESIGNS[key]
    print(f"\n=== creating mug: {key} ===")
    img_id = pp.upload_image(_wrap_path(key), f"mug_{key}_wrap.png")
    variants = [{"id": vid, "price": price, "is_enabled": True} for vid, price in VARIANTS.items()]
    payload = {
        "title": d["title"],
        "description": d["description"],
        "blueprint_id": BLUEPRINT,
        "print_provider_id": PROVIDER,
        "variants": variants,
        "print_areas": [{
            "variant_ids": list(VARIANTS.keys()),
            "placeholders": [{
                "position": POSITION,
                "images": [{"id": img_id, "x": 0.5, "y": 0.5, "scale": 1.0, "angle": 0}],
            }],
        }],
        "tags": d["tags"],
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    pid = prod.get("id")
    print("  PRODUCT ID:", pid)
    print("  TITLE:", prod.get("title")[:70])
    pp.margin_report(prod)
    _save_meta(key, prod)
    return prod


def _save_meta(key, prod):
    meta_path = os.path.join(MOCK, "mugs_created.json")
    data = {}
    if os.path.isfile(meta_path):
        data = json.load(open(meta_path))
    data[key] = {"product_id": prod.get("id"), "title": prod.get("title"),
                 "blueprint": BLUEPRINT, "provider": PROVIDER,
                 "variants": VARIANTS, "published": False}
    json.dump(data, open(meta_path, "w"), indent=2)


_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def download_mockups(product_id, key=None, limit=5):
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", _UA)]     # Printify CDN 403s without a browser UA
    urllib.request.install_opener(opener)
    prod = pp._req("GET", f"/shops/{pp.SHOP_ID}/products/{product_id}.json")
    key = key or "prod"
    imgs = prod.get("images", [])
    print(f"  {len(imgs)} mockups available for {product_id}")
    saved = []
    for i, im in enumerate(imgs):
        if im.get("src") and (im.get("is_default") or i < limit):
            url = im["src"]
            fn = os.path.join(MOCK, f"mug_{key}_pfy_{i:02d}{'_default' if im.get('is_default') else ''}.jpg")
            try:
                urllib.request.urlretrieve(url, fn)
                saved.append(fn); print("   ", os.path.basename(fn))
            except Exception as e:
                print("    (skip)", e)
        if len(saved) >= limit:
            break
    return saved


def publish(product_id):
    print("Publishing to Etsy (Printify → Etsy draft)…")
    res = pp.publish_product(product_id)
    print(json.dumps(res, indent=2)[:400])
    return res


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "art"
    if cmd == "art":
        render_all_art()
    elif cmd == "create":
        which = sys.argv[2] if len(sys.argv) > 2 else "all"
        keys = list(DESIGNS) if which == "all" else [which]
        for k in keys:
            create_one(k)
    elif cmd == "mockups" and len(sys.argv) > 2:
        download_mockups(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "publish" and len(sys.argv) > 2:
        publish(sys.argv[2])
    else:
        print(__doc__)
