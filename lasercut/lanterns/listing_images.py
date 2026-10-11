"""Listing images for the geometric lanterns: glowing 3D renders (2000×2000)."""
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
import importlib.util  # noqa: E402

import build_lanterns as L  # noqa: E402


def _load(name, rel):
    # both sibling packs name their helper "package_and_images": load under unique names
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "lasercut", rel, "package_and_images.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_orn = _load("ornaments_pkg", "ornaments_3d")      # dark festive scene + brand band
band, scene, wood = _orn.band, _orn.scene, _orn.wood

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
OUT = os.path.join(HERE, "listing")


def panel(g, ppm, seed, shade):
    """RGBA wood panel; cut-outs filled with warm light."""
    x0, y0, x1, y1 = -1, -5, L.W + 1, L.H + 5
    Wp, Hp = int((x1 - x0) * ppm), int((y1 - y0) * ppm)
    T = lambda r: [((x - x0) * ppm, (y1 - y) * ppm) for x, y in r]
    body = Image.new("L", (Wp, Hp), 0)
    holes = Image.new("L", (Wp, Hp), 0)
    ImageDraw.Draw(body).polygon(T(g.exterior.coords), fill=255)
    for r in g.interiors:
        ImageDraw.Draw(holes).polygon(T(r.coords), fill=255)
    tex = wood(Wp, Hp, tuple(int(c * shade) for c in (206, 160, 104)), seed, scale=0.4)
    yy = np.linspace(0, 1, Hp)[:, None]
    light = np.stack([np.full((Hp, Wp), 255), 200 - 60 * yy + 0 * np.ones((1, Wp)), 110 - 70 * yy + 0 * np.ones((1, Wp))], -1)
    light = Image.fromarray(np.clip(light, 0, 255).astype(np.uint8))
    out = Image.new("RGBA", (Wp, Hp), (0, 0, 0, 0))
    out.paste(tex, (0, 0), body)
    out.paste(light, (0, 0), holes)
    edge = ImageChops.subtract(holes.filter(ImageFilter.MaxFilter(3)), holes)
    out.paste((60, 34, 14), (0, 0), edge)
    return out, holes


def lantern(name, height_px, seed=1):
    ppm = height_px / (L.H + 10)
    f, s = L.wall("F", 3.0, name), L.wall("S", 3.0, name)
    pf, hf = panel(f, ppm, seed, 1.0)
    ps, hs = panel(s, ppm, seed + 3, 0.72)
    Wp, Hp = pf.size
    a, b, c, d = 0.86, 0.28, 0.55, 0.32          # front scale/shear, side scale/shear
    Wout = int(Wp * a + Wp * c) + 4
    Hout = int(Hp + Wp * b + 40)
    img = Image.new("RGBA", (Wout, Hout), (0, 0, 0, 0))
    off = int(Wp * d) + 10
    front = pf.transform((Wout, Hout), Image.AFFINE, (1 / a, 0, 0, -b / a, 1, -off), Image.BICUBIC)
    side = ps.transform((Wout, Hout), Image.AFFINE,
                        (1 / c, 0, -Wp * a / c, d / c, 1, -off - Wp * b - d * Wp * a / c), Image.BICUBIC)
    # glow halo from the light
    glow = ImageChops.add(front.split()[1].point(lambda v: 255 if v > 180 else 0),
                          side.split()[1].point(lambda v: 255 if v > 180 else 0))
    halo = Image.new("RGBA", (Wout, Hout), (255, 170, 70, 0))
    halo.putalpha(glow.filter(ImageFilter.GaussianBlur(height_px / 18)).point(lambda v: int(v * 0.8)))
    img.alpha_composite(halo)
    img.alpha_composite(side)
    img.alpha_composite(front)
    # top ring (seen from above) with the glowing opening, and the base lip
    tl, cr = (0, off), (Wp * a, off + Wp * b)
    tr, bk = (Wp * a + Wp * c, off + Wp * b - Wp * d), (Wp * c, off - Wp * d)
    dr = ImageDraw.Draw(img)
    dr.polygon([tl, cr, tr, bk], fill=(196, 152, 98, 255), outline=(90, 55, 25, 255))
    k = 0.28
    lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    cx, cy = (tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2
    inner = [lerp(pt, (cx, cy), k * 2) for pt in (tl, cr, tr, bk)]
    dr.polygon(inner, fill=(255, 205, 120, 255))
    yb = Hp - Wp * 0  # bottom edge of the walls in output space ≈ off + Hp
    base_tl, base_cr = (0, off + Hp - 6), (Wp * a, off + Hp - 6 + Wp * b)
    base_tr = (Wp * a + Wp * c, off + Hp - 6 + Wp * b - Wp * d)
    dr.polygon([base_tl, base_cr, (base_cr[0], base_cr[1] + 14), (base_tl[0], base_tl[1] + 14)], fill=(150, 108, 64, 255))
    dr.polygon([base_cr, base_tr, (base_tr[0], base_tr[1] + 14), (base_cr[0], base_cr[1] + 14)], fill=(120, 84, 48, 255))
    return img.crop(img.getbbox())


def fit(img, maxw, maxh):
    r = min(maxw / img.width, maxh / img.height)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)


