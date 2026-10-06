"""The 24 sticker designs (physics, chemistry, math). Each function draws on a Canvas (1000 units)."""
import math
import numpy as np
import cairo
from lib import Canvas, INK, NAVY, CREAM, PAPER, GOLD, CORAL, TEAL, SKY, LAV, PINK, MINT, TAN, WHITE, hexc

DESIGNS = {}


def design(group, title):
    def deco(fn):
        DESIGNS[fn.__name__] = (group, title, fn)
        return fn
    return deco


W8 = 10   # standard ink line width


# =============================================================== PHYSICS
@design("physics", "Atom")
def atom(k):
    c = k.c
    k.circle(500, 500, 400); k.fs(NAVY, INK, W8)
    k.circle(500, 500, 372); k.stroke(hexc("3b4a7a"), 4)
    for i in range(3):
        k.ellipse(500, 500, 330, 112, i * math.pi / 3); k.stroke(GOLD, 16)
    for i, t in enumerate((0.6, 2.4, 4.1)):
        rot = i * math.pi / 3; x, y = 330 * math.cos(t), 112 * math.sin(t)
        ex = 500 + x * math.cos(rot) - y * math.sin(rot); ey = 500 + x * math.sin(rot) + y * math.cos(rot)
        k.circle(ex, ey, 30); k.fs(SKY, INK, 7)
    for dx, dy, col in ((-24, -16, CORAL), (22, -20, CREAM), (-20, 22, CREAM), (24, 18, CORAL), (0, 0, CORAL)):
        k.circle(500 + dx, 500 + dy, 34); k.fs(col, INK, 6)


@design("physics", "E = mc²")
def emc2(k):
    k.rrect(90, 250, 820, 500, 70); k.fs(NAVY, INK, W8)
    k.rrect(122, 282, 756, 436, 46); k.stroke(hexc("3b4a7a"), 5)
    k.text(r"$E=mc^2$", "serif", 165, 500, 555, CREAM)
    for x, y, s in ((800, 330, 26), (845, 390, 14), (175, 650, 18)):
        sparkle(k, x, y, s, GOLD)
    k.c.new_path(); k.c.move_to(260, 640); k.c.line_to(740, 640); k.stroke(GOLD, 8)


def sparkle(k, x, y, s, col):
    k.c.new_path()
    for i in range(8):
        r = s if i % 2 == 0 else s * 0.28
        a = i * math.pi / 4 - math.pi / 2
        (k.c.move_to if i == 0 else k.c.line_to)(x + r * math.cos(a), y + r * math.sin(a))
    k.c.close_path(); k.fill(col)


@design("physics", "Schrödinger's Cat")
def schrodinger(k):
    c = k.c
    # box (isometric-ish)
    k.poly([(170, 470), (500, 560), (830, 470), (830, 830), (500, 920), (170, 830)]); k.fs(TAN, INK, W8)
    k.poly([(500, 560), (500, 920)], close=False); k.stroke(INK, 7)
    k.poly([(500, 560), (830, 470), (830, 830), (500, 920)]); k.fill(hexc("c68f58"))
    k.poly([(170, 470), (500, 560), (830, 470), (830, 830), (500, 920), (170, 830)]); k.stroke(INK, W8)
    k.poly([(500, 560), (500, 920)], close=False); k.stroke(INK, 7)
    # open flaps
    k.poly([(170, 470), (500, 560), (430, 640), (95, 545)]); k.fs(hexc("e7b884"), INK, 8)
    k.poly([(830, 470), (500, 560), (575, 640), (905, 545)]); k.fs(hexc("e7b884"), INK, 8)
    # cat peeking
    k.c.new_path(); k.c.move_to(330, 520); k.c.curve_to(330, 380, 380, 330, 500, 330)
    k.c.curve_to(620, 330, 670, 380, 670, 520); k.c.close_path(); k.fs(INK, INK, 6)
    k.poly([(345, 430), (360, 260), (450, 345)]); k.fs(INK, INK, 6)
    k.poly([(655, 430), (640, 260), (550, 345)]); k.fs(INK, INK, 6)
    k.poly([(370, 405), (378, 310), (430, 360)]); k.fill(PINK)
    k.poly([(630, 405), (622, 310), (570, 360)]); k.fill(PINK)
    for x in (445, 555):
        k.ellipse(x, 440, 30, 36); k.fill(GOLD)
        k.ellipse(x, 440, 9, 30); k.fill(INK)
    k.poly([(488, 482), (512, 482), (500, 496)]); k.fill(PINK)
    for s in (-1, 1):
        for dy in (-8, 10):
            k.c.new_path(); k.c.move_to(500 + s * 40, 492 + dy * 0.4); k.c.line_to(500 + s * 150, 480 + dy * 2.2); k.stroke(CREAM, 4)
    # psi label on the box
    k.text(r"$|\psi\rangle$", "serif", 120, 330, 790, INK)
    k.text("?", "serif_b", 150, 680, 800, hexc("8a5a2e"))


