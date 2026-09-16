# Julia Set — vibrant fractal art (digital + square POD)

A new math-art line: six Julia sets (z → z² + c) with smooth continuous
escape-time colouring in a vibrant electric palette. Targets the "julia set art"
niche (Etsy score **81.8**, only ~75 competitors, fav avg 120). Every pixel is
computed from the equation — no clip-art, no AI.

## Files
| File | What it does |
|---|---|
| `generate_julia.py` | Renders 6 constants (Dragon, Douady Rabbit, Spiral, Filament, Swirl, Pinwheel) at high res with boolean-mask iteration + cyclic palette → `masters/`. |
| `build_listing.py` | Etsy previews (gallery hero, grid, singles, info) + square print files + 2 ZIPs; `--publish` creates the digital set-of-6 listing. |
| `create_physical_posters.py` | Publishes the 6 as **square** matte posters (Printify blueprint 282 / provider 2: 10×10, 12×12, 16×16). |

## Live listings (2026-09-16)
| Item | Etsy ID | Price |
|---|---|---|
| Julia Set — Set of 6 (digital) | 4576428241 | $16.99 (draft) |
| Dragon (POD) | 4576429045 | $22–38 |
| Douady Rabbit (POD) | 4576447024 | $22–38 |
| Spiral (POD) | 4576447138 | $22–38 |
| Filament (POD) | 4576447222 | $22–38 |
| Swirl (POD) | 4576447334 | $22–38 |
| Pinwheel (POD) | 4576447410 | $22–38 |

POD posters publish live/active (Printify has no draft step); declare Printify
as the production partner on each in Etsy settings.
