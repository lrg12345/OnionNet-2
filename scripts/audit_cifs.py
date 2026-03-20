#!/usr/bin/env python3
import os
import sys
import glob
import csv
from collections import Counter

try:
    import gemmi
except Exception as e:
    print("ERROR: gemmi not importable. Install with: pip install gemmi", file=sys.stderr)
    raise

# Minimal residue name sets (tunable)
AA3 = {
    "ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS",
    "MET","PHE","PRO","SER","THR","TRP","TYR","VAL","SEC","PYL"
}
NUC = {"A","C","G","U","DA","DC","DG","DT","DU"}
WATER = {"HOH","WAT","H2O","DOD"}
IONS = {"NA","K","CL","CA","MG","ZN","MN","FE","CU","CO","NI","CD","HG","IOD","BR"}

def classify_res(res: "gemmi.Residue") -> str:
    """
    Classify residues by name only (robust across messy mmCIFs).
    """
    name = res.name.strip()
    if name in AA3:
        return "protein"
    if name in NUC:
        return "nucleic"
    if name in WATER:
        return "water"
    if name in IONS:
        return "ion"
    return "hetero"  # ligands + cofactors + additives, etc.

def main(in_glob: str, out_csv: str):
    files = sorted(glob.glob(in_glob))
    if not files:
        print(f"No files matched: {in_glob}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for fp in files:
        base = os.path.basename(fp)

        # Read structure
        try:
            st = gemmi.read_structure(fp)
            st.setup_entities()
        except Exception as e:
            rows.append({
                "file": base,
                "ok": 0,
                "error": str(e),
                "models": "",
                "chains": "",
                "protein_res": "",
                "nucleic_res": "",
                "hetero_res": "",
                "water_res": "",
                "ion_res": "",
                "unique_hetero": "",
                "notes": "READ_FAIL",
            })
            continue

        models = len(st)
        m0 = st[0]  # usually only one model in PDB/mmCIF inputs

        chain_ids = []
        counts = Counter()
        hetero_names = Counter()

        for ch in m0:
            chain_ids.append(ch.name)
            for res in ch:
                cls = classify_res(res)
                counts[cls] += 1
                if cls == "hetero":
                    hetero_names[res.name.strip()] += 1

        notes = []
        if models > 1:
            notes.append("MULTI_MODEL")
        if counts["protein"] == 0 and counts["nucleic"] == 0:
            notes.append("NO_POLYMER?")
        if sum(hetero_names.values()) == 0:
            notes.append("NO_HETERO?")
        if len(hetero_names) > 3:
            notes.append("MANY_HETERO")

        rows.append({
            "file": base,
            "ok": 1,
            "error": "",
            "models": models,
            "chains": ",".join(chain_ids),
            "protein_res": counts["protein"],
            "nucleic_res": counts["nucleic"],
            "hetero_res": counts["hetero"],
            "water_res": counts["water"],
            "ion_res": counts["ion"],
            "unique_hetero": ",".join(sorted(hetero_names.keys())),
            "notes": ";".join(notes),
        })

    # Write CSV
    out_dir = os.path.dirname(out_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_csv} ({len(rows)} rows)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: audit_cifs.py 'inputs/CHE882/*.cif' outputs/CHE882_audit.csv", file=sys.stderr)
        sys.exit(2)

    in_glob = sys.argv[1]
    out_csv = sys.argv[2]
    main(in_glob, out_csv)
