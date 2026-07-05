"""Inspecciona taxonomy_id de listings existentes + busca nodos 'coloring'."""
import etsy_manager

m = etsy_manager.EtsyManager()
shop_id = m.get_shop_id()
print(f"shop_id = {shop_id}\n")

# 1) Listings existentes (cualquier estado) y su taxonomy_id
print("=== LISTINGS EXISTENTES ===")
for state in ("active", "draft"):
    try:
        res = m.make_request('GET', f'/shops/{shop_id}/listings?state={state}&limit=25')
        for L in res.get("results", []):
            print(f"  [{state:6}] tax={L.get('taxonomy_id')}  type={L.get('listing_type','?'):8} {L.get('title','')[:55]}")
    except Exception as e:
        print(f"  ({state}) error: {e}")

# 2) Buscar nodos de taxonomía con 'coloring'
print("\n=== TAXONOMIA con 'coloring' ===")
nodes = m.make_request('GET', '/application/seller-taxonomy/nodes')
def walk(n, depth=0):
    nm = n.get("name","")
    if "color" in nm.lower():
        path = " > ".join(str(x) for x in n.get("full_path_taxonomy_ids", []))
        print(f"  id={n['id']:>6}  {nm}   (path ids: {path})")
    for c in n.get("children", []):
        walk(c, depth+1)
for n in nodes.get("results", []):
    walk(n)
