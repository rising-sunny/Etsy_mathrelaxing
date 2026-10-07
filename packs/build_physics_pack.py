"""Build Physics Wall Art Pack of 10: two Etsy-sized zips + listing previews."""
from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "physics_wall_art_10"
STAGE = OUT / "staging"

# Pure physics lineup (sold / high-signal + strong scientific plates)
ITEMS = [
    ("01_Maxwell_Electromagnetism", "wallart_set/out/physics/maxwell/Electromagnetism_prints.zip"),
    ("02_Schrodinger_Equation", "schrodinger_equation/Schrodinger_Equation_Physics_Wall_Art.zip"),
    ("03_Black_Hole_Anatomy", "wallart_set/out/physics/blackhole/BlackHole_prints.zip"),
    ("04_Wave_Equation", "equation_plates/wave_equation/Wave_Equation_Physics_Wall_Art.zip"),
    ("05_Dirac_Equation", "equation_plates/dirac_equation/Dirac_Equation_Physics_Wall_Art.zip"),
    ("06_Navier_Stokes", "equation_plates/navier_stokes/Navier_Stokes_Physics_Wall_Art.zip"),
    ("07_Fourier_Series", "equation_plates/fourier_series/Fourier_Series_Math_Wall_Art.zip"),
    ("08_Harmonic_Series_Vibrating_String", "wallart_set/out/concept/harmonic/HarmonicSeries_prints.zip"),
    ("09_Special_Functions_Set_of_6", "special_plates/special_functions_set/Special_Functions_Wall_Art_Set_of_6.zip"),
    ("10_Hermite_Quantum_Harmonic_Oscillator", "special_plates/hermite_qho/Hermite_QHO_Physics_Wall_Art.zip"),
]

