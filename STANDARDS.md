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
  `brand.COPYRIGHT` y `brand.STORE` (mathrelaxing.store).
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
- **Precio**: $3.99 (nivelado — todos los libros PDF al mismo precio) · **taxonomy_id**: 2078 (`TAXONOMY["coloring_book"]`).
- **Builder**: `template_coloring_book.build_book(cfg, render_design, emblem, watermark)`.
  El producto solo aporta: `render_design(n)->fig`, `emblem`, `watermark`, texto.
- **Referencia**: `generate_celtic_knots.py`.

### 2. Libro color-by-number — PDF imprimible
- **Ejemplo**: Sacred Geometry.
- Igual que el tipo 1, pero `render_design(n)` dibuja facetas numeradas + una
  pequeña guía de paleta. Mismo builder, mismo precio ($3.99) y taxonomy.

### 3. Edición iPad — bundle GoodNotes/Notability/Procreate
- **Ejemplos**: todos los `*_ipad`.
- **5 archivos EXACTOS** (límite Etsy): PDF hipervinculado (índice tap-to-jump +
  50 diseños), 2 ZIPs de PNGs transparentes 300 dpi, `.swatches` (30 colores),
  `How_to_use_on_iPad.pdf`.
- **Imágenes**: 3 previews navy (hero / included / two-ways) + video promo.
- **Precio**: $5.99 (nivelado — todos los bundles iPad al mismo precio) · **taxonomy_id**: 339 (`TAXONOMY["ipad_coloring"]`).
- **Builder**: `template_ipad_bundle.build(cfg, render_design_fig, line_png, colored_png)`.
  El producto aporta: `render_design_fig(n)`, la paleta, y 2 showcases (línea +
  coloreado — el coloreo es específico del producto).
- **Referencia**: `build_celtic_ipad.py` (+ `build_celtic_ipad_video.py` para el mp4).

### 4. Animación seamless loop — MP4
- **Ejemplos**: Thomas / De Jong / Julia / Voronoi Cell attractors + Phyllotaxis Bloom
  (los 5 ya construidos). No todo tiene que ser un atractor caótico: Phyllotaxis
  Bloom es un campo de partículas (posición fija por ángulo dorado, solo brillo/
  radio animados) — más simple y rápido de renderizar que iterar un sistema
  caótico, y una alternativa válida cuando se quiere un mood más "sereno" que
  "caótico".
- **Estructura**: MP4 1080×1080, ~30-60fps, loop perfecto. El **archivo de descarga
  es el MP4 limpio 1080p**; el **video del listing es un preview 540p CON marca de
  agua** (el producto ES un video → si subes el limpio como preview, lo copian).
- **⚠️ El archivo de descarga debe subirse como .mov, no .mp4**: la app de Etsy
  ("Archivos digitales" → subida manual, verificado 2026-07-05) solo acepta
  `.bmp .doc .gif .jpeg .jpg .mobi .mov .mp3 .mpeg .pdf .png .psp .rtf .stl .txt
  .zip .ePUB .iBook` — `.mp4` NO está en la lista. Convertir con
  `ffmpeg -i archivo.mp4 -c copy archivo.mov` (remux, sin recodificar, cero
  pérdida de calidad ni de tamaño). El video del listing (preview con marca de
  agua) sí puede subirse como .mp4 normalmente — esto solo aplica al archivo
  digital descargable.
- **Loop perfecto**: variar el/los parámetro(s) del sistema con una frecuencia
  angular entera respecto al total de frames (Voronoi), o recorrer una
  trayectoria CIRCULAR en el espacio de parámetros con `cos`/`sin` de la misma
  fase (De Jong) — nunca un solo `sin` en fase para dos parámetros distintos,
  porque retraza la misma trayectoria de ida y vuelta en vez de mutar en una
  sola dirección (bug detectado y corregido en `generate_dejong_loop.py`).
- **Imágenes**: 3 previews (hero / specs / loop).
- **Precio**: $4.99–5.99 · **taxonomy_id**: 2078 (`TAXONOMY["digital_art"]`).
- **Builder**: usar `brand.encode_mp4` para el encode. (Sin plantilla dedicada aún;
  seguir el patrón de `generate_dejong_loop.py` o `build_celtic_ipad_video.py` para
  frames + encode.)

