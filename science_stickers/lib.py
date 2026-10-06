"""
Drawing toolkit for the science sticker collection (pycairo).

- Canvas: square ARGB surface, artwork drawn in a 1000-unit coordinate system (y down).
- Text: any TTF (fonts/) or matplotlib mathtext ("$e^{i\\pi}+1=0$", Computer Modern) is turned into
  vector outlines with matplotlib's TextPath, so every glyph is a real path in cairo.
- die_cut(): white sticker border following the artwork's silhouette, plus an optional soft shadow.
"""
import os, math
import numpy as np
import cairo
from PIL import Image, ImageFilter
from scipy import ndimage
import matplotlib
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath

matplotlib.rcParams["mathtext.fontset"] = "cm"
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
FONTS = {k: os.path.join(FD, f) for k, f in {
    "serif": "Fraunces-600.ttf", "serif_b": "Fraunces-800.ttf", "serif_i": "Fraunces-600i.ttf",
    "sans": "Inter-500.ttf", "sans_b": "Inter-700.ttf", "sans_x": "Inter-800.ttf",
    "mono": "JetBrainsMono-500.ttf", "mono_b": "JetBrainsMono-700.ttf"}.items()}


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


# palette: deep ink + warm neutrals + four accents
INK = hexc("1d2742"); NAVY = hexc("243259"); CREAM = hexc("fbf5e9"); PAPER = hexc("f3ead8")
GOLD = hexc("e8b448"); CORAL = hexc("e2694f"); TEAL = hexc("2a9d8f"); SKY = hexc("7fb5da")
LAV = hexc("9d8ad6"); PINK = hexc("ef9aa6"); MINT = hexc("9fd6be"); TAN = hexc("d9a46a")
WHITE = (1, 1, 1, 1)


