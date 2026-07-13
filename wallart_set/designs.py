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

# Palettes. Each maps the ground ("bg"), a representative "accent" (used by the
# listing mockups) and a colour per design. Switch with use_palette(name).
PALETTES = {
    # Listing 1 — warm earth-tone / boho (published).
    "earth": {"bg": "#f2ebdd", "accent": "#b5715a",
              "maurer": "#b5715a", "phyllotaxis": "#c2a05f", "hilbert": "#4a463f",
              "cardioid": "#a9765c", "euler": "#4a463f", "fern": "#7f9070"},
    # Cool Japandi — soft cool greige ground, slate / sage / charcoal line work.
    "cool":  {"bg": "#e9e9e3", "accent": "#6d8b84",
              "maurer": "#6f7d84", "phyllotaxis": "#8a9284", "hilbert": "#3d4340",
              "cardioid": "#6d8b84", "euler": "#3d4340", "fern": "#7e8f76"},
    # Cream & black monochrome — charcoal line art on warm ivory.
    "mono":  {"bg": "#f4efe4", "accent": "#2b2823",
              "maurer": "#2b2823", "phyllotaxis": "#2b2823", "hilbert": "#2b2823",
              "cardioid": "#2b2823", "euler": "#2b2823", "fern": "#2b2823"},
}

BG = PALETTES["earth"]["bg"]
_C = dict(PALETTES["earth"])


def use_palette(name):
    """Switch the active palette (mutates module state read by the designs)."""
    global BG, _C
    _C = dict(PALETTES[name])
    BG = _C["bg"]


def accent():
    return _C["accent"]


def d_maurer(ax, lw_scale=1.0):
    n, d = 6, 71
    k = np.arange(0, 361)
    th = np.radians(k * d)
    r = np.sin(n * th)
    x, y = r * np.cos(th), r * np.sin(th)
    ax.plot(x, y, lw=0.5 * lw_scale, color=_C["maurer"], alpha=0.75)
    th2 = np.radians(np.arange(0, 361))
    r2 = np.sin(n * th2)
    ax.plot(r2 * np.cos(th2), r2 * np.sin(th2), lw=1.1 * lw_scale,
            color=_C["maurer"], alpha=0.5)
    return x, y


