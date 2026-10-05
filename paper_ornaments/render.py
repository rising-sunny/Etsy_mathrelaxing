"""
Vector PDF (US Letter + A4, colour + plain-white editions) and SVG cut files for the
Geometric 3D Paper Ornaments pack. Every template is printed at real size; a 2 cm /
1 inch scale bar on each page checks "print at 100%".

  python render.py
"""
import os, sys, json, math, zipfile, pickle
import numpy as np
import fitz
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "logic_book_xmas"))
import nets as N
import models as M
from render_book import FONTS, FOBJ, snow, star_pts  # shared fonts + motifs

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
CM = 28.3465


def c(rgb):
    return tuple(v / 255 for v in rgb)


COL = {"red": c((176, 42, 56)), "pine": c((36, 104, 80)), "gold": c((206, 164, 74)), "navy": c((30, 46, 82)),
       "cream": c((250, 246, 238))}
NAVY = COL["navy"]; RED = COL["red"]; PINE = COL["pine"]; GOLD = COL["gold"]
INK = c((36, 36, 40)); SUB = c((110, 106, 100)); LINE = c((205, 198, 184)); TAB = c((232, 228, 220))
WHITE = (1, 1, 1)
PAGES = {"Letter": (612, 792), "A4": (595.3, 841.9)}
MARGIN = 0.9 * CM; TOP = 2.6 * CM; BOTTOM = 1.6 * CM


def printable(W, H):
    return W - 2 * MARGIN, H - TOP - BOTTOM


def fit_edge(models):
    """Shrink a model's edge if any of its pieces would not fit on either page size."""
    for m in models:
        e = m["edge_cm"]
        for W, H in PAGES.values():
            pw, ph = printable(W, H)
            for p in m["pieces"]:
                x0, y0, x1, y1 = N.bounds(p["net"])
                e = min(e, pw / CM / (x1 - x0), ph / CM / (y1 - y0))
        if e < m["edge_cm"]:
            m["diameter_cm"] *= e / m["edge_cm"]
        m["edge_cm"] = e
    return models


# ------------------------------------------------------------------ drawing
class Doc:
    def __init__(self, W, H, colour):
        self.doc = fitz.open(); self.W, self.H = W, H; self.colour = colour; self.n = 0

    def page(self, title=None, sub=None, number=True):
        p = self.doc.new_page(width=self.W, height=self.H)
        for k, v in FONTS.items():
            p.insert_font(fontname=k, fontfile=v)
        self.n += 1
        if title:
            p.draw_rect(fitz.Rect(0, 0, self.W, 5), color=None, fill=NAVY)
            self.text(p, MARGIN, 34, title, "title", 17, NAVY)
            if sub:
                self.text(p, MARGIN, 52, sub, "body", 9, SUB)
            snow(p, self.W - MARGIN - 8, 30, 8, GOLD, 0.9)
        if number:
            self.ctext(p, self.W / 2, self.H - 14, str(self.n), "body", 8, SUB)
        return p

    def text(self, p, x, y, s, f, size, col=INK, rotate=0):
        p.insert_text((x, y), s, fontname=f, fontsize=size, color=col, rotate=rotate)

    def tlen(self, s, f, size):
        return FOBJ[f].text_length(s, fontsize=size)

    def ctext(self, p, cx, y, s, f, size, col=INK):
        self.text(p, cx - self.tlen(s, f, size) / 2, y, s, f, size, col)

    def para(self, p, x, y, s, f, size, width, col=INK, lh=1.42):
        for para in s.split("\n"):
            line = ""
            for w in para.split(" "):
                t = (line + " " + w).strip()
                if self.tlen(t, f, size) <= width:
                    line = t
                else:
                    self.text(p, x, y, line, f, size, col); y += size * lh; line = w
            self.text(p, x, y, line, f, size, col); y += size * lh
        return y

    def scale_bar(self, p):
        y = self.H - BOTTOM + 14; x = MARGIN
        p.draw_rect(fitz.Rect(x, y, x + 2 * CM, y + 5), color=INK, width=0.6, fill=None)
        p.draw_rect(fitz.Rect(x, y, x + 1 * CM, y + 5), color=None, fill=INK)
        self.text(p, x, y + 15, "2 cm", "body", 7, SUB)
        x2 = x + 2.6 * CM
        p.draw_rect(fitz.Rect(x2, y, x2 + 72, y + 5), color=INK, width=0.6, fill=None)
        self.text(p, x2, y + 15, "1 inch", "body", 7, SUB)
        s = "Print at 100% / actual size  ·  solid line = cut  ·  dashed line = fold  ·  grey = glue tab"
        self.text(p, self.W - MARGIN - self.tlen(s, "body", 7.5), y + 6, s, "body", 7.5, SUB)

    def save(self, path):
        self.doc.save(path, deflate=True, garbage=3)


