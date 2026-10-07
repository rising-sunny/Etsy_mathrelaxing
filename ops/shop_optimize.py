"""
Shop optimization ops for TheMathRelaxing:
  - pause_dead: pause up to N zero-traction listings (sold=0, views<=2)
  - ads_plan: print which listings should run Etsy Ads ON vs OFF
  - review_template: print buyer review-request message
  - report: full pause list + ads plan to ops/output/

Etsy Open API has NO advertising endpoints — ads toggles are manual in Seller Hub.
This script gives an exact ON/OFF list.

Usage (from repo root, needs listings_w + transactions_r on token):
  python ops/shop_optimize.py report
  python ops/shop_optimize.py pause_dead --limit 30 --yes
  python ops/shop_optimize.py ads_plan
  python ops/shop_optimize.py review_template
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
# Works both as ops/shop_optimize.py in the repo and standalone on VPS.
if os.path.isfile(os.path.join(_HERE, "etsy_manager.py")):
    ROOT = _HERE
elif os.path.isfile(os.path.join(_HERE, "..", "etsy_manager.py")):
    ROOT = os.path.abspath(os.path.join(_HERE, ".."))
else:
    ROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from etsy_manager import EtsyManager

OUT_DIR = os.path.join(_HERE, "output") if os.path.basename(_HERE) == "ops" else os.path.join(ROOT, "ops", "output")

# Never pause these (high intent / new / core)
PROTECT_IDS = {
    4544209146,  # Coffee table Beauty
    4548870190,  # Shape of an Idea
    4540082607,  # Famous Equations winner
    4538562680,  # Unit Circle
    4539473180,  # Physics Field set v1
}


def fetch_active(m: EtsyManager, shop: int) -> list:
    listings = []
    offset = 0
    while True:
        r = m.make_request("GET", f"/shops/{shop}/listings/active?limit=100&offset={offset}")
        batch = r.get("results") or []
        listings.extend(batch)
        if not batch or offset + len(batch) >= (r.get("count") or 0):
            break
        offset += 100
        time.sleep(0.25)
    return listings


def fetch_sales(m: EtsyManager, shop: int) -> tuple[Counter, dict]:
    sold: Counter = Counter()
    titles: dict = {}
    offset = 0
    while True:
        r = m.make_request(
            "GET", f"/shops/{shop}/receipts?limit=100&offset={offset}&was_paid=true"
        )
        batch = r.get("results") or []
        for rec in batch:
            for txn in rec.get("transactions") or []:
                lid = txn.get("listing_id")
                sold[lid] += int(txn.get("quantity") or 1)
                titles[lid] = (txn.get("title") or "")[:80]
        if not batch or offset + len(batch) >= (r.get("count") or 0):
            break
        offset += 100
        time.sleep(0.25)
    return sold, titles


def views(L):
    return L.get("views") or 0


def favs(L):
    return L.get("num_favorers") or 0


def price(L):
    p = L.get("price") or {}
    if isinstance(p, dict):
        return (p.get("amount") or 0) / (p.get("divisor") or 100)
    return float(p or 0)


def pause_candidates(listings, sold: Counter, limit: int = 30) -> list:
    rows = []
    for L in listings:
        lid = L["listing_id"]
        if lid in PROTECT_IDS:
            continue
        if sold.get(lid, 0) > 0:
            continue
        if views(L) > 2:
            continue
        # Prefer pausing expensive POD deadweight first (bookmarks $17.99, $15 prints)
        p = price(L)
        priority = 0
        t = (L.get("title") or "").lower()
        if "bookmark" in t and "aluminum" in t:
            priority = 100
        elif p >= 15 and L.get("listing_type") != "download":
            priority = 80
        elif p >= 8:
            priority = 50
        else:
            priority = 10
        rows.append(
            {
                "priority": priority,
                "listing_id": lid,
                "views": views(L),
                "favs": favs(L),
                "price": p,
                "type": L.get("listing_type"),
                "title": (L.get("title") or "")[:70],
                "url": L.get("url"),
            }
        )
    rows.sort(key=lambda r: (-r["priority"], r["views"], -r["price"]))
    return rows[:limit]


def ads_plan(listings, sold: Counter) -> dict:
    """ON: sold>0 or (views>=25 and favs>=1) or coffee table.
    OFF: everything else (especially 0 views physical POD)."""
    on, off, watch = [], [], []
    for L in listings:
        lid = L["listing_id"]
        s = sold.get(lid, 0)
        v, f, p = views(L), favs(L), price(L)
        row = {
            "listing_id": lid,
            "sold": s,
            "views": v,
            "favs": f,
            "price": p,
            "title": (L.get("title") or "")[:65],
            "url": L.get("url"),
        }
        if s > 0 or lid == 4544209146:
            row["reason"] = "has_sales" if s > 0 else "high_intent_book"
            on.append(row)
        elif v >= 25 and (f >= 1 or p <= 5):
            row["reason"] = "organic_signal"
            on.append(row)
        elif v >= 15 and s == 0 and p <= 5:
            row["reason"] = "watch_organic_first"
            watch.append(row)
        else:
            row["reason"] = "no_signal_or_dead"
            off.append(row)
    on.sort(key=lambda r: (-r["sold"], -r["views"]))
    off.sort(key=lambda r: (r["views"], -r["price"]))
    watch.sort(key=lambda r: -r["views"])
    return {"ads_on": on, "ads_off": off, "ads_watch": watch}


def review_template() -> str:
    return """\
Subject (if email): Quick thanks from MathRelaxing ✨

--- English (recommended) ---
Hi {{buyer_first_name}},

Thank you so much for your order from MathRelaxing — I hope the prints look great on your wall (or in your classroom)!

