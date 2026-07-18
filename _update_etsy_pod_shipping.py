"""
Update active physical Etsy listings with realistic POD production times
and a clear shipping/production blurb in the description.

Also ensure Printify shipping profiles cover rest-of-world with 10–30 day transit.

Does NOT change prices or stock.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from etsy_manager import CLIENT_ID, SHARED_SECRET, EtsyManager

# Production / print time (business days) — conservative vs Printify 2–7 + buffer
PROC_MIN = 7
PROC_MAX = 10

MARKER_START = "—— SHIPPING & PRODUCTION ——"
MARKER_END = "—— END SHIPPING ——"

SHIPPING_BLURB_PRINTIFY = f"""
{MARKER_START}
Made to order (print on demand) — not drop-shipped from a warehouse of pre-prints.

• Production / processing: about {PROC_MIN}–{PROC_MAX} business days after your order
• Shipping (after production):
  – United States: about 2–5 business days in transit
  – Canada: about 10–30 business days in transit
  – Rest of world: about 10–30 business days in transit (customs may add time)

Total delivery time depends on your country. US orders typically arrive in about 1–2 weeks; international orders often take 3–5+ weeks.

Tracking is provided when the print partner ships your order.
Frame not included (posters).
{MARKER_END}
""".strip()

SHIPPING_BLURB_LULU = f"""
{MARKER_START}
Printed on demand and shipped by our print partner (Lulu).

• Production / processing: about {PROC_MIN}–{PROC_MAX} business days after your order
• Shipping times vary by destination and method selected at checkout
• United States: often about 1–3 weeks total; international longer once customs is involved

