import json
from pathlib import Path

BASE = Path(__file__).parent
api = json.loads((BASE / "wave14_api_scan.json").read_text(encoding="utf-8"))
er = json.loads((BASE / "wave14_erank_bulk.json").read_text(encoding="utf-8"))

print("=== API by max_favorites ===")
for r in sorted(api, key=lambda x: -(x.get("max_favorites") or 0)):
    print(
        f"fav={r.get('max_favorites'):5} avgf={r.get('avg_favorites') or 0:6.1f} "
        f"n={r.get('listing_count'):6} med$={r.get('median_price') or 0:6.2f} "
        f"dig={r.get('digital_share')}  {r.get('keyword')}"
    )

print("\n=== eRank ===")
for r in er:
    print(
        f"latest={r.get('latest_month_searches')} avg={r.get('searches')} "
        f"mom={r.get('momentum')} kd={r.get('kd')} comp={r.get('competition')}  "
        f"{r.get('keyword')}"
    )
