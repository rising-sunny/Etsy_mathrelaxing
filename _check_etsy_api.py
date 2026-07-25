"""Quick Etsy API connectivity check."""
import json
from etsy_manager import EtsyManager

m = EtsyManager()
with open("etsy_token.json", encoding="utf-8") as f:
    tok = json.load(f)
print("token keys:", sorted(tok.keys()))
for k in ("scope", "scopes", "token_type", "expires_in"):
    if k in tok:
        print(f"  {k}: {tok[k]}")
print("access_token present:", bool(tok.get("access_token")), "len:", len(tok.get("access_token") or ""))

me = m.make_request("GET", "/users/me")
uid = me.get("user_id")
print("users/me OK user_id=", uid)

shops = m.make_request("GET", f"/users/{uid}/shops")
if isinstance(shops, dict) and shops.get("results"):
    shop = shops["results"][0]
elif isinstance(shops, dict) and shops.get("shop_id"):
    shop = shops
else:
    shop = {"shop_id": 66586766, "shop_name": "?"}
shop_id = shop.get("shop_id")
print("shop OK", shop.get("shop_name"), shop_id)

listings = m.make_request("GET", f"/shops/{shop_id}/listings/active?limit=1")
print("listings/active OK count=", listings.get("count") if isinstance(listings, dict) else "?")

try:
    receipts = m.make_request("GET", f"/shops/{shop_id}/receipts?limit=1")
    print("receipts OK", type(receipts), str(receipts)[:180])
except Exception as e:
    print("receipts FAIL:", str(e)[:300])
