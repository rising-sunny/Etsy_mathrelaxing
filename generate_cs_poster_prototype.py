"""
generate_cs_poster_prototype.py — CS educational plate PROTOTYPE
================================================================
Two scientific plates to validate style before the full set:

  1. Big O — growth of common complexity classes
  2. Binary Search Tree — structure & search path

Stack: matplotlib + LaTeX (MiKTeX) + networkx + pillow
Style: Maxwell / Schrödinger family (cream grid, rust accents, FIG.)

  python generate_cs_poster_prototype.py
  python generate_cs_poster_prototype.py --no-latex
"""
from __future__ import annotations

import argparse
import math
import os
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "cs_posters_prototype")
PREVIEWS = os.path.join(OUT, "previews")

# Palette — scientific plate + a bit more color (still gallery, not neon)
CREAM = "#F4F1EA"
CREAM_WARM = "#F7F0E4"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#555555"
INK_FAINT = "#8A857C"
RUST = "#B85C38"
RUST_SOFT = "#C4785A"
LINE_DARK = "#2A2A2A"
# Extra accents for CS diagrams
TEAL = "#2F6F6A"
TEAL_SOFT = "#5A9A93"
SLATE = "#3D5A80"
INDIGO = "#4A5080"
AMBER = "#C4922A"
CORAL = "#C45C4A"
NODE_FILL = "#FBF7F0"
NODE_PATH_FILL = "#F3E0D4"
NODE_LEFT_FILL = "#E8F0EF"
NODE_RIGHT_FILL = "#F5EDE4"

DPI = 180  # prototype preview density
_USE_LATEX = False


def _math_fs(fig_w: float, frac: float) -> float:
    """Slightly larger than body type — for equations & math labels."""
    return max(9.0, fig_w * 72 * frac * 1.12)


