"""Render puzzle mockups for the op-art puzzles by reusing the fractal-puzzle
jigsaw engine, pointed at this set's masters.

  python make_mockups.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "fractal_puzzles"))
import puzzle_mockups as pm

pm.MAST = os.path.join(HERE, "masters")
pm.OUT = os.path.join(HERE, "mockups"); os.makedirs(pm.OUT, exist_ok=True)
pm.SLUGS = ["vortex", "square", "wave", "moire"]
pm.LABELS = {"vortex": "Op Art · Vortex", "square": "Op Art · Hypnos",
             "wave": "Op Art · Ripple", "moire": "Op Art · Harlequin"}

if __name__ == "__main__":
    for s in pm.SLUGS:
        pm.build_one(s)
