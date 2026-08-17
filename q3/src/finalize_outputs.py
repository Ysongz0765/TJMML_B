from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _read_tables(root: Path) -> dict[str, pd.DataFrame]:
    tables = root / "q3" / "outputs" / "tables"
    return {
        "costs": pd.read_csv(tables / "scenario_costs.csv", keep_default_na=False),
        "pareto": pd.read_csv(tables / "q3_pareto_frontier.csv", keep_default_na=False),
        "budget": pd.read_csv(tables / "q3_budget_selection.csv", keep_default_na=False),
        "icer": pd.read_csv(tables / "q3_incremental_cost_effectiveness.csv", keep_default_na=False),
        "fit": pd.read_csv(tables / "q3_cost_performance_fit.csv", keep_default_na=False),
        "sensitivity": pd.read_csv(tables / "q3_sensitivity_analysis.csv", keep_default_na=False),
        "probability": pd.read_csv(tables / "q3_pareto_probability.csv", keep_default_na=False),
        "cohort": pd.read_csv(tables / "q3_model_analysis_cohort.csv", keep_default_na=False),
    }


def _write_scenario_costs_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    costs = data["costs"].copy()
    cohort = data["cohort"][["model_id", "pricing_human_verified", "included_in_regression"]].copy()
    pricing = pd.read_csv(tables.parent.parent / "data" / "model_pricing.csv", keep_default_na=False)
    prices = pricing[["model_id", "input_price", "output_price"]]
    result = costs.merge(prices, on="model_id", how="left").merge(cohort, on="model_id", how="left")
    result = result.drop(columns=["total_cost"], errors="ignore").rename(columns={"cost": "total_cost"})
    result["pricing_human_verified"] = result["pricing_human_verified"].astype(str).str.upper().eq("TRUE")
    columns = [
        "model_id",
        "model_name",
        "scenario",
        "utility",
        "input_tokens",
        "output_tokens",
        "input_price",
        "output_price",
        "input_cost",
        "output_cost",
        "total_cost",
        "cost_observability",
        "pricing_human_verified",
        "included_in_main_pareto",
        "included_in_regression",
        "cost_basis",
        "exclusion_reason",
    ]
    result = result[columns].sort_values(["scenario", "model_id"]).reset_index(drop=True)
    result.to_csv(tables / "scenario_costs_final.csv", index=False)
    return result


def _write_pareto_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    pareto = data["pareto"].copy()
    result = pareto.rename(columns={"model_name": "model"})[
        [
            "model_id",
            "model",
            "scenario",
            "utility",
            "cost",
            "pareto",
            "dominated_by",
            "dominance_count",
            "pareto_status_note",
        ]
    ].sort_values(["scenario", "cost", "model_id"]).reset_index(drop=True)
    result.to_csv(tables / "pareto_results_final.csv", index=False)
    return result


def _write_budget_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    budget = data["budget"].copy()
    rows = []
    for scenario, group in budget.groupby("scenario", sort=True):
        feasible = group[group["optimal_model_id"] != "NO_FEASIBLE_MODEL"].copy()
        feasible = feasible.sort_values("budget_lower").reset_index(drop=True)
        previous = None
        for _, row in feasible.iterrows():
            model_id = row["optimal_model_id"]
            if model_id == previous:
                continue
            if previous is None:
                before_utility = np.nan
                before_cost = np.nan
                before_model = "NO_FEASIBLE_MODEL"
            else:
                prior = feasible[feasible["optimal_model_id"] == previous].iloc[0]
                before_utility = float(prior["utility"])
                before_cost = float(prior["cost"])
                before_model = previous
            rows.append(
                {
                    "scenario": scenario,
                    "budget_threshold": float(row["budget_lower"]),
                    "optimal_model_before": before_model,
                    "optimal_model_after": model_id,
                    "delta_utility": np.nan if pd.isna(before_utility) else float(row["utility"]) - before_utility,
                    "delta_cost": np.nan if pd.isna(before_cost) else float(row["cost"]) - before_cost,
                    "utility_after": float(row["utility"]),
                    "cost_after": float(row["cost"]),
                }
            )
            previous = model_id
    result = pd.DataFrame(rows)
    result.to_csv(tables / "budget_switch_points_final.csv", index=False)
    return result


def _write_icer_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    result = data["icer"].copy()
    result["near_zero_utility_gain"] = result["delta_utility"].abs() < 1e-6
    result["unusually_large_icer"] = result["icer"].abs() >= 2.0
    result["extended_dominance_flag"] = False
    result.to_csv(tables / "icer_results_final.csv", index=False)
    return result


