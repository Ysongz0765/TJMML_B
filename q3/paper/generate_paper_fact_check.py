from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd


SCENARIOS = ["Research", "General", "Coding"]


def _money(value: object) -> str:
    quantized = Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return format(quantized, "f")


def _pct(value: object) -> str:
    quantized = Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return format(quantized, "f")


def _optional_number(value: object) -> str:
    if value is None or pd.isna(value) or str(value).strip() == "":
        return "NA"
    return f"{float(value):.6f}"


def build_fact_check(root: Path) -> Path:
    freeze = root / "q3" / "frozen" / "v1.0"
    paper = root / "q3" / "paper"
    names = pd.read_csv(paper / "q3_model_display_names.csv")
    label = dict(zip(names["model_id"], names["display_name"]))
    cohort = pd.read_csv(freeze / "q3_model_analysis_cohort.csv", keep_default_na=False)
    workload = pd.read_csv(freeze / "workload_config.csv", keep_default_na=False)
    pareto = pd.read_csv(freeze / "pareto_results_final.csv", keep_default_na=False)
    budget = pd.read_csv(freeze / "budget_switch_points_final.csv", keep_default_na=False)
    icer = pd.read_csv(freeze / "icer_results_final.csv", keep_default_na=False)
    fit = pd.read_csv(freeze / "cost_performance_fit_final.csv", keep_default_na=False)
    sensitivity = pd.read_csv(freeze / "sensitivity_summary_final.csv", keep_default_na=False)
    probability = pd.read_csv(freeze / "pareto_probability_final.csv", keep_default_na=False)

    lines = [
        "# Q3 Paper Fact Check",
        "",
        "This table is generated from `q3/frozen/v1.0/`; it is the numerical "
        "source of truth for the standalone manuscript.",
        "",
        "## Cohort",
        "",
        f"- FULL models: {', '.join(label[x] for x in cohort.loc[cohort.cost_observability == 'FULL', 'model_id'])}",
        f"- PARTIAL models: {', '.join(label[x] for x in cohort.loc[cohort.cost_observability == 'PARTIAL', 'model_id'])}",
        f"- MISSING models: {', '.join(label[x] for x in cohort.loc[cohort.cost_observability == 'MISSING', 'model_id'])}",
        f"- Main cohort size: {int((cohort.cost_observability == 'FULL').sum())}",
        "",
        "## Baseline Workloads",
        "",
        "| Scenario | N | Input tokens | Billable output tokens | Output/input ratio |",
        "|---|---:|---:|---:|---:|",
    ]
    baseline = workload[workload["workload_level"] == "baseline_template"]
    for _, row in baseline.iterrows():
        lines.append(
            f"| {row.scenario} | {int(row.n_calls)} | {int(row.input_tokens)} | "
            f"{int(row.output_tokens)} | {float(row.input_output_ratio):.4g} |"
        )

    lines.extend(["", "## Pareto Results", ""])
    for scenario in SCENARIOS:
        group = pareto[pareto.scenario == scenario]
        front = group[group.pareto.astype(str).str.upper() == "TRUE"]
        dominated = group[group.pareto.astype(str).str.upper() != "TRUE"]
        lines.extend(
            [
                f"### {scenario}",
                f"- Pareto models: {', '.join(label[x] for x in front.model_id)}",
                f"- Dominated models: {', '.join(label[x] for x in dominated.model_id)}",
                "| Model | Utility | Cost (USD) | Pareto |",
                "|---|---:|---:|---|",
            ]
        )
        for _, row in group.sort_values("cost").iterrows():
            lines.append(
                f"| {label[row.model_id]} | {float(row.utility):.6f} | "
                f"{_money(row.cost)} | {'Yes' if str(row.pareto).upper() == 'TRUE' else 'No'} |"
            )
        lines.append("")

    lines.extend(["## Budget Switching", ""])
    for scenario in SCENARIOS:
        group = budget[budget.scenario == scenario]
        thresholds = " → ".join(_money(x) for x in group.budget_threshold)
        models = " → ".join(label[x] for x in group.optimal_model_after)
        lines.extend([f"- {scenario}: thresholds = {thresholds}; model sequence = {models}"])

    lines.extend(
        [
            "",
            "## ICER",
            "",
            "| Scenario | From | To | Delta cost | Delta utility | ICER |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for _, row in icer.iterrows():
        lines.append(
            f"| {row.scenario} | {label[row.from_model]} | {label[row.to_model]} | "
            f"{_money(row.delta_cost)} | {float(row.delta_utility):.6f} | {_money(row.icer)} |"
        )

    lines.extend(
        [
            "",
            "## Cost--Performance Fits",
            "",
            "| Scenario | Subset | Model | R2 | AIC | AICc | BIC | LOOCV error | Warning |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in fit.iterrows():
        lines.append(
            f"| {row.scenario} | {row.subset} | {row.fit_model} | {float(row.r2):.6f} | "
            f"{float(row.aic):.6f} | {_optional_number(row.aicc)} | "
            f"{float(row.bic):.6f} | {_optional_number(row.loocv_error)} | "
            f"{row.fit_warning or 'None'} |"
        )

    lines.extend(["", "## Sensitivity", ""])
    for _, row in sensitivity.iterrows():
        lines.append(
            f"- {row.scenario}/{row.analysis}: {row.conclusion}; "
            f"nominal-member retention = {float(row.pareto_member_retention_rate):.4f}; "
            f"all-members retained = {float(row.all_nominal_members_retained_rate):.4f}; "
            f"tested points = {int(row.parameter_points)}."
        )

    lines.extend(
        [
            "",
            "## Bootstrap Pareto Probability",
            "",
            "| Model | Research | General | Coding |",
            "|---|---:|---:|---:|",
        ]
    )
    probability_model_ids = [
        model_id for model_id in names.model_id if model_id in set(probability.model_id)
    ]
    for model_id in probability_model_ids:
        values = []
        for scenario in SCENARIOS:
            value = probability[
                (probability.model_id == model_id) & (probability.scenario == scenario)
            ].iloc[0].pareto_probability
            values.append(_pct(value))
        lines.append(f"| {label[model_id]} | {values[0]} | {values[1]} | {values[2]} |")

    output = paper / "q3_paper_fact_check.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(build_fact_check(args.root))
