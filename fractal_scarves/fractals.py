"""
Fractal scarf artwork, rendered in horizontal strips so very large images fit in memory.

Each design maps pixel (i, j) of an N x N image to the plane via centre (cx, cy), width w and a
rotation angle; numba kernels do the math; colour normalisation comes from a small preview.

  midnight_mandelbrot   Mandelbrot set, distance-estimate glow, navy and gold
  coral_julia           Julia set c = -0.8 + 0.156i (turned 45 deg to fill the square), teal and coral
  stained_glass         Newton fractal for z^3 - 1, jewel-tone basins with gold seams
  seahorse_valley       Mandelbrot zoom (Seahorse Valley), silver blue
  zircon_lyapunov       Markus-Lyapunov fractal, sequence AABAB, gold and sapphire
  golden_angle          Phyllotaxis: seeds placed at the golden angle, gold on black
"""
import math
import numpy as np
from numba import njit, prange


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def palette(stops, t):
    pos = np.array([p for p, _ in stops], np.float32); cols = np.array([hexrgb(c) for _, c in stops])
    t = np.clip(t, 0, 1).astype(np.float32); i = np.clip(np.searchsorted(pos, t) - 1, 0, len(pos) - 2)
    f = (t - pos[i]) / (pos[i + 1] - pos[i]); f = f * f * (3 - 2 * f)
    return cols[i] * (1 - f[..., None]) + cols[i + 1] * f[..., None]


@njit(inline="always")
def _coord(i, j, N, cx, cy, w, ca, sa):
    u = (i - (N - 1) / 2) / (N - 1) * w; v = (j - (N - 1) / 2) / (N - 1) * w
    return cx + u * ca - v * sa, cy + u * sa + v * ca


@njit(parallel=True, fastmath=True)
def mandel_strip(cx, cy, w, ang, N, j0, j1, maxit):
    H = j1 - j0; nu = np.zeros((H, N), np.float32); de = np.zeros((H, N), np.float32); inside = np.zeros((H, N), np.bool_)
    ca, sa = math.cos(ang), math.sin(ang)
    for jj in prange(H):
        for i in range(N):
            px, py = _coord(i, j0 + jj, N, cx, cy, w, ca, sa)
            zx = 0.0; zy = 0.0; dx = 0.0; dy = 0.0; k = 0
            while k < maxit:
                ndx = 2 * (zx * dx - zy * dy) + 1.0; ndy = 2 * (zx * dy + zy * dx); dx, dy = ndx, ndy
                zx, zy = zx * zx - zy * zy + px, 2 * zx * zy + py
                if zx * zx + zy * zy > 1e6:
                    break
                k += 1
            if k == maxit:
                inside[jj, i] = True
            else:
                r = math.sqrt(zx * zx + zy * zy)
                nu[jj, i] = k + 1 - math.log(math.log(r)) / math.log(2.0)
                de[jj, i] = r * math.log(r) / max(math.sqrt(dx * dx + dy * dy), 1e-30)
    return nu, de, inside


@njit(parallel=True, fastmath=True)
def julia_strip(cr, ci, cx, cy, w, ang, N, j0, j1, maxit):
    H = j1 - j0; nu = np.zeros((H, N), np.float32); inside = np.zeros((H, N), np.bool_)
    ca, sa = math.cos(ang), math.sin(ang)
    for jj in prange(H):
        for i in range(N):
            zx, zy = _coord(i, j0 + jj, N, cx, cy, w, ca, sa); k = 0
            while k < maxit and zx * zx + zy * zy < 1e6:
                zx, zy = zx * zx - zy * zy + cr, 2 * zx * zy + ci; k += 1
            if k == maxit:
                inside[jj, i] = True
            else:
                r = math.sqrt(zx * zx + zy * zy); nu[jj, i] = k + 1 - math.log(math.log(r)) / math.log(2.0)
    return nu, inside


