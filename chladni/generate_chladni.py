"""
generate_chladni.py — Chladni figure art prints (Type-5 catalogue print).
=========================================================================
Chladni figures are the nodal lines of the standing waves on a vibrating
plate — the curves where sand settles because the plate is still. Two plate
geometries:

  SQUARE plate (Ritz approximation):
      W(x,y) = cos(nπx)cos(mπy) − cos(mπx)cos(nπy)     nodes: W = 0
  CIRCULAR plate ("the rings of power", Bessel modes):
      W(r,θ) = J_n(k·r)·cos(nθ)     with k = s-th zero of J_n
      → concentric rings (Bessel zeros) + 2n radial spokes

Rendering matches the shop's Type-5 look: the nodal "sand" glows in cream/gold
on the brand navy, with a soft bloom — the same density/glow language as the
attractor and harmonograph prints. The nodal set is drawn as a uniform-width
luminous line using the |W| / |∇W| distance-to-zero estimate.

  python generate_chladni.py --sheet    # contact sheet of many modes (review)
  python generate_chladni.py            # (later) full poster renders
"""
import os
import sys
import numpy as np
from scipy.special import jv, jn_zeros
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
NAVY = np.array([13, 17, 36], float)
SAND = np.array([242, 230, 196], float)     # warm cream/gold
GOLD = np.array([201, 162, 75], float)


# ── Field functions ───────────────────────────────────────────────────────────

def square_field(n, m, N=1000, a=1.0, b=1.0):
    xs = np.linspace(0, 1, N)
    X, Y = np.meshgrid(xs, xs)
    W = (a * np.cos(n * np.pi * X) * np.cos(m * np.pi * Y)
         - b * np.cos(m * np.pi * X) * np.cos(n * np.pi * Y))
    return W, None


def circular_field(n, s, N=1000):
    xs = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(xs, xs)
    R = np.hypot(X, Y)
    TH = np.arctan2(Y, X)
    k = jn_zeros(n, s)[-1]                    # s-th zero of J_n -> rim is a node
    W = jv(n, k * R) * np.cos(n * TH)
    mask = R <= 1.0
    W = np.where(mask, W, np.nan)
    return W, mask


# ── Nodal-line rendering (luminous sand on navy) ─────────────────────────────

def nodal_image(W, mask=None, line=1.6, glow=True, color=SAND):
    N = W.shape[0]
    Wf = np.nan_to_num(W, nan=1e3)
    gy, gx = np.gradient(Wf, 1.0 / N)
    dist = np.abs(Wf) / (np.hypot(gx, gy) + 1e-6)      # ~distance to nodal set
    lw = line / N                                       # line half-width (field units)
    bright = np.exp(-(dist / lw) ** 2)
    if mask is not None:
        bright = np.where(mask, bright, 0.0)

    rgb = NAVY[None, None, :] + bright[..., None] * (color - NAVY)[None, None, :]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    if glow:
        g = (bright[..., None] * color[None, None, :])
        gi = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
        blur = gi.filter(ImageFilter.GaussianBlur(max(1, N // 300)))
        base = np.asarray(img, float)
        bl = np.asarray(blur, float)
        screen = 255 - (255 - base) * (255 - bl) / 255.0
        img = Image.fromarray(np.clip(screen, 0, 255).astype(np.uint8))
    # circular plate: keep the navy outside the disk
    if mask is not None:
        arr = np.asarray(img).copy()
        arr[~mask] = NAVY.astype(np.uint8)
        img = Image.fromarray(arr)
    return img


# ── Realistic "sand on a dark plate" rendering ───────────────────────────────

PLATE = np.array([11, 12, 18], float)       # near-black plate (slight navy)
GRAIN = np.array([233, 227, 210], float)    # warm off-white sand


def render_sand(W, mask=None, line=2.4, gamma=1.4, grain_passes=14, seed=0,
                plate=PLATE, sand=GRAIN):
    """Scatter sand grains that pile up on the nodal set, on a textured dark
    plate — the look of a real Chladni experiment."""
    N = W.shape[0]
    rng = np.random.default_rng(seed)
    Wf = np.nan_to_num(W, nan=1e3)
    gy, gx = np.gradient(Wf, 1.0 / N)
    dist = np.abs(Wf) / (np.hypot(gx, gy) + 1e-6)
    lw = line / N
    dens = np.exp(-(dist / lw) ** 2)                 # 0..1 proximity to a node
    if mask is not None:
        dens = np.where(mask, dens, 0.0)
    prob = dens ** gamma

    # scatter grains by rejection sampling, accumulate with a tiny splat
    acc = np.zeros((N, N), float)
    M = N * N // 3
    for _ in range(grain_passes):
        xs = rng.integers(0, N, M); ys = rng.integers(0, N, M)
        keep = rng.random(M) < prob[ys, xs]
        xk, yk = xs[keep], ys[keep]
        w = 0.6 + 0.8 * rng.random(xk.size)          # per-grain brightness
        np.add.at(acc, (yk, xk), w)
    from scipy.ndimage import gaussian_filter
    acc = gaussian_filter(acc, 0.6)
    sand_amt = np.clip(acc / np.percentile(acc[acc > 0], 92) if (acc > 0).any() else acc, 0, 1)
    # a faint packed core so the lines never break up entirely
    sand_amt = np.clip(sand_amt + 0.22 * dens, 0, 1)

    # textured plate: brushed noise + radial vignette
    tex = rng.normal(0, 6, (N, N))
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N / 2, yy - N / 2) / (N / 2)
    vig = np.clip(1.0 - 0.35 * r ** 2, 0, 1)
    base = plate[None, None, :] * vig[..., None] + tex[..., None]

    grain_tint = sand[None, None, :] * (0.85 + 0.15 * rng.random((N, N, 1)))
    out = base + sand_amt[..., None] * (grain_tint - base)
    img = np.clip(out, 0, 255).astype(np.uint8)
    if mask is not None:
        img[~mask] = plate.astype(np.uint8)
    return Image.fromarray(img)


# ── Contact sheet of modes ───────────────────────────────────────────────────

def contact_sheet(out=os.path.join(BASE, "_chladni_sheet.png")):
    modes = [
        ("sq", 2, 3), ("sq", 3, 4), ("sq", 4, 5), ("sq", 2, 5),
        ("sq", 5, 6), ("sq", 3, 7),
        ("ci", 0, 3), ("ci", 1, 3), ("ci", 2, 3), ("ci", 3, 4),
        ("ci", 4, 3), ("ci", 5, 4),
    ]
    cell = 360
    tiles = []
    for kind, a, b in modes:
        if kind == "sq":
            W, mask = square_field(a, b, N=cell)
        else:
            W, mask = circular_field(a, b, N=cell)
        tiles.append(nodal_image(W, mask, line=1.5).resize((cell, cell), Image.LANCZOS))
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    gap = 8
    sheet = Image.new("RGB", (cols * cell + (cols + 1) * gap,
                              rows * cell + (rows + 1) * gap), (40, 44, 60))
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (cell + gap), gap + r * (cell + gap)))
    sheet.save(out)
    print("Guardado:", out)


if __name__ == "__main__":
    if "--sheet" in sys.argv:
        contact_sheet()
    else:
        contact_sheet()
