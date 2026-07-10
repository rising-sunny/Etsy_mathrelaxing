"""
generate_spiral_tilings.py — MathRelaxing "Spiral Tilings" generator
=============================================================================
Genera 50 diseños de teselaciones en espiral mediante mapeo conforme
(transformación exponencial de una cuadrícula en el plano complejo).
"""

import math
import random
import os
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import brand
import template_coloring_book as tcb

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 8.5, 11.0
LINE_COLOR = "black"

BG_DARK = "#1A1D24" # Un azul/gris oscuro profundo
GOLD = brand.GOLD
CREAM = brand.CREAM

PASTEL_PALETTE = [
    "#ffd1dc", "#ffb7b2", "#ffdac1", "#e2f0cb", "#b5ead7", "#c7ceea",
    "#f4c2d7", "#d8b4e2", "#ae98d6", "#8b9dc3", "#98b9d2", "#a6dcef",
    "#a8e6cf", "#dcedc1", "#ffd3b6", "#ffaaa5", "#ff8b94", "#e7b1b1",
    "#e2c4c4", "#d5c1b8", "#c8b0a5", "#a9c2c9", "#8ba9b0", "#7c9399",
    "#b8d8d8", "#7a9e9f", "#4f6272", "#f0e6ef", "#e5d4ed", "#cfbaf0"
]

# ─────────────────────────────────────────────────────────────────────────
# Edge Deformations
# ─────────────────────────────────────────────────────────────────────────

def edge_straight(t):
    return t

def edge_zigzag(t, amp=0.15, flips=1):
    # Zigzag with multiple bumps
    t_scaled = t * flips
    frac = t_scaled - np.floor(t_scaled)
    # triangle wave: 0 -> amp -> 0 -> -amp -> 0
    wave = 1 - 4 * np.abs(frac - 0.5)
    wave = wave * amp
    # ensure endpoints are exactly 0
    wave = wave * np.sin(t * np.pi) 
    return t + wave * 1j

def edge_wave(t, amp=0.15, freq=1.0):
    return t + amp * np.sin(t * np.pi * freq) * 1j

def edge_square(t, amp=0.15, flips=1):
    wave = np.sin(t * np.pi * flips)
    wave = np.sign(wave) * amp
    wave = wave * np.sin(t * np.pi) # taper at ends
    return t + wave * 1j

def edge_interlock(t, amp=0.2):
    # Jigsaw like
    offset = np.zeros_like(t, dtype=complex)
    for i, tv in enumerate(t):
        if tv < 0.3:
            offset[i] = 0
        elif tv < 0.5:
            offset[i] = amp * 1j * (tv - 0.3) / 0.2
        elif tv < 0.7:
            offset[i] = amp * 1j * (0.7 - tv) / 0.2
        else:
            offset[i] = 0
    return t + offset

EDGE_TYPES = [
    lambda t: edge_straight(t),
    lambda t: edge_zigzag(t, amp=0.2, flips=1),
    lambda t: edge_zigzag(t, amp=0.15, flips=2),
    lambda t: edge_wave(t, amp=0.2, freq=1),
    lambda t: edge_wave(t, amp=0.15, freq=2),
    lambda t: edge_square(t, amp=0.15, flips=2),
    lambda t: edge_interlock(t, amp=0.25),
    lambda t: edge_zigzag(t, amp=-0.2, flips=1),
    lambda t: edge_wave(t, amp=-0.2, freq=1)
]

# ─────────────────────────────────────────────────────────────────────────
# Spiral Generator
# ─────────────────────────────────────────────────────────────────────────

def get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx):
    edge_h_fn = EDGE_TYPES[edge_h_idx]
    edge_v_fn = EDGE_TYPES[edge_v_idx]
    
    R_in = 0.05
    x_min = math.log(R_in)
    x_max = math.log(R_out)
    
    i_min = int(math.floor(x_min / H))
    i_max = int(math.ceil(x_max / H))
    
    t_vals = np.linspace(0, 1, 15)
    tiles = []
    
    for i in range(i_min, i_max + 1):
        for j in range(N):
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
            
            cell_path_c = np.concatenate([
                path_inner[:-1], 
                path_right[:-1], 
                path_outer[::-1][:-1], 
                path_left[::-1][:-1]
            ])
            
            mapped = np.exp(cell_path_c)
            poly_pts = np.column_stack((cx + mapped.real, cy + mapped.imag))
            
            centroid = np.mean(poly_pts, axis=0)
            d = math.hypot(centroid[0] - cx, centroid[1] - cy)
            
            if d < R_out * 1.5:
                tiles.append({"poly": poly_pts, "centroid": centroid, "d": d, "ij": (i, j)})
                
    tiles.sort(key=lambda t: t["d"])
    return tiles

