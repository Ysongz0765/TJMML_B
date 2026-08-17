from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "outputs" / "q2" / "final"
FREEZE = FINAL / "freeze"
SPEC = ROOT / "q2" / "model_spec_v1.yaml"
Q2_DATA = ROOT / "q2" / "data"
Q3_HANDOFF = ROOT / "q2" / "q3_handoff"
DOCS = ROOT / "docs"
PDF = ROOT / "output" / "pdf" / "Q2_Final_Paper.pdf"

Q1_DATA_COMMIT = "754bc1b541b5b0d27e8b74b75b979849edf72cda"
Q1_FREEZE_VERSION = "frozen/v1.0 + Q1 v1.2 official outputs"
Q2_FREEZE_VERSION = "Q2_FINAL_v1.0"
EXPECTED_SCENES = {
    "research": ("Research", "科研长文本分析", ("C1", "C2", "C3")),
    "dialogue": ("Dialogue", "大众日常通用对话", ("C1", "C2", "C3", "C5")),
    "coding": ("Coding", "计算机代码开发", ("C1", "C4")),
}
REQUIRED_FREEZE_FILES = [
    "q2_scene_weights.csv",
    "q2_scene_scores.csv",
    "q2_scene_rankings.csv",
    "q2_linear_vs_ces.csv",
    "q2_pri.csv",
    "q2_marginal_effects.csv",
    "q2_parameter_robustness.csv",
    "q2_rank_transition_thresholds.csv",
    "q2_prior_sensitivity.csv",
    "q2_q1_uncertainty_propagation.csv",
    "q2_missingness_sensitivity.csv",
    "q2_kimi_analysis.csv",
    "q2_model_spec_snapshot.yaml",
    "q2_run_metadata.json",
    "ces_input_transformation_audit.csv",
    "ces_input_transformation_audit.md",
    "q1_uncertainty_scale_audit.md",
    "model_spec_provenance_audit.md",
    "scene_definition_audit.md",
    "c5_policy_audit.md",
    "pri_audit.md",
    "rank_migration_audit.md",
    "Q2_FINAL_AUDIT_REPORT.md",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def audit_uncertainty_scale(raw_path: Path) -> dict[str, Any]:
    standardized = pd.read_csv(Q2_DATA / "q1_uncertainty.csv")
    dimension = standardized[
        standardized["uncertainty_scope"].eq("DIMENSION_LATENT_SCORE")
    ][
        [
            "model_id",
            "dimension",
            "theta_bootstrap_mean",
            "theta_bootstrap_sd",
            "score_bootstrap_mean",
            "score_bootstrap_sd",
        ]
    ]
    raw = pd.read_csv(raw_path)
    required_raw = {"bootstrap", "dimension", "model_id", "theta"}
    if not required_raw.issubset(raw.columns):
        raise AssertionError(f"Raw Q1 theta bootstrap is missing {required_raw - set(raw.columns)}")
    calculated = (
        raw.groupby(["model_id", "dimension"], as_index=False)["theta"]
        .agg(theta_calculated_mean="mean", theta_calculated_sd="std", nonmissing="count")
    )
    comparison = dimension.merge(
        calculated, on=["model_id", "dimension"], how="outer", validate="one_to_one"
    )
    mean_diff = (
        comparison["theta_bootstrap_mean"] - comparison["theta_calculated_mean"]
    ).abs()
    sd_diff = (
        comparison["theta_bootstrap_sd"] - comparison["theta_calculated_sd"]
    ).abs()
    same_na = comparison["theta_bootstrap_sd"].isna().eq(
        comparison["theta_calculated_sd"].isna()
    ).all()
    passed = bool(
        len(raw) == 100000
        and raw["bootstrap"].nunique() == 2000
        and len(comparison) == 50
        and same_na
        and float(mean_diff.max(skipna=True)) <= 1e-12
        and float(sd_diff.max(skipna=True)) <= 1e-12
    )
    result = {
        "status": "PASS" if passed else "FAIL",
        "raw_path": str(raw_path),
        "raw_sha256": sha256(raw_path),
        "raw_rows": len(raw),
        "bootstrap_replicates": int(raw["bootstrap"].nunique()),
        "groups": len(comparison),
        "max_mean_abs_diff": float(mean_diff.max(skipna=True)),
        "max_sd_abs_diff": float(sd_diff.max(skipna=True)),
        "latent_sd_min": float(dimension["theta_bootstrap_sd"].min()),
        "latent_sd_max": float(dimension["theta_bootstrap_sd"].max()),
        "score_sd_min": float(dimension["score_bootstrap_sd"].min()),
        "score_sd_max": float(dimension["score_bootstrap_sd"].max()),
        "structural_c5_na_groups": int(comparison["theta_bootstrap_sd"].isna().sum()),
    }
    write(
        FINAL / "q1_uncertainty_scale_audit.md",
        f"""# Q1 uncertainty scale audit

`Q1_UNCERTAINTY_SCALE_AUDIT = {result['status']}`

## Evidence chain

- Q1 raw source: `{raw_path}`
- Raw source SHA-256: `{result['raw_sha256']}`
- Raw fields: `bootstrap`, `dimension`, `model_id`, `theta`.
- Raw rows: {result['raw_rows']}; bootstrap replicates: {result['bootstrap_replicates']}.
- Q2 standardization code groups the raw `theta` column by `(model_id, dimension)` and writes its sample mean and sample SD to `theta_bootstrap_mean` and `theta_bootstrap_sd`.
- The separate `score_bootstrap_mean` and `score_bootstrap_sd` fields are computed from the 0-100 score replicate file and are not used in the latent-theta uncertainty equation.

## Numerical reconstruction

- Model-dimension groups checked: {result['groups']}.
- Maximum absolute mean difference: {result['max_mean_abs_diff']:.3e}.
- Maximum absolute SD difference: {result['max_sd_abs_diff']:.3e}.
- Latent-theta SD range: [{result['latent_sd_min']:.6g}, {result['latent_sd_max']:.6g}].
- 0-100 score SD range: [{result['score_sd_min']:.6g}, {result['score_sd_max']:.6g}].
- Structural-C5 groups with latent SD intentionally unavailable: {result['structural_c5_na_groups']}.

## Conclusion

`theta_bootstrap_sd` is reconstructed directly from the raw Bradley-Terry `theta` bootstrap replicates and is in the same latent-theta scale as the point estimate used in Q2. No 0-100 score SD is added to latent theta. The existing uncertainty propagation equation is dimensionally valid and is retained.
""",
    )
    if not passed:
        raise AssertionError("Q1 uncertainty scale audit failed.")
    return result


def audit_model_spec(metadata: dict[str, Any]) -> dict[str, Any]:
    spec_hash = sha256(SPEC)
    snapshot_hash = sha256(FINAL / "q2_model_spec_snapshot.yaml")
    log = git_text("log", "-1", "--format=%H|%cI", "--", "q2/model_spec_v1.yaml")
    if not log:
        commit, commit_time = "UNAVAILABLE", "UNAVAILABLE"
        passed = False
    else:
        commit, commit_time = log.split("|", 1)
        passed = (
            spec_hash == metadata["q2_model_spec_sha256"] == snapshot_hash
            and datetime.fromisoformat(commit_time)
            <= datetime.fromisoformat(metadata["timestamp"])
        )
    result = {
        "status": "PASS" if passed else "FAIL",
        "model_spec_sha256": spec_hash,
        "model_spec_commit": commit,
        "model_spec_commit_time": commit_time,
        "final_run_time": metadata["timestamp"],
        "q1_data_commit": metadata["q1_data_commit"],
        "q2_code_commit": metadata["git_commit"],
        "snapshot_sha256": snapshot_hash,
    }
    write(
        FINAL / "model_spec_provenance_audit.md",
        f"""# Model specification provenance audit

`MODEL_SPEC_PROVENANCE_AUDIT = {result['status']}`

| Field | Value |
|---|---|
| model_spec_sha256 | `{spec_hash}` |
| model_spec_commit | `{commit}` |
| model_spec_commit_time | `{commit_time}` |
| final_run_time | `{metadata['timestamp']}` |
| q1_data_commit | `{metadata['q1_data_commit']}` |
| q2_code_commit | `{metadata['git_commit']}` |
| snapshot_sha256 | `{snapshot_hash}` |

The original untracked working-file history cannot prove that the specification preceded every exploratory calculation. The paper therefore uses the conservative statement that the specification was fixed and committed before this final clean rerun. For the frozen result reported here, the committed specification predates the run timestamp and its source, snapshot and metadata hashes are identical.
""",
    )
    if not passed:
        raise AssertionError("Model specification provenance audit failed.")
    return result


def audit_transformation_and_scenes(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    audit = pd.read_csv(FINAL / "ces_input_transformation_audit.csv")
    applicability = pd.read_csv(Q2_DATA / "q1_model_applicability.csv")
    scores = pd.read_csv(FINAL / "q2_scene_scores.csv")
    weights = pd.read_csv(FINAL / "q2_scene_weights.csv")
    missing = pd.read_csv(FINAL / "q2_missingness_sensitivity.csv")

    primary_error = float(audit["primary_abs_error"].max())
    positive = bool(audit["primary_is_strictly_positive"].all())
    finite = bool(audit["primary_is_finite"].all())
    ordering = True
    for dimension in ("C1", "C2", "C3", "C4", "C5"):
        block = audit[(audit["dimension"] == dimension) & audit["raw_q1_theta"].notna()]
        theta_order = block.sort_values(["raw_q1_theta", "model_id"])["model_id"].tolist()
        z_order = block.sort_values(["z_primary_latent_strength", "model_id"])["model_id"].tolist()
        ordering &= theta_order == z_order
    delta_columns = [column for column in audit if column.startswith("z_score_floor_delta_")]
    delta_finite = bool(np.isfinite(audit[delta_columns].to_numpy(dtype=float)).all())
    delta_positive = bool((audit[delta_columns].to_numpy(dtype=float) > 0).all())
    theta_span = float(audit["raw_q1_theta"].max() - audit["raw_q1_theta"].min())
    transform_pass = bool(
        primary_error <= 1e-15
        and positive
        and finite
        and ordering
        and delta_finite
        and delta_positive
        and theta_span < 700.0
    )
    transform_result = {
        "status": "PASS" if transform_pass else "FAIL",
        "max_primary_abs_error": primary_error,
        "strictly_positive": positive,
        "finite": finite,
        "ordering_preserved": ordering,
        "theta_span": theta_span,
        "delta_columns": delta_columns,
    }
    write(
        FINAL / "ces_input_transformation_audit.md",
        f"""# CES input transformation audit

`CES_INPUT_AUDIT = {transform_result['status']}`

- Primary mapping: `z_ij = exp(theta_ij - max_i theta_ij)`, with a separate maximum in each dimension.
- Maximum reconstruction error: {primary_error:.3e}.
- Ordering preserved within every estimable dimension: {ordering}.
- All formal CES inputs are finite: {finite}.
- All formal CES inputs are strictly positive: {positive}.
- Observed latent-theta span: {theta_span:.6g}; no overflow or underflow risk was encountered.
- Score-floor sensitivity columns checked: {', '.join(delta_columns)}.
- Every score-floor input is finite and positive: {delta_finite and delta_positive}.
- Structural C5 rows retain raw latent NA and use the explicit availability anchor; they are not treated as latent observations.
- The delta sensitivity calls the same reference-scene evaluator as the main transform, so KL constraints, scene weights and reference rho are unchanged within each matching scene setting.
""",
    )
    if not transform_pass:
        raise AssertionError("CES input audit failed.")

    expected_core = {key: tuple(value[2]) for key, value in EXPECTED_SCENES.items()}
    spec_core = {
        key: tuple(spec["scenes"][key]["ces_core_dimensions"])
        for key in EXPECTED_SCENES
    }
    weight_core = {
        scene: tuple(
            weights[
                (weights["scene"] == scene)
                & (weights["prior"] == "q1")
                & weights["active_in_scene"]
            ]["dimension"].tolist()
        )
        for scene in EXPECTED_SCENES
    }
    score_scenes = set(scores["scene"])
    grid_count = pd.read_csv(FINAL / "q2_parameter_grid.csv").groupby(
        ["scene", "prior"]
    ).size()
    expected_grid_rows = 1170
    scene_pass = bool(
        spec_core == expected_core
        and weight_core == expected_core
        and score_scenes == set(EXPECTED_SCENES)
        and len(scores) == 30
        and (grid_count == expected_grid_rows).all()
    )
    scene_result = {
        "status": "PASS" if scene_pass else "FAIL",
        "expected_core": expected_core,
        "spec_core": spec_core,
        "weight_core": weight_core,
        "grid_rows_per_scene_prior": grid_count.to_dict(),
    }
    write(
        FINAL / "scene_definition_audit.md",
        f"""# Scene definition audit

`SCENE_DEFINITION_AUDIT = {scene_result['status']}`

| Scene | Frozen CES core | Active KL dimensions | Grid |
|---|---|---|---:|
| Research | C1, C2, C3 | C1, C2, C3 | 9 x 13 |
| Dialogue | C1, C2, C3, C5 | C1, C2, C3, C5 | 9 x 13 |
| Coding | C1, C4 | C1, C4 | 9 x 13 |

The YAML specification, KL active-weight output, CES score implementation and paper table use the same sets. Non-core dimensions receive zero reported scene weight and are not passed to CES, so negative rho cannot penalize a non-core ability. Each scene-prior block contains 117 parameter settings x 10 models = 1170 rows.
""",
    )
    if not scene_pass:
        raise AssertionError("Scene definition audit failed.")

    c5_audit = audit[audit["dimension"] == "C5"].merge(
        applicability[["model_id", "C5_status"]],
        on="model_id",
        suffixes=("_audit", "_metadata"),
        validate="one_to_one",
    )
    structural = c5_audit[c5_audit["C5_status_metadata"] == "STRUCTURAL_CAPABILITY_ABSENCE"]
    estimable = c5_audit[c5_audit["C5_status_metadata"] == "ESTIMABLE"]
    ordinary_missing = estimable["raw_q1_theta"].isna().sum()
    anchor_values = structural["z_primary_latent_strength"].unique()
    c5_pass = bool(
        len(structural) == 3
        and structural["raw_q1_theta"].isna().all()
        and len(anchor_values) == 1
        and np.isclose(anchor_values[0], 0.35)
        and estimable["raw_q1_theta"].notna().all()
        and ordinary_missing == 0
        and missing["sensitivity_type"].eq("structural_c5_anchor").sum() == 50
        and missing["sensitivity_type"].eq("common_dimension_without_C5").sum() == 10
    )
    write(
        FINAL / "c5_policy_audit.md",
        f"""# C5 structural-availability policy audit

`C5_POLICY_AUDIT = {'PASS' if c5_pass else 'FAIL'}`

- Estimable C5 models: {len(estimable)}; all retain observed/estimated latent theta.
- Structural-capability-absence models: {len(structural)}; all retain latent theta as NA.
- Primary structural availability anchor: 0.35, used only for the three metadata-marked structural-absence models.
- Ordinary estimable-C5 missing theta count: {ordinary_missing}.
- Anchor sensitivity: 5 values x 10 models = 50 rows.
- Common-dimension C1-C3 dialogue check: 10 rows.

The anchor is an explicit task-availability encoding, not statistical imputation and not a benchmark score of 0.35. No latent NA is filled with zero. Kimi K3 has estimable C5 theta and never receives the structural anchor.
""",
    )
    if not c5_pass:
        raise AssertionError("C5 policy audit failed.")
    return transform_result, scene_result


def audit_pri_and_migration() -> tuple[dict[str, Any], dict[str, Any]]:
    scores = pd.read_csv(FINAL / "q2_scene_scores.csv")
    pri_table = pd.read_csv(FINAL / "q2_pri.csv")
    recomputed = (scores["linear_utility"] - scores["ces_utility"]) / scores["linear_utility"]
    max_diff = float((scores["pri"] - recomputed).abs().max())
    min_pri = float(scores["pri"].min())
    max_pri = float(scores["pri"].max())
    joined = scores[["model_id", "scene", "linear_utility", "ces_utility", "pri"]].merge(
        pri_table,
        on=["model_id", "scene"],
        suffixes=("_scores", "_pri"),
        validate="one_to_one",
    )
    cross_file_diff = max(
        float((joined[f"{column}_scores"] - joined[f"{column}_pri"]).abs().max())
        for column in ("linear_utility", "ces_utility", "pri")
    )
    passed = min_pri >= -1e-12 and max_diff <= 1e-15 and cross_file_diff <= 1e-15
    result = {
        "status": "PASS" if passed else "FAIL",
        "minimum_pri": min_pri,
        "maximum_pri": max_pri,
        "formula_max_difference": max_diff,
        "cross_file_max_difference": cross_file_diff,
    }
    write(
        FINAL / "pri_audit.md",
        f"""# PRI audit

`PRI_AUDIT = {result['status']}`

- Definition: `PRI = (Linear - CES) / Linear`.
- Minimum PRI: {min_pri:.10f}.
- Maximum PRI: {max_pri:.10f}.
- Maximum formula reconstruction difference: {max_diff:.3e}.
- Maximum formal-score versus PRI-file difference: {cross_file_diff:.3e}.

Linear and CES use the same transformed inputs and the same scene KL weights. PRI is interpreted only as the relative utility reduction of the CES complementarity structure against a fully compensatory linear aggregator; it is not an objective percentage loss of a model's underlying capability.
""",
    )
    if not passed:
        raise AssertionError("PRI audit failed.")

    q1 = pd.read_csv(Q2_DATA / "q1_model_rankings.csv")
    migration = pd.read_csv(FINAL / "q2_rank_migration.csv")
    comparison = migration.merge(
        q1[["model_id", "ranking_A_rank"]], on="model_id", validate="one_to_one"
    )
    q1_mismatch = int(
        (comparison["rank_q1_reference"].astype(int) != comparison["ranking_A_rank"].astype(int)).sum()
    )
    delta_mismatch = 0
    for scene in ("research", "dialogue", "coding"):
        delta_mismatch += int(
            (
                comparison[f"delta_rank_{scene}"]
                != comparison[f"rank_{scene}"] - comparison["rank_q1_reference"]
            ).sum()
        )
    migration_pass = q1_mismatch == 0 and delta_mismatch == 0 and len(comparison) == 10
    migration_result = {
        "status": "PASS" if migration_pass else "FAIL",
        "q1_rank_mismatch": q1_mismatch,
        "delta_mismatch": delta_mismatch,
    }
    write(
        FINAL / "rank_migration_audit.md",
        f"""# Rank migration audit

`RANK_MIGRATION_AUDIT = {migration_result['status']}`

- Q1 Ranking A rows checked: {len(comparison)}.
- Q1 reference-rank mismatches: {q1_mismatch}.
- Delta-rank formula mismatches: {delta_mismatch}.
- Definition: `Delta R_i^(s) = R_i^(s) - R_i^(0)`.

Ranking A is used only as the frozen Q1 all-model general-capability reference. Negative Delta R denotes a better relative scene position. The paper describes this as a scene-position change relative to Q1, not as a change in a model's true comprehensive ranking.
""",
    )
    if not migration_pass:
        raise AssertionError("Rank migration audit failed.")
    return result, migration_result


def audit_paper_language() -> dict[str, Any]:
    paths = [ROOT / "sections" / "q2_final.tex", ROOT / "paper" / "q2_standalone.tex"]
    forbidden = [
        "Kimi 稳居日常前三",
        "Kimi 必然进入前三",
        "Kimi 绝对领先",
        "模型真实综合排名提高",
        "结构性缺失等于 Benchmark 0 分",
        "rho 是真实估计值",
        "alpha 是客观真实偏好",
    ]
    hits = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            if phrase in text:
                hits.append(f"{path.relative_to(ROOT)}: {phrase}")
        for placeholder in ("TODO", "MOCK", "provisional"):
            if placeholder.lower() in text.lower():
                hits.append(f"{path.relative_to(ROOT)}: {placeholder}")
    return {"status": "PASS" if not hits else "FAIL", "hits": hits}


def create_q3_handoff(
    metadata: dict[str, Any], uncertainty: pd.DataFrame
) -> Path:
    scores = pd.read_csv(FINAL / "q2_scene_scores.csv")
    identity = scores[["model_id", "model"]].drop_duplicates()
    nominal = scores.pivot(index="model_id", columns="scene", values=["ces_utility", "ces_rank"])
    nominal.columns = [f"{scene}_{metric}" for metric, scene in nominal.columns]
    nominal = nominal.reset_index()
    unc_values = uncertainty.pivot(
        index="model_id",
        columns="scene",
        values=[
            "probability_rank_1",
            "probability_top_3",
            "utility_ci_low",
            "utility_ci_high",
        ],
    )
    unc_values.columns = [f"{scene}_{metric}" for metric, scene in unc_values.columns]
    unc_values = unc_values.reset_index()
    handoff = identity.merge(nominal, on="model_id", validate="one_to_one").merge(
        unc_values, on="model_id", validate="one_to_one"
    )
    rename = {}
    for scene in ("research", "dialogue", "coding"):
        rename.update(
            {
                f"{scene}_ces_utility": f"{scene}_utility",
                f"{scene}_ces_rank": f"{scene}_rank",
                f"{scene}_probability_rank_1": f"{scene}_top1_probability",
                f"{scene}_probability_top_3": f"{scene}_top3_probability",
                f"{scene}_utility_ci_low": f"{scene}_utility_low",
                f"{scene}_utility_ci_high": f"{scene}_utility_high",
            }
        )
    handoff = handoff.rename(columns=rename)
    handoff["q1_freeze_version"] = Q1_FREEZE_VERSION
    handoff["q2_freeze_version"] = Q2_FREEZE_VERSION
    handoff["q2_model_spec_sha256"] = metadata["q2_model_spec_sha256"]
    ordered = ["model_id", "model"]
    for scene in ("research", "dialogue", "coding"):
        ordered.extend(
            [
                f"{scene}_utility",
                f"{scene}_rank",
                f"{scene}_top1_probability",
                f"{scene}_top3_probability",
                f"{scene}_utility_low",
                f"{scene}_utility_high",
            ]
        )
    ordered.extend(["q1_freeze_version", "q2_freeze_version", "q2_model_spec_sha256"])
    handoff = handoff[ordered].sort_values("model_id").reset_index(drop=True)
    Q3_HANDOFF.mkdir(parents=True, exist_ok=True)
    path = Q3_HANDOFF / "q2_to_q3_scene_utility.csv"
    handoff.to_csv(path, index=False, encoding="utf-8-sig")
    if len(handoff) != 10 or handoff.isna().any().any():
        raise AssertionError("Q2-to-Q3 wide handoff is incomplete.")
    write(
        DOCS / "q2_to_q3_interface.md",
        f"""# Q2 to Q3 continuous scene-utility interface

## Interface

- File: `q2/q3_handoff/q2_to_q3_scene_utility.csv`
- Rows: 10, one per frozen Q1/Q2 model identity.
- Q1 freeze: `{Q1_FREEZE_VERSION}`.
- Q2 freeze: `{Q2_FREEZE_VERSION}`.
- Q2 model-spec SHA-256: `{metadata['q2_model_spec_sha256']}`.

## Performance variables for Q3

Q3 should use the continuous Q2 CES utilities:

- `research_utility`
- `dialogue_utility`
- `coding_utility`

as the scenario-specific performance variables. Q3 must perform cost-performance and Pareto calculations separately by scenario because the three CES utilities use different core dimensions, weights and substitution parameters.

The corresponding `_utility_low` and `_utility_high` columns are the 95% intervals from Q1 latent-ability uncertainty propagation. `_top1_probability` and `_top3_probability` are explanatory uncertainty measures.

## Rank usage rule

`research_rank`, `dialogue_rank` and `coding_rank` are ordinal variables. Rank does not preserve the size of performance gaps and must not be inserted directly into a numerical performance-cost function. The continuous CES utility preserves the modeled within-scene performance distance and is therefore the Q3 performance-benefit input. Rank may be used only for reporting and interpretation.

Q3 must not replace the Q2 utility with Q1 overall score, a rank-to-score conversion, a benchmark score, or a newly reweighted composite performance index.
""",
    )
    return path


def create_audit_report(
    metadata: dict[str, Any],
    uncertainty_audit: dict[str, Any],
    provenance_audit: dict[str, Any],
    transform_audit: dict[str, Any],
    scene_audit: dict[str, Any],
    pri_audit: dict[str, Any],
    migration_audit: dict[str, Any],
    paper_audit: dict[str, Any],
    pdf_qa_passed: bool,
    q3_path: Path,
) -> Path:
    scores = pd.read_csv(FINAL / "q2_scene_scores.csv")
    uncertainty = pd.read_csv(FINAL / "q2_q1_uncertainty_propagation.csv")
    top_lines = []
    for scene in ("research", "dialogue", "coding"):
        top = scores[scores["scene"] == scene].nsmallest(3, "ces_rank")
        top_lines.append(
            f"- {scene}: " + "; ".join(
                f"{int(row.ces_rank)}. {row.model} ({row.ces_utility:.6f})"
                for row in top.itertuples(index=False)
            )
        )
    kimi_lines = []
    for scene in ("research", "dialogue", "coding"):
        score = scores[(scores["scene"] == scene) & (scores["model_id"] == "kimi_k3_max")].iloc[0]
        unc = uncertainty[(uncertainty["scene"] == scene) & (uncertainty["model_id"] == "kimi_k3_max")].iloc[0]
        kimi_lines.append(
            f"- {scene}: rank {int(score['ces_rank'])}; Top3 probability {unc['probability_top_3']:.4f}."
        )
    statuses = {
        "uncertainty scale": uncertainty_audit["status"],
        "model spec provenance": provenance_audit["status"],
        "CES input transform": transform_audit["status"],
        "scene definition": scene_audit["status"],
        "structural C5": "PASS",
        "PRI": pri_audit["status"],
        "rank migration": migration_audit["status"],
        "paper language": paper_audit["status"],
        "PDF visual QA": "PASS" if pdf_qa_passed else "FAIL",
    }
    ready = all(value == "PASS" for value in statuses.values())
    report = FINAL / "Q2_FINAL_AUDIT_REPORT.md"
    write(
        report,
        "\n".join(
            [
                "# Q2 final audit report",
                "",
                "## Data",
                "",
                f"- Q1 freeze version: `{Q1_FREEZE_VERSION}`",
                f"- Q1 data commit: `{Q1_DATA_COMMIT}`",
                f"- Q2 code commit: `{metadata['git_commit']}`",
                f"- Q2 freeze version: `{Q2_FREEZE_VERSION}`",
                f"- Q2 model-spec SHA-256: `{metadata['q2_model_spec_sha256']}`",
                "",
                "## Audit",
                "",
                *[f"- {key}: {value}" for key, value in statuses.items()],
                "",
                "## Results",
                "",
                *top_lines,
                "",
                "### Kimi K3",
                "",
                *kimi_lines,
                "",
                "## Robustness",
                "",
                "- alpha-rho: 9 x 13 = 117 settings per scene and prior, with KL re-solved at every alpha.",
                "- prior: Q1 objective prior and equal prior rerun from the frozen scene constraints.",
                "- input transform: BT latent strength primary plus delta=0.10-0.30 positive-floor sensitivity.",
                "- uncertainty: 2000 draws using audited latent-theta SD, seed 20260817.",
                "- C5: anchor 0.20-0.50 sensitivity plus C1-C3 common-dimension dialogue rerun.",
                "",
                "## Artifacts",
                "",
                "- `sections/q2_final.tex`",
                "- `paper/q2_standalone.tex`",
                "- `output/pdf/Q2_Final_Paper.pdf`",
                "- `outputs/q2/final/q2_freeze_manifest.csv`",
                f"- `{q3_path.relative_to(ROOT).as_posix()}`",
                "",
                f"`Q2_READY_TO_FREEZE = {'TRUE' if ready else 'FALSE'}`",
                f"`Q2_READY_FOR_PAPER_MERGE = {'TRUE' if ready else 'FALSE'}`",
                f"`Q2_READY_FOR_Q3_HANDOFF = {'TRUE' if ready else 'FALSE'}`",
            ]
        ),
    )
    if not ready:
        raise AssertionError(f"Final Q2 audit is not ready: {statuses}")
    return report


def freeze_outputs() -> pd.DataFrame:
    FREEZE.mkdir(parents=True, exist_ok=True)
    records = []
    for name in REQUIRED_FREEZE_FILES:
        source = FINAL / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = FREEZE / name
        shutil.copy2(source, target)
        records.append(
            {
                "freeze_version": Q2_FREEZE_VERSION,
                "source_path": source.relative_to(ROOT).as_posix(),
                "frozen_path": target.relative_to(ROOT).as_posix(),
                "size_bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )
    manifest = pd.DataFrame(records)
    manifest.to_csv(FINAL / "q2_freeze_manifest.csv", index=False, encoding="utf-8-sig")
    manifest.to_csv(FREEZE / "q2_freeze_manifest.csv", index=False, encoding="utf-8-sig")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q1-bootstrap-theta", required=True, type=Path)
    parser.add_argument("--pdf-qa-passed", action="store_true")
    args = parser.parse_args()
    if not args.pdf_qa_passed:
        raise PermissionError("Final freeze requires an explicit completed PDF visual QA flag.")
    if not PDF.is_file() or PDF.stat().st_size == 0:
        raise FileNotFoundError(PDF)

    metadata_path = FINAL / "q2_run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    uncertainty = pd.read_csv(FINAL / "q2_q1_uncertainty_propagation.csv")

    uncertainty_audit = audit_uncertainty_scale(args.q1_bootstrap_theta.resolve())
    provenance_audit = audit_model_spec(metadata)
    transform_audit, scene_audit = audit_transformation_and_scenes(spec)
    pri_audit, migration_audit = audit_pri_and_migration()
    paper_audit = audit_paper_language()
    if paper_audit["status"] != "PASS":
        raise AssertionError(f"Paper wording audit failed: {paper_audit['hits']}")
    q3_path = create_q3_handoff(metadata, uncertainty)

    metadata["q2_freeze_version"] = Q2_FREEZE_VERSION
    metadata["final_audits"] = {
        "Q1_UNCERTAINTY_SCALE_AUDIT": uncertainty_audit["status"],
        "MODEL_SPEC_PROVENANCE_AUDIT": provenance_audit["status"],
        "CES_INPUT_AUDIT": transform_audit["status"],
        "SCENE_DEFINITION_AUDIT": scene_audit["status"],
        "C5_POLICY_AUDIT": "PASS",
        "PRI_AUDIT": pri_audit["status"],
        "RANK_MIGRATION_AUDIT": migration_audit["status"],
        "PAPER_LANGUAGE_AUDIT": paper_audit["status"],
        "PDF_VISUAL_QA": "PASS",
    }
    metadata["q3_wide_handoff"] = {
        "path": q3_path.relative_to(ROOT).as_posix(),
        "sha256": sha256(q3_path),
        "rows": 10,
    }
    metadata["final_pdf"] = {
        "path": PDF.relative_to(ROOT).as_posix(),
        "sha256": sha256(PDF),
        "size_bytes": PDF.stat().st_size,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    create_audit_report(
        metadata,
        uncertainty_audit,
        provenance_audit,
        transform_audit,
        scene_audit,
        pri_audit,
        migration_audit,
        paper_audit,
        args.pdf_qa_passed,
        q3_path,
    )
    manifest = freeze_outputs()
    print("Q2 final audit and freeze complete")
    print(f"freeze_version={Q2_FREEZE_VERSION}")
    print(f"freeze_files={len(manifest)}")
    print(f"q3_handoff={q3_path.relative_to(ROOT).as_posix()}")
    print("Q2_READY_TO_FREEZE = TRUE")
    print("Q2_READY_FOR_PAPER_MERGE = TRUE")
    print("Q2_READY_FOR_Q3_HANDOFF = TRUE")


if __name__ == "__main__":
    main()
