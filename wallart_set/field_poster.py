"""
field_poster.py — premium "field plates": one poster gathers the canonical
equations of a whole area of physics with a real, computed hero visualization.
Dark observatory aesthetic, Computer-Modern (LaTeX-look) mathtype via matplotlib
mathtext, and scipy-computed physics for the graphics — not clip art, not AI.

Fields: quantum, blackhole.

    FIELD=quantum python field_poster.py
"""
import io
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import PowerNorm
from scipy.special import genlaguerre, eval_legendre, factorial
from PIL import Image

# --- palettes + LaTeX-look math ---------------------------------------------
# Dark (default product): deep observatory black.
# Light: cream paper + dark ink — same family as the equation_plates line;
#        built for readability when the black ground is too heavy.
PALETTES = {
    "dark": {
        "BG": "#0a0c12", "PANEL": "#11141d", "LINE": "#2b3242",
        "INK": "#e9ecf5", "SUB": "#828aa0", "ACC": "#6fc9d8",
        "GOLD": "#ffe2b0",  # highlight strokes on dark ground
    },
    "light": {
        "BG": "#F4F1EA", "PANEL": "#EDEAE3", "LINE": "#C8C2B4",
        "INK": "#1A1A1A", "SUB": "#555555", "ACC": "#1A7A8A",
        "GOLD": "#B85C38",  # rust highlight — readable on cream
    },
}

BG = PALETTES["dark"]["BG"]
PANEL = PALETTES["dark"]["PANEL"]
LINE = PALETTES["dark"]["LINE"]
INK = PALETTES["dark"]["INK"]
SUB = PALETTES["dark"]["SUB"]
ACC = PALETTES["dark"]["ACC"]
GOLD = PALETTES["dark"]["GOLD"]

SANS = font_manager.FontProperties(family="DejaVu Sans")
MONO = font_manager.FontProperties(family="DejaVu Sans Mono")
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"


def set_theme(name="dark"):
    """Switch global palette. Call before render/build. name: 'dark' | 'light'."""
    global BG, PANEL, LINE, INK, SUB, ACC, GOLD
    if name not in PALETTES:
        raise ValueError(f"unknown theme {name!r}; expected one of {list(PALETTES)}")
    p = PALETTES[name]
    BG, PANEL, LINE = p["BG"], p["PANEL"], p["LINE"]
    INK, SUB, ACC, GOLD = p["INK"], p["SUB"], p["ACC"], p["GOLD"]
    return name


def _tile_ax(fig, rect):
    a = fig.add_axes(rect); a.set_facecolor(BG); a.axis("off")
    return a


# --- hydrogen orbital density (m = 0, real) ---------------------------------
def orbital_density(n, l, extent, res=700):
    x = np.linspace(-extent, extent, res)
    X, Z = np.meshgrid(x, x)
    r = np.sqrt(X ** 2 + Z ** 2)
    ct = np.divide(Z, r, out=np.ones_like(r), where=r > 0)
    rho = 2.0 * r / n
    norm = np.sqrt((2.0 / n) ** 3 * factorial(n - l - 1) / (2 * n * factorial(n + l)))
    R = norm * np.exp(-rho / 2) * rho ** l * genlaguerre(n - l - 1, 2 * l + 1)(rho)
    Y = np.sqrt((2 * l + 1) / (4 * np.pi)) * eval_legendre(l, ct)
    return (R * Y) ** 2


def orbital_tile(n, l, ext):
    def draw(fig, rect):
        a = _tile_ax(fig, rect)
        d = orbital_density(n, l, ext)
        a.imshow(d, origin="lower", extent=[-ext, ext, -ext, ext], cmap="magma",
                 norm=PowerNorm(0.42, vmin=0, vmax=d.max()), interpolation="bilinear")
        a.set_xlim(-ext, ext); a.set_ylim(-ext, ext)
    return draw


