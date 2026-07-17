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

# --- premium dark palette + LaTeX-look math ---------------------------------
BG = "#0a0c12"; PANEL = "#11141d"; LINE = "#2b3242"
INK = "#e9ecf5"; SUB = "#828aa0"; ACC = "#6fc9d8"
SANS = font_manager.FontProperties(family="DejaVu Sans")
MONO = font_manager.FontProperties(family="DejaVu Sans Mono")
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"


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
    a.add_patch(plt.Circle((0, 0), rs * 1.03, fill=False, edgecolor="#ffe2b0",
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

FIELDS = {"quantum": QUANTUM, "blackhole": BLACKHOLE}


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
