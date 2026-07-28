"""
mug_designs.py — MUG-NATIVE math artwork for MathRelaxing (Printify 11oz wrap)
=============================================================================
Every design is engineered for the cylinder: the print is a 360° horizontal
band whose math is *periodic*, so it meets itself seamlessly at the handle seam
and "completes" as you rotate the mug. This is the whole differentiator — these
cannot be done as a centered slap-on PNG.

Print area target: 11oz mug wrap ≈ 2775 × 1155 px (9.25 × 3.85 in @ 300 dpi).
The band bleeds to the left & right edges (no side margin) so the wrap is
continuous; content stays inside the vertical safe area.

  python printify/mug_designs.py            # render all wraps + mockups
  python printify/mug_designs.py unrolled   # one design

Designs: unrolled · fourier · harmonics
"""
from __future__ import annotations
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "lulu_books", "assets", "fonts")
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUT = os.path.join(HERE, "_mug_art"); os.makedirs(OUT, exist_ok=True)

# 11oz mug wrap, rendered at 2x supersample then downscaled
W, H = 2775, 1155
SS = 2

# palette — print on white ceramic
WHITE = (255, 255, 255)
INK   = (28, 43, 58)     # navy
SOFT  = (92, 104, 116)
MUTE  = (170, 178, 186)
GOLD  = (176, 134, 47)
FAINT = (214, 210, 200)


def _f(path, size):   return ImageFont.truetype(path, size)
DEJAVU_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
def CIN(s):  return _f(os.path.join(FONTS, "Cinzel-SemiBold.ttf"), s)
def RAL(s):  return _f(os.path.join(FONTS, "Raleway.ttf"), s)
def RALI(s): return _f(os.path.join(FONTS, "Raleway-Italic.ttf"), s)
def SYM(s):  return _f(DEJAVU, s)              # Greek / math glyphs (θ π …)
def SERI(s): return _f(DEJAVU_SERIF, s)        # serif italic w/ Greek (titles)


def _title_sin_theta(d, cx, cy, size):
    """Draw 'sin θ' centred at (cx,cy): 'sin' in Cinzel, 'θ' in serif italic."""
    fa, fb = CIN(size), SERI(int(size*1.02))
    wa = d.textlength("sin ", font=fa); wb = d.textlength("θ", font=fb)
    x0 = cx - (wa + wb) / 2
    d.text((x0, cy), "sin ", font=fa, fill=INK, anchor="lm")
    d.text((x0 + wa, cy), "θ", font=fb, fill=INK, anchor="lm")


def _canvas():
    im = Image.new("RGB", (W*SS, H*SS), WHITE)
    return im, ImageDraw.Draw(im)


def _poly(xs, ys):
    return list(zip(xs.tolist(), ys.tolist()))


def _finish(im, name):
    im = im.resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
    p = os.path.join(OUT, f"mug_{name}_wrap.png")
    im.save(p, "PNG", optimize=True)
    print(f"  wrap  {name:10s} -> {os.path.basename(p)} ({W}x{H})")
    return p


