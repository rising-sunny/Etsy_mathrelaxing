# The Shape of an Idea — coffee-table math art book

Premium **8.5×8.5″ hardcover** gallery: **18 plates** on great equations & concepts
(Euler, Möbius, Klein, tesseract, paradoxes of infinity…). Companion volume to
*The Mathematics of Beauty* (38 generative plates).

## Build print files (Lulu)

```bash
cd lulu_books/generators/concepts_gallery
python full_book.py          # -> fullbook/interior.pdf  (45 pages)
python build_cover_wrap.py   # -> fullbook/cover_wrap.pdf
```

Lulu SKU (standard hardcover color case-wrap):

`0850X0850.FC.STD.CW.080CW444.MXX`  
Premium edition uses `.FC.PRE.` instead of `.FC.STD.`

## Etsy listing

| Field | Value |
|---|---|
| Title | The Shape of an Idea \| Hardcover Math Art Book \| … |
| listing_id | **4548870190** (draft as of 2026-08) |
| Standard | $38 · SKU `SOI-STD-8585` |
| Premium | $52 · SKU `SOI-PREM-8585` |

Create/refresh draft (optional):

```bash
python listing/create_book_listing.py
```

## Fulfillment (Etsy → Lulu)

Mapped in `lulu_books/fulfillment.py` under `BOOKS[4548870190]`.

```bash
# from repo root (or lulu_books/)
python lulu_books/fulfillment.py register   # file status
python lulu_books/fulfillment.py dry-run    # upload PDFs to R2 if .env set
python lulu_books/fulfillment.py check      # poll paid Etsy receipts → Lulu UNPAID job
```

Requires:

1. `lulu_books/.env` (see `lulu_books/.env.example`) — Lulu + R2  
2. `etsy_token.json` with **`transactions_r`** scope (`python auth.py` to re-consent)  
3. Cron on VPS: e.g. every 15 min `python lulu_books/fulfillment.py check`

Print jobs land **UNPAID** in Lulu until paid in the Print Job Portal.
