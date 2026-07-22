"""
template_ipad_svg_bundle.py — reusable builder for MathRelaxing Interactive SVG editions
=========================================================================================
Assembles interactive Color-By-Number HTML files from Shapely polygons, packages them
into a ZIP, and generates an instructions PDF.

A concrete SVG edition supplies:
  • cfg                   — SvgBundleConfig with names, palette, copy
  • get_polygons(n)       — fn(design_number) -> list of dicts:
                              [{"poly": shapely.Polygon, "color_idx": int}, ...]
                            Each dict is one cell to color. color_idx maps into cfg.palette.

Produces, in cfg.out_dir:
  <Prefix>_Interactive.zip         (all HTML files)
  How_to_Use_Interactive_CBN.pdf   (instructions)

Usage example (build_spiral_ipad_svg.py):

    from template_ipad_svg_bundle import SvgBundleConfig, build_svg_bundle

    cfg = SvgBundleConfig(
        out_dir="ipad_spiral_cbn_svg",
        prefix="SpiralTilings_CBN",
        title="Spiral Tilings",
        palette=PASTEL_PALETTE,
        n_designs=50,
    )
    build_svg_bundle(cfg, get_polygons_fn)
"""

import os
import math
import shutil
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any

import shapely.geometry

BASE = os.path.dirname(os.path.abspath(__file__))


# ── Configuration ─────────────────────────────────────────────────────────────

@dataclass
class SvgBundleConfig:
    out_dir: str                      # e.g. "ipad_spiral_cbn_svg"
    prefix: str                       # file basename, e.g. "SpiralTilings_CBN"
    title: str                        # human name, e.g. "Spiral Tilings"
    palette: List[str] = field(default_factory=list)   # hex color list
    n_designs: int = 50
    stroke_color: str = "black"       # SVG stroke color for cell borders
    min_area: float = 0.00001         # discard polygons smaller than this
    area_threshold: float = 0.00001   # same, for sub-polygons after clipping
    font_clearance_ratio: float = 1.2 # font size = clearance * this ratio
    font_min: float = 0.003           # minimum font-size in SVG units
    font_max: float = 0.4             # maximum font-size in SVG units


# ── Polygon → SVG conversion ─────────────────────────────────────────────────

def polygons_to_svg(cells, cfg):
    """
    Convert a list of cell dicts to SVG <path> and <text> elements.

    Each cell dict must have:
      - "poly":      shapely.geometry.Polygon (already clipped/sanitized)
      - "color_idx": int index into cfg.palette

    Returns (svg_paths: list[str], svg_texts: list[str])
    """
    svg_paths = []
    svg_texts = []

    for idx, cell in enumerate(cells):
        p = cell["poly"]
        c_idx = cell["color_idx"] % len(cfg.palette)

        if p.is_empty or p.area < cfg.area_threshold:
            continue

        # Handle MultiPolygon from clipping
        geoms = [p] if p.geom_type == 'Polygon' else list(p.geoms)

        for g_idx, geom in enumerate(geoms):
            if geom.is_empty or geom.area < cfg.area_threshold:
                continue
            if geom.geom_type != 'Polygon':
                continue

            coords = list(geom.exterior.coords)
            path_d = "M " + " L ".join(
                [f"{x:.4f} {y:.4f}" for x, y in coords]
            ) + " Z"

            poly_id = f"poly_{idx}_{g_idx}"

            svg_paths.append(
                f'<path id="{poly_id}" class="polygon" d="{path_d}" '
                f'fill="white" stroke="{cfg.stroke_color}" '
                f'data-color-idx="{c_idx}" data-filled="false"></path>'
            )

            # Label: place at representative point, size to clearance
            pt = geom.representative_point()
            clearance = geom.boundary.distance(pt)
            fs = clearance * cfg.font_clearance_ratio
            fs = max(cfg.font_min, min(cfg.font_max, fs))

            svg_texts.append(
                f'<text id="text-{poly_id}" class="number-text" '
                f'x="{pt.x:.4f}" y="{pt.y:.4f}" '
                f'font-size="{fs:.5f}" text-anchor="middle" '
                f'dominant-baseline="central">{c_idx + 1}</text>'
            )

    return svg_paths, svg_texts


# ── HTML assembly ─────────────────────────────────────────────────────────────

