"""
generate_resume_luxe_kit.py — MathRelaxing Atelier Resume Kit (expanded)
========================================================================
Premium kit justified at $12.99+:

  LAYOUTS
    01 Atelier     — letterspaced name, double gold rules, magazine air
    02 Gallery     — left-aligned modern, gold top bar
    03 Manuscript  — literary serif density, classic rules
    04 Architect   — asymmetric header, strong geometry
    05 ATS         — portal-safe single column

  ATELIER STYLES (semi-transparent backgrounds, blank + sample)
    Cream Veil · Scientific Grid · Gold Geometry · Phi Whisper · Navy Edge

  APPLICATION SET
    Cover letter · References · Thank-you note · LinkedIn pack · Portfolio one-pager

  python generate_resume_luxe_kit.py
"""
from __future__ import annotations

import os
import shutil
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

import brand

# reuse editorial background plates
sys.path.insert(0, str(Path(__file__).resolve().parent / "resume_kit"))
from _backgrounds_lib import STYLES as BG_STYLES, write_all as write_backgrounds  # noqa: E402

BASE = Path(__file__).resolve().parent
OUT = BASE / "resume_luxe_kit"
TEMPLATES = OUT / "templates"
SAMPLES = OUT / "samples"
PREVIEWS = OUT / "previews"
BACKGROUNDS = OUT / "backgrounds"
ZIP_PATH = OUT / "MathRelaxing_Atelier_Resume_Kit.zip"

NAVY = "#12172D"
GOLD = "#C9A24B"
CREAM = "#F8F4EB"
INK = "#1A1A1A"
SOFT = "#5C5A56"
FAINT = "#9A958C"
TEAL = "#2F6F6A"

PERSONA = {
    "name": "CELINE MORA",
    "name_spaced": "C E L I N E   M O R A",
    "title": "Applied Research Lead  ·  Product Strategy",
    "contact": "celine.mora@email.com  ·  New York, NY  ·  linkedin.com/in/celinemora",
    "contact_short": "celine.mora@email.com  ·  New York, NY",
    "summary": (
        "Research lead bridging quantitative rigor and product judgment. "
        "Twelve years across labs, startups, and platform teams — designing experiments, "
        "shipping decision systems, and writing clearly for executives who need signal, not slides."
    ),
    "skills_core": "Causal inference  ·  Experimentation  ·  Bayesian modeling  ·  Decision science",
    "skills_tools": "Python  ·  SQL  ·  R  ·  Stan  ·  dbt  ·  Tableau  ·  Looker",
    "skills_lead": "Research ops  ·  Narrative design  ·  Cross-functional leadership  ·  Mentorship",
    "skills_flat": (
        "Causal inference  ·  Experimentation  ·  Bayesian modeling  ·  Python  ·  SQL  ·  R  ·  "
        "Product strategy  ·  Narrative design  ·  Stakeholder leadership"
    ),
    "experience": [
        {
            "role": "Applied Research Lead",
            "co": "Meridian Labs  ·  New York, NY",
            "dates": "2021 – Present",
            "bullets": [
                "Directed a 7-person research pod; roadmap influenced 3 major product bets ($18M ARR).",
                "Rebuilt experimentation governance; reduced underpowered tests by 40% in two quarters.",
                "Established a research writing standard adopted by product, design, and data science.",
            ],
        },
        {
            "role": "Senior Product Analyst",
            "co": "Northline  ·  Remote",
            "dates": "2017 – 2021",
            "bullets": [
                "Owned growth analytics for a 4M-user surface; +9% activation via sequenced onboarding.",
                "Partnered with design systems to quantify component impact (latency vs. conversion).",
                "Mentored analysts; two promoted to senior within 18 months.",
            ],
        },
        {
            "role": "Research Associate",
            "co": "Institute for Decision Science",
            "dates": "2014 – 2017",
            "bullets": [
                "Published peer-reviewed work on multi-armed bandits for adaptive surveys.",
                "Built reproducible analysis pipelines later open-sourced by the lab.",
            ],
        },
    ],
    "education": [
        {"deg": "Ph.D. Cognitive Systems", "school": "Columbia University", "dates": "2014"},
        {"deg": "B.A. Mathematics & Philosophy", "school": "Brown University  ·  Honors", "dates": "2009"},
    ],
    "selected": [
        "Keynote: “Research as Product,” MeasureCamp NY 2024.",
        "Essay series on decision quality — 40k readers, referenced in two industry newsletters.",
    ],
    "certs": [
        "Certified Experimentation Lead — internal Meridian program (2023)",
        "Deep Learning Specialization — Coursera / deeplearning.ai (2019)",
    ],
    "languages": "English (native)  ·  French (professional)  ·  Spanish (conversational)",
    "cover_body": (
        "I am writing to express interest in the Applied Research Lead role. "
        "My work sits at the intersection of rigorous measurement and product craft — "
        "I care as much about the question as the model.\n\n"
        "At Meridian Labs I lead a cross-functional research pod that has shaped multi-million-dollar "
        "roadmap decisions. I would welcome a conversation about how that practice could serve your team."
    ),
    "thankyou": (
        "Thank you for the conversation today — I appreciated the candor about the research roadmap "
        "and the tension between speed and rigor.\n\n"
        "As discussed, I am especially interested in building decision systems that product teams "
        "actually trust. I am happy to share a short case write-up from Meridian if useful.\n\n"
        "Looking forward to next steps."
    ),
    "linkedin_headline": "Applied Research Lead · Experiments, judgment, and clear writing for product teams",
    "linkedin_about": (
        "I lead applied research teams that turn ambiguous product questions into measurable decisions.\n\n"
        "What I do:\n"
        "• Design and govern experimentation programs\n"
        "• Build decision systems product teams will actually use\n"
        "• Write clearly for executives who need signal, not slides\n\n"
        "Background: Ph.D. Cognitive Systems (Columbia). Previously Northline growth analytics "
        "and academic decision science.\n\n"
        "Open to conversations about research leadership, product strategy, and decision quality."
    ),
}


def _ensure():
    for d in (OUT, TEMPLATES, SAMPLES, PREVIEWS, BACKGROUNDS):
        d.mkdir(parents=True, exist_ok=True)


def _hex_rgb(color: str) -> RGBColor:
    h = color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _font_run(run, name="Calibri", size=11, bold=False, color=None, all_caps=False, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = _hex_rgb(color)
    if all_caps:
        run.font.all_caps = True


def _sp(p, before=0, after=6, line=1.12):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def _border_bottom(paragraph, color="C9A24B", sz=8, space=6):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), str(space))
    bottom.set(qn("w:color"), color.lstrip("#"))
    # replace existing bottom
    for child in list(pBdr):
        if child.tag == qn("w:bottom"):
            pBdr.remove(child)
    pBdr.append(bottom)


