"""
physics_publish.py — create the Etsy DRAFT for one Famous Physics plate.
Mirrors concept_publish.py; the description reuses the plate's human caption.
Titles avoid ^, = and + (which break the Etsy API) and use at most one '&'.

    CONCEPT=relativity python wallart_set/physics_publish.py    (run from repo root)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager
import physics_poster as cp

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
TAX = 2078
PRICE = 5.50
SLUG = {"relativity": "Relativity", "blackhole": "BlackHole", "quantum": "QuantumOscillator",
        "maxwell": "Electromagnetism", "planck": "PlanckLaw", "gravity": "Gravitation"}

META = {
    "relativity": {
        "title": "Special Relativity Art Print | Einstein Physics Poster | Lorentz Factor Diagram | Science STEM Wall Art | Digital Download",
        "tags": ["relativity", "physics poster", "einstein art", "science poster", "space time",
                 "math poster", "educational poster", "lorentz factor", "stem wall art", "nerd gift",
                 "teacher gift", "digital download", "physics art print"]},
    "blackhole": {
        "title": "Black Hole Art Print | Schwarzschild Physics Poster | Event Horizon Diagram | Astronomy STEM Wall Art | Digital Download",
        "tags": ["black hole", "physics poster", "astronomy art", "science poster", "space poster",
                 "event horizon", "schwarzschild", "stem wall art", "nerd gift", "astrophysics",
                 "teacher gift", "digital download", "physics art print"]},
    "quantum": {
        "title": "Quantum Physics Art Print | Schrodinger Equation Poster | Harmonic Oscillator Diagram | STEM Wall Art | Digital Download",
        "tags": ["quantum physics", "physics poster", "schrodinger", "science poster", "quantum art",
                 "wave function", "math poster", "educational poster", "stem wall art", "nerd gift",
                 "teacher gift", "digital download", "physics art print"]},
    "maxwell": {
        "title": "Electromagnetism Art Print | Maxwell Equations Physics Poster | Light Wave Diagram | STEM Wall Art | Digital Download",
        "tags": ["electromagnetism", "physics poster", "maxwell equations", "science poster", "light wave",
                 "physics art", "optics poster", "stem wall art", "nerd gift", "teacher gift",
                 "classroom decor", "digital download", "physics art print"]},
}


def description(key):
    intro = " ".join(cp.CONCEPTS[key]["caption"])
    return (f"{cp.CONCEPTS[key]['title'].title()} - a scientific-plate art print.\n\n{intro}\n\n"
            "Every line is computed from the physics - not stock art, not AI.\n\n"
            "WHAT YOU GET (instant download)\n"
            "- 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A\n- 300 DPI - print small or large\n"
            "- Delivered as one ZIP\n\n"
            "Print at home, a print shop, or an online lab. For personal use. Frame not included.\n\n"
            "(c) MathRelaxing")


def main():
    key = os.environ["CONCEPT"]
    meta = META[key]
    base = os.path.join(HERE, "out", "physics", key)
    imgs = [os.path.join(base, "listing", f"{n}.jpg")
            for n in ["01_hero", "03_framed", "02_detail", "04_sizes", "05_note"]]
    zip_ = os.path.join(base, f"{SLUG[key]}_prints.zip")
    assert len(meta["title"]) <= 140 and len(meta["tags"]) <= 13 and all(len(t) <= 20 for t in meta["tags"]), \
        (len(meta["title"]), max(len(t) for t in meta["tags"]))
    for f in imgs + [zip_]:
        assert os.path.exists(f), f
    def retry(fn, tries=5):
        for k in range(tries):
            try:
                return fn()
            except Exception as e:
                print("  retry", k, str(e)[:70]); time.sleep(1.5 * (k + 1))
        raise RuntimeError("upload failed after retries")

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(meta["title"], description(key), PRICE, TAX, is_digital=True, tags=meta["tags"])
    for r, im in enumerate(imgs, 1):
        retry(lambda im=im, r=r: m.upload_listing_image(lid, im, rank=r))
        time.sleep(0.6)
    retry(lambda: m.upload_listing_file(lid, zip_))
    print(f"DRAFT [{key}]: {lid}  (${PRICE})  title={len(meta['title'])}")


if __name__ == "__main__":
    main()
