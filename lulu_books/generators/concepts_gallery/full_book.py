"""full_book.py — the complete 18-plate 'The Shape of an Idea' book:
interior PDF (8.5x8.5 + bleed, 300 DPI) + front cover with logo."""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
from PIL import Image
import img2pdf

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, "..", "math_gallery")
sys.path.insert(0, MG)
import mini_book as MB  # noqa: E402
# math_gallery has its own plate_library.py (different content) -- make sure
# THIS directory takes priority so "import plate_library" resolves to ours.
sys.path.insert(0, HERE)
import plate_library as PL  # noqa: E402

OUT = os.path.join(HERE, "fullbook"); os.makedirs(OUT, exist_ok=True)
PGS = os.path.join(OUT, "pages"); os.makedirs(PGS, exist_ok=True)
DPI, PAGE_PX, DARK, PAPER, GOLD, ACC, INK, SUB = MB.DPI, MB.PAGE_PX, MB.DARK, MB.PAPER, MB.GOLD, MB.ACC, MB.INK, MB.SUB
CINZEL, CINZEL_R, RALEWAY, RALEWAY_I = MB.CINZEL, MB.CINZEL_R, MB.RALEWAY, MB.RALEWAY_I
LOGO = os.path.join(MB.REPO, "lulu_books", "assets", "img", "logo.png")