def draw_net(D, p, net, ox, oy, k, face_cols, mirror_y=True):
    """Draw one net with origin offset (ox, oy) in pt and scale k (pt per edge unit)."""
    T = lambda q: fitz.Point(ox + q[0] * k, oy - q[1] * k if mirror_y else oy + q[1] * k)
    sh = p.new_shape()
    for t in net["tabs"]:
        sh.draw_polyline([T(q) for q in t] + [T(t[0])])
    sh.finish(color=None, fill=TAB, closePath=True)
    for f, col in zip(net["faces"], face_cols):
        sh.draw_polyline([T(q) for q in f] + [T(f[0])])
        sh.finish(color=None, fill=COL[col] if D.colour else WHITE, closePath=True)
    sh.commit()
    if D.colour:  # small snowflake motif in every face
        for f, col in zip(net["faces"], face_cols):
            P = Polygon(f); cen = P.centroid; r = max(0.0, min(P.exterior.distance(cen), 0.6)) * k * 0.42
            if r > 3:
                snow(p, ox + cen.x * k, oy - cen.y * k, r, COL["cream"] if col != "cream" else GOLD, max(0.5, r * 0.08))
    # folds dashed
    sh = p.new_shape()
    for a, b in net["folds"]:
        sh.draw_line(T(a), T(b))
    sh.finish(color=SUB, width=0.6, dashes="[3 2] 0"); sh.commit()
    # cut outline
    out = N.outline(net)
    polys = out.geoms if out.geom_type == "MultiPolygon" else [out]
    sh = p.new_shape()
    for g in polys:
        pts = list(g.exterior.coords)
        sh.draw_polyline([T(q) for q in pts])
    sh.finish(color=INK, width=0.9, closePath=True); sh.commit()


def piece_box(net, k):
    x0, y0, x1, y1 = N.bounds(net)
    return (x1 - x0) * k, (y1 - y0) * k, x0, y1


def model_pages(D, m):
    k = m["edge_cm"] * CM
    pw, ph = printable(D.W, D.H)
    sub_base = f"{m['group']} {'solid' if m['group'] != 'Star' else ''}".strip()
    diff = "Easy" if m["diff"] == 1 else "Medium" if m["diff"] == 2 else "Advanced"
    if m["fev"]:
        f, e, v = m["fev"]
        sub = f"{sub_base}  ·  {f} faces, {e} edges, {v} vertices  ·  finished size about {m['diameter_cm']:.1f} cm  ·  {diff}"
    else:
        total = sum(p["count"] for p in m["pieces"][1:])
        sub = f"Star on a {m['core'].lower()} core  ·  {total} points  ·  finished size about {m['diameter_cm']:.1f} cm  ·  {diff}"
    # core / single net page
    first = m["pieces"][0]
    p = D.page(m["name"], sub)
    w, h, x0, y1 = piece_box(first["net"], k)
    ox = MARGIN + (pw - w) / 2 - x0 * k; oy = TOP + (ph - h) / 2 + y1 * k
    draw_net(D, p, first["net"], ox, oy, k, first["colors"])
    if len(m["pieces"]) > 1:
        D.text(p, MARGIN, TOP - 8, first["label"], "bold", 9, RED)
    D.scale_bar(p)
    # star points: shelf-pack all copies
    items = []
    for piece in m["pieces"][1:]:
        net = N.compact_rotation(piece["net"], 1.6)
        for j in range(piece["count"]):
            items.append((net, piece["spike_colors"][j], piece["label"]))
    if not items:
        return
    gap = 0.35 * CM
    p = None; x = y = rowh = 0; label_done = set()
    for net, colname, label in items:
        w, h, x0, y1 = piece_box(net, k)
        if p is None or x + w > pw:
            x = 0; y += rowh + gap; rowh = 0
        if p is None or y + h > ph:
            p = D.page(m["name"] + " - points", sub); D.scale_bar(p); x = 0; y = 14; rowh = 0
        if label not in label_done:
            D.text(p, MARGIN + x, TOP + y - 4, label, "bold", 9, RED); label_done.add(label)
        ox = MARGIN + x - x0 * k; oy = TOP + y + y1 * k
        draw_net(D, p, net, ox, oy, k, [colname] * len(net["faces"]))
        x += w + gap; rowh = max(rowh, h)


