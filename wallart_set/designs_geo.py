"""
designs_geo.py — "Geometric Tilings" collection: six original tessellation /
geometric designs, none reused from the shop renderer. Same interface as
designs.py (COLLECTION, PALETTES, use_palette, accent, DESIGNS, RATIOS, ORDER,
SUB, SET_*, GRID_TITLE, anim_data, LISTINGS) so the shared pipeline can drive it.

  penrose    Penrose P3 aperiodic rhombus tiling (deflation)
  truchet    Truchet tiles — random quarter-arc weave
  girih      Islamic girih — {8/3} star grid
  rhombille  Rhombille tiling — isometric cube illusion
  sierpinski Sierpinski triangle (recursive)
  flower     Flower of Life — overlapping circle lattice

Geometric line art reads best in a single ink per palette (not multicolour),
so each palette here is ground + ink.
"""
import math
import cmath
import functools
import numpy as np

COLLECTION = "geo"
SLUG = "GeometricTilings"
SET_NAME = "Geometric Tilings"
SET_TAGLINE = "Set of 6 printable wall art · classic tessellations, drawn true"
GRID_TITLE = "Six geometric tilings — drawn from real mathematics"

PALETTES = {
    "mono":  {"bg": "#f4efe4", "ink": "#2b2823"},
    "earth": {"bg": "#f2ebdd", "ink": "#6b4f3f"},
    "cool":  {"bg": "#e9e9e3", "ink": "#43505a"},
}
BG = PALETTES["mono"]["bg"]
INK = PALETTES["mono"]["ink"]


def use_palette(name):
    global BG, INK
    BG = PALETTES[name]["bg"]
    INK = PALETTES[name]["ink"]


def accent():
    return INK


RATIOS = {
    "2x3": (2, 3), "3x4": (3, 4), "4x5": (4, 5), "5x7": (5, 7),
    "ISO": (1, math.sqrt(2)),
}
ORDER = ["penrose", "truchet", "girih", "rhombille", "sierpinski", "flower"]


# ---- geometry (deterministic; cached) ---------------------------------------
@functools.lru_cache(maxsize=None)
def _penrose():
    phi = (1 + 5 ** .5) / 2

    def sub(tris):
        res = []
        for c, A, B, C in tris:
            if c == 0:
                P = A + (B - A) / phi
                res += [(0, C, P, B), (1, P, C, A)]
            else:
                Q = B + (A - B) / phi
                R = B + (C - B) / phi
                res += [(1, R, C, A), (1, Q, R, B), (0, R, Q, A)]
        return res
    tris = []
    for i in range(10):
        B = cmath.rect(1, (2 * i - 1) * math.pi / 10)
        C = cmath.rect(1, (2 * i + 1) * math.pi / 10)
        if i % 2 == 0:
            B, C = C, B
        tris.append((0, 0 + 0j, B, C))
    for _ in range(6):
        tris = sub(tris)
    segs = []
    for c, A, B, C in tris:
        segs.append([(A.real, A.imag), (B.real, B.imag)])
        segs.append([(C.real, C.imag), (B.real, B.imag)])
    return segs


@functools.lru_cache(maxsize=None)
def _truchet():
    rng = np.random.default_rng(3)
    n = 9
    th = np.linspace(0, np.pi / 2, 18)
    polys = []
    for i in range(n):
        for j in range(n):
            if rng.random() < 0.5:
                corners = [(i, j, 0.0), (i + 1, j + 1, np.pi)]
            else:
                corners = [(i + 1, j, np.pi / 2), (i, j + 1, -np.pi / 2)]
            for cx, cy, a0 in corners:
                a = a0 + th
                polys.append(np.c_[cx + 0.5 * np.cos(a), cy + 0.5 * np.sin(a)])
    return polys


@functools.lru_cache(maxsize=None)
def _girih():
    segs = []
    for i in range(5):
        for j in range(6):
            pts = [cmath.rect(0.62, math.pi / 8 + k * math.pi / 4) + complex(i, j)
                   for k in range(8)]
            order = [(k * 3) % 8 for k in range(9)]
            for a in range(8):
                p, q = pts[order[a]], pts[order[a + 1]]
                segs.append([(p.real, p.imag), (q.real, q.imag)])
    return segs


