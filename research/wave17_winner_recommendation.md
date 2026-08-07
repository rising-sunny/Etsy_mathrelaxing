# Wave 17 — Productos ganadores (Etsy API + eRank Edge)

**Fecha:** 2026-08-06  
**Fuentes:**
- Etsy API → `product_finder.py` → `wave17_etsy_opportunities.{json,csv}` (43 keywords)
- eRank Edge → `erank_edge_bulk.py` + `research/.edge_erank_profile` → `wave17_erank_bulk.*`
- Keywords: `research/wave17_candidate_keywords.txt`

**Ya en tienda (no reinventar):** STEM Pack, Physics Pack, Physics Formula Set of 6, Unit Circle, Famous Equations, Platonic Solids, Schrödinger/Maxwell singles, lab notebook, graph paper bundles.

---

## Resumen ejecutivo

| Prioridad | Producto | Señal API | Acción |
|---|---|---|---|
| **#1 BUILD** | **Strange Attractors Poster Set of 6** (digital $11.99–$14.99) | Solo **2 listings**, fav avg **132**, score **79.4**; `lorenz attractor poster` = 17 listings / score **83.3** | Set cohesivo dark-observatory: Lorenz, Rössler, Thomas, Halvorsen, Chen, Aizawa (renderers ya en math_gallery) |
| **#2 BUILD** | **Trigonometry / Algebra Classroom Poster Set** | Trig set: **16 listings**, fav **85**, score **77.6**; algebra classroom set: **69 listings**, fav **91**, score **81.5**; unit circle set: **1 listing** | Bundle Unit Circle + SOHCAHTOA + identities + graphs + algebra essentials; SEO “math classroom posters set” |
| **#3 BUILD** | **DNA / Molecule Wall Art Set of 6** | DNA printable score **84.1** (305 listings, 100% digital, $4 med); molecule **77.9** | Estética scientific-plate / dark lab: double helix, base pairs, key molecules — abre bio sin salir del brand STEM |
| **#4 SCALE** | **Math Teacher Gift / Classroom Bundle** | math classroom posters set **82.5** (fav 163); gift set **77.5** (fav 182); bulletin board **80.8** | Re-bundle: Formula Set + Famous Equations + Unit Circle + Lab Notebook @ $19–24 |
| **#5 WATCH** | **Phase portrait / dynamical systems plate** | phase portrait score **78.9**, fav **133**, 193 listings | Hermano del attractor set; 1–2 plates hero o set of 4 |

### Ya cubierto (benchmarks en SERP)

| Keyword | Score | Status |
|---|---:|---|
| physics formula poster set | **80.5** | **Live** `4550732719` (top competitor es bundle genérico; nosotros más premium) |
| schrodinger equation poster | **83.3** | Single + packs |
| math wall art set of 6 | **80.9** | Famous Equations + packs |

---

## Señal eRank (Edge)

Sesión **logueada** en Bulk Tool (mejor que wave16 Session Limit), pero la mayoría de long-tails STEM siguen en **0 / sin Avg** (cuota o long-tail eRank).

| Keyword | Jul 2026 | Avg/mo | KD | Lectura |
|---|---:|---:|---:|---|
| scientific method poster | 10* | 20 | **47** | Volumen bajo pero KD moderado; producto fácil |
| chemistry / dna / trig / attractors… | 0 | — | — | Confiar en **API favs + #listings** |

\* latest 10 a menudo es ruido en eRank.

**Conclusión eRank:** no bloquea builds STEM; usa API para ranking y eRank solo para validar mainstream classroom más tarde (Trend Buzz / Keyword Tool single).

---

## Top API (nuevos, con fit MathRelaxing)

