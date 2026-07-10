"""
generate_color_fold.py — "Color & Fold" origami PoC
===================================================
Proof of concept for a printable product line that combines an origami
CREASE PATTERN with generative COLORING art placed only on the faces that
end up visible on the folded 3-D figure. Print → color → fold → 3-D toy.

Pipeline (matches the project spec):

  Fase A · Ingesta de datos geométricos
      A FoldModel defines, for one classic figure, its square size, the
      crease segments (each tagged valley / mountain / cut) and the polygons
      of the visible faces (a hand-curated "mask" — the reliable approach; a
      general 2-D→3-D visibility solver is a research problem on its own).

  Fase B · Lógica de arte generativo
      For every visible face a procedural line-art motif (rays / arcs /
      weave) is generated and CLIPPED (shapely intersection) strictly to the
      face polygon, so no ink lands on areas hidden inside the fold.

  Fase C · Renderizado y exportación
      The structural layer (fold lines, standard conventions) is composited
      over the art layer and written to a scalable, print-ready .svg
      (also a .png preview for review).

This PoC ships one model: the classic fortune-teller ("comecocos"). The
FoldModel abstraction is built so more figures (masu box, pajarita, cube…)
are just more entries — i.e. one generator, many listings.

  python generate_color_fold.py           # -> fortune_teller.svg + .png
"""
import math
import os
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
from shapely.geometry import Polygon, LineString, Point

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Print geometry (US-Letter friendly, mm) ───────────────────────────────────
PAGE_W, PAGE_H = 215.9, 279.4       # US Letter in mm
S = 180.0                           # paper square side (mm)
OX = (PAGE_W - S) / 2               # square origin (left)
OY = (PAGE_H - S) / 2               # square origin (top); SVG y grows downward

# Standard origami diagram conventions
CUT_STYLE = dict(stroke="#111111", width=1.4, dash=None)          # solid
VALLEY_STYLE = dict(stroke="#2f6fb0", width=0.8, dash="4,3")      # dashed
MOUNTAIN_STYLE = dict(stroke="#c0403a", width=0.8, dash="6,2,1,2")  # dash-dot
ART_STROKE = "#1b1b1b"
ART_WIDTH = 0.6


@dataclass
class Crease:
    p0: Tuple[float, float]
    p1: Tuple[float, float]
    kind: str            # "cut" | "valley" | "mountain"


@dataclass
class Face:
    poly: List[Tuple[float, float]]
    motif: str           # "rays" | "arcs" | "weave"
    focus: Tuple[float, float]   # focal point for the motif
    label: str = ""      # optional number/letter drawn small


@dataclass
class FoldModel:
    name: str
    creases: List[Crease] = field(default_factory=list)
    faces: List[Face] = field(default_factory=list)
    border: List[Tuple[float, float]] = field(default_factory=list)


# ── Fase A: the fortune teller ("comecocos") crease pattern ───────────────────

