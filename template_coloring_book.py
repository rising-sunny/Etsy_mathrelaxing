"""
template_coloring_book.py — reusable builder for MathRelaxing coloring books
=============================================================================
Any printable coloring-book PDF (Fractal Flora, Voronoi, Celtic, Hyperbolic,
Islamic, …) is assembled here so structure & branding never drift:

  page 1  : portrait themed cover (brand.cover)
  page 2  : "The Mathematics" intro (brand.about_page)
  page 3+ : the 50 design pages (from your render_design callback)

Outputs (into out_dir, default repo root):
  <prefix>_digital.pdf
  <prefix>_cover.jpg          (SQUARE listing photo)
  <prefix>_page_01..NN.jpg    (design preview photos)

A concrete product only supplies:
  • cfg           — text + theme (see BookConfig)
  • render_design — fn(n:int) -> portrait 8.5x11 matplotlib Figure of design n
  • emblem        — fn(ax, cx, cy, r) drawing the cover emblem in gold
  • watermark     — optional fn(ax, W, H) faint cover background

Color-by-number books use the SAME builder; their render_design simply draws
numbered facets + a small palette key (see STANDARDS.md).
"""

import os
from dataclasses import dataclass, field
from typing import Callable, Optional, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import brand

BASE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class BookConfig:
    prefix: str                       # file basename, e.g. "celtic_knot"
    theme_bg: str                     # dark cover colour, e.g. "#241014"
    title: str                        # cover product name (CREAM)
    subtitle: str                     # cover subtitle (GOLD)
    tagline: str                      # italic cover line
    count_label: str                  # e.g. "50 Knotwork Designs"
    about_heading: str = "THE MATHEMATICS"
    about_body: str = ""
    n_designs: int = 50
    preview_indices: List[int] = field(default_factory=lambda: [1, 8, 12, 20, 30, 38, 46])
    out_dir: str = BASE


def build_book(cfg: BookConfig,
               render_design: Callable[[int], "plt.Figure"],
               emblem: Callable = None,
               watermark: Optional[Callable] = None):
    pdf_path = os.path.join(cfg.out_dir, f"{cfg.prefix}_digital.pdf")
    previews = {}

    with PdfPages(pdf_path) as pdf:
        # page 1 — portrait themed cover
        fig = brand.cover(cfg.theme_bg, emblem, cfg.title, cfg.subtitle,
                          cfg.tagline, cfg.count_label, watermark=watermark, square=False)
        pdf.savefig(fig); plt.close(fig)

        # page 2 — the mathematics
        fig = brand.about_page(cfg.about_heading, cfg.about_body)
        pdf.savefig(fig); plt.close(fig)

        # pages 3+ — designs
        for n in range(1, cfg.n_designs + 1):
            fig = render_design(n)
            pdf.savefig(fig)
            if n in cfg.preview_indices:
                previews[n] = fig
            else:
                plt.close(fig)

    # SQUARE listing cover
    fig = brand.cover(cfg.theme_bg, emblem, cfg.title, cfg.subtitle,
                      cfg.tagline, cfg.count_label, watermark=watermark, square=True)
    fig.savefig(os.path.join(cfg.out_dir, f"{cfg.prefix}_cover.jpg"),
                dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)

    # design preview photos
    for slot, n in enumerate(cfg.preview_indices, start=1):
        fig = previews[n]
        fig.savefig(os.path.join(cfg.out_dir, f"{cfg.prefix}_page_{slot:02d}.jpg"),
                    dpi=150, facecolor="white")
        plt.close(fig)

    print(f"[{cfg.prefix}] libro listo: {2 + cfg.n_designs} paginas + "
          f"cover + {len(cfg.preview_indices)} previews")
    return pdf_path
