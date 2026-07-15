"""Wave 3 — broader opportunity scan (beyond physics plates)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import etsy_manager
from product_finder import analyze_keyword, product_idea, compute_scores

KWS = [
    "graph theory poster",
    "dna wall art printable",
    "circuit board wall art",
    "periodic table printable",
    "formula sheet printable",
    "teacher gift math",
    "graduation gift engineer",
    "study planner goodnotes",
    "svg geometric pattern",
    "laser cut mandala svg",
    "bookmark printable set",
    "astronomy chart printable",
    "moon phase wall art",
    "constellation map printable",
    "brain anatomy poster",
    "stem classroom poster set",
    "math flashcards printable",
    "goodnotes sticker book",
    "digital sticker science",
    "password tracker printable",
    "habit tracker printable",
    "engineering print blueprint",
    "architect wall art printable",
    "minimal calendar printable",
    "desk wallpaper digital",
    "iphone wallpaper abstract",
    "ipad wallpaper aesthetic",
    "wedding seating chart template",
    "baby milestone card printable",
    "affirmation card science",
    "flashcard template goodnotes",
    "cornell notes template",
    "lab notebook printable",
    "research journal template",
    "math formula poster set",
    "periodic table aesthetic",
    "solar system poster printable",
    "star map printable custom",
    "sound wave art custom",
    "waveform art print",
]

def main():
    manager = etsy_manager.EtsyManager()
    rows = []
    for kw in KWS:
        try:
            r = analyze_keyword(manager, kw, sample=25)
            # ensure scores/verdict
            if "score_total" not in r:
                r = compute_scores(r) if callable(compute_scores) else r
            try:
                r["product_idea"] = product_idea(r)
            except Exception:
                pass
            rows.append(r)
            print(
                f"{float(r.get('score_total') or 0):5.1f} | "
                f"n={int(r.get('listing_count') or 0):5d} "
                f"fav={float(r.get('avg_favorites') or 0):6.1f} "
                f"price={float(r.get('median_price') or 0):6.2f} "
                f"dig={float(r.get('digital_share') or 0):.0%} | {kw}"
            )
        except Exception as e:
            print(f"ERR | {kw} | {e}")
        time.sleep(0.35)

    rows.sort(key=lambda x: -float(x.get("score_total") or 0))
    out = Path(__file__).with_name("wave3_broad_candidates.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\n=== TOP 15 ===")
    for r in rows[:15]:
        print(
            f"{float(r.get('score_total') or 0):5.1f} | {r.get('verdict')} | "
            f"{r.get('keyword')} | idea={str(r.get('product_idea') or '')[:70]}"
        )
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
