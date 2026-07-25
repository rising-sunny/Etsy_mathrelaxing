"""
password_tracker/kit.py — elegant form toolkit for the Password & Login Tracker.

Design system: warm ivory paper, charcoal ink, soft bronze accent.
Typography: Cinzel (display) + Georgia (serif body) + Raleway (UI labels).
No shop branding.
"""
from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, HRFlowable, Paragraph, Spacer, Table, TableStyle

W, H = letter  # 612 x 792

# Refined palette — ivory paper, high-contrast ink (readable print + screen)
IVORY = HexColor("#F4EFE6")       # slightly deeper paper so white cards pop
PAPER = HexColor("#FFFDF9")
CHARCOAL = HexColor("#141311")    # near-black for titles
INK = HexColor("#1A1917")         # body text (was too soft)
MUTED = HexColor("#3F3C38")       # secondary labels — still elegant, not washed out
MUTED_SOFT = HexColor("#5C574F")  # captions / footers only
RULE = HexColor("#C9C0B0")
BRONZE = HexColor("#7A5E35")      # deeper bronze for contrast on ivory
BRONZE_SOFT = HexColor("#A8844E")
ROW_ALT = HexColor("#EDE6DA")
WHITE = HexColor("#FFFFFF")

# Back-compat aliases used by generator
CREAM = IVORY
GOLD = BRONZE
NAVY = CHARCOAL
SOFT = MUTED
LINE = RULE

_BASE = Path(__file__).resolve().parent.parent
_FONT_CANDIDATES = {
    "Cinzel": [
        _BASE / "lulu_books" / "assets" / "fonts" / "Cinzel.ttf",
        Path(r"C:\repos\mathrelaxing.store\static\fonts\Cinzel.ttf"),
    ],
    "Cinzel-SemiBold": [
        _BASE / "lulu_books" / "assets" / "fonts" / "Cinzel-SemiBold.ttf",
    ],
    "Raleway": [
        _BASE / "lulu_books" / "assets" / "fonts" / "Raleway.ttf",
        Path(r"C:\repos\mathrelaxing.store\static\fonts\Raleway.ttf"),
    ],
    "Raleway-Italic": [
        _BASE / "lulu_books" / "assets" / "fonts" / "Raleway-Italic.ttf",
        Path(r"C:\repos\mathrelaxing.store\static\fonts\Raleway-Italic.ttf"),
    ],
    "Georgia": [Path(r"C:\Windows\Fonts\georgia.ttf")],
    "Georgia-Bold": [Path(r"C:\Windows\Fonts\georgiab.ttf")],
    "Georgia-Italic": [Path(r"C:\Windows\Fonts\georgiai.ttf")],
}

_FONTS_READY = False
# Logical names after register (fallback to Times/Helvetica)
F_DISPLAY = "Times-Bold"
F_DISPLAY_REG = "Times-Roman"
F_SERIF = "Times-Roman"
F_SERIF_BOLD = "Times-Bold"
F_SERIF_IT = "Times-Italic"
F_SANS = "Helvetica"
F_SANS_BOLD = "Helvetica-Bold"
F_SANS_IT = "Helvetica-Oblique"


def ensure_fonts() -> None:
    global _FONTS_READY, F_DISPLAY, F_DISPLAY_REG, F_SERIF, F_SERIF_BOLD, F_SERIF_IT
    global F_SANS, F_SANS_BOLD, F_SANS_IT
    if _FONTS_READY:
        return

    def _reg(name: str) -> str | None:
        for p in _FONT_CANDIDATES.get(name, []):
            if p and Path(p).is_file():
                try:
                    pdfmetrics.registerFont(TTFont(name, str(p)))
                    return name
                except Exception:
                    continue
        return None

    cinzel = _reg("Cinzel")
    cinzel_sb = _reg("Cinzel-SemiBold")
    raleway = _reg("Raleway")
    raleway_it = _reg("Raleway-Italic")
    geo = _reg("Georgia")
    geo_b = _reg("Georgia-Bold")
    geo_i = _reg("Georgia-Italic")

    if cinzel:
        F_DISPLAY = cinzel_sb or cinzel
        F_DISPLAY_REG = cinzel
    if geo:
        F_SERIF = geo
        F_SERIF_BOLD = geo_b or geo
        F_SERIF_IT = geo_i or geo
    if raleway:
        F_SANS = raleway
        F_SANS_BOLD = raleway  # Raleway file is variable/regular; weight via size
        F_SANS_IT = raleway_it or raleway

    _FONTS_READY = True


