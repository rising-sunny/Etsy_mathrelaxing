"""
scigrid.py — "Engineering & Science Graph Paper": the technical papers a STEM
student or engineer actually needs — log-log, semi-log, millimeter, engineering
5x5, a numbered Cartesian plane, polar in degrees, log-polar and 3D isometric.

Companion to the aesthetic gridpaper.py (shares its earth palette and serif
header), but a distinct product: functional scientific plotting grids, vector,
US Letter or A4. Every grid is computed, not clip art.
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import gridpaper as gp                        # reuse palette, header, page sizes

SERIF = gp.SERIF
LETTER, A4 = gp.LETTER, gp.A4
use_palette = gp.use_palette                  # same palette switch (earth/mono/cool)
MM = 1.0 / 25.4                               # inches per millimetre


# ---- helpers ----------------------------------------------------------------
def _grid(ax, xs_levels, ys_levels):
    """xs_levels / ys_levels: list of (positions, color, lw, alpha) → one draw each."""
    for kind, levels in (("v", xs_levels), ("h", ys_levels)):
        for pos, color, lw, alpha in levels:
            if kind == "v":
                segs = [[(p, ax._sci_box[2]), (p, ax._sci_box[3])] for p in pos]
            else:
                segs = [[(ax._sci_box[0], p), (ax._sci_box[1], p)] for p in pos]
            ax.add_collection(LineCollection(segs, colors=color, linewidths=lw, alpha=alpha))


def _decade_positions(lo, hi, dec_len):
    """Return (minor, major) log positions spanning [lo, hi] with dec_len per decade."""
    n = max(1, round((hi - lo) / dec_len))
    step = (hi - lo) / n
    minor, major = [], []
    for d in range(n + 1):
        for m in range(1, 10):
            if d == n and m > 1:
                break
            p = lo + (d + math.log10(m)) * step
            (major if m == 1 else minor).append(p)
    return minor, major, n, step


# ---- styles -----------------------------------------------------------------
def s_engineering(ax, box):
    x0, x1, y0, y1 = box
    s = 0.1
    xs = np.arange(x0, x1 + 1e-6, s); ys = np.arange(y0, y1 + 1e-6, s)
    xmin = [x for i, x in enumerate(xs) if round((x - x0) / s) % 5]
    xmaj = [x for i, x in enumerate(xs) if round((x - x0) / s) % 5 == 0]
    ymin = [y for i, y in enumerate(ys) if round((y - y0) / s) % 5]
    ymaj = [y for i, y in enumerate(ys) if round((y - y0) / s) % 5 == 0]
    ax._sci_box = box
    _grid(ax, [(xmin, gp.GRID, 0.3, 0.7), (xmaj, gp.ACC, 0.6, 0.4)],
              [(ymin, gp.GRID, 0.3, 0.7), (ymaj, gp.ACC, 0.6, 0.4)])


def s_millimeter(ax, box):
    x0, x1, y0, y1 = box
    xs = np.arange(x0, x1 + 1e-6, MM); ys = np.arange(y0, y1 + 1e-6, MM)
    def split(vals, o):
        mn, md, mj = [], [], []
        for v in vals:
            k = round((v - o) / MM)
            (mj if k % 10 == 0 else md if k % 5 == 0 else mn).append(v)
        return mn, md, mj
    xmn, xmd, xmj = split(xs, x0); ymn, ymd, ymj = split(ys, y0)
    ax._sci_box = box
    _grid(ax, [(xmn, gp.GRID, 0.2, 0.45), (xmd, gp.GRID, 0.4, 0.9), (xmj, gp.ACC, 0.6, 0.4)],
              [(ymn, gp.GRID, 0.2, 0.45), (ymd, gp.GRID, 0.4, 0.9), (ymj, gp.ACC, 0.6, 0.4)])


def s_loglog(ax, box):
    x0, x1, y0, y1 = box
    xmin, xmaj, nx, sx = _decade_positions(x0, x1, 0.95)
    ymin, ymaj, ny, sy = _decade_positions(y0, y1, 0.95)
    ax._sci_box = box
    _grid(ax, [(xmin, gp.GRID, 0.3, 0.6), (xmaj, gp.ACC, 0.6, 0.5)],
              [(ymin, gp.GRID, 0.3, 0.6), (ymaj, gp.ACC, 0.6, 0.5)])
    for d in range(nx + 1):
        ax.text(x0 + d * sx, y0 - 0.16, f"10{_sup(d)}", ha="center", va="top",
                fontproperties=SERIF, fontsize=7, color=gp.ACC)
    for d in range(ny + 1):
        ax.text(x0 - 0.12, y0 + d * sy, f"10{_sup(d)}", ha="right", va="center",
                fontproperties=SERIF, fontsize=7, color=gp.ACC)


def s_semilog(ax, box):
    x0, x1, y0, y1 = box
    s = 0.25
    xs = np.arange(x0, x1 + 1e-6, s)
    xmin = [x for x in xs if round((x - x0) / s) % 5]
    xmaj = [x for x in xs if round((x - x0) / s) % 5 == 0]
    ymin, ymaj, ny, sy = _decade_positions(y0, y1, 0.95)
    ax._sci_box = box
    _grid(ax, [(xmin, gp.GRID, 0.3, 0.6), (xmaj, gp.ACC, 0.5, 0.4)],
              [(ymin, gp.GRID, 0.3, 0.6), (ymaj, gp.ACC, 0.55, 0.45)])
    for d in range(ny + 1):
        ax.text(x0 - 0.12, y0 + d * sy, f"10{_sup(d)}", ha="right", va="center",
                fontproperties=SERIF, fontsize=7, color=gp.ACC)
    ax.text((x0 + x1) / 2, y0 - 0.18, "linear  →", ha="center", va="top",
            fontproperties=SERIF, fontsize=7.5, color=gp.ACC)


def s_cartesian(ax, box):
    x0, x1, y0, y1 = box
    s = 0.25
    cx = x0 + round((x1 - x0) / 2 / s) * s
    cy = y0 + round((y1 - y0) / 2 / s) * s
    xs = np.arange(x0, x1 + 1e-6, s); ys = np.arange(y0, y1 + 1e-6, s)
    ax._sci_box = box
    _grid(ax, [(list(xs), gp.GRID, 0.35, 0.8)], [(list(ys), gp.GRID, 0.35, 0.8)])
    # bold axes with arrowheads
    ax.annotate("", xy=(x1, cy), xytext=(x0, cy),
                arrowprops=dict(arrowstyle="-|>", color=gp.TXT, lw=1.3))
    ax.annotate("", xy=(cx, y1), xytext=(cx, y0),
                arrowprops=dict(arrowstyle="-|>", color=gp.TXT, lw=1.3))
    ax.text(x1 - 0.05, cy - 0.16, "x", fontproperties=SERIF, fontsize=11, color=gp.TXT)
    ax.text(cx + 0.1, y1 - 0.08, "y", fontproperties=SERIF, fontsize=11, color=gp.TXT)
    unit = 4 * s                                # one labelled unit = 1 inch
    k = 1
    while cx + k * unit <= x1 - 0.1 or cx - k * unit >= x0 + 0.1:
        for sgn in (1, -1):
            x = cx + sgn * k * unit
            if x0 + 0.05 < x < x1 - 0.05:
                ax.plot([x, x], [cy - 0.05, cy + 0.05], color=gp.TXT, lw=1.0)
                ax.text(x, cy - 0.14, f"{sgn*k}", ha="center", va="top",
                        fontproperties=SERIF, fontsize=7, color=gp.TXT)
            y = cy + sgn * k * unit
            if y0 + 0.05 < y < y1 - 0.05:
                ax.plot([cx - 0.05, cx + 0.05], [y, y], color=gp.TXT, lw=1.0)
                ax.text(cx - 0.1, y, f"{sgn*k}", ha="right", va="center",
                        fontproperties=SERIF, fontsize=7, color=gp.TXT)
        k += 1


def s_polar_deg(ax, box):
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) / 2 * 0.94
    rings = 10
    for i in range(1, rings + 1):
        ax.add_patch(plt.Circle((cx, cy), R * i / rings, fill=False, edgecolor=gp.GRID,
                                lw=0.6 if i % 5 == 0 else 0.35, alpha=0.9))
    for deg in range(0, 360, 15):
        a = math.radians(deg)
        lw = 0.65 if deg % 90 == 0 else 0.45 if deg % 45 == 0 else 0.3
        ax.plot([cx, cx + R * math.cos(a)], [cy, cy + R * math.sin(a)],
                color=gp.GRID, lw=lw, alpha=0.9)
    for deg in range(0, 360, 30):
        a = math.radians(deg)
        ax.text(cx + (R + 0.2) * math.cos(a), cy + (R + 0.2) * math.sin(a),
                f"{deg}°", ha="center", va="center", fontproperties=SERIF,
                fontsize=7, color=gp.ACC)


def s_logpolar(ax, box):
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) / 2 * 0.94
    ndec = 4
    for d in range(ndec + 1):
        for m in range(1, 10):
            if d == ndec and m > 1:
                break
            rr = R * (d + math.log10(m)) / ndec
            if rr <= 0:
                continue
            ax.add_patch(plt.Circle((cx, cy), rr, fill=False,
                         edgecolor=gp.ACC if m == 1 else gp.GRID,
                         lw=0.6 if m == 1 else 0.3, alpha=0.5 if m == 1 else 0.7))
    for deg in range(0, 360, 15):
        a = math.radians(deg)
        lw = 0.55 if deg % 45 == 0 else 0.3
        ax.plot([cx, cx + R * math.cos(a)], [cy, cy + R * math.sin(a)],
                color=gp.GRID, lw=lw, alpha=0.9)


def s_isometric(ax, box):
    gp.s_isometric(ax, box)                    # reuse the aesthetic line's 3D grid


def _sup(n):
    return str(n).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))


# ---- registry + render ------------------------------------------------------
STYLES = {
    "Engineering 5x5": s_engineering,
    "Millimeter": s_millimeter,
    "Log-Log": s_loglog,
    "Semi-Log": s_semilog,
    "Cartesian Plane": s_cartesian,
    "Polar (degrees)": s_polar_deg,
    "Log-Polar": s_logpolar,
    "Isometric 3D": s_isometric,
}
ORDER = list(STYLES.keys())


def render_fig(style, size=LETTER, dpi=90):
    W, H = size
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    fig.patch.set_facecolor(gp.PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(gp.PAPER); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    gp.header(ax, style, W, H)
    STYLES[style](ax, gp.region(W, H))
    return fig


if __name__ == "__main__":
    import io
    from PIL import Image, ImageDraw
    imgs = []
    for name in ORDER:
        fig = render_fig(name)
        b = io.BytesIO(); fig.savefig(b, format="png", facecolor=gp.PAPER, dpi=90)
        plt.close(fig); b.seek(0)
        imgs.append((name, Image.open(b).convert("RGB")))
    cols, rows = 4, 2
    pad, lab = 10, 20
    iw, ih = imgs[0][1].size
    cw, ch = iw, ih + lab
    sheet = Image.new("RGB", (cols * cw + pad * (cols + 1), rows * ch + pad * (rows + 1)), "#fff")
    d = ImageDraw.Draw(sheet)
    for i, (nm, im) in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad); y = pad + r * (ch + pad)
        sheet.paste(im, (x, y + lab)); d.text((x + 4, y + 6), nm, fill="#111")
    out = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/scigrid_all.png"
    sheet.save(out); print("OK", out, sheet.size)
