"""
generate_attractor_collection.py
=================================
"Strange Attractors — A Field Guide to Deterministic Chaos": a single
reference POSTER (Tipo 5 del catalogo) that gathers six classic strange
attractors, each rendered in the same cohesive gold-on-navy treatment with
its name and governing equations typeset beside it.

Angle (validado via API): "strange attractor poster" tiene ~15 listings pero
el top ($18, 110 favs / 1.459 vistas) muestra demanda fuerte -> hueco claro.
No es un print de UN atractor (eso ya existe: rossler/vector_field/harmonograph)
sino una COLECCION curada -> producto nuevo, ticket mas alto, y produccion
barata porque reusamos la tecnica de histograma de densidad ya perfeccionada.

Cada tile: se integra el sistema (ODEs -> POCAS trayectorias x MUCHOS pasos;
mapas 2D -> MUCHAS trayectorias x POCAS iteraciones, per STANDARDS.md), se
acumula en un histograma de densidad, y se colorea negro->oro->crema con glow.

Salida en collection/:
  StrangeAttractors_print.jpg    (vendible, alta resolucion, sin marca)
  StrangeAttractors_preview.jpg  (listing, con marca de agua diagonal)

Uso:
  python generate_attractor_collection.py            # 9000x12000 (30x40in @300dpi)
  python generate_attractor_collection.py --test      # rapido, baja resolucion
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.colors import to_rgb
from PIL import Image, ImageFilter, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root, for brand.py
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "collection")

TEST = "--test" in sys.argv
# larger tiles + higher poster dpi -> more detail for big-format printing.
TILE = 380 if TEST else 2400          # px per attractor tile
POSTER_DPI = 60 if TEST else 500      # 18x24in figure -> 1080x1440 (test) or 9000x12000
#   (9000x12000 px = print-ready to 30x40 in at 300 dpi, matching the other big prints)

NAVY = "#0d1124"
GOLD = brand.GOLD
CREAM = brand.CREAM

# gold ramp: NAVY (= the poster background, so density-0 pixels blend in and the
# attractors float without a visible square edge) -> gold -> cream. Consistent
# across every tile so the six read as one designed collection.
LUT_STOPS = [(0.00, (13, 17, 36)), (0.32, (120, 85, 30)),
             (0.66, (201, 162, 75)), (1.00, (248, 244, 235))]


# ── attractors: (name, subtitle, equation-mathtext, renderer) ────────────────
def _lut(stops, n=256):
    lut = np.zeros((n, 3), dtype=np.float32)
    for i in range(n):
        t = i / (n - 1)
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]; t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                lut[i] = [c0[j] + (c1[j] - c0[j]) * f for j in range(3)]
                break
    return lut


def _rk4_step(f, x, dt):
    k1 = f(x); k2 = f(x + dt / 2 * k1); k3 = f(x + dt / 2 * k2); k4 = f(x + dt * k3)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def _ode_xy(deriv, start, dt, n, proj, warm=2000):
    xs = np.empty(n); ys = np.empty(n); x = np.array(start, float)
    for _ in range(warm):
        x = _rk4_step(deriv, x, dt)
    for i in range(n):
        x = _rk4_step(deriv, x, dt); xs[i], ys[i] = x[0], x[proj]
    return xs, ys


def _map_xy(step, seed, npts, iters, warm=20):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2, 2, npts); y = rng.uniform(-2, 2, npts)
    for _ in range(warm):
        x, y = step(x, y)
    XS = []; YS = []
    for _ in range(iters):
        x, y = step(x, y); XS.append(x.copy()); YS.append(y.copy())
    return np.concatenate(XS), np.concatenate(YS)


def _tile(xs, ys, W=TILE, gamma=0.52):
    lo_x, hi_x = np.percentile(xs, 0.2), np.percentile(xs, 99.8)
    lo_y, hi_y = np.percentile(ys, 0.2), np.percentile(ys, 99.8)
    span = max(hi_x - lo_x, hi_y - lo_y) * 1.10
    cx, cy = (lo_x + hi_x) / 2, (lo_y + hi_y) / 2
    lo_x, hi_x = cx - span / 2, cx + span / 2
    lo_y, hi_y = cy - span / 2, cy + span / 2
    px = ((xs - lo_x) / (hi_x - lo_x) * (W - 1)).astype(np.int32)
    py = ((hi_y - ys) / (hi_y - lo_y) * (W - 1)).astype(np.int32)
    v = (px >= 0) & (px < W) & (py >= 0) & (py < W)
    h = np.zeros((W, W)); np.add.at(h, (py[v], px[v]), 1.0)
    h = np.log1p(h); h = (h / h.max()) ** gamma
    lut = _lut(LUT_STOPS)
    rgb = lut[(h * 255).astype(np.int32)]
    core = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    br = max(1, W // 500)
    core_b = np.array(core.filter(ImageFilter.GaussianBlur(br)), dtype=np.float32)
    glow = np.clip((h - 0.5) / 0.5, 0, 1)[..., None] * rgb
    glow_b = np.array(Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(max(2, W // 120))), dtype=np.float32)
    screen = 255 - (255 - core_b) * (255 - glow_b) / 255.0
    return np.clip(screen, 0, 255).astype(np.uint8)


def lorenz_tile():
    def f(v): x, y, z = v; return np.array([10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z])
    n = 60000 if TEST else 1800000
    return _tile(*_ode_xy(f, [1, 1, 1], 0.005, n, proj=2))


def rossler_tile():
    def f(v): x, y, z = v; return np.array([-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)])
    n = 60000 if TEST else 1800000
    return _tile(*_ode_xy(f, [1, 1, 1], 0.02, n, proj=1))


def thomas_tile():
    def f(v): x, y, z = v; b = 0.208; return np.array([np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z])
    n = 60000 if TEST else 1800000
    return _tile(*_ode_xy(f, [1, 0, 1], 0.05, n, proj=1))


def aizawa_tile():
    def f(v):
        x, y, z = v; a, b, c, d, e, g = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
        return np.array([(z - b) * x - d * y, d * x + (z - b) * y,
                         c + a * z - z**3 / 3 - (x**2 + y**2) * (1 + e * z) + g * z * x**3])
    n = 60000 if TEST else 1800000
    return _tile(*_ode_xy(f, [0.1, 0, 0], 0.01, n, proj=2))


def dejong_tile():
    a, b, c, d = 1.641, 1.902, 0.316, 1.525
    npts = 15000 if TEST else 140000
    return _tile(*_map_xy(lambda x, y: (np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)),
                          7, npts, 60))


def clifford_tile():
    a, b, c, d = -1.4, 1.6, 1.0, 0.7
    npts = 15000 if TEST else 140000
    return _tile(*_map_xy(lambda x, y: (np.sin(a * y) + c * np.cos(a * x), np.sin(b * x) + d * np.cos(b * y)),
                          3, npts, 60))


ATTRACTORS = [
    ("Lorenz", "1963  ·  ODE flow",
     r"$\dot{x}=\sigma(y-x)$" "\n" r"$\dot{y}=x(\rho-z)-y$" "\n" r"$\dot{z}=xy-\beta z$", lorenz_tile),
    ("Rössler", "1976  ·  ODE flow",
     r"$\dot{x}=-y-z$" "\n" r"$\dot{y}=x+ay$" "\n" r"$\dot{z}=b+z(x-c)$", rossler_tile),
    ("Thomas", "cyclically symmetric",
     r"$\dot{x}=\sin y-bx$" "\n" r"$\dot{y}=\sin z-by$" "\n" r"$\dot{z}=\sin x-bz$", thomas_tile),
    ("Aizawa", "ODE flow",
     r"$\dot{x}=(z-b)x-dy$" "\n" r"$\dot{y}=dx+(z-b)y$" "\n" r"$\dot{z}=c+az-\frac{z^3}{3}-\ldots$", aizawa_tile),
    ("De Jong", "2-D iterated map",
     r"$x'=\sin(ay)-\cos(bx)$" "\n" r"$y'=\sin(cx)-\cos(dy)$", dejong_tile),
    ("Clifford", "2-D iterated map",
     r"$x'=\sin(ay)+c\cos(ax)$" "\n" r"$y'=\sin(bx)+d\cos(by)$", clifford_tile),
]


def build_poster():
    os.makedirs(OUT, exist_ok=True)
    W_IN, H_IN = 18.0, 24.0
    fig = plt.figure(figsize=(W_IN, H_IN))
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 3); ax.set_ylim(0, 4)

    # title block
    ax.text(1.5, 3.80, "STRANGE ATTRACTORS", ha="center", va="center",
            fontsize=42, color=CREAM, family="serif", fontweight="bold")
    ax.text(1.5, 3.63, "A Field Guide to Deterministic Chaos", ha="center", va="center",
            fontsize=19, color=GOLD, family="serif", style="italic")
    ax.plot([0.55, 2.45], [3.52, 3.52], color=GOLD, lw=1.2, alpha=0.7)

    # 2 columns x 3 rows grid of tiles
    cols, rows = 2, 3
    x0, x1 = 0.16, 2.84
    top, bot = 3.36, 0.42
    cw = (x1 - x0) / cols
    ch = (top - bot) / rows
    for i, (name, sub, eq, renderer) in enumerate(ATTRACTORS):
        print(f"  render {name}...")
        tile = renderer()
        c, r = i % cols, i // cols
        cx = x0 + c * cw + cw / 2
        cy = top - r * ch - ch / 2
        img_h = ch * 0.62
        img_w = img_h  # square
        ext = [cx - img_w / 2, cx + img_w / 2, cy + ch * 0.30 - img_h / 2, cy + ch * 0.30 + img_h / 2]
        ax.imshow(tile, extent=ext, zorder=3)
        # name + subtitle + equation under the tile
        ty = cy - ch * 0.09
        ax.text(cx, ty, name, ha="center", va="top", fontsize=21, color=CREAM,
                family="serif", fontweight="bold", zorder=4)
        ax.text(cx, ty - ch * 0.075, sub, ha="center", va="top", fontsize=11,
                color=GOLD, family="serif", style="italic", zorder=4)
        ax.text(cx, ty - ch * 0.15, eq, ha="center", va="top", fontsize=12.5,
                color=(0.80, 0.82, 0.88), zorder=4, linespacing=1.5)

    # No branding on the sellable file -- it's wall art for framing, same
    # convention as the other Type-5 art prints (Rossler, Vector Field...).

    print_path = os.path.join(OUT, "StrangeAttractors_print.jpg")
    fig.savefig(print_path, dpi=POSTER_DPI, facecolor=NAVY,
                pil_kwargs={"quality": 95})
    plt.close(fig)
    print("Guardado:", print_path)
    make_preview(print_path)


PREVIEW_LONG_EDGE = 3000
WATERMARK_TEXT = "MATHRELAXING.STORE  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def make_preview(print_path):
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(print_path)
    w, h = img.size
    scale = PREVIEW_LONG_EDGE / h
    prev = img.resize((int(w * scale), PREVIEW_LONG_EDGE), Image.LANCZOS).convert("RGB")
    # diagonal tiled watermark
    fs = max(20, int(prev.width * 0.030))
    font = ImageFont.truetype(FONT_PATH, fs)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(WATERMARK_TEXT, font=font))
    sx, sy = int(tw * 1.5), int(fs * 6)
    tile = Image.new("RGBA", (sx, sy), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((sx * 0.06, sy * 0.3), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 42))
    tile = tile.rotate(30, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", prev.size, (0, 0, 0, 0))
    for yy in range(-tile.height, prev.height, tile.height):
        for xx in range(-tile.width, prev.width, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    out = Image.alpha_composite(prev.convert("RGBA"), layer).convert("RGB")
    pp = os.path.join(OUT, "StrangeAttractors_preview.jpg")
    out.save(pp, quality=92)
    print("Guardado:", pp)


if __name__ == "__main__":
    build_poster()
