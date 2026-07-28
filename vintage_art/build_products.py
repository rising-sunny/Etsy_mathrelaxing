"""
build_products.py — production assets for the Vintage Math Art print sets
=========================================================================
Two digital-download products, each a set of 6 designs delivered as
print-ready JPGs in multiple aspect ratios (300 dpi), plus gallery previews.

  products:
    maurer_rose   — 6 rosettes (n,d)
    phyllotaxis   — 6 golden-angle sunflowers

  outputs (per product, under vintage_art/products/<slug>/):
    prints/<design>_<ratio>.jpg        -> zipped into <Name>_Set6.zip
    preview_<i>.jpg (watermarked)      -> Etsy gallery images
    hero.jpg, whatyouget.jpg           -> Etsy gallery images

    python vintage_art/build_products.py
"""
from pathlib import Path
import zipfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PROD = BASE / "products"
FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
SERIF = str(FONT_DIR / "DejaVuSerif.ttf")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")

IVORY = (0.937, 0.912, 0.842)
IVORY_RGB = tuple(int(c * 255) for c in IVORY)
INK = (0.16, 0.11, 0.07)
INK_RGB = tuple(int(c * 255) for c in INK)
GOLD = (0.647, 0.494, 0.204)
GOLD_RGB = tuple(int(c * 255) for c in GOLD)

# portrait print ratios, longest side 6000 px @300dpi
RATIOS = {"4x5": (4800, 6000), "3x4": (4500, 6000),
          "2x3": (4000, 6000), "ISO": (4243, 6000)}

rng = np.random.default_rng(21)

MAURER = [(2, 39), (3, 79), (5, 97), (6, 71), (7, 19), (13, 37)]
PHYLLO = [137.508, 137.3, 137.7, 137.1, 138.0, 99.501]


# ── art rendering (transparent square PNG) ───────────────────────────────────
def _art_fig():
    fig = plt.figure(figsize=(6, 6), dpi=720)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_aspect("equal")
    ax.patch.set_alpha(0)
    return fig, ax


def _ring(ax):
    th = np.linspace(0, 2 * np.pi, 600)
    for rr, a in ((1.2, 0.55), (1.17, 0.38)):
        ax.plot(rr * np.cos(th), rr * np.sin(th), color=INK, lw=0.9, alpha=a)


def render_maurer(nd, path):
    n, d = nd
    fig, ax = _art_fig()
    k = np.arange(0, 361); th = np.radians(k * d); r = np.sin(n * th)
    ax.plot(r * np.cos(th), r * np.sin(th), color=INK, lw=0.5, alpha=0.55)
    tt = np.linspace(0, 2 * np.pi, 2400); rr = np.sin(n * tt)
    ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=GOLD, lw=1.7, alpha=0.9)
    _ring(ax)
    fig.savefig(path, transparent=True, dpi=720); plt.close(fig)


def render_phyllo(ang, path, seeds=2200):
    fig, ax = _art_fig()
    i = np.arange(1, seeds + 1)
    ga = np.radians(ang)
    r = 1.02 / np.sqrt(seeds) * np.sqrt(i)
    th = i * ga
    x, y = r * np.cos(th), r * np.sin(th)
    sizes = 3 + 26 * (i / seeds) ** 1.3
    gm = (i % 5 == 0)
    ax.scatter(x[~gm], y[~gm], s=sizes[~gm], c=[INK], alpha=0.82, edgecolors="none")
    ax.scatter(x[gm], y[gm], s=sizes[gm], c=[GOLD], alpha=0.88, edgecolors="none")
    _ring(ax)
    fig.savefig(path, transparent=True, dpi=720); plt.close(fig)


# ── aged-paper ground (numpy low-res -> PIL upscale, cached per size) ─────────
_PAPER_CACHE = {}


def make_paper(W, H):
    if (W, H) in _PAPER_CACHE:
        return _PAPER_CACHE[(W, H)].copy()
    img = _make_paper(W, H)
    _PAPER_CACHE[(W, H)] = img
    return img.copy()


