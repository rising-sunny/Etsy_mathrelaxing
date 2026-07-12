"""
animate.py — a short listing video (Etsy) where each of the six designs draws
itself, then a closing "set of 6" card. Square 1080x1080, ~12s, H.264 MP4.

    WALLART_PALETTE=mono python animate.py     # default: earth
"""
import os
import math
import shutil
import subprocess
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import font_manager

import designs
from designs import DESIGNS

PAL = os.environ.get("WALLART_PALETTE", "earth")
designs.use_palette(PAL)
C = designs.PALETTES[PAL]
BG = C["bg"]
SERIF = font_manager.FontProperties(family="DejaVu Serif")

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "out", PAL, "video")
os.makedirs(OUTDIR, exist_ok=True)

PX = 1080
FPS = 24
DRAW, HOLD = 30, 14       # frames per design
CLOSE = 40                # closing card frames
LWS = 1.9                 # line/point weight scale for 1080px

TITLES = {n: DESIGNS[n]["title"] for n in DESIGNS}


# ---- design data (ordered elements, revealed progressively) -----------------
def data_maurer():
    k = np.arange(0, 361); th = np.radians(k * 71); r = np.sin(6 * th)
    return ("line", r * np.cos(th), r * np.sin(th), None)


def data_phyllotaxis():
    k = np.arange(1, 1500); a = k * np.radians(137.507); r = np.sqrt(k)
    s = ((k / 1500) * 7 + 1) * LWS ** 2
    return ("scatter", r * np.cos(a), r * np.sin(a), s)


