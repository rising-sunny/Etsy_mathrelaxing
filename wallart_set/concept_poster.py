"""
concept_poster.py — "Mathematical Concept Posters": each is a real scientific
plate (a genuine diagram + data + a terse, human caption), not decorative
AI-style art. Technical typography (sans / mono) on pale lab-paper — the
opposite of the cream+serif look that reads as AI.

Concepts: harmonic, golden, euler, pi, ulam, fourier.
Layout is proportional, so plates render cleanly at any aspect ratio.
"""
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib import font_manager
from PIL import Image

SANS = font_manager.FontProperties(family="DejaVu Sans")
MONO = font_manager.FontProperties(family="DejaVu Sans Mono")

PAPER = "#eef0ec"; INK = "#1c1e1c"; SUB = "#5c625c"; ACC = "#9a5236"; GRIDC = "#dadfd9"
ML, MR, MT, MB = 1.55, 1.35, 1.5, 2.05


def _prime(n):
    if n < 2:
        return False
    for p in range(2, int(n ** 0.5) + 1):
        if n % p == 0:
            return False
    return True


# ----- figure bodies (draw within box = (x0, x1, y0, y1)) --------------------
def fig_harmonic(ax, box, W):
    x0, x1, y0, y1 = box
    names = ["fundamental", "2nd harmonic", "3rd harmonic", "4th harmonic",
             "5th harmonic", "6th harmonic", "7th harmonic", "8th harmonic"]
    lam = ["2L", "L", "2L/3", "L/2", "2L/5", "L/3", "2L/7", "L/4"]
    x = np.linspace(0, 1, 700)
    xa = x0 + 0.2; L = x1 - xa - 0.9
    N = 8; step = (y1 - y0) / (N - 1); A = step * 0.42
    for i in range(N):
        n = i + 1; yb = y1 - i * step
        ax.plot([xa, xa + L], [yb, yb], color=SUB, lw=0.5)
        ax.plot(xa + x * L, yb + A * np.sin(n * np.pi * x), color=INK, lw=1.2)
        ax.plot(xa + x * L, yb - A * np.sin(n * np.pi * x), color=INK, lw=1.2, alpha=0.3)
        nd = np.arange(0, n + 1) / n
        ax.scatter(xa + nd * L, [yb] * len(nd), s=W * 1.3, color=ACC, zorder=5)
        ax.text(xa - 0.14, yb, f"{n}", fontproperties=MONO, fontsize=W * 1.4, color=INK, ha="right", va="center")
        ax.text(xa - 0.36, yb, names[i], fontproperties=SANS, fontsize=W * 0.9, color=SUB, ha="right", va="center")
        ax.text(xa + L + 0.12, yb, f"λ = {lam[i]}", fontproperties=MONO, fontsize=W * 1.0, color=SUB, va="center")


def fig_golden(ax, box, W):
    x0, x1, y0, y1 = box
    phi = (1 + 5 ** 0.5) / 2
    # Exact golden spiral: quarter-circle arcs whose radius grows by φ each turn
    # (geometric, not Fibonacci) so it keeps winding inward with ever-smaller
    # arcs — more turns toward the centre. The walk keeps the arcs tangent:
    # centre one radius to the LEFT of travel, 90° CCW sweep, heading +90°.
    radii = [phi ** k for k in range(-7, 12)]   # inner arcs added in ×4 counts
    #                                             so the composition stays landscape
    P = np.array([0.0, 0.0]); T = np.array([1.0, 0.0])
    arcs = []; squares = []; pts = [P.copy()]
    for s in radii:
        left = np.array([-T[1], T[0]])
        C = P + left * s
        a0 = np.degrees(np.arctan2(P[1] - C[1], P[0] - C[0]))
        arcs.append((C.copy(), s, a0, a0 + 90))
        # square containing this quarter arc
        ar = np.radians(a0 + 90)
        P2 = C + s * np.array([np.cos(ar), np.sin(ar)])
        xs_ = [C[0], P[0], P2[0]]; ys_ = [C[1], P[1], P2[1]]
        squares.append((min(xs_), min(ys_), s))
        P = P2; T = np.array([-T[1], T[0]]); pts.append(P.copy())
    pts = np.array(pts)
    # fit into box
    allx = [c[0] - r for c, r, _, _ in arcs] + [c[0] + r for c, r, _, _ in arcs]
    ally = [c[1] - r for c, r, _, _ in arcs] + [c[1] + r for c, r, _, _ in arcs]
    minx, maxx, miny, maxy = min(allx), max(allx), min(ally), max(ally)
    sc = min((x1 - x0) / (maxx - minx), (y1 - y0) / (maxy - miny)) * 0.88
    ox = (x0 + x1) / 2 - (minx + maxx) / 2 * sc
    oy = (y0 + y1) / 2 - (miny + maxy) / 2 * sc
    for (sx, sy, s) in squares:
        if s * sc < 0.06:      # skip the tiniest squares near the eye (clutter)
            continue
        ax.add_patch(mp.Rectangle((ox + sx * sc, oy + sy * sc), s * sc, s * sc,
                                  fill=False, edgecolor=SUB, lw=0.6))
    for (C, r, a0, a1) in arcs:
        lw = max(0.7, min(1.7, r * sc * 1.1))     # thinner as the arc shrinks
        ax.add_patch(mp.Arc((ox + C[0] * sc, oy + C[1] * sc), 2 * r * sc, 2 * r * sc,
                            angle=0, theta1=a0, theta2=a1, color=ACC, lw=lw))
    ax.text(x0 + 0.1, y1, "1, 1, 2, 3, 5, 8, 13, 21, …", fontproperties=MONO,
            fontsize=W * 1.1, color=SUB, va="top")
    ax.text(x1 - 0.1, y0 + 0.1, "φ = 1.6180339887…", fontproperties=MONO,
            fontsize=W * 1.25, color=ACC, ha="right", va="bottom")


