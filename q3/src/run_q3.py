from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from budget_selection import compute_budget_frontier, save_budget_selection
from cohort import attach_cost_observability, build_analysis_cohort, full_model_ids, save_analysis_cohort
from cost_model import compute_all_costs, load_and_compute
from cost_performance_fit import save_fit_reports
from incremental_cost import save_icer
from pareto_analysis import compute_bootstrap_pareto_probability, save_pareto
from plotting import generate_all_plots
from sensitivity_analysis import run_sensitivity
from validate_q3_data import validate_q3_data


EXPECTED_SCENARIOS = {"Research", "General", "Coding"}


def _has_complete_prices(path: Path) -> bool:
    df = pd.read_csv(path, keep_default_na=False)
    return pd.to_numeric(df["input_price"], errors="coerce").notna().all() and pd.to_numeric(df["output_price"], errors="coerce").notna().all()


def _has_pricing_mapping(audit_path: Path) -> bool:
    if not audit_path.exists():
        return False
    audit = pd.read_csv(audit_path, keep_default_na=False)
    required = {"sku_mapping_status", "config_mapping_status"}
    if not required.issubset(audit.columns):
        return False
    sku_ok = audit["sku_mapping_status"].astype(str).str.strip().ne("").all() and audit["sku_mapping_status"].ne("UNRESOLVED").all()
    config_ok = audit["config_mapping_status"].astype(str).str.strip().ne("").all() and audit["config_mapping_status"].ne("UNRESOLVED").all()
    return bool(sku_ok and config_ok)


def _has_human_verified_prices(path: Path) -> bool:
    df = pd.read_csv(path, keep_default_na=False)
    if "human_verified" not in df.columns:
        return False
    return bool(df["human_verified"].astype(str).str.upper().eq("TRUE").all())


def _validate_q2_nominal(utility: pd.DataFrame, model_ids: set[str]) -> dict:
    required = {"model_id", "model_name", "scenario", "utility"}
    if not required.issubset(utility.columns):
        return {"valid": False, "reason": f"missing columns: {sorted(required - set(utility.columns))}"}
    utility_num = pd.to_numeric(utility["utility"], errors="coerce")
    duplicates = int(utility.duplicated(["model_id", "scenario"]).sum())
    missing = int(utility_num.isna().sum())
    unknown_ids = sorted(set(utility["model_id"]) - model_ids)
    scenarios = set(utility["scenario"])
    per_scenario = utility.groupby("scenario")["model_id"].nunique().to_dict()
    rank_ok = True
    for _, group in utility.groupby("scenario"):
        ordered = group.sort_values("utility", ascending=False).reset_index(drop=True)
        rank_ok = rank_ok and ordered["utility"].is_monotonic_decreasing
    valid = (
        len(utility) == 30
        and utility["model_id"].nunique() == 10
        and scenarios == EXPECTED_SCENARIOS
        and duplicates == 0
        and missing == 0
        and not unknown_ids
        and all(value == 10 for value in per_scenario.values())
        and rank_ok
    )
    return {
        "valid": bool(valid),
        "rows": int(len(utility)),
        "models": int(utility["model_id"].nunique()),
        "scenarios": sorted(scenarios),
        "duplicates": duplicates,
        "missing_utility": missing,
        "unknown_model_ids": unknown_ids,
        "models_per_scenario": per_scenario,
        "utility_direction_larger_is_better": bool(rank_ok),
    }


def _validate_q2_bootstrap(bootstrap: pd.DataFrame, model_ids: set[str]) -> dict:
    required = {"bootstrap_id", "model_id", "scenario", "utility"}
    if not required.issubset(bootstrap.columns):
        return {"valid": False, "reason": f"missing columns: {sorted(required - set(bootstrap.columns))}"}
    utility_num = pd.to_numeric(bootstrap["utility"], errors="coerce")
    duplicates = int(bootstrap.duplicated(["bootstrap_id", "model_id", "scenario"]).sum())
    missing = int(utility_num.isna().sum())
    unknown_ids = sorted(set(bootstrap["model_id"]) - model_ids)
    valid = (
        len(bootstrap) == 60000
        and bootstrap["bootstrap_id"].nunique() == 2000
        and set(bootstrap["scenario"]) == EXPECTED_SCENARIOS
        and duplicates == 0
        and missing == 0
        and not unknown_ids
    )
    return {
        "valid": bool(valid),
        "rows": int(len(bootstrap)),
        "draws": int(bootstrap["bootstrap_id"].nunique()),
        "duplicates": duplicates,
        "missing_utility": missing,
        "unknown_model_ids": unknown_ids,
    }


def _baseline_workload(workload: pd.DataFrame) -> pd.DataFrame:
    baseline = workload[workload["workload_level"] == "baseline_template"].copy()
    baseline["input_tokens"] = pd.to_numeric(baseline["input_tokens"], errors="coerce")
    baseline["output_tokens"] = pd.to_numeric(baseline["output_tokens"], errors="coerce")
    return baseline


