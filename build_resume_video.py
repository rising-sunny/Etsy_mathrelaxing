"""
build_resume_video.py — Simulated Word UI promo (calm, complete draft)
=====================================================================
Shows the FULL Editorial resume draft, then edits placeholders one by one.
No zoom effects. No typing SFX — silent visual demo.
Word chrome modeled after modern Microsoft Word (ribbon, tabs, status).

  python build_resume_video.py
"""
from __future__ import annotations

import math
import os
import random
import shutil
import struct
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont

import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "resume_kit")
FRAMES = os.path.join(OUT, "_video_frames")
AUDIO_DIR = os.path.join(OUT, "_video_audio")
VIDEO = os.path.join(OUT, "Editorial_Resume_Kit_promo.mp4")
VIDEO_SILENT = os.path.join(OUT, "_promo_silent.mp4")
CHECK = os.path.join(OUT, "_video_checks")

S = 1080
FPS = 30
DURATION = 20.0
N = int(DURATION * FPS)
RNG = random.Random(62)

# Editorial palette
NAVY = (18, 23, 46)
GOLD = (184, 148, 70)
CREAM = (252, 250, 245)
INK = (40, 40, 40)
SOFT = (110, 108, 105)
MUTED = (140, 138, 134)
TEAL = (47, 111, 106)
WHITE = (255, 255, 255)
SELECT = (180, 213, 254)
WORD_BLUE = (24, 90, 189)
RIBBON = (245, 244, 242)
TAB_BG = (236, 240, 232)  # soft green-grey like modern Word
TITLE_DARK = (43, 43, 43)
STATUS = (248, 248, 248)
DESK = (228, 226, 222)
LINE = (210, 208, 205)

# Full draft placeholders → typed values
TYPING = {
    "name": "ALEX RIVERA",
    "role": "Data Scientist  ·  Applied Mathematics",
    "contact": "alex.rivera@email.com  ·  (555) 014-2088  ·  San Francisco, CA",
    "summary": "Data scientist with 6+ years turning models into product decisions.",
    "skills": "Python  ·  Causal Inference  ·  Experimentation  ·  SQL  ·  ML Ops",
    "job": "Senior Data Scientist",
    "company": "Northline Analytics  ·  San Francisco",
    "bullet1": "Lifted paid conversion +12% ($4.2M ARR).",
    "bullet2": "Owned experimentation across 40+ product squads.",
    "degree": "M.S. Applied Mathematics",
    "school": "University of California, Berkeley",
    "work": "Open-source forecasting toolkit — 2.4k GitHub stars.",
}

PLACEHOLDERS = {
    "name": "YOUR FULL NAME",
    "role": "Target Role  ·  Specialty",
    "contact": "email@domain.com  ·  (555) 000-0000  ·  City, ST  ·  linkedin.com/in/you",
    "summary": "[Editorial summary — precise, calm, numbers-forward.]",
    "skills": "Skill · Skill · Skill · Method · Stack",
    "job": "Job Title",
    "company": "Company  ·  Location",
    "bullet1": "Impact bullet with metric.",
    "bullet2": "Ownership and scope.",
    "degree": "Degree",
    "school": "School",
    "work": "Selected work highlight.",
}


