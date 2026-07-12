# -*- coding: utf-8 -*-
"""
06_outlier_figs.py — render the figures used by outlier-detection.html.
Output: python/figures/outlier/*.png   (Corn + honey outlier detection)
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy.stats import f as f_dist, norm

for fam in ["Microsoft JhengHei", "Noto Sans CJK TC", "PingFang TC", "SimHei"]:
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [fam]; break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 130

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "figures", "outlier")
os.makedirs(OUT, exist_ok=True)
TEAL, CORAL, GOLD, INK = "#0E7C7B", "#E36414", "#C8941F", "#1A1A1A"


def snv(X): return (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)
def t2lim(n, A, a=0.95): return A*(n-1)/(n-A)*f_dist.ppf(a, A, n-A)
def qlim(ev, a=0.95):
    ev = np.asarray(ev, float); th1, th2, th3 = ev.sum(), (ev**2).sum(), (ev**3).sum()
    h0 = 1 - 2*th1*th3/(3*th2**2); ca = norm.ppf(a)
    return th1*(ca*np.sqrt(2*th2*h0**2)/th1 + 1 + th2*h0*(h0-1)/th1**2)**(1/h0)
def save(fig, name):
    p = os.path.join(OUT, name); fig.savefig(p, bbox_inches="tight", facecolor="#FAF7EE")
    plt.close(fig); print("wrote", name)


# ---------------- Corn m5 ----------------
corn = pd.read_csv(os.path.join(DATA, "corn_m5.csv"))
meta = ["sample", "moisture", "oil", "protein", "starch"]
wl = np.array([float(c) for c in corn.columns if c not in meta])
X = corn[[c for c in corn.columns if c not in meta]].to_numpy(float)
A = 5
Xc = snv(X); mu = Xc.mean(0); Xc = Xc - mu
p = PCA(min(X.shape)-1).fit(Xc)
T = p.transform(Xc)[:, :A]; lam = p.explained_variance_
t2 = np.sum(T**2/lam[:A], 1)
Q = np.sum((Xc - T @ p.components_[:A])**2, 1)
TL, QL = t2lim(len(X), A), qlim(lam[A:])

# Fig A: raw vs SNV
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ax[0].plot(wl, X.T, lw=.35); ax[0].set_title("原始光譜"); ax[0].set_xlabel("波長 (nm)"); ax[0].set_ylabel("吸光值")
ax[1].plot(wl, snv(X).T, lw=.35); ax[1].set_title("SNV 前處理後"); ax[1].set_xlabel("波長 (nm)")
save(fig, "corn_spectra.png")

# Fig B: score plot + T2 ellipse
tl2 = t2lim(len(X), 2); rx, ry = np.sqrt(lam[0]*tl2), np.sqrt(lam[1]*tl2)
th = np.linspace(0, 2*np.pi, 200)
fig, ax = plt.subplots(figsize=(5.4, 4.6))
sc = ax.scatter(T[:, 0], T[:, 1], c=t2, cmap="viridis", s=42, edgecolor="k", lw=.4)
ax.plot(rx*np.cos(th), ry*np.sin(th), "--", color=CORAL, lw=1.8, label="95% $T^2$ 橢圓")
for i in np.where(t2 > TL)[0]:
    ax.annotate(str(i+1), (T[i, 0], T[i, 1]), fontsize=10, fontweight="bold", color=CORAL)
ax.axhline(0, color="0.8", lw=.6); ax.axvline(0, color="0.8", lw=.6)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.legend(loc="upper left")
ax.set_title("Corn m5 · PCA 分數圖（色 = $T^2$）")
fig.colorbar(sc, label="Hotelling $T^2$")
save(fig, "corn_scoreplot.png")

# Fig C: influence plot T2 vs Q
fig, ax = plt.subplots(figsize=(5.8, 4.6))
ax.scatter(t2, Q, s=44, edgecolor="k", lw=.4, color=TEAL)
ax.axvline(TL, color=CORAL, ls="--", lw=1.4); ax.axhline(QL, color=CORAL, ls="--", lw=1.4)
for i in range(len(t2)):
    if t2[i] > TL or Q[i] > QL:
        ax.annotate(str(i+1), (t2[i], Q[i]), fontsize=9.5, fontweight="bold", color=CORAL)
ax.set_xlabel("Hotelling $T^2$（模型內 · leverage）")
ax.set_ylabel("Q 殘差 / SPE（模型外）")
ax.set_title("Corn m5 · 影響圖（$T^2$ vs Q）")
ax.text(TL, ax.get_ylim()[1]*.96, " $T^2$ 界限", color=CORAL, fontsize=9, va="top")
ax.text(ax.get_xlim()[1]*.62, QL*1.04, "Q 界限", color=CORAL, fontsize=9)
save(fig, "corn_influence.png")

# Fig D: why 75 vs 46 differ
i_t2, i_q = int(np.argmax(t2)), int(np.argmax(Q))
Xs = snv(X); mm = Xs.mean(0)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ax[0].plot(wl, mm, "k", lw=1, label="全體平均")
ax[0].plot(wl, Xs[i_t2], color=CORAL, lw=1, label=f"樣本 {i_t2+1}（最大 $T^2$）")
ax[0].set_title("高 $T^2$：形狀相符、幅度極端"); ax[0].legend(fontsize=8); ax[0].set_xlabel("波長 (nm)")
res = (Xc - T @ p.components_[:A])[i_q]
ax[1].plot(wl, res, color=GOLD, lw=1, label=f"樣本 {i_q+1}（最大 Q）殘差")
ax[1].axhline(0, color="0.7", lw=.6)
ax[1].set_title("高 Q：一段模型解釋不掉的殘差"); ax[1].legend(fontsize=8); ax[1].set_xlabel("波長 (nm)")
save(fig, "corn_why.png")

# Fig E: instrument outliers
c3 = pd.read_csv(os.path.join(DATA, "corn_3instruments.csv"))
X3 = c3[[x for x in c3.columns if x not in ("sample", "instrument")]].to_numpy(float)
inst = c3["instrument"].to_numpy()
cols = {"m5": TEAL, "mp5": CORAL, "mp6": GOLD}
fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
for a, (Xin, ttl) in zip(ax, [(X3, "原始光譜 → 三台儀器分很開"), (snv(X3), "SNV 後 → 三群靠攏")]):
    s = PCA(2).fit_transform(Xin - Xin.mean(0))
    for g in ["m5", "mp5", "mp6"]:
        m = inst == g; a.scatter(s[m, 0], s[m, 1], s=16, c=cols[g], label=g, alpha=.75)
    a.set_title(ttl); a.set_xlabel("PC1"); a.set_ylabel("PC2"); a.legend()
save(fig, "corn_instrument.png")

# ---------------- Honey ----------------
honey = pd.read_csv(os.path.join(DATA, "honey_nir.csv"))
hm = ["sample", "label", "adulterant", "level_pct"]
hwl = np.array([float(c) for c in honey.columns if c not in hm])
Xh = honey[[c for c in honey.columns if c not in hm]].to_numpy(float)
is_pure = (honey["adulterant"] == "none").to_numpy()
Ah = 4; Xhs = snv(Xh); Xhc = Xhs - Xhs[is_pure].mean(0)
pm = PCA(Ah).fit(Xhc[is_pure]); Thn = pm.transform(Xhc)
Qh = np.sum((Xhc - Thn @ pm.components_)**2, 1)
t2h = np.sum(Thn**2/pm.explained_variance_, 1)
QLh = np.percentile(Qh[is_pure], 95); TLh = t2lim(is_pure.sum(), Ah)

# Fig F: honey mean spectra pure vs adulterated
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(hwl, snv(Xh)[is_pure].mean(0), color=TEAL, lw=1.6, label="純蜜 平均")
for lv, c in zip([10, 20, 40], ["#f0b37a", CORAL, "#a02c00"]):
    m = ((honey["level_pct"] == lv) & (honey["label"] == "adulterated")).to_numpy()
    ax.plot(hwl, snv(Xh)[m].mean(0), color=c, lw=1.1, label=f"摻糖漿 {lv}%")
ax.set_title("蜂蜜 NIR（SNV）：摻假改變糖帶比例"); ax.set_xlabel("波長 (nm)"); ax.set_ylabel("SNV 吸光值")
ax.legend(fontsize=8)
save(fig, "honey_spectra.png")

# Fig G: Q by adulteration level + influence
fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.8))
box = [Qh[is_pure]] + [Qh[((honey["level_pct"] == L) & (honey["label"] == "adulterated")).to_numpy()] for L in [10, 20, 40]]
bp = ax[0].boxplot(box, labels=["純蜜", "10%", "20%", "40%"], patch_artist=True)
for patch, c in zip(bp["boxes"], [TEAL, "#f0b37a", CORAL, "#a02c00"]):
    patch.set_facecolor(c); patch.set_alpha(.6)
ax[0].axhline(QLh, color=CORAL, ls="--", label="Q 95% 界限"); ax[0].set_yscale("log")
ax[0].set_ylabel("Q 殘差 (log)"); ax[0].set_title("摻假比例 ↑ → Q ↑"); ax[0].legend(fontsize=8)
col = honey["level_pct"].to_numpy()
sc = ax[1].scatter(t2h, Qh, c=col, cmap="YlOrRd", s=30, edgecolor="k", lw=.3)
gross = honey["adulterant"].str.startswith("gross").to_numpy()
ax[1].scatter(t2h[gross], Qh[gross], s=95, facecolors="none", edgecolors=TEAL, lw=1.8, label="gross 離群")
ax[1].axvline(TLh, color=CORAL, ls="--"); ax[1].axhline(QLh, color=CORAL, ls="--")
ax[1].set_yscale("log"); ax[1].set_xlabel("Hotelling $T^2$"); ax[1].set_ylabel("Q (log)")
ax[1].set_title("蜂蜜影響圖（色 = 摻假 %）"); ax[1].legend(fontsize=8)
fig.colorbar(sc, ax=ax[1], label="摻假 %")
save(fig, "honey_influence.png")

print("\nCorn: T2 high", (np.where(t2 > TL)[0]+1).tolist(), "| Q high", (np.where(Q > QL)[0]+1).tolist())
print("Honey Qlim95(pure)=%.3f" % QLh)
