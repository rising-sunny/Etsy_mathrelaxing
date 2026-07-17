"""
generate_lor_pack.py — MathRelaxing Letter of Recommendation Pack
=================================================================
6 editorial LOR templates (blank + sample) + writing guide + previews.
Informed by Etsy SERP: winners sell Word(+Docs) single letters at $2–7;
we ship a multi-use pack with samples + guide at premium-but-fair $7.99.

  python generate_lor_pack.py
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

import brand

BASE = Path(__file__).resolve().parent
OUT = BASE / "lor_pack"
TEMPLATES = OUT / "templates"
SAMPLES = OUT / "samples"
PREVIEWS = OUT / "previews"
ZIP_PATH = OUT / "MathRelaxing_Letter_of_Recommendation_Pack.zip"

NAVY = "#12172D"
GOLD = "#C9A24B"
CREAM = "#F8F4EB"
INK = "#1A1A1A"
SOFT = "#5C5A56"
FAINT = "#9A958C"

# Recommender persona (STEM-professional voice for samples)
REC = {
    "name": "Dr. Amira Shah",
    "title": "Director of Research",
    "org": "Meridian Labs",
    "email": "amira.shah@meridianlabs.example",
    "phone": "(212) 555-0142",
    "city": "New York, NY",
}

CAND = {
    "name": "Celine Mora",
    "pronouns": "she/her",
    "role": "Applied Research Lead",
}


def _ensure():
    for d in (OUT, TEMPLATES, SAMPLES, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)


def _hex(c: str) -> RGBColor:
    h = c.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _run(run, name="Calibri", size=11, bold=False, color=None, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = _hex(color)


def _sp(p, before=0, after=6, line=1.15):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line


def _page_bg(doc: Document):
    bg = OxmlElement("w:background")
    bg.set(qn("w:color"), "F8F4EB")
    doc.element.insert(0, bg)
    doc.settings.element.append(OxmlElement("w:displayBackgroundShape"))


def _bottom_border(paragraph, color="C9A24B", sz=10):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color.lstrip("#"))
    pBdr.append(bottom)
    pPr.append(pBdr)


def _letterhead(doc: Document, filled: bool):
    """Editorial letterhead — gap vs plain competitor Times docs."""
    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(name, before=0, after=2)
    r = name.add_run(REC["name"] if filled else "[Your Full Name]")
    _run(r, "Georgia", 14, bold=True, color=NAVY)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(title, before=0, after=2)
    r = title.add_run(
        f"{REC['title']}  ·  {REC['org']}" if filled else "[Your Title]  ·  [Organization]"
    )
    _run(r, "Georgia", 10, italic=True, color=GOLD)

    contact = doc.add_paragraph()
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(contact, before=0, after=6)
    r = contact.add_run(
        f"{REC['email']}  ·  {REC['phone']}  ·  {REC['city']}"
        if filled
        else "[email]  ·  [phone]  ·  [City, ST]"
    )
    _run(r, "Calibri", 9, color=SOFT)

    rule = doc.add_paragraph()
    _sp(rule, before=2, after=14)
    _bottom_border(rule, GOLD, sz=12)
    r = rule.add_run(" ")
    _run(r, "Georgia", 2, color=GOLD)


def _para(doc, text, size=11, after=10, first_indent=False):
    p = doc.add_paragraph()
    _sp(p, before=0, after=after, line=1.2)
    if first_indent:
        p.paragraph_format.first_line_indent = Inches(0.25)
    r = p.add_run(text)
    _run(r, "Calibri", size, color=INK)
    return p


# ── Letter bodies ────────────────────────────────────────────────────────────

LETTERS = {
    "01_Job_Employee": {
        "label": "Job / Employee (manager voice)",
        "filename": "01_Job_Employee_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "[Hiring Manager Name]\n[Company Name]\n[City, ST]",
            "salutation": "Dear [Hiring Manager Name],",
            "body": [
                "I am pleased to recommend [Candidate Full Name] for the [Role Title] position at [Company]. I supervised [him/her/them] as [Your Relationship] at [Organization] from [Start Year] to [End Year / Present].",
                "In that role, [Candidate] owned [scope of work]. A concrete example: [specific project or metric — e.g., improved X by Y%, led a team of N, shipped Z]. [He/She/They] combines strong judgment with clear communication — rare and valuable under pressure.",
                "Beyond delivery, [Candidate] raises the standard of the people around [him/her/them]. [Brief note on mentorship, collaboration, or integrity]. I would rehire [him/her/them] without hesitation.",
                "Please contact me if I can offer further detail. I recommend [Candidate Full Name] with confidence.",
            ],
            "closing": "Sincerely,",
        },
        "sample": {
            "date": "March 12, 2026",
            "recipient": "Hiring Committee\nNorthline Analytics\nSan Francisco, CA",
            "salutation": "Dear Hiring Committee,",
            "body": [
                f"I am pleased to recommend {CAND['name']} for a senior product analytics or research leadership role. I have supervised {CAND['name']} as Director of Research at Meridian Labs since 2021, where {CAND['pronouns'].split('/')[0]} serves as Applied Research Lead.",
                f"Celine directed a seven-person research pod whose work shaped three major product bets representing roughly $18M in ARR influence. {CAND['pronouns'].split('/')[0].capitalize()} rebuilt our experimentation governance and reduced underpowered tests by 40% within two quarters — a change product and engineering still cite as foundational.",
                "Equally important, Celine writes for executives who need signal, not slides. She established a research writing standard now used across product, design, and data science. I would rehire her without hesitation and recommend her with the highest confidence.",
                "I am happy to provide further detail by email or phone.",
            ],
            "closing": "Sincerely,",
        },
    },
    "02_Academic_GradSchool": {
        "label": "Academic / Graduate School",
        "filename": "02_Academic_GradSchool_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "Admissions Committee\n[Program Name]\n[University]",
            "salutation": "Dear Members of the Admissions Committee,",
            "body": [
                "I am writing to recommend [Candidate Full Name] for admission to [Program]. I taught / advised [him/her/them] in [Course or Lab] at [University] during [Term/Year].",
                "[Candidate] demonstrated intellectual rigor and independence. In [project/thesis], [he/she/they] [specific scholarly contribution]. [His/Her/Their] work stands out for [quality — clarity, originality, methods].",
                "Personally, [Candidate] is [collegial traits]. I believe [he/she/they] will thrive in a demanding graduate environment and contribute meaningfully to your cohort.",
                "I recommend [Candidate Full Name] enthusiastically for admission.",
            ],
            "closing": "Respectfully,",
        },
        "sample": {
            "date": "February 2, 2026",
            "recipient": "Admissions Committee\nM.S. Data Science\nUniversity of Example",
            "salutation": "Dear Members of the Admissions Committee,",
            "body": [
                f"I am writing to recommend {CAND['name']} for graduate study in applied data science. I advised Celine during her research appointment at the Institute for Decision Science (2014–2017) and have continued to collaborate on methodological questions since.",
                "Celine’s work on multi-armed bandits for adaptive surveys was peer-reviewed and later informed open-source tooling used by our lab. She pairs technical fluency with an unusual ability to frame research questions that product teams can actually use.",
                "She is rigorous, generous with collaborators, and clear under deadline. I recommend her enthusiastically for admission and expect her to be a strong contributor to your program.",
            ],
            "closing": "Respectfully,",
        },
    },
    "03_Teacher_Student": {
        "label": "Teacher recommending a student",
        "filename": "03_Teacher_Student_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "[Admissions / Scholarship Committee]\n[Institution]",
            "salutation": "Dear Committee Members,",
            "body": [
                "I am delighted to recommend [Student Full Name] for [college admission / scholarship / program]. I taught [him/her/them] in [Course] at [School] during [Year].",
                "Academically, [Student] [specific strength with example]. [He/She/They] consistently [effort / curiosity / leadership in class].",
                "Outside pure performance, [Student] [character example — integrity, kindness, resilience]. I am confident [he/she/they] will represent your institution well.",
                "Please contact me with any questions. I recommend [Student Full Name] without reservation.",
            ],
            "closing": "Sincerely,",
        },
        "sample": {
            "date": "January 18, 2026",
            "recipient": "Scholarship Committee\nSTEM Scholars Foundation",
            "salutation": "Dear Committee Members,",
            "body": [
                "I am delighted to recommend Jordan Hale for the STEM Scholars award. I taught Jordan in AP Statistics and Research Methods at Riverside High School during the 2024–2025 academic year.",
                "Jordan treats quantitative work as a craft: careful with assumptions, honest about uncertainty, and unusually clear when explaining results to classmates. In our capstone, Jordan designed a survey experiment on study habits and presented findings that the counseling office later used in workshops.",
                "Just as important, Jordan lifts peers — running after-school help sessions without being asked. I recommend Jordan without reservation.",
            ],
            "closing": "Sincerely,",
        },
    },
    "04_Character_Personal": {
        "label": "Character / personal reference",
        "filename": "04_Character_Personal_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "To Whom It May Concern:",
            "salutation": "To Whom It May Concern,",
            "body": [
                "I am writing as a personal reference for [Candidate Full Name], whom I have known for [X years] as [friend / neighbor / mentor / community colleague].",
                "In that time I have known [him/her/them] to be [2–3 character traits] . A representative example: [specific story showing reliability, integrity, or care for others].",
                "I trust [Candidate] completely in matters of judgment and responsibility. I recommend [him/her/them] for [opportunity] without hesitation.",
                "I am available to discuss this reference further if helpful.",
            ],
            "closing": "Sincerely,",
        },
        "sample": {
            "date": "April 5, 2026",
            "recipient": "To Whom It May Concern:",
            "salutation": "To Whom It May Concern,",
            "body": [
                f"I am writing as a personal reference for {CAND['name']}, whom I have known for eight years as a colleague and friend in New York’s research community.",
                "Celine is steady under pressure and careful with other people’s trust. When a mutual collaborator faced a difficult public correction, Celine helped rewrite the note with precision and kindness — protecting both the science and the person.",
                "I recommend her character and judgment without hesitation for any role requiring integrity and discretion.",
            ],
            "closing": "Sincerely,",
        },
    },
    "05_Scholarship": {
        "label": "Scholarship recommendation",
        "filename": "05_Scholarship_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "Scholarship Selection Committee\n[Foundation / University]",
            "salutation": "Dear Selection Committee,",
            "body": [
                "I recommend [Candidate Full Name] for the [Scholarship Name]. I have known [him/her/them] as [relationship] at [Organization/School] since [Year].",
                "[Candidate] stands out for [merit: academic excellence / leadership / service] . Evidence: [specific achievement].",
                "This scholarship would enable [Candidate] to [impact]. I am confident [he/she/they] will use the opportunity responsibly and with distinction.",
                "Thank you for considering this application. I welcome further questions.",
            ],
            "closing": "Sincerely,",
        },
        "sample": {
            "date": "November 10, 2025",
            "recipient": "Scholarship Selection Committee\nDecision Science Foundation",
            "salutation": "Dear Selection Committee,",
            "body": [
                f"I recommend {CAND['name']} for the Decision Science Leadership Scholarship. As her research director at Meridian Labs, I have seen Celine turn ambiguous product questions into measurable decisions — and teach others to do the same.",
                "Her experimentation governance work cut underpowered tests by 40% and became a standard across forty product squads. She pairs technical depth with public-facing clarity; her essay series on decision quality has reached tens of thousands of readers.",
                "This scholarship would amplify a researcher already multiplying others’ impact. I recommend her with enthusiasm.",
            ],
            "closing": "Sincerely,",
        },
    },
    "06_Coworker_Peer": {
        "label": "Coworker / peer recommendation",
        "filename": "06_Coworker_Peer_LOR",
        "blank": {
            "date": "[Month DD, YYYY]",
            "recipient": "[Hiring Manager / Committee]\n[Company]",
            "salutation": "Dear [Name],",
            "body": [
                "I am writing to recommend [Candidate Full Name], my colleague at [Organization] from [Years]. We worked together on [team / project].",
                "As a peer, I observed [Candidate] to be [strengths]. On [project], [he/she/they] [concrete contribution and outcome].",
                "Day to day, [Candidate] is [collaboration traits]. I would welcome the chance to work with [him/her/them] again.",
                "Please feel free to contact me for more detail.",
            ],
            "closing": "Best regards,",
        },
        "sample": {
            "date": "May 20, 2026",
            "recipient": "Hiring Manager\nHelix Health",
            "salutation": "Dear Hiring Manager,",
            "body": [
                f"I am writing to recommend {CAND['name']}, my colleague at Meridian Labs for the past four years. We partnered closely on experimentation design and research reviews across product squads.",
                "Celine is the person you want in the room when a result is ambiguous. She asks the hard methodological questions without ego, and she documents decisions so teams can move. Her review checklist is now the default for launches I support.",
                "I would work with her again immediately and recommend her without reservation.",
            ],
            "closing": "Best regards,",
        },
    },
}


def build_letter(path: Path, letter_key: str, filled: bool):
    spec = LETTERS[letter_key]
    content = spec["sample"] if filled else spec["blank"]
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.85)
        s.bottom_margin = Inches(0.85)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
    _page_bg(doc)
    _letterhead(doc, filled)

    p = doc.add_paragraph()
    _sp(p, before=0, after=12)
    r = p.add_run(content["date"])
    _run(r, "Calibri", 11, color=INK)

    for line in content["recipient"].split("\n"):
        p = doc.add_paragraph()
        _sp(p, before=0, after=0)
        r = p.add_run(line)
        _run(r, "Calibri", 11, color=INK)

    p = doc.add_paragraph()
    _sp(p, before=14, after=10)
    r = p.add_run(content["salutation"])
    _run(r, "Calibri", 11, color=INK)

    for para in content["body"]:
        _para(doc, para, after=10)

    p = doc.add_paragraph()
    _sp(p, before=8, after=2)
    r = p.add_run(content["closing"])
    _run(r, "Calibri", 11, color=INK)

    p = doc.add_paragraph()
    _sp(p, before=28, after=0)
    r = p.add_run(REC["name"] if filled else "[Your Name]")
    _run(r, "Georgia", 11, bold=True, color=NAVY)
    p = doc.add_paragraph()
    _sp(p, before=0, after=0)
    r = p.add_run(REC["title"] if filled else "[Your Title]")
    _run(r, "Calibri", 10, color=SOFT)
    p = doc.add_paragraph()
    _sp(p, before=0, after=0)
    r = p.add_run(REC["org"] if filled else "[Organization]")
    _run(r, "Calibri", 10, color=SOFT)

    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _sp(foot, before=36, after=0)
    r = foot.add_run("MathRelaxing  ·  Letter of Recommendation Pack")
    _run(r, "Georgia", 8, color=FAINT)

    doc.save(str(path))
    print(f"  {path.name}")


def build_howto_pdf(path: Path):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.6 * inch,
    )
    navy, gold, ink = HexColor(NAVY), HexColor(GOLD), HexColor(INK)
    h = ParagraphStyle("h", fontName="Times-Bold", fontSize=16, textColor=navy, alignment=1, spaceAfter=6)
    s = ParagraphStyle("s", fontName="Helvetica", fontSize=9.5, textColor=ink, leading=13, spaceAfter=6)
    b = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=10, textColor=gold, spaceBefore=10, spaceAfter=4)
    story = [
        Paragraph("How to Write a Strong Letter of Recommendation", h),
        Paragraph("MathRelaxing LOR Pack  ·  practical guide", ParagraphStyle("sub", fontName="Times-Italic", fontSize=11, textColor=gold, alignment=1, spaceAfter=10)),
        HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=12),
        Paragraph("What top Etsy packs get right (and we include)", b),
        Paragraph("• Editable <b>Word</b> templates (US Letter) — the format buyers expect<br/>"
                  "• A <b>filled sample</b> so writers see tone and length<br/>"
                  "• Multiple situations: job, academic, teacher, character, scholarship, peer<br/>"
                  "• Clear placeholders in [brackets]", s),
        Paragraph("Structure that works", b),
        Paragraph("1. <b>Open with relationship + duration</b> — how you know the person.<br/>"
                  "2. <b>One or two concrete stories with outcomes</b> — metrics beat adjectives.<br/>"
                  "3. <b>Character / collaboration</b> — how they work with others.<br/>"
                  "4. <b>Clear endorsement</b> — “I recommend without reservation.”<br/>"
                  "5. <b>Offer contact</b> — invite follow-up.", s),
        Paragraph("Length & tone", b),
        Paragraph("Aim for <b>three-quarters to one page</b>. Warm but specific. Avoid vague praise (“hard worker,” “team player”) unless you prove it with an example.", s),
        Paragraph("Which template to use", b),
        Paragraph("• <b>Job / Employee</b> — managers recommending reports for a new role<br/>"
                  "• <b>Academic / Grad school</b> — faculty or research advisors<br/>"
                  "• <b>Teacher → Student</b> — high school / college instructors<br/>"
                  "• <b>Character / Personal</b> — housing, personal opportunities (not legal advice)<br/>"
                  "• <b>Scholarship</b> — awards and foundations<br/>"
                  "• <b>Coworker / Peer</b> — lateral recommendations", s),
        Paragraph("Important", b),
        Paragraph("These are writing aids, not legal documents. For court, immigration, or formal legal references, consult appropriate counsel. Do not invent credentials or experiences.", s),
        Paragraph(brand.COPYRIGHT, ParagraphStyle("f", fontName="Helvetica", fontSize=8, textColor=HexColor(FAINT), spaceBefore=14)),
    ]
    doc.build(story)
    print(f"  {path.name}")


# ── Previews ─────────────────────────────────────────────────────────────────

def _font(size, bold=False):
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


def _sans(size, bold=False):
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


def _save(img, name):
    path = PREVIEWS / name
    img.resize((1500, 1500), Image.Resampling.LANCZOS).save(path, quality=92)
    print(f"  {name}")
    return path


def make_previews():
    S = 2000
    navy, gold, cream, soft = _rgb(NAVY), _rgb(GOLD), _rgb(CREAM), _rgb(SOFT)
    paths = []

    # 1 Hero
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 80), "LETTER OF RECOMMENDATION", font=_sans(14, True), fill=gold, anchor="mt")
    d.text((S // 2, 130), "Template Pack", font=_font(48, True), fill=cream, anchor="mt")
    d.text((S // 2, 210), "6 situations  ·  blank + sample  ·  writing guide", font=_sans(18), fill=gold, anchor="mt")
    # paper
    pw, ph = 820, 1050
    px, py = (S - pw) // 2, 300
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([px + 14, py + 18, px + pw + 14, py + ph + 18], fill=(0, 0, 0, 100))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([px, py, px + pw, py + ph], fill=cream)
    d.text((px + pw // 2, py + 50), "Dr. Amira Shah", font=_font(22, True), fill=navy, anchor="mt")
    d.text((px + pw // 2, py + 95), "Director of Research  ·  Meridian Labs", font=_font(12), fill=gold, anchor="mt")
    d.line([(px + 120, py + 140), (px + pw - 120, py + 140)], fill=gold, width=2)
    d.text((px + 80, py + 180), "March 12, 2026", font=_sans(14), fill=_rgb(INK), anchor="lt")
    d.text((px + 80, py + 240), "Dear Hiring Committee,", font=_sans(15), fill=_rgb(INK), anchor="lt")
    y = py + 300
    for _ in range(10):
        d.rectangle([px + 80, y, px + pw - 80, y + 12], fill=(220, 215, 205))
        y += 36
    d.text((px + 80, y + 20), "Sincerely,", font=_sans(15), fill=_rgb(INK), anchor="lt")
    d.text((px + 80, y + 80), "Dr. Amira Shah", font=_font(16, True), fill=navy, anchor="lt")
    d.rectangle([0, S - 90, S, S], fill=(8, 10, 22))
    d.text((S // 2, S - 45), "MathRelaxing  ·  Editorial letterheads, not plain Times", font=_sans(17), fill=gold, anchor="mm")
    paths.append(_save(img, "lor_preview_1_hero.jpg"))

    # 2 Six types
    img = Image.new("RGB", (S, S), cream)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 60), "Six real situations", font=_font(36, True), fill=navy, anchor="mt")
    d.text((S // 2, 120), "Competitors sell one letter. You get a system.", font=_sans(17), fill=gold, anchor="mt")
    cards = [
        ("01", "Job / Employee", "Manager recommending\na report for a new role"),
        ("02", "Academic", "Faculty / research advisor\nfor grad school"),
        ("03", "Teacher → Student", "College, scholarship,\nor program support"),
        ("04", "Character", "Personal reference\nfor housing & more"),
        ("05", "Scholarship", "Awards and foundation\nnominations"),
        ("06", "Coworker / Peer", "Lateral recommendation\nfrom a teammate"),
    ]
    cw, ch = 560, 420
    gap = 40
    x0 = (S - 3 * cw - 2 * gap) // 2
    y0 = 200
    for i, (num, title, sub) in enumerate(cards):
        c, r = i % 3, i // 3
        x = x0 + c * (cw + gap)
        y = y0 + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=12, fill=navy)
        d.ellipse([x + 30, y + 30, x + 100, y + 100], outline=gold, width=3)
        d.text((x + 65, y + 65), num, font=_font(18, True), fill=gold, anchor="mm")
        d.text((x + 36, y + 140), title, font=_font(24, True), fill=cream, anchor="lt")
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 36, y + 220 + j * 40), line, font=_sans(17), fill=gold, anchor="lt")
    d.rectangle([0, S - 90, S, S], fill=navy)
    d.text((S // 2, S - 45), "Blank template + filled sample for each", font=_sans(17), fill=cream, anchor="mm")
    paths.append(_save(img, "lor_preview_2_types.jpg"))

    # 3 vs competitors
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "Why this pack wins", font=_font(36, True), fill=cream, anchor="mt")
    rows = [
        ("Typical Etsy listing", "1 generic Word file · $2–5\nPlain black text · no sample"),
        ("MathRelaxing pack", "6 situations · blank + sample\nEditorial letterhead · writing guide"),
        ("Cross-sell ready", "Pairs with Atelier / Editorial\nresume kits you already sell"),
    ]
    y = 200
    for title, body in rows:
        d.rounded_rectangle([140, y, S - 140, y + 380], radius=14, outline=gold, width=2)
        d.text((200, y + 50), title, font=_font(26, True), fill=gold, anchor="lt")
        for j, line in enumerate(body.split("\n")):
            d.text((200, y + 140 + j * 50), line, font=_sans(22), fill=cream, anchor="lt")
        y += 420
    d.rectangle([0, S - 90, S, S], fill=(8, 10, 22))
    d.text((S // 2, S - 45), "eRank: rising demand  ·  KD 1  ·  thin competition", font=_sans(16), fill=gold, anchor="mm")
    paths.append(_save(img, "lor_preview_3_why.jpg"))

    # 4 Detail letter
    img = Image.new("RGB", (S, S), (228, 224, 216))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([200, 180, 1800, 1620], radius=8, fill=cream)
    d.text((1000, 260), "Dr. Amira Shah", font=_font(28, True), fill=navy, anchor="mt")
    d.text((1000, 320), "Director of Research  ·  Meridian Labs", font=_font(16), fill=gold, anchor="mt")
    d.line([(500, 380), (1500, 380)], fill=gold, width=2)
    d.text((320, 440), "March 12, 2026", font=_sans(16), fill=_rgb(INK), anchor="lt")
    d.text((320, 520), "Dear Hiring Committee,", font=_sans(18), fill=_rgb(INK), anchor="lt")
    body = (
        "I am pleased to recommend Celine Mora for a senior research leadership role. "
        "She directed a seven-person pod whose work shaped product bets representing roughly $18M in ARR influence."
    )
    # wrap roughly
    words = body.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) > 62:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    y = 600
    for line in lines:
        d.text((320, y), line, font=_sans(17), fill=_rgb(INK), anchor="lt")
        y += 40
    d.text((320, y + 40), "Sincerely,", font=_sans(18), fill=_rgb(INK), anchor="lt")
    d.text((320, y + 120), "Dr. Amira Shah", font=_font(18, True), fill=navy, anchor="lt")
    d.rectangle([0, S - 90, S, S], fill=navy)
    d.text((S // 2, S - 45), "Specific praise  ·  metrics  ·  clear endorsement", font=_sans(17), fill=gold, anchor="mm")
    paths.append(_save(img, "lor_preview_4_detail.jpg"))

    # 5 What's included
    img = Image.new("RGB", (S, S), cream)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 70), "What's included", font=_font(40, True), fill=navy, anchor="mt")
    items = [
        "6 Word templates (US Letter)",
        "6 filled SAMPLE letters",
        "Editorial navy / gold letterhead",
        "How-to writing guide (PDF)",
        "Job · Academic · Teacher · Character",
        "Scholarship · Coworker / Peer",
        "Instant digital download",
        "Personal-use license",
    ]
    y = 200
    for item in items:
        d.rounded_rectangle([280, y, S - 280, y + 140], radius=10, outline=navy, width=2)
        d.ellipse([320, y + 45, 380, y + 105], outline=gold, width=3)
        d.text((420, y + 70), item, font=_sans(24), fill=navy, anchor="lm")
        y += 170
    d.rectangle([0, S - 90, S, S], fill=navy)
    d.text((S // 2, S - 45), "$7.99  ·  One pack, every common recommendation", font=_sans(18), fill=gold, anchor="mm")
    paths.append(_save(img, "lor_preview_5_included.jpg"))

    # 6 Value / SEO
    img = Image.new("RGB", (S, S), navy)
    d = ImageDraw.Draw(img)
    d.text((S // 2, 100), "Built for people who write letters", font=_font(32, True), fill=cream, anchor="mt")
    d.text((S // 2, 180), "not for people who sell one blank page", font=_sans(18), fill=gold, anchor="mt")
    stats = [("6", "Letter types"), ("12", "Word files"), ("1", "Writing guide"), ("$7.99", "Fair kit price")]
    for i, (n, lab) in enumerate(stats):
        c, r = i % 2, i // 2
        x = 200 + c * 850
        y = 320 + r * 550
        d.rounded_rectangle([x, y, x + 750, y + 450], radius=16, outline=gold, width=2)
        d.text((x + 375, y + 140), n, font=_font(56, True), fill=gold, anchor="mt")
        d.text((x + 375, y + 280), lab, font=_sans(24), fill=cream, anchor="mt")
    paths.append(_save(img, "lor_preview_6_value.jpg"))
    return paths


def build_zip():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (TEMPLATES, SAMPLES):
            for p in folder.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(OUT).as_posix())
    print(f"ZIP {ZIP_PATH.name} ({ZIP_PATH.stat().st_size / 1024:.0f} KB)")


def main():
    _ensure()
    print("=== Letter of Recommendation Pack ===")
    print("Research gap: multi-situation pack + editorial letterhead + samples")
    for key in LETTERS:
        base = LETTERS[key]["filename"]
        build_letter(TEMPLATES / f"{base}_Template.docx", key, filled=False)
        build_letter(TEMPLATES / f"{base}_SAMPLE.docx", key, filled=True)
    build_howto_pdf(SAMPLES / "HOW_TO_WRITE_LOR.pdf")
    print("Previews…")
    make_previews()
    build_zip()
    print("DONE →", OUT)


if __name__ == "__main__":
    main()