def _brand(d, s):
    # bottom brand line, centered
    d.text((W*SS//2, int(H*SS*0.90)), "M A T H R E L A X I N G",
           font=RAL(int(20*SS)), fill=SOFT, anchor="mm")


# ── design 1: UNROLLED — unit circle → one full sine period ────────────────────
def d_unrolled():
    im, d = _canvas(); w, h = W*SS, H*SS
    mid = int(h*0.55)
    amp = int(h*0.26)
    # baseline
    d.line([(0, mid), (w, mid)], fill=FAINT, width=SS)
    # tick grid at 0, π/2, π, 3π/2, 2π
    labels = ["0", "π/2", "π", "3π/2", "2π"]
    for i, lab in enumerate(labels):
        x = int(w * i / 4)
        xx = min(max(x, SS), w-SS)
        d.line([(xx, mid-14*SS), (xx, mid+14*SS)], fill=MUTE, width=SS)
        d.text((xx, mid+40*SS), lab, font=SYM(int(30*SS)),
               fill=SOFT, anchor="ma" if 0 < i < 4 else ("la" if i == 0 else "ra"))
    # one full sine period across the whole wrap (seamless: sin0 = sin2π = 0)
    xs = np.linspace(0, w, 3000)
    ys = mid - amp*np.sin(2*np.pi*xs/w)
    d.line(_poly(xs, ys), fill=INK, width=int(9*SS), joint="curve")
    # unit circle "key" on the left
    ccx, ccy, cr = int(w*0.115), mid, amp
    d.ellipse([ccx-cr, ccy-cr, ccx+cr, ccy+cr], outline=GOLD, width=int(5*SS))
    d.line([(ccx-cr, ccy), (ccx+cr, ccy)], fill=FAINT, width=SS)
    d.line([(ccx, ccy-cr), (ccx, ccy+cr)], fill=FAINT, width=SS)
    th = np.radians(52)
    px, py = ccx+cr*np.cos(th), ccy-cr*np.sin(th)
    d.line([(ccx, ccy), (px, py)], fill=INK, width=int(5*SS))       # radius
    d.ellipse([px-11*SS, py-11*SS, px+11*SS, py+11*SS], fill=GOLD)  # point
    # dotted projection: circle point height -> onto the wave
    for xd in range(int(ccx), int(w*0.30), int(26*SS)):
        d.ellipse([xd-2*SS, py-2*SS, xd+2*SS, py+2*SS], fill=MUTE)
    # captions
    _title_sin_theta(d, int(w*0.5), int(h*0.14), int(64*SS))
    d.text((int(w*0.5), int(h*0.235)), "one turn of the mug — one full wave",
           font=RALI(int(30*SS)), fill=SOFT, anchor="mm")
    _brand(d, "unrolled")
    return _finish(im, "unrolled")


# ── design 2: FOURIER — a square wave built from its odd harmonics ─────────────
def d_fourier():
    im, d = _canvas(); w, h = W*SS, H*SS
    mid = int(h*0.56); amp = int(h*0.24)
    d.line([(0, mid), (w, mid)], fill=FAINT, width=SS)
    xs = np.linspace(0, w, 4000)
    t = 2*np.pi*xs/w                     # one fundamental period across the wrap
    # faint individual harmonics k = 1,3,5,7
    ktones = [1, 3, 5, 7]
    for k in ktones:
        yk = mid - amp*(4/np.pi)*(np.sin(k*t)/k)
        shade = tuple(int(c) for c in (np.array(MUTE)*0.6 + np.array(WHITE)*0.4))
        d.line(_poly(xs, yk), fill=shade, width=int(3*SS), joint="curve")
    # bold partial sum -> square wave
    ssum = np.zeros_like(t)
    for k in ktones:
        ssum += np.sin(k*t)/k
    ys = mid - amp*(4/np.pi)*ssum
    d.line(_poly(xs, ys), fill=INK, width=int(9*SS), joint="curve")
    # the ideal square (gold, thin) it converges to
    sq = mid - amp*np.sign(np.sin(t))
    d.line(_poly(xs, sq), fill=GOLD, width=int(3*SS), joint="curve")
    d.text((int(w*0.5), int(h*0.13)), "Fourier Series", font=CIN(int(60*SS)), fill=INK, anchor="mm")
    d.text((int(w*0.5), int(h*0.225)),
           "a square wave, summed from its harmonics — seamless around the turn",
           font=RALI(int(29*SS)), fill=SOFT, anchor="mm")
    # formula
    d.text((int(w*0.5), int(h*0.86)), "f(x) = Σ  sin((2k−1)x) / (2k−1)",
           font=SYM(int(34*SS)), fill=SOFT, anchor="mm")
    _brand(d, "fourier")
    return _finish(im, "fourier")


# ── design 3: HARMONICS — standing modes of a string, nodes at the seam ────────
def d_harmonics():
    im, d = _canvas(); w, h = W*SS, H*SS
    modes = [1, 2, 3, 4, 5]
    top, bot = int(h*0.30), int(h*0.86)
    band = (bot - top) / len(modes)
    xs = np.linspace(0, w, 3000)
    ords = ["1st", "2nd", "3rd", "4th", "5th"]
    for i, n in enumerate(modes):
        cy = int(top + band*(i+0.5)); a = int(band*0.34)
        d.line([(0, cy), (w, cy)], fill=FAINT, width=SS)
        # standing mode sin(nπ x/L): both ends = 0 -> seamless at the seam
        env = a*np.sin(n*np.pi*xs/w)
        d.line(_poly(xs, cy - env), fill=INK, width=int(6*SS), joint="curve")
        d.line(_poly(xs, cy + env), fill=(150,160,170), width=int(2*SS), joint="curve")
        # nodes (gold dots) where the mode crosses zero
        for kk in range(n+1):
            nx = int(w*kk/n); nx = min(max(nx, 4*SS), w-4*SS)
            d.ellipse([nx-7*SS, cy-7*SS, nx+7*SS, cy+7*SS], fill=GOLD)
        d.text((int(28*SS), cy), ords[i], font=RAL(int(24*SS)), fill=SOFT, anchor="lm")
    d.text((int(w*0.5), int(h*0.135)), "Harmonics", font=CIN(int(58*SS)), fill=INK, anchor="mm")
    d.text((int(w*0.5), int(h*0.225)), "the vibrating string — its first five modes",
           font=RALI(int(28*SS)), fill=SOFT, anchor="mm")
    _brand(d, "harmonics")
    return _finish(im, "harmonics")


DESIGNS = {"unrolled": d_unrolled, "fourier": d_fourier, "harmonics": d_harmonics}


# ── mockup: wrap the band onto a 3D-ish mug ────────────────────────────────────
def mockup(name):
    wrap = Image.open(os.path.join(OUT, f"mug_{name}_wrap.png")).convert("RGB")
    ww, wh = wrap.size
    # canvas
    CW, CH = 1600, 1300
    bg = Image.new("RGB", (CW, CH), (238, 235, 229))
    # mug body geometry — classic 11oz proportions (slightly taller than wide)
    bw, bh = 720, 800
    bx, by = (CW - bw)//2 - 70, (CH - bh)//2 + 20
    # visible front spans ~150° of the wrap; sample its centre slice with cosine
    # compression so the band foreshortens toward the mug's sides.
    face = wrap.crop((int(ww*0.16), 0, int(ww*0.84), wh))
    fw, fh = face.size
    src = np.asarray(face).astype(np.float32)
    band_h = int(bh*0.66)
    band = np.zeros((band_h, bw, 3), np.float32)
    phi_max = np.radians(74)
    for j in range(bw):
        phi = (j/(bw-1) - 0.5) * 2 * phi_max
        u = 0.5 + np.sin(phi)/(2*np.sin(phi_max))          # cosine edge compression
        sx = min(max(u*(fw-1), 0), fw-1)
        col = src[:, int(sx), :]
        # resize column height
        col_img = np.interp(np.linspace(0, fh-1, band_h), np.arange(fh), col[:, 0])
        g = np.interp(np.linspace(0, fh-1, band_h), np.arange(fh), col[:, 1])
        b = np.interp(np.linspace(0, fh-1, band_h), np.arange(fh), col[:, 2])
        shade = 0.68 + 0.32*np.cos(phi)                     # cylinder lighting
        band[:, j, 0] = col_img*shade
        band[:, j, 1] = g*shade
        band[:, j, 2] = b*shade
    band_img = Image.fromarray(np.clip(band, 0, 255).astype(np.uint8))

    # mug body (white ceramic) with soft cylinder shading
    body = Image.new("RGB", (bw, bh), (250, 249, 247))
    bd = ImageDraw.Draw(body)
    for j in range(bw):
        phi = (j/(bw-1) - 0.5) * 2 * phi_max
        sh = 0.80 + 0.20*np.cos(phi)
        c = int(250*sh)
        bd.line([(j, 0), (j, bh)], fill=(c, c-1, c-3))
    # rounded mask for the body + rim/base ellipses
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 40, bw-1, bh-40], radius=70, fill=255)
    md.ellipse([0, 0, bw-1, 80], fill=255)          # top rim
    md.ellipse([0, bh-80, bw-1, bh-1], fill=255)    # base
    # drop shadow
    sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([bx+70, by+bh-30, bx+bw-10, by+bh+70], fill=(60, 55, 48, 120))
    bg = Image.alpha_composite(bg.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(22))).convert("RGB")
    # handle (ring on the right)
    hd = ImageDraw.Draw(bg)
    hx, hy = bx+bw-40, by+bh//2
    hd.ellipse([hx-30, hy-150, hx+180, hy+150], outline=(232, 230, 226), width=54)
    hd.ellipse([hx-30, hy-150, hx+180, hy+150], outline=(214, 211, 205), width=6)
    # paste body then band
    bg.paste(body, (bx, by), mask)
    band_x = bx + (bw - band_img.width)//2
    band_y = by + (bh - band_img.height)//2 + 6
    bandmask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(bandmask).rounded_rectangle([0, 40, bw-1, bh-40], radius=70, fill=255)
    # only paste band where body is
    bmask = bandmask.crop((0, 0, band_img.width, band_img.height)) if False else None
    bg.paste(band_img, (band_x, band_y), Image.new("L", band_img.size, 255))
    # rim highlight
    rd = ImageDraw.Draw(bg)
    rd.ellipse([bx, by, bx+bw-1, by+80], outline=(226, 223, 218), width=5)
    rd.ellipse([bx+16, by+8, bx+bw-17, by+66], outline=(244, 243, 240), width=3)

    p = os.path.join(OUT, f"mug_{name}_mockup.jpg")
    bg.save(p, "JPEG", quality=92)
    print(f"  mockup {name:10s} -> {os.path.basename(p)}")
    return p


if __name__ == "__main__":
    keys = [sys.argv[1]] if len(sys.argv) > 1 else list(DESIGNS)
    for k in keys:
        DESIGNS[k]()
        mockup(k)
    print("DONE")
