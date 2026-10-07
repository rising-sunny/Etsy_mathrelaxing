"""Full-wrap hardcover cover for Lulu (same SKU/dims as math_gallery's book:
0850X0850FCPRECW080CW444MXX). Wrap 1386x738 pt = 19.25x10.25 in; spine 0.5 in;
wrap margin 0.875 in. Page count here is 45 (vs. book 1's 88) -- spine width
would technically be a touch narrower at that count, but Lulu quotes the
actual spine from the real interior page count at order time; this reuses
book 1's spine allowance which comfortably fits the title text either way."""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, "..", "math_gallery")
sys.path.insert(0, MG)
import mini_book as MB  # noqa: E402
sys.path.insert(0, HERE)
import plate_library as PL  # noqa: E402

OUT = os.path.join(HERE, "fullbook")
DPI = 300
W_IN, H_IN = 1386 / 72, 738 / 72
W_PX, H_PX = round(W_IN * DPI), round(H_IN * DPI)
DARK, GOLD, ACC = MB.DARK, MB.GOLD, MB.ACC
CINZEL, CINZEL_R, RALEWAY, RALEWAY_I = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")

WRAP = 63 / 1386
SPINE = 36 / 1386
TRIMW = 612 / 1386
xb0, xb1 = WRAP, WRAP + TRIMW
xs0, xs1 = xb1, xb1 + SPINE
xf0, xf1 = xs1, xs1 + TRIMW
FRONT_C = (xf0 + xf1) / 2
BACK_C = (xb0 + xb1) / 2


def build():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI); fig.patch.set_facecolor(DARK)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(DARK); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # faint tesseract-edge motif behind FRONT (echoes the "higher dimensions"
    # thread that runs through the book)
    rng = np.random.default_rng(4)
    for _ in range(40):
        a = rng.uniform(0, 2 * np.pi); r = rng.uniform(0.05, 0.22)
        x0 = FRONT_C + r * np.cos(a); y0 = 0.58 + 0.18 * r * np.sin(a)
        ax.plot([FRONT_C, x0], [0.58, y0], color=GOLD, lw=0.4, alpha=0.10)

    # ---- FRONT ----
    ax.plot([FRONT_C - 0.15, FRONT_C + 0.15], [0.44, 0.44], color=GOLD, lw=1.5)
    ax.text(FRONT_C, 0.39, "THE SHAPE", fontproperties=CINZEL, fontsize=33, color="#f0e9da", ha="center")
    ax.text(FRONT_C, 0.32, "OF AN IDEA", fontproperties=CINZEL, fontsize=33, color=GOLD, ha="center")
    ax.plot([FRONT_C - 0.15, FRONT_C + 0.15], [0.27, 0.27], color=GOLD, lw=1.5)
    ax.text(FRONT_C, 0.237, "A Gallery of Great Equations & Concepts",
            fontproperties=RALEWAY_I, fontsize=12.5, color="#b9b3a4", ha="center")

    # ---- SPINE ----
    ax.text((xs0 + xs1) / 2, 0.62, "THE SHAPE OF AN IDEA", fontproperties=CINZEL_R,
            fontsize=13, color="#f0e9da", ha="center", va="center", rotation=90)
    ax.text((xs0 + xs1) / 2, 0.20, "MathRelaxing", fontproperties=RALEWAY_I,
            fontsize=10, color=GOLD, ha="center", va="center", rotation=90)

    # ---- BACK ----
    ax.text(BACK_C, 0.60, "MathRelaxing", fontproperties=CINZEL_R, fontsize=13, color="#b9b3a4", ha="center")
    blurb = ("Not every mathematical object is a curve you can plot.\n"
             "Some are pure ideas: a proof, a paradox, a shape that only\n"
             "closes up properly in a dimension you cannot see.\n\n"
             "Eighteen plates, five chapters — foundations, waves, higher\n"
             "dimensions, chaos, and the paradoxes of infinity — each\n"
             "generated directly from its own mathematics.")
    ax.text(BACK_C, 0.52, blurb, fontproperties=RALEWAY, fontsize=12.5, color="#cfc9bb",
            ha="center", va="top", linespacing=1.8)
    ax.plot([BACK_C - 0.14, BACK_C + 0.14], [0.20, 0.20], color=GOLD, lw=1.0, alpha=0.7)

    base = fig_to_pil(fig)

    logo = Image.open(LOGO).convert("RGBA"); logo = logo.crop((0, 0, logo.width, int(logo.height * 0.76)))
    def place(cx_frac, top_frac, w_frac, alpha):
        w = int(base.width * w_frac); h = int(w * logo.height / logo.width)
        lg = logo.resize((w, h), Image.Resampling.LANCZOS)
        a = lg.split()[3].point(lambda p: int(p * alpha))
        base.paste(lg, (int(base.width * cx_frac) - w // 2, int(base.height * top_frac)), a)
    place(FRONT_C, 0.815, 0.07, 0.9)

    thumbs = [PL.g_mobius, PL.g_golden, PL.g_koch]
    tw = int(base.width * 0.085); gap = int(base.width * 0.012)
    total = 3 * tw + 2 * gap; x0 = int(base.width * BACK_C) - total // 2; y0 = int(base.height * 0.17)
    for i, fn in enumerate(thumbs):
        th = fn().resize((tw, tw), Image.Resampling.LANCZOS)
        base.paste(th, (x0 + i * (tw + gap), y0))

    png = os.path.join(OUT, "cover_wrap.png"); base.save(png)
    pdf = os.path.join(OUT, "cover_wrap.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert([png], layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    print("cover_wrap.png", base.size, "| pdf", os.path.getsize(pdf) // 1024, "KB")
    return pdf


def fig_to_pil(fig):
    import io
    buf = io.BytesIO(); fig.savefig(buf, dpi=DPI, facecolor=DARK, format="png"); plt.close(fig)
    buf.seek(0); return Image.open(buf).convert("RGB")


if __name__ == "__main__":
    build()
