from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_PRICING_COLUMNS = [
    "model_id",
    "model_name",
    "exact_version",
    "provider",
    "price_date",
    "input_price",
    "output_price",
    "cached_input_price",
    "price_unit",
    "deployment",
    "source_type",
    "source_url",
    "human_verified",
    "notes",
]
REQUIRED_UTILITY_COLUMNS = ["model_id", "model_name", "scenario", "utility"]
REQUIRED_WORKLOAD_COLUMNS = ["scenario", "scenario_name", "n_calls", "input_tokens", "output_tokens", "input_output_ratio", "workload_level", "source_or_rationale", "notes"]
PRICE_UNIT = "USD / 1M tokens"


def _issue(issues, severity, file, field, model_id, message):
    issues.append({"severity": severity, "file": file, "field": field, "model_id": model_id, "message": message})


def _num(series):
    return pd.to_numeric(series.replace({"NA": pd.NA, "": pd.NA}), errors="coerce")


def validate_q3_data(pricing_path: Path, workload_path: Path, utility_path: Path, q2_master_path: Path, report_path: Path) -> pd.DataFrame:
    issues = []
    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    workload = pd.read_csv(workload_path, keep_default_na=False)
    q2_master = pd.read_csv(q2_master_path, keep_default_na=False) if q2_master_path.exists() else pd.DataFrame()
    utility = pd.read_csv(utility_path, keep_default_na=False) if utility_path.exists() else pd.DataFrame(columns=REQUIRED_UTILITY_COLUMNS)

    for col in REQUIRED_PRICING_COLUMNS:
        if col not in pricing.columns:
            _issue(issues, "ERROR", str(pricing_path), col, "", "Missing required pricing column")
    for col in REQUIRED_WORKLOAD_COLUMNS:
        if col not in workload.columns:
            _issue(issues, "ERROR", str(workload_path), col, "", "Missing required workload column")
    for col in REQUIRED_UTILITY_COLUMNS:
        if col not in utility.columns:
            _issue(issues, "ERROR", str(utility_path), col, "", "Missing required utility column")

    if "model_id" in pricing.columns:
        dupes = pricing[pricing["model_id"].duplicated(keep=False)]
        for _, row in dupes.iterrows():
            _issue(issues, "ERROR", str(pricing_path), "model_id", row["model_id"], "Duplicate pricing model_id")

    if not q2_master.empty and "model_id" in pricing.columns:
        q2_ids = set(q2_master["model_id"])
        q3_ids = set(pricing["model_id"])
        for model_id in sorted(q2_ids - q3_ids):
            _issue(issues, "ERROR", str(pricing_path), "model_id", model_id, "Q2 model missing from Q3 pricing table")
        for model_id in sorted(q3_ids - q2_ids):
            _issue(issues, "ERROR", str(pricing_path), "model_id", model_id, "Q3 pricing model not present in Q2 master table")
        merged = pricing.merge(q2_master[["model_id", "model"]], on="model_id", how="inner")
        mismatched = merged[merged["model_name"] != merged["model"]]
        for _, row in mismatched.iterrows():
            _issue(issues, "WARNING", str(pricing_path), "model_name", row["model_id"], f"Model name differs from Q2: {row['model_name']} != {row['model']}")

    if "price_unit" in pricing.columns:
        bad_unit = pricing[pricing["price_unit"] != PRICE_UNIT]
        for _, row in bad_unit.iterrows():
            _issue(issues, "ERROR", str(pricing_path), "price_unit", row.get("model_id", ""), "Price unit must be USD / 1M tokens")

    for col in ["input_price", "output_price", "cached_input_price"]:
        if col in pricing.columns:
            nums = _num(pricing[col])
            negative = pricing[nums < 0]
            for _, row in negative.iterrows():
                _issue(issues, "ERROR", str(pricing_path), col, row.get("model_id", ""), "Price must be non-negative")
            missing = pricing[nums.isna()]
            for _, row in missing.iterrows():
                severity = "WARNING" if col == "cached_input_price" else "BLOCKING_INPUT_MISSING"
                _issue(issues, severity, str(pricing_path), col, row.get("model_id", ""), "Price is missing; final Q3 cost and Pareto run cannot use this model")

    for col in ["price_date", "source_url", "exact_version"]:
        if col in pricing.columns:
            missing = pricing[pricing[col].isin(["", "NA"])]
            for _, row in missing.iterrows():
                _issue(issues, "BLOCKING_INPUT_MISSING", str(pricing_path), col, row.get("model_id", ""), f"{col} is missing")

    if {"model_id", "price_date"}.issubset(pricing.columns):
        multi_dates = pricing.groupby("model_id")["price_date"].nunique(dropna=False)
        for model_id, count in multi_dates.items():
            if count > 1:
                _issue(issues, "WARNING", str(pricing_path), "price_date", model_id, "Multiple price dates found for the same model")

    for col in ["n_calls", "input_tokens", "output_tokens"]:
        if col in workload.columns:
            nums = pd.to_numeric(workload[col], errors="coerce")
            bad = workload[nums <= 0]
            for _, row in bad.iterrows():
                _issue(issues, "ERROR", str(workload_path), col, row.get("scenario", ""), "Workload value must be positive")

    if not utility.empty and "utility" in utility.columns:
        util = pd.to_numeric(utility["utility"], errors="coerce")
        supplied = utility[utility["utility"].astype(str).str.strip() != ""]
        bad = supplied[util.loc[supplied.index].isna() | (util.loc[supplied.index] < 0) | (util.loc[supplied.index] > 100)]
        for _, row in bad.iterrows():
            _issue(issues, "ERROR", str(utility_path), "utility", row.get("model_id", ""), "Utility must be numeric and in [0, 100]")
        if supplied.empty:
            _issue(issues, "BLOCKING_INPUT_MISSING", str(utility_path), "utility", "", "No Q2 scenario utility values supplied")
    else:
        _issue(issues, "BLOCKING_INPUT_MISSING", str(utility_path), "utility", "", "No Q2 scenario utility file found")

    report = pd.DataFrame(issues, columns=["severity", "file", "field", "model_id", "message"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path, index=False)
    hard = report[report["severity"] == "ERROR"] if not report.empty else pd.DataFrame()
    if not hard.empty:
        raise ValueError(f"Q3 validation failed with {len(hard)} ERROR issue(s). See {report_path}")
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    validate_q3_data(
        root / "q3" / "data" / "model_pricing.csv",
        root / "q3" / "data" / "workload_config.csv",
        root / "q3" / "data" / "scenario_utility.csv",
        root / "q2" / "data" / "q2_model_master_table.csv",
        root / "q3" / "outputs" / "diagnostics" / "q3_data_validation_report.csv",
    )

