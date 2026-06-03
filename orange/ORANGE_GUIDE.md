# Orange Data Mining 實作指南 — NIR 食品分析（PCA + PLS）

> 給課堂用的「不寫程式」版本。學生用拖拉式 widget，重現 Python 影片裡的 PCA 與 PLS 結果。
> 資料：`../data/tecator.csv`（240 肉品樣本 × 100 波長 + moisture/fat/protein）。
> 一鍵開檔：`nir_tecator_workflow.ows`（已含 8 個 widget、9 條連線）。
> Orange 版本：3.40（PLS widget 為內建，無需額外 add-on）。

---

## Part 0 ｜ 安裝 Orange

1. 到 <https://orangedatamining.com/download> 下載安裝（Windows / macOS 皆可，含 Python）。
2. 開啟 Orange，看到空白 canvas、左側 widget 工具列即安裝成功。
3. 確認有 **PLS** widget：左側 **Model** 類別內應有「PLS」。
   （Orange 3.34 以後內建；若沒有，`Options ▸ Add-ons` 安裝 *Orange3* 更新即可。）

---

## Part 1 ｜ 認識資料

`tecator.csv` 欄位：

| 欄位 | 數量 | 角色 (role) | 說明 |
|------|------|------------|------|
| `sample` | 1 | **meta** | 樣本編號（不參與分析） |
| `850.0` … `1050.0` | 100 | **feature** | 各波長 (nm) 的吸光值 → PCA / PLS 的輸入 |
| `moisture` | 1 | meta | 水分 %（備用目標） |
| `fat` | 1 | **target** | 脂肪 %（PLS 要預測的目標） |
| `protein` | 1 | meta | 蛋白質 %（備用目標） |

> 也可直接用 `../data/tecator_orange.tab`：它已標好角色（`fat` = target、其餘為 meta），省去手動設定。

---

## Part 2 ｜ 開啟現成工作流程

`File ▸ Open` 選 `nir_tecator_workflow.ows`。會看到兩條分支：

```
                ┌──────────────┐
        ┌──────▶│  Data Table  │   檢視原始數字
        │       └──────────────┘
        │       ┌──────┐   Transformed Data   ┌────────────────────┐
        │  ┌───▶│ PCA  │─────────────────────▶│ Scatter Plot 分數圖 │   ← PCA 分支（探索）
 ┌──────┴──┐│   └──────┘                       └────────────────────┘
 │  File   ├┤
 │tecator. ││   ┌──────┐  Learner   ┌───────────────┐
 │  csv    │└──▶│ PLS  │───────────▶│ Test and Score│   R² / RMSE   ← PLS 分支（預測）
 └────┬────┘    └───┬──┘            └───────────────┘
      │             │ Model         ┌─────────────┐  Predictions  ┌──────────────────────┐
      └─────────────┴──────────────▶│ Predictions │──────────────▶│ Scatter Plot 預測vs真實│
                    （Data 同時接 Test&Score / Predictions）        └──────────────────────┘
```

**第一步永遠是設定 File widget**：雙擊 `File` → 右下 `Browse` 選 `../data/tecator.csv` →
在下方欄位角色表把 `fat` 設成 **target (class)**、`sample`/`moisture`/`protein` 設成 **meta**、
其餘 100 個波長維持 **feature** → 按 `Apply`。（用 `.tab` 檔則已設好。）

> 不想用現成檔？Part 3 / Part 4 教你從零拉。

---

## Part 3 ｜ PCA 分支（對應第一支影片）

**目標**：把 100 個波長壓成 2–3 個主成分，看樣本是否依脂肪自動排列。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | 拉 **File** | 載入 `tecator.csv`、`fat`=target | 240 instances、100 features |
| 2 | 接 **Data Table** | （File→Data Table） | 看到原始吸光值表格 |
| 3 | 接 **PCA** | （File→PCA）。視窗內有 **Components** 滑桿與變異解釋曲線 | 拉到累積 ≥ 99% 約 **3 個成分**；PC1 已佔大部分變異 |
| 4 | 接 **Scatter Plot** | PCA 的 **Transformed Data** → Scatter Plot | 下一步上色 |
| 5 | 設定 Scatter Plot | Axis x = **PC1**、y = **PC2**、**Color = fat** | 點沿 PC1 由低脂肪→高脂肪呈漸層（與影片 fig04 一致） |