# ---- plate metadata: (title, [eqs], params, desc, gfn) ----
SECTIONS = [
 ("Foundations", [
  ("Euler's Identity", [r"$e^{i\pi}+1=0$"], r"$0,\,1,\,e,\,i,\,\pi$",
   "Five fundamental constants, from five different corners of mathematics, meet\nin a single equation. Rotate a unit vector by pi radians and you land\nexactly on -1 — arithmetic, algebra, analysis and geometry in one line.", PL.g_euler),
  ("The Golden Ratio", [r"$\varphi=\dfrac{1+\sqrt{5}}{2}$"], r"$\varphi \approx 1.618$",
   "Cut a square from a golden rectangle and what remains is another golden\nrectangle, forever. The whirling squares trace a spiral that widens by phi\nevery quarter turn — the same growth rule behind shells and sunflowers.", PL.g_golden),
  ("The Pythagorean Theorem", [r"$a^{2}+b^{2}=c^{2}$"], r"$\mathrm{right\ triangles}$",
   "The oldest theorem most people can still recite. Build a square on each side\nof a right triangle: the two smaller areas always add up, exactly, to the\nlargest. A truth so simple it has over 350 known proofs.", PL.g_pythagoras),
 ]),
 ("Waves & Signals", [
  ("Fourier Series", [r"$f(x)=\dfrac{a_0}{2}+\sum(a_n\cos nx+b_n\sin nx)$"], r"$N=1,3,7,31$",
   "Any periodic signal, however jagged, is secretly a sum of pure sine waves.\nAdd more harmonics and a smooth ripple sharpens toward a square wave —\nthe idea behind every digital filter and every note a synthesizer plays.", PL.g_fourier),
  ("The Wave Equation", [r"$\dfrac{\partial^{2}u}{\partial t^{2}}=c^{2}\dfrac{\partial^{2}u}{\partial x^{2}}$"], r"$\mathrm{speed}\ c$",
   "One equation governs sound in air, ripples on a pond, and light through\nspace. A disturbance keeps its shape while it travels — the reason a shout\nacross a canyon comes back to you still recognisably a shout.", PL.g_wave),
  ("The Normal Distribution", [r"$f(x)=\dfrac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^{2}/2\sigma^{2}}$"], r"$\mu,\,\sigma$",
   "Measure almost anything shaped by many small, independent causes — heights,\nerrors, exam scores — and this bell-shaped curve appears. About 68 percent\nof values fall within one standard deviation of the mean.", PL.g_bell),
 ]),
 ("Topology & Higher Dimensions", [
  ("The Mobius Strip", [r"$u\to u+2\pi\ \Rightarrow\ v\to-v$"], r"$\mathrm{one\ side,\ one\ edge}$",
   "Give a paper strip a half-twist before joining the ends and you build a\nsurface with only one side and one edge. Trace a finger along it and you\nvisit both 'faces' without ever lifting the pen.", PL.g_mobius),
  ("The Klein Bottle", [r"$\mathbb{R}^{3}\ \mathrm{immersion}$"], r"$\mathrm{no\ inside\ or\ outside}$",
   "A bottle whose neck reaches around and passes back through its own wall to\njoin its base from the inside — a surface with no inside or outside at all.\nIt only closes up properly in four dimensions; in three, it must cross itself.", PL.g_klein),
  ("The Tesseract", [r"$\{\pm1\}^{4}$"], r"$V{=}16,\,E{=}32,\,F{=}24$",
   "A cube has 8 vertices in three dimensions; its four-dimensional cousin has\n16. What you see is a shadow — a 3D projection of a rotating 4D object,\ncolour standing in for the axis we cannot draw.", PL.g_tesseract),
  ("Euler's Polyhedron Formula", [r"$V-E+F=2$"], r"$\mathrm{icosahedron:\ }12{-}30{+}20$",
   "Count the vertices, edges and faces of any convex polyhedron — a cube, a\npyramid, this twenty-faced icosahedron — and the same combination always\ncomes out to 2. A single invariant tying together every possible shape.", PL.g_polyhedron),
 ]),
 ("Chaos & Flow", [
  ("The Koch Snowflake", [r"$N_n=3\cdot4^{n}$"], r"$n=4$",
   "Replace the middle third of every side with a triangular bump, forever, and\na triangle grows into a snowflake. The perimeter lengthens without bound —\nyet the whole curve still encloses a stubbornly finite area.", PL.g_koch),
  ("The Navier–Stokes Equations", [r"$\rho\dfrac{D\mathbf{u}}{Dt}=-\nabla p+\mu\nabla^{2}\mathbf{u}$"], r"$\mathrm{sources,\ sinks,\ vortices}$",
   "The equations that govern every fluid that has ever flowed — air over a\nwing, blood through a vein, weather across a continent. Simple to write,\nnotoriously hard to solve: a full proof of smoothness is still unsolved.", PL.g_navier),
  ("The Dirac Equation", [r"$(i\gamma^{\mu}\partial_{\mu}-m)\psi=0$"], r"$\mathrm{matter\ and\ antimatter}$",
   "Written to make quantum mechanics agree with relativity, this equation had\na strange side effect: it predicted a mirror particle for every one we\nknew. Antimatter was discovered on paper before it was found in a lab.", PL.g_dirac),
  ("The Logistic Map", [r"$x_{n+1}=r\,x_n(1-x_n)$"], r"$r=2.4\ \mathrm{to}\ 4.0$",
   "A population model almost embarrassingly simple — breed, then crowd out —\nyet turning one dial smoothly slides it from a single steady population,\nthrough repeating cycles, into full deterministic chaos.", PL.g_logistic),
 ]),
 ("Paradox & Infinity", [
  ("Hilbert's Infinite Hotel", [r"$n \to n+1$"], r"$\aleph_0\ \mathrm{rooms}$",
   "A hotel with infinitely many rooms, every one occupied, can still make\nroom for a new guest: just shift everyone from room n to room n+1. Room\none opens up — infinity minus one is still infinity.", PL.g_hilbert_hotel),
  ("The Cantor Set", [r"$C=\bigcap_n C_n$"], r"$\mathrm{remove\ the\ middle\ third,\ forever}$",
   "Delete the middle third of a line, then the middle third of what remains,\nforever. What's left has zero length — yet just as many points as the\nline you started with. Two very different sizes of infinity, side by side.", PL.g_cantor),
  ("Zeno's Paradox", [r"$\sum_{k=0}^{\infty}\dfrac{1}{2^{k}}=2$"], r"$\mathrm{Achilles\ and\ the\ tortoise}$",
   "To cross a room you must first cross half of it, then half of what's left,\nforever — infinitely many steps. Yet the infinite sum of ever-smaller\nsteps adds up to a perfectly finite distance, and you do reach the wall.", PL.g_zeno),
  ("The Monty Hall Problem", [r"$P(\mathrm{switch})=\dfrac{2}{3}$"], r"$3\ \mathrm{doors,\ 1\ prize}$",
   "Pick one of three doors; the host, who knows what's behind them, opens\nanother to reveal a goat and offers you a switch. It feels like fifty-fifty.\nIt isn't — switching wins twice as often as staying.", PL.g_monty),
 ]),
]

ROMAN = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII".split()


def title_page():
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.plot([0.30, 0.70], [0.66, 0.66], color=ACC, lw=1.4)
    ax.text(0.5, 0.59, "THE SHAPE", fontproperties=CINZEL, fontsize=41, color=INK, ha="center")
    ax.text(0.5, 0.515, "OF AN IDEA", fontproperties=CINZEL, fontsize=41, color=INK, ha="center")
    ax.text(0.5, 0.43, "A Gallery of Great Equations & Concepts",
            fontproperties=RALEWAY_I, fontsize=17, color=SUB, ha="center")
    ax.plot([0.30, 0.70], [0.37, 0.37], color=ACC, lw=1.4)
    ax.text(0.5, 0.11, "MathRelaxing", fontproperties=CINZEL_R, fontsize=16, color=INK, ha="center")
    return MB.to_pil(fig, PAPER)


