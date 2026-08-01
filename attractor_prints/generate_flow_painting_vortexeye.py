"""
generate_flow_painting_vortexeye.py
====================================
Second signature flow-field "painting" for physical POD (canvas/poster via
Printify) — same engine as generate_flow_painting_canvas.py, but a
deliberately different composition and palette so the two pieces read as
distinct artworks, not variants of one:

  - "Vortex Eye": one dominant off-center vortex (a single strong focal
    point) instead of the first piece's balanced diagonal sweep between two
    equal eddies. Most of the canvas spirals toward one eye.
  - "Rose Ash" palette — dusty rose/blush glow on near-black, a warm pink
    family not used by any existing colorway (teal, copper, indigo, verdigris).

  python attractor_prints/generate_flow_painting_vortexeye.py            # full 9000x12000
  python attractor_prints/generate_flow_painting_vortexeye.py --test     # quick low-res
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "flow_painting_vortexeye")

TEST = "--test" in sys.argv

if TEST:
    W, H = 900, 1200
    SEED_GRID = (50, 65)
    STEP = 0.03
    MAX_STEPS = 900
else:
    W, H = 9000, 12000
    SEED_GRID = (170, 220)
    STEP = 0.006
    MAX_STEPS = 4500

DOMAIN_W, DOMAIN_H = 30.0, 40.0
EPS_SINGULARITY = 0.35

# One dominant vortex near the upper golden-ratio point (strong focal "eye"),
# a small counter-eddy and a source pushed to the lower corners for balance,
# and a faint saddle up top for structure -- most of the canvas spirals
# toward the single eye rather than splitting attention between two eddies.
SINGULARITIES = [
    (18.5, 26.0, "vortex_cw",  2.3),
    (7.0,  9.0,  "vortex_ccw", 1.0),
    (25.0, 10.0, "source",     0.9),
    (12.0, 36.5, "saddle",     0.4),
]

PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

rng = np.random.default_rng(41)


def field_vec(x, y, sings):
    fx = np.zeros_like(x)
    fy = np.zeros_like(y)
    for sx, sy, kind, strength in sings:
        dx, dy = x - sx, y - sy
        r2 = dx * dx + dy * dy + 1e-6
        if kind == "source":
            fx += strength * dx / r2; fy += strength * dy / r2
        elif kind == "sink":
            fx += -strength * dx / r2; fy += -strength * dy / r2
        elif kind == "vortex_cw":
            fx += strength * dy / r2; fy += -strength * dx / r2
        elif kind == "vortex_ccw":
            fx += -strength * dy / r2; fy += strength * dx / r2
        elif kind == "saddle":
            fx += strength * dx / r2; fy += -strength * dy / r2
    return fx, fy


def nearest_singularity_dist(x, y, sings):
    dmin = np.full_like(x, np.inf)
    for sx, sy, _, _ in sings:
        d = np.hypot(x - sx, y - sy)
        dmin = np.minimum(dmin, d)
    return dmin


def make_seeds():
    cols, rows = SEED_GRID
    xs = np.linspace(0, DOMAIN_W, cols)
    ys = np.linspace(0, DOMAIN_H, rows)
    gx, gy = np.meshgrid(xs, ys)
    gx = gx.ravel() + rng.uniform(-0.4, 0.4, gx.size)
    gy = gy.ravel() + rng.uniform(-0.4, 0.4, gy.size)
    return gx, gy


def simulate_histogram():
    lo_x, hi_x = 0.0, DOMAIN_W
    lo_y, hi_y = 0.0, DOMAIN_H
    sx_scale = (W - 1) / (hi_x - lo_x)
    sy_scale = (H - 1) / (hi_y - lo_y)

    seeds_x, seeds_y = make_seeds()
    x = np.concatenate([seeds_x, seeds_x])
    y = np.concatenate([seeds_y, seeds_y])
    direction = np.concatenate([np.ones_like(seeds_x), -np.ones_like(seeds_x)])
    n_lines = x.size
    alive = np.ones(n_lines, dtype=bool)

    hist = np.zeros((H, W), dtype=np.float64)
    print(f"Integrando {n_lines} streamlines x hasta {MAX_STEPS} pasos...")
    t0 = time.time()
    log_every = max(1, MAX_STEPS // 10)
    for step in range(MAX_STEPS):
        fx, fy = field_vec(x, y, SINGULARITIES)
        speed = np.hypot(fx, fy) + 1e-9
        vx, vy = direction * fx / speed, direction * fy / speed

        dist = nearest_singularity_dist(x, y, SINGULARITIES)
        alive &= dist > EPS_SINGULARITY

        x = np.where(alive, x + STEP * vx, x)
        y = np.where(alive, y + STEP * vy, y)
        alive &= (x >= lo_x) & (x <= hi_x) & (y >= lo_y) & (y <= hi_y)

        if not alive.any():
            break

        px = ((x - lo_x) * sx_scale).astype(np.int32)
        py = (H - 1 - (y - lo_y) * sy_scale).astype(np.int32)
        valid = alive & (px >= 0) & (px < W) & (py >= 0) & (py < H)
        if valid.any():
            np.add.at(hist, (py[valid], px[valid]), 1.0)

        if step % log_every == 0:
            print(f"  paso {step}/{MAX_STEPS}  vivas={alive.sum()}  ({time.time()-t0:.1f}s)")

    print(f"Listo integrar. {time.time()-t0:.1f}s total")
    return hist


# New signature palette: dusty rose / blush ("rose_ash") -- warm pink family,
# distinct from the existing teal/copper/indigo/verdigris colorways.
PALETTES = {
    "rose_ash": [(0.00, (10, 4, 7)), (0.35, (80, 25, 40)),
                 (0.68, (225, 120, 140)), (1.00, (255, 235, 238))],
}


def gradient_lut(stops, n=256):
    lut = np.zeros((n, 3), dtype=np.float32)
    for idx in range(n):
        t = idx / (n - 1)
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                lut[idx] = [c0[j] + (c1[j] - c0[j]) * f for j in range(3)]
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

    lut = gradient_lut(PALETTES[palette_name])
    idx = (dens_n * (len(lut) - 1)).astype(np.int32)
    rgb = lut[idx]

    core_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    blur_r = max(1, int(round(0.35 * (W / 1080))))
    core_blur = np.array(core_img.filter(ImageFilter.GaussianBlur(blur_r)), dtype=np.float32)

    bright = np.clip((dens_n - 0.45) / 0.55, 0, 1)[..., None] * rgb
    glow_img = Image.fromarray(np.clip(bright, 0, 255).astype(np.uint8))
    glow_r = max(2, int(round(1.8 * (W / 1080))))
    glow_blur = np.array(glow_img.filter(ImageFilter.GaussianBlur(glow_r)), dtype=np.float32)

    screen = 255 - (255 - core_blur) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)

    print_img = Image.fromarray(final)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print_img.save(out_path, quality=98)
    print("Guardado:", out_path)

    preview_path = out_path.replace("_print.jpg", "_preview.jpg")
    make_preview(print_img, preview_path)


def main():
    cache_path = os.path.join(OUT, "_hist_cache.npy")
    if "--load-cache" in sys.argv and os.path.exists(cache_path):
        print(f"Cargando histograma cacheado de {cache_path}...")
        hist = np.load(cache_path)
    else:
        hist = simulate_histogram()
        os.makedirs(OUT, exist_ok=True)
        np.save(cache_path, hist)
        print(f"Histograma cacheado en {cache_path}")
    suffix = "_test" if TEST else ""
    render_from_hist(hist, "rose_ash", os.path.join(OUT, f"flowpainting_roseash{suffix}_print.jpg"))


if __name__ == "__main__":
    main()
