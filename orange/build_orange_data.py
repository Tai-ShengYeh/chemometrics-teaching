# -*- coding: utf-8 -*-
"""
build_orange_data.py — make the five-sugar NIR data Orange-ready.

Source: the five-sugar InnoSpectra CSV (Yeh 2025 J. Chem. Educ.; see python/04_sugar_pca.py).
Outputs (into ../data/):
  five_sugar.csv  — plain CSV copy (also used by the Python notebook / Colab)
  five_sugar.tab  — Orange-native, 3-row header with roles baked in:
                    sugar_group = class (discrete), ID = meta, 228 wavelengths = features.
With roles in the .tab, the Orange File widget loads the target automatically
(no manual Domain-editor step needed).
"""
import os
import shutil
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
os.makedirs(DATA, exist_ok=True)

# source CSV (user-provided). Fall back to an already-copied repo version.
CANDIDATES = [
    r"D:/Orange/five_sugar/five_sugar_0511_2023_innospectra.csv",
    os.path.join(DATA, "five_sugar.csv"),
]
src = next((p for p in CANDIDATES if os.path.exists(p)), None)
if src is None:
    raise SystemExit("five_sugar source CSV not found in: " + " ; ".join(CANDIDATES))

csv_out = os.path.join(DATA, "five_sugar.csv")
if os.path.abspath(src) != os.path.abspath(csv_out):
    shutil.copyfile(src, csv_out)
print("csv ->", csv_out)

df = pd.read_csv(csv_out)
cols = list(df.columns)               # ID, sugar_group, 901.1..., ..., 1700.7...
wl_cols = cols[2:]
assert cols[0] == "ID" and cols[1] == "sugar_group", f"unexpected header: {cols[:3]}"

# Orange native .tab: row1 names / row2 types / row3 flags(roles)
names = cols
types = ["continuous", "discrete"] + ["continuous"] * len(wl_cols)
flags = ["meta", "class"] + [""] * len(wl_cols)

tab_out = os.path.join(DATA, "five_sugar.tab")
with open(tab_out, "w", encoding="utf-8") as f:
    f.write("\t".join(names) + "\n")
    f.write("\t".join(types) + "\n")
    f.write("\t".join(flags) + "\n")
    for _, row in df.iterrows():
        f.write("\t".join(str(v) for v in row.tolist()) + "\n")
print(f"tab -> {tab_out}  ({df.shape[0]} rows, {len(wl_cols)} wavelengths)")
print("classes:", sorted(df['sugar_group'].unique()))
