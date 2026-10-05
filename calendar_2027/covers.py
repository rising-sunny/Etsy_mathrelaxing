"""Front and back cover (3375 x 2625) for the 2027 Mathematical Art Calendar."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import art
from art import W, H, OUT, NAVY, GOLD, CREAM, MONTHS, font

MN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def tile(i, w, h):
    return Image.open(os.path.join(OUT, f"{i + 1:02d}_{MONTHS[i][0]}_raw.jpg")).convert("RGB").resize((w, h), Image.LANCZOS)


def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def cover():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    lw = int(W * 0.40); cx = lw / 2 + 40
    ctext(d, cx, 520, "2027", font("cinzel", 420), GOLD)
    ctext(d, cx, 1060, "A YEAR OF", font("cinzel", 120), CREAM)
    ctext(d, cx, 1210, "MATHEMATICAL", font("cinzel", 120), CREAM)
    ctext(d, cx, 1360, "ART", font("cinzel", 120), CREAM)
    d.line((cx - 260, 1560, cx + 260, 1560), fill=GOLD, width=6)
    for k, s in enumerate(["12 fractals, attractors & curves", "computed from real mathematics"]):
        ctext(d, cx, 1620 + k * 80, s, font("light", 60), (210, 216, 230))
    ctext(d, cx, 2380, "MathRelaxing", font("cinzel_r", 64), GOLD)
    gx, gy, gap = lw + 60, 90, 36; tw = (W - gx - 90 - 2 * gap) // 3; th = int(tw * H / W)
    gy = (H - (4 * th + 3 * gap)) // 2
    for i in range(12):
        r, c = divmod(i, 3)
        im.paste(tile(i, tw, th), (gx + c * (tw + gap), gy + r * (th + gap)))
    return im


def back():
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 110, "THE MATHEMATICS OF 2027", font("cinzel", 110), NAVY)
    gap = 50; y0 = 320; th = (H - y0 - 320 - 3 * 160) // 3; tw = int(th * W / H)
    x0 = (W - (4 * tw + 3 * gap)) // 2
    for i in range(12):
        r, c = divmod(i, 4); x = x0 + c * (tw + gap); y = y0 + r * (th + 160)
        im.paste(tile(i, tw, th), (x, y))
        d.text((x, y + th + 18), MN[i].upper(), font=font("bold", 40), fill=(170, 38, 52))
        d.text((x, y + th + 72), MONTHS[i][2], font=font("semi", 46), fill=NAVY)
    ctext(d, W / 2, H - 200, "Every image in this calendar was computed from mathematics: no AI, no clip-art.", font("light", 52), (90, 90, 100))
    ctext(d, W / 2, H - 120, "MathRelaxing", font("cinzel_r", 56), (170, 130, 60))
    return im


if __name__ == "__main__":
    cover().save(os.path.join(OUT, "00_cover.jpg"), quality=94)
    back().save(os.path.join(OUT, "13_back.jpg"), quality=94); print("covers ok")
