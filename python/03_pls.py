# -*- coding: utf-8 -*-
"""
03_pls.py — PLS regression: predict FAT (%) from the Tecator NIR spectra.
  - SNV + Savitzky-Golay 1st-derivative preprocessing
  - choose number of latent variables by 10-fold cross-validation
  - hold-out test set -> R2, RMSEP, RPD
  - figure 6: RMSECV vs #latent variables
  - figure 7: predicted vs measured fat (train + test)
  - figure 8: PLS regression coefficients vs wavelength
Teaching point: PLS finds a few latent variables that BOTH summarise the spectra
AND correlate with fat, giving a quantitative calibration model.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import train_test_split, cross_val_predict, KFold
from sklearn.metrics import r2_score, mean_squared_error
from nir_utils import load_tecator, snv, savgol_d, house_style, FIG, PALETTE

house_style()
wl, X, y = load_tecator()
Y = y["fat"].values

# preprocessing: SNV then SG 1st derivative
Xp = savgol_d(snv(X), window=15, poly=2, deriv=1)

Xtr, Xte, ytr, yte = train_test_split(Xp, Y, test_size=0.25, random_state=42)
print(f"train={Xtr.shape[0]}  test={Xte.shape[0]}")

# ---------- choose latent variables by 10-fold CV ----------
cv = KFold(n_splits=10, shuffle=True, random_state=42)
maxlv = 20
rmsecv = []
for k in range(1, maxlv + 1):
    yhat = cross_val_predict(PLSRegression(n_components=k), Xtr, ytr, cv=cv)
    rmsecv.append(np.sqrt(mean_squared_error(ytr, yhat)))
rmsecv = np.array(rmsecv)
absmin = int(np.argmin(rmsecv) + 1)
# parsimony (elbow) rule: stop when adding 1 more LV improves RMSECV by < 2%.
# This avoids the over-complex absolute minimum and teaches the bias-variance trade-off.
rel_improve = (rmsecv[:-1] - rmsecv[1:]) / rmsecv[:-1]
best = absmin
for k in range(1, maxlv):
    if rel_improve[k - 1] < 0.02:
        best = k
        break
print("RMSECV by LV:", np.round(rmsecv, 3))
print(f"absolute-min LV = {absmin} (RMSECV={rmsecv[absmin-1]:.3f}); "
      f"parsimony elbow LV = {best} (RMSECV={rmsecv[best-1]:.3f})")

# ---------- fit best model, evaluate on hold-out ----------
model = PLSRegression(n_components=best).fit(Xtr, ytr)
ytr_p = model.predict(Xtr).ravel()
yte_p = model.predict(Xte).ravel()
r2c, r2p = r2_score(ytr, ytr_p), r2_score(yte, yte_p)
rmsec = np.sqrt(mean_squared_error(ytr, ytr_p))
rmsep = np.sqrt(mean_squared_error(yte, yte_p))
rpd = yte.std() / rmsep
print(f"CAL  R2={r2c:.3f}  RMSEC={rmsec:.2f}")
print(f"TEST R2={r2p:.3f}  RMSEP={rmsep:.2f}  RPD={rpd:.2f}")

# ---------- figure 6: RMSECV vs LV ----------
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.plot(range(1, maxlv + 1), rmsecv, "-o", color=PALETTE["teal"], lw=2.4, markersize=7)
ax.axvspan(best, maxlv, color=PALETTE["grid"], alpha=0.45, zorder=0)
ax.plot(best, rmsecv[best - 1], "o", color=PALETTE["coral"], markersize=15, zorder=5)
ax.annotate(f"elbow = {best} LV\nRMSECV = {rmsecv[best-1]:.2f}",
            (best, rmsecv[best - 1]), textcoords="offset points", xytext=(24, 22),
            color=PALETTE["coral"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=PALETTE["coral"]))
ax.text(0.97, 0.55, "adding more LVs\nbarely helps → overfit risk", transform=ax.transAxes,
        ha="right", va="center", fontsize=13, color=PALETTE["ink"], style="italic")
ax.set_xlabel("Number of latent variables"); ax.set_ylabel("RMSECV — fat (%)")
ax.set_title("Cross-validation picks the model complexity (parsimony rule)")
ax.set_xticks(range(1, maxlv + 1, 2))
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig06_pls_rmsecv.png")); plt.close(fig)
print("saved fig06_pls_rmsecv.png")

# ---------- figure 7: predicted vs measured ----------
fig, ax = plt.subplots(figsize=(8.6, 8.0))
lo, hi = min(Y) - 3, max(Y) + 3
ax.plot([lo, hi], [lo, hi], "--", color=PALETTE["ink"], lw=1.6, label="1 : 1")
ax.scatter(ytr, ytr_p, s=60, color=PALETTE["teal"], alpha=0.55,
           edgecolor="white", linewidth=0.4, label=f"Calibration  R²={r2c:.3f}")
ax.scatter(yte, yte_p, s=85, color=PALETTE["coral"], edgecolor=PALETTE["ink"],
           linewidth=0.5, label=f"Test  R²={r2p:.3f}", zorder=4)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
ax.set_xlabel("Measured fat (%)"); ax.set_ylabel("Predicted fat (%)")
ax.set_title(f"PLS prediction of fat  ·  {best} latent variables", pad=12)
ax.text(0.97, 0.05, f"RMSEP = {rmsep:.2f} %\nRPD = {rpd:.1f}", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=15, fontweight="bold", color=PALETTE["ink"],
        bbox=dict(boxstyle="round,pad=0.5", fc=PALETTE["paper2"], ec=PALETTE["coral"], lw=1.4))
ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig07_pls_pred_vs_meas.png")); plt.close(fig)
print("saved fig07_pls_pred_vs_meas.png")

# ---------- figure 8: regression coefficients ----------
coef = np.asarray(model.coef_).ravel()
if coef.shape[0] != len(wl):  # sklearn may return (1, n_features)
    coef = coef.reshape(-1)[:len(wl)]
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.plot(wl, coef, color=PALETTE["teal"], lw=2.6)
ax.axhline(0, color=PALETTE["ink"], lw=1)
ax.fill_between(wl, coef, 0, where=coef > 0, color=PALETTE["teal"], alpha=0.18)
ax.fill_between(wl, coef, 0, where=coef < 0, color=PALETTE["coral"], alpha=0.18)
ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("PLS regression coefficient")
ax.set_title("Where the model 'looks' — wavelengths that predict fat")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig08_pls_coef.png")); plt.close(fig)
print("saved fig08_pls_coef.png")

# save a metrics summary for the script/HTML
with open(os.path.join(os.path.dirname(FIG), "..", "data", "pls_metrics.txt"),
          "w", encoding="utf-8") as f:
    f.write(f"best_LV={best}\nR2C={r2c:.3f}\nRMSEC={rmsec:.2f}\n"
            f"R2P={r2p:.3f}\nRMSEP={rmsep:.2f}\nRPD={rpd:.2f}\n"
            f"n_train={len(ytr)}\nn_test={len(yte)}\n")
print("\n03_pls done.")
