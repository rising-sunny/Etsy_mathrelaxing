# Análisis Etsy Ads — TheMathRelaxing

**Fecha:** 2026-07-14  
**Fuente:** Panel Etsy Ads (sesión Playwright / Edge)  
**Periodo stats:** Últimos 30 días (14 jun – 14 jul)

---

## Resumen ejecutivo

| Métrica | Valor | Evaluación |
|---------|------:|------------|
| Vistas ads | 2,776 | Tráfico real de ads |
| Clics | 36 | CTR global ~1.3% (aceptable) |
| Pedidos | **2** | Solo 2 conversiones |
| Ingresos ads | **$3.49** | Bajo |
| Inversión | **$9.81** | |
| **ROAS** | **0.36** | **Perdiendo dinero** (ideal >2) |
| Presupuesto diario (antes) | **$25** | Excesivo vs gasto real |
| Presupuesto diario (**ahora**) | **$7** | Ajustado |
| Estrategia | Mayor visibilidad | Amplia; gasta en muchos listings |

**Conclusión:** Campaña en modo “spray and pray” con presupuesto alto y ROAS malo. Había 2 winners reales; el resto quemaba clics sin pedidos. Se recortó presupuesto y se pausaron los peores gastadores.

---

## Winners (mantener ads ON)

| Listing | Vistas | Clics | CTR | Pedidos | Ingresos | Spend | ROAS |
|---------|-------:|------:|----:|--------:|---------:|------:|-----:|
| **Chaos Theory Procreate Palettes** | 286 | 3 | 1.0% | **1** | $1.99 | $0.76 | **2.62** |
| **STEM Graph Paper Bundle** | 253 | 2 | 0.8% | **1** | $1.50 | $0.38 | **3.95** |

Estos dos son los **únicos** con pedidos por ads en 30 días. Prioridad de presupuesto.

---

## Héroes orgánicos (Rank Checker) — ads ON confirmados

| Listing | Rank orgánico | Ads |
|---------|---------------|-----|
| Maxwell Equations | #1 physics wall art | **ON** |
| Ulam Spiral | #3 math wall art | **ON** |
| Phyllotaxis Bloom | #10 seamless loop | **ON** (21 vistas ads, 1 clic, $0.22) |

Phyllotaxis ya recibía algo de ads; Maxwell y Ulam también en ON. Con presupuesto concentrado deberían captar más share del $7/día.

---

## Pausados (gasto sin pedidos)

Confirmado **Desactivar** con diálogo:

1. Celtic Knot PDF — $1.22 spend, 4 clics, 0 pedidos  
2. Fractal Flora printed — $1.37, 3 clics, 0  
3. Chladni Figures — $1.18, 3 clics, 0 (CTR 3.2% bueno, pero sin conversión)  
4. Mathematical Constants Bundle — $0.76, 2 clics, 0  
5. Physics Calculus Set of 8 — $0.69, 3 clics, 0  
6. Neural Network Coloring — $0.22, 1 clic, 0  
7. Chaos Attractors Poster — $0.41, 2 clics, 0  
8. Spiral Tilings PDF — $0.18, 1 clic, 0  
9. PhD Dissertation Planner — $0.36, 3 clics, 0  
10. Rössler Attractor — $0.23, 1 clic, 0  

**Lógica:** Clicks caros sin venta a precio digital bajo = ROAS 0 permanente. Mejor reasignar a winners + héroes.

---

## Cambios aplicados

| Acción | Detalle |
|--------|---------|
| Presupuesto | **$25/día → $7/día** (confirmado en UI) |
| Pausas | 9–10 listings con spend y 0 pedidos |
| Heroes | Maxwell, Ulam, Phyllotaxis **ON** |
| Winners | Procreate palettes + STEM Graph **ON** |

---

## Lectura profunda

### 1. Presupuesto $25 vs gasto $9.81
Etsy cobra por clic; no siempre agota el techo. Pero un techo de $25 permite que el algoritmo **difunda** gasto a muchos listings mediocres (“Mayor visibilidad”). Bajar a **$7** fuerza priorización.

### 2. Estrategia “Mayor visibilidad”
Maximiza impresiones, no eficiencia. Con ROAS 0.36 conviene **no** volver a subir presupuesto hasta que ROAS > 1.5 durante 7–14 días.

### 3. Ticket bajo
Pedidos ads a **$1.50–$1.99** (palettes / graph paper). Un solo clic a ~$0.25–$0.40 deja poco margen. Los posters a $8–10 (Maxwell, Ulam) tienen mejor economía de ads **si** convierten.

### 4. Duplicidad
Dos De Jong loops y muchos wall arts similares diluyen el algoritmo. Concentrar ads reduce ruido.

---

## Plan 14 días (post-cambio)

| Día | Qué mirar | Acción |
|-----|-----------|--------|
| 3 | Clicks en Maxwell/Ulam/Phyllotaxis/Procreate/STEM Graph | Si 0 clicks en un hero → revisar fotos |
| 7 | ROAS global | Si <0.8 → bajar a $5/día; si >2 → subir a $10 |
| 14 | Pedidos por listing | Pausar lo que gaste sin venta; reactivar 1–2 pausados con buen CTR (ej. Chladni) solo si sobra presupuesto |

---

## No tocado (aún)

- **Offsite Ads** (panel separado) — revisar si está ON y comisionando  
- Estrategia default “Mayor visibilidad” a nivel listing restante — muchos siguen ON en páginas 2–5 sin spend alto; con $7 el algoritmo los priorizará menos  
- Reactivación de Newton/Julia si siguen ON con spend — verificar en página 2 manualmente

---

## Enlaces

- Panel: https://www.etsy.com/your/shops/me/advertising  
- Maxwell: …/listing-editor/edit/4537623277  
- Ulam: …/listing-editor/edit/4537362221  
- Phyllotaxis: …/listing-editor/edit/4533348472  
