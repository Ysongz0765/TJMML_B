from __future__ import annotations

import pandas as pd

from budget_selection import compute_budget_frontier
from cost_model import compute_all_costs
from pareto_analysis import compute_pareto_frontier


def input_scale_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, scales=(0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows = []
    baseline = workload[workload["workload_level"] == "baseline_template"].copy()
    for scale in scales:
        varied = baseline.copy()
        varied["input_tokens"] = pd.to_numeric(varied["input_tokens"], errors="coerce") * scale
        varied["workload_level"] = f"input_scale_{scale:g}"
        costs = compute_all_costs(pricing, varied, utilities, workload_level=None)
        pareto = compute_pareto_frontier(costs)
        budget = compute_budget_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "input_scale", "parameter": scale, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
        for _, row in budget.iterrows():
            rows.append({"analysis": "input_scale_budget", "parameter": scale, "scenario": row["scenario"], "model_id": row["optimal_model_id"], "cost": row.get("cost"), "utility": row.get("utility"), "pareto": pd.NA})
    return pd.DataFrame(rows)


def ratio_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, ratios=(0.1, 0.3, 0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows = []
    baseline = workload[workload["workload_level"] == "baseline_template"].copy()
    for ratio in ratios:
        varied = baseline.copy()
        varied["input_tokens"] = pd.to_numeric(varied["input_tokens"], errors="coerce")
        varied["output_tokens"] = varied["input_tokens"] * ratio
        varied["input_output_ratio"] = ratio
        varied["workload_level"] = f"ratio_{ratio:g}"
        costs = compute_all_costs(pricing, varied, utilities, workload_level=None)
        pareto = compute_pareto_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "input_output_ratio", "parameter": ratio, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
    return pd.DataFrame(rows)


def price_perturbation_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, deltas=(-0.1, -0.05, 0.0, 0.05, 0.1)) -> pd.DataFrame:
    rows = []
    for delta in deltas:
        varied = pricing.copy()
        for col in ["input_price", "output_price", "cached_input_price"]:
            if col in varied.columns:
                nums = pd.to_numeric(varied[col], errors="coerce")
                varied[col] = nums * (1 + delta)
        costs = compute_all_costs(varied, workload, utilities, workload_level="baseline_template")
        pareto = compute_pareto_frontier(costs)
        budget = compute_budget_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "price_perturbation", "parameter": delta, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
        for _, row in budget.iterrows():
            rows.append({"analysis": "price_perturbation_budget", "parameter": delta, "scenario": row["scenario"], "model_id": row["optimal_model_id"], "cost": row.get("cost"), "utility": row.get("utility"), "pareto": pd.NA})
    return pd.DataFrame(rows)


def run_sensitivity(pricing_path, workload_path, utility_path, output_path) -> pd.DataFrame:
    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    workload = pd.read_csv(workload_path, keep_default_na=False)
    utilities = None
    if utility_path is not None and utility_path.exists():
        utilities = pd.read_csv(utility_path, keep_default_na=False)
        utilities["utility"] = pd.to_numeric(utilities.get("utility"), errors="coerce")
        utilities = utilities.dropna(subset=["utility"])
    result = pd.concat(
        [
            input_scale_sensitivity(pricing, workload, utilities),
            ratio_sensitivity(pricing, workload, utilities),
            price_perturbation_sensitivity(pricing, workload, utilities),
        ],
        ignore_index=True,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result

