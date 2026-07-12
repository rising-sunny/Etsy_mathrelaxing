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

---

## Update 2026-07-12 (2) — 12 Etsy products replicated to the web

- Compared the 42-product Etsy catalog against the web's seed files; found the
  web already had 5 coloring-book PDFs + a few attractor animations, but was
  missing most prints, both Procreate palette packs, all iPad/interactive
  bundles, planners, and the newest listings (incl. the just-published
  Geometric CBN and CBN 3D).
- Replicated the "easy" tier first: 5 more coloring-book PDFs (Voronoi,
  Islamic Geometry, Celtic Knot, Spiral Tilings, Neural Network), the Physics
  & Calculus Equations print set, the Chladni poster, and the Rössler /
  Harmonograph / Vector Field prints (each zipped as its 3 color variants),
  plus both Procreate palette packs. 12 products total.
- Pushed to `rising-sunny/mathrelaxing.store` (commit 4cead9a): new
  `seed_etsy_digital_batch2.py` (same idempotent upsert-by-slug pattern as the
  existing `seed_etsy_digital.py`) + ~113 MB of assets under
  `static/downloads/` and `static/img/` (force-added past the binary
  gitignore rules — that blanket rule still correctly blocks everything else,
  e.g. the DB, `.codex-backups`, unrelated large mockup zips).
- **Still needs a manual step ON THE VPS** to actually go live (git push does
  not touch the live `mathrelaxing.db`):
  ```bash
  cd /var/www/mathrelaxing.store
  git pull origin main
  source .venv/bin/activate    # if the seed script needs the venv's deps
  python seed_etsy_digital_batch2.py
  ```
  No service restart needed — it's a DB write, not a code change the running
  process needs reloaded. Verify at https://mathrelaxing.store/collection/coloring-books
  (and /collection/strange-attractors, /collection/harmonic-geometry,
  /collection/flow-fields, /collection/chladni-figures, /collection/digital-downloads).

### Deferred to a later batch (not yet replicated)
- iPad/interactive bundles (Fractal Flora iPad, Sacred Geometry iPad+SVG,
  Voronoi iPad, Celtic Knot iPad, Islamic Geometry iPad, Spiral Tilings iPad,
  Geometric CBN, **CBN 3D**) — these are self-contained HTML apps; need a
  decision on how the web serves/sells them (probably same thematic_bundle
  pattern, file_url -> the .html, but worth confirming the download/delivery
  flow handles a single large HTML file gracefully).
- Planners (PhD, Life, STEM Focus, Quantified Self, STEM Notebook) — GoodNotes/
  Notability format, same simple pattern should work, just not done yet.
- Physical Lulu POD products (Hyperbolic Gardens, Fractal Flora, Sacred Math,
  Voronoi Gardens physical editions) — needs real fulfillment wiring, more
  involved than a static-file digital download.

### Web catalog conventions discovered (useful for future replication rounds)
- `main.py` has a fixed `COLLECTIONS` dict — a product's `collection` value
  MUST be one of its keys or it won't surface correctly in collection
  browsing. Valid keys seen: strange-attractors, de-jong-attractors,
  complex-plane-geometry, radial-symmetry, reaction-diffusion, fractal-series,
  turing-patterns, voronoi-organics, chladni-figures, flow-fields,
  fractal-flames, harmonic-geometry, notebooks, coloring-books, coloring-book,
  desk-mats, apparel, digital-downloads (generic catch-all bucket).
- `seed_digital.py`'s entries (image_pack/creator_assets/animation_pack, the
  ones with `/api/render/preview?product=...` covers) mostly have EMPTY
  `file_url` — that catalog looks half-wired, not a proven delivery path.
  The proven, working pattern is `seed_etsy_digital.py`'s: real static
  `cover_image` + real static `file_url`, `product_type="thematic_bundle"`.
  Stick to that pattern for future replications.

---

## Update 2026-07-12 (3) — sample galleries + zoom for the 12 replicated products

- User reported the /collection/digital-downloads previews were slow/broken.
  Root cause: `/api/render/preview` checks `static/previews/<slug>.jpg` FIRST;
  if absent it live-renders by `equation_type` — 6 of the 12 products had a
  made-up `equation_type` not in the renderer's registry (raised -> generic
  47,781-byte fallback image for all 6), the other 6 had valid-but-unrelated
  types (rendered a generic pattern, not the real cover). Fixed by dropping
  the real cover at `static/previews/<slug>.jpg` for all 12 (commit de7f208),
  and downsizing the 5 heaviest (up to 1.5 MB) to 60-190 KB to match the
  site's own preview convention.
