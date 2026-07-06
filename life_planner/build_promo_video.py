"""
build_promo_video.py — video promo motion-graphics del MathRelaxing Life Planner
================================================================================
Genera un MP4 1080x1080 profesional para el slot de video del listing:
intro (logo + titulo) -> dashboard -> barrido del calendario (año/mes/semana/
dia) -> trackers (mood/budget/habit/gratitude) -> callout de features -> outro.
Fondo navy, tipografia serif crema/oro, fades suaves y zoom Ken Burns.

No lleva marca de agua: el producto es el PDF, este video es solo marketing.

Uso: python build_promo_video.py   (requiere el PDF ya construido)
"""
import os
import sys
import fitz
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, "MathRelaxing_Life_Planner.pdf")
FRAMES = os.path.join(BASE, "_promo_frames")
OUT = os.path.join(BASE, "LifePlanner_promo.mp4")

W = H = 1080
FPS = 30

NAVY = (18, 23, 45)
NAVY_D = (11, 14, 28)
GOLD = (201, 162, 75)
CREAM = (248, 244, 235)
MUTED = (150, 154, 176)
BLACK = (0, 0, 0)

FD = "/usr/share/fonts/truetype/liberation"
def font(sz, style="B"):
    f = {"B": "LiberationSerif-Bold", "R": "LiberationSerif-Regular",
         "I": "LiberationSerif-Italic"}[style]
    return ImageFont.truetype(os.path.join(FD, f + ".ttf"), sz)

PAGES = {"dashboard": 0, "year": 2, "month": 11, "week": 23, "day": 75,
         "mood": 455, "budget": 483, "habit": 474, "gratitude": 463}


def render_pages(dpi=170):
    os.makedirs(FRAMES, exist_ok=True)
    doc = fitz.open(PDF)
    imgs = {}
    for name, idx in PAGES.items():
        pix = doc[idx].get_pixmap(dpi=dpi)
        p = os.path.join(FRAMES, f"_pg_{name}.png")
        pix.save(p)
        imgs[name] = Image.open(p).convert("RGBA")
    doc.close()
    logo = Image.open(brand.LOGO_PATH).convert("RGBA")
    return imgs, logo


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def env(i, n, fin=0.25, fout=0.25):
    """Envelope de opacidad 0..1 con fade-in/out (fracciones del scene)."""
    t = i / max(n - 1, 1)
    if t < fin:
        return ease(t / fin)
    if t > 1 - fout:
        return ease((1 - t) / fout)
    return 1.0


def navy_bg():
    # degradado vertical sutil navy -> navy oscuro
    bg = Image.new("RGB", (W, H), NAVY)
    top = Image.new("RGB", (W, H), NAVY_D)
    mask = Image.linear_gradient("L").resize((W, H))
    bg = Image.composite(bg, top, mask)
    return bg.convert("RGBA")


def paste_alpha(base, img, alpha, pos=(0, 0)):
    if alpha <= 0.001:
        return
    tmp = img
    if alpha < 0.999:
        a = img.split()[3].point(lambda v: int(v * alpha))
        tmp = img.copy()
        tmp.putalpha(a)
    base.alpha_composite(tmp, pos)


def draw_text(base, cx, y, s, fnt, fill, alpha=1.0, anchor="ma"):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((cx, y), s, font=fnt, fill=fill + (int(255 * alpha),), anchor=anchor)
    base.alpha_composite(layer)


def page_card(page_img, w, zoom=1.0):
    """Devuelve una tarjeta RGBA de la pagina con borde oro y sombra."""
    scale = w / page_img.width * zoom
    pw = int(page_img.width * scale)
    ph = int(page_img.height * scale)
    pg = page_img.resize((pw, ph), Image.LANCZOS)
    pad = 26
    card = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    # sombra
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rectangle([pad + 8, pad + 12, pad + pw + 8, pad + ph + 12], fill=(0, 0, 0, 150))
    sh = sh.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(12))
    card.alpha_composite(sh)
    card.alpha_composite(pg, (pad, pad))
    d = ImageDraw.Draw(card)
    d.rectangle([pad, pad, pad + pw - 1, pad + ph - 1], outline=GOLD + (255,), width=3)
    return card


def chip(base, cx, y, s, fnt, alpha=1.0):
    d = ImageDraw.Draw(base)
    tw = d.textlength(s, font=fnt)
    pad = 22
    w = tw + pad * 2
    h = fnt.size + 20
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + h], radius=h / 2,
                         fill=GOLD + (int(255 * alpha),))
    dl.text((cx, y + h / 2), s, font=fnt, fill=NAVY + (int(255 * alpha),), anchor="mm")
    base.alpha_composite(layer)


class Timeline:
    def __init__(self):
        self.k = 0

    def emit(self, frame):
        frame.convert("RGB").save(os.path.join(FRAMES, f"f_{self.k:04d}.png"))
        self.k += 1


