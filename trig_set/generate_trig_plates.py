"""
generate_trig_plates.py — "Trigonometry" scientific-plate set of 6, in the same
cream graph-paper / LaTeX house style as generate_equation_plates.py and the
Special Functions set. Classroom-oriented: Unit Circle, Sine & Cosine graphs,
Right-Triangle (SOHCAHTOA), Identities, Law of Sines & Cosines, Tangent &
Reciprocals.

  python generate_trig_plates.py            # 6 masters @ 12x18 300dpi -> masters/
"""
import os, sys, re
import numpy as np

# mathtext: allow \frac12 shorthand (LaTeX-valid) under matplotlib mathtext
import matplotlib.mathtext as _MT
_o = _MT.MathTextParser._parse_cached
def _pc(self, s, *a, **k):
    s = re.sub(r'\\frac(\d)(\d)', r'\\frac{\1}{\2}', s)
    s = re.sub(r'\\frac(\d)(?=[a-zA-Z\\])', r'\\frac{\1}', s)
    return _o(self, s, *a, **k)
_MT.MathTextParser._parse_cached = _pc

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, REPO)
import generate_equation_plates as EP
from generate_equation_plates import (
    _new_plate, _header, _caption, _footer_eqs, _open_axes, fig_to_image,
    INK, INK_SOFT, INK_FAINT, RUST, CREAM, DPI_PRINT, DPI_PREVIEW, _fs, SF)
import matplotlib.pyplot as plt

MAST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "masters")
os.makedirs(MAST, exist_ok=True)
TEAL = "#2f6f7e"


def _plot(fig, rect, xlim, ylim, aspect=None):
    a = _open_axes(fig, rect, 12)
    a.set_xlim(*xlim); a.set_ylim(*ylim)
    if aspect:
        a.set_aspect(aspect)
    return a


# ---------- 1. Unit Circle ----------------------------------------------------
def unit_circle(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "The Unit Circle", "FIG. 1", "angles, radians and coordinates",
            r"$(\cos\theta,\ \sin\theta)$", 12)
    a = _plot(fig, [0.10, 0.30, 0.80, 0.52], (-1.35, 1.35), (-1.35, 1.35), aspect="equal")
    th = np.linspace(0, 2 * np.pi, 400)
    a.plot(np.cos(th), np.sin(th), color=INK, lw=2.2, zorder=3)
    a.axhline(0, color=INK_FAINT, lw=0.8); a.axvline(0, color=INK_FAINT, lw=0.8)
    degs = list(range(0, 360, 30)) + [45, 135, 225, 315]
    for d in sorted(set(degs)):
        r = np.radians(d); x, y = np.cos(r), np.sin(r)
        a.plot([0, x], [0, y], color=INK_FAINT, lw=0.7, zorder=2)
        a.plot([x], [y], "o", color=TEAL, ms=5, zorder=4)
        a.text(1.16 * x, 1.16 * y, f"{d}\u00b0", fontsize=_fs(w, 0.010),
               color=INK_SOFT, ha="center", va="center")
    # radian labels for the quadrantal angles
    for d, lab in [(0, r"$0$"), (90, r"$\frac{\pi}{2}$"), (180, r"$\pi$"), (270, r"$\frac{3\pi}{2}$")]:
        r = np.radians(d)
        a.text(np.cos(r) * 0.80, np.sin(r) * 0.80, lab, fontsize=_fs(w, 0.011),
               color=RUST, ha="center", va="center")
    _caption(ax, ["Every point on the circle is (cos theta, sin theta).",
                  "Radians measure the arc length; a full turn is 2 pi."], 26, 12)
    _footer_eqs(ax, (r"$x=\cos\theta$", "abscissa"), (r"$x^2+y^2=1$", "identity"),
                (r"$y=\sin\theta$", "ordinate"), 12)
    return fig_to_image(fig)


