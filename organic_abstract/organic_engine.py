"""
organic_engine.py — organic abstract shapes, computed rather than drawn.

The look this targets (Matisse-style cut-outs on a deep ground) is usually
drawn by hand, which is why it is a crowded category: anyone can draw a blob.
Every shape here is instead the plot of a closed curve with a formula behind
it, which is the one thing a hand-drawn version cannot claim.

Two generators:

  fourier_blob   r(theta) as a truncated Fourier series. Amplitudes fall off
                 with harmonic number, so the curve is band-limited: smooth by
                 construction, never kinked, and the number of lobes is exactly
                 the harmonics you keep.

  superformula   Gielis' formula, the one that yields petals, shells and
                 rounded polygons from four exponents. Used for the shapes that
                 need obvious symmetry against the looser Fourier ones.

Fills are flat, and texture -- where a shape has it -- is a real dot lattice
clipped to the outline, not a bitmap overlay.
"""
from __future__ import annotations

import numpy as np


def fourier_blob(rng, lobes=(2, 5), rough=0.30, n=720):
    """Closed curve r(theta) = 1 + sum a_k cos(k theta + phi_k).

    Amplitudes decay as 1/k so high harmonics cannot spike the outline; the
    result is organic but never self-intersects at these amplitudes.
    """
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = np.ones_like(th)
    kmin, kmax = lobes
    for k in range(kmin, kmax + 1):
        r += rough * rng.uniform(0.4, 1.0) / k * np.cos(k * th + rng.uniform(0, 2 * np.pi))
    r = np.clip(r, 0.25, None)
    return np.column_stack([r * np.cos(th), r * np.sin(th)])


def superformula(m=6, n1=0.3, n2=0.3, n3=0.3, a=1.0, b=1.0, n=720):
    """Gielis superformula -- petals, shells and rounded polygons."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    t1 = np.abs(np.cos(m * th / 4) / a) ** n2
    t2 = np.abs(np.sin(m * th / 4) / b) ** n3
    r = (t1 + t2) ** (-1.0 / n1)
    r = r / r.max()
    return np.column_stack([r * np.cos(th), r * np.sin(th)])


def place(pts, cx, cy, scale, angle=0.0, squash=1.0):
    """Scale, squash on one axis, rotate, then move into position."""
    p = pts * np.array([scale, scale * squash])
    c, s = np.cos(angle), np.sin(angle)
    return np.column_stack([p[:, 0] * c - p[:, 1] * s + cx,
                            p[:, 0] * s + p[:, 1] * c + cy])


def dots_in(poly, view, step, stagger=True):
    """Staggered dot lattice, kept only where it is inside poly AND in view.

    Filtered numerically rather than by handing matplotlib a clip path: on a
    scatter, set_clip_path replaces the axes clip instead of intersecting with
    it, and set_clip_box did not restore it -- dots from shapes overhanging the
    plate edge drew out into the figure margin. Path.contains_points settles it
    before anything is drawn.
    """
    from matplotlib.path import Path as MPath

    x0, y0, x1, y1 = view
    px0, py0 = max(poly[:, 0].min(), x0), max(poly[:, 1].min(), y0)
    px1, py1 = min(poly[:, 0].max(), x1), min(poly[:, 1].max(), y1)
    if px1 <= px0 or py1 <= py0:
        return np.empty((0, 2))
    xs, ys, out = np.arange(px0, px1 + step, step), np.arange(py0, py1 + step, step), []
    for i, y in enumerate(ys):
        off = (step / 2) if (stagger and i % 2) else 0.0
        for x in xs:
            out.append((x + off, y))
    pts = np.array(out)
    if not len(pts):
        return pts
    inside = MPath(poly).contains_points(pts)
    pts = pts[inside]
    keep = (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1)
    return pts[keep]
