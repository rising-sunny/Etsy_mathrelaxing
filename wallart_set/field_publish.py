"""
field_publish.py — Etsy DRAFT for a premium physics field plate, or the set.
Titles avoid ^, = and + and use <=1 '&'.

    FIELD=quantum python wallart_set/field_publish.py     (run from repo root)
    FIELD=set     python wallart_set/field_publish.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set"))
import etsy_manager
import field_poster as fp
import field_build as fb

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wallart_set")
TAX = 2078
PRICE_ONE = 6.90
PRICE_SET = 18.00

META = {
    "quantum": {
        "title": "Quantum Mechanics Poster | Physics Equations Wall Art | Hydrogen Orbitals Schrodinger | Classroom Decor | Digital Download",
        "tags": ["quantum physics", "physics poster", "science poster", "physics wall art", "hydrogen orbital",
                 "schrodinger", "classroom decor", "stem wall art", "educational poster", "quantum art",
                 "physics art print", "science teacher gift", "digital download"]},
    "blackhole": {
        "title": "Black Hole Physics Poster | Relativity Equations Wall Art | Event Horizon Hawking | Astronomy Decor | Digital Download",
        "tags": ["black hole", "physics poster", "science poster", "astrophysics", "astronomy art",
                 "general relativity", "classroom decor", "stem wall art", "space poster", "physics wall art",
                 "physics art print", "science teacher gift", "digital download"]},
    "relativity": {
        "title": "Special Relativity Poster | Einstein Physics Equations Wall Art | Minkowski Spacetime | Classroom Decor | Digital Download",
        "tags": ["special relativity", "einstein art", "physics poster", "science poster", "spacetime",
                 "physics wall art", "classroom decor", "stem wall art", "educational poster", "relativity art",
                 "physics art print", "science teacher gift", "digital download"]},
    "electromagnetism": {
        "title": "Electromagnetism Poster | Maxwell Equations Wall Art | Electric Field Lines Physics | Classroom Decor | Digital Download",
        "tags": ["electromagnetism", "maxwell equations", "physics poster", "science poster", "physics wall art",
                 "field lines", "classroom decor", "stem wall art", "educational poster", "electric field",
                 "physics art print", "science teacher gift", "digital download"]},
    "thermodynamics": {
        "title": "Thermodynamics Poster | Physics Equations Wall Art | Entropy Maxwell Boltzmann | Classroom Decor | Digital Download",
        "tags": ["thermodynamics", "physics poster", "science poster", "entropy art", "physics wall art",
                 "boltzmann", "classroom decor", "stem wall art", "educational poster", "chemistry poster",
                 "physics art print", "science teacher gift", "digital download"]},
    "mechanics": {
        "title": "Classical Mechanics Poster | Physics Equations Wall Art | Newton Lagrange Phase Space | Classroom Decor | Digital Download",
        "tags": ["classical mechanics", "physics poster", "science poster", "newton physics", "physics wall art",
                 "phase space", "classroom decor", "stem wall art", "educational poster", "engineering art",
                 "physics art print", "science teacher gift", "digital download"]},
    "set": {
        "title": "Physics Poster Set of 6 | Field Equations Wall Art | Quantum Relativity Black Holes | Science Gallery Set | Digital Download",
        "tags": ["physics poster", "science poster", "poster set", "gallery wall set", "physics wall art",
                 "classroom decor", "stem wall art", "educational poster", "science teacher gift", "quantum art",
                 "astrophysics", "physics art print", "digital download"]},
}


def description(f):
    if f == "set":
        return ("Physics Field Collection — six premium scientific-plate posters as one coordinated gallery set: "
                "quantum mechanics, black holes, special relativity, electromagnetism, thermodynamics and "
                "classical mechanics.\n\n"
                "Each plate gathers its field's canonical equations in classic Computer-Modern math type on a "
                "deep observatory-black ground, with a real, computed hero — hydrogen orbitals, an accretion "
                "disk and photon ring, a Minkowski light cone, dipole field lines, the Maxwell-Boltzmann "
                "distribution and a pendulum phase portrait.\n\n"
                "Every graphic is computed from the physics itself — not stock art, not AI.\n\n"
                "WHAT YOU GET (instant download)\n"
                "- 6 posters, each in 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A\n"
                "- 300 DPI - print small or large\n- Delivered as one ZIP (folders per plate)\n\n"
                "Print at home, a print shop, or an online lab. For personal use. Frames not included.\n\n"
                "(c) MathRelaxing")
    c = fp.FIELDS[f]
    eqs = ", ".join(lab for _, lab in c["eqs"][:6])
    return (f"{fb._title(f)} — a premium physics field plate.\n\n"
            f"One poster gathering the canonical equations of {fb._title(f).lower()} — {eqs} and more — "
            "in classic Computer-Modern math type on a deep observatory-black ground. "
            f"{c['footnote']}\n\n"
            "Every graphic is computed from the physics itself — the equations, solved and plotted. "
            "Not stock art, not AI.\n\n"
            "WHAT YOU GET (instant download)\n"
            "- 5 aspect ratios: 2:3, 3:4, 4:5, 5:7 and ISO/A\n- 300 DPI - print small or large\n"
            "- Delivered as one ZIP\n\n"
            "Print at home, a print shop, or an online lab. For personal use. Frame not included.\n\n"
            "(c) MathRelaxing")


def main():
    f = os.environ["FIELD"]
    meta = META[f]
    title, tags = meta["title"], meta["tags"]
    assert len(title) <= 140 and title.count("&") <= 1 and not any(c in title for c in "^=+"), (f, len(title))
    assert len(tags) <= 13 and all(len(t) <= 20 for t in tags), (f, max(len(t) for t in tags))
    if f == "set":
        base = os.path.join(HERE, "out", "field", "set")
        imgs = [os.path.join(base, "listing", f"{n}.jpg")
                for n in ["01_gallery", "02_framed", "03_included", "04_sizes", "05_note"]]
        zip_ = os.path.join(base, "PhysicsFieldCollection_prints.zip")
        price = PRICE_SET
    else:
        base = os.path.join(HERE, "out", "field", f)
        imgs = [os.path.join(base, "listing", f"{n}.jpg")
                for n in ["01_hero", "02_framed", "03_detail", "04_sizes", "05_note"]]
        zip_ = os.path.join(base, f"{fb.SLUG[f]}_prints.zip")
        price = PRICE_ONE
    for p in imgs + [zip_]:
        assert os.path.exists(p), p

    def retry(fn, tries=5):
        for k in range(tries):
            try:
                return fn()
            except Exception as e:
                print("  retry", k, str(e)[:70]); time.sleep(1.5 * (k + 1))
        raise RuntimeError("upload failed after retries")

    m = etsy_manager.EtsyManager()
    lid = m.create_draft_listing(title, description(f), price, TAX, is_digital=True, tags=tags)
    for r, im in enumerate(imgs, 1):
        retry(lambda im=im, r=r: m.upload_listing_image(lid, im, rank=r))
        time.sleep(0.5)
    retry(lambda: m.upload_listing_file(lid, zip_))
    print(f"DRAFT [{f}]: {lid}  (${price})  title={len(title)}")


if __name__ == "__main__":
    main()
