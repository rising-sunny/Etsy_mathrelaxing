"""
plate_library.py — 18 graphic renderers for "The Shape of an Idea" book.
Shares mini_book.py's page geometry, fonts and palette with math_gallery
(the sibling "Mathematics of Beauty" book) for a consistent visual family,
but every design here is its own: equations & concepts, not generative forms.

Style rule for this book (per feedback on the first pyvista draft): 3D
objects are rendered as dense nets of thin contour lines, never as solid
shaded surfaces -- consistent with the flat 2D pieces, which favour many
overlaid line-strokes over filled colour blocks.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, "..", "math_gallery")
sys.path.insert(0, MG)
import mini_book as MB  # noqa: E402

DARK, PAPER, CMAP, GOLD, ACC, INK, SUB = MB.DARK, MB.PAPER, MB.CMAP, MB.GOLD, MB.ACC, MB.INK, MB.SUB


def _grad_line(ax, x, y, cmap=CMAP, lw=1.0, alpha=0.9):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, linewidth=lw, alpha=alpha)
    lc.set_array(np.linspace(0, 1, len(segs)))
    ax.add_collection(lc)
    return lc


def _pv_page(png_name, bg):
    """Composite a cached pyvista PNG (transparent) onto a book page."""
    fig, ax = MB.fig_trim(bg)
    im = Image.open(os.path.join(HERE, png_name)).convert("RGBA")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    iw, ih = im.size
    # letterbox the render into a centred square region, preserving aspect
    box = 0.86
    aspect = ih / iw
    if aspect <= 1:
        w = box; h = box * aspect
    else:
        h = box; w = box / aspect
    ax.imshow(np.asarray(im), extent=((1 - w) / 2, (1 + w) / 2, (1 - h) / 2, (1 + h) / 2), zorder=2)
    return MB.to_pil(fig, bg)


# ── Foundations ────────────────────────────────────────────────────────────

def g_euler():
    fig, ax = MB.fig_trim(DARK)
    th = np.linspace(0, 2 * np.pi, 800)
    ax.plot(np.cos(th), np.sin(th), color="#3f3d38", lw=1.1)
    n = 60
    for k, ang in enumerate(np.linspace(0, 2 * np.pi, n, endpoint=False)):
        col = CMAP(k / n)
        ax.plot([0, np.cos(ang)], [0, np.sin(ang)], color=col, lw=0.55, alpha=0.5)
    ax.plot([-1, 0], [0, 0], color=GOLD, lw=2.4, solid_capstyle="round")
    ax.plot([-1], [0], "o", color=GOLD, ms=11)
    ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35); ax.set_aspect("equal")
    return MB.to_pil(fig, DARK)


def g_golden():
    fig, ax = MB.fig_trim(PAPER)
    phi = (1 + np.sqrt(5)) / 2
    # classic whirling-squares construction: repeatedly cut a square off a
    # phi x 1 rectangle, rotating which side you cut from
    x, y, w, h = -phi / 2, -0.5, phi, 1.0
    squares, arcs = [], []
    direction = 0
    for i in range(9):
        s = min(w, h)
        if direction == 0:      # cut from the left
            sq = (x, y, s, s); c = (x + s, y + s); th0, th1 = 180, 90
            x, w = x + s, w - s
        elif direction == 1:    # cut from the bottom
            sq = (x, y, s, s); c = (x, y + s); th0, th1 = 270, 180
            y, h = y + s, h - s
        elif direction == 2:    # cut from the right
            sq = (x + w - s, y, s, s); c = (x + w - s, y); th0, th1 = 0, -90
            w = w - s
        else:                    # cut from the top
            sq = (x, y + h - s, s, s); c = (x + s, y + h - s); th0, th1 = 90, 0
            h = h - s
        squares.append(sq); arcs.append((c[0], c[1], s, th0, th1))
        direction = (direction + 1) % 4

    for i, (sx, sy, sw, sh) in enumerate(squares):
        ax.add_patch(Rectangle((sx, sy), sw, sh, fill=False,
                                edgecolor=ACC, lw=0.8, alpha=0.45 + 0.5 * (i / len(squares))))
    xs, ys = [], []
    for cx, cy, r, th0, th1 in arcs:
        th = np.linspace(np.radians(th0), np.radians(th1), 60)
        xs.append(cx + r * np.cos(th)); ys.append(cy + r * np.sin(th))
    X, Y = np.concatenate(xs), np.concatenate(ys)
    _grad_line(ax, X, Y, lw=2.2)
    ax.set_xlim(-phi / 2 - 0.08, phi / 2 + 0.08); ax.set_ylim(-0.58, 0.58)
    ax.set_aspect("equal")
    return MB.to_pil(fig, PAPER)


def g_pythagoras():
    fig, ax = MB.fig_trim(PAPER)
    a, b = 1.1, 1.7
    A, B, C = np.array([0, 0]), np.array([a, 0]), np.array([0, b])
    ax.add_patch(plt.Polygon([A, B, C], closed=True, facecolor=SUB, alpha=0.12,
                              edgecolor=INK, lw=2.0, zorder=5))

    def hatch_square(p0, p1, n=20, col=ACC):
        d = p1 - p0
        perp = np.array([-d[1], d[0]])
        for t in np.linspace(0, 1, n):
            s = p0 + t * d
            e = s + perp
            ax.plot([s[0], e[0]], [s[1], e[1]], color=col, lw=0.8, alpha=0.75)
        outline = [p0, p1, p1 + perp, p0 + perp, p0]
        ax.plot([q[0] for q in outline], [q[1] for q in outline], color=col, lw=1.8, zorder=4)

    hatch_square(B, A, col="#2a9d8f")             # on the base (below)
    hatch_square(A, C, col="#e76f51")             # on the height (left)
    hatch_square(C, B, col="#3a7ca8")             # on the hypotenuse (outward)
    ax.set_xlim(-1.9, 2.9); ax.set_ylim(-1.35, 2.9); ax.set_aspect("equal")
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


# ── Waves & Signals ──────────────────────────────────────────────────────────

def _square_wave(x, n_terms):
    s = np.zeros_like(x)
    for k in range(n_terms):
        n_odd = 2 * k + 1
        s += np.sin(n_odd * x) / n_odd
    return (4 / np.pi) * s


def g_fourier():
    fig, ax = MB.fig_trim(PAPER)
    x = np.linspace(-np.pi + 1e-3, np.pi - 1e-3, 2000)
    for i, N in enumerate([1, 3, 7, 31]):
        y = _square_wave(x, N) * 0.9
        col = CMAP(i / 3)
        ax.plot(x, y, color=col, lw=1.3, alpha=0.85)
    ax.axhline(0, color=SUB, lw=0.5, alpha=0.4)
    ax.set_xlim(-np.pi, np.pi); ax.set_ylim(-1.5, 1.5)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def g_wave():
    fig, ax = MB.fig_trim(DARK)
    x = np.linspace(-1, 1, 600)
    n = 10
    for i in range(n):
        phase = i * 0.35
        y = 0.75 * np.sin(6 * np.pi * x - phase) * np.exp(-0.15 * phase)
        col = CMAP(i / (n - 1))
        ax.plot(x, y - 0.0, color=col, lw=1.0, alpha=0.28 + 0.6 * (i / (n - 1)))
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.axis("off")
    return MB.to_pil(fig, DARK)


def g_bell():
    fig, ax = MB.fig_trim(PAPER)
    x = np.linspace(-4, 4, 1000)
    sigmas = np.linspace(0.6, 1.8, 9)
    for i, s in enumerate(sigmas):
        y = np.exp(-x**2 / (2 * s**2)) / (s * np.sqrt(2 * np.pi))
        col = CMAP(i / (len(sigmas) - 1))
        ax.plot(x, y, color=col, lw=1.2, alpha=0.85)
    ax.set_xlim(-4, 4); ax.set_ylim(0, 0.75)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


# ── Topology & Higher Dimensions (pyvista wireframe renders, cached) ────────

def g_mobius(): return _pv_page("_mobius_full.png", DARK)
def g_klein(): return _pv_page("_klein_full.png", DARK)


def g_tesseract():
    """4D hypercube projected to 2D as a dense contour wireframe (no pyvista)."""
    fig, ax = MB.fig_trim(DARK)
    # 16 vertices of the unit tesseract {-1,1}^4
    verts = np.array(
        [[x, y, z, w]
         for x in (-1, 1) for y in (-1, 1) for z in (-1, 1) for w in (-1, 1)],
        float,
    )
    # edges: differ in exactly one coordinate
    edges = []
    for i in range(16):
        for j in range(i + 1, 16):
            if np.sum(np.abs(verts[i] - verts[j]) > 0) == 1:
                edges.append((i, j))
    # project 4D → 3D (perspective on w) → 2D (isometric-ish)
    w = verts[:, 3]
    d = 3.2
    x3 = verts[:, 0] / (d - w)
    y3 = verts[:, 1] / (d - w)
    z3 = verts[:, 2] / (d - w)
    # rotate in 3D for a readable silhouette
    yaw, pitch = 0.55, 0.35
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    xr = cy * x3 + sy * z3
    zr = -sy * x3 + cy * z3
    yr = cp * y3 - sp * zr
    zr2 = sp * y3 + cp * zr
    # second perspective to 2D
    d2 = 3.5
    x2 = xr / (d2 - zr2)
    y2 = yr / (d2 - zr2)
    # draw edges with depth cue (farther = thinner/fainter)
    for a, b in edges:
        depth = 0.5 * (zr2[a] + zr2[b])
        t = float(np.clip((depth + 1.2) / 2.4, 0.0, 1.0))
        col = CMAP(0.15 + 0.7 * t)
        ax.plot(
            [x2[a], x2[b]], [y2[a], y2[b]],
            color=col, lw=0.55 + 1.1 * t, alpha=0.35 + 0.55 * t,
            solid_capstyle="round",
        )
    ax.scatter(x2, y2, s=8, c=zr2, cmap=CMAP, linewidths=0, zorder=5)
    pad = 0.12
    ax.set_xlim(x2.min() - pad, x2.max() + pad)
    ax.set_ylim(y2.min() - pad, y2.max() + pad)
    ax.set_aspect("equal")
    return MB.to_pil(fig, DARK)


def g_polyhedron(): return _pv_page("_polyhedron_full.png", DARK)


# ── Chaos & Flow ─────────────────────────────────────────────────────────────

def g_koch():
    fig, ax = MB.fig_trim(PAPER)

    def koch(order):
        p1, p2, p3 = 0j, 1 + 0j, 0.5 + 1j * np.sqrt(3) / 2
        pts = [p1, p2, p3, p1]
        for _ in range(order):
            new = [pts[0]]
            for i in range(len(pts) - 1):
                a0, a1 = pts[i], pts[i + 1]
                s = (a1 - a0) / 3
                a = a0 + s; b = a0 + 2 * s
                peak = a + s * np.exp(1j * np.pi / 3)
                new += [a, peak, b, a1]
            pts = new
        arr = np.array(pts)
        return arr.real, arr.imag

    x, y = koch(4)
    _grad_line(ax, x, y, lw=1.0)
    ax.set_xlim(-0.08, 1.08); ax.set_ylim(-0.1, 1.02); ax.set_aspect("equal")
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def g_navier():
    fig, ax = MB.fig_trim(DARK)
    rng = np.random.default_rng(11)
    sings = [(-0.5, 0.4, "src", 1.0), (0.55, 0.35, "sink", 1.0),
             (0.0, -0.5, "vcw", 0.8), (-0.55, -0.35, "vccw", 0.7)]

    def field(x, y):
        fx = np.zeros_like(x); fy = np.zeros_like(y)
        for sx, sy, kind, k in sings:
            dx, dy = x - sx, y - sy
            r2 = dx * dx + dy * dy + 0.02
            if kind == "src":
                fx += k * dx / r2; fy += k * dy / r2
            elif kind == "sink":
                fx += -k * dx / r2; fy += -k * dy / r2
            elif kind == "vcw":
                fx += k * dy / r2; fy += -k * dx / r2
            else:
                fx += -k * dy / r2; fy += k * dx / r2
        return fx, fy

    for _ in range(140):
        x, y = rng.uniform(-1, 1, 2)
        xs, ys = [x], [y]
        for _ in range(70):
            fx, fy = field(np.array([x]), np.array([y]))
            sp = np.hypot(fx[0], fy[0]) + 1e-6
            x += 0.02 * fx[0] / sp; y += 0.02 * fy[0] / sp
            if abs(x) > 1.1 or abs(y) > 1.1:
                break
            xs.append(x); ys.append(y)
        if len(xs) > 5:
            col = CMAP(min(1.0, len(xs) / 70))
            ax.plot(xs, ys, color=col, lw=0.6, alpha=0.55)
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1); ax.set_aspect("equal")
    ax.axis("off")
    return MB.to_pil(fig, DARK)


def g_dirac():
    fig, ax = MB.fig_trim(DARK)
    x = np.linspace(-6, 6, 1200)
    n = 14
    for i in range(n):
        k = 1.4 + 0.12 * i
        env_p = np.exp(-((x - 1.4) ** 2) / 3.2) * np.cos(k * x)
        env_m = -np.exp(-((x + 1.4) ** 2) / 3.2) * np.cos(k * x)
        col = CMAP(i / (n - 1))
        ax.plot(x, env_p * 0.8, color=col, lw=0.7, alpha=0.5)
        ax.plot(x, env_m * 0.8, color=col, lw=0.7, alpha=0.5)
    ax.axvline(0, color=GOLD, lw=1.0, alpha=0.6)
    ax.set_xlim(-6, 6); ax.set_ylim(-1, 1)
    ax.axis("off")
    return MB.to_pil(fig, DARK)


def g_logistic():
    fig, ax = MB.fig_trim(DARK)
    r = np.linspace(2.4, 4.0, 2200)
    x = np.full_like(r, 0.5)
    xs_plot, rs_plot = [], []
    for i in range(700):
        x = r * x * (1 - x)
        if i > 300:
            xs_plot.append(x); rs_plot.append(r)
    X = np.concatenate(xs_plot); R = np.concatenate(rs_plot)
    ax.scatter(R, X, s=0.7, c=CMAP((X - X.min()) / (X.max() - X.min())), alpha=0.65, linewidths=0)
    ax.set_xlim(2.4, 4.0); ax.set_ylim(0, 1)
    ax.axis("off")
    return MB.to_pil(fig, DARK)


# ── Paradox & Infinity ────────────────────────────────────────────────────────

def g_hilbert_hotel():
    fig, ax = MB.fig_trim(PAPER)
    n = 18
    for i in range(n):
        t = i / (n - 1)
        x = -1.05 + 1.9 * (1 - (1 - t) ** 1.4)
        w = 0.095 * (1 - 0.4 * t)
        h = 0.34 * (1 - 0.3 * t)
        y = -h / 2
        col = CMAP(t)
        ax.add_patch(Rectangle((x, y), w, h, fill=True, facecolor=col, alpha=0.18,
                                edgecolor=col, lw=2.2 * (1 - 0.25 * t)))
        if i < n - 1:
            t2 = (i + 1) / (n - 1)
            x2 = -1.05 + 1.9 * (1 - (1 - t2) ** 1.4)
            ax.annotate("", xy=(x2, 0), xytext=(x + w, 0),
                        arrowprops=dict(arrowstyle="->", color=INK, lw=1.1, alpha=0.85))
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-0.4, 0.4)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def g_cantor():
    fig, ax = MB.fig_trim(PAPER)
    levels = 7
    segs = [(0.0, 1.0)]
    y = 1.0
    for lvl in range(levels):
        col = CMAP(lvl / (levels - 1))
        for (a, b) in segs:
            ax.plot([a, b], [y, y], color=col, lw=1.6)
        new = []
        for (a, b) in segs:
            w = (b - a) / 3
            new.append((a, a + w)); new.append((b - w, b))
        segs = new
        y -= 1.0 / levels
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def g_zeno():
    fig, ax = MB.fig_trim(PAPER)
    x0 = -1.0
    total = 0.0
    n = 12
    for i in range(n):
        step = 1.6 / (2 ** i)
        col = CMAP(i / (n - 1))
        a, b = x0 + total, x0 + total + step
        yy = 0.05 * (-1) ** i
        th = np.linspace(0, np.pi, 60)
        arc_x = (a + b) / 2 + (b - a) / 2 * np.cos(th)
        arc_y = 0.12 * np.sin(th) + 0.02 * i
        ax.plot(arc_x, arc_y, color=col, lw=1.3, alpha=0.9)
        total += step
    ax.axhline(0.0, color=SUB, lw=0.6, alpha=0.4)
    ax.set_xlim(-1.15, 1.0); ax.set_ylim(-0.1, 0.5)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def g_monty():
    fig, ax = MB.fig_trim(PAPER)
    xs = [-0.7, 0, 0.7]
    root = (0, 0.62)
    for i, x in enumerate(xs):
        col = CMAP(i / 2)
        ax.add_patch(Rectangle((x - 0.18, -0.5), 0.36, 0.85, fill=True, facecolor=col,
                                alpha=0.14, edgecolor=INK, lw=1.6))
        ax.plot([root[0], x], [root[1], 0.4], color=col, lw=1.8, alpha=0.9)
        # after the reveal, branch lines fan from each first pick to the
        # remaining two doors -- the "switch" choices
        for j, x2 in enumerate(xs):
            if j == i:
                continue
            ax.plot([x, x2], [0.25, -0.05], color=col, lw=1.1, alpha=0.55)
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-0.6, 0.85)
    ax.axis("off")
    return MB.to_pil(fig, PAPER)


def contact_sheet():
    fns = [g_euler, g_golden, g_pythagoras, g_fourier, g_wave, g_bell,
           g_mobius, g_klein, g_tesseract, g_polyhedron,
           g_koch, g_navier, g_dirac, g_logistic,
           g_hilbert_hotel, g_cantor, g_zeno, g_monty]
    cols = 5
    rows = -(-len(fns) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    for ax, fn in zip(axes.ravel(), fns):
        img = fn()
        ax.imshow(img)
        ax.set_title(fn.__name__, fontsize=8)
        ax.axis("off")
    for ax in axes.ravel()[len(fns):]:
        ax.axis("off")
    out = os.path.join(HERE, "_contact_sheet.jpg")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    contact_sheet()
