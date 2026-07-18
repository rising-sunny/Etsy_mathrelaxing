from collections import Counter
from etsy_manager import EtsyManager

m = EtsyManager()
shop = m.get_shop_id()
r = m.make_request("GET", f"/shops/{shop}/listings?state=active&limit=100")
phys = []
for L in r.get("results") or []:
    lt = L.get("listing_type") or L.get("type")
    if L.get("is_digital") or lt == "download":
        continue
    if lt != "physical" and not L.get("shipping_profile_id"):
        continue
    phys.append(L)

print("physical", len(phys))
pc = Counter((L.get("processing_min"), L.get("processing_max")) for L in phys)
print("proc dist", dict(pc))
blurb = sum(1 for L in phys if "SHIPPING & PRODUCTION" in (L.get("description") or ""))
print("with blurb", blurb)

for L in phys:
    lid = L["listing_id"]
    inv = m.make_request("GET", f"/listings/{lid}/inventory")
    zero = en = tot = 0
    for p in inv.get("products") or []:
        for o in p.get("offerings") or []:
            if o.get("is_deleted"):
                continue
            if o.get("is_enabled"):
                en += 1
                q = int(o.get("quantity") or 0)
                tot += q
                if q <= 0:
                    zero += 1
    flag = "OK" if en and not zero else "PROBLEM"
    title = (L.get("title") or "")[:48]
    print(f"  {flag} en={en} zero={zero} tot={tot} list_qty={L.get('quantity')}  {title}")
