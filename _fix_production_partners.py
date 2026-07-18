"""
Set correct About-this-listing fields for POD physicals:
  who_made = i_did (you design)
  when_made = made_to_order
  is_supply = false
  production_partner_ids = Printify or Lulu partner

Matches Etsy UI:
  "Diseñé este artículo, pero un partner de producción lo fabrica"
"""
from __future__ import annotations

import time
from etsy_manager import EtsyManager

# From GET /shops/{id}/production-partners
PARTNER_PRINTIFY = 5702392  # Print-on-demand printing partner, Chatsworth CA
PARTNER_LULU = 5702394      # Print-on-demand book printing partner, Morrisville NC

LULU_SHIPPING_PROFILE = 310608167423


def main():
    m = EtsyManager()
    shop = m.get_shop_id()

    partners = m.make_request("GET", f"/shops/{shop}/production-partners")
    print("shop production partners:")
    for p in partners.get("results") or []:
        print(" ", p.get("production_partner_id"), p.get("partner_name"), p.get("location"))

    r = m.make_request("GET", f"/shops/{shop}/listings?state=active&limit=100")
    physical = []
    for L in r.get("results") or []:
        lt = L.get("listing_type") or L.get("type")
        if L.get("is_digital") or lt == "download":
            continue
        if lt == "physical" or L.get("shipping_profile_id"):
            physical.append(L)
    print(f"\nphysical active: {len(physical)}")

    ok = fail = 0
    for L in physical:
        lid = L["listing_id"]
        title = (L.get("title") or "")[:55]
        ship = L.get("shipping_profile_id")
        is_book = (
            ship == LULU_SHIPPING_PROFILE
            or "coloring book" in (L.get("title") or "").lower()
        )
        partner = PARTNER_LULU if is_book else PARTNER_PRINTIFY

        # Etsy form-encode: production_partner_ids may need comma-separated
        payload = {
            "who_made": "i_did",
            "when_made": "made_to_order",
            "is_supply": "false",
            "production_partner_ids": str(partner),
        }
        try:
            m.make_request(
                "PATCH",
                f"/shops/{shop}/listings/{lid}",
                payload=payload,
            )
            ok += 1
            print(f"  OK partner={partner}  {title}")
        except Exception as e:
            # try alternate key names / array style via JSON
            try:
                import json
                import urllib.request
                from etsy_manager import CLIENT_ID, SHARED_SECRET

                url = f"{m.base_url}/shops/{shop}/listings/{lid}"
                body = {
                    "who_made": "i_did",
                    "when_made": "made_to_order",
                    "is_supply": False,
                    "production_partner_ids": [partner],
                }
                data = json.dumps(body).encode("utf-8")
                headers = {
                    "x-api-key": f"{CLIENT_ID}:{SHARED_SECRET}",
                    "Authorization": f"Bearer {m.token_data['access_token']}",
                    "Content-Type": "application/json",
                }
                req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
                with urllib.request.urlopen(req) as resp:
                    resp.read()
                ok += 1
                print(f"  OK(json) partner={partner}  {title}")
            except Exception as e2:
                fail += 1
                print(f"  FAIL {title}: {e} | {e2}")
        time.sleep(0.2)

    print("\n=== VERIFY sample ===")
    for L in physical[:5]:
        full = m.make_request("GET", f"/listings/{L['listing_id']}")
        print(
            f"  who={full.get('who_made')} when={full.get('when_made')} "
            f"supply={full.get('is_supply')} partners={full.get('production_partners')}  "
            f"{(full.get('title') or '')[:40]}"
        )

    print(f"\nDONE ok={ok} fail={fail}")


if __name__ == "__main__":
    main()
