"""Wave 5 — next winners after CS set (digital + physical OK)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import etsy_manager
from product_finder import analyze_keyword, product_idea

# Exclude: CS posters, lab notebook, Schrödinger/physics plates, happy chemicals,
# generic planners, habit trackers, saturated coloring books.
KWS = [
    # classroom / study (runners-up still open)
    "unit circle poster",
    "unit circle wall art",
    "trigonometry reference poster",
    "math formula cheat sheet printable",
    "calculus cheat sheet printable",
    "physics formula sheet printable",
    "ap calculus reference sheet",
    "math flashcards printable",
    "stem flashcards digital",
    # physical / POD-friendly wall art
    "math poster physical print",
    "science wall art print physical",
    "physics equation poster print",
    "circuit board wall art",
    "dna helix wall art print",
    "golden ratio wall art print",
    "fibonacci spiral wall art",
    "strange attractor wall art",
    "lorenz attractor print",
    "fractal wall art print",
    "mandelbrot set wall art",
    "constellation star map print",
    "moon phase wall art print",
    # desk / stationery physical-ish
    "mouse pad math aesthetic",
    "desk mat geometric",
    "math sticker sheet vinyl",
    "laptop sticker math pack",
    "science pin enamel badge",
    "math enamel pin",
    # books / journals (Lulu path)
    "math coloring book hardcover",
    "sacred geometry book gift",
    "adult coloring book geometric hardcover",
    "science gift book illustrated",
    "mathematician gift book",
    # classroom bundles
    "math bulletin board set",
    "stem classroom decor set",
    "back to school math posters",
    "homeschool math posters",
    "engineering classroom poster",
    # niche digital still open
    "big o notation poster",
    "data structures poster",
    "machine learning poster",
    "neural network wall art",
    "quantum physics poster printable",
    "periodic table aesthetic print",
    "solar system educational poster",
    "brain anatomy aesthetic poster",
    "psychology office decor science",
    "therapist office wall art science",
]


def main():
    out = Path(__file__).parent / "wave5_candidates.json"
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
            dig = float(r.get("digital_share") or 0)
            print(
                f"{float(r.get('score_total') or 0):5.1f} | "
                f"n={int(r.get('listing_count') or 0):5d} "
                f"fav={float(r.get('avg_favorites') or 0):6.1f} "
                f"max={int(r.get('max_favorites') or 0):5d} "
                f"dig={dig:.0%} "
                f"${float(r.get('median_price') or 0):5.2f} | {kw}"
            )
            for t in (r.get("sample_titles") or [])[:2]:
                print(f"    - {t[:78]}")
        except Exception as e:
            print(f"ERR | {kw} | {e}")
        time.sleep(0.32)

    rows.sort(key=lambda x: float(x.get("score_total") or 0), reverse=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {out} ({len(rows)} keywords)")
    print("\n=== TOP 12 by Etsy score ===")
    for r in rows[:12]:
        print(
            f"  {float(r.get('score_total') or 0):5.1f}  "
            f"n={int(r.get('listing_count') or 0):5d}  "
            f"fav~{float(r.get('avg_favorites') or 0):5.0f}  "
            f"dig={float(r.get('digital_share') or 0):.0%}  | {r.get('keyword')}"
        )


if __name__ == "__main__":
    main()