**教學提問**：
- PCA 有沒有用到 `fat`？（沒有，它是非監督；卻仍依脂肪排列 → 結構自己浮現）
- 把 Color 改成 `moisture` 看看，水分是否也有梯度？
- Scatter Plot 點一個離群點 → 它的光譜是否異常？（呼應 Hotelling T² 概念）

> Orange 的 PCA 預設在原始光譜上計算；Python 版多做了 SNV 散射校正，故座標數值略有不同，
> 但「少數成分捕捉絕大多數變異、樣本依脂肪排列」的結論一致。
> 想更貼近 Python，可在 File 與 PCA 之間插一個 **Preprocess** widget（勾 Normalize Features）。

---

## Part 4 ｜ PLS 分支（對應第二支影片）

**目標**：用光譜建立可預測 `fat` 的回歸模型，並誠實地驗證它。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | **File** | 同上，務必 `fat`=target | — |
| 2 | 接 **PLS** | （File→PLS）。設 **Components (LV) = 4**（對應影片 elbow） | 產生 Learner / Model |
| 3 | 接 **Test and Score** | PLS 的 **Learner** → Test&Score；File 的 **Data** → Test&Score。選 **Cross validation, 10 folds** | 表格顯示 **R² ≈ 0.95–0.97、RMSE ≈ 2–3**（對應 fig07 的測試表現） |
| 4 | 接 **Predictions** | PLS 的 **Model** → Predictions 的 **Predictors**；File 的 **Data** → Predictions 的 **Data** | 每個樣本的預測脂肪 vs 真實脂肪 |
| 5 | 接 **Scatter Plot** | Predictions 的 **Predictions** → Scatter Plot。x = **fat**（真實）、y = **PLS**（預測） | 點緊貼對角線（預測≈真實，呼應 fig07） |

**比較 LV 的影響（重現 fig06 的過度擬合教學）**：
- 把 PLS 的 Components 從 1 → 2 → 4 → 15 逐一調，看 Test&Score 的 RMSE：
  先快速下降，4 之後趨平；硬加到很多反而 cross-validation 沒更好 → **過度擬合**。
- 教學結論：選在「誤差不再明顯下降」的轉折點（這裡 ≈ 4 個 LV），不是越多越好。

**看模型的化學意義**：PLS widget 另有輸出 **Coefficients and Loadings**，
接一個 Data Table 或 Line/Scatter，可看到係數在 ~928 nm 的脂肪 C–H 帶最大（呼應 fig08）。

---

## Part 5 ｜ 和 Python / 影片對照

| 概念 | 影片 / Python 圖 | Orange widget |
|------|-----------------|---------------|
| 原始光譜 | fig01 | File → Data Table（或 Line Plot） |
| 主成分數量 | fig03 scree | PCA 視窗內的變異曲線 / 滑桿 |
| 分數圖（依脂肪上色） | fig04 | PCA → Scatter Plot（Color=fat） |
| 選 LV / 過度擬合 | fig06 | 調 PLS Components + Test and Score |
| 預測 vs 真實 | fig07 | Predictions → Scatter Plot |
| 回歸係數 → 化學 | fig08 | PLS「Coefficients and Loadings」→ Data Table |

學生先看影片建立直覺、看 Python 看「怎麼算」、最後用 Orange 親手「拉一遍」，三層遞進。

---

## Part 6 ｜ 疑難排解

| 現象 | 原因 / 修法 |
|------|------------|
| PLS / Test&Score 灰掉沒反應 | File 沒設 `fat` 為 target（回歸需要數值目標） |
| 找不到 PLS widget | 確認 Orange ≥ 3.34；`Options ▸ Add-ons` 更新 Orange3 |
| 開 .ows 後 widget 紅框 | File 還沒指定檔案路徑：雙擊 File 重新 Browse 到 `tecator.csv` |
| Scatter Plot 沒有 PC1/PC2 選項 | 確認連的是 PCA 的 **Transformed Data**（不是原始 Data） |
| Test&Score 數字和 Python 略不同 | 隨機切分 / 折數不同所致，量級一致即可（R² 都在 0.95+） |
| 中文路徑載入失敗 | 把 `tecator.csv` 複製到純英文路徑再 Browse |
