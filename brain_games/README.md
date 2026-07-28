# Brain Games — printable puzzle book

A 22-page printable puzzle book in the MathRelaxing identity (cream `#F6F3EA` /
navy `#1c2b3a` + gold `#b0862f`, Cinzel/Raleway), generated **algorithmically**
so every puzzle is real and solvable:

- **12 Sudoku** — 4 Easy / 4 Medium / 4 Hard, each with a **verified unique
  solution** (randomized backtracking fill + solution-count check on removal).
- **6 mazes** — recursive-backtracker perfect mazes, growing in size, with the
  BFS solution path drawn in the answer key.
- **4 STEM word searches** — Mathematics, Science, Geometry, Space (8-direction
  placement) with highlighted answer keys.

## Files
| File | What it does |
|---|---|
| `generate_brain_games.py` | Renders all pages (PIL, US Letter @ 300 dpi) and assembles `out/MathRelaxing_Brain_Games.pdf` (+ `out/pages/p*.jpg`). |
| `package_brain_games.py` | Builds the buyer ZIP (book PDF + a short print guide) and 5 Etsy listing images (`listing/*.jpg`). |

## Build
```
python generate_brain_games.py   # -> out/MathRelaxing_Brain_Games.pdf + out/pages/
python package_brain_games.py    # -> listing/*.jpg, deliverable/Print_Guide.pdf, the ZIP
```

## Etsy
Digital download, instant, **$5.99**. Listed via the standard
`products_catalog.py` flow (slug `brain_games`): 5 images + the ZIP.

`out/`, `listing/`, `deliverable/` and the ZIP are generated and gitignored
(regenerate before re-upload).
