"""
build_fractal_palettes.py — "Fractal Dreams" Procreate Color Palette pack
=========================================================================
Second ultra-low-cost palette product (sibling of build_palettes.py / Chaos
Theory). Same machine — real generative renders → 30-colour Procreate
.swatches — but a fresh, highly marketable theme: the two most iconic
fractals, the Mandelbrot and Julia sets (plus a Burning Ship), each rendered
with its own colour ramp so the eight palettes span the whole spectrum.

Reuses build_palettes.extract_palette / swatch_card and brand.swatches_file;
only the SOURCE images are new (rendered here from the escape-time algorithm).

Output in fractal_palettes/:
  swatches/<Name>.swatches        (sellable files, zipped)
  FractalDreams_Palettes.zip       (deliverable)
  previews/palette_*.jpg           (Etsy listing images)

  python build_fractal_palettes.py
"""
import os
import zipfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw

import brand
from build_palettes import extract_palette, swatch_card

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "fractal_palettes")
SW = os.path.join(OUT, "swatches")
PREV = os.path.join(OUT, "previews")
SRC = os.path.join(OUT, "_srcframes")


# ── Fractal renderer (smooth escape-time) ─────────────────────────────────────

def _escape(kind, C, Z0, max_iter, R=30.0):
    z = Z0.copy()
    c = C
    out = np.full(z.shape, max_iter, dtype=float)
    alive = np.ones(z.shape, dtype=bool)
    for n in range(max_iter):
        if kind == "ship":
            z[alive] = (np.abs(z[alive].real) + 1j * np.abs(z[alive].imag)) ** 2 + c[alive] if np.ndim(c) else \
                       (np.abs(z[alive].real) + 1j * np.abs(z[alive].imag)) ** 2 + c
        else:
            z[alive] = z[alive] * z[alive] + (c[alive] if np.ndim(c) else c)
        esc = alive & (np.abs(z) > R)
        # smooth iteration count
        out[esc] = n + 1 - np.log(np.log(np.abs(z[esc]))) / np.log(2)
        alive &= ~esc
        if not alive.any():
            break
    return out, alive


def render_fractal(cfg, size=900):
    cx, cy = cfg["center"]
    span = cfg["span"]
    xs = np.linspace(cx - span / 2, cx + span / 2, size)
    ys = np.linspace(cy - span / 2, cy + span / 2, size)
    X, Y = np.meshgrid(xs, ys)
    grid = X + 1j * Y
    mi = cfg.get("max_iter", 220)
    if cfg["kind"] == "mandel" or cfg["kind"] == "ship":
        C = grid
        Z0 = np.zeros_like(grid)
    else:  # julia
        C = np.complex128(cfg["c"])
        Z0 = grid
    esc, interior = _escape(cfg["kind"], C, Z0, mi)

    t = np.clip(esc / mi, 0, 1) ** cfg.get("gamma", 0.5)
    cmap = LinearSegmentedColormap.from_list(cfg["name"], cfg["cmap"], N=256)
    rgb = (cmap(t)[..., :3] * 255).astype(np.uint8)
    rgb[interior] = np.array(cfg.get("inside", (8, 8, 14)), dtype=np.uint8)  # set colour
    os.makedirs(SRC, exist_ok=True)
    path = os.path.join(SRC, cfg["name"].replace(" ", "_") + ".png")
    Image.fromarray(rgb).save(path)
    return path


# ── The 8 fractal palettes (each colour-mapped for a distinct family) ─────────
CONFIGS = [
    {"name": "Ember Mandelbrot", "kind": "mandel", "center": (-0.55, 0.0), "span": 3.0,
     "cmap": ["#08040a", "#5c0a12", "#b5251f", "#e8622a", "#f2b43c", "#fff2c2"]},
    {"name": "Glacier Julia", "kind": "julia", "c": -0.8 + 0.156j, "center": (0, 0), "span": 3.0,
     "cmap": ["#04101f", "#0f3b66", "#2f7fbf", "#6fc2e0", "#bfeaf5", "#ffffff"]},
    {"name": "Jade Julia", "kind": "julia", "c": -0.4 + 0.6j, "center": (0, 0), "span": 3.0,
     "cmap": ["#04140f", "#0d4a38", "#1f9c74", "#68d3a2", "#c2f0d8", "#f2fff7"]},
    {"name": "Amethyst Julia", "kind": "julia", "c": 0.285 + 0.01j, "center": (0, 0), "span": 3.0,
     "cmap": ["#0c0518", "#3a1a6b", "#7b3fbf", "#b06fe0", "#e0b0f5", "#fbeaff"]},
    {"name": "Sunset Julia", "kind": "julia", "c": -0.70176 - 0.3842j, "center": (0, 0), "span": 3.0,
     "cmap": ["#160a2a", "#6b1f6b", "#c0356f", "#e8703c", "#f6c24a", "#fff0c6"]},
    {"name": "Molten Ship", "kind": "ship", "center": (-0.5, -0.5), "span": 3.2, "gamma": 0.45,
     "cmap": ["#0a0604", "#4a1408", "#992a12", "#d9691f", "#f2b43c", "#ffe9b0"]},
    {"name": "Peacock Mandelbrot", "kind": "mandel", "center": (-0.746, 0.108), "span": 0.06,
     "max_iter": 400, "cmap": ["#04141a", "#0d5560", "#189a8f", "#5fc0a0", "#d6b85a", "#fdf1c0"]},
    {"name": "Rose Gold Julia", "kind": "julia", "c": 0.355 + 0.355j, "center": (0, 0), "span": 3.0,
     "cmap": ["#1a0d14", "#6b2340", "#c04a6a", "#e88a86", "#f2c48f", "#fff0dc"]},
]


