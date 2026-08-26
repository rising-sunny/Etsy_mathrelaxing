"""
build_package.py — Etsy deliverables for the Neo Deco set.

From masters/*.png produces:
  previews/  — 2000x2000 Etsy images: set-of-3 gallery-wall hero, per-design
               framed wall mockups, a flat "set of 3" grid, an info card.
  prints/    — 300dpi print-ready JPEGs (2:3 master + 4:5 + ISO crops).
  Neo_Deco_Set.zip — the digital bundle a buyer downloads.

  python build_package.py
"""
import os, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
MAST = os.path.join(BASE, "masters")
PREV = os.path.join(BASE, "previews"); os.makedirs(PREV, exist_ok=True)
PRIN = os.path.join(BASE, "prints"); os.makedirs(PRIN, exist_ok=True)
AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")

NAMES = ["01_sunburst", "02_arches", "03_rosette"]
TITLES = ["Sunburst", "Arch Portal", "Rose Window"]
GOLD = (201, 161, 67)
INK = (26, 28, 32)
S = 2000


def font(name, size):
    return ImageFont.truetype(os.path.join(AF, name), size)


def master(i):
    return Image.open(os.path.join(MAST, f"{NAMES[i]}.png")).convert("RGB")


def wall(w, h, tone=(228, 223, 214)):
    """soft vertical-gradient plaster wall with a gentle floor glow."""
    top = np.array(tone, float); bot = np.array([max(0, c - 26) for c in tone], float)
    g = np.linspace(0, 1, h)[:, None]
    arr = (top * (1 - g) + bot * g).astype(np.uint8)
    arr = np.repeat(arr[:, None, :], w, axis=1)
    return Image.fromarray(arr, "RGB")


def frame_art(art, fw, mat=0, frame_col=INK, target_h=None):
    """put `art` in a thin frame (+ optional mat), return RGBA with shadow-ready alpha."""
    if target_h:
        r = target_h / art.height
        art = art.resize((int(art.width * r), target_h), Image.LANCZOS)
    aw, ah = art.size
    W = aw + 2 * mat + 2 * fw
    H = ah + 2 * mat + 2 * fw
    fr = Image.new("RGB", (W, H), frame_col)
    d = ImageDraw.Draw(fr)
    # subtle inner bevel highlight on the frame
    d.rectangle((fw - 2, fw - 2, W - fw + 1, H - fw + 1), outline=(90, 92, 96), width=2)
    if mat:
        fr.paste(Image.new("RGB", (aw + 2 * mat, ah + 2 * mat), (244, 241, 234)), (fw, fw))
    fr.paste(art, (fw + mat, fw + mat))
    return fr


