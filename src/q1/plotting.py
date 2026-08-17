from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


plt.rcParams.update({
    "figure.dpi": 140,
    "savefig.dpi": 300,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path)
    fig.savefig(path.with_suffix(".svg"))
    fig.savefig(path.with_suffix(".pdf"))
    plt.close(fig)


def heatmap(matrix: pd.DataFrame, path: Path, cmap: str = "viridis", vmin: float | None = None, vmax: float | None = None) -> None:
    fig_w = max(7, 0.35 * len(matrix.columns) + 3)
    fig_h = max(4, 0.35 * len(matrix.index) + 2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    masked = np.ma.masked_invalid(matrix.to_numpy(dtype=float))
    image = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    save_figure(fig, path)


def coverage_heatmap(coverage: pd.DataFrame, path: Path) -> None:
    heatmap(coverage, path, cmap="Greens", vmin=0, vmax=1)


def bar_with_ci(table: pd.DataFrame, path: Path) -> None:
    view = table.sort_values("overall_score")
    y = np.arange(len(view))
    low = view["overall_score"] - view["score_ci_low"]
    high = view["score_ci_high"] - view["overall_score"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(y, view["overall_score"], color="#4C78A8")
    ax.errorbar(view["overall_score"], y, xerr=[low, high], fmt="none", ecolor="#222222", capsize=3)
    ax.set_yticks(y)
    ax.set_yticklabels(view["model"], fontsize=8)
    ax.set_xlabel("Overall score")
    save_figure(fig, path)


def rank_stability(table: pd.DataFrame, path: Path) -> None:
    view = table.sort_values("median_rank", ascending=False)
    y = np.arange(len(view))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hlines(y, view["rank_ci_low"], view["rank_ci_high"], color="#6B7280", linewidth=3)
    ax.scatter(view["median_rank"], y, color="#D55E00", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(view["model"], fontsize=8)
    ax.set_xlabel("Rank interval")
    ax.invert_xaxis()
    save_figure(fig, path)


def score_visualization(dimension_scores: pd.DataFrame, dimensions: list[str], model_names: dict[str, str], path: Path) -> None:
    score_cols = [f"{d}_score" for d in dimensions]
    data = dimension_scores.set_index("model_id")[score_cols].rename(index=model_names)
    heatmap(data, path, cmap="YlGnBu", vmin=0, vmax=100)


def lofo_heatmap(table: pd.DataFrame, path: Path) -> None:
    pivot = table.pivot(index="model", columns="removed_family", values="delta_rank").fillna(0)
    heatmap(pivot, path, cmap="coolwarm")


def sensitivity_rank_plot(table: pd.DataFrame, path: Path) -> None:
    pivot = table.pivot(index="model", columns="scenario", values="rank")
    heatmap(pivot, path, cmap="magma_r")


def kimi_radar(kimi_row: pd.Series, median_scores: pd.Series, best_row: pd.Series, dimensions: list[str], path: Path) -> None:
    labels = [d.split(" ", 1)[0] for d in dimensions]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    def vals(source: pd.Series) -> list[float]:
        values = [float(source.get(f"{d}_score", np.nan)) for d in dimensions]
        values = [0.0 if not math.isfinite(v) else v for v in values]
        return values + values[:1]

    fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw={"polar": True})
    for source, label, color in [
        (kimi_row, "Kimi K3", "#D55E00"),
        (median_scores, "Median", "#6B7280"),
        (best_row, "Overall #1", "#0072B2"),
    ]:
        ax.plot(angles, vals(source), label=label, linewidth=2, color=color)
        ax.fill(angles, vals(source), alpha=0.08, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8)
    save_figure(fig, path)


def kimi_gap(gap_table: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = np.where(gap_table["gap_vs_median"] >= 0, "#2A9D8F", "#C44E52")
    ax.barh(gap_table["dimension"], gap_table["gap_vs_median"], color=colors)
    ax.axvline(0, color="#222222", linewidth=1)
    ax.set_xlabel("Kimi score minus median")
    save_figure(fig, path)

