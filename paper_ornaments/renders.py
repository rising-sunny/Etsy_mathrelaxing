"""3D renders of the finished ornaments (matplotlib, flat shading) for the cover and
listing images: one PNG per ornament plus a 4 x 3 grid."""
import os, sys, pickle, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "out"); R3 = os.path.join(OUT, "renders"); os.makedirs(R3, exist_ok=True)
BASE = {"red": (176, 42, 56), "pine": (36, 104, 80), "gold": (206, 164, 74), "navy": (64, 92, 150), "cream": (240, 234, 220)}
LIGHT = np.array([0.45, -0.55, 0.7]); LIGHT /= np.linalg.norm(LIGHT)


def shade(rgb, n):
    k = 0.62 + 0.5 * max(0.0, float(np.dot(n, LIGHT)))
    return tuple(min(1, v / 255 * k + 0.04) for v in rgb)


def render(m, path, bg=(24 / 255, 36 / 255, 64 / 255), elev=18, azim=35, size=6):
    fig = plt.figure(figsize=(size, size), dpi=150, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d", facecolor=bg)
    polys, cols = [], []
    e, a = math.radians(elev), math.radians(azim)
    view = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    items = []
    for P, col in m["model3d"]:
        P = np.asarray(P, float); c = P.mean(axis=0)
        n = np.cross(P[1] - P[0], P[2] - P[0]); n /= np.linalg.norm(n)
        if np.dot(n, c) < 0:
            n = -n
        if np.dot(n, view) <= 0.02:  # back-face culling
            continue
        items.append((float(np.dot(c, view)), P, shade(BASE[col], n)))
    for _, P, col in sorted(items, key=lambda t: t[0]):  # far to near
        polys.append(P); cols.append(col)
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(1, 1, 1, 0.55), linewidths=0.6)
    pc.set_sort_zpos(None)
    ax.add_collection3d(pc)
    r = max(np.linalg.norm(np.asarray(P), axis=1).max() for P, _ in m["model3d"])
    for f in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        f(-r * 0.78, r * 0.78)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    fig.savefig(path, facecolor=bg); plt.close(fig)


def grid(models, path, cols=4, cell=600, bg=(24, 36, 64)):
    rows = math.ceil(len(models) / cols)
    G = Image.new("RGB", (cols * cell, rows * cell), bg)
    for i, m in enumerate(models):
        im = Image.open(os.path.join(R3, m["name"].replace(" ", "_") + ".png")).convert("RGB").resize((cell, cell), Image.LANCZOS)
        G.paste(im, ((i % cols) * cell, (i // cols) * cell))
    G.save(path)


if __name__ == "__main__":
    models = pickle.load(open(os.path.join(OUT, "models.pkl"), "rb"))
    for m in models:
        render(m, os.path.join(R3, m["name"].replace(" ", "_") + ".png"))
        print("rendered", m["name"])
    grid(models, os.path.join(OUT, "cover_renders.png"))
