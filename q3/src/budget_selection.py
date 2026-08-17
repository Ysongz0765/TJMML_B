from __future__ import annotations

import math

import pandas as pd


def _choose_best(feasible: pd.DataFrame) -> pd.Series | None:
    if feasible.empty:
        return None
    ordered = feasible.sort_values(["utility", "cost", "model_id"], ascending=[False, True, True])
    return ordered.iloc[0]


def compute_budget_frontier(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    complete = df.dropna(subset=["utility", "cost"]).copy()
    for scenario, group in complete.groupby("scenario", dropna=False):
        costs = sorted(group["cost"].dropna().unique())
        if not costs:
            rows.append({"scenario": scenario, "budget_lower": 0.0, "budget_upper": math.inf, "optimal_model_id": "NO_FEASIBLE_MODEL"})
            continue
        first_cost = float(costs[0])
        if first_cost > 0:
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": 0.0,
                    "budget_upper": first_cost,
                    "optimal_model_id": "NO_FEASIBLE_MODEL",
                    "optimal_model_name": "NO_FEASIBLE_MODEL",
                    "utility": pd.NA,
                    "cost": pd.NA,
                }
            )
        for idx, cost in enumerate(costs):
            upper = float(costs[idx + 1]) if idx + 1 < len(costs) else math.inf
            best = _choose_best(group[group["cost"] <= cost])
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": float(cost),
                    "budget_upper": upper,
                    "optimal_model_id": best["model_id"] if best is not None else "NO_FEASIBLE_MODEL",
                    "optimal_model_name": best.get("model_name", best.get("model", "")) if best is not None else "NO_FEASIBLE_MODEL",
                    "utility": best["utility"] if best is not None else pd.NA,
                    "cost": best["cost"] if best is not None else pd.NA,
                }
            )
    if complete.empty:
        for scenario in sorted(df["scenario"].dropna().unique()):
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": 0.0,
                    "budget_upper": math.inf,
                    "optimal_model_id": "NO_FEASIBLE_MODEL",
                    "optimal_model_name": "NO_FEASIBLE_MODEL",
                    "utility": pd.NA,
                    "cost": pd.NA,
                }
            )
    return pd.DataFrame(rows)


def save_budget_selection(input_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    result = compute_budget_frontier(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result

