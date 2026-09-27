"""
2027 STEM Planner — dated, hyperlinked digital planner (GoodNotes / Notability).

Landscape letter pages (vector PDF, Base-14 serif type like the undated STEM
Focus Planner). Side tabs on every page link to index, year, the 12 months,
tools and notes. Month calendars link every date to its weekly spread.

  python build_planner_2027.py        # -> out/2027_STEM_Planner_{Monday,Sunday}_Start.pdf
"""
import os, sys, math, calendar, datetime as dt
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
LOGO = os.path.join(REPO, "mathrelaxing_logo.png")
YEAR = 2027

PW, PH = 792.0, 612.0
TAB_W = 46.0
X0, X1 = 36.0, PW - TAB_W - 18
Y0, Y1 = 30.0, PH - 30


def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


NAVY = hx("#18223f"); GOLD = hx("#c9a24b"); CREAM = hx("#faf7f0"); INK = hx("#26262a")
MUTED = hx("#8a857a"); LINE = hx("#dcd5c6"); SOFT = hx("#efe9dc"); TEAL = hx("#2a7f78"); RED = hx("#a8323e")
SERIF, SERIF_B, SERIF_I = "times-roman", "times-bold", "times-italic"
MONTHS = [calendar.month_name[m] for m in range(1, 13)]
MON_ABBR = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


# ---------------------------------------------------------------- page map
class Plan:
    def __init__(self, first_weekday):
        self.fw = first_weekday  # 0 = Monday, 6 = Sunday
        self.order = []          # list of (kind, arg)
        add = self.order.append
        for k in ("cover", "index", "goals", "year", "sem_spring", "sem_fall"):
            add((k, None))
        for m in range(1, 13):
            add(("month", m)); add(("habits", m))
        self.weeks = self._weeks()
        for i in range(len(self.weeks)):
            add(("week", i))
        self.tools = ["assignments", "exams", "grades", "study", "project", "lab", "reading", "cornell", "formula"]
        for t in self.tools:
            add(("tool", t))
        self.notes = ["graph", "graph", "graph", "dot", "dot", "dot", "lined", "lined"]
        for n in self.notes:
            add(("note", n))
        self.idx = {}
        for i, key in enumerate(self.order):
            self.idx.setdefault(key, i)

    def _weeks(self):
        d = dt.date(YEAR, 1, 1)
        start = d - dt.timedelta(days=(d.weekday() - self.fw) % 7)
        weeks = []
        while start <= dt.date(YEAR, 12, 31):
            weeks.append(start); start += dt.timedelta(days=7)
        return weeks

    def week_of(self, day):
        for i, s in enumerate(self.weeks):
            if s <= day < s + dt.timedelta(days=7):
                return i
        return None

    def page(self, kind, arg=None):
        return self.idx[(kind, arg)]

    def first(self, kind):
        return next(i for i, (k, _) in enumerate(self.order) if k == kind)


# ---------------------------------------------------------------- drawing helpers
def link(page, rect, target):
    page.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(rect), "page": target, "to": fitz.Point(0, 0)})


def text(page, x, y, s, size=10, font=SERIF, color=INK):
    page.insert_text((x, y), s, fontsize=size, fontname=font, color=color)


def ctext(page, rect, s, size=10, font=SERIF, color=INK, align=1):
    r = fitz.Rect(rect)
    # vertical centring for single lines
    h = size * 1.25
    rr = fitz.Rect(r.x0, r.y0 + (r.height - h) / 2 - 1, r.x1, r.y1 + 4)
    page.insert_textbox(rr, s, fontsize=size, fontname=font, color=color, align=align)


def box(page, r, color=LINE, width=0.8, fill=None, radius=None):
    page.draw_rect(fitz.Rect(r), color=color, fill=fill, width=width, radius=radius)


def hline(page, y, x0=X0, x1=X1, color=LINE, width=0.6):
    page.draw_line((x0, y), (x1, y), color=color, width=width)


