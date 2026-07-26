"""
mini_book.py — production test: a 10-plate square art book interior PDF
(8.5x8.5 + 0.125" bleed, 300 DPI) + a front cover, ready for Lulu.
"""
import io, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import odeint
from PIL import Image, ImageOps
import img2pdf

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(SCR, "..", "..", ".."))
OUT = os.path.join(SCR, "book"); os.makedirs(OUT, exist_ok=True)
PAGES = os.path.join(OUT, "pages"); os.makedirs(PAGES, exist_ok=True)
GEO = os.path.join(REPO, "wallart_set", "out", "geo", "mono", "prints")
AF = os.path.join(REPO, "lulu_books", "assets", "fonts")
CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RALEWAY = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RALEWAY_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")
plt.rcParams["mathtext.fontset"] = "cm"

DPI = 300; TRIM = 8.5; BLEED = 0.125
TRIM_PX = int(TRIM * DPI)              # 2550
BLEED_PX = int(BLEED * DPI)            # 37
PAGE_PX = TRIM_PX + 2 * BLEED_PX
PAPER = "#f4efe3"; INK = "#20201e"; SUB = "#6f6a5e"; ACC = "#9c6b3f"; DARK = "#0e1013"
GOLD = "#c9a24b"
CMAP = LinearSegmentedColormap.from_list("mr", ["#2a9d8f", "#8ecae6", "#e9c46a", "#e76f51"])
FRACT = LinearSegmentedColormap.from_list("mrf", ["#0e1013", "#12303a", "#2a9d8f",
                                                  "#8ecae6", "#e9c46a", "#e76f51"])


def fig_trim(face):
    fig = plt.figure(figsize=(TRIM, TRIM), dpi=DPI); fig.patch.set_facecolor(face)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(face); ax.axis("off")
    return fig, ax


def to_pil(fig, face):
    buf = io.BytesIO(); fig.savefig(buf, dpi=DPI, facecolor=face, format="png")
    plt.close(fig); buf.seek(0)
    return Image.open(buf).convert("RGB")


def pad_bleed(img, hexbg):
    rgb = tuple(int(hexbg[i:i + 2], 16) for i in (1, 3, 5))
    if img.size != (TRIM_PX, TRIM_PX):
        img = img.resize((TRIM_PX, TRIM_PX), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (PAGE_PX, PAGE_PX), rgb)
    canvas.paste(img, (BLEED_PX, BLEED_PX))
    return canvas


# ---------- graphics ----------
def g_lorenz():
    def f(s, t): x, y, z = s; return [10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z]
    t = np.linspace(0, 60, 24000); s = odeint(f, [1, 1, 1], t); x, z = s[:, 0], s[:, 2]
    fig, ax = fig_trim(DARK)
    _grad_line(ax, x, z, CMAP, 0.5); ax.set_xlim(x.min() - 2, x.max() + 2); ax.set_ylim(z.min() - 2, z.max() + 2)
    return to_pil(fig, DARK)


def g_rossler():
    def f(s, t): x, y, z = s; return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]
    t = np.linspace(0, 320, 40000); s = odeint(f, [0, 1, 0], t); x, y = s[:, 0], s[:, 1]
    fig, ax = fig_trim(DARK)
    _grad_line(ax, x, y, CMAP, 0.5); ax.set_xlim(x.min() - 1.5, x.max() + 1.5); ax.set_ylim(y.min() - 1.5, y.max() + 1.5)
    return to_pil(fig, DARK)


def g_thomas():
    b = 0.208
    def f(s, t): x, y, z = s; return [np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z]
    t = np.linspace(0, 340, 44000); s = odeint(f, [1.1, 1.1, -1.0], t); x, y = s[:, 0], s[:, 1]
    fig, ax = fig_trim(DARK)
    _grad_line(ax, x, y, CMAP, 0.5); ax.set_xlim(-5.5, 5.5); ax.set_ylim(-5.5, 5.5); ax.set_aspect("equal")
    return to_pil(fig, DARK)


def _grad_line(ax, x, y, cmap, lw):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, linewidth=lw, alpha=0.9)
    lc.set_array(np.linspace(0, 1, len(segs))); ax.add_collection(lc)


