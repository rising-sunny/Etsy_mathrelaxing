"""
generate_neural_art.py — MathRelaxing "Neural Networks & Tech Art" generator
=============================================================================
Genera proceduralmente 50 diseños basados en topologías de redes neuronales,
arquitecturas de inteligencia artificial y circuitos (Manhattan routing).

Salida:
  neural_network_digital.pdf   — PDF de 52 páginas
  neural_network_cover.jpg     — portada
  neural_network_page_01..07.jpg — páginas de muestra
"""

import math
import random
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, PathPatch
from matplotlib.path import Path

import brand
import template_coloring_book as tcb

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 8.5, 11.0
LINE_COLOR = "black"

# Cover theme colour for THIS product: Midnight Blue
BG_DARK = "#0F172A"
GOLD = brand.GOLD
CREAM = brand.CREAM
LOGO_PATH = brand.LOGO_PATH

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

# ─────────────────────────────────────────────────────────────────────────
# Generative Algorithms
# ─────────────────────────────────────────────────────────────────────────

def draw_dense_network(ax, x0, y0, w, h, layers, seed, lw=1.5, node_r=0.15):
    """Feedforward deep neural network style."""
    rng = random.Random(seed)
    
    # Generate nodes
    nodes = []
    layer_xs = [x0 + i * (w / (len(layers) - 1)) for i in range(len(layers))] if len(layers) > 1 else [x0 + w/2]
    
    for i, n_nodes in enumerate(layers):
        x = layer_xs[i]
        spacing = h / n_nodes
        offset = y0 + (h - (n_nodes - 1) * spacing) / 2
        
        layer_nodes = []
        for j in range(n_nodes):
            y = offset + j * spacing
            layer_nodes.append((x, y))
        nodes.append(layer_nodes)
        
    # Draw edges
    for i in range(len(nodes) - 1):
        for p1 in nodes[i]:
            for p2 in nodes[i+1]:
                # Dropout / sparsity
                if rng.random() > 0.70:
                    # Draw a nice curved connection instead of a straight line
                    path_data = [
                        (Path.MOVETO, p1),
                        (Path.CURVE4, (p1[0] + (p2[0]-p1[0])/2, p1[1])),
                        (Path.CURVE4, (p2[0] - (p2[0]-p1[0])/2, p2[1])),
                        (Path.CURVE4, p2)
                    ]
                    codes, verts = zip(*path_data)
                    path = Path(verts, codes)
                    patch = PathPatch(path, facecolor='none', edgecolor=LINE_COLOR, lw=lw, zorder=1)
                    ax.add_patch(patch)
                    
    # Draw nodes
    for layer in nodes:
        for (nx, ny) in layer:
            ax.add_patch(Circle((nx, ny), node_r, facecolor="white", edgecolor=LINE_COLOR, lw=lw*1.5, zorder=2))

def draw_radial_topology(ax, cx, cy, r_max, rings, nodes_per_ring, seed, lw=2.0):
    """Graph topologies in concentric rings."""
    rng = random.Random(seed)
    nodes = []
    
    # Center node
    nodes.append([(cx, cy)])
    
    for ring in range(1, rings + 1):
        r = ring * (r_max / rings)
        count = nodes_per_ring * ring
        ring_nodes = []
        angle_offset = rng.random() * math.pi
        for i in range(count):
            theta = angle_offset + i * 2 * math.pi / count
            nx = cx + r * math.cos(theta)
            ny = cy + r * math.sin(theta)
            ring_nodes.append((nx, ny))
        nodes.append(ring_nodes)
        
    # Edges
    for i in range(len(nodes) - 1):
        for j, p2 in enumerate(nodes[i+1]):
            # connect to closest node in previous ring
            p1 = min(nodes[i], key=lambda p: math.hypot(p[0]-p2[0], p[1]-p2[1]))
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=LINE_COLOR, lw=lw, zorder=1)
            # maybe one random cross-connection
            if rng.random() > 0.8:
                p1_rand = rng.choice(nodes[i])
                ax.plot([p1_rand[0], p2[0]], [p1_rand[1], p2[1]], color=LINE_COLOR, lw=lw*0.5, zorder=1)
                
    # Nodes
    node_r = 0.15 * (4 / max(4, rings))
    for layer in nodes:
        for (nx, ny) in layer:
            ax.add_patch(Circle((nx, ny), node_r, facecolor="white", edgecolor=LINE_COLOR, lw=lw, zorder=2))

def draw_circuit_routing(ax, x0, y0, w, h, paths, seed, lw=3.0):
    """Manhattan routing imitating circuit boards."""
    rng = random.Random(seed)
    
    # create grid
    grid_w, grid_h = 20, 26
    step_x, step_y = w / grid_w, h / grid_h
    
    def grid_pt(gx, gy):
        return (x0 + gx * step_x, y0 + gy * step_y)
        
    # Draw paths
    for _ in range(paths):
        gx1, gy1 = rng.randint(1, grid_w-1), rng.randint(1, grid_h-1)
        gx2, gy2 = rng.randint(1, grid_w-1), rng.randint(1, grid_h-1)
        
        path_pts = [(gx1, gy1)]
        curr_x, curr_y = gx1, gy1
        
        # Manhattan routing with one bend
        if rng.random() > 0.5:
            path_pts.append((curr_x, gy2))
        else:
            path_pts.append((gx2, curr_y))
        path_pts.append((gx2, gy2))
        
        real_pts = [grid_pt(x, y) for x, y in path_pts]
        
        # Draw thick lines for colorable traces
        xs, ys = zip(*real_pts)
        ax.plot(xs, ys, color=LINE_COLOR, lw=lw, solid_joinstyle="miter", solid_capstyle="round", zorder=1)
        
        # Draw pads
        ax.add_patch(Circle(real_pts[0], step_x*0.4, facecolor="white", edgecolor=LINE_COLOR, lw=lw*0.8, zorder=2))
        ax.add_patch(Circle(real_pts[-1], step_x*0.4, facecolor="white", edgecolor=LINE_COLOR, lw=lw*0.8, zorder=2))
        
        # Add a via (smaller internal circle)
        ax.add_patch(Circle(real_pts[0], step_x*0.15, facecolor="white", edgecolor=LINE_COLOR, lw=lw*0.5, zorder=3))