@design("physics", "Black Hole")
def black_hole(k):
    c = k.c
    k.circle(500, 500, 400); k.fs(hexc("0f1530"), INK, W8)
    for i in range(70):
        rng = np.random.default_rng(i); x, y = rng.uniform(150, 850, 2)
        if math.hypot(x - 500, y - 500) < 380:
            k.circle(x, y, rng.uniform(1.5, 4.5)); k.fill(hexc("fbf5e9", rng.uniform(0.4, 0.9)))
    # back half of the disk
    c.save(); c.translate(500, 500); c.scale(1, 0.32)
    g = cairo.RadialGradient(0, 0, 150, 0, 0, 360)
    for t, col in ((0, hexc("fff4d6")), (0.25, hexc("f6c85f")), (0.65, hexc("e2694f")), (1, hexc("e2694f", 0))):
        g.add_color_stop_rgba(t, *col)
    c.new_path(); c.arc(0, 0, 360, math.pi, 2 * math.pi); c.arc_negative(0, 0, 150, 2 * math.pi, math.pi); c.close_path()
    c.set_source(g); c.fill(); c.restore()
    # photon ring + shadow
    k.circle(500, 500, 168); c.set_source(k.rad(500, 500, 140, 200, [(0, hexc("fff4d6")), (0.4, hexc("f6c85f", 0.9)), (1, hexc("e2694f", 0))])); c.fill()
    k.circle(500, 500, 142); k.fill(hexc("05070f"))
    # lensed top arc
    c.save(); c.translate(500, 470); c.scale(1, 0.85)
    c.new_path(); c.arc(0, 0, 205, math.pi * 1.08, math.pi * 1.92); c.set_line_width(26)
    c.set_source_rgba(*hexc("f6c85f", 0.85)); c.stroke(); c.restore()
    # front half of the disk
    c.save(); c.translate(500, 500); c.scale(1, 0.32)
    g = cairo.RadialGradient(0, 0, 150, 0, 0, 360)
    for t, col in ((0, hexc("fffaf0")), (0.2, hexc("f8d77a")), (0.6, hexc("e8804f")), (1, hexc("e2694f", 0))):
        g.add_color_stop_rgba(t, *col)
    c.new_path(); c.arc(0, 0, 360, 0, math.pi); c.arc_negative(0, 0, 150, math.pi, 0); c.close_path()
    c.set_source(g); c.fill(); c.restore()
    k.circle(500, 500, 400); k.stroke(INK, W8)


@design("physics", "Ringed Planet")
def planet(k):
    c = k.c
    def ring(front):
        c.save(); c.translate(500, 520); c.rotate(-0.33); c.scale(1, 0.26)
        c.new_path()
        if front:
            c.arc(0, 0, 430, 0, math.pi); c.arc_negative(0, 0, 300, math.pi, 0)
        else:
            c.arc(0, 0, 430, math.pi, 2 * math.pi); c.arc_negative(0, 0, 300, 2 * math.pi, math.pi)
        c.close_path(); c.restore()
        k.fs(GOLD, INK, 9)
        c.save(); c.translate(500, 520); c.rotate(-0.33); c.scale(1, 0.26)
        c.new_path(); (c.arc(0, 0, 365, 0, math.pi) if front else c.arc(0, 0, 365, math.pi, 2 * math.pi)); c.restore()
        k.stroke(hexc("c48f2c"), 6)
    ring(False)
    k.circle(500, 520, 250); k.c.set_source(k.lin(300, 300, 700, 760, [(0, hexc("f2a07f")), (1, hexc("c4553f"))])); k.c.fill_preserve(); k.stroke(INK, W8)
    c.save(); k.circle(500, 520, 245); c.clip()
    for y, col, h in ((370, hexc("f8c6a6"), 40), (450, hexc("d9694f"), 30), (560, hexc("f8c6a6"), 26), (640, hexc("b04a37"), 44)):
        c.save(); c.translate(500, y); c.rotate(-0.33); k.rrect(-400, -h / 2, 800, h, h / 2); c.restore(); k.fill(col)
    c.restore()
    ring(True)
    for x, y, s in ((160, 190, 30), (830, 230, 22), (850, 820, 26), (190, 800, 16)):
        sparkle(k, x, y, s, GOLD)


