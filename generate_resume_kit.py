"""
generate_resume_kit.py — MathRelaxing Editorial Resume Kit
==========================================================
Lethal Etsy resume pack: ATS-safe Word templates + Editorial STEM aesthetic,
cover letter, references, filled PDF samples, listing mockups.

Positioning (from eRank SERP research):
  - Winners: ATS + Word/Google Docs + cover letter + references · $8–12
  - Differentiator: MathRelaxing editorial palette (navy / gold / cream)
    aimed at engineers, scientists, analysts — not floral Canva clutter.

  python generate_resume_kit.py
"""
from __future__ import annotations

import os
import zipfile
from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "resume_kit")
TEMPLATES = os.path.join(OUT, "templates")
SAMPLES = os.path.join(OUT, "samples")
PREVIEWS = os.path.join(OUT, "previews")
BACKGROUNDS = os.path.join(OUT, "backgrounds")

# MathRelaxing brand
NAVY = "#12172D"
GOLD = "#C9A24B"
CREAM = "#F8F4EB"
INK = "#1A1A1A"
SOFT = "#555555"
FAINT = "#8A857C"
SLATE = "#3D5A80"
TEAL = "#2F6F6A"

# Sample persona — STEM professional (fills templates + mockups)
PERSONA = {
    "name": "ALEX RIVERA",
    "title": "Data Scientist  ·  Applied Mathematics",
    "contact": "alex.rivera@email.com  ·  (555) 014-2088  ·  San Francisco, CA  ·  linkedin.com/in/alexrivera",
    "summary": (
        "Data scientist with 6+ years translating statistical models into product decisions. "
        "Strong in causal inference, experimentation, and production ML. Known for clear "
        "communication with engineering and leadership — turning ambiguous questions into "
        "measurable outcomes."
    ),
    "skills": (
        "Python · SQL · R · PyTorch · scikit-learn · dbt · Airflow · A/B testing · "
        "Causal inference · Bayesian modeling · Experiment design · Stakeholder storytelling"
    ),
    "experience": [
        {
            "role": "Senior Data Scientist",
            "co": "Northline Analytics  ·  San Francisco, CA",
            "dates": "2021 – Present",
            "bullets": [
                "Owned experimentation platform serving 40+ product squads; cut time-to-insight by 35%.",
                "Shipped propensity models that lifted paid conversion +12% ($4.2M incremental ARR).",
                "Mentored 4 junior scientists; established model-review checklist adopted org-wide.",
            ],
        },
        {
            "role": "Data Scientist",
            "co": "Helix Health  ·  Remote",
            "dates": "2018 – 2021",
            "bullets": [
                "Built risk-stratification models for 1.2M patient records; reduced false positives 18%.",
                "Partnered with clinical ops to redesign dashboards used daily by 200+ care managers.",
                "Published internal white paper on uplift modeling for care outreach programs.",
            ],
        },
        {
            "role": "Research Analyst",
            "co": "University Lab for Computational Social Science",
            "dates": "2016 – 2018",
            "bullets": [
                "Analyzed large-scale survey panels with hierarchical Bayesian models in R and Stan.",
                "Co-authored peer-reviewed paper on network effects in online learning platforms.",
            ],
        },
    ],
    "education": [
        {
            "deg": "M.S. Statistics",
            "school": "University of California  ·  GPA 3.9",
            "dates": "2016",
        },
        {
            "deg": "B.S. Applied Mathematics",
            "school": "Georgia Institute of Technology  ·  Magna Cum Laude",
            "dates": "2014",
        },
    ],
    "projects": [
        "Open-source contribution: experimental design utilities for Python (1.8k GitHub stars).",
        "Invited talk: “Causal Inference in Product Analytics,” Data Council 2024.",
    ],
}


def _ensure_dirs():
    for d in (OUT, TEMPLATES, SAMPLES, PREVIEWS, BACKGROUNDS):
        os.makedirs(d, exist_ok=True)


def _set_page_background(doc: Document, hex_color: str = "F8F4EB"):
    """Solid page wash (cream) — visible in Word Print Layout / PDF."""
    bg = OxmlElement("w:background")
    bg.set(qn("w:color"), hex_color.lstrip("#"))
    doc.element.insert(0, bg)
    # enable background display/print
    settings = doc.settings.element
    disp = OxmlElement("w:displayBackgroundShape")
    settings.append(disp)


