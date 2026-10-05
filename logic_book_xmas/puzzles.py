"""
Puzzle generators + verifiers for the Christmas Logic Puzzle Book.
Every puzzle is generated deterministically (fixed seeds) and verified to have
exactly one solution (sudoku, futoshiki, logic grids) or to be fully solvable by
line logic (nonograms). Results are cached in out/puzzles.json.
"""
import json, os, random, itertools, string

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)


# ============================================================ SUDOKU
def _sud_cands(g, i):
    r, c = divmod(i, 9); used = set(g[r * 9:(r + 1) * 9]) | set(g[c::9])
    br, bc = r // 3 * 3, c // 3 * 3
    for rr in range(br, br + 3):
        used |= set(g[rr * 9 + bc: rr * 9 + bc + 3])
    return [v for v in range(1, 10) if v not in used]


def sud_count(g, limit=2):
    g = list(g); n = 0
    def rec():
        nonlocal n
        best, bc = None, None
        for i in range(81):
            if g[i] == 0:
                cs = _sud_cands(g, i)
                if not cs:
                    return
                if best is None or len(cs) < len(bc):
                    best, bc = i, cs
                    if len(cs) == 1:
                        break
        if best is None:
            n += 1; return
        for v in bc:
            g[best] = v; rec()
            if n >= limit:
                break
        g[best] = 0
    rec(); return n


def sud_full(rnd):
    g = [0] * 81
    def rec(i):
        if i == 81:
            return True
        cs = _sud_cands(g, i); rnd.shuffle(cs)
        for v in cs:
            g[i] = v
            if rec(i + 1):
                return True
        g[i] = 0; return False
    rec(0); return g


def sud_singles(g):
    """Solve with naked + hidden singles only. Returns True if that finishes it."""
    g = list(g)
    units = [[r * 9 + c for c in range(9)] for r in range(9)] + [[r * 9 + c for r in range(9)] for c in range(9)] + \
            [[(br + r) * 9 + bc + c for r in range(3) for c in range(3)] for br in (0, 3, 6) for bc in (0, 3, 6)]
    while True:
        prog = False
        cand = {i: _sud_cands(g, i) for i in range(81) if g[i] == 0}
        if not cand:
            return True
        for i, cs in cand.items():
            if len(cs) == 1:
                g[i] = cs[0]; prog = True
        if not prog:
            for u in units:
                for v in range(1, 10):
                    spots = [i for i in u if g[i] == 0 and v in cand.get(i, [])]
                    if len(spots) == 1 and v not in [g[i] for i in u]:
                        g[spots[0]] = v; prog = True
        if not prog:
            return False


def make_sudoku(seed, level):
    rnd = random.Random(seed)
    while True:
        sol = sud_full(rnd); g = list(sol)
        pairs = list(range(41)); rnd.shuffle(pairs)  # symmetric removal
        target = {"easy": 38, "medium": 31, "hard": 0}[level]
        for i in pairs:
            j = 80 - i; keep = (g[i], g[j])
            g[i] = g[j] = 0
            if sud_count(g) != 1 or (level != "hard" and not sud_singles(g)):
                g[i], g[j] = keep
            if sum(1 for v in g if v) <= target:
                break
        givens = sum(1 for v in g if v)
        if level == "hard" and sud_singles(g):
            seed += 1000; rnd = random.Random(seed); continue  # hard must need more than singles
        if level == "medium" and givens > 33:
            seed += 1000; rnd = random.Random(seed); continue
        return {"grid": g, "sol": sol, "givens": givens, "level": level}


# ============================================================ FUTOSHIKI (5x5)
N5 = 5


def latin(rnd, n):
    base = [[(r + c) % n + 1 for c in range(n)] for r in range(n)]
    rows = list(range(n)); cols = list(range(n)); syms = list(range(1, n + 1))
    rnd.shuffle(rows); rnd.shuffle(cols); rnd.shuffle(syms)
    return [[syms[base[rows[r]][cols[c]] - 1] for c in range(n)] for r in range(n)]


