# The Mathematics of Beauty — math gallery art book

A premium 8.5×8.5″ hardcover coffee-table book: ~38 plates, each pairing a
beautiful mathematical graphic (right, full-bleed) with its elegant equation
and a short caption (left), generated directly from the mathematics.

## Files

| File | What it does |
|---|---|
| `mini_book.py` | Shared toolkit: page geometry (8.5″ trim + 0.125″ bleed, 300 DPI), `text_page`, `pad_bleed`, palette, fonts, and a 10-plate **mini** book (`python mini_book.py`) for quick tests. Other scripts import its helpers. |
| `plate_library.py` | ~38 graphic renderers (attractors, fractals, curves, waves & fields, tilings) + a `contact_sheet()` to eyeball them all. |
| `full_book.py` | Builds the **full interior PDF** (88 pp: title, foreword, section dividers, 38 plates, colophon) + the front cover. All plate metadata (section, title, equations, description) lives here. |
| `build_cover_wrap.py` | Builds the **hardcover full-wrap cover** (back + spine + front) at Lulu's exact dimensions, with the ∞ logo. |
| `lulu_ops.py` | Lulu API helpers (no fitz): `dims` (cover-dimensions / spine) and `validate` (R2 upload + validate-interior). Read-only — never places an order. |

## Build

```
python full_book.py          # -> fullbook/interior.pdf + fullbook/cover_front.png
python build_cover_wrap.py   # -> fullbook/cover_wrap.pdf  (hardcover wrap)
```

Assets used: `lulu_books/assets/fonts` (Cinzel, Raleway), `lulu_books/assets/img/logo.png`,
and the geometric tiling prints under `wallart_set/out/geo/mono/prints`.

## Lulu product

- **SKU:** `0850X0850.FC.PRE.CW.080CW444.MXX` — 8.5×8.5, full colour, premium,
  hardcover case-wrap, 80# coated white, matte cover.
- **Wrap (88 pp):** 1386×738 pt (19.25×10.25″); spine 0.5″; wrap margin 0.875″.
- **Validation:** the 88-page interior was validated against Lulu
  (`status: NORMALIZED`, no errors).

```
python lulu_ops.py dims 0850X0850.FC.PRE.CW.080CW444.MXX 88
python lulu_ops.py validate fullbook/interior.pdf 0850X0850.FC.PRE.CW.080CW444.MXX
```

Credentials come from `lulu_books/.env` (gitignored). `cover-dimensions` and
`validate-interior` cost nothing; **creating a print job would cost money** and
is intentionally not automated here.
