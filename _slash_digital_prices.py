"""
Slash digital listing prices as low as sensible for a new shop.
- Floor: $1.99 (don't race to $0.99)
- Singles / simple PDFs: $2.99
- Stickers / planners / LOR: $2.99
- iPad bundles: $3.99
- Multi-print sets / binders: $3.99
- Premium multi-file kits (resume atelier, wedding): $4.99
Updates Etsy (active + draft) + products_catalog.py
"""
from __future__ import annotations

import re
from pathlib import Path

from etsy_manager import EtsyManager
from products_catalog import PRODUCTS

# ── Aggressive catalog overrides (key → price) ──────────────────────────────
CATALOG_PRICES: dict[str, float] = {
    # Single / scientific plates
    "schrodinger_equation_print": 2.99,
    "unit_circle_print": 2.99,
    # Print sets
    "bauhaus_print_set": 3.99,
    "morris_botanical_print_set": 3.99,
    "sage_neutral_print_set": 3.99,
    "cs_poster_set": 3.99,
    "happy_chemicals_prints": 3.99,
    # Stickers
    "reader_os_stickers": 2.99,
    # Coloring PDFs
    "fractal_flora_pdf": 2.99,
    "sacred_geometry_pdf": 2.99,
    "hyperbolic_gardens_pdf": 2.99,
    "mathematical_tangle_art_pdf": 2.99,
    "sacred_harmonics_pdf": 2.99,
    "neural_network_pdf": 2.99,
    "voronoi_gardens_pdf": 2.99,
    "islamic_geometry_pdf": 2.99,
    "celtic_knot_pdf": 2.99,
    "spiral_tilings_pdf": 2.99,
    # iPad / interactive
    "fractal_flora_ipad": 3.99,
    "sacred_geometry_ipad": 3.99,
    "islamic_geometry_ipad": 3.99,
    "celtic_knot_ipad": 3.99,
    "voronoi_gardens_ipad": 3.99,
    "spiral_tilings_ipad": 3.99,
    # Animations / loops
    "thomas_attractor": 2.99,
    "julia_morph_01": 2.99,
    "voronoi_cell_garden": 2.99,
    # Planners / notebooks
    "stem_focus_planner": 2.99,
    "stem_notebook": 2.99,
    "stem_lab_notebook": 2.99,
    "quantified_self_planner": 2.99,
    # Career / life kits
    "editorial_resume_kit": 3.99,
    "atelier_resume_kit": 4.99,
    "lor_template_pack": 2.99,
    "emergency_binder": 3.99,
    "geometric_wedding_suite": 4.99,
}


def money(price_obj) -> float:
    if price_obj is None:
        return 0.0
    if isinstance(price_obj, dict):
        return float(price_obj.get("amount", 0)) / float(price_obj.get("divisor", 100) or 100)
    return float(price_obj)


def price_from_title(title: str, current: float) -> float:
    """Heuristic for live listings not (only) in catalog."""
    t = (title or "").lower()

    # Already at or under absolute floor
    if current <= 1.99 and current > 0:
        return current  # keep $1.50 graph paper etc.

    # Palettes / tiny add-ons
    if "palette" in t or "swatch" in t:
        return 1.99

    # Premium multi-file kits
    if "atelier" in t or "luxury resume" in t:
        return 4.99
    if "wedding" in t or "seating" in t:
        return 4.99
    if "resume" in t or "cv " in t or "cover letter" in t:
        return 3.99

    # Sets / multipacks
    if re.search(r"set of\s*\d|print set|poster set|gallery|bundle of", t):
        return 3.99
    if "set |" in t or "set of" in t or t.startswith("set "):
        return 3.99
    if "6 posters" in t or "6 designs" in t or "six " in t:
        return 3.99

    # Stickers
    if "sticker" in t:
        return 2.99

    # iPad / interactive coloring
    if "ipad" in t or "interactive" in t or "goodnotes" in t and "color" in t:
        return 3.99

    # Planners / notebooks
    if "planner" in t or "notebook" in t or "binder" in t:
        return 2.99 if "emergency" not in t else 3.99
    if "emergency" in t or "ice " in t:
        return 3.99

    # LOR / letter
    if "recommendation" in t or "letter of" in t:
        return 2.99

    # Coloring books PDFs
    if "coloring" in t or "color by number" in t:
        return 2.99

    # Loops / animation
    if "loop" in t or "animation" in t or "seamless" in t:
        return 2.99

    # Single wall art / posters
    if any(k in t for k in ("wall art", "poster", "print |", "art print", "equation")):
        return 2.99

    # Default aggressive
    if current >= 8.0:
        return 3.99
    if current >= 5.0:
        return 2.99
    if current >= 3.5:
        return 2.99
    return max(1.99, min(current, 2.99))


