"""Explicit missing-ability policies; no implicit zero filling is permitted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import ABILITY_COLUMNS, EPS


@dataclass(frozen=True)
class MissingPolicyResult:
    frame: pd.DataFrame
    dimensions: tuple[str, ...]
    label: str
    excluded_models: tuple[str, ...] = ()


def apply_missing_policy(
    frame: pd.DataFrame,
    mode: str,
    dimensions: tuple[str, ...] = ABILITY_COLUMNS,
    metadata: dict[str, Any] | None = None,
) -> MissingPolicyResult:
    """Apply complete-case, common-dimension, or inherited Q1 policy."""

    normalised_mode = mode.lower()
    if normalised_mode == "complete_case":
        mask = frame[list(dimensions)].notna().all(axis=1)
        excluded = tuple(frame.loc[~mask, "model"].astype(str))
        return MissingPolicyResult(
            frame=frame.loc[mask].copy().reset_index(drop=True),
            dimensions=dimensions,
            label="COMPLETE_CASE_RESULT",
            excluded_models=excluded,
        )
    if normalised_mode == "common_dimension":
        common = tuple(dimension for dimension in dimensions if frame[dimension].notna().all())
        if not common:
            raise ValueError("No ability dimension is jointly observed by all participating models.")
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=common,
            label="COMMON_DIMENSION_RESULT",
        )
    if normalised_mode == "q1_final_policy":
        metadata = metadata or {}
        if metadata.get("q1_missing_policy_applied") is not True:
            raise PermissionError(
                "q1_final_policy requires metadata.q1_missing_policy_applied=true."
            )
        if frame[list(dimensions)].isna().any().any():
            raise ValueError("Q1 final policy is declared, but the inherited ability matrix still contains NA.")
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=dimensions,
            label="Q1_FINAL_POLICY_RESULT",
        )
    if normalised_mode == "interval_propagation":
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=dimensions,
            label="INTERVAL_PROPAGATION_RESULT",
        )
    raise ValueError(
        "Unknown missing policy. Choose complete_case, common_dimension, "
        "interval_propagation, or q1_final_policy."
    )


def utility_intervals(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
    eps: float = EPS,
) -> pd.DataFrame:
    """Propagate monotone ability intervals through CES and bound possible ranks."""

    lower_rows: list[list[float]] = []
    upper_rows: list[list[float]] = []
    for _, row in frame.iterrows():
        lower_values: list[float] = []
        upper_values: list[float] = []
        for dimension in dimensions:
            value = row.get(dimension)
            lower = row.get(f"{dimension}_lower", np.nan)
            upper = row.get(f"{dimension}_upper", np.nan)
            if pd.notna(value):
                lower = value if pd.isna(lower) else lower
                upper = value if pd.isna(upper) else upper
            if pd.isna(lower) or pd.isna(upper):
                raise ValueError(
                    f"Model {row['model']!r} needs {dimension}_lower and {dimension}_upper "
                    "for interval propagation."
                )
            lower_float, upper_float = float(lower), float(upper)
            if not 0.0 <= lower_float <= upper_float <= 1.0:
                raise ValueError(f"Invalid interval [{lower_float}, {upper_float}] for {dimension}.")
            lower_values.append(lower_float)
            upper_values.append(upper_float)
        lower_rows.append(lower_values)
        upper_rows.append(upper_values)

    weight_vector = np.asarray([weights[d] for d in dimensions], dtype=float)
    lower_utility = np.asarray(ces_utility(np.asarray(lower_rows), weight_vector, rho, eps))
    upper_utility = np.asarray(ces_utility(np.asarray(upper_rows), weight_vector, rho, eps))
    output = pd.DataFrame(
        {
            "model": frame["model"].astype(str).to_numpy(),
            "utility_lower": lower_utility,
            "utility_upper": upper_utility,
        }
    )
    best_ranks: list[int] = []
    worst_ranks: list[int] = []
    for idx in range(len(output)):
        best_ranks.append(1 + int(np.sum(np.delete(lower_utility, idx) > upper_utility[idx])))
        worst_ranks.append(1 + int(np.sum(np.delete(upper_utility, idx) > lower_utility[idx])))
    output["best_possible_rank"] = best_ranks
    output["worst_possible_rank"] = worst_ranks
    return output
