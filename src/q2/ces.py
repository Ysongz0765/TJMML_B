"""Constant-elasticity-of-substitution (CES) scene utility."""

from __future__ import annotations

import numpy as np

from .config import EPS


RHO_ZERO_TOLERANCE = 1e-7


def _validate_inputs(values: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if z.shape[-1] != w.shape[0]:
        raise ValueError("The final ability axis must match the weight vector.")
    if np.isnan(z).any():
        raise ValueError("CES cannot silently consume missing abilities; apply a missing-data policy first.")
    if np.any(z < 0.0) or np.any(z > 1.0):
        raise ValueError("CES expects abilities normalised to [0, 1].")
    if np.any(w < 0.0) or not np.isclose(w.sum(), 1.0, atol=1e-10):
        raise ValueError("CES weights must be non-negative and sum to one.")
    return z, w


def ces_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Evaluate CES utility along the final axis.

    The rho=0 branch uses the continuous weighted-geometric-mean limit.
    """

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return np.exp(np.sum(w * np.log(x), axis=-1))
    inner = np.sum(w * np.power(x, float(rho)), axis=-1)
    return np.power(inner, 1.0 / float(rho))


def substitution_elasticity(rho: float) -> float:
    """Return sigma=1/(1-rho); rho=1 corresponds to infinite elasticity."""

    if np.isclose(rho, 1.0):
        return float("inf")
    return 1.0 / (1.0 - float(rho))
