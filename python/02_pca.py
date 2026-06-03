# -*- coding: utf-8 -*-
"""
02_pca.py — Principal Component Analysis of the Tecator NIR spectra.
  - SNV preprocessing, then PCA on the 100 wavelengths
  - figure 3: scree / explained variance
  - figure 4: PC1-PC2 score plot coloured by fat (+ Hotelling T2 95% ellipse)
  - figure 5: PC1 & PC2 loadings vs wavelength
Teaching point: 100 correlated wavelengths collapse to ~3 components that
capture >99% of the variance, and the samples line up by fat content.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from sklearn.decomposition import PCA
from nir_utils import load_tecator, snv, house_style, FIG, PALETTE

cmap = house_style()
wl, X, y = load_tecator()
fat = y["fat"].values

Xp = snv(X)
pca = PCA(n_components=10).fit(Xp)
scores = pca.transform(Xp)
evr = pca.explained_variance_ratio_ * 100
print("Explained variance (%) per PC:", np.round(evr[:6], 2))
print("Cumulative (%):", np.round(np.cumsum(evr)[:6], 2))

# ---------- figure 3: scree ----------
fig, ax = plt.subplots(figsize=(10, 6.0))
k = np.arange(1, 11)
ax.bar(k, evr, color=PALETTE["teal"], alpha=0.9, label="Individual")
ax2 = ax.twinx()
ax2.plot(k, np.cumsum(evr), "-o", color=PALETTE["coral"], lw=2.6,
         markersize=8, label="Cumulative")
ax2.set_ylim(0, 108)
cum = np.cumsum(evr)
box = (f"Cumulative variance\nPC1:      {cum[0]:.1f}%\n"
       f"PC1–2:  {cum[1]:.1f}%\nPC1–3:  {cum[2]:.1f}%")
ax.text(0.46, 0.42, box, transform=ax.transAxes, fontsize=15,
        color=PALETTE["ink"], family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", fc=PALETTE["paper2"], ec=PALETTE["coral"], lw=1.4))
ax.set_xlabel("Principal component"); ax.set_ylabel("Variance explained (%)")
ax2.set_ylabel("Cumulative (%)", color=PALETTE["coral"])
ax.set_title("Scree plot — first 3 PCs capture almost all the variance", pad=16)
ax.set_xticks(k); ax.grid(axis="x", alpha=0)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig03_pca_scree.png")); plt.close(fig)
print("saved fig03_pca_scree.png")

# ---------- figure 4: score plot ----------
norm = plt.Normalize(fat.min(), fat.max())
fig, ax = plt.subplots(figsize=(10, 6.4))
sc = ax.scatter(scores[:, 0], scores[:, 1], c=fat, cmap=cmap, s=70,
                edgecolor=PALETTE["ink"], linewidth=0.4, zorder=3)
# Hotelling T2 95% confidence ellipse
from scipy.stats import f as fdist
cov = np.cov(scores[:, :2].T)
vals, vecs = np.linalg.eigh(cov)
order = vals.argsort()[::-1]; vals, vecs = vals[order], vecs[:, order]
theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
n = len(scores); conf = 0.95
t2 = 2 * (n - 1) / (n - 2) * fdist.ppf(conf, 2, n - 2)
w, h = 2 * np.sqrt(vals * t2)
ax.add_patch(Ellipse((scores[:, 0].mean(), scores[:, 1].mean()), w, h, angle=theta,
                      fill=False, edgecolor=PALETTE["ink"], ls="--", lw=1.8, zorder=2))
ax.axhline(0, color=PALETTE["grid"], lw=1); ax.axvline(0, color=PALETTE["grid"], lw=1)
ax.set_xlabel(f"PC1  ({evr[0]:.1f}%)"); ax.set_ylabel(f"PC2  ({evr[1]:.1f}%)")
ax.set_title("PCA score plot — coloured by fat (%)")
cb = fig.colorbar(sc, ax=ax); cb.set_label("Fat (%)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig04_pca_scores.png")); plt.close(fig)
print("saved fig04_pca_scores.png")

# ---------- figure 5: loadings ----------
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.plot(wl, pca.components_[0], color=PALETTE["teal"], lw=2.8, label=f"PC1 loading ({evr[0]:.1f}%)")
ax.plot(wl, pca.components_[1], color=PALETTE["coral"], lw=2.8, label=f"PC2 loading ({evr[1]:.1f}%)")
ax.axhline(0, color=PALETTE["ink"], lw=1)
ax.axvspan(920, 940, color=PALETTE["gold"], alpha=0.15)
ax.annotate("~930 nm\nC-H (fat)", (930, ax.get_ylim()[1]*0.7), ha="center",
            color=PALETTE["ink"], fontsize=13)
ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("Loading weight")
ax.set_title("PCA loadings — which wavelengths drive each component")
ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig05_pca_loadings.png")); plt.close(fig)
print("saved fig05_pca_loadings.png")

print("\n02_pca done.")
