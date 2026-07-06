"""
build_life_planner.py — MathRelaxing All-in-One Undated Digital Planner
=======================================================================
Un planner digital "todo incluido" al estilo de los best-sellers de Etsy
(calendario completo + decenas de trackers en 5 categorias de vida + notas),
100% hipervinculado, para GoodNotes / Notability / cualquier app de anotacion
en iPad y Android.

Diseno: landscape 4:3 (estandar iPad). Identidad MathRelaxing: pagina clara y
escribible, banda de encabezado navy, acentos oro, franja inferior negra con el
logo. Tipografia serif en titulos.

Navegacion (hub-and-spoke, todo tap-to-jump):
  - Barra de pestañas lateral fija en cada pagina -> HOME / YEAR / MO / WK / DAY
    / LIFE / BODY / MIND / WORK / MONEY / NOTE (cada una salta a su hub).
  - Dashboard principal con accesos a todas las secciones.
  - Year-at-a-glance con 12 bloques de mes que enlazan a cada mes.
  - Meses / semanas / dias con navegacion prev/next.
  - Cada categoria de trackers tiene una pagina "hub" que lista sus plantillas
    como filas tappables que saltan a cada plantilla.

Resolucion de hipervinculos en DOS PASADAS:
  1) Se construye el "spine" (lista ordenada de todas las paginas con un id
     unico cada una) y se calcula page_index[id] = posicion.
  2) Se crean las paginas en blanco y se renderiza cada una, ya con acceso al
     page_index para insertar los links por id (no por numero magico).

Uso:
  python build_life_planner.py            # build completo (~500+ paginas)
  python build_life_planner.py --quick     # version reducida para iterar rapido
"""

import os
import sys
import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_PDF = os.path.join(BASE, "MathRelaxing_Life_Planner.pdf")

QUICK = "--quick" in sys.argv

# ── Lienzo landscape 4:3 ──────────────────────────────────────────────────────
PW, PH = 1024.0, 768.0
MARGIN = 40
TAB_W = 26                      # ancho de la barra de pestañas lateral (derecha)
CONTENT_R = PW - TAB_W - 18     # borde derecho util del contenido
HEADER_H = 58                   # alto de la banda de encabezado
FOOTER_H = 26                   # alto de la franja del logo

# ── Cantidades del calendario ────────────────────────────────────────────────
N_MONTHLY = 3 if QUICK else 12
N_WEEKLY = 4 if QUICK else 52
N_DAILY = 8 if QUICK else 365

# ── Paleta (hex de brand -> tupla 0..1 para fitz) ────────────────────────────
def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

NAVY = (0.07, 0.09, 0.18)
GOLD = _hex(brand.GOLD)
CREAM = _hex(brand.CREAM)
INK = (0.13, 0.14, 0.18)
MUTED = (0.52, 0.54, 0.60)
LINE = (0.80, 0.81, 0.84)
GRID = (0.90, 0.90, 0.93)
FAINT = (0.955, 0.955, 0.965)
WHITE = (1, 1, 1)

SERIF = "times-roman"
SERIF_B = "times-bold"
SERIF_I = "times-italic"
SANS = "helv"

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ═════════════════════════════════════════════════════════════════════════════
#  PRIMITIVAS DE DIBUJO
# ═════════════════════════════════════════════════════════════════════════════
def rect(pg, x0, y0, x1, y1, color=None, fill=None, width=0.8):
    pg.draw_rect(fitz.Rect(x0, y0, x1, y1), color=color, fill=fill, width=width)


def line(pg, x0, y0, x1, y1, color=LINE, width=0.6, dashes=None):
    pg.draw_line(fitz.Point(x0, y0), fitz.Point(x1, y1), color=color, width=width, dashes=dashes)


def text(pg, x, y, s, size=10, font=SERIF, color=INK, align=0, w=520):
    # box alto >= ~2x fontsize; si no, PyMuPDF descarta el texto en silencio
    pg.insert_textbox(fitz.Rect(x, y, x + w, y + size * 2.2), s,
                      fontsize=size, fontname=font, color=color, align=align)


def header(pg, title, subtitle=None):
    rect(pg, 0, 0, PW, HEADER_H, fill=NAVY, width=0)
    rect(pg, 0, HEADER_H, PW, HEADER_H + 2.2, fill=GOLD, width=0)
    text(pg, MARGIN, 16, title, size=21, font=SERIF_B, color=CREAM, w=PW - 2 * MARGIN)
    if subtitle:
        text(pg, PW - TAB_W - 360, 22, subtitle, size=10.5, font=SERIF_I,
             color=GOLD, align=2, w=340)


def footer(pg):
    rect(pg, 0, PH - FOOTER_H, PW, PH, fill=(0, 0, 0), width=0)
    if os.path.exists(brand.LOGO_PATH):
        lh = FOOTER_H * 0.66
        pg.insert_image(fitz.Rect(PW / 2 - 46, PH - FOOTER_H + (FOOTER_H - lh) / 2,
                                  PW / 2 + 46, PH - (FOOTER_H - lh) / 2),
                        filename=brand.LOGO_PATH, keep_proportion=True)
    text(pg, PW - TAB_W - 130, PH - FOOTER_H + 8, brand.STORE, size=7.5,
         font=SANS, color=(0.7, 0.7, 0.72), align=2, w=110)


def body_top():
    return HEADER_H + 22


def body_bottom():
    return PH - FOOTER_H - 16


def panel(pg, x0, y0, x1, y1, label=None):
    rect(pg, x0, y0, x1, y1, color=LINE, width=0.9)
    if label:
        rect(pg, x0, y0, x1, y0 + 22, color=None, fill=FAINT, width=0)
        line(pg, x0, y0 + 22, x1, y0 + 22, color=LINE, width=0.9)
        text(pg, x0 + 10, y0 + 5, label, size=9.5, font=SERIF_B, color=NAVY, w=x1 - x0 - 20)
        return y0 + 22
    return y0