def _page_bg(doc: Document, hex_color="F8F4EB"):
    bg = OxmlElement("w:background")
    bg.set(qn("w:color"), hex_color.lstrip("#"))
    doc.element.insert(0, bg)
    doc.settings.element.append(OxmlElement("w:displayBackgroundShape"))


def _add_behind_picture(paragraph, image_path: str, width_in=8.5, height_in=11.0):
    run = paragraph.add_run()
    inline_shape = run.add_picture(image_path, width=Inches(width_in), height=Inches(height_in))
    inline = inline_shape._inline
    cx, cy = inline.extent.cx, inline.extent.cy
    docPr = inline.docPr
    docPr_id = docPr.get("id") or "1"
    docPr_name = docPr.get("name") or "Background"
    graphic = inline.graphic
    anchor = parse_xml(
        f"""
    <wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
               xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
               distT="0" distB="0" distL="0" distR="0"
               simplePos="0" relativeHeight="0" behindDoc="1" locked="0"
               layoutInCell="1" allowOverlap="1">
      <wp:simplePos x="0" y="0"/>
      <wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>
      <wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>
      <wp:extent cx="{cx}" cy="{cy}"/>
      <wp:effectExtent l="0" t="0" r="0" b="0"/>
      <wp:wrapNone/>
      <wp:docPr id="{docPr_id}" name="{docPr_name}"/>
      <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
    </wp:anchor>
    """
    )
    anchor.append(graphic)
    drawing = inline.getparent()
    drawing.remove(inline)
    drawing.append(anchor)


def _apply_wm(doc: Document, watermark_path: str | None):
    _page_bg(doc, "F8F4EB")
    if not watermark_path or not os.path.isfile(watermark_path):
        return
    header = doc.sections[0].header
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p.clear()
    try:
        _add_behind_picture(p, watermark_path)
    except Exception as e:
        print(f"  wm skip: {e}")


def _blank():
    return {
        "name": "YOUR FULL NAME",
        "name_spaced": "Y O U R   F U L L   N A M E",
        "title": "Target Role  ·  Focus Area",
        "contact": "email@domain.com  ·  City, ST  ·  linkedin.com/in/you",
        "contact_short": "email@domain.com  ·  City, ST",
        "summary": "[One refined paragraph — judgment, scope, proof.]",
        "skills_core": "Capability  ·  Method  ·  Domain",
        "skills_tools": "Tool  ·  Tool  ·  Tool",
        "skills_lead": "Leadership  ·  Communication  ·  Mentorship",
        "skills_flat": "Capability  ·  Method  ·  Stack  ·  Leadership",
        "experience": [
            {
                "role": "Role Title",
                "co": "Organization  ·  City",
                "dates": "YYYY – Present",
                "bullets": [
                    "Outcome with metric.",
                    "Scope and collaboration.",
                    "Craft or standards you raised.",
                ],
            }
        ],
        "education": [{"deg": "Degree", "school": "School", "dates": "YYYY"}],
        "selected": ["Selected work or talk."],
        "certs": ["Certification or program."],
        "languages": "Language (level)  ·  Language (level)",
        "cover_body": (
            "[Opening — role + why this organization.]\n\n"
            "[Proof — one or two precise outcomes.]\n\n"
            "[Close — invitation to speak.]"
        ),
        "thankyou": (
            "[Thank them for time + one specific discussion point.]\n\n"
            "[Reiterate fit in one sentence.]\n\n"
            "[Offer a next step or artifact.]"
        ),
        "linkedin_headline": "[Role] · [Value proposition in one line]",
        "linkedin_about": "[3–5 short paragraphs: who you help, how, proof, CTA.]",
    }


def _bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.clear()
    r = p.add_run(text)
    _font_run(r, "Calibri", size, color=INK)
    _sp(p, before=1, after=3, line=1.12)


def _job_block(doc, job, tab_in=6.5):
    head = doc.add_paragraph()
    _sp(head, before=11, after=0)
    r = head.add_run(job["role"])
    _font_run(r, "Georgia", 11, bold=True, color=NAVY)
    r = head.add_run("\t" + job["dates"])
    _font_run(r, "Calibri", 9.5, color=SOFT)
    head.paragraph_format.tab_stops.add_tab_stop(Inches(tab_in), alignment=2)
    co = doc.add_paragraph()
    _sp(co, before=1, after=3)
    r = co.add_run(job["co"])
    _font_run(r, "Calibri", 10, italic=True, color=TEAL)
    for b in job["bullets"]:
        _bullet(doc, b)


def _edu_block(doc, ed, tab_in=6.5):
    head = doc.add_paragraph()
    _sp(head, before=8, after=0)
    r = head.add_run(ed["deg"])
    _font_run(r, "Georgia", 11, bold=True, color=NAVY)
    r = head.add_run("\t" + ed["dates"])
    _font_run(r, "Calibri", 9.5, color=SOFT)
    head.paragraph_format.tab_stops.add_tab_stop(Inches(tab_in), alignment=2)
    sch = doc.add_paragraph()
    _sp(sch, before=1, after=2)
    r = sch.add_run(ed["school"])
    _font_run(r, "Calibri", 10, color=SOFT)


def _skills_detailed(doc, P):
    for label, key in [
        ("Core", "skills_core"),
        ("Tools", "skills_tools"),
        ("Leadership", "skills_lead"),
    ]:
        p = doc.add_paragraph()
        _sp(p, before=3, after=2, line=1.15)
        r = p.add_run(label + "  ·  ")
        _font_run(r, "Georgia", 9.5, bold=True, color=GOLD)
        r = p.add_run(P[key])
        _font_run(r, "Calibri", 10.5, color=INK)


# ── Layouts ──────────────────────────────────────────────────────────────────

