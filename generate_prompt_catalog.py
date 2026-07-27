"""
generate_prompt_catalog.py — editorial PDF catalog of the teacher prompt library
=================================================================================
Reads ai_teacher_prompts/prompts.json (extracted from prompt_studio.html — the
single source of truth) and builds a print-ready PDF booklet plus Etsy previews,
in the same editorial style as the interactive tool: warm paper, serif display,
hairline rules, brick-red 'marking pen' accent, {{fields}} shown as [blanks].

  node ai_teacher_prompts/extract_prompts.js   # refresh prompts.json first
  python generate_prompt_catalog.py
"""
from __future__ import annotations
import json, re, zipfile
from pathlib import Path
import img2pdf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
DIR = BASE / "ai_teacher_prompts"
FONTS = BASE / "lulu_books" / "assets" / "fonts"
BUILD = Path("/tmp/claude-0/-home-user-Etsy-mathrelaxing/e24b7ec7-cf86-5f97-890f-aa4cef39fee4/scratchpad/cat_pages")
BUILD.mkdir(parents=True, exist_ok=True)

W, H = 2550, 3300
MX = 210
TOP = 250
BOT = H - 230

PAPER="#F3F2EC"; PANEL="#FBFAF5"; INK="#1b1a17"; INK_SOFT="#46443e"; MUTED="#8b867a"
RULE="#ded9cc"; RULE_STRONG="#c6c0b0"; ACCENT="#b23a2e"

def hx(c): return tuple(int(c[i:i+2],16) for i in (1,3,5))
def f(name,size): return ImageFont.truetype(str(FONTS/name), size)
DISP=lambda s: f("Cinzel-SemiBold.ttf", s)
HEAD=lambda s: f("Cinzel.ttf", s)
BODY=lambda s: f("Raleway.ttf", s)
ITAL=lambda s: f("Raleway-Italic.ttf", s)

prompts = json.loads((DIR/"prompts.json").read_text())
# category order as first appearance
CATS=[]
for p in prompts:
    if p["cat"] not in CATS: CATS.append(p["cat"])


class Book:
    def __init__(self):
        self.pages=[]; self._new()
    def _new(self):
        self.im=Image.new("RGB",(W,H),hx(PAPER)); self.d=ImageDraw.Draw(self.im); self.y=TOP
        self.pages.append(self.im)
    def footer(self, running):
        d=self.d
        d.line((MX,H-165,W-MX,H-165),fill=hx(RULE),width=2)
        d.text((MX,H-128),"THE PROMPT STUDIO",font=BODY(28),fill=hx(MUTED),anchor="lm")
        d.text((W-MX,H-128),running,font=BODY(28),fill=hx(MUTED),anchor="rm")
    def space(self, h, running="", new_divider=None):
        if self.y+h>BOT:
            self.footer(running); self._new()
            if new_divider: new_divider()
    def rule(self, color=RULE_STRONG, pad=18, w=1):
        self.y+=pad; self.d.line((MX,self.y,W-MX,self.y),fill=hx(color),width=w); self.y+=pad


SANITIZE={"→":"->","⇒":"=>","×":"x","≤":"<=","≥":">=","≠":"!="}
def san(s):
    for a,b in SANITIZE.items(): s=s.replace(a,b)
    return s

def wrap_rich(d, line, fields_map, font, fill, accent, x0, width, line_h, book, running):
    """Draw one source line with {{tokens}} as [Label] in accent; word-wrapped.
    Handles pagination via book.space()."""
    line=san(line)
    parts=re.split(r"(\{\{\w+\}\})", line)
    words=[]
    for part in parts:
        m=re.match(r"\{\{(\w+)\}\}", part)
        if m:
            words.append(("["+fields_map.get(m.group(1),m.group(1))+"]", accent))
        else:
            for w in part.split(" "):
                if w!="": words.append((w, fill))
    space_w=d.textlength(" ",font=font)
    cur=[]; curw=0
    def flush():
        nonlocal cur,curw
        book.space(line_h, running)
        d2=book.d; xx=x0
        for i,(w,c,ww) in enumerate(cur):
            if i>0: xx+=space_w
            d2.text((xx,book.y),w,font=font,fill=hx(c)); xx+=ww
        book.y+=line_h; cur=[]; curw=0
    for (w,c) in words:
        ww=d.textlength(w,font=font)
        if cur and curw+space_w+ww>width:
            flush()
        cur.append((w,c,ww)); curw+=(space_w if len(cur)>1 else 0)+ww
    if cur: flush()


