"""Stable Q1-to-Q2 data contract and finalisation guard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import ABILITY_COLUMNS


AVAILABILITY_COLUMNS = tuple(f"{dimension}_available" for dimension in ABILITY_COLUMNS)
REQUIRED_COLUMNS = ("model", *ABILITY_COLUMNS, *AVAILABILITY_COLUMNS)
OPTIONAL_COLUMNS = (
    "q1_overall_score",
    "q1_overall_rank",
    *(f"{dimension}_{bound}" for dimension in ABILITY_COLUMNS for bound in ("lower", "upper")),
)


@dataclass(frozen=True)
class Q1InputBundle:
    frame: pd.DataFrame
    metadata: dict[str, Any]
    objective_weights: dict[str, float] | None
    source_path: Path


def _coerce_bool(series: pd.Series, column: str) -> pd.Series:
    true_values = {True, 1, "1", "true", "t", "yes", "y"}
    false_values = {False, 0, "0", "false", "f", "no", "n"}

    def convert(value: Any) -> bool:
        if pd.isna(value):
            raise ValueError(f"Availability column {column!r} contains a missing flag.")
        normalised = value.strip().lower() if isinstance(value, str) else value
        if normalised in true_values:
            return True
        if normalised in false_values:
            return False
        raise ValueError(f"Invalid boolean value {value!r} in {column!r}.")

    return series.map(convert).astype(bool)


def _validate_metadata(metadata: dict[str, Any], mode: str) -> None:
    scale = metadata.get("ability_scale")
    if scale not in {"0-100", "0-1"}:
        raise ValueError("metadata.ability_scale must be either '0-100' or '0-1'.")
    normalised_mode = mode.upper()
    if normalised_mode not in {"DEVELOPMENT", "FINAL"}:
        raise ValueError("mode must be DEVELOPMENT or FINAL.")
    if normalised_mode == "FINAL":
        required = {
            "q1_finalized": metadata.get("q1_finalized") is True,
            "q1_freeze_version": bool(metadata.get("q1_freeze_version")),
            "q1_freeze_date": bool(metadata.get("q1_freeze_date")),
            "objective_weights_available": metadata.get("objective_weights_available") is True,
        }
        missing = [field for field, valid in required.items() if not valid]
        if missing:
            raise PermissionError(
                "FINAL mode is blocked until Q1 is frozen. Missing/invalid metadata: "
                + ", ".join(missing)
            )


def _read_objective_weights(metadata: dict[str, Any]) -> dict[str, float] | None:
    raw = metadata.get("objective_weights")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("metadata.objective_weights must be an object keyed by C1...C5.")
    missing = [dimension for dimension in ABILITY_COLUMNS if dimension not in raw]
    if missing:
        raise ValueError(f"Objective weights are missing: {missing}")
    weights = {dimension: float(raw[dimension]) for dimension in ABILITY_COLUMNS}
    values = np.asarray(list(weights.values()), dtype=float)
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("Objective weights must be finite and strictly positive for KL projection.")
    return {dimension: value / float(values.sum()) for dimension, value in weights.items()}


def load_q1_input(
    csv_path: str | Path,
    metadata_path: str | Path,
    mode: str = "DEVELOPMENT",
) -> Q1InputBundle:
    """Load and validate the standard Q1 output without importing Q1 code."""

    csv_file = Path(csv_path)
    metadata_file = Path(metadata_path)
    with metadata_file.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    _validate_metadata(metadata, mode)

    frame = pd.read_csv(csv_file)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Q1 input is missing required columns: {missing_columns}")
    if frame.empty:
        raise ValueError("Q1 input contains no model rows.")
    if frame["model"].isna().any() or frame["model"].astype(str).str.strip().eq("").any():
        raise ValueError("Every row must have a non-empty model name.")
    if frame["model"].duplicated().any():
        duplicated = frame.loc[frame["model"].duplicated(), "model"].tolist()
        raise ValueError(f"Model names must be unique; duplicates: {duplicated}")

    for column in AVAILABILITY_COLUMNS:
        frame[column] = _coerce_bool(frame[column], column)
    numeric_columns = [column for column in (*ABILITY_COLUMNS, *OPTIONAL_COLUMNS) if column in frame.columns]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    for dimension in ABILITY_COLUMNS:
        available = frame[f"{dimension}_available"]
        if frame.loc[available, dimension].isna().any():
            bad_models = frame.loc[available & frame[dimension].isna(), "model"].tolist()
            raise ValueError(
                f"{dimension} is marked available but missing for models: {bad_models}"
            )
        # An unavailable score is never allowed to leak into Q2 as an observed value.
        frame.loc[~available, dimension] = np.nan

    if mode.upper() == "DEVELOPMENT":
        if "MOCK_DATA_ONLY" not in frame.columns:
            raise PermissionError(
                "DEVELOPMENT inputs must contain MOCK_DATA_ONLY=TRUE to prevent use of Q1 half-products."
            )
        mock_flags = _coerce_bool(frame["MOCK_DATA_ONLY"], "MOCK_DATA_ONLY")
        if not bool(mock_flags.all()) or metadata.get("mock_data_only") is not True:
            raise PermissionError("Development execution is restricted to explicitly marked mock data.")
        frame["MOCK_DATA_ONLY"] = mock_flags

    objective_weights = _read_objective_weights(metadata)
    if mode.upper() == "FINAL" and objective_weights is None:
        raise PermissionError("FINAL mode requires Q1 objective weights.")
    return Q1InputBundle(frame=frame, metadata=metadata, objective_weights=objective_weights, source_path=csv_file)