# --- black-hole hero: shadow, photon ring, inclined accretion disk ----------
def blackhole_hero(fig, rect):
    a = _tile_ax(fig, rect)
    a.set_xlim(-1.4, 1.4); a.set_ylim(-1.4, 1.4); a.set_aspect("equal")
    rs = 0.5; tilt = 0.30
    def disk(front):
        phis = np.linspace(np.pi, 2 * np.pi, 160) if front else np.linspace(0, np.pi, 160)
        for rr in np.linspace(1.16 * rs, 2.55 * rs, 70):
            t = (rr - 1.16 * rs) / (1.39 * rs)             # 0 inner .. 1 outer
            col = plt.cm.inferno(0.30 + 0.62 * (1 - t))
            a.plot(rr * np.cos(phis), rr * tilt * np.sin(phis), color=col,
                   lw=1.7, alpha=max(0.05, (1 - t) * 0.95),
                   zorder=3 if front else 1, solid_capstyle="round")
    disk(front=False)
    a.add_patch(plt.Circle((0, 0), rs, facecolor="#000000", edgecolor="none", zorder=2))
    a.add_patch(plt.Circle((0, 0), rs * 1.03, fill=False, edgecolor=GOLD,
                lw=1.6, alpha=0.95, zorder=2.6))           # photon ring
    disk(front=True)


def bh_struct_tile(hi_r, hi_style):
    """Mini radial diagram: filled horizon + one highlighted ring at hi_r (in r_s)."""
    def draw(fig, rect):
        a = _tile_ax(fig, rect)
        m = max(3.4, hi_r + 0.6)
        a.set_xlim(-m, m); a.set_ylim(-m, m); a.set_aspect("equal")
        a.add_patch(plt.Circle((0, 0), 1.0, facecolor="#000000", edgecolor=SUB, lw=0.8))
        if hi_r > 1.0:
            a.add_patch(plt.Circle((0, 0), hi_r, fill=False, edgecolor=ACC,
                        lw=1.4, linestyle=hi_style))
    return draw


# --- special relativity: Minkowski diagram ----------------------------------
def relativity_hero(fig, rect):
    a = _tile_ax(fig, rect); a.set_xlim(-1.15, 1.15); a.set_ylim(-1.15, 1.15); a.set_aspect("equal")
    a.fill([0, 1.15, -1.15], [0, 1.15, 1.15], color=ACC, alpha=0.05)
    a.fill([0, 1.15, -1.15], [0, -1.15, -1.15], color=ACC, alpha=0.05)
    a.plot([-1.12, 1.12], [-1.12, 1.12], color=GOLD, lw=1.4)
    a.plot([-1.12, 1.12], [1.12, -1.12], color=GOLD, lw=1.4)
    xx = np.linspace(-1.12, 1.12, 300)
    for k in (0.3, 0.6, 0.9):
        a.plot(xx, np.sqrt(xx ** 2 + k ** 2), color=SUB, lw=0.7, alpha=0.55)
        a.plot(xx, -np.sqrt(xx ** 2 + k ** 2), color=SUB, lw=0.7, alpha=0.55)
        a.plot(np.sqrt(xx ** 2 + k ** 2), xx, color=LINE, lw=0.6, alpha=0.5)
        a.plot(-np.sqrt(xx ** 2 + k ** 2), xx, color=LINE, lw=0.6, alpha=0.5)
    a.axhline(0, color=SUB, lw=0.6); a.axvline(0, color=SUB, lw=0.6)
    b = 0.45
    a.plot([-1.12, 1.12], [-1.12 * b, 1.12 * b], color=INK, lw=1.3)
    a.plot([-1.12 * b, 1.12 * b], [-1.12, 1.12], color=INK, lw=1.3)


def sr_boost_tile(b):
    def draw(fig, rect):
        a = _tile_ax(fig, rect); a.set_xlim(-1.05, 1.05); a.set_ylim(-1.05, 1.05); a.set_aspect("equal")
        a.plot([-1, 1], [-1, 1], color=GOLD, lw=1.0); a.plot([-1, 1], [1, -1], color=GOLD, lw=1.0)
        a.axhline(0, color=SUB, lw=0.5); a.axvline(0, color=SUB, lw=0.5)
        a.plot([-1, 1], [-b, b], color=ACC, lw=1.3); a.plot([-b, b], [-1, 1], color=ACC, lw=1.3)
    return draw


