"""One-shot: fix Metatron POD title + set Printify production partner."""
import etsy_manager

PARTNER = 5702392
m = etsy_manager.EtsyManager()

m.update_listing(
    4544068954,
    title=(
        "Metatron's Cube Poster | Sacred Geometry Wall Art | "
        "Black White Minimalist Line Art Print"
    ),
    who_made="someone_else",
    when_made="made_to_order",
    is_supply=False,
    production_partner_ids=str(PARTNER),
)
m.update_listing(
    4544054415,
    who_made="someone_else",
    when_made="made_to_order",
    is_supply=False,
    production_partner_ids=str(PARTNER),
)

for lid in (4544068954, 4544054415):
    L = m.make_request("GET", f"/listings/{lid}")
    print(
        lid,
        (L.get("title") or "")[:70],
        L.get("who_made"),
        L.get("when_made"),
        L.get("production_partners"),
    )
