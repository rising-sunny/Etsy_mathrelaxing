"""Package + publish the "Kinetic" op-art Set of 6 as an Etsy digital listing.

  python build_listing.py            # build package only
  python build_listing.py --publish  # + create the Etsy listing
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

KEYS = ["01_vega", "02_moire", "03_vortex", "04_fall", "05_flare", "06_quanta"]
LABELS = ["Vega", "Moiré", "Vortex", "Fall", "Flare", "Quanta"]
S = BP.S; GOLD = BP.GOLD


def master(k):
    return Image.open(os.path.join(MAST, f"{k}.png")).convert("RGB")


def hero():
    c = BP.wall(S, S, (224, 219, 210)); d = ImageDraw.Draw(c)
    th = int(S * 0.30); xs = [int(S * 0.22), int(S * 0.5), int(S * 0.78)]; ys = [int(S * 0.30), int(S * 0.64)]
    for i, k in enumerate(KEYS):
        r, col = divmod(i, 3); BP.paste_framed(c, master(k), xs[col], ys[r], th, fw=13)
    d.text((S // 2, int(S * 0.95)), "K I N E T I C   ·   S E T   O F   6",
           font=BP.font("Cinzel-SemiBold.ttf", 36), fill=(70, 66, 60), anchor="mm")
    c.save(os.path.join(PREV, "01_hero.jpg"), quality=92); print("01_hero")


def grid():
    c = Image.new("RGB", (S, S), (20, 20, 24)); d = ImageDraw.Draw(c)
    d.text((S // 2, int(S * 0.065)), "KINETIC", font=BP.font("Cinzel-SemiBold.ttf", 66),
           fill=(240, 236, 228), anchor="mm")
    d.text((S // 2, int(S * 0.125)), "six optical illusions · pure geometry",
           font=BP.font("Raleway-Italic.ttf", 30), fill=(170, 166, 158), anchor="mm")
    tw = int(S * 0.27); th = int(tw * 1.5)
    xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]; ys = [int(S * 0.19), int(S * 0.55)]
    for i, k in enumerate(KEYS):
        r, col = divmod(i, 3); bx = xs[col] - tw // 2; by = ys[r]
        c.paste(master(k).resize((tw, th), Image.LANCZOS), (bx, by))
        d.rectangle((bx, by, bx + tw, by + th), outline=GOLD, width=2)
        d.text((xs[col], by + th + 22), LABELS[i], font=BP.font("Cinzel.ttf", 26),
               fill=(215, 211, 203), anchor="mm")
    d.text((S // 2, int(S * 0.95)), "instant download · 300 DPI",
           font=BP.font("Raleway.ttf", 26), fill=(170, 166, 158), anchor="mm")
    c.save(os.path.join(PREV, "02_grid.jpg"), quality=93); print("02_grid")


def single(i, dst):
    c = BP.wall(S, S, (226, 221, 212))
    BP.paste_framed(c, master(KEYS[i]), S // 2, int(S * 0.47), int(S * 0.72), fw=24)
    ImageDraw.Draw(c).text((S // 2, int(S * 0.95)), LABELS[i].upper(),
                           font=BP.font("Cinzel-SemiBold.ttf", 34), fill=(80, 76, 70), anchor="mm")
    c.save(os.path.join(PREV, dst), quality=92); print(dst)


def info():
    c = Image.new("RGB", (S, S), (244, 241, 234)); d = ImageDraw.Draw(c)
    d.rectangle((40, 40, S - 40, S - 40), outline=GOLD, width=4)
    d.text((S // 2, 150), "WHAT YOU GET", font=BP.font("Cinzel-SemiBold.ttf", 60), fill=(26, 28, 32), anchor="mm")
    for j, ln in enumerate([
        "- 6 high-resolution digital prints (JPEG, 300 DPI)",
        "- Each in THREE ratios: 2:3, 4:5 and ISO / A-size",
        "- 2:3 prints 4x6 up to 24x36 in",
        "- Instant download - no physical item is shipped",
        "- Print at home or any print shop - personal use",
    ]):
        d.text((175, 320 + j * 88), ln, font=BP.font("Raleway.ttf", 33), fill=(52, 48, 42))
    d.text((S // 2, S - 150), "MathRelaxing", font=BP.font("Cinzel-SemiBold.ttf", 40), fill=GOLD, anchor="mm")
    c.save(os.path.join(PREV, "08_info.jpg"), quality=93); print("08_info")


def prints_zip():
    per = {}
    for k in KEYS:
        m = master(k); fs = []
        for tag, im in [("2x3", m), ("4x5", BP.crop_ratio(m, 4, 5)), ("ISO_A", BP.crop_ratio(m, 1, 1.4142))]:
            p = os.path.join(PRIN, f"{k}_{tag}_300dpi.jpg"); im.save(p, quality=92, dpi=(300, 300)); fs.append(p)
        per[k] = fs
    readme = "KINETIC - Op-Art Set of 6 (MathRelaxing)\n6 optical-illusion prints, 2:3 / 4:5 / ISO A, 300 DPI JPEG.\nInstant download. Personal use.\n"
    zips = []
    for part, keys in [(1, KEYS[:3]), (2, KEYS[3:])]:
        z = os.path.join(HERE, f"Kinetic_Op_Art_Set_part{part}.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for k in keys:
                for f in per[k]:
                    zf.write(f, os.path.join("Kinetic_Op_Art_Set", os.path.basename(f)))
            zf.writestr("Kinetic_Op_Art_Set/READ_ME.txt", readme)
        print(f"zip part{part}", os.path.getsize(z) // 1024, "KB"); zips.append(z)
    return zips


def build_pkg():
    hero(); grid()
    single(2, "03_vortex.jpg"); single(0, "04_vega.jpg"); single(3, "05_fall.jpg")
    single(5, "06_quanta.jpg"); single(1, "07_moire.jpg")
    info()
    return prints_zip()


TITLE = ("Kinetic Op Art Set of 6 | Black & White Optical Illusion Wall Art Printable | "
         "Geometric Vasarely Prints | Modern Gallery Wall Download")
TAGS = ["op art print", "optical illusion", "black and white art", "geometric wall art",
        "kinetic art", "mid century modern", "abstract wall art", "modern wall art",
        "retro wall art", "monochrome art", "set of 6 prints", "statement wall art",
        "op art poster"]
DESC = """KINETIC — a set of six optical-illusion prints (instant download)

