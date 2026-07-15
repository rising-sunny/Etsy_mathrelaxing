"""
brand.py — MathRelaxing shared brand kit  (SINGLE SOURCE OF TRUTH)
===================================================================
Every product builder imports from here so the visual identity never drifts:
the black footer band + logo, the gold/cream palette, the serif typography,
the dark themed cover layout, the Procreate .swatches writer and the mp4
encoder. DO NOT hard-code these values in a product script — import them.

Rules that always hold (see STANDARDS.md):
  • Every cover / preview carries the black footer band with the MathRelaxing
    logo (infinity + wordmark), rendered from mathrelaxing_logo.png.
  • Titles are serif; product name in CREAM, subtitle in GOLD.
  • Covers sit on a per-product dark THEME colour; iPad previews use IPAD_NAVY.
  • Descriptions end with the COPYRIGHT line and the STORE url.
  • Listings are always created as drafts.
"""

import os
import json
import zipfile
import colorsys
import shutil
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

BASE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE, "mathrelaxing_logo.png")

# ── Palette ──────────────────────────────────────────────────────────────────
GOLD = "#c9a24b"          # accents, subtitles, count labels
CREAM = "#f8f4eb"         # product-name titles, body on dark
INK = "black"             # line art
IPAD_NAVY = "#12172d"     # fixed background for ALL iPad-bundle previews
IPAD_TEAL = "#7fb0aa"     # iPad app-name accent
IPAD_GOLD = "#c7ad7c"     # iPad subtitle gold

# ── Copy constants ───────────────────────────────────────────────────────────
# Do NOT put STORE in Etsy listing descriptions (off-platform link risk).
STORE = "mathrelaxing.store"  # only for non-Etsy assets if needed
COPYRIGHT = "© MathRelaxing. For personal use only. Not for redistribution or resale."

# ── Typography helpers (matplotlib kwargs) ───────────────────────────────────
SERIF = dict(family="serif")
SERIF_BOLD = dict(family="serif", fontweight="bold")
SANS = dict(family="sans-serif")


# ── Logo & footer band ───────────────────────────────────────────────────────
def add_logo(ax, cx, cy, width, zorder=6):
    """Place the MathRelaxing logo (infinity + wordmark), sized by width, centred at (cx,cy)."""
    logo = mpimg.imread(LOGO_PATH)
    h = width * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(cx - width / 2, cx + width / 2, cy - h / 2, cy + h / 2),
              zorder=zorder, aspect="auto")


def footer_band(ax, W, band_h, logo_frac=0.66):
    """Black footer band across the bottom with the logo centred inside it."""
    ax.add_patch(plt.Rectangle((0, 0), W, band_h, color="black", zorder=1))
    logo = mpimg.imread(LOGO_PATH)
    lh = band_h * logo_frac
    lw = lh * logo.shape[1] / logo.shape[0]
    add_logo(ax, W / 2, band_h * 0.5, lw)


# ── Standard dark cover (used by every book / print cover) ───────────────────
def cover(theme_bg, emblem, title, subtitle, tagline, count_label,
          watermark=None, square=True):
    """
    Build the canonical MathRelaxing cover figure and return it.

    theme_bg    : hex background colour for THIS product (books are themed).
    emblem      : fn(ax, cx, cy, r) that draws the product emblem in GOLD.
    title       : product name (rendered CREAM, serif bold, upper looks best).
    subtitle    : one-word/short subtitle (rendered GOLD serif).
    tagline     : italic line under the subtitle.
    count_label : e.g. "50 Knotwork Designs" (GOLD).
    watermark   : optional fn(ax, W, H) drawing a faint background pattern.
    square      : True -> 8x8 listing photo; False -> 8.5x11 portrait PDF cover.
    """
    W, H = (8.0, 8.0) if square else (8.5, 11.0)
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    fig.patch.set_facecolor(theme_bg); ax.set_facecolor(theme_bg)

    if watermark:
        watermark(ax, W, H)

    band_h = min(1.6, 0.18 * H)
    region = H - band_h
    if emblem:
        emblem(ax, W / 2, band_h + 0.64 * region, 0.245 * region)
    ax.text(W / 2, band_h + 0.35 * region, title, ha="center", va="center",
            fontsize=4.0 * W, color=CREAM, zorder=4, **SERIF_BOLD)
    ax.text(W / 2, band_h + 0.26 * region, subtitle, ha="center", va="center",
            fontsize=2.65 * W, color=GOLD, zorder=4, **SERIF)
    if tagline:
        ax.text(W / 2, band_h + 0.16 * region, tagline, ha="center", va="center",
                fontsize=1.5 * W, style="italic", color=CREAM, zorder=4, **SERIF)
    if count_label:
        ax.text(W / 2, band_h + 0.082 * region, count_label, ha="center", va="center",
                fontsize=1.35 * W, color=GOLD, zorder=4, **SERIF)

    footer_band(ax, W, band_h)
    return fig


# ── About / mathematics page (portrait, used inside book PDFs) ───────────────
def about_page(heading, body, footer=COPYRIGHT):
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
    ax.text(4.25, 10.0, heading, ha="center", fontsize=20, **SERIF_BOLD)
    ax.text(4.25, 8.9, body, ha="center", va="top", fontsize=11.5,
            linespacing=1.9, **SERIF)
    ax.text(4.25, 0.65, footer, ha="center", fontsize=9, color="#666666")
    return fig


# ── iPad-bundle preview scaffolds (fixed navy identity) ──────────────────────
def ipad_fig():
    fig = plt.figure(figsize=(10, 10)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    fig.patch.set_facecolor(IPAD_NAVY); ax.set_facecolor(IPAD_NAVY)
    return fig, ax


def ipad_frame(ax, cx, cy, w, h):
    """Draw an iPad bezel + white screen; return the white screen rect (x,y,w,h)."""
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=0.22", fill=True,
                 facecolor="#0c0e16", edgecolor="#3a3f52", lw=2, zorder=2))
    sm = 0.16
    ax.add_patch(FancyBboxPatch((cx - w / 2 + sm, cy - h / 2 + sm), w - 2 * sm, h - 2 * sm,
                 boxstyle="round,pad=0,rounding_size=0.05", fill=True,
                 facecolor="white", edgecolor="none", zorder=2.5))
    return (cx - w / 2 + sm, cy - h / 2 + sm, w - 2 * sm, h - 2 * sm)


def ipad_logo(ax, cx, cy, w):
    add_logo(ax, cx, cy, w, zorder=6)


# ── Procreate .swatches writer ───────────────────────────────────────────────
def swatches_file(path, name, hexes):
    """Write a Procreate .swatches file (zipped Swatches.json) from a list of hex colours."""
    sw = []
    for hx in hexes:
        r = int(hx[1:3], 16) / 255
        g = int(hx[3:5], 16) / 255
        b = int(hx[5:7], 16) / 255
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        sw.append({"hue": round(h, 4), "saturation": round(s, 4),
                   "brightness": round(v, 4), "alpha": 1, "colorSpace": 0})
    data = [{"name": name, "swatches": sw}]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Swatches.json", json.dumps(data))


# ── Video encoder (seamless loops & promos) ──────────────────────────────────
def encode_mp4(frames_dir, out_path, fps=30, pattern="f_%04d.png", crf=20, cleanup=True):
    """Encode a folder of numbered PNG frames into an Etsy-ready h264 mp4 (yuv420p)."""
    subprocess.run(
        ["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(frames_dir, pattern),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-crf", str(crf), out_path],
        check=True, capture_output=True)
    if cleanup:
        shutil.rmtree(frames_dir, ignore_errors=True)
