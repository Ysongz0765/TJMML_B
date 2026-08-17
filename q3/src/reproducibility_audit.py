from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype


FINAL_FILES = [
    "scenario_costs_final.csv",
    "pareto_results_final.csv",
    "budget_switch_points_final.csv",
    "icer_results_final.csv",
    "cost_performance_fit_final.csv",
    "sensitivity_summary_final.csv",
    "pareto_probability_final.csv",
]

FROZEN_INPUTS = [
    "scenario_utility.csv",
    "scenario_utility_bootstrap.csv",
    "q2_interface_provenance.json",
    "model_pricing.csv",
    "pricing_audit.csv",
    "pricing_human_check.csv",
    "workload_config.csv",
]


def _copy_frozen_inputs(root: Path, temp_root: Path) -> None:
    data = temp_root / "q3" / "data"
    data.mkdir(parents=True, exist_ok=True)
    for name in FROZEN_INPUTS:
        shutil.copy2(root / "q3" / "frozen" / "v1.0" / name, data / name)
    master = temp_root / "q2" / "data"
    master.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "q2" / "data" / "q2_model_master_table.csv", master / "q2_model_master_table.csv")


def _compare_csv(expected: Path, actual: Path) -> dict:
    left = pd.read_csv(expected, keep_default_na=False)
    right = pd.read_csv(actual, keep_default_na=False)
    result = {
        "row_count_match": len(left) == len(right),
        "column_match": list(left.columns) == list(right.columns),
        "max_absolute_difference": 0.0,
        "max_relative_difference": 0.0,
        "key_match": False,
    }
    if not result["row_count_match"] or not result["column_match"]:
        return result
    key_columns = [column for column in ["model_id", "scenario", "analysis", "parameter", "fit_model", "subset"] if column in left.columns]
    left = left.sort_values(key_columns).reset_index(drop=True) if key_columns else left
    right = right.sort_values(key_columns).reset_index(drop=True) if key_columns else right
    result["key_match"] = left[key_columns].equals(right[key_columns]) if key_columns else True
    for column in left.columns:
        if is_bool_dtype(left[column]) or is_bool_dtype(right[column]):
            if not left[column].astype(bool).equals(right[column].astype(bool)):
                result["max_absolute_difference"] = np.inf
                result["max_relative_difference"] = np.inf
            continue
        left_num = pd.to_numeric(left[column], errors="coerce")
        right_num = pd.to_numeric(right[column], errors="coerce")
        if left_num.notna().any() or right_num.notna().any():
            difference = (left_num - right_num).abs()
            relative = (difference / left_num.abs()).replace([np.inf, -np.inf], np.nan)
            result["max_absolute_difference"] = max(result["max_absolute_difference"], float(difference.max(skipna=True) or 0.0))
            result["max_relative_difference"] = max(result["max_relative_difference"], float(relative.max(skipna=True) or 0.0))
        elif not left[column].astype(str).equals(right[column].astype(str)):
            result["max_absolute_difference"] = np.inf
            result["max_relative_difference"] = np.inf
    return result


def run_reproducibility_audit(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "q3" / "src"))
    from finalize_outputs import finalize_outputs
    from run_q3 import run

    with tempfile.TemporaryDirectory(prefix="q3_frozen_repro_") as temp_dir:
        temp_root = Path(temp_dir)
        _copy_frozen_inputs(root, temp_root)
        status = run(temp_root)
        finalize_outputs(temp_root)
        rows = {}
        for name in FINAL_FILES:
            rows[name] = _compare_csv(
                root / "q3" / "frozen" / "v1.0" / name,
                temp_root / "q3" / "outputs" / "tables" / name,
            )
        passed = bool(
            status.get("Q3_FINAL_RESULTS_READY")
            and all(
                item["row_count_match"]
                and item["column_match"]
                and item["key_match"]
                and item["max_absolute_difference"] == 0.0
                for item in rows.values()
            )
        )
    report = root / "q3" / "outputs" / "diagnostics" / "q3_reproducibility_audit.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Q3 Reproducibility Audit",
        "",
        "The frozen input files under `q3/frozen/v1.0/` were copied to an isolated",
        "temporary root and executed through the Q3 runner and final-output",
        "formatter. No current working-tree input was used by the isolated run.",
        "",
        f"`Q3_REPRODUCIBILITY_AUDIT = {'PASS' if passed else 'FAIL'}`",
        "",
        "| Final table | Rows | Row count | Columns | Keys | Max abs diff | Max rel diff |",
        "|---|---:|---|---|---|---:|---:|",
    ]
    for name, item in rows.items():
        row_count = pd.read_csv(root / "q3" / "frozen" / "v1.0" / name, keep_default_na=False).shape[0]
        lines.append(
            f"| `{name}` | {row_count} | {item['row_count_match']} | {item['column_match']} | "
            f"{item['key_match']} | {item['max_absolute_difference']:.6g} | "
            f"{item['max_relative_difference']:.6g} |"
        )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"passed": passed, "tables": len(rows)}


if __name__ == "__main__":
    import json

    print(json.dumps(run_reproducibility_audit(), indent=2))
