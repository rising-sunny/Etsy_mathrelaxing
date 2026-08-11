"""
build_ulam_pod.py — POD print files for the Ulam Spiral poster.

Chosen from shop data: the Ulam Spiral print has 30 views (third-highest
among designs with no physical counterpart), is a single design rather than
a set (so one clean product, no cannibalisation), and is almost entirely
visual -- a dot field with emergent diagonals -- which is what the shop's
one physical sale so far (Penrose Tiling) also was.

Renders concept_poster.render() at Printify's three portrait ratios, long
edge 6000 px @ 300 dpi, matching the other POD lines. Font sizes in that
generator derive from figure width, so each ratio re-composes rather than
being cropped or stretched.

  python wallart_set/build_ulam_pod.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import concept_poster as cp  # noqa: E402

OUT = HERE / "ulam_pod"
CONCEPT = "ulam"
DPI = 300
# long edge 6000 px @ 300 dpi -> 20.0 in tall
RATIOS = {
    "2x3": (13.3333, 20.0),
    "3x4": (15.0, 20.0),
    "4x5": (16.0, 20.0),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for ratio, (w_in, h_in) in RATIOS.items():
        fig = cp.render(CONCEPT, w_in, h_in, dpi=DPI)
        out = OUT / f"ulam_spiral_{ratio}.jpg"
        fig.savefig(out, facecolor=cp.PAPER, dpi=DPI, pil_kwargs={"quality": 92})
        plt.close(fig)
        from PIL import Image
        print(f"  {out.relative_to(ROOT)}  {Image.open(out).size}")


if __name__ == "__main__":
    main()