# ------------------------------------------------------------------ SVG
def svg_for(m, k_mm=10.0):
    """One SVG per piece type (mm units): coloured faces, score lines (blue) and cut line (red)."""
    files = {}
    e = m["edge_cm"] * 10  # mm per edge unit
    for pi, piece in enumerate(m["pieces"]):
        net = piece["net"]; x0, y0, x1, y1 = N.bounds(net)
        pad = 5; W = (x1 - x0) * e + 2 * pad; H = (y1 - y0) * e + 2 * pad
        T = lambda q: (pad + (q[0] - x0) * e, pad + (y1 - q[1]) * e)
        cols = piece.get("colors") or [piece["spike_colors"][0]] * len(net["faces"])
        hexc = lambda t: "#%02x%02x%02x" % tuple(int(v * 255) for v in COL[t])
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.2f} {H:.2f}">',
               '<g id="print">']
        for t in net["tabs"]:
            out.append('<polygon points="%s" fill="#e8e4dc"/>' % " ".join(f"{a:.2f},{b:.2f}" for a, b in map(T, t)))
        for f, col in zip(net["faces"], cols):
            out.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{a:.2f},{b:.2f}" for a, b in map(T, f)), hexc(col)))
        out.append('</g><g id="score" fill="none" stroke="#1f6fd1" stroke-width="0.3" stroke-dasharray="2,1.2">')
        for a, b in net["folds"]:
            (ax, ay), (bx, by) = T(a), T(b)
            out.append(f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}"/>')
        out.append('</g><g id="cut" fill="none" stroke="#d11f1f" stroke-width="0.3">')
        ol = N.outline(net)
        for g in (ol.geoms if ol.geom_type == "MultiPolygon" else [ol]):
            out.append('<polygon points="%s"/>' % " ".join(f"{a:.2f},{b:.2f}" for a, b in map(T, list(g.exterior.coords)[:-1])))
        out.append("</g></svg>")
        nm = m["name"].replace(" ", "_")
        tag = "net" if len(m["pieces"]) == 1 else ("core" if pi == 0 else f"point_{len(net['faces'])}sided_x{piece['count']}")
        files[f"{nm}_{tag}.svg"] = "\n".join(out)
    return files


# ------------------------------------------------------------------ front matter
def cover(D, renders):
    p = D.page(number=False)
    p.draw_rect(fitz.Rect(0, 0, D.W, D.H), color=None, fill=NAVY)
    if renders and os.path.exists(renders):
        img = fitz.Rect(D.W * 0.06, D.H * 0.05, D.W * 0.94, D.H * 0.05 + D.W * 0.88)
        p.insert_image(img, filename=renders)
    y = D.H * 0.05 + D.W * 0.88 + 34
    D.ctext(p, D.W / 2, y, "GEOMETRIC 3D", "title", D.W * 0.07, COL["cream"])
    D.ctext(p, D.W / 2, y + D.W * 0.075, "PAPER ORNAMENTS", "title", D.W * 0.07, GOLD)
    D.ctext(p, D.W / 2, y + D.W * 0.13, "12 printable polyhedra & star templates", "body", D.W * 0.028, COL["cream"])
    D.ctext(p, D.W / 2, D.H - 30, "MathRelaxing", "title_r", D.W * 0.022, c((210, 216, 230)))


