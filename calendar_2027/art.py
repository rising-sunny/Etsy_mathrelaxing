"""
12 landscape artworks (3375 x 2625 px, Printify 2027 wall calendar) for the
"2027 Mathematical Art Calendar", one mathematical idea per month, plus cover and
back cover. Everything is computed from the mathematics (numpy + PIL).

  python art.py            # renders out/01_jan.jpg ... out/12_dec.jpg, cover.jpg, back.jpg
  python art.py jul        # re-render one month
"""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
from generate_advent import font

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
W, H = 3375, 2625
NAVY = (18, 26, 52); CREAM = (248, 244, 235); GOLD = (214, 172, 88)


def pal(t, stops):
    t = np.clip(t, 0, 1); xs = np.linspace(0, 1, len(stops)); out = np.zeros(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, xs, [s[c] for s in stops])
    return out.astype(np.uint8)


def grid(cx, cy, width, w=W, h=H):
    xs = np.linspace(cx - width / 2, cx + width / 2, w)
    hh = width * h / w; ys = np.linspace(cy - hh / 2, cy + hh / 2, h)
    X, Y = np.meshgrid(xs, ys); return X + 1j * Y


def escape(Z, C, it, julia):
    z = Z.copy(); c = C if not julia else C
    n = np.full(z.shape, -1.0); alive = np.ones(z.shape, bool)
    for k in range(it):
        if julia:
            z[alive] = z[alive] ** 2 + c
        else:
            z[alive] = z[alive] ** 2 + c[alive]
        esc = alive & (np.abs(z) > 8)
        n[esc] = k + 1 - np.log2(np.log(np.abs(z[esc])))
        alive &= ~esc
    return n


def density_image(xs, ys, bounds, stops, bg, gamma=0.45, blur=0.0):
    x0, x1, y0, y1 = bounds
    Hh, _, _ = np.histogram2d(ys, xs, bins=(H, W), range=((y0, y1), (x0, x1)))
    if blur:
        Hh = np.asarray(Image.fromarray((Hh / Hh.max() * 65535).astype(np.uint16)).filter(ImageFilter.GaussianBlur(blur))).astype(float)
    t = np.log1p(Hh) / np.log1p(Hh.max())
    img = pal(t ** gamma, stops); img[Hh == 0] = bg
    return Image.fromarray(img)


# ------------------------------------------------------------------ months
def jan():  # icy Julia set
    Z = grid(0, 0, 3.3); n = escape(Z, complex(-0.8, 0.156), 500, True)
    t = np.where(n < 0, 0.0, np.clip(np.log1p(np.clip(n, 0, None)) / np.log1p(140), 0, 1))
    img = pal(t, [(6, 12, 30), (18, 40, 86), (60, 120, 190), (190, 225, 250), (255, 255, 255)])
    img[n < 0] = (12, 24, 54); return Image.fromarray(img)


def feb():  # cardioid by modular multiplication (times table mod N)
    S = 2; im = Image.new("RGB", (W * S, H * S), (40, 10, 28)); d = ImageDraw.Draw(im)
    cx, cy, R = W * S / 2, H * S / 2, H * S * 0.43; N = 360
    P = [(cx + R * math.cos(2 * math.pi * k / N - math.pi), cy + R * math.sin(2 * math.pi * k / N - math.pi)) for k in range(N)]
    for k in range(N):
        t = k / N
        col = tuple(int(a + (b - a) * t) for a, b in zip((255, 120, 150), (255, 210, 120)))
        d.line((P[k], P[(2 * k) % N]), fill=col, width=2 * S)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 170, 170), width=3 * S)
    return im.resize((W, H), Image.LANCZOS)


