"""
Vector drawing kit for the Trig & Algebra classroom posters (pycairo).

Every poster is drawn in a 750 x 1000 unit box (3:4). render() places that box on any paper size
(PDF, vector) or on a PNG. Text, including math, is converted to outlines with matplotlib's TextPath:
plain strings use the Fredoka / Nunito fonts, "$...$" strings use mathtext (Computer Modern).
"""
import os, math
import cairo
import matplotlib
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath

matplotlib.rcParams["mathtext.fontset"] = "cm"
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
FONTS = {"title": "Fredoka-700.ttf", "title_s": "Fredoka-600.ttf", "body": "Nunito-700.ttf",
         "bold": "Nunito-800.ttf", "black": "Nunito-900.ttf", "semi": "Nunito-600.ttf"}
_PROPS = {k: FontProperties(fname=os.path.join(FD, v)) for k, v in FONTS.items()}
_CACHE = {}


def hexc(h, a=1.0):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


INK = hexc("2b2d42"); SOFT = hexc("6b6f85"); PAPER = hexc("fffdf8"); WHITE = (1, 1, 1, 1); GRID = hexc("e6e3dc")
ACC = {"red": hexc("e5534b"), "coral": hexc("ef6f6c"), "orange": hexc("f39237"), "gold": hexc("e9b52f"),
       "green": hexc("4caf6e"), "teal": hexc("1fa39b"), "blue": hexc("3d85d6"), "indigo": hexc("5866c4"),
       "purple": hexc("9562cc"), "pink": hexc("e2689f")}


def tint(col, t):
    """mix a colour with white (t = 0 original, 1 white)."""
    return tuple(c + (1 - c) * t for c in col[:3]) + (1,)


