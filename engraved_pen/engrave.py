"""
engrave.py — artwork for the brass ballpoint pen (Printify blueprint 10608).

The engraving window is a single 2400 x 300 px strip, position "right", and the
decoration method is a fiber laser. That combination sets hard rules:

  * one tone only. Printify engraves EVERY non-transparent pixel, whatever its
    colour, and skips only transparency -- so the file is solid black on a
    transparent ground. No grey, no gradients, no halftone. Anything of ours
    that relies on tonal fill (Turing fields, the organic plates, the coloured
    spiral tilings) cannot survive here at all.
  * 8:1. A band eight times wider than it is tall wants a line of type, not a
    picture.
  * minimums: 0.2 mm line, 1.5 mm text height. Taking the engraved band as
    roughly 2 in long, one pixel here is about 0.021 mm, which puts the floor
    near 10 px of stroke and 71 px of cap height. Everything below is drawn
    well clear of that -- strokes >= 14 px, type >= 110 px -- because the band
    length is an estimate and the cost of being wrong is an illegible pen.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

W, H = 2400, 300
DPI = 300
MIN_STROKE_PX = 14      # ~0.3 mm, comfortably over the 0.2 mm floor
MIN_TEXT_PX = 110       # ~2.3 mm, comfortably over the 1.5 mm floor


def canvas():
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


def px_to_pt(px):
    return px * 72.0 / DPI


def sine(ax, x0, x1, y, amp, cycles=2.5, lw_px=MIN_STROKE_PX):
    t = np.linspace(0, 1, 400)
    ax.plot(x0 + (x1 - x0) * t, y + amp * np.sin(2 * np.pi * cycles * t),
            color="black", lw=px_to_pt(lw_px), solid_capstyle="round")


def golden_spiral(ax, cx, cy, r, turns=1.1, lw_px=MIN_STROKE_PX):
    """NOT recommended on the pen -- kept for larger engraving areas.

    A golden spiral loses radius as phi to the power -4t/pi, so by 2.4 turns it
    is at 1.4% of its starting radius. Cutting back to just over one turn holds
    the tail near a tenth of the outer radius, but on a 300 px band even that
    still reads as a curl rather than a spiral once rendered. The sine wave and
    the unit-circle glyph survive this size; this one does not."""
    phi = (1 + 5 ** 0.5) / 2
    t = np.linspace(0, turns * 2 * np.pi, 500)
    rr = r * phi ** (-t / (np.pi / 2))
    ax.plot(cx + rr * np.cos(t), cy + rr * np.sin(t),
            color="black", lw=px_to_pt(lw_px), solid_capstyle="round")


def circle_glyph(ax, cx, cy, r, lw_px=MIN_STROKE_PX):
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(cx + r * np.cos(t), cy + r * np.sin(t), color="black", lw=px_to_pt(lw_px))
    ax.plot([cx - r * 1.25, cx + r * 1.25], [cy, cy], color="black", lw=px_to_pt(lw_px * 0.7))
    ax.plot([cx, cx], [cy - r * 1.25, cy + r * 1.25], color="black", lw=px_to_pt(lw_px * 0.7))
    ax.plot([cx, cx + r * np.cos(np.pi / 4)], [cy, cy + r * np.sin(np.pi / 4)],
            color="black", lw=px_to_pt(lw_px))


def rule(ax, x0, x1, y, lw_px=MIN_STROKE_PX * 0.8):
    ax.plot([x0, x1], [y, y], color="black", lw=px_to_pt(lw_px), solid_capstyle="butt")


def text(ax, x, y, s, size_px=MIN_TEXT_PX, ha="center", family="serif", weight="normal"):
    ax.text(x, y, s, ha=ha, va="center", color="black",
            fontsize=px_to_pt(size_px), family=family, weight=weight)


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # transparent=True is the whole point: only transparent pixels are skipped
    # by the laser, so the ground must carry no ink at all.
    fig.savefig(path, dpi=DPI, transparent=True)
    plt.close(fig)
    return path
