"""Fetch top Etsy listings for STEM wall-art validation (Tier A)."""
import json
import time
import urllib.parse

import etsy_manager

KEYWORDS = [
    "molecule wall art printable",
    "dna art print digital",
    "physics wall art printable",
    "happiness hormones poster",
    "dopamine serotonin art print",
    "science wall art printable",
]


def main():
    m = etsy_manager.EtsyManager()
    out = {}
    for kw in KEYWORDS:
        q = urllib.parse.quote_plus(kw)
        data = m.make_request(
            "GET",
            f"/listings/active?keywords={q}&limit=20&sort_on=score",
        )
        rows = []
        for r in data.get("results") or []:
            price = r.get("price") or {}
            amt = price.get("amount")
            div = price.get("divisor") or 100
            p = (amt / div) if amt is not None else None
            lid = r.get("listing_id")
            rows.append(
                {
                    "listing_id": lid,
                    "title": (r.get("title") or "")[:140],
                    "price": p,
                    "num_favorers": r.get("num_favorers"),
                    "url": r.get("url") or f"https://www.etsy.com/listing/{lid}",
                    "tags": r.get("tags") or [],
                    "materials": r.get("materials") or [],
                    "is_digital": bool(
                        r.get("is_digital") or r.get("listing_type") == "download"
                    ),
                    "shop_id": r.get("shop_id"),
                    "creation_timestamp": r.get("original_creation_timestamp")
                    or r.get("create_timestamp"),
                    "num_favorers": r.get("num_favorers"),
                    "views": r.get("views"),
                    "taxonomy_id": r.get("taxonomy_id"),
                    "who_made": r.get("who_made"),
                    "when_made": r.get("when_made"),
                }
            )
        out[kw] = {"count": data.get("count"), "top": rows}
        print(f"{kw}: count={data.get('count')} sample={len(rows)}")
        if rows:
            top = max(rows, key=lambda x: x.get("num_favorers") or 0)
            print(f"  max_fav={top['num_favorers']} | {top['title'][:70]}")
        time.sleep(0.35)

    path = "research/validation_raw_etsy.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"saved {path}")


if __name__ == "__main__":
    main()
