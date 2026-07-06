"""
generate_rossler_print.py
===========================
Genera un art print estatico de alta resolucion del atractor de Rossler —
Tipo 5 del catalogo (STANDARDS.md): imagen fija print-ready, no animacion.

El sistema de Rossler (ecuaciones diferenciales, 1976):
    dx/dt = -y - z
    dy/dt = x + a*y
    dz/dt = b + z*(x - c)
    a = 0.2, b = 0.2, c = 5.7 (parametros clasicos, region caotica)

Tecnica: a diferencia de un mapa discreto (De Jong, Clifford), un flujo
continuo como Rossler necesita que cada trayectoria de MUCHAS vueltas para
revelar la estructura fina de bandas plegadas (la imagen clasica del
atractor) — con pocos pasos, muchas trayectorias en paralelo solo trazan
un anillo liso y borroso porque no les da tiempo a decorrelacionarse. Por
eso acá se usan POCAS trayectorias (unos cientos) integradas por MUCHISIMOS
pasos (cientos de miles), acumulando en un histograma de densidad DURANTE la
integracion (streaming) en vez de guardar cada punto — así la memoria no
depende de la cantidad de pasos.

Proyeccion: plano X-Y (la vista clasica que muestra la banda en espiral
plegandose sobre si misma).

Salida: 9000x12000 px (retrato, imprimible a 30x40in @300dpi — formato
poster/canvas grande), 3 variantes de color.

Uso:
  python generate_rossler_print.py                # render final 9000x12000
  python generate_rossler_print.py --test          # 900x1200, rapido, para revisar
  python generate_rossler_print.py --save-cache P  # ademas guarda el histograma crudo en P (.npy)
  python generate_rossler_print.py --load-cache P  # salta la simulacion, renderiza desde P
"""
import numpy as np
from PIL import Image, ImageFilter
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "rossler")

TEST = "--test" in sys.argv


def _arg_after(flag):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


SAVE_CACHE = _arg_after("--save-cache")
LOAD_CACHE = _arg_after("--load-cache")

if TEST:
    W, H = 900, 1200
    N_TRAJ = 300
    STEPS = 60_000
else:
    W, H = 9000, 12000
    N_TRAJ = 600
    # ~2.78x mas bins que la version 5400x7200 original; steps escalados en la
    # misma proporcion para mantener la densidad de puntos/bin (y por lo tanto
    # el mismo nivel de detalle fino tras el blur, que tambien escala con W).
    STEPS = 3_300_000

DT = 0.006
WARMUP = 2000        # pasos descartados para que decorrelacionen entre si
A, B, C = 0.2, 0.2, 5.7

# bounding box conocido del atractor de Rossler clasico (a=b=0.2, c=5.7)
# en el plano X-Y, con margen — evita tener que hacer una pasada de sondeo
X_LO, X_HI = -11.5, 13.0
Y_LO, Y_HI = -11.5, 9.0

rng = np.random.default_rng(7)


def rossler_deriv(x, y, z):
    dx = -y - z
    dy = x + A * y
    dz = B + z * (x - C)
    return dx, dy, dz


def rk4_step(x, y, z, dt):
    k1x, k1y, k1z = rossler_deriv(x, y, z)
    k2x, k2y, k2z = rossler_deriv(x + dt / 2 * k1x, y + dt / 2 * k1y, z + dt / 2 * k1z)
    k3x, k3y, k3z = rossler_deriv(x + dt / 2 * k2x, y + dt / 2 * k2y, z + dt / 2 * k2z)
    k4x, k4y, k4z = rossler_deriv(x + dt * k3x, y + dt * k3y, z + dt * k3z)
    x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
    y = y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y)
    z = z + dt / 6 * (k1z + 2 * k2z + 2 * k3z + k4z)
    return x, y, z


def fit_bounds_to_aspect(lo_x, hi_x, lo_y, hi_y, w, h):
    fig_w, fig_h = hi_x - lo_x, hi_y - lo_y
    target_ratio = w / h
    cur_ratio = fig_w / fig_h
    if cur_ratio > target_ratio:
        new_h = fig_w / target_ratio
        cy = (lo_y + hi_y) / 2
        lo_y, hi_y = cy - new_h / 2, cy + new_h / 2
    else:
        new_w = fig_h * target_ratio
        cx = (lo_x + hi_x) / 2
        lo_x, hi_x = cx - new_w / 2, cx + new_w / 2
    return lo_x, hi_x, lo_y, hi_y


