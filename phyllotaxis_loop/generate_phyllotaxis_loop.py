"""
generate_phyllotaxis_loop.py
=============================
Genera los frames de "Phyllotaxis Bloom" — un campo de particulas doradas
dispuestas segun el angulo dorado (el mismo patron que organiza las semillas
de un girasol), respirando y titilando en un loop perfecto e infinito.

Por que "phyllotaxis": cada particula se ubica en:
    r_home_i     = R_MAX * sqrt((i + 0.5) / N)
    theta_home_i = i * GOLDEN_ANGLE      (GOLDEN_ANGLE = pi * (3 - sqrt(5)))
exactamente la misma regla que reparte semillas en un girasol / piñas /
Voronoi Gardens de este mismo catalogo — la particula NUNCA abandona su
angulo, solo respira en radio y titila en brillo.

Tecnica del loop perfecto:
  Cada particula respira con r(t) = r_home * (1 + amp*sin(2*pi*t/T + fase)) y
  titila con brillo(t) = 0.5 + 0.5*sin(2*pi*k*t/T + fase2), donde k es un
  ENTERO (distinto por particula, para que no titilen todas en sincronia).
  Cualquier suma de senos con frecuencia entera respecto a T vuelve
  exactamente a su valor inicial en t=T: frame 0 == frame T.

Render: se escaturan las posiciones (un punto por particula) ponderadas por
su brillo en un acumulador, y se aplican dos pasadas de blur (nucleo fino +
halo ancho) en screen-blend para el efecto bokeh/glow — mismo enfoque que
generate_dejong_loop.py, pero sin iterar ningun sistema caotico: es directo
y rapido (no hace falta transitorio ni miles de iteraciones por frame).

Paleta: negro calido -> ambar profundo -> oro -> crema casi blanco en el
nucleo de cada particula — la paleta de marca MathRelaxing (GOLD/CREAM de
brand.py), para que esta pieza se sienta el "centro" de la identidad visual,
distinta de Thomas (oro+aqua, forma de atractor) y De Jong (cian, atractor).

Uso:
  python generate_phyllotaxis_loop.py            # 240 frames en frames/
  python generate_phyllotaxis_loop.py --test      # 8 frames, resolucion chica
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
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

N = 700 if not TEST else 150
SEED = 11
R_MAX = 470 * (W / 1080)
CX = CY = W / 2

BREATHE_FREQ = 1        # respiracion radial: 1 ciclo completo por loop
BREATHE_AMP = 0.05

rng = np.random.default_rng(SEED)

GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))
i = np.arange(N)
r_home = R_MAX * np.sqrt((i + 0.5) / N)
theta_home = i * GOLDEN_ANGLE
r_norm = r_home / R_MAX

breathe_phase = rng.uniform(0, 2 * np.pi, size=N)
twinkle_freq = rng.integers(1, 4, size=N)          # entero: 1, 2 o 3
twinkle_phase = rng.uniform(0, 2 * np.pi, size=N)
base_brightness = rng.uniform(0.55, 1.0, size=N)

# ── Paleta de densidad: ambar profundo -> oro -> crema (nucleo brillante) ───
STOPS = [
    (0.00, (10, 6, 2)),
    (0.30, (90, 55, 15)),
    (0.65, (201, 162, 75)),   # brand.GOLD
    (1.00, (248, 244, 235)),  # brand.CREAM
]

def gradient_lut(n=256):
    lut = np.zeros((n, 3), dtype=np.float32)
    for idx in range(n):
        t = idx / (n - 1)
        for k in range(len(STOPS) - 1):
            t0, c0 = STOPS[k]
            t1, c1 = STOPS[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                lut[idx] = [c0[j] + (c1[j] - c0[j]) * f for j in range(3)]
                break
    return lut

LUT = gradient_lut()

# color base por particula: nucleo mas cremoso cuanto mas brillante titile,
# mezclado con un tono segun su radio (centro mas calido, borde mas ambar)
edge_color = np.array([120, 70, 20], dtype=np.float32)
core_color = np.array([248, 244, 235], dtype=np.float32)
particle_rgb = edge_color[None, :] * (1 - (1 - r_norm[:, None]) * 0.3) + \
               core_color[None, :] * ((1 - r_norm[:, None]) * 0.3)


particle_radius = (1.1 + 2.6 * (1 - r_norm) ** 1.3) * (W / 1080)  # nucleo mas grande hacia el centro


def render_frame(t):
    theta_t = 2 * np.pi * t / T

    r = r_home * (1 + BREATHE_AMP * np.sin(BREATHE_FREQ * theta_t + breathe_phase))
    twinkle = 0.5 + 0.5 * np.sin(twinkle_freq * theta_t + twinkle_phase)
    brightness = base_brightness * (0.35 + 0.65 * twinkle)

    px = CX + r * np.cos(theta_home)
    py = CY + r * np.sin(theta_home)
    valid = (px >= -6) & (px < W + 6) & (py >= -6) & (py < H + 6)

    # nucleo: circulos rellenos, tamaño y opacidad segun brillo/posicion
    core = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(core)
    order = np.argsort(brightness)  # dibuja primero las tenues, encima las brillantes
    for k in order:
        if not valid[k]:
            continue
        rad = particle_radius[k] * (0.55 + 0.45 * brightness[k])
        col = tuple(int(c) for c in np.clip(particle_rgb[k] * (0.5 + 0.5 * brightness[k]), 0, 255))
        d.ellipse((px[k] - rad, py[k] - rad, px[k] + rad, py[k] + rad), fill=col)

    core_arr = np.array(core, dtype=np.float32)
    core_blur = np.array(core.filter(ImageFilter.GaussianBlur(max(0.6, 0.9 * (W / 1080)))), dtype=np.float32)

    # halo: solo los nucleos mas brillantes, difuminados con un radio grande (bloom)
    bright_mask = (brightness > 0.55)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(glow)
    for k in np.where(bright_mask & valid)[0]:
        rad = particle_radius[k] * (0.55 + 0.45 * brightness[k])
        col = tuple(int(c) for c in np.clip(particle_rgb[k] * brightness[k], 0, 255))
        dg.ellipse((px[k] - rad, py[k] - rad, px[k] + rad, py[k] + rad), fill=col)
    glow_blur = np.array(glow.filter(ImageFilter.GaussianBlur(max(2, 8 * (W / 1080)))), dtype=np.float32)

    screen = 255 - (255 - core_blur) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)
    return final


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"Render: {W}x{H}, {T} frames, {N} particulas")
    t_start = time.time()
    for t in range(T):
        frame = render_frame(t)
        Image.fromarray(frame).save(os.path.join(FRAMES_DIR, f"frame_{t:04d}.png"))
        if t % 20 == 0 or t == T - 1:
            elapsed = time.time() - t_start
            print(f"  frame {t + 1}/{T}  ({elapsed:.1f}s elapsed)")
    print(f"Listo. {T} frames en {FRAMES_DIR}  ({time.time() - t_start:.1f}s total)")


if __name__ == "__main__":
    main()
