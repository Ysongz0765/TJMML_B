from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def dimension_score_matrix(dimension_scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=dimension_scores["model_id"])
    for dim in dimensions:
        out[dim] = dimension_scores[f"{dim}_score"].to_numpy()
    return out


def information_factor(scores: pd.Series, eps: float = 1e-9) -> float:
    values = scores.dropna().astype(float)
    n = len(values)
    if n <= 1:
        return 0.0
    shifted = values - min(0.0, values.min()) + eps
    total = shifted.sum()
    if total <= 0:
        return 0.0
    p = shifted / total
    entropy = -float(np.sum(p * np.log(p))) / np.log(n)
    return float(np.clip(1.0 - entropy, 0.0, 1.0))


def non_redundancy_factors(score_matrix: pd.DataFrame) -> dict[str, float]:
    out = {}
    for dim in score_matrix.columns:
        corrs = []
        for other in score_matrix.columns:
            if other == dim:
                continue
            common = score_matrix[[dim, other]].dropna()
            if len(common) >= 3 and common[dim].nunique() > 1 and common[other].nunique() > 1:
                rho = spearmanr(common[dim], common[other]).correlation
                if np.isfinite(rho):
                    corrs.append(abs(float(rho)))
        out[dim] = float(np.clip(1.0 - np.mean(corrs), 0.0, 1.0)) if corrs else 1.0
    return out


def stability_factors(
    dimensions: list[str],
    bootstrap_dimension_scores: pd.DataFrame | None = None,
) -> dict[str, float]:
    if bootstrap_dimension_scores is None or bootstrap_dimension_scores.empty:
        return {dim: 1.0 for dim in dimensions}
    uncertainty = {}
    for dim in dimensions:
        col = f"{dim}_score"
        if col not in bootstrap_dimension_scores:
            uncertainty[dim] = np.nan
            continue
        sd_by_model = bootstrap_dimension_scores.groupby("model_id")[col].std().dropna()
        uncertainty[dim] = float(sd_by_model.median()) if len(sd_by_model) else np.nan
    finite = [v for v in uncertainty.values() if np.isfinite(v)]
    denom = float(np.median(finite)) if finite and np.median(finite) > 0 else 1.0
    return {
        dim: float(1.0 / (1.0 + ((uncertainty[dim] / denom) if np.isfinite(uncertainty[dim]) else 1.0)))
        for dim in dimensions
    }


def compute_dimension_weights(
    dimension_scores: pd.DataFrame,
    dimensions: list[str],
    bootstrap_dimension_scores: pd.DataFrame | None = None,
    stability_override: dict[str, float] | None = None,
) -> pd.DataFrame:
    score_matrix = dimension_score_matrix(dimension_scores, dimensions)
    info = {dim: information_factor(score_matrix[dim]) for dim in dimensions}
    nonred = non_redundancy_factors(score_matrix)
    stability = stability_override or stability_factors(dimensions, bootstrap_dimension_scores)
    rows = []
    for dim in dimensions:
        raw = info[dim] * nonred[dim] * stability[dim]
        rows.append(
            {
                "dimension": dim,
                "information": info[dim],
                "non_redundancy": nonred[dim],
                "stability": stability[dim],
                "raw_weight": raw,
            }
        )
    out = pd.DataFrame(rows)
    total = out["raw_weight"].sum()
    if total <= 0:
        out["final_weight"] = 1.0 / len(out)
    else:
        out["final_weight"] = out["raw_weight"] / total
    return out

