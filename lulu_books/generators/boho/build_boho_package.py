"""Package the boho botanical 'Set of 3' printable product: per-palette ZIP
(3 print-ready PNGs + size guide PDF) + Etsy listing images (framed wall
mockup, 3-up grid, what-you-get)."""
import os, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import img2pdf
import generate_boho as B

HERE = os.path.dirname(os.path.abspath(__file__))
DEL = os.path.join(HERE, "deliverable"); os.makedirs(DEL, exist_ok=True)
LST = os.path.join(HERE, "listing"); os.makedirs(LST, exist_ok=True)
# fonts from the repo asset dir (lulu_books/assets/fonts)
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts")
PALS = {"blue": "Blue & Cream", "terra": "Terracotta"}


def font(name, size): return ImageFont.truetype(os.path.join(AF, name), size)


def panels(pal):
    return [Image.open(os.path.join(HERE, f"{pal}_panel{i+1}.png")).convert("RGB") for i in range(3)]


def size_guide_pdf(pal, path):
    W, H = 2000, 3000; P = B.PALETTES[pal]
    c = Image.new("RGB", (W, H), P["bg"]); d = ImageDraw.Draw(c); cx = W//2
    d.text((cx, 300), "BOHO BOTANICAL", font=font("Cinzel-SemiBold.ttf", 96), fill=P["ink"], anchor="mm")
    d.text((cx, 400), f"Set of 3 Printable Wall Art — {PALS[pal]}", font=font("Raleway-Italic.ttf", 46), fill=P["ink"], anchor="mm")
    d.line([(cx-320, 480),(cx+320,480)], fill=P["fill"], width=4)
    lines = [
        ("PRINT SIZES (2:3 ratio)", [
            "This file fits every standard 2:3 frame — just print at the",
            "size you need, no cropping:",
            "   4x6 · 8x12 · 12x18 · 16x24 · 20x30 · 24x36 inches",
            "   (and A-sizes: A5 · A4 · A3 · A2)",
        ]),
        ("HOW TO PRINT", [
            "1. Choose 'Fit to page' and your frame size.",
            "2. Print at home, at a print shop, or upload to a service",
            "   like Printful, Prints of Love, or your local Staples.",
            "3. Use matte or lightly textured art paper for the best look.",
        ]),
        ("WHAT'S INCLUDED", [
            "3 coordinated designs (this palette), 300 DPI, 2:3.",
            "For personal use. Colors vary slightly by screen & printer.",
        ]),
    ]
    y = 620
    for head, body in lines:
        d.text((220, y), head, font=font("Cinzel-SemiBold.ttf", 54), fill=P["fill"]); y += 96
        for ln in body:
            d.text((240, y), ln, font=font("Raleway.ttf", 40), fill=P["ink"]); y += 66
        y += 60
    d.text((cx, H-200), "MathRelaxing", font=font("Cinzel.ttf", 44), fill=P["ink"], anchor="mm")
    png = path.replace(".pdf", "_tmp.png"); c.save(png)
    with open(path, "wb") as f:
        f.write(img2pdf.convert([png], layout_fun=img2pdf.get_fixed_dpi_layout_fun((300, 300))))
    os.remove(png)


def wall_mockup(pal, path):
    W, H = 2000, 1500
    top, bot = ((0xdc,0xd3,0xc4),(0xcb,0xc1,0xb0))
    arr = np.zeros((H, W, 3), np.uint8)
    g = np.linspace(0, 1, H)[:, None]
    for i in range(3): arr[:, :, i] = (top[i]*(1-g)+bot[i]*g).astype(np.uint8)
    c = Image.fromarray(arr)
    ps = panels(pal)
    pw = 430; ph = int(pw*3/2); gap = 90
    total = 3*pw + 2*gap; x0 = (W-total)//2; y = (H-ph)//2 + 20
    fw = 20  # wood frame
    for i, p in enumerate(ps):
        x = x0 + i*(pw+gap)
        # soft shadow
        sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle((x-fw+10, y-fw+16, x+pw+fw+10, y+ph+fw+16), fill=90)
        c.paste(Image.new("RGB", c.size, (60,52,42)), (0,0), sh.filter(ImageFilter.GaussianBlur(18)))
        # wood frame
        ImageDraw.Draw(c).rectangle((x-fw, y-fw, x+pw+fw, y+ph+fw), fill=(196,150,96))
        ImageDraw.Draw(c).rectangle((x-4, y-4, x+pw+4, y+ph+4), outline=(150,110,70), width=2)
        c.paste(p.resize((pw, ph), Image.LANCZOS), (x, y))
    c.save(path, quality=92)


