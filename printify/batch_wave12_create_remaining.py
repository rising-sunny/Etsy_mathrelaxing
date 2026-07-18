"""Create remaining bauhaus poster + 2 magnets (fourier/euler/wave/mandelbrot already done)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_wave12_create import (  # noqa: E402
    GROUPS,
    MAG_DIR,
    OUT_JSON,
    POSTER_PRICES,
    create_magnet,
    create_multi_poster,
    make_square_magnet_art,
)
import printify_publish as pp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# already created posters
DONE = [
    {"type": "poster", "key": "fourier", "printify_id": "6a5bf0f381cebb5bdd03a737", "blueprint": 282},
    {"type": "poster", "key": "euler", "printify_id": "6a5bf105dde591a5200a7d9d", "blueprint": 282},
    {"type": "poster", "key": "wave", "printify_id": "6a5bf113dde591a5200a7da6", "blueprint": 282},
    {"type": "poster", "key": "mandelbrot", "printify_id": "6a5bf124ca82e4a6d2013421", "blueprint": 282},
]


def main():
    created = list(DONE)

    # Bauhaus
    print("\n=== POSTER: bauhaus_circles ===")
    folder = ROOT / "bauhaus_set" / "prints" / "01_circles_bars"
    files = {
        "2x3": "01_circles_bars_2x3_12x18_300dpi.jpg",
        "3x4": "01_circles_bars_3x4_12x16_300dpi.jpg",
        "4x5": "01_circles_bars_4x5_16x20_300dpi.jpg",
    }
    image_ids = {}
    for ratio, fname in files.items():
        path = folder / fname
        image_ids[ratio] = pp.upload_image(str(path), f"bauhaus_{ratio}.jpg")
    title = (
        "Bauhaus Poster | Geometric Wall Art Circles and Bars | "
        "Navy Cream Modern Math Print"
    )
    desc = (
        "Circles & Bars — a Bauhaus-inspired geometric poster from the "
        "MathRelaxing Bauhaus print set.\n\n"
        "Navy, cream, and gold balance. Strong graphic presence for living rooms, "
        "offices, and modern interiors.\n\n"
        "• Matte poster, printed on demand\n"
        "• Multiple sizes\n"
        "• Frame not included\n\n"
        "MathRelaxing — original code-drawn geometry."
    )
    tags = [
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
    ]
    prod = create_multi_poster(title, desc, image_ids, tags)
    print("  PRODUCT", prod.get("id"))
    pp.margin_report(prod)
    created.append(
        {
            "type": "poster",
            "key": "bauhaus_circles",
            "printify_id": prod.get("id"),
            "title": title,
            "blueprint": 282,
        }
    )

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
                "Computed from z to z squared plus c. Available in 3, 4, and 6 inch. "
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
                "Sizes 3, 4, 6 inch. Printed on demand.\n\n"
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
        art = make_square_magnet_art(m["src"], MAG_DIR / f"{m['key']}.png", m["label"])
        img_id = pp.upload_image(str(art), f"{m['key']}.png")
        prod = create_magnet(m["title"], m["desc"], img_id, m["tags"])
        print("  PRODUCT", prod.get("id"))
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
    print("\n=== DONE (Printify only — NOT on Etsy) ===")
    for c in created:
        print(f"  [{c['type']:6}] {c['printify_id']}  {c['key']}")
    print("Saved", OUT_JSON)


if __name__ == "__main__":
    main()
