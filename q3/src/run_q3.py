from __future__ import annotations

from pathlib import Path

import pandas as pd

from budget_selection import save_budget_selection
from cost_model import load_and_compute
from cost_performance_fit import save_fit_reports
from incremental_cost import save_icer
from pareto_analysis import save_pareto
from plotting import generate_all_plots
from sensitivity_analysis import run_sensitivity
from validate_q3_data import validate_q3_data


def _has_complete_prices(path: Path) -> bool:
    df = pd.read_csv(path, keep_default_na=False)
    return pd.to_numeric(df["input_price"], errors="coerce").notna().all() and pd.to_numeric(df["output_price"], errors="coerce").notna().all()


def _has_q2_utility(path: Path) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path, keep_default_na=False)
    return "utility" in df.columns and pd.to_numeric(df["utility"], errors="coerce").notna().any()


def run(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[2]
    q3 = root / "q3"
    pricing = q3 / "data" / "model_pricing.csv"
    workload = q3 / "data" / "workload_config.csv"
    utility = q3 / "data" / "scenario_utility.csv"
    utility_template = q3 / "data" / "scenario_utility_template.csv"
    q2_master = root / "q2" / "data" / "q2_model_master_table.csv"
    diagnostics = q3 / "outputs" / "diagnostics"
    tables = q3 / "outputs" / "tables"
    figures = q3 / "outputs" / "figures"

    utility_for_validation = utility if utility.exists() else utility_template
    report = validate_q3_data(pricing, workload, utility_for_validation, q2_master, diagnostics / "q3_data_validation_report.csv")
    complete_prices = _has_complete_prices(pricing)
    has_utility = _has_q2_utility(utility)
    waiting = not has_utility

    status = {
        "Q3_FRAMEWORK_READY": True,
        "Q3_PRICING_DATA_READY": complete_prices,
        "Q3_WORKLOAD_MODEL_READY": True,
        "Q3_WAITING_FOR_Q2_SCENARIO_UTILITY": waiting,
        "Q3_READY_FOR_FINAL_RUN": complete_prices and has_utility,
        "validation_issue_count": int(len(report)),
    }

    if complete_prices and not has_utility:
        load_and_compute(pricing, workload, None, tables / "q3_cost_only_waiting_for_utility.csv")

    if not status["Q3_READY_FOR_FINAL_RUN"]:
        (diagnostics / "q3_run_status.txt").write_text("\n".join(f"{k} = {v}" for k, v in status.items()), encoding="utf-8")
        print("Q3_WAITING_FOR_Q2_SCENARIO_UTILITY =", waiting)
        print("Q3_READY_FOR_FINAL_RUN =", status["Q3_READY_FOR_FINAL_RUN"])
        return status

    cost_path = tables / "q3_cost_utility.csv"
    pareto_path = tables / "q3_pareto_frontier.csv"
    budget_path = tables / "q3_budget_selection.csv"
    icer_path = tables / "q3_incremental_cost_effectiveness.csv"
    fit_path = tables / "q3_cost_performance_fit.csv"
    sensitivity_path = tables / "q3_sensitivity_analysis.csv"

    load_and_compute(pricing, workload, utility, cost_path)
    save_pareto(cost_path, pareto_path)
    save_budget_selection(cost_path, budget_path)
    save_icer(pareto_path, icer_path)
    save_fit_reports(cost_path, pareto_path, fit_path)
    run_sensitivity(pricing, workload, utility, sensitivity_path)
    generate_all_plots(pareto_path, budget_path, figures, cost_path=cost_path, icer_path=icer_path, sensitivity_path=sensitivity_path)
    (diagnostics / "q3_run_status.txt").write_text("\n".join(f"{k} = {v}" for k, v in status.items()), encoding="utf-8")
    return status


if __name__ == "__main__":
    run()