@njit(parallel=True, fastmath=True)
def newton_strip(cx, cy, w, ang, N, j0, j1, maxit):
    H = j1 - j0; root = np.zeros((H, N), np.int8); its = np.zeros((H, N), np.float32)
    rr = np.array([1.0, -0.5, -0.5]); ri = np.array([0.0, math.sqrt(3) / 2, -math.sqrt(3) / 2])
    ca, sa = math.cos(ang), math.sin(ang)
    for jj in prange(H):
        for i in range(N):
            zx, zy = _coord(i, j0 + jj, N, cx, cy, w, ca, sa); k = 0; found = -1
            while k < maxit:
                x2 = zx * zx - zy * zy; y2 = 2 * zx * zy
                x3 = x2 * zx - y2 * zy; y3 = x2 * zy + y2 * zx
                nr = x3 - 1.0; ni = y3; dr = 3 * x2; di = 3 * y2; den = dr * dr + di * di
                if den < 1e-20:
                    break
                zx -= (nr * dr + ni * di) / den; zy -= (ni * dr - nr * di) / den
                for q in range(3):
                    if (zx - rr[q]) ** 2 + (zy - ri[q]) ** 2 < 1e-6:
                        found = q
                if found >= 0:
                    break
                k += 1
            root[jj, i] = found
            # smooth the iteration count with the final distance to the root
            its[jj, i] = k
    return root, its


@njit(parallel=True, fastmath=True)
def lyapunov_strip(a0, a1, b0, b1, N, j0, j1, seq, warm, n):
    H = j1 - j0; L = np.zeros((H, N), np.float32); m = len(seq)
    for jj in prange(H):
        b = b1 - (b1 - b0) * (j0 + jj) / (N - 1)
        for i in range(N):
            a = a0 + (a1 - a0) * i / (N - 1); x = 0.5; s = 0.0
            for k in range(warm + n):
                r = a if seq[k % m] == 0 else b
                x = r * x * (1 - x)
                if k >= warm:
                    s += math.log(max(abs(r * (1 - 2 * x)), 1e-12))
            L[jj, i] = s / n
    return L


# ------------------------------------------------------------------ designs: raw(N, j0, j1) and colour(raw, stats, N)
class Midnight:
    view = (-0.62, 0.0, 2.9, 0.0)
    def raw(self, N, j0, j1):
        return mandel_strip(*self.view, N, j0, j1, 900)
    def stats(self, raw, N):
        return {}
    def colour(self, raw, st, N):
        nu, de, inside = raw; pix = self.view[2] / N
        t = 1 - np.clip(np.log(np.maximum(de / pix, 1e-9)) / 6.0, 0, 1)
        rgb = palette([(0, "0b1026"), (0.45, "1d2b5a"), (0.75, "8a6a2c"), (0.9, "d9b25c"), (1, "fff4d4")], t ** 1.6)
        rgb[inside] = hexrgb("070b1c"); return rgb


class Coral:
    view = (0.0, 0.0, 2.45, math.pi / 4)
    def raw(self, N, j0, j1):
        return julia_strip(-0.8, 0.156, *self.view, N, j0, j1, 700)
    def stats(self, raw, N):
        nu, inside = raw; return {"hi": float(np.percentile(nu[~inside], 99.5))}
    def colour(self, raw, st, N):
        nu, inside = raw; t = np.log1p(nu) / np.log1p(st["hi"])
        rgb = palette([(0, "0d2b33"), (0.35, "1f6f78"), (0.6, "6cc3b7"), (0.8, "f2a65a"), (0.93, "f6d7b0"), (1, "fffaf0")], t)
        rgb[inside] = hexrgb("f4e3c8"); return rgb


class Stained:
    view = (0.0, 0.0, 2.2, math.pi / 2)
    def raw(self, N, j0, j1):
        a = max(j0 - 1, 0)      # one extra row above for the seam detector
        r, it = newton_strip(*self.view, N, a, j1, 80)
        return r, it, j0 - a
    def stats(self, raw, N):
        return {}
    def colour(self, raw, st, N):
        root, its, off = raw
        base = np.array([hexrgb("1f3c88"), hexrgb("1f8a70"), hexrgb("b23a48")])
        rgb = base[np.clip(root, 0, 2)] * np.clip(1.08 - its / 24, 0.28, 1.08)[..., None]
        g = np.zeros_like(its); g[1:, :] += np.abs(np.diff(its, axis=0)); g[:, 1:] += np.abs(np.diff(its, axis=1))
        lw = max(1.0, N / 2400)
        edge = np.clip(g / 3, 0, 1)
        if lw > 1:
            from scipy.ndimage import maximum_filter
            edge = maximum_filter(edge, size=int(round(lw)))
        edge = (edge * (its > 3))[..., None]
        rgb = rgb * (1 - edge) + hexrgb("e8c46a") * edge
        rgb[root < 0] = hexrgb("e8c46a")
        return rgb[off:]