@design("physics", "Newton's Cradle")
def cradle(k):
    c = k.c
    k.rrect(40, 90, 920, 780, 90); k.fs(hexc("dfeaf4"), INK, W8)
    k.rrect(30, 820, 940, 80, 34); k.fs(NAVY, INK, W8)
    for x in (100, 900):
        k.rrect(x - 16, 150, 32, 680, 16); k.fs(hexc("c9d2e3"), INK, 8)
    k.rrect(84, 140, 832, 34, 17); k.fs(hexc("c9d2e3"), INK, 8)
    L = 420; xs = [320, 410, 500, 590, 680]; R = 44
    for i, x in enumerate(xs):
        a = -0.45 if i == 0 else 0.0
        bx, by = x + L * math.sin(a), 174 + L * math.cos(a)
        c.new_path(); c.move_to(x, 174); c.line_to(bx, by - R); k.stroke(INK, 5)
        k.circle(bx, by, R)
        c.set_source(k.rad(bx - 15, by - 15, 3, R * 1.2, [(0, hexc("ffffff")), (0.45, hexc("c9d2e3")), (1, hexc("6f7c99"))]))
        c.fill_preserve(); k.stroke(INK, 8)
    for r in (330, 370):
        c.new_path(); c.arc(320, 174, r, math.pi / 2 + 0.12, math.pi / 2 + 0.36); k.stroke(GOLD, 9)


@design("physics", "Good Vibrations")
def vibes(k):
    k.rrect(80, 270, 840, 460, 230); k.fs(TEAL, INK, W8)
    k.rrect(112, 302, 776, 396, 198); k.stroke(hexc("6cc3b7"), 5)
    k.c.new_path()
    for i in range(301):
        x = 170 + i * 2.2; t = (x - 170) / 660
        y = 470 - 120 * math.sin(t * 4 * math.pi) * math.sin(t * math.pi)
        (k.c.move_to if i == 0 else k.c.line_to)(x, y)
    k.stroke(INK, 26, preserve=True); k.stroke(CREAM, 12)
    k.text("GOOD VIBRATIONS", "sans_x", 52, 500, 650, INK, tracking=6)


@design("physics", "Prism")
def prism(k):
    c = k.c
    cols = ["e2694f", "f0a04b", "e8c547", "6dbb75", "4f9fd6", "7d6bd0"]
    for i, h in enumerate(cols):
        a0 = -0.18 + i * 0.075; a1 = a0 + 0.075
        k.poly([(600, 470), (960, 470 + 360 * math.tan(a0) + 140), (960, 470 + 360 * math.tan(a1) + 140)])
        k.fill(hexc(h))
    k.poly([(40, 600), (420, 470), (440, 500), (60, 630)]); k.fill(CREAM)
    k.poly([(40, 600), (420, 470), (440, 500), (60, 630)]); k.stroke(INK, 6)
    k.poly([(500, 170), (770, 760), (230, 760)]); k.c.set_source(k.lin(230, 170, 770, 760, [(0, hexc("e9f2fb", 0.95)), (1, hexc("a9c7e2", 0.95))])); k.c.fill_preserve(); k.stroke(INK, W8)
    k.poly([(500, 230), (712, 720)], close=False); k.stroke(WHITE, 10)


