"""
art_gallery.py — original generative math-art sources for the color-by-number
book. Three families, all generated numerically (copyright-clean) and chosen so
they quantise into clean, distinct colour-by-number bands:

  * domain colouring of complex maps   (smooth rainbow regions)
  * Newton-fractal basins              (crisp fractal region boundaries)
  * escape-time Julia sets             (organic filaments, vivid colour bands)
"""
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb


def _grid(size, span, cx=0.0, cy=0.0):
    x = np.linspace(cx - span, cx + span, size)
    y = np.linspace(cy - span, cy + span, size)
    X, Y = np.meshgrid(x, y)
    return X + 1j * Y


def _save(rgb01, out_path):
    Image.fromarray((np.clip(rgb01, 0, 1) * 255).astype(np.uint8), "RGB").save(
        out_path, dpi=(300, 300))
    return out_path


def domain_coloring(fn, out_path, size=1700, span=2.4, hue_shift=0.0, sat=0.72):
    Z = _grid(size, span)
    with np.errstate(all="ignore"):
        f = fn(Z)
    f = np.nan_to_num(f, nan=0.0, posinf=1e6, neginf=-1e6)
    hue = (np.angle(f * np.exp(1j * hue_shift)) + np.pi) / (2 * np.pi)
    val = 0.45 + 0.5 * (np.arctan(np.log1p(np.abs(f))) / (np.pi / 2))
    return _save(hsv_to_rgb(np.dstack([hue, np.full_like(hue, sat), np.clip(val, 0, 1)])), out_path)


def newton_fractal(roots, out_path, size=1700, span=1.6, iters=40, hue0=0.0):
    roots = np.array(roots, complex)
    coeffs = np.poly(roots)
    dcoeffs = np.polyder(coeffs)
    Z = _grid(size, span)
    speed = np.zeros(Z.shape)
    for _ in range(iters):
        with np.errstate(all="ignore"):
            step = np.polyval(coeffs, Z) / np.polyval(dcoeffs, Z)
        step = np.nan_to_num(step)
        Z = Z - step
        speed += np.abs(step) > 1e-3
    idx = np.argmin(np.abs(Z[..., None] - roots[None, None, :]), axis=-1)
    hue = (hue0 + idx / len(roots)) % 1.0
    val = 0.35 + 0.6 * (1 - speed / iters)
    return _save(hsv_to_rgb(np.dstack([hue, np.full_like(hue, 0.70), np.clip(val, 0.2, 1)])), out_path)


def julia(c, out_path, size=1700, span=1.55, iters=180, cmap="turbo"):
    """Escape-time Julia set with smooth (continuous) iteration colouring."""
    Z = _grid(size, span)
    niter = np.zeros(Z.shape)
    alive = np.ones(Z.shape, bool)
    for i in range(iters):
        Z[alive] = Z[alive] ** 2 + c
        escaped = alive & (np.abs(Z) > 4)
        with np.errstate(all="ignore"):
            niter[escaped] = i + 1 - np.log2(np.log2(np.abs(Z[escaped])))
        alive &= ~escaped
    # cyclic banding on sqrt(escape) -> colourful concentric rings that quantise
    # into clean colour-by-number bands (instead of one flat exterior colour).
    band = (np.sqrt(np.clip(np.nan_to_num(niter), 0, None)) * 0.16) % 1.0
    rgb = plt.get_cmap(cmap)(band)[..., :3]
    rgb[alive] = np.array([0.10, 0.08, 0.16])            # interior (non-escaping) colour
    return _save(rgb, out_path)


