"""
generate_emergency_binder.py — MathRelaxing Family Emergency Binder (printable)
================================================================================
US Letter PDF binder pages + cover + spine + tabs guide + fillable-style forms.
Informed by eRank (Jun 2026 rising, KD ~33, low comp) + Etsy SERP patterns:
multi-section ICE binders, document checklists, medical/insurance/contacts.

  python generate_emergency_binder.py
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas

import brand

BASE = Path(__file__).resolve().parent
OUT = BASE / "emergency_binder"
PREVIEWS = OUT / "previews"
PAGES = OUT / "pages"
ZIP_PATH = OUT / "MathRelaxing_Family_Emergency_Binder.zip"

NAVY = HexColor("#12172D")
GOLD = HexColor("#C9A24B")
CREAM = HexColor("#F8F4EB")
INK = HexColor("#1A1A1A")
SOFT = HexColor("#5C5A56")
LINE = HexColor("#D4CFC4")
WHITE = HexColor("#FFFFFF")

W, H = letter  # 612 x 792


def _ensure():
    for d in (OUT, PREVIEWS, PAGES):
        d.mkdir(parents=True, exist_ok=True)


def _styles():
    return {
        "cover_title": ParagraphStyle(
            "ct", fontName="Times-Bold", fontSize=28, textColor=NAVY, alignment=1, leading=34, spaceAfter=8
        ),
        "cover_sub": ParagraphStyle(
            "cs", fontName="Helvetica", fontSize=11, textColor=GOLD, alignment=1, spaceAfter=6
        ),
        "h1": ParagraphStyle(
            "h1", fontName="Times-Bold", fontSize=16, textColor=NAVY, spaceBefore=0, spaceAfter=8
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=11, textColor=GOLD, spaceBefore=12, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9.5, textColor=INK, leading=13, spaceAfter=5
        ),
        "small": ParagraphStyle(
            "small", fontName="Helvetica", fontSize=8.5, textColor=SOFT, leading=11, spaceAfter=3
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=8, textColor=SOFT, spaceAfter=2
        ),
        "foot": ParagraphStyle(
            "foot", fontName="Helvetica", fontSize=7.5, textColor=SOFT, alignment=1
        ),
    }


def _hline():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=4, spaceAfter=10)


def _field_row(label: str, width=6.5 * inch) -> Table:
    """Label + underline field."""
    data = [[Paragraph(f"<b>{label}</b>", ParagraphStyle("l", fontName="Helvetica", fontSize=8, textColor=SOFT)), ""]]
    t = Table(data, colWidths=[2.1 * inch, width - 2.1 * inch])
    t.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (1, 0), (1, 0), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _checkbox_list(items: list[str], cols=1) -> list:
    styles = _styles()
    out = []
    for it in items:
        out.append(Paragraph(f"☐  {it}", styles["body"]))
    return out


def _footer_canvas(canv: canvas.Canvas, doc):
    canv.saveState()
    canv.setFillColor(CREAM)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # gold corner marks
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1.2)
    m, L = 0.45 * inch, 0.28 * inch
    for x, y, sx, sy in [
        (m, H - m, 1, -1),
        (W - m, H - m, -1, -1),
        (m, m, 1, 1),
        (W - m, m, -1, 1),
    ]:
        canv.line(x, y, x + sx * L, y)
        canv.line(x, y, x, y + sy * L)
    canv.setFillColor(SOFT)
    canv.setFont("Helvetica", 7)
    canv.drawCentredString(W / 2, 0.35 * inch, f"MathRelaxing Family Emergency Binder  ·  Page {doc.page}")
    canv.restoreState()


def _doc(path: Path, story: list, top=0.7 * inch):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=top,
        bottomMargin=0.6 * inch,
    )
    doc.build(story, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)


def page_cover(path: Path):
    s = _styles()
    story = [
        Spacer(1, 1.4 * inch),
        Paragraph("FAMILY", s["cover_sub"]),
        Paragraph("Emergency Binder", s["cover_title"]),
        _hline(),
        Paragraph("In case of emergency — keep calm, find what matters", s["cover_sub"]),
        Spacer(1, 0.4 * inch),
        Paragraph(
            "Print · fill · store in a binder · tell trusted people where it lives",
            s["body"],
        ),
        Spacer(1, 0.8 * inch),
        Paragraph("<b>Household name</b>", s["label"]),
        _field_row("Household / family name", 5.5 * inch),
        Spacer(1, 0.15 * inch),
        _field_row("Primary address", 5.5 * inch),
        Spacer(1, 0.15 * inch),
        _field_row("Date last updated", 5.5 * inch),
        Spacer(1, 1.2 * inch),
        Paragraph("MathRelaxing  ·  Practical systems, calm design", s["foot"]),
        Paragraph(brand.COPYRIGHT, s["foot"]),
    ]
    _doc(path, story, top=0.9 * inch)
    print(f"  {path.name}")


def page_contents(path: Path):
    s = _styles()
    sections = [
        ("01", "Quick start & how to use"),
        ("02", "Emergency contacts"),
        ("03", "Household members"),
        ("04", "Medical information"),
        ("05", "Insurance overview"),
        ("06", "Important documents checklist"),
        ("07", "Home & property"),
        ("08", "Finances snapshot"),
        ("09", "Pets"),
        ("10", "Digital access notes"),
        ("11", "Evacuation & go-bag"),
        ("12", "Meeting place & school plans"),
        ("13", "Monthly update checklist"),
    ]
    story = [Paragraph("Contents", s["h1"]), _hline()]
    for num, title in sections:
        story.append(
            Paragraph(f"<font color='#C9A24B'><b>{num}</b></font>    {title}", s["body"])
        )
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Tip: print divider tabs using the section titles above.", s["small"]))
    _doc(path, story)
    print(f"  {path.name}")


def page_quick_start(path: Path):
    s = _styles()
    story = [
        Paragraph("01  ·  Quick start", s["h1"]),
        _hline(),
        Paragraph("How to use this binder", s["h2"]),
        Paragraph(
            "1. Print all pages (US Letter). Use a 1–2\" binder and tab dividers.<br/>"
            "2. Fill in pencil first; ink when stable.<br/>"
            "3. Store <b>copies</b> of critical IDs/insurance cards in sheet protectors — keep originals secure.<br/>"
            "4. Tell 1–2 trusted people where the binder lives.<br/>"
            "5. Review every 3 months (use the update checklist).",
            s["body"],
        ),
        Paragraph("In the first 10 minutes of an emergency", s["h2"]),
        *[_ for _ in _checkbox_list([
            "Ensure people and pets are safe",
            "Call emergency services if needed (local emergency number)",
            "Open Emergency Contacts page",
            "Grab go-bag if evacuating",
            "Take this binder or a digital photo of key pages",
            "Go to the agreed meeting place if separated",
        ])],
        Paragraph("Disclaimer", s["h2"]),
        Paragraph(
            "This is an organizational tool, not professional medical, legal, or financial advice. "
            "Adapt pages to your household and local rules.",
            s["small"],
        ),
    ]
    _doc(path, story)
    print(f"  {path.name}")


def page_contacts(path: Path):
    s = _styles()
    story = [Paragraph("02  ·  Emergency contacts", s["h1"]), _hline()]
    story.append(Paragraph("Primary emergency numbers", s["h2"]))
    for lab in [
        "Local emergency services",
        "Poison control",
        "Non-emergency police",
        "Family doctor / clinic",
        "Nearest hospital",
        "Veterinarian",
        "Building / landlord / HOA",
        "Insurance claims (auto / home)",
    ]:
        story.append(_field_row(lab))
    story.append(Paragraph("Trusted people", s["h2"]))
    for i in range(1, 5):
        story.append(Paragraph(f"<b>Contact {i}</b>", s["label"]))
        story.append(_field_row("Name / relationship"))
        story.append(_field_row("Phone / email"))
        story.append(Spacer(1, 0.08 * inch))
    _doc(path, story)
    print(f"  {path.name}")


def page_household(path: Path):
    s = _styles()
    story = [Paragraph("03  ·  Household members", s["h1"]), _hline()]
    story.append(
        Paragraph("List everyone who lives here (and frequent guests who matter in an emergency).", s["small"])
    )
    for i in range(1, 6):
        story.append(Paragraph(f"<b>Person {i}</b>", s["h2"]))
        story.append(_field_row("Full legal name"))
        story.append(_field_row("DOB / blood type (optional)"))
        story.append(_field_row("Phone / workplace / school"))
        story.append(_field_row("Allergies / critical notes"))
    _doc(path, story)
    print(f"  {path.name}")


def page_medical(path: Path):
    s = _styles()
    story = [
        Paragraph("04  ·  Medical information", s["h1"]),
        _hline(),
        Paragraph("Keep this page accurate. Bring a copy to ER if possible.", s["small"]),
        Paragraph("Primary care", s["h2"]),
    ]
    for lab in ["Physician name / clinic", "Phone", "Preferred hospital", "Pharmacy + phone"]:
        story.append(_field_row(lab))
    story.append(Paragraph("Medications (current)", s["h2"]))
    story.append(
        Paragraph(
            "☐ Name / dose / schedule _______________________________________________<br/>"
            "☐ Name / dose / schedule _______________________________________________<br/>"
            "☐ Name / dose / schedule _______________________________________________<br/>"
            "☐ Name / dose / schedule _______________________________________________",
            s["body"],
        )
    )
    story.append(Paragraph("Conditions & allergies", s["h2"]))
    story.append(_field_row("Medical conditions"))
    story.append(_field_row("Allergies (meds / food / other)"))
    story.append(_field_row("Devices (glasses, CPAP, etc.)"))
    story.append(_field_row("Insurance member ID (see also Insurance page)"))
    _doc(path, story)
    print(f"  {path.name}")


def page_insurance(path: Path):
    s = _styles()
    story = [Paragraph("05  ·  Insurance overview", s["h1"]), _hline()]
    for kind in ["Health", "Home / renters", "Auto", "Life", "Other"]:
        story.append(Paragraph(kind, s["h2"]))
        story.append(_field_row("Carrier"))
        story.append(_field_row("Policy # / member ID"))
        story.append(_field_row("Claims phone / portal"))
        story.append(_field_row("Agent name / phone"))
    _doc(path, story)
    print(f"  {path.name}")


def page_documents(path: Path):
    s = _styles()
    story = [
        Paragraph("06  ·  Important documents checklist", s["h1"]),
        _hline(),
        Paragraph(
            "Check what you have. Note location (binder sleeve / safe / cloud). Do not store originals you cannot replace without need.",
            s["small"],
        ),
        Paragraph("Identity & legal", s["h2"]),
    ]
    for it in [
        "Passports / national IDs",
        "Birth certificates",
        "Marriage / divorce certificates",
        "Social security / national insurance cards",
        "Wills / advance directives / POA",
        "Custody or care agreements (if any)",
    ]:
        story.append(Paragraph(f"☐  {it}    Location: ____________________", s["body"]))
    story.append(Paragraph("Property & finance", s["h2"]))
    for it in [
        "Deed / lease",
        "Mortgage / loan statements",
        "Vehicle titles / registration",
        "Recent tax return (copy)",
        "Bank / investment account list (names only)",
        "Insurance policies (full copies)",
    ]:
        story.append(Paragraph(f"☐  {it}    Location: ____________________", s["body"]))
    story.append(Paragraph("Other", s["h2"]))
    for it in [
        "Pet records / microchip",
        "Home inventory photos",
        "Emergency cash note (amount / where — carefully)",
        "Spare key location note",
    ]:
        story.append(Paragraph(f"☐  {it}    Location: ____________________", s["body"]))
    _doc(path, story)
    print(f"  {path.name}")


def page_home(path: Path):
    s = _styles()
    story = [Paragraph("07  ·  Home & property", s["h1"]), _hline()]
    for lab in [
        "Full address",
        "Utility company — electric",
        "Utility company — gas / water",
        "Internet / phone provider",
        "Alarm / security company",
        "Shutoff: water location",
        "Shutoff: gas location",
        "Breaker panel location",
        "Safe / lockbox location + who knows code",
    ]:
        story.append(_field_row(lab))
    story.append(Paragraph("Floor notes / hazards", s["h2"]))
    story.append(_field_row("Notes (exits, fire extinguisher, first-aid kit)"))
    _doc(path, story)
    print(f"  {path.name}")


def page_finances(path: Path):
    s = _styles()
    story = [
        Paragraph("08  ·  Finances snapshot", s["h1"]),
        _hline(),
        Paragraph(
            "List institutions and account nicknames only — not full passwords or full card numbers.",
            s["small"],
        ),
    ]
    for lab in [
        "Primary bank",
        "Secondary bank / credit union",
        "Credit cards (issuer names)",
        "Employer / payroll contact",
        "Accountant / tax pro",
        "Monthly bill autopay note",
    ]:
        story.append(_field_row(lab))
    story.append(Paragraph("If primary adult is unavailable", s["h2"]))
    story.append(_field_row("Who can access what (high level)"))
    story.append(_field_row("Where to find full records (safe / encrypted drive)"))
    _doc(path, story)
    print(f"  {path.name}")


def page_pets(path: Path):
    s = _styles()
    story = [Paragraph("09  ·  Pets", s["h1"]), _hline()]
    for i in range(1, 4):
        story.append(Paragraph(f"<b>Pet {i}</b>", s["h2"]))
        for lab in ["Name / species / breed", "Microchip #", "Vet + phone", "Meds / allergies", "Food / routine notes"]:
            story.append(_field_row(lab))
    _doc(path, story)
    print(f"  {path.name}")


def page_digital(path: Path):
    s = _styles()
    story = [
        Paragraph("10  ·  Digital access notes", s["h1"]),
        _hline(),
        Paragraph(
            "Do <b>not</b> write master passwords here. Note password manager name and who has emergency access.",
            s["small"],
        ),
    ]
    for lab in [
        "Password manager (name only)",
        "Emergency access contact",
        "Email accounts (addresses only)",
        "Phone carrier + account PIN location",
        "Cloud photo / document backup",
        "Social / important logins list location",
        "Device PINs recovery notes location",
    ]:
        story.append(_field_row(lab))
    _doc(path, story)
    print(f"  {path.name}")


def page_evac(path: Path):
    s = _styles()
    story = [
        Paragraph("11  ·  Evacuation & go-bag", s["h1"]),
        _hline(),
        Paragraph("Go-bag location", s["h2"]),
        _field_row("Where is the go-bag?"),
        Paragraph("Go-bag checklist", s["h2"]),
    ]
    for it in [
        "Water / snacks",
        "Copies of IDs & insurance cards",
        "Cash (small bills) + payment cards you choose",
        "Phone chargers / power bank",
        "Medications (3–7 days)",
        "Flashlight / batteries",
        "Change of clothes / hygiene",
        "Child / pet supplies",
        "Keys / multi-tool",
        "Printed contact list",
    ]:
        story.append(Paragraph(f"☐  {it}", s["body"]))
    story.append(Paragraph("Evacuation routes", s["h2"]))
    story.append(_field_row("Primary route / destination"))
    story.append(_field_row("Backup route / destination"))
    story.append(_field_row("Vehicle + fuel note"))
    _doc(path, story)
    print(f"  {path.name}")


def page_meeting(path: Path):
    s = _styles()
    story = [
        Paragraph("12  ·  Meeting place & school plans", s["h1"]),
        _hline(),
        Paragraph("If separated", s["h2"]),
        _field_row("Nearby meeting place (outdoor)"),
        _field_row("Out-of-area meeting place"),
        _field_row("Out-of-area contact person"),
        Paragraph("School / daycare", s["h2"]),
        _field_row("School name / address"),
        _field_row("Pickup policy / authorized adults"),
        _field_row("Emergency kit at school?"),
        Paragraph("Work", s["h2"]),
        _field_row("Workplace emergency contact"),
        _field_row("WFH / commute notes"),
    ]
    _doc(path, story)
    print(f"  {path.name}")


def page_update(path: Path):
    s = _styles()
    story = [
        Paragraph("13  ·  Monthly / quarterly update checklist", s["h1"]),
        _hline(),
        Paragraph("Every 3 months (or after any big life change)", s["small"]),
    ]
    for it in [
        "Contacts still correct",
        "Medications list updated",
        "Insurance cards current",
        "Document locations still true",
        "Go-bag restocked (water, meds, batteries)",
        "Kids / school info current",
        "Pet vet & microchip current",
        "Digital access notes still accurate",
        "Household photo inventory refreshed",
        "Told trusted person where binder is",
    ]:
        story.append(Paragraph(f"☐  {it}     Date: __________", s["body"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(_field_row("Last full review date"))
    story.append(_field_row("Next scheduled review"))
    _doc(path, story)
    print(f"  {path.name}")


def _draw_corners(c: canvas.Canvas, x, y, w, h, m=8, L=14):
    """Small gold L-marks at corners of a box (x,y = bottom-left)."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.1)
    c.line(x, y + m, x, y)
    c.line(x, y, x + m, y)
    c.line(x + w - m, y, x + w, y)
    c.line(x + w, y, x + w, y + m)
    c.line(x, y + h - m, x, y + h)
    c.line(x, y + h, x + m, y + h)
    c.line(x + w - m, y + h, x + w, y + h)
    c.line(x + w, y + h - m, x + w, y + h)


