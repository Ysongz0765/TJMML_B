"""Plot frameworks for rank migration and two-dimensional robustness."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_rank_migration(
    migration: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str = "Ranking Migration Across Scenarios",
):
    """Draw a bump chart; Q1 baseline is optional."""

    rank_columns = [column for column in migration.columns if column.startswith("rank_")]
    if len(rank_columns) < 2:
        raise ValueError("A rank migration plot needs at least two rank columns.")
    labels = [column.removeprefix("rank_") for column in rank_columns]
    x = np.arange(len(rank_columns))
    fig, ax = plt.subplots(figsize=(max(7, 1.8 * len(rank_columns)), 5.5))
    for _, row in migration.dropna(subset=rank_columns).iterrows():
        y = row[rank_columns].to_numpy(dtype=float)
        ax.plot(x, y, marker="o", linewidth=1.5, alpha=0.8)
        ax.text(x[-1] + 0.04, y[-1], str(row["model"]), va="center", fontsize=8)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Rank (1 = best)")
    ax.set_title(title)
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")
    return fig, ax


def plot_rank_surface(
    surface: pd.DataFrame,
    model: str,
    scene: str,
    output_path: str | Path | None = None,
):
    """Plot rank over the (alpha,rho) sensitivity grid."""

    fig, ax = plt.subplots(figsize=(7, 5))
    image = ax.imshow(surface.to_numpy(dtype=float), aspect="auto", cmap="viridis_r")
    ax.set_xticks(np.arange(surface.shape[1]), [f"{value:.3g}" for value in surface.columns], rotation=45)
    ax.set_yticks(np.arange(surface.shape[0]), [f"{value:.3g}" for value in surface.index])
    ax.set_xlabel("alpha")
    ax.set_ylabel("rho")
    ax.set_title(f"Rank Robustness: {model} / {scene}")
    fig.colorbar(image, ax=ax, label="Rank")
    fig.tight_layout()
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")
    return fig, ax
