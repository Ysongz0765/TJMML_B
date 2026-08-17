from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd


def _contains_all(text: str, tokens: list[str]) -> list[str]:
    return [token for token in tokens if token not in text]


def _fmt(value: object, digits: int) -> str:
    quantum = Decimal("1").scaleb(-digits)
    quantized = Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)
    return format(quantized, "f")


def run_check(root: Path) -> Path:
    freeze = root / "q3" / "frozen" / "v1.0"
    paper_dir = root / "q3" / "paper"
    text = (paper_dir / "q3_standalone.tex").read_text(encoding="utf-8")
    names = pd.read_csv(paper_dir / "q3_model_display_names.csv")
    labels = dict(zip(names.model_id, names.display_name))
    pareto = pd.read_csv(freeze / "pareto_results_final.csv", keep_default_na=False)
    costs = pd.read_csv(freeze / "scenario_costs_final.csv", keep_default_na=False)
    budget = pd.read_csv(freeze / "budget_switch_points_final.csv", keep_default_na=False)
    icer = pd.read_csv(freeze / "icer_results_final.csv", keep_default_na=False)
    fit = pd.read_csv(freeze / "cost_performance_fit_final.csv", keep_default_na=False)
    probability = pd.read_csv(freeze / "pareto_probability_final.csv", keep_default_na=False)

    checks: list[tuple[str, bool, str]] = []
    frontier_ids = pareto.loc[
        pareto.pareto.astype(str).str.upper() == "TRUE", "model_id"
    ].unique()
    missing_names = _contains_all(text, [labels[x] for x in frontier_ids])
    checks.append(("Pareto model names", not missing_names, ", ".join(missing_names)))

    threshold_tokens = sorted(
        {_fmt(value, 6) for value in budget.budget_threshold}
    )
    missing = _contains_all(text, threshold_tokens)
    checks.append(("Budget thresholds", not missing, ", ".join(missing)))

    icer_tokens = sorted({_fmt(value, 6) for value in icer.icer})
    missing = _contains_all(text, icer_tokens)
    checks.append(("ICER values", not missing, ", ".join(missing)))

    cost_tokens = sorted(
        {
            _fmt(value, 6)
            for value in costs.loc[
                costs.cost_observability == "FULL", "total_cost"
            ]
        }
    )
    missing = _contains_all(text, cost_tokens)
    checks.append(("FULL-cohort costs", not missing, ", ".join(missing)))

    all_models_fit = fit[fit.subset == "all_models"]
    for column in ["aicc", "loocv_error"]:
        values = all_models_fit[column].dropna()
        tokens = sorted({_fmt(value, 6) for value in values})
        missing = _contains_all(text, tokens)
        checks.append((f"Fit {column}", not missing, ", ".join(missing)))

    probability_tokens = sorted(
        {_fmt(value, 4) for value in probability.pareto_probability}
    )
    missing = _contains_all(text, probability_tokens)
    checks.append(("Bootstrap Pareto probabilities", not missing, ", ".join(missing)))

    forbidden = ["provisional", "待核验", "TODO", "TBD", "INSUFFICIENT_FRONTIER_SAMPLE"]
    forbidden_found = [token for token in forbidden if token.lower() in text.lower()]
    checks.append(("No release-state residue", not forbidden_found, ", ".join(forbidden_found)))

    passed = all(item[1] for item in checks)
    lines = [
        "# Q3 Numeric Consistency Check",
        "",
        "The standalone manuscript was checked against the final CSV files under "
        "`q3/frozen/v1.0/`.",
        "",
        f"`NUMERIC_CONSISTENCY = {'PASS' if passed else 'FAIL'}`",
        "",
        "| Check | Status | Missing or unexpected tokens |",
        "|---|---|---|",
    ]
    for name, status, evidence in checks:
        lines.append(f"| {name} | {'PASS' if status else 'FAIL'} | `{evidence}` |")
    output = paper_dir / "q3_numeric_consistency_check.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(run_check(args.root))