In the lineage of Victor Vasarely and Bridget Riley: high-contrast geometry that
seems to bulge, spin and vibrate on a flat page. A sphere pressed out of a grid
(Vega), a hypnotic spiral (Vortex), Riley's flowing waves (Fall), a shimmering
moiré, a radial flare and a pinched square spiral (Quanta). Every illusion is
computed from a parametric distortion field — nothing hand-drawn — so the lines
are razor-sharp at any size.

— WHAT YOU GET —
- 6 high-resolution digital prints (JPEG, 300 DPI)
- Each in THREE ratios: 2:3, 4:5 and ISO / A-size
- 2:3 prints at 4x6, 8x12, 12x18, 16x24, 20x30, 24x36 in
- Instant download — no physical item is shipped

— PERFECT FOR —
A modern living room, studio or office; a bold mid-century / retro gallery wall;
a gift for lovers of design, math and optical art.

For personal use. Designed and generated by MathRelaxing."""


def publish(zips):
    os.chdir(REPO)
    import etsy_manager
    m = etsy_manager.EtsyManager()
    assert len(TITLE) <= 140, len(TITLE)
    assert TITLE.count("&") <= 1
    lid = m.create_draft_listing(TITLE, DESC, 17.99, 2078, is_digital=True, quantity=999, tags=TAGS)
    imgs = ["01_hero.jpg", "02_grid.jpg", "03_vortex.jpg", "04_vega.jpg", "05_fall.jpg",
            "06_quanta.jpg", "07_moire.jpg", "08_info.jpg"]
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