def _main_analysis_ready(
    q2_valid: bool,
    workload_ready: bool,
    full_ids: list[str],
    cohort: pd.DataFrame,
    has_hard_validation_error: bool,
) -> bool:
    """Allow a transparent FULL-cohort run when other models are excluded."""
    return bool(
        q2_valid
        and workload_ready
        and len(full_ids) >= 3
        and len(cohort) == 10
        and not has_hard_validation_error
    )


def _write_scenario_costs(
    pricing: pd.DataFrame,
    workload: pd.DataFrame,
    utilities: pd.DataFrame,
    cohort: pd.DataFrame,
    output_path: Path,
) -> pd.DataFrame:
    baseline = _baseline_workload(workload)
    costs = compute_all_costs(pricing, baseline, utilities, workload_level=None)
    workload_fields = baseline[["scenario", "input_tokens", "output_tokens", "input_output_ratio"]].drop_duplicates("scenario")
    costs = costs.merge(workload_fields, on="scenario", how="left")
    costs = attach_cost_observability(costs, cohort)
    costs["total_cost"] = costs["cost"]
    costs["cost_basis"] = costs["cost_observability"].map(
        {
            "FULL": "complete official base API cost",
            "PARTIAL": "BASE_MODEL_COST_ONLY; fallback configuration cost unresolved",
            "MISSING": "cost unavailable; no imputation",
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    costs.to_csv(output_path, index=False)
    return costs


def _write_budget_aliases(budget: pd.DataFrame, tables: Path) -> None:
    budget.to_csv(tables / "budget_switch_points.csv", index=False)


def _write_icer_aliases(icer: pd.DataFrame, tables: Path) -> None:
    icer.to_csv(tables / "icer_results.csv", index=False)


def _write_fit_aliases(fit: pd.DataFrame, tables: Path) -> None:
    fit.to_csv(tables / "cost_performance_fit.csv", index=False)


def run(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[2]
    q3 = root / "q3"
    pricing_path = q3 / "data" / "model_pricing.csv"
    pricing_audit_path = q3 / "data" / "pricing_audit.csv"
    workload_path = q3 / "data" / "workload_config.csv"
    utility_path = q3 / "data" / "scenario_utility.csv"
    bootstrap_path = q3 / "data" / "scenario_utility_bootstrap.csv"
    utility_template = q3 / "data" / "scenario_utility_template.csv"
    q2_master_path = root / "q2" / "data" / "q2_model_master_table.csv"
    diagnostics = q3 / "outputs" / "diagnostics"
    tables = q3 / "outputs" / "tables"
    figures = q3 / "outputs" / "figures"

    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    pricing_audit = pd.read_csv(pricing_audit_path, keep_default_na=False)
    workload = pd.read_csv(workload_path, keep_default_na=False)
    utilities = pd.read_csv(utility_path, keep_default_na=False) if utility_path.exists() else pd.read_csv(utility_template, keep_default_na=False)
    bootstrap = pd.read_csv(bootstrap_path, keep_default_na=False) if bootstrap_path.exists() else pd.DataFrame()
    model_ids = set(pd.read_csv(q2_master_path, keep_default_na=False)["model_id"])

    utility_check = _validate_q2_nominal(utilities, model_ids) if utility_path.exists() else {"valid": False, "reason": "formal Q2 utility file absent"}
    bootstrap_check = _validate_q2_bootstrap(bootstrap, model_ids) if bootstrap_path.exists() else {"valid": False, "reason": "formal Q2 bootstrap file absent"}
    q2_valid = bool(utility_check.get("valid", False))
    cohort = build_analysis_cohort(pricing, pricing_audit, utilities if q2_valid else None)
    cohort_path = tables / "q3_model_analysis_cohort.csv"
    save_analysis_cohort(cohort, cohort_path)
    full_ids = full_model_ids(cohort)
    workload_ready = set(_baseline_workload(workload)["scenario"]) == EXPECTED_SCENARIOS
    main_ready = _main_analysis_ready(q2_valid, workload_ready, full_ids, cohort, False)

    utility_for_validation = utility_path if utility_path.exists() else utility_template
    validation_report = validate_q3_data(
        pricing_path,
        workload_path,
        utility_for_validation,
        q2_master_path,
        diagnostics / "q3_data_validation_report.csv",
    )
    has_hard_validation_error = bool((validation_report["severity"] == "ERROR").any()) if not validation_report.empty else False
    main_ready = _main_analysis_ready(q2_valid, workload_ready, full_ids, cohort, has_hard_validation_error)

    status = {
        "REMOTE_REPOSITORY_SYNCED": (q3 / "data" / "q2_interface_provenance.json").exists(),
        "Q2_FORMAL_SCENARIO_UTILITY_FOUND": utility_path.exists(),
        "Q2_SCENARIO_UTILITY_VALIDATED": q2_valid,
        "Q2_BOOTSTRAP_UTILITY_FOUND": bootstrap_path.exists(),
        "Q3_FRAMEWORK_READY": True,
        "Q3_WORKLOAD_BASELINE_READY": workload_ready,
        "Q3_PRICING_MAPPING_READY": _has_pricing_mapping(pricing_audit_path),
        "Q3_ALL_MODELS_FULL_COST_READY": set(cohort["cost_observability"]) == {"FULL"},
        "Q3_MAIN_ANALYSIS_COHORT_READY": main_ready,
        "Q3_PRICING_HUMAN_VERIFIED": _has_human_verified_prices(pricing_path),
        "Q3_PARETO_COMPLETED": False,
        "Q3_BUDGET_SELECTION_COMPLETED": False,
        "Q3_ICER_COMPLETED": False,
        "Q3_COST_PERFORMANCE_FIT_COMPLETED": False,
        "Q3_SENSITIVITY_COMPLETED": False,
        "Q3_BOOTSTRAP_PARETO_COMPLETED": False,
        "Q3_PROVISIONAL_RESULTS_READY": False,
        "Q3_FINAL_HUMAN_VERIFIED_RESULTS_READY": False,
        "FULL_COHORT_SIZE": len(full_ids),
        "PARTIAL_COHORT_SIZE": int((cohort["cost_observability"] == "PARTIAL").sum()),
        "MISSING_COHORT_SIZE": int((cohort["cost_observability"] == "MISSING").sum()),
        "validation_issue_count": int(len(validation_report)),
    }

    if not main_ready:
        diagnostics.mkdir(parents=True, exist_ok=True)
        (diagnostics / "q3_run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
        (diagnostics / "q3_run_status.txt").write_text("\n".join(f"{key} = {value}" for key, value in status.items()), encoding="utf-8")
        return status

    scenario_costs = _write_scenario_costs(pricing, workload, utilities, cohort, tables / "scenario_costs.csv")
    full_pricing = pricing[pricing["model_id"].isin(full_ids)].copy()
    full_costs = scenario_costs[scenario_costs["model_id"].isin(full_ids)].copy()
    full_costs.to_csv(tables / "q3_cost_utility.csv", index=False)
    full_costs.to_csv(tables / "q3_cost_utility_full_cohort.csv", index=False)

    pareto_path = tables / "q3_pareto_frontier.csv"
    pareto = save_pareto(tables / "q3_cost_utility.csv", pareto_path)
    pareto.to_csv(tables / "pareto_results.csv", index=False)

    budget_path = tables / "q3_budget_selection.csv"
    budget = save_budget_selection(tables / "q3_cost_utility.csv", budget_path)
    _write_budget_aliases(budget, tables)

    icer_path = tables / "q3_incremental_cost_effectiveness.csv"
    icer = save_icer(pareto_path, icer_path)
    _write_icer_aliases(icer, tables)

    fit_path = tables / "q3_cost_performance_fit.csv"
    fit = save_fit_reports(tables / "q3_cost_utility.csv", pareto_path, fit_path)
    _write_fit_aliases(fit, tables)

    sensitivity_path = tables / "q3_sensitivity_analysis.csv"
    run_sensitivity(full_pricing, workload, utilities, sensitivity_path)

    probability_path = tables / "q3_pareto_probability.csv"
    if bootstrap_check.get("valid", False):
        bootstrap_full = bootstrap[bootstrap["model_id"].isin(full_ids)].copy()
        probabilities = compute_bootstrap_pareto_probability(bootstrap_full, full_costs)
        probabilities.to_csv(probability_path, index=False)
    else:
        probabilities = pd.DataFrame()

    generated_plots = generate_all_plots(
        pareto_path,
        budget_path,
        figures,
        cost_path=tables / "q3_cost_utility.csv",
        icer_path=icer_path,
        sensitivity_path=sensitivity_path,
        pareto_probability_path=probability_path if probability_path.exists() else None,
    )

    status.update(
        {
            "Q3_PARETO_COMPLETED": pareto_path.exists(),
            "Q3_BUDGET_SELECTION_COMPLETED": budget_path.exists(),
            "Q3_ICER_COMPLETED": icer_path.exists(),
            "Q3_COST_PERFORMANCE_FIT_COMPLETED": fit_path.exists(),
            "Q3_SENSITIVITY_COMPLETED": sensitivity_path.exists(),
            "Q3_BOOTSTRAP_PARETO_COMPLETED": bool(bootstrap_check.get("valid", False) and probability_path.exists()),
            "Q3_PROVISIONAL_RESULTS_READY": True,
            "Q3_FINAL_HUMAN_VERIFIED_RESULTS_READY": False,
            "generated_plot_count": len(generated_plots),
            "bootstrap_probability_rows": int(len(probabilities)),
        }
    )
    diagnostics.mkdir(parents=True, exist_ok=True)
    (diagnostics / "q3_run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    (diagnostics / "q3_run_status.txt").write_text("\n".join(f"{key} = {value}" for key, value in status.items()), encoding="utf-8")
    return status


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
