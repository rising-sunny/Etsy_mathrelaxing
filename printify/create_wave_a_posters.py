"""
create_wave_a_posters.py — physical POD twins of best-viewed digital posters
(research 2026-10-10, block A):

  golden     Golden Ratio / Fibonacci scientific plate (wallart_set concept "golden")
  equations  "The Great Equations" — the 6 Famous Equations plates on one poster

Same product recipe as the Navier-Stokes / Ulam posters that sell:
blueprint 282 x provider 99, 3 ratio masters (2x3, 3x4, 4x5), 9 sizes $15–$59.

  python printify/create_wave_a_posters.py build            # masters + previews only
  python printify/create_wave_a_posters.py create [key...]  # upload + create in Printify (NOT published)
  python printify/create_wave_a_posters.py publish ID...    # push to Etsy (draft)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "wallart_set"))
OUT = os.path.join(HERE, "_wave_a_art")
PLATES = os.path.join(ROOT, "equation_plates", "famous_equations_set", "prints")

# ratio tag -> (width_px, height_px) at 6000 px tall (300 dpi @ 20 in)
MASTERS = {"2x3": (4000, 6000), "3x4": (4500, 6000), "4x5": (4800, 6000)}
# Printify variant -> master it uses (same grouping as the live posters)
VARIANT_MASTER = {
    43138: "2x3", 101113: "2x3", 43147: "2x3", 43150: "2x3",   # 12x18 16x24 20x30 24x36
    101110: "3x4", 43144: "3x4", 101118: "3x4",                # 12x16 18x24 30x40
    43135: "4x5", 43141: "4x5",                                # 11x14 16x20
}
PRICES = {43135: 1500, 43138: 1800, 101110: 1800, 43141: 2400, 101113: 2400,
          43144: 2600, 43147: 3200, 43150: 3900, 101118: 5900}
SHIPPING_TEMPLATE_HINT = "312767497404"  # Navier-Stokes listing (set by Printify)

EQ_ORDER = ["fourier_series", "wave_equation", "dirac_equation",
            "navier_stokes", "euler_identity", "mandelbrot_set"]
PAPER = (244, 241, 234)
INK = (26, 26, 26)
ACC = (184, 92, 56)

PRODUCTS = {
    "golden": dict(
        title="Golden Ratio Poster, Fibonacci Spiral | Math Wall Art, Phi Scientific Plate | Matte Print",
        tags=["golden ratio", "fibonacci spiral", "matte poster", "math wall art", "phi poster",
              "science poster", "stem wall art", "math teacher gift", "office wall art",
              "nerd gift", "minimalist poster", "educational poster", "study room decor"],
        description=(
            "The Golden Ratio — φ = (1 + √5) / 2 ≈ 1.618 — drawn as a scientific plate: the "
            "Fibonacci rectangle tiling, the golden spiral and the convergence of consecutive "
            "Fibonacci ratios to phi. Generated with code, typeset like a vintage science "
            "textbook figure.\n\n"
            "PHYSICAL PRINT — this is a printed matte poster shipped to your door (not a download).\n\n"
            "• Museum-style matte paper, 300 dpi artwork\n"
            "• Sizes from 11×14\" to 30×40\"\n"
            "• Frame not included\n"
            "• Printed and shipped by our print partner in the US\n\n"
            "A thoughtful gift for math teachers, engineers, architects, designers and anyone "
            "who loves the hidden geometry of nature."
        ),
    ),
    "equations": dict(
        title="Famous Equations Poster | Fourier, Dirac, Euler, Navier-Stokes Math Physics Wall Art | Matte Print",
        tags=["equation poster", "physics poster", "math wall art", "matte poster",
              "famous equations", "science poster", "stem wall art", "physics gift",
              "math teacher gift", "engineer gift", "office wall art", "nerd gift",
              "classroom decor"],
        description=(
            "The Great Equations — six landmark equations of mathematics and physics on one "
            "poster, each drawn as a scientific plate with its diagram:\n"
            "1. Fourier Series — square-wave harmonics\n"
            "2. Wave Equation — standing modes\n"
            "3. Dirac Equation — matter and antimatter\n"
            "4. Navier–Stokes — flow past a cylinder\n"
            "5. Euler's Identity — the unit circle\n"
            "6. Mandelbrot Set — z → z² + c\n\n"
            "PHYSICAL PRINT — this is a printed matte poster shipped to your door (not a download).\n\n"
            "• Museum-style matte paper, 300 dpi artwork\n"
            "• Sizes from 11×14\" to 30×40\" (larger sizes recommended to read every plate)\n"
            "• Frame not included\n"
            "• Printed and shipped by our print partner in the US\n\n"
            "A gift for physicists, engineers, math teachers and graduates."
        ),
    ),
}


def _font(size, bold=False):
    for name in (("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"),):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def build_golden():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import concept_poster as cp
    paths = {}
    for tag, (w, h) in MASTERS.items():
        fig = cp.render("golden", w / 300, h / 300, dpi=300)
        path = os.path.join(OUT, f"golden_ratio_{tag}.jpg")
        fig.savefig(path, facecolor=cp.PAPER, dpi=300)
        plt.close(fig)
        paths[tag] = path
    return paths


def build_equations():
    """6 plates (2:3 each) on one page: 3x2 grid under a title band."""
    plates = [Image.open(os.path.join(PLATES, f"{k}_2x3_300dpi.jpg")).convert("RGB")
              for k in EQ_ORDER]
    paths = {}
    for tag, (W, H) in MASTERS.items():
        page = Image.new("RGB", (W, H), PAPER)
        d = ImageDraw.Draw(page)
        margin, gutter = int(W * 0.045), int(W * 0.022)
        cols, rows = 3, 2
        cell_w = (W - 2 * margin - (cols - 1) * gutter) // cols
        cell_h = int(cell_w * 1.5)
        grid_h = rows * cell_h + (rows - 1) * gutter
        band = H - 2 * margin - grid_h  # space left for the title
        if band < H * 0.08:  # 2x3 page is too short for a band at this width → shrink grid
            cell_h = int((H - 2 * margin - int(H * 0.1) - gutter) / rows)
            cell_w = cell_h * 2 // 3
            grid_h = rows * cell_h + gutter
            band = H - 2 * margin - grid_h
        grid_w = cols * cell_w + (cols - 1) * gutter
        x0 = (W - grid_w) // 2
        # tall pages leave a huge band: cap it and split the surplus above/below
        surplus = max(0, band - int(H * 0.16))
        band -= surplus
        margin += surplus // 2
        y0 = margin + band
        # title band
        title, sub = "THE GREAT EQUATIONS", "SIX LANDMARKS OF MATHEMATICS & PHYSICS"
        t_size = int(band * 0.30)
        while d.textlength(title, font=_font(t_size, bold=True)) > grid_w * 0.92:
            t_size -= 4
        t_font = _font(t_size, bold=True)
        s_font = _font(int(t_size * 0.38))
        tw = d.textlength(title, font=t_font)
        d.text(((W - tw) / 2, margin + band * 0.18), title, font=t_font, fill=INK)
        sw = d.textlength(sub, font=s_font)
        d.text(((W - sw) / 2, margin + band * 0.58), sub, font=s_font, fill=ACC)
        for i, pl in enumerate(plates):
            r, c = divmod(i, cols)
            x = x0 + c * (cell_w + gutter)
            y = y0 + r * (cell_h + gutter)
            page.paste(pl.resize((cell_w, cell_h), Image.LANCZOS), (x, y))
            d.rectangle([x - 2, y - 2, x + cell_w + 1, y + cell_h + 1], outline=(200, 195, 185), width=3)
        path = os.path.join(OUT, f"great_equations_{tag}.jpg")
        page.save(path, quality=95, dpi=(300, 300))
        paths[tag] = path
    return paths


BUILDERS = {"golden": build_golden, "equations": build_equations}


def build(keys):
    os.makedirs(OUT, exist_ok=True)
    out = {}
    for k in keys:
        out[k] = BUILDERS[k]()
        prev = Image.open(out[k]["4x5"])
        prev.thumbnail((900, 1125))
        prev.save(os.path.join(OUT, f"_preview_{k}.jpg"), quality=88)
        print(k, {t: Image.open(p).size for t, p in out[k].items()})
    return out


def create(keys):
    import printify_publish as pp
    masters = build(keys)
    created = {}
    for k in keys:
        spec = PRODUCTS[k]
        img_ids = {t: pp.upload_image(p) for t, p in masters[k].items()}
        payload = {
            "title": spec["title"],
            "description": spec["description"],
            "blueprint_id": pp.BLUEPRINT_MATTE,
            "print_provider_id": pp.PROVIDER_CHOICE,
            "variants": [{"id": v, "price": p, "is_enabled": True} for v, p in PRICES.items()],
            "print_areas": [
                {"variant_ids": [v for v, t in VARIANT_MASTER.items() if t == tag],
                 "placeholders": [{"position": "front", "images": [
                     {"id": img_ids[tag], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}
                for tag in MASTERS
            ],
            "tags": spec["tags"],
        }
        prod = pp._req("POST", f"/shops/{pp.SHOP_ID}/products.json", payload)
        created[k] = prod["id"]
        print(f"\n{k}: Printify product {prod['id']} (NOT published)")
        pp.margin_report(prod)
    with open(os.path.join(OUT, "created.json"), "w") as f:
        json.dump(created, f, indent=2)
    return created


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    keys = sys.argv[2:] or list(BUILDERS)
    if cmd == "build":
        build(keys)
    elif cmd == "create":
        create(keys)
    elif cmd == "publish":
        import printify_publish as pp
        for pid in sys.argv[2:]:
            print(pid, pp.publish_product(pid))
    else:
        print(__doc__)
