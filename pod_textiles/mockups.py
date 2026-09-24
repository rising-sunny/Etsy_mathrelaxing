"""Lifestyle / room mockups for the tapestry listings: the design shown as a
fabric wall hanging on a wooden dowel in a styled room (wall gradient, soft
light, drop shadow, a plant and a floor). Printify's own tapestry mockups are
plain product shots, so these add the "ambiente" scenes.

  python mockups.py                 # all designs -> mockups/<slug>_roomN.jpg
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PR = os.path.join(HERE, "prints")
OUT = os.path.join(HERE, "mockups"); os.makedirs(OUT, exist_ok=True)

# slug -> (print file, portrait aspect to crop to)
DESIGNS = {
    "julia_filament": "tex_julia_filament.jpg",
    "julia_spiral":   "tex_julia_spiral.jpg",
    "chaos_6":        "tex_chaos_6.jpg",
    "opart_vortex":   "tex_opart_vortex.jpg",
}
ASPECT = 0.74   # tapestry portrait


def crop_portrait(im, aspect=ASPECT):
    w, h = im.size
    tw = int(h * aspect)
    if tw <= w:
        x0 = (w - tw) // 2
        return im.crop((x0, 0, x0 + tw, h))
    th = int(w / aspect)
    y0 = (h - th) // 2
    return im.crop((0, y0, w, y0 + th))


def wall(W, H, top, bot, light=(0.10, 0.28)):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top) * (1 - g) + np.array(bot) * g)
    yy, xx = np.mgrid[0:H, 0:W]
    lx, ly = light
    r = np.sqrt(((xx / W) - lx * 0 - 0.5) ** 2 + ((yy / H) - ly) ** 2)
    glow = np.clip(1 - r * 1.1, 0, 1)[:, :, None] * 14
    arr = np.clip(arr + glow, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def fabric(design):
    """apply soft vertical wrinkles + top fold shading to the design."""
    w, h = design.size
    a = np.asarray(design).astype(np.float32)
    x = np.linspace(0, 1, w)
    wr = 1 + 0.05 * np.sin(2 * np.pi * x * 7 + 0.6) + 0.03 * np.sin(2 * np.pi * x * 17)
    shade = np.repeat(wr[None, :], h, axis=0)
    yy = np.linspace(0, 1, h)[:, None]
    shade *= (1 - 0.10 * np.exp(-(yy / 0.05) ** 2))        # fold under the rod
    shade *= (1 - 0.06 * yy)                               # gentle fall-off
    a = np.clip(a * shade[:, :, None], 0, 255).astype(np.uint8)
    return Image.fromarray(a, "RGB")


def add_shadow(base, box, blur=26, alpha=90, off=(16, 26)):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.rectangle((x0 + off[0], y0 + off[1], x1 + off[0], y1 + off[1]), fill=(20, 18, 16, alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def rod(base, x0, x1, y):
    d = ImageDraw.Draw(base)
    h = max(6, (x1 - x0) // 90)
    ext = int((x1 - x0) * 0.04)
    for i in range(h):
        t = i / h
        c = (int(120 - 40 * t), int(86 - 30 * t), int(54 - 20 * t), 255)
        d.line((x0 - ext, y + i, x1 + ext, y + i), fill=c)
    r = int(h * 0.9)
    for cx in (x0 - ext, x1 + ext):
        d.ellipse((cx - r, y - r + h // 2, cx + r, y + r + h // 2), fill=(92, 66, 42, 255))


def plant(base, W, H):
    """simple potted plant in the lower-left for ambiance."""
    d = ImageDraw.Draw(base)
    px, py = int(W * 0.12), int(H * 0.9)
    pw, ph = int(W * 0.12), int(H * 0.09)
    # pot
    d.polygon([(px - pw // 2, py), (px + pw // 2, py),
               (px + pw // 2 - pw // 8, py + ph), (px - pw // 2 + pw // 8, py + ph)],
              fill=(150, 96, 74))
    d.rectangle((px - pw // 2 - 4, py - 10, px + pw // 2 + 4, py + 6), fill=(168, 110, 86))
    # leaves
    rng = np.random.default_rng(4)
    for k in range(9):
        ang = math.radians(-90 + (k - 4) * 15 + rng.uniform(-5, 5))
        L = int(ph * (2.4 + rng.uniform(-0.3, 0.5)))
        wdt = int(pw * 0.16)
        tipx = px + int(math.cos(ang) * L)
        tipy = py - 8 + int(math.sin(ang) * L)
        midx = px + int(math.cos(ang) * L * 0.5) + rng.integers(-12, 12)
        midy = py - 8 + int(math.sin(ang) * L * 0.5)
        col = (54 + k * 3, 92 + k * 4, 58)
        d.polygon([(px, py - 8), (midx - wdt, midy), (tipx, tipy), (midx + wdt, midy)], fill=col)


def room(design, variant=1):
    W, H = 1680, 2100
    if variant == 1:
        base = wall(W, H, (219, 212, 200), (201, 193, 180)).convert("RGBA")
    else:
        base = wall(W, H, (208, 210, 213), (188, 190, 194)).convert("RGBA")
    # floor
    fh = int(H * 0.12)
    fl = Image.new("RGBA", (W, fh), (176, 158, 132, 255) if variant == 1 else (170, 168, 165, 255))
    base.alpha_composite(fl, (0, H - fh))
    d = ImageDraw.Draw(base)
    d.line((0, H - fh, W, H - fh), fill=(150, 135, 112, 255), width=3)

    tw = int(W * 0.56); th = int(tw / ASPECT)
    x0 = (W - tw) // 2; y0 = int(H * 0.10)
    add_shadow(base, (x0, y0, x0 + tw, y0 + th))
    tap = fabric(crop_portrait(design).resize((tw, th), Image.LANCZOS))
    base.alpha_composite(tap.convert("RGBA"), (x0, y0))
    rod(base, x0, x0 + tw, y0 - 10)
    if variant == 1:
        plant(base, W, H)
    return base.convert("RGB")


def build_one(slug):
    design = Image.open(os.path.join(PR, DESIGNS[slug])).convert("RGB")
    for v in (1, 2):
        room(design, v).save(os.path.join(OUT, f"{slug}_room{v}.jpg"), quality=90)
    print("mockups:", slug)


if __name__ == "__main__":
    for s in (sys.argv[1:] or DESIGNS):
        build_one(s)
