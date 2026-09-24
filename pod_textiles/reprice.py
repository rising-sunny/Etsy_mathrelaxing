"""Raise retail prices (higher margin) on the textile POD products and
re-publish so Etsy syncs. Keeps only the intended sizes enabled.

  python reprice.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "printify")); sys.path.insert(0, REPO)
import printify_publish as pp

SHOP = pp.SHOP_ID

TAP_PRICES = {41686: 4499, 41687: 6999, 45130: 9999}   # 26x36 / 50x60 / 68x80
BLK_PRICES = {75114: 7999}                              # 50x60

TAPS = ["6ab516d33a6c94099b076cac", "6ab516d77ecdec64bf011112",
        "6ab516dbd94fb14cbf0e73b7", "6ab516de19537164330a0cf3"]
BLKS = ["6ab516e2d94fb14cbf0e73bd", "6ab516e53a6c94099b076cb4"]


def wait_unlocked(pid, tries=30, delay=20):
    import time
    for _ in range(tries):
        prod = pp.get_product(pid)
        if not prod.get("is_locked"):
            return prod
        time.sleep(delay)
    return prod


def reprice(pid, price_map):
    prod = wait_unlocked(pid)
    if prod.get("is_locked"):
        print(f"  {pid}: SIGUE BLOQUEADO; saltando"); return
    variants = []
    for v in prod["variants"]:
        vid = v["id"]
        if vid in price_map:
            variants.append({"id": vid, "price": price_map[vid], "is_enabled": True})
        else:
            variants.append({"id": vid, "price": v["price"], "is_enabled": False})
    pp._req("PUT", f"/shops/{SHOP}/products/{pid}.json", {"variants": variants})
    pp.publish_product(pid)
    # report
    p2 = pp.get_product(pid)
    en = [v for v in p2["variants"] if v["is_enabled"]]
    print(f"  {pid}: " + ", ".join(f"{v['title']} ${v['price']/100:.2f} (cost ${v['cost']/100:.2f})" for v in en))


def main():
    print("TAPESTRIES:")
    for pid in TAPS:
        reprice(pid, TAP_PRICES)
    print("BLANKETS:")
    for pid in BLKS:
        reprice(pid, BLK_PRICES)


if __name__ == "__main__":
    main()
