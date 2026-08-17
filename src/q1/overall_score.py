from __future__ import annotations

import numpy as np
import pandas as pd


def compute_overall_scores(
    dimension_scores: pd.DataFrame,
    weights: pd.DataFrame,
    dimensions: list[str],
    model_names: dict[str, str],
    model_subset: set[str] | None = None,
) -> pd.DataFrame:
    weight_map = dict(zip(weights["dimension"], weights["final_weight"]))
    rows = []
    for _, row in dimension_scores.iterrows():
        model_id = row["model_id"]
        if model_subset is not None and model_id not in model_subset:
            continue
        numerator = 0.0
        denominator = 0.0
        available = 0
        values = {}
        for dim in dimensions:
            score = row[f"{dim}_score"]
            values[f"{dim}_score"] = score
            if pd.notna(score):
                numerator += weight_map[dim] * float(score)
                denominator += weight_map[dim]
                available += 1
        overall = numerator / denominator if denominator > 0 else np.nan
        rows.append(
            {
                "model_id": model_id,
                "model": model_names.get(model_id, model_id),
                "overall_score": overall,
                "effective_weight_coverage": denominator,
                "number_of_available_dimensions": available,
                **values,
            }
        )
    out = pd.DataFrame(rows).sort_values(["overall_score", "effective_weight_coverage"], ascending=[False, False])
    out["rank"] = range(1, len(out) + 1)
    cols = ["rank", "model_id", "model", "overall_score", "effective_weight_coverage", "number_of_available_dimensions"]
    score_cols = [f"{dim}_score" for dim in dimensions]
    return out[cols + score_cols]


def rerank_with_dimensions(
    dimension_scores: pd.DataFrame,
    weights: pd.DataFrame,
    keep_dimensions: list[str],
    all_dimensions: list[str],
    model_names: dict[str, str],
    model_subset: set[str] | None = None,
) -> pd.DataFrame:
    sub_weights = weights[weights["dimension"].isin(keep_dimensions)].copy()
    sub_weights["final_weight"] = sub_weights["final_weight"] / sub_weights["final_weight"].sum()
    return compute_overall_scores(dimension_scores, sub_weights, keep_dimensions, model_names, model_subset=model_subset)
