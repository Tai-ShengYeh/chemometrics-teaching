# -*- coding: utf-8 -*-
"""
build_outlier_notebook.py — generate 02_outlier_detection.ipynb (Colab-ready).

Run:  python notebooks/build_outlier_notebook.py
Output: notebooks/02_outlier_detection.ipynb

Self-contained: loads Corn + honey CSVs straight from the course GitHub repo
(no upload), uses only Colab-preinstalled libs (numpy/pandas/sklearn/scipy/matplotlib).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/Tai-ShengYeh/chemometrics-teaching/main/data"

def md(*t): return {"cell_type": "markdown", "metadata": {}, "source": "\n".join(t)}
def code(*t): return {"cell_type": "code", "metadata": {}, "execution_count": None,
                      "outputs": [], "source": "\n".join(t)}

COLAB = ("https://colab.research.google.com/github/Tai-ShengYeh/"
         "chemometrics-teaching/blob/main/notebooks/02_outlier_detection.ipynb")

cells = []

cells.append(md(
f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})",
"",
"# 近紅外光譜的離群值偵測 — Hotelling $T^2$ 與 Q 殘差",
"",
"**近紅外光譜 × 食品分析化學計量學** · 離群值偵測 Jupyter Notebook",
"",
"這本 notebook 教你在 NIR 光譜資料中找出**離群樣本 (outliers)**，用兩個公開／教學資料集：",
"",
"1. **Eigenvector Corn**（80 玉米樣本 × 3 台儀器 × 700 波長）— 化學計量學經典離群教學集。",
"2. **蜂蜜摻假**（教學模擬資料）— 摻糖漿 = 殘差空間離群，帶到 SIMCA / one-class 觀念。",
"",
"核心觀念——**離群值有兩種，不是同一回事**：",
"",
"| 指標 | 空間 | 抓到什麼 | 幾何意義 |",
"|------|------|----------|----------|",
"| **Hotelling $T^2$** | 模型內 (score space) | 在主成分方向上「太極端」的樣本 | 離群心太遠、高 leverage |",
"| **Q 殘差 / SPE** | 模型外 (residual space) | 模型「解釋不了」的樣本（新化學訊號） | 偏離主成分超平面 |",
"",
"> 一個樣本可能 $T^2$ 高但 Q 低（極端但仍符合模型）、Q 高但 $T^2$ 低（有模型沒見過的訊號，如摻假），或兩者都高。",
"",
"---",
"### ▶ 在 Google Colab 執行（建議，零安裝）",
"點最上方 **Open in Colab** → `執行階段 ▸ 全部執行`。資料直接從 GitHub 線上讀取，**不用上傳檔案**。",
))

cells.append(code(
"# === 0a. 讓圖表能顯示中文（Colab 預設無中文字型；本機略過）===",
"import matplotlib, matplotlib.pyplot as plt, os, urllib.request",
"try:",
"    fp = '/tmp/NotoSansTC.otf'",
"    if not os.path.exists(fp):",
"        urllib.request.urlretrieve(",
"          'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf', fp)",
"    matplotlib.font_manager.fontManager.addfont(fp)",
"    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC']",
"except Exception as e:",
"    for f in ['Microsoft JhengHei','PingFang TC','Noto Sans CJK TC','SimHei']:",
"        if any(f in x.name for x in matplotlib.font_manager.fontManager.ttflist):",
"            plt.rcParams['font.sans-serif'] = [f]; break",
"plt.rcParams['axes.unicode_minus'] = False",
"print('字型設定完成，圖表可顯示中文')",
))

cells.append(code(
"# === 0b. 套件與工具函式（Colab 已預裝，直接執行）===",
"import numpy as np, pandas as pd",
"from sklearn.decomposition import PCA",
"from scipy.stats import f as f_dist, norm, chi2",
"plt.rcParams['figure.dpi'] = 110",
"",
"def snv(X):",
"    \"\"\"Standard Normal Variate：逐樣本去散射（減均值除標準差）\"\"\"",
"    return (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)",
"",
"def hotelling_t2_limit(n, A, alpha=0.95):",
"    \"\"\"T^2 控制界限：A(n-1)/(n-A) * F(alpha; A, n-A)\"\"\"",
"    return A*(n-1)/(n-A) * f_dist.ppf(alpha, A, n-A)",
"",
"def q_limit(residual_eigenvalues, alpha=0.95):",
"    \"\"\"Q/SPE 界限（Jackson–Mudholkar 1979）\"\"\"",
"    ev = np.asarray(residual_eigenvalues, float)",
"    th1, th2, th3 = ev.sum(), (ev**2).sum(), (ev**3).sum()",
"    if th1 <= 0: return np.inf",
"    h0 = 1 - 2*th1*th3/(3*th2**2)",
"    ca = norm.ppf(alpha)",
"    return th1*(ca*np.sqrt(2*th2*h0**2)/th1 + 1 + th2*h0*(h0-1)/th1**2)**(1/h0)",
"",
"def pca_t2_q(X, A):",
"    \"\"\"對已置中的 X 做 PCA，回傳 scores、T^2、Q、界限。\"\"\"",
"    p = PCA(n_components=min(X.shape)-1).fit(X)",
"    T_all = p.transform(X)",
"    lam = p.explained_variance_            # = 特徵值 (S^2/(n-1))",
"    T = T_all[:, :A]",
"    t2 = np.sum(T**2 / lam[:A], axis=1)",
"    Xhat = T @ p.components_[:A]",
"    Q = np.sum((X - Xhat)**2, axis=1)",
"    t2lim = hotelling_t2_limit(X.shape[0], A, 0.95)",
"    qlim = q_limit(lam[A:], 0.95)",
"    return p, T, t2, Q, t2lim, qlim, lam",
))

# ---------- PART 1: CORN ----------
cells.append(md(
"## Part 1 — Corn NIR：$T^2$ vs Q 的經典對比",
"",
"Eigenvector **Corn** 資料集：80 個玉米樣本，同一批樣本用 3 台近紅外儀（m5 / mp5 / mp6）量測，"
"波長 1100–2498 nm（700 點、2 nm），附 moisture / oil / protein / starch 四個參考值。",
"先用單一台儀器 **m5**，做 SNV → PCA → 找離群。",
))

cells.append(code(
"# 1-1 載入 Corn m5（80×700）",
f"corn = pd.read_csv('{RAW}/corn_m5.csv')",
"meta = ['sample','moisture','oil','protein','starch']",
"wl = np.array([float(c) for c in corn.columns if c not in meta])",
"Xm5 = corn[[c for c in corn.columns if c not in meta]].to_numpy(float)",
"print('X:', Xm5.shape, '| 波長', wl.min(),'-',wl.max(),'nm')",
"",
"fig, ax = plt.subplots(1,2, figsize=(11,3.4))",
"ax[0].plot(wl, Xm5.T, lw=.4); ax[0].set_title('原始光譜'); ax[0].set_xlabel('波長 nm')",
"ax[1].plot(wl, snv(Xm5).T, lw=.4); ax[1].set_title('SNV 前處理後'); ax[1].set_xlabel('波長 nm')",
"plt.tight_layout(); plt.show()",
))

cells.append(code(
"# 1-2 SNV + PCA，計算 T^2 與 Q",
"A = 5                                   # 主成分數（教學上先固定 5）",
"Xc = snv(Xm5); Xc = Xc - Xc.mean(0)     # SNV 後再置中",
"p, T, t2, Q, t2lim, qlim, lam = pca_t2_q(Xc, A)",
"print(f'解釋變異 (前{A} PC): {p.explained_variance_ratio_[:A].sum()*100:.1f}%')",
"print(f'T^2 95%界限 = {t2lim:.2f} | Q 95%界限 = {qlim:.4f}')",
"hi_t2 = np.where(t2 > t2lim)[0] + 1",
"hi_q  = np.where(Q  > qlim)[0] + 1",
"print('高 T^2 樣本:', hi_t2.tolist())",
"print('高 Q   樣本:', hi_q.tolist())",
))

cells.append(md(
"### 1-3 Score plot + Hotelling $T^2$ 95% 信賴橢圓",
"在 PC1–PC2 平面畫出 95% 信賴橢圓；**掉在橢圓外**的點是 $T^2$ 方向的離群候選。",
))

cells.append(code(
"# 橢圓半軸 = sqrt(特徵值 × T2界限(A=2))",
"t2lim2 = hotelling_t2_limit(len(Xc), 2, 0.95)",
"rx, ry = np.sqrt(lam[0]*t2lim2), np.sqrt(lam[1]*t2lim2)",
"th = np.linspace(0, 2*np.pi, 200)",
"",
"fig, ax = plt.subplots(figsize=(6,5))",
"sc = ax.scatter(T[:,0], T[:,1], c=t2, cmap='viridis', s=40, edgecolor='k', lw=.4)",
"ax.plot(rx*np.cos(th), ry*np.sin(th), 'r--', lw=1.6, label='95% T² 橢圓')",
"for i in np.where(t2>t2lim)[0]:",
"    ax.annotate(str(i+1), (T[i,0], T[i,1]), fontsize=9, fontweight='bold', color='crimson')",
"ax.axhline(0,color='0.8',lw=.6); ax.axvline(0,color='0.8',lw=.6)",
"ax.set_xlabel('PC1'); ax.set_ylabel('PC2'); ax.legend()",
"ax.set_title('Corn m5 — PCA score plot（色=T²）')",
"plt.colorbar(sc,label='Hotelling T²'); plt.tight_layout(); plt.show()",
))

cells.append(md(
"### 1-4 影響圖 (Influence plot)：$T^2$ vs Q — 最重要的一張圖",
"把每個樣本畫在 ($T^2$, Q) 平面，兩條虛線是 95% 界限，分成四象限：",
"",
"- **右下**（高 $T^2$、低 Q）：極端但仍符合模型 — 高 leverage 樣本。",
"- **左上**（低 $T^2$、高 Q）：模型沒見過的訊號 — 疑似**摻假 / 汙染 / 錯樣**。",
"- **右上**（兩者都高）：最可疑，通常該剔除。",
))

cells.append(code(
"fig, ax = plt.subplots(figsize=(6.4,5))",
"ax.scatter(t2, Q, s=40, edgecolor='k', lw=.4, color='#0E7C7B')",
"ax.axvline(t2lim, color='r', ls='--', lw=1.3); ax.axhline(qlim, color='r', ls='--', lw=1.3)",
"for i in range(len(t2)):",
"    if t2[i]>t2lim or Q[i]>qlim:",
"        ax.annotate(str(i+1), (t2[i], Q[i]), fontsize=9, fontweight='bold', color='crimson')",
"ax.set_xlabel('Hotelling T²  (模型內 / leverage)')",
"ax.set_ylabel('Q 殘差 / SPE  (模型外)')",
"ax.set_title('Corn m5 — 影響圖 (T² vs Q)')",
"ax.text(t2lim*1.02, ax.get_ylim()[1]*.95, 'T² 界限', color='r', fontsize=8)",
"ax.text(ax.get_xlim()[1]*.7, qlim*1.05, 'Q 界限', color='r', fontsize=8)",
"plt.tight_layout(); plt.show()",
))

cells.append(md(
"### 1-5 為什麼樣本 75（高 $T^2$）和樣本 46（高 Q）不一樣？",
"把兩個代表性離群的光譜疊到樣本平均上看差異：高 $T^2$ 者「形狀對、但幅度極端」；"
"高 Q 者「有一段模型解釋不掉的殘差」。",
))

cells.append(code(
"# 找出各自最大的樣本（避免寫死索引）",
"i_t2 = int(np.argmax(t2)); i_q = int(np.argmax(Q))",
"Xsnv = snv(Xm5); mu = Xsnv.mean(0)",
"fig, ax = plt.subplots(1,2, figsize=(11,3.6))",
"ax[0].plot(wl, mu, 'k', lw=1, label='全體平均')",
"ax[0].plot(wl, Xsnv[i_t2], 'crimson', lw=1, label=f'樣本{i_t2+1} (max T²)')",
"ax[0].set_title('高 T²：形狀相符、幅度極端'); ax[0].legend(fontsize=8); ax[0].set_xlabel('波長 nm')",
"# 殘差圖",
"Xhat = (T @ p.components_[:A])",
"ax[1].plot(wl, (Xc-Xhat)[i_q], 'darkorange', lw=1, label=f'樣本{i_q+1} (max Q) 殘差')",
"ax[1].axhline(0,color='0.7',lw=.6)",
"ax[1].set_title('高 Q：一段模型解釋不掉的殘差'); ax[1].legend(fontsize=8); ax[1].set_xlabel('波長 nm')",
"plt.tight_layout(); plt.show()",
))

# ---------- PART 2: instrument outliers ----------
cells.append(md(
"## Part 2 — 「離群不一定是壞樣本」：儀器差異造成的系統性離群",
"把同一批 80 樣本在 **3 台儀器** 的光譜疊在一起（240 列）做 PCA。你會看到三群分開——"
"這不是樣本壞掉，而是**儀器/校正差異**。前處理（SNV）可大幅拉近，這正是 calibration transfer 的動機。",
))

cells.append(code(
f"c3 = pd.read_csv('{RAW}/corn_3instruments.csv')",
"wl3 = np.array([float(x) for x in c3.columns if x not in ('sample','instrument')])",
"X3 = c3[[x for x in c3.columns if x not in ('sample','instrument')]].to_numpy(float)",
"inst = c3['instrument'].to_numpy()",
"colors = {'m5':'#0E7C7B','mp5':'#E36414','mp6':'#C8941F'}",
"",
"fig, ax = plt.subplots(1,2, figsize=(11,4))",
"for name, Xin, ttl in [('raw', X3, '原始光譜 → 三台儀器分很開'),",
"                        ('snv', snv(X3), 'SNV 後 → 三群靠攏')]:",
"    a = ax[0] if name=='raw' else ax[1]",
"    sc = PCA(2).fit_transform(Xin - Xin.mean(0))",
"    for g in ['m5','mp5','mp6']:",
"        m = inst==g; a.scatter(sc[m,0], sc[m,1], s=18, c=colors[g], label=g, alpha=.7)",
"    a.set_title(ttl); a.set_xlabel('PC1'); a.set_ylabel('PC2'); a.legend()",
"plt.tight_layout(); plt.show()",
))

# ---------- PART 3: HONEY ----------
cells.append(md(
"## Part 3 — 蜂蜜摻假：摻糖漿 = 殘差空間離群（SIMCA / one-class 觀念）",
"",
"> ⚠ **教學模擬資料**：譜帶中心取自真實 NIR 文獻（水 O–H ~1450 / 1940 nm、糖 C–H/O–H overtone ~1200 / 1690 / 2100 nm），"
"但光譜為程式合成，僅供教學示範，不可用於真實蜂蜜鑑別結論。",
"",
"作法：**只用純蜜樣本建 PCA 模型**（one-class），再把摻假樣本投影進來看 Q 殘差。"
"摻假引入模型沒見過的糖漿訊號 → **Q 會隨摻假比例上升**。這就是 SIMCA 類別建模的核心。",
))

cells.append(code(
f"honey = pd.read_csv('{RAW}/honey_nir.csv')",
"hmeta = ['sample','label','adulterant','level_pct']",
"hwl = np.array([float(c) for c in honey.columns if c not in hmeta])",
"Xh = honey[[c for c in honey.columns if c not in hmeta]].to_numpy(float)",
"is_pure = (honey['adulterant']=='none').to_numpy()      # 純蜜（不含 gross）",
"print('總樣本', len(honey), '| 純蜜', is_pure.sum(),",
"      '| 摻假', (honey['label']=='adulterated').sum(), '| gross 離群 3')",
))

cells.append(code(
"# 3-1 只用純蜜建模，投影全部樣本",
"Ah = 4",
"Xhs = snv(Xh)",
"mu_pure = Xhs[is_pure].mean(0)",
"Xhc = Xhs - mu_pure",
"pmod = PCA(Ah).fit(Xhc[is_pure])",
"Th = pmod.transform(Xhc)",
"Qh = np.sum((Xhc - Th @ pmod.components_)**2, axis=1)",
"lam_p = pmod.explained_variance_",
"t2h = np.sum(Th**2 / lam_p, axis=1)",
"# 界限由純蜜分佈估計",
"qlim_h = np.percentile(Qh[is_pure], 95)",
"t2lim_h = hotelling_t2_limit(is_pure.sum(), Ah, 0.95)",
"print(f'Q 95%界限(純蜜) = {qlim_h:.3f}')",
))

cells.append(code(
"# 3-2 Q 隨摻假比例上升",
"fig, ax = plt.subplots(1,2, figsize=(11,4))",
"box = [Qh[is_pure]] + [Qh[((honey['level_pct']==L)&(honey['label']=='adulterated')).to_numpy()] for L in [10,20,40]]",
"ax[0].boxplot(box, labels=['純蜜','10%','20%','40%'])",
"ax[0].axhline(qlim_h, color='r', ls='--', label='Q 95%界限'); ax[0].set_yscale('log')",
"ax[0].set_ylabel('Q 殘差 (log)'); ax[0].set_title('摻假比例 ↑ → Q ↑'); ax[0].legend()",
"# 影響圖，色=摻假比例",
"col = honey['level_pct'].to_numpy()",
"sc = ax[1].scatter(t2h, Qh, c=col, cmap='YlOrRd', s=28, edgecolor='k', lw=.3)",
"gross = honey['adulterant'].str.startswith('gross').to_numpy()",
"ax[1].scatter(t2h[gross], Qh[gross], s=90, facecolors='none', edgecolors='blue', lw=1.6, label='gross 離群')",
"ax[1].axvline(t2lim_h, color='r', ls='--'); ax[1].axhline(qlim_h, color='r', ls='--')",
"ax[1].set_yscale('log'); ax[1].set_xlabel('Hotelling T²'); ax[1].set_ylabel('Q (log)')",
"ax[1].set_title('蜂蜜影響圖（色=摻假%）'); ax[1].legend()",
"plt.colorbar(sc, ax=ax[1], label='摻假 %'); plt.tight_layout(); plt.show()",
))

cells.append(md(
"**觀察**：",
"- 摻假樣本大多落在 **高 Q** 區（模型外）→ 用 Q 就能把摻假抓出來，不需要事先知道摻什麼。",
"- **10% 低比例摻假**有些混在界限附近 → 真實世界低比例摻假難偵測，這是重要限制。",
"- 藍圈 gross 離群（氣泡/高溫/汙染）：`hot` 同時高 $T^2$ 高 Q；`bubble`/`dirty` 主要是高 Q。",
))

# ---------- exercises ----------
cells.append(md(
"## 練習 (Exercises)",
"1. 把 Part 1 的主成分數 `A` 從 5 改成 3 或 8，界限與被標記的離群樣本怎麼變？為什麼 Q 界限對 `A` 很敏感？",
"2. 把 Corn 換成 **mp5** 或 **mp6**（改 `corn_m5.csv` → 用 `corn_3instruments.csv` 篩選），離群樣本是否一致？",
"3. Part 3 改成 **只用 Q** 當摻假判準，畫 ROC / 算在 20% 摻假下的偵測率。",
"4. 進階：把純蜜模型換成 **SIMCA**（scikit-learn 沒有內建，可用 Q+T² 聯合界限），比較單用 Q 的差別。",
"",
"---",
"### 延伸資源",
"- 互動教學頁：<https://tai-shengyeh.github.io/chemometrics-teaching/outlier-detection.html>",
"- Corn 資料集原始出處：Eigenvector Research — <https://eigenvector.com/resources/data-sets/>",
"- 課程首頁：<https://tai-shengyeh.github.io/chemometrics-teaching/>",
))

nb = {
 "cells": cells,
 "metadata": {
   "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
   "language_info": {"name": "python", "version": "3.x"},
   "colab": {"provenance": [], "toc_visible": True},
 },
 "nbformat": 4, "nbformat_minor": 0,
}

out = os.path.join(HERE, "02_outlier_detection.ipynb")
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print("wrote", out, "|", len(cells), "cells")
