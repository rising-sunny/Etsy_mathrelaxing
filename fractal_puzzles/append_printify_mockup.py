"""Append Printify's own puzzle render (the assembled-jigsaw front view) as an
extra image on each fractal puzzle Etsy listing, alongside our custom mockups.

  python append_printify_mockup.py
"""
import os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "printify"))
from etsy_manager import EtsyManager
import printify_publish as pp

SCRATCH = os.path.join(HERE, "_pf_render")
os.makedirs(SCRATCH, exist_ok=True)

# printify product id -> Etsy listing id
PAIRS = [
    ("6aad5c0e34453b212b086977", 4577917562, "julia_filament"),
    ("6aad5c13b44ae1510b098c95", 4577917696, "julia_pinwheel"),
    ("6aad5c1b2c24aa53310130e3", 4577901321, "chaos_6"),
    ("6aad5c2f50878382180d1576", 4577917902, "chaos_5"),
]


def main():
    m = EtsyManager()
    for pid, lid, slug in PAIRS:
        print(f"\n=== {slug}: printify {pid} -> etsy {lid} ===")
        prod = pp.get_product(pid)
        imgs = prod.get("images", [])
        src = next((i["src"] for i in imgs if i.get("is_default")), imgs[0]["src"])
        local = os.path.join(SCRATCH, f"{slug}_printify.jpg")
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            open(local, "wb").write(r.read())
        print("  descargado:", os.path.getsize(local), "bytes")
        # how many images currently on the listing -> put ours at the end
        cur = m.make_request('GET', f'/listings/{lid}/images')
        rank = len(cur.get("results", [])) + 1
        m.upload_listing_image(lid, local, rank=rank)
        print(f"  agregado como rank {rank}")


if __name__ == "__main__":
    main()