# =============================================================== CHEMISTRY
@design("chemistry", "Erlenmeyer Flask")
def flask(k):
    c = k.c
    def body():
        c.new_path(); c.move_to(420, 170); c.line_to(420, 420); c.line_to(210, 800)
        c.curve_to(195, 830, 210, 860, 250, 860); c.line_to(750, 860); c.curve_to(790, 860, 805, 830, 790, 800)
        c.line_to(580, 420); c.line_to(580, 170); c.close_path()
    body(); k.fill(hexc("eef5fb"))
    c.save(); body(); c.clip()
    c.new_path(); c.move_to(150, 600)
    for i in range(9):
        c.curve_to(150 + i * 90 + 30, 580, 150 + i * 90 + 60, 620, 150 + (i + 1) * 90, 600)
    c.line_to(900, 900); c.line_to(100, 900); c.close_path(); c.set_source(k.lin(0, 600, 0, 860, [(0, hexc("3cc0ae")), (1, TEAL)])); c.fill()
    for x, y, r in ((420, 760, 26), (560, 700, 18), (480, 650, 12), (620, 800, 14), (340, 810, 10)):
        k.circle(x, y, r); k.fs(hexc("bfeee6"), None)
    c.restore()
    body(); k.stroke(INK, W8)
    k.rrect(395, 140, 210, 46, 18); k.fs(PAPER, INK, 8)
    c.new_path(); c.move_to(445, 470); c.line_to(300, 740); k.stroke(WHITE, 14)
    for x, y, r in ((470, 110, 22), (540, 60, 30), (600, 120, 16)):
        k.circle(x, y, r); k.fs(MINT, INK, 6)
    for y in (500, 560):
        c.new_path(); c.move_to(560, y); c.line_to(600, y); k.stroke(INK, 5)


def molecule(k, smiles, cx, cy, scale, col_bond=INK, labels=True, w=10, het_cols=None, label_size=0.55):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles(smiles); Chem.Kekulize(m, clearAromaticFlags=True); AllChem.Compute2DCoords(m)
    conf = m.GetConformer(); P = np.array([[conf.GetAtomPosition(i).x, -conf.GetAtomPosition(i).y] for i in range(m.GetNumAtoms())])
    P = (P - P.mean(0)) * scale + np.array([cx, cy])
    het_cols = het_cols or {"N": hexc("3a6fc4"), "O": CORAL}
    lab = {i: a.GetSymbol() for i, a in enumerate(m.GetAtoms()) if a.GetSymbol() != "C"}
    ring_info = m.GetRingInfo()
    for b in m.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx(); p, q = P[i].copy(), P[j].copy()
        d = q - p; L = np.linalg.norm(d); u = d / L
        if i in lab: p = p + u * scale * 0.32
        if j in lab: q = q - u * scale * 0.32
        k.c.new_path(); k.c.move_to(*p); k.c.line_to(*q); k.stroke(col_bond, w)
        if b.GetBondTypeAsDouble() == 2:
            n = np.array([-u[1], u[0]])
            # put the second line inside the ring when the bond is in a ring
            rings = [r for r in ring_info.AtomRings() if i in r and j in r]
            if rings:
                ctr = P[list(rings[0])].mean(0)
                if np.dot(ctr - (P[i] + P[j]) / 2, n) < 0: n = -n
                off = n * scale * 0.2; p2, q2 = p + off + u * scale * 0.14, q + off - u * scale * 0.14
            else:
                off = n * scale * 0.17; p2, q2 = p + off, q + off
            k.c.new_path(); k.c.move_to(*p2); k.c.line_to(*q2); k.stroke(col_bond, w)
    if labels:
        for i, s in lab.items():
            hs = m.GetAtomWithIdx(i).GetTotalNumHs()
            txt = s + ("H" if hs == 1 else ("H$_2$" if hs == 2 else ""))
            txt = txt if "$" not in txt else s + r"H$_{2}$"
            k.text(s if not hs else (s + "H" + ("₂" if hs == 2 else "")), "sans_x", scale * label_size, P[i][0], P[i][1] + scale * label_size * 0.36,
                   het_cols.get(s, INK))
    return P


