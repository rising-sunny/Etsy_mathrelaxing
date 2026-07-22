"""
publish_listing.py — create the Etsy DRAFT for the Geometric Color-by-Number
book: draft listing + 6 listing photos + the print-ready PDF. Draft only;
activation stays manual.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import etsy_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pkg_out")
LST = os.path.join(OUT, "listing")

TITLE = ("Geometric Color by Number - 20 Printable Low Poly Math Coloring Pages | "
         "Fractal & Complex Function Art | PDF Digital Download")

TAGS = ["color by number", "math coloring book", "geometric coloring", "low poly art",
        "fractal art", "printable coloring", "adult coloring", "newton fractal",
        "digital download", "math art print", "stem gift", "relaxing coloring",
        "coloring pages pdf"]

DESCRIPTION = """Color the mathematics.

Geometric Color by Number is a printable coloring book where every design is a real piece of generative math art - domain colorings of complex functions, Newton fractals, and Julia sets - broken into a low-poly triangular mosaic you color by number. Fill each numbered facet and the hidden fractal blooms back to life, one triangle at a time.

WHAT YOU GET (instant digital download)
- 20 unique low-poly color-by-number pages
- 20 full-color solution pages (your answer key)
- "The Mathematics" and "How to Color" guide pages
- 45-page PDF, US Letter (8.5 x 11 in), 300 DPI, print-ready
- Original generative art - no stock images

THE DESIGNS
11 complex-function domain colorings, 6 Newton-fractal basins (z3 through z8), and 3 Julia sets. Every page uses 9-12 colors with its own numbered color key.

HOW IT WORKS
1. Download the PDF and print the pages you like (print at 100% / Actual Size).
2. Match each number to a color from the key.
3. Fill the facets and watch the artwork appear.
Use colored pencils, markers, or gel pens - whatever you enjoy.

Perfect for adults, students, math and science lovers, and anyone who finds coloring relaxing. A unique STEM-flavored gift.

DIGITAL DOWNLOAD - no physical item will be shipped. Screen colors may differ slightly from your printer.

(c) MathRelaxing - For personal use only. Not for redistribution or resale."""

# rank order: lead with the colourful grid, then what-it-is, then how/samples
IMAGES = [
    os.path.join(LST, "listing_2_grid.jpg"),
    os.path.join(LST, "listing_1_hero.jpg"),
    os.path.join(LST, "listing_5_beforeafter.jpg"),
    os.path.join(LST, "listing_4_coloring.jpg"),
    os.path.join(LST, "listing_3_solution.jpg"),
    os.path.join(LST, "listing_6_included.jpg"),
]
PDF = os.path.join(OUT, "MathColorByNumber_Vol1.pdf")
PRICE = 9.99
TAXONOMY_ID = 2078   # Art & Collectibles > Prints > Digital Prints (used by the other PDF books)

# Draft published 2026-07-11 (activation manual). 6 images + 12.1 MB PDF attached.
LISTING_ID = 4536173762


def main():
    assert len(TITLE) <= 140, f"title too long: {len(TITLE)}"
    assert TITLE.count("&") <= 1, "more than one & in title"
    for f in IMAGES + [PDF]:
        assert os.path.exists(f), f"missing {f}"
    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(TITLE, DESCRIPTION, PRICE, TAXONOMY_ID,
                                 is_digital=True, tags=TAGS)
    for rank, img in enumerate(IMAGES, start=1):
        m.upload_listing_image(lid, img, rank=rank)
    m.upload_listing_file(lid, PDF)
    print(f"\nDRAFT LISTING creado: {lid}  (price ${PRICE}, {len(IMAGES)} imagenes, PDF subido)")
    print(f"title chars: {len(TITLE)}")
    return lid


if __name__ == "__main__":
    main()
