"""
generate_riso_set.py — "Science Specimens" Risograph-style STEM plate set
============================================================================
A cabinet-of-curiosities take on six classic phenomena (cymatics, the golden
spiral, the Platonic solids, the Bohr atom, a Koch snowflake, and two-slit
interference), styled like naturalist specimen cards run through a two-color
riso press: crisp black keyline + one halftone spot color per plate, slight
registration offset, uncoated recycled-paper grain. Distinct from the
cream/Cinzel "scientific plate" house style used elsewhere in the shop.

Architecture: every illustration is rendered twice on a throwaway matplotlib
figure — once as pure black linework, once as a spot-color "tone" layer whose
alpha encodes shading depth — then composited in PIL: paper texture, tone
layer run through an angled-dot halftone screen and nudged a few px off
register, black linework on top (kept crisp, never halftoned). ALL typography
and card chrome (border, corner marks, catalog labels, title, caption,
footer) is placed with plain PIL pixel math, not matplotlib text — sidesteps
the imshow aspect-lock / text-collision issues hit on the DNA set entirely,
since nothing here shares an Axes across multiple placements.

  python generate_riso_set.py
"""
import io
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import map_coordinates

BASE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(BASE, "plates")
os.makedirs(PLATES, exist_ok=True)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_BOLD = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF_REG = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SERIF_IT = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")
MONO = os.path.join(FONT_DIR, "LiberationMono-Regular.ttf")
MONO_BOLD = os.path.join(FONT_DIR, "LiberationMono-Bold.ttf")

# ── palette ──────────────────────────────────────────────────────────────
PAPER = "#efe6d3"
INK = "#1c1a17"
RISO_RED = "#e8432c"
RISO_BLUE = "#0d6fae"
RISO_OCHRE = "#e0952a"

DPI = 300
W_IN, H_IN = 9.0, 11.5
W_PX, H_PX = round(W_IN * DPI), round(H_IN * DPI)