def ruled(pg, x0, y0, x1, y1, gap=26, color=GRID):
    y = y0 + gap
    while y < y1 - 2:
        line(pg, x0, y, x1, y, color=color, width=0.5)
        y += gap


def dotgrid(pg, x0, y0, x1, y1, gap=20, color=(0.72, 0.73, 0.78)):
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            pg.draw_circle(fitz.Point(x, y), 0.6, color=color, fill=color)
            x += gap
        y += gap


def squares(pg, x0, y0, x1, y1, gap=20, color=GRID):
    x = x0
    while x <= x1:
        line(pg, x, y0, x, y1, color=color, width=0.4)
        x += gap
    y = y0
    while y <= y1:
        line(pg, x0, y, x1, y, color=color, width=0.4)
        y += gap


def isogrid(pg, x0, y0, x1, y1, gap=22, color=(0.75, 0.76, 0.80)):
    r = 0
    y = y0
    while y <= y1:
        off = gap / 2 if (r % 2) else 0
        x = x0 + off
        while x <= x1:
            pg.draw_circle(fitz.Point(x, y), 0.6, color=color, fill=color)
            x += gap
        y += gap * 0.87
        r += 1


def checkbox_rows(pg, x0, y0, x1, y1, gap=25, box=11):
    y = y0 + 6
    while y < y1 - box:
        rect(pg, x0, y, x0 + box, y + box, color=MUTED, width=0.8)
        line(pg, x0 + box + 12, y + box, x1, y + box, color=GRID, width=0.5)
        y += gap


def numbered_rows(pg, x0, y0, x1, y1, gap=26, start=1):
    y = y0 + 4
    n = start
    while y < y1 - gap + 6:
        text(pg, x0, y, f"{n:02d}", size=8.5, font=SANS, color=MUTED, w=22)
        line(pg, x0 + 26, y + 14, x1, y + 14, color=GRID, width=0.5)
        y += gap
        n += 1


def table(pg, x0, y0, x1, y1, cols, header_fill=FAINT, rowgap=26):
    """cols: lista de (label, frac_width). Dibuja cabecera + filas ruledas."""
    total = sum(c[1] for c in cols)
    rect(pg, x0, y0, x1, y0 + 24, color=LINE, fill=header_fill, width=0.9)
    cx = x0
    for label, frac in cols:
        w = (x1 - x0) * frac / total
        text(pg, cx + 6, y0 + 6, label, size=8.5, font=SERIF_B, color=NAVY, w=w - 8)
        if cx > x0:
            line(pg, cx, y0, cx, y1, color=GRID, width=0.5)
        cx += w
    rect(pg, x0, y0, x1, y1, color=LINE, width=0.9)
    y = y0 + 24 + rowgap
    while y < y1 - 2:
        line(pg, x0, y, x1, y, color=GRID, width=0.5)
        y += rowgap


def month_grid(pg, x0, y0, x1, y1, link_targets=None, pidx=None):
    """Cuadricula de mes en blanco (undated): 7 columnas x 6 filas."""
    cols, rows = 7, 6
    cw = (x1 - x0) / cols
    head_h = 20
    for i, wd in enumerate(WEEKDAYS):
        text(pg, x0 + i * cw, y0, wd, size=8.5, font=SERIF_B, color=MUTED,
             align=1, w=cw)
    gy0 = y0 + head_h
    ch = (y1 - gy0) / rows
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c * cw
            cy = gy0 + r * ch
            rect(pg, cx, cy, cx + cw, cy + ch, color=GRID, width=0.5)


def pill_link(pg, x0, y0, x1, y1, label, pidx, target, sub=None,
              fill=WHITE, bordered=True):
    if bordered:
        rect(pg, x0, y0, x1, y1, color=LINE, fill=fill, width=0.9)
    text(pg, x0 + 12, y0 + (8 if sub else (y1 - y0) / 2 - 8), label,
         size=11, font=SERIF_B, color=NAVY, w=x1 - x0 - 20)
    if sub:
        text(pg, x0 + 12, y0 + 26, sub, size=8, font=SANS, color=MUTED, w=x1 - x0 - 20)
    if pidx is not None and target in pidx:
        pg.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(x0, y0, x1, y1),
                        "page": pidx[target], "to": fitz.Point(0, 0)})


def goto(pg, x0, y0, x1, y1, pidx, target):
    if pidx is not None and target in pidx:
        pg.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(x0, y0, x1, y1),
                        "page": pidx[target], "to": fitz.Point(0, 0)})


# ═════════════════════════════════════════════════════════════════════════════
#  CROMO GLOBAL: pestañas laterales + prev/next
# ═════════════════════════════════════════════════════════════════════════════
TABS = [
    ("HOME", "dashboard"),
    ("YEAR", "year_hub"),
    ("MO", "month_1"),
    ("WK", "week_1"),
    ("DAY", "day_1"),
    ("LIFE", "hub_LIFE"),
    ("BODY", "hub_BODY"),
    ("MIND", "hub_MIND"),
    ("WORK", "hub_WORK"),
    ("MONEY", "hub_MONEY"),
    ("NOTE", "hub_NOTE"),
]