def d_phyllotaxis(ax, lw_scale=1.0):
    N = 1500
    k = np.arange(1, N)
    a = k * np.radians(137.507)
    r = np.sqrt(k)
    x, y = r * np.cos(a), r * np.sin(a)
    ax.scatter(x, y, s=((k / N) * 7 + 1) * lw_scale ** 2, color=_C["phyllotaxis"],
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
    ax.plot(p[:, 0], p[:, 1], lw=1.0 * lw_scale, color=_C["hilbert"],
            alpha=0.9, solid_capstyle="round")
    return p[:, 0], p[:, 1]


def d_cardioid(ax, lw_scale=1.0):
    from matplotlib.collections import LineCollection
    N, m = 240, 2
    th = np.linspace(0, 2 * np.pi, N, endpoint=False)
    px, py = np.cos(th), np.sin(th)
    segs = [[(px[i], py[i]), (px[(i * m) % N], py[(i * m) % N])] for i in range(N)]
    ax.add_collection(LineCollection(segs, colors=_C["cardioid"],
                                     linewidths=0.4 * lw_scale, alpha=0.4))
    return px, py


def d_euler(ax, lw_scale=1.0):
    t = np.linspace(-4.5, 4.5, 4000)
    dt = t[1] - t[0]
    x = np.cumsum(np.cos(t * t)) * dt
    y = np.cumsum(np.sin(t * t)) * dt
    x -= x.mean()
    y -= y.mean()
    ax.plot(x, y, lw=1.2 * lw_scale, color=_C["euler"], alpha=0.9,
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
    ax.scatter(xs, ys, s=0.11 * lw_scale ** 2, color=_C["fern"], alpha=0.7,
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

# ---- collection metadata (shared-pipeline interface) ------------------------
COLLECTION = "quiet"
SLUG = "QuietMathematics"
SET_NAME = "Quiet Mathematics"
SET_TAGLINE = "Set of 6 printable wall art · drawn from real equations"
GRID_TITLE = "Six original designs — drawn from real mathematics"
ORDER = ["maurer", "phyllotaxis", "hilbert", "cardioid", "euler", "fern"]
SUB = {
    "maurer": "Maurer rose · r = sin(6θ)",
    "phyllotaxis": "Golden angle · 137.5°",
    "hilbert": "Space-filling curve",
    "cardioid": "Modular circle · ×2",
    "euler": "Clothoid · Fresnel integrals",
    "fern": "Iterated function system",
}

_VS = 1.9  # video line/point scale for 1080px


def color(name):
    return _C[name]


def anim_data(name):
    """(kind, xs, ys, items, style) for the drawing animation.
    kind: 'poly' (items=(X,Y)), 'scatter' (items=(X,Y,S)), 'segs' (items=list)."""
    if name == "maurer":
        k = np.arange(0, 361); th = np.radians(k * 71); r = np.sin(6 * th)
        X, Y = r * np.cos(th), r * np.sin(th)
        return "poly", X, Y, (X, Y), 1.0 * _VS
    if name == "phyllotaxis":
        k = np.arange(1, 1500); a = k * np.radians(137.507); r = np.sqrt(k)
        X, Y = r * np.cos(a), r * np.sin(a)
        return "scatter", X, Y, (X, Y, ((k / 1500) * 7 + 1) * _VS ** 2), None
    if name == "hilbert":
        _, X, Y = None, *(_hilbert_xy())
        return "poly", X, Y, (X, Y), 1.0 * _VS
    if name == "euler":
        t = np.linspace(-4.5, 4.5, 4000); dt = t[1] - t[0]
        X = np.cumsum(np.cos(t * t)) * dt; Y = np.cumsum(np.sin(t * t)) * dt
        X -= X.mean(); Y -= Y.mean()
        return "poly", X, Y, (X, Y), 1.2 * _VS
    if name == "cardioid":
        N = 240; th = np.linspace(0, 2 * np.pi, N, endpoint=False)
        px, py = np.cos(th), np.sin(th)
        segs = [[(px[i], py[i]), (px[(i * 2) % N], py[(i * 2) % N])] for i in range(N)]
        return "segs", px, py, segs, 0.5 * _VS
    if name == "fern":
        rng = np.random.default_rng(7); Nn = 26000
        x = y = 0.0; X = np.empty(Nn); Y = np.empty(Nn); rs = rng.random(Nn)
        for i in range(Nn):
            r = rs[i]
            if r < 0.01: x, y = 0.0, 0.16 * y
            elif r < 0.86: x, y = 0.85*x+0.04*y, -0.04*x+0.85*y+1.6
            elif r < 0.93: x, y = 0.20*x-0.26*y, 0.23*x+0.22*y+1.6
            else: x, y = -0.15*x+0.28*y, 0.26*x+0.24*y+0.44
            X[i] = x; Y[i] = y
        return "scatter", X, Y, (X, Y, 0.12 * _VS ** 2), None
    raise KeyError(name)


def _hilbert_xy():
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
    return p[:, 0], p[:, 1]


def _description(palette_line, style, color_line):
    return f"""QUIET MATHEMATICS — a set of 6 printable wall art prints.

Six original designs, each drawn from a real mathematical curve and rendered as calm, minimalist line art {palette_line}. Not AI images and not clip art — every piece is generated from its equation, then composed for a {style} gallery wall.

THE SIX DESIGNS
• Maurer Rose — a rose curve walked in straight steps into a lace of interference
• Golden Spiral — sunflower seeds placed at the golden angle (137.5°)
• Hilbert Curve — a single continuous line that fills the plane
• Cardioid Weave — a times-table circle whose chords envelope a cardioid
• Euler Spiral — the clothoid, the curve of railways and roads
• Barnsley Fern — a fern grown from an iterated function system

WHAT YOU GET (instant digital download)
• All 6 designs in 5 aspect ratios — 2:3, 3:4, 4:5, 5:7 and ISO/A
• 300 DPI, high resolution — print small or large
• Delivered as 5 ZIP files (one per ratio), 30 files in total
• {color_line}

PRINT ALMOST ANY SIZE
2:3 → 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in
3:4 → 6x8, 9x12, 12x16, 18x24 in
4:5 → 8x10, 16x20, 24x30 in
5:7 → 5x7, 10x14, 15x21 in
ISO/A → A5, A4, A3, A2, A1

HOW IT WORKS
1) Buy and download instantly — no physical item is shipped.
2) Pick your size and ratio.
3) Print at home, a local print shop, or an online service.
4) Trim to your frame and hang.

Colours may vary slightly between screens and printers. Frames not included.

TERMS — For personal use only. Please do not resell, redistribute or share the files.

(c) MathRelaxing"""


LISTINGS = {
    "earth": {
        "title": ("Set of 6 Printable Wall Art | Boho Abstract Line Art Gallery Wall Set | "
                  "Neutral Earth Tone Japandi Decor | Mathematical Minimalist Prints"),
        "tags": ["printable wall art", "gallery wall set", "set of 6 prints", "boho wall art",
                 "abstract line art", "neutral wall art", "earth tone art", "japandi wall art",
                 "minimalist print", "digital download", "terracotta decor", "living room decor",
                 "math wall art"],
        "description": _description("in a warm earth-tone palette", "Japandi / boho",
                                    "Warm cream ground with muted terracotta, sage, gold and charcoal line work"),
        "price": 9.99, "listing_id": 4536831020,
    },
    "cool": {
        "title": ("Set of 6 Japandi Printable Wall Art | Sage Green Minimalist Line Art Gallery Wall Set | "
                  "Cool Neutral Zen Decor | Mathematical Prints"),
        "tags": ["japandi wall art", "printable wall art", "gallery wall set", "set of 6 prints",
                 "sage green art", "minimalist print", "zen wall art", "abstract line art",
                 "neutral wall art", "digital download", "scandinavian art", "living room decor",
                 "math wall art"],
        "description": _description("in a cool, muted Japandi palette", "Japandi / zen",
                                    "Soft cool greige ground with sage, slate and charcoal line work"),
        "price": 9.99, "listing_id": 4536825589,
    },
    "mono": {
        "title": ("Set of 6 Black and White Printable Wall Art | Minimalist Line Art Gallery Wall Set | "
                  "Scandinavian Abstract Decor | Mathematical Prints"),
        "tags": ["black and white art", "printable wall art", "gallery wall set", "set of 6 prints",
                 "minimalist print", "line art print", "scandinavian art", "abstract wall art",
                 "modern wall art", "digital download", "monochrome print", "living room decor",
                 "math wall art"],
        "description": _description("in black and white", "Scandinavian / minimalist",
                                    "Warm ivory ground with charcoal line work — a true black-and-white set"),
        "price": 9.99, "listing_id": 4536834070,
    },
}
