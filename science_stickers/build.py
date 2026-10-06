"""Render every sticker: raw art (transparent), die-cut PNG (white border), and a contact sheet.

  python build.py [names...]  -> out/art/*.png, out/stickers/*.png, out/contact.png
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
from PIL import Image, ImageDraw
from lib import Canvas, die_cut
from designs import DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); ART = os.path.join(OUT, "art"); STK = os.path.join(OUT, "stickers")
for d in (ART, STK):
    os.makedirs(d, exist_ok=True)


def render(name, px=1500):
    k = Canvas(px); DESIGNS[name][2](k)
    art = k.image(); art.save(os.path.join(ART, f"{name}.png"))
    st = die_cut(art); st.save(os.path.join(STK, f"{name}.png"))
    return st


def contact(names, path, T=420, cols=6):
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * T, rows * T), (226, 222, 214)); d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        st = Image.open(os.path.join(STK, f"{n}.png")); sh = die_cut(Image.open(os.path.join(ART, f"{n}.png")), shadow=True)
        sh.thumbnail((T - 50, T - 50)); x = (i % cols) * T + (T - sh.width) // 2; y = (i // cols) * T + (T - sh.height) // 2
        sheet.paste(sh, (x, y), sh); d.text(((i % cols) * T + 8, (i // cols) * T + 6), n, fill=(90, 80, 70))
    sheet.save(path)


if __name__ == "__main__":
    names = sys.argv[1:] or list(DESIGNS)
    for n in names:
        try:
            render(n); print("ok", n)
        except Exception as e:
            import traceback; traceback.print_exc(); print("FAIL", n)
    contact(names, os.path.join(OUT, "contact.png"))
