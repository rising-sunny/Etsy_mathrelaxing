"""
generate_turing_set.py — "Turing Patterns" reaction-diffusion plate set
==========================================================================
Six computed Gray-Scott fields (see generate_turing_field.py), each
colour-graded to evoke the real creature whose skin/shell shows that
pattern class -- pure full-bleed pattern, no title/caption/border burned
into the art (that copy lives in the Etsy listing text instead).

  python generate_turing_set.py
"""
import os

import numpy as np
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(BASE, "fields")
PLATES = os.path.join(BASE, "plates")
os.makedirs(PLATES, exist_ok=True)

DPI = 300
W_IN, H_IN = 9.0, 11.5
W_PX, H_PX = round(W_IN * DPI), round(H_IN * DPI)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


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


def build_plate(slug, stops, w_px=None, h_px=None):
    """Pure full-bleed pattern -- no title/caption/footer/border. The plate
    metadata in PLATE_SPECS (title, caption, footer stats) still feeds the
    Etsy listing text; it's just not burned into the artwork itself."""
    return render_pattern(slug, stops, w_px=w_px, h_px=h_px)


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
        canvas = build_plate(spec["slug"], spec["stops"])
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
