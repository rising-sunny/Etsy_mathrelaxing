"""
build_seamless_pack.py — renders the seamless pattern pack and packages it.

Nothing reaches the ZIP without passing seamless.verify() on its own rendered
pixels. A pattern pack whose tiles do not actually tile is worthless to the
buyer and unreturnable once downloaded, so the check is a build gate, not a
report: a failing tile aborts the run.

  python seamless_patterns/build_seamless_pack.py           # full build
  python seamless_patterns/build_seamless_pack.py --probe   # 1 tile, size check
"""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from zlib import crc32
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import families as F  # noqa: E402
import seamless as S  # noqa: E402

INCHES, DPI = 10, 300          # 3000 x 3000 px tiles
OUT = HERE / "out"
ZIP_NAME = "Seamless_Geometric_Pattern_Pack.zip"

# Stroke weights are fractions of one cell, so a pattern keeps the same visual
# weight whether its grid is 3 cells or 16.
def _pt(frac, n):
    return frac * 72 * INCHES / n


# family, slug, params, line fraction, casing fraction
DESIGNS = [
    ("celtic_weave", "celtic_bold",       dict(n=3,  cross_prob=0.30), 0.085, 0.075),
    ("celtic_weave", "celtic_classic",    dict(n=5,  cross_prob=0.34), 0.085, 0.075),
    ("celtic_weave", "celtic_fine",       dict(n=8,  cross_prob=0.34), 0.085, 0.075),
    ("celtic_weave", "celtic_micro",      dict(n=11, cross_prob=0.34), 0.085, 0.075),
    ("celtic_weave", "celtic_lattice",    dict(n=5,  cross_prob=0.68), 0.085, 0.075),
    ("celtic_weave", "celtic_open",       dict(n=5,  cross_prob=0.08), 0.085, 0.075),

    ("truchet_arcs", "arcs_large",        dict(n=3),  0.075, 0.0),
    ("truchet_arcs", "arcs_classic",      dict(n=5),  0.075, 0.0),
    ("truchet_arcs", "arcs_fine",         dict(n=8),  0.075, 0.0),
    ("truchet_arcs", "arcs_micro",        dict(n=12), 0.075, 0.0),
    ("truchet_arcs", "arcs_ribbon",       dict(n=5),  0.240, 0.0),
    ("truchet_arcs", "arcs_hairline",     dict(n=8),  0.022, 0.0),

    ("star_lattice", "star_large",        dict(n=2, points=8),  0.055, 0.045),
    ("star_lattice", "star_classic",      dict(n=3, points=8),  0.055, 0.045),
    ("star_lattice", "star_fine",         dict(n=5, points=8),  0.055, 0.045),
    ("star_lattice", "star_twelvepoint",  dict(n=3, points=12), 0.055, 0.045),
    ("star_lattice", "star_sixpoint",     dict(n=3, points=6),  0.055, 0.045),
    ("star_lattice", "star_dense",        dict(n=6, points=8),  0.055, 0.045),

    ("circle_lattice", "circles_large",   dict(n=3),  0.055, 0.050),
    ("circle_lattice", "circles_classic", dict(n=5),  0.055, 0.050),
    ("circle_lattice", "circles_fine",    dict(n=7),  0.055, 0.050),
    ("circle_lattice", "circles_micro",   dict(n=10), 0.055, 0.050),
    ("circle_lattice", "circles_bold",    dict(n=4),  0.100, 0.085),
    ("circle_lattice", "circles_hairline",dict(n=5),  0.020, 0.018),
]

# Every design ships in ink; a curated few also ship in the four colourways,
# which keeps the ZIP inside Etsy's 20 MB limit while still giving the buyer
# coordinating options.
COLOURWAY_PICKS = ["celtic_classic", "arcs_classic", "star_classic",
                   "circles_classic", "arcs_ribbon", "star_twelvepoint"]