def mar():  # Barnsley fern (chaos game with many parallel walkers)
    rng = np.random.default_rng(3); n = 400_000; steps = 40
    x = np.zeros(n); y = np.zeros(n); xs, ys = [], []
    A = [(0, 0, 0, 0.16, 0, 0), (0.85, 0.04, -0.04, 0.85, 0, 1.6), (0.2, -0.26, 0.23, 0.22, 0, 1.6), (-0.15, 0.28, 0.26, 0.24, 0, 0.44)]
    pr = np.array([0.01, 0.85, 0.07, 0.07])
    for s in range(steps):
        k = rng.choice(4, n, p=pr); nx = np.empty(n); ny = np.empty(n)
        for i, (a, b, c, dd, e, f) in enumerate(A):
            m = k == i; nx[m] = a * x[m] + b * y[m] + e; ny[m] = c * x[m] + dd * y[m] + f
        x, y = nx, ny
        if s > 8:
            xs.append(x.copy()); ys.append(y.copy())
    X = np.concatenate(xs); Y = np.concatenate(ys)
    # landscape: lay the fern sideways with a slight tilt
    a = math.radians(-62); Xr = X * math.cos(a) - Y * math.sin(a); Yr = X * math.sin(a) + Y * math.cos(a)
    w = (Xr.max() - Xr.min()) * 1.08; cx = (Xr.max() + Xr.min()) / 2; cy = (Yr.max() + Yr.min()) / 2; h = w * H / W
    return density_image(Xr, -Yr, (cx - w / 2, cx + w / 2, -cy - h / 2, -cy + h / 2),
                         [(236, 242, 226), (120, 170, 90), (40, 110, 60), (14, 60, 36)], (244, 246, 236), gamma=0.5)


def apr():  # phyllotaxis blossoms
    S = 2; im = Image.new("RGB", (W * S, H * S), (250, 240, 240)); d = ImageDraw.Draw(im); rnd = random.Random(8)
    ga = math.pi * (3 - 5 ** 0.5)
    flowers = [(0.27, 0.48, 0.30, ((236, 120, 150), (250, 200, 120))), (0.68, 0.38, 0.24, ((150, 120, 210), (240, 200, 230))),
               (0.78, 0.78, 0.15, ((240, 150, 90), (255, 230, 150))), (0.52, 0.82, 0.12, ((110, 170, 140), (220, 240, 200))),
               (0.10, 0.12, 0.10, ((236, 120, 150), (255, 220, 230))), (0.95, 0.10, 0.09, ((120, 170, 220), (220, 236, 250)))]
    for fx, fy, fr, (c0, c1) in flowers:
        cx, cy, R = fx * W * S, fy * H * S, fr * H * S; n = int(900 * (fr / 0.3) ** 1.2) + 120
        c_ = R / math.sqrt(n)
        for i in range(n, 0, -1):
            r = c_ * math.sqrt(i); a = i * ga; x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            t = i / n; col = tuple(int(p + (q - p) * (1 - t)) for p, q in zip(c0, c1))
            rr = c_ * (0.55 + 0.25 * t)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    return im.resize((W, H), Image.LANCZOS)


def may():  # Lorenz attractor (butterfly effect)
    s, r, b = 10.0, 28.0, 8 / 3; dt = 0.0025; n = 1_400_000
    xs_, zs_ = [0.0] * n, [0.0] * n; X, Y, Z = 0.1, 0.0, 20.0
    def f(x, y, z):
        return s * (y - x), x * (r - z) - y, x * y - b * z
    for i in range(n):
        a1 = f(X, Y, Z); a2 = f(X + dt / 2 * a1[0], Y + dt / 2 * a1[1], Z + dt / 2 * a1[2])
        a3 = f(X + dt / 2 * a2[0], Y + dt / 2 * a2[1], Z + dt / 2 * a2[2]); a4 = f(X + dt * a3[0], Y + dt * a3[1], Z + dt * a3[2])
        X += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]); Y += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])
        Z += dt / 6 * (a1[2] + 2 * a2[2] + 2 * a3[2] + a4[2]); xs_[i] = X; zs_[i] = Z
    x, z = np.array(xs_[2000:]), np.array(zs_[2000:])
    # interpolate between samples so the trace is continuous
    xi = np.concatenate([x[:-1] + (x[1:] - x[:-1]) * t for t in (0, 0.33, 0.66)])
    zi = np.concatenate([z[:-1] + (z[1:] - z[:-1]) * t for t in (0, 0.33, 0.66)])
    w = 58; h = w * H / W
    return density_image(xi, -zi, (-w / 2, w / 2, -25 - h / 2, -25 + h / 2),
                         [(10, 22, 40), (20, 90, 130), (60, 190, 200), (220, 250, 250)], (8, 16, 32), gamma=0.55)


