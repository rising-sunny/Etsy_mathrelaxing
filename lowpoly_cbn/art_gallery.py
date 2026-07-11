"""
art_gallery.py — a small library of original generative math-art sources for
the color-by-number package. Two families:

  * domain colouring of complex maps  (smooth rainbow regions)
  * Newton-fractal basins             (crisp fractal region boundaries)

Everything is generated numerically here, so it is copyright-clean and
quantises into clean colour-by-number bands.
"""
import numpy as np
from PIL import Image
from matplotlib.colors import hsv_to_rgb


def _grid(size, span):
    x = np.linspace(-span, span, size)
    y = np.linspace(-span, span, size)
    X, Y = np.meshgrid(x, y)
    return X + 1j * Y


def domain_coloring(fn, out_path, size=1800, span=2.4, hue_shift=0.0, sat=0.72):
    Z = _grid(size, span)
    with np.errstate(all="ignore"):
        f = fn(Z)
    f = np.nan_to_num(f, nan=0.0, posinf=1e6, neginf=-1e6)
    hue = (np.angle(f * np.exp(1j * hue_shift)) + np.pi) / (2 * np.pi)
    val = 0.45 + 0.5 * (np.arctan(np.log1p(np.abs(f))) / (np.pi / 2))
    rgb = hsv_to_rgb(np.dstack([hue, np.full_like(hue, sat), np.clip(val, 0, 1)]))
    Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(out_path, dpi=(300, 300))
    return out_path


def newton_fractal(roots, out_path, size=1800, span=1.6, iters=40, hue0=0.0):
    """Newton's method basins for the polynomial with the given complex roots.
    Hue = which root you land in; brightness = how fast you converged."""
    roots = np.array(roots, complex)
    # polynomial coeffs from roots, and derivative
    coeffs = np.poly(roots)
    dcoeffs = np.polyder(coeffs)
    Z = _grid(size, span)
    speed = np.zeros(Z.shape)
    for k in range(iters):
        fz = np.polyval(coeffs, Z)
        dfz = np.polyval(dcoeffs, Z)
        with np.errstate(all="ignore"):
            step = fz / dfz
        step = np.nan_to_num(step)
        Z = Z - step
        moving = np.abs(step) > 1e-3
        speed += moving
    # nearest root index
    d = np.abs(Z[..., None] - roots[None, None, :])
    idx = np.argmin(d, axis=-1)
    hue = (hue0 + idx / len(roots)) % 1.0
    val = 0.35 + 0.6 * (1 - speed / iters)
    sat = np.full_like(hue, 0.70)
    rgb = hsv_to_rgb(np.dstack([hue, sat, np.clip(val, 0.2, 1)]))
    Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(out_path, dpi=(300, 300))
    return out_path


# ── the gallery: (key, title, builder, cells side length, num colours) ────────
def build_all(out_dir):
    import os
    os.makedirs(out_dir, exist_ok=True)
    r5 = [np.exp(2j * np.pi * k / 5) for k in range(5)]
    r4 = [1, -1, 1j, -1j]
    r3 = [np.exp(2j * np.pi * k / 3) for k in range(3)]
    pieces = [
        ("trefoil", "Trefoil Field",
         lambda p: domain_coloring(lambda z: (z**3 - 1) / (z**2 + (0.35 + 0.5j)), p, hue_shift=0.6), 88, 12),
        ("rosette5", "Pentafoil Rosette",
         lambda p: domain_coloring(lambda z: z**5 - 1, p, span=1.6), 88, 10),
        ("dipole", "Dipole",
         lambda p: domain_coloring(lambda z: (z**2 - 1) / (z**2 + 1), p, span=2.2, hue_shift=1.2), 92, 10),
        ("wave", "Standing Wave",
         lambda p: domain_coloring(lambda z: np.sin(z * 1.4), p, span=3.0), 92, 12),
        ("newton3", "Newton Basins  z³−1",
         lambda p: newton_fractal(r3, p, span=1.5), 82, 9),
        ("newton5", "Newton Basins  z⁵−1",
         lambda p: newton_fractal(r5, p, span=1.5, hue0=0.15), 82, 11),
    ]
    made = []
    for key, title, builder, side, ncol in pieces:
        src = os.path.join(out_dir, f"src_{key}.png")
        builder(src)
        made.append({"key": key, "title": title, "src": src, "side": side, "colors": ncol})
    return made


if __name__ == "__main__":
    import os
    d = os.path.join(os.path.dirname(__file__), "pkg_src")
    for m in build_all(d):
        print(m["key"], "->", m["src"])
