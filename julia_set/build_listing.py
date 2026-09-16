"""Package + publish the Julia Set (of 6) as an Etsy digital listing.
Square art -> square previews/prints. `--publish` creates the listing.

  python build_listing.py            # build package only
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

SLUGS = ["dragon", "rabbit", "spiral", "dense", "swirl", "pinwheel"]
NAMES = ["Dragon", "Douady Rabbit", "Spiral", "Filament", "Swirl", "Pinwheel"]
S = BP.S; GOLD = BP.GOLD


def master(k):
    return Image.open(os.path.join(MAST, f"julia_{k}.png")).convert("RGB")


def hero():
    c = BP.wall(S, S, (222, 217, 208)); d = ImageDraw.Draw(c)
    th = int(S * 0.30); xs = [int(S * 0.22), int(S * 0.5), int(S * 0.78)]; ys = [int(S * 0.30), int(S * 0.64)]
    for i, k in enumerate(SLUGS):
        r, col = divmod(i, 3); BP.paste_framed(c, master(k), xs[col], ys[r], th, fw=13)
    d.text((S // 2, int(S * 0.95)), "J U L I A   S E T   ·   S E T   O F   6",
           font=BP.font("Cinzel-SemiBold.ttf", 34), fill=(70, 66, 60), anchor="mm")
    c.save(os.path.join(PREV, "01_hero.jpg"), quality=92); print("01_hero")


def grid():
    c = Image.new("RGB", (S, S), (12, 12, 22)); d = ImageDraw.Draw(c)
    d.text((S // 2, int(S * 0.065)), "JULIA SET", font=BP.font("Cinzel-SemiBold.ttf", 66),
           fill=(238, 234, 226), anchor="mm")
    d.text((S // 2, int(S * 0.125)), "six fractals · z -> z² + c",
           font=BP.font("Raleway-Italic.ttf", 30), fill=(150, 160, 190), anchor="mm")
    tw = int(S * 0.27); ys = [int(S * 0.19), int(S * 0.55)]
    xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]
    for i, k in enumerate(SLUGS):
        r, col = divmod(i, 3); bx = xs[col] - tw // 2; by = ys[r]
        c.paste(master(k).resize((tw, tw), Image.LANCZOS), (bx, by))
        d.rectangle((bx, by, bx + tw, by + tw), outline=GOLD, width=2)
        d.text((xs[col], by + tw + 20), NAMES[i], font=BP.font("Cinzel.ttf", 24),
               fill=(214, 210, 202), anchor="mm")
    d.text((S // 2, int(S * 0.95)), "instant download · 300 DPI · square",
           font=BP.font("Raleway.ttf", 26), fill=(150, 160, 190), anchor="mm")
    c.save(os.path.join(PREV, "02_grid.jpg"), quality=93); print("02_grid")


def single(i, dst):
    c = BP.wall(S, S, (224, 219, 210))
    BP.paste_framed(c, master(SLUGS[i]), S // 2, int(S * 0.46), int(S * 0.62), fw=22)
    ImageDraw.Draw(c).text((S // 2, int(S * 0.93)), NAMES[i].upper(),
                           font=BP.font("Cinzel-SemiBold.ttf", 32), fill=(80, 76, 70), anchor="mm")
    c.save(os.path.join(PREV, dst), quality=92); print(dst)


def info():
    c = Image.new("RGB", (S, S), (244, 241, 234)); d = ImageDraw.Draw(c)
    d.rectangle((40, 40, S - 40, S - 40), outline=GOLD, width=4)
    d.text((S // 2, 150), "WHAT YOU GET", font=BP.font("Cinzel-SemiBold.ttf", 60), fill=(26, 28, 32), anchor="mm")
    for j, ln in enumerate([
        "- 6 high-resolution digital prints (JPEG, 300 DPI)",
        "- Square format - for square frames",
        "- Prints beautifully at 8x8, 10x10, 12x12, 16x16, 20x20 in",
        "- Instant download - no physical item is shipped",
        "- Each mark computed from z -> z² + c (no AI)",
        "- Personal use - print at home or any print shop",
    ]):
        d.text((175, 320 + j * 88), ln, font=BP.font("Raleway.ttf", 33), fill=(52, 48, 42))
    d.text((S // 2, S - 150), "MathRelaxing", font=BP.font("Cinzel-SemiBold.ttf", 40), fill=GOLD, anchor="mm")
    c.save(os.path.join(PREV, "09_info.jpg"), quality=93); print("09_info")


def prints_zip():
    files = []
    for k in SLUGS:
        p = os.path.join(PRIN, f"julia_{k}_square_300dpi.jpg")
        master(k).save(p, quality=92, dpi=(300, 300)); files.append(p)
    zips = []
    for part, ks in [(1, files[:3]), (2, files[3:])]:
        z = os.path.join(HERE, f"Julia_Set_of_6_part{part}.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in ks:
                zf.write(f, os.path.join("Julia_Set_of_6", os.path.basename(f)))
            zf.writestr("Julia_Set_of_6/READ_ME.txt",
                        "JULIA SET - Set of 6 (MathRelaxing)\n6 fractal prints, square, 300 DPI JPEG.\n"
                        "Instant download. Personal use.\n")
        print(f"zip part{part}", os.path.getsize(z) // 1024, "KB"); zips.append(z)
    return zips


def build_pkg():
    hero(); grid()
    single(1, "03_rabbit.jpg"); single(3, "04_dense.jpg"); single(5, "05_pinwheel.jpg")
    single(0, "06_dragon.jpg"); single(4, "07_swirl.jpg"); single(2, "08_spiral.jpg")
    info()
    return prints_zip()


TITLE = ("Julia Set Fractal Art Set of 6 | Vibrant Math Wall Art Printable | Chaos "
         "Fractal Prints | Science Gallery Wall Digital Download")
TAGS = ["julia set art", "fractal wall art", "fractal art print", "math wall art",
        "chaos theory art", "science wall art", "generative art", "vibrant wall art",
        "mathematical art", "geometric wall art", "set of 6 prints", "modern wall art",
        "abstract fractal"]
DESC = """JULIA SET — a set of six fractal prints (instant download)

The Julia sets: iterate z -> z² + c across the complex plane and colour every
point by how it escapes to infinity. Each of these six uses a different constant
c — the Douady Rabbit, a dragon, spirals, dendrites and a pinwheel — giving six
utterly different infinitely-detailed forms, in a vibrant electric palette.
Every pixel is computed from the equation, not drawn and not AI.

— WHAT YOU GET —
- 6 high-resolution digital prints (JPEG, 300 DPI, square)
- Prints at 8x8, 10x10, 12x12, 16x16, 20x20 in
- Instant download — no physical item is shipped

— PERFECT FOR —
A study, lab, office or a bold modern gallery wall; a gift for mathematicians,
physicists and lovers of chaos and fractals.

For personal use. Designed and generated by MathRelaxing."""


def publish(zips):
    os.chdir(REPO)
    import etsy_manager
    m = etsy_manager.EtsyManager()
    assert len(TITLE) <= 140, len(TITLE)
    lid = m.create_draft_listing(TITLE, DESC, 16.99, 2078, is_digital=True, quantity=999, tags=TAGS)
    imgs = ["01_hero.jpg", "02_grid.jpg", "03_rabbit.jpg", "04_dense.jpg", "05_pinwheel.jpg",
            "06_dragon.jpg", "07_swirl.jpg", "08_spiral.jpg", "09_info.jpg"]
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
