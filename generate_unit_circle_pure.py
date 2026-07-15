"""
generate_unit_circle_pure.py — Unit Circle test images (stdlib only)
====================================================================
No matplotlib / numpy / PIL required. Writes PNG via zlib.

  python generate_unit_circle_pure.py
"""
from __future__ import annotations

import math
import os
import struct
import zlib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "unit_circle")
PREVIEWS = os.path.join(OUT, "previews")
PRINTS = os.path.join(OUT, "prints")

# Palette (RGB) — scientific plate family
CREAM = (244, 241, 234)
GRID = (230, 226, 216)
GRID_FINE = (237, 234, 227)
INK = (26, 26, 26)
INK_SOFT = (85, 85, 85)
INK_FAINT = (138, 133, 124)
RUST = (184, 92, 56)
LINE = (34, 34, 34)
WHITE = (255, 255, 255)
ROW_ALT = (239, 235, 227)


# ── Minimal PNG writer ───────────────────────────────────────────────────────
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def save_png(path: str, pixels: list[list[tuple[int, int, int]]]):
    """pixels[y][x] = (r,g,b)"""
    h = len(pixels)
    w = len(pixels[0]) if h else 0
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter none
        for x in range(w):
            r, g, b = pixels[y][x]
            raw.extend((r, g, b))
    compressed = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", compressed) + _png_chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print(f"  wrote {path}  ({os.path.getsize(path)/1024:.0f} KB)  {w}x{h}")


