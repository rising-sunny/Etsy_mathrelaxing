"""
Visual layer for The Mathematician's Vault: parchment texture, a rendered brass vault
door for the cover, brass plaques and a padlock icon.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PAPER = (244, 236, 218); NAVY = (26, 36, 62); GOLD = (184, 140, 62); CREAM = (246, 238, 220)
BRASS_DARK = (96, 66, 26); BRASS = (196, 152, 70); BRASS_LIGHT = (252, 222, 150)
_cache = {}


def _noise(w, h, scale, seed):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(float) / 255


def parchment(size):
    if size in _cache:
        return _cache[size].copy()
    W, H = size
    n = 0.55 * _noise(W, H, 160, 1) + 0.30 * _noise(W, H, 40, 2) + 0.15 * np.random.default_rng(3).random((H, W))
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = np.clip((r - 0.75) / 0.6, 0, 1) ** 1.6
    base = np.array(PAPER, float)
    img = base[None, None, :] * (0.955 + 0.07 * n[..., None]) - vig[..., None] * np.array([46, 50, 58])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    _cache[size] = im
    return im.copy()


def brass_ring(img, cx, cy, r0, r1, light=(-0.6, -0.8)):
    """Bevelled brass ring between radii r0 < r1, shaded by a light direction (numpy)."""
    W, H = img.size; x0, y0 = int(cx - r1 - 2), int(cy - r1 - 2); x1, y1 = int(cx + r1 + 2), int(cy + r1 + 2)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float); dx, dy = xx - cx, yy - cy; r = np.sqrt(dx * dx + dy * dy) + 1e-9
    t = (r - r0) / (r1 - r0); m = (t >= 0) & (t <= 1)
    nr = np.cos(np.pi * np.clip(t, 0, 1))  # +1 inner edge rising, -1 outer edge falling
    nx, ny = dx / r * -nr, dy / r * -nr
    lx, ly = light; lam = np.clip(0.55 + 0.45 * (nx * lx + ny * ly) + 0.12 * (1 - abs(nr)), 0, 1.2)
    col = np.array(BRASS_DARK, float)[None, None] + (np.array(BRASS_LIGHT, float) - np.array(BRASS_DARK, float))[None, None] * np.clip(lam, 0, 1)[..., None]
    patch = np.asarray(img.crop((x0, y0, x1, y1))).astype(float)
    a = np.clip(np.minimum(t, 1 - t) * (r1 - r0) / 1.5, 0, 1)[..., None] * m[..., None]
    patch = patch * (1 - a) + col * a
    img.paste(Image.fromarray(patch.astype(np.uint8)), (x0, y0))


def brass_disc(img, cx, cy, r, light=(-0.6, -0.8), dark=(40, 52, 82), lightc=(78, 92, 126)):
    x0, y0 = int(cx - r - 2), int(cy - r - 2); x1, y1 = int(cx + r + 2), int(cy + r + 2)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float); dx, dy = (xx - cx) / r, (yy - cy) / r; rr = np.sqrt(dx * dx + dy * dy)
    m = rr <= 1; lam = np.clip(0.5 - 0.5 * (dx * light[0] + dy * light[1]) * -1, 0, 1)
    col = np.array(dark, float)[None, None] + (np.array(lightc, float) - np.array(dark, float))[None, None] * lam[..., None]
    patch = np.asarray(img.crop((x0, y0, x1, y1))).astype(float)
    a = np.clip((1 - rr) * r / 1.5, 0, 1)[..., None]
    patch = patch * (1 - a) + col * a
    img.paste(Image.fromarray(patch.astype(np.uint8)), (x0, y0))


def bolt(img, cx, cy, r):
    brass_disc(img, cx, cy, r, dark=(110, 78, 30), lightc=(250, 220, 150))
    ImageDraw.Draw(img).ellipse((cx - r, cy - r, cx + r, cy + r), outline=(70, 48, 18), width=max(2, int(r / 8)))


def vault_door(img, cx, cy, R, font):
    d = ImageDraw.Draw(img)
    sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).ellipse((cx - R + 30, cy - R + 50, cx + R + 30, cy + R + 50), fill=190)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(R * 0.08)))
    brass_ring(img, cx, cy, R * 0.80, R)                      # outer frame
    brass_disc(img, cx, cy, R * 0.80, dark=(30, 40, 66), lightc=(70, 84, 118))  # door plate
    for k in range(12):                                       # bolts
        a = 2 * math.pi * k / 12 + math.pi / 12
        bolt(img, cx + R * 0.90 * math.cos(a), cy + R * 0.90 * math.sin(a), R * 0.045)
    brass_ring(img, cx, cy, R * 0.58, R * 0.66)               # dial ring
    d = ImageDraw.Draw(img)
    for k in range(100):                                      # dial ticks + numbers
        a = -math.pi / 2 + 2 * math.pi * k / 100; long = k % 10 == 0
        r1 = R * (0.545 if long else 0.565)
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + R * 0.58 * math.cos(a), cy + R * 0.58 * math.sin(a)),
               fill=BRASS_LIGHT if long else BRASS, width=max(2, int(R * (0.012 if long else 0.006))))
        if long:
            s = str(k); f = font("bold", int(R * 0.055)); rr = R * 0.49
            d.text((cx + rr * math.cos(a) - d.textlength(s, font=f) / 2, cy + rr * math.sin(a) - f.size * 0.6), s, font=f, fill=CREAM)
    brass_disc(img, cx, cy, R * 0.40, dark=(24, 32, 54), lightc=(58, 70, 100))
    for k in range(3):                                        # handle wheel spokes
        a = -math.pi / 2 + 2 * math.pi * k / 3
        ex, ey = cx + R * 0.34 * math.cos(a), cy + R * 0.34 * math.sin(a)
        d.line((cx, cy, ex, ey), fill=BRASS_DARK, width=int(R * 0.07)); d.line((cx, cy, ex, ey), fill=BRASS, width=int(R * 0.045))
        bolt(img, ex, ey, R * 0.06)
    bolt(img, cx, cy, R * 0.12)
    d = ImageDraw.Draw(img)
    d.polygon([(cx, cy - R * 0.70), (cx - R * 0.03, cy - R * 0.76), (cx + R * 0.03, cy - R * 0.76)], fill=(200, 60, 50))  # index mark


FORMULAS = ["e^(iπ) + 1 = 0", "a² + b² = c²", "F(n) = F(n-1) + F(n-2)", "z² + c", "∫ e^x dx = e^x + C", "π ≈ 3.14159",
            "∑ 1/n² = π²/6", "(1 + √5) / 2", "V - E + F = 2", "lim (1 + 1/n)^n = e", "Δ = b² - 4ac", "x² + y² = r²",
            "1 + 2 + 3 + ... + n", "∞", "√2 ≈ 1.41421", "2^10 = 1024"]


def cover(size, font):
    W, H = size
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.36) / H) ** 2)
    base = np.array((34, 46, 78), float)[None, None] * (1 - np.clip(r * 1.35, 0, 0.82))[..., None] + np.array((8, 12, 24), float)[None, None] * np.clip(r * 1.35, 0, 0.82)[..., None]
    n = _noise(W, H, 90, 7)[..., None]; img = Image.fromarray(np.clip(base * (0.96 + 0.08 * n), 0, 255).astype(np.uint8))
    lay = Image.new("RGBA", size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); rnd = random.Random(4)
    for k in range(34):  # faint formulas, like the professor's notes
        s = FORMULAS[k % len(FORMULAS)]; f = font("light", rnd.randint(46, 92))
        x, y = rnd.uniform(-100, W - 200), rnd.uniform(0, H)
        ld.text((x, y), s, font=f, fill=(214, 176, 100, rnd.randint(18, 38)))
    img = Image.alpha_composite(img.convert("RGBA"), lay.rotate(-8, resample=Image.BICUBIC)).convert("RGB")
    d = ImageDraw.Draw(img)
    m = int(W * 0.04); d.rectangle((m, m, W - m, H - m), outline=GOLD, width=6); d.rectangle((m + 22, m + 22, W - m - 22, H - m - 22), outline=(120, 92, 46), width=2)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):  # art-deco corners
        x0 = m if sx > 0 else W - m; y0 = m if sy > 0 else H - m
        for k in range(3):
            o = 50 + k * 36
            d.line((x0 + sx * 22, y0 + sy * o, x0 + sx * o, y0 + sy * 22), fill=GOLD, width=4)
        d.regular_polygon((x0 + sx * 30, y0 + sy * 30, 16), 4, rotation=45, fill=GOLD)
    vault_door(img, W / 2, H * 0.305, W * 0.28, font); d = ImageDraw.Draw(img)

    def ct(y, s, f, col, spacing=0):
        if spacing:
            w = sum(d.textlength(ch, font=f) for ch in s) + spacing * (len(s) - 1); x = (W - w) / 2
            for ch in s:
                d.text((x, y), ch, font=f, fill=col); x += d.textlength(ch, font=f) + spacing
        else:
            d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=col)
    y = H * 0.56
    ct(y, "THE MATHEMATICIAN'S", font("cinzel", int(W * 0.05)), CREAM, spacing=10)
    fv = font("cinzel", int(W * 0.165)); s = "VAULT"; wv = d.textlength(s, font=fv)
    d.text(((W - wv) / 2 + 8, y + W * 0.055 + 12), s, font=fv, fill=(10, 14, 26))
    d.text(((W - wv) / 2, y + W * 0.055), s, font=fv, fill=BRASS_LIGHT)
    ly = y + W * 0.24
    for side in (-1, 1):
        x_in, x_out = W / 2 + side * W * 0.06, W / 2 + side * W * 0.33
        d.line((x_in, ly, x_out, ly), fill=GOLD, width=4); d.regular_polygon((x_in - side * 6, ly, 12), 4, rotation=45, fill=GOLD)
    rb_y = ly + W * 0.035; rb_w = W * 0.66; rb_h = W * 0.07  # ribbon
    d.polygon([(W / 2 - rb_w / 2 - 40, rb_y + rb_h / 2), (W / 2 - rb_w / 2, rb_y), (W / 2 + rb_w / 2, rb_y),
               (W / 2 + rb_w / 2 + 40, rb_y + rb_h / 2), (W / 2 + rb_w / 2, rb_y + rb_h), (W / 2 - rb_w / 2, rb_y + rb_h)], fill=(128, 40, 36))
    ct(rb_y + rb_h * 0.22, "A PRINTABLE ESCAPE ROOM FOR ADULTS", font("bold", int(W * 0.03)), CREAM)
    by = H * 0.835; bw = W * 0.22  # badges
    for i, (big, small) in enumerate((("9", "PUZZLES"), ("2-6", "PLAYERS"), ("60-90", "MINUTES"))):
        cx = W / 2 + (i - 1) * (bw + W * 0.04)
        d.rounded_rectangle((cx - bw / 2, by, cx + bw / 2, by + W * 0.085), radius=int(W * 0.04), outline=GOLD, width=4, fill=(18, 24, 44))
        fb = font("cinzel", int(W * 0.036)); fs = font("bold", int(W * 0.017))
        d.text((cx - d.textlength(big, font=fb) / 2, by + W * 0.008), big, font=fb, fill=BRASS_LIGHT)
        d.text((cx - d.textlength(small, font=fs) / 2, by + W * 0.055), small, font=fs, fill=CREAM)
    ct(H - m - W * 0.06, "MathRelaxing", font("cinzel_r", int(W * 0.022)), GOLD)
    return img


def plaque(d, x, y, text, font, W):
    f = font("bold", int(W * 0.019)); w = d.textlength(text, font=f) + 80; h = int(W * 0.045)
    d.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=(150, 112, 50), outline=(96, 66, 26), width=4)
    d.rounded_rectangle((x + 8, y + 8, x + w - 8, y + h - 8), radius=6, outline=(236, 204, 130), width=2)
    for bx in (x + 20, x + w - 20):
        d.ellipse((bx - 7, y + h / 2 - 7, bx + 7, y + h / 2 + 7), fill=(96, 66, 26))
    d.text((x + 40, y + (h - f.size) / 2 - 4), text, font=f, fill=(255, 244, 214))


def padlock(d, x, y, s, col=(236, 204, 130)):
    d.arc((x + s * 0.2, y, x + s * 0.8, y + s * 0.7), 180, 360, fill=col, width=max(3, int(s * 0.09)))
    d.line((x + s * 0.2, y + s * 0.35, x + s * 0.2, y + s * 0.5), fill=col, width=max(3, int(s * 0.09)))
    d.line((x + s * 0.8, y + s * 0.35, x + s * 0.8, y + s * 0.5), fill=col, width=max(3, int(s * 0.09)))
    d.rounded_rectangle((x, y + s * 0.45, x + s, y + s * 1.15), radius=int(s * 0.12), fill=col)
    d.ellipse((x + s * 0.42, y + s * 0.68, x + s * 0.58, y + s * 0.84), fill=(26, 36, 62))
    d.rectangle((x + s * 0.47, y + s * 0.8, x + s * 0.53, y + s * 0.98), fill=(26, 36, 62))
