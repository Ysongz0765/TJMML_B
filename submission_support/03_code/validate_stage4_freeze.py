from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "raw_benchmark_data.csv"
MATRIX_PATH = ROOT / "data" / "final" / "final_modeling_matrix.csv"
BUNDLE_PATH = ROOT / "data" / "processed" / "stage4_finalization_bundle.json"
FROZEN = ROOT / "frozen" / "v1.0"
REPORT_PATH = ROOT / "reports" / "stage4_final_qc_summary.json"


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper().isin({"TRUE", "1", "YES"})


def finite_or_missing(value: object) -> bool:
    if pd.isna(value) or str(value).strip().upper() == "NA":
        return True
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False)
matrix = pd.read_csv(MATRIX_PATH, dtype=str, keep_default_na=False)
bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
tables = {name: pd.DataFrame(rows, columns=bundle["columns"][name]) for name, rows in bundle["tables"].items()}
lineage = tables["Lineage"]
traceability = tables["FinalTraceability"]
gate = tables["ModelingReadinessGate"]
manifest = tables["ModelingBenchmarkManifest"]
sources = tables["Sources"]

selected_mask = as_bool(raw["selected_for_final_modeling"])
human_mask = as_bool(raw["human_verified"])
selected = raw[selected_mask].copy()
nonselected = raw[~selected_mask].copy()
setting_columns = list(manifest["selected_setting"])

checks: dict[str, dict[str, object]] = {}


def check(name: str, passed: bool, detail: object) -> None:
    checks[name] = {"passed": bool(passed), "detail": detail}


check("raw_record_count", len(raw) == 242, len(raw))
check("selected_record_count", len(selected) == 164, len(selected))
check("selected_human_verified", int(human_mask[selected_mask].sum()) == 164, int(human_mask[selected_mask].sum()))
check("selected_human_unverified", int((~human_mask[selected_mask]).sum()) == 0, int((~human_mask[selected_mask]).sum()))
check("nonselected_not_promoted", int(human_mask[~selected_mask].sum()) == 0, int(human_mask[~selected_mask].sum()))

expected_fields = {
    "verification_method": "MANUAL_REVIEW_BY_TEAM",
    "verification_status": "VERIFIED",
    "verification_basis": "Team members manually checked model version, benchmark setting, metric, score and original source.",
    "human_verification_note": "Manual verification was completed by the competition team before Stage 4. Stage 4 only records the completed verification status into the dataset.",
    "verification_recorded_date": "2026-08-17",
}
for field, expected in expected_fields.items():
    mismatches = int((selected[field] != expected).sum())
    check(f"verification_field_{field}", mismatches == 0, {"mismatches": mismatches, "expected": expected})

check("selected_source_id_complete", bool(selected["source_id"].str.strip().ne("").all()), int(selected["source_id"].str.strip().eq("").sum()))
check("selected_source_url_complete", bool(selected["source_url"].str.strip().ne("").all()), int(selected["source_url"].str.strip().eq("").sum()))
registered = set(sources["source_id"])
unregistered = sorted(set(selected["source_id"]) - registered)
check("selected_sources_registered", not unregistered, unregistered)

duplicate_keys = int(selected.duplicated(["model_id", "setting_id"], keep=False).sum())
check("unique_model_setting_selection", duplicate_keys == 0, duplicate_keys)
check("selected_composite_excluded", int(as_bool(selected["is_composite_index"]).sum()) == 0, int(as_bool(selected["is_composite_index"]).sum()))
check("selected_conflict_free", int(as_bool(selected["conflict_flag"]).sum()) == 0, int(as_bool(selected["conflict_flag"]).sum()))

protocol_inconsistency = []
for setting_id, group in selected.groupby("setting_id"):
    for field in ["benchmark_version", "metric_name", "tools_allowed", "browsing_allowed", "test_protocol"]:
        values = sorted(set(group[field].astype(str)))
        if len(values) > 1:
            protocol_inconsistency.append({"setting_id": setting_id, "field": field, "values": values})
check("exact_setting_protocol_lock", not protocol_inconsistency, protocol_inconsistency)

check("matrix_shape", matrix.shape == (10, 25), list(matrix.shape))
check("setting_count", len(setting_columns) == 21 and len(set(setting_columns)) == 21, len(setting_columns))
matrix_nonmissing = int(matrix[setting_columns].apply(lambda col: col.astype(str).str.strip().str.upper().ne("NA") & col.astype(str).str.strip().ne("")).sum().sum())
check("matrix_nonmissing_cells", matrix_nonmissing == 164, matrix_nonmissing)

raw_map = {(row.model_id, row.setting_id): float(row.raw_score) for row in selected.itertuples(index=False)}
value_mismatches = []
matrix_keys = set()
for row in matrix.itertuples(index=False):
    row_dict = row._asdict()
    for setting_id in setting_columns:
        value = str(row_dict[setting_id]).strip()
        if not value or value.upper() == "NA":
            continue
        key = (row_dict["model_id"], setting_id)
        matrix_keys.add(key)
        if key not in raw_map or not math.isclose(float(value), raw_map[key], rel_tol=0.0, abs_tol=1e-12):
            value_mismatches.append({"key": key, "matrix": value, "raw": raw_map.get(key)})
