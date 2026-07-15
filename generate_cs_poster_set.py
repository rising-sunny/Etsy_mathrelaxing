"""
generate_cs_poster_set.py — Computer Science Educational Wall Art Set
=====================================================================
eRank pick: computer science poster (~127 searches, ~870 competition, 68% CTR)

Seven scientific plates (MathRelaxing Maxwell-family style):
  1. Big-O complexity
  2. Binary search tree
  3. Sorting comparison
  4. Boolean logic gates
  5. OSI network layers
  6. Stack & queue
  7. Finite state machine

Stack: matplotlib + LaTeX (circuitikz gates, TikZ automata FSM) + networkx + pillow

  python generate_cs_poster_set.py
  python generate_cs_poster_set.py --preview-only
  python generate_cs_poster_set.py --no-latex
  python generate_cs_poster_set.py --only big_o,bst
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath
import networkx as nx
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "cs_poster_set")
PRINTS = os.path.join(OUT, "prints")
PREVIEWS = os.path.join(OUT, "previews")

CREAM = "#F4F1EA"
CREAM_WARM = "#F7F0E4"
GRID = "#E6E2D8"
GRID_FINE = "#EDEAE3"
INK = "#1A1A1A"
INK_SOFT = "#555555"
INK_FAINT = "#8A857C"
RUST = "#B85C38"
LINE_DARK = "#2A2A2A"
TEAL = "#2F6F6A"
TEAL_SOFT = "#5A9A93"
SLATE = "#3D5A80"
INDIGO = "#4A5080"
AMBER = "#C4922A"
CORAL = "#C45C4A"
NODE_PATH_FILL = "#F3E0D4"
NODE_LEFT_FILL = "#E8F0EF"
NODE_RIGHT_FILL = "#F5EDE4"

DPI_PRINT = 240
DPI_PREVIEW = 160

SIZES = {
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
    "5x7": (10.0, 14.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
}

_USE_LATEX = False


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
            print("  math: LaTeX")
            return True
        except Exception as e:
            print(f"  LaTeX failed ({e}); STIX")
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
    print("  math: STIX")
    return False


def _fs(fig_w, frac):
    return max(7.0, fig_w * 72 * frac)


def _math_fs(fig_w, frac):
    return max(9.0, fig_w * 72 * frac * 1.12)


def _graph_paper(ax):
    for x in np.arange(0, 100.5, 1.25):
        ax.axvline(x, color=GRID_FINE, lw=0.35, zorder=0)
    for y in np.arange(0, 100.5, 1.25):
        ax.axhline(y, color=GRID_FINE, lw=0.35, zorder=0)
    for x in np.arange(0, 100.5, 5.0):
        ax.axvline(x, color=GRID, lw=0.55, zorder=0)
    for y in np.arange(0, 100.5, 5.0):
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def _plate_frame(ax):
    m = 3.0
    ax.add_patch(
        Rectangle((m, m), 100 - 2 * m, 100 - 2 * m, fill=False, edgecolor=GRID, lw=0.9, zorder=1)
    )


def _header(ax, title, subtitle_tex, fig_n, fig_w):
    ax.text(
        6.2,
        93.2,
        rf"\textsf{{\textbf{{{title}}}}}" if _USE_LATEX else title,
        fontsize=_fs(fig_w, 0.034),
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
        fontsize=_fs(fig_w, 0.013),
        color=INK_SOFT,
        va="center",
        ha="right",
        zorder=5,
    )
    ax.text(
        6.2,
        88.8,
        subtitle_tex,
        fontsize=_math_fs(fig_w, 0.0135),
        color=RUST,
        va="center",
        ha="left",
        zorder=5,
    )
    ax.plot([6.2, 93.8], [86.0, 86.0], color=INK, lw=0.85, zorder=5)


def _caption(ax, lines, fig_w, y0=16.0):
    y = y0
    for line in lines:
        ax.text(
            6.2,
            y,
            line,
            fontsize=_math_fs(fig_w, 0.011),
            color=INK_SOFT,
            ha="left",
            va="top",
            zorder=5,
        )
        y -= 2.5


def _footer_eq(ax, eq, label, fig_w, color=CORAL):
    ax.text(93.8, 9.5, eq, fontsize=_math_fs(fig_w, 0.017), color=color, ha="right", va="center", zorder=5)
    ax.text(
        93.8,
        6.6,
        rf"\textsf{{{label}}}" if _USE_LATEX else label,
        fontsize=_fs(fig_w, 0.0085),
        color=INK_FAINT,
        ha="right",
        va="center",
        zorder=5,
    )


def _new_plate(fig_w, fig_h, dpi):
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(CREAM)
    _graph_paper(ax)
    _plate_frame(ax)
    return fig, ax


def _fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_jpg(img, path, quality=90, dpi=DPI_PRINT):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.convert("RGB").save(
        path, "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path} ({os.path.getsize(path)/1024:.0f} KB)")


def hierarchy_pos(G, root, width=1.0, vert_gap=0.22, vert_loc=0.0, xcenter=0.5, pos=None, parent=None):
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
                G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root
            )
    return pos


# ── 1 Big O ──────────────────────────────────────────────────────────────────

def plate_big_o(w, h, dpi):
    fig, ax_bg = _new_plate(w, h, dpi)
    _header(
        ax_bg,
        "HOW ALGORITHMS GROW",
        r"BIG-$O$ COMPLEXITY  $\cdot$  $T(n)$ as input size $n\to\infty$",
        "FIG. 1",
        w,
    )
    ax_bg.add_patch(Rectangle((6, 30), 88, 54, facecolor=CREAM_WARM, edgecolor="none", alpha=0.5, zorder=1))
    ax = fig.add_axes([0.12, 0.34, 0.76, 0.48], zorder=3)
    ax.set_facecolor(CREAM)
    n = np.linspace(1, 40, 400)
    curves = [
        (np.ones_like(n) * 1.2, r"$O(1)$  constant", TEAL, 2.0, (0, (1.5, 2.5)), 0.06),
        (np.log2(n) * 1.15, r"$O(\log n)$  binary search", SLATE, 2.1, "-", 0.07),
        (n * 0.85, r"$O(n)$  scan a list", INDIGO, 2.15, "-", 0.05),
        (n * np.log2(n) / 5.5, r"$O(n\log n)$  good sort", AMBER, 2.2, "-", 0.06),
        (n ** 2 / 22, r"$O(n^{2})$  nested loops", CORAL, 2.35, "-", 0.08),
    ]
    for y, label, color, lw, ls, fa in curves:
        ax.fill_between(n, 0, y, color=color, alpha=fa, zorder=2, linewidth=0)
        ax.plot(n, y, color=color, lw=lw, ls=ls, solid_capstyle="round", label=label, zorder=4)
    ax.set_xlim(1, 40)
    ax.set_ylim(0, 48)
    ax.set_xlabel(r"input size $n$", fontsize=_math_fs(w, 0.012), color=INK_SOFT)
    ax.set_ylabel(r"relative work $T(n)$", fontsize=_math_fs(w, 0.012), color=INK_SOFT)
    ax.tick_params(colors=INK_FAINT, labelsize=_fs(w, 0.009))
    for s in ax.spines.values():
        s.set_color(LINE_DARK)
        s.set_linewidth(0.8)
    ax.grid(True, color=GRID, lw=0.5, zorder=1)
    ax.set_axisbelow(True)
    leg = ax.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=GRID, fontsize=_math_fs(w, 0.011), labelcolor=INK)
    leg.get_frame().set_facecolor(CREAM)
    leg.get_frame().set_alpha(0.96)
    _caption(
        ax_bg,
        [
            r"Big-$O$ hides constants and lower-order terms: it answers how work scales when $n$ grows large.",
            r"Prefer $O(\log n)$ and $O(n\log n)$ when $n$ can reach millions; $O(n^{2})$ collapses under load.",
            "A scientific plate for computer science classrooms, offices, and study walls.",
        ],
        w,
        22.0,
    )
    _footer_eq(ax_bg, r"$f(n)=O(g(n))$", "asymptotic upper bound", w)
    return _fig_to_image(fig)


# ── 2 BST ────────────────────────────────────────────────────────────────────

def plate_bst(w, h, dpi):
    fig, ax_bg = _new_plate(w, h, dpi)
    _header(
        ax_bg,
        "ORDERED BY COMPARISON",
        r"BINARY SEARCH TREE  $\cdot$  left $<$ node $<$ right",
        "FIG. 2",
        w,
    )
    edges = [(8, 3), (8, 10), (3, 1), (3, 6), (6, 4), (6, 7), (10, 14), (14, 13)]
    G = nx.DiGraph()
    G.add_edges_from(edges)
    path = [8, 10, 14, 13]
    path_edges = list(zip(path[:-1], path[1:]))
    path_set = set(path)
    pos = hierarchy_pos(G, root=8, width=1.35, vert_gap=0.26, vert_loc=1.0, xcenter=0.5)
    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    x_min, x_max, y_min, y_max = xs.min(), xs.max(), ys.min(), ys.max()

    def map_xy(x, y):
        return (
            0.5 + 0.42 * (2 * ((x - x_min) / max(x_max - x_min, 1e-6) - 0.5)),
            0.52 + 0.38 * (2 * ((y - y_min) / max(y_max - y_min, 1e-6) - 0.5)),
        )

    pos_n = {k: map_xy(*v) for k, v in pos.items()}
    ax_bg.add_patch(Rectangle((8, 32), 84, 50, facecolor=CREAM_WARM, edgecolor="none", alpha=0.5, zorder=1))
    ax_size = 0.72
    h_frac = ax_size * w / h
    ax = fig.add_axes([0.14, 0.30 + (0.52 - h_frac) / 2, ax_size, h_frac], zorder=3)
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
    for node, (x, y) in pos_n.items():
        on_path = node in path_set
        leftish = node in {1, 3, 4, 6, 7}
        if on_path:
            face, edge, tc, ms = NODE_PATH_FILL, CORAL, CORAL, 780
        elif leftish:
            face, edge, tc, ms = NODE_LEFT_FILL, TEAL, TEAL, 680
        else:
            face, edge, tc, ms = NODE_RIGHT_FILL, AMBER, "#8A6A20", 680
        ax.scatter([x], [y], s=ms, c=face, edgecolors=edge, linewidths=2.0, zorder=4, clip_on=False)
        ax.text(x, y, str(node), ha="center", va="center", fontsize=_fs(w, 0.014), color=tc, fontweight="bold", zorder=5, clip_on=False)
    ax.text(pos_n[3][0], pos_n[3][1] + 0.11, "left", ha="center", fontsize=_fs(w, 0.01), color=TEAL, style="italic", clip_on=False)
    ax.text(pos_n[10][0], pos_n[10][1] + 0.11, "right", ha="center", fontsize=_fs(w, 0.01), color=AMBER, style="italic", clip_on=False)
    ax_bg.text(
        50,
        27.5,
        r"search for $13$:  $8 \rightarrow 10 \rightarrow 14 \rightarrow 13$",
        fontsize=_math_fs(w, 0.012),
        color=CORAL,
        ha="center",
        zorder=5,
    )
    ax_bg.text(12, 21.5, r"left $<$ node $<$ right", fontsize=_math_fs(w, 0.0115), color=TEAL, zorder=5)
    ax_bg.text(52, 21.5, r"in-order traversal is sorted", fontsize=_math_fs(w, 0.0115), color=INK_SOFT, style="italic", zorder=5)
    ax_bg.text(12, 17.7, r"search / insert $O(h)$", fontsize=_math_fs(w, 0.0115), color=INK, zorder=5)
    ax_bg.text(52, 17.7, r"balanced: $h \approx \log_2 n$", fontsize=_math_fs(w, 0.0115), color=INK_SOFT, style="italic", zorder=5)
    _caption(
        ax_bg,
        [
            r"A binary search tree stores keys so every left child is smaller and every right child is larger.",
            r"Average search is $O(\log n)$ when balanced; a skewed chain falls back to $O(n)$.",
        ],
        w,
        13.5,
    )
    _footer_eq(ax_bg, r"$h \approx \log_2 n$", "balanced height", w)
    return _fig_to_image(fig)


# ── 3 Sorting ────────────────────────────────────────────────────────────────

def plate_sorting(w, h, dpi):
    fig, ax_bg = _new_plate(w, h, dpi)
    _header(
        ax_bg,
        "SORTED BY COMPARISON",
        r"BUBBLE vs MERGE  $\cdot$  $O(n^{2})$ vs $O(n\log n)$",
        "FIG. 3",
        w,
    )
    rng = np.random.default_rng(7)
    arr = rng.integers(3, 20, size=10)
    # bubble mid-pass (partially sorted left)
    bubble = arr.copy()
    for i in range(4):
        for j in range(len(bubble) - 1 - i):
            if bubble[j] > bubble[j + 1]:
                bubble[j], bubble[j + 1] = bubble[j + 1], bubble[j]
    merge_sorted = np.sort(arr)

    def draw_bars(ax, data, colors, title, y_label=True):
        x = np.arange(len(data))
        ax.bar(x, data, color=colors, edgecolor=LINE_DARK, linewidth=0.6, width=0.72, zorder=3)
        ax.set_xlim(-0.6, len(data) - 0.4)
        ax.set_ylim(0, max(data) * 1.25)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(GRID)
            spine.set_linewidth(0.7)
        ax.set_facecolor(CREAM)
        ax.set_title(title, fontsize=_math_fs(w, 0.012), color=INK, pad=8, fontfamily="serif")
        ax.grid(axis="y", color=GRID, lw=0.4, zorder=1)

    # three panels: unsorted, bubble mid, merge done
    ax1 = fig.add_axes([0.10, 0.42, 0.26, 0.38], zorder=3)
    ax2 = fig.add_axes([0.39, 0.42, 0.26, 0.38], zorder=3)
    ax3 = fig.add_axes([0.68, 0.42, 0.26, 0.38], zorder=3)
    c0 = [SLATE] * len(arr)
    c1 = [TEAL if i < 6 else CORAL for i in range(len(bubble))]
    c2 = [AMBER] * len(merge_sorted)
    draw_bars(ax1, arr, c0, "input (unsorted)")
    draw_bars(ax2, bubble, c1, r"bubble mid-pass $O(n^{2})$")
    draw_bars(ax3, merge_sorted, c2, r"merge complete $O(n\log n)$")

    # complexity chips
    chips = [
        (r"Bubble sort", r"$O(n^{2})$ comparisons", CORAL, 12),
        (r"Insertion sort", r"$O(n^{2})$ worst case", AMBER, 38),
        (r"Merge / heap sort", r"$O(n\log n)$ guaranteed", TEAL, 64),
    ]
    for title, body, col, x in chips:
        ax_bg.add_patch(
            FancyBboxPatch(
                (x, 26),
                24,
                10,
                boxstyle="round,pad=0.3,rounding_size=0.6",
                facecolor=CREAM_WARM,
                edgecolor=col,
                linewidth=1.2,
                zorder=4,
            )
        )
        ax_bg.text(x + 12, 33, title, ha="center", fontsize=_fs(w, 0.01), color=col, fontweight="bold", zorder=5)
        ax_bg.text(x + 12, 29, body, ha="center", fontsize=_math_fs(w, 0.01), color=INK_SOFT, zorder=5)

    _caption(
        ax_bg,
        [
            r"Sorting rearranges keys so each is $\le$ the next. Naive double loops cost $O(n^{2})$ comparisons.",
            r"Divide-and-conquer (merge sort) keeps $O(n\log n)$ even in the worst case --- the classroom default for large $n$.",
        ],
        w,
        20.0,
    )
    _footer_eq(ax_bg, r"$O(n\log n)$", "efficient comparison sorts", w, TEAL)
    return _fig_to_image(fig)


# ── 4 Logic gates — drawn in PLATE coords (0–100), never clipped by aspect ───

def _draw_and_body(ax, x0, y0, bw, bh, color, invert=False):
    """
    AND/NAND in plate coords.
    x0,y0 = lower-left of rectangular part; body width bw, height bh.
    """
    # rectangular left + semicircle right, single filled path
    n = 48
    theta = np.linspace(-np.pi / 2, np.pi / 2, n)
    cx, cy = x0 + bw * 0.55, y0 + bh / 2
    r = bh / 2
    # outline points clockwise from bottom-left
    pts = [(x0, y0), (cx, y0)]
    pts += list(zip(cx + r * np.cos(theta), cy + r * np.sin(theta)))
    pts += [(x0, y0 + bh), (x0, y0)]
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 2) + [MplPath.CLOSEPOLY]
    ax.add_patch(
        PathPatch(MplPath(pts, codes), facecolor=color, edgecolor=color, lw=1.8, alpha=0.12, zorder=3)
    )
    ax.add_patch(
        PathPatch(MplPath(pts, codes), facecolor="none", edgecolor=color, lw=1.9, zorder=4)
    )
    # inputs
    iy1, iy2 = y0 + bh * 0.72, y0 + bh * 0.28
    ix = x0 - bw * 0.35
    ax.plot([ix, x0], [iy1, iy1], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    ax.plot([ix, x0], [iy2, iy2], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    ax.plot(ix, iy1, "o", color=color, ms=3.8, zorder=5)
    ax.plot(ix, iy2, "o", color=color, ms=3.8, zorder=5)
    # output
    ox = cx + r
    if invert:
        bub = 0.55
        ax.add_patch(Circle((ox + bub, cy), bub, fill=False, edgecolor=color, lw=1.7, zorder=5))
        ox = ox + 2 * bub
    ax.plot([ox, ox + bw * 0.28], [cy, cy], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    return ix, iy1, iy2, cy


def _draw_or_body(ax, x0, y0, bw, bh, color, invert=False, xor=False):
    """OR / NOR / XOR curved body in plate coords."""
    cy = y0 + bh / 2
    # parametric OR shield
    t = np.linspace(0, 1, 40)
    # left concave curve
    left_x = x0 + bw * 0.12 * (1 - np.cos(np.pi * (t - 0.5)))
    left_y = y0 + bh * t
    # upper edge to tip
    tip_x = x0 + bw * 0.95
    tip_y = cy
    up_t = np.linspace(0, 1, 30)
    up_x = x0 + bw * 0.12 + (tip_x - x0 - bw * 0.12) * up_t
    up_y = y0 + bh - (bh / 2) * (up_t ** 1.3)
    dn_x = up_x[::-1]
    dn_y = y0 + (bh / 2) * (up_t[::-1] ** 1.3)
    xs = np.concatenate([left_x, up_x, dn_x])
    ys = np.concatenate([left_y, up_y, dn_y])
    ax.fill(xs, ys, color=color, alpha=0.12, zorder=3, lw=0)
    ax.plot(xs, ys, color=color, lw=1.9, zorder=4, solid_capstyle="round")
    if xor:
        # extra input arc
        th = np.linspace(-np.pi / 2, np.pi / 2, 28)
        ax.plot(
            x0 - bw * 0.08 + bw * 0.14 * np.cos(th),
            cy + (bh / 2) * 0.95 * np.sin(th),
            color=color,
            lw=1.5,
            zorder=4,
        )
    iy1, iy2 = y0 + bh * 0.72, y0 + bh * 0.28
    ix = x0 - bw * 0.32
    ax.plot([ix, x0 + bw * 0.08], [iy1, iy1], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    ax.plot([ix, x0 + bw * 0.08], [iy2, iy2], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    ax.plot(ix, iy1, "o", color=color, ms=3.8, zorder=5)
    ax.plot(ix, iy2, "o", color=color, ms=3.8, zorder=5)
    ox = tip_x
    if invert:
        bub = 0.55
        ax.add_patch(Circle((ox + bub, cy), bub, fill=False, edgecolor=color, lw=1.7, zorder=5))
        ox = ox + 2 * bub
    ax.plot([ox, ox + bw * 0.22], [cy, cy], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    return ix, iy1, iy2, cy


def _draw_not_body(ax, x0, y0, bw, bh, color):
    cy = y0 + bh / 2
    tri = MplPath(
        [(x0, y0), (x0 + bw * 0.85, cy), (x0, y0 + bh), (x0, y0)],
        [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO, MplPath.CLOSEPOLY],
    )
    ax.add_patch(PathPatch(tri, facecolor=color, edgecolor=color, lw=1.9, alpha=0.12, zorder=3))
    ax.add_patch(PathPatch(tri, facecolor="none", edgecolor=color, lw=1.9, zorder=4))
    bub = 0.55
    ax.add_patch(Circle((x0 + bw * 0.85 + bub, cy), bub, fill=False, edgecolor=color, lw=1.7, zorder=5))
    ix = x0 - bw * 0.32
    ax.plot([ix, x0], [cy, cy], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    ax.plot(ix, cy, "o", color=color, ms=3.8, zorder=5)
    ox = x0 + bw * 0.85 + 2 * bub
    ax.plot([ox, ox + bw * 0.18], [cy, cy], color=color, lw=1.7, zorder=4, solid_capstyle="round")
    return ix, cy, cy, cy


def _ensure_circuitikz_gates() -> str:
    """Build cream-bg IEEE gates PNG via circuitikz if missing/stale."""
    import subprocess
    import sys

    png = os.path.join(OUT, "_circuitikz_gates.png")
    script = os.path.join(OUT, "_render_circuitikz_gates.py")
    if os.path.isfile(script):
        # always refresh so palette/tex changes apply
        subprocess.run([sys.executable, script], check=False, capture_output=True)
    return png


def plate_logic(w, h, dpi):
    """
    Logic plate: professional IEEE ports from circuitikz (LaTeX),
    composited onto the MathRelaxing scientific plate.
    Cream pagecolor matches plate — no white 'sticker' look.
    """
    fig, ax = _new_plate(w, h, dpi)
    _header(
        ax,
        "BOOLEAN BUILDING BLOCKS",
        r"LOGIC GATES  $\cdot$  AND · OR · NOT · XOR · NAND · NOR",
        "FIG. 4",
        w,
    )

    png = _ensure_circuitikz_gates()
    if not os.path.isfile(png):
        # last-resort message
        ax.text(50, 55, "circuitikz render missing", ha="center", color=CORAL, zorder=5)
    else:
        gates = Image.open(png).convert("RGB")
        # soft frame card matching plate
        ax.add_patch(
            FancyBboxPatch(
                (8, 30),
                84,
                50,
                boxstyle="round,pad=0.35,rounding_size=0.7",
                facecolor=CREAM_WARM,
                edgecolor=GRID,
                lw=1.0,
                zorder=2,
            )
        )
        # Place gates image in plate coords via inset axes (fraction of figure)
        # Map plate y 32–78, x 10–90 → figure fractions
        # plate y increases up in data but axes is full figure with y 0–100 bottom-top...
        # Our plate ax is full [0,0,1,1] with ylim 0–100, y=0 at bottom.
        # imshow extent: [left, right, bottom, top] in data coords
        ax.imshow(
            gates,
            extent=[10, 90, 33, 78],
            aspect="auto",
            zorder=3,
            interpolation="lanczos",
        )

    ax.text(10, 27.5, r"$0$ false  ·  $1$ true", fontsize=_math_fs(w, 0.0105), color=INK_SOFT, zorder=5)
    ax.text(
        55,
        27.5,
        r"NAND / NOR are functionally complete",
        fontsize=_math_fs(w, 0.0105),
        color=TEAL,
        style="italic",
        zorder=5,
    )

    _caption(
        ax,
        [
            r"Logic gates implement Boolean algebra in hardware --- the atoms of every digital chip.",
            r"Any computable Boolean function can be built from NAND alone (or NOR alone).",
        ],
        w,
        21.0,
    )
    _footer_eq(ax, r"$A \cdot B$,\ $A+B$,\ $\overline{A}$", "Boolean algebra", w, TEAL)
    return _fig_to_image(fig)


# ── 5 OSI layers ─────────────────────────────────────────────────────────────

def plate_osi(w, h, dpi):
    fig, ax_bg = _new_plate(w, h, dpi)
    _header(
        ax_bg,
        "SEVEN LAYERS OF THE NETWORK",
        r"OSI MODEL  $\cdot$  application $\rightarrow$ physical",
        "FIG. 5",
        w,
    )
    layers = [
        ("7  Application", "HTTP, DNS, SMTP", CORAL),
        ("6  Presentation", "encryption, encoding", AMBER),
        ("5  Session", "dialogs and checkpoints", "#C4A35A"),
        ("4  Transport", "TCP / UDP ports", TEAL),
        ("3  Network", "IP routing", SLATE),
        ("2  Data link", "frames, MAC", INDIGO),
        ("1  Physical", "bits on the wire", "#5C6B7A"),
    ]
    top, bot = 82, 24
    n = len(layers)
    band_h = (top - bot) / n
    for i, (name, desc, col) in enumerate(layers):
        y1 = top - i * band_h
        y0 = y1 - band_h + 0.4
        ax_bg.add_patch(
            FancyBboxPatch(
                (12, y0),
                76,
                band_h - 0.6,
                boxstyle="round,pad=0.15,rounding_size=0.4",
                facecolor=col,
                edgecolor="none",
                alpha=0.18,
                zorder=3,
            )
        )
        ax_bg.add_patch(
            Rectangle((12, y0), 2.2, band_h - 0.6, facecolor=col, edgecolor="none", zorder=4)
        )
        ax_bg.text(17, (y0 + y1) / 2 - 0.3, name, va="center", fontsize=_fs(w, 0.013), color=INK, fontweight="bold", zorder=5)
        ax_bg.text(55, (y0 + y1) / 2 - 0.3, desc, va="center", fontsize=_fs(w, 0.011), color=INK_SOFT, style="italic", zorder=5)

    ax_bg.annotate(
        "",
        xy=(90, 26),
        xytext=(90, 80),
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.4),
        zorder=5,
    )
    ax_bg.text(92, 53, "down\nthe\nstack", fontsize=_fs(w, 0.009), color=TEAL, va="center", zorder=5)

    _caption(
        ax_bg,
        [
            r"The OSI model separates networking into seven layers so each can evolve independently.",
            r"Real stacks (TCP/IP) collapse some layers, but the mental model remains the classroom standard.",
        ],
        w,
        18.5,
    )
    _footer_eq(ax_bg, r"L7 $\rightarrow$ L1", "encapsulation path", w, SLATE)
    return _fig_to_image(fig)


# ── 6 Stack & Queue ──────────────────────────────────────────────────────────

def plate_stack_queue(w, h, dpi):
    fig, ax_bg = _new_plate(w, h, dpi)
    _header(
        ax_bg,
        "LIFO  AND  FIFO",
        r"STACK vs QUEUE  $\cdot$  push/pop  ·  enqueue/dequeue",
        "FIG. 6",
        w,
    )
    ax = fig.add_axes([0.08, 0.28, 0.84, 0.52], zorder=3)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12)
    ax.set_axis_off()
    ax.set_facecolor("none")

    # Stack (vertical)
    stack_vals = ["D", "C", "B", "A"]
    sx, sy, bw, bh = 3.5, 1.5, 3.2, 1.6
    for i, v in enumerate(stack_vals):
        y = sy + i * (bh + 0.15)
        col = CORAL if i == len(stack_vals) - 1 else TEAL_SOFT
        ax.add_patch(
            FancyBboxPatch(
                (sx, y),
                bw,
                bh,
                boxstyle="round,pad=0.05,rounding_size=0.12",
                facecolor=NODE_PATH_FILL if i == len(stack_vals) - 1 else NODE_LEFT_FILL,
                edgecolor=col,
                lw=1.8,
                zorder=3,
            )
        )
        ax.text(sx + bw / 2, y + bh / 2, v, ha="center", va="center", fontsize=_fs(w, 0.016), color=INK, fontweight="bold", zorder=4)
    ax.annotate(
        "push / pop",
        xy=(sx + bw / 2, sy + len(stack_vals) * (bh + 0.15) + 0.3),
        xytext=(sx + bw / 2, sy + len(stack_vals) * (bh + 0.15) + 1.6),
        ha="center",
        fontsize=_fs(w, 0.011),
        color=CORAL,
        arrowprops=dict(arrowstyle="<->", color=CORAL, lw=1.3),
        zorder=5,
    )
    ax.text(sx + bw / 2, 0.6, "STACK  (LIFO)", ha="center", fontsize=_fs(w, 0.013), color=CORAL, fontweight="bold")

    # Queue (horizontal)
    q_vals = ["A", "B", "C", "D"]
    qx, qy, qw, qh = 10.5, 5.0, 1.8, 2.4
    for i, v in enumerate(q_vals):
        x = qx + i * (qw + 0.2)
        col = AMBER if i in (0, len(q_vals) - 1) else SLATE
        ax.add_patch(
            FancyBboxPatch(
                (x, qy),
                qw,
                qh,
                boxstyle="round,pad=0.05,rounding_size=0.12",
                facecolor=NODE_RIGHT_FILL if i in (0, len(q_vals) - 1) else CREAM,
                edgecolor=col,
                lw=1.8,
                zorder=3,
            )
        )
        ax.text(x + qw / 2, qy + qh / 2, v, ha="center", va="center", fontsize=_fs(w, 0.016), color=INK, fontweight="bold", zorder=4)
    ax.annotate(
        "enqueue",
        xy=(qx + len(q_vals) * (qw + 0.2) + 0.1, qy + qh / 2),
        xytext=(qx + len(q_vals) * (qw + 0.2) + 1.4, qy + qh / 2),
        fontsize=_fs(w, 0.01),
        color=AMBER,
        va="center",
        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2),
        zorder=5,
    )
    ax.annotate(
        "dequeue",
        xy=(qx - 0.15, qy + qh / 2),
        xytext=(qx - 1.6, qy + qh / 2),
        fontsize=_fs(w, 0.01),
        color=AMBER,
        va="center",
        ha="right",
        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2),
        zorder=5,
    )
    ax.text(qx + 2 * (qw + 0.2), 3.8, "QUEUE  (FIFO)", ha="center", fontsize=_fs(w, 0.013), color=AMBER, fontweight="bold")

    _caption(
        ax_bg,
        [
            r"A stack is last-in, first-out (LIFO) --- call stacks, undo buffers, depth-first search.",
            r"A queue is first-in, first-out (FIFO) --- print jobs, breadth-first search, request pipelines.",
        ],
        w,
        20.0,
    )
    _footer_eq(ax_bg, r"LIFO $\mid$ FIFO", "abstract data types", w, AMBER)
    return _fig_to_image(fig)


# ── 7 FSM — compact diagram + tight labels + integrated table ────────────────

def _ensure_tikz_fsm() -> str:
    """Build cream-bg turnstile FSM PNG via TikZ automata if missing/stale."""
    import subprocess
    import sys

    png = os.path.join(OUT, "_tikz_fsm.png")
    script = os.path.join(OUT, "_render_tikz_fsm.py")
    if os.path.isfile(script):
        # always refresh so palette/tex changes apply
        subprocess.run([sys.executable, script], check=False, capture_output=True)
    return png


def plate_fsm(w, h, dpi):
    """
    FSM plate: textbook turnstile automaton from TikZ automata library (LaTeX),
    composited onto the MathRelaxing scientific plate.
    Diagram + legend + transition table live in one cream render — no white sticker.
    """
    fig, ax = _new_plate(w, h, dpi)
    _header(
        ax,
        "STATES AND TRANSITIONS",
        r"FINITE STATE MACHINE  $\cdot$  turnstile",
        "FIG. 7",
        w,
    )

    png = _ensure_tikz_fsm()
    if not os.path.isfile(png):
        ax.text(50, 55, "TikZ FSM render missing", ha="center", color=CORAL, zorder=5)
    else:
        fsm = Image.open(png).convert("RGB")
        # soft frame card matching plate (same recipe as circuitikz logic)
        ax.add_patch(
            FancyBboxPatch(
                (7, 28),
                86,
                52,
                boxstyle="round,pad=0.35,rounding_size=0.7",
                facecolor=CREAM_WARM,
                edgecolor=GRID,
                lw=1.0,
                zorder=2,
            )
        )
        # Fit TikZ image with true aspect so automata circles stay round.
        # Plate data is 0–100×0–100; figure is w×h inches → visual aspect of
        # a data rect [dx, dy] is (dx/dy)*(w/h). Match image pixel aspect.
        img_w, img_h = fsm.size
        img_aspect = img_w / img_h
        avail_x0, avail_x1 = 9.0, 91.0
        avail_y0, avail_y1 = 29.5, 78.5
        avail_dx = avail_x1 - avail_x0
        avail_dy = avail_y1 - avail_y0
        # data dx/dy needed so visual aspect == img_aspect
        target_dx_over_dy = img_aspect * (h / w)
        dx = avail_dx
        dy = dx / target_dx_over_dy
        if dy > avail_dy:
            dy = avail_dy
            dx = dy * target_dx_over_dy
        cx = (avail_x0 + avail_x1) / 2
        cy = (avail_y0 + avail_y1) / 2 + 0.5  # slight bias up toward header
        ax.imshow(
            fsm,
            extent=[cx - dx / 2, cx + dx / 2, cy - dy / 2, cy + dy / 2],
            aspect="auto",
            zorder=3,
            interpolation="lanczos",
        )

    _caption(
        ax,
        [
            r"A finite state machine has states $Q$ and a transition function $\delta$ labeled by inputs $\Sigma$.",
            r"Turnstile: coin unlocks; push on locked stays locked; push on unlocked locks again.",
        ],
        w,
        21.5,
    )
    _footer_eq(ax, r"$M=(Q,\Sigma,\delta,q_0,F)$", "formal definition", w, INDIGO)
    return _fig_to_image(fig)


PLATES = {
    "big_o": ("big_o", "How Algorithms Grow", plate_big_o),
    "bst": ("bst", "Binary Search Tree", plate_bst),
    "sorting": ("sorting", "Sorting Comparison", plate_sorting),
    "logic": ("logic", "Boolean Logic Gates", plate_logic),
    "osi": ("osi", "OSI Network Layers", plate_osi),
    "stack_queue": ("stack_queue", "Stack and Queue", plate_stack_queue),
    "fsm": ("fsm", "Finite State Machine", plate_fsm),
}


def build_prints(only: set[str] | None = None):
    os.makedirs(PRINTS, exist_ok=True)
    for key, (slug, title, fn) in PLATES.items():
        if only and key not in only:
            continue
        plate_dir = os.path.join(PRINTS, slug)
        os.makedirs(plate_dir, exist_ok=True)
        for size_name, (pw, ph) in SIZES.items():
            print(f"  {slug} {size_name}…")
            img = fn(pw, ph, DPI_PRINT)
            path = os.path.join(plate_dir, f"{slug}_{size_name}_{DPI_PRINT}dpi.jpg")
            save_jpg(img, path, quality=88, dpi=DPI_PRINT)


def build_zip():
    zip_path = os.path.join(OUT, "Computer_Science_Poster_Set.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            """Computer Science Educational Wall Art Set
