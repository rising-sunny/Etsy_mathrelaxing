"""
batch_wave12_create.py — Create Printify products (NO Etsy publish).

5 scientific posters (bp 282) + 2 magnets (bp 428).
Art from equation_plates / bauhaus / square crops for magnets.

  python printify/batch_wave12_create.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import printify_publish as pp  # noqa: E402

OUT_JSON = HERE / "wave12_created_products.json"
MAG_DIR = HERE / "_magnet_art"
MAG_DIR.mkdir(exist_ok=True)

# Poster retail (cents) — same as wallart_set/publish_posters.py
POSTER_PRICES = {
    43135: 1500,   # 11x14
    101110: 1800,  # 12x16
    43138: 1800,   # 12x18
    43141: 2400,   # 16x20
    101113: 2400,  # 16x24
    43144: 2600,   # 18x24
    43147: 3200,   # 20x30
    43150: 3900,   # 24x36
    101118: 5900,  # 30x40
}
# ratio group -> variant ids
GROUPS = {
    "2x3": [43138, 101113, 43147, 43150],
    "3x4": [101110, 43144, 101118],
    "4x5": [43141, 43135],
}

MAGNET_PRICES = {62034: 899, 62035: 1199, 62036: 1599}  # 3/4/6 in
BLUEPRINT_MAGNET = 428
PROVIDER_SPOKE = 1


def make_square_magnet_art(src: Path, dest: Path, label: str, size: int = 1800) -> Path:
    """Center-crop to square and add small cream label band (readable at 3in)."""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    sq = im.crop((left, top, left + side, top + side)).resize(
        (size, size), Image.Resampling.LANCZOS
    )
    # bottom label strip
    draw = ImageDraw.Draw(sq)
    band_h = int(size * 0.11)
    y0 = size - band_h
    draw.rectangle([0, y0, size, size], fill=(244, 241, 234))
    try:
        font = ImageFont.truetype("arial.ttf", size // 28)
        font_s = ImageFont.truetype("arial.ttf", size // 40)
    except OSError:
        font = ImageFont.load_default()
        font_s = font
    draw.text((size // 2, y0 + band_h // 2 - 8), label, font=font, fill=(26, 26, 26), anchor="mm")
    draw.text(
        (size // 2, y0 + band_h // 2 + 18),
        "MathRelaxing",
        font=font_s,
        fill=(184, 92, 56),
        anchor="mm",
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    sq.save(dest, "PNG", optimize=True)
    print(f"  magnet art {dest.name} {size}x{size}")
    return dest


def create_multi_poster(title, description, image_ids: dict, tags: list):
    variants = [
        {"id": vid, "price": p, "is_enabled": True} for vid, p in POSTER_PRICES.items()
    ]
    print_areas = []
    for ratio, vids in GROUPS.items():
        if ratio not in image_ids:
            continue
        print_areas.append(
            {
                "variant_ids": vids,
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_ids[ratio],
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0,
                            }
                        ],
                    }
                ],
            }
        )
    payload = {
        "title": title,
        "description": description,
        "blueprint_id": pp.BLUEPRINT_MATTE,
        "print_provider_id": pp.PROVIDER_CHOICE,
        "variants": variants,
        "print_areas": print_areas,
        "tags": tags[:13],
    }
    return pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)


def create_magnet(title, description, image_id, tags: list):
    variants = [
        {"id": vid, "price": p, "is_enabled": True} for vid, p in MAGNET_PRICES.items()
    ]
    payload = {
        "title": title,
        "description": description,
        "blueprint_id": BLUEPRINT_MAGNET,
        "print_provider_id": PROVIDER_SPOKE,
        "variants": variants,
        "print_areas": [
            {
                "variant_ids": list(MAGNET_PRICES.keys()),
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0,
                            }
                        ],
                    }
                ],
            }
        ],
        "tags": tags[:13],
    }
    return pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)


POSTERS = [
    {
        "key": "fourier",
        "folder": ROOT / "equation_plates" / "fourier_series" / "prints",
        "prefix": "fourier_series",
        "title": (
            "Fourier Series Poster | Math Wall Art Scientific Plate | "
            "Square Wave Harmonics STEM Print"
        ),
        "desc": (
            "The Shape of Waves — a scientific-plate poster of Fourier series "
            "building a square wave from pure sinusoids.\n\n"
            "Cream graph paper, true mathematical curves, LaTeX typography. "
            "Not AI art — computed from the series equation.\n\n"
            "• Matte poster, printed on demand\n"
            "• Multiple sizes (11×14 up to 24×36)\n"
            "• Perfect for STEM classrooms, offices, and math lovers\n"
            "• Frame not included\n\n"
            "MathRelaxing — every design is written from scratch in code."
        ),
        "tags": [
            "math wall art",
            "fourier series",
            "science poster",
            "stem wall art",
            "math poster",
            "educational poster",
            "physics wall art",
            "classroom decor",
            "nerd gift",
            "geometric wall art",
            "minimalist poster",
            "office wall art",
            "teacher gift",
        ],
    },
    {
        "key": "euler",
        "folder": ROOT / "equation_plates" / "euler_identity" / "prints",
        "prefix": "euler_identity",
        "title": (
            "Euler Identity Poster | Math Wall Art | e to the i pi Complex Plane "
            "STEM Scientific Print"
        ),
        "desc": (
            "The Most Beautiful Equation — Euler's identity on the complex unit circle.\n\n"
            "Scientific-plate wall art with cream graph paper and precise geometry. "
            "A classic gift for mathematicians, students, and teachers.\n\n"
            "• Matte poster, printed on demand\n"
            "• Multiple sizes\n"
            "• Frame not included\n\n"
            "MathRelaxing — code-drawn mathematics for your walls."
        ),
        "tags": [
            "math wall art",
            "euler identity",
            "complex numbers",
            "math poster",
            "stem wall art",
            "science poster",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "minimalist poster",
            "office wall art",
            "teacher gift",
            "mathematics art",
        ],
    },
    {
        "key": "wave",
        "folder": ROOT / "equation_plates" / "wave_equation" / "prints",
        "prefix": "wave_equation",
        "title": (
            "Wave Equation Poster | Physics Wall Art | Standing Waves on a String "
            "STEM Science Print"
        ),
        "desc": (
            "The Traveling Wave — the one-dimensional wave equation with standing-wave "
            "modes n = 1, 2, 3.\n\n"
            "Scientific-plate style: cream graph paper, dual panels for displacement "
            "and intensity, true physics curves.\n\n"
            "• Matte poster, printed on demand\n"
            "• Multiple sizes\n"
            "• Frame not included\n\n"
            "MathRelaxing — physics drawn from the equations."
        ),
        "tags": [
            "physics wall art",
            "wave equation",
            "science poster",
            "stem wall art",
            "physics poster",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "math wall art",
            "office wall art",
            "teacher gift",
            "standing waves",
            "minimalist poster",
        ],
    },
    {
        "key": "mandelbrot",
        "folder": ROOT / "equation_plates" / "mandelbrot_set" / "prints",
        "prefix": "mandelbrot_set",
        "title": (
            "Mandelbrot Set Poster | Math Wall Art Fractal | Chaos Theory "
            "Scientific Plate STEM Print"
        ),
        "desc": (
            "The Geometry of Chaos — Mandelbrot set as a scientific plate "
            "(cream / ink / rust, not neon fractal kitsch).\n\n"
            "Smooth escape-time portrait of z → z² + c. Perfect for coders, "
            "math lovers, and modern STEM walls.\n\n"
            "• Matte poster, printed on demand\n"
            "• Multiple sizes\n"
            "• Frame not included\n\n"
            "MathRelaxing — every design is computed in Python."
        ),
        "tags": [
            "math wall art",
            "mandelbrot set",
            "fractal art",
            "chaos theory",
            "math poster",
            "stem wall art",
            "science poster",
            "generative art",
            "nerd gift",
            "classroom decor",
            "office wall art",
            "minimalist poster",
            "teacher gift",
        ],
    },
    {
        "key": "bauhaus_circles",
        "folder": ROOT / "bauhaus_set" / "prints" / "01_circles_bars",
        "prefix": "01_circles_bars",
        "ratios": {
            "2x3": "01_circles_bars_2x3_12x18_300dpi.jpg",
            "3x4": "01_circles_bars_3x4_12x16_300dpi.jpg",
            "4x5": "01_circles_bars_4x5_16x20_300dpi.jpg",
        },
        "title": (
            "Bauhaus Poster | Geometric Wall Art Circles and Bars | "
            "Navy Cream Modern Math Print"
        ),
        "desc": (
            "Circles & Bars — a Bauhaus-inspired geometric poster from the "
            "MathRelaxing Bauhaus print set.\n\n"
            "Navy, cream, and gold balance. Strong graphic presence for living rooms, "
            "offices, and modern interiors.\n\n"
            "• Matte poster, printed on demand\n"
            "• Multiple sizes\n"
            "• Frame not included\n\n"
            "MathRelaxing — original code-drawn geometry."
        ),
        "tags": [
            "bauhaus poster",
            "geometric wall art",
            "math wall art",
            "minimalist poster",
            "modern wall art",
            "abstract poster",
            "office wall art",
            "navy cream art",
            "scandinavian art",
            "stem wall art",
            "line art print",
            "mid century modern",
            "teacher gift",
        ],
    },
]


def main():
    created = []

    # ── Posters ────────────────────────────────────────────────────────────
    for p in POSTERS:
        print(f"\n=== POSTER: {p['key']} ===")
        assert len(p["title"]) <= 140, f"title too long {len(p['title'])}"
        image_ids = {}
        if "ratios" in p:
            for ratio, fname in p["files"].items():
                path = p["folder"] / fname
                if not path.exists():
                    raise FileNotFoundError(path)
                image_ids[ratio] = pp.upload_image(str(path), f"{p['key']}_{ratio}.jpg")
        else:
            for ratio in ("2x3", "3x4", "4x5"):
                path = p["folder"] / f"{p['prefix']}_{ratio}_300dpi.jpg"
                if not path.exists():
                    raise FileNotFoundError(path)
                image_ids[ratio] = pp.upload_image(str(path), f"{p['key']}_{ratio}.jpg")
        prod = create_multi_poster(p["title"], p["desc"], image_ids, p["tags"])
        print(f"  PRODUCT {prod.get('id')}")
        pp.margin_report(prod)
        created.append(
            {
                "type": "poster",
                "key": p["key"],
                "printify_id": prod.get("id"),
                "title": p["title"],
                "blueprint": 282,
            }
        )

    # ── Magnets (2 new; Amethyst Julia already exists) ─────────────────────
    magnets = [
        {
            "key": "mandelbrot_magnet",
            "src": ROOT
            / "equation_plates"
            / "mandelbrot_set"
            / "prints"
            / "mandelbrot_set_2x3_300dpi.jpg",
            "label": "MANDELBROT SET",
            "title": (
                "Mandelbrot Fractal Fridge Magnet | Math Art | Chaos Theory "
                "Science Gift STEM Decor"
            ),
            "desc": (
                "A Mandelbrot-set fridge magnet — scientific cream/ink/rust palette, "
                "not neon fractal kitsch.\n\n"
                "Computed from z → z² + c. Available in 3\", 4\", and 6\". "
                "Printed on demand and shipped to you.\n\n"
                "MathRelaxing — mathematics made visible."
            ),
            "tags": [
                "math magnet",
                "fractal art",
                "mandelbrot set",
                "fridge magnet",
                "science gift",
                "stem gift",
                "math art",
                "chaos theory",
                "teacher gift",
                "nerd gift",
                "geometric magnet",
                "office decor",
                "science magnet",
            ],
        },
        {
            "key": "euler_magnet",
            "src": ROOT
            / "equation_plates"
            / "euler_identity"
            / "prints"
            / "euler_identity_2x3_300dpi.jpg",
            "label": "EULER IDENTITY",
            "title": (
                "Euler Identity Fridge Magnet | Math Art Complex Plane | "
                "STEM Science Gift Teacher"
            ),
            "desc": (
                "Euler's identity on a fridge magnet — the most beautiful equation "
                "for your kitchen, locker, or office cabinet.\n\n"
                "Scientific-plate design, cream graph paper aesthetic. "
                "Sizes 3\", 4\", 6\". Printed on demand.\n\n"
                "MathRelaxing — code-drawn math gifts."
            ),
            "tags": [
                "math magnet",
                "euler identity",
                "fridge magnet",
                "science gift",
                "stem gift",
                "math art",
                "teacher gift",
                "nerd gift",
                "complex numbers",
                "science magnet",
                "office decor",
                "math teacher gift",
                "physics gift",
            ],
        },
    ]

    for m in magnets:
        print(f"\n=== MAGNET: {m['key']} ===")
        assert len(m["title"]) <= 140
        art = make_square_magnet_art(m["src"], MAG_DIR / f"{m['key']}.png", m["label"])
        img_id = pp.upload_image(str(art), f"{m['key']}.png")
        prod = create_magnet(m["title"], m["desc"], img_id, m["tags"])
        print(f"  PRODUCT {prod.get('id')}")
        pp.margin_report(prod)
        created.append(
            {
                "type": "magnet",
                "key": m["key"],
                "printify_id": prod.get("id"),
                "title": m["title"],
                "blueprint": 428,
            }
        )

    OUT_JSON.write_text(json.dumps(created, indent=2), encoding="utf-8")
    print("\n=== DONE (Printify only — NOT published to Etsy) ===")
    for c in created:
        print(f"  [{c['type']:6}] {c['printify_id']}  {c['key']}")
    print(f"\nSaved {OUT_JSON}")
    print("Open Printify → My Etsy Store to review mockups.")
    print("Publish to Etsy only after review (use publish_product).")


if __name__ == "__main__":
    main()