def data_hilbert():
    n = 2 ** 6; pts = []
    for dd in range(n * n):
        x = y = 0; t = dd; s = 1
        while s < n:
            rx = 1 & (t // 2); ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1: x = s - 1 - x; y = s - 1 - y
                x, y = y, x
            x += s * rx; y += s * ry; t //= 4; s *= 2
        pts.append((x, y))
    p = np.array(pts, float)
    return ("line", p[:, 0], p[:, 1], None)


def data_cardioid():
    N = 240; th = np.linspace(0, 2 * np.pi, N, endpoint=False)
    px, py = np.cos(th), np.sin(th)
    segs = [[(px[i], py[i]), (px[(i * 2) % N], py[(i * 2) % N])] for i in range(N)]
    return ("segs", px, py, segs)


def data_euler():
    t = np.linspace(-4.5, 4.5, 4000); dt = t[1] - t[0]
    x = np.cumsum(np.cos(t * t)) * dt; y = np.cumsum(np.sin(t * t)) * dt
    return ("line", x - x.mean(), y - y.mean(), None)


def data_fern():
    rng = np.random.default_rng(7); N = 26000
    x = y = 0.0; xs = np.empty(N); ys = np.empty(N); rs = rng.random(N)
    for i in range(N):
        r = rs[i]
        if r < 0.01: x, y = 0.0, 0.16 * y
        elif r < 0.86: x, y = 0.85*x+0.04*y, -0.04*x+0.85*y+1.6
        elif r < 0.93: x, y = 0.20*x-0.26*y, 0.23*x+0.22*y+1.6
        else: x, y = -0.15*x+0.28*y, 0.26*x+0.24*y+0.44
        xs[i] = x; ys[i] = y
    return ("scatter", xs, ys, 0.12 * LWS ** 2)


DATA = {"maurer": data_maurer, "phyllotaxis": data_phyllotaxis, "hilbert": data_hilbert,
        "cardioid": data_cardioid, "euler": data_euler, "fern": data_fern}
ORDER = ["maurer", "phyllotaxis", "hilbert", "cardioid", "euler", "fern"]


def smooth(t):
    return t * t * (3 - 2 * t)


def window(xs, ys, pad):
    cx, cy = (xs.min()+xs.max())/2, (ys.min()+ys.max())/2
    h = max((xs.max()-xs.min())/2, (ys.max()-ys.min())/2, 1e-6) * pad
    return cx - h, cx + h, cy - h, cy + h


def new_ax(fig):
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    ax.set_aspect("equal")
    return ax


def render_frames(tmp):
    idx = 0
    for name in ORDER:
        kind, xs, ys, extra = DATA[name]()
        col = C[name]
        x0, x1, y0, y1 = window(xs, ys, DESIGNS[name]["pad"] * 1.05)
        M = len(xs)
        for f in range(DRAW + HOLD):
            frac = smooth(min(1.0, (f + 1) / DRAW)) if f < DRAW else 1.0
            k = max(2, int(frac * M))
            fig = plt.figure(figsize=(PX/100, PX/100), dpi=100)
            fig.patch.set_facecolor(BG); ax = new_ax(fig)
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
            if kind == "line":
                ax.plot(xs[:k], ys[:k], lw=1.0*LWS, color=col, alpha=0.9,
                        solid_capstyle="round")
                if f < DRAW:  # bright tip while drawing
                    ax.plot([xs[k-1]], [ys[k-1]], "o", ms=3.2, color=col, alpha=0.9)
            elif kind == "scatter":
                ax.scatter(xs[:k], ys[:k], s=extra if np.isscalar(extra) else extra[:k],
                           color=col, alpha=0.82, linewidths=0)
            else:  # segs
                ks = max(2, int(frac * len(extra)))
                ax.add_collection(LineCollection(extra[:ks], colors=col,
                                                 linewidths=0.5*LWS, alpha=0.42))
            # label fades in during hold
            la = 0.0 if f < DRAW else min(1.0, (f - DRAW) / 6)
            ax.text(0.5, 0.075, TITLES[name], transform=ax.transAxes, ha="center",
                    fontproperties=SERIF, fontsize=21, color="#3a3733", alpha=la)
            fig.savefig(os.path.join(tmp, f"{idx:04d}.png"), facecolor=BG)
            plt.close(fig); idx += 1
        print(f"  {name} frames done")
    # closing card: 2x3 of masters + title
    close = closing_frame()
    for _ in range(CLOSE):
        close.savefig(os.path.join(tmp, f"{idx:04d}.png"), facecolor=BG)
        idx += 1
    plt.close(close)
    return idx


def closing_frame():
    fig = plt.figure(figsize=(PX/100, PX/100), dpi=100)
    fig.patch.set_facecolor(BG)
    fig.text(0.5, 0.93, "Quiet Mathematics", ha="center", fontproperties=SERIF,
             fontsize=30, color="#3a3733")
    fig.text(0.5, 0.885, "Set of 6 printable wall art · drawn from real equations",
             ha="center", fontproperties=SERIF, fontsize=13.5, color="#6b6458")
    for i, name in enumerate(ORDER):
        kind, xs, ys, extra = DATA[name]()
        col = C[name]
        ax = fig.add_subplot(2, 3, i + 1)
        ax.set_facecolor(BG); ax.axis("off"); ax.set_aspect("equal")
        x0, x1, y0, y1 = window(xs, ys, DESIGNS[name]["pad"] * 1.05)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        if kind == "line":
            ax.plot(xs, ys, lw=0.8, color=col, alpha=0.9, solid_capstyle="round")
        elif kind == "scatter":
            ax.scatter(xs, ys, s=(extra if np.isscalar(extra) else extra)*0.4,
                       color=col, alpha=0.82, linewidths=0)
        else:
            ax.add_collection(LineCollection(extra, colors=col, linewidths=0.35, alpha=0.4))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.83, bottom=0.05, wspace=0.1, hspace=0.12)
    return fig


def main():
    tmp = tempfile.mkdtemp(prefix="qmvid_")
    try:
        n = render_frames(tmp)
        out = os.path.join(OUTDIR, f"quiet_mathematics_{PAL}.mp4")
        cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i",
               os.path.join(tmp, "%04d.png"), "-c:v", "libx264",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True, capture_output=True)
        dur = n / FPS
        print(f"\nVIDEO [{PAL}] {n} frames, {dur:.1f}s, {os.path.getsize(out)/1e6:.1f} MB -> {out}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