def _cut_rect(c: canvas.Canvas, x, y, w, h, radius=0):
    """
    Classic scissors-style cut guide: dashed rectangle just outside the label.
    Slightly larger than the solid design so the product edge stays clean.
    """
    pad = 3.5
    c.saveState()
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.7)
    c.setDash(2.5, 2.0)
    if radius > 0:
        c.roundRect(x - pad, y - pad, w + 2 * pad, h + 2 * pad, radius + 1, stroke=1, fill=0)
    else:
        c.rect(x - pad, y - pad, w + 2 * pad, h + 2 * pad, stroke=1, fill=0)
    c.setDash()
    # tiny corner ticks (solid) for registration
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.9)
    t = 5
    # outer box corners
    ox, oy, ow, oh = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    for cx, cy, dx, dy in [
        (ox, oy, 1, 1),
        (ox + ow, oy, -1, 1),
        (ox, oy + oh, 1, -1),
        (ox + ow, oy + oh, -1, -1),
    ]:
        c.line(cx, cy, cx + dx * t, cy)
        c.line(cx, cy, cx, cy + dy * t)
    c.restoreState()


def _centered_text(c: canvas.Canvas, text: str, cx: float, cy: float, font="Helvetica-Bold", size=11, color=NAVY):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(cx, cy - size * 0.35, text)


