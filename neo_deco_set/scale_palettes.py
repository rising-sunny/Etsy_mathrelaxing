"""Package + publish one Neo Deco *palette* set (all three motifs on a single
jewel ground) as its own Etsy digital listing.

Masters are expected at masters/<palette>/{01_sunburst,02_arches,03_rosette}.png
(rendered by `generate_neo_deco.py <palette>`).

  python scale_palettes.py ruby onyx amethyst           # build packages
  python scale_palettes.py --publish ruby onyx amethyst  # build + Etsy drafts...
  (note: create_draft_listing makes them active on this shop; see README)
"""
import os, sys, zipfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE); sys.path.insert(0, REPO)
import build_package as BP   # reuse wall/frame/shadow/paste_framed/font/crop_ratio

NAMES = ["01_sunburst", "02_arches", "03_rosette"]
TITLES = ["Sunburst", "Arch Portal", "Rose Window"]
S = BP.S
GOLD = BP.GOLD

PAL_LABEL = {"ruby": "Ruby", "onyx": "Onyx & Gold", "amethyst": "Amethyst",
             "emerald": "Emerald", "sapphire": "Sapphire", "midnight": "Midnight"}


def pal_dir(pal):
    return os.path.join(HERE, "masters", pal)


def master(pal, i):
    return Image.open(os.path.join(pal_dir(pal), f"{NAMES[i]}.png")).convert("RGB")