def shadow(base, box, blur=28, alpha=120, off=(10, 16)):
    x0, y0, x1, y1 = box
    sh = Image.new("L", base.size, 0)
    ImageDraw.Draw(sh).rectangle((x0 + off[0], y0 + off[1], x1 + off[0], y1 + off[1]), fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.paste(Image.new("RGB", base.size, (30, 26, 22)), (0, 0), sh)


def paste_framed(base, art, cx, cy, target_h, fw=26, mat=0, frame_col=INK):
    fr = frame_art(art, fw, mat, frame_col, target_h=target_h)
    x = cx - fr.width // 2; y = cy - fr.height // 2
    shadow(base, (x, y, x + fr.width, y + fr.height))
    base.paste(fr, (x, y))
    return fr.size


# ---------------------------------------------------------------- previews
def hero_gallery():
    """set-of-3 framed on a warm gallery wall above a console line."""
    c = wall(S, S, (223, 217, 207))
    # floor / console band
    d = ImageDraw.Draw(c)
    d.rectangle((0, int(S * 0.82), S, S), fill=(205, 197, 185))
    d.line((0, int(S * 0.82), S, int(S * 0.82)), fill=(150, 143, 130), width=3)
    th = int(S * 0.46)
    xs = [int(S * 0.22), int(S * 0.5), int(S * 0.78)]
    for x, i in zip(xs, range(3)):
        paste_framed(c, master(i), x, int(S * 0.44), th, fw=20, mat=0)
    d.text((S // 2, int(S * 0.93)), "N E O   D E C O   ·   S E T   O F   3",
           font=font("Cinzel-SemiBold.ttf", 40), fill=(70, 66, 60), anchor="mm")
    c.save(os.path.join(PREV, "01_hero_gallery.jpg"), quality=92)
    print("01_hero_gallery")


def single_mock(i, dst):
    c = wall(S, S, (226, 220, 210))
    paste_framed(c, master(i), S // 2, int(S * 0.47), int(S * 0.72), fw=30, mat=0)
    ImageDraw.Draw(c).text((S // 2, int(S * 0.95)), TITLES[i].upper(),
                           font=font("Cinzel-SemiBold.ttf", 34), fill=(80, 76, 70), anchor="mm")
    c.save(os.path.join(PREV, dst), quality=92)
    print(dst)


def flat_grid():
    c = Image.new("RGB", (S, S), (18, 20, 24)); d = ImageDraw.Draw(c)
    d.text((S // 2, int(S * 0.07)), "THE NEO DECO SET", font=font("Cinzel-SemiBold.ttf", 66),
           fill=(232, 226, 214), anchor="mm")
    d.text((S // 2, int(S * 0.135)), "three metallic Art-Deco prints · chrome, gold & emerald",
           font=font("Raleway-Italic.ttf", 30), fill=(150, 145, 134), anchor="mm")
    tw = int(S * 0.29); th = int(tw * 1.5); y = int(S * 0.22)
    xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]
    for x, i in zip(xs, range(3)):
        im = master(i).resize((tw, th), Image.LANCZOS)
        bx = x - tw // 2
        shadow(c, (bx, y, bx + tw, y + th), blur=22, alpha=140)
        c.paste(im, (bx, y))
        d.rectangle((bx, y, bx + tw, y + th), outline=GOLD, width=3)
        d.text((x, y + th + 34), TITLES[i], font=font("Cinzel.ttf", 30),
               fill=(210, 204, 192), anchor="mm")
    d.text((S // 2, int(S * 0.93)), "instant download · high-resolution 300 DPI",
           font=font("Raleway.ttf", 28), fill=(150, 145, 134), anchor="mm")
    c.save(os.path.join(PREV, "05_set_grid.jpg"), quality=93)
    print("05_set_grid")


def info_card():
    c = Image.new("RGB", (S, S), (244, 241, 234)); d = ImageDraw.Draw(c)
    d.rectangle((40, 40, S - 40, S - 40), outline=GOLD, width=4)
    d.text((S // 2, 150), "WHAT YOU GET", font=font("Cinzel-SemiBold.ttf", 60), fill=INK, anchor="mm")
    lines = [
        "• 3 high-resolution digital prints (JPEG, 300 DPI)",
        "• 2:3 ratio — prints 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in",
        "• Bonus 4:5 and ISO (A-size) crops included",
        "• Instant download — no physical item is shipped",
        "• For personal use; print at home or any print shop",
    ]
    y = 320
    for ln in lines:
        d.text((180, y), ln, font=font("Raleway.ttf", 34), fill=(52, 48, 42)); y += 90
    d.text((S // 2, S - 150), "MathRelaxing", font=font("Cinzel-SemiBold.ttf", 40),
           fill=GOLD, anchor="mm")
    c.save(os.path.join(PREV, "06_info.jpg"), quality=93)
    print("06_info")


# ------------------------------------------------------------------ prints
def crop_ratio(im, ratio_w, ratio_h):
    """center-crop `im` to the target ratio (keeps the border-safe center)."""
    W, H = im.size
    target = ratio_w / ratio_h
    if W / H > target:
        nw = int(H * target); return im.crop(((W - nw) // 2, 0, (W + nw) // 2, H))
    nh = int(W / target); return im.crop((0, (H - nh) // 2, W, (H + nh) // 2))


def make_prints():
    files = []
    for i, n in enumerate(NAMES):
        m = master(i)
        p23 = os.path.join(PRIN, f"{n}_2x3_300dpi.jpg"); m.save(p23, quality=95, dpi=(300, 300))
        p45 = os.path.join(PRIN, f"{n}_4x5_300dpi.jpg")
        crop_ratio(m, 4, 5).save(p45, quality=95, dpi=(300, 300))
        piso = os.path.join(PRIN, f"{n}_ISO_A_300dpi.jpg")
        crop_ratio(m, 1, 1.4142).save(piso, quality=95, dpi=(300, 300))
        files += [p23, p45, piso]
        print("prints:", n)
    return files


def make_zip(files):
    z = os.path.join(BASE, "Neo_Deco_Set.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, os.path.join("Neo_Deco_Set", os.path.basename(f)))
        # a small read-me
        readme = ("THE NEO DECO SET — MathRelaxing\n\n"
                  "3 metallic Art-Deco prints (Sunburst, Arch Portal, Rose Window).\n"
                  "Each in 2:3, 4:5 and ISO A ratios, 300 DPI JPEG.\n\n"
                  "Print at home or any print shop. Personal use.\n")
        zf.writestr("Neo_Deco_Set/READ_ME.txt", readme)
    print("zip:", z, f"{os.path.getsize(z)//1024} KB")
    return z


def build():
    hero_gallery()
    single_mock(0, "02_sunburst_mock.jpg")
    single_mock(1, "03_arches_mock.jpg")
    single_mock(2, "04_rosette_mock.jpg")
    flat_grid()
    info_card()
    files = make_prints()
    make_zip(files)


if __name__ == "__main__":
    build()
