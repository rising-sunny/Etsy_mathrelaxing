"""
build_reader_os_video.py — HTML/CSS animated promo for Reader OS
================================================================
Renders a self-contained HTML animation (CSS keyframes + staggered
sticker entrances, iPad mockup scene) and captures frames with
Playwright by scrubbing Web Animations API, then encodes Etsy MP4.

  python build_reader_os_video.py
  python build_reader_os_video.py --upload   # also push video to listing

Etsy: ~12s, 1080×1080, 30fps, h264 silent.
"""
from __future__ import annotations

import argparse
import base64
import math
import os
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import brand

BASE = Path(__file__).resolve().parent
OUT = BASE / "reader_os"
STICKERS = OUT / "stickers" / "png"
FRAMES = OUT / "_video_frames"
HTML_PATH = OUT / "_promo.html"
VIDEO = OUT / "Reader_OS_promo.mp4"

S = 1080
FPS = 30
DURATION = 12.0  # Etsy 5–15s
N = int(DURATION * FPS)

# Pick a curated set of stickers for the animation (must exist)
PICKS = [
    "status_currently_reading.png",
    "status_tbr.png",
    "status_finished.png",
    "status_dnf.png",
    "progress_50.png",
    "progress_100.png",
    "progress_10.png",
    "rating_5star.png",
    "rating_4star.png",
    "rating_life_changing.png",
    "genre_fantasy.png",
    "genre_sci_fi.png",
    "genre_romance.png",
    "note_plot_twist.png",
    "note_highlight.png",
    "mood_cozy.png",
    "mood_dark_academia.png",
    "chip_ipad_session.png",
    "chip_goodnotes_log.png",
    "chip_book_club.png",
    "icon_book_currently.png",
    "icon_book_tbr.png",
]


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def build_html() -> str:
    """Self-contained HTML with CSS animations scrubbable via getAnimations()."""
    imgs = []
    for name in PICKS:
        p = STICKERS / name
        if not p.exists():
            print(f"  warn: missing {name}")
            continue
        imgs.append((name, f"data:image/png;base64,{_b64(p)}"))

    # Layout positions for floating stickers (scene 2) — % of stage
    float_layout = [
        (8, 18, 0.22, 0.0),
        (38, 12, 0.20, 0.08),
        (68, 20, 0.24, 0.04),
        (12, 48, 0.21, 0.12),
        (42, 42, 0.26, 0.06),
        (72, 48, 0.20, 0.14),
        (20, 72, 0.22, 0.10),
        (50, 70, 0.23, 0.16),
        (78, 74, 0.19, 0.18),
        (30, 30, 0.18, 0.20),
        (60, 32, 0.19, 0.22),
        (5, 65, 0.17, 0.24),
    ]

    float_html = []
    for i, ((x, y, sc, delay), (name, src)) in enumerate(zip(float_layout, imgs)):
        float_html.append(
            f'<img class="float-s" src="{src}" alt="" '
            f'style="--x:{x}%;--y:{y}%;--sc:{sc};--d:{delay}s;" />'
        )

    # iPad page stickers (scene 3)
    ipad_stickers = [
        (imgs[0][1], 12, 22, 0.28, 0.0),
        (imgs[1][1], 48, 18, 0.20, 0.15),
        (imgs[4][1], 72, 22, 0.26, 0.30),
        (imgs[7][1], 18, 48, 0.30, 0.45),
        (imgs[10][1], 55, 50, 0.22, 0.55),
        (imgs[15][1], 30, 70, 0.24, 0.70),
        (imgs[17][1], 62, 72, 0.28, 0.85),
    ]
    ipad_html = []
    for src, x, y, sc, delay in ipad_stickers:
        ipad_html.append(
            f'<img class="ipad-s" src="{src}" alt="" '
            f'style="--x:{x}%;--y:{y}%;--sc:{sc};--d:{delay}s;" />'
        )

    # Module chips scene
    modules = [
        ("STATUS", imgs[0][1]),
        ("PROGRESS", imgs[4][1]),
        ("RATING", imgs[7][1]),
        ("GENRE", imgs[10][1]),
        ("NOTES", imgs[13][1]),
        ("MOOD", imgs[15][1]),
    ]
    mod_html = []
    for i, (lab, src) in enumerate(modules):
        mod_html.append(
            f'<div class="mod" style="--i:{i};">'
            f'<img src="{src}" alt=""/><span>{lab}</span></div>'
        )

    # End card row
    end_row = "".join(
        f'<img src="{src}" alt="" class="end-s" style="--i:{i};"/>'
        for i, (_, src) in enumerate(imgs[:8])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width={S}, height={S}"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {S}px; height: {S}px;
  overflow: hidden;
  background: #161f38;
  font-family: 'DM Sans', system-ui, sans-serif;
  color: #faf6ec;
  -webkit-font-smoothing: antialiased;
}}
.stage {{
  position: relative;
  width: {S}px; height: {S}px;
  background:
    radial-gradient(ellipse 80% 60% at 50% 40%, #1e2a4a 0%, #161f38 55%, #0e1424 100%);
  overflow: hidden;
}}

/* ── Scene visibility (driven by CSS animations on opacity) ── */
.scene {{
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
}}

/* Timeline (total 12s):
   0.0–1.8  title
   1.5–5.2  float stickers (overlap title fade)
   4.8–8.4  iPad
   8.0–10.4 modules
   10.0–12  end
*/

/* Single-timeline keyframes per scene (scrub-friendly) */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Scene 1 — title 0–1.9s */
#s-title {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  animation: titleLife 1.9s cubic-bezier(.22,1,.36,1) 0s both;
}}
@keyframes titleLife {{
  0%   {{ opacity: 0; transform: scale(0.92) translateY(18px); }}
  18%  {{ opacity: 1; transform: scale(1) translateY(0); }}
  78%  {{ opacity: 1; transform: scale(1) translateY(0); }}
  100% {{ opacity: 0; transform: scale(1.02) translateY(-8px); }}
}}
#s-title h1 {{
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 700;
  font-size: 96px;
  letter-spacing: 0.04em;
  color: #faf6ec;
  text-shadow: 0 8px 40px rgba(0,0,0,0.35);
}}
#s-title .line {{
  width: 0; height: 4px; background: #c49e48; border-radius: 2px;
  margin: 22px 0 18px;
  animation: lineGrow 0.7s cubic-bezier(.22,1,.36,1) 0.35s both;
}}
@keyframes lineGrow {{
  from {{ width: 0; }}
  to   {{ width: 140px; }}
}}
#s-title .sub {{
  font-size: 28px; font-weight: 500; color: #c49e48;
  letter-spacing: 0.02em;
  animation: fadeUp 0.7s ease 0.45s both;
}}
#s-title .tag {{
  margin-top: 28px;
  font-size: 18px; font-weight: 600; color: #a8a498;
  letter-spacing: 0.12em; text-transform: uppercase;
  animation: fadeUp 0.7s ease 0.65s both;
}}

