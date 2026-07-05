"""
etsy_research.py — Investigacion de nichos en Etsy
Busca keywords y cuenta listings activos para medir nivel de competencia.
Menos resultados = nicho menos saturado.
"""
import etsy_manager, time

KEYWORDS = [
    # Referencia: lo que ya existe en MathRelaxing
    "fractal coloring book",
    "sacred geometry coloring book",
    "mathematical coloring book",
    # Nichos a explorar
    "diatom coloring book",
    "microscopy coloring book",
    "flow field coloring book",
    "vector field coloring",
    "knot theory coloring",
    "circuit board coloring",
    "topology coloring book",
    "crystallography coloring",
    "origami crease pattern coloring",
    "fluid dynamics coloring",
    "mycology coloring book",
    "fungus mushroom science coloring",
    "architecture blueprint coloring",
    "islamic geometry coloring",
    "celtic knot coloring book",
    "voronoi coloring book",
    "neural network art coloring",
    "bioluminescence coloring",
    "radiolaria coloring",
    "scientific illustration coloring",
]

def search_count(manager, keyword, limit=100):
    try:
        result = manager.make_request(
            'GET',
            f'/listings/active?keywords={keyword.replace(" ", "+")}&limit={limit}&includes[]=Images'
        )
        return result.get('count', 0)
    except Exception as e:
        return f"error: {e}"

def main():
    manager = etsy_manager.EtsyManager()
    print(f"\n{'KEYWORD':<40} {'LISTINGS':>10}")
    print("-" * 52)
    results = []
    for kw in KEYWORDS:
        count = search_count(manager, kw)
        results.append((kw, count))
        marker = " <-- BAJO" if isinstance(count, int) and count < 200 else ""
        print(f"{kw:<40} {str(count):>10}{marker}")
        time.sleep(0.3)  # respetar rate limit

    print("\n--- Nichos con menos de 500 listings (menor competencia) ---")
    low = [(kw, c) for kw, c in results if isinstance(c, int) and c < 500]
    for kw, c in sorted(low, key=lambda x: x[1]):
        print(f"  {c:>6}  {kw}")

if __name__ == "__main__":
    main()
