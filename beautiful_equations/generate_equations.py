"""
generate_equations.py — "Beautiful Equations" minimalist art-print line.
=======================================================================
Type-5 catalogue print (STANDARDS.md): fixed print-ready poster, not a book.

A departure from the density-histogram art (attractors, harmonograph, vector
field): here the subject IS the mathematics itself, set as elegant typography.
Each iconic equation is typeset in Computer Modern — the real LaTeX face — in
a museum-label layout on the brand navy, with a gold eyebrow, the equation's
name in gold serif italic and a short poetic line.

House style (minimalist navy / gold / serif):
  · background  = NAVY (deep brand navy, slightly darker than IPAD_NAVY)
  · equation    = cream, Computer Modern (mathtext.fontset = 'cm')
  · eyebrow     = gold small-caps, letter-spaced, with a short rule
  · name        = gold serif italic
  · poetic line = muted cream serif

Deliverables per equation (Type-5 convention: NO branding on the sellable file,
watermark only on the public preview):
  · {slug}_print.pdf  — VECTOR, prints razor-sharp at ANY size (hero file)
  · {slug}_print.jpg  — 7200×9000 raster (24×30 in @ 300 dpi) for JPG-only shops
  · {slug}_preview.jpg — ~2000 px, diagonal watermark

  python generate_equations.py            # full render (pdf + jpg + preview)
  python generate_equations.py --sheet     # quick low-res contact sheet only
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

# authentic LaTeX look: Computer Modern for every $...$ expression
matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"
matplotlib.rcParams["pdf.fonttype"] = 42     # embed TrueType for the plain text

BASE = os.path.dirname(os.path.abspath(__file__))

NAVY = "#0d1124"
GOLD = brand.GOLD          # #c9a24b
CREAM = brand.CREAM        # #f8f4eb
MUTED = (0.70, 0.73, 0.80)  # poetic line

W_IN, H_IN = 8.0, 10.0      # 4:5 logical canvas
PRINT_DPI = 900             # 8x10 @ 900 -> 7200x9000 (24x30 in @ 300 dpi)
PREVIEW_LONG_EDGE = 2000
WATERMARK_TEXT = "MATHRELAXING.STORE  ·  PREVIEW"
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# ── The eight equations. `size` is hand-tuned so each fills the same width band
#    on the 8-wide canvas (long/tall expressions get a smaller point size).
#    NOTE: chosen to NOT overlap with the shop's other two navy/gold LaTeX sets
#    ("Mathematical Constants Bundle": pi, e, phi, sqrt2, i, infinity, 0, 1 —
#     "Beautiful Equations Bundle": Euler's Identity, Pythagorean Theorem,
#     Schrodinger, Maxwell's First Equation, E=mc^2, Gaussian Integral, Heat
#     Equation, Bayes' Theorem). This set is the physics/calculus companion. ──
EQUATIONS = [
    dict(slug="newton_second_law",
         eyebrow="CLASSICAL MECHANICS · 1687",
         eq=r"$\vec{F} = m\vec{a}$", size=92,
         name="Newton's Second Law",
         poetic="force is nothing but\nmass, learning to move"),
    dict(slug="gravitation",
         eyebrow="CLASSICAL MECHANICS · 1687",
         eq=r"$\vec{F} = -G\,\frac{m_1 m_2}{r^{2}}\,\hat{r}$", size=52,
         name="Universal Gravitation",
         poetic="every mass reaching\nfor every other"),
    dict(slug="ideal_gas",
         eyebrow="THERMODYNAMICS",
         eq=r"$PV = nRT$", size=82,
         name="The Ideal Gas Law",
         poetic="pressure, volume, heat —\nthree ways of counting one motion"),
    dict(slug="planck_einstein",
         eyebrow="QUANTUM MECHANICS · 1900",
         eq=r"$E = h\nu$", size=100,
         name="The Planck–Einstein Relation",
         poetic="light arrives in packets,\nnever less than one"),
    dict(slug="basel",
         eyebrow="NUMBER THEORY · 1734",
         eq=r"$\sum_{n=1}^{\infty}\frac{1}{n^{2}} = \frac{\pi^{2}}{6}$", size=64,
         name="The Basel Problem",
         poetic="add every square's reciprocal\nand a circle appears"),
    dict(slug="fundamental_calculus",
         eyebrow="CALCULUS",
         eq=r"$\int_{a}^{b}\! f'(x)\,dx = f(b) - f(a)$", size=50,
         name="The Fundamental Theorem",
         poetic="the whole is nothing but\nits gathered change"),
    dict(slug="heisenberg",
         eyebrow="QUANTUM MECHANICS · 1927",
         eq=r"$\Delta x\,\Delta p \geq \frac{\hbar}{2}$", size=58,
         name="The Uncertainty Principle",
         poetic="the more precisely you look,\nthe less the world will say"),
    dict(slug="taylor_series",
         eyebrow="CALCULUS · 1715",
         eq=r"$f(x)=\sum_{n=0}^{\infty}\frac{f^{(n)}(a)}{n!}(x-a)^{n}$", size=38,
         name="The Taylor Series",
         poetic="any curve, rebuilt\nfrom a single point"),
]


def draw_poster(ax, spec):
    """Render one equation poster onto an 8x10 axes."""
    ax.set_xlim(0, 8); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_facecolor(NAVY)
    # eyebrow (gold small-caps, letter-spaced) + short rule
    eb = "   ".join(spec["eyebrow"])   # loose tracking
    ax.text(4, 8.95, eb, ha="center", va="center", fontsize=10.5,
            color=GOLD, family="sans-serif")
    ax.plot([2.9, 5.1], [8.62, 8.62], color=GOLD, lw=0.8, alpha=0.55)
    # the equation — Computer Modern, cream, centred in the upper-middle
    ax.text(4, 5.75, spec["eq"], ha="center", va="center",
            fontsize=spec["size"], color=CREAM)
    # name — gold serif italic
    ax.text(4, 3.55, spec["name"], ha="center", va="center",
            fontsize=25, color=GOLD, family="serif", style="italic")
    # poetic line — muted cream serif
    ax.text(4, 2.55, spec["poetic"], ha="center", va="center",
            fontsize=14.5, color=MUTED, family="serif", linespacing=1.55)
    # tiny closing rule
    ax.plot([3.45, 4.55], [1.25, 1.25], color=GOLD, lw=0.6, alpha=0.4)


def one_figure(spec):
    fig = plt.figure(figsize=(W_IN, H_IN))
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(NAVY)
    draw_poster(ax, spec)
    return fig


def add_watermark(img, text=WATERMARK_TEXT, opacity=42, angle=30):
    w, h = img.size
    fs = max(18, int(w * 0.030))
    font = ImageFont.truetype(FONT_PATH, fs)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(text, font=font))
    step_x, step_y = int(tw * 1.7), int(fs * 6.0)
    tile = Image.new("RGBA", (step_x, step_y), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((step_x * 0.08, step_y * 0.3), text, font=font,
                              fill=(255, 255, 255, opacity))
    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for yy in range(-tile.height, h, tile.height):
        for xx in range(-tile.width, w, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def render_all():
    for spec in EQUATIONS:
        slug = spec["slug"]
        fig = one_figure(spec)
        pdf = os.path.join(BASE, f"{slug}_print.pdf")
        jpg = os.path.join(BASE, f"{slug}_print.jpg")
        fig.savefig(pdf, facecolor=NAVY)                       # vector, any size
        fig.savefig(jpg, dpi=PRINT_DPI, facecolor=NAVY,
                    pil_kwargs={"quality": 95})                 # 7200x9000
        plt.close(fig)
        # watermarked preview from the raster
        img = Image.open(jpg)
        scale = PREVIEW_LONG_EDGE / img.height
        prev = img.resize((int(img.width * scale), PREVIEW_LONG_EDGE), Image.LANCZOS)
        add_watermark(prev).save(os.path.join(BASE, f"{slug}_preview.jpg"), quality=90)
        print(f"  {slug}: pdf + jpg({img.width}x{img.height}) + preview")


def contact_sheet(out=os.path.join(BASE, "_lineup.png"), cols=4, cell_w=520):
    """Render each full 8x10 poster to a raster, then tile them with PIL so the
    typography keeps its true proportions (subplotting mangles fixed-pt text)."""
    tiles = []
    for spec in EQUATIONS:
        fig = one_figure(spec)
        tmp = os.path.join(BASE, f"_tmp_{spec['slug']}.png")
        fig.savefig(tmp, dpi=cell_w / W_IN, facecolor=NAVY)
        plt.close(fig)
        tiles.append(Image.open(tmp).convert("RGB"))
    tw, th = tiles[0].size
    n = len(tiles); rows = (n + cols - 1) // cols
    gap, pad = 16, 16
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap,
                              rows * th + (rows + 1) * gap), "#555555")
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(out)
    for spec in EQUATIONS:
        os.remove(os.path.join(BASE, f"_tmp_{spec['slug']}.png"))
    print("Guardado:", out)


if __name__ == "__main__":
    if "--sheet" in sys.argv:
        contact_sheet()
    else:
        render_all()
