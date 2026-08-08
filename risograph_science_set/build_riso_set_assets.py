"""
build_riso_set_assets.py — packaging for "Science Specimens: Riso Edition"

Takes the six finished plates (risograph_science_set/plates/*.jpg, 2700x3450
@ 300dpi, native ratio 9:11.5) and builds:

  risograph_science_set/prints/*.jpg        -- 9x11.5in and 11x14in masters per plate
  risograph_science_set/Science_Specimens_Riso_Edition_Set_of_6.zip
  risograph_science_set/previews/*.jpg      -- Etsy listing images (one per plate)

  python build_riso_set_assets.py
"""
import os
import zipfile

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
PLATES_DIR = os.path.join(BASE, "plates")
PRINTS = os.path.join(BASE, "prints"); os.makedirs(PRINTS, exist_ok=True)
PREVIEWS = os.path.join(BASE, "previews"); os.makedirs(PREVIEWS, exist_ok=True)

DPI = 300
SIZES = {
    "9x11.5in": (9.0, 11.5),
    "11x14in": (11.0, 14.0),
}

PLATE_NAMES = [
    "01_cymatics", "02_nautilus_spiral", "03_platonic_solids",
    "04_bohr_atom", "05_koch_snowflake", "06_double_slit",
]

README = """Science Specimens: Riso Edition -- Set of 6
MathRelaxing scientific plate set

Six phenomena from math and physics -- cymatics, the golden spiral,
the five Platonic solids, the Bohr atom, a Koch snowflake, and two-slit
interference -- styled as naturalist specimen cards run through a two-colour
riso press: crisp black keyline, one halftone spot colour per plate, a
touch of registration offset, uncoated paper grain. Every pattern (the
Chladni nodal lines, the interference fringes, the logarithmic spiral) is
computed from the real underlying physics and mathematics, not decorative.

WHAT YOU GET
Six designs, each as a high-resolution JPG at 300 dpi, portrait ratio:
  - 9 x 11.5 in (signature size)
  - 11 x 14 in

Print at home, a print shop, or online lab. Simple black or natural-wood
frame recommended. Frame not included. Personal use only.

(c) MathRelaxing
"""


def build_prints():
    paths = []
    for name in PLATE_NAMES:
        master = Image.open(os.path.join(PLATES_DIR, f"{name}.jpg")).convert("RGB")
        for label, (w_in, h_in) in SIZES.items():
            w_px, h_px = round(w_in * DPI), round(h_in * DPI)
            img = master.resize((w_px, h_px), Image.LANCZOS)
            p = os.path.join(PRINTS, f"{name}_{label}_300dpi.jpg")
            img.save(p, "JPEG", quality=80, dpi=(DPI, DPI))
            paths.append(p)
            print("print:", name, label, img.size, f"{os.path.getsize(p)//1024}KB")
    return paths


def build_zip(print_paths):
    zpath = os.path.join(BASE, "Science_Specimens_Riso_Edition_Set_of_6.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", README)
        for p in print_paths:
            z.write(p, os.path.basename(p))
    print("zip:", zpath, f"{os.path.getsize(zpath)//1024//1024}MB")
    return zpath


def build_previews():
    for i, name in enumerate(PLATE_NAMES, start=1):
        img = Image.open(os.path.join(PLATES_DIR, f"{name}.jpg")).convert("RGB")
        w, h = img.size
        prev = img.resize((round(1600 * w / h), 1600), Image.LANCZOS)
        p = os.path.join(PREVIEWS, f"riso_set_preview_{i}_{name}.jpg")
        prev.save(p, "JPEG", quality=92)
        print("preview:", p)


if __name__ == "__main__":
    prints = build_prints()
    build_zip(prints)
    build_previews()
    print("DONE")
