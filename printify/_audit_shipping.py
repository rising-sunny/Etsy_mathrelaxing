"""
Audit Printify shipping / production times per blueprint × provider
for all POD products in the Etsy shop.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import printify_publish as pp

# Known wave12 products + scan shop for others
KNOWN = [
    ("6a5bf0f381cebb5bdd03a737", "fourier_poster"),
    ("6a5bf105dde591a5200a7d9d", "euler_poster"),
    ("6a5bf113dde591a5200a7da6", "wave_poster"),
    ("6a5bf124ca82e4a6d2013421", "mandelbrot_poster"),
    ("6a5bf199f45e269c8f0106f0", "bauhaus_poster"),
    ("6a5bf1a032a5c3424f0f46a4", "mandelbrot_magnet"),
    ("6a5bf1b3dde591a5200a7e08", "euler_magnet"),
]

FOCUS_COUNTRIES = {
    "US": "United States",
    "CA": "Canada",
    "GB": "United Kingdom",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France",
    "ES": "Spain",
    "IT": "Italy",
    "NL": "Netherlands",
    "MX": "Mexico",
    "JP": "Japan",
    "CL": "Chile",
    "BR": "Brazil",
    "NZ": "New Zealand",
    "REST_OF_THE_WORLD": "Rest of world",
}


def money(cents, currency="USD"):
    if cents is None:
        return "?"
    return f"{currency} {cents/100:.2f}"


def main():
    print("=== SHOP PRODUCTS (blueprint × provider) ===\n")
    combos = {}  # (bp, prov) -> list of product keys
    products_detail = []

    # Also list first page of shop products
    try:
        listing = pp._req("GET", f"/shops/{pp.SHOP_ID}/products.json?limit=50")
        shop_items = listing.get("data") or listing if isinstance(listing, list) else listing.get("data", [])
        print(f"shop product count (page): {len(shop_items)}")
        for p in shop_items:
            key = p.get("title", "")[:40]
            bp = p.get("blueprint_id")
            pr = p.get("print_provider_id")
            combos.setdefault((bp, pr), []).append(key)
            products_detail.append(p)
    except Exception as e:
        print("list products failed:", e)

    for pid, key in KNOWN:
        try:
            p = pp.get_product(pid)
            bp, pr = p.get("blueprint_id"), p.get("print_provider_id")
            combos.setdefault((bp, pr), [])
            if key not in combos[(bp, pr)]:
                combos[(bp, pr)].append(key)
            products_detail.append(p)
            print(f"  {key:22s}  bp={bp}  provider={pr}  id={pid}")
        except Exception as e:
            print(f"  {key}: {e}")

    print("\n=== UNIQUE BLUEPRINT × PROVIDER COMBOS ===")
    for (bp, pr), keys in sorted(combos.items(), key=lambda x: (x[0][0] or 0, x[0][1] or 0)):
        print(f"  blueprint {bp} × provider {pr}  →  {len(keys)} products")
        for k in keys[:8]:
            print(f"      - {k}")

    print("\n=== CATALOG SHIPPING / HANDLING ===\n")
    reports = []
    for (bp, pr) in sorted(combos.keys(), key=lambda x: (x[0] or 0, x[1] or 0)):
        if not bp or not pr:
            continue
        print(f"--- Blueprint {bp} / Provider {pr} ---")
        # provider meta
        try:
            prov = pp._req("GET", f"/catalog/print_providers/{pr}.json")
            print(f"  provider title: {prov.get('title')}")
            loc = prov.get("location") or {}
            if loc:
                print(f"  location: {loc.get('city')}, {loc.get('region')} {loc.get('country')}")
        except Exception as e:
            print(f"  provider meta: {e}")

        try:
            bp_meta = pp._req("GET", f"/catalog/blueprints/{bp}.json")
            print(f"  blueprint: {bp_meta.get('title')} ({bp_meta.get('brand')} {bp_meta.get('model')})")
        except Exception as e:
            print(f"  blueprint meta: {e}")

        try:
            ship = pp._req(
                "GET",
                f"/catalog/blueprints/{bp}/print_providers/{pr}/shipping.json",
            )
        except Exception as e:
            print(f"  shipping API error: {e}")
            continue

        # handling_time
        ht = ship.get("handling_time") or {}
        print(f"  PRODUCTION / HANDLING: {ht.get('value')} {ht.get('unit', 'day')}(s)")
        print(f"  (this is print time before ship — not transit)")

        profiles = ship.get("profiles") or []
        print(f"  shipping profiles: {len(profiles)}")

        # Build country -> profile summary
        by_country = {}
        for prof in profiles:
            first = prof.get("first_item") or {}
            add = prof.get("additional_items") or {}
            countries = prof.get("countries") or []
            entry = {
                "first": first.get("cost"),
                "currency": first.get("currency", "USD"),
                "additional": add.get("cost"),
                "variants": len(prof.get("variant_ids") or []),
            }
            for c in countries:
                by_country.setdefault(c, []).append(entry)

        print("\n  SHIPPING COST (first item) by focus country:")
        print(f"  {'CC':<6} {'Country':<22} {'First':>12} {'Addl':>12}  notes")
        for cc, name in FOCUS_COUNTRIES.items():
            rows = by_country.get(cc) or by_country.get("REST_OF_THE_WORLD")
            src = cc if cc in by_country else ("REST" if by_country.get("REST_OF_THE_WORLD") else None)
            if not rows:
                print(f"  {cc:<6} {name:<22} {'—':>12} {'—':>12}  no profile")
                continue
            # if multiple profiles (size-based), show range
            firsts = [r["first"] for r in rows if r["first"] is not None]
            adds = [r["additional"] for r in rows if r["additional"] is not None]
            cur = rows[0]["currency"]
            if not firsts:
                fstr = "?"
            elif min(firsts) == max(firsts):
                fstr = money(firsts[0], cur)
            else:
                fstr = f"{money(min(firsts), cur)}–{money(max(firsts), cur)}"
            if not adds:
                astr = "?"
            elif min(adds) == max(adds):
                astr = money(adds[0], cur)
            else:
                astr = f"{money(min(adds), cur)}–{money(max(adds), cur)}"
            note = "explicit" if cc in by_country else "via REST_OF_WORLD"
            if len(rows) > 1:
                note += f" · {len(rows)} size bands"
            print(f"  {cc:<6} {name:<22} {fstr:>12} {astr:>12}  {note}")

        # sample raw profile countries for coverage
        all_cc = sorted(by_country.keys())
        print(f"\n  countries/regions with explicit profiles ({len(all_cc)}):")
        print("   ", ", ".join(all_cc[:40]), ("..." if len(all_cc) > 40 else ""))

        reports.append(
            {
                "blueprint_id": bp,
                "provider_id": pr,
                "handling_time": ht,
                "profiles": profiles,
                "by_country_focus": {
                    cc: by_country.get(cc) or by_country.get("REST_OF_THE_WORLD")
                    for cc in FOCUS_COUNTRIES
                },
                "all_country_codes": all_cc,
            }
        )
        print()

    # Try to get delivery estimate from Printify docs pattern - sometimes
    # products have options. Also check if shipping has delivery fields we missed.
    print("=== RAW KEYS SAMPLE (first profile) ===")
    if reports and reports[0]["profiles"]:
        print(json.dumps(reports[0]["profiles"][0], indent=2)[:1500])
        print("handling_time full:", reports[0]["handling_time"])

    out = HERE / "_shipping_audit.json"
    out.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")

    print(
        """
=== HOW TO READ THIS ===
• handling_time = production / print time at the facility (business days typically)
• shipping profiles = cost only in this API; transit days are NOT always exposed
• Total customer ETA ≈ production + carrier transit (varies by destination & method)
• Printify Choice (provider 99) routes to nearest facility — times vary by region
"""
    )


if __name__ == "__main__":
    main()
