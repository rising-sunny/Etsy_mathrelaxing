"""
build_previews.py — imagenes de listing para el MathRelaxing Life Planner
=========================================================================
Genera imagenes 2000x2000 (fondo navy, branding MathRelaxing) donde el
comprador puede LEER cada pagina: showcases de una o dos paginas a alta
resolucion + slides de "que incluye" y compatibilidad.

Uso: python build_previews.py   (requiere el PDF ya construido)
"""
import os
import sys
import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, "MathRelaxing_Life_Planner.pdf")
PREV = os.path.join(BASE, "previews")
TMP = os.path.join(BASE, "_pagepng")

NAVY = brand.IPAD_NAVY
NAVY2 = "#0b0e1c"
GOLD = brand.GOLD
CREAM = brand.CREAM
MUTED = "#aeb2c4"

PAGES = {
    "dashboard": 0, "year_hub": 1, "year": 2, "month": 11, "week": 23,
    "day": 75, "hub_life": 440, "gratitude": 463, "mood": 455, "habit": 474,
    "budget": 483, "expense": 484, "cornell": 496, "vision": 459,
}


def render_pages(dpi=210):
    os.makedirs(TMP, exist_ok=True)
    doc = fitz.open(PDF)
    paths = {}
    for name, idx in PAGES.items():
        if idx < doc.page_count:
            p = os.path.join(TMP, f"{name}.png")
            doc[idx].get_pixmap(dpi=dpi).save(p)
            paths[name] = p
    doc.close()
    return paths


def _fig():
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    return fig, ax


def _page(ax, path, cx, cy, w, border=GOLD, lw=1.6):
    img = mpimg.imread(path)
    h = w * img.shape[0] / img.shape[1]
    # sombra
    ax.add_patch(Rectangle((cx - w / 2 + 0.06, cy - h / 2 - 0.07), w, h,
                           facecolor="black", alpha=0.45, zorder=2))
    ax.imshow(img, extent=[cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2], zorder=3)
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fill=False,
                           edgecolor=border, lw=lw, zorder=4))
    return h


def _title(ax, y, s, size=30, color=CREAM, bold=True):
    ax.text(5, y, s, ha="center", va="center", fontsize=size, color=color,
            **(brand.SERIF_BOLD if bold else brand.SERIF))


def _sub(ax, y, s, size=15, color=GOLD):
    ax.text(5, y, s, ha="center", va="center", fontsize=size, color=color,
            **brand.SERIF)


def _chip(ax, x, y, s, size=12.5, h=0.5):
    # ancho segun largo del texto para que nunca se corte
    w = max(2.0, 0.16 * len(s) * size / 12.5 + 0.5)
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.12",
                 facecolor=GOLD, edgecolor="none", zorder=6))
    ax.text(x, y, s, ha="center", va="center", fontsize=size, color=NAVY,
            zorder=7, **brand.SERIF_BOLD)


def _save(fig, name):
    os.makedirs(PREV, exist_ok=True)
    fig.savefig(os.path.join(PREV, name), dpi=200, facecolor=NAVY,
                bbox_inches="tight", pad_inches=0.0)
    plt.close(fig)


