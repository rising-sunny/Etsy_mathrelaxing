import time
import urllib.parse
import etsy_manager

m = etsy_manager.EtsyManager()
for kw in [
    "computer science poster",
    "computer science wall art",
    "algorithm poster",
    "binary code wall art",
    "coding poster classroom",
    "data structure poster",
    "stem classroom poster set",
    "math formula cheat sheet",
]:
    q = urllib.parse.quote_plus(kw)
    d = m.make_request("GET", f"/listings/active?keywords={q}&limit=8&offset=0")
    print("===", kw, "count", d.get("count"))
    for r in d.get("results") or []:
        p = r.get("price") or {}
        amt = (p.get("amount") or 0) / (p.get("divisor") or 100)
        title = (r.get("title") or "")[:68]
        print(
            f"  fav={r.get('num_favorers'):4d} dig={r.get('is_digital')} "
            f"${amt:6.2f} {title}"
        )
    time.sleep(0.25)
