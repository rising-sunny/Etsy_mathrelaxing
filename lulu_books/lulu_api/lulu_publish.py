"""
lulu_publish.py — Lulu Print API (POD) automation for the mathrelaxing
coloring book.

This is the Lulu-adapted successor to the old `ingramspark_kdp_video.py`
publishing pipeline. Key differences vs. that KDP/IngramSpark script:

  KDP / IngramSpark (old script)      ->  Lulu (this module)
  ----------------------------------      ----------------------------------
  Generate PDFs, upload by hand on    ->  Generate PDFs, host them at a public
  the platform website                    URL, then create a print-job via API
  Spine width from hard-coded paper   ->  Spine/cover size from Lulu's
  thickness constants                     /cover-dimensions/ API (authoritative)
  Trim chosen from SUPPORTED_SIZES_*  ->  pod_package_id SKU (dotted 27-char)
  Source art = raster images, forced  ->  Source art = the existing *vector*
  to CMYK, rasterized into pages           page PDFs, merged vector-preserving
  No ordering / fulfilment                Cost calc + create print-job + status

Lulu file rules implemented here (from the API getting-started guide):
  * Interior: single-page portrait PDF; every page sized to trim + 0.125" bleed
    on all four sides; 0.5" safety margin; fonts embedded; images 300-600 PPI.
  * Cover: single-page spread (back | spine | front); dimensions come from the
    /cover-dimensions/ endpoint; 0.125" bleed; 0.5" safety margin.

Credentials are read from a .env file (see make_env() / .env.example), never
hard-coded.  Endpoints:
  prod    https://api.lulu.com/
  sandbox https://api.sandbox.lulu.com/
"""

from __future__ import annotations

import base64
import glob
import hashlib
import json
import os
import secrets
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(HERE)
BOOK = os.path.join(HERE, "book")

# Lulu fetches interior/cover files from a PUBLIC url — this repo has no web
# server of its own, so publish_to_downloads() writes locally and you must
# host DOWNLOADS_DIR somewhere public (your own site, S3 + CloudFront, etc.)
# and point DOWNLOADS_URL at that host. Override both via env vars.
DOWNLOADS_DIR = os.environ.get("LULU_DOWNLOADS_DIR", os.path.join(_ROOT, "output", "hosted"))
DOWNLOADS_URL = os.environ.get("LULU_DOWNLOADS_URL", "")  # e.g. https://your-domain.com/downloads

PT_PER_IN = 72.0

