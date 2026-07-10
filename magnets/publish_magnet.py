"""
publish_magnet.py — POD fractal magnet via Printify (Etsy's #1 underserved
low-cost niche in our market scan: "math magnet" = 285 competitors but a top
listing with 2,851 favourites).

Blueprint 428 "Magnets" (SPOKE Custom Products), square print area, sizes
3in / 4in / 6in. The artwork is a Julia-set fractal rendered by
build_fractal_palettes.render_fractal at 1800px (full-bleed, reads great small).

Flow (mirrors printify/printify_publish.py, the poster pilot):
  create   — upload art + create the product in Printify (NOT on Etsy yet),
             print the cost/retail margin table.
  publish  — push it to the connected Etsy shop. NOTE: Printify publishes as
             an ACTIVE Etsy listing, so per the house "drafts only" convention
             this must be run only with explicit permission; immediately after,
             set the Etsy listing inactive (or enable Printify's "publish as
             draft" option first).

Pilot already created 2026-07-10: product_id 6a5116a4604797a6fa0f66b6,
retail 3in $8.99 / 4in $11.99 / 6in $15.99 (cost $2.82 / $3.22 / $4.83).

  python publish_magnet.py create   # (re)create the product in Printify
  python publish_magnet.py publish <product_id>   # push to Etsy (guarded)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "printify"))
import printify_publish as pp

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "Amethyst_Julia_1800.png")

BLUEPRINT_MAGNET = 428
PROVIDER_SPOKE = 1
SIZES = {62034: 899, 62035: 1199, 62036: 1599}   # 3x3, 4x4, 6x6 (retail cents)

TITLE = ("Fractal Math Art Fridge Magnet - Julia Set Purple Amethyst - "
         "Science Geometry Gift for Kitchen Office Locker Decor")
DESC = ("A vivid fractal magnet for anyone who loves mathematics. This is the Julia set "
        "(constant c = 0.285 + 0.01i), computed from its equation in Python and rendered as a "
        "luminous amethyst bloom - no AI, no stock art, pure mathematics made visible.\n\n"
        "Bright, durable and full-bleed, it turns a fridge, locker, whiteboard or office cabinet "
        "into a little piece of generative math art. A perfect small gift for a mathematician, "
        "physicist, engineer, teacher or science student.\n\n"
        "Available in 3 sizes (3in, 4in, 6in). Made on demand and shipped for you.\n\n"
        "MathRelaxing - every design in this shop is written from scratch in code.")
TAGS = ["fractal art", "math magnet", "julia set", "science gift", "geometric magnet",
        "fridge magnet", "math art", "purple decor", "stem gift", "generative art"]


def create():
    img = pp.upload_image(ART, "amethyst_julia_magnet.png")
    prod = pp.create_poster(TITLE, DESC, img, sizes_prices=SIZES, tags=TAGS,
                            blueprint_id=BLUEPRINT_MAGNET, provider_id=PROVIDER_SPOKE)
    print("PRODUCT ID:", prod["id"])
    pp.margin_report(prod)
    return prod["id"]


def publish(product_id):
    """Push to Etsy. Goes ACTIVE — run only with explicit permission, then set
    the Etsy listing inactive to honour the drafts-only convention."""
    return pp.publish_product(product_id)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create()
    elif len(sys.argv) > 2 and sys.argv[1] == "publish":
        print(publish(sys.argv[2]))
    else:
        print(__doc__)
