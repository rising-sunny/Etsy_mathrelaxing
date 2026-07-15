"""
product_finder.py — Encuentra productos con potencial real de venta
===================================================================
Combina:
  • API Etsy v3  → #listings, precios, favorites (proxy de demanda)
  • Métricas eRank (opcional, CSV o dict) → Avg. Searches, KD, Competition

Uso:
  python product_finder.py                  # corre semillas MathRelaxing
  python product_finder.py --kw "mandala digital download"
  python product_finder.py --erank research/erank_export.csv
  python product_finder.py --top 25 --out research/opportunities.json

Score (0–100):
  demanda   (favorites de top listings + búsquedas eRank si hay)
  oportunidad (ratio demanda/competencia; castiga saturación)
  precio    (sweet spot digital $4–$15)
  fit       (encaje con capacidad MathRelaxing: digital math/geo/STEM)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import time
import urllib.parse
from datetime import datetime, timezone

import etsy_manager

# ── Semillas alineadas a MathRelaxing (digital, math, geometry, STEM, relax) ─
SEED_KEYWORDS = [
    # Core brand (baseline)
    "sacred geometry coloring book",
    "fractal coloring book",
    "mathematical coloring book",
    "adult coloring book printable",
    "coloring book digital download",
    # Geometry / patterns
    "mandala coloring book printable",
    "geometric coloring pages",
    "islamic geometry art print",
    "celtic knot coloring page",
    "voronoi art print",
    "tessellation coloring book",
    "penrose tiling art",
    "sacred geometry wall art digital",
    "flower of life printable",
    "metatron cube art print",
    # Science / STEM digital
    "physics wall art printable",
    "math poster digital download",
    "chemistry periodic table art",
    "astronomy coloring book",
    "constellation art print digital",
    "dna art print digital",
    "molecule wall art printable",
    "neural network art print",
    "circuit board art print",
    "chladni figures print",
    "cymatics art print",
    # iPad / digital coloring & planners
    "procreate coloring pages",
    "goodnotes coloring book",
    "digital coloring book ipad",
    "color by number procreate",
    "stem digital planner",
    "math digital planner goodnotes",
    "science digital notebook",
    "bullet journal math stickers",
    # Loops / motion (existing product type)
    "seamless loop video download",
    "abstract loop animation digital",
    "generative art print digital",
    "fractal art print digital",
    # Niche low-competition candidates
    "radiolaria art print",
    "diatom art print digital",
    "hyperbolic geometry art",
    "lissajous curve art",
    "phyllotaxis art print",
    "mandelbrot art print digital",
    "julia set art print",
    "strange attractor art print",
    "platonic solids coloring",
    "polyhedra coloring pages",
    "origami crease pattern art",
    "knot theory art print",
    "topology art print",
    "fourier series art",
    "graph theory poster",
    "golden ratio wall art digital",
    "fibonacci spiral printable",
    "zellige pattern printable",
    "muqarnas geometry art",
    "yantra coloring page",
    "labyrinth coloring page printable",
    "zen tangle math digital",
]

# Tokens que aumentan fit con MathRelaxing (digital + math/geo/STEM aesthetic)
FIT_POSITIVE = {
    "math", "mathematical", "geometry", "geometric", "sacred", "fractal",
    "mandala", "tessellation", "voronoi", "celtic", "islamic", "coloring",
    "printable", "digital", "download", "procreate", "goodnotes", "ipad",
    "physics", "chemistry", "science", "stem", "astronomy", "constellation",
    "molecule", "neural", "circuit", "chladni", "cymatics", "mandelbrot",
    "julia", "attractor", "fibonacci", "golden", "polyhedra", "topology",
    "knot", "lissajous", "phyllotaxis", "diatom", "radiolaria", "hyperbolic",
    "generative", "art", "wall", "poster", "planner", "notebook", "loop",
    "seamless", "animation", "metatron", "flower of life", "penrose",
    "zellige", "yantra", "labyrinth", "fourier", "graph",
}
FIT_NEGATIVE = {
    "jewelry", "necklace", "ring", "earring", "shirt", "hoodie", "mug",
    "sticker pack physical", "wedding", "baby", "crochet", "knit", "candle",
    "soap", "perfume", "custom photo", "pet portrait", "3d printed physical",
}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research")


def _price_amount(listing: dict) -> float | None:
    price = listing.get("price") or {}
    amount = price.get("amount")
    divisor = price.get("divisor") or 100
    if amount is None:
        return None
    return float(amount) / float(divisor)


def parse_search_count(val) -> float | None:
    """Parse eRank-style search counts: '< 20', '1,079', 'Unknown'."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s.lower() in {"unknown", "n/a", "-", ""}:
        return None
    if s.startswith("<"):
        m = re.search(r"[\d.]+", s)
        return float(m.group()) * 0.5 if m else 10.0
    try:
        return float(s)
    except ValueError:
        return None


