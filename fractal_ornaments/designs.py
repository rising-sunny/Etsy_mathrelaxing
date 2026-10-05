"""
Front + back artwork (1800 x 1800 px, round-safe) for the fractal ceramic ornaments
(Printify blueprint 1599, 2-side print). Fronts are pure mathematics; backs name the
shape and its formula.

  python designs.py      -> out/<key>_front.png, out/<key>_back.png, out/contact.jpg
"""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem")); sys.path.insert(0, os.path.join(REPO, "math_cards_xmas"))
from generate_advent import font, CREAM, NAVY, RED, PINE, GOLD
import generate_cards as GC

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
N = 1800
DEEP = (16, 24, 48); ICE = (214, 232, 245); GOLD2 = (232, 192, 104)


def circle_mask(im, bg):
    """Keep the art inside the round ornament; paint the corners with the background."""
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((0, 0, N, N), fill=255)
    base = Image.new("RGB", im.size, bg); base.paste(im, (0, 0), m); return base


def safe(im, bg, k=0.80, dy=0.0):
    """Shrink the motif into the ornament's safe zone, clear of the rim and the hanging hole."""
    sm = im.resize((int(N * k), int(N * k)), Image.LANCZOS)
    out = Image.new("RGB", (N, N), bg)
    m = Image.new("L", sm.size, 0); ImageDraw.Draw(m).ellipse((0, 0) + sm.size, fill=255)
    out.paste(sm, ((N - sm.width) // 2, (N - sm.height) // 2 + int(N * dy)), m)
    return out


def center(im, bg, tol=25):
    """Shift the motif so its bounding box is exactly centred in the round ornament."""
    a = np.asarray(im.convert("L")).astype(float); m = np.abs(a - np.median(a[:30, :30])) > tol
    ys, xs = np.nonzero(m)
    dx = int(round(N / 2 - (xs.min() + xs.max()) / 2)); dy = int(round(N / 2 - (ys.min() + ys.max()) / 2))
    out = Image.new("RGB", im.size, bg); out.paste(im, (dx, dy)); return out


def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


# ------------------------------------------------------------------ fronts
def f_koch():
    S = 2; im = Image.new("RGB", (N * S, N * S), NAVY); d = ImageDraw.Draw(im); rnd = random.Random(5)
    for _ in range(18):
        x, y, r = rnd.uniform(0.15, 0.85) * N * S, rnd.uniform(0.15, 0.85) * N * S, rnd.uniform(40, 90) * S
        q = GC.koch_pts(x, y, r, 3); d.line(q + [q[0]], fill=(60, 82, 125), width=3 * S)
    big = GC.koch_pts(N * S / 2, N * S * 0.50, N * S * 0.42, 5)
    d.polygon(big, fill=(34, 54, 96)); d.line(big + [big[0]], fill=ICE, width=10 * S)
    mid = GC.koch_pts(N * S / 2, N * S * 0.50, N * S * 0.42 / 3, 4)
    d.line(mid + [mid[0]], fill=GOLD2, width=6 * S)
    return circle_mask(im.resize((N, N), Image.LANCZOS), NAVY)


def smooth_escape(c, z0=None, it=400, julia=False):
    z = np.zeros_like(c) if not julia else z0.copy()
    cc = c if not julia else np.full_like(z0, c)
    n = np.zeros(z.shape); alive = np.ones(z.shape, bool)
    for k in range(it):
        z[alive] = z[alive] ** 2 + cc[alive]
        esc = alive & (np.abs(z) > 4)
        n[esc] = k + 1 - np.log2(np.log(np.abs(z[esc])))
        alive &= ~esc
    n[alive] = -1
    return n


def palette(t, stops):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,))
    xs = np.linspace(0, 1, len(stops))
    for ch in range(3):
        out[..., ch] = np.interp(t, xs, [s[ch] for s in stops])
    return out


