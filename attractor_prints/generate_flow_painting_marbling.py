"""
generate_flow_painting_marbling.py
====================================
Third signature flow-field "painting" for physical POD (canvas/poster via
Printify) — same density-histogram rendering pipeline as the other two
flow_painting scripts, but a genuinely different mathematical expression
driving the flow:

  The first two pieces used potential flow: a handful of point singularities
  (source/sink/vortex/saddle), each contributing a 1/r-decaying field. This
  one instead sums several plane sine waves into a stream function

      psi(x,y) = sum_i A_i * sin(k_i*(x*cos(theta_i) + y*sin(theta_i)) + phi_i)

  and takes the velocity as its curl, (u,v) = (d(psi)/dy, -d(psi)/dx) — the
  standard construction that makes ANY scalar field into a divergence-free
  flow. With no point singularities to spiral into, streamlines instead
  weave through smooth, all-over turbulence: it reads as ink marbling
  (suminagashi) or wood-grain burl rather than the vortex "eyes" of the
  other two pieces.

  - "Amber Gold" palette — warm honey/gold marbling on black, a colour
    family not used by any existing flow-painting or digital colorway.

  python attractor_prints/generate_flow_painting_marbling.py            # full 9000x12000
  python attractor_prints/generate_flow_painting_marbling.py --test     # quick low-res
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "flow_painting_marbling")

TEST = "--test" in sys.argv

if TEST:
    W, H = 900, 1200
    SEED_GRID = (50, 65)
    STEP = 0.03
    MAX_STEPS = 700
else:
    W, H = 9000, 12000
    SEED_GRID = (170, 220)
    STEP = 0.006
    MAX_STEPS = 3200

DOMAIN_W, DOMAIN_H = 30.0, 40.0

# Stream function: a sum of plane sine waves at different wavenumbers,
# orientations and phases. (amplitude, wavenumber, angle_deg, phase)
WAVES = [
    (1.00, 0.34, 15,  0.4),
    (0.85, 0.55, 100, 2.1),
    (0.65, 0.27, 152, 1.0),
    (0.55, 0.90, 58,  3.0),
    (0.38, 1.40, 205, 0.7),
    (0.28, 2.10, 260, 1.6),
]
_WAVE_ARR = np.array([(a, k, np.radians(deg), phi) for a, k, deg, phi in WAVES])


PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

rng = np.random.default_rng(59)


def field_vec(x, y):
    """(u, v) = (d(psi)/dy, -d(psi)/dx) for psi = sum A*sin(k*(x*ca+y*sa)+phi)."""
    u = np.zeros_like(x)
    v = np.zeros_like(y)
    for a, k, th, phi in _WAVE_ARR:
        ca, sa = np.cos(th), np.sin(th)
        phase = k * (x * ca + y * sa) + phi
        c = a * k * np.cos(phase)
        u += c * sa
        v += -c * ca
    return u, v


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
        fx, fy = field_vec(x, y)
        speed = np.hypot(fx, fy) + 1e-9
        vx, vy = direction * fx / speed, direction * fy / speed

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


# New signature palette: warm honey/gold marbling ("amber_gold") -- distinct
# from teal/copper/indigo (digital) and verdigris/wine (canvas pieces 1-2).
PALETTES = {
    "amber_gold": [(0.00, (6, 4, 2)), (0.35, (90, 55, 10)),
                   (0.68, (230, 175, 60)), (1.00, (255, 245, 215))],
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
    # Normalize against a high percentile, not the true max -- a few outlier
    # hot pixels (e.g. where two wave crests align) would otherwise crush
    # the rest of the canvas toward black. See generate_flow_painting_
    # vortexeye.py for the full writeup of this bug.
    positive = dens[dens > 0]
    dmax = np.percentile(positive, 99.9) if positive.size else 1.0
    dmax = dmax if dmax > 0 else 1.0
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
    render_from_hist(hist, "amber_gold", os.path.join(OUT, f"flowpainting_ambergold{suffix}_print.jpg"))


if __name__ == "__main__":
    main()
