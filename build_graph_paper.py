# /// script
# dependencies = ["pymupdf==1.23.26", "matplotlib"]
# ///
"""
build_graph_paper.py — "The STEM Graph Paper Bundle" (ultra low-cost printable)
================================================================================
Genera un set imprimible de papel cuadriculado en 8 estilos, en los DOS tamanos
mas usados (US Letter 8.5x11 y A4), listo para imprimir en casa. Incluye los
estilos de baja competencia / alta demanda detectados via la API de Etsy:
isometrico (solo ~73 listings, top con 1.092 vistas) y hexagonal, ademas de los
clasicos (cuadricula 5mm y 1/4", puntos, triangular, Cornell, rayado).

Salida en graph_paper/:
  GraphPaper_US_Letter.pdf   (8 paginas)
  GraphPaper_A4.pdf          (8 paginas)
  GraphPaper_Bundle.zip      (deliverable: ambos PDFs + guia)
  previews/*.jpg             (imagenes para el listing)

Papel cuadriculado = debe verse limpio de borde a borde; la marca queda como
una firma diminuta y tenue en el margen inferior, no una franja.
"""
import os
import math
import zipfile

import fitz

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "graph_paper")
PREV = os.path.join(OUT, "previews")

MM = 72.0 / 25.4          # points per millimetre
INCH = 72.0

# page sizes in points (w, h) portrait
SIZES = {
    "US_Letter": (8.5 * INCH, 11.0 * INCH),
    "A4": (210 * MM, 297 * MM),
}

MARGIN = 0.45 * INCH

# grid colours (soft blue-grey like real engineering paper)
MINOR = (0.62, 0.69, 0.78)
MAJOR = (0.44, 0.53, 0.66)
SIG = (0.70, 0.74, 0.80)   # tiny signature text


def _content_rect(W, H):
    return fitz.Rect(MARGIN, MARGIN, W - MARGIN, H - MARGIN)


def _signature(page, W, style_name):
    page.insert_textbox(fitz.Rect(MARGIN, page.rect.height - MARGIN + 4,
                                  W - MARGIN, page.rect.height - MARGIN + 18),
                        f"{style_name}   ·   mathrelaxing.store",
                        fontsize=6.5, fontname="helv", color=SIG, align=0)


# ── grid renderers (all clip to the content rect) ────────────────────────────
def sq(page, W, H, step, major_every=5, label="Square Grid"):
    r = _content_rect(W, H)
    n = 0
    x = r.x0
    while x <= r.x1 + 0.1:
        col = MAJOR if (n % major_every == 0) else MINOR
        wln = 0.7 if (n % major_every == 0) else 0.35
        page.draw_line(fitz.Point(x, r.y0), fitz.Point(x, r.y1), color=col, width=wln)
        x += step; n += 1
    n = 0
    y = r.y0
    while y <= r.y1 + 0.1:
        col = MAJOR if (n % major_every == 0) else MINOR
        wln = 0.7 if (n % major_every == 0) else 0.35
        page.draw_line(fitz.Point(r.x0, y), fitz.Point(r.x1, y), color=col, width=wln)
        y += step; n += 1
    _signature(page, W, label)


def dots(page, W, H, step, label="Dot Grid"):
    r = _content_rect(W, H)
    y = r.y0
    while y <= r.y1 + 0.1:
        x = r.x0
        while x <= r.x1 + 0.1:
            page.draw_circle(fitz.Point(x, y), 0.9, color=MAJOR, fill=MAJOR)
            x += step
        y += step
    _signature(page, W, label)


def _clip_seg(x0, y0, x1, y1, r):
    """Liang-Barsky clip of a segment to rect r; returns clipped endpoints or None."""
    dx, dy = x1 - x0, y1 - y0
    p = [-dx, dx, -dy, dy]
    q = [x0 - r.x0, r.x1 - x0, y0 - r.y0, r.y1 - y0]
    u0, u1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                u0 = max(u0, t)
            else:
                u1 = min(u1, t)
    if u0 > u1:
        return None
    return (x0 + u0 * dx, y0 + u0 * dy, x0 + u1 * dx, y0 + u1 * dy)


def _family(page, r, angle_deg, step, color, width):
    """Draw a family of parallel lines at angle_deg spaced `step` apart,
    covering rect r (via clipping a long line swept across the diagonal)."""
    ang = math.radians(angle_deg)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx                      # normal direction to offset along
    diag = math.hypot(r.width, r.height)
    cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
    k = int(diag / step) + 2
    for i in range(-k, k + 1):
        ox, oy = cx + nx * i * step, cy + ny * i * step
        seg = _clip_seg(ox - dx * diag, oy - dy * diag, ox + dx * diag, oy + dy * diag, r)
        if seg:
            page.draw_line(fitz.Point(seg[0], seg[1]), fitz.Point(seg[2], seg[3]),
                           color=color, width=width)


