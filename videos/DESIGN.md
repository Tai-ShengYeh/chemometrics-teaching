# DESIGN — NIR 食品分析教學影片（PCA / PLS 共用視覺系統）

> 兩支影片皆為 **Type 02 教學影片**，共用同一套視覺規範（kit `specs/02-教學影片.md` 第 4 節）。
> 產出 agent：Claude Code。純 CSS/JS + Playwright + FFmpeg 管線（不用 HyperFrames CLI）。

---

## 核心字體

源石黑體 `GenSekiGothic2TW`（H 900 / B 700 / M 500），HTML `<style>` 內以 `@font-face`
指向本地 `assets/fonts/*.otf`（GOTCHAS C-5）。技術名詞（NIR / PCA / PLS / nm / R²）以
拉丁字母呈現，源石黑體本身含 Latin 字符，數字與英文一併使用。

| 字重 | 用途 |
|------|------|
| **H (900)** | 封面標題、章節大標、關鍵數字（68.9% / R²=0.96） |
| **B (700)** | 副標、章節編號、字幕 |
| **M (500)** | 內文、定義、註解 |

---

## 配色（kit 規範 4.3，教學版 — teal + coral 為主，gold 點綴；不用社群霓虹）

| HEX | 名稱 | 用途 |
|------|------|------|
| `#FAF7EE` | paper 米黃 | 內容頁背景 |
| `#F2EDDC` | paper-2 | 卡片底色、圖表襯底 |
| `#1A1A1A` | ink 墨黑 | 文字主色、封面 / 結語背景 |
| `#0E7C7B` | **teal** | 主強調：PCA 軸、PC1、訓練集、概念名詞 |
| `#E36414` | **coral** | 副強調：關鍵數字、測試集、轉折點、反轉 |
| `#C8941F` | gold | 第三色，僅用於微點綴（≤2 處 / 頁） |

> 所有 matplotlib 圖表（fig01–fig08）已用同一組色票輸出，影片與圖表色感一致。

---

## 字級階（1920×1080，kit 規範 4.2）

| Token | 大小 | 用途 |
|-------|------|------|
| `--fs-hero` | **200px** | 封面、結語金句、巨大強調數字 |
| `--fs-title` | **128px** | 頁面主標題 |
| `--fs-sub` | **84px** | 副標題、章節標題 |
| `--fs-body` | **52px** | 內文、定義 |
| `--fs-note` | **30px** | 註解、章節編號、字幕 |

行距 line-height 1.15–1.35。內容填滿 ≥ 80% 畫布（教學留白少）。

---

## 版面庫（教學用，相鄰頁不重複版面）

| 版面 | 名稱 | 用途 |
|------|------|------|
| **T0** | 純黑封面 / 結語 | 封面、金句、收尾（三明治結構） |
| **T1** | 大圖置中 + 標題列 | 展示 matplotlib 圖表（光譜、scree、分數圖…） |
| **T2** | 左圖右文 / 左文右圖 | 圖＋解說並列 |
| **T3** | SVG 概念動畫置中 | PCA 旋轉軸、PLS 共變異、知識地圖 |
| **T4** | 公式 + 說明（KaTeX） | X≈T·Pᵀ、cov(Xw,y) |
| **T5** | 卡片陣列 / 重點條列 | 「PCA 是 / 不是」、metrics 三條 |

---

## 必備 UI 元件（kit 規範 4.5）

- **章節 chip**（左上）：`teal` 底白字 `01 / 13 — 章節名`
- **進度條**（底部 5px，teal；可隨頁推進）
- **字幕條**（底部 30px，最大寬 88%，`rgba(26,26,26,0.92)` 圓角 10px，白字 30px / 700）
- **黑色封面 + 黑色結語**，內容頁淺色 paper

---

## ★ 關鍵動畫（每片 ≥ 3 個，動畫服務理解）

**PCA 片**
1. **點雲旋轉找軸**（T3）：散布點雲中，PC1 軸沿最大分散方向畫出、PC2 垂直彈出。
2. **Scree 長出 + 累積線繪製**（T1 疊圖）：bars 由低到高升起，coral 累積線 `stroke-dasharray` 繪到 99%。
3. **分數圖依脂肪上色**（T1 疊圖）：點先灰階出現，再由 teal→coral 依脂肪「染色」，凸顯自動排序。
4. **知識地圖輻射**（T3）：光譜 → 前處理 → PCA → 分數/負荷量/陡坡 中心輻射連線。

**PLS 片**
1. **PCA vs PLS 雙箭頭**（T3）：一箭頭追 X 分散方向，另一箭頭「轉向」貼近 y，示意共變異。
2. **RMSECV 曲線繪製 + 轉折點脈動**（T1 疊圖）：曲線左到右畫出，elbow 在第 4 點 coral 放大脈動。
3. **預測散點落到 1:1 線**（T1 疊圖）：點淡入後，對角 1:1 線繪出，點「貼線」。
4. **PCA↔PLS 知識地圖**（T3）：兩條路徑（探索 / 預測）匯整。

動畫節奏：單一動畫 0.5–1.5s、階層延遲 0.4–0.6s、動畫結束靜止 ≥ 1.5s 讓學生消化。

---

## 數學（KaTeX）

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"></script>
```

- PCA：$X \approx T P^{\top}$（分數×負荷量）、$\text{Var}(t_1)$ 最大
- PLS：$\max\ \text{cov}(Xw,\ y)$（潛在變量最大化共變異）

---

## 旁白與字幕

- **人聲**：Edge-TTS `zh-TW-YunJheNeural`，`rate -10% / pitch -2Hz`（kit 規範 7.1，教學語速）
- **文案**：第三人稱口語講解，每頁 1–4 句、讀完 8–22 秒；補充而非照念投影片
- **字幕**：單行 ≤ 25 字、不換行（GOTCHAS B-1）；技術名詞保留英文

---

## 已內建避坑（對應 GOTCHAS）

| 風險 | 措施 | 對應 |
|------|------|------|
| 渲染 crash | 純 CSS/JS + Playwright（Node 24 安全），不用 HF CLI | C-4 |
| 成品沒聲音 | ffmpeg mux 強制 `-map 0:v:0 -map 1:a:0` | E-2 |
| 字體不顯示 | HTML 內 `@font-face` 指向本地 .otf | C-5 |
| 開場殘留遮罩 | `?render=true` 自動播放、CSS 隱藏遮罩 | D-3 |
| 中文路徑 / node_modules | 渲染暫存與 node_modules 全在 `%TEMP%\cvs-render\` | D-1 / E-3 |
| Python 印中文崩潰 | 腳本強制 utf-8 stdout | F-1 |
| 音畫不同步 | index.html PAGES = render.py PAGES_TIMINGS = record 秒數 | PIPELINE |
