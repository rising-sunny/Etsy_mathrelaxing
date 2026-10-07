"""
generate_platonic_solids_plate.py — The Five Platonic Solids (scientific plate)
================================================================================
Dark observatory aesthetic (field_poster family): deep black ground, cream ink,
gold accents, cyan highlights. 3D solids via matplotlib mplot3d + Poly3DCollection
(Gouraud-ish face lighting from normals).

  python generate_platonic_solids_plate.py
  python generate_platonic_solids_plate.py --preview-only
"""
from __future__ import annotations

import argparse
import math
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "special_plates" / "platonic_solids"
PHI = (1.0 + math.sqrt(5.0)) / 2.0

# Dark observatory palette (aligned with wallart_set/field_poster.py)
BG = "#0a0c12"
PANEL = "#11141d"
LINE = "#2b3242"
INK = "#e9ecf5"
SUB = "#828aa0"
ACC = "#6fc9d8"       # cyan highlight
GOLD = "#e8c98a"
EDGE = "#c8cdd8"

DPI_PRINT = 300
DPI_PREVIEW = 150
SIZES = {
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
    "5x7": (10.0, 14.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
}

SANS = font_manager.FontProperties(family="DejaVu Sans")
SERIF = font_manager.FontProperties(family="DejaVu Serif")
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"
plt.rcParams["axes.unicode_minus"] = False


def _fs(fig_w: float, frac: float) -> float:
    return max(7.0, fig_w * 72 * frac)


# ── Geometry ──────────────────────────────────────────────────────────────────

def _norm(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n < 1e-12, 1.0, n)


def tetrahedron():
    v = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    faces = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
    return v, faces, dict(V=4, E=6, F=4, face="4 triangles", schlafli="{3,3}")


def cube():
    v = np.array([[x, y, z] for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)], float)
    # indices: z fastest within y within x
    faces = [
        [0, 1, 3, 2], [4, 6, 7, 5],
        [0, 4, 5, 1], [2, 3, 7, 6],
        [0, 2, 6, 4], [1, 5, 7, 3],
    ]
    return v, faces, dict(V=8, E=12, F=6, face="6 squares", schlafli="{4,3}")


