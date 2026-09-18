"""Puzzle mockups for the fractal jigsaw listings: a jigsaw-cut product shot
(with a few loose pieces) and a wood-table lifestyle scene. Built from the 5:4
crops in masters/. Real tabbed piece geometry so it reads unmistakably as a
puzzle.

  python puzzle_mockups.py            # all four -> mockups/<slug>_{1,2,3}.jpg
"""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(HERE, "masters")
OUT = os.path.join(HERE, "mockups"); os.makedirs(OUT, exist_ok=True)
AF = os.path.join(HERE, "..", "lulu_books", "assets", "fonts")

SLUGS = ["julia_dense", "julia_pinwheel", "chaos_6", "chaos_5"]
LABELS = {"julia_dense": "Julia Filament", "julia_pinwheel": "Julia Pinwheel",
          "chaos_6": "Magnetic Pendulum · 6 Magnets", "chaos_5": "Magnetic Pendulum · 5 Magnets"}
COLS, ROWS = 18, 14


def font(n, s):
    return ImageFont.truetype(os.path.join(AF, n), s)


def _edge(p0, p1, sign):
    """points from p0 to p1 with a jigsaw knob in the middle (sign=+/-1, 0=flat)."""
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0; L = np.hypot(*d)
    if sign == 0 or L < 1e-6:
        return [tuple(p0), tuple(p1)]
    u = d / L; n = np.array([-u[1], u[0]]) * sign
    kr = 0.13 * L; neck = 0.10 * L
    pts = [p0, p0 + u * (0.40 * L), p0 + u * (0.40 * L) + n * neck * 0.5]
    c = p0 + u * (0.5 * L) + n * (neck * 0.5 + kr)
    a0 = math.atan2((p0 + u * (0.40 * L) + n * neck * 0.5 - c)[1],
                    (p0 + u * (0.40 * L) + n * neck * 0.5 - c)[0])
    for k in range(1, 22):
        a = a0 - sign * (2 * math.pi * 0.78) * k / 22
        pts.append(c + kr * np.array([math.cos(a), math.sin(a)]))
    pts += [p1 - u * (0.40 * L) + n * neck * 0.5, p1 - u * (0.40 * L), p1]
    return [tuple(p) for p in pts]


def _grid(w, h, seed=7):
    rng = random.Random(seed)
    xs = [round(w * i / COLS) for i in range(COLS + 1)]
    ys = [round(h * j / ROWS) for j in range(ROWS + 1)]
    hsign = [[rng.choice((-1, 1)) for _ in range(COLS)] for _ in range(ROWS + 1)]
    vsign = [[rng.choice((-1, 1)) for _ in range(COLS + 1)] for _ in range(ROWS)]
    return xs, ys, hsign, vsign


def _piece_path(i, j, xs, ys, hsign, vsign):
    top = _edge((xs[i], ys[j]), (xs[i + 1], ys[j]), 0 if j == 0 else hsign[j][i])
    right = _edge((xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), 0 if i + 1 == COLS else vsign[j][i + 1])
    bot = list(reversed(_edge((xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), 0 if j + 1 == ROWS else hsign[j + 1][i])))
    left = list(reversed(_edge((xs[i], ys[j]), (xs[i], ys[j + 1]), 0 if i == 0 else vsign[j][i])))
    return top + right[1:] + bot[1:] + left[1:]