def futo_count(n, givens, ineq, limit=2):
    g = [[givens.get((r, c), 0) for c in range(n)] for r in range(n)]
    cnt = 0
    def ok(r, c, v):
        if any(g[r][k] == v for k in range(n)) or any(g[k][c] == v for k in range(n)):
            return False
        for (a, b) in ineq:  # a > b
            for (p, q) in ((a, b),):
                if p == (r, c) and g[q[0]][q[1]] and not v > g[q[0]][q[1]]:
                    return False
                if q == (r, c) and g[p[0]][p[1]] and not g[p[0]][p[1]] > v:
                    return False
        return True
    cells = [(r, c) for r in range(n) for c in range(n) if not g[r][c]]
    def rec(k):
        nonlocal cnt
        if k == len(cells):
            cnt += 1; return
        r, c = cells[k]
        for v in range(1, n + 1):
            if ok(r, c, v):
                g[r][c] = v; rec(k + 1); g[r][c] = 0
                if cnt >= limit:
                    return
    rec(0); return cnt


def make_futoshiki(seed, n=5, max_givens=3):
    rnd = random.Random(seed)
    sol = latin(rnd, n)
    adj = [((r, c), (r, c + 1)) for r in range(n) for c in range(n - 1)] + \
          [((r, c), (r + 1, c)) for r in range(n - 1) for c in range(n)]
    rnd.shuffle(adj)
    ineq = []; givens = {}
    cells = [(r, c) for r in range(n) for c in range(n)]; rnd.shuffle(cells)
    gi = 0
    for a, b in adj:
        x, y = (a, b) if sol[a[0]][a[1]] > sol[b[0]][b[1]] else (b, a)
        ineq.append((x, y))
        if len(ineq) % 4 == 0 and gi < max_givens:
            cl = cells[gi]; givens[cl] = sol[cl[0]][cl[1]]; gi += 1
        if len(ineq) >= 6 and futo_count(n, givens, ineq) == 1:
            break
    # prune redundant clues
    for clue in list(ineq):
        t = [q for q in ineq if q != clue]
        if futo_count(n, givens, t) == 1:
            ineq = t
    for cl in list(givens):
        t = {k: v for k, v in givens.items() if k != cl}
        if futo_count(n, t, ineq) == 1:
            givens = t
    assert futo_count(n, givens, ineq) == 1
    return {"n": n, "sol": sol, "givens": [[r, c, v] for (r, c), v in givens.items()],
            "ineq": [[list(a), list(b)] for a, b in ineq]}


# ============================================================ NONOGRAMS
NONO_ART = {
    "Christmas Tree": """
.......#.......
......###......
.......#.......
......###......
.....#####.....
....###.###....
.....#####.....
....#######....
...####.####...
....#######....
..###########..
.#####.#.#####.
#######.#######
......###......
.....#####.....""",
    "Bell": """
.......#.......
......###......
....#######....
...###...###...
...##.....##...
..###.....###..
..##.......##..
..##.......##..
.###.......###.
.##.........##.
###############
###############
......###......
.......#.......
...............""",
    "Snowman": """
.....#####.....
.....#####.....
...#########...
.....#####.....
....##.#.##....
....#######....
....##...##....
.....#####.....
...#########...
..#####.#####..
.######.######.
.#############.
.######.######.
..###########..
....#######....""",
    "Gift Box": """
....##...##....
...#..#.#..#...
....##.#.##....
.......#.......
.#############.
.#############.
.......#.......
.#############.
.#.....#.....#.
.#.....#.....#.
.#.....#.....#.
.#.....#.....#.
.#.....#.....#.
.#############.
...............""",
    "Candy Cane": """
.....#####.....
....##...##....
...##.....##...
...#.......#...
...#.......#...
...........#...
..........##...
..........#....
..........##...
...........#...
..........##...
..........#....
..........##...
...........#...
..........###..""",
    "Stocking": """
...#########...
...#########...
....#######....
....#######....
....#######....
....#######....
....#######....
....#######....
...########....
..########.....
.#########.....
##########.....
#########......
.#######.......
..####.........""",
    "Star": """
.......#.......
......###......
......###......
.....#####.....
###############
.#############.
..###########..
...#########...
....#######....
....#######....
...#########...
...####.####...
..####...####..
..###.....###..
.##.........##.""",
    "Gingerbread Man": """
......###......
.....#####.....
.....#.#.#.....
.....#####.....
......###......
..###########..
.######.######.
.##.#######.##.
....###.###....
....#######....
....###.###....
....###.###....
...###...###...
...###...###...
..####...####..""",
    "Ornament": """
......###......
.......#.......
.....#####.....
...#########...
..###########..
.#############.
.#...........#.
.#.#.#.#.#.#.#.
.#...........#.
.#############.
..###########..
...#########...
.....#####.....
...............
...............""",
    "Mitten": """
.....######....
....########...
....########...
.##.########...
####.#######...
####.#######...
.###########...
..##########...
...#########...
....########...
.....#######...
....#########..
....#########..
....#########..
...............""",
}