def _write_fit_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    result = data["fit"].copy()
    result["n_models_used"] = result["n"]
    result["n_parameters"] = result["fit_model"].map({"linear": 2, "log": 2, "saturation": 3})
    result["aicc_valid"] = result["aicc"].notna()
    result["fit_warning"] = ""
    frontier = result["subset"].eq("pareto_frontier")
    result.loc[frontier & (result["n_models_used"] <= 3), "fit_warning"] = "INSUFFICIENT_FRONTIER_SAMPLE"
    result["parameter_stability"] = np.where(
        frontier & (result["n_models_used"] <= 3),
        "UNSTABLE_SMALL_SAMPLE",
        "CAUTION_SMALL_SAMPLE",
    )
    result["marginal_return_conclusion"] = (
        "NO_STABLE_UNIFIED_DIMINISHING_RETURN_EVIDENCE"
    )
    result.to_csv(tables / "cost_performance_fit_final.csv", index=False)
    return result


def _summarize_sensitivity(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    sensitivity = data["sensitivity"].copy()
    pareto = data["pareto"]
    nominal = {
        scenario: set(group.loc[group["pareto"], "model_id"])
        for scenario, group in pareto.groupby("scenario")
    }
    rows = []
    analysis_map = {
        "input_scale": ("input_scale", "input_scale_budget"),
        "input_output_ratio": ("input_output_ratio", None),
        "price_perturbation": ("price_perturbation", "price_perturbation_budget"),
    }
    for scenario in sorted(nominal):
        for label, (pareto_analysis, budget_analysis) in analysis_map.items():
            p = sensitivity[(sensitivity["scenario"] == scenario) & (sensitivity["analysis"] == pareto_analysis)]
            if p.empty:
                continue
            by_parameter = p.groupby("parameter")
            member_rates = []
            all_member_rates = []
            front_sizes = []
            for _, group in by_parameter:
                members = set(group.loc[group["pareto"].astype(str).str.upper() == "TRUE", "model_id"])
                front_sizes.append(len(members))
                member_rates.extend([model_id in members for model_id in nominal[scenario]])
                all_member_rates.append(nominal[scenario].issubset(members))
            budget = (
                sensitivity[
                    (sensitivity["scenario"] == scenario)
                    & (sensitivity["analysis"] == budget_analysis)
                    & (sensitivity["model_id"] != "NO_FEASIBLE_MODEL")
                ]
                if budget_analysis
                else pd.DataFrame()
            )
            mode_model = ""
            mode_rate = np.nan
            threshold_min = np.nan
            threshold_max = np.nan
            if not budget.empty:
                counts = budget["model_id"].value_counts()
                mode_model = str(counts.index[0])
                mode_rate = float(counts.iloc[0] / len(budget))
                threshold_min = float(pd.to_numeric(budget["cost"], errors="coerce").min())
                threshold_max = float(pd.to_numeric(budget["cost"], errors="coerce").max())
            rows.append(
                {
                    "scenario": scenario,
                    "analysis": label,
                    "parameter_points": int(p["parameter"].nunique()),
                    "nominal_pareto_models": ";".join(sorted(nominal[scenario])),
                    "pareto_member_retention_rate": float(np.mean(member_rates)),
                    "all_nominal_members_retained_rate": float(np.mean(all_member_rates)),
                    "mean_frontier_size": float(np.mean(front_sizes)),
                    "optimal_model_mode": mode_model,
                    "optimal_model_mode_rate": mode_rate,
                    "budget_threshold_min": threshold_min,
                    "budget_threshold_max": threshold_max,
                    "conclusion": "STABLE_ON_TESTED_GRID"
                    if float(np.mean(all_member_rates)) == 1.0
                    else "SENSITIVE_ON_TESTED_GRID",
                }
            )
    result = pd.DataFrame(rows)
    result.to_csv(tables / "sensitivity_summary_final.csv", index=False)
    return result


def _write_probability_final(data: dict[str, pd.DataFrame], tables: Path) -> pd.DataFrame:
    nominal = data["pareto"][["model_id", "scenario", "pareto"]].rename(columns={"pareto": "nominal_pareto"})
    result = data["probability"].merge(nominal, on=["model_id", "scenario"], how="left")
    result = result[["model_id", "scenario", "nominal_pareto", "pareto_probability"]]
    result.to_csv(tables / "pareto_probability_final.csv", index=False)
    return result


def finalize_outputs(root: Path | None = None) -> dict[str, int]:
    root = root or Path(__file__).resolve().parents[2]
    tables = root / "q3" / "outputs" / "tables"
    data = _read_tables(root)
    outputs = {
        "scenario_costs_final": len(_write_scenario_costs_final(data, tables)),
        "pareto_results_final": len(_write_pareto_final(data, tables)),
        "budget_switch_points_final": len(_write_budget_final(data, tables)),
        "icer_results_final": len(_write_icer_final(data, tables)),
        "cost_performance_fit_final": len(_write_fit_final(data, tables)),
        "sensitivity_summary_final": len(_summarize_sensitivity(data, tables)),
        "pareto_probability_final": len(_write_probability_final(data, tables)),
    }
    return outputs


if __name__ == "__main__":
    import json

    print(json.dumps(finalize_outputs(), indent=2))
