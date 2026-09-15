# Chaos Theory — Magnetic Pendulum (square POD posters)

Physical POD version of the "Chaos Theory Wall Art Set of 4 | Magnetic Pendulum
Fractal Prints" digital listing (4573180570). The source generator was not in
the repo, so the basins of attraction were **regenerated from the equation of
motion** at high resolution (`generate_pendulum.py`, numpy-vectorised, 3000²)
to closely match the sold aesthetic — jewel palette, computed swirls, magnet
dots. Square art → square posters (no crop).

## Files
| File | What it does |
|---|---|
| `generate_pendulum.py` | Simulates a damped pendulum over N magnets across the whole grid at once; colours each start by the magnet it settles on, shaded by settle time. Renders `masters/pendulum_{3,4,5,6}.png`. |
| `create_physical_posters.py` | Publishes the 4 as **square** matte posters (Printify blueprint 282 / provider 2: 10×10, 12×12, 16×16) to the connected Etsy shop. |

## Live listings (2026-09-15)
| Design | Etsy ID | Sizes / price |
|---|---|---|
| Three Magnets | 4576033993 | 10/12/16 in · $22–38 |
| Four Magnets | 4576034077 | 10/12/16 in · $22–38 |
| Five Magnets | 4576034183 | 10/12/16 in · $22–38 |
| Six Magnets | 4576053050 | 10/12/16 in · $22–38 |

Publish live/active (Printify has no draft step); declare Printify as the
production partner on each in Etsy settings.