def _make_paper(W, H):
    long = 1400
    if W >= H:
        w0, h0 = long, max(1, round(long * H / W))
    else:
        h0, w0 = long, max(1, round(long * W / H))
    base = np.ones((h0, w0, 3)) * np.array(IVORY)
    grain = rng.normal(0, 1, (h0, w0))
    grain = (grain - grain.min()) / (grain.max() - grain.min())
    base *= (0.965 + 0.05 * grain)[..., None]
    yy, xx = np.mgrid[0:h0, 0:w0]
    for _ in range(int(0.0004 * w0 * h0)):
        cx, cy = rng.uniform(0, w0), rng.uniform(0, h0); rr = rng.uniform(4, 14)
        blot = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / rr ** 2) * rng.uniform(0.05, 0.12)
        base *= (1 - blot[..., None] * np.array([0.35, 0.45, 0.6]))
    cx, cy = w0 / 2, h0 / 2
    rad = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2)
    vig = np.clip(1 - 0.18 * rad ** 2.6, 0, 1)[..., None]
    edge = np.array([0.62, 0.55, 0.44])
    base = base * vig + edge * (1 - vig) * 0.5
    img = Image.fromarray(np.clip(base * 255, 0, 255).astype("uint8"), "RGB")
    return img.resize((W, H), Image.LANCZOS)


