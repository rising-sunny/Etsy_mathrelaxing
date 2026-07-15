"""
seo_optimize_listings.py — Batch SEO for MathRelaxing active listings
=====================================================================
Uses Etsy API listing data + eRank-informed keyword banks to improve
titles and tags (max 13 tags, each ≤20 chars; title ≤140).

  python seo_optimize_listings.py              # dry-run report
  python seo_optimize_listings.py --apply      # PATCH titles/tags via API
  python seo_optimize_listings.py --only 4533140321 --apply
  python seo_optimize_listings.py --min-score 0 --limit 20 --apply

Does NOT change prices, images, or files. Always keeps personal-use tone.
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

OUT = os.path.join(os.path.dirname(__file__), "research")
ACTIVE_CACHE = os.path.join(OUT, "active_listings.json")
PLAN_PATH = os.path.join(OUT, "seo_plan.json")
REPORT_PATH = os.path.join(OUT, "seo_report.md")

# eRank-informed + shop-fit keyword banks (all ≤20 chars when used as tags)
# High-demand parents from eRank research sessions + listing context
BANK = {
    "wall_art": [
        "math wall art", "math poster", "science wall art", "physics wall art",
        "printable wall art", "stem wall art", "math art print", "science poster",
        "math gift", "minimalist poster", "digital download", "generative art",
        "dark academia print", "office wall art", "dorm wall art",
    ],
    "coloring": [
        "adult coloring book", "coloring book pdf", "math coloring book",
        "printable coloring", "geometric coloring", "mindful coloring",
        "digital download", "mandala coloring", "fractal coloring",
        "sacred geometry", "relaxing coloring", "coloring pages",
        "stem gift", "teacher gift",
    ],
    "planner": [
        "digital planner", "goodnotes planner", "ipad planner",
        "undated planner", "digital download", "notability planner",
        "student planner", "stem planner", "habit tracker",
        "hyperlinked planner", "academic planner", "phd planner",
    ],
    "notebook": [
        "digital notebook", "goodnotes notebook", "grid paper",
        "digital download", "ipad notebook", "dot grid notebook",
        "cornell notes", "hexagonal paper", "stem notebook",
    ],
    "animation": [
        "seamless loop", "math animation", "generative art",
        "digital download", "abstract loop", "strange attractor",
        "math art video", "chaos theory art", "motion art",
        "fractal wallpaper", "stem art gift",
    ],
    "palette": [
        "procreate palette", "procreate swatches", "color palette",
        "digital download", "ipad art", "math art", "artist gift",
        "generative art", "abstract palette", "color swatches",
    ],
    "sacred": [
        "sacred geometry", "flower of life", "geometric wall art",
        "printable wall art", "math wall art", "line art print",
        "minimalist poster", "digital download", "mandala wall art",
    ],
}

# Superstar-style primary phrases to push front of title when missing
PRIMARY_HINTS = [
    (r"coloring book|color by number|coloring pages", "adult coloring book"),
    (r"goodnotes|digital planner|habit tracker|dissertation|phd", "digital planner"),
    (r"digital notebook|grid paper|cornell|hexagonal|isometric", "digital notebook"),
    (r"procreate|swatches|palette", "procreate palette"),
    (r"seamless loop|animation|attractor loop|mp4|60fps|30fps", "seamless loop"),
    (r"sacred geometry|flower of life|metatron", "sacred geometry"),
    (r"physics|chladni|fourier|maxwell|black hole", "physics wall art"),
    (r"math poster|math print|wall art|art print|poster", "math wall art"),
]


def categorize(title: str) -> str:
    t = title.lower()
    if re.search(r"procreate|swatches|palette", t):
        return "palette"
    if re.search(r"seamless loop|animation|60fps|30fps|mp4|attractor loop", t):
        return "animation"
    if re.search(r"goodnotes|planner|habit|dissertation|phd|thesis", t):
        return "planner"
    if re.search(r"notebook|grid paper|cornell|dot grid", t):
        return "notebook"
    if re.search(r"coloring|color by number", t):
        return "coloring"
    if re.search(r"sacred geometry|flower of life|girih|penrose|truchet|sierpinski", t):
        return "sacred"
    return "wall_art"


def clean_title(title: str) -> str:
    t = html.unescape(title or "")
    t = t.replace("\u2014", " - ").replace("\u2013", " - ")
    t = re.sub(r"\s+", " ", t).strip()
    # normalize separators
    t = re.sub(r"\s*\|\s*", " | ", t)
    return t


def clip_title(title: str, limit: int = 140) -> str:
    if len(title) <= limit:
        return title
    # cut at last space before limit
    cut = title[: limit - 1].rsplit(" ", 1)[0]
    return cut.strip(" |,-")


def tagify(s: str) -> str | None:
    s = re.sub(r"\s+", " ", (s or "").strip().lower())
    s = s.replace("—", " ").replace("–", "-")
    if not s or len(s) > 20:
        return None
    # Etsy disallows some punctuation in tags; keep simple
    if re.search(r"[^a-z0-9 &\-']", s):
        s = re.sub(r"[^a-z0-9 &\-']", "", s).strip()
    if not s or len(s) > 20:
        return None
    return s


def extract_topic_tags(title: str) -> list[str]:
    """Pull meaningful multi-word chunks from title for tags."""
    t = clean_title(title).lower()
    # drop noise
    for noise in [
        "digital download", "printable", "pdf download", "physical edition",
        "printed edition", "seamless loop animation",
    ]:
        t = t.replace(noise, " ")
    parts = re.split(r"[|,\-/]+", t)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        # take 2-3 word phrases
        words = [w for w in p.split() if w not in {"a", "the", "of", "and", "for", "with", "set"}]
        if 1 <= len(words) <= 3:
            cand = " ".join(words)
            tg = tagify(cand)
            if tg:
                out.append(tg)
        if len(words) > 3:
            for i in range(len(words) - 1):
                for n in (2, 3):
                    if i + n <= len(words):
                        tg = tagify(" ".join(words[i : i + n]))
                        if tg:
                            out.append(tg)
    return out


def improve_title(title: str, cat: str) -> str:
    t = clean_title(html.unescape(title))
    t = t.replace("&#39;", "'")
    is_physical = bool(re.search(r"printed|physical edition|perfect bound", t, re.I))
    low = t.lower()

    # Prefer pipe separators
    t = re.sub(r"\s+-\s+", " | ", t)
    t = re.sub(r"(\s*\|\s*){2,}", " | ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" |")

    # Front-load category superstar when title starts with weak/buried keyword
    front_map = {
        "palette": "Procreate Color Palette",
        "animation": "Seamless Loop",
        "planner": "Digital Planner",
        "notebook": "Digital Notebook",
        "coloring": None,
        "sacred": None,
        "wall_art": None,
    }
    prefix = front_map.get(cat)
    if prefix:
        # only if not already front-loaded
        head40 = low[:45]
        already = (
            prefix.lower() in head40
            or (cat == "animation" and ("seamless loop" in head40 or low.startswith("seamless")))
            or (cat == "planner" and low.startswith("digital planner"))
            or (cat == "notebook" and ("digital notebook" in head40 or "grid paper" in head40))
            or (cat == "palette" and "procreate" in head40)
        )
        if not already:
            t = f"{prefix} | {t}"
            low = t.lower()

    # Wall art: ensure searchable head terms
    if cat == "wall_art":
        if re.search(r"equation|calculus|physics|attractor|fractal|fourier|maxwell|ulam|euler|golden ratio", low):
            if not re.search(r"^(math|physics|science|stem)\b", low):
                if re.search(r"physics|black hole|chladni|fourier|maxwell|vibrating|wave", low):
                    head = "Physics Wall Art"
                else:
                    head = "Math Wall Art"
                if head.lower() not in low[:55]:
                    t = f"{head} | {t}"
                    low = t.lower()

    # Dedupe accidental "Seamless Seamless" / repeated prefix
    t = re.sub(r"(?i)\b(seamless\s+)+", "Seamless ", t)
    t = re.sub(r"(?i)^(Seamless Loop)\s*\|\s*Seamless Loop\b", r"\1", t)
    t = re.sub(r"(?i)^(Digital Planner)\s*\|\s*Digital Planner\b", r"\1", t)
    t = re.sub(r"(?i)^(Digital Notebook)\s*\|\s*Digital Notebook\b", r"\1", t)
    t = re.sub(r"(?i)^(Math Wall Art)\s*\|\s*Math Wall Art\b", r"\1", t)
    t = re.sub(r"(?i)^(Physics Wall Art)\s*\|\s*Physics Wall Art\b", r"\1", t)

    # Format token for digital products
    if not is_physical:
        if not re.search(
            r"digital download|pdf|goodnotes|ipad|printable|mp4|seamless loop|swatches|procreate",
            t,
            re.I,
        ):
            if len(t) + 22 <= 140:
                t = f"{t} | Digital Download"

    t = re.sub(r"(\s*\|\s*){2,}", " | ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" |")
    return clip_title(t, 140)


def build_tags(title: str, old_tags: list[str], cat: str) -> list[str]:
    bank = BANK.get(cat, BANK["wall_art"])
    candidates: list[str] = []

    # 1) keep good existing tags
    for t in old_tags:
        tg = tagify(t)
        if tg:
            candidates.append(tg)

    # 2) topic from title
    candidates.extend(extract_topic_tags(title))

    # 3) category bank
    candidates.extend(bank)

    # 4) always useful digital cues by category
    if cat == "coloring":
        candidates += ["adult coloring book", "coloring book pdf", "math coloring book"]
    if cat in ("wall_art", "sacred"):
        candidates += ["math wall art", "printable wall art", "digital download"]
    if cat == "animation":
        candidates += ["seamless loop", "generative art"]

    # de-dupe preserve order, enforce 13
    seen = set()
    final = []
    for c in candidates:
        tg = tagify(c)
        if not tg or tg in seen:
            continue
        # avoid near-duplicates (same first two words)
        key = " ".join(tg.split()[:2])
        if any(" ".join(x.split()[:2]) == key and x != tg for x in final):
            # allow if both short and distinct
            if len(tg.split()) == 1:
                pass
            else:
                continue
        seen.add(tg)
        final.append(tg)
        if len(final) >= 13:
            break

    return final[:13]


def score_listing(title: str, tags: list[str]) -> dict:
    """Heuristic SEO health 0-100 (aligned with eRank-ish visibility ideas)."""
    t = clean_title(title)
    low = t.lower()
    score = 50
    notes = []

    # title length
    if 50 <= len(t) <= 130:
        score += 10
    elif len(t) < 40:
        score -= 15
        notes.append("title too short")
    elif len(t) > 140:
        score -= 10
        notes.append("title too long")

    # keyword early
    if re.search(r"^(math|physics|science|digital|adult|sacred|fractal|seamless|procreate|stem|grid)", low):
        score += 8
    else:
        notes.append("primary keyword not front-loaded")

    # format clarity
    if re.search(r"digital download|printable|pdf|goodnotes|ipad|loop|swatches|printed", low):
        score += 8
    else:
        score -= 8
        notes.append("missing format keyword")

    # tags
    n = len(tags)
    if n == 13:
        score += 15
    elif n >= 10:
        score += 8
        notes.append(f"only {n}/13 tags")
    elif n == 0:
        score -= 30
        notes.append("NO TAGS")
    else:
        score -= 10
        notes.append(f"only {n}/13 tags")

    multi = sum(1 for x in tags if " " in x)
    if multi >= 8:
        score += 8
    elif multi < 5 and n:
        notes.append("prefer multi-word tags")

    long_tags = [x for x in tags if len(x) > 20]
    if long_tags:
        score -= 10
        notes.append("tags >20 chars")

    if "&#" in title:
        score -= 5
        notes.append("HTML entities in title")

    return {"score": max(0, min(100, score)), "notes": notes}


def fetch_active(manager: etsy_manager.EtsyManager, refresh: bool = False) -> list[dict]:
    if not refresh and os.path.exists(ACTIVE_CACHE):
        with open(ACTIVE_CACHE, encoding="utf-8") as f:
            return json.load(f)["listings"]

    sid = manager.get_shop_id()
    all_rows = []
    offset = 0
    while True:
        data = manager.make_request(
            "GET", f"/shops/{sid}/listings/active?limit=100&offset={offset}"
        )
        results = data.get("results") or []
        count = data.get("count", 0)
        for r in results:
            all_rows.append(
                {
                    "listing_id": r["listing_id"],
                    "title": r.get("title") or "",
                    "tags": r.get("tags") or [],
                    "views": r.get("views"),
                    "num_favorers": r.get("num_favorers"),
                    "url": r.get("url"),
                    "taxonomy_id": r.get("taxonomy_id"),
                }
            )
        if not results or len(all_rows) >= count:
            break
        offset += 100
        time.sleep(0.25)
    os.makedirs(OUT, exist_ok=True)
    with open(ACTIVE_CACHE, "w", encoding="utf-8") as f:
        json.dump({"count": len(all_rows), "listings": all_rows}, f, indent=2, ensure_ascii=False)
    return all_rows


def plan_for(listing: dict) -> dict:
    old_title = listing.get("title") or ""
    old_tags = listing.get("tags") or []
    cat = categorize(old_title)
    new_title = improve_title(old_title, cat)
    new_tags = build_tags(new_title, old_tags, cat)
    old_score = score_listing(old_title, old_tags)
    new_score = score_listing(new_title, new_tags)

    title_changed = clean_title(old_title) != new_title
    tags_changed = [t.lower() for t in old_tags] != new_tags

    return {
        "listing_id": listing["listing_id"],
        "category": cat,
        "url": listing.get("url"),
        "views": listing.get("views"),
        "old_title": old_title,
        "new_title": new_title,
        "old_tags": old_tags,
        "new_tags": new_tags,
        "old_score": old_score["score"],
        "new_score": new_score["score"],
        "old_notes": old_score["notes"],
        "title_changed": title_changed,
        "tags_changed": tags_changed,
        "needs_update": title_changed or tags_changed,
        "delta": new_score["score"] - old_score["score"],
    }


def write_report(plans: list[dict]):
    os.makedirs(OUT, exist_ok=True)
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "count": len(plans),
                "needs_update": sum(1 for p in plans if p["needs_update"]),
                "plans": plans,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    lines = [
        "# SEO Optimization Plan — TheMathRelaxing",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Listings: {len(plans)} | Need update: {sum(1 for p in plans if p['needs_update'])}",
        "",
        "## Priority fixes (biggest score gain)",
        "",
    ]
    ranked = sorted(plans, key=lambda p: (-p["delta"], p["old_score"]))
    for p in ranked[:25]:
        if not p["needs_update"] and p["delta"] <= 0:
            continue
        lines.append(f"### {p['listing_id']}  ({p['category']})  {p['old_score']}→{p['new_score']} (Δ{p['delta']:+d})")
        if p["old_notes"]:
            lines.append(f"- Issues: {', '.join(p['old_notes'])}")
        if p["title_changed"]:
            lines.append(f"- Title was: {p['old_title']}")
            lines.append(f"- Title new: {p['new_title']}")
        if p["tags_changed"]:
            lines.append(f"- Tags was ({len(p['old_tags'])}): {', '.join(p['old_tags'])}")
            lines.append(f"- Tags new ({len(p['new_tags'])}): {', '.join(p['new_tags'])}")
        lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Plan:   {PLAN_PATH}")
    print(f"Report: {REPORT_PATH}")


def apply_plan(manager: etsy_manager.EtsyManager, plans: list[dict], sleep: float = 0.4):
    updated = 0
    for p in plans:
        if not p["needs_update"]:
            continue
        fields = {}
        if p["title_changed"]:
            fields["title"] = p["new_title"]
        if p["tags_changed"]:
            fields["tags"] = p["new_tags"]
        print(f"PATCH {p['listing_id']}: {list(fields.keys())}")
        try:
            manager.update_listing(p["listing_id"], **fields)
            updated += 1
        except Exception as e:
            print(f"  ERROR {p['listing_id']}: {e}")
        time.sleep(sleep)
    print(f"Updated {updated} listings.")
    return updated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Apply PATCHes to Etsy")
    ap.add_argument("--refresh", action="store_true", help="Refresh active listings cache")
    ap.add_argument("--only", type=int, nargs="*", help="Only these listing IDs")
    ap.add_argument("--limit", type=int, default=0, help="Max listings to update when applying")
    ap.add_argument("--min-delta", type=int, default=1, help="Only update if score gain >= this")
    args = ap.parse_args()

    manager = etsy_manager.EtsyManager()
    listings = fetch_active(manager, refresh=args.refresh)
    if args.only:
        want = set(args.only)
        listings = [r for r in listings if r["listing_id"] in want]

    plans = [plan_for(r) for r in listings]
    # sort by urgency
    plans.sort(key=lambda p: (-p["delta"], p["old_score"]))
    write_report(plans)

    need = [p for p in plans if p["needs_update"] and p["delta"] >= args.min_delta]
    print(f"\nListings: {len(plans)} | improvements: {len(need)}")
    print(f"{'ID':<12} {'Δ':>4} {'OLD':>4} {'NEW':>4}  CAT         TITLE")
    for p in need[:30]:
        print(
            f"{p['listing_id']:<12} {p['delta']:>+4} {p['old_score']:>4} {p['new_score']:>4}  "
            f"{p['category']:<10}  {p['new_title'][:55]}"
        )

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to PATCH Etsy.")
        return

    to_apply = need
    if args.limit:
        to_apply = need[: args.limit]
    print(f"\nApplying {len(to_apply)} updates...")
    apply_plan(manager, to_apply)


if __name__ == "__main__":
    main()