def fit_score(keyword: str) -> float:
    """0–100: how well this keyword matches MathRelaxing production capacity."""
    kw = keyword.lower()
    tokens = set(re.findall(r"[a-z0-9]+", kw))
    # multi-word + token positives (count unique phrase hits)
    pos_hits = [p for p in FIT_POSITIVE if (len(p) > 3 and p in kw) or p in tokens]
    pos = len(pos_hits)
    neg = sum(1 for n in FIT_NEGATIVE if n in kw)
    # Base: each relevant token helps; brand core starts higher
    raw = 28 + min(pos, 10) * 6 - neg * 30
    # digital / delivery formats we sell
    if any(d in kw for d in ("digital", "printable", "download", "procreate", "goodnotes", "ipad", "pdf")):
        raw += 14
    # product types we already ship
    if any(t in kw for t in ("coloring", "wall art", "poster", "planner", "notebook", "loop", "art print", "pages")):
        raw += 12
    # strong brand-core math/geometry signal
    if any(t in kw for t in (
        "math", "geometry", "geometric", "fractal", "sacred", "voronoi", "mandelbrot",
        "julia", "attractor", "tessellation", "fibonacci", "stem", "physics", "science",
        "molecule", "dna", "neural", "chladni", "cymatics", "constellation", "astronomy",
    )):
        raw += 10
    return max(0.0, min(100.0, float(raw)))


def demand_score(avg_favorites: float, erank_searches: float | None) -> float:
    """0–100 from favorites (always) + eRank searches (if present)."""
    # favorites: log-ish scale; 50 fav ≈ mid, 200+ high
    fav = 0.0
    if avg_favorites > 0:
        fav = min(100.0, (avg_favorites ** 0.55) * 8.0)

    if erank_searches is None:
        return fav

    # searches: <20 low, 100 mid, 1000+ high
    if erank_searches < 20:
        srch = erank_searches * 1.5
    elif erank_searches < 100:
        srch = 30 + (erank_searches - 20) * 0.5
    elif erank_searches < 1000:
        srch = 70 + (erank_searches - 100) * 0.03
    else:
        srch = min(100.0, 97 + erank_searches / 5000)

    return 0.55 * srch + 0.45 * fav


def competition_score(listing_count: int, erank_kd: float | None) -> float:
    """0–100 where HIGH = easier (low competition). Used as opportunity component."""
    if listing_count <= 0:
        base = 90.0
    elif listing_count < 100:
        base = 95.0
    elif listing_count < 500:
        base = 85.0
    elif listing_count < 2000:
        base = 70.0
    elif listing_count < 10000:
        base = 50.0
    elif listing_count < 50000:
        base = 30.0
    else:
        base = 12.0

    if erank_kd is not None:
        # KD 0 easy, 100 hard → invert
        kd_ease = max(0.0, 100.0 - erank_kd)
        base = 0.55 * base + 0.45 * kd_ease
    return base


def price_score(median_price: float | None) -> float:
    if median_price is None or median_price <= 0:
        return 50.0
    # Digital sweet spot $4–$12
    if 4.0 <= median_price <= 12.0:
        return 95.0
    if 3.0 <= median_price < 4.0 or 12.0 < median_price <= 18.0:
        return 75.0
    if 18.0 < median_price <= 30.0:
        return 45.0
    if median_price < 3.0:
        return 35.0
    return 25.0


def compute_scores(row: dict) -> dict:
    d = demand_score(row.get("avg_favorites") or 0, row.get("erank_searches"))
    c = competition_score(row.get("listing_count") or 0, row.get("erank_kd"))
    p = price_score(row.get("median_price"))
    f = row.get("fit") if row.get("fit") is not None else fit_score(row["keyword"])

    # opportunity component (demand × ease)
    opp = 100.0 * ((max(d, 1) / 100) ** 0.55) * ((max(c, 1) / 100) ** 0.45)

    # Final: opportunity heavy, fit gates garbage niches, price soft
    total = 0.42 * opp + 0.28 * f + 0.18 * d + 0.12 * p

    # Hard gate: terrible fit → kill
    if f < 35:
        total *= 0.45
    # Dead demand + no eRank signal and almost no favorites
    if d < 8 and (row.get("erank_searches") is None or (row.get("erank_searches") or 0) < 15):
        total *= 0.7

    row = dict(row)
    row.update({
        "score_demand": round(d, 1),
        "score_competition_ease": round(c, 1),
        "score_price": round(p, 1),
        "score_fit": round(f, 1),
        "score_opportunity": round(opp, 1),
        "score_total": round(total, 1),
        "verdict": verdict(total, d, c, f),
    })
    return row


