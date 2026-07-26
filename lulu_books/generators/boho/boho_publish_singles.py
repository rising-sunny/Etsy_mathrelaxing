"""Package + publish one DRAFT Etsy listing per palette (single-palette sets).
For each of sage/mustard/noir/blush: build a ZIP (3 PNGs + size guide) and 5
listing images, then create the draft ($9.99, digital)."""
import os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/user/Etsy_mathrelaxing")
os.chdir("/home/user/Etsy_mathrelaxing")
import etsy_manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_boho as B
import build_boho_package as BP

H = BP.HERE
PRICE = 9.99
TAXONOMY = 2078

META = {
    "sage": dict(name="Sage Green",
        title="Set of 3 Sage Green Boho Botanical Wall Art | Printable Abstract Line Art | Mid Century Prints | Instant Download",
        tags=["sage green art","boho wall art","botanical print","set of 3 prints","printable wall art","abstract line art","mid century art","green wall art","boho decor","minimalist print","gallery wall set","neutral wall art","instant download"]),
    "mustard": dict(name="Mustard Yellow",
        title="Set of 3 Mustard Yellow Boho Botanical Wall Art | Printable Ochre Abstract Line Art | Mid Century Prints | Instant Download",
        tags=["mustard wall art","ochre art print","boho wall art","botanical print","set of 3 prints","printable wall art","abstract line art","mid century art","yellow wall art","boho decor","gallery wall set","minimalist print","instant download"]),
    "noir": dict(name="Black and Cream",
        title="Set of 3 Black and Cream Boho Botanical Wall Art | Printable Abstract Line Art | Minimalist Mid Century Prints | Instant Download",
        tags=["black and cream art","black wall art","boho wall art","botanical print","set of 3 prints","printable wall art","abstract line art","mid century art","monochrome art","minimalist print","gallery wall set","neutral wall art","instant download"]),
    "blush": dict(name="Blush Pink",
        title="Set of 3 Blush Pink Boho Botanical Wall Art | Printable Dusty Rose Abstract Line Art | Mid Century Prints | Instant Download",
        tags=["blush pink art","dusty rose print","boho wall art","botanical print","set of 3 prints","printable wall art","abstract line art","mid century art","pink wall art","boho decor","gallery wall set","minimalist print","instant download"]),
}


def desc(name):
    return f"""SET OF 3 — BOHO BOTANICAL WALL ART · {name.upper()} (Printable)
Minimalist abstract line-art in a calm, mid-century boho style — soft shapes, botanical leaf branches and arch motifs that make an effortless gallery wall in {name.lower()} tones.

— WHAT YOU GET —
- 3 coordinated designs in {name}
- High-resolution 300 DPI PNG files, 2:3 ratio
- Fits every standard frame with no cropping — 4x6 up to 24x36 in (and A5–A2)
- A size & print guide (PDF)

— HOW IT WORKS —
1. Buy and download instantly (a ZIP file).
2. Print at home, at a local shop, or upload to a print service.
3. Frame and enjoy. Matte or textured art paper looks best.

— PLEASE NOTE —
- Digital download only — nothing is shipped.
- For personal use. Colors may vary slightly by screen and printer.

Designed by MathRelaxing."""


def framed_single(pal, i, path):
    """one panel in a wood frame centered on a warm wall (square)."""
    S = 2000; P = B.PALETTES[pal]
    top, bot = (0xdc,0xd3,0xc4), (0xcb,0xc1,0xb0)
    g = np.linspace(0,1,S)[:,None]; arr = np.zeros((S,S,3),np.uint8)
    for k in range(3): arr[:,:,k] = (top[k]*(1-g)+bot[k]*g).astype(np.uint8)
    c = Image.fromarray(arr)
    panel = BP.panels(pal)[i]
    pw = 760; ph = int(pw*3/2); fw = 26
    x = (S-pw)//2; y = (S-ph)//2
    sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle((x-fw+12, y-fw+18, x+pw+fw+12, y+ph+fw+18), fill=95)
    c.paste(Image.new("RGB", c.size, (60,52,42)), (0,0), sh.filter(ImageFilter.GaussianBlur(22)))
    ImageDraw.Draw(c).rectangle((x-fw, y-fw, x+pw+fw, y+ph+fw), fill=(196,150,96))
    ImageDraw.Draw(c).rectangle((x-4, y-4, x+pw+4, y+ph+4), outline=(150,110,70), width=2)
    c.paste(panel.resize((pw, ph), Image.LANCZOS), (x, y))
    c.save(path, quality=92)


