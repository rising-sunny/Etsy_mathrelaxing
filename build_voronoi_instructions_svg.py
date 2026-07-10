"""
Generate an instructions PDF for the Interactive SVG Color-By-Number product.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

OUT_DIR = "ipad_voronoi_cbn_svg"
PDF_PATH = os.path.join(OUT_DIR, "How_to_Use_Interactive_CBN.pdf")

BG_DARK = HexColor("#1A1D24")
GOLD = HexColor("#C8A951")
CREAM = HexColor("#FFF8E7")

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=0.8*inch,
        rightMargin=0.8*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=28,
        textColor=BG_DARK,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=13,
        textColor=HexColor("#666666"),
        spaceAfter=20,
        fontName='Helvetica',
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=BG_DARK,
        spaceBefore=18,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor("#333333"),
        spaceAfter=6,
        fontName='Helvetica',
        leading=15,
    )
    
    step_style = ParagraphStyle(
        'Step',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor("#333333"),
        spaceAfter=4,
        fontName='Helvetica',
        leading=15,
        leftIndent=20,
    )
    
    tip_style = ParagraphStyle(
        'Tip',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor("#556B2F"),
        spaceAfter=4,
        fontName='Helvetica-Oblique',
        leading=14,
        leftIndent=20,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor("#999999"),
        spaceBefore=30,
        fontName='Helvetica',
        alignment=TA_CENTER,
    )

    elements = []
    
    # ── Title ──
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("🌿 Voronoi Gardens", title_style))
    elements.append(Paragraph("Interactive Color-By-Number for iPad", subtitle_style))
    elements.append(HRFlowable(width="80%", thickness=1, color=GOLD, spaceBefore=5, spaceAfter=15))
    
    elements.append(Paragraph(
        "Thank you for your purchase! This bundle contains <b>50 interactive Color-By-Number designs</b> "
        "that run directly in your iPad's Safari browser. No app installation needed. "
        "Because they use vector graphics (SVG), you can zoom in infinitely without any pixelation.",
        body_style
    ))
    
    # ── What's Included ──
    elements.append(Paragraph("📦 What's Included", heading_style))
    elements.append(Paragraph("• <b>50 HTML files</b> — one interactive design per file", step_style))
    elements.append(Paragraph("• <b>This instructions PDF</b>", step_style))
    elements.append(Paragraph("• All files work 100% offline — no internet required", step_style))
    
    # ── Getting Started ──
    elements.append(Paragraph("🚀 Getting Started on iPad", heading_style))
    
    elements.append(Paragraph("<b>Step 1 — Download the ZIP</b>", step_style))
    elements.append(Paragraph(
        "Download the ZIP file from Etsy to your iPad. It will appear in the <b>Files</b> app.",
        step_style
    ))
    
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Step 2 — Unzip</b>", step_style))
    elements.append(Paragraph(
        "Tap the ZIP file in the Files app. It will automatically extract into a folder "
        "containing the 50 HTML files.",
        step_style
    ))
    
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Step 3 — Open in Safari</b>", step_style))
    elements.append(Paragraph(
        "Tap any HTML file (e.g., <b>SpiralTilings_CBN_01.html</b>). "
        "If it doesn't open in Safari directly, tap the <b>Share</b> button (↑) and choose "
        "<b>\"Open in Safari\"</b>.",
        step_style
    ))
    
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "💡 Tip: You can also use any browser like Chrome or Firefox.",
        tip_style
    ))
    
    # ── How to Color ──
    elements.append(Paragraph("🎨 How to Color", heading_style))
    
    elements.append(Paragraph(
        "<b>1.</b> At the bottom of the screen you'll see a <b>color palette</b> with 30 numbered colors.",
        step_style
    ))
    elements.append(Paragraph(
        "<b>2.</b> Tap a color to select it. The selected color gets a white border.",
        step_style
    ))
    elements.append(Paragraph(
        "<b>3.</b> Now tap any zone on the design that shows <b>the same number</b> as your selected color.",
        step_style
    ))
    elements.append(Paragraph(
        "<b>4.</b> The zone fills with color and the number disappears! ✨",
        step_style
    ))
    elements.append(Paragraph(
        "<b>5.</b> If you tap a zone with the <b>wrong</b> color, the border flashes red briefly — "
        "pick the matching color and try again.",
        step_style
    ))
    
    # ── Zoom & Pan ──
    elements.append(Paragraph("🔍 Zoom & Pan", heading_style))
    
    elements.append(Paragraph(
        "• <b>Pinch to zoom</b> in and out — lines stay perfectly crisp at any zoom level",
        step_style
    ))
    elements.append(Paragraph(
        "• <b>Drag with one finger</b> to pan around the design",
        step_style
    ))
    elements.append(Paragraph(
        "• Use the <b>+ / −</b> buttons (bottom right) for quick zoom",
        step_style
    ))
    elements.append(Paragraph(
        "💡 Tip: Zoom in on the center of the spiral to find the tiny zones. "
        "The numbers scale to fit each zone perfectly!",
        tip_style
    ))
    
    # ── Saving Progress ──
    elements.append(Paragraph("💾 Saving Your Progress", heading_style))
    
    elements.append(Paragraph(
        "Your progress is <b>saved automatically</b> in your browser. "
        "You can close the tab, turn off your iPad, and when you reopen the same file "
        "in Safari, your coloring will be right where you left it.",
        step_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "⚠️ <b>Important:</b> If you clear Safari's website data (Settings → Safari → "
        "Clear History and Website Data), your progress will be lost. Avoid doing this "
        "while you have designs in progress.",
        step_style
    ))
    
    # ── Undo & Clear ──
    elements.append(Paragraph("↩️ Undo & Clear", heading_style))
    
    elements.append(Paragraph(
        "• <b>Undo</b> button (top right): reverses your last coloring action",
        step_style
    ))
    elements.append(Paragraph(
        "• <b>Clear All</b> button (top right): resets the entire design to white (asks for confirmation)",
        step_style
    ))
    
    # ── Also Works On ──
    elements.append(Paragraph("💻 Also Works On", heading_style))
    elements.append(Paragraph(
        "These files work on <b>any device with a modern browser</b>: "
        "iPhone, Android tablet, PC, or Mac. "
        "On a computer, use mouse click to color and scroll wheel to zoom.",
        step_style
    ))
    
    # ── Footer ──
    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="60%", thickness=0.5, color=HexColor("#CCCCCC"), spaceBefore=10, spaceAfter=10))
    elements.append(Paragraph("© MathRelaxing — For personal use only. Not for redistribution or resale.", footer_style))
    elements.append(Paragraph("mathrelaxing.store", footer_style))
    
    doc.build(elements)
    print(f"PDF generado: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
