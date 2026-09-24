"""Fix the white bands: scale the print image so it fully covers each variant's
print area (cover, not fit-to-width), per variant aspect. Re-publish to Etsy.

  python fix_coverage.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "printify")); sys.path.insert(0, REPO)
import printify_publish as pp
SHOP = pp.SHOP_ID

# ALL variants must appear in print_areas. Scale covers each area's height.
TAP_GROUPS = [
    ([41686], 1.36),                              # 26x36  portrait 0.744
    ([41687, 45130, 61899], 1.19),               # 50x60/68x80/88x104 portrait ~0.85
    ([46151, 46152, 46153, 46154], 1.03),        # landscape (disabled) — square covers
]
BLK_GROUPS = [([75114], 1.20)]                    # 0.842

TAPS = ["6ab516d33a6c94099b076cac", "6ab516d77ecdec64bf011112",
        "6ab516dbd94fb14cbf0e73b7", "6ab516de19537164330a0cf3"]
BLKS = ["6ab516e2d94fb14cbf0e73bd", "6ab516e53a6c94099b076cb4"]


def img_id(prod):
    for pa in prod.get("print_areas", []):
        for ph in pa.get("placeholders", []):
            for im in ph.get("images", []):
                return im["id"]


def wait_unlocked(pid, tries=30, delay=20):
    for _ in range(tries):
        prod = pp.get_product(pid)
        if not prod.get("is_locked"):
            return prod
        time.sleep(delay)
    return prod


def fix(pid, groups):
    prod = wait_unlocked(pid)
    if prod.get("is_locked"):
        print(f"  {pid}: BLOQUEADO; saltando"); return
    iid = img_id(prod)
    print_areas = [{
        "variant_ids": vids,
        "placeholders": [{"position": "front",
                          "images": [{"id": iid, "x": 0.5, "y": 0.5, "scale": sc, "angle": 0}]}],
    } for vids, sc in groups]
    pp._req("PUT", f"/shops/{SHOP}/products/{pid}.json", {"print_areas": print_areas})
    pp.publish_product(pid)
    print(f"  {pid}: cobertura completa aplicada + republicado")


def main():
    print("TAPESTRIES:")
    for pid in TAPS:
        fix(pid, TAP_GROUPS)
    print("BLANKETS:")
    for pid in BLKS:
        fix(pid, BLK_GROUPS)


if __name__ == "__main__":
    main()
