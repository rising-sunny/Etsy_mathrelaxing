"""
build_lowpoly_ipad_svg.py — Interactive SVG iPad edition of Geometric Color by Number
======================================================================================
Companion to Etsy listing 4536173762 (printable PDF low-poly CBN book).

Reuses the same generative sources + triangular tessellation as lowpoly_cbn/,
but emits tap-to-fill SVG HTML pages (Safari) via template_ipad_svg_bundle.

Each design keeps its own quantized palette (the PDF book already does this).

    python build_lowpoly_ipad_svg.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image
import shapely.geometry

# lowpoly_cbn package lives in a subfolder
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lowpoly_cbn"))

import art_gallery
from lowpoly_core import quantize, _iter_cells, _nearest_number

from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle

# ── Config ────────────────────────────────────────────────────────────────────

SRC_DIR = os.path.join(HERE, "lowpoly_cbn", "pkg_src")
N_DESIGNS = 20  # same as the published PDF book

# Fallback palette (overridden per design by quantization)
_FALLBACK = [
    "#E8B4B8", "#E6C79C", "#E8E0A0", "#B8D4A8", "#A0D4D4",
    "#A8C0E0", "#C0A8E0", "#D4A0C0", "#D0D0D0", "#909090",
    "#606060", "#303030",
]

CFG = SvgBundleConfig(
    out_dir="ipad_lowpoly_cbn_svg",
    prefix="GeometricCBN",
    title="Geometric Color by Number",
    palette=_FALLBACK,
    n_designs=N_DESIGNS,
    stroke_color="#1A1D24",
    # Coordinates are normalized to ~unit square; font sizes follow.
    min_area=1e-10,
    area_threshold=1e-10,
    font_clearance_ratio=1.15,
    font_min=0.008,
    font_max=0.045,
)

# Cached pieces list (built once)
_PIECES = None


def _pieces():
    global _PIECES
    if _PIECES is None:
        _PIECES = art_gallery.build_all(SRC_DIR)
        assert len(_PIECES) == N_DESIGNS, (
            f"Expected {N_DESIGNS} designs, got {len(_PIECES)}"
        )
    return _PIECES


def _palette_hex(palette_rgb: np.ndarray) -> list[str]:
    out = []
    for r, g, b in palette_rgb:
        out.append(f"#{int(r):02x}{int(g):02x}{int(b):02x}")
    return out


def get_polygons(n: int):
    """
    Design n (1-based) -> cells + per-design palette.

    Each cell is a triangular facet from the same tessellation as the PDF book.
    color_idx is 0-based into the design's quantized palette.
    Coordinates are normalized to roughly [-0.5, 0.5]² centered, so the SVG
    viewBox auto-fit and number sizing stay consistent across designs.
    """
    piece = _pieces()[n - 1]
    src = Image.open(piece["src"]).convert("RGB")
    quant, palette = quantize(src, piece["colors"])
    # Work in a square art canvas (same aspect handling as generate_cbn, simplified)
    # Resize to fixed working resolution for stable polygon density.
    art_size = 900
    ar = quant.width / quant.height
    if ar >= 1:
        art_w, art_h = art_size, max(1, int(art_size / ar))
    else:
        art_h, art_w = art_size, max(1, int(art_size * ar))
    art = quant.resize((art_w, art_h), Image.Resampling.LANCZOS)
    art_px = np.asarray(art)

    # Scale side_length from original book settings (tuned for ~letter art)
    # Original side ~84-94 on ~2000px art → scale to our art_w.
    # Book art width is roughly 2200px; keep similar relative density.
    ref_w = 2200.0
    side = max(28, int(piece["side"] * (art_w / ref_w)))

    # Normalize: map art to centered unit-ish box (max dimension = 1)
    scale = 1.0 / max(art_w, art_h)
    ox, oy = art_w / 2.0, art_h / 2.0

    cells = []
    for pts, (sx, sy) in _iter_cells("triangular", art_w, art_h, side):
        ix = min(art_w - 1, max(0, int(sx)))
        iy = min(art_h - 1, max(0, int(sy)))
        color = tuple(int(c) for c in art_px[iy, ix])
        # _nearest_number returns 1-based index
        color_idx = _nearest_number(color, palette) - 1

        norm = [((x - ox) * scale, (y - oy) * scale) for x, y in pts]
        try:
            poly = shapely.geometry.Polygon(norm)
        except Exception:
            continue
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.area < CFG.area_threshold:
            continue

        cells.append({
            "poly": poly,
            "color_idx": color_idx,
            "dist": float(np.hypot((sx - ox) * scale, (sy - oy) * scale)),
        })

    return {"cells": cells, "palette": _palette_hex(palette)}


if __name__ == "__main__":
    print("Building Geometric CBN Interactive SVG bundle...")
    print(f"  sources -> {SRC_DIR}")
    # Ensure generative sources exist
    _pieces()
    build_svg_bundle(CFG, get_polygons)
