"""
planner_build.py — Etsy listing images for the Relaxing Planner bundle
(2026-2027 academic dated + undated, hyperlinked GoodNotes). Renders real
pages from the built PDFs and composes the listing photos.

    python planner_build.py
"""
import os
import fitz
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

import gridpaper as gp
gp.use_palette("earth")
PAPER, GRID, ACC, TXT = gp.PAPER, gp.GRID, gp.ACC, gp.TXT

HERE = os.path.dirname(os.path.abspath(__file__))
DATED = os.path.join(HERE, "out", "planner", "academic-2026-2027",
                     "RelaxingPlanner_Academic_2026-2027_GoodNotes.pdf")
UNDATED = os.path.join(HERE, "out", "planner", "earth",
                       "RelaxingPlanner_earth_GoodNotes.pdf")
LST = os.path.join(HERE, "out", "planner", "listing")
os.makedirs(LST, exist_ok=True)
_FONT = font_manager.findfont(font_manager.FontProperties(family="DejaVu Serif"))


def font(sz):
    return ImageFont.truetype(_FONT, sz)


def center(d, W, y, text, sz, color):
    f = font(sz); w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, fill=color, font=f)


def page(pdf, pno, dpi=150):
    doc = fitz.open(pdf); pix = doc[pno].get_pixmap(dpi=dpi)
    im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close(); return im


# page indices: 0 cover, 1 year, 2 first month (Aug), 14 first week, 74 notes
def img_hero():
    thumbs = [page(DATED, p) for p in (1, 2, 14, 74)]   # year, month, week, notes
    tw = 360
    thumbs = [t.resize((tw, int(t.height * tw / t.width))) for t in thumbs]
    th = thumbs[0].height
    pad, top = 30, 210
    W = 4 * tw + pad * 5
    H = top + th + pad * 2
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for i, t in enumerate(thumbs):
        x = pad + i * (tw + pad); y = top
        im.paste(t, (x, y)); d.rectangle([x, y, x + tw - 1, y + th - 1], outline=GRID)
    center(d, W, 60, "The Relaxing Planner", 72, TXT)
    center(d, W, 150, "2026-2027 Academic  +  Undated  ·  Hyperlinked  ·  GoodNotes / iPad", 34, ACC)
    im.save(os.path.join(LST, "01_hero.jpg"), quality=92); print("01 hero")


def img_ipad():
    pg = page(DATED, 2, dpi=200)                         # a real month calendar
    W, H = 1600, 1200
    im = Image.new("RGB", (W, H), "#efe9dd"); d = ImageDraw.Draw(im)
    bw, bh = 780, 1010
    bx, by = (W - bw) // 2, (H - bh) // 2 + 20
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=42, fill="#2c2925")
    m = 26; pw = bw - 2 * m; ph = int(pg.height * pw / pg.width)
    if ph > bh - 2 * m:
        ph = bh - 2 * m; pw = int(pg.width * ph / pg.height)
    pg = pg.resize((pw, ph))
    im.paste(pg, (bx + (bw - pw) // 2, by + (bh - ph) // 2))
    center(d, W, 46, "Works on iPad · GoodNotes · Notability · any PDF app", 34, TXT)
    im.save(os.path.join(LST, "02_ipad.jpg"), quality=92); print("02 ipad")


def img_pages():
    picks = [(DATED, 0, "Cover"), (DATED, 1, "Year at a glance"),
             (DATED, 2, "Monthly (dated)"), (DATED, 14, "Weekly"),
             (DATED, 74, "Notes papers"), (UNDATED, 2, "Undated version")]
    tw = 470
    ims = [(page(pdf, p).resize((tw, int(page(pdf, p).height * tw / page(pdf, p).width))), lab)
           for pdf, p, lab in picks]
    th = ims[0][0].height; pad = 24; lab_h = 40
    cols, rows = 3, 2
    W = cols * tw + pad * (cols + 1)
    H = 90 + rows * (th + lab_h) + pad * (rows + 1)
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    center(d, W, 30, "Every page you get", 40, TXT)
    for i, (t, lab) in enumerate(ims):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad); y = 90 + pad + r * (th + lab_h + pad)
        im.paste(t, (x, y)); d.rectangle([x, y, x + tw - 1, y + th - 1], outline=GRID)
        f = font(22); w = d.textlength(lab, font=f)
        d.text((x + (tw - w) / 2, y + th + 8), lab, fill=ACC, font=f)
    im.save(os.path.join(LST, "03_pages.jpg"), quality=92); print("03 pages")


def img_features():
    pg = page(DATED, 2, dpi=170)
    W, H = 1600, 1200
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    # crop the right-edge tab strip to showcase navigation
    cw = int(pg.width * 0.16)
    strip = pg.crop((pg.width - cw, 0, pg.width, pg.height))
    sh = 900; sw = int(strip.width * sh / strip.height)
    strip = strip.resize((sw, sh))
    im.paste(strip, (W - sw - 80, (H - sh) // 2))
    d.rectangle([W - sw - 80, (H - sh) // 2, W - 80, (H - sh) // 2 + sh], outline=GRID)
    x = 90
    d.text((x, 150), "Fully hyperlinked", fill=TXT, font=font(58))
    lines = [
        "· Tap any month tab to jump straight there",
        "· Year → Month → Week, all interlinked",
        "· 1,200+ real PDF links — no scrolling",
        "· Month tabs down every page",
        "· Top nav: Year · Notes on every page",
    ]
    y = 280
    for ln in lines:
        d.text((x, y), ln, fill="#4a463f", font=font(30)); y += 62
    d.text((x, y + 30), "80 pages · vector · crisp at any zoom", fill=ACC, font=font(28))
    im.save(os.path.join(LST, "04_features.jpg"), quality=92); print("04 features")


def img_how():
    W, H = 1600, 1200
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    center(d, W, 90, "How it works", 60, TXT)
    steps = [
        ("1", "Download instantly", "Two PDFs — dated 2026-2027 academic and undated."),
        ("2", "Import to your app", "Open in GoodNotes, Notability or any PDF app on iPad or tablet."),
        ("3", "Plan & tap", "Tap tabs to navigate; write with your pencil. Reuse the undated forever."),
    ]
    y = 320
    for n, h, b in steps:
        d.text((150, y), n, fill=ACC, font=font(52))
        d.text((240, y + 4), h, fill="#3a3733", font=font(40))
        d.text((240, y + 62), b, fill="#6b6458", font=font(26))
        y += 230
    im.save(os.path.join(LST, "05_how.jpg"), quality=92); print("05 how")


if __name__ == "__main__":
    img_hero(); img_ipad(); img_pages(); img_features(); img_how()
    print("DONE ->", LST)
