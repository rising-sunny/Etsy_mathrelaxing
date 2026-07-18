"""
gridpaper.py — "Aesthetic Grid Paper" pages: functional note/graph papers drawn
in the MathRelaxing earth palette with a minimal serif header. Vector output
(matplotlib) so the PDF prints crisp at any size. US Letter or A4.

Ten styles: square, dot, isometric, triangular, hexagonal, ruled, cornell,
penrose (decorative, ties to the wall-art line), polar, sketch+notes.
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection

import designs_geo

SERIF = font_manager.FontProperties(family="DejaVu Serif")

# palettes: paper ground, grid line, accent, text
PALETTES = {
    "earth": {"paper": "#fbf8f1", "grid": "#dcc9ae", "acc": "#b5715a", "txt": "#7a614c"},
    "mono":  {"paper": "#f7f4ee", "grid": "#d5cec2", "acc": "#4a463f", "txt": "#3a3733"},
    "cool":  {"paper": "#eef0ec", "grid": "#ccd4cc", "acc": "#6d8b84", "txt": "#43505a"},
}
PAPER, GRID, ACC, TXT = (PALETTES["earth"][k] for k in ("paper", "grid", "acc", "txt"))

# featured decorative page: (label, module_name, design_name)
FEATURED = ("Penrose Grid", "designs_geo", "penrose")


def use_palette(name):
    global PAPER, GRID, ACC, TXT
    p = PALETTES[name]
    PAPER, GRID, ACC, TXT = p["paper"], p["grid"], p["acc"], p["txt"]


def set_featured(label, module_name, design_name):
    global FEATURED
    FEATURED = (label, module_name, design_name)
    _build_styles()

# margins (inches): left, right, bottom, top(header)
ML, MR, MB, MT = 0.6, 0.6, 0.55, 1.15


def region(W, H):
    return ML, W - MR, MB, H - MT       # x0, x1, y0, y1


def _inbox(seg, box):
    (x0, x1, y0, y1) = box
    for (x, y) in seg:
        if not (x0 - 0.3 <= x <= x1 + 0.3 and y0 - 0.3 <= y <= y1 + 0.3):
            return False
    return True


def header(ax, title, W, H):
    x0, x1, y0, y1 = region(W, H)
    ax.text(W / 2, H - 0.62, title, ha="center", va="center",
            fontproperties=SERIF, fontsize=15, color=TXT)
    ax.text(W / 2, H - 0.9, "M A T H R E L A X I N G", ha="center", va="center",
            fontproperties=SERIF, fontsize=8, color=ACC)
    ax.plot([x0, x1], [H - 1.05, H - 1.05], color=GRID, lw=1.0)
    ax.plot([x0, x1], [y0 - 0.12, y0 - 0.12], color=GRID, lw=1.0)


# ---- styles ------------------------------------------------------------------
def s_square(ax, box, s=0.25):
    x0, x1, y0, y1 = box
    for x in np.arange(x0, x1 + 1e-6, s):
        ax.plot([x, x], [y0, y1], color=GRID, lw=0.5)
    for y in np.arange(y0, y1 + 1e-6, s):
        ax.plot([x0, x1], [y, y], color=GRID, lw=0.5)


def s_dot(ax, box, s=0.25):
    x0, x1, y0, y1 = box
    xs = np.arange(x0, x1 + 1e-6, s)
    ys = np.arange(y0, y1 + 1e-6, s)
    X, Y = np.meshgrid(xs, ys)
    ax.scatter(X, Y, s=1.6, color=GRID)


def _tri_segs(box, a, transpose=False):
    x0, x1, y0, y1 = box
    if transpose:                       # build in transposed frame, map back
        bx = (y0, y1, x0, x1)
    else:
        bx = box
    bx0, bx1, by0, by1 = bx
    hy = a * math.sqrt(3) / 2
    rows = int((by1 - by0) / hy) + 3
    cols = int((bx1 - bx0) / a) + 4
    pts = {}
    for jj in range(rows):
        for ii in range(cols):
            x = bx0 - a + ii * a + (jj % 2) * a / 2
            y = by0 + jj * hy
            pts[(ii, jj)] = (x, y)
    segs = []
    for (ii, jj), p in pts.items():
        for di, dj in [(1, 0), (0, 1), (-1, 1)]:
            n = pts.get((ii + di, jj + dj))
            if n:
                segs.append([p, n])
    if transpose:
        segs = [[(p[1], p[0]) for p in s] for s in segs]
    return [s for s in segs if _inbox(s, box)]


def s_triangular(ax, box, a=0.5):
    ax.add_collection(LineCollection(_tri_segs(box, a), colors=GRID, linewidths=0.4))


def s_isometric(ax, box, a=0.5):
    ax.add_collection(LineCollection(_tri_segs(box, a, transpose=True),
                                     colors=GRID, linewidths=0.4))


def s_hexagonal(ax, box, R=0.28):
    x0, x1, y0, y1 = box
    w = math.sqrt(3) * R                # pointy-top honeycomb
    vh = 1.5 * R
    segs = []
    rows = int((y1 - y0) / vh) + 3
    cols = int((x1 - x0) / w) + 3
    for j in range(rows):
        for i in range(cols):
            cx = x0 + i * w + (j % 2) * w / 2
            cy = y0 + j * vh
            hexpts = [(cx + R * math.cos(math.pi / 6 + k * math.pi / 3),
                       cy + R * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
            for k in range(6):
                seg = [hexpts[k], hexpts[(k + 1) % 6]]
                if _inbox(seg, box):
                    segs.append(seg)
    ax.add_collection(LineCollection(segs, colors=GRID, linewidths=0.4))


def s_ruled(ax, box, s=0.34):
    x0, x1, y0, y1 = box
    for y in np.arange(y0, y1 + 1e-6, s):
        ax.plot([x0, x1], [y, y], color=GRID, lw=0.5)
    ax.plot([x0 + 0.9, x0 + 0.9], [y0, y1], color=ACC, lw=0.6, alpha=0.5)


def s_cornell(ax, box, s=0.34):
    x0, x1, y0, y1 = box
    cue = x0 + 2.0
    sumy = y0 + 1.6
    ax.plot([cue, cue], [sumy, y1], color=GRID, lw=0.8)
    ax.plot([x0, x1], [sumy, sumy], color=GRID, lw=0.8)
    for y in np.arange(sumy + s, y1, s):
        ax.plot([cue, x1], [y, y], color=GRID, lw=0.4)
    ax.text((x0 + cue) / 2, (sumy + y1) / 2, "Cue", ha="center", rotation=90,
            fontproperties=SERIF, fontsize=10, color=GRID)
    ax.text((x0 + x1) / 2, y0 + 0.75, "Summary", ha="center",
            fontproperties=SERIF, fontsize=10, color=GRID)


def draw_in_box(ax, module_name, name, box, color, lw=0.35):
    """Draw any of our designs (from designs / designs_geo) scaled into `box`."""
    import importlib
    mod = importlib.import_module(module_name)
    if hasattr(mod, "data"):                      # geo: (kind, xs, ys, items, lw)
        kind, xs, ys, items, _ = mod.data(name)
    else:                                          # quiet: anim_data
        kind, xs, ys, items, _ = mod.anim_data(name)
    xs = np.asarray(xs); ys = np.asarray(ys)
    x0, x1, y0, y1 = box
    sc = min((x1 - x0) / (xs.max() - xs.min()), (y1 - y0) / (ys.max() - ys.min())) * 0.98
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mx, my = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    T = lambda x, y: (cx + (x - mx) * sc, cy + (y - my) * sc)
    if kind == "segs":
        ax.add_collection(LineCollection([[T(*a), T(*b)] for a, b in items],
                                         colors=color, linewidths=lw))
    elif kind == "circles":
        for ccx, ccy, r in items:
            ax.add_patch(plt.Circle(T(ccx, ccy), r * sc, fill=False,
                                    edgecolor=color, lw=lw))
    elif kind == "poly":
        X, Y = items
        P = [T(x, y) for x, y in zip(X, Y)]
        ax.plot([p[0] for p in P], [p[1] for p in P], color=color, lw=lw)
    elif kind == "scatter":
        X, Y, _S = items
        P = [T(x, y) for x, y in zip(X, Y)]
        ax.scatter([p[0] for p in P], [p[1] for p in P], s=0.5, color=color, linewidths=0)


def s_featured(ax, box):
    _, module_name, name = FEATURED
    draw_in_box(ax, module_name, name, box, GRID, lw=0.35)


def s_polar(ax, box):
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) / 2 * 0.98
    for r in np.arange(R / 12, R + 1e-6, R / 12):
        ax.add_patch(plt.Circle((cx, cy), r, fill=False, edgecolor=GRID, lw=0.4))
    for k in range(24):
        a = k * math.pi / 12
        ax.plot([cx, cx + R * math.cos(a)], [cy, cy + R * math.sin(a)], color=GRID, lw=0.4)


def s_sketch(ax, box, s=0.34):
    x0, x1, y0, y1 = box
    split = y0 + (y1 - y0) * 0.55
    ax.add_patch(plt.Rectangle((x0, split), x1 - x0, y1 - split, fill=False,
                               edgecolor=GRID, lw=0.8))
    for y in np.arange(y0, split - 0.1, s):
        ax.plot([x0, x1], [y, y], color=GRID, lw=0.5)


def _build_styles():
    global STYLES, ORDER
    STYLES = {
        "Square Grid": s_square, "Dot Grid": s_dot, "Isometric": s_isometric,
        "Triangular": s_triangular, "Hexagonal": s_hexagonal, "Ruled Notes": s_ruled,
        "Cornell Notes": s_cornell, FEATURED[0]: s_featured, "Polar Grid": s_polar,
        "Sketch + Notes": s_sketch,
    }
    ORDER = list(STYLES.keys())


_build_styles()

LETTER = (8.5, 11.0)
A4 = (8.27, 11.69)


def render_fig(style, size=LETTER, dpi=90):
    W, H = size
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(PAPER)
    ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    header(ax, style, W, H)
    STYLES[style](ax, region(W, H))
    return fig


if __name__ == "__main__":
    import io
    from PIL import Image, ImageDraw
    imgs = []
    for name in ORDER:
        fig = render_fig(name)
        b = io.BytesIO(); fig.savefig(b, format="png", facecolor=PAPER, dpi=90)
        plt.close(fig); b.seek(0)
        imgs.append((name, Image.open(b).convert("RGB")))
    cols, rows = 5, 2
    pad, lab = 10, 20
    iw, ih = imgs[0][1].size
    cw, ch = iw, ih + lab
    sheet = Image.new("RGB", (cols * cw + pad * (cols + 1), rows * ch + pad * (rows + 1)), "#fff")
    d = ImageDraw.Draw(sheet)
    for i, (nm, im) in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad); y = pad + r * (ch + pad)
        sheet.paste(im, (x, y + lab)); d.text((x + 4, y + 6), nm, fill="#111")
    out = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/wallart/gridpaper_v2.png"
    sheet.save(out); print("OK", out, sheet.size)