def _escape(c_grid, z0=None, it=220):
    Z = np.zeros_like(c_grid) if z0 is None else np.full(c_grid.shape, z0, complex)
    C = c_grid; out = np.zeros(c_grid.shape); m = np.ones(c_grid.shape, bool)
    for k in range(it):
        Z[m] = Z[m] * Z[m] + (C[m] if z0 is None else C)
        esc = np.abs(Z) > 2; out[esc & m] = k; m &= ~esc
    out[m] = it; return (out / it) ** 0.55


def g_julia():
    S = 2200; c = complex(-0.8, 0.156)
    x = np.linspace(-1.6, 1.6, S); X, Y = np.meshgrid(x, x); Z = X + 1j * Y
    out = np.zeros(Z.shape); m = np.ones(Z.shape, bool)
    for k in range(220):
        Z[m] = Z[m] ** 2 + c; esc = np.abs(Z) > 2; out[esc & m] = k; m &= ~esc
    out[m] = 220; v = (out / 220) ** 0.55
    fig, ax = fig_trim(DARK); ax.imshow(v, cmap=FRACT, origin="lower", vmin=0, vmax=1)
    return to_pil(fig, DARK)


def g_mandel():
    S = 2200
    x = np.linspace(-2.2, 0.9, S); y = np.linspace(-1.35, 1.35, S)
    X, Y = np.meshgrid(x, y); C = X + 1j * Y
    Z = np.zeros(C.shape, complex); out = np.zeros(C.shape); m = np.ones(C.shape, bool)
    for k in range(240):
        Z[m] = Z[m] ** 2 + C[m]; esc = np.abs(Z) > 2; out[esc & m] = k; m &= ~esc
    out[m] = 240; v = (out / 240) ** 0.5
    fig, ax = fig_trim(DARK); ax.imshow(v, cmap=FRACT, origin="lower", vmin=0, vmax=1)
    return to_pil(fig, DARK)


def g_rose():
    th = np.linspace(0, 2 * np.pi, 6000); r = np.cos(7 * th)
    x, y = r * np.cos(th), r * np.sin(th)
    fig, ax = fig_trim(PAPER); _grad_line(ax, x, y, CMAP, 2.4)
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect("equal")
    return to_pil(fig, PAPER)


def g_lissajous():
    t = np.linspace(0, 2 * np.pi, 5000)
    x, y = np.sin(5 * t + np.pi / 2), np.sin(4 * t)
    fig, ax = fig_trim(PAPER); _grad_line(ax, x, y, CMAP, 2.4)
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect("equal")
    return to_pil(fig, PAPER)


def g_harmono():
    t = np.linspace(0, 60, 40000)
    x = np.exp(-0.006 * t) * (np.sin(2.01 * t) + np.sin(3.0 * t + 1.3))
    y = np.exp(-0.006 * t) * (np.sin(3.0 * t) + np.sin(2.0 * t + 0.5))
    fig, ax = fig_trim(PAPER); _grad_line(ax, x, y, CMAP, 1.4)
    ax.set_xlim(x.min() * 1.1, x.max() * 1.1); ax.set_ylim(y.min() * 1.1, y.max() * 1.1); ax.set_aspect("equal")
    return to_pil(fig, PAPER)


def g_print(name):
    im = Image.open(f"{GEO}/{name}_4x5.jpg").convert("RGB")
    return ImageOps.fit(im, (TRIM_PX, TRIM_PX), Image.Resampling.LANCZOS)


