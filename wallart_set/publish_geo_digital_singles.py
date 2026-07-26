"""
publish_geo_digital_singles.py — create six INDIVIDUAL digital-download listings
(one per geometric tiling design) as Etsy DRAFTS. Complements the existing
6-in-1 "Geometric Tessellation Wall Art Set" bundle.

Each listing ships the design's 5 print-ready ratio files (2:3, 3:4, 4:5, 5:7,
ISO) and uses a framed room mockup + flat art + shared sizes/how images.

    python wallart_set/publish_geo_digital_singles.py         (run from repo root)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import etsy_manager

PRINTS = os.path.join(HERE, "out", "geo", "mono", "prints")
LST = os.path.join(HERE, "out", "geo", "mono", "listing")
RATIOS = ["2x3", "3x4", "4x5", "5x7", "ISO"]
PRICE = 2.99
TAXONOMY = 2078  # Digital Prints

ORDER = ["penrose", "truchet", "girih", "rhombille", "sierpinski", "flower"]
DISPLAY = {
    "penrose": "Penrose Tiling", "truchet": "Truchet Weave", "girih": "Girih Stars",
    "rhombille": "Isometric Cubes", "sierpinski": "Sierpinski Triangle",
    "flower": "Flower of Life",
}
HOOK = {
    "penrose": "An aperiodic Penrose tiling — two rhombi that fill the plane and never exactly repeat, built on the golden ratio.",
    "truchet": "Truchet tiles — a single arc tile dropped at random in four rotations, flowing into an endless maze of curves.",
    "girih": "An eight-fold Islamic girih star grid, the geometry behind centuries of tilework.",
    "rhombille": "A rhombille tiling — rhombi that lock into a field of three-dimensional cubes.",
    "sierpinski": "The Sierpinski triangle — a triangle endlessly subdivided into smaller triangles, a self-similar fractal.",
    "flower": "The Flower of Life — the overlapping-circle lattice at the heart of sacred geometry.",
}
COMMON_TAGS = ["printable wall art", "digital download", "black and white art",
               "line art print", "geometric print", "minimalist print",
               "math wall art", "scandinavian art", "modern wall art", "tessellation art"]
EXTRA_TAGS = {
    "penrose": ["penrose tiling", "aperiodic art", "physics gift"],
    "truchet": ["pattern print", "op art", "black white decor"],
    "girih": ["islamic art", "star pattern", "sacred geometry"],
    "rhombille": ["isometric art", "3d cube art", "op art"],
    "sierpinski": ["fractal art", "sierpinski", "math gift"],
    "flower": ["sacred geometry", "flower of life", "mandala art"],
}


def meta(name):
    disp = DISPLAY[name]
    title = (f"{disp} Printable Wall Art | Black and White Geometric Print | "
             f"Digital Download | Minimalist Line Art Poster")
    assert len(title) <= 140, f"title too long ({len(title)}): {title}"
    assert title.count("&") <= 1 and not any(c in title for c in "^=+")
    tags = (COMMON_TAGS + EXTRA_TAGS[name])[:13]
    desc = (
        f"{disp} — a printable geometric wall art print. Instant digital download; "
        "no physical item is shipped.\n\n"
        f"{HOOK[name]}\n\n"
        "— WHAT YOU GET —\n"
        "5 print-ready JPG files (300 DPI, high resolution), one per aspect ratio, so "
        "you can print almost any size:\n"
        "- 2:3 — 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in\n"
        "- 3:4 — 6x8, 9x12, 12x16, 18x24 in\n"
        "- 4:5 — 8x10, 11x14, 16x20 in\n"
        "- 5:7 — 5x7, 10x14, 15x21 in\n"
        "- ISO / A-series — A5, A4, A3, A2, A1\n\n"
        "— HOW IT WORKS —\n"
        "1. Buy and download instantly (files are available right after purchase).\n"
        "2. Print at home, at a local print shop, or through an online print service.\n"
        "3. Trim to your frame and hang. Frame not included.\n\n"
        "— PLEASE NOTE —\n"
        "- Digital download only. No physical item will be shipped.\n"
        "- Colors may vary slightly depending on your screen and printer.\n"
        "- For personal use.\n\n"
        "Part of the Geometric Tilings series. Want all six designs together? Look for "
        "the full Geometric Tessellation Wall Art Set in our shop and save.\n\n"
        "Made by MathRelaxing."
    )
    return title, desc, tags


def _retry(fn, *a, **k):
    for att in range(4):
        try:
            return fn(*a, **k)
        except Exception as e:  # noqa: BLE001
            print("   retry", att + 1, str(e)[:70])
            time.sleep(2 ** att)
    raise RuntimeError("failed after retries")


def main():
    m = etsy_manager.EtsyManager()
    only = set(sys.argv[1:])
    created = []
    for name in ORDER:
        if only and name not in only:
            continue
        title, desc, tags = meta(name)
        print(f"\n=== {DISPLAY[name]} ({len(title)} chars) ===")
        lid = _retry(m.create_draft_listing, title, desc, PRICE, TAXONOMY,
                     is_digital=True, quantity=999, tags=tags)
        # digital files: 5 ratios
        for r in RATIOS:
            fp = os.path.join(PRINTS, f"{name}_{r}.jpg")
            _retry(m.upload_listing_file, lid, fp)
            time.sleep(1)
        # images: framed mockup, flat art, sizes, how
        imgs = [f"room_{name}.jpg", f"master_{name}.jpg", "05_sizes.jpg", "06_how.jpg"]
        for rank, fn in enumerate(imgs, start=1):
            _retry(m.upload_listing_image, lid, os.path.join(LST, fn), rank=rank)
            time.sleep(1)
        print(f"  draft {lid} created (5 files + 4 images)")
        created.append((name, lid))
    print("\n=== DONE ===")
    for name, lid in created:
        print(f"  {DISPLAY[name]:20s} {lid}")


if __name__ == "__main__":
    main()