def grid_3(pal, path):
    W = 2000; P = B.PALETTES[pal]
    ps = panels(pal)
    pw = 560; ph = int(pw*3/2); gap = 50
    Hh = ph + 360
    c = Image.new("RGB", (W, Hh), P["bg"]); d = ImageDraw.Draw(c)
    d.text((W//2, 130), "SET OF 3 — BOHO BOTANICAL", font=font("Cinzel-SemiBold.ttf", 68), fill=P["ink"], anchor="mm")
    d.text((W//2, 210), f"{PALS[pal]} · printable wall art", font=font("Raleway-Italic.ttf", 40), fill=P["ink"], anchor="mm")
    total = 3*pw + 2*gap; x0 = (W-total)//2; y = 300
    for i, p in enumerate(ps):
        x = x0 + i*(pw+gap); c.paste(p.resize((pw, ph), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x+pw, y+ph), outline=P["fill"], width=2)
    c.save(path, quality=92)


def what_you_get(path):
    W = H = 2000; c = Image.new("RGB", (W, H), "#efe9dc"); d = ImageDraw.Draw(c)
    d.text((W//2, 210), "WHAT YOU GET", font=font("Cinzel-SemiBold.ttf", 84), fill="#39465e", anchor="mm")
    d.line([(W//2-230, 300),(W//2+230,300)], fill="#c0674a", width=4)
    items = ["Set of 3 coordinated designs", "TWO colorways: Blue & Cream + Terracotta",
             "High-resolution 300 DPI, 2:3 ratio", "Fits 4x6 up to 24x36 in (+ A-sizes)",
             "6 print-ready PNG files total", "Size & print guide (PDF)",
             "Instant download — print at home"]
    y = 430
    for it in items:
        d.ellipse((W//2-560, y+14, W//2-536, y+38), fill="#c0674a")
        d.text((W//2-505, y), it, font=font("Raleway.ttf", 46), fill="#3a362e"); y += 96
    d.text((W//2, H-160), "MathRelaxing", font=font("Cinzel.ttf", 42), fill="#39465e", anchor="mm")
    c.save(path, quality=92)


def build():
    for pal in PALS:
        pdf = os.path.join(DEL, f"SizeGuide_{pal}.pdf"); size_guide_pdf(pal, pdf)
        z = os.path.join(HERE, f"MathRelaxing_Boho_{pal}.zip")
        if os.path.exists(z): os.remove(z)
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in range(3):
                zf.write(os.path.join(HERE, f"{pal}_panel{i+1}.png"), f"{PALS[pal]}/Boho_Botanical_{pal}_{i+1}.png")
            zf.write(pdf, "Size_and_Print_Guide.pdf")
        print("zip", os.path.basename(z), f"{os.path.getsize(z)/1e6:.1f}MB")
    # listing images
    wall_mockup("blue", os.path.join(LST, "01_wall_blue.jpg"))
    wall_mockup("terra", os.path.join(LST, "02_wall_terra.jpg"))
    grid_3("blue", os.path.join(LST, "03_grid_blue.jpg"))
    grid_3("terra", os.path.join(LST, "04_grid_terra.jpg"))
    what_you_get(os.path.join(LST, "05_what_you_get.jpg"))
    print("listing images done")


if __name__ == "__main__":
    build()