def side_tabs(pg, pidx, active=None):
    x0 = PW - TAB_W
    n = len(TABS)
    avail = PH - HEADER_H - FOOTER_H - 8
    th = avail / n
    for i, (label, target) in enumerate(TABS):
        y0 = HEADER_H + 4 + i * th
        y1 = y0 + th - 3
        is_active = (target == active)
        fill = GOLD if is_active else (NAVY if i % 2 == 0 else (0.11, 0.13, 0.24))
        txt_col = NAVY if is_active else CREAM
        rect(pg, x0, y0, PW, y1, fill=fill, width=0)
        # etiqueta vertical corta
        text(pg, x0 - 2, (y0 + y1) / 2 - 6, label, size=7.2, font=SERIF_B,
             color=txt_col, align=1, w=TAB_W + 2)
        if target in pidx:
            pg.insert_link({"kind": fitz.LINK_GOTO,
                            "from": fitz.Rect(x0, y0, PW, y1),
                            "page": pidx[target], "to": fitz.Point(0, 0)})


def prevnext(pg, pidx, prev_id=None, next_id=None):
    y = PH - FOOTER_H - 26
    if prev_id and prev_id in pidx:
        r = (MARGIN, y, MARGIN + 90, y + 20)
        rect(pg, *r, color=LINE, fill=FAINT, width=0.8)
        text(pg, r[0], r[1] + 4, "< Prev", size=9, font=SERIF_B, color=NAVY, align=1, w=90)
        pg.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(*r),
                        "page": pidx[prev_id], "to": fitz.Point(0, 0)})
    if next_id and next_id in pidx:
        r = (CONTENT_R - 90, y, CONTENT_R, y + 20)
        rect(pg, *r, color=LINE, fill=FAINT, width=0.8)
        text(pg, r[0], r[1] + 4, "Next >", size=9, font=SERIF_B, color=NAVY, align=1, w=90)
        pg.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(*r),
                        "page": pidx[next_id], "to": fitz.Point(0, 0)})


def chrome(pg, pidx, active=None, prev_id=None, next_id=None, foot=True):
    if foot:
        footer(pg)
    side_tabs(pg, pidx, active=active)
    prevnext(pg, pidx, prev_id, next_id)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGINAS DE CALENDARIO
# ═════════════════════════════════════════════════════════════════════════════
def r_dashboard(pg, pidx, meta):
    rect(pg, 0, 0, PW, PH, fill=WHITE, width=0)
    footer(pg)
    side_tabs(pg, pidx, active="dashboard")
    # Encabezado grande
    rect(pg, 0, 0, PW, 132, fill=NAVY, width=0)
    rect(pg, 0, 132, PW, 135, fill=GOLD, width=0)
    text(pg, MARGIN, 30, "MathRelaxing", size=15, font=SERIF_I, color=GOLD, w=400)
    text(pg, MARGIN, 52, "LIFE PLANNER", size=34, font=SERIF_B, color=CREAM, w=600)
    text(pg, MARGIN, 100, "Undated · All-in-One · Fully Hyperlinked", size=11,
         font=SERIF_I, color=(0.8, 0.82, 0.9), w=500)

    cards = [
        ("Year at a Glance", "Overview, quarters & review", "year_hub"),
        ("Monthly Planner", f"{N_MONTHLY} undated month spreads", "month_1"),
        ("Weekly Planner", f"{N_WEEKLY} weekly layouts", "week_1"),
        ("Daily Planner", f"{N_DAILY} daily pages", "day_1"),
        ("Lifestyle", "Lists, logs & organization", "hub_LIFE"),
        ("Wellness", "Health & body trackers", "hub_BODY"),
        ("Self-Care", "Gratitude, journaling & mindset", "hub_MIND"),
        ("Productivity", "Goals, tasks & focus", "hub_WORK"),
        ("Finance", "Budget & money trackers", "hub_MONEY"),
        ("Notes", "Dot, grid, Cornell & more", "hub_NOTE"),
    ]
    cols = 3
    gx0, gy0 = MARGIN, 152
    gw = (CONTENT_R - gx0)
    cw = (gw - (cols - 1) * 16) / cols
    ch = 88
    for i, (title, sub, tgt) in enumerate(cards):
        r = i // cols
        c = i % cols
        x0 = gx0 + c * (cw + 16)
        y0 = gy0 + r * (ch + 14)
        pill_link(pg, x0, y0, x0 + cw, y0 + ch, title, pidx, tgt, sub=sub)


def r_year_hub(pg, pidx, meta):
    header(pg, "THE YEAR", "TAP TO OPEN")
    chrome(pg, pidx, active="year_hub")
    x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
    items = [
        ("Year at a Glance", "12-month overview", "year_glance"),
        ("Yearly Goals", "Intentions by life area", "year_goals"),
        ("Year in Review", "Look back & celebrate", "year_review"),
        ("Key Dates", "Birthdays & important days", "key_dates"),
        ("Year Highlights", "One line a month", "highlights"),
        ("Q1 Planner", "January - March", "quarter_1"),
        ("Q2 Planner", "April - June", "quarter_2"),
        ("Q3 Planner", "July - September", "quarter_3"),
        ("Q4 Planner", "October - December", "quarter_4"),
    ]
    cols = 3
    cw = (x1 - x0 - (cols - 1) * 16) / cols
    ch = 88
    for i, (t, s, tgt) in enumerate(items):
        r = i // cols
        c = i % cols
        bx = x0 + c * (cw + 16)
        by = y0 + r * (ch + 16)
        pill_link(pg, bx, by, bx + cw, by + ch, t, pidx, tgt, sub=s)


