# MathRelaxing — Session Notes & Roadmap

Handoff notes so any fresh Claude Code session can pick up without the chat
history. Everything below is reflected in committed code on branch
`claude/content-review-j4gu48`.

## Big picture / strategy

- **Goal:** multi-channel selling with `products_catalog.py` as the single
  source of truth, and **business continuity** (a fallback if Etsy ever
  suspends the shop). Etsy does **not** require exclusivity — the same product
  can be sold on Etsy + own web + Bonanza. The only rule is: **never use Etsy
  listings/images/messages to divert buyers off-platform** (fee avoidance).
- **Target architecture:**
  ```
  products_catalog.py  ──► etsy_manager.py        ──► Etsy
                       ──► export_catalog.py (TODO) ──► mathrelaxing.store (VPS)
                       ──► bonanza publisher (exists on VPS) ──► Bonanza
  ```
  One catalog, multiple publish targets. Sync direction is repo → channels.

## Channels / infrastructure

- **Etsy:** `etsy_manager.py` (OAuth token in `etsy_token.json`). Token
  currently **lacks `transactions_r` scope** → cannot read orders/receipts
  (403). `auth.py` already requests it; must **re-run `auth.py` from a PC**
  (browser OAuth, redirect `https://mathrelaxing.store/callback`) to grant it.
- **Web (mathrelaxing.store):** custom-coded (Python; `.gitignore` shows
  Django/Flask signals), lives **only on the VPS**. The GitHub repo
  `rising-sunny/mathrelaxing.store` is **empty** (just a `.gitignore`).
  Already has **PayPal** checkout/delivery (digital + physical) and a working
  **Bonanza API** publisher. Deploy mechanism: unknown.
- **Bonanza:** API integration already built and used on the VPS.

## Pending work (needs a PC)

1. **Push the VPS web code to GitHub** (`rising-sunny/mathrelaxing.store`).
   This is the #1 continuity fix (web currently is a single point of failure).
   Check `git status` for secrets before committing (`.env`, DB creds, keys).
2. **Re-authorize Etsy** with `transactions_r` so orders can be read.
3. **`export_catalog.py`** — emit a clean `catalog.json` (+ assets) from
   `products_catalog.py` for the web to consume. Field mapping depends on how
   the web stores products (DB / JSON / API) — decide after seeing the code.
4. **`etsy_orders.py`** — pull receipts via API into a local record for
   accounting/analytics (LEGITIMATE internal use only). NOTE: Etsy policy +
   GDPR forbid marketing to Etsy buyers / exporting their emails to a list.
   Build the owned customer list on the **web** with opt-in instead.
5. **Bonanza:** decide whether the publisher lives on the VPS (consumes
   catalog.json) or is centralized into this repo next to `etsy_manager`.

## Done this session

- **New product published (DRAFT, activation manual):** "Geometric Color by
  Number" — 20-design low-poly coloring book from generative math art
  (domain colourings, Newton fractals, Julia sets). Code in `lowpoly_cbn/`
  (`lowpoly_core.py`, `art_gallery.py`, `build_package.py`, `build_listing.py`,
  `publish_listing.py`). Etsy draft **listing_id 4536173762**, $9.99,
  taxonomy 2078, 6 photos + 12.7 MB PDF. (pkg_src/pkg_out are gitignored.)
- **3D CBN app** (`ipad_3d_cbn/`): earlier work; per-face number sizing +
  raycast occlusion so numbers show only on visible faces. Etsy draft 4535962223.
- **Domain cleanup (anti-suspension):**
  - Removed the bare `mathrelaxing.store` domain from **27 live Etsy
    descriptions** and from the catalog source (`products_catalog.py`). Brand
    name "MathRelaxing" kept; only the domain dropped.
  - Changed the diagonal preview **watermark** `MATHRELAXING.STORE · PREVIEW`
    → `MATHRELAXING · PREVIEW` in the generators, regenerated previews, and
    re-uploaded to **6 listings**: Chladni (4535746170), Rössler (4533519822),
    Harmonograph (4534117446), Vector Field (4533974490), Strange Attractors
    (4534313102), Physics/Calculus (4535639595).
  - Audit: **no domain remains on any pre-sale (listing) surface**; 0 active
    listings have a video. Remaining domain mentions are all **post-purchase
    delivered files** (readmes/instruction PDFs), **physical Lulu book prints**
    (legitimate branding), or **functional** (auth redirect, order email,
    internal notes). Decision: leave those — legitimate/low-risk. (Optional
    future: code-only cleanup of delivered-file footers.)

## Conventions / gotchas

- `products_catalog.py` is **CRLF** — after editing, verify lone-LF count is 0.
- Etsy: title ≤140 chars, ≤1 `&`; ≤13 tags, each ≤20 chars; digital file
  ≤20 MB; max 10 images/listing.
- Reupload images safely: upload the new set first, then delete the old ids
  (Etsy requires ≥1 image at all times).
- Headless Chromium for WebGL/Playwright captures: args
  `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.
- All drafts stay **draft** — activation is always manual by the owner.

---

## Update 2026-07-12 — web is now on GitHub ✅

- **`rising-sunny/mathrelaxing.store` now contains the site code** (commit 4d9b1bb,
  345 files, code-only). Independently verified clean: no `.env`, no DB, no
  token files, no `.codex-backups`, no hardcoded keys. Force-pushed over the
  empty placeholder. The #1 continuity gap (code only on the VPS) is CLOSED.
- **VPS facts:** Hetzner Ubuntu, IP 5.78.125.169, `root@`. Site at
  `/var/www/mathrelaxing.store/`. FastAPI + uvicorn (127.0.0.1:8000) via systemd
  `mathrelaxing.service`; nginx TLS reverse proxy. SQLite `mathrelaxing.db`.
  venv `.venv`, secrets in `.env`. Payments: **PayPal** (digital + physical),
  token-gated `private_downloads/`. POD via Printful/Gelato/Lulu. Also sells on
  Bonanza/eBay/Gumroad/Whop; social auto-posting (Pinterest/TikTok/Meta).
- **What is deliberately NOT in git** (gitignored): `.env`, `*.db*`, all
  `*_token.json`, `.codex-backups-*/`, big media (`static/videos|previews|
  downloads|digital|bonanza|...`, `*.mp4/*.psd/*.pdf/*.zip`), print images.
  These must be backed up SEPARATELY (they are not in the repo).
- **Web catalog = `seed.py`** — `PRODUCTS = [{slug, name, collection,
  equation_type, description, price_usd, params_json, active}, ...]`, seeds the
  DB. It is RICHER than the Etsy `products_catalog.py` (desk mats, image/loop
  packs, apparel...). The export_catalog bridge must reconcile the two, not
  blind-copy. Open question: which is master, or keep separate + sync.
- **2 utility scripts excluded** because they had a hardcoded Printful key
  (`check_notebook_variants.py`, `fetch_mockup.py`). Recommend rotating that
  Printful key and moving it to `.env`, then cleaning + re-adding the scripts.

### Remaining continuity gaps (next priorities)
1. **DB backup** — `mathrelaxing.db` (orders + customer PII) still lives ONLY on
   the VPS. Set up a cron `sqlite3 .backup` dump + offsite copy (NOT git).
   This is now the biggest single point of failure.
2. **Deliverables backup** — `private_downloads/` + `static/downloads/` (paid
   product files) also VPS-only; rsync to offsite storage.
3. Etsy re-auth with `transactions_r`; then `export_catalog.py` / `etsy_orders.py`.
