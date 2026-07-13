"""
gridpaper_build.py — produce the Aesthetic Grid Paper deliverables + listing
images. Vector PDFs (US Letter + A4), 300-DPI PNGs (for GoodNotes/iPad), a
delivery ZIP, and the Etsy listing photos.
"""
import io
import os
import zipfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
from PIL import Image, ImageDraw

import gridpaper as gp

PAL = os.environ.get("GRIDPAPER_PALETTE", "earth")
EDITION = os.environ.get("GRIDPAPER_EDITION", PAL)
_feat = os.environ.get("GRIDPAPER_FEATURED")     # "Label|module|design"
gp.use_palette(PAL)
if _feat:
    gp.set_featured(*_feat.split("|"))

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "out", "gridpaper", EDITION)
PNG = os.path.join(BASE, "png")
LST = os.path.join(BASE, "listing")
for d in (BASE, PNG, LST):
    os.makedirs(d, exist_ok=True)
SERIF = font_manager.FontProperties(family="DejaVu Serif")
PAPER, GRID, ACC, TXT = gp.PAPER, gp.GRID, gp.ACC, gp.TXT


def thumb(style, dpi=120):
    fig = gp.render_fig(style, gp.LETTER, dpi=dpi)
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor=PAPER, dpi=dpi)
    plt.close(fig); b.seek(0)
    return Image.open(b).convert("RGB")


