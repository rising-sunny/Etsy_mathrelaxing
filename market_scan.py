"""
market_scan.py — competition/price/demand scan over candidate niches (Etsy API).
Feeds the shortlist in MARKET_STRATEGY.md. The API gives competition (# active
listings), median price and top-listing favourites; it CANNOT give search
volume or sales — look those up in eRank for the starred candidates.

  python market_scan.py            # scans the default KEYWORDS below
  python market_scan.py "kw one" "kw two" ...   # scan custom keywords
"""
import sys
import time
import statistics
import urllib.parse

import etsy_manager

# candidate niches tied to what we sell / could make next (edit freely)
KEYWORDS = [
    "chladni art", "cymatics wall art", "strange attractor print",
    "math magnet", "equation poster", "fractal art print",
    "sacred geometry svg", "math svg", "procreate color palette",
    "abstract math poster", "physics poster", "sacred geometry print",
    "math art print", "science wall art", "math teacher gift",
    "dark academia poster", "geometric wall art",
]


def scan(m, kw):
    q = urllib.parse.quote_plus(kw)
    r = m.make_request('GET', f'/listings/active?keywords={q}&limit=100&sort_on=score')
    res = r.get('results', [])
    prices = [l['price']['amount'] / l['price']['divisor'] for l in res if l.get('price')]
    favs = [l.get('num_favorers', 0) for l in res]
    med = statistics.median(prices) if prices else 0.0
    return r.get('count', 0), med, (max(favs) if favs else 0)


def main(keywords):
    m = etsy_manager.EtsyManager()
    print(f"{'KEYWORD':<26}{'COMPET':>9}{'MED$':>8}{'MAXfav':>8}")
    print("-" * 51)
    rows = []
    for kw in keywords:
        try:
            c, med, mf = scan(m, kw)
            rows.append((kw, c, med, mf))
            print(f"{kw:<26}{c:>9}{med:>8.2f}{mf:>8}")
        except Exception as e:
            print(f"{kw:<26} ERR {str(e)[:24]}")
        time.sleep(0.35)              # respect rate limits
    print("\n(sube estos a MARKET_STRATEGY.md §5; el volumen de busqueda va en eRank)")
    return rows


if __name__ == "__main__":
    kws = sys.argv[1:] or KEYWORDS
    main(kws)
