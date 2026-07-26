"""Full-wrap hardcover cover for Lulu (0850X0850FCPRECW080CW444MXX, 88 pp).
Wrap 1386x738 pt = 19.25x10.25 in; spine 0.5 in; wrap margin 0.875 in."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
import img2pdf
import mini_book as MB
import plate_library as PL

OUT = os.path.join(MB.SCR, "fullbook")
DPI = 300
W_IN, H_IN = 1386 / 72, 738 / 72          # 19.25 x 10.25
W_PX, H_PX = round(W_IN * DPI), round(H_IN * DPI)   # 5775 x 3075
DARK, GOLD, CMAP = MB.DARK, MB.GOLD, MB.CMAP
CINZEL, CINZEL_R, RALEWAY, RALEWAY_I = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")

# panel fractions (of total wrap)
WRAP = 63 / 1386          # 0.875 in
SPINE = 36 / 1386         # 0.5 in
TRIMW = 612 / 1386
xb0, xb1 = WRAP, WRAP + TRIMW                    # back panel
xs0, xs1 = xb1, xb1 + SPINE                       # spine
xf0, xf1 = xs1, xs1 + TRIMW                       # front panel
yb, yt = 63 / 738, 1 - 63 / 738                   # trim vertical band
FRONT_C = (xf0 + xf1) / 2
BACK_C = (xb0 + xb1) / 2


def harmono(seed_shift=0.0):
    t = np.linspace(0, 60, 26000)
    x = np.exp(-0.005 * t) * (np.sin(2.02 * t) + np.sin(2.99 * t + 1.1 + seed_shift))
    y = np.exp(-0.005 * t) * (np.sin(3.01 * t) + np.sin(1.99 * t + 0.6))
    return x / np.abs(x).max(), y / np.abs(y).max()


def build():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI); fig.patch.set_facecolor(DARK)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(DARK); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # faint motif behind FRONT
    hx, hy = harmono()
    fx = FRONT_C + 0.145 * hx; fy = 0.60 + 0.27 * hy
    pts = np.array([fx, fy]).T.reshape(-1, 1, 2); segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=CMAP, linewidth=0.5, alpha=0.30); lc.set_array(np.linspace(0, 1, len(segs))); ax.add_collection(lc)

    # ---- FRONT ---- (title raised; a small logo sits at the foot)
    ax.plot([FRONT_C - 0.15, FRONT_C + 0.15], [0.44, 0.44], color=GOLD, lw=1.5)
    ax.text(FRONT_C, 0.39, "THE MATHEMATICS", fontproperties=CINZEL, fontsize=33, color="#f0e9da", ha="center")
    ax.text(FRONT_C, 0.32, "OF BEAUTY", fontproperties=CINZEL, fontsize=33, color=GOLD, ha="center")
    ax.plot([FRONT_C - 0.15, FRONT_C + 0.15], [0.27, 0.27], color=GOLD, lw=1.5)
    ax.text(FRONT_C, 0.237, "A Visual Gallery of Equations, Curves and Chaos",
            fontproperties=RALEWAY_I, fontsize=12.5, color="#b9b3a4", ha="center")

    # ---- SPINE ---- (rotated)
    ax.text((xs0 + xs1) / 2, 0.62, "THE MATHEMATICS OF BEAUTY", fontproperties=CINZEL_R,
            fontsize=13, color="#f0e9da", ha="center", va="center", rotation=90)
    ax.text((xs0 + xs1) / 2, 0.20, "MathRelaxing", fontproperties=RALEWAY_I,
            fontsize=10, color=GOLD, ha="center", va="center", rotation=90)

    # ---- BACK ---- (thumbnails sit at the top; text below)
    ax.text(BACK_C, 0.60, "MathRelaxing", fontproperties=CINZEL_R, fontsize=13, color="#b9b3a4", ha="center")
    blurb = ("Some equations do more than compute — they draw.\n"
             "This gallery pairs each beautiful form with the\n"
             "mathematics that makes it: strange attractors and\n"
             "fractals, curves and waves, the tilings of symmetry.\n\n"
             "Thirty-eight plates, each generated directly from its\n"
             "own formula — nothing traced, nothing drawn by hand.")
    ax.text(BACK_C, 0.52, blurb, fontproperties=RALEWAY, fontsize=12.5, color="#cfc9bb",
            ha="center", va="top", linespacing=1.8)
    ax.plot([BACK_C - 0.14, BACK_C + 0.14], [0.20, 0.20], color=GOLD, lw=1.0, alpha=0.7)

    base = fig_to_pil(fig)

    # logos (front emblem + small back)
    logo = Image.open(LOGO).convert("RGBA"); logo = logo.crop((0, 0, logo.width, int(logo.height * 0.76)))
    def place(cx_frac, top_frac, w_frac, alpha):
        w = int(base.width * w_frac); h = int(w * logo.height / logo.width)
        lg = logo.resize((w, h), Image.Resampling.LANCZOS)
        a = lg.split()[3].point(lambda p: int(p * alpha))
        base.paste(lg, (int(base.width * cx_frac) - w // 2, int(base.height * top_frac)), a)
    place(FRONT_C, 0.815, 0.07, 0.9)   # small logo at the foot of the front

    # small plate thumbnails on the back (a taste of the interior)
    thumbs = [PL.g_julia, PL.g_rose, PL.g_penrose]
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
