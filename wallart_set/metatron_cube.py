"""
metatron_cube.py — Metatron's Cube, ultra-precise wire + solid faces
====================================================================
Built from the Fruit of Life (13 equal circles). Every line is a chord
between real circle centres — no freehand, no AI, no clip art.

Layers (back → front):
  1. Soft filled faces of the star tetrahedron (Merkaba) + cube silhouette
  2. The 13 Fruit-of-Life circles (hairline)
  3. Full wireframe (all centre-to-centre chords)
  4. Emphasized solid edges (Merkaba + cube hexagon)
  5. Node discs on the 13 centres

Palettes: mono (ivory/charcoal), earth, cool, navy_gold
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.collections import LineCollection, PatchCollection

# ── palettes ─────────────────────────────────────────────────────────────────
PALETTES = {
    "mono": {
        "bg": "#f4efe4", "ink": "#2b2823", "wire": "#2b2823",
        "circle": "#2b2823", "face_a": "#2b2823", "face_b": "#2b2823",
        "cube": "#2b2823", "node": "#2b2823",
    },
    "earth": {
        "bg": "#f2ebdd", "ink": "#5c4336", "wire": "#6b4f3f",
        "circle": "#8a6a55", "face_a": "#a0765c", "face_b": "#7a5a48",
        "cube": "#6b4f3f", "node": "#4a3428",
    },
    "cool": {
        "bg": "#e9e9e3", "ink": "#3a454f", "wire": "#43505a",
        "circle": "#5a6a75", "face_a": "#5a7078", "face_b": "#4a5c66",
        "cube": "#43505a", "node": "#2c363e",
    },
    "navy_gold": {
        "bg": "#f7f3ea", "ink": "#12172e", "wire": "#1a2340",
        "circle": "#2a3558", "face_a": "#9a7b4f", "face_b": "#7a6238",
        "cube": "#1a2340", "node": "#9a7b4f",
    },
}

_P = dict(PALETTES["mono"])
BG = _P["bg"]


def use_palette(name: str):
    global _P, BG
    if name not in PALETTES:
        raise KeyError(name)
    _P = dict(PALETTES[name])
    BG = _P["bg"]


# ── geometry (exact, deterministic) ──────────────────────────────────────────
R = 1.0  # circle radius = centre spacing


def centres() -> np.ndarray:
    """13 Fruit-of-Life centres: origin + inner hexagon + outer hexagon."""
    pts = [(0.0, 0.0)]
    for k in range(6):
        a = k * math.pi / 3
        pts.append((R * math.cos(a), R * math.sin(a)))
    for k in range(6):
        a = k * math.pi / 3
        pts.append((2 * R * math.cos(a), 2 * R * math.sin(a)))
    return np.asarray(pts, dtype=float)


def all_chords(pts: np.ndarray) -> list:
    """Every unique centre-to-centre segment (the Metatron wireframe)."""
    segs = []
    for i, j in combinations(range(len(pts)), 2):
        segs.append([pts[i], pts[j]])
    return segs


def platonic_faces(pts: np.ndarray) -> dict:
    """
    Index map (angle k*60°):
      0     = origin
      1..6  = inner ring  (k = 0..5)
      7..12 = outer ring  (k = 0..5)

    Star tetrahedron (Merkaba) in 2D = two large equilateral triangles
    on alternating outer vertices (classic Metatron projection).

    Cube silhouette = regular hexagon on the inner ring (isometric cube face).
    Three cube face rhombi from origin to alternating inner vertices.
    """
    # outer indices: 7 + k for angle k*60°
    # Merkaba triangle A: outer 0°, 120°, 240° → k = 0, 2, 4
    tri_a = [pts[7 + 0], pts[7 + 2], pts[7 + 4]]
    # Merkaba triangle B: outer 60°, 180°, 300° → k = 1, 3, 5
    tri_b = [pts[7 + 1], pts[7 + 3], pts[7 + 5]]

    # Inner hexagon (cube silhouette in isometric view)
    hex_inner = [pts[1 + k] for k in range(6)]

    # Three rhombi radiating from centre through opposite inner vertices
    # (reads as the three visible faces of a cube)
    rhombi = []
    for k in range(3):
        a, b = 1 + k, 1 + ((k + 1) % 6)
        c, d = 1 + ((k + 3) % 6), 1 + ((k + 4) % 6)
        # rhombus: centre is not a vertex of outer cube faces in iso —
        # use: inner[k], outer[k], inner[k+1], origin? Better classic:
        # rhombus of cube: H_k, O_k, H_{k+1}, O? 
        # Clean isometric cube faces from Metatron:
        # Face k: H_k — H_{k+1} — O? Actually:
        # Three parallelograms: (0, H_k, mid, H_{k+2}) 
        # Standard: (H0, H1, O1? no)
        # Use: (center, H_k, O_k, H_{k-1}) — wait center not cube vertex.
        #
        # Isometric cube from hexagon H0..H5: three rhombi
        #   R0 = H0, H1, H2, origin-ish no: R0 = H5, H0, H1, and centroid?
        # Classic iso cube on hexagon vertices V0..V5:
        #   face top: V0, V1, V2, center-of-hex = origin when H is regular about 0
        #   Actually with origin = center of hex:
        #   Rhombus 1: H0, H1, origin, H5  — not right
        # Standard three faces for cube projected as hexagon with internal Y:
        #   Face A: origin, H0, H1, H2? No that's not rhombus.
        #
        # Vertices of cube silhouette hexagon: H0..H5
        # Internal three rhombi share the center ONLY if we draw from center —
        # In pure isometric cube, center is a vertex (front corner).
        # So: faces = (C, H0, H1), wait triangles?
        # Isometric cube: three parallelograms
        #   P0 = C, H0, H1, H?  with C as a cube vertex:
        #   P0 = C, H0, M01, H5 where M is not...
        # If C is the nearest cube vertex and H0..H5 are the silhouette:
        #   Face0 = C, H0, H1? No 3 points.
        # Correct: Face0 = C, H0, (H0+H1-C)=H0+H1 since C=0 → H0, H1, H0+H1
        # H0+H1 is outer point at angle 30° — but our outer points are at 0,60,...
        # H_k + H_{k+1} = 2R*(cos((k+0.5)*60), ...) at radius R*√3 ≈ 1.732R
        # Our outer is at 2R — different construction.
        #
        # Simpler elegant solid faces that ARE exact on Metatron points:
        # - Two Merkaba triangles (already)
        # - Central hexagon fill (cube outline)
        # - Six small equilateral triangles around origin (inner ring)
        # - Optional: star tetrahedron "depth" as filled hexagram intersection
        pass

    # Six small equilateral triangles around the centre (inner flower core)
    petals = []
    for k in range(6):
        petals.append([pts[0], pts[1 + k], pts[1 + ((k + 1) % 6)]])

    # Cube face rhombi using exact Metatron vertices:
    # Isometric cube with near vertex = origin:
    # H_k + H_{k+1} lands between outers — use outer points at k that equal H_k*2
    # Outer[k] = 2*H_k, so rhombus (0, H_k, O_k, H_{k+?}):
    # Rhombus (0, H0, O0, H5): vectors H0 and H5 — |H0|=|H5|=R, angle 60° → rhombus yes
    for k in range(6):
        hk = pts[1 + k]
        ok = pts[7 + k]
        hm = pts[1 + ((k + 5) % 6)]  # previous
        # only every other for three visible faces of a cube:
        if k % 2 == 0:
            rhombi.append([pts[0], hk, ok, hm])

    # Hexagram intersection (central hexagon of the star) for depth
    # Intersection of tri_a and tri_b is a regular hexagon
    star_hex = _star_intersection_hex(tri_a, tri_b)

    return {
        "tri_a": tri_a,
        "tri_b": tri_b,
        "hex_inner": hex_inner,
        "rhombi": rhombi,
        "petals": petals,
        "star_hex": star_hex,
        "edge_merkaba": [tri_a, tri_b],
        "edge_hex": hex_inner,
    }


def _line_intersect(p1, p2, p3, p4):
    """Intersection of segments p1-p2 and p3-p4 (as infinite lines)."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])


