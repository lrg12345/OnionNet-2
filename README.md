# OnionNet-2

OnionNet-2 is constructed based on convolutional neural network (CNN) to predict protein–ligand binding affinity. One of the greatest advantages of OnionNet-2 is that it achieves high accuracy at relatively low computational cost. When benchmarked on CASF-2016 and CASF-2013, OnionNet-2 demonstrates strong scoring power.

<img src="models/RAbinding.png">

---

## Contact
Zechen Wang, Shandong University  
zechenwang@mail.sdu.edu.cn

---

## Citation
Wang Z, Zheng L, Liu Y, et al.  
**OnionNet-2: A Convolutional Neural Network Model for Predicting Protein-Ligand Binding Affinity based on Residue-Atom Contacting Shells.**  
Front Chem 2021, 9, 753002.  
https://www.frontiersin.org/articles/10.3389/fchem.2021.753002/full

---

## Installation

### 1. Clone the Original Repository

```bash
git clone https://github.com/zchwang/OnionNet-2.git
```

### 2. Download the Pretrained Model

Download the model weights from Zenodo:

https://zenodo.org/records/10728089

Place the downloaded model file inside the `models/` directory.

> ⚠️ This repository does not redistribute trained model weights. You must obtain them from the official OnionNet-2 source.

### 3. Create Conda Environment

Install required dependencies:

```bash
python >= 3.8
tensorflow==2.3 or tensorflow-gpu==2.3
pandas==1.3.4
scikit-learn==0.22.1
joblib==1.0.1
numpy==1.18.5
scipy==1.4.1
```

---

# Usage

---

## 0. Preprocessing Requirements (IMPORTANT)

Before running OnionNet-2, your protein–ligand complexes must be properly prepared.

### A. Clean Your PDB Files

Before splitting, clean each structure:

- Remove crystallographic waters (`HOH`)
- Remove extra ligands or cofactors (unless intentionally modeled)
- Remove alternate conformations
- Ensure consistent chain naming
- Ensure proper residue numbering

Improperly cleaned files may cause featurization failures.

---

### B. Split Complex into Separate Protein and Ligand Files

OnionNet-2 requires **two separate PDB files**:

- One file containing only the protein
- One file containing only the ligand

Coordinates must remain identical to the original complex.

If ligands are provided in `.sdf` or `.mol2` format, convert them to `.pdb` using Open Babel:

```bash
conda install -c conda-forge openbabel
```

Example conversion:

```bash
obabel ligand.sdf -O ligand.pdb
```

---

### C. Organize Directory Structure

Each protein–ligand pair must live in its own subdirectory under `inputs/`.

Example structure:

```
inputs/
    Complex_001/
        protein.pdb
        ligand.pdb
    Complex_002/
        protein.pdb
        ligand.pdb
```

For retraining, your `inputs.dat` file must reference these separated files.

---

## 1. Predicting Affinity

After preparing cleaned and separated protein and ligand PDB files, use the `predict.py` script in the `scoring` directory:

```bash
python predict.py \
    -rec_fpath $rec_fpath \
    -lig_fpath $lig_fpath \
    -shape 84,124,1 \
    -scaler $scaler_fpath \
    -model $model_fpath \
    -shells 62 \
    -out_fpath $out_fpath
```

Where:

- `rec_fpath` → path to protein PDB file  
- `lig_fpath` → path to ligand PDB file  
- `model_fpath` → path to model file  
- `scaler_fpath` → path to scaler file  
- `out_fpath` → output file for predicted affinity  

The predicted binding affinity is written to `out_fpath`.

Alternatively, run the provided shell script:

```bash
bash run_predict.sh
```

---

## 2. Retraining OnionNet-2

In the `retrain` directory, use `generate_features.py` to prepare training and validation data:

```bash
python generate_features.py \
    -inp inputs.dat \
    -out samples_features.pkl \
    -shells 62
```

The `inputs.dat` file must contain one complex per line:

```
1c5z    ../samples/1c5z/1c5z_protein.pdb    ../samples/1c5z/1c5z_ligand.pdb
1bzc    ../samples/1bzc/1bzc_protein.pdb    ../samples/1bzc/1bzc_ligand.pdb
```

Each entry must reference properly cleaned and separated files.

You can test feature generation with:

```bash
bash run_generate-features.sh
```

After generating features, train the model using:

```bash
python train.py
```

Refer to `run_training.sh` for training parameters.

---

## Notes

- Ensure model and scaler files match.
- Input PDB files must be cleaned and separated before featurization.
- Proper directory organization is required for batch processing.
- OnionNet-2 outputs predicted binding affinity values (e.g., pKd).

---

## Summary Workflow

1. Clone original OnionNet-2 repository  
2. Download model weights  
3. Clean PDB structures  
4. Split protein and ligand into separate PDB files  
5. Organize inputs directory structure  
6. Run prediction or retrain model  

---