def clues(line):
    out, k = [], 0
    for v in line:
        if v:
            k += 1
        elif k:
            out.append(k); k = 0
    if k:
        out.append(k)
    return out or [0]


def line_arrangements(cl, n):
    if cl == [0]:
        return [[0] * n]
    res = []
    def rec(i, pos, cur):
        if i == len(cl):
            res.append(cur + [0] * (n - len(cur))); return
        rest = sum(cl[i + 1:]) + len(cl) - i - 1
        for s in range(pos, n - rest - cl[i] + 1):
            seg = cur + [0] * (s - len(cur)) + [1] * cl[i]
            if i < len(cl) - 1:
                seg = seg + [0]
            rec(i + 1, len(seg), seg)
    rec(0, 0, []); return res


def nono_line_solve(rows, cols):
    R, C = len(rows), len(cols)
    g = [[-1] * C for _ in range(R)]
    ra = [line_arrangements(c, C) for c in rows]; ca = [line_arrangements(c, R) for c in cols]
    changed = True
    while changed:
        changed = False
        for r in range(R):
            ra[r] = [a for a in ra[r] if all(g[r][k] in (-1, a[k]) for k in range(C))]
            for k in range(C):
                vals = {a[k] for a in ra[r]}
                if len(vals) == 1 and g[r][k] == -1:
                    g[r][k] = vals.pop(); changed = True
        for c in range(C):
            ca[c] = [a for a in ca[c] if all(g[k][c] in (-1, a[k]) for k in range(R))]
            for k in range(R):
                vals = {a[k] for a in ca[c]}
                if len(vals) == 1 and g[k][c] == -1:
                    g[k][c] = vals.pop(); changed = True
    return g


def make_nonogram(name):
    rows = [l for l in NONO_ART[name].strip("\n").split("\n")]
    grid = [[1 if ch == "#" else 0 for ch in l] for l in rows]
    assert all(len(r) == len(grid[0]) for r in grid), name
    rc = [clues(r) for r in grid]; cc = [clues([grid[r][c] for r in range(len(grid))]) for c in range(len(grid[0]))]
    solved = nono_line_solve(rc, cc)
    ok = all(v != -1 for row in solved for v in row) and solved == grid
    return {"name": name, "grid": grid, "rows": rc, "cols": cc, "line_solvable": ok}


# ============================================================ CRYPTOGRAMS (public-domain quotes)
QUOTES = [
    ("I will honour Christmas in my heart, and try to keep it all the year.", "Charles Dickens, A Christmas Carol"),
    ("At Christmas play and make good cheer, for Christmas comes but once a year.", "Thomas Tusser"),
    ("Heap on more wood! The wind is chill; but let it whistle as it will, we'll keep our Christmas merry still.", "Sir Walter Scott"),
    ("I am as light as a feather, I am as happy as an angel, I am as merry as a school-boy.", "Charles Dickens, A Christmas Carol"),
    ("Christmas won't be Christmas without any presents.", "Louisa May Alcott, Little Women"),
    ("He knew how to keep Christmas well, if any man alive possessed the knowledge.", "Charles Dickens, A Christmas Carol"),
    ("Twas the night before Christmas, when all through the house not a creature was stirring, not even a mouse.", "Clement Clarke Moore"),
    ("I heard the bells on Christmas Day their old, familiar carols play.", "Henry Wadsworth Longfellow"),
    ("At Christmas I no more desire a rose than wish a snow in May's new-fangled mirth.", "William Shakespeare"),
    ("Reflect upon your present blessings, of which every man has many; not on your past misfortunes.", "Charles Dickens"),
    ("Christmas is the season for kindling the fire of hospitality in the hall, the genial flame of charity in the heart.", "Washington Irving"),
    ("There is nothing in the world so irresistibly contagious as laughter and good humour.", "Charles Dickens, A Christmas Carol"),
    ("Mathematics is the queen of the sciences and number theory is the queen of mathematics.", "Carl Friedrich Gauss"),
    ("The essence of mathematics lies in its freedom.", "Georg Cantor"),
    ("Pure mathematics is, in its way, the poetry of logical ideas.", "Albert Einstein"),
]


