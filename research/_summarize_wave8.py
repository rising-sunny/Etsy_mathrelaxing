import csv
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).parent / "wave8_erank_bulk.csv", encoding="utf-8")))


def f(x):
    try:
        return float(x) if x not in ("", "None", None) else None
    except Exception:
        return None


print("=== GO (s>=200, KD<=55, comp<50k) ===")
for r in rows:
    s, kd, c = f(r["searches"]), f(r["kd"]), f(r["competition"])
    if s and s >= 200 and (kd is None or kd <= 55) and (c is None or c < 50000):
        print(f"  {r['score']:>5} s={s:>7.0f} kd={kd} c={c:>8.0f}  {r['keyword']}")

print("\n=== High volume hard (s>=2000, kd>=70) ===")
for r in rows:
    s, kd, c = f(r["searches"]), f(r["kd"]), f(r["competition"])
    if s and s >= 2000 and kd and kd >= 70:
        print(f"  {r['score']:>5} s={s:>7.0f} kd={kd} c={c}  {r['keyword']}")

print("\n=== Blue-ish (comp<5000, s>=100) ===")
for r in rows:
    s, kd, c = f(r["searches"]), f(r["kd"]), f(r["competition"])
    if s and s >= 100 and c and c < 5000:
        print(f"  {r['score']:>5} s={s:>7.0f} kd={kd} c={c:>7.0f}  {r['keyword']}")

print("\n=== All sorted ===")
for r in rows:
    print(
        f"  {r['score']:>5} s={r['searches']:>8} kd={r['kd']:>6} c={r['competition']:>10}  {r['keyword']}"
    )