# ── Canvas ───────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg=CREAM):
        self.w = w
        self.h = h
        self.px = [[bg for _ in range(w)] for _ in range(h)]

    def set(self, x: int, y: int, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def fill_rect(self, x0, y0, x1, y1, c):
        x0, x1 = max(0, min(x0, x1)), min(self.w - 1, max(x0, x1))
        y0, y1 = max(0, min(y0, y1)), min(self.h - 1, max(y0, y1))
        for y in range(y0, y1 + 1):
            row = self.px[y]
            for x in range(x0, x1 + 1):
                row[x] = c

    def line(self, x0, y0, x1, y1, c, thickness=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if thickness <= 1:
                self.set(x0, y0, c)
            else:
                r = thickness // 2
                for yy in range(-r, r + 1):
                    for xx in range(-r, r + 1):
                        if xx * xx + yy * yy <= r * r + 1:
                            self.set(x0 + xx, y0 + yy, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, thickness=2, fill=False):
        cx, cy, r = int(round(cx)), int(round(cy)), int(round(r))
        if fill:
            for y in range(-r, r + 1):
                for x in range(-r, r + 1):
                    if x * x + y * y <= r * r:
                        self.set(cx + x, cy + y, c)
            return
        # ring
        r2_outer = (r + thickness // 2) ** 2
        r2_inner = max(0, (r - (thickness + 1) // 2)) ** 2
        for y in range(-r - thickness, r + thickness + 1):
            for x in range(-r - thickness, r + thickness + 1):
                d = x * x + y * y
                if r2_inner <= d <= r2_outer:
                    self.set(cx + x, cy + y, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def graph_paper(self, major=40, minor=10):
        for x in range(0, self.w, minor):
            for y in range(self.h):
                self.px[y][x] = GRID_FINE if x % major else GRID
        for y in range(0, self.h, minor):
            for x in range(self.w):
                # keep major stronger
                cur = self.px[y][x]
                if y % major == 0:
                    self.px[y][x] = GRID
                elif cur == CREAM:
                    self.px[y][x] = GRID_FINE

    def border(self, m, c=GRID, t=2):
        self.line(m, m, self.w - 1 - m, m, c, t)
        self.line(m, self.h - 1 - m, self.w - 1 - m, self.h - 1 - m, c, t)
        self.line(m, m, m, self.h - 1 - m, c, t)
        self.line(self.w - 1 - m, m, self.w - 1 - m, self.h - 1 - m, c, t)

    # 5x7 bitmap font (uppercase + digits + few symbols)
    _FONT = {
        " ": [],
        "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
        "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
        "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
        "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
        "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
        "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
        "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
        "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
        "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
        "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
        "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
        "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
        "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
        "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
        "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
        "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
        "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
        "W": ["10001", "10001", "10001", "10001", "10101", "11011", "10001"],
        "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
        "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
        "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
        "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
        "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
        "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
        "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
        "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
        "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
        "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
        "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
        "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
        "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
        ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
        ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
        "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
        "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
        "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
        "/": ["00001", "00010", "00100", "01000", "10000", "00000", "00000"],
        "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
        ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
        "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
        "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
        "°": ["01110", "10001", "10001", "01110", "00000", "00000", "00000"],
        "π": ["00000", "11111", "10101", "10101", "10101", "10101", "10101"],
        "√": ["00001", "00001", "00010", "10010", "01000", "00100", "00000"],
        "·": ["00000", "00000", "01100", "01100", "00000", "00000", "00000"],
        "θ": ["01110", "10001", "11111", "10001", "10001", "10001", "01110"],
        "²": ["01100", "00010", "00100", "01000", "01110", "00000", "00000"],
    }

    def text(self, x, y, s, c=INK, scale=2, align="left"):
        s = s.upper()
        # measure
        char_w = 6 * scale
        total = len(s) * char_w
        if align == "center":
            x = int(x - total / 2)
        elif align == "right":
            x = int(x - total)
        cx = int(x)
        cy = int(y)
        for ch in s:
            glyph = self._FONT.get(ch) or self._FONT.get(ch.upper()) or self._FONT[" "]
            if not glyph:
                cx += char_w
                continue
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col_i * scale + dx, cy + row_i * scale + dy, c)
            cx += char_w

    def text_small(self, x, y, s, c=INK, scale=1, align="left"):
        self.text(x, y, s, c=c, scale=scale, align=align)


# ── Geometry helpers ─────────────────────────────────────────────────────────
ANGLES = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]

RAD_LABELS = {
    0: "0",
    30: "π/6",
    45: "π/4",
    60: "π/3",
    90: "π/2",
    120: "2π/3",
    135: "3π/4",
    150: "5π/6",
    180: "π",
    210: "7π/6",
    225: "5π/4",
    240: "4π/3",
    270: "3π/2",
    300: "5π/3",
    315: "7π/4",
    330: "11π/6",
}

COORD_LABELS = {
    0: "(1, 0)",
    45: "(√2/2, √2/2)",
    90: "(0, 1)",
    135: "(-√2/2, √2/2)",
    180: "(-1, 0)",
    225: "(-√2/2, -√2/2)",
    270: "(0, -1)",
    315: "(√2/2, -√2/2)",
}


def draw_unit_circle(cv: Canvas, cx: int, cy: int, R: int, label_scale=2, highlight_45=True):
    # axes
    cv.line(cx - R - 40, cy, cx + R + 40, cy, LINE, 2)
    cv.line(cx, cy + R + 40, cx, cy - R - 40, LINE, 2)
    # arrow heads
    tip_x = cx + R + 40
    cv.line(tip_x, cy, tip_x - 12, cy - 7, LINE, 2)
    cv.line(tip_x, cy, tip_x - 12, cy + 7, LINE, 2)
    tip_y = cy - R - 40
    cv.line(cx, tip_y, cx - 7, tip_y + 12, LINE, 2)
    cv.line(cx, tip_y, cx + 7, tip_y + 12, LINE, 2)
    cv.text(tip_x + 6, cy - 18, "X", INK, scale=label_scale)
    cv.text(cx + 10, tip_y - 8, "Y", INK, scale=label_scale)

    # circle
    cv.circle(cx, cy, R, LINE, thickness=3)

    # quadrants
    qs = label_scale
    cv.text(cx + int(0.35 * R), cy - int(0.35 * R) - 8, "I", INK_FAINT, scale=qs)
    cv.text(cx - int(0.45 * R), cy - int(0.35 * R) - 8, "II", INK_FAINT, scale=qs)
    cv.text(cx - int(0.50 * R), cy + int(0.30 * R), "III", INK_FAINT, scale=qs)
    cv.text(cx + int(0.32 * R), cy + int(0.30 * R), "IV", INK_FAINT, scale=qs)

    for deg in ANGLES:
        th = math.radians(deg)
        # screen y is down
        px = cx + R * math.cos(th)
        py = cy - R * math.sin(th)
        cv.line(cx, cy, px, py, INK_FAINT, 1)
        major = deg % 90 == 0
        cv.disc(px, py, 5 if major else 3, RUST if deg in (0, 45, 90, 180, 270) else LINE)

        # angle labels outside
        lr = R + 28
        lx = cx + lr * math.cos(th)
        ly = cy - lr * math.sin(th)
        lab = RAD_LABELS[deg]
        cv.text(lx, ly - 6, lab, INK, scale=max(1, label_scale - 0), align="center")
        if deg % 45 == 0:
            lr2 = R + 52
            lx2 = cx + lr2 * math.cos(th)
            ly2 = cy - lr2 * math.sin(th)
            cv.text(lx2, ly2 - 4, f"{deg}°", INK_SOFT, scale=max(1, label_scale - 1), align="center")

        if deg in COORD_LABELS:
            lr3 = R + 78
            # special placement for axis labels
            if deg == 0:
                lx3, ly3 = cx + R + 70, cy + 18
            elif deg == 90:
                lx3, ly3 = cx + 18, cy - R - 70
            elif deg == 180:
                lx3, ly3 = cx - R - 70, cy + 18
            elif deg == 270:
                lx3, ly3 = cx + 18, cy + R + 55
            else:
                lx3 = cx + lr3 * math.cos(th)
                ly3 = cy - lr3 * math.sin(th)
            cv.text(lx3, ly3 - 4, COORD_LABELS[deg], INK_SOFT, scale=max(1, label_scale - 1), align="center")

    # 45° triangle highlight
    if highlight_45:
        th = math.radians(45)
        px = cx + R * math.cos(th)
        py = cy - R * math.sin(th)
        # horizontal cos
        cv.line(cx, cy, px, cy, RUST, 3)
        # vertical sin
        cv.line(px, cy, px, py, RUST, 3)
        # hypotenuse already a ray; redraw thicker
        cv.line(cx, cy, px, py, RUST, 3)
        # right angle mark
        m = max(10, R // 18)
        cv.line(px - m, cy, px - m, cy - m, RUST, 2)
        cv.line(px - m, cy - m, px, cy - m, RUST, 2)
        # labels
        cv.text((cx + px) / 2, cy + 10, "COS θ", RUST, scale=max(1, label_scale - 1), align="center")
        cv.text(px + 10, (cy + py) / 2 - 6, "SIN θ", RUST, scale=max(1, label_scale - 1))
        # small arc for theta
        for a in range(0, 46, 2):
            ar = R * 0.22
            x0 = cx + ar * math.cos(math.radians(a))
            y0 = cy - ar * math.sin(math.radians(a))
            x1 = cx + ar * math.cos(math.radians(a + 2))
            y1 = cy - ar * math.sin(math.radians(a + 2))
            cv.line(x0, y0, x1, y1, RUST, 2)
        cv.text(cx + R * 0.28, cy - R * 0.12, "θ", RUST, scale=label_scale)

    cv.disc(cx, cy, 4, LINE)
    cv.text(cx - 18, cy + 12, "O", INK_SOFT, scale=max(1, label_scale - 1))
    # r=1
    cv.text(cx + R * 0.55, cy - R * 0.55 - 10, "R=1", INK_SOFT, scale=max(1, label_scale - 1))


def make_plate(w=900, h=1125) -> Canvas:
    """Portrait scientific plate test image."""
    cv = Canvas(w, h, CREAM)
    cv.graph_paper(major=45, minor=15)
    cv.border(28, GRID, 2)

    # header
    cv.text(50, 48, "THE UNIT CIRCLE", INK, scale=4)
    cv.text(w - 50, 55, "FIG. 1", INK_SOFT, scale=2, align="right")
    cv.text(50, 100, "TRIGONOMETRY  ·  X=COS θ  Y=SIN θ  ·  X²+Y²=1", RUST, scale=2)
    cv.line(50, 130, w - 50, 130, LINE, 2)

    # circle region
    cx = w // 2
    cy = int(h * 0.48)
    R = int(min(w, h) * 0.28)
    draw_unit_circle(cv, cx, cy, R, label_scale=2, highlight_45=True)

    # footer
    y0 = int(h * 0.82)
    cv.line(50, y0, w - 50, y0, LINE, 1)
    cv.text(50, y0 + 20, "KEY IDENTITIES", INK, scale=2)
    cv.text(50, y0 + 55, "SIN²θ + COS²θ = 1", INK_SOFT, scale=2)
    cv.text(50, y0 + 85, "TAN θ = SIN θ / COS θ", INK_SOFT, scale=2)
    cv.text(50, y0 + 115, "POINT: (COS θ, SIN θ)   ·   π = 180°", INK_SOFT, scale=2)
    cv.text(w - 50, y0 + 115, "MATHRELAXING", INK_FAINT, scale=2, align="right")
    return cv


def make_square(size=1000) -> Canvas:
    cv = Canvas(size, size, CREAM)
    cv.graph_paper(major=40, minor=10)
    cv.text(size // 2, 40, "THE UNIT CIRCLE", INK, scale=4, align="center")
    cv.text(size // 2, 90, "(COS θ, SIN θ)", RUST, scale=2, align="center")
    cv.line(80, 120, size - 80, 120, LINE, 2)
    cx = size // 2
    cy = int(size * 0.55)
    R = int(size * 0.28)
    draw_unit_circle(cv, cx, cy, R, label_scale=2, highlight_45=True)
    return cv


def make_detail(w=1100, h=850) -> Canvas:
    cv = Canvas(w, h, CREAM)
    cv.graph_paper(major=40, minor=10)
    cv.text(40, 35, "DETAIL  ·  REFERENCE ANGLE θ=45°", INK, scale=3)
    cv.text(40, 80, "COS(π/4)=SIN(π/4)=√2/2   ·   RIGHT TRIANGLE ON UNIT CIRCLE", RUST, scale=2)
    cv.line(40, 115, w - 40, 115, LINE, 1)

    # zoomed first quadrant
    cx, cy = 120, h - 100
    R = int(min(w, h) * 0.62)
    cv.line(cx - 20, cy, cx + R + 80, cy, LINE, 2)
    cv.line(cx, cy + 20, cx, cy - R - 80, LINE, 2)
    cv.circle(cx, cy, R, LINE, thickness=3)

    for deg in [0, 30, 45, 60, 90]:
        th = math.radians(deg)
        px = cx + R * math.cos(th)
        py = cy - R * math.sin(th)
        cv.line(cx, cy, px, py, INK_FAINT, 1)
        cv.disc(px, py, 6 if deg == 45 else 4, RUST if deg == 45 else LINE)
        lr = R + 36
        lx = cx + lr * math.cos(th)
        ly = cy - lr * math.sin(th)
        cv.text(lx, ly - 6, f"{RAD_LABELS[deg]}  {deg}°", INK, scale=2, align="center")
        if deg in (0, 45, 90):
            lr2 = R + 70
            lx2 = cx + lr2 * math.cos(th)
            ly2 = cy - lr2 * math.sin(th)
            if deg == 0:
                lx2, ly2 = cx + R + 40, cy + 25
            if deg == 90:
                lx2, ly2 = cx + 30, cy - R - 50
            cv.text(lx2, ly2, COORD_LABELS[deg], INK_SOFT, scale=2, align="center")

    th = math.radians(45)
    px = cx + R * math.cos(th)
    py = cy - R * math.sin(th)
    cv.line(cx, cy, px, cy, RUST, 3)
    cv.line(px, cy, px, py, RUST, 3)
    cv.line(cx, cy, px, py, RUST, 3)
    m = 18
    cv.line(px - m, cy, px - m, cy - m, RUST, 2)
    cv.line(px - m, cy - m, px, cy - m, RUST, 2)
    cv.text((cx + px) / 2, cy + 15, "COS θ", RUST, scale=2, align="center")
    cv.text(px + 12, (cy + py) / 2, "SIN θ", RUST, scale=2)
    for a in range(0, 46, 2):
        ar = R * 0.18
        x0 = cx + ar * math.cos(math.radians(a))
        y0 = cy - ar * math.sin(math.radians(a))
        x1 = cx + ar * math.cos(math.radians(a + 2))
        y1 = cy - ar * math.sin(math.radians(a + 2))
        cv.line(x0, y0, x1, y1, RUST, 2)
    cv.text(cx + R * 0.22, cy - R * 0.10, "θ", RUST, scale=3)
    return cv


def make_table(w=1000, h=800) -> Canvas:
    cv = Canvas(w, h, CREAM)
    cv.graph_paper(major=40, minor=10)
    cv.text(w // 2, 40, "SPECIAL ANGLES", INK, scale=4, align="center")
    cv.text(w // 2, 90, "EXACT VALUES ON THE UNIT CIRCLE", RUST, scale=2, align="center")
    cv.line(80, 125, w - 80, 125, LINE, 2)

    headers = ["θ°", "RAD", "SIN", "COS", "TAN"]
    rows = [
        ["0", "0", "0", "1", "0"],
        ["30", "π/6", "1/2", "√3/2", "1/√3"],
        ["45", "π/4", "√2/2", "√2/2", "1"],
        ["60", "π/3", "√3/2", "1/2", "√3"],
        ["90", "π/2", "1", "0", "—"],
        ["180", "π", "0", "-1", "0"],
        ["270", "3π/2", "-1", "0", "—"],
        ["360", "2π", "0", "1", "0"],
    ]
    cols = [100, 280, 460, 640, 820]
    y = 160
    for i, htxt in enumerate(headers):
        cv.text(cols[i], y, htxt, RUST, scale=2, align="center")
    y = 210
    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            cv.fill_rect(60, y - 12, w - 60, y + 28, ROW_ALT)
        for i, cell in enumerate(row):
            cv.text(cols[i], y, cell, INK, scale=2, align="center")
        y += 55

    cv.text(w // 2, h - 50, "SIN²θ + COS²θ = 1   ·   MATHRELAXING", INK_FAINT, scale=2, align="center")
    return cv


def make_included(w=1000, h=1000) -> Canvas:
    cv = Canvas(w, h, CREAM)
    cv.graph_paper(major=40, minor=10)
    # mini plate on left
    mini_w, mini_h = 420, 560
    # draw mini plate into a subregion by compositing coordinates
    # reuse plate scaled conceptually: just draw circle panel
    cv.text(520, 120, "INCLUDED", INK, scale=4)
    lines = [
        "1 SCIENTIFIC-PLATE PRINT",
        "UNIT CIRCLE · RAD & DEG",
        "EXACT COORDS AT KEY ANGLES",
        "",
        "ASPECT RATIOS:",
        "2:3 · 3:4 · 4:5 · 5:7",
        "ISO A4 · A3",
        "",
        "300 DPI JPG · ZIP",
        "CLASSROOM · STUDY · DORM",
        "",
        "BEST ON MATTE PAPER",
        "INSTANT DOWNLOAD",
    ]
    y = 200
    for line in lines:
        cv.text(520, y, line, INK_SOFT, scale=2)
        y += 40

    # left mini circle
    cx, cy, R = 230, 520, 160
    cv.fill_rect(40, 140, 420, 900, CREAM)
    cv.border_region = None
    # small header
    cv.text(230, 170, "UNIT CIRCLE", INK, scale=2, align="center")
    cv.line(70, 210, 390, 210, LINE, 1)
    draw_unit_circle(cv, cx, cy, R, label_scale=1, highlight_45=True)
    return cv


def main():
    print("=== Unit Circle test images (pure Python PNG) ===")
    os.makedirs(PREVIEWS, exist_ok=True)
    os.makedirs(PRINTS, exist_ok=True)

    print("1/5 plate hero…")
    save_png(os.path.join(PREVIEWS, "unit_circle_preview_1_hero.png"), make_plate().px)

    print("2/5 square listing…")
    sq = make_square()
    save_png(os.path.join(PREVIEWS, "unit_circle_preview_2_square.png"), sq.px)
    save_png(os.path.join(OUT, "unit_circle_cover.png"), sq.px)

    print("3/5 detail 45°…")
    save_png(os.path.join(PREVIEWS, "unit_circle_preview_3_detail.png"), make_detail().px)

    print("4/5 included…")
    save_png(os.path.join(PREVIEWS, "unit_circle_preview_4_included.png"), make_included().px)

    print("5/5 special-angle table…")
    save_png(os.path.join(PREVIEWS, "unit_circle_preview_5_table.png"), make_table().px)

    # also a larger print sample
    print("bonus: larger plate sample…")
    save_png(os.path.join(PRINTS, "unit_circle_A4_test.png"), make_plate(1240, 1754).px)

    print("output:", OUT)
    print("done.")


if __name__ == "__main__":
    main()
