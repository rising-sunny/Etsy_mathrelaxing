"""Package the Strange Attractors bookmark set: print-ready sheets (US Letter +
A4 with cut marks), individual PNGs, a styled print guide, the buyer ZIP, and
Etsy listing images. Adapted from ../bookmarks/build_package.py for this set."""
import os, glob, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "math_gallery"))
import mini_book as MB

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEL = os.path.join(HERE, "deliverable"); os.makedirs(DEL, exist_ok=True)
BMK = os.path.join(DEL, "bookmarks"); os.makedirs(BMK, exist_ok=True)
SHEETS = os.path.join(DEL, "print_sheets"); os.makedirs(SHEETS, exist_ok=True)
LST = os.path.join(HERE, "listing"); os.makedirs(LST, exist_ok=True)
AF = MB.AF
GOLD, INK, DARK, PAPER, SUB = MB.GOLD, MB.INK, MB.DARK, MB.PAPER, MB.SUB
DPI = 300
TRIM_W, TRIM_H = 600, 1800
BLEED_PX = 37
SET_NAME = "STRANGE ATTRACTORS"
SET_SUB = "10 printable bookmarks — the geometry of chaos"

ORDER = ["lorenz", "clifford", "dejong", "rossler", "thomas",
         "aizawa", "halvorsen", "hopalong", "svensson", "chen"]
TITLES = {
    "lorenz": "The Lorenz Attractor", "clifford": "The Clifford Attractor",
    "dejong": "The De Jong Attractor", "rossler": "The Rossler Attractor",
    "thomas": "Thomas Attractor", "aizawa": "The Aizawa Attractor",
    "halvorsen": "The Halvorsen Attractor", "hopalong": "The Hopalong Attractor",
    "svensson": "The Svensson Attractor", "chen": "The Chen Attractor",
}


def font(name, size): return ImageFont.truetype(os.path.join(AF, name), size)
def bleed_img(key): return Image.open(os.path.join(OUT, f"bm_{key}.png")).convert("RGB")
def trim_img(key):
    im = bleed_img(key)
    return im.crop((BLEED_PX, BLEED_PX, BLEED_PX + TRIM_W, BLEED_PX + TRIM_H))


def copy_individuals():
    for k in ORDER:
        bleed_img(k).save(os.path.join(BMK, f"{TITLES[k].replace(' ', '_')}.png"))
    print("individuals ->", BMK)


def crop_marks(d, x0, y0, x1, y1, ln=22, col=(120, 120, 120)):
    for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line([(cx, cy - dy * ln), (cx, cy)], fill=col, width=2)
        d.line([(cx - dx * ln, cy), (cx, cy)], fill=col, width=2)