/* Scene 2 — floating stickers 1.5–5.2s */
#s-float {{
  animation: floatScene 3.7s linear 1.5s both;
}}
@keyframes floatScene {{
  0%   {{ opacity: 0; }}
  8%   {{ opacity: 1; }}
  88%  {{ opacity: 1; }}
  100% {{ opacity: 0; }}
}}
#s-float .caption {{
  position: absolute; top: 48px; left: 0; right: 0;
  text-align: center;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 36px; font-weight: 700; color: #faf6ec;
  animation: fadeUp 0.5s ease 1.7s both;
}}
#s-float .caption span {{ color: #c49e48; }}
.float-s {{
  position: absolute;
  left: var(--x); top: var(--y);
  width: calc(1080px * var(--sc));
  height: auto;
  transform: translate(-50%, -50%) scale(0.6);
  opacity: 0;
  filter: drop-shadow(0 14px 28px rgba(0,0,0,0.35));
  animation: popIn 0.65s cubic-bezier(.34,1.4,.64,1) calc(1.55s + var(--d)) both;
}}
@keyframes popIn {{
  from {{ opacity: 0; transform: translate(-50%, -50%) scale(0.55) rotate(-6deg); }}
  to   {{ opacity: 1; transform: translate(-50%, -50%) scale(1) rotate(0deg); }}
}}

