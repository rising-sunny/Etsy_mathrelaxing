"""
generate_turing_field.py — Gray-Scott reaction-diffusion solver
==================================================================
Simulates the actual Turing/Gray-Scott PDE (not a decorative noise
texture) for six (f, k) parameter pairs, each landing in a different,
visually distinct pattern class -- the same handful of pattern families
that show up on real animal skins and shells. Saves each result as a
16-bit-precision .npy field (so the plate renderer can apply its own
per-plate color gradient) plus a quick preview PNG.

  python generate_turing_field.py
"""
import os
import time

import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(BASE, "fields")
os.makedirs(FIELDS, exist_ok=True)

W_IN, H_IN = 9.0, 11.5
GRID_W = 340
GRID_H = round(GRID_W * H_IN / W_IN)  # match the plate's aspect so the field
                                        # doesn't need non-uniform stretching
STEPS = 11000
DU, DV = 0.16, 0.08

# (slug, f, k, seed) -- tuned by visual inspection at low-res before
# committing to a full run; each lands in a distinct Gray-Scott regime.
PRESETS = [
    ("leopard_rosettes", 0.0367, 0.0649, 2),
    ("pufferfish_mesh", 0.039, 0.058, 2),
    ("brain_coral", 0.0545, 0.062, 2),
    ("tiger_current", 0.022, 0.051, 2),
    ("fingerprint_whorl", 0.058, 0.063, 2),
    ("cuttlefish_static", 0.018, 0.051, 2),
]


def laplacian(Z):
    return (
        np.roll(Z, 1, axis=0) + np.roll(Z, -1, axis=0)
        + np.roll(Z, 1, axis=1) + np.roll(Z, -1, axis=1) - 4 * Z
    )


def run_gray_scott(f, k, steps=STEPS, w=GRID_W, h=GRID_H, seed=0):
    rng = np.random.default_rng(seed)
    U = np.ones((h, w))
    V = np.zeros((h, w))
    # seed blobs scattered across the *whole* domain (not just the center)
    # so growth fronts start everywhere and fill the frame within the step
    # budget -- a few center-only seeds left visible unfilled corners on a
    # large grid even though the same approach fully filled a small one.
    r = min(w, h) // 22
    n_seeds = max(40, (w * h) // 3000)
    for _ in range(n_seeds):
        cy = rng.integers(r, h - r)
        cx = rng.integers(r, w - r)
        U[cy - r:cy + r, cx - r:cx + r] = 0.50
        V[cy - r:cy + r, cx - r:cx + r] = 0.25
    U += 0.02 * rng.standard_normal((h, w))
    V += 0.02 * rng.standard_normal((h, w))
    for _ in range(steps):
        Lu, Lv = laplacian(U), laplacian(V)
        UVV = U * V * V
        U += DU * Lu - UVV + f * (1 - U)
        V += DV * Lv + UVV - (f + k) * V
    return U, V


def main():
    for slug, f, k, seed in PRESETS:
        t0 = time.time()
        U, V = run_gray_scott(f, k, seed=seed)
        v = (V - V.min()) / (np.ptp(V) + 1e-9)
        np.save(os.path.join(FIELDS, f"{slug}.npy"), v.astype(np.float32))
        Image.fromarray((v * 255).astype(np.uint8)).save(os.path.join(FIELDS, f"{slug}_preview.png"))
        print(f"{slug}: f={f} k={k}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