def draw_paragraph(book, template, fields_map, running):
    font=BODY(33); line_h=50; x0=MX+46; width=W-MX-x0
    for raw in template.split("\n"):
        if raw.strip()=="":
            book.y+=line_h*0.55; continue
        # accent left rule segment drawn per line for a continuous blockquote feel
        y_start=book.y
        wrap_rich(book.d, raw, fields_map, font, INK, ACCENT, x0, width, line_h, book, running)
        book.d.line((MX+8,y_start-4,MX+8,book.y-line_h+38),fill=hx(RULE_STRONG),width=3)


def prompt_card(book, p, num):
    running=p["cat"]
    fields_map={fld["k"]: re.sub(r" —.*","",fld["l"]) for fld in p["fields"]}
    # keep header block together
    book.space(230, running)
    d=book.d
    d.text((MX,book.y),f"{num:02d}",font=HEAD(34),fill=hx(MUTED),anchor="lm")
    d.text((MX+90,book.y),p["cat"].upper(),font=BODY(24),fill=hx(ACCENT),anchor="lm")
    book.y+=54
    d.text((MX+90,book.y),san(p["title"]),font=DISP(46),fill=hx(INK),anchor="lm"); book.y+=64
    d.text((MX+90,book.y),san(p["desc"]),font=ITAL(34),fill=hx(INK_SOFT),anchor="lm"); book.y+=70
    draw_paragraph(book, p["tpl"], fields_map, running)
    book.y+=54
    d.line((MX,book.y,W-MX,book.y),fill=hx(RULE),width=2); book.y+=46


def divider(book, cat, count):
    # (previous page was already footered by the end-of-category call)
    book._new()
    d=book.d; cx=W//2
    book.y=560
    d.text((cx,book.y),f"{CATS.index(cat)+1:02d}",font=HEAD(60),fill=hx(MUTED),anchor="mm"); book.y+=140
    d.text((cx,book.y),cat.upper(),font=DISP(92),fill=hx(INK),anchor="mm"); book.y+=100
    d.line((cx-150,book.y,cx+150,book.y),fill=hx(ACCENT),width=6); book.y+=80
    d.text((cx,book.y),f"{count} prompt{'s' if count!=1 else ''}",font=ITAL(38),fill=hx(INK_SOFT),anchor="mm")
    book.y=1120  # content starts on the SAME divider page, below the section title


def spaced_center(d, cx, y, text, font, fill, track):
    widths=[d.textlength(ch,font=font) for ch in text]
    total=sum(widths)+track*(len(text)-1)
    x=cx-total/2
    for ch,w in zip(text,widths):
        d.text((x,y),ch,font=font,fill=fill,anchor="lm"); x+=w+track

def cover(book):
    d=book.d; cx=W//2
    spaced_center(d,cx,560,"A TEACHER'S AI TOOLKIT",BODY(34),hx(ACCENT),10)
    d.line((cx-360,620,cx+360,620),fill=hx(ACCENT),width=3)
    d.text((cx,940),"The Prompt",font=DISP(190),fill=hx(INK),anchor="mm")
    d.text((cx,1150),"Studio",font=DISP(190),fill=hx(INK),anchor="mm")
    d.text((cx,1360),"84 expert, fill-in-the-blank prompts for planning, assessment,",font=ITAL(42),fill=hx(INK_SOFT),anchor="mm")
    d.text((cx,1420),"feedback, communication, SEL & STEM.",font=ITAL(42),fill=hx(INK_SOFT),anchor="mm")
    # category list
    y=1720
    d.text((cx,y),"INSIDE",font=BODY(30),fill=hx(MUTED),anchor="mm"); y+=70
    for i in range(0,len(CATS),2):
        row=CATS[i:i+2]
        txt="     ·     ".join(c for c in row)
        d.text((cx,y),txt,font=DISP(40),fill=hx(INK),anchor="mm"); y+=76
    d.text((cx,H-360),"Works with ChatGPT · Claude · Gemini",font=BODY(34),fill=hx(INK_SOFT),anchor="mm")
    d.text((cx,H-300),"Includes the interactive offline prompt builder",font=ITAL(34),fill=hx(ACCENT),anchor="mm")
    # frame
    d.rectangle((90,90,W-90,H-90),outline=hx(RULE_STRONG),width=3)