def f_mandel():
    xs = np.linspace(-2.65, 1.15, N); ys = np.linspace(-1.9, 1.9, N)
    X, Y = np.meshgrid(xs, ys); n = smooth_escape(X + 1j * Y, it=300)
    t = np.where(n < 0, 0, np.sqrt(np.clip(n, 0, None) / 60) % 1.0)
    rgb = palette(t, [DEEP, (40, 60, 110), (120, 80, 60), GOLD2, (255, 240, 200), GOLD2, (40, 60, 110)])
    rgb[n < 0] = (12, 16, 30)
    return circle_mask(Image.fromarray(rgb.astype("uint8")), DEEP)


def f_julia():
    xs = np.linspace(-2.0, 2.0, N); X, Y = np.meshgrid(xs, np.linspace(-2.0, 2.0, N))
    z = X + 1j * Y; c = complex(-0.8, 0.156)
    n = np.zeros(z.shape); alive = np.ones(z.shape, bool)
    for k in range(300):
        z[alive] = z[alive] ** 2 + c
        esc = alive & (np.abs(z) > 4); n[esc] = k + 1 - np.log2(np.log(np.abs(z[esc]))); alive &= ~esc
    t = np.where(alive, 1, np.sqrt(n / 300))
    rgb = palette(t, [DEEP, (30, 50, 100), (90, 140, 200), ICE, (255, 255, 255)])
    return circle_mask(Image.fromarray(rgb.astype("uint8")), DEEP)


def f_golden():
    S = 2; im = Image.new("RGB", (N * S, N * S), CREAM); d = ImageDraw.Draw(im)
    cx = cy = N * S / 2; ga = math.pi * (3 - 5 ** 0.5); cols = [PINE, (52, 128, 92), RED, GOLD]
    for i in range(1, 1300):
        r = 23 * S * math.sqrt(i)
        if r > N * S * 0.47:
            break
        a = i * ga; x, y = cx + r * math.cos(a), cy + r * math.sin(a); rr = (10 + 0.010 * r / S) * S
        col = RED if i % 13 == 0 else GOLD if i % 8 == 0 else cols[i % 2]
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    return circle_mask(im.resize((N, N), Image.LANCZOS), CREAM)


def f_tree():
    S = 2; im = Image.new("RGB", (N * S, N * S), CREAM); d = ImageDraw.Draw(im); rnd = random.Random(4); tips = []
    def br(x, y, ang, L, depth):
        if depth == 0:
            tips.append((x, y)); return
        x2, y2 = x + L * math.cos(ang), y - L * math.sin(ang)
        d.line((x, y, x2, y2), fill=GC.lerp(GC.BROWN, PINE, min(1, (1 - depth / 11) * 1.6)), width=max(2, int(depth ** 1.55 * S * 0.9)))
        for s in (-1, 1):
            br(x2, y2, ang + s * math.radians(27 + rnd.uniform(-4, 4)), L * rnd.uniform(0.72, 0.78), depth - 1)
    br(N * S / 2, N * S * 0.86, math.pi / 2, 300 * S, 11)
    for x, y in rnd.sample(tips, 110):
        r = rnd.choice((11, 13, 16)) * S; d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice([RED, GOLD, RED]))
    return circle_mask(im.resize((N, N), Image.LANCZOS), CREAM)


def f_pi():
    S = 2; im = Image.new("RGB", (N * S, N * S), (150, 30, 44)); d = ImageDraw.Draw(im)
    digits = GC.pi_digits(1600); cx = cy = N * S / 2
    k = 0; th = 0.0; f_cache = {}
    while k < len(digits):
        r = 200 * S + 9.5 * S * th
        if r > N * S * 0.41:
            break
        size = int(18 * S + r * 0.045)
        f = f_cache.setdefault(size, font("bold", size))
        x, y = cx + r * math.cos(th), cy + r * math.sin(th)
        ch = digits[k] if k else "3"
        d.text((x - size * 0.3, y - size * 0.55), ch, font=f, fill=GOLD2 if k % 7 else (255, 236, 200))
        th += (size * 0.78) / r; k += 1
    pf = font("bold", 380 * S); ctext(d, cx, cy - 300 * S, "π", pf, (255, 240, 210))
    return circle_mask(im.resize((N, N), Image.LANCZOS), (150, 30, 44))


