"""
generate_neo_deco.py — "Neo Deco" generative metallic geometric art.

Rides the 2026 Pinterest "Neo Deco / Glamoratti" trend (chrome + jewel tones,
Art-Deco geometry) with a code moat: every motif is parametric (sunbursts,
stepped arches, radial rosettes) and every metal surface is a real multi-stop
vertical gradient masked to the shape, giving a polished chrome / brushed-gold
look no clip-art competitor reproduces.

Output: 2:3 masters at 2400x3600 (= 8x12in @300dpi) -> masters/.
  python generate_neo_deco.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters"); os.makedirs(MAST, exist_ok=True)
AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")

W, H = 2400, 3600
SS = 1                     # native render; masks are edge-softened for AA
BW, BH = W * SS, H * SS

# ---- palettes (background jewel + metals) -------------------------------
EMERALD_BG = [(0.0, "#0b3b31"), (0.5, "#0e4a3d"), (1.0, "#072a23")]
INK_BG     = [(0.0, "#141a24"), (0.5, "#1b2431"), (1.0, "#0c1017")]
SAPPHIRE_BG= [(0.0, "#122a4a"), (0.5, "#173458"), (1.0, "#0c1c33")]

# Matte foil metals: soft single-sweep (lit from top), NO pure-white specular
# band -- avoids the plastic "WordArt chrome" look. Brushed grain is added in
# metal() for a real foil/leaf surface.
CHROME = [(0.00, "#e3e7ea"), (0.34, "#c2c8cd"), (0.62, "#99a1a8"), (1.0, "#727a81")]
GOLD   = [(0.00, "#ecd79c"), (0.34, "#d0ad57"), (0.62, "#a9853a"), (1.0, "#7f6127")]
BRASS  = [(0.00, "#d8b877"), (0.34, "#b48f4c"), (0.62, "#8a6a33"), (1.0, "#5f4720")]


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def grad_v(h, stops):
    """(h,3) uint8 vertical gradient from (pos,color) stops."""
    ps = np.array([p for p, _ in stops])
    cs = np.array([hx(c) for _, c in stops], float)
    y = np.linspace(0, 1, h)
    out = np.empty((h, 3))
    for k in range(3):
        out[:, k] = np.interp(y, ps, cs[:, k])
    return out.astype(np.uint8)


def bg(stops):
    g = grad_v(BH, stops)
    arr = np.repeat(g[:, None, :], BW, axis=1).astype(np.float32)
    # analytic radial vignette computed small then upscaled (fast, smooth)
    sh, sw = BH // 8, BW // 8
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    dx = (xx - sw / 2) / (sw / 2); dy = (yy - sh / 2) / (sh / 2)
    r = np.sqrt(dx * dx + dy * dy)
    v = np.clip(1.0 - 0.5 * np.clip((r - 0.45) / 0.95, 0, 1), 0, 1)
    vimg = Image.fromarray((v * 255).astype(np.uint8), "L").resize((BW, BH), Image.BILINEAR)
    vv = (np.asarray(vimg, np.float32) / 255.0)[:, :, None]
    return Image.fromarray((arr * vv).astype(np.uint8), "RGB")


_GRAIN = None


def metal(mask, stops, band_shift=0.0):
    """RGBA: `mask` filled with a soft single-sweep foil gradient (spanning the
    mask bbox) plus a subtle brushed-metal grain -- reads as real leaf/foil,
    not plastic chrome."""
    global _GRAIN
    bbox = mask.getbbox()
    if not bbox:
        return Image.new("RGBA", mask.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = bbox
    hh = max(1, y1 - y0); ww = mask.size[0]
    g = grad_v(hh, stops).astype(np.float32)
    if band_shift:
        g = np.roll(g, int(band_shift * hh), axis=0)
    tile = np.repeat(g[:, None, :], ww, axis=1)
    # brushed grain: fine per-column streaks + faint pixel noise (cached base)
    if _GRAIN is None or _GRAIN.shape[0] < mask.size[1] or _GRAIN.shape[1] < ww:
        rng = np.random.default_rng(7)
        streak = rng.normal(1.0, 0.018, (1, ww))
        fine = rng.normal(1.0, 0.012, (mask.size[1], ww))
        _GRAIN = (streak * fine).astype(np.float32)
    grain = _GRAIN[y0:y1, :ww, None]
    tile = np.clip(tile * grain, 0, 255)
    strip = np.zeros((mask.size[1], ww, 3), np.uint8)
    strip[y0:y1, :, :] = tile.astype(np.uint8)
    rgba = np.dstack([strip, np.array(mask, np.uint8)])
    return Image.fromarray(rgba, "RGBA")


def outline(base, mask, color, width):
    edge = mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    ring = Image.fromarray(np.clip(np.array(edge, int) - np.array(mask, int), 0, 255).astype(np.uint8))
    lay = Image.new("RGBA", base.size, (*color, 0))
    lay.putalpha(ring)
    base.alpha_composite(lay)


def wedge_mask(cx, cy, r0, r1, a0, a1, steps=60):
    m = Image.new("L", (BW, BH), 0)
    d = ImageDraw.Draw(m)
    ang = np.linspace(np.radians(a0), np.radians(a1), steps)
    pts = [(cx + r1 * np.cos(a), cy + r1 * np.sin(a)) for a in ang]
    pts += [(cx + r0 * np.cos(a), cy + r0 * np.sin(a)) for a in ang[::-1]]
    d.polygon(pts, fill=255)
    return m


def ring_mask(cx, cy, r0, r1):
    m = Image.new("L", (BW, BH), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((cx - r1, cy - r1, cx + r1, cy + r1), fill=255)
    d.ellipse((cx - r0, cy - r0, cx + r0, cy + r0), fill=0)
    return m


def arc_band_mask(cx, cy, r0, r1, a0=180, a1=360):
    return wedge_mask(cx, cy, r0, r1, a0, a1, steps=200)


def place(base, mask, stops, band=0.0, ol=(10, 12, 14), olw=2):
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))   # edge AA
    if ol:
        outline(base, mask, ol, olw)
    base.alpha_composite(metal(mask, stops, band))


def font(name, size):
    return ImageFont.truetype(os.path.join(AF, name), size)


# =======================================================================
# Design 1 — SUNBURST (rising-sun deco fan)
# =======================================================================
def design_sunburst(ground=None):
    im = bg(ground or EMERALD_BG).convert("RGBA")
    cx, cy = BW // 2, int(BH * 0.605)
    R = int(BW * 0.40)

    # concentric arc bands behind the rays
    for r0f, r1f, st in [(0.99, 1.03, GOLD), (0.915, 0.965, CHROME), (0.845, 0.885, GOLD)]:
        place(im, arc_band_mask(cx, cy, int(R * r0f), int(R * r1f)), st, band=0.1)

    # fan of rays (alternating chrome / gold), spanning 180deg
    n = 17
    a = np.linspace(180, 360, n + 1)
    gap = 1.0
    for i in range(n):
        st = CHROME if i % 2 == 0 else GOLD
        m = wedge_mask(cx, cy, int(R * 0.10), int(R * 0.82), a[i] + gap, a[i + 1] - gap)
        place(im, m, st, band=0.05 * (i % 3))

    # central half-disc sun
    place(im, wedge_mask(cx, cy, 0, int(R * 0.13), 180, 360), GOLD, band=0.1)
    place(im, arc_band_mask(cx, cy, int(R * 0.125), int(R * 0.15)), CHROME)

    # ---- stepped deco plinth below the baseline (fills lower third) ----
    d = ImageDraw.Draw(im)
    d.line([(int(BW * 0.10), cy), (int(BW * 0.90), cy)], fill=hx("#e9d9a6"), width=6 * SS)
    tiers = [(0.80, GOLD), (0.62, CHROME), (0.44, GOLD)]
    ty = cy + int(BH * 0.015)
    th = int(BH * 0.032)
    for wf, st in tiers:
        half = int(BW * wf / 2)
        m = Image.new("L", (BW, BH), 0)
        ImageDraw.Draw(m).rectangle((cx - half, ty, cx + half, ty + th), fill=255)
        place(im, m, st, band=0.1)
        ty += th + int(BH * 0.014)
    # emerald diamond finial centered on the plinth
    jy = ty + int(BH * 0.02); s = int(BW * 0.05)
    d.polygon([(cx, jy - s), (cx + s, jy), (cx, jy + s), (cx - s, jy)],
              fill=hx("#1f9e7f"), outline=hx("#eaf5ef"), width=4 * SS)
    d.polygon([(cx, jy - s // 2), (cx + s // 2, jy), (cx, jy + s // 2), (cx - s // 2, jy)],
              fill=hx("#4fd0ad"))
    return finish(im, "I")


# =======================================================================
# Design 2 — STEPPED ARCHES (deco skyscraper doorway)
# =======================================================================
def design_arches(ground=None):
    im = bg(ground or INK_BG).convert("RGBA")
    cx = BW // 2
    widths = [0.62, 0.50, 0.385, 0.275, 0.17]
    stops = [GOLD, CHROME, GOLD, CHROME, GOLD]
    outer_half = int(BW * widths[0] / 2)
    top = int(BW * 0.05 + outer_half + BH * 0.02)   # outer crown just below top border
    base_y = int(BH * 0.84)
    step = int((base_y - top) * 0.085)
    thick = int(BW * 0.035)
    crown_inner = top
    for i, (wf, st) in enumerate(zip(widths, stops)):
        half = int(BW * wf / 2)
        r = half
        ay = top + i * step
        crown_inner = ay - r
        m = Image.new("L", (BW, BH), 0)
        dd = ImageDraw.Draw(m)
        dd.ellipse((cx - half, ay - r, cx + half, ay + r), fill=255)
        dd.ellipse((cx - half + thick, ay - r + thick, cx + half - thick, ay + r + thick), fill=0)
        dd.rectangle((0, ay, BW, BH), fill=0)          # keep upper half
        dd.rectangle((cx - half, ay, cx - half + thick, base_y), fill=255)   # legs
        dd.rectangle((cx + half - thick, ay, cx + half, base_y), fill=255)
        place(im, m, st, band=0.06 * i)

    # emerald keystone jewel seated in the innermost opening
    d = ImageDraw.Draw(im)
    jy = crown_inner + int(BH * 0.055); s = int(BW * 0.043)
    d.polygon([(cx, jy - s), (cx + s, jy), (cx, jy + s), (cx - s, jy)],
              fill=hx("#1f9e7f"), outline=hx("#eaf5ef"), width=4 * SS)
    d.polygon([(cx, jy - s // 2), (cx + s // 2, jy), (cx, jy + s // 2), (cx - s // 2, jy)],
              fill=hx("#4fd0ad"))
    d.line([(int(BW * 0.14), base_y), (int(BW * 0.86), base_y)], fill=hx("#d9b45a"), width=7 * SS)
    return finish(im, "II")


# =======================================================================
# Design 3 — ROSETTE (deco rose-window medallion)
# =======================================================================
def design_rosette(ground=None):
    im = bg(ground or SAPPHIRE_BG).convert("RGBA")
    cx, cy = BW // 2, int(BH * 0.50)
    R = int(BW * 0.42)

    for r0f, r1f, st in [(1.0, 1.04, GOLD), (0.93, 0.965, CHROME)]:
        place(im, ring_mask(cx, cy, int(R * r0f), int(R * r1f)), st, band=0.1)

    # petals (full 360) alternating metals
    n = 24
    a = np.linspace(0, 360, n + 1)
    for i in range(n):
        st = CHROME if i % 2 == 0 else GOLD
        m = wedge_mask(cx, cy, int(R * 0.34), int(R * 0.9), a[i] + 1.0, a[i + 1] - 1.0)
        place(im, m, st, band=0.04 * (i % 4))
    # inner ring
    place(im, ring_mask(cx, cy, int(R * 0.30), int(R * 0.335)), GOLD, band=0.1)
    # inner rays
    n2 = 12
    a2 = np.linspace(0, 360, n2 + 1)
    for i in range(n2):
        st = GOLD if i % 2 == 0 else CHROME
        m = wedge_mask(cx, cy, int(R * 0.08), int(R * 0.29), a2[i] + 1.4, a2[i + 1] - 1.4)
        place(im, m, st, band=0.05 * (i % 2))
    # emerald center cabochon
    d = ImageDraw.Draw(im)
    rr = int(R * 0.075)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=hx("#1f9e7f"), outline=hx("#eaf5ef"), width=4 * SS)
    d.ellipse((cx - int(rr * 0.5), cy - int(rr * 0.6), cx + int(rr * 0.15), cy - int(rr * 0.05)),
              fill=hx("#7fe0c3"))
    return finish(im, "III")


# ---- shared finish: frame + title plate ---------------------------------
def finish(im, numeral):
    d = ImageDraw.Draw(im)
    m = int(BW * 0.05)
    d.rectangle((m, m, BW - m, BH - m), outline=hx("#caa143"), width=4 * SS)
    d.rectangle((m + 14 * SS, m + 14 * SS, BW - m - 14 * SS, BH - m - 14 * SS),
                outline=hx("#6f7b85"), width=2 * SS)
    # corner deco ticks
    for (x, y) in [(m, m), (BW - m, m), (m, BH - m), (BW - m, BH - m)]:
        d.ellipse((x - 10 * SS, y - 10 * SS, x + 10 * SS, y + 10 * SS), fill=hx("#caa143"))
    # downscale
    return im.convert("RGB").resize((W, H), Image.LANCZOS)


# extra jewel-tone grounds (each becomes its own per-palette listing)
GROUNDS = {
    "ruby":     [(0.0, "#4c1020"), (0.5, "#5e1626"), (1.0, "#350a15")],
    "onyx":     [(0.0, "#191511"), (0.5, "#221d17"), (1.0, "#0c0a08")],
    "amethyst": [(0.0, "#2d1747"), (0.5, "#392058"), (1.0, "#1b0f2e")],
    "emerald":  EMERALD_BG,   # the original mixed set uses these three
    "midnight": INK_BG,
    "sapphire": SAPPHIRE_BG,
}

MOTIFS = [("01_sunburst", design_sunburst), ("02_arches", design_arches),
          ("03_rosette", design_rosette)]


def build():
    """the original mixed-ground set (emerald / midnight / sapphire)."""
    for (name, fn), ground in zip(MOTIFS, [EMERALD_BG, INK_BG, SAPPHIRE_BG]):
        print("rendering", name)
        fn(ground).save(os.path.join(MAST, f"{name}.png"))


def build_palette(pal):
    """render all three motifs on one jewel ground -> masters/<pal>_*.png"""
    ground = GROUNDS[pal]
    out = os.path.join(MAST, pal); os.makedirs(out, exist_ok=True)
    for name, fn in MOTIFS:
        print("rendering", pal, name)
        fn(ground).save(os.path.join(out, f"{name}.png"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for pal in sys.argv[1:]:
            build_palette(pal)
    else:
        build()
