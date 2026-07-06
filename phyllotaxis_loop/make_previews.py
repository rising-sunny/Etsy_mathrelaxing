"""
make_previews.py — compone las 3 imagenes de preview del listing de
Phyllotaxis Bloom (hero / titled / loop-explainer) en 2000x2000, mismo
estilo visual que dejong_loop/make_previews.py (fondo negro, serif blanco,
subtitulo italica dorada, logo MathRelaxing real).
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FRAMES = os.path.join(BASE, "frames")
OUT = os.path.join(BASE, "previews")
os.makedirs(OUT, exist_ok=True)

CANVAS = 2000
BG = (2, 2, 2)
GOLD = (223, 178, 120)
WHITE = (240, 240, 235)
GREY = (150, 150, 148)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
f_title = ImageFont.truetype(os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf"), 92)
f_sub = ImageFont.truetype(os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf"), 46)
f_specs = ImageFont.truetype(os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf"), 34)
f_specs_small = ImageFont.truetype(os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf"), 28)
f_loop = ImageFont.truetype(os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf"), 44)


def load_frame(idx, size):
    im = Image.open(os.path.join(FRAMES, f"frame_{idx:04d}.png")).convert("RGB")
    return im.resize((size, size), Image.LANCZOS)


def canvas():
    return Image.new("RGB", (CANVAS, CANVAS), BG)


def center_text(draw, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((CANVAS - w) / 2, y), text, font=font, fill=fill)


# ── 1. HERO ──────────────────────────────────────────────────────────────
def build_hero():
    im = canvas()
    art = load_frame(0, 1780)
    im.paste(art, ((CANVAS - 1780) // 2, 60))
    logo = Image.open(os.path.join(ROOT, "mathrelaxing_logo.png")).convert("RGBA")
    logo = logo.resize((int(logo.width * 260 / logo.height), 260), Image.LANCZOS)
    im.paste(logo, ((CANVAS - logo.width) // 2, 1900 - logo.height), logo)
    im.save(os.path.join(OUT, "phyllotaxis_preview_1_hero.jpg"), quality=92)


# ── 2. TITLED / SPECS ────────────────────────────────────────────────────
def build_titled():
    im = canvas()
    art = load_frame(60, 1480)
    im.paste(art, ((CANVAS - 1480) // 2, 330))
    d = ImageDraw.Draw(im)
    center_text(d, 95, "PHYLLOTAXIS BLOOM", f_title, WHITE)
    center_text(d, 215, "Seamless 30 fps Animation Loop", f_sub, GOLD)
    center_text(d, 1865, "1080 × 1080   ·   30 FPS   ·   8s PERFECT LOOP", f_specs, GREY)
    center_text(d, 1918, "Instant MP4 Digital Download", f_specs_small, GREY)
    im.save(os.path.join(OUT, "phyllotaxis_preview_2_specs.jpg"), quality=92)


# ── 3. LOOP EXPLAINER ────────────────────────────────────────────────────
def build_loop():
    im = canvas()
    art = load_frame(120, 1780)
    im.paste(art, ((CANVAS - 1780) // 2, 60))

    logo = Image.open(os.path.join(ROOT, "mathrelaxing_logo.png")).convert("RGBA")
    logo = logo.resize((int(logo.width * 140 / logo.height), 140), Image.LANCZOS)
    im.paste(logo, ((CANVAS - logo.width) // 2, 1790 - logo.height), logo)

    d = ImageDraw.Draw(im)
    center_text(d, 1905, "Plays forever — no visible seam", f_loop, (215, 210, 205))
    im.save(os.path.join(OUT, "phyllotaxis_preview_3_loop.jpg"), quality=92)


if __name__ == "__main__":
    build_hero()
    build_titled()
    build_loop()
    print("Previews generados en", OUT)
