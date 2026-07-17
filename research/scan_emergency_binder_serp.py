"""Etsy SERP sample for emergency binder printables."""
import json
import time
import urllib.parse
from pathlib import Path

import etsy_manager

OUT = Path(__file__).parent / "emergency_binder_serp.json"
KWS = [
    "emergency binder",
    "emergency binder printable",
    "family emergency binder",
    "in case of emergency binder",
    "home emergency binder",
    "important documents organizer",
]


def main():
    m = etsy_manager.EtsyManager()
    rows, seen = [], set()
    for kw in KWS:
        q = urllib.parse.quote_plus(kw)
        d = m.make_request("GET", f"/listings/active?keywords={q}&limit=15&offset=0")
        print("===", kw, "count", d.get("count"))
        for r in d.get("results") or []:
            lid = r.get("listing_id")
            if lid in seen:
                continue
            seen.add(lid)
            p = r.get("price") or {}
            amt = (p.get("amount") or 0) / (p.get("divisor") or 100)
            row = {
                "keyword": kw,
                "listing_id": lid,
                "favorites": r.get("num_favorers"),
                "price": amt,
                "title": r.get("title"),
                "tags": r.get("tags") or [],
            }
            rows.append(row)
            print(f"  fav={row['favorites']:5} ${amt:6.2f} {(row['title'] or '')[:78]}")
        time.sleep(0.35)
    rows.sort(key=lambda x: int(x.get("favorites") or 0), reverse=True)
    for row in rows[:8]:
        try:
            det = m.make_request("GET", f"/listings/{row['listing_id']}")
            row["description"] = (det.get("description") or "")[:900]
            print(f"\n--- fav={row['favorites']} ${row['price']} {row['title'][:60]}")
            print((row["description"] or "")[:400].replace("\n", " | "))
        except Exception as e:
            print("detail", e)
        time.sleep(0.3)
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", OUT, len(rows))


if __name__ == "__main__":
    main()
