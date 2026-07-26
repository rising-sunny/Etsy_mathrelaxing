# The Mathematics of Beauty — printable bookmarks

A set of **10 exclusive vertical bookmark designs** (2×6 in) in the same identity
as the art book: black/cream backgrounds, gold accents, Cinzel/Raleway type,
Computer-Modern mathtext, and the ∞ mark as the only signature. Each design is
generated from its own equation — not a crop of the book plates.

Designs: Golden Spiral · Rose Curve · Euler's Identity · Lissajous · Harmonograph
· Butterfly Curve · Lemniscate · Heart Curve · Phyllotaxis · Standing Wave.

## Files
| File | What it does |
|---|---|
| `generate_bookmarks.py` | Renders the 10 bookmarks (2.25×6.25 in w/ bleed, 300 DPI) to `out/`, plus a contact sheet. Reuses palette/fonts/`_grad_line` from `../math_gallery/mini_book.py`. |
| `build_package.py` | Builds the buyer deliverable + Etsy listing images: individual PNGs, print-ready sheets (US Letter + A4 with cut marks), a styled print guide PDF, the `MathRelaxing_Bookmarks.zip`, and `listing/*.jpg`. |
| `create_bookmark_listing.py` | Creates the DRAFT Etsy listing (digital, instant download, $5.50). Uploads the ZIP + images. Draft only — the owner activates. |

## Build
```
python generate_bookmarks.py    # -> out/bm_*.png + out/contact.jpg
python build_package.py         # -> deliverable/, listing/, MathRelaxing_Bookmarks.zip
python create_bookmark_listing.py   # -> DRAFT Etsy listing (needs etsy_token.json at repo root)
```

`out/`, `deliverable/`, `listing/` and the ZIP are generated and gitignored.
The Etsy draft first created here is `listing_id=4544427938`.
