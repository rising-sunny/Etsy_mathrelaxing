"""Inspect Etsy SERP for unit circle design research."""
from __future__ import annotations

import json
import time
import urllib.parse
from pathlib import Path

import etsy_manager

OUT = Path(__file__).parent / "unit_circle_serp.json"

KWS = [
    "unit circle poster",
    "unit circle chart",
    "unit circle printable",
    "unit circle",
    "trigonometry unit circle",
]


def main():
    m = etsy_manager.EtsyManager()
    all_rows = []
    seen = set()
    for kw in KWS:
        q = urllib.parse.quote_plus(kw)
        d = m.make_request(
            "GET",
            f"/listings/active?keywords={q}&limit=15&offset=0&sort_on=score",
        )
        print("===", kw, "count", d.get("count"))
        for r in d.get("results") or []:
            lid = r.get("listing_id")
            if lid in seen:
                continue
            # filter obvious non-math
            title = (r.get("title") or "").lower()
            if any(
                x in title
                for x in (
                    "dress",
                    "shirt",
                    "weather",
                    "circle time",
                    "tape case",
                    "jump ring",
                    "montessori",
                    "wish novel",
                )
            ):
                continue
            p = r.get("price") or {}
            amt = (p.get("amount") or 0) / (p.get("divisor") or 100)
            row = {
                "keyword": kw,
                "listing_id": lid,
                "favorites": r.get("num_favorers"),
                "is_digital": r.get("is_digital"),
                "price": amt,
                "currency": (p.get("currency_code") or "USD"),
                "title": r.get("title"),
                "url": f"https://www.etsy.com/listing/{lid}",
                "tags": r.get("tags") or [],
                "views": r.get("views"),
                "num_favorers": r.get("num_favorers"),
            }
            seen.add(lid)
            all_rows.append(row)
            print(
                f"  fav={row['favorites']:4} dig={row['is_digital']} "
                f"${amt:6.2f} {(row['title'] or '')[:75]}"
            )
        time.sleep(0.35)

    # sort by favorites
    all_rows.sort(key=lambda x: int(x.get("favorites") or 0), reverse=True)
    OUT.write_text(json.dumps(all_rows, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT} ({len(all_rows)} unique filtered listings)")


if __name__ == "__main__":
    main()