# --- electromagnetism: field lines via streamplot ---------------------------
def _stream(a, charges, ext=1.5, res=200, dens=1.3):
    Y, X = np.mgrid[-ext:ext:res * 1j, -ext:ext:res * 1j]
    Ex = np.zeros_like(X); Ey = np.zeros_like(X)
    for qx, qy, q in charges:
        dx = X - qx; dy = Y - qy; r = (dx ** 2 + dy ** 2 + 2e-3) ** 1.5
        Ex += q * dx / r; Ey += q * dy / r
    mag = np.hypot(Ex, Ey)
    a.set_xlim(-ext, ext); a.set_ylim(-ext, ext); a.set_aspect("equal")
    a.streamplot(X, Y, Ex, Ey, color=np.log(mag + 1), cmap="plasma", density=dens,
                 linewidth=0.7, arrowsize=0.55)
    for qx, qy, q in charges:
        a.scatter([qx], [qy], c="#ff7a7a" if q > 0 else "#7ab5ff", s=26, zorder=5, edgecolors="none")


def em_hero(fig, rect):
    _stream(_tile_ax(fig, rect), [(0.45, 0, 1), (-0.45, 0, -1)], ext=1.5, res=240, dens=1.5)


def em_tile(charges):
    def draw(fig, rect):
        _stream(_tile_ax(fig, rect), charges, ext=1.4, res=130, dens=1.0)
    return draw


# --- thermodynamics: Maxwell-Boltzmann + PV processes -----------------------
def thermo_hero(fig, rect):
    a = _tile_ax(fig, rect); v = np.linspace(0, 3.2, 500)
    a.set_xlim(0, 3.2); a.set_ylim(0, 1.15)
    for T, col in [(0.35, "#6fb1ff"), (0.8, "#c77dff"), (1.6, "#ff8a5c")]:
        f = v ** 2 * np.exp(-v ** 2 / (2 * T)); f /= f.max()
        a.plot(v, f, color=col, lw=2.3, alpha=0.95)
    a.plot([0, 3.2], [0, 0], color=SUB, lw=0.7); a.plot([0, 0], [0, 1.15], color=SUB, lw=0.7)


def pv_tile(kind):
    def draw(fig, rect):
        a = _tile_ax(fig, rect); V = np.linspace(0.35, 2.1, 200)
        a.set_xlim(0.15, 2.2); a.set_ylim(0, 3.2)
        if kind == "iso":
            for c in (0.6, 1.1, 1.7):
                a.plot(V, c / V, color=ACC, lw=1.1, alpha=0.85)
        elif kind == "adia":
            for c in (0.5, 0.9, 1.4):
                a.plot(V, c / V ** 1.667, color="#ff8a5c", lw=1.1, alpha=0.85)
        else:  # iso-P / iso-V
            for p in (0.8, 1.6, 2.4):
                a.plot([0.35, 2.1], [p, p], color=ACC, lw=1.0, alpha=0.8)
            for vv in (0.6, 1.1, 1.6):
                a.plot([vv, vv], [0.2, 3.0], color="#ff8a5c", lw=1.0, alpha=0.7)
        a.plot([0.15, 2.2], [0, 0], color=SUB, lw=0.5); a.plot([0.15, 0.15], [0, 3.2], color=SUB, lw=0.5)
    return draw


