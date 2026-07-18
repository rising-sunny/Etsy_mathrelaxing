"""
generate_reader_os.py — Reader OS digital sticker system (iPad / GoodNotes first)
================================================================================
Premium stickers via HTML/CSS + Playwright Chromium (retina capture, Google fonts,
SVG progress rings, die-cut white borders, soft shadows).

Positioned for digital readers: iPad, GoodNotes, Notability, Procreate, Freeform,
Kindle-app journals. Optional print sheet included.

  python generate_reader_os.py
"""
from __future__ import annotations

import html
import math
import os
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
OUT = BASE / "reader_os"
STICKERS = OUT / "stickers"
SHEETS = OUT / "sheets"
PREVIEWS = OUT / "previews"
HTML_DIR = OUT / "_html"
ZIP_PATH = OUT / "MathRelaxing_Reader_OS_Stickers.zip"

# Editorial palette
NAVY = "#161f38"
NAVY_SOFT = "#304060"
CREAM = "#faf6ec"
GOLD = "#c49e48"
GOLD_LT = "#e8c56a"
INK = "#1c1e24"
SOFT = "#6e6c64"
ROSE = "#b46e6e"
SAGE = "#5a7864"
BLUE = "#466e96"
STONE = "#968c7d"
WHITE = "#ffffff"
PURPLE = "#785a8c"
CLAY = "#a0785a"
HORROR = "#502832"

S = 900  # sticker master px
SHEET_CELL = 280