def isometric(page, W, H, step, label="Isometric"):
    r = _content_rect(W, H)
    _family(page, r, 90, step, MINOR, 0.4)     # vertical
    _family(page, r, 30, step, MINOR, 0.4)     # +30
    _family(page, r, -30, step, MINOR, 0.4)    # -30
    _signature(page, W, label)


def triangular(page, W, H, step, label="Triangular"):
    r = _content_rect(W, H)
    _family(page, r, 0, step * math.sin(math.radians(60)), MINOR, 0.4)   # horizontal rows
    _family(page, r, 60, step, MINOR, 0.4)
    _family(page, r, -60, step, MINOR, 0.4)
    _signature(page, W, label)


def hexagons(page, W, H, size, label="Hexagonal"):
    """Flat-top hex tiling of the content rect."""
    r = _content_rect(W, H)
    w = size * 2                 # hex width (flat-top)
    h = math.sqrt(3) * size      # hex height
    horiz = 1.5 * size           # horizontal distance between columns
    col = 0
    x = r.x0
    while x - size <= r.x1:
        yoff = 0 if col % 2 == 0 else h / 2
        y = r.y0 + yoff
        while y - h / 2 <= r.y1:
            _hex(page, x, y, size, r)
            y += h
        x += horiz; col += 1
    _signature(page, W, label)


def _hex(page, cx, cy, size, r):
    pts = []
    for k in range(6):
        a = math.radians(60 * k)
        pts.append((cx + size * math.cos(a), cy + size * math.sin(a)))
    for k in range(6):
        x0, y0 = pts[k]
        x1, y1 = pts[(k + 1) % 6]
        seg = _clip_seg(x0, y0, x1, y1, r)
        if seg:
            page.draw_line(fitz.Point(seg[0], seg[1]), fitz.Point(seg[2], seg[3]),
                           color=MINOR, width=0.4)


def cornell(page, W, H, label="Cornell Notes"):
    r = _content_rect(W, H)
    cue_x = r.x0 + 2.4 * INCH
    summ_y = r.y1 - 1.9 * INCH
    # outer + main divisions
    page.draw_rect(r, color=MAJOR, width=0.9)
    page.draw_line(fitz.Point(r.x0, summ_y), fitz.Point(r.x1, summ_y), color=MAJOR, width=0.9)
    page.draw_line(fitz.Point(cue_x, r.y0), fitz.Point(cue_x, summ_y), color=MAJOR, width=0.9)
    # faint rule lines in the notes area
    y = r.y0 + 26
    while y < summ_y - 6:
        page.draw_line(fitz.Point(cue_x + 8, y), fitz.Point(r.x1 - 8, y), color=MINOR, width=0.3)
        y += 26
    page.insert_textbox(fitz.Rect(r.x0 + 6, summ_y + 6, r.x1, summ_y + 22),
                        "Summary", fontsize=9, fontname="times-italic", color=MAJOR)
    _signature(page, W, label)


def ruled(page, W, H, step=8 * MM, label="College Ruled"):
    r = _content_rect(W, H)
    margin_x = r.x0 + 0.9 * INCH
    page.draw_line(fitz.Point(margin_x, r.y0), fitz.Point(margin_x, r.y1),
                   color=(0.85, 0.55, 0.55), width=0.7)   # red margin, classic
    y = r.y0 + step
    while y <= r.y1:
        page.draw_line(fitz.Point(r.x0, y), fitz.Point(r.x1, y), color=MINOR, width=0.4)
        y += step
    _signature(page, W, label)


# ── the 8 styles, in draw order ──────────────────────────────────────────────
def render_all(doc, W, H):
    def pg():
        return doc.new_page(width=W, height=H)
    sq(pg(), W, H, 5 * MM, 5, "Square Grid — 5 mm")
    sq(pg(), W, H, 0.25 * INCH, 4, "Square Grid — 1/4 inch")
    dots(pg(), W, H, 5 * MM, "Dot Grid — 5 mm")
    isometric(pg(), W, H, 6 * MM, "Isometric")
    triangular(pg(), W, H, 8 * MM, "Triangular")
    hexagons(pg(), W, H, 7 * MM, "Hexagonal")
    cornell(pg(), W, H, "Cornell Notes")
    ruled(pg(), W, H, 8 * MM, "College Ruled")


def build_pdfs():
    os.makedirs(OUT, exist_ok=True)
    paths = {}
    for name, (W, H) in SIZES.items():
        doc = fitz.open()
        render_all(doc, W, H)
        out = os.path.join(OUT, f"GraphPaper_{name}.pdf")
        doc.save(out, deflate=True, garbage=4)
        doc.close()
        paths[name] = out
        print(f"  {name}: {out} ({os.path.getsize(out)//1024} KB)")
    return paths


