"""
build_palettes.py — "Chaos Theory" Procreate Color Palette pack (ultra low-cost)
================================================================================
Extrae paletas de color REALES de los art prints / animaciones de MathRelaxing
(atractores extraños y sistemas generativos) y las empaqueta como archivos
.swatches de Procreate. Angulo diferenciado: nadie mas en Etsy vende paletas
sacadas de sistemas dinamicos caoticos reales renderizados con codigo.

Cada paleta = 30 colores muestreados del render real (mediante quantizacion
adaptativa sobre las zonas con tinta, descartando el fondo negro para que la
paleta no salga toda negra), ordenados en una rampa por luminancia.

Salida en palettes/:
  swatches/<Nombre>.swatches      (los archivos vendibles, van en un zip)
  ChaosTheory_Palettes.zip         (deliverable: todos los .swatches juntos)
  previews/palette_preview_*.jpg   (imagenes para el listing de Etsy)

Reusa brand.swatches_file() (el escritor de .swatches ya existe en brand.py).
"""
import os
import colorsys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "palettes")
SW = os.path.join(OUT, "swatches")
PREV = os.path.join(OUT, "previews")
SRC = os.path.join(OUT, "_srcframes")

# palette name -> source image. Chosen for maximum colour variety across the set.
SOURCES = [
    ("Rossler Amber",      os.path.join(BASE, "attractor_prints", "rossler", "rossler_amber_print.jpg")),
    ("Rossler Rose",       os.path.join(BASE, "attractor_prints", "rossler", "rossler_violet_print.jpg")),
    ("Vector Field Teal",  os.path.join(BASE, "attractor_prints", "vector_field", "vectorfield_teal_print.jpg")),
    ("Vector Field Copper",os.path.join(BASE, "attractor_prints", "vector_field", "vectorfield_copper_print.jpg")),
    ("Vector Field Indigo",os.path.join(BASE, "attractor_prints", "vector_field", "vectorfield_indigo_print.jpg")),
    ("Voronoi Garden",     os.path.join(SRC, "voronoi.png")),
    ("De Jong Ice",        os.path.join(SRC, "dejong.png")),
    ("Julia Jade",         os.path.join(SRC, "julia.png")),
]

N_COLORS = 30
DARK_CUT = 22       # luminance below this = background, dropped before quantizing
KEEP_DARKS = 2      # re-inject a couple of real shadow tones (a palette needs darks)
KEEP_LIGHTS = 2     # and a couple of the brightest highlight tones for a full ramp


def _lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def _sat(arr):
    mx = arr.max(axis=1).astype(float)
    mn = arr.min(axis=1).astype(float)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)


