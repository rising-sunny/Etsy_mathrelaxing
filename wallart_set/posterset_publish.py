"""
posterset_publish.py — Etsy DRAFT for a gallery poster set (6 prints).
Title avoids ^, = and + and uses <=1 '&'.

    SET=physics python wallart_set/posterset_publish.py     (run from repo root)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
SET = os.environ.get("SET", "physics")
TAX = 2078
PRICE = 13.99

META = {
    "physics": {
        "slug": "PhysicsPosterSet",
        "title": ("Physics Poster Set of 6 | Science Classroom Wall Art | Relativity Quantum Black Hole "
                  "Prints | STEM Gallery Set | Digital Download"),
        "tags": ["physics poster", "science poster", "physics wall art", "classroom decor",
                 "stem wall art", "poster set", "gallery wall set", "science teacher gift",
                 "physics print", "educational poster", "quantum art", "space poster",
                 "digital download"],
        "intro": ("Six scientific-plate physics prints as one coordinated gallery set: special "
                  "relativity, a black hole, the quantum harmonic oscillator, electromagnetism, "
                  "Planck's law and Kepler's orbits."),
    },
    "math": {
        "slug": "MathPosterSet",
        "title": ("Math Poster Set of 6 | Mathematics Classroom Wall Art | Golden Ratio Euler Pi Prints "
                  "| STEM Gallery Set | Digital Download"),
        "tags": ["math poster", "mathematics art", "math wall art", "classroom decor",
                 "stem wall art", "poster set", "gallery wall set", "math teacher gift",
                 "geometry print", "educational poster", "golden ratio", "science poster",
                 "digital download"],
        "intro": ("Six scientific-plate mathematics prints as one coordinated gallery set: the golden "
                  "ratio, Euler's identity, pi by Archimedes, a Fourier square wave, the Ulam spiral "
                  "and the harmonic series."),
    },
}[SET]


def description():
    return (f"{META['intro']}\n\n"
            "Every plate is computed from the mathematics itself - the equations, solved and plotted. "
            "Not stock art, not AI. A clean, technical look that hangs together as a gallery wall for a "
            "classroom, office or study.\n\n"
            "WHAT YOU GET (instant download)\n"
            "- 6 prints, each in 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A\n"
            "- 300 DPI - print small or large\n"
            "- Delivered as one ZIP (folders per design)\n\n"
            "Print at home, a print shop, or an online lab. For personal use. Frames not included.\n\n"
            "(c) MathRelaxing")


def main():
    base = os.path.join(HERE, "out", "posterset", SET)
    imgs = [os.path.join(base, "listing", f"{n}.jpg")
            for n in ["01_gallery", "02_framed", "03_closeups", "04_included", "05_note"]]
    zip_ = os.path.join(base, f"{META['slug']}_prints.zip")
    title, tags = META["title"], META["tags"]
    assert len(title) <= 140 and title.count("&") <= 1 and not any(c in title for c in "^=+"), len(title)
    assert len(tags) <= 13 and all(len(t) <= 20 for t in tags), max(len(t) for t in tags)
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
    lid = m.create_draft_listing(title, description(), PRICE, TAX, is_digital=True, tags=tags)
    for r, im in enumerate(imgs, 1):
        retry(lambda im=im, r=r: m.upload_listing_image(lid, im, rank=r))
        time.sleep(0.6)
    retry(lambda: m.upload_listing_file(lid, zip_))
    print(f"DRAFT [{SET} set]: {lid}  (${PRICE})  title={len(title)}  tags={len(tags)}")


if __name__ == "__main__":
    main()
