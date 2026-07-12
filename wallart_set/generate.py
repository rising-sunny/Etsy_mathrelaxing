"""
generate.py — produce the 30 print-ready files (6 designs x 5 aspect ratios,
300 DPI) plus a master preview per design for the listing mockups.
"""
import os
import time
from render import render
from designs import DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
PRINTS = os.path.join(HERE, "out", "prints")
LISTING = os.path.join(HERE, "out", "listing")
os.makedirs(PRINTS, exist_ok=True)
os.makedirs(LISTING, exist_ok=True)

# 300 DPI pixel sizes per ratio (inches noted).
RATIO_PX = {
    "2x3": (4800, 7200),   # 16x24 in
    "3x4": (5400, 7200),   # 18x24 in
    "4x5": (4800, 6000),   # 16x20 in
    "5x7": (4500, 6300),   # 15x21 in
    "ISO": (4961, 7016),   # A2
}


def main():
    t0 = time.time()
    total = 0
    for name in DESIGNS:
        for rk, (pw, ph) in RATIO_PX.items():
            im = render(name, pw, ph)
            out = os.path.join(PRINTS, f"{name}_{rk}.jpg")
            im.save(out, "JPEG", quality=92, dpi=(300, 300))
            mb = os.path.getsize(out) / 1e6
            total += 1
            print(f"  {name:12s} {rk:4s} {pw}x{ph}  {mb:.1f} MB")
        # master preview (4:5) for mockups / individual listing images
        prev = render(name, 1080, 1350)
        prev.save(os.path.join(LISTING, f"master_{name}.jpg"), "JPEG", quality=94)
    print(f"\nDONE {total} print files in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
