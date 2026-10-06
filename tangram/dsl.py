"""
Tiny placement language for hand-authored tangram figures.

  f = Fig()
  f.put("L1", rot, at=(x, y))                   # piece vertex 0 at (x, y)
  f.put("SQ", rot, v=2, to=("L1", 1))           # piece vertex 2 on vertex 1 of L1
  f.put("PA", rot, flip=1, v=0, to=("M", 2), shift=(dx, dy))

Rotations are multiples of 45 degrees counter-clockwise. Vertex 0 is the right angle of a
triangle (legs to vertices 1 and 2), the lower-left corner of the square, and the acute
corner (0,0) of the parallelogram [(0,0),(1,0),(2,1),(1,1)].
"""
import math
from shapely.geometry import Polygon
from shapely import affinity
from engine import PIECES, silhouette

H = math.sqrt(2) / 2
R2 = math.sqrt(2)


class Fig:
    def __init__(self):
        self.p = {}

    def put(self, name, rot, flip=0, at=None, v=0, to=None, shift=(0, 0)):
        g = Polygon(PIECES[name])
        if flip:
            g = affinity.scale(g, xfact=-1, yfact=1, origin=(0, 0))
        g = affinity.rotate(g, 45 * rot, origin=(0, 0))
        pts = list(g.exterior.coords)[:-1]
        if to is not None:
            at = self.v(*to)
        at = at or (0, 0)
        dx = at[0] - pts[v][0] + shift[0]; dy = at[1] - pts[v][1] + shift[1]
        g = affinity.translate(g, dx, dy)
        self.p[name] = Polygon([(round(x, 9), round(y, 9)) for x, y in g.exterior.coords])
        return self

    def v(self, name, i):
        return list(self.p[name].exterior.coords)[i]

    def placed(self):
        return [(n, self.p[n]) for n in self.p]

    def check(self):
        names = list(self.p)
        assert sorted(names) == sorted(PIECES), f"missing {set(PIECES) - set(names)}"
        bad = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if self.p[a].intersection(self.p[b]).area > 1e-6]
        sil = silhouette(self.placed())
        return bad, sil.geom_type
