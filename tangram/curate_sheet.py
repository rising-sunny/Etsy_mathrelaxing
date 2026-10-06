"""Generate many edge-to-edge figures, stand each on its longest bottom edge, and render
numbered contact sheets for visual curation (saved with the placements in out/cands.json)."""
import os, sys, json, math, warnings
warnings.filterwarnings("ignore")
from PIL import Image, ImageDraw, ImageFont
from shapely import affinity
import assemble as A
from engine import signature, compactness, silhouette, clean_poly

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)


def stand(placed, poly):
    """Rotate by a multiple of 45 deg so the figure rests on its longest horizontal bottom edge."""
    best = None
    for r in range(8):
        q = affinity.rotate(poly, 45 * r, origin=(0, 0)); miny = q.bounds[1]
        pts = list(q.exterior.coords)
        base = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)
                   if abs(pts[i][1] - miny) < 1e-6 and abs(pts[i + 1][1] - miny) < 1e-6)
        h = q.bounds[3] - q.bounds[1]; w = q.bounds[2] - q.bounds[0]
        score = base - 0.05 * w * h
        if best is None or score > best[0]:
            best = (score, r)
    r = best[1]
    pl = [(n, affinity.rotate(g, 45 * r, origin=(0, 0))) for n, g in placed]
    q = affinity.rotate(poly, 45 * r, origin=(0, 0))
    mx, my = q.bounds[0], q.bounds[1]
    return [(n, affinity.translate(g, -mx, -my)) for n, g in pl], affinity.translate(q, -mx, -my)


def main(n=6000, seed=11):
    res = A.generate(n, seed); seen = set(); keep = []
    for pl, p in res:
        sg = signature(p)
        if sg in seen:
            continue
        seen.add(sg)
        c = compactness(p)
        if not (0.22 <= c <= 0.62):
            continue
        pl, p = stand(pl, p)
        keep.append({"c": round(c, 3), "placed": [(nm, [list(map(float, xy)) for xy in list(g.exterior.coords)[:-1]]) for nm, g in pl],
                     "poly": [list(map(float, xy)) for xy in list(p.exterior.coords)[:-1]]})
    json.dump(keep, open(os.path.join(OUT, "cands.json"), "w"))
    print(len(res), "built ->", len(keep), "distinct candidates")
    T = 170; cols = 8; rows = 6; per = cols * rows; fnt = ImageFont.load_default()
    for s in range(0, len(keep), per):
        sheet = Image.new("RGB", (cols * T, rows * T), "white"); d = ImageDraw.Draw(sheet)
        for k, f in enumerate(keep[s:s + per]):
            x0 = (k % cols) * T; y0 = (k // cols) * T
            pts = f["poly"]; w = max(p[0] for p in pts); h = max(p[1] for p in pts)
            sc = (T - 30) / max(w, h, 4.5)
            ox = x0 + (T - w * sc) / 2; oy = y0 + T - 8 - (T - 22 - h * sc) / 2
            d.polygon([(ox + x * sc, oy - y * sc) for x, y in pts], fill=(30, 30, 40))
            d.text((x0 + 4, y0 + 2), str(s + k), fill=(200, 0, 0), font=fnt)
            d.rectangle((x0, y0, x0 + T - 1, y0 + T - 1), outline=(220, 220, 220))
        sheet.save(os.path.join(OUT, f"sheet_{s // per:02d}.png"))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6000)
