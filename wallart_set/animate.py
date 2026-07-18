"""
animate.py — a short listing video (Etsy) where each design in the active
collection draws itself, then a closing "set of 6" card. Square 1080x1080,
~12s, H.264 MP4. Collection-generic via WALLART_MODULE / WALLART_PALETTE.

    WALLART_MODULE=designs_geo WALLART_PALETTE=mono python animate.py
"""
import os
import shutil
import subprocess
import tempfile
import importlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib import font_manager

designs = importlib.import_module(os.environ.get("WALLART_MODULE", "designs"))
PAL = os.environ.get("WALLART_PALETTE", "earth")
designs.use_palette(PAL)

SERIF = font_manager.FontProperties(family="DejaVu Serif")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "out", designs.COLLECTION, PAL, "video")
os.makedirs(OUTDIR, exist_ok=True)

PX = 1080
FPS = 24
DRAW, HOLD = 30, 14
CLOSE = 40
ORDER = designs.ORDER
TITLES = {n: designs.DESIGNS[n]["title"] for n in ORDER}


def smooth(t):
    return t * t * (3 - 2 * t)


def window(xs, ys, pad):
    cx, cy = (xs.min()+xs.max())/2, (ys.min()+ys.max())/2
    h = max((xs.max()-xs.min())/2, (ys.max()-ys.min())/2, 1e-6) * pad
    return cx - h, cx + h, cy - h, cy + h


def new_ax(fig):
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(designs.BG); ax.axis("off")
    ax.set_aspect("equal")
    return ax


def draw(ax, kind, items, style, col, reveal):
    if kind == "poly":
        X, Y = items; k = max(2, int(reveal * len(X)))
        ax.plot(X[:k], Y[:k], lw=style, color=col, alpha=0.9, solid_capstyle="round")
        if reveal < 1:
            ax.plot([X[k-1]], [Y[k-1]], "o", ms=3.2, color=col, alpha=0.9)
    elif kind == "scatter":
        X, Y, S = items; k = max(2, int(reveal * len(X)))
        s = S[:k] if not np.isscalar(S) else S
        ax.scatter(X[:k], Y[:k], s=s, color=col, alpha=0.82, linewidths=0)
    elif kind == "segs":
        k = max(1, int(reveal * len(items)))
        ax.add_collection(LineCollection(items[:k], colors=col, linewidths=style, alpha=0.9))
    elif kind == "circles":
        k = max(1, int(reveal * len(items)))
        for cx, cy, r in items[:k]:
            ax.add_patch(mpatches.Circle((cx, cy), r, fill=False, edgecolor=col,
                                         lw=style, alpha=0.9))


def render_frames(tmp):
    idx = 0
    for name in ORDER:
        kind, xs, ys, items, style = designs.anim_data(name)
        col = designs.color(name)
        x0, x1, y0, y1 = window(np.asarray(xs), np.asarray(ys), designs.DESIGNS[name]["pad"] * 1.05)
        for f in range(DRAW + HOLD):
            reveal = smooth(min(1.0, (f + 1) / DRAW)) if f < DRAW else 1.0
            fig = plt.figure(figsize=(PX/100, PX/100), dpi=100)
            fig.patch.set_facecolor(designs.BG); ax = new_ax(fig)
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
            draw(ax, kind, items, style, col, reveal)
            la = 0.0 if f < DRAW else min(1.0, (f - DRAW) / 6)
            ax.text(0.5, 0.075, TITLES[name], transform=ax.transAxes, ha="center",
                    fontproperties=SERIF, fontsize=21, color="#3a3733", alpha=la)
            fig.savefig(os.path.join(tmp, f"{idx:04d}.png"), facecolor=designs.BG)
            plt.close(fig); idx += 1
        print(f"  {name} frames done")
    close = closing_frame()
    for _ in range(CLOSE):
        close.savefig(os.path.join(tmp, f"{idx:04d}.png"), facecolor=designs.BG); idx += 1
    plt.close(close)
    return idx


def closing_frame():
    fig = plt.figure(figsize=(PX/100, PX/100), dpi=100)
    fig.patch.set_facecolor(designs.BG)
    fig.text(0.5, 0.93, designs.SET_NAME, ha="center", fontproperties=SERIF,
             fontsize=30, color="#3a3733")
    fig.text(0.5, 0.885, designs.SET_TAGLINE, ha="center", fontproperties=SERIF,
             fontsize=13.5, color="#6b6458")
    for i, name in enumerate(ORDER):
        kind, xs, ys, items, style = designs.anim_data(name)
        col = designs.color(name)
        ax = fig.add_subplot(2, 3, i + 1)
        ax.set_facecolor(designs.BG); ax.axis("off"); ax.set_aspect("equal")
        x0, x1, y0, y1 = window(np.asarray(xs), np.asarray(ys), designs.DESIGNS[name]["pad"] * 1.05)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        draw(ax, kind, items, style * 0.7 if style else style, col, 1.0)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.83, bottom=0.05, wspace=0.1, hspace=0.12)
    return fig


def main():
    tmp = tempfile.mkdtemp(prefix="qmvid_")
    try:
        n = render_frames(tmp)
        out = os.path.join(OUTDIR, f"{designs.SLUG.lower()}_{PAL}.mp4")
        subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(tmp, "%04d.png"), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                       check=True, capture_output=True)
        print(f"\nVIDEO [{designs.COLLECTION}/{PAL}] {n} frames, {n/FPS:.1f}s, "
              f"{os.path.getsize(out)/1e6:.1f} MB -> {out}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
