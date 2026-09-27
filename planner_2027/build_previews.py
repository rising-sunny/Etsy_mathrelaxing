"""Etsy listing images (2000x2000) for the 2027 STEM Planner, rendered from the
real PDF pages inside iPad frames on the brand IPAD_NAVY background."""
import os, sys
import fitz
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)
import brand

OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)
MON = os.path.join(HERE, "out", "2027_STEM_Planner_Monday_Start.pdf")
SUN = os.path.join(HERE, "out", "2027_STEM_Planner_Sunday_Start.pdf")
S = 2000
NAVY = brand.IPAD_NAVY; GOLD = brand.IPAD_GOLD; CREAM = brand.CREAM
LIB = "/usr/share/fonts/truetype/liberation"


def F(size, style="Bold"):
    return ImageFont.truetype(f"{LIB}/LiberationSerif-{style}.ttf", size)


def page_img(pdf, n, dpi=150):
    doc = fitz.open(pdf); pix = doc[n].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def canvas():
    c = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(c)
    d.rectangle((0, S - 150, S, S), fill=(0, 0, 0))
    logo = Image.open(brand.LOGO_PATH).convert("RGBA"); logo.thumbnail((360, 120))
    c.paste(logo, ((S - logo.width) // 2, S - 75 - logo.height // 2), logo)
    return c, d


def ipad(c, img, cx, cy, w):
    """iPad-style bezel with the page inside, centred at (cx, cy), total width w."""
    b = int(w * 0.035)
    inner_w = w - 2 * b
    im = img.resize((inner_w, int(inner_w * img.height / img.width)), Image.LANCZOS)
    h = im.height + 2 * b
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 18, y0 + 28, x0 + w + 18, y0 + h + 28), radius=int(b * 1.6), fill=(0, 0, 0, 150))
    c.paste(sh.filter(ImageFilter.GaussianBlur(26)), (0, 0), sh.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=int(b * 1.6), fill=(12, 13, 18), outline=(70, 74, 88), width=3)
    c.paste(im, (x0 + b, y0 + b))
    return (x0 + b, y0 + b, x0 + b + im.width, y0 + b + im.height)


def title(d, t, sub=None, y=90):
    f = F(104); d.text(((S - d.textlength(t, font=f)) / 2, y), t, font=f, fill=CREAM)
    if sub:
        s = F(52, "Italic"); d.text(((S - d.textlength(sub, font=s)) / 2, y + 130), sub, font=s, fill=GOLD)


def hero():
    c, d = canvas()
    title(d, "2027 STEM Planner", "Hyperlinked digital planner · GoodNotes & Notability")
    ipad(c, page_img(MON, 0), S / 2, 1050, 1700)
    return c


def month_week():
    c, d = canvas()
    title(d, "Dated Months & Weeks", "every date links to its weekly spread")
    ipad(c, page_img(MON, 6), 760, 830, 1250)
    ipad(c, page_img(MON, 31), 1240, 1330, 1250)
    return c


def inside():
    c, d = canvas()
    title(d, "What's Inside", "100 pages · 53 weeks · 12 months · 9 STEM tools")
    picks = [(1, "Index"), (3, "Year at a Glance"), (7, "Habit Tracker"), (4, "Semester Planner"),
             (83, "Assignment Tracker"), (85, "Grade & GPA"), (86, "Study Sessions"), (88, "Lab Notebook"), (90, "Cornell Notes")]
    w = 520; boxes = []
    for i, (n, lab) in enumerate(picks):
        r, col = divmod(i, 3)
        cx = 380 + col * 620; cy = 540 + r * 470
        boxes.append((cx, ipad(c, page_img(MON, n, dpi=90), cx, cy, w), lab))
    d = ImageDraw.Draw(c); f = F(38)
    for cx, box, lab in boxes:
        d.text((cx - d.textlength(lab, font=f) / 2, box[3] + 26), lab, font=f, fill=CREAM)
    return c


def links():
    c, d = canvas()
    title(d, "Tap to Navigate", "2,000+ hyperlinks on every page")
    x0, y0, x1, y1 = ipad(c, page_img(MON, 6), 760, 1000, 1360)
    d = ImageDraw.Draw(c); g = (201, 162, 75)
    # side tabs callout
    d.rounded_rectangle((x1 - 70, y0 + 10, x1 - 8, y1 - 10), radius=18, outline=g, width=8)
    d.line((x1 + 30, y0 + 250, 1560, y0 + 250), fill=g, width=6)
    f = F(52, "Italic")
    for i, t in enumerate(("Side tabs on", "every page:", "index, year,", "12 months,", "tools, notes")):
        d.text((1580, y0 + 170 + i * 64), t, font=f, fill=CREAM)
    k = (x1 - x0) / 792.0                      # px per PDF point
    cwp = (610 - 36) / 7.0; rhp = (582 - 92) / 5.0  # month-grid geometry from the PDF
    cx0, cy0 = x0 + (36 + 2 * cwp) * k, y0 + (92 + rhp) * k
    d.rounded_rectangle((cx0, cy0, cx0 + cwp * k, cy0 + rhp * k), radius=12, outline=g, width=8)
    d.text((x0, y1 + 50), "Tap any date  »  that week's spread", font=F(60, "Italic"), fill=GOLD)
    return c


def features():
    c, d = canvas()
    title(d, "Everything You Get", None, y=120)
    rows = ["2027 dated, January to December", "Monday AND Sunday start versions",
            "12 monthly calendars + habit trackers", "53 weekly spreads with priorities & study hours",
            "Goals, year at a glance, 2 semester planners", "Assignment, exam, grade & GPA trackers",
            "Study-session log, project planner, lab notebook", "Reading & research log, Cornell notes, formula sheet",
            "Graph, dot-grid and lined note pages", "Works in GoodNotes, Notability, Xodo & more"]
    f = F(56, "Regular"); y = 330
    for t in rows:
        d.ellipse((200, y + 14, 236, y + 50), fill=(201, 162, 75))
        d.text((270, y), t, font=f, fill=CREAM); y += 142
    return c


def starts():
    c, d = canvas()
    title(d, "Choose Your Week Start", "both versions included")
    ipad(c, page_img(MON, 6), 520, 1030, 900)
    ipad(c, page_img(SUN, 6), 1480, 1030, 900)
    f = F(64); d = ImageDraw.Draw(c)
    for cx, t in ((520, "Monday start"), (1480, "Sunday start")):
        d.text((cx - d.textlength(t, font=f) / 2, 580), t, font=f, fill=GOLD)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, month_week, inside, links, features, starts), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