def draw_spiral_tiling(ax, cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx, lw, color, cbn=False):
    from matplotlib.patches import Polygon
    
    if cbn:
        tiles = get_spiral_tiles(cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx)
        clip_path = plt.Circle((cx, cy), R_out, transform=ax.transData)
        
        for t in tiles:
            x_c, y_c = t["centroid"]
            d = math.hypot(x_c - cx, y_c - cy)
            c_idx = (t["ij"][0] * 3 + t["ij"][1] * 7) % len(PASTEL_PALETTE)
            
            # If the cell is too close to the center, it's very small. We pre-color it.
            if d < 1.2:
                fill_color = PASTEL_PALETTE[c_idx]
                poly = Polygon(t["poly"], closed=True, fill=True, facecolor=fill_color, edgecolor=color, lw=lw, zorder=2)
                poly.set_clip_path(clip_path)
                ax.add_patch(poly)
                # We still want the border on top
                poly_border = Polygon(t["poly"], closed=True, fill=False, edgecolor=color, lw=lw, zorder=3)
                poly_border.set_clip_path(clip_path)
                ax.add_patch(poly_border)
            else:
                poly = Polygon(t["poly"], closed=True, fill=False, edgecolor=color, lw=lw, zorder=3)
                poly.set_clip_path(clip_path)
                ax.add_patch(poly)
                
                if d < R_out - 0.2:
                    ax.text(x_c, y_c, str(c_idx + 1), ha="center", va="center", 
                            fontsize=5, color="#808080", zorder=4, **brand.SANS)
        return
        
    # Standard fast line-drawing
    edge_h_fn = EDGE_TYPES[edge_h_idx]
    edge_v_fn = EDGE_TYPES[edge_v_idx]
    
    R_in = 0.05
    x_min = math.log(R_in)
    x_max = math.log(R_out)
    
    i_min = int(math.floor(x_min / H))
    i_max = int(math.ceil(x_max / H))
    
    t_vals = np.linspace(0, 1, 30)
    
    for i in range(i_min, i_max + 1):
        x_i = i * H
        x_next = (i + 1) * H
        
        for j in range(N):
            y_j = j * (2 * math.pi / N) + i * shift
            y_next_j = (j + 1) * (2 * math.pi / N) + i * shift
            
            y_j_up = j * (2 * math.pi / N) + (i + 1) * shift
            
            A_h = x_i + 1j * y_j
            B_h = x_i + 1j * y_next_j
            path_h_c = A_h + edge_h_fn(t_vals) * (B_h - A_h)
            
            A_v = x_i + 1j * y_j
            B_v = x_next + 1j * y_j_up
            path_v_c = A_v + edge_v_fn(t_vals) * (B_v - A_v)
            
            mapped_h = np.exp(path_h_c)
            mapped_v = np.exp(path_v_c)
            
            X_h = cx + mapped_h.real
            Y_h = cy + mapped_h.imag
            
            X_v = cx + mapped_v.real
            Y_v = cy + mapped_v.imag
            
            ax.plot(X_h, Y_h, lw=lw, color=color, solid_capstyle="round", solid_joinstyle="round")
            ax.plot(X_v, Y_v, lw=lw, color=color, solid_capstyle="round", solid_joinstyle="round")


# ─────────────────────────────────────────────────────────────────────────
# Page scaffolding
# ─────────────────────────────────────────────────────────────────────────
def new_page(bg=None):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect("equal")
    ax.axis("off")
    if bg:
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
    return fig, ax

def emblem(ax, cx, cy, r):
    """Product emblem drawn in gold on the cover."""
    draw_spiral_tiling(ax, cx, cy, r, N=7, H=0.3, shift=0.4, 
                       edge_h_idx=1, edge_v_idx=0, lw=2.5, color=brand.GOLD)
    # White out the center for the logo/text to breathe
    circle = plt.Circle((cx, cy), r * 0.25, color=BG_DARK, zorder=5)
    ax.add_patch(circle)

def watermark(ax, W, H):
    """Faint watermark filling the whole cover."""
    ghost = (0.79, 0.63, 0.29, 0.15)  # gold at low alpha
    draw_spiral_tiling(ax, W/2, H/2, W, N=12, H=0.2, shift=0.6, 
                       edge_h_idx=3, edge_v_idx=3, lw=1.0, color=ghost)

ABOUT_BODY = r"""Spiral tilings are a mesmerizing intersection of complex analysis and art.
By taking a regular Euclidean grid of squares in the complex plane $\mathbb{C}$
and mapping it through the complex exponential function $f(z) = e^z$,
straight lines burst outward into logarithmic spirals of the form
$r = a e^{b\theta}$ that endlessly wrap around a central origin.

Every design in this book is generated mathematically. By tweaking just
three parameters—the number of radial arms $N$, the radial expansion rate $H$,
and the twist shift $\Delta y$—an infinite variety of radial geometries emerge.
We then apply periodic deformations (such as sine waves or zig-zags) to the
edges in the pre-image grid. When mapped, these become interlocking jigsaw
pieces, scales, and floral petals that fit together perfectly without
a single gap or overlap.

Relax, color from the center outward, and watch the math unfold."""

