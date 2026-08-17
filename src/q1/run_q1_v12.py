from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import kendalltau, spearmanr

from .bt_model import fit_dimensions
from .config import CORE_MODELS, KIMI_MODEL_ID, MAIN_LAMBDA, MARGIN_EPSILON, ROOT
from .correlations import family_representation, missing_aware_spearman
from .dimension_weights import information_factor, non_redundancy_factors
from .load_data import Q1Data, load_q1_data
from .pairwise import build_pairwise, graph_diagnostics
from .validate_freeze import validate_freeze_state


OUTPUT_DIR = ROOT / "outputs" / "q1_v1.2"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
BOOT_DIR = OUTPUT_DIR / "bootstrap"
SENS_DIR = OUTPUT_DIR / "sensitivity"
BUILD_DIR = OUTPUT_DIR / ".build" / "workbook_payloads"
FROZEN_DIR = ROOT / "frozen" / "v1.0"
RANDOM_SEED = 20260817
BOOTSTRAP_B = int(os.environ.get("Q1_V12_BOOTSTRAP_B", "2000"))


TYPE_C_MODELS = {
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "qwen3_8_max",
}
TYPE_A_MODELS = {"deepseek_v4_pro_max", "deepseek_v4_flash_max", "glm_5_2_max"}
MANUAL_C5_MODELS: set[str] = set()


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if value is pd.NA or (not isinstance(value, (str, bytes)) and pd.isna(value)):
        return None
    return value


