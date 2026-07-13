"""
generate.py — print-ready files for a collection+palette: each design x 5 aspect
ratios @ 300 DPI, a master preview per design, and 5 per-ratio delivery ZIPs.

    WALLART_MODULE=designs_geo WALLART_PALETTE=mono python generate.py
"""
import os
import time
import zipfile
import importlib

designs = importlib.import_module(os.environ.get("WALLART_MODULE", "designs"))
PAL = os.environ.get("WALLART_PALETTE", "earth")
designs.use_palette(PAL)

from render import render   # imports the same module via WALLART_MODULE
DESIGNS = designs.DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", designs.COLLECTION, PAL)
PRINTS = os.path.join(BASE, "prints")
LISTING = os.path.join(BASE, "listing")
ZIPS = os.path.join(BASE, "zips")
for d in (PRINTS, LISTING, ZIPS):
    os.makedirs(d, exist_ok=True)

RATIO_PX = {
    "2x3": (4800, 7200), "3x4": (5400, 7200), "4x5": (4800, 6000),
    "5x7": (4500, 6300), "ISO": (4961, 7016),
}
NAMES = designs.ORDER
FILE_TITLE = {n: DESIGNS[n]["title"].replace(" ", "-") for n in NAMES}
READ_ME = (f"{designs.SET_NAME} - Printable Wall Art Set of 6\n"
           "300 DPI. Personal use only; not for resale or redistribution.\n"
           "This ZIP contains all 6 designs in the {r} aspect ratio.\n"
           "Print at home, a print shop, or an online lab. Trim to your frame.\n")


def main():
    t0 = time.time()
    for name in NAMES:
        for rk, (pw, ph) in RATIO_PX.items():
            render(name, pw, ph).save(os.path.join(PRINTS, f"{name}_{rk}.jpg"),
                                      "JPEG", quality=92, dpi=(300, 300))
        render(name, 1080, 1350).save(
            os.path.join(LISTING, f"master_{name}.jpg"), "JPEG", quality=94)
        print(f"  {name} done")

    for rk in RATIO_PX:
        zpath = os.path.join(ZIPS, f"{designs.SLUG}_{PAL}_{rk}.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for name in NAMES:
                z.write(os.path.join(PRINTS, f"{name}_{rk}.jpg"),
                        f"{FILE_TITLE[name]}_{rk}.jpg")
            z.writestr("READ-ME.txt", READ_ME.format(r=rk))
        print(f"  zip {rk}  {os.path.getsize(zpath)/1e6:.1f} MB")

    print(f"\nDONE [{designs.COLLECTION}/{PAL}] in {time.time()-t0:.0f}s -> {BASE}")


if __name__ == "__main__":
    main()
