"""Strange Attractors — a second printable bookmark set for MathRelaxing.

Reuses the exact render engine of the first set (generate_bookmarks.build_one:
2.25x6.25 in @ 300 DPI, black/cream + gold + Cinzel/Raleway + ∞ logo) but with
10 chaos attractors instead of curves. Output is redirected to this folder.

Designs: Lorenz · Clifford · De Jong · Rössler · Thomas · Aizawa · Halvorsen
· Ikeda · Svensson · Chen.
"""
import os, sys
import numpy as np
from scipy.integrate import odeint

BM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bookmarks")
sys.path.insert(0, BM)
import generate_bookmarks as GB          # reuse build_one / contact / grad / palette
from generate_bookmarks import grad, CMAP, GOLD

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
GB.OUT = OUT                              # redirect the engine's output here


# ── flows (3D systems, integrated then projected) ─────────────────────────────
def _flow(f, s0, t_end, n):
    t = np.linspace(0, t_end, n)
    return odeint(f, s0, t, mxstep=5000)


def a_lorenz(ax):
    s = _flow(lambda s, t: [10*(s[1]-s[0]), s[0]*(28-s[2])-s[1], s[0]*s[1]-8/3*s[2]],
              [1, 1, 1], 45, 22000)
    grad(ax, s[:, 0], s[:, 2], lw=0.7); ax.set_aspect("equal")


def a_rossler(ax):
    s = _flow(lambda s, t: [-s[1]-s[2], s[0]+0.2*s[1], 0.2+s[2]*(s[0]-5.7)],
              [0, 1, 0], 220, 26000)
    grad(ax, s[:, 0], s[:, 1], lw=0.8); ax.set_aspect("equal")


def a_thomas(ax):
    b = 0.208
    s = _flow(lambda s, t: [np.sin(s[1])-b*s[0], np.sin(s[2])-b*s[1], np.sin(s[0])-b*s[2]],
              [1.1, 1.1, -1], 320, 30000)
    grad(ax, s[:, 0], s[:, 1], lw=0.7); ax.set_aspect("equal")


def a_aizawa(ax):
    a, b, c, d, e, ff = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
    def f(s, t):
        x, y, z = s
        return [(z-b)*x-d*y, d*x+(z-b)*y,
                c+a*z-z**3/3-(x**2+y**2)*(1+e*z)+ff*z*x**3]
    s = _flow(f, [0.1, 0, 0], 110, 30000)
    grad(ax, s[:, 0], s[:, 2], lw=0.6); ax.set_aspect("equal")


def a_halvorsen(ax):
    a = 1.4
    def f(s, t):
        x, y, z = s
        return [-a*x-4*y-4*z-y*y, -a*y-4*z-4*x-z*z, -a*z-4*x-4*y-x*x]
    s = _flow(f, [-5, 0, 0], 45, 26000)
    grad(ax, s[:, 0], s[:, 1], lw=0.7); ax.set_aspect("equal")


def a_chen(ax):
    a, b, c = 35, 3, 28
    def f(s, t):
        x, y, z = s
        return [a*(y-x), (c-a)*x-x*z+c*y, x*y-b*z]
    s = _flow(f, [-7, -4, 35], 26, 26000)
    grad(ax, s[:, 0], s[:, 2], lw=0.6); ax.set_aspect("equal")


# ── maps (2D iterated systems, drawn as coloured point clouds) ─────────────────
def _iter(step, x0, y0, n=150000, burn=100):
    x = np.empty(n); y = np.empty(n)
    xi, yi = x0, y0
    for _ in range(burn):
        xi, yi = step(xi, yi)
    for i in range(n):
        xi, yi = step(xi, yi)
        x[i], y[i] = xi, yi
    return x, y


def _cloud(ax, x, y, s=0.15, alpha=0.35):
    ax.scatter(x, y, c=np.arange(len(x)), cmap=CMAP, s=s, alpha=alpha, linewidths=0)
    ax.set_aspect("equal")
    # clip the view to the dense body so rare transients can't shrink it
    ax.set_xlim(np.percentile(x, 0.3), np.percentile(x, 99.7))
    ax.set_ylim(np.percentile(y, 0.3), np.percentile(y, 99.7))


def a_clifford(ax):
    a, b, c, d = -1.4, 1.6, 1.0, 0.7
    x, y = _iter(lambda x, y: (np.sin(a*y)+c*np.cos(a*x), np.sin(b*x)+d*np.cos(b*y)), 0.1, 0.1)
    _cloud(ax, x, y)


def a_dejong(ax):
    a, b, c, d = 1.641, 1.902, 0.316, 1.525
    x, y = _iter(lambda x, y: (np.sin(a*y)-np.cos(b*x), np.sin(c*x)-np.cos(d*y)), 0.1, 0.1)
    _cloud(ax, x, y)


def a_svensson(ax):
    a, b, c, d = 1.4, 1.56, 1.4, -6.56
    x, y = _iter(lambda x, y: (d*np.sin(a*x)-np.sin(b*y), c*np.cos(a*x)+np.cos(b*y)), 0.1, 0.1)
    _cloud(ax, x, y)


def a_hopalong(ax):
    a, b, c = -2.0, -0.33, 0.01           # Barry Martin's "Hopalong" orbit
    def step(x, y):
        return y - np.sign(x)*np.sqrt(abs(b*x - c)), a - x
    x, y = _iter(step, 0.0, 0.0, n=240000, burn=50)
    _cloud(ax, x, y, s=0.2, alpha=0.45)


DESIGNS = [
    ("lorenz",    "The Lorenz Attractor",  r"$\dot{x}=\sigma(y-x)$",           "dark",  a_lorenz,    "the butterfly effect"),
    ("clifford",  "The Clifford Attractor",r"$x' = \sin ay + c\cos ax$",        "cream", a_clifford,  "chaos from two maps"),
    ("dejong",    "The De Jong Attractor", r"$x' = \sin ay - \cos bx$",         "dark",  a_dejong,    "woven trajectories"),
    ("rossler",   "The Rössler Attractor", r"$\dot{x} = -y - z$",               "cream", a_rossler,   "a single folding spiral"),
    ("thomas",    "Thomas' Attractor",     r"$\dot{x} = \sin y - bx$",          "dark",  a_thomas,    "cyclically symmetric"),
    ("aizawa",    "The Aizawa Attractor",  r"$\dot{x} = (z-b)x - dy$",          "cream", a_aizawa,    "a torus of chaos"),
    ("halvorsen", "The Halvorsen Attractor",r"$\dot{x} = -ax - 4y - 4z - y^2$", "dark",  a_halvorsen, "a symmetric swirl"),
    ("hopalong",  "The Hopalong Attractor",r"$x' = y - \mathrm{sgn}(x)\sqrt{|bx-c|}$", "cream", a_hopalong, "Barry Martin's orbit"),
    ("svensson",  "The Svensson Attractor",r"$x' = d\sin ax - \sin by$",        "dark",  a_svensson,  "fractal filaments"),
    ("chen",      "The Chen Attractor",    r"$\dot{x} = a(y - x)$",             "cream", a_chen,      "a double-scroll"),
]


if __name__ == "__main__":
    paths = []
    for d in DESIGNS:
        p = GB.build_one(*d)
        print("  ", os.path.basename(p))
        paths.append(p)
    print(GB.contact(paths))