def build_zip(paths):
    zpath = os.path.join(OUT, "GraphPaper_Bundle.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name, pth in paths.items():
            z.write(pth, os.path.basename(pth))
        z.writestr("README.txt",
                   "The STEM Graph Paper Bundle — MathRelaxing\n"
                   "==========================================\n\n"
                   "8 grid styles, in US Letter (8.5x11 in) and A4:\n"
                   "  Square 5mm · Square 1/4in · Dot grid · Isometric ·\n"
                   "  Triangular · Hexagonal · Cornell notes · College ruled\n\n"
                   "TO PRINT: open the PDF for your paper size and print the page(s)\n"
                   "you need at 100% / 'Actual size' (do NOT 'fit to page', or the\n"
                   "grid spacing will scale). Black & white is fine.\n\n"
                   "For personal & classroom use. Print as many copies as you like.\n"
                   "Please don't resell or redistribute the files themselves.\n"
                   "(c) MathRelaxing · mathrelaxing.store\n")
    print(f"Zip: {zpath} ({os.path.getsize(zpath)//1024} KB)")
    return zpath


# ── previews ─────────────────────────────────────────────────────────────────
def build_previews():
    os.makedirs(PREV, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    letter = os.path.join(OUT, "GraphPaper_US_Letter.pdf")
    doc = fitz.open(letter)
    # crop each page to a clean square swatch of the grid for the preview tiles
    tile_paths = []
    labels = ["Square 5mm", "Square 1/4\"", "Dot grid", "Isometric",
              "Triangular", "Hexagonal", "Cornell", "Ruled"]
    for i in range(8):
        pix = doc[i].get_pixmap(dpi=150)
        pth = os.path.join(PREV, f"_p{i}.png")
        pix.save(pth)
        tile_paths.append(pth)
    doc.close()

    # hero: brand navy, title, 8 grid tiles in a grid
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(brand.IPAD_NAVY); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    ax.text(5, 7.45, "THE STEM GRAPH PAPER BUNDLE", ha="center", va="center",
            fontsize=25, color=brand.CREAM, **brand.SERIF)
    ax.text(5, 6.95, "8 grid styles · US Letter + A4 · print at home",
            ha="center", va="center", fontsize=14, color=brand.GOLD, **brand.SANS)
    cols, rows = 4, 2
    tw, th = 2.05, 2.55
    x0, y0 = 0.85, 3.6
    gapx = (10 - 2 * x0 - cols * 0) / cols
    for i, (tp, lab) in enumerate(zip(tile_paths, labels)):
        c, r = i % cols, i // cols
        cx = x0 + c * (2.15) + 1.0
        cy = 4.6 - r * 2.75
        img = mpimg.imread(tp)
        # crop the top-left grid area (skip margins) to a square
        h, w = img.shape[:2]
        crop = img[int(h*0.06):int(h*0.06)+int(w*0.5), int(w*0.06):int(w*0.06)+int(w*0.5)]
        ax.imshow(crop, extent=[cx-0.9, cx+0.9, cy-0.9, cy+0.9], zorder=3)
        ax.add_patch(plt.Rectangle((cx-0.9, cy-0.9), 1.8, 1.8, fill=False,
                                   edgecolor=brand.GOLD, lw=1, zorder=4))
        ax.text(cx, cy-1.06, lab, ha="center", va="top", fontsize=9,
                color=brand.CREAM, **brand.SANS)
    brand.ipad_logo(ax, 5, 0.28, 0.85)
    fig.savefig(os.path.join(PREV, "graph_preview_1_hero.jpg"), dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

    # individual full-page previews for isometric + hexagonal (the hero styles)
    for idx, key in [(3, "isometric"), (5, "hexagonal"), (0, "square"), (6, "cornell")]:
        fig, ax = plt.subplots(figsize=(8, 10))
        fig.patch.set_facecolor(brand.IPAD_NAVY); ax.axis("off")
        ax.set_xlim(0, 8); ax.set_ylim(0, 10)
        ax.imshow(mpimg.imread(tile_paths[idx]), extent=[1, 7, 1.2, 9], zorder=3)
        ax.add_patch(plt.Rectangle((1, 1.2), 6, 7.8, fill=False, edgecolor=brand.GOLD, lw=1.5, zorder=4))
        ax.text(4, 9.5, labels[idx].upper(), ha="center", va="center",
                fontsize=20, color=brand.CREAM, **brand.SERIF)
        fig.savefig(os.path.join(PREV, f"graph_preview_{key}.jpg"), dpi=170, facecolor=brand.IPAD_NAVY)
        plt.close(fig)

    for tp in tile_paths:
        os.remove(tp)
    print(f"Previews en {PREV}/")


def main():
    paths = build_pdfs()
    build_zip(paths)
    build_previews()
    print("Listo. Actualiza products_catalog.py y sube el borrador.")


if __name__ == "__main__":
    main()
