"""
spiral_engine.py — spiral tilings by near-congruent tiles.

Not the exponential conformal map the shop's coloring book uses. That one sends
a grid through exp(), so tiles grow without bound outward and pile into a
singularity at the centre. Here every tile stays the same size across the whole
plate, which is what makes it read as a tiling rather than a vortex.

The construction:

  Rings of constant radial thickness h. Ring k holds N_k tiles, chosen so that
  arc length per tile stays constant -- so N_k grows with radius.

  The ring boundaries carry a zigzag whose pitch is constant in ARC LENGTH, not
  in angle. That is the load-bearing detail: it makes the outer boundary of ring
  k the identical curve to the inner boundary of ring k+1, so the rings interlock
  even though they are cut into different numbers of pieces.

  Those extra tiles per ring are what produce the spiral arms. The offset
  accumulates modulo the ring's tile count, and the arms are where it wraps.

Three earlier attempts are worth recording as dead ends: putting the zigzag on
the radial edges gave tiny teeth that read as texture; making tiles span many
teeth hid the cuts and left plain stripes; and giving a tile one smooth edge and
one toothed edge is not a tiling at all -- the teeth invade the neighbouring
band instead of meshing, because a shared border has to be the same curve from
both sides.
"""
from __future__ import annotations

import numpy as np


def teeth_count(r, pitch):
    """Whole number of teeth around a ring of radius r.

    Must be an integer or the zigzag does not close on itself: 2*pi*r/pitch is
    generally fractional, which left a visible pale seam radiating from the
    centre where the last tile of a ring failed to meet the first. Rounding is
    safe for the interlock because both sides of a shared border are computed
    from the same radius, so they still round to the same count.
    """
    return max(3, round(2 * np.pi * r / pitch))


def boundary(r, th, pitch, amp):
    """Effective radius of a ring border: triangle wave, whole teeth per turn."""
    s = th * teeth_count(r, pitch) / (2 * np.pi)
    return r + amp * (1 - 4 * np.abs((s % 1.0) - 0.5))


def _tile(rk, h, a, b, pitch, amp, n=120):
    ti = np.linspace(a, b, n)
    to = np.linspace(b, a, n)
    R = np.concatenate([boundary(rk, ti, pitch, amp),
                        boundary(rk + h, to, pitch, amp)])
    T = np.concatenate([ti, to])
    return np.column_stack([R * np.cos(T), R * np.sin(T)])


def build(r0=0.55, h=0.34, rings=34, pitch=0.36, amp=0.14, per_tile=2,
          twist=0.5, n=120):
    """Returns a list of dicts: poly, ring k, index j, ring count N, centroid."""
    out = []
    for k in range(rings):
        rk = r0 + k * h
        N = max(3, round(2 * np.pi * rk / (per_tile * pitch)))
        th0 = twist * k * (2 * np.pi / N)
        for j in range(N):
            a = th0 + 2 * np.pi * j / N
            b = th0 + 2 * np.pi * (j + 1) / N
            poly = _tile(rk, h, a, b, pitch, amp, n)
            out.append({"poly": poly, "k": k, "j": j, "N": N,
                        "r": rk + h / 2, "th": (a + b) / 2})
    return out


# ── Colour ───────────────────────────────────────────────────────────────────
def arm_index(t, arms, pitch_log=0.0):
    """Which spiral arm a tile falls in.

    Colouring by (k, j) directly would follow the rings, which is the one
    structure already obvious from the outlines. Quantising angle plus a
    multiple of log(r) instead follows a logarithmic spiral, so the colour
    reveals the arms the modular offset creates rather than restating the rings.
    """
    ang = t["th"] + pitch_log * np.log(t["r"])
    return int(np.floor(arms * ang / (2 * np.pi))) % arms


def ring_mod(t, m):
    """Plain ring index modulo m -- concentric colour banding."""
    return t["k"] % m
