# -*- coding: utf-8 -*-
"""
04_sugar_pca.py — reproduce the PCA analysis from Yeh (2025) J. Chem. Educ.
on the FIVE-SUGAR NIR data, in the teaching-video visual style.

Data: D:/JCE/five_sugar_0511_2023_innospectra.csv
      25 samples (fructose/glucose/lactose/maltose/sucrose x5), 228 wavelengths 901-1700 nm.

Figures (-> python/figures/):
  sugar01_raw_spectra   raw NIR spectra by sugar          (paper Fig 3)
  sugar02_raw_score     raw PCA score plot PC1-PC2         (paper Fig 4b/d)
  sugar03_raw_loading   raw PCA loadings vs wavelength     (paper Fig 4e)  -> OH peaks
  sugar04_prep_score    score plot after cut + SG 2nd deriv(paper Fig 5c/e)
  sugar05_prep_loading  loadings after preprocessing       (paper Fig 5f)
Preprocessing follows the paper: keep 949.7-1650.8 nm, then Savitzky-Golay
2nd derivative, polynomial order 2, window 5.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA
from nir_utils import house_style, FIG, PALETTE

house_style()
CSV = r"D:/JCE/five_sugar_0511_2023_innospectra.csv"
df = pd.read_csv(CSV)
wl = np.array([float(c) for c in df.columns[2:]])
X = df.iloc[:, 2:].to_numpy(float)
labels = df["sugar_group"].astype(str).values
order = ["fructose", "glucose", "lactose", "maltose", "sucrose"]
SUGAR_C = {"fructose": "#2A6F97", "glucose": "#E36414", "lactose": "#0E7C7B",
           "maltose": "#C8941F", "sucrose": "#6A4C93"}
print(f"X={X.shape}  wl={wl.min():.0f}-{wl.max():.0f} nm  sugars={order}")


def scatter_by_sugar(ax, xs, ys):
    for s in order:
        m = labels == s
        ax.scatter(xs[m], ys[m], s=120, color=SUGAR_C[s], edgecolor=PALETTE["ink"],
                   linewidth=0.5, label=s, zorder=3)
    ax.legend(title="sugar", loc="best", framealpha=.9)


# ---------- Fig 3: raw spectra ----------
fig, ax = plt.subplots(figsize=(10, 6.0))
for s in order:
    for i in np.where(labels == s)[0]:
        ax.plot(wl, X[i], color=SUGAR_C[s], lw=1.1, alpha=.8)
    ax.plot([], [], color=SUGAR_C[s], lw=2.5, label=s)
ax.axvspan(1400, 1500, color=PALETTE["gold"], alpha=.10)
ax.annotate("O–H\n(1400–1500 nm)", (1450, ax.get_ylim()[1]*0.92), ha="center", fontsize=12)
ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("Absorbance")
ax.set_title("NIR spectra of five white sugars (5 scans each)")
ax.legend(title="sugar", ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13))
fig.tight_layout(); fig.savefig(os.path.join(FIG, "sugar01_raw_spectra.png")); plt.close(fig)
print("saved sugar01_raw_spectra.png")

# ---------- raw PCA ----------
pca = PCA(n_components=5).fit(X)
T = pca.transform(X); evr = pca.explained_variance_ratio_ * 100
print("raw EVR%:", np.round(evr[:4], 2), " cum:", np.round(np.cumsum(evr)[:3], 2))
fig, ax = plt.subplots(figsize=(9.2, 6.6))
scatter_by_sugar(ax, T[:, 0], T[:, 1])
ax.axhline(0, color=PALETTE["grid"], lw=1); ax.axvline(0, color=PALETTE["grid"], lw=1)
ax.set_xlabel(f"PC1  ({evr[0]:.1f}%)"); ax.set_ylabel(f"PC2  ({evr[1]:.1f}%)")
ax.set_title("Raw-spectra PCA score plot — five sugars separate")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "sugar02_raw_score.png")); plt.close(fig)
print("saved sugar02_raw_score.png")

# raw loadings
L = pca.components_
p1 = wl[np.argmax(np.abs(L[0]))]; p2 = wl[np.argmax(np.abs(L[1]))]
print(f"raw loading peaks: PC1 ~{p1:.1f} nm, PC2 ~{p2:.1f} nm")
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.plot(wl, L[0], color=PALETTE["coral"], lw=2.6, label=f"PC1 ({evr[0]:.1f}%)")
ax.plot(wl, L[1], color="#2A8C3A", lw=2.6, label=f"PC2 ({evr[1]:.1f}%)")
ax.axhline(0, color=PALETTE["ink"], lw=1)
for p, c in [(p1, PALETTE["coral"]), (p2, "#2A8C3A")]:
    ax.axvline(p, color=c, ls=":", lw=1.5)
    ax.annotate(f"{p:.0f} nm", (p, ax.get_ylim()[1]*0.86), color=c, fontsize=12, ha="center")
ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("Loading")
ax.set_title("Raw-spectra loadings — peaks at the sugars' O–H bands")
ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(FIG, "sugar03_raw_loading.png")); plt.close(fig)
print("saved sugar03_raw_loading.png")

# ---------- preprocessing: cut 949.7-1650.8 nm + SG 2nd derivative ----------
keep = (wl >= 949.7) & (wl <= 1650.8)
wl2 = wl[keep]
Xp = savgol_filter(X[:, keep], window_length=5, polyorder=2, deriv=2, axis=1)
pca2 = PCA(n_components=5).fit(Xp)
T2 = pca2.transform(Xp); evr2 = pca2.explained_variance_ratio_ * 100
print("prep EVR%:", np.round(evr2[:4], 2), " cum:", np.round(np.cumsum(evr2)[:3], 2))
fig, ax = plt.subplots(figsize=(9.2, 6.6))
scatter_by_sugar(ax, T2[:, 0], T2[:, 1])
ax.axhline(0, color=PALETTE["grid"], lw=1); ax.axvline(0, color=PALETTE["grid"], lw=1)
ax.set_xlabel(f"PC1  ({evr2[0]:.1f}%)"); ax.set_ylabel(f"PC2  ({evr2[1]:.1f}%)")
ax.set_title("After preprocessing (cut + SG 2nd-derivative)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "sugar04_prep_score.png")); plt.close(fig)
print("saved sugar04_prep_score.png")

L2 = pca2.components_
q1 = wl2[np.argmax(np.abs(L2[0]))]; q2 = wl2[np.argmax(np.abs(L2[1]))]
print(f"prep loading peaks: PC1 ~{q1:.1f} nm, PC2 ~{q2:.1f} nm")
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.plot(wl2, L2[0], color=PALETTE["coral"], lw=2.4, label=f"PC1 ({evr2[0]:.1f}%)")
ax.plot(wl2, L2[1], color="#2A8C3A", lw=2.4, label=f"PC2 ({evr2[1]:.1f}%)")
ax.axhline(0, color=PALETTE["ink"], lw=1)
ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("Loading (2nd-derivative)")
ax.set_title("Preprocessed loadings — sharper, resolved features")
ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(FIG, "sugar05_prep_loading.png")); plt.close(fig)
print("saved sugar05_prep_loading.png")
print("\n04_sugar_pca done.")