def contents(D, models, pages):
    p = D.page("What's Inside", "12 ornaments, each with real-size templates")
    y = 92
    for m, pg in zip(models, pages):
        diff = "●" * m["diff"]
        D.text(p, MARGIN, y, m["name"], "bold", 11.5, NAVY)
        D.text(p, MARGIN + 190, y, m["group"], "body", 10, SUB)
        D.text(p, MARGIN + 290, y, f"about {m['diameter_cm']:.0f} cm", "body", 10, SUB)
        for j in range(3):
            col = GOLD if j < m["diff"] else LINE
            p.draw_circle((MARGIN + 380 + j * 11, y - 3.5), 3.5, color=None, fill=col)
        s = f"page {pg}"; D.text(p, D.W - MARGIN - D.tlen(s, "body", 10), y, s, "body", 10, INK)
        p.draw_line((MARGIN, y + 8), (D.W - MARGIN, y + 8), color=LINE, width=0.5)
        y += 30
    y += 10
    D.para(p, MARGIN, y, "Difficulty: one gold dot = easy (great first project), three = advanced (patience and a steady "
                         "hand). Sizes are the finished ornament measured tip to tip.", "light", 9.5, D.W - 2 * MARGIN, SUB)


def howto(D):
    p = D.page("How to Make Your Ornaments", "about 20-90 minutes each, depending on the model")
    W = D.W - 2 * MARGIN; y = 92
    blocks = [
        ("You need", "Card stock 160-250 gsm (65-110 lb), a ruler, scissors or a craft knife and cutting mat, an empty "
                     "ballpoint pen or bone folder for scoring, and a glue stick, craft glue or thin double-sided tape. "
                     "Thread or ribbon to hang."),
        ("1. Print", "Print at 100% / actual size (turn off 'fit to page'). Check the 2 cm scale bar at the bottom of the "
                     "page. Use the colour pages, or the white pages on coloured or metallic card."),
        ("2. Score", "Lay the ruler on every dashed line and run the empty pen along it. Scored folds are crisp and "
                     "accurate, which matters most on the bigger models."),
        ("3. Cut", "Cut along the solid outer line, glue tabs included."),
        ("4. Fold", "Fold every dashed line inward (the printed side stays outside), then flatten the piece again."),
        ("5. Glue", "Glue one tab at a time, starting from the middle of the net and working outwards. Hold each tab for a "
                    "few seconds. Close the last face carefully, pressing from the outside with a pencil end."),
        ("6. Hang", "Before closing the last face, push a threaded needle through one corner from the inside and knot the "
                    "thread, or glue a loop of ribbon under the last tab."),
        ("Stars", "Build the core first. Fold each point, glue its side tab to close it, then glue its base tabs onto one "
                  "face of the core. The Moravian star looks best with all points the same colour, or with gold square "
                  "points and red triangle points."),
    ]
    for h, t in blocks:
        D.text(p, MARGIN, y, h, "bold", 11.5, RED)
        y = D.para(p, MARGIN, y + 15, t, "body", 10, W) + 10


def math_corner(D):
    p = D.page("The Math Behind the Ornaments", "every template here is computed from exact coordinates")
    W = D.W - 2 * MARGIN; y = 92
    blocks = [
        ("Platonic solids", "Only five solids have identical regular faces with the same number meeting at every corner: "
                            "the tetrahedron, cube, octahedron, dodecahedron and icosahedron. The angles around a corner "
                            "must add up to less than 360 degrees, and that leaves exactly five possibilities. They have "
                            "been known since ancient Greece."),
        ("Euler's formula", "Count the faces F, edges E and vertices V of any of these solids: F - E + V = 2. A cube has "
                            "6 - 12 + 8 = 2, the truncated icosahedron (the classic football) has 32 - 90 + 60 = 2."),
        ("Archimedean solids", "Mix two or more kinds of regular faces, keep every corner identical, and you get the 13 "
                               "Archimedean solids. Four are in this pack: the cuboctahedron, truncated octahedron, "
                               "rhombicuboctahedron and truncated icosahedron."),
        ("Kepler's star", "The small stellated dodecahedron, described by Johannes Kepler in 1619, puts a five-sided "
                          "point on each face of a dodecahedron. Each side of a point is a golden triangle: the long "
                          "sides are exactly phi = 1.618... times the base."),
        ("Stella octangula", "Two interlocking tetrahedra, the eight-pointed star Kepler also studied. Here it is built "
                             "as eight small tetrahedra on an octahedron."),
        ("Moravian star", "The traditional Advent star from Herrnhut, Germany has 26 points on a rhombicuboctahedron: "
                          "18 on its squares and 8 on its triangles. The point lengths here are calculated so that every "
                          "tip is the same distance from the centre."),
        ("Nets", "Every flat pattern is a 'net' of its solid: an unfolding along a tree of edges with no overlaps. Most "
                 "solids have thousands of different nets; these were chosen by computer to fit the page as large as "
                 "possible."),
    ]
    for h, t in blocks:
        D.text(p, MARGIN, y, h, "bold", 11.5, PINE)
        y = D.para(p, MARGIN, y + 15, t, "body", 10, W) + 9