@design("chemistry", "Caffeine")
def caffeine(k):
    c = k.c
    k.rrect(160, 60, 680, 430, 150); k.fs(CREAM, INK, W8)
    molecule(k, "Cn1cnc2c1c(=O)n(C)c(=O)n2C", 500, 270, 62, w=9, label_size=0.62)
    c.new_path(); c.move_to(230, 520); c.line_to(770, 520); c.line_to(720, 850); c.curve_to(710, 900, 680, 910, 640, 910)
    c.line_to(360, 910); c.curve_to(320, 910, 290, 900, 280, 850); c.close_path(); k.fs(CORAL, INK, W8)
    c.new_path(); c.arc(790, 650, 75, -1.6, 1.6); k.stroke(INK, 34); c.new_path(); c.arc(790, 650, 75, -1.6, 1.6); k.stroke(CORAL, 16)
    k.ellipse(500, 520, 270, 40); k.fs(hexc("6b3f2a"), INK, 8)
    k.rrect(320, 760, 360, 70, 35); k.fill(CREAM)
    k.text("CAFFEINE", "sans_x", 44, 500, 811, INK, tracking=5)


@design("chemistry", "Dopamine")
def dopamine(k):
    k.rrect(70, 200, 860, 600, 300); k.fs(PINK, INK, W8)
    molecule(k, "NCCc1ccc(O)c(O)c1", 500, 450, 68, w=10, het_cols={"N": hexc("3a4fa8"), "O": hexc("b2353a")})
    k.text("dopamine", "serif_i", 80, 500, 735, INK)


@design("chemistry", "Serotonin")
def serotonin(k):
    k.rrect(70, 200, 860, 600, 300); k.fs(LAV, INK, W8)
    molecule(k, "NCCc1c[nH]c2ccc(O)cc12", 500, 440, 62, w=10, het_cols={"N": hexc("23306b"), "O": hexc("b2353a")})
    k.text("serotonin", "serif_i", 80, 500, 735, INK)


@design("chemistry", "Ge Ni U S")
def genius(k):
    tiles = [("Ge", "32", "Germanium", TEAL), ("Ni", "28", "Nickel", GOLD), ("U", "92", "Uranium", CORAL), ("S", "16", "Sulfur", SKY)]
    for i, (sym, z, name, col) in enumerate(tiles):
        x = 70 + i * 220; y = 330 + (i % 2) * 40
        k.rrect(x, y, 200, 240, 22); k.fs(col, INK, W8)
        k.text(z, "mono_b", 34, x + 22, y + 52, INK, anchor="l")
        k.text(sym, "serif_b", 120, x + 100, y + 172, INK)
        k.text(name, "sans_b", 24, x + 100, y + 215, INK)