def fetch_state(m: EtsyManager, shop: int, state: str) -> list[dict]:
    offset = 0
    all_ = []
    while True:
        ep = f"/shops/{shop}/listings?state={state}&limit=100&offset={offset}"
        r = m.make_request("GET", ep)
        results = r.get("results") or []
        all_.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return all_


def is_digital(it: dict) -> bool:
    typ = (it.get("listing_type") or it.get("type") or "").lower()
    return typ in ("download", "digital", "downloadable")


def catalog_lid_map() -> dict[int, tuple[str, float]]:
    """listing_id → (key, new_price)."""
    m = {}
    for key, price in CATALOG_PRICES.items():
        p = PRODUCTS.get(key)
        if not p:
            continue
        lid = p.get("listing_id")
        if lid:
            m[int(lid)] = (key, price)
    return m


def update_catalog_file():
    path = Path(__file__).resolve().parent / "products_catalog.py"
    text = path.read_text(encoding="utf-8")
    # For each product key, replace the price line near the key definition.
    # Safer: parse by key block — replace "price": X or "price": X.XX after key
    for key, new_price in CATALOG_PRICES.items():
        # Match product block starting with "key": {
        # then first "price": number within next ~30 lines
        pattern = re.compile(
            rf'("{re.escape(key)}"\s*:\s*\{{[\s\S]*?"price"\s*:\s*)([0-9]+(?:\.[0-9]+)?)',
            re.MULTILINE,
        )

        def repl(match, np=new_price):
            # only first price after key
            return f"{match.group(1)}{np}"

        new_text, n = pattern.subn(repl, text, count=1)
        if n:
            text = new_text
            print(f"  catalog {key} → ${new_price:.2f}")
        else:
            # try alternate spacing: "price":       4.99,
            pattern2 = re.compile(
                rf'("{re.escape(key)}"\s*:\s*\{{[\s\S]{{0,800}}?"price"\s*:\s*)([0-9]+(?:\.[0-9]+)?)',
            )
            new_text, n = pattern2.subn(repl, text, count=1)
            if n:
                text = new_text
                print(f"  catalog {key} → ${new_price:.2f}")
            else:
                print(f"  WARN: could not patch catalog price for {key}")
    path.write_text(text, encoding="utf-8")


def main():
    print("=== 1) Patch products_catalog.py ===")
    update_catalog_file()

    lid_map = catalog_lid_map()
    m = EtsyManager()
    shop = m.get_shop_id()

    changed = []
    skipped = []
    errors = []

    for state in ("active", "draft"):
        items = fetch_state(m, shop, state)
        dig = [it for it in items if is_digital(it)]
        print(f"\n=== {state}: {len(dig)} digital ===")
        for it in dig:
            lid = int(it["listing_id"])
            title = it.get("title") or ""
            old = money(it.get("price"))
            if lid in lid_map:
                key, new = lid_map[lid]
            else:
                key, new = None, price_from_title(title, old)

            # never raise
            if new >= old - 0.001:
                skipped.append((lid, old, new, title[:50], "no-cut"))
                continue

            try:
                m.update_listing_price(lid, new)
                # verify
                check = m.make_request("GET", f"/listings/{lid}")
                pobj = check.get("price")
                got = (
                    float(pobj["amount"]) / float(pobj["divisor"])
                    if isinstance(pobj, dict)
                    else float(pobj)
                )
                if abs(got - new) > 0.02:
                    errors.append((lid, f"verify got {got} want {new}", title[:40]))
                    print(f"  WARN {lid}: wanted ${new:.2f} got ${got:.2f}")
                else:
                    changed.append((lid, old, new, title[:55], key or "heuristic"))
                    print(f"  ${old:.2f} → ${got:.2f}  [{key or 'heur'}]  {title[:50]}")
            except Exception as e:
                errors.append((lid, str(e), title[:40]))
                print(f"  ERR {lid}: {e}")

    print("\n=== SUMMARY ===")
    print(f"  updated: {len(changed)}")
    print(f"  skipped (already low / no cut): {len(skipped)}")
    print(f"  errors: {len(errors)}")
    if changed:
        drops = [o - n for _, o, n, _, _ in changed]
        print(f"  avg cut: ${sum(drops)/len(drops):.2f}")
        print(f"  biggest cut: ${max(drops):.2f}")
        # new distribution
        news = sorted(n for _, _, n, _, _ in changed)
        print(f"  new prices among updated: min=${news[0]:.2f} max=${news[-1]:.2f} median=${news[len(news)//2]:.2f}")


if __name__ == "__main__":
    main()