def _ensure():
    for d in (OUT, STICKERS, SHEETS, PREVIEWS, HTML_DIR, STICKERS / "png"):
        d.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = (
        ["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    )
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _serif(size: int, bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


# ── Sticker catalog ───────────────────────────────────────────────────────────

def catalog() -> list[dict]:
    """Each item: slug, module, kind, label, optional sub/pct/stars/icon/colors."""
    items: list[dict] = []

    for slug, label, bg, fg, icon in [
        ("currently_reading", "Currently Reading", NAVY, CREAM, "book-open"),
        ("on_hold", "On Hold", STONE, CREAM, "pause"),
        ("dnf", "DNF", ROSE, CREAM, "x"),
        ("finished", "Finished", SAGE, CREAM, "check"),
        ("reread", "Reread", BLUE, CREAM, "refresh"),
        ("tbr", "TBR", GOLD, NAVY, "stack"),
        ("up_next", "Up Next", NAVY_SOFT, CREAM, "arrow"),
        ("book_mail", "Book Mail", ROSE, CREAM, "mail"),
    ]:
        items.append(
            {
                "slug": f"status_{slug}",
                "module": "status",
                "kind": "pill",
                "label": label,
                "bg": bg,
                "fg": fg,
                "ring": GOLD if bg in (NAVY, NAVY_SOFT) else None,
                "icon": icon,
            }
        )

    for pct in (10, 25, 50, 75, 90, 100):
        items.append(
            {
                "slug": f"progress_{pct}",
                "module": "progress",
                "kind": "ring",
                "label": f"{pct}%",
                "sub": "DONE",
                "pct": pct,
                "bg": CREAM,
                "fg": NAVY,
                "accent": GOLD,
            }
        )
    for slug, label, bg, fg in [
        ("last_chapter", "Last Chapter", NAVY, CREAM),
        ("cliffhanger", "Cliffhanger", ROSE, CREAM),
    ]:
        items.append(
            {
                "slug": f"progress_{slug}",
                "module": "progress",
                "kind": "card",
                "label": label,
                "bg": bg,
                "fg": fg,
                "filled": True,
            }
        )

    for n, lab in [(1, "Nope"), (2, "Mid"), (3, "Solid"), (4, "Loved"), (5, "No notes")]:
        items.append(
            {
                "slug": f"rating_{n}star",
                "module": "rating",
                "kind": "stars",
                "label": lab,
                "stars": n,
                "bg": CREAM,
                "fg": NAVY,
                "accent": GOLD,
            }
        )
    items.append(
        {
            "slug": "rating_life_changing",
            "module": "rating",
            "kind": "hex",
            "label": "Life Changing",
            "bg": GOLD,
            "fg": NAVY,
        }
    )

    for slug, label, accent in [
        ("fantasy", "Fantasy", NAVY_SOFT),
        ("romance", "Romance", ROSE),
        ("thriller", "Thriller", INK),
        ("sci_fi", "Sci-Fi", BLUE),
        ("litfic", "Litfic", SAGE),
        ("memoir", "Memoir", GOLD),
        ("mystery", "Mystery", NAVY),
        ("horror", "Horror", HORROR),
        ("nonfiction", "Nonfiction", STONE),
        ("ya", "YA", PURPLE),
    ]:
        items.append(
            {
                "slug": f"genre_{slug}",
                "module": "genre",
                "kind": "outline_pill",
                "label": label,
                "bg": CREAM,
                "fg": accent,
                "ring": accent,
            }
        )

    for slug, label, fg in [
        ("plot_twist", "Plot Twist", GOLD),
        ("foreshadowing", "Foreshadowing", BLUE),
        ("unreliable", "Unreliable Narrator", ROSE),
        ("trope_unlocked", "Trope Unlocked", NAVY),
        ("character_arc", "Character Arc", SAGE),
        ("worldbuilding", "Worldbuilding", NAVY_SOFT),
        ("quotable", "Quotable", GOLD),
        ("tearjerker", "Tearjerker", ROSE),
        ("highlight", "Highlight", GOLD),
        ("bookmark", "Bookmark", BLUE),
    ]:
        items.append(
            {
                "slug": f"note_{slug}",
                "module": "annotation",
                "kind": "card",
                "label": label,
                "bg": CREAM,
                "fg": fg,
                "ring": NAVY,
            }
        )

    for slug, label, bg in [
        ("cozy", "Cozy", SAGE),
        ("spicy", "Spicy", ROSE),
        ("dark_academia", "Dark Academia", NAVY),
        ("mind_blown", "Mind Blown", GOLD),
        ("comfort_reread", "Comfort Reread", BLUE),
        ("slow_burn", "Slow Burn", CLAY),
    ]:
        items.append(
            {
                "slug": f"mood_{slug}",
                "module": "mood",
                "kind": "circle",
                "label": label,
                "bg": bg,
                "fg": CREAM if bg != GOLD else NAVY,
            }
        )

    for slug, title, sub in [
        ("page_tracker", "Page tracker", "mark your place"),
        ("quote_capture", "Quote capture", "save a line"),
        ("book_club", "Book club", "discuss tonight"),
        ("library_haul", "Library haul", "borrowed joy"),
        ("bookstore_find", "Bookstore find", "new treasure"),
        ("series_catchup", "Series catch-up", "next volume"),
        ("ipad_session", "iPad session", "GoodNotes ready"),
        ("digital_shelf", "Digital shelf", "e-library pick"),
        ("goodnotes_log", "GoodNotes log", "tap to stamp"),
        ("ereader_night", "E-reader night", "lights low"),
    ]:
        items.append(
            {
                "slug": f"chip_{slug}",
                "module": "chips",
                "kind": "chip",
                "label": title,
                "sub": sub,
                "bg": CREAM,
                "fg": NAVY,
                "accent": GOLD,
            }
        )

    for slug, label, bg in [
        ("book_currently", "NOW", NAVY),
        ("book_finished", "DONE", SAGE),
        ("book_tbr", "TBR", GOLD),
    ]:
        items.append(
            {
                "slug": f"icon_{slug}",
                "module": "icons",
                "kind": "book",
                "label": label,
                "bg": bg,
                "fg": CREAM if bg != GOLD else NAVY,
            }
        )

    return items


# ── SVG micro-icons (inline, no external deps) ────────────────────────────────

ICONS = {
    "book-open": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H2z"/><path d="M22 4h-7a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h8z"/></svg>""",
    "pause": """<svg class="ico" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>""",
    "x": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>""",
    "check": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5L19 7"/></svg>""",
    "refresh": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.6-6.3"/><path d="M21 3v6h-6"/></svg>""",
    "stack": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7l8-4 8 4-8 4-8-4z"/><path d="M4 12l8 4 8-4"/><path d="M4 17l8 4 8-4"/></svg>""",
    "arrow": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>""",
    "mail": """<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 7 9-7"/></svg>""",
}


# ── HTML sticker templates ────────────────────────────────────────────────────

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500;9..40,700;9..40,800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {S}px; height: {S}px;
  background: transparent !important;
  overflow: hidden;
  font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}
.stage {{
  width: {S}px; height: {S}px;
  display: flex; align-items: center; justify-content: center;
  background: transparent;
}}

/* Die-cut sticker shell: white border + soft depth */
.shell {{
  position: relative;
  filter:
    drop-shadow(0 1px 0 rgba(255,255,255,0.9))
    drop-shadow(0 14px 28px rgba(22,31,56,0.22))
    drop-shadow(0 4px 8px rgba(22,31,56,0.12));
}}
.shell::before {{
  content: '';
  position: absolute;
  inset: -16px;
  border-radius: inherit;
  background: #fff;
  z-index: -1;
  box-shadow: 0 0 0 3px rgba(255,255,255,0.95);
}}

.pill {{
  position: relative;
  padding: 34px 58px 34px 52px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 48px;
  letter-spacing: 0.035em;
  text-transform: uppercase;
  line-height: 1.12;
  text-align: center;
  max-width: 780px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  box-shadow:
    0 0 0 14px #fff,
    0 18px 40px rgba(22,31,56,0.18),
    inset 0 2px 0 rgba(255,255,255,0.22);
}}
.pill .ico {{ width: 42px; height: 42px; flex-shrink: 0; opacity: 0.92; }}
.pill .txt {{ text-align: left; }}

.outline-pill {{
  padding: 30px 54px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 50px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 7px solid;
  background: linear-gradient(180deg, #fffef9 0%, {CREAM} 100%);
  box-shadow:
    0 0 0 14px #fff,
    0 14px 32px rgba(22,31,56,0.12);
  position: relative;
}}
.outline-pill::after {{
  content: '';
  position: absolute;
  left: 28px; right: 28px; top: 12px; height: 40%;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(255,255,255,0.55), transparent);
  pointer-events: none;
}}

.card {{
  width: 700px;
  min-height: 300px;
  padding: 44px 40px;
  border-radius: 44px;
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  font-weight: 800;
  font-size: 48px;
  line-height: 1.18;
  letter-spacing: 0.015em;
  border: 6px solid {NAVY};
  box-shadow:
    0 0 0 14px #fff,
    0 20px 44px rgba(22,31,56,0.16);
  background: linear-gradient(165deg, #fffef9 0%, {CREAM} 55%, #f3ebe0 100%);
  position: relative;
}}
.card.filled {{
  border: none;
  box-shadow:
    0 0 0 14px #fff,
    0 20px 44px rgba(22,31,56,0.2),
    inset 0 2px 0 rgba(255,255,255,0.2);
}}
.card .accent-bar {{
  position: absolute;
  left: 0; top: 28px; bottom: 28px;
  width: 14px;
  border-radius: 0 8px 8px 0;
  background: linear-gradient(180deg, {GOLD_LT}, {GOLD});
}}

.circle {{
  width: 620px; height: 620px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  font-weight: 800;
  font-size: 46px;
  line-height: 1.18;
  padding: 56px;
  box-shadow:
    0 0 0 16px #fff,
    0 22px 50px rgba(22,31,56,0.22),
    inset 0 3px 0 rgba(255,255,255,0.22),
    inset 0 -8px 20px rgba(0,0,0,0.08);
  border: 6px solid rgba(255,255,255,0.2);
  position: relative;
}}
.circle::after {{
  content: '';
  position: absolute;
  inset: 28px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.12);
  pointer-events: none;
}}

.hex {{
  width: 600px; height: 520px;
  clip-path: polygon(25% 6%, 75% 6%, 100% 50%, 75% 94%, 25% 94%, 0% 50%);
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 700;
  font-size: 46px;
  line-height: 1.12;
  padding: 60px 80px;
  filter: drop-shadow(0 0 0 12px #fff) drop-shadow(0 18px 28px rgba(22,31,56,0.22));
}}

.ring {{
  width: 680px; height: 680px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 32% 28%, #fffefb 0%, {CREAM} 52%, #efe6d6 100%);
  box-shadow:
    0 0 0 16px #fff,
    0 22px 48px rgba(22,31,56,0.16),
    inset 0 2px 0 rgba(255,255,255,0.8);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  position: relative;
}}
.ring .track {{
  position: absolute;
  inset: 52px;
  width: calc(100% - 104px);
  height: calc(100% - 104px);
}}
.ring .pct {{
  position: relative; z-index: 2;
  font-weight: 800; font-size: 108px; color: {NAVY};
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  line-height: 1;
}}
.ring .sub {{
  position: relative; z-index: 2;
  font-weight: 700; font-size: 26px; letter-spacing: 0.22em;
  color: {SOFT}; margin-top: 8px;
}}

.stars-card {{
  width: 740px; min-height: 360px;
  border-radius: 48px;
  background: linear-gradient(165deg, #fffef9, {CREAM});
  border: 6px solid {NAVY};
  box-shadow:
    0 0 0 14px #fff,
    0 20px 44px rgba(22,31,56,0.15);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 22px; padding: 44px 36px;
}}
.stars {{ display: flex; gap: 12px; align-items: center; }}
.star {{
  width: 72px; height: 72px;
}}
.star.on path {{
  fill: url(#goldGrad);
  filter: drop-shadow(0 3px 6px rgba(196,158,72,0.45));
}}
.star.off path {{
  fill: #e0d6c4;
}}
.stars-card .lab {{
  font-weight: 800; font-size: 34px; color: {NAVY}; letter-spacing: 0.05em;
  text-transform: uppercase;
}}

.chip {{
  width: 740px; min-height: 260px;
  border-radius: 40px;
  background: linear-gradient(135deg, #fffef9, {CREAM});
  border: 5px solid {NAVY};
  box-shadow:
    0 0 0 14px #fff,
    0 18px 40px rgba(22,31,56,0.14);
  display: flex; align-items: stretch; overflow: hidden;
}}
.chip .bar {{
  width: 26px;
  background: linear-gradient(180deg, {GOLD_LT}, {GOLD} 60%, #a88430);
}}
.chip .body {{
  flex: 1; padding: 40px 44px;
  display: flex; flex-direction: column; justify-content: center; gap: 8px;
}}
.chip .title {{ font-weight: 800; font-size: 46px; color: {NAVY}; letter-spacing: -0.01em; }}
.chip .sub {{ font-weight: 500; font-size: 28px; color: {SOFT}; }}

.book {{
  width: 400px; height: 560px;
  border-radius: 16px 26px 26px 16px;
  position: relative;
  box-shadow:
    0 0 0 12px #fff,
    0 22px 40px rgba(22,31,56,0.22);
  border: 4px solid {NAVY};
  overflow: hidden;
}}
.book .spine {{
  position: absolute; left: 0; top: 0; bottom: 0; width: 44px;
  background: linear-gradient(90deg, #0a0e18, {NAVY} 70%, #243050);
  border-radius: 12px 0 0 12px;
}}
.book .pages {{
  position: absolute; right: 8px; top: 16px; bottom: 16px; width: 12px;
  background: repeating-linear-gradient(180deg, {CREAM} 0 3px, #e8dfd0 3px 4px);
  border-radius: 2px;
  box-shadow: -2px 0 4px rgba(0,0,0,0.06);
}}
.book .band {{
  position: absolute; left: 64px; right: 36px; top: 42%;
  background: linear-gradient(180deg, #fffef9, {CREAM});
  border-radius: 12px;
  padding: 20px 14px;
  text-align: center;
  font-weight: 800; font-size: 40px; letter-spacing: 0.1em;
  color: {NAVY};
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}
.book .shine {{
  position: absolute; left: 50px; top: 0; bottom: 0; width: 40%;
  background: linear-gradient(90deg, rgba(255,255,255,0.12), transparent);
  pointer-events: none;
}}
"""


def sticker_html(item: dict) -> str:
    kind = item["kind"]
    label = html.escape(item["label"])
    bg = item.get("bg", CREAM)
    fg = item.get("fg", NAVY)
    ring = item.get("ring")
    accent = item.get("accent", GOLD)
    icon_key = item.get("icon")
    icon_svg = ICONS.get(icon_key, "") if icon_key else ""

    # Shared SVG defs for gold stars
    defs = f"""
    <svg width="0" height="0" style="position:absolute">
      <defs>
        <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{GOLD_LT}"/>
          <stop offset="100%" stop-color="{GOLD}"/>
        </linearGradient>
      </defs>
    </svg>"""

    if kind == "pill":
        style = f"background:linear-gradient(165deg, {bg}f0 0%, {bg} 55%, {bg}ee 100%); color:{fg};"
        if ring:
            style += f" box-shadow: 0 0 0 14px #fff, 0 0 0 19px {ring}, 0 18px 40px rgba(22,31,56,0.18), inset 0 2px 0 rgba(255,255,255,0.22);"
        # multiline for long labels
        words = item["label"].upper().split()
        if len(words) >= 2 and len(item["label"]) > 10:
            mid = max(1, len(words) // 2)
            line1 = html.escape(" ".join(words[:mid]))
            line2 = html.escape(" ".join(words[mid:]))
            txt = f'<div class="txt">{line1}<br>{line2}</div>'
        else:
            txt = f'<div class="txt">{html.escape(item["label"].upper())}</div>'
        inner = f'<div class="pill" style="{style}">{icon_svg}{txt}</div>'

    elif kind == "outline_pill":
        inner = (
            f'<div class="outline-pill" style="color:{fg}; border-color:{ring or fg};">'
            f"{html.escape(item['label'].upper())}</div>"
        )

    elif kind == "card":
        filled = item.get("filled")
        if filled:
            style = (
                f"background:linear-gradient(165deg, {bg}ee, {bg}); color:{fg};"
            )
            cls = "card filled"
            bar = ""
        else:
            style = f"color:{fg}; border-color:{item.get('ring', NAVY)};"
            cls = "card"
            bar = f'<div class="accent-bar" style="background:linear-gradient(180deg,{GOLD_LT},{fg});"></div>'
        inner = f'<div class="{cls}" style="{style}">{bar}<span>{label}</span></div>'

    elif kind == "circle":
        style = (
            f"background:radial-gradient(circle at 30% 25%, {bg}dd, {bg} 60%, {bg}ee);"
            f" color:{fg};"
        )
        inner = f'<div class="circle" style="{style}">{label}</div>'

    elif kind == "hex":
        style = f"background:linear-gradient(160deg, {GOLD_LT}, {bg}); color:{fg};"
        inner = f'<div class="hex" style="{style}">{label}</div>'

    elif kind == "ring":
        pct = item.get("pct", 0)
        r = 40
        c = 2 * math.pi * r
        dash = c * pct / 100
        gap = c - dash
        sub = html.escape(item.get("sub", "DONE"))
        # glow stroke for completed feel
        glow = f'filter="url(#glow)"' if pct >= 100 else ""
        inner = f"""
        <div class="ring">
          <svg class="track" viewBox="0 0 100 100">
            <defs>
              <linearGradient id="ringGold" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="{GOLD_LT}"/>
                <stop offset="100%" stop-color="{accent}"/>
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="1.2" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
            </defs>
            <circle cx="50" cy="50" r="{r}" fill="none" stroke="#e5dccb" stroke-width="7.5"/>
            <circle cx="50" cy="50" r="{r}" fill="none" stroke="url(#ringGold)" stroke-width="7.5"
              stroke-linecap="round"
              stroke-dasharray="{dash:.3f} {gap:.3f}"
              transform="rotate(-90 50 50)" {glow}/>
          </svg>
          <div class="pct">{label}</div>
          <div class="sub">{sub}</div>
        </div>"""

    elif kind == "stars":
        n = item.get("stars", 0)
        star_path = "M12 2.2l2.9 6.1 6.7.9-4.9 4.6 1.2 6.6L12 17.2 6.1 20.4l1.2-6.6L2.4 9.2l6.7-.9L12 2.2z"
        stars = "".join(
            f'<svg class="star {"on" if i < n else "off"}" viewBox="0 0 24 24">'
            f'<path d="{star_path}"/></svg>'
            for i in range(5)
        )
        lab = html.escape(item.get("label", f"{n}/5"))
        inner = (
            f'<div class="stars-card"><div class="stars">{stars}</div>'
            f'<div class="lab">{lab}</div></div>'
        )

    elif kind == "chip":
        sub = html.escape(item.get("sub", ""))
        inner = f"""
        <div class="chip">
          <div class="bar"></div>
          <div class="body">
            <div class="title">{label}</div>
            <div class="sub">{sub}</div>
          </div>
        </div>"""

    elif kind == "book":
        inner = f"""
        <div class="book" style="background:linear-gradient(145deg, {bg}ee, {bg});">
          <div class="spine"></div>
          <div class="shine"></div>
          <div class="pages"></div>
          <div class="band" style="color:{item.get("fg", NAVY)};">{label}</div>
        </div>"""
    else:
        inner = f'<div class="pill" style="background:{bg};color:{fg};">{label}</div>'

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
{defs}
<div class="stage">{inner}</div>
</body></html>"""


def render_all_stickers(items: list[dict]) -> list[tuple[str, str, Path]]:
    """Render each sticker via Chromium; return (filename, module, path)."""
    _ensure()
    out_paths: list[tuple[str, str, Path]] = []
    png_dir = STICKERS / "png"
    if png_dir.exists():
        shutil.rmtree(png_dir)
    by_mod_root = STICKERS / "by_module"
    if by_mod_root.exists():
        shutil.rmtree(by_mod_root)
    png_dir.mkdir(parents=True)

    print(f"=== Rendering {len(items)} stickers (Playwright HTML/CSS retina) ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": S, "height": S},
            device_scale_factor=2,  # 1800px capture → downscale to 900 crisp
        )
        # Preload fonts once
        warm = HTML_DIR / "_warmup.html"
        warm.write_text(
            f"<!DOCTYPE html><html><head><style>{CSS}</style></head>"
            f"<body><div class='stage'><div class='pill' style='background:{NAVY};color:{CREAM}'>"
            f"WARM</div></div></body></html>",
            encoding="utf-8",
        )
        page.goto(warm.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(600)

        for i, item in enumerate(items):
            fname = f"{item['slug']}.png"
            html_path = HTML_DIR / f"{item['slug']}.html"
            html_path.write_text(sticker_html(item), encoding="utf-8")
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.wait_for_timeout(60)
            raw = HTML_DIR / f"{item['slug']}_raw.png"
            page.screenshot(path=str(raw), omit_background=True)
            im = Image.open(raw).convert("RGBA")
            if im.size != (S, S):
                im = im.resize((S, S), Image.Resampling.LANCZOS)
            dest = png_dir / fname
            im.save(dest, "PNG", optimize=True)
            mod_dir = STICKERS / "by_module" / item["module"]
            mod_dir.mkdir(parents=True, exist_ok=True)
            im.save(mod_dir / fname, "PNG", optimize=True)
            out_paths.append((fname, item["module"], dest))
            if i % 10 == 0 or i + 1 == len(items):
                print(f"  {i+1}/{len(items)} {fname}")
        browser.close()
    print(f"  done {len(out_paths)} stickers")
    return out_paths


def make_sheet(paths: list[tuple[str, str, Path]]) -> Image.Image:
    cols = 6
    rows = math.ceil(len(paths) / cols)
    cell = SHEET_CELL
    margin, gap, header = 60, 22, 140
    W = margin * 2 + cols * cell + (cols - 1) * gap
    H = margin * 2 + header + rows * cell + (rows - 1) * gap + 70
    img = Image.new("RGB", (W, H), (250, 246, 236))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=(22, 32, 56))
    d.text(
        (W // 2, 32),
        "READER OS  ·  DIGITAL STICKER SYSTEM",
        font=_serif(32, True),
        fill=(250, 246, 236),
        anchor="mt",
    )
    d.text(
        (W // 2, 78),
        "iPad · GoodNotes · Notability · Procreate · Kindle apps",
        font=_font(18),
        fill=(196, 158, 72),
        anchor="mt",
    )

    for i, (fname, _mod, path) in enumerate(paths):
        c, r = i % cols, i // cols
        x = margin + c * (cell + gap)
        y = margin + header + r * (cell + gap)
        for yy in range(0, cell, 14):
            for xx in range(0, cell, 14):
                col = (238, 232, 220) if (xx // 14 + yy // 14) % 2 == 0 else (250, 246, 236)
                d.rectangle([x + xx, y + yy, x + xx + 14, y + yy + 14], fill=col)
        im = Image.open(path).convert("RGBA").resize((cell - 8, cell - 8), Image.Resampling.LANCZOS)
        img.paste(im, (x + 4, y + 4), im)
        d.rectangle([x, y, x + cell, y + cell], outline=(22, 32, 56), width=2)

    d.rectangle([0, H - 56, W, H], fill=(22, 32, 56))
    d.text(
        (W // 2, H - 28),
        f"{len(paths)} PNG stickers  ·  transparent  ·  built for iPad digital readers",
        font=_font(16),
        fill=(250, 246, 236),
        anchor="mm",
    )
    return img


def make_previews(paths: list[tuple[str, str, Path]], sheet: Image.Image):
    print("=== Previews (iPad digital reader) ===")
    H = 1600
    imgs = [(m, Image.open(p).convert("RGBA")) for _, m, p in paths]

    def pick(*indices):
        out = []
        for idx in indices:
            if 0 <= idx < len(imgs):
                out.append(imgs[idx][1])
        return out

    # 1 hero
    hero = Image.new("RGB", (H, H), (22, 32, 56))
    d = ImageDraw.Draw(hero)
    d.text((H // 2, 55), "READER OS", font=_serif(72, True), fill=(250, 246, 236), anchor="mt")
    d.text(
        (H // 2, 140),
        "Digital sticker system for iPad readers",
        font=_font(28),
        fill=(196, 158, 72),
        anchor="mt",
    )
    d.rectangle([H // 2 - 70, 185, H // 2 + 70, 191], fill=(196, 158, 72))
    picks = [0, 3, 5, 10, 14, 20, 28, 36, 42, 48, min(52, len(imgs) - 1), 8]
    pos = [
        (90, 250), (410, 230), (750, 260), (1090, 240),
        (160, 540), (500, 520), (880, 540),
        (120, 880), (480, 900), (840, 860), (1160, 920), (680, 320),
    ]
    for idx, (px, py) in zip(picks, pos):
        if idx >= len(imgs):
            continue
        thumb = imgs[idx][1].resize((300, 300), Image.Resampling.LANCZOS)
        hero.paste(thumb, (px, py), thumb)
    d.rectangle([0, H - 120, H, H], fill=(10, 14, 24))
    d.text(
        (H // 2, H - 78),
        "GoodNotes · Notability · Procreate · Freeform · Kindle app journals",
        font=_font(20),
        fill=(250, 246, 236),
        anchor="mt",
    )
    d.text(
        (H // 2, H - 40),
        "Status · Progress · Rating · Genre · Notes · Mood",
        font=_font(18),
        fill=(196, 158, 72),
        anchor="mt",
    )
    hero.save(PREVIEWS / "reader_os_preview_1_hero.jpg", quality=93)
    print("  reader_os_preview_1_hero.jpg")

    # 2 iPad mockup
    ipad = Image.new("RGB", (H, H), (210, 208, 202))
    d = ImageDraw.Draw(ipad)
    for y in range(H):
        t = y / H
        d.line([(0, y), (H, y)], fill=(int(215 - 10 * t), int(212 - 8 * t), int(205 - 6 * t)))
    # tablet frame
    d.rounded_rectangle([250, 100, 1350, 1400], radius=52, fill=(28, 28, 32), outline=(12, 12, 14), width=4)
    d.rounded_rectangle([290, 150, 1310, 1300], radius=10, fill=(250, 246, 236))
    d.rectangle([290, 150, 1310, 210], fill=(22, 32, 56))
    d.text((800, 180), "GoodNotes  ·  Reading Log", font=_font(22, True), fill=(250, 246, 236), anchor="mm")
    for y in range(270, 1220, 44):
        d.line([(350, y), (1250, y)], fill=(230, 222, 208), width=2)
    d.text((800, 250), "June reading list", font=_serif(32, True), fill=(22, 32, 56), anchor="mt")
    # camera notch hint
    d.ellipse([780, 118, 820, 140], fill=(18, 18, 20))
    stickers_for_ipad = pick(0, 5, 10, 18, 30, 40, min(50, len(imgs) - 1), 8)
    coords = [
        (360, 330, 0.30), (700, 310, 0.28), (1000, 340, 0.27),
        (400, 660, 0.30), (780, 680, 0.28), (520, 980, 0.26),
        (900, 980, 0.26), (1100, 700, 0.24),
    ]
    for im, (px, py, sc) in zip(stickers_for_ipad, coords):
        tw = int(S * sc)
        thumb = im.resize((tw, tw), Image.Resampling.LANCZOS)
        ipad.paste(thumb, (px, py), thumb)
    d.rounded_rectangle([700, 1330, 900, 1348], radius=6, fill=(80, 80, 85))
    d.rectangle([0, H - 90, H, H], fill=(22, 32, 56))
    d.text(
        (H // 2, H - 45),
        "Made for iPad · drag & drop into GoodNotes / Notability",
        font=_font(20),
        fill=(196, 158, 72),
        anchor="mm",
    )
    ipad.save(PREVIEWS / "reader_os_preview_2_ipad.jpg", quality=93)
    print("  reader_os_preview_2_ipad.jpg")

    # 3 modules
    by_mod: dict[str, list] = {}
    for fname, mod, path in paths:
        by_mod.setdefault(mod, []).append(Image.open(path).convert("RGBA"))
    grid = Image.new("RGB", (H, H), (250, 246, 236))
    d = ImageDraw.Draw(grid)
    d.rectangle([0, 0, H, 150], fill=(22, 32, 56))
    d.text((H // 2, 45), "SIX MODULES  ·  ONE SYSTEM", font=_serif(36, True), fill=(250, 246, 236), anchor="mt")
    d.text((H // 2, 100), "Built for digital reading journals on iPad", font=_font(22), fill=(196, 158, 72), anchor="mt")
    order = ["status", "progress", "rating", "genre", "annotation", "mood"]
    labels = {
        "status": "STATUS",
        "progress": "PROGRESS",
        "rating": "RATING",
        "genre": "GENRE",
        "annotation": "NOTES",
        "mood": "MOOD",
    }
    for i, cat in enumerate(order):
        col, row = i % 3, i // 3
        x0 = 50 + col * 520
        y0 = 190 + row * 640
        d.rounded_rectangle([x0, y0, x0 + 490, y0 + 580], radius=28, fill=(255, 255, 255), outline=(22, 32, 56), width=3)
        d.text((x0 + 245, y0 + 40), labels[cat], font=_font(26, True), fill=(22, 32, 56), anchor="mt")
        samples = by_mod.get(cat, [])[:4]
        for j, im in enumerate(samples):
            cx, cy = j % 2, j // 2
            thumb = im.resize((190, 190), Image.Resampling.LANCZOS)
            grid.paste(thumb, (x0 + 40 + cx * 220, y0 + 100 + cy * 220), thumb)
    grid.save(PREVIEWS / "reader_os_preview_3_modules.jpg", quality=93)
    print("  reader_os_preview_3_modules.jpg")

    # 4 included
    incl = Image.new("RGB", (H, H), (250, 246, 236))
    d = ImageDraw.Draw(incl)
    d.rectangle([0, 0, H, 160], fill=(22, 32, 56))
    d.text((H // 2, 50), "WHAT'S INCLUDED", font=_serif(40, True), fill=(250, 246, 236), anchor="mt")
    d.text((H // 2, 115), "Instant download for your iPad library", font=_font(20), fill=(196, 158, 72), anchor="mt")
    bullets = [
        (str(len(paths)), "Transparent PNGs", "900×900 — crisp on retina iPad displays"),
        ("6+", "System modules", "Status · Progress · Rating · Genre · Notes · Mood"),
        ("Apps", "Works in", "GoodNotes · Notability · Procreate · Freeform · Canva"),
        ("1", "Master sheet", "Optional print sheet if you ever want paper"),
    ]
    y = 230
    for num, title, sub in bullets:
        d.ellipse([130, y, 270, y + 130], fill=(22, 32, 56))
        d.text((200, y + 65), num, font=_font(28, True), fill=(196, 158, 72), anchor="mm")
        d.text((310, y + 35), title, font=_font(34, True), fill=(22, 32, 56), anchor="lt")
        d.text((310, y + 90), sub, font=_font(22), fill=(110, 108, 100), anchor="lt")
        y += 170
    d.rectangle([100, 980, H - 100, 990], fill=(196, 158, 72))
    d.text(
        (H // 2, 1080),
        "Import → GoodNotes Elements / Notability photos / Procreate",
        font=_font(22),
        fill=(22, 32, 56),
        anchor="mt",
    )
    d.text(
        (H // 2, 1150),
        "Track TBR, progress, genre & notes on your digital reading log",
        font=_font(20),
        fill=(110, 108, 100),
        anchor="mt",
    )
    for i, (_, _, path) in enumerate(paths[:8]):
        thumb = Image.open(path).convert("RGBA").resize((150, 150), Image.Resampling.LANCZOS)
        incl.paste(thumb, (100 + i * 180, 1280), thumb)
    incl.save(PREVIEWS / "reader_os_preview_4_included.jpg", quality=93)
    print("  reader_os_preview_4_included.jpg")

    # 5 how to use digital
    how = Image.new("RGB", (H, H), (22, 32, 56))
    d = ImageDraw.Draw(how)
    d.text((H // 2, 80), "HOW TO USE ON IPAD", font=_serif(40, True), fill=(250, 246, 236), anchor="mt")
    steps = [
        ("1", "Download the ZIP on your iPad (Files app)"),
        ("2", "Unzip → open stickers/png/ or by_module/"),
        ("3", "GoodNotes: insert image · pin as Element for reuse"),
        ("4", "Notability: add photo · resize · duplicate freely"),
        ("5", "Procreate: import PNG · stamp on reading journal pages"),
        ("6", "Layer STATUS + GENRE + RATING on each book entry"),
    ]
    y = 220
    for num, text in steps:
        d.ellipse([120, y, 220, y + 100], fill=(196, 158, 72))
        d.text((170, y + 50), num, font=_font(36, True), fill=(22, 32, 56), anchor="mm")
        d.text((260, y + 50), text, font=_font(26), fill=(250, 246, 236), anchor="lm")
        y += 140
    d.text(
        (H // 2, H - 80),
        "Designed for digital readers  ·  optional print sheet included",
        font=_font(20),
        fill=(196, 158, 72),
        anchor="mt",
    )
    how.save(PREVIEWS / "reader_os_preview_5_howto.jpg", quality=93)
    print("  reader_os_preview_5_howto.jpg")

    # 6 sheet
    sp = sheet.copy()
    sp.thumbnail((1500, 1500), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1600, 1600), (250, 246, 236))
    canvas.paste(sp, ((1600 - sp.width) // 2, (1600 - sp.height) // 2))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 1520, 1600, 1600], fill=(22, 32, 56))
    d.text(
        (800, 1560),
        "Full system sheet  ·  also great as printables if you want paper",
        font=_font(18),
        fill=(250, 246, 236),
        anchor="mm",
    )
    canvas.save(PREVIEWS / "reader_os_preview_6_sheet.jpg", quality=93)
    print("  reader_os_preview_6_sheet.jpg")


def build_zip(paths: list[tuple[str, str, Path]]):
    print("=== ZIP ===")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    readme = f"""MathRelaxing — Reader OS Digital Sticker System
================================================

A functional sticker system for DIGITAL readers.

Made for:
  · iPad + GoodNotes / Notability / Freeform
  · Procreate reading journals
  · Kindle app screenshots & digital logs
  · Optional: print the master sheet on sticker paper

This is NOT a random cute pack.
Modules work as a reading "OS":

  STATUS      Currently Reading, TBR, DNF, Finished...
  PROGRESS    10%–100% rings, Last Chapter, Cliffhanger
  RATING      1–5 stars + Life Changing
  GENRE       Fantasy, Romance, Thriller, Sci-Fi...
  ANNOTATION  Plot Twist, Highlight, Bookmark, Trope Unlocked...
  MOOD        Cozy, Spicy, Dark Academia, Mind Blown...
  + chips (iPad session, GoodNotes log, e-reader night...) & mini book icons

CONTENTS
  stickers/png/           {len(paths)} transparent PNGs (900×900)
  stickers/by_module/     same files sorted by module
  sheets/                 master sheet (optional print)
  README.txt

HOW TO USE ON IPAD
  1. Open the ZIP in the Files app and unzip
  2. GoodNotes: Insert image → save as Element for reuse
  3. Notability: Add photo → resize and duplicate
  4. Procreate: Import PNG as a stamp layer
  5. Stack STATUS + GENRE + RATING on each book entry

Personal use only. Not for resale of the sticker files.
© MathRelaxing
"""
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", readme)
        for fname, mod, path in paths:
            zf.write(path, f"stickers/png/{fname}")
            zf.write(path, f"stickers/by_module/{mod}/{fname}")
        for p in SHEETS.glob("*"):
            if p.suffix.lower() in (".png", ".jpg"):
                zf.write(p, f"sheets/{p.name}")
    mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"  {ZIP_PATH.name} ({mb:.1f} MB)")


def main():
    _ensure()
    items = catalog()
    paths = render_all_stickers(items)
    sheet = make_sheet(paths)
    sheet.save(SHEETS / "Reader_OS_All_Stickers_Sheet.png", "PNG")
    sheet.convert("RGB").save(SHEETS / "Reader_OS_All_Stickers_Sheet.jpg", quality=92)
    print("  sheets saved")
    make_previews(paths, sheet)
    build_zip(paths)
    if HTML_DIR.exists():
        shutil.rmtree(HTML_DIR, ignore_errors=True)
    print("DONE →", OUT)
    print(f"Total: {len(paths)} premium stickers")


if __name__ == "__main__":
    main()
