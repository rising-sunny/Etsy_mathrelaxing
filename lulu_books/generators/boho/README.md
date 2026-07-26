# Boho Botanical — abstract wall art, generated with math

A mainstream **boho / mid-century** wall-art line, generated entirely from code:
parametric leaf curves, curved branches (Bézier), concentric arches, discs and a
diamond, composed into coordinated **"Set of 3"** printables. Palette-driven, so
new colorways are just a dict entry.

## Files
| File | What it does |
|---|---|
| `generate_boho.py` | The generator. Primitives (`leaf`, `branch`, `arches`, `disc`, `ring`, `diamond`) + 3 panel compositions. Renders print-ready **2000×3000 (2:3)** PNG panels per palette + a preview triptych. Palettes live in `PALETTES`. |
| `build_boho_package.py` | Buyer deliverable + Etsy images: per-palette ZIP (3 PNGs + size-guide PDF), framed **wall mockup**, 3-up grid, "what you get". |
| `create_boho_listing.py` | DRAFT Etsy listing for the **Blue & Cream + Terracotta** combo (Palette variation, both colorways in the download, $9.99). |
| `boho_publish_singles.py` | Batch: one DRAFT listing **per palette** (sage/mustard/noir/blush) — ZIP + 5 images + color-keyword SEO title/tags. |

## Palettes
`blue` · `terra` · `sage` · `mustard` · `noir` (black & cream) · `blush`.
Add a palette = one line in `PALETTES` (`bg`, `fill`, `fill2`, `ink`) + a
`WALL_TONE` entry.

## Build / publish
```
python generate_boho.py          # -> {pal}_panel{1..3}.png + {pal}_triptych.jpg
python build_boho_package.py     # -> ZIPs + listing/*.jpg (blue+terra combo)
python create_boho_listing.py    # -> DRAFT combo listing (needs etsy_token.json at repo root)
python boho_publish_singles.py   # -> DRAFT listing per new palette
```

Generated output (`*_panel*.png`, triptychs, `deliverable/`, `listing*/`, `*.zip`)
is gitignored. Fonts come from `lulu_books/assets/fonts`.

## Etsy drafts created (2026-07-26, all state=draft, $9.99, digital)
- Blue & Cream + Terracotta (variants): `4544472523`
- Sage Green: `4544491366` · Mustard/Ochre: `4544491444`
- Black & Cream: `4544475669` · Blush Pink: `4544475777`