def build_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    r = lambda n: [np.exp(2j * np.pi * k / n) for k in range(n)]
    r_cubic = list(np.roots([1, 0, -2, 2]))              # z^3 - 2z + 2

    # (key, title, desc, builder, side_length, num_colors)
    pieces = [
        # ── domain colourings ───────────────────────────────────────────────
        ("trefoil", "Trefoil Field", "domain colouring of (z³−1)/(z²+c)",
         lambda p: domain_coloring(lambda z: (z**3 - 1) / (z**2 + (0.35 + 0.5j)), p, hue_shift=0.6), 90, 12),
        ("pentafoil", "Pentafoil Rosette", "domain colouring of z⁵−1",
         lambda p: domain_coloring(lambda z: z**5 - 1, p, span=1.6), 90, 10),
        ("dipole", "Dipole", "domain colouring of (z²−1)/(z²+1)",
         lambda p: domain_coloring(lambda z: (z**2 - 1) / (z**2 + 1), p, span=2.2, hue_shift=1.2), 94, 10),
        ("wave", "Standing Wave", "domain colouring of sin(z)",
         lambda p: domain_coloring(lambda z: np.sin(z * 1.4), p, span=3.0), 94, 12),
        ("quatrefoil", "Quatrefoil", "domain colouring of z⁴−1",
         lambda p: domain_coloring(lambda z: z**4 - 1, p, span=1.6, hue_shift=0.3), 90, 10),
        ("hexafoil", "Hexafoil Bloom", "domain colouring of z⁶−1",
         lambda p: domain_coloring(lambda z: z**6 - 1, p, span=1.6), 88, 12),
        ("poledance", "Pole & Zero", "domain colouring of z + 1/z",
         lambda p: domain_coloring(lambda z: z + 1 / z, p, span=2.6, hue_shift=0.9), 94, 10),
        ("tangent", "Tangent Tiles", "domain colouring of tan(z)",
         lambda p: domain_coloring(lambda z: np.tan(z), p, span=3.0), 92, 12),
        ("cubicwave", "Cubic Current", "domain colouring of z³ + z",
         lambda p: domain_coloring(lambda z: z**3 + z, p, span=1.9, hue_shift=1.5), 90, 11),
        ("essential", "Essential Whirl", "domain colouring of exp(1/z)",
         lambda p: domain_coloring(lambda z: np.exp(1 / z), p, span=1.1), 88, 12),
        ("mobius", "Möbius Flow", "domain colouring of (z−1)/(z+1)",
         lambda p: domain_coloring(lambda z: (z - 1) / (z + 1), p, span=2.4, hue_shift=2.0), 94, 10),
        # ── Newton basins ───────────────────────────────────────────────────
        ("newton3", "Newton Basins  z³−1", "Newton's-method basins of attraction",
         lambda p: newton_fractal(r(3), p, span=1.5), 84, 9),
        ("newton4", "Newton Basins  z⁴−1", "Newton's-method basins of attraction",
         lambda p: newton_fractal(r(4), p, span=1.5, hue0=0.1), 84, 10),
        ("newton5", "Newton Basins  z⁵−1", "Newton's-method basins of attraction",
         lambda p: newton_fractal(r(5), p, span=1.5, hue0=0.15), 84, 11),
        ("newton6", "Newton Basins  z⁶−1", "Newton's-method basins of attraction",
         lambda p: newton_fractal(r(6), p, span=1.5, hue0=0.05), 84, 12),
        ("newtoncubic", "Newton Basins  z³−2z+2", "the classic divergent cubic",
         lambda p: newton_fractal(r_cubic, p, span=2.2, hue0=0.3), 84, 10),
        ("newton8", "Newton Basins  z⁸−1", "Newton's-method basins of attraction",
         lambda p: newton_fractal(r(8), p, span=1.5, hue0=0.6), 82, 12),
        # ── Julia sets ──────────────────────────────────────────────────────
        ("julia_dendrite", "Julia · Dendrite", "escape-time Julia set, c = −0.4 + 0.6i",
         lambda p: julia(-0.4 + 0.6j, p), 88, 11),
        ("julia_spiral", "Julia · Spiral", "escape-time Julia set, c = 0.285 + 0.01i",
         lambda p: julia(0.285 + 0.01j, p, span=1.5), 88, 11),
        ("julia_swirl", "Julia · Swirl", "escape-time Julia set, c = −0.8 + 0.156i",
         lambda p: julia(-0.8 + 0.156j, p, span=1.6), 88, 12),
    ]
    made = []
    for key, title, desc, builder, side, ncol in pieces:
        src = os.path.join(out_dir, f"src_{key}.png")
        if not os.path.exists(src):
            builder(src)
        made.append({"key": key, "title": title, "desc": desc, "src": src,
                     "side": side, "colors": ncol})
    return made


if __name__ == "__main__":
    d = os.path.join(os.path.dirname(__file__), "pkg_src")
    for m in build_all(d):
        print(m["key"], "->", os.path.basename(m["src"]))
