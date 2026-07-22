"""Create the custom pet paint-by-numbers DRAFT listing on Etsy.

Run from anywhere; paths resolve relative to the repo root. Listing images are
expected in ./listing (build them with make_listing_images.py first).
"""
import os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)
os.chdir(_REPO)  # etsy_token.json is cwd-relative
import etsy_manager

LDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listing")

TITLE = ("Custom Pet Portrait Paint by Numbers from Your Photo | "
         "Personalized Dog & Cat Paint by Number Kit | Printable Pet Memorial Gift")

PRICE = 12.99
TAXONOMY = 2078  # Digital Prints

# Tags optimized with eRank (Jul 2026). All <=20 chars (Etsy hard limit).
# Strong low-comp: paint by numbers (15.6k) / paint by number kit (11.8k).
# High demand: custom pet portrait (5.3k) / pet portrait (9k) / pet memorial gift (5.5k).
TAGS = [
    "paint by numbers", "paint by number kit", "custom pet portrait",
    "custom pet painting", "pet memorial gift", "custom cat portrait",
    "custom dog portrait", "pet coloring page", "pet portrait",
    "portrait from photo", "dog portrait", "cat portrait", "personalized pet",
]

DESC = """Turn your favorite pet photo into a custom paint-by-numbers you can print and paint at home. A personalized, hand-painted keepsake — a one-of-a-kind gift for any dog or cat lover, and a heartfelt pet memorial to honor a companion you'll always remember.

— A MEANINGFUL PET MEMORIAL —
Painting your pet, square by square, is a calm and personal way to remember them. The finished piece becomes a lasting custom portrait to frame — a thoughtful memorial gift for yourself or for anyone grieving a beloved dog or cat.

— WHAT YOU GET —
- 6 print sizes in one bundle: A3, A2, A1 and US 14x11, 20x16, 24x18 inches
- For every size: a numbered paint-by-numbers sheet AND a full-color reference image
- 300 DPI, print-ready PNG files
- A short print guide

— HOW IT WORKS —
1. Buy this listing.
2. Send us your pet photo through Etsy Messages.
3. Within 1-3 days we send you a private download link with your custom bundle.

This is a made-to-order digital product. Nothing is shipped — you receive digital files to print yourself at home or at any print shop.

— FOR THE BEST RESULT, YOUR PHOTO SHOULD BE —
- Clear and in focus, with good lighting
- Taken so your pet clearly stands out from the background
- A close-up, front or side view (landscape, portrait or square all work)
Blurry, dark or low-contrast photos lose detail in the final design.

— ONE DESIGN, MANY SIZES —
It is the same picture at every size, so you can print it as small or as large as you like. Bigger paper means bigger, easier-to-paint squares.

— PLEASE NOTE —
- Digital download only. No physical item will be shipped.
- Colors may vary slightly depending on your screen and printer.
- For personal use. This is a hand-made custom design, not a mass-produced file.

Made with love by MathRelaxing."""

PERSONALIZATION = ("After you order, please message us your pet photo through Etsy "
                   "(clear, well-lit, with your pet standing out from the background). "
                   "You can add any notes about your pet here.")


def main():
    assert len(TITLE) <= 140, f"title too long: {len(TITLE)}"
    assert TITLE.count("&") <= 1
    assert not any(ch in TITLE for ch in "^=+"), "forbidden char in title"
    print(f"title {len(TITLE)} chars OK | tags {len(TAGS)} | price ${PRICE}")

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True,
                                 quantity=999, tags=TAGS)
    print("draft listing id:", lid)

    # made-to-order + personalization (who_made/when_made/is_supply sent together)
    try:
        m.update_listing(lid, who_made="i_did", when_made="made_to_order", is_supply=False,
                         is_personalizable=True, personalization_is_required=False,
                         personalization_char_count_max=256,
                         personalization_instructions=PERSONALIZATION)
    except Exception as e:
        print("  made_to_order/personalization PATCH warn:", str(e)[:120])

    # images in order: cover, sizes, how
    for rank, fn in enumerate(["01_cover.png", "02_sizes.png", "03_how.png"], start=1):
        p = os.path.join(LDIR, fn)
        try:
            m.upload_listing_image(lid, p, rank=rank)
            print(f"  uploaded {fn} rank={rank}")
        except Exception as e:
            print(f"  image {fn} err:", str(e)[:120])

    print("\nDONE. Draft listing", lid, "created (state=draft).")
    print("Review at: Etsy Shop Manager > Listings > Drafts")


if __name__ == "__main__":
    main()
