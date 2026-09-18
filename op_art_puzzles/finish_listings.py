"""For each op-art puzzle: find its Etsy listing (via the Printify product's
external id), replace the flat Printify images with our 3 puzzle mockups, then
append Printify's own puzzle render as a 4th image.

  python finish_listings.py
"""
import os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "printify"))
from etsy_manager import EtsyManager
import printify_publish as pp

MOCK = os.path.join(HERE, "mockups")
REND = os.path.join(HERE, "_pf_render"); os.makedirs(REND, exist_ok=True)

# slug -> printify product id
PRODUCTS = [
    ("square", "6aad95e00abbca769e0f1735"),
    ("wave",   "6aad95e6e4a14c8c0900fef3"),
    ("moire",  "6aad95ee0bf70dd84a09fd60"),
]


def wait_external(pid, tries=20, delay=20):
    import time
    for _ in range(tries):
        prod = pp.get_product(pid)
        ext = prod.get("external") or {}
        if ext.get("id"):
            return prod, int(ext["id"])
        time.sleep(delay)
    return prod, None


def main():
    m = EtsyManager()
    for slug, pid in PRODUCTS:
        prod, lid = wait_external(pid)
        print(f"\n=== {slug}: printify {pid} -> etsy {lid} ===")
        if not lid:
            print("  SIN external id tras esperar; saltando"); continue
        # existing (Printify-pushed) images
        cur = m.make_request('GET', f'/listings/{lid}/images')
        old = [im['listing_image_id'] for im in cur.get('results', [])]
        # 1-3: our mockups
        for rank, suf in enumerate([1, 2, 3], start=1):
            m.upload_listing_image(lid, os.path.join(MOCK, f"{slug}_{suf}.jpg"), rank=rank)
        # 4: Printify's own render
        imgs = prod.get("images", [])
        src = next((i["src"] for i in imgs if i.get("is_default")), imgs[0]["src"])
        local = os.path.join(REND, f"{slug}_printify.jpg")
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            open(local, "wb").write(r.read())
        m.upload_listing_image(lid, local, rank=4)
        # remove old flat images
        for iid in old:
            m.delete_listing_image(lid, iid)
        print(f"  hecho: {lid}")


if __name__ == "__main__":
    main()
