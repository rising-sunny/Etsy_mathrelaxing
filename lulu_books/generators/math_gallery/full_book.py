"""full_book.py — the complete 38-plate 'The Mathematics of Beauty' book:
interior PDF (8.5x8.5 + bleed, 300 DPI) + front cover with logo."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.collections import LineCollection
from PIL import Image
import img2pdf
import mini_book as MB
import plate_library as PL

OUT = os.path.join(MB.SCR, "fullbook"); os.makedirs(OUT, exist_ok=True)
PGS = os.path.join(OUT, "pages"); os.makedirs(PGS, exist_ok=True)
DPI, PAGE_PX, DARK, PAPER, GOLD, ACC, INK, SUB = MB.DPI, MB.PAGE_PX, MB.DARK, MB.PAPER, MB.GOLD, MB.ACC, MB.INK, MB.SUB
CINZEL, CINZEL_R, RALEWAY, RALEWAY_I = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")

# ---- plate metadata: (title, [eqs], params, desc, gfn) ----
SECTIONS = [
 ("Strange Attractors", [
  ("The Lorenz System", [r"$\dot{x}=\sigma(y-x)$", r"$\dot{y}=x(\rho-z)-y$", r"$\dot{z}=xy-\beta z$"], r"$\sigma=10 \quad \rho=28 \quad \beta=8/3$",
   "The first strange attractor and the birthplace of chaos theory. Two paths a\nhair apart diverge without bound — the butterfly effect, drawn as a butterfly.", PL.g_lorenz),
  ("The Rössler Attractor", [r"$\dot{x}=-y-z$", r"$\dot{y}=x+a y$", r"$\dot{z}=b+z(x-c)$"], r"$a=b=0.2 \quad c=5.7$",
   "A single spiral that stretches, folds and reinjects itself — about the simplest\nflow that can still wander forever on a thin fractal sheet.", PL.g_rossler),
  ("The Thomas Attractor", [r"$\dot{x}=\sin y-b x$", r"$\dot{y}=\sin z-b y$", r"$\dot{z}=\sin x-b z$"], r"$b=0.208$",
   "A cyclically symmetric flow. As the damping falls, a calm orbit softens and\ndissolves into gentle, aimless chaos.", PL.g_thomas),
  ("The Halvorsen Attractor", [r"$\dot{x}=-a x-4y-4z-y^{2}$", r"$(\mathrm{cyclic\ in}\ x,y,z)$"], r"$a=1.89$",
   "Perfectly symmetric in its three variables; one parameter tips a smooth swirl\ninto a tightly wound chaotic knot.", PL.g_halvorsen),
  ("The Chen Attractor", [r"$\dot{x}=a(y-x)$", r"$\dot{y}=(c-a)x-xz+cy$", r"$\dot{z}=xy-bz$"], r"$a=35 \quad b=3 \quad c=28$",
   "A close cousin of Lorenz found through control theory — related in spirit, yet\nnot the same shape at heart.", PL.g_chen),
  ("The Dadras Attractor", [r"$\dot{x}=y-ax+byz$", r"$\dot{y}=cy-xz+z$", r"$\dot{z}=dxy-ez$"], r"$a,b,c,d,e\ \mathrm{fixed}$",
   "A four-scroll flow that folds space into overlapping wings, each orbit weaving\nbetween them without ever settling.", PL.g_dadras),
  ("The Aizawa Attractor", [r"$\dot{x}=(z-b)x-d y$", r"$\dot{y}=d x+(z-b)y$", r"$\dot{z}=c+az-\frac{z^{3}}{3}-r^{2}(1{+}ez)+\dots$"], r"$r^{2}=x^{2}+y^{2}$",
   "A torus that never quite closes, wound around an axis it threads endlessly —\na sphere spun into thread.", PL.g_aizawa),
  ("The Sprott Attractor", [r"$\dot{x}=y+2.07xy+xz$", r"$\dot{y}=1-1.79x^{2}+yz$", r"$\dot{z}=x-x^{2}-y^{2}$"], None,
   "One of Sprott's minimal chaotic flows, found by searching for the simplest\nequations that could still refuse to repeat.", PL.g_sprott),
  ("The Four-Wing Attractor", [r"$\dot{x}=ax+yz$", r"$\dot{y}=bx+cy-xz$", r"$\dot{z}=-z-xy$"], None,
   "Four folded wings unfold from a compact quadratic flow — a butterfly given\ntwice the room to wander.", PL.g_fourwing),
 ]),
 ("Fractals", [
  ("The Julia Set", [r"$z_{n+1}=z_n^{2}+c$"], r"$c=-0.8+0.156\,i$",
   "Iterate each point and ask: does it fly to infinity or stay bounded forever? The\nborder between the two is infinitely intricate, self-similar at every scale.", PL.g_julia),
  ("The Mandelbrot Set", [r"$z_{n+1}=z_n^{2}+c,\ \ z_0=0$"], r"$c \in \mathbb{C}$",
   "The atlas of every Julia set at once: colour each point by how fast the orbit of\nzero escapes. Its border hides endless depth.", PL.g_mandel),
  ("The Burning Ship", [r"$z_{n+1}=(|\mathrm{Re}\,z_n|+i\,|\mathrm{Im}\,z_n|)^{2}+c$"], None,
   "Take the Mandelbrot rule and fold every step into the positive quadrant. From\nthe smooth cardioid, a fleet of ships appears.", PL.g_burning),
  ("The Tricorn", [r"$z_{n+1}=\bar{z}_n^{2}+c$"], None,
   "Conjugate at each step and the Mandelbrot's smooth edge sprouts cusps —\nthe multicorn, symmetric and sharp.", PL.g_tricorn),
  ("The Newton Fractal", [r"$z_{n+1}=z_n-\dfrac{z_n^{3}-1}{3z_n^{2}}$"], r"$f(z)=z^{3}-1$",
   "Newton's root-finder run on the whole plane. Which of three roots each point\nfalls to paints a frontier of infinite detail.", PL.g_newton),
  ("The Multibrot", [r"$z_{n+1}=z_n^{5}+c$"], None,
   "Raise the power and the Mandelbrot gains symmetry — here a five-fold bloom,\nthe same escape, a new flower.", PL.g_multibrot),
 ]),
 ("Curves", [
  ("The Rose", [r"$r=\cos(k\,\theta)$"], r"$k=7$",
   "A single polar equation traces a flower. When k is odd it draws k petals; when\neven, 2k. A garden hides in one line of trigonometry.", PL.g_rose),
  ("The Lissajous Figure", [r"$x=\sin(a t+\delta)$", r"$y=\sin(b t)$"], r"$a=5 \quad b=4 \quad \delta=\pi/2$",
   "Two perpendicular oscillations, drawn against each other. Simple whole-number\nratios weave closed, harmonic knots.", PL.g_lissajous),
  ("The Harmonograph", [r"$x(t)=e^{-dt}[\sin f_1 t+\sin f_2 t]$"], r"$\mathrm{two\ coupled\ pendulums}$",
   "The trace of coupled, slowly-dying pendulums — the Victorian machine that\ndrew mathematics as it swung to rest.", PL.g_harmono),
  ("The Butterfly Curve", [r"$x=\sin t\,(e^{\cos t}-2\cos 4t-\sin^{5}\frac{t}{12})$"], r"$0 \leq t \leq 12\pi$",
   "Fay's transcendental butterfly: one long parametric breath of sines and\nexponentials that closes into two wings.", PL.g_butterfly),
  ("The Hypotrochoid", [r"$x=(R-r)\cos t+d\cos\frac{(R-r)t}{r}$", r"$y=(R-r)\sin t-d\sin\frac{(R-r)t}{r}$"], None,
   "The spirograph curve: a small circle rolling inside a large one, a pen fixed to\nthe wheel tracing looping rosettes.", PL.g_hypotrochoid),
  ("The Epicycloid", [r"$x=(R+r)\cos t-r\cos\frac{(R+r)t}{r}$", r"$y=(R+r)\sin t-r\sin\frac{(R+r)t}{r}$"], None,
   "A circle rolling outside another — the very geometry Ptolemy used to hold the\nwandering planets in their courses.", PL.g_epicycloid),
  ("The Logarithmic Spiral", [r"$r=e^{\,b\,\theta}$"], r"$b=0.15$",
   "The equiangular spiral of shells, storms and galaxies: it grows without ever\nchanging its shape — spira mirabilis.", PL.g_logspiral),
  ("The Lemniscate", [r"$(x^{2}+y^{2})^{2}=a^{2}(x^{2}-y^{2})$"], None,
   "Bernoulli's figure-eight: the set of points whose distances to two foci multiply\nto a constant — infinity, drawn.", PL.g_lemniscate),
  ("The Cardioid", [r"$r=1-\cos\theta$"], None,
   "The heart curve: one point on a rolling circle — and the bright caustic that\ngathers in the bottom of your coffee cup.", PL.g_cardioid),
  ("The Astroid", [r"$x=\cos^{3} t \quad y=\sin^{3} t$"], None,
   "A four-cusped hypocycloid, and the envelope of a ladder as it slides down a\nwall — a star swept out by a moving line.", PL.g_astroid),
  ("The Deltoid", [r"$x=2\cos t+\cos 2t$", r"$y=2\sin t-\sin 2t$"], None,
   "A three-cusped hypocycloid, the graceful triangle a single wandering line can\nsweep as it turns.", PL.g_deltoid),
  ("Fermat's Spiral", [r"$r=\pm\sqrt{\theta}$"], None,
   "Fermat's spiral packs its arms like the seeds of a sunflower — each turn set by\nthe golden angle, filling space evenly.", PL.g_fermat),
 ]),
 ("Waves & Fields", [
  ("Chladni Figures", [r"$\cos n\pi x\,\cos m\pi y=\cos m\pi x\,\cos n\pi y$"], r"$n=7 \quad m=4$",
   "Sand on a vibrating plate flees the motion and gathers along the silent nodal\nlines — sound made visible.", PL.g_chladni),
  ("Wave Interference", [r"$I=(\cos k r_1+\cos k r_2)^{2}$"], None,
   "Two sources in one medium: crests meet crests in bright fringes and cancel to\ndark — the signature of every wave.", PL.g_interference),
  ("Standing Waves", [r"$u=\sin a\pi x\,\sin b\pi y$"], None,
   "A confined wave can only ring at certain shapes. These are the modes of a\nsquare membrane, superposed into flow.", PL.g_standing),
  ("The Vibrating Drum", [r"$u=J_m(\alpha_{mn}\,r)\,\cos m\theta$"], r"$m=3$",
   "A round drumhead vibrates in Bessel functions; its nodal circles and diameters\nset the overtones you hear.", PL.g_bessel),
  ("The Dipole Field", [r"$\mathbf{E}=\sum_k \dfrac{q_k(\mathbf{r}-\mathbf{r}_k)}{|\mathbf{r}-\mathbf{r}_k|^{3}}$"], None,
   "The electric field of two opposite charges: every line of force leaves the\npositive and dives into the negative.", PL.g_vectorfield),
 ]),
 ("Symmetry & Tilings", [
  ("Penrose Tiling", [r"$\varphi=\dfrac{1+\sqrt{5}}{2}$"], r"$36^{\circ}/72^{\circ}\ \mathrm{rhombi}$",
   "Two rhombi, built on the golden ratio, tile the plane so the pattern never\nexactly repeats — an aperiodic order once thought impossible.", PL.g_penrose),
  ("Girih Stars", [r"$\{8/3\}\ \mathrm{star\ polygon}$"], None,
   "An eight-fold Islamic girih grid — the strapwork geometry behind centuries of\ntilework, drawn from a handful of tiles.", PL.g_girih),
  ("Truchet Tiles", [r"$\mathrm{one\ arc\ tile},\ 4\ \mathrm{rotations}$"], None,
   "A single quarter-arc tile, dropped at random in four orientations, flows into an\nendless labyrinth of curves.", PL.g_truchet),
  ("Rhombille Tiling", [r"$\mathrm{rhombi\ at}\ 120^{\circ}$"], None,
   "Rhombi meeting three-to-a-point lock the eye into a field of tumbling three-\ndimensional cubes — an ancient optical trick.", PL.g_rhombille),
  ("The Sierpinski Triangle", [r"$S=\bigcup_{i}\ \frac{1}{2}(S+v_i)$"], None,
   "A triangle endlessly emptied of its middle — the same shape at every scale, a\nfractal you can draw with one simple rule.", PL.g_sierpinski),
  ("The Flower of Life", [r"$(x-x_k)^{2}+(y-y_k)^{2}=r^{2}$"], r"$\mathrm{hexagonal\ lattice}$",
   "Overlapping circles on a hexagonal lattice, each radius equal to the spacing —\nthe seed pattern of sacred geometry.", PL.g_flower),
 ]),
]

ROMAN = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV XXV XXVI XXVII XXVIII XXIX XXX XXXI XXXII XXXIII XXXIV XXXV XXXVI XXXVII XXXVIII".split()


def title_page():
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.plot([0.30, 0.70], [0.66, 0.66], color=ACC, lw=1.4)
    ax.text(0.5, 0.59, "THE MATHEMATICS", fontproperties=CINZEL, fontsize=41, color=INK, ha="center")
    ax.text(0.5, 0.515, "OF BEAUTY", fontproperties=CINZEL, fontsize=41, color=INK, ha="center")
    ax.text(0.5, 0.43, "A Visual Gallery of Equations, Curves and Chaos",
            fontproperties=RALEWAY_I, fontsize=17, color=SUB, ha="center")
    ax.plot([0.30, 0.70], [0.37, 0.37], color=ACC, lw=1.4)
    ax.text(0.5, 0.11, "MathRelaxing", fontproperties=CINZEL_R, fontsize=16, color=INK, ha="center")
    return MB.to_pil(fig, PAPER)


def foreword_page():
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.17, 0.72, "Foreword", fontproperties=CINZEL, fontsize=26, color=INK)
    ax.plot([0.17, 0.30], [0.685, 0.685], color=ACC, lw=1.2)
    body = ("Some equations do more than compute — they draw. A rule as short as a\n"
            "single line, repeated without mercy, can fold space into a butterfly,\n"
            "scatter light into a fractal coast, or tile a floor that never repeats.\n\n"
            "This gallery pairs each form with the mathematics that makes it. On the\n"
            "left, the equation and a few words; on the right, the picture it draws —\n"
            "every one generated from its own formula, nothing traced by hand.\n\n"
            "Turn slowly. The same short rules keep returning, in the swing of a\n"
            "pendulum, the shell of a snail, the arms of a distant galaxy.")
    ax.text(0.17, 0.60, body, fontproperties=RALEWAY, fontsize=14.5, color="#403c34", va="top", linespacing=1.7)
    return MB.to_pil(fig, PAPER)


def divider_page(name, n):
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.54, name.upper(), fontproperties=CINZEL, fontsize=32, color=INK, ha="center", va="center")
    ax.plot([0.40, 0.60], [0.47, 0.47], color=ACC, lw=1.3)
    ax.text(0.5, 0.43, f"{n} plates", fontproperties=RALEWAY_I, fontsize=14, color=SUB, ha="center", va="center")
    return MB.to_pil(fig, PAPER)


def blank_page():
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return MB.to_pil(fig, PAPER)


def colophon_page():
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.60, "Colophon", fontproperties=CINZEL, fontsize=22, color=INK, ha="center")
    txt = ("Every plate in this book was generated directly from its own mathematics —\n"
           "nothing traced, nothing drawn by hand. Typeset in Cinzel and Raleway,\n"
           "with equations in Computer Modern.")
    ax.text(0.5, 0.50, txt, fontproperties=RALEWAY, fontsize=13, color="#403c34", ha="center", va="top", linespacing=1.7)
    ax.text(0.5, 0.20, "MathRelaxing", fontproperties=CINZEL_R, fontsize=15, color=INK, ha="center")
    return MB.to_pil(fig, PAPER)


def front_cover():
    fig, ax = MB.fig_trim(DARK); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    t = np.linspace(0, 60, 30000)
    x = np.exp(-0.005 * t) * (np.sin(2.02 * t) + np.sin(2.99 * t + 1.1))
    y = np.exp(-0.005 * t) * (np.sin(3.01 * t) + np.sin(1.99 * t + 0.6))
    x = 0.5 + 0.33 * x / np.abs(x).max(); y = 0.55 + 0.33 * y / np.abs(y).max()
    pts = np.array([x, y]).T.reshape(-1, 1, 2); segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=MB.CMAP, linewidth=0.6, alpha=0.32)
    lc.set_array(np.linspace(0, 1, len(segs))); ax.add_collection(lc)
    ax.plot([0.28, 0.72], [0.30, 0.30], color=GOLD, lw=1.6)
    ax.text(0.5, 0.235, "THE MATHEMATICS", fontproperties=CINZEL, fontsize=37, color="#f0e9da", ha="center")
    ax.text(0.5, 0.16, "OF BEAUTY", fontproperties=CINZEL, fontsize=37, color=GOLD, ha="center")
    ax.plot([0.28, 0.72], [0.105, 0.105], color=GOLD, lw=1.6)
    ax.text(0.5, 0.07, "A Visual Gallery of Equations, Curves and Chaos",
            fontproperties=RALEWAY_I, fontsize=14.5, color="#b9b3a4", ha="center")
    base = MB.to_pil(fig, DARK)
    base = MB.pad_bleed(base, DARK)
    # discreet logo emblem at top (infinity mark only)
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.crop((0, 0, logo.width, int(logo.height * 0.76)))
    w = int(base.width * 0.16); h = int(w * logo.height / logo.width)
    logo = logo.resize((w, h), Image.Resampling.LANCZOS)
    a = logo.split()[3].point(lambda p: int(p * 0.9))
    base.paste(logo, ((base.width - w) // 2, int(base.height * 0.11)), a)
    out = os.path.join(OUT, "cover_front.png"); base.save(out)
    print("cover_front.png", os.path.getsize(out) // 1024, "KB"); return out


def build():
    pages = []  # (img, bg)

    def add(img, bg=PAPER): pages.append((img, bg))
    def ensure_recto():
        if len(pages) % 2 == 1: add(blank_page())   # next page becomes recto
    def ensure_verso():
        if len(pages) % 2 == 0: add(blank_page())   # next page becomes verso

    add(title_page())        # p1 recto
    add(foreword_page())     # p2 verso
    n = 0
    for sec, plates in SECTIONS:
        ensure_recto(); add(divider_page(sec, len(plates)))
        for title, eqs, params, desc, gfn in plates:
            n += 1
            ensure_verso()
            add(MB.text_page(sec, title, eqs, params, desc, f"PLATE {ROMAN[n-1]}"))
            print(f"  {ROMAN[n-1]:>6}  {title}")
            add(gfn(), DARK if _is_dark(gfn) else PAPER)
    add(colophon_page())
    if len(pages) % 2 == 1: add(blank_page())

    paths = []
    for i, (img, bg) in enumerate(pages):
        p = os.path.join(PGS, f"p{i:03d}.jpg")
        MB.pad_bleed(img, bg).save(p, "JPEG", quality=90, dpi=(DPI, DPI))
        paths.append(p)
    pdf = os.path.join(OUT, "interior.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print(f"\ninterior.pdf: {len(pages)} pages, {os.path.getsize(pdf)//1024//1024} MB")
    front_cover()
    return pdf


DARKSET = {PL.g_lorenz, PL.g_rossler, PL.g_thomas, PL.g_halvorsen, PL.g_chen, PL.g_dadras,
           PL.g_aizawa, PL.g_sprott, PL.g_fourwing, PL.g_julia, PL.g_mandel, PL.g_burning,
           PL.g_tricorn, PL.g_newton, PL.g_multibrot, PL.g_interference, PL.g_standing,
           PL.g_bessel, PL.g_vectorfield}
def _is_dark(fn): return fn in DARKSET


if __name__ == "__main__":
    build()