def hero(pal, prev):
    c = BP.wall(S, S, (223, 217, 207)); d = ImageDraw.Draw(c)
    d.rectangle((0, int(S * 0.82), S, S), fill=(205, 197, 185))
    d.line((0, int(S * 0.82), S, int(S * 0.82)), fill=(150, 143, 130), width=3)
    th = int(S * 0.40); xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]
    for x, i in zip(xs, range(3)):
        BP.paste_framed(c, master(pal, i), x, int(S * 0.44), th, fw=18, mat=0)
    d.text((S // 2, int(S * 0.93)), f"N E O   D E C O   ·   {PAL_LABEL[pal].upper()}",
           font=BP.font("Cinzel-SemiBold.ttf", 38), fill=(70, 66, 60), anchor="mm")
    c.save(os.path.join(prev, "01_hero.jpg"), quality=92)


def single(pal, i, prev):
    c = BP.wall(S, S, (226, 220, 210))
    BP.paste_framed(c, master(pal, i), S // 2, int(S * 0.47), int(S * 0.72), fw=30)
    ImageDraw.Draw(c).text((S // 2, int(S * 0.95)), TITLES[i].upper(),
                           font=BP.font("Cinzel-SemiBold.ttf", 34), fill=(80, 76, 70), anchor="mm")
    c.save(os.path.join(prev, f"0{i+2}_{NAMES[i][3:]}.jpg"), quality=92)


def grid(pal, prev):
    c = Image.new("RGB", (S, S), (18, 20, 24)); d = ImageDraw.Draw(c)
    d.text((S // 2, int(S * 0.07)), f"NEO DECO · {PAL_LABEL[pal].upper()}",
           font=BP.font("Cinzel-SemiBold.ttf", 60), fill=(232, 226, 214), anchor="mm")
    d.text((S // 2, int(S * 0.135)), "three metallic Art-Deco prints · set of 3",
           font=BP.font("Raleway-Italic.ttf", 30), fill=(150, 145, 134), anchor="mm")
    tw = int(S * 0.29); th = int(tw * 1.5); y = int(S * 0.22)
    xs = [int(S * 0.19), int(S * 0.5), int(S * 0.81)]
    for x, i in zip(xs, range(3)):
        im = master(pal, i).resize((tw, th), Image.LANCZOS); bx = x - tw // 2
        BP.shadow(c, (bx, y, bx + tw, y + th), blur=22, alpha=140); c.paste(im, (bx, y))
        d.rectangle((bx, y, bx + tw, y + th), outline=GOLD, width=3)
    d.text((S // 2, int(S * 0.93)), "instant download · 300 DPI",
           font=BP.font("Raleway.ttf", 28), fill=(150, 145, 134), anchor="mm")
    c.save(os.path.join(prev, "05_grid.jpg"), quality=93)


def prints_zip(pal):
    prin = os.path.join(pal_dir(pal), "prints"); os.makedirs(prin, exist_ok=True)
    files = []
    for i, n in enumerate(NAMES):
        m = master(pal, i)
        for tag, im in [("2x3", m), ("4x5", BP.crop_ratio(m, 4, 5)),
                        ("ISO_A", BP.crop_ratio(m, 1, 1.4142))]:
            p = os.path.join(prin, f"{pal}_{n}_{tag}_300dpi.jpg")
            im.save(p, quality=95, dpi=(300, 300)); files.append(p)
    z = os.path.join(pal_dir(pal), f"Neo_Deco_{PAL_LABEL[pal].split()[0]}_Set.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, os.path.join(f"Neo_Deco_{pal}", os.path.basename(f)))
        zf.writestr(f"Neo_Deco_{pal}/READ_ME.txt",
                    f"NEO DECO - {PAL_LABEL[pal]} set (MathRelaxing)\n"
                    "3 metallic Art-Deco prints, 2:3 / 4:5 / ISO A, 300 DPI JPEG.\n")
    return z


def build_pkg(pal):
    prev = os.path.join(pal_dir(pal), "previews"); os.makedirs(prev, exist_ok=True)
    hero(pal, prev)
    for i in range(3):
        single(pal, i, prev)
    grid(pal, prev)
    z = prints_zip(pal)
    # a review contact-sheet
    ims = [master(pal, i) for i in range(3)]
    tw = 700; th = int(tw * 1.5); pad = 30
    sheet = Image.new("RGB", (3 * tw + 4 * pad, th + 2 * pad), (24, 26, 30))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + i * (tw + pad), pad))
    sheet.save(os.path.join(pal_dir(pal), "_sheet.jpg"), quality=90)
    print(f"packaged {pal}: previews + prints + {os.path.basename(z)}")
    return prev, z


def publish(pal, prev, zip_path):
    os.chdir(REPO)
    import etsy_manager
    m = etsy_manager.EtsyManager()
    label = PAL_LABEL[pal]
    title = (f"Neo Deco {label} Set of 3 | Art Deco Wall Art Printable | Metallic "
             f"Geometric Prints | Gatsby Gallery Wall Digital Download")[:140]
    tags = ["neo deco", "art deco print", "art deco wall art", f"{pal} wall art"[:20],
            "geometric wall art", "gold geometric art", "gatsby decor", "jewel tone art",
            "gallery wall set", "luxury wall art", "printable wall art", "set of 3 prints",
            "maximalist wall art"]
    tags = [t for t in tags if len(t) <= 20][:13]
    desc = (f"NEO DECO — {label} — a set of three metallic Art-Deco prints (instant download)\n\n"
            "Old-world glamour reimagined for 2026: brushed gold and platinum foil geometry "
            f"with emerald jewel accents on a deep {label.lower()} ground. A rising Sunburst, a "
            "nested Arch Portal, and a radiant Rose Window — generated from exact geometry.\n\n"
            "— WHAT YOU GET —\n"
            "- 3 high-resolution digital prints (JPEG, 300 DPI)\n"
            "- Each in THREE ratios: 2:3, 4:5 and ISO / A-size\n"
            "- 2:3 prints 4x6 up to 24x36 in; 4:5 at 8x10/16x20; A5-A1\n"
            "- Instant download — no physical item is shipped\n\n"
            "For personal use. Designed and generated by MathRelaxing.")
    lid = m.create_draft_listing(title, desc, 14.00, 2078, is_digital=True, quantity=999, tags=tags)
    imgs = ["01_hero.jpg", "05_grid.jpg", "02_sunburst.jpg", "03_arches.jpg", "04_rosette.jpg"]
    for rank, fn in enumerate(imgs, 1):
        p = os.path.join(prev, fn)
        if os.path.exists(p):
            try: m.upload_listing_image(lid, p, rank=rank)
            except Exception as e: print("  img err", fn, str(e)[:100])
    try: m.upload_listing_file(lid, zip_path)
    except Exception as e: print("  file err", str(e)[:100])
    print(f"  {pal}: listing {lid} -> https://www.etsy.com/listing/{lid}")
    return lid


if __name__ == "__main__":
    args = sys.argv[1:]
    do_pub = "--publish" in args
    pals = [a for a in args if not a.startswith("--")]
    for pal in pals:
        prev, z = build_pkg(pal)
        if do_pub:
            publish(pal, prev, z)
