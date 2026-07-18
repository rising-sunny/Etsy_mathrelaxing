"""Audit digital listing prices: catalog + live Etsy shop."""
from __future__ import annotations

from products_catalog import PRODUCTS
from etsy_manager import EtsyManager


def money(price_obj) -> float:
    if price_obj is None:
        return 0.0
    if isinstance(price_obj, dict):
        return float(price_obj.get("amount", 0)) / float(price_obj.get("divisor", 100) or 100)
    return float(price_obj)


def fetch_state(m: EtsyManager, shop: int, state: str) -> list[dict]:
    offset = 0
    all_ = []
    while True:
        ep = f"/shops/{shop}/listings?state={state}&limit=100&offset={offset}"
        r = m.make_request("GET", ep)
        results = r.get("results") or []
        all_.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return all_


def main():
    print("=== CATALOG (products_catalog.py) ===")
    rows = []
    for key, p in PRODUCTS.items():
        price = float(p.get("price", 0))
        title = (p.get("title") or key)[:60]
        lid = p.get("listing_id")
        rows.append((price, key, title, lid))
    rows.sort(reverse=True)
    for price, key, title, lid in rows:
        print(f"  ${price:5.2f}  {key:35}  lid={lid}  {title}")

    prices = [r[0] for r in rows]
    if prices:
        print(
            f"\n  n={len(prices)}  min=${min(prices):.2f}  "
            f"median=${sorted(prices)[len(prices)//2]:.2f}  "
            f"mean=${sum(prices)/len(prices):.2f}  max=${max(prices):.2f}"
        )

    print("\n=== LIVE ETSY ===")
    m = EtsyManager()
    shop = m.get_shop_id()
    for state in ("active", "draft", "inactive"):
        try:
            items = fetch_state(m, shop, state)
        except Exception as e:
            print(f"  {state}: error {e}")
            continue
        print(f"\n--- {state}: {len(items)} listings ---")
        dig = []
        phys = []
        for it in items:
            typ = (it.get("listing_type") or it.get("type") or "").lower()
            p = money(it.get("price"))
            row = (p, typ, it.get("listing_id"), (it.get("title") or "")[:55], it.get("views", 0), it.get("num_favorers", 0))
            if typ in ("download", "digital", "downloadable"):
                dig.append(row)
            else:
                phys.append(row)
        dig.sort(reverse=True)
        phys.sort(reverse=True)
        print(f"  digital: {len(dig)}  physical/other: {len(phys)}")
        if dig:
            dp = [r[0] for r in dig]
            print(
                f"  digital price: min=${min(dp):.2f} median=${sorted(dp)[len(dp)//2]:.2f} "
                f"mean=${sum(dp)/len(dp):.2f} max=${max(dp):.2f}"
            )
            print("  Top / sample digital:")
            for r in dig[:25]:
                print(f"    ${r[0]:5.2f}  views={r[4]:4} favs={r[5]:3}  id={r[2]}  {r[3]}")
            if len(dig) > 25:
                print(f"    ... +{len(dig)-25} more")
                print("  Lowest digital:")
                for r in dig[-8:]:
                    print(f"    ${r[0]:5.2f}  views={r[4]:4} favs={r[5]:3}  id={r[2]}  {r[3]}")


if __name__ == "__main__":
    main()
