import csv
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).parent / "wave11_erank_bulk.csv", encoding="utf-8")))


def f(x):
    try:
        return float(x) if x not in ("", "None", None) else None
    except Exception:
        return None


print("n", len(rows))
print("=== ALL RANKED ===")
for i, r in enumerate(rows, 1):
    print(
        f"{i:2} sc={r['score']:>5} jun={r['latest_month_searches']:>7} "
        f"avg={r['searches_avg']:>7} mom={r['momentum']:>5} kd={r['kd']:>5} "
        f"c={r['competition']:>10}  {r['keyword']}"
    )

print("\n=== KD < 80 AND jun >= 800 ===")
for r in rows:
    lat, kd = f(r["latest_month_searches"]), f(r["kd"])
    if lat and kd is not None and lat >= 800 and kd < 80:
        print(
            f"  kd={kd:>5} jun={lat:>7} mom={r['momentum']:>5} sc={r['score']:>5}  {r['keyword']}"
        )

print("\n=== RISING mom>=1.2 jun>=500 ===")
for r in rows:
    mom, lat = f(r["momentum"]), f(r["latest_month_searches"])
    if mom and lat and mom >= 1.2 and lat >= 500:
        print(
            f"  mom={mom:>5} jun={lat:>7} kd={r['kd']:>5}  {r['keyword']}"
        )