def make_quarter(q):
    names = {1: ("Q1", [0, 1, 2]), 2: ("Q2", [3, 4, 5]),
             3: ("Q3", [6, 7, 8]), 4: ("Q4", [9, 10, 11])}
    qname, months = names[q]

    def render(pg, pidx, meta):
        header(pg, f"{qname} PLANNER", "QUARTERLY FOCUS")
        chrome(pg, pidx, active="year_hub")
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        # 3 columnas de mes con objetivos
        cw = (x1 - x0 - 2 * 16) / 3
        for i, m in enumerate(months):
            bx = x0 + i * (cw + 16)
            top = panel(pg, bx, y0, bx + cw, y0 + (y1 - y0) * 0.55, label=MONTHS[m].upper())
            checkbox_rows(pg, bx + 12, top + 2, bx + cw - 12, y0 + (y1 - y0) * 0.55 - 6, gap=24)
            tgt = f"month_{m + 1}" if m + 1 <= N_MONTHLY else "month_1"
            goto(pg, bx, y0, bx + cw, y0 + 22, pidx, tgt)
        # abajo: prioridades del trimestre
        by = y0 + (y1 - y0) * 0.55 + 16
        top = panel(pg, x0, by, x1, y1, label="QUARTER PRIORITIES & BIG GOALS")
        cw2 = (x1 - x0 - 24) / 2
        checkbox_rows(pg, x0 + 12, top + 2, x0 + cw2, y1 - 6, gap=26)
        checkbox_rows(pg, x0 + cw2 + 24, top + 2, x1 - 12, y1 - 6, gap=26)
    return render


def r_key_dates(pg, pidx, meta):
    header(pg, "KEY DATES", "IMPORTANT DAYS ALL YEAR")
    chrome(pg, pidx, active="year_hub")
    x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
    cols = 3
    cw = (x1 - x0 - (cols - 1) * 14) / cols
    rows = 4
    ch = (y1 - y0 - (rows - 1) * 12) / rows
    for m in range(12):
        r = m // cols
        c = m % cols
        bx = x0 + c * (cw + 14)
        by = y0 + r * (ch + 12)
        top = panel(pg, bx, by, bx + cw, by + ch, label=MONTHS[m])
        ruled(pg, bx + 10, top + 2, bx + cw - 10, by + ch - 6, gap=22)


def r_highlights(pg, pidx, meta):
    header(pg, "YEAR HIGHLIGHTS", "ONE MEMORY A MONTH")
    chrome(pg, pidx, active="year_hub")
    x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
    rh = (y1 - y0) / 12
    for m in range(12):
        ry = y0 + m * rh
        if m % 2 == 1:
            rect(pg, x0, ry, x1, ry + rh, color=None, fill=FAINT, width=0)
        text(pg, x0 + 8, ry + rh / 2 - 8, MONTHS[m], size=10, font=SERIF_B, color=NAVY, w=110)
        line(pg, x0 + 130, ry + rh - 6, x1 - 10, ry + rh - 6, color=GRID, width=0.5)
    rect(pg, x0, y0, x1, y0 + 12 * rh, color=LINE, width=0.7)


def r_year_glance(pg, pidx, meta):
    header(pg, "YEAR AT A GLANCE", "TAP A MONTH")
    chrome(pg, pidx, active="year_hub")
    x0, y0 = MARGIN, body_top()
    x1, y1 = CONTENT_R, body_bottom()
    cols, rows = 4, 3
    cw = (x1 - x0 - (cols - 1) * 14) / cols
    ch = (y1 - y0 - (rows - 1) * 14) / rows
    for m in range(12):
        r = m // cols
        c = m % cols
        bx = x0 + c * (cw + 14)
        by = y0 + r * (ch + 14)
        top = panel(pg, bx, by, bx + cw, by + ch, label=MONTHS[m])
        # mini grid 7x5
        mg_y = top + 6
        gc, gr = 7, 5
        mcw = (cw - 16) / gc
        mch = (by + ch - mg_y - 8) / gr
        for rr in range(gr):
            for cc in range(gc):
                mx = bx + 8 + cc * mcw
                my = mg_y + rr * mch
                rect(pg, mx, my, mx + mcw, my + mch, color=GRID, width=0.4)
        tgt = f"month_{m + 1}"
        if m + 1 > N_MONTHLY:
            tgt = "month_1"
        goto(pg, bx, by, bx + cw, by + ch, pidx, tgt)


def r_year_goals(pg, pidx, meta):
    header(pg, "YEARLY GOALS", "SET YOUR INTENTIONS")
    chrome(pg, pidx, active="year_hub")
    x0, y0 = MARGIN, body_top()
    x1, y1 = CONTENT_R, body_bottom()
    colw = (x1 - x0 - 28) / 2
    areas = ["Health & Body", "Career & Study", "Finance", "Relationships",
             "Personal Growth", "Fun & Adventure"]
    for i, a in enumerate(areas):
        r = i // 2
        c = i % 2
        bx = x0 + c * (colw + 28)
        by = y0 + r * ((y1 - y0) / 3)
        bh = (y1 - y0) / 3 - 14
        top = panel(pg, bx, by, bx + colw, by + bh, label=a.upper())
        checkbox_rows(pg, bx + 12, top + 4, bx + colw - 12, by + bh - 6, gap=24)


def r_year_review(pg, pidx, meta):
    header(pg, "YEAR IN REVIEW", "LOOK BACK & CELEBRATE")
    chrome(pg, pidx, active="year_hub")
    x0, y0 = MARGIN, body_top()
    x1, y1 = CONTENT_R, body_bottom()
    colw = (x1 - x0 - 28) / 2
    blocks = ["Biggest Wins", "Lessons Learned", "Favorite Memories",
              "What I'm Grateful For", "Goals Achieved", "Word of the Year"]
    for i, b in enumerate(blocks):
        r = i // 2
        c = i % 2
        bx = x0 + c * (colw + 28)
        by = y0 + r * ((y1 - y0) / 3)
        bh = (y1 - y0) / 3 - 14
        top = panel(pg, bx, by, bx + colw, by + bh, label=b.upper())
        ruled(pg, bx + 12, top, bx + colw - 12, by + bh - 6, gap=24)


