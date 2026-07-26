# The Mathematics of Beauty — hardcover journal (POD)

A matte hardcover **notebook** (to write in) in the art book's identity, made
via Printify POD → Etsy. The cover pairs the Lorenz attractor with the black +
gold title, and a clear **"A NOTEBOOK"** label so buyers don't confuse it with
the art book.

## File
| File | What it does |
|---|---|
| `generate_journal_cover.py` | Builds the full-wrap cover PNG (4065×2850, Printify blueprint 485 / District Photo) → `out/journal_wrap.png` + a `journal_front.png` preview. Reuses palette/fonts from `../math_gallery/mini_book.py` and plate art from `plate_library.py`. |

## Printify / Etsy flow
- **Blueprint 485** "Hardcover Journal Matte", **provider 28** District Photo (US).
  Single variant `65223`; print area 4065×2850. Base cost ~$9.63, US shipping
  ~$5.29. Retail $34 (free shipping) → ~$14 net after Etsy fees.
- Publish uses `printify/printify_publish.py`: `upload_image` → `create_poster`
  (blueprint 485/provider 28) → set title/description/tags/price via a product
  PUT → `publish_product` (pushes to Etsy as a **draft**).
- First published 2026-07-26 (Printify draft → Etsy draft, price $34).

```
python generate_journal_cover.py   # -> out/journal_wrap.png
```

`out/`, `mock/` and the Printify scratch files are gitignored.
