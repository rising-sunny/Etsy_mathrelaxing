"""
generate_number_theory_poster.py — "History of Number Theory" timeline poster
==============================================================================
Second entry in the "History of X" pilot series (after History of Calculus):
same dark/gold house style -- gradient linework with a PIL bloom pass,
Cinzel/Raleway type, per-milestone accent palettes -- but its own nine
milestones and bespoke diagrams, spanning Euclid's proof of infinitely many
primes to Wiles' proof of Fermat's Last Theorem.

  python generate_number_theory_poster.py
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "history_of_number_theory")
os.makedirs(OUT, exist_ok=True)
AF = os.path.join(BASE, "lulu_books", "assets", "fonts")

DARK = "#0d0f12"
CREAM = "#f0ece0"
SUB = "#8f8a78"
GOLD = "#c9a24b"
GOLD_HI = "#f3dfa0"
BRONZE = "#7a5a2a"
LINE = "#2c2a24"

CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RALEWAY = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RALEWAY_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")

plt.rcParams.update({"mathtext.fontset": "stix", "axes.unicode_minus": False})

GOLD_CMAP = LinearSegmentedColormap.from_list("gold", [BRONZE, GOLD, GOLD_HI])
PALETTES = {
    "gold": dict(cmap=GOLD_CMAP, mid=GOLD, hi=GOLD_HI, deep=BRONZE),
    "rose": dict(cmap=LinearSegmentedColormap.from_list("rose", ["#4a1f30", "#b8547a", "#f0c4d8"]),
                 mid="#b8547a", hi="#f0c4d8", deep="#4a1f30"),
    "teal": dict(cmap=LinearSegmentedColormap.from_list("teal", ["#173f3a", "#4f9e8f", "#c3ede2"]),
                 mid="#4f9e8f", hi="#c3ede2", deep="#173f3a"),
    "blue": dict(cmap=LinearSegmentedColormap.from_list("blue", ["#1c2c47", "#5a7fae", "#c8ddf5"]),
                 mid="#5a7fae", hi="#c8ddf5", deep="#1c2c47"),
}

W, H = 12.0, 17.0
DPI = 300

GLOW = lambda lw=1.8, c=GOLD, a=0.30, extra=2.4: [
    pe.Stroke(linewidth=lw + extra, foreground=c, alpha=a), pe.Normal()]


def tracked(s, thin=1):
    """Insert thin-space letter tracking for a more elegant, poster-style caps line."""
    return (" " * thin).join(s)


def grad_line(ax, x, y, cmap=GOLD_CMAP, lw=1.9, alpha=1.0, zorder=4, glow=True, glow_color=None):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, alpha=alpha, linewidths=lw, zorder=zorder,
                         capstyle="round")
    lc.set_array(np.linspace(0, 1, len(x)))
    if glow:
        lc.set_path_effects(GLOW(lw=lw, c=glow_color or GOLD, a=0.25))
    ax.add_collection(lc)


def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:
            return False
    return True


# ---------------------------------------------------------------- diagrams
def draw_euclid(ax, pal=PALETTES["gold"]):
    primes = [n for n in range(2, 48) if is_prime(n)]
    ax.axhline(0, color=SUB, lw=1.0)
    for p in primes:
        ax.plot([p], [0], "o", color=pal["hi"], ms=5, zorder=5, mec=DARK, mew=0.6)
    ax.plot([primes[-1] + 2, primes[-1] + 7], [0, 0], color=SUB, lw=1.0, ls=(0, (1, 1.6)))
    ax.annotate("", xy=(primes[-1] + 8, 0), xytext=(primes[-1] + 3, 0.9),
                arrowprops=dict(arrowstyle="->", color=CREAM, lw=1.0,
                                connectionstyle="arc3,rad=-0.3"))
    ax.text(primes[-1] + 3, 1.05, "always one more", fontsize=10.5, color=CREAM,
            ha="center", fontproperties=RALEWAY_I)
    ax.set_xlim(-2, 58); ax.set_ylim(-1.3, 1.4); ax.axis("off")


def draw_diophantus(ax, pal=PALETTES["gold"]):
    r = 5
    th = np.linspace(0, 2 * np.pi, 300)
    grad_line(ax, r * np.cos(th), r * np.sin(th), cmap=pal["cmap"], lw=1.5, glow_color=pal["mid"])
    lattice = [(gx, gy) for gx in range(-6, 7) for gy in range(-6, 7) if gx * gx + gy * gy <= 32]
    lx, ly = zip(*lattice)
    ax.plot(lx, ly, ".", color=SUB, ms=2.2, alpha=0.35, zorder=1)
    sols = [(x, y) for x in range(-6, 7) for y in range(-6, 7) if x * x + y * y == 25]
    for x, y in sols:
        ax.plot([x], [y], "o", color=pal["hi"], ms=7, zorder=5, mec=DARK, mew=0.7)
    ax.text(3.2, 4.5, "(3, 4)", fontsize=10, color=CREAM, fontproperties=RALEWAY)
    ax.set_xlim(-6.6, 6.6); ax.set_ylim(-6.6, 6.6); ax.set_aspect("equal"); ax.axis("off")


def draw_fermat(ax, pal=PALETTES["gold"]):
    p = 7
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(1.0 * np.cos(th), 1.0 * np.sin(th), color=SUB, lw=1.0, alpha=0.6)
    for k in range(p):
        a = 2 * np.pi * k / p
        ax.plot([np.cos(a)], [np.sin(a)], "o", color=pal["deep"], ms=8, mec=DARK, mew=0.6, zorder=4)
        ax.text(1.22 * np.cos(a), 1.22 * np.sin(a), str(k), fontsize=9.5, color=SUB,
                ha="center", va="center")
    a0 = 2 * np.pi * 3 / p
    ax.plot([np.cos(a0)], [np.sin(a0)], "o", color=pal["hi"], ms=10, mec=DARK, mew=0.9, zorder=6)
    loops = np.linspace(a0, a0 + 2 * np.pi * (p - 1), 300)
    rr = np.linspace(1.0, 0.05, 300)
    grad_line(ax, rr * np.cos(loops), rr * np.sin(loops), cmap=pal["cmap"], lw=1.3,
              glow_color=pal["mid"], zorder=3)
    ax.text(0, 0, r"$a^p\!\equiv\!a$", fontsize=13, color=CREAM, ha="center", va="center")
    ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal"); ax.axis("off")


def draw_goldbach(ax, pal=PALETTES["gold"]):
    evens = [10, 16, 22, 28, 34]
    primes = [n for n in range(2, 40) if is_prime(n)]
    ax.axhline(0, color=SUB, lw=1.0)
    for n in evens:
        ax.plot([n], [0], "o", color=CREAM, ms=5, zorder=5)
        ax.text(n, -0.32, str(n), fontsize=9, color=SUB, ha="center")
    pairs = []
    for n in evens:
        for p in primes:
            q = n - p
            if q in primes and p <= q:
                pairs.append((n, p, q))
                break
    for i, (n, p, q) in enumerate(pairs):
        h = 0.55 + 0.18 * (i % 3)
        t = np.linspace(0, 1, 60)
        arc_x = p + (q - p) * t
        arc_y = h * np.sin(np.pi * t)
        grad_line(ax, arc_x, arc_y, cmap=pal["cmap"], lw=1.4, glow_color=pal["mid"], zorder=3)
        ax.plot([p, q], [0, 0], "o", color=pal["hi"], ms=4, zorder=5, mec=DARK, mew=0.4)
    ax.set_xlim(0, 38); ax.set_ylim(-0.55, 1.5); ax.axis("off")


def draw_gauss(ax, pal=PALETTES["gold"]):
    n_mod = 5
    xs = np.arange(0, 21)
    colors = [pal["cmap"](0.15 + 0.7 * (x % n_mod) / (n_mod - 1)) for x in xs]
    ax.axhline(0, color=SUB, lw=1.0, zorder=1)
    for x, c in zip(xs, colors):
        ax.plot([x], [0], "o", color=c, ms=11, mec=DARK, mew=0.8, zorder=4)
        ax.text(x, -0.34, str(x % n_mod), fontsize=8, color=DARK, ha="center", va="center",
                zorder=5)
    for r in range(n_mod):
        members = [x for x in xs if x % n_mod == r]
        y0 = 0.55 + 0.16 * r
        ax.plot([members[0], members[-1]], [y0, y0], color=pal["deep"], lw=0.8, alpha=0.7)
    ax.set_xlim(-1.5, 21.5); ax.set_ylim(-0.9, 1.4); ax.axis("off")


def draw_riemann(ax, pal=PALETTES["gold"]):
    ax.axvspan(0, 1, color=SUB, alpha=0.08)
    ax.axvline(0.5, color=pal["mid"], lw=1.3, ls=(0, (4, 3)), path_effects=GLOW(lw=1.3, c=pal["mid"]))
    ax.axvline(0, color=SUB, lw=0.8); ax.axvline(1, color=SUB, lw=0.8)
    zeros = [14.13, 21.02, 25.01, 30.42, 32.94, 37.59]
    for t in zeros:
        ax.plot([0.5], [t], "o", color=pal["hi"], ms=6, zorder=5, mec=DARK, mew=0.6)
    ax.text(0.02, -3, "0", fontsize=10, color=SUB); ax.text(0.98, -3, "1", fontsize=10, color=SUB, ha="right")
    ax.set_xlim(-0.15, 1.15); ax.set_ylim(-6, max(zeros) + 5); ax.axis("off")


def draw_pnt(ax, pal=PALETTES["gold"]):
    xs = np.arange(2, 200)
    pi_x = np.cumsum([is_prime(n) for n in xs])
    ax.plot(xs, pi_x, color=SUB, lw=1.3, drawstyle="steps-post", alpha=0.85)
    approx = xs / np.log(xs)
    grad_line(ax, xs.astype(float), approx, cmap=pal["cmap"], lw=1.8, glow_color=pal["mid"])
    ax.text(6, max(pi_x) - 4, r"$\pi(x)$", fontsize=12, color=SUB, fontproperties=RALEWAY_I)
    ax.set_xlim(0, 200); ax.set_ylim(0, max(pi_x) + 8); ax.axis("off")


def draw_ramanujan(ax, pal=PALETTES["gold"]):
    partitions = [
        [5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1],
    ]
    x0 = 0.0
    for row in partitions:
        y0 = 0.0
        for part in row:
            for i in range(part):
                sq = plt.Rectangle((x0 + i * 0.55, y0), 0.5, 0.5, facecolor="none",
                                    edgecolor=pal["mid"], lw=1.1)
                ax.add_patch(sq)
            y0 -= 0.62
        x0 += 3.6
    ax.text(0, 0.55, "p(5) = 7", fontsize=12, color=CREAM, fontproperties=CINZEL_R)
    ax.set_xlim(-0.5, 25); ax.set_ylim(-4.6, 1.1); ax.axis("off")


def draw_wiles(ax, pal=PALETTES["gold"]):
    # classic three-real-root curve (discriminant > 0): an oval + an unbounded branch
    x_oval = np.linspace(-1, 0, 200)
    y_oval = np.sqrt(np.clip(x_oval**3 - x_oval, 0, None))
    grad_line(ax, x_oval, y_oval, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    grad_line(ax, x_oval, -y_oval, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    x_branch = np.linspace(1, 2.2, 200)
    y_branch = np.sqrt(np.clip(x_branch**3 - x_branch, 0, None))
    grad_line(ax, x_branch, y_branch, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    grad_line(ax, x_branch, -y_branch, cmap=pal["cmap"], lw=1.7, glow_color=pal["mid"])
    for rx in (-1, 0, 1):
        ax.plot([rx], [0], "o", color=pal["hi"], ms=5, mec=DARK, mew=0.6, zorder=5)
    ax.text(-1.85, 2.0, r"$y^2=x^3-x$", fontsize=12, color=CREAM, ha="left")
    ax.set_xlim(-2.0, 2.5); ax.set_ylim(-2.4, 2.4); ax.axis("off")


MILESTONES = [
    ("c. 300 BCE", "EUCLID", "INFINITUDE OF THE PRIMES",
     r"$N=p_1p_2\cdots p_n+1$", "gold", draw_euclid),
    ("c. 250 CE", "DIOPHANTUS", "DIOPHANTINE EQUATIONS",
     r"$x^2+y^2=z^2$", "teal", draw_diophantus),
    ("1640", "PIERRE DE FERMAT", "FERMAT'S LITTLE THEOREM",
     r"$a^p\equiv a\ (\mathrm{mod}\ p)$", "rose", draw_fermat),
    ("1742", "CHRISTIAN GOLDBACH", "THE GOLDBACH CONJECTURE",
     r"$2n=p+q$", "blue", draw_goldbach),
    ("1801", "CARL FRIEDRICH GAUSS", "MODULAR ARITHMETIC",
     r"$a\equiv b\ (\mathrm{mod}\ n)$", "teal", draw_gauss),
    ("1859", "BERNHARD RIEMANN", "THE RIEMANN HYPOTHESIS",
     r"$\zeta(s)=0\Rightarrow\mathrm{Re}(s)=\frac{1}{2}$", "gold", draw_riemann),
    ("1896", "HADAMARD & DE LA VALLÉE POUSSIN", "THE PRIME NUMBER THEOREM",
     r"$\pi(x)\sim\frac{x}{\ln x}$", "blue", draw_pnt),
    ("1913", "SRINIVASA RAMANUJAN", "PARTITIONS & MODULAR FORMS",
     r"$p(n)\sim\frac{1}{4n\sqrt{3}}e^{\pi\sqrt{2n/3}}$", "rose", draw_ramanujan),
    ("1994", "ANDREW WILES", "FERMAT'S LAST THEOREM, PROVED",
     r"$x^n+y^n\neq z^n\ (n>2)$", "gold", draw_wiles),
]


def build():
    n = len(MILESTONES)
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_facecolor(DARK)
    gs = fig.add_gridspec(
        nrows=n + 2, ncols=3,
        height_ratios=[1.65] + [1.0] * n + [0.7],
        width_ratios=[0.30, 0.44, 0.26],
        left=0.09, right=0.95, top=0.965, bottom=0.03,
        hspace=0.28, wspace=0.02,
    )

    ax_title = fig.add_subplot(gs[0, :]); ax_title.axis("off"); ax_title.set_facecolor(DARK)
    ax_title.text(0.5, 0.80, tracked("HISTORY OF", 1), fontsize=23, color=CREAM, ha="center",
                  va="center", fontproperties=CINZEL_R)
    ax_title.text(0.5, 0.555, tracked("NUMBER THEORY", 1), fontsize=40, color=GOLD, ha="center",
                  va="center", fontproperties=CINZEL, path_effects=GLOW(lw=0.5, a=0.35, extra=3.5))
    ax_title.plot([0.40, 0.60], [0.335, 0.335], color=GOLD, lw=1.0, alpha=0.85)
    ax_title.text(0.5, 0.18, tracked("FROM EUCLID TO THE MODULARITY THEOREM", 1), fontsize=11.5,
                  color=SUB, ha="center", va="center", fontproperties=RALEWAY_I)
    ax_title.plot([0.09, 0.91], [0.02, 0.02], color=LINE, lw=1.0)
    ax_title.set_xlim(0, 1); ax_title.set_ylim(0, 1)

    for i, (year, name, label, eq, palkey, drawfn) in enumerate(MILESTONES):
        r = i + 1
        ax_txt = fig.add_subplot(gs[r, 0]); ax_txt.axis("off"); ax_txt.set_facecolor(DARK)
        ax_txt.set_xlim(0, 1); ax_txt.set_ylim(0, 1)
        ax_txt.text(0.18, 0.66, year, fontsize=14, color=CREAM, ha="left", va="center",
                    fontproperties=CINZEL_R)
        ns = 10.5 * min(1.0, 21 / max(len(name), 1))
        ax_txt.text(0.18, 0.46, name, fontsize=ns, color=GOLD, ha="left", va="center",
                    fontproperties=CINZEL_R)
        ax_txt.text(0.18, 0.30, label, fontsize=7.4, color=SUB, ha="left", va="center",
                    fontproperties=RALEWAY)

        ax_d = fig.add_subplot(gs[r, 1]); ax_d.set_facecolor(DARK)
        drawfn(ax_d, PALETTES[palkey])

        ax_eq = fig.add_subplot(gs[r, 2]); ax_eq.axis("off"); ax_eq.set_facecolor(DARK)
        ax_eq.set_xlim(0, 1); ax_eq.set_ylim(0, 1)
        ax_eq.text(0.06, 0.5, eq, fontsize=12.5, color=CREAM, ha="left", va="center")

    ax_foot = fig.add_subplot(gs[-1, :]); ax_foot.axis("off"); ax_foot.set_facecolor(DARK)
    ax_foot.set_xlim(0, 1); ax_foot.set_ylim(0, 1)
    ax_foot.plot([0.09, 0.91], [0.85, 0.85], color=LINE, lw=1.0)
    ax_foot.text(0.5, 0.35, "Twenty-three centuries of primes, congruences, and one very stubborn theorem.",
                 fontsize=11, color=SUB, ha="center", fontproperties=RALEWAY_I)
    ax_foot.text(0.5, 0.05, "MathRelaxing", fontsize=11, color=GOLD, ha="center",
                 fontproperties=CINZEL_R)

    positions = gs.get_grid_positions(fig)
    bottoms, tops, lefts, rights = positions
    x_dot = lefts[0] + 0.028
    y_top = tops[1]
    y_bot = bottoms[-2]
    overlay = fig.add_axes([0, 0, 1, 1]); overlay.axis("off"); overlay.set_zorder(10)
    overlay.set_xlim(0, 1); overlay.set_ylim(0, 1)
    overlay.plot([x_dot, x_dot], [y_bot, y_top], color=LINE, lw=1.6, solid_capstyle="round")
    for i in range(n):
        yc = (bottoms[i + 1] + tops[i + 1]) / 2
        overlay.plot([x_dot], [yc], "o", color=GOLD, ms=7.5, mec=DARK, mew=1.4, zorder=11,
                     path_effects=GLOW(lw=0, a=0.4, extra=6))

    raw_png = os.path.join(OUT, "_history_of_number_theory_raw.png")
    fig.savefig(raw_png, facecolor=DARK)
    plt.close(fig)

    img = Image.open(raw_png).convert("RGB")
    bloomed = add_bloom(img, blur_radius=round(10 * DPI / 200))
    out_png = os.path.join(OUT, "history_of_number_theory_preview.png")
    bloomed.save(out_png)
    print("wrote", out_png)


def add_bloom(img: Image.Image, threshold=150, blur_radius=10, intensity=0.55) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    lum = arr.mean(axis=2)
    mask = np.clip((lum - threshold) / max(1, 255 - threshold), 0, 1)
    bright = (arr * mask[..., None]).astype(np.uint8)
    blurred = Image.fromarray(bright).filter(ImageFilter.GaussianBlur(blur_radius))
    out = arr + np.asarray(blurred).astype(np.float32) * intensity
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    build()