def styles() -> dict[str, ParagraphStyle]:
    ensure_fonts()
    return {
        "cover_kicker": ParagraphStyle(
            "pt_kicker",
            fontName=F_SANS,
            fontSize=8.5,
            textColor=BRONZE,
            alignment=1,
            leading=11,
            spaceAfter=14,
        ),
        "cover_title": ParagraphStyle(
            "pt_ct",
            fontName=F_DISPLAY,
            fontSize=34,
            textColor=CHARCOAL,
            alignment=1,
            leading=40,
            spaceAfter=4,
        ),
        "cover_sub": ParagraphStyle(
            "pt_cs",
            fontName=F_SERIF_IT,
            fontSize=11.5,
            textColor=MUTED,  # was washed gray on ivory
            alignment=1,
            leading=16,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "pt_h1",
            fontName=F_DISPLAY,
            fontSize=16,
            textColor=CHARCOAL,
            spaceBefore=0,
            spaceAfter=4,
            leading=20,
        ),
        "h2": ParagraphStyle(
            "pt_h2",
            fontName=F_SANS,
            fontSize=8.5,
            textColor=CHARCOAL,  # section labels: dark, not pale bronze
            spaceBefore=12,
            spaceAfter=5,
            leading=11,
        ),
        "body": ParagraphStyle(
            "pt_body",
            fontName=F_SERIF,
            fontSize=10.5,
            textColor=INK,
            leading=14.5,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "pt_small",
            fontName=F_SERIF,
            fontSize=9,
            textColor=MUTED,
            leading=12.5,
            spaceAfter=3,
        ),
        "label": ParagraphStyle(
            "pt_label",
            fontName=F_SANS,
            fontSize=8,
            textColor=MUTED,
            spaceAfter=1,
        ),
        "cell": ParagraphStyle(
            "pt_cell",
            fontName=F_SANS,
            fontSize=8.5,
            textColor=MUTED,
            leading=10.5,
        ),
        "foot": ParagraphStyle(
            "pt_foot",
            fontName=F_SANS,
            fontSize=7.5,
            textColor=MUTED_SOFT,
            alignment=1,
        ),
        "index_row": ParagraphStyle(
            "pt_idx",
            fontName=F_SERIF,
            fontSize=10.5,
            textColor=INK,
            leading=14.5,
        ),
    }


def thin_rule(width="100%", space_before=2, space_after=10) -> HRFlowable:
    return HRFlowable(
        width=width,
        thickness=0.6,
        color=BRONZE_SOFT,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )


def gold_rule(width="100%", thick=0.6) -> HRFlowable:
    """Alias used by generator."""
    return thin_rule(width=width, space_before=2, space_after=10)


def field_line(label: str, col_w: float = 6.5 * inch) -> Table:
    ensure_fonts()
    st = styles()
    data = [[Paragraph(label, st["label"]), ""]]
    t = Table(data, colWidths=[1.75 * inch, col_w - 1.75 * inch])
    t.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (1, 0), (1, 0), 0.45, RULE),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return t


class CredentialCard(Flowable):
    """Quiet card: hairline border, bronze index, generous field lines."""

    def __init__(self, width: float, index: int | None = None, height: float = 84):
        super().__init__()
        self.box_width = width
        self.index = index
        self.box_height = height

    def wrap(self, availWidth, availHeight):
        self.width = min(self.box_width, availWidth)
        self.height = self.box_height
        return self.width, self.height

    def draw(self):
        ensure_fonts()
        c = self.canv
        w, h = self.width, self.height

        # soft paper card
        c.setFillColor(PAPER)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.7)
        c.roundRect(0, 0, w, h, 3, fill=1, stroke=1)

        # subtle top edge in bronze
        c.setStrokeColor(BRONZE_SOFT)
        c.setLineWidth(0.9)
        c.line(12, h - 0.5, w - 12, h - 0.5)

        # index
        left = 14
        if self.index is not None:
            c.setFillColor(CHARCOAL)
            c.setFont(F_DISPLAY, 8.5)
            c.drawString(12, h - 16, f"{self.index:02d}")
            left = 36

        def lab_line(y, text, x0=None, x1=None):
            x0 = left if x0 is None else x0
            x1 = w - 12 if x1 is None else x1
            c.setFillColor(MUTED)
            c.setFont(F_SANS, 7.2)
            c.drawString(x0, y, text.upper())
            c.setStrokeColor(RULE)
            c.setLineWidth(0.6)
            c.line(x0, y - 3.5, x1, y - 3.5)

        lab_line(h - 16, "Website / app")
        lab_line(h - 34, "Username / email")
        mid = w * 0.52
        lab_line(h - 52, "Password", x1=mid - 10)
        lab_line(h - 52, "2FA / recovery", x0=mid, x1=w - 12)
        lab_line(h - 70, "Notes")


def credential_stack(n: int, width: float = 6.55 * inch, start: int = 1) -> list:
    items: list = []
    for i in range(n):
        items.append(CredentialCard(width, index=start + i))
        items.append(Spacer(1, 7))
    return items


def log_table(rows: int = 14, width: float = 6.55 * inch) -> Table:
    ensure_fonts()
    st = styles()
    headers = ["Date", "Site / app", "Action", "Notes"]
    col_w = [0.95 * inch, 1.95 * inch, 1.35 * inch, width - 4.25 * inch]
    data = [[Paragraph(h, st["cell"]) for h in headers]]
    for _ in range(rows):
        data.append(["", "", "", ""])
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CHARCOAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), IVORY),
                ("FONTNAME", (0, 0), (-1, 0), F_SANS),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, ROW_ALT]),
            ]
        )
    )
    return t


def wifi_block(width: float = 6.55 * inch) -> list:
    return [
        field_line("Network name (SSID)", width),
        field_line("Wi-Fi password", width),
        field_line("Router admin URL", width),
        field_line("Router admin user", width),
        field_line("Router admin password", width),
        field_line("ISP / account number", width),
        field_line("Guest network", width),
        field_line("Notes", width),
    ]


def checkbox_tips(items: list[str]) -> list:
    st = styles()
    out = []
    for it in items:
        out.append(Paragraph(f"<font color='#7A5E35' size='9'>●</font>  &nbsp;{it}", st["body"]))
    return out
