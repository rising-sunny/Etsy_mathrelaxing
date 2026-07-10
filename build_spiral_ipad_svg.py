"""
build_spiral_ipad_svg.py — Interactive SVG edition of Spiral Tilings CBN
=========================================================================
Uses the reusable template_ipad_svg_bundle framework.
Supplies: SvgBundleConfig + get_polygons(n) -> list of cell dicts.
"""
import math
import shapely.geometry
from generate_spiral_tilings import PASTEL_PALETTE, get_spiral_tiles, _plan, PAGE_W, PAGE_H
from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle


# ── Configuration ─────────────────────────────────────────────────────────────

CFG = SvgBundleConfig(
    out_dir="ipad_spiral_cbn_svg",
    prefix="SpiralTilings_CBN",
    title="Spiral Tilings",
    palette=PASTEL_PALETTE,
    n_designs=50,
    stroke_color="black",
)


# ── Polygon generator ────────────────────────────────────────────────────────

def get_polygons(n):
    """
    For design n (1-based), generate all Color-By-Number cells.
    Returns list of {"poly": shapely.Polygon, "color_idx": int}.
    """
    plan = _plan(cbn=True)
    N, H, shift, edge_h_idx, edge_v_idx, lw = plan[n - 1]
    cx, cy = PAGE_W / 2, PAGE_H / 2 + 0.7
    R_out = 4.0

    tiles = get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx)
    circle_shape = shapely.geometry.Point(cx, cy).buffer(R_out - 0.05)

    cells = []
    for t in tiles:
        poly_shape = shapely.geometry.Polygon(t["poly"]).buffer(0)
        if poly_shape.is_empty:
            continue
        clipped = poly_shape.intersection(circle_shape)
        if clipped.is_empty:
            continue

        c_idx = (t["ij"][0] * 3 + t["ij"][1] * 7) % len(PASTEL_PALETTE)
        cells.append({
            "poly": clipped,
            "color_idx": c_idx,
        })

    return cells


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_svg_bundle(CFG, get_polygons)
