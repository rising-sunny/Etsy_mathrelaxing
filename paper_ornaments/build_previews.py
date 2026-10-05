"""Etsy listing images (2000x2000) for the Geometric 3D Paper Ornaments pack."""
import os, sys, importlib.util
import fitz
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(REPO, "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
bg, place, banner, S = _ap.bg, _ap.place, _ap.banner, _ap.S

OUT = os.path.join(HERE, "out"); PREV = os.path.join(OUT, "previews"); os.makedirs(PREV, exist_ok=True)
R3 = os.path.join(OUT, "renders")
DOC = fitz.open(os.path.join(OUT, "Geometric_Paper_Ornaments_Letter.pdf"))
NAVYBG = (24, 36, 64)


def pg(n, dpi=170):
    pix = DOC[n].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def find(title):
    for i, p in enumerate(DOC):
        t = p.get_text()
        if t.split("\n")[0].replace("\xa0", " ").strip().lower() == title.lower():
            return i
    raise KeyError(title)


def rnd(name, size):
    im = Image.open(os.path.join(R3, name.replace(" ", "_") + ".png")).convert("RGB")
    w, h = im.size; im = im.crop((int(w * 0.08), int(h * 0.08), int(w * 0.92), int(h * 0.92)))
    return im.resize((size, size), Image.LANCZOS)


def pill(d, text, y, fill=G.RED, size=58, fg=None):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 140), radius=70, fill=fill)
    d.text(((S - w) / 2, y + 36), text, font=f, fill=fg or G.CREAM)


def hero():
    c = Image.new("RGB", (S, S), NAVYBG); d = ImageDraw.Draw(c)
    names = ["Tetrahedron", "Cube", "Octahedron", "Dodecahedron", "Icosahedron", "Cuboctahedron",
             "Truncated Octahedron", "Rhombicuboctahedron", "Truncated Icosahedron", "Stella Octangula", "Kepler Star", "Moravian Star"]
    cell = 470
    for i, n in enumerate(names):
        r, col = divmod(i, 4)
        c.paste(rnd(n, cell), (60 + col * cell, 70 + r * cell))
    f = G.font("cinzel", 112); t = "GEOMETRIC 3D ORNAMENTS"
    d.text(((S - d.textlength(t, font=f)) / 2, 1520), t, font=f, fill=G.CREAM)
    f2 = G.font("semi", 54); t2 = "12 printable paper polyhedra & star templates"
    d.text(((S - d.textlength(t2, font=f2)) / 2, 1665), t2, font=f2, fill=G.GOLD)
    pill(d, "PDF + SVG  ·  COLOUR & WHITE  ·  INSTANT DOWNLOAD", 1790, size=50)
    return c


def templates():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Real-Size Templates", "print, score, cut, fold & glue")
    place(c, pg(find("Rhombicuboctahedron")), 700, (90, 450), angle=6)
    place(c, pg(find("Icosahedron")), 700, (1210, 450), angle=-6)
    place(c, pg(find("Dodecahedron")), 760, (620, 380))
    return c


def stars():
    c = Image.new("RGB", (S, S), NAVYBG); d = ImageDraw.Draw(c)
    f = G.font("cinzel", 100); t = "3 Christmas Stars"
    d.text(((S - d.textlength(t, font=f)) / 2, 90), t, font=f, fill=G.CREAM)
    f2 = G.font("semi", 50); t2 = "including the 26-point Moravian Advent star"
    d.text(((S - d.textlength(t2, font=f2)) / 2, 225), t2, font=f2, fill=G.GOLD)
    c.paste(rnd("Moravian Star", 1150), (425, 330))
    c.paste(rnd("Kepler Star", 560), (40, 1380))
    c.paste(rnd("Stella Octangula", 560), (1400, 1380))
    fl = G.font("bold", 46)
    for x, s in ((320, "Kepler star"), (1680, "Stella octangula"), (1000, "Moravian star")):
        d.text((x - d.textlength(s, font=fl) / 2, 1900 if x != 1000 else 1480), s, font=fl, fill=G.CREAM)
    return c


def flat_to_3d():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "From Flat to 3D", "every net is computed from exact geometry")
    place(c, pg(find("Truncated Icosahedron")), 880, (80, 430), angle=3)
    r = rnd("Truncated Icosahedron", 820)
    disc = Image.new("L", r.size, 0); ImageDraw.Draw(disc).ellipse((0, 0, r.size[0], r.size[1]), fill=255)
    c.paste(r, (1100, 620), disc)
    d.polygon([(985, 1000), (1075, 1040), (985, 1080)], fill=G.RED)
    d.line((900, 1040, 1000, 1040), fill=G.RED, width=18)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "40 pages · US Letter + A4 · SVG cut files")
    place(c, pg(1), 860, (110, 420), angle=2)
    rows = ["5 Platonic solids", "4 Archimedean solids", "3 Christmas stars", "Colour templates with snowflakes",
            "Plain white templates", "Step-by-step instructions", "The math behind each shape", "SVG files for Cricut",
            "Finished size 8-12 cm"]
    f = G.font("semi", 50); y = 500
    for t in rows:
        d.ellipse((1080, y + 14, 1112, y + 46), fill=G.GOLD)
        d.text((1140, y), t, font=f, fill=G.NAVY); y += 128
    return c


def white_svg():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "White Templates & SVG Files", "for coloured or metallic card and cutting machines")
    place(c, pg(find("Plain White Templates") + 4), 760, (110, 430), angle=3)
    place(c, pg(find("Plain White Templates") + 8), 760, (1100, 450), angle=-3)
    pill(d, "CRICUT & SILHOUETTE READY", 1790, fill=G.PINE)
    return c


def maths():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Real Mathematics, Made Beautiful", "Platonic & Archimedean solids, Euler, Kepler and the golden ratio")
    place(c, pg(3), 900, (100, 440), angle=2)
    place(c, pg(2), 900, (1000, 460), angle=-2)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, templates, stars, flat_to_3d, inside, white_svg, maths), 1):
        p = os.path.join(PREV, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
