"""
build_chladni_poster.py — "Chladni Figures" collection poster (field guide).
Sand-on-dark-plate figures in a grid, with the governing equations, in the
same spirit as the Strange Attractors field-guide poster.

  python build_chladni_poster.py           # 18x24 in @ 300 dpi (5400x7200)
  python build_chladni_poster.py --test     # small & fast
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

import generate_chladni as ch

matplotlib.rcParams["mathtext.fontset"] = "cm"

BASE = ch.BASE
OUT = os.path.join(BASE, "collection")
PLATE = "#0b0c12"
CREAM = "#f2e6c4"
GOLD = "#c9a24b"
MUTED = (0.68, 0.66, 0.60)

TEST = "--test" in sys.argv
TILE_N = 460 if TEST else 2000
DPI = 100 if TEST else 380          # 18x24 @380 = 6840x9120 (more grain detail)

# 8 figures (mix of square & circular), each with a caption
FIGS = [
    ("sq", (2, 3), "Square plate", r"$(2,3)$"),
    ("ci", (0, 3), "Circular plate", r"$J_0,\ 3\ \mathrm{rings}$"),
    ("sq", (3, 5), "Square plate", r"$(3,5)$"),
    ("ci", (3, 4), "Circular plate", r"$J_3,\ 4\ \mathrm{rings}$"),
    ("sq", (4, 5), "Square plate", r"$(4,5)$"),
    ("ci", (4, 3), "Circular plate", r"$J_4,\ 3\ \mathrm{rings}$"),
    ("sq", (5, 6), "Square plate", r"$(5,6)$"),
    ("ci", (5, 4), "Circular plate", r"$J_5,\ 4\ \mathrm{rings}$"),
]


def render_tile(kind, params, seed):
    if kind == "sq":
        W, m = ch.square_field(*params, N=TILE_N)
    else:
        W, m = ch.circular_field(*params, N=TILE_N)
    return ch.sand_rgba(W, m, seed=seed)          # sand only, transparent bg


def _plate_bg(N=1500):
    """One shared, subtly textured dark plate for the whole poster (so figures
    float on a single continuous background, not on per-figure tiles)."""
    rng = np.random.default_rng(7)
    plate = np.array([11, 12, 18], float)
    tex = rng.normal(0, 4.5, (N, N, 1))
    img = np.clip(plate[None, None, :] + tex, 0, 255).astype(np.uint8)
    return img


def build():
    os.makedirs(OUT, exist_ok=True)
    W_IN, H_IN = 18.0, 24.0
    fig = plt.figure(figsize=(W_IN, H_IN))
    fig.patch.set_facecolor(PLATE)
    # single continuous plate background behind everything
    bgtex = fig.add_axes([0, 0, 1, 1]); bgtex.axis("off")
    bgtex.imshow(_plate_bg(), extent=(0, 1, 0, 1), aspect="auto", zorder=0)
    bgtex.set_xlim(0, 1); bgtex.set_ylim(0, 1)
    bg = fig.add_axes([0, 0, 1, 1], zorder=1); bg.axis("off")
    bg.patch.set_alpha(0.0)

    # ── header ──
    bg.text(0.5, 0.955, "C H L A D N I   F I G U R E S", ha="center", va="center",
            fontsize=34, color=CREAM, family="serif", fontweight="bold")
    bg.text(0.5, 0.928, "The Hidden Geometry of Sound", ha="center", va="center",
            fontsize=19, color=GOLD, family="serif", style="italic")
    bg.text(0.5, 0.906, "N O D A L   L I N E S   O F   A   V I B R A T I N G   P L A T E   ·   E. F. F.  C H L A D N I ,   1 7 8 7",
            ha="center", va="center", fontsize=9.5, color=MUTED, family="sans-serif")
    bg.plot([0.35, 0.65], [0.892, 0.892], color=GOLD, lw=0.8, alpha=0.5)

    # ── grid of figures (2 cols x 4 rows) ──
    cols, rows = 2, 4
    gx0, gx1 = 0.07, 0.93
    gy0, gy1 = 0.085, 0.86
    cw = (gx1 - gx0) / cols
    ch_ = (gy1 - gy0) / rows
    tile = 0.80 * min(cw, ch_ * 0.92)
    for i, (kind, params, name, label) in enumerate(FIGS):
        img = render_tile(kind, params, seed=i + 1)
        r, c = divmod(i, cols)
        ccx = gx0 + (c + 0.5) * cw
        ccy = gy1 - (r + 0.5) * ch_
        ax = fig.add_axes([ccx - tile / 2, ccy - tile / 2 + 0.012, tile, tile], zorder=2)
        ax.imshow(img); ax.axis("off"); ax.patch.set_alpha(0.0)
        bg.text(ccx, ccy - tile / 2 - 0.004, f"{name}   {label}",
                ha="center", va="top", fontsize=12.5, color=CREAM, family="serif")

    # ── footer: the two governing equations ──
    bg.plot([0.30, 0.70], [0.066, 0.066], color=GOLD, lw=0.6, alpha=0.4)
    bg.text(0.5, 0.048,
            r"$W_{\mathrm{square}}=\cos(n\pi x)\cos(m\pi y)-\cos(m\pi x)\cos(n\pi y)$"
            "        "
            r"$W_{\mathrm{disk}}=J_n(k\,r)\,\cos(n\theta)$",
            ha="center", va="center", fontsize=15, color=CREAM)
    bg.text(0.5, 0.028, "sand settles where the plate is still — on the curves W = 0",
            ha="center", va="center", fontsize=11, color=MUTED, family="serif", style="italic")

    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    suffix = "_test" if TEST else ""
    out_jpg = os.path.join(OUT, f"ChladniFigures{suffix}_print.jpg")
    fig.savefig(out_jpg, dpi=DPI, facecolor=PLATE, pil_kwargs={"quality": 94})
    plt.close(fig)
    full = Image.open(out_jpg)
    print("Guardado:", out_jpg, full.size)
    if not TEST:
        make_preview(full, os.path.join(OUT, "ChladniFigures_preview.jpg"))
        # two detail crops that show the sand grain up close
        w, h = full.size
        full.crop((int(w*0.06), int(h*0.14), int(w*0.50), int(h*0.36))).save(
            os.path.join(OUT, "ChladniFigures_detail1.jpg"), quality=92)
        full.crop((int(w*0.52), int(h*0.55), int(w*0.95), int(h*0.75))).save(
            os.path.join(OUT, "ChladniFigures_detail2.jpg"), quality=92)
        print("previews + detail crops listos")
    return out_jpg


def make_preview(full, out, long_edge=3000):
    w, h = full.size
    scale = long_edge / h
    prev = full.resize((int(w*scale), long_edge), Image.LANCZOS)
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    text = "MATHRELAXING.STORE  ·  PREVIEW"
    fs = max(20, int(prev.width * 0.030))
    font = ImageFont.truetype(font_path, fs)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(text, font=font))
    sx, sy = int(tw * 1.7), int(fs * 6.0)
    tile = Image.new("RGBA", (sx, sy), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((sx*0.08, sy*0.3), text, font=font, fill=(255, 255, 255, 40))
    tile = tile.rotate(30, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", prev.size, (0, 0, 0, 0))
    for yy in range(-tile.height, prev.height, tile.height):
        for xx in range(-tile.width, prev.width, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    Image.alpha_composite(prev.convert("RGBA"), layer).convert("RGB").save(out, quality=92)
    print("Guardado:", out)


if __name__ == "__main__":
    build()
