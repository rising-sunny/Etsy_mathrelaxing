# The Mathematics of Beauty — bookmarks (digital + POD)

A set of **10 exclusive vertical bookmark designs** in the same identity as the
art book: black/cream backgrounds, gold accents, Cinzel/Raleway type,
Computer-Modern mathtext, and the ∞ mark as the only signature. Each design is
generated from its own equation — not a crop of the book plates.

Designs: Golden Spiral · Rose Curve · Euler's Identity · Lissajous · Harmonograph
· Butterfly Curve · Lemniscate · Heart Curve · Phyllotaxis · Standing Wave.

## Two product lines

| Line | Format | How it sells |
|---|---|---|
| **Printable set** | 2×6 in trim (+ bleed → 2.25×6.25 @ 300 DPI) | Digital Etsy download (ZIP of 10) |
| **POD aluminum** | 2×7 in, 450×1575 px (Printify bp 765) | Physical metal bookmark, one design per listing |

The POD ratio is taller/narrower than the printable set — always **re-render**
with `generate_pod_bookmark.py`, never just rescale. Keep key art away from the
top ~10% (U-shaped page slot on the aluminum blank).

## Files
| File | What it does |
|---|---|
| `generate_bookmarks.py` | Renders the 10 printable bookmarks to `out/`, plus a contact sheet. |
| `generate_pod_bookmark.py` | Renders one design at Printify size → `out/pod/pod_bm_<key>.png`. |
| `build_package.py` | Buyer ZIP + Etsy listing images for the **digital** set. |
| `create_bookmark_listing.py` | DRAFT Etsy listing for the digital set ($5.50). |
| `../../../printify/create_pod_bookmark.py` | Upload + create Printify product; optional `--publish` to Etsy draft. |

## Build — digital set
```
python generate_bookmarks.py    # -> out/bm_*.png + out/contact.jpg
python build_package.py         # -> deliverable/, listing/, MathRelaxing_Bookmarks.zip
python create_bookmark_listing.py   # -> DRAFT Etsy listing (needs etsy_token.json)
```

## Build — POD line (one design per listing)
```
# from printify/
python create_pod_bookmark.py --design golden --publish
python create_pod_bookmark.py --all --publish --price 1799   # full line
python create_pod_bookmark.py --all --skip golden --publish  # only missing
```

Printify blueprint **765** has a **single** physical variant (One size / White),
so each design is a **sibling product + Etsy draft**, not options on one SKU.
Cost ~$5.99 + US ship ~$5.89 · retail **$17.99**. Ids: `printify/pod_bookmark_created.json`.

### Mockups (3 per design)
API publish only attaches the **front** camera. Two lifestyle mockups also exist
(in-book + table scene). Download them with:

```
cd printify
python download_bookmark_mockups.py              # -> bookmark_listing_mockups/<design>/*.jpg
python download_bookmark_mockups.py --push-etsy  # needs etsy_token.json; uploads ranks 1–3
```

Or in Printify UI: product → **View all mockups** → enable lifestyle shots → re-publish images.

`out/`, `deliverable/`, `listing/` and the ZIP are generated and gitignored.

| Product | listing_id | printify_id |
|---|---|---|
| Digital set of 10 | `4544427938` | — ($5.50 download) |
| POD Golden Spiral | `4546605138` | `6a6abfaad3560ab0280a4903` |
| POD Rose Curve | `4546593319` | `6a6ac098a2ff7e986a0ff9ae` |
| POD Euler Identity | `4546593459` | `6a6ac0a86e4c98e0ee061c31` |
| POD Lissajous | `4546593573` | `6a6ac0bad3560ab0280a4a5c` |
| POD Harmonograph | `4546606580` | `6a6ac0cad3560ab0280a4a7d` |
| POD Butterfly Curve | `4546593783` | `6a6ac0da097240048f0cd8ac` |
| POD Lemniscate | `4546593817` | `6a6ac0e9097240048f0cd8c4` |
| POD Heart Curve | `4546606826` | `6a6ac0f9fcb6af0cc70143c4` |
| POD Phyllotaxis | `4546607004` | `6a6ac109a2ff7e986a0ffa9b` |
| POD Standing Wave | `4546607100` | `6a6ac119a55df4f3cd0db3b8` |
