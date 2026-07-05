# STEM Focus Planner - Status & Continuation Guide

**Última actualización:** 2026-07-05  
**Estado:** v3 subida a Etsy como borrador (ID 4531825862) — activación manual pendiente

---

## Contexto Inicial

El usuario solicitó mejorar el STEM Focus Planner existente basándose en el análisis de un best-seller de Etsy (listing 4329390689). El objetivo era diferenciarse de la competencia genérica con una propuesta STEM/MathRelaxing.

**Producto original:** 21 páginas, diseño básico, sin stickers  
**Producto mejorado:** 35 páginas, diseño elegante, 14 stickers matemáticos

---

## Correcciones Realizadas (v2.1)

### 1. ✅ Index page — HTML entity fix
- Reemplazado `&bull;` (no renderizable en PDF) por `·` (Unicode middle dot)
- Features actualizadas: 6 monthly, 6 weekly, 10 daily, 4 académicas, fórmulas
- Layout de botones recalculado: 3 columnas × 5 filas para 15 secciones sin superposición

### 2. ✅ Stickers — calidad mejorada
- DPI corregido: `figsize=(5.12, 5.12), dpi=100` = exactamente 512×512px
- Z-order arreglado: sombra dibujada ANTES del símbolo
- Símbolos más grandes: fontsize 120→200 (símbolos), 36→60 (ecuaciones)
- Ecuaciones con LaTeX mathtext: `$e^{i\pi}+1=0$`, `$a^2+b^2=c^2$`, `$\frac{dy}{dx}$`, `$\sum_{i=1}^{n} i$`

### 3. ✅ Previews — datos corregidos
- **Preview 1 (Hero):** Muestra página Index en lugar de Yearly Overview
- **Preview 2 (Sections):** "35 hyperlinked pages", conteos correctos, incluye plantillas académicas y stickers
- **Preview 3 (STEM):** Renderiza Research Log y Cornell Notes reales (ambos con contenido)
- **Preview 4 (Nav):** 8 tabs laterales + HOME, labels legibles, 8 botones de navegación

### 4. ✅ Catálogo — errores corregidos
- Tags reducidos de 16 a 13 (límite Etsy)
- Notas corregidas: "35 páginas" (no "40+")

---

## Archivos Modificados

1. `build_stem_planner.py` — Index page, previews, build_previews()
2. `generate_math_stickers.py` — DPI, z-order, LaTeX, tamaños
3. `products_catalog.py` — Tags, notas

## Archivos Regenerados

1. `stem_planner/STEM_Focus_Planner_v2.pdf` — 35 páginas
2. `stem_planner/stickers/*.png` — 14 stickers (512×512px)
3. `stem_planner/previews/stem_planner_preview_*.jpg` — 4 previews

---

## Estado Actual del Producto

**PDF:** `stem_planner/STEM_Focus_Planner_v3.pdf` (35 páginas — v3 reemplazó a v2 por locks de archivo, ver checklist abajo)
**Stickers:** 14 archivos PNG en `stem_planner/stickers/`, empaquetados en `stem_planner/math_stickers.zip` para respetar el límite de 5 archivos de Etsy
**Etsy:** Subido como borrador (ID 4531825862) — activación manual pendiente desde el panel de Etsy
**Precio:** $5.99 (ajustado para ser competitivo — ver `products_catalog.py`, nota del producto)

---

## Comandos Útiles

### Regenerar stickers:
```bash
python generate_math_stickers.py
```

### Regenerar PDF:
```bash
python build_stem_planner.py
```

### Subir a Etsy:
```bash
python products_catalog.py upload stem_focus_planner
```

---

## Pendiente

1. **Activar el listing** desde el panel de Etsy (borrador ID 4531825862 ya subido con PDF v3 y stickers en ZIP)

---

## Brand MathRelaxing

**Colores:**
- GOLD: #C9A227
- CREAM: #F5F1E6
- NAVY: #12172E
- MUTED: #8C9199

**Estética:** Minimalista, académica, sofisticada, orientada a mentes analíticas

---

## Contacto/Continuación

Si otra IA agéntica continúa este trabajo, debe:
1. Leer este archivo completo
2. Revisar el estado actual en Etsy
3. Seguir las convenciones de brand MathRelaxing
4. Mantener la estructura de archivos existente
5. Actualizar este archivo con cualquier cambio adicional

**Directorio base:** `G:\Mi unidad\Etsy\`  
**API de Etsy:** `etsy_token.json`  
**Catálogo:** `products_catalog.py`
- [x] Cream background color lightened for better contrast.
- [x] Dot grid transparency increased (lighter color).
- [x] Index page beautified (centered features list, reversed to natural order).
- [x] PDF output renamed to v3 to bypass file locks and catalog updated.
- [x] Added 3-letter abbreviations to side navigation tabs for clear identification.
- [x] Final PDF (v3) uploaded successfully to Etsy as a draft (ID: 4531825862).
- [x] Promo video re-rendered (296 frames) to include cinematic zooms, panning, and handwriting simulation ('Submit Research Paper').
