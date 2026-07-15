# Wave 3 — Oportunidades amplias (eRank + Etsy API)

**Fecha:** 2026-07-14  
**Scope:** Más allá de physics plates — stationery STEM, classroom, digital stickers, astronomy, study tools  
**Artefactos:** `wave3_broad_candidates.json`, `wave3_refined.json`, bulk eRank + Keyword Tool

---

## Método

1. **40 keywords** Etsy API (`scan_wave3_broad.py`) — demanda vía favoritos / listings / % digital  
2. **Bulk eRank** 20 terms — Avg. Searches, CTR, Competition, KD  
3. **Refined** 30 long-tails + SERP manual (descartar falsos positivos)  
4. **Trend Buzz** Etsy daily — casi todo mass-market (halloween, tshirt, pokemon); **poco útil** para MathRelaxing

---

## Señal estrella eRank

### `lab notebook printable`

| Métrica eRank | Valor | Lectura |
|---------------|------:|---------|
| Avg. Searches | **98** | Demanda real (no long-tail unknown) |
| Avg. Clicks | **97** | Casi 1:1 search→click |
| CTR | **99%** | Intent altísimo |
| Competition | **55** | Mercado vacío |
| KD | muy bajo (~1–22 según vista) | Fácil de rankear |

**SERP actual:** listings flojos (0–38 favs), mezcla de kids worksheets, medical lab trackers y un par de lab notebooks mediocres. **Nadie domina con marca premium STEM.**

**Fit MathRelaxing:** alto — ya tienes graph paper bundles, STEM notebooks y planners. Producto = **stationery**, no wall art (diversifica catálogo).

**Producto propuesto:**  
*STEM Lab Notebook — Printable & GoodNotes*  
- Portada + índice  
- Scientific method log (hypothesis → procedure → data → conclusion)  
- Data tables + graph paper inserts  
- Chemistry / physics / bio section dividers (estética MathRelaxing navy/cream)  
- PDF print + PDF GoodNotes  
- Precio **$6.99–8.99**

---

## Shortlist (prioridad)

| # | Producto | Tipo | eRank / Etsy | Por qué |
|---|----------|------|--------------|---------|
| **1** | **Lab Notebook printable** | Stationery PDF | 98 searches · 55 comp · CTR 99% | Mejor ratio demanda/comp de la wave |
| **2** | **Unit Circle scientific plate** | Wall art (plate) | ~17–60 listings · favs 86–176 en tops | Classroom + plate pipeline; hueco vs Euler (ya tienes) |
| **3** | **Math formula cheat sheet set** | Study PDF / posters | 177 listings · digital 100% | Exámenes / AP / calc — ticket $3–8, fácil de generar LaTeX |
| **4** | **STEM study flashcards GoodNotes** | Digital study | 177 listings · tops con 463 fav (bio) | Math/physics formula cards aesthetic |
| **5** | **Classroom math poster set** | Bundle wall art | 899 listings · **499–980 favs** en tops | Demanda alta; más competencia; SEO “classroom” + “bulletin board” |

### eRank bulk (muestra)

| Keyword | Searches | Competition | Nota |
|---------|----------|-------------|------|
| lab notebook printable | **98** | **55** | ★ pick |
| study planner goodnotes | **190** | 7,036 | Volumen pero saturado; ya tienes planners |
| habit tracker printable | 168 | 42,776 | Evitar |
| unit circle poster | &lt;20 | 60 | Long-tail classroom |
| moon phase wall art | &lt;20 | 13,150 | Saturado |
| circuit board wall art | &lt;20 | 625 | Más physical/canvas |

---

## Descartados / trampa de SERP

| Keyword | Problema |
|---------|----------|
| waveform art print | Es **custom soundwave de canciones** (QR), no abstract math |
| graph theory poster | SERP contamina con music theory / economics; búsquedas reales nulas |
| unit circle poster printable (API score 86) | Mezcla con “circle time” preschool |
| science digital stickers | Clipart random; keyword sucia |
| ipad wallpaper aesthetic | Genérico, no STEM |
| laser cut mandala svg | Saturado, fuera de marca |
| graduation gift engineer | Physical gifts, 0% digital |

---

## Relación con catálogo actual

| Ya cubierto | No abrir más de lo mismo |
|-------------|---------------------------|
| Physics wall art plates | Schrödinger draft + Maxwell #1 |
| Happy chemicals / therapy office | Ya aparece en SERP psychology |
| STEM graph paper / planners | No otro planner genérico GoodNotes (7k comp) |
| Coloring / iPad CBN | Optimizar listings > otro PDF genérico |

**Gap real:** stationery **científica** (lab notebook) y **classroom reference** (unit circle / formula sheets) con estética premium.

---

## Recomendación de ejecución

### Pick A (recomendado) — Lab Notebook
- Nuevo vertical (stationery)  
- Mejor métrica eRank de la wave  
- Competencia débil → fácil #1–3 orgánico  
- Build: 1–2 días (PDF multi-página + previews)

### Pick B — Unit Circle plate  
- Reutiliza generador scientific-plate + LaTeX  
- Classroom + dorm STEM  
- Complementa Euler (ya en shop)

### Pick C — Formula cheat sheet pack (AP Calc / Physics)  
- Rápido con LaTeX  
- Temporada escolar / back-to-school  
- Precio bajo, volumen potencial

---

## No hacer

- Perseguir Trend Buzz (halloween, tshirts, pokemon)  
- Otro habit tracker / planner genérico  
- Custom soundwave (fulfillment y soporte)  
- Ampliar ads en SKUs sin señal (regla ROAS vigente)

---

## Next step

Elegir **A / B / C** (o combo A+B) y generar draft Etsy.

---

## Ejecutado — Pick A

| Campo | Valor |
|-------|--------|
| Producto | STEM Lab Notebook |
| Listing draft | **`4538070573`** |
| Precio | $7.99 |
| Generator | `generate_lab_notebook.py` |
| Assets | `lab_notebook/STEM_Lab_Notebook.pdf` + 6 previews |
| Fecha | 2026-07-14 |

