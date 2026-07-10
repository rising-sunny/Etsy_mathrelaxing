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
ATTR = os.path.join(BASE, "attractor_prints")
LULU = os.path.join(BASE, "lulu_books", "output")
PAL  = os.path.join(BASE, "palettes")
BEQ  = os.path.join(BASE, "beautiful_equations")
FRAC = os.path.join(BASE, "fractal_palettes")

def p(*parts): return os.path.join(BASE, *parts)
def ff(*parts): return os.path.join(FF, *parts)
def sg(*parts): return os.path.join(SG, *parts)
def attractor(*parts): return os.path.join(ATTR, *parts)
def lulu(*parts): return os.path.join(LULU, *parts)
def pal(*parts): return os.path.join(PAL, *parts)
def beq(*parts): return os.path.join(BEQ, *parts)
def frac(*parts): return os.path.join(FRAC, *parts)

# ── Taxonomy IDs verificados ──────────────────────────────────────────────────
# Fuente: GET /application/seller-taxonomy/nodes (llamada al API de Etsy)
# Para descubrir IDs ejecutar: manager.make_request('GET', '/application/seller-taxonomy/nodes')
# IDs verificados contra el árbol real de Etsy: GET /seller-taxonomy/nodes
# (OJO: la ruta correcta es '/seller-taxonomy/nodes' — base_url ya incluye /v3/application)
TAXONOMY = {
    "coloring_book":    2078,   # = "Art & Collectibles > Prints > Digital Prints" (lo usan FF/SG PDF)
    "ipad_coloring":    339,    # = "Books, Movies & Music > Books > Coloring Books" (ediciones iPad)
    "coloring_book_physical": 339,  # mismo nodo que ipad_coloring -- Etsy no separa fisico/digital a nivel de categoria
    "digital_art":      2078,   # = Digital Prints (atractores/art prints)
    "digital_drawing":  77,     # = "Art & Collectibles > Drawing & Illustration > Digital" (assets tipo paletas Procreate)
    "planner_template": 12476,  # = "Paper > Stationery > Templates > Planner Templates" (notebooks/planners digitales)
    "journal_template": 12475,  # = "... > Templates > Journal Templates" (variante journal/cuaderno)
    "root":             1,      # fallback genérico
}

# Shipping profile para libros fisicos POD (Lulu) -- creado en Etsy Shop Manager
# > Settings > Shipping, ver STANDARDS.md Tipo 8 para el detalle de destinos/costos.
SHIPPING_PROFILE_LULU_BOOKS = 310608167423
# Processing profile ("Tus perfiles de preparacion"): hecho a pedido, 3-5 dias.
READINESS_STATE_LULU_BOOKS = 1498071010932
# Return policy del shop (unica existente, creada automaticamente por Etsy).
# Los primeros 4 listings fisicos se crearon SIN esto (create_draft_listing no
# lo pedia todavia) y quedaron con return_policy_id=None -- corregido a mano
# via update_listing() el 2026-07-07. create_draft_listing ahora lo exige.
RETURN_POLICY_ID = 1496849341269

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

    "mathematical_tangle_art_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 elaborate Zentangle-inspired designs built from pure mathematical curves: \
Lissajous figures, rose curves, epicycloids, spirals and more — woven into \
dense, meditative patterns for hours of mindful coloring.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original mathematical tangle designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

    "sacred_harmonics_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 designs where sound meets sacred geometry: Chladni figures, cymatics \
patterns, harmonic wave interference, and resonant mandalas — the hidden \
geometry of vibration made visible and colorable.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original cymatics & harmonic designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

    "neural_network_pdf": """\
Instant download — printable coloring book PDF (50 pages, 8.5×11 in).
50 futuristic designs blending neural network architectures, cybernetic circuits, \
and complex radial graph topologies. Perfect for coders, AI enthusiasts, \
and anyone who loves high-tech geometry.

► What you get
• 1 high-resolution PDF (print-ready)
• 50 original neural network & tech art designs

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

    "de_jong_attractor": """\
Instant download — seamless loop animation (MP4, 1080×1080, 30 fps, 8 s).
The De Jong attractor — a chaotic dynamical system discovered by physicist \
Peter de Jong — rendered as a glowing electric-cyan filament against deep \
indigo. Every frame morphs continuously along a closed parameter path, so \
the shape never stops evolving yet always returns exactly to where it began. \
Loops perfectly for wallpapers, screensavers, digital frames, or social \
media backgrounds.

► What you get
• 1 MP4 file — 1080×1080 px, 30 fps, 8-second seamless loop
• Silent (add your own music or keep it ambient)

► Art born from equations.

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

    "phyllotaxis_bloom": """\
Instant download — seamless loop animation (MP4, 1600×1600, 60 fps, 8 s).
15,000 particles of light, placed by the golden angle — the same rule that \
arranges sunflower seeds and pinecone scales — breathing, twinkling, and \
swirling in warm gold and cream against near-black. The whole field turns \
like a single body while the core spins faster than the edge, the same \
shearing motion you see in a spiral galaxy. Every particle keeps its place \
in the spiral forever; the bloom never stops shimmering yet always returns \
exactly to where it began. Loops perfectly for wallpapers, screensavers, \
digital frames, or social media backgrounds.

► What you get
• 1 MP4 file — 1600×1600 px, 60 fps, 8-second seamless loop, high resolution
• Silent (add your own music or keep it ambient)

► Art born from equations.

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

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
mathrelaxing.store""",

    "life_planner": """\
Instant download — undated all-in-one digital planner for GoodNotes, Notability \
& any PDF annotation app on iPad, Android & Windows tablets. 500+ fully \
hyperlinked pages: one planner for every part of your life.

► What's inside (500+ hyperlinked pages)
• Full calendar system — year at a glance, 12 monthly spreads, 52 weekly \
layouts & 365 daily pages (all undated, start any day)
• Quarterly planners (Q1–Q4), yearly goals, year in review, key dates & highlights
• 50+ life trackers & templates across 5 categories:
   – Lifestyle: wishlist, contacts, book log, watchlist, trip planner, passwords, cleaning
   – Wellness: meal planner, mood, sleep, water, workout, symptom, period & vitamin trackers
   – Self-Care: gratitude, bucket list, vision board, dream journal, affirmations
   – Productivity: to-do, priority matrix, habit tracker, time tracker, SMART goals, projects
   – Finance: budget, expenses, savings, bills, subscriptions, debt payoff & investments
• Note-taking pages — dot grid, squared, lined, Cornell & isometric
• Tap-to-jump navigation on every page: category hubs + side tabs

► How to use
Import the PDF into GoodNotes, Notability, Penly, Xodo or any annotation app. \
Tap any tab or link to jump instantly. Duplicate any page as many times as you \
like — start any month, any year.

This is a DIGITAL file — no physical product is shipped. A separate PDF \
annotation app is required. Not designed for printing.

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

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
mathrelaxing.store""",

    "graph_paper": """\
Instant download — printable graph & grid paper in 8 styles, US Letter + A4.

Clean, edge-to-edge grids drawn from scratch (not scanned) — the ones you \
actually need for math, engineering, drafting, bullet journaling and note-taking, \
including the isometric and hexagonal sheets that are so hard to find printable.

► What you get (2 PDFs — US Letter 8.5×11 in AND A4)
Each PDF has all 8 styles, one per page:
• Square grid — 5 mm (with darker major lines every 5th)
• Square grid — 1/4 inch
• Dot grid — 5 mm
• Isometric — for 3D sketching & technical drawing
• Triangular
• Hexagonal — for organic chemistry, game maps, tiling
• Cornell notes — cue column, notes area & summary
• College ruled

► How to use
Open the PDF for your paper size and print the page you need at 100% / \
"Actual size" (not "fit to page", so the grid keeps its true spacing). \
Print as many as you like. Works on any printer, black & white is fine.

This is a DIGITAL download — no physical item is shipped.

© MathRelaxing. For personal & classroom use. Do not resell or redistribute \
the files themselves.
mathrelaxing.store""",

    "fractal_palettes": """\
Instant download — 8 Procreate color palettes (.swatches), 30 colors each.

Every palette here is the real color signature of a famous fractal — a \
Mandelbrot, Julia or Burning Ship set computed from the escape-time \
algorithm in Python, then sampled color-by-color into a smooth ramp. No \
stock photos, no AI. Just mathematics, turned into a palette you can paint \
with.

► What you get (240 curated colors)
• Ember Mandelbrot — maroon → red → orange → gold
• Glacier Julia — midnight → blue → icy cyan → white
• Jade Julia — deep forest → emerald → mint
• Amethyst Julia — indigo → violet → lilac
• Sunset Julia — plum → magenta → coral → amber
• Molten Ship — black → rust → ember gold
• Peacock Mandelbrot — deep teal → jade → soft gold
• Rose Gold Julia — wine → rose → blush → cream

8 .swatches files (30 swatches each), delivered in one .zip, plus an \
install guide.

► How to install (Procreate on iPad)
Open Procreate → tap the color circle → Palettes → the + button → \
"New from file" → pick a .swatches file. It loads as a ready-to-use \
30-color palette. Works in any app that reads Procreate .swatches.

This is a DIGITAL download — no physical item is shipped.

© MathRelaxing. For personal & commercial artwork. Do not resell or \
redistribute the palette files themselves.
mathrelaxing.store""",

    "chaos_palettes": """\
Instant download — 8 Procreate color palettes (.swatches), 30 colors each.

Every palette here is the real color signature of a chaotic dynamical \
system — a strange attractor or generative pattern rendered from its \
equations in Python, then sampled color-by-color. No stock photos, no AI. \
Just mathematics, turned into a palette you can paint with.

► What you get (240 curated colors)
• Rossler Amber — warm gold on black
• Rossler Rose — deep magenta & plum
• Vector Field Teal — electric cyan-teal
• Vector Field Copper — molten rust & orange
• Vector Field Indigo — violet & midnight blue
• Voronoi Garden — plum → coral → gold (a full spectrum)
• De Jong Ice — navy → glacial cyan
• Julia Jade — teal → mint → warm jade

8 .swatches files (30 swatches each), delivered in one .zip, plus an \
install guide.

► How to install (Procreate on iPad)
Open Procreate → tap the color circle → Palettes → the + button → \
"New from file" → pick a .swatches file. It loads as a ready-to-use \
30-color palette. Works in any app that reads Procreate .swatches.

This is a DIGITAL download — no physical item is shipped.

© MathRelaxing. For personal & commercial artwork. Do not resell or \
redistribute the palette files themselves.
mathrelaxing.store""",

    "phd_planner": """\
Instant download — undated digital planner for GoodNotes, Notability & any PDF \
annotation app on iPad, Android & Windows tablets. Built for one job: getting \
you from first proposal to final defense without losing track of anything.

► What's inside (136 hyperlinked pages)
• Research Roadmap — a multi-year milestone Gantt (coursework → lit review → \
proposal → data → analysis → writing → revisions → defense), one grid per year
• Chapter Progress tracker — draft / revised / sent to advisor / approved, \
for every chapter and section
• Literature Log — 70+ paper cards with citation, key finding, relevance \
rating & themes, so your reading never turns into a pile of forgotten PDFs
• Advisor & Committee Meeting log — agenda, discussion, decisions and action \
items for 24 meetings (never show up unprepared again)
• 52 Weekly Research pages — top 3 priorities, a daily writing-word tracker \
and a 7-day task planner
• 12 Monthly Overviews — objectives, milestones reached & a "what moved the \
thesis forward?" review
• Conferences & Deadlines — submissions, travel and funding, all in one table
• Qualifying / Comprehensive Exam prep + a full Dissertation Defense checklist
• Dot-grid Research Notes pages
• Tap-to-jump navigation on every page: dashboard + side tabs

► How to use
Import the PDF into GoodNotes, Notability, Penly, Xodo or any annotation app. \
Tap any tab or link to jump instantly. Undated — start any day, duplicate any \
page as many times as you need.

This is a DIGITAL file — no physical product is shipped. A separate PDF \
annotation app is required.

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",

    "physics_calculus_equations": """\
