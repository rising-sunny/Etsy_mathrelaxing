"""Live shop snapshot: views/favs ranking + tags."""
import json
from collections import Counter
from etsy_manager import EtsyManager

m = EtsyManager()
shop = 66586766
listings = []
offset = 0
while True:
    data = m.make_request(
        "GET", f"/shops/{shop}/listings/active?limit=100&offset={offset}"
    )
    res = data.get("results") or []
    if not res:
        break
    for it in res:
        price = it.get("price") or {}
        if isinstance(price, dict):
            p = price.get("amount", 0) / max(price.get("divisor", 100), 1)
        else:
            p = price or 0
        listings.append(
            {
                "id": it.get("listing_id"),
                "title": (it.get("title") or "")[:100],
                "views": it.get("views") or 0,
                "favs": it.get("num_favorers") or 0,
                "price": p,
                "digital": bool(it.get("is_digital") or it.get("listing_type") == "download"),
                "tags": it.get("tags") or [],
            }
        )
    if len(res) < 100:
        break
    offset += 100

listings.sort(key=lambda x: (-x["views"], -x["favs"]))
print("TOTAL", len(listings),
      "digital", sum(1 for x in listings if x["digital"]),
      "physical", sum(1 for x in listings if not x["digital"]))
print("\nTOP BY VIEWS")
for i, x in enumerate(listings[:30], 1):
    kind = "D" if x["digital"] else "P"
    print(f"{i:2}. v={x['views']:3} f={x['favs']:2} ${x['price']:.2f} {kind} {x['title']}")
print("\nTOP BY FAVS")
for x in sorted(listings, key=lambda z: -z["favs"])[:15]:
    print(f"  f={x['favs']:2} v={x['views']:3} {x['title'][:75]}")
c = Counter()
for x in listings:
    for t in x["tags"]:
        c[t.lower()] += 1
print("\nTOP TAGS")
for t, n in c.most_common(25):
    print(f"  {n:3} {t}")
out = {
    "total": len(listings),
    "top_views": listings[:40],
    "top_tags": c.most_common(40),
}
with open("research/live_shop_snapshot_20260725.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("saved research/live_shop_snapshot_20260725.json")