def make_cryptogram(i):
    text, who = QUOTES[i]
    rnd = random.Random(500 + i)
    L = list(string.ascii_uppercase)
    while True:
        p = L[:]; rnd.shuffle(p)
        if all(a != b for a, b in zip(L, p)):
            break
    key = dict(zip(L, p))
    enc = "".join(key.get(ch, ch) for ch in text.upper())
    letters = [ch for ch in dict.fromkeys(text.upper()) if ch.isalpha()]
    hint_plain = max(letters, key=lambda ch: text.upper().count(ch)) if i < 5 else rnd.choice(letters)
    return {"plain": text.upper(), "who": who, "enc": enc, "hint": [key[hint_plain], hint_plain]}


# ============================================================ LOGIC GRIDS (verified by brute force)
LOGIC = [
    {"title": "The Elves' Workshop",
     "intro": "Four elves each built a different toy, in a different color, on Christmas Eve.",
     "people": ["Holly", "Jingle", "Pip", "Sprout"],
     "cats": {"Toy": ["Robot", "Train", "Kite", "Drum"], "Color": ["Red", "Green", "Blue", "Gold"]},
     "clues": [
         ("The robot is not red, and it was not built by Holly.", lambda a: a["Toy"]["Robot"] != a["Color"]["Red"] and a["Toy"]["Robot"] != "Holly"),
         ("Jingle built the drum.", lambda a: a["Toy"]["Drum"] == "Jingle"),
         ("The kite is gold.", lambda a: a["Toy"]["Kite"] == a["Color"]["Gold"]),
         ("Pip's toy is green.", lambda a: a["Color"]["Green"] == "Pip"),
         ("Sprout did not build the train, and Sprout's toy is not gold.", lambda a: a["Toy"]["Train"] != "Sprout" and a["Color"]["Gold"] != "Sprout"),
         ("The drum is not blue.", lambda a: a["Toy"]["Drum"] != a["Color"]["Blue"]),
     ]},
    {"title": "Cookie Exchange",
     "intro": "Four neighbors brought a different cookie to the exchange, each baked for a different number of minutes.",
     "people": ["Ava", "Ben", "Cleo", "Dev"],
     "cats": {"Cookie": ["Gingerbread", "Shortbread", "Snickerdoodle", "Macaron"], "Minutes": ["8", "10", "12", "15"]},
     "clues": [
         ("The macarons baked for less time than Ben's cookies.", lambda a: int(a["inv"]["Minutes"][a["Cookie"]["Macaron"]]) < int(a["inv"]["Minutes"]["Ben"])),
         ("Cleo's cookies baked for exactly 12 minutes.", lambda a: a["Minutes"]["12"] == "Cleo"),
         ("The gingerbread baked longest.", lambda a: a["Cookie"]["Gingerbread"] == a["Minutes"]["15"]),
         ("Ava brought shortbread.", lambda a: a["Cookie"]["Shortbread"] == "Ava"),
         ("Dev's cookies baked for less time than Ava's.", lambda a: int(a["inv"]["Minutes"]["Dev"]) < int(a["inv"]["Minutes"]["Ava"])),
         ("Cleo did not bring snickerdoodles.", lambda a: a["Cookie"]["Snickerdoodle"] != "Cleo"),
     ]},
    {"title": "Reindeer Practice Flights",
     "intro": "Four reindeer practiced on four nights, each flying to a different city.",
     "people": ["Comet", "Cupid", "Dasher", "Vixen"],
     "cats": {"Night": ["Monday", "Tuesday", "Wednesday", "Thursday"], "City": ["Oslo", "Quebec", "Tokyo", "Lima"]},
     "clues": [
         ("Dasher flew the night after the reindeer who went to Tokyo.", lambda a: a["dn"](a["inv"]["Night"]["Dasher"]) == a["dn"](a["inv"]["Night"][a["City"]["Tokyo"]]) + 1),
         ("The Oslo flight was on Thursday.", lambda a: a["City"]["Oslo"] == a["Night"]["Thursday"]),
         ("Vixen flew to Lima.", lambda a: a["City"]["Lima"] == "Vixen"),
         ("Comet flew later in the week than Dasher.", lambda a: a["dn"](a["inv"]["Night"]["Comet"]) > a["dn"](a["inv"]["Night"]["Dasher"])),
         ("Cupid did not fly on Monday.", lambda a: a["Night"]["Monday"] != "Cupid"),
         ("The Quebec flight was later in the week than Vixen's.", lambda a: a["dn"](a["inv"]["Night"][a["City"]["Quebec"]]) > a["dn"](a["inv"]["Night"]["Vixen"])),
     ]},
    {"title": "Secret Santa",
     "intro": "Five coworkers drew names for Secret Santa. Each gave a different gift with a different budget.",
     "people": ["Grace", "Hugo", "Iris", "Jon", "Kai"],
     "cats": {"Gift": ["Book", "Mug", "Scarf", "Puzzle", "Candle"], "Budget": ["$10", "$15", "$20", "$25", "$30"]},
     "clues": [
         ("The scarf cost $15 more than the mug.", lambda a: a["bud"](a["Gift"]["Scarf"]) == a["bud"](a["Gift"]["Mug"]) + 15),
         ("Iris spent the most.", lambda a: a["Budget"]["$30"] == "Iris"),
         ("Hugo gave the puzzle, and spent less than Jon.", lambda a: a["Gift"]["Puzzle"] == "Hugo" and a["bud"]("Hugo") < a["bud"]("Jon")),
         ("The candle cost $15.", lambda a: a["Gift"]["Candle"] == a["Budget"]["$15"]),
         ("Grace spent $5 more than Kai.", lambda a: a["bud"]("Grace") == a["bud"]("Kai") + 5),
         ("Jon did not give the book.", lambda a: a["Gift"]["Book"] != "Jon"),
         ("The book was not the cheapest gift.", lambda a: a["Gift"]["Book"] != a["Budget"]["$10"]),
     ]},
    {"title": "Christmas Lights Contest",
     "intro": "Five houses on Holly Lane entered the lights contest. Each used a different number of bulbs and a different theme.",
     "people": ["No. 1", "No. 2", "No. 3", "No. 4", "No. 5"],
     "cats": {"Theme": ["Snowflakes", "Reindeer", "Candy canes", "Stars", "Angels"], "Bulbs": ["500", "800", "1000", "1200", "2000"]},
     "clues": [
         ("House No. 1 used 800 bulbs.", lambda a: a["Bulbs"]["800"] == "No. 1"),
         ("House No. 3 has the stars theme.", lambda a: a["Theme"]["Stars"] == "No. 3"),
         ("The snowflakes house used the most bulbs.", lambda a: a["Theme"]["Snowflakes"] == a["Bulbs"]["2000"]),
         ("The candy canes house used the fewest bulbs.", lambda a: a["Theme"]["Candy canes"] == a["Bulbs"]["500"]),
         ("The angels house is directly next to the house with 2000 bulbs.", lambda a: abs(a["hn"](a["Theme"]["Angels"]) - a["hn"](a["Bulbs"]["2000"])) == 1),
         ("The reindeer house has a lower number than the candy canes house.", lambda a: a["hn"](a["Theme"]["Reindeer"]) < a["hn"](a["Theme"]["Candy canes"])),
         ("House No. 5 used 1000 bulbs.", lambda a: a["Bulbs"]["1000"] == "No. 5"),
     ]},
    {"title": "The Holiday Train",
     "intro": "Five travelers on the holiday train sat in carriages 1 to 5, each heading to a different town with a different snack.",
     "people": ["Lena", "Max", "Nora", "Omar", "Pia"],
     "cats": {"Carriage": ["1", "2", "3", "4", "5"], "Snack": ["Cocoa", "Pretzel", "Orange", "Fudge", "Chestnuts"]},
     "clues": [
         ("Nora sat in a higher-numbered carriage than both Max and Pia.", lambda a: a["cn"]("Nora") > a["cn"]("Max") and a["cn"]("Nora") > a["cn"]("Pia")),
         ("The traveler with cocoa sat in carriage 1.", lambda a: a["Snack"]["Cocoa"] == a["Carriage"]["1"]),
         ("Omar sat in carriage 5 and did not have fudge.", lambda a: a["Carriage"]["5"] == "Omar" and a["Snack"]["Fudge"] != "Omar"),
         ("Max sat directly in front of Pia (Max's carriage number is one less).", lambda a: a["cn"]("Pia") == a["cn"]("Max") + 1),
         ("The chestnuts were in carriage 3.", lambda a: a["Snack"]["Chestnuts"] == a["Carriage"]["3"]),
         ("Lena had the pretzel.", lambda a: a["Snack"]["Pretzel"] == "Lena"),
         ("The orange was not in carriage 4.", lambda a: a["Snack"]["Orange"] != a["Carriage"]["4"]),
     ]},
]
DAYN = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4}


