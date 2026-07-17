"""
generate_bauhaus_set_samples.py — Bauhaus wall art SAMPLE set (MathRelaxing)
============================================================================
Gallery-grade geometric posters: modular grids, intentional asymmetry,
tight negative space, registration marks, subtle paper grain.

  python generate_bauhaus_set_samples.py
"""
from __future__ import annotations

import math
import os
import random
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = Path(__file__).resolve().parent
OUT = BASE / "bauhaus_set_samples"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"
ZIP_PATH = OUT / "MathRelaxing_Bauhaus_Samples_Preview.zip"

# Printable 2:3 — samples at solid preview res (full product → 300 dpi)
W, H = 1600, 2400

# Palette — deep, museum-wall ready
NAVY = (16, 22, 48)
NAVY_DEEP = (10, 14, 32)
CREAM = (249, 245, 236)
CREAM_WARM = (242, 236, 224)
GOLD = (196, 158, 72)
GOLD_LIGHT = (214, 182, 108)
RED = (192, 48, 42)
RED_DEEP = (148, 32, 30)
BLUE = (38, 82, 152)
BLUE_SOFT = (72, 112, 168)
BLACK = (18, 18, 20)
SOFT = (88, 86, 82)
WHITE = (255, 255, 255)
CHARCOAL = (36, 38, 48)


def _ensure():
    for d in (OUT, PRINTS, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)


