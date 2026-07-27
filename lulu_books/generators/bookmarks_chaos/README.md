# Strange Attractors — printable bookmarks (set 2)

A second set of **10 printable bookmark designs** (2×6 in) in the MathRelaxing
identity (black/cream + gold, Cinzel/Raleway, CM mathtext, ∞ mark), themed on
**chaos theory / strange attractors** — a sibling to the first set (*The
Mathematics of Beauty*, curves).

Designs: Lorenz · Clifford · De Jong · Rössler · Thomas · Aizawa · Halvorsen ·
Hopalong · Svensson · Chen.

## Files
| File | What it does |
|---|---|
| `generate_chaos.py` | Renders the 10 bookmarks by **reusing `../bookmarks/generate_bookmarks.build_one`** (same 2.25×6.25 in @ 300 DPI engine) with attractor art (`scipy.odeint` flows + iterated 2D maps as coloured point clouds). Output → `out/`. |
| `package_chaos.py` | Builds the buyer deliverable + Etsy listing images: individual PNGs, print-ready sheets (US Letter + A4 with cut marks), a print guide PDF, `MathRelaxing_Strange_Attractors_Bookmarks.zip`, and `listing/*.jpg` (5 images). |

## Build
```
python generate_chaos.py    # -> out/bm_*.png + out/contact.jpg
python package_chaos.py     # -> deliverable/, listing/, the ZIP
```

## Etsy
Digital download, instant, **$5.50** (same as set 1). Listed via the standard
`products_catalog.py` flow (slug `attractor_bookmarks`): 5 images + the ZIP.

`out/`, `deliverable/`, `listing/` and the ZIP are generated and gitignored.
