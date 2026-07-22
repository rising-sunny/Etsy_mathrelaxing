"""Build Etsy listing images for the custom pet paint-by-numbers product."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCR = os.path.dirname(os.path.abspath(__file__))
BUN = os.path.join(SCR, "lab_bundle_dense")
OUT = os.path.join(SCR, "listing")
os.makedirs(OUT, exist_ok=True)

PAPER = (250, 247, 241); INK = (32, 32, 30); SUB = (122, 118, 104)
ACC = (168, 73, 58); LINE = (222, 216, 202); GREEN = (15, 107, 87)
FDIR = "/usr/share/fonts/truetype/dejavu"
def F(name, sz): return ImageFont.truetype(os.path.join(FDIR, name), sz)
BOLD = "DejaVuSans-Bold.ttf"; REG = "DejaVuSans.ttf"; SERIF = "DejaVuSerif.ttf"; SERIFB = "DejaVuSerif-Bold.ttf"


def art_square(path, side_out, legend_frac=0.075, margin_frac=0.03):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    m = int(min(w, h) * margin_frac)
    box = (m, m, w - m, h - int(h * legend_frac))
    im = im.crop(box)
    return ImageOps.fit(im, (side_out, side_out), Image.Resampling.LANCZOS)


def photo_square(path, side_out):
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (side_out, side_out), Image.Resampling.LANCZOS)


def art_zoom(path, side_out, cx=0.58, cy=0.42, frac=0.34):
    """Crop a zoomed square from the artwork so grid + numbers stay legible."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    side = int(w * frac)
    x = int(cx * w - side / 2); y = int(cy * h - side / 2)
    x = max(0, min(x, w - side)); y = max(0, min(y, h - side))
    im = im.crop((x, y, x + side, y + side))
    return im.resize((side_out, side_out), Image.Resampling.LANCZOS)


def ctext(d, xy, text, font, fill, anchor="mm"):
    d.text(xy, text, font=font, fill=fill, anchor=anchor)


