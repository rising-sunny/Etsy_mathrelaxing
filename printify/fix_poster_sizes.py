"""
fix_poster_sizes.py — give POD poster listings a proper size ladder.

Some posters were published with only ONE size enabled (11x14), so the Etsy
listing showed no size selector even though the description promised "multiple
sizes". This enables a standard 4-size ladder and re-syncs it to Etsy.

KEY TECHNIQUE — variants-only publish:
    Printify's normal publish pushes title, description, images AND tags, which
    would overwrite any customization done on the Etsy listing after publishing
    (e.g. a hand-edited title). We publish with everything False except
    variants, so only the size options sync and the custom Etsy copy is left
    untouched. Verified: title / description / tags / images stay intact.

Only applies to portrait posters whose design is placed for the ladder's aspect
ratios (checked via print-area coverage). Square-format posters are skipped.

    python fix_poster_sizes.py --scan                 # list single-size posters
    python fix_poster_sizes.py <product_id> [<id>...] # fix specific products
    python fix_poster_sizes.py --auto                 # fix all single-size ones
"""
import sys
import time

import printify_publish as P

POSTER_BLUEPRINT = 282  # matte poster blueprint used by this shop

# variant id -> retail price (cents). Same provider as the 11x14 base variant.
LADDER = {
    43135: 1500,   # 11" x 14"  (4:5)
    43141: 2400,   # 16" x 20"  (4:5)
    43144: 2600,   # 18" x 24"  (3:4)
    43150: 3900,   # 24" x 36"  (2:3)
}


def _rq(fn, *a, **k):
    for att in range(4):
        try:
            return fn(*a, **k)
        except Exception as e:  # noqa: BLE001 — transient Printify/network errors
            print(f"   retry {att + 1}: {str(e)[:60]}")
            time.sleep(2 ** att)
    raise RuntimeError("failed after retries")


def _all_products():
    out, page = [], 1
    while True:
        r = _rq(P._req, "GET", f"/shops/{P.SHOP_ID}/products.json?limit=50&page={page}")
        data = r.get("data", []) if isinstance(r, dict) else r
        out += data
        if len(data) < 50:
            return out
        page += 1


def publish_variants_only(pid):
    """Re-sync ONLY the size variants to the connected Etsy listing."""
    return _rq(P._req, "POST", f"/shops/{P.SHOP_ID}/products/{pid}/publish.json",
               {"title": False, "description": False, "images": False, "variants": True,
                "tags": False, "keyFeatures": False, "shipping_template": False})


def _ladder_placeable(pr):
    """True if every ladder variant is available and covered by a placed image."""
    vs = {v["id"]: v for v in pr["variants"]}
    covered = set()
    for pa in pr.get("print_areas", []):
        if any(ph.get("images") for ph in pa.get("placeholders", [])):
            covered.update(pa.get("variant_ids", []))
    return all(vs.get(i, {}).get("is_available") and i in covered for i in LADDER)


def fix_product(pid):
    pr = _rq(P.get_product, pid)
    name = pr.get("title", "")[:40]
    if not _ladder_placeable(pr):
        print(f"SKIP  {name}: ladder not placeable (wrong blueprint or square design)")
        return False
    enabled = {v["id"] for v in pr["variants"] if v["is_enabled"]}
    if enabled != set(LADDER):
        new = [{"id": v["id"], "price": LADDER.get(v["id"], v.get("price")),
                "is_enabled": v["id"] in LADDER} for v in pr["variants"]]
        _rq(P._req, "PUT", f"/shops/{P.SHOP_ID}/products/{pid}.json", {"variants": new})
    publish_variants_only(pid)
    sizes = [v["title"].split(" /")[0] for v in _rq(P.get_product, pid)["variants"] if v["is_enabled"]]
    print(f"OK    {name}: {sizes}")
    return True


def scan():
    """List published posters that have only one enabled size."""
    for pr in _all_products():
        if pr.get("blueprint_id") != POSTER_BLUEPRINT:
            continue
        ext = pr.get("external") or {}
        en = [v for v in pr["variants"] if v["is_enabled"]]
        flag = "SINGLE-SIZE" if len(en) == 1 else f"{len(en)} sizes"
        print(f"  {pr['id']} etsy={ext.get('id')} {flag:12} {pr.get('title','')[:40]}")


def main(argv):
    if not argv or argv[0] == "--scan":
        scan()
        return
    if argv[0] == "--auto":
        pids = [pr["id"] for pr in _all_products()
                if pr.get("blueprint_id") == POSTER_BLUEPRINT
                and (pr.get("external") or {}).get("id")
                and sum(v["is_enabled"] for v in pr["variants"]) == 1]
    else:
        pids = argv
    for pid in pids:
        fix_product(pid)
        time.sleep(3)


if __name__ == "__main__":
    main(sys.argv[1:])
