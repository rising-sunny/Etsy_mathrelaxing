"""
poincare_disc.py — Poincaré disk hyperbolic tiling (ultra-precise line art)
===========================================================================
Regular tiling {p,q} of the hyperbolic plane, rendered in the Poincaré unit
disk via recursive geodesic reflection. Every edge is a true hyperbolic
straight line (circular arc orthogonal to the boundary, or a diameter).

Default {3,7} — triangular tiling with 7 triangles at each vertex
(the classic Escher Circle Limit family). Also supports {7,3}, {5,4}, …

Palette: mono ivory/charcoal (same language as Metatron / Flower of Life).
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.collections import LineCollection

# ── palettes ─────────────────────────────────────────────────────────────────
PALETTES = {
    "mono": {
        "bg": "#f4efe4", "ink": "#2b2823", "wire": "#2b2823",
        "boundary": "#2b2823", "face_a": "#2b2823", "face_b": "#2b2823",
    },
    "earth": {
        "bg": "#f2ebdd", "ink": "#5c4336", "wire": "#6b4f3f",
        "boundary": "#4a3428", "face_a": "#a0765c", "face_b": "#7a5a48",
    },
    "cool": {
        "bg": "#e9e9e3", "ink": "#3a454f", "wire": "#43505a",
        "boundary": "#2c363e", "face_a": "#5a7078", "face_b": "#4a5c66",
    },
    "navy_gold": {
        "bg": "#f7f3ea", "ink": "#12172e", "wire": "#1a2340",
        "boundary": "#12172e", "face_a": "#9a7b4f", "face_b": "#1a2340",
    },
}

_P = dict(PALETTES["mono"])
BG = _P["bg"]


def use_palette(name: str):
    global _P, BG
    _P = dict(PALETTES[name])
    BG = _P["bg"]


# ── complex / geodesic helpers ───────────────────────────────────────────────
def _as_c(z) -> complex:
    if isinstance(z, complex):
        return z
    return complex(float(z[0]), float(z[1]))


def central_vertex_radius(p: int, q: int) -> float:
    """Euclidean radius (Poincaré) of vertices of the central regular p-gon in {p,q}."""
    cv = math.cos(math.pi / q)
    sp = math.sin(math.pi / p)
    if cv <= sp + 1e-15:
        raise ValueError(f"{{p,q}}={{{p},{q}}} is not hyperbolic")
    return math.sqrt((cv - sp) / (cv + sp))


def central_polygon(p: int, q: int) -> list[complex]:
    r = central_vertex_radius(p, q)
    # flat-top orientation looks balanced in a portrait frame
    rot = -math.pi / p
    return [r * cmath_exp(2 * math.pi * k / p + rot) for k in range(p)]


def cmath_exp(theta: float) -> complex:
    return complex(math.cos(theta), math.sin(theta))


def geodesic_circle(a: complex, b: complex):
    """
    Circle through a,b orthogonal to the unit circle.
    Returns (center, radius) or None if the geodesic is a diameter.
    """
    A = np.array([[a.real, a.imag], [b.real, b.imag]], dtype=float)
    rhs = np.array([(abs(a) ** 2 + 1) / 2, (abs(b) ** 2 + 1) / 2], dtype=float)
    det = float(np.linalg.det(A))
    if abs(det) < 1e-12:
        return None
    xy = np.linalg.solve(A, rhs)
    c = complex(float(xy[0]), float(xy[1]))
    rr = abs(c) ** 2 - 1.0
    if rr <= 1e-14:
        return None
    return c, math.sqrt(rr)


def reflect_point(z: complex, a: complex, b: complex) -> complex:
    """Hyperbolic reflection of z across geodesic a—b (circle inversion / diameter)."""
    gc = geodesic_circle(a, b)
    if gc is None:
        d = a if abs(a) >= abs(b) else b
        if abs(d) < 1e-15:
            d = a + b
        if abs(d) < 1e-15:
            return -z
        proj_scale = (z.real * d.real + z.imag * d.imag) / (abs(d) ** 2)
        return 2 * d * proj_scale - z
    c, R = gc
    w = z - c
    if abs(w) < 1e-18:
        return z
    # inversion in circle |z − c| = R  (geodesic is the arc)
    return c + (R * R) / w.conjugate()


def reflect_polygon(poly: list[complex], a: complex, b: complex) -> list[complex]:
    return [reflect_point(z, a, b) for z in poly]


def arc_polyline(a: complex, b: complex, n: int = 48) -> np.ndarray:
    """Sample the hyperbolic geodesic a→b as an (N,2) polyline inside the disk."""
    gc = geodesic_circle(a, b)
    if gc is None:
        t = np.linspace(0, 1, max(2, n // 3))
        pts = np.c_[a.real * (1 - t) + b.real * t, a.imag * (1 - t) + b.imag * t]
        return pts
    c, R = gc
    th0 = math.atan2(a.imag - c.imag, a.real - c.real)
    th1 = math.atan2(b.imag - c.imag, b.real - c.real)
    # two possible arcs; pick the one whose midpoint lies deeper in the disk
    def sweep(t0, t1, direction):
        # direction +1 or -1 short path adjustment
        d = (t1 - t0) % (2 * math.pi)
        if direction < 0:
            d = d - 2 * math.pi
        if abs(d) < 1e-12:
            d = 0.0
        # prefer the arc with |Δθ| <= π when both ok; check mid radius
        return d

    d_ccw = (th1 - th0) % (2 * math.pi)
    d_cw = d_ccw - 2 * math.pi
    mid_ccw = c + R * cmath_exp(th0 + d_ccw / 2)
    mid_cw = c + R * cmath_exp(th0 + d_cw / 2)
    # geodesic inside disk is the arc that stays inside — smaller |mid| usually,
    # but also both mids may be inside; choose arc where max sample |z| is minimized
    # and arc is the minor one if both fine
    def score(d):
        ts = th0 + np.linspace(0, d, 12)
        zs = c + R * np.exp(1j * ts)
        return float(np.max(np.abs(zs)))

    d = d_ccw if score(d_ccw) <= score(d_cw) else d_cw
    # if chosen arc goes outside, flip
    if score(d) > 0.999:
        d = d_cw if d == d_ccw else d_ccw
    ts = th0 + np.linspace(0, d, n)
    zs = c + R * np.exp(1j * ts)
    return np.c_[zs.real, zs.imag]


# ── tiling generation ────────────────────────────────────────────────────────
def _poly_key(poly: list[complex], nd: int = 5) -> frozenset:
    return frozenset((round(z.real, nd), round(z.imag, nd)) for z in poly)


def _edge_key(a: complex, b: complex, nd: int = 5) -> frozenset:
    return frozenset({
        (round(a.real, nd), round(a.imag, nd)),
        (round(b.real, nd), round(b.imag, nd)),
    })


def generate_tiling(p: int = 3, q: int = 7, depth: int = 5):
    """
    BFS reflection tiling. Returns (polygons, edges).
    polygons: list of list[complex]
    edges: list of (complex, complex)
    """
    if (p - 2) * (q - 2) <= 4:
        raise ValueError(f"{{p,q}}={{{p},{q}}} is not hyperbolic")

    root = central_polygon(p, q)
    polys = [root]
    seen = {_poly_key(root)}
    edges_set = {}
    queue = deque([(root, 0)])

    def add_edge(u, v):
        k = _edge_key(u, v)
        if k not in edges_set:
            edges_set[k] = (u, v)

    for i in range(p):
        add_edge(root[i], root[(i + 1) % p])

    while queue:
        poly, d = queue.popleft()
        if d >= depth:
            continue
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            nb = reflect_polygon(poly, a, b)
            # drop if any vertex escaped the disk (numerical)
            if any(abs(z) > 0.9995 for z in nb):
                # still keep edges near boundary if endpoints ok
                pass
            key = _poly_key(nb)
            if key in seen:
                continue
            # reject if centroid outside open disk
            cen = sum(nb, 0j) / len(nb)
            if abs(cen) > 0.998:
                continue
            if any(abs(z) > 1.001 for z in nb):
                continue
            seen.add(key)
            polys.append(nb)
            queue.append((nb, d + 1))
            for j in range(len(nb)):
                add_edge(nb[j], nb[(j + 1) % len(nb)])

    return polys, list(edges_set.values())


# ── draw ─────────────────────────────────────────────────────────────────────
def draw_poincare(
    ax,
    p: int = 7,
    q: int = 3,
    depth: int = 3,
    lw_scale: float = 1.0,
    style: str = "atelier",
    fill_alternate: bool = True,
):
    """
    Draw {p,q} tiling in the unit Poincaré disk.
    style: atelier | wire | solid
    Defaults {7,3} depth 3 — classic filled Poincaré disk (heptagons).
    Returns xs, ys for framing (slightly past unit circle).
    """
    polys, edges = generate_tiling(p, q, depth=depth)
    pal = _P

    # Light gallery look: whisper fills + hairline wire (avoid the black disk)
    if style == "atelier":
        face_a, face_b, wire_a = 0.022, 0.012, 0.55
        fill_r_max = 0.55
        lw_base, lw_min = 0.55, 0.12
    elif style == "solid":
        face_a, face_b, wire_a = 0.06, 0.035, 0.60
        fill_r_max = 0.65
        lw_base, lw_min = 0.65, 0.14
    else:  # wire
        face_a, face_b, wire_a = 0.0, 0.0, 0.58
        fill_r_max = 0.0
        lw_base, lw_min = 0.50, 0.11

    if style != "wire" and fill_alternate and face_a > 0:
        for poly in polys:
            cen = sum(poly, 0j) / len(poly)
            r = abs(cen)
            if r > fill_r_max:
                continue
            band = int(r * 10)
            ang = int((math.atan2(cen.imag, cen.real) + math.pi) / (math.pi / 3))
            pts = np.array([[z.real, z.imag] for z in poly])
            # fade fills quickly — never a solid grey disk at centre
            fade = max(0.0, 1.0 - r / max(fill_r_max, 1e-6)) ** 1.4
            alpha = (face_a if (band + ang) % 2 == 0 else face_b) * fade
            if alpha > 0.006:
                ax.add_patch(mp.Polygon(
                    pts, closed=True, facecolor=pal["face_a"],
                    edgecolor="none", alpha=alpha, zorder=1,
                ))

    # edges as geodesic arcs — more samples near the rim
    segs = []
    lws = []
    alphas = []
    for a, b in edges:
        if abs(a) > 1.002 or abs(b) > 1.002:
            continue
        rm = 0.5 * (abs(a) + abs(b))
        n = 20 if rm < 0.55 else (36 if rm < 0.85 else 52)
        pl = arc_polyline(a, b, n=n)
        rr = pl[:, 0] ** 2 + pl[:, 1] ** 2
        pl = pl[rr <= 1.0005]
        if len(pl) < 2:
            continue
        mid = pl[len(pl) // 2]
        r = math.hypot(float(mid[0]), float(mid[1]))
        # strong radial thinning: outer rings stay lace-like, not charcoal
        lw = max(lw_min, lw_base * (1.0 - 0.88 * r * r)) * lw_scale
        al = wire_a * (0.42 + 0.58 * (1.0 - r) ** 0.85)
        segs.append(pl)
        lws.append(lw)
        alphas.append(min(0.72, al))

    for pl, lw, al in zip(segs, lws, alphas):
        ax.plot(
            pl[:, 0], pl[:, 1], color=pal["wire"], lw=lw,
            alpha=al, solid_capstyle="round", solid_joinstyle="round",
            zorder=3,
        )

    # unit circle boundary (the absolute) — present but not heavy
    theta = np.linspace(0, 2 * math.pi, 500)
    ax.plot(
        np.cos(theta), np.sin(theta), color=pal["boundary"],
        lw=1.15 * lw_scale, alpha=0.72, zorder=5,
    )

    if style == "atelier":
        ax.add_patch(mp.Circle(
            (0, 0), 0.007, facecolor=pal["ink"],
            edgecolor="none", alpha=0.55, zorder=6,
        ))

    pad = 1.08
    return np.array([-pad, pad]), np.array([-pad, pad])


def render_image(
    px_w: int,
    px_h: int,
    palette: str = "mono",
    style: str = "atelier",
    p: int = 7,
    q: int = 3,
    depth: int = 3,
    pad: float = 1.10,
):
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

    # Slightly softer than Metatron — dense tilings read heavy at 1:1 scale
    lw_scale = (px_h / 600.0) * 0.82
    xs, ys = draw_poincare(
        ax, p=p, q=q, depth=depth, lw_scale=lw_scale, style=style,
    )
    cx = cy = 0.0
    a = px_w / px_h
    # square art in frame — disk centered
    half = pad
    HH = half
    WW = HH * a
    # ensure disk fits: half disk radius ~1 * pad framing
    # art extends to ~1.0; pad multiplies view
    view = pad
    HH = view
    WW = HH * a
    if WW < view:
        WW = view
        HH = WW / a
    ax.set_xlim(-WW, WW)
    ax.set_ylim(-HH, HH)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parent / "out" / "poincare" / "_smoke"
    out.mkdir(parents=True, exist_ok=True)
    configs = [
        (7, 3, 3),   # primary product — heptagons, fills disk
        (3, 7, 11),  # Escher triangles — needs depth to reach rim
        (5, 4, 4),
    ]
    for p, q, depth in configs:
        for st in ("atelier", "wire"):
            im = render_image(900, 1125, palette="mono", style=st, p=p, q=q, depth=depth)
            im.save(out / f"smoke_{p}_{q}_d{depth}_mono_{st}.jpg", quality=92)
            print("wrote", p, q, "d"+str(depth), st)
    print("OK", out)