def _add_behind_picture(paragraph, image_path: str, width_in: float = 8.5, height_in: float = 11.0):
    """
    Insert a floating picture BEHIND text, anchored to the page (watermark).
    Image should already be semi-transparent PNG.
    """
    run = paragraph.add_run()
    # create relationship via inline picture first
    inline_shape = run.add_picture(image_path, width=Inches(width_in), height=Inches(height_in))
    inline = inline_shape._inline
    # dimensions already set on inline
    extent = inline.extent
    cx = extent.cx
    cy = extent.cy
    docPr = inline.docPr
    docPr_id = docPr.get("id") or "1"
    docPr_name = docPr.get("name") or "Background"
    # graphic data
    graphic = inline.graphic
    # Build anchor (behind text)
    anchor_xml = f"""
    <wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
               xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
               xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
               xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
               distT="0" distB="0" distL="0" distR="0"
               simplePos="0" relativeHeight="0" behindDoc="1" locked="0"
               layoutInCell="1" allowOverlap="1">
      <wp:simplePos x="0" y="0"/>
      <wp:positionH relativeFrom="page">
        <wp:posOffset>0</wp:posOffset>
      </wp:positionH>
      <wp:positionV relativeFrom="page">
        <wp:posOffset>0</wp:posOffset>
      </wp:positionV>
      <wp:extent cx="{cx}" cy="{cy}"/>
      <wp:effectExtent l="0" t="0" r="0" b="0"/>
      <wp:wrapNone/>
      <wp:docPr id="{docPr_id}" name="{docPr_name}"/>
      <wp:cNvGraphicFramePr>
        <a:graphicFrameLocks noChangeAspect="1"/>
      </wp:cNvGraphicFramePr>
    </wp:anchor>
    """
    # parse and attach existing graphic to new anchor
    from docx.oxml import parse_xml

    anchor = parse_xml(anchor_xml)
    anchor.append(graphic)
    # replace drawing content
    drawing = inline.getparent()
    drawing.remove(inline)
    drawing.append(anchor)


def _apply_editorial_background(doc: Document, watermark_path: str | None):
    """Cream page + optional semi-transparent full-page watermark behind text."""
    _set_page_background(doc, "F8F4EB")
    if not watermark_path or not os.path.isfile(watermark_path):
        return
    section = doc.sections[0]
    header = section.header
    # clear default empty para content carefully
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p.clear()
    try:
        _add_behind_picture(p, watermark_path, width_in=8.5, height_in=11.0)
    except Exception as e:
        print(f"  watermark skip ({e})")
        # fallback: light inline header image (still decorative)
        try:
            p = header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(watermark_path, width=Inches(7.5))
        except Exception as e2:
            print(f"  watermark fallback failed ({e2})")


def _hex_rgb(color: str) -> RGBColor:
    h = color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _set_run_font(run, name="Calibri", size=11, bold=False, color=None, all_caps=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = _hex_rgb(color)
    if all_caps:
        run.font.all_caps = True


def _set_paragraph_spacing(p, before=0, after=6, line=1.08):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def _add_bottom_border(paragraph, color="12172D", sz=12):
    """Add a bottom border to a paragraph (section rule)."""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _section_header(doc, text, color="12172D"):
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=12, after=4, line=1.0)
    run = p.add_run(text.upper())
    _set_run_font(run, "Calibri", 10, bold=True, color=color, all_caps=True)
    _add_bottom_border(p, color=color.lstrip("#") if color.startswith("#") else color, sz=10)
    return p


def _bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.clear()
    run = p.add_run(text)
    _set_run_font(run, "Calibri", size, color=INK)
    _set_paragraph_spacing(p, before=1, after=2, line=1.08)
    return p


def build_ats_resume(path: str, filled: bool = True):
    """Single-column ATS-safe resume (Calibri, no tables, no text boxes)."""
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    P = PERSONA if filled else {
        "name": "YOUR FULL NAME",
        "title": "Target Role  ·  Specialty",
        "contact": "email@domain.com  ·  (555) 000-0000  ·  City, ST  ·  linkedin.com/in/you",
        "summary": (
            "[2–3 sentences: years of experience, domain, signature strength, and the "
            "value you create. Use numbers wherever possible.]"
        ),
        "skills": "Skill One · Skill Two · Skill Three · Tool · Method · Domain expertise",
        "experience": [
            {
                "role": "Job Title",
                "co": "Company Name  ·  City, ST",
                "dates": "YYYY – Present",
                "bullets": [
                    "Achievement with metric (e.g., +X% / $Y / N users).",
                    "Ownership statement: what you built, led, or improved.",
                    "Cross-functional impact with a concrete outcome.",
                ],
            },
            {
                "role": "Previous Title",
                "co": "Company Name  ·  City, ST",
                "dates": "YYYY – YYYY",
                "bullets": [
                    "Second role achievement with measurable result.",
                    "Technical or leadership highlight.",
                ],
            },
        ],
        "education": [
            {"deg": "Degree, Field", "school": "University Name", "dates": "YYYY"},
        ],
        "projects": [
            "Selected project or publication with one-line impact.",
        ],
    }

    # Name
    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(name, before=0, after=2, line=1.0)
    r = name.add_run(P["name"])
    _set_run_font(r, "Calibri", 20, bold=True, color=INK)

    # Subtitle
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(sub, before=0, after=2, line=1.0)
    r = sub.add_run(P["title"])
    _set_run_font(r, "Calibri", 10.5, color=SOFT)

    # Contact
    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(con, before=0, after=8, line=1.0)
    r = con.add_run(P["contact"])
    _set_run_font(r, "Calibri", 9.5, color=SOFT)

    # Summary
    _section_header(doc, "Professional Summary")
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=4, after=4)
    r = p.add_run(P["summary"])
    _set_run_font(r, "Calibri", 10.5, color=INK)

    # Skills
    _section_header(doc, "Core Skills")
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=4, after=4)
    r = p.add_run(P["skills"])
    _set_run_font(r, "Calibri", 10.5, color=INK)

    # Experience
    _section_header(doc, "Experience")
    for job in P["experience"]:
        head = doc.add_paragraph()
        _set_paragraph_spacing(head, before=8, after=0, line=1.0)
        r = head.add_run(job["role"])
        _set_run_font(r, "Calibri", 11, bold=True, color=INK)
        # dates right-ish via tab
        r = head.add_run("\t" + job["dates"])
        _set_run_font(r, "Calibri", 10, color=SOFT)
        # set right tab
        tab_stops = head.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Inches(7.0), alignment=2)  # right

        co = doc.add_paragraph()
        _set_paragraph_spacing(co, before=0, after=2, line=1.0)
        r = co.add_run(job["co"])
        _set_run_font(r, "Calibri", 10, color=SOFT)

        for b in job["bullets"]:
            _bullet(doc, b)

    # Education
    _section_header(doc, "Education")
    for ed in P["education"]:
        head = doc.add_paragraph()
        _set_paragraph_spacing(head, before=6, after=0, line=1.0)
        r = head.add_run(ed["deg"])
        _set_run_font(r, "Calibri", 11, bold=True, color=INK)
        r = head.add_run("\t" + ed["dates"])
        _set_run_font(r, "Calibri", 10, color=SOFT)
        head.paragraph_format.tab_stops.add_tab_stop(Inches(7.0), alignment=2)
        sch = doc.add_paragraph()
        _set_paragraph_spacing(sch, before=0, after=2)
        r = sch.add_run(ed["school"])
        _set_run_font(r, "Calibri", 10, color=SOFT)

    # Selected work
    _section_header(doc, "Selected Work")
    for proj in P["projects"]:
        _bullet(doc, proj)

    doc.save(path)
    print(f"  wrote {path}")


