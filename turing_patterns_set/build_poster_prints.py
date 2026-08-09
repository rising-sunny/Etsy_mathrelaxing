"""
build_poster_prints.py — POD print files for the Turing Patterns line.

Renders each of the 6 designs directly at the three portrait ratios
Printify's "Matte Vertical Posters" blueprint groups its sizes into
(2:3, 3:4, 4:5), at the same long-edge-6000px/300dpi target used for the
Vintage Math Art POD line (vintage_art/build_products.py) -- rendered
fresh from the cached Gray-Scott fields rather than cropped from the
9x11.5 digital plate, so every ratio is a full, uncropped composition.

  python build_poster_prints.py
"""
import os

from generate_turing_set import PLATE_SPECS, build_plate

BASE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = os.path.join(BASE, "products")

RATIOS = {"4x5": (4800, 6000), "3x4": (4500, 6000), "2x3": (4000, 6000)}


def main():
    for spec in PLATE_SPECS:
        folder = os.path.join(PRODUCTS, spec["slug"])
        os.makedirs(folder, exist_ok=True)
        for ratio, (w_px, h_px) in RATIOS.items():
            canvas = build_plate(spec["slug"], spec["stops"], w_px=w_px, h_px=h_px)
            out = os.path.join(folder, f"{spec['slug']}_{ratio}.jpg")
            canvas.save(out, "JPEG", quality=92)
            print("wrote", out, canvas.size)


if __name__ == "__main__":
    main()
