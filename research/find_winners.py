"""
find_winners.py — discovery pipeline (config-driven, not hard-coded lists)

Replaces the "edit SEED_KEYWORDS in three different .py files" workflow:

  1. Load research/config/winners.yaml  (seeds, modifiers, fit, thresholds)
  2. Expand seeds × modifiers → long-tail candidates
  3. Optionally mine tags from top Etsy SERPs of each seed
  4. Scan Etsy API (reuse product_finder.analyze_keyword)
  5. Mark keywords already covered by your active shop
  6. Rank + write MD/JSON/CSV
  7. Optional: eRank bulk only for top-N (saves quota)

Usage:
  python research/find_winners.py
  python research/find_winners.py --expand-only
  python research/find_winners.py --seeds "adhd planner" "habit tracker"
  python research/find_winners.py --file research/my_seeds.txt --no-expand
  python research/find_winners.py --erank              # Edge bulk for top-N
  python research/find_winners.py --config research/config/winners.yaml
  python research/find_winners.py --max 40 --top 20
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# repo root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import etsy_manager  # noqa: E402
import product_finder as pf  # noqa: E402

BASE = Path(__file__).resolve().parent
DEFAULT_CONFIG = BASE / "config" / "winners.yaml"


# ── config load ──────────────────────────────────────────────────────────────

def load_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # Minimal YAML subset (enough for our config shape) — no external dep
    return _simple_yaml(text)


def _simple_yaml(text: str):
    """Tiny indented-YAML loader for dict/list/scalars used in winners.yaml."""
    # Prefer json if user passed .json
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # retry after message
        return yaml.safe_load(text)
    except ImportError:
        print(
            "NOTE: install PyYAML for full config support:  pip install pyyaml\n"
            "Falling back to embedded defaults + any --seeds/--file you passed."
        )
        return {}


def _cfg(cfg: dict, *keys, default=None):
    cur = cfg
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default


# ── keyword expansion ────────────────────────────────────────────────────────

def _normalize(kw: str) -> str:
    return re.sub(r"\s+", " ", kw.strip().lower())


def expand_keywords(seeds: list[str], cfg: dict) -> list[str]:
    """seeds + seed+suffix combos (skip if product stem already in seed)."""
    suffixes = list(_cfg(cfg, "modifiers", "suffixes", default=[]) or [])
    stems = [s.lower() for s in (_cfg(cfg, "modifiers", "product_stems", default=[]) or [])]
    out: list[str] = []
    seen: set[str] = set()

    def add(k: str):
        n = _normalize(k)
        if not n or n in seen:
            return
        seen.add(n)
        out.append(k.strip())

    for seed in seeds:
        seed = seed.strip()
        if not seed or seed.startswith("#"):
            continue
        add(seed)
        sl = seed.lower()
        if any(st in sl for st in stems):
            continue  # already product-shaped
        for suf in suffixes:
            sufl = suf.lower()
            # avoid "molecule art wall art", "poster poster", etc.
            if sufl in sl:
                continue
            if sl.endswith(" art") and sufl in ("wall art", "poster", "art print"):
                continue
            if sl.endswith(" poster") and "poster" in sufl:
                continue
            add(f"{seed} {suf}")

    return out


def mine_tags_for_seed(manager, seed: str, cfg: dict) -> list[str]:
    """Pull tags from top active listings for a seed keyword."""
    per = int(_cfg(cfg, "expansion", "mine_per_seed", default=8) or 8)
    min_chars = int(_cfg(cfg, "expansion", "min_tag_chars", default=4) or 4)
    max_words = int(_cfg(cfg, "expansion", "max_tag_words", default=4) or 4)
    block = {t.lower() for t in (_cfg(cfg, "expansion", "tag_blocklist", default=[]) or [])}

    q = urllib.parse.quote_plus(seed)
    try:
        data = manager.make_request(
            "GET",
            f"/listings/active?keywords={q}&limit={min(per, 25)}&offset=0",
        )
    except Exception as e:
        print(f"  tag-mine skip [{seed}]: {e}")
        return []

    counts: dict[str, int] = {}
    for listing in data.get("results") or []:
        for tag in listing.get("tags") or []:
            t = _normalize(str(tag))
            if len(t) < min_chars:
                continue
            words = t.split()
            if len(words) > max_words:
                continue
            if t in block or any(b == w for w in words for b in block):
                continue
            # skip pure numbers
            if re.fullmatch(r"[\d\s]+", t):
                continue
            counts[t] = counts.get(t, 0) + 1

    # most frequent tags first
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [t for t, _ in ranked[: per * 2]]


def apply_exclusions(keywords: list[str], cfg: dict) -> list[str]:
    ban = [b.lower() for b in (_cfg(cfg, "exclude_if_contains", default=[]) or [])]
    out = []
    for k in keywords:
        kl = k.lower()
        if any(b in kl for b in ban):
            continue
        out.append(k)
    return out


def cap_keywords(keywords: list[str], seeds: list[str], cfg: dict) -> list[str]:
    max_k = int(_cfg(cfg, "expansion", "max_keywords", default=60) or 60)
    keep_seeds = bool(_cfg(cfg, "expansion", "keep_seeds", default=True))
    if len(keywords) <= max_k:
        return keywords
    seed_set = {_normalize(s) for s in seeds}
    seeds_kept = [k for k in keywords if _normalize(k) in seed_set]
    rest = [k for k in keywords if _normalize(k) not in seed_set]
    if keep_seeds:
        room = max(0, max_k - len(seeds_kept))
        return seeds_kept + rest[:room]
    return keywords[:max_k]


# ── shop coverage ────────────────────────────────────────────────────────────

def load_shop_phrases(manager, cfg: dict) -> list[str]:
    """Active listing titles + config aliases → phrases we already cover."""
    phrases: list[str] = []
    aliases = _cfg(cfg, "shop", "owned_aliases", default=[]) or []
    phrases.extend(_normalize(a) for a in aliases)

    if not _cfg(cfg, "shop", "mark_owned", default=True):
        return phrases

    try:
        shop_id = manager.get_shop_id()
        # paginate a bit
        offset = 0
        titles = []
        while offset < 200:
            data = manager.make_request(
                "GET",
                f"/shops/{shop_id}/listings/active?limit=100&offset={offset}",
            )
            batch = data.get("results") or []
            if not batch:
                break
            for L in batch:
                t = L.get("title") or ""
                titles.append(t)
                for tag in L.get("tags") or []:
                    phrases.append(_normalize(str(tag)))
            offset += 100
            if len(batch) < 100:
                break
            time.sleep(0.25)
        # rough title tokens: keep 2–4 word windows of interest is heavy;
        # store full normalized titles for substring match
        for t in titles:
            phrases.append(_normalize(t))
        print(f"  shop: {len(titles)} active listings loaded for coverage check")
    except Exception as e:
        print(f"  shop coverage skipped: {e}")

    # dedupe
    seen = set()
    out = []
    for p in phrases:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def is_owned(keyword: str, shop_phrases: list[str]) -> bool:
    k = _normalize(keyword)
    if not k:
        return False
    # direct phrase / alias hit
    for p in shop_phrases:
        if len(p) < 4:
            continue
        # keyword contained in a listing title, or alias contained in keyword
        if k in p or p in k:
            # avoid ultra-short false positives
            if len(p) >= 6 or len(k) >= 6:
                return True
    return False


# ── fit override from config ─────────────────────────────────────────────────

def apply_config_fit(row: dict, cfg: dict) -> dict:
    pos = _cfg(cfg, "fit", "positive", default=None)
    neg = _cfg(cfg, "fit", "negative", default=None)
    if not pos and not neg:
        return row
    kw = row["keyword"].lower()
    tokens = set(re.findall(r"[a-z0-9]+", kw))
    score = 28.0
    if pos:
        hits = sum(1 for p in pos if (len(p) > 3 and p in kw) or p in tokens)
        score += min(hits, 10) * 6
    if neg:
        score -= sum(1 for n in neg if n in kw) * 30
    if any(d in kw for d in ("digital", "printable", "download", "procreate", "goodnotes", "ipad", "pdf")):
        score += 14
    if any(t in kw for t in (
        "coloring", "wall art", "poster", "planner", "notebook", "tracker",
        "binder", "template", "magnet", "sticker", "tote", "doormat",
        "mousepad", "mouse pad", "pillow", "shirt", "sweatshirt",
    )):
        score += 12
    # STEM signal on physical gift blanks
    if any(t in kw for t in ("math", "physics", "science", "stem", "nurse", "teacher", "bookish")):
        if any(t in kw for t in ("magnet", "sticker", "tote", "doormat", "mousepad", "shirt", "pillow", "mug")):
            score += 10
    score = max(0.0, min(100.0, score))
    row = dict(row)
    row["fit"] = score
    return pf.compute_scores(row)


# ── POD cross (Printify catalog cache — no live API required) ────────────────

# keyword stem → Printify family labels used in printify_catalog_scan.json
POD_FAMILY_HINTS = [
    (r"magnet", "magnet"),
    (r"sticker|decal", "sticker"),
    (r"tote|bag", "tote_bag"),
    (r"doormat|door mat|welcome mat", "doormat"),
    (r"mouse\s*pad|mousepad", "mousepad"),
    (r"pillow|cushion", "pillow"),
    (r"mug|tumbler|bottle", "drinkware"),
    (r"shirt|tee|hoodie|sweatshirt|tank", "apparel"),
    (r"notebook|journal", "notebook"),
    (r"poster|wall art|print|canvas", "poster_print"),
    (r"card|milestone", "card"),
    (r"puzzle", "puzzle"),
    (r"clock", "clock"),
]

# Preferred blueprint IDs already piloted / known good for this shop
POD_PREFERRED = {
    "poster_print": [282],   # Matte Vertical Posters (in production)
    "magnet": [428, 857, 771],
    "sticker": [400, 600, 811],
    "tote_bag": [5113, 1300, 507],
    "doormat": [1346, 1601],
    "mousepad": [582, 663],
    "notebook": [485, 514],
    "pillow": [10699, 574],
    "apparel": [5, 6, 6842],
    "drinkware": [535, 583],
}


def load_printify_catalog(path: Path | None = None) -> dict | None:
    path = path or (BASE / "printify_catalog_scan.json")
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  POD catalog load failed: {e}")
        return None


def pod_families_for_keyword(keyword: str) -> list[str]:
    kl = keyword.lower()
    fams = []
    for pat, fam in POD_FAMILY_HINTS:
        if re.search(pat, kl):
            fams.append(fam)
    # digital-only vibes → still suggest poster as physical upsell
    if not fams and any(x in kl for x in ("math", "physics", "science", "stem", "fractal", "geometry", "molecule", "dna")):
        fams.append("poster_print")
        fams.append("magnet")
    return fams


def match_pod_blueprints(keyword: str, catalog: dict | None, limit: int = 4) -> dict:
    """Attach offline Printify blank options for a keyword."""
    if not catalog:
        return {"pod_viable": False, "pod_families": [], "pod_blueprints": [], "pod_note": "no catalog cache"}
    fams = pod_families_for_keyword(keyword)
    by_id = {b.get("id"): b for b in (catalog.get("blueprints") or []) if b.get("id") is not None}
    by_fam: dict[str, list] = {}
    for b in catalog.get("blueprints") or []:
        by_fam.setdefault(b.get("family") or "other", []).append(b)

    picks = []
    seen = set()
    for fam in fams:
        # preferred IDs first
        for bid in POD_PREFERRED.get(fam, []):
            if bid in seen:
                continue
            b = by_id.get(bid)
            if b:
                picks.append({
                    "blueprint_id": bid,
                    "title": b.get("title"),
                    "family": fam,
                    "brand_fit": b.get("brand_fit"),
                    "preferred": True,
                })
                seen.add(bid)
        # then top fit in family
        cands = sorted(by_fam.get(fam, []), key=lambda r: (-(r.get("brand_fit") or 0), r.get("title") or ""))
        for b in cands:
            bid = b.get("id")
            if bid in seen:
                continue
            picks.append({
                "blueprint_id": bid,
                "title": b.get("title"),
                "family": fam,
                "brand_fit": b.get("brand_fit"),
                "preferred": False,
            })
            seen.add(bid)
            if len([p for p in picks if p["family"] == fam]) >= limit:
                break

    # already selling this blank?
    existing = []
    for p in catalog.get("existing_products") or []:
        if p.get("blueprint_id") in seen or any(
            (p.get("title") or "").lower().find(keyword.split()[0].lower()) >= 0 for _ in [0]
        ):
            existing.append({"id": p.get("id"), "title": p.get("title"), "blueprint_id": p.get("blueprint_id")})

    return {
        "pod_viable": bool(picks),
        "pod_families": fams,
        "pod_blueprints": picks[:12],
        "pod_existing_related": existing[:5],
        "pod_note": "from research/printify_catalog_scan.json (offline)" if picks else "no family match",
    }


def attach_pod(rows: list[dict], catalog: dict | None) -> list[dict]:
    out = []
    for r in rows:
        if r.get("score_total", -1) < 0:
            out.append(r)
            continue
        info = match_pod_blueprints(r.get("keyword") or "", catalog)
        rr = dict(r)
        rr.update(info)
        # small score nudge if POD blank is clear + preferred pilot available
        if info.get("pod_viable") and any(p.get("preferred") for p in info.get("pod_blueprints") or []):
            rr["score_total"] = round(float(rr.get("score_total") or 0) + 2.0, 1)
            rr["pod_boost"] = 2.0
        out.append(rr)
    return out


# ── report ───────────────────────────────────────────────────────────────────

def write_report(rows: list[dict], out_prefix: Path, cfg: dict, meta: dict) -> None:
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    ranked = sorted(
        [r for r in rows if r.get("score_total", -1) >= 0],
        key=lambda r: r.get("score_total", 0),
        reverse=True,
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": _cfg(cfg, "profile", default="mathrelaxing"),
        "meta": meta,
        "count": len(ranked),
        "results": ranked,
    }
    json_path = Path(str(out_prefix) + ".json")
    csv_path = Path(str(out_prefix) + ".csv")
    md_path = Path(str(out_prefix) + "_report.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    fields = [
        "score_total", "verdict", "keyword", "listing_count", "avg_favorites",
        "max_favorites", "median_price", "digital_share", "score_demand",
        "score_competition_ease", "score_fit", "erank_searches", "erank_kd",
        "erank_latest", "erank_momentum", "already_in_shop", "source", "product_idea",
        "pod_viable", "pod_families", "pod_blueprint_ids",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in ranked:
            row = dict(r)
            row["pod_families"] = ",".join(r.get("pod_families") or [])
            row["pod_blueprint_ids"] = ",".join(
                str(p.get("blueprint_id")) for p in (r.get("pod_blueprints") or [])[:6]
            )
            w.writerow(row)

    lines = [
        f"# Opportunity report — {_cfg(cfg, 'profile', default='mathrelaxing')}",
        "",
        f"**Generated:** {payload['generated_at']}  ",
        f"**Keywords scanned:** {meta.get('n_keywords')} "
        f"(seeds {meta.get('n_seeds')} → expanded {meta.get('n_expanded')} "
        f"+ tags {meta.get('n_from_tags')})  ",
        f"**Config:** `{meta.get('config_path')}`  ",
        "",
        "## How this run worked",
        "",
        "1. Seeds from config / CLI (not hard-coded in Python)",
        "2. Expanded with modifiers (printable, wall art, …)",
        "3. Optional tag mining from Etsy SERPs",
        "4. Etsy API scoring (`product_finder`)",
        "5. Shop coverage down-rank",
        "6. Optional eRank bulk on top-N",
        "",
        "## Top opportunities",
        "",
        "| # | Score | Keyword | Listings | Fav~ | $~ | eRank | KD | Shop | Verdict |",
        "|--:|------:|---------|---------:|-----:|---:|------:|---:|------|---------|",
    ]
    for i, r in enumerate(ranked[:40], 1):
        price = r.get("median_price")
        price_s = f"${price:.2f}" if isinstance(price, (int, float)) else "—"
        er = r.get("erank_searches")
        er_s = f"{er:g}" if isinstance(er, (int, float)) else "—"
        kd = r.get("erank_kd")
        kd_s = f"{kd:g}" if isinstance(kd, (int, float)) else "—"
        shop = "yes" if r.get("already_in_shop") else ""
        lines.append(
            f"| {i} | {r.get('score_total', 0):.1f} | {r.get('keyword')} "
            f"| {r.get('listing_count', 0)} | {r.get('avg_favorites', 0)} "
            f"| {price_s} | {er_s} | {kd_s} | {shop} | {r.get('verdict', '')} |"
        )

    lines += [
        "",
        "## BUILD / TEST shortlist",
        "",
    ]
    for r in ranked:
        v = r.get("verdict") or ""
        if not v.startswith(("BUILD", "TEST")):
            continue
        owned = " *(already in shop — optimize)*" if r.get("already_in_shop") else ""
        pod = ""
        if r.get("pod_viable"):
            bps = ", ".join(
                f"{p.get('blueprint_id')} ({p.get('title', '')[:28]})"
                for p in (r.get("pod_blueprints") or [])[:3]
            )
            pod = f"  \n  POD blanks: `{','.join(r.get('pod_families') or [])}` → {bps}"
        lines.append(
            f"- **{r['keyword']}** — {r.get('score_total')} — {v}{owned}  \n"
            f"  idea: {r.get('product_idea')}{pod}"
        )

    # POD matrix section
    lines += [
        "",
        "## POD cross (Printify catalog cache — offline)",
        "",
        f"Source: `{meta.get('pod_catalog') or 'research/printify_catalog_scan.json'}`  ",
        "No live Printify API in this run. Preferred pilots: poster **282**, magnet **428**.",
        "",
        "| Keyword | Score | POD families | Top blueprints |",
        "|---------|------:|--------------|----------------|",
    ]
    for r in ranked[:30]:
        if not r.get("pod_viable"):
            continue
        bps = ", ".join(
            str(p.get("blueprint_id")) + ("*" if p.get("preferred") else "")
            for p in (r.get("pod_blueprints") or [])[:4]
        )
        lines.append(
            f"| {r.get('keyword')} | {r.get('score_total', 0):.1f} "
            f"| {', '.join(r.get('pod_families') or [])} | {bps} |"
        )
    lines.append("")
    lines.append("\\* = preferred / already piloted blank")

    lines += [
        "",
        "## Re-run",
        "",
        "```bash",
        f"python research/find_winners.py --config {meta.get('config_path')}",
        "python research/find_winners.py --erank          # top-N eRank in Edge",
        "python research/find_winners.py --seeds \"new idea\" \"another\"",
        "```",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


# ── eRank handoff ────────────────────────────────────────────────────────────

def run_erank_top(keywords: list[str], cfg: dict, out_prefix: str) -> dict[str, dict]:
    """Call erank_edge_bulk for a shortlist; return mapping keyword → metrics."""
    from research import erank_edge_bulk as eb  # may fail if run as script path

    # import by path
    import importlib.util
    eb_path = BASE / "erank_edge_bulk.py"
    spec = importlib.util.spec_from_file_location("erank_edge_bulk", eb_path)
    eb = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(eb)

    # write temp keywords file
    kw_file = BASE / f"_{out_prefix}_erank_keywords.txt"
    kw_file.write_text("\n".join(keywords) + "\n", encoding="utf-8")
    print(f"\n=== eRank bulk for top {len(keywords)} (Edge) ===")
    print(f"Keywords file: {kw_file}")

    # Reuse module API: set outs and run main logic programmatically
    eb.OUT_JSON = BASE / f"{out_prefix}_erank_bulk.json"
    eb.OUT_CSV = BASE / f"{out_prefix}_erank_bulk.csv"
    eb.OUT_MD = BASE / f"{out_prefix}_erank_opportunity_report.md"
    eb.PROFILE.mkdir(parents=True, exist_ok=True)

    login_wait = int(_cfg(cfg, "erank", "login_wait", default=90) or 90)
    batch_size = int(_cfg(cfg, "erank", "batch_size", default=20) or 20)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(eb.PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(eb.BULK_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        body = ""
        try:
            body = page.inner_text("body")[:2000].lower()
        except Exception:
            pass
        if any(x in body for x in ("log in", "sign in", "login")) and "bulk" not in body:
            print(f"Log into eRank in the Edge window (up to {login_wait}s)…")
            deadline = time.time() + login_wait
            while time.time() < deadline:
                page.wait_for_timeout(3000)
                try:
                    body = page.inner_text("body")[:1500].lower()
                except Exception:
                    continue
                if "bulk" in body or ("keyword" in body and "password" not in body):
                    break
            page.goto(eb.BULK_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1500)

        raw = eb.run_batches(page, keywords, batch_size=batch_size)
        context.close()

    rows = [eb.normalize_row(r) for r in raw]
    eb.write_report(rows)
    mapping = {}
    for r in rows:
        kw = (r.get("keyword") or "").lower()
        if not kw:
            continue
        mapping[kw] = {
            "erank_searches": r.get("searches"),
            "erank_kd": r.get("kd"),
            "erank_competition": r.get("competition"),
            "erank_ctr": r.get("ctr"),
            "erank_latest": r.get("latest_month_searches"),
            "erank_momentum": r.get("momentum"),
        }
    return mapping


def merge_erank_map(row: dict, erank_map: dict[str, dict]) -> dict:
    e = erank_map.get(row["keyword"].lower())
    if not e:
        # fuzzy: substring
        kl = row["keyword"].lower()
        for ek, ev in erank_map.items():
            if ek in kl or kl in ek:
                e = ev
                break
    if not e:
        return row
    row = dict(row)
    row.update({k: v for k, v in e.items() if v is not None})
    return pf.compute_scores(row)


# ── main pipeline ────────────────────────────────────────────────────────────

def build_keyword_list(cfg: dict, seeds_cli: list[str], file_path: str | None,
                       do_expand: bool, do_mine: bool, manager) -> tuple[list[str], dict]:
    seeds = []
    seeds.extend(_cfg(cfg, "seeds", default=[]) or [])
    seeds.extend(seeds_cli or [])
    if file_path:
        for line in Path(file_path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                seeds.append(line)

    # de-dupe seeds
    seen = set()
    seeds_u = []
    for s in seeds:
        n = _normalize(s)
        if n and n not in seen:
            seen.add(n)
            seeds_u.append(s.strip())
    seeds = seeds_u

    if do_expand:
        kws = expand_keywords(seeds, cfg)
    else:
        kws = list(seeds)

    n_expanded = len(kws)
    n_from_tags = 0
    if do_mine and do_expand and _cfg(cfg, "expansion", "mine_tags", default=True):
        print(f"Mining tags from {len(seeds)} seeds…")
        tag_seen = {_normalize(k) for k in kws}
        for i, seed in enumerate(seeds, 1):
            tags = mine_tags_for_seed(manager, seed, cfg)
            added = 0
            for t in tags:
                if t not in tag_seen:
                    tag_seen.add(t)
                    kws.append(t)
                    added += 1
                    n_from_tags += 1
            print(f"  [{i}/{len(seeds)}] {seed}: +{added} tags")
            time.sleep(float(_cfg(cfg, "etsy", "sleep", default=0.35) or 0.35))

    kws = apply_exclusions(kws, cfg)
    kws = cap_keywords(kws, seeds, cfg)
    meta = {
        "n_seeds": len(seeds),
        "n_expanded": n_expanded,
        "n_from_tags": n_from_tags,
        "n_keywords": len(kws),
        "seeds": seeds,
    }
    return kws, meta


def main():
    ap = argparse.ArgumentParser(
        description="Config-driven product opportunity finder (Etsy + optional eRank)"
    )
    ap.add_argument("--config", default=str(DEFAULT_CONFIG), help="YAML config path")
    ap.add_argument("--seeds", nargs="*", default=[], help="Extra seed keywords")
    ap.add_argument("--file", help="Text file with seeds (one per line)")
    ap.add_argument("--no-expand", action="store_true", help="Do not apply modifiers")
    ap.add_argument("--no-mine", action="store_true", help="Do not mine Etsy tags")
    ap.add_argument("--expand-only", action="store_true", help="Print keyword list and exit")
    ap.add_argument("--max", type=int, default=None, help="Override max_keywords")
    ap.add_argument("--top", type=int, default=20, help="Print top N")
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=None)
    ap.add_argument("--erank", action="store_true", help="Run eRank Edge on top-N after Etsy rank")
    ap.add_argument("--no-erank", action="store_true", help="Force skip eRank")
    ap.add_argument("--erank-n", type=int, default=None, help="How many top keywords for eRank")
    ap.add_argument("--prefix", default=None, help="Output file prefix (under research/)")
    ap.add_argument("--no-shop", action="store_true", help="Skip shop coverage check")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path) if cfg_path.exists() else {}
    if not cfg:
        cfg = {"seeds": [], "expansion": {"max_keywords": 40, "mine_tags": False}}
    if args.max is not None:
        cfg.setdefault("expansion", {})["max_keywords"] = args.max
    if args.no_shop:
        cfg.setdefault("shop", {})["mark_owned"] = False

    print(f"Config: {cfg_path if cfg_path.exists() else '(defaults / CLI only)'}")
    manager = etsy_manager.EtsyManager()

    keywords, meta = build_keyword_list(
        cfg,
        seeds_cli=args.seeds,
        file_path=args.file,
        do_expand=not args.no_expand,
        do_mine=not args.no_mine,
        manager=manager,
    )
    meta["config_path"] = str(cfg_path)

    print(f"\nKeywords to scan: {len(keywords)}")
    if args.expand_only:
        for k in keywords:
            print(f"  {k}")
        out_list = BASE / "last_expanded_keywords.txt"
        out_list.write_text("\n".join(keywords) + "\n", encoding="utf-8")
        print(f"\nSaved {out_list}")
        return

    sample = args.sample or int(_cfg(cfg, "etsy", "sample", default=25) or 25)
    sleep = args.sleep if args.sleep is not None else float(_cfg(cfg, "etsy", "sleep", default=0.35) or 0.35)

    # Shop coverage phrases
    shop_phrases: list[str] = []
    if _cfg(cfg, "shop", "mark_owned", default=True):
        print("Loading shop coverage…")
        shop_phrases = load_shop_phrases(manager, cfg)

    owned_factor = float(_cfg(cfg, "shop", "owned_score_factor", default=0.55) or 0.55)

    # Etsy scan
    print(f"\nAnalyzing {len(keywords)} keywords via Etsy API…")
    print(f"{'KEYWORD':<42} {'LIST':>8} {'FAV~':>7} {'$~':>7} {'SCORE':>7}  NOTE")
    print("-" * 100)
    rows: list[dict] = []
    for i, kw in enumerate(keywords, 1):
        try:
            row = pf.analyze_keyword(manager, kw, sample=sample)
            row = apply_config_fit(row, cfg)
            row["source"] = "seed" if _normalize(kw) in {_normalize(s) for s in meta.get("seeds", [])} else "expanded"
            owned = is_owned(kw, shop_phrases) if shop_phrases else False
            row["already_in_shop"] = owned
            if owned:
                row["score_total"] = round(float(row.get("score_total") or 0) * owned_factor, 1)
                row["verdict"] = (row.get("verdict") or "") + " · IN SHOP"
            row["product_idea"] = pf.product_idea(row)
            rows.append(row)
            price = f"${row['median_price']:.2f}" if row.get("median_price") else "  —"
            note = "owned" if owned else ""
            print(
                f"{kw[:42]:<42} {row['listing_count']:>8} {row['avg_favorites']:>7.1f} "
                f"{price:>7} {row['score_total']:>7.1f}  {note}"
            )
        except Exception as e:
            print(f"{kw[:42]:<42} ERROR: {e}")
            rows.append({"keyword": kw, "error": str(e), "score_total": -1, "verdict": "ERROR"})
        if i < len(keywords):
            time.sleep(sleep)

    # POD cross from offline Printify catalog cache
    catalog = load_printify_catalog()
    if catalog:
        print(f"POD catalog cache: {catalog.get('blueprint_count')} blueprints "
              f"(shop {catalog.get('shop_id')})")
        rows = attach_pod(rows, catalog)
        meta["pod_catalog"] = "research/printify_catalog_scan.json"
        meta["pod_blueprint_count"] = catalog.get("blueprint_count")
    else:
        print("POD catalog cache missing — skip Printify cross")
        meta["pod_catalog"] = None

    # Optional eRank on top-N
    want_erank = args.erank or (
        _cfg(cfg, "erank", "enabled", default=False) and not args.no_erank
    )
    if want_erank:
        n = args.erank_n or int(_cfg(cfg, "erank", "top_n", default=15) or 15)
        ranked_tmp = sorted(
            [r for r in rows if r.get("score_total", -1) >= 0 and not r.get("already_in_shop")],
            key=lambda r: r.get("score_total", 0),
            reverse=True,
        )
        # include some owned high-scorers too for validation
        shortlist = [r["keyword"] for r in ranked_tmp[:n]]
        if not shortlist:
            shortlist = [
                r["keyword"]
                for r in sorted(rows, key=lambda r: r.get("score_total", 0), reverse=True)[:n]
                if r.get("score_total", -1) >= 0
            ]
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        prefix = args.prefix or _cfg(cfg, "output", "prefix", default="winners")
        try:
            erank_map = run_erank_top(shortlist, cfg, out_prefix=f"{prefix}_{stamp}")
            rows = [merge_erank_map(r, erank_map) for r in rows]
            # re-apply owned penalty + POD preferred boost after rescore
            for r in rows:
                if r.get("score_total", -1) < 0:
                    continue
                if r.get("already_in_shop"):
                    r["score_total"] = round(float(r["score_total"]) * owned_factor, 1)
                if r.get("pod_viable") and any(
                    p.get("preferred") for p in (r.get("pod_blueprints") or [])
                ):
                    r["score_total"] = round(float(r["score_total"]) + 2.0, 1)
                    r["pod_boost"] = 2.0
        except Exception as e:
            print(f"eRank step failed (Etsy results still saved): {e}")

    # Output
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    prefix = args.prefix or _cfg(cfg, "output", "prefix", default="winners")
    out_prefix = BASE / f"{prefix}_{stamp}"
    write_report(rows, out_prefix, cfg, meta)

    # Console top
    ok = sorted(
        [r for r in rows if r.get("score_total", -1) >= 0],
        key=lambda r: r.get("score_total", 0),
        reverse=True,
    )
    print("\n" + "=" * 90)
    print(f"TOP {min(args.top, len(ok))}")
    print("=" * 90)
    for i, r in enumerate(ok[: args.top], 1):
        shop = " [IN SHOP]" if r.get("already_in_shop") else ""
        er = ""
        if r.get("erank_searches") is not None:
            er = f"  eRank={r.get('erank_searches')} KD={r.get('erank_kd')}"
        print(
            f"#{i:2} {r.get('score_total', 0):5.1f}  {r['keyword']}{shop}\n"
            f"     list={r.get('listing_count')} fav~={r.get('avg_favorites')} "
            f"$~={r.get('median_price')}{er}\n"
            f"     {r.get('verdict')}"
        )


if __name__ == "__main__":
    main()