# ---------- 2. Sine & Cosine graphs ------------------------------------------
def sine_cosine(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "Sine & Cosine", "FIG. 2", "the fundamental waves",
            r"$y=\sin x,\ \ y=\cos x$", 12)
    a = _plot(fig, [0.10, 0.34, 0.80, 0.46], (-0.3, 2 * np.pi + 0.3), (-1.5, 1.5))
    x = np.linspace(0, 2 * np.pi, 600)
    a.axhline(0, color=INK_FAINT, lw=0.8)
    a.plot(x, np.sin(x), color=RUST, lw=2.6, zorder=4, label="sin")
    a.plot(x, np.cos(x), color=TEAL, lw=2.6, zorder=4, label="cos")
    for xt, lab in [(np.pi/2, r"$\frac{\pi}{2}$"), (np.pi, r"$\pi$"),
                    (3*np.pi/2, r"$\frac{3\pi}{2}$"), (2*np.pi, r"$2\pi$")]:
        a.axvline(xt, color=INK_FAINT, lw=0.5, ls=(0, (1, 2)))
        a.text(xt, -1.72, lab, fontsize=_fs(w, 0.011), color=INK_SOFT, ha="center")
    a.text(np.pi/2, 1.18, "sin", color=RUST, fontsize=_fs(w, 0.013), ha="center", weight="bold")
    a.text(0.12, 1.18, "cos", color=TEAL, fontsize=_fs(w, 0.013), ha="left", weight="bold")
    _caption(ax, ["Both have amplitude 1 and period 2 pi; cosine leads sine by pi/2.",
                  "y = A sin(Bx + C) + D scales amplitude, period, phase and midline."], 28, 12)
    _footer_eqs(ax, (r"amplitude $=|A|$", "height"), (r"period $=\frac{2\pi}{|B|}$", "length"),
                (r"$\cos x=\sin(x+\frac{\pi}{2})$", "phase"), 12)
    return fig_to_image(fig)


# ---------- 3. Right triangle / SOHCAHTOA ------------------------------------
def right_triangle(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "Right Triangle", "FIG. 3", "SOH \u00b7 CAH \u00b7 TOA",
            r"$\sin,\cos,\tan=\frac{O}{H},\frac{A}{H},\frac{O}{A}$", 12)
    a = _plot(fig, [0.10, 0.42, 0.80, 0.40], (0, 10), (0, 5), aspect="equal")
    P = [(0.6, 0.8), (8.2, 0.8), (8.2, 4.3)]  # A(theta), B(right), C
    a.add_patch(plt.Polygon(P, closed=True, fill=True, facecolor="#eef2f2",
                            edgecolor=INK, lw=2.4, zorder=3))
    a.plot([7.5, 7.5, 8.2], [0.8, 1.5, 1.5], color=INK, lw=1.6, zorder=4)  # right-angle mark
    a.text(4.4, 0.45, "adjacent", fontsize=_fs(w, 0.011), color=INK_SOFT, ha="center", va="top")
    a.text(8.45, 2.55, "opposite", fontsize=_fs(w, 0.011), color=INK_SOFT, ha="left", va="center", rotation=90)
    a.text(4.1, 2.95, "hypotenuse", fontsize=_fs(w, 0.011), color=INK_SOFT, ha="center", va="bottom", rotation=27)
    a.text(1.35, 1.05, r"$\theta$", fontsize=_fs(w, 0.016), color=RUST, ha="center")
    _caption(ax, ["Each ratio compares two sides relative to the angle theta.",
                  "The reciprocals are cosecant, secant and cotangent."], 34, 12)
    _footer_eqs(ax, (r"$\sin\theta=\frac{O}{H}$", "SOH"), (r"$\cos\theta=\frac{A}{H}$", "CAH"),
                (r"$\tan\theta=\frac{O}{A}$", "TOA"), 12)
    return fig_to_image(fig)


# ---------- 4. Identities -----------------------------------------------------
def identities(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "Trig Identities", "FIG. 4", "the essential relations",
            r"$\sin^2\theta+\cos^2\theta=1$", 12)
    rows = [
        ("Pythagorean", r"$\sin^2\theta+\cos^2\theta=1$"),
        ("", r"$1+\tan^2\theta=\sec^2\theta$"),
        ("Reciprocal", r"$\csc\theta=\frac{1}{\sin\theta},\quad \sec\theta=\frac{1}{\cos\theta}$"),
        ("Quotient", r"$\tan\theta=\frac{\sin\theta}{\cos\theta}$"),
        ("Sum", r"$\sin(A\!+\!B)=\sin A\cos B+\cos A\sin B$"),
        ("", r"$\cos(A\!+\!B)=\cos A\cos B-\sin A\sin B$"),
        ("Double angle", r"$\sin 2\theta=2\sin\theta\cos\theta$"),
        ("", r"$\cos 2\theta=\cos^2\theta-\sin^2\theta$"),
    ]
    y = 78
    for lab, eq in rows:
        if lab:
            ax.text(9, y, SF(lab.upper()), fontsize=_fs(w, 0.011), color=RUST, ha="left", va="center")
        ax.text(30, y, eq, fontsize=_fs(w, 0.015), color=INK, ha="left", va="center")
        y -= 7.6
    _caption(ax, ["From one circle relation the whole toolkit follows.",
                  "Sum and double-angle formulas rebuild any angle from known ones."], 22, 12)
    _footer_eqs(ax, (r"$\tan=\frac{\sin}{\cos}$", "quotient"),
                (r"$\sin^2+\cos^2=1$", "pythagorean"),
                (r"$\sin 2\theta=2\sin\theta\cos\theta$", "double"), 12)
    return fig_to_image(fig)


