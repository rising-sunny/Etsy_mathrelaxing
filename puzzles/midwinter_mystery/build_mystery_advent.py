"""
build_mystery_advent.py — "The Midwinter Theorem": a printable 24-day murder
mystery logic-puzzle advent calendar.

Mechanics
---------
* 36 suspects, each a unique combination of 5 attributes.
* Every day has a code-generated logic puzzle (Sudoku / Futoshiki /
  Skyscrapers) with a UNIQUE solution (verified by an exhaustive solver).
* The digit in the starred cell picks which of the day's numbered statements
  is TRUE. The true statements are chosen by a clue engine so that, after day
  24, exactly one suspect remains. Every decoy statement is false for the
  culprit, so a wrong answer leads to a contradiction (self-checking).

  python puzzles/midwinter_mystery/build_mystery_advent.py            # Letter + A4 PDFs
  python puzzles/midwinter_mystery/build_mystery_advent.py --seed 7
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "out")
FONTS = os.path.join(ROOT, "lulu_books", "assets", "fonts")
LOGO = os.path.join(ROOT, "mathrelaxing_logo.png")

NAVY = HexColor("#13192e")
WINE = HexColor("#5a1a24")
GOLD = HexColor("#c9a24b")
CREAM = HexColor("#f8f4eb")
INK = HexColor("#1d1d1f")
SOFT = HexColor("#6b6458")
SHADE = HexColor("#efe7d4")
COPYRIGHT = "© MathRelaxing. For personal use only. Not for redistribution or resale."

# ── Cast ─────────────────────────────────────────────────────────────────────
ATTRS = {
    "dept": ["Algebra", "Geometry", "Analysis", "Topology", "Number Theory", "Statistics"],
    "loc": ["Library", "Observatory", "Ballroom", "Conservatory", "Billiard Room", "Chapel"],
    "acc": ["Scarf", "Pocket Watch", "Spectacles", "Fountain Pen", "Walking Cane", "Bow Tie"],
    "drink": ["Earl Grey", "Black Coffee", "Hot Cocoa", "Mulled Wine"],
    "arr": ["7:00", "7:30", "8:00", "8:30", "9:00", "9:30"],
}
NAMES = [
    "Dr. Iris Calloway", "Prof. Edmund Hale", "Miss Clara Winslow", "Mr. Felix Dunmore",
    "Dr. Agnes Pemberton", "Prof. Rupert Ashby", "Mrs. Lydia Fairfax", "Mr. Theodore Quill",
    "Dr. Margot Ellery", "Prof. Silas Wren", "Miss Harriet Vance", "Mr. Oliver Crane",
    "Dr. Beatrix Holm", "Prof. Ansel Marchetti", "Mrs. Eloise Tran", "Mr. Gideon Pratt",
    "Dr. Nadia Okafor", "Prof. Leopold Brandt", "Miss Rosalind Kerr", "Mr. Jasper Thorne",
    "Dr. Vivian Sato", "Prof. Cornelius Bell", "Mrs. Ottilie Grey", "Mr. Barnaby Fitch",
    "Dr. Helena Moreau", "Prof. Ignatius Lowe", "Miss Philippa Shaw", "Mr. Lucian Hargrove",
    "Dr. Estelle Park", "Prof. Hugo Lindqvist", "Mrs. Constance Reed", "Mr. Percival Oates",
    "Dr. Matilda Fenn", "Prof. Victor Abernathy", "Miss Josephine Lark", "Mr. Ambrose Kettle",
]

STORY = [
    "Snow sealed the roads to Ashcombe Hall on the night of the Midwinter Gala. At midnight the "
    "Society's president, Professor Ambrose Vale, was found dead beside his notebook, the final "
    "page torn out. He had promised to reveal a proof of the Midwinter Conjecture at dawn.",
    "The butler confirms the doors were bolted from eleven o'clock. Whoever silenced Vale never "
    "left the Hall. Thirty-six guests remain snowed in, and every one of them had heard of the proof.",
    "Vale's teacup was still warm when he was found. The kitchen kept a careful record of what each "
    "guest drank that evening, and the housekeeper is willing to talk.",
    "A trail of wet footprints crosses the marble floor and fades near the grand staircase. "
    "Someone came in from the cold not long before midnight.",
    "In the margins of Vale's notebook: a column of crossed-out names and a single underlined word, "
    "'betrayal'. He suspected someone close to him.",
    "The guest book is water-stained but legible. Arrival times can be trusted, the porter insists; "
    "he wrote each one down himself.",
    "A cracked pocket mirror lies under the piano. The pianist swears it was not there during the waltz.",
    "The torn page left an impression on the sheet below. Rubbed with pencil, it shows a lattice of "
    "numbers, the start of the proof.",
    "Two guests quarrelled loudly in the corridor at half past ten. Neither will say what about.",
    "The observatory telescope was turned away from the stars and toward the east wing windows. "
    "Someone was watching the Hall rather than the sky.",
    "Vale's will was amended last week. The solicitor, stranded with everyone else, is nervous.",
    "The chapel candles were relit after the evening service. Wax drips on the floor are still soft.",
    "A frost-rimed window in the conservatory has been forced from the inside, but the snow beneath "
    "it is untouched. A false trail.",
    "The housekeeper recalls a guest asking, twice, where the president would be sitting at midnight.",
    "Among the billiard balls one is missing. It turns up later, wrapped in a handkerchief, in a coat pocket.",
    "A letter in Vale's desk, unsent: 'If anything should happen to me, look to the one who "
    "counts the hours.'",
    "The library ledger shows a rare volume on lattice theory borrowed at nine and never returned.",
    "Half the guests have gone to bed. The other half are watching each other over cold coffee. "
    "The suspect list is shrinking.",
    "The torn page is found at last, burned to a curl in the ballroom grate. Only a few symbols survive.",
    "A guest tries to leave on foot through the snow and is brought back, shivering, by the gardener.",
    "The pattern is clear now. The killer knew the proof was real and wanted the credit.",
    "Only a handful of names remain on your list. Each of them is watching the door.",
    "On the eve of Christmas Eve, the last few alibis are about to crumble. Tomorrow you will know.",
    "One final clue. When this puzzle is solved, exactly one name will remain on your list. "
    "Write it down, then turn to the sealed Final Reveal.",
]


# ── Puzzle engine ────────────────────────────────────────────────────────────
def box_shape(n):
    return {4: (2, 2), 6: (2, 3)}.get(n)


def sky_view(line):
    seen, best = 0, 0
    for v in line:
        if v > best:
            seen, best = seen + 1, v
    return seen


def count_solutions(p, limit=2, out=None):
    """p: dict(kind, n, givens{(r,c):v}, ineq[((r,c),(r2,c2))] a<b, sky{top,bottom,left,right})."""
    n, kind = p["n"], p["kind"]
    grid = [[0] * n for _ in range(n)]
    for (r, c), v in p.get("givens", {}).items():
        grid[r][c] = v
    bs = box_shape(n) if kind == "sudoku" else None
    ineq = p.get("ineq", [])
    sky = p.get("sky")
    cells = [(r, c) for r in range(n) for c in range(n) if not grid[r][c]]
    count = 0

    def ok(r, c, v):
        if any(grid[r][j] == v for j in range(n)) or any(grid[i][c] == v for i in range(n)):
            return False
        if bs:
            br, bc = r // bs[0] * bs[0], c // bs[1] * bs[1]
            for i in range(br, br + bs[0]):
                for j in range(bc, bc + bs[1]):
                    if grid[i][j] == v:
                        return False
        grid[r][c] = v
        good = True
        for a, b in ineq:
            va, vb = grid[a[0]][a[1]], grid[b[0]][b[1]]
            if va and vb and not va < vb:
                good = False
                break
        if good and sky:
            row = grid[r]
            if all(row):
                if (sky["left"][r] and sky_view(row) != sky["left"][r]) or \
                   (sky["right"][r] and sky_view(row[::-1]) != sky["right"][r]):
                    good = False
            col = [grid[i][c] for i in range(n)]
            if good and all(col):
                if (sky["top"][c] and sky_view(col) != sky["top"][c]) or \
                   (sky["bottom"][c] and sky_view(col[::-1]) != sky["bottom"][c]):
                    good = False
        grid[r][c] = 0
        return good

    def rec(k):
        nonlocal count
        if count >= limit:
            return
        if k == len(cells):
            count += 1
            if out is not None and count == 1:
                out[:] = [row[:] for row in grid]
            return
        r, c = cells[k]
        for v in range(1, n + 1):
            if ok(r, c, v):
                grid[r][c] = v
                rec(k + 1)
                grid[r][c] = 0

    rec(0)
    return count


def solve(p):
    """Return the first solution found by the exhaustive solver."""
    out = []
    count_solutions(p, 1, out)
    return out


def random_solution(n, kind, rng):
    grid = [[0] * n for _ in range(n)]
    bs = box_shape(n) if kind == "sudoku" else None

    def ok(r, c, v):
        if v in grid[r] or any(grid[i][c] == v for i in range(n)):
            return False
        if bs:
            br, bc = r // bs[0] * bs[0], c // bs[1] * bs[1]
            return all(grid[i][j] != v for i in range(br, br + bs[0]) for j in range(bc, bc + bs[1]))
        return True

    def rec(k):
        if k == n * n:
            return True
        r, c = divmod(k, n)
        vals = list(range(1, n + 1))
        rng.shuffle(vals)
        for v in vals:
            if ok(r, c, v):
                grid[r][c] = v
                if rec(k + 1):
                    return True
                grid[r][c] = 0
        return False

    rec(0)
    return grid


def make_puzzle(kind, n, level, rng):
    """level 0..1 → fewer hints. Returns puzzle dict with 'solution'."""
    sol = random_solution(n, kind, rng)
    allg = {(r, c): sol[r][c] for r in range(n) for c in range(n)}
    p = {"kind": kind, "n": n, "givens": {}}
    if kind == "sudoku":
        p["givens"] = dict(allg)
        target = int(n * n * (0.55 - 0.25 * level))
        removable = list(allg)
        rng.shuffle(removable)
        for cell in removable:
            if len(p["givens"]) <= target:
                break
            v = p["givens"].pop(cell)
            if count_solutions(p) != 1:
                p["givens"][cell] = v
    elif kind == "futoshiki":
        pairs = []
        for r in range(n):
            for c in range(n):
                for dr, dc in ((0, 1), (1, 0)):
                    r2, c2 = r + dr, c + dc
                    if r2 < n and c2 < n:
                        a, b = (r, c), (r2, c2)
                        pairs.append((a, b) if sol[r][c] < sol[r2][c2] else (b, a))
        p["ineq"] = pairs
        cells = list(allg)
        rng.shuffle(cells)
        while count_solutions(p) != 1:
            cell = cells.pop()
            p["givens"][cell] = allg[cell]
        target = int(len(pairs) * (0.45 - 0.2 * level))
        order = list(pairs)
        rng.shuffle(order)
        for pr in order:
            if len(p["ineq"]) <= target:
                break
            p["ineq"].remove(pr)
            if count_solutions(p) != 1:
                p["ineq"].append(pr)
    elif kind == "skyscrapers":
        sky = {"top": [sky_view([sol[r][c] for r in range(n)]) for c in range(n)],
               "bottom": [sky_view([sol[r][c] for r in range(n)][::-1]) for c in range(n)],
               "left": [sky_view(sol[r]) for r in range(n)],
               "right": [sky_view(sol[r][::-1]) for r in range(n)]}
        p["sky"] = sky
        cells = list(allg)
        rng.shuffle(cells)
        while count_solutions(p) != 1:
            cell = cells.pop()
            p["givens"][cell] = allg[cell]
        edges = [(s, i) for s in sky for i in range(n)]
        rng.shuffle(edges)
        target = int(4 * n * (0.7 - 0.3 * level))
        for s, i in edges:
            if sum(1 for v in itertools.chain(*sky.values()) if v) <= target:
                break
            v, sky[s][i] = sky[s][i], 0
            if count_solutions(p) != 1:
                sky[s][i] = v
    assert count_solutions(p) == 1
    p["solution"] = sol
    return p


# ── Clue engine ──────────────────────────────────────────────────────────────
def build_cast(rng):
    combos = list(itertools.product(*(range(len(v)) for v in ATTRS.values())))
    rng.shuffle(combos)
    picked = []
    # spread: avoid too-similar suspects (need ≥2 differing attrs)
    for cmb in combos:
        if all(sum(a != b for a, b in zip(cmb, q)) >= 2 for q in picked):
            picked.append(cmb)
        if len(picked) == 36:
            break
    names = NAMES[:]
    rng.shuffle(names)
    keys = list(ATTRS)
    return [dict(id=i + 1, name=names[i], **{k: v for k, v in zip(keys, cmb)})
            for i, cmb in enumerate(picked)]


def clue_pool():
    A = ATTRS
    pool = []
    for i, v in enumerate(A["loc"]):
        pool.append((f"The culprit was not in the {v} at midnight.", lambda s, i=i: s["loc"] != i))
    for i, v in enumerate(A["dept"]):
        pool.append((f"The culprit does not work in {v}.", lambda s, i=i: s["dept"] != i))
    for i, v in enumerate(A["acc"]):
        art = "an" if v[0] in "AEIOU" else "a"
        pool.append((f"The culprit was not carrying {art} {v.lower()}.", lambda s, i=i: s["acc"] != i))
    for i, v in enumerate(A["drink"]):
        pool.append((f"The culprit was not drinking {v}.", lambda s, i=i: s["drink"] != i))
    for t in range(1, 6):
        pool.append((f"The culprit arrived at {A['arr'][t]} or later.", lambda s, t=t: s["arr"] >= t))
        pool.append((f"The culprit arrived before {A['arr'][t]}.", lambda s, t=t: s["arr"] < t))
    for (i, a), (j, b) in itertools.combinations(enumerate(A["loc"]), 2):
        pool.append((f"At midnight the culprit was in either the {a} or the {b}.",
                     lambda s, i=i, j=j: s["loc"] in (i, j)))
    for (i, a), (j, b) in itertools.combinations(enumerate(A["dept"]), 2):
        pool.append((f"The culprit works in either {a} or {b}.", lambda s, i=i, j=j: s["dept"] in (i, j)))
    for (i, d), (t, tm) in itertools.product(enumerate(A["drink"]), list(enumerate(A["arr"]))[1:]):
        pool.append((f"If the culprit drank {d}, they arrived before {tm}.",
                     lambda s, i=i, t=t: s["drink"] != i or s["arr"] < t))
    for (i, dp), (j, ac) in itertools.product(enumerate(A["dept"]), enumerate(A["acc"])):
        pool.append((f"The culprit is not a {dp} scholar carrying a {ac.lower()}.",
                     lambda s, i=i, j=j: not (s["dept"] == i and s["acc"] == j)))
    for (i, lc), (j, dr) in itertools.product(enumerate(A["loc"]), enumerate(A["drink"])):
        pool.append((f"Nobody drinking {dr} in the {lc} is guilty.",
                     lambda s, i=i, j=j: not (s["loc"] == i and s["drink"] == j)))
    pool.append(("The culprit's first name has more than five letters.",
                 lambda s: len(s["name"].split()[1]) > 5))
    pool.append(("The culprit's first name has five letters or fewer.",
                 lambda s: len(s["name"].split()[1]) <= 5))
    for t, title in (("Dr.", "doctor"), ("Prof.", "professor")):
        pool.append((f"The culprit is not a {title}.", lambda s, t=t: not s["name"].startswith(t)))
    return pool


def plan_clues(cast, rng, days=24):
    pool = clue_pool()
    for _ in range(4000):
        culprit = rng.choice(cast)
        alive = list(cast)
        chosen = []
        used = set()
        okrun = True
        for k in range(1, days + 1):
            floor = days + 1 - k  # leave room for one elimination per remaining day
            target = max(floor, round(36 * (1 / 36) ** (k / days)))
            cands = []
            for idx, (txt, f) in enumerate(pool):
                if idx in used or not f(culprit):
                    continue
                rem = [s for s in alive if f(s)]
                if len(rem) == len(alive):
                    continue
                if len(rem) < floor:
                    continue
                if k == days and len(rem) != 1:
                    continue
                cands.append((abs(len(rem) - target) + rng.random() * 0.8, idx, rem))
            if not cands:
                okrun = False
                break
            cands.sort(key=lambda x: x[0])
            _, idx, rem = cands[0]
            used.add(idx)
            chosen.append(idx)
            alive = rem
        if okrun and len(alive) == 1 and alive[0] is culprit:
            return culprit, [pool[i] for i in chosen], pool, used
    raise RuntimeError("clue plan failed")


def decoys(pool, culprit, used, n, rng, usage):
    """n statements that are FALSE for the culprit (never a true-chain clue);
    least-used first so repeats across days are rare."""
    false_ = [i for i, (t, f) in enumerate(pool) if not f(culprit) and i not in used]
    rng.shuffle(false_)
    false_.sort(key=lambda i: usage.get(i, 0))
    pick = false_[:n]
    for i in pick:
        usage[i] = usage.get(i, 0) + 1
    return [pool[i][0] for i in pick]


# ── Plan the calendar ────────────────────────────────────────────────────────
SCHEDULE = (  # (kind, n, level) per day — gentle start, tougher finish
    [("sudoku", 4, 0.0), ("futoshiki", 4, 0.0), ("skyscrapers", 4, 0.0)] * 2
    + [("sudoku", 6, 0.2), ("futoshiki", 5, 0.2), ("skyscrapers", 5, 0.2)] * 3
    + [("sudoku", 6, 0.6), ("futoshiki", 5, 0.6), ("skyscrapers", 5, 0.6)] * 2
    + [("sudoku", 6, 1.0), ("futoshiki", 5, 1.0), ("skyscrapers", 5, 1.0)]
)


def plan(seed):
    rng = random.Random(seed)
    cast = build_cast(rng)
    culprit, true_clues, pool, used = plan_clues(cast, rng)
    days = []
    usage = {}
    for d, ((kind, n, level), (ttxt, _)) in enumerate(zip(SCHEDULE, true_clues), start=1):
        p = make_puzzle(kind, n, level, rng)
        sol = p["solution"]
        open_cells = [(r, c) for r in range(n) for c in range(n) if (r, c) not in p["givens"]]
        star = rng.choice(open_cells)
        k = sol[star[0]][star[1]]
        opts = decoys(pool, culprit, used, n - 1, rng, usage)
        opts.insert(k - 1, ttxt)
        days.append(dict(day=d, puzzle=p, star=star, answer=k, options=opts, story=STORY[d - 1]))
    # self-check: applying each day's true clue leaves exactly the culprit
    alive = cast
    for (txt, f) in true_clues:
        alive = [s for s in alive if f(s)]
    assert [s["id"] for s in alive] == [culprit["id"]]
    return cast, culprit, days


# ── Rendering ────────────────────────────────────────────────────────────────
def register_fonts():
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(FONTS, "Cinzel-SemiBold.ttf")))
    # Raleway.ttf is a variable font: reportlab renders its hairline master, so use Liberation Sans
    pdfmetrics.registerFont(TTFont("Raleway", "LiberationSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("RalewayIt", "LiberationSans-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuB", "DejaVuSans-Bold.ttf"))


def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(c, text, x, y, width, font="Raleway", size=10.5, lead=1.45, color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= size * lead
    return y


KIND_RULES = {
    "sudoku": "Fill the grid so every row, column and outlined box contains each number exactly once.",
    "futoshiki": "Fill the grid so every row and column contains each number once. Every inequality sign "
                 "between two cells, across or down, must be obeyed: it always points at the smaller number.",
    "skyscrapers": "Each number is a building of that height; every row and column holds each height "
                   "once. A number outside the grid says how many buildings you can see from that side "
                   "(taller ones hide shorter ones behind them).",
}


def draw_grid(c, p, x0, y0, size, star=None, show=False):
    """x0,y0 = top-left of the grid square."""
    n = p["n"]
    cs = size / n
    font = "DejaVuB"
    # star cell
    if star:
        r, cc = star
        c.setFillColor(SHADE)
        c.rect(x0 + cc * cs, y0 - (r + 1) * cs, cs, cs, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("DejaVu", cs * 0.32)
        c.drawString(x0 + cc * cs + cs * 0.06, y0 - r * cs - cs * 0.34, "★")
    c.setStrokeColor(INK)
    gap = cs * 0.22 if p["kind"] == "futoshiki" else 0
    if p["kind"] == "futoshiki":
        for r in range(n):
            for cc in range(n):
                c.setLineWidth(1.1)
                c.rect(x0 + cc * cs + gap / 2, y0 - (r + 1) * cs + gap / 2, cs - gap, cs - gap, fill=0)
    else:
        for i in range(n + 1):
            c.setLineWidth(0.6)
            c.line(x0, y0 - i * cs, x0 + size, y0 - i * cs)
            c.line(x0 + i * cs, y0, x0 + i * cs, y0 - size)
        bs = box_shape(n) if p["kind"] == "sudoku" else None
        c.setLineWidth(2.2)
        c.rect(x0, y0 - size, size, size, fill=0)
        if bs:
            for i in range(bs[0], n, bs[0]):
                c.line(x0, y0 - i * cs, x0 + size, y0 - i * cs)
            for j in range(bs[1], n, bs[1]):
                c.line(x0 + j * cs, y0, x0 + j * cs, y0 - size)
    # numbers
    for (r, cc), v in p["givens"].items():
        c.setFillColor(INK)
        c.setFont(font, cs * 0.5)
        c.drawCentredString(x0 + (cc + 0.5) * cs, y0 - (r + 0.68) * cs, str(v))
    if show:
        for r in range(n):
            for cc in range(n):
                if (r, cc) not in p["givens"]:
                    c.setFillColor(SOFT)
                    c.setFont("DejaVu", cs * 0.45)
                    c.drawCentredString(x0 + (cc + 0.5) * cs, y0 - (r + 0.66) * cs, str(p["solution"][r][cc]))
    if p["kind"] == "futoshiki":
        c.setFillColor(INK)
        c.setFont("DejaVuB", cs * 0.3)
        for (a, b) in p["ineq"]:
            (r1, c1), (r2, c2) = a, b  # value a < value b
            if r1 == r2:  # horizontal
                x = x0 + max(c1, c2) * cs
                y = y0 - (r1 + 0.6) * cs
                c.drawCentredString(x, y, "<" if c1 < c2 else ">")
            else:  # vertical
                x = x0 + (c1 + 0.5) * cs
                y = y0 - max(r1, r2) * cs - cs * 0.1
                c.drawCentredString(x, y, "∧" if r1 < r2 else "∨")
    if p["kind"] == "skyscrapers":
        sky = p["sky"]
        c.setFillColor(WINE)
        c.setFont("DejaVuB", cs * 0.42)
        for i in range(n):
            if sky["top"][i]:
                c.drawCentredString(x0 + (i + 0.5) * cs, y0 + cs * 0.25, str(sky["top"][i]))
            if sky["bottom"][i]:
                c.drawCentredString(x0 + (i + 0.5) * cs, y0 - size - cs * 0.5, str(sky["bottom"][i]))
            if sky["left"][i]:
                c.drawCentredString(x0 - cs * 0.4, y0 - (i + 0.66) * cs, str(sky["left"][i]))
            if sky["right"][i]:
                c.drawCentredString(x0 + size + cs * 0.4, y0 - (i + 0.66) * cs, str(sky["right"][i]))


def footer(c, W, page_label=""):
    c.setFillColor(SOFT)
    c.setFont("Raleway", 7.5)
    c.drawCentredString(W / 2, 0.42 * inch, f"The Midwinter Theorem  ·  MathRelaxing  {page_label}")


def page_header(c, W, H, title, sub=None, band=WINE):
    c.setFillColor(band)
    c.rect(0, H - 1.05 * inch, W, 1.05 * inch, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Cinzel", 22)
    c.drawCentredString(W / 2, H - 0.62 * inch, title)
    if sub:
        c.setFillColor(GOLD)
        c.setFont("Raleway", 10)
        c.drawCentredString(W / 2, H - 0.88 * inch, sub)


def render(cast, culprit, days, size, path):
    W, H = size
    M = 0.7 * inch
    c = canvas.Canvas(path, pagesize=size)
    c.setTitle("The Midwinter Theorem — Murder Mystery Advent Calendar")
    c.setAuthor("MathRelaxing")

    # Cover
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    rng = random.Random(3)
    c.setFillColor(CREAM)
    for _ in range(140):
        x, y, r = rng.uniform(0, W), rng.uniform(1.3 * inch, H), rng.uniform(0.6, 2.2)
        c.setFillAlpha(rng.uniform(0.2, 0.8))
        c.circle(x, y, r, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.rect(M * 0.6, M * 0.6 + 1.0 * inch, W - 1.2 * M, H - 1.2 * M - 1.0 * inch, fill=0)
    c.setFillColor(GOLD)
    c.setFont("Raleway", 12)
    c.drawCentredString(W / 2, H * 0.80, "A 24-DAY MURDER MYSTERY ADVENT CALENDAR")
    c.setFillColor(CREAM)
    c.setFont("Cinzel", 40)
    c.drawCentredString(W / 2, H * 0.69, "THE MIDWINTER")
    c.drawCentredString(W / 2, H * 0.62, "THEOREM")
    c.setFillColor(GOLD)
    c.setFont("RalewayIt", 13)
    c.drawCentredString(W / 2, H * 0.555, "36 suspects · 24 logic puzzles · 1 killer")
    # lattice emblem
    cx, cy, s = W / 2, H * 0.38, 1.25 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    for i in range(7):
        c.line(cx - s + i * s / 3, cy - s, cx - s + i * s / 3, cy + s)
        c.line(cx - s, cy - s + i * s / 3, cx + s, cy - s + i * s / 3)
    c.setFillColor(GOLD)
    c.setFont("DejaVu", 30)
    c.drawCentredString(cx + s / 3 * 0.5, cy - s / 3 * 0.65, "★")
    c.setFillColor(CREAM)
    c.setFont("Raleway", 10.5)
    c.drawCentredString(W / 2, H * 0.205, "Solve one puzzle a day from December 1 to 24.")
    c.drawCentredString(W / 2, H * 0.205 - 15, "Each answer reveals one true clue. Find the killer on Christmas Eve.")
    c.setFillColor(HexColor("#000000"))
    c.rect(0, 0, W, 1.0 * inch, fill=1, stroke=0)
    if os.path.exists(LOGO):
        c.drawImage(LOGO, W / 2 - 1.1 * inch, 0.18 * inch, 2.2 * inch, 0.64 * inch,
                    preserveAspectRatio=True, mask="auto")
    c.showPage()

    # How to play
    page_header(c, W, H, "How to Play", "read this first")
    y = H - 1.6 * inch
    steps = [
        ("The case", "Professor Ambrose Vale has been murdered at the Midwinter Gala. Thirty-six "
                     "guests are snowed in at Ashcombe Hall. One of them is the killer."),
        ("Each day", "Open the page for today's date. Read the journal entry, then solve the logic "
                     "puzzle. Every puzzle has exactly one solution, so no guessing is needed."),
        ("The starred cell", "When the puzzle is solved, look at the number in the starred cell. That "
                      "number tells you which of the day's statements is TRUE. The others are rumours."),
        ("Eliminate", "Use the true statement to cross suspects off the Suspect Tracker. Statements are "
                      "always about the culprit, using the facts listed on the Cast pages."),
        ("Self-check", "If a 'true' statement would eliminate every remaining suspect, your puzzle "
                       "answer is wrong. Recheck the grid."),
        ("Christmas Eve", "After Day 24 exactly one suspect remains. Write the name down, then open the "
                          "sealed Final Reveal. Full puzzle solutions are at the back."),
    ]
    for head, body in steps:
        c.setFillColor(WINE)
        c.setFont("Cinzel", 13)
        c.drawString(M, y, head)
        y = para(c, body, M + 1.85 * inch, y, W - 2 * M - 1.85 * inch, size=11) - 12
    y -= 6
    c.setFillColor(SOFT)
    c.setFont("RalewayIt", 9.5)
    for line in wrap("Puzzle types: Sudoku, Futoshiki and Skyscrapers, growing from gentle 4×4 grids "
                     "to tricky 6×6 and 5×5 grids by the final week. Rules are printed on every page. "
                     "Play alone, as a couple or as a family. Print double-sided or one day per sheet.",
                     "RalewayIt", 9.5, W - 2 * M):
        c.drawString(M, y, line)
        y -= 14
    footer(c, W)
    c.showPage()

    # Cast pages (18 per page)
    for part in range(2):
        page_header(c, W, H, "The Cast", f"suspects {part * 18 + 1}–{part * 18 + 18}")
        cols, rows = 3, 6
        gw, gh = (W - 2 * M) / cols, (H - 1.6 * inch - 0.8 * inch) / rows
        for k, s in enumerate(cast[part * 18:(part + 1) * 18]):
            col, row = k % cols, k // cols
            x, ytop = M + col * gw, H - 1.35 * inch - row * gh
            c.setStrokeColor(GOLD)
            c.setLineWidth(0.7)
            c.roundRect(x + 3, ytop - gh + 6, gw - 6, gh - 8, 5, fill=0)
            c.setFillColor(WINE)
            c.circle(x + 18, ytop - 17, 9, fill=1, stroke=0)
            c.setFillColor(CREAM)
            c.setFont("DejaVuB", 8.5)
            c.drawCentredString(x + 18, ytop - 20, str(s["id"]))
            c.setFillColor(INK)
            c.setFont("Cinzel", 10)
            c.drawString(x + 32, ytop - 21, s["name"])
            c.setFont("Raleway", 8.6)
            facts = [f"Field: {ATTRS['dept'][s['dept']]}", f"Midnight: {ATTRS['loc'][s['loc']]}",
                     f"Carrying: {ATTRS['acc'][s['acc']]}", f"Drinking: {ATTRS['drink'][s['drink']]}",
                     f"Arrived: {ATTRS['arr'][s['arr']]}"]
            for i, f in enumerate(facts):
                c.drawString(x + 14, ytop - 36 - i * 11.2, f)
        footer(c, W)
        c.showPage()

    # Suspect tracker
    page_header(c, W, H, "Suspect Tracker", "cross off each suspect the day they are eliminated")
    cols = 3
    rows = 12
    gw = (W - 2 * M) / cols
    rh = (H - 1.6 * inch - 1.0 * inch) / rows
    for k, s in enumerate(cast):
        col, row = k // rows, k % rows
        x, y = M + col * gw, H - 1.45 * inch - row * rh
        c.setStrokeColor(SOFT)
        c.setLineWidth(0.6)
        c.rect(x + 2, y - 13, 11, 11, fill=0)
        c.setFillColor(INK)
        c.setFont("Raleway", 9.2)
        c.drawString(x + 19, y - 11, f"{s['id']:>2}. {s['name']}")
        c.setStrokeColor(SHADE)
        c.line(x + 19, y - 17, x + gw - 10, y - 17)
        c.setFillColor(SOFT)
        c.setFont("Raleway", 6.5)
        c.drawRightString(x + gw - 10, y - 11, "day ___")
    footer(c, W)
    c.showPage()

    # Days
    for d in days:
        p = d["puzzle"]
        page_header(c, W, H, f"December {d['day']}", f"day {d['day']} of 24")
        y = H - 1.45 * inch
        y = para(c, d["story"], M, y, W - 2 * M, font="RalewayIt", size=10.5, color=SOFT) - 10
        c.setFillColor(WINE)
        c.setFont("Cinzel", 11)
        c.drawString(M, y, f"Today's puzzle: {p['kind'].capitalize()} {p['n']}×{p['n']}")
        y = para(c, KIND_RULES[p["kind"]], M, y - 15, W - 2 * M, size=9.5) - 6
        gsize = min(3.9 * inch, W - 2 * M - 1.2 * inch)
        gtop = y - (0.45 * inch if p["kind"] == "skyscrapers" else 0.12 * inch)
        draw_grid(c, p, W / 2 - gsize / 2, gtop, gsize, star=d["star"])
        y = gtop - gsize - (0.6 * inch if p["kind"] == "skyscrapers" else 0.35 * inch)
        c.setFillColor(INK)
        c.setFont("Cinzel", 11)
        c.drawString(M, y, "The starred number tells you which statement is true:")
        y -= 17
        for i, o in enumerate(d["options"], start=1):
            c.setFillColor(GOLD)
            c.circle(M + 8, y + 3.5, 7.5, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.setFont("DejaVuB", 8.5)
            c.drawCentredString(M + 8, y + 0.6, str(i))
            y = para(c, o, M + 22, y, W - 2 * M - 22, size=10.5) - 5
        nb = y - 0.8 * inch
        if nb > 0.25 * inch:
            c.setStrokeColor(SHADE)
            c.setLineWidth(0.8)
            c.roundRect(M, 0.75 * inch, W - 2 * M, y - 0.75 * inch - 8, 6, fill=0)
            c.setFillColor(SOFT)
            c.setFont("Raleway", 8)
            c.drawString(M + 8, y - 22, "NOTES  ·  suspects eliminated today:")
        footer(c, W, f"·  Day {d['day']}")
        c.showPage()

    # Final reveal (sealed)
    page_header(c, W, H, "Final Reveal", "do not read before solving Day 24", band=NAVY)
    y = H * 0.55
    c.setFillColor(SOFT)
    c.setFont("RalewayIt", 11)
    c.drawCentredString(W / 2, H * 0.72, "Fold this page in half along the dotted line and seal it until Christmas Eve.")
    c.setDash(4, 4)
    c.setStrokeColor(SOFT)
    c.line(M, H * 0.62, W - M, H * 0.62)
    c.setDash()
    s = culprit
    reveal = (f"The killer is suspect {s['id']}, {s['name']}, a specialist in "
              f"{ATTRS['dept'][s['dept']]}. Arriving at {ATTRS['arr'][s['arr']]} with a "
              f"{ATTRS['acc'][s['acc']].lower()} and a glass of {ATTRS['drink'][s['drink']]}, "
              f"{s['name'].split()[-1]} slipped away to the {ATTRS['loc'][s['loc']]} just before "
              "midnight. Vale had shown them the proof in confidence, and they could not bear to see "
              "him take the credit. The torn page was meant to be published under their own name. "
              "They had not reckoned on a detective who could count.")
    c.setFillColor(WINE)
    c.setFont("Cinzel", 18)
    c.drawCentredString(W / 2, y, "Case closed.")
    para(c, reveal, M + 0.3 * inch, y - 30, W - 2 * M - 0.6 * inch, size=11.5)
    footer(c, W)
    c.showPage()

    # Solutions (6 per page)
    for start in range(0, 24, 6):
        page_header(c, W, H, "Solutions", f"days {start + 1}–{start + 6}")
        for k, d in enumerate(days[start:start + 6]):
            col, row = k % 2, k // 2
            cx = M + (col + 0.5) * (W - 2 * M) / 2
            top = H - 1.75 * inch - row * 2.85 * inch
            gs = 1.75 * inch
            c.setFillColor(WINE)
            c.setFont("Cinzel", 10.5)
            c.drawCentredString(cx, top + 0.05 * inch, f"Day {d['day']}  ·  star = {d['answer']}")
            draw_grid(c, d["puzzle"], cx - gs / 2, top - 0.35 * inch, gs, star=d["star"], show=True)
        footer(c, W)
        c.showPage()

    # About
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Cinzel", 20)
    c.drawCentredString(W / 2, H * 0.62, "Thank you for playing")
    para(c, "Every puzzle in this calendar was generated and verified by computer to have exactly one "
            "solution, and the clue chain was checked so that a single suspect survives Day 24. "
            "If you enjoyed the case, a review on Etsy helps a small studio more than you know.",
         M + 0.4 * inch, H * 0.55, W - 2 * M - 0.8 * inch, size=11, color=CREAM)
    c.setFillColor(GOLD)
    c.setFont("Raleway", 8.5)
    c.drawCentredString(W / 2, H * 0.2, COPYRIGHT)
    c.showPage()
    c.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    register_fonts()
    cast, culprit, days = plan(a.seed)
    for label, size in (("Letter", LETTER), ("A4", A4)):
        path = os.path.join(OUT, f"Midwinter_Theorem_Mystery_Advent_{label}.pdf")
        render(cast, culprit, days, size, path)
        print("wrote", path)
    meta = {"seed": a.seed, "culprit": culprit,
            "days": [{"day": d["day"], "kind": d["puzzle"]["kind"], "n": d["puzzle"]["n"],
                      "answer": d["answer"], "true": d["options"][d["answer"] - 1]} for d in days]}
    with open(os.path.join(OUT, "solution_key.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("culprit:", culprit["name"])


if __name__ == "__main__":
    sys.exit(main())
