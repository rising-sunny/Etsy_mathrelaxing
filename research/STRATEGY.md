# Product Opportunity Strategy — MathRelaxing

**Shop:** TheMathRelaxing (Etsy shop_id `66586766`)  
**Stack:** Etsy API v3 + eRank (Playwright) + **config-driven discovery**  
**Wave 1:** 2026-07-14 — 60 keywords Etsy + 20 bulk eRank  

## Pipeline recomendado (desde 2026-07-24)

Ya no hace falta editar listas hardcodeadas en tres `.py`. Flujo único:

| Pieza | Rol |
|-------|-----|
| `research/config/winners.yaml` | Seeds, modifiers, fit, umbrales, shop aliases — **editas aquí** |
| `research/find_winners.py` | Orquestador: expande → mine tags → API Etsy → marca “ya en tienda” → rank → informe |
| `product_finder.py` | Scoring / analyze_keyword (motor reutilizado) |
| `research/erank_edge_bulk.py` | eRank Edge (llamado opcionalmente solo para top-N) |

```bash
# Solo ver keywords generadas (sin gastar API)
python research/find_winners.py --expand-only

# Scan Etsy completo desde config
python research/find_winners.py

# Añadir semillas al vuelo + eRank en top 15
python research/find_winners.py --seeds "adhd planner" "habit tracker" --erank

# Solo un archivo de ideas, sin expansión
python research/find_winners.py --file research/my_ideas.txt --no-expand --no-mine
```

Salida: `research/winners_YYYYMMDD_HHMM.{json,csv,_report.md}`

## Estado de la tienda (eRank dashboard)

| Métrica | Valor |
|---------|-------|
| Sales | 2 |
| Active listings | 62 |
| Sales rank | ~1,229 / 2.9M global |

Conclusión: catálogo amplio, tracción baja → **priorizar menos productos con demanda real y SEO/título afinado**, no más volumen a ciegas.

## Cómo decidimos

1. **Etsy API** (`product_finder.py`): #listings, favorites medios del top, precio mediano, % digital, fit de marca.
2. **eRank Bulk/Keyword Tool**: Avg. Searches, KD, Competition (cuota ~100 búsquedas/día).
3. **Score compuesto** → BUILD / TEST / WATCH / HARD / WEAK / SKIP.
4. **Revisión humana** de top listings (evitar falsos positivos tipo “Julia” = santo, no Julia set).

Artefactos:
- `research/opportunities_wave1.json` / `.csv`
- `research/erank_bulk_wave1.csv`
- `product_finder.py`

```bash
python product_finder.py --out research/opportunities_wave1.json
python product_finder.py --erank research/erank_bulk_wave1.csv --out research/merged.json
python product_finder.py --kw "your keyword" --no-seeds
```

## Top oportunidades (Wave 1) — accionables

### Tier A — BUILD primero (demanda + fit + producible)

| # | Keyword | Score | Listings | Fav~ | $~ | Producto MathRelaxing |
|---|---------|------:|---------:|-----:|---:|------------------------|
| 1 | **molecule wall art printable** | 91.7 | 272 | 93 | $4.50 | Set de prints: moléculas / hormonas / “happy chemicals” estilo minimal MathRelaxing |
| 2 | **science digital notebook** | 85.7 | 521 | 159 | $3.20 | Notebook STEM GoodNotes (ya tienes línea STEM) — **revisar que top no sea clipart** |
| 3 | **dna art print digital** | 81.5 | 1042 | 77 | $4.25 | Helix / DNA abstract generative print pack |
| 4 | **physics wall art printable** | 81.0 | 561 | 62 | $5.00 | Posters: ecuaciones + diagramas (Chladni, ondas, óptica) — alinea con listing Chladni ya en shop |
| 5 | **neural network art print** | 77.5 | 421 | 88 | $19 | Ya tienes neural PDF; **pack de wall art** a $6–10 digital puede competir mejor en precio |
| 6 | **strange attractor art print** | 74.2 | 28 | 56 | $18 | Lorenz / Thomas / Clifford — **nicho vacío**, ya generas attractors |
| 7 | **seamless loop video download** | 74.9 | 597 | 56 | $8 | Ya tienes Thomas/Julia/Voronoi loops — SEO + packs temáticos |
| 8 | **julia set / mandelbrot art print** | 74/64 | 67/90 | 67/15 | var | Prints digitales (no solo coloring) — cuidado keyword “julia” genérica |

### Tier B — TEST (buena apuesta, validar copy/SEO)

- `math poster digital download` (score 69) — saturado en “classroom posters”; diferenciar con **aesthetic dark/gold MathRelaxing**, no pastel teacher.
- `math digital planner goodnotes` (63) — competencia baja (72 listings).
- `fibonacci spiral printable` (63) — fácil de generar; validar búsquedas eRank del parent `fibonacci` / `golden ratio`.
- `goodnotes coloring book` (62) — puente a iPad bundles existentes.
- `sacred geometry coloring book` (58) — ya vendes esto; **optimizar listings actuales** > crear otro PDF genérico.
- `phyllotaxis art print` (66) — 7 listings, favorites decentes → blue ocean pequeño.

### Tier C — evitar como “nuevo producto genérico”

| Keyword | Por qué no |
|---------|------------|
| adult/coloring book digital download | 90k–118k listings, HARD |
| flower of life / constellation genéricos | Demanda alta pero custom star maps y farmhouse art contaminan SERP |
| procreate coloring pages | 103 búsquedas eRank pero KD 99 y 9.8k competencia |
| geometric coloring pages | KD 100, saturado, intent bajo |

## Insight eRank clave

Muchas long-tails **MathRelaxing** tienen Avg. Searches `< 20` o `Unknown`. Eso **no** significa “no vender”:

- El comprador busca el **parent** (`sacred geometry`, `physics poster`, `molecule art`) y elige el listing bonito.
- Estrategia: **título = parent demand + diferenciador brand**, tags = long-tail técnica.

Ejemplo eRank (Keyword Tool):
- `sacred geometry coloring book` → &lt;20 searches, 110 competition, KD 87  
- `sacred geometry` → ~1,079 searches, 38k competition, CTR alto  

## Plan de ejecución sugerido (próximos pasos)

1. **Validar top 5 listings** de cada Tier A en eRank (Shop Info / listing URL) — ver ventas estimadas y tags.
2. **Elegir 2 MVPs** (recomendación):
   - **A)** Molecule / DNA / Physics **printable wall art set** (rápido, precio $4.99–6.99).
   - **B)** **Strange attractors print pack** o **loop pack** (aprovecha generadores existentes).
3. Generar con `brand.py` + plantillas; draft vía `products_catalog.py`.
4. Optimizar con eRank AI Listing Helper + Health Check (sync listings primero).
5. Segunda oleada de keywords en Bulk (cuota restante hoy ~98/100).

## Falsos positivos a filtrar a mano

- `julia set art print` → resultados “St Julia” religiosos.
- `science digital notebook` → clipart “back to school”.
- `graph theory poster` → a veces “supply/demand” economics (aún así el nicho math poster es real).
- `chemistry periodic table art` → mucha merch de camisetas PNG.

Siempre abrir 3–5 top listings antes de BUILD.