def _centered_lines(c: canvas.Canvas, lines: list[str], cx: float, cy: float, sizes, colors, leading=14):
    """Draw multi-line centered stack around vertical center cy."""
    total_h = leading * (len(lines) - 1) if lines else 0
    y0 = cy + total_h / 2
    for i, line in enumerate(lines):
        size = sizes[i] if i < len(sizes) else 9
        col = colors[i] if i < len(colors) else NAVY
        font = "Helvetica-Bold" if i == 0 else "Helvetica"
        _centered_text(c, line, cx, y0 - i * leading, font=font, size=size, color=col)


def _spine_vertical(c: canvas.Canvas, x, y, w, h, lines: list[str], fill_navy=False):
    """Vertical spine strip; text rotated 90° and centered on the strip."""
    _cut_rect(c, x, y, w, h, radius=3)
    if fill_navy:
        c.setFillColor(NAVY)
        c.roundRect(x, y, w, h, 4, stroke=0, fill=1)
        text_col = CREAM
        accent = GOLD
    else:
        c.setFillColor(CREAM)
        c.roundRect(x, y, w, h, 4, stroke=0, fill=1)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.4)
        c.roundRect(x, y, w, h, 4, stroke=1, fill=0)
        text_col = NAVY
        accent = GOLD
    c.setStrokeColor(accent)
    c.setLineWidth(1)
    inset = 10
    c.line(x + 4, y + inset, x + w - 4, y + inset)
    c.line(x + 4, y + h - inset, x + w - 4, y + h - inset)

    c.saveState()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(90)
    n = len(lines)
    lead = 13
    total = lead * (n - 1)
    for i, line in enumerate(lines):
        size = 10 if i == 0 else 8
        font = "Helvetica-Bold" if i == 0 else "Helvetica"
        c.setFont(font, size)
        c.setFillColor(text_col if i == 0 else (GOLD if fill_navy else SOFT))
        tw = c.stringWidth(line, font, size)
        c.drawString(-tw / 2, total / 2 - i * lead - size * 0.35, line)
    c.restoreState()


