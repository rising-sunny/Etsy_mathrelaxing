"""SERP peek for wave6 shortlist."""
import time
import urllib.parse

import etsy_manager

KWS = [
    "biology poster",
    "cell biology poster",
    "periodic table wall art",
    "periodic table printable",
    "calculus poster",
    "math stickers",
]


def main():
    m = etsy_manager.EtsyManager()
    for kw in KWS:
        q = urllib.parse.quote_plus(kw)
        d = m.make_request("GET", f"/listings/active?keywords={q}&limit=6&offset=0")
        print("===", kw, "count", d.get("count"))
        for r in d.get("results") or []:
            p = r.get("price") or {}
            amt = (p.get("amount") or 0) / (p.get("divisor") or 100)
            title = (r.get("title") or "")[:70]
            print(f"  fav={r.get('num_favorers'):4d} ${amt:6.2f} {title}")
        time.sleep(0.35)


if __name__ == "__main__":
    main()
