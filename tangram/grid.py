"""
Half-square grid notation for tangram silhouettes (small-triangle legs = 1 = one cell).
Rows are written top to bottom, one character per unit cell:
  .  empty      #  full
  a  ◣ lower-left half     b  ◢ lower-right half
  c  ◥ upper-right half    d  ◤ upper-left half
"""
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HALF = {"a": [(0, 0), (1, 0), (0, 1)], "b": [(0, 0), (1, 0), (1, 1)],
        "c": [(1, 0), (1, 1), (0, 1)], "d": [(0, 0), (1, 1), (0, 1)]}


def parse(rows):
    rows = [r.replace(" ", ".") for r in rows]
    n = len(rows); cells = []
    for i, r in enumerate(rows):
        y = n - 1 - i
        for x, ch in enumerate(r):
            if ch == "#":
                cells.append(box(x, y, x + 1, y + 1))
            elif ch in HALF:
                cells.append(Polygon([(x + u, y + v) for u, v in HALF[ch]]))
            elif ch != ".":
                raise ValueError(ch)
    u = unary_union([c.buffer(1e-9, join_style=2) for c in cells]).buffer(-1e-9, join_style=2)
    return u.simplify(1e-7)


def area_half(rows):
    return sum(2 if ch == "#" else (1 if ch in HALF else 0) for r in rows for ch in r)