def make_month(idx):
    prev_id = f"month_{idx - 1}" if idx > 1 else None
    next_id = f"month_{idx + 1}" if idx < N_MONTHLY else None
    name = MONTHS[idx - 1] if idx <= 12 else f"Month {idx}"

    def render(pg, pidx, meta):
        header(pg, name.upper(), "MONTHLY PLANNER")
        chrome(pg, pidx, active="month_1", prev_id=prev_id, next_id=next_id)
        x0, y0 = MARGIN, body_top()
        x1, y1 = CONTENT_R, body_bottom() - 26
        # calendario a la izquierda (70%), objetivos a la derecha
        cal_w = (x1 - x0) * 0.68
        month_grid(pg, x0, y0 + 6, x0 + cal_w, y1)
        sx0 = x0 + cal_w + 20
        top = panel(pg, sx0, y0, x1, y0 + (y1 - y0) * 0.5, label="MONTHLY GOALS")
        checkbox_rows(pg, sx0 + 12, top + 2, x1 - 12, y0 + (y1 - y0) * 0.5 - 6, gap=24)
        ny0 = y0 + (y1 - y0) * 0.5 + 14
        top2 = panel(pg, sx0, ny0, x1, y1, label="NOTES")
        ruled(pg, sx0 + 12, top2, x1 - 12, y1 - 6, gap=24)
    return render


def make_week(idx):
    prev_id = f"week_{idx - 1}" if idx > 1 else None
    next_id = f"week_{idx + 1}" if idx < N_WEEKLY else None

    def render(pg, pidx, meta):
        header(pg, f"WEEK {idx}", "WEEKLY PLANNER")
        chrome(pg, pidx, active="week_1", prev_id=prev_id, next_id=next_id)
        x0, y0 = MARGIN, body_top()
        x1, y1 = CONTENT_R, body_bottom() - 26
        # 7 columnas de dias + columna de foco/todo abajo compartida
        top_h = (y1 - y0) * 0.66
        cols = 7
        cw = (x1 - x0) / cols
        for i, wd in enumerate(WEEKDAYS):
            cx = x0 + i * cw
            rect(pg, cx, y0, cx + cw, y0 + 20, color=LINE, fill=FAINT, width=0.6)
            text(pg, cx, y0 + 5, wd, size=8.5, font=SERIF_B, color=NAVY, align=1, w=cw)
            rect(pg, cx, y0 + 20, cx + cw, y0 + top_h, color=GRID, width=0.5)
            ruled(pg, cx + 5, y0 + 22, cx + cw - 4, y0 + top_h, gap=22)
        # fila inferior: foco de la semana + pendientes
        by = y0 + top_h + 14
        halfw = (x1 - x0 - 20) / 2
        t1 = panel(pg, x0, by, x0 + halfw, y1, label="TOP PRIORITIES")
        checkbox_rows(pg, x0 + 12, t1 + 2, x0 + halfw - 12, y1 - 6, gap=24)
        t2 = panel(pg, x0 + halfw + 20, by, x1, y1, label="NOTES & TO-DO")
        ruled(pg, x0 + halfw + 32, t2, x1 - 12, y1 - 6, gap=24)
    return render


def make_day(idx):
    prev_id = f"day_{idx - 1}" if idx > 1 else None
    next_id = f"day_{idx + 1}" if idx < N_DAILY else None

    def render(pg, pidx, meta):
        header(pg, f"DAY {idx}", "DAILY PLANNER")
        chrome(pg, pidx, active="day_1", prev_id=prev_id, next_id=next_id)
        x0, y0 = MARGIN, body_top()
        x1, y1 = CONTENT_R, body_bottom() - 26
        # Izq: agenda por horas. Centro: to-do + prioridades. Der: trackers
        col1 = x0 + (x1 - x0) * 0.34
        col2 = x0 + (x1 - x0) * 0.68
        # Agenda
        top = panel(pg, x0, y0, col1 - 12, y1, label="SCHEDULE")
        hy = top + 4
        hgap = (y1 - top - 6) / 15
        for h in range(15):
            yy = hy + h * hgap
            text(pg, x0 + 6, yy, f"{h + 6:02d}:00", size=8, font=SANS, color=MUTED, w=40)
            line(pg, x0 + 46, yy + hgap - 4, col1 - 18, yy + hgap - 4, color=GRID, width=0.45)
        # To-do / prioridades
        tt = panel(pg, col1, y0, col2 - 12, y0 + (y1 - y0) * 0.55, label="TOP 3 PRIORITIES")
        checkbox_rows(pg, col1 + 12, tt + 2, col2 - 24, y0 + (y1 - y0) * 0.55 - 6, gap=26)
        ty = y0 + (y1 - y0) * 0.55 + 12
        tt2 = panel(pg, col1, ty, col2 - 12, y1, label="TO-DO")
        checkbox_rows(pg, col1 + 12, tt2 + 2, col2 - 24, y1 - 6, gap=24)
        # Trackers
        tk = panel(pg, col2, y0, x1, y0 + (y1 - y0) * 0.4, label="WATER & HABITS")
        wy = tk + 16
        for c in range(8):
            cx = col2 + 18 + c * 20
            pg.draw_circle(fitz.Point(cx, wy), 6, color=MUTED, width=0.8)
        text(pg, col2 + 12, wy + 14, "Mood:   low   -   ok   -   great", size=9,
             font=SERIF, color=INK, w=x1 - col2 - 20)
        gy = y0 + (y1 - y0) * 0.4 + 12
        gt = panel(pg, col2, gy, x1, y1, label="NOTES / GRATITUDE")
        ruled(pg, col2 + 12, gt, x1 - 12, y1 - 6, gap=24)
    return render


