"""
build_unit_circle_pod.py — POD print files for the Unit Circle poster.

The Unit Circle print is tied for the most-viewed listing in the shop (109
views), is one of only nine organic sales, and had no physical counterpart --
and a reference poster is the kind of thing people want on a wall rather than
as a file. So it gets a matte POD poster.

Renders compose_plate() at the three portrait ratios Printify's "Matte
Vertical Posters" blueprint groups its sizes into (2:3, 3:4, 4:5), long edge
6000 px @ 300 dpi, matching the Vintage / Turing / Famous Equations POD
lines. The plate is size-adaptive (font sizes derive from figure width via
_fs()), so each ratio is a real re-composition rather than a crop.

  python unit_circle/build_unit_circle_pod.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import generate_unit_circle as g  # noqa: E402

OUT = Path(__file__).resolve().parent / "pod_products"

DPI = 300
# long edge 6000 px @ 300 dpi -> 20.0 in tall
RATIOS = {
    "2x3": (13.3333, 20.0),
    "3x4": (15.0, 20.0),
    "4x5": (16.0, 20.0),
}


def main():
    # generate_unit_circle defaults to no LaTeX until this is called; without
    # it the plate renders in a fallback face instead of the Computer Modern
    # the digital listing was published with.
    g.configure_matplotlib(use_latex=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for ratio, (w_in, h_in) in RATIOS.items():
        img = g.compose_plate(w_in, h_in, DPI)
        out = OUT / f"unit_circle_{ratio}.jpg"
        g.save_rgb(img, str(out), DPI, 92)
        print(f"  {out.relative_to(ROOT)}  {img.size}")


if __name__ == "__main__":
    main()
