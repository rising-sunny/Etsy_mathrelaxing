"""Remove duplicate images on the tapestry listings (the amb1 mockup got
uploaded twice). Detect exact duplicates by content hash and delete the extras,
keeping the lowest-rank copy.

  python dedupe_images.py
"""
import os, sys, hashlib, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager

LISTINGS = [4581741917, 4581756626, 4581743701, 4581756870]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return hashlib.md5(urllib.request.urlopen(req).read()).hexdigest()


def main():
    m = EtsyManager()
    for lid in LISTINGS:
        imgs = m.make_request('GET', f'/listings/{lid}/images').get('results', [])
        imgs.sort(key=lambda i: i.get('rank', 0))
        seen = {}
        dupes = []
        for im in imgs:
            url = im.get('url_fullxfull') or im.get('url_570xN')
            h = fetch(url)
            if h in seen:
                dupes.append(im['listing_image_id'])
            else:
                seen[h] = im['listing_image_id']
        print(f"{lid}: {len(imgs)} imgs, {len(dupes)} duplicados")
        for iid in dupes:
            m.delete_listing_image(lid, iid)


if __name__ == "__main__":
    main()
