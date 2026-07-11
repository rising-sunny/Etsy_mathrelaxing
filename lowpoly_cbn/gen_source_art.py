"""
gen_source_art.py — vibrant, original generative math art to feed the
color-by-number core. Domain colouring of a complex rational map: the phase
becomes hue and the magnitude modulates brightness, giving smooth rainbow
regions that quantise into clean, distinct colour-by-number bands.
100% generated here — no external/stock imagery, so it's copyright-clean.
"""
import numpy as np
from PIL import Image
from matplotlib.colors import hsv_to_rgb


def domain_coloring(out_path, size=2000, span=2.4):
    x = np.linspace(-span, span, size)
    y = np.linspace(-span, span, size)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    # a rational map with a few zeros and poles -> several petal regions
    f = (Z**3 - 1) / (Z**2 + (0.35 + 0.5j))
    f *= np.exp(1j * 0.6)                      # rotate the hue wheel a touch

    arg = np.angle(f)
    mag = np.abs(f)
    hue = (arg + np.pi) / (2 * np.pi)
    sat = np.full_like(hue, 0.72)
    # bright, smooth value from magnitude (log-compressed), never fully dark
    val = 0.45 + 0.5 * (np.arctan(np.log1p(mag)) / (np.pi / 2))
    rgb = hsv_to_rgb(np.dstack([hue, sat, np.clip(val, 0, 1)]))
    img = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    img.save(out_path, dpi=(300, 300))
    return out_path


if __name__ == "__main__":
    import os
    p = os.path.join(os.path.dirname(__file__), "source_domain_coloring.png")
    domain_coloring(p)
    print("wrote", p)