### 5. Art print generativo — imagen estática
- **Ejemplos**: Lorenz (id=4528168404) y Clifford (id=4528164675) — publicados
  fuera de este pipeline, sin script generador ni backup local (ver gotcha de
  API abajo: no se puede recuperar el archivo vendible original por API).
  Rössler (`attractor_prints/generate_rossler_print.py`) es el primero
  construido y trackeado en el repo.
- **Carpeta**: `attractor_prints/<nombre>/` — un subdirectorio por diseño.
- **Estructura**: 3 archivos JPG (mismo diseño, 3 variantes de color) — NO 1
  archivo. `images` y `files` en el catálogo apuntan a los mismos 3 JPG.
- **Sin franja/logo de marca** en el archivo vendible — a diferencia de TODO
  el resto del catálogo. Es a propósito: es wall art para enmarcar, no una
  página de muestra de un producto multi-página. No usar `brand.footer_band`
  aquí.
- **Resolución**: print-ready a 300dpi (ej. 5400×7200 = 18×24in retrato,
  5400×5400 = 18×18in cuadrado — la relación de aspecto depende de la forma
  natural del atractor, no hay que forzar un formato fijo).
- **Precio**: $5.99 · **taxonomy_id**: 2078 (`TAXONOMY["digital_art"]`).
- **Técnica de render** (`generate_rossler_print.py` como referencia):
  - Mapas discretos (De Jong, Clifford, Voronoi) → MUCHAS trayectorias en
    paralelo, POCAS iteraciones cada una (cada "kick" del mapa decorrelaciona
    rápido).
  - **Flujos continuos / ODEs (Lorenz, Rössler, Aizawa, Chen, Halvorsen...)
    → al revés**: POCAS trayectorias, MUCHÍSIMOS pasos (cientos de miles) —
    una trayectoria necesita dar muchas vueltas para revelar la estructura de
    bandas plegadas; con pocos pasos solo se traza un anillo liso y borroso.
  - Acumular en histograma DURANTE la integración (streaming, `np.add.at` en
    cada paso), nunca guardar todos los puntos — con cientos de miles de
    pasos la memoria explota si se guarda el historial completo.
  - Proyección 2D: para cada atractor investigar cuál plano (X-Y, X-Z, Y-Z)
    da la vista "clásica" reconocible — no es siempre la misma para todos los
    sistemas (Rössler: X-Y; Lorenz: X-Z típicamente).
  - Encuadre: usar percentiles de las coordenadas reales (no un bounding box
    fijo adivinado) para centrar automáticamente. Un crop post-proceso al
    bounding box del contenido (con margen ~20-25%) sirve si el encuadre
    inicial quedó con demasiado espacio negro muerto.

### 6. Notebook digital STEM — PDF hipervinculado
- **Ejemplo**: STEM Digital Notebook (grids con pestañas).
- **Estructura**: PDF landscape 4:3 hipervinculado (tabs tap-to-jump).
- **Imágenes**: 4 previews + video.
- **Precio**: $8.99 · **taxonomy_id**: 12476 (`TAXONOMY["planner_template"]`).

### 7. Planner digital all-in-one — PDF hipervinculado masivo
- **Ejemplo**: The Life Planner (`life_planner/`).
- **Estructura**: PDF landscape 4:3, 500+ páginas 100% hipervinculadas. Navegación
  **hub-and-spoke**: dashboard → hubs de sección → plantillas, con barra de pestañas
  lateral fija en cada página + prev/next en el calendario. Calendario completo
  (año/hub + Q1-Q4 + 12 meses + 52 semanas + 365 días) + 55 plantillas de tracker en
  5 categorías de vida (Lifestyle/Wellness/Self-Care/Productivity/Finance) + notas.
- **Builder**: `life_planner/build_life_planner.py`. Motor propio (no usa
  `planner_framework.py`, demasiado simple para hubs + cross-links). **Hipervínculos
  en 2 pasadas**: (1) construir el "spine" = lista ordenada de páginas con id único,
  calcular `page_index[id]`; (2) crear páginas en blanco y renderizar con acceso al
  index para linkear por id (nunca por número de página mágico). Plantillas declarativas
  compuestas con primitivas (`tpl_table`, `tpl_checklist`, `tpl_month_grid_tracker`…).
  Usar `--quick` para iterar rápido (reduce meses/semanas/días).
- **Previews**: `life_planner/build_previews.py` (renderiza páginas del PDF a PNG y
  compone 5 imágenes sobre navy con el branding). Los índices de página en `PAGES`
  dependen del spine — si cambia el orden/conteo, reverificarlos.
