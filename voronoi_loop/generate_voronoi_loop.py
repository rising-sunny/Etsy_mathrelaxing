"""
generate_voronoi_loop.py
=========================
Genera los frames de "Voronoi Cell Garden" — animacion seamless de celdas
Voronoi respirando organicamente, con loop matematicamente perfecto.

Tecnica del loop perfecto:
  Cada semilla orbita su posicion base con una frecuencia angular que es un
  multiplo ENTERO de 2*pi / T (T = frames totales). Por lo tanto en t=0 y en
  t=T las semillas ocupan exactamente la misma posicion -> frame 0 == frame T,
  y el video puede repetirse infinitamente sin corte visible.

Paleta: violeta profundo (centro) -> magenta/rosa -> oro calido -> vuelve a
negro-violeta en el borde exterior (efecto "mandala flotando en el vacio"),
con lineas de borde de celda brillantes tipo vitral.

Uso:
  python generate_voronoi_loop.py            # genera 300 frames en frames/
  python generate_voronoi_loop.py --test     # genera solo 12 frames a menor
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

W = H = 1080 if not TEST else 270
FPS = 30
DURATION = 10
T = FPS * DURATION if not TEST else 12
K = 90               # numero de celdas/semillas
R_MAX = 800 * (W / 1080)   # radio que cubre incluso las esquinas del lienzo
CX = CY = W / 2
EDGE_WIDTH = 5.0 * (W / 1080)   # grosor del glow de borde en px
SEED = 42

rng = np.random.default_rng(SEED)

# ── Colocacion de semillas: espiral de angulo dorado (phyllotaxis) ──────────
GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))
i = np.arange(K)
r_home = R_MAX * np.sqrt((i + 0.5) / K)
theta_home = i * GOLDEN_ANGLE
home_x = CX + r_home * np.cos(theta_home)
home_y = CY + r_home * np.sin(theta_home)
r_norm = r_home / R_MAX  # 0 en el centro, 1 en el borde

# ── Movimiento orbital de cada semilla (loop exacto) ────────────────────────
orbit_r = rng.uniform(6, 26, size=K) * (W / 1080)
phase = rng.uniform(0, 2 * np.pi, size=K)
freq = rng.choice([1, 1, 1, 2], size=K)  # entero -> periodo exacto = T

def seed_positions(t):
    theta_t = 2 * np.pi * t / T
    ang = theta_t * freq + phase
    sx = home_x + orbit_r * np.cos(ang)
    sy = home_y + orbit_r * np.sin(ang)
    return sx.astype(np.float32), sy.astype(np.float32)

# ── Paleta: violeta -> magenta -> oro -> negro-violeta ──────────────────────
STOPS = [
    (0.00, (70, 15, 95)),
    (0.35, (200, 35, 120)),
    (0.65, (255, 170, 70)),
    (1.00, (18, 8, 22)),
]

def gradient(t):
    t = np.clip(t, 0, 1)
    for k in range(len(STOPS) - 1):
        t0, c0 = STOPS[k]
        t1, c1 = STOPS[k + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return tuple(c0[j] + (c1[j] - c0[j]) * f for j in range(3))
    return STOPS[-1][1]

hue_jitter = rng.uniform(-0.04, 0.04, size=K)
color_table = np.array(
    [gradient(np.clip(rn + hj, 0, 1)) for rn, hj in zip(r_norm, hue_jitter)],
    dtype=np.float32,
)  # (K, 3)

GLOW_COLOR = np.array([255, 235, 205], dtype=np.float32)

# ── Render de un frame, en bandas para no explotar memoria ─────────────────
ROW_CHUNK = max(1, (54 * 1080) // W)  # ~54 filas a 1080px, escala con W

def render_frame(t):
    sx, sy = seed_positions(t)
    out = np.empty((H, W, 3), dtype=np.float32)
    glow_layer = np.zeros((H, W, 3), dtype=np.float32)

    xs_full = np.arange(W, dtype=np.float32)

    for r0 in range(0, H, ROW_CHUNK):
        r1 = min(r0 + ROW_CHUNK, H)
        ys = np.arange(r0, r1, dtype=np.float32)[:, None]      # (rows,1)
        xs = xs_full[None, :]                                   # (1,W)

        dx = xs[:, :, None] - sx[None, None, :]                 # (rows,W,K)
        dy = ys[:, :, None] - sy[None, None, :]
        dist2 = dx * dx + dy * dy

        idx1 = np.argmin(dist2, axis=2)                          # (rows,W)
        d1 = np.take_along_axis(dist2, idx1[..., None], axis=2)[..., 0]

        rows_idx, cols_idx = np.indices(idx1.shape)
        dist2_masked = dist2.copy()
        dist2_masked[rows_idx, cols_idx, idx1] = np.inf
        d2 = dist2_masked.min(axis=2)

        d1s = np.sqrt(d1)
        d2s = np.sqrt(d2)

        base_rgb = color_table[idx1]                             # (rows,W,3)

        # ligero facetado: mas brillo cerca del centro de la celda
        facet = 1.0 - 0.18 * np.clip(d1s / (60.0 * (W / 1080)), 0, 1)
        base_rgb = base_rgb * facet[..., None]

        edge = np.clip(1.0 - (d2s - d1s) / EDGE_WIDTH, 0, 1) ** 1.6
        chunk_out = base_rgb * (1 - edge[..., None]) + GLOW_COLOR[None, None, :] * edge[..., None]

        out[r0:r1] = chunk_out
        glow_layer[r0:r1] = GLOW_COLOR[None, None, :] * edge[..., None]

    # bloom: difuminar las lineas brillantes y sumarlas (screen blend)
    glow_img = Image.fromarray(np.clip(glow_layer, 0, 255).astype(np.uint8))
    blur_radius = max(2, int(round(6 * (W / 1080))))
    glow_blur = np.array(glow_img.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float32)

    screen = 255 - (255 - out) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)
    return final


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"Render: {W}x{H}, {T} frames, chunk={ROW_CHUNK} filas")
    t_start = time.time()
    for t in range(T):
        frame = render_frame(t)
        Image.fromarray(frame).save(os.path.join(FRAMES_DIR, f"frame_{t:04d}.png"))
        if t % 10 == 0 or t == T - 1:
            elapsed = time.time() - t_start
            print(f"  frame {t+1}/{T}  ({elapsed:.1f}s elapsed)")
    print(f"Listo. {T} frames en {FRAMES_DIR}  ({time.time()-t_start:.1f}s total)")


if __name__ == "__main__":
    main()
