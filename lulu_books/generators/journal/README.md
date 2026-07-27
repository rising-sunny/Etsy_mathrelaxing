# Math notebooks — matte hardcover journals (POD)

A family of matte hardcover **notebooks** (to write in) in the art book's
identity, made via Printify POD → Etsy. Each cover pairs a math-generated hero
with the black + gold title and a clear **"A NOTEBOOK"** label so buyers don't
confuse them with the art book. New titles are siblings of the first generator
(same layout, different theme + hero art).

## Files
| File | Theme | What it does |
|---|---|---|
| `generate_journal_cover.py` | *The Mathematics of Beauty* — chaos (Lorenz) | Full-wrap cover PNG (4065×2850) → `out/journal_wrap.png` + `journal_front.png` preview. |
| `generate_waves_cover.py` | *Waves & Harmony* — physics of waves | Same layout; interference hero on the front, Lissajous / harmonograph / Chladni plates on the back → `out/waves_wrap.png` + `waves_front.png` preview. |

Both reuse palette/fonts from `../math_gallery/mini_book.py` and plate art from
`plate_library.py`, and target Printify blueprint 485 / District Photo.

## Printify / Etsy flow
- **Blueprint 485** "Hardcover Journal Matte", **provider 28** District Photo (US).
  Single variant `65223`; print area 4065×2850. Base cost ~$9.63, US shipping
  ~$5.29. Retail $34 (free shipping) → ~$14 net after Etsy fees.
- Publish uses `printify/printify_publish.py`: `upload_image` → `create_poster`
  (blueprint 485/provider 28) → set title/description/tags/price via a product
  PUT → `publish_product` (pushes to Etsy as a **draft**). Needs
  `printify/.env` (gitignored) with `PRINTIFY_TOKEN` + `PRINTIFY_ETSY_SHOP_ID`.
- *The Mathematics of Beauty* first published 2026-07-26 (Etsy draft, $34).

```
python generate_journal_cover.py   # -> out/journal_wrap.png
python generate_waves_cover.py     # -> out/waves_wrap.png
```

## Etsy listing copy — *Waves & Harmony*
- **Title:** `Waves & Harmony Math Notebook | Hardcover Lined Journal | Physics Wave Interference Art | STEM Gift for Students, Teachers & Engineers`
- **Price:** $34 (free shipping) — same margin as the first notebook.
- **Tags (13):** `math notebook`, `physics journal`, `wave art`, `hardcover journal`, `lined notebook`, `STEM gift`, `science notebook`, `math teacher gift`, `engineer gift`, `sound wave art`, `resonance`, `student notebook`, `math lover gift`
- **Description:**
  > Some ideas do more than compute — they resonate. **Waves & Harmony** is a
  > matte hardcover notebook built from real wave mathematics: a two-source
  > interference field on the cover, with Lissajous curves, a harmonograph
  > trace and a Chladni figure on the back.
  >
  > • 150 lined pages — think, sketch and dream
  > • Matte hardcover, lays reasonably flat
  > • Black + gold design, printed edge to edge
  > • A quiet gift for students, teachers, engineers and anyone who loves the
  >   math behind sound, light and vibration.

`out/`, `mock/` and the Printify scratch files are gitignored.
