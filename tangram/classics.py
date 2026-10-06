"""Hand-authored figures (mixed 45-degree lattices) in the placement language of dsl.py."""
from dsl import Fig, H, R2

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
    f.put("PA", 4, flip=1, v=2, at=(0, 0))                              # belly fin
    f.put("SQ", 0, v=1, at=(-R2, 1))                                    # snout
    return f