# ─────────────────────────────────────────────────────────────────────────
# Brand hooks
# ─────────────────────────────────────────────────────────────────────────
def emblem(ax, cx, cy, r):
    """Product emblem drawn in gold on the cover (a stylistic node network)."""
    # Simple central node with 6 radiating connected nodes
    ax.add_patch(Circle((cx, cy), r*0.3, facecolor="none", edgecolor=brand.GOLD, lw=4))
    for i in range(6):
        theta = i * 2 * math.pi / 6
        nx = cx + r * 0.75 * math.cos(theta)
        ny = cy + r * 0.75 * math.sin(theta)
        ax.plot([cx + r*0.3*math.cos(theta), nx], [cy + r*0.3*math.sin(theta), ny], color=brand.GOLD, lw=3)
        ax.add_patch(Circle((nx, ny), r*0.2, facecolor="none", edgecolor=brand.GOLD, lw=3))
        # connect ring
        theta2 = (i+1) * 2 * math.pi / 6
        nx2 = cx + r * 0.75 * math.cos(theta2)
        ny2 = cy + r * 0.75 * math.sin(theta2)
        ax.plot([nx, nx2], [ny, ny2], color=brand.GOLD, lw=2)

def watermark(ax, W, H):
    """Faint dense neural net watermark filling the whole cover."""
    ghost = (0.79, 0.63, 0.29, 0.15)  # gold at low alpha
    draw_dense_network(ax, 0.5, 0.5, W-1, H-1, [4, 6, 5, 7, 5, 6, 4], seed=42, lw=1.5, node_r=0.2)
    # recolor the watermark
    for child in ax.get_children():
        if isinstance(child, (PathPatch, Circle)):
            child.set_edgecolor(ghost)
        if isinstance(child, Circle):
            child.set_facecolor("none")

# ─────────────────────────────────────────────────────────────────────────
# Pages Config
# ─────────────────────────────────────────────────────────────────────────
ABOUT_BODY = (
    "Welcome to the architectural beauty of Artificial Intelligence.\n\n"
    "Hidden behind the algorithms that power modern technology lies a profound\n"
    "geometric elegance. The graphs and topologies found in this book represent\n"
    "the actual structures of Neural Networks, from simple Feedforward layers\n"
    "to complex Radial graphs and Manhattan-routed silicon circuits.\n\n"
    "Every design was procedurally generated using mathematical node routing,\n"
    "reflecting the true organized chaos of machine learning models. As you\n"
    "color these interconnected nodes and synaptic pathways, you are interacting\n"
    "with the foundational blueprints of the digital age."
)

def build_plan():
    plan = []
    # 50 pages alternating between styles
    for n in range(1, 51):
        seed = 2000 + n * 13
        lw = 1.0 + (n % 4) * 0.25
        if n % 3 == 0:
            # Dense network
            layers = [random.Random(seed+i).randint(3, 12) for i in range(6)]
            plan.append(("dense", (layers, seed, lw)))
        elif n % 3 == 1:
            # Radial
            rings = 4 + (n % 4)
            nodes = 5 + (n % 5)
            plan.append(("radial", (rings, nodes, seed, lw)))
        else:
            # Circuit
            paths = 25 + (n % 20)
            plan.append(("circuit", (paths, seed, lw + 1.0)))
    return plan

_PLAN = None
def _plan():
    global _PLAN
    if _PLAN is None:
        _PLAN = build_plan()
    return _PLAN

def render_design(n):
    fig, ax = new_page()
    margin_x, margin_y = 1.0, 1.5
    w, h = PAGE_W - 2*margin_x, PAGE_H - 2*margin_y - 0.5
    
    kind, params = _plan()[n - 1]
    if kind == "dense":
        layers, seed, lw = params
        draw_dense_network(ax, margin_x, margin_y, w, h, layers, seed, lw)
    elif kind == "radial":
        rings, nodes, seed, lw = params
        draw_radial_topology(ax, PAGE_W/2, PAGE_H/2 + 0.2, min(w, h)/2, rings, nodes, seed, lw)
    elif kind == "circuit":
        paths, seed, lw = params
        draw_circuit_routing(ax, margin_x, margin_y, w, h, paths, seed, lw)
        
    return fig

CONFIG = tcb.BookConfig(
    prefix="neural_network",
    theme_bg=BG_DARK,
    title="NEURAL NETWORK",
    subtitle="TECH ART",
    tagline="A Coloring Book of AI Topologies & Circuits",
    count_label="50 Algorithmic Designs",
    about_body=ABOUT_BODY,
    n_designs=50,
    preview_indices=[1, 2, 5, 9, 15, 23, 40],
)

def main():
    tcb.build_book(CONFIG, render_design, emblem, watermark)

if __name__ == "__main__":
    main()
