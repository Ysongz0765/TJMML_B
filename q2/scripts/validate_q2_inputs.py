from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.q1.bt_model import fit_dimensions  # noqa: E402
from src.q1.config import CORE_MODELS, MAIN_LAMBDA, MARGIN_EPSILON  # noqa: E402
from src.q1.load_data import load_q1_data  # noqa: E402
from src.q1.pairwise import build_pairwise  # noqa: E402


Q2 = ROOT / "q2"
DATA = Q2 / "data"
Q1_OUT = ROOT / "outputs" / "q1_v1.2"
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


def fail(message: str) -> None:
    raise AssertionError(message)


def close(a, b, tol: float = 1e-9) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def code(dimension: str) -> str:
    return dimension.split(" ", 1)[0]


def main() -> None:
    with (Q1_OUT / "results_summary_v1.2.json").open(encoding="utf-8") as handle:
        summary = json.load(handle)

    capability = pd.read_csv(DATA / "q1_capability_scores.csv")
    theta = pd.read_csv(DATA / "q1_bt_latent_scores.csv")
    applicability = pd.read_csv(DATA / "q1_model_applicability.csv")
    rankings = pd.read_csv(DATA / "q1_model_rankings.csv")
    weights = pd.read_csv(DATA / "q1_dimension_weights_reference.csv")

    for name, df in [("capability", capability), ("theta", theta), ("applicability", applicability), ("rankings", rankings)]:
        if df["model_id"].nunique() != 10 or len(df) != 10:
            fail(f"{name}: expected 10 unique models")
        if df["model_id"].duplicated().any():
            fail(f"{name}: duplicated model_id")
        if set(df["model_id"]) != set(CORE_MODELS):
            fail(f"{name}: model set mismatch")

    if capability[["C1_score", "C2_score", "C3_score", "C4_score"]].isna().any(axis=None):
        fail("C1-C4 scores must be available for all 10 models")

    for model_id in TYPE_A_MODELS:
        row = capability.set_index("model_id").loc[model_id]
        app = applicability.set_index("model_id").loc[model_id]
        if not pd.isna(row["C5_BT_score"]):
            fail(f"{model_id}: C5_BT_score must remain NA for structural absence")
        if float(row["C5_effective_score"]) != 0.0:
            fail(f"{model_id}: C5_effective_score must be 0")
        if app["C5_status"] != "STRUCTURAL_CAPABILITY_ABSENCE":
            fail(f"{model_id}: C5_status mismatch")

    for model_id in TYPE_C_MODELS:
        row = capability.set_index("model_id").loc[model_id]
        if pd.isna(row["C5_BT_score"]):
            fail(f"{model_id}: C5_BT_score must be available")
        if not close(row["C5_BT_score"], row["C5_effective_score"]):
            fail(f"{model_id}: C5 effective must equal C5 BT")

    if len(summary["ranking_A"]) != 10 or len(summary["ranking_B"]) != 10 or len(summary["ranking_C"]) != 7:
        fail("Q1 summary ranking counts are not 10/10/7")
    if rankings["ranking_A_rank"].notna().sum() != 10:
        fail("Ranking A must contain 10 models")
    if rankings["ranking_B_rank"].notna().sum() != 10:
        fail("Ranking B must contain 10 models")
    if rankings["ranking_C_rank"].notna().sum() != 7:
        fail("Ranking C must contain 7 models")

    if not close(weights["q1_weight"].sum(), 1.0, tol=1e-6):
        fail("Q1 reference weights do not sum to 1")

    q1 = load_q1_data()
    pairwise = build_pairwise(q1.long, margin_method="range", epsilon_m=MARGIN_EPSILON)
    main_scores, diagnostics = fit_dimensions(pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
    if not all(bool(diagnostics[dim]["converged"]) for dim in q1.dimensions):
        fail("BT did not converge for all dimensions")
    main = main_scores.set_index("model_id")

    for model_id in CORE_MODELS:
        cap_row = capability.set_index("model_id").loc[model_id]
        theta_row = theta.set_index("model_id").loc[model_id]
        for dim in ["C1", "C2", "C3", "C4", "C5"]:
            q1_score = main.loc[model_id, f"{next(d for d in q1.dimensions if code(d) == dim)}_score"]
            if dim != "C5" or model_id in TYPE_C_MODELS:
                cap_field = f"{dim}_score" if dim != "C5" else "C5_BT_score"
                if not close(cap_row[cap_field], q1_score):
                    fail(f"{model_id} {dim}: capability score mismatch")
            q1_theta = main.loc[model_id, f"{next(d for d in q1.dimensions if code(d) == dim)}_theta"]
            if not close(theta_row[f"{dim}_theta"], q1_theta):
                fail(f"{model_id} {dim}: theta mismatch")

    ranking_a = {row["model_id"]: row for row in summary["ranking_A"]}
    ranking_b = {row["model_id"]: row for row in summary["ranking_B"]}
    ranking_c = {row["model_id"]: row for row in summary["ranking_C"]}
    for model_id in CORE_MODELS:
        cap_row = capability.set_index("model_id").loc[model_id]
        for dim in ["C1", "C2", "C3", "C4"]:
            if not close(cap_row[f"{dim}_score"], ranking_a[model_id][dim]):
                fail(f"{model_id} {dim}: exported score differs from Q1 Ranking A official output")
        if not close(cap_row["C5_effective_score"], ranking_a[model_id]["C5"]):
            fail(f"{model_id}: C5 effective score differs from Q1 Ranking A")
        rank_row = rankings.set_index("model_id").loc[model_id]
        if int(rank_row["ranking_A_rank"]) != int(ranking_a[model_id]["rank"]):
            fail(f"{model_id}: Ranking A rank mismatch")
        if int(rank_row["ranking_B_rank"]) != int(ranking_b[model_id]["rank"]):
            fail(f"{model_id}: Ranking B rank mismatch")
        if model_id in ranking_c:
            if int(rank_row["ranking_C_rank"]) != int(ranking_c[model_id]["rank"]):
                fail(f"{model_id}: Ranking C rank mismatch")
        elif not pd.isna(rank_row["ranking_C_rank"]):
            fail(f"{model_id}: Ranking C should be NA")

    status = subprocess.run(
        ["git", "status", "--short", "--", "frozen/v1.0", "outputs/q1_v1.2", "sections/q1_v1_2.tex"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    if status:
        fail(f"frozen/Q1 output files modified:\n{status}")

    print("Q2 validation passed")
    print("10 unique models: OK")
    print("C1-C5 values match Q1 v1.2: OK")
    print("C5 applicability preserved: OK")
    print("Ranking counts A/B/C = 10/10/7: OK")
    print("Q1 weights sum to 1: OK")
    print("BT converged: OK")
    print("Frozen and Q1 v1.2 tracked files unchanged: OK")


if __name__ == "__main__":
    main()
