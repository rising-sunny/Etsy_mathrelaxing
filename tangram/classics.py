"""Hand-authored figures (mixed 45-degree lattices) in the placement language of dsl.py."""
from shapely.geometry import Polygon
from dsl import Fig, H, R2
import solver


class Outline:
    """A figure given by its outline; the exact solver finds the seven-piece tiling."""
    TYPES = {"L": ["L1", "L2"], "S": ["S1", "S2"], "M": ["M"], "SQ": ["SQ"], "PA": ["PA"]}

    def __init__(self, pts):
        sol = solver.solve(Polygon(pts))
        assert sol, "outline has no tangram solution"
        used = {k: list(v) for k, v in self.TYPES.items()}
        self.p = {used[t].pop(0): q for t, rot, flip, q in sol[0]}

    def placed(self):
        return list(self.p.items())

    def check(self):
        return [], "Polygon"

FIGS = {}


def fig(fn):
    FIGS[fn.__name__.replace("_", " ").title()] = fn
    return fn


@fig
def cat():
    f = Fig()
    f.put("L1", 5, at=(R2, R2)); f.put("L2", 3, at=(R2, R2))           # body: big right triangle
    f.put("SQ", 1, v=3, to=("L2", 1))                                   # head: diamond on the back
    f.put("S1", 3, to=("SQ", 2)); f.put("S2", 7, to=("SQ", 2))          # ears
    f.put("PA", 0, flip=1, v=1, to=("L1", 2))                           # tail along the ground
    f.put("M", 7, at=(-1, 1))                                           # chest
    return f


@fig
def fish():
    f = Fig()
    f.put("L1", 3, at=(R2, R2)); f.put("L2", 7, at=(-R2, R2))           # body diamond
    f.put("S1", 1, at=(R2, R2)); f.put("S2", 5, at=(R2, R2))            # tail
    f.put("M", 6, at=(-R2, 2 * R2))                                     # dorsal fin
    f.put("PA", 6, at=(-R2, R2))                                        # belly fin
    f.put("SQ", 0, v=2, at=(-R2, R2))                                   # snout
    return f


@fig
def rabbit():
    f = Fig()
    f.put("L1", 5, at=(R2, R2)); f.put("L2", 1, at=(0, 0))          # long body
    f.put("SQ", 1, v=3, at=(R2, R2))                                # head
    f.put("PA", 1, at=(R2, R2))                                     # long ear
    f.put("S1", 7, to=("SQ", 2))                                    # second ear
    f.put("S2", 7, at=(2 * R2 - H, H))                              # chin
    f.put("M", 0, at=(2 * R2, 0))                                   # front paws
    return f


@fig
def swan():
    f = Fig()
    f.put("L1", 4, at=(2, 0)); f.put("L2", 6, at=(2, 0))            # body floating
    f.put("S1", 0, at=(0, 0)); f.put("S2", 0, at=(1, 0))            # tail and wing
    f.put("PA", 0, at=(3, 0)); f.put("SQ", 0, at=(4, 1))            # neck
    f.put("M", 0, at=(4, 2))                                        # head with beak
    return f


@fig
def horse():
    f = Fig()
    f.put("L1", 1, at=(0, 0)); f.put("L2", 5, at=(R2, R2))          # body
    f.put("PA", 0, flip=1, at=(-R2 + 1, R2))                        # neck
    f.put("SQ", 1, v=2, to=("PA", 2))                               # head
    f.put("S1", 6, at=(0, 0)); f.put("S2", 4, at=(2 * R2, 0))       # legs
    f.put("M", 7, at=(R2, R2))                                      # tail
    return f


@fig
def teapot():
    f = Fig()
    f.put("L1", 0, at=(0, 0)); f.put("L2", 4, at=(2, 2))            # pot
    f.put("PA", 1, at=(2, 1)); f.put("S2", 0, at=(2, 0))            # spout
    f.put("M", 7, at=(-1, 1))                                       # handle
    f.put("SQ", 0, at=(0.5, 2))                                     # lid
    f.put("S1", 5, at=(1, 3 + H))                                   # knob
    return f


@fig
def whale():
    f = Fig()
    f.put("L1", 0, at=(0, 0)); f.put("L2", 4, at=(2, 2))            # head and body
    f.put("M", 3, at=(3, 1))                                        # tapering tail
    f.put("S1", 1, at=(3, 1)); f.put("S2", 5, at=(3, 1))            # flukes
    f.put("PA", 2, at=(1, 2))                                       # spout
    f.put("SQ", 0, at=(1, -1))                                      # flipper
    return f


@fig
def elephant():
    return Outline([(0, 0), (1, 1), (2, 0), (2, 1), (3, 2), (2, 3), (0, 3), (-1, 3), (-1, 2), (-2, 1), (-1, 1), (0, 2), (0, 1)])


@fig
def camel():
    return Outline([(0, -1), (1, 0), (2, -1), (2, 1), (3, 2), (4, 2), (4, 3), (3, 3), (2, 2), (1, 3), (0, 2)])


@fig
def chicken():
    f = Fig()
    f.put("L1", 0, at=(0, 0)); f.put("L2", 4, at=(2, 2))            # body
    f.put("M", 7, at=(-1, 1))                                       # tail
    f.put("SQ", 0, at=(1, 2))                                       # head
    f.put("S1", 0, at=(1, 3)); f.put("S2", 0, at=(2, 2))            # comb, beak
    f.put("PA", 4, at=(1.5, 0))                                     # legs
    return f
