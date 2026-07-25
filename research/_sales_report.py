"""Pull Etsy paid receipts and write a sales focus report."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from etsy_manager import EtsyManager

OUT_JSON = Path(__file__).parent / "sales_live_report.json"
OUT_MD = Path(__file__).parent / "sales_live_report.md"


def money(obj) -> float:
    if not obj or not isinstance(obj, dict):
        return 0.0
    div = obj.get("divisor") or 100
    return (obj.get("amount") or 0) / div


def main():
    m = EtsyManager()
    shop = m.get_shop_id()
    receipts = []
    offset = 0
    while True:
        r = m.make_request(
            "GET", f"/shops/{shop}/receipts?limit=100&offset={offset}&was_paid=true"
        )
        batch = r.get("results") or []
        receipts.extend(batch)
        count = r.get("count") or 0
        if not batch or offset + len(batch) >= count:
            break
        offset += 100

    # shop snapshot for views
    listings = []
    off = 0
    while True:
        data = m.make_request(
            "GET", f"/shops/{shop}/listings/active?limit=100&offset={off}"
        )
        batch = data.get("results") or []
        listings.extend(batch)
        if len(batch) < 100:
            break
        off += 100
    by_id = {x["listing_id"]: x for x in listings}

    rows = []
    product_stats = defaultdict(
        lambda: {
            "title": "",
            "listing_id": None,
            "qty": 0,
            "gross": 0.0,
            "orders": 0,
            "is_digital": None,
        }
    )
    countries = Counter()
    coupons_orders = 0
    multi_item = 0
    total_gross = 0.0
    total_discount = 0.0
    total_vat = 0.0
    messages = []

    for rec in receipts:
        rid = rec["receipt_id"]
        ts = rec.get("created_timestamp") or rec.get("create_timestamp") or 0
        dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
        grand = money(rec.get("grandtotal"))
        sub = money(rec.get("subtotal") or rec.get("total_price"))
        disc = money(rec.get("discount_amt"))
        vat = money(rec.get("total_vat_cost"))
        total_gross += grand
        total_discount += disc
        total_vat += vat
        if disc > 0:
            coupons_orders += 1
        country = rec.get("country_iso") or "?"
        countries[country] += 1
        txs = rec.get("transactions") or []
        if len(txs) > 1:
            multi_item += 1
        if rec.get("message_from_buyer"):
            messages.append((rid, rec.get("message_from_buyer")))

        items = []
        for t in txs:
            lid = t.get("listing_id")
            title = (t.get("title") or "")[:90]
            qty = t.get("quantity") or 1
            price = money(t.get("price"))
            line = price * qty
            # digital heuristic from listing or title
            live = by_id.get(lid) or {}
            is_dig = live.get("is_digital")
            if is_dig is None:
                is_dig = "digital" in title.lower() or "download" in title.lower()
            key = lid or title
            st = product_stats[key]
            st["title"] = title
            st["listing_id"] = lid
            st["qty"] += qty
            st["gross"] += line
            st["orders"] += 1
            st["is_digital"] = is_dig
            items.append(
                {
                    "listing_id": lid,
                    "title": title,
                    "qty": qty,
                    "price": price,
                    "line": line,
                    "transaction_id": t.get("transaction_id"),
                }
            )

        rows.append(
            {
                "receipt_id": rid,
                "date": dt.isoformat() if dt else None,
                "date_local": dt.strftime("%Y-%m-%d %H:%M UTC") if dt else None,
                "buyer_name": rec.get("name"),
                "country": country,
                "city": rec.get("city"),
                "status": rec.get("status"),
                "grandtotal": grand,
                "subtotal": sub,
                "discount": disc,
                "vat": vat,
                "payment_method": rec.get("payment_method"),
                "items": items,
                "n_items": len(items),
            }
        )

    products = sorted(product_stats.values(), key=lambda x: (-x["gross"], -x["qty"]))
    rows.sort(key=lambda x: x.get("date") or "")

    # views of sold listings
    for p in products:
        lid = p["listing_id"]
        live = by_id.get(lid) or {}
        p["views"] = live.get("views")
        p["favorers"] = live.get("num_favorers")
        p["active"] = lid in by_id

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_orders": len(rows),
        "n_line_items": sum(r["n_items"] for r in rows),
        "total_grandtotal_usd": round(total_gross, 2),
        "total_subtotal_usd": round(sum(r["subtotal"] for r in rows), 2),
        "total_discount_usd": round(total_discount, 2),
        "total_vat_usd": round(total_vat, 2),
        "avg_order_value": round(total_gross / len(rows), 2) if rows else 0,
        "multi_item_orders": multi_item,
        "orders_with_discount": coupons_orders,
        "countries": dict(countries),
        "products": products,
        "orders": rows,
        "buyer_messages": messages,
        "active_listings": len(listings),
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    lines = [
        "# Sales analysis — TheMathRelaxing (live Etsy receipts)",
        "",
        f"**Generated:** {report['generated_at']}  ",
        f"**Source:** Etsy API `GET /shops/{{id}}/receipts?was_paid=true` (scope `transactions_r`)",
        "",
        "## Snapshot",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Paid orders | **{report['n_orders']}** |",
        f"| Line items | {report['n_line_items']} |",
        f"| Grand total (buyer paid, USD) | **${report['total_grandtotal_usd']:.2f}** |",
        f"| Subtotal (items) | ${report['total_subtotal_usd']:.2f} |",
        f"| Discounts given | ${report['total_discount_usd']:.2f} |",
        f"| VAT collected | ${report['total_vat_usd']:.2f} |",
        f"| Avg order value (grand) | **${report['avg_order_value']:.2f}** |",
        f"| Multi-item orders | {multi_item} |",
        f"| Orders with coupon | {coupons_orders} |",
        f"| Active listings (shop) | {len(listings)} |",
        "",
        "## By country",
        "",
        "| Country | Orders |",
        "|---------|-------:|",
    ]
    for c, n in countries.most_common():
        lines.append(f"| {c} | {n} |")

    lines += [
        "",
        "## Products sold (focus list)",
        "",
        "| # | Qty | Revenue* | Orders | Type | Views | Listing |",
        "|--:|----:|---------:|-------:|------|------:|---------|",
    ]
    for i, p in enumerate(products, 1):
        kind = "D" if p["is_digital"] else "P"
        views = p.get("views") if p.get("views") is not None else "—"
        title = (p["title"] or "")[:70]
        lines.append(
            f"| {i} | {p['qty']} | ${p['gross']:.2f} | {p['orders']} | {kind} | {views} | {title} |"
        )
    lines.append("")
    lines.append("\\*Revenue = sum of listing unit price × qty (before coupon/VAT split).")
    lines += [
        "",
        "## Order log",
        "",
    ]
    for r in rows:
        lines.append(
            f"### #{r['receipt_id']} — {r['date_local']} — ${r['grandtotal']:.2f} — {r['country']}"
        )
        lines.append(f"- Buyer: {r['buyer_name']} ({r['city']})")
        if r["discount"]:
            lines.append(f"- Discount: −${r['discount']:.2f}")
        for it in r["items"]:
            lines.append(
                f"- ×{it['qty']} ${it['price']:.2f} — {it['title'][:75]} (`{it['listing_id']}`)"
            )
        lines.append("")

    # Focus recommendations
    dig_rev = sum(p["gross"] for p in products if p["is_digital"])
    phys_rev = sum(p["gross"] for p in products if not p["is_digital"])
    top = products[0] if products else None
    lines += [
        "## What to focus on",
        "",
        f"- Digital line revenue (item $): **${dig_rev:.2f}** vs physical: **${phys_rev:.2f}**",
        "",
    ]
    if top:
        lines.append(
            f"1. **Double down on what already sold:** top seller by $ is “{top['title'][:60]}…” "
            f"({top['qty']} units, ${top['gross']:.2f}). Polish SEO, ads, variants/light themes, bundles."
        )
    lines += [
        "2. **Gallery sets beat singles** if equation/STEM sets appear in sales — package more multi-plate downloads.",
        "3. **International demand is real** (see countries) — digital has zero ship friction; keep prices in USD and clear ‘instant download’.",
        "4. **Coupons:** track MATHCODE-style promos — they convert multi-item carts; use sparingly on high-margin digital.",
        "5. **Early sample size:** with few orders, treat this as directional, not statistically final. Still prioritize proven titles over unproven experiments for ads budget.",
        "",
        "See also Wave 14 research for demand keywords; align ads with *sold* SKUs first, then password tracker / systems products as secondary tests.",
        "",
        f"Raw JSON: `{OUT_JSON.name}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