def simulate_histogram():
    lo_x, hi_x, lo_y, hi_y = fit_bounds_to_aspect(X_LO, X_HI, Y_LO, Y_HI, W, H)
    sx = (W - 1) / (hi_x - lo_x)
    sy = (H - 1) / (hi_y - lo_y)

    # nube pequeña alrededor de un punto seguro dentro de la cuenca de
    # atraccion; cada trayectoria decorrelaciona de las demas con el tiempo,
    # y cada una individualmente "pinta" el atractor completo con suficientes
    # vueltas (ergodicidad) — por eso no hace falta que N_TRAJ sea grande.
    x = rng.uniform(-0.5, 0.5, N_TRAJ).astype(np.float64) + 1.0
    y = rng.uniform(-0.5, 0.5, N_TRAJ).astype(np.float64) + 1.0
    z = rng.uniform(-0.5, 0.5, N_TRAJ).astype(np.float64) + 1.0

    print(f"Integrando {N_TRAJ} trayectorias x {STEPS} pasos (warmup {WARMUP})...")
    t0 = time.time()
    for _ in range(WARMUP):
        x, y, z = rk4_step(x, y, z, DT)

    hist = np.zeros((H, W), dtype=np.float64)
    log_every = max(1, STEPS // 10)
    for i in range(STEPS):
        x, y, z = rk4_step(x, y, z, DT)
        px = ((x - lo_x) * sx).astype(np.int32)
        py = (H - 1 - (y - lo_y) * sy).astype(np.int32)
        valid = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        if valid.any():
            np.add.at(hist, (py[valid], px[valid]), 1.0)
        if i % log_every == 0:
            print(f"  paso {i}/{STEPS}  ({time.time()-t0:.1f}s)")
    print(f"Listo integrar. {time.time()-t0:.1f}s total")
    return hist


# ── Paletas: negro -> color -> nucleo casi blanco ───────────────────────────
PALETTES = {
    "classic_cyan": [(0.00, (3, 4, 10)), (0.35, (10, 60, 90)),
                      (0.68, (60, 200, 220)), (1.00, (225, 250, 255))],
    "violet_rose":  [(0.00, (8, 3, 12)), (0.35, (75, 20, 90)),
                      (0.68, (200, 70, 170)), (1.00, (255, 230, 245))],
    "amber_gold":   [(0.00, (10, 6, 2)), (0.35, (90, 55, 15)),
                      (0.68, (230, 165, 60)), (1.00, (255, 248, 225))],
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


def render_from_hist(hist, palette_name, out_path):
    dens = np.log1p(hist)
    dmax = dens.max() if dens.max() > 0 else 1.0
    dens_n = np.clip(dens / dmax, 0, 1)

    lut = gradient_lut(PALETTES[palette_name])
    idx = (dens_n * (len(lut) - 1)).astype(np.int32)
    rgb = lut[idx]

    # El blur ANTES escalaba con W (1.4*W/1080 -> 12px a 9000px, glow 58px):
    # a mayor resolucion, mas blur en pixeles absolutos, asi que el hilado fino
    # de la trayectoria quedaba siempre borrado por igual sin importar cuanto
    # zoom se hiciera. Aca el radio es casi fijo (solo antialiasing del
    # binning), independiente de la resolucion de salida, para que las lineas
    # finas del atractor sean visibles al hacer zoom en el print grande.
    core_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    blur_r = max(1, int(round(0.35 * (W / 1080))))
    core_blur = np.array(core_img.filter(ImageFilter.GaussianBlur(blur_r)), dtype=np.float32)

    bright = np.clip((dens_n - 0.45) / 0.55, 0, 1)[..., None] * rgb
    glow_img = Image.fromarray(np.clip(bright, 0, 255).astype(np.uint8))
    glow_r = max(2, int(round(1.8 * (W / 1080))))
    glow_blur = np.array(glow_img.filter(ImageFilter.GaussianBlur(glow_r)), dtype=np.float32)

    screen = 255 - (255 - core_blur) * (255 - glow_blur) / 255.0
    final = np.clip(screen, 0, 255).astype(np.uint8)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(final).save(out_path, quality=95)
    print("Guardado:", out_path)


def main():
    if LOAD_CACHE:
        print(f"Cargando histograma cacheado de {LOAD_CACHE}...")
        hist = np.load(LOAD_CACHE)
    else:
        hist = simulate_histogram()
        if SAVE_CACHE:
            np.save(SAVE_CACHE, hist)
            print(f"Histograma cacheado en {SAVE_CACHE}")
    suffix = "_test" if TEST else ""
    render_from_hist(hist, "classic_cyan", os.path.join(OUT, f"rossler_classic{suffix}.jpg"))
    render_from_hist(hist, "violet_rose", os.path.join(OUT, f"rossler_violet{suffix}.jpg"))
    render_from_hist(hist, "amber_gold", os.path.join(OUT, f"rossler_amber{suffix}.jpg"))


if __name__ == "__main__":
    main()
