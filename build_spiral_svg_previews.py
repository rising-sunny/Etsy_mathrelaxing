"""
build_spiral_svg_previews.py
Generates preview images and a promo video for the Interactive SVG Color-By-Number product.
"""

import os
import shapely.geometry
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import brand
from generate_spiral_tilings import PASTEL_PALETTE, get_spiral_tiles, _plan, PAGE_W, PAGE_H

OUT_DIR = "ipad_spiral_cbn_svg"
PREVIEWS_DIR = os.path.join(OUT_DIR, "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

# Helper to get colored cells for a design
def get_cells(n, reverse_sort=True):
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
        
        # Calculate distance from center to order them from outside to inside
        pt = clipped.representative_point()
        dist = ((pt.x - cx)**2 + (pt.y - cy)**2)**0.5
        
        cells.append({
            "poly": clipped,
            "color_idx": c_idx,
            "dist": dist
        })
        
    # Sort cells
    cells.sort(key=lambda c: c["dist"], reverse=reverse_sort)
    
    # Adjust coordinates to be centered at (0,0) for plotting
    for c in cells:
        geoms = [c["poly"]] if c["poly"].geom_type == 'Polygon' else list(c["poly"].geoms)
        new_geoms = []
        for g in geoms:
            coords = list(g.exterior.coords)
            new_coords = [(x - cx, y - cy) for x, y in coords]
            new_geoms.append(shapely.geometry.Polygon(new_coords))
        if len(new_geoms) == 1:
            c["poly"] = new_geoms[0]
        else:
            c["poly"] = shapely.geometry.MultiPolygon(new_geoms)
            
    return cells, R_out

def draw_palette(ax, x, y, w, h, palette):
    """Draw a simple palette bar at the bottom."""
    ax.add_patch(plt.Rectangle((x, y), w, h, color="#1A1D24", zorder=10))
    n_colors = len(palette)
    swatch_w = min((w - 0.2) / n_colors, h * 0.8)
    padding = (w - n_colors * swatch_w) / 2
    for i, color in enumerate(palette):
        cx = x + padding + i * swatch_w + swatch_w / 2
        cy = y + h / 2
        ax.add_patch(plt.Circle((cx, cy), swatch_w * 0.4, color=color, zorder=11))

def draw_design(ax, cells, R_out, colored_count, cx, cy, w, h, zoom=1.0):
    """Draw the design inside a specific area (cx, cy, w, h)."""
    scale = (min(w, h) / (2 * R_out)) * zoom
    clip_rect = Rectangle((cx - w/2, cy - h/2), w, h, transform=ax.transData)
    
    for i, cell in enumerate(cells):
        is_colored = i < colored_count
        color = PASTEL_PALETTE[cell["color_idx"]] if is_colored else "white"
        
        geoms = [cell["poly"]] if cell["poly"].geom_type == 'Polygon' else list(cell["poly"].geoms)
        for g in geoms:
            coords = list(g.exterior.coords)
            xs = [cx + x * scale for x, _ in coords]
            ys = [cy + y * scale for _, y in coords]
            
            patches = ax.fill(xs, ys, color=color, edgecolor="black", linewidth=0.5, zorder=3)
            for p in patches:
                p.set_clip_path(clip_rect)
            
            if not is_colored:
                pt = g.representative_point()
                clearance = g.boundary.distance(pt)
                # Convert clearance to points: clearance * scale (inches) * 72 (points/inch) * factor
                fs = clearance * scale * 72.0 * 0.8
                fs = max(2.0, min(20.0, fs))
                t = ax.text(cx + pt.x * scale, cy + pt.y * scale, str(cell["color_idx"] + 1), 
                        ha="center", va="center", fontsize=fs, color="#1A1D24", zorder=4,
                        **brand.SANS)
                t.set_clip_path(clip_rect)

def build_preview_1():
    fig, ax = brand.ipad_fig()
    ax.text(5, 8.5, "Interactive Color By Number", ha="center", va="center", 
            fontsize=40, color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 7.7, "Spiral Tilings · 50 Math Designs", ha="center", va="center", 
            fontsize=25, color=brand.GOLD, **brand.SERIF)
            
    scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 5, 4.0, 6.0, 4.5)
    
    cells, R_out = get_cells(10)
    colored = int(len(cells) * 0.4)
    
    draw_design(ax, cells, R_out, colored, scr_x + scr_w/2, scr_y + scr_h/2 + 0.2, scr_w, scr_h - 0.4)
    draw_palette(ax, scr_x, scr_y, scr_w, 0.4, PASTEL_PALETTE)
    
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_1_hero.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 1")

