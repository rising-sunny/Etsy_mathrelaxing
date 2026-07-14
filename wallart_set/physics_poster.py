"""
physics_poster.py — "Famous Physics" scientific plates: relativity, black
holes, quantum mechanics, electromagnetism, Planck's law, gravitation. Same
lab-paper / sans-mono house style as the maths line (concept_poster), so the
two series hang together as one collection. Every curve is computed from the
physics — the Lorentz factor, real Hermite wavefunctions, Planck's law, a true
Kepler ellipse with equal-area sectors — not decorative AI art.

Concepts: relativity, blackhole, quantum, maxwell, planck, gravity.
Layout is proportional, so plates render cleanly at any aspect ratio.
"""
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from numpy.polynomial.hermite import hermval

# reuse the exact house style + plate scaffolding from the maths line
from concept_poster import (SANS, MONO, PAPER, INK, SUB, ACC, GRIDC,
                            render_plate, to_pil)


# ----- figure bodies (draw within box = (x0, x1, y0, y1)) --------------------
def fig_relativity(ax, box, W):
    """Lorentz factor γ = 1/√(1 − β²) blowing up as v → c."""
    x0, x1, y0, y1 = box
    ax0, ay0 = x0 + 0.55, y0 + 0.55          # plot origin (inside the box)
    axw, axh = x1 - ax0 - 0.2, y1 - ay0 - 0.25
    gmax = 6.0
    b = np.linspace(0, 0.9986, 900)
    g = 1 / np.sqrt(1 - b ** 2)
    X = ax0 + b * axw
    Y = ay0 + np.clip(g - 1, 0, gmax - 1) / (gmax - 1) * axh
    # axes
    ax.plot([ax0, ax0 + axw], [ay0, ay0], color=SUB, lw=0.8)
    ax.plot([ax0, ax0], [ay0, ay0 + axh], color=SUB, lw=0.8)
    for gv in (1, 2, 3, 4, 5, 6):
        yy = ay0 + (gv - 1) / (gmax - 1) * axh
        ax.plot([ax0 - 0.05, ax0], [yy, yy], color=SUB, lw=0.8)
        ax.text(ax0 - 0.12, yy, f"{gv}", fontproperties=MONO, fontsize=W * 0.9,
                color=SUB, ha="right", va="center")
    for bv in (0, 0.25, 0.5, 0.75, 1.0):
        xx = ax0 + bv * axw
        ax.plot([xx, xx], [ay0 - 0.05, ay0], color=SUB, lw=0.8)
        ax.text(xx, ay0 - 0.14, f"{bv:g}", fontproperties=MONO, fontsize=W * 0.9,
                color=SUB, ha="center", va="top")
    # asymptote v = c
    ax.plot([ax0 + axw, ax0 + axw], [ay0, ay0 + axh], color=ACC, lw=0.9,
            ls=(0, (4, 3)))
    ax.text(ax0 + axw, ay0 + axh + 0.02, "v = c", fontproperties=MONO,
            fontsize=W * 1.0, color=ACC, ha="right", va="bottom")
    # the curve
    ax.plot(X, Y, color=INK, lw=2.0)
    # mark γ = 2 at β = √3/2
    b2 = np.sqrt(3) / 2; x2 = ax0 + b2 * axw; y2 = ay0 + 1 / (gmax - 1) * axh
    ax.plot([ax0, x2], [y2, y2], color=SUB, lw=0.6, ls=(0, (2, 3)))
    ax.plot([x2, x2], [ay0, y2], color=SUB, lw=0.6, ls=(0, (2, 3)))
    ax.scatter([x2], [y2], s=W * 1.6, color=ACC, zorder=5)
    ax.text(x2 + 0.08, y2 - 0.05, "at 87% of c,\nclocks run half-speed",
            fontproperties=SANS, fontsize=W * 0.82, color=SUB, va="top")
    ax.text(ax0 - 0.12, ay0 + axh + 0.02, "γ", fontproperties=SANS,
            fontsize=W * 1.2, color=INK, ha="right", va="bottom")
    ax.text(ax0 + axw, ay0 - 0.32, "speed  v / c", fontproperties=SANS,
            fontsize=W * 0.95, color=SUB, ha="right", va="top")


