"""
generate_harmonograph_print.py
================================
Art print estatico de alta resolucion de un HARMONOGRAFO — Tipo 5 del catalogo
(STANDARDS.md): imagen fija print-ready, no animacion ni libro.

Un harmonografo es la figura que traza un lapiz movido por dos pendulos
amortiguados (mecanismo victoriano, ~1870). Matematicamente:
    x(t) = a1 sin(f1 t + p1) e^{-d1 t} + a2 sin(f2 t + p2) e^{-d2 t}
    y(t) = a3 sin(f3 t + p3) e^{-d3 t} + a4 sin(f4 t + p4) e^{-d4 t}
La amortiguacion (d) hace que la amplitud decaiga, anidando lazos cada vez
mas chicos y creando patrones de interferencia (nodos brillantes donde la
curva se cruza consigo misma). Reusa el motor de lulu_books/core/
generate_harmonographs.py, con una figura elegida (seed 1, freqs 3-3-4-5).

Tecnica de render: identica a generate_vector_field_print.py / _rossler_ —
se acumulan los puntos de la curva en un histograma de densidad (streaming),
se colorea con una rampa negro->color->blanco y se le suma glow; los cruces
de la curva quedan como nodos casi blancos. Cuadrado (la figura es ~circular).

Salida: 3 variantes de color, cada una con archivo vendible ("*_print.jpg",
resolucion completa, sin marca) y preview publico ("*_preview.jpg", ~3000px,
con marca de agua diagonal).

Uso:
  python generate_harmonograph_print.py            # 9000x9000 final
  python generate_harmonograph_print.py --test      # chico y rapido
  python generate_harmonograph_print.py --load-cache # re-render desde cache
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import sys
import math
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "harmonograph")

TEST = "--test" in sys.argv

if TEST:
    W = 900
    N_POINTS = 400_000
else:
    W = 9000
    # a harmonograph is ONE continuous curve; to draw it as a smooth luminous
    # line across a 9000px canvas the points must be spaced well under 1px of
    # arc length, hence millions of samples.
    N_POINTS = 14_000_000

H = W  # square

# chosen figure (seed 1 from the exploration sheet: a balanced multi-petal
# flower with rich self-interference). Params are frozen here so the render is
# reproducible and always the same artwork.
SEED = 1
T_MAX = 190.0

PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING.STORE  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def harmonograph_xy(n):
    rng = np.random.default_rng(SEED)
    f = rng.integers(1, 6, 4).astype(float)      # -> [3,3,4,5] for seed 1
    p = rng.uniform(0, 2 * math.pi, 4)
    d = rng.uniform(0.0015, 0.004, 4)
    a = rng.uniform(1.0, 2.4, 4)
    t = np.linspace(0, T_MAX, n)
    x = a[0] * np.sin(f[0] * t + p[0]) * np.exp(-d[0] * t) + a[1] * np.sin(f[1] * t + p[1]) * np.exp(-d[1] * t)
    y = a[2] * np.sin(f[2] * t + p[2]) * np.exp(-d[2] * t) + a[3] * np.sin(f[3] * t + p[3]) * np.exp(-d[3] * t)
    return x, y


def simulate_histogram():
    print(f"Trazando harmonografo: {N_POINTS:,} puntos...")
    t0 = time.time()
    x, y = harmonograph_xy(N_POINTS)
    # frame to a square around the figure (percentiles ignore the sparse tips)
    lo_x, hi_x = np.percentile(x, 0.15), np.percentile(x, 99.85)
    lo_y, hi_y = np.percentile(y, 0.15), np.percentile(y, 99.85)
    span = max(hi_x - lo_x, hi_y - lo_y) * 1.10
    cx, cy = (lo_x + hi_x) / 2, (lo_y + hi_y) / 2
    lo_x, hi_x = cx - span / 2, cx + span / 2
    lo_y, hi_y = cy - span / 2, cy + span / 2

    px = ((x - lo_x) / (hi_x - lo_x) * (W - 1)).astype(np.int32)
    py = (H - 1 - (y - lo_y) / (hi_y - lo_y) * (H - 1)).astype(np.int32)
    valid = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    hist = np.zeros((H, W), dtype=np.float64)
    np.add.at(hist, (py[valid], px[valid]), 1.0)
    print(f"Listo. {time.time()-t0:.1f}s")
    return hist


# ── Paletas: negro -> color -> nucleo casi blanco. Elegidas para NO repetir las
#    de Rossler (cyan/violet/amber) ni Vector Field (teal/copper/indigo);
#    "verdigris" aporta el verde que faltaba en el catalogo de prints. ─────────
# The bulk of the figure is a single-pass line that lands around the low-mid of
# the (log) density scale, so the vivid, saturated colour is placed EARLY (low t)
# and near-white is reserved for the very top (the self-crossing nodes only).
# This keeps the whole curve reading as a bright coloured line on black instead
# of a dim thread that only glows where it overlaps.
PALETTES = {
    "moonlit": [(0.00, (4, 8, 20)), (0.14, (30, 80, 170)),
                 (0.42, (90, 180, 255)), (0.80, (170, 220, 255)), (1.00, (240, 250, 255))],
    "rose_gold": [(0.00, (14, 5, 12)), (0.14, (150, 40, 95)),
                   (0.42, (240, 90, 150)), (0.72, (250, 175, 120)), (1.00, (255, 240, 225))],
    "verdigris": [(0.00, (4, 14, 11)), (0.14, (25, 120, 95)),
                   (0.42, (70, 220, 165)), (0.80, (170, 240, 210)), (1.00, (235, 255, 245))],
}


def gradient_lut(stops, n=256):
    lut = np.zeros((n, 3), dtype=np.float32)
    for idx in range(n):
        t = idx / (n - 1)
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                fr = (t - t0) / (t1 - t0) if t1 > t0 else 0
                lut[idx] = [c0[j] + (c1[j] - c0[j]) * fr for j in range(3)]
                break
    return lut


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


def render_from_hist(hist, palette_name, out_path):
    dens = np.log1p(hist)
    dmax = dens.max() if dens.max() > 0 else 1.0
    dens_n = np.clip(dens / dmax, 0, 1)
    # the single-pass line sits low on the log scale; lift it hard so the curve
    # itself reads as a bright luminous line, not a faint thread. (0.72 left the
    # bulk of the figure too dim against the black ground.)
    dens_n = dens_n ** 0.45

    lut = gradient_lut(PALETTES[palette_name])
    idx = (dens_n * (len(lut) - 1)).astype(np.int32)
    rgb = lut[idx]

    core_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    blur_r = max(1, int(round(0.35 * (W / 1080))))
    core_blur = np.array(core_img.filter(ImageFilter.GaussianBlur(blur_r)), dtype=np.float32)

    bright = np.clip((dens_n - 0.5) / 0.5, 0, 1)[..., None] * rgb
    glow_img = Image.fromarray(np.clip(bright, 0, 255).astype(np.uint8))
    glow_r = max(2, int(round(1.8 * (W / 1080))))
    glow_blur = np.array(glow_img.filter(ImageFilter.GaussianBlur(glow_r)), dtype=np.float32)

    screen = 255 - (255 - core_blur) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)

    print_img = Image.fromarray(final)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print_img.save(out_path, quality=98)
    print("Guardado:", out_path)
    make_preview(print_img, out_path.replace("_print.jpg", "_preview.jpg"))


def main():
    cache = os.path.join(OUT, "_hist_cache.npy")
    if "--load-cache" in sys.argv and os.path.exists(cache):
        print("Cargando histograma cacheado...")
        hist = np.load(cache)
    else:
        hist = simulate_histogram()
        os.makedirs(OUT, exist_ok=True)
        np.save(cache, hist)
    suffix = "_test" if TEST else ""
    render_from_hist(hist, "moonlit", os.path.join(OUT, f"harmonograph_moonlit{suffix}_print.jpg"))
    render_from_hist(hist, "rose_gold", os.path.join(OUT, f"harmonograph_rosegold{suffix}_print.jpg"))
    render_from_hist(hist, "verdigris", os.path.join(OUT, f"harmonograph_verdigris{suffix}_print.jpg"))


if __name__ == "__main__":
    main()
