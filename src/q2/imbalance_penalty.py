"""Performance Imbalance Penalty Index (PRI)."""

from __future__ import annotations

import numpy as np


def imbalance_penalty(linear: np.ndarray, ces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return absolute penalty P=L-U and relative penalty PRI=(L-U)/L."""

    linear_values = np.asarray(linear, dtype=float)
    ces_values = np.asarray(ces, dtype=float)
    if linear_values.shape != ces_values.shape:
        raise ValueError("Linear and CES utility arrays must have the same shape.")
    penalty = linear_values - ces_values
    pri = np.divide(
        penalty,
        linear_values,
        out=np.full_like(penalty, np.nan, dtype=float),
        where=np.abs(linear_values) > 1e-15,
    )
    return penalty, pri