# --- classical mechanics: pendulum phase portrait ---------------------------
def mechanics_hero(fig, rect):
    a = _tile_ax(fig, rect)
    th = np.linspace(-np.pi, np.pi, 400); p = np.linspace(-3, 3, 400)
    TH, P = np.meshgrid(th, p)
    E = 0.5 * P ** 2 - np.cos(TH)
    a.set_xlim(-np.pi, np.pi); a.set_ylim(-3, 3)
    a.contour(TH, P, E, levels=np.linspace(-0.9, 3.0, 13), cmap="magma", linewidths=0.8)
    a.contour(TH, P, E, levels=[1.0], colors=[GOLD], linewidths=1.5)     # separatrix
    a.axhline(0, color=SUB, lw=0.5)


def sho_tile():
    def draw(fig, rect):
        a = _tile_ax(fig, rect); a.set_xlim(-1.2, 1.2); a.set_ylim(-1.2, 1.2); a.set_aspect("equal")
        t = np.linspace(0, 2 * np.pi, 200)
        for r in (0.35, 0.65, 0.95):
            a.plot(r * np.cos(t), r * np.sin(t), color=ACC, lw=1.0, alpha=0.85)
        a.axhline(0, color=SUB, lw=0.5); a.axvline(0, color=SUB, lw=0.5)
    return draw


def kepler_tile():
    def draw(fig, rect):
        a = _tile_ax(fig, rect); a.set_aspect("equal"); a.set_xlim(-1.35, 1.15); a.set_ylim(-1.1, 1.1)
        t = np.linspace(0, 2 * np.pi, 300); e = 0.6; A = 1.0; B = A * np.sqrt(1 - e ** 2)
        a.plot(A * np.cos(t) - A * e, B * np.sin(t), color=ACC, lw=1.3)
        a.scatter([0], [0], c="#ffcf6b", s=26, zorder=5, edgecolors="none")
    return draw


def projectile_tile():
    def draw(fig, rect):
        a = _tile_ax(fig, rect); x = np.linspace(0, 1, 100)
        for v in (0.55, 0.78, 1.0):
            a.plot(x, v * 4 * x * (1 - x), color="#ff8a5c", lw=1.2, alpha=0.9)
        a.plot([0, 1], [0, 0], color=SUB, lw=0.6)
        a.set_xlim(-0.03, 1.03); a.set_ylim(-0.02, 1.08)
    return draw


# --- fields ------------------------------------------------------------------
QUANTUM = {
    "title": "QUANTUM MECHANICS", "eyebrow": "THE PHYSICS OF THE VERY SMALL", "plate": "PLATE I",
    "hero": blackhole_hero if False else orbital_tile(3, 2, 34),
    "hero_caption": "HYDROGEN  ·  3d ORBITAL  ·  |ψ|²",
    "strip": [(orbital_tile(1, 0, 6), "1s"), (orbital_tile(2, 1, 16), "2p"),
              (orbital_tile(3, 2, 32), "3d"), (orbital_tile(4, 3, 54), "4f")],
    "eqs": [
        (r"$i\hbar\,\frac{\partial \psi}{\partial t} = \hat{H}\psi$", "time-dependent Schrödinger"),
        (r"$[\hat{x},\hat{p}] = i\hbar$", "canonical commutator"),
        (r"$\hat{H}\psi = E\psi$", "stationary states"),
        (r"$\lambda = \frac{h}{p}$", "de Broglie wavelength"),
        (r"$\hat{H} = -\frac{\hbar^{2}}{2m}\nabla^{2} + V$", "the Hamiltonian"),
        (r"$\langle A\rangle = \int \psi^{*}\hat{A}\,\psi\,dx$", "expectation value"),
        (r"$\Delta x\,\Delta p \geq \frac{\hbar}{2}$", "Heisenberg uncertainty"),
        (r"$P = |\psi|^{2}$", "Born rule"),
    ],
    "constants": r"$\hbar = 1.055\times10^{-34}\ \mathrm{J\,s}$        $h = 6.626\times10^{-34}\ \mathrm{J\,s}$",
    "footnote": "Hero: the hydrogen 3d orbital, |ψ|² in the x–z plane — solved from the Schrödinger equation.",
}