PREVIEW_SOURCES = [
    "wallart_set/out/physics/maxwell/listing/01_hero.jpg",
    "schrodinger_equation/previews/schrodinger_preview_1_hero.jpg",
    "wallart_set/out/physics/blackhole/listing/01_hero.jpg",
    "equation_plates/wave_equation/previews/wave_equation_preview_1_hero.jpg",
    "equation_plates/dirac_equation/previews/dirac_equation_preview_1_hero.jpg",
    "equation_plates/navier_stokes/previews/navier_stokes_preview_1_hero.jpg",
    "equation_plates/fourier_series/previews/fourier_series_preview_1_hero.jpg",
    "wallart_set/out/concept/harmonic/listing/01_hero.jpg",
    "special_plates/special_functions_set/previews/special_functions_preview_1_hero.jpg",
    "special_plates/hermite_qho/previews/hermite_qho_preview_1_hero.jpg",
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


def stage_items() -> None:
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
        print(f"  staged {name} ({src.stat().st_size // 1024} KB)")

    (STAGE / "README_MathRelaxing_Physics_Wall_Art_Pack.txt").write_text(
        """MathRelaxing — Physics Wall Art Pack (10 designs)
===================================================
Thank you for purchasing this digital pack.

CONTENTS (10 folders):
1. Maxwell Electromagnetism
2. Schrödinger Equation — quantum mechanics
3. Black Hole Anatomy — Schwarzschild physics
4. Wave Equation
5. Dirac Equation
6. Navier–Stokes equations
7. Fourier Series
8. Harmonic Series / Vibrating String
9. Special Functions — set of 6 scientific plates
10. Hermite polynomials / Quantum Harmonic Oscillator

Each folder contains high-resolution print-ready files (JPG/PDF as included).
Personal use only. Not for redistribution or resale of the digital files.
Shop: https://www.etsy.com/shop/TheMathRelaxing
""",
        encoding="utf-8",
    )


def write_split_zips() -> list[Path]:
    folders = sorted([p for p in STAGE.iterdir() if p.is_dir()])
    readme = STAGE / "README_MathRelaxing_Physics_Wall_Art_Pack.txt"
    part_a, part_b = folders[:5], folders[5:]
    paths = []
    for name, group in (
        ("MathRelaxing_Physics_Pack_Part1_of_2.zip", part_a),
        ("MathRelaxing_Physics_Pack_Part2_of_2.zip", part_b),
    ):
        zp = OUT / name
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
            if readme.is_file():
                zf.write(readme, readme.name)
            for folder in group:
                for p in folder.rglob("*"):
                    if p.is_file():
                        zf.write(p, Path(folder.name).joinpath(p.relative_to(folder)).as_posix())
        mb = zp.stat().st_size / (1024 * 1024)
        print(f"  ZIP {name}: {mb:.1f} MB  folders={[f.name for f in group]}")
        if mb > 19.5:
            raise SystemExit(f"Zip too large for Etsy: {zp} ({mb:.1f} MB)")
        paths.append(zp)
    return paths


def _collect_preview_images() -> list[Path]:
    imgs: list[Path] = []
    for rel in PREVIEW_SOURCES:
        p = ROOT / rel
        if p.is_file():
            imgs.append(p)
        else:
            # fallback: any hero/preview jpg nearby
            parent = p.parent if p.suffix else p
            if parent.is_dir():
                for f in list(parent.rglob("*hero*.jpg")) + list(parent.rglob("*preview*.jpg")):
                    if f.is_file():
                        imgs.append(f)
                        break
    return imgs[:10]


def build_previews() -> list[Path]:
    imgs = _collect_preview_images()
    print(f"  preview source images: {len(imgs)}")
    font = _font(54)
    font_s = _font(28)
    W = H = 2000

    canvas = Image.new("RGB", (W, H), (12, 16, 28))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, 220], fill=(8, 10, 18))
    draw.text((W // 2, 70), "PHYSICS WALL ART PACK", fill=(230, 236, 255), font=font, anchor="mt")
    draw.text(
        (W // 2, 145),
        "10 digital physics prints  ·  MathRelaxing",
        fill=(150, 165, 200),
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

    card = Image.new("RGB", (2000, 2000), (245, 242, 235))
    d = ImageDraw.Draw(card)
    d.text((100, 80), "What's included", fill=(20, 24, 40), font=font)
    lines = [
        "1. Maxwell Electromagnetism",
        "2. Schrödinger Equation",
        "3. Black Hole Anatomy",
        "4. Wave Equation",
        "5. Dirac Equation",
        "6. Navier–Stokes",
        "7. Fourier Series",
        "8. Harmonic Series / vibrating string",
        "9. Special Functions (set of 6)",
        "10. Hermite / Quantum Harmonic Oscillator",
        "",
        "Instant download · Print-ready files",
        "Worth ~$30+ if bought separately",
        "Pack price: $16.99",
    ]
    y = 200
    for line in lines:
        d.text((120, y), line, fill=(40, 44, 60), font=font_s)
        y += 55
    included = OUT / "preview_2_included.jpg"
    card.save(included, quality=90)

    value = Image.new("RGB", (2000, 2000), (12, 16, 28))
    vd = ImageDraw.Draw(value)
    vd.text((W // 2, 700), "10 physics designs · one download", fill=(230, 236, 255), font=font, anchor="mt")
    vd.text((W // 2, 820), "$16.99 pack  vs  $30+ separate", fill=(180, 200, 255), font=font_s, anchor="mt")
    vd.text((W // 2, 920), "Classroom · Lab · Office · STEM gift", fill=(140, 155, 190), font=font_s, anchor="mt")
    value_path = OUT / "preview_3_value.jpg"
    value.save(value_path, quality=90)

    print(f"  previews: {hero.name}, {included.name}, {value_path.name}")
    return [hero, included, value_path]


def main():
    print("Building Physics Wall Art Pack…")
    stage_items()
    write_split_zips()
    build_previews()
    print("Done →", OUT)


if __name__ == "__main__":
    main()
