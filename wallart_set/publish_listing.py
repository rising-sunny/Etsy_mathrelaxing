"""
publish_listing.py — create the Etsy DRAFT for a "Quiet Mathematics" printable
wall-art set. One entry per palette; draft only, activation stays manual.

    WALLART_PALETTE=mono python wallart_set/publish_listing.py   # run from repo root
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import etsy_manager

HERE = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_ID = 2078   # Art & Collectibles > Prints > Digital Prints


def _description(palette_line, style, color_line):
    return f"""QUIET MATHEMATICS — a set of 6 printable wall art prints.

Six original designs, each drawn from a real mathematical curve and rendered as calm, minimalist line art {palette_line}. Not AI images and not clip art — every piece is generated from its equation, then composed for a {style} gallery wall.

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
• {color_line}

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


LISTINGS = {
    "earth": {
        "title": ("Set of 6 Printable Wall Art | Boho Abstract Line Art Gallery Wall Set | "
                  "Neutral Earth Tone Japandi Decor | Mathematical Minimalist Prints"),
        "tags": ["printable wall art", "gallery wall set", "set of 6 prints", "boho wall art",
                 "abstract line art", "neutral wall art", "earth tone art", "japandi wall art",
                 "minimalist print", "digital download", "terracotta decor", "living room decor",
                 "math wall art"],
        "description": _description("in a warm earth-tone palette", "Japandi / boho",
                                    "Warm cream ground with muted terracotta, sage, gold and charcoal line work"),
        "price": 9.99,
        "listing_id": 4536831020,   # already published
    },
    "cool": {
        "title": ("Set of 6 Japandi Printable Wall Art | Sage Green Minimalist Line Art Gallery Wall Set | "
                  "Cool Neutral Zen Decor | Mathematical Prints"),
        "tags": ["japandi wall art", "printable wall art", "gallery wall set", "set of 6 prints",
                 "sage green art", "minimalist print", "zen wall art", "abstract line art",
                 "neutral wall art", "digital download", "scandinavian art", "living room decor",
                 "math wall art"],
        "description": _description("in a cool, muted Japandi palette", "Japandi / zen",
                                    "Soft cool greige ground with sage, slate and charcoal line work"),
        "price": 9.99,
        "listing_id": 4536825589,   # draft published 2026-07-12 (activation manual)
    },
    "mono": {
        "title": ("Set of 6 Black and White Printable Wall Art | Minimalist Line Art Gallery Wall Set | "
                  "Scandinavian Abstract Decor | Mathematical Prints"),
        "tags": ["black and white art", "printable wall art", "gallery wall set", "set of 6 prints",
                 "minimalist print", "line art print", "scandinavian art", "abstract wall art",
                 "modern wall art", "digital download", "monochrome print", "living room decor",
                 "math wall art"],
        "description": _description("in black and white", "Scandinavian / minimalist",
                                    "Warm ivory ground with charcoal line work — a true black-and-white set"),
        "price": 9.99,
        "listing_id": 4536834070,   # draft published 2026-07-12 (activation manual)
    },
}

IMG_ORDER = ["01_hero_gallery", "02_room", "04_included", "03_detail", "05_sizes", "06_how"]
RATIOS = ["2x3", "3x4", "4x5", "5x7", "ISO"]


def main():
    pal = os.environ.get("WALLART_PALETTE", "earth")
    cfg = LISTINGS[pal]
    base = os.path.join(HERE, "out", pal)
    images = [os.path.join(base, "listing", f"{n}.jpg") for n in IMG_ORDER]
    files = [os.path.join(base, "zips", f"QuietMathematics_{pal}_{r}.zip") for r in RATIOS]

    assert len(cfg["title"]) <= 140, f"title too long: {len(cfg['title'])}"
    assert cfg["title"].count("&") <= 1, "more than one & in title"
    assert len(cfg["tags"]) <= 13 and all(len(t) <= 20 for t in cfg["tags"]), "tag limits"
    for f in images + files:
        assert os.path.exists(f), f"missing {f}"

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(cfg["title"], cfg["description"], cfg["price"],
                                 TAXONOMY_ID, is_digital=True, tags=cfg["tags"])
    for rank, img in enumerate(images, start=1):
        m.upload_listing_image(lid, img, rank=rank)
    for f in files:
        m.upload_listing_file(lid, f)
    print(f"\nDRAFT [{pal}] creado: {lid}  (${cfg['price']}, {len(images)} imagenes, {len(files)} zips)")
    print(f"title chars: {len(cfg['title'])}")
    return lid


if __name__ == "__main__":
    main()