| Keyword | Listings | Fav≈ | $ med | Digital | Score | Fit |
|---|---:|---:|---:|---:|---:|---|
| **dna wall art printable** | 305 | 69 | $4 | 100% | **84.1** | Alto (plate aesthetic) |
| **lorenz attractor poster** | **17** | **90** | $18 | 41% | **83.3** | **Excelente** (código) |
| math classroom posters set | 966 | **163** | $9 | 100% | **82.5** | Alto (sets) |
| algebra poster set classroom | **69** | **91** | $9 | 97% | **81.5** | Alto |
| measurement conversion poster | 237 | **195** | $7 | 67% | **81.3** | Medio (menos “art”) |
| math bulletin board set | 242 | **143** | $11 | 100% | **80.8** | Medio (kits) |
| **strange attractor poster set** | **2** | **132** | $43 | 0%* | **79.4** | **Excelente** (digital gap) |
| physics classroom posters set | 121 | 74 | $11 | 83% | **79.8** | Ya formula set + pack |
| **trigonometry poster set** | **16** | **85** | $13 | 75% | **77.6** | Excelente |
| molecule wall art printable | 275 | 43 | $6 | 100% | **77.9** | Alto |
| chemistry wall art set | 481 | 65 | $15 | 73% | **74.0** | Bueno |
| biology cell poster set | **53** | 70 | $15 | 33% | **73.6** | Bueno (digital limpio) |

\* Sample 0% digital = SERP de canvas caros → **hueco digital a $12–15**.

---

## Plan de build (orden)

### 1) Strange Attractors Set of 6 — **siguiente producto “wow”**
- **Por qué:** océano casi vacío (2 sets), favs altos, moat generativo, estética dark-observatory alineada con Formula Set.
- **Contenido:** Lorenz, Rössler, Thomas, Halvorsen, Chen, Aizawa (ya en `math_gallery` / plate_library).
- **Precio:** set $12.99–$14.99 (SERP físico a $43 → digital premium justificado).
- **Esfuerzo:** 1–2 días (reutilizar renderers + layout zones del formula set).
- **SEO:** strange attractor poster set, lorenz attractor poster, chaos theory wall art.

### 2) Trigonometry Classroom Poster Set
- Unit Circle (existente) + values table plate + identities + sine/cosine graphs + law of sines/cosines.
- **Precio:** $9.99–$12.99.
- **Listings:** 16 (trig set) / 1 (unit circle set) → room.

### 3) DNA & Molecules Scientific Plate Set of 6
- Double helix structure, base pairing, DNA vs RNA, simple amino acid / molecule icons en estilo plate (no stock cartoon).
- **Precio:** $9.99–$11.99 (med DNA ~$4 → subir con calidad).
- Abre **bio/chem** con la misma marca.

### 4) Math Teacher Gift Bundle (zero new art)
- Physics Formula Set + Famous Equations + Unit Circle + Lab Notebook PDF.
- **Precio:** $19.99–$24.99.
- Keywords: math teacher gift set, math classroom posters set, science classroom decor.

### 5) Optional: Algebra Classroom Poster Set
- Score 81.5, 69 comps — si classroom convierte bien tras #2.

---

## Qué no priorizar ahora

| Idea | Motivo |
|---|---|
| Otro physics formula / pack genérico | Ya live; SERP top somos nosotros |
| Measurement conversion poster | Favs de cocina/floral — SERP ruidoso |
| Bulletin board kits genéricos | Menos “art brand”, más clipart teacher |
| Mandelbrot set suelto | Score bajo; mejor dentro de fractal set luego |
| Coffee table book #3 | Esperar venta de Beauty |

---

## Matriz rápida

| Criterio | Attractors set | Trig set | DNA set | Teacher gift bundle |
|---|---|---|---|---|
| Demanda (favs) | Alta | Alta | Media-alta | Alta |
| Competencia | **Muy baja (2)** | Baja (16) | Media | Media |
| Moat / fit | **Máximo** | Máximo | Alto | Máximo (re-pack) |
| Velocidad | 1–2 d | 1–2 d | 2–3 d | **0.5 d** |
| AOV | $13–15 | $10–13 | $10–12 | **$20–24** |

**Cash esta semana:** Teacher Gift Bundle.  
**Mejor producto nuevo “extraordinario”:** **Strange Attractors Set of 6**.  
**Mejor classroom SEO:** Trig / Algebra classroom set.

---

## Artefactos

```
research/wave17_candidate_keywords.txt
research/wave17_etsy_opportunities.json
research/wave17_etsy_opportunities.csv
research/wave17_erank_bulk.json
research/wave17_erank_bulk.csv
research/wave17_erank_batch{1,2,3}.png
research/wave17_opportunity_report.md
research/wave17_winner_recommendation.md
```