def compose_hero():
    S = 2000
    im = scene(S, 11)
    band(im, S, "GEOMETRIC LANTERN SVG FILES", "6 mathematical tealight lanterns · laser cut SVG · DXF")
    for name, cx, maxw, maxh in (("voronoi", 360, 560, 900), ("golden", 1640, 560, 900), ("girih", 1000, 700, 1180)):
        lt = fit(lantern(name, 1000), maxw, maxh)
        im.alpha_composite(lt, (int(cx - lt.width / 2), 1800 - 40 - lt.height))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    S = 2000
    compose_hero().convert("RGB").save(os.path.join(OUT, "01_hero.jpg"), quality=92)
    # all six
    im = scene(S, 12)
    band(im, S, "SIX DESIGNS", "Voronoi · honeycomb · golden angle · snowflakes · girih · circles")
    f = ImageFont.truetype(SANS, 40)
    for k, name in enumerate(L.DESIGNS):
        lt = fit(lantern(name, 800, seed=k), 520, 600)
        x, y = 90 + (k % 3) * 640 + (520 - lt.width) // 2, 260 + (k // 3) * 760
        im.alpha_composite(lt, (x, y))
        d = ImageDraw.Draw(im)
        w = d.textlength(L.LABEL[name], font=f)
        d.text((x + lt.width / 2 - w / 2, y + lt.height + 18), L.LABEL[name], font=f, fill=(222, 186, 110))
    im.convert("RGB").save(os.path.join(OUT, "02_all_six.jpg"), quality=92)
    # 3 cut sheet
    im = scene(S, 13)
    band(im, S, "ONE SHEET, SIX PIECES", "2 front walls · 2 side walls · base · top ring")
    f_, s_ = L.wall("F", 3.0, "honeycomb"), L.wall("S", 3.0, "honeycomb")
    pieces = L.layout([f_, f_, s_, s_, L.plate(3.0, False), L.plate(3.0, True)])
    from shapely.ops import unary_union
    gx0, gy0, gx1, gy1 = unary_union(pieces).bounds
    sc = 1700 / (gx1 - gx0)
    sheet = Image.new("RGBA", (int((gx1 - gx0) * sc) + 40, int((gy1 - gy0) * sc) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, sheet.width, sheet.height], fill=(232, 214, 180, 255))
    for g in pieces:
        T = lambda r: [((x - gx0) * sc + 20, (gy1 - y) * sc + 20) for x, y in r]
        d.polygon(T(g.exterior.coords), fill=(214, 172, 116), outline=(200, 40, 40))
        for r in g.interiors:
            d.polygon(T(r.coords), fill=(232, 214, 180), outline=(200, 40, 40))
    im.alpha_composite(sheet, ((S - sheet.width) // 2, 330))
    im.convert("RGB").save(os.path.join(OUT, "03_sheet.jpg"), quality=92)
    # 4 specs
    im = scene(S, 14)
    band(im, S, "READY FOR YOUR LASER", "Glowforge · xTool · LightBurn · any SVG / DXF laser")
    specs = ["6 designs × 3 thicknesses: 3 mm · 1/8\" · 4 mm", "Finger joints sized to your material",
             f"Lantern {L.W:.0f} × {L.W:.0f} × {L.H:.0f} mm · fits an LED tealight",
             "Whole lantern on one 375 × 239 mm sheet", "Red = cut · SVG + DXF in millimetres",
             "Every piece verified as one solid part", "Assembly guide included",
             "For LED / battery tealights only"]
    f = ImageFont.truetype(SANS, 56)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(specs):
        d.text((200, 330 + i * 165), "■", font=f, fill=(222, 186, 110))
        d.text((290, 330 + i * 165), t, font=f, fill=(248, 244, 235))
    im.convert("RGB").save(os.path.join(OUT, "04_specs.jpg"), quality=92)
    # 5 close-up
    im = scene(S, 15)
    band(im, S, "KOCH SNOWFLAKE LANTERN", "fractal snowflakes, glowing for the holidays")
    lt = fit(lantern("snowflakes", 1400, 3), 1300, 1500)
    im.alpha_composite(lt, ((S - lt.width) // 2, 1800 - 30 - lt.height))
    im.convert("RGB").save(os.path.join(OUT, "05_snowflakes.jpg"), quality=92)
    print("listing ->", OUT)


if __name__ == "__main__":
    main()