- Then, per user request, added real sample-page galleries with zoom
  (commit 6fb8083): `bundle.html`'s per-item thumbnails use
  `static/previews/<slug>_<index>.jpg` + zoom target
  `static/previews/<slug>_<index>_clean.jpg` (checked first, same pattern as
  the main preview), and the main hero's zoom needs `static/previews/
  <slug>_clean.jpg`. None of these existed for the 12 new products (item
  thumbnails were returning 21-byte errors, hero zoom 404'd). Rewrote each
  product's `contents_json` in `seed_etsy_digital_batch2.py` to list real
  sample items (5-7 interior pages per coloring book, 8 equation designs for
  Physics set, 2 detail crops for Chladni, 3 color variants each for Rössler/
  Harmonograph/Vector Field, 8 swatch packs per palette pack) backed by real
  source images from the Etsy repo — 148 new preview files (~15 MB).
- **Still needs the VPS activation step** (git pull + re-run seed, same as
  before — contents_json changed so the seed script MUST be re-run, not just
  git pulled):
  ```bash
  cd /var/www/mathrelaxing.store
  git pull origin main
  source .venv/bin/activate
  python seed_etsy_digital_batch2.py
  ```
- Learned: `bundle.html` (thematic_bundle/generic products) is entirely
  different from `bundle_download.html` (gated on `collection ==
  "digital-downloads"` only) — but BOTH support the same static-preview-first
  pattern for images via `/api/render/preview` and `/api/render/bundle-item`.
  For any future product with real sample content, always populate
  `static/previews/<slug>.jpg`, `<slug>_clean.jpg`, and per contents_json item
  `<slug>_<i>.jpg` / `<slug>_<i>_clean.jpg` — never rely on the dynamic
  equation renderer for non-generative (uploaded file) products.

---

## Update 2026-07-12 (4) — filled the empty "iPad Coloring Bundles" section

- User pointed out products missing from "iPad Coloring Bundle (GoodNotes ·
  Procreate)". Root cause: `main.py`'s `/collection/digital-downloads` page
  groups products into sections by `product_type` (DIGITAL_GROUPS dict);
  `"ipad_bundle" -> "iPad Coloring Bundles"` was defined in the code but ZERO
  products ever used that product_type — the section always rendered empty.
  This was exactly the deferred "iPad/interactive bundles" item from the
  first replication batch.
- Added all 9 iPad products from Etsy (commit 28f843e), `product_type=
  "ipad_bundle"`, `collection="digital-downloads"` (both required for the
  section to populate): 4 GoodNotes/Procreate bundles (Fractal Flora, Sacred
  Geometry, Celtic Knot, Islamic Geometry — each a combined zip merging what
  were separate Etsy files: GoodNotes PDF + Procreate PNG set + .swatches +
  how-to PDF) and 4 interactive Safari SVG apps (Voronoi Gardens, Spiral
  Tilings, Geometric CBN, Sacred Geometry SVG) + **CBN 3D** (zip copied as-is,
  already self-contained).
- **Important template-routing discovery**: `collection == "digital-downloads"`
  routes the detail page to `bundle_download.html`, a DIFFERENT template from
  the generic `bundle.html` used for everything else. `bundle_download.html`'s
  image gallery comes from listing files in `static/digital/<slug>/`
  (hero/cover-named files bubble first) — it does NOT use contents_json items
  as images, and does NOT use static/previews/<slug>_<i>.jpg. contents_json
  there is shown only as a plain "What you get" text list.
  This meant the earlier commit's (6fb8083) per-item sample-gallery-with-zoom
  work was WASTED on the 3 pre-existing digital-downloads products (Physics
  print set, both Procreate palette packs) — their real gallery mechanism
  needed static/digital/<slug>/ populated instead, which is now done too
  (retrofitted in the same commit, no DB change needed for those 3).
  **Rule of thumb for any future digital-downloads-collection product**:
  populate static/digital/<slug>/ for the gallery, static/previews/<slug>.jpg
  (+_clean.jpg) for the collection-grid thumbnail, and static/img/<slug>_
  cover.jpg for the DB cover_image field — three different asset locations
  for three different rendering paths.
- **VPS activation** (git pull + re-run — new products need the seed script):
  ```bash
  cd /var/www/mathrelaxing.store
  git pull origin main
  source .venv/bin/activate
  python seed_etsy_digital_batch3.py
  ```
