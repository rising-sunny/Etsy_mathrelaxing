"""
fractal_atlas.py — "THE FRACTAL ATLAS", a 64-page premium 8.5x8.5 hardcover
coffee-table book: a vibrant, full-bleed gallery of fractals and strange
attractors, each generated directly from its mathematics.

Reuses mini_book.py's page toolkit (geometry, text pages, PDF assembly) but
renders its own high-colour full-bleed plates (smooth escape-time fractals +
glowing attractor line-art on black).

  python fractal_atlas.py           # -> atlas/interior.pdf  (+ atlas/cover_front.png)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import odeint
from PIL import Image
import img2pdf
import mini_book as MB

SCR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCR, "atlas"); os.makedirs(OUT, exist_ok=True)
PAGES = os.path.join(OUT, "pages"); os.makedirs(PAGES, exist_ok=True)

DPI = MB.DPI; TRIM_PX = MB.TRIM_PX
PAPER, INK, SUB, ACC, DARK = MB.PAPER, MB.INK, MB.SUB, MB.ACC, MB.DARK
CIN, CINR, RAL, RALI = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I

S = 2000          # fractal render resolution
IT = 260          # iterations

# ---------- vibrant fractal engine (smooth escape-time) ----------
def _grid(cx, cy, w):
    h = w
    x = np.linspace(cx - w / 2, cx + w / 2, S)
    y = np.linspace(cy - h / 2, cy + h / 2, S)
    X, Y = np.meshgrid(x, y)
    return X + 1j * Y


def _smooth(C, Z0, power=2, conj=False, absfold=False, it=IT, bail=1e4):
    Z = np.array(Z0, dtype=complex)
    if Z.shape != C.shape:
        Z = np.full(C.shape, Z0, dtype=complex)
    out = np.full(C.shape, np.nan)
    m = np.ones(C.shape, bool)
    for k in range(it):
        z = Z[m]
        if absfold:
            z = np.abs(z.real) + 1j * np.abs(z.imag)
        if conj:
            z = np.conj(z)
        z = z ** power + C[m]
        Z[m] = z
        a = np.abs(z)
        esc = a > bail
        newly = m.copy(); newly[m] = esc
        with np.errstate(all="ignore"):
            out[newly] = k + 1 - np.log(np.log(a[esc])) / np.log(power)
        m[m] = ~esc
    return out  # nan = interior (bounded)


def _color(out, cmap, cyc=0.028, phase=0.0, gamma=0.9):
    interior = np.isnan(out)
    v = np.nan_to_num(out, nan=0.0)
    vv = (np.power(np.clip(v, 0, None), gamma) * cyc + phase) % 1.0
    rgb = cmap(vv)[:, :, :3].copy()
    rgb[interior] = (0.02, 0.02, 0.03)
    return Image.fromarray((rgb * 255).astype("uint8"), "RGB")


def julia(c, cmap, w=3.0, phase=0.0, cyc=0.03):
    C = np.full((S, S), c, dtype=complex)
    x = np.linspace(-w / 2, w / 2, S)
    X, Y = np.meshgrid(x, x)
    return _color(_smooth(C, X + 1j * Y, cyc_bail := None or None) if False else _smooth(C, X + 1j * Y), cmap, cyc, phase)


def mandel(cx, cy, w, cmap, phase=0.0, cyc=0.03, power=2, conj=False, absfold=False):
    C = _grid(cx, cy, w)
    return _color(_smooth(C, 0.0 + 0j, power=power, conj=conj, absfold=absfold), cmap, cyc, phase)


def newton(n, cmap, w=3.2, it=40):
    x = np.linspace(-w / 2, w / 2, S)
    X, Y = np.meshgrid(x, x); Z = X + 1j * Y
    roots = np.exp(2j * np.pi * np.arange(n) / n)
    itc = np.full(Z.shape, float(it)); done = np.zeros(Z.shape, bool)
    for k in range(it):
        with np.errstate(all="ignore"):
            Z = Z - (Z ** n - 1) / (n * Z ** (n - 1) + 1e-12)
        # cheap convergence test: |z^n - 1| small  (no huge root broadcast)
        with np.errstate(all="ignore"):
            near = np.abs(Z ** n - 1)
        conv = (near < 1e-4) & (~done); itc[conv] = k; done |= conv
    # nearest root computed ONCE at the end
    idx = np.argmin(np.abs(Z[..., None] - roots), axis=-1)
    shade = 1 - itc / it
    base = cmap(idx / max(1, n - 1))[:, :, :3]
    rgb = base * (0.18 + 0.82 * shade[:, :, None])
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype("uint8"), "RGB")


# ---------- attractors (glowing line art on black) ----------
def _attractor(f, s0, tmax, n, proj, lw=0.45, cmap=MB.CMAP, lims=None):
    t = np.linspace(0, tmax, n)
    s = odeint(f, s0, t)
    a, b = s[:, proj[0]], s[:, proj[1]]
    fig, ax = MB.fig_trim(DARK)
    MB._grad_line(ax, a, b, cmap, lw)
    if lims:
        ax.set_xlim(lims[0]); ax.set_ylim(lims[1])
    else:
        ax.set_xlim(a.min() - abs(np.ptp(a)) * 0.04, a.max() + abs(np.ptp(a)) * 0.04)
        ax.set_ylim(b.min() - abs(np.ptp(b)) * 0.04, b.max() + abs(np.ptp(b)) * 0.04)
    ax.set_aspect("auto")
    return MB.to_pil(fig, DARK)


def a_lorenz():   return _attractor(lambda s, t: [10*(s[1]-s[0]), s[0]*(28-s[2])-s[1], s[0]*s[1]-8/3*s[2]], [1,1,1], 60, 24000, (0,2))
def a_rossler():  return _attractor(lambda s, t: [-s[1]-s[2], s[0]+0.2*s[1], 0.2+s[2]*(s[0]-5.7)], [0,1,0], 320, 40000, (0,1))
def a_thomas():   return _attractor(lambda s, t: [np.sin(s[1])-0.208*s[0], np.sin(s[2])-0.208*s[1], np.sin(s[0])-0.208*s[2]], [1.1,1.1,-1], 340, 44000, (0,1))
def a_halvorsen():
    a=1.89
    return _attractor(lambda s,t:[-a*s[0]-4*s[1]-4*s[2]-s[1]**2, -a*s[1]-4*s[2]-4*s[0]-s[2]**2, -a*s[2]-4*s[0]-4*s[1]-s[0]**2], [-5,0,0], 100, 50000, (0,1))
def a_chen():     return _attractor(lambda s,t:[35*(s[1]-s[0]), (28-35)*s[0]-s[0]*s[2]+28*s[1], s[0]*s[1]-3*s[2]], [-7,-4,35], 40, 40000, (0,1))
def a_aizawa():
    a,b,c,d,e,f=0.95,0.7,0.6,3.5,0.25,0.1
    def fn(s,t):
        x,y,z=s
        return [(z-b)*x-d*y, d*x+(z-b)*y, c+a*z-z**3/3-(x**2+y**2)*(1+e*z)+f*z*x**3]
    return _attractor(fn, [0.1,0,0], 200, 50000, (0,1))
def a_sprott():   return _attractor(lambda s,t:[s[1]+2.07*s[0]*s[1]+s[0]*s[2], 1-1.79*s[0]**2+s[1]*s[2], s[0]-s[0]**2-s[1]**2], [0.63,0.47,-0.54], 200, 50000, (0,1))
def a_fourwing(): return _attractor(lambda s,t:[0.2*s[0]+s[1]*s[2], -0.01*s[0]-0.4*s[1]-s[0]*s[2], -s[2]-s[0]*s[1]], [1,0,-1], 300, 50000, (0,1))


# palettes
TURBO = plt.get_cmap("turbo"); MAGMA = plt.get_cmap("magma"); TWI = plt.get_cmap("twilight_shifted")
INFERNO = plt.get_cmap("inferno"); PLASMA = plt.get_cmap("plasma"); VIRIDIS = plt.get_cmap("viridis")
CIVIDIS = plt.get_cmap("cividis"); OCEAN = LinearSegmentedColormap.from_list("oc", ["#03071e","#0353a4","#00b4d8","#90e0ef","#ffd166","#ef476f"])

# ---------- plate table: (section, title, eqs, params, desc, render_fn) ----------
PLATES = [
    # ---- Julia gallery ----
    ("Julia Sets", "Dendrite", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.8+0.156\,i$",
     "Iterate a point; ask whether it stays bounded forever. The frontier between\ncaptured and escaped is a fractal filament — self-similar at every zoom.",
     lambda: julia(complex(-0.8,0.156), TURBO, w=3.2)),
    ("Julia Sets", "Douady Rabbit", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.123+0.745\,i$",
     "A three-eared fractal whose lobes spiral into ever-smaller copies of the whole.",
     lambda: julia(complex(-0.123,0.745), MAGMA, w=3.0)),
    ("Julia Sets", "Spiral", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.702-0.384\,i$",
     "Near the boundary of the Mandelbrot set, Julia sets wind into tightening spirals.",
     lambda: julia(complex(-0.70176,-0.3842), OCEAN, w=3.0)),
    ("Julia Sets", "Siegel Disk", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.391-0.587\,i$",
     "A delicate lace where orbits rotate forever on nested invariant curves.",
     lambda: julia(complex(-0.391,-0.587), TWI, w=3.0)),
    ("Julia Sets", "San Marco", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.75+0\,i$",
     "Named for its reflection in the Venetian basilica's flooded piazza.",
     lambda: julia(complex(-0.75,0.0), INFERNO, w=3.2)),
    ("Julia Sets", "Dragon", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=0.285+0.01\,i$",
     "A near-connected coastline of interlocking hooks and bays.",
     lambda: julia(complex(0.285,0.01), PLASMA, w=3.0)),
    ("Julia Sets", "Airbrush", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.4+0.6\,i$",
     "Soft symmetric plumes — a fractal drawn as if with an airbrush.",
     lambda: julia(complex(-0.4,0.6), VIRIDIS, w=3.0)),
    ("Julia Sets", "Starfish", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=0.355+0.355\,i$",
     "Radial arms that split, and split again, without end.",
     lambda: julia(complex(0.355,0.355), TURBO, w=3.0, phase=0.4)),
    ("Julia Sets", "Frost", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.54+0.54\,i$",
     "Feathered dendrites like frost spreading across a cold pane.",
     lambda: julia(complex(-0.54,0.54), OCEAN, w=3.0, phase=0.5)),
    # ---- Mandelbrot & zooms ----
    ("The Mandelbrot Set", "The Whole Set", [r"$z_{n+1}=z_n^{2}+c,\ z_0=0$"], r"$c\in\mathbb{C}$",
     "Colour each point c by how fast the orbit of zero escapes. This one shape\ncontains a copy of every Julia set along its infinitely detailed border.",
     lambda: mandel(-0.7, 0.0, 3.1, TURBO, cyc=0.05)),
    ("The Mandelbrot Set", "Seahorse Valley", [r"$z_{n+1}=z_n^{2}+c$"], r"$c\approx -0.75+0.1\,i$",
     "The cleft between the head and body, filled with spiralling seahorse tails.",
     lambda: mandel(-0.745, 0.113, 0.05, MAGMA, cyc=0.09)),
    ("The Mandelbrot Set", "Elephant Valley", [r"$z_{n+1}=z_n^{2}+c$"], r"$c\approx 0.275+0.007\,i$",
     "A parade of self-similar 'elephants' marching trunk-to-tail around the bulb.",
     lambda: mandel(0.275, 0.0075, 0.05, INFERNO, cyc=0.09)),
    ("The Mandelbrot Set", "Triple Spiral", [r"$z_{n+1}=z_n^{2}+c$"], r"$c\approx -0.088+0.654\,i$",
     "Three arms winding into a single point of infinite regress.",
     lambda: mandel(-0.088, 0.654, 0.03, OCEAN, cyc=0.12)),
    ("The Mandelbrot Set", "The Mini-brot", [r"$z_{n+1}=z_n^{2}+c$"], r"$c\approx -1.749$",
     "Zoom deep along the spike and the whole set returns, smaller, again and again.",
     lambda: mandel(-1.7495, 0.0, 0.03, PLASMA, cyc=0.12)),
    ("The Mandelbrot Set", "The Burning Ship", [r"$z_{n+1}=(|\Re z|+i|\Im z|)^{2}+c$"], r"$c\in\mathbb{C}$",
     "Fold the plane onto its absolute value each step and the Mandelbrot set\ncatches fire — a fractal armada trailing smoke.",
     lambda: mandel(-0.5, -0.5, 3.2, INFERNO, cyc=0.06, absfold=True)),
    ("The Mandelbrot Set", "The Tricorn", [r"$z_{n+1}=\bar{z_n}^{2}+c$"], r"$\mathrm{Mandelbar}$",
     "Conjugate before squaring and the set grows three-cornered, its symmetry\nbroken into a fractal trefoil.",
     lambda: mandel(0.0, 0.0, 3.4, MAGMA, cyc=0.06, conj=True)),
    ("The Mandelbrot Set", "The Multibrot", [r"$z_{n+1}=z_n^{5}+c,\ z_0=0$"], r"$\mathrm{power}=5$",
     "Raise the power and the set sprouts more lobes — here a four-fold flower\nof escaping and captured points.",
     lambda: mandel(0.0, 0.0, 2.8, TURBO, cyc=0.06, power=5)),
    # ---- Newton ----
    ("Newton Fractals", "Cube Roots of Unity", [r"$z\mapsto z-\frac{z^{3}-1}{3z^{2}}$"], r"$z^{3}=1$",
     "Colour each start by which of the three roots Newton's method finds. The\nbasins meet along a fractal border where the method can't decide.",
     lambda: newton(3, TURBO)),
    ("Newton Fractals", "Fifth Roots", [r"$z\mapsto z-\frac{z^{5}-1}{5z^{4}}$"], r"$z^{5}=1$",
     "Five basins of attraction interlocking in five-fold fractal symmetry.",
     lambda: newton(5, PLASMA)),
    ("Newton Fractals", "Eighth Roots", [r"$z\mapsto z-\frac{z^{8}-1}{8z^{7}}$"], r"$z^{8}=1$",
     "Eight roots, eight basins, and a boundary of endlessly budding filigree.",
     lambda: newton(8, OCEAN)),
    # ---- Attractors ----
    ("Strange Attractors", "The Lorenz System", [r"$\dot x=\sigma(y-x)$", r"$\dot y=x(\rho-z)-y$", r"$\dot z=xy-\beta z$"],
     r"$\sigma=10\ \ \rho=28\ \ \beta=8/3$",
     "The first strange attractor. Paths never cross and never repeat; two started\na hair apart diverge without bound — the butterfly effect, drawn as a butterfly.",
     a_lorenz),
    ("Strange Attractors", "The Rössler Attractor", [r"$\dot x=-y-z$", r"$\dot y=x+ay$", r"$\dot z=b+z(x-c)$"],
     r"$a=b=0.2\ \ c=5.7$",
     "About the simplest flow that still wanders forever — one spiral that stretches,\nfolds, and reinjects itself onto a thin fractal band.", a_rossler),
    ("Strange Attractors", "The Thomas Attractor", [r"$\dot x=\sin y-bx$", r"$\dot y=\sin z-by$", r"$\dot z=\sin x-bz$"],
     r"$b=0.208$",
     "A cyclically symmetric flow that softens into gentle, aimless chaos as its\nfriction is lowered.", a_thomas),
    ("Strange Attractors", "The Halvorsen Attractor", [r"$\dot x=-ax-4y-4z-y^{2}$", r"$(\mathrm{cyclic\ in}\ x,y,z)$"],
     r"$a=1.89$",
     "Three cyclically-linked equations coil into a knotted, shell-like spiral.", a_halvorsen),
    ("Strange Attractors", "The Chen Attractor", [r"$\dot x=a(y-x)$", r"$\dot y=(c-a)x-xz+cy$", r"$\dot z=xy-bz$"],
     r"$a=35\ \ b=3\ \ c=28$",
     "A cousin of Lorenz with a doubled, denser weave of trajectories.", a_chen),
    ("Strange Attractors", "The Aizawa Attractor", [r"$\dot x=(z-b)x-dy$", r"$\dot y=dx+(z-b)y$", r"$\dot z=c+az-\frac{z^{3}}{3}-\ldots$"],
     r"$a=0.95\ \ b=0.7\ \ldots$",
     "A three-dimensional orbit that threads a sphere, drawing a wound ball of yarn.", a_aizawa),
    ("Strange Attractors", "The Sprott Attractor", [r"$\dot x=y+2.07xy+xz$", r"$\dot y=1-1.79x^{2}+yz$", r"$\dot z=x-x^{2}-y^{2}$"],
     r"$\mathrm{minimal\ quadratic}$",
     "One of Sprott's algebraically simplest chaotic flows — proof that complexity\nneeds almost nothing to begin.", a_sprott),
    ("Strange Attractors", "The Four-Wing Attractor", [r"$\dot x=ax+yz$", r"$\dot y=bx+cy-xz$", r"$\dot z=-z-xy$"],
     r"$\mathrm{four\ winged\ chaos}$",
     "Trajectories hop between four lobes, tracing the wings of an impossible moth.", a_fourwing),
]

ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX",
         "XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII","XXIX","XXX"]


def title_page():
    fig, ax = MB.fig_trim(DARK); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.plot([0.28,0.72],[0.70,0.70], color=MB.GOLD, lw=1.4)
    ax.text(0.5,0.63,"THE FRACTAL", fontproperties=CIN, fontsize=44, color="#f4efe3", ha="center")
    ax.text(0.5,0.55,"ATLAS", fontproperties=CIN, fontsize=44, color="#f4efe3", ha="center")
    ax.text(0.5,0.465,"A Vibrant Gallery of Fractals and Strange Attractors",
            fontproperties=RALI, fontsize=16, color="#c9c3b5", ha="center")
    ax.plot([0.28,0.72],[0.40,0.40], color=MB.GOLD, lw=1.4)
    ax.text(0.5,0.12,"MathRelaxing", fontproperties=CINR, fontsize=16, color="#f4efe3", ha="center")
    return MB.to_pil(fig, DARK)


def build():
    pages = []
    pages.append((title_page(), DARK))
    pages.append((MB.simple_text_page([
        ("The Fractal Atlas", CIN, 20, INK),
        ("A rule as short as z → z² + c, repeated without mercy, can fold the plane\n"
         "into coastlines, spirals and butterflies of infinite depth. Every plate in\n"
         "this atlas is computed directly from its equation — no clip-art, no AI —\n"
         "and printed full-bleed so the detail runs to the very edge of the page.", RAL, 14.5, "#403c34"),
    ]), PAPER))
    pages.append((MB.simple_text_page([
        ("How to read a fractal", CINR, 17, ACC),
        ("For the escape-time plates, each point is coloured by how quickly its orbit\n"
         "runs to infinity; the black heart is the set itself, where the orbit stays\n"
         "bounded forever. For the attractors, a single trajectory is drawn in one\n"
         "continuous, glowing line as it wanders its strange, unrepeating path.", RAL, 14, "#403c34"),
    ]), PAPER))
    cur = None
    pi = 0
    for (sec, title, eqs, params, desc, gfn) in PLATES:
        if sec != cur:
            pages.append((MB.divider_page(sec.upper()), PAPER)); cur = sec
        print(f"  plate {ROMAN[pi]}: {sec} / {title}")
        pages.append((MB.text_page(sec, title, eqs, params, desc, f"PLATE {ROMAN[pi]}"), PAPER))
        pages.append((gfn(), DARK))
        pi += 1
    pages.append((MB.simple_text_page([
        ("Colophon", CIN, 19, INK),
        ("Twenty-nine plates, each generated from its own mathematics by original\n"
         "code — nothing traced, nothing drawn by hand. Escape-time fields at 2400\n"
         "samples; attractors integrated over tens of thousands of steps. Typeset in\n"
         "Cinzel and Raleway. Made by MathRelaxing.", RAL, 13.5, "#403c34"),
    ]), PAPER))

    # pad to an even page count (Lulu requires even)
    if len(pages) % 2:
        pages.append((MB.simple_text_page([("", RAL, 10, PAPER)]), PAPER))

    paths = []
    for i, (img, bg) in enumerate(pages):
        p = os.path.join(PAGES, f"p{i:02d}.jpg")
        MB.pad_bleed(img, bg).save(p, "JPEG", quality=92, dpi=(DPI, DPI))
        paths.append(p)
    pdf = os.path.join(OUT, "interior.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    title_page().save(os.path.join(OUT, "cover_front.png"))
    print(f"\ninterior.pdf: {len(pages)} pages, {os.path.getsize(pdf)//1024//1024} MB")
    return pdf, len(pages)


if __name__ == "__main__":
    build()
