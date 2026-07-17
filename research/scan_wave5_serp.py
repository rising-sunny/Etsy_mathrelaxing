"""Quick SERP peek for wave5 shortlist."""
from __future__ import annotations

import time
import urllib.parse

import etsy_manager

KWS = [
    "unit circle",
    "unit circle poster",
    "math stickers",
    "science stickers",
    "math teacher gift",
    "golden ratio",
    "math mouse pad",
    "formula sheet",
    "trigonometry poster",
]


def main():
    m = etsy_manager.EtsyManager()
    for kw in KWS:
        q = urllib.parse.quote_plus(kw)
        d = m.make_request("GET", f"/listings/active?keywords={q}&limit=8&offset=0")
        print("===", kw, "count", d.get("count"))
        for r in (d.get("results") or [])[:5]:
            p = r.get("price") or {}
            amt = (p.get("amount") or 0) / (p.get("divisor") or 100)
            title = (r.get("title") or "")[:72]
            print(
                f"  fav={r.get('num_favorers'):4d} dig={r.get('is_digital')} "
                f"${amt:6.2f} {title}"
            )
        time.sleep(0.3)


if __name__ == "__main__":
    main()