def configure_matplotlib(use_latex: bool = True) -> bool:
    global _USE_LATEX
    has_tex = bool(shutil.which("latex") or shutil.which("pdflatex"))
    use_latex = use_latex and has_tex
    if use_latex:
        try:
            plt.rcParams.update(
                {
                    "text.usetex": True,
                    "font.family": "serif",
                    "font.serif": ["Computer Modern Roman", "cmr10", "Times New Roman"],
                    "mathtext.fontset": "cm",
                    "axes.unicode_minus": False,
                    "axes.formatter.use_mathtext": True,
                    "text.latex.preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{helvet}
""",
                }
            )
            fig = plt.figure(figsize=(1, 1))
            fig.text(0.5, 0.5, r"$O(n)$")
            fig.canvas.draw()
            plt.close(fig)
            _USE_LATEX = True
            print("  math: LaTeX (Computer Modern)")
            return True
        except Exception as e:
            print(f"  LaTeX probe failed ({e}); mathtext STIX")
            plt.rcParams["text.usetex"] = False

    plt.rcParams.update(
        {
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "DejaVu Serif", "Times New Roman"],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
        }
    )
    _USE_LATEX = False
    print("  math: mathtext STIX")
    return False


def _fs(fig_w: float, frac: float) -> float:
    return max(7.0, fig_w * 72 * frac)


def _graph_paper(ax, major=5.0, minor=1.25):
    for x in np.arange(0, 100.5, minor):
        ax.axvline(x, color=GRID_FINE, lw=0.35, zorder=0)
    for y in np.arange(0, 100.5, minor):
        ax.axhline(y, color=GRID_FINE, lw=0.35, zorder=0)
    for x in np.arange(0, 100.5, major):
        ax.axvline(x, color=GRID, lw=0.55, zorder=0)
    for y in np.arange(0, 100.5, major):
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def _plate_frame(ax):
    m = 3.0
    ax.add_patch(
        Rectangle(
            (m, m),
            100 - 2 * m,
            100 - 2 * m,
            fill=False,
            edgecolor=GRID,
            lw=0.9,
            zorder=1,
        )
    )


def _header(ax, title: str, subtitle_tex: str, fig_n: str, fig_w: float):
    ax.text(
        6.2,
        93.2,
        rf"\textsf{{\textbf{{{title}}}}}" if _USE_LATEX else title,
        fontsize=_fs(fig_w, 0.036),
        color=INK,
        va="center",
        ha="left",
        zorder=5,
        fontfamily="sans-serif" if not _USE_LATEX else None,
        fontweight="bold" if not _USE_LATEX else None,
    )
    ax.text(
        93.8,
        93.2,
        rf"\textsf{{{fig_n}}}" if _USE_LATEX else fig_n,
        fontsize=_fs(fig_w, 0.014),
        color=INK_SOFT,
        va="center",
        ha="right",
        zorder=5,
    )
    ax.text(
        6.2,
        88.8,
        subtitle_tex,
        fontsize=_math_fs(fig_w, 0.0145),
        color=RUST,
        va="center",
        ha="left",
        zorder=5,
    )
    ax.plot([6.2, 93.8], [86.0, 86.0], color=INK, lw=0.85, solid_capstyle="butt", zorder=5)


def _caption(ax, lines: list[str], fig_w: float, y0: float = 16.5):
    y = y0
    for line in lines:
        ax.text(
            6.2,
            y,
            line,
            fontsize=_math_fs(fig_w, 0.0115),
            color=INK_SOFT,
            ha="left",
            va="top",
            zorder=5,
        )
        y -= 2.55


def _fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_jpg(img: Image.Image, path: str, quality: int = 92):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    print(f"  wrote {path}  ({os.path.getsize(path)/1024:.0f} KB)")


# ── Hierarchy layout for trees (no Graphviz required) ───────────────────────

def hierarchy_pos(G: nx.DiGraph, root, width=1.0, vert_gap=0.22, vert_loc=0.0, xcenter=0.5, pos=None, parent=None):
    """Top-down layout for a tree rooted at `root`."""
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    children = list(G.successors(root))
    if children:
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos = hierarchy_pos(
                G,
                child,
                width=dx,
                vert_gap=vert_gap,
                vert_loc=vert_loc - vert_gap,
                xcenter=nextx,
                pos=pos,
                parent=root,
            )
    return pos


# ═══════════════════════════════════════════════════════════════════════════════
# PLATE 1 — Big O
# ═══════════════════════════════════════════════════════════════════════════════

def compose_big_o(width_in: float = 10.0, height_in: float = 12.5, dpi: int = DPI) -> Image.Image:
    fig_w, fig_h = width_in, height_in
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)

    # Background plate
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 100)
    ax_bg.set_ylim(0, 100)
    ax_bg.set_axis_off()
    ax_bg.set_facecolor(CREAM)
    _graph_paper(ax_bg)
    _plate_frame(ax_bg)
    _header(
        ax_bg,
        "HOW ALGORITHMS GROW",
        r"BIG-$O$ COMPLEXITY  $\cdot$  $T(n)$ as input size $n\to\infty$",
        "FIG. 1",
        fig_w,
    )

    # Soft warm wash behind the chart band
    ax_bg.add_patch(
        Rectangle((6, 30), 88, 54, facecolor=CREAM_WARM, edgecolor="none", alpha=0.55, zorder=1)
    )

    # Inset chart — leave room under for captions
    ax = fig.add_axes([0.12, 0.34, 0.76, 0.48], zorder=3)
    ax.set_facecolor(CREAM)

    n = np.linspace(1, 40, 400)
    # Distinct colors: teal → slate → charcoal → amber → coral
    curves = [
        (np.ones_like(n) * 1.2, r"$O(1)$  constant", TEAL, 2.0, (0, (1.5, 2.5)), 0.06),
        (np.log2(n) * 1.15, r"$O(\log n)$  binary search", SLATE, 2.1, "-", 0.07),
        (n * 0.85, r"$O(n)$  scan a list", INDIGO, 2.15, "-", 0.05),
        (n * np.log2(n) / 5.5, r"$O(n\log n)$  good sort", AMBER, 2.2, "-", 0.06),
        (n ** 2 / 22, r"$O(n^{2})$  nested loops", CORAL, 2.35, "-", 0.08),
    ]
    for y, label, color, lw, ls, fill_a in curves:
        ax.fill_between(n, 0, y, color=color, alpha=fill_a, zorder=2, linewidth=0)
        ax.plot(n, y, color=color, lw=lw, ls=ls, solid_capstyle="round", label=label, zorder=4)

    ax.set_xlim(1, 40)
    ax.set_ylim(0, 48)
    ax.set_xlabel(
        r"input size $n$" if _USE_LATEX else "input size n",
        fontsize=_math_fs(fig_w, 0.013),
        color=INK_SOFT,
    )
    ax.set_ylabel(
        r"relative work $T(n)$" if _USE_LATEX else "relative work T(n)",
        fontsize=_math_fs(fig_w, 0.013),
        color=INK_SOFT,
    )
    ax.tick_params(colors=INK_FAINT, labelsize=_fs(fig_w, 0.0095))
    for spine in ax.spines.values():
        spine.set_color(LINE_DARK)
        spine.set_linewidth(0.8)
    ax.grid(True, color=GRID, lw=0.5, zorder=1)
    ax.set_axisbelow(True)

    leg = ax.legend(
        loc="upper left",
        frameon=True,
        fancybox=False,
        edgecolor=GRID,
        fontsize=_math_fs(fig_w, 0.0115),
        labelcolor=INK,
        borderpad=0.7,
    )
    leg.get_frame().set_facecolor(CREAM)
    leg.get_frame().set_alpha(0.96)

    _caption(
        ax_bg,
        [
            r"Big-$O$ hides constants and lower-order terms: it answers how work scales when $n$ grows large."
            if _USE_LATEX
            else "Big-O hides constants and lower-order terms: it answers how work scales when n grows large.",
            r"Prefer $O(\log n)$ and $O(n\log n)$ when $n$ can reach millions; $O(n^{2})$ collapses under load."
            if _USE_LATEX
            else "Prefer log and n-log-n when n can reach millions; quadratic collapses under load.",
            "A scientific plate for computer science classrooms, offices, and study walls.",
        ],
        fig_w,
        y0=22.0,
    )

    # Footer equation — larger math
    ax_bg.text(
        93.8,
        9.8,
        r"$f(n)=O(g(n))$" if _USE_LATEX else "f(n) = O(g(n))",
        fontsize=_math_fs(fig_w, 0.018),
        color=CORAL,
        ha="right",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        93.8,
        6.8,
        r"\textsf{asymptotic upper bound}" if _USE_LATEX else "asymptotic upper bound",
        fontsize=_fs(fig_w, 0.009),
        color=INK_FAINT,
        ha="right",
        va="center",
        zorder=5,
    )

    return _fig_to_image(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PLATE 2 — Binary Search Tree
# ═══════════════════════════════════════════════════════════════════════════════

def _build_demo_bst() -> tuple[nx.DiGraph, dict, list]:
    """
    Classic demo tree:

            8
         /     \\
        3       10
       / \\        \\
      1   6        14
         / \\      /
        4   7    13

    Search path for 13 highlighted: 8 → 10 → 14 → 13
    """
    edges = [
        (8, 3),
        (8, 10),
        (3, 1),
        (3, 6),
        (6, 4),
        (6, 7),
        (10, 14),
        (14, 13),
    ]
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = hierarchy_pos(G, root=8, width=1.6, vert_gap=0.2, vert_loc=1.0, xcenter=0.5)
    # normalize pos to nice data coords
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    # map to plate-ish inset coords later
    search_path = [8, 10, 14, 13]
    return G, pos, search_path


def compose_bst(width_in: float = 10.0, height_in: float = 12.5, dpi: int = DPI) -> Image.Image:
    fig_w, fig_h = width_in, height_in
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)

    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 100)
    ax_bg.set_ylim(0, 100)
    ax_bg.set_axis_off()
    ax_bg.set_facecolor(CREAM)
    _graph_paper(ax_bg)
    _plate_frame(ax_bg)
    _header(
        ax_bg,
        "ORDERED BY COMPARISON",
        r"BINARY SEARCH TREE  $\cdot$  left $<$ node $<$ right",
        "FIG. 2",
        fig_w,
    )

    G, pos, path = _build_demo_bst()
    pos = hierarchy_pos(G, root=8, width=1.35, vert_gap=0.26, vert_loc=1.0, xcenter=0.5)
    path_edges = list(zip(path[:-1], path[1:]))
    path_set = set(path)

    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()

    def map_xy(x, y):
        nx_ = 0.5 + 0.42 * (2 * ((x - x_min) / max(x_max - x_min, 1e-6) - 0.5))
        ny_ = 0.52 + 0.38 * (2 * ((y - y_min) / max(y_max - y_min, 1e-6) - 0.5))
        return nx_, ny_

    pos_n = {k: map_xy(*v) for k, v in pos.items()}

    # Soft tinted panel behind the tree
    ax_bg.add_patch(
        Rectangle((8, 32), 84, 50, facecolor=CREAM_WARM, edgecolor="none", alpha=0.5, zorder=1)
    )

    # Square axes → equal aspect; scatter markers are always circular in display space
    ax_size = 0.72
    h_frac = ax_size * fig_w / fig_h
    ax = fig.add_axes(
        [0.14, 0.30 + (0.52 - h_frac) / 2, ax_size, h_frac],
        zorder=3,
    )
    ax.set_facecolor("none")
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.set_clip_on(False)

    for u, v in G.edges():
        x0, y0 = pos_n[u]
        x1, y1 = pos_n[v]
        is_path = (u, v) in path_edges
        ax.plot(
            [x0, x1],
            [y0, y1],
            color=CORAL if is_path else TEAL_SOFT,
            lw=2.6 if is_path else 1.65,
            solid_capstyle="round",
            zorder=2,
            alpha=0.95 if is_path else 0.85,
            clip_on=False,
        )

    # Scatter markers = true circles (fixes flattened Circle patches)
    for node, (x, y) in pos_n.items():
        on_path = node in path_set
        is_leftish = node in {1, 3, 4, 6, 7}
        if on_path:
            face, edge, tc = NODE_PATH_FILL, CORAL, CORAL
            ms, lw = 780, 2.5
        elif is_leftish:
            face, edge, tc = NODE_LEFT_FILL, TEAL, TEAL
            ms, lw = 680, 1.9
        else:
            face, edge, tc = NODE_RIGHT_FILL, AMBER, "#8A6A20"
            ms, lw = 680, 1.9
        ax.scatter(
            [x], [y], s=ms, c=face, edgecolors=edge, linewidths=lw, zorder=4, clip_on=False
        )
        ax.text(
            x,
            y,
            str(node),
            ha="center",
            va="center",
            fontsize=_fs(fig_w, 0.0145),
            color=tc,
            fontweight="bold",
            zorder=5,
            clip_on=False,
        )

    ax.text(
        pos_n[3][0],
        pos_n[3][1] + 0.11,
        "left",
        ha="center",
        fontsize=_fs(fig_w, 0.01),
        color=TEAL,
        style="italic",
        clip_on=False,
    )
    ax.text(
        pos_n[10][0],
        pos_n[10][1] + 0.11,
        "right",
        ha="center",
        fontsize=_fs(fig_w, 0.01),
        color=AMBER,
        style="italic",
        clip_on=False,
    )

    ax_bg.text(
        50,
        27.5,
        r"search for $13$:  $8 \rightarrow 10 \rightarrow 14 \rightarrow 13$  (highlighted)"
        if _USE_LATEX
        else "search for 13:  8 → 10 → 14 → 13  (highlighted)",
        fontsize=_math_fs(fig_w, 0.0125),
        color=CORAL,
        ha="center",
        va="center",
        zorder=5,
    )

    props = [
        (r"left $<$ node $<$ right", r"in-order traversal is sorted"),
        (r"search / insert $O(h)$", r"balanced: $h \approx \log_2 n$"),
    ]
    for i, (a, b) in enumerate(props):
        y = 21.5 - i * 3.8
        ax_bg.text(12, y, a, fontsize=_math_fs(fig_w, 0.012), color=TEAL if i == 0 else INK, zorder=5)
        ax_bg.text(52, y, b, fontsize=_math_fs(fig_w, 0.012), color=INK_SOFT, style="italic", zorder=5)

    _caption(
        ax_bg,
        [
            r"A binary search tree stores keys so every left child is smaller and every right child is larger."
            if _USE_LATEX
            else "A binary search tree stores keys so every left child is smaller and every right child is larger.",
            r"Average search is $O(\log n)$ when balanced; a skewed chain falls back to $O(n)$."
            if _USE_LATEX
            else "Average search is O(log n) when balanced; a skewed chain falls back to O(n).",
        ],
        fig_w,
        y0=13.5,
    )

    ax_bg.text(
        93.8,
        7.8,
        r"$h \approx \log_2 n$" if _USE_LATEX else "h ≈ log₂ n",
        fontsize=_math_fs(fig_w, 0.018),
        color=CORAL,
        ha="right",
        va="center",
        zorder=5,
    )
    ax_bg.text(
        93.8,
        5.2,
        r"\textsf{balanced height}" if _USE_LATEX else "balanced height",
        fontsize=_fs(fig_w, 0.009),
        color=INK_FAINT,
        ha="right",
        va="center",
        zorder=5,
    )

    return _fig_to_image(fig)


# ── Contact / side-by-side ───────────────────────────────────────────────────

def compose_contact(big_o: Image.Image, bst: Image.Image) -> Image.Image:
    """Side-by-side prototype sheet for quick review."""
    w, h = 1600, 1100
    canvas = Image.new("RGB", (w, h), (244, 241, 234))
    a = big_o.copy()
    b = bst.copy()
    a.thumbnail((720, 900), Image.Resampling.LANCZOS)
    b.thumbnail((720, 900), Image.Resampling.LANCZOS)
    canvas.paste(a, (60, 80))
    canvas.paste(b, (820, 80))
    # simple title bar via matplotlib
    fig = plt.figure(figsize=(16, 1.2), dpi=100, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    ax.text(0.5, 0.55, "CS Poster Prototype  ·  Big-O  +  Binary Search Tree", ha="center", va="center",
            fontsize=16, color=INK, fontfamily="serif")
    ax.text(0.5, 0.2, "MathRelaxing scientific-plate style  ·  review before full set", ha="center", va="center",
            fontsize=10, color=INK_SOFT, fontfamily="serif", style="italic")
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    bar = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    bar = bar.resize((w, 90), Image.Resampling.LANCZOS)
    canvas.paste(bar, (0, 0))
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-latex", action="store_true")
    args = ap.parse_args()

    print("=== CS poster prototype (Big-O + BST) ===")
    os.makedirs(PREVIEWS, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    print("plate 1: Big O…")
    big_o = compose_big_o()
    save_jpg(big_o, os.path.join(PREVIEWS, "proto_1_big_o.jpg"))

    print("plate 2: Binary Search Tree…")
    bst = compose_bst()
    save_jpg(bst, os.path.join(PREVIEWS, "proto_2_bst.jpg"))

    print("contact sheet…")
    contact = compose_contact(big_o, bst)
    save_jpg(contact, os.path.join(PREVIEWS, "proto_contact.jpg"), quality=90)

    print(f"done → {PREVIEWS}")


if __name__ == "__main__":
    main()