def lines(page, r, gap=18, color=LINE):
    r = fitz.Rect(r); y = r.y0 + gap
    while y < r.y1 - 2:
        hline(page, y, r.x0, r.x1, color); y += gap


def checkbox(page, x, y, s=8):
    page.draw_rect(fitz.Rect(x, y, x + s, y + s), color=MUTED, width=0.7)


def header(page, title, sub=None):
    text(page, X0, Y0 + 26, title, 24, SERIF_B, NAVY)
    if sub:
        w = fitz.get_text_length(title, fontname=SERIF_B, fontsize=24)
        text(page, X0 + w + 14, Y0 + 26, sub, 12, SERIF_I, GOLD)
    hline(page, Y0 + 36, color=GOLD, width=1.2)


def background(page):
    page.draw_rect(page.rect, color=None, fill=CREAM, width=0)


def tabs(page, plan, active=None):
    x0 = PW - TAB_W; items = [("IDX", plan.page("index"), "index"), ("YR", plan.page("year"), "year")]
    items += [(MON_ABBR[m - 1], plan.page("month", m), m) for m in range(1, 13)]
    items += [("TOOLS", plan.first("tool"), "tool"), ("NOTES", plan.first("note"), "note")]
    n = len(items); h = (PH - 24) / n
    for i, (lab, tgt, key) in enumerate(items):
        r = fitz.Rect(x0 + 4, 12 + i * h + 1.2, PW - 4, 12 + (i + 1) * h - 1.2)
        on = key == active
        page.draw_rect(r, color=None, fill=GOLD if on else NAVY, width=0, radius=0.18)
        ctext(page, r, lab, 7.2 if len(lab) > 2 else 9, SERIF_B, NAVY if on else CREAM)
        link(page, r, tgt)


def footer(page):
    text(page, X0, PH - 12, f"{YEAR} STEM Planner  ·  MathRelaxing", 7, SERIF_I, MUTED)


# ---------------------------------------------------------------- pages
def lorenz_points(n=9000):
    x, y, z = 0.1, 0.0, 0.0; pts = []; dtt = 0.006
    for _ in range(n):
        dx = 10 * (y - x); dy = x * (28 - z) - y; dz = x * y - 8 / 3 * z
        x += dx * dtt; y += dy * dtt; z += dz * dtt
        pts.append((x, z))
    return pts


def draw_cover(page, plan):
    page.draw_rect(page.rect, color=None, fill=NAVY, width=0)
    pts = lorenz_points()
    xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
    sx = 300 / (max(xs) - min(xs)); sz = 260 / (max(zs) - min(zs))
    cx, cy = PW * 0.70, PH * 0.47
    poly = [(cx + (p[0] - (max(xs) + min(xs)) / 2) * sx, cy - (p[1] - (max(zs) + min(zs)) / 2) * sz) for p in pts]
    for i in range(0, len(poly) - 40, 40):
        page.draw_polyline(poly[i:i + 41], color=GOLD, width=0.45)
    text(page, 60, 220, str(YEAR), 96, SERIF_B, CREAM)
    text(page, 64, 270, "STEM PLANNER", 30, SERIF_B, CREAM)
    text(page, 64, 300, "Hyperlinked digital planner for students & researchers", 13, SERIF_I, GOLD)
    start = "Monday" if plan.fw == 0 else "Sunday"
    text(page, 64, 322, f"January – December {YEAR}  ·  {start} start  ·  GoodNotes · Notability", 10.5, SERIF, CREAM)
    page.draw_rect(fitz.Rect(0, PH - 56, PW, PH), color=None, fill=(0, 0, 0), width=0)
    if os.path.exists(LOGO):
        page.insert_image(fitz.Rect(PW / 2 - 70, PH - 50, PW / 2 + 70, PH - 6), filename=LOGO, keep_proportion=True)
    link(page, fitz.Rect(40, 140, 420, 340), plan.page("index"))