BLACKHOLE = {
    "title": "BLACK HOLES", "eyebrow": "SPACETIME AT THE EXTREME", "plate": "PLATE II",
    "hero": blackhole_hero,
    "hero_caption": "SCHWARZSCHILD BLACK HOLE  ·  SHADOW & ACCRETION DISK",
    "strip": [(bh_struct_tile(1.0, "-"), "horizon  rₛ"),
              (bh_struct_tile(1.5, (0, (4, 3))), "photon sphere"),
              (bh_struct_tile(3.0, (0, (5, 4))), "ISCO  3rₛ")],
    "eqs": [
        (r"$G_{\mu\nu} = \frac{8\pi G}{c^{4}}\,T_{\mu\nu}$", "Einstein field equations"),
        (r"$r_{s} = \frac{2GM}{c^{2}}$", "event horizon radius"),
        (r"$T_{H} = \frac{\hbar c^{3}}{8\pi G M k_{B}}$", "Hawking temperature"),
        (r"$r_{\mathrm{ph}} = \frac{3GM}{c^{2}}$", "photon sphere"),
        (r"$S = \frac{k_{B}\,c^{3}A}{4 G\hbar}$", "black-hole entropy"),
        (r"$r_{\mathrm{isco}} = \frac{6GM}{c^{2}}$", "innermost stable orbit"),
        (r"$d\tau = dt\,\sqrt{1-\frac{r_s}{r}}$", "gravitational time dilation"),
        (r"$v_{\mathrm{esc}} = \sqrt{\frac{2GM}{r}}$", "escape velocity"),
    ],
    "constants": r"$r_s(\mathrm{Sun}) \approx 2.95\ \mathrm{km}$        $G = 6.674\times10^{-11}\ \mathrm{m^{3}kg^{-1}s^{-2}}$",
    "footnote": "Hero: the shadow, photon ring and inclined accretion disk of a Schwarzschild black hole.",
}

RELATIVITY = {
    "title": "SPECIAL RELATIVITY", "eyebrow": "SPACE, TIME AND LIGHT", "plate": "PLATE III",
    "hero": relativity_hero, "hero_caption": "MINKOWSKI SPACETIME  ·  LIGHT CONE & BOOST",
    "strip": [(sr_boost_tile(0.3), "β = 0.3"), (sr_boost_tile(0.6), "β = 0.6"), (sr_boost_tile(0.85), "β = 0.85")],
    "eqs": [
        (r"$E = mc^{2}$", "mass–energy equivalence"),
        (r"$\Delta t = \gamma\,\Delta\tau$", "time dilation"),
        (r"$\gamma = \frac{1}{\sqrt{1-v^{2}/c^{2}}}$", "the Lorentz factor"),
        (r"$L = L_{0}/\gamma$", "length contraction"),
        (r"$E^{2} = (pc)^{2} + (mc^{2})^{2}$", "energy–momentum relation"),
        (r"$s^{2} = (ct)^{2} - x^{2}$", "invariant interval"),
        (r"$p = \gamma m v$", "relativistic momentum"),
        (r"$u' = \frac{u+v}{1 + uv/c^{2}}$", "velocity addition"),
    ],
    "constants": r"$c = 2.998\times10^{8}\ \mathrm{m/s}$        $E = mc^{2}$",
    "footnote": "Hero: a Minkowski diagram — the light cone, invariant hyperbolae and a boosted frame.",
}

