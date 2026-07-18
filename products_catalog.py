"""
products_catalog.py  —  MathRelaxing Etsy Product Catalog
===========================================================
Script base para que cualquier IA agéntica pueda publicar productos en Etsy
sin partir de cero. Solo instancia EtsyManager e invoca upload_product().

Estructura de la carpeta local (G:/Mi unidad/Etsy/):
  fractal_flora_*.{jpg,pdf,mp4}
  sacred_geometry_*.{jpg,pdf,mp4}
  hyperbolic_gardens_digital.pdf
  mathematical_tangle_art_digital.pdf
  sacred_harmonics_digital.pdf
  ipad_ff/  — bundle iPad Fractal Flora
  ipad_sg/  — bundle iPad Sacred Geometry
  thomas_attractor_loop.mp4 + thomas_preview_*.jpg

Notas importantes para la IA agéntica:
  - EtsyManager.create_full_product sube hasta 5 archivos digitales por listing.
  - Los vídeos (.mp4) se suben como "imagen" rank=1 vía upload_listing_image
    (Etsy acepta vídeo como primer slot de galería). EtsyManager ya lo soporta.
  - taxonomy_id: usar get_taxonomy_id() para buscar el correcto, o pasar
    TAXONOMY["coloring_book"] como punto de partida.
  - Los productos sin imágenes (HG, MTA, SH) necesitan previewss antes de publicar.
  - Siempre se crea en estado "draft"; la activación es manual desde Etsy.
"""

import os
import etsy_manager

# ── Ruta base ────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
FF   = os.path.join(BASE, "ipad_ff")
SG   = os.path.join(BASE, "ipad_sg")

def p(*parts): return os.path.join(BASE, *parts)
def ff(*parts): return os.path.join(FF, *parts)
def sg(*parts): return os.path.join(SG, *parts)

# ── Taxonomy IDs verificados ──────────────────────────────────────────────────
# Fuente: GET /application/seller-taxonomy/nodes (llamada al API de Etsy)
# Para descubrir IDs ejecutar: manager.make_request('GET', '/application/seller-taxonomy/nodes')
# IDs verificados contra el árbol real de Etsy: GET /seller-taxonomy/nodes
# (OJO: la ruta correcta es '/seller-taxonomy/nodes' — base_url ya incluye /v3/application)
TAXONOMY = {
    "coloring_book":    2078,   # = "Art & Collectibles > Prints > Digital Prints" (lo usan FF/SG PDF)
    "ipad_coloring":    339,    # = "Books, Movies & Music > Books > Coloring Books" (ediciones iPad)
    "digital_art":      2078,   # = Digital Prints (atractores/art prints)
    "planner_template": 12476,  # = "Paper > Stationery > Templates > Planner Templates" (notebooks/planners digitales)
    "journal_template": 12475,  # = "... > Templates > Journal Templates" (variante journal/cuaderno)
    "root":             1,      # fallback genérico
}

