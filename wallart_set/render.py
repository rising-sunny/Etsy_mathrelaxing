"""
render.py — render a design into a given pixel size, framing the artwork to the
target aspect ratio with padded negative space (centered composition).
"""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import designs
from designs import DESIGNS, RATIOS


def render(name, px_w, px_h, pad=None, lw_scale=None):
    """Return a PIL RGB image (px_w x px_h) of design `name`, framed to that
    aspect ratio with the art centered and surrounded by negative space."""
    spec = DESIGNS[name]
    if pad is None:
        pad = spec["pad"]
    if lw_scale is None:
        # Keep line/point weight visually constant across output sizes; the
        # approved prototype was ~600px tall at scale 1.0.
        lw_scale = px_h / 600.0
    dpi = 100.0
    fig = plt.figure(figsize=(px_w / dpi, px_h / dpi), dpi=dpi)
    fig.patch.set_facecolor(designs.BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(designs.BG)
    ax.axis("off")
    ax.set_aspect("equal")

    xs, ys = spec["fn"](ax, lw_scale=lw_scale)
    xs = np.asarray(xs)
    ys = np.asarray(ys)

    # art bounding box + center
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx = max((x1 - x0) / 2, 1e-6) * pad
    hy = max((y1 - y0) / 2, 1e-6) * pad

    # window must have the pixel aspect ratio; grow the smaller side so the art
    # always fits, distributing the surplus as negative space.
    a = px_w / px_h                      # data-window width/height must equal this
    HH = max(hy, hx / a)
    WW = HH * a
    ax.set_xlim(cx - WW, cx + WW)
    ax.set_ylim(cy - HH, cy + HH)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=designs.BG, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


if __name__ == "__main__":
    # Verification montage: rows = designs, cols = ratios, small thumbnails.
    from PIL import ImageDraw
    names = list(DESIGNS.keys())
    ratio_keys = list(RATIOS.keys())
    TH = 300  # thumbnail height
    pad_px = 10
    lab = 22
    cells = []
    maxw = 0
    for nm in names:
        row = []
        for rk in ratio_keys:
            rw, rh = RATIOS[rk]
            pw = int(TH * rw / rh)
            im = render(nm, pw, TH)
            row.append((rk, im))
            maxw = max(maxw, pw)
        cells.append((nm, row))
    colw = maxw + pad_px
    cellh = TH + lab + pad_px
    sheet_w = pad_px + len(ratio_keys) * colw
    sheet_h = pad_px + len(names) * cellh + 24
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#ffffff")
    d = ImageDraw.Draw(sheet)
    for r, (nm, row) in enumerate(cells):
        y = 24 + pad_px + r * cellh
        d.text((pad_px, y - 16), nm, fill="#111")
        for c, (rk, im) in enumerate(row):
            x = pad_px + c * colw + (maxw - im.width) // 2
            if r == 0:
                d.text((pad_px + c * colw, 6), rk, fill="#333")
            sheet.paste(im, (x, y + lab // 2))
    out = "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/wallart/framing_check.png"
    sheet.save(out)
    print("FRAMING", out, sheet.size)
