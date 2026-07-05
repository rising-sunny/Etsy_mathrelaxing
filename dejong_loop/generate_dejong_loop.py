"""
generate_dejong_loop.py
=========================
Genera los frames de "De Jong Attractor" — animacion seamless de un atractor
caotico de Peter de Jong, mutando de forma continua, con loop matematicamente
perfecto.

El mapa de De Jong:
    x' = sin(a*y) - cos(b*x)
    y' = sin(c*x) - cos(d*y)

Tecnica del loop perfecto:
  Los parametros (a, c) recorren una trayectoria CIRCULAR en el espacio de
  parametros: a(t) = a0 + amp*cos(theta), c(t) = c0 + amp*sin(theta), con
  theta = 2*pi*t/T. Al ser un circulo completo (no una oscilacion de ida y
  vuelta sobre la misma recta), el atractor muta de forma continua y en una
  sola direccion sin retroceder sobre si mismo, y en t=0 y en t=T theta da la
  vuelta completa: frame 0 == frame T, el video puede repetirse infinitamente
  sin corte visible.

Render: cada frame se recalcula desde cero (mismos puntos iniciales, misma
semilla) iterando el mapa con los parametros de ESE frame; se descarta un
transitorio inicial y se acumulan las posiciones siguientes en un histograma
2D (densidad de visitas), que se colorea con una paleta de "plasma" cian/
indigo sobre negro y se le agrega bloom (glow) en las zonas mas brillantes.

Paleta: negro -> indigo profundo -> cian electrico -> nucleo blanco-cian en
las zonas de mayor densidad. Deliberadamente fria, para diferenciarse de
Thomas Attractor (oro/aqua) y Voronoi Cell Garden (violeta/magenta/oro).

Uso:
  python generate_dejong_loop.py            # genera 240 frames en frames/
  python generate_dejong_loop.py --test      # genera solo 8 frames a menor
                                              # resolucion para revisar rapido
"""
import numpy as np
from PIL import Image, ImageFilter
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(BASE, "frames")

TEST = "--test" in sys.argv

W = H = 1080 if not TEST else 360
FPS = 30
DURATION = 8
T = FPS * DURATION if not TEST else 8

N_POINTS = 120_000 if not TEST else 20_000
WARMUP = 60
ITERS = 220 if not TEST else 80
SEED = 7

# ── Parametros base del mapa de De Jong (configuracion clasica "swirl") ─────
A0, B0, C0, D0 = 1.641, 1.902, 0.316, 1.525
A_AMP, C_AMP = 0.24, 0.20   # amplitud de la oscilacion (mantiene la forma
                             # reconocible en todo el loop, sin degenerar)

rng = np.random.default_rng(SEED)
x0 = rng.uniform(-1, 1, size=N_POINTS).astype(np.float32)
y0 = rng.uniform(-1, 1, size=N_POINTS).astype(np.float32)

# ── Bounding box fijo, estimado una sola vez recorriendo todo el rango de
#    parametros que se usara en la animacion (para que el encuadre no
#    "respire" de frame a frame) ─────────────────────────────────────────────
def sample_bounds():
    xs, ys = x0.copy(), y0.copy()
    lo = np.array([1e9, 1e9]); hi = np.array([-1e9, -1e9])
    probe_ts = np.linspace(0, T, 24, endpoint=False)
    for tp in probe_ts:
        theta = 2 * np.pi * tp / T
        a = A0 + A_AMP * np.cos(theta)
        c = C0 + C_AMP * np.sin(theta)
        xs, ys = x0.copy(), y0.copy()
        for _ in range(WARMUP + ITERS):
            xs, ys = np.sin(a * ys) - np.cos(B0 * xs), np.sin(c * xs) - np.cos(D0 * ys)
        lo = np.minimum(lo, [xs.min(), ys.min()])
        hi = np.maximum(hi, [xs.max(), ys.max()])
    pad = 0.06 * (hi - lo)
    return lo - pad, hi + pad

print("Calculando encuadre fijo...")
BOUNDS_LO, BOUNDS_HI = sample_bounds()
print(f"  bounds: {BOUNDS_LO} .. {BOUNDS_HI}")

# ── Paleta de densidad: negro -> indigo -> cian electrico -> blanco-cian ────
STOPS = [
    (0.00, (2, 2, 8)),
    (0.35, (30, 20, 90)),
    (0.65, (0, 200, 220)),
    (1.00, (215, 250, 255)),
]

def gradient_lut(n=256):
    lut = np.zeros((n, 3), dtype=np.float32)
    for i in range(n):
        t = i / (n - 1)
        for k in range(len(STOPS) - 1):
            t0, c0 = STOPS[k]
            t1, c1 = STOPS[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                lut[i] = [c0[j] + (c1[j] - c0[j]) * f for j in range(3)]
                break
    return lut

LUT = gradient_lut()


def render_frame(t):
    theta = 2 * np.pi * t / T
    a = A0 + A_AMP * np.cos(theta)
    c = C0 + C_AMP * np.sin(theta)

    xs, ys = x0.copy(), y0.copy()
    for _ in range(WARMUP):
        xs, ys = np.sin(a * ys) - np.cos(B0 * xs), np.sin(c * xs) - np.cos(D0 * ys)

    hist = np.zeros((H, W), dtype=np.float64)
    rangex = (BOUNDS_LO[0], BOUNDS_HI[0])
    rangey = (BOUNDS_LO[1], BOUNDS_HI[1])
    sx = (W - 1) / (rangex[1] - rangex[0])
    sy = (H - 1) / (rangey[1] - rangey[0])

    for _ in range(ITERS):
        xs, ys = np.sin(a * ys) - np.cos(B0 * xs), np.sin(c * xs) - np.cos(D0 * ys)
        px = ((xs - rangex[0]) * sx).astype(np.int32)
        py = ((ys - rangey[0]) * sy).astype(np.int32)
        valid = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        np.add.at(hist, (py[valid], px[valid]), 1.0)

    # densidad -> log -> normalizado -> LUT de color
    dens = np.log1p(hist)
    dmax = dens.max() if dens.max() > 0 else 1.0
    dens_n = np.clip(dens / dmax, 0, 1)
    idx = (dens_n * (len(LUT) - 1)).astype(np.int32)
    rgb = LUT[idx]  # (H, W, 3)

    # bloom: difuminar y sumar con screen blend para el brillo "neon"
    bright = np.clip((dens_n - 0.45) / 0.55, 0, 1)[..., None] * rgb
    glow_img = Image.fromarray(np.clip(bright, 0, 255).astype(np.uint8))
    blur_radius = max(2, int(round(7 * (W / 1080))))
    glow_blur = np.array(glow_img.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float32)

    screen = 255 - (255 - rgb) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)
    return final


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"Render: {W}x{H}, {T} frames, {N_POINTS} puntos x {ITERS} iters")
    t_start = time.time()
    for t in range(T):
        frame = render_frame(t)
        Image.fromarray(frame).save(os.path.join(FRAMES_DIR, f"frame_{t:04d}.png"))
        if t % 5 == 0 or t == T - 1:
            elapsed = time.time() - t_start
            print(f"  frame {t + 1}/{T}  ({elapsed:.1f}s elapsed)")
    print(f"Listo. {T} frames en {FRAMES_DIR}  ({time.time() - t_start:.1f}s total)")


if __name__ == "__main__":
    main()
