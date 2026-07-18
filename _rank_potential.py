"""Rank live listings by traffic + sales potential signals."""
from __future__ import annotations

from collections import defaultdict
from etsy_manager import EtsyManager


def money(p) -> float:
    if p is None:
        return 0.0
    if isinstance(p, dict):
        return float(p.get("amount", 0)) / float(p.get("divisor", 100) or 100)
    return float(p)


def fetch_all(m, shop, state):
    offset, items = 0, []
    while True:
        r = m.make_request(
            "GET",
            f"/shops/{shop}/listings?state={state}&limit=100&offset={offset}",
        )
        batch = r.get("results") or []
        items.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    return items


def classify(title: str) -> str:
    t = (title or "").lower()
    if "sticker" in t:
        return "stickers"
    if any(k in t for k in ("resume", "cv ", "cover letter", "recommendation")):
        return "career_docs"
    if "wedding" in t or "seating" in t:
        return "wedding"
    if "emergency" in t or "binder" in t and "ice" in t:
        return "organizer"
    if "planner" in t or "notebook" in t or "journal" in t:
        return "planner_notebook"
    if "palette" in t or "swatch" in t:
        return "palettes"
    if "loop" in t or "animation" in t or "seamless" in t:
        return "animation_loop"
    if "ipad" in t or "interactive" in t or "goodnotes" in t and "color" in t:
        return "ipad_coloring"
    if "coloring" in t or "color by number" in t:
        return "coloring_pdf"
    if any(k in t for k in ("set of", "print set", "poster set", "gallery", "bundle")) and any(
        k in t for k in ("wall", "print", "poster", "art")
    ):
        return "wall_art_set"
    if any(k in t for k in ("wall art", "poster", "art print", "equation", "attractor")):
        return "wall_art_single"
    if "grid paper" in t or "graph paper" in t:
        return "graph_paper"
    return "other"


def score(it: dict) -> float:
    """Heuristic potential score (not pure popularity)."""
    views = int(it.get("views") or 0)
    favs = int(it.get("num_favorers") or 0)
    # quantity sold if present
    sold = int(it.get("quantity_sold") or it.get("total_sales") or 0)
    price = money(it.get("price"))
    # engagement rate: favs relative to views (cold start bias if views=0)
    eng = (favs / views) if views > 0 else 0.0
    # Score weights: views drive discovery; favs intent; sold is gold
    s = views * 1.0 + favs * 8.0 + sold * 50.0 + eng * 20.0
    # slight boost if priced in sweet spot for new shop
    if 1.99 <= price <= 3.99:
        s *= 1.05
    return s


def main():
    m = EtsyManager()
    shop = m.get_shop_id()
    items = fetch_all(m, shop, "active")
    dig = [
        it
        for it in items
        if (it.get("listing_type") or it.get("type") or "").lower()
        in ("download", "digital", "downloadable")
    ]

    rows = []
    for it in dig:
        rows.append(
            {
                "id": it.get("listing_id"),
                "title": (it.get("title") or "")[:70],
                "views": int(it.get("views") or 0),
                "favs": int(it.get("num_favorers") or 0),
                "sold": int(it.get("quantity_sold") or it.get("total_sales") or 0),
                "price": money(it.get("price")),
                "cat": classify(it.get("title") or ""),
                "score": score(it),
                "tags": it.get("tags") or [],
            }
        )

    rows.sort(key=lambda r: (r["views"], r["favs"], r["score"]), reverse=True)

    print(f"=== ACTIVE DIGITAL: {len(rows)} ===\n")
    print("--- TOP BY VIEWS ---")
    print(f"{'views':>5} {'favs':>4} {'sold':>4} {'$':>5}  {'cat':18}  title")
    for r in rows[:25]:
        print(
            f"{r['views']:5} {r['favs']:4} {r['sold']:4} {r['price']:5.2f}  {r['cat']:18}  {r['title']}"
        )

    with_signal = [r for r in rows if r["views"] > 0 or r["favs"] > 0]
    print(f"\n=== WITH ANY SIGNAL: {len(with_signal)} / {len(rows)} ===")

    # Category aggregates
    by_cat = defaultdict(lambda: {"n": 0, "views": 0, "favs": 0, "sold": 0, "prices": []})
    for r in rows:
        c = by_cat[r["cat"]]
        c["n"] += 1
        c["views"] += r["views"]
        c["favs"] += r["favs"]
        c["sold"] += r["sold"]
        c["prices"].append(r["price"])

    print("\n--- BY CATEGORY (sorted by total views) ---")
    cat_rows = sorted(by_cat.items(), key=lambda x: x[1]["views"], reverse=True)
    for cat, c in cat_rows:
        avg_v = c["views"] / c["n"] if c["n"] else 0
        avg_p = sum(c["prices"]) / len(c["prices"]) if c["prices"] else 0
        print(
            f"  {cat:18}  n={c['n']:2}  views={c['views']:3}  favs={c['favs']:2}  "
            f"sold={c['sold']}  avg_views={avg_v:.1f}  avg$={avg_p:.2f}"
        )

    # Potential: high views OR high favs OR category strength
    print("\n--- TOP POTENTIAL (score) ---")
    by_score = sorted(rows, key=lambda r: r["score"], reverse=True)
    for r in by_score[:20]:
        if r["score"] <= 0:
            continue
        print(
            f"  score={r['score']:6.1f}  v={r['views']:3} f={r['favs']}  "
            f"${r['price']:.2f}  [{r['cat']}]  {r['title'][:55]}"
        )

    # Keyword hints from top titles
    print("\n--- KEYWORD HINTS FROM TOP VIEWED TITLES ---")
    words = defaultdict(int)
    for r in rows[:30]:
        for w in (r["title"] or "").lower().replace("|", " ").replace("–", " ").split():
            w = "".join(ch for ch in w if ch.isalnum() or ch == "-")
            if len(w) < 4 or w in {
                "with", "from", "this", "that", "digital", "download", "printable",
                "instant", "edition", "bundle", "print", "prints", "poster", "posters",
            }:
                continue
            words[w] += 1
    for w, n in sorted(words.items(), key=lambda x: -x[1])[:25]:
        print(f"  {n:2}×  {w}")

    # Zero-signal expensive categories still worth scaling if product-market fit known
    zeros = [r for r in rows if r["views"] == 0 and r["favs"] == 0]
    print(f"\n=== ZERO SIGNAL: {len(zeros)} listings (need SEO/ads or retire) ===")
    zcat = defaultdict(int)
    for r in zeros:
        zcat[r["cat"]] += 1
    for cat, n in sorted(zcat.items(), key=lambda x: -x[1]):
        print(f"  {cat:18}  {n}")


if __name__ == "__main__":
    main()
