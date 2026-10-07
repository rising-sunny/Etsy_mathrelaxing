"""
Render the ten posters.

  python build.py preview   -> out/png/NN_name.png (750x1000 pt at 2 px/pt) + out/contact.jpg
  python build.py           -> vector PDFs in five sizes + 300 dpi PNGs (18x24)
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
import cairo
from PIL import Image
from kit import render
from posters import POSTERS

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
SIZES = {"18x24": (18 * 72, 24 * 72), "11x17": (11 * 72, 17 * 72), "Letter": (8.5 * 72, 11 * 72),
         "A4": (595.3, 841.9), "A3": (841.9, 1190.6)}


def preview(scale=2.0):
    d = os.path.join(OUT, "png"); os.makedirs(d, exist_ok=True); paths = []
    for i, fn in enumerate(POSTERS, 1):
        p = os.path.join(d, f"{i:02d}_{fn.__name__}.png"); render(fn, p, 750, 1000, kind="png", px_per_pt=scale); paths.append(p)
    ims = [Image.open(p).convert("RGB").resize((450, 600)) for p in paths]
    sh = Image.new("RGB", (5 * 450, 2 * 600), "white")
    for i, im in enumerate(ims):
        sh.paste(im, ((i % 5) * 450, (i // 5) * 600))
    sh.save(os.path.join(OUT, "contact.jpg"), quality=88)
    return paths


def pdfs():
    d = os.path.join(OUT, "pdf"); os.makedirs(d, exist_ok=True)
    for name, (w, h) in SIZES.items():
        path = os.path.join(d, f"Trig_Algebra_Classroom_Posters_{name}.pdf")
        surf = cairo.PDFSurface(path, w, h)
        for fn in POSTERS:
            render(fn, None, w, h, kind="pdf", surface=surf)
        surf.finish(); print(name, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    preview()
    if "preview" not in sys.argv:
        pdfs()
