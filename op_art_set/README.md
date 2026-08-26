# Kinetic — op-art line (blue-ocean, high-ticket)

High-contrast optical illusions in the Vasarely / Bridget Riley lineage, each
generated from a parametric distortion field (nothing hand-drawn). Targets the
low-competition, high-price "kinetic geometric art" niche (~1.1k Etsy comps,
median ~$50).

## Files
| File | What it does |
|---|---|
| `generate_opart.py` | Renders the 6 masters from numpy scalar fields with analytic anti-aliasing → `masters/`. Fields: Vega (bombé sphere), Moiré, Vortex, Fall (wave), Flare (radial), Quanta (square spiral). |
| `build_listing.py` | Etsy previews + print sizes + 2 ZIPs; `--publish` creates the digital set-of-6 listing. |
| `create_physical_posters.py` | Publishes the 6 as matte POD posters (Printify blueprint 282, 2:3 sizes). |

## Live listings (2026-08-26)
| Listing | Etsy ID | Price |
|---|---|---|
| Kinetic — Op Art Set of 6 (digital) | 4563164732 | $17.99 |
| Vega Op Art Poster (POD) | 4563165126 | $28–54 |
| Moiré Op Art Poster (POD) | 4563165226 | $28–54 |
| Vortex Op Art Poster (POD) | 4563165272 | $28–54 |
| Fall Op Art Poster (POD) | 4563165400 | $28–54 |
| Flare Op Art Poster (POD) | 4563141595 | $28–54 |
| Quanta Op Art Poster (POD) | 4563165506 | $28–54 |

Physical posters publish live/active (Printify has no draft step). Declare
Printify as the production partner on each in Etsy settings.