def build_preview_2():
    fig, ax = brand.ipad_fig()
    
    ax.text(5, 8.8, "How It Works", ha="center", va="center", 
            fontsize=45, color=brand.CREAM, **brand.SERIF_BOLD)
            
    features = [
        (7.0, "1. Select a Color", "Tap any number on the palette to select it"),
        (5.0, "2. Tap to Fill", "Tap matching zones to fill them instantly"),
        (3.0, "3. Zoom Infinitely", "Vector graphics mean perfectly crisp lines")
    ]
    
    for y, title, desc in features:
        ax.text(1, y, title, ha="left", va="bottom", fontsize=28, color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(1, y-0.4, desc, ha="left", va="top", fontsize=18, color=brand.CREAM, **brand.SERIF)
        
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_2_features.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 2")

def build_preview_3():
    fig, ax = brand.ipad_fig()
    
    ax.text(5, 8.5, "What's Included", ha="center", va="center", 
            fontsize=45, color=brand.CREAM, **brand.SERIF_BOLD)
            
    items = [
        "50 Interactive Designs",
        "Infinite SVG Zoom",
        "Auto-Save Progress",
        "Works Offline in Safari",
        "Instructions PDF"
    ]
    
    for i, item in enumerate(items):
        y = 6.5 - i * 0.9
        ax.text(2, y, "•", ha="right", va="center", fontsize=30, color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(2.5, y, item, ha="left", va="center", fontsize=28, color=brand.CREAM, **brand.SERIF)
        
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_3_included.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 3")
    
def build_promo_video():
    frames_dir = os.path.join(OUT_DIR, "promo_frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    cells1, R_out1 = get_cells(10, reverse_sort=True)
    total_cells1 = len(cells1)
    
    cells2, R_out2 = get_cells(25, reverse_sort=False)
    total_cells2 = len(cells2)
    
    n_frames_1 = 150
    n_frames_2 = 150
    n_frames = n_frames_1 + n_frames_2
    
    print(f"Generating {n_frames} frames for promo video...")
    
    for f in range(n_frames):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.axis("off")
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        fig.patch.set_facecolor(brand.IPAD_NAVY); ax.set_facecolor(brand.IPAD_NAVY)
        
        scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 5, 5, 8, 6)
        
        if f < n_frames_1:
            if f < 120:
                colored = int((f / 120) * total_cells1)
            else:
                colored = total_cells1
            zoom = 1.0
            draw_design(ax, cells1, R_out1, colored, scr_x + scr_w/2, scr_y + scr_h/2 + 0.3, scr_w, scr_h - 0.6, zoom=zoom)
        else:
            f2 = f - n_frames_1
            if f2 < 120:
                colored = int((f2 / 120) * total_cells2)
                progress = f2 / 120.0
                zoom = 4.0 - 3.0 * (progress ** 1.5)  # Easing
            else:
                colored = total_cells2
                zoom = 1.0
            draw_design(ax, cells2, R_out2, colored, scr_x + scr_w/2, scr_y + scr_h/2 + 0.3, scr_w, scr_h - 0.6, zoom=zoom)
            
        draw_palette(ax, scr_x, scr_y, scr_w, 0.6, PASTEL_PALETTE)
        
        ax.text(5, 9.0, "Interactive Color By Number", ha="center", va="center", 
                fontsize=40, color=brand.CREAM, **brand.SERIF_BOLD)
                
        brand.footer_band(ax, 10, 1.5)
        
        out = os.path.join(frames_dir, f"f_{f:04d}.png")
        fig.savefig(out, dpi=100)
        plt.close(fig)
        
        if f % 10 == 0:
            print(f"  Frame {f}/{n_frames}")
            
    out_video = os.path.join(OUT_DIR, "SpiralTilings_SVG_promo.mp4")
    print(f"Encoding video {out_video}...")
    brand.encode_mp4(frames_dir, out_video, fps=30, cleanup=True)
    print("Video generated")

if __name__ == "__main__":
    build_preview_1()
    build_preview_2()
    build_preview_3()
    build_promo_video()
