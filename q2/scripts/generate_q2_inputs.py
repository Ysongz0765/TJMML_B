from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.q1.bt_model import fit_dimensions  # noqa: E402
from src.q1.config import CORE_MODELS, MAIN_LAMBDA, MARGIN_EPSILON  # noqa: E402
from src.q1.load_data import load_q1_data  # noqa: E402
from src.q1.pairwise import build_pairwise  # noqa: E402


Q1_OUT = ROOT / "outputs" / "q1_v1.2"
FROZEN = ROOT / "frozen" / "v1.0"
Q2 = ROOT / "q2"
DATA = Q2 / "data"
META = Q2 / "metadata"

TYPE_A_MODELS = {"deepseek_v4_pro_max", "deepseek_v4_flash_max", "glm_5_2_max"}
TYPE_C_MODELS = {
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "qwen3_8_max",
}
DIM_LABELS = {
    "C1": "复杂推理",
    "C2": "知识与事实可靠性",
    "C3": "长上下文",
    "C4": "代码与软件工程",
    "C5": "多模态",
}


def code(dimension: str) -> str:
    return dimension.split(" ", 1)[0]


def clean(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if pd.isna(value):
        return None
    return value


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: "" if row.get(col) is None else row.get(col) for col in columns})


def quantile(series: pd.Series, q: float):
    series = pd.to_numeric(series, errors="coerce").dropna()
    return float(series.quantile(q)) if len(series) else None


def strength_label(observed_families: int, total_families: int, source_count: int) -> str:
    if total_families <= 0 or observed_families <= 0:
        return "LOW"
    ratio = observed_families / total_families
    if ratio >= 0.75 and source_count >= 2:
        return "HIGH"
    return "MEDIUM"


def observed_note(observed: list[str], missing: list[str]) -> str:
    observed_part = ", ".join(observed) if observed else "none"
    missing_part = ", ".join(missing) if missing else "none"
    return f"observed: {observed_part}; missing: {missing_part}"