def terms(D):
    p = D.page("Terms of Use")
    D.para(p, MARGIN, 92, "For personal use, family use and use in a single classroom. Print as many copies as you need "
                          "for yourself, your household or your own class.\n\nPlease do not resell the files or the "
                          "finished ornaments made from them, share the files, or post them anywhere the public can "
                          "download them.\n\nAll templates and artwork are original work by MathRelaxing, generated from "
                          "exact geometry. If you ever spot a problem, send a message through the shop and a corrected "
                          "file will be sent free.\n\nMerry Christmas and happy folding!\n\n(c) MathRelaxing",
           "body", 11, D.W - 2 * MARGIN)


def build(models, renders):
    outs = []
    for size, (W, H) in PAGES.items():
        D = Doc(W, H, True)
        cover(D, renders)
        D.page(); contents_page = D.n  # placeholder, rewritten below
        howto(D); math_corner(D)
        starts = {}
        for colour, label in ((True, "colour"), (False, "white")):
            D.colour = colour
            if not colour:
                p = D.page("Plain White Templates", "print these on coloured, kraft or metallic card stock")
                D.para(p, MARGIN, 92, "The same 12 templates without colour fills. Use them on coloured or metallic "
                                      "card, or let children colour the faces before folding.", "body", 11, D.W - 2 * MARGIN)
            for m in models:
                if colour:
                    starts[m["name"]] = D.n + 1
                model_pages(D, m)
        terms(D)
        # contents on page 2
        D.doc.delete_page(contents_page - 1)
        tmp = Doc(W, H, True); tmp.n = contents_page - 1; contents(tmp, models, [starts[m["name"]] for m in models])
        tmp.doc[0].clean_contents()
        D.doc.insert_pdf(tmp.doc, from_page=0, to_page=0, start_at=contents_page - 1)
        path = os.path.join(OUT, f"Geometric_Paper_Ornaments_{size}.pdf")
        D.save(path); outs.append(path)
        print(f"{size}: {len(D.doc)} pages, {os.path.getsize(path) // 1024} KB")
    # SVG zip
    zp = os.path.join(OUT, "Geometric_Paper_Ornaments_SVG.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", "SVG cut files in millimetres, real size.\nLayers: 'print' (colour faces and grey glue "
                                 "tabs), 'score' (blue dashed fold lines) and 'cut' (red outline).\nFor Cricut Design "
                                 "Space: upload, set 'score' lines to Score and 'cut' to Cut, or use the 'print' layer "
                                 "with Print Then Cut.\n(c) MathRelaxing - personal use only.\n")
        for m in models:
            for fn, txt in svg_for(m).items():
                z.writestr(fn, txt)
    print("svg zip", os.path.getsize(zp) // 1024, "KB")
    return outs + [zp]


if __name__ == "__main__":
    cache = os.path.join(OUT, "models.pkl")
    if os.path.exists(cache):
        models = pickle.load(open(cache, "rb"))
    else:
        models = fit_edge(M.all_models())
        pickle.dump(models, open(cache, "wb"))
    for m in models:
        print(f"{m['name']:22s} edge {m['edge_cm']:.2f} cm  diameter {m['diameter_cm']:.1f} cm")
    build(models, os.path.join(OUT, "cover_renders.png"))
