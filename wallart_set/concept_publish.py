"""
concept_publish.py — create the Etsy DRAFT for one Mathematical Concept Poster.
Copy per concept below; the description reuses the plate's own human caption.

    CONCEPT=golden python wallart_set/concept_publish.py    (run from repo root)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager
import concept_poster as cp

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
TAX = 2078
PRICE = 5.50
SLUG = {"harmonic": "HarmonicSeries", "golden": "GoldenRatio", "euler": "EulersIdentity",
        "pi": "Pi", "ulam": "UlamSpiral", "fourier": "FourierSquareWave"}

META = {
    "golden": {
        "title": "Golden Ratio Art Print | Fibonacci Spiral Math Poster | Phi Scientific Diagram | Educational STEM Wall Art | Digital Download",
        "tags": ["golden ratio", "fibonacci art", "math poster", "phi print", "science poster",
                 "math wall art", "educational poster", "geometry print", "spiral art",
                 "stem wall art", "teacher gift", "digital download", "math art print"]},
    "euler": {
        "title": "Eulers Identity Art Print | The Most Beautiful Equation | Complex Plane Unit Circle Math Poster | STEM Wall Art Download",
        "tags": ["eulers identity", "math poster", "physics poster", "complex numbers", "science poster",
                 "math wall art", "educational poster", "euler formula", "stem wall art", "nerd gift",
                 "teacher gift", "digital download", "math art print"]},
    "pi": {
        "title": "Pi Art Print | Archimedes Method Math Poster | Squeezing Pi Circle Diagram | Educational STEM Wall Art | Digital Download",
        "tags": ["pi print", "math poster", "pi day", "archimedes", "science poster",
                 "math wall art", "educational poster", "geometry print", "stem wall art",
                 "teacher gift", "circle art", "digital download", "math art print"]},
    "ulam": {
        "title": "Ulam Spiral Art Print | Prime Numbers Math Poster | Number Theory Scientific Diagram | STEM Wall Art | Digital Download",
        "tags": ["ulam spiral", "prime numbers", "math poster", "number theory", "science poster",
                 "math wall art", "educational poster", "prime art", "stem wall art", "nerd gift",
                 "teacher gift", "digital download", "math art print"]},
    "fourier": {
        "title": "Fourier Series Art Print | Square Wave Math Poster | Sound Waves Scientific Diagram | STEM Music Wall Art | Digital",
        "tags": ["fourier series", "math poster", "physics poster", "sound waves", "science poster",
                 "math wall art", "educational poster", "signal art", "stem wall art", "music theory art",
                 "teacher gift", "digital download", "math art print"]},
}


def description(key):
    intro = " ".join(cp.CONCEPTS[key]["caption"])
    return (f"{cp.CONCEPTS[key]['title'].title()} - a scientific-plate art print.\n\n{intro}\n\n"
            "Every line is computed from the mathematics - not stock art, not AI.\n\n"
            "WHAT YOU GET (instant download)\n"
            "- 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A\n- 300 DPI - print small or large\n"
            "- Delivered as one ZIP\n\n"
            "Print at home, a print shop, or an online lab. For personal use. Frame not included.\n\n"
            "(c) MathRelaxing")


def main():
    key = os.environ["CONCEPT"]
    meta = META[key]
    base = os.path.join(HERE, "out", "concept", key)
    imgs = [os.path.join(base, "listing", f"{n}.jpg")
            for n in ["01_hero", "03_framed", "02_detail", "04_sizes", "05_note"]]
    zip_ = os.path.join(base, f"{SLUG[key]}_prints.zip")
    assert len(meta["title"]) <= 140 and len(meta["tags"]) <= 13 and all(len(t) <= 20 for t in meta["tags"]), \
        (len(meta["title"]), max(len(t) for t in meta["tags"]))
    for f in imgs + [zip_]:
        assert os.path.exists(f), f
    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(meta["title"], description(key), PRICE, TAX, is_digital=True, tags=meta["tags"])
    for r, im in enumerate(imgs, 1):
        m.upload_listing_image(lid, im, rank=r)
    m.upload_listing_file(lid, zip_)
    print(f"DRAFT [{key}]: {lid}  (${PRICE})  title={len(meta['title'])}")


if __name__ == "__main__":
    main()