def _star_intersection_hex(tri_a, tri_b):
    """Regular hexagon at the intersection of two equilateral triangles."""
    # Each edge of A intersects two edges of B → 6 vertices, ordered by angle
    verts = []
    for i in range(3):
        a0, a1 = tri_a[i], tri_a[(i + 1) % 3]
        for j in range(3):
            b0, b1 = tri_b[j], tri_b[(j + 1) % 3]
            p = _line_intersect(a0, a1, b0, b1)
            if p is None:
                continue
            # keep only intersections inside both edges (parameter 0..1-ish)
            if _on_seg(a0, a1, p) and _on_seg(b0, b1, p):
                verts.append(p)
    if len(verts) < 6:
        # fallback: scale inner hex from average radius
        return None
    # unique + sort by angle
    arr = np.array(verts)
    # dedupe
    uniq = []
    for v in arr:
        if not any(np.linalg.norm(v - u) < 1e-6 for u in uniq):
            uniq.append(v)
    uniq = np.array(uniq)
    ang = np.arctan2(uniq[:, 1], uniq[:, 0])
    order = np.argsort(ang)
    return uniq[order]


def _on_seg(a, b, p, eps=1e-6):
    a, b, p = np.asarray(a), np.asarray(b), np.asarray(p)
    d = np.linalg.norm(b - a)
    if d < eps:
        return np.linalg.norm(p - a) < eps
    t = np.dot(p - a, b - a) / (d * d)
    if t < -eps or t > 1 + eps:
        return False
    proj = a + t * (b - a)
    return np.linalg.norm(p - proj) < 1e-5