def draw_index(page, plan):
    background(page); header(page, "Index", f"{YEAR} STEM Planner"); tabs(page, plan, "index")
    items = [("Goals " + str(YEAR), plan.page("goals")), ("Year at a Glance", plan.page("year")),
             ("Spring Semester", plan.page("sem_spring")), ("Fall Semester", plan.page("sem_fall"))]
    items += [(t.title(), plan.page("tool", t)) for t in plan.tools]
    items += [("Graph Notes", plan.first("note")), ("Weekly Spreads", plan.first("week"))]
    names = {"Assignments": "Assignment Tracker", "Exams": "Exam Planner", "Grades": "Grade & GPA Tracker",
             "Study": "Study Session Log", "Project": "Project Planner", "Lab": "Lab Notebook",
             "Reading": "Reading & Research Log", "Cornell": "Cornell Notes", "Formula": "Formula Sheet"}
    cols, bw, bh = 3, (X1 - X0 - 24) / 3, 30
    for i, (lab, tgt) in enumerate(items):
        c, r = i % cols, i // cols
        rect = fitz.Rect(X0 + c * (bw + 12), 90 + r * (bh + 12), X0 + c * (bw + 12) + bw, 90 + r * (bh + 12) + bh)
        box(page, rect, NAVY, 1.0, SOFT, 0.25)
        ctext(page, rect, names.get(lab, lab), 11.5, SERIF_B, NAVY)
        link(page, rect, tgt)
    y = 90 + ((len(items) + cols - 1) // cols) * (bh + 12) + 14
    text(page, X0, y, "Months", 13, SERIF_B, NAVY); y += 10
    mw = (X1 - X0 - 11 * 6) / 12
    for m in range(12):
        rect = fitz.Rect(X0 + m * (mw + 6), y, X0 + m * (mw + 6) + mw, y + 34)
        box(page, rect, GOLD, 1.0, None, 0.25)
        ctext(page, rect, MONTHS[m][:3].upper(), 11, SERIF_B, NAVY)
        link(page, rect, plan.page("month", m + 1))
    footer(page)


def draw_goals(page, plan):
    background(page); header(page, f"Goals {YEAR}", "aim, plan, measure"); tabs(page, plan)
    labels = ["Academic", "Research & Projects", "Skills to Learn", "Personal & Health"]
    w, h = (X1 - X0 - 16) / 2, (Y1 - 120 - 16) / 2
    for i, lab in enumerate(labels):
        c, r = i % 2, i // 2
        rect = fitz.Rect(X0 + c * (w + 16), 84 + r * (h + 16), X0 + c * (w + 16) + w, 84 + r * (h + 16) + h)
        box(page, rect, LINE, 0.9, None, 0.04)
        text(page, rect.x0 + 10, rect.y0 + 18, lab, 13, SERIF_B, NAVY)
        for k in range(5):
            yy = rect.y0 + 40 + k * 22
            if yy > rect.y1 - 8: break
            checkbox(page, rect.x0 + 10, yy - 8); hline(page, yy, rect.x0 + 24, rect.x1 - 10)
    text(page, X0, Y1 - 6, f"My word for {YEAR}: ______________________", 12, SERIF_I, MUTED)
    footer(page)


def mini_month(page, plan, m, rect):
    r = fitz.Rect(rect)
    ctext(page, fitz.Rect(r.x0, r.y0, r.x1, r.y0 + 16), MONTHS[m - 1].upper(), 10, SERIF_B, NAVY)
    cal = calendar.Calendar(plan.fw)
    days = ["M", "T", "W", "T", "F", "S", "S"] if plan.fw == 0 else ["S", "M", "T", "W", "T", "F", "S"]
    cw = r.width / 7; y = r.y0 + 22
    for i, dname in enumerate(days):
        ctext(page, fitz.Rect(r.x0 + i * cw, y, r.x0 + (i + 1) * cw, y + 10), dname, 7, SERIF_B, GOLD)
    y += 13
    for week in cal.monthdayscalendar(YEAR, m):
        for i, dd in enumerate(week):
            if dd:
                ctext(page, fitz.Rect(r.x0 + i * cw, y, r.x0 + (i + 1) * cw, y + 10), str(dd), 7.5, SERIF, INK)
        y += 12
    link(page, r, plan.page("month", m))


def draw_year(page, plan):
    background(page); header(page, "Year at a Glance", str(YEAR)); tabs(page, plan, "year")
    cols, rows = 4, 3
    w, h = (X1 - X0 - 3 * 20) / 4, (Y1 - 84 - 2 * 14) / 3
    for m in range(1, 13):
        c, r = (m - 1) % cols, (m - 1) // cols
        rect = fitz.Rect(X0 + c * (w + 20), 84 + r * (h + 14), X0 + c * (w + 20) + w, 84 + r * (h + 14) + h)
        box(page, rect, LINE, 0.7, None, 0.05)
        mini_month(page, plan, m, fitz.Rect(rect.x0 + 6, rect.y0 + 6, rect.x1 - 6, rect.y1 - 4))
    footer(page)


def table(page, cols, y0, rows, row_h=20, widths=None):
    widths = widths or [1] * len(cols)
    tot = sum(widths); W = X1 - X0; xs = [X0]
    for w in widths:
        xs.append(xs[-1] + W * w / tot)
    page.draw_rect(fitz.Rect(X0, y0, X1, y0 + row_h), color=None, fill=NAVY, width=0)
    for i, c in enumerate(cols):
        ctext(page, fitz.Rect(xs[i] + 4, y0, xs[i + 1] - 4, y0 + row_h), c, 9.5, SERIF_B, CREAM, 0)
    y = y0 + row_h
    for k in range(rows):
        if k % 2:
            page.draw_rect(fitz.Rect(X0, y, X1, y + row_h), color=None, fill=SOFT, width=0)
        hline(page, y + row_h, color=LINE); y += row_h
    for x in xs[1:-1]:
        page.draw_line((x, y0 + row_h), (x, y), color=LINE, width=0.5)
    box(page, (X0, y0, X1, y), LINE, 0.8)
    return xs, y


def draw_semester(page, plan, name):
    background(page); header(page, f"{name} Semester", str(YEAR)); tabs(page, plan)
    _, y = table(page, ["Course", "Code", "Credits", "Instructor", "Exam dates", "Target"], 80, 9, 22,
                 [3, 1.3, 1, 2.2, 2.2, 1.2])
    w = (X1 - X0 - 16) / 2
    for i, lab in enumerate(["Key dates & deadlines", "Semester focus"]):
        rect = fitz.Rect(X0 + i * (w + 16), y + 18, X0 + i * (w + 16) + w, Y1 - 4)
        box(page, rect, LINE, 0.8, None, 0.04)
        text(page, rect.x0 + 10, rect.y0 + 16, lab, 12, SERIF_B, NAVY)
        lines(page, fitz.Rect(rect.x0 + 10, rect.y0 + 22, rect.x1 - 10, rect.y1 - 4), 18)
    footer(page)


def draw_month(page, plan, m):
    background(page); header(page, MONTHS[m - 1], str(YEAR)); tabs(page, plan, m)
    days = list(calendar.day_name); days = days if plan.fw == 0 else days[6:] + days[:6]
    gx0, gx1 = X0, X1 - 118
    cw = (gx1 - gx0) / 7
    for i, d in enumerate(days):
        ctext(page, fitz.Rect(gx0 + i * cw, 74, gx0 + (i + 1) * cw, 88), d.upper()[:3], 9, SERIF_B, GOLD)
    weeks = calendar.Calendar(plan.fw).monthdatescalendar(YEAR, m)
    rh = (Y1 - 92) / len(weeks)
    for r, week in enumerate(weeks):
        for i, day in enumerate(week):
            rect = fitz.Rect(gx0 + i * cw, 92 + r * rh, gx0 + (i + 1) * cw, 92 + (r + 1) * rh)
            inm = day.month == m
            box(page, rect, LINE, 0.7, None if inm else SOFT)
            text(page, rect.x0 + 5, rect.y0 + 13, str(day.day), 11 if inm else 9, SERIF_B if inm else SERIF,
                 NAVY if inm else MUTED)
            wi = plan.week_of(day)
            if wi is not None:
                link(page, rect, plan.page("week", wi))
    side = fitz.Rect(X1 - 108, 74, X1, Y1)
    box(page, side, LINE, 0.8, None, 0.04)
    text(page, side.x0 + 8, side.y0 + 16, "Focus", 12, SERIF_B, NAVY)
    lines(page, fitz.Rect(side.x0 + 8, side.y0 + 22, side.x1 - 8, side.y0 + 200), 18)
    text(page, side.x0 + 8, side.y0 + 222, "Deadlines", 12, SERIF_B, NAVY)
    lines(page, fitz.Rect(side.x0 + 8, side.y0 + 228, side.x1 - 8, side.y1 - 6), 18)
    hr = fitz.Rect(side.x0 + 8, Y1 - 4, side.x1 - 8, Y1 + 10)
    ctext(page, hr, "habit tracker »", 8.5, SERIF_I, TEAL); link(page, hr, plan.page("habits", m))
    footer(page)


def draw_habits(page, plan, m):
    background(page); header(page, f"{MONTHS[m - 1]} Habits", str(YEAR)); tabs(page, plan, m)
    nd = calendar.monthrange(YEAR, m)[1]
    lw = 150; cw = (X1 - X0 - lw) / nd; y0 = 84
    for d in range(1, nd + 1):
        ctext(page, fitz.Rect(X0 + lw + (d - 1) * cw, y0, X0 + lw + d * cw, y0 + 12), str(d), 7, SERIF_B, GOLD)
    rows = 14; rh = (Y1 - 110 - y0) / rows
    for r in range(rows):
        y = y0 + 16 + r * rh
        if r % 2:
            page.draw_rect(fitz.Rect(X0, y, X1, y + rh), color=None, fill=SOFT, width=0)
        hline(page, y + rh, color=LINE)
        for d in range(nd):
            cx = X0 + lw + d * cw + cw / 2
            page.draw_circle((cx, y + rh / 2), min(cw, rh) * 0.28, color=LINE, width=0.6)
    text(page, X0, Y1 - 70, "Monthly reflection", 12, SERIF_B, NAVY)
    lines(page, fitz.Rect(X0, Y1 - 64, X1, Y1), 18)
    ml = fitz.Rect(X1 - 120, Y0 + 12, X1, Y0 + 30)
    ctext(page, ml, "« back to month", 8.5, SERIF_I, TEAL, 2); link(page, ml, plan.page("month", m))
    footer(page)


def draw_week(page, plan, i):
    s = plan.weeks[i]; e = s + dt.timedelta(days=6)
    rng = f"{s.day} {s.strftime('%b')} – {e.day} {e.strftime('%b')} {e.year}"
    background(page); header(page, f"Week {i + 1:02d}", rng)
    mid = s + dt.timedelta(days=3); tabs(page, plan, mid.month if mid.year == YEAR else None)
    days = [s + dt.timedelta(days=k) for k in range(7)]
    w = (X1 - X0 - 3 * 10) / 4; h = (Y1 - 80 - 10) / 2
    for k, day in enumerate(days):
        c, r = k % 4, k // 4
        rect = fitz.Rect(X0 + c * (w + 10), 80 + r * (h + 10), X0 + c * (w + 10) + w, 80 + r * (h + 10) + h)
        box(page, rect, LINE, 0.8, None, 0.04)
        page.draw_rect(fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + 22), color=None,
                       fill=NAVY if day.year == YEAR else MUTED, width=0, radius=0.2)
        text(page, rect.x0 + 8, rect.y0 + 15, day.strftime("%A").upper(), 9.5, SERIF_B, CREAM)
        dn = f"{day.day} {day.strftime('%b')}"
        text(page, rect.x1 - 8 - fitz.get_text_length(dn, fontname=SERIF_B, fontsize=9.5), rect.y0 + 15, dn, 9.5, SERIF_B, GOLD)
        lines(page, fitz.Rect(rect.x0 + 8, rect.y0 + 26, rect.x1 - 8, rect.y1 - 4), 17)
    rect = fitz.Rect(X0 + 3 * (w + 10), 80 + h + 10, X1, Y1)
    box(page, rect, GOLD, 1.0, SOFT, 0.04)
    text(page, rect.x0 + 8, rect.y0 + 16, "Top 3 priorities", 11, SERIF_B, NAVY)
    for k in range(3):
        yy = rect.y0 + 34 + k * 20; checkbox(page, rect.x0 + 8, yy - 8); hline(page, yy, rect.x0 + 22, rect.x1 - 8)
    text(page, rect.x0 + 8, rect.y0 + 112, "Study hours", 11, SERIF_B, NAVY)
    for k in range(7):
        page.draw_rect(fitz.Rect(rect.x0 + 8 + k * 22, rect.y0 + 120, rect.x0 + 26 + k * 22, rect.y0 + 138), color=LINE, width=0.7)
        ctext(page, fitz.Rect(rect.x0 + 8 + k * 22, rect.y0 + 140, rect.x0 + 26 + k * 22, rect.y0 + 150), "MTWTFSS"[k] if plan.fw == 0 else "SMTWTFS"[k], 6.5, SERIF_B, MUTED)
    text(page, rect.x0 + 8, rect.y0 + 170, "Notes", 11, SERIF_B, NAVY)
    lines(page, fitz.Rect(rect.x0 + 8, rect.y0 + 176, rect.x1 - 8, rect.y1 - 4), 16)
    # prev / next
    if i > 0:
        r = fitz.Rect(X1 - 150, Y0 + 12, X1 - 80, Y0 + 30); ctext(page, r, "« prev week", 8.5, SERIF_I, TEAL); link(page, r, plan.page("week", i - 1))
    if i < len(plan.weeks) - 1:
        r = fitz.Rect(X1 - 75, Y0 + 12, X1, Y0 + 30); ctext(page, r, "next week »", 8.5, SERIF_I, TEAL); link(page, r, plan.page("week", i + 1))
    footer(page)


