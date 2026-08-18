"""
designs.py — the six plates of the Spiral Tilings wall-art set.

Each plate varies geometry as well as palette, so the set reads as six designs
rather than one design in six colourways. The colour index is always a modular
function of a tile's position -- the same arithmetic that produces the spiral
arms -- so the colour reveals the structure instead of being painted over it.
"""
from __future__ import annotations

import spiral_engine as E

PALETTES = {
    "teal_rust":  ["#0f2e3d", "#1b5566", "#3d8b93", "#7fbfb4", "#e2cf9a", "#c96f45"],
    "indigo":     ["#151a35", "#2b3566", "#4a5a9c", "#8792c4", "#c8cbe0", "#d98f5f"],
    "terracotta": ["#3b1f16", "#7a3b22", "#b45f34", "#d99364", "#eec9a3", "#5d7a6b"],
    "forest":     ["#12251c", "#22402c", "#3d6647", "#6d9169", "#b9c9a0", "#d8a44e"],
    "plum":       ["#1d1024", "#4a2a55", "#8a4f86", "#c185b4", "#f0dced", "#d9a24e"],
    "ink":        ["#0d0d0d", "#2f2f2f", "#5c5c5c", "#8f8f8f", "#c4c2bc", "#f4f2ec"],
}


# name, slug, geometry, colour scheme, palette, centre offset in view units.
# "centre" moves the spiral eye off the plate for the two compositions that read
# better as an all-over field than as a rosette.
DESIGNS = [
    dict(slug="vortex",   title="Vortex",
         geo=dict(per_tile=2, amp=0.14, pitch=0.36, h=0.34),
         scheme=("arm", 6, 3.0),  pal="teal_rust",  centre=(0, 0),    vh=5.6),
    dict(slug="helix",    title="Helix",
         geo=dict(per_tile=2, amp=0.16, pitch=0.34, h=0.32),
         scheme=("arm", 8, 6.0),  pal="indigo",     centre=(0, 0),    vh=5.2),
    dict(slug="radiant",  title="Radiant",
         geo=dict(per_tile=3, amp=0.12, pitch=0.30, h=0.34),
         scheme=("jk", 6, 0),     pal="terracotta", centre=(0, 0),    vh=5.4),
    dict(slug="corona",   title="Corona",
         geo=dict(per_tile=2, amp=0.14, pitch=0.38, h=0.36),
         scheme=("ring", 6, 0),   pal="forest",     centre=(0, 0),    vh=5.8),
    dict(slug="drift",    title="Drift",
         geo=dict(per_tile=3, amp=0.15, pitch=0.34, h=0.34),
         scheme=("arm", 6, 8.0),  pal="plum",       centre=(4.2, 0),  vh=3.2),
    dict(slug="pinwheel", title="Pinwheel",
         geo=dict(per_tile=2, amp=0.13, pitch=0.36, h=0.34),
         scheme=("arm", 7, 2.2),  pal="ink",        centre=(0, 0),    vh=5.0),
]


# arm_index reduces modulo `arms`, so an arms count below the palette length
# silently drops the tail colours -- vortex lost its rust accent and drift never
# showed its two lightest plums. Keep arms a multiple of the palette length.
def colour_index(t, scheme):
    kind, a, b = scheme
    if kind == "arm":
        return E.arm_index(t, a, b)
    if kind == "ring":
        return E.ring_mod(t, a)
    return (t["j"] + t["k"]) % a


def render(design, w_in, h_in, dpi=300, n=120):
    """One plate, full bleed, no text -- the tiling is the whole picture."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    pal = PALETTES[design["pal"]]
    cx, cy = design["centre"]
    vh = design["vh"]
    vw = vh * (w_in / h_in)
    # Rings must reach the far corner of the view, measured from the spiral
    # centre, or the plate shows bare paper where the tiling runs out.
    reach = max(np.hypot(cx + sx * vw, cy + sy * vh)
                for sx in (-1, 1) for sy in (-1, 1))
    g = design["geo"]
    rings = int(np.ceil((reach * 1.04) / g["h"])) + 2

    tiles = E.build(r0=0.5, rings=rings, n=n, **g)
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(cx - vw, cx + vw)
    ax.set_ylim(cy - vh, cy + vh)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(pal[0])
    ax.set_facecolor(pal[0])
    lw = max(0.15, 0.45 * (w_in / 12.0))
    for t in tiles:
        ax.fill(t["poly"][:, 0], t["poly"][:, 1],
                facecolor=pal[colour_index(t, design["scheme"]) % len(pal)],
                edgecolor=pal[0], lw=lw)
    return fig