def build_plan(cbn=False):
    plan = []
    rng = random.Random(42)
    for n in range(1, 51):
        progress = n / 50.0
        
        # Increase complexity as we go
        N = int(4 + progress * 24 + rng.randint(-2, 2))
        N = max(3, N)
        if cbn:
            N = min(N, 14)
        
        H = 0.5 - progress * 0.35 + rng.uniform(-0.05, 0.05)
        H = max(0.08, H)
        if cbn:
            H = max(0.2, H)
        
        shift = rng.uniform(0.1, 1.5)
        if rng.random() < 0.2:
            shift = 0.0 # pure concentric rings
            
        edge_h_idx = rng.randint(0, len(EDGE_TYPES) - 1)
        edge_v_idx = rng.randint(0, len(EDGE_TYPES) - 1)
        
        # Sometimes make them both straight or both the same
        if rng.random() < 0.15:
            edge_h_idx = 0
            edge_v_idx = 0
        elif rng.random() < 0.2:
            edge_v_idx = edge_h_idx
            
        lw = 2.0 - progress * 1.2
        lw = max(0.6, lw)
        
        plan.append((N, H, shift, edge_h_idx, edge_v_idx, lw))
    return plan

_PLAN = None
_PLAN_CBN = None

def _plan(cbn=False):
    global _PLAN, _PLAN_CBN
    if cbn:
        if _PLAN_CBN is None:
            _PLAN_CBN = build_plan(cbn=True)
        return _PLAN_CBN
    else:
        if _PLAN is None:
            _PLAN = build_plan(cbn=False)
        return _PLAN

def render_design(n, cbn=False):
    N, H, shift, edge_h_idx, edge_v_idx, lw = _plan(cbn)[n - 1]
    fig, ax = new_page()
    cx, cy = PAGE_W / 2, PAGE_H / 2 + 0.2
    
    if cbn:
        # Move up slightly to make room for palette
        cy = PAGE_H / 2 + 0.7
        
    R_out = 5.0
    if cbn:
        R_out = 4.0
        
    draw_spiral_tiling(ax, cx, cy, R_out, N, H, shift, edge_h_idx, edge_v_idx, lw, LINE_COLOR, cbn=cbn)
    
    circle = plt.Circle((cx, cy), 0.15, color="white", zorder=10)
    circle_outline = plt.Circle((cx, cy), 0.15, color=LINE_COLOR, fill=False, lw=lw, zorder=11)
    ax.add_patch(circle)
    ax.add_patch(circle_outline)
    
    bound = plt.Circle((cx, cy), R_out - 0.2, color=LINE_COLOR, fill=False, lw=lw*2, zorder=11)
    ax.add_patch(bound)
    
    if cbn:
        # Draw color key at the bottom
        cols, rows = 10, 3
        cell_size = 0.5
        ox = PAGE_W / 2 - (cols * cell_size) / 2 + cell_size / 2
        oy = 2.0
        for i, hex_color in enumerate(PASTEL_PALETTE):
            r, c = divmod(i, cols)
            px, py = ox + c * cell_size, oy - r * cell_size
            ax.add_patch(plt.Circle((px, py), 0.18, color=hex_color, zorder=5))
            ax.add_patch(plt.Circle((px, py), 0.18, fill=False, color="black", lw=0.8, zorder=6))
            ax.text(px, py, str(i + 1), ha="center", va="center", fontsize=7, color="black", zorder=7)
    
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    
    return fig

def back_cover_page():
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, PAGE_W); ax.set_ylim(0, PAGE_H)
    fig.patch.set_facecolor(BG_DARK); ax.set_facecolor(BG_DARK)
    
    watermark(ax, PAGE_W, PAGE_H)
    band_h = min(1.6, 0.18 * PAGE_H)
    brand.footer_band(ax, PAGE_W, band_h)
    
    ax.text(PAGE_W / 2, PAGE_H / 2, "SPIRAL TILINGS", ha="center", va="center",
            fontsize=34, color=CREAM, zorder=4, **brand.SERIF_BOLD)
    ax.text(PAGE_W / 2, PAGE_H / 2 - 0.7, "mathrelaxing.store", ha="center", va="center",
            fontsize=16, color=GOLD, zorder=4, **brand.SERIF)
    return fig

CONFIG = tcb.BookConfig(
    prefix="spiral_tilings",
    theme_bg=BG_DARK,
    title="SPIRAL TILINGS",
    subtitle="MATHEMATICS",
    tagline="A Coloring Book of Radial Geometry",
    count_label="50 Parametric Designs",
    about_body=ABOUT_BODY,
    n_designs=50,
    preview_indices=[1, 8, 15, 25, 35, 42, 50],
)

def main():
    tcb.build_book(CONFIG, render_design, emblem, watermark, back_cover=back_cover_page)

if __name__ == "__main__":
    main()
