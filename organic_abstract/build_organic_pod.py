"""
build_organic_pod.py — POD print files for the Computed Organic posters.

Printify's matte poster blueprint (282 / provider 99) is portrait only. Each
ratio is re-composed rather than cropped: designs.render() lays the shapes out
against that frame's own width, so nothing important falls off the edge of a
narrower print.

Long edge 6000 px @ 300 dpi, matching the shop's other POD lines.

  python organic_abstract/build_organic_pod.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import designs as D  # noqa: E402

OUT = HERE / "pod"
DPI = 300
RATIOS = {"2x3": (13.3333, 20.0), "3x4": (15.0, 20.0), "4x5": (16.0, 20.0)}


def main():
    for d in D.DESIGNS:
        sub = OUT / d["slug"]
        sub.mkdir(parents=True, exist_ok=True)
        for ratio, (w, h) in RATIOS.items():
            fig = D.render(d, w, h, dpi=DPI)
            out = sub / f"{d['slug']}_{ratio}.jpg"
            fig.savefig(out, dpi=DPI, facecolor=fig.get_facecolor(), pil_kwargs={"quality": 92})
            plt.close(fig)
            print(f"  {out.relative_to(HERE)}  {Image.open(out).size}")


if __name__ == "__main__":
    main()
