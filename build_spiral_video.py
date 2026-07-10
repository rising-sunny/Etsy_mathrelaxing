"""
build_spiral_video.py — Promo MP4 for the Spiral Tilings coloring book.
A spiral design fills with color from the center outward.
"""

import os
import math
import shutil
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Polygon

import brand
import generate_spiral_tilings as gs

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "spiral_video_out")
FRAMES = os.path.join(OUT, "_frames")

# We can use a nice palette like the Celtic one or generate a custom one.
FILL_COLORS = ["#2e6b4f", "#3f8f6b", "#2f7d7b", "#c9a24b", "#b9762f", "#9c3b2e", "#6b4a8a", "#31597f"]
NAVY = brand.IPAD_NAVY
CREAM = brand.CREAM
TEAL = brand.IPAD_TEAL

S = 10.8
CARD = (1.35, 1.35, 8.1, 8.1)

def get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx):
    """
    Returns a list of dicts: {"poly": np.array of shape (M, 2), "d": distance_from_center, "ij": (i, j)}
    """
    edge_h_fn = gs.EDGE_TYPES[edge_h_idx]
    edge_v_fn = gs.EDGE_TYPES[edge_v_idx]
    
    R_in = 0.05
    x_min = math.log(R_in)
    x_max = math.log(R_out)
    
    i_min = int(math.floor(x_min / H))
    i_max = int(math.ceil(x_max / H))
    
    t_vals = np.linspace(0, 1, 15)
    
    # Precompute all edges to avoid recomputing and ensure exact matching
    edges_h = {} # (i, j) -> array of complex points
    edges_v = {} # (i, j) -> array of complex points
    
    for i in range(i_min, i_max + 2):
        x_i = i * H
        x_next = (i + 1) * H
        for j in range(N):
            y_j = j * (2 * math.pi / N) + i * shift
            y_next_j = (j + 1) * (2 * math.pi / N) + i * shift
            y_j_up = j * (2 * math.pi / N) + (i + 1) * shift
            
            # h edge
            A_h = x_i + 1j * y_j
            B_h = x_i + 1j * y_next_j
            edges_h[(i, j)] = A_h + edge_h_fn(t_vals) * (B_h - A_h)
            
            # v edge
            A_v = x_i + 1j * y_j
            B_v = x_next + 1j * y_j_up
            edges_v[(i, j)] = A_v + edge_v_fn(t_vals) * (B_v - A_v)
            
    tiles = []
    
    for i in range(i_min, i_max + 1):
        for j in range(N):
            j_next = (j + 1) % N
            
            x_i = i * H
            x_next = (i + 1) * H
            y_j = j * (2 * math.pi / N) + i * shift
            y_next_j = (j + 1) * (2 * math.pi / N) + i * shift
            y_j_up = j * (2 * math.pi / N) + (i + 1) * shift
            y_next_j_up = (j + 1) * (2 * math.pi / N) + (i + 1) * shift
            
            A_h_in = x_i + 1j * y_j
            B_h_in = x_i + 1j * y_next_j
            path_inner = A_h_in + edge_h_fn(t_vals) * (B_h_in - A_h_in)
            
            A_v_right = x_i + 1j * y_next_j
            B_v_right = x_next + 1j * y_next_j_up
            path_right = A_v_right + edge_v_fn(t_vals) * (B_v_right - A_v_right)
            
            A_h_out = x_next + 1j * y_j_up
            B_h_out = x_next + 1j * y_next_j_up
            path_outer = A_h_out + edge_h_fn(t_vals) * (B_h_out - A_h_out)
            
            A_v_left = x_i + 1j * y_j
            B_v_left = x_next + 1j * y_j_up
            path_left = A_v_left + edge_v_fn(t_vals) * (B_v_left - A_v_left)
            
            # Combine them: inner, right, reverse(outer), reverse(left)
            cell_path_c = np.concatenate([
                path_inner[:-1], 
                path_right[:-1], 
                path_outer[::-1][:-1], 
                path_left[::-1][:-1]
            ])
            
            mapped = np.exp(cell_path_c)
            poly_pts = np.column_stack((cx + mapped.real, cy + mapped.imag))
            
            # Calculate distance of centroid from center
            centroid = np.mean(poly_pts, axis=0)
            d = math.hypot(centroid[0] - cx, centroid[1] - cy)
            
            # Only add if it's within the canvas bounding circle (roughly)
            if d < R_out * 1.5:
                tiles.append({"poly": poly_pts, "d": d, "ij": (i, j)})
                
    tiles.sort(key=lambda t: t["d"])
    return tiles

