"""
generate_password_tracker.py — Password & Login Tracker (printable PDF)
=======================================================================
Elegant private password log. No shop branding on the deliverable.

Stack: reportlab + password_tracker/kit.py (Cinzel / Georgia / Raleway when available).

  python generate_password_tracker.py
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

from password_tracker import kit
from password_tracker.kit import (
    BRONZE,
    BRONZE_SOFT,
    CHARCOAL,
    INK,
    IVORY,
    MUTED,
    MUTED_SOFT,
    PAPER,
    RULE,
    W,
    H,
    checkbox_tips,
    credential_stack,
    ensure_fonts,
    field_line,
    gold_rule,
    log_table,
    styles,
    thin_rule,
    wifi_block,
    F_DISPLAY,
    F_SANS,
    F_SERIF,
    F_SERIF_IT,
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "password_tracker"
PREVIEWS = OUT / "previews"
PDF_PATH = OUT / "Password_Login_Tracker.pdf"
ZIP_PATH = OUT / "Password_Login_Tracker.zip"

SECTIONS: list[tuple[str, str, int]] = [
    ("01", "Email & cloud accounts", 4),
    ("02", "Banking & finance", 4),
    ("03", "Shopping & payments", 4),
    ("04", "Streaming & entertainment", 4),
    ("05", "Social & messaging", 4),
    ("06", "Work & school", 4),
    ("07", "Devices & apps", 4),
    ("08", "Utilities & subscriptions", 4),
    ("09", "General log pages", 5),
]


def _ensure():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    ensure_fonts()


# ── page chrome ──────────────────────────────────────────────────────────────

def _page_bg(canv: canvas.Canvas, doc):
    ensure_fonts()
    canv.saveState()
    canv.setFillColor(IVORY)
    canv.rect(0, 0, W, H, fill=1, stroke=0)

    # elegant top: thin double rule + small caps title (no brand)
    y_top = H - 0.48 * inch
    canv.setStrokeColor(BRONZE_SOFT)
    canv.setLineWidth(0.9)
    canv.line(0.65 * inch, y_top, W - 0.65 * inch, y_top)
    canv.setLineWidth(0.35)
    canv.line(0.65 * inch, y_top - 3.2, W - 0.65 * inch, y_top - 3.2)

    canv.setFillColor(CHARCOAL)
    canv.setFont(F_SANS, 7.5)
    canv.drawCentredString(W / 2, y_top + 8, "P A S S W O R D   &   L O G I N   T R A C K E R")

    # footer
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.4)
    canv.line(0.65 * inch, 0.55 * inch, W - 0.65 * inch, 0.55 * inch)
    canv.setFillColor(MUTED)
    canv.setFont(F_SANS, 7)
    canv.drawString(0.65 * inch, 0.38 * inch, "Private  ·  Offline use  ·  Update when you change passwords")
    if doc.page > 1:
        canv.setFont(F_SERIF, 9)
        canv.setFillColor(CHARCOAL)
        canv.drawRightString(W - 0.65 * inch, 0.38 * inch, f"—  {doc.page}  —")
    canv.restoreState()


def _cover_bg(canv: canvas.Canvas, doc):
    ensure_fonts()
    canv.saveState()
    # full ivory cover (not heavy navy block)
    canv.setFillColor(IVORY)
    canv.rect(0, 0, W, H, fill=1, stroke=0)

    # outer bronze frame
    m = 0.55 * inch
    canv.setStrokeColor(BRONZE_SOFT)
    canv.setLineWidth(1.1)
    canv.rect(m, m, W - 2 * m, H - 2 * m, fill=0, stroke=1)
    canv.setLineWidth(0.35)
    inset = 0.12 * inch
    canv.rect(m + inset, m + inset, W - 2 * m - 2 * inset, H - 2 * m - 2 * inset, fill=0, stroke=1)

    # decorative diamond
    cx, cy = W / 2, H - 1.35 * inch
    canv.setStrokeColor(BRONZE)
    canv.setLineWidth(0.8)
    s = 5
    canv.line(cx, cy + s, cx + s, cy)
    canv.line(cx + s, cy, cx, cy - s)
    canv.line(cx, cy - s, cx - s, cy)
    canv.line(cx - s, cy, cx, cy + s)

    canv.setFillColor(MUTED)
    canv.setFont(F_SANS, 8)
    canv.drawCentredString(W / 2, 0.85 * inch, "U S   L E T T E R   ·   P R I N T A B L E")
    canv.restoreState()


# ── story ────────────────────────────────────────────────────────────────────

def _cover_flow():
    st = styles()
    story = [Spacer(1, 2.15 * inch)]
    story.append(
        Paragraph(
            "A PRIVATE LOGBOOK",
            ParagraphStyle(
                "k",
                fontName=F_SANS,
                fontSize=8.5,
                textColor=MUTED,
                alignment=1,
                spaceAfter=16,
            ),
        )
    )
    story.append(Paragraph("Password", st["cover_title"]))
    story.append(Paragraph("&amp; Login", st["cover_title"]))
    story.append(Spacer(1, 10))
    story.append(thin_rule("28%", space_before=2, space_after=14))
    story.append(
        Paragraph(
            "Websites, Wi-Fi, apps &amp; recovery notes —<br/>kept quietly in one place.",
            ParagraphStyle(
                "cover_sub2",
                fontName=F_SERIF_IT,
                fontSize=12,
                textColor=MUTED,
                alignment=1,
                leading=17,
                spaceAfter=8,
            ),
        )
    )
    story.append(Spacer(1, 28))
    story.append(
        Paragraph(
            "A paper companion to your password manager.<br/>"
            "Not a replacement — a private record you control.",
            ParagraphStyle(
                "cv",
                fontName=F_SERIF,
                fontSize=9.5,
                textColor=MUTED,
                alignment=1,
                leading=14,
            ),
        )
    )
    story.append(Spacer(1, 1.15 * inch))
    for b in (
        "Categorized credential cards",
        "Home network &amp; Wi-Fi sheet",
        "Recovery &amp; 2FA notes",
        "Password change history",
    ):
        story.append(
            Paragraph(
                f"<font color='#7A5E35' size='9'>◆</font>  &nbsp;&nbsp;{b}",
                ParagraphStyle(
                    "cb",
                    fontName=F_SERIF,
                    fontSize=10.5,
                    textColor=INK,
                    alignment=1,
                    leading=16,
                    spaceAfter=3,
                ),
            )
        )
    story.append(PageBreak())
    return story


def _howto_flow():
    st = styles()
    return [
        Paragraph("How to use this tracker", st["h1"]),
        thin_rule(),
        Paragraph(
            "This book is for <i>private offline use</i>. Fill only what you need. "
            "It complements a modern password manager — it does not replace one.",
            st["body"],
        ),
        Paragraph("WORKFLOW", st["h2"]),
        *checkbox_tips(
            [
                "Print on US Letter, or open the PDF in a notes app on a tablet.",
                "Begin with Email, Banking, and Wi-Fi — highest-impact accounts.",
                "Record recovery email, phone, and 2FA method in the recovery fields.",
                "When you rotate a password, add a line on the Change history page.",
                "Keep the binder or device in a locked place; avoid cloud photos of filled pages.",
                "Tell one trusted person <i>where</i> the book lives — not what is inside.",
            ]
        ),
        Paragraph("SECURITY NOTES", st["h2"]),
        Paragraph(
            "Prefer unique passwords; this log helps you remember them, not reuse them. "
            "Never store a password-manager master password here. "
            "If a page is lost, change those passwords first. "
            "Optional: use a private shorthand only you understand.",
            st["small"],
        ),
        Paragraph("A NOTE ON SCOPE", st["h2"]),
        Paragraph(
            "Household emergency organizers should only record <i>where</i> digital access lives. "
            "This tracker is the dedicated place for login details — keep the two separate.",
            st["body"],
        ),
        PageBreak(),
    ]


def _index_flow():
    st = styles()
    story = [
        Paragraph("Contents", st["h1"]),
        thin_rule(),
    ]
    rows = [
        ["", "Section", ""],
        ["", "How to use & security", ""],
        ["", "Contents", ""],
        ["", "Master recovery sheet", ""],
        ["", "Home network & Wi-Fi", ""],
    ]
    for code, title, _n in SECTIONS:
        if code == "09":
            rows.append([code, title, ""])
        else:
            rows.append([code, title, ""])
    rows.append(["", "Password change history", ""])
    rows.append(["", "Quick notes", ""])

    data = []
    for i, r in enumerate(rows):
        if i == 0:
            data.append(
                [
                    Paragraph("", st["cell"]),
                    Paragraph("<b>Section</b>", st["cell"]),
                    Paragraph("", st["cell"]),
                ]
            )
        else:
            data.append(
                [
                    Paragraph(f"<font color='#7A5E35'><b>{r[0]}</b></font>" if r[0] else "", st["cell"]),
                    Paragraph(r[1], st["index_row"]),
                    Paragraph("", st["cell"]),
                ]
            )
    t = Table(data, colWidths=[0.5 * inch, 5.5 * inch, 0.5 * inch])
    cmds = [
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, BRONZE_SOFT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "Tip: print double-sided and use tab dividers labeled 01–09 for a slim binder.",
            st["small"],
        )
    )
    story.append(PageBreak())
    return story


def _recovery_flow():
    st = styles()
    return [
        Paragraph("Master recovery sheet", st["h1"]),
        thin_rule(),
        Paragraph(
            "High-level recovery only — do <b>not</b> write a password-manager master password here.",
            st["small"],
        ),
        Spacer(1, 4),
        Paragraph("PASSWORD MANAGER", st["h2"]),
        field_line("App / service name"),
        field_line("Account email"),
        field_line("Emergency kit / recovery codes location"),
        field_line("Who has emergency access"),
        Paragraph("PRIMARY RECOVERY CHANNELS", st["h2"]),
        field_line("Primary email"),
        field_line("Secondary email"),
        field_line("Phone for SMS / app 2FA"),
        field_line("Authenticator app device"),
        Paragraph("DEVICE UNLOCK NOTES", st["h2"]),
        field_line("Phone model / find-my account"),
        field_line("Laptop recovery key location"),
        field_line("Important notes"),
        PageBreak(),
    ]


def _wifi_flow():
    st = styles()
    return [
        Paragraph("Home network &amp; Wi-Fi", st["h1"]),
        thin_rule(),
        Paragraph("PRIMARY NETWORK", st["h2"]),
        *wifi_block(),
        Spacer(1, 6),
        Paragraph("SECONDARY / GUEST / OFFICE", st["h2"]),
        field_line("Network name (SSID)"),
        field_line("Wi-Fi password"),
        field_line("Notes"),
        PageBreak(),
    ]


def _category_flow(code: str, title: str, n_cards: int):
    st = styles()
    return [
        Paragraph(f"{code}    {title}", st["h1"]),
        thin_rule(),
        *credential_stack(n_cards, start=1),
        PageBreak(),
    ]


def _general_pages(n_pages: int = 3):
    st = styles()
    story = []
    for p in range(n_pages):
        story.append(Paragraph(f"09    General log    ·    {p + 1}", st["h1"]))
        story.append(thin_rule())
        story.extend(credential_stack(5, start=1 + p * 5))
        story.append(PageBreak())
    return story


def _change_history_flow():
    st = styles()
    return [
        Paragraph("Password change history", st["h1"]),
        thin_rule(),
        Paragraph(
            "Log resets and rotations. Examples: changed · rotated · retired · breach response.",
            st["small"],
        ),
        Spacer(1, 8),
        log_table(rows=16),
        PageBreak(),
    ]


def _notes_flow():
    st = styles()
    story = [
        Paragraph("Quick notes", st["h1"]),
        thin_rule(),
        Paragraph(
            "Shared household rules, migration checklist, or carefully stored security-question hints.",
            st["small"],
        ),
        Spacer(1, 6),
    ]
    for _ in range(14):
        story.append(field_line("Note", 6.55 * inch))
    return story


def build_pdf() -> Path:
    _ensure()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=(W, H),
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.78 * inch,
        title="Password & Login Tracker",
        author="",
    )
    story: list = []
    story += _cover_flow()
    story += _howto_flow()
    story += _index_flow()
    story += _recovery_flow()
    story += _wifi_flow()
    for code, title, n in SECTIONS:
        if code == "09":
            story += _general_pages(3)
        else:
            story += _category_flow(code, title, n)
    story += _change_history_flow()
    story += _notes_flow()

    doc.build(story, onFirstPage=_cover_bg, onLaterPages=_page_bg)
    print("PDF:", PDF_PATH, f"({PDF_PATH.stat().st_size // 1024} KB)")
    return PDF_PATH


# ── listing previews (real PDF page mockups) ─────────────────────────────────

def _font_path(kind: str) -> str | None:
    root = BASE
    maps = {
        "display": [
            root / "lulu_books/assets/fonts/Cinzel-SemiBold.ttf",
            root / "lulu_books/assets/fonts/Cinzel.ttf",
            Path(r"C:\Windows\Fonts\georgiab.ttf"),
        ],
        "serif": [
            Path(r"C:\Windows\Fonts\georgia.ttf"),
            root / "lulu_books/assets/fonts/Cinzel.ttf",
        ],
        "sans": [
            root / "lulu_books/assets/fonts/Raleway.ttf",
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
        ],
    }
    for p in maps.get(kind, []):
        if Path(p).is_file():
            return str(p)
    return None


def _f(kind: str, size: int):
    path = _font_path(kind)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _render_pdf_pages(pdf_path: Path, dpi: float = 140) -> list[Image.Image]:
    """Rasterize every PDF page for mockups."""
    import fitz

    doc = fitz.open(str(pdf_path))
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pages = []
    for i in range(doc.page_count):
        pix = doc[i].get_pixmap(matrix=mat, alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        pages.append(im)
    doc.close()
    return pages


def _drop_shadow(base: Image.Image, page: Image.Image, xy: tuple[int, int], blur: int = 18, alpha: int = 90):
    """Paste page with soft shadow onto base (RGB)."""
    x, y = xy
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([x + 10, y + 14, x + page.width + 10, y + page.height + 14], fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(base.convert("RGBA"), shadow)
    out.paste(page, (x, y))
    return out.convert("RGB")


def _fit_page(page: Image.Image, max_h: int, max_w: int | None = None) -> Image.Image:
    w, h = page.size
    scale = max_h / h
    if max_w is not None:
        scale = min(scale, max_w / w)
    nw, nh = int(w * scale), int(h * scale)
    return page.resize((nw, nh), Image.Resampling.LANCZOS)


def make_previews() -> list[Path]:
    """
    Etsy gallery: show REAL product pages (PDF renders), not empty abstract cards.
    Fixes sparse/broken layouts (e.g. previous 'How it works' columns).
    """
    S = 2000
    ivory, charcoal = (244, 239, 230), (20, 19, 17)
    bronze, muted = (122, 94, 53), (63, 60, 56)
    warm_bg = (236, 230, 218)
    paths: list[Path] = []

    if not PDF_PATH.is_file():
        raise FileNotFoundError(f"Build PDF first: {PDF_PATH}")
    pages = _render_pdf_pages(PDF_PATH, dpi=150)
    # Useful page indices (0-based): cover, howto, index, recovery, wifi, email, banking, change hist
    n = len(pages)
    cover = pages[0]
    howto = pages[1] if n > 1 else cover
    index = pages[2] if n > 2 else cover
    recovery = pages[3] if n > 3 else cover
    wifi = pages[4] if n > 4 else cover
    email = pages[5] if n > 5 else cover
    banking = pages[6] if n > 6 else cover
    change = pages[n - 2] if n > 2 else cover

    # ── 1 HERO: cover page centered with soft scene ─────────────────────────
    img = Image.new("RGB", (S, S), ivory)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "PASSWORD & LOGIN TRACKER", font=_f("sans", 22), fill=bronze, anchor="mt")
    d.text((S // 2, 120), "Printable password book  ·  US Letter PDF", font=_f("serif", 24), fill=muted, anchor="mt")
    pg = _fit_page(cover, max_h=1580)
    x = (S - pg.width) // 2
    y = 200
    img = _drop_shadow(img, pg, (x, y), blur=22, alpha=100)
    d = ImageDraw.Draw(img)
    d.text((S // 2, S - 55), "Instant download  ·  18 pages", font=_f("sans", 20), fill=muted, anchor="mt")
    p = PREVIEWS / "pt_preview_1_hero.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # ── 2 INSIDE: three real pages side by side ─────────────────────────────
    img = Image.new("RGB", (S, S), warm_bg)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "What's inside", font=_f("display", 40), fill=charcoal, anchor="mt")
    d.line([(S // 2 - 50, 115), (S // 2 + 50, 115)], fill=bronze, width=2)
    trio = [email, wifi, recovery]
    labels = ["Category log", "Wi-Fi sheet", "Recovery"]
    gap = 36
    max_h = 1480
    # equal width columns
    col_w = (S - 2 * 80 - 2 * gap) // 3
    for i, (pg0, lab) in enumerate(zip(trio, labels)):
        pg = _fit_page(pg0, max_h=max_h, max_w=col_w)
        x = 80 + i * (col_w + gap) + (col_w - pg.width) // 2
        y = 180
        img = _drop_shadow(img, pg, (x, y), blur=14, alpha=85)
        d = ImageDraw.Draw(img)
        d.text((x + pg.width // 2, y + pg.height + 28), lab, font=_f("sans", 20), fill=muted, anchor="mt")
    p = PREVIEWS / "pt_preview_2_sections.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # ── 3 DETAIL: single page close-up (credential cards) ───────────────────
    img = Image.new("RGB", (S, S), charcoal)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 60), "Card-style login entries", font=_f("display", 36), fill=ivory, anchor="mt")
    d.text(
        (S // 2, 120),
        "Site  ·  username  ·  password  ·  2FA  ·  notes",
        font=_f("serif", 22),
        fill=bronze,
        anchor="mt",
    )
    pg = _fit_page(email, max_h=1550)
    x = (S - pg.width) // 2
    y = 200
    # white frame
    d.rectangle([x - 12, y - 12, x + pg.width + 12, y + pg.height + 12], fill=(255, 253, 249))
    img.paste(pg, (x, y))
    p = PREVIEWS / "pt_preview_3_why.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # ── 4 WIFI page full ────────────────────────────────────────────────────
    img = Image.new("RGB", (S, S), ivory)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "Home network & Wi-Fi", font=_f("display", 38), fill=charcoal, anchor="mt")
    pg = _fit_page(wifi, max_h=1620)
    x = (S - pg.width) // 2
    y = 140
    img = _drop_shadow(img, pg, (x, y), blur=18, alpha=95)
    p = PREVIEWS / "pt_preview_4_wifi.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # ── 5 HOW: four compact steps + small page thumb ────────────────────────
    img = Image.new("RGB", (S, S), ivory)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "How it works", font=_f("display", 44), fill=charcoal, anchor="mt")
    steps = [
        ("1", "Download", "Instant PDF"),
        ("2", "Print or tablet", "Binder / notes app"),
        ("3", "Fill by category", "Cards + Wi-Fi"),
        ("4", "Update", "Change history"),
    ]
    # balanced cards: 2x2 grid (not tall empty columns)
    card_w, card_h = 820, 380
    gap_x, gap_y = 50, 45
    x0 = (S - 2 * card_w - gap_x) // 2
    y0 = 200
    for i, (num, title, sub) in enumerate(steps):
        c, r = i % 2, i // 2
        x = x0 + c * (card_w + gap_x)
        y = y0 + r * (card_h + gap_y)
        d.rounded_rectangle([x, y, x + card_w, y + card_h], radius=14, fill=(255, 253, 249), outline=bronze, width=2)
        d.ellipse([x + 40, y + 50, x + 130, y + 140], outline=bronze, width=3)
        d.text((x + 85, y + 95), num, font=_f("display", 36), fill=bronze, anchor="mm")
        d.text((x + 170, y + 75), title, font=_f("display", 32), fill=charcoal, anchor="lt")
        d.text((x + 170, y + 140), sub, font=_f("serif", 26), fill=muted, anchor="lt")
    # footer strip with real page strip
    strip_y = 1180
    d.text((S // 2, strip_y), "Includes categorized pages like this", font=_f("sans", 20), fill=muted, anchor="mt")
    thumbs = [banking, change, howto]
    tw = 280
    total_w = len(thumbs) * tw + (len(thumbs) - 1) * 24
    tx0 = (S - total_w) // 2
    for i, pg0 in enumerate(thumbs):
        th = _fit_page(pg0, max_h=420, max_w=tw)
        x = tx0 + i * (tw + 24) + (tw - th.width) // 2
        y = strip_y + 50
        img = _drop_shadow(img, th, (x, y), blur=10, alpha=70)
        d = ImageDraw.Draw(img)
    p = PREVIEWS / "pt_preview_5_how.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # ── 6 VALUE: stats + page collage ───────────────────────────────────────
    img = Image.new("RGB", (S, S), charcoal)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 55), "Everything in one log", font=_f("display", 38), fill=ivory, anchor="mt")
    stats = [("18", "Pages"), ("9+", "Categories"), ("Wi-Fi", "Sheet"), ("2FA", "Fields")]
    for i, (big, lab) in enumerate(stats):
        x = 80 + i * 480
        y = 140
        d.rounded_rectangle([x, y, x + 440, y + 220], radius=12, outline=bronze, width=2)
        d.text((x + 220, y + 70), big, font=_f("display", 42), fill=bronze, anchor="mt")
        d.text((x + 220, y + 145), lab, font=_f("serif", 22), fill=ivory, anchor="mt")
    # bottom: three pages
    trio = [cover, email, wifi]
    gap = 30
    max_h = 1180
    col_w = (S - 2 * 70 - 2 * gap) // 3
    for i, pg0 in enumerate(trio):
        pg = _fit_page(pg0, max_h=max_h, max_w=col_w)
        x = 70 + i * (col_w + gap) + (col_w - pg.width) // 2
        y = 420
        # subtle light mat
        d = ImageDraw.Draw(img)
        d.rectangle([x - 6, y - 6, x + pg.width + 6, y + pg.height + 6], fill=(255, 253, 249))
        img.paste(pg, (x, y))
    p = PREVIEWS / "pt_preview_6_value.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    print(f"  {len(paths)} previews (PDF mockups) → {PREVIEWS}")
    return paths


def build_zip() -> Path:
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(PDF_PATH, "Password_Login_Tracker.pdf")
        z.writestr(
            "READ_ME.txt",
            """Password & Login Tracker
========================

INCLUDED
  Password_Login_Tracker.pdf  — US Letter printable

PRINTING
  · Print at 100% scale
  · Hole-punch for a 3-ring binder, or use sheet protectors
  · Works in GoodNotes / Notability on tablet

PRIVACY
  · For private offline use
  · Do not store a password-manager master password in this book
  · Do not share photos of filled pages

Personal use only. Not for redistribution or resale.
""",
        )
    print("ZIP:", ZIP_PATH, f"({ZIP_PATH.stat().st_size // 1024} KB)")
    return ZIP_PATH


def main():
    print("Building Password & Login Tracker (unbranded, refined)…")
    build_pdf()
    make_previews()
    build_zip()
    # remove old branded filenames if present
    for old in (
        OUT / "MathRelaxing_Password_Login_Tracker.pdf",
        OUT / "MathRelaxing_Password_Login_Tracker.zip",
    ):
        if old.exists():
            old.unlink()
            print("removed", old.name)
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
