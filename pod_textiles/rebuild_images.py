"""Rebuild each tapestry listing's images deterministically:
  rank 1 = amb1 (AI room mockup)
  rank 2 = amb2 (AI room mockup)
  rank 3+ = Printify's own product shots
Deletes all existing images first to clear duplicates.

  python rebuild_images.py
"""
import os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "printify"))
from etsy_manager import EtsyManager
import printify_publish as pp

AI = os.path.join(HERE, "ai_mockups")
TMP = os.path.join(HERE, "_pf_render"); os.makedirs(TMP, exist_ok=True)

# printify product id, etsy listing id, slug
ITEMS = [
    ("6ab516d33a6c94099b076cac", 4581741917, "julia_filament"),
    ("6ab516d77ecdec64bf011112", 4581756626, "julia_spiral"),
    ("6ab516dbd94fb14cbf0e73b7", 4581743701, "chaos_6"),
    ("6ab516de19537164330a0cf3", 4581756870, "opart_vortex"),
]


def dl(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        open(path, "wb").write(r.read())


def main():
    m = EtsyManager()
    for pid, lid, slug in ITEMS:
        print(f"\n=== {slug} -> {lid} ===")
        # printify product shots
        prod = pp.get_product(pid)
        shots = [i["src"] for i in prod.get("images", []) if i.get("is_selected_for_publishing")][:4]
        shot_paths = []
        for k, src in enumerate(shots):
            p = os.path.join(TMP, f"{slug}_shot{k}.jpg"); dl(src, p); shot_paths.append(p)
        # delete existing
        cur = m.make_request('GET', f'/listings/{lid}/images').get('results', [])
        # upload new set
        rank = 1
        for amb in ("amb1", "amb2"):
            m.upload_listing_image(lid, os.path.join(AI, f"{slug}_{amb}.jpg"), rank=rank); rank += 1
        for p in shot_paths:
            m.upload_listing_image(lid, p, rank=rank); rank += 1
        for im in cur:
            m.delete_listing_image(lid, im['listing_image_id'])
        print(f"  reconstruido: {rank-1} imgs")


if __name__ == "__main__":
    main()
