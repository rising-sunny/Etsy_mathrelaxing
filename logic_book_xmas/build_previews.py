"""Etsy listing images (2000x2000) for the Christmas Logic Puzzles book, composited
from the real PDF pages (rendered at 200 dpi)."""
import os, sys, importlib.util
import fitz
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "advent_stem"))
import generate_advent as G
_spec = importlib.util.spec_from_file_location("advent_previews", os.path.join(HERE, "..", "advent_stem", "build_previews.py"))
_ap = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ap)
bg, place, banner, S = _ap.bg, _ap.place, _ap.banner, _ap.S

PDF = os.path.join(HERE, "out", "Christmas_Logic_Puzzles_Letter.pdf")
OUT = os.path.join(HERE, "out", "previews"); os.makedirs(OUT, exist_ok=True)
DOC = fitz.open(PDF)
# page index of each section (0-based)
P = {"cover": 0, "howto": 1, "contents": 2, "sudoku": 3, "sudoku_h": 16, "futoshiki": 18, "nonogram": 24,
     "nonogram2": 26, "logic": 34, "logic2": 37, "crypto": 40, "maze": 45, "maze2": 46, "maze3": 52, "maze4": 49,
     "teaser": 53, "sol_sudoku": 58, "sol_futo": 63, "sol_nono": 65, "sol_maze": 71}


def pg(n, dpi=200):
    pix = DOC[n].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def pill(d, text, y, fill=G.RED, size=58):
    f = G.font("bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle(((S - w) / 2 - 70, y, (S + w) / 2 + 70, y + 140), radius=70, fill=fill)
    d.text(((S - w) / 2, y + 36), text, font=f, fill=G.CREAM)


def hero():
    c = bg(); d = ImageDraw.Draw(c)
    place(c, pg(P["maze2"]), 760, (1080, 500), angle=-8)
    place(c, pg(P["nonogram"]), 760, (140, 450), angle=6)
    place(c, pg(P["cover"]), 840, (580, 330))
    pill(d, "101 PUZZLES  ·  SOLUTIONS INCLUDED", 1780)
    return c


def kinds():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "7 Kinds of Puzzles", "sudoku · futoshiki · nonograms · logic grids · cryptograms · mazes · teasers")
    picks = [("sudoku", "30 Sudoku"), ("futoshiki", "12 Futoshiki"), ("nonogram", "10 Nonograms"), ("logic", "6 Logic Grids"),
             ("crypto", "15 Cryptograms"), ("maze", "8 Mazes"), ("teaser", "20 Brain Teasers"), ("sol_sudoku", "Full Solutions")]
    w = 420; f = G.font("semi", 40)
    for i, (k, lab) in enumerate(picks):
        r, col = divmod(i, 4)
        x = 90 + col * 470; y = 380 + r * 760
        place(c, pg(P[k], 100), w, (x, y))
        d.text((x + (w - d.textlength(lab, font=f)) / 2, y + 565), lab, font=f, fill=G.INK)
    return c


def nonograms():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Reveal Hidden Pictures", "10 Christmas nonograms, solvable by pure logic")
    place(c, pg(P["nonogram2"]), 980, (90, 430), angle=3)
    place(c, pg(P["sol_nono"]), 900, (1030, 470), angle=-3)
    return c


def logic():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Clues, Codes & Pure Logic", "logic grids and cryptograms with public-domain quotes")
    place(c, pg(P["logic2"]), 960, (80, 430), angle=3)
    place(c, pg(P["crypto"]), 960, (960, 450), angle=-3)
    return c


def mazes():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Christmas-Shaped Mazes", "tree · ornament · star · snowman · gift · bell · stocking · house")
    place(c, pg(P["maze"]), 640, (90, 470), angle=4)
    place(c, pg(P["maze4"]), 640, (690, 430))
    place(c, pg(P["maze3"]), 640, (1280, 470), angle=-4)
    return c


def inside():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "What's Inside", "75 pages · US Letter + A4 · print at home")
    place(c, pg(P["contents"]), 860, (110, 420), angle=2)
    rows = ["30 Sudoku, easy to hard", "12 Futoshiki", "10 picture Nonograms", "6 Logic Grid stories",
            "15 Cryptograms", "8 shaped Mazes", "20 Christmas math teasers", "How-to-play guide",
            "Every solution explained"]
    f = G.font("semi", 50); y = 520
    for t in rows:
        d.ellipse((1080, y + 14, 1112, y + 46), fill=G.GOLD)
        d.text((1140, y), t, font=f, fill=G.NAVY); y += 128
    return c


def solutions():
    c = bg(); d = ImageDraw.Draw(c)
    banner(d, "Every Answer Included", "each puzzle checked by computer to have exactly one solution")
    place(c, pg(P["sol_sudoku"]), 640, (90, 470), angle=4)
    place(c, pg(P["sol_futo"]), 640, (690, 430))
    place(c, pg(P["sol_maze"]), 640, (1280, 470), angle=-4)
    pill(d, "INSTANT DOWNLOAD  ·  TEENS & ADULTS", 1780)
    return c


if __name__ == "__main__":
    for i, fn in enumerate((hero, kinds, nonograms, logic, mazes, inside, solutions), 1):
        p = os.path.join(OUT, f"{i:02d}_{fn.__name__}.jpg"); fn().save(p, quality=90); print("wrote", p)