def sheet(page_px, keys, fname_stub):
    W, H = page_px
    c = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(c)
    n = len(keys); gap = 26
    total = n * TRIM_W + (n - 1) * gap
    x0 = (W - total) // 2; y0 = (H - TRIM_H) // 2 + 40
    for i, k in enumerate(keys):
        x = x0 + i * (TRIM_W + gap)
        c.paste(trim_img(k), (x, y0))
        crop_marks(d, x, y0, x + TRIM_W, y0 + TRIM_H)
    d.text((W // 2, 66), f"{SET_NAME}  ·  BOOKMARKS", font=font("Cinzel-SemiBold.ttf", 34), fill=(40, 38, 34), anchor="mm")
    d.text((W // 2, H - 60), "Print at 100% (Actual size) · cut along the corner marks",
           font=font("Raleway-Italic.ttf", 24), fill=(120, 114, 102), anchor="mm")
    png = os.path.join(SHEETS, fname_stub + ".png"); c.save(png, quality=95)
    return png


def build_sheets():
    groups = [ORDER[0:4], ORDER[4:8], ORDER[8:10]]
    letter = (2550, 3300); a4 = (2480, 3508); lp, ap = [], []
    for i, g in enumerate(groups, 1):
        lp.append(sheet(letter, g, f"letter_{i}")); ap.append(sheet(a4, g, f"a4_{i}"))
    for stub, pages in [("US_Letter", lp), ("A4", ap)]:
        pdf = os.path.join(SHEETS, f"MathRelaxing_Attractor_Bookmarks_{stub}.pdf")
        with open(pdf, "wb") as f:
            f.write(img2pdf.convert(pages, layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
        print("sheet pdf ->", os.path.basename(pdf))
    for p in lp + ap:
        os.remove(p)


def build_guide():
    W, H = 2550, 3300
    c = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(c)
    cx = W // 2
    d.text((cx, 300), SET_NAME, font=font("Cinzel-SemiBold.ttf", 60), fill=INK, anchor="mm")
    d.text((cx, 380), "Printable Bookmarks — Quick Print Guide", font=font("Raleway-Italic.ttf", 38), fill=SUB, anchor="mm")
    d.line([(cx - 260, 450), (cx + 260, 450)], fill=GOLD, width=3)
    body = [
        ("WHAT'S INSIDE", [
            "- 10 strange-attractor bookmark designs (individual 300 DPI PNG files)",
            "- Print-ready sheets: US Letter and A4, with cut marks",
            "- Each bookmark is 2 x 6 in (5 x 15 cm)",
        ]),
        ("HOW TO PRINT", [
            "1. Open the US Letter or A4 sheet PDF (or an individual PNG).",
            "2. Print at 100% / 'Actual size' - do NOT 'fit to page'.",
            "3. Use heavy paper: cardstock 250-300 gsm (80-110 lb cover).",
            "4. Matte or satin photo paper gives the richest color.",
        ]),
        ("CUT & FINISH", [
            "1. Cut along the corner marks with a paper trimmer or ruler + blade.",
            "2. Optional: laminate, or self-laminate with a cold pouch, for durability.",
            "3. Optional: punch a hole at the top and add a tassel or ribbon.",
        ]),
        ("NOTES", [
            "- For personal use. Colors may vary by screen and printer.",
            "- Digital download - nothing is shipped.",
        ]),
    ]
    y = 560
    for head, lines in body:
        d.text((240, y), head, font=font("Cinzel-SemiBold.ttf", 40), fill=MB.ACC); y += 78
        for ln in lines:
            d.text((260, y), ln, font=font("Raleway.ttf", 33), fill="#403c34"); y += 60
        y += 40
    d.text((cx, H - 140), "Made by MathRelaxing", font=font("Cinzel.ttf", 34), fill=INK, anchor="mm")
    png = os.path.join(DEL, "_guide.png"); c.save(png)
    pdf = os.path.join(DEL, "Print_Guide.pdf")
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert([png], layout_fun=img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))))
    os.remove(png); print("guide ->", os.path.basename(pdf))


def bg_sq(S, top=(244, 240, 233), bot=(228, 222, 212)):
    g = np.linspace(0, 1, S)[:, None]; a = np.zeros((S, S, 3), np.uint8)
    for i in range(3):
        a[:, :, i] = (top[i] * (1 - g) + bot[i] * g).astype(np.uint8)
    return Image.fromarray(a)


def li_hero():
    S = 2000; c = bg_sq(S); d = ImageDraw.Draw(c)
    d.text((S // 2, 130), SET_NAME, font=font("Cinzel-SemiBold.ttf", 66), fill=INK, anchor="mm")
    d.text((S // 2, 202), "10 printable bookmarks — the art of chaos theory", font=font("Raleway-Italic.ttf", 36), fill=SUB, anchor="mm")
    d.line([(S // 2 - 290, 270), (S // 2 + 290, 270)], fill=GOLD, width=3)
    bw = 228; bh = int(bw * TRIM_H / TRIM_W); gap = 40; row_gap = 54; y = 335
    total = 5 * bw + 4 * gap; x0 = (S - total) // 2
    for row, keys in enumerate([ORDER[:5], ORDER[5:]]):
        yy = y + row * (bh + row_gap)
        for i, k in enumerate(keys):
            im = trim_img(k).resize((bw, bh), Image.LANCZOS); x = x0 + i * (bw + gap)
            sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle((x+6, yy+8, x+bw+6, yy+bh+8), fill=90)
            c.paste(Image.new("RGB", c.size, (70, 62, 50)), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
            c.paste(im, (x, yy))
    c.save(os.path.join(LST, "01_hero.jpg"), quality=92); print("li 01_hero")


def li_included():
    S = 2000; c = bg_sq(S, (247, 243, 236), (236, 230, 220)); d = ImageDraw.Draw(c)
    d.text((S//2, 200), "WHAT YOU GET", font=font("Cinzel-SemiBold.ttf", 76), fill=INK, anchor="mm")
    d.line([(S//2-220, 290), (S//2+220, 290)], fill=GOLD, width=3)
    items = ["10 unique strange-attractor designs", "High-resolution 300 DPI PNG files",
             "Print-ready sheets — US Letter + A4", "Cut marks included",
             "Size 2 x 6 in (5 x 15 cm)", "Quick print & finish guide (PDF)",
             "Instant download — print at home"]
    y = 420
    for it in items:
        d.ellipse((S//2-470, y+14, S//2-446, y+38), fill=GOLD)
        d.text((S//2-420, y), it, font=font("Raleway.ttf", 46), fill="#3a362e"); y += 92
    d.text((S//2, S-140), "MathRelaxing", font=font("Cinzel.ttf", 40), fill=INK, anchor="mm")
    c.save(os.path.join(LST, "04_included.jpg"), quality=92); print("li 04_included")


def li_pair(keyA, keyB, fname, label):
    S = 2000; c = bg_sq(S); d = ImageDraw.Draw(c)
    for i, k in enumerate([keyA, keyB]):
        im = trim_img(k); h = int(S * 0.62); w = int(h * TRIM_W / TRIM_H)
        im = im.resize((w, h), Image.LANCZOS)
        x = int(S * (0.33 if i == 0 else 0.67)) - w // 2; yy = int(S*0.28)
        sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle((x+8, yy+10, x+w+8, yy+h+10), fill=95)
        c.paste(Image.new("RGB", c.size, (70, 62, 50)), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
        c.paste(im, (x, yy))
    d.text((S//2, S-170), label, font=font("Cinzel-SemiBold.ttf", 46), fill=INK, anchor="mm")
    c.save(os.path.join(LST, fname), quality=92); print("li", fname)


def li_sheet():
    p = sheet((2550, 3300), ORDER[:5], "_preview")
    im = Image.open(p); os.remove(p)
    S = 2000; c = bg_sq(S)
    scale = (S * 0.92) / im.height; w = int(im.width * scale); h = int(im.height * scale)
    im = im.resize((w, h), Image.LANCZOS); c.paste(im, ((S - w) // 2, (S - h) // 2))
    d = ImageDraw.Draw(c)
    d.text((S // 2, S - 70), "Print-ready sheets · US Letter + A4 · cut marks included",
           font=font("Raleway-Italic.ttf", 32), fill=SUB, anchor="mm")
    c.save(os.path.join(LST, "05_sheet.jpg"), quality=92); print("li 05_sheet")


def build_listing_images():
    li_hero()
    li_pair("lorenz", "svensson", "02_detail_dark.jpg", "Chaos, glowing on black")
    li_pair("hopalong", "rossler", "03_detail_cream.jpg", "Elegant orbits on ivory")
    li_sheet()
    li_included()


def build_zip():
    z = os.path.join(HERE, "MathRelaxing_Strange_Attractors_Bookmarks.zip")
    if os.path.exists(z):
        os.remove(z)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(glob.glob(os.path.join(BMK, "*.png"))):
            zf.write(p, f"Bookmarks/{os.path.basename(p)}")
        for p in sorted(glob.glob(os.path.join(SHEETS, "*.pdf"))):
            zf.write(p, f"Print Sheets/{os.path.basename(p)}")
        zf.write(os.path.join(DEL, "Print_Guide.pdf"), "Print_Guide.pdf")
    print(f"ZIP -> {z} ({os.path.getsize(z)/1e6:.1f} MB)")


if __name__ == "__main__":
    copy_individuals(); build_sheets(); build_guide(); build_listing_images(); build_zip()
    print("DONE")
