"""Assemble the final Etsy preview set for the art book: AI-generated lifestyle
mockups (dropped into fullbook/ai_mockups/) + interior-page images rendered here
from the real book pages. Outputs square 2000x2000 JPEGs to fullbook/previews/.

The four AI lifestyle mockups were generated externally (see ai_mockup_kit/
PROMPTS.md) from the real cover, then saved as:
    fullbook/ai_mockups/01_hero_lifestyle.jpg  (front, standing, warm wood)
    fullbook/ai_mockups/02_dark_marble.jpg     (front, flat, dark marble)
    fullbook/ai_mockups/03_white_marble.jpg    (front, flat, white marble)
    fullbook/ai_mockups/04_back_cover.jpg      (back cover)
Interior spreads + the plate grid are rendered here from fullbook/pages/*.jpg.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import mini_book as MB

SCR = MB.SCR
FB = os.path.join(SCR, "fullbook")
PAGES = os.path.join(FB, "pages")
AIM = os.path.join(FB, "ai_mockups")
OUT = os.path.join(FB, "previews"); os.makedirs(OUT, exist_ok=True)
AF = MB.AF
S = 2000
BLEED = 37

AI_MOCKUPS = ["01_hero_lifestyle.jpg", "02_dark_marble.jpg",
              "03_white_marble.jpg", "04_back_cover.jpg"]


def font(name, size):
    return ImageFont.truetype(os.path.join(AF, name), size)


def place_ai(name):
    """Copy an AI mockup into the set at 2000x2000 (upscale if needed)."""
    src = os.path.join(AIM, name)
    if not os.path.exists(src):
        print("  (missing AI mockup:", name, "- skipped)"); return
    im = Image.open(src).convert("RGB")
    if im.size != (S, S):
        im = im.resize((S, S), Image.LANCZOS)
    im.save(os.path.join(OUT, name), quality=92); print(name)


def trim(p):
    im = Image.open(f"{PAGES}/{p}.jpg").convert("RGB")
    return im.crop((BLEED, BLEED, im.width - BLEED, im.height - BLEED))


def make_spread(a, b):
    """flat two-page spread (5100x2550) with a soft center gutter."""
    L, R = trim(a), trim(b)
    W, H = L.width + R.width, L.height
    s = Image.new("RGB", (W, H)); s.paste(L, (0, 0)); s.paste(R, (L.width, 0))
    g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
    d.rectangle((L.width - 60, 0, L.width + 60, H), fill=110)
    s.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0),
            g.filter(ImageFilter.GaussianBlur(45)))
    return s


def bg_square(top=(240, 235, 227), bot=(224, 217, 205)):
    import numpy as np
    g = np.linspace(0, 1, S)[:, None]
    arr = np.zeros((S, S, 3), np.uint8)
    for i in range(3):
        arr[:, :, i] = (top[i] * (1 - g) + bot[i] * g).astype(np.uint8)
    return Image.fromarray(arr)


def spread_preview(a, b, dst, caption=None):
    """place a 2:1 spread centered on a square canvas with a drop shadow."""
    sp = make_spread(a, b)
    c = bg_square()
    tw = int(S * 0.90); th = int(tw * sp.height / sp.width)
    sp = sp.resize((tw, th), Image.LANCZOS)
    x = (S - tw) // 2; y = (S - th) // 2 - (30 if caption else 0)
    sh = Image.new("L", (S, S), 0); ds = ImageDraw.Draw(sh)
    ds.rectangle((x + 8, y + 14, x + tw + 8, y + th + 22), fill=120)
    c.paste(Image.new("RGB", (S, S), (60, 52, 40)), (0, 0),
            sh.filter(ImageFilter.GaussianBlur(26)))
    c.paste(sp, (x, y))
    ImageDraw.Draw(c).rectangle((x, y, x + tw, y + th), outline=(206, 199, 186), width=2)
    if caption:
        ImageDraw.Draw(c).text((S // 2, y + th + 70), caption,
                               font=font("Cinzel-SemiBold.ttf", 40),
                               fill=(46, 44, 40), anchor="mm")
    c.save(os.path.join(OUT, dst), quality=92); print(dst)


def inside_grid(dst):
    picks = ["p012", "p040", "p044", "p016", "p070", "p060", "p004", "p036", "p010"]
    picks = [p for p in picks if os.path.exists(f"{PAGES}/{p}.jpg")][:9]
    c = bg_square((244, 240, 233), (230, 224, 214)); d = ImageDraw.Draw(c)
    d.text((S // 2, 96), "INSIDE THE BOOK", font=font("Cinzel-SemiBold.ttf", 60),
           fill=(34, 32, 30), anchor="mm")
    d.text((S // 2, 156), "thirty-eight plates — each with its equation and a note",
           font=font("Raleway-Italic.ttf", 30), fill=(120, 112, 98), anchor="mm")
    cell = (S - 4 * 44) // 3; y0 = 230
    for i, p in enumerate(picks):
        r, col = divmod(i, 3); x = 44 + col * (cell + 44); y = y0 + r * (cell + 34)
        im = Image.open(f"{PAGES}/{p}.jpg").convert("RGB")
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2,
                      (im.width + s) // 2, (im.height + s) // 2)).resize((cell, cell), Image.LANCZOS)
        c.paste(im, (x, y)); d.rectangle((x, y, x + cell, y + cell), outline=(208, 202, 190), width=2)
    c.save(os.path.join(OUT, dst), quality=91); print(dst)


def build():
    for name in AI_MOCKUPS:
        place_ai(name)
    spread_preview("p003", "p004", "05_inside_lorenz.jpg",
                   caption="Every plate: the graphic, its equation, a note")
    spread_preview("p039", "p040", "06_inside_lissajous.jpg")
    spread_preview("p069", "p070", "07_inside_bessel.jpg")
    inside_grid("08_inside_grid.jpg")


if __name__ == "__main__":
    build()