# ── draw ─────────────────────────────────────────────────────────────────────
def draw_metatron(ax, lw_scale: float = 1.0, style: str = "atelier"):
    """
    Draw Metatron's Cube on axes.
    style:
      atelier — soft solid faces + full wire (default, premium)
      wire    — wire + circles only
      solid   — stronger face fills, slightly quieter wire
    Returns xs, ys for framing.
    """
    pts = centres()
    faces = platonic_faces(pts)
    segs = all_chords(pts)
    p = _P

    face_a_alpha = 0.10 if style != "solid" else 0.16
    face_b_alpha = 0.08 if style != "solid" else 0.13
    cube_alpha = 0.05 if style != "solid" else 0.09
    rhomb_alpha = 0.06 if style != "solid" else 0.10
    wire_alpha = 0.55 if style != "solid" else 0.40
    circle_alpha = 0.35

    # 1) solid faces (back)
    if style != "wire":
        ax.add_patch(mp.Polygon(faces["tri_a"], closed=True,
                                facecolor=p["face_a"], edgecolor="none",
                                alpha=face_a_alpha, zorder=1))
        ax.add_patch(mp.Polygon(faces["tri_b"], closed=True,
                                facecolor=p["face_b"], edgecolor="none",
                                alpha=face_b_alpha, zorder=1))
        ax.add_patch(mp.Polygon(faces["hex_inner"], closed=True,
                                facecolor=p["cube"], edgecolor="none",
                                alpha=cube_alpha, zorder=2))
        for rh in faces["rhombi"]:
            ax.add_patch(mp.Polygon(rh, closed=True,
                                    facecolor=p["cube"], edgecolor="none",
                                    alpha=rhomb_alpha, zorder=2))
        if faces["star_hex"] is not None:
            ax.add_patch(mp.Polygon(faces["star_hex"], closed=True,
                                    facecolor=p["face_a"], edgecolor="none",
                                    alpha=0.07, zorder=3))

    # 2) 13 circles
    for cx, cy in pts:
        ax.add_patch(mp.Circle((cx, cy), R, fill=False,
                               edgecolor=p["circle"],
                               lw=0.55 * lw_scale, alpha=circle_alpha, zorder=4))

    # 3) full wireframe
    ax.add_collection(LineCollection(
        segs, colors=p["wire"], linewidths=0.45 * lw_scale,
        alpha=wire_alpha, zorder=5))

    # 4) emphasized structure edges
    def poly_edges(poly, lw, alpha=0.95, z=6):
        edges = [[poly[i], poly[(i + 1) % len(poly)]] for i in range(len(poly))]
        ax.add_collection(LineCollection(
            edges, colors=p["ink"], linewidths=lw * lw_scale,
            alpha=alpha, zorder=z))

    poly_edges(faces["tri_a"], 1.35, 0.92, 7)
    poly_edges(faces["tri_b"], 1.35, 0.92, 7)
    poly_edges(faces["hex_inner"], 1.15, 0.88, 7)
    for rh in faces["rhombi"]:
        poly_edges(rh, 0.85, 0.75, 6)

    # outer containing circle (optional atelier ring) — through outer centres + R
    outer_r = 2 * R + R  # 3R — same as Flower of Life boundary
    ax.add_patch(mp.Circle((0, 0), outer_r, fill=False,
                           edgecolor=p["ink"], lw=1.1 * lw_scale,
                           alpha=0.55, zorder=8))

    # 5) nodes
    node_r = 0.045 * R
    for cx, cy in pts:
        ax.add_patch(mp.Circle((cx, cy), node_r * (1.0 if (cx, cy) != (0.0, 0.0) else 1.35),
                               facecolor=p["node"], edgecolor="none",
                               alpha=0.95, zorder=9))

    xs = pts[:, 0]
    ys = pts[:, 1]
    # include outer circle in bounds
    return np.r_[xs, -outer_r, outer_r], np.r_[ys, -outer_r, outer_r]


def render_image(px_w: int, px_h: int, palette: str = "mono",
                 style: str = "atelier", pad: float = 1.14) -> "Image":
    """PIL RGB image framed to pixel size."""
    from PIL import Image
    import io

    use_palette(palette)
    dpi = 100.0
    fig = plt.figure(figsize=(px_w / dpi, px_h / dpi), dpi=dpi)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_aspect("equal")

    lw_scale = px_h / 600.0
    xs, ys = draw_metatron(ax, lw_scale=lw_scale, style=style)
    xs, ys = np.asarray(xs), np.asarray(ys)
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx = max((x1 - x0) / 2, 1e-6) * pad
    hy = max((y1 - y0) / 2, 1e-6) * pad
    a = px_w / px_h
    HH = max(hy, hx / a)
    WW = HH * a
    ax.set_xlim(cx - WW, cx + WW)
    ax.set_ylim(cy - HH, cy + HH)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


if __name__ == "__main__":
    # quick local smoke: three style/palette thumbs
    from pathlib import Path
    out = Path(__file__).resolve().parent / "out" / "metatron" / "_smoke"
    out.mkdir(parents=True, exist_ok=True)
    for pal in ("mono", "navy_gold", "cool", "earth"):
        for st in ("atelier", "wire", "solid"):
            im = render_image(900, 1125, palette=pal, style=st)
            im.save(out / f"smoke_{pal}_{st}.jpg", quality=92)
            print("wrote", pal, st)
    print("OK", out)