def extract_palette(img_path, n=N_COLORS):
    im = Image.open(img_path).convert("RGB")
    im.thumbnail((460, 460))
    arr = np.asarray(im).reshape(-1, 3)
    lum = _lum(arr)
    sat = _sat(arr)

    # the vivid "ink": lit AND either saturated or a bright highlight. This
    # drops the muddy grey transitional pixels between the black background and
    # the coloured structure, which otherwise dominate the median-cut result
    # and make the palette look washed-out.
    vivid = arr[(lum > DARK_CUT) & ((sat > 0.18) | (lum > 175))]
    if len(vivid) < n * 25:                 # colourful image, or sparse structure
        vivid = arr[lum > DARK_CUT]
    if len(vivid) < n * 25:                 # last resort: everything
        vivid = arr

    body = max(2, n - KEEP_DARKS - KEEP_LIGHTS)
    q_im = Image.fromarray(vivid.reshape(-1, 1, 3).astype(np.uint8))
    q = q_im.quantize(colors=body, method=Image.MEDIANCUT)
    pal = np.array(q.getpalette()[: body * 3]).reshape(-1, 3)

    order = np.argsort(lum)
    darks = arr[order[: max(1, len(arr) // 200)]]
    dq = Image.fromarray(darks.reshape(-1, 1, 3).astype(np.uint8)).quantize(colors=KEEP_DARKS, method=Image.MEDIANCUT)
    dpal = np.array(dq.getpalette()[: KEEP_DARKS * 3]).reshape(-1, 3)

    lights = arr[order[-max(1, len(arr) // 400):]]
    lq = Image.fromarray(lights.reshape(-1, 1, 3).astype(np.uint8)).quantize(colors=KEEP_LIGHTS, method=Image.MEDIANCUT)
    lpal = np.array(lq.getpalette()[: KEEP_LIGHTS * 3]).reshape(-1, 3)

    cols = np.vstack([dpal, pal, lpal])
    # de-dup near-identical, then sort into a value ramp for a clean display
    seen, uniq = set(), []
    for c in cols:
        key = tuple((c // 8))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    uniq = sorted(uniq, key=lambda c: _lum(np.array(c, dtype=float)))
    # pad if de-dup left us short
    while len(uniq) < n:
        uniq.append(uniq[-1])
    uniq = uniq[:n]
    return ["#%02x%02x%02x" % (int(c[0]), int(c[1]), int(c[2])) for c in uniq]


def swatch_card(name, hexes, w=760, cols=6):
    """A single palette shown as a labelled grid — one Etsy preview per palette."""
    rows = (len(hexes) + cols - 1) // cols
    pad, gap, cell = 40, 10, 100
    h = pad * 2 + 60 + rows * cell + (rows - 1) * gap
    img = Image.new("RGB", (w, h), (18, 23, 45))          # brand IPAD_NAVY-ish
    d = ImageDraw.Draw(img)
    d.text((pad, 30), name.upper(), fill=(248, 244, 235))
    d.text((pad, 52), "30 colours · Procreate .swatches", fill=(201, 162, 75))
    gw = cols * cell + (cols - 1) * gap
    x0 = (w - gw) // 2
    y0 = pad + 60
    for i, hx in enumerate(hexes):
        r, c = divmod(i, cols)
        x = x0 + c * (cell + gap)
        y = y0 + r * (cell + gap)
        rgb = tuple(int(hx[j:j + 2], 16) for j in (1, 3, 5))
        d.rectangle([x, y, x + cell, y + cell], fill=rgb)
    return img


def main():
    os.makedirs(SW, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)

    palettes = []
    for name, path in SOURCES:
        hexes = extract_palette(path)
        brand.swatches_file(os.path.join(SW, f"{name}.swatches"), name, hexes)
        palettes.append((name, hexes))
        card = swatch_card(name, hexes)
        card.save(os.path.join(PREV, f"palette_{name.replace(' ', '_')}.jpg"), quality=90)
        print(f"  {name}: {len(hexes)} colores")

    # zip deliverable
    zip_path = os.path.join(OUT, "ChaosTheory_Palettes.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, _ in palettes:
            z.write(os.path.join(SW, f"{name}.swatches"), f"{name}.swatches")
        # a small readme in the zip
        z.writestr("HOW TO INSTALL.txt",
                   "Chaos Theory — Procreate Color Palettes by MathRelaxing\n"
                   "=======================================================\n\n"
                   "Each .swatches file is a 30-colour palette extracted from a real\n"
                   "chaotic dynamical system (a strange attractor / generative render),\n"
                   "computed in Python — not sampled from stock or AI.\n\n"
                   "TO INSTALL (Procreate on iPad):\n"
                   "  1. Save the .swatches files to your iPad (Files app / iCloud).\n"
                   "  2. Open Procreate. Tap the colour circle (top right) > Palettes.\n"
                   "  3. Tap the + at the top right > 'New from file'.\n"
                   "  4. Pick a .swatches file. It appears as a new 30-colour palette.\n\n"
                   "Also works in any app that reads Procreate .swatches files.\n\n"
                   "For personal & commercial artwork. Do not resell or redistribute\n"
                   "the palette files themselves.\n"
                   "© MathRelaxing · mathrelaxing.store\n")
    print(f"Zip: {zip_path}  ({os.path.getsize(zip_path)} bytes)")

    build_hero(palettes)
    print(f"Listo: {len(palettes)} paletas en {OUT}")


def build_hero(palettes):
    """Listing hero: all palettes as horizontal ramps, stacked, on brand navy."""
    W = 1200
    row_h, pad, top = 116, 60, 150
    H = top + len(palettes) * row_h + 60
    img = Image.new("RGB", (W, H), (13, 17, 36))
    d = ImageDraw.Draw(img)
    d.text((pad, 46), "CHAOS THEORY", fill=(248, 244, 235))
    d.text((pad, 82), "8 Procreate Color Palettes · extracted from real strange attractors",
           fill=(201, 162, 75))
    sw = 30
    ramp_w = W - pad * 2 - 250
    for i, (name, hexes) in enumerate(palettes):
        y = top + i * row_h
        d.text((pad, y + row_h // 2 - 16), name, fill=(230, 232, 240))
        x0 = pad + 250
        cw = ramp_w / len(hexes)
        for j, hx in enumerate(hexes):
            rgb = tuple(int(hx[k:k + 2], 16) for k in (1, 3, 5))
            x = x0 + j * cw
            d.rectangle([x, y + 20, x + cw + 1, y + row_h - 24], fill=rgb)
    if os.path.exists(brand.LOGO_PATH):
        logo = Image.open(brand.LOGO_PATH).convert("RGBA")
        lw = 150
        logo = logo.resize((lw, int(lw * logo.height / logo.width)))
        img.paste(logo, (W // 2 - lw // 2, H - 60), logo)
    img.save(os.path.join(PREV, "palette_preview_1_hero.jpg"), quality=90)


if __name__ == "__main__":
    main()