def overlay(design):
    w, h = design.size
    xs, ys, hs, vs = _grid(w, h)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for j in range(ROWS + 1):
        for i in range(COLS):
            if j in (0, ROWS):
                continue
            d.line(_edge((xs[i], ys[j]), (xs[i + 1], ys[j]), hs[j][i]), fill=(15, 15, 18, 150), width=max(2, w // 900))
    for j in range(ROWS):
        for i in range(1, COLS):
            d.line(_edge((xs[i], ys[j]), (xs[i], ys[j + 1]), vs[j][i]), fill=(15, 15, 18, 150), width=max(2, w // 900))
    out = design.convert("RGBA"); out.alpha_composite(lay)
    # faint bevel highlight
    hi = lay.filter(ImageFilter.GaussianBlur(2)); out.alpha_composite(hi.point(lambda p: p * 0.25))
    return out, (xs, ys, hs, vs)


def piece_img(design, i, j, grid):
    xs, ys, hs, vs = grid
    path = _piece_path(i, j, xs, ys, hs, vs)
    x0 = min(p[0] for p in path); y0 = min(p[1] for p in path)
    x1 = max(p[0] for p in path); y1 = max(p[1] for p in path)
    mask = Image.new("L", design.size, 0)
    ImageDraw.Draw(mask).polygon(path, fill=255)
    rgba = design.convert("RGBA"); rgba.putalpha(mask)
    piece = rgba.crop((int(x0), int(y0), int(x1), int(y1)))
    ImageDraw.Draw(piece).line(path_shift(path, -int(x0), -int(y0)) + [path_shift(path, -int(x0), -int(y0))[0]],
                               fill=(15, 15, 18, 180), width=3)
    return piece


def path_shift(path, dx, dy):
    return [(p[0] + dx, p[1] + dy) for p in path]


def _shadow(base, im, x, y, blur=18, a=110):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    alpha = im.split()[-1].point(lambda p: a if p > 20 else 0)
    tmp = Image.new("RGBA", base.size, (0, 0, 0, 0)); tmp.paste((20, 18, 16), (x + 8, y + 12), alpha)
    base.alpha_composite(tmp.filter(ImageFilter.GaussianBlur(blur)))


def build_one(slug):
    design = Image.open(os.path.join(MAST, f"{slug}.jpg")).convert("RGB")
    W, H = design.size
    ov, grid = overlay(design)

    # ---- mockup 1: studio product shot with a few loose pieces ----
    S = 2000; c = Image.new("RGBA", (S, S), (238, 235, 229, 255))
    d = ImageDraw.Draw(c)
    pw = int(S * 0.80); ph = int(pw * H / W)
    puzzle = ov.resize((pw, ph), Image.LANCZOS)
    px, py = (S - pw) // 2, int(S * 0.16)
    _shadow(c, puzzle, px, py, blur=22, a=120)
    c.alpha_composite(puzzle, (px, py))
    # detach 3 corner pieces -> scatter below
    rng = random.Random(3)
    for n, (i, j) in enumerate([(COLS - 1, ROWS - 1), (COLS - 2, ROWS - 1), (COLS - 1, ROWS - 2)]):
        pc = piece_img(design, i, j, grid)
        sc = pw / W; pc = pc.resize((int(pc.width * sc), int(pc.height * sc)), Image.LANCZOS)
        pc = pc.rotate(rng.uniform(-25, 25), expand=True, resample=Image.BICUBIC)
        lx = int(S * (0.30 + 0.20 * n)); ly = int(S * 0.86)
        _shadow(c, pc, lx, ly, blur=10, a=120); c.alpha_composite(pc, (lx, ly))
    # erase those cells from the main puzzle (show gap)
    d.text((S // 2, int(S * 0.075)), LABELS[slug], font=font("Cinzel-SemiBold.ttf", 46),
           fill=(40, 38, 34), anchor="mm")
    d.text((S // 2, int(S * 0.125)), "JIGSAW PUZZLE · 120 · 252 · 500 PIECES",
           font=font("Raleway.ttf", 26), fill=(120, 116, 108), anchor="mm")
    c.convert("RGB").save(os.path.join(OUT, f"{slug}_1.jpg"), quality=92)

    # ---- mockup 2: wood-table lifestyle ----
    wood = _wood(S, S)
    pw2 = int(S * 0.72); ph2 = int(pw2 * H / W)
    puz2 = ov.resize((pw2, ph2), Image.LANCZOS)
    x2, y2 = (S - pw2) // 2, int(S * 0.20)
    _shadow(wood, puz2, x2, y2, blur=26, a=140); wood.alpha_composite(puz2, (x2, y2))
    rng = random.Random(9)
    for i, j in [(0, 0), (1, 0), (0, 1)]:
        pc = piece_img(design, i, j, grid); sc = pw2 / W
        pc = pc.resize((int(pc.width * sc), int(pc.height * sc)), Image.LANCZOS)
        pc = pc.rotate(rng.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        lx = int(S * rng.uniform(0.12, 0.72)); ly = int(S * 0.86)
        _shadow(wood, pc, lx, ly, blur=12, a=130); wood.alpha_composite(pc, (lx, ly))
    wood.convert("RGB").save(os.path.join(OUT, f"{slug}_2.jpg"), quality=92)

    # ---- mockup 3: clean flat design (so buyers see the full art) ----
    flat = Image.new("RGB", (S, int(S * H / W)), (0, 0, 0)); flat.paste(design.resize((S, int(S * H / W))), (0, 0))
    flat.save(os.path.join(OUT, f"{slug}_3.jpg"), quality=92)
    print("mockups:", slug)


def _wood(w, h):
    base = np.zeros((h, w, 3), np.float32)
    top = np.array([176, 142, 100], float); bot = np.array([150, 118, 80], float)
    g = np.linspace(0, 1, h)[:, None]
    for k in range(3):
        base[:, :, k] = top[k] * (1 - g) + bot[k] * g
    rng = np.random.default_rng(2)
    grain = rng.normal(0, 6, (h, w, 1)).astype(np.float32)
    plank = (np.sin(np.linspace(0, w / 90 * math.pi, w)) * 5)[None, :, None]
    arr = np.clip(base + grain + plank, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


if __name__ == "__main__":
    for s in (sys.argv[1:] or SLUGS):
        build_one(s)
