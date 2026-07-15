# MathRelaxing — Estándares de Producto (LEER PRIMERO)

Este documento evita que cada producto se construya desde cero. **Antes de crear
cualquier producto nuevo, identifica su TIPO abajo, importa `brand.py` + la
plantilla del tipo, y reutiliza el builder.** No vuelvas a hard-codear colores,
la franja del logo, ni la estructura de los libros.

## Arquitectura del código

```
brand.py                     ← FUENTE ÚNICA de identidad visual (colores, tipografía,
                               franja negra + logo, portada, .swatches, encode mp4)
template_coloring_book.py    ← builder de libros para colorear (PDF + previews)
template_ipad_bundle.py      ← builder del bundle iPad de 5 archivos + 3 previews
mathrelaxing_logo.png        ← logo oficial (infinito + wordmark), NO regenerar
products_catalog.py          ← copy, precio, tags, taxonomy; sube borradores a Etsy
etsy_manager.py / auth.py    ← API Etsy v3 (crea SIEMPRE en estado draft)

Implementaciones de referencia (copiar el patrón):
  generate_celtic_knots.py   ← libro para colorear (motor + config delgada)
  build_celtic_ipad.py       ← bundle iPad (config delgada sobre la plantilla)
  build_celtic_ipad_video.py ← promo mp4 (coloreo progresivo)
```

## Reglas de marca invariables (aplican a TODO)

- **Franja negra inferior con el logo** (infinito + "MathRelaxing") en toda
  portada y preview. Se dibuja con `brand.footer_band` / `brand.add_logo` desde
  `mathrelaxing_logo.png`. Nunca redibujar el logo a mano.
- **Tipografía**: títulos en serif; nombre del producto en `brand.CREAM`,
  subtítulo en `brand.GOLD`. Cuerpo en sans.
- **Portadas de libros**: fondo oscuro temático por producto (`theme_bg`),
  emblema dorado arriba, marca de agua tenue opcional. Usar `brand.cover`.
- **Previews de bundles iPad**: fondo fijo `brand.IPAD_NAVY`, acento
  `brand.IPAD_TEAL`. Usar los scaffolds `brand.ipad_fig/ipad_frame/ipad_logo`.
- **Descripciones** (en `products_catalog.py`) terminan con la línea
  `brand.COPYRIGHT`. **No** incluir `mathrelaxing.store` ni URLs externas
  en copy de Etsy (política de la plataforma / riesgo de flags).
- **Publicación**: SIEMPRE se crea el listing en `draft`. La activación es manual.
- **Cover del listing = cuadrada** (8×8 → Etsy recorta 1:1). La página 1 del PDF
  es la versión portrait; son distintas a propósito.

---

## Tipos de producto

### 1. Libro para colorear — PDF imprimible
- **Ejemplos**: Fractal Flora, Voronoi Gardens, Hyperbolic Gardens, Islamic
  Geometry, Celtic Knot, Mathematical Tangle, Sacred Harmonics.
- **Estructura**: PDF 8.5×11, 52 págs (portada + "The Mathematics" + 50 diseños).
- **Archivos Etsy**: 1 PDF (`<prefix>_digital.pdf`) + video promo opcional.
- **Imágenes**: `<prefix>_cover.jpg` (cuadrada) + `<prefix>_page_01..07.jpg`.
- **Precio**: $6.99 · **taxonomy_id**: 2078 (`TAXONOMY["coloring_book"]`).
- **Builder**: `template_coloring_book.build_book(cfg, render_design, emblem, watermark)`.
  El producto solo aporta: `render_design(n)->fig`, `emblem`, `watermark`, texto.
- **Referencia**: `generate_celtic_knots.py`.

### 2. Libro color-by-number — PDF imprimible
- **Ejemplo**: Sacred Geometry.
- Igual que el tipo 1, pero `render_design(n)` dibuja facetas numeradas + una
  pequeña guía de paleta. Mismo builder, mismo precio/taxonomy (a veces $8.99).

### 3. Edición iPad — bundle GoodNotes/Notability/Procreate
- **Ejemplos**: todos los `*_ipad`.
- **5 archivos EXACTOS** (límite Etsy): PDF hipervinculado (índice tap-to-jump +
  50 diseños), 2 ZIPs de PNGs transparentes 300 dpi, `.swatches` (30 colores),
  `How_to_use_on_iPad.pdf`.
- **Imágenes**: 3 previews navy (hero / included / two-ways) + video promo.
- **Precio**: $9.99–11.99 · **taxonomy_id**: 339 (`TAXONOMY["ipad_coloring"]`).
- **Builder**: `template_ipad_bundle.build(cfg, render_design_fig, line_png, colored_png)`.
  El producto aporta: `render_design_fig(n)`, la paleta, y 2 showcases (línea +
  coloreado — el coloreo es específico del producto).
- **Referencia**: `build_celtic_ipad.py` (+ `build_celtic_ipad_video.py` para el mp4).

### 4. Animación seamless loop — MP4
- **Ejemplos**: Thomas / De Jong / Julia / Voronoi Cell attractors.
- **Estructura**: MP4 1080×1080, ~60fps, loop perfecto. El **archivo de descarga
  es el MP4 limpio 1080p**; el **video del listing es un preview 540p CON marca de
  agua** (el producto ES un video → si subes el limpio como preview, lo copian).
- **Imágenes**: 3 previews (hero / specs / loop).
- **Precio**: $4.99–5.99 · **taxonomy_id**: 2078 (`TAXONOMY["digital_art"]`).
- **Builder**: usar `brand.encode_mp4` para el encode. (Sin plantilla dedicada aún;
  seguir el patrón de `build_celtic_ipad_video.py` para frames + encode.)

### 5. Art print generativo — imagen estática
- **Ejemplos**: Newton / Clifford / Lorenz attractors.
- **Estructura**: imagen de alta resolución (archivo de descarga) + previews.
- **Precio**: $5.99–6.99 · **taxonomy_id**: 2078 (`TAXONOMY["digital_art"]`).
- Reutiliza `brand` para previews/branding.

### 6. Notebook digital STEM — PDF hipervinculado
- **Ejemplo**: STEM Digital Notebook (grids con pestañas).
- **Estructura**: PDF landscape 4:3 hipervinculado (tabs tap-to-jump).
- **Imágenes**: 4 previews + video.
- **Precio**: $8.99 · **taxonomy_id**: 12476 (`TAXONOMY["planner_template"]`).

---

## Checklist para publicar un producto nuevo

1. Identifica el tipo arriba e importa `brand` + la plantilla correspondiente.
2. Escribe una config delgada + `render_design` (patrón: los scripts `*_celtic*`).
3. Genera archivos y **revisa visualmente** portada y previews antes de subir.
4. Añade la entrada a `products_catalog.py` (title, description con © + store,
   price, taxonomy_id, tags ≤13/≤20 chars, images, files, video).
5. `python products_catalog.py dry-run <slug>` → luego `upload <slug>`.
6. Queda en **draft**; el usuario lo activa desde Etsy.