Eight equations from physics and calculus, set as elegant typography —
a gallery-style collection for anyone who loves science, mathematics,
or the quiet order beneath the world.

Each equation is typeset in Computer Modern (the classic typeface of
LaTeX, the language mathematicians actually write in) on a deep navy
ground, with its name and field. No AI, no clip-art — every poster is
designed from scratch.

────────────────────────
THE EIGHT EQUATIONS
────────────────────────
· Newton's Second Law — 𝐅 = m𝐚 (full vector form)
· Universal Gravitation — 𝐅 = −G·m₁m₂/r²·r̂ (full vector form)
· The Ideal Gas Law — PV = nRT
· The Planck–Einstein Relation — E = hν
· The Basel Problem — Σ 1/n² = π²/6
· The Fundamental Theorem of Calculus
· The Uncertainty Principle — ΔxΔp ≥ ℏ/2
· The Taylor Series

────────────────────────
WHAT YOU GET · instant download
────────────────────────
One ZIP with all 8 designs in two formats:
· 8 × PDF — vector, prints razor-sharp at ANY size
· 8 × JPG — 7200 × 9000 px (print-ready up to 24×30 in at 300 dpi)
Proportion 4:5 — frames beautifully in 8×10, 16×20 or 24×30 in.

────────────────────────
PERFECT FOR
────────────────────────
A study, classroom, lab or office · a gift for a mathematician,
physicist, engineer, teacher or new graduate · dark-academia and
minimalist interiors.

────────────────────────
PRINTING TIPS
────────────────────────
· Best on matte or satin paper, framed
· Any local print shop or online service (Printful, Canva Print,
  Costco Photo) can handle these files

────────────────────────
INSTANT DOWNLOAD · No physical item is shipped.
────────────────────────

I'm an electrical engineer who got lost in recreational mathematics.
Every piece in this shop is written from scratch in Python — equations,
typography, colours and all.
mathrelaxing.store""",

    "attractor_collection": """\
Six strange attractors of chaos theory, rendered entirely with code —
a field-guide poster of deterministic chaos.

No AI, no stock. Each attractor is computed from its own equations in
Python and drawn as a luminous gold density map: the Lorenz butterfly,
the Rössler band, the Thomas cyclically-symmetric loop, the Aizawa
sphere, and the De Jong & Clifford iterated maps — each with its name
and governing equations typeset beside it.

A strange attractor is the shape a chaotic system is drawn toward:
deterministic (no randomness at all) yet never exactly repeating.
This poster gathers six of the most beautiful, side by side.

────────────────────────
WHAT YOU GET
────────────────────────
1 high-resolution JPG poster
Resolution: 9000 × 12000 px (print-ready up to 30×40 inches at 300dpi)
Format: JPG, high quality

────────────────────────
PRINTING TIPS
────────────────────────
· Best on matte or satin paper — stunning framed for a study, lab,
  classroom or office
· Any local print shop or online service (Printful, Canva Print,
  Costco Photo) can handle this file

────────────────────────
INSTANT DOWNLOAD · No physical item is shipped.
────────────────────────

I'm an electrical engineer who got lost in recreational mathematics.
Every piece in this shop is written from scratch in Python — equations,
rendering, colours and all.
mathrelaxing.store""",

    "harmonograph_print": """\
A harmonograph figure, rendered entirely with code.

No AI image generators were used — this is pure mathematics made
visible. A harmonograph is a Victorian drawing machine (c. 1870):
a pen swung by two decaying pendulums traces a curve that loops
over itself thousands of times. Here that curve is computed from
its equations:

  x(t) = a₁·sin(f₁t + p₁)·e^(−d₁t) + a₂·sin(f₂t + p₂)·e^(−d₂t)
  y(t) = a₃·sin(f₃t + p₃)·e^(−d₃t) + a₄·sin(f₄t + p₄)·e^(−d₄t)

The damping (e^−dt) shrinks each successive loop, nesting them into
a delicate web of interference — brightest where the curve crosses
itself, fading to a whisper at the edges.

────────────────────────
WHAT YOU GET
────────────────────────
3 high-resolution JPG files (same design, 3 color variants):
· Moonlit — deep blue to glacial cyan
· Rose Gold — plum & magenta with warm gold nodes
· Verdigris — emerald to mint green

Resolution: 9000 × 9000 px (square, print-ready up to 30×30 inches at 300dpi)
Format: JPG, high quality

────────────────────────
PRINTING TIPS
────────────────────────
· Best printed on matte or satin paper
· Stunning as a large framed square or canvas
· A local print shop or online service (Printful, Canva Print,
  Costco Photo) can handle this file easily

────────────────────────
INSTANT DOWNLOAD
────────────────────────
Files are available immediately after purchase.
No physical item will be shipped.

────────────────────────
ABOUT THE ARTIST
────────────────────────
I'm an electrical engineer who got lost in recreational
mathematics. Every piece in this shop is written from scratch
in Python — equations, rendering, colors and all.""",

    "rossler_attractor_print": """\
A Rössler strange attractor, rendered entirely with code.

No AI image generators were used — this is pure mathematics
made visible. The attractor is computed by solving this system
of differential equations:

  dx/dt = −y − z
  dy/dt = x + a·y
  dz/dt = b + z(x − c)

  a = 0.2  ·  b = 0.2  ·  c = 5.7

A single trajectory is followed for hundreds of thousands of steps,
folding over itself again and again in a band that never quite
closes and never quite repeats — deterministic chaos made visible
as a spiral galaxy of light.

────────────────────────
WHAT YOU GET
────────────────────────
3 high-resolution JPG files (same design, 3 color variants):
· Classic — electric cyan on black
· Violet — soft magenta on black
· Amber — warm gold on black

Resolution: 5400 × 7200 px (print-ready up to 18×24 inches at 300dpi)
Format: JPG, high quality

────────────────────────
PRINTING TIPS
────────────────────────
· Best printed on matte or satin paper
· Works great as a poster, framed print, or canvas
· A local print shop or online service (Printful, Canva Print,
  Costco Photo) can handle this file easily

────────────────────────
INSTANT DOWNLOAD
────────────────────────
Files are available immediately after purchase.
No physical item will be shipped.

────────────────────────
ABOUT THE ARTIST
────────────────────────
I'm an electrical engineer who got lost in recreational
mathematics. Every piece in this shop is written from scratch
in Python — equations, rendering, colors and all.""",

    "vector_field_print": """\
A 2D vector field, rendered entirely with code.

No AI image generators were used — this is pure mathematics
made visible. Every curve on this poster is a streamline: at
each point on the page an invisible arrow tells the flow which
way to move, and the line simply follows those arrows.

The flow is built from a handful of point singularities placed
across the canvas — sources (flow radiating outward), sinks
(flow draining inward), vortices (flow spinning around a point),
and a saddle (flow diverging on one axis, converging on the
other) — the same mathematics used to model wind, water currents,
and magnetic fields. Thousands of streamlines, seeded across the
full canvas and traced in both time directions, reveal how every
point on the page connects to every singularity.

────────────────────────
WHAT YOU GET
────────────────────────
3 high-resolution JPG files (same design, 3 color variants):
· Aurora Teal — electric cyan-teal on black
· Ember Copper — warm copper-orange on black
· Midnight Indigo — deep violet-blue on black

Resolution: 9000 × 12000 px (print-ready up to 30×40 inches at 300dpi)
Format: JPG, high quality

────────────────────────
PRINTING TIPS
────────────────────────
· Best printed on matte or satin paper
· Works great as a poster, framed print, or canvas
· A local print shop or online service (Printful, Canva Print,
  Costco Photo) can handle this file easily

────────────────────────
INSTANT DOWNLOAD
────────────────────────
Files are available immediately after purchase.
No physical item will be shipped.

────────────────────────
ABOUT THE ARTIST
────────────────────────
I'm an electrical engineer who got lost in recreational
mathematics. Every piece in this shop is written from scratch
in Python — equations, rendering, colors and all.""",

    "hyperbolic_gardens_physical": """\
PRINTED physical coloring book — ships to your door (50 designs, 8.5×11 in, perfect-bound).
Journey into hyperbolic geometry with 50 intricate tiling designs inspired \
by Escher's Circle Limit series and the Poincaré disc model. Each design repeats \
toward infinity — a meditative coloring experience unlike any other.

