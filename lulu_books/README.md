# lulu_books — physical coloring-book generation + Lulu POD integration

Ported from mathrelaxing.store's production codebase (app root, `scripts/`,
and a separate `/root/coloring_prototype` workspace) into a standalone,
path-independent package. All absolute `/var/www/mathrelaxing.store/...` and
`/root/coloring_prototype/...` paths were rewritten to be relative to this
folder — nothing here depends on the original VPS layout.

Syntax-checked (`py_compile`) on every file. Runtime import testing was not
completed in this environment — verify imports actually resolve before
relying on this in production (see "Before you run anything" below).

## Layout

```
lulu_books/
  assets/            fonts (Cinzel, Raleway) + logo.png used by covers
  core/              shared toolkit — no app coupling
    mathrelaxing_kit.py       big shared toolkit (PDF/image/video helpers)
    math_meshes.py            mesh generator used by the Sacred Math book
    generate_one_per_family.py  curve-family math (rose, hypotrochoid, etc.)
    generate_harmonographs.py   harmonograph curve generator
  generators/        one script (or pair) per physical book
    gen_hyperbolic_book.py + gen_hyperbolic_cover.py   → Hyperbolic Gardens
    gen_l_systems_book.py + gen_l_systems_cover.py     → Fractal Flora
    gen_sacred_math_book.py                            → Sacred Geometry
    make_voronoi_book.py                                → Voronoi Gardens
    build_harmonograph_cover.py                        → Harmonograph Dreams cover
                                                           (calls the live Lulu API
                                                           for cover-dimensions —
                                                           needs real credentials)
    extract_cover.py / extract_harmonograph_cover.py    small PNG-from-PDF
                                                          extraction utilities
    make_samples.py                                     Fractal Flora listing photos
  lulu_api/          the Lulu Print API client (order-fulfilment)
    lulu_publish.py    LuluClient (auth, cost calc, print-job creation,
                       shipping options) + interior/cover PDF builders
    cover_hero.py      mandala/pattern generator used by cover art
  output/            generators write here (interior.pdf, cover.pdf, ...);
                     nothing is committed here, it's created at runtime
  .env.example        copy to .env and fill in your Lulu credentials
```

## What's genuinely portable vs. what needs your attention

**Clean, self-contained** (no missing dependencies once you install
requirements): `gen_hyperbolic_book.py`+cover, `gen_l_systems_book.py`+cover,
`gen_sacred_math_book.py`, `make_voronoi_book.py`, `core/*`.

**Needs a source file you'll have to supply** (the original generator for
these predates the clean `gen_*_book.py` pattern and wasn't found in a
portable form):
- `extract_cover.py` expects an already-built `Sacred_Harmonics_Cover_v3.pdf`
  in `output/`.
- `extract_harmonograph_cover.py` / `build_harmonograph_cover.py`'s `gallery`
  list expect hand-colored sample PNGs (e.g. colored in Procreate) that
  weren't part of the generator pipeline.

**Calls the real Lulu API when run** (costs nothing in sandbox mode, but
needs valid credentials): `lulu_api/lulu_publish.py`'s `create_print_job`,
`cost_calculation`, `cover_dimensions`; `build_harmonograph_cover.py` (calls
`cover_dimensions` to build the cover).

## Before you run anything

1. `pip install fitz PyMuPDF numpy matplotlib scipy shapely pillow requests`
   (exact package names: `pymupdf`, not `fitz`, on PyPI).
2. `cp .env.example .env` and fill in `LULU_CLIENT_KEY` / `LULU_CLIENT_SECRET`
   from your Lulu developer account. Keep `LULU_SANDBOX=1` until you're sure.
3. `lulu_api/lulu_publish.py` also expects DejaVu Sans at
   `/usr/share/fonts/truetype/dejavu/` (a system font, install via
   `apt install fonts-dejavu-core` on Debian/Ubuntu if missing) — required
   because Lulu rejects PDFs with non-embedded fonts.
4. Because import-level testing wasn't completed here, run each generator
   once locally and confirm it produces a PDF in `output/` before trusting
   it — e.g. `python generators/gen_hyperbolic_book.py`.

## Order-fulfilment flow (for Etsy)

`lulu_api/lulu_publish.py`'s `LuluClient` is fully generic — it doesn't
assume mathrelaxing.store's database or Order model (that coupling lived in
the *other*, simpler `services/lulu.py` in the app, which was NOT ported
here per your choice). To fulfil an Etsy order:

1. Generate/host the interior + cover PDFs publicly (`DOWNLOADS_URL` in
   `.env`).
2. `client = lulu_publish.make_client()`
3. `client.create_print_job(interior_url=..., cover_url=..., pod_package_id=...,
   quantity=1, shipping_address={...}, contact_email=..., title=...)`
4. Poll `client.get_status(job_id)` for fulfilment status.

`cost_calculation()` and `cover_dimensions()` are read-only/no-charge; only
`create_print_job()` spends money.
