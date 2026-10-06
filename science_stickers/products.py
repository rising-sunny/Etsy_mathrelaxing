"""
Product files for the Science Sticker Collection.

Digital pack (out/digital/):
  - Science_Stickers_PNG.zip     24 die-cut PNGs (white border) + 24 borderless PNGs (GoodNotes)
  - Cricut sheets                3 PNG sheets, 6.75 x 9.25 in @300 dpi (print-then-cut area)
  - Printable PDF (Letter, A4)   instructions + 3 themed sheets for sticker paper
Printify kiss-cut sheets (out/printify/): A5 1750x2482 sticker layers + 1822x2554 backgrounds.

  python products.py
"""
import os, zipfile, math
import fitz
from PIL import Image, ImageDraw, ImageFont
from designs import DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); ART = os.path.join(OUT, "art"); STK = os.path.join(OUT, "stickers")
DIG = os.path.join(OUT, "digital"); PFY = os.path.join(OUT, "printify")
for d in (DIG, PFY):
    os.makedirs(d, exist_ok=True)
FD = os.path.join(HERE, "fonts")
GROUPS = {"physics": "Physics", "chemistry": "Chemistry", "math": "Math"}
INK = (29, 39, 66); CREAM = (251, 245, 233)


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def names(group):
    return [n for n, (g, t, f) in DESIGNS.items() if g == group]


def trimmed(path):
    im = Image.open(path).convert("RGBA"); return im.crop(im.getbbox())


def grid_sheet(items, W, H, top, margin, gap, cols=2, rows=4, bg=None):
    """Place images in a cols x rows grid inside (margin..W-margin, top..H-margin)."""
    sheet = Image.new("RGBA", (W, H), bg or (0, 0, 0, 0))
    cw = (W - 2 * margin - (cols - 1) * gap) / cols; ch = (H - top - margin - (rows - 1) * gap) / rows
    for i, im in enumerate(items):
        r, c = divmod(i, cols); im = im.copy(); im.thumbnail((int(cw), int(ch)), Image.LANCZOS)
        x = margin + c * (cw + gap) + (cw - im.width) / 2; y = top + r * (ch + gap) + (ch - im.height) / 2
        sheet.alpha_composite(im, (int(x), int(y)))
    return sheet


def printify_sheets():
    for g, label in GROUPS.items():
        items = [trimmed(os.path.join(ART, f"{n}.png")) for n in names(g)]
        # 0.12" white border is added by the printer: keep >= 0.35" (105 px) between artworks
        layer = grid_sheet(items, 1750, 2482, top=300, margin=120, gap=130)
        layer.save(os.path.join(PFY, f"{g}_stickers.png"))
        bg = Image.new("RGB", (1822, 2554), CREAM); d = ImageDraw.Draw(bg)
        t = f"{label.upper()} STICKERS"; f = font("Fraunces-800.ttf", 110)
        d.text(((1822 - d.textlength(t, font=f)) / 2, 105), t, font=f, fill=INK)
        bg.save(os.path.join(PFY, f"{g}_background.png"))
        prev = bg.convert("RGBA"); prev.alpha_composite(Image.open(os.path.join(PFY, f"{g}_stickers.png")), (36, 36))
        prev.convert("RGB").save(os.path.join(PFY, f"{g}_preview.jpg"), quality=90)


def cricut_sheets():
    paths = []
    for g, label in GROUPS.items():
        items = [trimmed(os.path.join(STK, f"{n}.png")) for n in names(g)]
        sheet = grid_sheet(items, 2025, 2775, top=60, margin=60, gap=70)
        p = os.path.join(DIG, f"Cricut_{label}_Sheet.png"); sheet.save(p, dpi=(300, 300)); paths.append(p)
    return paths


def printable_pdf(name, W, H, cricut):
    doc = fitz.open(); fonts = {"t": os.path.join(FD, "Fraunces-800.ttf"), "b": os.path.join(FD, "Inter-500.ttf"),
                                "bb": os.path.join(FD, "Inter-700.ttf")}
    def page():
        p = doc.new_page(width=W, height=H)
        for k, v in fonts.items():
            p.insert_font(fontname=k, fontfile=v)
        return p
    p = page(); m = 54
    p.insert_text((m, 90), "Science Sticker Collection", fontname="t", fontsize=26, color=(0.11, 0.15, 0.26))
    p.insert_text((m, 116), "24 stickers  ·  Physics  ·  Chemistry  ·  Math  ·  MathRelaxing", fontname="bb", fontsize=11, color=(0.77, 0.55, 0.2))
    lines = ["HOW TO PRINT",
             "1. Print pages 2-4 at 100% / Actual size on glossy or matte sticker paper.",
             "2. Cut around each sticker with scissors, leaving the white border.",
             "",
             "CRICUT PRINT THEN CUT",
             "Upload the three Cricut_..._Sheet.png files (6.75 x 9.25 in, the maximum",
             "Print Then Cut area). Each sticker already has its white cut border.",
             "",
             "GOODNOTES / NOTABILITY / DIGITAL PLANNERS",
             "Open the PNG folder: every sticker comes with and without the white border,",
             "on a transparent background. Drag them into your notes or sticker book.",
             "",
             "Personal use only. Please do not resell or share the files.  (c) MathRelaxing"]
    y = 160
    for ln in lines:
        p.insert_text((m, y), ln, fontname="bb" if ln.isupper() else "b", fontsize=11.5, color=(0.11, 0.15, 0.26)); y += 20
    # preview of all 24 on the first page
    allst = [trimmed(os.path.join(STK, f"{n}.png")) for n in DESIGNS]
    prev = grid_sheet(allst, 1800, 1200, top=0, margin=0, gap=40, cols=6, rows=4)
    pp = os.path.join(OUT, "_prev.png"); prev.save(pp)
    p.insert_image(fitz.Rect(m, y + 20, W - m, y + 20 + (W - 2 * m) * 2 / 3), filename=pp)
    for path, label in zip(cricut, GROUPS.values()):
        p = page()
        p.insert_text((m, 44), label.upper() + " STICKERS", fontname="bb", fontsize=10, color=(0.77, 0.55, 0.2))
        w_in, h_in = 6.75 * 72, 9.25 * 72
        x0 = (W - w_in) / 2; y0 = (H - h_in) / 2 + 8
        p.insert_image(fitz.Rect(x0, y0, x0 + w_in, y0 + h_in), filename=path)
    out = os.path.join(DIG, f"Science_Stickers_Printable_{name}.pdf"); doc.save(out, deflate=True, garbage=3)
    return out


def png_zip():
    z = os.path.join(DIG, "Science_Stickers_PNG.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n, (g, t, f) in DESIGNS.items():
            nice = t.replace("'", "").replace(" ", "_").replace("²", "2").replace("ö", "o")
            zf.write(os.path.join(STK, f"{n}.png"), f"with_border/{GROUPS[g]}/{nice}.png")
            zf.write(os.path.join(ART, f"{n}.png"), f"no_border_goodnotes/{GROUPS[g]}/{nice}.png")
        for p in sorted(os.listdir(DIG)):
            if p.startswith("Cricut_"):
                zf.write(os.path.join(DIG, p), f"cricut_print_then_cut/{p}")
    return z


if __name__ == "__main__":
    printify_sheets(); cr = cricut_sheets()
    for nm, W, H in (("Letter", 612, 792), ("A4", 595.3, 841.9)):
        print(printable_pdf(nm, W, H, cr))
    z = png_zip()
    for f in sorted(os.listdir(DIG)):
        print(f, os.path.getsize(os.path.join(DIG, f)) // 1024, "KB")