# ═════════════════════════════════════════════════════════════════════════════
#  PLANTILLAS DE TRACKERS (compuestas con primitivas)
# ═════════════════════════════════════════════════════════════════════════════
def tpl_lined(title, sub, gap=26):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        ruled(pg, x0, y0, x1, y1, gap=gap, color=GRID)
    return title, sub, r


def tpl_checklist(title, sub, cols=1):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        if cols == 1:
            checkbox_rows(pg, x0, y0, x1, y1, gap=26)
        else:
            cw = (x1 - x0 - 20) / 2
            checkbox_rows(pg, x0, y0, x0 + cw, y1, gap=26)
            checkbox_rows(pg, x0 + cw + 20, y0, x1, y1, gap=26)
    return title, sub, r


def tpl_table(title, sub, cols):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        table(pg, x0, y0, x1, y1, cols)
    return title, sub, r


def tpl_two_panels(title, sub, l_label, r_label, l_kind="check", r_kind="lined"):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        cw = (x1 - x0 - 24) / 2
        for bx, label, kind in [(x0, l_label, l_kind), (x0 + cw + 24, r_label, r_kind)]:
            top = panel(pg, bx, y0, bx + cw, y1, label=label)
            if kind == "check":
                checkbox_rows(pg, bx + 12, top + 2, bx + cw - 12, y1 - 6, gap=26)
            elif kind == "num":
                numbered_rows(pg, bx + 12, top + 2, bx + cw - 12, y1 - 6)
            else:
                ruled(pg, bx + 12, top, bx + cw - 12, y1 - 6, gap=26)
    return title, sub, r


def tpl_month_grid_tracker(title, sub, rows_labels):
    """Grid tipo hábitos: filas etiquetadas x 31 columnas de dias, que llena
    el alto disponible, con una franja de notas debajo si sobra espacio."""
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        label_w = 155
        days = 31
        cw = (x1 - x0 - label_w) / days
        # cabecera de dias
        for d in range(days):
            cx = x0 + label_w + d * cw
            text(pg, cx, y0, str(d + 1), size=6.5, font=SANS, color=MUTED, align=1, w=cw)
        gy0 = y0 + 16
        n = max(len(rows_labels), 1)
        # el grid ocupa como mucho el 62% del alto; el resto -> notas
        grid_h = min((y1 - gy0) * 0.62, n * 40)
        rh = grid_h / n
        for i, lbl in enumerate(rows_labels):
            ry = gy0 + i * rh
            if i % 2 == 1:
                rect(pg, x0 + label_w, ry, x1, ry + rh, color=None, fill=FAINT, width=0)
            text(pg, x0, ry + rh / 2 - 6, lbl, size=9, font=SERIF, color=INK, w=label_w - 8)
            for d in range(days):
                cx = x0 + label_w + d * cw
                rect(pg, cx, ry, cx + cw, ry + rh, color=GRID, width=0.35)
        rect(pg, x0 + label_w, gy0, x1, gy0 + n * rh, color=LINE, width=0.7)
        # franja de notas debajo
        ny0 = gy0 + n * rh + 24
        if ny0 < y1 - 40:
            top = panel(pg, x0, ny0, x1, y1, label="NOTES & REFLECTIONS")
            ruled(pg, x0 + 12, top, x1 - 12, y1 - 6, gap=26)
    return title, sub, r


def tpl_dotgrid(title, sub):
    def r(pg):
        dotgrid(pg, MARGIN, body_top(), CONTENT_R, body_bottom())
    return title, sub, r


def tpl_squares(title, sub):
    def r(pg):
        squares(pg, MARGIN, body_top(), CONTENT_R, body_bottom())
    return title, sub, r


def tpl_iso(title, sub):
    def r(pg):
        isogrid(pg, MARGIN, body_top(), CONTENT_R, body_bottom())
    return title, sub, r


def tpl_cornell(title, sub):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        cue_w = (x1 - x0) * 0.28
        sum_h = 70
        line(pg, x0 + cue_w, y0, x0 + cue_w, y1 - sum_h, color=LINE, width=0.9)
        line(pg, x0, y1 - sum_h, x1, y1 - sum_h, color=LINE, width=0.9)
        text(pg, x0 + 4, y0 - 2, "Cues", size=8, font=SERIF_I, color=MUTED, w=cue_w)
        text(pg, x0 + cue_w + 8, y0 - 2, "Notes", size=8, font=SERIF_I, color=MUTED, w=200)
        text(pg, x0 + 4, y1 - sum_h + 4, "Summary", size=8, font=SERIF_I, color=MUTED, w=200)
        ruled(pg, x0 + cue_w + 8, y0 + 6, x1, y1 - sum_h, gap=26)
    return title, sub, r


def tpl_priority_matrix(title, sub):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        quad = [("URGENT + IMPORTANT", x0, y0), ("NOT URGENT + IMPORTANT", mx, y0),
                ("URGENT + NOT IMPORTANT", x0, my), ("NOT URGENT + NOT IMPORTANT", mx, my)]
        for label, qx, qy in quad:
            top = panel(pg, qx + 4, qy + 4, qx + (x1 - x0) / 2 - 4, qy + (y1 - y0) / 2 - 4, label=label)
            checkbox_rows(pg, qx + 14, top + 2, qx + (x1 - x0) / 2 - 14,
                          qy + (y1 - y0) / 2 - 10, gap=25)
    return title, sub, r


def tpl_vision(title, sub):
    def r(pg):
        x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
        cols, rows = 3, 2
        cw = (x1 - x0 - (cols - 1) * 16) / cols
        ch = (y1 - y0 - (rows - 1) * 16) / rows
        for i in range(6):
            r_ = i // cols
            c = i % cols
            bx = x0 + c * (cw + 16)
            by = y0 + r_ * (ch + 16)
            rect(pg, bx, by, bx + cw, by + ch, color=LINE, width=0.9, fill=FAINT)
            text(pg, bx, by + ch / 2 - 8, "+", size=20, font=SANS, color=LINE, align=1, w=cw)
    return title, sub, r