def build_html(design_id, svg_paths, svg_texts, cfg):
    """
    Inject SVG paths, texts, and palette into the HTML template.
    Returns the full HTML string.
    """
    template_path = os.path.join(BASE, "template_ipad_svg.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # SVG content
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg">\n'
        '  <g id="svg-group">\n'
        '    ' + '\n    '.join(svg_paths) + '\n'
        '    ' + '\n    '.join(svg_texts) + '\n'
        '  </g>\n'
        '</svg>'
    )
    html = html.replace('<!-- SVG_CONTENT_PLACEHOLDER -->', svg_content)

    # Palette bar
    palette_html = []
    for i, hex_color in enumerate(cfg.palette):
        palette_html.append(
            f'<div class="color-swatch" style="background-color: {hex_color};" '
            f'data-color="{hex_color}" data-idx="{i}">{i+1}</div>'
        )
    html = html.replace('<!-- PALETTE_CONTENT_PLACEHOLDER -->', '\n'.join(palette_html))

    # Design ID (for localStorage key)
    html = html.replace('<!-- DESIGN_ID_PLACEHOLDER -->', f"{cfg.prefix}_{design_id}")

    # Page title
    html = html.replace(
        '<title>Color By Number - Spiral Tilings</title>',
        f'<title>Color By Number - {cfg.title} #{design_id}</title>'
    )

    return html


# ── Instructions PDF ──────────────────────────────────────────────────────────