def build_atelier(path: Path, filled=True, wm: str | None = None):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.6)
        s.left_margin = Inches(0.95)
        s.right_margin = Inches(0.95)
    _apply_wm(doc, wm)

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=8, after=8, line=1.0)
    r = name.add_run(P["name_spaced"])
    _font_run(r, "Georgia", 20, bold=True, color=NAVY)

    for sz, aft in ((4, 0), (12, 10)):
        rule = doc.add_paragraph()
        rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _sp(rule, before=2 if sz == 4 else 2, after=aft, line=1.0)
        _border_bottom(rule, GOLD, sz=sz, space=1)
        r = rule.add_run(" ")
        _font_run(r, "Georgia", 3, color=GOLD)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(sub, before=4, after=3)
    r = sub.add_run(P["title"])
    _font_run(r, "Georgia", 11, italic=True, color=GOLD)

    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(con, before=0, after=14)
    r = con.add_run(P["contact"])
    _font_run(r, "Calibri", 9, color=SOFT)

    def sec(t):
        p = doc.add_paragraph()
        _sp(p, before=14, after=6, line=1.0)
        r = p.add_run(t)
        _font_run(r, "Georgia", 9, bold=True, color=NAVY, all_caps=True)
        _border_bottom(p, GOLD, sz=8, space=5)

    sec("Profile")
    p = doc.add_paragraph()
    _sp(p, before=4, after=4, line=1.2)
    r = p.add_run(P["summary"])
    _font_run(r, "Calibri", 10.5, color=INK)

    sec("Capabilities")
    _skills_detailed(doc, P)

    sec("Experience")
    for job in P["experience"]:
        _job_block(doc, job)

    sec("Education")
    for ed in P["education"]:
        _edu_block(doc, ed)

    sec("Selected Work")
    for item in P["selected"]:
        _bullet(doc, item)

    sec("Certifications")
    for c in P["certs"]:
        _bullet(doc, c)

    sec("Languages")
    p = doc.add_paragraph()
    _sp(p, before=4, after=4)
    r = p.add_run(P["languages"])
    _font_run(r, "Calibri", 10.5, color=INK)

    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(foot, before=18, after=0)
    r = foot.add_run("·  MathRelaxing Atelier  ·")
    _font_run(r, "Georgia", 8, color=FAINT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_gallery(path: Path, filled=True, wm: str | None = None):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.62)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
    _apply_wm(doc, wm)

    top = doc.add_paragraph()
    _sp(top, before=0, after=10, line=1.0)
    _border_bottom(top, GOLD, sz=18, space=1)
    r = top.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)

    name = doc.add_paragraph()
    _sp(name, before=4, after=2, line=1.0)
    r = name.add_run(P["name"])
    _font_run(r, "Georgia", 26, bold=True, color=NAVY)

    sub = doc.add_paragraph()
    _sp(sub, before=2, after=2)
    r = sub.add_run(P["title"])
    _font_run(r, "Georgia", 11, color=GOLD)

    con = doc.add_paragraph()
    _sp(con, before=0, after=12)
    r = con.add_run(P["contact"])
    _font_run(r, "Calibri", 9, color=SOFT)

    def sec(t):
        p = doc.add_paragraph()
        _sp(p, before=13, after=5, line=1.0)
        r = p.add_run("▸  " + t.upper())
        _font_run(r, "Georgia", 9, bold=True, color=NAVY)
        _border_bottom(p, "12172D", sz=6, space=4)

    sec("Summary")
    p = doc.add_paragraph()
    _sp(p, before=4, after=4, line=1.18)
    r = p.add_run(P["summary"])
    _font_run(r, "Calibri", 10.5, color=INK)

    sec("Skills")
    _skills_detailed(doc, P)

    sec("Experience")
    for job in P["experience"]:
        _job_block(doc, job, tab_in=6.55)

    sec("Education")
    for ed in P["education"]:
        _edu_block(doc, ed, tab_in=6.55)

    sec("Selected")
    for item in P["selected"]:
        _bullet(doc, item)

    sec("More")
    p = doc.add_paragraph()
    _sp(p, before=3, after=2)
    r = p.add_run("Certifications  ·  ")
    _font_run(r, "Georgia", 9.5, bold=True, color=GOLD)
    r = p.add_run("  |  ".join(P["certs"]))
    _font_run(r, "Calibri", 10, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=2, after=2)
    r = p.add_run("Languages  ·  ")
    _font_run(r, "Georgia", 9.5, bold=True, color=GOLD)
    r = p.add_run(P["languages"])
    _font_run(r, "Calibri", 10, color=INK)

    foot = doc.add_paragraph()
    _sp(foot, before=16, after=0)
    r = foot.add_run("MathRelaxing Atelier  ·  Gallery")
    _font_run(r, "Georgia", 8, color=FAINT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_manuscript(path: Path, filled=True, wm: str | None = None):
    """Literary / classic — denser serif, centered small caps feel."""
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(1.05)
        s.right_margin = Inches(1.05)
    _apply_wm(doc, wm)

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=6, after=4)
    r = name.add_run(P["name"])
    _font_run(r, "Georgia", 22, bold=True, color=NAVY)

    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(rule, before=2, after=6)
    r = rule.add_run("—  ·  —")
    _font_run(r, "Georgia", 10, color=GOLD)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(sub, before=0, after=2)
    r = sub.add_run(P["title"])
    _font_run(r, "Georgia", 10.5, italic=True, color=SOFT)

    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(con, before=0, after=14)
    r = con.add_run(P["contact_short"])
    _font_run(r, "Calibri", 9, color=SOFT)

    def sec(t):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _sp(p, before=14, after=8)
        r = p.add_run("·  " + t.upper() + "  ·")
        _font_run(r, "Georgia", 9, bold=True, color=NAVY)

    sec("Profile")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _sp(p, before=0, after=6, line=1.25)
    r = p.add_run(P["summary"])
    _font_run(r, "Georgia", 10.5, color=INK)

    sec("Capabilities")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(p, before=0, after=6, line=1.2)
    r = p.add_run(P["skills_flat"])
    _font_run(r, "Calibri", 10, color=INK)

    sec("Experience")
    for job in P["experience"]:
        head = doc.add_paragraph()
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _sp(head, before=10, after=1)
        r = head.add_run(job["role"])
        _font_run(r, "Georgia", 11, bold=True, color=NAVY)
        meta = doc.add_paragraph()
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _sp(meta, before=0, after=4)
        r = meta.add_run(f"{job['co']}  ·  {job['dates']}")
        _font_run(r, "Calibri", 9.5, italic=True, color=TEAL)
        for b in job["bullets"]:
            bp = doc.add_paragraph()
            bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _sp(bp, before=1, after=2, line=1.15)
            r = bp.add_run("–  " + b)
            _font_run(r, "Calibri", 10, color=INK)

    sec("Education & More")
    for ed in P["education"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _sp(p, before=4, after=2)
        r = p.add_run(f"{ed['deg']}  ·  {ed['school']}  ·  {ed['dates']}")
        _font_run(r, "Georgia", 10, color=INK)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(p, before=8, after=2)
    r = p.add_run(P["languages"])
    _font_run(r, "Calibri", 9.5, color=SOFT)

    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(foot, before=18, after=0)
    r = foot.add_run("MathRelaxing Atelier  ·  Manuscript")
    _font_run(r, "Georgia", 8, color=FAINT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_architect(path: Path, filled=True, wm: str | None = None):
    """Asymmetric modern — name left large, meta right-ish via tabs, geometric cues."""
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.6)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.75)
    _apply_wm(doc, wm)

    # geometric top double rule
    for sz in (6, 14):
        p = doc.add_paragraph()
        _sp(p, before=0, after=1 if sz == 6 else 8, line=1.0)
        _border_bottom(p, GOLD if sz == 6 else NAVY, sz=sz, space=1)
        r = p.add_run(" ")
        _font_run(r, "Georgia", 2, color=GOLD)

    name = doc.add_paragraph()
    _sp(name, before=2, after=0, line=1.0)
    r = name.add_run(P["name"])
    _font_run(r, "Georgia", 28, bold=True, color=NAVY)

    # title + dates feel
    row = doc.add_paragraph()
    _sp(row, before=4, after=2)
    r = row.add_run(P["title"])
    _font_run(r, "Calibri", 11, color=GOLD)

    con = doc.add_paragraph()
    _sp(con, before=0, after=8)
    r = con.add_run(P["contact"])
    _font_run(r, "Calibri", 9, color=SOFT)

    # thin full rule
    rule = doc.add_paragraph()
    _sp(rule, before=2, after=10)
    _border_bottom(rule, GOLD, sz=6, space=2)
    r = rule.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)

    def sec(t):
        p = doc.add_paragraph()
        _sp(p, before=12, after=4, line=1.0)
        r = p.add_run(t.upper())
        _font_run(r, "Georgia", 9, bold=True, color=NAVY)
        # short gold underline effect via border
        _border_bottom(p, GOLD, sz=10, space=3)

    sec("Profile")
    p = doc.add_paragraph()
    _sp(p, before=4, after=4, line=1.18)
    r = p.add_run(P["summary"])
    _font_run(r, "Calibri", 10.5, color=INK)

    sec("Capabilities")
    _skills_detailed(doc, P)

    sec("Experience")
    for job in P["experience"]:
        _job_block(doc, job, tab_in=6.6)

    sec("Education")
    for ed in P["education"]:
        _edu_block(doc, ed, tab_in=6.6)

    sec("Selected Work & Credentials")
    for item in P["selected"] + P["certs"]:
        _bullet(doc, item)
    p = doc.add_paragraph()
    _sp(p, before=6, after=2)
    r = p.add_run(P["languages"])
    _font_run(r, "Calibri", 10, color=SOFT)

    foot = doc.add_paragraph()
    _sp(foot, before=14, after=0)
    r = foot.add_run("MathRelaxing Atelier  ·  Architect")
    _font_run(r, "Georgia", 8, color=FAINT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_ats(path: Path, filled=True):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.55)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=0, after=2)
    r = name.add_run(P["name"])
    _font_run(r, "Calibri", 18, bold=True, color=INK)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(sub, before=0, after=2)
    r = sub.add_run(P["title"].replace("  ·  ", " | "))
    _font_run(r, "Calibri", 11, color=SOFT)

    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(con, before=0, after=10)
    r = con.add_run(P["contact"].replace("  ·  ", " | "))
    _font_run(r, "Calibri", 9, color=SOFT)

    def sec(t):
        p = doc.add_paragraph()
        _sp(p, before=10, after=3)
        r = p.add_run(t.upper())
        _font_run(r, "Calibri", 10, bold=True, color=INK)
        _border_bottom(p, "333333", sz=8, space=3)

    sec("Summary")
    p = doc.add_paragraph()
    _sp(p, before=2, after=4)
    r = p.add_run(P["summary"])
    _font_run(r, "Calibri", 10.5, color=INK)

    sec("Skills")
    for label, key in [("Core", "skills_core"), ("Tools", "skills_tools"), ("Leadership", "skills_lead")]:
        p = doc.add_paragraph()
        _sp(p, before=2, after=2)
        r = p.add_run(f"{label}: ")
        _font_run(r, "Calibri", 10.5, bold=True, color=INK)
        r = p.add_run(P[key].replace("  ·  ", ", "))
        _font_run(r, "Calibri", 10.5, color=INK)

    sec("Experience")
    for job in P["experience"]:
        head = doc.add_paragraph()
        _sp(head, before=8, after=0)
        r = head.add_run(f"{job['role']} | {job['co']}")
        _font_run(r, "Calibri", 11, bold=True, color=INK)
        d = doc.add_paragraph()
        _sp(d, before=0, after=2)
        r = d.add_run(job["dates"])
        _font_run(r, "Calibri", 10, color=SOFT)
        for b in job["bullets"]:
            _bullet(doc, b)

    sec("Education")
    for ed in P["education"]:
        p = doc.add_paragraph()
        _sp(p, before=4, after=1)
        r = p.add_run(f"{ed['deg']} | {ed['school']} | {ed['dates']}")
        _font_run(r, "Calibri", 10.5, color=INK)

    sec("Selected Work")
    for item in P["selected"]:
        _bullet(doc, item)

    sec("Certifications & Languages")
    for c in P["certs"]:
        _bullet(doc, c)
    p = doc.add_paragraph()
    _sp(p, before=4, after=2)
    r = p.add_run(P["languages"].replace("  ·  ", " | "))
    _font_run(r, "Calibri", 10.5, color=INK)

    doc.save(str(path))
    print(f"  {path.name}")