# Lulu requires ALL fonts embedded. PyMuPDF's built-in "Helvetica" is a
# non-embedded base-14 font and gets rejected, so we embed real TrueType.
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = os.path.join(_FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")
# Display face for the cover title: Cinzel (engraved Roman capitals, OFL —
# free for commercial print). Static SemiBold instanced from the variable font.
FONT_TITLE = os.path.join(_ROOT, "assets", "fonts", "Cinzel-SemiBold.ttf")

# generate_one_per_family.py (curve functions used on the math appendix page)
# lives in core/, one level up from this file.
sys.path.insert(0, os.path.join(_ROOT, "core"))


def _embed_textbox(page, rect, text, fontsize, *, bold=False,
                   align=fitz.TEXT_ALIGN_CENTER, color=(0, 0, 0), rotate=0,
                   fontname=None, fontfile=None):
    """insert_textbox with an embedded (subset) TrueType font. Pass an explicit
    fontname+fontfile to use a custom face (e.g. the Cinzel cover title)."""
    fn = fontname or ("djvb" if bold else "djv")
    ff = fontfile or (FONT_BOLD if bold else FONT_REGULAR)
    return page.insert_textbox(
        rect, text, fontsize=fontsize, fontname=fn, fontfile=ff,
        align=align, color=color, rotate=rotate)


# ---------------------------------------------------------------------------
# Credentials / config
# ---------------------------------------------------------------------------
def load_env(path: Optional[str] = None) -> dict:
    """Minimal .env loader (no external dependency). Looks in lulu_books/
    (package root, next to .env.example) by default -- NOT lulu_api/,
    matching where the README tells you to `cp .env.example .env`."""
    path = path or os.path.join(_ROOT, ".env")
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    # process env overrides file
    for k in ("LULU_CLIENT_KEY", "LULU_CLIENT_SECRET", "LULU_SANDBOX"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


# ---------------------------------------------------------------------------
# Product specification (replaces SUPPORTED_SIZES_* dicts)
# ---------------------------------------------------------------------------
@dataclass
class BookSpec:
    """A Lulu product. `pod_package_id` MUST be copied from the Lulu Pricing
    Calculator for the exact specs you choose; the ones below are sensible
    defaults that you should confirm before a real order."""
    pod_package_id: str
    trim_w_in: float
    trim_h_in: float
    bleed_in: float = 0.125
    safety_in: float = 0.5
    title: str = "Mathematical Tangle Art"
    subtitle: str = "A Coloring Book of Curves"
    author: str = "mathrelaxing"
    blurb: str = (
        "Fifty hand-crafted coloring pages built from real mathematical "
        "curves - Lissajous figures, polar roses, spirographs, "
        "hypocycloids and more. Each page is rendered as fine line art and "
        "filled with intricate tangle patterns, ready for you to color and "
        "relax."
    )

    # page box (trim + bleed on every side), in points
    @property
    def page_w_pt(self) -> float:
        return (self.trim_w_in + 2 * self.bleed_in) * PT_PER_IN

    @property
    def page_h_pt(self) -> float:
        return (self.trim_h_in + 2 * self.bleed_in) * PT_PER_IN

    @property
    def bleed_pt(self) -> float:
        return self.bleed_in * PT_PER_IN

    @property
    def safety_pt(self) -> float:
        return self.safety_in * PT_PER_IN


# Presets. SKUs follow the dotted format: TRIM.INK.QUALITY.BIND.PAPER.FINISH
#   0850X1100 = 8.5x11 in   |  BW=black&white  FC=full color
#   STD=standard quality    |  PB=perfect bound  CO=coil  SS=saddle-stitch
#   060UW444 = 60# uncoated white  |  MXX=matte cover  GXX=glossy cover
# CONFIRM the exact SKU in the Pricing Calculator before ordering.
PRESETS = {
    "letter_bw_pb":   BookSpec("0850X1100.BW.STD.PB.060UW444.MXX", 8.5, 11.0),
    "letter_color_pb": BookSpec("0850X1100.FC.STD.PB.080CW444.MXX", 8.5, 11.0),
    "letter_color_coil": BookSpec("0850X1100.FC.STD.CO.080CW444.MXX", 8.5, 11.0),
    "a4_bw_pb":       BookSpec("0827X1169.BW.STD.PB.060UW444.MXX", 8.27, 11.69),
}


# ---------------------------------------------------------------------------
# Lulu API client
# ---------------------------------------------------------------------------
class LuluError(RuntimeError):
    pass


class LuluClient:
    def __init__(self, client_key: str, client_secret: str, sandbox: bool = True,
                 timeout: int = 60):
        if not client_key or not client_secret:
            raise LuluError("Missing Lulu client key/secret.")
        self.client_key = client_key
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.timeout = timeout
        host = "api.sandbox.lulu.com" if sandbox else "api.lulu.com"
        self.base = f"https://{host}"
        self.token_url = (
            f"{self.base}/auth/realms/glasstree/protocol/openid-connect/token"
        )
        self._access_token = None
        self._token_expiry = 0.0

    # -- auth -------------------------------------------------------------
    def _basic_header(self) -> str:
        raw = f"{self.client_key}:{self.client_secret}".encode()
        return "Basic " + base64.b64encode(raw).decode()

    def token(self) -> str:
        if self._access_token and time.time() < self._token_expiry - 30:
            return self._access_token
        r = requests.post(
            self.token_url,
            data={"grant_type": "client_credentials"},
            headers={"Authorization": self._basic_header(),
                     "Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )
        if r.status_code != 200:
            raise LuluError(f"Token request failed ({r.status_code}): {r.text}")
        data = r.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + int(data.get("expires_in", 3600))
        return self._access_token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token()}",
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"}

    def _req(self, method: str, path: str, **kw):
        url = path if path.startswith("http") else f"{self.base}{path}"
        r = requests.request(method, url, headers=self._headers(),
                             timeout=self.timeout, **kw)
        if r.status_code >= 400:
            raise LuluError(f"{method} {path} -> {r.status_code}: {r.text}")
        return r.json() if r.text else {}

    # -- endpoints --------------------------------------------------------
    def cover_dimensions(self, pod_package_id: str, page_count: int,
                         unit: str = "pt") -> dict:
        """POST /cover-dimensions/ -> {width, height, unit}. The width/height
        is the FULL spread (back+spine+front incl. bleed)."""
        return self._req("POST", "/cover-dimensions/", json={
            "pod_package_id": pod_package_id,
            "interior_page_count": page_count,
            "unit": unit,
        })

    def validate_interior(self, source_url: str,
                          pod_package_id: Optional[str] = None) -> dict:
        body = {"source_url": source_url}
        if pod_package_id:
            body["pod_package_id"] = pod_package_id
        return self._req("POST", "/validate-interior/", json=body)

    def get_interior_validation(self, vid: int) -> dict:
        return self._req("GET", f"/validate-interior/{vid}/")

    def validate_cover(self, source_url: str, pod_package_id: str,
                       page_count: int) -> dict:
        return self._req("POST", "/validate-cover/", json={
            "source_url": source_url,
            "pod_package_id": pod_package_id,
            "interior_page_count": page_count,
        })

    def get_cover_validation(self, vid: int) -> dict:
        return self._req("GET", f"/validate-cover/{vid}/")

    def poll_interior(self, vid: int, tries: int = 30, delay: float = 4) -> dict:
        for _ in range(tries):
            res = self.get_interior_validation(vid)
            if res.get("status") in ("VALIDATED", "ERROR", "NORMALIZED"):
                return res
            time.sleep(delay)
        return self.get_interior_validation(vid)

    def cost_calculation(self, line_items: list, shipping_address: dict,
                         shipping_level: str = "MAIL",
                         currency: str = "USD") -> dict:
        """POST /print-job-cost-calculations/ — price WITHOUT placing an order.
        line_items: [{"page_count": int, "pod_package_id": str, "quantity": int}]"""
        return self._req("POST", "/print-job-cost-calculations/", json={
            "line_items": line_items,
            "shipping_address": shipping_address,
            "shipping_option": shipping_level,
            "shipping_level": shipping_level,
        })

    def create_print_job(self, *, interior_url: str, cover_url: str,
                         pod_package_id: str, quantity: int,
                         shipping_address: dict, contact_email: str,
                         title: str, shipping_level: str = "MAIL",
                         external_id: Optional[str] = None) -> dict:
        body = {
            "contact_email": contact_email,
            "external_id": external_id or f"mr-{secrets.token_hex(4)}",
            "line_items": [{
                "external_id": f"li-{secrets.token_hex(3)}",
                "title": title,
                "printable_normalization": {
                    "cover": {"source_url": cover_url},
                    "interior": {"source_url": interior_url},
                },
                "pod_package_id": pod_package_id,
                "quantity": quantity,
            }],
            "shipping_address": shipping_address,
            "shipping_level": shipping_level,
        }
        return self._req("POST", "/print-jobs/", json=body)

    def get_print_job(self, job_id: int) -> dict:
        return self._req("GET", f"/print-jobs/{job_id}/")

    def get_status(self, job_id: int) -> dict:
        return self._req("GET", f"/print-jobs/{job_id}/status/")

    def shipping_options(self, country_code: str, state_code: str = "",
                         quantity: int = 1,
                         pod_package_id: str = "") -> dict:
        params = {"country_code": country_code, "quantity": quantity}
        if state_code:
            params["state_code"] = state_code
        if pod_package_id:
            params["pod_package_id"] = pod_package_id
        return self._req("GET", "/shipping-options/", params=params)


# ---------------------------------------------------------------------------
# PDF builders (PyMuPDF / fitz — vector preserving)
# ---------------------------------------------------------------------------
def _fit_rect(src_w: float, src_h: float, box: fitz.Rect) -> fitz.Rect:
    """Largest rect with src aspect that fits inside `box`, centered."""
    scale = min(box.width / src_w, box.height / src_h)
    w, h = src_w * scale, src_h * scale
    x0 = box.x0 + (box.width - w) / 2
    y0 = box.y0 + (box.height - h) / 2
    return fitz.Rect(x0, y0, x0 + w, y0 + h)


def _add_text_page(doc: fitz.Document, spec: BookSpec, items, *,
                   align=fitz.TEXT_ALIGN_CENTER, top_frac=0.32):
    """Append a vector text page (title / copyright / intro).

    `items` is a list of (text, fontsize, bold) tuples. Empty text adds
    vertical space."""
    page = doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)
    safety = spec.safety_pt
    x0 = spec.bleed_pt + safety
    x1 = spec.page_w_pt - spec.bleed_pt - safety
    y = spec.page_h_pt * top_frac
    for text, fs, bold in items:
        if not text:
            y += fs * 1.4
            continue
        rect = fitz.Rect(x0, y, x1, y + fs * 6)
        _embed_textbox(page, rect, text, fs, bold=bold, align=align)
        approx_lines = max(1, int(len(text) / max(1, (x1 - x0) / (fs * 0.5))) + 1)
        y += fs * 1.5 * approx_lines + fs * 0.6
    return page


# ---------------------------------------------------------------------------
# Reference / instruction pages (math explainer + colouring tips).
# These print on the B&W interior, so everything is greyscale line-art + text.
# ---------------------------------------------------------------------------
def _draw_curve_icon(page, pts, cx, cy, half, *, width=0.7,
                     color=(0.12, 0.12, 0.12), max_pts=720):
    """Draw a small vector line-art icon of a curve, centred at (cx, cy) and
    scaled to fit a box of half-size `half` points. `pts` is an Nx2 array in
    math coordinates (y up); fitz y grows downward, so we flip it."""
    if len(pts) > max_pts:
        step = len(pts) // max_pts
        pts = pts[::step]
    xs, ys = pts[:, 0], pts[:, 1]
    w = max(float(xs.max() - xs.min()), 1e-9)
    h = max(float(ys.max() - ys.min()), 1e-9)
    s = (2 * half) / max(w, h)
    mx = (float(xs.max()) + float(xs.min())) / 2
    my = (float(ys.max()) + float(ys.min())) / 2
    poly = [fitz.Point(cx + (x - mx) * s, cy - (y - my) * s) for x, y in pts]
    page.draw_polyline(poly, color=color, width=width, closePath=False)


def _flow(page, x0, x1, y, text, fs, *, bold=False, color=(0, 0, 0),
          align=fitz.TEXT_ALIGN_LEFT, bottom=765.0, gap=4.0):
    """Lay out a paragraph in [x0,x1] starting at `y`; return the new y just
    below it. Uses insert_textbox's leftover-height return to advance exactly."""
    h = bottom - y
    leftover = _embed_textbox(page, fitz.Rect(x0, y, x1, y + h), text, fs,
                              bold=bold, align=align, color=color)
    used = (h - leftover) if leftover >= 0 else h
    return y + used + gap


def _cardioid_pts(scale=2.6, points=1400):
    import numpy as np
    t = np.linspace(0, 2 * np.pi, points)
    x = scale * (2 * np.cos(t) - np.cos(2 * t))
    y = scale * (2 * np.sin(t) - np.sin(2 * t))
    return np.column_stack([x, y])


def add_math_page(doc: fitz.Document, spec: BookSpec):
    """Appendix page: the curve families and their equations, each with a
    tiny line-art icon traced from the very functions used in the book."""
    import numpy as np
    from generate_one_per_family import (  # noqa: E402
        rose, hypotrochoid, hypocycloid, lissajous, lemniscate_bernoulli,
    )
    page = doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)
    x0 = spec.bleed_pt + spec.safety_pt
    x1 = spec.page_w_pt - spec.bleed_pt - spec.safety_pt
    GRAY = (0.45, 0.45, 0.45)
    EQ = (0.20, 0.20, 0.20)
    HAIR = (0.85, 0.85, 0.85)

    _embed_textbox(page, fitz.Rect(x0, 66, x1, 104),
                   "The Mathematics Behind the Art", 21, bold=True)
    _embed_textbox(page, fitz.Rect(x0, 108, x1, 150),
                   "Every page in this book is the exact trace of a real "
                   "mathematical curve. Here are the families you have been "
                   "colouring.", 11.5, color=GRAY)
    page.draw_line(fitz.Point(x0, 162), fitz.Point(x1, 162),
                   color=GRAY, width=0.8)

    rows = [
        ("Lissajous figure", "x = A·sin(a·t + δ)  "
         "y = B·sin(b·t)",
         "Two perpendicular vibrations. The frequency ratio a : b decides how "
         "the ribbon weaves and knots.",
         lissajous(7.5, 9.5, 3, 2, np.pi / 2)),
        ("Polar rose", "r = a·cos(k·θ)",
         "Petals open around the centre; the integer k sets how many bloom.",
         rose(k=5, a=7.0)),
        ("Spirograph (hypotrochoid)",
         "x = (R−r)cos t + d·cos(((R−r)/r)·t)",
         "The path of a point fixed inside a small wheel rolling around the "
         "inside of a ring.",
         hypotrochoid(R=8, r=3, d=5)),
        ("Hypocycloid", "x = (R−r)cos t + r·cos(((R−r)/r)·t)",
         "A wheel rolling inside a circle carves crisp, cusped stars.",
         hypocycloid(R=5, r=2)),
        ("Lemniscate of Bernoulli", "r² = a²·cos(2θ)",
         "The elegant figure-eight — the mathematical infinity sign.",
         lemniscate_bernoulli(a=7.0)),
        ("Cardioid", "r = a·(1 − cos θ)",
         "A heart traced by one circle rolling around another the same size.",
         _cardioid_pts(2.6)),
    ]
    top, bot = 180.0, 738.0
    row_h = (bot - top) / len(rows)
    icon_cx = x0 + 40
    text_x = x0 + 96
    for i, (name, eq, desc, pts) in enumerate(rows):
        cy = top + row_h * i + row_h / 2
        _draw_curve_icon(page, np.asarray(pts), icon_cx, cy, 33, width=0.7)
        ty = top + row_h * i + 8
        ty = _flow(page, text_x, x1, ty, name, 13.5, bold=True, gap=3)
        ty = _flow(page, text_x, x1, ty, eq, 11.5, color=EQ, gap=4)
        _flow(page, text_x, x1, ty, desc, 10, color=GRAY)
        if i < len(rows) - 1:
            ly = top + row_h * (i + 1)
            page.draw_line(fitz.Point(text_x, ly - 4),
                           fitz.Point(x1, ly - 4), color=HAIR, width=0.5)

    _embed_textbox(page, fitz.Rect(x0, 752, x1, 768),
                   "mathrelaxing.store", 9, color=GRAY)
    return page


def add_tips_page(doc: fitz.Document, spec: BookSpec):
    """How-to page: colouring tips and media recommendations tuned to the
    book's actual paper (60# / 90 gsm uncoated white)."""
    import numpy as np
    from generate_one_per_family import lemniscate_bernoulli  # noqa: E402
    page = doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)
    x0 = spec.bleed_pt + spec.safety_pt
    x1 = spec.page_w_pt - spec.bleed_pt - spec.safety_pt
    GRAY = (0.45, 0.45, 0.45)
    BODY = (0.20, 0.20, 0.20)

    _embed_textbox(page, fitz.Rect(x0, 66, x1, 104),
                   "How to Colour This Book", 21, bold=True)
    _embed_textbox(page, fitz.Rect(x0, 108, x1, 150),
                   "Your paper: 60# (90 gsm) uncoated white — a smooth, "
                   "lightly textured matte sheet that loves dry media.",
                   11.5, color=GRAY)
    page.draw_line(fitz.Point(x0, 162), fitz.Point(x1, 162),
                   color=GRAY, width=0.8)

    sections = [
        ("Best choice — Coloured pencils",
         "Wax- or oil-based pencils are ideal on this paper. Build colour from "
         "light to dark in thin layers, then burnish with a colourless blender "
         "or a pale pencil for a smooth, even finish."),
        ("Excellent — Fineliners & gel pens",
         "Use fine tips (0.3–0.5 mm) for the smallest regions. Let the ink "
         "settle for a moment before resting your hand so it doesn't smudge. "
         "Metallic and white gel pens shine for highlights."),
        ("Use with care — Markers",
         "Alcohol- and water-based markers will bleed through a 90 gsm sheet. "
         "Slip a spare sheet of paper behind the page you're working on and "
         "colour one side at a time."),
        ("Better to avoid — Wet media",
         "Watercolour, gouache and heavy washes soak and buckle thin paper. If "
         "you love paint, photocopy the design onto thick card stock first."),
    ]
    y = 184.0
    for head, body in sections:
        y = _flow(page, x0, x1, y, head, 13.5, bold=True, gap=3)
        y = _flow(page, x0, x1, y, body, 11, color=BODY, gap=16)

    page.draw_line(fitz.Point(x0, y + 2), fitz.Point(x1, y + 2),
                   color=(0.85, 0.85, 0.85), width=0.5)
    y += 18
    y = _flow(page, x0, x1, y, "A few gentle reminders", 13.5, bold=True, gap=6)
    bullets = (
        "•  Rest your hand on a scrap sheet to keep the page clean.\n"
        "•  Colour in good, natural light to judge your tones.\n"
        "•  Start at the centre and work outward to avoid smudging.\n"
        "•  There is no wrong way — the point is to slow down and relax."
    )
    y = _flow(page, x0, x1, y, bullets, 11, color=BODY, gap=10)

    # small infinity motif as a closing ornament, centred
    icon = lemniscate_bernoulli(a=7.0)
    _draw_curve_icon(page, np.asarray(icon), (x0 + x1) / 2, min(y + 40, 724),
                     26, width=0.9, color=(0.55, 0.55, 0.55))
    _embed_textbox(page, fitz.Rect(x0, 752, x1, 768),
                   "mathrelaxing.store", 9, color=GRAY)
    return page


