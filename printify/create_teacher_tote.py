"""
create_teacher_tote.py — STEM Math Teacher tote for Back-to-School (Printify POD)

Blueprint: 5113 Matte Carryall Tote (Port Authority) · provider 217 Fulfill Engine · DTF
Print area: front_dtf 1800×1800 px

  python printify/create_teacher_tote.py art      # render artwork only
  python printify/create_teacher_tote.py create   # upload + create product in Printify
  python printify/create_teacher_tote.py publish <product_id>  # push to Etsy (confirm first)

Does NOT publish to Etsy unless you pass publish.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import printify_publish as pp  # noqa: E402

OUT_DIR = os.path.join(HERE, "_tote_art")
ART_PATH = os.path.join(OUT_DIR, "math_teacher_tote_1800.png")

# Primary: classic canvas shopping tote — healthy margin for BTS.
# (Matte Carryall 5113 costs ~$37 blank; keep only if you want premium SKU.)
BLUEPRINT = 1092
PROVIDER = 41  # Duplium DTG
SIZES_PRICES = {
    81758: 3999,  # 18" x 15" canvas shopping tote @ $39.99
}
PLACEHOLDER = "front"

# Optional premium blank (high COGS ~$37 — retail must be ~$55+)
PREMIUM_BLUEPRINT = 5113
PREMIUM_PROVIDER = 217
PREMIUM_PRICES = {
    242394: 5499,  # Sahara
    242395: 5499,  # Storm Grey
    242396: 5499,  # Deep Black
}
PREMIUM_PLACEHOLDER = "front_dtf"

# SEO from eRank bulk (research/tote_seo_erank_bulk.csv, Jun 2026):
# primary = "teacher tote bag" (3300 latest / 1547 avg / mom 2.13 / KD 75)
TITLE = (
    "Teacher Tote Bag | Math Teacher Gift Canvas Tote | "
    "STEM Classroom Bag | Back to School Teacher Gift"
)  # 99 chars — exact primary keyword front-loaded
DESC = (
    "Teacher tote bag for math and STEM classrooms — a sturdy canvas tote with equation art "
    "designed for back to school, everyday teaching, and math teacher gifts.\n\n"
    "This is not a generic monogram tote. The front print features MathRelaxing scientific art "
    "(Euler identity + orbital geometry), computed for a clean classroom look.\n\n"
    "WHAT YOU GET\n"
    "• Canvas shopping tote (18\" × 15\")\n"
    "• Print-on-demand — made when you order\n"
    "• Design: math teacher / STEM equation art\n\n"
    "GREAT FOR\n"
    "• Math teacher gift\n"
    "• Back to school teacher gift\n"
    "• STEM teacher / science teacher\n"
    "• Teacher appreciation (or treat yourself)\n\n"
    "MathRelaxing — math and science art written in code, not AI clipart."
)
# 13 tags, each ≤20 chars — parent demand first, then STEM differentiators
TAGS = [
    "teacher tote bag",
    "teacher tote",
    "teacher gift",
    "math teacher gift",
    "back to school",
    "teacher bag",
    "canvas tote bag",
    "math teacher",
    "stem teacher",
    "classroom bag",
    "science teacher",
    "gift for teacher",
    "stem gift",
]


def _font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_art(path: str = ART_PATH, size: int = 1800) -> str:
    """Square DTF master: cream plate + navy math + teal accent (brand family)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    S = size
    # cream paper like equation plates
    bg = (244, 241, 234)
    ink = (26, 26, 26)
    sub = (85, 85, 85)
    acc = (26, 122, 138)  # teal
    line = (200, 194, 180)
    gold = (184, 92, 56)

    im = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(im)

    # outer frame
    m = int(S * 0.055)
    d.rectangle([m, m, S - m, S - m], outline=line, width=max(2, S // 400))
    d.rectangle([m + 10, m + 10, S - m - 10, S - m - 10], outline=line, width=1)

    # header
    d.text((S // 2, int(S * 0.12)), "MATH TEACHER", font=_font(int(S * 0.055), bold=True),
           fill=ink, anchor="mm")
    d.text((S // 2, int(S * 0.175)), "STEM  ·  CLASSROOM  ·  EVERY DAY", font=_font(int(S * 0.022)),
           fill=acc, anchor="mm")
    y_line = int(S * 0.205)
    d.line([(int(S * 0.18), y_line), (int(S * 0.82), y_line)], fill=line, width=2)

    # orbital / atom-ish geometry (computed rings)
    cx, cy = S // 2, int(S * 0.42)
    r0 = int(S * 0.16)
    # soft glow disk
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, a in enumerate(range(40, 0, -4)):
        gd.ellipse([cx - r0 - i * 3, cy - r0 - i * 3, cx + r0 + i * 3, cy + r0 + i * 3],
                   fill=(26, 122, 138, a))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(im)

    # rings + orbits
    for rr, w in [(r0, 3), (int(r0 * 0.62), 2), (int(r0 * 0.28), 2)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=acc, width=w)
    # tilted ellipses
    for ang, rx, ry in [(25, 1.35, 0.45), (-35, 1.2, 0.38), (70, 1.15, 0.42)]:
        # approximate tilted ellipse with polygon
        pts = []
        for t in np.linspace(0, 2 * np.pi, 120):
            x = rx * r0 * np.cos(t)
            y = ry * r0 * np.sin(t)
            ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
            xr, yr = x * ca - y * sa, x * sa + y * ca
            pts.append((cx + xr, cy + yr))
        d.line(pts + [pts[0]], fill=ink, width=2)
    # nucleus
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=gold)

    # equation strip
    # Unicode math (avoid raw TeX braces on bag)
    d.text((S // 2, int(S * 0.62)), "e^(iπ) + 1 = 0", font=_font(int(S * 0.052), bold=True),
           fill=ink, anchor="mm")
    d.text((S // 2, int(S * 0.68)), "Euler's identity  ·  the most beautiful equation",
           font=_font(int(S * 0.02)), fill=sub, anchor="mm")

    d.line([(int(S * 0.22), int(S * 0.72)), (int(S * 0.78), int(S * 0.72))], fill=line, width=2)

    # footer badges
    badges = ["BACK TO SCHOOL", "TEACHER GIFT", "STEM"]
    bx0 = int(S * 0.18)
    gap = int(S * 0.22)
    for i, b in enumerate(badges):
        x = bx0 + i * gap
        d.rounded_rectangle([x, int(S * 0.76), x + int(S * 0.2), int(S * 0.82)],
                            radius=12, outline=acc, width=2)
        d.text((x + int(S * 0.1), int(S * 0.79)), b, font=_font(int(S * 0.016), bold=True),
               fill=acc, anchor="mm")

    d.text((S // 2, int(S * 0.88)), "M A T H R E L A X I N G", font=_font(int(S * 0.024)),
           fill=sub, anchor="mm")
    d.text((S // 2, int(S * 0.92)), "computed math art  ·  not AI clipart",
           font=_font(int(S * 0.018)), fill=line, anchor="mm")

    # slight sharpen
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))
    im.save(path, "PNG", optimize=True)
    print(f"art saved: {path}  ({S}x{S})")
    return path


def create_product(art_path: str = ART_PATH):
    # Prefer exclusive transparent design
    exclusive = os.path.join(OUT_DIR, "math_teacher_tote_exclusive_3000.png")
    if os.path.isfile(exclusive):
        art_path = exclusive
    elif not os.path.isfile(art_path):
        try:
            from render_teacher_tote_art import main as render_exclusive
            render_exclusive()
            art_path = exclusive
        except Exception:
            render_art(art_path)
    img_id = pp.upload_image(art_path, "math_teacher_tote_1800.png")
    variant_ids = list(SIZES_PRICES.keys())
    variants = [{"id": vid, "price": price, "is_enabled": True}
                for vid, price in SIZES_PRICES.items()]
    payload = {
        "title": TITLE,
        "description": DESC,
        "blueprint_id": BLUEPRINT,
        "print_provider_id": PROVIDER,
        "variants": variants,
        "print_areas": [{
            "variant_ids": variant_ids,
            "placeholders": [{
                "position": PLACEHOLDER,
                "images": [{"id": img_id, "x": 0.5, "y": 0.5, "scale": 1.0, "angle": 0}],
            }],
        }],
        "tags": TAGS,
    }
    prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
    print("PRODUCT ID:", prod.get("id"))
    print("TITLE:", prod.get("title"))
    pp.margin_report(prod)
    # save id for later
    meta = os.path.join(OUT_DIR, "last_teacher_tote.json")
    import json
    with open(meta, "w", encoding="utf-8") as f:
        json.dump({
            "product_id": prod.get("id"),
            "title": prod.get("title"),
            "blueprint_id": BLUEPRINT,
            "provider_id": PROVIDER,
            "retail_cents": SIZES_PRICES,
            "art": art_path,
        }, f, indent=2)
    print(f"meta: {meta}")
    return prod


def publish(product_id: str):
    print("Publishing to Etsy-connected shop (Printify → Etsy)…")
    res = pp.publish_product(product_id)
    print(res)
    return res


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "art"
    if cmd == "art":
        render_art()
    elif cmd == "create":
        create_product()
    elif cmd == "publish" and len(sys.argv) > 2:
        publish(sys.argv[2])
    else:
        print(__doc__)
