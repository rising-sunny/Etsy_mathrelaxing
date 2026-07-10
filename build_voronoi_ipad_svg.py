"""
build_voronoi_ipad_svg.py — Interactive SVG edition of Voronoi Gardens CBN
=========================================================================
Uses the reusable template_ipad_svg_bundle framework.
"""
import os
import sys
import math
import numpy as np
import shapely.geometry
from scipy.spatial import Voronoi

# Add lulu_books/generators to path to import make_voronoi_book
sys.path.append(os.path.join(os.path.dirname(__file__), "lulu_books", "generators"))
from make_voronoi_book import DESIGNS, RDISK, CX, CY, VORONOI_PALETTE, _disk_polygon

from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle

# Convert RGB (0-255) to hex
PALETTE_HEX = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in VORONOI_PALETTE]

# ── Configuration ─────────────────────────────────────────────────────────────

CFG = SvgBundleConfig(
    out_dir="ipad_voronoi_cbn_svg",
    prefix="VoronoiGardens_CBN",
    title="Voronoi Gardens",
    palette=PALETTE_HEX,
    n_designs=50,
    stroke_color="#1A1D24",
    font_min=1.0,
    font_max=15.0,
)

# ── Polygon generator ────────────────────────────────────────────────────────

def _clip_polygon(coords, clip_poly):
    """Clip a list of coordinates with a shapely polygon."""
    if len(coords) < 3:
        return None
    p = shapely.geometry.Polygon(coords)
    if not p.is_valid:
        p = p.buffer(0)
    inter = p.intersection(clip_poly)
    if inter.is_empty:
        return None
        
    return inter

def get_polygons(n):
    """
    For design n (1-based), generate all Color-By-Number cells.
    Returns list of {"poly": shapely.Polygon, "color_idx": int}.
    """
    cfg = DESIGNS[n - 1]
    seed = n + 100
    sym = cfg.get("sym", 0)
    
    # Generate points
    pts = cfg["fn"](seed)
    
    # Generate Voronoi
    vor = Voronoi(pts)
    
    # Bounding disk for clipping
    disk_coords = _disk_polygon(0, 0, RDISK)
    clip_poly = shapely.geometry.Polygon(disk_coords)
    
    cells = []
    
    for i in range(len(pts)):
        reg_idx = vor.point_region[i]
        if reg_idx == -1:
            continue
            
        reg = vor.regions[reg_idx]
        if not reg or -1 in reg:
            continue
            
        # The coordinates are centered at (CX, CY), we want them centered at (0,0)
        coords = [(vor.vertices[v][0] - CX, vor.vertices[v][1] - CY) for v in reg]
        clipped = _clip_polygon(coords, clip_poly)
        if clipped is None:
            continue
            
        # Calculate color index using point index `i` to guarantee symmetry
        if sym > 0:
            color_idx = ((i // sym) * 7) % 30
        else:
            color_idx = (i * 7 + i % 13) % 30
            
        # Optional: Add dist for previews
        pt_x, pt_y = pts[i]
        dist = math.hypot(pt_x - CX, pt_y - CY)
        
        cells.append({
            "poly": clipped,
            "color_idx": color_idx,
            "dist": dist
        })
        
    return cells

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_svg_bundle(CFG, get_polygons)
