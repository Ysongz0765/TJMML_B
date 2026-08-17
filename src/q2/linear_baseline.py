"""Fully compensatory linear baseline used only for comparison."""

from __future__ import annotations

import numpy as np


def linear_utility(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    z = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if z.shape[-1] != w.shape[0]:
        raise ValueError("The final ability axis must match the weight vector.")
    if np.isnan(z).any():
        raise ValueError("Linear utility cannot silently consume missing abilities.")
    if np.any(w < 0.0) or not np.isclose(w.sum(), 1.0, atol=1e-10):
        raise ValueError("Weights must be non-negative and sum to one.")
    return np.sum(z * w, axis=-1)
