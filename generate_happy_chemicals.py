"""
generate_happy_chemicals.py — Happy Chemicals wall-art print set
================================================================
Molecule structures via **RDKit** (real 2D depiction from SMILES).
Paper aesthetic + typography via **Pillow** (no matplotlib chemistry).

  python generate_happy_chemicals.py
  python generate_happy_chemicals.py --preview-only
  python generate_happy_chemicals.py --mol serotonin   # one molecule only
"""
from __future__ import annotations

import argparse
import io
import os
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "happy_chemicals")
PRINTS = os.path.join(OUT, "prints")
PREVIEWS = os.path.join(OUT, "previews")

# Paper + richer color (still gallery, not neon poster)
PAPER = (250, 245, 236)       # warm cream
INK = (36, 32, 30)            # deep charcoal
INK_SOFT = (88, 78, 72)
INK_FAINT = (150, 138, 125)

# Richer CPK-inspired atom colors for RDKit (0–1 RGB)
ATOM_PALETTE = {
    6:  (0.18, 0.16, 0.15),   # C — deep charcoal
    7:  (0.18, 0.38, 0.78),   # N — vivid soft blue
    8:  (0.86, 0.22, 0.24),   # O — strong coral-red
    16: (0.90, 0.68, 0.12),   # S — saturated gold
    15: (0.90, 0.48, 0.12),   # P
    17: (0.18, 0.68, 0.38),   # Cl
    9:  (0.25, 0.72, 0.55),   # F
    35: (0.62, 0.28, 0.22),   # Br
    1:  (0.40, 0.40, 0.44),   # H labels
    -1: (0.20, 0.18, 0.17),   # default / bonds
}