# ── Registro de categorias -> plantillas ─────────────────────────────────────
CATEGORIES = {
    "LIFE": ("Lifestyle", [
        tpl_checklist("Wishlist", "Things I want", cols=2),
        tpl_table("Birthdays & Dates", "Never miss an occasion",
                  [("Name", 3), ("Date", 2), ("Gift Idea", 3)]),
        tpl_table("Contacts", "People directory",
                  [("Name", 3), ("Phone", 2), ("Email", 3), ("Notes", 2)]),
        tpl_table("Book Log", "Reading tracker",
                  [("Title", 3), ("Author", 2), ("Rating", 1), ("Notes", 2)]),
        tpl_table("Watchlist", "Movies & shows",
                  [("Title", 3), ("Platform", 2), ("Rating", 1), ("Done", 1)]),
        tpl_two_panels("Trip Planner", "Plan your getaway", "ITINERARY", "PACKING LIST",
                       l_kind="lined", r_kind="check"),
        tpl_checklist("Packing Checklist", "Don't forget a thing", cols=2),
        tpl_table("Password Tracker", "Keep logins safe",
                  [("Site / App", 3), ("Username", 3), ("Notes", 2)]),
        tpl_month_grid_tracker("Cleaning Schedule", "Home routine",
                               ["Kitchen", "Bathroom", "Bedrooms", "Floors",
                                "Laundry", "Dusting", "Trash", "Windows"]),
        tpl_table("Parcel Tracker", "Incoming orders",
                  [("Item", 3), ("Store", 2), ("Order #", 2), ("Arrival", 2)]),
    ]),
    "BODY": ("Wellness", [
        tpl_two_panels("Weekly Meal Planner", "Plan your meals", "MEALS", "GROCERY LIST",
                       l_kind="lined", r_kind="check"),
        tpl_checklist("Grocery List", "Shopping made simple", cols=2),
        tpl_table("Recipe Log", "Favorite recipes",
                  [("Recipe", 3), ("Source", 2), ("Rating", 1), ("Notes", 2)]),
        tpl_month_grid_tracker("Mood Tracker", "How you feel each day",
                               ["Happy", "Calm", "Anxious", "Tired", "Energetic",
                                "Sad", "Motivated", "Stressed"]),
        tpl_month_grid_tracker("Sleep Tracker", "Hours & quality",
                               ["<5h", "5-6h", "6-7h", "7-8h", "8-9h", ">9h",
                                "Nap", "Good Quality"]),
        tpl_month_grid_tracker("Water Tracker", "8 glasses a day",
                               [f"Glass {i + 1}" for i in range(8)]),
        tpl_table("Workout Log", "Move your body",
                  [("Date", 2), ("Workout", 3), ("Duration", 1), ("Notes", 2)]),
        tpl_month_grid_tracker("Symptom Tracker", "Track how you feel",
                               ["Headache", "Fatigue", "Nausea", "Pain", "Fever",
                                "Cough", "Other 1", "Other 2"]),
        tpl_month_grid_tracker("Period Tracker", "Cycle overview",
                               ["Period", "Cramps", "Mood swings", "Cravings",
                                "Fatigue", "Headache", "Bloating", "PMS"]),
        tpl_month_grid_tracker("Vitamins & Meds", "Daily intake",
                               ["Multivitamin", "Vitamin D", "Omega-3", "Magnesium",
                                "Probiotic", "Med 1", "Med 2", "Water"]),
    ]),
    "MIND": ("Self-Care", [
        tpl_lined("Gratitude Journal", "Three things a day", gap=30),
        tpl_checklist("Bucket List", "Dreams to chase", cols=2),
        tpl_lined("Favorite Quotes", "Words that inspire", gap=30),
        tpl_lined("Letter to Myself", "A note for the future", gap=28),
        tpl_vision("Vision Board", "Picture your dream life"),
        tpl_lined("Dream Journal", "Capture your dreams", gap=26),
        tpl_month_grid_tracker("Self-Care Tracker", "Small acts of care",
                               ["Meditate", "Read", "Walk outside", "Journal",
                                "Digital detox", "Early night", "Hobby", "Rest"]),
        tpl_lined("Daily Affirmations", "I am...", gap=30),
    ]),
    "WORK": ("Productivity", [
        tpl_checklist("Master To-Do List", "Everything in one place", cols=2),
        tpl_priority_matrix("Priority Matrix", "Eisenhower method"),
        tpl_month_grid_tracker("Habit Tracker", "Build your routines",
                               [f"Habit {i + 1}" for i in range(10)]),
        tpl_table("Time Tracker", "Where your hours go",
                  [("Activity", 3), ("Start", 1), ("End", 1), ("Total", 1), ("Category", 2)]),
        tpl_lined("Meeting Notes", "Capture the essentials", gap=26),
        tpl_two_panels("SMART Goals", "Specific & measurable", "GOAL & WHY", "ACTION STEPS",
                       l_kind="lined", r_kind="check"),
        tpl_two_panels("Project Planner", "Break it down", "MILESTONES", "TASKS",
                       l_kind="lined", r_kind="check"),
        tpl_month_grid_tracker("30-Day Challenge", "One month, one goal",
                               [f"Day {i + 1}-{i + 8}" for i in range(0, 30, 8)] + ["Reward"]),
        tpl_table("Appointment Tracker", "Upcoming commitments",
                  [("Date", 2), ("Time", 1), ("With", 2), ("Location", 2), ("Notes", 2)]),
    ]),
    "MONEY": ("Finance", [
        tpl_two_panels("Finance Overview", "Money at a glance", "INCOME", "EXPENSES",
                       l_kind="lined", r_kind="lined"),
        tpl_table("Monthly Budget", "Plan every dollar",
                  [("Category", 3), ("Budgeted", 2), ("Actual", 2), ("Difference", 2)]),
        tpl_table("Expense Tracker", "Track your spending",
                  [("Date", 2), ("Description", 3), ("Category", 2), ("Amount", 2)]),
        tpl_two_panels("Savings Goals", "Reach your targets", "GOALS & TARGETS", "PROGRESS",
                       l_kind="lined", r_kind="check"),
        tpl_table("Bills Tracker", "Never miss a payment",
                  [("Bill", 3), ("Due Date", 2), ("Amount", 2), ("Paid", 1)]),
        tpl_table("Subscriptions", "Recurring costs",
                  [("Service", 3), ("Renewal", 2), ("Amount", 2), ("Cancel?", 1)]),
        tpl_table("Debt Payoff", "Get to zero",
                  [("Debt", 3), ("Balance", 2), ("Rate", 1), ("Min. Pay", 2)]),
        tpl_table("Sinking Funds", "Save for the expected",
                  [("Fund", 3), ("Goal", 2), ("Saved", 2), ("Left", 2)]),
        tpl_month_grid_tracker("No-Spend Challenge", "Days without spending",
                               [f"Week {i + 1}" for i in range(5)] + ["Reward"]),
        tpl_table("Investment Tracker", "Grow your wealth",
                  [("Asset", 3), ("Amount", 2), ("Value", 2), ("Change", 2)]),
    ]),
    "NOTE": ("Notes", [
        tpl_dotgrid("Dot Grid Notes", "Freeform dotted page"),
        tpl_squares("Grid Notes", "Squared page"),
        tpl_lined("Lined Notes", "Classic ruled page", gap=26),
        tpl_cornell("Cornell Notes", "Cues · Notes · Summary"),
        tpl_iso("Isometric Notes", "3D & engineering grid"),
        tpl_lined("Meeting Notes", "Ruled with wide spacing", gap=30),
        tpl_dotgrid("Brainstorm", "Mind-map on dots"),
        tpl_squares("Project Grid", "Squared planning page"),
    ]),
}


