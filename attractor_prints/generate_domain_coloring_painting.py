"""
generate_domain_coloring_painting.py
======================================
A flow-painting-line piece from a genuinely different branch of mathematics:
complex analysis, not dynamics. Every previous piece in this line (potential
flow singularities, sinusoidal wave interference, the Clifford strange
attractor) is a single-hue glow built from either a vector field or an
iterated map. This one has no field, no trajectory, no iteration at all —
just one closed-form complex function evaluated once per pixel.

Domain coloring: for a rational function f(z) with hand-placed zeros and
poles, colour each point z by

    hue        = arg(f(z))                      -- full hue wheel, not one accent colour
    brightness = fractional part of log2|f(z)|   -- concentric "shell" contours around
                                                      every zero/pole, one band per octave

This is also the shop's first full-colour piece (everything else is a single
gradient on black) — reads as iridescent abalone shell / oil-slick opal
rather than a glowing swirl.

  python attractor_prints/generate_domain_coloring_painting.py            # full 9000x12000
  python attractor_prints/generate_domain_coloring_painting.py --test     # quick low-res
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from matplotlib.colors import hsv_to_rgb
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "domain_coloring")

TEST = "--test" in sys.argv
W, H = (900, 1200) if TEST else (9000, 12000)

# Complex window (matches the 30x40 poster aspect at 0.75).
RE_HALF, IM_HALF = 4.5, 6.0

# Hand-placed zeros/poles (each: complex location, multiplicity). Multiplicity
# > 1 tightens the hue spiral around that point (more colour wraps per ring),
# giving some features a busier rosette and others a calmer single swirl --
# same "vary strength/kind to fill the canvas" idea as the flow paintings'
# singularities, just for a complex rational function instead of a vector field.
ZEROS = [
    (0 + 0j,          1),
    (2.6 + 3.4j,      2),
    (-2.3 - 1.2j,     1),
    (-3.0 + 4.2j,     1),
]
POLES = [
    (-3.2 + 2.0j,     1),
    (3.0 - 3.6j,      2),
    (0.3 + 5.3j,      1),
    (2.4 - 0.8j,      1),
]

SATURATION = 0.66
VALUE_MID = 0.40
VALUE_AMP = 0.36
RING_PERIOD = 1.6    # octaves of |f| per contour cycle -- bigger = fewer, calmer rings

# Restrict hue to a curated jewel-tone arc (blue -> violet -> magenta -> rose
# -> amber), deliberately skipping the yellow/green/cyan third of the wheel
# that makes a full 360 degree hue map read as a cheap neon rainbow.
HUE_START = 0.56
HUE_ARC = 0.55

PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def eval_f(Z):
    num = np.ones_like(Z)
    for z0, m in ZEROS:
        num = num * (Z - z0) ** m
    den = np.ones_like(Z)
    for z0, m in POLES:
        den = den * (Z - z0) ** m
    return num / den


def render():
    print(f"Evaluando f(z) en grilla {W}x{H}...")
    t0 = time.time()
    xs = np.linspace(-RE_HALF, RE_HALF, W, dtype=np.float64)
    ys = np.linspace(IM_HALF, -IM_HALF, H, dtype=np.float64)  # top row = +Im
    X, Y = np.meshgrid(xs, ys)
    Z = (X + 1j * Y).astype(np.complex128)

    W_ = eval_f(Z)
    del X, Y, Z

    t = (np.angle(W_) + np.pi) / (2 * np.pi)
    hue = (HUE_START + HUE_ARC * t) % 1.0
    modulus = np.abs(W_)
    del W_
    logm = np.log2(modulus + 1e-12)
    # A smooth sinusoidal contour (not a sawtooth) -- no hard ring edges,
    # reads as soft embossed shells instead of a target/bullseye pattern.
    value = VALUE_MID + VALUE_AMP * np.sin(2 * np.pi * logm / RING_PERIOD)
    sat = np.full_like(hue, SATURATION)

    hsv = np.stack([hue, sat, value], axis=-1).astype(np.float32)
    rgb = hsv_to_rgb(hsv)
    print(f"  color listo ({time.time()-t0:.1f}s)")

    img = Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))
    # Very mild blur -- softens per-pixel aliasing near zeros/poles into a
    # painterly finish without losing the crisp contour rings.
    blur_r = max(0.6, 0.9 * (W / 1080))
    img = img.filter(ImageFilter.GaussianBlur(blur_r))
    return img


def add_preview_watermark(img, text=WATERMARK_TEXT, opacity=46, angle=30):
    w, h = img.size
    font_size = max(20, int(w * 0.028))
    font = ImageFont.truetype(FONT_PATH, font_size)

    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(text, font=font))
    step_x, step_y = int(tw * 1.6), int(font_size * 5.5)

    tile = Image.new("RGBA", (step_x, step_y), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((step_x * 0.08, step_y * 0.28), text, font=font,
                              fill=(255, 255, 255, opacity))
    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(-tile.height, h, tile.height):
        for x in range(-tile.width, w, tile.width):
            layer.alpha_composite(tile, (x, y))

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def make_preview(print_img, preview_path):
    w, h = print_img.size
    scale = PREVIEW_LONG_EDGE / h
    preview = print_img.resize((int(w * scale), PREVIEW_LONG_EDGE), Image.LANCZOS)
    preview = add_preview_watermark(preview)
    preview.save(preview_path, quality=92)
    print("Guardado:", preview_path)


def main():
    os.makedirs(OUT, exist_ok=True)
    img = render()
    suffix = "_test" if TEST else ""
    out_path = os.path.join(OUT, f"domaincoloring_iridescent{suffix}_print.jpg")
    img.save(out_path, quality=98)
    print("Guardado:", out_path)
    make_preview(img, out_path.replace("_print.jpg", "_preview.jpg"))


if __name__ == "__main__":
    main()
