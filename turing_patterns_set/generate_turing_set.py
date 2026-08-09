"""
generate_turing_set.py — "Turing Patterns" reaction-diffusion plate set
==========================================================================
Six computed Gray-Scott fields (see generate_turing_field.py), each
colour-graded to evoke the real creature whose skin/shell shows that
pattern class, printed full-bleed on a dark ground with gold linework --
the same "premium dark plate" family as the History-of-X posters, but
built around a filled organic texture instead of timeline linework.

  python generate_turing_set.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(BASE, "fields")
PLATES = os.path.join(BASE, "plates")
os.makedirs(PLATES, exist_ok=True)

AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")
CINZEL = os.path.join(AF, "Cinzel-SemiBold.ttf")
CINZEL_R = os.path.join(AF, "Cinzel.ttf")
RALEWAY = os.path.join(AF, "Raleway.ttf")
RALEWAY_I = os.path.join(AF, "Raleway-Italic.ttf")

DARK = "#0a0b0d"
CREAM = "#f0ece0"
SUB = "#9a9484"
GOLD = "#c9a24b"
GOLD_HI = "#f3dfa0"

DPI = 300
W_IN, H_IN = 9.0, 11.5
W_PX, H_PX = round(W_IN * DPI), round(H_IN * DPI)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


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


def colorize(field01, stops):
    """field01: (h,w) float array in [0,1]. stops: list of hex colors,
    evenly spaced, linearly interpolated per-channel."""
    stops_rgb = np.array([hx(s) for s in stops], dtype=np.float32)
    n = len(stops_rgb)
    pos = field01 * (n - 1)
    lo = np.clip(np.floor(pos).astype(int), 0, n - 2)
    t = (pos - lo)[..., None]
    rgb = stops_rgb[lo] * (1 - t) + stops_rgb[lo + 1] * t
    return rgb.astype(np.uint8)


def render_pattern(slug, stops, blur=1.1, w_px=None, h_px=None):
    w_px, h_px = w_px or W_PX, h_px or H_PX
    field = np.load(os.path.join(FIELDS, f"{slug}.npy"))
    rgb = colorize(field, stops)
    img = Image.fromarray(rgb, "RGB").resize((w_px, h_px), Image.LANCZOS)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return img


def vertical_scrim(w, h, top_frac, bot_frac, top_strength=0.82, bot_strength=0.88):
    """Black gradient, strong at top/bottom edges, transparent in the middle,
    so title/caption text stays legible over a busy full-bleed texture."""
    alpha = np.zeros(h, dtype=np.float32)
    top_n = int(h * top_frac)
    bot_n = int(h * bot_frac)
    alpha[:top_n] = np.linspace(top_strength, 0, top_n)
    alpha[h - bot_n:] = np.linspace(0, bot_strength, bot_n)
    scrim = np.zeros((h, w, 4), dtype=np.uint8)
    scrim[..., 3] = (alpha[:, None] * 255).astype(np.uint8)
    return Image.fromarray(scrim, "RGBA")


MARGIN = 90
REF_H = H_PX  # chrome (margins, font sizes, line widths) was tuned against this
              # reference height; build_plate() scales everything relative to it
              # so a same-looking plate can be rendered at other resolutions/ratios.


def build_plate(spec_no, title, eyebrow_right, caption, footer_items, slug, stops,
                 w_px=None, h_px=None):
    w_px, h_px = w_px or W_PX, h_px or H_PX
    s = h_px / REF_H  # uniform scale factor for every absolute pixel constant below

    def sc(v):
        return round(v * s)

    canvas = render_pattern(slug, stops, blur=1.1 * s, w_px=w_px, h_px=h_px).convert("RGBA")
    scrim = vertical_scrim(w_px, h_px, top_frac=0.30, bot_frac=0.34)
    canvas.alpha_composite(scrim)
    canvas = canvas.convert("RGB")
    d = ImageDraw.Draw(canvas)
    gold = hx(GOLD)
    cream = hx(CREAM)
    sub = hx(SUB)
    margin = sc(MARGIN)

    # hairline inset border + corner marks
    d.rectangle([margin, margin, w_px - margin, h_px - margin], outline=gold, width=max(1, sc(2)))
    arm = sc(30)
    for cx0, cy0 in [(margin, margin), (w_px - margin, margin),
                     (margin, h_px - margin), (w_px - margin, h_px - margin)]:
        d.line([cx0 - arm, cy0, cx0 + arm, cy0], fill=gold, width=max(1, sc(1)))
        d.line([cx0, cy0 - arm, cx0, cy0 + arm], fill=gold, width=max(1, sc(1)))

    # eyebrow row
    ey = margin + sc(54)
    f_eyebrow = font(RALEWAY, sc(28))
    draw_tracked(d, (margin + sc(56), ey), "MATHRELAXING · TURING PATTERNS", f_eyebrow, sub, tracking=sc(3))
    draw_tracked(d, (w_px - margin - sc(56), ey), eyebrow_right, f_eyebrow, sub, tracking=sc(3), anchor="r")

    # title
    f_title = font(CINZEL, sc(96))
    ty = margin + sc(120)
    draw_tracked(d, (w_px // 2, ty), title.upper(), f_title, cream, tracking=sc(8), anchor="m")
    rule_w = sc(150)
    d.rectangle([w_px // 2 - rule_w // 2, ty + sc(118), w_px // 2 + rule_w // 2, ty + sc(122)], fill=gold)

    # caption block, bottom
    f_cap = font(RALEWAY_I, sc(42))
    max_w = w_px - 2 * (margin + sc(260))
    lines = wrap_text(d, caption, f_cap, max_w)
    line_h = sc(56)
    cap_h = len(lines) * line_h
    cap_y = h_px - margin - sc(300) - cap_h
    for ln in lines:
        w = d.textbbox((0, 0), ln, font=f_cap)[2]
        d.text((w_px // 2 - w / 2, cap_y), ln, font=f_cap, fill=cream)
        cap_y += line_h

    # footer museum-label strip
    fy0 = h_px - margin - sc(190)
    d.line([margin + sc(60), fy0, w_px - margin - sc(60), fy0], fill=gold, width=max(1, sc(1)))
    n = len(footer_items)
    col_w = (w_px - 2 * (margin + sc(60))) / n
    f_val = font(CINZEL_R, sc(40))
    f_key = font(RALEWAY, sc(25))
    for i, (val, key) in enumerate(footer_items):
        cx = margin + sc(60) + col_w * i + col_w / 2
        draw_tracked(d, (cx, fy0 + sc(34)), val, f_val, hx(GOLD_HI), tracking=sc(1), anchor="m")
        draw_tracked(d, (cx, fy0 + sc(90)), key.upper(), f_key, sub, tracking=sc(2), anchor="m")
        if i > 0:
            d.line([margin + sc(60) + col_w * i, fy0 + sc(20), margin + sc(60) + col_w * i, fy0 + sc(130)],
                   fill=(70, 66, 58), width=max(1, sc(1)))

    f_id = font(RALEWAY, sc(22))
    draw_tracked(d, (w_px // 2, h_px - margin - sc(46)),
                 f"SPECIMEN {spec_no:02d} / 06  ·  GRAY-SCOTT MODEL  ·  MATHRELAXING",
                 f_id, sub, tracking=sc(2), anchor="m")

    return canvas


PLATE_SPECS = [
    dict(spec_no=1, fname="01_leopard_rosettes.jpg", title="Leopard Rosettes", eyebrow="FIG. 01",
         slug="leopard_rosettes", stops=["#180f06", "#7a4a12", "#d8912f", "#f6d488"],
         caption="Two chemicals, one rule: activate nearby, inhibit at a distance -- "
                  "the spots assemble themselves, no blueprint required.",
         footer=[("F=0.0367, K=0.0649", "gray-scott params"), ("SELF-REPLICATING", "spot regime"), ("A. TURING, 1952", "morphogenesis")]),
    dict(spec_no=2, fname="02_pufferfish_mesh.jpg", title="Pufferfish Mesh", eyebrow="FIG. 02",
         slug="pufferfish_mesh", stops=["#04141a", "#0d4a52", "#2fa9ab", "#c8f3ec"],
         caption="Where the inhibitor gets the upper hand, a hole opens in the field -- "
                  "and the reaction keeps it open, permanently.",
         footer=[("F=0.039, K=0.058", "gray-scott params"), ("TURING HOLES", "spot regime"), ("REACTION-DIFFUSION", "pde class")]),
    dict(spec_no=3, fname="03_brain_coral.jpg", title="Brain Coral", eyebrow="FIG. 03",
         slug="brain_coral", stops=["#170a0c", "#6e2233", "#d85b4a", "#f8c3a0"],
         caption="Neither maze nor accident: the ridges grow to fill every inch of "
                  "space while never quite touching themselves.",
         footer=[("F=0.0545, K=0.062", "gray-scott params"), ("LABYRINTHINE", "growth regime"), ("MEINHARDT, 1982", "theory of growth")]),
    dict(spec_no=4, fname="04_tiger_current.jpg", title="Tiger Current", eyebrow="FIG. 04",
         slug="tiger_current", stops=["#0d0704", "#4a1707", "#c9481c", "#f7b23e"],
         caption="The pattern never sits still. Every stripe drifts, forks, and "
                  "re-forms for as long as the reaction keeps running.",
         footer=[("F=0.022, K=0.051", "gray-scott params"), ("TRAVELING STRIPES", "worm regime"), ("MURRAY, 1981", "tiger-stripe model")]),
    dict(spec_no=5, fname="05_fingerprint_whorl.jpg", title="Fingerprint Whorl", eyebrow="FIG. 05",
         slug="fingerprint_whorl", stops=["#05070d", "#1c3350", "#5a83ad", "#e4edf6"],
         caption="The same instability that ridges your fingertip ridges this page -- "
                  "the same mathematics, run just a little tighter.",
         footer=[("F=0.058, K=0.063", "gray-scott params"), ("DENSE MAZE", "fine regime"), ("KUCERA & BARRETT", "dermatoglyphics")]),
    dict(spec_no=6, fname="06_cuttlefish_static.jpg", title="Cuttlefish Static", eyebrow="FIG. 06",
         slug="cuttlefish_static", stops=["#0c0714", "#3b1a4d", "#9a3f8f", "#e8b3dd"],
         caption="Right at the edge of collapse, spots merge and scatter -- the "
                  "chemical equivalent of a cuttlefish changing its camouflage.",
         footer=[("F=0.018, K=0.051", "gray-scott params"), ("COALESCING CHAOS", "unstable regime"), ("EDGE OF PATTERN", "bifurcation")]),
]


def save_plate(canvas, name):
    out = os.path.join(PLATES, name)
    canvas.save(out, "JPEG", quality=93)
    print("wrote", out, canvas.size)


def build():
    for spec in PLATE_SPECS:
        canvas = build_plate(
            spec_no=spec["spec_no"], title=spec["title"], eyebrow_right=spec["eyebrow"],
            caption=spec["caption"], footer_items=spec["footer"], slug=spec["slug"], stops=spec["stops"],
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
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad), "#0a0b0d")
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (pad + c * (cw + pad), pad + r * (ch + pad)))
    sheet.save(os.path.join(BASE, "_contact_sheet.jpg"), quality=90)
    print("contact sheet ->", os.path.join(BASE, "_contact_sheet.jpg"))


if __name__ == "__main__":
    build()
    contact_sheet()
    print("DONE")
