"""
build_stem_study_kit.py — "STEM Student Complete Study Kit" bundle.

Assembled from components the shop already sells, because that is where its
real buyer signal is: four of the nine organic sales so far were practical
STEM study printables (lab notebook, planners, graph paper), each priced
$1.50-$2.99 -- while 69% of the catalog is wall art. Bundling raises revenue
per visitor instead of adding a 154th listing competing on the same keywords.

Deliberately ships A4 + US Letter only. These are printables a student runs
off on standard paper; the 2:3 / 3:4 / 4:5 framing ratios belong to the
standalone wall-art listings, and including them here pushed the ZIP past
Etsy's 20 MB per-file limit (~20.8 MB) for no benefit to this buyer.

  python stem_study_kit/build_stem_study_kit.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import products_catalog as pc  # noqa: E402

OUT = Path(__file__).resolve().parent
ZIP_NAME = "STEM_Student_Complete_Study_Kit.zip"
KEEP = ("_a4", "_letter", "_us_letter")  # lowercase substrings we keep

README = """STEM STUDENT COMPLETE STUDY KIT
MathRelaxing

Everything in one download, print-ready at A4 and US Letter.

01_FORMULA_SHEETS
   Calculus - derivatives, integrals, series, limits
   Linear Algebra - matrices, determinants, eigenvalues
   Vector Calculus - grad, div, curl, Green, Stokes, divergence
   Physics - mechanics, thermodynamics, E&M, waves

02_REFERENCE
   The Unit Circle - every special angle in degrees and radians,
   with exact (cos, sin) coordinates

03_GRID_PAPER
   Square, dot, isometric, hexagonal, Cornell, log-log, semi-log,
   millimetre, polar and Cartesian grids

04_NOTEBOOKS
   STEM Lab Notebook - experiment log with hypothesis, method,
   data tables, results
   STEM Notebook - mixed grid pages for problem sets

05_CORNELL_LAB_SYLLABUS
   Cornell note pages, lab report templates, syllabus planners

06_BINDER_COVERS
   Subject covers and spines for maths, physics, chemistry, biology

07_PLANNER
   STEM Focus Planner - undated weekly planning, habit tracking,
   research log, plus a set of maths stickers

HOW TO USE
Print at home or at a copy shop. A4 and US Letter are both included for
every printable, so use whichever your printer takes. Nothing is dated,
so the planner and logs work in any term or year.

Personal and single-classroom use. Not for redistribution or resale.

(c) MathRelaxing
"""


def _keep(name: str) -> bool:
    """A4 / US Letter printables only (PDFs and non-sized assets always pass)."""
    low = name.lower()
    if low.endswith(".txt"):
        return False  # component READMEs are replaced by ours
    if low.endswith(".pdf") or low.endswith(".png"):
        return True
    return any(k in low for k in KEEP)


def _add_zip(bundle: zipfile.ZipFile, src: Path, dest_dir: str, rename=None):
    with zipfile.ZipFile(src) as z:
        for info in z.infolist():
            if info.is_dir() or not _keep(info.filename):
                continue
            base = Path(info.filename).name
            if rename:
                base = rename(base)
            bundle.writestr(f"{dest_dir}/{base}", z.read(info))


def _add_file(bundle: zipfile.ZipFile, src: Path, dest_dir: str):
    bundle.write(src, f"{dest_dir}/{src.name}")


def main():
    P = pc.PRODUCTS
    out_path = OUT / ZIP_NAME
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as b:
        b.writestr("READ-ME.txt", README)

        # 01 formula sheets -- strip the verbose per-file prefix
        for key, nice in [("calculus_formula_sheet", "calculus"),
                          ("linear_algebra_formula_sheet", "linear_algebra"),
                          ("vector_calculus_formula_sheet", "vector_calculus"),
                          ("physics_formula_sheet", "physics")]:
            _add_zip(b, Path(P[key]["files"][0]), "01_Formula_Sheets",
                     rename=lambda n, s=nice: n.replace(f"{s}_formula_sheet_", f"{s}_").replace("_300dpi", ""))

        _add_zip(b, Path(P["unit_circle_print"]["files"][0]), "02_Reference",
                 rename=lambda n: n.replace("_300dpi", ""))
        _add_zip(b, Path(P["graph_paper"]["files"][0]), "03_Grid_Paper")
        _add_file(b, Path(P["stem_lab_notebook"]["files"][0]), "04_Notebooks")
        _add_file(b, Path(P["stem_notebook"]["files"][0]), "04_Notebooks")
        _add_zip(b, ROOT / "stem_student_pack" / "STEM_Student_Pack_Cornell_Lab_Syllabus.zip",
                 "05_Cornell_Lab_Syllabus")
        _add_zip(b, ROOT / "subject_binder_covers" / "STEM_Subject_Binder_Covers.zip",
                 "06_Binder_Covers")
        for f in P["stem_focus_planner"]["files"]:
            f = Path(f)
            if f.suffix == ".pdf":
                _add_file(b, f, "07_Planner")
            else:
                _add_zip(b, f, "07_Planner/stickers")

    mb = out_path.stat().st_size / 1e6
    with zipfile.ZipFile(out_path) as z:
        names = z.namelist()
    print(f"{ZIP_NAME}: {mb:.1f} MB, {len(names)} archivos")
    if mb > 19.5:
        print("  WARNING: cerca del limite de 20MB de Etsy")
    from collections import Counter
    for folder, n in sorted(Counter(x.split("/")[0] for x in names).items()):
        print(f"  {n:3d}  {folder}")
    return out_path


if __name__ == "__main__":
    main()
