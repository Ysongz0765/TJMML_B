"""Composable, guarded Q2 pipeline; intentionally not an executable script."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import ABILITY_COLUMNS, SCENES, equal_reference
from .data_adapter import Q1InputBundle, load_q1_input
from .imbalance_penalty import imbalance_penalty
from .kl_weights import KLWeightResult, solve_scene_weights
from .linear_baseline import linear_utility
from .marginal_analysis import (
    ces_inner_shares,
    ces_marginal_utility,
    ces_utility_elasticity,
)
from .missing_policy import MissingPolicyResult, apply_missing_policy, utility_intervals
from .normalize import normalise_abilities
from .rank_migration import build_rank_migration


@dataclass(frozen=True)
class Q2PipelineResult:
    mode: str
    metadata: dict[str, Any]
    missing_policy: str
    result_label: str
    ability_frame: pd.DataFrame
    scene_results: dict[str, pd.DataFrame]
    interval_results: dict[str, pd.DataFrame]
    weight_results: dict[str, KLWeightResult]
    scene_dimensions: dict[str, tuple[str, ...]]
    scene_rho: dict[str, float]
    rank_migration: pd.DataFrame | None


def _select_prior(bundle: Q1InputBundle, prior_kind: str) -> dict[str, float]:
    kind = prior_kind.lower()
    if kind == "q1":
        if bundle.objective_weights is None:
            raise ValueError("The Q1 prior was requested, but objective_weights are unavailable.")
        return bundle.objective_weights
    if kind == "equal":
        return equal_reference()
    raise ValueError("prior_kind must be 'q1' or 'equal'.")


def _scene_result(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
    scene: str,
    result_label: str,
) -> pd.DataFrame:
    values = frame[list(dimensions)].to_numpy(dtype=float)
    weight_vector = np.asarray([weights[d] for d in dimensions], dtype=float)
    utility = np.asarray(ces_utility(values, weight_vector, rho), dtype=float)
    linear = np.asarray(linear_utility(values, weight_vector), dtype=float)
    penalty, pri = imbalance_penalty(linear, utility)
    shares = ces_inner_shares(values, weight_vector, rho)
    marginal = ces_marginal_utility(values, weight_vector, rho)
    elasticity = ces_utility_elasticity(values, weight_vector, rho)
    output = pd.DataFrame(
        {
            "model": frame["model"].astype(str).to_numpy(),
            "scene": scene,
            "utility": utility,
            "linear_utility": linear,
            "imbalance_penalty": penalty,
            "pri": pri,
            "rho": float(rho),
            "result_label": result_label,
        }
    )
    output["rank"] = output["utility"].rank(method="min", ascending=False).astype(int)
    output["linear_rank"] = output["linear_utility"].rank(method="min", ascending=False).astype(int)
    output["rank_ces_minus_linear"] = output["rank"] - output["linear_rank"]
    for idx, dimension in enumerate(dimensions):
        output[f"inner_share_{dimension}"] = shares[:, idx]
        output[f"marginal_utility_{dimension}"] = marginal[:, idx]
        output[f"elasticity_{dimension}"] = elasticity[:, idx]
    return output.sort_values(["rank", "model"]).reset_index(drop=True)


def build_q2_pipeline(
    csv_path: str | Path,
    metadata_path: str | Path,
    *,
    mode: str = "DEVELOPMENT",
    missing_mode: str = "complete_case",
    prior_kind: str = "q1",
    alpha_overrides: dict[str, float] | None = None,
    rho_overrides: dict[str, float] | None = None,
) -> Q2PipelineResult:
    """Build scene results in memory after enforcing the Q1-freeze guard.

    No files are written.  Development mode accepts only explicitly marked
    anonymous mock data; final mode requires frozen Q1 metadata.
    """

    normalised_mode = mode.upper()
    bundle = load_q1_input(csv_path, metadata_path, normalised_mode)
    frame = normalise_abilities(bundle.frame, bundle.metadata["ability_scale"])
    policy: MissingPolicyResult = apply_missing_policy(
        frame, missing_mode, ABILITY_COLUMNS, bundle.metadata
    )
    prior = _select_prior(bundle, prior_kind)
    alpha_overrides = alpha_overrides or {}
    rho_overrides = rho_overrides or {}

    scene_results: dict[str, pd.DataFrame] = {}
    interval_results: dict[str, pd.DataFrame] = {}
    weight_results: dict[str, KLWeightResult] = {}
    scene_dimensions: dict[str, tuple[str, ...]] = {}
    scene_rho: dict[str, float] = {}
    for scene_key, scene in SCENES.items():
        dimensions = policy.dimensions
        alpha = alpha_overrides.get(scene_key, scene.alpha_development_default)
        rho = float(rho_overrides.get(scene_key, scene.rho_development_default))
        weight_result = solve_scene_weights(prior, scene, dimensions, alpha)
        weight_results[scene_key] = weight_result
        scene_dimensions[scene_key] = dimensions
        scene_rho[scene_key] = rho
        if missing_mode.lower() == "interval_propagation":
            interval = utility_intervals(
                policy.frame, dimensions, weight_result.weights, rho
            )
            interval["scene"] = scene_key
            interval["rho"] = rho
            interval["result_label"] = policy.label
            interval_results[scene_key] = interval
        else:
            scene_results[scene_key] = _scene_result(
                policy.frame,
                dimensions,
                weight_result.weights,
                rho,
                scene_key,
                policy.label,
            )

    migration = None
    if scene_results:
        q1_frame = policy.frame if "q1_overall_rank" in policy.frame.columns else None
        migration = build_rank_migration(scene_results, q1_frame)
    return Q2PipelineResult(
        mode=normalised_mode,
        metadata=bundle.metadata,
        missing_policy=missing_mode,
        result_label=policy.label,
        ability_frame=policy.frame,
        scene_results=scene_results,
        interval_results=interval_results,
        weight_results=weight_results,
        scene_dimensions=scene_dimensions,
        scene_rho=scene_rho,
        rank_migration=migration,
    )


def write_pipeline_tables(result: Q2PipelineResult, output_directory: str | Path) -> list[Path]:
    """Write tables only to the mode-appropriate protected Q2 directory."""

    output = Path(output_directory).resolve()
    normalised = str(output).replace("\\", "/").lower()
    if result.mode == "DEVELOPMENT":
        if "/outputs/q2/dev" not in normalised:
            raise PermissionError("Development results may only be written under outputs/q2/dev.")
        prefix = "MOCK_DATA_ONLY__"
    elif result.mode == "FINAL":
        if result.metadata.get("q1_finalized") is not True:
            raise PermissionError("Final output is blocked because Q1 is not finalized.")
        if "/outputs/q2/final" not in normalised:
            raise PermissionError("Final results may only be written under outputs/q2/final.")
        prefix = ""
    else:
        raise ValueError(f"Unsupported result mode {result.mode!r}.")

    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for scene, table in result.scene_results.items():
        path = output / f"{prefix}{scene}_results.csv"
        table.to_csv(path, index=False)
        written.append(path)
    for scene, table in result.interval_results.items():
        path = output / f"{prefix}{scene}_interval_results.csv"
        table.to_csv(path, index=False)
        written.append(path)
    if result.rank_migration is not None:
        path = output / f"{prefix}rank_migration.csv"
        result.rank_migration.to_csv(path, index=False)
        written.append(path)
    return written