class Seahorse:
    view = (-0.7453, 0.1127, 0.0065, 0.6)
    def raw(self, N, j0, j1):
        return mandel_strip(*self.view, N, j0, j1, 1600)
    def stats(self, raw, N):
        nu, de, inside = raw; t = np.log1p(nu[~inside])
        return {"lo": float(np.percentile(t, 1)), "hi": float(np.percentile(t, 99.7))}
    def colour(self, raw, st, N):
        nu, de, inside = raw; t = (np.log1p(nu) - st["lo"]) / (st["hi"] - st["lo"])
        rgb = palette([(0, "0a1a2f"), (0.4, "23476e"), (0.7, "7fa8c9"), (0.88, "dce8f0"), (1, "ffffff")], t)
        rgb[inside] = hexrgb("0a1a2f"); return rgb


class Zircon:
    def raw(self, N, j0, j1):
        return lyapunov_strip(2.6, 4.0, 2.6, 4.0, N, j0, j1, np.array([0, 0, 1, 0, 1], np.int64), 120, 400)
    def stats(self, raw, N):
        return {}
    def colour(self, L, st, N):
        rgb = np.zeros(L.shape + (3,), np.float32); neg = L < 0
        rgb[neg] = palette([(0, "3a2a0c"), (0.4, "a3782b"), (0.75, "e8c46a"), (1, "fff2c8")], np.clip(-L[neg] / 1.6, 0, 1) ** 0.55)
        rgb[~neg] = palette([(0, "0a1630"), (0.5, "1f3c88"), (1, "4f86c6")], np.clip(L[~neg] / 0.7, 0, 1) ** 0.6)
        return rgb


def golden_angle(N):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (N, N), (10, 12, 20)); d = ImageDraw.Draw(img)
    ga = math.pi * (3 - math.sqrt(5)); n = 2200; R = N * 0.46
    cols = palette([(0, "fff2c8"), (0.5, "e8c46a"), (1, "a3782b")], np.linspace(0, 1, n + 1))
    for k in range(n, 0, -1):
        r = R * math.sqrt(k / n); a = k * ga; t = k / n
        x, y = N / 2 + r * math.cos(a), N / 2 + r * math.sin(a); s = N * (0.0016 + 0.0048 * t)
        d.ellipse((x - s, y - s, x + s, y + s), fill=tuple(int(v) for v in cols[k]))
    return np.array(img)


DESIGNS = {
    "midnight_mandelbrot": ("Midnight Mandelbrot", "the Mandelbrot set", Midnight(), "e8c46a", "0b1026"),
    "coral_julia": ("Coral Julia", "a Julia set, c = -0.8 + 0.156i", Coral(), "f2a65a", "0d2b33"),
    "stained_glass": ("Stained Glass", "Newton's method for z³ = 1", Stained(), "e8c46a", "15224a"),
    "seahorse_valley": ("Seahorse Valley", "a deep zoom into the Mandelbrot set", Seahorse(), "dce8f0", "0a1a2f"),
    "zircon_lyapunov": ("Zircon", "a Markus-Lyapunov fractal", Zircon(), "e8c46a", "0a1630"),
    "golden_angle": ("Golden Angle", "seeds placed at the golden angle", golden_angle, "e8c46a", "0a0c14"),
}


def render(key, N, strip=600):
    """Full N x N uint8 RGB image of a design."""
    spec = DESIGNS[key][2]
    if callable(spec) and not hasattr(spec, "raw"):
        return spec(N)
    P = 800; st = spec.stats(spec.raw(P, 0, P), P)
    out = np.zeros((N, N, 3), np.uint8)
    for j0 in range(0, N, strip):
        j1 = min(N, j0 + strip)
        out[j0:j1] = np.clip(spec.colour(spec.raw(N, j0, j1), st, N), 0, 255).astype(np.uint8)
    return out