def compose(art_path, size, out_path, art_frac=0.9, watermark=False, quality=90):
    W, H = size
    paper = make_paper(W, H)
    art = Image.open(art_path).convert("RGBA")
    target = int(min(W, H) * art_frac)
    art = art.resize((target, target), Image.LANCZOS)
    paper.paste(art, ((W - target) // 2, (H - target) // 2), art)
    if watermark:
        _watermark(paper)
    paper.save(out_path, "JPEG", quality=quality)


def _watermark(img):
    W, H = img.size
    diag = int((W ** 2 + H ** 2) ** 0.5)
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(SERIF, int(W * 0.032))
    txt = "MATHRELAXING  ·  PREVIEW"
    tw = d.textbbox((0, 0), txt, font=f)[2]
    step_x = int(tw * 1.35)
    step_y = int(W * 0.16)
    for j, yy in enumerate(range(0, diag, step_y)):
        off = (j % 2) * (step_x // 2)                 # brick offset
        for xx in range(-step_x, diag, step_x):
            d.text((xx + off, yy), txt, font=f, fill=(120, 105, 80, 55))
    layer = layer.rotate(30, resample=Image.BICUBIC, center=(diag // 2, diag // 2))
    crop = layer.crop(((diag - W) // 2, (diag - H) // 2,
                       (diag - W) // 2 + W, (diag - H) // 2 + H))
    img.paste(Image.alpha_composite(img.convert("RGBA"), crop).convert("RGB"), (0, 0))


# ── gallery cards ────────────────────────────────────────────────────────────
def hero_card(art_paths, title, subtitle, out):
    W, H = 2000, 1900
    img = make_paper(W, H)
    d = ImageDraw.Draw(img)
    tf = ImageFont.truetype(SERIF_B, 100)
    sf = ImageFont.truetype(SERIF, 46)
    _center(d, title.upper(), tf, W, 74, INK_RGB)
    _center(d, subtitle, sf, W, 208, GOLD_RGB)
    cols = 3
    cell = 610; gx = (W - cols * cell) // 2; gy = 330
    for idx, ap in enumerate(art_paths):
        r, c = divmod(idx, cols)
        thumb = Image.open(ap).convert("RGBA").resize((cell - 30, cell - 30), Image.LANCZOS)
        img.paste(thumb, (gx + c * cell + 15, gy + r * cell + 15), thumb)
    _logo(img, W // 2, H - 95, 360)
    img.save(out, "JPEG", quality=92)


def whatyouget_card(title, out):
    W, H = 2000, 2500
    img = make_paper(W, H)
    d = ImageDraw.Draw(img)
    tf = ImageFont.truetype(SERIF_B, 92)
    hf = ImageFont.truetype(SERIF_B, 60)
    bf = ImageFont.truetype(SANS, 46)
    _center(d, "WHAT YOU GET", tf, W, 130, INK_RGB)
    _center(d, title, ImageFont.truetype(SERIF, 46), W, 250, GOLD_RGB)
    lines = [
        "• 6 original designs — hand-coded math art, no AI, no stock",
        "• 4 print ratios each (24 files): 4:5, 3:4, 2:3 and ISO / A-series",
        "• High resolution — 6000 px long edge (300 dpi at 20 in)",
        "• Instant download — 4 ZIP files (one per ratio); nothing shipped",
        "",
        "HOW TO PRINT",
        "• Home printer, local print shop, or online (Printful, etc.)",
        "• Choose the ratio that matches your frame; scale to any size",
        "",
        "© MathRelaxing. For personal use only. Not for resale.",
    ]
    y = 470
    for ln in lines:
        font = hf if ln.isupper() and ln else bf
        d.text((190, y), ln, font=font, fill=INK_RGB if ln else INK_RGB)
        y += 118 if (ln.isupper() and ln) else 96
    _logo(img, W // 2, H - 110, 380)
    img.save(out, "JPEG", quality=92)


def _center(d, text, font, W, y, fill):
    w = d.textbbox((0, 0), text, font=font)[2]
    d.text(((W - w) // 2, y), text, font=font, fill=fill)


def _logo(img, cx, cy, width):
    logo = Image.open(ROOT / "mathrelaxing_logo.png").convert("RGBA")
    h = int(width * logo.height / logo.width)
    logo = logo.resize((width, h), Image.LANCZOS)
    img.paste(logo, (cx - width // 2, cy - h // 2), logo)


# ── product build ────────────────────────────────────────────────────────────
def build(slug, name, subtitle, designs, render_fn):
    pdir = PROD / slug
    prints = pdir / "prints"
    prints.mkdir(parents=True, exist_ok=True)
    art_dir = pdir / "_art"; art_dir.mkdir(exist_ok=True)
    print(f"\n=== {name} ===")

    art_paths = []
    for idx, params in enumerate(designs, 1):
        ap = art_dir / f"design_{idx}.png"
        render_fn(params, ap)
        art_paths.append(ap)
        for rname, size in RATIOS.items():
            compose(ap, size, prints / f"{slug}_{idx:02d}_{rname}.jpg", art_frac=0.9)
        print(f"  design {idx}: prints done")

    # zip
    zpath = pdir / f"{name.replace(' ', '')}_Set6.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for jp in sorted(prints.glob("*.jpg")):
            z.write(jp, arcname=f"{name}/{jp.name}")
        z.writestr(f"{name}/README.txt",
                   f"{name} — MathRelaxing\n\n6 designs x 4 ratios (4:5, 3:4, 2:3, ISO) at 300 dpi.\n"
                   "Print at home or any print shop; pick the ratio matching your frame.\n\n"
                   "(c) MathRelaxing. For personal use only. Not for redistribution or resale.\n")
    print(f"  zip -> {zpath.name}  ({zpath.stat().st_size/1e6:.1f} MB)")

    # gallery previews (watermarked 4:5)
    for idx, ap in enumerate(art_paths, 1):
        compose(ap, (1600, 2000), pdir / f"preview_{idx:02d}.jpg",
                art_frac=0.9, watermark=True, quality=88)
    hero_card(art_paths, name, subtitle, pdir / "hero.jpg")
    whatyouget_card(name, pdir / "whatyouget.jpg")
    print("  previews + hero + whatyouget done")
    return zpath


if __name__ == "__main__":
    build("maurer_rose", "Maurer Rose", "vintage mathematical line art · set of 6",
          MAURER, render_maurer)
    build("phyllotaxis", "Phyllotaxis", "golden-ratio spiral art · set of 6",
          PHYLLO, lambda p, path: render_phyllo(p, path))
    print("\nDONE")
