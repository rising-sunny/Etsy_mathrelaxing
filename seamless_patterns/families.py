"""
families.py — periodic pattern families, all drawn on the unit square.

Every family here is periodic by construction, which is the point: a repeat is
computed, not drawn and then patched at the edges. Two rules keep it that way.

  Grid families (Truchet, Celtic, star lattice) place motifs inside cells of an
  n x n grid. Strands meet cell edges perpendicular at the midpoints, so cutting
  the image at the grid cuts every strand the same way on both sides.

  Scatter families (Voronoi) are drawn on a torus: seeds are replicated into the
  eight neighbouring copies of the square before the geometry is computed, so
  a cell that leaves one edge arrives at the other already matching.

Penrose is deliberately absent. A Penrose tiling is aperiodic -- it has no
translational symmetry at all -- so no finite patch of it can be a repeat. It
was in the original plan; it cannot exist as a product.
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Polygon
from scipy.spatial import Voronoi

# ── Colorways ────────────────────────────────────────────────────────────────
# Surface-pattern buyers shop by palette, so these are chosen as decor colours
# rather than the cream/ink of the wall-art line.
PALETTES = {
    "ink":       {"line": "#1b1b1b", "bg": "#ffffff"},
    "indigo":    {"line": "#26324d", "bg": "#eef1f6"},
    "terracotta": {"line": "#a4512f", "bg": "#faf1e8"},
    "sage":      {"line": "#3f5b46", "bg": "#eef2ea"},
    "gold":      {"line": "#9a7b2f", "bg": "#1e1c19"},
}


def _arc(cx, cy, r, t0, t1, n=64):
    t = np.linspace(np.radians(t0), np.radians(t1), n)
    return cx + r * np.cos(t), cy + r * np.sin(t)


def _stroke(ax, x, y, line, lw, band, z=4, closed=False):
    """A strand: background casing underneath, coloured core on top.

    The casing is what makes strands read as passing over one another instead
    of merging into a blob where they meet.
    """
    if closed:
        x = np.append(x, x[0]); y = np.append(y, y[0])
    if band > 0:
        ax.plot(x, y, color=line["bg"], lw=lw + band, solid_capstyle="butt",
                zorder=z, clip_on=True)
    ax.plot(x, y, color=line["line"], lw=lw, solid_capstyle="butt",
            zorder=z + 0.5, clip_on=True)


# ── Truchet-based families ───────────────────────────────────────────────────
def _cells(n, seed):
    rng = np.random.default_rng(seed)
    return rng, 1.0 / n


def _ring(n, seed, size=None):
    """Tile choices plus the indices to draw, including one ring outside.

    Strokes that stop exactly on the border leave those boundary pixels only
    half covered, because the border falls mid-pixel. Half coverage on one
    edge against full coverage on the other shows up as a pale line down the
    join -- measured at 140 vs 27 on a 0-255 scale, and plainly visible once
    magnified. Drawing one ring of cells beyond the square, indexed modulo n
    so it is the same pattern wrapping round, floods those pixels from both
    sides; the axes clip the overspill.
    """
    rng = np.random.default_rng(seed)
    choice = rng.integers(2, size=size or (n, n))
    return choice, 1.0 / n, range(-1, n + 1)


def truchet_arc(ax, pal, n=6, lw=3.0, seed=0, band=0.0, **_):
    """Smith tiles: two quarter-circle arcs per cell, one of two orientations."""
    choice, s, rng_ij = _ring(n, seed)
    for i in rng_ij:
        for j in rng_ij:
            x0, y0 = j * s, i * s
            if choice[i % n, j % n]:
                corners = [(x0, y0, 0, 90), (x0 + s, y0 + s, 180, 270)]
            else:
                corners = [(x0 + s, y0, 90, 180), (x0, y0 + s, 270, 360)]
            for cx, cy, t0, t1 in corners:
                _stroke(ax, *_arc(cx, cy, s / 2, t0, t1), pal, lw, band)


def truchet_maze(ax, pal, n=10, lw=3.0, seed=0, band=0.0, **_):
    """Diagonals only -- the '10 PRINT' maze, a classic surface pattern.

    Offset by half a cell so the image border runs through cell *centres*
    instead of cell corners. Cut at a corner, the border lands where two
    independently-chosen diagonals happen to meet, and the two sides disagree;
    cut through the centre it always crosses one diagonal at 45 degrees, and
    periodic indexing guarantees the cell beyond the top edge is the same cell
    that sits above the bottom edge. Cutting at corners left visible stubs
    along the join.
    """
    rng, s = _cells(n, seed)
    choice = rng.integers(2, size=(n, n))
    for i in range(-1, n + 1):
        for j in range(-1, n + 1):
            x0, y0 = j * s - s / 2, i * s - s / 2
            if choice[i % n, j % n]:
                x, y = np.array([x0, x0 + s]), np.array([y0, y0 + s])
            else:
                x, y = np.array([x0, x0 + s]), np.array([y0 + s, y0])
            _stroke(ax, x, y, pal, lw, band)


def celtic(ax, pal, n=6, lw=3.0, seed=0, band=2.6, cross_prob=0.34, **_):
    """Celtic weave: Truchet arcs plus crossings, with true over/under.

    Every tile connects all four edge midpoints, so neighbouring tiles always
    align and no strand ever dead-ends -- including across the image border.
    """
    rng = np.random.default_rng(seed)
    s = 1.0 / n
    kind = rng.random((n, n))            # < cross_prob -> crossing, else arcs
    flip = rng.integers(2, size=(n, n))
    under, over = [], []           # every strand; and the one crossing on top
    for i in range(-1, n + 1):
        for j in range(-1, n + 1):
            x0, y0 = j * s, i * s
            a, b = i % n, j % n
            if kind[a, b] < cross_prob:
                under.append((np.array([x0, x0 + s]),
                              np.array([y0 + s / 2, y0 + s / 2])))
                over.append((np.array([x0 + s / 2, x0 + s / 2]),
                             np.array([y0, y0 + s])))
            else:
                if flip[a, b]:
                    corners = [(x0, y0, 0, 90), (x0 + s, y0 + s, 180, 270)]
                else:
                    corners = [(x0 + s, y0, 90, 180), (x0, y0 + s, 270, 360)]
                under += [_arc(cx, cy, s / 2, t0, t1) for cx, cy, t0, t1 in corners]

    # Passes, not per-cell drawing. Alternating the z-order cell by cell let a
    # cell's white casing sit above its neighbour's ink and erase it along the
    # shared edge. Harmless in the interior, fatal on the border ring added
    # above: it reopened the very pixels the ring exists to fill. Casings go
    # down first, then all cores, and only the crossing strand cuts a gap --
    # inside its own cell, which is the one place a gap is wanted.
    def pen(items, colour, width, z):
        for x, y in items:
            ax.plot(x, y, color=colour, lw=width, solid_capstyle="butt", zorder=z)

    pen(under + over, pal["bg"], lw + band, 1)
    pen(under, pal["line"], lw, 2)
    pen(over, pal["bg"], lw + band, 3)
    pen(over, pal["line"], lw, 4)


# ── Islamic star lattice ─────────────────────────────────────────────────────
def star_lattice(ax, pal, n=4, lw=2.6, seed=0, band=2.4, points=8, **_):
    """Khatam: an eight-pointed star at each lattice node, joined by crosses.

    Periodic on the square lattice, so the unit square repeats exactly. Motifs
    are drawn in the eight neighbouring copies too, so a star sitting on the
    border arrives whole on the opposite side.
    """
    s = 1.0 / n
    r_out, r_in = s * 0.46, s * 0.19
    # No angular offset. Offsetting by half a step put the star's points at
    # 22.5, 67.5, ... degrees, leaving nothing on the horizontal and vertical
    # axes -- so the connectors, which run along those axes, began outside the
    # silhouette and floated between the stars as loose bars instead of joining
    # them. Starting at zero puts a point on each axis for the links to meet.
    ang = np.arange(2 * points) * (np.pi / points)
    rad = np.where(np.arange(2 * points) % 2 == 0, r_out, r_in)
    reach = r_out * 0.94          # overlap the tip so the join reads as one line
    for i in range(-1, n + 1):
        for j in range(-1, n + 1):
            cx, cy = j * s, i * s
            _stroke(ax, cx + rad * np.cos(ang), cy + rad * np.sin(ang),
                    pal, lw, band, closed=True)
            _stroke(ax, np.array([cx + reach, cx + s - reach]),
                    np.array([cy, cy]), pal, lw, band, z=3)
            _stroke(ax, np.array([cx, cx]),
                    np.array([cy + reach, cy + s - reach]), pal, lw, band, z=3)


def interlace_circles(ax, pal, n=5, lw=2.8, seed=0, band=2.6, **_):
    """Overlapping circle lattice -- the classic 'flower of life' grid."""
    s = 1.0 / n
    r = s * 0.62
    for i in range(-1, n + 2):
        for j in range(-1, n + 2):
            cx, cy = j * s, i * s
            z = 4 + ((i + j) % 3) * 2      # rotate depth so circles interlace
            _stroke(ax, *_arc(cx, cy, r, 0, 360, n=200), pal, lw, band, z=z)


# ── Toroidal Voronoi ─────────────────────────────────────────────────────────
def voronoi_cells(ax, pal, k=5, lw=2.4, seed=0, band=0.0, **_):
    """Organic cell pattern computed on a torus so the edges match exactly.

    Seeds come from a jittered grid rather than uniform random points. Uniform
    points put two seeds almost on top of each other often enough that every
    tile grew a few sliver cells -- two near-parallel lines a hair apart, which
    reads as a printing mistake, and repeats nine times on a proof sheet.
    Jitter kept under half a cell kills slivers while staying organic.
    """
    rng = np.random.default_rng(seed)
    s = 1.0 / k
    gx, gy = np.meshgrid((np.arange(k) + 0.5) * s, (np.arange(k) + 0.5) * s)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    pts = (pts + rng.uniform(-0.42 * s, 0.42 * s, pts.shape)) % 1.0
    tiled = np.vstack([pts + (dx, dy)
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
    vor = Voronoi(tiled)
    for a, b in vor.ridge_vertices:
        if a < 0 or b < 0:
            continue
        p, q = vor.vertices[a], vor.vertices[b]
        # keep ridges anywhere near the unit square; the axes clip the rest
        if max(p[0], q[0]) < -0.3 or min(p[0], q[0]) > 1.3:
            continue
        if max(p[1], q[1]) < -0.3 or min(p[1], q[1]) > 1.3:
            continue
        _stroke(ax, np.array([p[0], q[0]]), np.array([p[1], q[1]]), pal, lw, band)


# The diagonal maze and the Voronoi cells are built above but deliberately not
# shipped. Both failed verification at every resolution and every line weight
# (0.43-0.75 against a 0.90 floor, and getting worse as the stroke thickened,
# so it is a geometric displacement rather than a sampling artefact). Both draw
# strokes that cross the tile border at an angle; every family that ships
# crosses it perpendicular. Left here because the finding is worth keeping, and
# excluded because a repeat that does not repeat is not sellable.
UNVERIFIED = {"truchet_maze": truchet_maze, "organic_cells": voronoi_cells}

FAMILIES = {
    "celtic_weave": celtic,
    "truchet_arcs": truchet_arc,
    "star_lattice": star_lattice,
    "circle_lattice": interlace_circles,
}
