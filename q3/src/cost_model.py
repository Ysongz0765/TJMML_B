from __future__ import annotations

from pathlib import Path

import pandas as pd


PRICE_UNIT = "USD / 1M tokens"


def _to_number(value):
    if pd.isna(value) or value == "" or str(value).upper() == "NA":
        return pd.NA
    return pd.to_numeric(value, errors="coerce")


def compute_scenario_cost(model_price: dict, workload: dict) -> dict:
    """Compute one model-scenario workload cost using prices in USD / 1M tokens."""
    input_price = _to_number(model_price.get("input_price"))
    output_price = _to_number(model_price.get("output_price"))
    n_calls = _to_number(workload.get("n_calls"))
    input_tokens = _to_number(workload.get("input_tokens"))
    output_tokens = _to_number(workload.get("output_tokens"))

    if any(pd.isna(x) for x in [input_price, output_price, n_calls, input_tokens, output_tokens]):
        return {"input_cost": pd.NA, "output_cost": pd.NA, "cost": pd.NA}

    input_cost = float(n_calls) * float(input_tokens) * float(input_price) / 1_000_000
    output_cost = float(n_calls) * float(output_tokens) * float(output_price) / 1_000_000
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "cost": input_cost + output_cost,
    }


def compute_all_costs(
    pricing: pd.DataFrame,
    workloads: pd.DataFrame,
    utilities: pd.DataFrame | None = None,
    workload_level: str = "baseline_template",
) -> pd.DataFrame:
    workloads_use = workloads.copy()
    if workload_level is not None and "workload_level" in workloads_use.columns:
        workloads_use = workloads_use[workloads_use["workload_level"] == workload_level]

    rows = []
    utility_lookup = {}
    if utilities is not None and not utilities.empty:
        for _, row in utilities.iterrows():
            utility_lookup[(row.get("model_id"), row.get("scenario"))] = row.get("utility")

    for _, model_row in pricing.iterrows():
        for _, workload_row in workloads_use.iterrows():
            costs = compute_scenario_cost(model_row.to_dict(), workload_row.to_dict())
            rows.append(
                {
                    "model_id": model_row.get("model_id"),
                    "model_name": model_row.get("model_name"),
                    "scenario": workload_row.get("scenario"),
                    "workload_level": workload_row.get("workload_level"),
                    "utility": utility_lookup.get((model_row.get("model_id"), workload_row.get("scenario")), pd.NA),
                    **costs,
                }
            )
    return pd.DataFrame(rows)


def load_and_compute(
    pricing_path: Path,
    workload_path: Path,
    utility_path: Path | None,
    output_path: Path,
    workload_level: str = "baseline_template",
) -> pd.DataFrame:
    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    workloads = pd.read_csv(workload_path, keep_default_na=False)
    utilities = None
    if utility_path is not None and utility_path.exists():
        utilities = pd.read_csv(utility_path, keep_default_na=False)
        utilities["utility"] = pd.to_numeric(utilities.get("utility"), errors="coerce")
        utilities = utilities.dropna(subset=["utility"])
    result = compute_all_costs(pricing, workloads, utilities, workload_level=workload_level)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result