def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["georgiab.ttf", "timesbd.ttf", "calibrib.ttf"]
        if bold
        else ["georgia.ttf", "times.ttf", "calibri.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _font_sans(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _lerp(a, b, t):
    t = _ease(t)
    if isinstance(a, (tuple, list)):
        return type(a)(a[i] + (b[i] - a[i]) * t for i in range(len(a)))
    return a + (b - a) * t


# Layout: keep full draft readable in frame
PAGE = (78, 188, S - 78, S - 70)  # x0,y0,x1,y1


# ── Audio ────────────────────────────────────────────────────────────────────

def _write_wav(path: str, samples: list[float], rate: int = 44100):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(
            b"".join(
                struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples
            )
        )


def _synth_key(rate=44100, kind="key") -> list[float]:
    dur = 0.028 if kind == "key" else 0.048
    n = int(rate * dur)
    f0 = RNG.uniform(1700, 3400) if kind == "key" else RNG.uniform(420, 800)
    out = []
    for i in range(n):
        t = i / rate
        env = math.exp(-t * (110 if kind == "key" else 55))
        tone = math.sin(2 * math.pi * f0 * t) * 0.26
        noise = (RNG.random() * 2 - 1) * 0.4 * math.exp(-t * 230)
        thump = math.sin(2 * math.pi * 95 * t) * 0.15 * math.exp(-t * 70)
        out.append((tone + noise + thump) * env * (0.52 if kind == "key" else 0.68))
    return out


def _build_sfx(events: list[tuple[float, str]], path: str, total_sec: float, rate=44100):
    total_n = int((total_sec + 0.4) * rate)
    mix = [0.0] * total_n
    keys = [_synth_key(rate, "key") for _ in range(12)]
    clicks = [_synth_key(rate, "click") for _ in range(4)]
    for t, kind in events:
        pool = keys if kind == "key" else clicks
        clip = pool[RNG.randint(0, len(pool) - 1)]
        start = int(t * rate)
        for i, s in enumerate(clip):
            if 0 <= start + i < total_n:
                mix[start + i] += s
    peak = max(1e-6, max(abs(x) for x in mix))
    _write_wav(path, [x * 0.88 / peak for x in mix], rate)


# ── Cursor ───────────────────────────────────────────────────────────────────

def _draw_cursor(img: Image.Image, x, y, mode="arrow", clicking=False):
    d = ImageDraw.Draw(img, "RGBA")
    if mode == "ibeam":
        h = 22
        d.line([(x, y - h // 2), (x, y + h // 2)], fill=(20, 20, 20, 255), width=2)
        d.line([(x - 4, y - h // 2), (x + 4, y - h // 2)], fill=(20, 20, 20, 255), width=2)
        d.line([(x - 4, y + h // 2), (x + 4, y + h // 2)], fill=(20, 20, 20, 255), width=2)
        return
    s = 20
    pts = [
        (x, y),
        (x, y + s * 1.55),
        (x + s * 0.38, y + s * 1.2),
        (x + s * 0.72, y + s * 1.85),
        (x + s * 0.95, y + s * 1.7),
        (x + s * 0.55, y + s * 1.05),
        (x + s * 0.95, y + s * 1.05),
    ]
    d.polygon(pts, fill=(15, 15, 15, 245), outline=(255, 255, 255, 230))
    if clicking:
        r = 14
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 120), width=2)


# ── Realistic Word chrome ────────────────────────────────────────────────────

def _icon_btn(d, x, y, w, h, label, font, active=False):
    fill = (229, 243, 255) if active else WHITE
    outline = WORD_BLUE if active else (205, 203, 200)
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill, outline=outline)
    d.text((x + w / 2, y + h / 2), label, font=font, fill=INK, anchor="mm")


def _draw_word_chrome(d: ImageDraw.ImageDraw, zoom_pct: int = 100):
    # Window outer
    d.rectangle([0, 0, S, S], fill=(60, 60, 60))
    d.rectangle([10, 10, S - 10, S - 10], fill=TAB_BG)

    # Title bar (dark strip like Word)
    d.rectangle([10, 10, S - 10, 48], fill=TITLE_DARK)
    # Quick access icons (circles)
    for i, col in enumerate([(120, 120, 120), (120, 120, 120), (120, 120, 120)]):
        cx = 28 + i * 22
        d.ellipse([cx, 22, cx + 14, 36], outline=(180, 180, 180), width=1)
    # Word badge
    d.rounded_rectangle([100, 16, 122, 42], radius=3, fill=WORD_BLUE)
    d.text((111, 29), "W", font=_font_sans(12, True), fill=WHITE, anchor="mm")
    d.text(
        (130, 29),
        "02_Editorial_Resume_Template.docx  —  Word",
        font=_font_sans(13),
        fill=(230, 230, 230),
        anchor="lm",
    )
    # Caption buttons
    for i, sym in enumerate(["—", "□", "×"]):
        cx = S - 30 - (2 - i) * 40
        if sym == "×":
            d.rectangle([cx - 18, 10, cx + 18, 48], fill=(196, 43, 28))
        d.text((cx, 29), sym, font=_font_sans(13), fill=WHITE, anchor="mm")

    # Tab row (soft green-grey like real Word)
    d.rectangle([10, 48, S - 10, 82], fill=TAB_BG)
    tabs = [
        ("File", False),
        ("Home", True),
        ("Insert", False),
        ("Design", False),
        ("Layout", False),
        ("References", False),
        ("Review", False),
        ("View", False),
        ("Help", False),
    ]
    x = 28
    for lab, on in tabs:
        tw = d.textlength(lab, font=_font_sans(12))
        if on:
            d.rectangle([x - 8, 76, x + tw + 8, 82], fill=WORD_BLUE)
            d.text((x, 60), lab, font=_font_sans(12, True), fill=WORD_BLUE)
        else:
            d.text((x, 60), lab, font=_font_sans(12), fill=(70, 70, 70))
        x += int(tw + 22)
    # Share / comments
    d.rounded_rectangle([S - 200, 54, S - 120, 76], radius=4, fill=WHITE, outline=LINE)
    d.text((S - 160, 65), "Share", font=_font_sans(11), fill=INK, anchor="mm")
    d.rounded_rectangle([S - 110, 54, S - 28, 76], radius=4, fill=WHITE, outline=LINE)
    d.text((S - 69, 65), "Comments", font=_font_sans(11), fill=INK, anchor="mm")

    # Ribbon body
    d.rectangle([10, 82, S - 10, 168], fill=RIBBON)
    d.line([(10, 168), (S - 10, 168)], fill=LINE, width=1)

    f11 = _font_sans(11)
    f10 = _font_sans(10)
    f9 = _font_sans(9)

    # --- Font group ---
    gx = 22
    d.rounded_rectangle([gx, 90, gx + 210, 160], radius=3, fill=(250, 249, 248), outline=LINE)
    # font name + size
    d.rounded_rectangle([gx + 8, 96, gx + 120, 116], radius=2, fill=WHITE, outline=LINE)
    d.text((gx + 14, 106), "Georgia", font=f11, fill=INK, anchor="lm")
    d.rounded_rectangle([gx + 126, 96, gx + 160, 116], radius=2, fill=WHITE, outline=LINE)
    d.text((gx + 143, 106), "24", font=f11, fill=INK, anchor="mm")
    # B I U
    for i, lab in enumerate(["B", "I", "U"]):
        _icon_btn(d, gx + 8 + i * 28, 122, 24, 22, lab, f11, active=(lab == "B"))
    d.text((gx + 105, 152), "Font", font=f9, fill=SOFT, anchor="mm")

    # --- Paragraph group ---
    gx = 242
    d.rounded_rectangle([gx, 90, gx + 150, 160], radius=3, fill=(250, 249, 248), outline=LINE)
    for i, lab in enumerate(["≡", "•", "1.", "↔"]):
        _icon_btn(d, gx + 10 + i * 32, 110, 28, 28, lab, f11)
    d.text((gx + 75, 152), "Paragraph", font=f9, fill=SOFT, anchor="mm")

    # --- Styles group ---
    gx = 402
    d.rounded_rectangle([gx, 90, gx + 220, 160], radius=3, fill=(250, 249, 248), outline=LINE)
    d.rounded_rectangle([gx + 8, 100, gx + 78, 140], radius=3, fill=WHITE, outline=WORD_BLUE, width=2)
    d.text((gx + 43, 120), "Normal", font=f10, fill=INK, anchor="mm")
    d.rounded_rectangle([gx + 86, 100, gx + 156, 140], radius=3, fill=WHITE, outline=LINE)
    d.text((gx + 121, 120), "Title", font=f10, fill=WORD_BLUE, anchor="mm")
    d.rounded_rectangle([gx + 164, 100, gx + 210, 140], radius=3, fill=WHITE, outline=LINE)
    d.text((gx + 187, 120), "H1", font=f10, fill=INK, anchor="mm")
    d.text((gx + 110, 152), "Styles", font=f9, fill=SOFT, anchor="mm")

    # --- Editing ---
    gx = 632
    d.rounded_rectangle([gx, 90, gx + 120, 160], radius=3, fill=(250, 249, 248), outline=LINE)
    _icon_btn(d, gx + 12, 105, 96, 32, "Find", f11)
    d.text((gx + 60, 152), "Editing", font=f9, fill=SOFT, anchor="mm")

    # --- Voice / Editor chips ---
    gx = 762
    d.rounded_rectangle([gx, 90, gx + 140, 160], radius=3, fill=(250, 249, 248), outline=LINE)
    _icon_btn(d, gx + 10, 100, 55, 40, "Dict", f10)
    _icon_btn(d, gx + 72, 100, 55, 40, "Editor", f10)
    d.text((gx + 70, 152), "Voice", font=f9, fill=SOFT, anchor="mm")

    # Status bar (bottom)
    d.rectangle([10, S - 48, S - 10, S - 10], fill=STATUS)
    d.rectangle([10, S - 48, S - 10, S - 46], fill=WORD_BLUE)
    d.text(
        (28, S - 29),
        "Page 1 of 1    ·    English (United States)    ·    Accessibility: Good",
        font=_font_sans(11),
        fill=SOFT,
        anchor="lm",
    )
    d.rounded_rectangle([S - 170, S - 40, S - 28, S - 18], radius=3, fill=WHITE, outline=LINE)
    d.text((S - 99, S - 29), f"−  {zoom_pct}%  +", font=_font_sans(11), fill=INK, anchor="mm")


# ── Full Editorial draft page ────────────────────────────────────────────────

def _section_head(d, x, y, x1, title):
    d.text((x, y), title, font=_font_sans(11, True), fill=NAVY)
    y += 15
    d.line([(x, y), (x1, y)], fill=GOLD, width=1)
    return y + 10


def _draw_document(base: Image.Image, fields: dict, selection_key=None, caret_key=None):
    """Complete resume draft layout (matches Editorial template structure)."""
    d = ImageDraw.Draw(base)
    x0, y0, x1, y1 = PAGE

    # Desk + page
    d.rectangle([10, 168, S - 10, S - 48], fill=DESK)
    d.rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], fill=(50, 50, 55))
    d.rectangle([x0, y0, x1, y1], fill=CREAM, outline=(200, 196, 190))

    # Soft page corners (gold L)
    for ox, oy, sx, sy in [
        (x0 + 16, y0 + 14, 1, 1),
        (x1 - 16, y0 + 14, -1, 1),
        (x0 + 16, y1 - 14, 1, -1),
        (x1 - 16, y1 - 14, -1, -1),
    ]:
        d.line([(ox, oy), (ox + sx * 16, oy)], fill=GOLD, width=2)
        d.line([(ox, oy), (ox, oy + sy * 16)], fill=GOLD, width=2)

    cx = (x0 + x1) // 2
    left = x0 + 40
    right = x1 - 40
    coords = {}
    y = y0 + 28

    def place(key, text, font, fill, y_pos, center=False, max_w=None):
        txt = text or " "
        bb = d.textbbox((0, 0), txt, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if max_w and tw > max_w:
            # simple truncate with ellipsis for layout safety
            while tw > max_w and len(txt) > 4:
                txt = txt[:-2]
                bb = d.textbbox((0, 0), txt + "…", font=font)
                tw = bb[2] - bb[0]
            txt = txt + "…"
            bb = d.textbbox((0, 0), txt, font=font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = cx - tw // 2 if center else left
        if selection_key == key:
            d.rectangle([tx - 4, y_pos - 2, tx + tw + 4, y_pos + th + 3], fill=SELECT)
        d.text((tx, y_pos), txt, font=font, fill=fill)
        if caret_key == key:
            d.rectangle([tx + tw + 1, y_pos - 1, tx + tw + 3, y_pos + th + 1], fill=INK)
        coords[key] = (tx + tw // 2, y_pos + th // 2, tx, y_pos, tw, th)
        return th

    # Header
    place("name", fields["name"], _font(28, True), NAVY, y, center=True)
    y += 34
    d.text((cx, y), "·   ·   ·", font=_font(11), fill=GOLD, anchor="mt")
    y += 20
    place("role", fields["role"], _font(13), GOLD, y, center=True)
    y += 20
    place("contact", fields["contact"], _font_sans(10), SOFT, y, center=True, max_w=right - left)
    y += 22
    d.line([(left, y), (right, y)], fill=GOLD, width=1)
    y += 14

    # PROFESSIONAL SUMMARY
    y = _section_head(d, left, y, right, "PROFESSIONAL SUMMARY")
    place("summary", fields["summary"], _font_sans(11), INK, y, center=False, max_w=right - left)
    y += 22

    # CORE SKILLS
    y = _section_head(d, left, y, right, "CORE SKILLS")
    place("skills", fields["skills"], _font_sans(11), INK, y, center=False, max_w=right - left)
    y += 22

    # EXPERIENCE
    y = _section_head(d, left, y, right, "EXPERIENCE")
    place("job", fields["job"], _font(13, True), NAVY, y, center=False)
    # dates on the right
    d.text((right, y), "YYYY – Present", font=_font_sans(10), fill=MUTED, anchor="rt")
    y += 20
    place("company", fields["company"], _font_sans(11), TEAL, y, center=False)
    y += 18
    place("bullet1", "•  " + fields["bullet1"], _font_sans(11), INK, y, center=False, max_w=right - left - 8)
    y += 17
    place("bullet2", "•  " + fields["bullet2"], _font_sans(11), INK, y, center=False, max_w=right - left - 8)
    y += 22

    # EDUCATION
    y = _section_head(d, left, y, right, "EDUCATION")
    place("degree", fields["degree"], _font(12, True), NAVY, y, center=False)
    d.text((right, y), "YYYY", font=_font_sans(10), fill=MUTED, anchor="rt")
    y += 18
    place("school", fields["school"], _font_sans(11), SOFT, y, center=False)
    y += 22

    # SELECTED WORK
    y = _section_head(d, left, y, right, "SELECTED WORK")
    place("work", "•  " + fields["work"], _font_sans(11), INK, y, center=False, max_w=right - left - 8)

    d.text(
        (cx, y1 - 18),
        "·  MathRelaxing Editorial  ·",
        font=_font_sans(9),
        fill=(175, 170, 160),
        anchor="mm",
    )
    return coords


# ── Timeline: show full draft, then edit key fields ──────────────────────────

def _timeline():
    def f(sec):
        return int(sec * FPS)

    # Hold complete blank draft first, then progressive edits
    return [
        ("idle", f(0.0), f(2.2)),  # full draft overview
        ("move", f(2.2), f(2.85), "name"),
        ("click", f(2.85), f(3.15), "name"),
        ("type", f(3.15), f(4.6), "name"),
        ("move", f(4.6), f(5.15), "role"),
        ("click", f(5.15), f(5.4), "role"),
        ("type", f(5.4), f(6.9), "role"),
        ("move", f(6.9), f(7.4), "contact"),
        ("click", f(7.4), f(7.65), "contact"),
        ("type", f(7.65), f(9.4), "contact"),
        ("move", f(9.4), f(10.0), "job"),
        ("click", f(10.0), f(10.25), "job"),
        ("type", f(10.25), f(11.5), "job"),
        ("move", f(11.5), f(12.0), "company"),
        ("click", f(12.0), f(12.25), "company"),
        ("type", f(12.25), f(13.6), "company"),
        ("move", f(13.6), f(14.1), "bullet1"),
        ("click", f(14.1), f(14.35), "bullet1"),
        ("type", f(14.35), f(15.9), "bullet1"),
        ("move", f(15.9), f(16.4), "degree"),
        ("click", f(16.4), f(16.65), "degree"),
        ("type", f(16.65), f(18.0), "degree"),
        ("idle", f(18.0), f(20.0)),  # finished full view
    ]


def _phase_at(frame):
    for item in _timeline():
        kind, a, b = item[0], item[1], item[2]
        if a <= frame < b or (frame >= N - 1 and b >= N and a <= frame):
            rest = item[3:] if len(item) > 3 else ()
            t = 0.0 if b == a else (frame - a) / max(1, b - a)
            return kind, max(0.0, min(1.0, t)), rest, a, b
    return "idle", 0.0, (), 0, 1


def main():
    for d in (FRAMES, AUDIO_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(CHECK, exist_ok=True)

    probe = Image.new("RGB", (S, S), CREAM)
    coords = _draw_document(probe, dict(PLACEHOLDERS))
    targets = {k: (v[0], v[1]) for k, v in coords.items()}

    cursor = (200.0, 400.0)
    move_from = cursor
    move_key = None
    fields = dict(PLACEHOLDERS)
    typed = {k: "" for k in TYPING}
    cleared = set()

    print(f"Rendering {N} frames — full draft, no zoom, silent…")
    for frame in range(N):
        kind, t, rest, fa, fb = _phase_at(frame)
        key = rest[0] if rest else None
        clicking = False
        cursor_mode = "arrow"
        frame_select = None

        if kind == "idle":
            if frame < int(2.2 * FPS):
                cursor = _lerp((160, 520), (S / 2, 300), min(1.0, frame / (2.0 * FPS)))
            else:
                cursor = _lerp(cursor, targets.get("name", (S / 2, 250)), 0.06)
        elif kind == "move" and key:
            if move_key != key:
                move_from = cursor
                move_key = key
            cursor = _lerp(move_from, targets[key], t)
        elif kind == "click" and key:
            move_key = None
            cursor = targets[key]
            clicking = t < 0.45
            frame_select = key if t > 0.15 else None
            if t > 0.55 and key not in cleared:
                fields[key] = ""
                typed[key] = ""
                cleared.add(key)
        elif kind == "type" and key:
            move_key = None
            full = TYPING[key]
            nchars = min(len(full), max(0, int(len(full) * min(1.0, t * 1.04) + 0.02)))
            typed[key] = full[:nchars]
            fields[key] = typed[key]
            cursor_mode = "ibeam"

        for k, v in typed.items():
            if v:
                fields[k] = v

        img = Image.new("RGB", (S, S), (55, 55, 55))
        d = ImageDraw.Draw(img)
        _draw_word_chrome(d, zoom_pct=100)
        coords = _draw_document(
            img,
            fields,
            selection_key=frame_select,
            caret_key=key if kind == "type" and (frame // 10) % 2 == 0 else None,
        )
        for k, v in coords.items():
            targets[k] = (v[0], v[1])

        if kind == "type" and key and key in coords:
            tx, ty, tw, th = coords[key][2], coords[key][3], coords[key][4], coords[key][5]
            cursor = (tx + tw + 2, ty + th / 2)

        _draw_cursor(img, int(cursor[0]), int(cursor[1]), mode=cursor_mode, clicking=clicking)
        img.save(os.path.join(FRAMES, f"f_{frame:04d}.png"))
        if frame % 60 == 0:
            print(f"  frame {frame}/{N}  {kind}")

    print("Encode silent video (no zoom, no typing SFX)…")
    brand.encode_mp4(FRAMES, VIDEO_SILENT, fps=FPS, pattern="f_%04d.png", crf=17, cleanup=False)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            VIDEO_SILENT,
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "17",
            "-movflags",
            "+faststart",
            VIDEO,
        ],
        check=True,
        capture_output=True,
    )
    if os.path.isfile(VIDEO_SILENT):
        os.remove(VIDEO_SILENT)
    shutil.rmtree(FRAMES, ignore_errors=True)
    shutil.rmtree(AUDIO_DIR, ignore_errors=True)

    for ss, name in ((1.5, "c1"), (5, "c5"), (10, "c10"), (15, "c15"), (19, "c19")):
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(ss),
                "-i",
                VIDEO,
                "-frames:v",
                "1",
                os.path.join(CHECK, f"{name}.png"),
            ],
            capture_output=True,
        )

    mb = os.path.getsize(VIDEO) / (1024 * 1024)
    print(f"OK {VIDEO} ({mb:.2f} MB, {DURATION:.0f}s)")


if __name__ == "__main__":
    main()
