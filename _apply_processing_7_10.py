"""
With shops_w token: create 7-10 processing profile, attach to physical listings,
and ensure shipping profile destinations include RoW with transit days.
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from etsy_manager import EtsyManager

PROC_MIN = 7
PROC_MAX = 10


def main():
    m = EtsyManager()
    shop = m.get_shop_id()
    print("shop", shop)

    # 1) List / create readiness definition 7-10
    defs = m.make_request("GET", f"/shops/{shop}/readiness-state-definitions")
    results = defs.get("results") or []
    print("existing readiness defs:")
    rid_710 = None
    for d in results:
        print(
            " ",
            d.get("readiness_state_id"),
            d.get("readiness_state"),
            d.get("min_processing_days"),
            d.get("max_processing_days"),
            d.get("processing_days_display_label"),
        )
        if (
            d.get("readiness_state") == "made_to_order"
            and int(d.get("min_processing_days") or 0) == PROC_MIN
            and int(d.get("max_processing_days") or 0) == PROC_MAX
        ):
            rid_710 = d["readiness_state_id"]

    if not rid_710:
        # try create
        for payload in [
            {
                "readiness_state": "made_to_order",
                "min_processing_days": PROC_MIN,
                "max_processing_days": PROC_MAX,
            },
            {
                "readiness_state": "made_to_order",
                "min_processing_time": PROC_MIN,
                "max_processing_time": PROC_MAX,
            },
        ]:
            try:
                created = m.make_request(
                    "POST",
                    f"/shops/{shop}/readiness-state-definitions",
                    payload=payload,
                )
                print("CREATED", created)
                rid_710 = created.get("readiness_state_id") or (
                    (created.get("results") or [{}])[0].get("readiness_state_id")
                )
                if rid_710:
                    break
            except Exception as e:
                print("create fail", payload, e)

    # If still none, try UPDATE the 2-5 profile in place
    if not rid_710:
        for d in results:
            if int(d.get("min_processing_days") or 0) == 2 and int(
                d.get("max_processing_days") or 0
            ) == 5:
                rid = d["readiness_state_id"]
                try:
                    updated = m.make_request(
                        "PUT",
                        f"/shops/{shop}/readiness-state-definitions/{rid}",
                        payload={
                            "readiness_state": "made_to_order",
                            "min_processing_days": PROC_MIN,
                            "max_processing_days": PROC_MAX,
                        },
                    )
                    print("UPDATED def", rid, updated)
                    rid_710 = rid
                    break
                except Exception as e:
                    print("update def fail", e)

    if not rid_710:
        # re-list
        defs = m.make_request("GET", f"/shops/{shop}/readiness-state-definitions")
        for d in defs.get("results") or []:
            if int(d.get("min_processing_days") or 0) == PROC_MIN:
                rid_710 = d["readiness_state_id"]
                break

    print("rid_710 =", rid_710)
    if not rid_710:
        raise SystemExit("Could not create/find 7-10 readiness definition")

    # 2) Shipping profiles RoW
    print("\n=== SHIPPING PROFILES ===")
    for pid, primary, secondary in [
        (310714340926, 14.99, 4.99),
        (310656583069, 12.19, 2.99),
        (310608167423, 9.99, 6.99),
    ]:
        try:
            p = m.make_request("GET", f"/shops/{shop}/shipping-profiles/{pid}")
        except Exception as e:
            print("profile get fail", pid, e)
            continue
        dests = p.get("shipping_profile_destinations") or []
        countries = {d.get("destination_country_iso") for d in dests}
        print(f"profile {pid} countries={countries}")

        # Fix US/CA null transit
        for d in dests:
            iso = d.get("destination_country_iso")
            did = d["shipping_profile_destination_id"]
            pc = d["primary_cost"]["amount"] / d["primary_cost"]["divisor"]
            sc = d["secondary_cost"]["amount"] / d["secondary_cost"]["divisor"]
            if iso == "US" and (
                d.get("min_delivery_days") is None or d.get("max_delivery_days") is None
            ):
                try:
                    m.make_request(
                        "PUT",
                        f"/shops/{shop}/shipping-profiles/{pid}/destinations/{did}",
                        payload={
                            "primary_cost": pc,
                            "secondary_cost": sc,
                            "min_delivery_days": 2 if pid != 310608167423 else 5,
                            "max_delivery_days": 5 if pid != 310608167423 else 15,
                        },
                    )
                    print("  US transit set", did)
                except Exception as e:
                    print("  US set fail", e)
            if iso == "CA" and d.get("min_delivery_days") is None:
                try:
                    m.make_request(
                        "PUT",
                        f"/shops/{shop}/shipping-profiles/{pid}/destinations/{did}",
                        payload={
                            "primary_cost": pc,
                            "secondary_cost": sc,
                            "min_delivery_days": 10,
                            "max_delivery_days": 30,
                        },
                    )
                    print("  CA transit set", did)
                except Exception as e:
                    print("  CA set fail", e)
            # empty iso worldwide without days
            if (not iso) and (
                d.get("min_delivery_days") is None or d.get("max_delivery_days") is None
            ):
                try:
                    m.make_request(
                        "PUT",
                        f"/shops/{shop}/shipping-profiles/{pid}/destinations/{did}",
                        payload={
                            "primary_cost": pc,
                            "secondary_cost": sc,
                            "min_delivery_days": 10,
                            "max_delivery_days": 30,
                        },
                    )
                    print("  RoW transit set", did)
                except Exception as e:
                    print("  RoW set fail", e)

        has_worldwide = any(not d.get("destination_country_iso") for d in dests)
        if not has_worldwide and countries <= {"US", "CA", None, ""}:
            try:
                m.make_request(
                    "POST",
                    f"/shops/{shop}/shipping-profiles/{pid}/destinations",
                    payload={
                        "primary_cost": primary,
                        "secondary_cost": secondary,
                        "min_delivery_days": 10,
                        "max_delivery_days": 30,
                        "destination_country_iso": "",
                        "destination_region": "none",
                    },
                )
                print("  created RoW dest")
            except Exception as e:
                try:
                    m.make_request(
                        "POST",
                        f"/shops/{shop}/shipping-profiles/{pid}/destinations",
                        payload={
                            "primary_cost": primary,
                            "secondary_cost": secondary,
                            "min_delivery_days": 10,
                            "max_delivery_days": 30,
                            "destination_region": "non_eu",
                        },
                    )
                    print("  created non_eu dest")
                except Exception as e2:
                    try:
                        m.make_request(
                            "POST",
                            f"/shops/{shop}/shipping-profiles/{pid}/destinations",
                            payload={
                                "primary_cost": primary,
                                "secondary_cost": secondary,
                                "min_delivery_days": 10,
                                "max_delivery_days": 30,
                                "destination_region": "eu",
                            },
                        )
                        print("  created eu dest")
                    except Exception as e3:
                        print("  create dest fail", e, "|", e2, "|", e3)

    # 3) Update physical listings: readiness_state_id + inventory offerings
    print("\n=== LISTINGS ===")
    r = m.make_request("GET", f"/shops/{shop}/listings?state=active&limit=100")
    physical = []
    for L in r.get("results") or []:
        lt = L.get("listing_type") or L.get("type")
        if L.get("is_digital") or lt == "download":
            continue
        if lt == "physical" or L.get("shipping_profile_id"):
            physical.append(L)
    print("physical", len(physical))

    ok = 0
    for L in physical:
        lid = L["listing_id"]
        title = (L.get("title") or "")[:50]
        try:
            # listing-level readiness + processing
            m.make_request(
                "PATCH",
                f"/shops/{shop}/listings/{lid}",
                payload={
                    "readiness_state_id": rid_710,
                    "processing_min": PROC_MIN,
                    "processing_max": PROC_MAX,
                },
            )
        except Exception as e:
            print(f"  listing patch fail {lid}: {e}")

        # inventory-level readiness on each offering
        try:
            inv = m.make_request("GET", f"/listings/{lid}/inventory")
            products_out = []
            for prod in inv.get("products") or []:
                offerings_out = []
                for off in prod.get("offerings") or []:
                    if off.get("is_deleted"):
                        continue
                    price = off.get("price") or {}
                    if isinstance(price, dict):
                        price_val = price.get("amount", 0) / max(price.get("divisor") or 100, 1)
                    else:
                        price_val = float(price)
                    offerings_out.append(
                        {
                            "price": price_val,
                            "quantity": int(off.get("quantity") or 999),
                            "is_enabled": bool(off.get("is_enabled", True)),
                            "readiness_state_id": int(rid_710),
                        }
                    )
                if not offerings_out:
                    continue
                pvs = []
                for pv in prod.get("property_values") or []:
                    pvs.append(
                        {
                            "property_id": pv.get("property_id"),
                            "value_ids": pv.get("value_ids") or [],
                            "values": pv.get("values") or [],
                            "property_name": pv.get("property_name") or "",
                            "scale_id": pv.get("scale_id"),
                        }
                    )
                products_out.append(
                    {
                        "sku": prod.get("sku") or "",
                        "property_values": pvs,
                        "offerings": offerings_out,
                    }
                )
            if products_out:
                body = {"products": products_out}
                for key in ("price_on_property", "quantity_on_property", "sku_on_property"):
                    if inv.get(key):
                        body[key] = inv[key]
                # readiness_state_on_property sometimes needed
                if inv.get("readiness_state_on_property") is not None:
                    body["readiness_state_on_property"] = inv["readiness_state_on_property"]

                import urllib.request
                from etsy_manager import CLIENT_ID, SHARED_SECRET

                url = f"{m.base_url}/listings/{lid}/inventory"
                data = json.dumps(body).encode("utf-8")
                headers = {
                    "x-api-key": f"{CLIENT_ID}:{SHARED_SECRET}",
                    "Authorization": f"Bearer {m.token_data['access_token']}",
                    "Content-Type": "application/json",
                }
                req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
                with urllib.request.urlopen(req) as resp:
                    resp.read()
            ok += 1
            print(f"  OK {title}")
        except Exception as e:
            print(f"  FAIL inventory {title}: {e}")
        time.sleep(0.2)

    # 4) Verify
    print("\n=== VERIFY ===")
    r2 = m.make_request("GET", f"/shops/{shop}/listings?state=active&limit=100")
    pc = Counter()
    for L in r2.get("results") or []:
        lt = L.get("listing_type") or L.get("type")
        if L.get("is_digital") or lt == "download":
            continue
        if lt != "physical" and not L.get("shipping_profile_id"):
            continue
        key = (L.get("processing_min"), L.get("processing_max"), L.get("readiness_state_id"))
        pc[key] += 1
        print(
            f"  proc={L.get('processing_min')}-{L.get('processing_max')} "
            f"ready={L.get('readiness_state_id')}  {(L.get('title') or '')[:48]}"
        )
    print("counts", dict(pc))
    print(f"DONE inventory_ok={ok}/{len(physical)} rid={rid_710}")

    Path("printify/_processing_710_report.json").write_text(
        json.dumps({"rid_710": rid_710, "ok": ok, "total": len(physical), "counts": {str(k): v for k, v in pc.items()}}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