missing_matrix_keys = sorted(set(raw_map) - matrix_keys)
check("matrix_rebuild_exact", not value_mismatches and not missing_matrix_keys,
      {"value_mismatches": value_mismatches[:20], "missing_keys": missing_matrix_keys[:20]})

check("matrix_finite_values", bool(matrix[setting_columns].map(finite_or_missing).all().all()), "No NaN/Inf/non-numeric nonmissing value")
check("lineage_count", len(lineage) == 164 and lineage["record_id"].nunique() == 164, {"rows": len(lineage), "records": lineage["record_id"].nunique()})
check("traceability_count", len(traceability) == 164, len(traceability))
trace_pass = as_bool(traceability["traceability_pass"]) if "traceability_pass" in traceability else pd.Series(False, index=traceability.index)
check("traceability_100_percent", int(trace_pass.sum()) == 164, int(trace_pass.sum()))
trace_human = as_bool(traceability["human_verified"])
check("traceability_human_verified", int(trace_human.sum()) == 164, int(trace_human.sum()))

check("gate_status", bundle["metadata"].get("status") == "FULLY_MODELING_READY", bundle["metadata"].get("status"))
check("gate_all_passed", bool(as_bool(gate["passed"]).all()), gate.loc[~as_bool(gate["passed"]), "gate_id"].tolist())
check("freeze_version", bundle["metadata"].get("data_freeze_version") == "v1.0", bundle["metadata"].get("data_freeze_version"))
check("freeze_date", bundle["metadata"].get("data_freeze_date") == "2026-08-17", bundle["metadata"].get("data_freeze_date"))

required_frozen = [
    "final_modeling_matrix_v1.0.xlsx", "raw_benchmark_data_v1.0.xlsx", "source_registry_v1.0.xlsx",
    "final_modeling_benchmark_manifest_v1.0.xlsx", "benchmark_family_manifest_v1.0.xlsx",
    "model_pool_v1.0.xlsx", "human_verification_log_v1.0.xlsx", "modeling_readiness_gate_v1.0.xlsx",
    "data_freeze_manifest_v1.0.xlsx", "SHA256SUMS_v1.0.txt", "README.md",
]
missing_frozen = [name for name in required_frozen if not (FROZEN / name).exists()]
check("required_frozen_files", not missing_frozen, missing_frozen)

hash_mismatches = []
hash_file = FROZEN / "SHA256SUMS_v1.0.txt"
if hash_file.exists():
    for line in hash_file.read_text(encoding="utf-8").splitlines():
        expected, filename = line.split("  ", 1)
        target = FROZEN / filename
        actual = file_hash(target) if target.exists() else "MISSING"
        if actual != expected:
            hash_mismatches.append({"filename": filename, "expected": expected, "actual": actual})
check("sha256_integrity", not hash_mismatches, hash_mismatches)

figure_dir = ROOT / "reports" / "figures" / "stage3"
png_count = len(list(figure_dir.glob("*.png")))
svg_count = len(list(figure_dir.glob("*.svg")))
check("figure_rebuild_count", png_count == 21 and svg_count == 21, {"png": png_count, "svg": svg_count})

paper_required = [
    "paper_data_source_section.md", "paper_table_data_sources.xlsx", "paper_table_data_sources.md",
    "appendix_A_benchmark_system.md", "appendix_A_benchmark_system.xlsx",
    "appendix_B_source_mapping.md", "appendix_B_source_mapping.xlsx", "source_reference_mapping.xlsx",
    "paper_references_data_sources.md", "appendix_C_model_versions.md", "appendix_C_model_versions.xlsx",
    "appendix_D_data_rules.md", "appendix_E_supporting_materials.md",
]
missing_paper = [name for name in paper_required if not (ROOT / "paper_materials" / name).exists()]
check("paper_materials_complete", not missing_paper, missing_paper)

passed = all(item["passed"] for item in checks.values())
summary = {
    "status": "PASS" if passed else "FAIL",
    "dataset_status": bundle["metadata"].get("status"),
    "freeze_version": "v1.0",
    "freeze_date": "2026-08-17",
    "selected_records": len(selected),
    "human_verified_selected": int(human_mask[selected_mask].sum()),
    "matrix_nonmissing": matrix_nonmissing,
    "traceability_rate": float(trace_pass.mean()) if len(trace_pass) else 0.0,
    "checks_passed": sum(item["passed"] for item in checks.values()),
    "checks_total": len(checks),
    "checks": checks,
}
REPORT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key != "checks"}, ensure_ascii=False, indent=2))
if not passed:
    raise SystemExit(1)