def build_editorial_resume(path: str, filled: bool = True, watermark_path: str | None = None):
    """
    Editorial MathRelaxing variant: single-column, cream page wash,
    optional semi-transparent background style (behind text), navy + gold rules.
    """
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Cream page + optional decorative watermark (NOT on ATS templates)
    _apply_editorial_background(doc, watermark_path)

    P = PERSONA if filled else {
        "name": "YOUR FULL NAME",
        "title": "Target Role  ·  Specialty",
        "contact": "email@domain.com  ·  (555) 000-0000  ·  City, ST  ·  linkedin.com/in/you",
        "summary": "[Editorial summary — precise, calm, numbers-forward.]",
        "skills": "Skill · Skill · Skill · Method · Stack",
        "experience": [
            {
                "role": "Job Title",
                "co": "Company  ·  Location",
                "dates": "YYYY – Present",
                "bullets": [
                    "Impact bullet with metric.",
                    "Ownership and scope.",
                ],
            }
        ],
        "education": [{"deg": "Degree", "school": "School", "dates": "YYYY"}],
        "projects": ["Selected work highlight."],
    }

    # Name — refined Georgia
    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(name, before=6, after=4, line=1.0)
    r = name.add_run(P["name"])
    _set_run_font(r, "Georgia", 24, bold=True, color=NAVY)

    # Dual elegance: gold dots + thin navy rule
    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(rule, before=0, after=2, line=1.0)
    r = rule.add_run("·   ·   ·")
    _set_run_font(r, "Georgia", 9, color=GOLD)

    hair = doc.add_paragraph()
    hair.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(hair, before=0, after=8, line=1.0)
    _add_bottom_border(hair, color="C9A24B", sz=6)
    r = hair.add_run(" ")
    _set_run_font(r, "Georgia", 4, color=GOLD)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(sub, before=2, after=2)
    r = sub.add_run(P["title"])
    _set_run_font(r, "Georgia", 11, color=GOLD)

    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(con, before=0, after=14)
    r = con.add_run(P["contact"])
    _set_run_font(r, "Calibri", 9, color=SOFT)

    def e_section(text):
        p = doc.add_paragraph()
        _set_paragraph_spacing(p, before=14, after=5, line=1.0)
        run = p.add_run(text.upper())
        _set_run_font(run, "Georgia", 9.5, bold=True, color=NAVY, all_caps=True)
        _add_bottom_border(p, color="C9A24B", sz=10)

    e_section("Professional Summary")
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=6, after=6, line=1.15)
    r = p.add_run(P["summary"])
    _set_run_font(r, "Calibri", 10.5, color=INK)

    e_section("Core Skills")
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=6, after=6, line=1.15)
    r = p.add_run(P["skills"])
    _set_run_font(r, "Calibri", 10.5, color=INK)

    e_section("Experience")
    for job in P["experience"]:
        head = doc.add_paragraph()
        _set_paragraph_spacing(head, before=10, after=0)
        r = head.add_run(job["role"])
        _set_run_font(r, "Georgia", 11, bold=True, color=NAVY)
        r = head.add_run("\t" + job["dates"])
        _set_run_font(r, "Calibri", 10, color=SOFT)
        head.paragraph_format.tab_stops.add_tab_stop(Inches(6.7), alignment=2)
        co = doc.add_paragraph()
        _set_paragraph_spacing(co, before=1, after=3)
        r = co.add_run(job["co"])
        _set_run_font(r, "Calibri", 10, color=TEAL)
        for b in job["bullets"]:
            _bullet(doc, b, size=10.5)

    e_section("Education")
    for ed in P["education"]:
        head = doc.add_paragraph()
        _set_paragraph_spacing(head, before=8, after=0)
        r = head.add_run(ed["deg"])
        _set_run_font(r, "Georgia", 11, bold=True, color=NAVY)
        r = head.add_run("\t" + ed["dates"])
        _set_run_font(r, "Calibri", 10, color=SOFT)
        head.paragraph_format.tab_stops.add_tab_stop(Inches(6.7), alignment=2)
        sch = doc.add_paragraph()
        _set_paragraph_spacing(sch, before=1, after=3)
        r = sch.add_run(ed["school"])
        _set_run_font(r, "Calibri", 10, color=SOFT)

    e_section("Selected Work")
    for proj in P["projects"]:
        _bullet(doc, proj, size=10.5)

    # Footer line
    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(foot, before=18, after=0)
    r = foot.add_run("·  MathRelaxing Editorial  ·")
    _set_run_font(r, "Georgia", 8, color=FAINT)

    doc.save(path)
    print(f"  wrote {path}")


