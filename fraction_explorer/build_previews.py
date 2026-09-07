"""Etsy preview images for the Fraction Explorer interactive.
Frames the three live screenshots in a browser chrome + a cover + info card.
Screenshots are taken by shot_modes.py (Playwright) into SHOTS.
  python build_previews.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.environ.get("FX_SHOTS", "/tmp/claude-0/-home-user-Etsy-mathrelaxing/083e0cf9-d7ef-5f41-a39f-80c548fddc12/scratchpad")
PREV = os.path.join(HERE, "previews"); os.makedirs(PREV, exist_ok=True)
AF = os.path.join(HERE, "..", "lulu_books", "assets", "fonts")
S = 2000
CREAM = (244, 241, 234); INK = (40, 44, 54); TEAL = (47, 111, 126); MUT = (109, 114, 128)


def font(n, s):
    return ImageFont.truetype(os.path.join(AF, n), s)


def browser(shot_path, w):
    """put a screenshot inside a simple browser window frame, scaled to width w."""
    sc = Image.open(shot_path).convert("RGB")
    h = int(sc.height * w / sc.width)
    sc = sc.resize((w, h), Image.LANCZOS)
    bar = 44
    fr = Image.new("RGB", (w, h + bar), (255, 255, 255))
    d = ImageDraw.Draw(fr)
    d.rectangle((0, 0, w, bar), fill=(237, 240, 243))
    for i, c in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
        d.ellipse((20 + i * 26, bar // 2 - 7, 20 + i * 26 + 14, bar // 2 + 7), fill=c)
    fr.paste(sc, (0, bar))
    d.rectangle((0, 0, w - 1, h + bar - 1), outline=(210, 214, 220), width=2)
    return fr


def shadow(base, box, blur=26, a=70):
    from PIL import ImageFilter
    x0, y0, x1, y1 = box
    sh = Image.new("L", base.size, 0)
    ImageDraw.Draw(sh).rectangle((x0 + 8, y0 + 14, x1 + 8, y1 + 16), fill=a)
    base.paste((25, 30, 35), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))


def cover():
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c)
    d.text((S // 2, 150), "INTERACTIVE", font=font("Raleway.ttf", 40), fill=TEAL, anchor="mm")
    d.text((S // 2, 232), "Fraction Explorer", font=font("Cinzel-SemiBold.ttf", 92), fill=INK, anchor="mm")
    d.text((S // 2, 312), "model · equivalents · compare · number line",
           font=font("Raleway-Italic.ttf", 34), fill=MUT, anchor="mm")
    fr = browser(f"{SHOTS}/fx_model.png", 1360)
    x = (S - fr.width) // 2; y = 380
    shadow(c, (x, y, x + fr.width, y + fr.height))
    c.paste(fr, (x, y))
    badges = ["Works offline", "No install", "Grades 3–6", "1 file"]
    bw = 360; total = len(badges) * bw + (len(badges) - 1) * 24; bx = (S - total) // 2; by = 1740
    for b in badges:
        d.rounded_rectangle((bx, by, bx + bw, by + 78), 39, fill=(255, 255, 255), outline=(214, 224, 226), width=2)
        d.text((bx + bw // 2, by + 39), b, font=font("Raleway.ttf", 30), fill=TEAL, anchor="mm")
        bx += bw + 24
    d.text((S // 2, 1900), "MathRelaxing", font=font("Cinzel-SemiBold.ttf", 40), fill=TEAL, anchor="mm")
    c.save(f"{PREV}/01_cover.jpg", quality=92); print("01_cover")


def feature(shot, title, sub, dst):
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c)
    d.text((S // 2, 130), title, font=font("Cinzel-SemiBold.ttf", 66), fill=INK, anchor="mm")
    d.text((S // 2, 205), sub, font=font("Raleway-Italic.ttf", 34), fill=MUT, anchor="mm")
    fr = browser(f"{SHOTS}/{shot}", 1580)
    x = (S - fr.width) // 2; y = 300
    shadow(c, (x, y, x + fr.width, y + fr.height))
    c.paste(fr, (x, y))
    c.save(f"{PREV}/{dst}", quality=92); print(dst)


def info():
    c = Image.new("RGB", (S, S), (255, 255, 255)); d = ImageDraw.Draw(c)
    d.rectangle((44, 44, S - 44, S - 44), outline=TEAL, width=4)
    d.text((S // 2, 150), "HOW IT WORKS", font=font("Cinzel-SemiBold.ttf", 60), fill=INK, anchor="mm")
    lines = [
        "• One self-contained HTML file — just double-click to open",
        "• Runs in any browser, fully offline (great for Chromebooks)",
        "• No install, no logins, no student data collected",
        "• 3 modes: model & equivalents · compare · number line",
        "• Built-in practice with instant feedback",
        "• Project on the board or let students explore 1:1",
        "• Single-classroom license (extra licenses discounted)",
    ]
    y = 320
    for ln in lines:
        d.text((150, y), ln, font=font("Raleway.ttf", 36), fill=(52, 56, 66)); y += 92
    d.text((S // 2, S - 150), "MathRelaxing", font=font("Cinzel-SemiBold.ttf", 40), fill=TEAL, anchor="mm")
    c.save(f"{PREV}/06_info.jpg", quality=93); print("06_info")


if __name__ == "__main__":
    cover()
    feature("fx_model.png", "MODEL & EQUIVALENTS", "shade it · simplify · build equivalents", "02_model.jpg")
    feature("fx_compare.png", "COMPARE", "line up two bars · read < = >", "03_compare.jpg")
    feature("fx_line.png", "NUMBER LINE", "place any fraction between the wholes", "04_line.jpg")
    info()