ILL_PX = 2000  # square working canvas for each illustration pass


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ── paper texture ────────────────────────────────────────────────────────
def paper_texture(w, h, seed=7):
    rng = np.random.default_rng(seed)
    base = np.array(hx(PAPER), dtype=np.float32)
    small = rng.normal(0, 1, size=(h // 3, w // 3)).astype(np.float32)
    grain = np.array(Image.fromarray(((small - small.min()) / (np.ptp(small)) * 255).astype(np.uint8))
                      .resize((w, h), Image.BILINEAR), dtype=np.float32)
    grain = (grain - grain.mean()) / 255.0
    arr = np.ones((h, w, 3), dtype=np.float32) * base
    arr += grain[..., None] * 14.0
    n_flecks = int(w * h * 0.00012)
    fx = rng.integers(0, w, n_flecks)
    fy = rng.integers(0, h, n_flecks)
    fd = rng.uniform(-30, -10, n_flecks)
    arr[fy, fx, :] += fd[:, None]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


# ── halftone (with dot gain + uneven ink coverage) ──────────────────────
def smooth_noise_field(h, w, seed, scale, lo=-1.0, hi=1.0):
    rng = np.random.default_rng(seed)
    small = rng.normal(0, 1, size=(max(2, h // scale), max(2, w // scale))).astype(np.float32)
    big = np.array(Image.fromarray(((small - small.min()) / np.ptp(small) * 255).astype(np.uint8))
                    .resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0
    big = (big - big.min()) / (big.max() - big.min())
    return lo + big * (hi - lo)


def mottle_field(h, w, seed=11, scale=230, strength=0.45):
    return 1.0 + smooth_noise_field(h, w, seed, scale, -strength, strength)


def halftone_from_alpha(alpha01, cell=9, angle=37.0, mottle=None, gain_gamma=0.74):
    h, w = alpha01.shape
    theta = np.radians(angle)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xr = xx * np.cos(theta) + yy * np.sin(theta)
    yr = -xx * np.sin(theta) + yy * np.cos(theta)
    cx = np.mod(xr, cell) - cell / 2.0
    cy = np.mod(yr, cell) - cell / 2.0
    dist = np.sqrt(cx ** 2 + cy ** 2)
    a = np.clip(alpha01, 0, 1)
    if mottle is not None:
        a = np.clip(a * mottle, 0, 1)
    a_gain = a ** gain_gamma  # gamma < 1 boosts midtones -> simulated dot gain
    radius = (cell * 0.74 / 2.0) * np.sqrt(a_gain)
    return dist <= radius


def render_pass(draw_fn, mode, px=ILL_PX):
    fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    draw_fn(ax, mode)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA").resize((px, px), Image.LANCZOS)


# ── organic press wobble ─────────────────────────────────────────────────
def organic_warp(img, seed, amplitude=1.6, scale=260):
    arr = np.asarray(img).astype(np.float32)
    h, w = arr.shape[:2]
    dx = smooth_noise_field(h, w, seed, scale, -amplitude, amplitude)
    dy = smooth_noise_field(h, w, seed + 1, scale, -amplitude, amplitude)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    src_y = np.clip(yy + dy, 0, h - 1)
    src_x = np.clip(xx + dx, 0, w - 1)
    out = np.empty_like(arr)
    for c in range(arr.shape[2]):
        out[..., c] = map_coordinates(arr[..., c], [src_y, src_x], order=1, mode="nearest")
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def compose_illustration(draw_fn, spot_hex, cell=9, angle=37.0, offset=(5, -4), warp_seed=None):
    line_img = render_pass(draw_fn, "line")
    tone_img = render_pass(draw_fn, "tone")
    if warp_seed is not None:
        line_img = organic_warp(line_img, seed=warp_seed * 10 + 1)
        tone_img = organic_warp(tone_img, seed=warp_seed * 10 + 1)

    tone_alpha = np.asarray(tone_img)[..., 3].astype(np.float32) / 255.0
    mottle = mottle_field(*tone_alpha.shape, seed=(warp_seed or 0) * 10 + 3)
    dots = halftone_from_alpha(tone_alpha, cell=cell, angle=angle, mottle=mottle)
    spot_rgb = hx(spot_hex)
    tone_out = np.zeros((*dots.shape, 4), dtype=np.uint8)
    tone_out[dots, 0:3] = spot_rgb
    tone_out[dots, 3] = 232  # slight translucency -- paper shows through the ink
    tone_final = Image.fromarray(tone_out, "RGBA").filter(ImageFilter.GaussianBlur(0.55))

    line_final = line_img.filter(ImageFilter.GaussianBlur(0.32))

    canvas = Image.new("RGBA", line_img.size, (0, 0, 0, 0))
    dx, dy = offset
    canvas.alpha_composite(tone_final, (dx, dy))
    canvas.alpha_composite(line_final, (0, 0))
    return canvas


# ── typography helpers ──────────────────────────────────────────────────
def font(path, size):
    return ImageFont.truetype(path, size)


def tracked_width(draw, text, fnt, tracking):
    w = 0
    for ch in text:
        b = draw.textbbox((0, 0), ch, font=fnt)
        w += (b[2] - b[0]) + tracking
    return max(0, w - tracking)


def draw_tracked(draw, xy, text, fnt, fill, tracking=0, anchor="l"):
    x, y = xy
    total = tracked_width(draw, text, fnt, tracking)
    if anchor == "m":
        x -= total / 2
    elif anchor == "r":
        x -= total
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        b = draw.textbbox((0, 0), ch, font=fnt)
        x += (b[2] - b[0]) + tracking
    return total


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ── card scaffold ───────────────────────────────────────────────────────
MARGIN = 96
ILL_BOX = (200, 300, W_PX - 200, 2460)  # x0,y0,x1,y1


def build_plate(spec_no, title, eyebrow_right, caption, footer_items, draw_fn,
                 spot_hex, cell=9, angle=37.0, offset=(5, -4), sub_eyebrow="MATHRELAXING FIELD NOTES"):
    warp_seed = spec_no
    canvas = paper_texture(W_PX, H_PX).convert("RGB")
    d = ImageDraw.Draw(canvas)
    ink = hx(INK)
    spot = hx(spot_hex)

    # outer + inner border (double rule, specimen-card frame)
    d.rectangle([MARGIN, MARGIN, W_PX - MARGIN, H_PX - MARGIN], outline=ink, width=3)
    d.rectangle([MARGIN + 14, MARGIN + 14, W_PX - MARGIN - 14, H_PX - MARGIN - 14], outline=ink, width=1)

    # corner registration crosshairs, just outside the frame
    arm = 26
    for cx0, cy0 in [(MARGIN, MARGIN), (W_PX - MARGIN, MARGIN), (MARGIN, H_PX - MARGIN), (W_PX - MARGIN, H_PX - MARGIN)]:
        d.line([cx0 - arm, cy0, cx0 + arm, cy0], fill=spot, width=3)
        d.line([cx0, cy0 - arm, cx0, cy0 + arm], fill=spot, width=3)
        d.ellipse([cx0 - 5, cy0 - 5, cx0 + 5, cy0 + 5], outline=ink, width=2)

    # eyebrow row
    ey = MARGIN + 56
    f_eyebrow = font(MONO, 30)
    draw_tracked(d, (MARGIN + 60, ey), sub_eyebrow, f_eyebrow, ink, tracking=4)
    draw_tracked(d, (W_PX - MARGIN - 60, ey), eyebrow_right, f_eyebrow, ink, tracking=4, anchor="r")
    d.line([MARGIN + 60, ey + 52, W_PX - MARGIN - 60, ey + 52], fill=ink, width=2)

    # illustration box (glass-case frame) + paste composited artwork
    x0, y0, x1, y1 = ILL_BOX
    d.rectangle([x0, y0, x1, y1], outline=ink, width=2)
    art = compose_illustration(draw_fn, spot_hex, cell=cell, angle=angle, offset=offset, warp_seed=warp_seed)
    inner_pad = 26
    box_w, box_h = (x1 - x0 - 2 * inner_pad), (y1 - y0 - 2 * inner_pad)
    side = min(box_w, box_h)
    art_resized = art.resize((side, side), Image.LANCZOS)
    ax_ = x0 + (x1 - x0 - side) // 2
    ay_ = y0 + (y1 - y0 - side) // 2
    canvas.paste(art_resized, (ax_, ay_), art_resized)

    # title (tracked bold caps, centered)
    f_title = font(SERIF_BOLD, 74)
    ty = y1 + 66
    draw_tracked(d, (W_PX // 2, ty), title.upper(), f_title, ink, tracking=6, anchor="m")

    # spot-color accent rule under title
    rule_w = 130
    d.rectangle([W_PX // 2 - rule_w // 2, ty + 96, W_PX // 2 + rule_w // 2, ty + 101], fill=spot)

    # caption (wrapped, italic serif, centered block)
    f_cap = font(SERIF_IT, 40)
    cap_y = ty + 132
    max_w = W_PX - 2 * (MARGIN + 220)
    lines = []
    for para in caption:
        lines.extend(wrap_text(d, para, f_cap, max_w))
    for ln in lines:
        w = d.textbbox((0, 0), ln, font=f_cap)[2]
        d.text((W_PX // 2 - w / 2, cap_y), ln, font=f_cap, fill=ink)
        cap_y += 54

    # footer museum-label strip
    fy0 = H_PX - MARGIN - 210
    d.line([MARGIN + 60, fy0, W_PX - MARGIN - 60, fy0], fill=ink, width=2)
    n = len(footer_items)
    col_w = (W_PX - 2 * (MARGIN + 60)) / n
    f_val = font(MONO_BOLD, 42)
    f_key = font(MONO, 26)
    for i, (val, key) in enumerate(footer_items):
        cx = MARGIN + 60 + col_w * i + col_w / 2
        draw_tracked(d, (cx, fy0 + 34), val, f_val, ink, tracking=1, anchor="m")
        draw_tracked(d, (cx, fy0 + 96), key.upper(), f_key, hx("#6b6558"), tracking=3, anchor="m")
        if i > 0:
            d.line([MARGIN + 60 + col_w * i, fy0 + 20, MARGIN + 60 + col_w * i, fy0 + 150], fill=hx("#c9c0aa"), width=1)

    # bottom plate id
    f_id = font(MONO, 24)
    draw_tracked(d, (W_PX // 2, H_PX - MARGIN - 60), f"SPECIMEN {spec_no:02d} / 06  ·  RISO EDITION  ·  MATHRELAXING",
                 f_id, hx("#8a8370"), tracking=3, anchor="m")

    return canvas


def save_plate(canvas, name):
    out = os.path.join(PLATES, name)
    canvas.save(out, "JPEG", quality=93)
    print("wrote", out, canvas.size)


# ── shared small helpers ────────────────────────────────────────────────
def _fill_nested(ax, xs, ys, base_alpha, steps=6, min_scale=0.28):
    cx, cy = np.mean(xs), np.mean(ys)
    for i in range(steps):
        s = 1.0 - (1.0 - min_scale) * i / (steps - 1)
        sx = cx + (np.array(xs) - cx) * s
        sy = cy + (np.array(ys) - cy) * s
        ax.fill(sx, sy, color="black", alpha=base_alpha, linewidth=0)


# ── 1. cymatics / chladni plate ─────────────────────────────────────────
def draw_cymatics(ax, mode):
    n, m = 5, 4
    N = 500
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    U, V = (X + 1) / 2, (Y + 1) / 2
    W = np.cos(n * np.pi * U) * np.cos(m * np.pi * V) - np.cos(m * np.pi * U) * np.cos(n * np.pi * V)

    if mode == "tone":
        amp = np.abs(W) / np.abs(W).max()
        alpha = 0.10 + 0.30 * (1 - amp)
        rgba = np.zeros((N, N, 4))
        rgba[..., 3] = alpha
        ax.imshow(rgba, extent=(-1, 1, -1, 1), origin="lower", aspect="auto", zorder=1)
        ax.fill([-0.86, 0.86, 0.86, -0.86], [-0.86, -0.86, 0.86, 0.86], color="black", alpha=0.05, zorder=0)
        ax.add_patch(plt.Circle((0, 0), 0.05, color="black", alpha=0.35, zorder=2))
        return

    cs = ax.contour(X, Y, W, levels=[0])
    segs = cs.allsegs[0]
    cs.remove()
    rng = np.random.default_rng(3)
    for seg in segs:
        seg = np.asarray(seg)
        d = np.sqrt(((seg[1:] - seg[:-1]) ** 2).sum(axis=1))
        arc = np.concatenate([[0], np.cumsum(d)])
        total = arc[-1]
        if total <= 0:
            continue
        n_pts = max(int(total / 0.0035), 2)
        s = np.linspace(0, total, n_pts)
        px = np.interp(s, arc, seg[:, 0])
        py = np.interp(s, arc, seg[:, 1])
        jx = rng.normal(0, 0.004, n_pts)
        jy = rng.normal(0, 0.004, n_pts)
        sizes = rng.uniform(2.0, 6.5, n_pts)
        ax.scatter(px + jx, py + jy, s=sizes, c=INK, alpha=1.0, linewidths=0, zorder=3)

    ax.plot([-0.86, 0.86, 0.86, -0.86, -0.86], [-0.86, -0.86, 0.86, 0.86, -0.86], color=INK, lw=2.4, zorder=4)
    ax.add_patch(plt.Circle((0, 0), 0.05, edgecolor=INK, facecolor="none", lw=1.6, zorder=4))
    for a in np.linspace(0, 2 * np.pi, 4, endpoint=False):
        ax.plot([0, 0.10 * np.cos(a)], [0, 0.10 * np.sin(a)], color=INK, lw=0.8, alpha=0.5, zorder=4)


# ── 2. nautilus / golden spiral ─────────────────────────────────────────
def draw_fibonacci(ax, mode):
    phi = (1 + 5 ** 0.5) / 2
    b = np.log(phi) / (np.pi / 2)
    r0 = 0.028
    theta_max = 6.4 * np.pi
    theta = np.linspace(0.001, theta_max, 3000)
    r_outer = r0 * np.exp(b * theta)
    keep = r_outer <= 0.92
    theta, r_outer = theta[keep], r_outer[keep]
    r_inner = r_outer * 0.82

    xo, yo = r_outer * np.cos(theta), r_outer * np.sin(theta)
    xi, yi = r_inner * np.cos(theta), r_inner * np.sin(theta)

    septa_theta = np.arange(np.pi, theta[-1], np.pi / 2)

    if mode == "line":
        ax.plot(xo, yo, color=INK, lw=2.2, zorder=4)
        ax.plot(xi, yi, color=INK, lw=1.1, alpha=0.75, zorder=4)
        for th in septa_theta:
            ro = r0 * np.exp(b * th)
            ri = ro * 0.82
            if ro > 0.92:
                continue
            ax.plot([ri * np.cos(th), ro * np.cos(th)], [ri * np.sin(th), ro * np.sin(th)],
                     color=INK, lw=1.0, alpha=0.8, zorder=4)
        ax.plot(0, 0, marker="o", ms=2.5, color=INK, zorder=5)
        return

    # tone: fill successive chambers between septa with alternating alpha
    chambers = np.concatenate([[theta[0]], septa_theta, [theta[-1]]])
    chambers = chambers[chambers <= theta[-1]]
    for i in range(len(chambers) - 1):
        t0, t1 = chambers[i], chambers[i + 1]
        seg = theta[(theta >= t0) & (theta <= t1)]
        if len(seg) < 2:
            continue
        ro = r0 * np.exp(b * seg)
        ri = ro * 0.82
        xs = np.concatenate([ro * np.cos(seg), (ri * np.cos(seg))[::-1]])
        ys = np.concatenate([ro * np.sin(seg), (ri * np.sin(seg))[::-1]])
        a = 0.16 + 0.22 * (i % 3) / 2
        ax.fill(xs, ys, color="black", alpha=a, linewidth=0, zorder=1)


# ── 3. platonic solids (real 3D pyvista render, see render_solids_3d.py) ──
_SOLIDS_TONE = np.asarray(Image.open(os.path.join(BASE, "_solids_tone.png")))
_SOLIDS_LINE = np.asarray(Image.open(os.path.join(BASE, "_solids_line.png")))


def draw_platonic(ax, mode):
    img = _SOLIDS_TONE if mode == "tone" else _SOLIDS_LINE
    ax.imshow(img, extent=(-1, 1, -1, 1), aspect="auto",
              zorder=1 if mode == "tone" else 4)


# ── 4. bohr atom ──────────────────────────────────────────────────────────
def draw_bohr(ax, mode):
    radii = [0.28, 0.44, 0.60, 0.76]
    if mode == "tone":
        N = 400
        x = np.linspace(-1, 1, N)
        X, Y = np.meshgrid(x, x)
        R = np.sqrt(X ** 2 + Y ** 2)
        glow = np.clip(1 - R / 0.30, 0, 1) ** 1.6
        rgba = np.zeros((N, N, 4))
        rgba[..., 3] = glow * 0.55
        ax.imshow(rgba, extent=(-1, 1, -1, 1), origin="lower", aspect="auto", zorder=1)
        for rr in radii:
            band = np.exp(-((R - rr) ** 2) / (2 * 0.012 ** 2))
            rgba2 = np.zeros((N, N, 4))
            rgba2[..., 3] = band * 0.30
            ax.imshow(rgba2, extent=(-1, 1, -1, 1), origin="lower", aspect="auto", zorder=1)
        return

    for i in range(3):
        a = np.random.default_rng(i).uniform(0, 2 * np.pi)
        ax.plot(0.10 * np.cos(a) * 0.5, 0.10 * np.sin(a) * 0.5, marker="o", ms=3, color=INK, zorder=5)
    ax.add_patch(plt.Circle((0, 0), 0.09, edgecolor=INK, facecolor="none", lw=1.8, zorder=4))
    for rr in radii:
        ax.add_patch(plt.Circle((0, 0), rr, edgecolor=INK, facecolor="none", lw=1.0, alpha=0.7,
                                 linestyle=(0, (1, 2)), zorder=3))

    ang = np.radians(35)
    p3 = (radii[2] * np.cos(ang), radii[2] * np.sin(ang))
    p2 = (radii[1] * np.cos(ang), radii[1] * np.sin(ang))
    ax.plot(*p3, marker="o", ms=6, color=INK, zorder=6)
    ax.annotate("", xy=p2, xytext=p3,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4,
                                 connectionstyle="arc3,rad=-0.5"), zorder=5)
    ax.plot(*p2, marker="o", ms=6, markerfacecolor=INK, markeredgecolor=INK, zorder=6)

    # photon flies off the opposite side so it never crosses the transition arc
    pang = ang + np.pi
    p_start = (radii[1] * 0.55 * np.cos(pang), radii[1] * 0.55 * np.sin(pang))
    p_end = (0.97 * np.cos(pang), 0.97 * np.sin(pang))
    t = np.linspace(0, 1, 120)
    perp = pang + np.pi / 2
    wx = p_start[0] + t * (p_end[0] - p_start[0]) + 0.045 * np.sin(t * 7 * np.pi) * (1 - t * 0.3) * np.cos(perp)
    wy = p_start[1] + t * (p_end[1] - p_start[1]) + 0.045 * np.sin(t * 7 * np.pi) * (1 - t * 0.3) * np.sin(perp)
    ax.plot(wx, wy, color=INK, lw=1.1, alpha=0.85, zorder=5)


# ── 5. koch snowflake ─────────────────────────────────────────────────────
def _koch(p1, p2, depth):
    if depth == 0:
        return [p1, p2]
    p1, p2 = np.array(p1), np.array(p2)
    delta = (p2 - p1) / 3
    a = p1 + delta
    b = p1 + 2 * delta
    ang = np.pi / 3
    rot = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    peak = a + rot.dot(delta)
    return (_koch(p1, a, depth - 1)[:-1] + _koch(a, peak, depth - 1)[:-1]
            + _koch(peak, b, depth - 1)[:-1] + _koch(b, p2, depth - 1))


def _snowflake(depth, R=0.82):
    angs = [np.pi / 2, np.pi / 2 + 2 * np.pi / 3, np.pi / 2 + 4 * np.pi / 3]
    corners = [(R * np.cos(a), R * np.sin(a)) for a in angs]
    pts = (_koch(corners[0], corners[1], depth)[:-1]
           + _koch(corners[1], corners[2], depth)[:-1]
           + _koch(corners[2], corners[0], depth))
    return np.array(pts)


def draw_koch(ax, mode):
    if mode == "tone":
        pts = _snowflake(3)
        _fill_nested(ax, pts[:, 0], pts[:, 1], base_alpha=0.07, steps=7, min_scale=0.15)
        return

    for depth, a in [(0, 0.22), (1, 0.30), (2, 0.45)]:
        pts = _snowflake(depth)
        xs = np.append(pts[:, 0], pts[0, 0])
        ys = np.append(pts[:, 1], pts[0, 1])
        ax.plot(xs, ys, color=INK, lw=0.8, alpha=a, linestyle=(0, (2, 3)), zorder=2)

    pts = _snowflake(4)
    xs = np.append(pts[:, 0], pts[0, 0])
    ys = np.append(pts[:, 1], pts[0, 1])
    ax.plot(xs, ys, color=INK, lw=1.5, zorder=4)


# ── 6. double-slit interference ───────────────────────────────────────────
SLIT_X = -0.55
SLIT_Y = 0.12
SLIT_HALF = 0.05
LAM = 0.16
SCREEN_X = 0.86


def draw_interference(ax, mode):
    if mode == "tone":
        N = 500
        x = np.linspace(-1, 1, N)
        y = np.linspace(-1, 1, N)
        X, Y = np.meshgrid(x, y)
        r1 = np.sqrt((X - SLIT_X) ** 2 + (Y - SLIT_Y) ** 2)
        r2 = np.sqrt((X - SLIT_X) ** 2 + (Y + SLIT_Y) ** 2)
        k = 2 * np.pi / LAM
        amp = np.cos(k * r1) + np.cos(k * r2)
        inten = (amp ** 2) / 4.0
        inten[X < SLIT_X + 0.02] = 0
        rgba = np.zeros((N, N, 4))
        rgba[..., 3] = inten * 0.85
        ax.imshow(rgba, extent=(-1, 1, -1, 1), origin="lower", aspect="auto", zorder=1)
        return

    for r in np.arange(0.08, 1.6, 0.09):
        th = np.linspace(-np.pi * 0.48, np.pi * 0.48, 200)
        for sy, sign in [(SLIT_Y, 1), (-SLIT_Y, 1)]:
            xs = SLIT_X + r * np.cos(th)
            ys = sy + r * np.sin(th)
            keep = xs > SLIT_X + 0.02
            ax.plot(xs[keep], ys[keep], color=INK, lw=0.5, alpha=0.22, zorder=2)

    wall_segs = [(0.17, 1.0), (-SLIT_HALF - 0.02, SLIT_HALF + 0.02), (-1.0, -0.17)]
    for y0, y1 in wall_segs:
        ax.plot([SLIT_X, SLIT_X], [y0, y1], color=INK, lw=5.0, solid_capstyle="butt", zorder=5)

    ax.plot([SCREEN_X, SCREEN_X], [-1, 1], color=INK, lw=1.2, linestyle=(0, (4, 3)), zorder=4)

    y = np.linspace(-1, 1, 400)
    r1 = np.sqrt((SCREEN_X - SLIT_X) ** 2 + (y - SLIT_Y) ** 2)
    r2 = np.sqrt((SCREEN_X - SLIT_X) ** 2 + (y + SLIT_Y) ** 2)
    k = 2 * np.pi / LAM
    amp = np.cos(k * r1) + np.cos(k * r2)
    inten = (amp ** 2) / 4.0
    prof_x = SCREEN_X + 0.05 + 0.16 * inten
    ax.plot(prof_x, y, color=INK, lw=1.3, zorder=5)
    ax.plot([SCREEN_X + 0.05, SCREEN_X + 0.05], [-1, 1], color=INK, lw=0.7, alpha=0.5, zorder=3)


# ── plate specs & build ───────────────────────────────────────────────────
PLATE_SPECS = [
    dict(spec_no=1, fname="01_cymatics.jpg", title="Cymatics", eyebrow="FIG. 01",
         spot=RISO_BLUE, draw=draw_cymatics, cell=8, angle=32,
         caption=["A brass plate, fine sand, and a violin bow: nodal lines emerge",
                  "where the surface holds still while every antinode dances."],
         footer=[("N=5, M=4", "chladni modes"), ("SQUARE PLATE", "boundary"), ("E. CHLADNI, 1787", "first observed")]),
    dict(spec_no=2, fname="02_nautilus_spiral.jpg", title="The Golden Spiral", eyebrow="FIG. 02",
         spot=RISO_OCHRE, draw=draw_fibonacci, cell=8, angle=42,
         caption=["Each chamber is built at a quarter turn from the last, scaled",
                  "by phi -- the same growth rule a nautilus shell has followed for 500 million years."],
         footer=[("PHI = 1.618...", "growth ratio"), ("R = R0 * e^(B*THETA)", "logarithmic spiral"), ("NAUTILUS POMPILIUS", "specimen")]),
    dict(spec_no=3, fname="03_platonic_solids.jpg", title="The Five Solids", eyebrow="FIG. 03",
         spot=RISO_RED, draw=draw_platonic, cell=7, angle=27,
         caption=["Tetrahedron, cube, octahedron, dodecahedron, icosahedron -- the only",
                  "five convex forms where every face, edge, and angle repeats identically."],
         footer=[("4, 6, 8, 12, 20 FACES", "by solid"), ("PLATO, C. 360 BCE", "timaeus"), ("EUCLID XIII.18", "proof of exactly five")]),
    dict(spec_no=4, fname="04_bohr_atom.jpg", title="The Bohr Atom", eyebrow="FIG. 04",
         spot=RISO_BLUE, draw=draw_bohr, cell=7, angle=50,
         caption=["An electron falls from shell n=3 to n=2 and the energy it sheds",
                  "leaves as a single photon of exactly one wavelength -- no more, no less."],
         footer=[("N=3 -> N=2", "transition"), ("656 NM", "balmer-alpha"), ("N. BOHR, 1913", "quantized orbits")]),
    dict(spec_no=5, fname="05_koch_snowflake.jpg", title="A Koch Snowflake", eyebrow="FIG. 05",
         spot=RISO_OCHRE, draw=draw_koch, cell=7, angle=20,
         caption=["Every edge sprouts a smaller triangle, forever: infinite perimeter",
                  "wrapped around a stubbornly finite patch of ice."],
         footer=[("DIM = LOG4/LOG3", "fractal dimension"), ("PERIMETER -> INF", "4 iterations shown"), ("H. VON KOCH, 1904", "first published")]),
    dict(spec_no=6, fname="06_double_slit.jpg", title="Two-Slit Interference", eyebrow="FIG. 06",
         spot=RISO_RED, draw=draw_interference, cell=6, angle=15,
         caption=["Waves from two slits overlap on the screen behind them: crest meets",
                  "crest for a bright fringe, crest meets trough for darkness."],
         footer=[("LAMBDA = 0.16 U", "wavelength"), ("D = 0.24 U", "slit spacing"), ("T. YOUNG, 1801", "first demonstrated")]),
]


def build():
    for spec in PLATE_SPECS:
        canvas = build_plate(
            spec_no=spec["spec_no"], title=spec["title"], eyebrow_right=spec["eyebrow"],
            caption=spec["caption"], footer_items=spec["footer"], draw_fn=spec["draw"],
            spot_hex=spec["spot"], cell=spec["cell"], angle=spec["angle"],
        )
        save_plate(canvas, spec["fname"])


def contact_sheet():
    thumbs = []
    for spec in PLATE_SPECS:
        img = Image.open(os.path.join(PLATES, spec["fname"]))
        thumbs.append(img.resize((450, round(450 * img.height / img.width))))
    cols, rows = 3, 2
    pad = 24
    cw, ch = thumbs[0].size
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad), "#1c1a17")
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (pad + c * (cw + pad), pad + r * (ch + pad)))
    sheet.save(os.path.join(BASE, "_contact_sheet.jpg"), quality=90)
    print("contact sheet ->", os.path.join(BASE, "_contact_sheet.jpg"))


if __name__ == "__main__":
    build()
    contact_sheet()
    print("DONE")
