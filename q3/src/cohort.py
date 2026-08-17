from __future__ import annotations

from pathlib import Path

import pandas as pd


COHORT_ORDER = ["FULL", "PARTIAL", "MISSING"]


def build_analysis_cohort(
    pricing: pd.DataFrame,
    pricing_audit: pd.DataFrame,
    utilities: pd.DataFrame | None = None,
    pricing_human_check: pd.DataFrame | None = None,
) -> pd.DataFrame:
    price = pricing.copy()
    audit = pricing_audit.copy()
    price["input_price_num"] = pd.to_numeric(price.get("input_price"), errors="coerce")
    price["output_price_num"] = pd.to_numeric(price.get("output_price"), errors="coerce")

    audit_fields = [
        "model_id",
        "pricing_status",
        "fallback_issue",
        "fallback_rate",
        "sku_mapping_status",
        "config_mapping_status",
        "human_verified",
    ]
    audit_use = audit[[col for col in audit_fields if col in audit.columns]].drop_duplicates("model_id")
    merged = price.merge(audit_use, on="model_id", how="left", suffixes=("", "_audit"))
    if pricing_human_check is not None and not pricing_human_check.empty and "model_id" in pricing_human_check.columns:
        check = pricing_human_check[[col for col in ["model_id", "human_verified"] if col in pricing_human_check.columns]].drop_duplicates("model_id")
        merged = merged.merge(check, on="model_id", how="left", suffixes=("", "_human_check"))

    utility_ids = set()
    if utilities is not None and not utilities.empty and "model_id" in utilities.columns:
        utility_ids = set(utilities["model_id"].astype(str))

    rows = []
    for _, row in merged.iterrows():
        model_id = str(row["model_id"])
        pricing_status = str(row.get("pricing_status", ""))
        has_base_price = pd.notna(row["input_price_num"]) and pd.notna(row["output_price_num"])
        fallback_issue = str(row.get("fallback_issue", "")).upper() == "TRUE"
        verified_fields = [
            str(row.get("human_verified", "")).upper() == "TRUE",
            str(row.get("human_verified_audit", "")).upper() == "TRUE",
            str(row.get("human_verified_human_check", "")).upper() == "TRUE",
        ]
        pricing_human_verified = all(verified_fields)
        if pricing_status == "READY" and has_base_price and not fallback_issue:
            observability = "FULL"
            included = pricing_human_verified
            exclusion_reason = "" if included else "complete price is present but all human-verification records are not TRUE"
        elif has_base_price:
            observability = "PARTIAL"
            included = False
            exclusion_reason = "base model price exists but benchmark configuration has unresolved special billing"
        else:
            observability = "MISSING"
            included = False
            exclusion_reason = "official input/output price is missing or not publicly observable"

        rows.append(
            {
                "model_id": model_id,
                "model_name": row.get("model_name", ""),
                "utility_available": model_id in utility_ids,
                "pricing_available": has_base_price,
                "pricing_human_verified": pricing_human_verified,
                "cost_observability": observability,
                "pricing_status": pricing_status,
                "sku_mapping_status": row.get("sku_mapping_status", ""),
                "config_mapping_status": row.get("config_mapping_status", ""),
                "fallback_issue": str(row.get("fallback_issue", "")),
                "fallback_rate": row.get("fallback_rate", ""),
                "included_in_main_pareto": included,
                "included_in_regression": included,
                "exclusion_reason": exclusion_reason,
            }
        )

    result = pd.DataFrame(rows)
    result["cost_observability"] = pd.Categorical(result["cost_observability"], categories=COHORT_ORDER, ordered=True)
    return result.sort_values(["cost_observability", "model_id"]).reset_index(drop=True)


def full_model_ids(cohort: pd.DataFrame) -> list[str]:
    included = cohort["included_in_main_pareto"].astype(str).str.upper().eq("TRUE")
    return cohort.loc[
        (cohort["cost_observability"].astype(str) == "FULL") & included,
        "model_id",
    ].astype(str).tolist()


def attach_cost_observability(costs: pd.DataFrame, cohort: pd.DataFrame) -> pd.DataFrame:
    fields = ["model_id", "cost_observability", "included_in_main_pareto", "exclusion_reason"]
    return costs.merge(cohort[fields], on="model_id", how="left")


def save_analysis_cohort(cohort: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = cohort.copy()
    output["cost_observability"] = output["cost_observability"].astype(str)
    output.to_csv(output_path, index=False)
    return output