def build_cover(path: Path, filled=True):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.9)
        s.bottom_margin = Inches(0.9)
        s.left_margin = Inches(1.05)
        s.right_margin = Inches(1.05)
    _page_bg(doc)

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=6, after=6)
    r = name.add_run(P["name_spaced"])
    _font_run(r, "Georgia", 14, bold=True, color=NAVY)
    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(rule, before=0, after=8)
    _border_bottom(rule, GOLD, sz=8, space=2)
    r = rule.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)
    con = doc.add_paragraph()
    con.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(con, before=0, after=18)
    r = con.add_run(P["contact"])
    _font_run(r, "Calibri", 9, color=SOFT)

    p = doc.add_paragraph()
    _sp(p, before=0, after=12)
    r = p.add_run("March 12, 2026" if filled else "Month DD, YYYY")
    _font_run(r, "Calibri", 10.5, color=INK)
    for line in ["Hiring Manager", "Organization Name" if not filled else "Meridian Labs", "City, ST"]:
        p = doc.add_paragraph()
        _sp(p, before=0, after=0)
        r = p.add_run(line)
        _font_run(r, "Calibri", 10.5, color=INK)

    p = doc.add_paragraph()
    _sp(p, before=14, after=10)
    r = p.add_run("Dear Hiring Manager,")
    _font_run(r, "Calibri", 10.5, color=INK)
    for para in P["cover_body"].split("\n\n"):
        p = doc.add_paragraph()
        _sp(p, before=0, after=10, line=1.25)
        r = p.add_run(para.strip())
        _font_run(r, "Calibri", 10.5, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=8, after=2)
    r = p.add_run("With appreciation,")
    _font_run(r, "Calibri", 10.5, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=16, after=0)
    r = p.add_run(P["name"])
    _font_run(r, "Georgia", 11, bold=True, color=NAVY)
    doc.save(str(path))
    print(f"  {path.name}")