@functools.lru_cache(maxsize=None)
def _rhombille():
    segs = []
    dx, dy = 1.5, math.sqrt(3)

    def hexc(cx, cy, r=0.87):
        return [cmath.rect(r, math.pi / 6 + k * math.pi / 3) + complex(cx, cy)
                for k in range(6)]
    for i in range(6):
        for j in range(6):
            cx = i * dx
            cy = j * dy + (i % 2) * dy / 2
            h = hexc(cx, cy)
            for k in range(6):
                a, b = h[k], h[(k + 1) % 6]
                segs.append([(a.real, a.imag), (b.real, b.imag)])
            cen = complex(cx, cy)
            for k in (0, 2, 4):
                segs.append([(cen.real, cen.imag), (h[k].real, h[k].imag)])
    return segs


@functools.lru_cache(maxsize=None)
def _sierpinski():
    segs = []

    def tri(A, B, C, d):
        if d == 0:
            segs.extend([[A, B], [B, C], [C, A]])
            return
        AB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        BC = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
        CA = ((C[0] + A[0]) / 2, (C[1] + A[1]) / 2)
        tri(A, AB, CA, d - 1)
        tri(AB, B, BC, d - 1)
        tri(CA, BC, C, d - 1)
    tri((0.0, 0.0), (1.0, math.sqrt(3)), (2.0, 0.0), 6)
    return segs


@functools.lru_cache(maxsize=None)
def _flower():
    r = 1.0
    centers = []
    for i in range(-4, 5):
        for j in range(-4, 5):
            cx = i * r + (j % 2) * r / 2
            cy = j * r * math.sqrt(3) / 2
            if cx * cx + cy * cy <= (3.05 * r) ** 2:
                centers.append((round(cx, 3), round(cy, 3)))
    centers.sort(key=lambda p: p[0] ** 2 + p[1] ** 2)      # centre-out
    circles = [(cx, cy, r) for cx, cy in centers]
    circles.append((0.0, 0.0, 3 * r))                       # boundary last
    return circles


# ---- kind + data per design (used by both static render and the animator) ---
def data(name):
    if name == "penrose":
        segs = _penrose()
        pts = np.array([p for s in segs for p in s])
        return ("segs", pts[:, 0], pts[:, 1], segs, 0.5)
    if name == "truchet":
        polys = _truchet()
        pts = np.vstack(polys)
        return ("segs", pts[:, 0], pts[:, 1], polys, 0.9)
    if name == "girih":
        segs = _girih()
        pts = np.array([p for s in segs for p in s])
        return ("segs", pts[:, 0], pts[:, 1], segs, 0.8)
    if name == "rhombille":
        segs = _rhombille()
        pts = np.array([p for s in segs for p in s])
        return ("segs", pts[:, 0], pts[:, 1], segs, 0.7)
    if name == "sierpinski":
        segs = _sierpinski()
        pts = np.array([p for s in segs for p in s])
        return ("segs", pts[:, 0], pts[:, 1], segs, 0.5)
    if name == "flower":
        circles = _flower()
        cs = np.array(circles)
        xs = np.r_[cs[:, 0] - cs[:, 2], cs[:, 0] + cs[:, 2]]
        ys = np.r_[cs[:, 1] - cs[:, 2], cs[:, 1] + cs[:, 2]]
        return ("circles", xs, ys, circles, 0.8)
    raise KeyError(name)


def _draw(ax, name, lw_scale, reveal=1.0):
    from matplotlib.collections import LineCollection
    import matplotlib.patches as mp
    kind, xs, ys, items, lw = data(name)
    if kind == "segs":
        k = max(1, int(reveal * len(items)))
        ax.add_collection(LineCollection(items[:k], colors=INK,
                                         linewidths=lw * lw_scale, alpha=0.9))
    else:  # circles
        k = max(1, int(reveal * len(items)))
        for cx, cy, r in items[:k]:
            ax.add_patch(mp.Circle((cx, cy), r, fill=False, edgecolor=INK,
                                   lw=lw * lw_scale, alpha=0.9))
    return xs, ys