# ═════════════════════════════════════════════════════════════════════════════
#  SPINE + BUILD (dos pasadas)
# ═════════════════════════════════════════════════════════════════════════════
def build():
    spine = []  # (pid, render_fn(pg, pidx, meta), meta)

    def add(pid, render, **meta):
        spine.append((pid, render, meta))

    # Dashboard + calendario
    add("dashboard", r_dashboard)
    add("year_hub", r_year_hub)
    add("year_glance", r_year_glance)
    add("year_goals", r_year_goals)
    add("year_review", r_year_review)
    add("key_dates", r_key_dates)
    add("highlights", r_highlights)
    for q in range(1, 5):
        add(f"quarter_{q}", make_quarter(q))
    for m in range(1, N_MONTHLY + 1):
        add(f"month_{m}", make_month(m))
    for w in range(1, N_WEEKLY + 1):
        add(f"week_{w}", make_week(w))
    for d in range(1, N_DAILY + 1):
        add(f"day_{d}", make_day(d))

    # Categorias: hub + plantillas
    for cat_key, (cat_name, templates) in CATEGORIES.items():
        item_ids = [f"{cat_key}_{i}" for i in range(len(templates))]
        item_labels = [t[0] for t in templates]

        def make_hub(cat_name=cat_name, item_ids=item_ids, item_labels=item_labels,
                     cat_key=cat_key, templates=templates):
            def render(pg, pidx, meta):
                header(pg, cat_name.upper(), "TAP A TEMPLATE")
                chrome(pg, pidx, active=f"hub_{cat_key}")
                x0, y0, x1, y1 = MARGIN, body_top(), CONTENT_R, body_bottom()
                cols = 2
                cw = (x1 - x0 - 20) / cols
                n = len(item_ids)
                rows = (n + cols - 1) // cols
                ch = min(64, (y1 - y0 - (rows - 1) * 10) / rows)
                for i, (iid, lbl) in enumerate(zip(item_ids, item_labels)):
                    r_ = i // cols
                    c = i % cols
                    bx = x0 + c * (cw + 20)
                    by = y0 + r_ * (ch + 10)
                    pill_link(pg, bx, by, bx + cw, by + ch, lbl, pidx, iid,
                              sub=templates[i][1])
            return render

        add(f"hub_{cat_key}", make_hub())
        for i, (title, sub, tpl_render) in enumerate(templates):
            def make_tpl(title=title, sub=sub, tpl_render=tpl_render, cat_key=cat_key):
                def render(pg, pidx, meta):
                    header(pg, title.upper(), sub)
                    chrome(pg, pidx, active=f"hub_{cat_key}")
                    tpl_render(pg)
                return render
            add(f"{cat_key}_{i}", make_tpl())

    # Pasada 1: indice de paginas
    pidx = {pid: i for i, (pid, _, _) in enumerate(spine)}

    # Crear paginas en blanco
    doc = fitz.open()
    for _ in spine:
        doc.new_page(width=PW, height=PH)

    # Pasada 2: render
    for i, (pid, render, meta) in enumerate(spine):
        pg = doc[i]
        rect(pg, 0, 0, PW, PH, fill=WHITE, width=0)
        render(pg, pidx, meta)

    doc.save(OUT_PDF, deflate=True, garbage=4)
    n = len(spine)
    doc.close()
    size_mb = os.path.getsize(OUT_PDF) / 1e6
    print(f"OK  {OUT_PDF}")
    print(f"    {n} paginas · {size_mb:.1f} MB")
    return n, size_mb


if __name__ == "__main__":
    build()
