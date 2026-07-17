"""
Wave 8 — broad product scan (not limited to math / digital-only).
Uses product_finder Etsy sampling + optional eRank CSV if present.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import product_finder as pf  # noqa: E402

OUT = Path(__file__).resolve().parent

KEYWORDS = [
    # Career / business
    "resume template",
    "invoice template",
    "price list template",
    "business card template",
    "proposal template",
    "letter of recommendation template",
    "freelance contract template",
    # Wedding / events
    "wedding seating chart",
    "wedding table numbers",
    "bridal shower game",
    "wedding timeline template",
    "baby shower invitation",
    "baby milestone cards",
    "gender reveal invitation",
    # Home / life printables
    "chore chart for kids",
    "homeschool planner",
    "meal planner printable",
    "budget planner printable",
    "habit tracker printable",
    "cleaning schedule printable",
    "medication tracker printable",
    "password book printable",
    # Wall art / home (POD OK)
    "nursery wall art",
    "bathroom wall art",
    "kitchen wall art",
    "office wall art",
    "affirmation wall art",
    "welcome sign wedding",
    "custom name sign",
    # Apparel / POD
    "teacher sweatshirt",
    "bookish sweatshirt",
    "dog mom shirt",
    "nurse tote bag",
    # Stickers / merch
    "kindle stickers",
    "laptop stickers funny",
    "water bottle stickers",
    # Journals
    "gratitude journal",
    "wine tasting journal",
    "reading journal printable",
    # Tools
    "procreate brushes",
    "canva template bundle",
    "etsy seller planner",
    # Health
    "blood pressure log",
    "symptom tracker printable",
    "medication log book",
    # Kids
    "reward chart kids",
    "potty training chart",
    # Blue ocean / practical
    "first aid kit printable",
    "emergency binder printable",
    "moving checklist printable",
    "apartment emergency kit",
    # Physical home
    "funny doormat",
    "monogram doormat",
    "wall key holder",
    # STEM-adjacent keep a few for comparison
    "unit circle poster",
    "periodic table poster",
    "lab notebook printable",
]


def main():
    erank = None
    for cand in [
        OUT / "erank_bulk_wave1.csv",
        OUT / "erank_bulk_seo_keywords.csv",
    ]:
        if cand.is_file():
            erank = str(cand)
            print(f"Merging eRank CSV: {cand.name}")
            break

    print(f"Scanning {len(KEYWORDS)} keywords (Etsy sample)…")
    rows = pf.run(KEYWORDS, erank, sample=10, sleep=0.4)

    # Prefer score_total if present
    def score(r):
        return float(r.get("score_total") or r.get("score") or 0)

    rows_sorted = sorted(rows, key=score, reverse=True)

    json_path = OUT / "wave8_candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows_sorted, f, indent=2, ensure_ascii=False)

    csv_path = OUT / "wave8_candidates.csv"
    fields = [
        "keyword",
        "score_total",
        "score",
        "avg_favorites",
        "listing_count",
        "median_price",
        "erank_searches",
        "erank_kd",
        "erank_competition",
        "product_idea",
        "notes",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows_sorted:
            w.writerow(r)

    print("\n=== TOP 20 by score ===")
    for r in rows_sorted[:20]:
        sc = score(r)
        fav = r.get("avg_favorites") or 0
        n = r.get("listing_count") or 0
        price = r.get("median_price") or 0
        es = r.get("erank_searches")
        kd = r.get("erank_kd")
        er = f" eRank s={es} KD={kd}" if es is not None else ""
        print(f"{sc:5.1f}  fav={fav:6.0f}  n={n:6}  ${price:5.1f}  {r.get('keyword')}{er}")

    print(f"\nWrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
