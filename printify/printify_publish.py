"""
printify_publish.py — Printify Print-on-Demand client for MathRelaxing posters.

Unlike Printful (whose API blocks product creation for platform-connected
stores), Printify lets us do the WHOLE flow via API for an Etsy-connected
shop: upload art -> create product -> publish to Etsy -> auto-fulfill orders.

Flow
----
1. upload_image(path)            -> uploads art (base64), returns image_id.
2. create_poster(...)            -> creates the product in Printify
   (blueprint 282 "Matte Vertical Posters" x provider 99 "Printify Choice",
   which offers both square and portrait sizes at 300 dpi). Returns the
   product with per-variant COST so we can sanity-check margins. This does
   NOT put anything on Etsy yet.
3. publish_product(product_id)   -> pushes it to the connected Etsy shop.
   THIS is the step that creates the Etsy listing (as a draft, per Printify's
   default publish settings). Call it only after reviewing the product.

Fulfillment is automatic: once published and someone buys on Etsy, Printify
receives the order and prints/ships it. No order-polling automation needed
(unlike the Lulu book flow).

Config: printify/.env (gitignored) — PRINTIFY_TOKEN, PRINTIFY_ETSY_SHOP_ID.
"""
import base64
import json
import os
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.printify.com/v1"
UA = "MathRelaxing/1.0 (posters)"

BLUEPRINT_MATTE = 282        # "Matte Vertical Posters"
PROVIDER_CHOICE = 99         # "Printify Choice"

# size title -> Printify variant id (blueprint 282 / provider 99)
SQUARE_SIZES = {
    "10x10": 101119, "12x12": 101127, "14x14": 112749, "16x16": 101120,
    "18x18": 101133, "20x20": 101121, "24x24": 101140,
}
PORTRAIT_SIZES = {
    "11x14": 43135, "12x16": 101110, "12x18": 43138, "16x20": 43141,
    "16x24": 101113, "18x24": 43144, "20x30": 43147, "24x36": 43150,
    "30x40": 101118,
}


def load_env():
    """Load printify/.env, then overlay OS env vars."""
    env = {}
    path = os.path.join(HERE, ".env")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("PRINTIFY_TOKEN", "PRINTIFY_ETSY_SHOP_ID", "PRINTIFY_SHOP_ID"):
        v = os.environ.get(k)
        if v:
            env[k] = v.strip()
    if "PRINTIFY_ETSY_SHOP_ID" not in env and "PRINTIFY_SHOP_ID" in env:
        env["PRINTIFY_ETSY_SHOP_ID"] = env["PRINTIFY_SHOP_ID"]
    return env


ENV = load_env()
if "PRINTIFY_TOKEN" not in ENV or "PRINTIFY_ETSY_SHOP_ID" not in ENV:
    raise RuntimeError(
        "Missing Printify credentials. Create printify/.env with:\n"
        "  PRINTIFY_TOKEN=...\n"
        "  PRINTIFY_ETSY_SHOP_ID=...\n"
        "Token: https://printify.com/app/account/api\n"
        "Scopes: catalog.read shops.read products.read products.write uploads.write"
    )
TOKEN = ENV["PRINTIFY_TOKEN"]
SHOP_ID = ENV["PRINTIFY_ETSY_SHOP_ID"]


def _req(method, path, body=None):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:500]
        raise RuntimeError(f"Printify {method} {path} -> HTTP {e.code}: {msg}")


def upload_image(local_path, file_name=None):
    file_name = file_name or os.path.basename(local_path)
    with open(local_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    res = _req("POST", "/uploads/images.json", {"file_name": file_name, "contents": b64})
    print(f"  imagen subida: {file_name} -> id={res['id']} ({res.get('width')}x{res.get('height')})")
    return res["id"]


def create_poster(title, description, image_id, sizes_prices, tags=None,
                  blueprint_id=BLUEPRINT_MATTE, provider_id=PROVIDER_CHOICE):
    """sizes_prices: dict {variant_id: retail_price_cents}. Image is centered
    at full scale in the 'front' print area of every chosen variant."""
    variant_ids = list(sizes_prices.keys())
    variants = [{"id": vid, "price": price, "is_enabled": True}
                for vid, price in sizes_prices.items()]
    payload = {
        "title": title,
        "description": description,
        "blueprint_id": blueprint_id,
        "print_provider_id": provider_id,
        "variants": variants,
        "print_areas": [{
            "variant_ids": variant_ids,
            "placeholders": [{
                "position": "front",
                "images": [{"id": image_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}],
            }],
        }],
        "tags": tags or [],
    }
    res = _req("POST", f"/shops/{SHOP_ID}/products.json", payload)
    return res


def get_product(product_id):
    return _req("GET", f"/shops/{SHOP_ID}/products/{product_id}.json")


def publish_product(product_id):
    """Push the product to the connected Etsy shop (creates the Etsy listing).
    Printify's default publishes it as a DRAFT on Etsy."""
    body = {"title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True}
    return _req("POST", f"/shops/{SHOP_ID}/products/{product_id}/publish.json", body)


def create_order(order_body):
    """Create a new order in Printify."""
    return _req("POST", f"/shops/{SHOP_ID}/orders.json", order_body)



def margin_report(product):
    """Print cost vs retail per variant so we can sanity-check pricing."""
    print(f"\n  {'SIZE':<14}{'COST':>8}{'RETAIL':>9}{'PROFIT':>9}")
    for v in product.get("variants", []):
        if not v.get("is_enabled"):
            continue
        cost = v.get("cost", 0) / 100
        price = v.get("price", 0) / 100
        print(f"  {v.get('title','')[:14]:<14}{cost:>8.2f}{price:>9.2f}{price-cost:>9.2f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "shops":
        print(json.dumps(_req("GET", "/shops.json"), indent=2))
