# Neo Deco — generative metallic Art-Deco set

Rides the 2026 "Neo Deco / Glamoratti" trend (chrome + jewel tones, Art-Deco
geometry). Validated on Etsy API: `chrome geometric art` score **70.8**, only
~1.5k competitors, ~$42 median — a wide-open lane for a generative moat.

Three parametric designs — **Sunburst**, **Arch Portal**, **Rose Window** —
built from exact geometry, surfaced with a **matte brushed-foil metal engine**
(soft single-sweep gradient + grain; deliberately *not* the plastic "WordArt
chrome" band) and emerald jewel accents on jewel-tone grounds.

## Files
| File | What it does |
|---|---|
| `generate_neo_deco.py` | The art engine. `metal()` masks a soft foil gradient (+ brushed grain) to each parametric motif. → `masters/*.png` (2:3, 2400×3600 = 8×12in @300). |
| `build_package.py` | Etsy deliverables: gallery-wall hero, per-design framed mockups, flat set grid, info card → `previews/`; 2:3/4:5/ISO print files → `prints/`; `Neo_Deco_Set.zip`. |
| `create_digital_listing.py` | Digital printable "Set of 3" Etsy listing (taxonomy 2078, $14). |
| `create_physical_posters.py` | 3 POD poster products via Printify (blueprint 282 / provider 99, 2:3 sizes 12×18/20×30/24×36) → pushed to Etsy. |

## Live listings (2026-08-26)
| Listing | Etsy ID | Type | Price |
|---|---|---|---|
| Neo Deco — Set of 3 (printable) | 4563088169 | Digital | $14 |
| Neo Deco Sunburst Poster | 4563113946 | POD | $28–54 |
| Neo Deco Arch Poster | 4563090295 | POD | $28–54 |
| Neo Deco Rosette Poster | 4563090523 | POD | $28–54 |

All four are **active/live**.

## ⚠️ Printify → Etsy publishes as ACTIVE, not draft
`printify_publish.publish_product()` pushes the product to the connected Etsy
shop and Etsy makes it **active (live) immediately** — there is no draft step.
While Printify's `is_locked=True` (publish in progress, ~1–3 min), Etsy state
changes (`state=inactive`) do **not** commit — they report back as `edit` and
the public listing stays active. Wait for `is_locked=False`, then set state.
The `/shops/{id}/listings/active` index also lags several minutes behind the
authoritative per-listing `GET /listings/{id}` state — trust the latter.

## Build
```
python generate_neo_deco.py     # -> masters/
python build_package.py         # -> previews/, prints/, Neo_Deco_Set.zip
python create_digital_listing.py
python create_physical_posters.py
```
Etsy auth: `etsy_token.json` (repo root, gitignored). Printify: `printify/.env`
(gitignored). Derived outputs (`prints/`, `previews/`, `*.zip`, `_pf_*.jpg`) are
gitignored.