# ── Copy de productos ─────────────────────────────────────────────────────────
DESCRIPTIONS = {

    "fractal_flora_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
Lose yourself in 50 unique fractal & botanical line-art designs: Dragon Curves, \
Julia Sets, Barnsley Ferns, twin fractals, and more — all drawn with mathematical \
precision and free of color numbers.

► What you get
• 1 high-resolution PDF (print-ready, 300 dpi equivalent)
• 50 original line-art designs — no clip-art, no AI

► Print it once, color it endlessly — or use it on your iPad with GoodNotes.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "sacred_geometry_pdf": """\
Instant download — color-by-number PDF coloring book (50 pages, 8.5×11 in).
50 stunning low-poly sacred geometry designs: mandalas, metatrons, tori, \
Platonic solids, flower of life — each with a numbered color guide so you \
always know exactly where each hue goes.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 color-by-number designs with palette guide
• Meditative, screen-free relaxation

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "hyperbolic_gardens_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
Journey into hyperbolic geometry with 50 intricate tiling designs inspired \
by Escher's Circle Limit series and the Poincaré disc model. Each design \
repeats to infinity toward the boundary — a meditative coloring experience \
unlike any other.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original hyperbolic tiling designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "mathematical_tangle_art_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 elaborate Zentangle-inspired designs built from pure mathematical curves: \
Lissajous figures, rose curves, epicycloids, spirals and more — woven into \
dense, meditative patterns for hours of mindful coloring.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original mathematical tangle designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "sacred_harmonics_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 designs where sound meets sacred geometry: Chladni figures, cymatics \
patterns, harmonic wave interference, and resonant mandalas — the hidden \
geometry of vibration made visible and colorable.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original cymatics & harmonic designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "neural_network_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 futuristic designs blending neural network architectures, cybernetic circuits, \
and complex radial graph topologies. Perfect for coders, AI enthusiasts, \
and anyone who loves high-tech geometry.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original neural network & tech art designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "fractal_flora_ipad": """\
Instant download — iPad coloring bundle for GoodNotes, Notability & Procreate.
50 fractal & botanical line-art designs, fully optimized for digital coloring \
with Apple Pencil. Tap any thumbnail to jump straight to a design, paint \
beneath the transparent PNG layers, or mix your own colors with the included \
Procreate palette.

► What's included (5 files)
• Hyperlinked PDF — tap-to-navigate index + 50 designs (GoodNotes / Notability)
• 50 transparent PNGs at 300 dpi — part 1 of 2 (ZIP)
• 50 transparent PNGs at 300 dpi — part 2 of 2 (ZIP)
• FractalFlora.swatches — 30-color garden palette for Procreate
• How to use on iPad (PDF guide)

► How to use
GoodNotes / Notability: open the PDF, tap a thumbnail, color right on top.
Procreate: import a PNG, paint on a layer below the linework.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "sacred_geometry_ipad": """\
Instant download — iPad coloring bundle for GoodNotes, Notability & Procreate.
50 low-poly sacred geometry color-by-number designs, fully optimized for \
digital coloring with Apple Pencil. Each numbered facet fills perfectly — \
no bleeding, no guesswork. Tap any thumbnail to navigate instantly.

► What's included (5 files)
• Hyperlinked PDF — tap-to-navigate index + 50 designs (GoodNotes / Notability)
• 50 transparent PNGs at 300 dpi — part 1 of 2 (ZIP)
• 50 transparent PNGs at 300 dpi — part 2 of 2 (ZIP)
• SacredGeometry.swatches — 30-color sacred palette for Procreate
• How to use on iPad (PDF guide)

► How to use
GoodNotes / Notability: open the PDF, tap a thumbnail, color right on top.
Procreate: import a PNG, paint on a layer below the numbered linework.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "thomas_attractor": """\
Instant download — seamless loop animation (MP4, 1080×1080, 60 fps, 12 s).
The Thomas attractor — a chaotic dynamical system — rendered as a glowing \
density cloud in gold and aqua. Every frame is a new cross-section of an \
infinite 3-D trajectory. Loops perfectly for wallpapers, screensavers, \
digital frames, or social media backgrounds.

► What you get
• 1 MP4 file — 1080×1080 px, 60 fps, 12-second seamless loop
• Silent (add your own music or keep it ambient)

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "voronoi_gardens_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 mesmerizing Voronoi designs grown from pure mathematics: radial mandalas, \
golden-angle sunflower spirals, cathedral rose windows and softly relaxed \
organic cells. Every cell is a closed region — perfect for clean, satisfying \
color fills.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original Voronoi designs — mandalas, phyllotaxis, rose windows & organic cells
• Title page, "about" & "the mathematics" intro pages

► Print it once, color it endlessly — or use it on your iPad with GoodNotes.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "stem_focus_planner": """\
Instant download — undated STEM focus planner for GoodNotes, Notability & any PDF app. \
A minimalist, hyperlinked planner built for students, researchers and analytical minds — \
cream & gold MathRelaxing aesthetic, not another generic wellness journal.

► What's inside (35 hyperlinked pages)
• 1 yearly overview · 6 undated monthly spreads
• 6 weekly + 10 daily layouts  
• 5 STEM templates: research log, problem-solving Cornell, 52-week habit grid, project planner
• 4 academic templates: lab notes, data analysis, literature review, meeting notes
• Formula reference page · graph paper · dot grid notes
• Index buttons + side-tab navigation on every page
• Bonus: 14 mathematical stickers (π, ∫, Σ, ∞, equations, geometric patterns)

► How to use
Import the PDF into GoodNotes or Notability, tap any section on the index or the \
side tabs to jump. Duplicate any page as often as you like — start any month, any year. \
Use the included stickers to mark important equations, deadlines, or achievements.

This is a DIGITAL file — no physical product is shipped.
© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "stem_notebook": """\
Instant download — hyperlinked STEM digital notebook for GoodNotes, Notability \
& any PDF app. 142 pages of the grids science, engineering & math students \
actually need — with tap-to-jump tabs so you never scroll.

► 7 grid types (20 pages each)
• Dot grid  •  Graph / quad ruled  •  Hexagonal (organic chemistry)
• Isometric (3D & engineering)  •  Cornell notes  •  Polar  •  Lined

► Why you'll love it
• Tabbed navigation — tap a side tab to jump to any grid instantly
• Landscape 4:3, sized perfectly for iPad
• Reuse forever — duplicate any page as many times as you like
• Clean, distraction-free design with subtle grid lines

► How to use
Import the PDF into GoodNotes or Notability (or any annotation app), open it, \
and tap the side tabs to navigate. Write with your Apple Pencil on any page.

This is a DIGITAL file — no physical product is shipped.
© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "voronoi_gardens_ipad": """\
Instant download — iPad coloring bundle for GoodNotes, Notability & Procreate.
50 Voronoi designs — radial mandalas, golden-angle spirals, rose windows and \
organic cells — optimized for digital coloring with Apple Pencil. Tap any \
thumbnail to jump straight to a design, or paint beneath the transparent PNG \
layers with the included palette.

► What's included (5 files)
• Hyperlinked PDF — tap-to-navigate index + 50 designs (GoodNotes / Notability)
• 50 transparent PNGs at 300 dpi — part 1 of 2 (ZIP)
• 50 transparent PNGs at 300 dpi — part 2 of 2 (ZIP)
• VoronoiGardens.swatches — 30-color palette for Procreate
• How to use on iPad (PDF guide)

► How to use
GoodNotes / Notability: open the PDF, tap a thumbnail, color right on top.
Procreate: import a PNG, paint on a layer below the cell outlines.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "julia_morph_01": """\
Instant download — seamless loop animation (MP4, 1080×1080, 60 fps, ~12 s).
A Julia set fractal endlessly morphing as its parameter glides around the edge \
of the Mandelbrot set — rendered as a glowing teal-and-gold form on deep navy. \
Every frame is mathematically generated; the loop is perfect, with no visible cut.

► What you get
• 1 MP4 file — 1080×1080 px, 60 fps, seamless ~12-second loop
• Silent — perfect for wallpapers, screensavers, digital frames & social backgrounds

► Art born from equations.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "islamic_geometry_pdf": """\
Instant download — color-by-number PDF coloring book (50 pages, 8.5×11 in).
50 geometric star rosettes built the same way real Islamic geometric artisans \
laid out star patterns — compass-and-circle constructions formalized as an \
algorithm. Octagrams, decagrams, dodecagrams and more, each with a numbered \
color guide so every facet is exactly where it belongs.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 color-by-number star rosette designs with palette guide
• Meditative, screen-free relaxation

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "celtic_knot_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 interlace knotwork designs generated by the same grid logic real Celtic \
artisans used centuries ago — now formalized as an algorithm. Endless woven \
bands, alternating over-under crossings, and two classic named motifs (the \
Trinity Shamrock and the Triskelion), all rendered as clean, numberless line art.

► What you get
• 1 high-resolution PDF (print-ready, vector-quality lines)
• 50 original knotwork designs — from simple bordered panels to dense, \
intricate weaves
• Title page & "the mathematics" intro page explaining the grid algorithm

► Print it once, color it endlessly — or use it on your iPad with GoodNotes.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "islamic_geometry_ipad": """\
Color by number on your iPad — no printer, no mess.

This is the iPad Edition of Islamic Star Geometry: 50 color-by-number star \
rosette designs, ready to color right on your tablet in GoodNotes, Notability \
or Procreate.

────────────────────────────────
WHAT YOU GET
────────────────────────────────
✦ Hyperlinked PDF — tap any design in the index to jump straight to it (GoodNotes / Notability)
✦ 50 transparent PNGs (300 dpi) — color on a layer beneath the lines in Procreate
✦ Procreate color palette (.swatches) — match every number in one tap
✦ "How to use on iPad" quick guide
✦ Instant download — start coloring in minutes

────────────────────────────────
HOW IT WORKS
────────────────────────────────
GOODNOTES / NOTABILITY → import the PDF, tap a thumbnail, color on top with the Apple Pencil.
PROCREATE → drop a PNG on a canvas, color underneath the transparent line art, load the palette.

────────────────────────────────
ABOUT THE ART
────────────────────────────────
50 geometric star rosettes generated algorithmically from real compass-and-circle \
Islamic geometric construction rules — original code by the artist, not AI image generators.

© MathRelaxing. This file is for personal use only.
Redistribution, resale, or commercial use is strictly prohibited.""",

    "celtic_knot_ipad": """\
Instant download — iPad coloring bundle for GoodNotes, Notability & Procreate.
50 woven Celtic knotwork designs, optimized for digital coloring with Apple \
Pencil. Every strand is a true over-under ribbon — tap any thumbnail to jump \
straight to a design, or paint beneath the transparent PNG layers with the \
included Celtic palette.

► What's included (5 files)
• Hyperlinked PDF — tap-to-navigate index + 50 designs (GoodNotes / Notability)
• 50 transparent PNGs at 300 dpi — part 1 of 2 (ZIP)
• 50 transparent PNGs at 300 dpi — part 2 of 2 (ZIP)
• CelticKnot.swatches — 30-color Celtic palette for Procreate
• How to use on iPad (PDF guide)

► How to use
GoodNotes / Notability: open the PDF, tap a thumbnail, color right on top.
Procreate: import a PNG, paint on a layer below the woven bands.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "voronoi_cell_garden": """\
A living mosaic that never stops breathing.

This is a Voronoi cell tessellation — the mathematical pattern behind soap \
bubbles, giraffe spots, and dragonfly wings — arranged along a golden-angle \
spiral and set into gentle, endless motion. Every cell pulses on its own \
rhythm in a seamless loop: deep amethyst at the core fading through rose and \
magenta into warm gold at the edges, with softly glowing stained-glass \
borders between every facet.

────────────────────────────────
WHAT YOU GET
────────────────────────────────
✦ 1 MP4 video file (H.264)
✦ 1080 x 1080 square format
✦ 30 fps — smooth, fluid motion
✦ 10-second perfect seamless loop
✦ Instant digital download — no waiting, no shipping

────────────────────────────────
PERFECT FOR
────────────────────────────────
✦ Animated / live wallpaper (Wallpaper Engine, Lively Wallpaper)
✦ Ambient visuals on a TV or monitor
✦ Meditation, focus & relaxation backdrops
✦ Backgrounds for videos, streams & social media
✦ Lovers of math, generative art & stained glass design

────────────────────────────────
HOW TO USE
────────────────────────────────
Download the MP4 after purchase. Set it as a live wallpaper, loop it on any \
screen, or drop it into your video/stream editor. Plays on any modern device \
or player.

────────────────────────────────
ABOUT THE ART
────────────────────────────────
Generated algorithmically: 90 seed points are placed along a golden-angle \
spiral, then each one orbits its own position at an exact integer frequency \
— so after one full loop every cell returns to its precise starting shape, \
and the first frame connects perfectly to the last. Rendered from scratch \
with original Python code, not AI image generators.

© MathRelaxing. This file is for personal use only.
Redistribution, resale, or commercial use is strictly prohibited.""",

    "quantified_self_planner": """\
Treat your life like a dataset. The Quantified Self Journal is a hyperlinked digital \
planner designed for data lovers, software engineers, and analytical minds.

Move beyond simple to-do lists and visualize your progress with a 365-day \
GitHub-style heatmap, monthly scatter plots, bar charts, and weekly agile \
sprint Kanban boards. 

────────────────────────────────
WHAT YOU GET
────────────────────────────────
✦ 1 Hyperlinked PDF (127 pages)
✦ YER (Yearly Heatmap Tracker)
✦ MON (12 Monthly Data Trackers & Goals)
✦ WEK (52 Weekly Agile Sprints / Kanban boards)
✦ DAY (31 Daily Pomodoro & Focus Trackers)
✦ DAT (10 Isometric & Dot Grid notes pages)

Designed with our elegant Dark Mode (Navy & Gold) aesthetic to match your \
favorite IDE and reduce eye strain.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "spiral_tilings_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 mesmerizing spiral tilings generated from pure mathematics: complex exponential \
mappings, logarithmic spirals, and interlocked radial mandalas. \
Each design repeats and rotates seamlessly, offering an incredibly satisfying \
coloring experience as you follow the fractal-like curves outward.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original parametric spiral designs
• "The mathematics" intro page explaining the mapping algorithms

► Print it once, color it endlessly — or use it on your iPad with GoodNotes.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "spiral_tilings_ipad": """\
Experience the meditative flow of Color-by-Number with the endless mathematics of spirals, right on your iPad with this fully INTERACTIVE app-like experience.

This digital bundle features 50 original radial designs. It is NOT a static PDF. Instead, you get 50 interactive HTML files that run directly in your iPad's Safari browser (no internet required). Because they use vector SVG graphics, you can zoom in infinitely without ANY pixelation. No more blurry lines or numbers crashing into borders!

Features:
• Infinite zoom with perfectly crisp lines (SVG format)
• Tap-to-fill: Select a color from the palette and tap a cell to instantly fill it
• Auto-hiding numbers: Numbers disappear magically when you color a cell
• Save your progress offline
• 50 unique mathematically-generated designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "happy_chemicals_prints": """\
Instant download — Happy Chemicals print set (4 science wall-art posters).

Four minimalist molecular structure prints on a warm paper aesthetic — \
clean ink lines, generous negative space, gallery-ready:

• Serotonin — the happiness chemical
• Dopamine — the reward chemical
• Oxytocin — the bonding hormone
• Caffeine — the focus molecule

Perfect for therapy offices, psychology & neuroscience spaces, coffee nooks, \
classrooms, dorms, and science-lover gifts.

► What you get
• 4 original molecule art prints (JPG, 300 dpi)
• Multiple sizes per print: 5×7, 8×10, 11×14, 16×20, A4, A3
• Print at home or any print shop (matte / textured paper looks best)
• Instant download ZIP — no physical item ships

► Style
Warm paper background with a soft color wash, double decorative frame, \
rich atom colors (N blue, O coral, S gold), charcoal bonds, italic titles.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "cs_poster_set": """\
Instant download — Computer Science educational wall-art poster set (7 scientific plates).

Seven clean classroom-ready diagrams in the MathRelaxing scientific-plate style — \
cream graph paper, LaTeX equations, and a soft color palette:

1. How Algorithms Grow — Big-O complexity curves
2. Ordered by Comparison — Binary search tree
3. Sorted by Comparison — Bubble vs merge sort
4. Boolean Building Blocks — Logic gates (AND, OR, NOT, XOR, NAND, NOR)
5. Seven Layers of the Network — OSI model
6. LIFO and FIFO — Stack and queue
7. States and Transitions — Finite state machine (turnstile)

► What you get
• 7 original educational posters (JPG)
• Multiple aspect ratios: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Print-ready resolution for home or print shop
• Delivered as one ZIP — instant download

Perfect for CS classrooms, coding bootcamps, home offices, and STEM gifts.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "stem_lab_notebook": """\
Instant download — STEM Lab Notebook printable PDF (48 pages, US Letter).

A clean scientific notebook for real experiments — not a generic planner. Built for \
students, teachers, undergrads, and makers who want the scientific method laid out \
clearly on paper or iPad.

► What's inside
• 12 scientific-method experiment logs (hypothesis → procedure → data → conclusion)
• Data tables for raw measurements
• Observation + sketch pages
• 5 mm graph paper and dot grid
• Chemistry, Physics, and Biology note layouts
• Lab inventory + pre-lab safety checklist
• Lined notes for freeform writing
• Hyperlinked index and side tabs for GoodNotes / Notability

► Print or digital
Print at home (letter 8.5×11 in) or import the PDF into GoodNotes, Notability, or \
any PDF annotation app. Undated — duplicate any page as many times as you need.

► Perfect for
High school & college labs, AP science, research notebooks, homeschool science, \
and STEM gifts.

This is a DIGITAL file — no physical product is shipped.
© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "schrodinger_equation_print": """\
Instant download — Physics Wall Art.

The Shape Of Probability - a scientific-plate art print.

The Schrödinger equation says a particle is a wave of probability ψ. Squaring it gives |ψ|² — the chance of finding the particle at each place. In a one-dimensional box the allowed waves are standing modes: higher n, more nodes, higher energy. This plate shows the ground state and first two excited states with their probability densities.

Every line is computed from the physics - not stock art, not AI.

WHAT YOU GET (instant download)
- 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A
- 300 DPI - print small or large
- Delivered as one ZIP

Print at home, a print shop, or an online lab. For personal use. Frame not included.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "fourier_series_print": """\
Instant download — Math Wall Art scientific plate.

The Shape of Waves — Fourier series building a square wave from pure sinusoids \
(partial sums N = 1, 3, 7, 25). Cream graph paper, true LaTeX equations, rust accent.

Every curve is computed from the math — not stock art, not AI.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

Perfect for STEM classrooms, offices, dorms, and math-lover gifts. Matte paper looks best.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "wave_equation_print": """\
Instant download — Physics Wall Art scientific plate.

The Traveling Wave — the 1D wave equation with standing-wave modes n = 1, 2, 3 \
on a fixed string (nodes, antinodes, harmonics). Cream graph paper + LaTeX.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

Perfect for physics classrooms, labs, and STEM wall galleries.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "dirac_equation_print": """\
Instant download — Physics Wall Art scientific plate.

Matter and Antimatter — the Dirac equation with the relativistic ± energy continuum \
and mass gap. Cream graph paper, LaTeX typography, rust accent.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

For quantum / relativity fans, physics offices, and classroom walls.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "navier_stokes_print": """\
Instant download — Physics Wall Art scientific plate.

The Equations of Flow — Navier–Stokes with potential-flow streamlines past a cylinder. \
Cream graph paper, LaTeX equations, engineering-plate style.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

Ideal for engineers, fluid-dynamics students, and modern STEM decor.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "euler_identity_print": """\
Instant download — Math Wall Art scientific plate.

The Most Beautiful Equation — Euler's identity e^(iπ)+1=0 on the complex unit circle. \
Cream graph paper, LaTeX math, minimal editorial layout.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

A classic for math classrooms, study nooks, and gifts for number lovers.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "mandelbrot_set_print": """\
Instant download — Math Wall Art scientific plate.

The Geometry of Chaos — Mandelbrot set escape-time portrait with z→z²+c. \
Scientific cream / ink / rust palette (not neon fractal kitsch). LaTeX equations.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

For chaos-theory fans, coders, and modern math wall galleries.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "bessel_functions_print": """\
Instant download — Physics Wall Art scientific plate.

Waves in a Circle — Bessel functions J0, J1, J2 with zeros marked (circular drum \
modes / cylindrical waves). Cream graph paper, true LaTeX, computed with scipy.special.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

Perfect for physics classrooms, acoustics, and STEM gallery walls.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "hermite_qho_print": """\
Instant download — Physics Wall Art scientific plate.

The Quantum Spring — harmonic oscillator states n = 0..3 with Hermite × Gaussian \
wavefunctions and |ψ|² densities. Energies E = ℏω(n+1/2). LaTeX + scipy.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

For quantum mechanics students, physics offices, and STEM gifts.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "legendre_polynomials_print": """\
Instant download — Math Wall Art scientific plate.

Polynomials on the Sphere — Legendre P0..P4 on [-1,1], the orthogonal basis behind \
multipoles and spherical harmonics. Cream graph paper, LaTeX, scipy.special.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

Ideal for math classrooms, gravity/electrostatics context, and modern STEM decor.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "mandelbrot_zoom_print": """\
Instant download — Math Wall Art scientific plate.

Infinite Coastline — deep Mandelbrot zoom (seahorse valley) with smooth escape-time \
coloring. Companion plate to the classic full-set Mandelbrot portrait. Cream/ink/rust.

► What you get
• 1 scientific-plate print (high-quality JPG)
• Aspect ratios @ 300 dpi: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• Instant download ZIP — no physical item ships

For chaos-theory fans, fractal lovers, and math gallery walls.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "famous_equations_set": """\
Instant download — Famous Equations wall art set of 6 scientific plates.

Six MathRelaxing gallery prints in one download:
1. Fourier Series — square-wave harmonics
2. Wave Equation — standing modes on a string
3. Dirac Equation — matter & antimatter continuum
4. Navier–Stokes — flow past a cylinder
5. Euler's Identity — complex unit circle
6. Mandelbrot Set — geometry of chaos

Same cream graph-paper family as our Maxwell / Schrödinger plates. LaTeX equations.

► What you get
• 6 scientific-plate designs
• Masters @ 300 dpi (12×18 / 2:3 + A4 per design)
• Instant download ZIP — no physical item ships

Build a STEM gallery wall in one click. Matte paper recommended.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "unit_circle_print": """\
Instant download — Unit Circle trigonometry wall art (scientific plate).

A clean educational reference for high school, precalculus, and college trig: \
degrees, radians, and exact coordinates (x, y) = (cos θ, sin θ) on the unit circle.

Styled as a MathRelaxing scientific plate — cream graph paper, LaTeX math, \
and a soft teal/rust palette (not a generic gray classroom cheat sheet).

► What you get
• 1 original unit-circle plate (JPG)
• Multiple aspect ratios: 2:3, 3:4, 4:5, 5:7, ISO A4, A3
• 300 dpi print-ready files
• Instant download ZIP — no physical item ships

Perfect for math classrooms, tutoring walls, dorm STEM decor, and teacher gifts.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "reader_os_stickers": """\
Instant download — Reader OS digital sticker system for iPad readers.

Made for digital reading logs on iPad (GoodNotes, Notability, Procreate, Freeform) \
and other tablet / e-reader journals. Not a random cute pack — a functional sticker \
system for your reading life.

Six modules that work together:
• STATUS — Currently Reading, TBR, DNF, Finished, On Hold, Reread, Up Next, Book Mail
• PROGRESS — 10%–100% rings, Last Chapter, Cliffhanger
• RATING — 1–5 stars with labels + Life Changing
• GENRE — Fantasy, Romance, Thriller, Sci-Fi, Litfic, Memoir, Mystery, Horror, YA...
• ANNOTATION — Plot Twist, Highlight, Bookmark, Foreshadowing, Trope Unlocked...
• MOOD — Cozy, Spicy, Dark Academia, Mind Blown, Slow Burn...
• Plus chips (iPad session, GoodNotes log, e-reader night...) & mini book icons

► What you get
• 61 individual PNG stickers (transparent, 900×900 — crisp on retina iPad)
• Organized by module folders for easy import
• Master sheet (optional print on sticker paper)
• README with iPad / GoodNotes / Notability / Procreate how-to
• Instant download ZIP — no physical item ships

► How to use on iPad
1. Download & unzip in the Files app
2. GoodNotes: Insert image → pin as Element for reuse
3. Notability: Add photo → resize & duplicate
4. Procreate: Import PNG as a stamp layer
5. Stack STATUS + GENRE + RATING on each book entry

Also works in Canva, Freeform, and other digital planners. Optional print sheet \
if you ever want paper stickers.

Editorial navy / cream / gold — calm and intentional, not clutter.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "sage_neutral_print_set": """\
Instant download — Sage Green Neutral Abstract print set (6 posters).

Six quiet-luxury abstract compositions in sage, cream, stone, and soft clay — \
calm gallery wall art for modern, Japandi, and neutral interiors. Clean forms, \
generous space, museum-soft palette (not busy pattern clutter).

1. Balance Forms — monumental soft disc + spine + horizon bar
2. Stacked Horizon — layered bands with floating ring
3. Arch Still — architectural arch and clay block
4. Rings Field — concentric meditative rings
5. Grid Calm — modular study board (form · space · calm)
6. Path Stone — zen stepping path through sage field

► What you get
• 6 original abstract posters (high-quality JPG)
• Sizes @ 300 dpi: 24×36, 18×24, 16×20, 12×18, A4
• Scale 24×36 down for other frames
• Instant download ZIP — folders per design + README
• No physical item ships

► Perfect for
Living rooms, bedrooms, entryways, offices, and soft modern interiors. \
Matte or lightly textured paper looks best.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "morris_botanical_print_set": """\
Instant download — William Morris–inspired botanical print set (6 posters).

Six original Arts & Crafts botanical compositions in the spirit of William Morris — \
willow boughs, strawberry garden, trellis rose, pimpernel field, honeysuckle, and \
acanthus scroll. Rich indigo, cream, sage, and rose tones for a timeless gallery wall.

Original drawings (not wallpaper scans). Built for LARGE posters: true 300 dpi \
masters up to 24×36 in and ISO A1.

1. Willow Boughs — interlaced green leaves on cream
2. Strawberry Garden — indigo field with thrushes and berries
3. Trellis Rose — diamond lattice with climbing roses
4. Pimpernel Field — dense all-over floral
5. Honeysuckle — trailing vines and ochre blooms
6. Acanthus Scroll — formal indigo & cream medallion

► What you get
• 6 original botanical posters (high-quality JPG)
• Large poster sizes @ 300 dpi: 24×36, 18×24, 16×20
• Home sizes @ 300 dpi: 12×18, A4 (scale 24×36 down for any other frame)
• Instant download — 5 ZIPs (one pack family per design group)
• Dense Arts & Crafts pattern work — original code-drawn compositions
• No physical item ships

► Perfect for
Living rooms, bedrooms, reading nooks, cottage & traditional interiors, and gifts. \
Use a print shop for 24×36 / A1; matte or lightly textured paper looks best.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "bauhaus_print_set": """\
Instant download — Bauhaus geometric wall-art print set (6 posters).

Six gallery-grade compositions inspired by Bauhaus form, color, and balance — \
navy, cream, and gold with classic Bauhaus red and blue. Clean geometry, \
intentional asymmetry, and museum-wall presence (not cluttered clip-art).

Built for LARGE posters: true 300 dpi masters up to 24×36 in and ISO A1.

1. Circles & Bars — monumental red disc, navy spine, blue mass
2. Triangles — dark-field tension with cream mountain and blue core
3. Grid Modules — 3×4 modular study board (form · color · balance)
4. Arcs — architectural pies and counterweights
5. Form & Type — manifesto typography + geometry
6. Balance — asymmetric column vs stacked primary forms

► What you get
• 6 original geometric posters (high-quality JPG)
• Large poster sizes @ 300 dpi: 24×36, 18×24, 24×30, 20×28, A1, A2
• Standard / home sizes @ 300 dpi: 12×18, 12×16, 16×20, 10×14, A3, A4
• 12 sizes per design — scale large files down for smaller frames
• Instant download ZIP(s) — folders per design + README
• No physical item ships

► Perfect for
Living rooms, home offices, studios, galleries-at-home, modern interiors, \
and design-lover gifts. Use a print shop for 24×36 / A1; matte paper looks best.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "emergency_binder": """\
Instant download — Family Emergency Binder (printable PDF organizer).

When something goes wrong, you should not be hunting for phone numbers, \
insurance cards, or school pickup rules. This calm, editorial binder helps \
your household put the essentials in one place — and keep them updated.

► 13+ sections (US Letter)
• Quick start & first-10-minutes checklist
• Emergency contacts · household members
• Medical · insurance · important documents checklist
• Home & utilities · finances snapshot · pets
• Digital access notes (privacy-aware — no master passwords)
• Evacuation / go-bag · meeting place & school plans
• Quarterly update checklist · spine labels

► Designed for real use
Navy · gold · cream MathRelaxing layout. Fill-in fields and checklists. \
Print, put in a 1–2\" binder with tabs and sheet protectors, tell trusted people where it lives.

► Not included (on purpose)
This is an organizational tool — not medical, legal, or financial advice. \
End-of-life / funeral planning is a different product category; this pack focuses \
on household readiness and document location.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "lor_template_pack": """\
Instant download — Letter of Recommendation Template Pack (6 situations).

Write a strong recommendation in minutes — without starting from a blank page. \
Six editorial Word templates with filled samples and a practical writing guide.

► 6 letter types (blank + SAMPLE each)
• Job / Employee (manager voice)
• Academic / Graduate school
• Teacher → Student
• Character / Personal reference
• Scholarship
• Coworker / Peer

► What winners on Etsy include — we go further
Competitors often sell one plain Word file for $2–5. This pack gives you six \
situations, polished samples with specific praise and metrics, navy/gold \
editorial letterhead, and a how-to PDF (structure, tone, what to avoid).

► Formats
Microsoft Word (.docx) · US Letter · Instant download

Not legal advice. For court or immigration letters, consult appropriate counsel.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "atelier_resume_kit": """\
Instant download — Atelier Resume Kit (premium editorial system).

A complete application toolkit — not a single template. Five distinct layouts, \
five Atelier background styles, and a full set of matching career documents.

► 5 resume layouts
• Atelier — letterspaced name, double gold rules, magazine air
• Gallery — left-aligned modern with gold top bar
• Manuscript — literary centered classic
• Architect — geometric asymmetric presence
• ATS — portal-safe Calibri single column

► 5 Atelier background styles (already in Word)
Cream Veil · Scientific Grid · Gold Geometry · Phi Whisper · Navy Edge
(semi-transparent plates + free PNG pack to restyle)

► Full application set
• Cover letter · References · Thank-you note
• LinkedIn pack (headline + About)
• Portfolio one-pager
• How-to PDF + filled sample PDF (Celine Mora persona)
• Blank + filled SAMPLE for every major document

Built for product, research, strategy, and STEM professionals who want quiet \
luxury on the page — without Canva florals.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "geometric_wedding_suite": """\
Instant download — Geometric Wedding Seating Suite (printables).

A modern editorial wedding set in navy, gold & cream — designed with calm \
geometry (golden-ratio corner marks, circle table badges) instead of generic florals.

► What you get
• Seating chart (blank + sample) — landscape US Letter, 6 tables
• Table numbers 1–12 (print & cut cards)
• Place cards (blank + sample names)
• Day-of timeline card
• Menu card
• Guest list CSV (plan tables in Sheets/Excel)
• How-to PDF

► Perfect for
Modern, minimal, architectural, museum, conservatory, or STEM-couple weddings \
that want structure and elegance without clip-art roses.

► How it works
Assign guests in the CSV → edit blank PDFs in Acrobat/Preview/Canva → print on \
cardstock or poster paper.

© MathRelaxing. For personal use only. Not for redistribution or resale.
""",

    "editorial_resume_kit": """\
Instant download — Editorial Resume Kit (ATS + 5 elegant background styles).

Built for engineers, scientists, analysts, and precision professionals — \
navy, gold & cream MathRelaxing elegance, not floral Canva clutter.

► ATS Clean
Single-column, pure white, portal-safe (Word / Google Docs / Pages).

► Editorial suite — 5 semi-transparent backgrounds
Already embedded behind the text (swap anytime from the backgrounds folder):
• Cream Veil · Scientific Grid · Gold Geometry · Phi Whisper · Navy Edge

► Full kit
• ATS + Editorial resumes (blank + filled STEM sample)
• Cover letter + references
• Sample PDF + how-to guide
• PNG background pack to restyle in Word

► Formats
Editable .docx. Open in Word, Google Docs, or Pages. \
For company portals use ATS; for email/networking use Editorial.

Instant download ZIP. Personal use only.
© MathRelaxing.
""",
}

# ── Catálogo de productos ─────────────────────────────────────────────────────
PRODUCTS = {

    "fractal_flora_pdf": {
        "title":       "Fractal Flora — Printable Coloring Book PDF | 50 Fractal & Botanical Line Art Designs",
        "description": DESCRIPTIONS["fractal_flora_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "video": p("fractal_flora_promo_etsy.mp4"),
        "images": [
            p("fractal_flora_cover.jpg"),
            p("fractal_flora_page_01.jpg"),
            p("fractal_flora_page_02.jpg"),
            p("fractal_flora_page_03.jpg"),
            p("fractal_flora_page_04.jpg"),
            p("fractal_flora_page_05.jpg"),
            p("fractal_flora_sample_colored.jpg"),
            p("fractal_flora_sample_detail.jpg"),
            p("fractal_flora_sample_spread.jpg"),
        ],
        "files": [
            p("fractal_flora_digital.pdf"),
        ],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar.",
    },

    "sacred_geometry_pdf": {
        "title":       "Sacred Geometry — Color by Number Coloring Book PDF | 50 Low-Poly Mandala Designs",
        "description": DESCRIPTIONS["sacred_geometry_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "video": p("sacred_geometry_promo_etsy.mp4"),
        "images": [
            p("sacred_geometry_cover.jpg"),
            p("sacred_geometry_page_01.jpg"),
            p("sacred_geometry_page_02.jpg"),
            p("sacred_geometry_page_03.jpg"),
            p("sacred_geometry_page_04.jpg"),
            p("sacred_geometry_page_05.jpg"),
            p("_sg_contact_sheet.jpg"),
        ],
        "files": [
            p("sacred_geometry_digital.pdf"),
        ],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar.",
    },

    "hyperbolic_gardens_pdf": {
        "title":       "Hyperbolic Gardens — Printable Coloring Book PDF | 50 Escher-Style Tiling Designs",
        "description": DESCRIPTIONS["hyperbolic_gardens_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar cover.jpg + page samples con make_samples.py
        "files": [
            p("hyperbolic_gardens_digital.pdf"),
        ],
        "notes": "PENDIENTE: faltan imágenes de preview. Ejecutar make_samples.py para HG.",
    },

    "mathematical_tangle_art_pdf": {
        "title":       "Mathematical Tangle Art — Printable Coloring Book PDF | 50 Zentangle Math Designs",
        "description": DESCRIPTIONS["mathematical_tangle_art_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar previews
        "files": [
            p("mathematical_tangle_art_digital.pdf"),
        ],
        "notes": "PENDIENTE: faltan imágenes de preview.",
    },

    "sacred_harmonics_pdf": {
        "title":       "Sacred Harmonics — Printable Coloring Book PDF | 50 Cymatics & Wave Geometry Designs",
        "description": DESCRIPTIONS["sacred_harmonics_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar previews
        "files": [
            p("sacred_harmonics_digital.pdf"),
        ],
        "notes": "PENDIENTE: faltan imágenes de preview.",
    },

    "neural_network_pdf": {
        "title":       "Neural Network & Tech Art — Printable Coloring Book PDF | 50 Cybernetic Circuit and AI Graph Designs",
        "description": DESCRIPTIONS["neural_network_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [
            p("neural_network_cover.jpg"),
            p("neural_network_page_01.jpg"),
            p("neural_network_page_02.jpg"),
            p("neural_network_page_03.jpg"),
            p("neural_network_page_04.jpg"),
            p("neural_network_page_05.jpg"),
            p("neural_network_page_06.jpg"),
            p("neural_network_page_07.jpg"),
        ],
        "files": [
            p("neural_network_digital.pdf"),
        ],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar.",
    },

    "fractal_flora_ipad": {
        "title":       "Fractal Flora iPad Edition — Digital Coloring Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["fractal_flora_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": ff("FractalFlora_iPad_promo.mp4"),
        "images": [
            ff("previews", "ipad_preview_1_hero.jpg"),
            ff("previews", "ipad_preview_2_included.jpg"),
            ff("previews", "ipad_preview_3_twoways.jpg"),
        ],
        "files": [
            ff("FractalFlora_iPad_GoodNotes.pdf"),    # 1 — PDF hipervinculado
            ff("FractalFlora_Procreate_PNG_part1.zip"),  # 2 — PNGs parte 1
            ff("FractalFlora_Procreate_PNG_part2.zip"),  # 3 — PNGs parte 2
            ff("FractalFlora.swatches"),              # 4 — paleta Procreate
            ff("How_to_use_on_iPad.pdf"),             # 5 — guía
        ],
        "notes": "5 archivos exactos = límite Etsy. Listo para publicar.",
    },

    "sacred_geometry_ipad": {
        "title":       "Sacred Geometry iPad Edition — Color by Number Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["sacred_geometry_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": sg("SacredGeometry_iPad_promo.mp4"),
        "images": [
            sg("previews", "ipad_preview_1_hero.jpg"),
            sg("previews", "ipad_preview_2_included.jpg"),
            sg("previews", "ipad_preview_3_twoways.jpg"),
        ],
        "files": [
            sg("SacredGeometry_iPad_GoodNotes.pdf"),
            sg("SacredGeometry_Procreate_PNG_part1.zip"),
            sg("SacredGeometry_Procreate_PNG_part2.zip"),
            sg("SacredGeometry.swatches"),
            sg("How_to_use_on_iPad.pdf"),
        ],
        "notes": "5 archivos exactos = límite Etsy. Listo para publicar.",
    },

    "thomas_attractor": {
        "title":       "Thomas Attractor — Seamless Loop Animation | 1080x1080 60fps Mathematical Art",
        "description": DESCRIPTIONS["thomas_attractor"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "video": p("thomas", "Thomas_preview.mp4"),   # preview 540p con marca de agua
        "images": [
            p("thomas_preview_1_hero.jpg"),
            p("thomas_preview_2_titled.jpg"),
            p("thomas_preview_3_loop.jpg"),
        ],
        "files": [
            p("thomas_attractor_loop.mp4"),
        ],
        "notes": "Ya PUBLICADO (id=4528956373, activo). Video preview marcado añadido 2026-06-29. Archivo=mp4 limpio.",
    },

    "voronoi_gardens_pdf": {
        "title":       "Voronoi Gardens — Printable Coloring Book PDF | 50 Mandala & Cell Tessellation Designs",
        "description": DESCRIPTIONS["voronoi_gardens_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [
            p("voronoi_cover.jpg"),
            p("voronoi_page_01.jpg"),
            p("voronoi_page_02.jpg"),
            p("voronoi_page_03.jpg"),
            p("voronoi_page_04.jpg"),
            p("voronoi_page_05.jpg"),
        ],
        "files": [
            p("voronoi_gardens_digital.pdf"),
        ],
        "tags": ["voronoi coloring","voronoi mandala","math coloring book","geometric coloring",
                 "mandala coloring","printable coloring","adult coloring book","cell tessellation",
                 "sacred geometry","mindful coloring","coloring book pdf","relaxing coloring","voronoi art"],
        "notes": "Nicho de baja competencia (research: 1 listing 'voronoi coloring book'). Verificar taxonomy_id.",
    },

    "voronoi_gardens_ipad": {
        "title":       "Voronoi Gardens iPad Edition — Interactive Digital Coloring Bundle | Safari SVG",
        "description": DESCRIPTIONS["voronoi_gardens_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": p("ipad_voronoi_cbn_svg", "VoronoiGardens_SVG_promo.mp4"),
        "images": [
            p("ipad_voronoi_cbn_svg", "previews", "ipad_svg_preview_1_hero.jpg"),
            p("ipad_voronoi_cbn_svg", "previews", "ipad_svg_preview_2_features.jpg"),
            p("ipad_voronoi_cbn_svg", "previews", "ipad_svg_preview_3_included.jpg"),
        ],
        "files": [
            p("ipad_voronoi_cbn_svg", "VoronoiGardens_CBN_Interactive.zip"),
            p("ipad_voronoi_cbn_svg", "How_to_Use_Interactive_CBN.pdf"),
        ],
        "tags": ["ipad coloring book","color by number","voronoi diagram","math art","nature coloring","digital download","procreate swatches","goodnotes planner","interactive coloring","cellular automata","relaxing coloring"],
        "notes": "Migrated to Interactive SVG framework via build_voronoi_ipad_svg.py",
    },

    "stem_focus_planner": {
        "title":       "STEM Focus Planner Undated Digital | GoodNotes Notability iPad | Research Cornell Habit Tracker | Math Stickers",
        "description": DESCRIPTIONS["stem_focus_planner"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("stem_planner", "previews", "stem_planner_preview_1_hero.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_2_sections.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_3_stem.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_4_nav.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_5_stickers.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_6_formula.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_7_academic.jpg"),
            p("stem_planner", "previews", "stem_planner_preview_8_compat.jpg"),
        ],
        "files": [
            p("stem_planner", "STEM_Focus_Planner_v3.pdf"),
            p("stem_planner", "math_stickers.zip"),
        ],
        "video": p("stem_planner", "STEM_Planner_Promo.mp4"),
        "tags": ["stem planner","undated planner","goodnotes planner","digital planner",
                 "research planner","cornell notes","habit tracker","math planner",
                 "science planner","ipad planner","notability planner","student planner",
                 "math stickers"],
        "notes": "35 páginas hipervinculadas + 14 stickers matemáticos en ZIP. Precio $5.99 (ajustado para ser competitivo).",
    },

    "stem_notebook": {
        "title":       "STEM Digital Notebook for GoodNotes Notability | Hexagonal Isometric Dot Graph Cornell | 142 Pages iPad",
        "description": DESCRIPTIONS["stem_notebook"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["planner_template"],   # 12476 Planner Templates (categoría correcta para notebook digital)
        "video": p("stem_notebook", "STEM_Notebook_promo.mp4"),
        "images": [
            p("stem_notebook", "previews", "stem_preview_1_hero.jpg"),
            p("stem_notebook", "previews", "stem_preview_2_grids.jpg"),
            p("stem_notebook", "previews", "stem_preview_3_tabs.jpg"),
            p("stem_notebook", "previews", "stem_preview_4_included.jpg"),
        ],
        "files": [
            p("stem_notebook", "STEM_Notebook.pdf"),
        ],
        "tags": ["stem notebook","digital notebook","goodnotes notebook","hexagonal notebook",
                 "isometric notebook","chemistry notebook","engineering notebook","math notebook",
                 "dot grid notebook","cornell notes","science notebook","notability notebook","ipad notebook"],
        "notes": "Nicho STEM muy baja competencia (research: isometric=16, hex=49, eng=45). 142 págs hipervinculadas.",
    },

    "julia_morph_01": {
        "title":       "Julia Set Animation Seamless Loop | Fractal Wallpaper | Mathematical Art | 1080x1080 60fps MP4",
        "description": DESCRIPTIONS["julia_morph_01"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["digital_art"],   # 2078 Digital Prints (igual que atractores)
        # OJO animaciones: el video del listing = preview 540p CON marca de agua
        # (el producto ES un video → si fuera el limpio, se podría robar desde el preview).
        # El archivo de descarga ('files') sí es el MP4 limpio 1080p.
        "video": p("julia", "JuliaMorph_01_preview.mp4"),
        "images": [
            p("julia", "previews", "julia_preview_1_hero.jpg"),
            p("julia", "previews", "julia_preview_2_specs.jpg"),
            p("julia", "previews", "julia_preview_3_loop.jpg"),
        ],
        "files": [
            p("julia", "JuliaMorph_01.mp4"),
        ],
        "tags": ["julia set animation","fractal animation","fractal wallpaper","fractal loop",
                 "seamless loop","mathematical art","julia set art","fractal screensaver",
                 "digital wallpaper","generative art","abstract animation","math art","fractal video"],
        "notes": "Nicho 'julia set animation'=0 listings (demanda: fractal wallpaper=214). Loop seamless cardioide. Primero de serie.",
    },

    "islamic_geometry_pdf": {
        "title":       "Islamic Star Geometry — Color by Number Coloring Book PDF | 50 Geometric Star Rosette Designs",
        "description": DESCRIPTIONS["islamic_geometry_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [
            p("islamic_geometry_cover.jpg"),
            p("islamic_geometry_page_01.jpg"),
            p("islamic_geometry_page_02.jpg"),
            p("islamic_geometry_page_03.jpg"),
            p("islamic_geometry_page_04.jpg"),
            p("islamic_geometry_page_05.jpg"),
            p("islamic_geometry_page_06.jpg"),
            p("islamic_geometry_page_07.jpg"),
        ],
        "files": [
            p("islamic_geometry_digital.pdf"),
        ],
        "tags": ["islamic geometry","color by number","geometric coloring","islamic pattern",
                 "low poly coloring","adult coloring book","printable coloring","coloring book pdf",
                 "mandala coloring","mindful coloring","geometric art","star rosette art",
                 "math color number"],
        "notes": "Comparable a sacred_geometry_pdf (mismo formato color-by-number, 8 tonos) pero con "
                  "tema distinto: rosetones de simetria radial n-fold (girih) en vez de mallas 3D. "
                  "Nicho 'islamic pattern color by number'=0 listings activos (research 2026-07-02). "
                  "Generado con generate_islamic_geometry.py. Subido como DRAFT (id=4531791578, 2026-07-02). "
                  "Activacion manual pendiente desde el panel de Etsy.",
    },

    "islamic_geometry_ipad": {
        "title":       "Islamic Star Geometry iPad Edition — Color by Number Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["islamic_geometry_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "images": [
            p("ipad_islamic", "previews", "ipad_preview_1_hero.jpg"),
            p("ipad_islamic", "previews", "ipad_preview_2_included.jpg"),
            p("ipad_islamic", "previews", "ipad_preview_3_twoways.jpg"),
        ],
        "files": [
            p("ipad_islamic", "IslamicGeometry_iPad_GoodNotes.pdf"),
            p("ipad_islamic", "IslamicGeometry_Procreate_PNG_part1.zip"),
            p("ipad_islamic", "IslamicGeometry_Procreate_PNG_part2.zip"),
            p("ipad_islamic", "IslamicGeometry.swatches"),
            p("ipad_islamic", "How_to_use_on_iPad.pdf"),
        ],
        "tags": ["color by number ipad","procreate coloring","goodnotes coloring","ipad coloring page",
                 "digital coloring","color by number","procreate template","islamic geometry",
                 "geometric coloring","math color number","coloring page ipad","procreate palette",
                 "instant download"],
        "notes": "5 archivos exactos = limite Etsy. Bundle iPad companion de islamic_geometry_pdf. "
                  "Generado con build_islamic_ipad.py. Subido como DRAFT (id=4531778205, 2026-07-02). "
                  "Activacion manual pendiente desde el panel de Etsy.",
    },

    "celtic_knot_pdf": {
        "title":       "Celtic Knot Mathematics — Printable Coloring Book PDF | 50 Interlace & Knotwork Designs",
        "description": DESCRIPTIONS["celtic_knot_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [
            p("celtic_knot_cover.jpg"),
            p("celtic_knot_page_01.jpg"),
            p("celtic_knot_page_02.jpg"),
            p("celtic_knot_page_03.jpg"),
            p("celtic_knot_page_04.jpg"),
            p("celtic_knot_page_05.jpg"),
            p("celtic_knot_page_06.jpg"),
            p("celtic_knot_page_07.jpg"),
        ],
        "files": [
            p("celtic_knot_digital.pdf"),
        ],
        "tags": ["celtic knot","celtic coloring","knotwork coloring","irish coloring book",
                 "celtic mandala","adult coloring book","printable coloring","coloring book pdf",
                 "triskelion art","celtic pattern","mindful coloring","geometric coloring","meditative coloring"],
        "notes": "Generado con generate_celtic_knots.py (algoritmo de grid propio). Listo para publicar como borrador.",
    },

    "celtic_knot_ipad": {
        "title":       "Celtic Knot iPad Edition — Digital Coloring Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["celtic_knot_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": p("ipad_celtic", "CelticKnot_iPad_promo.mp4"),
        "images": [
            p("ipad_celtic", "previews", "ipad_preview_1_hero.jpg"),
            p("ipad_celtic", "previews", "ipad_preview_2_included.jpg"),
            p("ipad_celtic", "previews", "ipad_preview_3_twoways.jpg"),
        ],
        "files": [
            p("ipad_celtic", "CelticKnot_iPad_GoodNotes.pdf"),
            p("ipad_celtic", "CelticKnot_Procreate_PNG_part1.zip"),
            p("ipad_celtic", "CelticKnot_Procreate_PNG_part2.zip"),
            p("ipad_celtic", "CelticKnot.swatches"),
            p("ipad_celtic", "How_to_use_on_iPad.pdf"),
        ],
        "tags": ["celtic knot","ipad coloring","goodnotes coloring","procreate coloring",
                 "digital coloring","ipad coloring book","celtic mandala","knotwork coloring",
                 "geometric coloring","notability","procreate template","coloring book ipad","celtic pattern"],
        "notes": "Generado con build_celtic_ipad.py. 5 archivos exactos = limite Etsy. Bundle iPad de los 50 nudos tejidos.",
    },

    "voronoi_cell_garden": {
        "title":       "Voronoi Cell Garden Seamless Loop | Organic Mosaic Animation | Math Art Digital Download | 30fps MP4 | Ambient Stained Glass Screensaver",
        "description": DESCRIPTIONS["voronoi_cell_garden"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["digital_art"],   # 2078 Digital Prints (misma categoria que las otras animaciones)
        # OJO animaciones: el video del listing = preview 540p CON marca de agua.
        # El archivo de descarga ('files') es el MP4 limpio 1080p.
        "video": p("voronoi_loop", "VoronoiCellGarden_preview.mp4"),
        "images": [
            p("voronoi_loop", "previews", "voronoi_preview_1_hero.jpg"),
            p("voronoi_loop", "previews", "voronoi_preview_2_titled.jpg"),
            p("voronoi_loop", "previews", "voronoi_preview_3_loop.jpg"),
        ],
        "files": [
            p("voronoi_loop", "VoronoiCellGarden_loop.mp4"),
        ],
        "tags": ["voronoi animation","seamless loop","cellular animation","mosaic wallpaper",
                 "generative art","organic loop","voronoi art","digital wallpaper",
                 "screensaver loop","math art video","stained glass art","ambient video",
                 "voronoi mandala"],
        "notes": "Subido como DRAFT (id=4531784730, 2026-07-02). Nicho 'voronoi animation'=0 listings activos. Loop de celdas Voronoi con orbita de fase entera (loop exacto). Cross-sell con linea Voronoi Gardens (PDF/iPad). Cuarto de la serie de animaciones seamless (Thomas/Julia/De Jong). Video preview subido 2026-07-02 (video_id=830793288). Activacion manual pendiente desde el panel de Etsy.",
    },

    "quantified_self_planner": {
        "title":       "The Quantified Self Journal — Digital Data Planner | GitHub Heatmap & Agile Sprint Trackers | GoodNotes Notability iPad Notebook",
        "description": DESCRIPTIONS["quantified_self_planner"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("quantified_self", "previews", "qs_preview_1_hero.jpg"),
            p("quantified_self", "previews", "qs_preview_2_analytics.jpg"),
            p("quantified_self", "previews", "qs_preview_3_sprints.jpg"),
            p("quantified_self", "previews", "_idx.png"),
            p("quantified_self", "previews", "_yer.png"),
            p("quantified_self", "previews", "_mon.png"),
            p("quantified_self", "previews", "_wek.png"),
        ],
        "files": [
            p("quantified_self", "Quantified_Self_Journal.pdf"),
        ],
        "tags": ["quantified self","data planner","agile sprint planner","programmer gift","software engineer gift","habit tracker","github heatmap","digital planner","goodnotes planner","ipad planner","dark mode planner","bullet journal","stem notebook"],
        "notes": "Generado con build_quantified_self.py",
    },

    "spiral_tilings_ipad": {
        "title":       "Interactive Color By Number Spiral Tilings — iPad Safari SVG App | 50 Math Mandala Radial Designs",
        "description": DESCRIPTIONS["spiral_tilings_ipad"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": p("ipad_spiral_cbn_svg", "SpiralTilings_SVG_promo.mp4"),
        "images": [
            p("ipad_spiral_cbn_svg", "previews", "ipad_svg_preview_1_hero.jpg"),
            p("ipad_spiral_cbn_svg", "previews", "ipad_svg_preview_2_features.jpg"),
            p("ipad_spiral_cbn_svg", "previews", "ipad_svg_preview_3_included.jpg"),
        ],
        "files": [
            p("ipad_spiral_cbn_svg", "SpiralTilings_CBN_Interactive.zip"),
            p("ipad_spiral_cbn_svg", "How_to_Use_Interactive_CBN.pdf"),
        ],
        "tags": ["ipad coloring book","color by number","goodnotes planner","procreate coloring","digital mandala","spiral art","math art","pastel aesthetic","adult coloring pdf","procreate swatches","digital download","relaxing coloring","adhd coloring"],
        "notes": "Generado con build_spiral_ipad.py",
    },

    "spiral_tilings_pdf": {
        "title":       "Spiral Tilings — Printable Coloring Book PDF | 50 Math & Mandala Radial Designs",
        "description": DESCRIPTIONS["spiral_tilings_pdf"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "video": p("spiral_video_out", "SpiralTilings_promo.mp4"),
        "images": [
            p("spiral_tilings_cover.jpg"),
            p("spiral_tilings_page_01.jpg"),
            p("spiral_tilings_page_02.jpg"),
            p("spiral_tilings_page_03.jpg"),
            p("spiral_tilings_page_04.jpg"),
            p("spiral_tilings_page_05.jpg"),
            p("spiral_tilings_page_06.jpg"),
            p("spiral_tilings_page_07.jpg"),
        ],
        "files": [
            p("spiral_tilings_digital.pdf"),
        ],
        "tags": ["spiral coloring","mandala coloring","math coloring book","geometric coloring",
                 "spiral mandala","printable coloring","adult coloring book","radial tessellation",
                 "sacred geometry","mindful coloring","coloring book pdf","relaxing coloring","logarithmic spiral"],
        "notes": "Generado con generate_spiral_tilings.py. Listo para publicar como borrador.",
    },

    "happy_chemicals_prints": {
        "title": (
            "Happy Chemicals Print Set | Serotonin Dopamine Oxytocin Caffeine "
            "Molecule Wall Art | Science Printable Digital Download"
        ),
        "description": DESCRIPTIONS["happy_chemicals_prints"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["digital_art"],  # 2078 Digital Prints
        "images": [
            p("happy_chemicals", "previews", "happy_chemicals_preview_1_hero.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_2_set.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_3_included.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_4_serotonin.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_5_dopamine.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_6_oxytocin.jpg"),
            p("happy_chemicals", "previews", "happy_chemicals_preview_7_caffeine.jpg"),
        ],
        "files": [
            # Combined pack kept under Etsy ~20MB digital limit (JPEG q=80)
            p("happy_chemicals", "Happy_Chemicals_Print_Set.zip"),
        ],
        "tags": [
            "molecule wall art",
            "serotonin print",
            "dopamine poster",
            "oxytocin art",
            "caffeine molecule",
            "science wall art",
            "therapy office art",
            "printable wall art",
            "chemistry poster",
            "mental health art",
            "happiness hormones",
            "digital download",
            "psychology gift",
        ],
        "notes": (
            "Validado eRank (Tier A). RDKit color + frames. "
            "Draft listing_id=4538046387. ZIP q=80 ~11MB under Etsy limit."
        ),
    },

    "cs_poster_set": {
        "title": (
            "Computer Science Poster Set | Big O Algorithm Binary Tree Logic Gates "
            "OSI STEM Wall Art Printable (Digital Download)"
        ),
        "description": DESCRIPTIONS["cs_poster_set"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("cs_poster_set", "previews", "cs_preview_1_hero.jpg"),
            p("cs_poster_set", "previews", "cs_preview_2_set.jpg"),
            p("cs_poster_set", "previews", "cs_preview_3_included.jpg"),
            p("cs_poster_set", "previews", "cs_preview_big_o.jpg"),
            p("cs_poster_set", "previews", "cs_preview_bst.jpg"),
            p("cs_poster_set", "previews", "cs_preview_sorting.jpg"),
            p("cs_poster_set", "previews", "cs_preview_logic.jpg"),
            p("cs_poster_set", "previews", "cs_preview_osi.jpg"),
            p("cs_poster_set", "previews", "cs_preview_stack_queue.jpg"),
            p("cs_poster_set", "previews", "cs_preview_fsm.jpg"),
        ],
        "files": [
            p("cs_poster_set", "Computer_Science_Poster_Set.zip"),
        ],
        "tags": [
            "computer science poster",
            "algorithm poster",
            "big o notation",
            "binary search tree",
            "logic gates poster",
            "osi model poster",
            "stem wall art",
            "coding classroom",
            "programming gift",
            "data structure art",
            "cs teacher gift",
            "digital download",
            "science wall art",
        ],
        "notes": (
            "eRank wave4: computer science poster ~127 searches, 870 comp, 68% CTR. "
            "7 plates: matplotlib+networkx + circuitikz gates + TikZ automata FSM. "
            "Draft listing_id=4538180109. Ads OFF until organic signal."
        ),
        "listing_id": 4538180109,
    },

    "stem_lab_notebook": {
        "title": (
            "Lab Notebook Printable | STEM Science Experiment Log PDF | "
            "GoodNotes Notability Digital Lab Journal (Digital Download)"
        ),

        "description": DESCRIPTIONS["stem_lab_notebook"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["planner_template"],  # 12476 Planner Templates
        "images": [
            p("lab_notebook", "previews", "lab_notebook_preview_1_hero.jpg"),
            p("lab_notebook", "previews", "lab_notebook_preview_2_pages.jpg"),
            p("lab_notebook", "previews", "lab_notebook_preview_3_included.jpg"),
            p("lab_notebook", "previews", "lab_notebook_preview_4_experiment.jpg"),
            p("lab_notebook", "previews", "lab_notebook_preview_5_graph.jpg"),
            p("lab_notebook", "previews", "lab_notebook_preview_6_chemistry.jpg"),
        ],
        "files": [
            p("lab_notebook", "STEM_Lab_Notebook.pdf"),
        ],
        "tags": [
            "lab notebook printable",
            "science notebook",
            "lab journal",
            "stem notebook",
            "experiment log",
            "goodnotes notebook",
            "scientific method",
            "digital lab notebook",
            "printable lab report",
            "chemistry notebook",
            "physics notebook",
            "student lab book",
            "notability notebook",
        ],
        "notes": (
            "eRank wave3 pick: lab notebook printable ~98 searches, 55 competition, "
            "99% CTR. 48-page PDF US Letter, hyperlinked. "
            "Draft listing_id=4538070573."
        ),
    },

    "schrodinger_equation_print": {
        "title": (
            "Physics Wall Art | Schrödinger Equation Print | Quantum Mechanics "
            "Particle in a Box STEM Art (Digital Download)"
        ),

        "description": DESCRIPTIONS["schrodinger_equation_print"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["digital_art"],  # 2078 Digital Prints
        "images": [
            p("schrodinger_equation", "previews", "schrodinger_preview_1_hero.jpg"),
            p("schrodinger_equation", "previews", "schrodinger_preview_2_detail.jpg"),
            p("schrodinger_equation", "previews", "schrodinger_preview_3_included.jpg"),
            p("schrodinger_equation", "previews", "schrodinger_preview_4_plate.jpg"),
            p("schrodinger_equation", "previews", "schrodinger_preview_5_equation.jpg"),
        ],
        "files": [
            p("schrodinger_equation", "Schrodinger_Equation_Physics_Wall_Art.zip"),
        ],
        "tags": [
            "physics wall art",
            "schrodinger equation",
            "quantum physics art",
            "science poster",
            "physics poster",
            "math wall art",
            "stem wall art",
            "educational poster",
            "digital download",
            "classroom decor",
            "nerd gift",
            "teacher gift",
            "quantum mechanics",
        ],
        "notes": (
            "eRank wave2 pick: ~9 listings, avg 144 favs, med $5.50, 78% digital. "
            "Competition <20 on long-tail; rides physics wall art cluster (Maxwell #1). "
            "Scientific plate style matching Maxwell/Black Hole. "
            "Draft listing_id=4538061513."
        ),
    },

    "unit_circle_print": {
        "title": (
            "Unit Circle Poster | Trigonometry Reference Wall Art | "
            "Degrees Radians Cos Sin STEM Print (Digital Download)"
        ),
        "description": DESCRIPTIONS["unit_circle_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("unit_circle", "previews", "unit_circle_preview_1_hero.jpg"),
            p("unit_circle", "previews", "unit_circle_preview_2_detail.jpg"),
            p("unit_circle", "previews", "unit_circle_preview_3_included.jpg"),
            p("unit_circle", "previews", "unit_circle_preview_4_plate.jpg"),
            p("unit_circle", "previews", "unit_circle_preview_5_equation.jpg"),
        ],
        "files": [
            p("unit_circle", "Unit_Circle_Trigonometry_Wall_Art.zip"),
        ],
        "tags": [
            "unit circle",
            "unit circle poster",
            "trigonometry poster",
            "math wall art",
            "trig reference",
            "precalculus poster",
            "stem wall art",
            "math classroom",
            "degrees radians",
            "digital download",
            "teacher gift",
            "science wall art",
            "educational poster",
        ],
        "notes": (
            "eRank wave5: unit circle 108 searches, 457 competition, KD 31, CTR 146%. "
            "Scientific plate (LaTeX). Draft listing_id=4538562680. Ads OFF until organic signal."
        ),
        "listing_id": 4538562680,
    },

    "editorial_resume_kit": {
        "title": (
            "ATS Resume Template | Editorial Professional CV Word Google Docs | "
            "Cover Letter & References STEM Modern (Digital Download)"
        ),
        "description": DESCRIPTIONS["editorial_resume_kit"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("resume_kit", "previews", "resume_preview_1_hero.jpg"),
            p("resume_kit", "previews", "resume_preview_2_styles.jpg"),
            p("resume_kit", "previews", "resume_preview_3_included.jpg"),
            p("resume_kit", "previews", "resume_preview_4_detail.jpg"),
            p("resume_kit", "previews", "resume_preview_5_features.jpg"),
            p("resume_kit", "previews", "resume_preview_6_backgrounds.jpg"),
        ],
        "files": [
            p("resume_kit", "MathRelaxing_Editorial_Resume_Kit.zip"),
        ],
        "video": p("resume_kit", "Editorial_Resume_Kit_promo.mp4"),
        "tags": [
            "resume template",
            "ats resume template",
            "modern resume",
            "cv template",
            "cover letter",
            "google docs resume",
            "word resume",
            "professional resume",
            "minimalist resume",
            "tech resume",
            "digital download",
            "job application",
            "career template",
        ],
        "notes": (
            "eRank wave7: resume template 6,264 searches, 32.8k comp, KD 36, CTR 104%. "
            "ATS + 5 Editorial background styles (semi-transparent watermarks). "
            "Promo video: Word demo cursor/type. Draft listing_id=4538574036. "
            "Ads OFF until organic signal."
        ),
        "listing_id": 4538574036,
    },

    "atelier_resume_kit": {
        "title": (
            "Luxury Resume Template Kit | 5 Editorial Layouts + ATS | "
            "Cover Letter LinkedIn Thank You Portfolio (Digital Download)"
        ),
        "description": DESCRIPTIONS["atelier_resume_kit"],
        "price": 4.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("resume_luxe_kit", "previews", "luxe_preview_01_hero.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_02_layouts.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_03_styles.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_04_application.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_05_skills.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_06_blank_sample.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_07_more_layouts.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_08_inventory.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_09_usecases.jpg"),
            p("resume_luxe_kit", "previews", "luxe_preview_10_value.jpg"),
        ],
        "files": [
            p("resume_luxe_kit", "MathRelaxing_Atelier_Resume_Kit.zip"),
        ],
        "tags": [
            "luxury resume",
            "editorial resume",
            "ats resume template",
            "modern cv template",
            "professional resume",
            "cover letter",
            "word resume",
            "minimalist resume",
            "executive resume",
            "linkedin template",
            "digital download",
            "job application",
            "resume kit",
        ],
        "notes": (
            "Expanded premium kit: 5 layouts + 5 bg styles + cover/refs/thankyou/"
            "linkedin/portfolio. 10 listing previews. Persona Celine Mora. $12.99. "
            "generate_resume_luxe_kit.py + build_atelier_previews.py. "
            "Draft listing_id=4538604802. Ads OFF."
        ),
        "listing_id": 4538604802,
    },

    "lor_template_pack": {
        "title": (
            "Letter of Recommendation Template Pack | Job Academic Teacher "
            "Character Scholarship Coworker | Editable Word (Digital Download)"
        ),
        "description": DESCRIPTIONS["lor_template_pack"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("lor_pack", "previews", "lor_preview_1_hero.jpg"),
            p("lor_pack", "previews", "lor_preview_2_types.jpg"),
            p("lor_pack", "previews", "lor_preview_3_why.jpg"),
            p("lor_pack", "previews", "lor_preview_4_detail.jpg"),
            p("lor_pack", "previews", "lor_preview_5_included.jpg"),
            p("lor_pack", "previews", "lor_preview_6_value.jpg"),
        ],
        "files": [
            p("lor_pack", "MathRelaxing_Letter_of_Recommendation_Pack.zip"),
        ],
        "tags": [
            "recommendation letter",
            "letter of recommend",
            "reference letter",
            "job reference letter",
            "teacher recommend",
            "academic letter",
            "character reference",
            "scholarship letter",
            "employee reference",
            "word template",
            "digital download",
            "editable template",
            "reference template",
        ],
        "notes": (
            "eRank NOW: letter of recommendation Jun 1160 · mom 1.15 · KD 1 · 605 comp. "
            "SERP: tops ~$2–7 single letters, few multi-packs, plain design. "
            "Our edge: 6 situations + samples + guide + editorial letterhead. "
            "generate_lor_pack.py. Draft listing_id=4539149064. Ads OFF."
        ),
        "listing_id": 4539149064,
    },

    "emergency_binder": {
        "title": (
            "Family Emergency Binder Printable | ICE Household Organizer PDF | "
            "Contacts Medical Insurance Documents Go-Bag (Digital Download)"
        ),
        "description": DESCRIPTIONS["emergency_binder"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("emergency_binder", "previews", "eb_preview_1_hero.jpg"),
            p("emergency_binder", "previews", "eb_preview_2_sections.jpg"),
            p("emergency_binder", "previews", "eb_preview_3_why.jpg"),
            p("emergency_binder", "previews", "eb_preview_4_detail.jpg"),
            p("emergency_binder", "previews", "eb_preview_5_how.jpg"),
            p("emergency_binder", "previews", "eb_preview_6_value.jpg"),
            p("emergency_binder", "previews", "eb_preview_7_spine.jpg"),
        ],
        "files": [
            p("emergency_binder", "MathRelaxing_Family_Emergency_Binder.zip"),
        ],
        "tags": [
            "emergency binder",
            "family emergency",
            "ice binder",
            "home binder",
            "document organizer",
            "emergency planner",
            "printable binder",
            "medical binder",
            "go bag checklist",
            "household binder",
            "digital download",
            "preparedness",
            "family organizer",
        ],
        "notes": (
            "eRank NOW: emergency binder mom 1.70 · KD 33 · ~3k comp. "
            "SERP mixes ICE binders ($8–18 digital) with end-of-life planners; "
            "we position household readiness (not funeral). "
            "generate_emergency_binder.py. Draft listing_id=4539135067. "
            "7 previews incl. spine cut labels. Ads OFF."
        ),
        "listing_id": 4539135067,
    },

    "reader_os_stickers": {
        "title": (
            "Reader OS iPad Stickers | GoodNotes Bookish Sticker System | "
            "Digital Reading Journal PNG Pack (Digital Download)"
        ),
        "description": DESCRIPTIONS["reader_os_stickers"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("reader_os", "previews", "reader_os_preview_1_hero.jpg"),
            p("reader_os", "previews", "reader_os_preview_2_ipad.jpg"),
            p("reader_os", "previews", "reader_os_preview_3_modules.jpg"),
            p("reader_os", "previews", "reader_os_preview_4_included.jpg"),
            p("reader_os", "previews", "reader_os_preview_5_howto.jpg"),
            p("reader_os", "previews", "reader_os_preview_6_sheet.jpg"),
        ],
        "files": [
            p("reader_os", "MathRelaxing_Reader_OS_Stickers.zip"),
        ],
        "tags": [
            "goodnotes stickers",
            "ipad stickers",
            "digital stickers",
            "bookish stickers",
            "reading journal",
            "kindle stickers",
            "tbr stickers",
            "book stickers",
            "notability sticker",
            "digital download",
            "reading tracker",
            "planner stickers",
            "book lover gift",
        ],
        "notes": (
            "Novel angle: functional Reader OS system for digital readers (iPad first). "
            "eRank: bookish stickers / kindle stickers / goodnotes stickers. "
            "generate_reader_os.py (Playwright HTML/CSS premium). "
            "Draft listing_id=4540003882. Ads OFF."
        ),
        "listing_id": 4540003882,
    },

    "sage_neutral_print_set": {
        "title": (
            "Sage Green Wall Art Print Set | Neutral Abstract Posters | "
            "Japandi Cream Gallery Bundle (Digital Download)"
        ),
        "description": DESCRIPTIONS["sage_neutral_print_set"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("sage_set", "previews", "sage_preview_1_hero.jpg"),
            p("sage_set", "previews", "sage_preview_2_set.jpg"),
            p("sage_set", "previews", "sage_preview_3_included.jpg"),
            p("sage_set", "previews", "sage_preview_4_balance_forms.jpg"),
            p("sage_set", "previews", "sage_preview_5_stacked_horizon.jpg"),
            p("sage_set", "previews", "sage_preview_6_arch_still.jpg"),
            p("sage_set", "previews", "sage_preview_7_rings_field.jpg"),
            p("sage_set", "previews", "sage_preview_8_grid_calm.jpg"),
            p("sage_set", "previews", "sage_preview_9_path_stone.jpg"),
            p("sage_set", "previews", "sage_preview_10_all.jpg"),
        ],
        "files": [
            # filled after generate — may be 1 combined or 2 packs
            p("sage_set", "MathRelaxing_Sage_Neutral_Print_Set.zip"),
        ],
        "tags": [
            "sage green wall art",
            "neutral wall art",
            "sage green print",
            "japandi wall art",
            "abstract wall art",
            "cream wall art",
            "minimalist print",
            "gallery wall set",
            "printable wall art",
            "modern wall art",
            "digital download",
            "quiet luxury",
            "abstract poster",
        ],
        "notes": (
            "eRank wave9 #3: sage green wall art Jun 2130 · mom 1.56 · KD 72. "
            "v2 LETHAL artistic compositions. generate_sage_set.py. "
            "Draft listing_id=4539181090. Ads OFF until organic signal."
        ),
        "listing_id": 4539181090,
    },

    "morris_botanical_print_set": {
        "title": (
            "William Morris Print Set | Botanical Wall Art Printable | "
            "Arts Crafts Floral Poster Bundle (Digital Download)"
        ),
        "description": DESCRIPTIONS["morris_botanical_print_set"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("morris_set", "previews", "morris_preview_1_hero.jpg"),
            p("morris_set", "previews", "morris_preview_2_set.jpg"),
            p("morris_set", "previews", "morris_preview_3_included.jpg"),
            p("morris_set", "previews", "morris_preview_4_willow_boughs.jpg"),
            p("morris_set", "previews", "morris_preview_5_strawberry_garden.jpg"),
            p("morris_set", "previews", "morris_preview_6_trellis_rose.jpg"),
            p("morris_set", "previews", "morris_preview_7_pimpernel_field.jpg"),
            p("morris_set", "previews", "morris_preview_8_honeysuckle.jpg"),
            p("morris_set", "previews", "morris_preview_9_acanthus_scroll.jpg"),
            p("morris_set", "previews", "morris_preview_10_all.jpg"),
        ],
        "files": [
            p("morris_set", "MathRelaxing_Morris_01_Willow.zip"),
            p("morris_set", "MathRelaxing_Morris_02_Strawberry.zip"),
            p("morris_set", "MathRelaxing_Morris_03_Trellis.zip"),
            p("morris_set", "MathRelaxing_Morris_04_05_Pimpernel_Honeysuckle.zip"),
            p("morris_set", "MathRelaxing_Morris_06_Acanthus.zip"),
        ],
        "tags": [
            "william morris print",
            "morris wall art",
            "botanical wall art",
            "arts crafts print",
            "floral wall art",
            "vintage floral print",
            "printable wall art",
            "strawberry thief",
            "willow bough print",
            "cottage decor",
            "digital download",
            "gallery wall set",
            "large wall art",
        ],
        "notes": (
            "eRank wave9 #2 after Bauhaus: william morris print "
            "Jun 1630 · mom 1.35 · KD 64. "
            "v2 LETHAL dense Arts & Crafts (code-drawn). "
            "generate_morris_set.py + _pack_morris_zips.py (5 packs <20MB). "
            "Draft listing_id=4539170520. Ads OFF until organic signal."
        ),
        "listing_id": 4539170520,
    },

    "bauhaus_print_set": {
        "title": (
            "Bauhaus Wall Art Print Set | 6 Geometric Modern Posters | "
            "Navy Cream Gold Printable Decor (Digital Download)"
        ),
        "description": DESCRIPTIONS["bauhaus_print_set"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["digital_art"],  # 2078 Digital Prints
        "video": p("bauhaus_set", "Bauhaus_Print_Set_promo.mp4"),
        "images": [
            p("bauhaus_set", "previews", "bauhaus_preview_1_hero.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_2_set.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_3_included.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_4_circles_bars.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_5_triangles.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_6_grid_modules.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_7_arcs.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_8_form_type.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_9_balance.jpg"),
            p("bauhaus_set", "previews", "bauhaus_preview_10_all.jpg"),
        ],
        "files": [
            p("bauhaus_set", "MathRelaxing_Bauhaus_Print_Set.zip"),
        ],
        "tags": [
            "bauhaus wall art",
            "bauhaus poster",
            "geometric wall art",
            "modern wall art",
            "mid century print",
            "abstract wall art",
            "printable wall art",
            "large wall art",
            "gallery wall set",
            "minimalist print",
            "digital download",
            "poster print set",
            "geometric poster",
        ],
        "notes": (
            "eRank art/décor lead: Bauhaus-style geometric set. "
            "6 compositions × large poster 300 dpi (up to 24×36 / A1) + standard sizes. "
            "generate_bauhaus_set.py + build_bauhaus_video.py. "
            "Draft listing_id=4539161960. Ads OFF until organic signal."
        ),
        "listing_id": 4539161960,
    },

    "geometric_wedding_suite": {
        "title": (
            "Wedding Seating Chart Template | Geometric Modern Printable Suite | "
            "Table Numbers Place Cards Timeline Menu (Digital Download)"
        ),
        "description": DESCRIPTIONS["geometric_wedding_suite"],
        "price": 4.99,
        "taxonomy_id": TAXONOMY["digital_art"],  # Digital Prints — verify party/wedding node later
        "images": [
            p("wedding_seating_suite", "previews", "wedding_preview_1_hero.jpg"),
            p("wedding_seating_suite", "previews", "wedding_preview_2_included.jpg"),
            p("wedding_seating_suite", "previews", "wedding_preview_3_detail.jpg"),
            p("wedding_seating_suite", "previews", "wedding_preview_4_edit.jpg"),
            p("wedding_seating_suite", "previews", "wedding_preview_5_features.jpg"),
        ],
        "files": [
            p("wedding_seating_suite", "MathRelaxing_Geometric_Wedding_Suite.zip"),
        ],
        "tags": [
            "wedding seating chart",
            "seating chart template",
            "wedding table numbers",
            "place cards wedding",
            "wedding printables",
            "modern wedding",
            "geometric wedding",
            "minimalist wedding",
            "wedding timeline",
            "reception seating",
            "digital download",
            "printable wedding",
            "table assignment",
        ],
        "notes": (
            "eRank wave7: wedding seating chart 4,197 searches, 28.1k comp, KD 41. "
            "MathRelaxing angle: geometric editorial navy/gold/cream (not florals). "
            "Generator: generate_wedding_seating_suite.py. Draft listing_id=4538602540. "
            "STAND-BY — not prioritizing; focus elsewhere. Ads OFF."
        ),
        "listing_id": 4538602540,
        "status": "standby",
    },

    # ── Equation scientific plates (scale Maxwell/Ulam cluster) ───────────────
    "fourier_series_print": {
        "title": (
            "Math Wall Art | Fourier Series Print | Square Wave Harmonics "
            "STEM Mathematics Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["fourier_series_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "fourier_series", "previews", "fourier_series_preview_1_hero.jpg"),
            p("equation_plates", "fourier_series", "previews", "fourier_series_preview_2_detail.jpg"),
            p("equation_plates", "fourier_series", "previews", "fourier_series_preview_3_included.jpg"),
            p("equation_plates", "fourier_series", "previews", "fourier_series_preview_4_plate.jpg"),
            p("equation_plates", "fourier_series", "previews", "fourier_series_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "fourier_series", "Fourier_Series_Math_Wall_Art.zip")],
        "tags": [
            "math wall art",
            "fourier series",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "calculus art",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "signal processing",
            "math print",
        ],
        "notes": "generate_equation_plates.py. Scale math wall art cluster. $2.99.",
        "listing_id": 4540082127,
    },
    "wave_equation_print": {
        "title": (
            "Physics Wall Art | Wave Equation Print | Standing Waves on a String "
            "STEM Science Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["wave_equation_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "wave_equation", "previews", "wave_equation_preview_1_hero.jpg"),
            p("equation_plates", "wave_equation", "previews", "wave_equation_preview_2_detail.jpg"),
            p("equation_plates", "wave_equation", "previews", "wave_equation_preview_3_included.jpg"),
            p("equation_plates", "wave_equation", "previews", "wave_equation_preview_4_plate.jpg"),
            p("equation_plates", "wave_equation", "previews", "wave_equation_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "wave_equation", "Wave_Equation_Physics_Wall_Art.zip")],
        "tags": [
            "physics wall art",
            "wave equation",
            "physics poster",
            "stem wall art",
            "science poster",
            "math wall art",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "standing waves",
            "science wall art",
        ],
        "notes": "generate_equation_plates.py. Scale physics wall art (Maxwell). $2.99.",
        "listing_id": 4540099296,
    },
    "dirac_equation_print": {
        "title": (
            "Physics Wall Art | Dirac Equation Print | Matter Antimatter "
            "Relativistic Quantum Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["dirac_equation_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "dirac_equation", "previews", "dirac_equation_preview_1_hero.jpg"),
            p("equation_plates", "dirac_equation", "previews", "dirac_equation_preview_2_detail.jpg"),
            p("equation_plates", "dirac_equation", "previews", "dirac_equation_preview_3_included.jpg"),
            p("equation_plates", "dirac_equation", "previews", "dirac_equation_preview_4_plate.jpg"),
            p("equation_plates", "dirac_equation", "previews", "dirac_equation_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "dirac_equation", "Dirac_Equation_Physics_Wall_Art.zip")],
        "tags": [
            "physics wall art",
            "dirac equation",
            "quantum physics art",
            "physics poster",
            "antimatter art",
            "stem wall art",
            "science poster",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "relativity art",
            "science wall art",
        ],
        "notes": "generate_equation_plates.py. Quantum/relativity cluster. $2.99.",
        "listing_id": 4540082241,
    },
    "navier_stokes_print": {
        "title": (
            "Physics Wall Art | Navier-Stokes Equations Print | Fluid Dynamics "
            "Streamlines STEM Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["navier_stokes_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "navier_stokes", "previews", "navier_stokes_preview_1_hero.jpg"),
            p("equation_plates", "navier_stokes", "previews", "navier_stokes_preview_2_detail.jpg"),
            p("equation_plates", "navier_stokes", "previews", "navier_stokes_preview_3_included.jpg"),
            p("equation_plates", "navier_stokes", "previews", "navier_stokes_preview_4_plate.jpg"),
            p("equation_plates", "navier_stokes", "previews", "navier_stokes_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "navier_stokes", "Navier_Stokes_Physics_Wall_Art.zip")],
        "tags": [
            "physics wall art",
            "navier stokes",
            "fluid dynamics art",
            "physics poster",
            "stem wall art",
            "science poster",
            "math wall art",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "engineering art",
            "science wall art",
        ],
        "notes": "generate_equation_plates.py. Engineering/fluids angle. $2.99.",
        "listing_id": 4540082293,
    },
    "euler_identity_print": {
        "title": (
            "Math Wall Art | Euler Identity Print | Complex Plane Beautiful Equation "
            "STEM Mathematics Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["euler_identity_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "euler_identity", "previews", "euler_identity_preview_1_hero.jpg"),
            p("equation_plates", "euler_identity", "previews", "euler_identity_preview_2_detail.jpg"),
            p("equation_plates", "euler_identity", "previews", "euler_identity_preview_3_included.jpg"),
            p("equation_plates", "euler_identity", "previews", "euler_identity_preview_4_plate.jpg"),
            p("equation_plates", "euler_identity", "previews", "euler_identity_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "euler_identity", "Euler_Identity_Math_Wall_Art.zip")],
        "tags": [
            "math wall art",
            "eulers identity",
            "euler formula",
            "mathematics poster",
            "complex numbers",
            "stem wall art",
            "science poster",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "classroom decor",
        ],
        "notes": "generate_equation_plates.py. Classic math identity. $2.99.",
        "listing_id": 4540099676,
    },
    "mandelbrot_set_print": {
        "title": (
            "Math Wall Art | Mandelbrot Set Print | Fractal Chaos Theory "
            "Complex Dynamics STEM Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["mandelbrot_set_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "mandelbrot_set", "previews", "mandelbrot_set_preview_1_hero.jpg"),
            p("equation_plates", "mandelbrot_set", "previews", "mandelbrot_set_preview_2_detail.jpg"),
            p("equation_plates", "mandelbrot_set", "previews", "mandelbrot_set_preview_3_included.jpg"),
            p("equation_plates", "mandelbrot_set", "previews", "mandelbrot_set_preview_4_plate.jpg"),
            p("equation_plates", "mandelbrot_set", "previews", "mandelbrot_set_preview_5_equation.jpg"),
        ],
        "files": [p("equation_plates", "mandelbrot_set", "Mandelbrot_Set_Math_Wall_Art.zip")],
        "tags": [
            "math wall art",
            "mandelbrot set",
            "fractal art",
            "mathematics poster",
            "chaos theory",
            "stem wall art",
            "generative art",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "complex dynamics",
            "math print",
        ],
        "notes": "generate_equation_plates.py. Chaos/fractal scientific plate. $2.99.",
        "listing_id": 4540082547,
    },
    "famous_equations_set": {
        "title": (
            "Famous Equations Wall Art Set of 6 | Math Physics Scientific Plates | "
            "Fourier Dirac Euler STEM Gallery (Digital Download)"
        ),
        "description": DESCRIPTIONS["famous_equations_set"],
        "price": 3.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_1_hero.jpg"),
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_2_included.jpg"),
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_3_eq.jpg"),
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_4_eq.jpg"),
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_5_eq.jpg"),
            p("equation_plates", "famous_equations_set", "previews", "famous_equations_preview_6_eq.jpg"),
        ],
        "files": [
            p("equation_plates", "famous_equations_set", "Famous_Equations_Wall_Art_Set_of_6.zip"),
        ],
        "tags": [
            "math wall art",
            "physics wall art",
            "equation poster",
            "stem wall art",
            "science poster set",
            "gallery wall set",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print set",
            "science wall art",
        ],
        "notes": (
            "Bundle of 6 equation plates. generate_equation_plates.py. $3.99. "
            "Scales math/physics wall art set demand."
        ),
        "listing_id": 4540082607,
    },

    # ── Special-function plates (scipy) — new listings ───────────────────────
    "bessel_functions_print": {
        "title": (
            "Physics Wall Art | Bessel Functions Print | Circular Drum Modes "
            "Jn STEM Mathematics Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["bessel_functions_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("special_plates", "bessel_functions", "previews", "bessel_functions_preview_1_hero.jpg"),
            p("special_plates", "bessel_functions", "previews", "bessel_functions_preview_2_detail.jpg"),
            p("special_plates", "bessel_functions", "previews", "bessel_functions_preview_3_included.jpg"),
            p("special_plates", "bessel_functions", "previews", "bessel_functions_preview_4_plate.jpg"),
            p("special_plates", "bessel_functions", "previews", "bessel_functions_preview_5_equation.jpg"),
        ],
        "files": [p("special_plates", "bessel_functions", "Bessel_Functions_Physics_Wall_Art.zip")],
        "tags": [
            "physics wall art",
            "bessel function",
            "math wall art",
            "stem wall art",
            "science poster",
            "mathematics poster",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "wave equation",
            "science wall art",
        ],
        "notes": "generate_special_plates.py + scipy.special. NEW listing. $2.99.",
        "listing_id": 4540091753,
    },
    "hermite_qho_print": {
        "title": (
            "Physics Wall Art | Quantum Harmonic Oscillator Print | Hermite "
            "Wavefunctions STEM Science Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["hermite_qho_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("special_plates", "hermite_qho", "previews", "hermite_qho_preview_1_hero.jpg"),
            p("special_plates", "hermite_qho", "previews", "hermite_qho_preview_2_detail.jpg"),
            p("special_plates", "hermite_qho", "previews", "hermite_qho_preview_3_included.jpg"),
            p("special_plates", "hermite_qho", "previews", "hermite_qho_preview_4_plate.jpg"),
            p("special_plates", "hermite_qho", "previews", "hermite_qho_preview_5_equation.jpg"),
        ],
        "files": [p("special_plates", "hermite_qho", "Hermite_QHO_Physics_Wall_Art.zip")],
        "tags": [
            "physics wall art",
            "quantum physics art",
            "harmonic oscillator",
            "math wall art",
            "stem wall art",
            "science poster",
            "hermite polynomial",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "quantum mechanics",
            "science wall art",
        ],
        "notes": "generate_special_plates.py + scipy Hermite QHO. NEW listing. $2.99.",
        "listing_id": 4540091851,
    },
    "legendre_polynomials_print": {
        "title": (
            "Math Wall Art | Legendre Polynomials Print | Orthogonal Polynomials "
            "Spherical STEM Mathematics Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["legendre_polynomials_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("special_plates", "legendre_polynomials", "previews", "legendre_polynomials_preview_1_hero.jpg"),
            p("special_plates", "legendre_polynomials", "previews", "legendre_polynomials_preview_2_detail.jpg"),
            p("special_plates", "legendre_polynomials", "previews", "legendre_polynomials_preview_3_included.jpg"),
            p("special_plates", "legendre_polynomials", "previews", "legendre_polynomials_preview_4_plate.jpg"),
            p("special_plates", "legendre_polynomials", "previews", "legendre_polynomials_preview_5_equation.jpg"),
        ],
        "files": [p("special_plates", "legendre_polynomials", "Legendre_Polynomials_Math_Wall_Art.zip")],
        "tags": [
            "math wall art",
            "legendre polynomial",
            "mathematics poster",
            "stem wall art",
            "science poster",
            "spherical harmonics",
            "educational poster",
            "classroom decor",
            "nerd gift",
            "digital download",
            "teacher gift",
            "math print",
            "physics wall art",
        ],
        "notes": "generate_special_plates.py + scipy Legendre. NEW listing. $2.99.",
        "listing_id": 4540091917,
    },
    "mandelbrot_zoom_print": {
        "title": (
            "Math Wall Art | Mandelbrot Zoom Print | Seahorse Valley Fractal "
            "Detail Chaos STEM Poster (Digital Download)"
        ),
        "description": DESCRIPTIONS["mandelbrot_zoom_print"],
        "price": 2.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            p("special_plates", "mandelbrot_zoom", "previews", "mandelbrot_zoom_preview_1_hero.jpg"),
            p("special_plates", "mandelbrot_zoom", "previews", "mandelbrot_zoom_preview_2_detail.jpg"),
            p("special_plates", "mandelbrot_zoom", "previews", "mandelbrot_zoom_preview_3_included.jpg"),
            p("special_plates", "mandelbrot_zoom", "previews", "mandelbrot_zoom_preview_4_plate.jpg"),
            p("special_plates", "mandelbrot_zoom", "previews", "mandelbrot_zoom_preview_5_equation.jpg"),
        ],
        "files": [p("special_plates", "mandelbrot_zoom", "Mandelbrot_Zoom_Math_Wall_Art.zip")],
        "tags": [
            "math wall art",
            "mandelbrot set",
            "fractal art",
            "chaos theory",
            "mathematics poster",
            "stem wall art",
            "generative art",
            "educational poster",
            "nerd gift",
            "digital download",
            "teacher gift",
            "complex dynamics",
            "math print",
        ],
        "notes": (
            "generate_special_plates.py Mandelbrot seahorse zoom. "
            "Companion NEW listing to mandelbrot_set_print (classic view). $2.99."
        ),
        "listing_id": 4540109240,
    },
}

# ── Funciones de utilidad ─────────────────────────────────────────────────────

def check_product_files(slug):
    """Verifica que todos los archivos de un producto existen antes de subir."""
    prod = PRODUCTS[slug]
    missing = []
    to_check = list(prod["images"]) + list(prod["files"])
    if prod.get("video"):
        to_check.append(prod["video"])
    for f in to_check:
        if not os.path.exists(f):
            missing.append(f)
    if missing:
        print(f"[{slug}] Archivos faltantes:")
        for m in missing:
            print(f"  [FALTA] {m}")
        return False
    print(f"[{slug}] Todos los archivos presentes [OK]")
    return True


def upload_product(slug, dry_run=False):
    """
    Sube un producto a Etsy como borrador.
    slug: clave de PRODUCTS, o "all" para subir todos.
    dry_run=True: solo muestra qué se subiría sin llamar al API.
    """
    if slug == "all":
        for s in PRODUCTS:
            upload_product(s, dry_run=dry_run)
        return

    if slug not in PRODUCTS:
        print(f"Producto '{slug}' no encontrado. Disponibles: {list(PRODUCTS.keys())}")
        return

    prod = PRODUCTS[slug]
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Subiendo: {slug}")
    print(f"  Título:  {prod['title'][:60]}...")
    print(f"  Precio:  ${prod['price']}")
    print(f"  Imágenes: {len(prod['images'])}")
    print(f"  Archivos: {len(prod['files'])}")
    if prod["notes"]:
        print(f"  Nota: {prod['notes']}")

    if not check_product_files(slug):
        print(f"  Abortando '{slug}' por archivos faltantes.")
        return

    if dry_run:
        return

    manager = etsy_manager.EtsyManager()
    listing_id = manager.create_full_product(
        title=prod["title"],
        description=prod["description"],
        price=prod["price"],
        taxonomy_id=prod["taxonomy_id"],
        image_paths=prod["images"],
        digital_file_paths=prod["files"],
        video_path=prod.get("video"),
        tags=prod.get("tags"),
    )
    print(f"  -> Borrador creado: listing_id={listing_id}")
    return listing_id


def get_taxonomy_id(keyword="coloring"):
    """
    Busca nodos de taxonomía en el API de Etsy que coincidan con keyword.
    Útil para encontrar el taxonomy_id correcto antes de publicar.
    """
    manager = etsy_manager.EtsyManager()
    nodes = manager.make_request('GET', '/application/seller-taxonomy/nodes')
    results = []
    def search(node):
        if keyword.lower() in node.get("name", "").lower():
            results.append({"id": node["id"], "name": node["name"],
                            "path": node.get("full_path_taxonomy_ids", [])})
        for child in node.get("children", []):
            search(child)
    for n in nodes.get("results", []):
        search(n)
    for r in results:
        print(f"  id={r['id']:6d}  {r['name']}")
    return results


# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if not args or args[0] == "list":
        print("Productos disponibles:")
        for slug, prod in PRODUCTS.items():
            ready = "✓" if not prod["images"] == [] or prod["files"] else "✗"
            status = "LISTO" if "PENDIENTE" not in prod["notes"] else "PENDIENTE"
            print(f"  [{status:8s}] {slug:<35} ${prod['price']}")
        print("\nUso:")
        print("  python products_catalog.py dry-run <slug|all>")
        print("  python products_catalog.py upload  <slug|all>")
        print("  python products_catalog.py taxonomy [keyword]")

    elif args[0] == "dry-run":
        slug = args[1] if len(args) > 1 else "all"
        upload_product(slug, dry_run=True)

    elif args[0] == "upload":
        slug = args[1] if len(args) > 1 else "all"
        upload_product(slug, dry_run=False)

    elif args[0] == "taxonomy":
        keyword = args[1] if len(args) > 1 else "coloring"
        print(f"Buscando taxonomía '{keyword}'...")
        get_taxonomy_id(keyword)

    else:
        print(f"Comando no reconocido: {args[0]}")
