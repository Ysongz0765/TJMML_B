from __future__ import annotations

from pathlib import Path

import pandas as pd


def run_audit(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[2]
    tables = root / "q3" / "outputs" / "tables"
    paper = (root / "q3" / "paper" / "q3_results.tex").read_text(encoding="utf-8")
    discussion = (root / "q3" / "paper" / "q3_discussion.tex").read_text(encoding="utf-8")
    pareto = pd.read_csv(tables / "pareto_results_final.csv", keep_default_na=False)
    budget = pd.read_csv(tables / "budget_switch_points_final.csv", keep_default_na=False)
    icer = pd.read_csv(tables / "icer_results_final.csv", keep_default_na=False)
    fit = pd.read_csv(tables / "cost_performance_fit_final.csv", keep_default_na=False)
    probability_table = pd.read_csv(tables / "pareto_probability_final.csv", keep_default_na=False)

    checks: list[tuple[str, bool, str]] = []
    aliases = {
        "deepseek_v4_flash_max": "DeepSeek-V4-Flash Max",
        "deepseek_v4_pro_max": "DeepSeek-V4-Pro Max",
        "kimi_k3_max": "Kimi K3",
        "qwen3_8_max": "Qwen3.8-Max",
        "gemini_3_1_pro_high": "Gemini-3.1-Pro",
        "gpt_5_6_sol_max": "GPT-5.6 Sol",
    }
    for scenario, group in pareto.groupby("scenario"):
        for model_id in group.loc[group["pareto"].astype(str).str.upper() == "TRUE", "model_id"]:
            label = aliases.get(model_id, model_id)
            checks.append((f"Pareto {scenario}/{model_id}", label in paper, label))

    thresholds = sorted(set(pd.to_numeric(budget["budget_threshold"], errors="coerce").dropna()))
    for threshold in thresholds:
        token = f"{threshold:.6f}"
        checks.append((f"Budget threshold {token}", token in paper, token))

    for value in pd.to_numeric(icer["icer"], errors="coerce"):
        token = f"{value:.6f}"
        checks.append((f"ICER {token}", token in paper, token))

    for scenario, group in fit[fit["subset"] == "all_models"].groupby("scenario"):
        best_aicc = group.loc[group["aicc"].idxmin(), "fit_model"]
        checks.append((f"Best AICc fit {scenario}", str(best_aicc) in paper, str(best_aicc)))
    checks.extend(
        [
            ("Sensitivity statement", "nominal Pareto" in paper and r"\pm5\%/\pm10\%" in paper, "grid conclusion"),
            ("Fable exclusion wording", "fallback" in discussion and "严格等价比较" in discussion, "PARTIAL wording"),
            ("GLM exclusion wording", "GLM-5.2" in discussion and "公开标准 API" in discussion, "MISSING wording"),
        ]
    )
    for model_id, scenario, expected_probability in [
        ("deepseek_v4_flash_max", "Coding", 1.0),
        ("deepseek_v4_pro_max", "Coding", 0.9465),
        ("kimi_k3_max", "Coding", 0.6150),
        ("qwen3_8_max", "General", 1.0),
        ("gpt_5_6_sol_max", "General", 0.9765),
    ]:
        row = probability_table[
            (probability_table["model_id"] == model_id) & (probability_table["scenario"] == scenario)
        ].iloc[0]
        token = f"{float(row['pareto_probability']):.4f}"
        checks.append((f"Bootstrap {model_id}/{scenario}", token in paper, token))

    passed = all(item[1] for item in checks)
    report = root / "q3" / "outputs" / "diagnostics" / "paper_result_consistency_audit.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Paper Result Consistency Audit",
        "",
        "The checks below compare paper-ready text with the final CSV tables.",
        "",
        f"`Q3_PAPER_CONSISTENCY_AUDIT = {'PASS' if passed else 'FAIL'}`",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]
    for name, status, evidence in checks:
        lines.append(f"| {name} | {'PASS' if status else 'FAIL'} | `{evidence}` |")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"passed": passed, "checks": len(checks)}


if __name__ == "__main__":
    import json

    print(json.dumps(run_audit(), indent=2))