def logic_solutions(p):
    people = p["people"]; cats = list(p["cats"])
    sols = []
    for perms in itertools.product(*[itertools.permutations(people) for _ in cats]):
        a = {"people": people, "inv": {}}
        for cat, perm in zip(cats, perms):
            a[cat] = dict(zip(p["cats"][cat], perm))
            a["inv"][cat] = {v: k for k, v in a[cat].items()}
        a["dn"] = lambda d: DAYN[d]
        a["bud"] = lambda who: int(a["inv"]["Budget"][who][1:]) if "Budget" in a["inv"] and who in a["inv"]["Budget"] else int(a["inv"]["Budget"][who][1:])
        a["hn"] = lambda h: int(h.split()[-1])
        a["cn"] = lambda who: int(a["inv"]["Carriage"][who])
        try:
            if all(f(a) for _, f in p["clues"]):
                sols.append({cat: a["inv"][cat] for cat in cats})
        except KeyError:
            pass
    return sols


# ============================================================ MAZES (Christmas-shaped)
def _in_poly(x, y, poly):
    ins = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def _star(cx, cy, R, r, k=5):
    import math
    return [(cx + (R if i % 2 == 0 else r) * math.cos(-math.pi / 2 + i * math.pi / k),
             cy + (R if i % 2 == 0 else r) * math.sin(-math.pi / 2 + i * math.pi / k)) for i in range(2 * k)]