► What you get
• A real printed book, 8.5×11 in, matte perfect-bound cover
• 50 original hyperbolic tiling designs, printed on 60# (90 gsm) uncoated white paper
• A blank page after every design, so pens/markers never bleed through to the next one
• Made fresh for your order (print-on-demand) — ships in 3-5 business days

© MathRelaxing. mathrelaxing.store""",

    "fractal_flora_physical": """\
PRINTED physical coloring book — ships to your door (50 designs, 8.5×11 in, perfect-bound).
Lose yourself in 50 unique fractal & botanical line-art designs: Dragon Curves, \
Julia Sets, Barnsley Ferns, twin fractals, and more — all drawn with mathematical \
precision and free of color numbers.

► What you get
• A real printed book, 8.5×11 in, matte perfect-bound cover
• 50 original fractal & botanical designs, printed on 60# (90 gsm) uncoated white paper
• A blank page after every design, so pens/markers never bleed through to the next one
• Made fresh for your order (print-on-demand) — ships in 3-5 business days

© MathRelaxing. mathrelaxing.store""",

    "sacred_math_physical": """\
PRINTED physical coloring book — ships to your door (50 designs, 8.5×11 in, perfect-bound).
Fifty 3D mathematical surfaces — tori, Möbius bands, helicoids, golden spirals \
and faceted gems — projected into flat, numbered regions. Match the numbers to \
the palette and watch the illusion of volume emerge as you color. Each model is \
rendered from its real parametric equations, not traced by hand.

► What you get
• A real printed book, 8.5×11 in, matte perfect-bound cover
• 50 original 3D color-by-number designs, printed on 60# (90 gsm) uncoated white paper
• A blank page after every design, so pens/markers never bleed through to the next one
• Made fresh for your order (print-on-demand) — ships in 3-5 business days

© MathRelaxing. mathrelaxing.store""",

    "voronoi_gardens_physical": """\
PRINTED physical coloring book — ships to your door (50 designs, 8.5×11 in, perfect-bound).
50 mesmerizing Voronoi designs grown from pure mathematics: radial mandalas, \
golden-angle sunflower spirals, cathedral rose windows and softly relaxed organic \
cells. Every cell is a closed region — perfect for clean, satisfying color fills.

► What you get
• A real printed book, 8.5×11 in, matte perfect-bound cover
• 50 original Voronoi designs, printed on 60# (90 gsm) uncoated white paper
• A blank page after every design, so pens/markers never bleed through to the next one
• Made fresh for your order (print-on-demand) — ships in 3-5 business days

© MathRelaxing. mathrelaxing.store""",
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
mathrelaxing.store""",

    "sacred_geometry_ipad_svg": """\
Color low-poly 3D sacred geometry on your iPad — no printer, no app to install, no mess. A fully INTERACTIVE, app-like Color-by-Number experience that runs right in Safari.

This digital bundle features 50 original three-dimensional designs — faceted tori, Möbius bands and geometric gems, each built from real mathematics and lit like a 3D object. Color the numbers from 1 (shadow) to 8 (highlight) and the flat facets pop into a shaded three-dimensional form. It is NOT a static PDF. You get 50 interactive HTML files that open directly in your iPad's Safari browser (no internet needed). Because they use vector SVG graphics, you can zoom in infinitely without ANY pixelation — no more blurry lines or numbers crashing into borders.

Features:
• A true low-poly 3D look — the numbers follow each facet's lighting, so coloring reveals depth and volume
• Infinite zoom with perfectly crisp lines (true vector SVG)
• Tap-to-fill: pick a shade from the palette, tap a facet, done
• Auto-hiding numbers: the number vanishes the moment you color its facet
• Progress saves automatically — close the tab and pick up later
• Works 100% offline, on iPad, iPhone, Android, Mac or PC
• 50 unique mathematically-generated 3D surfaces

────────────────────────
WHAT YOU GET · instant download
────────────────────────
• 50 interactive HTML designs (one file each) in a ZIP
• A "How to Use on iPad" instructions PDF
• No physical item is shipped

────────────────────────
ABOUT THE ART
────────────────────────
Every design is a real mathematical surface — a torus, a Möbius band, a faceted sphere — triangulated and shaded by light in code, never AI image generators.

© MathRelaxing. For personal use only. Not for redistribution or resale.
mathrelaxing.store""",
}

