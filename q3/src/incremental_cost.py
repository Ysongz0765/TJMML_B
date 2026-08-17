from __future__ import annotations

import math

import pandas as pd


def compute_icer(pareto_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    front = pareto_df[(pareto_df["pareto"] == True)].dropna(subset=["utility", "cost"]).copy()
    for scenario, group in front.groupby("scenario", dropna=False):
        ordered = group.sort_values(["cost", "utility", "model_id"], ascending=[True, True, True]).reset_index(drop=True)
        for idx in range(len(ordered) - 1):
            a = ordered.iloc[idx]
            b = ordered.iloc[idx + 1]
            delta_cost = float(b["cost"]) - float(a["cost"])
            delta_utility = float(b["utility"]) - float(a["utility"])
            if delta_utility == 0:
                icer = math.inf if delta_cost > 0 else pd.NA
            else:
                icer = delta_cost / delta_utility
            rows.append(
                {
                    "scenario": scenario,
                    "from_model": a["model_id"],
                    "to_model": b["model_id"],
                    "delta_cost": delta_cost,
                    "delta_utility": delta_utility,
                    "icer": icer,
                }
            )
    return pd.DataFrame(rows)


def save_icer(pareto_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(pareto_path)
    result = compute_icer(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result