class P:
    """Poster painter: thin wrapper around a cairo context in poster units."""

    def __init__(self, c):
        self.c = c
        c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)

    # ---- shapes
    def rrect(self, x, y, w, h, r):
        c = self.c; r = min(r, w / 2, h / 2); c.new_sub_path()
        c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()

    def circle(self, x, y, r):
        self.c.new_sub_path(); self.c.arc(x, y, r, 0, 2 * math.pi)

    def poly(self, pts, close=True):
        self.c.move_to(*pts[0])
        for p in pts[1:]:
            self.c.line_to(*p)
        if close:
            self.c.close_path()

    def line(self, x0, y0, x1, y1, col=INK, w=2.0, dash=None):
        c = self.c; c.new_path(); c.move_to(x0, y0); c.line_to(x1, y1)
        c.set_dash(dash or []); self.stroke(col, w); c.set_dash([])

    def fill(self, col, keep=False):
        self.c.set_source_rgba(*col); (self.c.fill_preserve if keep else self.c.fill)()

    def stroke(self, col, w, keep=False):
        self.c.set_source_rgba(*col); self.c.set_line_width(w); (self.c.stroke_preserve if keep else self.c.stroke)()

    def fs(self, fill=None, stroke=None, w=2.0):
        if fill:
            self.fill(fill, keep=True)
        if stroke:
            self.stroke(stroke, w, keep=True)
        self.c.new_path()

    def arrow(self, x0, y0, x1, y1, col=INK, w=2.0, head=10):
        self.line(x0, y0, x1, y1, col, w)
        a = math.atan2(y1 - y0, x1 - x0)
        self.c.new_path()
        self.poly([(x1, y1), (x1 - head * math.cos(a - 0.4), y1 - head * math.sin(a - 0.4)),
                   (x1 - head * math.cos(a + 0.4), y1 - head * math.sin(a + 0.4))]); self.fill(col)

    # ---- text
    def _tp(self, s, font, size):
        key = (s, font, size)
        if key not in _CACHE:
            _CACHE[key] = TextPath((0, 0), s, size=size, prop=_PROPS[font])
        return _CACHE[key]

    def bounds(self, s, font, size):
        e = self._tp(s, font, size).get_extents(); return e.x0, -e.y1, e.x1, -e.y0

    def width(self, s, font, size):
        x0, _, x1, _ = self.bounds(s, font, size); return x1 - x0

    def text(self, s, font, size, x, y, col=INK, anchor="c", valign="base", halo=0):
        """anchor c/l/r horizontally; valign 'base' (y is the baseline) or 'mid' (y is the visual centre)."""
        if not s.strip():
            return
        tp = self._tp(s, font, size); e = tp.get_extents()
        ox = {"c": x - (e.x0 + e.x1) / 2, "l": x - e.x0, "r": x - e.x1}[anchor]
        oy = y if valign == "base" else y + (e.y0 + e.y1) / 2
        c = self.c; c.new_path(); last = None
        for verts, code in tp.iter_segments(curves=True, simplify=False):
            v = [(ox + verts[i], oy - verts[i + 1]) for i in range(0, len(verts), 2)]
            if code == MPath.MOVETO:
                c.move_to(*v[0]); last = v[0]
            elif code == MPath.LINETO:
                c.line_to(*v[0]); last = v[0]
            elif code == MPath.CURVE3:
                (qx, qy), (ex, ey) = v; sx, sy = last
                c.curve_to(sx + 2 / 3 * (qx - sx), sy + 2 / 3 * (qy - sy), ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey); last = (ex, ey)
            elif code == MPath.CURVE4:
                c.curve_to(*v[0], *v[1], *v[2]); last = v[2]
            elif code == MPath.CLOSEPOLY:
                c.close_path()
        if halo:
            self.stroke(PAPER, halo, keep=True)
        self.fill(col)

    def fit_text(self, s, font, size, x, y, maxw, col=INK, anchor="c", valign="base"):
        w = self.width(s, font, size)
        if w > maxw:
            size *= maxw / w
        self.text(s, font, size, x, y, col, anchor, valign)

    def para(self, s, font, size, x, y, maxw, col=INK, lead=1.35, anchor="l"):
        words = s.split(); line = ""; lines = []
        for w in words:
            t = (line + " " + w).strip()
            if self.width(t, font, size) > maxw and line:
                lines.append(line); line = w
            else:
                line = t
        lines.append(line)
        for i, ln in enumerate(lines):
            self.text(ln, font, size, x, y + i * size * lead, col, anchor)
        return y + len(lines) * size * lead

    # ---- poster furniture
    def frame(self, title, subtitle, acc, num, total=10):
        self.c.rectangle(0, 0, 750, 1000); self.fill(acc)
        self.rrect(22, 22, 706, 956, 34); self.fill(PAPER)
        self.rrect(46, 46, 658, 132, 26); self.fill(acc)
        self.fit_text(title, "title", 66, 375, 120, 600, WHITE, valign="mid")
        if subtitle:
            self.fit_text(subtitle, "bold", 20, 375, 163, 600, tint(acc, 0.75))
        self.text(f"TRIG & ALGEBRA CLASSROOM SET  ·  {num}/{total}", "bold", 11, 60, 958, SOFT, "l")
        self.text("MathRelaxing", "title_s", 14, 690, 958, acc, "r")

    def card(self, x, y, w, h, acc, label=None, fill_t=0.88):
        self.rrect(x, y, w, h, 18); self.fs(tint(acc, fill_t), acc, 3)
        if label:
            lw = self.width(label, "black", 15) + 30
            self.rrect(x + 18, y - 14, lw, 28, 14); self.fill(acc)
            self.text(label, "black", 15, x + 18 + lw / 2, y, WHITE, valign="mid")


def render(draw, path, w_pt, h_pt, kind="pdf", px_per_pt=1.0, surface=None):
    """Draw a 750x1000 poster onto a page of w_pt x h_pt (fit, centred, background extended)."""
    if kind == "pdf":
        surf = surface or cairo.PDFSurface(path, w_pt, h_pt)
    else:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, int(w_pt * px_per_pt), int(h_pt * px_per_pt))
    c = cairo.Context(surf)
    if kind != "pdf":
        c.scale(px_per_pt, px_per_pt)
    s = min(w_pt / 750, h_pt / 1000); ox = (w_pt - 750 * s) / 2; oy = (h_pt - 1000 * s) / 2
    acc = draw.ACC
    c.rectangle(0, 0, w_pt, h_pt); c.set_source_rgba(*acc); c.fill()        # bleed in the accent colour
    c.translate(ox, oy); c.scale(s, s)
    draw(P(c))
    if kind == "pdf":
        c.show_page()
        return surf
    surf.write_to_png(path)