ELECTROMAGNETISM = {
    "title": "ELECTROMAGNETISM", "eyebrow": "FIELDS, CHARGES AND LIGHT", "plate": "PLATE IV",
    "hero": em_hero, "hero_caption": "ELECTRIC DIPOLE  ·  FIELD LINES",
    "strip": [(em_tile([(0, 0, 1)]), "point charge"),
              (em_tile([(0.4, 0, 1), (-0.4, 0, -1)]), "dipole"),
              (em_tile([(0.4, 0, 1), (-0.4, 0, 1)]), "like charges")],
    "eqs": [
        (r"$\nabla\cdot\mathbf{E} = \frac{\rho}{\varepsilon_{0}}$", "Gauss's law"),
        (r"$\nabla\times\mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$", "Faraday's law"),
        (r"$\nabla\cdot\mathbf{B} = 0$", "no magnetic monopoles"),
        (r"$\nabla\times\mathbf{B} = \mu_{0}\mathbf{J} + \mu_{0}\varepsilon_{0}\,\partial_{t}\mathbf{E}$", "Ampère–Maxwell law"),
        (r"$\mathbf{F} = q(\mathbf{E} + \mathbf{v}\times\mathbf{B})$", "Lorentz force"),
        (r"$c = 1/\sqrt{\mu_{0}\varepsilon_{0}}$", "speed of light"),
        (r"$\mathbf{S} = \frac{1}{\mu_{0}}\mathbf{E}\times\mathbf{B}$", "Poynting vector"),
        (r"$u = \frac{1}{2}\left(\varepsilon_{0}E^{2} + \frac{B^{2}}{\mu_{0}}\right)$", "field energy density"),
    ],
    "constants": r"$\varepsilon_{0} = 8.854\times10^{-12}$        $\mu_{0} = 1.257\times10^{-6}$",
    "footnote": "Hero: the electric field lines of a dipole — streamlines computed from Coulomb's law.",
}

THERMODYNAMICS = {
    "title": "THERMODYNAMICS", "eyebrow": "HEAT, ENTROPY AND ENERGY", "plate": "PLATE V",
    "hero": thermo_hero, "hero_caption": "MAXWELL–BOLTZMANN  ·  SPEED DISTRIBUTION",
    "strip": [(pv_tile("iso"), "isothermal"), (pv_tile("adia"), "adiabatic"), (pv_tile("isoPV"), "iso-P / iso-V")],
    "eqs": [
        (r"$dU = \delta Q - \delta W$", "first law"),
        (r"$dS \geq 0$", "second law"),
        (r"$PV = N k_{B} T$", "ideal gas law"),
        (r"$S = k_{B}\ln\Omega$", "Boltzmann entropy"),
        (r"$\eta = 1 - \frac{T_{c}}{T_{h}}$", "Carnot efficiency"),
        (r"$j = \sigma T^{4}$", "Stefan–Boltzmann law"),
        (r"$G = H - TS$", "Gibbs free energy"),
        (r"$\langle E\rangle = \frac{3}{2}k_{B}T$", "equipartition"),
    ],
    "constants": r"$k_{B} = 1.381\times10^{-23}\ \mathrm{J/K}$        $\sigma = 5.67\times10^{-8}$",
    "footnote": "Hero: the Maxwell–Boltzmann speed distribution at three temperatures.",
}

MECHANICS = {
    "title": "CLASSICAL MECHANICS", "eyebrow": "MOTION, FORCE AND ENERGY", "plate": "PLATE VI",
    "hero": mechanics_hero, "hero_caption": "PENDULUM PHASE PORTRAIT  ·  SEPARATRIX",
    "strip": [(sho_tile(), "phase space"), (kepler_tile(), "orbit"), (projectile_tile(), "projectile")],
    "eqs": [
        (r"$\mathbf{F} = \frac{d\mathbf{p}}{dt}$", "Newton's second law"),
        (r"$F = \frac{G m_{1} m_{2}}{r^{2}}$", "law of gravitation"),
        (r"$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}} = \frac{\partial L}{\partial q}$", "Euler–Lagrange equation"),
        (r"$E = \frac{1}{2}mv^{2} + V$", "total energy"),
        (r"$\dot{q} = \partial_{p}H,\ \ \dot{p} = -\partial_{q}H$", "Hamilton's equations"),
        (r"$\mathbf{L} = \mathbf{r}\times\mathbf{p}$", "angular momentum"),
        (r"$\omega = \sqrt{k/m}$", "harmonic oscillator"),
        (r"$T^{2} \propto a^{3}$", "Kepler's third law"),
    ],
    "constants": r"$G = 6.674\times10^{-11}\ \mathrm{m^{3}kg^{-1}s^{-2}}$",
    "footnote": "Hero: the phase portrait of a pendulum — trajectories and the separatrix (E = 1).",
}

