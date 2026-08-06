# Etsy → Lulu automatic fulfillment

When a buyer pays for a mapped physical book on Etsy, a cron job runs
`fulfillment.py check`, which creates a Lulu print-job with the buyer’s
shipping address and the public interior/cover PDFs.

```
Etsy paid receipt (poll every ~15 min)
        │
        ▼
  listing_id in BOOKS?
        │
        ▼
  PDF URLs (mathrelaxing.store/static/downloads/{slug}/…)
        │
        ▼
  Lulu POST /print-jobs/  →  status UNPAID
        │
        ▼
  Pay in Lulu Print Job Portal (or card-on-file)
        │
        ▼
  Lulu prints + ships to buyer
```

Etsy v3 has **no order webhooks** — only polling `GET /shops/{id}/receipts`.

## Mapped hardcover listings

| listing_id | Book | Etsy | Pages | Package |
|---:|---|---|---:|---|
| **4544209146** | *The Mathematics of Beauty* (live title: Math Art Coffee Table Book…) | **active** | 88 | square HC color STD/PREM |
| **4548870190** | *The Shape of an Idea* | draft | 45 | square HC color STD/PREM |

Etsy SKUs: `TMB-STD-8585` / `TMB-PREM-8585` and `SOI-STD-8585` / `SOI-PREM-8585`.  
Premium SKUs select Lulu package `0850X0850.FC.PRE.CW.080CW444.MXX`.

Production partner on both listings: **5702394** (Lulu / Morrisville NC) — Etsy handmade disclosure only; **does not** auto-print. The API bridge does.

Coloring books are also in `BOOKS` if you later point their PDFs at the same host.

## One-time setup

### 1. Credentials — `lulu_books/.env` (gitignored)

```bash
cp lulu_books/.env.example lulu_books/.env
# fill LULU_CLIENT_KEY / LULU_CLIENT_SECRET from developers.lulu.com
# PDF_PUBLIC_BASE=https://mathrelaxing.store/static/downloads
```

Keys already live in `mathrelaxing.store/.env.vps` (`LULU_*`).

### 2. Etsy token with `transactions_r`

Current `etsy_token.json` must include `transactions_r` or receipts return 403:

```bash
python auth.py   # scopes: listings_* shops_* transactions_r
```

### 3. Print PDFs

```bash
# Shape of an Idea
cd lulu_books/generators/concepts_gallery
python full_book.py && python build_cover_wrap.py

# Mathematics of Beauty
cd ../math_gallery
python full_book.py && python build_cover_wrap.py
```

### 4. Host PDFs publicly (same pattern as store coloring books)

```bash
cd /path/to/Etsy_mathrelaxing
python lulu_books/fulfillment.py publish-pdfs
# copies into ../mathrelaxing.store/static/downloads/{shape-of-an-idea,mathematics-of-beauty}/
# Deploy that tree to the VPS so these return 200:
#   https://mathrelaxing.store/static/downloads/shape-of-an-idea/interior.pdf
#   https://mathrelaxing.store/static/downloads/shape-of-an-idea/cover.pdf
#   https://mathrelaxing.store/static/downloads/mathematics-of-beauty/interior.pdf
#   https://mathrelaxing.store/static/downloads/mathematics-of-beauty/cover.pdf
```

### 5. Verify

```bash
python lulu_books/fulfillment.py register
python lulu_books/fulfillment.py dry-run
python lulu_books/fulfillment.py ensure-partner   # Lulu partner on both listings
```

## Production cron (VPS)

```cron
*/15 * * * * cd /path/to/Etsy_mathrelaxing && python lulu_books/fulfillment.py check >> /var/log/lulu_fulfill.log 2>&1
```

| Command | Action |
|---|---|
| `check` | Poll Etsy → stage → **create Lulu print-job (UNPAID)** |
| `list` | Staged / submitted jobs |
| `submit RECEIPT_ID` | Re-submit one |
| `register` | File + URL readiness |
| `publish-pdfs` | Copy local PDFs → store `static/downloads/` |
| `dry-run` | Stage both hardcovers, no Lulu call |
| `ensure-partner` | Set Etsy production partner = Lulu |

## Safety

- Jobs are **UNPAID** until paid in the Lulu portal. Do **not** add a card on file if you want that human gate.
- State (gitignored): `lulu_books/output/fulfillment_state.json`, `pending_orders.json`.
- Failed submits are **not** marked processed — the next `check` retries.

## Activate Shape of an Idea

When ready:

1. Confirm partner + images + variants on draft `4548870190`.
2. Activate listing in Etsy (or via API `state=active`).
3. Ensure PDFs are live under `PDF_PUBLIC_BASE`.
4. Cron running `fulfillment.py check`.
