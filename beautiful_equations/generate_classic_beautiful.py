"""
generate_classic_beautiful.py
=============================
The original "Beautiful Equations Bundle" / listing
"Set of 8 Minimalist Math Posters – Navy Gold LaTeX Typography"
(listing_id=4534831774) — Euler, Pythagoras, Schrödinger, Maxwell,
E=mc², Gaussian integral, heat equation, Bayes.

Separate from generate_equations.py (Physics & Calculus companion set).

  python generate_classic_beautiful.py            # navy/gold (default product)
  python generate_classic_beautiful.py --light    # cream paper + dark ink
  python generate_classic_beautiful.py --light --zip-only  # pack existing light prints

Outputs (in this folder / light/ subfolder):
  {slug}_print.pdf / .jpg / _preview.jpg
  Beautiful_Equations_Bundle.zip          (dark)
  Beautiful_Equations_Light_Bundle.zip    (--light)
"""
from __future__ import annotations

import os
import sys
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"
matplotlib.rcParams["pdf.fonttype"] = 42

BASE = os.path.dirname(os.path.abspath(__file__))
LIGHT = "--light" in sys.argv
ZIP_ONLY = "--zip-only" in sys.argv
SHEET = "--sheet" in sys.argv

NAVY = "#0d1124"
GOLD = brand.GOLD
CREAM = brand.CREAM
INK = "#1a1a1a"
MUTED_DARK = (0.70, 0.73, 0.80)
MUTED_LIGHT = (0.35, 0.36, 0.40)

if LIGHT:
    BG = CREAM
    EQ_C = NAVY
    EYEBROW_C = "#8a6a28"
    NAME_C = "#1a1a1a"
    POETIC_C = MUTED_LIGHT
    OUT_DIR = os.path.join(BASE, "light")
    ZIP_NAME = "Beautiful_Equations_Light_Bundle.zip"
    FOLDER = "Beautiful_Equations_Light"
else:
    BG = NAVY
    EQ_C = CREAM
    EYEBROW_C = GOLD
    NAME_C = GOLD
    POETIC_C = MUTED_DARK
    OUT_DIR = BASE
    ZIP_NAME = "Beautiful_Equations_Bundle.zip"
    FOLDER = "Beautiful_Equations"

W_IN, H_IN = 8.0, 10.0
PRINT_DPI = 600  # 8x10 @ 600 → 4800x6000 (16x20 @ 300 dpi); solid for customer swap
PREVIEW_LONG_EDGE = 2000
WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"

# Classic Beautiful Equations Bundle (no overlap with Physics/Calculus set)
EQUATIONS = [
    dict(
        slug="euler_identity",
        eyebrow="NUMBER THEORY · 1748",
        eq=r"$e^{i\pi} + 1 = 0$",
        size=78,
        name="Euler's Identity",
        poetic="five constants,\none perfect sentence",
    ),
    dict(
        slug="pythagorean",
        eyebrow="GEOMETRY · ~500 BCE",
        eq=r"$a^{2} + b^{2} = c^{2}$",
        size=72,
        name="The Pythagorean Theorem",
        poetic="the square on the long side\nis the sum of the other two",
    ),
    dict(
        slug="schrodinger",
        eyebrow="QUANTUM MECHANICS · 1926",
        eq=r"$i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi$",
        size=42,
        name="The Schrödinger Equation",
        poetic="the wave that is a particle\nlearning where it may be",
    ),
    dict(
        slug="maxwell_gauss",
        eyebrow="ELECTROMAGNETISM · 1861",
        eq=r"$\nabla\cdot\mathbf{E} = \frac{\rho}{\varepsilon_{0}}$",
        size=48,
        name="Gauss's Law (Maxwell)",
        poetic="charge tells the field\nhow to open",
    ),
    dict(
        slug="mass_energy",
        eyebrow="SPECIAL RELATIVITY · 1905",
        eq=r"$E = mc^{2}$",
        size=100,
        name="Mass–Energy Equivalence",
        poetic="matter is energy\nwaiting to be counted",
    ),
    dict(
        slug="gaussian_integral",
        eyebrow="ANALYSIS",
        eq=r"$\int_{-\infty}^{\infty} e^{-x^{2}}\,dx = \sqrt{\pi}$",
        size=40,
        name="The Gaussian Integral",
        poetic="the bell curve's area\nis a circle in disguise",
    ),
    dict(
        slug="heat_equation",
        eyebrow="THERMODYNAMICS · 1822",
        eq=r"$\frac{\partial u}{\partial t} = \alpha\nabla^{2}u$",
        size=48,
        name="The Heat Equation",
        poetic="warmth spreads\nlike a smoothed thought",
    ),
    dict(
        slug="bayes",
        eyebrow="PROBABILITY · 1763",
        eq=r"$P(A\mid B) = \frac{P(B\mid A)\,P(A)}{P(B)}$",
        size=40,
        name="Bayes' Theorem",
        poetic="belief, revised\nby what you just learned",
    ),
]

READ_ME_LIGHT = """BEAUTIFUL EQUATIONS — Light / cream edition
MathRelaxing · mathrelaxing.store

Customer swap for order (cream paper + dark ink).
Same eight equations as the Navy Gold listing, light ground.

WHAT'S INSIDE
-------------
PDF_vector_any_size/   8 vector PDFs — print sharp at any size.
JPG_print/             8 JPG files, 4:5 ratio, print-ready.

THE EQUATIONS
-------------
  Euler's Identity · Pythagorean Theorem · Schrödinger Equation
  Gauss's Law (Maxwell) · Mass–Energy Equivalence
  Gaussian Integral · Heat Equation · Bayes' Theorem

PRINTING TIPS
-------------
· Proportion 4:5 — frames in 8×10, 16×20, 24×30.
· Matte or satin paper recommended.

© MathRelaxing. Personal use only. Not for redistribution or resale.
"""

