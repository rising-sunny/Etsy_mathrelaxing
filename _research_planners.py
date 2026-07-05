"""Competencia en Etsy para la dirección 'planners/notebooks GoodNotes'."""
import etsy_manager, time

KEYWORDS = [
    # Broad (para ver saturación)
    "digital planner",
    "goodnotes planner",
    "digital notebook",
    "goodnotes notebook",
    "hyperlinked digital planner",
    # Grids especiales / STEM (ángulo diferenciador MathRelaxing)
    "dot grid digital notebook",
    "hexagonal notebook digital",
    "hexagonal paper goodnotes",
    "isometric notebook digital",
    "isometric grid notebook",
    "graph paper digital notebook",
    "engineering notebook digital",
    "chemistry notebook digital",
    "math digital notebook",
    "math digital planner",
    "geometric digital planner",
    "cornell notes digital",
    "science digital planner",
    "student notebook goodnotes",
    "grid paper goodnotes",
    "dotted notebook goodnotes",
    "lab notebook digital",
    "physics notebook digital",
    "bullet journal digital goodnotes",
    "minimalist digital notebook",
]

def count(m, kw):
    try:
        r = m.make_request('GET', f'/listings/active?keywords={kw.replace(" ","+")}&limit=1')
        return r.get('count', 0)
    except Exception as e:
        return f"err:{e}"

def main():
    m = etsy_manager.EtsyManager()
    rows = []
    print(f"\n{'KEYWORD':<36}{'LISTINGS':>10}")
    print("-"*48)
    for kw in KEYWORDS:
        c = count(m, kw)
        rows.append((kw, c))
        mk = "  <-- BAJO" if isinstance(c,int) and c < 1000 else ("  <-- medio" if isinstance(c,int) and c<5000 else "")
        print(f"{kw:<36}{str(c):>10}{mk}")
        time.sleep(0.25)
    print("\n--- ORDENADO por menos competencia ---")
    for kw,c in sorted([r for r in rows if isinstance(r[1],int)], key=lambda x:x[1]):
        print(f"  {c:>7}  {kw}")

if __name__ == "__main__":
    main()
