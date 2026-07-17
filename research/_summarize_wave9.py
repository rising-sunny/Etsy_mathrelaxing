import csv
import shutil
from pathlib import Path

src = Path(__file__).parent / "wave8_erank_bulk.csv"
dst = Path(__file__).parent / "wave9_art_decor_erank.csv"
shutil.copy(src, dst)
shutil.copy(
    Path(__file__).parent / "wave8_erank_bulk.json",
    Path(__file__).parent / "wave9_art_decor_erank.json",
)
rows = list(csv.DictReader(open(dst, encoding="utf-8")))


def f(x):
    try:
        return float(x) if x not in ("", "None", None) else None
    except Exception:
        return None


print("n", len(rows))
print("=== top by score ===")
for r in rows[:25]:
    print(
        f"{r['score']:>5} latest={r['latest_month_searches']:>7} avg={r['searches_avg']:>7} "
        f"mom={r['momentum']:>4} kd={r['kd']:>5} c={r['competition']:>10}  {r['keyword']}"
    )

print("\n=== KD < 90 ===")
for r in sorted(rows, key=lambda x: f(x["kd"]) or 999):
    kd = f(r["kd"])
    if kd is not None and kd < 90:
        print(
            f"  kd={kd} latest={r['latest_month_searches']} mom={r['momentum']}  {r['keyword']}"
        )

print("\n=== rising mom>=1.2 latest>=800 ===")
for r in rows:
    mom, lat, kd = f(r["momentum"]), f(r["latest_month_searches"]), f(r["kd"])
    if mom and lat and mom >= 1.2 and lat >= 800:
        print(f"  mom={mom} latest={lat:.0f} kd={kd} c={r['competition']}  {r['keyword']}")
