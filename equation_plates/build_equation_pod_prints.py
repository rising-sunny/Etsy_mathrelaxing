"""
build_equation_pod_prints.py — POD print files for the Famous Equations line.

The Famous Equations Set of 6 is the shop's only design bought by more than
one distinct organic customer, and a single physical poster sale has netted
~5.5x what a digital download does -- so these six get physical POD listings
alongside the digital bundle.

Renders each design straight from generate_equation_plates.py's compose()
API at the three portrait ratios Printify's "Matte Vertical Posters"
blueprint groups its sizes into (2:3, 3:4, 4:5), long edge 6000 px @ 300 dpi
to match the Vintage Math Art / Turing POD lines. The plate layout is
already size-adaptive (font sizes derive from figure width via _fs()), so
each ratio is a proper re-composition rather than a crop.

  python equation_plates/build_equation_pod_prints.py [slug ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import generate_equation_plates as g  # noqa: E402

OUT = Path(__file__).resolve().parent / "pod_products"

# The six designs bundled in the "Famous Equations Wall Art Set of 6".
SET_SLUGS = [
    "fourier_series", "wave_equation", "dirac_equation",
    "navier_stokes", "euler_identity", "mandelbrot_set",
]

DPI = 300
# long edge 6000 px @ 300 dpi -> 20.0 in tall
RATIOS = {
    "2x3": (13.3333, 20.0),
    "3x4": (15.0, 20.0),
    "4x5": (16.0, 20.0),
}


def main(slugs=None):
    # Must be called explicitly: the module defaults _USE_LATEX to False, and
    # without this the plates render in mathtext sans instead of the Computer
    # Modern serif the digital set was published with -- the physical posters
    # would not have matched the digital product's typography.
    g.configure_matplotlib(use_latex=True)
    by = {d.slug: d for d in g.DESIGNS}
    slugs = slugs or SET_SLUGS
    for slug in slugs:
        design = by[slug]
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        for ratio, (w_in, h_in) in RATIOS.items():
            img = design.compose(w_in, h_in, DPI)
            out = folder / f"{slug}_{ratio}.jpg"
            g.save_rgb(img, out, DPI, 92)
            print(f"  {out.relative_to(ROOT)}  {img.size}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