def what_you_get(pal, path):
    S = 2000; P = B.PALETTES[pal]; name = META[pal]["name"]
    c = Image.new("RGB", (S, S), P["bg"]); d = ImageDraw.Draw(c)
    d.text((S//2, 210), "WHAT YOU GET", font=BP.font("Cinzel-SemiBold.ttf", 84), fill=P["ink"], anchor="mm")
    d.line([(S//2-230, 300),(S//2+230,300)], fill=P["fill"], width=4)
    items = [f"Set of 3 coordinated designs in {name}", "High-resolution 300 DPI, 2:3 ratio",
             "Fits 4x6 up to 24x36 in (+ A-sizes)", "3 print-ready PNG files",
             "Size & print guide (PDF)", "Instant download — print at home"]
    y = 470
    for it in items:
        d.ellipse((S//2-560, y+14, S//2-536, y+38), fill=P["fill"])
        d.text((S//2-505, y), it, font=BP.font("Raleway.ttf", 44), fill=P["ink"]); y += 100
    d.text((S//2, S-160), "MathRelaxing", font=BP.font("Cinzel.ttf", 42), fill=P["ink"], anchor="mm")
    c.save(path, quality=92)


def build_and_list(m, pal):
    meta = META[pal]; name = meta["name"]
    ld = os.path.join(H, f"listing_{pal}"); os.makedirs(ld, exist_ok=True)
    # zip
    pdf = os.path.join(BP.DEL, f"SizeGuide_{pal}.pdf"); BP.size_guide_pdf(pal, pdf)
    z = os.path.join(H, f"MathRelaxing_Boho_{pal}.zip")
    if os.path.exists(z): os.remove(z)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(3):
            zf.write(os.path.join(H, f"{pal}_panel{i+1}.png"), f"{name}/Boho_Botanical_{pal}_{i+1}.png")
        zf.write(pdf, "Size_and_Print_Guide.pdf")
    # images
    BP.wall_mockup(pal, os.path.join(ld, "01_wall.jpg"))
    BP.grid_3(pal, os.path.join(ld, "02_grid.jpg"))
    framed_single(pal, 0, os.path.join(ld, "03_single.jpg"))
    framed_single(pal, 2, os.path.join(ld, "04_single.jpg"))
    what_you_get(pal, os.path.join(ld, "05_what.jpg"))
    # listing
    T = meta["title"]; assert len(T) <= 140, f"{pal} title {len(T)}"
    lid = m.create_draft_listing(T, desc(name), PRICE, TAXONOMY, is_digital=True, quantity=999, tags=meta["tags"])
    for rank, fn in enumerate(["01_wall.jpg","02_grid.jpg","03_single.jpg","04_single.jpg","05_what.jpg"], 1):
        try: m.upload_listing_image(lid, os.path.join(ld, fn), rank=rank)
        except Exception as e: print("  img err", str(e)[:100])
    try: m.upload_listing_file(lid, z)
    except Exception as e: print("  file err", str(e)[:100])
    print(f"{pal}: draft {lid} ({len(T)} chars) https://www.etsy.com/listing/{lid}")
    return lid


def main():
    BP.PALS.update({pal: META[pal]["name"] for pal in META})  # names for captions
    m = etsy_manager.EtsyManager()
    for pal in ["sage", "mustard", "noir", "blush"]:
        build_and_list(m, pal)


if __name__ == "__main__":
    main()
