"""Inspect Etsy SERP for resume templates."""
import json
import time
import urllib.parse
from pathlib import Path

import etsy_manager

OUT = Path(__file__).parent / "resume_serp.json"
KWS = [
    "resume template",
    "modern resume template",
    "resume template canva",
    "minimalist resume template",
    "ats resume template",
    "professional resume template",
]


def main():
    m = etsy_manager.EtsyManager()
    rows = []
    seen = set()
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
                "url": f"https://www.etsy.com/listing/{lid}",
                "tags": r.get("tags") or [],
                "views": r.get("views"),
            }
            rows.append(row)
            print(f"  fav={row['favorites']:4} ${amt:6.2f} {(row['title'] or '')[:75]}")
        time.sleep(0.35)
    rows.sort(key=lambda x: int(x.get("favorites") or 0), reverse=True)
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", OUT, len(rows))


if __name__ == "__main__":
    main()