MAZE_SHAPES = {
    "Christmas Tree": lambda x, y: _in_poly(x, y, [(0.5, 0.0), (0.98, 0.86), (0.6, 0.86), (0.6, 1.0), (0.4, 1.0), (0.4, 0.86), (0.02, 0.86)]),
    "Ornament": lambda x, y: (x - 0.5) ** 2 + (y - 0.55) ** 2 < 0.45 ** 2 or (0.42 < x < 0.58 and 0.0 <= y < 0.15),
    "Star": lambda x, y: _in_poly(x, y, _star(0.5, 0.53, 0.5, 0.24)),
    "Snowman": lambda x, y: (x - 0.5) ** 2 + (y - 0.27) ** 2 < 0.22 ** 2 or (x - 0.5) ** 2 + (y - 0.7) ** 2 < 0.3 ** 2,
    "Gift Box": lambda x, y: (0.04 < x < 0.96 and 0.22 < y < 1.0) or (x - 0.33) ** 2 + (y - 0.13) ** 2 < 0.13 ** 2 or (x - 0.67) ** 2 + (y - 0.13) ** 2 < 0.13 ** 2,
    "Bell": lambda x, y: _in_poly(x, y, [(0.4, 0.0), (0.6, 0.0), (0.6, 0.08), (0.76, 0.18), (0.82, 0.5), (0.98, 0.86), (0.98, 0.92), (0.6, 0.92), (0.6, 1.0), (0.4, 1.0), (0.4, 0.92), (0.02, 0.92), (0.02, 0.86), (0.18, 0.5), (0.24, 0.18), (0.4, 0.08)]),
    "Stocking": lambda x, y: _in_poly(x, y, [(0.3, 0.0), (0.75, 0.0), (0.75, 0.62), (0.5, 0.95), (0.1, 1.0), (0.02, 0.85), (0.3, 0.6)]),
    "Gingerbread House": lambda x, y: _in_poly(x, y, [(0.5, 0.0), (0.98, 0.42), (0.88, 0.42), (0.88, 1.0), (0.12, 1.0), (0.12, 0.42), (0.02, 0.42)]),
}


