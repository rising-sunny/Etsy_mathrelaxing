"""Full Etsy + Printify stock/availability audit + shipping processing snapshot."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from etsy_manager import EtsyManager

sys.path.insert(0, str(Path(__file__).resolve().parent / "printify"))
import printify_publish as pp

OUT = Path(__file__).resolve().parent / "printify" / "_stock_shipping_audit.json"

SHIPPING_BLURB_MARK = "SHIPPING & PRODUCTION"


def main():
    m = EtsyManager()
    shop_id = m.get_shop_id()

    # ── Etsy listings ────────────────────────────────────────────────────────
    all_listings = []
    for state in ("active", "draft", "inactive"):
        offset = 0
        while True:
            r = m.make_request(
                "GET",
                f"/shops/{shop_id}/listings?state={state}&limit=100&offset={offset}",
            )
            batch = r.get("results") or []
            if not batch:
                break
            for L in batch:
                L["_state_query"] = state
                all_listings.append(L)
            if len(batch) < 100:
                break
            offset += 100

    print(f"Etsy listings fetched: {len(all_listings)}")

    by_type = Counter()
    physical = []
    digital = []
    issues = []

    for L in all_listings:
        lid = L.get("listing_id")
        title = (L.get("title") or "")[:70]
        ltype = L.get("listing_type") or L.get("type") or "?"
        is_digital = bool(L.get("is_digital")) or ltype == "download"
        qty = L.get("quantity")
        state = L.get("state")
        proc = (L.get("processing_min"), L.get("processing_max"))
        ship = L.get("shipping_profile_id")
        has_variations = L.get("has_variations")
        by_type[(state, "digital" if is_digital else "physical")] += 1

        row = {
            "listing_id": lid,
            "title": title,
            "state": state,
            "type": "digital" if is_digital else "physical",
            "quantity": qty,
            "processing_min": L.get("processing_min"),
            "processing_max": L.get("processing_max"),
            "shipping_profile_id": ship,
            "has_variations": has_variations,
            "url": f"https://www.etsy.com/listing/{lid}",
        }

        # inventory deep check for active
        if state == "active":
            try:
                inv = m.make_request("GET", f"/listings/{lid}/inventory")
                products = inv.get("products") or []
                en_offs = 0
                dis_offs = 0
                zero_qty = 0
                total_qty = 0
                for p in products:
                    for o in p.get("offerings") or []:
                        if o.get("is_deleted"):
                            continue
                        q = int(o.get("quantity") or 0)
                        total_qty += q
                        if o.get("is_enabled"):
                            en_offs += 1
                            if q <= 0:
                                zero_qty += 1
                        else:
                            dis_offs += 1
                row["inv_products"] = len(products)
                row["inv_enabled_offerings"] = en_offs
                row["inv_disabled_offerings"] = dis_offs
                row["inv_zero_qty_enabled"] = zero_qty
                row["inv_total_qty"] = total_qty
                if en_offs == 0:
                    issues.append({"kind": "no_enabled_offerings", **row})
                if zero_qty:
                    issues.append({"kind": "zero_qty_enabled", **row})
                if not is_digital and (L.get("processing_max") or 0) < 7:
                    issues.append({"kind": "processing_too_short", **row})
            except Exception as e:
                row["inv_error"] = str(e)[:160]
                issues.append({"kind": "inv_error", "error": str(e)[:160], **row})

        if is_digital:
            digital.append(row)
        else:
            physical.append(row)

    print("\n=== ETSY COUNTS BY STATE×TYPE ===")
    for k, v in sorted(by_type.items()):
        print(f"  {k}: {v}")

    print(f"\nActive physical: {sum(1 for r in physical if r['state']=='active')}")
    print(f"Active digital:  {sum(1 for r in digital if r['state']=='active')}")

    # processing distribution physical active
    print("\n=== ACTIVE PHYSICAL processing_min/max ===")
    pc = Counter((r["processing_min"], r["processing_max"]) for r in physical if r["state"] == "active")
    for k, v in pc.most_common():
        print(f"  {k}: {v}")

    print("\n=== ACTIVE PHYSICAL qty summary ===")
    for r in sorted(physical, key=lambda x: x.get("title") or "") :
        if r["state"] != "active":
            continue
        print(
            f"  qty={r.get('quantity')} inv_tot={r.get('inv_total_qty')} "
            f"en={r.get('inv_enabled_offerings')} zero={r.get('inv_zero_qty_enabled')} "
            f"proc={r.get('processing_min')}-{r.get('processing_max')}  {r['title'][:55]}"
        )

    print("\n=== ACTIVE DIGITAL qty < 50 or zero ===")
    for r in digital:
        if r["state"] != "active":
            continue
        q = r.get("quantity") or 0
        if q < 50:
            print(f"  LOW qty={q}  {r['title']}")

    # ── Printify ─────────────────────────────────────────────────────────────
    print("\n=== PRINTIFY PRODUCTS ===")
    listing = pp._req("GET", f"/shops/{pp.SHOP_ID}/products.json?limit=50")
    pitems = listing.get("data") or []
    pf_issues = []
    for p in pitems:
        vs = p.get("variants") or []
        en = [v for v in vs if v.get("is_enabled")]
        unavail = [v for v in en if not v.get("is_available")]
        ext = p.get("external") or {}
        etsy_id = ext.get("id")
        row = {
            "printify_id": p.get("id"),
            "title": (p.get("title") or "")[:70],
            "blueprint_id": p.get("blueprint_id"),
            "provider_id": p.get("print_provider_id"),
            "visible": p.get("visible"),
            "etsy_listing_id": etsy_id,
            "enabled_variants": len(en),
            "unavailable_enabled": len(unavail),
            "total_variants": len(vs),
        }
        print(
            f"  en={len(en):2d} unavail={len(unavail)} etsy={etsy_id or 'NOT_PUBLISHED':12} "
            f"bp={p.get('blueprint_id')}  {(p.get('title') or '')[:50]}"
        )
        if unavail:
            pf_issues.append({"kind": "printify_unavailable_variants", **row,
                              "titles": [v.get("title") for v in unavail[:10]]})
        if not etsy_id:
            pf_issues.append({"kind": "printify_not_on_etsy", **row})
        if len(en) == 0:
            pf_issues.append({"kind": "printify_no_enabled_variants", **row})

    report = {
        "etsy_counts": {str(k): v for k, v in by_type.items()},
        "physical_active": [r for r in physical if r["state"] == "active"],
        "digital_active": [r for r in digital if r["state"] == "active"],
        "issues": issues,
        "printify_issues": pf_issues,
        "printify_count": len(pitems),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nISSUES etsy={len(issues)} printify={len(pf_issues)}")
    for i in issues[:30]:
        print(" ", i.get("kind"), i.get("title", "")[:50], i.get("processing_min"), i.get("processing_max"))
    for i in pf_issues:
        print(" ", i.get("kind"), i.get("title", "")[:50])
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
