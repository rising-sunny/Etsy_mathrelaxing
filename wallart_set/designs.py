"""
designs.py — six original generative-math designs for the "Quiet Mathematics"
printable wall-art set. Each design is drawn from a mathematical expression NOT
used elsewhere in the shop's renderer:

  maurer      Maurer rose         — a rose curve walked in straight steps
  phyllotaxis Vogel spiral        — sunflower seeds at the golden angle
  hilbert     Hilbert curve       — a single line that fills the plane
  cardioid    Times-table circle  — modular chords whose envelope is a cardioid
  euler       Euler spiral        — the clothoid (Fresnel integrals)
  fern        Barnsley fern       — an iterated function system (botanical)

Every design is DETERMINISTIC (fixed params + fixed RNG seed) so the delivered
print is identical to the preview. Each draw fn returns the point cloud used to
frame the composition per aspect ratio.

Palette: warm cream ground, muted earth-tone line work (2026 Japandi/boho).
"""
import math
import numpy as np

BG = "#f2ebdd"
COL = {
    "terracotta": "#b5715a",
    "sage":       "#7f9070",
    "gold":       "#c2a05f",
    "charcoal":   "#4a463f",
    "clay":       "#a9765c",
}


def d_maurer(ax, lw_scale=1.0):
    n, d = 6, 71
    k = np.arange(0, 361)
    th = np.radians(k * d)
    r = np.sin(n * th)
    x, y = r * np.cos(th), r * np.sin(th)
    ax.plot(x, y, lw=0.5 * lw_scale, color=COL["terracotta"], alpha=0.75)
    th2 = np.radians(np.arange(0, 361))
    r2 = np.sin(n * th2)
    ax.plot(r2 * np.cos(th2), r2 * np.sin(th2), lw=1.1 * lw_scale,
            color=COL["terracotta"], alpha=0.5)
    return x, y


def d_phyllotaxis(ax, lw_scale=1.0):
    N = 1500
    k = np.arange(1, N)
    a = k * np.radians(137.507)
    r = np.sqrt(k)
    x, y = r * np.cos(a), r * np.sin(a)
    ax.scatter(x, y, s=((k / N) * 7 + 1) * lw_scale ** 2, color=COL["gold"],
               alpha=0.85, linewidths=0)
    return x, y


def d_hilbert(ax, lw_scale=1.0):
    order = 6
    n = 2 ** order
    pts = []
    for dd in range(n * n):
        x = y = 0
        t = dd
        s = 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1:
                    x = s - 1 - x
                    y = s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        pts.append((x, y))
    p = np.array(pts, dtype=float)
    ax.plot(p[:, 0], p[:, 1], lw=1.0 * lw_scale, color=COL["charcoal"],
            alpha=0.9, solid_capstyle="round")
    return p[:, 0], p[:, 1]


def d_cardioid(ax, lw_scale=1.0):
    from matplotlib.collections import LineCollection
    N, m = 240, 2
    th = np.linspace(0, 2 * np.pi, N, endpoint=False)
    px, py = np.cos(th), np.sin(th)
    segs = [[(px[i], py[i]), (px[(i * m) % N], py[(i * m) % N])] for i in range(N)]
    ax.add_collection(LineCollection(segs, colors=COL["clay"],
                                     linewidths=0.4 * lw_scale, alpha=0.4))
    return px, py


def d_euler(ax, lw_scale=1.0):
    t = np.linspace(-4.5, 4.5, 4000)
    dt = t[1] - t[0]
    x = np.cumsum(np.cos(t * t)) * dt
    y = np.cumsum(np.sin(t * t)) * dt
    x -= x.mean()
    y -= y.mean()
    ax.plot(x, y, lw=1.2 * lw_scale, color=COL["charcoal"], alpha=0.9,
            solid_capstyle="round")
    return x, y


def d_fern(ax, lw_scale=1.0):
    rng = np.random.default_rng(7)   # fixed seed -> reproducible
    N = 90000
    x = y = 0.0
    xs = np.empty(N)
    ys = np.empty(N)
    rs = rng.random(N)
    for i in range(N):
        r = rs[i]
        if r < 0.01:
            x, y = 0.0, 0.16 * y
        elif r < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            x, y = 0.20 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        xs[i] = x
        ys[i] = y
    ax.scatter(xs, ys, s=0.11 * lw_scale ** 2, color=COL["sage"], alpha=0.7,
               linewidths=0)
    return xs, ys


DESIGNS = {
    "maurer":      {"fn": d_maurer,      "title": "Maurer Rose",        "pad": 1.18},
    "phyllotaxis": {"fn": d_phyllotaxis, "title": "Golden Spiral",      "pad": 1.16},
    "hilbert":     {"fn": d_hilbert,     "title": "Hilbert Curve",      "pad": 1.14},
    "cardioid":    {"fn": d_cardioid,    "title": "Cardioid Weave",     "pad": 1.18},
    "euler":       {"fn": d_euler,       "title": "Euler Spiral",       "pad": 1.30},
    "fern":        {"fn": d_fern,        "title": "Barnsley Fern",      "pad": 1.12},
}

# aspect ratios (portrait) -> (w, h) in ratio units
RATIOS = {
    "2x3":  (2, 3),
    "3x4":  (3, 4),
    "4x5":  (4, 5),
    "5x7":  (5, 7),
    "ISO":  (1, math.sqrt(2)),
}
