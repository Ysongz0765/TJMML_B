import pandas as pd

from cohort import build_analysis_cohort, full_model_ids
from run_q3 import _main_analysis_ready, _validate_q2_bootstrap, _validate_q2_nominal


MODEL_IDS = {"full", "partial", "missing"}


def test_cohort_keeps_partial_and_missing_models_visible():
    pricing = pd.DataFrame(
        [
            {"model_id": "full", "model_name": "Full", "input_price": 1.0, "output_price": 2.0, "pricing_status": "READY"},
            {"model_id": "partial", "model_name": "Partial", "input_price": 1.0, "output_price": 2.0, "pricing_status": "SPECIAL_CASE"},
            {"model_id": "missing", "model_name": "Missing", "input_price": "NA", "output_price": "NA", "pricing_status": "MISSING"},
        ]
    )
    audit = pd.DataFrame(
        [
            {"model_id": "full", "pricing_status": "READY", "fallback_issue": "FALSE", "sku_mapping_status": "EXACT", "config_mapping_status": "SUPPORTED_CONFIG"},
            {"model_id": "partial", "pricing_status": "SPECIAL_CASE", "fallback_issue": "TRUE", "sku_mapping_status": "EXACT", "config_mapping_status": "FALLBACK_DEPENDENT"},
            {"model_id": "missing", "pricing_status": "MISSING", "fallback_issue": "FALSE", "sku_mapping_status": "EXACT", "config_mapping_status": "SUPPORTED_CONFIG"},
        ]
    )
    cohort = build_analysis_cohort(pricing, audit)
    assert cohort["cost_observability"].astype(str).tolist() == ["FULL", "PARTIAL", "MISSING"]
    assert full_model_ids(cohort) == ["full"]
    assert cohort.loc[cohort["model_id"] == "partial", "included_in_main_pareto"].item() is False
    assert cohort.loc[cohort["model_id"] == "missing", "included_in_main_pareto"].item() is False


def test_q2_nominal_interface_requires_30_rows_and_three_scenarios():
    nominal = pd.DataFrame(
        [
            {"model_id": model_id, "model_name": model_id, "scenario": scenario, "utility": float(index)}
            for scenario in ["Research", "General", "Coding"]
            for index, model_id in enumerate(sorted(MODEL_IDS), start=1)
        ]
    )
    result = _validate_q2_nominal(nominal, MODEL_IDS)
    assert result["valid"] is False
    assert result["rows"] == 9
    assert result["models"] == 3


def test_q2_bootstrap_interface_rejects_duplicate_keys():
    bootstrap = pd.DataFrame(
        [
            {"bootstrap_id": 0, "model_id": "full", "scenario": "Research", "utility": 0.5},
            {"bootstrap_id": 0, "model_id": "full", "scenario": "Research", "utility": 0.5},
        ]
    )
    result = _validate_q2_bootstrap(bootstrap, MODEL_IDS)
    assert result["valid"] is False
    assert result["duplicates"] == 1


def test_runner_allows_full_cohort_when_partial_and_missing_exist():
    cohort = pd.DataFrame(
        [{"model_id": f"full_{index}", "cost_observability": "FULL"} for index in range(8)]
        + [
            {"model_id": "partial", "cost_observability": "PARTIAL"},
            {"model_id": "missing", "cost_observability": "MISSING"},
        ]
    )
    assert _main_analysis_ready(True, True, [f"full_{index}" for index in range(8)], cohort, False) is True
    assert _main_analysis_ready(True, True, ["full"], cohort, True) is False