def fig_euler(ax, box, W):
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) / 2 * 0.62
    ax.plot([cx - R * 1.5, cx + R * 1.5], [cy, cy], color=SUB, lw=0.6)
    ax.plot([cx, cx], [cy - R * 1.5, cy + R * 1.5], color=SUB, lw=0.6)
    ax.text(cx + R * 1.55, cy, "Re", fontproperties=SANS, fontsize=W * 0.9, color=SUB, va="center")
    ax.text(cx, cy + R * 1.6, "Im", fontproperties=SANS, fontsize=W * 0.9, color=SUB, ha="center")
    ax.add_patch(mp.Circle((cx, cy), R, fill=False, edgecolor=INK, lw=1.2))
    th = np.linspace(0, np.pi, 160)
    ax.plot(cx + R * np.cos(th), cy + R * np.sin(th), color=ACC, lw=2.4)
    ax.annotate("", xy=(cx - R, cy), xytext=(cx - R + 0.001, cy + 0.02),
                arrowprops=dict(arrowstyle="-|>", color=ACC, lw=2))
    for px, py, lab in [(1, 0, "1"), (0, 1, "i"), (-1, 0, "−1"), (0, -1, "−i")]:
        ax.scatter([cx + px * R], [cy + py * R], s=W * 1.6, color=INK, zorder=5)
        ax.text(cx + px * R * 1.16, cy + py * R * 1.16, lab, fontproperties=MONO,
                fontsize=W * 1.2, color=INK, ha="center", va="center")
    # angle theta = pi
    ax.plot([cx, cx - R], [cy, cy], ls=(0, (4, 3)), color=SUB, lw=0.8)
    ax.text(cx + R * 0.18, cy + R * 0.14, "θ", fontproperties=SANS, fontsize=W * 1.0, color=ACC)
    ax.text(cx, cy - R * 1.75, "e^{iθ} = cos θ + i sin θ", fontproperties=SANS,
            fontsize=W * 1.35, color=INK, ha="center")


def fig_pi(ax, box, W):
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 0.2
    R = min(x1 - x0, y1 - y0) / 2 * 0.6
    ax.add_patch(mp.Circle((cx, cy), R, fill=False, edgecolor=INK, lw=1.6))
    for m, col, alp in [(6, SUB, 0.9), (12, ACC, 0.9), (24, INK, 0.6)]:
        a = np.linspace(0, 2 * np.pi, m + 1) + np.pi / 2
        ax.plot(cx + R * np.cos(a), cy + R * np.sin(a), color=col, lw=1.0, alpha=alp)   # inscribed
    a6 = np.linspace(0, 2 * np.pi, 7) + np.pi / 2                                        # circumscribed hexagon
    Rc = R / np.cos(np.pi / 6)
    ax.plot(cx + Rc * np.cos(a6), cy + Rc * np.sin(a6), color=SUB, lw=0.9, ls=(0, (4, 3)))
    ax.text(cx, cy - R * 1.9, "3 + 10/71  <  π  <  3 + 1/7", fontproperties=MONO,
            fontsize=W * 1.25, color=ACC, ha="center")
    ax.text(cx, cy - R * 2.2, "3.1408 … < π < 3.1429 …   (96-gon, Archimedes)",
            fontproperties=SANS, fontsize=W * 0.95, color=SUB, ha="center")