def jun():  # harmonograph
    t = np.linspace(0, 240, 3_000_000)
    x = np.sin(2.01 * t + 0.3) * np.exp(-0.0042 * t) + np.sin(3.0 * t + 1.7) * np.exp(-0.0031 * t)
    y = np.sin(3.003 * t) * np.exp(-0.0037 * t) + np.sin(2.0 * t + 0.9) * np.exp(-0.0045 * t)
    w = 4.6; h = w * H / W
    return density_image(x, y, (-w / 2, w / 2, -h / 2, h / 2), [(26, 20, 40), (150, 90, 60), (230, 180, 100), (255, 240, 200)],
                         (22, 18, 34), gamma=0.5)


def jul():  # Mandelbrot, seahorse valley
    Z = grid(-0.74364, 0.13183, 0.0125); n = escape(Z, Z, 1000, False)
    t = np.where(n < 0, 0, (np.log1p(np.clip(n, 0, None)) * 0.9) % 1.0)
    img = pal(t, [(10, 10, 30), (90, 20, 60), (220, 80, 40), (255, 200, 90), (255, 250, 230), (90, 20, 60), (10, 10, 30)])
    img[n < 0] = (6, 6, 16); return Image.fromarray(img)


def aug():  # Newton fractal for z^5 - 1
    Z = grid(0, 0, 3.4); z = Z.copy(); it = np.zeros(z.shape)
    for k in range(40):
        z = z - (z ** 5 - 1) / (5 * z ** 4 + 1e-12)
    roots = np.exp(2j * np.pi * np.arange(5) / 5)
    which = np.argmin(np.abs(z[..., None] - roots), axis=-1)
    z = Z.copy(); conv = np.zeros(z.shape)
    for k in range(30):
        z = z - (z ** 5 - 1) / (5 * z ** 4 + 1e-12)
        done = (np.min(np.abs(z[..., None] - roots), axis=-1) < 1e-3) & (conv == 0); conv[done] = k + 1
    cols = np.array([(250, 190, 60), (60, 170, 200), (230, 90, 110), (90, 190, 120), (160, 120, 220)], float)
    shade = np.clip(1.15 - conv / 18, 0.25, 1.0)[..., None]
    return Image.fromarray((cols[which] * shade).astype(np.uint8))


def sep():  # Heighway dragon curve
    turns = [1]
    for _ in range(17):
        turns = turns + [1] + [-t for t in reversed(turns)]
    d = 0; x = y = 0; pts = [(0, 0)]
    for t in turns:
        dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][d]; x += dx; y += dy; pts.append((x, y)); d = (d + t) % 4
    dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][d]; pts.append((x + dx, y + dy))
    P = np.array(pts, float); a = math.radians(30)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]); P = P @ R.T
    mn, mx = P.min(0), P.max(0); sc = min(W * 0.9 / (mx[0] - mn[0]), H * 0.9 / (mx[1] - mn[1]))
    P = (P - (mn + mx) / 2) * sc + (W / 2, H / 2)
    S = 2; im = Image.new("RGB", (W * S, H * S), (24, 16, 12)); dr = ImageDraw.Draw(im)
    stops = [(200, 50, 40), (240, 120, 40), (255, 200, 80), (255, 240, 190)]
    n = len(P) - 1; seg = 2000
    for i in range(0, n, seg):
        t = i / n; k = min(int(t * 3), 2); u = t * 3 - k
        col = tuple(int(stops[k][c] + (stops[k + 1][c] - stops[k][c]) * u) for c in range(3))
        dr.line([tuple(p * S) for p in P[i:i + seg + 1]], fill=col, width=max(2, int(sc * S * 0.55)))
    return im.resize((W, H), Image.LANCZOS)


