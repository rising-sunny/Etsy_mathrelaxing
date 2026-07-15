"""Render IEEE logic gates via circuitikz → high-res PNG (cream bg)."""
from __future__ import annotations

import os
import subprocess
import tempfile

import fitz
from PIL import Image

OUT_PNG = os.path.join(os.path.dirname(__file__), "_circuitikz_gates.png")
OUT_PDF = os.path.join(os.path.dirname(__file__), "_circuitikz_gates.pdf")

TEX = r"""
\documentclass[border=18pt]{standalone}
\usepackage{circuitikz}
\usepackage{amsmath}
\usepackage{xcolor}
\usetikzlibrary{positioning}
\definecolor{cream}{HTML}{F4F1EA}
\definecolor{teal}{HTML}{2F6F6A}
\definecolor{slate}{HTML}{3D5A80}
\definecolor{indigo}{HTML}{4A5080}
\definecolor{amber}{HTML}{C4922A}
\definecolor{coral}{HTML}{C45C4A}
\definecolor{rust}{HTML}{B85C38}
\pagecolor{cream}
\begin{document}
\begin{circuitikz}[american, scale=1.45, transform shape, thick]
% AND
\node[and port, teal, fill=cream] (and1) at (0,4.0) {};
\draw[teal] (and1.in 1) -- ++(-0.8,0) node[left,font=\small]{A};
\draw[teal] (and1.in 2) -- ++(-0.8,0) node[left,font=\small]{B};
\node[below=7mm of and1,teal,font=\bfseries\small]{AND};
\node[below=12mm of and1,font=\small]{$A\cdot B$};
% OR
\node[or port, slate, fill=cream] (or1) at (4.8,4.0) {};
\draw[slate] (or1.in 1) -- ++(-0.8,0) node[left,font=\small]{A};
\draw[slate] (or1.in 2) -- ++(-0.8,0) node[left,font=\small]{B};
\node[below=7mm of or1,slate,font=\bfseries\small]{OR};
\node[below=12mm of or1,font=\small]{$A+B$};
% NOT
\node[not port, indigo, fill=cream] (not1) at (9.6,4.0) {};
\draw[indigo] (not1.in) -- ++(-0.8,0) node[left,font=\small]{A};
\node[below=7mm of not1,indigo,font=\bfseries\small]{NOT};
\node[below=12mm of not1,font=\small]{$\overline{A}$};
% XOR
\node[xor port, amber, fill=cream] (xor1) at (0,0) {};
\draw[amber] (xor1.in 1) -- ++(-0.8,0) node[left,font=\small]{A};
\draw[amber] (xor1.in 2) -- ++(-0.8,0) node[left,font=\small]{B};
\node[below=7mm of xor1,amber,font=\bfseries\small]{XOR};
\node[below=12mm of xor1,font=\small]{$A\oplus B$};
% NAND
\node[nand port, coral, fill=cream] (nand1) at (4.8,0) {};
\draw[coral] (nand1.in 1) -- ++(-0.8,0) node[left,font=\small]{A};
\draw[coral] (nand1.in 2) -- ++(-0.8,0) node[left,font=\small]{B};
\node[below=7mm of nand1,coral,font=\bfseries\small]{NAND};
\node[below=12mm of nand1,font=\small]{$\overline{A\cdot B}$};
% NOR
\node[nor port, rust, fill=cream] (nor1) at (9.6,0) {};
\draw[rust] (nor1.in 1) -- ++(-0.8,0) node[left,font=\small]{A};
\draw[rust] (nor1.in 2) -- ++(-0.8,0) node[left,font=\small]{B};
\node[below=7mm of nor1,rust,font=\bfseries\small]{NOR};
\node[below=12mm of nor1,font=\small]{$\overline{A+B}$};
\end{circuitikz}
\end{document}
"""


def main():
    td = tempfile.mkdtemp()
    tex_path = os.path.join(td, "gates.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(TEX)
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "gates.tex"],
        cwd=td,
        capture_output=True,
        text=True,
    )
    pdf = os.path.join(td, "gates.pdf")
    if not os.path.isfile(pdf):
        print(r.stdout[-2500:])
        raise SystemExit(f"pdflatex failed: {r.returncode}")
    import shutil

    shutil.copy(pdf, OUT_PDF)
    doc = fitz.open(pdf)
    page = doc[0]
    mat = fitz.Matrix(5, 5)  # ~360+ dpi effective
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.save(OUT_PNG, "PNG")
    doc.close()
    print("OK", OUT_PNG, img.size)


if __name__ == "__main__":
    main()
