"""Append shipping/production blurb to all Printify product descriptions and republish."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import printify_publish as pp

MARKER_START = "—— SHIPPING & PRODUCTION ——"
MARKER_END = "—— END SHIPPING ——"

BLURB_POSTER = f"""
{MARKER_START}
Made to order (print on demand).

• Production / processing: about 7–10 business days after your order
• Shipping after production:
  – United States: about 2–5 business days in transit
  – Canada & international: about 10–30 business days in transit (customs may add time)

US orders typically arrive in about 1–2 weeks total; international often 3–5+ weeks.
Tracking is provided when the print partner ships. Frame not included.
{MARKER_END}
""".strip()

BLURB_MAGNET = f"""
{MARKER_START}
Made to order (print on demand).

• Production / processing: about 7–10 business days after your order
• Shipping after production:
  – United States: about 2–5 business days in transit
  – International: about 10–30 business days in transit (customs may add time)

Tracking is provided when the print partner ships.
{MARKER_END}
""".strip()


def upsert(desc: str, blurb: str) -> str:
    desc = desc or ""
    if MARKER_START in desc and MARKER_END in desc:
        return re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            blurb,
            desc,
            flags=re.DOTALL,
        ).strip()
    return (desc.rstrip() + "\n\n" + blurb).strip()


def main():
    listing = pp._req("GET", f"/shops/{pp.SHOP_ID}/products.json?limit=50")
    items = listing.get("data") or []
    print(f"products={len(items)}")
    results = []
    for p in items:
        pid = p["id"]
        title = (p.get("title") or "")[:55]
        bp = p.get("blueprint_id")
        blurb = BLURB_MAGNET if bp == 428 else BLURB_POSTER
        new_desc = upsert(p.get("description") or "", blurb)

        # keep variants as-is
        variants = [
            {
                "id": v["id"],
                "price": v["price"],
                "is_enabled": bool(v.get("is_enabled")),
            }
            for v in (p.get("variants") or [])
        ]
        # preserve print areas
        print_areas = []
        for pa in p.get("print_areas") or []:
            print_areas.append(
                {
                    "variant_ids": pa.get("variant_ids"),
                    "placeholders": pa.get("placeholders"),
                }
            )

        payload = {
            "title": p.get("title"),
            "description": new_desc,
            "tags": p.get("tags") or [],
            "variants": variants,
            "print_areas": print_areas,
        }
        try:
            pp._req("PUT", f"/shops/{pp.SHOP_ID}/products/{pid}.json", payload)
            # only republish if already on Etsy
            ext = p.get("external") or {}
            if ext.get("id"):
                pp.publish_product(pid)
                action = "updated+published"
            else:
                action = "updated_not_on_etsy"
            print(f"  OK {action}  {title}")
            results.append({"id": pid, "ok": True, "action": action, "title": title})
        except Exception as e:
            print(f"  FAIL {title}: {e}")
            results.append({"id": pid, "ok": False, "error": str(e)[:300], "title": title})
        time.sleep(0.4)

    ok = sum(1 for r in results if r.get("ok"))
    print(f"DONE {ok}/{len(results)}")
    Path("_printify_shipping_copy_report.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
