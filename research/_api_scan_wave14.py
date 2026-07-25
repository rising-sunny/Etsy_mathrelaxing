"""Etsy API SERP scan for wave14 keywords — competition + favorites proxy."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import etsy_manager  # noqa: E402
import product_finder as pf  # noqa: E402

KEYS = [
    "password tracker",
    "medication tracker",
    "blood pressure log",
    "chore chart for kids",
    "homeschool planner",
    "science fair board",
    "multiplication chart",
    "periodic table poster",
    "dna wall art",
    "molecule wall art",
    "nursing school notes",
    "medical student planner",
    "circuit board art",
    "constellation wall art",
    "calculus cheat sheet",
    "physics formula sheet",
    "math fridge magnet",
    "chatgpt prompts teachers",
    "reading journal",
    "dark academia wall art",
    "canva social media templates",
    "teacher classroom decor",
    "first day of school sign",
    "lab safety poster",
    "fraction wall",
]

m = etsy_manager.EtsyManager()
rows = []
for i, kw in enumerate(KEYS, 1):
    print(f"[{i}/{len(KEYS)}] {kw}…", flush=True)
    try:
        r = pf.analyze_keyword(m, kw, sample=20)
        rows.append(r)
        print(
            f"  n={r.get('count') or r.get('total') or r.get('listings')} "
            f"med$={r.get('median_price') or r.get('med_price')} "
            f"maxfav={r.get('max_favorers') or r.get('max_favs')} "
            f"keys={list(r.keys())[:12]}"
        )
    except Exception as e:
        print("  ERR", e)
        rows.append({"keyword": kw, "error": str(e)[:200]})
    time.sleep(0.35)

out = Path(__file__).parent / "wave14_api_scan.json"
out.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
print("saved", out)
