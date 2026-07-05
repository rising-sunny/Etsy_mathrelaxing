"""
generate_math_stickers.py — Mathematical Stickers for STEM Planner
==================================================================
Genera stickers PNG temáticos matemáticos: π, ∫, nodos, fractales, etc.
Optimizados para GoodNotes/Notability con fondo transparente.
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "stem_planner", "stickers")
os.makedirs(OUT_DIR, exist_ok=True)

# Brand colors
GOLD = "#C9A227"
CREAM = "#F5F1E6"
NAVY = "#12172E"
DARK_GOLD = "#8B6914"


def draw_symbol_sticker(symbol, filename):
    """Generic function to draw mathematical symbol stickers using matplotlib."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Add subtle shadow (drawn first so it stays behind)
    ax.text(5.1, 4.9, symbol, fontsize=200, ha='center', va='center',
            color=(0, 0, 0, 0.2), fontweight='bold')
    
    # Draw symbol
    ax.text(5, 5, symbol, fontsize=200, ha='center', va='center',
            color=GOLD, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"[OK] {filename} created")


def draw_pi_sticker():
    """π symbol sticker."""
    draw_symbol_sticker("π", "pi_symbol.png")


def draw_integral_sticker():
    """∫ integral symbol sticker."""
    draw_symbol_sticker("∫", "integral_symbol.png")


def draw_sigma_sticker():
    """Σ sigma symbol sticker."""
    draw_symbol_sticker("Σ", "sigma_symbol.png")


def draw_infinity_sticker():
    """∞ infinity symbol sticker."""
    draw_symbol_sticker("∞", "infinity_symbol.png")


def draw_square_root_sticker():
    """√ square root symbol sticker."""
    draw_symbol_sticker("√", "sqrt_symbol.png")


def draw_delta_sticker():
    """Δ delta symbol sticker."""
    draw_symbol_sticker("Δ", "delta_symbol.png")


def draw_node_network_sticker():
    """Network nodes sticker (graph theory)."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Create nodes
    positions = [(2, 8), (5, 7), (8, 8), (3, 4), (7, 4), (5, 2)]
    
    # Draw edges
    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 4), (3, 4), (3, 5), (4, 5)]
    for i, j in edges:
        x1, y1 = positions[i]
        x2, y2 = positions[j]
        ax.plot([x1, x2], [y1, y2], color=GOLD, linewidth=2, alpha=0.7)
    
    # Draw nodes
    for x, y in positions:
        circle = Circle((x, y), 0.4, color=NAVY, ec=GOLD, lw=2)
        ax.add_patch(circle)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "node_network.png"), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("[OK] Node network sticker created")


def draw_fractal_spiral_sticker():
    """Golden spiral fractal sticker."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Golden spiral approximation
    golden_ratio = (1 + math.sqrt(5)) / 2
    theta = np.linspace(0, 4 * math.pi, 200)
    r = 0.5 * np.power(golden_ratio, theta / (math.pi / 2))
    
    x = 5 + r * np.cos(theta)
    y = 5 + r * np.sin(theta)
    
    ax.plot(x, y, color=GOLD, linewidth=3)
    ax.plot(5, 5, 'o', color=NAVY, markersize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fractal_spiral.png"), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("[OK] Fractal spiral sticker created")


def draw_geometric_flower_sticker():
    """Geometric flower pattern sticker."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Create flower pattern
    petals = 8
    for i in range(petals):
        angle = 2 * math.pi * i / petals
        x_center = 5 + 2 * math.cos(angle)
        y_center = 5 + 2 * math.sin(angle)
        
        petal = Circle((x_center, y_center), 1.2, 
                      color=GOLD, alpha=0.6, ec=NAVY, lw=2)
        ax.add_patch(petal)
    
    # Center
    center = Circle((5, 5), 0.8, color=NAVY, ec=GOLD, lw=2)
    ax.add_patch(center)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "geometric_flower.png"), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("[OK] Geometric flower sticker created")


def draw_celtic_knot_sticker():
    """Simplified Celtic knot pattern sticker."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Draw interlocking circles pattern
    positions = [(3, 5), (5, 5), (7, 5), (5, 3), (5, 7)]
    
    for x, y in positions:
        circle = Circle((x, y), 1.2, color=GOLD, alpha=0.5, 
                       ec=NAVY, lw=2, fill=False)
        ax.add_patch(circle)
    
    # Center connector
    center = Circle((5, 5), 0.5, color=NAVY)
    ax.add_patch(center)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "celtic_knot_simple.png"), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("[OK] Celtic knot sticker created")


def draw_equation_sticker(text, filename, fontsize=60):
    """Generic function to draw equation stickers using matplotlib."""
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Add subtle shadow (drawn first so it stays behind)
    ax.text(5.1, 4.9, text, fontsize=fontsize, ha='center', va='center',
            color=(0, 0, 0, 0.2), fontweight='bold')
    
    # Draw equation
    ax.text(5, 5, text, fontsize=fontsize, ha='center', va='center',
            color=GOLD, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), 
                transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"[OK] {filename} created")


def draw_euler_sticker():
    """Euler's identity e^(iπ) + 1 = 0 sticker."""
    draw_equation_sticker(r"$e^{i\pi}+1=0$", "euler_identity.png", fontsize=55)


def draw_pythagoras_sticker():
    """a² + b² = c² Pythagorean theorem sticker."""
    draw_equation_sticker(r"$a^2+b^2=c^2$", "pythagoras.png", fontsize=55)


def draw_calculus_sticker():
    """dy/dx calculus notation sticker."""
    draw_equation_sticker(r"$\frac{dy}{dx}$", "calculus_derivative.png", fontsize=80)


def draw_summation_sticker():
    """∑ summation with limits sticker."""
    draw_equation_sticker(r"$\sum_{i=1}^{n} i$", "summation.png", fontsize=70)


def main():
    print("Generating mathematical stickers...")
    print(f"Output directory: {OUT_DIR}")
    
    # Symbol stickers
    draw_pi_sticker()
    draw_integral_sticker()
    draw_sigma_sticker()
    draw_infinity_sticker()
    draw_square_root_sticker()
    draw_delta_sticker()
    
    # Geometric stickers
    draw_node_network_sticker()
    draw_fractal_spiral_sticker()
    draw_geometric_flower_sticker()
    draw_celtic_knot_sticker()
    
    # Equation stickers
    draw_euler_sticker()
    draw_pythagoras_sticker()
    draw_calculus_sticker()
    draw_summation_sticker()
    
    print(f"\n[OK] All stickers generated in {OUT_DIR}")
    print(f"Total: 14 mathematical stickers (512x512px PNG, transparent background)")


if __name__ == "__main__":
    main()