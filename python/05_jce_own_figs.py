# -*- coding: utf-8 -*-
"""
05_jce_own_figs.py — ORIGINAL replacements for the 2 published-paper images in the JCE video:
  orange_workflow.png  my own Orange-workflow diagram (replaces paper Fig 1 screenshot)
  questionnaire.png    my own bar chart of the reported survey means (replaces paper Fig 6)
Output -> python/figures/jce/ ; caller copies into both pca-orange* video asset folders.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from nir_utils import house_style, PALETTE, FIG

house_style()
OUT = os.path.join(FIG, "jce"); os.makedirs(OUT, exist_ok=True)
P = PALETTE

# ---------- orange_workflow.png : own widget-flow diagram ----------
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
def widget(cx, cy, label, sub, face, edge):
    ax.add_patch(FancyBboxPatch((cx - 0.95, cy - 0.62), 1.9, 1.24, boxstyle="round,pad=0.08,rounding_size=0.18",
                                fc=face, ec=edge, lw=2.5))
    ax.text(cx, cy + 0.12, label, ha="center", va="center", fontsize=18, fontweight="bold", color=P["ink"])
    ax.text(cx, cy - 0.34, sub, ha="center", va="center", fontsize=12, color="#6a5f4e")
def arrow(x1, x2, y1=2.6, y2=2.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22,
                                 lw=2.6, color=P["teal"]))
widget(1.4, 2.6, "File", "load data", "#FBE9D6", P["coral"])
widget(4.0, 2.6, "Preprocess", "SNV / cut / SG", "#F4E6C5", P["gold"])
widget(6.6, 2.6, "PCA", "decompose", "#D7ECEB", P["teal"])
widget(9.3, 4.1, "Scatter Plot", "score plot", "#FBE9D6", P["coral"])
widget(9.3, 1.1, "Scatter Plot", "loading plot", "#FBE9D6", P["coral"])
arrow(2.35, 3.05); arrow(4.95, 5.65)
ax.add_patch(FancyArrowPatch((7.55, 2.9), (8.35, 4.0), arrowstyle="-|>", mutation_scale=22, lw=2.6, color=P["teal"]))
ax.add_patch(FancyArrowPatch((7.55, 2.3), (8.35, 1.2), arrowstyle="-|>", mutation_scale=22, lw=2.6, color=P["teal"]))
ax.text(5.5, 4.9, "Orange visual-programming workflow (illustration)", ha="center", fontsize=19, fontweight="bold", color=P["ink"])
ax.text(5.5, 0.2, "drag widgets onto the canvas, connect with links — no code", ha="center", fontsize=13, color="#6a5f4e", style="italic")
fig.savefig(os.path.join(OUT, "orange_workflow.png"), bbox_inches="tight"); plt.close(fig)
print("orange_workflow.png ok")

# ---------- questionnaire.png : own bar chart of reported survey means ----------
means = [3.58, 3.25, 3.67, 2.83, 3.67, 4.17]
sds   = [0.79, 0.45, 0.49, 1.03, 0.78, 0.58]
labels = ["Q1\nunderstand", "Q2\nease of use", "Q3\nlearning", "Q4\nengagement", "Q5\nvisualization", "Q6\nsatisfaction"]
xpos = np.arange(6)
colors = [P["teal"] if m >= 3 else P["coral"] for m in means]
fig, ax = plt.subplots(figsize=(10, 6.0))
ax.bar(xpos, means, yerr=sds, color=colors, edgecolor=P["ink"], linewidth=.6,
       capsize=6, error_kw=dict(ecolor="#6a5f4e", lw=1.6))
ax.axhline(3, color=P["gold"], ls="--", lw=1.6); ax.text(5.4, 3.06, "neutral (3)", color=P["gold"], fontsize=12, fontweight="bold")
for i, m in enumerate(means):
    ax.text(i, m + sds[i] + 0.08, f"{m:.2f}", ha="center", fontsize=13, fontweight="bold", color=P["ink"])
ax.set_xticks(xpos, labels, fontsize=12); ax.set_ylim(0, 5); ax.set_ylabel("Mean Likert score (1–5)")
ax.set_title("Student survey — mean response (n=12, reported means)")
ax.grid(axis="x", alpha=0)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "questionnaire.png")); plt.close(fig)
print("questionnaire.png ok ->", OUT)