def verdict(total: float, demand: float, ease: float, fit: float) -> str:
    if fit < 35:
        return "SKIP — fuera de marca / no producible"
    if total >= 68 and demand >= 30:
        return "BUILD — fuerte potencial"
    if total >= 55:
        return "TEST — buena apuesta (MVP o listing piloto)"
    if total >= 45 and ease >= 55:
        return "WATCH — nicho abierto, demanda a validar"
    if demand >= 50 and ease < 35:
        return "HARD — demanda real, mercado saturado"
    return "WEAK — priorizar otras keywords"


def analyze_keyword(manager: etsy_manager.EtsyManager, keyword: str, sample: int = 25) -> dict:
    q = urllib.parse.quote_plus(keyword)
    # Sort by relevance (default). Sample top results for favorers/price.
    data = manager.make_request(
        "GET",
        f"/listings/active?keywords={q}&limit={min(sample, 100)}&offset=0",
    )
    results = data.get("results") or []
    count = int(data.get("count") or 0)

    favorites = [int(r.get("num_favorers") or 0) for r in results]
    prices = [p for r in results if (p := _price_amount(r)) is not None]
    titles = [r.get("title", "")[:80] for r in results[:5]]

    avg_fav = statistics.mean(favorites) if favorites else 0.0
    med_fav = statistics.median(favorites) if favorites else 0.0
    max_fav = max(favorites) if favorites else 0
    med_price = statistics.median(prices) if prices else None
    avg_price = statistics.mean(prices) if prices else None

    digital_flags = 0
    for r in results:
        if r.get("is_digital") or r.get("listing_type") == "download":
            digital_flags += 1
    digital_share = digital_flags / len(results) if results else 0.0

    row = {
        "keyword": keyword,
        "listing_count": count,
        "sample_size": len(results),
        "avg_favorites": round(avg_fav, 1),
        "median_favorites": round(med_fav, 1),
        "max_favorites": max_fav,
        "median_price": round(med_price, 2) if med_price is not None else None,
        "avg_price": round(avg_price, 2) if avg_price is not None else None,
        "digital_share": round(digital_share, 2),
        "sample_titles": titles,
        "erank_searches": None,
        "erank_kd": None,
        "erank_competition": None,
        "erank_ctr": None,
        "fit": fit_score(keyword),
    }
    return compute_scores(row)


def load_erank_csv(path: str) -> dict[str, dict]:
    """Load eRank export. Flexible column names."""
    mapping: dict[str, dict] = {}
    def _cell(v) -> str:
        if v is None:
            return ""
        if isinstance(v, (list, tuple)):
            return " ".join(str(x) for x in v).strip()
        return str(v).strip()

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            # normalize keys
            row = { _cell(k).lower(): _cell(v) for k, v in raw.items() }
            kw = row.get("keywords") or row.get("keyword") or row.get("search term")
            if not kw:
                continue
            mapping[kw.lower()] = {
                "erank_searches": parse_search_count(
                    row.get("avg. searches") or row.get("avg searches") or row.get("searches")
                ),
                "erank_kd": parse_search_count(row.get("kd") or row.get("keyword difficulty")),
                "erank_competition": parse_search_count(
                    row.get("etsy competition") or row.get("competition")
                ),
                "erank_ctr": parse_search_count(
                    (row.get("avg. ctr") or row.get("ctr") or "").replace("%", "")
                ),
            }
    return mapping


def merge_erank(row: dict, erank: dict[str, dict]) -> dict:
    e = erank.get(row["keyword"].lower())
    if not e:
        return row
    row = dict(row)
    row.update({k: v for k, v in e.items() if v is not None})
    # Prefer eRank competition if Etsy count missing/weird
    if row.get("erank_competition") and (row.get("listing_count") or 0) == 0:
        row["listing_count"] = int(row["erank_competition"])
    return compute_scores(row)


def product_idea(row: dict) -> str:
    """Suggest product type MathRelaxing can ship."""
    kw = row["keyword"].lower()
    if any(x in kw for x in ("planner", "notebook", "goodnotes", "bullet journal")):
        return "STEM planner / digital notebook (PDF hipervinculado)"
    if any(x in kw for x in ("procreate", "ipad", "color by number")):
        return "iPad bundle (GoodNotes PDF + Procreate PNG + swatches)"
    if any(x in kw for x in ("loop", "animation", "seamless")):
        return "Seamless loop MP4 (1080p + preview con marca de agua)"
    if any(x in kw for x in ("wall art", "poster", "print", "art print")):
        return "Digital art print (JPG/PNG alta res + mockups)"
    if "coloring" in kw or "coloring book" in kw:
        return "Libro para colorear PDF 50 págs (template_coloring_book)"
    return "Digital download (print o tablet) — definir tipo tras validar top listings"


