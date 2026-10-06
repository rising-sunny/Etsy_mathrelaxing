"""
Compose a scarf: fractal field + framed border (two fine lines, corner squares, small caption),
like a classic silk carré.

  python compose.py preview      -> out/preview/<key>.jpg (1500 px) + contact sheet
  python compose.py final [keys] -> out/final/<key>.jpg (9000 px, for Printify)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fractals import DESIGNS, render, hexrgb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FD = os.path.join(HERE, "..", "science_stickers", "fonts")
Image.MAX_IMAGE_PIXELS = None


def scarf(key, N):
    name, blurb, _, accent, dark = DESIGNS[key]
    b = int(N * 0.06)                               # border band
    art = Image.fromarray(render(key, N - 2 * b))
    im = Image.new("RGB", (N, N), tuple(int(v) for v in hexrgb(dark))); im.paste(art, (b, b))
    d = ImageDraw.Draw(im); acc = tuple(int(v) for v in hexrgb(accent)); lw = max(2, N // 900)
    for inset in (b - lw * 3, int(N * 0.022)):
        d.rectangle((inset, inset, N - 1 - inset, N - 1 - inset), outline=acc, width=lw)
    cs = int(b * 0.42)
    for cx in (b / 2, N - b / 2):
        for cy in (b / 2, N - b / 2):
            d.rectangle((cx - cs / 2, cy - cs / 2, cx + cs / 2, cy + cs / 2), outline=acc, width=lw)
            d.rectangle((cx - cs / 5, cy - cs / 5, cx + cs / 5, cy + cs / 5), fill=acc)
    f = ImageFont.truetype(os.path.join(FD, "Fraunces-600.ttf"), int(b * 0.30))
    cap = f"{name.upper()}   ·   MATHRELAXING"
    tw = d.textlength(cap, font=f); y = N - b / 2 - b * 0.18
    d.text(((N - tw) / 2, y), cap, font=f, fill=acc)
    return im


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    keys = sys.argv[2:] or list(DESIGNS)
    if mode == "preview":
        os.makedirs(os.path.join(OUT, "preview"), exist_ok=True); ims = []
        for k in keys:
            im = scarf(k, 1500); im.save(os.path.join(OUT, "preview", f"{k}.jpg"), quality=92); ims.append(im.resize((700, 700)))
        sh = Image.new("RGB", (3 * 700, ((len(ims) + 2) // 3) * 700))
        for i, im in enumerate(ims):
            sh.paste(im, ((i % 3) * 700, (i // 3) * 700))
        sh.save(os.path.join(OUT, "preview_contact.jpg"), quality=90)
    else:
        os.makedirs(os.path.join(OUT, "final"), exist_ok=True)
        for k in keys:
            t = time.time(); im = scarf(k, 9000)
            p = os.path.join(OUT, "final", f"{k}.jpg"); im.save(p, quality=90, dpi=(360, 360))
            print(k, round(time.time() - t), "s", os.path.getsize(p) // 1024 // 1024, "MB")