def _mk(name):
    def fn(ax, lw_scale=1.0):
        return _draw(ax, name, lw_scale, reveal=1.0)
    return fn


DESIGNS = {
    "penrose":    {"fn": _mk("penrose"),    "title": "Penrose Tiling",  "pad": 1.10},
    "truchet":    {"fn": _mk("truchet"),    "title": "Truchet Weave",   "pad": 1.06},
    "girih":      {"fn": _mk("girih"),      "title": "Girih Stars",     "pad": 1.08},
    "rhombille":  {"fn": _mk("rhombille"),  "title": "Isometric Cubes", "pad": 1.08},
    "sierpinski": {"fn": _mk("sierpinski"), "title": "Sierpinski",      "pad": 1.12},
    "flower":     {"fn": _mk("flower"),     "title": "Flower of Life",  "pad": 1.10},
}

SUB = {
    "penrose": "Aperiodic · golden ratio",
    "truchet": "Truchet tiles",
    "girih": "Islamic girih · 8-fold",
    "rhombille": "Rhombille · isometric",
    "sierpinski": "Recursive triangle",
    "flower": "Overlapping circles",
}


def color(name):
    return INK


def anim_data(name):
    """(kind, xs, ys, items, style) for the drawing animation. Reveal a growing
    prefix of `items` (segments/polylines or circles); style = line width."""
    kind, xs, ys, items, lw = data(name)
    return kind, np.asarray(xs), np.asarray(ys), items, lw * 1.9


def _description():
    return f"""GEOMETRIC TILINGS — a set of 6 printable wall art prints.

Six classic tessellations and geometric constructions, each drawn true from its
mathematics and rendered as clean black-and-white line art. Not AI images and not
clip art — every piece is generated from the real tiling, then composed for a
minimalist / Scandinavian gallery wall.

THE SIX DESIGNS
• Penrose Tiling — an aperiodic rhombus tiling that never repeats (golden ratio)
• Truchet Weave — random quarter-arc tiles that flow into a maze of curves
• Girih Stars — an eight-fold Islamic star grid
• Isometric Cubes — a rhombille tiling that reads as a field of 3D cubes
• Sierpinski — the recursive triangle fractal
• Flower of Life — the overlapping-circle lattice of sacred geometry

WHAT YOU GET (instant digital download)
• All 6 designs in 5 aspect ratios — 2:3, 3:4, 4:5, 5:7 and ISO/A
• 300 DPI, high resolution — print small or large
• Delivered as 5 ZIP files (one per ratio), 30 files in total
• Charcoal line work on a warm ivory ground — a true black-and-white set

PRINT ALMOST ANY SIZE
2:3 → 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in
3:4 → 6x8, 9x12, 12x16, 18x24 in
4:5 → 8x10, 16x20, 24x30 in
5:7 → 5x7, 10x14, 15x21 in
ISO/A → A5, A4, A3, A2, A1

HOW IT WORKS
1) Buy and download instantly — no physical item is shipped.
2) Pick your size and ratio.
3) Print at home, a local print shop, or an online service.
4) Trim to your frame and hang.

Colours may vary slightly between screens and printers. Frames not included.

TERMS — For personal use only. Please do not resell, redistribute or share the files.

(c) MathRelaxing"""


LISTINGS = {
    "mono": {
        "title": ("Set of 6 Geometric Printable Wall Art | Black and White Tessellation Line Art "
                  "Gallery Wall Set | Sacred Geometry Scandinavian Decor"),
        "tags": ["geometric wall art", "black and white art", "printable wall art",
                 "tessellation art", "sacred geometry", "penrose tiling", "line art print",
                 "minimalist print", "gallery wall set", "digital download", "scandinavian art",
                 "mid century art", "math wall art"],
        "description": _description(),
        "price": 9.99,
        "listing_id": 4536907663,   # draft published 2026-07-12 (activation manual)
    },
}