def _label_card(c: canvas.Canvas, x, y, w, h, lines: list[str], fill_navy=False):
    """Horizontal card with upright, centered text + dashed cut guide."""
    _cut_rect(c, x, y, w, h, radius=5)
    if fill_navy:
        c.setFillColor(NAVY)
        c.roundRect(x, y, w, h, 6, stroke=0, fill=1)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.2)
        c.roundRect(x + 5, y + 5, w - 10, h - 10, 4, stroke=1, fill=0)
        cols = [CREAM, GOLD, SOFT]
    else:
        c.setFillColor(CREAM)
        c.roundRect(x, y, w, h, 6, stroke=0, fill=1)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.5)
        c.roundRect(x, y, w, h, 6, stroke=1, fill=0)
        _draw_corners(c, x + 6, y + 6, w - 12, h - 12, m=10, L=12)
        cols = [NAVY, GOLD, SOFT]
    sizes = [12, 9, 8][: len(lines)]
    while len(cols) < len(lines):
        cols.append(cols[-1])
    _centered_lines(c, lines, x + w / 2, y + h / 2, sizes, cols[: len(lines)], leading=15)


def page_spine_labels(path: Path):
    """Printable spine strips + cover labels with dashed cut lines."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    _draw_corners(c, 0.4 * inch, 0.4 * inch, W - 0.8 * inch, H - 0.8 * inch, m=12, L=18)

    # Header (minimal — no meta instructions)
    c.setFillColor(NAVY)
    c.setFont("Times-Bold", 16)
    c.drawCentredString(W / 2, H - 0.62 * inch, "Spine & Cover Labels")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(W * 0.30, H - 0.75 * inch, W * 0.70, H - 0.75 * inch)

    # ── A: horizontal cover cards ─────────────────────────────────────────
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.65 * inch, H - 1.05 * inch, "A  ·  COVER LABELS")

    cards = [
        (True, ["EMERGENCY BINDER", "Family · In Case of Emergency", "MathRelaxing"]),
        (False, ["FAMILY ICE BINDER", "Household readiness", "Update every 3 months"]),
        (True, ["IN CASE OF EMERGENCY", "Contacts · Medical · Documents", "Tell trusted people where this lives"]),
        (False, ["HOUSEHOLD BINDER", "[Write family name]", "Keep with go-bag notes"]),
    ]
    card_w, card_h = 3.35 * inch, 1.05 * inch
    gap_x, gap_y = 0.28 * inch, 0.22 * inch  # room for dashed cut outlines
    x0 = 0.65 * inch
    y0 = H - 1.28 * inch - card_h
    for i, (navy_fill, lines) in enumerate(cards):
        col, row = i % 2, i // 2
        x = x0 + col * (card_w + gap_x)
        y = y0 - row * (card_h + gap_y)
        _label_card(c, x, y, card_w, card_h, lines, fill_navy=navy_fill)

    # ── B: vertical spines ────────────────────────────────────────────────
    y_sec = y0 - 2 * (card_h + gap_y) - 0.32 * inch
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.65 * inch, y_sec + 0.12 * inch, "B  ·  BINDER SPINES")

    spines = [
        (True, ["EMERGENCY", "BINDER", "FAMILY"], 1.0 * inch),
        (False, ["FAMILY", "ICE", "BINDER"], 1.0 * inch),
        (True, ["IN CASE OF", "EMERGENCY"], 1.0 * inch),
        (False, ["HOUSEHOLD", "READY"], 0.85 * inch),
        (True, ["ICE", "DOCS"], 0.7 * inch),
        (False, ["GO-BAG", "+ BINDER"], 0.85 * inch),
    ]
    spine_h = 3.2 * inch
    x = 0.65 * inch
    y = y_sec - spine_h - 0.08 * inch
    for navy_fill, lines, sw in spines:
        _spine_vertical(c, x, y, sw, spine_h, lines, fill_navy=navy_fill)
        x += sw + 0.22 * inch  # gap for dashed outline

    # ── C: divider tabs ───────────────────────────────────────────────────
    y_tabs = y - 0.48 * inch
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.65 * inch, y_tabs, "C  ·  DIVIDER TABS")

    tabs = [
        "START",
        "CONTACTS",
        "MEDICAL",
        "INSURANCE",
        "DOCUMENTS",
        "HOME",
        "MONEY",
        "PETS",
        "DIGITAL",
        "EVAC",
        "SCHOOL",
        "UPDATE",
    ]
    tw, th = 1.05 * inch, 0.42 * inch
    x = 0.65 * inch
    y = y_tabs - 0.52 * inch
    for i, lab in enumerate(tabs):
        if i and i % 6 == 0:
            x = 0.65 * inch
            y -= th + 0.18 * inch
        _cut_rect(c, x, y, tw, th, radius=2)
        c.setFillColor(CREAM)
        c.roundRect(x, y, tw, th, 3, stroke=0, fill=1)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1)
        c.roundRect(x, y, tw, th, 3, stroke=1, fill=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        c.line(x + 6, y + th - 5, x + tw - 6, y + th - 5)
        _centered_text(c, lab, x + tw / 2, y + th / 2, font="Helvetica-Bold", size=7.5, color=NAVY)
        x += tw + 0.14 * inch

    c.setFillColor(SOFT)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(W / 2, 0.38 * inch, "MathRelaxing Family Emergency Binder")
    c.save()
    print(f"  {path.name}")


def merge_pdfs(paths: list[Path], out: Path):
    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfWriter, PdfReader  # type: ignore
        except ImportError:
            # fallback: just zip individual pages
            print("  (pypdf not installed — skipping merged PDF)")
            return
    w = PdfWriter()
    for p in paths:
        r = PdfReader(str(p))
        for page in r.pages:
            w.add_page(page)
    with open(out, "wb") as f:
        w.write(f)
    print(f"  merged {out.name}")


# ── Previews ─────────────────────────────────────────────────────────────────

def _tf(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _ts(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    names = ["segoeuib.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def make_previews():
    S = 2000
    navy, gold, cream = (18, 23, 46), (201, 162, 75), (248, 244, 235)
    paths = []

    # 1 hero
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 80), "FAMILY EMERGENCY BINDER", font=_ts(14, True), fill=gold, anchor="mt")
    d.text((S // 2, 130), "Printable Organizer", font=_tf(44, True), fill=cream, anchor="mt")
    d.text((S // 2, 210), "13 sections  ·  US Letter  ·  fill · update · ready", font=_ts(17), fill=gold, anchor="mt")
    pw, ph = 780, 1000
    px, py = (S - pw) // 2, 300
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([px + 14, py + 18, px + pw + 14, py + ph + 18], fill=(0, 0, 0, 100))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px, py, px + pw, py + ph], fill=cream)
    d.text((px + pw // 2, py + 80), "FAMILY", font=_ts(14, True), fill=gold, anchor="mt")
    d.text((px + pw // 2, py + 130), "Emergency Binder", font=_tf(32, True), fill=navy, anchor="mt")
    d.line([(px + 140, py + 200), (px + pw - 140, py + 200)], fill=gold, width=2)
    y = py + 260
    for lab in ["Contacts", "Medical", "Insurance", "Documents", "Go-bag", "Meeting place"]:
        d.rounded_rectangle([px + 80, y, px + pw - 80, y + 70], radius=8, outline=navy, width=2)
        d.text((px + 110, y + 35), "§  " + lab, font=_ts(18), fill=navy, anchor="lm")
        y += 90
    d.rectangle([0, S - 90, S, S], fill=(8, 10, 22))
    d.text((S // 2, S - 45), "MathRelaxing  ·  Calm systems for real life", font=_ts(17), fill=gold, anchor="mm")
    p = PREVIEWS / "eb_preview_1_hero.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 2 sections grid
    img = Image.new("RGB", (S, S), cream)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "What's inside", font=_tf(36, True), fill=navy, anchor="mt")
    secs = [
        "01 Quick start",
        "02 Contacts",
        "03 Household",
        "04 Medical",
        "05 Insurance",
        "06 Documents",
        "07 Home & property",
        "08 Finances",
        "09 Pets",
        "10 Digital access",
        "11 Evacuation",
        "12 Meeting / school",
        "13 Update checklist",
        "Spine labels",
    ]
    # 2 columns
    for i, lab in enumerate(secs):
        col, row = i % 2, i // 2
        x = 120 + col * 920
        y = 160 + row * 200
        d.rounded_rectangle([x, y, x + 840, y + 160], radius=10, fill=navy)
        d.text((x + 50, y + 80), lab, font=_ts(26), fill=cream, anchor="lm")
    p = PREVIEWS / "eb_preview_2_sections.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 3 why now
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 80), "Why this binder", font=_tf(36, True), fill=cream, anchor="mt")
    points = [
        ("Built for action", "Checklists and fields you can fill\nin one evening — not a 200-page book."),
        ("Rising demand now", "eRank: emergency binder warming\n(Jun 2026 up vs average)."),
        ("Editorial, not clutter", "Navy · gold · cream. Clear tabs.\nNo cartoon panic graphics."),
        ("Privacy-aware", "Prompts for locations and nicknames —\nnot a dump of full passwords."),
    ]
    y = 200
    for title, body in points:
        d.rounded_rectangle([140, y, S - 140, y + 320], radius=12, outline=gold, width=2)
        d.text((200, y + 50), title, font=_tf(24, True), fill=gold, anchor="lt")
        for j, line in enumerate(body.split("\n")):
            d.text((200, y + 130 + j * 45), line, font=_ts(20), fill=cream, anchor="lt")
        y += 360
    p = PREVIEWS / "eb_preview_3_why.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 4 detail form
    img = Image.new("RGB", (S, S), (228, 224, 216))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([180, 200, 1820, 1600], radius=8, fill=cream)
    d.text((1000, 280), "02  ·  Emergency contacts", font=_tf(28, True), fill=navy, anchor="mt")
    d.line([(400, 350), (1600, 350)], fill=gold, width=2)
    y = 420
    for lab in ["Local emergency services", "Family doctor / clinic", "Nearest hospital", "Trusted person 1", "Trusted person 2"]:
        d.text((320, y), lab.upper(), font=_ts(14, True), fill=gold, anchor="lt")
        d.line([(320, y + 50), (1680, y + 50)], fill=(200, 195, 185), width=2)
        y += 120
    d.rectangle([0, S - 90, S, S], fill=navy)
    d.text((S // 2, S - 45), "Printable fields  ·  US Letter  ·  binder-ready", font=_ts(17), fill=gold, anchor="mm")
    p = PREVIEWS / "eb_preview_4_detail.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 5 how it works
    img = Image.new("RGB", (S, S), cream)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "How it works", font=_tf(40, True), fill=navy, anchor="mt")
    steps = [
        ("1", "Print", "US Letter PDF pages\n+ spine labels"),
        ("2", "Fill", "Contacts, medical,\ninsurance, documents"),
        ("3", "Assemble", "Binder + sheet protectors\n+ tab dividers"),
        ("4", "Share", "Tell 1–2 trusted people\nwhere it lives"),
        ("5", "Update", "Quarterly checklist\nincluded"),
        ("6", "Act", "First-10-minutes list\nwhen it matters"),
    ]
    cw, ch = 560, 420
    gap = 40
    x0 = (S - 3 * cw - 2 * gap) // 2
    y0 = 200
    for i, (n, title, sub) in enumerate(steps):
        c, r = i % 3, i // 3
        x = x0 + c * (cw + gap)
        y = y0 + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=12, fill=navy)
        d.ellipse([x + 36, y + 36, x + 110, y + 110], outline=gold, width=3)
        d.text((x + 73, y + 73), n, font=_tf(22, True), fill=gold, anchor="mm")
        d.text((x + 40, y + 160), title, font=_tf(26, True), fill=cream, anchor="lt")
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 40, y + 240 + j * 40), line, font=_ts(18), fill=gold, anchor="lt")
    p = PREVIEWS / "eb_preview_5_how.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 6 value
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 100), "Complete household system", font=_tf(34, True), fill=cream, anchor="mt")
    stats = [("13+", "Sections"), ("US", "Letter PDF"), ("ICE", "Ready"), ("$9.99", "Kit price")]
    for i, (n, lab) in enumerate(stats):
        c, r = i % 2, i // 2
        x = 200 + c * 850
        y = 280 + r * 550
        d.rounded_rectangle([x, y, x + 750, y + 450], radius=16, outline=gold, width=2)
        d.text((x + 375, y + 140), n, font=_tf(52, True), fill=gold, anchor="mt")
        d.text((x + 375, y + 280), lab, font=_ts(24), fill=cream, anchor="mt")
    p = PREVIEWS / "eb_preview_6_value.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)
    print(f"  {len(paths)} previews")
    return paths


def build_zip(page_files: list[Path]):
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for p in page_files:
            z.write(p, f"pages/{p.name}")
        merged = OUT / "MathRelaxing_Family_Emergency_Binder_ALL_PAGES.pdf"
        if merged.exists():
            z.write(merged, merged.name)
        readme = OUT / "README.txt"
        readme.write_text(
            "MathRelaxing Family Emergency Binder\n"
            "====================================\n\n"
            "1. Print pages/ or the merged ALL_PAGES.pdf (US Letter).\n"
            "2. Use a 1–2 inch binder + tab dividers + sheet protectors.\n"
            "3. Fill contacts, medical, insurance, documents.\n"
            "4. Tell trusted people where the binder is.\n"
            "5. Review every 3 months (page 13).\n\n"
            + brand.COPYRIGHT
            + "\n",
            encoding="utf-8",
        )
        z.write(readme, "README.txt")
    print(f"ZIP {ZIP_PATH.name} ({ZIP_PATH.stat().st_size / 1024:.0f} KB)")


def main():
    _ensure()
    print("=== Family Emergency Binder ===")
    pages = [
        (PAGES / "00_Cover.pdf", page_cover),
        (PAGES / "01_Contents.pdf", page_contents),
        (PAGES / "02_Quick_Start.pdf", page_quick_start),
        (PAGES / "03_Emergency_Contacts.pdf", page_contacts),
        (PAGES / "04_Household_Members.pdf", page_household),
        (PAGES / "05_Medical.pdf", page_medical),
        (PAGES / "06_Insurance.pdf", page_insurance),
        (PAGES / "07_Documents_Checklist.pdf", page_documents),
        (PAGES / "08_Home_Property.pdf", page_home),
        (PAGES / "09_Finances.pdf", page_finances),
        (PAGES / "10_Pets.pdf", page_pets),
        (PAGES / "11_Digital_Access.pdf", page_digital),
        (PAGES / "12_Evacuation_GoBag.pdf", page_evac),
        (PAGES / "13_Meeting_School.pdf", page_meeting),
        (PAGES / "14_Update_Checklist.pdf", page_update),
        (PAGES / "15_Spine_Labels.pdf", page_spine_labels),
    ]
    paths = []
    for path, fn in pages:
        fn(path)
        paths.append(path)
    merge_pdfs(paths, OUT / "MathRelaxing_Family_Emergency_Binder_ALL_PAGES.pdf")
    make_previews()
    build_zip(paths)
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
