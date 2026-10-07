# Wave 16 — Productos ganadores (Etsy API + eRank Edge)

**Fecha:** 2026-08-06  
**Fuentes:**
- Etsy API → `product_finder.py` → `wave16_etsy_opportunities.{json,csv}` (46 keywords)
- eRank Edge → `erank_edge_bulk.py` + profile `research/.edge_erank_profile` → `wave16_erank_bulk.*`
- Keywords: `research/wave16_candidate_keywords.txt`

**Contexto tienda:** ya vendemos singles STEM + **2 packs live** (STEM `4550715355`, Physics `4550737656`); ads concentrados en winners; 30 listings pausados.

---

## Resumen ejecutivo

| Prioridad | Producto | Señal | Acción |
|---|---|---|---|
| **#1 BUILD** | **Physics Formula Poster Set** (set of 6–8 plates, $9.99–$14.99) | API: solo **5 listings**, score **80.5**, fav avg ~70, 80% digital | Nuevo set “classroom formula” (kinematics, energy, EM, quantum, waves…) en identidad scientific plate |
| **#2 BUILD** | **Trigonometry Poster Set** (+ Unit Circle hero) | API: **16 listings**, fav avg **85**, score **77.6**, $13 med | Bundle Unit Circle (ya vendemos) + identidades + law of sines/cosines + graphs |
| **#3 BUILD** | **Chemistry Wall Art Set of 6** | API: **480 listings** pero fav avg **194**, score **82.3**, digital 80% | Línea adyacente: glassware, orbital, periodic aesthetic, molecules — code/render moat |
| **#4 SCALE** | **Math Teacher Gift Set / Classroom pack** | “math poster pack” **85.8**, “math teacher gift set” **77.5**, eRank classroom decor con volumen | Empaquetar Famous Equations + Unit Circle + Lab Notebook + 1 formula sheet en un gift listing $19–24 |
| **#5 DEEPEN** | **Strange Attractors / Fractal set of 6** | Fractal set fav avg **526** (score 79); attractors 77 listings score 70; moat de código | Set cohesivo dark/cream (ya hay singles) |

### Ya cubierto (no reinventar)

| Keyword API | Score | Status |
|---|---:|---|
| stem wall art pack | **87.5** | **Live** `4550715355` |
| math poster pack | **85.8** | **Live** STEM pack (SERP top) |
| physics poster pack | **69.5** | **Live** `4550737656` (solo 10 comps en API — gap real) |
| schrodinger equation poster | **83.3** | Single + packs |
| platonic solids / polyhedra | 68.9 / 78.3 | Platonic listing + plan polyhedra |

---

## Señal eRank (Edge)