def build_files():
    for label, size in [("US_Letter", gp.LETTER), ("A4", gp.A4)]:
        pdf_path = os.path.join(BASE, f"AestheticGridPaper_{label}.pdf")
        with PdfPages(pdf_path) as pdf:
            for style in gp.ORDER:
                fig = gp.render_fig(style, size)
                pdf.savefig(fig, facecolor=PAPER)
                plt.close(fig)
        print("  pdf", label, f"{os.path.getsize(pdf_path)/1e6:.2f} MB")
    for style in gp.ORDER:
        fig = gp.render_fig(style, gp.LETTER, dpi=300)
        fig.savefig(os.path.join(PNG, style.replace(" ", "_").replace("+", "and") + ".png"),
                    facecolor=PAPER, dpi=300)
        plt.close(fig)
    zpath = os.path.join(BASE, f"AestheticGridPaper_{EDITION}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for label in ("US_Letter", "A4"):
            z.write(os.path.join(BASE, f"AestheticGridPaper_{label}.pdf"),
                    f"AestheticGridPaper_{label}.pdf")
        for f in sorted(os.listdir(PNG)):
            z.write(os.path.join(PNG, f), f"PNG_for_iPad_GoodNotes/{f}")
        z.writestr("READ-ME.txt",
                   "AESTHETIC GRID PAPER — 10 styles, MathRelaxing\n"
                   "US Letter + A4 vector PDFs (print) and 300 DPI PNGs (GoodNotes / iPad).\n"
                   "Personal use only; not for resale or redistribution.\n")
    print("  zip", f"{os.path.getsize(zpath)/1e6:.2f} MB")


def img_hero():
    ths = [thumb(s) for s in gp.ORDER]
    tw = 300
    ths = [t.resize((tw, int(t.height * tw / t.width))) for t in ths]
    th = ths[0].height
    cols, rows = 5, 2
    pad = 26
    top = 190
    W = cols * tw + pad * (cols + 1)
    H = top + rows * th + pad * (rows + 1)
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(ths):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad); y = top + pad + r * (th + pad)
        im.paste(t, (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=GRID)
    _center(d, W, 70, "Aesthetic Grid Paper", 60, TXT)
    _center(d, W, 130, "10 styles · US Letter + A4 · GoodNotes & printable", 30, ACC)
    im.save(os.path.join(LST, "01_hero.jpg"), quality=92)
    print("  01 hero")


def _center(d, W, y, text, size, color):
    try:
        f = font_manager.findfont(SERIF)
        from PIL import ImageFont
        fnt = ImageFont.truetype(f, size)
    except Exception:
        fnt = None
    w = d.textlength(text, font=fnt) if fnt else len(text) * size * 0.5
    d.text(((W - w) / 2, y), text, fill=color, font=fnt)


def img_ipad():
    page = thumb("Dot Grid", dpi=150)
    W, H = 1600, 1200
    im = Image.new("RGB", (W, H), "#efe9dd")
    d = ImageDraw.Draw(im)
    # tablet body
    bw, bh = 760, 1000
    bx, by = (W - bw) // 2, (H - bh) // 2
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=40, fill="#2c2925")
    # screen with page
    m = 26
    pw = bw - 2 * m
    ph = int(page.height * pw / page.width)
    if ph > bh - 2 * m:
        ph = bh - 2 * m; pw = int(page.width * ph / page.height)
    page = page.resize((pw, ph))
    im.paste(page, (bx + (bw - pw) // 2, by + (bh - ph) // 2))
    _center(d, W, 60, "Works on iPad · GoodNotes · Notability", 34, TXT)
    im.save(os.path.join(LST, "02_ipad.jpg"), quality=92)
    print("  02 ipad")


def img_closeups():
    picks = ["Square Grid", gp.FEATURED[0], "Cornell Notes", "Polar Grid"]
    ths = [thumb(s, dpi=150) for s in picks]
    tw = 520
    ths = [t.resize((tw, int(t.height * tw / t.width))) for t in ths]
    th = ths[0].height
    pad = 22
    W = 2 * tw + pad * 3
    H = 2 * th + pad * 3
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(ths):
        r, c = divmod(i, 2)
        x = pad + c * (tw + pad); y = pad + r * (th + pad)
        im.paste(t, (x, y)); d.rectangle([x, y, x + tw - 1, y + th - 1], outline=GRID)
    im.save(os.path.join(LST, "03_closeups.jpg"), quality=92)
    print("  03 closeups")


def img_included():
    fig = plt.figure(figsize=(12.8, 9.6), dpi=125)
    fig.patch.set_facecolor(PAPER)
    fig.text(0.5, 0.9, "What's inside — 10 paper styles", ha="center",
             fontproperties=SERIF, fontsize=27, color=TXT)
    lines = gp.ORDER
    for i, name in enumerate(lines):
        r, c = divmod(i, 2)
        fig.text(0.09 + c * 0.5, 0.75 - r * 0.11, f"·  {name}", fontproperties=SERIF,
                 fontsize=19, color="#4a463f")
    fig.text(0.5, 0.13, "US Letter + A4 · vector PDF (print) + 300 DPI PNG (iPad / GoodNotes)",
             ha="center", fontproperties=SERIF, fontsize=15, color=ACC)
    fig.text(0.5, 0.07, "Instant digital download · for personal use",
             ha="center", fontproperties=SERIF, fontsize=12, color="#8a8478")
    fig.savefig(os.path.join(LST, "04_included.jpg"), facecolor=PAPER)
    plt.close(fig)
    print("  04 included")


def img_how():
    fig = plt.figure(figsize=(12.8, 9.6), dpi=125)
    fig.patch.set_facecolor(PAPER)
    fig.text(0.5, 0.88, "How it works", ha="center", fontproperties=SERIF,
             fontsize=28, color=TXT)
    steps = [
        ("1", "Download instantly", "No physical item — your files are ready at checkout."),
        ("2", "Print or import", "Print the US Letter / A4 PDF, or import the PNGs into GoodNotes, Notability or any note app."),
        ("3", "Write & plan", "Use for study notes, bullet journaling, sketching, math and STEM work."),
    ]
    y = 0.68
    for n, h, b in steps:
        fig.text(0.12, y, n, fontproperties=SERIF, fontsize=22, color=ACC)
        fig.text(0.18, y, h, fontproperties=SERIF, fontsize=20, color="#3a3733")
        fig.text(0.18, y - 0.05, b, fontproperties=SERIF, fontsize=14, color="#6b6458")
        y -= 0.17
    fig.savefig(os.path.join(LST, "05_how.jpg"), facecolor=PAPER)
    plt.close(fig)
    print("  05 how")


if __name__ == "__main__":
    print("files:")
    build_files()
    print("listing:")
    img_hero(); img_ipad(); img_closeups(); img_included(); img_how()
    print("DONE ->", BASE)
