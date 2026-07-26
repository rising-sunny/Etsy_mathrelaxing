# AI Mockup Kit — *The Mathematics of Beauty* (MathRelaxing)

Este paquete sirve para generar **mockups fotorrealistas** del libro usando una IA
de imagen (ChatGPT / DALL·E, Google Gemini / Nano-Banana, Grok, Midjourney, etc.).

## Contenido del zip
| Archivo | Qué es |
|---|---|
| `cover_front.png` | Portada real — **cuadrada 2550×2550 px (1:1)**, sin sangrado |
| `cover_back.png` | Contraportada real — **cuadrada 2550×2550 px (1:1)**, sin sangrado |
| `interior_spread.png` | Spread interior real (dos páginas enfrentadas, 5100×2550 px): texto + gráfica |
| `PROMPTS.md` | Este documento con los prompts |

---

## 📐 MEDIDAS REALES DEL LIBRO — LÉELO PRIMERO
> Este es el punto MÁS importante. Las IAs tienden a dibujar libros rectangulares
> (verticales, tipo novela). **Este libro es un CUADRADO PERFECTO.** Repíteselo.

- **Formato:** libro **CUADRADO**. Ancho = alto.
- **Medidas exactas del trim:** **8.5 × 8.5 pulgadas = 21.6 × 21.6 cm.**
- **Relación de aspecto de la portada y la contraportada:** **1:1 (perfectamente cuadrada).**
  Tanto `cover_front.png` como `cover_back.png` son imágenes **2550×2550 px, cuadradas**.
- **Encuadernación:** tapa dura *case-wrap*, acabado **mate**, tipo coffee-table / libro de arte.
- **Páginas:** ~88 páginas de papel **couché premium** grueso.
- **Grosor del libro (lomo):** ≈ **1.3 cm** (≈ 0.5 in) — delgado pero rígido.
  → En una vista 3/4, el lomo y el bloque de páginas se ven como una franja **fina**,
  NO como un libro grueso tipo diccionario.

**Frase corta para pegar y forzar la geometría (añádela a cualquier prompt):**
```
The book is a PERFECT SQUARE: exactly 8.5 x 8.5 inches (21.6 x 21.6 cm), so its width
and height are EQUAL — a 1:1 square cover, NOT a tall/portrait rectangle. Keep both the
front and back covers perfectly square. The hardcover is thin, about 1.3 cm / 0.5 inch
thick (a slim rigid spine), not a thick heavy book.
```

---

## ⚙️ Cómo usarlo (importante)
1. **Adjunta la imagen de referencia** que pida cada prompt (`cover_front.png`,
   `cover_back.png` o `interior_spread.png`).
2. Copia y pega el **prompt de escena**.
3. Reglas de oro:
   - Dile que use la portada **EXACTA de la referencia, sin redibujar** el arte ni el texto.
   - Recuérdale que el libro es **cuadrado 1:1 (8.5×8.5 in)**, lomo **fino** (~1.3 cm).
4. Pide salida **cuadrada 1:1** o vertical **4:5** (ideal para Etsy) — pero el LIBRO
   dentro de la imagen debe seguir siendo cuadrado.

> **Tip por plataforma**
> - **ChatGPT (GPT-4o) y Gemini / Nano-Banana:** los mejores para "pega esta portada
>   tal cual sobre el libro". Adjunta la imagen y usa el prompt directo.
> - **Grok:** igual, adjunta la imagen y pega el prompt.
> - **Midjourney:** sube la portada como *image prompt* al inicio y añade
>   `--ar 1:1 --style raw --v 6`. Refuerza "square book, 8.5x8.5 inch" en el texto.

---

## 🎨 Bloque de estilo maestro (anteponer a cualquier escena)
```
Photorealistic studio product photograph of a real, physical hardcover art book.
The book is a PERFECT SQUARE, exactly 8.5 x 8.5 inches (21.6 x 21.6 cm) — equal width
and height, a 1:1 square cover, NOT a tall portrait rectangle. Case-wrap hardcover with
a MATTE finish, about 88 pages of thick premium coated paper, a THIN rigid spine roughly
1.3 cm (0.5 inch) thick. Use the ATTACHED IMAGE as the EXACT front cover — do not redraw,
restyle, re-letter or reinterpret the cover art or typography; wrap it faithfully onto the
physical book with correct perspective, subtle matte paper texture and a soft sheen.
Keep the cover perfectly square. High-end commercial photography, 50mm lens, shallow depth
of field, crisp focus on the book, realistic materials.
```

---

## 📸 Prompts de escena
> Todos asumen un **libro cuadrado 8.5×8.5 in con lomo fino (~1.3 cm)**. La geometría
> cuadrada está repetida a propósito en cada uno.

### 1 — Hero 3/4 (la principal del listing)
```
[attach cover_front.png]
A premium SQUARE hardcover art book photographed at a three-quarter front angle on a clean
surface. The book is a perfect square, exactly 8.5 x 8.5 inches (21.6 x 21.6 cm) — equal
width and height, 1:1, NOT a portrait rectangle. Use the attached image as the EXACT matte
front cover (do not redraw the art or text). Thin rigid hardcover (~1.3 cm spine) visible on
the left, cream page block visible along the bottom edge. Soft studio softbox key light from
the upper left, gentle warm ivory gradient background, realistic soft contact shadow.
Editorial product photography, sharp, elegant, minimalist. Square 1:1 output.
```

