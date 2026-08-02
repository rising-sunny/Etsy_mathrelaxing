"""
generate_flow_painting_clifford.py
====================================
Third signature flow-field "painting" for physical POD (canvas/poster via
Printify) — replaces the sinusoidal-marbling piece with a genuinely
different class of mathematical object:

  Pieces 1-2 seed thousands of streamlines into a smooth, continuous vector
  field (potential flow) and integrate them forward/backward in time —
  classical field theory. This piece instead iterates a discrete nonlinear
  map, the Clifford attractor:

      x_{n+1} = sin(a*y_n) + c*cos(a*x_n)
      y_{n+1} = sin(b*x_n) + d*cos(b*y_n)

  Tens of thousands of points are dropped at random, burned in for a few
  dozen iterations to reach the attractor, then iterated thousands more
  times while their visited pixels accumulate in the same density histogram
  used by the other pieces. There is no field to seed into and no notion of
  "leaving the domain" — chaos theory / discrete dynamical systems, not
  vector calculus. Same render pipeline (percentile-normalized density ->
  gradient LUT -> screen-blended glow) so the finished piece still belongs
  to the same visual family.

  - "Sapphire" palette — deep, saturated blue glow on black, cooler and less
    purple than the existing Midnight Indigo digital colorway.

  python attractor_prints/generate_flow_painting_clifford.py            # full 9000x12000
  python attractor_prints/generate_flow_painting_clifford.py --test     # quick low-res
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "flow_painting_clifford")

TEST = "--test" in sys.argv

if TEST:
    W, H = 900, 1200
    N_TRAJ = 4000
    N_COUNT = 800
else:
    W, H = 9000, 12000
    N_TRAJ = 45000
    N_COUNT = 3000

N_BURN = 60
DOMAIN_W, DOMAIN_H = 30.0, 40.0
MARGIN_FRAC = 0.92  # fraction of the domain the attractor's bbox is fit into

# Classic Clifford attractor parameters (two-lobe butterfly form).
A, B, C, D = -1.4, 1.6, 1.0, 0.7

PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

rng = np.random.default_rng(83)


def clifford_step(x, y):
    return np.sin(A * y) + C * np.cos(A * x), np.sin(B * x) + D * np.cos(B * y)


def simulate_histogram():
    x = rng.uniform(-1, 1, N_TRAJ)
    y = rng.uniform(-1, 1, N_TRAJ)

    print(f"Quemando {N_TRAJ} trayectorias x {N_BURN} pasos...")
    for _ in range(N_BURN):
        x, y = clifford_step(x, y)

    # Fit the attractor's bounding box into the canvas: rotate 90 degrees
    # (map data-y -> canvas-x, data-x -> canvas-y) since Clifford's natural
    # bbox is wider than tall while the poster canvas is portrait -- this
    # orientation fills it far more tightly than the unrotated one.
    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    span_u, span_v = ymax - ymin, xmax - xmin  # u=canvas-x from data-y, v=canvas-y from data-x
    scale = min((DOMAIN_W * MARGIN_FRAC) / span_u, (DOMAIN_H * MARGIN_FRAC) / span_v)
    u_mid, v_mid = (ymin + ymax) / 2, (xmin + xmax) / 2

    sx_scale = (W - 1) / DOMAIN_W
    sy_scale = (H - 1) / DOMAIN_H

    hist = np.zeros((H, W), dtype=np.float64)
    print(f"Iterando y acumulando {N_COUNT} pasos...")
    t0 = time.time()
    log_every = max(1, N_COUNT // 10)
    for step in range(N_COUNT):
        x, y = clifford_step(x, y)

        dom_x = (y - u_mid) * scale + DOMAIN_W / 2
        dom_y = (x - v_mid) * scale + DOMAIN_H / 2

        px = (dom_x * sx_scale).astype(np.int32)
        py = (H - 1 - dom_y * sy_scale).astype(np.int32)
        valid = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        if valid.any():
            np.add.at(hist, (py[valid], px[valid]), 1.0)

        if step % log_every == 0:
            print(f"  paso {step}/{N_COUNT}  ({time.time()-t0:.1f}s)")

    print(f"Listo iterar. {time.time()-t0:.1f}s total")
    return hist


# New signature palette: deep sapphire blue -- cooler and more saturated-blue
# (less purple) than the existing Midnight Indigo digital colorway.
PALETTES = {
    "sapphire": [(0.00, (2, 4, 10)), (0.35, (10, 35, 95)),
                 (0.68, (55, 130, 230)), (1.00, (215, 235, 255))],
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
    # Normalize against a high percentile, not the true max -- see
    # generate_flow_painting_vortexeye.py for the full writeup of why a
    # handful of outlier hot pixels must not be allowed to crush the rest
    # of the canvas toward black.
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
    render_from_hist(hist, "sapphire", os.path.join(OUT, f"flowpainting_sapphire{suffix}_print.jpg"))


if __name__ == "__main__":
    main()
