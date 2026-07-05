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
}

# ── Catálogo de productos ─────────────────────────────────────────────────────
PRODUCTS = {

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
        "notes": "5 archivos exactos = límite Etsy. Listo para publicar. Precio nivelado a $5.99 (igual que el resto de bundles iPad).",
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
            p("dejong_loop", "DeJongAttractor_loop.mp4"),
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
                  "Listo para publicar como borrador.",
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
        "title":       "Voronoi Gardens iPad Edition — Digital Coloring Bundle | GoodNotes Notability Procreate",
        "description": DESCRIPTIONS["voronoi_gardens_ipad"],
        "price":       5.99,
        "taxonomy_id": TAXONOMY["ipad_coloring"],
        "video": p("ipad_voronoi", "VoronoiGardens_iPad_promo.mp4"),
        "images": [
            p("ipad_voronoi", "previews", "ipad_preview_1_hero.jpg"),
            p("ipad_voronoi", "previews", "ipad_preview_2_included.jpg"),
            p("ipad_voronoi", "previews", "ipad_preview_3_twoways.jpg"),
        ],
        "files": [
            p("ipad_voronoi", "VoronoiGardens_iPad_GoodNotes.pdf"),
            p("ipad_voronoi", "VoronoiGardens_Procreate_PNG_part1.zip"),
            p("ipad_voronoi", "VoronoiGardens_Procreate_PNG_part2.zip"),
            p("ipad_voronoi", "VoronoiGardens.swatches"),
            p("ipad_voronoi", "How_to_use_on_iPad.pdf"),
        ],
        "tags": ["voronoi coloring","ipad coloring","goodnotes coloring","procreate coloring",
                 "digital coloring","ipad coloring book","mandala coloring","math coloring",
                 "geometric coloring","notability","procreate template","coloring book ipad","voronoi mandala"],
        "notes": "5 archivos exactos = límite Etsy. Bundle iPad nicho nuevo.",
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