def fortune_teller() -> FoldModel:
    """Classic cootie-catcher. Real fold sequence → crease pattern on the sheet:
      · both diagonals              (mountain)
      · both mid-lines              (valley)
      · blintz diamond (edge mids)  (valley)
      · inner square (2nd blintz)   (valley)
    Visible colouring faces: the 8 inner triangles of the diamond (the number
    faces) + the 4 corner flaps (the 'pick-a-colour' flaps)."""
    x0, y0 = OX, OY
    c = (x0 + S / 2, y0 + S / 2)                       # centre
    # square corners
    A, B, C_, D = (x0, y0), (x0 + S, y0), (x0 + S, y0 + S), (x0, y0 + S)
    # edge midpoints (diamond vertices)
    mAB = (x0 + S / 2, y0)
    mBC = (x0 + S, y0 + S / 2)
    mCD = (x0 + S / 2, y0 + S)
    mDA = (x0, y0 + S / 2)
    # diamond edge midpoints (inner square corners)
    q1 = (x0 + 3 * S / 4, y0 + S / 4)
    q2 = (x0 + 3 * S / 4, y0 + 3 * S / 4)
    q3 = (x0 + S / 4, y0 + 3 * S / 4)
    q4 = (x0 + S / 4, y0 + S / 4)

    creases = [
        # cut border
        Crease(A, B, "cut"), Crease(B, C_, "cut"),
        Crease(C_, D, "cut"), Crease(D, A, "cut"),
        # diagonals (mountain)
        Crease(A, C_, "mountain"), Crease(B, D, "mountain"),
        # mid-lines (valley)
        Crease(mAB, mCD, "valley"), Crease(mDA, mBC, "valley"),
        # blintz diamond (valley)
        Crease(mAB, mBC, "valley"), Crease(mBC, mCD, "valley"),
        Crease(mCD, mDA, "valley"), Crease(mDA, mAB, "valley"),
        # inner square / 2nd blintz (valley)
        Crease(q1, q2, "valley"), Crease(q2, q3, "valley"),
        Crease(q3, q4, "valley"), Crease(q4, q1, "valley"),
    ]

    faces = []
    # 8 inner triangles of the diamond (centre + diamond vertex + edge midpoint)
    diamond_seq = [(mAB, q1), (q1, mBC), (mBC, q2), (q2, mCD),
                   (mCD, q3), (q3, mDA), (mDA, q4), (q4, mAB)]
    motifs = ["rays", "arcs", "weave"]
    for i, (v, e) in enumerate(diamond_seq):
        # focus each motif on the face's OWN outer tip (the diamond vertex/edge
        # point nearest the paper edge) so every visible face is a self-contained
        # little design that lines up when folded — not one shared starburst.
        tip = v if i % 2 == 0 else e
        faces.append(Face(poly=[c, v, e], motif=motifs[i % 3], focus=tip,
                          label=str(i + 1)))
    # 4 corner flaps (square corner + its two edge midpoints)
    corners = [(A, mAB, mDA), (B, mBC, mAB), (C_, mCD, mBC), (D, mDA, mCD)]
    for i, (corner, e1, e2) in enumerate(corners):
        faces.append(Face(poly=[corner, e1, e2], motif="arcs", focus=corner))

    return FoldModel("Fortune Teller", creases, faces, border=[A, B, C_, D])


# ── Fase B: generative line-art motifs, clipped to a face polygon ─────────────

def _clip(lines, poly: Polygon):
    out = []
    for ls in lines:
        inter = LineString(ls).intersection(poly)
        if inter.is_empty:
            continue
        geoms = [inter] if inter.geom_type == "LineString" else list(getattr(inter, "geoms", []))
        for g in geoms:
            if g.geom_type == "LineString" and g.length > 0.5:
                out.append(list(g.coords))
    return out


def motif_rays(face: Face, poly: Polygon, n=13):
    """Fan of straight rays from the focal point across the face."""
    fx, fy = face.focus
    minx, miny, maxx, maxy = poly.bounds
    R = math.hypot(maxx - minx, maxy - miny) * 1.6
    lines = []
    for k in range(n):
        a = math.pi * k / (n - 1) - math.pi / 2      # spread ~180°
        lines.append([(fx, fy), (fx + R * math.cos(a), fy + R * math.sin(a))])
    return _clip(lines, poly)


def motif_arcs(face: Face, poly: Polygon, n=7):
    """Concentric arcs around the focal point."""
    fx, fy = face.focus
    minx, miny, maxx, maxy = poly.bounds
    Rmax = math.hypot(maxx - minx, maxy - miny) * 1.15
    lines = []
    for k in range(1, n + 1):
        r = Rmax * k / n
        pts = [(fx + r * math.cos(t), fy + r * math.sin(t))
               for t in np.linspace(0, 2 * math.pi, 80)]
        lines.append(pts)
    return _clip(lines, poly)


def motif_weave(face: Face, poly: Polygon, step=9.0):
    """Cross-hatch weave (two families of parallel lines)."""
    minx, miny, maxx, maxy = poly.bounds
    lines = []
    d = max(maxx - minx, maxy - miny)
    for off in np.arange(-d, d, step):
        lines.append([(minx + off, miny - d), (minx + off + 2 * d, maxy + d)])   # /
        lines.append([(minx + off, maxy + d), (minx + off + 2 * d, miny - d)])   # \
    return _clip(lines, poly)


MOTIF_FN = {"rays": motif_rays, "arcs": motif_arcs, "weave": motif_weave}


def build_face_art(face: Face):
    poly = Polygon(face.poly)
    return MOTIF_FN[face.motif](face, poly)


