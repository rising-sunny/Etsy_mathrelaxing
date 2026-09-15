"""
generate_pendulum.py — Magnetic Pendulum fractal basins of attraction.

A damped pendulum swings over N magnets on a circle; each starting point is
coloured by the magnet it finally settles on, shaded by how long it took to
settle — the classic chaos "basin of attraction" fractal. Every pixel is
computed from the equation of motion (no drawing, no AI). Fully vectorised in
numpy: the whole grid is integrated at once.

  python generate_pendulum.py            # 3,4,5,6 magnets at final res
  python generate_pendulum.py 3 --res 1400   # quick single preview
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)

# jewel palette sampled to match the digital set (rust/teal/gold/red/blue/purple)
PAL = ["#b4552f", "#3d8b84", "#c39b3f", "#a83a48", "#3f5f8a", "#6d4e8c"]


def hx(c):
    c = c.lstrip("#"); return np.array([int(c[i:i+2], 16) for i in (0, 2, 4)], float) / 255


def render(n_mag, res, A=1.7, steps=300, dt=0.045, R=0.21, C=0.40, h=0.27,
           cap_r=0.11, v_thr=0.34):
    ang = np.pi / 2 + np.arange(n_mag) * 2 * np.pi / n_mag
    mx, my = np.cos(ang).astype(np.float32), np.sin(ang).astype(np.float32)
    xs = np.linspace(-A, A, res).astype(np.float32)
    X, Y = np.meshgrid(xs, xs)
    VX = np.zeros_like(X); VY = np.zeros_like(Y)
    captured = -np.ones(X.shape, np.int16)
    settle = np.full(X.shape, steps, np.float32)
    for step in range(steps):
        ax = -R * VX - C * X
        ay = -R * VY - C * Y
        for i in range(n_mag):
            dx = mx[i] - X; dy = my[i] - Y
            inv = (dx * dx + dy * dy + h * h) ** -1.5
            ax += dx * inv; ay += dy * inv
        VX += ax * dt; VY += ay * dt
        X += VX * dt; Y += VY * dt
        speed2 = VX * VX + VY * VY
        active = captured < 0
        if step % 4 == 0 and active.any():
            for i in range(n_mag):
                d2 = (X - mx[i]) ** 2 + (Y - my[i]) ** 2
                newly = active & (d2 < cap_r * cap_r) & (speed2 < v_thr * v_thr)
                captured[newly] = i; settle[newly] = step
    rem = captured < 0
    if rem.any():
        d2s = np.stack([(X - mx[i]) ** 2 + (Y - my[i]) ** 2 for i in range(n_mag)])
        nearest = np.argmin(d2s, axis=0).astype(np.int16)
        captured[rem] = nearest[rem]
    # colour: hue by magnet, value by settle time (fast = bright, slow = deep)
    t = settle / steps
    val = 0.30 + 0.72 * (1.0 - t) ** 0.55
    img = np.zeros((res, res, 3), np.float32)
    for i in range(n_mag):
        m = captured == i
        col = hx(PAL[i])
        for c in range(3):
            img[..., c][m] = col[c] * val[m]
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")
    # light dot at each magnet centre
    d = ImageDraw.Draw(out)
    for i in range(n_mag):
        px = int((mx[i] + A) / (2 * A) * res); py = int((my[i] + A) / (2 * A) * res)
        r = max(4, res // 240)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(238, 232, 220))
    return out


def build(res=4000):
    for n in (3, 4, 5, 6):
        print("rendering", n, "magnets @", res)
        im = render(n, res)
        im.save(os.path.join(MAST, f"pendulum_{n}.png"))
        print("  wrote pendulum_%d.png" % n)


if __name__ == "__main__":
    argv = sys.argv[1:]
    res = 3000
    if "--res" in argv:
        i = argv.index("--res"); res = int(argv[i + 1]); del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if args:
        n = int(args[0])
        render(n, res).save(os.path.join(MAST, f"pendulum_{n}.png"))
        print("wrote pendulum_%d.png @ %d" % (n, res))
    else:
        build(res)