FIELDS = {"quantum": QUANTUM, "blackhole": BLACKHOLE, "relativity": RELATIVITY,
          "electromagnetism": ELECTROMAGNETISM, "thermodynamics": THERMODYNAMICS,
          "mechanics": MECHANICS}


def render(field, W=10.0, H=12.5, dpi=200):
    c = FIELDS[field]
    fig = plt.figure(figsize=(W, H), dpi=dpi); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ML, MR = 0.075, 0.075

    ax.add_patch(plt.Rectangle((0.028, 0.022), 0.944, 0.956, fill=False, edgecolor=LINE, lw=1.1))
    ax.text(ML, 0.945, c["title"], fontproperties=SANS, fontsize=W * 3.05, color=INK, weight="bold", va="center")
    ax.text(0.972, 0.947, c["plate"], fontproperties=MONO, fontsize=W * 1.15, color=SUB, ha="right", va="center")
    ax.text(ML, 0.915, c["eyebrow"], fontproperties=MONO, fontsize=W * 1.2, color=ACC, va="center")
    ax.plot([ML, 1 - MR], [0.900, 0.900], color=LINE, lw=1.0)

    def frame(rx, ry, rw, rh):
        ax.add_patch(plt.Rectangle((rx, ry), rw, rh, fill=False, edgecolor=LINE, lw=1.0))

    # hero
    hw, hh = 3.5 / W, 3.5 / H
    hx, hy = 0.5 - hw / 2, 0.590
    ax.text(0.5, 0.879, c["hero_caption"], fontproperties=MONO, fontsize=W * 0.95, color=SUB, ha="center", va="center")
    c["hero"](fig, [hx, hy, hw, hh]); frame(hx, hy, hw, hh)

    # strip
    strip = c["strip"]; nS = len(strip)
    tw, th = 1.5 / W, 1.5 / H
    gap = 0.05
    total = nS * tw + (nS - 1) * gap
    x0 = 0.5 - total / 2; ty = 0.450
    for i, (drawer, lab) in enumerate(strip):
        rx = x0 + i * (tw + gap)
        drawer(fig, [rx, ty, tw, th]); frame(rx, ty, tw, th)
        ax.text(rx + tw / 2, ty - 0.012, lab, fontproperties=MONO, fontsize=W * 0.95, color=ACC, ha="center", va="top")
    ax.plot([ML, 1 - MR], [0.423, 0.423], color=LINE, lw=1.0)

    # equations — two columns × four rows
    col_x = [ML + 0.02, 0.53]; row_y = [0.385, 0.305, 0.225, 0.145]
    for i, (eq, lab) in enumerate(c["eqs"]):
        x = col_x[i // 4]; y = row_y[i % 4]
        ax.text(x, y, eq, fontsize=W * 2.0, color=INK, va="center", ha="left")
        ax.text(x, y - 0.038, lab, fontproperties=MONO, fontsize=W * 0.9, color=SUB, va="center", ha="left")

    ax.plot([ML, 1 - MR], [0.095, 0.095], color=LINE, lw=1.0)
    ax.text(ML, 0.070, c["constants"], fontsize=W * 1.1, color=ACC, va="center")
    ax.text(ML, 0.043, c["footnote"], fontproperties=SANS, fontsize=W * 0.82, color=SUB, va="center")
    ax.text(0.972, 0.052, "M A T H R E L A X I N G", fontproperties=MONO, fontsize=W * 0.95, color=SUB, ha="right", va="center")
    return fig


def to_pil(fig, dpi=200):
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor=BG, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGB")


if __name__ == "__main__":
    field = os.environ.get("FIELD", "quantum")
    im = to_pil(render(field, dpi=170))
    p = f"/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/field_{field}.png"
    im.save(p); print("saved", p, im.size)