If everything arrived as expected, a short review on Etsy would mean a lot. We're a small shop and early reviews help other STEM lovers find us.

It only takes a minute from your order page → Leave a review.

Thanks again,
Esteban
MathRelaxing

--- Español (si el comprador escribió en ES) ---
Hola {{buyer_first_name}},

¡Gracias por tu pedido en MathRelaxing! Espero que los prints te gusten.

Si todo salió bien, una reseña breve en Etsy nos ayuda muchísimo (somos una tienda pequeña).

Desde tu pedido en Etsy → Dejar una reseña.

¡Gracias!
Esteban
MathRelaxing

--- Tips ---
• Send 3–7 days after delivery (digital: 1–2 days after download).
• Never offer payment for reviews (Etsy policy).
• Personalize with the product name when you can.
• Max ~1 follow-up if no reply; don't spam.
"""


def cmd_report(m, shop, limit):
    listings = fetch_active(m, shop)
    sold, _ = fetch_sales(m, shop)
    pause = pause_candidates(listings, sold, limit=limit)
    ads = ads_plan(listings, sold)
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = os.path.join(OUT_DIR, f"shop_optimize_{stamp}.json")
    data = {
        "generated_at": stamp,
        "active_count": len(listings),
        "pause_candidates": pause,
        **ads,
        "ads_on_count": len(ads["ads_on"]),
        "ads_off_count": len(ads["ads_off"]),
        "ads_watch_count": len(ads["ads_watch"]),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Active listings: {len(listings)}")
    print(f"\n=== PAUSE TOP {len(pause)} (sold=0, views<=2) ===")
    for r in pause:
        print(
            f"  {r['listing_id']} v={r['views']} ${r['price']:.2f} [{r['type']}] {r['title']}"
        )

    print(f"\n=== ADS ON ({len(ads['ads_on'])}) — enable in Seller Hub ===")
    for r in ads["ads_on"]:
        print(
            f"  ON  {r['listing_id']} sold={r['sold']} v={r['views']} fav={r['favs']} "
            f"${r['price']:.2f}  ({r['reason']})  {r['title']}"
        )

    print(f"\n=== ADS WATCH only — no ads yet ({len(ads['ads_watch'])}) ===")
    for r in ads["ads_watch"][:15]:
        print(
            f"  ..  {r['listing_id']} v={r['views']} ${r['price']:.2f}  {r['title']}"
        )

    print(
        f"\n=== ADS OFF ({len(ads['ads_off'])}) — keep disabled (showing first 20) ==="
    )
    for r in ads["ads_off"][:20]:
        print(f"  OFF {r['listing_id']} v={r['views']} ${r['price']:.2f}  {r['title']}")

    md = os.path.join(OUT_DIR, f"shop_optimize_{stamp}.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write(f"# Shop optimize {stamp}\n\n")
        f.write(f"Active: {len(listings)}\n\n")
        f.write("## Pause candidates\n\n")
        for r in pause:
            f.write(
                f"- `{r['listing_id']}` v={r['views']} ${r['price']:.2f} — {r['title']}\n"
            )
        f.write("\n## Etsy Ads ON\n\n")
        for r in ads["ads_on"]:
            f.write(
                f"- **ON** `{r['listing_id']}` sold={r['sold']} v={r['views']} — {r['title']}\n"
            )
        f.write("\n## Etsy Ads OFF (rule)\n\n")
        f.write("All other listings: leave ads OFF until they get sales or organic signal.\n")
        f.write("\n## Review message\n\n```\n")
        f.write(review_template())
        f.write("```\n")
    print(f"\nWrote {path}")
    print(f"Wrote {md}")
    return data


def cmd_pause(m, shop, limit, yes: bool):
    listings = fetch_active(m, shop)
    sold, _ = fetch_sales(m, shop)
    pause = pause_candidates(listings, sold, limit=limit)
    print(f"Will pause {len(pause)} listings:")
    for r in pause:
        print(f"  {r['listing_id']}  {r['title']}")
    if not yes:
        print("\nDry-run only. Re-run with --yes to apply state=inactive.")
        return
    ok = fail = 0
    for r in pause:
        lid = r["listing_id"]
        try:
            m.make_request(
                "PATCH",
                f"/shops/{shop}/listings/{lid}",
                payload={"state": "inactive"},
                json_body=True,
            )
            ok += 1
            print(f"  paused {lid}")
        except Exception as e:
            try:
                m.update_listing(lid, state="inactive")
                ok += 1
                print(f"  paused {lid} (form)")
            except Exception as e2:
                fail += 1
                print(f"  FAIL {lid}: {e2}")
        time.sleep(0.35)
    print(f"Done ok={ok} fail={fail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "cmd",
        choices=["report", "pause_dead", "ads_plan", "review_template"],
    )
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--yes", action="store_true", help="Actually pause listings")
    args = ap.parse_args()

    if args.cmd == "review_template":
        print(review_template())
        return

    m = EtsyManager()
    shop = m.get_shop_id()

    if args.cmd == "report":
        cmd_report(m, shop, args.limit)
    elif args.cmd == "pause_dead":
        cmd_pause(m, shop, args.limit, args.yes)
    elif args.cmd == "ads_plan":
        listings = fetch_active(m, shop)
        sold, _ = fetch_sales(m, shop)
        ads = ads_plan(listings, sold)
        print("ADS ON:")
        for r in ads["ads_on"]:
            print(f"  {r['listing_id']} sold={r['sold']} v={r['views']} {r['title']}")
        print("\nADS OFF count:", len(ads["ads_off"]))


if __name__ == "__main__":
    main()
