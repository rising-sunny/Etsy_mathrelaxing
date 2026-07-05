"""
build_celtic_ipad_video.py — promo MP4 for the Celtic Knot iPad bundle.
A woven knot on a white "canvas" fills with colour from the centre outward
(the Procreate ColorDrop feeling), on the branded navy background.
1080x1080, 30 fps, ~8 s, h264 — matches the other MathRelaxing iPad promos.
"""

import os
import math
import random
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

import brand
import generate_celtic_knots as gk

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "ipad_celtic")
FRAMES = os.path.join(OUT, "_frames")
NAVY = brand.IPAD_NAVY
GOLD = brand.IPAD_GOLD
CREAM = brand.CREAM
TEAL = brand.IPAD_TEAL
CELTIC_FILLS = ["#2e6b4f", "#3f8f6b", "#2f7d7b", "#c9a24b", "#b9762f",
                "#9c3b2e", "#6b4a8a", "#31597f"]

S = 10.8                       # figure size in inches -> 1080 px @100 dpi
ROWS = COLS = 10
SEED = 1210
CARD = (1.35, 1.75, 8.1, 8.1)  # x,y,w,h of the white canvas


def build_tiles():
    """Return list of tile dicts (rect, type, fill) plus reveal order key."""
    cx0, cy0, w, h = CARD
    margin = 0.55
    x0, y0 = cx0 + margin, cy0 + margin
    gw, gh = w - 2 * margin, h - 2 * margin
    cell = min(gw / COLS, gh / ROWS)
    ox = x0 + (gw - cell * COLS) / 2
    oy = y0 + (gh - cell * ROWS) / 2
    ccx, ccy = ox + cell * COLS / 2, oy + cell * ROWS / 2

    base = {}
    tiles = []
    for i in range(ROWS):
        for j in range(COLS):
            ci, cj = min(i, ROWS - 1 - i), min(j, COLS - 1 - j)
            if (ci, cj) not in base:
                base[(ci, cj)] = (
                    gk._pick_tile(random.Random(SEED + ci * 131 + cj * 17), 0.42),
                    CELTIC_FILLS[(ci * 3 + cj * 5) % len(CELTIC_FILLS)])
            t, fill = base[(ci, cj)]
            if (i != ci) ^ (j != cj):
                t = gk._MIRROR[t]
            cxL, cxR = ox + j * cell, ox + (j + 1) * cell
            cyB, cyT = oy + i * cell, oy + (i + 1) * cell
            mx, my = (cxL + cxR) / 2, (cyB + cyT) / 2
            tiles.append({"t": t, "fill": fill, "rect": (cxL, cxR, cyB, cyT),
                          "ij": (i, j), "d": math.hypot(mx - ccx, my - ccy)})
    tiles.sort(key=lambda d: (d["d"], d["ij"]))
    return tiles, cell


def draw_fill(ax, tile, cell, flw):
    cxL, cxR, cyB, cyT = tile["rect"]
    i, j = tile["ij"]
    t, fill = tile["t"], tile["fill"]
    band = cell * gk.BAND_RATIO
    R = cell / 2
    if t == 0:
        gk._add_arc(ax, (cxL, cyT), cell, cell, 0, 270, 360, flw, fill, zorder=1)
        gk._add_arc(ax, (cxR, cyB), cell, cell, 0, 90, 180, flw, fill, zorder=1)
    elif t == 1:
        gk._add_arc(ax, (cxR, cyT), cell, cell, 0, 180, 270, flw, fill, zorder=1)
        gk._add_arc(ax, (cxL, cyB), cell, cell, 0, 0, 90, flw, fill, zorder=1)
    else:
        mx, my = (cxL + cxR) / 2, (cyB + cyT) / 2
        brk = band + cell * 0.11
        if (i + j) % 2 == 0:
            gk._add_line(ax, (mx, cyB), (mx, cyT), flw, fill, zorder=1)
            gk._add_line(ax, (cxL, my), (mx - brk, my), flw, fill, zorder=1)
            gk._add_line(ax, (mx + brk, my), (cxR, my), flw, fill, zorder=1)
        else:
            gk._add_line(ax, (cxL, my), (cxR, my), flw, fill, zorder=1)
            gk._add_line(ax, (mx, cyB), (mx, my - brk), flw, fill, zorder=1)
            gk._add_line(ax, (mx, my + brk), (mx, cyT), flw, fill, zorder=1)


def setup_ax():
    fig = plt.figure(figsize=(S, S), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, S); ax.set_ylim(0, S); ax.set_aspect("equal")
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.text(S / 2, S - 0.62, "Celtic Knot  ·  iPad Edition", ha="center",
            fontsize=21, family="serif", color=CREAM, zorder=6)
    cx0, cy0, w, h = CARD
    ax.add_patch(FancyBboxPatch((cx0, cy0), w, h,
                 boxstyle="round,pad=0,rounding_size=0.18", facecolor="white",
                 edgecolor="#3a3f52", lw=1.5, zorder=0.2))
    ax.text(S / 2, 1.12, "GoodNotes  ·  Notability  ·  Procreate", ha="center",
            fontsize=14, color=TEAL, zorder=6)
    logo = mpimg.imread(gk.LOGO_PATH)
    lw = 1.5; lh = lw * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(S / 2 - lw / 2, S / 2 + lw / 2, 0.28, 0.28 + lh), zorder=6)
    return fig, ax


def main():
    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES)

    tiles, cell = build_tiles()
    flw = 1.85 * cell * gk.BAND_RATIO * 72.0

    fig, ax = setup_ax()
    # all black outlines drawn once, always on top
    for tl in tiles:
        cxL, cxR, cyB, cyT = tl["rect"]
        gk._emit_tile(ax, tl["t"], cxL, cxR, cyB, cyT, tl["ij"][0], tl["ij"][1],
                      1.5, "black", zorder=3)

    n = len(tiles)
    hold_start, reveal_frames, hold_end = 12, 168, 45
    revealed = 0
    frame = 0

    def save():
        nonlocal frame
        fig.savefig(os.path.join(FRAMES, f"f_{frame:04d}.png"),
                    facecolor=NAVY, dpi=100)
        frame += 1

    for _ in range(hold_start):     # line-art hold
        save()
    for k in range(reveal_frames):  # bloom fill outward
        target = round((k + 1) / reveal_frames * n)
        while revealed < target:
            draw_fill(ax, tiles[revealed], cell, flw)
            revealed += 1
        save()
    while revealed < n:
        draw_fill(ax, tiles[revealed], cell, flw); revealed += 1
    for _ in range(hold_end):       # coloured hold
        save()
    plt.close(fig)
    print(f"{frame} frames renderizados")

    out = os.path.join(OUT, "CelticKnot_iPad_promo.mp4")
    brand.encode_mp4(FRAMES, out, fps=30, pattern="f_%04d.png", crf=20)
    print("Video listo:", out)


if __name__ == "__main__":
    main()