# ── Catálogo de productos ─────────────────────────────────────────────────────
PRODUCTS = {

    "physics_calculus_equations": {
        "title":       "Set of 8 Physics & Calculus Equation Art Prints, Minimalist Math Wall Art | Newton Heisenberg Poster Bundle | Printable Digital Download",
        "description": DESCRIPTIONS["physics_calculus_equations"],
        "price":       7.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            beq("_hero.jpg"),
            beq("newton_second_law_preview.jpg"),
            beq("gravitation_preview.jpg"),
            beq("ideal_gas_preview.jpg"),
            beq("planck_einstein_preview.jpg"),
            beq("basel_preview.jpg"),
            beq("fundamental_calculus_preview.jpg"),
            beq("heisenberg_preview.jpg"),
            beq("taylor_series_preview.jpg"),
            beq("_whatyouget.jpg"),
        ],
        "files": [
            beq("PhysicsCalculusEquations_Set8.zip"),
        ],
        "tags": ["math wall art","physics poster","mathematics poster","minimalist math",
                 "science wall art","newton second law","physics art print","printable art",
                 "math teacher gift","physics teacher gift","classroom decor","academic gift",
                 "digital download"],
        "notes": "Tipo 5 pero NUEVA LINEA: arte matematico CONCEPTUAL/tipografico (no histograma de "
                  "densidad). ORIGINALMENTE llamado 'beautiful_equations' con Euler/Pitagoras/E=mc2/"
                  "phi/Basel/FTC/Gaussiana/Schrodinger -- se descubrio DESPUES de crear el borrador "
                  "que la tienda YA TENIA 2 listings activos no trackeados en este catalogo con el "
                  "mismo concepto navy/oro/LaTeX: 'Mathematical Constants Bundle' (listing_id="
                  "4534820167: pi,e,phi,sqrt2,i,infinity,0,1) y 'Beautiful Equations Bundle' "
                  "(listing_id=4534831774: Euler's Identity, Pythagorean Theorem, Schrodinger, "
                  "Maxwell's First Equation, E=mc^2, Gaussian Integral, Heat Equation, Bayes' "
                  "Theorem) -- 6 de las 8 ecuaciones originales coincidian. Renombrado a "
                  "'physics_calculus_equations' con set 100% sin overlap: Newton's Second Law, "
                  "Universal Gravitation, Ideal Gas Law, Planck-Einstein, Basel Problem (unica que "
                  "se mantuvo), Fundamental Theorem of Calculus (unica que se mantuvo), Heisenberg "
                  "Uncertainty, Taylor Series. Precio $7.99 (los 2 listings hermanos estan a $6.99). "
                  "beautiful_equations/generate_equations.py rinde c/u a 8x10 logico -> PDF "
                  "VECTOR (imprime nitido a cualquier tamano, el gran plus tipografico) + JPG 7200x9000 "
                  "(24x30@300dpi) + preview watermarkeado. build_bundle_and_assets.py empaqueta los 16 "
                  "archivos (8 pdf+8 jpg) + READ_ME en UN zip de 3.7MB (Etsy limita 5 archivos/listing) "
                  "y genera _hero.jpg (grid 2x4 de las 8) + _whatyouget.jpg. 10 imagenes (hero + 8 "
                  "previews + whatyouget). Extensible: mas ecuaciones sin overlap (Fourier, Dirac, "
                  "Coulomb, entropia de Shannon) o variante pizarra. Draft listing_id=4535639595 "
                  "(creado 2026-07-10, reescrito el mismo dia tras detectar el overlap). Activacion "
                  "manual pendiente. IMPORTANTE: revisar tambien los listings 4534820167 y 4534831774 "
                  "para agregarlos a este catalogo (no estaban trackeados).",
    },

    "attractor_collection": {
        "title":       "Strange Attractors Poster | Chaos Theory Math Wall Art, 6 Attractors with Equations | Science Physics Print Digital Download",
        "description": DESCRIPTIONS["attractor_collection"],
        "price":       12.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            attractor("collection", "StrangeAttractors_preview.jpg"),
            attractor("collection", "StrangeAttractors_detail1.jpg"),
            attractor("collection", "StrangeAttractors_detail2.jpg"),
        ],
        "files": [
            attractor("collection", "StrangeAttractors_print.jpg"),
        ],
        "tags": ["strange attractor","chaos theory art","math poster","science wall art",
                 "lorenz attractor","physics art print","generative art","math gift",
                 "stem wall decor","dark academia print","dorm wall art","code art print",
                 "differential equations"],
        "notes": "Tipo 5 (art print generativo), pero NUEVO formato: POSTER-COLECCION (no un atractor "
                  "suelto). Nicho validado via API: 'strange attractor poster' ~15 listings pero top $18 "
                  "con 110 favs/1.459 vistas -> demanda fuerte, competencia minima. Producto de ticket mas "
                  "alto ($12.99) reusando la tecnica de histograma de densidad ya perfeccionada. "
                  "generate_attractor_collection.py renderiza 6 atractores clasicos en tratamiento "
                  "cohesivo oro-sobre-navy (LUT[0]=navy del poster para que floten sin borde cuadrado): "
                  "Lorenz, Rossler, Thomas, Aizawa (ODEs: pocas trayect x 900k pasos RK4), De Jong y "
                  "Clifford (mapas 2D: 90k trayect x 60 iters). Cada tile con nombre + ecuaciones "
                  "(matplotlib mathtext). Compuesto en poster 18x24 (5400x7200 @300dpi) con titulo 'A "
                  "Field Guide to Deterministic Chaos' + footer con logo. Calidad JPEG 95 (1.66MB, bajo "
                  "el limite). 3 imagenes: preview watermarkeada full + 2 crops de detalle. 'files' = "
                  "poster limpio sin marca. Precio $12.99 (medio entre nuestros prints $8.99 y el top de "
                  "$18 del nicho). Subido como draft el 2026-07-07, listing_id=4534313102. Activacion "
                  "manual pendiente. Extensible: agregar mas atractores o vender variantes de color.",
    },

    "harmonograph_print": {
        "title":       "Harmonograph Art Print | Generative Math Wall Art from a Victorian Pendulum Curve | 3 Colors, 30x30in Digital Download",
        "description": DESCRIPTIONS["harmonograph_print"],
        "price":       8.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            attractor("harmonograph", "harmonograph_moonlit_preview.jpg"),
            attractor("harmonograph", "harmonograph_rosegold_preview.jpg"),
            attractor("harmonograph", "harmonograph_verdigris_preview.jpg"),
        ],
        "files": [
            attractor("harmonograph", "harmonograph_moonlit_print.jpg"),
            attractor("harmonograph", "harmonograph_rosegold_print.jpg"),
            attractor("harmonograph", "harmonograph_verdigris_print.jpg"),
        ],
        "tags": ["harmonograph art","math art print","generative art","pendulum art",
                 "science wall art","math poster","dark wall art","printable wall art",
                 "physics art print","stem wall decor","code art print","lissajous art",
                 "square print"],
        "notes": "Tipo 5 (STANDARDS.md, 'Art print generativo'), tercer print trackeado (tras rossler y "
                  "vector_field). Nicho elegido via API: 'harmonograph art' tiene solo ~44 listings (la "
                  "competencia mas baja vista) pero demanda probada (top $9.37 con 1.081 vistas/12 favs; "
                  "pen-plot a $90; poster a $32); 'lissajous art' ~11 (casi virgen, candidato futuro con "
                  "el mismo motor). 100% on-brand (matematica hecha curva). Motor reusado de lulu_books/"
                  "core/generate_harmonographs.py (4 pendulos amortiguados). Figura fija = seed 1 "
                  "(freqs 3-3-4-5), elegida de un sheet de 12 semillas por ser la mas balanceada/"
                  "gallery-worthy. Pipeline identico a vector_field/rossler: histograma de densidad de "
                  "la curva (14M puntos, es UNA curva continua asi que necesita millones de muestras para "
                  "linea continua a 9000px) + rampa negro->color->blanco + glow; gamma 0.72 para levantar "
                  "la linea de un solo paso (log1p(1) es bajo) y que brille. Cuadrado 9000x9000 (30x30in "
                  "@300dpi) porque la figura es ~circular -- primer print cuadrado del catalogo. 3 paletas "
                  "NUEVAS para no repetir Rossler (cyan/violet/amber) ni Vector Field (teal/copper/indigo): "
                  "moonlit (azul->cian), rose_gold (magenta/oro), verdigris (verde -- el que faltaba). "
                  "~6MB c/u (q98, bajo el limite de 20MB). Bio de artista reusada. Sin franja/logo en el "
                  "vendible (wall art). 'images'=*_preview.jpg (marca de agua diagonal), 'files'=*_print.jpg "
                  "limpio. Subido como draft el 2026-07-07, listing_id=4534117446. Activacion manual pendiente.",
    },

    "rossler_attractor_print": {
        "title":       "Rössler Attractor Art Print – Generative Code Mathematics Wall Art (Digital Download)",
        "description": DESCRIPTIONS["rossler_attractor_print"],
        "price":       8.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            attractor("rossler", "rossler_classic_preview.jpg"),
            attractor("rossler", "rossler_violet_preview.jpg"),
            attractor("rossler", "rossler_amber_preview.jpg"),
        ],
        "files": [
            attractor("rossler", "rossler_classic_print.jpg"),
            attractor("rossler", "rossler_violet_print.jpg"),
            attractor("rossler", "rossler_amber_print.jpg"),
        ],
        "tags": ["rossler attractor","math art print","generative art","strange attractor",
                 "science wall art","math poster","dark wall art","printable wall art",
                 "physics art print","stem wall decor","code art print","chaos theory art",
                 "math gift"],
        "notes": "Tipo 5 (STANDARDS.md, 'Art print generativo') — primer producto de este tipo "
                  "construido y trackeado en el repo. Contexto: existian YA DOS listings live de este "
                  "mismo tipo (Lorenz id=4528168404, Clifford id=4528164675, ambos $5.99, ambos 0 "
                  "vistas/0 favs a 10 dias de publicados) que nunca se sincronizaron al catalogo local "
                  "-- no hay script generador ni backup de sus archivos vendibles (el API no expone "
                  "descarga de 'files' al dueño de la tienda, solo metadata: nombre/tamaño). Rossler es "
                  "nuevo (no duplica Lorenz/Clifford). Generado con generate_rossler_print.py: a "
                  "diferencia de un mapa discreto (De Jong/Clifford), un flujo continuo (ODE) necesita "
                  "POCAS trayectorias x MUCHISIMOS pasos (no muchas trayectorias cortas) para revelar "
                  "la estructura de bandas -- acumulado en histograma durante la integracion (streaming) "
                  "para no acumular memoria. 3 variantes de color (mismo patron que Lorenz/Clifford), "
                  "9000x12000px (30x40in @300dpi, listo para poster/canvas grande), ~3.8-4.2MB c/u "
                  "(subido desde 5400x7200/~1.5MB tras pedido explicito de mayor resolucion para "
                  "impresion grande; STEPS de la simulacion escalado en proporcion a los bins nuevos "
                  "para mantener la densidad de puntos). Blur de render desacoplado de la resolucion "
                  "(antes escalaba con W y borraba las lineas finas al hacer zoom -- ver "
                  "generate_rossler_print.py) para que el detalle de las bandas se vea nitido en "
                  "impresion grande. Sin franja/logo de marca en el archivo vendible "
                  "(a proposito: es wall art para enmarcar, no una pagina de muestra de un producto "
                  "multi-pagina; sigue la convencion ya establecida por los prints de Lorenz/Clifford). "
                  "Bio de 'about the artist' reusada tal cual de los otros dos listings para mantener voz "
                  "consistente de esta sub-linea. Precio $8.99 (subido de $5.99 tras investigar competencia "
                  "real via API: listings similares de 'strange attractor print' venden bien en $10-18 con "
                  "miles de vistas -- el nicho soporta mas de lo que se penso al nivelar todo a $5.99 por "
                  "'competir bajo'. Lorenz/Clifford corregidos igual, ver sus notas). Subido como borrador "
                  "el 2026-07-06, listing_id=4533519822; imagenes/archivos reemplazados el mismo dia por "
                  "la version de alta resolucion. 'images' y 'files' ya NO apuntan al mismo archivo: "
                  "'images' usa *_preview.jpg (2250x3000, marca de agua diagonal tileada 'mathrelaxing.store "
                  "· preview', ver add_preview_watermark en generate_rossler_print.py) y 'files' sigue "
                  "usando el *_print.jpg limpio de 9000x12000 que recibe el comprador -- antes el preview "
                  "publico del listing ERA el archivo vendible completo sin proteccion.",
    },

    "vector_field_print": {
        "title":       "Vector Field Art Print – Generative Code Mathematics Wall Art (Digital Download)",
        "description": DESCRIPTIONS["vector_field_print"],
        "price":       8.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        "images": [
            attractor("vector_field", "vectorfield_teal_preview.jpg"),
            attractor("vector_field", "vectorfield_copper_preview.jpg"),
            attractor("vector_field", "vectorfield_indigo_preview.jpg"),
        ],
        "files": [
            attractor("vector_field", "vectorfield_teal_print.jpg"),
            attractor("vector_field", "vectorfield_copper_print.jpg"),
            attractor("vector_field", "vectorfield_indigo_print.jpg"),
        ],
        "tags": ["vector field art","math art print","generative art","flow field print",
                 "fluid dynamics art","science wall art","math poster","dark wall art",
                 "printable wall art","physics art print","stem wall decor","code art print",
                 "math gift"],
        "notes": "Tipo 5 (STANDARDS.md, 'Art print generativo'), segundo producto de este tipo "
                  "trackeado en el repo (despues de rossler_attractor_print). Origen: se probo primero "
                  "como libro para colorear (gen_vector_field.py, eliminado) pero las streamlines de un "
                  "campo vectorial dejan demasiado espacio en blanco entre si para ese formato -- como "
                  "poster de pared en cambio esa apertura es la composicion, no un defecto. Tecnica "
                  "(generate_vector_field_print.py): superposicion de 7 singularidades puntuales "
                  "(fuente/sumidero/vortice horario/vortice antihorario/silla) fijas a mano para que la "
                  "composicion cubra todo el lienzo; miles de streamlines sembradas en grilla densa con "
                  "jitter e integradas EN AMBAS direcciones de tiempo, todas EN PARALELO (arrays de numpy, "
                  "no una por una) y acumuladas en histograma durante la integracion (mismo patron que "
                  "Rossler). A diferencia de un atractor caotico, el flujo NO es recurrente -- la cobertura "
                  "del lienzo viene de la CANTIDAD de lineas sembradas, no de que una sola trayectoria de "
                  "muchas vueltas. Bug encontrado y corregido durante el prototipado: el campo de la silla "
                  "usaba (strength*dx, -strength*dy) sin decaimiento por distancia, creciendo sin limite y "
                  "tapando las otras 6 singularidades (todo el poster salia dominado por una sola cruz); "
                  "corregido para decaer 1/r igual que fuente/sumidero/vortice. Resolucion 9000x12000 "
                  "(30x40in @300dpi) directo, sin version previa de menor resolucion. calidad JPEG 98 "
                  "elegida deliberadamente: quality=100 se pasaba el limite de 20MB de Etsy (27-30MB), "
                  "quality=98 da 14-16MB por archivo con margen de sobra. 3 variantes de color (Aurora "
                  "Teal, Ember Copper, Midnight Indigo). Bio de 'about the artist' reusada tal cual de "
                  "rossler_attractor_print para mantener voz consistente de esta sub-linea. Sin franja/logo "
                  "de marca en el archivo vendible (misma convencion que Rossler: es wall art para "
                  "enmarcar). 'images' usa *_preview.jpg (marca de agua diagonal tileada) y 'files' usa el "
                  "*_print.jpg limpio de resolucion completa. Subido como borrador el 2026-07-07, "
                  "listing_id=4533974490.",
    },

    "graph_paper": {
        "title":       "STEM Graph Paper Bundle | 8 Printable Grid Styles: Isometric, Hexagonal, Dot, Square, Cornell | US Letter + A4 Digital Download",
        "description": DESCRIPTIONS["graph_paper"],
        "price":       1.50,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("graph_paper", "previews", "graph_preview_1_hero.jpg"),
            p("graph_paper", "previews", "graph_preview_isometric.jpg"),
            p("graph_paper", "previews", "graph_preview_hexagonal.jpg"),
            p("graph_paper", "previews", "graph_preview_square.jpg"),
            p("graph_paper", "previews", "graph_preview_cornell.jpg"),
        ],
        "files": [
            p("graph_paper", "GraphPaper_Bundle.zip"),
        ],
        "tags": ["graph paper printable","isometric graph paper","hexagonal graph paper",
                 "printable grid paper","dot grid printable","cornell notes template",
                 "engineering paper","math paper printable","bullet journal paper",
                 "printable stationery","grid paper a4","us letter graph paper","stem gift"],
        "notes": "Digital ultra low-cost ($1.50), segundo producto de entrada (junto a chaos_palettes). "
                  "Nicho elegido via API: 'isometric graph paper printable' tiene solo ~73 listings pero "
                  "demanda fuerte (top $2.24 con 1.092 vistas/43 favs; $5.50 con 3.201 vistas); "
                  "'printable dot grid paper' ~2.859. El bundle multi-estilo valida ($1.50 'Square, Dot, "
                  "Isometric'). Construido con build_graph_paper.py (fitz directo, NO planner_framework: "
                  "el papel cuadriculado necesita paginas portrait limpias de borde a borde, no el layout "
                  "landscape con tabs del framework). 8 estilos: square 5mm (con lineas mayores c/5), "
                  "square 1/4in, dot 5mm, isometrico, triangular, hexagonal, Cornell, ruled. En AMBOS "
                  "tamanos (US Letter + A4) = 2 PDFs de 8 pags c/u. Isometrico/triangular/hexagonal "
                  "dibujados con familias de lineas paralelas clippeadas (Liang-Barsky) al rect de "
                  "contenido. Marca = firma diminuta y tenue en el margen inferior (el papel debe verse "
                  "limpio, no una franja). Deliverable: 1 zip con los 2 PDFs + README (imprimir al 100%, "
                  "no 'fit to page'). taxonomy 12476 (Planner Templates, printable stationery). 5 "
                  "imagenes: hero con las 8 grillas + full-page de iso/hex/square/cornell. Subido como "
                  "draft el 2026-07-07, listing_id=4534027247. Activacion manual pendiente.",
    },

    "fractal_palettes": {
        "title":       "Fractal Color Palettes for Procreate | 8 Swatch Packs, 240 Colors from Mandelbrot & Julia Sets | Generative Math Art Download",
        "description": DESCRIPTIONS["fractal_palettes"],
        "price":       1.99,
        "taxonomy_id": TAXONOMY["digital_drawing"],
        "images": [
            frac("previews", "palette_preview_1_hero.jpg"),
            frac("previews", "palette_preview_2_sources.jpg"),
            frac("previews", "palette_Ember_Mandelbrot.jpg"),
            frac("previews", "palette_Glacier_Julia.jpg"),
            frac("previews", "palette_Jade_Julia.jpg"),
            frac("previews", "palette_Amethyst_Julia.jpg"),
            frac("previews", "palette_Sunset_Julia.jpg"),
            frac("previews", "palette_Molten_Ship.jpg"),
            frac("previews", "palette_Peacock_Mandelbrot.jpg"),
            frac("previews", "palette_Rose_Gold_Julia.jpg"),
        ],
        "files": [
            frac("FractalDreams_Palettes.zip"),
        ],
        "tags": ["procreate palette","color palette","procreate color palette","fractal art",
                 "generative art","procreate swatches","math art","mandelbrot julia",
                 "color swatches","ipad art","fractal palette","digital download","artist gift"],
        "notes": "Segundo pack de paletas ultra low-cost ($1.99), hermano de chaos_palettes. Mismo motor "
                  "(build_palettes.extract_palette + brand.swatches_file) pero tema NUEVO y muy vendible: "
                  "fractales Mandelbrot/Julia/Burning Ship. build_fractal_palettes.py RENDERIZA 8 fractales "
                  "coloridos (escape-time suave + colormap propio por familia: ember/glacier/jade/amethyst/"
                  "sunset/molten/peacock/rosegold) y extrae 30 colores de cada uno -> 8 .swatches en 1 zip "
                  "+ HOW TO INSTALL.txt. 10 imagenes: hero (8 rampas) + grid de los 8 renders fuente + 1 "
                  "card por paleta. taxonomy 77 (digital_drawing, igual que chaos). Diferenciador vs miles "
                  "de packs de paletas: colores de fractales REALES computados, no stock/AI. Extensible a "
                  "mas fractales/zooms. Subido como draft el 2026-07-10, listing_id=4535716135. Activacion manual pendiente.",
    },

    "chaos_palettes": {
        "title":       "Chaos Theory Procreate Color Palettes | 8 Swatches Packs, 240 Colors from Real Strange Attractors | Generative Math Art Digital Download",
        "description": DESCRIPTIONS["chaos_palettes"],
        "price":       1.99,
        "taxonomy_id": TAXONOMY["digital_drawing"],
        "images": [
            pal("previews", "palette_preview_1_hero.jpg"),
            pal("previews", "palette_Voronoi_Garden.jpg"),
            pal("previews", "palette_Rossler_Amber.jpg"),
            pal("previews", "palette_Rossler_Rose.jpg"),
            pal("previews", "palette_Vector_Field_Teal.jpg"),
            pal("previews", "palette_Vector_Field_Copper.jpg"),
            pal("previews", "palette_Vector_Field_Indigo.jpg"),
            pal("previews", "palette_De_Jong_Ice.jpg"),
            pal("previews", "palette_Julia_Jade.jpg"),
        ],
        "files": [
            pal("ChaosTheory_Palettes.zip"),
        ],
        "tags": ["procreate palette","color palette","procreate color palette","digital art",
                 "generative art","procreate swatches","math art","strange attractor",
                 "color swatches","ipad art","abstract palette","digital download","artist gift"],
        "notes": "Digital ultra low-cost ($1.99) -- puerta de entrada para atraer trafico/reseñas. "
                  "Nicho elegido via API: 'procreate color palette' tiene demanda probada (top a $2.00 "
                  "con 2.635 vistas/31 favs) y nuestro angulo (paletas extraidas de atractores caoticos "
                  "reales) no lo ofrece nadie. Costo de produccion casi cero: brand.swatches_file() (el "
                  "escritor de .swatches ya existia). build_palettes.py extrae 8 paletas de 30 colores de "
                  "los renders reales (rossler amber/rose, vector field teal/copper/indigo, voronoi, "
                  "de jong, julia) por quantizacion adaptativa (median-cut) sobre las zonas con tinta, "
                  "filtrando pixeles grises de transicion (sat<0.18 y no-highlight) + anclas de "
                  "sombra/luz, para paletas vividas y no lavadas. Se descartaron Thomas y Phyllotaxis "
                  "(frames barrosos) a favor de De Jong (azul->cian) y Julia (teal->jade) para cubrir "
                  "azul y verde. Deliverable: 1 zip con los 8 .swatches + 'HOW TO INSTALL.txt'. taxonomy "
                  "77 (Art & Collectibles > Drawing & Illustration > Digital, no 'Digital Prints' porque "
                  "no es un print). 9 imagenes: hero con las 8 rampas + 1 card por paleta (grilla 6x5). "
                  "Subido como draft el 2026-07-07, listing_id=4534035590. Activacion manual pendiente.",
    },

    "phd_planner": {
        "title":       "PhD & Dissertation Planner | Undated Digital GoodNotes Notability iPad | Thesis Tracker, Literature Log, Defense Prep",
        "description": DESCRIPTIONS["phd_planner"],
        "price":       6.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "images": [
            p("phd_planner", "previews", "phd_preview_1_hero.jpg"),
            p("phd_planner", "previews", "phd_preview_2_included.jpg"),
            p("phd_planner", "previews", "phd_preview_3_roadmap.jpg"),
            p("phd_planner", "previews", "phd_preview_4_literature.jpg"),
            p("phd_planner", "previews", "phd_preview_5_weekly.jpg"),
            p("phd_planner", "previews", "phd_preview_6_defense.jpg"),
            p("phd_planner", "previews", "phd_preview_7_navigation.jpg"),
        ],
        "files": [
            p("phd_planner", "PhD_Dissertation_Planner.pdf"),
        ],
        "tags": ["phd planner","dissertation planner","thesis planner","academic planner",
                 "grad school planner","research planner","goodnotes planner","digital planner",
                 "undated planner","ipad planner","phd student gift","literature review",
                 "notability planner"],
        "notes": "Tipo 7 (STANDARDS.md, 'Planner digital'), nicho elegido tras investigar el mercado "
                  "via la API de Etsy (script _planner_research_tmp.py, borrado): 'phd planner digital' "
                  "tiene solo ~189 listings activos pero el top (Ultimate PhD Planner Pack, $6.50) "
                  "acumula 1.272 favs / ~39.7k vistas -> demanda real validada, poca oferta. En "
                  "contraste, otros nichos de baja competencia (data science planner ~61, engineering "
                  "student planner ~120, math teacher planner ~526) tienen favs/views casi nulos en su "
                  "top = baja competencia porque nadie compra, no oportunidad. Ninguno de los planners "
                  "actuales (life/stem_focus/stem_notebook/quantified_self) cubre el ciclo doctoral "
                  "especificamente. Construido con build_phd_planner.py sobre planner_framework."
                  "DigitalPlanner (mismo motor/estilo que quantified_self). 136 pags landscape 4:3, "
                  "100% hipervinculadas (dashboard + tabs laterales): roadmap Gantt plurianual (4), "
                  "chapter tracker (2), literature log 3 papers/pag (24 = 72 papers), advisor meeting "
                  "log (24), weekly research (52), monthly (12), deadlines (3), qualifying exam + "
                  "defense prep (2), notas dot-grid (12). 708 KB (muy bajo el limite de 20MB de Etsy). "
                  "Archivo = 1 PDF directo (formato aceptado). Gotcha PyMuPDF corregido: guiones largos "
                  "'—' en headers salian como '?' (base14 no tiene el glifo) -> reemplazados por '-'; "
                  "rating de relevancia '○○○' idem -> dibujado con draw_circle. Feature set derivado de "
                  "busqueda externa (Goodnotes 2026 + planners similares): navegacion hyperlinked, log "
                  "de reuniones con director, tracker de papers, progreso por capitulo, Gantt de hitos, "
                  "cuenta regresiva a defensa. Precio $6.99 (alineado al benchmark validado de $6.50 y "
                  "al rango actual del catalogo $2.99-8.99). Subido como draft el 2026-07-07, "
                  "listing_id=4533973003. Titulo: 2 gotchas de Etsy en el titulo -- max 140 chars, y '&' "
                  "solo se puede usar UNA vez (por eso 'Thesis Tracker, Literature Log, Defense Prep' con "
                  "comas en vez de '&'). Previews con build_phd_planner.py: 7 imagenes sobre navy con "
                  "branding (hero/dashboard, tarjeta 'que incluye' con las 9 secciones + conteos, y 5 "
                  "cards con 2 paginas reales grandes c/u: roadmap+chapters, literature+meetings, "
                  "weekly+monthly, deadlines+defense, mas navegacion/compatibilidad). Se subio primero "
                  "con 3 previews (2026-07-07) y se reemplazaron por estas 7 el mismo dia via script "
                  "temporal (subir nuevas ANTES de borrar viejas, por el scope sin listings_d; GET de "
                  "imagenes usa /listings/{id}/images SIN shop_id, el POST/DELETE si con shop_id). "
                  "Activacion manual pendiente desde el panel de Etsy.",
    },

    "life_planner": {
        "title":       "Undated Digital Planner GoodNotes Notability iPad | All-in-One Life Planner | 500+ Hyperlinked Pages | Daily Weekly Monthly + 50 Trackers",
        "description": DESCRIPTIONS["life_planner"],
        "price":       2.99,
        "taxonomy_id": TAXONOMY["planner_template"],
        "video": p("life_planner", "LifePlanner_promo.mp4"),
        "images": [
            p("life_planner", "previews", "life_preview_1_hero.jpg"),
            p("life_planner", "previews", "life_preview_2_daily.jpg"),
            p("life_planner", "previews", "life_preview_3_weekly.jpg"),
            p("life_planner", "previews", "life_preview_4_monthyear.jpg"),
            p("life_planner", "previews", "life_preview_5_trackers_a.jpg"),
            p("life_planner", "previews", "life_preview_6_trackers_b.jpg"),
            p("life_planner", "previews", "life_preview_7_navigation.jpg"),
            p("life_planner", "previews", "life_preview_8_included.jpg"),
            p("life_planner", "previews", "life_preview_9_compatibility.jpg"),
        ],
        "files": [
            p("life_planner", "MathRelaxing_Life_Planner.pdf"),
        ],
        "tags": ["digital planner","undated planner","goodnotes planner","ipad planner",
                 "notability planner","all in one planner","life planner","daily planner",
                 "weekly planner","budget tracker","habit tracker","self care planner",
                 "goodnotes template"],
        "notes": "All-in-one undated digital planner al estilo del best-seller de Etsy 4329390689 "
                  "(720 pags, €2, 281k vistas, 4390 favs, verificado via API de Etsy 2026-07-06). "
                  "Construido con life_planner/build_life_planner.py: 501 paginas 100% hipervinculadas "
                  "(dashboard + hub de año + Q1-Q4 + 12 meses + 52 semanas + 365 dias + 55 plantillas "
                  "en 5 categorias + notas), navegacion hub-and-spoke con pestañas laterales en cada "
                  "pagina. Landscape 4:3, identidad MathRelaxing (navy/oro/crema). 2.2 MB (bajo el "
                  "limite de Etsy). Archivo = 1 PDF (formato aceptado directamente, NO necesita .mov). "
                  "Previews con build_previews.py. Precio $2.99: estrategia de competir bajo (decision "
                  "del usuario), apenas arriba de los ~EUR2 del best-seller 4329390689 para entrar "
                  "agresivo en el nicho sin ir a fondo absoluto. Subido como DRAFT (id=4533446838, "
                  "2026-07-06) via API. Assets actualizados el mismo dia: 9 previews grandes/legibles "
                  "(build_previews.py) + video promo motion-graphics (build_promo_video.py, "
                  "LifePlanner_promo.mp4) + el PDF. Nota API: el token solo tiene scope listings_r/w/"
                  "shops_r (NO listings_d), asi que no se puede borrar un listing por API; para cambiar "
                  "imagenes hay que subir las nuevas ANTES de borrar las viejas (Etsy exige >=1 imagen "
                  "siempre). Activacion manual pendiente desde el panel de Etsy. Posible mejora futura: "
                  "6 temas de color (limite Etsy = 5 archivos) y set de stickers.",
    },

    "fractal_flora_pdf": {
        "title":       "Fractal Flora — Printable Coloring Book PDF | 50 Fractal & Botanical Line Art Designs",
        "description": DESCRIPTIONS["fractal_flora_pdf"],
        "price":       3.99,
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
        "tags": ["fractal coloring","botanical coloring","adult coloring book","printable coloring",
                 "math coloring book","line art coloring","nature coloring","coloring book pdf",
                 "mindful coloring","relaxing coloring","dragon curve art","julia set coloring",
                 "geometric coloring"],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar. Precio nivelado a $3.99 (igual que el resto de libros PDF).",
    },

    "sacred_geometry_pdf": {
        "title":       "Sacred Geometry — Color by Number Coloring Book PDF | 50 Low-Poly Mandala Designs",
        "description": DESCRIPTIONS["sacred_geometry_pdf"],
        "price":       3.99,
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
        "tags": ["sacred geometry","color by number","low poly coloring","mandala coloring",
                 "geometric coloring","adult coloring book","printable coloring","coloring book pdf",
                 "platonic solids art","flower of life art","meditative coloring","math color number",
                 "metatron cube art"],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar. Precio nivelado a $3.99 (igual que el resto de libros PDF).",
    },

    "hyperbolic_gardens_pdf": {
        "title":       "Hyperbolic Gardens — Printable Coloring Book PDF | 50 Escher-Style Tiling Designs",
        "description": DESCRIPTIONS["hyperbolic_gardens_pdf"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar cover.jpg + page samples con make_samples.py
        "files": [
            p("hyperbolic_gardens_digital.pdf"),
        ],
        "tags": ["hyperbolic coloring","escher coloring","tiling coloring","geometric coloring",
                 "adult coloring book","printable coloring","math coloring book","coloring book pdf",
                 "poincare disc art","infinite tiling art","mindful coloring","relaxing coloring",
                 "geometric art"],
        "notes": "PENDIENTE: faltan imágenes de preview. Ejecutar make_samples.py para HG. Precio nivelado a $3.99.",
    },

    "mathematical_tangle_art_pdf": {
        "title":       "Mathematical Tangle Art — Printable Coloring Book PDF | 50 Zentangle Math Designs",
        "description": DESCRIPTIONS["mathematical_tangle_art_pdf"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar previews
        "files": [
            p("mathematical_tangle_art_digital.pdf"),
        ],
        "tags": ["zentangle coloring","math tangle art","lissajous art","adult coloring book",
                 "printable coloring","math coloring book","coloring book pdf","geometric coloring",
                 "mindful coloring","relaxing coloring","spiral coloring","rose curve art",
                 "meditative coloring"],
        "notes": "PENDIENTE: faltan imágenes de preview. Precio nivelado a $3.99.",
    },

    "sacred_harmonics_pdf": {
        "title":       "Sacred Harmonics — Printable Coloring Book PDF | 50 Cymatics & Wave Geometry Designs",
        "description": DESCRIPTIONS["sacred_harmonics_pdf"],
        "price":       3.99,
        "taxonomy_id": TAXONOMY["coloring_book"],
        "images": [],   # ← PENDIENTE: generar previews
        "files": [
            p("sacred_harmonics_digital.pdf"),
        ],
        "tags": ["cymatics coloring","chladni figures","sacred harmonics","sound geometry art",
                 "adult coloring book","printable coloring","math coloring book","coloring book pdf",
                 "geometric coloring","mindful coloring","relaxing coloring","wave pattern art",
                 "resonance mandala"],
        "notes": "PENDIENTE: faltan imágenes de preview. Precio nivelado a $3.99.",
    },

    "neural_network_pdf": {
        "title":       "Neural Network & Tech Art — Printable Coloring Book PDF | 50 Cybernetic Circuit and AI Graph Designs",
        "description": DESCRIPTIONS["neural_network_pdf"],
        "price":       3.99,
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
        "tags": ["neural network art","tech coloring book","circuit coloring","ai art coloring",
                 "adult coloring book","printable coloring","coloring book pdf","geometric coloring",
                 "cyberpunk coloring","futuristic art","mindful coloring","relaxing coloring",
                 "graph theory art"],
        "notes": "Listo para publicar. Verificar taxonomy_id antes de activar. Precio nivelado a $3.99.",
    },

    "fractal_flora_ipad": {
        "title":       "Fractal Flora iPad Edition — Digital Coloring Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["fractal_flora_ipad"],
        "price":       5.99,
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
        "tags": ["fractal coloring","ipad coloring","goodnotes coloring","procreate coloring",
                 "digital coloring","ipad coloring book","botanical coloring","nature coloring ipad",
                 "geometric coloring","notability","procreate template","coloring book ipad",
                 "fractal art ipad"],
        "notes": "5 archivos exactos = límite Etsy. Listo para publicar. Precio nivelado a $5.99 (igual que el resto de bundles iPad).",
    },

    "sacred_geometry_ipad": {
        "title":       "Sacred Geometry iPad Edition — Color by Number Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["sacred_geometry_ipad"],
        "price":       5.99,
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
        "tags": ["color by number ipad","procreate coloring","goodnotes coloring","ipad coloring page",
                 "digital coloring","color by number","procreate template","sacred geometry",
                 "geometric coloring","math color number","coloring page ipad","procreate palette",
                 "mandala coloring"],
        "notes": "5 archivos exactos = límite Etsy. Precio nivelado a $5.99 (igual que el resto de bundles "
                  "iPad). Ya PUBLICADO (id=4529089106, activo, creado 2026-06-27) con precio viejo $11.99 "
                  "nunca sincronizado — corregido a $5.99 via API el 2026-07-06. En esa revisión: solo "
                  "2 vistas / 0 favoritos desde creación (9 días) — el problema real de este listing es "
                  "visibilidad/tráfico, no precio ni conversión. Bug de API descubierto y corregido: "
                  "update_listing(price=...) NO actualiza el precio (Etsy ignora el campo en el PATCH "
                  "del listing); el precio vive en /listings/{id}/inventory y hay que escribirlo con "
                  "EtsyManager.update_price() (nuevo método, JSON real + limpieza de campos read-only).",
    },

    "thomas_attractor": {
        "title":       "Thomas Attractor — Seamless Loop Animation | 1080x1080 60fps Mathematical Art",
        "description": DESCRIPTIONS["thomas_attractor"],
        "price":       4.99,
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
        "tags": ["attractor animation","chaos theory art","fractal wallpaper","seamless loop",
                 "mathematical art","attractor art","math wallpaper","digital wallpaper",
                 "generative art","abstract animation","math art","screensaver loop",
                 "chaotic system art"],
        "notes": "Ya PUBLICADO (id=4528956373, activo). Video preview marcado añadido 2026-06-29. Archivo=mp4 limpio. "
                  "Tags añadidos solo al registro local; no se sincronizan automáticamente con el listing ya activo en Etsy.",
    },

    "de_jong_attractor": {
        "title":       "De Jong Attractor — Seamless Loop Animation | 1080x1080 30fps Mathematical Art",
        "description": DESCRIPTIONS["de_jong_attractor"],
        "price":       4.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        # OJO animaciones: el video del listing = preview 540p CON marca de agua
        # (el producto ES un video → si fuera el limpio, se podría robar desde el preview).
        # El archivo de descarga ('files') sí es el MP4 limpio 1080p.
        "video": p("dejong_loop", "DeJongAttractor_preview.mp4"),
        "images": [
            p("dejong_loop", "previews", "dejong_preview_1_hero.jpg"),
            p("dejong_loop", "previews", "dejong_preview_2_specs.jpg"),
            p("dejong_loop", "previews", "dejong_preview_3_loop.jpg"),
        ],
        "files": [
            p("dejong_loop", "DeJongAttractor_loop.mov"),   # .mov, no .mp4: ver nota
        ],
        "tags": ["de jong attractor","chaos theory art","fractal wallpaper","seamless loop",
                 "mathematical art","neon math art","math wallpaper","digital wallpaper",
                 "generative art","abstract animation","math art","screensaver loop",
                 "cyan wallpaper"],
        "notes": "Cuarto de la serie de animaciones seamless (Thomas/Julia/Voronoi Cell/De Jong), "
                  "hueco documentado en STANDARDS.md nunca antes construido. Nicho 'de jong attractor' "
                  "sin competencia dedicada en Etsy (research web 2026-07-05). Paleta cian/indigo "
                  "deliberadamente distinta a Thomas (oro/aqua) para no canibalizar ventas. "
                  "Generado con generate_dejong_loop.py (atractor caotico de Peter de Jong, "
                  "mutacion continua via trayectoria circular en el espacio de parametros a/c). "
                  "IMPORTANTE: el archivo de descarga es .mov, no .mp4 — la app de Etsy (subida manual) "
                  "no acepta .mp4 en 'Archivos digitales' (visto 2026-07-05), solo .mov/.mpeg para video. "
                  "DeJongAttractor_loop.mov es el mismo .mp4 remuxeado sin recodificar (ffmpeg -c copy), "
                  "cero perdida de calidad. Listo para publicar como borrador.",
    },

    "phyllotaxis_bloom": {
        "title":       "Phyllotaxis Bloom — Seamless Loop Animation | Golden Particle Field | 1600x1600 60fps Mathematical Art",
        "description": DESCRIPTIONS["phyllotaxis_bloom"],
        "price":       4.99,
        "taxonomy_id": TAXONOMY["digital_art"],
        # OJO animaciones: el video del listing = preview 540p CON marca de agua.
        # El archivo de descarga ('files') es .mov (ver nota) del limpio 1080p.
        "video": p("phyllotaxis_loop", "PhyllotaxisBloom_preview.mp4"),
        "images": [
            p("phyllotaxis_loop", "previews", "phyllotaxis_preview_1_hero.jpg"),
            p("phyllotaxis_loop", "previews", "phyllotaxis_preview_2_specs.jpg"),
            p("phyllotaxis_loop", "previews", "phyllotaxis_preview_3_loop.jpg"),
        ],
        "files": [
            p("phyllotaxis_loop", "PhyllotaxisBloom_loop.mov"),   # .mov, no .mp4: ver nota
        ],
        "tags": ["phyllotaxis art","golden ratio art","particle animation","seamless loop",
                 "mathematical art","stardust wallpaper","math wallpaper","digital wallpaper",
                 "generative art","abstract animation","math art","screensaver loop",
                 "fibonacci spiral art"],
        "notes": "Quinto de la serie de animaciones seamless. Nacio de pedir 'algo similar' a un "
                  "template generico de particle logo reveal (Pinterest) — investigue esa categoria "
                  "en Etsy: esta saturada Y es mayormente un SERVICIO personalizado (subes tu logo, "
                  "te lo entregan editado), no encaja con el modelo de instant-download fijo de la "
                  "tienda. En vez de copiarlo, redirigi la tecnica visual (particulas) a lo que ya "
                  "funciona: un wallpaper en loop infinito, sin personalizacion. "
                  "Iterado 3 veces a pedido del usuario ('mas dinamismo, mas particulas'): "
                  "v1=700 particulas/1080p/30fps solo respirando+titilando (muy plano) -> "
                  "v2=2200 particulas + rotacion global de 1 vuelta (mas vivo) -> "
                  "v3=6000 particulas + rotacion DIFERENCIAL (centro hasta 3 vueltas mas que el "
                  "borde, cizallamiento tipo galaxia espiral) -> v4 (final)=15000 particulas, "
                  "1600x1600, 60fps. Particulas ubicadas por angulo dorado (misma regla que las "
                  "semillas de Voronoi Gardens); todas las frecuencias de movimiento (respiracion, "
                  "titileo, rotacion global+diferencial, balanceo) son ENTERAS respecto al total de "
                  "frames -> loop perfecto sin importar cuantos terminos se sumen. Paleta oro/crema "
                  "pura (identidad central de marca), distinta de Thomas (oro+aqua, atractor) y "
                  "De Jong (cian, atractor) — esta es la unica basada en un campo de particulas, no "
                  "en una trayectoria caotica. Generado con generate_phyllotaxis_loop.py. "
                  "IMPORTANTE: a 1600x1600/60fps/8s el mp4 con crf=18 pesaba 30MB (excede el limite "
                  "de 20MB de Etsy para 'Archivos digitales'); se subio crf a 23 -> 18.1MB, sin "
                  "perdida de calidad visible. Archivo de descarga en .mov (ver nota de De Jong "
                  "sobre compatibilidad de Etsy). Listo para publicar como borrador.",
    },

    "voronoi_gardens_pdf": {
        "title":       "Voronoi Gardens — Printable Coloring Book PDF | 50 Mandala & Cell Tessellation Designs",
        "description": DESCRIPTIONS["voronoi_gardens_pdf"],
        "price":       3.99,
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
        "price":       9.99,
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
        "price":       5.99,
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
        "price":       8.99,
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
        "price":       4.99,
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
        "price":       3.99,
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
                  "Activacion manual pendiente desde el panel de Etsy. Precio nivelado a $3.99: el draft "
                  "ya creado en Etsy tiene el precio viejo, hay que actualizarlo manualmente o resubirlo.",
    },

    "islamic_geometry_ipad": {
        "title":       "Islamic Star Geometry iPad Edition — Color by Number Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["islamic_geometry_ipad"],
        "price":       5.99,
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
                  "Activacion manual pendiente desde el panel de Etsy. Precio nivelado a $5.99.",
    },

    "celtic_knot_pdf": {
        "title":       "Celtic Knot Mathematics — Printable Coloring Book PDF | 50 Interlace & Knotwork Designs",
        "description": DESCRIPTIONS["celtic_knot_pdf"],
        "price":       3.99,
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
        "notes": "Generado con generate_celtic_knots.py (algoritmo de grid propio). Listo para publicar como borrador. Precio nivelado a $3.99.",
    },

    "celtic_knot_ipad": {
        "title":       "Celtic Knot iPad Edition — Digital Coloring Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["celtic_knot_ipad"],
        "price":       5.99,
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
        "notes": "Generado con build_celtic_ipad.py. 5 archivos exactos = limite Etsy. Bundle iPad de los 50 nudos tejidos. Precio nivelado a $5.99.",
    },

    "voronoi_cell_garden": {
        "title":       "Voronoi Cell Garden Seamless Loop | Organic Mosaic Animation | Math Art Digital Download | 30fps MP4 | Ambient Stained Glass Screensaver",
        "description": DESCRIPTIONS["voronoi_cell_garden"],
        "price":       4.99,
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
        "price":       7.99,
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
        "tags": ["quantified self","data planner","agile sprint planner","programmer gift","engineer gift","habit tracker","github heatmap","digital planner","goodnotes planner","ipad planner","dark mode planner","bullet journal","stem notebook"],
        "notes": "Generado con build_quantified_self.py",
    },

    # ── Libros físicos (Lulu POD) — Tipo 8, ver STANDARDS.md ──────────────────
    "hyperbolic_gardens_physical": {
        "title":       "Hyperbolic Gardens Coloring Book – PRINTED Physical Edition | 50 Escher-Style Tessellation Designs | Perfect Bound",
        "description": DESCRIPTIONS["hyperbolic_gardens_physical"],
        "price":       18.99,
        "taxonomy_id": TAXONOMY["coloring_book_physical"],
        "images": [
            lulu("hyperbolic_gardens_cover.png"),
            lulu("listing_photos", "hyperbolic_sample1.jpg"),
            lulu("listing_photos", "hyperbolic_sample2.jpg"),
            lulu("listing_photos", "hyperbolic_sample3.jpg"),
        ],
        "files": [],
        "shipping_profile_id": SHIPPING_PROFILE_LULU_BOOKS,
        "readiness_state_id": READINESS_STATE_LULU_BOOKS,
        "return_policy_id": RETURN_POLICY_ID,
        "tags": ["hyperbolic geometry","tessellation art","escher inspired","printed book","adult coloring book","math coloring book","perfect bound book","stem gift","relaxation gift","geometric coloring","mandala coloring","math teacher gift","physical book gift"],
        "notes": "Tipo 8 (libro fisico POD via Lulu, ver STANDARDS.md). Generado con lulu_books/generators/gen_hyperbolic_book.py + gen_hyperbolic_cover.py. 104 paginas (50 disenos + 50 blancas + frontmatter, ver commit de blank-after-each). Precio $18.99 + shipping profile Lulu Publishing ($5.99 EE.UU. / $9.99 resto via USPS Media Mail / Priority Intl). Sin archivo digital: se cumple imprimiendo bajo demanda con Lulu al recibir el pedido (flujo manual por ahora, ver lulu_api/lulu_publish.py). Subido como borrador el 2026-07-07, listing_id=4533722112.",
    },

    "fractal_flora_physical": {
        "title":       "Fractal Flora Coloring Book – PRINTED Physical Edition | 50 Fractal & Botanical Designs | Perfect Bound",
        "description": DESCRIPTIONS["fractal_flora_physical"],
        "price":       18.99,
        "taxonomy_id": TAXONOMY["coloring_book_physical"],
        "images": [
            lulu("fractal_flora_cover.png"),
            lulu("listing_photos", "fractal_flora_sample1.jpg"),
            lulu("listing_photos", "fractal_flora_sample2.jpg"),
            lulu("listing_photos", "fractal_flora_sample3.jpg"),
        ],
        "files": [],
        "shipping_profile_id": SHIPPING_PROFILE_LULU_BOOKS,
        "readiness_state_id": READINESS_STATE_LULU_BOOKS,
        "return_policy_id": RETURN_POLICY_ID,
        "tags": ["fractal coloring","botanical art book","algorithmic art","printed book","adult coloring book","math coloring book","perfect bound book","stem gift","nature coloring","relaxation gift","math teacher gift","physical book gift","dragon curve art"],
        "notes": "Tipo 8 (libro fisico POD via Lulu). Generado con lulu_books/generators/gen_l_systems_book.py + gen_l_systems_cover.py. 104 paginas. Precio $18.99 + shipping profile Lulu Publishing. Subido como borrador el 2026-07-07, listing_id=4533708985.",
    },

    "sacred_math_physical": {
        "title":       "Sacred Geometry & Topology Coloring Book – 3D Color-by-Number | PRINTED Physical Edition | 50 Designs",
        "description": DESCRIPTIONS["sacred_math_physical"],
        "price":       18.99,
        "taxonomy_id": TAXONOMY["coloring_book_physical"],
        "images": [
            lulu("sacred_math_cover.png"),
            lulu("listing_photos", "sacred_math_sample1.jpg"),
            lulu("listing_photos", "sacred_math_sample2.jpg"),
            lulu("listing_photos", "sacred_math_sample3.jpg"),
        ],
        "files": [],
        "shipping_profile_id": SHIPPING_PROFILE_LULU_BOOKS,
        "readiness_state_id": READINESS_STATE_LULU_BOOKS,
        "return_policy_id": RETURN_POLICY_ID,
        "tags": ["3d coloring book","color by number","sacred geometry","topology art","printed book","adult coloring book","math coloring book","perfect bound book","stem gift","geometry gift","math teacher gift","physical book gift","torus mobius art"],
        "notes": "Tipo 8 (libro fisico POD via Lulu). Generado con lulu_books/generators/gen_sacred_math_book.py + gen_sacred_math_cover.py (portada nueva, ver commit). 108 paginas. Distinto del 'sacred_geometry_pdf' ya existente (ese es low-poly mandala 2D; este es proyeccion 3D color-by-number). Precio $18.99 + shipping profile Lulu Publishing. Nota de calidad: el renderer de mallas 3D tiene un defecto residual conocido (ver fix commits) -- la mayoria de paginas quedan limpias tras la curacion multi-angulo pero algunas conservan pequenas astillas oscuras menores; las 3 fotos de muestra elegidas para el listing estan entre las mas limpias. Subido como borrador el 2026-07-07, listing_id=4533709025.",
    },

    "voronoi_gardens_physical": {
        "title":       "Voronoi Gardens Coloring Book – PRINTED Physical Edition | 50 Mandala & Cell Tessellation Designs | Perfect Bound",
        "description": DESCRIPTIONS["voronoi_gardens_physical"],
        "price":       18.99,
        "taxonomy_id": TAXONOMY["coloring_book_physical"],
        "images": [
            lulu("voronoi_gardens_cover.png"),
            lulu("listing_photos", "voronoi_sample1.jpg"),
            lulu("listing_photos", "voronoi_sample2.jpg"),
            lulu("listing_photos", "voronoi_sample3.jpg"),
        ],
        "files": [],
        "shipping_profile_id": SHIPPING_PROFILE_LULU_BOOKS,
        "readiness_state_id": READINESS_STATE_LULU_BOOKS,
        "return_policy_id": RETURN_POLICY_ID,
        "tags": ["voronoi coloring","cell tessellation","mandala coloring","printed book","adult coloring book","math coloring book","perfect bound book","stem gift","phyllotaxis art","relaxation gift","math teacher gift","physical book gift","organic mandala"],
        "notes": "Tipo 8 (libro fisico POD via Lulu). Generado con lulu_books/generators/make_voronoi_book.py (comando 'interior' con blank_after_each=True -> *_interior_print.pdf; portada reutiliza el cover.pdf ya existente del producto digital, rasterizado a PNG). 104 paginas. Precio $18.99 + shipping profile Lulu Publishing. Subido como borrador el 2026-07-07, listing_id=4533709063.",
    },

    "spiral_tilings_ipad": {
        "title":       "Interactive Color By Number Spiral Tilings — iPad Safari SVG App | 50 Math Mandala Radial Designs",
        "description": DESCRIPTIONS["spiral_tilings_ipad"],
        "price":       9.99,
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

    "sacred_geometry_ipad_svg": {
        "title":       "Interactive Color By Number Sacred Geometry — iPad Safari SVG App | 50 Low Poly 3D Topology Designs",
        "description": DESCRIPTIONS["sacred_geometry_ipad_svg"],
        "price":       9.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": p("ipad_sacred_cbn_svg", "SacredGeometry_SVG_promo.mp4"),
        "images": [
            p("ipad_sacred_cbn_svg", "previews", "ipad_svg_preview_1_hero.jpg"),
            p("ipad_sacred_cbn_svg", "previews", "ipad_svg_preview_2_features.jpg"),
            p("ipad_sacred_cbn_svg", "previews", "ipad_svg_preview_3_included.jpg"),
        ],
        "files": [
            p("ipad_sacred_cbn_svg", "SacredGeometry_CBN_Interactive.zip"),
            p("ipad_sacred_cbn_svg", "How_to_Use_Interactive_CBN.pdf"),
        ],
        "tags": ["ipad coloring book","color by number","sacred geometry","procreate coloring","3d coloring","low poly art","math art","topology art","goodnotes coloring","torus mobius","digital download","relaxing coloring","adhd coloring"],
        "notes": "MIGRACION del listing INACTIVO 'Sacred Geometry Color by Number iPad Pages | 50 Low Poly "
                  "Procreate Designs' (listing_id=4529089106, estado edit/inactive, $5.99, PNG+PDF "
                  "GoodNotes/Procreate) al NUEVO formato SVG interactivo Safari (igual que spiral_tilings_ipad "
                  "y voronoi SVG). El sacred original era 'Low Poly 3D' (superficies "
                  "topologicas facetadas + color-by-number sombreado). PRIMERA version SVG fueron mandalas "
                  "2D planas -> el usuario pidio recuperar la SENSACION 3D. build_sacred_ipad_svg.py ahora "
                  "reutiliza las mallas 3D reales de lulu_books/core/math_meshes.py (gen_torus, "
                  "gen_sphere_bumpy, gen_mobius): 22 toros + 22 gemas facetadas + 6 Mobius. Cada cara se "
                  "rota a camara, se proyecta ortografico, se hace BACK-FACE CULLING (una sola capa limpia "
                  "para el SVG) y se sombrea intensity=normal.luz -> indice en paleta 8 tonos navy->oro->crema "
                  "ordenada por luminosidad (colorear 1->8 = sombra->brillo revela el 3D). Filtro de slivers "
                  "para quitar spikes de silueta/polos. Usa el framework template_ipad_svg_bundle "
                  "-> 50 HTML interactivos + ZIP (0.5MB) + How_to_Use PDF. Previews/video con "
                  "build_sacred_svg_previews.py. Verificado en Chromium: render SVG + tap-to-fill + zoom OK. "
                  "Precio $9.99 (como spiral SVG; sube desde $5.99 del PNG original por mayor valor "
                  "interactivo). Actualizar el listing 4529089106 en su lugar (mantener draft/inactive para "
                  "activacion manual).",
    },

    "spiral_tilings_pdf": {
        "title":       "Spiral Tilings — Printable Coloring Book PDF | 50 Math & Mandala Radial Designs",
        "description": DESCRIPTIONS["spiral_tilings_pdf"],
        "price":       6.99,
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
        shipping_profile_id=prod.get("shipping_profile_id"),
        readiness_state_id=prod.get("readiness_state_id"),
        return_policy_id=prod.get("return_policy_id"),
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