def run(keywords: list[str], erank_path: str | None, sample: int, sleep: float) -> list[dict]:
    manager = etsy_manager.EtsyManager()
    erank = load_erank_csv(erank_path) if erank_path else {}
    rows = []
    total = len(keywords)
    print(f"\nAnalizando {total} keywords (Etsy API)...")
    print(f"{'KEYWORD':<42} {'LIST':>8} {'FAV~':>7} {'$~':>7} {'SCORE':>7}  VERDICT")
    print("-" * 100)
    for i, kw in enumerate(keywords, 1):
        try:
            row = analyze_keyword(manager, kw, sample=sample)
            if erank:
                row = merge_erank(row, erank)
            row["product_idea"] = product_idea(row)
            rows.append(row)
            price = f"${row['median_price']:.2f}" if row.get("median_price") else "  —"
            print(
                f"{kw[:42]:<42} {row['listing_count']:>8} {row['avg_favorites']:>7.1f} "
                f"{price:>7} {row['score_total']:>7.1f}  {row['verdict']}"
            )
        except Exception as e:
            print(f"{kw[:42]:<42} ERROR: {e}")
            rows.append({"keyword": kw, "error": str(e), "score_total": -1, "verdict": "ERROR"})
        if i < total:
            time.sleep(sleep)
    return rows


def print_top(rows: list[dict], n: int = 15) -> None:
    ok = [r for r in rows if r.get("score_total", -1) >= 0]
    ok.sort(key=lambda r: r.get("score_total", 0), reverse=True)
    print("\n" + "=" * 100)
    print(f"TOP {min(n, len(ok))} OPORTUNIDADES — MathRelaxing")
    print("=" * 100)
    for i, r in enumerate(ok[:n], 1):
        print(f"\n#{i}  {r['keyword']}   →  {r.get('score_total')}  |  {r.get('verdict')}")
        print(
            f"    listings={r.get('listing_count')}  fav_avg={r.get('avg_favorites')}  "
            f"price_med={r.get('median_price')}  digital={r.get('digital_share')}  "
            f"fit={r.get('score_fit')}  demand={r.get('score_demand')}  ease={r.get('score_competition_ease')}"
        )
        if r.get("erank_searches") is not None:
            print(
                f"    eRank: searches={r.get('erank_searches')}  KD={r.get('erank_kd')}  "
                f"comp={r.get('erank_competition')}"
            )
        print(f"    idea: {r.get('product_idea')}")
        titles = r.get("sample_titles") or []
        if titles:
            print(f"    top: {titles[0][:70]}")


def save_results(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shop": "TheMathRelaxing",
        "count": len(rows),
        "results": sorted(rows, key=lambda r: r.get("score_total", -1), reverse=True),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    # Also CSV for quick scan
    csv_path = os.path.splitext(path)[0] + ".csv"
    fields = [
        "keyword", "score_total", "verdict", "listing_count", "avg_favorites",
        "median_price", "digital_share", "score_demand", "score_competition_ease",
        "score_fit", "score_price", "erank_searches", "erank_kd", "product_idea",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in payload["results"]:
            w.writerow(r)
    print(f"\nGuardado: {path}")
    print(f"CSV:      {csv_path}")


def main():
    ap = argparse.ArgumentParser(description="Product opportunity finder (Etsy + eRank)")
    ap.add_argument("--kw", action="append", dest="keywords", help="Keyword extra (repeatable)")
    ap.add_argument("--file", help="Archivo texto con 1 keyword por línea")
    ap.add_argument("--erank", help="CSV export de eRank para fusionar búsquedas/KD")
    ap.add_argument("--seeds", action="store_true", default=True, help="Usar semillas MathRelaxing")
    ap.add_argument("--no-seeds", action="store_true", help="Solo keywords pasadas por --kw/--file")
    ap.add_argument("--sample", type=int, default=25, help="Listings a muestrear por keyword")
    ap.add_argument("--sleep", type=float, default=0.35, help="Pausa entre requests (s)")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument(
        "--out",
        default=os.path.join(OUT_DIR, f"opportunities_{datetime.now().strftime('%Y%m%d_%H%M')}.json"),
    )
    args = ap.parse_args()

    kws: list[str] = []
    if not args.no_seeds:
        kws.extend(SEED_KEYWORDS)
    if args.keywords:
        kws.extend(args.keywords)
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            kws.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))

    # de-dupe preserve order
    seen = set()
    keywords = []
    for k in kws:
        kl = k.lower().strip()
        if kl and kl not in seen:
            seen.add(kl)
            keywords.append(k.strip())

    rows = run(keywords, args.erank, args.sample, args.sleep)
    print_top(rows, args.top)
    save_results(rows, args.out)


if __name__ == "__main__":
    main()