def build_references(path: Path, filled=True):
    P = PERSONA if filled else _blank()
    refs = (
        [
            ("Dr. Amira Shah", "Director of Research", "Meridian Labs", "amira.shah@email.com"),
            ("Jonas Reed", "VP Product", "Northline", "jonas.reed@email.com"),
            ("Prof. Helen Cho", "Dissertation Advisor", "Columbia University", "h.cho@email.com"),
        ]
        if filled
        else [("Reference Name", "Title", "Organization", "email@domain.com")] * 3
    )
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.85)
        s.bottom_margin = Inches(0.85)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
    _page_bg(doc)
    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=8, after=6)
    r = name.add_run(P["name_spaced"])
    _font_run(r, "Georgia", 14, bold=True, color=NAVY)
    rule = doc.add_paragraph()
    rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(rule, before=0, after=8)
    _border_bottom(rule, GOLD, sz=8, space=2)
    r = rule.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(t, before=4, after=18)
    r = t.add_run("REFERENCES")
    _font_run(r, "Georgia", 10, bold=True, color=NAVY, all_caps=True)
    for nm, title, org, email in refs:
        p = doc.add_paragraph()
        _sp(p, before=14, after=2)
        r = p.add_run(nm)
        _font_run(r, "Georgia", 12, bold=True, color=NAVY)
        p = doc.add_paragraph()
        _sp(p, before=0, after=1)
        r = p.add_run(f"{title}  ·  {org}")
        _font_run(r, "Calibri", 10.5, color=TEAL)
        p = doc.add_paragraph()
        _sp(p, before=0, after=6)
        r = p.add_run(email)
        _font_run(r, "Calibri", 10, color=SOFT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_thankyou(path: Path, filled=True):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.1)
        s.right_margin = Inches(1.1)
    _page_bg(doc)
    p = doc.add_paragraph()
    _sp(p, before=0, after=4)
    r = p.add_run("Subject:  ")
    _font_run(r, "Calibri", 10.5, bold=True, color=NAVY)
    r = p.add_run("Thank you — " + ("conversation today" if filled else "[role / conversation]"))
    _font_run(r, "Calibri", 10.5, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=12, after=10)
    r = p.add_run("Dear Hiring Manager," if filled else "Dear [Name],")
    _font_run(r, "Calibri", 10.5, color=INK)
    for para in P["thankyou"].split("\n\n"):
        p = doc.add_paragraph()
        _sp(p, before=0, after=10, line=1.25)
        r = p.add_run(para.strip())
        _font_run(r, "Calibri", 10.5, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=8, after=2)
    r = p.add_run("Warmly,")
    _font_run(r, "Calibri", 10.5, color=INK)
    p = doc.add_paragraph()
    _sp(p, before=14, after=0)
    r = p.add_run(P["name"])
    _font_run(r, "Georgia", 11, bold=True, color=NAVY)
    doc.save(str(path))
    print(f"  {path.name}")


def build_linkedin_pack(path: Path, filled=True):
    P = PERSONA if filled else _blank()
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.95)
        s.right_margin = Inches(0.95)
    _page_bg(doc)
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(t, before=4, after=4)
    r = t.add_run("LINKEDIN COPY PACK")
    _font_run(r, "Georgia", 12, bold=True, color=NAVY, all_caps=True)
    rule = doc.add_paragraph()
    _sp(rule, before=0, after=12)
    _border_bottom(rule, GOLD, sz=8, space=2)
    r = rule.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)

    p = doc.add_paragraph()
    _sp(p, before=8, after=4)
    r = p.add_run("Headline")
    _font_run(r, "Georgia", 10, bold=True, color=GOLD, all_caps=True)
    p = doc.add_paragraph()
    _sp(p, before=2, after=12, line=1.2)
    r = p.add_run(P["linkedin_headline"])
    _font_run(r, "Calibri", 11, color=INK)

    p = doc.add_paragraph()
    _sp(p, before=8, after=4)
    r = p.add_run("About")
    _font_run(r, "Georgia", 10, bold=True, color=GOLD, all_caps=True)
    for para in P["linkedin_about"].split("\n\n"):
        p = doc.add_paragraph()
        _sp(p, before=0, after=8, line=1.25)
        r = p.add_run(para.strip())
        _font_run(r, "Calibri", 10.5, color=INK)

    p = doc.add_paragraph()
    _sp(p, before=12, after=4)
    r = p.add_run("Featured section tips")
    _font_run(r, "Georgia", 10, bold=True, color=GOLD, all_caps=True)
    for tip in [
        "Pin your strongest case study or talk PDF.",
        "Add a short post that shows how you think (not only job updates).",
        "Match headline keywords to roles you want next.",
    ]:
        _bullet(doc, tip)
    doc.save(str(path))
    print(f"  {path.name}")


def build_portfolio_onepager(path: Path, filled=True):
    """One-page project brief sheet matching Atelier."""
    P = PERSONA if filled else _blank()
    projects = (
        [
            (
                "Experimentation governance",
                "Meridian Labs",
                "Cut underpowered tests 40%; created a review checklist now used by 40+ squads.",
            ),
            (
                "Decision quality essays",
                "Independent",
                "Series with 40k readers; translated research craft for product audiences.",
            ),
            (
                "Growth activation system",
                "Northline",
                "+9% activation via sequenced onboarding informed by causal analysis.",
            ),
        ]
        if filled
        else [
            ("Project title", "Organization", "One-line outcome with metric."),
            ("Project title", "Organization", "One-line outcome with metric."),
            ("Project title", "Organization", "One-line outcome with metric."),
        ]
    )
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.65)
        s.left_margin = Inches(0.9)
        s.right_margin = Inches(0.9)
    _page_bg(doc)

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=4, after=4)
    r = name.add_run(P["name_spaced"])
    _font_run(r, "Georgia", 14, bold=True, color=NAVY)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(sub, before=0, after=4)
    r = sub.add_run("SELECTED WORK  ·  ONE-PAGER")
    _font_run(r, "Georgia", 9, bold=True, color=GOLD, all_caps=True)
    rule = doc.add_paragraph()
    _sp(rule, before=2, after=12)
    _border_bottom(rule, GOLD, sz=10, space=2)
    r = rule.add_run(" ")
    _font_run(r, "Georgia", 2, color=GOLD)

    for title, org, blurb in projects:
        p = doc.add_paragraph()
        _sp(p, before=12, after=2)
        r = p.add_run(title)
        _font_run(r, "Georgia", 12, bold=True, color=NAVY)
        p = doc.add_paragraph()
        _sp(p, before=0, after=3)
        r = p.add_run(org)
        _font_run(r, "Calibri", 10, italic=True, color=TEAL)
        p = doc.add_paragraph()
        _sp(p, before=0, after=6, line=1.2)
        r = p.add_run(blurb)
        _font_run(r, "Calibri", 10.5, color=INK)
        div = doc.add_paragraph()
        _sp(div, before=2, after=2)
        _border_bottom(div, "E5DFD3", sz=4, space=1)
        r = div.add_run(" ")
        _font_run(r, "Georgia", 2, color=FAINT)

    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(foot, before=16, after=0)
    r = foot.add_run(P["contact_short"] + "  ·  MathRelaxing Atelier")
    _font_run(r, "Calibri", 9, color=SOFT)
    doc.save(str(path))
    print(f"  {path.name}")