def build_interior_pdf(page_pdf_paths: list, out_path: str, spec: BookSpec, *,
                       front_matter: bool = True,
                       blank_after_each: bool = False,
                       tips_page: bool = True,
                       math_page: bool = True) -> dict:
    """Merge the per-page vector PDFs into one Lulu interior PDF.

    Each source page is placed (vector-preserving) onto a trim+bleed canvas,
    scaled to fit. Title + copyright pages are prepended. The final page count
    is padded to an even number (required for perfect binding)."""
    doc = fitz.open()

    if front_matter:
        _add_text_page(doc, spec, [
            ("", 30, False),
            (spec.title, 30, True),
            ("", 15, False),
            (spec.subtitle, 15, False),
            ("", 14, False), ("", 14, False),
            (spec.author, 14, True),
        ])
        year = time.strftime("%Y")
        _add_text_page(doc, spec, [
            ("", 11, False), ("", 11, False), ("", 11, False), ("", 11, False),
            (f"(c) {year} {spec.author}", 11, False),
            ("mathrelaxing.store", 11, True),
            ("", 9, False),
            ("All rights reserved. No part of this book may be reproduced "
             "without written permission from the publisher.", 9, False),
            ("", 9, False),
            ("First edition", 9, False),
            ("ISBN: ___-_-_____-___-_", 9, False),
        ])

    if tips_page:
        add_tips_page(doc, spec)

    for src_path in page_pdf_paths:
        src = fitz.open(src_path)
        sp = src[0]
        page = doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)
        box = fitz.Rect(0, 0, spec.page_w_pt, spec.page_h_pt)  # full bleed page
        target = _fit_rect(sp.rect.width, sp.rect.height, box)
        page.show_pdf_page(target, src, 0)
        src.close()
        if blank_after_each:
            doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)

    if math_page:
        add_math_page(doc, spec)

    if doc.page_count % 2 != 0:  # perfect binding needs even pages
        doc.new_page(width=spec.page_w_pt, height=spec.page_h_pt)

    page_count = doc.page_count
    doc.save(out_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return {"path": out_path, "page_count": page_count,
            "page_size_in": (round(spec.page_w_pt / 72, 3),
                             round(spec.page_h_pt / 72, 3))}


# Cover theme (dark, premium; the colorful mandala pops on it)
COVER_TOP = (0.122, 0.094, 0.204)   # deep indigo  #1F1834
COVER_BOT = (0.302, 0.165, 0.353)   # plum         #4D2A5A
COVER_GOLD = (0.902, 0.722, 0.361)  # warm gold    #E6B85C
COVER_WHITE = (1.0, 1.0, 1.0)
COVER_LAV = (0.847, 0.804, 0.922)   # light lavender
COVER_LOGO = os.path.join(_ROOT, "assets", "img", "logo.png")


def build_cover_pdf(out_path: str, spec: BookSpec, page_count: int,
                    client: LuluClient, *, featured_png: Optional[str] = None,
                    gallery_pngs: Optional[list] = None,
                    bg=None) -> dict:
    """Build a full-color 'hero' cover spread using Lulu's authoritative
    cover-dimensions. Layout = [back | spine | front].

    Design: dark gradient field across the whole spread; a vivid stained-glass
    mandala (cover_hero) full-bleed on the FRONT with the title above it; on
    the BACK a blurb plus a 3-up gallery of colored sample pages.
    """
    import cover_hero
    from PIL import Image

    dims = client.cover_dimensions(spec.pod_package_id, page_count, unit="pt")
    total_w = float(dims["width"])
    total_h = float(dims["height"])

    panel_w = (spec.trim_w_in + spec.bleed_in) * PT_PER_IN   # one outer panel
    spine_w = max(0.0, total_w - 2 * panel_w)

    bleed = spec.bleed_pt
    safety = spec.safety_pt

    back_box = fitz.Rect(0, 0, panel_w, total_h)
    front_box = fitz.Rect(panel_w + spine_w, 0, total_w, total_h)

    # --- generate raster assets (embedded into the PDF, then deleted) -------
    tmp = os.path.join(HERE, "_cover_tmp")
    os.makedirs(tmp, exist_ok=True)
    grad_png = os.path.join(tmp, "grad.png")
    patt_png = os.path.join(tmp, "patt.png")
    hero_png = os.path.join(tmp, "hero.png")
    cover_hero.make_gradient(grad_png, int(total_w / 72 * 300),
                             int(total_h / 72 * 300), COVER_TOP, COVER_BOT)
    cover_hero.make_pattern(patt_png, total_w / 72, total_h / 72, dpi=200)
    hero_side_in = (front_box.width / PT_PER_IN) + 0.5   # bleed overflow
    cover_hero.render_hero(hero_png, hero_side_in, dpi=300, min_area=0.005)

    doc = fitz.open()
    page = doc.new_page(width=total_w, height=total_h)

    # background gradient + faint pattern texture across the whole spread
    page.insert_image(fitz.Rect(0, 0, total_w, total_h), filename=grad_png)
    page.insert_image(fitz.Rect(0, 0, total_w, total_h), filename=patt_png,
                      keep_proportion=False, overlay=True)

    # =====================  FRONT  =====================
    # hero mandala — square, centered low on the front so it bleeds off edges
    hs = hero_side_in * PT_PER_IN
    hcx = front_box.x0 + front_box.width / 2 + 0.18 * PT_PER_IN  # bias to outer edge
    hcy = total_h * 0.645
    page.insert_image(fitz.Rect(hcx - hs / 2, hcy - hs / 2, hcx + hs / 2,
                                hcy + hs / 2), filename=hero_png,
                      keep_proportion=True, overlay=True)

    fx0 = front_box.x0 + safety
    fx1 = front_box.x1 - bleed - safety
    # title — Cinzel engraved caps (auto-uppercased + tracked for impact)
    title_txt = spec.title.upper()
    _embed_textbox(page, fitz.Rect(fx0, total_h * 0.048, fx1, total_h * 0.210),
                   title_txt, 30, color=COVER_WHITE,
                   fontname="cinzel", fontfile=FONT_TITLE)
    # gold rule under the title
    ry = total_h * 0.227
    rcx = (fx0 + fx1) / 2
    page.draw_line(fitz.Point(rcx - 54, ry), fitz.Point(rcx + 54, ry),
                   color=COVER_GOLD, width=1.6)
    _embed_textbox(page, fitz.Rect(fx0, total_h * 0.238, fx1, total_h * 0.288),
                   spec.subtitle, 14.5, color=COVER_LAV)

    # =====================  BACK  =====================
    bx0 = back_box.x0 + bleed + safety
    bx1 = back_box.x1 - safety
    bcx = (bx0 + bx1) / 2
    _embed_textbox(page, fitz.Rect(bx0, total_h * 0.085, bx1, total_h * 0.125),
                   "50 UNIQUE MATHEMATICAL DESIGNS", 12, bold=True,
                   color=COVER_GOLD)
    _embed_textbox(page, fitz.Rect(bx0, total_h * 0.16, bx1, total_h * 0.40),
                   spec.blurb, 12.5, align=fitz.TEXT_ALIGN_LEFT,
                   color=COVER_LAV)
    # 3-up gallery of colored sample pages
    gallery_pngs = gallery_pngs or []
    gallery_pngs = [p for p in gallery_pngs if p and os.path.exists(p)][:3]
    if gallery_pngs:
        n = len(gallery_pngs)
        gap = 12
        avail = (bx1 - bx0) - gap * (n - 1)
        tw = avail / n
        iw, ih = Image.open(gallery_pngs[0]).size
        th = tw * (ih / iw)
        gy0 = total_h * 0.50
        for i, gp in enumerate(gallery_pngs):
            gx0 = bx0 + i * (tw + gap)
            frame = fitz.Rect(gx0 - 2, gy0 - 2, gx0 + tw + 2, gy0 + th + 2)
            page.draw_rect(frame, color=None, fill=COVER_WHITE, fill_opacity=0.9)
            page.insert_image(fitz.Rect(gx0, gy0, gx0 + tw, gy0 + th),
                              filename=gp, keep_proportion=True, overlay=True)

    # =====================  BOTTOM BAND (logo strip)  =====================
    band_h = 1.6 * PT_PER_IN
    band_top = total_h - band_h
    page.draw_rect(fitz.Rect(0, band_top, total_w, total_h),
                   color=None, fill=(0, 0, 0))
    page.draw_line(fitz.Point(0, band_top), fitz.Point(total_w, band_top),
                   color=COVER_GOLD, width=1.2)
    lcy = total_h - 0.95 * PT_PER_IN  # logo/brand vertical center (within safety)
    # logo centered on the FRONT half of the band
    lw_px, lh_px = Image.open(COVER_LOGO).size
    logo_h = 0.82 * PT_PER_IN
    logo_w = logo_h * (lw_px / lh_px)
    lcx = front_box.x0 + front_box.width / 2
    page.insert_image(fitz.Rect(lcx - logo_w / 2, lcy - logo_h / 2,
                                lcx + logo_w / 2, lcy + logo_h / 2),
                      filename=COVER_LOGO, keep_proportion=True, overlay=True)
    # site URL centered on the BACK half of the band.
    # NOTE: insert_textbox silently draws nothing (returns < 0) if the line
    # doesn't fit, so give it a generously tall rect and verify the return.
    url_fs = 13
    url_rect = fitz.Rect(back_box.x0, lcy - url_fs, back_box.x1, lcy + url_fs)
    rv = _embed_textbox(page, url_rect, "mathrelaxing.store", url_fs,
                        bold=True, color=COVER_WHITE)
    if rv < 0:
        # fallback: draw a single baseline-anchored string, horizontally centered
        tw = fitz.get_text_length("mathrelaxing.store", fontname="djvb",
                                   fontsize=url_fs)
        bx_mid = (back_box.x0 + back_box.x1) / 2
        page.insert_text(fitz.Point(bx_mid - tw / 2, lcy + url_fs * 0.35),
                         "mathrelaxing.store", fontsize=url_fs,
                         fontname="djvb", fontfile=FONT_BOLD, color=COVER_WHITE)

    # =====================  SPINE  =====================
    if spine_w >= 0.25 * PT_PER_IN:
        sx = panel_w
        _embed_textbox(
            page, fitz.Rect(sx, total_h * 0.30, sx + spine_w, total_h * 0.70),
            f"{spec.title}   -   {spec.author}",
            min(11, spine_w * 0.45), bold=True, rotate=90, color=COVER_WHITE)

    doc.save(out_path, garbage=4, deflate=True, clean=True)
    doc.close()
    # clean temp raster assets (already embedded in the PDF)
    for f in (grad_png, patt_png, hero_png):
        if os.path.exists(f):
            os.remove(f)
    try:
        os.rmdir(tmp)
    except OSError:
        pass
    return {"path": out_path, "spread_pt": (total_w, total_h),
            "spread_in": (round(total_w / 72, 3), round(total_h / 72, 3)),
            "spine_in": round(spine_w / 72, 4), "page_count": page_count}


# ---------------------------------------------------------------------------
# Hosting (Lulu fetches files from a public URL)
# ---------------------------------------------------------------------------
def publish_to_downloads(local_path: str, prefix: str = "lulu") -> str:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    slug = f"{prefix}-{secrets.token_hex(8)}.pdf"
    dst = os.path.join(DOWNLOADS_DIR, slug)
    with open(local_path, "rb") as r, open(dst, "wb") as w:
        w.write(r.read())
    os.chmod(dst, 0o644)
    return f"{DOWNLOADS_URL}/{slug}"


def md5sum(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ordered_page_pdfs() -> list:
    """The 50 coloring pages in book order: L01..L16, R01..R12, H01..H14, X01..X08."""
    out = []
    for fam in ("L", "R", "H", "X"):
        out += sorted(glob.glob(os.path.join(BOOK, f"page_{fam}*.pdf")))
    return out


def make_client(sandbox: Optional[bool] = None) -> LuluClient:
    """If `sandbox` is None, fall back to the .env LULU_SANDBOX flag
    (default sandbox). An explicit True/False always wins."""
    env = load_env()
    if sandbox is None:
        sandbox = env.get("LULU_SANDBOX", "1") == "1"
    return LuluClient(env.get("LULU_CLIENT_KEY"), env.get("LULU_CLIENT_SECRET"),
                      sandbox=sandbox)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _cmd_build(args):
    spec = PRESETS[args.preset]
    pages = ordered_page_pdfs()
    print(f"interior: {len(pages)} coloring pages, preset={args.preset} "
          f"({spec.pod_package_id})")
    interior = os.path.join(HERE, "lulu_interior.pdf")
    info = build_interior_pdf(pages, interior, spec,
                              blank_after_each=args.blank_backs)
    print("  ->", info)
    client = make_client(sandbox=False if args.prod else None)
    cover = os.path.join(HERE, "lulu_cover.pdf")
    gallery = [
        os.path.join(BOOK, "page_R03_Rosa_plus_spirograph_colored.png"),
        os.path.join(BOOK, "page_H01_Hipocicloides_colored.png"),
        os.path.join(BOOK, "page_X02_Exoticas_colored.png"),
    ]
    cinfo = build_cover_pdf(cover, spec, info["page_count"], client,
                            gallery_pngs=gallery)
    print("  ->", cinfo)


def _cmd_token(args):
    client = make_client(sandbox=False if args.prod else None)
    tok = client.token()
    print(f"OK ({'sandbox' if client.sandbox else 'PROD'}): token len={len(tok)}")


def _cmd_quote(args):
    spec = PRESETS[args.preset]
    client = make_client(sandbox=False if args.prod else None)
    # page count from a freshly built interior if present
    interior = os.path.join(HERE, "lulu_interior.pdf")
    pc = fitz.open(interior).page_count if os.path.exists(interior) else 52
    dims = client.cover_dimensions(spec.pod_package_id, pc)
    print("cover-dimensions:", dims)
    addr = {"name": "Test", "street1": "101 Independence Ave SE",
            "city": "Washington", "state_code": "DC", "postcode": "20540",
            "country_code": "US", "phone_number": "+1 202 555 0100"}
    cost = client.cost_calculation(
        [{"page_count": pc, "pod_package_id": spec.pod_package_id, "quantity": 1}],
        addr, shipping_level="MAIL")
    print("cost:", json.dumps(cost, indent=2)[:1500])


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Lulu POD automation")
    ap.add_argument("--prod", action="store_true", help="use production (default sandbox)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build interior + cover PDFs")
    b.add_argument("--preset", default="letter_bw_pb", choices=list(PRESETS))
    b.add_argument("--no-blank-backs", dest="blank_backs", action="store_false",
                   help="skip the blank page after each coloring page (on by "
                        "default, so marker/pen ink doesn't bleed onto the next design)")
    b.set_defaults(blank_backs=True)
    b.set_defaults(func=_cmd_build)

    t = sub.add_parser("token", help="test OAuth token")
    t.set_defaults(func=_cmd_token)

    q = sub.add_parser("quote", help="cover-dimensions + cost calculation")
    q.add_argument("--preset", default="letter_bw_pb", choices=list(PRESETS))
    q.set_defaults(func=_cmd_quote)

    args = ap.parse_args()
    args.func(args)
