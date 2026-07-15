"""Refine top wave3 niches with cleaner keywords."""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import etsy_manager
from product_finder import analyze_keyword, product_idea

KWS = [
    "graph theory art",
    "network graph art print",
    "data visualization poster",
    "math formula cheat sheet",
    "physics formula sheet",
    "calculus formula poster",
    "stem sticker pack goodnotes",
    "science digital stickers",
    "astronomy wall art printable",
    "solar system wall art digital",
    "classroom math posters set",
    "study flashcards goodnotes",
    "anatomy art print digital",
    "psychology wall art printable",
    "therapy office art science",
    "lab notebook printable",
    "lab notebook digital",
    "student lab notebook",
    "scientific notebook printable",
    "composition notebook printable science",
    "graph paper lab notes",
    "engineering lab notebook",
    "stem classroom posters",
    "math bulletin board set",
    "formula sheet calculus",
    "unit circle poster printable",
    "trig identity poster",
    "fourier transform poster",
    "algorithm poster computer science",
    "big o notation poster",
]


def main():
    m = etsy_manager.EtsyManager()
    rows = []
    for kw in KWS:
        r = analyze_keyword(m, kw, sample=25)
        try:
            r["product_idea"] = product_idea(r)
        except Exception:
            pass
        rows.append(r)
        titles = r.get("sample_titles") or []
        print(
            f"{r['score_total']:5.1f} n={r['listing_count']:5d} "
            f"fav={r['avg_favorites']:6.1f} max={r['max_favorites']:5d} "
            f"dig={r['digital_share']:.0%} | {kw}"
        )
        for t in titles[:3]:
            print(f"    {t[:78]}")
        time.sleep(0.3)

    rows.sort(key=lambda x: -float(x.get("score_total") or 0))
    out = Path(__file__).with_name("wave3_refined.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\n=== TOP ===")
    for r in rows[:12]:
        print(f"{r['score_total']:5.1f} | {r['keyword']} | {r.get('verdict')}")
    print("saved", out)


if __name__ == "__main__":
    main()
