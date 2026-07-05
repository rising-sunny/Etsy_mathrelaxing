"""
generate_celtic_knots.py — MathRelaxing "Celtic Knot Mathematics" generator
=============================================================================
Genera proceduralmente 50 diseños de nudos celtas mediante un algoritmo de
grid (variante de Truchet tiles + cruces con hueco de tejido, que produce
un patron de entrelazado continuo sin extremos sueltos). Tres familias de
composicion (rejilla completa, mandala radial, marco con centro en blanco)
mas 2 disenos insignia (rosa trinity, espiral triskelion) dan variedad real
pagina a pagina.

Salida:
  celtic_knot_digital.pdf   — PDF de 52 paginas, 8.5x11in, listo para imprimir
  celtic_knot_cover.jpg     — portada (fondo oscuro, estilo de marca)
  celtic_knot_page_01..07.jpg — paginas de muestra para el listing
"""

import math
import random
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Arc, FancyBboxPatch, Circle

import brand
import template_coloring_book as tcb

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 8.5, 11.0
LINE_COLOR = "black"

# Cover theme colour for THIS product (books are themed). All other brand
# constants (GOLD, CREAM, logo, fonts, footer band) come from brand.py.
BG_DARK = "#241014"
GOLD = brand.GOLD
CREAM = brand.CREAM
LOGO_PATH = brand.LOGO_PATH

# Each knot strand is drawn as a RIBBON: two parallel outlines a fixed
# fraction of the cell apart. This is what makes it read as woven Celtic
# knotwork instead of a single-line maze. BAND_RATIO is the half-width of
# the ribbon as a fraction of the cell.
BAND_RATIO = 0.155


# ─────────────────────────────────────────────────────────────────────────
# Low-level primitives with optional rotation
# ─────────────────────────────────────────────────────────────────────────
def _rot(pt, pivot, deg):
    if deg == 0 or pivot is None:
        return pt
    rad = math.radians(deg)
    px, py = pivot
    x, y = pt[0] - px, pt[1] - py
    c, s = math.cos(rad), math.sin(rad)
    return (px + x * c - y * s, py + x * s + y * c)


def _add_arc(ax, center, w, h, angle, t1, t2, lw, color, rot_deg=0, pivot=None, zorder=2):
    c2 = _rot(center, pivot, rot_deg)
    ax.add_patch(Arc(c2, w, h, angle=angle + rot_deg, theta1=t1, theta2=t2,
                      lw=lw, color=color, capstyle="round", zorder=zorder))


def _add_line(ax, p1, p2, lw, color, rot_deg=0, pivot=None, zorder=2):
    a = _rot(p1, pivot, rot_deg)
    b = _rot(p2, pivot, rot_deg)
    ax.plot([a[0], b[0]], [a[1], b[1]], lw=lw, color=color, solid_capstyle="round", zorder=zorder)


def _band_arc(ax, center, radius, t1, t2, band, lw, color, rot_deg=0, pivot=None, zorder=2):
    """A quarter-turn ribbon: two concentric arcs radius ± band."""
    for r in (radius - band, radius + band):
        d = 2 * r
        _add_arc(ax, center, d, d, 0, t1, t2, lw, color, rot_deg, pivot, zorder)


