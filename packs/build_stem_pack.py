"""Build STEM Wall Art Pack of 10 bestsellers: one zip + listing previews."""
from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "stem_wall_art_10"
STAGE = OUT / "staging"

ITEMS = [
    ("01_Famous_Equations_Set_of_6", "equation_plates/famous_equations_set/Famous_Equations_Wall_Art_Set_of_6.zip"),
    ("02_Unit_Circle_Trigonometry", "unit_circle/Unit_Circle_Trigonometry_Wall_Art.zip"),
    ("03_Ulam_Spiral_Prime_Numbers", "wallart_set/out/concept/ulam/UlamSpiral_prints.zip"),
    ("04_Eulers_Identity", "wallart_set/out/concept/euler/EulersIdentity_prints.zip"),
    ("05_Black_Hole_Anatomy", "wallart_set/out/physics/blackhole/BlackHole_prints.zip"),
    ("06_Schrodinger_Equation", "schrodinger_equation/Schrodinger_Equation_Physics_Wall_Art.zip"),
    ("07_Platonic_Solids", "special_plates/platonic_solids/Platonic_Solids_Math_Wall_Art.zip"),
    ("08_Special_Functions_Set_of_6", "special_plates/special_functions_set/Special_Functions_Wall_Art_Set_of_6.zip"),
    ("09_Harmonic_Series_Vibrating_String", "wallart_set/out/concept/harmonic/HarmonicSeries_prints.zip"),
    ("10_Fourier_Series", "equation_plates/fourier_series/Fourier_Series_Math_Wall_Art.zip"),
]

PREVIEW_SOURCES = [
    "equation_plates/famous_equations_set/previews/famous_equations_preview_1_hero.jpg",
    "unit_circle/previews/unit_circle_preview_1_hero.jpg",
    "special_plates/platonic_solids/previews/platonic_solids_preview_1_hero.jpg",
    "wallart_set/out/concept/ulam/prints/UlamSpiral_2x3.jpg",
    "wallart_set/out/physics/blackhole/prints/BlackHole_2x3.jpg",
]