def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf"]
        if bold
        else ["arial.ttf", "segoeui.ttf", "calibri.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _serif(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _bg(color=CREAM) -> Image.Image:
    return Image.new("RGB", (W, H), color)


def _paper_grain(img: Image.Image, amount: int = 8) -> Image.Image:
    """Subtle paper texture — print-shop feel without noise overload."""
    rng = random.Random(42)
    noise = Image.new("L", (W, H))
    px = noise.load()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            v = 128 + rng.randint(-amount, amount)
            px[x, y] = v
            if x + 1 < W:
                px[x + 1, y] = v
            if y + 1 < H:
                px[x, y + 1] = v
                if x + 1 < W:
                    px[x + 1, y + 1] = v
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    base = img.convert("RGB")
    # Soft multiply blend
    out = Image.blend(base, Image.merge("RGB", (noise, noise, noise)), 0.045)
    return out


def _margin_frame(d: ImageDraw.ImageDraw, m: int = 72, color=NAVY, w: int = 2):
    d.rectangle([m, m, W - m, H - m], outline=color, width=w)


def _corner_marks(d: ImageDraw.ImageDraw, m: int = 72, arm: int = 48, color=NAVY, w: int = 3):
    """Gallery registration / crop corner marks."""
    pts = [
        # TL
        [(m, m + arm), (m, m), (m + arm, m)],
        # TR
        [(W - m - arm, m), (W - m, m), (W - m, m + arm)],
        # BL
        [(m, H - m - arm), (m, H - m), (m + arm, H - m)],
        # BR
        [(W - m - arm, H - m), (W - m, H - m), (W - m, H - m - arm)],
    ]
    for path in pts:
        d.line(path, fill=color, width=w)


def _hairline(d: ImageDraw.ImageDraw, xy, color=NAVY, w: int = 1):
    d.line(xy, fill=color, width=w)


def _save_print(img: Image.Image, name: str) -> Path:
    path = PRINTS / name
    img = _paper_grain(img)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img.save(path, quality=96)
    print(f"  print {name}")
    return path


# ── Six Bauhaus compositions — lethal edition ────────────────────────────────

def poster_01_circles_bars() -> Image.Image:
    """
    Primary hero: monumental red disc vs vertical navy spine + blue mass.
    Strong scale contrast, one gold accent, breathing room.
    """
    img = _bg(CREAM)
    d = ImageDraw.Draw(img)

    # Soft cream zone with warm shift at bottom third
    for y in range(int(H * 0.62), H):
        t = (y - H * 0.62) / (H * 0.38)
        col = (
            int(CREAM[0] - 6 * t),
            int(CREAM[1] - 5 * t),
            int(CREAM[2] - 4 * t),
        )
        d.line([(0, y), (W, y)], fill=col)

    # Monumental red circle — left weight, slightly off-center (optical)
    r = 520
    cx, cy = 480, 780
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    # Inner soft ring suggestion (cream arc cut via smaller offset ellipse outline)
    d.ellipse([cx - r + 28, cy - r + 28, cx + r - 28, cy + r - 28], outline=RED_DEEP, width=2)

    # Navy vertical spine — precise right third
    bar_x0, bar_x1 = 1080, 1260
    d.rectangle([bar_x0, 160, bar_x1, 2100], fill=NAVY)

    # Cream window on navy (module)
    d.rectangle([bar_x0 + 36, 340, bar_x1 - 36, 460], fill=CREAM)
    d.rectangle([bar_x0 + 36, 500, bar_x1 - 36, 560], fill=GOLD)

    # Blue horizontal mass — intersects circle + bar (Bauhaus collision)
    d.rectangle([140, 1380, 1320, 1620], fill=BLUE)

    # Gold hairline under blue
    d.rectangle([140, 1660, 1320, 1674], fill=GOLD)

    # Small black square accent (Albers echo) bottom-left of bar
    d.rectangle([bar_x0 - 90, 1760, bar_x0 - 20, 1830], fill=BLACK)

    # Micro modules top-left
    d.rectangle([140, 160, 260, 172], fill=NAVY)
    d.rectangle([140, 160, 152, 280], fill=NAVY)
    d.ellipse([280, 168, 340, 228], fill=BLUE)

    _corner_marks(d, m=64, arm=40, color=NAVY, w=2)
    return img


def poster_02_triangles() -> Image.Image:
    """
    Dark field: stacked geometric force — cream mountain, red apex, blue core.
    Tension through overlap, not clutter.
    """
    img = _bg(NAVY_DEEP)
    d = ImageDraw.Draw(img)

    # Top / bottom gold rules (editorial)
    d.rectangle([120, 180, W - 120, 188], fill=GOLD)
    d.rectangle([120, H - 200, W - 120, H - 192], fill=GOLD_LIGHT)

    # Large cream triangle (base mass)
    d.polygon([(140, 1980), (800, 320), (1460, 1980)], fill=CREAM)

    # Red inverted force triangle — overlapping mid
    d.polygon([(220, 480), (1180, 480), (700, 1480)], fill=RED)

    # Navy cut triangle for depth (negative space illusion)
    d.polygon([(500, 620), (900, 620), (700, 1100)], fill=NAVY_DEEP)

    # Blue core circle — absolute center of tension
    d.ellipse([540, 780, 860, 1100], fill=BLUE)
    # Gold ring precision
    d.ellipse([560, 800, 840, 1080], outline=GOLD, width=6)
    d.ellipse([600, 840, 800, 1040], outline=CREAM, width=2)

    # Thin cream vertical index line
    d.rectangle([798, 200, 804, 1900], fill=CREAM)

    # Micro type-like bar cluster bottom
    d.rectangle([200, 2100, 360, 2112], fill=CREAM)
    d.rectangle([380, 2100, 440, 2112], fill=RED)
    d.rectangle([460, 2100, 620, 2112], fill=GOLD)

    return img


def poster_03_grid_modules() -> Image.Image:
    """
    Strict 3×4 modular study — each cell a miniature composition.
    Gallery board / foundation-course energy.
    """
    img = _bg(CREAM)
    d = ImageDraw.Draw(img)

    # Header band
    d.rectangle([0, 0, W, 200], fill=NAVY)
    d.text((W // 2, 78), "FORM  ·  COLOR  ·  BALANCE", font=_font(28, True), fill=CREAM, anchor="mt")
    d.text((W // 2, 130), "MODULAR STUDY  N° 03", font=_font(16), fill=GOLD, anchor="mt")

    margin_x = 100
    margin_top = 260
    margin_bot = 140
    cols, rows = 3, 4
    gap = 22
    usable_w = W - 2 * margin_x - (cols - 1) * gap
    usable_h = H - margin_top - margin_bot - (rows - 1) * gap
    cw = usable_w // cols
    ch = usable_h // rows

    # Cell definitions: (bg, motif)
    # motif kinds: solid, circle, tri_up, tri_down, bar_h, bar_v, split, ring, square_in, cross, dia, dual
    cells = [
        (NAVY, "circle_red"),
        (CREAM, "tri_navy"),
        (BLUE, "square_cream"),
        (CREAM, "bar_h_gold"),
        (RED, "circle_cream"),
        (NAVY, "tri_gold"),
        (GOLD, "bar_v_navy"),
        (CREAM, "ring_blue"),
        (BLUE, "split_red"),
        (NAVY, "square_gold"),
        (CREAM, "cross_navy"),
        (RED, "dual_circles"),
    ]

    i = 0
    for r in range(rows):
        for c in range(cols):
            x = margin_x + c * (cw + gap)
            y = margin_top + r * (ch + gap)
            bg, motif = cells[i]
            d.rectangle([x, y, x + cw, y + ch], fill=bg)
            # thin frame on light cells
            if bg == CREAM:
                d.rectangle([x, y, x + cw, y + ch], outline=NAVY, width=2)

            pad = int(min(cw, ch) * 0.18)
            ix0, iy0 = x + pad, y + pad
            ix1, iy1 = x + cw - pad, y + ch - pad
            cx, cy = x + cw // 2, y + ch // 2
            s = min(cw, ch) // 2 - pad

            if motif == "circle_red":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=RED)
            elif motif == "tri_navy":
                d.polygon([(cx, iy0), (ix1, iy1), (ix0, iy1)], fill=NAVY)
            elif motif == "square_cream":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
            elif motif == "bar_h_gold":
                d.rectangle([ix0, cy - 18, ix1, cy + 18], fill=GOLD)
                d.rectangle([ix0, cy + 40, ix1, cy + 52], fill=NAVY)
            elif motif == "circle_cream":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=CREAM)
            elif motif == "tri_gold":
                d.polygon([(ix0, iy0), (ix1, iy0), (cx, iy1)], fill=GOLD)
            elif motif == "bar_v_navy":
                d.rectangle([cx - 20, iy0, cx + 20, iy1], fill=NAVY)
                d.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], fill=CREAM)
            elif motif == "ring_blue":
                d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=BLUE, width=14)
                d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=RED)
            elif motif == "split_red":
                d.rectangle([x, y, x + cw // 2, y + ch], fill=RED)
                d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=CREAM)
            elif motif == "square_gold":
                d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=GOLD)
                d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=NAVY)
            elif motif == "cross_navy":
                d.rectangle([cx - 16, iy0, cx + 16, iy1], fill=NAVY)
                d.rectangle([ix0, cy - 16, ix1, cy + 16], fill=NAVY)
                d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=GOLD)
            elif motif == "dual_circles":
                d.ellipse([ix0, cy - s // 2, ix0 + s, cy + s // 2], fill=CREAM)
                d.ellipse([ix1 - s, cy - s // 2, ix1, cy + s // 2], fill=NAVY)

            i += 1

    # Footer rule
    d.rectangle([margin_x, H - 90, W - margin_x, H - 86], fill=NAVY)
    return img


def poster_04_arc_geometry() -> Image.Image:
    """
    Editorial arcs: large pieslice masses, red vertical panel, gold weight.
    Architectural, quiet, expensive.
    """
    img = _bg(CREAM)
    d = ImageDraw.Draw(img)

    # Outer fine frame
    _margin_frame(d, m=56, color=NAVY, w=3)

    # Large navy arc (upper-left quarter mass)
    d.pieslice([-280, 120, 980, 1380], 280, 20, fill=NAVY)
    # Cream counter-circle punch through navy
    d.ellipse([160, 520, 520, 880], fill=CREAM)
    # Blue micro-disc inside cream
    d.ellipse([280, 640, 400, 760], fill=BLUE)

    # Blue lower-right arc mass
    d.pieslice([480, 900, 1780, 2200], 160, 280, fill=BLUE)

    # Red vertical panel (right) — sharp counterweight
    d.rectangle([1120, 200, 1420, 920], fill=RED)
    # Gold thin bar inside red
    d.rectangle([1160, 280, 1380, 300], fill=GOLD)
    # Cream square module on red
    d.rectangle([1200, 400, 1340, 540], fill=CREAM)
    d.ellipse([1230, 430, 1310, 510], fill=NAVY)

    # Gold circle weight bottom-left
    d.ellipse([200, 1680, 480, 1960], fill=GOLD)
    d.ellipse([260, 1740, 420, 1900], fill=CREAM)

    # Navy horizontal spine cutting through
    d.rectangle([120, 1200, 1480, 1240], fill=NAVY_DEEP)

    # Micro index top-right
    d.rectangle([1280, 160, 1420, 172], fill=NAVY)
    d.rectangle([1408, 160, 1420, 280], fill=NAVY)

    return img


def poster_05_type_form() -> Image.Image:
    """
    Typography + geometry — Bauhaus manifesto energy without being a logo.
    Clean hierarchy, modular panels, lethal type scale.
    """
    img = _bg(NAVY_DEEP)
    d = ImageDraw.Draw(img)

    # Outer cream margin field
    d.rectangle([80, 80, W - 80, H - 80], fill=CREAM)

    # Left red spine panel
    d.rectangle([80, 80, 320, 1280], fill=RED)
    # Gold accent on spine
    d.rectangle([80, 80, 320, 160], fill=GOLD)
    d.rectangle([120, 400, 280, 416], fill=CREAM)
    d.rectangle([120, 450, 220, 466], fill=NAVY)

    # Main cream content already is background of inner
    # Blue circle — right of type
    d.ellipse([980, 280, 1380, 680], fill=BLUE)
    d.ellipse([1060, 360, 1300, 600], outline=CREAM, width=4)

    # Gold bar under type block
    d.rectangle([380, 920, 1380, 1080], fill=GOLD)
    d.text((400, 970), "1919  →  FORM", font=_font(28, True), fill=NAVY, anchor="lt")

    # Type block
    d.text((380, 320), "FORM", font=_font(120, True), fill=NAVY, anchor="lt")
    d.text((380, 480), "FOLLOWS", font=_font(48, True), fill=SOFT, anchor="lt")
    d.text((380, 560), "FUNCTION", font=_font(56, True), fill=NAVY, anchor="lt")

    # Hairline under FUNCTION
    d.rectangle([380, 660, 900, 666], fill=NAVY)

    # Small navy square system near blue
    d.rectangle([1180, 720, 1280, 820], fill=NAVY)
    d.rectangle([1300, 720, 1360, 780], fill=RED)

    # Bottom geometry panel
    d.rectangle([80, 1320, W - 80, H - 80], fill=NAVY)
    # Cream triangle
    d.polygon([(200, 2100), (560, 1480), (920, 2100)], fill=CREAM)
    # Red circle
    d.ellipse([1000, 1520, 1280, 1800], fill=RED)
    # Gold bar
    d.rectangle([1000, 1880, 1440, 1940], fill=GOLD)
    # Blue vertical
    d.rectangle([1360, 1480, 1460, 2100], fill=BLUE)
    # Cream window on blue
    d.rectangle([1380, 1600, 1440, 1680], fill=CREAM)

    return img


def poster_06_balance() -> Image.Image:
    """
    Asymmetric balance: heavy navy column vs stacked primary forms.
    One gold beam locks the composition — pure Bauhaus equilibrium.
    """
    img = _bg(CREAM)
    d = ImageDraw.Draw(img)

    # Soft vertical gradient on cream (very subtle)
    for x in range(W):
        t = x / W
        # barely warm shift
        pass

    # Left navy column — ~32% width
    col_w = 520
    d.rectangle([0, 0, col_w, H], fill=NAVY)

    # Cream circle punched into navy
    d.ellipse([120, 320, 400, 600], fill=CREAM)
    # Blue ring inside
    d.ellipse([170, 370, 350, 550], outline=BLUE, width=10)
    d.ellipse([210, 410, 310, 510], fill=GOLD)

    # Micro stack on navy lower
    d.rectangle([100, 1400, 420, 1440], fill=CREAM)
    d.rectangle([100, 1480, 280, 1500], fill=RED)
    d.rectangle([100, 1540, 360, 1552], fill=GOLD)

    # Right field compositions
    # Large red disc
    d.ellipse([640, 180, 1360, 900], fill=RED)
    # Navy square overlay (upper right of circle)
    d.rectangle([1180, 220, 1380, 420], fill=NAVY)
    # Cream inner square
    d.rectangle([1220, 260, 1340, 380], fill=CREAM)

    # Blue rectangle mass
    d.rectangle([720, 980, 1280, 1360], fill=BLUE)
    # Cream horizontal cut
    d.rectangle([720, 1120, 1280, 1160], fill=CREAM)
    # Gold vertical on blue
    d.rectangle([1080, 980, 1120, 1360], fill=GOLD)

    # Gold beam — the lock across the whole poster
    d.rectangle([0, 1120, W, 1160], fill=GOLD)
    # navy reassert on left over gold (column continuity)
    d.rectangle([0, 1120, col_w, 1160], fill=NAVY)
    # thin cream line on navy where gold would cross
    d.rectangle([0, 1136, col_w, 1144], fill=CREAM)

    # Gold triangle bottom-right
    d.polygon([(700, 2100), (1180, 1480), (1480, 2100)], fill=GOLD)
    # Navy triangle cut
    d.polygon([(900, 2100), (1180, 1720), (1460, 2100)], fill=NAVY)

    # Corner marks on cream zone only
    d.line([(W - 72, 72), (W - 72 - 48, 72)], fill=NAVY, width=3)
    d.line([(W - 72, 72), (W - 72, 72 + 48)], fill=NAVY, width=3)
    d.line([(W - 72, H - 72), (W - 72 - 48, H - 72)], fill=NAVY, width=3)
    d.line([(W - 72, H - 72), (W - 72, H - 72 - 48)], fill=NAVY, width=3)

    return img


POSTERS = [
    ("01_Circles_and_Bars.jpg", poster_01_circles_bars, "Circles & Bars"),
    ("02_Triangles.jpg", poster_02_triangles, "Triangles"),
    ("03_Grid_Modules.jpg", poster_03_grid_modules, "Grid Modules"),
    ("04_Arcs.jpg", poster_04_arc_geometry, "Arcs"),
    ("05_Form_Type.jpg", poster_05_type_form, "Form & Type"),
    ("06_Balance.jpg", poster_06_balance, "Balance"),
]


def make_contact_sheet(paths: list[tuple[Path, str]]):
    """6-up contact sheet for quick review."""
    S = 2800
    img = Image.new("RGB", (S, S + 200), NAVY_DEEP)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 56), "BAUHAUS  ·  LETHAL SAMPLE SET", font=_serif(42, True), fill=CREAM, anchor="mt")
    d.text((S // 2, 118), "MathRelaxing  ·  geometric wall art  ·  v2", font=_font(22), fill=GOLD, anchor="mt")
    # gold hairline
    d.rectangle([S // 2 - 120, 155, S // 2 + 120, 158], fill=GOLD)

    tw, th = 780, 1170
    gap = 48
    x0 = (S - 3 * tw - 2 * gap) // 2
    y0 = 200
    for i, (path, title) in enumerate(paths):
        c, r = i % 3, i // 3
        x = x0 + c * (tw + gap)
        y = y0 + r * (th + gap + 56)
        im = Image.open(path).convert("RGB")
        im = im.resize((tw, th), Image.Resampling.LANCZOS)
        # thin gold frame
        d.rectangle([x - 4, y - 4, x + tw + 4, y + th + 4], fill=GOLD)
        img.paste(im, (x, y))
        d = ImageDraw.Draw(img)
        d.text((x + tw // 2, y + th + 22), f"{i + 1:02d}  ·  {title.upper()}", font=_font(18, True), fill=GOLD, anchor="mt")

    d.rectangle([0, S + 120, S, S + 200], fill=(6, 8, 18))
    d.text((S // 2, S + 160), "Sample only — full SKU: multi-ratio ZIP @ 300 dpi", font=_font(18), fill=CREAM, anchor="mm")
    out = PREVIEWS / "bauhaus_contact_sheet.jpg"
    img.resize((1600, int(1600 * img.height / img.width)), Image.Resampling.LANCZOS).save(out, quality=93)
    print(f"  {out.name}")
    return out


def make_room_mockup(print_path: Path, name: str):
    """Refined wall mockup: soft gradient wall + deep frame + soft shadow."""
    S = 2200
    img = Image.new("RGB", (S, S), (235, 230, 222))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / S
        col = (
            int(236 - 10 * t),
            int(231 - 8 * t),
            int(222 - 6 * t),
        )
        d.line([(0, y), (S, y)], fill=col)
    # floor
    d.rectangle([0, int(S * 0.80), S, S], fill=(48, 44, 40))
    # floor highlight line
    d.rectangle([0, int(S * 0.80), S, int(S * 0.80) + 3], fill=(70, 64, 58))

    poster = Image.open(print_path).convert("RGB")
    pw, ph = 800, 1200
    poster = poster.resize((pw, ph), Image.Resampling.LANCZOS)
    px, py = (S - pw) // 2, 200
    frame = 32

    # soft shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [px - frame + 18, py - frame + 24, px + pw + frame + 18, py + ph + frame + 24],
        fill=(0, 0, 0, 80),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle(
        [px - frame, py - frame, px + pw + frame, py + ph + frame],
        fill=(22, 22, 24),
    )
    # mat
    d.rectangle(
        [px - 10, py - 10, px + pw + 10, py + ph + 10],
        fill=CREAM,
    )
    img.paste(poster, (px, py))
    d = ImageDraw.Draw(img)
    d.rectangle([0, S - 100, S, S], fill=NAVY_DEEP)
    d.text((S // 2, S - 50), "MathRelaxing  ·  Bauhaus lethal sample", font=_font(20), fill=GOLD, anchor="mm")
    out = PREVIEWS / name
    img.resize((1600, 1600), Image.Resampling.LANCZOS).save(out, quality=93)
    print(f"  {out.name}")
    return out


def make_set_mockup(print_paths: list[Path]):
    """Three frames on a gallery wall — tighter spacing, premium feel."""
    S = 2400
    wall_h = int(S * 0.72)
    img = Image.new("RGB", (S, wall_h), (238, 233, 226))
    d = ImageDraw.Draw(img)
    for y in range(wall_h):
        t = y / wall_h
        col = (int(238 - 8 * t), int(233 - 6 * t), int(226 - 5 * t))
        d.line([(0, y), (S, y)], fill=col)
    d.rectangle([0, int(wall_h * 0.86), S, wall_h], fill=(42, 38, 34))

    chosen = [print_paths[0], print_paths[1], print_paths[5]]
    pw, ph = 520, 780
    gap = 72
    total = 3 * pw + 2 * gap
    x0 = (S - total) // 2
    y0 = 140
    for i, pp in enumerate(chosen):
        poster = Image.open(pp).convert("RGB").resize((pw, ph), Image.Resampling.LANCZOS)
        x = x0 + i * (pw + gap)
        # shadow
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([x - 14 + 10, y0 - 14 + 14, x + pw + 14 + 10, y0 + ph + 14 + 14], fill=(0, 0, 0, 60))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        d = ImageDraw.Draw(img)
        d.rectangle([x - 18, y0 - 18, x + pw + 18, y0 + ph + 18], fill=(20, 20, 22))
        d.rectangle([x - 6, y0 - 6, x + pw + 6, y0 + ph + 6], fill=CREAM)
        img.paste(poster, (x, y0))

    d = ImageDraw.Draw(img)
    d.text((S // 2, 56), "SET OF 3  ·  GALLERY", font=_serif(32, True), fill=NAVY, anchor="mt")

    square = Image.new("RGB", (S, S), (238, 233, 226))
    square.paste(img, (0, (S - wall_h) // 2))
    d = ImageDraw.Draw(square)
    d.rectangle([0, S - 100, S, S], fill=NAVY_DEEP)
    d.text((S // 2, S - 50), "MathRelaxing Bauhaus Sample Set  ·  v2 lethal", font=_font(20), fill=GOLD, anchor="mm")
    out = PREVIEWS / "bauhaus_mockup_set_of_3.jpg"
    square.resize((1600, 1600), Image.Resampling.LANCZOS).save(out, quality=93)
    print(f"  {out.name}")
    return out


def main():
    _ensure()
    print("=== Bauhaus samples v2 LETHAL ===")
    print_paths = []
    titles = []
    for fname, fn, title in POSTERS:
        img = fn()
        p = _save_print(img, fname)
        print_paths.append(p)
        titles.append(title)

    make_contact_sheet(list(zip(print_paths, titles)))
    make_room_mockup(print_paths[0], "bauhaus_mockup_01.jpg")
    make_room_mockup(print_paths[1], "bauhaus_mockup_02.jpg")
    make_room_mockup(print_paths[4], "bauhaus_mockup_05.jpg")
    make_set_mockup(print_paths)

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for p in PRINTS.glob("*.jpg"):
            z.write(p, f"prints/{p.name}")
        for p in PREVIEWS.glob("*.jpg"):
            z.write(p, f"previews/{p.name}")
        z.writestr(
            "README.txt",
            "MathRelaxing Bauhaus Sample Set v2 — LETHAL (PREVIEW ONLY)\n"
            "==========================================================\n\n"
            "6 geometric compositions — tighter modular systems, stronger hierarchy,\n"
            "paper grain, registration marks, gallery mockups.\n\n"
            "Full Etsy product would include:\n"
            "  · multi-ratio files (2:3, 3:4, 4:5, A4/A3)\n"
            "  · 300 dpi print resolution\n"
            "  · listing mockups + download ZIP\n\n"
            "Palette: navy, cream, gold + Bauhaus red/blue.\n",
        )
    print(f"ZIP {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024:.0f} KB)")
    print("DONE →", OUT)
    print("Open previews: bauhaus_set_samples/previews/")


if __name__ == "__main__":
    main()