def howto(book):
    book._new(); d=book.d
    book.y=TOP+40
    d.text((MX,book.y),"HOW TO USE",font=BODY(30),fill=hx(ACCENT),anchor="lm"); book.y+=70
    d.text((MX,book.y),"From prompt to precise result",font=DISP(72),fill=hx(INK),anchor="lm"); book.y+=60
    book.rule()
    steps=[
        ("Pick a prompt","Browse by category or use the interactive builder (open the included HTML file)."),
        ("Fill the blanks","Replace every [bracket] with your subject, grade, topic and context."),
        ("Copy & paste","Paste the completed prompt into ChatGPT, Claude or Gemini."),
        ("Refine","Ask a follow-up if you want it shorter, simpler, or in a different format."),
        ("Always review","You are the expert — edit the AI's output to fit your students before using it."),
    ]
    book.y+=30
    for i,(t,s) in enumerate(steps,1):
        d.ellipse((MX,book.y,MX+84,book.y+84),outline=hx(ACCENT),width=5)
        d.text((MX+42,book.y+42),str(i),font=HEAD(44),fill=hx(ACCENT),anchor="mm")
        d.text((MX+140,book.y+8),t,font=DISP(46),fill=hx(INK),anchor="lm")
        d.text((MX+140,book.y+66),s,font=BODY(33),fill=hx(INK_SOFT),anchor="lm")
        book.y+=200
    book.y+=20
    d.line((MX,book.y,W-MX,book.y),fill=hx(RULE_STRONG),width=2); book.y+=50
    note=("Why brackets, not a fillable PDF? A single instruction the AI can act on beats a form. "
          "Every prompt gives the AI an expert role, your context, a required output format, and a "
          "teaching framework — that is what makes the results precise and classroom-ready.")
    wrap_rich(book.d, note, {}, ITAL(34), INK_SOFT, ACCENT, MX, W-2*MX, 52, book, "How to use")
    book.footer("How to use")


def build():
    book=Book()
    cover(book)
    howto(book)
    # per category
    for cat in CATS:
        items=[p for p in prompts if p["cat"]==cat]
        divider(book, cat, len(items))
        n=1
        for p in items:
            prompt_card(book, p, n); n+=1
        book.footer(cat)
    return book.pages


def save_pdf(pages):
    paths=[]
    for i,im in enumerate(pages,1):
        pth=BUILD/f"p{i:03d}.jpg"; im.convert("RGB").save(pth,"JPEG",quality=94,dpi=(300,300),subsampling=0); paths.append(pth)
    pdf=DIR/"The_Prompt_Studio_84_Teacher_Prompts.pdf"
    layout=img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5),img2pdf.in_to_pt(11)))
    with open(pdf,"wb") as fh:
        fh.write(img2pdf.convert([str(p) for p in paths],layout_fun=layout))
    print(f"  PDF {pdf.name} ({pdf.stat().st_size//1024} KB, {len(pages)} pages)")
    return pdf, pages


