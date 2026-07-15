"""Wave 4 — fresh niches not yet productized (post lab notebook)."""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import etsy_manager
from product_finder import analyze_keyword, product_idea

# Avoid: lab notebook, physics wall art, molecules, planners generic, habit tracker
KWS = [
    "unit circle poster math",
    "trigonometry poster printable",
    "math formula cheat sheet",
    "calculus formula sheet printable",
    "physics formula sheet printable",
    "ap calculus poster",
    "big o notation cheat sheet",
    "algorithm poster printable",
    "computer science poster set",
    "periodic table aesthetic printable",
    "periodic table wall art digital",
    "solar system chart printable",
    "constellation wall art minimal",
    "anatomy brain poster printable",
    "psychology office wall art",
    "therapy office poster science",
    "math flashcards printable high school",
    "physics flashcards goodnotes",
    "chemistry flashcards digital",
    "stem classroom poster set printable",
    "math bulletin board posters",
    "famous mathematicians posters",
    "engineering graph paper printable pack",
    "isometric paper printable pad",
    "hexagonal paper printable chemistry",
    "cornell notes science printable",
    "meeting notes template stem",
    "research log printable",
    "lab report template printable",
    "scientific method poster classroom",
    "password tracker minimalist printable",
    "reading log printable aesthetic",
    "grade tracker printable teacher",
    "homeschool science planner",
    "student planner stem printable",
    "desk wallpaper math aesthetic",
    "phone wallpaper math formula",
    "procreate stamp set geometric",
    "svg geometric pattern seamless",
    "mandala math coloring page",
]


def main():
    m = etsy_manager.EtsyManager()
    rows = []
    for kw in KWS:
        try:
            r = analyze_keyword(m, kw, sample=25)
            try:
                r["product_idea"] = product_idea(r)
            except Exception:
                pass
            rows.append(r)
            print(
                f"{float(r.get('score_total') or 0):5.1f} | "
                f"n={int(r.get('listing_count') or 0):5d} "
                f"fav={float(r.get('avg_favorites') or 0):6.1f} "
                f"max={int(r.get('max_favorites') or 0):5d} "
                f"dig={float(r.get('digital_share') or 0):.0%} | {kw}"
            )
            for t in (r.get("sample_titles") or [])[:2]:
                print(f"    - {t[:75]}")
        except Exception as e:
            print(f"ERR | {kw} | {e}")
        time.sleep(0.32)

    rows.sort(key=lambda x: -float(x.get("score_total") or 0))
    out = Path(__file__).with_name("wave4_candidates.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\n=== TOP 15 ===")
    for r in rows[:15]:
        print(
            f"{float(r['score_total']):5.1f} | {r.get('verdict')} | {r['keyword']}"
        )
    print("saved", out)


if __name__ == "__main__":
    main()
