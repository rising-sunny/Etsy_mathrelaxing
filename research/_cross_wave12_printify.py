"""Cross wave12 eRank POD keywords with Printify blueprints + proven costs."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
erank = json.loads((BASE / "wave12_pod_erank_bulk.json").read_text(encoding="utf-8"))
rows = erank if isinstance(erank, list) else erank.get("rows", [])

MAP = {
    "math wall art": ("poster", 282, "Matte Vertical Posters"),
    "physics wall art": ("poster", 282, "Matte Vertical Posters"),
    "science poster": ("poster", 282, "Matte Vertical Posters"),
    "math poster": ("poster", 282, "Matte Vertical Posters"),
    "fractal wall art": ("poster", 282, "Matte Vertical Posters"),
    "geometric wall art": ("poster", 282, "Matte Vertical Posters"),
    "bauhaus poster": ("poster", 282, "Matte Vertical Posters"),
    "equation poster": ("poster", 282, "Matte Vertical Posters"),
    "stem wall art": ("poster", 282, "Matte Vertical Posters"),
    "office wall art": ("poster", 282, "Matte Vertical Posters"),
    "math magnet": ("magnet", 428, "Magnets SPOKE"),
    "fridge magnet": ("magnet", 428, "Magnets SPOKE"),
    "science magnet": ("magnet", 428, "Magnets SPOKE"),
    "fractal magnet": ("magnet", 428, "Magnets SPOKE"),
    "teacher magnet": ("magnet", 428, "Magnets SPOKE"),
    "teacher tote bag": ("tote", 5113, "Matte Carryall Tote"),
    "canvas tote bag": ("tote", 5113, "Matte Carryall Tote"),
    "tote bag": ("tote", 5113, "Matte Carryall Tote"),
    "math tote bag": ("tote", 5113, "Matte Carryall Tote"),
    "stem tote bag": ("tote", 5113, "Matte Carryall Tote"),
    "halloween doormat": ("doormat", 1346, "Doormat 24x16"),
    "funny doormat": ("doormat", 1346, "Doormat 24x16"),
    "welcome doormat": ("doormat", 1346, "Doormat 24x16"),
    "custom doormat": ("doormat", 1346, "Doormat 24x16"),
    "bookish stickers": ("sticker", 600, "Die-Cut Stickers"),
    "kindle stickers": ("sticker", 600, "Die-Cut Stickers"),
    "math stickers": ("sticker", 600, "Die-Cut Stickers"),
    "science stickers": ("sticker", 600, "Die-Cut Stickers"),
    "die cut stickers": ("sticker", 600, "Die-Cut Stickers"),
    "mouse pad": ("mousepad", 582, "Mouse Pad"),
    "math mouse pad": ("mousepad", 582, "Mouse Pad"),
    "gaming mouse pad": ("mousepad", 582, "Mouse Pad"),
    "desk mat": ("mousepad", 582, "Mouse Pad / desk"),
    "teacher sweatshirt": ("apparel", None, "apparel blank TBD"),
    "science shirt": ("apparel", None, "apparel blank TBD"),
    "math teacher gift": ("gift_multi", 282, "poster/magnet/tote multi"),
    "stem gift": ("gift_multi", 428, "magnet+poster multi"),
    "engineer gift": ("gift_multi", 282, "poster multi"),
    "hardcover journal": ("journal", 485, "Hardcover Journal Matte"),
    "custom journal": ("journal", 485, "Hardcover Journal Matte"),
    "science mug": ("mug", 635, "Accent Coffee Mug"),
    "math mug": ("mug", 635, "Accent Coffee Mug"),
    "custom mug": ("mug", 635, "Accent Coffee Mug"),
}

COSTS = {
    "poster": (5.92, 15.0, "11x14 proven"),
    "magnet": (2.82, 8.99, "3in proven"),
    "tote": (None, 24.0, "est retail"),
    "doormat": (None, 39.0, "est retail"),
    "sticker": (None, 8.0, "est pack"),
    "mousepad": (None, 16.0, "est"),
    "journal": (None, 20.0, "est"),
    "mug": (None, 18.0, "est"),
    "apparel": (None, 28.0, "est"),
    "gift_multi": (2.82, 12.0, "magnet/poster gift"),
}

BRAND = {
    "poster": 10,
    "magnet": 9,
    "gift_multi": 8,
    "mousepad": 7,
    "sticker": 7,
    "tote": 6,
    "journal": 6,
    "mug": 5,
    "doormat": 4,
    "apparel": 3,
}

GENERIC_TRAP = {
    "tote bag",
    "mouse pad",
    "desk mat",
    "fridge magnet",
    "custom mug",
    "custom journal",
    "custom doormat",
    "gaming mouse pad",
}


def erank_score(r: dict) -> float:
    avg = r.get("searches") or 0
    latest = r.get("latest_month_searches")
    s = latest if latest else avg
    mom = r.get("momentum") or 1
    if mom >= 1.15:
        s = s * 1.1
    elif mom and mom <= 0.75:
        s = s * 0.9
    kd = r.get("kd")
    demand = min(100.0, (s**0.5) * 1.2) if s else 0.0
    ease = max(0.0, 100 - (kd if kd is not None else 50))
    return demand * 0.45 + ease * 0.45


cross = []
for r in rows:
    kw = (r.get("keyword") or "").strip().lower()
    m = MAP.get(kw)
    if not m:
        for k, v in MAP.items():
            if k in kw or kw in k:
                m = v
                break
    if not m:
        fam, bp, blank = "unknown", None, "?"
        brand = 2
    else:
        fam, bp, blank = m
        brand = BRAND.get(fam, 3)

    es = erank_score(r)
    latest = r.get("latest_month_searches") or 0
    kd = r.get("kd")
    mom = r.get("momentum") or 0
    composite = brand * 8 + es
    if mom and mom >= 1.2:
        composite += 8
    if kd is not None and kd <= 70:
        composite += 6
    if latest and latest >= 2000:
        composite += 5
    if kw in GENERIC_TRAP and brand < 8:
        composite -= 12

    cost, retail, note = COSTS.get(fam, (None, None, ""))
    margin = (retail - cost) if (retail is not None and cost is not None) else None
    cross.append(
        {
            "keyword": r.get("keyword"),
            "latest": latest,
            "avg": r.get("searches"),
            "mom": mom,
            "comp": r.get("competition"),
            "kd": r.get("kd"),
            "erank_score": round(es, 1),
            "family": fam,
            "blueprint": bp,
            "blank": blank,
            "brand_fit": brand,
            "composite": round(composite, 1),
            "cost": cost,
            "retail": retail,
            "margin": round(margin, 2) if margin is not None else None,
            "note": note,
        }
    )

cross.sort(key=lambda x: -x["composite"])

lines: list[str] = []
lines.append("# Wave 12 — eRank × Printify POD cross\n\n")
lines.append("**Date:** 2026-07-18  \n")
lines.append("**eRank:** `wave12_pod_erank_bulk.json` (43 keywords, Jun 2026)  \n")
lines.append("**Printify shop:** 28170054 (Etsy-connected)  \n")
lines.append("**Catalog:** 1797 blueprints · 8 existing products  \n\n")
lines.append(
    "Composite ≈ brand fit (MathRelaxing STEM) + eRank demand/ease "
    "+ rising/low-KD bonuses − generic volume traps.\n\n"
)

lines.append("## Full cross table (ranked)\n\n")
lines.append(
    "| # | Keyword | Jun | Mom | KD | Comp | Brand | BP | Blank | Comp. |\n"
)
lines.append("|---|---------|----:|----:|---:|-----:|------:|---:|-------|------:|\n")
for i, c in enumerate(cross, 1):
    kd = c["kd"] if c["kd"] is not None else "—"
    comp = int(c["comp"]) if c["comp"] else "—"
    bp = c["blueprint"] if c["blueprint"] else "—"
    mom = c["mom"] if c["mom"] else "—"
    lines.append(
        f"| {i} | {c['keyword']} | {c['latest'] or '—'} | {mom} | {kd} | "
        f"{comp} | {c['brand_fit']} | {bp} | {c['blank'][:28]} | {c['composite']} |\n"
    )

fam: dict = defaultdict(
    lambda: {"kws": [], "best_latest": 0, "best_mom": 0, "min_kd": 999, "best_comp": 0}
)
for c in cross:
    f = c["family"]
    fam[f]["kws"].append(c)
    if (c["latest"] or 0) > fam[f]["best_latest"]:
        fam[f]["best_latest"] = c["latest"] or 0
    if (c["mom"] or 0) > fam[f]["best_mom"]:
        fam[f]["best_mom"] = c["mom"] or 0
    if c["kd"] is not None and c["kd"] < fam[f]["min_kd"]:
        fam[f]["min_kd"] = c["kd"]
    if c["composite"] > fam[f]["best_comp"]:
        fam[f]["best_comp"] = c["composite"]

lines.append("\n## By Printify family (aggregated)\n\n")
lines.append(
    "| Family | Blueprint | Best Jun | Best Mom | Best KD | Top composite | Best keyword |\n"
)
lines.append("|--------|-----------|---------:|---------:|--------:|--------------:|--------------|\n")
for f, d in sorted(fam.items(), key=lambda x: -x[1]["best_comp"]):
    best = max(d["kws"], key=lambda x: x["composite"])
    bp = best["blueprint"] or "—"
    kd = d["min_kd"] if d["min_kd"] < 999 else "—"
    lines.append(
        f"| {f} | {bp} | {d['best_latest']} | {d['best_mom']} | {kd} | "
        f"{d['best_comp']} | {best['keyword']} |\n"
    )

lines.append("\n## Recommended playbook (cross-validated)\n\n")
lines.append("| Priority | Action | eRank signal | Printify | Margin proof |\n")
lines.append("|---------:|--------|--------------|----------|--------------|\n")
lines.append(
    "| 1 | **STEM wall art posters** (equation plates → POD) | "
    "bauhaus poster mom **1.54** KD **68**; geometric wall art mom **2.15**; "
    "physics/math wall art cluster | **bp 282** | COGS $5.92 → retail $15–35 |\n"
)
lines.append(
    "| 2 | **Math/science magnets** | fridge/math/fractal magnet niche | "
    "**bp 428** | COGS $2.82–4.83 → $9–16 |\n"
)
lines.append(
    "| 3 | **Teacher STEM tote** (not generic tote) | teacher tote bag Jun **3300** "
    "mom **2.13** KD **75** | **bp 5113** | est retail $22–28 |\n"
)
lines.append(
    "| 4 | **Halloween / funny doormat** (1–2 SKUs) | halloween doormat mom **1.43** "
    "KD **62** | **bp 1346** | higher COGS; seasonal |\n"
)
lines.append(
    "| 5 | **Bookish/Kindle + math stickers** | bookish 1390 KD 71; kindle 1210 KD 77 | "
    "**bp 600** | packs $6–12 |\n"
)
lines.append(
    "| 6 | **STEM mouse pad** (math design, not desk mat alone) | mouse pad 6.7k vol | "
    "**bp 582** | est $14–18 |\n"
)
lines.append(
    "| 7 | Journal / mug | custom journal mom 1.14 KD 75 — later | 485 / 635 | later |\n"
)

lines.append("\n### Avoid / deprioritize\n")
lines.append(
    "- **tote bag** generic (11.7k Jun, KD 79) — ocean; use *teacher/math/STEM* angle only\n"
)
lines.append(
    "- **desk mat / mouse pad** pure volume — need STEM art to rank against giants\n"
)
lines.append("- **teacher sweatshirt / apparel** KD 100 traps\n")
lines.append("- **office wall art** KD 100 without niche\n")

lines.append("\n### Immediate product matrix\n\n")
lines.append(
    "| Design asset (already have) | Poster 282 | Magnet 428 | Tote 5113 | Sticker 600 |\n"
)
lines.append(
    "|----------------------------|:----------:|:----------:|:---------:|:-----------:|\n"
)
lines.append("| Equation plates (Fourier, Euler…) | ★ | ★ mini | — | ★ mini pack |\n")
lines.append("| Bauhaus / geometric set | ★ | ○ | ○ | — |\n")
lines.append("| Fractal Julia / Mandelbrot | ★ | ★ (pilot done) | — | ○ |\n")
lines.append("| Reader OS bookish | — | — | — | ★ |\n")
lines.append("| Teacher STEM typography | ○ | ○ | ★ | — |\n")
lines.append("\n★ = launch now · ○ = optional second wave\n")

lines.append("\n## Proven shop costs (from live Printify products)\n\n")
lines.append("| Blank | Size | Cost | Example retail | Profit |\n")
lines.append("|-------|------|-----:|---------------:|-------:|\n")
lines.append("| Poster 282 | 11×14 | $5.92 | $15.00 | $9.08 |\n")
lines.append("| Poster 282 | 18×18 | $10.63 | $34.99 | $24.36 |\n")
lines.append("| Magnet 428 | 3×3 | $2.82 | $8.99 | $6.17 |\n")
lines.append("| Magnet 428 | 6×6 | $4.83 | $15.99 | $11.16 |\n")

out = BASE / "wave12_pod_cross_report.md"
out.write_text("".join(lines), encoding="utf-8")
(BASE / "wave12_pod_cross.json").write_text(
    json.dumps(cross, indent=2), encoding="utf-8"
)
print("Wrote", out)
print("\nTOP 12 composite:")
for c in cross[:12]:
    print(
        f"  {c['composite']:5.1f}  jun={c['latest']!s:>6} mom={c['mom']} "
        f"kd={c['kd']}  [{c['family']}]  {c['keyword']}"
    )
