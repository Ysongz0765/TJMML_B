"""Ability scaling for Q2, preserving missing values exactly."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ABILITY_COLUMNS


def normalise_abilities(
    frame: pd.DataFrame,
    ability_scale: str,
    dimensions: tuple[str, ...] = ABILITY_COLUMNS,
) -> pd.DataFrame:
    """Return a copy with ability scores on [0,1]; NaN remains NaN."""

    if ability_scale not in {"0-100", "0-1"}:
        raise ValueError("ability_scale must be '0-100' or '0-1'.")
    result = frame.copy()
    factor = 100.0 if ability_scale == "0-100" else 1.0
    for dimension in dimensions:
        numeric = pd.to_numeric(result[dimension], errors="coerce")
        observed = numeric.dropna()
        upper = 100.0 if ability_scale == "0-100" else 1.0
        if ((observed < 0.0) | (observed > upper)).any():
            raise ValueError(f"{dimension} contains values outside the declared {ability_scale} scale.")
        result[dimension] = numeric / factor
        for bound in ("lower", "upper"):
            column = f"{dimension}_{bound}"
            if column in result.columns:
                interval = pd.to_numeric(result[column], errors="coerce")
                observed_interval = interval.dropna()
                if ((observed_interval < 0.0) | (observed_interval > upper)).any():
                    raise ValueError(f"{column} lies outside the declared {ability_scale} scale.")
                result[column] = interval / factor
    return result