def setup_ax():
    fig = plt.figure(figsize=(S, S), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, S); ax.set_ylim(0, S); ax.set_aspect("equal")
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    
    ax.text(S / 2, S - 0.62, "Spiral Tilings  ·  Digital Edition", ha="center",
            fontsize=21, family="serif", color=CREAM, zorder=6)
            
    cx0, cy0, w, h = CARD
    ax.add_patch(FancyBboxPatch((cx0, cy0), w, h,
                 boxstyle="round,pad=0,rounding_size=0.18", facecolor="white",
                 edgecolor="#3a3f52", lw=1.5, zorder=0.2))
                 
    ax.text(S / 2, 0.72, "mathrelaxing.store", ha="center",
            fontsize=14, color=TEAL, zorder=6)
            
    logo = mpimg.imread(brand.LOGO_PATH)
    lw = 1.5; lh = lw * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(S / 2 - lw / 2, S / 2 + lw / 2, 0.2, 0.2 + lh), zorder=6)
    return fig, ax

def render_design_animation(design_idx, frame, cx, cy, R_out):
    design = gs._plan()[design_idx]
    N, H, shift, edge_h_idx, edge_v_idx, lw = design
    print(f"Building tiles for design {design_idx}...")
    tiles = get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx)
    
    fig, ax = setup_ax()
    
    circle = plt.Circle((cx, cy), 0.15, color="white", zorder=4)
    circle_outline = plt.Circle((cx, cy), 0.15, color="black", fill=False, lw=lw, zorder=5)
    ax.add_patch(circle)
    ax.add_patch(circle_outline)
    
    bound = plt.Circle((cx, cy), R_out, color="black", fill=False, lw=lw*2, zorder=5)
    ax.add_patch(bound)
    
    clip_path = plt.Circle((cx, cy), R_out, transform=ax.transData)
    
    print(f"Drawing {len(tiles)} polygons for design {design_idx}...")
    for t in tiles:
        poly = Polygon(t["poly"], closed=True, fill=False, edgecolor="black", lw=lw, zorder=3)
        poly.set_clip_path(clip_path)
        ax.add_patch(poly)

    n_tiles = len(tiles)
    hold_start, reveal_frames, hold_end = 10, 90, 30
    revealed = 0

    def save():
        nonlocal frame
        fig.savefig(os.path.join(FRAMES, f"f_{frame:04d}.png"), facecolor=NAVY, dpi=100)
        frame += 1

    print("Rendering animation...")
    for _ in range(hold_start):
        save()
        
    for k in range(reveal_frames):
        target = round((k + 1) / reveal_frames * n_tiles)
        while revealed < target and revealed < n_tiles:
            t = tiles[revealed]
            fill_color = FILL_COLORS[(t["ij"][0] * 3 + t["ij"][1] * 7) % len(FILL_COLORS)]
            poly_fill = Polygon(t["poly"], closed=True, fill=True, facecolor=fill_color, edgecolor="none", zorder=2)
            poly_fill.set_clip_path(clip_path)
            ax.add_patch(poly_fill)
            revealed += 1
        save()
        if k % 20 == 0:
            print(f"Frame {frame} ({revealed}/{n_tiles} tiles)")
            
    while revealed < n_tiles:
        t = tiles[revealed]
        fill_color = FILL_COLORS[(t["ij"][0] * 3 + t["ij"][1] * 7) % len(FILL_COLORS)]
        poly_fill = Polygon(t["poly"], closed=True, fill=True, facecolor=fill_color, edgecolor="none", zorder=2)
        poly_fill.set_clip_path(clip_path)
        ax.add_patch(poly_fill)
        revealed += 1
        
    for _ in range(hold_end):
        save()
        
    plt.close(fig)
    return frame

def main():
    if not os.path.exists(OUT):
        os.makedirs(OUT)
    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES, exist_ok=True)

    cx = S / 2
    cy = CARD[1] + CARD[3] / 2
    R_out = 4.0
    
    frame = 0
    # 3 different designs to showcase
    for d_idx in [14, 28, 42]:
        frame = render_design_animation(d_idx, frame, cx, cy, R_out)
        
    print(f"Total {frame} frames renderizados")

    out_file = os.path.join(OUT, "SpiralTilings_promo.mp4")
    brand.encode_mp4(FRAMES, out_file, fps=30, pattern="f_%04d.png", crf=20)
    print("Video listo:", out_file)

if __name__ == "__main__":
    main()
