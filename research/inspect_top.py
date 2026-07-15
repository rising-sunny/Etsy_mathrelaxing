import etsy_manager
import urllib.parse

m = etsy_manager.EtsyManager()
for kw in [
    "lab notebook printable",
    "unit circle math poster",
    "math unit circle printable",
    "math formula cheat sheet",
    "classroom math posters set",
    "study flashcards goodnotes",
]:
    q = urllib.parse.quote_plus(kw)
    data = m.make_request("GET", f"/listings/active?keywords={q}&limit=10&offset=0")
    print("===", kw, "count", data.get("count"))
    for r in data.get("results") or []:
        price = r.get("price") or {}
        amt = (price.get("amount") or 0) / (price.get("divisor") or 100)
        print(
            f"  fav={r.get('num_favorers'):4d} dig={r.get('is_digital')} "
            f"${amt:6.2f}  {(r.get('title') or '')[:72]}"
        )
