"""
publish_listing.py — create the Etsy DRAFT for the "Quiet Mathematics" printable
wall-art set (6 designs x 5 ratios). Draft only; activation stays manual.

    python publish_listing.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import etsy_manager

HERE = os.path.dirname(os.path.abspath(__file__))
LST = os.path.join(HERE, "out", "listing")
ZIPS = os.path.join(HERE, "out", "zips")

TITLE = ("Set of 6 Printable Wall Art | Boho Abstract Line Art Gallery Wall Set | "
         "Neutral Earth Tone Japandi Decor | Mathematical Minimalist Prints")

TAGS = ["printable wall art", "gallery wall set", "set of 6 prints", "boho wall art",
        "abstract line art", "neutral wall art", "earth tone art", "japandi wall art",
        "minimalist print", "digital download", "terracotta decor", "living room decor",
        "math wall art"]

DESCRIPTION = """QUIET MATHEMATICS — a set of 6 printable wall art prints.

Six original designs, each drawn from a real mathematical curve and rendered as calm, minimalist line art in a warm earth-tone palette. Not AI images and not clip art — every piece is generated from its equation, then composed for a Japandi / boho gallery wall.

THE SIX DESIGNS
• Maurer Rose — a rose curve walked in straight steps into a lace of interference
• Golden Spiral — sunflower seeds placed at the golden angle (137.5°)
• Hilbert Curve — a single continuous line that fills the plane
• Cardioid Weave — a times-table circle whose chords envelope a cardioid
• Euler Spiral — the clothoid, the curve of railways and roads
• Barnsley Fern — a fern grown from an iterated function system

WHAT YOU GET (instant digital download)
• All 6 designs in 5 aspect ratios — 2:3, 3:4, 4:5, 5:7 and ISO/A
• 300 DPI, high resolution — print small or large
• Delivered as 5 ZIP files (one per ratio), 30 files in total
• Warm cream ground with muted terracotta, sage, gold and charcoal line work

PRINT ALMOST ANY SIZE
2:3 → 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in
3:4 → 6x8, 9x12, 12x16, 18x24 in
4:5 → 8x10, 16x20, 24x30 in
5:7 → 5x7, 10x14, 15x21 in
ISO/A → A5, A4, A3, A2, A1

HOW IT WORKS
1) Buy and download instantly — no physical item is shipped.
2) Pick your size and ratio.
3) Print at home, a local print shop, or an online service.
4) Trim to your frame and hang.

Colours may vary slightly between screens and printers. Frames not included.

TERMS — For personal use only. Please do not resell, redistribute or share the files.

(c) MathRelaxing"""

# Listing photos in rank order (first = thumbnail).
IMAGES = [
    os.path.join(LST, "01_hero_gallery.jpg"),
    os.path.join(LST, "02_room.jpg"),
    os.path.join(LST, "04_included.jpg"),
    os.path.join(LST, "03_detail.jpg"),
    os.path.join(LST, "05_sizes.jpg"),
    os.path.join(LST, "06_how.jpg"),
]
FILES = [
    os.path.join(ZIPS, "QuietMathematics_2x3.zip"),
    os.path.join(ZIPS, "QuietMathematics_3x4.zip"),
    os.path.join(ZIPS, "QuietMathematics_4x5.zip"),
    os.path.join(ZIPS, "QuietMathematics_5x7.zip"),
    os.path.join(ZIPS, "QuietMathematics_ISO.zip"),
]
PRICE = 12.00
TAXONOMY_ID = 2078   # Art & Collectibles > Prints > Digital Prints


def main():
    assert len(TITLE) <= 140, f"title too long: {len(TITLE)}"
    assert TITLE.count("&") <= 1, "more than one & in title"
    assert len(TAGS) <= 13 and all(len(t) <= 20 for t in TAGS), "tag limits"
    for f in IMAGES + FILES:
        assert os.path.exists(f), f"missing {f}"
    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(TITLE, DESCRIPTION, PRICE, TAXONOMY_ID,
                                 is_digital=True, tags=TAGS)
    for rank, img in enumerate(IMAGES, start=1):
        m.upload_listing_image(lid, img, rank=rank)
    for f in FILES:
        m.upload_listing_file(lid, f)
    print(f"\nDRAFT LISTING creado: {lid}  (${PRICE}, {len(IMAGES)} imagenes, {len(FILES)} zips)")
    print(f"title chars: {len(TITLE)}")
    return lid


if __name__ == "__main__":
    main()
