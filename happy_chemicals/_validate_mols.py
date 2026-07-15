"""Validate Happy Chemicals SMILES against expected formulas and PubChem twins."""
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

PRIMARY = {
    "serotonin": "NCCc1c[nH]c2ccc(O)cc12",
    "dopamine": "NCCc1ccc(O)c(O)c1",
    "caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "oxytocin": (
        "N[C@H]1CSSC[C@H](NC(=O)[C@H](CC(N)=O)NC(=O)[C@H](CCC(N)=O)"
        "NC(=O)[C@@H](NC(=O)[C@H](Cc2ccc(O)cc2)NC1=O)[C@@H](C)CC)"
        "C(=O)N1CCC[C@H]1C(=O)N[C@@H](CC(C)C)C(=O)NCC(N)=O"
    ),
}
EXPECT = {
    "serotonin": ("C10H12N2O", 176.22),
    "dopamine": ("C8H11NO2", 153.18),
    "caffeine": ("C8H10N4O2", 194.19),
    "oxytocin": ("C43H66N12O12S2", 1007.19),
}
ALTS = {
    "serotonin": "C1=CC2=C(C=C1O)C(=CN2)CCN",
    "dopamine": "C1=CC(=C(C=C1CCN)O)O",
    "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
}

ok_all = True
print("=== PRIMARY CHECKS ===")
for name, smi in PRIMARY.items():
    m = Chem.MolFromSmiles(smi)
    if m is None:
        print(f"FAIL {name}: invalid SMILES")
        ok_all = False
        continue
    f = rdMolDescriptors.CalcMolFormula(m)
    mw = Descriptors.MolWt(m)
    exp_f, exp_mw = EXPECT[name]
    formula_ok = f == exp_f
    mw_ok = abs(mw - exp_mw) < 1.0
    rings = m.GetRingInfo().NumRings()
    print(
        f"{name:10} formula={f:16} expect={exp_f:16} "
        f"{'OK' if formula_ok else 'BAD'}  MW={mw:.2f} "
        f"({'OK' if mw_ok else 'CHECK'}) rings={rings} atoms={m.GetNumAtoms()}"
    )
    if not formula_ok:
        ok_all = False

print("\n=== INCHI vs PUBCHEM-STYLE ALTS ===")
for name, alt in ALTS.items():
    m1 = Chem.MolFromSmiles(PRIMARY[name])
    m2 = Chem.MolFromSmiles(alt)
    same = Chem.MolToInchiKey(m1) == Chem.MolToInchiKey(m2)
    print(f"{name:10} same molecule as pubchem SMILES: {same}")
    if not same:
        ok_all = False

print("\n=== STRUCTURAL SPOT-CHECKS ===")
# Serotonin: has phenolic O, 2 N, indole (rings>=2)
ms = Chem.MolFromSmiles(PRIMARY["serotonin"])
n_n = sum(1 for a in ms.GetAtoms() if a.GetAtomicNum() == 7)
n_o = sum(1 for a in ms.GetAtoms() if a.GetAtomicNum() == 8)
print(f"serotonin N count={n_n} (expect 2), O count={n_o} (expect 1), rings={ms.GetRingInfo().NumRings()} (expect 2)")
if n_n != 2 or n_o != 1 or ms.GetRingInfo().NumRings() != 2:
    ok_all = False

md = Chem.MolFromSmiles(PRIMARY["dopamine"])
n_n = sum(1 for a in md.GetAtoms() if a.GetAtomicNum() == 7)
n_o = sum(1 for a in md.GetAtoms() if a.GetAtomicNum() == 8)
print(f"dopamine  N count={n_n} (expect 1), O count={n_o} (expect 2), rings={md.GetRingInfo().NumRings()} (expect 1)")
if n_n != 1 or n_o != 2 or md.GetRingInfo().NumRings() != 1:
    ok_all = False

mc = Chem.MolFromSmiles(PRIMARY["caffeine"])
n_n = sum(1 for a in mc.GetAtoms() if a.GetAtomicNum() == 7)
n_o = sum(1 for a in mc.GetAtoms() if a.GetAtomicNum() == 8)
print(f"caffeine  N count={n_n} (expect 4), O count={n_o} (expect 2), rings={mc.GetRingInfo().NumRings()} (expect 2)")
if n_n != 4 or n_o != 2 or mc.GetRingInfo().NumRings() != 2:
    ok_all = False

mo = Chem.MolFromSmiles(PRIMARY["oxytocin"])
n_s = sum(1 for a in mo.GetAtoms() if a.GetAtomicNum() == 16)
n_n = sum(1 for a in mo.GetAtoms() if a.GetAtomicNum() == 7)
print(f"oxytocin  S count={n_s} (expect 2), N count={n_n} (expect 12)")
if n_s != 2 or n_n != 12:
    ok_all = False

print("\nRESULT:", "ALL CHECKS PASSED" if ok_all else "FAILURES FOUND")
raise SystemExit(0 if ok_all else 1)
