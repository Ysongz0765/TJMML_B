"""Construction and validation of parameterised scene constraints."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from .config import CONSTRAINT_TOLERANCE, SceneConfig


@dataclass(frozen=True)
class ActiveSceneConstraints:
    scene: str
    dimensions: tuple[str, ...]
    alpha: float
    core_dimensions: tuple[str, ...]
    lower_bounds: tuple[tuple[str, float], ...]
    order_constraints: tuple[tuple[str, str], ...]


def activate_constraints(
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    alpha: float | None = None,
) -> ActiveSceneConstraints:
    """Restrict a scene demand system to currently available dimensions.

    This is essential for ``common_dimension`` analysis.  Constraints that
    reference an unavailable dimension are removed, while the core-mass
    threshold remains attached to the surviving core dimensions.
    """

    if len(set(dimensions)) != len(dimensions):
        raise ValueError("Ability dimensions must be unique.")
    chosen_alpha = scene.alpha_development_default if alpha is None else float(alpha)
    if not 0.0 <= chosen_alpha <= 1.0:
        raise ValueError("alpha must lie in [0, 1].")
    core = tuple(d for d in scene.core_dimensions if d in dimensions)
    if not core:
        raise ValueError(f"Scene {scene.key!r} has no core dimension in the active data.")
    lower = tuple((d, value) for d, value in scene.lower_bounds if d in dimensions)
    orders = tuple(
        (higher, lower_dim)
        for higher, lower_dim in scene.order_constraints
        if higher in dimensions and lower_dim in dimensions
    )
    return ActiveSceneConstraints(
        scene=scene.key,
        dimensions=dimensions,
        alpha=chosen_alpha,
        core_dimensions=core,
        lower_bounds=lower,
        order_constraints=orders,
    )


def scipy_inequality_constraints(active: ActiveSceneConstraints) -> list[dict]:
    """Translate the active system to SLSQP constraints ``fun(w) >= 0``."""

    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    constraints: list[dict] = []
    core_idx = np.array([index[d] for d in active.core_dimensions], dtype=int)
    constraints.append(
        {"type": "ineq", "fun": lambda w, idx=core_idx, a=active.alpha: float(np.sum(w[idx]) - a)}
    )
    for dimension, lower in active.lower_bounds:
        idx = index[dimension]
        constraints.append(
            {"type": "ineq", "fun": lambda w, i=idx, bound=lower: float(w[i] - bound)}
        )
    for higher, lower_dim in active.order_constraints:
        high_idx, low_idx = index[higher], index[lower_dim]
        constraints.append(
            {"type": "ineq", "fun": lambda w, hi=high_idx, lo=low_idx: float(w[hi] - w[lo])}
        )
    return constraints


def find_feasible_weights(active: ActiveSceneConstraints) -> np.ndarray:
    """Find a feasible simplex point with linear programming."""

    n = len(active.dimensions)
    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []

    core_row = np.zeros(n)
    for dimension in active.core_dimensions:
        core_row[index[dimension]] = -1.0
    a_ub.append(core_row)
    b_ub.append(-active.alpha)

    for higher, lower_dim in active.order_constraints:
        row = np.zeros(n)
        row[index[higher]] = -1.0
        row[index[lower_dim]] = 1.0
        a_ub.append(row)
        b_ub.append(0.0)

    bounds = [(0.0, 1.0) for _ in range(n)]
    for dimension, lower in active.lower_bounds:
        bounds[index[dimension]] = (lower, 1.0)

    result = linprog(
        c=np.zeros(n),
        A_ub=np.vstack(a_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.ones((1, n)),
        b_eq=np.ones(1),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        raise ValueError(f"Infeasible constraints for scene {active.scene}: {result.message}")
    return np.asarray(result.x, dtype=float)


def constraint_diagnostics(
    weights: np.ndarray,
    active: ActiveSceneConstraints,
    tolerance: float = CONSTRAINT_TOLERANCE,
) -> dict[str, float | bool]:
    """Report simplex and scene-demand residuals."""

    values = np.asarray(weights, dtype=float)
    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    diagnostics: dict[str, float | bool] = {
        "weight_sum": float(values.sum()),
        "minimum_weight": float(values.min()),
        "core_mass": float(sum(values[index[d]] for d in active.core_dimensions)),
    }
    residuals = [diagnostics["core_mass"] - active.alpha]
    for dimension, lower in active.lower_bounds:
        residuals.append(float(values[index[dimension]] - lower))
    for higher, lower_dim in active.order_constraints:
        residuals.append(float(values[index[higher]] - values[index[lower_dim]]))
    diagnostics["minimum_constraint_residual"] = float(min(residuals))
    diagnostics["feasible"] = bool(
        abs(float(values.sum()) - 1.0) <= tolerance
        and float(values.min()) >= -tolerance
        and min(residuals) >= -tolerance
    )
    return diagnostics
