# -*- coding: utf-8 -*-
"""
build_notebooks.py — generate the downloadable / Colab teaching notebooks.

Run:  python notebooks/build_notebooks.py
Output: notebooks/01_beginner_tecator.ipynb

The notebook is fully self-contained: it loads the Tecator CSV straight from the
course GitHub repo (no file upload), and only uses libraries pre-installed in
Google Colab (numpy / pandas / scikit-learn / scipy / matplotlib). So students
can click "Open in Colab" and Run-all with zero installation.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- cell sources
INTRO = """\
# 入門：Tecator 肉品 NIR — PCA 與 PLS

**近紅外光譜 × 食品分析化學計量學** · 入門 Jupyter Notebook

這本 notebook 重現課程入門頁的完整流程：

1. 載入 Tecator 肉品 NIR 資料（240 樣本 × 100 波長）
2. **SNV 前處理** — 看前處理前 / 後光譜的差異
3. **PCA** 探索 — 樣本是否依脂肪含量自動排列
4. **PLS** 預測脂肪含量 — 用交叉驗證挑潛在變量

---

### 在 Google Colab 執行（建議，零安裝）
點最上方的 **Open in Colab** 按鈕 → 上方選單 `執行階段 ▸ 全部執行`。
**完全不用安裝任何東西**：`numpy / pandas / scikit-learn / scipy / matplotlib` 在 Colab 都已預裝；
資料會直接從 GitHub 線上讀取，**連檔案都不用上傳**。沒有電腦也可以用瀏覽器（手機 / 平板）開。

### 在自己電腦執行
先安裝一次套件：`pip install numpy pandas scikit-learn scipy matplotlib`，再用 Jupyter 開啟本檔。
"""

LOAD = """\
# === 0. 載入套件與資料（Colab 不需安裝，直接執行）===
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 直接從課程 GitHub 讀 Tecator 資料：240 肉品樣本 × 100 波長 + moisture/fat/protein
URL = "https://raw.githubusercontent.com/Tai-ShengYeh/chemometrics-teaching/main/data/tecator.csv"
df = pd.read_csv(URL)

meta_cols = ["sample", "moisture", "fat", "protein"]
wl_cols = [c for c in df.columns if c not in meta_cols]   # 100 個波長欄位
wl  = np.array([float(c) for c in wl_cols])               # 波長 (nm)
X   = df[wl_cols].to_numpy(float)                          # 光譜矩陣 (240, 100)
fat = df["fat"].to_numpy(float)                            # 預測目標 y

print("光譜矩陣 X :", X.shape)
print("波長範圍   :", wl.min(), "-", wl.max(), "nm")
df[["moisture", "fat", "protein"]].describe().round(2)
"""

SNV_MD = """\
## 1. SNV 前處理：先降低散射與基線差異

肉品樣本的顆粒大小、表面狀態與量測距離會造成**散射差異**，讓原始光譜整條上下漂移。
SNV（Standard Normal Variate）對**每一條光譜各自**標準化（減掉自己的平均、除以自己的標準差），
讓模型專注在**化學差異**而不是物理散射。

下面把 **raw（原始）** 與 **SNV 處理後** 兩張光譜並排 —— 這就是前處理前後的差異：
左邊基線散開、上下漂移；右邊基線對齊、形狀更一致。
"""

SNV_CODE = """\
def snv(X):
    \"\"\"Standard Normal Variate：逐樣本（逐列）散射校正。\"\"\"
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True)
    return (X - mu) / sd

Xsnv = snv(X)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
norm = plt.Normalize(fat.min(), fat.max())
panels = [(axes[0], X,    "Raw spectra",  "Absorbance"),
          (axes[1], Xsnv, "After SNV",    "SNV absorbance (a.u.)")]
for ax, data, title, ylab in panels:
    for i in range(len(data)):
        ax.plot(wl, data[i], color=plt.cm.viridis(norm(fat[i])), lw=0.6, alpha=0.6)
    ax.set_title(title); ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel(ylab)
sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm); sm.set_array([])
fig.colorbar(sm, ax=axes, label="Fat (%)")
plt.show()
"""

PCA_MD = """\
## 2. PCA：先看脂肪含量是否沿主成分呈現梯度

PCA 是**非監督**方法 —— 它不使用 `fat` 當輸入，但我們可以用 fat 幫分數圖**上色**。
若樣本沿 PC1 / PC2 出現由低脂到高脂的連續梯度，代表光譜的主要變異和成分差異有關。

下面一次畫三張圖：**Scree（變異解釋）**、**Score plot（依脂肪上色）**、**Loadings（哪些波長在主導）**。
"""

PCA_CODE = """\
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

Xp  = StandardScaler().fit_transform(snv(X))   # SNV + 逐變數標準化
pca = PCA(n_components=10).fit(Xp)
T   = pca.transform(Xp)
evr = pca.explained_variance_ratio_ * 100
print("各 PC 解釋變異 (%):", np.round(evr[:5], 2))
print("累積 (%)        :", np.round(np.cumsum(evr)[:5], 2))

fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
# scree
ax[0].bar(range(1, 11), evr, color="#0E7C7B", alpha=.9)
ax[0].plot(range(1, 11), np.cumsum(evr), "-o", color="#E36414")
ax[0].set_title("Scree plot"); ax[0].set_xlabel("PC"); ax[0].set_ylabel("Variance (%)")
# score plot
sc = ax[1].scatter(T[:, 0], T[:, 1], c=fat, cmap="viridis", s=45, edgecolor="k", lw=.3)
ax[1].set_title("PCA score plot (color = fat)")
ax[1].set_xlabel(f"PC1 ({evr[0]:.1f}%)"); ax[1].set_ylabel(f"PC2 ({evr[1]:.1f}%)")
fig.colorbar(sc, ax=ax[1], label="Fat (%)")
# loadings
ax[2].plot(wl, pca.components_[0], color="#0E7C7B", lw=2, label="PC1")
ax[2].plot(wl, pca.components_[1], color="#E36414", lw=2, label="PC2")
ax[2].axhline(0, color="k", lw=.8)
ax[2].set_title("PCA loadings"); ax[2].set_xlabel("Wavelength (nm)"); ax[2].legend()
plt.tight_layout(); plt.show()
"""

PLS_MD = """\
## 3. PLS Regression：用整條光譜預測脂肪含量

PLS 會找出**同時**描述 X 光譜與 y 脂肪含量的潛在變量（latent variables, LV）。
我們用 10 折交叉驗證掃描 LV 數量（看 RMSECV 的轉折點，**不是越多越好**），
再用獨立測試集評估，看預測 vs 真實是否貼近 1:1 對角線。
"""

PLS_CODE = """\
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy.signal import savgol_filter

def savgol_d(X, window=15, poly=2, deriv=1):
    \"\"\"Savitzky-Golay 平滑導數（沿波長軸）。\"\"\"
    return savgol_filter(X, window_length=window, polyorder=poly, deriv=deriv, axis=1)

# 前處理：SNV + Savitzky-Golay 一階導數
Xpls = savgol_d(snv(X))

# 用 10 折 CV 掃描 LV 數量（RMSE 用 np.sqrt 寫法，相容新版 scikit-learn）
cv = KFold(n_splits=10, shuffle=True, random_state=42)
rmsecv = []
for k in range(1, 21):
    yhat = cross_val_predict(PLSRegression(n_components=k), Xpls, fat, cv=cv).ravel()
    rmsecv.append(np.sqrt(mean_squared_error(fat, yhat)))
rmsecv = np.array(rmsecv)
best = int(np.argmin(rmsecv) + 1)
print(f"最佳 LV = {best}   RMSECV = {rmsecv[best-1]:.2f} %")

# 獨立測試集評估
Xtr, Xte, ytr, yte = train_test_split(Xpls, fat, test_size=0.25, random_state=42)
model = PLSRegression(n_components=best).fit(Xtr, ytr)
yte_p = model.predict(Xte).ravel()
r2p   = r2_score(yte, yte_p)
rmsep = np.sqrt(mean_squared_error(yte, yte_p))
print(f"測試集  R2 = {r2p:.3f}   RMSEP = {rmsep:.2f} %   RPD = {yte.std()/rmsep:.1f}")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(range(1, 21), rmsecv, "-o", color="#0E7C7B")
ax[0].plot(best, rmsecv[best-1], "o", color="#E36414", ms=14)
ax[0].set_title("RMSECV vs latent variables"); ax[0].set_xlabel("Latent variables"); ax[0].set_ylabel("RMSECV (fat %)")
lo, hi = fat.min() - 3, fat.max() + 3
ax[1].plot([lo, hi], [lo, hi], "--k", label="1:1")
ax[1].scatter(yte, yte_p, color="#E36414", edgecolor="k", lw=.4)
ax[1].set_title(f"Predicted vs measured ({best} LV, R2={r2p:.2f})")
ax[1].set_xlabel("Measured fat (%)"); ax[1].set_ylabel("Predicted fat (%)"); ax[1].legend()
plt.tight_layout(); plt.show()
"""

NEXT_MD = """\
## 4. 接下來

- **不想寫程式？** 用 **Orange Data Mining** 拖拉式重現同樣的 PCA / PLS：
  下載課程的 `orange/tecator_pca.ows`（PCA）與 `orange/tecator_pls.ows`（PLS），照 `orange/ORANGE_GUIDE.md` 一步步操作。
  （Orange 是桌面程式，需安裝；沒辦法安裝的同學就用這本 Colab notebook。）
- **下一章（中階）**：Coffee–Barley NIR — 從「成分預測」進到「食品摻偽鑑別」。

> 小提醒：本 notebook 用 `np.sqrt(mean_squared_error(...))` 計算 RMSE，
> 相容新版 scikit-learn（舊寫法 `mean_squared_error(..., squared=False)` 在 sklearn ≥ 1.6 已移除）。
"""

CELLS = [
    ("markdown", INTRO),
    ("code",     LOAD),
    ("markdown", SNV_MD),
    ("code",     SNV_CODE),
    ("markdown", PCA_MD),
    ("code",     PCA_CODE),
    ("markdown", PLS_MD),
    ("code",     PLS_CODE),
    ("markdown", NEXT_MD),
]


def build(cells):
    out = []
    for i, (ctype, src) in enumerate(cells):
        cell = {
            "cell_type": ctype,
            "id": f"cell-{i:02d}",
            "metadata": {},
            "source": src.splitlines(keepends=True),
        }
        if ctype == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {
        "cells": out,
        "metadata": {
            "colab": {"provenance": [], "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


if __name__ == "__main__":
    nb = build(CELLS)
    path = os.path.join(HERE, "01_beginner_tecator.ipynb")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {path}  ({len(nb['cells'])} cells)")