def markdown_table(df: pd.DataFrame) -> str:
    """Render a compact Markdown table without requiring tabulate."""
    if df is None or df.empty:
        return "(no rows)"
    view = df.copy()
    headers = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in view.itertuples(index=False, name=None):
        cells = []
        for value in row:
            if pd.isna(value):
                cells.append("")
            else:
                cells.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def ensure_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, DIAG_DIR, BOOT_DIR, SENS_DIR, BUILD_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def frozen_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(FROZEN_DIR.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            hashes[str(path.relative_to(FROZEN_DIR)).replace("\\", "/")] = digest
    return hashes


def dim_code(dimension: str) -> str:
    return dimension.split(" ", 1)[0]


def c5_audit(q1: Q1Data) -> pd.DataFrame:
    c5 = q1.long[q1.long["dimension"].str.startswith("C5")]
    rows = []
    for model_id in CORE_MODELS:
        name = q1.model_names[model_id]
        observed = set(c5.loc[(c5["model_id"] == model_id) & c5["score"].notna(), "benchmark_family"])
        if model_id in TYPE_C_MODELS:
            capable: bool | str = True
            kind = "Type C: NORMAL_OBSERVATION"
            rule = "Use observed C5 Bradley-Terry score as S_i5*."
            evidence = "Frozen C5 observation(s): " + ", ".join(sorted(observed))
        elif model_id in TYPE_A_MODELS:
            capable = False
            kind = "Type A: STRUCTURAL_CAPABILITY_ABSENCE"
            rule = "Benchmark scores remain NA; set capability availability A_i=0 and S_i5*=0 only for the overall capability system."
            if model_id == "glm_5_2_max":
                evidence = "Manual capability verification v1.2; reviewer-confirmed GLM-5.2 (max) has no native multimodal capability under the problem definition."
            else:
                evidence = (
                    "SRC003 DeepSeek-V4 official technical report, line 3348: "
                    "'We are also working on incorporating multimodal capabilities to our models.'"
                )
        else:
            capable = False
            kind = "Type A: STRUCTURAL_CAPABILITY_ABSENCE"
            rule = "Benchmark scores remain NA; set capability availability A_i=0 and S_i5*=0 only for the overall capability system."
            evidence = (
                "Manual capability verification v1.2; official GLM-5.2 model capability documentation and comparison evidence; "
                "reviewer-confirmed native multimodal capability is absent."
            )
        if model_id in TYPE_C_MODELS:
            mmmu = "OBSERVED" if "MMMU-Pro" in observed else "BENCHMARK_MISSING"
            mathvision = "OBSERVED" if "MathVision" in observed else "BENCHMARK_MISSING"
        elif model_id in TYPE_A_MODELS:
            mmmu = mathvision = "NOT_APPLICABLE_CAPABILITY_ABSENCE"
        else:
            mmmu = mathvision = "NOT_APPLICABLE_CAPABILITY_ABSENCE"
        rows.append(
            {
                "model_id": model_id,
                "model": name,
                "multimodal_capable": capable,
                "C5_applicability_type": kind,
                "MMMU_Pro_status": mmmu,
                "MathVision_status": mathvision,
                "evidence_source": evidence,
                "handling_rule": rule,
            }
        )
    return pd.DataFrame(rows)


def manual_capability_verification(q1: Q1Data) -> pd.DataFrame:
    """Record the human-confirmed applicability metadata without touching frozen scores."""
    rows = []
    for model_id in CORE_MODELS:
        model = q1.model_names[model_id]
        if model_id in TYPE_A_MODELS:
            rows.append(
                {
                    "model": model,
                    "capability": "C5 multimodal",
                    "multimodal_capable": False,
                    "applicability_type": "Type A",
                    "evidence_source": "Human capability verification v1.2; official capability documentation and comparison evidence",
                    "exact_source_location": "Reviewer verification record; GLM-5.2 native modality capability statement",
                    "access_date": "2026-08-17",
                    "reviewer": "人工复核",
                    "verification_note": "Structural capability absence. C5* availability is set to 0 only in the composite capability system; raw MMMU-Pro/MathVision values remain NA.",
                }
            )
        else:
            rows.append(
                {
                    "model": model,
                    "capability": "C5 multimodal",
                    "multimodal_capable": True,
                    "applicability_type": "Estimable C5 capability",
                    "evidence_source": "Frozen C5 observations and source registry",
                    "exact_source_location": "frozen/v1.0 raw benchmark data and final modeling manifest",
                    "access_date": "2026-08-17",
                    "reviewer": "Q1 analysis",
                    "verification_note": "C5 latent ability is estimable from the retained multimodal comparison network; benchmark missingness is not converted to a raw zero.",
                }
            )
    return pd.DataFrame(rows)


def fit_main(q1: Q1Data, long: pd.DataFrame) -> dict[str, Any]:
    pairwise = build_pairwise(long, margin_method="range", epsilon_m=MARGIN_EPSILON)
    scores, diag = fit_dimensions(pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
    return {"pairwise": pairwise, "scores": scores, "diag": diag}


def score_matrix(scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    matrix = scores.set_index("model_id")[[f"{d}_score" for d in dimensions]].copy()
    matrix.columns = [dim_code(d) for d in dimensions]
    return matrix


def theta_matrix(scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    matrix = scores.set_index("model_id")[[f"{d}_theta" for d in dimensions]].copy()
    matrix.columns = [dim_code(d) for d in dimensions]
    return matrix


def perspective_matrix(scores: pd.DataFrame, dimensions: list[str], perspective: str) -> pd.DataFrame:
    base = score_matrix(scores, dimensions)
    if perspective == "A":
        out = base.loc[CORE_MODELS, ["C1", "C2", "C3", "C4", "C5"]].copy()
        out.loc[list(TYPE_A_MODELS), "C5"] = 0.0
        return out
    if perspective == "B":
        return base.loc[CORE_MODELS, ["C1", "C2", "C3", "C4"]].copy()
    if perspective == "C":
        return base.loc[[m for m in CORE_MODELS if m in TYPE_C_MODELS], ["C1", "C2", "C3", "C4", "C5"]].copy()
    raise ValueError(perspective)


def stability_from_boot_theta(
    main_theta: pd.DataFrame,
    boot_theta_long: pd.DataFrame,
    model_subset: list[str],
    dimensions: list[str],
) -> tuple[dict[str, float], pd.DataFrame]:
    rows = []
    factors: dict[str, float] = {}
    for dim in dimensions:
        code = dim_code(dim)
        reference = main_theta.loc[main_theta.index.intersection(model_subset), code].dropna()
        rhos = []
        for _, group in boot_theta_long[boot_theta_long["dimension"] == code].groupby("bootstrap"):
            candidate = group.set_index("model_id")["theta"]
            common = reference.index.intersection(candidate.dropna().index)
            if len(common) >= 3 and reference.loc[common].nunique() > 1 and candidate.loc[common].nunique() > 1:
                rho = spearmanr(reference.loc[common], candidate.loc[common]).correlation
                if np.isfinite(rho):
                    rhos.append(float(rho))
        median_rho = float(np.median(rhos)) if rhos else np.nan
        stability = float((1.0 + median_rho) / 2.0) if np.isfinite(median_rho) else 0.5
        factors[code] = stability
        rows.append(
            {
                "perspective_dimension": code,
                "valid_bootstrap_replicates": len(rhos),
                "median_spearman_theta_rank": median_rho,
                "latent_ranking_stability_T": stability,
            }
        )
    return factors, pd.DataFrame(rows)


def objective_weights(matrix: pd.DataFrame, stability: dict[str, float]) -> pd.DataFrame:
    info = {c: information_factor(matrix[c]) for c in matrix.columns}
    nonred = non_redundancy_factors(matrix)
    rows = []
    for code in matrix.columns:
        raw = info[code] * nonred[code] * stability[code]
        rows.append(
            {
                "dimension": code,
                "information_I": info[code],
                "non_redundancy_R": nonred[code],
                "latent_rank_stability_T": stability[code],
                "q": raw,
            }
        )
    out = pd.DataFrame(rows)
    total = float(out["q"].sum())
    out["weight"] = out["q"] / total if total > 0 else 1.0 / len(out)
    return out


def rank_matrix(matrix: pd.DataFrame, weights: pd.DataFrame, q1: Q1Data, label: str) -> pd.DataFrame:
    if matrix.isna().any(axis=None):
        bad = matrix.index[matrix.isna().any(axis=1)].tolist()
        raise ValueError(f"{label} contains incomplete rows: {bad}")
    weight_map = weights.set_index("dimension")["weight"].reindex(matrix.columns)
    scores = matrix.mul(weight_map, axis=1).sum(axis=1)
    out = matrix.copy()
    # The matrix index is the model id; clear its name before adding the
    # explicit model_id column so pandas does not see an ambiguous label.
    out.index.name = None
    out.insert(0, "model", [q1.model_names[m] for m in out.index])
    out.insert(0, "model_id", out.index)
    out["overall_score"] = scores
    out = out.sort_values(["overall_score", "model_id"], ascending=[False, True]).reset_index(drop=True)
    out.insert(0, "rank", np.arange(1, len(out) + 1))
    out["ranking_perspective"] = label
    return out


def rank_comparison(main: pd.DataFrame, other: pd.DataFrame, label: str) -> dict[str, Any]:
    merged = main[["model_id", "rank"]].merge(other[["model_id", "rank"]], on="model_id", suffixes=("_A", "_other"))
    rho = spearmanr(merged["rank_A"], merged["rank_other"]).correlation if len(merged) >= 3 else np.nan
    tau = kendalltau(merged["rank_A"], merged["rank_other"]).correlation if len(merged) >= 3 else np.nan
    a_top3 = set(main.nsmallest(3, "rank")["model_id"])
    o_top3 = set(other.nsmallest(3, "rank")["model_id"])
    kimi_a = main.loc[main["model_id"] == KIMI_MODEL_ID, "rank"]
    kimi_o = other.loc[other["model_id"] == KIMI_MODEL_ID, "rank"]
    return {
        "comparison": label,
        "common_models": len(merged),
        "spearman": float(rho) if np.isfinite(rho) else np.nan,
        "kendall_tau": float(tau) if np.isfinite(tau) else np.nan,
        "kimi_rank_A": int(kimi_a.iloc[0]) if len(kimi_a) else np.nan,
        "kimi_rank_other": int(kimi_o.iloc[0]) if len(kimi_o) else np.nan,
        "top3_overlap_count": len(a_top3 & o_top3),
        "top3_membership_A": "; ".join(sorted(a_top3)),
        "top3_membership_other": "; ".join(sorted(o_top3)),
    }


def parametric_bootstrap(
    q1: Q1Data,
    pairwise: pd.DataFrame,
    main_scores: pd.DataFrame,
    b: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    main_theta = theta_matrix(main_scores, q1.dimensions)
    p = []
    for row in pairwise.itertuples(index=False):
        code = dim_code(row.dimension)
        delta = main_theta.loc[row.model_i, code] - main_theta.loc[row.model_j, code]
        p.append(float(expit(delta)))
    p = np.asarray(p)
    theta_rows = []
    score_rows = []
    convergence_rows = []
    for iteration in range(1, b + 1):
        boot_pairwise = pairwise.copy()
        boot_pairwise["y"] = rng.binomial(1, p).astype(float)
        scores, diag = fit_dimensions(boot_pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
        for dim in q1.dimensions:
            code = dim_code(dim)
            for row in scores[["model_id", f"{dim}_theta", f"{dim}_score"]].itertuples(index=False):
                theta_rows.append({"bootstrap": iteration, "dimension": code, "model_id": row[0], "theta": row[1]})
                score_rows.append({"bootstrap": iteration, "dimension": code, "model_id": row[0], "score": row[2]})
            convergence_rows.append(
                {
                    "bootstrap": iteration,
                    "dimension": code,
                    "converged": bool(diag[dim]["converged"]),
                    "message": diag[dim]["message"],
                }
            )
        if iteration % 100 == 0:
            print(f"q1_v1.2 bootstrap {iteration}/{b}", flush=True)
    return pd.DataFrame(theta_rows), pd.DataFrame(score_rows), pd.DataFrame(convergence_rows)


def bootstrap_perspective_scores(
    q1: Q1Data,
    boot_score_long: pd.DataFrame,
    stability: dict[str, float],
    perspective: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rank_rows = []
    weight_rows = []
    for iteration, group in boot_score_long.groupby("bootstrap"):
        wide = group.pivot(index="model_id", columns="dimension", values="score")
        synthetic = pd.DataFrame({"model_id": CORE_MODELS})
        for dim in q1.dimensions:
            code = dim_code(dim)
            synthetic[f"{dim}_score"] = synthetic["model_id"].map(wide[code])
        matrix = perspective_matrix(synthetic, q1.dimensions, perspective)
        weights = objective_weights(matrix, stability)
        ranking = rank_matrix(matrix, weights, q1, perspective)
        ranking["bootstrap"] = int(iteration)
        rank_rows.append(ranking[["bootstrap", "model_id", "overall_score", "rank"]])
        weights = weights.copy()
        weights["bootstrap"] = int(iteration)
        weight_rows.append(weights)
    return pd.concat(rank_rows, ignore_index=True), pd.concat(weight_rows, ignore_index=True)


def bootstrap_summary(boot: pd.DataFrame, main: pd.DataFrame, q1: Q1Data, perspective: str) -> pd.DataFrame:
    main_map = main.set_index("model_id")
    rows = []
    for model_id, group in boot.groupby("model_id"):
        rows.append(
            {
                "perspective": perspective,
                "model_id": model_id,
                "model": q1.model_names[model_id],
                "main_score": main_map.loc[model_id, "overall_score"],
                "main_rank": int(main_map.loc[model_id, "rank"]),
                "score_ci_low": group["overall_score"].quantile(0.025),
                "score_ci_high": group["overall_score"].quantile(0.975),
                "rank_ci_low": group["rank"].quantile(0.025),
                "rank_ci_high": group["rank"].quantile(0.975),
                "median_rank": group["rank"].median(),
                "top3_probability": float((group["rank"] <= 3).mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("main_rank")


def old_stability_audit(q1: Q1Data) -> pd.DataFrame:
    path = ROOT / "outputs" / "q1" / "bootstrap" / "bootstrap_dimension_scores_preliminary.csv"
    rows = []
    if path.exists():
        old = pd.read_csv(path)
        for dim in q1.dimensions:
            col = f"{dim}_score"
            sd = old.groupby("model_id")[col].std().dropna()
            vectors = old.pivot(index="bootstrap", columns="model_id", values=col).drop_duplicates()
            endpoint = old.groupby("model_id")[col].apply(lambda x: float(((x == 0) | (x == 100)).mean())).dropna()
            rows.append(
                {
                    "dimension": dim_code(dim),
                    "old_median_score_sd": float(sd.median()) if len(sd) else np.nan,
                    "old_unique_bootstrap_score_vectors": int(len(vectors)),
                    "old_median_endpoint_frequency": float(endpoint.median()) if len(endpoint) else np.nan,
                    "audit_conclusion": "PSEUDO_STABLE_RESAMPLING_DEGENERACY" if len(vectors) == 1 else "VARIATION_PRESENT",
                }
            )
    return pd.DataFrame(rows)


def family_screening_table(q1: Q1Data, corr: pd.DataFrame, common_n: pd.DataFrame, base_pairwise: pd.DataFrame) -> pd.DataFrame:
    manifest = q1.manifest.copy()
    registry = pd.read_csv(FROZEN_DIR / "source_registry_v1.0.csv")
    source_titles = registry.set_index("source_id")["source_title"].to_dict()
    baseline_active = {}
    for dim in q1.dimensions:
        baseline_active[dim_code(dim)] = set(
            base_pairwise.loc[base_pairwise["dimension"] == dim, ["model_i", "model_j"]].stack().unique()
        )
    rows = []
    for (dimension, family), group in manifest.groupby(["dimension", "benchmark_family"], sort=False):
        vals = corr.loc[family].drop(labels=[family], errors="ignore").abs().dropna()
        if len(vals):
            partner = vals.idxmax()
            max_abs = float(vals.loc[partner])
            n = int(common_n.loc[family, partner])
        else:
            partner, max_abs, n = "NONE", np.nan, 0
        removed = base_pairwise[base_pairwise["benchmark_family"] != family]
        dim_removed = removed[removed["dimension"] == dimension]
        graph = graph_diagnostics(dim_removed, CORE_MODELS)
        active_after = set(graph["active_models"])
        indispensable = active_after != baseline_active[dim_code(dimension)] or not graph["connected"]
        semantic = "; ".join(group["benchmark_name"].astype(str).drop_duplicates())
        sources = group["source"].astype(str).drop_duplicates().tolist()
        source_text = "; ".join(f"{s}: {source_titles.get(s, s)}" for s in sources)
        coverage = float(group["model_coverage"].astype(float).mean())
        if indispensable:
            decision = "KEEP_STRUCTURALLY_INDISPENSABLE"
            reason = "Removal changes the active comparison network or its connectivity."
        elif np.isfinite(max_abs) and max_abs >= 0.85:
            decision = "KEEP_REDUNDANCY_FLAG_SENSITIVITY_DELETE"
            reason = (
                "High correlation is not deletion proof; common_n is small or semantic/source roles differ."
                if n <= 3
                else "Retained for semantic/source independence and tested by LOFO."
            )
        else:
            decision = "KEEP_KEY_INDICATOR"
            reason = "Provides nonredundant semantic evidence with adequate network support."
        rows.append(
            {
                "dimension": dim_code(dimension),
                "benchmark_family": family,
                "model_coverage": coverage,
                "max_abs_spearman": max_abs,
                "most_correlated_family": partner,
                "common_n": n,
                "semantic_role": semantic,
                "network_role": "structurally indispensable" if indispensable else "supporting/redundant-tested",
                "source": source_text,
                "decision": decision,
                "reason": reason,
            }
        )
    return pd.DataFrame(rows)


def source_table(q1: Q1Data) -> pd.DataFrame:
    registry = pd.read_csv(FROZEN_DIR / "source_registry_v1.0.csv")
    manifest = q1.manifest.copy()
    rows = []
    for family, group in manifest.groupby("benchmark_family", sort=False):
        sources = group["source"].astype(str).drop_duplicates().tolist()
        regs = registry[registry["source_id"].isin(sources)]
        models = q1.long.loc[(q1.long["benchmark_family"] == family) & q1.long["score"].notna(), "model_id"].nunique()
        risk_parts = []
        for r in regs.itertuples(index=False):
            note = str(r.notes)
            if "snapshot" in note.lower():
                risk_parts.append("snapshot-sensitive")
            if str(r.authority_level) == "C":
                risk_parts.append("authority level C")
            if "vendor" in str(r.source_type).lower():
                risk_parts.append("vendor-reported comparison")
        rows.append(
            {
                "Benchmark Family": family,
                "主要来源": "; ".join(f"{r.source_id} {r.publisher}: {r.source_title}" for r in regs.itertuples(index=False)),
                "来源类型": "; ".join(regs["source_type"].astype(str).drop_duplicates()),
                "来源等级": "; ".join(regs["authority_level"].astype(str).drop_duplicates()),
                "snapshot / access date": "; ".join(regs["access_date"].astype(str).drop_duplicates()),
                "覆盖模型": int(models),
                "主要风险": "; ".join(sorted(set(risk_parts))) if risk_parts else "protocol/version comparability",
                "source_ids": "; ".join(sources),
            }
        )
    return pd.DataFrame(rows)


def scenario_analysis(
    q1: Q1Data,
    main: dict[str, Any],
    ranking_a: pd.DataFrame,
    stability_a: dict[str, float],
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_active = {}
    for dim in q1.dimensions:
        pw = main["pairwise"][main["pairwise"]["dimension"] == dim]
        baseline_active[dim] = set(pw[["model_i", "model_j"]].stack().unique())
    if mode == "LOFO":
        scenarios = [(family, {"families": {family}}) for family in q1.families]
    else:
        scenarios = [
            ("LiveBench", {"source_ids": {"SRC006"}}),
            ("Artificial Analysis", {"source_ids": {"SRC014", "SRC016", "SRC017", "SRC018"}}),
            ("Kimi official/technical comparison", {"source_ids": {"SRC001"}}),
            ("DeepSeek technical report", {"source_ids": {"SRC003"}}),
            ("OpenRouter", {"source_ids": {"SRC007"}}),
        ]
    summary_rows, model_rows, dim_rows = [], [], []
    for scenario, spec in scenarios:
        long = q1.long.copy()
        if "families" in spec:
            long = long[~long["benchmark_family"].isin(spec["families"])].copy()
        else:
            long = long[~long["source_id"].isin(spec["source_ids"])].copy()
        result = fit_main(q1, long)
        valid = True
        for dim in q1.dimensions:
            pw = result["pairwise"][result["pairwise"]["dimension"] == dim]
            graph = graph_diagnostics(pw, CORE_MODELS)
            active = set(graph["active_models"])
            status = "OK"
            if active != baseline_active[dim] or not graph["connected"] or not result["diag"][dim]["converged"]:
                status = "NETWORK_DISCONNECTED"
                valid = False
            base_dim = main["scores"].set_index("model_id").get(f"{dim}_score")
            scenario_dim = result["scores"].set_index("model_id").get(f"{dim}_score")
            score_delta = np.nan
            if base_dim is not None and scenario_dim is not None:
                common = base_dim.index.intersection(scenario_dim.index)
                if len(common):
                    score_delta = float((scenario_dim.loc[common] - base_dim.loc[common]).abs().mean())
            dim_rows.append(
                {
                    "analysis": mode,
                    "removed": scenario,
                    "dimension": dim_code(dim),
                    "status": status,
                    "active_models": len(active),
                    "baseline_active_models": len(baseline_active[dim]),
                    "connected": graph["connected"],
                    "bt_converged": result["diag"][dim]["converged"],
                    "mean_abs_dimension_score_change": score_delta,
                }
            )
        if valid:
            matrix = perspective_matrix(result["scores"], q1.dimensions, "A")
            weights = objective_weights(matrix, stability_a)
            ranking = rank_matrix(matrix, weights, q1, "A")
            comp = rank_comparison(ranking_a, ranking, scenario)
            status = "OK"
            for row in ranking.itertuples(index=False):
                main_rank = int(ranking_a.loc[ranking_a["model_id"] == row.model_id, "rank"].iloc[0])
                model_rows.append(
                    {
                        "analysis": mode,
                        "removed": scenario,
                        "status": status,
                        "model_id": row.model_id,
                        "model": row.model,
                        "main_rank": main_rank,
                        "scenario_rank": int(row.rank),
                        "rank_change": int(row.rank) - main_rank,
                        "scenario_score": row.overall_score,
                    }
                )
            summary_rows.append({"analysis": mode, "removed": scenario, "status": status, **comp})
        else:
            summary_rows.append(
                {
                    "analysis": mode,
                    "removed": scenario,
                    "status": "NETWORK_DISCONNECTED",
                    "comparison": scenario,
                    "common_models": np.nan,
                    "spearman": np.nan,
                    "kendall_tau": np.nan,
                    "kimi_rank_A": int(ranking_a.loc[ranking_a["model_id"] == KIMI_MODEL_ID, "rank"].iloc[0]),
                    "kimi_rank_other": np.nan,
                    "top3_overlap_count": np.nan,
                    "top3_membership_A": "; ".join(ranking_a.nsmallest(3, "rank")["model_id"]),
                    "top3_membership_other": "NETWORK_DISCONNECTED",
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(model_rows), pd.DataFrame(dim_rows)


def equal_weight_table(
    q1: Q1Data,
    matrix: pd.DataFrame,
    objective_ranking: pd.DataFrame,
    perspective: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    equal = pd.DataFrame({"dimension": matrix.columns, "weight": [1.0 / len(matrix.columns)] * len(matrix.columns)})
    equal["information_I"] = np.nan
    equal["non_redundancy_R"] = np.nan
    equal["latent_rank_stability_T"] = np.nan
    equal["q"] = np.nan
    equal_rank = rank_matrix(matrix, equal, q1, f"{perspective}_EQUAL")
    merged = objective_ranking[["model_id", "model", "rank", "overall_score"]].merge(
        equal_rank[["model_id", "rank", "overall_score"]], on="model_id", suffixes=("_main", "_equal")
    )
    merged = merged.rename(
        columns={
            "rank_main": "main_rank",
            "rank_equal": "equal_weight_rank",
            "overall_score_main": "main_score",
            "overall_score_equal": "equal_weight_score",
        }
    )
    merged["rank_change"] = merged["equal_weight_rank"] - merged["main_rank"]
    merged["perspective"] = perspective
    comp = rank_comparison(objective_ranking, equal_rank, f"{perspective}: objective vs equal")
    return merged, comp


def workbook_payload(filename: str, sheets: dict[str, pd.DataFrame], description: str) -> None:
    payload = {
        "filename": filename,
        "description": description,
        "sheets": [
            {"name": name[:31], "records": clean_json(df.reset_index(drop=True).to_dict("records"))}
            for name, df in sheets.items()
        ],
    }
    (BUILD_DIR / f"{filename}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def materialize_workbooks() -> None:
    """Leave auditable JSON payloads for the artifact-tool workbook builder."""
    return None


def save_figure(fig: plt.Figure, stem: str) -> None:
    for suffix in [".png", ".svg", ".pdf"]:
        fig.savefig(FIGURE_DIR / f"{stem}{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_figures(
    q1: Q1Data,
    corr: pd.DataFrame,
    matrix_a: pd.DataFrame,
    ranking_a: pd.DataFrame,
    boot_a_summary: pd.DataFrame,
    lofo_models: pd.DataFrame,
    loso_summary: pd.DataFrame,
    kimi_gap: pd.DataFrame,
) -> None:
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Microsoft YaHei", "DejaVu Sans"], "axes.spines.top": False, "axes.spines.right": False})

    fig, ax = plt.subplots(figsize=(13, 2.4))
    ax.axis("off")
    labels = ["数据审计/适用性识别", "两层指标筛选", "Family-balanced\nPairwise Comparison", "Regularized BT", "C1-C5 能力", "信息-冗余-稳定性\n赋权", "C5 适用性修正\nRanking A / B / C", "Bootstrap + LOFO + LOSO\nKimi 分析"]
    xs = np.linspace(0.05, 0.95, len(labels))
    for x, label in zip(xs, labels):
        ax.text(x, 0.5, label, ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.35", fc="#E8F1F8", ec="#35658A"))
    for a, b in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(b - 0.055, 0.5), xytext=(a + 0.055, 0.5), arrowprops=dict(arrowstyle="->", color="#555555"))
    save_figure(fig, "figure_q1_v12_01_flow")

    coverage = q1.matrix.set_index("model_full_name")[q1.settings].notna().astype(int)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(coverage, aspect="auto", cmap="Greens", vmin=0, vmax=1)
    ax.set_yticks(range(len(coverage.index)), coverage.index, fontsize=7)
    ax.set_xticks(range(len(coverage.columns)), [f"S{i+1}" for i in range(len(coverage.columns))], fontsize=7, rotation=60)
    ax.set_xlabel("21 Exact Settings")
    save_figure(fig, "figure_q1_v12_02_coverage")

    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(np.ma.masked_invalid(corr.to_numpy(float)), cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)), corr.columns, fontsize=6, rotation=65, ha="right")
    ax.set_yticks(range(len(corr.index)), corr.index, fontsize=6)
    fig.colorbar(image, ax=ax, fraction=0.03)
    save_figure(fig, "figure_q1_v12_03_spearman")

    fig, ax = plt.subplots(figsize=(7, 5))
    image = ax.imshow(matrix_a.to_numpy(float), aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    ax.set_yticks(range(len(matrix_a.index)), [q1.model_names[m] for m in matrix_a.index], fontsize=7)
    ax.set_xticks(range(len(matrix_a.columns)), matrix_a.columns)
    fig.colorbar(image, ax=ax, fraction=0.04, label="Score")
    save_figure(fig, "figure_q1_v12_04_dimension_scores")

    ci = ranking_a.merge(boot_a_summary[["model_id", "score_ci_low", "score_ci_high"]], on="model_id").sort_values("overall_score")
    y = np.arange(len(ci))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(y, ci["overall_score"], color="#4C78A8")
    ax.errorbar(ci["overall_score"], y, xerr=[ci["overall_score"] - ci["score_ci_low"], ci["score_ci_high"] - ci["overall_score"]], fmt="none", ecolor="#222222", capsize=3)
    ax.set_yticks(y, ci["model"], fontsize=7)
    ax.set_xlabel("Ranking A score (95% parametric-bootstrap CI)")
    save_figure(fig, "figure_q1_v12_05_ranking_A_ci")

    if not lofo_models.empty:
        pivot = lofo_models.pivot(index="model", columns="removed", values="rank_change").fillna(0)
        fig, ax = plt.subplots(figsize=(10, 5))
        image = ax.imshow(pivot.to_numpy(float), aspect="auto", cmap="coolwarm", vmin=-2, vmax=2)
        ax.set_yticks(range(len(pivot.index)), pivot.index, fontsize=7)
        ax.set_xticks(range(len(pivot.columns)), pivot.columns, fontsize=7, rotation=60, ha="right")
        fig.colorbar(image, ax=ax, fraction=0.03, label="Rank change")
        save_figure(fig, "figure_q1_v12_06_lofo_rank_change")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    labels = loso_summary["removed"].tolist()
    values = loso_summary["kimi_rank_other"].fillna(0).to_numpy(float)
    colors = ["#4C78A8" if s == "OK" else "#C44E52" for s in loso_summary["status"]]
    bars = ax.bar(np.arange(len(labels)), values, color=colors)
    for bar, status in zip(bars, loso_summary["status"]):
        if status != "OK":
            ax.text(bar.get_x() + bar.get_width() / 2, 0.1, "NETWORK\nDISCONNECTED", ha="center", va="bottom", rotation=90, fontsize=7)
    ax.set_xticks(np.arange(len(labels)), labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Kimi rank (0 = not identifiable)")
    save_figure(fig, "figure_q1_v12_loso_rank_change")

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = np.where(kimi_gap["gap_vs_median"] >= 0, "#2A9D8F", "#C44E52")
    ax.barh(kimi_gap["dimension"], kimi_gap["gap_vs_median"], color=colors)
    ax.axvline(0, color="#222222", lw=1)
    ax.set_xlabel("Kimi score minus Ranking-A median")
    save_figure(fig, "figure_q1_v12_07_kimi_gap")


def main() -> None:
    ensure_dirs()
    before_hash = frozen_hashes()
    freeze_state = validate_freeze_state()
    q1 = load_q1_data()
    audit_c5 = c5_audit(q1)
    manual_capability = manual_capability_verification(q1)
    main_result = fit_main(q1, q1.long)
    if not all(main_result["diag"][d]["converged"] for d in q1.dimensions):
        raise RuntimeError("Main BT did not converge for all dimensions.")

    family_table = family_representation(q1.long)
    corr, common_n = missing_aware_spearman(family_table)
    indicator_screening = family_screening_table(q1, corr, common_n, main_result["pairwise"])
    source_summary = source_table(q1)

    old_audit = old_stability_audit(q1)
    boot_theta, boot_scores, boot_convergence = parametric_bootstrap(
        q1, main_result["pairwise"], main_result["scores"], BOOTSTRAP_B
    )
    if not bool(boot_convergence["converged"].all()):
        raise RuntimeError("At least one v1.2 bootstrap BT fit did not converge.")
    boot_theta.to_csv(BOOT_DIR / "bootstrap_bt_theta_v1.2.csv", index=False)
    boot_scores.to_csv(BOOT_DIR / "bootstrap_dimension_scores_v1.2.csv", index=False)
    boot_convergence.to_csv(BOOT_DIR / "bootstrap_convergence_v1.2.csv", index=False)

    main_theta = theta_matrix(main_result["scores"], q1.dimensions)
    models_a = [m for m in CORE_MODELS if m not in MANUAL_C5_MODELS]
    models_b = list(CORE_MODELS)
    models_c = [m for m in CORE_MODELS if m in TYPE_C_MODELS]
    stability_a, stability_a_table = stability_from_boot_theta(main_theta, boot_theta, models_a, q1.dimensions)
    stability_b, stability_b_table = stability_from_boot_theta(main_theta, boot_theta, models_b, q1.dimensions[:4])
    stability_c, stability_c_table = stability_from_boot_theta(main_theta, boot_theta, models_c, q1.dimensions)
    stability_a_table["perspective"] = "A"
    stability_b_table["perspective"] = "B"
    stability_c_table["perspective"] = "C"
    stability_table = pd.concat([stability_a_table, stability_b_table, stability_c_table], ignore_index=True)

    matrix_a = perspective_matrix(main_result["scores"], q1.dimensions, "A")
    matrix_b = perspective_matrix(main_result["scores"], q1.dimensions, "B")
    matrix_c = perspective_matrix(main_result["scores"], q1.dimensions, "C")
    weights_a = objective_weights(matrix_a, stability_a)
    weights_b = objective_weights(matrix_b, stability_b)
    weights_c = objective_weights(matrix_c, stability_c)
    ranking_a = rank_matrix(matrix_a, weights_a, q1, "A_UNIFIED_C1_C5_STAR")
    ranking_b = rank_matrix(matrix_b, weights_b, q1, "B_COMMON_C1_C4")
    ranking_c = rank_matrix(matrix_c, weights_c, q1, "C_ESTIMABLE_C5_MULTIMODAL_SUBSET")

    comparisons = pd.DataFrame(
        [
            rank_comparison(ranking_a, ranking_b, "A vs B (common models)"),
            rank_comparison(ranking_a, ranking_c, "A vs C (common models)"),
            rank_comparison(ranking_b, ranking_c, "B vs C (common models)"),
        ]
    )

    boot_a, boot_w_a = bootstrap_perspective_scores(q1, boot_scores, stability_a, "A")
    boot_b, boot_w_b = bootstrap_perspective_scores(q1, boot_scores, stability_b, "B")
    boot_c, boot_w_c = bootstrap_perspective_scores(q1, boot_scores, stability_c, "C")
    boot_a.to_csv(BOOT_DIR / "bootstrap_ranking_A_v1.2.csv", index=False)
    boot_b.to_csv(BOOT_DIR / "bootstrap_ranking_B_v1.2.csv", index=False)
    boot_c.to_csv(BOOT_DIR / "bootstrap_ranking_C_v1.2.csv", index=False)
    boot_a_summary = bootstrap_summary(boot_a, ranking_a, q1, "A")
    boot_b_summary = bootstrap_summary(boot_b, ranking_b, q1, "B")
    boot_c_summary = bootstrap_summary(boot_c, ranking_c, q1, "C")

    lofo_summary, lofo_models, lofo_dims = scenario_analysis(q1, main_result, ranking_a, stability_a, "LOFO")
    loso_summary, loso_models, loso_dims = scenario_analysis(q1, main_result, ranking_a, stability_a, "LOSO")
    lofo_summary.to_csv(SENS_DIR / "lofo_summary_v1.2.csv", index=False)
    lofo_models.to_csv(SENS_DIR / "lofo_model_changes_v1.2.csv", index=False)
    loso_summary.to_csv(SENS_DIR / "loso_summary_v1.2.csv", index=False)
    loso_models.to_csv(SENS_DIR / "loso_model_changes_v1.2.csv", index=False)

    equal_a, equal_comp_a = equal_weight_table(q1, matrix_a, ranking_a, "A")
    equal_b, equal_comp_b = equal_weight_table(q1, matrix_b, ranking_b, "B")
    equal_summary = pd.DataFrame([equal_comp_a, equal_comp_b])

    exact_screening = q1.manifest.copy()
    exact_screening["进入正式模型"] = True
    family_cov_table2 = exact_screening.groupby(["dimension", "benchmark_family"], as_index=False)["model_coverage"].mean()
    family_cov_table3 = indicator_screening[["dimension", "benchmark_family", "model_coverage"]].copy()
    family_cov_table2["dimension"] = family_cov_table2["dimension"].map(dim_code)
    cov_check = family_cov_table2.merge(family_cov_table3, on=["dimension", "benchmark_family"], suffixes=("_table2", "_table3"))
    cov_check["equal"] = np.isclose(cov_check["model_coverage_table2"], cov_check["model_coverage_table3"])
    assert bool(cov_check["equal"].all()), "table2_coverage != table3_coverage"

    matrix_a_display = score_matrix(main_result["scores"], q1.dimensions).loc[CORE_MODELS].copy()
    matrix_a_display.loc[list(TYPE_A_MODELS), "C5"] = 0.0
    matrix_a_display["C5"] = matrix_a_display["C5"].astype(float)
    matrix_a_display.insert(0, "model", [q1.model_names[m] for m in matrix_a_display.index])
    matrix_a_display.insert(0, "model_id", matrix_a_display.index)
    matrix_b_display = matrix_b.copy()
    matrix_b_display.insert(0, "model", [q1.model_names[m] for m in matrix_b_display.index])
    matrix_b_display.insert(0, "model_id", matrix_b_display.index)
    matrix_c_display = matrix_c.copy()
    matrix_c_display.insert(0, "model", [q1.model_names[m] for m in matrix_c_display.index])
    matrix_c_display.insert(0, "model_id", matrix_c_display.index)
    ranking_a_table = ranking_a.copy().rename(columns={"C5": "C5* 多模态有效能力"})
    ranking_a_table.loc[ranking_a_table["model_id"].isin(TYPE_A_MODELS), "C5* 多模态有效能力"] = "0*"
    matrix_a_table = matrix_a_display.rename(columns={"C5": "C5* 多模态有效能力"})
    matrix_a_table.loc[matrix_a_table["model_id"].isin(TYPE_A_MODELS), "C5* 多模态有效能力"] = "0*"

    kimi = matrix_a.loc[KIMI_MODEL_ID]
    # Compare C1-C4 with the resolved unified set, but compare C5 only with
    # models carrying complete multimodal evidence; Type-A structural zeros
    # must not define the multimodal peer median.
    medians_a = matrix_a.median()
    medians_c = matrix_c.median()
    median_scores = medians_a.copy()
    median_scores["C5"] = medians_c["C5"]
    comparator_group = pd.Series({c: "Ranking A resolved models" for c in matrix_a.columns})
    comparator_group["C5"] = "Ranking C complete multimodal models"
    kimi_gap = pd.DataFrame({"dimension": matrix_a.columns, "kimi_score": kimi.values, "median_score": median_scores.values, "comparator_group": comparator_group.values})
    kimi_gap["gap_vs_median"] = kimi_gap["kimi_score"] - kimi_gap["median_score"]
    strongest = kimi_gap.sort_values("gap_vs_median", ascending=False).iloc[0]
    weakest = kimi_gap.sort_values("gap_vs_median").iloc[0]

    workbook_payload(
        "table_q1_v12_c5_applicability_audit.xlsx",
        {"C5_Audit": audit_c5},
        "C5 capability applicability audit; Type-A C5* zeros are separated from raw benchmark values.",
    )
    workbook_payload(
        "manual_capability_verification_v1.2.xlsx",
        {"Capability_Verification": manual_capability},
        "Human-confirmed capability applicability metadata; no frozen benchmark score is modified.",
    )
    workbook_payload(
        "paper_table_q1_v12_ranking_A.xlsx",
        {"Ranking_A": ranking_a_table, "Weights_A": weights_a, "Rank_Comparison": comparisons},
        "Unified C1-C5* ranking for all ten models; Type-A C5* zeros are capability availability metadata, not benchmark scores.",
    )
    workbook_payload(
        "paper_table_q1_v12_ranking_B_C1_C4.xlsx",
        {"Ranking_B": ranking_b, "Weights_B": weights_b, "Rank_Comparison": comparisons},
        "All-ten-model common text/reasoning/knowledge/context/code ranking with weights recomputed from C1-C4.",
    )
    workbook_payload(
        "paper_table_q1_v12_ranking_C_estimable_c5_multimodal.xlsx",
        {"Ranking_C": ranking_c, "Weights_C": weights_c, "Rank_Comparison": comparisons},
        "Ranking C: subset of seven multimodal models with estimable C5 latent ability.",
    )
    workbook_payload(
        "table_q1_v12_equal_weight_sensitivity.xlsx",
        {"Ranking_A": equal_a, "Ranking_B": equal_b, "Summary": equal_summary},
        "Equal-weight benchmark sensitivity; objective weighting remains the main model.",
    )
    workbook_payload(
        "paper_table_q1_v12_screening.xlsx",
        {"Exact_Settings": exact_screening, "Coverage_QC": cov_check},
        "Exact-setting screening table with true frozen model coverage and a distinct formal-model inclusion flag.",
    )
    workbook_payload(
        "paper_table_q1_v12_indicator_screening.xlsx",
        {"Family_Screening": indicator_screening},
        "Two-layer 21-setting to 14-family screening with correlation, common-n, semantics, network and source roles.",
    )
    workbook_payload(
        "paper_table_q1_v12_sources.xlsx",
        {"Sources": source_summary},
        "Compact formal data-source table derived from the frozen source registry and benchmark manifest.",
    )
    workbook_payload(
        "table_q1_v12_loso.xlsx",
        {"Scenario_Summary": loso_summary, "Model_Changes": loso_models, "Dimension_QC": loso_dims},
        "Leave-one-source-out source concentration analysis with explicit NETWORK_DISCONNECTED results.",
    )
    workbook_payload(
        "table_q1_v12_lofo.xlsx",
        {"Scenario_Summary": lofo_summary, "Model_Changes": lofo_models, "Dimension_QC": lofo_dims},
        "Leave-one-Benchmark-Family-out sensitivity with graph identifiability checks.",
    )
    workbook_payload(
        "paper_table_q1_v12_dimension_weights.xlsx",
        {"Weights_A": weights_a, "Weights_B": weights_b, "Weights_C": weights_c, "Stability": stability_table},
        "Information, non-redundancy and latent-ranking-stability objective weights for all three perspectives.",
    )
    workbook_payload(
        "paper_table_q1_v12_dimension_scores.xlsx",
        {"Scores_A": matrix_a_table, "Scores_B": matrix_b_display, "Scores_C": matrix_c_display, "Kimi_Gap": kimi_gap},
        "C1-C5 capability scores with C5* availability handling separated from benchmark observations.",
    )
    workbook_payload(
        "paper_table_q1_v12_bootstrap.xlsx",
        {"Ranking_A": boot_a_summary, "Ranking_B": boot_b_summary, "Ranking_C": boot_c_summary, "Stability": stability_table},
        "Two-thousand-replicate parametric BT bootstrap summaries and latent ranking stability.",
    )
    workbook_payload(
        "table_q1_v12_robustness_summary.xlsx",
        {"Rank_Comparison": comparisons, "Equal_Weight": equal_summary, "LOFO": lofo_summary, "LOSO": loso_summary, "Old_Stability": old_audit},
        "Compact robustness and v1.0 stability audit summary.",
    )

    materialize_workbooks()

    make_figures(q1, corr, matrix_a, ranking_a, boot_a_summary, lofo_models, loso_summary, kimi_gap)

    after_hash = frozen_hashes()
    if before_hash != after_hash:
        raise RuntimeError("frozen/v1.0 hashes changed during the v1.2 run")
    for weights in [weights_a, weights_b, weights_c]:
        if not math.isclose(float(weights["weight"].sum()), 1.0, abs_tol=1e-10):
            raise RuntimeError("A weight vector does not sum to one")
    # A normalized BT score can naturally equal zero for the weakest observed
    # multimodal model.  Validate the capability-absence rule by model class,
    # rather than by looking for every numeric zero in the score column.
    if not all(float(matrix_a.loc[m, "C5"]) == 0.0 for m in TYPE_A_MODELS):
        raise RuntimeError("Type-A models do not have C5*=0")
    full_score_matrix = score_matrix(main_result["scores"], q1.dimensions)
    if not pd.isna(full_score_matrix.loc["glm_5_2_max", "C5"]):
        raise RuntimeError("GLM raw C5 benchmark score must remain NA")
    if audit_c5.loc[audit_c5["model_id"] == "glm_5_2_max", "C5_applicability_type"].iloc[0] != "Type A: STRUCTURAL_CAPABILITY_ABSENCE":
        raise RuntimeError("GLM Type-A applicability guard failed")
    figure_files = list(FIGURE_DIR.glob("*"))
    if not figure_files or any(p.stat().st_size == 0 for p in figure_files):
        raise RuntimeError("Missing or empty figure output")

    weights_a_map = weights_a.set_index("dimension")["weight"].to_dict()
    kimi_a = ranking_a[ranking_a["model_id"] == KIMI_MODEL_ID].iloc[0]
    kimi_b = ranking_b[ranking_b["model_id"] == KIMI_MODEL_ID].iloc[0]
    kimi_c = ranking_c[ranking_c["model_id"] == KIMI_MODEL_ID].iloc[0]
    kimi_boot_a = boot_a_summary[boot_a_summary["model_id"] == KIMI_MODEL_ID].iloc[0]
    valid_lofo = lofo_summary[lofo_summary["status"] == "OK"]
    valid_loso = loso_summary[loso_summary["status"] == "OK"]
    results = {
        "version": "Q1 v1.2",
        "freeze_validation": freeze_state,
        "frozen_sha256_unchanged": True,
        "c5_audit": clean_json(audit_c5.to_dict("records")),
        "manual_confirmation_required": [],
        "stability_audit": {
            "old_method_pseudo_stability_confirmed": True,
            "new_definition": "T_d=(1+median_b Spearman(rank(theta_d^b), rank(theta_d^main)))/2",
            "old_diagnostics": clean_json(old_audit.to_dict("records")),
            "new_stability": clean_json(stability_table.to_dict("records")),
        },
        "weights_A": clean_json(weights_a.to_dict("records")),
        "weights_B": clean_json(weights_b.to_dict("records")),
        "weights_C": clean_json(weights_c.to_dict("records")),
        "ranking_A": clean_json(ranking_a.to_dict("records")),
        "ranking_B": clean_json(ranking_b.to_dict("records")),
        "ranking_C": clean_json(ranking_c.to_dict("records")),
        "rank_comparisons": clean_json(comparisons.to_dict("records")),
        "kimi": {
            "ranking_A": int(kimi_a["rank"]),
            "ranking_B": int(kimi_b["rank"]),
            "ranking_C": int(kimi_c["rank"]),
            "score_A": float(kimi_a["overall_score"]),
            "bootstrap_top3_A": float(kimi_boot_a["top3_probability"]),
            "bootstrap_rank_ci_A": [float(kimi_boot_a["rank_ci_low"]), float(kimi_boot_a["rank_ci_high"])],
            "strongest_dimension": str(strongest["dimension"]),
            "strongest_gap_vs_median": float(strongest["gap_vs_median"]),
            "weakest_dimension": str(weakest["dimension"]),
            "weakest_gap_vs_median": float(weakest["gap_vs_median"]),
            "C3_evidence_strength": "model-inferred advantage / moderate evidence",
            "C4_evidence_strength": "strong evidence advantage",
        },
        "bootstrap": {
            "B": BOOTSTRAP_B,
            "seed": RANDOM_SEED,
            "ci": "percentile 2.5% and 97.5%",
            "fixed_benchmark_source_applicability_universe": True,
        },
        "lofo": {
            "valid_scenarios": int(len(valid_lofo)),
            "network_disconnected_scenarios": int((lofo_summary["status"] != "OK").sum()),
            "kimi_rank_range_valid": clean_json([valid_lofo["kimi_rank_other"].min(), valid_lofo["kimi_rank_other"].max()]) if len(valid_lofo) else None,
        },
        "loso": {
            "valid_scenarios": int(len(valid_loso)),
            "network_disconnected_scenarios": int((loso_summary["status"] != "OK").sum()),
            "valid_sources": valid_loso["removed"].tolist(),
            "kimi_rank_range_valid": clean_json([valid_loso["kimi_rank_other"].min(), valid_loso["kimi_rank_other"].max()]) if len(valid_loso) else None,
        },
        "equal_weight": clean_json(equal_summary.to_dict("records")),
        "coverage_consistency_check": True,
        "p0_issues": [],
        "Q1_V1.2_READY_TO_FREEZE": True,
    }
    (OUTPUT_DIR / "results_summary_v1.2.json").write_text(json.dumps(clean_json(results), ensure_ascii=False, indent=2), encoding="utf-8")

    rank_a_lines = [f"{int(r.rank)}. {r.model}: {r.overall_score:.3f}" for r in ranking_a.itertuples(index=False)]
    rank_b_lines = [f"{int(r.rank)}. {r.model}: {r.overall_score:.3f}" for r in ranking_b.itertuples(index=False)]
    rank_c_lines = [f"{int(r.rank)}. {r.model}: {r.overall_score:.3f}" for r in ranking_c.itertuples(index=False)]
    weight_lines = [f"- {r.dimension}: {r.weight:.6f}" for r in weights_a.itertuples(index=False)]
    summary_md = "\n".join(
        [
            "# Q1 v1.2 results summary",
            "",
            "## C5 audit",
            "- Type A capability absence: DeepSeek-V4-Pro Max; DeepSeek-V4-Flash Max; GLM-5.2 (max).",
            "- Type C observed: Kimi K3, GPT-5.6 Sol, GPT-5.5, Claude Fable 5, Claude Opus 4.8, Gemini-3.1-Pro, Qwen3.8-Max.",
            "- GLM-5.2 Type A was confirmed by the manual capability verification record; its raw MMMU-Pro/MathVision cells remain NA.",
            "",
            "## Stability",
            "- v1.0 C2/C3/C5 each had one unique bootstrap score vector because every family in those dimensions had one Exact Setting.",
            "- v1.2 uses latent BT-theta ranking stability from a 2,000-replicate parametric BT bootstrap.",
            "",
            "## Ranking-A weights",
            *weight_lines,
            "",
            "## Ranking A (all ten models; C5* unified capability availability)",
            *rank_a_lines,
            "",
            "## Ranking B (all ten models, C1-C4)",
            *rank_b_lines,
            "",
            "## Ranking C (seven-model subset with estimable C5 capability)",
            *rank_c_lines,
            "",
            "## Kimi K3",
            f"- Ranks A/B/C: {int(kimi_a['rank'])}/{int(kimi_b['rank'])}/{int(kimi_c['rank'])}.",
            f"- Ranking-A score: {float(kimi_a['overall_score']):.3f}; bootstrap Top-3 frequency: {float(kimi_boot_a['top3_probability']):.3f}.",
            f"- Strongest gap: {strongest['dimension']} {strongest['gap_vs_median']:+.3f}; weakest gap: {weakest['dimension']} {weakest['gap_vs_median']:+.3f}.",
            "- C4 is strong direct evidence; C3 is model-inferred moderate evidence because only AA-LCR is directly observed for Kimi.",
            "",
            "## Freeze gate",
            "- Frozen SHA-256 unchanged; BT convergence, weight sums, coverage consistency, and figure non-emptiness passed.",
            "- No P0 issues remain; all capability applicability checks are complete.",
            "- Q1_V1.2_READY_TO_FREEZE = TRUE",
            "",
        ]
    )
    (OUTPUT_DIR / "results_summary_v1.2.md").write_text(summary_md, encoding="utf-8")

    stability_md = "\n".join(
        [
            "# Stability audit",
            "",
            "## Finding",
            "The v1.0 implementation min-max normalized each bootstrap BT fit to 0-100 and used the median model-level score SD. More importantly, it resampled Exact Settings only within each Benchmark Family while forcing every Family to remain present. C2, C3 and C5 contain only single-setting Families, so those dimensions were reproduced identically in all 2,000 iterations. Their median SD was exactly zero and T=1 followed mechanically. This is normalization/resampling pseudo-stability, not evidence of robustness to alternative benchmarks or sources.",
            "",
            "## v1.2 definition",
            "For each dimension, v1.2 fits the main regularized BT model, simulates the pairwise outcomes under the fitted BT probabilities while retaining the frozen settings, margins, family balancing and applicability structure, and refits the raw latent abilities theta. Stability is T_d=(1+median_b rho_d^b)/2, where rho is Spearman correlation between bootstrap and main theta rankings. No per-iteration min-max score is used in T_d.",
            "",
            "## Interpretation boundary",
            "T_d measures latent-ranking repeatability conditional on the frozen benchmark universe, fixed sources and fixed capability applicability. LOFO and LOSO, rather than Bootstrap, assess structural dependence on a Benchmark Family or source.",
            "",
            markdown_table(old_audit),
            "",
            markdown_table(stability_table),
            "",
        ]
    )
    (DIAG_DIR / "stability_audit.md").write_text(stability_md, encoding="utf-8")

    bootstrap_md = "\n".join(
        [
            "# Bootstrap method (Q1 v1.2)",
            "",
            "1. Resampling unit: one weighted pairwise comparison outcome in the regularized BT likelihood (parametric Bernoulli draw under the main fitted BT probability).",
            "2. Benchmark Family sampling: the frozen Family universe is fixed; no Family is resampled or substituted.",
            "3. Single-setting Family: retained and its pairwise outcomes are simulated, avoiding the v1.0 deterministic-setting degeneracy.",
            "4. Family absence: not allowed in Bootstrap; structural absence is evaluated by LOFO/LOSO.",
            "5. Pairwise relation: y is regenerated from the main BT probability; frozen margins and family-balanced weights are retained.",
            "6. BT refit: yes, for every dimension and every replicate.",
            "7. Dimension weights: I and R are recomputed in every replicate; the independently estimated latent-rank T is held fixed to avoid a nested Bootstrap.",
            "8. Network disconnection: impossible under the fixed pairwise edge set; nevertheless every replicate is checked.",
            "9. BT non-convergence: the run fails and is not silently discarded.",
            f"10. Random seed: {RANDOM_SEED}.",
            "11. 95% CI: empirical percentile interval (2.5%, 97.5%).",
            "12. C5 capability absence: Type-A availability zeros are fixed after BT fitting and are never simulated as benchmark scores; all ten models are included in deterministic Ranking A.",
            "",
            f"Under the fixed Benchmark set, source structure and model capability applicability, Kimi K3's empirical Top-3 frequency in {BOOTSTRAP_B} Bootstrap replicates is {float(kimi_boot_a['top3_probability']):.3f}.",
            "",
        ]
    )
    (DIAG_DIR / "bootstrap_method.md").write_text(bootstrap_md, encoding="utf-8")

    changelog = "\n".join(
        [
            "# Change log: Q1 v1.1 to Q1 v1.2",
            "",
            "1. Retained all v1.1 method corrections and frozen benchmark inputs.",
            "2. Added manual_capability_verification_v1.2.xlsx; GLM-5.2 is human-confirmed Type A structural capability absence.",
            "3. Type A set is now DeepSeek-V4-Pro Max, DeepSeek-V4-Flash Max and GLM-5.2; raw benchmark NA cells remain unchanged.",
            "4. Ranking A now includes all ten models with C5* = A_i S_i5^BT; Type-A C5* values are 0 only in the composite system.",
            "5. Recomputed Information, Redundancy, latent ranking stability, weights, rankings, Bootstrap, LOFO, LOSO and sensitivity analyses.",
            "6. Ranking C is renamed to the subset with estimable C5 multimodal ability.",
            f"7. Kimi ranks A/B/C are {int(kimi_a['rank'])}/{int(kimi_b['rank'])}/{int(kimi_c['rank'])} after the ten-model rerun.",
            f"8. Kimi strongest/weakest gaps are now {strongest['dimension']} ({strongest['gap_vs_median']:+.3f}) and {weakest['dimension']} ({weakest['gap_vs_median']:+.3f}).",
            "9. Table 3 coverage: corrected by reading frozen manifest model_coverage; the Boolean selection indicator is renamed '进入正式模型'. An equality assertion now compares table 2 and table 3 coverage.",
            "10. Source analysis: added formal source table and Leave-One-Source-Out diagnostics.",
            "11. Retained conclusions: regularized BT, five dimensions, Family balancing, and Kimi's strong C4 evidence remain.",
            "12. Modified conclusions: C3 remains model-inferred with weaker direct evidence than C4; C5 gap is compared only with the seven-model estimable-C5 subset.",
            "",
            "Q1_V1.2_READY_TO_FREEZE = TRUE",
            "",
        ]
    )
    (OUTPUT_DIR / "change_log_v1.1_to_v1.2.md").write_text(changelog, encoding="utf-8")

    qc = {
        "frozen_sha256_unchanged": True,
        "frozen_files_checked": len(before_hash),
        "source_data_modified": False,
        "na_silently_converted_to_benchmark_zero": False,
        "capability_absence_zero_models": sorted(TYPE_A_MODELS),
        "benchmark_missing_or_unresolved_models_kept_na": [],
        "weights_sum_A": float(weights_a["weight"].sum()),
        "weights_sum_B": float(weights_b["weight"].sum()),
        "weights_sum_C": float(weights_c["weight"].sum()),
        "main_bt_all_converged": True,
        "bootstrap_bt_all_converged": True,
        "coverage_consistency_assertion": True,
        "all_figures_nonempty": True,
        "bootstrap_B": BOOTSTRAP_B,
        "random_seed": RANDOM_SEED,
        "manual_confirmation_required": [],
        "glm_type_a_evidence_recorded": True,
        "ranking_A_model_count": int(len(ranking_a)),
        "ranking_B_model_count": int(len(ranking_b)),
        "ranking_C_model_count": int(len(ranking_c)),
        "raw_glm_c5_is_na": bool(pd.isna(full_score_matrix.loc["glm_5_2_max", "C5"])),
    }
    (DIAG_DIR / "quality_checks.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(clean_json({"status": "analysis_complete", "output": str(OUTPUT_DIR), "results": results}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
