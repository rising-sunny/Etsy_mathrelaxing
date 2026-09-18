"""Optical-illusion puzzle masters: the op-art distortion fields rendered
full-bleed in landscape 5:4 (2900x2320) for jigsaw puzzles. High-contrast
monochrome — the classic Vasarely / Bridget Riley look, which doubles as the
"hardest / most hypnotic puzzle" hook.

  python gen_opart_puzzle.py
"""
import os
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)

# 5:4 landscape, supersampled
W, H = 2900, 2320
SS = 2
BW, BH = W * SS, H * SS
A = W / H  # aspect
INK = np.array([16, 17, 20], float)
PAPER = np.array([245, 242, 235], float)


def coords():
    y = np.linspace(-1, 1, BH)[:, None]
    x = np.linspace(-A, A, BW)[None, :]
    return x + 0 * y, y + 0 * x


def smooth(field):
    gx = np.abs(np.gradient(field, axis=1))
    gy = np.abs(np.gradient(field, axis=0))
    g = np.maximum(gx + gy, 1e-6)
    return np.clip(0.5 + field / (2.0 * g), 0, 1)


def save(field, name):
    inten = smooth(field)[:, :, None]
    arr = (INK * (1 - inten) + PAPER * inten).astype(np.uint8)
    im = Image.fromarray(arr, "RGB").resize((W, H), Image.LANCZOS)
    im.save(os.path.join(MAST, f"{name}.jpg"), quality=95)
    print("wrote", name)


# ---- fields (tuned for the wider frame) --------------------------------
def f_sphere():
    """Vasarely 'Vega' — grid bulging like a sphere."""
    x, y = coords()
    r = np.sqrt(x * x + y * y)
    bulge = 0.60 * np.exp(-(r / 0.70) ** 2)
    u = x * (1 - bulge); v = y * (1 - bulge)
    freq = 15 * np.pi
    return np.sin(freq * u) * np.sin(freq * v)


def f_vortex():
    """concentric rings dragged into a spiral -> rotation illusion."""
    x, y = coords()
    r = np.sqrt(x * x + y * y); th = np.arctan2(y, x)
    return np.sin(24 * r * np.pi + 7 * th)


def f_wave():
    """Bridget Riley 'Fall' — parallel curves compressing to a vibration."""
    x, y = coords()
    return np.sin(26 * (y + 0.42 * np.sin(1.9 * x) * np.exp(-(x ** 2) * 0.25)))


def f_moire():
    """two fine gratings crossed -> shimmering moiré."""
    x, y = coords()
    a = np.sin(40 * x + 6 * np.sin(1.3 * y))
    b = np.sin(40 * (x * np.cos(0.06) - y * np.sin(0.06)))
    return a * b


def f_flare():
    """radial wedges modulated by rings -> flicker at the center."""
    x, y = coords()
    r = np.sqrt(x * x + y * y); th = np.arctan2(y, x)
    return np.sin(44 * th) * np.sin(26 * r * np.pi)


def f_bulgesq():
    """nested square rings with a twist -> pinched-square spiral."""
    x, y = coords()
    d = np.maximum(np.abs(x), np.abs(y)); th = np.arctan2(y, x)
    return np.sin(22 * d * np.pi + 6 * th)


DESIGNS = [
    ("sphere", f_sphere),
    ("vortex", f_vortex),
    ("wave", f_wave),
    ("moire", f_moire),
    ("flare", f_flare),
    ("square", f_bulgesq),
]


def build():
    for slug, fn in DESIGNS:
        save(fn(), slug)


if __name__ == "__main__":
    build()
