"""One- and two-dimensional alpha/rho robustness analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import DEFAULT_ALPHA_GRID_SIZE, DEFAULT_RHO_GRID_SIZE, SceneConfig
from .kl_weights import solve_scene_weights


def parameter_grid(
    scene: SceneConfig,
    alpha_values: np.ndarray | None = None,
    rho_values: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    alpha = (
        np.linspace(*scene.alpha_range, DEFAULT_ALPHA_GRID_SIZE)
        if alpha_values is None
        else np.asarray(alpha_values, dtype=float)
    )
    rho = (
        np.linspace(*scene.rho_range, DEFAULT_RHO_GRID_SIZE)
        if rho_values is None
        else np.asarray(rho_values, dtype=float)
    )
    return alpha, rho


def run_sensitivity_grid(
    frame: pd.DataFrame,
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    prior: dict[str, float],
    alpha_values: np.ndarray | None = None,
    rho_values: np.ndarray | None = None,
) -> pd.DataFrame:
    """Evaluate Rank_i=f(alpha,rho) over a rectangular parameter grid."""

    alpha_grid, rho_grid = parameter_grid(scene, alpha_values, rho_values)
    values = frame[list(dimensions)].to_numpy(dtype=float)
    if np.isnan(values).any():
        raise ValueError("Sensitivity analysis requires an explicit missing-data policy first.")
    records: list[pd.DataFrame] = []
    for alpha in alpha_grid:
        weight_result = solve_scene_weights(prior, scene, dimensions, float(alpha))
        weights = np.asarray([weight_result.weights[d] for d in dimensions], dtype=float)
        for rho in rho_grid:
            utility = ces_utility(values, weights, float(rho))
            block = pd.DataFrame(
                {
                    "model": frame["model"].astype(str).to_numpy(),
                    "scene": scene.key,
                    "alpha": float(alpha),
                    "rho": float(rho),
                    "utility": utility,
                    "kl_divergence": weight_result.kl_divergence,
                }
            )
            block["rank"] = block["utility"].rank(method="min", ascending=False).astype(int)
            block["top3"] = block["rank"] <= 3
            records.append(block)
    return pd.concat(records, ignore_index=True)


def summarise_rank_robustness(grid: pd.DataFrame) -> pd.DataFrame:
    """Summarise average/best/worst rank, Top-3 share, variability and jumps."""

    required = {"model", "alpha", "rho", "rank", "top3"}
    if not required.issubset(grid.columns):
        raise ValueError(f"Sensitivity grid is missing columns: {sorted(required - set(grid.columns))}")
    ordered = grid.sort_values(["model", "rho", "alpha"])
    jump = ordered.groupby(["model", "rho"])["rank"].diff().abs().fillna(0)
    ordered = ordered.assign(rank_jump=jump)
    summary = (
        ordered.groupby("model", as_index=False)
        .agg(
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
            top3_share=("top3", "mean"),
            rank_std=("rank", "std"),
            maximum_adjacent_alpha_jump=("rank_jump", "max"),
        )
        .fillna({"rank_std": 0.0})
    )
    summary["has_rank_jump"] = summary["maximum_adjacent_alpha_jump"] > 0
    return summary.sort_values(["mean_rank", "model"]).reset_index(drop=True)


def detect_rank_jump_thresholds(grid: pd.DataFrame) -> pd.DataFrame:
    """Locate adjacent-alpha intervals where a model's rank changes at fixed rho."""

    required = {"model", "scene", "alpha", "rho", "rank"}
    if not required.issubset(grid.columns):
        raise ValueError(f"Sensitivity grid is missing columns: {sorted(required - set(grid.columns))}")
    records: list[dict[str, float | int | str]] = []
    ordered = grid.sort_values(["model", "rho", "alpha"])
    for (model, rho), group in ordered.groupby(["model", "rho"], sort=False):
        previous = None
        for row in group.itertuples(index=False):
            if previous is not None and int(row.rank) != int(previous.rank):
                records.append(
                    {
                        "model": str(model),
                        "scene": str(row.scene),
                        "rho": float(rho),
                        "alpha_from": float(previous.alpha),
                        "alpha_to": float(row.alpha),
                        "rank_from": int(previous.rank),
                        "rank_to": int(row.rank),
                        "rank_jump": int(row.rank) - int(previous.rank),
                    }
                )
            previous = row
    return pd.DataFrame(
        records,
        columns=[
            "model",
            "scene",
            "rho",
            "alpha_from",
            "alpha_to",
            "rank_from",
            "rank_to",
            "rank_jump",
        ],
    )


def compare_prior_robustness(
    q1_prior_grid: pd.DataFrame,
    equal_prior_grid: pd.DataFrame,
) -> pd.DataFrame:
    """Compare rank distributions under Q1-objective and equal reference priors."""

    q1_summary = summarise_rank_robustness(q1_prior_grid).add_suffix("_q1_prior")
    q1_summary = q1_summary.rename(columns={"model_q1_prior": "model"})
    equal_summary = summarise_rank_robustness(equal_prior_grid).add_suffix("_equal_prior")
    equal_summary = equal_summary.rename(columns={"model_equal_prior": "model"})
    comparison = q1_summary.merge(equal_summary, on="model", validate="one_to_one")
    comparison["mean_rank_prior_shift"] = (
        comparison["mean_rank_equal_prior"] - comparison["mean_rank_q1_prior"]
    )
    comparison["top3_share_prior_shift"] = (
        comparison["top3_share_equal_prior"] - comparison["top3_share_q1_prior"]
    )
    return comparison.sort_values(["mean_rank_q1_prior", "model"]).reset_index(drop=True)


def rank_surface(grid: pd.DataFrame, model: str) -> pd.DataFrame:
    """Return a rho-by-alpha rank surface suitable for heatmap plotting."""

    subset = grid[grid["model"] == model]
    if subset.empty:
        raise KeyError(f"Model {model!r} is absent from the sensitivity grid.")
    return subset.pivot(index="rho", columns="alpha", values="rank").sort_index(ascending=False)