class Canvas:
    def __init__(self, px=1200):
        self.px = px
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, px, px)
        self.c = cairo.Context(self.surf)
        self.c.scale(px / 1000, px / 1000)
        self.c.set_line_join(cairo.LINE_JOIN_ROUND); self.c.set_line_cap(cairo.LINE_CAP_ROUND)

    # ---- painting helpers ------------------------------------------------
    def fill(self, col, preserve=False):
        self.c.set_source_rgba(*col)
        (self.c.fill_preserve if preserve else self.c.fill)()

    def stroke(self, col, w, preserve=False):
        self.c.set_source_rgba(*col); self.c.set_line_width(w)
        (self.c.stroke_preserve if preserve else self.c.stroke)()

    def fs(self, fillc, strokec=INK, w=10):
        """fill then ink outline (the house style)."""
        if fillc:
            self.fill(fillc, preserve=True)
        if strokec:
            self.stroke(strokec, w)
        else:
            self.c.new_path()

    def circle(self, x, y, r):
        self.c.new_sub_path(); self.c.arc(x, y, r, 0, 2 * math.pi)

    def rrect(self, x, y, w, h, r):
        c = self.c; c.new_sub_path()
        c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        c.close_path()

    def poly(self, pts, close=True):
        c = self.c; c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        if close:
            c.close_path()

    def ellipse(self, x, y, rx, ry, rot=0.0):
        c = self.c; c.save(); c.translate(x, y); c.rotate(rot); c.scale(rx, ry)
        c.new_sub_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()

    def lin(self, x0, y0, x1, y1, stops):
        g = cairo.LinearGradient(x0, y0, x1, y1)
        for t, col in stops:
            g.add_color_stop_rgba(t, *col)
        return g

    def rad(self, x, y, r0, r1, stops):
        g = cairo.RadialGradient(x, y, r0, x, y, r1)
        for t, col in stops:
            g.add_color_stop_rgba(t, *col)
        return g

    # ---- text --------------------------------------------------------------
    def text_path(self, s, font, size, x, y, anchor="c", tracking=0.0):
        """Append text outlines to the current path. anchor: c / l / r on the baseline at y."""
        if tracking and "$" not in s:
            widths = [self.text_width(ch, font, size) for ch in s]
            total = sum(widths) + tracking * (len(s) - 1)
            x0 = {"c": x - total / 2, "l": x, "r": x - total}[anchor]
            for ch, w in zip(s, widths):
                if ch.strip():
                    self.text_path(ch, font, size, x0, y, "l")
                x0 += w + tracking
            return
        tp = TextPath((0, 0), s, size=size, prop=FontProperties(fname=FONTS[font]))
        ext = tp.get_extents()
        w = ext.x1 if anchor != "c" else ext.x0 + ext.x1
        ox = {"c": x - (ext.x0 + ext.x1) / 2, "l": x, "r": x - ext.x1}[anchor]
        self._mpath(tp, ox, y)

    def text_width(self, s, font, size):
        if not s.strip():
            return size * 0.28 * len(s)
        tp = TextPath((0, 0), s, size=size, prop=FontProperties(fname=FONTS[font]))
        e = tp.get_extents()
        return e.x1 + size * 0.04

    def text_bounds(self, s, font, size):
        e = TextPath((0, 0), s, size=size, prop=FontProperties(fname=FONTS[font])).get_extents()
        return e.x0, -e.y1, e.x1, -e.y0

    def _mpath(self, tp, ox, oy):
        c = self.c; last = None
        for verts, code in tp.iter_segments(curves=True, simplify=False):
            v = [(ox + verts[i], oy - verts[i + 1]) for i in range(0, len(verts), 2)]
            if code == MPath.MOVETO:
                c.move_to(*v[0]); last = v[0]
            elif code == MPath.LINETO:
                c.line_to(*v[0]); last = v[0]
            elif code == MPath.CURVE3:
                (qx, qy), (ex, ey) = v; sx, sy = last
                c.curve_to(sx + 2 / 3 * (qx - sx), sy + 2 / 3 * (qy - sy), ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey)
                last = (ex, ey)
            elif code == MPath.CURVE4:
                c.curve_to(*v[0], *v[1], *v[2]); last = v[2]
            elif code == MPath.CLOSEPOLY:
                c.close_path()

    def text(self, s, font, size, x, y, col, anchor="c", tracking=0.0, outline=None, ow=0):
        self.c.new_path(); self.text_path(s, font, size, x, y, anchor, tracking)
        if outline:
            self.stroke(outline, ow, preserve=True)
        self.fill(col)

    def arc_text(self, s, font, size, cx, cy, r, mid_angle, col, tracking=4.0, inward=False):
        """Text on a circle; mid_angle in radians (cairo convention, -pi/2 = top). inward=True reads along the bottom."""
        widths = [self.text_width(ch, font, size) for ch in s]
        total = sum(widths) + tracking * (len(s) - 1)
        sign = -1 if inward else 1
        a = mid_angle - sign * total / 2 / r
        for ch, w in zip(s, widths):
            if not ch.strip():
                a += sign * (w + tracking) / r; continue
            ac = a + sign * (w / 2) / r
            c = self.c; c.save(); c.translate(cx + r * math.cos(ac), cy + r * math.sin(ac))
            c.rotate(ac + (math.pi / 2 if not inward else -math.pi / 2))
            c.new_path(); self.text_path(ch, font, size, 0, size * 0.35 if not inward else size * 0.35, "c")
            self.fill(col); c.restore()
            a += sign * (w + tracking) / r

    # ---- output ------------------------------------------------------------
    def image(self):
        buf = np.ndarray((self.px, self.px, 4), np.uint8, self.surf.get_data(), strides=(self.surf.get_stride(), 4, 1)).copy()
        b, g, r, a = buf[..., 0], buf[..., 1], buf[..., 2], buf[..., 3]
        rgba = np.dstack([r, g, b, a]).astype(np.float32)
        af = np.maximum(a.astype(np.float32), 1) / 255
        rgba[..., :3] = np.clip(rgba[..., :3] / af[..., None], 0, 255)   # un-premultiply
        return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def die_cut(art, border=0.035, shadow=False):
    """White sticker border around the artwork silhouette. border = fraction of the canvas width."""
    a = np.array(art)[..., 3] > 8
    pad = int(art.width * (border + 0.04))
    A = np.pad(a, pad)
    d = ndimage.distance_transform_edt(~A)
    R = art.width * border
    mask = (d <= R).astype(np.float32)
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(R * 0.35))
    m = m.point(lambda v: 255 if v > 127 else 0).filter(ImageFilter.GaussianBlur(1.2))
    W = A.shape[1]; out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (W, W), (20, 24, 40, 0)); sh.putalpha(m.point(lambda v: v * 0.28).filter(ImageFilter.GaussianBlur(R * 0.6)))
        out.alpha_composite(sh, (int(R * 0.15), int(R * 0.35)))
    white = Image.new("RGBA", (W, W), (255, 255, 255, 0)); white.putalpha(m)
    out.alpha_composite(white); out.alpha_composite(art, (pad, pad))
    bbox = out.getbbox()
    return out.crop(bbox)
