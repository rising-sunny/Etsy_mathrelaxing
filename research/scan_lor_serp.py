"""Inspect Etsy SERP for letter of recommendation templates."""
import json
import time
import urllib.parse
from pathlib import Path

import etsy_manager

OUT = Path(__file__).parent / "lor_serp.json"
KWS = [
    "letter of recommendation",
    "letter of recommendation template",
    "recommendation letter template",
    "teacher recommendation letter",
    "letter of recommendation for job",
    "character reference letter template",
    "academic recommendation letter",
]


def main():
    m = etsy_manager.EtsyManager()
    rows = []
    seen = set()
    for kw in KWS:
        q = urllib.parse.quote_plus(kw)
        d = m.make_request(
            "GET",
            f"/listings/active?keywords={q}&limit=20&offset=0&sort_on=score",
        )
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
                "url": f"https://www.etsy.com/listing/{lid}",
                "tags": r.get("tags") or [],
                "is_digital": r.get("is_digital") or r.get("listing_type") == "download",
            }
            rows.append(row)
            print(f"  fav={row['favorites']:5} ${amt:6.2f}  {(row['title'] or '')[:80]}")
        time.sleep(0.4)

    # detail pass: top by favorites
    rows.sort(key=lambda x: int(x.get("favorites") or 0), reverse=True)
    print("\n=== DETAIL top 12 ===")
    for row in rows[:12]:
        try:
            det = m.make_request("GET", f"/listings/{row['listing_id']}")
            row["description"] = (det.get("description") or "")[:1200]
            row["materials"] = det.get("materials") or []
            row["num_favorers"] = det.get("num_favorers")
            print(f"\n--- {row['listing_id']} fav={row['favorites']} ${row['price']}")
            print(row["title"])
            print((row["description"] or "")[:500].replace("\n", " | "))
            print("tags:", row.get("tags")[:10])
        except Exception as e:
            print("detail fail", row["listing_id"], e)
        time.sleep(0.35)

    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\nwrote", OUT, len(rows))


if __name__ == "__main__":
    main()
