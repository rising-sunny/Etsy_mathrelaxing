# Unit Circle — competitive design research

**Fecha:** 2026-07-15  
**Fuentes:** eRank Top Listings + Etsy listing pages (Playwright)  
**Refs locales:** `research/unit_circle_refs/`

---

## Qué vende en el SERP (formatos)

| Tipo | Ejemplo | Hearts / price | Rol |
|------|---------|----------------|-----|
| **Cheat-sheet poster** (físico multi-size) | MeloPrints trig + unit circle | 176 · $16–85 | Dominante en “poster serio” |
| **Unit circle only poster** | MeloPrints dedicated | 63 · $16+ | Hero = círculo grande |
| **Printable aesthetic** | “The Unit Circle” pastel | 86 · ~$3 digital | Classroom soft / dorm |
| **Minimal line SVG** | Black on white SVG print | 38 · $2 digital | Line art simple |
| **Vinyl sticker** | PhilosophicallyYours | 113 · $3.99 | #1 eRank top listing |
| Cross-stitch / mug / pie plate | varios | niche gift | No competir |

**Insight:** el volumen de *búsqueda* es “unit circle”; el producto wall-art que monetiza bien mezcla **referencia didáctica densa** (cheat sheet) o **círculo limpio hero**. Stickers ganan hearts pero otro formato.

---

## Arquetipos de diseño

### A — Classroom cheat sheet (MeloPrints family)
- Fondo **gris claro / blanco**, marco negro en mockups
- Círculo con **anillo rojo** grueso, ejes negros
- Radios cada 15°/30°, etiquetas **grados + radianes** en cada rayo
- Coordenadas **(x,y)** en el **exterior** del círculo
- **Tabla** degrees / radians / coordinates al lado o abajo
- Sub-panel: triángulo unitario con **sin/cos/tan/sec/csc/cot** en colores
- A veces: identidades + 4 gráficos sin/cos/tan/cot
- Tipografía: sans “infografía” densa, estilo textbook moderno
- Mockups: framed print en pared / escritorio

### B — Soft aesthetic printable (pastel classroom)
- Fondo **blanco puro**, marco blanco, mockup lifestyle (manos, flores)
- Título serif/script “The Unit Circle”
- Círculo negro fino, **coordenadas en verde menta / coral** (por cuadrantes)
- **Sin tabla** — solo el diagrama
- Menos densidades, más “decor”
- Precio bajo digital

### C — Minimal SVG / line art
- Negro sobre blanco, muy limpio
- Mucho espacio negativo
- Menos etiquetas o layout más simple
- Mockup dorm/classroom genérico
- $2 digital — volumen, no premium

### D — Vinyl sticker (best seller hearts)
- Recorte **circular** (die-cut)
- Fondo blanco, círculo negro
- **Coordenadas azul + fracciones**
- **Ángulos en rojo** (grados)
- Radians en negro interior
- Puntos de color en el perímetro
- Mockup sobre madera / laptop

---

## Contenido canónico que el comprador espera

1. Círculo unitario r=1 con ejes x,y  
2. Ángulos especiales cada **30°/45°/60°** (a veces 15°)  
3. **Grados y radianes** en cada ángulo  
4. Coordenadas \((\cos\theta,\sin\theta)\) en fracciones / √  
5. Opcional pero muy valorado: **tabla resumen**  
6. Opcional premium: diagrama sin/cos/tan + identidades  
7. Footer con \(x=\cos\theta,\ y=\sin\theta\)

---

## Precios observados

| Formato | Rango |
|--------|--------|
| Digital printable | $2–6 |
| Physical print (POD multi-size) | $16–45 (hasta $85 A2+) |
| Sticker | ~$3.5–4 |

MathRelaxing digital plate sweet spot: **$5.99–7.99** (como Schrödinger / Maxwell).

---

## Hueco MathRelaxing (diferenciación)

La mayoría es **gris/blanco infografía classroom** o **pastel cute**.  
Casi nadie hace:

- **Scientific plate** cream grid + FIG. + serif editorial (familia Maxwell/Schrödinger)
- Tipografía **LaTeX** real para fracciones y √
- Estética **museum / lab notebook** (no “Teachers Pay Teachers”)
- Caption + footer equation band

→ Podemos ser el **unit circle de laboratorio / dorm STEM premium**, no otro cheat sheet gris.

---

## Propuesta de layout (plate)

```
┌─────────────────────────────────────────┐
│  THE UNIT CIRCLE              FIG. n    │  serif bold black
│  TRIGONOMETRY  ·  degrees & radians     │  rust subtitle
│  ─────────────────────────────────────  │
│                                         │
│         [ large unit circle ]           │  center hero
│         cream card optional             │  labels LaTeX
│                                         │
│  ┌──────────────┐  x = cos θ            │  small table or
│  │ deg · rad · (x,y) │  y = sin θ      │  key angles only
│  └──────────────┘                       │
│                                         │
│  caption 2 lines pedagogical            │
│  footer: (cos θ, sin θ) · unit circle   │
└─────────────────────────────────────────┘
```

**Incluir (sí):**
- 0°, 30°, 45°, 60°, 90° … 360° (16 rayos estándar)
- Grados + π-radianes en rayos
- Coordenadas exteriores con √ LaTeX
- 4 ejes etiquetados (0,1) etc.
- Color acento **rust/teal** en cuadrantes o en sin vs cos (no arcoíris infantil)

**Evitar (para no ser Melo clon):**
- Título “CHEAT SHEET” genérico
- 6 paneles densos de identidades en una sola plate (salvo set aparte)
- Fondo gris flat + rojo clipart
- Pastel coral/mint “TPT”

**Mockups Etsy:** hero = plate full; + detail crop del círculo; + “what’s included” sizes; opcional lifestyle frame.

---

## Competidores clave (referencia)

| Listing | Shop | Notas |
|---------|------|-------|
| [810167187](https://www.etsy.com/listing/810167187) | MeloPrints | Trig cheat sheet full — 176 hearts |
| [1264952515](https://www.etsy.com/listing/1264952515) | MeloPrints | Unit circle only — mismo sistema visual |
| [1169760175](https://www.etsy.com/listing/1169760175) | (pastel) | Soft aesthetic 86 hearts, $3 |
| [1173280830](https://www.etsy.com/listing/1173280830) | SVG | Minimal black line $2 |
| [1409877564](https://www.etsy.com/listing/1409877564) | PhilosophicallyYours | Sticker 113 hearts — blue/red labels |

Imágenes guardadas en `research/unit_circle_refs/`.