def previews(pages):
    prev=DIR/"previews"; prev.mkdir(parents=True,exist_ok=True); S=2000
    bg=(240,239,232); paths=[]
    def pf(sz,disp=False,ital=False):
        return f("Cinzel-SemiBold.ttf" if disp else ("Raleway-Italic.ttf" if ital else "Raleway.ttf"),sz)
    def mock(page,title,sub,fname):
        c=Image.new("RGB",(S,S),bg); d=ImageDraw.Draw(c)
        d.text((S//2,80),title,font=pf(44,True),fill=hx(ACCENT),anchor="mt")
        d.text((S//2,150),sub,font=pf(30,ital=True),fill=hx(INK_SOFT),anchor="mt")
        pg=page.copy(); sc=1500/pg.height; pg=pg.resize((int(pg.width*sc),1500),Image.Resampling.LANCZOS)
        x,y=(S-pg.width)//2,240
        sh=Image.new("RGBA",(S,S),(0,0,0,0))
        ImageDraw.Draw(sh).rectangle([x+14,y+18,x+pg.width+14,y+pg.height+18],fill=(0,0,0,70))
        c=Image.alpha_composite(c.convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(20))).convert("RGB")
        c.paste(pg,(x,y))
        ImageDraw.Draw(c).text((S//2,S-58),"Instant download · PDF + interactive tool",font=pf(28),fill=hx(MUTED),anchor="mt")
        p=prev/fname; c.resize((1500,1500),Image.Resampling.LANCZOS).save(p,quality=92); paths.append(p)
    # find a STEM divider page and a sample content page
    mock(pages[0],"THE PROMPT STUDIO","84 expert prompts for teachers","aiprompts_preview_1_cover.jpg")
    mock(pages[3],"BROWSE BY CATEGORY","11 categories, fill-in-the-blank prompts","aiprompts_preview_2_pages.jpg")
    # STEM divider: search pages list index by rendering? just use a late page
    mock(pages[-6],"A DEDICATED STEM BATCH","Math · science · engineering · coding","aiprompts_preview_3_stem.jpg")

    # included card
    c=Image.new("RGB",(S,S),hx(INK)); d=ImageDraw.Draw(c)
    d.text((S//2,120),"What's included",font=pf(54,True),fill=(244,242,236),anchor="mt")
    items=["84 expert teacher prompts","11 categories incl. a STEM batch",
           "Interactive offline prompt builder (HTML)","Print-ready PDF catalog · US Letter",
           "Works with ChatGPT, Claude & Gemini"]
    y=330
    for it in items:
        d.rounded_rectangle([190,y,S-190,y+160],radius=10,outline=hx(ACCENT),width=3)
        d.text((260,y+80),it,font=pf(30),fill=(233,232,226),anchor="lm"); y+=200
    p=prev/"aiprompts_preview_4_included.jpg"; c.resize((1500,1500),Image.Resampling.LANCZOS).save(p,quality=92); paths.append(p)

    # thumbnail grid
    c=Image.new("RGB",(S,S),bg); d=ImageDraw.Draw(c)
    d.text((S//2,90),"A 40+ page prompt library",font=pf(44,True),fill=hx(INK),anchor="mt")
    picks=[pages[0],pages[3],pages[len(pages)//3],pages[len(pages)//2],pages[2*len(pages)//3],pages[-2]]
    tw=560; x0=(S-3*tw-2*60)//2; y0=250; gap=60
    for i,tp in enumerate(picks):
        gx=x0+(i%3)*(tw+gap); gy=y0+(i//3)*(int(tw*11/8.5)+gap)
        th=tp.resize((tw,int(tw*11/8.5)),Image.Resampling.LANCZOS); c.paste(th,(gx,gy))
        d.rectangle((gx,gy,gx+tw,gy+int(tw*11/8.5)),outline=hx(RULE_STRONG),width=3)
    p=prev/"aiprompts_preview_5_grid.jpg"; c.resize((1500,1500),Image.Resampling.LANCZOS).save(p,quality=92); paths.append(p)
    print(f"  {len(paths)} previews")
    return paths


def build_zip(pdf):
    z=DIR/"the_prompt_studio_kit.zip"
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf,pdf.name)
        zf.write(DIR/"prompt_studio.html","Prompt_Studio_interactive_tool.html")
        zf.writestr("READ_ME.txt",
            "The Prompt Studio — A Teacher's AI Toolkit\n\n"
            "INCLUDED\n"
            "  The_Prompt_Studio_84_Teacher_Prompts.pdf  — printable catalog of all 84 prompts\n"
            "  Prompt_Studio_interactive_tool.html       — open in any browser; pick a prompt,\n"
            "                                              fill the blanks, click Copy. Works offline.\n\n"
            "HOW TO USE\n"
            "  Replace every [bracket] with your details, then paste into ChatGPT, Claude or Gemini.\n"
            "  You are the expert — always review and edit the AI's output before using it with students.\n\n"
            "Original, curated teaching prompts. Personal / single-classroom use. Not for resale.\n")
    print(f"  ZIP {z.name} ({z.stat().st_size//1024} KB)")
    return z


def main():
    print("=== The Prompt Studio — PDF catalog ===")
    pages=build()
    pdf,pages=save_pdf(pages)
    previews(pages)
    build_zip(pdf)
    print("DONE →", DIR)


if __name__=="__main__":
    main()
