"""
build_spiral_ipad.py — Spiral Tilings iPad Edition (Color By Number)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math

import brand
import generate_spiral_tilings as gs
import template_ipad_bundle as tib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "ipad_spiral_cbn")
PNG_DIR = os.path.join(OUT, "_png")
os.makedirs(PNG_DIR, exist_ok=True)

CFG = tib.BundleConfig(
    out_dir=OUT,
    prefix="SpiralTilings_CBN",
    edition="Spiral Tilings Color-By-Number",
    subtitle_line="Spiral Tilings Color-By-Number   ·   50 Math & Mandala Designs",
    design_word="spiral cells",
    palette_name="MathRelaxing — Pastel Dreams",
    palette_hexes=gs.PASTEL_PALETTE,
    n_designs=50,
    included=[
        "50 unique color-by-number spiral designs",
        "Hyperlinked PDF index for GoodNotes & Notability",
        "50 transparent PNGs (300 dpi) for Procreate",
        "Procreate palette  ·  30 curated pastel swatches",
        "'How to use on iPad' quick guide",
        "Instant download  ·  personal use",
    ],
)

def render_design_fig_cbn(n):
    return gs.render_design(n, cbn=True)

def render_showcase(colored, path, size_in=6.0, design_idx=14):
    fig = plt.figure(figsize=(size_in, size_in))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, size_in); ax.set_ylim(0, size_in); ax.set_aspect("equal")
    
    cx, cy = size_in / 2, size_in / 2
    R_out = size_in / 2 - 0.2
    
    N, H, shift, edge_h_idx, edge_v_idx, lw = gs._plan(cbn=True)[design_idx]
    tiles = gs.get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx)
    
    clip_path = plt.Circle((cx, cy), R_out, transform=ax.transData)
    
    import shapely.geometry
    circle_shape = shapely.geometry.Point(cx, cy).buffer(R_out - 0.05)
    
    for t in tiles:
        poly_shape = shapely.geometry.Polygon(t["poly"]).buffer(0)  # fix self-intersections
        if poly_shape.is_empty:
            continue
        clipped = poly_shape.intersection(circle_shape)
        if clipped.is_empty or clipped.area < 0.005:
            continue
        
        c_idx = (t["ij"][0] * 3 + t["ij"][1] * 7) % len(gs.PASTEL_PALETTE)
        eroded = clipped.buffer(-0.12)
        
        if colored:
            fill_color = gs.PASTEL_PALETTE[c_idx]
            poly = Polygon(t["poly"], closed=True, fill=True, facecolor=fill_color, edgecolor=gs.LINE_COLOR, lw=lw, zorder=2)
            poly.set_clip_path(clip_path)
            ax.add_patch(poly)
        else:
            if eroded.is_empty or eroded.area < 0.02:
                # Cell too small — pre-color it
                fill_color = gs.PASTEL_PALETTE[c_idx]
                poly = Polygon(t["poly"], closed=True, fill=True, facecolor=fill_color, edgecolor=gs.LINE_COLOR, lw=lw, zorder=2)
                poly.set_clip_path(clip_path)
                ax.add_patch(poly)
                poly_border = Polygon(t["poly"], closed=True, fill=False, edgecolor=gs.LINE_COLOR, lw=lw, zorder=3)
                poly_border.set_clip_path(clip_path)
                ax.add_patch(poly_border)
            else:
                poly = Polygon(t["poly"], closed=True, fill=False, edgecolor=gs.LINE_COLOR, lw=lw, zorder=3)
                poly.set_clip_path(clip_path)
                ax.add_patch(poly)
                
                pt = eroded.representative_point()
                x_c, y_c = pt.x, pt.y
                fs = max(2.0, min(7.0, math.sqrt(eroded.area) * 10))
                ax.text(x_c, y_c, str(c_idx + 1), ha="center", va="center", 
                        fontsize=fs, color="#808080", zorder=4, **brand.SANS)
                        
    circle = plt.Circle((cx, cy), 0.15, color="white", zorder=10)
    circle_outline = plt.Circle((cx, cy), 0.15, color=gs.LINE_COLOR, fill=False, lw=lw, zorder=11)
    ax.add_patch(circle)
    ax.add_patch(circle_outline)
    bound = plt.Circle((cx, cy), R_out, color=gs.LINE_COLOR, fill=False, lw=lw*2, zorder=11)
    ax.add_patch(bound)

    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)

def main():
    line_png = os.path.join(PNG_DIR, "_showcase_line.png")
    colored_png = os.path.join(PNG_DIR, "_showcase_colored.png")
    render_showcase(False, line_png)
    render_showcase(True, colored_png)
    tib.build(CFG, render_design_fig_cbn, line_png, colored_png)

if __name__ == "__main__":
    main()