def build() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    with (Q1_OUT / "results_summary_v1.2.json").open(encoding="utf-8") as handle:
        summary = json.load(handle)

    q1 = load_q1_data()
    pairwise = build_pairwise(q1.long, margin_method="range", epsilon_m=MARGIN_EPSILON)
    main_scores, diagnostics = fit_dimensions(pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
    dim_codes = [code(d) for d in q1.dimensions]

    score_cols = {code(d): f"{d}_score" for d in q1.dimensions}
    theta_cols = {code(d): f"{d}_theta" for d in q1.dimensions}
    applicable_cols = {code(d): f"{d}_applicable" for d in q1.dimensions}
    scores_by_id = main_scores.set_index("model_id")
    model_names = q1.model_names

    ranking_maps: dict[str, dict[str, dict]] = {}
    for key in ["ranking_A", "ranking_B", "ranking_C"]:
        ranking_maps[key] = {row["model_id"]: row for row in summary[key]}

    c5_audit = {row["model_id"]: row for row in summary["c5_audit"]}

    capability_rows = []
    for model_id in CORE_MODELS:
        row = {"model_id": model_id, "model": model_names[model_id]}
        for dim in ["C1", "C2", "C3", "C4"]:
            row[f"{dim}_score"] = clean(scores_by_id.loc[model_id, score_cols[dim]])
        row["C5_BT_score"] = clean(scores_by_id.loc[model_id, score_cols["C5"]])
        row["C5_effective_score"] = 0.0 if model_id in TYPE_A_MODELS else row["C5_BT_score"]
        capability_rows.append(row)
    write_csv(
        DATA / "q1_capability_scores.csv",
        capability_rows,
        ["model_id", "model", "C1_score", "C2_score", "C3_score", "C4_score", "C5_BT_score", "C5_effective_score"],
    )

    theta_rows = []
    for model_id in CORE_MODELS:
        row = {"model_id": model_id, "model": model_names[model_id]}
        for dim in dim_codes:
            row[f"{dim}_theta"] = clean(scores_by_id.loc[model_id, theta_cols[dim]])
        theta_rows.append(row)
    write_csv(DATA / "q1_bt_latent_scores.csv", theta_rows, ["model_id", "model"] + [f"{d}_theta" for d in dim_codes])

    dimension_families = {
        code(dim): sorted(q1.manifest.loc[q1.manifest["dimension"].eq(dim), "benchmark_family"].dropna().unique())
        for dim in q1.dimensions
    }
    observed_by_model_dim: dict[tuple[str, str], pd.DataFrame] = {}
    for dim in q1.dimensions:
        dim_code = code(dim)
        part = q1.long[(q1.long["dimension"].eq(dim)) & q1.long["score"].notna()].copy()
        for model_id in CORE_MODELS:
            observed_by_model_dim[(model_id, dim_code)] = part[part["model_id"].eq(model_id)]

    applicability_rows = []
    for model_id in CORE_MODELS:
        c5_obs = observed_by_model_dim[(model_id, "C5")]
        c3_obs = sorted(c5 for c5 in observed_by_model_dim[(model_id, "C3")]["benchmark_family"].dropna().unique())
        c4_obs = sorted(c5 for c5 in observed_by_model_dim[(model_id, "C4")]["benchmark_family"].dropna().unique())
        c3_missing = [fam for fam in dimension_families["C3"] if fam not in c3_obs]
        c4_missing = [fam for fam in dimension_families["C4"] if fam not in c4_obs]
        c3_sources = observed_by_model_dim[(model_id, "C3")]["source_id"].dropna().nunique()
        c4_sources = observed_by_model_dim[(model_id, "C4")]["source_id"].dropna().nunique()
        row = {
            "model_id": model_id,
            "model": model_names[model_id],
            "multimodal_capable": model_id in TYPE_C_MODELS,
            "C1_applicable": bool(scores_by_id.loc[model_id, applicable_cols["C1"]]),
            "C2_applicable": bool(scores_by_id.loc[model_id, applicable_cols["C2"]]),
            "C3_applicable": bool(scores_by_id.loc[model_id, applicable_cols["C3"]]),
            "C4_applicable": bool(scores_by_id.loc[model_id, applicable_cols["C4"]]),
            "C5_applicable": model_id in TYPE_C_MODELS,
            "C5_status": "STRUCTURAL_CAPABILITY_ABSENCE" if model_id in TYPE_A_MODELS else "ESTIMABLE",
            "C5_direct_benchmark_count": int(len(c5_obs)),
            "C3_direct_observation_strength": f"{strength_label(len(c3_obs), len(dimension_families['C3']), c3_sources)}: {observed_note(c3_obs, c3_missing)}",
            "C4_direct_observation_strength": f"{strength_label(len(c4_obs), len(dimension_families['C4']), c4_sources)}: {observed_note(c4_obs, c4_missing)}",
        }
        applicability_rows.append(row)
    write_csv(
        DATA / "q1_model_applicability.csv",
        applicability_rows,
        [
            "model_id",
            "model",
            "multimodal_capable",
            "C1_applicable",
            "C2_applicable",
            "C3_applicable",
            "C4_applicable",
            "C5_applicable",
            "C5_status",
            "C5_direct_benchmark_count",
            "C3_direct_observation_strength",
            "C4_direct_observation_strength",
        ],
    )

    ranking_rows = []
    for model_id in CORE_MODELS:
        a = ranking_maps["ranking_A"].get(model_id, {})
        b = ranking_maps["ranking_B"].get(model_id, {})
        c = ranking_maps["ranking_C"].get(model_id, {})
        ranking_rows.append(
            {
                "model_id": model_id,
                "model": model_names[model_id],
                "ranking_A_rank": a.get("rank"),
                "ranking_A_score": a.get("overall_score"),
                "ranking_B_rank": b.get("rank"),
                "ranking_B_score": b.get("overall_score"),
                "ranking_C_rank": c.get("rank"),
                "ranking_C_score": c.get("overall_score"),
            }
        )
    write_csv(
        DATA / "q1_model_rankings.csv",
        ranking_rows,
        [
            "model_id",
            "model",
            "ranking_A_rank",
            "ranking_A_score",
            "ranking_B_rank",
            "ranking_B_score",
            "ranking_C_rank",
            "ranking_C_score",
        ],
    )

    stability_A = {
        row["perspective_dimension"]: row["latent_ranking_stability_T"]
        for row in summary["stability_audit"]["new_stability"]
        if row.get("perspective") == "A"
    }
    boot_theta = pd.read_csv(Q1_OUT / "bootstrap" / "bootstrap_bt_theta_v1.2.csv")
    boot_scores = pd.read_csv(Q1_OUT / "bootstrap" / "bootstrap_dimension_scores_v1.2.csv")
    uncertainty_rows = []
    for (model_id, dim), theta_group in boot_theta.groupby(["model_id", "dimension"]):
        score_group = boot_scores[(boot_scores["model_id"].eq(model_id)) & (boot_scores["dimension"].eq(dim))]
        theta_values = pd.to_numeric(theta_group["theta"], errors="coerce")
        score_values = pd.to_numeric(score_group["score"], errors="coerce")
        uncertainty_rows.append(
            {
                "uncertainty_scope": "DIMENSION_LATENT_SCORE",
                "perspective": "",
                "model_id": model_id,
                "model": model_names[model_id],
                "dimension": dim,
                "theta_bootstrap_mean": float(theta_values.mean()) if theta_values.notna().any() else None,
                "theta_bootstrap_sd": float(theta_values.std(ddof=1)) if theta_values.notna().sum() >= 2 else None,
                "score_bootstrap_mean": float(score_values.mean()) if score_values.notna().any() else None,
                "score_bootstrap_sd": float(score_values.std(ddof=1)) if score_values.notna().sum() >= 2 else None,
                "score_ci_low": quantile(score_values, 0.025),
                "score_ci_high": quantile(score_values, 0.975),
                "rank_ci_low": None,
                "rank_ci_high": None,
                "T_d": stability_A.get(dim),
                "top3_probability": None,
                "availability_note": "rank CI unavailable for dimension-level BT score rows",
            }
        )
    for perspective in ["A", "B", "C"]:
        boot = pd.read_csv(Q1_OUT / "bootstrap" / f"bootstrap_ranking_{perspective}_v1.2.csv")
        for model_id, group in boot.groupby("model_id"):
            uncertainty_rows.append(
                {
                    "uncertainty_scope": "Q1_RANKING",
                    "perspective": perspective,
                    "model_id": model_id,
                    "model": model_names[model_id],
                    "dimension": f"RANKING_{perspective}",
                    "theta_bootstrap_mean": None,
                    "theta_bootstrap_sd": None,
                    "score_bootstrap_mean": float(group["overall_score"].mean()),
                    "score_bootstrap_sd": float(group["overall_score"].std(ddof=1)),
                    "score_ci_low": quantile(group["overall_score"], 0.025),
                    "score_ci_high": quantile(group["overall_score"], 0.975),
                    "rank_ci_low": quantile(group["rank"], 0.025),
                    "rank_ci_high": quantile(group["rank"], 0.975),
                    "T_d": None,
                    "top3_probability": float((group["rank"] <= 3).mean()),
                    "availability_note": "overall ranking bootstrap row; theta fields not applicable",
                }
            )
    for dim, t_value in stability_A.items():
        uncertainty_rows.append(
            {
                "uncertainty_scope": "DIMENSION_STABILITY",
                "perspective": "A",
                "model_id": "",
                "model": "",
                "dimension": dim,
                "theta_bootstrap_mean": None,
                "theta_bootstrap_sd": None,
                "score_bootstrap_mean": None,
                "score_bootstrap_sd": None,
                "score_ci_low": None,
                "score_ci_high": None,
                "rank_ci_low": None,
                "rank_ci_high": None,
                "T_d": t_value,
                "top3_probability": None,
                "availability_note": "dimension-level latent ranking stability",
            }
        )
    uncertainty_columns = [
        "uncertainty_scope",
        "perspective",
        "model_id",
        "model",
        "dimension",
        "theta_bootstrap_mean",
        "theta_bootstrap_sd",
        "score_bootstrap_mean",
        "score_bootstrap_sd",
        "score_ci_low",
        "score_ci_high",
        "rank_ci_low",
        "rank_ci_high",
        "T_d",
        "top3_probability",
        "availability_note",
    ]
    write_csv(DATA / "q1_uncertainty.csv", uncertainty_rows, uncertainty_columns)

    weight_rows = []
    for row in summary["weights_A"]:
        weight_rows.append(
            {
                "dimension": row["dimension"],
                "dimension_label": DIM_LABELS[row["dimension"]],
                "q1_weight": row["weight"],
                "information": row["information_I"],
                "redundancy": row["non_redundancy_R"],
                "stability": row["latent_rank_stability_T"],
                "reference_scope": "Q1 Ranking A 综合性能评价; not Q2 scenario weight",
            }
        )
    write_csv(
        DATA / "q1_dimension_weights_reference.csv",
        weight_rows,
        ["dimension", "dimension_label", "q1_weight", "information", "redundancy", "stability", "reference_scope"],
    )

    registry = pd.read_csv(FROZEN / "source_registry_v1.0.csv")
    source_type_map = registry.set_index("source_id")["source_type"].to_dict()
    source_title_map = registry.set_index("source_id")["source_title"].to_dict()
    manifest = pd.read_csv(FROZEN / "final_modeling_benchmark_manifest_v1.0.csv")
    mapping_rows = []
    for row in manifest.to_dict("records"):
        mapping_rows.append(
            {
                "dimension": code(row["capability"]),
                "dimension_label": row["capability"],
                "benchmark_family": row["benchmark_family"],
                "exact_setting": row["selected_setting"],
                "benchmark_name": row["benchmark_name"],
                "version": row["version"],
                "metric": row["metric"],
                "model_coverage": row["model_coverage"],
                "source": row["source"],
                "source_title": source_title_map.get(row["source"], ""),
                "source_type": source_type_map.get(row["source"], ""),
                "final_role": row["final_role"],
            }
        )
    write_csv(
        DATA / "benchmark_family_mapping.csv",
        mapping_rows,
        [
            "dimension",
            "dimension_label",
            "benchmark_family",
            "exact_setting",
            "benchmark_name",
            "version",
            "metric",
            "model_coverage",
            "source",
            "source_title",
            "source_type",
            "final_role",
        ],
    )

    source_rows = []
    for row in registry.to_dict("records"):
        source_rows.append(
            {
                "source_id": row["source_id"],
                "source_name": f"{row['publisher']}: {row['source_title']}",
                "source_type": row["source_type"],
                "benchmark_family": row["benchmark_related"],
                "snapshot_date": row["access_date"],
                "authority_level": row["authority_level"],
                "notes": row["notes"],
            }
        )
    write_csv(
        DATA / "source_registry_summary.csv",
        source_rows,
        ["source_id", "source_name", "source_type", "benchmark_family", "snapshot_date", "authority_level", "notes"],
    )

    evidence_rows = []
    for model_id in CORE_MODELS:
        for dim in dim_codes:
            obs = observed_by_model_dim[(model_id, dim)]
            observed_fams = sorted(obs["benchmark_family"].dropna().unique())
            missing_fams = [fam for fam in dimension_families[dim] if fam not in observed_fams]
            source_count = int(obs["source_id"].dropna().nunique())
            family_count = int(len(observed_fams))
            total_count = int(len(dimension_families[dim]))
            if family_count == 0:
                dependency = "NOT_ESTIMABLE_OR_ABSENT"
            elif family_count == total_count:
                dependency = "LOW_NETWORK_DEPENDENCY"
            elif family_count >= 2:
                dependency = "MODERATE_NETWORK_DEPENDENCY"
            else:
                dependency = "HIGH_NETWORK_DEPENDENCY"
            label = strength_label(family_count, total_count, source_count)
            if dim == "C5" and model_id in TYPE_A_MODELS:
                label = "LOW"
                dependency = "STRUCTURAL_CAPABILITY_ABSENCE"
            evidence_rows.append(
                {
                    "model_id": model_id,
                    "model": model_names[model_id],
                    "dimension": dim,
                    "direct_observation_count": int(len(obs)),
                    "benchmark_family_count": family_count,
                    "source_count": source_count,
                    "network_dependency": dependency,
                    "evidence_strength": label,
                    "notes": observed_note(observed_fams, missing_fams),
                }
            )
    write_csv(
        DATA / "q1_evidence_strength.csv",
        evidence_rows,
        [
            "model_id",
            "model",
            "dimension",
            "direct_observation_count",
            "benchmark_family_count",
            "source_count",
            "network_dependency",
            "evidence_strength",
            "notes",
        ],
    )

    boot_a = pd.read_csv(Q1_OUT / "bootstrap" / "bootstrap_ranking_A_v1.2.csv")
    rank_a_ci = {
        model_id: {
            "Q1_bootstrap_rank_low": quantile(group["rank"], 0.025),
            "Q1_bootstrap_rank_high": quantile(group["rank"], 0.975),
        }
        for model_id, group in boot_a.groupby("model_id")
    }
    evidence_by_model_dim = {(r["model_id"], r["dimension"]): r for r in evidence_rows}
    master_rows = []
    cap_by_id = {r["model_id"]: r for r in capability_rows}
    theta_by_id = {r["model_id"]: r for r in theta_rows}
    app_by_id = {r["model_id"]: r for r in applicability_rows}
    rank_by_id = {r["model_id"]: r for r in ranking_rows}
    for model_id in CORE_MODELS:
        row = {
            "model_id": model_id,
            "model": model_names[model_id],
            **{k: cap_by_id[model_id].get(k) for k in ["C1_score", "C2_score", "C3_score", "C4_score", "C5_BT_score", "C5_effective_score"]},
            **{k: theta_by_id[model_id].get(k) for k in ["C1_theta", "C2_theta", "C3_theta", "C4_theta", "C5_theta"]},
            "multimodal_capable": app_by_id[model_id]["multimodal_capable"],
            "C5_status": app_by_id[model_id]["C5_status"],
            "ranking_A": rank_by_id[model_id]["ranking_A_rank"],
            "ranking_B": rank_by_id[model_id]["ranking_B_rank"],
            "ranking_C": rank_by_id[model_id]["ranking_C_rank"],
            "ranking_A_score": rank_by_id[model_id]["ranking_A_score"],
            "ranking_B_score": rank_by_id[model_id]["ranking_B_score"],
            "ranking_C_score": rank_by_id[model_id]["ranking_C_score"],
            **rank_a_ci[model_id],
        }
        for dim in dim_codes:
            ev = evidence_by_model_dim[(model_id, dim)]
            row[f"{dim}_evidence_note"] = f"{ev['evidence_strength']}; {ev['notes']}"
        master_rows.append(row)
    master_columns = [
        "model_id",
        "model",
        "C1_score",
        "C2_score",
        "C3_score",
        "C4_score",
        "C5_BT_score",
        "C5_effective_score",
        "C1_theta",
        "C2_theta",
        "C3_theta",
        "C4_theta",
        "C5_theta",
        "multimodal_capable",
        "C5_status",
        "ranking_A",
        "ranking_B",
        "ranking_C",
        "ranking_A_score",
        "ranking_B_score",
        "ranking_C_score",
        "Q1_bootstrap_rank_low",
        "Q1_bootstrap_rank_high",
        "C1_evidence_note",
        "C2_evidence_note",
        "C3_evidence_note",
        "C4_evidence_note",
        "C5_evidence_note",
    ]
    write_csv(DATA / "q2_model_master_table.csv", master_rows, master_columns)

    (Q2 / "README_Q2_DATA.md").write_text(readme_text(), encoding="utf-8")
    (META / "q2_data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")
    (META / "q2_data_provenance.md").write_text(data_provenance_text(), encoding="utf-8")
    (META / "q1_to_q2_mapping.md").write_text(mapping_text(), encoding="utf-8")

    qc = {
        "main_bt_converged": {code(dim): bool(diagnostics[dim]["converged"]) for dim in q1.dimensions},
        "generated_files": sorted(str(p.relative_to(Q2)).replace("\\", "/") for p in Q2.rglob("*") if p.is_file()),
        "C5_status_enum": ["ESTIMABLE", "STRUCTURAL_CAPABILITY_ABSENCE", "BENCHMARK_MISSING"],
        "evidence_strength_rule": "HIGH if observed benchmark-family coverage >=75% and source_count >=2; MEDIUM if at least one direct family is observed; LOW if none or structural C5 absence.",
    }
    (DATA / "q2_generation_qc.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")


def readme_text() -> str:
    return """# Q2 standardized input datasets

This directory is a Q2 data interface prepared from Q1 frozen data and Q1 v1.2 official outputs.

## Data source

All files here are derived from:

- `frozen/v1.0/`
- `outputs/q1_v1.2/`

No benchmark was re-fetched, no Q1 ranking was changed, and no missing benchmark or latent score was imputed.

## Primary Q1 capability inputs

Q2 should primarily read the model capability profile:

- `data/q1_capability_scores.csv`
- `data/q1_bt_latent_scores.csv`
- `data/q1_model_applicability.csv`
- `data/q2_model_master_table.xlsx`

`C5_BT_score` is the estimated BT multimodal score and remains missing for structural capability absence. `C5_effective_score` is the Q1 Ranking A capability-availability value `C5*`; it is 0 for DeepSeek-V4-Pro Max, DeepSeek-V4-Flash Max, and GLM-5.2 (max).

## Reference only

The following are Q1 reference outputs, not Q2 scenario weights or utilities:

- `data/q1_model_rankings.csv`
- `data/q1_dimension_weights_reference.csv`

Q1 weights are for Q1 comprehensive performance evaluation under the frozen benchmark universe. They are not Q2 scenario weights for scientific long-text analysis, daily chat, or code development.

## What Q2 must not do directly

- Do not use Q1 Ranking A overall score as the final utility value for the three Q2 application scenarios.
- Do not reuse Q1 objective weights as Q2 scenario weights.
- Do not confuse C5 structural capability absence with benchmark zero.
- Do not fill missing latent scores with 0.
- Do not treat Ranking C as applicable to non-estimable C5 models.

## File groups

- `data/`: machine-readable Q1-to-Q2 data tables.
- `metadata/`: field definitions, provenance, and candidate Q1-to-Q2 capability mapping.
- `scripts/`: generation and validation scripts for this interface.
"""


def data_dictionary_text() -> str:
    return """# Q2 data dictionary

| field | meaning | unit/range | missing-value meaning | source file | Q2 intended use |
| --- | --- | --- | --- | --- | --- |
| model_id | Stable machine-readable model id | text | not allowed | all data files | joins across Q2 inputs |
| model | Human-readable model name | text | not allowed | all data files | reporting and sanity checks |
| C1_score | Q1 0-100 BT score for complex reasoning | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C2_score | Q1 0-100 BT score for knowledge/factual reliability | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C3_score | Q1 0-100 BT score for long context | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C4_score | Q1 0-100 BT score for code/software engineering | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C5_BT_score | Q1 0-100 BT score for estimable multimodal ability | 0-100 | structural C5 absence or not estimable; not benchmark zero | q1_capability_scores.csv | capability profile when C5 is estimable |
| C5_effective_score | Q1 Ranking A effective C5* availability score | 0-100 | not expected | q1_capability_scores.csv | capability availability for Q1-style all-model comparison |
| C1_theta-C5_theta | Raw regularized Bradley-Terry latent ability | real-valued theta | dimension not estimable; never auto-fill with 0 | q1_bt_latent_scores.csv | alternative modeling input without min-max scaling |
| multimodal_capable | Whether model has native multimodal capability under Q1 definition | TRUE/FALSE | not expected | q1_model_applicability.csv | C5 applicability gating |
| C5_status | C5 applicability status | ESTIMABLE / STRUCTURAL_CAPABILITY_ABSENCE / BENCHMARK_MISSING | not expected | q1_model_applicability.csv | capability applicability handling |
| C5_direct_benchmark_count | Number of direct selected C5 benchmark observations | integer | 0 means no direct C5 observation | q1_model_applicability.csv | evidence coverage |
| C3_direct_observation_strength | Rule-based coverage note for C3 | text category plus note | unavailable if no diagnostic support | q1_model_applicability.csv | caution for long-context scenario |
| C4_direct_observation_strength | Rule-based coverage note for C4 | text category plus note | unavailable if no diagnostic support | q1_model_applicability.csv | caution for coding scenario |
| ranking_A_rank / ranking_A_score | Q1 all-model C1-C5* reference rank and score | rank / 0-100 composite | not expected | q1_model_rankings.csv | reference sanity check only |
| ranking_B_rank / ranking_B_score | Q1 all-model C1-C4 reference rank and score | rank / 0-100 composite | not expected | q1_model_rankings.csv | reference sanity check only |
| ranking_C_rank / ranking_C_score | Q1 estimable-C5 subset reference rank and score | rank / 0-100 composite | NA for non-Ranking-C models | q1_model_rankings.csv | reference sanity check only |
| theta_bootstrap_mean / theta_bootstrap_sd | Bootstrap mean and SD of raw BT theta | theta | unavailable for ranking-level rows | q1_uncertainty.csv | uncertainty-aware modeling |
| score_bootstrap_mean / score_bootstrap_sd | Bootstrap mean and SD of dimension or ranking score | 0-100 | unavailable for stability-only rows | q1_uncertainty.csv | uncertainty-aware modeling |
| score_ci_low / score_ci_high | Percentile 95% bootstrap interval for score | 0-100 | unavailable when Q1 did not define a score row | q1_uncertainty.csv | uncertainty bounds |
| rank_ci_low / rank_ci_high | Percentile 95% bootstrap interval for Q1 ranking | rank | unavailable for dimension score rows | q1_uncertainty.csv | ranking uncertainty reference |
| T_d | Q1 v1.2 latent-ranking stability | 0-1 | unavailable for model-only rows where not applicable | q1_uncertainty.csv and q1_dimension_weights_reference.csv | data reliability cue |
| q1_weight | Q1 Ranking A objective weight | sums to 1 | not expected | q1_dimension_weights_reference.csv | reference only, not scenario weight |
| information / redundancy / stability | Q1 weight components | non-negative | not expected | q1_dimension_weights_reference.csv | audit and reference |
| direct_observation_count | Count of selected direct benchmark rows observed | integer | 0 means no direct observation | q1_evidence_strength.csv | evidence coverage |
| benchmark_family_count | Count of benchmark families directly observed | integer | 0 means no direct family | q1_evidence_strength.csv | evidence coverage |
| source_count | Count of source ids directly observed | integer | 0 means no direct source | q1_evidence_strength.csv | source diversity cue |
| evidence_strength | Rule-based category, not an arbitrary score | HIGH / MEDIUM / LOW | not expected | q1_evidence_strength.csv | scenario-risk adjustment candidate |

Important C5 distinction: `C5_BT_score = NA` and `C5_effective_score = 0` can occur at the same time. This means the model lacks native multimodal capability under Q1's definition; it does not mean the model received a raw benchmark score of 0.
"""


def data_provenance_text() -> str:
    return """# Q2 data provenance

| Q1 source file | Q2 output file | transformation | numerical values changed |
| --- | --- | --- | --- |
| `outputs/q1_v1.2/results_summary_v1.2.json` and frozen BT inputs | `data/q1_capability_scores.csv` | direct export of Q1 v1.2 scores plus C5* applicability separation | no, except explicit C5* availability field copied from Q1 Ranking A rule |
| frozen BT inputs and Q1 v1.2 BT code path | `data/q1_bt_latent_scores.csv` | read-only reconstruction of main regularized BT theta | no new scaling or imputation |
| `outputs/q1_v1.2/results_summary_v1.2.json` C5 audit and frozen selected benchmark rows | `data/q1_model_applicability.csv` | status normalization and direct observation counts | no benchmark scores changed |
| `outputs/q1_v1.2/results_summary_v1.2.json` rankings | `data/q1_model_rankings.csv` | direct export | no |
| `outputs/q1_v1.2/bootstrap/*.csv` | `data/q1_uncertainty.csv` | grouped bootstrap summary statistics and percentile intervals | summary statistics only |
| `outputs/q1_v1.2/results_summary_v1.2.json` weights | `data/q1_dimension_weights_reference.csv` | direct export of Ranking A reference weights and components | no |
| `frozen/v1.0/final_modeling_benchmark_manifest_v1.0.csv` | `data/benchmark_family_mapping.csv` | selected fields copied and joined to source type/title | no |
| `frozen/v1.0/source_registry_v1.0.csv` | `data/source_registry_summary.csv` | selected fields copied and renamed | no |
| frozen selected benchmark rows | `data/q1_evidence_strength.csv` | direct counts by model and dimension plus rule-based category | no benchmark scores changed |
| Q2 CSV files | `data/q2_model_master_table.xlsx` | one-row-per-model merge for Q2 interface convenience | no |
"""


def mapping_text() -> str:
    return """# Candidate Q1-to-Q2 capability mapping

This file records possible relevance only. It does not define Q2 scenario weights and does not introduce CES parameters.

## Scientific long-text analysis

Likely relevant Q1 capabilities:

- C3 长上下文
- C1 复杂推理
- C2 知识与事实可靠性

C5 多模态 may have auxiliary relevance when scientific inputs include figures, tables, screenshots, or image-based documents. Its final role and weight must be determined by the Q2 model.

## Daily general conversation

Likely relevant Q1 capabilities:

- C2 知识与事实可靠性
- C1 复杂推理

Other non-Q1 factors may also matter, such as latency, style, safety, tool availability, and cost. These are outside this Q1-derived interface.

## Computer code development

Likely relevant Q1 capabilities:

- C4 代码与软件工程
- C1 复杂推理

C2 and C3 may be relevant for documentation understanding, API reasoning, and long-repository context, but final Q2 weights are not defined here.
"""


if __name__ == "__main__":
    build()
