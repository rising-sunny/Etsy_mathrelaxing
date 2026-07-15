"""
seo_rewrite_descriptions.py — Enrich Etsy listing descriptions with eRank keywords
================================================================================
Rewrites short/weak active listing descriptions (keeps product meaning, no
external store URLs). Uses high-demand eRank keywords naturally.

  python seo_rewrite_descriptions.py              # dry-run
  python seo_rewrite_descriptions.py --apply
  python seo_rewrite_descriptions.py --limit 15 --apply
  python seo_rewrite_descriptions.py --min-len 900 --apply
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import time
from datetime import datetime, timezone

import etsy_manager
from seo_optimize_listings import categorize, clean_title

OUT = os.path.join(os.path.dirname(__file__), "research")
FULL_CACHE = os.path.join(OUT, "active_listings_full.json")
PLAN = os.path.join(OUT, "seo_descriptions_plan.json")

COPYRIGHT = (
    "© MathRelaxing. For personal use only. Not for redistribution or resale."
)

# eRank high-value phrases to weave in by category
KW = {
    "wall_art": [
        "printable wall art",
        "math wall art",
        "science wall art",
        "digital download",
        "minimalist wall art",
        "math gift",
    ],
    "sacred": [
        "sacred geometry",
        "printable wall art",
        "geometric wall art",
        "digital download",
        "minimalist wall art",
    ],
    "coloring": [
        "adult coloring book",
        "coloring book pdf",
        "math coloring book",
        "printable coloring",
        "digital download",
    ],
    "planner": [
        "digital planner",
        "goodnotes planner",
        "ipad planner",
        "digital download",
        "undated planner",
    ],
    "notebook": [
        "digital notebook",
        "goodnotes notebook",
        "grid paper",
        "digital download",
        "ipad notebook",
    ],
    "animation": [
        "seamless loop",
        "generative art",
        "math animation",
        "digital download",
        "strange attractor",
    ],
    "palette": [
        "procreate palette",
        "procreate swatches",
        "digital download",
        "ipad art",
        "color palette",
    ],
}


def load_listings(manager, refresh=False):
    if not refresh and os.path.exists(FULL_CACHE):
        with open(FULL_CACHE, encoding="utf-8") as f:
            return json.load(f)["listings"]
    sid = manager.get_shop_id()
    rows = []
    offset = 0
    while True:
        data = manager.make_request(
            "GET", f"/shops/{sid}/listings/active?limit=100&offset={offset}"
        )
        for r in data.get("results") or []:
            rows.append(
                {
                    "listing_id": r["listing_id"],
                    "title": html.unescape(r.get("title") or ""),
                    "tags": r.get("tags") or [],
                    "description": r.get("description") or "",
                    "views": r.get("views") or 0,
                }
            )
        if len(rows) >= (data.get("count") or 0) or not data.get("results"):
            break
        offset += 100
        time.sleep(0.25)
    os.makedirs(OUT, exist_ok=True)
    with open(FULL_CACHE, "w", encoding="utf-8") as f:
        json.dump({"count": len(rows), "listings": rows}, f, indent=2, ensure_ascii=False)
    return rows


def topic_from_title(title: str) -> str:
    t = clean_title(title)
    # first segment before |
    head = t.split("|")[0].strip()
    head = re.sub(r"\s+", " ", head)
    return head[:80]


def product_bullets(title: str, cat: str) -> list[str]:
    low = title.lower()
    bullets = []
    if cat == "coloring":
        bullets = [
            "High-resolution printable PDF (instant download)",
            "Original mathematical / geometric line-art designs",
            "Print at home or use on iPad (GoodNotes / Procreate)",
            "Relaxing, screen-optional creative time",
        ]
        if "color by number" in low or "iPad" in title or "svg" in low:
            bullets[0] = "Interactive or printable digital coloring files"
    elif cat == "planner":
        bullets = [
            "Undated digital planner for GoodNotes / Notability / iPad",
            "Hyperlinked sections for fast navigation",
            "Built for focus, research, and real workflows",
            "Instant download — reuse every semester",
        ]
    elif cat == "notebook":
        bullets = [
            "Digital notebook / grid paper for GoodNotes & iPad",
            "Clean STEM-friendly layouts (dot, hex, isometric, Cornell…)",
            "Instant download — print or use digitally",
            "Great for students, engineers, and makers",
        ]
    elif cat == "animation":
        bullets = [
            "Seamless loop mathematical animation (digital download)",
            "Generative / chaos-theory inspired motion art",
            "Use as wallpaper, ambient art, or creative footage",
            "High-quality MP4 loop file",
        ]
    elif cat == "palette":
        bullets = [
            "Procreate color palette / swatches (instant download)",
            "Math-inspired generative color sets",
            "Import into Procreate on iPad",
            "Perfect for digital artists and fractal lovers",
        ]
    else:
        bullets = [
            "High-resolution printable wall art (digital download)",
            "Clean minimalist science / math aesthetic",
            "Print at home or local print shop on matte paper",
            "Ideal for office, classroom, dorm, or gallery wall",
        ]
        if "set of" in low or "bundle" in low:
            bullets[0] = "Multi-print digital set — instant download"
        if "physical" in low or "printed" in low:
            bullets = [
                "Physical printed edition (ships as a real book / product)",
                "Original mathematical designs throughout",
                "Gift-ready for STEM teachers, students, and art lovers",
                "Premium print quality",
            ]
    return bullets


def rewrite_description(listing: dict) -> str:
    title = clean_title(listing["title"])
    cat = categorize(title)
    topic = topic_from_title(title)
    kws = KW.get(cat, KW["wall_art"])
    old = (listing.get("description") or "").strip()

    # Keep a short unique snippet from old desc if useful (first non-empty line)
    old_lines = [ln.strip() for ln in old.splitlines() if ln.strip()]
    keep_bits = []
    for ln in old_lines[:6]:
        if "mathrelaxing.store" in ln.lower():
            continue
        if ln.startswith("©"):
            continue
        if len(ln) > 40 and ln not in keep_bits:
            keep_bits.append(ln)
        if len(keep_bits) >= 2:
            break

    bullets = product_bullets(title, cat)
    kw_line = ", ".join(kws[:5])

    parts = [
        f"Instant download — {topic}.",
        "",
    ]
    if keep_bits:
        parts.append(keep_bits[0])
        parts.append("")
    else:
        # category intro with demand keywords
        if cat in ("wall_art", "sacred"):
            parts.append(
                f"A refined {kws[0]} design for lovers of mathematics, physics, and minimalist decor. "
                f"This {kws[3]} arrives ready to print — perfect {kws[4]} energy for modern spaces."
            )
        elif cat == "coloring":
            parts.append(
                f"An {kws[0]} style digital set with mathematical structure and meditative line work. "
                f"Use as a {kws[1]} at home or color on tablet."
            )
        elif cat == "planner":
            parts.append(
                f"A focused {kws[0]} made for GoodNotes and iPad workflows. "
                f"Stay organized with a clean {kws[1]} experience built for real work."
            )
        elif cat == "notebook":
            parts.append(
                f"A practical {kws[0]} with STEM-friendly grids. "
                f"Use as a {kws[1]} on iPad or print the pages you need."
            )
        elif cat == "animation":
            parts.append(
                f"A {kws[0]} of generative mathematical motion. "
                f"Ambient {kws[1]} for screens, portfolios, and creative projects."
            )
        elif cat == "palette":
            parts.append(
                f"A ready-to-import {kws[0]} for Procreate. "
                f"Math-inspired hues for digital illustration and abstract work."
            )
        parts.append("")

    if len(keep_bits) > 1:
        parts.append(keep_bits[1])
        parts.append("")

    parts.append("► What you get")
    for b in bullets:
        parts.append(f"• {b}")
    parts.append("")
    parts.append("► Perfect for")
    if cat in ("wall_art", "sacred"):
        parts.append(
            "Home office, classroom STEM walls, dorm rooms, therapy / study spaces, "
            "and thoughtful math or science gifts."
        )
    elif cat == "coloring":
        parts.append(
            "Adults who love geometry, mindfulness, STEM teachers, students, and weekend creative time."
        )
    elif cat in ("planner", "notebook"):
        parts.append(
            "Students, researchers, engineers, PhD workflows, and anyone who thinks better on structured pages."
        )
    elif cat == "animation":
        parts.append(
            "Digital art collectors, math lovers, ambient displays, and creators needing seamless generative loops."
        )
    else:
        parts.append("Digital artists, Procreate users, and fans of mathematical color systems.")
    parts.append("")
    parts.append(f"Search-friendly details: {kw_line}.")
    parts.append("")
    parts.append(COPYRIGHT)

    desc = "\n".join(parts)
    # Etsy description limit ~13k
    return desc[:12000]


def needs_rewrite(listing: dict, min_len: int) -> bool:
    d = listing.get("description") or ""
    if len(d) < min_len:
        return True
    if "mathrelaxing.store" in d.lower():
        return True
    # thin / generic
    if d.count("\n") < 4 and len(d) < min_len + 200:
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--min-len", type=int, default=750, help="Rewrite if description shorter than this")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", type=int, nargs="*")
    args = ap.parse_args()

    m = etsy_manager.EtsyManager()
    listings = load_listings(m, refresh=args.refresh)
    if args.only:
        want = set(args.only)
        listings = [r for r in listings if r["listing_id"] in want]

    plans = []
    for r in listings:
        if not needs_rewrite(r, args.min_len) and not args.only:
            continue
        new_d = rewrite_description(r)
        old_d = r.get("description") or ""
        if new_d.strip() == old_d.strip():
            continue
        plans.append(
            {
                "listing_id": r["listing_id"],
                "title": r["title"],
                "category": categorize(r["title"]),
                "old_len": len(old_d),
                "new_len": len(new_d),
                "old_description": old_d,
                "new_description": new_d,
            }
        )

    plans.sort(key=lambda p: p["old_len"])
    if args.limit:
        plans = plans[: args.limit]

    os.makedirs(OUT, exist_ok=True)
    with open(PLAN, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "count": len(plans),
                "plans": plans,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Rewrites planned: {len(plans)}  → {PLAN}")
    for p in plans[:20]:
        print(
            f"  {p['listing_id']}  {p['old_len']:4}→{p['new_len']:4}  "
            f"{p['category']:<10}  {p['title'][:50]}"
        )

    if not args.apply:
        print("\nDry-run only. Use --apply to PATCH descriptions.")
        return

    for p in plans:
        print(f"PATCH description {p['listing_id']}...")
        try:
            m.update_listing(p["listing_id"], description=p["new_description"])
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.45)
    print(f"Done. Updated {len(plans)} descriptions.")


if __name__ == "__main__":
    main()