# ---------- text pages ----------
def text_page(section, title, eqs, params, desc, plate):
    fig, ax = fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.17, 0.82, section, fontproperties=CINZEL_R, fontsize=15, color=ACC)
    ax.plot([0.17, 0.17 + 0.011 * len(section)], [0.797, 0.797], color=ACC, lw=1.3)
    ax.text(0.17, 0.715, title, fontproperties=CINZEL, fontsize=34, color=INK)
    n = len(eqs); y0 = 0.55 + (n - 1) * 0.038
    for i, e in enumerate(eqs):
        ax.text(0.19, y0 - i * 0.076, e, fontsize=27, color=INK, va="center")
    if params:
        ax.text(0.17, 0.335, params, fontsize=16, color=SUB)
    ax.text(0.17, 0.27, desc, fontproperties=RALEWAY, fontsize=14, color="#403c34", va="top", linespacing=1.6)
    ax.plot([0.17, 0.83], [0.085, 0.085], color="#d8d0be", lw=1.1)
    ax.text(0.17, 0.055, plate, fontproperties=CINZEL_R, fontsize=12.5, color=SUB, va="center")
    ax.text(0.83, 0.055, "MathRelaxing", fontproperties=RALEWAY_I, fontsize=12.5, color=SUB, ha="right", va="center")
    return to_pil(fig, PAPER)


def title_page():
    fig, ax = fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.plot([0.30, 0.70], [0.70, 0.70], color=ACC, lw=1.4)
    ax.text(0.5, 0.63, "THE MATHEMATICS", fontproperties=CINZEL, fontsize=40, color=INK, ha="center")
    ax.text(0.5, 0.555, "OF BEAUTY", fontproperties=CINZEL, fontsize=40, color=INK, ha="center")
    ax.text(0.5, 0.47, "A Visual Gallery of Equations, Curves and Chaos",
            fontproperties=RALEWAY_I, fontsize=17, color=SUB, ha="center")
    ax.plot([0.30, 0.70], [0.41, 0.41], color=ACC, lw=1.4)
    ax.text(0.5, 0.12, "MathRelaxing", fontproperties=CINZEL_R, fontsize=16, color=INK, ha="center")
    return to_pil(fig, PAPER)


def simple_text_page(lines, center=True):
    fig, ax = fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    y = 0.62
    for txt, fp, sz, col in lines:
        ax.text(0.5 if center else 0.17, y, txt, fontproperties=fp, fontsize=sz, color=col,
                ha="center" if center else "left", va="top",
                linespacing=1.7, wrap=True)
        y -= 0.09 + 0.006 * sz
    return to_pil(fig, PAPER)


def divider_page(label):
    fig, ax = fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.5, label, fontproperties=CINZEL, fontsize=30, color=INK, ha="center", va="center")
    ax.plot([0.42, 0.58], [0.44, 0.44], color=ACC, lw=1.3)
    return to_pil(fig, PAPER)


