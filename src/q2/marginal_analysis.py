"""Nonlinear CES interpretation by inner shares and marginal utility."""

from __future__ import annotations

import numpy as np

from .ces import RHO_ZERO_TOLERANCE, _validate_inputs, ces_utility
from .config import EPS


def ces_inner_shares(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Return q_j = w_j x_j^rho / sum_k w_k x_k^rho."""

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return np.broadcast_to(w, z.shape).copy()
    numerator = w * np.power(x, float(rho))
    return numerator / np.sum(numerator, axis=-1, keepdims=True)


def ces_marginal_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Analytic derivative dU/dz_j for the CES aggregator."""

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    utility = np.expand_dims(ces_utility(z, w, rho, eps), axis=-1)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return utility * w / x
    return w * np.power(x, float(rho) - 1.0) * np.power(utility, 1.0 - float(rho))


def ces_utility_elasticity(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Return E_j=(dU/dz_j)(z_j/U), using the unshifted normalised z_j."""

    z, w = _validate_inputs(values, weights)
    utility = np.expand_dims(ces_utility(z, w, rho, eps), axis=-1)
    marginal = ces_marginal_utility(z, w, rho, eps)
    return marginal * z / utility


def numerical_marginal_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    step: float = 1e-6,
    eps: float = EPS,
) -> np.ndarray:
    """Central/one-sided finite differences for derivative verification."""

    z, w = _validate_inputs(values, weights)
    flat = np.atleast_2d(z).astype(float)
    derivatives = np.empty_like(flat)
    for row_idx, row in enumerate(flat):
        for col_idx in range(row.size):
            lower = row.copy()
            upper = row.copy()
            lower[col_idx] = max(0.0, lower[col_idx] - step)
            upper[col_idx] = min(1.0, upper[col_idx] + step)
            width = upper[col_idx] - lower[col_idx]
            derivatives[row_idx, col_idx] = (
                float(ces_utility(upper, w, rho, eps))
                - float(ces_utility(lower, w, rho, eps))
            ) / width
    return derivatives[0] if z.ndim == 1 else derivatives