def oct_():  # Clifford attractor
    a, b, c, d = -1.7, 1.8, -0.9, -0.4
    rng = np.random.default_rng(1); n = 300_000; x = rng.uniform(-1, 1, n); y = rng.uniform(-1, 1, n); xs, ys = [], []
    for k in range(70):
        x, y = np.sin(a * y) + c * np.cos(a * x), np.sin(b * x) + d * np.cos(b * y)
        if k > 5:
            xs.append(x); ys.append(y)
    X = np.concatenate(xs); Y = np.concatenate(ys)
    w = 4.4; h = w * H / W; cx = (X.max() + X.min()) / 2; cy = (Y.max() + Y.min()) / 2
    return density_image(X, Y, (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2),
                         [(22, 14, 30), (110, 40, 90), (220, 100, 50), (250, 200, 110), (255, 245, 220)], (18, 12, 24), gamma=0.5)


def nov():  # autumn fractal tree
    S = 2; im = Image.new("RGB", (W * S, H * S), (246, 238, 222)); d = ImageDraw.Draw(im); rnd = random.Random(11)
    tips = []
    def br(x, y, ang, L, depth):
        if depth == 0:
            tips.append((x, y)); return
        x2, y2 = x + L * math.cos(ang), y - L * math.sin(ang)
        d.line((x, y, x2, y2), fill=(70 + depth * 4, 50 + depth * 2, 36), width=max(2, int(depth ** 1.6 * S * 1.1)))
        for s in (-1, 1):
            br(x2, y2, ang + s * math.radians(25 + rnd.uniform(-6, 6)), L * rnd.uniform(0.70, 0.78), depth - 1)
    br(W * S / 2, H * S * 0.98, math.pi / 2, 520 * S, 13)
    leaf = [(196, 72, 34), (226, 130, 40), (238, 180, 60), (160, 50, 40), (200, 110, 60)]
    for x, y in tips:
        if rnd.random() < 0.85:
            r = rnd.uniform(7, 14) * S; d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=rnd.choice(leaf))
    for _ in range(260):  # falling leaves
        x, y, r = rnd.uniform(0, W * S), rnd.uniform(H * S * 0.55, H * S), rnd.uniform(8, 15) * S
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=rnd.choice(leaf))
    return im.resize((W, H), Image.LANCZOS)


