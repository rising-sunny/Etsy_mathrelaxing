# Celestial Mathematics — generative astronomy art

A distinct line from Neo Deco: deep night-sky grounds with fine gold/cream
linework, every plate computed from real math. Validated on Etsy API:
`celestial mathematical art` score **69.5**, only ~98 competitors — a wide-open
lane with a pure generative moat.

## Files
| File | What it does |
|---|---|
| `generate_celestial.py` | The art engine. Plates: **Orbits** (elliptical orrery), **Lunar Phases** (synodic terminator), and the **Resonance** harmonograph family (`plate_resonance()` is parametric over frequency ratios; `build_resonance_set()` renders the set of 6). → `masters/`. |
| `build_resonance_listing.py` | Etsy deliverables for the Resonance set: gallery-wall hero, flat grid, single mockups, info card → `previews/`; 2:3/4:5/ISO prints → `prints/`; two ZIPs (each < Etsy's 20 MB cap). `--publish` creates the listing. |

## Live listings (2026-08-26)
| Listing | Etsy ID | Price |
|---|---|---|
| Resonance — Set of 6 (digital printables) | 4563133990 | $16.99 |
| Resonance II:III Poster (POD) | 4563112045 | $28–54 |
| Resonance III:IV Poster (POD) | 4563135708 | $28–54 |
| Resonance III:V Poster (POD) | 4563112181 | $28–54 |
| Resonance IV:V Poster (POD) | 4563135938 | $28–54 |
| Resonance V:VI Poster (POD) | 4563136002 | $28–54 |
| Resonance II:V Poster (POD) | 4563136064 | $28–54 |

Physical posters are Printify blueprint 282 (matte, 2:3) via
`create_physical_posters.py`; they publish live/active (no draft step).

The six figures are the frequency ratios II:III, III:IV, III:V, IV:V, V:VI,
II:V — each a damped two-pendulum harmonograph, auto-centered and scaled to fit.

## Build
```
python generate_celestial.py            # orbits + lunar + resonance (defaults)
python -c "import generate_celestial as g; g.build_resonance_set(6)"
python build_resonance_listing.py --publish
```
Etsy auth: `etsy_token.json` (repo root, gitignored). Derived outputs
(`previews/`, `prints/`, `*.zip`) are gitignored. Note: the Etsy listing is
created **live/active** by the shop, not as a draft — see neo_deco_set/README.