MathRelaxing scientific plates

7 posters:
  1. How Algorithms Grow — Big-O complexity
  2. Ordered by Comparison — Binary search tree
  3. Sorted by Comparison — Bubble vs merge sort
  4. Boolean Building Blocks — Logic gates
  5. Seven Layers of the Network — OSI model
  6. LIFO & FIFO — Stack and queue
  7. States and Transitions — Finite state machine

Aspect ratios @ 240 dpi JPG:
  2:3 · 3:4 · 4:5 · 5:7 · ISO A4 · A3

Print on matte paper. Personal use only.
© MathRelaxing
""",
        )
        for slug, _, _ in PLATES.values():
            plate_dir = os.path.join(PRINTS, slug)
            if not os.path.isdir(plate_dir):
                continue
            for fn in sorted(os.listdir(plate_dir)):
                if fn.lower().endswith((".jpg", ".jpeg", ".png")):
                    zf.write(os.path.join(plate_dir, fn), arcname=f"{slug}/{fn}")
    mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"ZIP: {zip_path} ({mb:.1f} MB)")
    if mb > 19.5:
        print("WARNING: near Etsy 20MB limit")
    return zip_path


def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_previews(only: set[str] | None = None):
    os.makedirs(PREVIEWS, exist_ok=True)
    # Generate each plate once at preview size
    thumbs = {}
    for key, (slug, title, fn) in PLATES.items():
        if only and key not in only:
            continue
        print(f"preview plate {slug}…")
        img = fn(8.0, 10.0, DPI_PREVIEW)
        path = os.path.join(PREVIEWS, f"cs_preview_{slug}.jpg")
        save_jpg(img, path, quality=90, dpi=DPI_PREVIEW)
        thumbs[key] = img

    # Hero: first plate + set title
    if "big_o" in thumbs:
        hero_src = thumbs["big_o"]
    else:
        hero_src = next(iter(thumbs.values()))
    side = 1200
    hero = Image.new("RGB", (side, side), (18, 23, 46))
    t = hero_src.copy()
    t.thumbnail((int(side * 0.58), int(side * 0.72)), Image.Resampling.LANCZOS)
    hero.paste(t, ((side - t.width) // 2, int(side * 0.06)))
    draw = ImageDraw.Draw(hero)
    draw.rectangle([0, int(side * 0.80), side, side], fill=(18, 23, 46))
    ft, fs = _font(36, True), _font(18)
    title = "Computer Science Posters"
    sub = "7 educational plates  ·  algorithms  ·  systems"
    bb = draw.textbbox((0, 0), title, font=ft)
    draw.text(((side - (bb[2] - bb[0])) // 2, int(side * 0.84)), title, font=ft, fill=(248, 244, 235))
    bb2 = draw.textbbox((0, 0), sub, font=fs)
    draw.text(((side - (bb2[2] - bb2[0])) // 2, int(side * 0.91)), sub, font=fs, fill=(201, 162, 75))
    save_jpg(hero, os.path.join(PREVIEWS, "cs_preview_1_hero.jpg"), 92, DPI_PREVIEW)

    # Grid of all plates
    keys = [k for k in PLATES if k in thumbs]
    cols, rows = 4, 2
    cell_w, cell_h = 340, 420
    grid_w = cols * cell_w + 60
    grid_h = rows * cell_h + 100
    grid = Image.new("RGB", (grid_w, grid_h), (244, 241, 234))
    gd = ImageDraw.Draw(grid)
    gd.text((30, 24), "the set", font=_font(28, True), fill=(26, 26, 26))
    for i, key in enumerate(keys[:8]):
        r, c = divmod(i, cols)
        th = thumbs[key].copy()
        th.thumbnail((cell_w - 20, cell_h - 40), Image.Resampling.LANCZOS)
        x = 30 + c * cell_w + (cell_w - th.width) // 2
        y = 70 + r * cell_h
        grid.paste(th, (x, y))
    save_jpg(grid, os.path.join(PREVIEWS, "cs_preview_2_set.jpg"), 90, DPI_PREVIEW)

    # Included card
    card = Image.new("RGB", (1200, 1200), (244, 241, 234))
    if thumbs:
        mini = next(iter(thumbs.values())).copy()
        mini.thumbnail((480, 640), Image.Resampling.LANCZOS)
        card.paste(mini, (50, 200))
    cd = ImageDraw.Draw(card)
    cd.text((560, 180), "included", font=_font(34, True), fill=(26, 26, 26))
    lines = [
        "7 scientific-plate posters",
        "Big-O · BST · Sorting",
        "Logic gates · OSI model",
        "Stack & queue · FSM",
        "",
        "Ratios: 2:3 · 3:4 · 4:5",
        "5:7 · A4 · A3",
        "240 dpi JPG · ZIP",
        "",
        "LaTeX equations",
        "Classroom & office ready",
        "Instant download",
    ]
    y = 250
    for line in lines:
        cd.text((560, y), line, font=_font(22), fill=(70, 70, 70))
        y += 40
    save_jpg(card, os.path.join(PREVIEWS, "cs_preview_3_included.jpg"), 90, DPI_PREVIEW)

    # Individual listing images for first 4 already saved as cs_preview_{slug}
    # Also numbered 4-7 for Etsy gallery variety
    order = ["big_o", "bst", "sorting", "logic", "osi", "stack_queue", "fsm"]
    for i, key in enumerate(order, start=4):
        if key in thumbs:
            src = os.path.join(PREVIEWS, f"cs_preview_{key}.jpg")
            # copy-style rename for gallery slots if needed — already have per-slug files
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--only", type=str, default="", help="comma keys: big_o,bst,sorting,logic,osi,stack_queue,fsm")
    args = ap.parse_args()
    only = {x.strip() for x in args.only.split(",") if x.strip()} or None

    print("=== CS Educational Poster Set ===")
    print("  gates: native matplotlib (no schemdraw paste)")
    os.makedirs(OUT, exist_ok=True)
    configure_matplotlib(use_latex=not args.no_latex)

    if not args.preview_only:
        build_prints(only)
        build_zip()
    build_previews(only)
    print("done.")


if __name__ == "__main__":
    main()