def dec():  # Apollonian gasket (Descartes' circle theorem)
    S = 2; im = Image.new("RGB", (W * S, H * S), NAVY); d = ImageDraw.Draw(im)
    R = H * S * 0.46; cx, cy = W * S / 2, H * S / 2
    # start: outer circle (curvature -1/R) and three mutually tangent inner circles
    k1 = -1 / R; r2 = R * (2 * math.sqrt(3) - 3)  # three equal circles inside
    circles = [(complex(cx, cy), k1)]
    inner = []
    for j in range(3):
        a = -math.pi / 2 + 2 * math.pi * j / 3; c = complex(cx, cy) + (R - r2) * complex(math.cos(a), math.sin(a)); inner.append((c, 1 / r2))
    circles += inner
    seen = []
    def draw(c, k, depth):
        r = abs(1 / k); t = min(1, depth / 7)
        col = tuple(int(p + (q - p) * t) for p, q in zip((236, 196, 110), (130, 170, 230)))
        if depth % 2 == 1 and r > 6 * S:
            d.ellipse((c.real - r, c.imag - r, c.real + r, c.imag + r), fill=(26 + depth * 3, 38 + depth * 3, 74 + depth * 3))
        d.ellipse((c.real - r, c.imag - r, c.real + r, c.imag + r), outline=col, width=max(2 * S, int(min(6 * S, r / 9))))
    def new(c1, k1, c2, k2, c3, k3, c4, k4):  # reflection of circle 4 across the others
        k = 2 * (k1 + k2 + k3) - k4
        c = (2 * (k1 * c1 + k2 * c2 + k3 * c3) - k4 * c4) / k
        return c, k
    def rec(a, b, c_, old, depth):
        n = new(*a, *b, *c_, *old)
        if 1 / n[1] < 2.5 * S or depth > 14:
            return
        draw(n[0], n[1], depth)
        rec(a, b, n, c_, depth + 1); rec(a, c_, n, b, depth + 1); rec(b, c_, n, a, depth + 1)
    # fourth initial circles (the two Soddy circles)
    o = circles[0]; A, B, C = inner
    for c in circles:
        draw(c[0], c[1], 0)
    ks = A[1] * 3 + 2 * math.sqrt(3 * A[1] * A[1])
    inner_soddy = (complex(cx, cy), ks); draw(*inner_soddy, 1)
    for (p, q, s_) in ((A, B, inner_soddy), (A, C, inner_soddy), (B, C, inner_soddy)):
        rec(p, q, s_, [x for x in (A, B, C) if x not in (p, q)][0], 2)
    for (p, q) in ((A, B), (A, C), (B, C)):
        rec(p, q, o, [x for x in (A, B, C) if x not in (p, q)][0], 2)
    rnd = random.Random(12)
    for _ in range(160):
        x, y, r = rnd.uniform(0, W * S), rnd.uniform(0, H * S), rnd.uniform(2, 6) * S
        d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 214, 240))
    return im.resize((W, H), Image.LANCZOS)


MONTHS = [
    ("jan", jan, "Julia Set", "z² + c, with c = -0.8 + 0.156i"),
    ("feb", feb, "Cardioid", "join k to 2k on a circle of 360 points"),
    ("mar", mar, "Barnsley Fern", "four affine maps, chosen at random"),
    ("apr", apr, "Phyllotaxis", "every seed turns by the golden angle, 137.5°"),
    ("may", may, "Lorenz Attractor", "the butterfly effect, 1963"),
    ("jun", jun, "Harmonograph", "two damped pendulums drawing together"),
    ("jul", jul, "Mandelbrot Set", "seahorse valley, z² + c"),
    ("aug", aug, "Newton Fractal", "Newton's method on z⁵ = 1"),
    ("sep", sep, "Dragon Curve", "fold a strip of paper in half, 17 times"),
    ("oct", oct_, "Clifford Attractor", "x' = sin(ay) + c cos(ax), y' = sin(bx) + d cos(by)"),
    ("nov", nov, "Fractal Tree", "every branch splits into two smaller copies"),
    ("dec", dec, "Apollonian Gasket", "Descartes' circle theorem, again and again"),
]


def caption(im, title, sub):
    d = ImageDraw.Draw(im); f1 = font("bold", 58); f2 = font("light", 44)
    w = max(d.textlength(title, font=f1), d.textlength(sub, font=f2)) + 90
    x0, y0 = W - w - 70, H - 210
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    o.rounded_rectangle((x0, y0, x0 + w, y0 + 150), radius=28, fill=(10, 14, 28, 150))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"); d = ImageDraw.Draw(im)
    d.text((x0 + 45, y0 + 18), title, font=f1, fill=(255, 255, 255)); d.text((x0 + 45, y0 + 88), sub, font=f2, fill=(230, 220, 200))
    return im


if __name__ == "__main__":
    only = sys.argv[1:]
    for i, (key, fn, title, sub) in enumerate(MONTHS, 1):
        p = os.path.join(OUT, f"{i:02d}_{key}.jpg")
        if only and key not in only:
            continue
        im = fn(); im.save(os.path.join(OUT, f"{i:02d}_{key}_raw.jpg"), quality=94)
        caption(im, title, sub).save(p, quality=94); print("rendered", key, flush=True)
