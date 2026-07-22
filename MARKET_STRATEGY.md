# MathRelaxing — Market Strategy & Research Playbook

Guía viva para decidir **qué producto hacer** y **cómo posicionarlo** en Etsy.
La actualizamos cada vez que corremos un escaneo nuevo.

Última actualización: 2026-07-11

---

## 1. La meta real (no es solo "poca competencia + alto volumen")

"Poca competencia + alto volumen" es la **brújula** para encontrar candidatos,
no la meta final. La meta es **venta rentable y repetible**:

> **Ingreso ≈ búsquedas × conversión × precio × recurrencia**

Chasear solo volumen/competencia optimiza el primer factor e ignora los otros
tres. Dos trampas frecuentes:

- **"Poca competencia" a veces = "no hay demanda".** Un nicho vacío puede estar
  vacío por una razón. Ejemplo real del escaneo: `desktop wallpaper math` = 0
  competencia y 0 demanda.
- **Volumen alto con precio $1 engaña.** 10.000 búsquedas de un ítem de $1 puede
  rendir menos que 500 de un póster de $25.

### Nuestra ventaja injusta (moat)
Arte matemático **real, hecho con código** (no stock, no AI). Con un moat fuerte
podemos **ganar en nichos más competidos** porque el producto se ve claramente
único. Por eso NO descartamos un nicho solo por competencia si podemos destacar.

---

## 2. La regla de 3 preguntas (para evaluar cada idea)

Antes de construir un producto, responde las tres:

1. **¿Hay demanda?** → volumen de búsqueda (eRank) + favoritos/ventas.
2. **¿Puedo destacar?** → ¿mi arte de código es un diferenciador claro aquí?
3. **¿El margen vale?** → precio × conversión, no solo búsquedas.

Fórmula mental: **demanda comprobada × diferenciación × margen.**

---

## 3. Herramientas: API de Etsy vs eRank

| Dato | API Etsy (gratis, automatizado) | eRank |
|---|---|---|
| Competencia (nº listings) | ✅ | ✅ |
| Precios de la competencia | ✅ | ✅ |
| Favoritos por listing | ✅ | ✅ |
| **Volumen de búsqueda/mes** | ❌ | ✅ (estimado) |
| **Ventas estimadas** | ❌ | ✅ (limitado) |
| Long-tail keywords / tags | ❌ | ✅ |
| Auditoría SEO de listings | ❌ | ✅ |

**Flujo eficiente (tier gratis de eRank tiene búsquedas limitadas):**
1. La API (la corro yo) da **competencia + precio** de un set de nichos.
2. Tú miras en eRank el **volumen** solo de los 4–8 mejores (⭐ en §5).
3. Decidimos con las dos señales + la regla de 3 preguntas.

---

## 4. Umbrales de interpretación (tienda chica)

| Señal | 🟢 Buena | 🟡 Aceptable | 🔴 Evita |
|---|---|---|---|
| Volumen búsqueda/mes (eRank) | > 1.000 | 300 – 1.000 | < 100 (salvo ticket alto) |
| Competencia (nº listings) | < 5.000 | 5.000 – 20.000 | > 20.000 |
| Precio / ticket | — | — | volumen alto + precio $1 = trampa |

Regla práctica: **volumen alto ÷ competencia baja = candidato**; luego filtra con
diferenciación + margen.

---

## 5. Shortlist vigente (escaneo API 2026-07-11)

`fav` = favoritos del listing top (proxy de demanda). Columnas de eRank a llenar tú.

| Keyword | Comp. | Precio med | Fav máx | eRank vol. | Prioridad |
|---|---|---|---|---|---|
| chladni art | 39 🟢 | $25 | 155 | _(llenar)_ | ⭐ casi sin comp + ticket alto |
| cymatics wall art | 104 🟢 | $27 | 155 | | ⭐ hermano de Chladni |
| strange attractor print | 29 🟢 | $18 | 433 | | ⭐ ya lo tenemos |
| math magnet | 284 🟢 | $7.37 | 2851 | | ⭐ ya lo tenemos |
| equation poster | 333 🟢 | $13.49 | 514 | | ⭐ ya lo tenemos |
| fractal art print | 3338 | $27 | 735 | | ✅ comp media + moat + ticket |
| sacred geometry svg | 1495 | $3.48 | 1457 | | ✅ idea SVG cut files |
| math svg | 4309 | $3.41 | 1603 | | ✅ idea SVG cut files |
| procreate color palette | 10342 | $2.48 | 2160 | | opcional (ya tenemos 2) |
| abstract math poster | 1300 | $11 | 498 | | opcional |
| physics poster | 2387 | $12 | 1035 | | opcional (ya tenemos equations) |
| sacred geometry print | 16430 | $13.99 | 769 | | 🟡 solo con long-tail |
| math art print | 14613 | $15.38 | 597 | | 🟡 solo con long-tail |
| science wall art | 148k 🔴 | $17.99 | 1157 | | ❌ saturado |
| math teacher gift | 32610 🔴 | $17.99 | 414 | | ❌ saturado |
| dark academia poster | 59833 🔴 | $18.45 | 378 | | ❌ saturado |
| geometric wall art | 1.36M 🔴 | $55 | 884 | | ❌ saturadísimo |

**Gasta las búsquedas de eRank solo en las ⭐/✅.**

Hallazgo clave: **chladni art (39 comp, $25)** y **cymatics wall art (104, $27)** —
competencia casi nula con ticket alto y calzan con nuestro moat. Fuertes candidatos
a expandir (posters individuales, variantes de color).

---

## 6. Cómo proceder en eRank (paso a paso)

**Setup:** cuenta → región **United States** → moneda USD.

**Job 1 — Optimizar listings existentes (PRIMERO, mayor ROI ahora):**
- Pega cada URL de tus listings en el Listing Audit / Keyword Explorer.
- Corrige: título con la keyword fuerte **adelante**; los **13 tags llenos** con
  frases long-tail (2–3 palabras, ≤20 chars) sacadas del Keyword Tool; tags que
  matcheen el título.

**Job 2 — Investigar el próximo producto (Keyword Tool):**
- Para cada keyword ⭐/✅ mira: **Etsy Searches** (volumen), **Etsy Competition**,
  **Avg Clicks / CTR**.
- Anota el volumen en la tabla de §5 y aplica la regla de 3 preguntas.

**Ritmo (tier gratis):** una semana auditas lo existente; otra investigas 1 idea
nueva. No malgastes la cuota diaria explorando a ciegas.

---

## 7. Cómo actualizar esta guía
- Cada escaneo nuevo de API → actualiza la tabla de §5 (fecha + números).
- Cuando llenes volúmenes de eRank → pégalos en la columna correspondiente.
- El script de escaneo vive como referencia; pídeme "corre el escaneo de mercado"
  y regenero la tabla con los nichos que definamos.
