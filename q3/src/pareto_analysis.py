from __future__ import annotations

import pandas as pd


def _complete(row) -> bool:
    return pd.notna(row.get("utility")) and pd.notna(row.get("cost"))


def dominates(candidate, target) -> bool:
    if not _complete(candidate) or not _complete(target):
        return False
    better_or_equal_utility = float(candidate["utility"]) >= float(target["utility"])
    cheaper_or_equal = float(candidate["cost"]) <= float(target["cost"])
    strictly_better = float(candidate["utility"]) > float(target["utility"]) or float(candidate["cost"]) < float(target["cost"])
    return better_or_equal_utility and cheaper_or_equal and strictly_better


def compute_pareto_frontier(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario, group in df.groupby("scenario", dropna=False):
        records = group.to_dict("records")
        for row in records:
            dominators = [other["model_id"] for other in records if dominates(other, row)]
            missing = not _complete(row)
            rows.append(
                {
                    **row,
                    "pareto": False if missing else len(dominators) == 0,
                    "dominated_by": ";".join(dominators),
                    "dominance_count": len(dominators),
                    "pareto_status_note": "missing utility or cost" if missing else "complete",
                }
            )
    return pd.DataFrame(rows)


def save_pareto(input_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    result = compute_pareto_frontier(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def compute_bootstrap_pareto_probability(bootstrap_utility: pd.DataFrame, cost_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate P(model in Pareto frontier) when Q2 bootstrap utility samples exist."""
    if bootstrap_utility.empty:
        return pd.DataFrame(columns=["model_id", "scenario", "pareto_probability"])
    required = {"model_id", "scenario", "bootstrap_id", "utility"}
    if not required.issubset(bootstrap_utility.columns):
        raise ValueError(f"Bootstrap utility must contain {sorted(required)}")
    cost_lookup = cost_df[["model_id", "scenario", "cost"]].drop_duplicates()
    merged = bootstrap_utility.merge(cost_lookup, on=["model_id", "scenario"], how="left")
    rows = []
    for (scenario, bootstrap_id), group in merged.groupby(["scenario", "bootstrap_id"], dropna=False):
        pareto = compute_pareto_frontier(group)
        for _, row in pareto.iterrows():
            rows.append({"scenario": scenario, "bootstrap_id": bootstrap_id, "model_id": row["model_id"], "pareto": row["pareto"]})
    if not rows:
        return pd.DataFrame(columns=["model_id", "scenario", "pareto_probability"])
    probs = pd.DataFrame(rows).groupby(["model_id", "scenario"], as_index=False)["pareto"].mean()
    return probs.rename(columns={"pareto": "pareto_probability"})