- **Archivo Etsy**: 1 PDF directo (formato aceptado, sin conversión a .mov). Vector,
  ~2 MB para 500 págs (muy por debajo del límite de 20 MB).
- **Precio**: $2.99 (competir bajo vs. best-seller ~EUR2) · **taxonomy_id**: 12476 (`TAXONOMY["planner_template"]`).
- **Gotchas de PyMuPDF**: los textbox deben ser ≥ ~2× el fontsize de alto o el texto se
  descarta en silencio; times-roman base14 no tiene glifos como `›`/`‹`/emojis (usar
  ASCII `>`/`<` y texto plano).

## Gotchas de la API de Etsy (etsy_manager.py)

- **Cambiar el precio de un listing YA CREADO no es `update_listing(price=...)`.**
  Ese PATCH le pega a `/shops/{id}/listings/{id}` y Etsy responde 200 OK sin error,
  pero el precio queda igual (lo ignora en silencio). El precio real vive en el
  **inventario** (`GET/PUT /listings/{id}/inventory`), y el PUT exige:
  1. JSON real (`Content-Type: application/json`), NO form-urlencoded — mandar los
     arrays anidados (`products`/`offerings`) url-encodeados falla con
     `"Not a valid JSON string"`.
  2. Solo los campos escribibles: cada `offering` acepta `price`/`quantity`/
     `is_enabled` — si mandás de vuelta `offering_id`, `is_deleted` o
     `readiness_state_id` (que sí vienen en el GET), Etsy rechaza con
     `"Array contains invalid keys"`.
  Usar **`EtsyManager.update_price(listing_id, price)`** (ya implementado: lee el
  inventario, lo limpia, lo reenvía como JSON) — no reinventar esto con
  `update_listing`.
- **El token no tiene todos los scopes.** Actual: `listings_r listings_w shops_r`
  (ver `auth.py`). Sin `transactions_r` no se pueden leer receipts/pedidos/ventas
  (`GET /shops/{id}/receipts` → 403). Sin `listings_d` no se puede borrar un
  listing por API (`DELETE /listings/{id}` → 403) — para reemplazar imágenes de
  un listing ya creado hay que subir las nuevas ANTES de borrar las viejas,
  porque Etsy exige que un listing tenga siempre ≥1 imagen.
- **`views`/`num_favorers` del GET del listing son el dato real** — si el usuario
  reporta "muchas visitas" pero la API dice 2, confiar en la API y preguntar de
  dónde saca el otro número (Etsy Ads mide clics, no vistas orgánicas; el
  dashboard de Shop Manager a veces no coincide 1:1 con este campo).
- **No se puede recuperar el archivo digital vendible de un listing por API.**
  `GET /shops/{id}/listings/{id}/files` da metadata (nombre, tamaño, fecha) pero
  ninguna URL de descarga del contenido — esa descarga firmada solo se genera
  para el comprador después de pagar, no para el dueño de la tienda vía esta
  API. `GET /shops/{id}/listings/{id}/images` sí trae URLs públicas
  (`url_fullxfull`), pero son la miniatura de exhibición de Etsy (tope ~1200px
  de lado), NO el archivo original en su resolución real. Conclusión: si un
  producto se creó fuera de este repo (a mano, o en otra sesión) y no se
  guardó el archivo fuente original en algún lado, **no hay forma de
  recuperarlo** — ni por API ni scrapeando las imágenes del listing. Hay que
  reconstruirlo desde cero (regenerar con un script) o pedirle al usuario que
  lo suba si todavía lo tiene en su máquina.

---

## Checklist para publicar un producto nuevo

1. Identifica el tipo arriba e importa `brand` + la plantilla correspondiente.
2. Escribe una config delgada + `render_design` (patrón: los scripts `*_celtic*`).
3. Genera archivos y **revisa visualmente** portada y previews antes de subir.
4. Añade la entrada a `products_catalog.py` (title, description con © + store,
   price, taxonomy_id, **tags obligatorios** — exactamente 13, ≤20 chars cada uno —,
   images, files, video). Sin tags el listing pierde SEO en Etsy; no se debe omitir
   este campo aunque el producto se suba solo como borrador.
5. `python products_catalog.py dry-run <slug>` → luego `upload <slug>`.
6. Queda en **draft**; el usuario lo activa desde Etsy.