### 2 — Libro abierto (spread interior REAL) ⭐ recomendado
Usa **`interior_spread.png`** como referencia: es un spread real del libro (página de
texto a la izquierda + gráfica a la derecha), así la IA no inventa el contenido.
```
[attach interior_spread.png]
Photorealistic photo of a SQUARE hardcover coffee-table art book (each page is 8.5 x 8.5
inches / 21.6 cm, perfectly square) lying OPEN and flat, seen slightly from above at a gentle
angle. Because both pages are square, the fully open spread is a WIDE 2:1 rectangle (twice as
wide as it is tall). Map the ATTACHED IMAGE EXACTLY onto the visible two-page spread (left =
cream text page with the equation, right = dark page with the generative curve) — do not
redraw or alter the page content or typography. Show realistic thick premium coated paper,
the two square pages meeting at a soft central gutter shadow, pages subtly curved near the
spine, and the thin rigid hardcover boards around the spread. Soft natural daylight from the
upper left, gentle shadow under the book, premium editorial book photography.
```
> Alternativa sin referencia: "an open SQUARE art book, each page 8.5x8.5 inch, left cream
> page with an elegant serif equation, right dark page with a luminous teal-gold-coral Lorenz
> attractor curve; the open spread is a wide 2:1 rectangle; black + cream + gold identity".

### 3 — Lifestyle sobre mesa (ambiente cálido)
```
[attach cover_front.png]
The SQUARE hardcover art book (exactly 8.5 x 8.5 inches, 1:1 — equal width and height, not a
tall rectangle) standing upright on a warm walnut wood table, leaning slightly, in a cozy
interior. Use the attached image as the EXACT matte front cover. Thin rigid spine (~1.3 cm).
Warm directional lamp light from the left creating a soft glow pool on the wall behind and a
gentle reflection on the polished table. Out-of-focus warm background (a plant and a cup of
coffee softly blurred to the side). Cinematic, inviting, editorial home-decor photography,
golden-hour mood, shallow depth of field. Keep the book perfectly square.
```

### 4 — Detalle / textura (close-up premium)
```
[attach cover_front.png]
Extreme close-up, macro product shot of the corner of the SQUARE hardcover art book (8.5 x
8.5 inch, 1:1, thin rigid ~1.3 cm board). Raking light across the surface reveals the matte
coated paper texture, the crisp square board corner and the gold foil-like title detail from
the attached cover. Very shallow depth of field, dramatic soft light, luxury book
craftsmanship feel, dark elegant background. Square 1:1 output.
```

### 5 — Portada + contraportada (dos ejemplares)
```
[attach cover_front.png AND cover_back.png]
Two copies of the same SQUARE hardcover art book on a soft neutral studio surface. Each book
is a perfect square, 8.5 x 8.5 inches (21.6 x 21.6 cm), 1:1 — equal width and height, thin
rigid spine (~1.3 cm). One copy stands showing the FRONT cover (first attached image), one
lies in front showing the BACK cover (second attached image). Use both attached images EXACTLY
as the printed matte covers, keeping both covers perfectly square. Soft even studio light,
minimalist e-commerce product photography, warm ivory background, soft shadows. Square 1:1.
```

### 6 — Pila / stack (varios ejemplares)
```
[attach cover_front.png]
A neat stack of three copies of the SQUARE hardcover art book (each 8.5 x 8.5 inches, 1:1,
thin rigid ~1.3 cm spine) on a marble surface. The top copy shows the attached front cover,
the spines of the lower copies read "THE MATHEMATICS OF BEAUTY" and "MathRelaxing". Matte
hardcovers, thick premium pages, elegant minimalist styling, soft studio light, luxury
bookstore display feel. Keep every cover perfectly square. Square 1:1 output.
```

---

## 🚫 Negative prompt / cosas a evitar
Añade esto si tu IA soporta *negative prompt*, o pídelo en lenguaje natural:
```
Avoid: portrait / tall rectangular book, non-square cover, wrong proportions, thick heavy
book, oversized spine, redrawing or altering the cover art or text, warped or curved
typography, glossy plastic look, cartoonish render, extra logos or watermarks, distorted
infinity symbol, blurry cover, text artifacts, melted or duplicated letters, over-saturated
colors.
```

## ✅ Checklist de calidad
- [ ] El libro se ve **cuadrado 1:1** (mismo ancho que alto) — NO vertical/rectangular.
- [ ] El **lomo es fino** (~1.3 cm), no un libro grueso.
- [ ] La portada es **idéntica** a `cover_front.png` (sin texto inventado).
- [ ] El símbolo ∞ y "THE MATHEMATICS OF BEAUTY" se leen bien.
- [ ] Acabado **mate**, no plástico brillante.
- [ ] Sombras/reflejos coherentes con una sola fuente de luz.

---
*MathRelaxing · The Mathematics of Beauty — kit para generación de mockups con IA.*
*Libro cuadrado 8.5 × 8.5 in (21.6 × 21.6 cm), tapa dura mate, ~88 pág.*
