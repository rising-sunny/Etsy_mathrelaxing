"""
build_previews.py — imagenes de listing para el MathRelaxing Life Planner
=========================================================================
Renderiza paginas representativas del PDF a PNG y las compone en imagenes de
2000x2000 (fondo navy iPad, logo MathRelaxing, titulos serif crema/oro),
siguiendo el estilo de los demas listings de la tienda.

Uso: python build_previews.py   (requiere el PDF ya construido)
"""
import os
import sys
import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, "MathRelaxing_Life_Planner.pdf")
PREV = os.path.join(BASE, "previews")
TMP = os.path.join(BASE, "_pagepng")

NAVY = brand.IPAD_NAVY
GOLD = brand.GOLD
CREAM = brand.CREAM

# indices de pagina representativos del build COMPLETO (501 paginas)
PAGES = {
    "dashboard": 0,
    "year": 2,       # year_glance
    "month": 11,
    "week": 23,
    "day": 75,
    "hub_life": 440,
    "gratitude": 463,     # MIND_0
    "mood": 455,          # BODY_3
    "habit": 474,         # WORK_2
    "budget": 483,        # MONEY_1
    "expense": 484,       # MONEY_2
    "cornell": 496,       # NOTE_3
}


def render_pages(dpi=150):
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
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    return fig, ax


def _shot(ax, path, x, y, w, border=GOLD, lw=1.5, shadow=True):
    """Coloca una captura de pagina (4:3) centrada en (x,y) con ancho w."""
    img = mpimg.imread(path)
    h = w * img.shape[0] / img.shape[1]
    if shadow:
        ax.add_patch(plt.Rectangle((x - w / 2 + 0.05, y - h / 2 - 0.05), w, h,
                                   facecolor="black", alpha=0.35, zorder=2))
    ax.imshow(img, extent=[x - w / 2, x + w / 2, y - h / 2, y + h / 2], zorder=3)
    ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fill=False,
                               edgecolor=border, lw=lw, zorder=4))
    return h


def _save(fig, name):
    os.makedirs(PREV, exist_ok=True)
    fig.savefig(os.path.join(PREV, name), dpi=200, facecolor=NAVY,
                bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def build(paths):
    # 1 · HERO
    fig, ax = _fig()
    ax.text(5, 9.3, "THE LIFE PLANNER", ha="center", fontsize=40,
            color=CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.55, "Undated All-in-One Digital Planner", ha="center",
            fontsize=19, color=GOLD, **brand.SERIF)
    ax.text(5, 8.05, "GoodNotes · Notability · iPad & Android",
            ha="center", fontsize=13, color=(0.8, 0.82, 0.9), **brand.SANS)
    _shot(ax, paths["dashboard"], 5, 4.4, 7.4)
    brand.ipad_logo(ax, 5, 0.55, 1.5)
    _save(fig, "life_preview_1_hero.jpg")

    # 2 · CALENDAR SYSTEM
    fig, ax = _fig()
    ax.text(5, 9.4, "A COMPLETE CALENDAR SYSTEM", ha="center", fontsize=26,
            color=CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.8, "Year · Month · Week · Day — all fully hyperlinked",
            ha="center", fontsize=14, color=GOLD, **brand.SERIF)
    _shot(ax, paths["year"], 2.9, 6.2, 4.6)
    _shot(ax, paths["month"], 7.1, 6.2, 4.6)
    _shot(ax, paths["week"], 2.9, 2.7, 4.6)
    _shot(ax, paths["day"], 7.1, 2.7, 4.6)
    _save(fig, "life_preview_2_calendar.jpg")

    # 3 · TRACKERS BREADTH
    fig, ax = _fig()
    ax.text(5, 9.4, "50+ LIFE TRACKERS & TEMPLATES", ha="center", fontsize=25,
            color=CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.8, "Wellness · Finance · Productivity · Self-Care · Lifestyle",
            ha="center", fontsize=13, color=GOLD, **brand.SERIF)
    _shot(ax, paths["mood"], 2.7, 6.0, 4.3)
    _shot(ax, paths["budget"], 7.3, 6.0, 4.3)
    _shot(ax, paths["habit"], 2.7, 2.6, 4.3)
    _shot(ax, paths["gratitude"], 7.3, 2.6, 4.3)
    brand.ipad_logo(ax, 5, 0.5, 1.2)
    _save(fig, "life_preview_3_trackers.jpg")

    # 4 · HUB NAVIGATION
    fig, ax = _fig()
    ax.text(5, 9.4, "TAP TO JUMP ANYWHERE", ha="center", fontsize=27,
            color=CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.8, "Category hubs + side tabs on every single page",
            ha="center", fontsize=14, color=GOLD, **brand.SERIF)
    _shot(ax, paths["hub_life"], 3.4, 4.7, 5.6)
    _shot(ax, paths["expense"], 7.4, 3.4, 4.0, lw=1.2)
    brand.ipad_logo(ax, 5, 0.55, 1.3)
    _save(fig, "life_preview_4_navigation.jpg")

    # 5 · WHAT'S INCLUDED (mosaico)
    fig, ax = _fig()
    ax.text(5, 9.45, "500+ HYPERLINKED PAGES", ha="center", fontsize=27,
            color=CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.9, "One planner for every part of your life",
            ha="center", fontsize=14, color=GOLD, **brand.SERIF)
    tiles = ["dashboard", "month", "day", "mood", "budget", "habit",
             "gratitude", "cornell", "week"]
    cols = 3
    x0, y0 = 2.2, 6.7
    dx, dy = 2.8, 2.55
    for i, key in enumerate(tiles):
        if key not in paths:
            continue
        r = i // cols
        c = i % cols
        _shot(ax, paths[key], x0 + c * dx, y0 - r * dy, 2.55, lw=1.0, shadow=False)
    _save(fig, "life_preview_5_included.jpg")

    print("Previews en", PREV)


if __name__ == "__main__":
    paths = render_pages()
    build(paths)