# ---------- plates ----------
PLATES = [
    ("Attractors", "The Lorenz System", [r"$\dot{x} = \sigma(y-x)$", r"$\dot{y} = x(\rho-z)-y$", r"$\dot{z} = xy-\beta z$"],
     r"$\sigma=10 \quad \rho=28 \quad \beta=8/3$",
     "A deterministic system whose paths never repeat and never cross — the first\nstrange attractor, and the birthplace of chaos theory. Two trajectories a hair\napart diverge without bound: the butterfly effect, drawn as a butterfly.", g_lorenz, DARK),
    ("Attractors", "The Rössler Attractor", [r"$\dot{x} = -y-z$", r"$\dot{y} = x+a\,y$", r"$\dot{z} = b+z(x-c)$"],
     r"$a=0.2 \quad b=0.2 \quad c=5.7$",
     "A single spiral that stretches, folds, and reinjects itself — about the simplest\nflow that can still wander forever on a thin fractal sheet.", g_rossler, DARK),
    ("Attractors", "The Thomas Attractor", [r"$\dot{x} = \sin y - b\,x$", r"$\dot{y} = \sin z - b\,y$", r"$\dot{z} = \sin x - b\,z$"],
     r"$b=0.208$",
     "A cyclically symmetric flow. As the damping b is lowered, a calm orbit softens\nand dissolves into gentle, aimless chaos.", g_thomas, DARK),
    ("Fractals", "The Julia Set", [r"$z_{n+1} = z_n^{2} + c$"], r"$c=-0.8+0.156\,i$",
     "For each starting point, iterate and ask: does it fly to infinity, or stay bounded\nforever? The boundary between the two is infinitely intricate — self-similar at\nevery scale, yet never quite repeating.", g_julia, DARK),
    ("Fractals", "The Mandelbrot Set", [r"$z_{n+1} = z_n^{2} + c,\ \ z_0=0$"], r"$c \in \mathbb{C}$",
     "The atlas of every Julia set at once: colour each point c by how quickly the\norbit of zero escapes. Its border hides infinite depth, the same shapes\nreturning smaller, forever.", g_mandel, DARK),
    ("Curves", "The Rose", [r"$r = \cos(k\,\theta)$"], r"$k=7$",
     "A single polar equation traces a flower. When k is odd the curve draws k\npetals; when even, 2k. A whole garden hides in one line of trigonometry.", g_rose, PAPER),
    ("Curves", "The Lissajous Figure", [r"$x=\sin(a\,t+\delta)$", r"$y=\sin(b\,t)$"], r"$a=5 \quad b=4 \quad \delta=\pi/2$",
     "Two perpendicular oscillations drawn against each other. Simple whole-number\nfrequency ratios weave closed, harmonic knots.", g_lissajous, PAPER),
    ("Curves", "The Harmonograph", [r"$x(t)=e^{-d t}\,[\sin f_1 t + \sin f_2 t]$"], r"$\mathrm{two\ coupled\ pendulums}$",
     "The trace of coupled, slowly-dying pendulums — the Victorian machine that\ndrew mathematics as it swung its way to rest.", g_harmono, PAPER),
    ("Symmetry & Tilings", "Penrose Tiling", [r"$\varphi = \dfrac{1+\sqrt{5}}{2}$"], r"$36^{\circ}\,/\,72^{\circ}\ \mathrm{rhombi}$",
     "Two rhombi, built on the golden ratio, tile the plane so that the pattern never\nexactly repeats — an aperiodic order once thought impossible.", lambda: g_print("penrose"), PAPER),
    ("Symmetry & Tilings", "The Flower of Life", [r"$(x-x_k)^2+(y-y_k)^2=r^2$"], r"$\mathrm{hexagonal\ lattice}$",
     "A lattice of overlapping circles, each radius equal to the spacing — the seed\npattern that has ornamented temples and manuscripts for millennia.", lambda: g_print("flower"), PAPER),
]

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def build():
    pages = []  # (pil_image, bg_hex)
    pages.append((title_page(), PAPER))
    pages.append((simple_text_page([
        ("Foreword", CINZEL, 22, INK),
        ("Some equations do more than compute — they draw. A rule as short as one\n"
         "line, repeated without mercy, can fold space into a butterfly, scatter light\n"
         "into a fractal coast, or tile a floor that never repeats.\n\n"
         "This little gallery pairs each form with the mathematics that makes it. On\n"
         "the left, the equation and a few words. On the right, the picture it draws.",
         RALEWAY, 15, "#403c34"),
    ]), PAPER))
    pages.append((divider_page("THE PLATES"), PAPER))
    for i, (sec, title, eqs, params, desc, gfn, bg) in enumerate(PLATES):
        print(f"  plate {ROMAN[i]}: {title}")
        pages.append((text_page(sec, title, eqs, params, desc, f"PLATE {ROMAN[i]}"), PAPER))
        pages.append((gfn(), bg))
    pages.append((simple_text_page([
        ("Colophon", CINZEL, 20, INK),
        ("Every plate was generated from its own mathematics — nothing traced,\n"
         "nothing drawn by hand. Typeset in Cinzel and Raleway; equations in\n"
         "Computer Modern.\n\nMade by MathRelaxing.", RALEWAY, 14, "#403c34"),
    ]), PAPER))

    # write page JPEGs at trim+bleed, assemble PDF
    paths = []
    for i, (img, bg) in enumerate(pages):
        p = os.path.join(PAGES, f"p{i:02d}.jpg")
        pad_bleed(img, bg).save(p, "JPEG", quality=92, dpi=(DPI, DPI))
        paths.append(p)
    pdf = os.path.join(OUT, "interior.pdf")
    layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=layout))
    print(f"\ninterior.pdf: {len(pages)} pages, {os.path.getsize(pdf)//1024//1024} MB")
    return pdf, pages


if __name__ == "__main__":
    build()
