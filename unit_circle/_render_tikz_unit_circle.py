"""
Render unit circle via TikZ (polar geometry) → high-res cream PNG.

TikZ is the right tool for this diagram: exact polar placement, LaTeX
fractions on rays, and a proper booktabs table — same pipeline as
circuitikz gates / TikZ automata FSM.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import fitz
from PIL import Image

OUT_DIR = os.path.dirname(__file__)
OUT_PNG = os.path.join(OUT_DIR, "_tikz_unit_circle.png")
OUT_PDF = os.path.join(OUT_DIR, "_tikz_unit_circle.pdf")

# Degrees and radians live on the SAME ray at different radii (all 16 angles).
# Coordinates sit outside the circle. Colors: teal = 30/60 family, rust = 45 family.
TEX = r"""
\documentclass[border=18pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{xcolor}
\definecolor{cream}{HTML}{F4F1EA}
\definecolor{creamy}{HTML}{FBF9F4}
\definecolor{teal}{HTML}{2F6F6A}
\definecolor{rust}{HTML}{B85C38}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{inksoft}{HTML}{555555}
\definecolor{inkfaint}{HTML}{8A857C}
\definecolor{grid}{HTML}{E6E2D8}
\pagecolor{cream}

% Ray helpers (defined outside tikzpicture)
% \ucray{angle}{deg}{rad}{coord}{color}  — full labels on true ray
\newcommand{\ucray}[5]{%
  \draw[#5, line width=0.85pt, opacity=0.88] (0,0) -- (#1:2.55);
  \fill[#5] (#1:2.55) circle[radius=1.35pt];
  \node[font=\scriptsize\bfseries, #5, inner sep=0.6pt,
        fill=creamy, fill opacity=0.88, text opacity=1, rounded corners=1pt]
        at (#1:1.32) {$#2$};
  \node[font=\scriptsize, inksoft, inner sep=0.5pt]
        at (#1:1.95) {$#3$};
  \node[font=\footnotesize\bfseries, #5, inner sep=1pt]
        at (#1:3.28) {$#4$};
}
% Cardinals: ray on true angle; deg/rad on slight angular nudge (same two radii)
\newcommand{\ucaxis}[5]{%
  % #1 ray  #2 label-angle  #3 deg  #4 rad  #5 color
  \draw[#5, line width=0.95pt, opacity=0.55] (0,0) -- (#1:2.55);
  \fill[#5] (#1:2.55) circle[radius=1.45pt];
  \node[font=\scriptsize\bfseries, #5, inner sep=0.6pt,
        fill=creamy, fill opacity=0.9, text opacity=1, rounded corners=1pt]
        at (#2:1.32) {$#3$};
  \node[font=\scriptsize, inksoft, inner sep=0.5pt]
        at (#2:1.95) {$#4$};
}

\begin{document}
\begin{tikzpicture}[>=Stealth, x=1cm, y=1cm, font=\small]

% soft card
\fill[creamy, rounded corners=6pt] (-4.45,-4.75) rectangle (4.65,4.55);
\draw[grid, rounded corners=6pt, thin] (-4.45,-4.75) rectangle (4.65,4.55);

% axes
\draw[ink, thick, ->] (-3.55,0) -- (3.55,0);
\node[ink, font=\small, anchor=west] at (4.05,0.22) {$x$};
\draw[ink, thick, ->] (0,-3.55) -- (0,3.55);
\node[ink, font=\small, anchor=south] at (0.28,3.95) {$y$};

% unit circle
\draw[ink, line width=1.35pt, fill=creamy] (0,0) circle[radius=2.55];
\draw[rust, line width=0.55pt, opacity=0.35] (0,0) circle[radius=2.55];
\fill[ink] (0,0) circle[radius=1.6pt];

% --- cardinals (deg + rad on same pattern as other rays) ---
\ucaxis{0}{12}{0^\circ}{0,\,2\pi}{ink}
\node[font=\footnotesize\bfseries, ink, anchor=west] at (3.20,0.38) {$(1,\,0)$};
\ucaxis{90}{78}{90^\circ}{\pi/2}{ink}
\node[font=\footnotesize\bfseries, ink, anchor=south west] at (0.28,3.10) {$(0,\,1)$};
\ucaxis{180}{168}{180^\circ}{\pi}{ink}
\node[font=\footnotesize\bfseries, ink, anchor=east] at (-3.20,0.38) {$(-1,\,0)$};
\ucaxis{270}{258}{270^\circ}{3\pi/2}{ink}
\node[font=\footnotesize\bfseries, ink, anchor=north west] at (0.28,-3.10) {$(0,\,-1)$};

% --- 30/60 family (teal) ---
\ucray{30}{30^\circ}{\pi/6}{\bigl(\tfrac{\sqrt{3}}{2},\,\tfrac{1}{2}\bigr)}{teal}
\ucray{60}{60^\circ}{\pi/3}{\bigl(\tfrac{1}{2},\,\tfrac{\sqrt{3}}{2}\bigr)}{teal}
\ucray{120}{120^\circ}{2\pi/3}{\bigl(-\tfrac{1}{2},\,\tfrac{\sqrt{3}}{2}\bigr)}{teal}
\ucray{150}{150^\circ}{5\pi/6}{\bigl(-\tfrac{\sqrt{3}}{2},\,\tfrac{1}{2}\bigr)}{teal}
\ucray{210}{210^\circ}{7\pi/6}{\bigl(-\tfrac{\sqrt{3}}{2},\,-\tfrac{1}{2}\bigr)}{teal}
\ucray{240}{240^\circ}{4\pi/3}{\bigl(-\tfrac{1}{2},\,-\tfrac{\sqrt{3}}{2}\bigr)}{teal}
\ucray{300}{300^\circ}{5\pi/3}{\bigl(\tfrac{1}{2},\,-\tfrac{\sqrt{3}}{2}\bigr)}{teal}
\ucray{330}{330^\circ}{11\pi/6}{\bigl(\tfrac{\sqrt{3}}{2},\,-\tfrac{1}{2}\bigr)}{teal}

% --- 45 family (rust) ---
\ucray{45}{45^\circ}{\pi/4}{\bigl(\tfrac{\sqrt{2}}{2},\,\tfrac{\sqrt{2}}{2}\bigr)}{rust}
\ucray{135}{135^\circ}{3\pi/4}{\bigl(-\tfrac{\sqrt{2}}{2},\,\tfrac{\sqrt{2}}{2}\bigr)}{rust}
\ucray{225}{225^\circ}{5\pi/4}{\bigl(-\tfrac{\sqrt{2}}{2},\,-\tfrac{\sqrt{2}}{2}\bigr)}{rust}
\ucray{315}{315^\circ}{7\pi/4}{\bigl(\tfrac{\sqrt{2}}{2},\,-\tfrac{\sqrt{2}}{2}\bigr)}{rust}

% legend
\node[font=\scriptsize, inksoft, anchor=north] at (0,-3.95) {%
  \textcolor{teal}{$\bullet$ $30^\circ/60^\circ$ family}\quad
  \textcolor{rust}{$\bullet$ $45^\circ$ family}\quad
  \textcolor{ink}{$\bullet$ axes}%
};

% booktabs table
\node[anchor=north] at (0,-4.85) {%
\renewcommand{\arraystretch}{1.18}%
\begin{tabular}{@{} r @{\hspace{10pt}} c @{\hspace{10pt}} c @{\hspace{10pt}} c
                 @{\hspace{18pt}}
                 r @{\hspace{10pt}} c @{\hspace{10pt}} c @{\hspace{10pt}} c @{}}
\multicolumn{8}{@{}l@{}}{%
  \textbf{\small special angles}\;
  \textcolor{inksoft}{\scriptsize $(x,y)=(\cos\theta,\,\sin\theta)$}%
}\\
\toprule
\multicolumn{1}{@{}c}{\textit{\scriptsize $\theta$}} &
\multicolumn{1}{c}{\textit{\scriptsize rad}} &
\multicolumn{1}{c}{\textit{\scriptsize $x$}} &
\multicolumn{1}{c}{\textit{\scriptsize $y$}} &
\multicolumn{1}{c}{\textit{\scriptsize $\theta$}} &
\multicolumn{1}{c}{\textit{\scriptsize rad}} &
\multicolumn{1}{c}{\textit{\scriptsize $x$}} &
\multicolumn{1}{c@{}}{\textit{\scriptsize $y$}} \\
\midrule
$0^\circ$   & $0$       & $1$            & $0$             &
$180^\circ$ & $\pi$     & $-1$           & $0$ \\
$30^\circ$  & $\pi/6$   & $\sqrt{3}/2$   & $1/2$           &
$210^\circ$ & $7\pi/6$  & $-\sqrt{3}/2$  & $-1/2$ \\
$45^\circ$  & $\pi/4$   & $\sqrt{2}/2$   & $\sqrt{2}/2$    &
$225^\circ$ & $5\pi/4$  & $-\sqrt{2}/2$  & $-\sqrt{2}/2$ \\
$60^\circ$  & $\pi/3$   & $1/2$          & $\sqrt{3}/2$    &
$240^\circ$ & $4\pi/3$  & $-1/2$         & $-\sqrt{3}/2$ \\
$90^\circ$  & $\pi/2$   & $0$            & $1$             &
$270^\circ$ & $3\pi/2$  & $0$            & $-1$ \\
$120^\circ$ & $2\pi/3$  & $-1/2$         & $\sqrt{3}/2$    &
$300^\circ$ & $5\pi/3$  & $1/2$          & $-\sqrt{3}/2$ \\
$135^\circ$ & $3\pi/4$  & $-\sqrt{2}/2$  & $\sqrt{2}/2$    &
$315^\circ$ & $7\pi/4$  & $\sqrt{2}/2$   & $-\sqrt{2}/2$ \\
$150^\circ$ & $5\pi/6$  & $-\sqrt{3}/2$  & $1/2$           &
$330^\circ$ & $11\pi/6$ & $\sqrt{3}/2$   & $-1/2$ \\
\bottomrule
\end{tabular}%
};

\end{tikzpicture}
\end{document}
"""


def main():
    td = tempfile.mkdtemp()
    tex_path = os.path.join(td, "uc.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(TEX)
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "uc.tex"],
        cwd=td,
        capture_output=True,
        text=True,
    )
    pdf = os.path.join(td, "uc.pdf")
    if not os.path.isfile(pdf) or os.path.getsize(pdf) < 5000:
        print(r.stdout[-3000:] if r.stdout else "")
        print(r.stderr[-1500:] if r.stderr else "")
        raise SystemExit(f"pdflatex failed: {r.returncode}, pdf size={os.path.getsize(pdf) if os.path.isfile(pdf) else 0}")
    shutil.copy(pdf, OUT_PDF)
    doc = fitz.open(pdf)
    page = doc[0]
    mat = fitz.Matrix(5, 5)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.save(OUT_PNG, "PNG")
    doc.close()
    print("OK", OUT_PNG, img.size, f"pdf={os.path.getsize(OUT_PDF)}B")


if __name__ == "__main__":
    main()
