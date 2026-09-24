"""Upload the AI room mockups to each tapestry listing as hero images:
amb1 -> rank 1, amb2 -> rank 2 (whichever exist). Printify's product shots
stay after them.

  python upload_ai_mockups.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "printify"))
from etsy_manager import EtsyManager
import printify_publish as pp

AI = os.path.join(HERE, "ai_mockups")

TAPS = [
    ("6ab516d33a6c94099b076cac", "julia_filament"),
    ("6ab516d77ecdec64bf011112", "julia_spiral"),
    ("6ab516dbd94fb14cbf0e73b7", "chaos_6"),
    ("6ab516de19537164330a0cf3", "opart_vortex"),
]


def etsy_id(pid, tries=15, delay=15):
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
        for rank, amb in ((1, "amb1"), (2, "amb2")):
            p = os.path.join(AI, f"{slug}_{amb}.jpg")
            if os.path.exists(p):
                m.upload_listing_image(lid, p, rank=rank)
        print(f"  hecho: {lid}")


if __name__ == "__main__":
    main()