/* Scene 3 — iPad 4.85–8.3s */
#s-ipad {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  animation: ipadScene 3.45s linear 4.85s both;
}}
@keyframes ipadScene {{
  0%   {{ opacity: 0; }}
  10%  {{ opacity: 1; }}
  88%  {{ opacity: 1; }}
  100% {{ opacity: 0; }}
}}
#s-ipad .cap {{
  position: absolute; top: 36px; left: 0; right: 0; text-align: center;
  font-size: 22px; font-weight: 700; color: #c49e48; letter-spacing: 0.08em;
  text-transform: uppercase;
  animation: fadeUp 0.5s ease 5.0s both;
}}
.tablet {{
  width: 720px; height: 880px;
  background: #1c1c20;
  border-radius: 42px;
  box-shadow:
    0 30px 80px rgba(0,0,0,0.45),
    0 0 0 3px #0a0a0c,
    inset 0 0 0 2px #3a3a42;
  position: relative;
  padding: 28px 22px 36px;
  animation: tabletIn 0.7s cubic-bezier(.22,1,.36,1) 4.95s both;
}}
@keyframes tabletIn {{
  from {{ opacity: 0; transform: translateY(40px) scale(0.94); }}
  to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.tablet .notch {{
  position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
  width: 90px; height: 10px; background: #0a0a0c; border-radius: 6px;
}}
.tablet .screen {{
  width: 100%; height: 100%;
  background: linear-gradient(180deg, #faf6ec 0%, #f3ebe0 100%);
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}}
.tablet .bar {{
  height: 48px; background: #161f38;
  display: flex; align-items: center; justify-content: center;
  color: #faf6ec; font-size: 16px; font-weight: 700; letter-spacing: 0.04em;
}}
.tablet .page {{
  position: absolute; inset: 48px 0 0 0;
  padding: 24px 28px;
}}
.tablet .page-title {{
  font-family: 'Fraunces', Georgia, serif;
  font-size: 26px; color: #161f38; text-align: center; margin-bottom: 10px;
}}
.tablet .lines {{
  position: absolute; left: 36px; right: 36px; top: 90px; bottom: 24px;
  background: repeating-linear-gradient(
    180deg, transparent 0 38px, #e6ddd0 38px 40px
  );
  opacity: 0.85;
}}
.ipad-s {{
  position: absolute;
  left: var(--x); top: var(--y);
  width: calc(100% * var(--sc));
  height: auto;
  transform: translate(-50%, -50%) scale(0.4);
  opacity: 0;
  filter: drop-shadow(0 8px 16px rgba(22,31,56,0.18));
  animation: stampIn 0.55s cubic-bezier(.34,1.45,.64,1) calc(5.35s + var(--d)) both;
}}
@keyframes stampIn {{
  0%   {{ opacity: 0; transform: translate(-50%, -50%) scale(1.4) rotate(8deg); }}
  70%  {{ opacity: 1; transform: translate(-50%, -50%) scale(0.95) rotate(-2deg); }}
  100% {{ opacity: 1; transform: translate(-50%, -50%) scale(1) rotate(0deg); }}
}}
.tablet .home {{
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  width: 100px; height: 5px; background: #5a5a62; border-radius: 3px;
}}
#s-ipad .foot {{
  position: absolute; bottom: 40px; left: 0; right: 0; text-align: center;
  font-size: 18px; color: #a8a498;
  animation: fadeUp 0.5s ease 5.2s both;
}}

/* Scene 4 — modules 8.05–10.25s */
#s-mods {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 28px;
  animation: modsScene 2.2s linear 8.05s both;
}}
@keyframes modsScene {{
  0%   {{ opacity: 0; }}
  12%  {{ opacity: 1; }}
  85%  {{ opacity: 1; }}
  100% {{ opacity: 0; }}
}}
#s-mods h2 {{
  font-family: 'Fraunces', Georgia, serif;
  font-size: 40px; font-weight: 700;
  animation: fadeUp 0.45s ease 8.15s both;
}}
#s-mods h2 span {{ color: #c49e48; }}
.mod-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  width: 900px;
}}
.mod {{
  background: rgba(250,246,236,0.06);
  border: 2px solid rgba(196,158,72,0.35);
  border-radius: 24px;
  padding: 18px 12px 16px;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  opacity: 0;
  transform: translateY(24px) scale(0.9);
  animation: modIn 0.5s cubic-bezier(.22,1,.36,1) calc(8.25s + var(--i) * 0.1s) both;
}}
@keyframes modIn {{
  to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.mod img {{ width: 140px; height: 140px; object-fit: contain; }}
.mod span {{
  font-size: 15px; font-weight: 800; letter-spacing: 0.14em;
  color: #c49e48;
}}

/* Scene 5 — end 10.05–12s */
#s-end {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  animation: endScene 2.0s linear 10.05s both;
}}
@keyframes endScene {{
  0%   {{ opacity: 0; }}
  15%  {{ opacity: 1; }}
  100% {{ opacity: 1; }}
}}
#s-end h1 {{
  font-family: 'Fraunces', Georgia, serif;
  font-size: 72px; font-weight: 700;
  animation: fadeUp 0.55s ease 10.15s both;
}}
#s-end .gold {{
  margin: 16px 0 10px;
  font-size: 24px; font-weight: 700; color: #c49e48;
  animation: fadeUp 0.55s ease 10.3s both;
}}
#s-end .apps {{
  font-size: 18px; color: #a8a498; letter-spacing: 0.04em;
  animation: fadeUp 0.55s ease 10.4s both;
}}
#s-end .row {{
  display: flex; gap: 8px; margin-top: 36px;
  animation: fadeUp 0.6s ease 10.5s both;
}}
.end-s {{
  width: 96px; height: 96px; object-fit: contain;
  filter: drop-shadow(0 6px 14px rgba(0,0,0,0.3));
  animation: endPop 0.45s cubic-bezier(.34,1.4,.64,1) calc(10.55s + var(--i) * 0.05s) both;
  opacity: 0;
}}
@keyframes endPop {{
  from {{ opacity: 0; transform: scale(0.5) translateY(16px); }}
  to   {{ opacity: 1; transform: scale(1) translateY(0); }}
}}
#s-end .brand {{
  position: absolute; bottom: 48px;
  font-size: 18px; color: #6e6c64; letter-spacing: 0.08em;
  animation: fadeUp 0.5s ease 10.7s both;
}}