# ---------- 5. Law of Sines & Cosines ----------------------------------------
def laws(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "Laws of Triangles", "FIG. 5", "sines and cosines for any triangle",
            r"$\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}$", 12)
    a = _plot(fig, [0.12, 0.42, 0.76, 0.40], (0, 10), (0, 5), aspect="equal")
    A, B, C = (0.8, 0.8), (9.0, 1.4), (3.4, 4.4)
    a.add_patch(plt.Polygon([A, B, C], closed=True, fill=True, facecolor="#eef2f2",
                            edgecolor=INK, lw=2.4, zorder=3))
    for p, name in [(A, "A"), (B, "B"), (C, "C")]:
        a.text(p[0], p[1] - 0.1, f" {name}", fontsize=_fs(w, 0.013), color=RUST,
               ha="center", va="top", weight="bold")
    a.text(5.0, 0.7, "c", fontsize=_fs(w, 0.012), color=INK_SOFT, ha="center", va="top")
    a.text(6.5, 3.1, "a", fontsize=_fs(w, 0.012), color=INK_SOFT, ha="left")
    a.text(1.7, 2.8, "b", fontsize=_fs(w, 0.012), color=INK_SOFT, ha="right")
    _caption(ax, ["Law of sines: sides are proportional to the sines of opposite angles.",
                  "Law of cosines generalises Pythagoras to any angle C."], 34, 12)
    _footer_eqs(ax, (r"$\frac{a}{\sin A}=\frac{b}{\sin B}$", "law of sines"),
                (r"$c^2=a^2+b^2-2ab\cos C$", "law of cosines"),
                (r"$C=90^\circ\Rightarrow$ Pythagoras", "special case"), 12)
    return fig_to_image(fig)


# ---------- 6. Tangent & reciprocals -----------------------------------------
def tangent(w, h, dpi):
    fig, ax = _new_plate(w, h, dpi)
    _header(ax, "Tangent & Asymptotes", "FIG. 6", "period pi, vertical asymptotes",
            r"$y=\tan x=\frac{\sin x}{\cos x}$", 12)
    a = _plot(fig, [0.10, 0.34, 0.80, 0.46], (-np.pi, np.pi), (-4, 4))
    a.axhline(0, color=INK_FAINT, lw=0.8)
    for k in (-1, 0, 1):
        asy = np.pi/2 + k*np.pi
        if -np.pi < asy < np.pi:
            a.axvline(asy, color=RUST, lw=1.0, ls=(0, (4, 3)))
    for lo in (-np.pi, 0, np.pi):
        xx = np.linspace(lo - np.pi/2 + 0.06, lo + np.pi/2 - 0.06, 240)
        xx = xx[(xx > -np.pi) & (xx < np.pi)]
        a.plot(xx, np.tan(xx), color=INK, lw=2.4, zorder=4)
    for xt, lab in [(-np.pi, r"$-\pi$"), (-np.pi/2, r"$-\frac{\pi}{2}$"), (np.pi/2, r"$\frac{\pi}{2}$"), (np.pi, r"$\pi$")]:
        a.text(xt, -4.5, lab, fontsize=_fs(w, 0.011), color=INK_SOFT, ha="center")
    _caption(ax, ["Tangent repeats every pi and blows up where cosine is zero.",
                  "Secant, cosecant and cotangent share these asymptotes."], 28, 12)
    _footer_eqs(ax, (r"period $=\pi$", "tangent"), (r"$\tan x=\frac{\sin x}{\cos x}$", "definition"),
                (r"$\cot x=\frac{1}{\tan x}$", "reciprocal"), 12)
    return fig_to_image(fig)


DESIGNS = [
    ("unit_circle", unit_circle), ("sine_cosine", sine_cosine), ("right_triangle", right_triangle),
    ("identities", identities), ("laws", laws), ("tangent", tangent),
]


def build(w=12.0, h=18.0, dpi=DPI_PRINT):
    for slug, fn in DESIGNS:
        print("rendering", slug)
        img = fn(w, h, dpi)
        img.save(os.path.join(MAST, f"trig_{slug}.png"))
        print("  wrote trig_%s.png" % slug, img.size)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        for slug, fn in DESIGNS:
            fn(12.0, 18.0, DPI_PREVIEW).save(os.path.join(MAST, f"trig_{slug}.png"))
            print("preview", slug)
    else:
        build()