def panel(canvas, img, x, y, s, caption, cap_font):
    canvas.paste(img, (x, y))
    d = ImageDraw.Draw(canvas)
    d.rectangle((x, y, x + s, y + s), outline=LINE, width=3)
    ctext(d, (x + s // 2, y + s + 42), caption, cap_font, SUB)


def cover():
    W = H = 2000
    c = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(c)
    # title
    ctext(d, (W // 2, 150), "CUSTOM PET PAINT BY NUMBERS", F(SERIFB, 82), INK)
    ctext(d, (W // 2, 250), "made from your own photo", F(SERIF, 52), ACC)
    # three panels
    s = 500; gap = 70; total = 3 * s + 2 * gap
    x0 = (W - total) // 2; y = 470
    ph = photo_square(os.path.join(SCR, "lab_photo.webp"), s)
    nm = art_zoom(os.path.join(BUN, "paint-by-numbers_A3_29.7x42cm_NUMBERED.png"), s)
    rf = art_square(os.path.join(BUN, "color-reference_A3_29.7x42cm.png"), s)
    caps = F(REG, 40)
    panel(c, ph, x0, y, s, "YOUR PHOTO", caps)
    panel(c, nm, x0 + s + gap, y, s, "PAINT-BY-NUMBERS", caps)
    panel(c, rf, x0 + 2 * (s + gap), y, s, "PAINTED RESULT", caps)
    # arrows
    ay = y + s // 2
    for ax in (x0 + s + gap // 2, x0 + 2 * s + gap + gap // 2):
        ctext(d, (ax, ay), "→", F(BOLD, 90), ACC)
    # bottom band
    by = 1230
    d.rounded_rectangle((160, by, W - 160, by + 560), radius=26, fill=(255, 253, 247), outline=LINE, width=3)
    ctext(d, (W // 2, by + 90), "Printable Digital Download", F(SERIFB, 62), INK)
    lines = [
        "6 print sizes in one download  ·  A3 · A2 · A1 · US 20x16 & more",
        "Numbered sheet + full-color reference for every size",
        "300 DPI, print-ready  ·  landscape, portrait or square photos",
        "A thoughtful, one-of-a-kind gift for any pet lover",
    ]
    ly = by + 200
    for ln in lines:
        ctext(d, (W // 2, ly), ln, F(REG, 43), (70, 68, 62))
        ly += 78
    # small footer
    ctext(d, (W // 2, 1900), "MathRelaxing", F(SERIF, 40), SUB)
    c.save(os.path.join(OUT, "01_cover.png"))
    print("saved 01_cover.png")


def sizes_img():
    W = H = 2000
    c = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(c)
    ctext(d, (W // 2, 150), "ONE DESIGN, MANY SIZES", F(SERIFB, 80), INK)
    ctext(d, (W // 2, 250), "print it as small or as large as you like", F(SERIF, 48), ACC)
    rows = [
        ("A3", "29.7 x 42 cm"), ("A2", "42 x 59.4 cm"), ("A1", "59.4 x 84.1 cm"),
        ("US 14x11 in", "35.6 x 27.9 cm"), ("US 20x16 in", "50.8 x 40.6 cm"),
        ("US 24x18 in", "61 x 45.7 cm"),
    ]
    bx, by, bw = 360, 430, 1280
    d.rounded_rectangle((bx, by, bx + bw, by + 960), radius=24, fill=(255, 253, 247), outline=LINE, width=3)
    y = by + 90
    for name, dims in rows:
        d.rectangle((bx + 70, y - 26, bx + 120, y + 26), fill=ACC)
        ctext(d, (bx + 175, y), name, F(SERIFB, 52), INK, anchor="lm")
        ctext(d, (bx + bw - 70, y), dims, F(REG, 46), SUB, anchor="rm")
        y += 148
    ctext(d, (W // 2, 1500), "Same picture at every size — bigger paper means bigger,", F(REG, 44), (70, 68, 62))
    ctext(d, (W // 2, 1565), "easier-to-paint squares. Just print the size you want.", F(REG, 44), (70, 68, 62))
    ctext(d, (W // 2, 1720), "300 DPI  ·  print at home or at any print shop", F(REG, 42), SUB)
    c.save(os.path.join(OUT, "02_sizes.png"))
    print("saved 02_sizes.png")


def _badge_check(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.line([(cx - r * 0.42, cy + r * 0.02), (cx - r * 0.08, cy + r * 0.38),
            (cx + r * 0.48, cy - r * 0.36)], fill=(255, 255, 255), width=max(4, r // 6), joint="curve")


def _badge_x(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    o = r * 0.4; wdt = max(4, r // 6)
    d.line([(cx - o, cy - o), (cx + o, cy + o)], fill=(255, 255, 255), width=wdt)
    d.line([(cx - o, cy + o), (cx + o, cy - o)], fill=(255, 255, 255), width=wdt)


def how_img():
    from PIL import ImageEnhance, ImageFilter
    W = H = 2000
    c = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(c)
    # editorial header, left aligned
    d.text((150, 130), "For the best result", font=F(SERIFB, 84), fill=INK)
    d.text((156, 250), "a couple of quick tips for the photo you send", font=F(SERIF, 46), fill=ACC)
    d.line([(158, 340), (158 + 470, 340)], fill=ACC, width=4)

    src = os.path.join(SCR, "lab_photo.webp")
    good = photo_square(src, 700)
    bad = photo_square(src, 700)
    bad = ImageEnhance.Contrast(bad).enhance(0.55)
    bad = ImageEnhance.Brightness(bad).enhance(0.62)
    bad = bad.filter(ImageFilter.GaussianBlur(5))

    panels = [
        (150, good, GREEN, "check", "GREAT", "Sharp, good light, pet fills the frame\nand stands out from the background."),
        (1150, bad, (150, 60, 50), "x", "TRY TO AVOID", "Blurry, dark or low-contrast photos\nlose detail in the final design."),
    ]
    py = 430
    for px, img, col, kind, label, body in panels:
        c.paste(img, (px, py))
        d.rectangle((px, py, px + 700, py + 700), outline=col, width=6)
        if kind == "check":
            _badge_check(d, px + 700 - 6, py + 6, 62, col)
        else:
            _badge_x(d, px + 700 - 6, py + 6, 62, col)
        d.text((px + 4, py + 730), label, font=F(SERIFB, 52), fill=col)
        d.multiline_text((px + 6, py + 800), body, font=F(REG, 38), fill=(70, 68, 62), spacing=12)

    # slim process strip along the bottom
    sy = 1640
    d.line([(150, sy - 40), (W - 150, sy - 40)], fill=LINE, width=3)
    steps = ["Order this listing", "Message us your pet photo", "Get your download link in 1–3 days"]
    seg = (W - 300) / 3
    for i, s in enumerate(steps):
        cx = int(150 + seg * i + seg / 2)
        d.ellipse((cx - 44, sy + 30, cx + 44, sy + 118), fill=ACC)
        ctext(d, (cx, sy + 74), str(i + 1), F(SERIFB, 50), (255, 255, 255))
        d.multiline_text((cx, sy + 150),
                         s.replace(" ", "\n", 1) if i == 2 else s,
                         font=F(REG, 36), fill=(70, 68, 62), anchor="ma", align="center", spacing=8)
        if i < 2:
            ctext(d, (int(150 + seg * (i + 1)), sy + 74), "→", F(BOLD, 60), (190, 175, 150))
    c.save(os.path.join(OUT, "03_how.png"))
    print("saved 03_how.png")


def avoid_img():
    from PIL import ImageEnhance, ImageFilter
    W = H = 2000
    c = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(c)
    d.text((150, 110), "Photos that don't work as well", font=F(SERIFB, 76), fill=INK)
    d.text((156, 222), "please avoid these — they lose detail in the design", font=F(SERIF, 44), fill=ACC)
    d.line([(158, 306), (158 + 520, 306)], fill=ACC, width=4)

    lab = Image.open(os.path.join(SCR, "lab_photo.webp")).convert("RGB")
    # a real low-contrast/busy example (e.g. white pet on a light floor); if it
    # is not present we synthesize a desaturated stand-in from the main photo.
    white_dog = os.path.join(SCR, "lowcontrast_example.jpg")
    S = 640

    blurry = ImageOps.fit(lab, (S, S), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(8))
    dark = ImageEnhance.Brightness(ImageOps.fit(lab, (S, S), Image.Resampling.LANCZOS)).enhance(0.4)
    blends = photo_square(white_dog, S) if os.path.exists(white_dog) else \
        ImageEnhance.Color(ImageOps.fit(lab, (S, S), Image.Resampling.LANCZOS)).enhance(0.2)
    # pet too far / too small: shrink the whole photo onto a grass-toned canvas
    small = lab.resize((250, int(250 * lab.height / lab.width)), Image.Resampling.LANCZOS)
    g = ImageOps.fit(lab, (40, 40), Image.Resampling.LANCZOS).resize((1, 1)).getpixel((0, 0))
    far = Image.new("RGB", (S, S), g)
    far.paste(small, ((S - small.width) // 2, (S - small.height) // 2))

    cells = [
        (blurry, "Blurry / out of focus"),
        (dark, "Too dark"),
        (blends, "Blends into background"),
        (far, "Too small / too far"),
    ]
    RED = (150, 60, 50)
    gap = 70
    x0 = (W - (2 * S + gap)) // 2
    y0 = 360
    pitch = S + 150
    for i, (img, label) in enumerate(cells):
        col, row = i % 2, i // 2
        x = x0 + col * (S + gap); y = y0 + row * pitch
        c.paste(img, (x, y))
        d.rectangle((x, y, x + S, y + S), outline=RED, width=6)
        _badge_x(d, x + S - 6, y + 6, 54, RED)
        d.text((x + 4, y + S + 18), label, font=F(SERIFB, 44), fill=RED)
    c.save(os.path.join(OUT, "04_avoid.png"))
    print("saved 04_avoid.png")


if __name__ == "__main__":
    cover(); sizes_img(); how_img(); avoid_img()