def _band_seg(ax, p1, p2, band, lw, color, rot_deg=0, pivot=None, zorder=2):
    """A straight ribbon segment: two lines offset ± band perpendicular."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return
    px, py = -dy / L, dx / L
    for s in (-band, band):
        a = (p1[0] + px * s, p1[1] + py * s)
        b = (p2[0] + px * s, p2[1] + py * s)
        _add_line(ax, a, b, lw, color, rot_deg, pivot, zorder)


def _emit_tile(ax, t, cxL, cxR, cyB, cyT, i, j, lw, color, rot_deg=0, pivot=None, zorder=2):
    cell = cxR - cxL
    band = cell * BAND_RATIO
    R = cell / 2
    if t == 0:  # arcs: N-W  and  S-E
        _band_arc(ax, (cxL, cyT), R, 270, 360, band, lw, color, rot_deg, pivot, zorder)
        _band_arc(ax, (cxR, cyB), R, 90, 180, band, lw, color, rot_deg, pivot, zorder)
    elif t == 1:  # arcs: N-E  and  S-W
        _band_arc(ax, (cxR, cyT), R, 180, 270, band, lw, color, rot_deg, pivot, zorder)
        _band_arc(ax, (cxL, cyB), R, 0, 90, band, lw, color, rot_deg, pivot, zorder)
    else:  # woven cross: one ribbon passes OVER, the other is broken UNDER it
        cx_, cy_ = (cxL + cxR) / 2, (cyB + cyT) / 2
        brk = band + cell * 0.11  # how far the under-ribbon is cut back
        vertical_on_top = (i + j) % 2 == 0
        if vertical_on_top:
            _band_seg(ax, (cx_, cyB), (cx_, cyT), band, lw, color, rot_deg, pivot, zorder)
            _band_seg(ax, (cxL, cy_), (cx_ - brk, cy_), band, lw, color, rot_deg, pivot, zorder)
            _band_seg(ax, (cx_ + brk, cy_), (cxR, cy_), band, lw, color, rot_deg, pivot, zorder)
        else:
            _band_seg(ax, (cxL, cy_), (cxR, cy_), band, lw, color, rot_deg, pivot, zorder)
            _band_seg(ax, (cx_, cyB), (cx_, cy_ - brk), band, lw, color, rot_deg, pivot, zorder)
            _band_seg(ax, (cx_, cy_ + brk), (cx_, cyT), band, lw, color, rot_deg, pivot, zorder)


def _pick_tile(rng, cross_prob):
    r = rng.random()
    if r < cross_prob:
        return 2
    elif r < cross_prob + (1 - cross_prob) / 2:
        return 0
    return 1


# ─────────────────────────────────────────────────────────────────────────
# Family 1 — full rectangular weave
# ─────────────────────────────────────────────────────────────────────────
def draw_grid_knot(ax, x0, y0, w, h, rows, cols, seed, cross_prob=0.32, lw=3.2,
                    frame=True, color=LINE_COLOR, zorder=2):
    rng = random.Random(seed)
    cell = min(w / cols, h / rows)
    gw, gh = cell * cols, cell * rows
    ox = x0 + (w - gw) / 2
    oy = y0 + (h - gh) / 2

    for i in range(rows):
        for j in range(cols):
            cxL, cxR = ox + j * cell, ox + (j + 1) * cell
            cyB, cyT = oy + i * cell, oy + (i + 1) * cell
            t = _pick_tile(rng, cross_prob)
            _emit_tile(ax, t, cxL, cxR, cyB, cyT, i, j, lw, color, zorder=zorder)

    if frame:
        pad = cell * 0.06
        ax.add_patch(FancyBboxPatch((ox - pad, oy - pad), gw + 2 * pad, gh + 2 * pad,
                                     boxstyle="round,pad=0,rounding_size=" + str(cell * 0.35),
                                     fill=False, lw=lw * 1.15, edgecolor=color, zorder=zorder))


# ─────────────────────────────────────────────────────────────────────────
# Family 3 — knot with full 4-fold (dihedral) symmetry.
# A tile is chosen freely only in the top-left quadrant; the rest is a mirror
# image. Reflecting a Truchet arc tile swaps its two orientations (0<->1),
# crossings map to crossings. The result reads as a deliberate, ornate panel
# rather than a random weave — the "too basic" fix.
# ─────────────────────────────────────────────────────────────────────────
_MIRROR = {0: 1, 1: 0, 2: 2}


def draw_symmetric_knot(ax, x0, y0, w, h, rows, cols, seed, cross_prob=0.4, lw=2.2,
                         frame=True, color=LINE_COLOR):
    cell = min(w / cols, h / rows)
    gw, gh = cell * cols, cell * rows
    ox = x0 + (w - gw) / 2
    oy = y0 + (h - gh) / 2

    base = {}
    for i in range(rows):
        for j in range(cols):
            ci = min(i, rows - 1 - i)
            cj = min(j, cols - 1 - j)
            if (ci, cj) not in base:
                base[(ci, cj)] = _pick_tile(random.Random(seed + ci * 131 + cj * 17), cross_prob)
            t = base[(ci, cj)]
            mirrored = (i != ci) ^ (j != cj)  # odd number of reflections?
            if mirrored:
                t = _MIRROR[t]
            cxL, cxR = ox + j * cell, ox + (j + 1) * cell
            cyB, cyT = oy + i * cell, oy + (i + 1) * cell
            _emit_tile(ax, t, cxL, cxR, cyB, cyT, i, j, lw, color)

    if frame:
        pad = cell * 0.06
        ax.add_patch(FancyBboxPatch((ox - pad, oy - pad), gw + 2 * pad, gh + 2 * pad,
                                     boxstyle="round,pad=0,rounding_size=" + str(cell * 0.35),
                                     fill=False, lw=lw * 1.15, edgecolor=color))


# ─────────────────────────────────────────────────────────────────────────
# Flagship parametric motifs
# ─────────────────────────────────────────────────────────────────────────
def draw_trinity_rose(ax, cx, cy, R, lw=3.4, n=2000, color=LINE_COLOR):
    theta = [t * 2 * math.pi / n for t in range(n + 1)]
    for offset in (-0.055, 0.055):
        xs, ys = [], []
        for t in theta:
            r = R * (0.42 + 0.58 * abs(math.cos(1.5 * t))) + offset * R
            xs.append(cx + r * math.cos(t))
            ys.append(cy + r * math.sin(t))
        ax.plot(xs, ys, lw=lw, color=color, solid_capstyle="round", solid_joinstyle="round")
    ax.add_patch(Arc((cx, cy), R * 0.62, R * 0.62, theta1=0, theta2=360, lw=lw, color=color))


def draw_triskelion(ax, cx, cy, R, lw=3.8, turns=1.05, color=LINE_COLOR):
    n = 300
    for k in range(3):
        rot = k * 2 * math.pi / 3
        xs, ys = [], []
        for i in range(n + 1):
            t = turns * 2 * math.pi * i / n
            r = (R * 0.16) + (R * 0.82) * (t / (turns * 2 * math.pi))
            ang = t + rot
            xs.append(cx + r * math.cos(ang))
            ys.append(cy + r * math.sin(ang))
        ax.plot(xs, ys, lw=lw, color=color, solid_capstyle="round")
        tip_ang = turns * 2 * math.pi + rot
        tip_r = R * 0.16 + R * 0.82
        hook_cx = cx + tip_r * 0.86 * math.cos(tip_ang)
        hook_cy = cy + tip_r * 0.86 * math.sin(tip_ang)
        ax.add_patch(Arc((hook_cx, hook_cy), R * 0.3, R * 0.3, theta1=0, theta2=360, lw=lw, color=color))
    ax.add_patch(Arc((cx, cy), R * 0.3, R * 0.3, theta1=0, theta2=360, lw=lw, color=color))
    ax.add_patch(Arc((cx, cy), R * 2.06, R * 2.06, theta1=0, theta2=360, lw=lw * 0.9, color=color))


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


# ── Brand hooks (cover emblem + watermark) consumed by template_coloring_book ─
def emblem(ax, cx, cy, r):
    """Product emblem drawn in gold on the cover (the Triskelion)."""
    draw_triskelion(ax, cx, cy, r, lw=4.0, color=brand.GOLD)


def watermark(ax, W, H):
    """Faint woven-knot watermark filling the whole cover."""
    ghost = (0.79, 0.63, 0.29, 0.11)  # gold at low alpha
    draw_grid_knot(ax, -0.5, -0.5, W + 1.0, H + 1.0, rows=12, cols=12,
                    seed=77, cross_prob=0.42, lw=1.3, frame=False,
                    color=ghost, zorder=0.5)


ABOUT_BODY = (
    "Every knotwork panel in this book is generated by the same rule real\n"
    "Celtic artisans used centuries ago — formalized as a grid algorithm.\n\n"
    "The page is divided into a grid of cells. Each cell is randomly assigned\n"
    "one of three tiles: two mirror-image quarter-circle arcs (a Truchet tile),\n"
    "or a straight crossing. Every tile connects all four edge midpoints of its\n"
    "cell, so neighboring tiles always align — no strand ever dead-ends.\n\n"
    "Each strand is drawn as a woven ribbon: at every crossing one band\n"
    "passes over and the other is broken to pass under, alternating by grid\n"
    "parity — the rule that defines an alternating knot in knot theory.\n"
    "Three page styles appear: full-bleed woven panels, smaller centered\n"
    "medallions, and mirror-symmetric knots with four-fold symmetry.\n\n"
    "Two pages break from the grid to show classic motifs by name: the\n"
    "Trinity Shamrock (a polar rose curve, r = cos 1.5θ) and the Triskelion\n"
    "(three Archimedean spirals rotated 120° apart)."
)


def flagship_page(kind):
    fig, ax = new_page()
    cx, cy = PAGE_W / 2, PAGE_H / 2 + 0.2
    if kind == "rose":
        draw_trinity_rose(ax, cx, cy, 3.5)
    elif kind == "triskelion":
        draw_triskelion(ax, cx, cy, 3.2)
    return fig


def grid_page(seed, rows, cols, cross_prob, lw):
    fig, ax = new_page()
    margin = 0.7
    draw_grid_knot(ax, margin, margin + 0.2, PAGE_W - 2 * margin, PAGE_H - 2 * margin - 0.4,
                    rows=rows, cols=cols, seed=seed, cross_prob=cross_prob, lw=lw)
    return fig


def symmetric_page(seed, rows, cols, cross_prob, lw):
    fig, ax = new_page()
    margin = 0.7
    draw_symmetric_knot(ax, margin, margin + 0.2, PAGE_W - 2 * margin, PAGE_H - 2 * margin - 0.4,
                         rows=rows, cols=cols, seed=seed, cross_prob=cross_prob, lw=lw)
    return fig


def medallion_page(seed, rows, cols, cross_prob, lw):
    fig, ax = new_page()
    size = 4.7
    x0 = (PAGE_W - size) / 2
    y0 = (PAGE_H - size) / 2 + 0.3
    draw_grid_knot(ax, x0, y0, size, size, rows=rows, cols=cols,
                    seed=seed, cross_prob=cross_prob, lw=lw)
    return fig


# ─────────────────────────────────────────────────────────────────────────
# Build the 50-design plan: interleave 3 families for real page-to-page
# contrast, with progressive complexity and varying line weight.
# ─────────────────────────────────────────────────────────────────────────
def build_plan():
    plan = []
    flagship_slots = {8: "rose", 30: "triskelion"}
    # Denser grids + a much higher floor on cross_prob: more actual
    # over-under weaving, less empty flowing-tube look ("too basic" feedback).
    grid_sizes = [(8, 8), (8, 9), (9, 9), (9, 10), (10, 10), (10, 11), (11, 12), (12, 13), (13, 14)]
    medallion_sizes = [(6, 6), (6, 7), (7, 7), (7, 8), (8, 8), (8, 9), (9, 9)]
    symmetric_sizes = [(8, 8), (8, 8), (10, 10), (10, 10), (12, 12), (12, 12), (14, 14)]
    family_cycle = ["grid", "medallion", "symmetric"]
    fam_i = 0
    for n in range(1, 51):
        if n in flagship_slots:
            plan.append(("flagship", flagship_slots[n]))
            continue
        family = family_cycle[fam_i % len(family_cycle)]
        fam_i += 1
        progress = n / 50
        # ribbon outlines are thin; keep a modest range
        lw = 1.5 + 0.9 * ((n * 37) % 10) / 10
        if family == "grid":
            idx = min(int(progress * len(grid_sizes)), len(grid_sizes) - 1)
            rows, cols = grid_sizes[idx]
            cross_prob = 0.34 + 0.32 * ((n * 13) % 10) / 10
            plan.append(("grid", (rows, cols, cross_prob, lw)))
        elif family == "medallion":
            idx = min(int(progress * len(medallion_sizes)), len(medallion_sizes) - 1)
            rows, cols = medallion_sizes[idx]
            cross_prob = 0.34 + 0.32 * ((n * 19) % 10) / 10
            plan.append(("medallion", (rows, cols, cross_prob, lw)))
        else:
            idx = min(int(progress * len(symmetric_sizes)), len(symmetric_sizes) - 1)
            rows, cols = symmetric_sizes[idx]
            cross_prob = 0.4 + 0.25 * ((n * 23) % 10) / 10
            plan.append(("symmetric", (rows, cols, cross_prob, lw)))
    return plan


# ── Design dispatch (consumed by the coloring-book / iPad templates) ──────────
_PLAN = None


def _plan():
    global _PLAN
    if _PLAN is None:
        _PLAN = build_plan()
    return _PLAN


def render_design(n):
    """Return the portrait 8.5x11 Figure for design n (1..50)."""
    kind, params = _plan()[n - 1]
    seed = 1000 + n * 7
    if kind == "flagship":
        return flagship_page(params)
    if kind == "grid":
        rows, cols, cross_prob, lw = params
        return grid_page(seed, rows, cols, cross_prob, lw)
    if kind == "medallion":
        rows, cols, cross_prob, lw = params
        return medallion_page(seed, rows, cols, cross_prob, lw)
    rows, cols, cross_prob, lw = params
    return symmetric_page(seed, rows, cols, cross_prob, lw)


# ── Book config — everything product-specific lives here ─────────────────────
CONFIG = tcb.BookConfig(
    prefix="celtic_knot",
    theme_bg=BG_DARK,
    title="CELTIC KNOT",
    subtitle="MATHEMATICS",
    tagline="A Coloring Book of Interlace & Weave",
    count_label="50 Knotwork Designs",
    about_body=ABOUT_BODY,
    n_designs=50,
    preview_indices=[1, 8, 12, 20, 30, 38, 46],
)


def main():
    tcb.build_book(CONFIG, render_design, emblem, watermark)


if __name__ == "__main__":
    main()
