"""
generate_dna_set.py — "DNA & Molecules" scientific-plate set, redesign pass 2.

Keeps the cream/ink/rust "scientific plate" family (same register as the
Schrodinger/equation_plates house style) but:
  - swaps the generic sans-serif type for Cinzel (display) + Raleway (body),
    the same pairing used across the coffee-table books and History posters
  - replaces the old flat-matplotlib "fake 3D" helix with a real pyvista/VTK
    3D B-DNA render (see generate_helix_render.py)
  - redraws the molecule cards via RDKit with a custom atom-color palette
    tuned to the house ink/rust/slate scheme instead of default RDKit colors
  - tightens the plate layout (title/rule/subtitle/footer-stats scaffold)

  python generate_dna_set.py
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = BASE
PLATES = os.path.join(OUT, "plates"); os.makedirs(PLATES, exist_ok=True)
AF = os.path.join(os.path.dirname(BASE), "lulu_books", "assets", "fonts")

CREAM = "#f4f1ea"
INK = "#2a2620"
INK_SOFT = "#5a564e"
INK_FAINT = "#9a948a"
RUST = "#b85c38"
RUST_SOFT = "#c4785a"
SLATE = "#3d5a80"
TEAL = "#3f8f82"
ROSE = "#b8547a"
LINE = "#ddd5c3"

CINZEL = fm.FontProperties(fname=f"{AF}/Cinzel-SemiBold.ttf")
CINZEL_R = fm.FontProperties(fname=f"{AF}/Cinzel.ttf")
RALEWAY = fm.FontProperties(fname=f"{AF}/Raleway.ttf")
RALEWAY_I = fm.FontProperties(fname=f"{AF}/Raleway-Italic.ttf")

DPI = 300
W_IN, H_IN = 9.0, 11.5
ASPECT = W_IN / H_IN  # axes are 0-1 x 0-1 but the figure isn't square --
# an image "w" wide and "w*ih/iw" tall in that fractional space would
# render visually stretched; multiply by ASPECT to correct for it.


def tracked(s, thin=1):
    return (" " * thin).join(s)


# ------------------------------------------------------------ RDKit helpers
def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


ATOM_PALETTE = {6: _hex2rgb(INK), 7: _hex2rgb(SLATE), 8: _hex2rgb(RUST),
                1: _hex2rgb(INK), 15: _hex2rgb(TEAL)}


def mol_png(smiles, size=700, bond_lw=3):
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DCairo(size, size)
    opts = d.drawOptions()
    opts.setBackgroundColour((1, 1, 1, 0))
    opts.bondLineWidth = bond_lw
    opts.minFontSize = 20
    opts.maxFontSize = 34
    opts.updateAtomPalette(ATOM_PALETTE)
    opts.setSymbolColour(_hex2rgb(INK))
    opts.padding = 0.12
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    png = d.GetDrawingText()
    from io import BytesIO
    img = Image.open(BytesIO(png))
    # RDKit's canvas is always square with generous padding -- an elongated
    # molecule (e.g. a dipeptide chain) ends up mostly transparent margin,
    # which threw off every w -> h size computation downstream. Trim to the
    # actual drawn bounding box (plus a small margin) so "w" means the
    # molecule's real footprint, not the padded canvas.
    bbox = img.getbbox()
    if bbox:
        pad = 14
        l, t, r, b = bbox
        l = max(0, l - pad); t = max(0, t - pad)
        r = min(img.width, r + pad); b = min(img.height, b + pad)
        img = img.crop((l, t, r, b))
    return img


def place_mol(ax, smiles, cx, cy, w, size=700, bond_lw=3):
    img = mol_png(smiles, size=size, bond_lw=bond_lw)
    iw, ih = img.size
    h = w * (ih / iw) * ASPECT
    ax.imshow(np.asarray(img), extent=(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2), zorder=4, aspect="auto")
    return h


# ------------------------------------------------------------ plate scaffold
def new_plate():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(CREAM); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    m = 0.045
    ax.add_patch(Rectangle((m, m), 1 - 2 * m, 1 - 2 * m, fill=False,
                            edgecolor=INK_FAINT, lw=1.1))
    return fig, ax


def header(ax, title, fig_no, subtitle):
    x0 = 0.095
    ax.text(x0, 0.925, title, fontproperties=CINZEL, fontsize=27, color=INK, ha="left")
    ax.text(0.905, 0.928, tracked(f"FIG. {fig_no}"), fontproperties=RALEWAY_I,
            fontsize=11, color=RUST, ha="right")
    ax.plot([x0, 0.905], [0.900, 0.900], color=INK, lw=1.3)
    ax.text(x0, 0.876, subtitle, fontproperties=RALEWAY_I, fontsize=12.5,
            color=INK_SOFT, ha="left")


def caption(ax, lines):
    y = 0.155
    for line in lines:
        ax.text(0.095, y, line, fontproperties=RALEWAY, fontsize=10.8, color=INK_SOFT, ha="left")
        y -= 0.021


def footer_stats(ax, items):
    ax.plot([0.095, 0.905], [0.112, 0.112], color=LINE, lw=1.1)
    xs = [0.095, 0.40, 0.70]
    for x, (val, label) in zip(xs, items):
        ax.text(x, 0.082, val, fontproperties=CINZEL_R, fontsize=13.5, color=INK, ha="left")
        ax.text(x, 0.050, tracked(label.upper(), 0), fontproperties=RALEWAY_I, fontsize=9,
                color=INK_FAINT, ha="left")


# ------------------------------------------------------------------ plate 1
def draw_double_helix():
    fig, ax = new_plate()
    header(ax, "DOUBLE HELIX", "01", "B-DNA — antiparallel strands, ~10.5 bp/turn, Watson–Crick pairs")

    helix = Image.open(os.path.join(BASE, "_helix_full.png"))
    iw, ih = helix.size
    cx, cy, w = 0.40, 0.51, 0.52
    h = w * (ih / iw) * ASPECT
    ax.imshow(np.asarray(helix), extent=(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2), zorder=3, aspect="auto")

    ax.add_patch(Rectangle((0.11, 0.855), 0.028, 0.014, facecolor=ROSE, edgecolor="none"))
    ax.text(0.145, 0.862, "A – T", fontproperties=RALEWAY, fontsize=9.5, color=INK_SOFT, va="center")
    ax.add_patch(Rectangle((0.24, 0.855), 0.028, 0.014, facecolor=TEAL, edgecolor="none"))
    ax.text(0.275, 0.862, "G – C", fontproperties=RALEWAY, fontsize=9.5, color=INK_SOFT, va="center")

    # anchor points measured directly off the rendered helix (non-transparent
    # pixel bounding box at each height) so the leader lines actually touch
    # the strand/rung instead of floating in empty space
    callouts = [
        ((0.484, 0.693), (0.80, 0.80), "sugar–phosphate\nbackbone"),
        ((0.477, 0.458), (0.80, 0.50), "base pairs"),
        ((0.454, 0.301), (0.80, 0.22), "antiparallel\n5'->3'  /  3'->5'"),
    ]
    for (x0, y0), (x1, y1), label in callouts:
        ax.plot([x0], [y0], "o", color=INK_SOFT, ms=3.5, zorder=6)
        bend_x = x0 + (x1 - x0) * 0.4
        ax.plot([x0, bend_x, x1], [y0, y0, y1], color=INK_FAINT, lw=0.8, zorder=5)
        ax.text(x1 + 0.012, y1, label, fontproperties=RALEWAY_I, fontsize=9.5, color=INK_SOFT, va="center")
    ax.text(0.40, 0.255, "helical axis", fontproperties=RALEWAY_I, fontsize=9.5,
            color=INK_FAINT, ha="center")

    caption(ax, [
        "Projected B-form DNA: two antiparallel strands wind about a common axis.",
        "Base pairs stack every ~3.4 Å; a full turn holds ~10.5 pairs.",
    ])
    footer_stats(ax, [("~10.5 bp/turn", "B-DNA pitch"), ("3.4 Å/bp", "axial rise"), ("~2 nm", "diameter")])
    return fig


# ------------------------------------------------------------------ plate 2
def draw_base_pairing():
    fig, ax = new_plate()
    header(ax, "BASE PAIRING", "02", "Watson–Crick pairs — hydrogen bonds enforce complementarity")

    def pair_card(y0, h, left_smiles, right_smiles, label, n_hbonds):
        ax.add_patch(Rectangle((0.095, y0), 0.81, h, facecolor="white", edgecolor=LINE, lw=1.0, zorder=2))
        ax.text(0.5, y0 + h - 0.028, label, fontproperties=CINZEL_R, fontsize=12.5, color=INK,
                ha="center", va="top", zorder=4)
        ax.text(0.5, y0 + h - 0.052, tracked(f"{n_hbonds} HYDROGEN BONDS"), fontproperties=RALEWAY_I,
                fontsize=8.5, color=RUST, ha="center", va="top", zorder=4)
        place_mol(ax, left_smiles, 0.26, y0 + h * 0.40, 0.28)
        place_mol(ax, right_smiles, 0.74, y0 + h * 0.40, 0.28)
        for i in range(n_hbonds):
            yy = y0 + h * 0.42 + (i - (n_hbonds - 1) / 2) * 0.045
            ax.plot([0.40, 0.60], [yy, yy], color=INK_FAINT, lw=1.1, ls=(0, (3, 2)), zorder=4)

    pair_card(0.515, 0.29, "Nc1ncnc2[nH]cnc12", "Cc1c[nH]c(=O)[nH]c1=O", "Adenine — Thymine", 2)
    pair_card(0.17, 0.29, "Nc1nc2[nH]cnc2c(=O)[nH]1", "Nc1ccnc(=O)[nH]1", "Guanine — Cytosine", 3)

    caption(ax, [
        "Purines (A, G) pair with pyrimidines (T, C). Geometry and H-bond count lock specificity.",
        "Structures drawn from SMILES with RDKit — standard valence and aromaticity.",
    ])
    footer_stats(ax, [("A <-> T", "2 H-bonds"), ("G <-> C", "3 H-bonds"), ("purine + pyrimidine", "pair geometry")])
    return fig


# ------------------------------------------------------------------ plate 3
def draw_dna_vs_rna():
    fig, ax = new_plate()
    header(ax, "DNA VS RNA", "03", "Sugar chemistry and the T <-> U base swap")

    def column(x0, w, label, color, sugar_smiles, base_smiles, base_name, note):
        y0, h = 0.300, 0.545
        ax.add_patch(Rectangle((x0, y0), w, h, facecolor="white", edgecolor=color, lw=1.4, zorder=2))
        ax.text(x0 + w / 2, y0 + h - 0.045, label, fontproperties=CINZEL, fontsize=16, color=color,
                ha="center", zorder=4)
        ax.text(x0 + w / 2, y0 + h - 0.098, "2'-deoxyribose" if label == "DNA" else "ribose (2'-OH)",
                fontproperties=RALEWAY_I, fontsize=9, color=INK_FAINT, ha="center", zorder=4)
        place_mol(ax, sugar_smiles, x0 + w / 2, y0 + h - 0.245, w * 0.66)
        ax.plot([x0 + 0.06, x0 + w - 0.06], [y0 + h - 0.400, y0 + h - 0.400], color=LINE, lw=0.9, zorder=3)
        ax.text(x0 + w / 2, 0.420, base_name, fontproperties=RALEWAY, fontsize=10.5, color=INK,
                ha="center", zorder=4)
        place_mol(ax, base_smiles, x0 + w / 2, 0.353, w * 0.40)
        ax.text(x0 + w / 2, y0 - 0.032, note, fontproperties=RALEWAY_I, fontsize=8.8, color=INK_FAINT,
                ha="center", zorder=4)

    column(0.11, 0.375, "DNA", SLATE, "OCC1CC(O)C(O)O1", "Cc1c[nH]c(=O)[nH]c1=O", "Thymine (T)",
           "double helix · stable archive")
    column(0.515, 0.375, "RNA", TEAL, "OCC1OC(O)C(O)C1O", "O=c1cc[nH]c(=O)[nH]1", "Uracil (U)",
           "often single · messages & catalysis")

    caption(ax, [
        "The 2'-OH on ribose makes RNA chemically more reactive than DNA.",
        "Uracil replaces thymine; pairing rules still hold (A–U instead of A–T).",
    ])
    footer_stats(ax, [("T <-> U", "base swap"), ("2'-OH", "ribose mark"), ("dsDNA / mRNA", "typical form")])
    return fig


# ------------------------------------------------------------------ plate 4
def draw_central_dogma():
    fig, ax = new_plate()
    header(ax, "CENTRAL DOGMA", "04", "Information flow: DNA -> RNA -> protein")

    nodes = [(0.20, "DNA", INK), (0.5, "RNA", SLATE), (0.80, "Protein", RUST)]
    y = 0.72
    for x, label, color in nodes:
        ax.plot([x], [y], "o", color=color, ms=13, mec=CREAM, mew=2, zorder=5)
        ax.text(x, y - 0.055, label, fontproperties=CINZEL_R, fontsize=15, color=color,
                ha="center", zorder=5)
    for (x0, _, _), (x1, _, _), label in zip(nodes[:-1], nodes[1:], ["transcription", "translation"]):
        arr = FancyArrowPatch((x0 + 0.035, y), (x1 - 0.035, y), arrowstyle="-|>",
                               color=INK_SOFT, mutation_scale=16, lw=1.4, zorder=4)
        ax.add_patch(arr)
        ax.text((x0 + x1) / 2, y + 0.028, label, fontproperties=RALEWAY_I, fontsize=10,
                color=INK_SOFT, ha="center")
    replicate = FancyArrowPatch((0.188, y + 0.040), (0.212, y + 0.040), connectionstyle="arc3,rad=1.5",
                                 arrowstyle="-|>", color=INK_FAINT, mutation_scale=11, lw=1.1, zorder=3)
    ax.add_patch(replicate)
    ax.text(0.20, y + 0.115, "replication", fontproperties=RALEWAY_I, fontsize=9, color=INK_FAINT, ha="center")

    rows = [
        ("DNA -> DNA", "replication · DNA polymerase", INK),
        ("DNA -> mRNA", "transcription · RNA polymerase", SLATE),
        ("mRNA -> amino acids", "translation · ribosome", RUST),
    ]
    y0 = 0.535
    for i, (rule, desc, color) in enumerate(rows):
        yy = y0 - i * 0.062
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.095, yy - 0.020), 0.81, 0.044, facecolor=LINE, alpha=0.35, zorder=1))
        ax.add_patch(Rectangle((0.11, yy - 0.016), 0.012, 0.036, facecolor=color, edgecolor="none", zorder=3))
        ax.text(0.145, yy, rule, fontproperties=CINZEL_R, fontsize=11.5, color=INK, va="center", zorder=3)
        ax.text(0.60, yy, desc, fontproperties=RALEWAY_I, fontsize=9.5, color=INK_SOFT, va="center",
                ha="left", zorder=3)
    ax.text(0.5, 0.275, "4³ = 64 codons  ->  20 amino acids + start / stop",
            fontproperties=RALEWAY, fontsize=11, color=INK_SOFT, ha="center")

    caption(ax, [
        "Crick's central dogma: sequence information flows from nucleic acids to protein.",
        "Reverse transcription (RNA to DNA) is a notable exception in retroviruses.",
    ])
    footer_stats(ax, [("codon -> aa", "genetic code"), ("3 nt / 1 aa", "reading frame"), ("20 amino acids", "standard set")])
    return fig


# ------------------------------------------------------------------ plate 5
def draw_amino_acids():
    fig, ax = new_plate()
    header(ax, "AMINO ACIDS", "05", "Shared backbone · variable side chain R · peptide condensation")

    ax.text(0.5, 0.83, "general form", fontproperties=RALEWAY_I, fontsize=10, color=INK_FAINT, ha="center")
    ax.text(0.5, 0.775, r"$H_2N\!-\!C_\alpha H(R)\!-\!COOH$", fontsize=19, color=INK, ha="center")
    ax.text(0.5, 0.735, "C-alpha — chiral carbon (except glycine)  ·  R — side chain",
            fontproperties=RALEWAY_I, fontsize=9.5, color=INK_FAINT, ha="center")

    ax.plot([0.5, 0.5], [0.335, 0.685], color=LINE, lw=1.0)
    ax.text(0.27, 0.665, "Glycine", fontproperties=CINZEL_R, fontsize=13, color=INK, ha="center")
    ax.text(0.27, 0.635, "R = H", fontproperties=RALEWAY_I, fontsize=9.5, color=INK_FAINT, ha="center")
    place_mol(ax, "NCC(=O)O", 0.27, 0.49, 0.30)
    ax.text(0.73, 0.665, "Alanine", fontproperties=CINZEL_R, fontsize=13, color=INK, ha="center")
    ax.text(0.73, 0.635, "R = CH₃", fontproperties=RALEWAY_I, fontsize=9.5, color=INK_FAINT, ha="center")
    place_mol(ax, "N[C@@H](C)C(=O)O", 0.73, 0.49, 0.30)

    ax.plot([0.11, 0.905], [0.345, 0.345], color=LINE, lw=1.0)
    ax.text(0.5, 0.315, "peptide bond · condensation (-H2O)", fontproperties=RALEWAY_I,
            fontsize=9.5, color=RUST, ha="center")
    place_mol(ax, "NCC(=O)N[C@@H](C)C(=O)O", 0.5, 0.235, 0.26)

    caption(ax, [
        "Twenty standard amino acids share this backbone; R sets chemical personality.",
        "The carboxyl of one residue condenses with the amino of the next — amide linkage.",
    ])
    footer_stats(ax, [("H3N-CHR-COOH", "general aa"), ("-CO-NH-", "peptide"), ("n x aa -> protein", "polymer")])
    return fig


# ------------------------------------------------------------------ plate 6
def draw_key_molecules():
    fig, ax = new_plate()
    header(ax, "KEY MOLECULES", "06", "Water · D-glucose · ATP — structures via RDKit")

    cards = [
        (0.11, "Water", "O", "H2O", "polar solvent of life", "density 1.00 g/mL"),
        (0.405, "Glucose", "OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O", "C6H12O6",
         "D-glucopyranose", "cellular fuel"),
        (0.70, "ATP", "Nc1ncnc2c1ncn2C1OC(COP(=O)(O)OP(=O)(O)OP(=O)(O)O)C(O)C1O", "C10H16N5O13P3",
         "adenosine triphosphate", "~30.5 kJ/mol · bond"),
    ]
    w = 0.195
    for x0, name, smiles, formula, note1, note2 in cards:
        ax.add_patch(Rectangle((x0, 0.335), w, 0.50, facecolor="white", edgecolor=LINE, lw=1.2, zorder=2))
        ax.text(x0 + w / 2, 0.795, name, fontproperties=CINZEL_R, fontsize=13.5, color=INK,
                ha="center", zorder=4)
        ax.text(x0 + w / 2, 0.755, formula, fontproperties=RALEWAY, fontsize=9, color=RUST,
                ha="center", zorder=4)
        place_mol(ax, smiles, x0 + w / 2, 0.58, w * 0.86, size=500)
        ax.text(x0 + w / 2, 0.400, note1, fontproperties=RALEWAY_I, fontsize=8, color=INK_SOFT,
                ha="center", zorder=4)
        ax.text(x0 + w / 2, 0.365, note2, fontproperties=RALEWAY_I, fontsize=8, color=INK_FAINT,
                ha="center", zorder=4)

    caption(ax, [
        "Water shapes biomolecular structure; glucose feeds glycolysis; ATP pays the energy bill.",
        "Structures computed from SMILES with RDKit (2D coordinates, standard valence).",
    ])
    footer_stats(ax, [("H2O", "solvent"), ("C6H12O6", "fuel"), ("ATP <-> ADP + Pi", "currency")])
    return fig


def build():
    plates = [
        ("01_double_helix", draw_double_helix),
        ("02_base_pairing", draw_base_pairing),
        ("03_dna_vs_rna", draw_dna_vs_rna),
        ("04_central_dogma", draw_central_dogma),
        ("05_amino_acids", draw_amino_acids),
        ("06_key_molecules", draw_key_molecules),
    ]
    paths = []
    for name, fn in plates:
        print("building", name)
        fig = fn()
        p = os.path.join(PLATES, f"{name}.jpg")
        fig.savefig(p, facecolor=CREAM, pil_kwargs={"quality": 92})
        plt.close(fig)
        paths.append(p)
        print("  wrote", p)
    return paths


def contact_sheet(paths):
    imgs = [Image.open(p) for p in paths]
    w, h = imgs[0].size
    cols, rows = 3, 2
    pad = 40
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad + 140), CREAM)
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    d.text((pad, 40), "DNA & MOLECULES — CONTACT SHEET", fill=INK)
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (w + pad)
        y = 140 + pad + r * (h + pad)
        sheet.paste(im, (x, y))
    out = os.path.join(BASE, "_contact_sheet.jpg")
    sheet.save(out, quality=88)
    print("contact sheet:", out)


if __name__ == "__main__":
    paths = build()
    contact_sheet(paths)
    print("DONE")