def build_hero(palettes):
    W = 1200
    row_h, pad, top = 116, 60, 150
    H = top + len(palettes) * row_h + 60
    img = Image.new("RGB", (W, H), (13, 17, 36))
    d = ImageDraw.Draw(img)
    d.text((pad, 46), "FRACTAL DREAMS", fill=(248, 244, 235))
    d.text((pad, 82), "8 Procreate Color Palettes - from real Mandelbrot and Julia fractals",
           fill=(201, 162, 75))
    ramp_w = W - pad * 2 - 250
    for i, (name, hexes) in enumerate(palettes):
        y = top + i * row_h
        d.text((pad, y + row_h // 2 - 16), name, fill=(230, 232, 240))
        x0 = pad + 250
        cw = ramp_w / len(hexes)
        for j, hx in enumerate(hexes):
            rgb = tuple(int(hx[k:k + 2], 16) for k in (1, 3, 5))
            x = x0 + j * cw
            d.rectangle([x, y + 20, x + cw + 1, y + row_h - 24], fill=rgb)
    if os.path.exists(brand.LOGO_PATH):
        logo = Image.open(brand.LOGO_PATH).convert("RGBA")
        lw = 150
        logo = logo.resize((lw, int(lw * logo.height / logo.width)))
        img.paste(logo, (W // 2 - lw // 2, H - 60), logo)
    img.save(os.path.join(PREV, "palette_preview_1_hero.jpg"), quality=90)


def build_showcase(palettes):
    """A hero-2: the eight fractal source renders in a 4x2 grid (shows the art
    the palettes came from — a strong second listing image)."""
    cols, rows = 4, 2
    cell, gap, pad, top = 280, 10, 20, 70
    W = pad * 2 + cols * cell + (cols - 1) * gap
    H = top + pad + rows * cell + (rows - 1) * gap
    img = Image.new("RGB", (W, H), (13, 17, 36))
    d = ImageDraw.Draw(img)
    d.text((pad, 26), "Extracted from real fractal renders - computed in Python, not AI",
           fill=(201, 162, 75))
    for i, cfg in enumerate(CONFIGS):
        src = os.path.join(SRC, cfg["name"].replace(" ", "_") + ".png")
        thumb = Image.open(src).convert("RGB").resize((cell, cell), Image.LANCZOS)
        r, c = divmod(i, cols)
        img.paste(thumb, (pad + c * (cell + gap), top + r * (cell + gap)))
    img.save(os.path.join(PREV, "palette_preview_2_sources.jpg"), quality=90)


def main():
    os.makedirs(SW, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    palettes = []
    for cfg in CONFIGS:
        src = render_fractal(cfg)
        hexes = extract_palette(src)
        brand.swatches_file(os.path.join(SW, f"{cfg['name']}.swatches"), cfg["name"], hexes)
        swatch_card(cfg["name"], hexes).save(
            os.path.join(PREV, f"palette_{cfg['name'].replace(' ', '_')}.jpg"), quality=90)
        palettes.append((cfg["name"], hexes))
        print(f"  {cfg['name']}: {len(hexes)} colores")

    zip_path = os.path.join(OUT, "FractalDreams_Palettes.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, _ in palettes:
            z.write(os.path.join(SW, f"{name}.swatches"), f"{name}.swatches")
        z.writestr("HOW TO INSTALL.txt",
                   "Fractal Dreams — Procreate Color Palettes by MathRelaxing\n"
                   "========================================================\n\n"
                   "Each .swatches file is a 30-colour palette extracted from a real\n"
                   "fractal (a Mandelbrot, Julia or Burning Ship set), computed in\n"
                   "Python from the escape-time algorithm — not sampled from stock or AI.\n\n"
                   "TO INSTALL (Procreate on iPad):\n"
                   "  1. Save the .swatches files to your iPad (Files app / iCloud).\n"
                   "  2. Open Procreate. Tap the colour circle (top right) > Palettes.\n"
                   "  3. Tap the + at the top right > 'New from file'.\n"
                   "  4. Pick a .swatches file. It appears as a new 30-colour palette.\n\n"
                   "Also works in any app that reads Procreate .swatches files.\n\n"
                   "For personal & commercial artwork. Do not resell or redistribute\n"
                   "the palette files themselves.\n"
                   "© MathRelaxing · mathrelaxing.store\n")
    print(f"Zip: {zip_path}  ({os.path.getsize(zip_path)} bytes)")

    build_hero(palettes)
    build_showcase(palettes)
    print(f"Listo: {len(palettes)} paletas en {OUT}")


if __name__ == "__main__":
    main()