# ── Fase C: SVG + PNG rendering ───────────────────────────────────────────────

def _poly_pts(poly):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in poly)


def render_svg(model: FoldModel, path):
    W, H = PAGE_W, PAGE_H
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')

    # clip defs + art layer
    out.append("<defs>")
    for i, f in enumerate(model.faces):
        out.append(f'<clipPath id="f{i}"><polygon points="{_poly_pts(f.poly)}"/></clipPath>')
    out.append("</defs>")

    for i, f in enumerate(model.faces):
        out.append(f'<g clip-path="url(#f{i})" stroke="{ART_STROKE}" '
                   f'stroke-width="{ART_WIDTH}" fill="none" stroke-linecap="round">')
        for seg in build_face_art(f):
            out.append(f'<polyline points="{_poly_pts(seg)}"/>')
        out.append("</g>")

    # structural crease layer
    def line(cr):
        st = {"cut": CUT_STYLE, "valley": VALLEY_STYLE, "mountain": MOUNTAIN_STYLE}[cr.kind]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        return (f'<line x1="{cr.p0[0]:.2f}" y1="{cr.p0[1]:.2f}" '
                f'x2="{cr.p1[0]:.2f}" y2="{cr.p1[1]:.2f}" '
                f'stroke="{st["stroke"]}" stroke-width="{st["width"]}"{dash}/>')
    for cr in model.creases:
        out.append(line(cr))

    # face number labels
    for f in model.faces:
        if f.label:
            cx = sum(p[0] for p in f.poly) / 3
            cy = sum(p[1] for p in f.poly) / 3
            out.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="7" '
                       f'fill="#888" text-anchor="middle" font-family="sans-serif">{f.label}</text>')

    # legend
    lx, ly = OX, OY + S + 12
    legend = [("Cut / edge", CUT_STYLE), ("Valley fold", VALLEY_STYLE),
              ("Mountain fold", MOUNTAIN_STYLE)]
    for k, (name, st) in enumerate(legend):
        yy = ly + k * 7
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        out.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+16}" y2="{yy}" '
                   f'stroke="{st["stroke"]}" stroke-width="{st["width"]}"{dash}/>')
        out.append(f'<text x="{lx+20}" y="{yy+2}" font-size="5.5" fill="#333" '
                   f'font-family="sans-serif">{name}</text>')
    out.append(f'<text x="{OX+S}" y="{OY-6}" font-size="6" fill="#999" '
               f'text-anchor="end" font-family="sans-serif">MathRelaxing · Color &amp; Fold · Fortune Teller</text>')

    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("SVG:", path)


def render_png(model: FoldModel, path, dpi=130):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly

    fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PAGE_W); ax.set_ylim(PAGE_H, 0)
    ax.set_aspect("equal"); ax.axis("off"); fig.patch.set_facecolor("white")

    for f in model.faces:
        clip = MPoly(f.poly, closed=True, transform=ax.transData)
        for seg in build_face_art(f):
            xs = [p[0] for p in seg]; ys = [p[1] for p in seg]
            ln, = ax.plot(xs, ys, color=ART_STROKE, lw=ART_WIDTH, solid_capstyle="round")
            ln.set_clip_path(clip)
    for cr in model.creases:
        st = {"cut": CUT_STYLE, "valley": VALLEY_STYLE, "mountain": MOUNTAIN_STYLE}[cr.kind]
        dash = (0, [4, 3]) if cr.kind == "valley" else ((0, [6, 2, 1, 2]) if cr.kind == "mountain" else None)
        ax.plot([cr.p0[0], cr.p1[0]], [cr.p0[1], cr.p1[1]], color=st["stroke"],
                lw=st["width"], dashes=dash[1] if dash else [], solid_capstyle="round")
    for f in model.faces:
        if f.label:
            cx = sum(p[0] for p in f.poly) / 3; cy = sum(p[1] for p in f.poly) / 3
            ax.text(cx, cy, f.label, fontsize=7, color="#888", ha="center", va="center")
    fig.savefig(path, dpi=dpi, facecolor="white"); plt.close(fig)
    print("PNG:", path)


if __name__ == "__main__":
    model = fortune_teller()
    render_svg(model, os.path.join(BASE, "fortune_teller.svg"))
    render_png(model, os.path.join(BASE, "fortune_teller_preview.png"))