def make_maze(name, n, seed):
    rnd = random.Random(seed)
    f = MAZE_SHAPES[name]
    cells = {(r, c) for r in range(n) for c in range(n) if f((c + 0.5) / n, (r + 0.5) / n)}
    # keep the largest 4-connected component
    comp, seen = [], set()
    for s in cells:
        if s in seen:
            continue
        st, cc = [s], []
        seen.add(s)
        while st:
            u = st.pop(); cc.append(u)
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (u[0] + dr, u[1] + dc)
                if v in cells and v not in seen:
                    seen.add(v); st.append(v)
        comp.append(cc)
    cells = set(max(comp, key=len))
    start = min(cells, key=lambda t: (t[0], abs(t[1] - n / 2)))
    end = max(cells, key=lambda t: (t[0], -abs(t[1] - n / 2)))
    # randomized DFS spanning tree
    links = set(); vis = {start}; st = [start]
    while st:
        u = st[-1]
        nb = [(u[0] + dr, u[1] + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        nb = [v for v in nb if v in cells and v not in vis]
        if not nb:
            st.pop(); continue
        v = rnd.choice(nb); vis.add(v); links.add(frozenset((u, v))); st.append(v)
    # solution path (BFS on tree)
    prev = {start: None}; q = [start]
    for u in q:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = (u[0] + dr, u[1] + dc)
            if v not in prev and frozenset((u, v)) in links:
                prev[v] = u; q.append(v)
    path = []; u = end
    while u:
        path.append(u); u = prev[u]
    return {"name": name, "n": n, "cells": sorted(cells), "links": [sorted(l) for l in links],
            "start": start, "end": end, "path": path[::-1]}


# ============================================================ BRAIN TEASERS
TEASERS = [
    ("The Twelve Days", "In the song, on day 1 you receive 1 gift, on day 2 you receive 1 + 2 gifts, on day 3 you receive 1 + 2 + 3 gifts, and so on. How many gifts arrive over all twelve days?",
     "364. Day k brings 1 + 2 + ... + k gifts; adding these for k = 1 to 12 gives 364."),
    ("Party Handshakes", "Ten guests arrive at a Christmas party and every guest shakes hands with every other guest exactly once. How many handshakes are there?",
     "45. Each pair shakes once: 10 x 9 / 2 = 45."),
    ("The Candle and the Holder", "A candle and its holder cost $1.10 together. The candle costs $1.00 more than the holder. How much is the holder?",
     "5 cents. Holder = x, candle = x + 1.00, so 2x + 1.00 = 1.10 and x = 0.05."),
    ("Socks in the Dark", "A drawer holds 10 red and 10 green socks. In the dark, how many socks must you take to be sure of a matching pair?",
     "3. With only two colors, any 3 socks must include two of the same color."),
    ("Snow on the Lawn", "Each day the snow-covered part of a lawn doubles. The lawn is fully covered on day 30. On which day was it half covered?",
     "Day 29. It doubles once more on day 30."),
    ("Busy Elves", "5 elves make 5 toys in 5 minutes. How long do 100 elves take to make 100 toys?",
     "5 minutes. Each elf makes one toy in 5 minutes."),
    ("Brothers and Sisters", "In a family, each boy has as many brothers as sisters, but each girl has twice as many brothers as sisters. How many children are there?",
     "7 (4 boys and 3 girls). Boys: b - 1 = g. Girls: b = 2(g - 1). So b = 4 and g = 3."),
    ("Reindeer on the Stairs", "A reindeer climbs a staircase of 10 steps, taking 1 or 2 steps at a time. In how many different ways can it reach the top?",
     "89. The counts follow the Fibonacci pattern 1, 2, 3, 5, 8, 13, 21, 34, 55, 89."),
    ("The Painted Gift Cube", "A 3 x 3 x 3 cube is painted on the outside and then cut into 27 small cubes. How many small cubes have paint on exactly two faces?",
     "12, one in the middle of each of the cube's 12 edges."),
    ("The Light Switch Elves", "100 lights are off. Elf 1 switches every light, elf 2 switches every 2nd light, elf 3 every 3rd, and so on up to elf 100. How many lights are on at the end?",
     "10. A light ends on only if it has an odd number of divisors, which happens exactly for the perfect squares 1, 4, 9, ..., 100."),
    ("The Lighter Coin", "Among 9 gold coins, one fake is slightly lighter. Using a balance scale, what is the smallest number of weighings that always finds it?",
     "2. Weigh 3 against 3: the light group (or the 3 left out) holds the fake. Then weigh 1 against 1 from that group."),
    ("Sleigh Average", "Santa flies 120 km to a town at 60 km/h and returns along the same route at 40 km/h. What is his average speed for the round trip?",
     "48 km/h. 240 km in 2 h + 3 h = 5 h."),
    ("The Advent Sum", "Behind door n of an advent calendar are n chocolates. How many chocolates are behind all 24 doors?",
     "300. 1 + 2 + ... + 24 = 24 x 25 / 2 = 300."),
    ("Three-Way Secret Santa", "Three friends draw names at random from a hat for Secret Santa. What is the chance that nobody draws their own name?",
     "1/3. Of the 6 possible draws, only 2 give everyone someone else."),
    ("Christmas Next Year", "Christmas Day 2026 falls on a Friday. On which day of the week does Christmas Day 2027 fall?",
     "Saturday. 2027 is not a leap year, so 365 days = 52 weeks + 1 day."),
    ("The Hourglasses", "You have a 4-minute and a 7-minute hourglass. How can you time exactly 9 minutes for the pudding?",
     "Start both. At 4 min flip the 4. At 7 min flip the 7. At 8 min the 4 runs out; the 7 has run 1 minute, so flip it again and it runs out at 9 min."),
    ("The Fifth Ornament", "Four ornaments have an average weight of 50 g. Adding a fifth ornament raises the average to 52 g. How heavy is the fifth one?",
     "60 g. 5 x 52 - 4 x 50 = 260 - 200 = 60."),
    ("Squares on the Board", "How many squares of any size are there on an 8 x 8 chessboard?",
     "204. 64 + 49 + 36 + 25 + 16 + 9 + 4 + 1 = 204."),
    ("Three Cuts", "How can you cut a round Christmas cake into 8 equal pieces with only 3 straight cuts?",
     "Two perpendicular cuts from above give 4 pieces, then one horizontal cut through the middle layer doubles them to 8."),
    ("Clock Hands", "Between midnight and noon (not counting either), how many times do the hour and minute hands of a clock overlap?",
     "10. The hands meet every 12/11 hours (about 1:05, 2:11, 3:16, ...). The 11th meeting after midnight is noon itself, so 10 fall strictly between."),
]


# ============================================================ BUILD ALL
def build_all():
    data = {}
    data["sudoku"] = []
    for i, lvl in enumerate(["easy"] * 10 + ["medium"] * 10 + ["hard"] * 10):
        s = make_sudoku(1000 + i, lvl)
        assert sud_count(s["grid"]) == 1
        data["sudoku"].append(s)
        print("sudoku", i + 1, lvl, s["givens"], flush=True)
    data["futoshiki"] = [make_futoshiki(2000 + i) for i in range(12)]
    print("futoshiki", [len(f["ineq"]) for f in data["futoshiki"]], flush=True)
    data["nonogram"] = [make_nonogram(k) for k in NONO_ART]
    print("nonogram", [(n["name"], n["line_solvable"]) for n in data["nonogram"]], flush=True)
    data["crypto"] = [make_cryptogram(i) for i in range(len(QUOTES))]
    data["logic"] = []
    for p in LOGIC:
        sols = logic_solutions(p)
        print("logic", p["title"], len(sols), flush=True)
        data["logic"].append({"title": p["title"], "intro": p["intro"], "people": p["people"],
                              "cats": p["cats"], "clues": [c for c, _ in p["clues"]], "sol": sols[0] if len(sols) == 1 else None,
                              "nsol": len(sols)})
    data["maze"] = [make_maze(k, n, 3000 + i) for i, (k, n) in enumerate(zip(MAZE_SHAPES, (24, 26, 28, 28, 30, 30, 32, 34)))]
    data["teaser"] = TEASERS
    with open(os.path.join(OUT, "puzzles.json"), "w") as f:
        json.dump(data, f)
    return data


if __name__ == "__main__":
    build_all()
