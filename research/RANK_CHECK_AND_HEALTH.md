# Rank Checker + Health Check — MathRelaxing

**Date:** 2026-07-14  
**Shop:** TheMathRelaxing  
**Source:** eRank Rank Checker (no personalization / no ads) + Health Check  

---

## Health Check

**Result: no open issues listed** (eRank only shows listings with problems).

Post-SEO pass (tags filled, titles cleaned), Health Check is clean for:
- Missing tags  
- Missing images  
- One-word tags  
- Spelling  

If anything reappears after next Sync, re-run `seo_optimize_listings.py`.

---

## Rank Checker highlights

### `math wall art` (from first batch)

| Listing | Page | Rank |
|---------|-----:|-----:|
| **Ulam Spiral** | 1 | **#3** |
| Euler's Identity | 1 | #48 |
| Golden Ratio / Fibonacci | 2 | #86 |
| Physics Calculus Set of 8 | 3 | #127 |
| Harmonograph | 4 | #165 |
| Rössler Attractor | 5 | #203 |
| Newton Fractal | 5 | #240 |
| Clifford Attractor | 6 | #277 |
| Lorenz Attractor | 7 | #314 |

**Action:** Double down on Ulam Spiral (#3) — promote / ads optional / more similar number-theory prints.

### `physics wall art` (second batch)

| Listing | Page | Rank |
|---------|-----:|-----:|
| **Maxwell Equations** | 1 | **#1** |
| Chaos Theory Strange Attractors | 2 | #51 |
| Black Hole / Schwarzschild | 2 | #88 |
| Vibrating String Harmonics | 3 | #125 |
| Fourier Square Wave | 4 | #163 |
| Physics Calculus Set of 8 | 5 | #200 |

**Action:** Maxwell is a hero SKU — protect SEO, improve images/video, consider ads. Title front-load we applied is working.

### `seamless loop`

| Listing | Page | Rank |
|---------|-----:|-----:|
| **Phyllotaxis Bloom** | 1 | **#10** |
| De Jong Seamless | 2 | #53 |
| Voronoi Cell Garden Loop | 2 | #88 |
| Julia Set Animation | 3 | #125 |
| Thomas Attractor Loop | 4 | #163 |
| De Jong Loop (alt) | 5 | #201 |

**Action:** Phyllotaxis is strong. Merge/redirect energy away from duplicate De Jong listings long-term.

### Keywords with little/no shop presence in results UI
(May rank very deep or not at all for this shop — prioritize elsewhere)

- `digital planner` / `goodnotes planner` — high demand (~20k / ~1.4k) but competitive; keep optimizing titles/tags  
- `adult coloring book` — demand huge, competition huge  
- `science wall art` / `printable wall art` — use as tags; rank where physics/math titles already work  
- `sacred geometry` — keep on sacred listings as superstar  

---

## Superstar Keywords applied (eRank)

Session total ~**12** listings with Superstar set (earlier + this pass), including:

| Superstar | Examples |
|-----------|----------|
| math wall art | Harmonograph, Lorenz, Clifford, Ulam cluster |
| physics wall art | Chladni, Maxwell, Fourier, Calculus set |
| science wall art | Chaos attractors poster |
| seamless loop | De Jong, loops |
| digital planner / notebook | Graph paper bundles |
| adult coloring book | Fractal Flora PDF |
| minimalist wall art | Japandi set |
| generative art | Julia loop |

Full map: `research/superstar_keywords.md`

---

## Strategic takeaways

1. **Winning clusters:** Physics wall art + Math wall art title formula is ranking.  
2. **Hero products:** Maxwell (#1 physics), Ulam (#3 math), Phyllotaxis (#10 seamless).  
3. **Health:** Clean — maintain 13 tags, multi-word, format keywords.  
4. **Next growth levers:**  
   - More listings in the *physics wall art* / *math wall art* formula  
   - Optional Etsy Ads on #1–#10 ranks  
   - Reduce duplicate De Jong loops  
   - Keep Superstar Keywords filled shop-wide  

---

## Re-run commands

```bash
python seo_optimize_listings.py --refresh --apply
python seo_rewrite_descriptions.py --refresh --apply
```

eRank: Sync Listings → Rank Checker (quota 25/day) → Health Check.
