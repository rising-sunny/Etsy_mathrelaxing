"""Upload the two Vintage Math Art print sets as Etsy DRAFTS."""
import json
from pathlib import Path
from etsy_manager import EtsyManager

BASE = Path(__file__).resolve().parent
PROD = BASE / "products"
TAXONOMY_DIGITAL_ART = 2078
PRICE = 8.99

COPYRIGHT = "© MathRelaxing. For personal use only. Not for redistribution or resale."

MAURER_DESC = f"""Instant download — a set of 6 printable Maurer Rose art prints, drawn with real mathematics (no AI, no stock images).

A Maurer rose is the hidden figure that appears when you connect points around a rose curve with straight lines — an intricate lattice of gold and ink that reads like antique string art or an engraved compass rose. Six distinct designs, from a soft four-petal bloom to a twelve-point star, on a warm aged-ivory background.

► WHAT YOU GET
• 6 original designs — hand-coded, one of a kind
• 4 aspect ratios each (24 files total): 4:5, 3:4, 2:3 and ISO / A-series
• High resolution — 6000 px long edge (300 dpi at 20 in)
• 4 ZIP files (one per ratio) — instant download, nothing is shipped

► HOW TO USE
Print at home, at a local print shop, or online. Choose the ratio that fits your frame and scale to any size. Perfect for a gallery wall, a study, or a mathematician / dark-academia gift.

► ABOUT THE ART
Every design is generated from its equation in code — never an AI image generator — so the geometry is exact and unique to this shop.

{COPYRIGHT}"""

PHYLLO_DESC = f"""Instant download — a set of 6 printable Phyllotaxis art prints based on the golden ratio, drawn with real mathematics (no AI, no stock images).

Phyllotaxis is the spiral packing nature uses to arrange sunflower seeds and pinecone scales, set by the golden angle (137.5°). Six designs sweep the angle by fractions of a degree — turning the same seed head from radial rays to bold Fibonacci spirals — in gold and ink on a warm aged-ivory background.

► WHAT YOU GET
• 6 original designs — hand-coded, one of a kind
• 4 aspect ratios each (24 files total): 4:5, 3:4, 2:3 and ISO / A-series
• High resolution — 6000 px long edge (300 dpi at 20 in)
• 4 ZIP files (one per ratio) — instant download, nothing is shipped

► HOW TO USE
Print at home, at a local print shop, or online. Choose the ratio that fits your frame and scale to any size. Perfect for a gallery wall, a calm minimalist space, or a nature / sacred-geometry lover's gift.

► ABOUT THE ART
Every design is generated from the golden angle in code — never an AI image generator — so the geometry is exact and unique to this shop.

{COPYRIGHT}"""

PRODUCTS = {
    "maurer_rose": {
        "title": ("Maurer Rose Set of 6 Prints, Vintage Mathematical Line Art | "
                  "Geometric Rosette Wall Art, Sacred Geometry | Printable Digital Download"),
        "description": MAURER_DESC,
        "tags": ["maurer rose", "math wall art", "geometric print", "line art print",
                 "rosette art", "sacred geometry", "vintage math art", "string art print",
                 "mandala wall art", "mathematical art", "printable art", "dark academia",
                 "digital download"],
    },
    "phyllotaxis": {
        "title": ("Phyllotaxis Set of 6 Prints, Golden Ratio Spiral Wall Art | "
                  "Fibonacci Sunflower Botanical Math Art | Printable Digital Download"),
        "description": PHYLLO_DESC,
        "tags": ["phyllotaxis", "golden ratio art", "fibonacci print", "spiral wall art",
                 "sunflower art", "sacred geometry", "vintage math art", "botanical print",
                 "mathematical art", "printable art", "dark academia", "nature wall art",
                 "digital download"],
    },
}

RATIO_ORDER = ["4x5", "3x4", "2x3", "ISO"]
ZIP_PREFIX = {"maurer_rose": "MaurerRose", "phyllotaxis": "Phyllotaxis"}


def images_for(slug):
    d = PROD / slug
    imgs = [d / "hero.jpg"] + [d / f"preview_{i:02d}.jpg" for i in range(1, 7)] + [d / "whatyouget.jpg"]
    return [str(p) for p in imgs]


def files_for(slug):
    d = PROD / slug
    return [str(d / f"{ZIP_PREFIX[slug]}_{r}.zip") for r in RATIO_ORDER]


def main():
    m = EtsyManager()
    results = {}
    for slug, cfg in PRODUCTS.items():
        print(f"\n=== {slug} :: {cfg['title'][:60]}... (${PRICE}) ===")
        imgs = images_for(slug)
        files = files_for(slug)
        for p in imgs + files:
            assert Path(p).exists(), f"MISSING {p}"
        assert len(cfg["title"]) <= 140, f"title too long: {len(cfg['title'])}"
        lid = m.create_full_product(
            title=cfg["title"],
            description=cfg["description"],
            price=PRICE,
            taxonomy_id=TAXONOMY_DIGITAL_ART,
            image_paths=imgs,
            digital_file_paths=files,
            tags=cfg["tags"],
        )
        try:
            m.update_listing_price(lid, PRICE)
        except Exception as e:
            print(f"  price verify warn: {e}")
        results[slug] = lid
        print(f"  DRAFT https://www.etsy.com/listing/{lid}")
    (PROD / "listing_ids.json").write_text(json.dumps(results, indent=2))
    print("\nSAVED", results)


if __name__ == "__main__":
    main()
