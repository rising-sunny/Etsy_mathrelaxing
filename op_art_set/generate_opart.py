"""
generate_opart.py — "Kinetic" op-art line: high-contrast geometric illusions
generated from parametric distortion fields (Vasarely / Bridget Riley lineage).

Every image is a numpy scalar field mapped to ink/paper through a smooth
threshold (analytic anti-aliasing), so the moving-eye illusions are exact and
razor-sharp at any print size. Blue-ocean niche, premium price, pure code moat.

Output: 2:3 masters at 2400x3600 -> masters/.
  python generate_opart.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)
AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")

W, H = 2400, 3600
SS = 2
BW, BH = W * SS, H * SS
INK = np.array([17, 18, 20], float)
PAPER = np.array([244, 241, 234], float)
GOLD = (201, 161, 67)


def font(name, size):
    return ImageFont.truetype(os.path.join(AF, name), size)


def coords():
    """normalized coords; x in [-a,a], y in [-1,1] (a = aspect/…), origin center."""
    y = np.linspace(-1, 1, BH)[:, None]
    x = np.linspace(-W / H, W / H, BW)[None, :]
    return x + 0 * y, y + 0 * x


def smooth(field):
    """map a signed field to [0,1] ink/paper with edge AA proportional to the
    field's local slope (keeps fine stripes crisp, not aliased)."""
    gx = np.abs(np.gradient(field, axis=1))
    gy = np.abs(np.gradient(field, axis=0))
    g = np.maximum(gx + gy, 1e-6)
    return np.clip(0.5 + field / (2.0 * g), 0, 1)


def render(field, name, caption):
    inten = smooth(field)[:, :, None]
    arr = (INK * (1 - inten) + PAPER * inten).astype(np.uint8)
    im = Image.fromarray(arr, "RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    m = int(W * 0.05)
    d.rectangle((m, m, W - m, H - m), outline=(214, 206, 190), width=3)
    # caption plate
    d.rectangle((m, int(H * 0.912), W - m, H - m), fill=tuple(PAPER.astype(int)))
    d.line((m, int(H * 0.912), W - m, int(H * 0.912)), fill=(214, 206, 190), width=3)
    d.text((W // 2, int(H * 0.945)), caption, font=font("Cinzel-SemiBold.ttf", 46),
           fill=(24, 24, 28), anchor="mm")
    d.text((W // 2, int(H * 0.972)), "KINETIC · MathRelaxing", font=font("Raleway-Italic.ttf", 24),
           fill=(150, 144, 132), anchor="mm")
    im.save(os.path.join(MAST, f"{name}.png"))
    print("wrote", name)


# ---- fields ------------------------------------------------------------
def f_bombe():
    """Vasarely 'Vega' — a grid bulging like a sphere."""
    x, y = coords()
    r = np.sqrt(x * x + y * y)
    bulge = 0.55 * np.exp(-(r / 0.62) ** 2)
    u = x * (1 - bulge); v = y * (1 - bulge)
    freq = 15 * np.pi
    return np.sin(freq * u) * np.sin(freq * v)


def f_moire():
    """two fine line gratings crossed -> shimmering moiré."""
    x, y = coords()
    a = np.sin(46 * x + 6 * np.sin(1.4 * y))
    b = np.sin(46 * (x * np.cos(0.06) - y * np.sin(0.06)))
    return a * b


def f_vortex():
    """concentric rings dragged into a spiral -> rotation illusion."""
    x, y = coords()
    r = np.sqrt(x * x + y * y); th = np.arctan2(y, x)
    return np.sin(26 * r * np.pi + 6 * th)


def f_wavefield():
    """Bridget Riley 'Fall' — parallel curves compressing to a vibration."""
    x, y = coords()
    return np.sin(30 * (y + 0.42 * np.sin(2.3 * x) * np.exp(-((x) ** 2) * 0.3)))


def f_flicker():
    """radial wedges modulated by rings -> flicker at the center."""
    x, y = coords()
    r = np.sqrt(x * x + y * y); th = np.arctan2(y, x)
    return np.sin(40 * th) * np.sin(30 * r * np.pi)


def f_squares():
    """nested square rings with a twist -> pinched-square spiral."""
    x, y = coords()
    d = np.maximum(np.abs(x), np.abs(y)); th = np.arctan2(y, x)
    return np.sin(24 * d * np.pi + 5 * th)


def build():
    render(f_bombe(), "01_vega", "VEGA")
    render(f_moire(), "02_moire", "MOIRE")
    render(f_vortex(), "03_vortex", "VORTEX")
    render(f_wavefield(), "04_fall", "FALL")
    render(f_flicker(), "05_flare", "FLARE")
    render(f_squares(), "06_quanta", "QUANTA")


if __name__ == "__main__":
    build()
