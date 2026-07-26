"""Full-wrap hardcover journal cover (Printify blueprint 485 / District Photo,
print area 4065 x 2850 px). Same identity as the art book. Full-bleed dark so
minor fold misalignment stays graceful; front art + title sit inside the right
panel, spine title centered, blurb + thumbnails on the left (back) panel."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
MG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "math_gallery")
sys.path.insert(0, MG)
import mini_book as MB
import plate_library as PL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")
AF = MB.AF
DARK, GOLD, PAPER, SUB = MB.DARK, MB.GOLD, MB.PAPER, MB.SUB
W, H = 4065, 2850

def font(name, size): return ImageFont.truetype(os.path.join(AF, name), size)
def hx(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))


def frame(base, im, cx, cy, side, gold=True):
    im = im.resize((side, side), Image.LANCZOS)
    x, y = cx - side // 2, cy - side // 2
    base.paste(im, (x, y))
    if gold:
        ImageDraw.Draw(base).rectangle((x, y, x + side, y + side), outline=hx(GOLD), width=4)


def draw_spaced(d, cx, y, text, fnt, fill, spacing):
    """centered text with extra letter-spacing between characters."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill, anchor="lm")
        x += w + spacing


def rot_text(txt, fnt, fill, angle=90):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bb = d0.textbbox((0, 0), txt, font=fnt)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    t = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((4 - bb[0], 4 - bb[1]), txt, font=fnt, fill=fill)
    return t.rotate(angle, expand=True)


def build():
    base = Image.new("RGB", (W, H), hx(DARK)); d = ImageDraw.Draw(base)
    fcx = int(W * 0.735)                      # front panel center (right)
    bcx = int(W * 0.265)                      # back panel center (left)
    scx = int(W * 0.5)                        # spine center

    # ---- FRONT ----
    hero = PL.g_lorenz()
    frame(base, hero, fcx, int(H * 0.375), 1280)
    d.line([(fcx - 430, int(H*0.655)), (fcx + 430, int(H*0.655))], fill=hx(GOLD), width=3)
    d.text((fcx, int(H*0.70)), "THE MATHEMATICS", font=font("Cinzel-SemiBold.ttf", 88), fill=hx("#f0e9da"), anchor="mm")
    d.text((fcx, int(H*0.752)), "OF BEAUTY", font=font("Cinzel-SemiBold.ttf", 88), fill=hx(GOLD), anchor="mm")
    d.line([(fcx - 430, int(H*0.792)), (fcx + 430, int(H*0.792))], fill=hx(GOLD), width=3)
    # clear "A NOTEBOOK" label so it isn't confused with the art book
    draw_spaced(d, fcx, int(H*0.838), "A NOTEBOOK", font("Cinzel-SemiBold.ttf", 54), hx(GOLD), 14)
    d.text((fcx, int(H*0.878)), "150 lined pages  ·  Curves, Equations & Chaos",
           font=font("Raleway-Italic.ttf", 38), fill=hx("#cfc9bb"), anchor="mm")

    # ---- SPINE ----
    st = rot_text("THE MATHEMATICS OF BEAUTY", font("Cinzel-SemiBold.ttf", 46), hx("#f0e9da"))
    base.paste(st, (scx - st.width // 2, int(H*0.30)), st)
    sm = rot_text("MathRelaxing", font("Raleway-Italic.ttf", 34), hx(GOLD))
    base.paste(sm, (scx - sm.width // 2, int(H*0.66)), sm)

    # ---- BACK ----
    blurb = ["Some equations do more than compute —", "they draw.",
             "", "A notebook for the mathematically minded:", "150 pages to think, sketch and dream."]
    y = int(H * 0.30)
    for ln in blurb:
        d.text((bcx, y), ln, font=font("Raleway.ttf", 40), fill=hx("#cfc9bb"), anchor="mm"); y += 66
    thumbs = [PL.g_rose(), PL.g_flower(), PL.g_lissajous()]
    tw = 300; gap = 34; total = 3*tw + 2*gap; x0 = bcx - total//2; ty = int(H*0.60)
    for i, th in enumerate(thumbs):
        frame(base, th, x0 + i*(tw+gap) + tw//2, ty + tw//2, tw, gold=False)
        ImageDraw.Draw(base).rectangle((x0+i*(tw+gap), ty, x0+i*(tw+gap)+tw, ty+tw), outline=hx("#4a463f"), width=2)

    # ∞ logos (front foot + back foot)
    logo = Image.open(LOGO).convert("RGBA"); logo = logo.crop((0, 0, logo.width, int(logo.height*0.76)))
    def place(cx, cy, w):
        h = int(w * logo.height / logo.width); lg = logo.resize((w, h), Image.LANCZOS)
        base.paste(lg, (cx - w//2, cy - h//2), lg)
    place(fcx, int(H*0.94), 150)
    place(bcx, int(H*0.80), 130)

    png = os.path.join(OUT, "journal_wrap.png"); base.save(png)
    print("journal_wrap.png", base.size)
    # front-only preview crop for quick review
    base.crop((int(W*0.53), 0, int(W*0.955), H)).save(os.path.join(OUT, "journal_front.png"))
    return png


if __name__ == "__main__":
    build()
