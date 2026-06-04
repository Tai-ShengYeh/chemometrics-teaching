# Chemometrics Teaching — NIR Food Analysis (PCA & PLS)

Teaching materials for **near-infrared (NIR) spectroscopy + chemometrics** in food
analysis, built around the public **Tecator** meat dataset. Includes a single-page
HTML course, runnable Python, an Orange Data Mining workflow, and narrated videos.

**▶ Live course page:** https://tai-shengyeh.github.io/chemometrics-teaching/

## 📚 Course series — Chemometrics × Food Analysis

Two sibling courses, same teaching pipeline (interactive page + Python + Orange + narrated videos):

| Course | Methods | Data | Live | Repo |
|--------|---------|------|------|------|
| **NIR spectroscopy (this repo)** | PCA + PLS (quantify) | Tecator meat | [page ↗](https://tai-shengyeh.github.io/chemometrics-teaching/) | this repo |
| Mass spectrometry | PCA + PLS-DA (classify) | White-wine GC-MS | [page ↗](https://tai-shengyeh.github.io/ms-food-analysis/) | [ms-food-analysis ↗](https://github.com/Tai-ShengYeh/ms-food-analysis) |

## Contents

| Path | What |
|------|------|
| `teaching.html` | Single-page course: NIR intro → dataset → **PCA** → **PLS** → Python code → Orange → summary |
| `python/` | Runnable analysis — `01_data_prep.py`, `02_pca.py`, `03_pls.py`, `04_sugar_pca.py` + `figures/` |
| `data/` | Tecator dataset (`tecator.csv`, `tecator_orange.tab`) |
| `orange/` | Orange Data Mining workflow (`nir_tecator_workflow.ows`) + illustrated guide |
| `videos/*/renders/*.mp4` | Narrated teaching videos — PCA, PLS, and PCA × Orange (sugar NIR) |

## Data & credits

- **Tecator** meat NIR dataset — public (StatLib / OpenML id 505).
- The PCA × Orange (five-sugar) video is adapted from **Yeh, T.-S.** *Open-Source Visual
  Programming Software for Introducing PCA to the Analytical Curriculum*,
  *J. Chem. Educ.* **2025**, *102*, 1428–1435.
- Figures generated with Python (scikit-learn / matplotlib). Videos built with a
  pure-CSS/JS + Playwright + FFmpeg pipeline. Font: 源石黑體 GenSeki (SIL OFL).

## Reproduce the analysis

```bash
pip install numpy pandas scipy scikit-learn matplotlib
cd python
python 01_data_prep.py   # data + raw/SNV spectra
python 02_pca.py         # scree / scores / loadings
python 03_pls.py         # LV selection / predicted-vs-measured / coefficients
```
