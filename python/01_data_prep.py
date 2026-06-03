# -*- coding: utf-8 -*-
"""
01_data_prep.py
  - load Tecator NIR data
  - write clean CSVs (for Python + Orange Data Mining)
  - plot raw spectra and SNV-corrected spectra (figures 1-2)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nir_utils import load_tecator, snv, house_style, WAVELENGTHS, PALETTE, DATA, FIG

cmap = house_style()
wl, X, y = load_tecator()
print(f"Loaded Tecator: X={X.shape}  targets={list(y.columns)}")
print(y.describe().round(2).to_string())

# ---------- clean CSVs ----------
# wavelength-named columns so Orange shows real nm on axes
cols = [f"{w:.1f}" for w in wl]
full = pd.DataFrame(X, columns=cols)
full.insert(0, "sample", np.arange(1, len(X) + 1))
full["moisture"] = y["moisture"].values
full["fat"]      = y["fat"].values
full["protein"]  = y["protein"].values
full.to_csv(os.path.join(DATA, "tecator.csv"), index=False)
print(f"wrote data/tecator.csv  ({full.shape[0]} rows x {full.shape[1]} cols)")

# Orange-native .tab with explicit roles (3-row header: name / type / role)
tab_path = os.path.join(DATA, "tecator_orange.tab")
with open(tab_path, "w", encoding="utf-8") as f:
    names = ["sample"] + cols + ["moisture", "fat", "protein"]
    types = ["discrete"] + ["continuous"] * len(cols) + ["continuous"] * 3
    roles = ["meta"] + [""] * len(cols) + ["class", "", ""]   # fat = target class
    # NOTE: Orange allows one class column; moisture/protein kept as meta-ish extra targets
    roles = ["meta"] + [""] * len(cols) + ["meta", "class", "meta"]
    f.write("\t".join(names) + "\n")
    f.write("\t".join(types) + "\n")
    f.write("\t".join(roles) + "\n")
    for i in range(len(X)):
        row = [str(i + 1)] + [f"{v:.5f}" for v in X[i]] + \
              [f"{y['moisture'][i]:.2f}", f"{y['fat'][i]:.2f}", f"{y['protein'][i]:.2f}"]
        f.write("\t".join(row) + "\n")
print(f"wrote data/tecator_orange.tab (fat = target)")

# ---------- figure 1: raw spectra ----------
fat = y["fat"].values
norm = plt.Normalize(fat.min(), fat.max())
fig, ax = plt.subplots(figsize=(10, 6.0))
for i in range(len(X)):
    ax.plot(wl, X[i], color=cmap(norm(fat[i])), lw=0.7, alpha=0.6)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Absorbance  $-\\log_{10}T$")
ax.set_title("Tecator NIR spectra — 240 meat samples")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
cb = fig.colorbar(sm, ax=ax); cb.set_label("Fat (%)")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig01_raw_spectra.png")); plt.close(fig)
print("saved fig01_raw_spectra.png")

# ---------- figure 2: SNV spectra ----------
Xsnv = snv(X)
fig, ax = plt.subplots(figsize=(10, 6.0))
for i in range(len(X)):
    ax.plot(wl, Xsnv[i], color=cmap(norm(fat[i])), lw=0.7, alpha=0.6)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("SNV absorbance (a.u.)")
ax.set_title("After SNV scatter correction (baseline aligned)")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
cb = fig.colorbar(sm, ax=ax); cb.set_label("Fat (%)")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig02_snv_spectra.png")); plt.close(fig)
print("saved fig02_snv_spectra.png")

print("\n01_data_prep done.")
