"""Probe how to update Etsy listing price via inventory API."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from etsy_manager import CLIENT_ID, SHARED_SECRET, EtsyManager

LID = 4540003882


def put_json(m: EtsyManager, endpoint: str, body: dict):
    url = f"https://api.etsy.com/v3/application{endpoint}"
    data = json.dumps(body).encode("utf-8")
    headers = {
        "x-api-key": f"{CLIENT_ID}:{SHARED_SECRET}",
        "Authorization": f"Bearer {m.token_data['access_token']}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    m = EtsyManager()
    shop = m.get_shop_id()
    inv = m.make_request("GET", f"/listings/{LID}/inventory")
    print("GET inventory OK, old price:", inv["products"][0]["offerings"][0]["price"])

    body = {
        "products": [
            {
                "sku": "",
                "property_values": [],
                "offerings": [
                    {
                        "price": 2.99,
                        "quantity": 999,
                        "is_enabled": True,
                    }
                ],
            }
        ]
    }

    for ep in [
        f"/listings/{LID}/inventory",
        f"/shops/{shop}/listings/{LID}/inventory",
    ]:
        code, res = put_json(m, ep, body)
        print(f"\nPUT {ep} → {code}")
        if isinstance(res, dict) and "products" in res:
            print("  new:", res["products"][0]["offerings"][0]["price"])
        else:
            print(" ", str(res)[:400])

    listing = m.make_request("GET", f"/listings/{LID}")
    p = listing["price"]
    print("\nlisting price:", p["amount"] / p["divisor"] if isinstance(p, dict) else p)


if __name__ == "__main__":
    main()
