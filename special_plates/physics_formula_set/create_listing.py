"""Create + activate Etsy listing for Physics Formula Poster Set of 6."""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from etsy_manager import EtsyManager

HERE = os.path.join(ROOT, "special_plates", "physics_formula_set")
ZIP = os.path.join(HERE, "Physics_Formula_Poster_Set_of_6.zip")
PREV = os.path.join(HERE, "previews")
IMAGES = [
    os.path.join(PREV, "physics_formula_preview_1_hero.jpg"),
    os.path.join(PREV, "physics_formula_preview_2_included.jpg"),
    os.path.join(PREV, "physics_formula_preview_3_eq.jpg"),
    os.path.join(PREV, "physics_formula_preview_4_eq.jpg"),
    os.path.join(PREV, "physics_formula_preview_5_eq.jpg"),
    os.path.join(PREV, "physics_formula_preview_6_eq.jpg"),
]

TAXONOMY = 2078
PRICE = 11.99

TITLE = (
    "Physics Formula Poster Set of 6 | Classroom Science Wall Art | "
    "Kinematics Energy Maxwell Waves Thermo Digital Download"
)

TAGS = [
    "physics poster",
    "physics formula",
    "science wall art",
    "classroom decor",
    "physics classroom",
    "stem wall art",
    "equation poster",
    "teacher gift",
    "digital download",
    "maxwell equations",
    "kinematics poster",
    "science classroom",
    "lab decor",
]

DESC = """PHYSICS FORMULA POSTER SET — 6 ELEGANT SCIENTIFIC PLATES
Dark observatory aesthetic with cream ink, gold accents, and cyan highlights. Built for physics classrooms, labs, and modern STEM walls.

— WHAT'S INCLUDED —
1. Kinematics — motion under constant acceleration
2. Energy — spring–mass mechanical energy
3. Momentum — 1-D elastic collision
4. Electromagnetism — Maxwell’s four equations
5. Waves — traveling harmonic wave
6. Thermodynamics — ideal-gas isotherms

Each design includes print-ready JPG files @ 300 dpi (2×3 and A4).

— DESIGN —
No crowded cheat-sheet clutter: every plate reserves clear zones for title, graphic, caption, and key formulae so text never collides with curves.

— PERFECT FOR —
Physics teachers, AP/IB classrooms, engineering students, science offices, STEM gifts.

Instant download. Designed by MathRelaxing.
"""


def main():
    for p in [ZIP, *IMAGES]:
        if not os.path.isfile(p):
            raise SystemExit(f"Missing {p} — run generate_physics_formula_set.py first")

    m = EtsyManager()
    lid = m.create_full_product(
        TITLE,
        DESC,
        PRICE,
        TAXONOMY,
        image_paths=IMAGES,
        digital_file_paths=[ZIP],
        tags=TAGS,
    )
    shop = m.get_shop_id()
    try:
        m.make_request(
            "PATCH",
            f"/shops/{shop}/listings/{lid}",
            payload={
                "state": "active",
                "who_made": "i_did",
                "when_made": "2020_2026",
                "is_supply": False,
            },
            json_body=True,
        )
        print("Activated.")
    except Exception as e:
        print("Activate warn:", e)
        try:
            m.update_listing(lid, state="active")
        except Exception as e2:
            print("Still draft:", e2)

    full = m.make_request("GET", f"/listings/{lid}")
    print("listing_id:", lid)
    print("state:", full.get("state"))
    print("url:", full.get("url") or f"https://www.etsy.com/listing/{lid}")
    return lid


if __name__ == "__main__":
    main()