READ_ME_DARK = """BEAUTIFUL EQUATIONS — Navy Gold set of 8
MathRelaxing · mathrelaxing.store

Eight mathematical art prints in Computer Modern on deep navy with gold accents.

WHAT'S INSIDE
-------------
PDF_vector_any_size/   8 vector PDFs — print sharp at any size.
JPG_print/             8 JPG files, 4:5 ratio, print-ready.

© MathRelaxing. Personal use only. Not for redistribution or resale.
"""


def _font_path():
    for p in (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if os.path.isfile(p):
            return p
    return None


FONT_PATH = _font_path()


def draw_poster(ax, spec):
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_facecolor(BG)
    eb = "   ".join(spec["eyebrow"])
    ax.text(4, 8.95, eb, ha="center", va="center", fontsize=10.5, color=EYEBROW_C, family="sans-serif")
    ax.plot([2.9, 5.1], [8.62, 8.62], color=EYEBROW_C, lw=0.8, alpha=0.55)
    ax.text(4, 5.75, spec["eq"], ha="center", va="center", fontsize=spec["size"], color=EQ_C)
    ax.text(4, 3.55, spec["name"], ha="center", va="center", fontsize=25, color=NAME_C, family="serif", style="italic")
    ax.text(4, 2.55, spec["poetic"], ha="center", va="center", fontsize=14.5, color=POETIC_C, family="serif", linespacing=1.55)
    ax.plot([3.45, 4.55], [1.25, 1.25], color=EYEBROW_C, lw=0.6, alpha=0.4)


def one_figure(spec):
    fig = plt.figure(figsize=(W_IN, H_IN))
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(BG)
    draw_poster(ax, spec)
    return fig


def add_watermark(img, text=WATERMARK_TEXT, opacity=40, angle=30):
    if not FONT_PATH:
        return img
    w, h = img.size
    fs = max(18, int(w * 0.030))
    font = ImageFont.truetype(FONT_PATH, fs)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(text, font=font))
    step_x, step_y = int(tw * 1.7), int(fs * 6.0)
    tile = Image.new("RGBA", (step_x, step_y), (0, 0, 0, 0))
    fill = (40, 40, 40, opacity) if LIGHT else (255, 255, 255, opacity)
    ImageDraw.Draw(tile).text((step_x * 0.08, step_y * 0.3), text, font=font, fill=fill)
    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for yy in range(-tile.height, h, tile.height):
        for xx in range(-tile.width, w, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def render_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    theme = "light" if LIGHT else "navy"
    print(f"Rendering Beautiful Equations classic set ({theme}) → {OUT_DIR}")
    for spec in EQUATIONS:
        slug = spec["slug"]
        fig = one_figure(spec)
        pdf = os.path.join(OUT_DIR, f"{slug}_print.pdf")
        jpg = os.path.join(OUT_DIR, f"{slug}_print.jpg")
        fig.savefig(pdf, facecolor=BG)
        fig.savefig(jpg, dpi=PRINT_DPI, facecolor=BG, pil_kwargs={"quality": 95})
        plt.close(fig)
        img = Image.open(jpg)
        scale = PREVIEW_LONG_EDGE / img.height
        prev = img.resize((int(img.width * scale), PREVIEW_LONG_EDGE), Image.LANCZOS)
        add_watermark(prev).save(os.path.join(OUT_DIR, f"{slug}_preview.jpg"), quality=90)
        print(f"  {slug}: {img.width}x{img.height}")


def build_zip():
    out = os.path.join(BASE, ZIP_NAME)
    readme = READ_ME_LIGHT if LIGHT else READ_ME_DARK
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for spec in EQUATIONS:
            s = spec["slug"]
            pdf = os.path.join(OUT_DIR, f"{s}_print.pdf")
            jpg = os.path.join(OUT_DIR, f"{s}_print.jpg")
            if not os.path.isfile(pdf) or not os.path.isfile(jpg):
                raise FileNotFoundError(f"missing print for {s} in {OUT_DIR}")
            z.write(pdf, f"{FOLDER}/PDF_vector_any_size/{s}.pdf")
            z.write(jpg, f"{FOLDER}/JPG_print/{s}.jpg")
        z.writestr(f"{FOLDER}/READ_ME.txt", readme)
    mb = os.path.getsize(out) / 1e6
    print(f"ZIP: {out}  ({mb:.1f} MB)")
    return out


def pack_customer_folder():
    """Copy deliverables into order_swaps/4125528649/."""
    import shutil

    dest = os.path.join(os.path.dirname(BASE), "order_swaps", "4125528649")
    os.makedirs(dest, exist_ok=True)
    zip_src = os.path.join(BASE, ZIP_NAME)
    if os.path.isfile(zip_src):
        shutil.copy2(zip_src, os.path.join(dest, ZIP_NAME))
        print("Copied ZIP →", dest)
    return dest


if __name__ == "__main__":
    if not ZIP_ONLY:
        render_all()
    build_zip()
    if LIGHT:
        pack_customer_folder()
