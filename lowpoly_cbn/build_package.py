"""
build_package.py — assemble the test package: a branded multi-page PDF with a
cover, N geometric color-by-number pages (one per generative-art piece), a
divider, and the full-colour solutions. Everything digital / Etsy-ready.

    python build_package.py     # -> pkg_out/MathColorByNumber_Vol1.pdf (+ preview PNGs)
"""
import os
from PIL import Image, ImageDraw

import art_gallery
from lowpoly_core import generate_cbn, _font, _centered_text, LETTER_PX

HERE = os.path.dirname(os.path.abspath(__file__))
DARK = (26, 29, 36)
GOLD = (200, 169, 81)
CREAM = (244, 240, 226)


def _text_page(lines):
    """A branded full-page (dark) with centered stacked lines: (text, size, color)."""
    img = Image.new("RGB", LETTER_PX, DARK)
    d = ImageDraw.Draw(img)
    m = 60
    d.rectangle([m, m, LETTER_PX[0] - m, LETTER_PX[1] - m], outline=GOLD, width=6)
    total = sum(sz for _, sz, _ in lines) + (len(lines) - 1) * 40
    y = (LETTER_PX[1] - total) / 2
    for text, size, color in lines:
        _centered_text(d, text, LETTER_PX[0] / 2, y + size / 2, _font(size), color)
        y += size + 40
    return img


def build(out_dir=None, cell_scale=1.0):
    out_dir = out_dir or os.path.join(HERE, "pkg_out")
    os.makedirs(out_dir, exist_ok=True)
    src_dir = os.path.join(HERE, "pkg_src")
    pieces = art_gallery.build_all(src_dir)

    coloring_pages, colored_pages = [], []
    for p in pieces:
        info = generate_cbn(p["src"], out_dir,
                            poly_type="triangular",
                            side_length=int(p["side"] * cell_scale),
                            num_colors=p["colors"],
                            title=f"MathRelaxing   ·   {p['title']}")
        coloring_pages.append(Image.open(info["coloring"]).convert("RGB"))
        colored_pages.append(Image.open(info["colored"]).convert("RGB"))
        print(f"  {p['title']:22} {info['cells']:>5} cells, {p['colors']} colors")

    cover = _text_page([
        ("MATH", 150, CREAM),
        ("COLOR BY NUMBER", 110, GOLD),
        ("Generative Art · Low-Poly Edition", 46, CREAM),
        (f"{len(pieces)} printable pages  ·  full-colour solutions", 34, GOLD),
        ("MathRelaxing", 40, CREAM),
    ])
    divider = _text_page([("SOLUTIONS", 130, GOLD),
                          ("full-colour reference for every page", 40, CREAM)])

    pages = [cover] + coloring_pages + [divider] + colored_pages
    pdf_path = os.path.join(out_dir, "MathColorByNumber_Vol1.pdf")
    pages[0].save(pdf_path, "PDF", save_all=True, append_images=pages[1:], resolution=300)
    # a couple of flat previews too
    cover.save(os.path.join(out_dir, "preview_cover.png"))
    print(f"\nPDF: {pdf_path}  ({len(pages)} pages, {os.path.getsize(pdf_path)/1e6:.1f} MB)")
    return pdf_path


if __name__ == "__main__":
    build()