def octahedron():
    v = np.array(
        [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float
    )
    faces = [
        [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
        [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5],
    ]
    return v, faces, dict(V=6, E=12, F=8, face="8 triangles", schlafli="{3,4}")


def icosahedron():
    v = np.array(
        [
            [-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0],
            [0, -1, PHI], [0, 1, PHI], [0, -1, -PHI], [0, 1, -PHI],
            [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1],
        ],
        float,
    )
    faces = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
    ]
    return v, faces, dict(V=12, E=30, F=20, face="20 triangles", schlafli="{3,5}")


def dodecahedron():
    """Dual of icosahedron → regular pentagon faces."""
    iv, iff, _ = icosahedron()
    iv = _norm(iv)
    cents = _norm(np.array([iv[list(fa)].mean(axis=0) for fa in iff]))
    faces = []
    for vi in range(len(iv)):
        adj = [fi for fi, fa in enumerate(iff) if vi in fa]
        pts = np.array([cents[fi] for fi in adj])
        c = pts.mean(axis=0)
        nrm = _norm(iv[vi])
        ref = _norm(pts[0] - c)
        b = np.cross(nrm, ref)
        ang = [math.atan2(np.dot(p - c, b), np.dot(p - c, ref)) for p in pts]
        order = [adj[k] for k in np.argsort(ang)]
        faces.append(order)
    return cents, faces, dict(V=20, E=30, F=12, face="12 pentagons", schlafli="{5,3}")


SOLIDS = [
    ("TETRAHEDRON", tetrahedron, (22, 35)),
    ("CUBE", cube, (28, 38)),
    ("OCTAHEDRON", octahedron, (30, 42)),
    ("DODECAHEDRON", dodecahedron, (24, 32)),
    ("ICOSAHEDRON", icosahedron, (26, 48)),
]


def _center_scale(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, float)
    v = v - v.mean(axis=0)
    return v / (np.linalg.norm(v, axis=1).max() + 1e-12)


def _face_polys(v: np.ndarray, faces: list) -> list[np.ndarray]:
    return [v[list(fa)] for fa in faces]


def _face_colors(polys: list[np.ndarray], light=np.array([-0.4, 0.55, 0.75])) -> list:
    """Soft cyan→gold shade from face normals."""
    light = light / np.linalg.norm(light)
    # base dark panel + gold/cyan mix
    c_lo = np.array([0.12, 0.14, 0.20])
    c_mid = np.array([0.35, 0.55, 0.62])   # ACC-ish
    c_hi = np.array([0.78, 0.70, 0.48])    # GOLD-ish
    cols = []
    for pts in polys:
        n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            cols.append((*c_lo, 0.92))
            continue
        n = n / nn
        # flip normal toward camera (+z)
        if n[2] < 0:
            n = -n
        s = float(np.clip(0.15 + 0.85 * max(0.0, np.dot(n, light)), 0, 1))
        if s < 0.5:
            t = s / 0.5
            rgb = (1 - t) * c_lo + t * c_mid
        else:
            t = (s - 0.5) / 0.5
            rgb = (1 - t) * c_mid + t * c_hi
        cols.append((*rgb, 0.94))
    return cols


def _edges_from_faces(faces: list) -> list[tuple[int, int]]:
    s = set()
    for fa in faces:
        n = len(fa)
        for i in range(n):
            a, b = fa[i], fa[(i + 1) % n]
            s.add((min(a, b), max(a, b)))
    return sorted(s)


def draw_solid_3d(ax3d, verts, faces, elev=22, azim=32):
    v = _center_scale(verts)
    polys = _face_polys(v, faces)
    colors = _face_colors(polys)
    coll = Poly3DCollection(
        polys,
        facecolors=colors,
        edgecolors=EDGE,
        linewidths=0.55,
        linestyle="solid",
        zorder=2,
    )
    coll.set_sort_zpos(0)
    ax3d.add_collection3d(coll)

    # subtle silhouette boost: slightly thicker outer-feeling edges
    edges = _edges_from_faces(faces)
    segs = [[v[a], v[b]] for a, b in edges]
    lc = Line3DCollection(segs, colors=GOLD, linewidths=0.35, alpha=0.35, zorder=3)
    ax3d.add_collection3d(lc)

    ax3d.set_xlim(-1.02, 1.02)
    ax3d.set_ylim(-1.02, 1.02)
    ax3d.set_zlim(-1.02, 1.02)
    ax3d.set_box_aspect((1, 1, 1))
    ax3d.view_init(elev=elev, azim=azim)
    ax3d.set_axis_off()
    ax3d.set_facecolor(BG)
    # kill panes
    ax3d.xaxis.pane.fill = False
    ax3d.yaxis.pane.fill = False
    ax3d.zaxis.pane.fill = False
    ax3d.xaxis.pane.set_edgecolor(BG)
    ax3d.yaxis.pane.set_edgecolor(BG)
    ax3d.zaxis.pane.set_edgecolor(BG)
    ax3d.grid(False)


# ── Plate chrome ──────────────────────────────────────────────────────────────

def _new_dark_plate(width_in: float, height_in: float, dpi: int):
    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(BG)
    # subtle vignette frame
    m = 2.8
    ax.add_patch(
        Rectangle(
            (m, m), 100 - 2 * m, 100 - 2 * m,
            fill=False, edgecolor=LINE, lw=0.8, zorder=1,
        )
    )
    # thin gold inner hairline
    ax.add_patch(
        Rectangle(
            (m + 0.55, m + 0.55), 100 - 2 * (m + 0.55), 100 - 2 * (m + 0.55),
            fill=False, edgecolor=GOLD, lw=0.35, alpha=0.35, zorder=1,
        )
    )
    return fig, ax


def compose_platonic(width_in: float, height_in: float, dpi: int) -> Image.Image:
    """Dark plate with generous margins — no text/frame collisions."""
    fig, ax = _new_dark_plate(width_in, height_in, dpi)
    fig_w = width_in

    # ── Header (safe band 88–95, clear of outer frame at ~2.8) ──
    ax.text(
        7.2, 93.8, "THE FIVE SOLIDS",
        fontsize=_fs(fig_w, 0.034), color=INK, va="center", ha="left",
        fontproperties=SERIF, fontweight="bold", zorder=5,
    )
    ax.text(
        92.8, 93.8, "FIG. 14",
        fontsize=_fs(fig_w, 0.012), color=SUB, va="center", ha="right",
        fontproperties=SANS, zorder=5,
    )
    # single elegant subtitle line (mathtext — no floating gap between words)
    ax.text(
        7.2, 89.55,
        r"$\mathrm{PLATONIC\ SOLIDS}\ \ \cdot\ \ V - E + F = 2$",
        fontsize=_fs(fig_w, 0.0125), color=GOLD, va="center", ha="left", zorder=5,
    )
    # rule with gold accent tip — clear of frame
    ax.plot([7.2, 92.8], [86.7, 86.7], color=LINE, lw=0.85, solid_capstyle="butt", zorder=5)
    ax.plot([7.2, 21.0], [86.7, 86.7], color=GOLD, lw=1.15, solid_capstyle="butt",
            zorder=6, alpha=0.9)

    # ── Cards 3+2 — labels INSIDE with padded zones ──
    # Outer frame sits at ~3% plate margin; keep cards clear of it
    left, right = 0.075, 0.925
    gap = 0.024
    n1 = 3
    col_w = (right - left - (n1 - 1) * gap) / n1
    # top row: solid + title + stats need vertical room
    top_y0, top_h = 0.515, 0.315
    row1 = [[left + i * (col_w + gap), top_y0, col_w, top_h] for i in range(3)]

    n2 = 2
    col_w2 = col_w * 1.12
    total2 = n2 * col_w2 + gap
    x0 = 0.5 - total2 / 2
    bot_y0, bot_h = 0.22, 0.275
    row2 = [[x0 + i * (col_w2 + gap), bot_y0, col_w2, bot_h] for i in range(2)]
    rects = row1 + row2

    for (name, builder, (elev, azim)), rect in zip(SOLIDS, rects):
        v, faces, meta = builder()
        card = fig.add_axes(rect, zorder=2)
        card.set_facecolor(PANEL)
        card.set_xticks([])
        card.set_yticks([])
        for sp in card.spines.values():
            sp.set_color(LINE)
            sp.set_linewidth(0.75)
        card.set_xlim(0, 1)
        card.set_ylim(0, 1)

        # title — padded from top edge of card
        card.text(
            0.5, 0.92, name,
            ha="center", va="top", color=INK, fontsize=_fs(fig_w, 0.0082),
            fontproperties=SANS, fontweight="bold", transform=card.transAxes, zorder=5,
            clip_on=True,
        )

        # 3D inset: leave clear headroom for title and foot for stats
        # title band ~ top 12%, stats band ~ bottom 18%
        r3 = [
            rect[0] + 0.08 * rect[2],
            rect[1] + 0.20 * rect[3],
            rect[2] * 0.84,
            rect[3] * 0.55,
        ]
        a3 = fig.add_axes(r3, projection="3d", zorder=3)
        draw_solid_3d(a3, v, faces, elev=elev, azim=azim)
        a3.set_facecolor(PANEL)
        try:
            a3.patch.set_facecolor(PANEL)
            a3.patch.set_alpha(1.0)
        except Exception:
            pass

        # V · E · F with Schläfli — open spacing, pure mathtext
        p, q = meta["schlafli"].strip("{}").split(",")
        math_line = (
            rf"$V = {meta['V']}\ \ ·\ \ "
            rf"E = {meta['E']}\ \ ·\ \ "
            rf"F = {meta['F']}"
            rf"\ \ ·\ \ \{{{p},{q}\}}$"
        )
        card.text(
            0.5, 0.128, math_line,
            ha="center", va="center", color=SUB, fontsize=_fs(fig_w, 0.0068),
            transform=card.transAxes, zorder=5, clip_on=True,
        )
        card.text(
            0.5, 0.048, meta["face"],
            ha="center", va="center", color=ACC, fontsize=_fs(fig_w, 0.0060),
            fontproperties=SANS, transform=card.transAxes, zorder=5, clip_on=True,
        )

    # ── Caption: refined copy, clear of cards (bottom ≥ 0.22) and footer ──
    cap_lines = [
        r"Only five convex regular polyhedra exist in three dimensions — "
        r"the solids of Plato.",
        r"Each obeys Euler’s relation  $V - E + F = 2$.  "
        r"Self-dual tetrahedron;  cube dual to octahedron;  "
        r"dodecahedron dual to icosahedron.",
        r"Coordinates computed exactly — not stock geometry, not AI illustration.",
    ]
    cap_y0 = 17.0
    for i, line in enumerate(cap_lines):
        ax.text(
            7.2, cap_y0 - i * 2.05, line,
            fontsize=_fs(fig_w, 0.0088), color=SUB, ha="left", va="top", zorder=5,
        )

    # hairline separator caption → footer
    ax.plot([7.2, 92.8], [10.3, 10.3], color=LINE, lw=0.5, alpha=0.65, zorder=4)

    # ── Footer triad — math elegant, labels clear of frame (frame ~3%) ──
    y_eq, y_lab = 8.0, 5.4
    footer = [
        (7.2, "left", r"$V - E + F = 2$", "Euler characteristic"),
        (50.0, "center", r"$\{p,\, q\}$", "Schläfli symbol"),
        (92.8, "right", r"$5\ \mathrm{in}\ \mathbb{R}^{3}$", "regular · convex"),
    ]
    for x, ha, eq, lab in footer:
        col = GOLD if ha == "right" else (INK if ha == "center" else ACC)
        ax.text(
            x, y_eq, eq,
            fontsize=_fs(fig_w, 0.0135 if ha == "center" else 0.012),
            color=col, ha=ha, va="center", zorder=5,
        )
        ax.text(
            x, y_lab, lab,
            fontsize=_fs(fig_w, 0.0072), color=SUB, ha=ha, va="center",
            fontproperties=SANS, zorder=5,
        )

    ax.text(
        50, 3.6, "MathRelaxing",
        fontsize=_fs(fig_w, 0.0072), color=LINE, ha="center", va="center",
        fontproperties=SANS, zorder=5,
    )

    return fig_to_image(fig)


def fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


WATERMARK_TEXT = "MATHRELAXING  ·  PREVIEW"


def _find_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def add_watermark(img: Image.Image, text: str = WATERMARK_TEXT, opacity: int = 38, angle: int = 30) -> Image.Image:
    """Diagonal tiled watermark for listing previews only (not on print files)."""
    w, h = img.size
    fs = max(16, int(w * 0.028))
    font = _find_font(fs)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    try:
        tw = int(probe.textlength(text, font=font))
    except Exception:
        bb = probe.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0]
    step_x, step_y = int(tw * 1.65), int(fs * 5.5)
    tile = Image.new("RGBA", (max(step_x, 1), max(step_y, 1)), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text(
        (int(step_x * 0.06), int(step_y * 0.28)),
        text,
        font=font,
        fill=(255, 255, 255, opacity),
    )
    tile = tile.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for yy in range(-tile.height, h + tile.height, tile.height):
        for xx in range(-tile.width, w + tile.width, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def save_rgb(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 92, watermark: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = add_watermark(img) if watermark else img
    out.convert("RGB").save(
        str(path), "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    tag = " +wm" if watermark else ""
    print(f"  wrote {path.name}  ({path.stat().st_size / 1024:.0f} KB){tag}")


def compose_equation_card(width_in: float = 10.0, height_in: float = 10.0, dpi: int = DPI_PREVIEW):
    fig, ax = _new_dark_plate(width_in, height_in, dpi)
    ax.text(50, 76, "PLATONIC SOLIDS", fontsize=_fs(width_in, 0.030), color=INK,
            ha="center", fontproperties=SERIF, fontweight="bold")
    ax.text(50, 56, r"$V - E + F = 2$", fontsize=_fs(width_in, 0.052), color=GOLD, ha="center")
    ax.text(50, 40, "tetra  ·  cube  ·  octa  ·  dodeca  ·  icosa",
            fontsize=_fs(width_in, 0.013), color=ACC, ha="center", fontproperties=SANS)
    ax.text(50, 28, "Math Wall Art  ·  scientific plate",
            fontsize=_fs(width_in, 0.012), color=SUB, ha="center", fontproperties=SANS)
    ax.text(50, 16, "MathRelaxing", fontsize=_fs(width_in, 0.012), color=LINE, ha="center")
    return fig_to_image(fig)


def build(preview_only: bool = False):
    prints = OUT / "prints"
    previews = OUT / "previews"
    OUT.mkdir(parents=True, exist_ok=True)
    prints.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)
    print("\n=== platonic_solids (dark) ===")

    if not preview_only:
        for name, (w, h) in SIZES.items():
            print(f"  print {name} ({w}×{h} @ {DPI_PRINT}dpi)…")
            img = compose_platonic(w, h, DPI_PRINT)
            save_rgb(img, prints / f"platonic_solids_{name}_{DPI_PRINT}dpi.jpg", DPI_PRINT, 92)

        zip_path = OUT / "Platonic_Solids_Math_Wall_Art.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "README.txt",
                """The Five Platonic Solids — Math Wall Art
MathRelaxing scientific plate (dark observatory edition)

Wireframe + shaded portraits of the five convex regular polyhedra:
  Tetrahedron · Cube · Octahedron · Dodecahedron · Icosahedron

Generated from exact coordinates (golden-ratio icosa/dodeca family).
Euler V−E+F=2 and Schläfli symbols {p,q} on the plate.

WHAT YOU GET
High-resolution JPG prints at 300 dpi:
  • 2:3  (12×18 in)
  • 3:4  (12×16 in)
  • 4:5  (16×20 in)
  • 5:7  (10×14 in)
  • ISO A4 and A3

Best on matte or semi-gloss paper. Frame not included. Personal use only.

© MathRelaxing
""",
            )
            for fn in sorted(prints.glob("*.jpg")):
                zf.write(fn, arcname=fn.name)
        mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  ZIP {zip_path.name} ({mb:.1f} MB)")

    print("  previews (watermarked for Etsy listing)…")
    # Listing previews ONLY — prints above stay clean (no watermark).
    hero = compose_platonic(10.0, 12.5, DPI_PREVIEW)
    save_rgb(hero, previews / "platonic_solids_preview_1_hero.jpg", DPI_PREVIEW, 93, watermark=True)

    detail = compose_platonic(14.0, 10.0, DPI_PREVIEW)
    dw, dh = detail.size
    crop = detail.crop((int(dw * 0.04), int(dh * 0.10), int(dw * 0.96), int(dh * 0.68)))
    side = max(crop.size)
    pad = Image.new("RGB", (side, int(side * 0.85)), (10, 12, 18))
    pad.paste(crop, ((pad.size[0] - crop.size[0]) // 2, (pad.size[1] - crop.size[1]) // 2))
    save_rgb(pad, previews / "platonic_solids_preview_2_detail.jpg", DPI_PREVIEW, 93, watermark=True)

    # included card
    fig, ax = _new_dark_plate(10, 10, DPI_PREVIEW)
    ax.text(54, 78, "included", fontsize=22, color=INK, ha="left", fontproperties=SERIF)
    lines = [
        "1 scientific-plate print",
        "The Five Platonic Solids",
        "dark observatory edition",
        "",
        "Aspect ratios:",
        "2:3 · 3:4 · 4:5 · 5:7",
        "ISO A4 · A3",
        "",
        "300 dpi JPG · ZIP",
        "code-drawn polyhedra",
        "",
        "Best on matte paper",
        "Instant download",
    ]
    y = 68
    for line in lines:
        ax.text(54, y, line, fontsize=12, color=SUB, ha="left", fontproperties=SANS)
        y -= 3.8
    base = fig_to_image(fig)
    mini = compose_platonic(5.0, 7.0, DPI_PREVIEW)
    mini = mini.resize((int(base.size[0] * 0.42), int(base.size[1] * 0.68)), Image.Resampling.LANCZOS)
    base.paste(mini, (int(base.size[0] * 0.06), int(base.size[1] * 0.15)))
    save_rgb(base, previews / "platonic_solids_preview_3_included.jpg", DPI_PREVIEW, 93, watermark=True)

    plate = compose_platonic(8.0, 10.0, DPI_PREVIEW)
    save_rgb(plate, previews / "platonic_solids_preview_4_plate.jpg", DPI_PREVIEW, 93, watermark=True)

    eq = compose_equation_card()
    save_rgb(eq, previews / "platonic_solids_preview_5_equation.jpg", DPI_PREVIEW, 93, watermark=True)
    print(f"  done → {OUT}")


def main():
    ap = argparse.ArgumentParser(description="Platonic Solids scientific plate (dark)")
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--no-latex", action="store_true", help="(compat; mathtext always on)")
    args = ap.parse_args()
    build(preview_only=args.preview_only)


if __name__ == "__main__":
    main()