def build(paths):
    # ── 1 · HERO ─────────────────────────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.35, "THE LIFE PLANNER", size=42)
    _sub(ax, 8.62, "Undated All-in-One Digital Planner", size=20)
    ax.text(5, 8.12, "500+ hyperlinked pages  ·  GoodNotes · Notability · iPad & Android",
            ha="center", fontsize=12.5, color=MUTED, **brand.SANS)
    _page(ax, paths["dashboard"], 5, 4.35, 8.1)
    brand.ipad_logo(ax, 5, 0.5, 1.5)
    _save(fig, "life_preview_1_hero.jpg")

    # ── 2 · DAILY (grande y legible) ────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "DAILY PLANNER", size=32)
    _sub(ax, 8.8, "Schedule · Top 3 · To-do · Habits · Gratitude — 365 undated days")
    _page(ax, paths["day"], 5, 4.5, 9.2)
    _save(fig, "life_preview_2_daily.jpg")

    # ── 3 · WEEKLY ──────────────────────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "WEEKLY PLANNER", size=32)
    _sub(ax, 8.8, "7-day spread · priorities · notes — 52 weeks, start any day")
    _page(ax, paths["week"], 5, 4.5, 9.2)
    _save(fig, "life_preview_3_weekly.jpg")

    # ── 4 · MONTHLY + YEAR ──────────────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "MONTH & YEAR AT A GLANCE", size=27)
    _sub(ax, 8.82, "12 monthly spreads · yearly overview · quarterly planners")
    _page(ax, paths["month"], 2.85, 4.8, 5.4)
    _page(ax, paths["year"], 7.15, 4.8, 5.4)
    _chip(ax, 2.85, 1.5, "Tap a month to jump")
    _chip(ax, 7.15, 1.5, "Q1 · Q2 · Q3 · Q4")
    _save(fig, "life_preview_4_monthyear.jpg")

    # ── 5 · WELLNESS & FINANCE TRACKERS ─────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "TRACK YOUR BODY & MONEY", size=27)
    _sub(ax, 8.82, "Mood · sleep · water · budget · expenses · savings & more")
    _page(ax, paths["mood"], 2.85, 4.8, 5.4)
    _page(ax, paths["budget"], 7.15, 4.8, 5.4)
    brand.ipad_logo(ax, 5, 0.55, 1.2)
    _save(fig, "life_preview_5_trackers_a.jpg")

    # ── 6 · PRODUCTIVITY & SELF-CARE ────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "PLAN & REFLECT", size=27)
    _sub(ax, 8.82, "Habit tracker · priority matrix · gratitude · vision board")
    _page(ax, paths["habit"], 2.85, 4.8, 5.4)
    _page(ax, paths["gratitude"], 7.15, 4.8, 5.4)
    brand.ipad_logo(ax, 5, 0.55, 1.2)
    _save(fig, "life_preview_6_trackers_b.jpg")

    # ── 7 · NAVIGATION (detalle con callout) ────────────────────────────────
    fig, ax = _fig()
    _title(ax, 9.4, "TAP TO JUMP ANYWHERE", size=30)
    _sub(ax, 8.8, "Category hubs + side tabs on every single page")
    pw = 7.1
    pcx = 4.15
    _page(ax, paths["hub_life"], pcx, 4.75, pw)
    # callout sobre la barra de pestañas (borde derecho de la pagina)
    px_right = pcx + pw / 2
    ax.annotate("Side tabs\non every\npage",
                xy=(px_right - 0.12, 5.3), xytext=(px_right + 0.55, 6.7),
                fontsize=13, color=CREAM, ha="left", va="center",
                **brand.SERIF,
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=2))
    _chip(ax, pcx, 0.75, "Every card is a live link")
    _save(fig, "life_preview_7_navigation.jpg")

    # ── 8 · WHAT'S INCLUDED (slide de texto elegante) ───────────────────────
    fig, ax = _fig()
    _title(ax, 9.3, "WHAT'S INCLUDED", size=32)
    ax.plot([3.3, 6.7], [8.75, 8.75], color=GOLD, lw=1.5)
    rows = [
        ("CALENDAR", "Year · 12 Months · 52 Weeks · 365 Days · Q1-Q4"),
        ("LIFESTYLE", "Wishlist · Contacts · Book & Watch logs · Trips"),
        ("WELLNESS", "Meal · Mood · Sleep · Water · Workout · more"),
        ("SELF-CARE", "Gratitude · Bucket list · Vision board · Journaling"),
        ("PRODUCTIVITY", "To-do · Priority matrix · Habits · Goals · Projects"),
        ("FINANCE", "Budget · Expenses · Savings · Bills · Debt · more"),
        ("NOTES", "Dot grid · Squared · Lined · Cornell · Isometric"),
        ("NAVIGATION", "500+ hyperlinked pages · side tabs everywhere"),
    ]
    y = 7.9
    for head, body in rows:
        ax.text(1.25, y, head, ha="left", va="center", fontsize=14.5,
                color=GOLD, **brand.SERIF_BOLD)
        ax.text(4.05, y, body, ha="left", va="center", fontsize=11.8,
                color=CREAM, **brand.SANS)
        y -= 0.82
    brand.ipad_logo(ax, 5, 0.7, 1.3)
    _save(fig, "life_preview_8_included.jpg")

    # ── 9 · COMPATIBILITY / FORMAT ──────────────────────────────────────────
    fig, ax = _fig()
    _title(ax, 8.9, "WORKS EVERYWHERE YOU PLAN", size=27)
    apps = ["GoodNotes", "Notability", "Penly", "Xodo", "Noteshelf", "Kilonotes"]
    y = 7.4
    for i, a in enumerate(apps):
        col = i % 2
        row = i // 2
        x = 3.0 + col * 4.0
        yy = y - row * 1.15
        ax.text(x - 0.45, yy, "✓", ha="center", va="center", fontsize=20,
                color=GOLD, **brand.SANS)
        ax.text(x, yy, a, ha="left", va="center", fontsize=17, color=CREAM,
                **brand.SERIF)
    facts = ["Undated — start any day, reuse every year",
             "Instant digital download — no shipping",
             "iPad · Android · Windows tablets",
             "A separate annotation app is required"]
    yy = 3.4
    for f in facts:
        ax.text(5, yy, f, ha="center", va="center", fontsize=13, color=MUTED,
                **brand.SERIF)
        yy -= 0.6
    brand.ipad_logo(ax, 5, 0.6, 1.3)
    _save(fig, "life_preview_9_compatibility.jpg")

    print("Previews en", PREV)


if __name__ == "__main__":
    paths = render_pages()
    build(paths)