def _font(size: int):
    for path in (
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def build_zip() -> Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    STAGE.mkdir(parents=True)

    for name, rel in ITEMS:
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError(src)
        dest = STAGE / name
        dest.mkdir()
        with zipfile.ZipFile(src) as zf:
            zf.extractall(dest)
        print(f"  staged {name}")

    (STAGE / "README_MathRelaxing_STEM_Wall_Art_Pack.txt").write_text(
        """MathRelaxing — STEM Wall Art Pack (10 designs)
================================================
Thank you for purchasing this digital pack.

CONTENTS (10 folders):
1. Famous Equations — set of 6 scientific plates
2. Unit Circle — trigonometry reference poster
3. Ulam Spiral — prime numbers art print
4. Euler's Identity — complex plane art print
5. Black Hole Anatomy — Schwarzschild physics print
6. Schrödinger Equation — quantum mechanics print
7. Platonic Solids — sacred geometry poster
8. Special Functions — set of 6 scientific plates
9. Harmonic Series / Vibrating String
10. Fourier Series

Each folder contains high-resolution print-ready files (JPG/PDF as included).
Personal use only. Not for redistribution or resale of the digital files.
Shop: https://www.etsy.com/shop/TheMathRelaxing
""",
        encoding="utf-8",
    )

    zip_path = OUT / "MathRelaxing_STEM_Wall_Art_Pack_10_Designs.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in STAGE.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(STAGE).as_posix())
    print(f"ZIP {zip_path} ({zip_path.stat().st_size // 1024} KB)")
    return zip_path


def _collect_preview_images() -> list[Path]:
    imgs: list[Path] = []
    for rel in PREVIEW_SOURCES:
        p = ROOT / rel
        if p.is_file():
            imgs.append(p)
    extra_dirs = [
        ROOT / "wallart_set/out/concept/euler/prints",
        ROOT / "schrodinger_equation",
        ROOT / "special_plates/special_functions_set",
        ROOT / "wallart_set/out/concept/harmonic/prints",
        ROOT / "equation_plates/fourier_series",
    ]
    for d in extra_dirs:
        if not d.exists():
            continue
        candidates = (
            list(d.rglob("*preview*.jpg"))
            + list(d.rglob("*_2x3.jpg"))
            + list(d.rglob("*print*.jpg"))
            + list(d.rglob("*.jpg"))
        )
        for f in candidates:
            if f.is_file() and f not in imgs:
                imgs.append(f)
                break
        if len(imgs) >= 10:
            break
    return imgs[:10]


def build_previews() -> list[Path]:
    imgs = _collect_preview_images()
    print(f"  preview source images: {len(imgs)}")
    font = _font(54)
    font_s = _font(28)

    # Hero collage
    W = H = 2000
    canvas = Image.new("RGB", (W, H), (18, 18, 22))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, 220], fill=(12, 12, 16))
    draw.text((W // 2, 70), "STEM WALL ART PACK", fill=(240, 232, 210), font=font, anchor="mt")
    draw.text(
        (W // 2, 145),
        "10 digital math & physics designs  ·  MathRelaxing",
        fill=(180, 170, 150),
        font=font_s,
        anchor="mt",
    )

    cols, rows = 5, 2
    pad = 24
    top = 250
    gw = (W - pad * (cols + 1)) // cols
    gh = (H - top - pad * (rows + 1)) // rows
    while len(imgs) < 10 and imgs:
        imgs.append(imgs[-1])
    for i, path in enumerate(imgs[:10]):
        r, c = i // cols, i % cols
        x = pad + c * (gw + pad)
        y = top + pad + r * (gh + pad)
        try:
            im = Image.open(path).convert("RGB")
            im.thumbnail((gw, gh), Image.Resampling.LANCZOS)
            ox = x + (gw - im.width) // 2
            oy = y + (gh - im.height) // 2
            canvas.paste(im, (ox, oy))
        except Exception as e:
            print(f"  img err {path}: {e}")

    hero = OUT / "preview_1_hero.jpg"
    canvas.save(hero, quality=90)

    # Included list
    card = Image.new("RGB", (2000, 2000), (245, 242, 235))
    d = ImageDraw.Draw(card)
    d.text((100, 80), "What's included", fill=(30, 28, 24), font=font)
    lines = [
        "1. Famous Equations (set of 6)",
        "2. Unit Circle trigonometry poster",
        "3. Ulam Spiral prime-number art",
        "4. Euler's Identity",
        "5. Black Hole anatomy print",
        "6. Schrödinger Equation",
        "7. Platonic Solids geometry",
        "8. Special Functions (set of 6)",
        "9. Harmonic Series / vibrating string",
        "10. Fourier Series",
        "",
        "Instant download · Print-ready files",
        "Worth ~$30+ if bought separately",
        "Pack price: $16.99",
    ]
    y = 200
    for line in lines:
        d.text((120, y), line, fill=(50, 48, 44), font=font_s)
        y += 55
    included = OUT / "preview_2_included.jpg"
    card.save(included, quality=90)

    # Value card
    value = Image.new("RGB", (2000, 2000), (18, 18, 22))
    vd = ImageDraw.Draw(value)
    vd.text((W // 2, 700), "10 designs · one download", fill=(240, 232, 210), font=font, anchor="mt")
    vd.text((W // 2, 820), "$16.99 pack  vs  $30+ separate", fill=(200, 180, 120), font=font_s, anchor="mt")
    vd.text((W // 2, 920), "Math · Physics · Classroom · Office", fill=(160, 155, 145), font=font_s, anchor="mt")
    value_path = OUT / "preview_3_value.jpg"
    value.save(value_path, quality=90)

    print(f"  previews: {hero.name}, {included.name}, {value_path.name}")
    return [hero, included, value_path]


def main():
    print("Building STEM Wall Art Pack…")
    build_zip()
    build_previews()
    print("Done →", OUT)


if __name__ == "__main__":
    main()
