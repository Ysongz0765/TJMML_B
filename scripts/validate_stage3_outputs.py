from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "data/final/final_modeling_matrix.xlsx",
    "data/processed/final_modeling_benchmark_manifest.xlsx",
    "data/processed/benchmark_family_manifest.xlsx",
    "data/processed/livebench_independence_audit.xlsx",
    "data/processed/source_concentration_analysis.xlsx",
    "data/processed/leave_one_source_out_diagnostics.xlsx",
    "data/processed/bridge_evidence_report.xlsx",
    "data/processed/kimi_evidence_audit.xlsx",
    "data/processed/benchmark_redundancy_audit.xlsx",
    "data/processed/spearman_missing_aware.xlsx",
    "data/processed/family_effect_sensitivity.xlsx",
    "data/processed/bt_identifiability_test.xlsx",
    "data/processed/livebench_dependency_sensitivity.xlsx",
    "data/processed/human_verification_final_checklist.xlsx",
    "data/processed/modeling_readiness_gate.xlsx",
    "reports/modeling_readiness_report.md",
    "data/final/LLM_Benchmark_Evaluation_Dataset.xlsx",
    "data/raw/raw_benchmark_data.csv",
    "data/raw/raw_benchmark_data.xlsx",
    "data/processed/source_registry.xlsx",
]


def main() -> None:
    raw = pd.read_csv(ROOT / "data/raw/raw_benchmark_data.csv", dtype=str, keep_default_na=False)
    matrix = pd.read_csv(ROOT / "data/final/final_modeling_matrix.csv", na_values=["NA"])
    bundle = json.loads((ROOT / "data/processed/stage3_analysis_bundle.json").read_text(encoding="utf-8"))
    workbook_qc = json.loads((ROOT / "reports/stage3_workbook_qc.json").read_text(encoding="utf-8"))
    selected = raw[raw["selected_for_final_modeling"].str.lower().eq("true")].copy()
    setting_columns = [column for column in matrix if column.startswith("S_")]
    lineage = pd.DataFrame(bundle["tables"]["Lineage"])

    strict_keys = ["model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed",
                   "browsing_allowed", "reasoning_setting", "pass_k_setting", "prompting_setting", "test_protocol"]
    conflicts = 0
    for _, group in raw.groupby(strict_keys, dropna=False):
        if group["source_id"].nunique() > 1 and group["raw_score"].nunique() > 1:
            conflicts += 1

    required_sheets = {
        "FinalModelingMatrix", "ModelingBenchmarkManifest", "BenchmarkFamilies", "LiveBenchAudit",
        "SourceConcentration", "BridgeEvidence", "KimiAudit", "RedundancyAudit", "SpearmanQC",
        "BTReadiness", "ModelingReadinessGate",
    }
    figure_dir = ROOT / "reports/figures/stage3"
    png_figures = list(figure_dir.glob("*.png"))
    svg_figures = list(figure_dir.glob("*.svg"))
    readiness_text = (ROOT / "reports/modeling_readiness_report.md").read_text(encoding="utf-8")
    checks = {
        "required_files_present": all((ROOT / path).is_file() and (ROOT / path).stat().st_size > 0 for path in REQUIRED),
        "raw_record_count_242": len(raw) == 242,
        "selected_cell_count_164": len(selected) == 164,
        "matrix_shape_10_by_21": len(matrix) == 10 and len(setting_columns) == 21,
        "matrix_nonempty_count_164": int(matrix[setting_columns].notna().sum().sum()) == 164,
        "lineage_count_164": len(lineage) == 164 and lineage["matrix_cell_key"].nunique() == 164,
        "selected_source_id_complete": selected["source_id"].str.strip().ne("").all(),
        "selected_url_complete": selected["source_url"].str.match(r"^https?://").all(),
        "selected_model_setting_unique": not selected.duplicated(["model_id", "setting_id"]).any(),
        "no_human_verification_fabrication": raw["human_verified"].str.upper().eq("FALSE").all(),
        "strict_conflict_groups_zero": conflicts == 0,
        "total_workbook_31_sheets": workbook_qc["sheetCount"] == 31,
        "required_stage3_sheets_present": required_sheets.issubset(workbook_qc["sheetNames"]),
        "formula_error_scan_zero": "matched 0 entries" in workbook_qc["errorScan"],
        "paper_figures_21_png_and_svg": len(png_figures) >= 21 and len(svg_figures) >= 21,
        "readiness_report_answers_12_questions": all(f"## {index}." in readiness_text for index in range(1, 13)),
        "status_pending_human_signoff": bundle["metadata"]["status"] == "MODELING_READY_PENDING_HUMAN_SIGNOFF",
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed": failed,
        "metrics": {
            "raw_records": len(raw), "selected_cells": len(selected), "core_models": len(matrix),
            "exact_settings": len(setting_columns), "matrix_nonempty": int(matrix[setting_columns].notna().sum().sum()),
            "strict_conflict_groups": conflicts, "human_verified_true": int(raw["human_verified"].str.upper().eq("TRUE").sum()),
            "total_workbook_sheets": workbook_qc["sheetCount"],
            "png_figures": len(png_figures), "svg_figures": len(svg_figures),
        },
    }
    output = ROOT / "reports/stage3_final_qc_summary.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
