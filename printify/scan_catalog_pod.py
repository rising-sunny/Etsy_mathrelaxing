"""
scan_catalog_pod.py — Explore Printify catalog + rank POD blueprints for MathRelaxing.

Requires printify/.env (PRINTIFY_TOKEN, PRINTIFY_ETSY_SHOP_ID).

  python printify/scan_catalog_pod.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

# allow import of printify_publish from this folder
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import printify_publish as pp  # noqa: E402

OUT = HERE.parent / "research" / "printify_catalog_scan.json"
OUT_MD = HERE.parent / "research" / "printify_pod_opportunity_report.md"

# Keywords from eRank waves that map to POD blanks (wave 10/11 + STEM brand)
ERANK_POD = [
    # from wave11 physical lowcost
    {"kw": "teacher tote bag", "jun": 3300, "mom": 2.13, "kd": 75, "model": "tote"},
    {"kw": "halloween doormat", "jun": 1070, "mom": 1.43, "kd": 62, "model": "doormat"},
    {"kw": "bookish stickers", "jun": 1390, "mom": 0.52, "kd": 71, "model": "sticker"},
    {"kw": "kindle stickers", "jun": 1210, "mom": 0.52, "kd": 77, "model": "sticker"},
    {"kw": "baby milestone cards", "jun": 1170, "mom": 1.00, "kd": 53, "model": "card"},
    {"kw": "nurse shirt", "jun": 6770, "mom": 1.06, "kd": 84, "model": "tee"},
    {"kw": "throw pillow cover", "jun": 1200, "mom": 1.18, "kd": 100, "model": "pillow"},
    # wave10 / earlier POD-ish
    {"kw": "teacher sweatshirt", "jun": None, "mom": None, "kd": None, "model": "sweatshirt"},
    {"kw": "funny doormat", "jun": None, "mom": None, "kd": None, "model": "doormat"},
    {"kw": "nursery wall art", "jun": None, "mom": None, "kd": None, "model": "poster"},
    {"kw": "math magnet", "jun": 285, "mom": None, "kd": None, "model": "magnet"},  # competitor count from prior scan
    # brand-fit STEM
    {"kw": "math wall art", "jun": None, "mom": None, "kd": None, "model": "poster"},
    {"kw": "physics wall art", "jun": None, "mom": None, "kd": None, "model": "poster"},
    {"kw": "science poster", "jun": None, "mom": None, "kd": None, "model": "poster"},
    {"kw": "stem gift", "jun": None, "mom": None, "kd": None, "model": "gift"},
]

# Map blueprint title patterns -> product family
FAMILY_PATTERNS = [
    (r"poster|print|canvas|framed", "poster_print"),
    (r"magnet", "magnet"),
    (r"tote|bag", "tote_bag"),
    (r"doormat|door mat|welcome mat", "doormat"),
    (r"sticker|decal", "sticker"),
    (r"pillow|cushion", "pillow"),
    (r"mug|tumbler|bottle", "drinkware"),
    (r"shirt|tee|t-shirt|hoodie|sweatshirt|tank", "apparel"),
    (r"phone case|iphone|samsung", "phone_case"),
    (r"notebook|journal", "notebook"),
    (r"calendar", "calendar"),
    (r"blanket|towel", "textile_home"),
    (r"sock", "socks"),
    (r"hat|cap|beanie", "headwear"),
    (r"mouse pad|mousepad", "mousepad"),
    (r"puzzle", "puzzle"),
    (r"ornament", "ornament"),
    (r"clock", "clock"),
    (r"card|postcard", "card"),
]


def family_of(title: str) -> str:
    t = (title or "").lower()
    for pat, fam in FAMILY_PATTERNS:
        if re.search(pat, t):
            return fam
    return "other"


def brand_fit(title: str, fam: str) -> int:
    """0-10 how well this blank fits MathRelaxing (math/physics/STEM art shop)."""
    t = (title or "").lower()
    score = 0
    # strong fit families
    if fam in ("poster_print", "magnet", "mousepad", "notebook", "puzzle", "clock"):
        score += 5
    if fam in ("tote_bag", "sticker", "pillow", "apparel", "drinkware"):
        score += 3
    if fam in ("doormat", "card", "textile_home"):
        score += 2
    # quality signals
    if any(k in t for k in ("matte", "premium", "gallery", "enhanced", "giclee", "canvas")):
        score += 1
    if any(k in t for k in ("kids", "baby", "toddler")) and fam == "apparel":
        score -= 1
    # avoid oversaturated generic blanks slightly
    if re.search(r"unisex.*tee|heavy cotton tee|bella.*canvas 3001", t):
        score -= 0  # still usable for STEM tees
    return max(0, min(10, score))


def main():
    print("=== Printify shops ===")
    shops = pp._req("GET", "/shops.json")
    for s in shops:
        mark = " <<<" if str(s["id"]) == str(pp.SHOP_ID) else ""
        print(f"  {s['id']}  {s.get('title')}  channel={s.get('sales_channel')}{mark}")

    print("\n=== Catalog blueprints ===")
    blueprints = pp._req("GET", "/catalog/blueprints.json")
    if isinstance(blueprints, dict):
        blueprints = blueprints.get("data") or blueprints.get("blueprints") or []
    print(f"  total blueprints: {len(blueprints)}")

    rows = []
    by_fam = defaultdict(list)
    for b in blueprints:
        title = b.get("title") or ""
        fam = family_of(title)
        fit = brand_fit(title, fam)
        row = {
            "id": b.get("id"),
            "title": title,
            "brand": b.get("brand"),
            "model": b.get("model"),
            "family": fam,
            "brand_fit": fit,
            "images": (b.get("images") or [])[:1],
        }
        rows.append(row)
        by_fam[fam].append(row)

    # Known good pilots already in code
    known = {
        282: "Matte Vertical Posters (pilot posters)",
        428: "Magnets / SPOKE (pilot fractal magnet)",
    }

    # Deep-dive high-fit families: get providers + sample variant costs
    priority_fams = [
        "poster_print", "magnet", "tote_bag", "doormat", "sticker",
        "pillow", "mousepad", "apparel", "drinkware", "notebook",
    ]
    deep = []
    # pick top blueprints per family by brand_fit then title relevance
    for fam in priority_fams:
        cands = sorted(by_fam.get(fam, []), key=lambda r: (-r["brand_fit"], r["title"]))
        # take up to 4 per family, prefer known IDs first
        picked = []
        for r in cands:
            if r["id"] in known:
                picked.append(r)
        for r in cands:
            if r not in picked:
                picked.append(r)
            if len(picked) >= 4:
                break
        for r in picked:
            bid = r["id"]
            try:
                providers = pp._req("GET", f"/catalog/blueprints/{bid}/print_providers.json")
                if isinstance(providers, dict):
                    providers = providers.get("data") or []
                time.sleep(0.35)  # catalog rate limit 100/min
            except Exception as e:
                print(f"  providers fail blueprint {bid}: {e}")
                continue
            if not providers:
                continue
            # prefer Printify Choice (99) or first
            prov = next((p for p in providers if p.get("id") == 99), providers[0])
            pid = prov["id"]
            try:
                variants = pp._req(
                    "GET",
                    f"/catalog/blueprints/{bid}/print_providers/{pid}/variants.json",
                )
                time.sleep(0.35)
            except Exception as e:
                print(f"  variants fail {bid}/{pid}: {e}")
                continue
            # variants structure: {"id":..., "title":..., "variants":[...]} or list
            if isinstance(variants, dict):
                vlist = variants.get("variants") or []
                vtitle = variants.get("title") or r["title"]
            else:
                vlist = variants
                vtitle = r["title"]
            costs = []
            samples = []
            for v in vlist[:80]:
                if not isinstance(v, dict):
                    continue
                cost = v.get("cost")  # may be absent on catalog
                if cost is None and "placeholders" in v:
                    cost = None
                # some APIs put price in options
                c = v.get("cost")
                if c is not None:
                    costs.append(c / 100 if c > 50 else c)  # cents vs dollars heuristic
                if len(samples) < 6:
                    samples.append({
                        "id": v.get("id"),
                        "title": v.get("title"),
                        "options": v.get("options"),
                        "cost": v.get("cost"),
                    })
            # shipping
            ship = None
            try:
                ship = pp._req(
                    "GET",
                    f"/catalog/blueprints/{bid}/print_providers/{pid}/shipping.json",
                )
                time.sleep(0.25)
            except Exception:
                pass
            deep.append({
                "blueprint_id": bid,
                "title": r["title"],
                "brand": r["brand"],
                "family": fam,
                "brand_fit": r["brand_fit"],
                "provider_id": pid,
                "provider_title": prov.get("title"),
                "decoration_methods": prov.get("decoration_methods"),
                "variant_count": len(vlist) if isinstance(vlist, list) else 0,
                "sample_variants": samples,
                "cost_min": min(costs) if costs else None,
                "cost_max": max(costs) if costs else None,
                "shipping": ship,
                "known_pilot": known.get(bid),
            })
            print(f"  deep {fam:14} bp={bid:5} {r['title'][:40]:40} prov={prov.get('title')} vars={len(vlist) if isinstance(vlist,list) else '?'}")

    # Existing shop products
    products = []
    try:
        page = 1
        while True:
            res = pp._req("GET", f"/shops/{pp.SHOP_ID}/products.json?limit=50&page={page}")
            if isinstance(res, dict):
                batch = res.get("data") or []
                products.extend(batch)
                if page >= (res.get("last_page") or 1):
                    break
            else:
                products = res if isinstance(res, list) else []
                break
            page += 1
            time.sleep(0.2)
    except Exception as e:
        print(f"  products list: {e}")

    payload = {
        "shop_id": pp.SHOP_ID,
        "blueprint_count": len(rows),
        "family_counts": {k: len(v) for k, v in sorted(by_fam.items(), key=lambda x: -len(x[1]))},
        "blueprints": rows,
        "deep_dive": deep,
        "existing_products": [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "blueprint_id": p.get("blueprint_id"),
                "visible": p.get("visible"),
            }
            for p in products[:50]
        ],
        "erank_pod_context": ERANK_POD,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}")

    # Markdown report
    lines = []
    lines.append("# Printify POD opportunity scan (API + eRank context)\n")
    lines.append(f"**Shop:** {pp.SHOP_ID} (Etsy-connected)  \n")
    lines.append(f"**Blueprints in catalog:** {len(rows)}  \n")
    lines.append(f"**Existing Printify products:** {len(products)}\n")
    lines.append("\n## Family counts (full catalog)\n")
    lines.append("| Family | Count |\n|--------|------:|\n")
    for fam, n in sorted(payload["family_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"| {fam} | {n} |\n")

    lines.append("\n## eRank POD signals (prior waves)\n")
    lines.append("| Keyword | Jun | Mom | KD | Blank model |\n|---------|----:|----:|---:|-------------|\n")
    for e in ERANK_POD:
        jun = e["jun"] if e["jun"] is not None else "—"
        mom = e["mom"] if e["mom"] is not None else "—"
        kd = e["kd"] if e["kd"] is not None else "—"
        lines.append(f"| {e['kw']} | {jun} | {mom} | {kd} | {e['model']} |\n")

    lines.append("\n## Deep-dive blueprints (costs / providers)\n")
    for d in sorted(deep, key=lambda x: (-x["brand_fit"], x["family"], x["title"])):
        cmin, cmax = d.get("cost_min"), d.get("cost_max")
        cost_s = "n/a on catalog"
        if cmin is not None:
            cost_s = f"${cmin:.2f}" + (f"–${cmax:.2f}" if cmax != cmin else "")
        pilot = f" · **PILOT** {d['known_pilot']}" if d.get("known_pilot") else ""
        lines.append(
            f"\n### {d['title']}  \n"
            f"- blueprint **{d['blueprint_id']}** · family `{d['family']}` · fit **{d['brand_fit']}/10**{pilot}  \n"
            f"- provider **{d['provider_id']}** {d.get('provider_title')} · methods {d.get('decoration_methods')}  \n"
            f"- variants: {d.get('variant_count')} · cost sample: {cost_s}  \n"
        )
        if d.get("sample_variants"):
            lines.append("  Sample variants:  \n")
            for v in d["sample_variants"][:4]:
                lines.append(f"  - `{v.get('id')}` {v.get('title')} cost={v.get('cost')}  \n")

    lines.append("\n## Recommended winners for MathRelaxing\n")
    lines.append(
        """
