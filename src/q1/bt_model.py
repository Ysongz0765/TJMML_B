from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, log_expit


def separation_warning(pairwise: pd.DataFrame, models: list[str]) -> bool:
    if pairwise.empty:
        return False
    wins = {m: 0.0 for m in models}
    losses = {m: 0.0 for m in models}
    for row in pairwise.itertuples(index=False):
        if row.y > 0.5:
            wins[row.model_i] += row.weight
            losses[row.model_j] += row.weight
        elif row.y < 0.5:
            wins[row.model_j] += row.weight
            losses[row.model_i] += row.weight
    active = [m for m in models if wins[m] + losses[m] > 0]
    return any((wins[m] == 0.0 or losses[m] == 0.0) for m in active)


def fit_bt(pairwise: pd.DataFrame, models: list[str], lambda_: float = 1.0) -> dict[str, object]:
    active = sorted(set(pairwise["model_i"]).union(set(pairwise["model_j"])), key=models.index) if len(pairwise) else []
    if len(active) < 2:
        return {
            "theta": {m: np.nan for m in models},
            "converged": False,
            "message": "Fewer than two active models",
            "n_iter": 0,
            "objective": np.nan,
            "separation_warning": False,
        }
    index = {m: i for i, m in enumerate(active)}
    i_idx = pairwise["model_i"].map(index).to_numpy()
    j_idx = pairwise["model_j"].map(index).to_numpy()
    y = pairwise["y"].astype(float).to_numpy()
    w = pairwise["weight"].astype(float).to_numpy()
    n = len(active)

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        delta = theta[i_idx] - theta[j_idx]
        p = expit(delta)
        # -[y log(sigmoid(delta)) + (1-y) log(sigmoid(-delta))]
        nll = -np.sum(w * (y * log_expit(delta) + (1.0 - y) * log_expit(-delta)))
        nll += 0.5 * lambda_ * float(np.dot(theta, theta))
        grad = np.zeros(n)
        g = w * (p - y)
        np.add.at(grad, i_idx, g)
        np.add.at(grad, j_idx, -g)
        grad += lambda_ * theta
        return float(nll), grad

    result = minimize(lambda t: objective(t), np.zeros(n), jac=True, method="L-BFGS-B", options={"maxiter": 500})
    theta = result.x - result.x.mean()
    theta_map = {m: np.nan for m in models}
    theta_map.update({m: float(theta[index[m]]) for m in active})
    return {
        "theta": theta_map,
        "converged": bool(result.success),
        "message": str(result.message),
        "n_iter": int(result.nit),
        "objective": float(result.fun) if math.isfinite(float(result.fun)) else np.nan,
        "separation_warning": separation_warning(pairwise, models),
    }


def score_dimension(pairwise: pd.DataFrame, models: list[str], dimension: str, lambda_: float) -> tuple[pd.DataFrame, dict[str, object]]:
    fit = fit_bt(pairwise, models=models, lambda_=lambda_)
    theta = pd.Series(fit["theta"], name="theta", dtype=float)
    available = theta.notna()
    scores = pd.Series(np.nan, index=theta.index, dtype=float, name="score")
    if available.sum() >= 2:
        values = theta[available]
        spread = values.max() - values.min()
        if spread > 0:
            scores.loc[available] = 100.0 * (values - values.min()) / spread
        else:
            scores.loc[available] = 50.0
    out = pd.DataFrame(
        {
            "model_id": theta.index,
            f"{dimension}_theta": theta.values,
            f"{dimension}_score": scores.values,
            f"{dimension}_applicable": available.values,
        }
    )
    return out, fit


def fit_dimensions(
    pairwise: pd.DataFrame,
    dimensions: list[str],
    models: list[str],
    lambda_: float,
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    base = pd.DataFrame({"model_id": models})
    diagnostics: dict[str, dict[str, object]] = {}
    for dim in dimensions:
        dim_pw = pairwise[pairwise["dimension"].eq(dim)].copy()
        dim_score, fit = score_dimension(dim_pw, models, dim, lambda_)
        base = base.merge(dim_score, on="model_id", how="left")
        diagnostics[dim] = fit
    return base, diagnostics