def divider_page(label):
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.5, label, fontproperties=CINZEL, fontsize=30, color=INK, ha="center", va="center")
    ax.plot([0.42, 0.58], [0.44, 0.44], color=ACC, lw=1.3)
    return MB.to_pil(fig, PAPER)


def simple_text_page(lines):
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    y = 0.62
    for txt, fp, sz, col in lines:
        ax.text(0.5, y, txt, fontproperties=fp, fontsize=sz, color=col,
                ha="center", va="top", linespacing=1.7, wrap=True)
        y -= 0.09 + 0.006 * sz
    return MB.to_pil(fig, PAPER)


def text_page(section, title, eqs, params, desc, plate):
    fig, ax = MB.fig_trim(PAPER); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.17, 0.82, section, fontproperties=CINZEL_R, fontsize=14, color=ACC)
    ax.plot([0.17, 0.17 + 0.011 * len(section)], [0.797, 0.797], color=ACC, lw=1.3)
    ts = 30 * min(1.0, 20 / max(len(title), 1))
    ax.text(0.17, 0.715, title, fontproperties=CINZEL, fontsize=ts, color=INK)
    n = len(eqs); y0 = 0.55 + (n - 1) * 0.038
    for i, e in enumerate(eqs):
        ax.text(0.19, y0 - i * 0.076, e, fontsize=24, color=INK, va="center")
    if params:
        ax.text(0.17, 0.335, params, fontsize=15, color=SUB)
    ax.text(0.17, 0.27, desc, fontproperties=RALEWAY, fontsize=13.5, color="#403c34", va="top", linespacing=1.6)
    ax.plot([0.17, 0.83], [0.085, 0.085], color="#d8d0be", lw=1.1)
    ax.text(0.17, 0.055, plate, fontproperties=CINZEL_R, fontsize=12, color=SUB, va="center")
    ax.text(0.83, 0.055, "MathRelaxing", fontproperties=RALEWAY_I, fontsize=12, color=SUB, ha="right", va="center")
    return MB.to_pil(fig, PAPER)


def build():
    pages = []
    pages.append((title_page(), PAPER))
    pages.append((simple_text_page([
        ("Foreword", CINZEL, 22, INK),
        ("Not every mathematical object is a graph or a curve. Some are pure\n"
         "ideas — a proof, a paradox, a shape that only closes up properly in a\n"
         "dimension we cannot see.\n\n"
         "This gallery pairs eighteen of them with the equation or argument behind\n"
         "each: the constant, the theorem, the strange bottle. On the left, the idea\n"
         "and a few words. On the right, the picture it draws.",
         RALEWAY, 15, "#403c34"),
    ]), PAPER))
    pages.append((divider_page("THE PLATES"), PAPER))

    idx = 0
    for sec, plates in SECTIONS:
        pages.append((divider_page(sec.upper()), PAPER))
        for title, eqs, params, desc, gfn in plates:
            print(f"  plate {ROMAN[idx]}: {title}")
            bg = DARK if gfn in (PL.g_euler, PL.g_wave, PL.g_mobius, PL.g_klein,
                                  PL.g_tesseract, PL.g_polyhedron, PL.g_navier,
                                  PL.g_dirac, PL.g_logistic) else PAPER
            pages.append((text_page(sec, title, eqs, params, desc, f"PLATE {ROMAN[idx]}"), PAPER))
            pages.append((gfn(), bg))
            idx += 1

    pages.append((simple_text_page([
        ("Colophon", CINZEL, 20, INK),
        ("Every plate was generated from its own mathematics — nothing traced,\n"
         "nothing drawn by hand. The topological pieces are real 3D renders,\n"
         "shown as woven contour lines rather than solid surfaces. Typeset in\n"
         "Cinzel and Raleway; equations in Computer Modern.\n\nMade by MathRelaxing.",
         RALEWAY, 14, "#403c34"),
    ]), PAPER))

    paths = []
    for i, (img, bg) in enumerate(pages):
        p = os.path.join(PGS, f"p{i:02d}.jpg")
        MB.pad_bleed(img, bg).save(p, "JPEG", quality=92, dpi=(DPI, DPI))
        paths.append(p)
    pdf = os.path.join(OUT, "interior.pdf")
    layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(paths, layout_fun=layout))
    print(f"\ninterior.pdf: {len(pages)} pages, {os.path.getsize(pdf)//1024//1024} MB")
    return pdf, pages


if __name__ == "__main__":
    build()
