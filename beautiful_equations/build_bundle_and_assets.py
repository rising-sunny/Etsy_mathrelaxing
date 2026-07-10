"""
build_bundle_and_assets.py
==========================
Packages the "Beautiful Equations" set of 8 into the single deliverable ZIP
that Etsy hands the buyer, and builds the listing images (hero grid + a
"what you get" card). Run AFTER generate_equations.py.

  ZIP layout (one file, < 20 MB, so it fits Etsy's per-file limit):
    Beautiful_Equations/
      PDF_vector_any_size/   8 × {slug}_print.pdf   (razor-sharp at any size)
      JPG_24x30in_300dpi/    8 × {slug}_print.jpg   (7200×9000)
      READ_ME.txt

  Listing images:
    _hero.jpg              2400×3000, the 8 posters in a 2×4 grid + header
    _whatyouget.jpg        2400×3000, plain "what's included" card
"""
import os
import zipfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"

import generate_equations as G   # reuse specs, palette, one_figure

BASE = G.BASE
NAVY, GOLD, CREAM, MUTED = G.NAVY, G.GOLD, G.CREAM, G.MUTED
MUTED_PIL = tuple(int(c * 255) for c in MUTED)   # PIL needs 0-255 ints
FONT = G.FONT_PATH

READ_ME = """BEAUTIFUL EQUATIONS — The Set of 8
MathRelaxing · mathrelaxing.store

Thank you! This bundle contains 8 mathematical art prints, each set in
Computer Modern (the classic LaTeX typeface) on a deep navy ground.

WHAT'S INSIDE
-------------
PDF_vector_any_size/   8 vector PDFs. These print razor-sharp at ANY size —
                       from a small A5 card up to a huge gallery poster.
                       Best choice for most printers and print shops.
JPG_24x30in_300dpi/    8 JPG files, 7200 × 9000 px. Print-ready up to
                       24 × 30 inches at 300 dpi. Use these where a JPG is
                       required (Costco Photo, some online print services).

THE EQUATIONS
-------------
  Euler's Identity · The Pythagorean Theorem · Mass–Energy Equivalence
  The Golden Ratio · The Basel Problem · The Fundamental Theorem of Calculus
  The Normal Distribution · The Schrödinger Equation

PRINTING TIPS
-------------
· Proportion is 4:5 — frame in 8x10, 16x20 or 24x30 inch mounts.
· Best on matte or satin paper; stunning framed in a study, classroom,
  lab or office.
· Any local print shop or online service can handle these files.

© MathRelaxing. For personal use only. Not for redistribution or resale.
"""


def build_zip(out=os.path.join(BASE, "BeautifulEquations_Set8.zip")):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for spec in G.EQUATIONS:
            s = spec["slug"]
            z.write(os.path.join(BASE, f"{s}_print.pdf"),
                    f"Beautiful_Equations/PDF_vector_any_size/{s}.pdf")
            z.write(os.path.join(BASE, f"{s}_print.jpg"),
                    f"Beautiful_Equations/JPG_24x30in_300dpi/{s}.jpg")
        z.writestr("Beautiful_Equations/READ_ME.txt", READ_ME)
    mb = os.path.getsize(out) / 1e6
    print(f"ZIP: {out}  ({mb:.1f} MB)")
    return out


def _light_watermark(img, text="MATHRELAXING.STORE", opacity=34, angle=30):
    w, h = img.size
    fs = max(16, int(w * 0.026))
    font = ImageFont.truetype(FONT, fs)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = int(tmp.textlength(text, font=font))
    step_x, step_y = int(tw * 2.0), int(fs * 8.0)
    tile = Image.new("RGBA", (step_x, step_y), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((step_x * 0.1, step_y * 0.35), text, font=font,
                              fill=(255, 255, 255, opacity))
    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for yy in range(-tile.height, h, tile.height):
        for xx in range(-tile.width, w, tile.width):
            layer.alpha_composite(tile, (xx, yy))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def build_hero(out=os.path.join(BASE, "_hero.jpg"), W=2400, Hh=3000):
    """Navy hero: header + 2×4 grid of the eight posters."""
    sheet = Image.new("RGB", (W, Hh), NAVY)
    d = ImageDraw.Draw(sheet)
    # header
    f_eye = ImageFont.truetype(FONT, 46)
    f_ttl = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 120)
    f_sub = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 58)
    eye = "T H E   M O S T   B E A U T I F U L   E Q U A T I O N S"
    d.text((W/2, 150), eye, font=f_eye, fill=GOLD, anchor="mm")
    d.text((W/2, 300), "The Set of 8", font=f_ttl, fill=CREAM, anchor="mm")
    d.text((W/2, 405), "mathematical art prints", font=f_sub, fill=MUTED_PIL, anchor="mm")
    # grid of all 8 thumbnails, sized to fit the space below the header
    cols, rows = 2, 4
    gy0, gbot, cgap, rgap = 500, 60, 40, 26
    ch = (Hh - gy0 - gbot - (rows-1)*rgap) // rows     # fit 4 rows in the height
    cw = int(ch * 8/10)                                # keep 4:5 (portrait)
    grid_w = cols*cw + (cols-1)*cgap
    gx0 = (W - grid_w) // 2
    for i, spec in enumerate(G.EQUATIONS):
        fig = G.one_figure(spec)
        tmp = os.path.join(BASE, f"_h_{spec['slug']}.png")
        fig.savefig(tmp, dpi=cw/G.W_IN, facecolor=NAVY); plt.close(fig)
        thumb = Image.open(tmp).convert("RGB").resize((cw, ch), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = gx0 + c*(cw+cgap); y = gy0 + r*(ch+rgap)
        sheet.paste(thumb, (x, y))
        d.rectangle([x, y, x+cw-1, y+ch-1], outline="#2a3148", width=2)
        os.remove(tmp)
    sheet = _light_watermark(sheet)
    sheet.save(out, quality=90)
    print("Hero:", out)


def build_whatyouget(out=os.path.join(BASE, "_whatyouget.jpg"), W=2400, Hh=3000):
    fig = plt.figure(figsize=(8, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8); ax.set_ylim(0, 10); fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    ax.text(4, 9.2, "   ".join("WHAT YOU GET"), ha="center", fontsize=14, color=GOLD, family="sans-serif")
    ax.plot([3.0, 5.0], [8.85, 8.85], color=GOLD, lw=1, alpha=0.6)
    lines = [
        ("8", "iconic equations, set as fine typography"),
        ("8 × PDF", "vector — prints razor-sharp at ANY size"),
        ("8 × JPG", "7200 × 9000 px · up to 24×30 in at 300 dpi"),
        ("4:5", "ratio — frames in 8×10, 16×20, 24×30 in"),
        ("∞", "instant download — nothing is shipped"),
    ]
    y = 7.6
    for big, small in lines:
        ax.text(1.5, y, big, ha="center", va="center", fontsize=29, color=CREAM, family="serif")
        ax.text(2.55, y, small, ha="left", va="center", fontsize=14.5, color=MUTED, family="serif")
        y -= 1.3
    ax.text(4, 0.9, "MATHRELAXING.STORE", ha="center", fontsize=15, color=GOLD, family="sans-serif")
    fig.savefig(out, dpi=W/8, facecolor=NAVY, pil_kwargs={"quality": 92}); plt.close(fig)
    print("What-you-get:", out)


if __name__ == "__main__":
    build_zip()
    build_hero()
    build_whatyouget()