def build_howto_pdf(path: Path):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=0.85 * inch, rightMargin=0.85 * inch, topMargin=0.7 * inch, bottomMargin=0.6 * inch)
    navy, gold, ink = HexColor(NAVY), HexColor(GOLD), HexColor(INK)
    h = ParagraphStyle("h", fontName="Times-Bold", fontSize=16, textColor=navy, spaceAfter=8, alignment=1)
    s = ParagraphStyle("s", fontName="Helvetica", fontSize=9.5, textColor=ink, leading=13, spaceAfter=6)
    b = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=10, textColor=gold, spaceBefore=10, spaceAfter=4)
    story = [
        Paragraph("MathRelaxing Atelier Resume Kit", h),
        Paragraph("How to use — expanded edition", ParagraphStyle("sub", fontName="Times-Italic", fontSize=11, textColor=gold, alignment=1, spaceAfter=12)),
        HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=12),
        Paragraph("Choose a layout", b),
        Paragraph("<b>Atelier</b> — centered, letterspaced name, double gold rules. Most elegant for email PDFs.", s),
        Paragraph("<b>Gallery</b> — left-aligned modern with gold top bar. Strong for product/design-adjacent roles.", s),
        Paragraph("<b>Manuscript</b> — literary centered classic. Quiet authority for research/writing-forward roles.", s),
        Paragraph("<b>Architect</b> — geometric, asymmetric weight. Bold modern presence.", s),
        Paragraph("<b>ATS</b> — single-column Calibri for online portals that strip design.", s),
        Paragraph("Atelier background styles", b),
        Paragraph("Open any <b>Atelier_Style_*</b> file to get cream paper + a semi-transparent plate already behind the text: Cream Veil, Scientific Grid, Gold Geometry, Phi Whisper, Navy Edge. Use SAMPLE files as visual guides, then edit the TEMPLATE.", s),
        Paragraph("Application set", b),
        Paragraph("Cover letter · References · Thank-you note · LinkedIn pack (headline + About) · Portfolio one-pager. Match tone across all files.", s),
        Paragraph("Workflow", b),
        Paragraph("1) Fill Guest persona fields in SAMPLE to learn rhythm.<br/>2) Duplicate TEMPLATE and replace placeholders.<br/>3) Export PDF from Word for email applications.<br/>4) Use ATS file only for portals.<br/>5) Paste LinkedIn pack into your profile.", s),
        Paragraph(brand.COPYRIGHT, ParagraphStyle("f", fontName="Helvetica", fontSize=8, textColor=HexColor(FAINT), spaceBefore=16)),
    ]
    doc.build(story)
    print(f"  {path.name}")


