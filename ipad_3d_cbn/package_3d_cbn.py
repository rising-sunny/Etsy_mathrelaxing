"""
package_3d_cbn.py — deliverable ZIP + instructions PDF + listing previews for
the Interactive 3D Color-by-Number app. Run after build_3d_cbn.py and the
screenshot capture (screenshots live in _caps/).
"""
import os
import glob
import zipfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.image as mpimg

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

HERE = os.path.dirname(os.path.abspath(__file__))
CAPS = os.path.join(HERE, "_caps")
PREV = os.path.join(HERE, "previews")
APP = os.path.join(HERE, "MathRelaxing_3D_CBN.html")
os.makedirs(PREV, exist_ok=True)

FIG_ORDER = ["Tetrahedron", "Cube", "Octahedron", "Dodecahedron",
             "Icosahedron", "GeodesicSphere", "Torus", "Gem"]


def cap(name):
    m = glob.glob(os.path.join(CAPS, f"*{name}*.png"))
    return mpimg.imread(m[0]) if m else None


# ── instructions PDF ──────────────────────────────────────────────────────────

def build_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    pdf = os.path.join(HERE, "How_to_Use_3D_CBN.pdf")
    DARK, GOLD = HexColor("#1A1D24"), HexColor("#C8A951")
    doc = SimpleDocTemplate(pdf, pagesize=letter, leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch)
    S = getSampleStyleSheet()
    ts = ParagraphStyle('T', parent=S['Title'], fontSize=26, textColor=DARK, fontName='Helvetica-Bold', alignment=TA_CENTER)
    ss = ParagraphStyle('S', parent=S['Normal'], fontSize=13, textColor=HexColor("#666"), alignment=TA_CENTER, spaceAfter=18)
    hs = ParagraphStyle('H', parent=S['Heading2'], fontSize=15, textColor=DARK, fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=7)
    bs = ParagraphStyle('B', parent=S['Normal'], fontSize=11, textColor=HexColor("#333"), leading=15, leftIndent=18, spaceAfter=5)
    ft = ParagraphStyle('F', parent=S['Normal'], fontSize=9, textColor=HexColor("#999"), alignment=TA_CENTER, spaceBefore=26)
    e = [Spacer(1, .25*inch), Paragraph("3D Color by Number", ts),
         Paragraph("Interactive · runs in your iPad's Safari browser", ss),
         HRFlowable(width="80%", thickness=1, color=GOLD, spaceAfter=14)]
    for h, items in [
        ("What this is", [
            "A single interactive app with <b>8 low-poly 3D figures</b> (the five Platonic solids, a geodesic sphere, a torus and a faceted gem).",
            "Each face is numbered. Colour the numbers and the figure lights up as a shaded 3-D object.",
            "It runs 100% offline in Safari — no app to install."]),
        ("Getting started on iPad", [
            "<b>1.</b> Download the ZIP from Etsy to your iPad (Files app).",
            "<b>2.</b> Tap the ZIP to unzip it.",
            "<b>3.</b> Tap <b>MathRelaxing_3D_CBN.html</b>. If needed, Share &gt; Open in Safari."]),
        ("How to play", [
            "<b>Rotate:</b> drag with one finger.  <b>Zoom:</b> pinch.  <b>Reset view:</b> button top-right.",
            "<b>Pick a colour</b> from the palette bar (each is numbered 1–8).",
            "<b>Tap a face</b> showing that number — it fills and the number disappears.",
            "Switch figures from the menu at the top. Progress saves automatically per figure.",
            "<b>Undo</b> / <b>Clear</b> are top-right."]),
        ("Tips", [
            "Rotate as you go — numbers only show on faces pointing toward you.",
            "Works on any modern browser (iPhone, Android, Mac, PC) too."]),
    ]:
        e.append(Paragraph(h, hs))
        for it in items:
            e.append(Paragraph(it, bs))
    e += [Spacer(1, .2*inch),
          HRFlowable(width="60%", thickness=.5, color=HexColor("#CCC"), spaceBefore=8, spaceAfter=8),
          Paragraph("MathRelaxing — For personal use only. Not for redistribution or resale.", ft),
          Paragraph("mathrelaxing.store", ft)]
    doc.build(e)
    print("PDF:", pdf)
    return pdf


def build_zip(pdf):
    out = os.path.join(HERE, "MathRelaxing_3D_CBN.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(APP, "MathRelaxing_3D_CBN.html")
        z.write(pdf, "How_to_Use_3D_CBN.pdf")
    print(f"ZIP: {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


def _screen(ax, img, cx, cy, w, h):
    sx, sy, sw, sh = brand.ipad_frame(ax, cx, cy, w, h)
    ax.imshow(img, extent=(sx, sx + sw, sy, sy + sh), zorder=3, aspect="auto")


def preview_hero():
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.25, "3D Color by Number", ha="center", fontsize=52, color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.55, "Rotate · Zoom · Colour — right in Safari", ha="center", fontsize=26, color=brand.GOLD, **brand.SERIF)
    _screen(ax, cap("GeodesicSphere"), 5, 4.9, 6.2, 6.2)
    brand.footer_band(ax, 10, 1.5)
    fig.savefig(os.path.join(PREV, "prev_1_hero.jpg"), dpi=100); plt.close(fig)
    print("preview 1")


def preview_how():
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.3, "How It Works", ha="center", fontsize=52, color=brand.CREAM, **brand.SERIF_BOLD)
    _screen(ax, cap("numbered"), 7.4, 4.6, 4.2, 4.2)
    steps = [(7.2, "1. Pick a colour", "each palette colour is numbered 1–8"),
             (5.2, "2. Rotate to a face", "spin the figure to any numbered face"),
             (3.2, "3. Tap to fill", "the colour lands and the 3-D form appears")]
    for y, t, d in steps:
        ax.text(0.7, y, t, ha="left", fontsize=25, color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(0.7, y - 0.45, d, ha="left", fontsize=15, color=brand.CREAM, **brand.SERIF)
    brand.footer_band(ax, 10, 1.5)
    fig.savefig(os.path.join(PREV, "prev_2_how.jpg"), dpi=100); plt.close(fig)
    print("preview 2")


def preview_included():
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.4, "8 Interactive 3D Figures", ha="center", fontsize=38, color=brand.CREAM, **brand.SERIF_BOLD)
    labels = ["Tetrahedron", "Cube", "Octahedron", "Dodecahedron",
              "Icosahedron", "Geodesic Sphere", "Torus", "Gem"]
    cols = 4
    xs = [1.55, 3.75, 6.25, 8.45]
    rows_y = [6.7, 3.9]
    for i, (k, lb) in enumerate(zip(FIG_ORDER, labels)):
        r, c = divmod(i, cols)
        cx, cy = xs[c], rows_y[r]
        ax.imshow(cap(k), extent=(cx - 0.92, cx + 0.92, cy - 0.92, cy + 0.92), zorder=3, aspect="auto")
        ax.text(cx, cy - 1.12, lb, ha="center", fontsize=10.5, color=brand.GOLD, **brand.SERIF)
    ax.text(5, 1.78, "Works offline in Safari  ·  Saves progress  ·  Instructions PDF included",
            ha="center", fontsize=13, color=brand.CREAM, **brand.SERIF)
    brand.footer_band(ax, 10, 1.5)
    fig.savefig(os.path.join(PREV, "prev_3_included.jpg"), dpi=100); plt.close(fig)
    print("preview 3")


if __name__ == "__main__":
    pdf = build_pdf()
    build_zip(pdf)
    preview_hero()
    preview_how()
    preview_included()