# ------------------------------------------------------------------ backs
def back(title, lines, bg=NAVY, fg=CREAM, accent=GOLD2):
    S = 2; im = Image.new("RGB", (N * S, N * S), bg); d = ImageDraw.Draw(im)
    cx = N * S / 2
    # snowflake on top
    def flake(x, y, r, col, w):
        for k in range(6):
            a = k * math.pi / 3; d.line((x, y, x + r * math.cos(a), y + r * math.sin(a)), fill=col, width=w)
            for t in (0.5,):
                bx, by = x + r * t * math.cos(a), y + r * t * math.sin(a)
                for s in (-1, 1):
                    b = a + s * math.pi / 4; d.line((bx, by, bx + r * 0.3 * math.cos(b), by + r * 0.3 * math.sin(b)), fill=col, width=w)
    flake(cx, 470 * S, 90 * S, accent, 8 * S)
    tf = font("cinzel", 150 * S)
    y = 640 * S
    for t in title.split("\n"):
        ctext(d, cx, y, t, tf, fg); y += 170 * S
    y += 30 * S
    d.line((cx - 220 * S, y, cx + 220 * S, y), fill=accent, width=5 * S); y += 60 * S
    for s in lines:
        f = font("semi", 74 * S); ctext(d, cx, y, s, f, accent if s == lines[0] else fg); y += 100 * S
    ctext(d, cx, 1450 * S, "MathRelaxing", font("cinzel_r", 48 * S), accent)
    return circle_mask(im.resize((N, N), Image.LANCZOS), bg)


DESIGNS = [
    ("koch", f_koch, "Koch\nSnowflake", ["infinite perimeter", "finite area"], "Koch Snowflake",
     "the Koch snowflake: replace the middle third of every edge with a triangle, forever. Its edge is infinitely long, yet it encloses a finite area"),
    ("mandelbrot", f_mandel, "Mandelbrot\nSet", ["z² + c", "infinite detail"], "Mandelbrot Set",
     "the Mandelbrot set, drawn from the simple rule z² + c, whose boundary holds infinite detail at every zoom"),
    ("julia", f_julia, "Julia\nSet", ["z² + c", "c = -0.8 + 0.156i"], "Julia Set",
     "a Julia set (z² + c with c = -0.8 + 0.156i), a fractal of endlessly repeating icy spirals"),
    ("golden", f_golden, "Golden\nAngle", ["137.5°", "Fibonacci spirals"], "Golden Angle",
     "a sunflower pattern where every dot turns by the golden angle, 137.5 degrees, so Fibonacci spirals appear"),
    ("tree", f_tree, "Fractal\nTree", ["2,048 branches", "self-similar"], "Fractal Tree",
     "a fractal tree: every branch splits into two smaller copies of itself, eleven times over, ending in 2,048 tips"),
    ("pi", f_pi, "Pi", ["3.14159...", "never ends, never repeats"], "Pi Spiral",
     "the digits of pi spiralling out from the centre, more than a thousand of them, an irrational number that never ends"),
]


if __name__ == "__main__":
    tiles = []
    for key, ff, title, lines, *_ in DESIGNS:
        fr = ff()
        if key in ("koch", "golden", "tree", "pi"):
            fr = safe(fr, fr.getpixel((5, 5)))
            fr = center(fr, fr.getpixel((5, 5)))
        elif key == "julia":
            fr = center(fr, fr.getpixel((5, 5)), tol=40)
        fr.save(os.path.join(OUT, f"{key}_front.png"))
        bk = safe(back(title, lines), NAVY, k=0.86, dy=0.03); bk.save(os.path.join(OUT, f"{key}_back.png"))
        tiles += [fr, bk]; print("design", key)
    t = 360; C = Image.new("RGB", (4 * t, 3 * t), "white")
    for i, im in enumerate(tiles):
        C.paste(im.resize((t, t)), ((i % 4) * t, (i // 4) * t))
    C.save(os.path.join(OUT, "contact.jpg"))