def build_instructions_pdf(cfg):
    """Generate How_to_Use_Interactive_CBN.pdf in cfg.out_dir."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    )

    pdf_path = os.path.join(cfg.out_dir, "How_to_Use_Interactive_CBN.pdf")
    BG_DARK = HexColor("#1A1D24")
    GOLD = HexColor("#C8A951")

    doc = SimpleDocTemplate(
        pdf_path, pagesize=letter,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        topMargin=0.6*inch, bottomMargin=0.6*inch,
    )

    styles = getSampleStyleSheet()
    ts = ParagraphStyle('T', parent=styles['Title'], fontSize=28,
                        textColor=BG_DARK, spaceAfter=6,
                        fontName='Helvetica-Bold', alignment=TA_CENTER)
    ss = ParagraphStyle('S', parent=styles['Normal'], fontSize=13,
                        textColor=HexColor("#666"), spaceAfter=20,
                        fontName='Helvetica', alignment=TA_CENTER)
    hs = ParagraphStyle('H', parent=styles['Heading2'], fontSize=16,
                        textColor=BG_DARK, spaceBefore=18, spaceAfter=8,
                        fontName='Helvetica-Bold')
    bs = ParagraphStyle('B', parent=styles['Normal'], fontSize=11,
                        textColor=HexColor("#333"), spaceAfter=6,
                        fontName='Helvetica', leading=15, leftIndent=20)
    tip = ParagraphStyle('Tip', parent=styles['Normal'], fontSize=10,
                         textColor=HexColor("#556B2F"), spaceAfter=4,
                         fontName='Helvetica-Oblique', leading=14, leftIndent=20)
    ft = ParagraphStyle('F', parent=styles['Normal'], fontSize=9,
                        textColor=HexColor("#999"), spaceBefore=30,
                        fontName='Helvetica', alignment=TA_CENTER)

    e = []
    e.append(Spacer(1, 0.3*inch))
    e.append(Paragraph(f"{cfg.title}", ts))
    e.append(Paragraph("Interactive Color-By-Number for iPad", ss))
    e.append(HRFlowable(width="80%", thickness=1, color=GOLD,
                         spaceBefore=5, spaceAfter=15))
    e.append(Paragraph(
        f"Thank you for your purchase! This bundle contains "
        f"<b>{cfg.n_designs} interactive Color-By-Number designs</b> "
        "that run directly in your iPad's Safari browser. No app installation needed. "
        "Because they use vector graphics (SVG), you can zoom in infinitely "
        "without any pixelation.", bs))

    for heading, items in [
        ("What's Included", [
            f"<b>{cfg.n_designs} HTML files</b> -- one interactive design per file",
            "<b>This instructions PDF</b>",
            "All files work 100% offline -- no internet required",
        ]),
        ("Getting Started on iPad", [
            "<b>Step 1 -- Download</b>: Download the ZIP from Etsy to your iPad (Files app)",
            "<b>Step 2 -- Unzip</b>: Tap the ZIP in Files. It extracts automatically",
            "<b>Step 3 -- Open</b>: Tap any HTML file. If needed, use Share > Open in Safari",
        ]),
        ("How to Color", [
            "<b>1.</b> Tap a <b>numbered color</b> from the palette bar at the bottom",
            "<b>2.</b> Tap any zone showing <b>the same number</b>",
            "<b>3.</b> The zone fills with color and the number disappears!",
            "<b>4.</b> Wrong color? The border flashes red -- pick the right one",
        ]),
        ("Zoom and Pan", [
            "<b>Pinch to zoom</b> in and out -- lines stay perfectly crisp",
            "<b>Drag with one finger</b> to pan around the design",
            "Use the <b>+ / -</b> buttons (bottom right) for quick zoom",
        ]),
        ("Saving Your Progress", [
            "Progress is <b>saved automatically</b> in your browser",
            "Close the tab, reopen the file later -- your coloring is preserved",
            "Avoid clearing Safari data while designs are in progress",
        ]),
        ("Undo and Clear", [
            "<b>Undo</b> button (top right): reverses your last coloring action",
            "<b>Clear All</b> button: resets the entire design (asks for confirmation)",
        ]),
        ("Also Works On", [
            "These files work on <b>any device with a modern browser</b>: "
            "iPhone, Android, PC, or Mac",
        ]),
    ]:
        e.append(Paragraph(heading, hs))
        for item in items:
            e.append(Paragraph(item, bs))

    e.append(Spacer(1, 0.3*inch))
    e.append(HRFlowable(width="60%", thickness=0.5, color=HexColor("#CCC"),
                          spaceBefore=10, spaceAfter=10))
    e.append(Paragraph(
        "MathRelaxing -- For personal use only. Not for redistribution or resale.", ft))
    e.append(Paragraph("mathrelaxing.store", ft))

    doc.build(e)
    return pdf_path


# ── Full bundle builder ───────────────────────────────────────────────────────

def build_svg_bundle(cfg, get_polygons):
    """
    Main entry point.  Generates all HTML files, ZIP, and instructions PDF.

    Parameters
    ----------
    cfg : SvgBundleConfig
    get_polygons : callable(n: int) -> list[dict]
        For design number n (1-based), return a list of cell dicts:
        [{"poly": shapely.Polygon, "color_idx": int}, ...]
    """
    html_dir = os.path.join(cfg.out_dir, "html")
    os.makedirs(html_dir, exist_ok=True)

    print(f"Generating {cfg.n_designs} interactive SVG HTMLs...")
    saved_palette = list(cfg.palette)
    for n in range(1, cfg.n_designs + 1):
        result = get_polygons(n)
        # Allow per-design palette: return (cells, palette_hex) or
        # {"cells": [...], "palette": [...]}. Global cfg.palette is the default.
        design_palette = None
        if isinstance(result, dict):
            cells = result["cells"]
            design_palette = result.get("palette")
        elif isinstance(result, tuple) and len(result) == 2:
            cells, design_palette = result
        else:
            cells = result

        if design_palette:
            cfg.palette = list(design_palette)
        else:
            cfg.palette = saved_palette

        svg_paths, svg_texts = polygons_to_svg(cells, cfg)
        html = build_html(n, svg_paths, svg_texts, cfg)

        path = os.path.join(html_dir, f"{cfg.prefix}_{n:02d}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [{n}/{cfg.n_designs}] {os.path.basename(path)}  "
              f"({len(svg_paths)} polys, {len(cfg.palette)} colors)")
    cfg.palette = saved_palette

    # Package ZIP
    zip_base = os.path.join(cfg.out_dir, f"{cfg.prefix}_Interactive")
    shutil.make_archive(zip_base, 'zip', html_dir)
    zip_path = zip_base + ".zip"
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"  ZIP: {zip_path} ({size_mb:.1f} MB)")

    if size_mb > 20:
        print("  WARNING: ZIP exceeds 20 MB Etsy limit!")

    # Instructions PDF
    pdf_path = build_instructions_pdf(cfg)
    print(f"  PDF: {pdf_path}")

    print(f"Bundle complete! -> {cfg.out_dir}")
    return {
        "zip": zip_path,
        "pdf": pdf_path,
        "html_dir": html_dir,
    }
