"""Create the DRAFT Etsy listing for the boho botanical Set of 3 printable,
with a Palette variation (Blue & Cream / Terracotta). Both colorways are
included in the download. DRAFT only."""
import os, sys
sys.path.insert(0, "/home/user/Etsy_mathrelaxing")
os.chdir("/home/user/Etsy_mathrelaxing")
import etsy_manager

H = os.path.dirname(os.path.abspath(__file__))
LST = os.path.join(H, "listing")
CUSTOM_PROP = 513

TITLE = ("Set of 3 Boho Botanical Wall Art | Printable Abstract Line Art | Blue Cream "
         "and Terracotta | Mid Century Prints | Instant Download")
PRICE = 9.99
TAXONOMY = 2078

TAGS = [
    "boho wall art", "botanical print", "set of 3 prints", "printable wall art",
    "abstract line art", "mid century art", "terracotta print", "boho decor",
    "minimalist print", "gallery wall set", "neutral wall art", "living room art",
    "instant download",
]

DESC = """SET OF 3 — BOHO BOTANICAL WALL ART (Printable)
Minimalist abstract line-art in a calm, mid-century boho style — soft shapes, botanical leaf branches, and arch motifs that make an effortless gallery wall.

★ BOTH COLORWAYS INCLUDED ★
Your download contains BOTH palettes — Blue & Cream AND Terracotta — 6 prints in total. (Pick your favorite in the dropdown; you'll receive both.)

— WHAT YOU GET —
- 2 colorways × 3 coordinated designs = 6 high-resolution PNG files
- 300 DPI, 2:3 ratio — fits every standard frame with no cropping
- Prints beautifully from 4x6 up to 24x36 inches (and A5–A2)
- A size & print guide (PDF)

— HOW IT WORKS —
1. Buy and download instantly (ZIP files).
2. Print at home, at a local shop, or upload to a print service.
3. Frame and enjoy. Matte or textured art paper looks best.

— PLEASE NOTE —
- Digital download only — nothing is shipped.
- For personal use. Colors may vary slightly by screen and printer.

Designed by MathRelaxing."""

IMAGES = ["01_wall_blue.jpg", "02_wall_terra.jpg", "03_grid_blue.jpg", "04_grid_terra.jpg", "05_what_you_get.jpg"]
ZIPS = [os.path.join(H, "MathRelaxing_Boho_blue.zip"), os.path.join(H, "MathRelaxing_Boho_terra.zip")]
VARIANTS = [("BOHO-BLUE", "Blue & Cream"), ("BOHO-TERRA", "Terracotta")]


def main():
    assert len(TITLE) <= 140, f"title {len(TITLE)}"
    assert TITLE.count("&") <= 1 and not any(c in TITLE for c in "^=+")
    print(f"title {len(TITLE)} OK | tags {len(TAGS)} | ${PRICE}")
    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, quantity=999, tags=TAGS)
    print("draft:", lid)
    for rank, fn in enumerate(IMAGES, 1):
        try: m.upload_listing_image(lid, os.path.join(LST, fn), rank=rank)
        except Exception as e: print(" img", fn, "err", str(e)[:120])
    for z in ZIPS:
        try: m.upload_listing_file(lid, z)
        except Exception as e: print(" file", os.path.basename(z), "err", str(e)[:120])
    # Palette variation (same price on both)
    inv = {"products": [
        {"sku": sku, "property_values": [{"property_id": CUSTOM_PROP, "property_name": "Palette",
          "scale_id": None, "value_ids": [], "values": [label]}],
         "offerings": [{"price": PRICE, "quantity": 999, "is_enabled": True}]}
        for sku, label in VARIANTS],
        "price_on_property": [], "quantity_on_property": [], "sku_on_property": [CUSTOM_PROP]}
    try:
        m.make_request("PUT", f"/listings/{lid}/inventory", payload=inv, json_body=True)
        print("  palette variation set")
    except Exception as e:
        print("  inventory err:", str(e)[:200])
    print("DONE draft", lid, f"https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