@design("chemistry", "DNA")
def dna(k):
    c = k.c
    n = 260; ys = np.linspace(110, 890, n)
    xa = 500 + 210 * np.sin(ys / 780 * 2.6 * math.pi); xb = 500 - 210 * np.sin(ys / 780 * 2.6 * math.pi)
    depth = np.cos(ys / 780 * 2.6 * math.pi)
    cols = [CORAL, GOLD, TEAL, SKY]
    for i in range(10, n - 10, 20):
        k.c.new_path(); k.c.move_to(xa[i], ys[i]); k.c.line_to(xb[i], ys[i]); k.stroke(INK, 22)
        mid = (xa[i] + xb[i]) / 2
        k.c.new_path(); k.c.move_to(xa[i], ys[i]); k.c.line_to(mid, ys[i]); k.stroke(cols[(i // 20) % 4], 12)
        k.c.new_path(); k.c.move_to(mid, ys[i]); k.c.line_to(xb[i], ys[i]); k.stroke(cols[(i // 20 + 2) % 4], 12)
    for xs, sgn in ((xa, 1), (xb, -1)):
        for i in range(n - 1):
            front = sgn * depth[i] > 0
            if not front:
                k.c.new_path(); k.c.move_to(xs[i], ys[i]); k.c.line_to(xs[i + 1], ys[i + 1]); k.stroke(INK, 44)
                k.c.new_path(); k.c.move_to(xs[i], ys[i]); k.c.line_to(xs[i + 1], ys[i + 1]); k.stroke(hexc("3d4c7f"), 26)
    for xs, sgn in ((xa, 1), (xb, -1)):
        for i in range(n - 1):
            if sgn * depth[i] > 0:
                k.c.new_path(); k.c.move_to(xs[i], ys[i]); k.c.line_to(xs[i + 1], ys[i + 1]); k.stroke(INK, 46)
    for xs, sgn in ((xa, 1), (xb, -1)):
        for i in range(n - 1):
            if sgn * depth[i] > 0:
                k.c.new_path(); k.c.move_to(xs[i], ys[i]); k.c.line_to(xs[i + 1], ys[i + 1]); k.stroke(NAVY, 28)


@design("chemistry", "Test Tubes")
def test_tubes(k):
    c = k.c
    cols = [CORAL, GOLD, TEAL]; tops = [380, 300, 420]
    for i, (col, lv) in enumerate(zip(cols, tops)):
        x = 270 + i * 230
        c.save(); c.translate(x, 0)
        def tube():
            c.new_path(); c.move_to(-70, 150); c.line_to(-70, 760); c.arc_negative(0, 760, 70, math.pi, 0); c.line_to(70, 150); c.close_path()
        tube(); k.fill(hexc("eef5fb"))
        c.save(); tube(); c.clip(); k.c.rectangle(-80, lv, 160, 700); k.fill(col)
        k.ellipse(0, lv, 70, 14); k.fill(hexc("ffffff", 0.45)); c.restore()
        tube(); k.stroke(INK, W8)
        k.rrect(-92, 130, 184, 40, 16); k.fs(PAPER, INK, 8)
        c.new_path(); c.move_to(-38, 210); c.line_to(-38, 700); k.stroke(WHITE, 12)
        c.restore()
    k.rrect(120, 600, 760, 70, 20); k.fs(NAVY, INK, W8)
    for i in range(3):
        k.c.new_path(); k.c.move_to(150, 900); k.c.line_to(150, 670); k.stroke(INK, 18)
        k.c.new_path(); k.c.move_to(850, 900); k.c.line_to(850, 670); k.stroke(INK, 18)


@design("chemistry", "Stay Positive")
def stay_positive(k):
    c = k.c
    for i in range(3):
        k.ellipse(500, 470, 380, 130, i * math.pi / 3 + 0.3); k.stroke(hexc("e8b448", 0.9), 10)
    k.circle(500, 470, 190); k.c.set_source(k.rad(450, 410, 10, 200, [(0, hexc("ff9c80")), (1, CORAL)])); k.c.fill_preserve(); k.stroke(INK, W8)
    k.c.new_path(); k.c.move_to(500, 395); k.c.line_to(500, 545); k.c.move_to(425, 470); k.c.line_to(575, 470); k.stroke(CREAM, 34)
    k.rrect(190, 750, 620, 110, 55); k.fs(NAVY, INK, W8)
    k.text("STAY POSITIVE", "sans_x", 54, 500, 825, CREAM, tracking=6)


# =============================================================== MATH
@design("math", "Pi")
def pi_badge(k):
    k.circle(500, 500, 410); k.fs(GOLD, INK, W8)
    k.circle(500, 500, 300); k.fs(NAVY, INK, 8)
    k.text(r"$\pi$", "serif", 420, 500, 590, CREAM)
    digits = ("3.14159265358979323846264338327950288419716939937510"
              "58209749445923078164062862089986280348253421170679")
    size, tr, r = 34, 1.5, 354
    step = k.text_width("0", "mono_b", size) + tr
    n = int(2 * math.pi * r * 0.985 / step)
    k.arc_text(digits[:n], "mono_b", size, 500, 500, r, -math.pi / 2, INK, tracking=tr)


@design("math", "Golden Spiral")
def golden(k):
    c = k.c
    phi = (1 + 5 ** 0.5) / 2
    W_ = 840; H_ = W_ / phi; x, y, w, h = 500 - W_ / 2, 500 - H_ / 2, W_, H_
    cols = [TEAL, CORAL, GOLD, SKY, MINT, LAV, PINK, CREAM, GOLD, CORAL]
    squares, arcs = [], []
    for i in range(10):
        m = i % 4
        if m == 0:
            s_ = h; squares.append((x, y, s_)); arcs.append((x + s_, y + s_, s_, math.pi, 1.5 * math.pi)); x += s_; w -= s_
        elif m == 1:
            s_ = w; squares.append((x, y, s_)); arcs.append((x, y + s_, s_, 1.5 * math.pi, 2 * math.pi)); y += s_; h -= s_
        elif m == 2:
            s_ = h; squares.append((x + w - s_, y, s_)); arcs.append((x + w - s_, y, s_, 0, 0.5 * math.pi)); w -= s_
        else:
            s_ = w; squares.append((x, y + h - s_, s_)); arcs.append((x + s_, y + h - s_, s_, 0.5 * math.pi, math.pi)); h -= s_
    for i, (sx, sy, s_) in enumerate(squares):
        c.rectangle(sx, sy, s_, s_); k.fill(cols[i])
    for i, (sx, sy, s_) in enumerate(squares):
        c.rectangle(sx, sy, s_, s_); k.stroke(INK, max(2.5, 8 - i))
    c.new_path()
    for cx, cy, r, a0, a1 in arcs:
        c.arc(cx, cy, r, a0, a1)
    k.stroke(CREAM, 22, preserve=True); k.stroke(INK, 10)
    c.rectangle(500 - W_ / 2, 500 - H_ / 2, W_, H_); k.stroke(INK, W8)


@design("math", "Mandelbrot")
def mandelbrot(k):
    c = k.c
    N = 900; xs = np.linspace(-2.25, 0.85, N); ys = np.linspace(-1.55, 1.55, N)
    C = xs[None, :] + 1j * ys[:, None]; Z = np.zeros_like(C); it = np.zeros(C.shape)
    alive = np.ones(C.shape, bool)
    for i in range(120):
        Z[alive] = Z[alive] ** 2 + C[alive]
        esc = alive & (np.abs(Z) > 4)
        it[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc]) + 1e-9) + 1e-9); alive &= ~esc
    t = np.where(alive, 0, np.clip(it / 40, 0, 1) ** 0.6)
    stops = np.array([[0x1d, 0x27, 0x42], [0x2a, 0x9d, 0x8f], [0xe8, 0xb4, 0x48], [0xfb, 0xf5, 0xe9]], float)
    idx = t * (len(stops) - 1); lo = np.floor(idx).astype(int).clip(0, len(stops) - 2); f = (idx - lo)[..., None]
    rgb = stops[lo] * (1 - f) + stops[lo + 1] * f
    rgb[alive] = [0x14, 0x1b, 0x31]
    img = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], np.full(rgb.shape[:2], 255)]).astype(np.uint8)
    surf = cairo.ImageSurface.create_for_data(bytearray(img.tobytes()), cairo.FORMAT_ARGB32, N, N, N * 4)
    c.save(); k.circle(500, 500, 400); c.clip()
    c.translate(100, 100); c.scale(800 / N, 800 / N); c.set_source_surface(surf, 0, 0); c.paint(); c.restore()
    k.circle(500, 500, 400); k.stroke(INK, W8)
    k.circle(500, 500, 385); k.stroke(hexc("e8b448", 0.8), 5)


