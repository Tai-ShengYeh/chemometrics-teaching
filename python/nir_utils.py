# -*- coding: utf-8 -*-
"""
nir_utils.py — shared helpers for the NIR / Tecator teaching project.

Functions:
  load_tecator()  -> (wl, X, y_df)   raw absorbance matrix + reference values
  snv(X)          -> SNV-normalised spectra (scatter correction)
  savgol_d(X,...) -> Savitzky-Golay derivative spectra
  house_style()   -> apply the teaching-video colour palette to matplotlib
  PALETTE, CMAP   -> brand colours + teal->coral continuous colormap

Dataset: Tecator (Infratec Food & Feed Analyzer), 240 meat samples,
100 NIR absorbance channels over 850-1050 nm, with reference moisture/fat/protein
(% w/w) measured by wet chemistry. Public domain (StatLib / OpenML id 505).
"""
import sys, os
import numpy as np
import pandas as pd

# force utf-8 stdout on Windows (GOTCHAS F-1)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
FIG  = os.path.join(HERE, "figures")
os.makedirs(DATA, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# Tecator channels span 850-1050 nm, 100 evenly spaced points
WAVELENGTHS = np.linspace(850, 1050, 100)

# ---- brand palette (matches DESIGN.md / kit spec 02 section 4.3) ----
PALETTE = {
    "paper":  "#FAF7EE",
    "paper2": "#F2EDDC",
    "ink":    "#1A1A1A",
    "teal":   "#0E7C7B",
    "coral":  "#E36414",
    "gold":   "#C8941F",
    "grid":   "#D9D2BE",
}


def load_tecator():
    """Return (wl, X, y_df). X is (n,100) absorbance, y_df has moisture/fat/protein."""
    raw = os.path.join(DATA, "_tecator_openml_raw.csv")
    if os.path.exists(raw):
        df = pd.read_csv(raw)
    else:
        from sklearn.datasets import fetch_openml
        d = fetch_openml("tecator", version=1, as_frame=True, parser="auto")
        df = d.frame
        df.to_csv(raw, index=False)
    abs_cols = [c for c in df.columns if c.startswith("absorbance_")]
    abs_cols = sorted(abs_cols, key=lambda c: int(c.split("_")[1]))
    X = df[abs_cols].to_numpy(dtype=float)
    y = df[["moisture", "fat", "protein"]].astype(float).reset_index(drop=True)
    return WAVELENGTHS, X, y


def snv(X):
    """Standard Normal Variate: row-wise scatter correction."""
    X = np.asarray(X, dtype=float)
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True)
    return (X - mu) / sd


def savgol_d(X, window=15, poly=2, deriv=1):
    """Savitzky-Golay smoothing derivative along the wavelength axis."""
    from scipy.signal import savgol_filter
    return savgol_filter(X, window_length=window, polyorder=poly,
                         deriv=deriv, axis=1)


def house_style():
    """Apply the teaching palette + large fonts (figures are shown at 1080p)."""
    import matplotlib as mpl
    from matplotlib.colors import LinearSegmentedColormap
    mpl.rcParams.update({
        "figure.facecolor":  PALETTE["paper"],
        "axes.facecolor":    PALETTE["paper"],
        "savefig.facecolor": PALETTE["paper"],
        "axes.edgecolor":    PALETTE["ink"],
        "axes.labelcolor":   PALETTE["ink"],
        "text.color":        PALETTE["ink"],
        "xtick.color":       PALETTE["ink"],
        "ytick.color":       PALETTE["ink"],
        "axes.linewidth":    1.4,
        "font.size":         17,
        "axes.titlesize":    21,
        "axes.labelsize":    18,
        "legend.fontsize":   15,
        "figure.dpi":        150,
        "axes.grid":         True,
        "grid.color":        PALETTE["grid"],
        "grid.linewidth":    0.9,
        "font.family":       "DejaVu Sans",
    })
    # teal -> gold -> coral continuous colormap for "colour by property"
    return LinearSegmentedColormap.from_list(
        "tealcoral", [PALETTE["teal"], "#5BA89A", PALETTE["gold"], PALETTE["coral"]])


CMAP = None  # set by house_style() callers if needed
