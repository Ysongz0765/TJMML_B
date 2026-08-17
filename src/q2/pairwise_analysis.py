"""Mechanism-oriented model comparison and target-model analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .imbalance_penalty import imbalance_penalty
from .linear_baseline import linear_utility
from .marginal_analysis import ces_inner_shares, ces_marginal_utility
from .rank_migration import identify_competitors


def compare_models(
    frame: pd.DataFrame,
    model_a: str,
    model_b: str,
    scene: str,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
) -> dict[str, Any]:
    """Explain a pairwise scene-utility gap without treating w_j z_j as CES contribution."""

    indexed = frame.set_index("model")
    missing = [model for model in (model_a, model_b) if model not in indexed.index]
    if missing:
        raise KeyError(f"Models absent from comparison frame: {missing}")
    z_a = indexed.loc[model_a, list(dimensions)].to_numpy(dtype=float)
    z_b = indexed.loc[model_b, list(dimensions)].to_numpy(dtype=float)
    w = np.asarray([weights[d] for d in dimensions], dtype=float)
    u_a, u_b = float(ces_utility(z_a, w, rho)), float(ces_utility(z_b, w, rho))
    l_a, l_b = float(linear_utility(z_a, w)), float(linear_utility(z_b, w))
    _, pri_a = imbalance_penalty(np.asarray([l_a]), np.asarray([u_a]))
    _, pri_b = imbalance_penalty(np.asarray([l_b]), np.asarray([u_b]))
    shares_a = ces_inner_shares(z_a, w, rho)
    shares_b = ces_inner_shares(z_b, w, rho)
    marginal_a = ces_marginal_utility(z_a, w, rho)
    marginal_b = ces_marginal_utility(z_b, w, rho)
    ability_gap = z_a - z_b
    weighted_effect = w * ability_gap
    return {
        "scene": scene,
        "model_a": model_a,
        "model_b": model_b,
        "utility_a": u_a,
        "utility_b": u_b,
        "utility_gap_a_minus_b": u_a - u_b,
        "linear_gap_a_minus_b": l_a - l_b,
        "ces_curvature_gap_effect": (u_a - u_b) - (l_a - l_b),
        "ability_difference": dict(zip(dimensions, ability_gap.tolist())),
        "weighted_ability_effect": dict(zip(dimensions, weighted_effect.tolist())),
        "ces_inner_share_a": dict(zip(dimensions, shares_a.tolist())),
        "ces_inner_share_b": dict(zip(dimensions, shares_b.tolist())),
        "marginal_utility_a": dict(zip(dimensions, marginal_a.tolist())),
        "marginal_utility_b": dict(zip(dimensions, marginal_b.tolist())),
        "priority_improvement_a": dimensions[int(np.argmax(marginal_a))],
        "priority_improvement_b": dimensions[int(np.argmax(marginal_b))],
        "pri_a": float(pri_a[0]),
        "pri_b": float(pri_b[0]),
        "larger_shortfall_penalty": model_a if pri_a[0] > pri_b[0] else model_b,
    }


def analyze_target_model(
    ability_frame: pd.DataFrame,
    scene_results: dict[str, pd.DataFrame],
    scene_weights: dict[str, dict[str, float]],
    scene_rho: dict[str, float],
    scene_dimensions: dict[str, tuple[str, ...]],
    model_name: str = "Kimi K3",
    rank_migration: pd.DataFrame | None = None,
    sensitivity_summary: dict[str, pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Assemble a result-driven target report after final data become available."""

    report: dict[str, Any] = {"model": model_name, "scenes": {}}
    for scene, result in scene_results.items():
        row = result.loc[result["model"] == model_name]
        if row.empty:
            report["scenes"][scene] = {"available": False}
            continue
        record = row.iloc[0]
        dimensions = scene_dimensions[scene]
        competitors = identify_competitors(result, model_name)
        comparisons = {}
        for role, competitor in competitors.items():
            if competitor is not None and competitor != model_name:
                comparisons[role] = compare_models(
                    ability_frame,
                    model_name,
                    competitor,
                    scene,
                    dimensions,
                    scene_weights[scene],
                    scene_rho[scene],
                )
        report["scenes"][scene] = {
            "available": True,
            "rank": int(record["rank"]),
            "utility": float(record["utility"]),
            "pri": float(record["pri"]),
            "rho": float(scene_rho[scene]),
            "ces_inner_shares": {
                dimension: float(record[f"inner_share_{dimension}"])
                for dimension in dimensions
            },
            "marginal_utilities": {
                dimension: float(record[f"marginal_utility_{dimension}"])
                for dimension in dimensions
            },
            "utility_elasticities": {
                dimension: float(record[f"elasticity_{dimension}"])
                for dimension in dimensions
            },
            "priority_improvement": max(
                dimensions,
                key=lambda dimension: float(record[f"marginal_utility_{dimension}"]),
            ),
            "competitors": competitors,
            "comparisons": comparisons,
        }
        if sensitivity_summary and scene in sensitivity_summary:
            summary_row = sensitivity_summary[scene]
            summary_row = summary_row[summary_row["model"] == target_model]
            if not summary_row.empty:
                report["scenes"][scene]["sensitivity"] = summary_row.iloc[0].to_dict()
    if rank_migration is not None:
        migration = rank_migration[rank_migration["model"] == model_name]
        report["rank_migration"] = None if migration.empty else migration.iloc[0].to_dict()
    return report