/* Soft grain overlay */
.grain {{
  position: absolute; inset: 0; pointer-events: none; opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  z-index: 50;
}}
</style>
</head>
<body>
<div class="stage">
  <div class="scene" id="s-title">
    <h1>READER OS</h1>
    <div class="line"></div>
    <div class="sub">Digital sticker system for iPad readers</div>
    <div class="tag">61 stickers  ·  6 modules  ·  one system</div>
  </div>

  <div class="scene" id="s-float">
    <div class="caption">Not random cute — a <span>reading OS</span></div>
    {"".join(float_html)}
  </div>

  <div class="scene" id="s-ipad">
    <div class="cap">Drop into GoodNotes · Notability · Procreate</div>
    <div class="tablet">
      <div class="notch"></div>
      <div class="screen">
        <div class="bar">GoodNotes  ·  Reading Log</div>
        <div class="page">
          <div class="page-title">June reading list</div>
          <div class="lines"></div>
          {"".join(ipad_html)}
        </div>
      </div>
      <div class="home"></div>
    </div>
    <div class="foot">Stamp STATUS · GENRE · RATING on every book</div>
  </div>

  <div class="scene" id="s-mods">
    <h2>Six modules · <span>one system</span></h2>
    <div class="mod-grid">{"".join(mod_html)}</div>
  </div>

  <div class="scene" id="s-end">
    <h1>READER OS</h1>
    <div class="gold">iPad digital stickers · Instant download</div>
    <div class="apps">GoodNotes · Notability · Procreate · Freeform</div>
    <div class="row">{end_row}</div>
    <div class="brand">MathRelaxing</div>
  </div>

  <div class="grain"></div>
</div>
<script>
// Expose scrub helper for Playwright
window.__scrub = function(ms) {{
  document.getAnimations({{ subtree: true }}).forEach(a => {{
    a.pause();
    a.currentTime = ms;
  }});
}};
// Pause everything at t=0 so first paint is clean
window.__scrub(0);
</script>
</body>
</html>
"""


def render_frames():
    if not STICKERS.exists():
        print("ERROR: stickers not found. Run generate_reader_os.py first.")
        sys.exit(1)

    print("Building HTML promo…")
    html = build_html()
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"  {HTML_PATH} ({len(html) / 1024:.0f} KB)")

    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)

    print(f"Capturing {N} frames @ {FPS}fps ({DURATION}s) via Playwright…")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": S, "height": S},
            device_scale_factor=1,
        )
        page.goto(HTML_PATH.resolve().as_uri(), wait_until="networkidle")
        # Wait for Google fonts
        page.wait_for_timeout(800)
        page.evaluate("window.__scrub(0)")

        for i in range(N):
            t_ms = (i / FPS) * 1000.0
            page.evaluate(f"window.__scrub({t_ms:.2f})")
            # tiny settle for layout
            page.wait_for_timeout(8)
            path = FRAMES / f"f_{i:04d}.png"
            page.screenshot(path=str(path), type="png")
            if i % 30 == 0:
                print(f"  frame {i}/{N} t={t_ms/1000:.1f}s")

        browser.close()
    print(f"  done {N} frames")


def encode():
    print("Encoding MP4…")
    brand.encode_mp4(str(FRAMES), str(VIDEO), fps=FPS, pattern="f_%04d.png", crf=20, cleanup=True)
    mb = VIDEO.stat().st_size / (1024 * 1024)
    print(f"Video listo: {VIDEO} ({mb:.1f} MB)")
    print(f"Duration ~{DURATION:.0f}s · {S}x{S} · silent · Etsy-ready")


def upload():
    from etsy_manager import EtsyManager
    from products_catalog import PRODUCTS

    lid = PRODUCTS["reader_os_stickers"]["listing_id"]
    m = EtsyManager()
    print(f"Uploading video to listing {lid}…")
    m.upload_listing_video(lid, str(VIDEO))
    print("Video uploaded.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true", help="Upload MP4 to Etsy listing")
    ap.add_argument("--skip-render", action="store_true", help="Only encode existing frames")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if not args.skip_render:
        render_frames()
    encode()
    if args.upload:
        upload()


if __name__ == "__main__":
    main()
