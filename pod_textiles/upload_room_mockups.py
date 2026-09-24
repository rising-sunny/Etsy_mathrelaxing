"""Add the room/ambiance mockups as the hero images on each tapestry listing
(ranks 1-2), keeping Printify's product shots after them.

  python upload_room_mockups.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "printify"))
from etsy_manager import EtsyManager
import printify_publish as pp

MOCK = os.path.join(HERE, "mockups")

# printify product id -> slug
TAPS = [
    ("6ab516d33a6c94099b076cac", "julia_filament"),
    ("6ab516d77ecdec64bf011112", "julia_spiral"),
    ("6ab516dbd94fb14cbf0e73b7", "chaos_6"),
    ("6ab516de19537164330a0cf3", "opart_vortex"),
]


def etsy_id(pid, tries=20, delay=20):
    import time
    for _ in range(tries):
        ext = (pp.get_product(pid).get("external") or {})
        if ext.get("id"):
            return int(ext["id"])
        time.sleep(delay)
    return None


def main():
    m = EtsyManager()
    for pid, slug in TAPS:
        lid = etsy_id(pid)
        print(f"\n=== {slug}: etsy {lid} ===")
        if not lid:
            print("  sin external id; saltando"); continue
        m.upload_listing_image(lid, os.path.join(MOCK, f"{slug}_room1.jpg"), rank=1)
        m.upload_listing_image(lid, os.path.join(MOCK, f"{slug}_room2.jpg"), rank=2)
        print(f"  hecho: {lid}")


if __name__ == "__main__":
    main()
