#!/usr/bin/env python3
"""
Split mmCIF protein-ligand complexes into separate PDBs by chain IDs.

Validated for your CHE882 set:
  - Chain A = protein
  - Chain B = ligand (single residue LIG1)
  - One model per file

This version avoids gemmi Model.name (not present in some gemmi builds).
"""

import sys
import glob
from pathlib import Path
import gemmi

PROT_CHAIN = "A"
LIG_CHAIN  = "B"

def keep_only_chain(st: gemmi.Structure, chain_id: str) -> gemmi.Structure:
    out = gemmi.Structure()
    out.name = st.name
    out.cell = st.cell
    out.spacegroup_hm = st.spacegroup_hm

    for model in st:
        m2 = gemmi.Model("1")
        for ch in model:
            if ch.name == chain_id:
                m2.add_chain(ch)
        if len(m2) > 0:
            out.add_model(m2)

    return out

def write_pdb(st: gemmi.Structure, out_pdb: Path):
    out_pdb.parent.mkdir(parents=True, exist_ok=True)
    st.write_pdb(str(out_pdb))

def main(in_glob: str, out_dir: str):
    files = sorted(glob.glob(in_glob))
    if not files:
        print(f"ERROR: No files matched: {in_glob}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(out_dir)
    prot_dir = out_dir / "protein"
    lig_dir  = out_dir / "ligand"
    prot_dir.mkdir(parents=True, exist_ok=True)
    lig_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for fp in files:
        fp = Path(fp)
        base = fp.stem

        st = gemmi.read_structure(str(fp))

        prot = keep_only_chain(st, PROT_CHAIN)
        lig  = keep_only_chain(st, LIG_CHAIN)

        prot_out = prot_dir / f"{base}_protein.pdb"
        lig_out  = lig_dir  / f"{base}_ligand.pdb"

        if len(prot) == 0:
            print(f"[WARN] {fp.name}: missing protein chain {PROT_CHAIN}")
            continue
        if len(lig) == 0:
            print(f"[WARN] {fp.name}: missing ligand chain {LIG_CHAIN}")
            continue

        write_pdb(prot, prot_out)
        write_pdb(lig, lig_out)
        ok += 1

        print(f"[OK] {fp.name} → {prot_out.name}, {lig_out.name}")

    print(f"\nFinished: {ok}/{len(files)} complexes successfully split.")
    print(f"Protein PDBs → {prot_dir}")
    print(f"Ligand  PDBs → {lig_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "  split_cifs_by_chain.py 'inputs/CHE882/*.cif' inputs/CHE882_clean",
            file=sys.stderr
        )
        sys.exit(2)

    main(sys.argv[1], sys.argv[2])
    