@design("math", "Fibonacci Sunflower")
def sunflower(k):
    c = k.c
    for i in range(21):
        a = i * 2 * math.pi / 21
        c.save(); c.translate(500 + 300 * math.cos(a), 500 + 300 * math.sin(a)); c.rotate(a)
        k.ellipse(0, 0, 150, 58); c.restore(); k.fs(GOLD, INK, 8)
    for i in range(21):
        a = (i + 0.5) * 2 * math.pi / 21
        c.save(); c.translate(500 + 260 * math.cos(a), 500 + 260 * math.sin(a)); c.rotate(a)
        k.ellipse(0, 0, 120, 44); c.restore(); k.fs(hexc("f2c45c"), INK, 7)
    k.circle(500, 500, 250); k.fs(hexc("5b3a26"), INK, W8)
    ga = math.pi * (3 - math.sqrt(5)); N = 340
    for n in range(N, 0, -1):
        r = 232 * math.sqrt(n / N); a = n * ga
        t = n / N
        col = tuple(np.array(hexc("f6d27a")[:3]) * (1 - t) + np.array(hexc("c9793f")[:3]) * t) + (1,)
        k.circle(500 + r * math.cos(a), 500 + r * math.sin(a), 5 + 7 * t); k.fill(col)


@design("math", "Euler's Identity")
def euler(k):
    k.rrect(80, 300, 840, 400, 200); k.fs(CREAM, INK, W8)
    k.rrect(110, 330, 780, 340, 170); k.stroke(GOLD, 6)
    k.text(r"$e^{i\pi}+1=0$", "serif", 160, 500, 560, INK)