def scene_page(tl, page_img, secs, label=None, sublabel=None, chip_txt=None,
               slide=False, zoom_from=1.0, zoom_to=1.04, page_w=900, page_cy=560):
    n = int(secs * FPS)
    f_lab = font(58, "B")
    f_sub = font(30, "I")
    f_chip = font(30, "B")
    for i in range(n):
        a = env(i, n)
        t = i / max(n - 1, 1)
        bg = navy_bg()
        zoom = zoom_from + (zoom_to - zoom_from) * ease(t)
        card = page_card(page_img, page_w, zoom=zoom)
        # slide-in horizontal
        dx = int((1 - ease(min(t / 0.35, 1))) * 140) if slide else 0
        cardx = (W - card.width) // 2 + dx
        cardy = int(page_cy - card.height / 2)
        paste_alpha(bg, card, a, pos=(cardx, cardy))
        if label:
            draw_text(bg, W // 2, 70, label, f_lab, CREAM, a)
        if sublabel:
            draw_text(bg, W // 2, 145, sublabel, f_sub, GOLD, a)
        if chip_txt:
            chip(bg, W // 2, H - 92, chip_txt, f_chip, a)
        tl.emit(bg)


def scene_intro(tl, logo, secs=2.6):
    n = int(secs * FPS)
    f_title = font(84, "B")
    f_sub = font(38, "I")
    f_small = font(26, "R")
    lw = 260
    logo_r = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    for i in range(n):
        a = env(i, n, fin=0.3, fout=0.2)
        t = i / max(n - 1, 1)
        bg = navy_bg()
        # logo sube y aparece
        ly = int(300 - 20 * ease(min(t / 0.5, 1)))
        paste_alpha(bg, _center(logo_r, ly), a)
        draw_text(bg, W // 2, 470, "THE LIFE PLANNER", f_title, CREAM, a)
        draw_text(bg, W // 2, 585, "Undated All-in-One Digital Planner", f_sub, GOLD, a)
        draw_text(bg, W // 2, 665, "500+ hyperlinked pages  ·  GoodNotes · Notability · iPad",
                  f_small, MUTED, a)
        tl.emit(bg)


def _center(img, y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(img, ((W - img.width) // 2, y))
    return layer


def scene_features(tl, secs=2.6):
    n = int(secs * FPS)
    f_big = font(72, "B")
    f_mid = font(40, "R")
    lines = [("500+", "HYPERLINKED PAGES"),
             ("50+", "LIFE TRACKERS & TEMPLATES"),
             ("UNDATED", "START ANY DAY, REUSE FOREVER")]
    for i in range(n):
        t = i / max(n - 1, 1)
        bg = navy_bg()
        for j, (big, small) in enumerate(lines):
            # cada linea aparece escalonada
            start = 0.12 + j * 0.16
            la = ease(min(max((t - start) / 0.25, 0), 1)) * env(i, n, fin=0.01, fout=0.22)
            y = 300 + j * 175
            draw_text(bg, W // 2, y, big, f_big, GOLD, la)
            draw_text(bg, W // 2, y + 82, small, f_mid, CREAM, la)
        tl.emit(bg)


def scene_outro(tl, logo, secs=2.6):
    n = int(secs * FPS)
    f_title = font(64, "B")
    f_store = font(34, "I")
    f_small = font(26, "R")
    lw = 300
    logo_r = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    for i in range(n):
        a = env(i, n, fin=0.25, fout=0.3)
        bg = navy_bg()
        paste_alpha(bg, _center(logo_r, 330), a)
        draw_text(bg, W // 2, 560, "The Life Planner", f_title, CREAM, a)
        draw_text(bg, W // 2, 650, "mathrelaxing.store", f_store, GOLD, a)
        draw_text(bg, W // 2, 715, "Instant digital download", f_small, MUTED, a)
        tl.emit(bg)


def main():
    imgs, logo = render_pages()
    tl = Timeline()

    scene_intro(tl, logo)
    scene_page(tl, imgs["dashboard"], 2.2, label="ONE HOME FOR EVERYTHING",
               chip_txt="Tap any card to jump", page_w=880)
    scene_page(tl, imgs["year"], 1.5, label="YEAR", sublabel="12 months at a glance",
               slide=True, page_w=900)
    scene_page(tl, imgs["month"], 1.5, label="MONTH", sublabel="Undated monthly spreads",
               slide=True, page_w=900)
    scene_page(tl, imgs["week"], 1.5, label="WEEK", sublabel="52 weekly layouts",
               slide=True, page_w=900)
    scene_page(tl, imgs["day"], 1.5, label="DAY", sublabel="365 daily pages",
               slide=True, page_w=900)
    scene_page(tl, imgs["mood"], 1.4, label="WELLNESS", sublabel="Mood · sleep · water · more",
               slide=True, page_w=900)
    scene_page(tl, imgs["budget"], 1.4, label="FINANCE", sublabel="Budget · expenses · savings",
               slide=True, page_w=900)
    scene_page(tl, imgs["habit"], 1.4, label="PRODUCTIVITY", sublabel="Habits · goals · projects",
               slide=True, page_w=900)
    scene_page(tl, imgs["gratitude"], 1.4, label="SELF-CARE", sublabel="Gratitude · journaling",
               slide=True, page_w=900)
    scene_features(tl)
    scene_outro(tl, logo)

    print(f"Frames: {tl.k}  ({tl.k / FPS:.1f}s)")
    brand.encode_mp4(FRAMES, OUT, fps=FPS, pattern="f_%04d.png", crf=18, cleanup=False)
    # limpiar frames y pngs de pagina
    for f in os.listdir(FRAMES):
        os.remove(os.path.join(FRAMES, f))
    os.rmdir(FRAMES)
    size = os.path.getsize(OUT) / 1e6
    print(f"OK  {OUT}  ({size:.1f} MB)")


if __name__ == "__main__":
    main()
