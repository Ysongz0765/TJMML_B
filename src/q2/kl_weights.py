"""Minimum-information-shift scenario weighting via KL projection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import xlogy

from .config import OPTIMIZER_TOLERANCE, SceneConfig
from .scene_constraints import (
    ActiveSceneConstraints,
    activate_constraints,
    constraint_diagnostics,
    find_feasible_weights,
    scipy_inequality_constraints,
)


@dataclass(frozen=True)
class KLWeightResult:
    scene: str
    dimensions: tuple[str, ...]
    weights: dict[str, float]
    prior: dict[str, float]
    alpha: float
    kl_divergence: float
    success: bool
    message: str
    diagnostics: dict[str, float | bool]


def _normalise_prior(prior: dict[str, float], dimensions: tuple[str, ...]) -> np.ndarray:
    try:
        values = np.asarray([prior[dimension] for dimension in dimensions], dtype=float)
    except KeyError as exc:
        raise ValueError(f"Prior is missing ability dimension {exc.args[0]!r}.") from exc
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("KL prior weights must be finite and strictly positive.")
    return values / values.sum()


def kl_divergence(weights: np.ndarray, prior: np.ndarray) -> float:
    """Compute D_KL(weights || prior), using the 0 log 0 convention."""

    w = np.asarray(weights, dtype=float)
    p = np.asarray(prior, dtype=float)
    return float(np.sum(xlogy(w, w / p)))


def solve_scene_weights(
    prior: dict[str, float],
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    alpha: float | None = None,
) -> KLWeightResult:
    """Project a neutral prior onto a scene's feasible demand set."""

    active: ActiveSceneConstraints = activate_constraints(scene, dimensions, alpha)
    p = _normalise_prior(prior, dimensions)
    feasible = find_feasible_weights(active)
    start = 0.5 * p + 0.5 * feasible
    constraints = [
        {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)},
        *scipy_inequality_constraints(active),
    ]
    result = minimize(
        fun=lambda w: kl_divergence(w, p),
        x0=start,
        method="SLSQP",
        bounds=[(0.0, 1.0) for _ in dimensions],
        constraints=constraints,
        options={"ftol": OPTIMIZER_TOLERANCE, "maxiter": 2000, "disp": False},
    )
    diagnostics = constraint_diagnostics(result.x, active)
    success = bool(result.success and diagnostics["feasible"])
    if not success:
        raise RuntimeError(
            f"KL projection failed for scene {scene.key}: {result.message}; "
            f"diagnostics={diagnostics}"
        )
    weights = {dimension: float(result.x[idx]) for idx, dimension in enumerate(dimensions)}
    prior_out = {dimension: float(p[idx]) for idx, dimension in enumerate(dimensions)}
    return KLWeightResult(
        scene=scene.key,
        dimensions=dimensions,
        weights=weights,
        prior=prior_out,
        alpha=active.alpha,
        kl_divergence=kl_divergence(result.x, p),
        success=success,
        message=str(result.message),
        diagnostics=diagnostics,
    )
