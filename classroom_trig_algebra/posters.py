"""The ten classroom posters. Each function draws on a P painter in a 750 x 1000 box."""
import math
from kit import P, ACC, INK, SOFT, PAPER, WHITE, GRID, tint, hexc

POSTERS = []


def poster(acc):
    def deco(fn):
        fn.ACC = ACC[acc]; fn.acc_name = acc; POSTERS.append(fn); return fn
    return deco


def n(fn):
    return POSTERS.index(fn) + 1


# =========================================================== 1 UNIT CIRCLE
@poster("blue")
def unit_circle(p):
    a = ACC["blue"]; p.frame("The Unit Circle", r"radius 1  ·  every point is $(\cos\theta,\ \sin\theta)$", a, n(unit_circle))
    cx, cy, R = 375, 535, 232
    p.line(cx - R - 22, cy, cx + R + 22, cy, SOFT, 2); p.line(cx, cy - R - 22, cx, cy + R + 22, SOFT, 2)
    p.circle(cx, cy, R); p.stroke(a, 5)
    angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
    rad = {0: "0", 30: r"\frac{\pi}{6}", 45: r"\frac{\pi}{4}", 60: r"\frac{\pi}{3}", 90: r"\frac{\pi}{2}",
           120: r"\frac{2\pi}{3}", 135: r"\frac{3\pi}{4}", 150: r"\frac{5\pi}{6}", 180: r"\pi", 210: r"\frac{7\pi}{6}",
           225: r"\frac{5\pi}{4}", 240: r"\frac{4\pi}{3}", 270: r"\frac{3\pi}{2}", 300: r"\frac{5\pi}{3}",
           315: r"\frac{7\pi}{4}", 330: r"\frac{11\pi}{6}"}
    val = {0: "1", 30: r"\frac{\sqrt{3}}{2}", 45: r"\frac{\sqrt{2}}{2}", 60: r"\frac{1}{2}", 90: "0"}
    def cs(d):
        q = d % 90; base = d - q
        if q == 0:
            return {0: ("1", "0"), 90: ("0", "1"), 180: ("-1", "0"), 270: ("0", "-1")}[d]
        cosv, sinv = val[q], val[90 - q]
        if base in (90, 270):
            cosv, sinv = sinv, cosv
        sc = -1 if 90 < d < 270 else 1; ss = -1 if d > 180 else 1
        return ("-" if sc < 0 else "") + cosv, ("-" if ss < 0 else "") + sinv
    quad_col = {0: ACC["blue"], 1: ACC["green"], 2: ACC["orange"], 3: ACC["purple"]}
    for d in angles:
        t = math.radians(d); x, y = cx + R * math.cos(t), cy - R * math.sin(t)
        col = quad_col[min(d // 90, 3)] if d % 90 else INK
        if d % 90:
            p.line(cx, cy, x, y, tint(col, 0.45), 1.6)
        p.circle(x, y, 8); p.fs(col, WHITE, 2)
        rr = R * 0.82
        p.text(f"{d}°", "black", 15, cx + rr * math.cos(t), cy - rr * math.sin(t), col, valign="mid", halo=6)
        if d != 0:
            rr2 = R * (0.63 if d % 90 else 0.64)
            off = (0, 0) if d % 90 else ((0, 0) if d in (90, 270) else (0, -18))
            p.text(f"${rad[d]}$", "body", 19, cx + rr2 * math.cos(t) + off[0], cy - rr2 * math.sin(t) + off[1], col, valign="mid", halo=6)
        c_, s_ = cs(d); lab = f"$\\left({c_},\\,{s_}\\right)$"
        ro = R + (62 if d % 90 else 44)
        lx, ly = cx + ro * math.cos(t), cy - ro * math.sin(t)
        if d in (0, 180):
            lx += 26 if d == 0 else -26
        p.text(lab, "body", 18, lx, ly, INK, valign="mid", halo=6)
    for q, (lab, qx, qy) in enumerate((("I", 1, -1), ("II", -1, -1), ("III", -1, 1), ("IV", 1, 1))):
        p.text(lab, "title", 34, cx + qx * 285, cy + qy * 290, tint(quad_col[q], 0.15), valign="mid")
    p.card(70, 860, 610, 76, a, None, 0.9)
    p.text(r"$\tan\theta=\frac{\sin\theta}{\cos\theta}$", "body", 28, 200, 898, INK, valign="mid")
    p.text("ASTC:  All · Sine · Tangent · Cosine", "black", 16, 520, 886, INK, valign="mid")
    p.text("are positive in quadrants I · II · III · IV", "bold", 14, 520, 912, SOFT, valign="mid")


# =========================================================== 2 SOHCAHTOA
@poster("coral")
def sohcahtoa(p):
    a = ACC["coral"]; p.frame("SOH CAH TOA", "the three trig ratios of a right triangle", a, n(sohcahtoa))
    O, A, H = ACC["blue"], ACC["green"], ACC["purple"]
    x0, y0, x1, y1 = 160, 520, 590, 520; top = (590, 250)
    p.c.new_path(); p.poly([(x0, y0), (x1, y1), top]); p.fs(tint(a, 0.92), None)
    p.line(x0, y0, x1, y1, A, 8); p.line(x1, y1, *top, O, 8); p.line(x0, y0, *top, H, 8)
    p.c.new_path(); p.poly([(x1 - 30, y1), (x1 - 30, y1 - 30), (x1, y1 - 30)], close=False); p.stroke(INK, 3)
    p.c.new_path(); p.c.arc(x0, y0, 70, -math.atan2(y0 - top[1], top[0] - x0), 0); p.stroke(a, 4)
    p.text(r"$\theta$", "body", 40, x0 + 100, y0 - 22, a, valign="mid")
    p.text("ADJACENT", "black", 24, (x0 + x1) / 2, y0 + 40, A)
    p.c.save(); p.c.translate(x1 + 34, (y1 + top[1]) / 2); p.c.rotate(-math.pi / 2)
    p.text("OPPOSITE", "black", 24, 0, 0, O, valign="mid"); p.c.restore()
    ang = math.atan2(y0 - top[1], top[0] - x0)
    p.c.save(); p.c.translate((x0 + top[0]) / 2 - 22, (y0 + top[1]) / 2 - 22); p.c.rotate(-ang)
    p.text("HYPOTENUSE", "black", 24, 0, 0, H, valign="mid"); p.c.restore()
    rows = [("SOH", r"$\sin\theta=\frac{\mathrm{opposite}}{\mathrm{hypotenuse}}$", O, H),
            ("CAH", r"$\cos\theta=\frac{\mathrm{adjacent}}{\mathrm{hypotenuse}}$", A, H),
            ("TOA", r"$\tan\theta=\frac{\mathrm{opposite}}{\mathrm{adjacent}}$", O, A)]
    for i, (k, f, c1, c2) in enumerate(rows):
        y = 610 + i * 100
        p.rrect(70, y, 610, 84, 20); p.fs(WHITE, a, 3)
        p.rrect(70, y, 150, 84, 20); p.fill(a)
        p.text(k, "title", 44, 145, y + 42, WHITE, valign="mid")
        p.text(f, "body", 34, 450, y + 42, INK, valign="mid")
    p.text(r"Reciprocals:   $\csc\theta=\frac{1}{\sin\theta}$    $\sec\theta=\frac{1}{\cos\theta}$    $\cot\theta=\frac{1}{\tan\theta}$",
           "bold", 20, 375, 925, SOFT, valign="mid")


# =========================================================== 3 SPECIAL RIGHT TRIANGLES
@poster("green")
def special(p):
    a = ACC["green"]; p.frame("Special Right Triangles", "memorize the side ratios", a, n(special))
    # 45-45-90
    p.card(60, 215, 300, 380, a, "45°- 45°- 90°")
    A_, B_, C_ = (100, 540), (320, 540), (100, 320)
    p.c.new_path(); p.poly([A_, B_, C_]); p.fs(tint(a, 0.6), INK, 4)
    p.c.new_path(); p.poly([(A_[0] + 24, A_[1]), (A_[0] + 24, A_[1] - 24), (A_[0], A_[1] - 24)], close=False); p.stroke(INK, 3)
    p.text("$x$", "body", 34, 210, 580, INK); p.text("$x$", "body", 34, 76, 440, INK, valign="mid")
    p.text(r"$x\sqrt{2}$", "body", 34, 240, 410, INK, valign="mid")
    p.text("45°", "black", 18, 280, 528, INK); p.text("45°", "black", 18, 115, 360, INK)
    # 30-60-90
    p.card(390, 215, 300, 380, a, "30°- 60°- 90°")
    A_, B_, C_ = (430, 540), (650, 540), (430, 413)
    s = 1.0
    A_, B_, C_ = (430, 540), (650, 540), (430, 540 - 220 / math.sqrt(3))
    p.c.new_path(); p.poly([A_, B_, C_]); p.fs(tint(a, 0.6), INK, 4)
    p.c.new_path(); p.poly([(A_[0] + 22, A_[1]), (A_[0] + 22, A_[1] - 22), (A_[0], A_[1] - 22)], close=False); p.stroke(INK, 3)
    p.text(r"$x\sqrt{3}$", "body", 32, 540, 580, INK); p.text("$x$", "body", 34, 408, 480, INK, valign="mid")
    p.text("$2x$", "body", 34, 560, 440, INK, valign="mid")
    p.text("30°", "black", 18, 606, 528, INK); p.text("60°", "black", 18, 448, 450, INK)
    # table of exact values
    p.card(60, 640, 630, 290, a, "EXACT VALUES")
    cols = ["", "30°", "45°", "60°"]; rows = [("sin", [r"\frac{1}{2}", r"\frac{\sqrt{2}}{2}", r"\frac{\sqrt{3}}{2}"]),
                                              ("cos", [r"\frac{\sqrt{3}}{2}", r"\frac{\sqrt{2}}{2}", r"\frac{1}{2}"]),
                                              ("tan", [r"\frac{\sqrt{3}}{3}", "1", r"\sqrt{3}"])]
    xs = [140, 300, 450, 600]
    for x, h in zip(xs, cols):
        p.text(h, "black", 24, x, 690, a, valign="mid")
    for i, (fn, vals) in enumerate(rows):
        y = 760 + i * 62
        p.line(90, y - 31, 660, y - 31, tint(a, 0.6), 2)
        p.text(fn, "black", 26, xs[0], y, INK, valign="mid")
        for x, v in zip(xs[1:], vals):
            p.text(f"${v}$", "body", 30, x, y, INK, valign="mid")


# =========================================================== 4 TRIG IDENTITIES
@poster("purple")
def identities(p):
    a = ACC["purple"]; p.frame("Trig Identities", "the formulas you will use again and again", a, n(identities))
    blocks = [("RECIPROCAL", [r"$\csc\theta=\frac{1}{\sin\theta}$", r"$\sec\theta=\frac{1}{\cos\theta}$", r"$\cot\theta=\frac{1}{\tan\theta}$"]),
              ("QUOTIENT", [r"$\tan\theta=\frac{\sin\theta}{\cos\theta}$", r"$\cot\theta=\frac{\cos\theta}{\sin\theta}$"]),
              ("PYTHAGOREAN", [r"$\sin^2\theta+\cos^2\theta=1$", r"$1+\tan^2\theta=\sec^2\theta$", r"$1+\cot^2\theta=\csc^2\theta$"]),
              ("DOUBLE ANGLE", [r"$\sin 2\theta=2\sin\theta\,\cos\theta$", r"$\cos 2\theta=\cos^2\theta-\sin^2\theta$",
                                r"$\tan 2\theta=\frac{2\tan\theta}{1-\tan^2\theta}$"]),
              ("SUM & DIFFERENCE", [r"$\sin(\alpha\pm\beta)=\sin\alpha\,\cos\beta\pm\cos\alpha\,\sin\beta$",
                                    r"$\cos(\alpha\pm\beta)=\cos\alpha\,\cos\beta\mp\sin\alpha\,\sin\beta$"]),
              ("EVEN / ODD", [r"$\sin(-\theta)=-\sin\theta$", r"$\cos(-\theta)=\cos\theta$", r"$\tan(-\theta)=-\tan\theta$"])]
    pos = [(60, 220, 300, 200), (390, 220, 300, 200), (60, 455, 630, 120), (60, 610, 630, 120), (60, 765, 630, 90), (60, 885, 630, 52)]
    for (lab, fs), (x, y, w, h) in zip(blocks, pos):
        p.card(x, y, w, h, a, lab)
        if w < 400:
            for i, f in enumerate(fs):
                p.fit_text(f, "body", 28, x + w / 2, y + 48 + i * (h - 40) / len(fs) + 6, w - 30, INK, valign="mid")
        elif lab == "EVEN / ODD":
            for i, f in enumerate(fs):
                p.text(f, "body", 22, x + 110 + i * 205, y + 30, INK, valign="mid")
        elif lab == "SUM & DIFFERENCE":
            for i, f in enumerate(fs):
                p.fit_text(f, "body", 24, x + w / 2, y + 32 + i * 32, w - 40, INK, valign="mid")
        else:
            if len(fs) == 3:
                for i, f in enumerate(fs[:2]):
                    p.fit_text(f, "body", 24, x + 165 + i * 310, y + 42, 290, INK, valign="mid")
                p.fit_text(fs[2], "body", 24, x + w / 2, y + 88, 400, INK, valign="mid")


# =========================================================== 5 GRAPHS
@poster("teal")
def graphs(p):
    a = ACC["teal"]; p.frame("Graphs of Trig Functions", "amplitude, period and asymptotes at a glance", a, n(graphs))
    specs = [("SINE", r"$y=\sin x$", math.sin, ACC["blue"], "amplitude 1  ·  period 2π  ·  zeros at kπ"),
             ("COSINE", r"$y=\cos x$", math.cos, ACC["coral"], "amplitude 1  ·  period 2π  ·  y-intercept 1"),
             ("TANGENT", r"$y=\tan x$", math.tan, ACC["purple"], "period π  ·  asymptotes at π/2 + kπ")]
    for k, (lab, formula, f, col, note) in enumerate(specs):
        x0, y0, w, h = 60, 215 + k * 245, 630, 222
        p.card(x0, y0, w, h, a, lab)
        p.c.save(); p.rrect(x0 + 3, y0 + 3, w - 6, h - 6, 16); p.c.clip()
        gx0, gx1, gy = x0 + 40, x0 + w - 40, y0 + 104
        cx = (gx0 + gx1) / 2; sx = (gx1 - gx0) / (4 * math.pi); sy = 38
        for m in range(-4, 5):
            X = cx + m * math.pi / 2 * sx; p.line(X, gy - 2.1 * sy, X, gy + 2.1 * sy, GRID, 1)
        p.line(gx0, gy, gx1, gy, SOFT, 2); p.line(cx, gy - 2.1 * sy, cx, gy + 2.1 * sy, SOFT, 2)
        labs = {-4: r"-2\pi", -2: r"-\pi", 2: r"\pi", 4: r"2\pi", -3: r"-\frac{3\pi}{2}", -1: r"-\frac{\pi}{2}", 1: r"\frac{\pi}{2}", 3: r"\frac{3\pi}{2}"}
        for m, l in labs.items():
            p.text(f"${l}$", "body", 15, cx + m * math.pi / 2 * sx + 4, gy + 20, SOFT, valign="mid", halo=5)
        for yy, l in ((1, "1"), (-1, "−1")):
            p.line(cx - 5, gy - yy * sy, cx + 5, gy - yy * sy, SOFT, 2)
            p.text(l, "bold", 13, cx - 12, gy - yy * sy, SOFT, "r", "mid", halo=5)
        if lab == "TANGENT":
            for m in (-3, -1, 1, 3):
                X = cx + m * math.pi / 2 * sx; p.line(X, gy - 2.1 * sy, X, gy + 2.1 * sy, col, 2, dash=[6, 6])
        p.c.new_path(); started = False
        for i in range(1201):
            xv = -2 * math.pi + 4 * math.pi * i / 1200; yv = f(xv)
            if abs(yv) > 2.2:
                started = False; continue
            X, Y = cx + xv * sx, gy - yv * sy
            (p.c.line_to if started else p.c.move_to)(X, Y); started = True
        p.stroke(col, 5)
        p.c.restore()
        p.text(formula, "body", 30, x0 + 30, y0 + 48, col, "l", "mid", halo=8)
        p.text(note, "bold", 15, x0 + w - 20, y0 + h - 16, SOFT, "r", halo=8)


# =========================================================== 6 LAW OF SINES & COSINES
@poster("orange")
def laws(p):
    a = ACC["orange"]; p.frame("Law of Sines & Cosines", "for ANY triangle, not just right triangles", a, n(laws))
    A_, B_, C_ = (130, 470), (620, 470), (430, 230)
    p.c.new_path(); p.poly([A_, B_, C_]); p.fs(tint(a, 0.85), INK, 5)
    for (pt, lab, dx, dy) in ((A_, "A", -26, 10), (B_, "B", 26, 10), (C_, "C", 0, -26)):
        p.text(lab, "title", 36, pt[0] + dx, pt[1] + dy, a, valign="mid")
    mid = lambda u, v: ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
    for (u, v, lab, dx, dy) in ((B_, C_, "a", 26, -6), (A_, C_, "b", -22, -18), (A_, B_, "c", 0, 30)):
        m_ = mid(u, v); p.text(f"${lab}$", "body", 40, m_[0] + dx, m_[1] + dy, INK, valign="mid")
    p.card(60, 545, 630, 150, a, "LAW OF SINES")
    p.text(r"$\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}$", "body", 44, 375, 605, INK, valign="mid")
    p.text("use it for  AAS · ASA · SSA (watch for the ambiguous case)", "bold", 16, 375, 668, SOFT, valign="mid")
    p.card(60, 730, 630, 150, a, "LAW OF COSINES")
    p.text(r"$c^2=a^2+b^2-2ab\,\cos C$", "body", 44, 375, 790, INK, valign="mid")
    p.text("use it for  SAS · SSS", "bold", 16, 375, 853, SOFT, valign="mid")
    p.text(r"Area of any triangle:   $K=\frac{1}{2}ab\,\sin C$", "bold", 22, 375, 918, INK, valign="mid")


# =========================================================== 7 ORDER OF OPERATIONS
@poster("red")
def pemdas(p):
    a = ACC["red"]; p.frame("Order of Operations", "work from the top step to the bottom step", a, n(pemdas))
    steps = [("P", "Parentheses", "( )  [ ]  { }", ACC["red"]), ("E", "Exponents", "x²  √x", ACC["orange"]),
             ("MD", "Multiply & Divide", "× ÷   left to right", ACC["green"]), ("AS", "Add & Subtract", "+ −   left to right", ACC["blue"])]
    for i, (k, name, ex, col) in enumerate(steps):
        y = 215 + i * 112; x = 60 + i * 22
        p.rrect(x, y, 630 - i * 44, 96, 24); p.fs(tint(col, 0.85), col, 3)
        p.rrect(x, y, 120, 96, 24); p.fill(col)
        p.text(k, "title", 48 if len(k) == 1 else 40, x + 60, y + 48, WHITE, valign="mid")
        p.text(name, "title", 34, x + 145, y + 40, INK, "l", "mid")
        p.text(ex, "bold", 20, x + 145, y + 74, SOFT, "l", "mid")
    p.card(60, 690, 630, 245, a, "EXAMPLE")
    lines = [r"$3+6\times(5+4)\div 3-7$", r"$=3+6\times 9\div 3-7$", r"$=3+54\div 3-7$", r"$=3+18-7$", r"$=14$"]
    tags = ["", "P", "M", "D", "A, S"]
    for i, (ln, t) in enumerate(zip(lines, tags)):
        y = 730 + i * 42
        p.text(ln, "body", 30, 120, y, INK if i < 4 else a, "l", "mid")
        if t:
            p.rrect(560, y - 15, 90, 30, 15); p.fill(tint(a, 0.6)); p.text(t, "black", 16, 605, y, INK, valign="mid")


# =========================================================== 8 SLOPE & LINEAR EQUATIONS
@poster("indigo")
def slope(p):
    a = ACC["indigo"]; p.frame("Slope & Linear Equations", "rise over run", a, n(slope))
    # graph
    gx, gy, s = 70, 220, 26
    for i in range(11):
        p.line(gx + i * s, gy, gx + i * s, gy + 10 * s, GRID, 1); p.line(gx, gy + i * s, gx + 10 * s, gy + i * s, GRID, 1)
    p.line(gx, gy + 7 * s, gx + 10 * s, gy + 7 * s, SOFT, 2); p.line(gx + 2 * s, gy, gx + 2 * s, gy + 10 * s, SOFT, 2)
    P1 = (gx + 3 * s, gy + 6 * s); P2 = (gx + 8 * s, gy + 2 * s)
    p.line(gx + 0.5 * s, gy + 8 * s, gx + 10 * s, gy + 0.4 * s, a, 5)
    p.line(P1[0], P1[1], P2[0], P1[1], ACC["green"], 4, dash=[8, 6]); p.line(P2[0], P1[1], P2[0], P2[1], ACC["coral"], 4, dash=[8, 6])
    p.text("run", "black", 18, (P1[0] + P2[0]) / 2, P1[1] + 22, ACC["green"], valign="mid")
    p.text("rise", "black", 18, P2[0] + 30, (P1[1] + P2[1]) / 2, ACC["coral"], valign="mid")
    for pt, lab in ((P1, r"$(x_1,y_1)$"), (P2, r"$(x_2,y_2)$")):
        p.circle(*pt, 7); p.fs(a, WHITE, 2); p.text(lab, "body", 20, pt[0] - 12, pt[1] - 20, INK, "r", "mid")
    p.card(370, 220, 320, 260, a, "SLOPE")
    p.text(r"$m=\frac{y_2-y_1}{x_2-x_1}$", "body", 46, 530, 330, INK, valign="mid")
    p.text(r"$=\frac{\mathrm{rise}}{\mathrm{run}}$", "body", 38, 530, 420, a, valign="mid")
    forms = [("SLOPE-INTERCEPT", r"$y=mx+b$", "m = slope,  b = y-intercept"),
             ("POINT-SLOPE", r"$y-y_1=m(x-x_1)$", "through the point (x₁, y₁)"),
             ("STANDARD", r"$Ax+By=C$", "A, B, C are integers")]
    for i, (lab, f, note) in enumerate(forms):
        y = 525 + i * 95
        p.card(60, y, 630, 78, a, lab)
        p.text(f, "body", 34, 250, y + 42, INK, valign="mid"); p.text(note, "bold", 16, 470, y + 42, SOFT, "l", "mid")
    kinds = [("positive", 1), ("negative", -1), ("zero", 0), ("undefined", None)]
    for i, (k, m) in enumerate(kinds):
        x = 100 + i * 160; y = 865
        p.rrect(x - 50, y - 30, 100, 60, 12); p.fs(WHITE, tint(a, 0.4), 2)
        if m is None:
            p.line(x, y - 22, x, y + 22, a, 4)
        else:
            p.line(x - 36, y + 18 * m, x + 36, y - 18 * m, a, 4)
        p.text(k, "black", 15, x, y + 48, INK, valign="mid")


# =========================================================== 9 QUADRATIC FORMULA
@poster("pink")
def quadratic(p):
    a = ACC["pink"]; p.frame("The Quadratic Formula", "solves any equation  ax² + bx + c = 0", a, n(quadratic))
    p.card(60, 215, 630, 165, a, None, 0.86)
    p.text(r"$x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}$", "body", 72, 375, 300, INK, valign="mid")
    # parabola with roots and vertex
    gx0, gx1, gy = 110, 640, 600; sx = 48; sy = 22
    p.line(gx0, gy, gx1, gy, SOFT, 2); p.line(375, 420, 375, 660, SOFT, 2)
    f = lambda x: 0.5 * (x - 0.5) ** 2 - 4.5
    p.c.new_path()
    for i in range(201):
        xv = -4.6 + 10.2 * i / 200; X, Y = 375 + xv * sx, gy - f(xv) * sy
        if Y < 415:
            continue
        (p.c.line_to if p.c.has_current_point() else p.c.move_to)(X, Y)
    p.stroke(a, 5)
    for r_ in (-2.5, 3.5):
        p.circle(375 + r_ * sx, gy, 8); p.fs(ACC["blue"], WHITE, 2)
    p.text("roots", "black", 16, 375 + 3.5 * sx + 34, gy - 20, ACC["blue"], valign="mid")
    vx, vy = 375 + 0.5 * sx, gy + 4.5 * sy
    p.circle(vx, vy, 8); p.fs(ACC["green"], WHITE, 2)
    p.text(r"vertex  $x=-\frac{b}{2a}$", "bold", 18, vx + 20, vy + 4, ACC["green"], "l", "mid")
    p.line(vx, gy - 170, vx, gy + 110, ACC["green"], 2, dash=[6, 6])
    p.card(60, 735, 630, 200, a, "THE DISCRIMINANT   b² − 4ac")
    cases = [(">0", "2 real roots", -2.0), ("=0", "1 real root", 0.0), ("<0", "no real roots", 1.6)]
    for i, (sgn, txt, k) in enumerate(cases):
        x = 165 + i * 210; y = 790
        p.line(x - 70, y, x + 70, y, SOFT, 1.5)
        p.c.new_path()
        for j in range(61):
            xv = -1.6 + 3.2 * j / 60; X, Y = x + xv * 40, y - (xv * xv + k) * 16
            if Y > y + 36 or Y < y - 45:
                continue
            (p.c.line_to if p.c.has_current_point() else p.c.move_to)(X, Y)
        p.stroke(a, 4)
        for r0 in ([-math.sqrt(-k), math.sqrt(-k)] if k < 0 else ([0.0] if k == 0 else [])):
            p.circle(x + r0 * 40, y, 6); p.fs(ACC["blue"], WHITE, 2)
        p.text(f"$b^2-4ac{sgn}$", "body", 22, x, y + 72, INK, valign="mid"); p.text(txt, "black", 15, x, y + 102, SOFT, valign="mid")


# =========================================================== 10 LAWS OF EXPONENTS
@poster("gold")
def exponents(p):
    a = ACC["gold"]; p.frame("Laws of Exponents", "the rules for powers", a, n(exponents))
    rules = [("PRODUCT", r"$a^m\cdot a^n=a^{m+n}$", r"$x^2\cdot x^3=x^5$"),
             ("QUOTIENT", r"$\frac{a^m}{a^n}=a^{m-n}$", r"$\frac{x^7}{x^4}=x^3$"),
             ("POWER OF A POWER", r"$(a^m)^n=a^{mn}$", r"$(x^2)^4=x^8$"),
             ("POWER OF A PRODUCT", r"$(ab)^n=a^nb^n$", r"$(2x)^3=8x^3$"),
             ("POWER OF A QUOTIENT", r"$\left(\frac{a}{b}\right)^n=\frac{a^n}{b^n}$", r"$\left(\frac{x}{3}\right)^2=\frac{x^2}{9}$"),
             ("ZERO EXPONENT", r"$a^0=1$", r"$7^0=1$"),
             ("NEGATIVE EXPONENT", r"$a^{-n}=\frac{1}{a^n}$", r"$x^{-2}=\frac{1}{x^2}$"),
             ("FRACTIONAL EXPONENT", r"$a^{\frac{m}{n}}=\sqrt[n]{a^m}$", r"$8^{\frac{2}{3}}=4$")]
    for i, (lab, rule, ex) in enumerate(rules):
        col, row = i % 2, i // 2; x = 60 + col * 325; y = 215 + row * 182
        p.card(x, y, 305, 162, a, lab, 0.86)
        p.fit_text(rule, "body", 36, x + 152, y + 68, 270, INK, valign="mid")
        p.line(x + 40, y + 108, x + 265, y + 108, tint(a, 0.4), 2)
        p.fit_text(ex, "body", 26, x + 152, y + 136, 260, SOFT, valign="mid")