Tracking is provided when the order ships.
{MARKER_END}
""".strip()


def upsert_blurb(description: str, blurb: str) -> str:
    desc = description or ""
    if MARKER_START in desc and MARKER_END in desc:
        pattern = re.compile(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            re.DOTALL,
        )
        return pattern.sub(blurb, desc).strip()
    # strip older similar blocks if any
    desc = re.sub(
        r"\n*Made to order \(print on demand\).*?(?=\n\n|\Z)",
        "",
        desc,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return (desc.rstrip() + "\n\n" + blurb + "\n").strip()


def patch_listing_json(m: EtsyManager, shop_id: int, listing_id: int, fields: dict) -> dict:
    """PATCH with JSON body (needed for some integer fields)."""
    url = f"{m.base_url}/shops/{shop_id}/listings/{listing_id}"
    data = json.dumps(fields).encode("utf-8")
    headers = {
        "x-api-key": f"{CLIENT_ID}:{SHARED_SECRET}",
        "Authorization": f"Bearer {m.token_data['access_token']}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        if e.code == 401:
            m.refresh_token()
            headers["Authorization"] = f"Bearer {m.token_data['access_token']}"
            req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        body = e.read().decode("utf-8")
        raise RuntimeError(f"PATCH listing {listing_id} HTTP {e.code}: {body[:400]}")


def form_patch(m: EtsyManager, shop_id: int, listing_id: int, fields: dict) -> dict:
    return m.make_request(
        "PATCH",
        f"/shops/{shop_id}/listings/{listing_id}",
        payload=fields,
    )


def ensure_row_destination(m: EtsyManager, shop_id: int, profile_id: int,
                           primary: float, secondary: float,
                           min_d: int, max_d: int) -> str:
    """Ensure a catch-all / rest-of-world destination exists with transit days."""
    p = m.make_request("GET", f"/shops/{shop_id}/shipping-profiles/{profile_id}")
    dests = p.get("shipping_profile_destinations") or []
    # Look for empty-country or ZZ-like worldwide destination
    worldwide = [
        d for d in dests
        if not d.get("destination_country_iso")
        or d.get("destination_country_iso") in ("", None)
    ]
    # Also check if non-US/CA countries exist
    countries = {d.get("destination_country_iso") for d in dests}
    has_us = "US" in countries
    has_ca = "CA" in countries
    only_us_ca = countries <= {"US", "CA", "", None}

    if worldwide:
        d = worldwide[0]
        did = d["shipping_profile_destination_id"]
        # update delivery days if missing
        if d.get("min_delivery_days") is None or d.get("max_delivery_days") is None:
            try:
                m.make_request(
                    "PUT",
                    f"/shops/{shop_id}/shipping-profiles/{profile_id}/destinations/{did}",
                    payload={
                        "primary_cost": primary,
                        "secondary_cost": secondary,
                        "min_delivery_days": min_d,
                        "max_delivery_days": max_d,
                    },
                )
                return f"updated worldwide dest {did}"
            except Exception as e:
                return f"worldwide exists {did}, update failed: {e}"
        return f"worldwide dest ok {did} ({d.get('min_delivery_days')}-{d.get('max_delivery_days')}d)"

    if only_us_ca and has_us:
        # create rest-of-world destination (empty country iso)
        try:
            # Etsy expects form fields
            m.make_request(
                "POST",
                f"/shops/{shop_id}/shipping-profiles/{profile_id}/destinations",
                payload={
                    "primary_cost": primary,
                    "secondary_cost": secondary,
                    "min_delivery_days": min_d,
                    "max_delivery_days": max_d,
                    "destination_country_iso": "",
                    "destination_region": "none",
                },
            )
            return "created rest-of-world destination"
        except Exception as e:
            # try without empty iso — use non_eu region
            try:
                m.make_request(
                    "POST",
                    f"/shops/{shop_id}/shipping-profiles/{profile_id}/destinations",
                    payload={
                        "primary_cost": primary,
                        "secondary_cost": secondary,
                        "min_delivery_days": min_d,
                        "max_delivery_days": max_d,
                        "destination_region": "non_eu",
                    },
                )
                return "created non_eu destination"
            except Exception as e2:
                return f"create RoW failed: {e} | {e2}"
    return f"destinations already diverse: {countries}"


def main():
    m = EtsyManager()
    shop_id = m.get_shop_id()

    # 1) Shipping profiles: ensure RoW + transit labels where possible
    print("=== SHIPPING PROFILES ===")
    profile_notes = {}
    for pid, primary, secondary in [
        (310714340926, 14.99, 4.99),   # Standard Printify Choice
        (310656583069, 12.19, 2.99),   # Free Standard Printify
        (310608167423, 9.99, 6.99),    # Lulu
    ]:
        # set delivery days on CA if needed already ok
        note = ensure_row_destination(m, shop_id, pid, primary, secondary, 10, 30)
        profile_notes[pid] = note
        print(f"  profile {pid}: {note}")
        # US already 2-5 on Printify profiles; Lulu US has null days — set 5-15
        try:
            p = m.make_request("GET", f"/shops/{shop_id}/shipping-profiles/{pid}")
            for d in p.get("shipping_profile_destinations") or []:
                if d.get("destination_country_iso") == "US" and (
                    d.get("min_delivery_days") is None or d.get("max_delivery_days") is None
                ):
                    did = d["shipping_profile_destination_id"]
                    pc = d["primary_cost"]["amount"] / d["primary_cost"]["divisor"]
                    sc = d["secondary_cost"]["amount"] / d["secondary_cost"]["divisor"]
                    m.make_request(
                        "PUT",
                        f"/shops/{shop_id}/shipping-profiles/{pid}/destinations/{did}",
                        payload={
                            "primary_cost": pc,
                            "secondary_cost": sc,
                            "min_delivery_days": 5,
                            "max_delivery_days": 15,
                        },
                    )
                    print(f"    set US transit 5-15d on dest {did}")
                if d.get("destination_country_iso") == "CA" and (
                    d.get("min_delivery_days") is None
                ):
                    did = d["shipping_profile_destination_id"]
                    pc = d["primary_cost"]["amount"] / d["primary_cost"]["divisor"]
                    sc = d["secondary_cost"]["amount"] / d["secondary_cost"]["divisor"]
                    m.make_request(
                        "PUT",
                        f"/shops/{shop_id}/shipping-profiles/{pid}/destinations/{did}",
                        payload={
                            "primary_cost": pc,
                            "secondary_cost": sc,
                            "min_delivery_days": 10,
                            "max_delivery_days": 30,
                        },
                    )
                    print(f"    set CA transit 10-30d on dest {did}")
        except Exception as e:
            print(f"  dest update note: {e}")

    # 2) Active physical listings
    print("\n=== UPDATE ACTIVE PHYSICAL LISTINGS ===")
    r = m.make_request("GET", f"/shops/{shop_id}/listings?state=active&limit=100")
    listings = r.get("results") or []
    physical = [
        L for L in listings
        if not L.get("is_digital") and (L.get("listing_type") or L.get("type")) != "download"
    ]
    # re-filter: listing_type physical
    physical = []
    for L in listings:
        lt = L.get("listing_type") or L.get("type")
        if L.get("is_digital") or lt == "download":
            continue
        if lt == "physical" or L.get("shipping_profile_id"):
            physical.append(L)

    print(f"physical active: {len(physical)}")
    results = []
    for L in physical:
        lid = L["listing_id"]
        title = (L.get("title") or "")[:55]
        ship_id = L.get("shipping_profile_id")
        is_lulu = ship_id == 310608167423 or "coloring book" in (L.get("title") or "").lower()
        blurb = SHIPPING_BLURB_LULU if is_lulu else SHIPPING_BLURB_PRINTIFY
        old_desc = L.get("description") or ""
        new_desc = upsert_blurb(old_desc, blurb)
        old_proc = (L.get("processing_min"), L.get("processing_max"))

        row = {"listing_id": lid, "title": title, "old_proc": old_proc, "ship_id": ship_id}
        try:
            # Prefer form-encoded (EtsyManager default) — matches create_draft_listing style
            form_patch(
                m,
                shop_id,
                lid,
                {
                    "processing_min": PROC_MIN,
                    "processing_max": PROC_MAX,
                    "description": new_desc,
                },
            )
            row["ok"] = True
            row["desc_changed"] = new_desc != old_desc
            print(f"  OK  {old_proc}→({PROC_MIN},{PROC_MAX})  {title}")
        except Exception as e1:
            try:
                patch_listing_json(
                    m,
                    shop_id,
                    lid,
                    {
                        "processing_min": PROC_MIN,
                        "processing_max": PROC_MAX,
                        "description": new_desc,
                    },
                )
                row["ok"] = True
                row["via"] = "json"
                print(f"  OK(json) {old_proc}→({PROC_MIN},{PROC_MAX})  {title}")
            except Exception as e2:
                row["ok"] = False
                row["error"] = f"{e1} | {e2}"[:400]
                print(f"  FAIL {title}: {row['error'][:200]}")
        results.append(row)
        time.sleep(0.25)

    # verify sample
    print("\n=== VERIFY ===")
    r2 = m.make_request("GET", f"/shops/{shop_id}/listings?state=active&limit=100")
    proc_counts = {}
    for L in r2.get("results") or []:
        lt = L.get("listing_type") or L.get("type")
        if L.get("is_digital") or lt == "download":
            continue
        if lt != "physical" and not L.get("shipping_profile_id"):
            continue
        key = (L.get("processing_min"), L.get("processing_max"))
        proc_counts[key] = proc_counts.get(key, 0) + 1
        has = MARKER_START in (L.get("description") or "")
        print(
            f"  proc={key} blurb={'Y' if has else 'N'}  "
            f"{(L.get('title') or '')[:50]}"
        )

    ok = sum(1 for r in results if r.get("ok"))
    print(f"\nDONE updated={ok}/{len(results)}")
    print("processing distribution after:", proc_counts)

    out = Path("printify/_etsy_shipping_update_report.json")
    out.write_text(
        json.dumps(
            {
                "proc": [PROC_MIN, PROC_MAX],
                "profile_notes": profile_notes,
                "results": results,
                "verify_proc_counts": {str(k): v for k, v in proc_counts.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("report", out)


if __name__ == "__main__":
    main()