TOOL_TITLES = {"assignments": ("Assignment Tracker", "never miss a due date"),
               "exams": ("Exam Planner", "plan the revision, not the panic"),
               "grades": ("Grade & GPA Tracker", "weighted = weight × score ÷ 100"),
               "study": ("Study Session Log", "25-minute focus blocks"),
               "project": ("Project Planner", "from idea to done"),
               "lab": ("Lab Notebook", "record it while it happens"),
               "reading": ("Reading & Research Log", "papers, books, sources"),
               "cornell": ("Cornell Notes", "cue · notes · summary"),
               "formula": ("Formula Sheet", "equations & constants")}


def draw_tool(page, plan, t):
    title, sub = TOOL_TITLES[t]
    background(page); header(page, title, sub); tabs(page, plan, "tool")
    if t == "assignments":
        xs, y = table(page, ["Course", "Assignment", "Due", "Done", "Grade"], 80, 21, 21, [2, 4, 1.3, 0.8, 1])
        for k in range(21): checkbox(page, (xs[3] + xs[4]) / 2 - 4, 80 + 21 * (k + 1) + 6.5)
    elif t == "exams":
        w = (X1 - X0 - 20) / 3
        for c in range(3):
            rect = fitz.Rect(X0 + c * (w + 10), 80, X0 + c * (w + 10) + w, Y1 - 4)
            box(page, rect, LINE, 0.9, None, 0.04)
            y = rect.y0 + 18
            for lab in ("Subject", "Date & time", "Room"):
                text(page, rect.x0 + 8, y, lab + ":", 10, SERIF_B, NAVY); hline(page, y + 2, rect.x0 + 80, rect.x1 - 8); y += 22
            text(page, rect.x0 + 8, y + 6, "Topics to review", 11, SERIF_B, NAVY); y += 16
            for k in range(8):
                yy = y + 8 + k * 19; checkbox(page, rect.x0 + 8, yy - 8); hline(page, yy, rect.x0 + 22, rect.x1 - 8)
            y += 8 + 8 * 19 + 14
            text(page, rect.x0 + 8, y, "Study plan (days before)", 11, SERIF_B, NAVY)
            lines(page, fitz.Rect(rect.x0 + 8, y + 4, rect.x1 - 8, rect.y1 - 4), 18)
    elif t == "grades":
        table(page, ["Course", "Assessment", "Weight %", "Score %", "Weighted"], 80, 18, 21, [2, 3, 1, 1, 1])
        text(page, X0, Y1 - 8, "Course total = sum of weighted scores.   GPA: ______", 10.5, SERIF_I, MUTED)
    elif t == "study":
        xs, y = table(page, ["Date", "Subject", "Focus goal", "Focus blocks", "Min"], 80, 20, 22, [1.1, 1.8, 3, 3, 0.8])
        for k in range(20):
            yy = 80 + 22 * (k + 1) + 11
            for b in range(8):
                page.draw_circle((xs[3] + 14 + b * ((xs[4] - xs[3] - 20) / 8), yy), 5, color=RED, width=0.7)
    elif t == "project":
        y = 80
        for lab in ("Project", "Goal", "Deadline"):
            text(page, X0, y + 14, lab + ":", 11, SERIF_B, NAVY); hline(page, y + 16, X0 + 70, X1); y += 26
        xs, y2 = table(page, ["Milestone", "Owner", "Due", "Done"], y + 12, 6, 21, [5, 1.6, 1.3, 0.8])
        for k in range(6): checkbox(page, (xs[3] + xs[4]) / 2 - 4, y + 12 + 21 * (k + 1) + 6.5)
        text(page, X0, y2 + 20, "Tasks & notes", 11, SERIF_B, NAVY)
        lines(page, fitz.Rect(X0, y2 + 26, X1, Y1), 18)
    elif t == "lab":
        lw = (X1 - X0) * 0.42
        y = 80
        for lab, hgt in (("Title / Date", 30), ("Objective", 50), ("Materials", 56), ("Method", 90), ("Observations", 92)):
            text(page, X0, y + 12, lab, 11, SERIF_B, NAVY)
            lines(page, fitz.Rect(X0, y + 14, X0 + lw, y + 14 + hgt), 17); y += hgt + 20
        gx0 = X0 + lw + 16; g = 10
        text(page, gx0, 92, "Data · sketch · graph", 11, SERIF_B, NAVY)
        grid(page, fitz.Rect(gx0, 100, X1, Y1), g)
    elif t == "reading":
        xs, y = table(page, ["Title", "Author(s)", "Year", "Key idea / result", "Cited"], 80, 20, 22, [3, 2, 0.8, 4, 0.8])
        for k in range(20): checkbox(page, (xs[4] + xs[5]) / 2 - 4, 80 + 22 * (k + 1) + 7)
    elif t == "cornell":
        cue = X0 + (X1 - X0) * 0.28
        text(page, X0, 84, "Topic:", 11, SERIF_B, NAVY); hline(page, 86, X0 + 44, X1 - 150)
        text(page, X1 - 140, 84, "Date:", 11, SERIF_B, NAVY); hline(page, 86, X1 - 104, X1)
        page.draw_line((cue, 96), (cue, Y1 - 96), color=GOLD, width=1.1)
        hline(page, Y1 - 96, color=GOLD, width=1.1)
        text(page, X0, 110, "Cues / questions", 10, SERIF_I, MUTED); text(page, cue + 10, 110, "Notes", 10, SERIF_I, MUTED)
        lines(page, fitz.Rect(cue + 10, 114, X1, Y1 - 100), 18)
        text(page, X0, Y1 - 80, "Summary", 11, SERIF_B, NAVY); lines(page, fitz.Rect(X0, Y1 - 76, X1, Y1), 18)
    elif t == "formula":
        grid(page, fitz.Rect(X0, 80, X1, Y1), 14, soft=True)
        consts = ["pi = 3.14159", "e = 2.71828", "golden ratio = 1.61803", "c = 2.998 × 10^8 m/s", "g = 9.81 m/s²"]
        text(page, X0 + 6, 98, "Handy constants:   " + "    ".join(consts), 8.5, SERIF_I, MUTED)
    footer(page)


