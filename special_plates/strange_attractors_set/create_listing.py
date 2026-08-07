"""Create + activate Etsy listing for Strange Attractors Poster Set of 6."""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from etsy_manager import EtsyManager

HERE = os.path.join(ROOT, "special_plates", "strange_attractors_set")
ZIP = os.path.join(HERE, "Strange_Attractors_Poster_Set_of_6.zip")
PREV = os.path.join(HERE, "previews")
IMAGES = [
    os.path.join(PREV, "strange_attractors_preview_1_hero.jpg"),
    os.path.join(PREV, "strange_attractors_preview_2_included.jpg"),
    os.path.join(PREV, "strange_attractors_preview_3_eq.jpg"),
    os.path.join(PREV, "strange_attractors_preview_4_eq.jpg"),
    os.path.join(PREV, "strange_attractors_preview_5_eq.jpg"),
    os.path.join(PREV, "strange_attractors_preview_6_eq.jpg"),
]

TAXONOMY = 2078
PRICE = 12.99

TITLE = (
    "Strange Attractors Poster Set of 6 | Chaos Theory Wall Art | "
    "Lorenz Rossler Thomas Chen Math Digital Download"
)

TAGS = [
    "chaos theory art",
    "strange attractor",
    "lorenz attractor",
    "math wall art",
    "physics wall art",
    "science wall art",
    "fractal art",
    "stem wall art",
    "digital download",
    "math poster set",
    "classroom decor",
    "nerd gift",
    "equation poster",
]

DESC = """STRANGE ATTRACTORS — SET OF 6
Elegant dark-observatory plates of deterministic chaos. Each design is integrated from the classic ODE system and rendered as a fine trajectory on a deep black field — gallery wall art for mathematicians, physicists, and chaos lovers.

— WHAT'S INCLUDED —
1. Lorenz — the classic butterfly
2. Rössler — minimal continuous chaos
3. Thomas — cyclic sine labyrinth
4. Four-Wing — multi-scroll chaos
5. Chen — dual-wing dissipative flow
6. Aizawa — sphere-like strange cloud

Print-ready JPG files @ 300 dpi (2×3 and A4 for every design).

— DESIGN —
Scientific-plate layout with reserved zones for title, graphic, caption, and governing equations — no text colliding with the orbit.

— PERFECT FOR —
Math/physics classrooms, offices, studios, STEM gifts, chaos theory fans.

Instant download by MathRelaxing.
"""


def main():
    for p in [ZIP, *IMAGES]:
        if not os.path.isfile(p):
            raise SystemExit(f"Missing {p}")

    m = EtsyManager()
    lid = m.create_full_product(
        TITLE, DESC, PRICE, TAXONOMY,
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
