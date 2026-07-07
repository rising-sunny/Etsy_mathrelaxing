"""Generate the Lulu wraparound cover (1255x810 pt = 17.43x11.25") for
Sacred Geometry & Topology, plus a square web cover image of the front."""
import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon
from matplotlib.backends.backend_pdf import PdfPages
from gen_sacred_math_book import best_candidate

# Slate/graphite-blue aesthetic, distinct from Hyperbolic's indigo and Flora's emerald
BG = "#141A26"; GOLD = "#C8A96E"; CREAM = "#EDE6D6"; FAINT = "#2A3346"; BAND = "#000000"
LOGO_PATH = os.path.join(_ROOT, "assets", "img", "logo.png")
_LOGO = mpimg.imread(LOGO_PATH)


def place_logo(fig, rect):
    ax = fig.add_axes(rect); ax.axis("off"); ax.imshow(_LOGO, aspect="equal")


def draw_mesh_motif(ax, idx, color):
    """Clean gold line-art render of one mesh (no numbers/fills, just outlines)."""
    result = best_candidate(idx)
    if result is None:
        return
    _, face_data, _, _ = result
    for fd in face_data:
        poly = Polygon(fd['pts_2d'], closed=True, facecolor="none",
                       edgecolor=color, linewidth=0.9)
        ax.add_patch(poly)
    all_pts = [fd['pts_2d'] for fd in face_data]
    import numpy as np
    all_pts = np.vstack(all_pts)
    min_x, max_x = all_pts[:, 0].min(), all_pts[:, 0].max()
    min_y, max_y = all_pts[:, 1].min(), all_pts[:, 1].max()
    margin = max(max_x - min_x, max_y - min_y) * 0.08
    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)
    ax.set_aspect("equal"); ax.axis("off")


def build_cover():
    W, H = 1255 / 72.0, 810 / 72.0
    fig = plt.figure(figsize=(W, H))
    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    fb = 9 / 1255.0; front_l = 634 / 1255.0; front_r = 1246 / 1255.0
    spine_l = 621 / 1255.0; spine_r = 634 / 1255.0

    # FRONT motif: a clean Torus Topology
    axm = fig.add_axes([front_l + 0.055, 0.40, (front_r - front_l) - 0.11, 0.35])
    draw_mesh_motif(axm, 0, GOLD)

    fig.text((front_l + front_r) / 2, 0.86, "SACRED GEOMETRY", ha="center", va="center",
             fontsize=30, family="serif", color=CREAM, weight="light")
    fig.text((front_l + front_r) / 2, 0.805, "& TOPOLOGY", ha="center", va="center",
             fontsize=30, family="serif", color=GOLD, weight="light")
    fig.text((front_l + front_r) / 2, 0.36, "A 3D Color-by-Numbers Journey", ha="center",
             fontsize=14, family="serif", style="italic", color=CREAM)
    fig.text((front_l + front_r) / 2, 0.255, "50 geometric 3D models", ha="center",
             fontsize=11, family="serif", color=GOLD)

    band_h = 0.155
    bg.add_patch(plt.Rectangle((front_l, 0), 1 - front_l, band_h, color=BAND, zorder=5))
    fc = (front_l + front_r) / 2
    place_logo(fig, [fc - 0.085, 0.018, 0.17, band_h * 0.74])

    fig.text((spine_l + spine_r) / 2, 0.5, "SACRED GEOMETRY & TOPOLOGY   ·   MATHRELAXING",
             rotation=90, ha="center", va="center", fontsize=8.5, family="serif", color=CREAM)

    back_c = (fb + spine_l) / 2
    axb = fig.add_axes([0.06, 0.46, 0.22, 0.30])
    draw_mesh_motif(axb, 42, FAINT)  # a Geometric Gem, faint accent

    blurb = ("Fifty 3D mathematical surfaces -- tori, Mobius bands, helicoids,\n"
             "golden spirals and faceted gems -- projected into flat, numbered\n"
             "regions. Match the numbers to the palette and watch the illusion\n"
             "of volume emerge as you colour.\n\n"
             "Each model is rendered from its real parametric equations, not\n"
             "traced by hand: a genuine 3D object, flattened for you to fill in.\n\n"
             "Perfect-bound - 8.5 x 11 in - matte cover - printed on demand.")
    fig.text(0.06, 0.40, blurb, ha="left", va="top", fontsize=9.5, family="serif",
             color=CREAM, linespacing=1.5)
    fig.text(back_c, 0.07, "mathrelaxing.store", ha="center", fontsize=9, family="serif", color=GOLD)

    out_dir = os.path.join(_ROOT, "output", "sacred-math-coloring-book")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "cover.pdf")
    with PdfPages(out) as pdf:
        pdf.savefig(fig)
    plt.close(fig); print("cover ->", out)


def build_web_cover():
    fig = plt.figure(figsize=(10, 12.5))
    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    axm = fig.add_axes([0.13, 0.38, 0.74, 0.40])
    draw_mesh_motif(axm, 0, GOLD)

    fig.text(0.5, 0.88, "SACRED GEOMETRY", ha="center", fontsize=36, family="serif",
             color=CREAM, weight="light")
    fig.text(0.5, 0.825, "& TOPOLOGY", ha="center", fontsize=36, family="serif",
             color=GOLD, weight="light")
    fig.text(0.5, 0.31, "A 3D Color-by-Numbers Journey", ha="center", fontsize=15,
             family="serif", style="italic", color=CREAM)
    fig.text(0.5, 0.225, "50 geometric 3D models", ha="center", fontsize=11,
             family="serif", color=GOLD)

    band_h = 0.135
    bg.add_patch(plt.Rectangle((0, 0), 1, band_h, color=BAND, zorder=5))
    place_logo(fig, [0.385, 0.02, 0.23, band_h * 0.74])

    out = os.path.join(_ROOT, "output", "sacred_math_cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=BG, dpi=100); plt.close(fig); print("web cover ->", out)


if __name__ == "__main__":
    build_cover()
    build_web_cover()