def grid(page, r, g, soft=False):
    r = fitz.Rect(r); col = SOFT if soft else LINE
    x = r.x0
    while x <= r.x1 + 0.1:
        page.draw_line((x, r.y0), (x, r.y1), color=col, width=0.4); x += g
    y = r.y0
    while y <= r.y1 + 0.1:
        page.draw_line((r.x0, y), (r.x1, y), color=col, width=0.4); y += g


def draw_note(page, plan, kind):
    title = {"graph": "Graph Paper", "dot": "Dot Grid", "lined": "Lined Notes"}[kind]
    background(page); header(page, title, "notes"); tabs(page, plan, "note")
    r = fitz.Rect(X0, 76, X1, Y1)
    if kind == "graph":
        grid(page, r, 14.17)   # 5 mm
    elif kind == "dot":
        y = r.y0
        while y <= r.y1:
            x = r.x0
            while x <= r.x1:
                page.draw_circle((x, y), 0.7, color=MUTED, fill=MUTED); x += 14.17
            y += 14.17
    else:
        lines(page, r, 20)
    footer(page)


def build(first_weekday):
    plan = Plan(first_weekday)
    doc = fitz.open()
    for _ in plan.order:
        doc.new_page(width=PW, height=PH)
    for n, (kind, arg) in enumerate(plan.order):
        page = doc[n]
        if kind == "cover": draw_cover(page, plan)
        elif kind == "index": draw_index(page, plan)
        elif kind == "goals": draw_goals(page, plan)
        elif kind == "year": draw_year(page, plan)
        elif kind == "sem_spring": draw_semester(page, plan, "Spring")
        elif kind == "sem_fall": draw_semester(page, plan, "Fall")
        elif kind == "month": draw_month(page, plan, arg)
        elif kind == "habits": draw_habits(page, plan, arg)
        elif kind == "week": draw_week(page, plan, arg)
        elif kind == "tool": draw_tool(page, plan, arg)
        elif kind == "note": draw_note(page, plan, arg)
    name = "Monday" if first_weekday == 0 else "Sunday"
    toc = [[1, "Index", plan.page("index") + 1], [1, "Year at a Glance", plan.page("year") + 1]]
    toc += [[1, MONTHS[m - 1], plan.page("month", m) + 1] for m in range(1, 13)]
    toc += [[1, "Tools", plan.first("tool") + 1], [1, "Notes", plan.first("note") + 1]]
    doc.set_toc(toc)
    doc.set_metadata({"title": f"{YEAR} STEM Planner ({name} start)", "author": "MathRelaxing"})
    p = os.path.join(OUT, f"{YEAR}_STEM_Planner_{name}_Start.pdf")
    doc.save(p, garbage=4, deflate=True)
    print(f"{name} start: {len(doc)} pages, {os.path.getsize(p)//1024} KB, weeks={len(plan.weeks)}")
    return p


if __name__ == "__main__":
    build(0); build(6)
