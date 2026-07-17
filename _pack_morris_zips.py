"""Repack Morris under Etsy 20MB — curated size set + lower JPEG for dense art."""
from pathlib import Path
from PIL import Image
import zipfile

PRINTS = Path("morris_set/prints")
OUT = Path("morris_set")
DPI = 300
# Curated: large poster + common frames + home letter
KEEP = {
    "2x3_24x36",  # big poster
    "3x4_18x24",
    "4x5_16x20",
    "2x3_12x18",
    "A4",
}
LARGE = {"2x3_24x36", "3x4_18x24", "4x5_24x30", "5x7_20x28", "A1", "A2", "4x5_16x20"}
POSTERS = [
    "01_willow_boughs",
    "02_strawberry_garden",
    "03_trellis_rose",
    "04_pimpernel_field",
    "05_honeysuckle",
    "06_acanthus_scroll",
]
README = (
    "MathRelaxing — William Morris–Inspired Botanical Print Set (v2 lethal)\n"
    "6 original dense Arts & Crafts posters @ 300 dpi.\n"
    "Sizes included: 24x36, 18x24, 16x20, 12x18, A4.\n"
    "Scale 24x36 down for other frames. Matte paper recommended.\n"
    "Personal use only. © MathRelaxing\n"
)


def recompress():
    for slug in POSTERS:
        folder = PRINTS / slug
        if not folder.is_dir():
            continue
        for f in folder.glob("*.jpg"):
            sk = f.stem[len(slug) + 1 : -len(f"_{DPI}dpi")]
            if sk not in KEEP:
                continue
            q = 38 if sk in LARGE or sk == "2x3_24x36" else 50
            if sk in ("2x3_24x36", "3x4_18x24"):
                q = 36
            im = Image.open(f).convert("RGB")
            im.save(
                f,
                "JPEG",
                quality=q,
                dpi=(DPI, DPI),
                optimize=True,
                progressive=True,
                subsampling=2,
            )
    print("recompressed curated sizes")


def pack(path: Path, slugs, label):
    if path.exists():
        path.unlink()
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", README)
        for slug in slugs:
            folder = PRINTS / slug
            for f in sorted(folder.glob("*.jpg")):
                sk = f.stem[len(slug) + 1 : -len(f"_{DPI}dpi")]
                if sk not in KEEP:
                    continue
                z.write(f, f"{slug}/{f.name}")
                n += 1
    mb = path.stat().st_size / 1024 / 1024
    flag = "OK" if mb <= 19.5 else "OVER"
    print(f"{label}: {path.name} {mb:.1f}MB n={n} {flag}")
    return mb


if __name__ == "__main__":
    recompress()
    for p in OUT.glob("MathRelaxing_Morris_*.zip"):
        p.unlink()
    packs = [
        (OUT / "MathRelaxing_Morris_01_Willow.zip", ["01_willow_boughs"], "01"),
        (OUT / "MathRelaxing_Morris_02_Strawberry.zip", ["02_strawberry_garden"], "02"),
        (OUT / "MathRelaxing_Morris_03_Trellis.zip", ["03_trellis_rose"], "03"),
        (
            OUT / "MathRelaxing_Morris_04_05_Pimpernel_Honeysuckle.zip",
            ["04_pimpernel_field", "05_honeysuckle"],
            "04-05",
        ),
        (OUT / "MathRelaxing_Morris_06_Acanthus.zip", ["06_acanthus_scroll"], "06"),
    ]
    for path, slugs, label in packs:
        pack(path, slugs, label)