def build_cover_letter(path: str, filled: bool = True, watermark_path: str | None = None):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    if watermark_path:
        _apply_editorial_background(doc, watermark_path)
    else:
        _set_page_background(doc, "F8F4EB")

    if filled:
        header_lines = [
            ("ALEX RIVERA", True, 14, NAVY),
            (PERSONA["contact"], False, 9, SOFT),
        ]
        body = [
            "Hiring Manager",
            "Company Name",
            "",
            "Dear Hiring Manager,",
            "",
            (
                "I’m applying for the Data Scientist role. Over the last six years I’ve designed "
                "experiments, shipped production models, and partnered with product teams to turn "
                "ambiguous questions into decisions — most recently lifting paid conversion 12% "
                "through propensity modeling at Northline Analytics."
            ),
            "",
            (
                "What I offer is a rare mix of statistical rigor and product empathy: I write code "
                "that ships, explain uncertainty without the jargon, and care as much about "
                "adoption as about AUC. I’d welcome the chance to discuss how that approach could "
                "support your team’s roadmap."
            ),
            "",
            "Thank you for your time and consideration.",
            "",
            "Sincerely,",
            "Alex Rivera",
        ]
    else:
        header_lines = [
            ("YOUR FULL NAME", True, 14, NAVY),
            ("email@domain.com  ·  phone  ·  city  ·  linkedin", False, 9, SOFT),
        ]
        body = [
            "Hiring Manager Name",
            "Company Name",
            "",
            "Dear [Hiring Manager],",
            "",
            (
                "[Opening: role + one signature achievement with a number. Show you researched "
                "the company in one short clause.]"
            ),
            "",
            (
                "[Middle: 2–3 proof points mapped to the job description. Prefer outcomes over "
                "duties. Keep paragraphs short.]"
            ),
            "",
            (
                "[Close: clear ask for a conversation + gratitude. No clichés.]"
            ),
            "",
            "Sincerely,",
            "Your Name",
        ]

    for text, bold, size, color in header_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_paragraph_spacing(p, before=0, after=2)
        r = p.add_run(text)
        _set_run_font(r, "Georgia" if bold else "Calibri", size, bold=bold, color=color)

    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(rule, before=2, after=14)
    r = rule.add_run("·  ·  ·")
    _set_run_font(r, "Georgia", 8, color=GOLD)

    for line in body:
        p = doc.add_paragraph()
        _set_paragraph_spacing(p, before=0, after=6 if line else 4)
        r = p.add_run(line)
        _set_run_font(r, "Calibri", 11, color=INK)

    doc.save(path)
    print(f"  wrote {path}")


def build_references(path: str, filled: bool = True, watermark_path: str | None = None):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    if watermark_path:
        _apply_editorial_background(doc, watermark_path)
    else:
        _set_page_background(doc, "F8F4EB")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(title, before=0, after=4)
    r = title.add_run("REFERENCES" if not filled else f"{PERSONA['name']}  ·  REFERENCES")
    _set_run_font(r, "Georgia", 14, bold=True, color=NAVY)

    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(rule, before=0, after=16)
    r = rule.add_run("Available upon request" if not filled else "Professional references")
    _set_run_font(r, "Calibri", 10, color=GOLD)

    refs = (
        [
            ("Dr. Jordan Lee", "Director of Data Science, Northline Analytics", "jordan.lee@email.com  ·  (555) 010-4411"),
            ("Sam Okonkwo", "VP Product, Helix Health", "sam.okonkwo@email.com  ·  (555) 010-8822"),
            ("Prof. Mira Chen", "Statistics, University of California", "mira.chen@university.edu  ·  (555) 010-3399"),
        ]
        if filled
        else [
            ("Reference Name", "Title, Company", "email  ·  phone"),
            ("Reference Name", "Title, Company", "email  ·  phone"),
            ("Reference Name", "Title, Company", "email  ·  phone"),
        ]
    )
    for name, role, contact in refs:
        p = doc.add_paragraph()
        _set_paragraph_spacing(p, before=10, after=0)
        r = p.add_run(name)
        _set_run_font(r, "Georgia", 12, bold=True, color=NAVY)
        p2 = doc.add_paragraph()
        _set_paragraph_spacing(p2, before=2, after=0)
        r = p2.add_run(role)
        _set_run_font(r, "Calibri", 10.5, color=INK)
        p3 = doc.add_paragraph()
        _set_paragraph_spacing(p3, before=1, after=6)
        r = p3.add_run(contact)
        _set_run_font(r, "Calibri", 10, color=SOFT)

    doc.save(path)
    print(f"  wrote {path}")


# ── PDF samples (filled) for buyers who want a polished PDF + mockups ─────────