def build_sample_resume_pdf(path: Path):
    P = PERSONA
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.65 * inch, bottomMargin=0.55 * inch)
    navy, gold, ink, soft, teal = HexColor(NAVY), HexColor(GOLD), HexColor(INK), HexColor(SOFT), HexColor(TEAL)
    styles = {
        "name": ParagraphStyle("n", fontName="Times-Bold", fontSize=15, textColor=navy, alignment=1, spaceAfter=6),
        "sub": ParagraphStyle("su", fontName="Times-Italic", fontSize=10, textColor=gold, alignment=1, spaceAfter=3),
        "con": ParagraphStyle("c", fontName="Helvetica", fontSize=8, textColor=soft, alignment=1, spaceAfter=10),
        "sec": ParagraphStyle("se", fontName="Times-Bold", fontSize=9, textColor=navy, spaceBefore=10, spaceAfter=3),
        "body": ParagraphStyle("bo", fontName="Helvetica", fontSize=9, textColor=ink, leading=12, spaceAfter=3),
        "role": ParagraphStyle("ro", fontName="Times-Bold", fontSize=10, textColor=navy, spaceBefore=7),
        "co": ParagraphStyle("co", fontName="Helvetica-Oblique", fontSize=8.5, textColor=teal, spaceAfter=2),
        "bu": ParagraphStyle("bu", fontName="Helvetica", fontSize=9, textColor=ink, leftIndent=10, leading=11, spaceAfter=1),
    }
    story = [
        Paragraph(P["name_spaced"].replace(" ", "&nbsp;"), styles["name"]),
        HRFlowable(width="38%", thickness=0.5, color=gold, hAlign="CENTER", spaceAfter=1),
        HRFlowable(width="38%", thickness=1.2, color=gold, hAlign="CENTER", spaceAfter=6),
        Paragraph(P["title"], styles["sub"]),
        Paragraph(P["contact"], styles["con"]),
        Paragraph("PROFILE", styles["sec"]),
        HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=4),
        Paragraph(P["summary"], styles["body"]),
        Paragraph("CAPABILITIES", styles["sec"]),
        HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=4),
        Paragraph(f"<b>Core</b> — {P['skills_core']}", styles["body"]),
        Paragraph(f"<b>Tools</b> — {P['skills_tools']}", styles["body"]),
        Paragraph(f"<b>Lead</b> — {P['skills_lead']}", styles["body"]),
        Paragraph("EXPERIENCE", styles["sec"]),
        HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=3),
    ]
    for job in P["experience"]:
        story.append(Paragraph(f"{job['role']}  —  {job['dates']}", styles["role"]))
        story.append(Paragraph(job["co"], styles["co"]))
        for b in job["bullets"]:
            story.append(Paragraph(f"• {b}", styles["bu"]))
    story += [
        Paragraph("EDUCATION", styles["sec"]),
        HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=3),
    ]
    for ed in P["education"]:
        story.append(Paragraph(f"<b>{ed['deg']}</b> — {ed['school']} ({ed['dates']})", styles["body"]))
    story.append(Paragraph("· MathRelaxing Atelier ·", ParagraphStyle("f", fontName="Times-Roman", fontSize=8, textColor=HexColor(FAINT), alignment=1, spaceBefore=12)))
    doc.build(story)
    print(f"  {path.name}")


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


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_previews(bg_paths: dict):
    s = 2000
    cream, navy, gold = _rgb(CREAM), _rgb(NAVY), _rgb(GOLD)
    paths = []

    # 1 hero
    img = Image.new("RGB", (s, s), navy)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 80), "ATELIER", font=_tf(16), fill=gold, anchor="mt")
    d.text((s // 2, 120), "Resume Kit", font=_tf(46, True), fill=cream, anchor="mt")
    d.text((s // 2, 190), "5 layouts  ·  5 background styles  ·  full application set", font=_ts(16), fill=gold, anchor="mt")
    pw, ph = 720, 940
    px, py = (s - pw) // 2, 280
    sh = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([px + 16, py + 20, px + pw + 16, py + ph + 20], fill=(0, 0, 0, 100))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px, py, px + pw, py + ph], fill=cream, outline=gold, width=2)
    d.text((px + pw // 2, py + 60), "C E L I N E   M O R A", font=_tf(22, True), fill=navy, anchor="mt")
    d.line([(px + 180, py + 110), (px + pw - 180, py + 110)], fill=gold, width=1)
    d.line([(px + 180, py + 118), (px + pw - 180, py + 118)], fill=gold, width=2)
    d.text((px + pw // 2, py + 150), "Applied Research Lead", font=_ts(14), fill=gold, anchor="mt")
    y = py + 220
    for title, nlines in [("PROFILE", 3), ("CAPABILITIES", 3), ("EXPERIENCE", 6)]:
        d.text((px + 60, y), title, font=_tf(12, True), fill=navy, anchor="lt")
        y += 28
        d.line([(px + 60, y), (px + pw - 60, y)], fill=gold, width=1)
        y += 16
        for _ in range(nlines):
            d.rectangle([px + 60, y, px + pw - 60, y + 10], fill=(220, 215, 205))
            y += 24
        y += 16
    d.rectangle([0, s - 90, s, s], fill=(8, 10, 22))
    d.text((s // 2, s - 45), "MathRelaxing  ·  Premium application system", font=_ts(18), fill=gold, anchor="mm")
    p = PREVIEWS / "luxe_preview_1_hero.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 2 five layouts strip
    img = Image.new("RGB", (s, s), cream)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 60), "Five layout systems", font=_tf(34, True), fill=navy, anchor="mt")
    labels = ["Atelier", "Gallery", "Manuscript", "Architect", "ATS"]
    cw = 320
    gap = 30
    total = 5 * cw + 4 * gap
    x0 = (s - total) // 2
    for i, lab in enumerate(labels):
        x = x0 + i * (cw + gap)
        d.rectangle([x, 180, x + cw, 1500], fill=cream if i < 4 else (255, 255, 255), outline=navy, width=2)
        if i == 0:
            d.text((x + cw // 2, 220), "C E L I N E", font=_tf(14, True), fill=navy, anchor="mt")
            d.line([(x + 60, 260), (x + cw - 60, 260)], fill=gold, width=2)
        elif i == 1:
            d.rectangle([x + 20, 200, x + cw - 20, 208], fill=gold)
            d.text((x + 30, 230), "CELINE MORA", font=_tf(16, True), fill=navy, anchor="lt")
        elif i == 2:
            d.text((x + cw // 2, 230), "CELINE MORA", font=_tf(15, True), fill=navy, anchor="mt")
            d.text((x + cw // 2, 270), "— · —", font=_tf(12), fill=gold, anchor="mt")
        elif i == 3:
            d.line([(x + 24, 210), (x + cw - 24, 210)], fill=gold, width=3)
            d.text((x + 30, 240), "CELINE", font=_tf(22, True), fill=navy, anchor="lt")
            d.text((x + 30, 280), "MORA", font=_tf(22, True), fill=navy, anchor="lt")
        else:
            d.text((x + cw // 2, 230), "CELINE MORA", font=_ts(16, True), fill=navy, anchor="mt")
        y = 340
        for _ in range(12):
            d.rectangle([x + 28, y, x + cw - 28, y + 8], fill=(220, 215, 205))
            y += 28
        d.text((x + cw // 2, 1560), lab.upper(), font=_ts(14, True), fill=gold, anchor="mt")
    d.rectangle([0, s - 80, s, s], fill=navy)
    d.text((s // 2, s - 40), "Pick the system that fits the role", font=_ts(16), fill=cream, anchor="mm")
    p = PREVIEWS / "luxe_preview_2_layouts.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 3 background styles
    img = Image.new("RGB", (s, s), navy)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 70), "Atelier background styles", font=_tf(32, True), fill=cream, anchor="mt")
    d.text((s // 2, 130), "Semi-transparent plates already in the Word files", font=_ts(16), fill=gold, anchor="mt")
    keys = list(BG_STYLES.keys())
    tw, th = 340, 440
    for i, key in enumerate(keys):
        label, _ = BG_STYLES[key]
        c, r = i % 5, 0
        # 5 across one row - smaller
        tw = 340
        x = 80 + i * (tw + 28)
        y = 220
        card = Image.new("RGB", (tw, th), cream)
        if key in bg_paths and os.path.isfile(bg_paths[key]):
            bg = Image.open(bg_paths[key]).convert("RGBA")
            bg = bg.resize((tw - 20, th - 60), Image.Resampling.LANCZOS)
            base = Image.new("RGBA", (tw - 20, th - 60), (*cream, 255))
            base = Image.alpha_composite(base, bg)
            card.paste(base.convert("RGB"), (10, 10))
        cd = ImageDraw.Draw(card)
        cd.text((tw // 2, th - 30), label, font=_ts(14, True), fill=navy, anchor="mm")
        img.paste(card, (x, y))
    d.rectangle([0, s - 200, s, s], fill=(8, 10, 22))
    extras = [
        "Cover letter",
        "References",
        "Thank-you note",
        "LinkedIn pack",
        "Portfolio one-pager",
        "How-to PDF",
    ]
    d.text((s // 2, s - 150), "Also included", font=_tf(20, True), fill=gold, anchor="mt")
    d.text((s // 2, s - 90), "   ·   ".join(extras), font=_ts(15), fill=cream, anchor="mt")
    p = PREVIEWS / "luxe_preview_3_styles.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=90)
    paths.append(p)

    # 4 application set
    img = Image.new("RGB", (s, s), cream)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 70), "Full application set", font=_tf(36, True), fill=navy, anchor="mt")
    pieces = [
        ("Cover", "Matching Atelier\nletter system"),
        ("References", "Three polished\nreference slots"),
        ("Thank-you", "Post-interview\nemail draft"),
        ("LinkedIn", "Headline + About\nready to paste"),
        ("Portfolio", "One-pager of\nselected work"),
        ("How-to", "Layout guide &\nworkflow PDF"),
    ]
    cw, ch = 560, 420
    gap = 40
    x0 = (s - 3 * cw - 2 * gap) // 2
    y0 = 200
    for i, (title, sub) in enumerate(pieces):
        c, r = i % 3, i // 3
        x = x0 + c * (cw + gap)
        y = y0 + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=12, fill=navy)
        d.text((x + 40, y + 60), title, font=_tf(28, True), fill=gold, anchor="lt")
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 40, y + 160 + j * 40), line, font=_ts(20), fill=cream, anchor="lt")
    p = PREVIEWS / "luxe_preview_4_set.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 5 detail
    img = Image.new("RGB", (s, s), (228, 224, 216))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([180, 280, 1820, 1400], radius=10, fill=cream)
    d.text((1000, 400), "C E L I N E   M O R A", font=_tf(40, True), fill=navy, anchor="mt")
    d.line([(650, 500), (1350, 500)], fill=gold, width=1)
    d.line([(650, 512), (1350, 512)], fill=gold, width=3)
    d.text((1000, 560), "Applied Research Lead  ·  Product Strategy", font=_tf(20), fill=gold, anchor="mt")
    d.text((1000, 640), "Core  ·  Causal inference  ·  Experimentation  ·  Bayesian modeling", font=_ts(16), fill=_rgb(SOFT), anchor="mt")
    d.text((1000, 720), "Tools  ·  Python  ·  SQL  ·  R  ·  Stan  ·  dbt", font=_ts(16), fill=_rgb(SOFT), anchor="mt")
    d.text((1000, 860), "Designed detail — not a single blank file", font=_ts(18), fill=navy, anchor="mt")
    d.rectangle([0, s - 100, s, s], fill=navy)
    d.text((s // 2, s - 50), "$12.99  ·  Built to feel complete", font=_ts(18), fill=gold, anchor="mm")
    p = PREVIEWS / "luxe_preview_5_detail.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    # 6 what's inside count
    img = Image.new("RGB", (s, s), navy)
    d = ImageDraw.Draw(img)
    d.text((s // 2, 100), "What's inside", font=_tf(40, True), fill=cream, anchor="mt")
    counts = [
        ("20+", "Word documents"),
        ("5", "Layout systems"),
        ("5", "Background styles"),
        ("6", "Application pieces"),
        ("1", "How-to PDF"),
        ("∞", "Roles you can tailor"),
    ]
    for i, (n, lab) in enumerate(counts):
        c, r = i % 3, i // 3
        x = 160 + c * 580
        y = 280 + r * 520
        d.rounded_rectangle([x, y, x + 520, y + 440], radius=16, outline=gold, width=2)
        d.text((x + 260, y + 140), n, font=_tf(64, True), fill=gold, anchor="mt")
        d.text((x + 260, y + 280), lab, font=_ts(22), fill=cream, anchor="mt")
    p = PREVIEWS / "luxe_preview_6_value.jpg"
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(p, quality=92)
    paths.append(p)

    print(f"  {len(paths)} previews")
    return paths


def build_zip():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (TEMPLATES, SAMPLES, BACKGROUNDS):
            if not folder.exists():
                continue
            for p in folder.rglob("*"):
                if p.is_file() and not p.name.startswith("_"):
                    z.write(p, p.relative_to(OUT).as_posix())
        # include contact sheet if present
        sheet = BACKGROUNDS / "_styles_contact_sheet.jpg"
        if sheet.exists():
            z.write(sheet, "backgrounds/_styles_contact_sheet.jpg")
    print(f"  ZIP {ZIP_PATH.name} ({ZIP_PATH.stat().st_size / 1024:.0f} KB)")


def main():
    _ensure()
    print("=== Atelier Resume Kit — expanded ===")
    print("Backgrounds…")
    bg_paths = write_backgrounds(str(BACKGROUNDS))

    print("Core layouts…")
    build_atelier(TEMPLATES / "01_Atelier_Resume_Template.docx", False)
    build_atelier(TEMPLATES / "01_Atelier_Resume_SAMPLE.docx", True)
    build_gallery(TEMPLATES / "02_Gallery_Resume_Template.docx", False)
    build_gallery(TEMPLATES / "02_Gallery_Resume_SAMPLE.docx", True)
    build_manuscript(TEMPLATES / "03_Manuscript_Resume_Template.docx", False)
    build_manuscript(TEMPLATES / "03_Manuscript_Resume_SAMPLE.docx", True)
    build_architect(TEMPLATES / "04_Architect_Resume_Template.docx", False)
    build_architect(TEMPLATES / "04_Architect_Resume_SAMPLE.docx", True)
    build_ats(TEMPLATES / "05_ATS_Resume_Template.docx", False)
    build_ats(TEMPLATES / "05_ATS_Resume_SAMPLE.docx", True)

    print("Atelier style variants…")
    style_map = {
        "CreamVeil": "cream_veil",
        "ScientificGrid": "scientific_grid",
        "GoldGeometry": "gold_geometry",
        "PhiWhisper": "phi_whisper",
        "NavyEdge": "navy_edge",
    }
    for label, key in style_map.items():
        wm = bg_paths.get(key)
        build_atelier(TEMPLATES / f"01_Atelier_Style_{label}_Template.docx", False, wm)
        build_atelier(TEMPLATES / f"01_Atelier_Style_{label}_SAMPLE.docx", True, wm)

    print("Application set…")
    build_cover(TEMPLATES / "06_Cover_Letter_Template.docx", False)
    build_cover(TEMPLATES / "06_Cover_Letter_SAMPLE.docx", True)
    build_references(TEMPLATES / "07_References_Template.docx", False)
    build_references(TEMPLATES / "07_References_SAMPLE.docx", True)
    build_thankyou(TEMPLATES / "08_ThankYou_Note_Template.docx", False)
    build_thankyou(TEMPLATES / "08_ThankYou_Note_SAMPLE.docx", True)
    build_linkedin_pack(TEMPLATES / "09_LinkedIn_Pack_Template.docx", False)
    build_linkedin_pack(TEMPLATES / "09_LinkedIn_Pack_SAMPLE.docx", True)
    build_portfolio_onepager(TEMPLATES / "10_Portfolio_OnePager_Template.docx", False)
    build_portfolio_onepager(TEMPLATES / "10_Portfolio_OnePager_SAMPLE.docx", True)

    print("Guides & PDF…")
    build_howto_pdf(SAMPLES / "HOW_TO_USE.pdf")
    build_sample_resume_pdf(SAMPLES / "Sample_Atelier_Resume_Celine_Mora.pdf")

    print("Previews…")
    make_previews(bg_paths)
    build_zip()
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
