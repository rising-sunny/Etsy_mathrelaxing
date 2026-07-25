"""Etsy API competition scan for iPad accessory keywords."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import etsy_manager  # noqa: E402
import product_finder as pf  # noqa: E402

KEYS = [
    "ipad case",
    "ipad pro case",
    "ipad air case",
    "ipad mini case",
    "ipad sleeve",
    "ipad stand",
    "ipad desk stand",
    "ipad keyboard case",
    "apple pencil case",
    "apple pencil grip",
    "ipad screen protector",
    "paperlike screen protector",
    "ipad skin",
    "ipad sticker",
    "ipad decal",
    "custom ipad case",
    "personalized ipad case",
    "leather ipad case",
    "magnetic ipad case",
    "ipad case with pencil holder",
    "ipad bag",
    "ipad pouch",
    "ipad portfolio",
    "drawing glove ipad",
    "artist glove",
    "ipad stand wood",
    "tablet pillow stand",
    "ipad lap desk",
    "procreate accessories",
    "digital planner accessories",
    "remarkable 2 case",
    "kindle paperwhite case",
    "ipad keyboard folio",
    "clear ipad case",
    "kids ipad case",
    "teacher ipad case",
    "ipad organizer",
    "apple pencil tip cover",
    "ipad pen loop",
    "ipad folio leather",
]

m = etsy_manager.EtsyManager()
rows = []
for i, kw in enumerate(KEYS, 1):
    print(f"[{i}/{len(KEYS)}] {kw}…", flush=True)
    try:
        r = pf.analyze_keyword(m, kw, sample=20)
        rows.append(r)
        print(
            f"  n={r.get('listing_count')} maxfav={r.get('max_favorites')} "
            f"avgf={r.get('avg_favorites')} med$={r.get('median_price')} dig={r.get('digital_share')}"
        )
    except Exception as e:
        print("  ERR", e)
        rows.append({"keyword": kw, "error": str(e)[:200]})
    time.sleep(0.3)

out = Path(__file__).parent / "ipad_accessories_api_scan.json"
out.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
print("saved", out)
