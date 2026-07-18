"""Inventory active Etsy listings not yet seeded to the web store."""
import json
import re
from pathlib import Path

LIVE = Path(__file__).with_name("_live_listings.json")
with open(LIVE, encoding="utf-8") as f:
    active = [x for x in json.load(f) if x["state"] == "active"]

# Already published to mathrelaxing.store (batches 1–2 + earlier seeds)
DONE = re.compile(
    r"""(?ix)
    happy\s+chemicals|computer\s+science\s+poster|unit\s+circle\s+poster|
    schr.?dinger|lab\s+notebook\s+printable|stem\s+digital\s+notebook|
    julia\s+set|voronoi\s+cell\s+garden|thomas\s+attractor|
    fractal\s+flora|sacred\s+geometry|voronoi\s+gardens|celtic\s+knot|
    spiral\s+tilings|neural\s+network|chladni\s+figures\s+poster|
    r.?ssler|harmonograph\s+art\s+print|vector\s+field\s+art\s+print|
    set\s+of\s+8\s+physics\s+calculus|procreate\s+fractal|
    chaos\s+theory\s+procreate|interactive\s+geometric|
    interactive\s+math\s+mandala|interactive\s+sacred|
    quantified\s+self|stem\s+focus\s+planner|ats\s+resume|
    luxury\s+resume|letter\s+of\s+recommendation|emergency\s+binder|
    hyperbolic\s+gardens\s+coloring\s+book|printed\s+edition|
    printed\s+physical|islamic\s+star
    """
)

remaining = []
for x in active:
    t = x["title"].replace("&#39;", "'")
    if DONE.search(t):
        continue
    remaining.append({**x, "title": t})

print(f"ACTIVE remaining (not yet on web match): {len(remaining)}\n")
for x in sorted(remaining, key=lambda z: (-z["price"], z["title"])):
    print(f"  ${x['price']:.2f} | {x['listing_id']} | {x['title'][:90]}")

out = Path(__file__).with_name("_batch3_remaining.json")
out.write_text(json.dumps(remaining, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nWrote {out}")
