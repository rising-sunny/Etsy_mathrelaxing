"""
generate_julia.py — Julia set art with smooth (continuous) escape-time colour.

For each pixel z0 in the complex plane we iterate z -> z^2 + c and colour by a
smooth iteration count through a vibrant cyclic palette — the glowing contour
bands of classic fractal art, computed exactly (no clip-art, no AI). Six iconic
constants c give six very different forms. Square output for square posters.

  python generate_julia.py            # all 6 at final res
  python generate_julia.py dragon --res 1400
"""
import os, sys
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)

# (slug, Name, constant c, half-width of the view window)
JULIAS = [
    ("dragon",   "Dragon",        complex(-0.8,  0.156),   1.55),
    ("rabbit",   "Douady Rabbit", complex(-0.123, 0.745),  1.45),
    ("spiral",   "Spiral",        complex(-0.70176, -0.3842), 1.55),
    ("dense",    "Filament",      complex(0.285,  0.01),   1.35),
    ("swirl",    "Swirl",         complex(-0.4,   0.6),    1.55),
    ("pinwheel", "Pinwheel",      complex(0.355,  0.355),  1.5),
]

# vibrant cyclic palette (indigo -> blue -> cyan -> green -> yellow -> orange -> red -> indigo)
_STOPS = [(0.00, "#0a0036"), (0.14, "#1b3bd0"), (0.30, "#00c8ff"), (0.45, "#22ffb0"),
          (0.60, "#f6ff2a"), (0.74, "#ff8a12"), (0.88, "#ff1e5a"), (1.00, "#0a0036")]
INTERIOR = np.array([6, 2, 20], np.float32)


def _ramp(n=1024):
    ps = np.array([p for p, _ in _STOPS])
    cs = np.array([[int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] for _, c in _STOPS], float)
    x = np.linspace(0, 1, n)
    lut = np.empty((n, 3))
    for k in range(3):
        lut[:, k] = np.interp(x, ps, cs[:, k])
    return lut.astype(np.float32)


_LUT = _ramp()


def render(c, res, half=1.5, max_iter=400, R=256.0, period=15.0):
    xs = np.linspace(-half, half, res).astype(np.float64)
    X, Y = np.meshgrid(xs, xs)
    Z = X + 1j * Y
    dt = np.zeros((res, res), np.float64)      # smooth divergence time
    m = np.ones((res, res), bool)              # still iterating
    for i in range(max_iter):
        Z[m] = Z[m] * Z[m] + c
        az = np.abs(Z)
        esc = m & (az > R)
        if esc.any():
            dt[esc] = i + 1.0 - np.log(np.log(az[esc])) / np.log(2.0)
        m &= ~esc
        if not m.any():
            break
    # colour: cyclic palette, one full cycle every `period` iterations — broad
    # glowing bands far out, tightening toward the set boundary (classic look)
    idx = ((dt / period) % 1.0) * (_LUT.shape[0] - 1)
    lo = idx.astype(np.int32); fr = (idx - lo)[..., None]
    col = _LUT[lo] * (1 - fr) + _LUT[np.minimum(lo + 1, _LUT.shape[0] - 1)] * fr
    col[m] = INTERIOR                          # never-escaped interior -> near-black
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")


def build(res=3000):
    for slug, name, c, half in JULIAS:
        print("rendering", slug, c)
        render(c, res, half=half).save(os.path.join(MAST, f"julia_{slug}.png"))
        print("  wrote julia_%s.png" % slug)


if __name__ == "__main__":
    argv = sys.argv[1:]; res = 3000
    if "--res" in argv:
        i = argv.index("--res"); res = int(argv[i + 1]); del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if args:
        d = {s: (s, n, c, h) for s, n, c, h in JULIAS}[args[0]]
        render(d[2], res, half=d[3]).save(os.path.join(MAST, f"julia_{d[0]}.png"))
        print("wrote", d[0], "@", res)
    else:
        build(res)
