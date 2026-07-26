"""Photoreal-ish hardcover mockups for the Etsy listing (3/4 hero, open spread,
inside grid), composited from the real cover + interior pages."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import mini_book as MB

SCR = MB.SCR
FB = os.path.join(SCR, "fullbook")
COVER = os.path.join(FB, "cover_wrap.png")
PAGES = os.path.join(FB, "pages")
OUTM = os.path.join(FB, "mockups"); os.makedirs(OUTM, exist_ok=True)
AF = MB.AF

# crops from the 5775x3075 wrap (px/pt = 4.1667)
FRONT = Image.open(COVER).convert("RGB").crop((2962, 262, 5512, 2812))   # 2550x2550
SPINE = Image.open(COVER).convert("RGB").crop((2812, 262, 2962, 2812))   # 150x2550


def find_coeffs(dst, src):
    m = []
    for (dx, dy), (sx, sy) in zip(dst, src):
        m.append([sx, sy, 1, 0, 0, 0, -dx*sx, -dx*sy])
        m.append([0, 0, 0, sx, sy, 1, -dy*sx, -dy*sy])
    A = np.array(m, float); B = np.array(dst).reshape(8)
    return np.linalg.solve(A, B)


def paste_quad(canvas, img, dst):
    """Paste img so its 4 corners (TL,TR,BR,BL) land on dst quad."""
    w, h = img.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = find_coeffs(src, dst)  # note: transform maps output->input
    warped = img.transform(canvas.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    # mask
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
    black = Image.new("RGB", canvas.size, (30, 26, 22))
    canvas.paste(black, (0, 0), sh)


def hero():
    W = H = 2000
    c = bg(W, H)
    # frontal SQUARE front face (book is 8.5x8.5) + clean axonometric thickness.
    # depth vector v shifts the back down-left, so we see the spine (left) and
    # the page block (bottom) — one consistent, undistorted view.
    A = (700, 480); B = (1540, 480); Cc = (1540, 1320); D = (700, 1320)  # 840 square
    v = (-74, 40)
    Ap = (A[0]+v[0], A[1]+v[1]); Dp = (D[0]+v[0], D[1]+v[1]); Cp = (Cc[0]+v[0], Cc[1]+v[1])
    soft_shadow(c, [Ap, B, Cc, Dp], blur=48, alpha=115, off=(26, 42))
    d = ImageDraw.Draw(c)
    # bottom edge: thin dark cover board, then cream page block
    d.polygon([D, Cc, Cp, Dp], fill=(236, 230, 217))                       # pages
    d.polygon([D, Cc, (Cc[0]+8, Cc[1]+8), (D[0]+8, D[1]+8)], fill=(20, 18, 16))  # board lip
    paste_quad(c, SPINE, [Ap, A, D, Dp])                                   # spine (left)
    paste_quad(c, FRONT, [A, B, Cc, D])                                    # front (frontal)
    c.save(os.path.join(OUTM, "01_hero.jpg"), quality=92); print("01_hero")


def spread_img(a, b):
    A = Image.open(f"{PAGES}/{a}").convert("RGB"); B = Image.open(f"{PAGES}/{b}").convert("RGB")
    s = Image.new("RGB", (A.width+B.width, A.height), "#e7e0d1")
    s.paste(A, (0, 0)); s.paste(B, (A.width, 0)); return s


def open_book(a="p003.jpg", b="p004.jpg"):
    W = H = 2000
    c = bg(W, H, (236, 232, 224), (210, 204, 193))
    sp = spread_img(a, b)
    # two-page open; quad ~2:1 so each of the two pages reads as a square
    TL = (210, 560); TR = (1790, 560); BR = (1900, 1440); BL = (100, 1440)
    soft_shadow(c, [TL, TR, BR, BL], blur=55, alpha=110, off=(0, 55))
    paste_quad(c, sp, [TL, TR, BR, BL])
    # center gutter shadow
    g = Image.new("L", c.size, 0); dd = ImageDraw.Draw(g)
    dd.polygon([( (TL[0]+TR[0])//2-30, TL[1]), ((TL[0]+TR[0])//2+30, TR[1]),
                ((BL[0]+BR[0])//2+30, BR[1]), ((BL[0]+BR[0])//2-30, BL[1])], fill=90)
    c.paste(Image.new("RGB", c.size, (0, 0, 0)), (0, 0), g.filter(ImageFilter.GaussianBlur(18)))
    c.save(os.path.join(OUTM, "02_open.jpg"), quality=92); print("02_open")


def inside_grid():
    # a 3x3 grid of graphic pages (the "what's inside")
    picks = ["p004.jpg", "p010.jpg", "p012.jpg", "p016.jpg", "p036.jpg",
             "p040.jpg", "p044.jpg", "p060.jpg", "p070.jpg"]
    picks = [p for p in picks if os.path.exists(f"{PAGES}/{p}")][:9]
    W = 2000; cell = (W - 4*40) // 3
    c = bg(W, W, (244, 240, 233), (232, 227, 217)); d = ImageDraw.Draw(c)
    ft = ImageFont.truetype(f"{AF}/Cinzel-SemiBold.ttf", 46)
    d.text((W//2, 70), "INSIDE THE BOOK", font=ft, fill=(32, 32, 30), anchor="mm")
    y0 = 140
    for i, p in enumerate(picks):
        r, col = divmod(i, 3); x = 40 + col*(cell+40); y = y0 + r*(cell+30)
        im = Image.open(f"{PAGES}/{p}").convert("RGB")
        # center-crop square from the page (avoid bleed edges)
        s = min(im.size); im = im.crop(((im.width-s)//2, (im.height-s)//2, (im.width+s)//2, (im.height+s)//2))
        im = im.resize((cell, cell), Image.Resampling.LANCZOS)
        c.paste(im, (x, y)); d.rectangle((x, y, x+cell, y+cell), outline=(210, 204, 192), width=2)
    c.save(os.path.join(OUTM, "03_inside.jpg"), quality=90); print("03_inside")


def _radial(shape, cx, cy, rx, ry, power=2.0):
    """0..1 radial falloff mask (1 at center)."""
    H, W = shape
    Y, X = np.mgrid[0:H, 0:W]
    d = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** power


def lifestyle():
    """Book standing on a warm wood table against a lit wall. Lighting: a warm
    key-light pool on the wall, a pool on the table, a subtle reflection, a
    tight contact shadow + soft cast, rim light on the cover, and a vignette."""
    W = H = 2000
    horizon = 1080
    arr = np.zeros((H, W, 3), float)
    # wall (warm, dim -> lighter toward the table) then warm walnut table
    wall_top, wall_bot = (46, 42, 39), (86, 78, 69)
    tab_far, tab_near = (118, 92, 62), (56, 41, 27)
    for y in range(horizon):
        t = y / horizon
        arr[y, :] = [wall_top[i] * (1 - t) + wall_bot[i] * t for i in range(3)]
    for y in range(horizon, H):
        t = (y - horizon) / (H - horizon)
        arr[y, :] = [tab_far[i] * (1 - t) + tab_near[i] * t for i in range(3)]

    # warm key-light pool on the wall behind the book
    glow = _radial((H, W), 1000, 720, 720, 640, 2.2)
    for i, cch in enumerate((255, 226, 172)):
        arr[:, :, i] += glow * cch * 0.50
    # pool of light on the table where the book sits
    pool = _radial((H, W), 1030, 1300, 620, 180, 1.8)
    for i, cch in enumerate((255, 232, 190)):
        arr[:, :, i] += pool * cch * 0.14

    c = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    # ---- book geometry (axonometric, standing on the table, 3/4 from left) ----
    A = (792, 548); B = (1448, 548); Cc = (1448, 1204); D = (792, 1204)   # 656 sq
    v = (-58, 32)
    Ap = (A[0] + v[0], A[1] + v[1]); Dp = (D[0] + v[0], D[1] + v[1]); Cp = (Cc[0] + v[0], Cc[1] + v[1])

    # build the book on a transparent layer (so we can also reflect it)
    bl = Image.new("RGBA", c.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    bd.polygon([D, Cc, Cp, Dp], fill=(236, 230, 217, 255))                  # page block
    bd.polygon([D, Cc, (Cc[0] + 7, Cc[1] + 7), (D[0] + 7, D[1] + 7)], fill=(20, 18, 16, 255))
    paste_quad(bl, SPINE, [Ap, A, D, Dp])                                  # spine (left)
    paste_quad(bl, FRONT, [A, B, Cc, D])                                   # front

    # subtle reflection on the polished table
    bx0, bx1, bytop, bybot = Dp[0] - 4, B[0] + 4, A[1] - 4, Cp[1] + 2
    crop = bl.crop((bx0, bytop, bx1, bybot)).transpose(Image.FLIP_TOP_BOTTOM)
    ra = np.asarray(crop).copy()
    fade = np.linspace(0.26, 0.0, ra.shape[0])[:, None]
    ra[:, :, 3] = (ra[:, :, 3] * fade).astype(np.uint8)
    refl = Image.fromarray(ra)
    c.paste(refl, (bx0, bybot), refl)

    # tight contact shadow under the base + soft directional cast to the right
    sh = Image.new("L", c.size, 0); ds = ImageDraw.Draw(sh)
    bcx = (Dp[0] + Cp[0]) // 2
    ds.ellipse([bcx - 380, Cp[1] - 22, bcx + 360, Cp[1] + 66], fill=175)
    ds.polygon([(Dp[0] + 30, Dp[1]), (Cp[0] + 190, Cp[1]),
                (Cp[0] + 210, Cp[1] + 66), (Dp[0] + 60, Dp[1] + 66)], fill=95)
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    c.paste(Image.new("RGB", c.size, (22, 15, 9)), (0, 0), sh)

    # the book on top
    c.paste(bl, (0, 0), bl)

    # ---- rim / edge light on the cover (sells the lighting) ----
    rl = Image.new("L", c.size, 0); dr = ImageDraw.Draw(rl)
    dr.line([A, B], fill=220, width=5)          # top edge
    dr.line([Ap, A], fill=150, width=4)         # spine top edge
    rl = rl.filter(ImageFilter.GaussianBlur(2))
    c.paste(Image.new("RGB", c.size, (255, 238, 200)), (0, 0), rl)

    # gentle sheen on the cover + a warm, restrained vignette
    arr2 = np.asarray(c, float)
    sheen = _radial((H, W), 1010, 700, 420, 420, 2.6)
    for i, cch in enumerate((255, 242, 214)):
        arr2[:, :, i] += sheen * cch * 0.08
    vig = _radial((H, W), W / 2, H / 2 + 30, W * 0.80, H * 0.84, 1.5)
    arr2 *= (0.72 + 0.28 * vig)[:, :, None]

    Image.fromarray(np.clip(arr2, 0, 255).astype(np.uint8)).save(
        os.path.join(OUTM, "04_lifestyle.jpg"), quality=92)
    print("04_lifestyle")


if __name__ == "__main__":
    hero(); open_book(); inside_grid(); lifestyle()