| Priority | Product blank | Why (eRank + brand) | Blueprint candidates | Suggested retail |
|---------:|---------------|---------------------|----------------------|------------------|
| 1 | **Matte posters** (multi-size) | math/physics wall art ranks (#1 Maxwell, #3 Ulam); you already have digital masters @ 300 dpi | **282** (in code) | $18–35 |
| 2 | **Fridge magnets** | prior scan: math magnet underserved; low COGS, gift impulse | **428** (in code) | $9–16 |
| 3 | **Tote bags** | teacher tote bag 3.3k Jun, mom 2.13, KD 75 — best apparel-adjacent | tote blueprints below | $22–28 |
| 4 | **Doormats** (seasonal) | halloween doormat KD 62, mom 1.43 — prep for fall | doormat blueprints | $35–45 |
| 5 | **Mousepads / stickers** | desk STEM + bookish/kindle sticker demand | sticker/mousepad bps | $12–18 / $6–12 |
| 6 | **Apparel STEM niche** | only with strong design system (not generic funny tee) | tees/sweatshirts | $24–35 |

### What NOT to chase first
- Generic dog/cat mom tees (KD 100)
- Generic throw pillows without art system
- High-weight canvases until poster margins proven

### Next actions
1. Confirm tote + doormat blueprint IDs from deep dive above
2. Pick 1 design system (equation plate or fractal) → mockup on poster + magnet + tote
3. Create products via API (Printify only) → publish as Etsy **draft** after review
"""
    )
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
