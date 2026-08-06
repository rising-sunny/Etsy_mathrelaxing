"""Self-contained Etsy preview set for 'The Shape of an Idea' -- no external
AI mockups needed. Composited from the real cover_wrap.png + interior pages
(book_mockups' approach), plus a few standout full-bleed plates."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, "..", "math_gallery")
sys.path.insert(0, MG)
import mini_book as MB  # noqa: E402

FB = os.path.join(HERE, "fullbook")
COVER = os.path.join(FB, "cover_wrap.png")
PAGES = os.path.join(FB, "pages")
OUT = os.path.join(FB, "previews"); os.makedirs(OUT, exist_ok=True)
AF = MB.AF
S = 2000

FRONT = Image.open(COVER).convert("RGB").crop((2962, 262, 5512, 2812))   # 2550x2550
SPINE = Image.open(COVER).convert("RGB").crop((2812, 262, 2962, 2812))   # 150x2550
BACK = Image.open(COVER).convert("RGB").crop((262, 262, 2812, 2812))


def find_coeffs(dst, src):
    m = []
    for (dx, dy), (sx, sy) in zip(dst, src):
        m.append([sx, sy, 1, 0, 0, 0, -dx*sx, -dx*sy])
        m.append([0, 0, 0, sx, sy, 1, -dy*sx, -dy*sy])
    A = np.array(m, float); B = np.array(dst).reshape(8)
    return np.linalg.solve(A, B)


def paste_quad(canvas, img, dst):
    w, h = img.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = find_coeffs(src, dst)
    warped = img.transform(canvas.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    m = Image.new("L", (w, h), 255).transform(canvas.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    canvas.paste(warped, (0, 0), m)


def bg(w, h, top=(238, 234, 227), bot=(214, 208, 197)):
    g = np.linspace(0, 1, h)[:, None]
    arr = np.zeros((h, w, 3), np.uint8)
    for i in range(3):
        arr[:, :, i] = (top[i]*(1-g) + bot[i]*g).astype(np.uint8)
    return Image.fromarray(arr)


def soft_shadow(canvas, quad, blur=45, alpha=120, off=(24, 40)):
    sh = Image.new("L", canvas.size, 0); d = ImageDraw.Draw(sh)
    q = [(x+off[0], y+off[1]) for x, y in quad]
    d.polygon(q, fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    black = Image.new("RGB", canvas.size, (10, 9, 12))
    canvas.paste(black, (0, 0), sh)


def hero():
    W = H = S
    c = bg(W, H)
    A = (700, 480); B = (1540, 480); Cc = (1540, 1320); D = (700, 1320)
    v = (-74, 40)
    Ap = (A[0]+v[0], A[1]+v[1]); Dp = (D[0]+v[0], D[1]+v[1]); Cp = (Cc[0]+v[0], Cc[1]+v[1])
    soft_shadow(c, [Ap, B, Cc, Dp], blur=48, alpha=115, off=(26, 42))
    d = ImageDraw.Draw(c)
    d.polygon([D, Cc, Cp, Dp], fill=(236, 230, 217))
    d.polygon([D, Cc, (Cc[0]+8, Cc[1]+8), (D[0]+8, D[1]+8)], fill=(12, 11, 14))
    paste_quad(c, SPINE, [Ap, A, D, Dp])
    paste_quad(c, FRONT, [A, B, Cc, D])
    c.save(os.path.join(OUT, "01_hero.jpg"), quality=92); print("01_hero")


def back_cover():
    W = H = S
    im = BACK.resize((W, H), Image.LANCZOS)
    im.save(os.path.join(OUT, "02_back_cover.jpg"), quality=92); print("02_back_cover")


def spread_img(a, b):
    A = Image.open(f"{PAGES}/{a}").convert("RGB"); B = Image.open(f"{PAGES}/{b}").convert("RGB")
    s = Image.new("RGB", (A.width+B.width, A.height), "#e7e0d1")
    s.paste(A, (0, 0)); s.paste(B, (A.width, 0)); return s


def open_book(a, b, name):
    W = H = S
    c = bg(W, H, (236, 232, 224), (210, 204, 193))
    sp = spread_img(a, b)
    TL = (210, 560); TR = (1790, 560); BR = (1900, 1440); BL = (100, 1440)
    soft_shadow(c, [TL, TR, BR, BL], blur=55, alpha=110, off=(0, 55))
    paste_quad(c, sp, [TL, TR, BR, BL])
    g = Image.new("L", c.size, 0); dd = ImageDraw.Draw(g)
    dd.polygon([((TL[0]+TR[0])//2-30, TL[1]), ((TL[0]+TR[0])//2+30, TR[1]),
                ((BL[0]+BR[0])//2+30, BR[1]), ((BL[0]+BR[0])//2-30, BL[1])], fill=90)
    c.paste(Image.new("RGB", c.size, (0, 0, 0)), (0, 0), g.filter(ImageFilter.GaussianBlur(18)))
    c.save(os.path.join(OUT, name), quality=92); print(name)


def inside_grid():
    picks = ["p05.jpg", "p07.jpg", "p09.jpg", "p12.jpg", "p19.jpg",
             "p21.jpg", "p23.jpg", "p30.jpg", "p37.jpg"]
    picks = [p for p in picks if os.path.exists(f"{PAGES}/{p}")][:9]
    W = S; cell = (W - 4*40) // 3
    c = bg(W, W, (244, 240, 233), (232, 227, 217)); d = ImageDraw.Draw(c)
    ft = ImageFont.truetype(f"{AF}/Cinzel-SemiBold.ttf", 46)
    d.text((W//2, 70), "INSIDE THE BOOK", font=ft, fill=(32, 32, 30), anchor="mm")
    y0 = 140
    for i, p in enumerate(picks):
        r, col = divmod(i, 3); x = 40 + col*(cell+40); y = y0 + r*(cell+30)
        im = Image.open(f"{PAGES}/{p}").convert("RGB")
        s = min(im.size); im = im.crop(((im.width-s)//2, (im.height-s)//2, (im.width+s)//2, (im.height+s)//2))
        im = im.resize((cell, cell), Image.Resampling.LANCZOS)
        c.paste(im, (x, y)); d.rectangle((x, y, x+cell, y+cell), outline=(210, 204, 192), width=2)
    c.save(os.path.join(OUT, "05_inside_grid.jpg"), quality=90); print("05_inside_grid")


def plate_showcase(page_file, name):
    im = Image.open(f"{PAGES}/{page_file}").convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width-s)//2, (im.height-s)//2, (im.width+s)//2, (im.height+s)//2))
    im = im.resize((S, S), Image.LANCZOS)
    im.save(os.path.join(OUT, name), quality=92); print(name)


if __name__ == "__main__":
    hero()
    back_cover()
    open_book("p04.jpg", "p05.jpg", "03_spread_euler.jpg")
    open_book("p18.jpg", "p19.jpg", "04_spread_mobius.jpg")
    inside_grid()
    plate_showcase("p19.jpg", "06_plate_mobius.jpg")
    plate_showcase("p21.jpg", "07_plate_klein.jpg")
    plate_showcase("p34.jpg", "08_plate_logistic.jpg")
    print("DONE")