# inches @ 300 dpi
SIZES = {
    "8x10": (8.0, 10.0),
    "11x14": (11.0, 14.0),
    "16x20": (16.0, 20.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
    "5x7": (5.0, 7.0),
}
DPI_PRINT = 300
DPI_PREVIEW = 160

# Canonical SMILES — validated formulas via RDKit (see check in main)
# Oxytocin MUST be C43H66N12O12S2 (previous SMILES was wrong: C46…)
MOLECULES = {
    "serotonin": {
        "name": "Serotonin",
        "subtitle": "the happiness chemical",
        "formula": "C₁₀H₁₂N₂O",
        "smiles": "NCCc1c[nH]c2ccc(O)cc12",  # = C10H12N2O ✓
        "accent": (220, 95, 115),    # rose
        "frame": (230, 150, 160),
        "expect_formula": "C10H12N2O",
    },
    "dopamine": {
        "name": "Dopamine",
        "subtitle": "the reward chemical",
        "formula": "C₈H₁₁NO₂",
        "smiles": "NCCc1ccc(O)c(O)c1",  # = C8H11NO2 ✓
        "accent": (220, 145, 45),    # amber
        "frame": (225, 175, 90),
        "expect_formula": "C8H11NO2",
    },
    "oxytocin": {
        "name": "Oxytocin",
        "subtitle": "the bonding hormone",
        "formula": "C₄₃H₆₆N₁₂O₁₂S₂",
        # Correct cyclic nonapeptide → C43H66N12O12S2
        "smiles": (
            "N[C@H]1CSSC[C@H](NC(=O)[C@H](CC(N)=O)NC(=O)[C@H](CCC(N)=O)"
            "NC(=O)[C@@H](NC(=O)[C@H](Cc2ccc(O)cc2)NC1=O)[C@@H](C)CC)"
            "C(=O)N1CCC[C@H]1C(=O)N[C@@H](CC(C)C)C(=O)NCC(N)=O"
        ),
        "accent": (115, 105, 185),   # lilac
        "frame": (155, 145, 200),
        "expect_formula": "C43H66N12O12S2",
    },
    "caffeine": {
        "name": "Caffeine",
        "subtitle": "the focus molecule",
        "formula": "C₈H₁₀N₄O₂",
        "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",  # = C8H10N4O2 ✓
        "accent": (45, 145, 150),    # teal
        "frame": (90, 170, 175),
        "expect_formula": "C8H10N4O2",
    },
}


def _font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Prefer Georgia / Times for paper editorial feel; fall back to default."""
    candidates = []
    windir = os.environ.get("WINDIR", r"C:\Windows")
    if italic:
        candidates += [
            os.path.join(windir, "Fonts", "georgiai.ttf"),
            os.path.join(windir, "Fonts", "timesi.ttf"),
            os.path.join(windir, "Fonts", "Gabriola.ttf"),
        ]
    else:
        candidates += [
            os.path.join(windir, "Fonts", "georgia.ttf"),
            os.path.join(windir, "Fonts", "times.ttf"),
            os.path.join(windir, "Fonts", "calibri.ttf"),
        ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def mol_from_smiles(smiles: str) -> Chem.Mol:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    mol = Chem.Mol(mol)
    rdDepictor.Compute2DCoords(mol)
    # Prefer cleaner 2D layouts when available
    try:
        rdDepictor.SetPreferCoordGen(True)
        rdDepictor.Compute2DCoords(mol)
    except Exception:
        pass
    return mol


def render_molecule_rgba(
    smiles: str,
    px: int,
    *,
    bond_width: float = 2.2,
    padding: float = 0.12,
    min_font: int = 14,
) -> Image.Image:
    """
    RDKit Cairo drawer → RGBA transparent bg, soft colored heteroatoms + charcoal bonds.
    """
    mol = mol_from_smiles(smiles)
    drawer = rdMolDraw2D.MolDraw2DCairo(px, px)
    opts = drawer.drawOptions()
    opts.clearBackground = True
    opts.bondLineWidth = bond_width * 1.15  # slightly bolder lines
    opts.padding = padding
    opts.minFontSize = min_font
    opts.maxFontSize = max(min_font + 10, int(px / 24))
    opts.additionalAtomLabelPadding = 0.10
    # Soft palette (not pure B/W)
    try:
        opts.useDefaultAtomPalette()
    except Exception:
        pass
    try:
        # RDKit expects atomic-number keys → (r,g,b) floats 0–1
        for k, v in ATOM_PALETTE.items():
            opts.atomColourPalette[k] = v
    except Exception:
        # Fallback older API
        try:
            opts.updateAtomPalette(ATOM_PALETTE)
        except Exception:
            pass
    try:
        opts.setBackgroundColour((1.0, 1.0, 1.0, 1.0))
    except Exception:
        pass

    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    png = drawer.GetDrawingText()
    img = Image.open(io.BytesIO(png)).convert("RGBA")

    arr = np.asarray(img).copy()
    rgb = arr[:, :, :3].astype(np.float32)
    lum = rgb.mean(axis=2)
    # Near-white paper from Cairo → transparent; keep atom/bond colors
    white = lum >= 246
    out = arr.copy()
    out[white, 3] = 0
    # Boost alpha slightly on structure so colors read cleanly on cream paper
    structure = ~white
    out[structure, 3] = np.clip(out[structure, 3].astype(np.int16) + 20, 0, 255).astype(np.uint8)
    # Gently darken very light grays (anti-alias fringes) toward charcoal
    fringe = structure & (lum > 200) & (lum < 246)
    for c in range(3):
        out[fringe, c] = np.clip(
            out[fringe, c] * 0.55 + np.array(INK[c]) * 0.45, 0, 255
        ).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def _paper_canvas(w: int, h: int, accent: tuple[int, int, int] | None = None) -> Image.Image:
    """Warm paper + stronger accent wash (radial) for richer color prints."""
    base = np.full((h, w, 3), PAPER, dtype=np.float32)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 2.0, size=(h, w, 1)).astype(np.float32)
    base = base + noise

    if accent is not None:
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = w * 0.50, h * 0.36
        rx, ry = w * 0.42, h * 0.32
        d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        glow = np.clip(1.0 - d, 0, 1) ** 1.35
        glow = glow[:, :, None] * 0.26  # stronger wash
        acc = np.array(accent, dtype=np.float32).reshape(1, 1, 3)
        # blend accent into paper
        base = base * (1 - glow * 0.85) + acc * glow * 0.55 + np.array(PAPER) * glow * 0.30
        # soft corner vignette (very light warm)
        vig = ((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2) * 0.08
        base = base * (1 - vig[:, :, None])

    arr = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _draw_frame(
    draw: ImageDraw.ImageDraw,
    W: int,
    H: int,
    frame_col: tuple[int, int, int],
    accent: tuple[int, int, int],
    dpi: int,
):
    """Double frame: outer thin accent + inner charcoal-tinted rule."""
    m = int(min(W, H) * 0.045)          # outer margin
    gap = max(3, int(dpi * 0.012))      # gap between double lines
    lw_out = max(2, int(dpi * 0.006))
    lw_in = max(1, int(dpi * 0.0035))

    # outer frame (accent)
    draw.rectangle(
        [m, m, W - m - 1, H - m - 1],
        outline=frame_col,
        width=lw_out,
    )
    # inner frame (softer)
    inner = m + gap + lw_out
    draw.rectangle(
        [inner, inner, W - inner - 1, H - inner - 1],
        outline=tuple(min(255, c + 40) for c in frame_col),
        width=lw_in,
    )
    # corner ticks (decorative)
    tick = int(min(W, H) * 0.035)
    for (x0, y0, dx, dy) in (
        (m, m, 1, 1),
        (W - m, m, -1, 1),
        (m, H - m, 1, -1),
        (W - m, H - m, -1, -1),
    ):
        draw.line([(x0, y0), (x0 + dx * tick, y0)], fill=accent, width=lw_out)
        draw.line([(x0, y0), (x0, y0 + dy * tick)], fill=accent, width=lw_out)


# Cache high-res RDKit rasters per slug (reuse across sizes)
_MOL_CACHE: dict[str, Image.Image] = {}


def get_molecule_master(slug: str, master_px: int = 2400) -> Image.Image:
    """Render each molecule once at high res; scale later for each print size."""
    if slug in _MOL_CACHE:
        return _MOL_CACHE[slug]
    meta = MOLECULES[slug]
    if slug == "oxytocin":
        bond_w, pad, mfont = 1.6, 0.05, 11
        master_px = 2800
    else:
        bond_w, pad, mfont = 2.6, 0.12, 18
    img = render_molecule_rgba(
        meta["smiles"], master_px, bond_width=bond_w, padding=pad, min_font=mfont
    )
    _MOL_CACHE[slug] = img
    return img


def compose_print(
    slug: str,
    width_in: float,
    height_in: float,
    dpi: int = DPI_PRINT,
) -> Image.Image:
    """Full print: tinted paper + double frame + saturated RDKit structure."""
    meta = MOLECULES[slug]
    W = int(width_in * dpi)
    H = int(height_in * dpi)
    accent = tuple(meta.get("accent", (180, 160, 140)))
    frame_col = tuple(meta.get("frame", accent))
    canvas = _paper_canvas(W, H, accent=accent)
    draw = ImageDraw.Draw(canvas)

    # Double decorative frame
    _draw_frame(draw, W, H, frame_col, accent, dpi)

    # Target molecule box (leave room for frame + type)
    target = int(min(W, H) * (0.70 if slug == "oxytocin" else 0.56))
    master = get_molecule_master(slug)
    mol_img = master.resize((target, target), Image.Resampling.LANCZOS)

    mx = (W - mol_img.width) // 2
    my = int(H * 0.36 - mol_img.height / 2)
    my = max(int(H * 0.10), my)
    canvas.paste(mol_img, (mx, my), mol_img)

    # Typography
    name_size = max(28, int(0.044 * min(W, H)))
    sub_size = max(16, int(0.022 * min(W, H)))
    form_size = max(14, int(0.018 * min(W, H)))
    font_name = _font(name_size, italic=True)
    font_sub = _font(sub_size, italic=False)
    font_form = _font(form_size, italic=False)

    cy = int(H * 0.78)

    # Accent bar under title zone (thicker)
    bar_w = int(W * 0.18)
    bar_y = cy - int(name_size * 0.55)
    draw.line(
        [(W // 2 - bar_w, bar_y), (W // 2 + bar_w, bar_y)],
        fill=accent,
        width=max(3, dpi // 100),
    )

    def centered_text(text: str, y: int, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=font, fill=fill)

    sub_fill = tuple(int(a * 0.70 + b * 0.30) for a, b in zip(accent, INK_SOFT))
    centered_text(meta["name"], cy, font_name, INK)
    centered_text(meta["subtitle"], cy + int(name_size * 1.35), font_sub, sub_fill)
    centered_text(meta["formula"], cy + int(name_size * 2.35), font_form, INK_FAINT)

    return canvas


def save_rgb(img: Image.Image, path: str, dpi: int = DPI_PRINT):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # q=80 keeps full set ZIP under Etsy's ~20MB digital-file limit
    img.convert("RGB").save(
        path, "JPEG", quality=80, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path}")


def build_prints(only: str | None = None):
    os.makedirs(PRINTS, exist_ok=True)
    slugs = [only] if only else list(MOLECULES)
    for slug in slugs:
        if slug not in MOLECULES:
            raise SystemExit(f"Unknown molecule: {slug}")
        # validate SMILES early
        mol_from_smiles(MOLECULES[slug]["smiles"])
        mol_dir = os.path.join(PRINTS, slug)
        os.makedirs(mol_dir, exist_ok=True)
        for size_name, (w, h) in SIZES.items():
            img = compose_print(slug, w, h, dpi=DPI_PRINT)
            path = os.path.join(mol_dir, f"{slug}_{size_name}_{DPI_PRINT}dpi.jpg")
            save_rgb(img, path, DPI_PRINT)


def build_zip():
    zip_path = os.path.join(OUT, "Happy_Chemicals_Print_Set.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            """Happy Chemicals — Science of Feeling
Minimalist molecule wall-art print set

Includes 4 prints (structures generated with RDKit from standard SMILES):
  • Serotonin — the happiness chemical
  • Dopamine — the reward chemical
  • Oxytocin — the bonding hormone
  • Caffeine — the focus molecule

Each folder: high-resolution JPG (300 dpi)
Sizes: 5x7, 8x10, 11x14, 16x20, A4, A3

Print on warm matte or textured paper for best results.
Personal use only.
""",
        )
        for slug in MOLECULES:
            mol_dir = os.path.join(PRINTS, slug)
            if not os.path.isdir(mol_dir):
                continue
            for fn in sorted(os.listdir(mol_dir)):
                if fn.lower().endswith((".jpg", ".jpeg", ".png")):
                    zf.write(os.path.join(mol_dir, fn), arcname=f"{slug}/{fn}")
    print(f"ZIP: {zip_path}")


def build_previews(only: str | None = None):
    os.makedirs(PREVIEWS, exist_ok=True)
    slugs = list(MOLECULES) if not only else [only]

    # Hero 8x8 — serotonin
    hero_slug = "serotonin" if "serotonin" in slugs else slugs[0]
    hero = compose_print(hero_slug, 8.0, 8.0, dpi=DPI_PREVIEW)
    # override bottom caption for set branding
    draw = ImageDraw.Draw(hero)
    W, H = hero.size
    # cover lower third with paper and set title
    band_y = int(H * 0.72)
    draw.rectangle([0, band_y, W, H], fill=PAPER)  # clean caption band
    font_t = _font(max(28, W // 14), italic=True)
    font_s = _font(max(16, W // 28), italic=False)
    font_f = _font(max(12, W // 36), italic=False)
    for text, y, font, fill in [
        ("Happy Chemicals", int(H * 0.78), font_t, INK),
        ("four molecule prints", int(H * 0.86), font_s, INK_SOFT),
        ("serotonin  ·  dopamine  ·  oxytocin  ·  caffeine", int(H * 0.92), font_f, INK_FAINT),
    ]:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=font, fill=fill)
    path = os.path.join(PREVIEWS, "happy_chemicals_preview_1_hero.jpg")
    save_rgb(hero, path, DPI_PREVIEW)

    # Set grid 10x10
    grid = _paper_canvas(10 * DPI_PREVIEW, 10 * DPI_PREVIEW)
    gdraw = ImageDraw.Draw(grid)
    gw, gh = grid.size
    title_f = _font(max(28, gw // 22), italic=True)
    t = "the set"
    bb = gdraw.textbbox((0, 0), t, font=title_f)
    gdraw.text(((gw - (bb[2] - bb[0])) // 2, int(gh * 0.03)), t, font=title_f, fill=INK)
    positions = [(0.04, 0.12), (0.52, 0.12), (0.04, 0.54), (0.52, 0.54)]
    cell_w, cell_h = int(gw * 0.44), int(gh * 0.40)
    for slug, (fx, fy) in zip(list(MOLECULES), positions):
        thumb = compose_print(slug, 4.5, 5.5, dpi=DPI_PREVIEW)
        thumb = thumb.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        x, y = int(fx * gw), int(fy * gh)
        grid.paste(thumb, (x, y))
        # thin frame
        gdraw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], outline=(200, 195, 185), width=1)
    path = os.path.join(PREVIEWS, "happy_chemicals_preview_2_set.jpg")
    save_rgb(grid, path, DPI_PREVIEW)

    # Included
    incl = _paper_canvas(10 * DPI_PREVIEW, 10 * DPI_PREVIEW)
    idraw = ImageDraw.Draw(incl)
    iw, ih = incl.size
    left = compose_print("dopamine", 4.5, 6.5, dpi=DPI_PREVIEW)
    left = left.resize((int(iw * 0.46), int(ih * 0.70)), Image.Resampling.LANCZOS)
    incl.paste(left, (int(iw * 0.04), int(ih * 0.12)))
    f_h = _font(max(30, iw // 20), italic=True)
    f_b = _font(max(18, iw // 32), italic=False)
    idraw.text((int(iw * 0.55), int(ih * 0.18)), "included", font=f_h, fill=INK)
    lines = [
        "4 molecule prints",
        "Serotonin, Dopamine,",
        "Oxytocin & Caffeine",
        "",
        "Structures via RDKit",
        "from standard SMILES",
        "",
        "Sizes: 5×7 · 8×10",
        "11×14 · 16×20 · A4 · A3",
        "300 dpi JPG",
        "",
        "Best on matte or",
        "textured paper",
    ]
    y = int(ih * 0.30)
    for line in lines:
        idraw.text((int(iw * 0.55), y), line, font=f_b, fill=INK_SOFT)
        y += int(ih * 0.045)
    path = os.path.join(PREVIEWS, "happy_chemicals_preview_3_included.jpg")
    save_rgb(incl, path, DPI_PREVIEW)

    # Individual previews
    order = list(MOLECULES)
    for i, slug in enumerate(order, start=4):
        img = compose_print(slug, 8.0, 8.0, dpi=DPI_PREVIEW)
        path = os.path.join(PREVIEWS, f"happy_chemicals_preview_{i}_{slug}.jpg")
        save_rgb(img, path, DPI_PREVIEW)


def main():
    ap = argparse.ArgumentParser(description="Happy Chemicals — RDKit paper prints")
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--mol", choices=list(MOLECULES), help="Only one molecule")
    args = ap.parse_args()

    print("=== Happy Chemicals (RDKit + paper) ===")
    os.makedirs(OUT, exist_ok=True)

    # Validate all SMILES + molecular formulas (catch connectivity pifias)
    from rdkit.Chem import rdMolDescriptors
    for slug, meta in MOLECULES.items():
        if args.mol and slug != args.mol:
            continue
        m = Chem.MolFromSmiles(meta["smiles"])
        if m is None:
            raise SystemExit(f"Bad SMILES for {slug}")
        formula = rdMolDescriptors.CalcMolFormula(m)
        expect = meta.get("expect_formula")
        ok = (expect is None) or (formula == expect)
        flag = "OK" if ok else f"MISMATCH want {expect}"
        print(f"  {slug:12s}  {formula:16s}  {flag}  ({meta['name']})")
        if not ok:
            raise SystemExit(f"Formula check failed for {slug}: got {formula}")
    # clear cache so color/smiles changes always re-render
    _MOL_CACHE.clear()

    if not args.preview_only:
        print("Prints…")
        build_prints(args.mol)
        if not args.mol:
            build_zip()
    print("Previews…")
    build_previews(args.mol)
    print("Done.")


if __name__ == "__main__":
    main()