def fig_blackhole(ax, box, W):
    """Schwarzschild geometry drawn to scale: horizon, photon sphere, ISCO."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 0.1
    span = min(x1 - x0, y1 - y0)
    u = span / 2 / 3.4                      # length of one r_s on the page
    # gravitational-lensing halo (faint radial rings outside the horizon)
    for k in range(14, 0, -1):
        rr = u * (1.0 + k * 0.16)
        ax.add_patch(mp.Circle((cx, cy), rr, fill=False, edgecolor=SUB,
                     lw=0.5, alpha=0.05 + 0.03 * (14 - k) / 14))
    # ISCO (innermost stable circular orbit) at 3 r_s
    ax.add_patch(mp.Circle((cx, cy), 3 * u, fill=False, edgecolor=SUB,
                 lw=0.9, ls=(0, (5, 4))))
    # photon sphere at 1.5 r_s
    ax.add_patch(mp.Circle((cx, cy), 1.5 * u, fill=False, edgecolor=ACC,
                 lw=1.2, ls=(0, (4, 3))))
    # event horizon: solid black disk at r_s
    ax.add_patch(mp.Circle((cx, cy), u, facecolor=INK, edgecolor=INK, lw=0))
    # radius marker
    ax.annotate("", xy=(cx + u, cy), xytext=(cx, cy),
                arrowprops=dict(arrowstyle="-|>", color=PAPER, lw=1.4))
    ax.text(cx + u * 0.5, cy + 0.12, "rₛ", fontproperties=MONO,
            fontsize=W * 1.0, color=PAPER, ha="center")
    # labels with leader lines
    def label(r, text, color, dy):
        px = cx + r * np.cos(np.radians(58)); py = cy + r * np.sin(np.radians(58))
        ax.plot([px, cx + span * 0.42], [py, cy + r + dy], color=color, lw=0.6)
        ax.text(cx + span * 0.44, cy + r + dy, text, fontproperties=SANS,
                fontsize=W * 0.85, color=color, va="center")
    label(u, "event horizon  ·  rₛ = 2GM/c²", INK, 0.02)
    label(1.5 * u, "photon sphere  ·  1.5 rₛ", ACC, 0.05)
    label(3 * u, "innermost stable orbit  ·  3 rₛ", SUB, 0.05)


def fig_quantum(ax, box, W):
    """Quantum harmonic oscillator: V = ½x², quantised levels, real ψₙ(x)."""
    x0, x1, y0, y1 = box
    xa, xb = x0 + 0.35, x1 - 0.35
    xspan = xb - xa
    nlev = 5
    xmax = 4.2
    x = np.linspace(-xmax, xmax, 600)
    def X(u):                                # physics-x → page-x
        return xa + (u + xmax) / (2 * xmax) * xspan
    Emax = nlev - 1 + 0.5
    yb, yt = y0 + 0.35, y1 - 0.3
    def Y(E):                                # energy → page-y
        return yb + (E + 0.5) / (Emax + 1.3) * (yt - yb)
    # potential well V = ½ x²  (clipped so its arms stop at the box top)
    V = 0.5 * x ** 2
    vis = V <= (Emax + 0.8)
    ax.plot(X(x[vis]), Y(V[vis]), color=SUB, lw=1.1)
    # energy levels + wavefunctions
    for n in range(nlev):
        E = n + 0.5
        # classical turning points ½x² = E  →  x = ±√(2E)
        xt = np.sqrt(2 * E)
        ax.plot([X(-xt), X(xt)], [Y(E), Y(E)], color=GRIDC, lw=0.8)
        # ψ_n via physicists' Hermite, offset onto its level
        c = np.zeros(n + 1); c[n] = 1
        psi = hermval(x, c) * np.exp(-x ** 2 / 2)
        psi = psi / np.max(np.abs(psi)) * 0.42
        col = ACC if n % 2 == 0 else INK
        ax.plot(X(x), Y(E) + psi * (yt - yb) / (Emax + 1.3), color=col, lw=1.4)
        ax.text(xa - 0.12, Y(E), f"n={n}", fontproperties=MONO,
                fontsize=W * 0.85, color=SUB, ha="right", va="center")
        ax.text(xb + 0.1, Y(E), f"{2*n+1}/2 ℏω", fontproperties=MONO,
                fontsize=W * 0.8, color=SUB, ha="left", va="center")
    ax.text((xa + xb) / 2, yb - 0.28, "position  x",
            fontproperties=SANS, fontsize=W * 0.9, color=SUB, ha="center", va="top")
    ax.text(xa - 0.12, yt + 0.02, "energy", fontproperties=SANS,
            fontsize=W * 0.9, color=INK, ha="right", va="bottom")


def fig_maxwell(ax, box, W):
    """A travelling EM wave: E and B fields, transverse and in phase."""
    x0, x1, y0, y1 = box
    cy = (y0 + y1) / 2
    xa, xb = x0 + 0.3, x1 - 0.35
    z = np.linspace(0, 1, 600)
    L = xb - xa
    amp = (y1 - y0) * 0.30
    skew = 0.34                              # depth direction for B (drawn skew)
    wave = np.sin(2 * np.pi * 2 * z)
    # propagation axis
    ax.annotate("", xy=(xb + 0.12, cy), xytext=(xa - 0.05, cy),
                arrowprops=dict(arrowstyle="-|>", color=SUB, lw=1.0))
    ax.text(xb + 0.14, cy - 0.12, "propagation", fontproperties=SANS,
            fontsize=W * 0.85, color=SUB, va="top")
    # E field: vertical (in the page)
    Ex = xa + z * L; Ey = cy + wave * amp
    ax.plot(Ex, Ey, color=ACC, lw=1.9)
    for i in range(0, len(z), 26):
        ax.plot([Ex[i], Ex[i]], [cy, Ey[i]], color=ACC, lw=0.7, alpha=0.55)
    # B field: perpendicular, drawn skew to fake the 3rd axis
    Bx = xa + z * L + wave * amp * skew
    By = cy + wave * amp * skew
    ax.plot(Bx, By, color=INK, lw=1.5, alpha=0.9)
    for i in range(0, len(z), 26):
        ax.plot([xa + z[i] * L, Bx[i]], [cy, By[i]], color=INK, lw=0.6, alpha=0.4)
    # one wavelength bracket
    z0, z1 = 0.0, 0.5
    yb = cy - amp - 0.28
    ax.annotate("", xy=(xa + z1 * L, yb), xytext=(xa + z0 * L, yb),
                arrowprops=dict(arrowstyle="<->", color=SUB, lw=0.8))
    ax.text(xa + 0.25 * L, yb - 0.03, "λ", fontproperties=MONO,
            fontsize=W * 1.1, color=SUB, ha="center", va="top")
    ax.text(xa + 0.02, cy + amp + 0.06, "E", fontproperties=SANS, weight="bold",
            fontsize=W * 1.3, color=ACC, va="bottom")
    ax.text(xa + 0.02 + amp * skew, cy + amp * skew + 0.06, "B",
            fontproperties=SANS, weight="bold", fontsize=W * 1.15, color=INK, va="bottom")


def fig_planck(ax, box, W):
    """Planck's law: blackbody spectra at several temperatures (Wien's peak)."""
    x0, x1, y0, y1 = box
    xa, xb = x0 + 0.5, x1 - 0.3
    yb, yt = y0 + 0.5, y1 - 0.25
    lam = np.linspace(0.1e-6, 2.2e-6, 900)   # 0.1–2.2 µm
    h, c, kB = 6.626e-34, 2.998e8, 1.381e-23
    def planck(l, T):
        return (2 * h * c ** 2 / l ** 5) / (np.exp(h * c / (l * kB * T)) - 1)
    temps = [(3500, SUB), (4500, ACC), (5778, INK)]
    curves = {T: planck(lam, T) for T, _ in temps}
    gmax = max(v.max() for v in curves.values())
    def X(l):
        return xa + (l - lam[0]) / (lam[-1] - lam[0]) * (xb - xa)
    def Y(v):
        return yb + v / gmax * (yt - yb) * 0.90     # headroom for peak labels
    # visible band
    for l0, l1, col in [(0.40e-6, 0.75e-6, "#c9ccc4")]:
        ax.add_patch(mp.Rectangle((X(l0), yb), X(l1) - X(l0), yt - yb,
                     color=col, alpha=0.35, lw=0))
    ax.text((X(0.40e-6) + X(0.75e-6)) / 2, yt - 0.03, "visible",
            fontproperties=SANS, fontsize=W * 0.78, color=SUB, ha="center", va="top")
    # axes
    ax.plot([xa, xb], [yb, yb], color=SUB, lw=0.8)
    ax.plot([xa, xa], [yb, yt], color=SUB, lw=0.8)
    for T, col in temps:
        v = curves[T]
        ax.plot(X(lam), Y(v), color=col, lw=1.9)
        i = int(np.argmax(v))
        ax.scatter([X(lam[i])], [Y(v[i])], s=W * 1.4, color=col, zorder=5)
        dx, ha = (0.05, "left") if T < 5000 else (-0.06, "right")
        ax.text(X(lam[i]) + dx, Y(v[i]) + 0.02, f"{T} K", fontproperties=MONO,
                fontsize=W * 0.85, color=col, ha=ha, va="bottom")
    # Wien's law: locus of peaks
    Tw = np.linspace(3200, 6000, 60)
    lp = 2.898e-3 / Tw
    vp = np.array([planck(l, T) for l, T in zip(lp, Tw)])
    ax.plot(X(lp), Y(vp), color=INK, lw=0.7, ls=(0, (3, 3)))
    ax.text((xa + xb) / 2, yb - 0.28, "wavelength  λ  (µm)", fontproperties=SANS,
            fontsize=W * 0.9, color=SUB, ha="center", va="top")
    for lm in (0.5e-6, 1.0e-6, 1.5e-6, 2.0e-6):
        ax.text(X(lm), yb - 0.06, f"{lm*1e6:g}", fontproperties=MONO,
                fontsize=W * 0.8, color=SUB, ha="center", va="top")
    ax.text(xa - 0.1, yt, "intensity", fontproperties=SANS, fontsize=W * 0.9,
            color=INK, ha="right", va="bottom")


def fig_gravity(ax, box, W):
    """Kepler ellipse: Sun at a focus, two sectors swept in equal TIME (Kepler II).

    The two shaded fans span the same interval of mean anomaly (same Δt), so by
    the equal-area law they enclose exactly equal area — the fan is wide and
    short near the Sun (fast) and narrow and long far out (slow)."""
    x0, x1, y0, y1 = box
    a = min(x1 - x0, y1 - y0) * 0.42
    e = 0.6; b = a * np.sqrt(1 - e ** 2); f = a * e
    cx, cy = (x0 + x1) / 2 - f, (y0 + y1) / 2      # centre offset so Sun sits mid-box
    sx, sy = cx + f, cy                            # Sun at the right-hand focus
    # ellipse outline
    th = np.linspace(0, 2 * np.pi, 700)
    ax.plot(cx + a * np.cos(th), cy + b * np.sin(th), color=INK, lw=1.6)
    # empty focus (faint open marker)
    ax.scatter([cx - f], [cy], s=W * 1.0, facecolor="none", edgecolors=SUB, lw=0.7)
    # Sun
    ax.scatter([sx], [sy], s=W * 22, color=ACC, alpha=0.16, zorder=5)
    ax.scatter([sx], [sy], s=W * 6.0, color=ACC, zorder=6)
    ax.text(sx, sy - 0.24, "Sun", fontproperties=SANS, fontsize=W * 0.9,
            color=ACC, ha="center", va="top")

    # position from mean anomaly M via Kepler's equation  M = E − e·sinE
    def point_from_M(M):
        E = M
        for _ in range(60):
            E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        # planet coords relative to ellipse centre, then to page
        px = cx + a * (np.cos(E) - e)
        py = cy + b * np.sin(E)
        return px, py

    def sector(M0, M1, n=48):
        Ms = np.linspace(M0, M1, n)
        pts = [(sx, sy)] + [point_from_M(m) for m in Ms] + [(sx, sy)]
        ax.add_patch(mp.Polygon(pts, closed=True, facecolor=ACC,
                     edgecolor=ACC, lw=0.9, alpha=0.24))
        return point_from_M(M0), point_from_M(M1)

    dM = 0.62                                      # same Δt for both fans
    sector(-dM, dM)                                # perihelion: fast → wide fan
    sector(np.pi - dM, np.pi + dM)                 # aphelion:  slow → narrow fan
    for M in (0.0, np.pi):
        px, py = point_from_M(M)
        ax.scatter([px], [py], s=W * 1.7, color=INK, zorder=6)
    ax.text((x0 + x1) / 2, y0 + 0.12,
            "the two fans cover equal time — so their areas are equal (Kepler's 2nd law)",
            fontproperties=SANS, fontsize=W * 0.82, color=SUB, ha="center", va="bottom")


CONCEPTS = {
    "relativity": {
        "title": "THE COSMIC SPEED LIMIT", "eyebrow": "SPECIAL RELATIVITY   ·   γ = 1 / √(1 − v²/c²)",
        "fig": fig_relativity, "corner": "E = mc²",
        "caption": ["Nothing with mass reaches the speed of light. As it approaches, the factor γ climbs",
                    "without limit — moving clocks tick slow, lengths shrink, mass resists more. At 87% of c,",
                    "γ = 2: one second aboard is two outside. Energy and mass are the same thing: E = mc²."],
    },
    "blackhole": {
        "title": "ANATOMY OF A BLACK HOLE", "eyebrow": "SCHWARZSCHILD GEOMETRY   ·   rₛ = 2GM / c²",
        "fig": fig_blackhole, "corner": "rₛ = 2GM/c²",
        "caption": ["Cross the event horizon at rₛ = 2GM/c² and no path — not even light — leads back out.",
                    "At 1.5 rₛ light can circle the hole on the photon sphere; inside 3 rₛ no stable orbit",
                    "survives. For the Sun, that horizon would be just 3 km across; for Earth, 9 mm."],
    },
    "quantum": {
        "title": "ENERGY COMES IN STEPS", "eyebrow": "SCHRÖDINGER'S EQUATION   ·   Eₙ = (n + ½) ℏω",
        "fig": fig_quantum, "corner": "iℏ ∂ψ/∂t = Ĥψ",
        "caption": ["Trap a particle in a well and it can no longer hold any energy it likes — only a ladder",
                    "of levels Eₙ = (n + ½)ℏω. Each curve is a real solution ψₙ of Schrödinger's equation;",
                    "its square is where the particle is likely to be. Even the lowest rung is never at rest."],
    },
    "maxwell": {
        "title": "WHAT LIGHT IS MADE OF", "eyebrow": "MAXWELL'S EQUATIONS   ·   c = 1 / √(μ₀ε₀)",
        "fig": fig_maxwell, "corner": "c = 1/√(μ₀ε₀)",
        "caption": ["A changing electric field E makes a magnetic field B, and a changing B remakes E —",
                    "so the two roll forward together as a wave. Maxwell found its speed from the lab",
                    "constants μ₀ and ε₀ and got c. Light, radio and X-rays are all this same wave."],
    },
    "planck": {
        "title": "THE COLOUR OF HEAT", "eyebrow": "PLANCK'S LAW   ·   the birth of the quantum",
        "fig": fig_planck, "corner": "E = hν",
        "caption": ["Every warm body glows with a spectrum set only by its temperature — hotter means",
                    "bluer, by Wien's law. Classical physics predicted infinite glow; Planck fixed it in 1900",
                    "by letting energy come in packets E = hν. That one repair began quantum theory."],
    },
    "gravity": {
        "title": "HOW THE PLANETS MOVE", "eyebrow": "NEWTON & KEPLER   ·   F = G m₁m₂ / r²",
        "fig": fig_gravity, "corner": "F = G m₁m₂/r²",
        "caption": ["One inverse-square law, F = G m₁m₂/r², bends a planet's path into an ellipse with the",
                    "Sun at a focus. A line from Sun to planet sweeps equal areas in equal times, so worlds",
                    "race at perihelion and dawdle far out — Kepler's rule, explained by Newton's gravity."],
    },
}


def render(key, W, H, dpi=110):
    return render_plate(CONCEPTS[key], W, H, dpi)


if __name__ == "__main__":
    from PIL import Image
    keys = list(CONCEPTS.keys())
    ims = [to_pil(render(k, 8, 10, dpi=95)) for k in keys]
    tw = 380; ims = [i.resize((tw, int(i.height * tw / i.width))) for i in ims]
    th = ims[0].height; pad = 10
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 2 * th + 3 * pad), "#fff")
    for i, im in enumerate(ims):
        r, c = divmod(i, 3)
        sheet.paste(im, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save("/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad/physics_all.png")
    print("montage saved")
