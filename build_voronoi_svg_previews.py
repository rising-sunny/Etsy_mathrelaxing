"""
build_voronoi_svg_previews.py
Generates preview images and promo video for Voronoi Gardens Interactive SVG.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import brand
from build_voronoi_ipad_svg import CFG, get_polygons, PALETTE_HEX

OUT_DIR = "ipad_voronoi_cbn_svg"
PREVIEWS_DIR = os.path.join(OUT_DIR, "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

def get_cells(n, reverse_sort=True):
    cells = get_polygons(n)
    # Sort cells
    cells.sort(key=lambda c: c["dist"], reverse=reverse_sort)
    # The cells are already centered at (0,0) and have dist and color_idx
    # We need to find R_out to calculate scale. RDISK is 120, wait, it's imported in the generator, but we can just use a fixed max dist or find the max bounds.
    R_out = max(c["dist"] for c in cells) if cells else 1.0
    return cells, R_out

def draw_palette(ax, x, y, w, h, palette):
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
    # Use max(w,h) or min(w,h) depending on how we want it to fit.
    # For Voronoi (circle), min(w,h) is good.
    scale = (min(w, h) / (2 * R_out)) * zoom
    clip_rect = Rectangle((cx - w/2, cy - h/2), w, h, transform=ax.transData)
    
    for i, cell in enumerate(cells):
        is_colored = i < colored_count
        color = PALETTE_HEX[cell["color_idx"]] if is_colored else "white"
        
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
    
    cells, R_out = get_cells(10) # 10 is Cathedral
    colored_count = int(len(cells) * 0.45)
    
    scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 5, 5, 8, 6)
    
    draw_design(ax, cells, R_out, colored_count, scr_x + scr_w/2, scr_y + scr_h/2 + 0.3, scr_w, scr_h - 0.6)
    draw_palette(ax, scr_x, scr_y, scr_w, 0.6, PALETTE_HEX)
    
    ax.text(5, 9.2, "Voronoi Gardens", ha="center", va="center", 
            fontsize=55, color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.5, "Interactive Color By Number", ha="center", va="center", 
            fontsize=30, color=brand.GOLD, **brand.SERIF)
            
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_1_hero.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 1")

def build_preview_2():
    fig, ax = brand.ipad_fig()
    
    cells, R_out = get_cells(30) # 30 is organic/floral
    
    scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 7.5, 4.5, 4, 3)
    draw_design(ax, cells, R_out, int(len(cells)*0.8), scr_x + scr_w/2, scr_y + scr_h/2 + 0.3, scr_w, scr_h - 0.6)
    draw_palette(ax, scr_x, scr_y, scr_w, 0.6, PALETTE_HEX)
    
    ax.text(5, 9.2, "How It Works", ha="center", va="center", 
            fontsize=55, color=brand.CREAM, **brand.SERIF_BOLD)
            
    features = [
        (7.0, "1. Select a Color", "Tap any number on the palette to select it"),
        (5.0, "2. Tap to Fill", "Tap matching zones to fill them instantly"),
        (3.0, "3. Relax & Enjoy", "Create stunning cellular designs")
    ]
    
    for y, title, desc in features:
        ax.text(1.5, y, title, ha="left", va="bottom", fontsize=28, color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(1.5, y-0.4, desc, ha="left", va="top", fontsize=18, color=brand.CREAM, **brand.SERIF)
    
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_2_features.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 2")

def build_preview_3():
    fig, ax = brand.ipad_fig()
    
    cells1, R_out1 = get_cells(1)
    cells2, R_out2 = get_cells(15)
    cells3, R_out3 = get_cells(45)
    
    ax.text(5, 9.0, "What's Included", ha="center", va="center", 
            fontsize=45, color=brand.CREAM, **brand.SERIF_BOLD)
            
    # Draw mini iPads
    cx, cy, cw, ch = brand.ipad_frame(ax, 2, 6.5, 3.5, 2.6)
    draw_design(ax, cells1, R_out1, len(cells1), cx + cw/2, cy + ch/2, cw, ch)
    
    cx, cy, cw, ch = brand.ipad_frame(ax, 5, 6.5, 3.5, 2.6)
    draw_design(ax, cells2, R_out2, len(cells2), cx + cw/2, cy + ch/2, cw, ch)
    
    cx, cy, cw, ch = brand.ipad_frame(ax, 8, 6.5, 3.5, 2.6)
    draw_design(ax, cells3, R_out3, len(cells3), cx + cw/2, cy + ch/2, cw, ch)
    
    items = [
        "50 Interactive Designs",
        "Infinite SVG Zoom",
        "Auto-Save Progress",
        "Works Offline in Safari",
        "Instructions PDF"
    ]
    
    for i, item in enumerate(items):
        y = 4.4 - i * 0.65
        ax.text(2.5, y, "•", ha="right", va="center", fontsize=28, color=brand.GOLD, **brand.SERIF_BOLD) 
        ax.text(3.0, y, item, ha="left", va="center", fontsize=26, color=brand.CREAM, **brand.SERIF)
        
    brand.footer_band(ax, 10, 1.5)
    
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_3_included.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated preview 3")
    
def build_promo_video():
    frames_dir = os.path.join(OUT_DIR, "promo_frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    cells1, R_out1 = get_cells(4, reverse_sort=True) # Cathedral 12-fold
    total_cells1 = len(cells1)
    
    cells2, R_out2 = get_cells(15, reverse_sort=False) # Different design for sequence 2
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
            
        draw_palette(ax, scr_x, scr_y, scr_w, 0.6, PALETTE_HEX)
        
        ax.text(5, 9.0, "Interactive Color By Number", ha="center", va="center", 
                fontsize=40, color=brand.CREAM, **brand.SERIF_BOLD)
                
        brand.footer_band(ax, 10, 1.5)
        
        out = os.path.join(frames_dir, f"f_{f:04d}.png")
        fig.savefig(out, dpi=100)
        plt.close(fig)
        
        if f % 10 == 0:
            print(f"  Frame {f}/{n_frames}")
            
    out_video = os.path.join(OUT_DIR, "VoronoiGardens_SVG_promo.mp4")
    print(f"Encoding video {out_video}...")
    brand.encode_mp4(frames_dir, out_video, fps=30, cleanup=True)
    print("Video generated")

if __name__ == "__main__":
    build_preview_1()
    build_preview_2()
    build_preview_3()
    build_promo_video()
