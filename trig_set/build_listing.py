"""Package + publish the Trigonometry scientific-plate Set of 6 as an Etsy
digital listing (portrait 2:3). `--publish` creates the listing.

  python build_listing.py            # build package
  python build_listing.py --publish
"""
import os, sys, zipfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
MAST = os.path.join(HERE, "masters")
PREV = os.path.join(HERE, "previews"); os.makedirs(PREV, exist_ok=True)
PRIN = os.path.join(HERE, "prints"); os.makedirs(PRIN, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "neo_deco_set")); sys.path.insert(0, REPO)
import build_package as BP

SLUGS = ["unit_circle", "sine_cosine", "right_triangle", "identities", "laws", "tangent"]
NAMES = ["The Unit Circle", "Sine & Cosine", "Right Triangle", "Trig Identities",
         "Laws of Triangles", "Tangent"]
S = BP.S; GOLD = BP.GOLD


def master(k):
    return Image.open(os.path.join(MAST, f"trig_{k}.png")).convert("RGB")


def hero():
    c = BP.wall(S, S, (223, 218, 209)); d = ImageDraw.Draw(c)
    th = int(S * 0.345); xs = [int(S * 0.2), int(S * 0.5), int(S * 0.8)]; ys = [int(S * 0.30), int(S * 0.63)]
    for i, k in enumerate(SLUGS):
        r, col = divmod(i, 3); BP.paste_framed(c, master(k), xs[col], ys[r], th, fw=12)
    d.text((S // 2, int(S * 0.95)), "T R I G O N O M E T R Y   ·   S E T   O F   6",
           font=BP.font("Cinzel-SemiBold.ttf", 33), fill=(70, 66, 60), anchor="mm")
    c.save(os.path.join(PREV, "01_hero.jpg"), quality=92); print("01_hero")


def grid():
    c = Image.new("RGB", (S, S), (244, 241, 234)); d = ImageDraw.Draw(c)
    d.text((S // 2, int(S * 0.06)), "TRIGONOMETRY", font=BP.font("Cinzel-SemiBold.ttf", 60),
           fill=(26, 28, 32), anchor="mm")
    d.text((S // 2, int(S * 0.115)), "six classroom plates · unit circle to laws",
           font=BP.font("Raleway-Italic.ttf", 30), fill=(120, 116, 108), anchor="mm")
    tw = int(S * 0.28); th = int(tw * 1.5); ys = [int(S * 0.17), int(S * 0.55)]
    xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]
    for i, k in enumerate(SLUGS):
        r, col = divmod(i, 3); bx = xs[col] - tw // 2; by = ys[r]
        c.paste(master(k).resize((tw, th), Image.LANCZOS), (bx, by))
        d.rectangle((bx, by, bx + tw, by + th), outline=(206, 198, 182), width=2)
    d.text((S // 2, int(S * 0.95)), "instant download · 300 DPI · 2:3",
           font=BP.font("Raleway.ttf", 26), fill=(120, 116, 108), anchor="mm")
    c.save(os.path.join(PREV, "02_grid.jpg"), quality=93); print("02_grid")


def single(i, dst):
    c = BP.wall(S, S, (224, 219, 210))
    BP.paste_framed(c, master(SLUGS[i]), S // 2, int(S * 0.47), int(S * 0.74), fw=22)
    ImageDraw.Draw(c).text((S // 2, int(S * 0.95)), NAMES[i].upper(),
                           font=BP.font("Cinzel-SemiBold.ttf", 30), fill=(80, 76, 70), anchor="mm")
    c.save(os.path.join(PREV, dst), quality=92); print(dst)


def info():
    c = Image.new("RGB", (S, S), (255, 255, 255)); d = ImageDraw.Draw(c)
    d.rectangle((44, 44, S - 44, S - 44), outline=(47, 111, 126), width=4)
    d.text((S // 2, 150), "WHAT YOU GET", font=BP.font("Cinzel-SemiBold.ttf", 60), fill=(26, 28, 32), anchor="mm")
    for j, ln in enumerate([
        "- 6 high-resolution digital prints (JPEG, 300 DPI)",
        "- 2:3 ratio - prints 8x12, 12x18, 16x24, 20x30, 24x36 in",
        "- Unit Circle, Sine & Cosine, Right Triangle (SOHCAHTOA),",
        "   Identities, Laws of Sines & Cosines, Tangent",
        "- Instant download - no physical item is shipped",
        "- Great for a classroom, study or math gallery wall",
    ]):
        d.text((150, 320 + j * 86), ln, font=BP.font("Raleway.ttf", 33), fill=(52, 56, 66))
    d.text((S // 2, S - 150), "MathRelaxing", font=BP.font("Cinzel-SemiBold.ttf", 40), fill=(47, 111, 126), anchor="mm")
    c.save(os.path.join(PREV, "09_info.jpg"), quality=93); print("09_info")


def prints_zip():
    files = []
    for k in SLUGS:
        p = os.path.join(PRIN, f"trig_{k}_2x3_300dpi.jpg")
        master(k).save(p, quality=92, dpi=(300, 300)); files.append(p)
    zips = []
    for part, ks in [(1, files[:3]), (2, files[3:])]:
        z = os.path.join(HERE, f"Trigonometry_Set_of_6_part{part}.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in ks:
                zf.write(f, os.path.join("Trigonometry_Set_of_6", os.path.basename(f)))
            zf.writestr("Trigonometry_Set_of_6/READ_ME.txt",
                        "TRIGONOMETRY - Set of 6 (MathRelaxing)\n6 scientific-plate prints, 2:3, 300 DPI JPEG.\n"
                        "Instant download. Personal / single-classroom use.\n")
        print(f"zip part{part}", os.path.getsize(z) // 1024, "KB"); zips.append(z)
    return zips


def build_pkg():
    hero(); grid()
    single(0, "03_unit_circle.jpg"); single(1, "04_sine_cosine.jpg"); single(3, "05_identities.jpg")
    single(4, "06_laws.jpg"); single(2, "07_triangle.jpg"); single(5, "08_tangent.jpg")
    info()
    return prints_zip()


TITLE = ("Trigonometry Poster Set of 6 | Unit Circle, Identities, Graphs and Laws | "
         "Math Classroom Wall Art Printable | Digital Download")
TAGS = ["trigonometry poster", "unit circle poster", "math classroom decor", "trig identities",
        "precalculus poster", "high school math", "math teacher gift", "algebra 2 poster",
        "sohcahtoa poster", "math wall art", "educational poster", "printable wall art",
        "set of 6 prints"]
DESC = """TRIGONOMETRY — a set of six scientific-plate prints (instant download)

A clean, classroom-ready trig reference set in a warm graph-paper "scientific
plate" style: the Unit Circle, Sine & Cosine graphs, the Right Triangle
(SOHCAHTOA), the essential Identities, the Laws of Sines & Cosines, and Tangent
with its asymptotes. Every graph is computed from the mathematics.

— WHAT YOU GET —
- 6 high-resolution digital prints (JPEG, 300 DPI, 2:3)
- Prints at 8x12, 12x18, 16x24, 20x30, 24x36 in
- Instant download — no physical item is shipped

— PERFECT FOR —
A math classroom, a tutor's wall, a student's study, or a precalculus / algebra 2
gift. Single-classroom / personal use. Designed and generated by MathRelaxing."""


def publish(zips):
    os.chdir(REPO)
    import etsy_manager
    m = etsy_manager.EtsyManager()
    assert len(TITLE) <= 140, len(TITLE)
    lid = m.create_draft_listing(TITLE, DESC, 12.99, 2078, is_digital=True, quantity=999, tags=TAGS)
    imgs = ["01_hero.jpg", "02_grid.jpg", "03_unit_circle.jpg", "04_sine_cosine.jpg",
            "05_identities.jpg", "06_laws.jpg", "07_triangle.jpg", "08_tangent.jpg", "09_info.jpg"]
    for rank, fn in enumerate(imgs, 1):
        p = os.path.join(PREV, fn)
        if os.path.exists(p):
            try: m.upload_listing_image(lid, p, rank=rank)
            except Exception as e: print("  img err", fn, str(e)[:100])
    for z in zips:
        try: m.upload_listing_file(lid, z); print("  file", os.path.basename(z))
        except Exception as e: print("  file err", os.path.basename(z), str(e)[:100])
    print(f"listing {lid} -> https://www.etsy.com/listing/{lid}")
    return lid


if __name__ == "__main__":
    zs = build_pkg()
    if "--publish" in sys.argv:
        publish(zs)