**Limitación:** sesión eRank con *Session Limit* / sparse rows — la mayoría de long-tails STEM salen **0** o sin Avg. Eso es típico: **para STEM confiar en API (favs + #listings)**.

| Keyword | Jul 2026 | Avg/mo | Mom. | Comp | KD | Lectura |
|---|---:|---:|---:|---:|---:|---|
| **science classroom decor** | **1200** | 106 | **11.3×** | 12.8k | 100 | Spike fuerte BTS/classroom — empuja packs + classroom SEO |
| math classroom decor | 10* | 315 | 0.03 | 10.2k | 75 | Avg sólido; latest ruidoso |
| stem classroom poster | — | — | — | 2.3k | — | Comp. moderada en bulk |
| schrodinger equation poster | — | — | — | **20** | — | Muy azul océano en eRank |

\* latest 10 a veces es placeholder eRank.

**Implicación:** títulos/tags de packs y sets deben empujar **classroom / teacher / science decor** (no solo “math art”).

---

## Señal API Etsy (Top oportunidades nuevas)

| Keyword | Listings | Fav avg | $ med | Digital | Score | Por qué importa |
|---|---:|---:|---:|---:|---:|---|
| **physics formula poster set** | **5** | 70 | $10 | 80% | **80.5** | Casi vacío + precio set |
| **trigonometry poster set** | **16** | 85 | $13 | 75% | **77.6** | Bajo comp; apila Unit Circle |
| **chemistry wall art set** | 480 | **194** | $14 | 80% | **82.3** | Demanda alta; adyacente STEM |
| math wall art set of 6 | 134 | 71 | $8 | 100% | **80.8** | Formato Famous Equations gana |
| biology cell poster set | **53** | 70 | $15 | 33% | **73.6** | Nicho abierto digital limpio |
| strange attractor wall art | 77 | 34 | $8 | 70% | **70.0** | Moat código; set > single |
| polyhedra wall art | 71 | 88 | $20 | 50% | **78.3** | Expandir Platonic a set-of-6 |
| math teacher gift set | 830 | **152** | $8 | 43% | **77.5** | Gift AOV; bundle digital |

---

## Plan de producto (orden de build)

### 1) Physics Formula Poster Set — **siguiente build**
- **Qué:** 6–8 plates (Displacement/Velocity/Accel, Energy, Momentum, EM Maxwell summary, Waves, Thermo/Quantum intro) en familia visual Scientific Plate.
- **Precio:** $9.99–$12.99 set (API med ~$10).
- **SEO:** “physics formula poster set”, “physics classroom poster”, “science classroom decor”.
- **Ads:** ON cuando tenga 1–2 semanas orgánicas o si el pack Physics ROAS aguanta.
- **Esfuerzo:** 1–2 días (plantilla plate ya existe).

### 2) Trigonometry Poster Set
- Unit Circle (existente) + Unit Circle values + SOHCAHTOA + graphs + identities sheet.
- **Precio:** set $9.99 o pack $12.99.
- **Listings API:** 16 → room.

### 3) Chemistry Wall Art Set of 6
- Estética lab/minimal (no stock clipart): glassware still-life, orbitals, bonds, periodic aesthetic, titration, molecule.
- **Precio:** $11.99–$14.99.
- Abre vertical “science” sin salir del brand.

### 4) Math Teacher Gift Set ($19–24)
- No arte nuevo: re-bundle Famous Equations + Unit Circle + Lab Notebook + 1 grid pack PDF.
- Keyword “math teacher gift set” / classroom decor spike.

### 5) Strange Attractors Set of 6 (dark or cream)
- Lorenz, Rössler, Thomas, Halvorsen, Chen, Aizawa — ya hay renderers en books.
- Menor volumen eRank; alta diferenciación.

---

## Qué **no** priorizar

| Idea | Motivo |
|---|---|
| Más packs genéricos STEM | Ya tenemos 2 live; SERP top ya es nuestro |
| Coffee table book #3 | API `math art book coffee table` débil (score 34) hasta vender Beauty |
| CS poster set | Score 44, poco fav |
| Long-tail fourier/chladni solo | Favs bajos en sample; mejor dentro de physics formula set |
| eRank-only mainstream (homeschool planner, etc.) | Fuera de marca / saturado |

---

## Matriz decisión (regla de 3)

| Criterio | Formula set | Trig set | Chemistry set | Teacher gift bundle |
|---|---|---|---|---|
| Demanda (favs/API) | Media-alta | Alta | **Alta** | Alta |
| Competencia | **Muy baja (5)** | Baja (16) | Media | Media |
| Fit / moat | Excelente | Excelente | Bueno (nuevo dominio) | Excelente (zero art) |
| Velocidad | 1–2 d | 1–2 d | 2–4 d | **0.5 d** |
| AOV | $10–13 | $10–13 | $12–15 | **$19–24** |

**Si querés cash esta semana:** Teacher Gift Bundle (re-pack).  
**Si querés moat + gap de mercado:** **Physics Formula Poster Set**.  
**Si querés expansión de categoría:** Chemistry set.

---

## Artefactos

```
research/wave16_candidate_keywords.txt
research/wave16_etsy_opportunities.json
research/wave16_etsy_opportunities.csv
research/wave16_erank_bulk.json
research/wave16_erank_bulk.csv
research/wave16_erank_batch{1,2,3}.png
research/wave16_opportunity_report.md   # auto eRank
research/wave16_winner_recommendation.md  # este archivo
```

## Siguiente paso sugerido

1. **Build Physics Formula Poster Set** (MVP 6 plates + listing $11.99).  
2. En paralelo: **Math Teacher Gift Set** listing (re-bundle, $19.99).  
3. SEO refresh de packs con “science classroom decor” / “physics classroom poster”.  
4. Re-run eRank cuando la sesión no esté en Session Limit (volumen classroom).
