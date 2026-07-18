import json
import printify_publish as pp

checks = [
    (282, 99, "Matte Vertical Posters"),
    (428, 1, "Magnets SPOKE"),
    (5113, None, "Matte Carryall Tote"),
    (1346, None, "Doormat"),
    (600, None, "Die-Cut Stickers"),
    (582, 99, "Mouse Pad Choice"),
    (485, 28, "Hardcover Journal"),
]

for bp, prov, name in checks:
    if prov is None:
        provs = pp._req("GET", f"/catalog/blueprints/{bp}/print_providers.json")
        if isinstance(provs, dict):
            provs = provs.get("data") or []
        print(f"\n{name} bp={bp} providers={[ (p.get('id'), p.get('title')) for p in provs[:5] ]}")
        if not provs:
            continue
        prov = provs[0]["id"]
    v = pp._req("GET", f"/catalog/blueprints/{bp}/print_providers/{prov}/variants.json")
    if isinstance(v, dict):
        variants = v.get("variants") or []
        print(f"{name} bp={bp} prov={prov} n={len(variants)} top_keys={list(v.keys())[:10]}")
        if variants:
            print("  variant0 keys", list(variants[0].keys()))
            for x in variants[:8]:
                print(f"  id={x.get('id')} title={x.get('title')!r} cost={x.get('cost')} opts={x.get('options')}")
    else:
        print(name, type(v), str(v)[:200])

# existing products with real costs
print("\n=== existing shop products (real costs) ===")
res = pp._req("GET", f"/shops/{pp.SHOP_ID}/products.json?limit=20")
prods = res.get("data") if isinstance(res, dict) else res
for p in prods or []:
    full = pp._req("GET", f"/shops/{pp.SHOP_ID}/products/{p['id']}.json")
    print(f"\n{full.get('title','')[:60]}  bp={full.get('blueprint_id')} id={full.get('id')}")
    for v in (full.get("variants") or [])[:8]:
        if v.get("is_enabled"):
            print(f"  {v.get('title')}: cost={v.get('cost')} price={v.get('price')}")