def _pdf_colors():
    return HexColor(NAVY), HexColor(GOLD), HexColor(INK), HexColor(SOFT), HexColor(TEAL), HexColor(CREAM)


def build_sample_pdf_editorial(path: str):
    navy, gold, ink, soft, teal, cream = _pdf_colors()
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    styles = {
        "name": ParagraphStyle("name", fontName="Times-Bold", fontSize=20, textColor=navy, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle("sub", fontName="Times-Roman", fontSize=10, textColor=gold, alignment=1, spaceAfter=2),
        "con": ParagraphStyle("con", fontName="Helvetica", fontSize=8.5, textColor=soft, alignment=1, spaceAfter=10),
        "h": ParagraphStyle("h", fontName="Times-Bold", fontSize=9, textColor=navy, spaceBefore=11, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, textColor=ink, leading=12, spaceAfter=4),
        "role": ParagraphStyle("role", fontName="Times-Bold", fontSize=10.5, textColor=navy, spaceBefore=7, spaceAfter=0),
        "co": ParagraphStyle("co", fontName="Helvetica", fontSize=9, textColor=teal, spaceAfter=2),
        "b": ParagraphStyle("b", fontName="Helvetica", fontSize=9.5, textColor=ink, leading=12, leftIndent=8),
    }
    story = []
    story.append(Paragraph(PERSONA["name"], styles["name"]))
    story.append(Paragraph("·  ·  ·", ParagraphStyle("dots", fontName="Times-Roman", fontSize=8, textColor=gold, alignment=1)))
    story.append(Paragraph(PERSONA["title"], styles["sub"]))
    story.append(Paragraph(PERSONA["contact"].replace("  ·  ", " · "), styles["con"]))
    story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=6))

    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["h"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceAfter=4))
    story.append(Paragraph(PERSONA["summary"], styles["body"]))

    story.append(Paragraph("CORE SKILLS", styles["h"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceAfter=4))
    story.append(Paragraph(PERSONA["skills"], styles["body"]))

    story.append(Paragraph("EXPERIENCE", styles["h"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceAfter=2))
    for job in PERSONA["experience"]:
        story.append(Paragraph(f"{job['role']} <font color='#8A857C'>&nbsp;&nbsp;{job['dates']}</font>", styles["role"]))
        story.append(Paragraph(job["co"], styles["co"]))
        for b in job["bullets"]:
            story.append(Paragraph(f"• {b}", styles["b"]))

    story.append(Paragraph("EDUCATION", styles["h"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceAfter=2))
    for ed in PERSONA["education"]:
        story.append(Paragraph(f"{ed['deg']} <font color='#8A857C'>&nbsp;&nbsp;{ed['dates']}</font>", styles["role"]))
        story.append(Paragraph(ed["school"], styles["co"]))

    story.append(Paragraph("SELECTED WORK", styles["h"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceAfter=2))
    for proj in PERSONA["projects"]:
        story.append(Paragraph(f"• {proj}", styles["b"]))

    doc.build(story)
    print(f"  wrote {path}")


def build_howto_pdf(path: str):
    navy, gold, ink, soft, _, _ = _pdf_colors()
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
    )
    h = ParagraphStyle("h", fontName="Times-Bold", fontSize=16, textColor=navy, spaceAfter=6, alignment=1)
    sh = ParagraphStyle("sh", fontName="Times-Bold", fontSize=11, textColor=gold, spaceBefore=14, spaceAfter=6)
    b = ParagraphStyle("b", fontName="Helvetica", fontSize=10, textColor=ink, leading=14, spaceAfter=6)
    story = [
        Paragraph("MathRelaxing Editorial Resume Kit", h),
        Paragraph("How to use your templates", ParagraphStyle("s", fontName="Helvetica", fontSize=10, textColor=soft, alignment=1, spaceAfter=16)),
        Paragraph("What’s included", sh),
        Paragraph(
            "• <b>01_ATS_Resume_Template.docx</b> — pure white, portal-safe (no background)<br/>"
            "• <b>02_Editorial_*.docx</b> — five elegant background styles (cream page + semi-transparent art)<br/>"
            "• Cover letter + references matching the default editorial style<br/>"
            "• Filled STEM samples + Sample PDF<br/>"
            "• <b>backgrounds/</b> folder — PNG style pack to swap or recolor yourself",
            b,
        ),
        Paragraph("Background styles (Editorial)", sh),
        Paragraph(
            "Each Editorial resume already embeds one semi-transparent background behind the text:<br/>"
            "1. Cream Veil · 2. Scientific Grid · 3. Gold Geometry · 4. Phi Whisper · 5. Navy Edge<br/><br/>"
            "To change style: open the matching <b>02_Editorial_Style_*.docx</b>, or in Word:<br/>"
            "Header → select the background image → Replace Picture → pick another file from <b>backgrounds/</b>. "
            "Keep “Behind Text” wrap so type stays readable.",
            b,
        ),
        Paragraph("Microsoft Word", sh),
        Paragraph("Open any .docx → replace text → File → Save as PDF. Prefer Georgia/Calibri as shipped.", b),
        Paragraph("Google Docs (free)", sh),
        Paragraph(
            "1. Upload .docx to Drive → Open with Google Docs<br/>"
            "2. Note: Docs may flatten fancy backgrounds; for full elegance export PDF from Word/Pages first.",
            b,
        ),
        Paragraph("ATS tip", sh),
        Paragraph(
            "Use the <b>ATS</b> template for company portals (no watermark). "
            "Use an <b>Editorial</b> style when emailing a hiring manager or sharing a portfolio PDF.",
            b,
        ),
        Paragraph("License", sh),
        Paragraph("© MathRelaxing. Personal use only. Not for resale or redistribution of the templates themselves.", b),
    ]
    doc.build(story)
    print(f"  wrote {path}")


# ── Listing mockups ──────────────────────────────────────────────────────────

def _font(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\\Windows")
    names = ["georgiab.ttf", "timesbd.ttf"] if bold else ["georgia.ttf", "times.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _font_sans(size, bold=False):
    windir = os.environ.get("WINDIR", r"C:\\Windows")
    names = ["arialbd.ttf", "calibrib.ttf"] if bold else ["arial.ttf", "calibri.ttf"]
    for n in names:
        p = os.path.join(windir, "Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _render_resume_card(w=620, h=800, editorial=True, bg_path: str | None = None) -> Image.Image:
    """Raster mini-resume for mockups (optional semi-transparent bg overlay)."""
    bg = CREAM if editorial else "#FFFFFF"
    img = Image.new("RGB", (w, h), bg)
    if editorial and bg_path and os.path.isfile(bg_path):
        try:
            overlay = Image.open(bg_path).convert("RGBA")
            overlay = overlay.resize((w, h), Image.Resampling.LANCZOS)
            base = Image.new("RGBA", (w, h), (*Image.new("RGB", (1, 1), bg).getpixel((0, 0)), 255))
            base = Image.alpha_composite(base, overlay)
            img = base.convert("RGB")
        except Exception:
            pass
    d = ImageDraw.Draw(img)
    accent = GOLD if editorial else SLATE
    title_c = NAVY if editorial else INK
    d.rectangle([0, 0, w - 1, h - 1], outline="#E0DCD2", width=2)

    y = 28
    d.text((w // 2, y), PERSONA["name"], font=_font(28, True), fill=title_c, anchor="mt")
    y += 36
    if editorial:
        d.text((w // 2, y), "·  ·  ·", font=_font(12), fill=GOLD, anchor="mt")
        y += 18
    d.text((w // 2, y), "Data Scientist  ·  Applied Mathematics", font=_font_sans(13), fill=accent, anchor="mt")
    y += 22
    d.text((w // 2, y), "alex.rivera@email.com  ·  San Francisco, CA", font=_font_sans(11), fill=SOFT, anchor="mt")
    y += 28
    d.line([(40, y), (w - 40, y)], fill=accent, width=2)
    y += 18

    def section(label):
        nonlocal y
        d.text((40, y), label.upper(), font=_font_sans(12, True), fill=title_c)
        y += 16
        d.line([(40, y), (w - 40, y)], fill=accent if editorial else "#CCCCCC", width=1)
        y += 10

    def body(text, max_w=w - 80):
        nonlocal y
        # simple wrap
        words = text.split()
        line = ""
        font = _font_sans(12)
        for word in words:
            test = (line + " " + word).strip()
            if d.textlength(test, font=font) > max_w:
                d.text((40, y), line, font=font, fill=INK)
                y += 16
                line = word
            else:
                line = test
        if line:
            d.text((40, y), line, font=font, fill=INK)
            y += 18

    section("Professional Summary")
    body(PERSONA["summary"][:220] + "…")
    y += 6
    section("Core Skills")
    body("Python · SQL · PyTorch · A/B testing · Causal inference · Experiment design")
    y += 6
    section("Experience")
    d.text((40, y), "Senior Data Scientist", font=_font_sans(13, True), fill=title_c)
    d.text((w - 40, y), "2021 – Present", font=_font_sans(11), fill=SOFT, anchor="rt")
    y += 18
    d.text((40, y), "Northline Analytics", font=_font_sans(12), fill=TEAL if editorial else SOFT)
    y += 18
    for b in PERSONA["experience"][0]["bullets"][:2]:
        body("• " + b)
        y += 2
    return img


def build_previews():
    os.makedirs(PREVIEWS, exist_ok=True)
    bg = _PREVIEW_BG or os.path.join(BACKGROUNDS, "bg_gold_geometry.png")
    card_ed = _render_resume_card(editorial=True, bg_path=bg)
    card_ats = _render_resume_card(editorial=False)

    # Extra preview: all 5 background styles side by side
    sheet_src = os.path.join(BACKGROUNDS, "_styles_contact_sheet.jpg")
    if os.path.isfile(sheet_src):
        import shutil as _sh

        _sh.copy(sheet_src, os.path.join(PREVIEWS, "resume_preview_6_backgrounds.jpg"))
        print("  wrote backgrounds preview")

    # 1 Hero
    side = 1400
    hero = Image.new("RGB", (side, side), (18, 23, 46))
    c = card_ed.copy()
    c.thumbnail((int(side * 0.52), int(side * 0.70)), Image.Resampling.LANCZOS)
    hero.paste(c, ((side - c.width) // 2, int(side * 0.08)))
    d = ImageDraw.Draw(hero)
    d.rectangle([0, int(side * 0.82), side, side], fill=(18, 23, 46))
    d.text((side // 2, int(side * 0.86)), "Editorial Resume Kit", font=_font(42, True), fill=CREAM, anchor="mt")
    d.text(
        (side // 2, int(side * 0.92)),
        "ATS + navy/gold templates  ·  cover letter  ·  references",
        font=_font_sans(18),
        fill=GOLD,
        anchor="mt",
    )
    # badge
    d.ellipse([side - 220, 40, side - 40, 220], fill=NAVY, outline=GOLD, width=3)
    d.text((side - 130, 110), "ATS", font=_font(22, True), fill=CREAM, anchor="mm")
    d.text((side - 130, 140), "friendly", font=_font_sans(14), fill=GOLD, anchor="mm")
    hero.save(os.path.join(PREVIEWS, "resume_preview_1_hero.jpg"), quality=92)
    print("  wrote hero")

    # 2 Side by side
    pair = Image.new("RGB", (1400, 900), CREAM)
    d = ImageDraw.Draw(pair)
    d.text((70, 40), "two styles included", font=_font(32, True), fill=NAVY)
    d.text((70, 90), "ATS Clean  ·  Editorial MathRelaxing", font=_font_sans(18), fill=SOFT)
    a = card_ats.copy()
    e = card_ed.copy()
    a.thumbnail((520, 680), Image.Resampling.LANCZOS)
    e.thumbnail((520, 680), Image.Resampling.LANCZOS)
    pair.paste(a, (80, 150))
    pair.paste(e, (760, 150))
    d.text((80 + a.width // 2, 150 + a.height + 20), "ATS Clean", font=_font_sans(16, True), fill=INK, anchor="mt")
    d.text((760 + e.width // 2, 150 + e.height + 20), "Editorial", font=_font_sans(16, True), fill=NAVY, anchor="mt")
    pair.save(os.path.join(PREVIEWS, "resume_preview_2_styles.jpg"), quality=92)
    print("  wrote styles")

    # 3 Included
    inc = Image.new("RGB", (1200, 900), (18, 23, 46))
    d = ImageDraw.Draw(inc)
    d.text((60, 50), "what's inside", font=_font(36, True), fill=CREAM)
    items = [
        "01  ATS Resume Template (.docx)",
        "02  Editorial Resume Template (.docx)",
        "03  Cover Letter Template (.docx)",
        "04  References Template (.docx)",
        "05  Filled sample PDFs",
        "06  How-to guide (Word · Google Docs · Pages)",
    ]
    y = 140
    for it in items:
        d.rounded_rectangle([60, y, 1140, y + 80], radius=12, fill=(28, 34, 60), outline=GOLD)
        d.text((90, y + 40), it, font=_font_sans(22), fill=CREAM, anchor="lm")
        y += 100
    inc.save(os.path.join(PREVIEWS, "resume_preview_3_included.jpg"), quality=92)
    print("  wrote included")

    # 4 Full plate-like detail
    detail = Image.new("RGB", (1000, 1300), (40, 44, 55))
    # "desk" feel
    paper = card_ed.copy().resize((780, 1000), Image.Resampling.LANCZOS)
    detail.paste(paper, (110, 100))
    d = ImageDraw.Draw(detail)
    d.ellipse([780, 80, 960, 260], fill=NAVY, outline=GOLD, width=3)
    d.text((870, 150), "ATS", font=_font(24, True), fill=CREAM, anchor="mm")
    d.text((870, 185), "ready", font=_font_sans(14), fill=GOLD, anchor="mm")
    detail.save(os.path.join(PREVIEWS, "resume_preview_4_detail.jpg"), quality=92)
    print("  wrote detail")

    # 5 Features strip
    feat = Image.new("RGB", (1200, 700), CREAM)
    d = ImageDraw.Draw(feat)
    d.text((60, 40), "built for serious applications", font=_font(30, True), fill=NAVY)
    features = [
        ("ATS-safe layout", "Single column · no tables · portal-ready"),
        ("Editorial twin", "Navy, gold & cream — MathRelaxing polish"),
        ("Full kit", "Resume + cover letter + references"),
        ("STEM sample", "Data science persona with real metrics"),
    ]
    positions = [(60, 120), (620, 120), (60, 380), (620, 380)]
    for (x, y), (t, s) in zip(positions, features):
        d.rounded_rectangle([x, y, x + 520, y + 200], radius=16, fill="white", outline="#E6E2D8", width=2)
        d.rectangle([x, y, x + 12, y + 200], fill=GOLD)
        d.text((x + 40, y + 50), t, font=_font(22, True), fill=NAVY)
        d.text((x + 40, y + 100), s, font=_font_sans(16), fill=SOFT)
    feat.save(os.path.join(PREVIEWS, "resume_preview_5_features.jpg"), quality=92)
    print("  wrote features")


def build_zip():
    zip_path = os.path.join(OUT, "MathRelaxing_Editorial_Resume_Kit.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            """MathRelaxing Editorial Resume Kit
================================

For engineers, scientists, analysts, and precision professionals.

INCLUDED
--------
templates/
  01_ATS_Resume_Template.docx              pure white, portal-safe
  01_ATS_Resume_SAMPLE.docx
  02_Editorial_Style_CreamVeil.docx        + SAMPLE
  02_Editorial_Style_ScientificGrid.docx   + SAMPLE
  02_Editorial_Style_GoldGeometry.docx     + SAMPLE
  02_Editorial_Style_PhiWhisper.docx       + SAMPLE
  02_Editorial_Style_NavyEdge.docx         + SAMPLE
  03_Cover_Letter_Template.docx / SAMPLE
  04_References_Template.docx / SAMPLE

backgrounds/
  bg_*.png          semi-transparent full-page art (swap freely)
  _styles_contact_sheet.jpg
  BACKGROUNDS_README.txt

samples/
  Sample_Editorial_Resume.pdf
  HOW_TO_USE.pdf

BACKGROUNDS
-----------
Editorial templates embed a faint MathRelaxing background BEHIND the text
(cream page wash + decorative layer). Five styles ship as separate .docx files
so you can pick elegance level without design skills.

To swap: Header → click image → Change Picture → choose another backgrounds/bg_*.png
Wrap should stay Behind Text.

TIP
---
ATS template = company portals (no watermark).
Editorial styles = email / networking / portfolio PDF.

© MathRelaxing — personal use only.
""",
        )
        for folder, arc_prefix in (
            (TEMPLATES, "templates"),
            (SAMPLES, "samples"),
            (BACKGROUNDS, "backgrounds"),
        ):
            if not os.path.isdir(folder):
                continue
            for fn in sorted(os.listdir(folder)):
                full = os.path.join(folder, fn)
                if os.path.isfile(full):
                    zf.write(full, arcname=f"{arc_prefix}/{fn}")
    mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"ZIP: {zip_path} ({mb:.2f} MB)")
    return zip_path


def main():
    print("=== MathRelaxing Editorial Resume Kit ===")
    _ensure_dirs()

    print("backgrounds…")
    sys_path_bg = os.path.join(OUT)
    if sys_path_bg not in os.sys.path:
        os.sys.path.insert(0, sys_path_bg)
    import sys

    if OUT not in sys.path:
        sys.path.insert(0, OUT)
    from _backgrounds_lib import write_all

    bg_paths = write_all(BACKGROUNDS)
    with open(os.path.join(BACKGROUNDS, "BACKGROUNDS_README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Semi-transparent background styles for Editorial resumes\n"
            "========================================================\n\n"
            "These PNGs are already embedded in the matching Editorial .docx files.\n"
            "You can also insert them manually in Word:\n"
            "  Insert → Header → Picture → pick bg_*.png\n"
            "  Picture Format → Wrap Text → Behind Text\n"
            "  Resize to full page (8.5 x 11 in).\n\n"
            "Styles:\n"
            "  cream_veil       soft cream wash + gold vignettes\n"
            "  scientific_grid  whisper graph paper (MathRelaxing signature)\n"
            "  gold_geometry    corner frames + soft circles\n"
            "  phi_whisper      ultra-faint golden spiral\n"
            "  navy_edge        left navy edge + gold hairline\n\n"
            "ATS templates intentionally have NO background.\n"
        )

    # Default elegance: gold geometry for cover/refs samples
    default_bg = bg_paths.get("gold_geometry")

    print("templates…")
    build_ats_resume(os.path.join(TEMPLATES, "01_ATS_Resume_Template.docx"), filled=False)
    build_ats_resume(os.path.join(TEMPLATES, "01_ATS_Resume_SAMPLE.docx"), filled=True)

    style_files = {
        "cream_veil": "CreamVeil",
        "scientific_grid": "ScientificGrid",
        "gold_geometry": "GoldGeometry",
        "phi_whisper": "PhiWhisper",
        "navy_edge": "NavyEdge",
    }
    for key, label in style_files.items():
        wp = bg_paths[key]
        build_editorial_resume(
            os.path.join(TEMPLATES, f"02_Editorial_Style_{label}.docx"),
            filled=False,
            watermark_path=wp,
        )
        build_editorial_resume(
            os.path.join(TEMPLATES, f"02_Editorial_Style_{label}_SAMPLE.docx"),
            filled=True,
            watermark_path=wp,
        )

    # Canonical “default” editorial = Gold Geometry (most elegant)
    build_editorial_resume(
        os.path.join(TEMPLATES, "02_Editorial_Resume_Template.docx"),
        filled=False,
        watermark_path=default_bg,
    )
    build_editorial_resume(
        os.path.join(TEMPLATES, "02_Editorial_Resume_SAMPLE.docx"),
        filled=True,
        watermark_path=default_bg,
    )

    build_cover_letter(os.path.join(TEMPLATES, "03_Cover_Letter_Template.docx"), filled=False, watermark_path=default_bg)
    build_cover_letter(os.path.join(TEMPLATES, "03_Cover_Letter_SAMPLE.docx"), filled=True, watermark_path=default_bg)
    build_references(os.path.join(TEMPLATES, "04_References_Template.docx"), filled=False, watermark_path=default_bg)
    build_references(os.path.join(TEMPLATES, "04_References_SAMPLE.docx"), filled=True, watermark_path=default_bg)

    print("samples…")
    build_sample_pdf_editorial(os.path.join(SAMPLES, "Sample_Editorial_Resume.pdf"))
    build_howto_pdf(os.path.join(SAMPLES, "HOW_TO_USE.pdf"))

    print("previews…")
    # richer mockups with gold_geometry bg
    global _PREVIEW_BG
    _PREVIEW_BG = default_bg
    build_previews()

    print("zip…")
    build_zip()
    print("done.")


# used by build_previews if set
_PREVIEW_BG = None


if __name__ == "__main__":
    main()