def fig_ulam(ax, box, W):
    x0, x1, y0, y1 = box
    S = 251                       # ~63,000 numbers: the diagonal prime lines are unmistakable
    cell = min(x1 - x0, y1 - y0) / S
    gx = (x0 + x1) / 2 - S * cell / 2
    gy = (y0 + y1) / 2 - S * cell / 2
    NN = S * S
    sieve = np.ones(NN + 1, bool); sieve[:2] = False
    for p in range(2, int(NN ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    cxc = cyc = S // 2
    px, py = [], []

    def put(n, ix, iy):
        if sieve[n]:
            fx, fy = cxc + ix, cyc + iy
            if 0 <= fx < S and 0 <= fy < S:
                px.append(gx + (fx + 0.5) * cell)
                py.append(gy + (fy + 0.5) * cell)
    x = y = 0; n = 1; step = 1; d = 0
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    put(1, 0, 0)
    while n < NN:
        for _ in range(2):
            dx, dy = dirs[d % 4]
            for _ in range(step):
                if n >= NN:
                    break
                x += dx; y += dy; n += 1; put(n, x, y)
            d += 1
        step += 1
    ax.scatter(px, py, s=(cell * 72) ** 2 * 0.8, color=INK, zorder=4, marker="s", linewidths=0)
    ax.add_patch(mp.Rectangle((gx, gy), S * cell, S * cell, fill=False, edgecolor=SUB, lw=0.6))
    ax.text((x0 + x1) / 2, y0 + 0.02, "each dot is a prime  ·  the diagonals are its hidden order",
            fontproperties=SANS, fontsize=W * 0.9, color=SUB, ha="center", va="bottom")


def fig_fourier(ax, box, W):
    x0, x1, y0, y1 = box
    t = np.linspace(0, 1, 1000)
    xa = x0 + 0.2; L = x1 - xa - 0.2
    Ks = [1, 2, 3, 12]
    labs = ["1 term", "2 terms", "3 terms", "12 terms"]
    N = len(Ks)
    band_top = y1 - 0.55; band_bot = y0 + 0.6
    step = (band_top - band_bot) / (N - 1); A = step * 0.24
    for i, K in enumerate(Ks):
        yb = band_top - i * step
        sq = np.sign(np.sin(2 * np.pi * t)); sq[sq == 0] = 1
        ax.plot(xa + t * L, yb + A * sq, color=SUB, lw=0.6, alpha=0.5)          # target
        s = np.zeros_like(t)
        for j in range(1, K + 1):
            k = 2 * j - 1
            s += (4 / np.pi) * np.sin(2 * np.pi * k * t) / k
        ax.plot(xa + t * L, yb + A * s, color=INK, lw=1.3)
        ax.text(xa - 0.14, yb, labs[i], fontproperties=SANS, fontsize=W * 0.9, color=SUB, ha="right", va="center")


CONCEPTS = {
    "harmonic": {
        "title": "MODES OF A VIBRATING STRING", "eyebrow": "THE HARMONIC SERIES   ·   1, 1/2, 1/3, 1/4, …",
        "fig": fig_harmonic, "corner": "∑ 1/n  →  ∞",
        "caption": ["A plucked string sounds all of these at once. Their wavelengths are L, L/2, L/3, …",
                    "— the harmonic series. The sum 1 + 1/2 + 1/3 + … never settles: it passes every",
                    "value, however slowly. Reaching a total of just 100 takes about 1.5 × 10⁴³ terms."],
    },
    "golden": {
        "title": "THE GOLDEN RATIO", "eyebrow": "φ = (1 + √5) / 2   ·   the Fibonacci squares",
        "fig": fig_golden, "corner": "φ² = φ + 1",
        "caption": ["Split a length so the whole is to the larger part as the larger is to the smaller,",
                    "and the ratio is φ = 1.618… Tile squares whose sides are the Fibonacci numbers",
                    "1, 1, 2, 3, 5, 8, … and their ratios close in on φ — the spiral is the limit."],
    },
    "euler": {
        "title": "EULER'S IDENTITY", "eyebrow": "e^{iπ} + 1 = 0   ·   the unit circle",
        "fig": fig_euler, "corner": "e^{iπ} + 1 = 0",
        "caption": ["Walk the unit circle: e^{iθ} = cos θ + i sin θ. A quarter turn lands on i, a half",
                    "turn on −1. So e^{iπ} = −1, which rearranges to e^{iπ} + 1 = 0 — one line tying",
                    "together e, i, π, 1 and 0, arguably the five most important numbers in mathematics."],
    },
    "pi": {
        "title": "SQUEEZING π", "eyebrow": "ARCHIMEDES' METHOD   ·   inscribed & circumscribed polygons",
        "fig": fig_pi, "corner": "π = 3.14159…",
        "caption": ["Trap a circle between two polygons and measure their perimeters. With 96 sides",
                    "Archimedes proved 3 + 10/71 < π < 3 + 1/7 — that is 3.1408… < π < 3.1429… More",
                    "sides tighten the trap; the circle itself is the limit both polygons approach."],
    },
    "ulam": {
        "title": "THE ULAM SPIRAL", "eyebrow": "PRIME NUMBERS   ·   2, 3, 5, 7, 11, 13, …",
        "fig": fig_ulam, "corner": "primes: 2, 3, 5, 7, …",
        "caption": ["Write the whole numbers in a square spiral and shade the primes. They refuse to",
                    "scatter evenly — instead they crowd onto diagonal lines, the tracks of simple",
                    "quadratics like n² + n + 41. Even so, no formula catches every prime."],
    },
    "fourier": {
        "title": "BUILDING A SQUARE WAVE", "eyebrow": "FOURIER SERIES   ·   sin x + sin 3x/3 + sin 5x/5 + …",
        "fig": fig_fourier, "corner": "Σ sin(nx)/n",
        "caption": ["Add sine waves of frequency 1, 3, 5, 7, … with heights 1, 1/3, 1/5, … and a square",
                    "wave takes shape. Any repeating signal is a sum of pure tones — the same idea",
                    "behind a synthesiser, an MP3, and how your ear pulls a chord apart."],
    },
}


def render(key, W, H, dpi=110):
    return render_plate(CONCEPTS[key], W, H, dpi)


def render_plate(c, W, H, dpi=110):
    """Draw one scientific plate from a spec dict (shared by the physics line)."""
    fig = plt.figure(figsize=(W, H), dpi=dpi); fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(PAPER); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    for gx in np.arange(0.5, W, 0.5):
        ax.plot([gx, gx], [0.4, H - 0.4], color=GRIDC, lw=0.4, zorder=0)
    for gy in np.arange(0.5, H, 0.5):
        ax.plot([0.4, W - 0.4], [gy, gy], color=GRIDC, lw=0.4, zorder=0)
    lx = 0.5
    ax.text(lx, H - 0.85, c["title"], fontproperties=SANS, fontsize=W * 2.15, color=INK, weight="bold")
    ax.text(lx, H - 1.16, c["eyebrow"], fontproperties=MONO, fontsize=W * 1.15, color=ACC)
    ax.text(W - 0.5, H - 0.88, "FIG. 1", fontproperties=MONO, fontsize=W * 1.1, color=SUB, ha="right")
    ax.plot([lx, W - 0.5], [H - 1.34, H - 1.34], color=INK, lw=0.8)
    box = (ML, W - MR, MB + 0.15, H - MT - 0.35)
    c["fig"](ax, box, W)
    ax.plot([lx, W - 0.5], [MB - 0.3, MB - 0.3], color=GRIDC, lw=0.8)
    ax.text(lx, MB - 0.55, "\n".join(c["caption"]), fontproperties=SANS, fontsize=W * 1.02,
            color=INK, va="top", linespacing=1.6)
    ax.text(W - 0.5, 0.42, c["corner"], fontproperties=MONO, fontsize=W * 1.45, color=ACC, ha="right")
    return fig


def to_pil(fig, dpi=110):
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor=PAPER, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGB")


if __name__ == "__main__":
    from PIL import ImageDraw
    keys = list(CONCEPTS.keys())
    ims = [to_pil(render(k, 8, 10, dpi=95)) for k in keys]
    tw = 380; ims = [i.resize((tw, int(i.height * tw / i.width))) for i in ims]
    th = ims[0].height; pad = 10
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 2 * th + 3 * pad), "#fff")
    for i, im in enumerate(ims):
        r, c = divmod(i, 3)
        sheet.paste(im, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save("/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/wallart/concepts_all.png")
    print("montage saved")
