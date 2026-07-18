import csv
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).parent / "wave10_erank_bulk.csv", encoding="utf-8")))


def f(x):
    try:
        return float(x) if x not in ("", "None", None) else None
    except Exception:
        return None


print("n", len(rows))
print("=== TOP 30 SCORE ===")
for i, r in enumerate(rows[:30], 1):
    print(
        f"{i:2} sc={r['score']:>5} jun={r['latest_month_searches']:>7} "
        f"avg={r['searches_avg']:>7} mom={r['momentum']:>4} kd={r['kd']:>5} "
        f"c={r['competition']:>10}  {r['keyword']}"
    )

print("\n=== RISING mom>=1.15 AND latest>=800 AND kd<80 ===")
cand = []
for r in rows:
    mom, lat, kd = f(r["momentum"]), f(r["latest_month_searches"]), f(r["kd"])
    if mom and lat and kd is not None and mom >= 1.15 and lat >= 800 and kd < 80:
        cand.append(r)
cand = sorted(cand, key=lambda r: (-f(r["score"]), f(r["kd"]) or 99))
for r in cand:
    print(
        f"  sc={r['score']:>5} jun={r['latest_month_searches']:>7} "
        f"mom={r['momentum']:>4} kd={r['kd']:>5}  {r['keyword']}"
    )

print("\n=== BEST KD among latest>=1000 ===")
hi = [
    r
    for r in rows
    if (f(r["latest_month_searches"]) or 0) >= 1000 and f(r["kd"]) is not None
]
hi = sorted(hi, key=lambda r: f(r["kd"]))
for r in hi[:20]:
    print(
        f"  kd={r['kd']:>5} jun={r['latest_month_searches']:>7} "
        f"mom={r['momentum']:>4} sc={r['score']:>5}  {r['keyword']}"
    )

print("\n=== HIGH VOL + KD<=55 ===")
for r in rows:
    lat, kd = f(r["latest_month_searches"]), f(r["kd"])
    if lat and kd is not None and lat >= 1000 and kd <= 55:
        print(
            f"  kd={kd:>5} jun={lat:>7} mom={r['momentum']}  {r['keyword']}"
        )
