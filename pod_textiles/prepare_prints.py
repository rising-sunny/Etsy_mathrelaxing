"""Prepare square print files for the textile POD line from existing masters
(upscaled to 6000 px) plus a crisp square op-art vortex. Regenerates
pod_textiles/prints/ (gitignored).

  python prepare_prints.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "prints"); os.makedirs(OUT, exist_ok=True)


def upscale(src, name, target=6000):
    im = Image.open(os.path.join(REPO, src)).convert("RGB")
    if im.width < target:
        im = im.resize((target, target), Image.LANCZOS)
    im.save(os.path.join(OUT, name), quality=94)
    print("prepared", name, im.size)


def opart_vortex_square(name="tex_opart_vortex.jpg", S=5000):
    y = np.linspace(-1, 1, S)[:, None]; x = np.linspace(-1, 1, S)[None, :]
    r = np.sqrt(x * x + y * y); th = np.arctan2(y, x)
    field = np.sin(24 * r * np.pi + 7 * th)
    gx = np.abs(np.gradient(field, axis=1)); gy = np.abs(np.gradient(field, axis=0))
    g = np.maximum(gx + gy, 1e-6); inten = np.clip(0.5 + field / (2 * g), 0, 1)[:, :, None]
    INK = np.array([16, 17, 20], float); PAPER = np.array([245, 242, 235], float)
    arr = (INK * (1 - inten) + PAPER * inten).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(os.path.join(OUT, name), quality=94)
    print("prepared", name, (S, S))


if __name__ == "__main__":
    upscale("julia_set/masters/julia_dense.png", "tex_julia_filament.jpg")
    upscale("julia_set/masters/julia_spiral.png", "tex_julia_spiral.jpg")
    upscale("chaos_pendulum_set/masters/pendulum_6.png", "tex_chaos_6.jpg")
    opart_vortex_square()