README = """SEAMLESS GEOMETRIC PATTERN PACK
MathRelaxing

24 seamless repeat patterns, four families, 300 dpi.
Every tile is computed to repeat exactly -- no visible join, in any direction.

WHAT'S INSIDE
  PNG/          3000 x 3000 px tiles, 300 dpi, white ground
  PNG_transparent/   the same tiles with no background
  SVG/          full vector, every stroke editable
  colourways/   six of the patterns in indigo, terracotta, sage and gold

HOW TO USE A SEAMLESS TILE
  Photoshop:  Edit > Define Pattern, then fill any shape with it
  Illustrator / Affinity:  drag the SVG into the Swatches panel
  Procreate:  insert the PNG, then duplicate and snap copies edge to edge
  Canva:      upload the PNG and tile it across the page
  Sublimation / POD:  tile to your blank size before printing

LICENCE -- COMMERCIAL USE INCLUDED
  You may use these patterns in finished products you sell: fabric, wrapping
  paper, tumblers, mugs, stationery, packaging, apparel, digital products.
  No credit required, no volume cap.
  You may NOT resell or redistribute the pattern files themselves, as-is or
  recoloured, as digital products, clipart or pattern packs.

(c) MathRelaxing
"""


def _shrink_alpha(path: Path):
    """Re-save a transparent tile as greyscale+alpha.

    Only the alpha channel carries anything: every inked pixel is the same
    near-black, so three identical colour channels are paid for and never used.
    Dropping them takes the transparent set from 9.3 MB to about 5.5 MB, which
    is what keeps the download clear of Etsy's 20 MB ceiling.
    """
    from PIL import Image
    Image.open(path).convert("LA").save(path, optimize=True)


def render_one(family, slug, params, lw_frac, band_frac, pal_name, png, svg=None,
               transparent=False):
    # crc32, not hash(): Python randomises str hashing per process, so hash()
    # would redraw every pattern differently on each run and the shipped files
    # would stop matching the previews.
    pal = F.PALETTES[pal_name]
    n = params.get("n") or params.get("k")
    fig, ax = S.canvas(px=INCHES * DPI, dpi=DPI)
    F.FAMILIES[family](ax, pal, lw=_pt(lw_frac, n), band=_pt(band_frac, n),
                       seed=crc32(slug.encode()) % 9973, **params)
    S.save(fig, png, svg, bg=None if transparent else pal["bg"], dpi=DPI)
    return png


def main(probe=False):
    if OUT.exists():
        shutil.rmtree(OUT)
    designs = DESIGNS[:1] if probe else DESIGNS

    failures, made = [], []
    for family, slug, params, lwf, bf in designs:
        png = OUT / "PNG" / f"{slug}.png"
        svg = OUT / "SVG" / f"{slug}.svg"
        render_one(family, slug, params, lwf, bf, "ink", png, svg)
        m = S.verify(png)
        mark = "OK" if m["ok"] else "** COSTURA **"
        print(f"  {slug:22s} h={m['seam_h']:5.2f} v={m['seam_v']:5.2f}  {mark}")
        if not m["ok"]:
            failures.append(slug)
        made.append((family, slug, params, lwf, bf))

        tp = render_one(family, slug, params, lwf, bf, "ink",
                        OUT / "PNG_transparent" / f"{slug}.png", transparent=True)
        _shrink_alpha(tp)

        if slug in COLOURWAY_PICKS and not probe:
            for pal_name in ("indigo", "terracotta", "sage", "gold"):
                render_one(family, slug, params, lwf, bf, pal_name,
                           OUT / "colourways" / f"{slug}_{pal_name}.png")

    if failures:
        raise SystemExit(f"\nABORTADO: {len(failures)} con costura -> {failures}")

    if probe:
        for p in sorted(OUT.rglob("*.*")):
            print(f"  {p.stat().st_size/1e6:6.2f} MB  {p.relative_to(OUT)}")
        return

    (OUT / "READ-ME.txt").write_text(README, encoding="utf-8")
    zip_path = HERE / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT).as_posix())
    mb = zip_path.stat().st_size / 1e6
    with zipfile.ZipFile(zip_path) as z:
        n_files = len(z.namelist())
    print(f"\n{ZIP_NAME}: {mb:.1f} MB, {n_files} archivos")
    if mb > 19.5:
        print("  WARNING: cerca del limite de 20 MB de Etsy")
    return zip_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    main(**vars(ap.parse_args()))
