"""Render turnstile FSM via TikZ automata → high-res cream PNG."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import fitz
from PIL import Image

OUT_DIR = os.path.dirname(__file__)
OUT_PNG = os.path.join(OUT_DIR, "_tikz_fsm.png")
OUT_PDF = os.path.join(OUT_DIR, "_tikz_fsm.pdf")

TEX = r"""
\documentclass[border=20pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{automata,positioning,arrows.meta,calc}
\usepackage{amsmath}
\usepackage{xcolor}
\definecolor{cream}{HTML}{F4F1EA}
\definecolor{teal}{HTML}{2F6F6A}
\definecolor{coral}{HTML}{C45C4A}
\definecolor{amber}{HTML}{C4922A}
\definecolor{slate}{HTML}{3D5A80}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{inksoft}{HTML}{555555}
\pagecolor{cream}
\begin{document}
\begin{tikzpicture}[
  >=Stealth,
  every state/.style={
    draw=ink,
    thick,
    minimum size=1.55cm,
    font=\bfseries\small,
    fill=cream
  },
  locked/.style={
    state,
    draw=coral,
    fill=coral!12,
    text=coral
  },
  unlocked/.style={
    state,
    accepting,
    draw=teal,
    fill=teal!10,
    text=teal
  },
  every edge/.style={draw, thick},
  every loop/.style={looseness=8, min distance=8mm},
  every initial by arrow/.style={-Stealth, thick, ink},
  initial text=start,
  font=\small
]
% States
\node[locked, initial, initial where=left] (L) {Locked};
\node[unlocked, right=3.6cm of L] (U) {Unlocked};

% Cross transitions — labels in the “eye” between the two arcs (textbook style)
\path[->]
  (L) edge[bend left=32, teal, line width=1.15pt]
      node[midway, yshift=-5pt, teal, font=\bfseries\small, inner sep=1pt] {coin}
      (U)
  (U) edge[bend left=32, coral, line width=1.15pt]
      node[midway, yshift=7pt, coral, font=\bfseries\small, inner sep=1pt] {push}
      (L);

% Self-loops: loop above, labels tight to loop
\path[->]
  (L) edge[loop above, amber, line width=1.0pt]
      node[above=1pt, amber, font=\bfseries\scriptsize] {push}
      (L)
  (U) edge[loop above, slate, line width=1.0pt]
      node[above=1pt, slate, font=\bfseries\scriptsize] {coin}
      (U);

% Legend — clear air below the lower arc
\node[below=14mm of $(L)!0.5!(U)$, inksoft, font=\scriptsize, align=center] (leg) {
  \textcolor{teal}{$\bullet$ coin unlocks}\quad
  \textcolor{coral}{$\bullet$ push walks through}\quad
  \textcolor{amber}{$\bullet$ ignored input loops}
};

% Transition table under legend
\node[below=5mm of leg, anchor=north] {
\begin{tabular}{@{}lll@{}}
\multicolumn{3}{@{}l@{}}{\textbf{\small transition table $\delta$}}\\[2pt]
\textit{\scriptsize state} & \textit{\scriptsize input} & \textit{\scriptsize next}\\
\textcolor{coral}{Locked} & \textcolor{teal}{coin} & \textcolor{teal}{Unlocked}\\
\textcolor{coral}{Locked} & \textcolor{amber}{push} & \textcolor{coral}{Locked}\\
\textcolor{teal}{Unlocked} & \textcolor{coral}{push} & \textcolor{coral}{Locked}\\
\textcolor{teal}{Unlocked} & \textcolor{slate}{coin} & \textcolor{teal}{Unlocked}\\
\end{tabular}
};

\end{tikzpicture}
\end{document}
"""


def main():
    td = tempfile.mkdtemp()
    tex_path = os.path.join(td, "fsm.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(TEX)
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "fsm.tex"],
        cwd=td,
        capture_output=True,
        text=True,
    )
    pdf = os.path.join(td, "fsm.pdf")
    if not os.path.isfile(pdf):
        print(r.stdout[-2500:])
        raise SystemExit(f"pdflatex failed: {r.returncode}")
    shutil.copy(pdf, OUT_PDF)
    doc = fitz.open(pdf)
    page = doc[0]
    mat = fitz.Matrix(5, 5)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.save(OUT_PNG, "PNG")
    doc.close()
    print("OK", OUT_PNG, img.size)


if __name__ == "__main__":
    main()
