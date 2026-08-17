from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "q2" / "final"
Q3_OUT = ROOT / "q2" / "outputs"
Q2_METADATA = ROOT / "q2" / "metadata"
FIG = ROOT / "figures" / "q2"
SPEC = ROOT / "q2" / "model_spec_v1.yaml"
SCENES = {"research", "dialogue", "coding"}
REQUIRED = {
    "ces_input_transformation_audit.csv",
    "q2_scene_weights.csv",
    "q2_scene_scores.csv",
    "q2_scene_rankings.csv",
    "q2_linear_vs_ces.csv",
    "q2_pri.csv",
    "q2_marginal_effects.csv",
    "q2_rank_migration.csv",
    "q2_parameter_robustness.csv",
    "q2_prior_sensitivity.csv",
    "q2_q1_uncertainty_propagation.csv",
    "q2_missingness_sensitivity.csv",
    "q2_kimi_analysis.csv",
    "q2_model_spec_snapshot.yaml",
    "q2_run_metadata.json",
}
Q3_REQUIRED = {
    "scenario_utility.csv",
    "scenario_utility_summary.csv",
    "scenario_utility_bootstrap.csv",
    "q2_to_q3_validation.csv",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    missing = sorted(name for name in REQUIRED if not (OUT / name).is_file())
    if missing:
        raise AssertionError(f"Missing formal outputs: {missing}")
    missing_q3 = sorted(name for name in Q3_REQUIRED if not (Q3_OUT / name).is_file())
    if missing_q3:
        raise AssertionError(f"Missing Q2-to-Q3 outputs: {missing_q3}")
    for document in ("q2_to_q3_interface.md", "q2_final_status.md"):
        if not (Q2_METADATA / document).is_file():
            raise AssertionError(f"Missing Q2-to-Q3 metadata document: {document}")
    metadata = json.loads((OUT / "q2_run_metadata.json").read_text(encoding="utf-8"))
    if metadata["q2_model_spec_sha256"] != digest(SPEC):
        raise AssertionError("Model-spec hash mismatch.")
    if digest(SPEC) != digest(OUT / "q2_model_spec_snapshot.yaml"):
        raise AssertionError("Model-spec snapshot differs from the frozen source.")

    weights = pd.read_csv(OUT / "q2_scene_weights.csv")
    active = weights[weights["active_in_scene"]]
    sums = active.groupby(["scene", "prior"])["weight"].sum()
    if not np.allclose(sums.to_numpy(), 1.0, atol=1e-9):
        raise AssertionError(f"Scene weights do not sum to one: {sums.to_dict()}")

    scores = pd.read_csv(OUT / "q2_scene_scores.csv")
    if set(scores["scene"]) != SCENES or len(scores) != 30:
        raise AssertionError("Formal score table must contain 10 models in each of 3 scenes.")
    if scores[["ces_utility", "linear_utility", "pri"]].isna().any().any():
        raise AssertionError("Formal score table contains missing utilities or PRI.")
    if not scores["ces_utility"].between(0.0, 1.00001).all():
        raise AssertionError("CES utilities are outside the transformed ability scale.")
    if not scores["pri"].between(-1e-10, 1.0).all():
        raise AssertionError("PRI is outside its valid range.")
    for _, group in scores.groupby("scene"):
        if sorted(group["ces_rank"].tolist()) != list(range(1, 11)):
            raise AssertionError("Each scene must have a complete rank permutation 1..10.")

    marginal = pd.read_csv(OUT / "q2_marginal_effects.csv")
    if (marginal["marginal_utility"] <= 0).any():
        raise AssertionError("CES marginal utilities must be positive.")
    share_sums = marginal.groupby(["model_id", "scene"])["inner_share"].sum()
    if not np.allclose(share_sums.to_numpy(), 1.0, atol=1e-9):
        raise AssertionError("CES inner shares do not sum to one.")

    audit = pd.read_csv(OUT / "ces_input_transformation_audit.csv")
    c5_absent = audit[(audit["dimension"] == "C5") & (audit["C5_status"] == "STRUCTURAL_CAPABILITY_ABSENCE")]
    if len(c5_absent) != 3 or c5_absent["raw_q1_theta"].notna().any():
        raise AssertionError("C5 structural absence was not preserved as latent NA.")
    if not np.allclose(c5_absent["z_primary_latent_strength"], 0.35):
        raise AssertionError("C5 structural availability anchor differs from the frozen specification.")

    uncertainty = pd.read_csv(OUT / "q2_q1_uncertainty_propagation.csv")
    if len(uncertainty) != 30 or set(uncertainty["draws"]) != {2000}:
        raise AssertionError("Q1 uncertainty propagation is incomplete.")
    if not uncertainty[["probability_rank_1", "probability_top_3"]].apply(lambda s: s.between(0, 1).all()).all():
        raise AssertionError("Uncertainty probabilities are invalid.")

    kimi = pd.read_csv(OUT / "q2_kimi_analysis.csv")
    if set(kimi["scene"]) != SCENES or len(kimi) != 3:
        raise AssertionError("Kimi analysis must cover all three scenes.")

    utility = pd.read_csv(Q3_OUT / "scenario_utility.csv")
    expected_interface_scenes = {"Research", "General", "Coding"}
    if len(utility) != 30 or utility["model_id"].nunique() != 10:
        raise AssertionError("Nominal Q2-to-Q3 utility must contain 10 models x 3 scenes.")
    if set(utility["scenario_code"]) != expected_interface_scenes:
        raise AssertionError("Q2-to-Q3 scenario codes are invalid.")
    if utility.duplicated(["model_id", "scenario_code"]).any():
        raise AssertionError("Duplicate nominal Q2-to-Q3 utility keys.")
    if utility[["utility", "utility_rank"]].isna().any().any():
        raise AssertionError("Missing nominal Q2-to-Q3 utility or rank.")
    if not np.isfinite(utility["utility"]).all():
        raise AssertionError("Non-finite nominal Q2-to-Q3 utility.")
    if utility["model_setting"].isna().any() or utility["model_setting"].eq("").any():
        raise AssertionError("Q2-to-Q3 model_setting is incomplete.")
    for _, group in utility.groupby("scenario_code"):
        if sorted(group["utility_rank"].astype(int).tolist()) != list(range(1, 11)):
            raise AssertionError("Q2-to-Q3 ranks are not a complete 1..10 permutation.")

    scene_map = {"research": "Research", "dialogue": "General", "coding": "Coding"}
    score_compare = scores[["model_id", "scene", "ces_utility", "ces_rank"]].copy()
    score_compare["scenario_code"] = score_compare["scene"].map(scene_map)
    joined = utility.merge(
        score_compare,
        on=["model_id", "scenario_code"],
        validate="one_to_one",
    )
    if not np.allclose(joined["utility"], joined["ces_utility"], atol=1e-15, rtol=0.0):
        raise AssertionError("Q2 paper/formal utilities differ from the Q3 interface.")
    if not (joined["utility_rank"].astype(int) == joined["ces_rank"].astype(int)).all():
        raise AssertionError("Q2 paper/formal ranks differ from the Q3 interface.")

    summary = pd.read_csv(Q3_OUT / "scenario_utility_summary.csv")
    if len(summary) != 30:
        raise AssertionError("Q2-to-Q3 utility summary is incomplete.")

    bootstrap = pd.read_csv(Q3_OUT / "scenario_utility_bootstrap.csv")
    if len(bootstrap) != 60000 or bootstrap["bootstrap_id"].nunique() != 2000:
        raise AssertionError("Q2-to-Q3 bootstrap utility must contain 2000 x 10 x 3 rows.")
    if bootstrap.duplicated(["bootstrap_id", "model_id", "scenario_code"]).any():
        raise AssertionError("Duplicate Q2-to-Q3 bootstrap utility keys.")
    if bootstrap["utility"].isna().any() or not np.isfinite(bootstrap["utility"]).all():
        raise AssertionError("Q2-to-Q3 bootstrap utilities are incomplete or non-finite.")
    per_draw = bootstrap.groupby(["bootstrap_id", "scenario_code"])["model_id"].nunique()
    if len(per_draw) != 6000 or not per_draw.eq(10).all():
        raise AssertionError("Each bootstrap draw/scene must contain all 10 model IDs.")

    interface_validation = pd.read_csv(Q3_OUT / "q2_to_q3_validation.csv")
    if interface_validation.empty or not interface_validation["status"].eq("PASS").all():
        raise AssertionError("Q2-to-Q3 validation report contains a failed check.")
    interface_meta = metadata.get("q2_to_q3_interface", {})
    if interface_meta.get("freeze_version") != "Q2_SCENARIO_UTILITY_v1.0":
        raise AssertionError("Q2-to-Q3 freeze version is missing or unexpected.")
    for field in (
        "Q2_MODEL_READY",
        "Q2_FINAL_Q1_INPUT_READY",
        "Q2_SCENARIO_UTILITY_READY",
        "Q2_SCENARIO_UTILITY_VALIDATED",
        "Q2_BOOTSTRAP_UTILITY_READY",
        "Q2_TO_Q3_INTERFACE_READY",
        "Q2_PAPER_RESULTS_MATCH_INTERFACE",
    ):
        if interface_meta.get(field) is not True:
            raise AssertionError(f"Q2-to-Q3 readiness field is not true: {field}")
    for item in interface_meta.get("interface_files", []):
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item["sha256"]:
            raise AssertionError(f"Q2-to-Q3 interface hash mismatch: {path}")

    bootstrap_stats = (
        bootstrap.groupby(["model_id", "scenario_code"], as_index=False)["utility"]
        .agg(
            utility_mean="mean",
            utility_ci_low=lambda values: values.quantile(0.025),
            utility_ci_high=lambda values: values.quantile(0.975),
        )
    )
    uncertainty_compare = uncertainty[
        ["model_id", "scene", "utility_mean", "utility_ci_low", "utility_ci_high"]
    ].copy()
    uncertainty_compare["scenario_code"] = uncertainty_compare["scene"].map(scene_map)
    uncertainty_compare = uncertainty_compare.drop(columns="scene")
    statistics = bootstrap_stats.merge(
        uncertainty_compare,
        on=["model_id", "scenario_code"],
        suffixes=("_interface", "_formal"),
        validate="one_to_one",
    )
    for column in ("utility_mean", "utility_ci_low", "utility_ci_high"):
        if not np.allclose(
            statistics[f"{column}_interface"],
            statistics[f"{column}_formal"],
            atol=1e-15,
            rtol=0.0,
        ):
            raise AssertionError(f"Bootstrap interface does not reproduce formal {column}.")

    for stem in (
        "q2_fig1_framework",
        "q2_fig2_scene_weights",
        "q2_fig3_utility_heatmap",
        "q2_fig4_rank_migration",
        "q2_fig5_kimi_alpha_rho",
        "q2_fig6_kimi_mechanism",
    ):
        for suffix in (".pdf", ".png"):
            path = FIG / f"{stem}{suffix}"
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing figure: {path}")

    print("Q2 final verification passed")
    print(f"spec_sha256={digest(SPEC)}")
    print(f"score_rows={len(scores)}, uncertainty_rows={len(uncertainty)}")
    print(
        f"q2_to_q3_nominal_rows={len(utility)}, "
        f"q2_to_q3_bootstrap_rows={len(bootstrap)}, "
        f"interface_checks={len(interface_validation)}"
    )
    print(f"PRI_range=[{scores.pri.min():.8f}, {scores.pri.max():.8f}]")


if __name__ == "__main__":
    main()