@design("math", "Sierpinski")
def sierpinski(k):
    def tri(a, b, c_, d):
        if d == 0:
            k.poly([a, b, c_]); k.fs(None, None); return [(a, b, c_)]
        ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); bc = ((b[0] + c_[0]) / 2, (b[1] + c_[1]) / 2); ca = ((c_[0] + a[0]) / 2, (c_[1] + a[1]) / 2)
        return tri(a, ab, ca, d - 1) + tri(ab, b, bc, d - 1) + tri(ca, bc, c_, d - 1)
    A, B, C = (500, 110), (930, 855), (70, 855)
    k.poly([A, B, C]); k.fs(NAVY, INK, W8 + 4)
    tris = tri(A, B, C, 5)
    for t in tris:
        cy = (t[0][1] + t[1][1] + t[2][1]) / 3; f = (cy - 110) / 745
        col = tuple(np.array(GOLD[:3]) * (1 - f) + np.array(CORAL[:3]) * f) + (1,)
        k.poly(list(t)); k.fill(col)
    k.poly([A, B, C]); k.stroke(INK, W8 + 4)


@design("math", "Infinity")
def infinity(k):
    c = k.c
    pts = [(500 + 380 * math.cos(t) / (1 + math.sin(t) ** 2), 500 + 380 * math.sin(t) * math.cos(t) / (1 + math.sin(t) ** 2))
           for t in np.linspace(0, 2 * math.pi, 400)]
    for w, col in ((120, INK), (100, None)):
        k.c.new_path(); k.c.move_to(*pts[0])
        for p in pts[1:]:
            k.c.line_to(*p)
        k.c.close_path()
        if col:
            k.stroke(col, w)
        else:
            c.set_source(k.lin(120, 500, 880, 500, [(0, TEAL), (0.5, GOLD), (1, CORAL)])); c.set_line_width(w); c.stroke()
    k.c.new_path(); k.c.move_to(*pts[0])
    for p in pts[1:]:
        k.c.line_to(*p)
    k.stroke(hexc("ffffff", 0.35), 18)


@design("math", "Pythagoras")
def pythagoras(k):
    A = np.array([0.0, 0.0]); B = np.array([4.0, 0.0]); C = np.array([0.0, -3.0])   # right angle at A (y up = -)
    G = (A + B + C) / 3
    def sq(p, q):
        d = q - p; n = np.array([d[1], -d[0]])
        if np.dot(n, (p + q) / 2 - G) < 0:
            n = -n
        return [p, q, q + n, p + n]
    S = {"a": sq(C, A), "b": sq(A, B), "c": sq(B, C)}
    pts = np.vstack([np.array(v) for v in S.values()])
    lo, hi = pts.min(0), pts.max(0); sc = 820 / max(hi - lo); off = 500 - (lo + hi) / 2 * sc
    T = lambda p: tuple(p * sc + off)
    cols = {"a": GOLD, "b": SKY, "c": CORAL}
    for key in ("a", "b", "c"):
        k.poly([T(p) for p in S[key]]); k.fs(cols[key], INK, 9)
    k.poly([T(A), T(B), T(C)]); k.fs(CREAM, INK, 9)
    q = 0.42; k.poly([T(A + [q, 0]), T(A + [q, -q]), T(A + [0, -q])], close=False); k.stroke(INK, 6)
    for key, size in (("a", 78), ("b", 86), ("c", 100)):
        ctr = np.mean(S[key], axis=0); x, y = T(ctr)
        k.text({"a": r"$a^2$", "b": r"$b^2$", "c": r"$c^2$"}[key], "serif", size, x, y + size * 0.3, INK)
