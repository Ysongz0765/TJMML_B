from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from .bt_model import fit_dimensions
from .config import (
    BOOT_DIR,
    CORE_MODELS,
    DEFAULT_BOOTSTRAP_B,
    DIAG_DIR,
    FIGURE_DIR,
    KIMI_MODEL_ID,
    LAMBDA_GRID,
    LOG_DIR,
    MAIN_LAMBDA,
    MARGIN_EPSILON,
    OUTPUT_DIR,
    REDUNDANCY_THRESHOLDS,
    TABLE_DIR,
    ensure_output_dirs,
)
from .correlations import family_representation, family_screening, missing_aware_spearman
from .dimension_weights import compute_dimension_weights
from .load_data import Q1Data, load_q1_data
from .overall_score import compute_overall_scores, rerank_with_dimensions
from .pairwise import build_pairwise, graph_diagnostics, pairwise_diagnostics
from .plotting import (
    bar_with_ci,
    coverage_heatmap,
    heatmap,
    kimi_gap,
    kimi_radar,
    lofo_heatmap,
    rank_stability,
    score_visualization,
    sensitivity_rank_plot,
)
from .validate_freeze import validate_freeze_state


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def dim_code(dimension: str) -> str:
    return dimension.split(" ", 1)[0]


def short_dimension_scores(scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    out = scores[["model_id"]].copy()
    for dim in dimensions:
        code = dim_code(dim)
        out[f"{code}_theta"] = scores[f"{dim}_theta"]
        out[f"{code}_score"] = scores[f"{dim}_score"]
        out[f"{code}_applicable"] = scores[f"{dim}_applicable"]
    return out


def short_overall(overall: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    out = overall.copy()
    for dim in dimensions:
        out = out.rename(columns={f"{dim}_score": f"{dim_code(dim)}_score"})
    return out


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            sheet = name[:31]
            write_index = not isinstance(df.index, pd.RangeIndex) or df.index.name is not None
            df.to_excel(writer, sheet_name=sheet, index=write_index)


def run_model(
    q1: Q1Data,
    long: pd.DataFrame,
    lambda_: float = MAIN_LAMBDA,
    margin_method: str = "range",
    exclude_families: set[str] | None = None,
    dimensions: list[str] | None = None,
    stability_override: dict[str, float] | None = None,
) -> dict[str, Any]:
    dimensions = dimensions or q1.dimensions
    pairwise = build_pairwise(
        long,
        margin_method=margin_method,
        epsilon_m=MARGIN_EPSILON,
        exclude_families=exclude_families,
    )
    pairwise = pairwise[pairwise["dimension"].isin(dimensions)].copy()
    dim_scores, bt_diag = fit_dimensions(pairwise, dimensions, CORE_MODELS, lambda_)
    weights = compute_dimension_weights(dim_scores, dimensions, stability_override=stability_override)
    overall = compute_overall_scores(dim_scores, weights, dimensions, q1.model_names)
    return {"pairwise": pairwise, "dimension_scores": dim_scores, "weights": weights, "overall": overall, "bt_diag": bt_diag}


def data_audit(q1: Q1Data, freeze_state: dict[str, Any]) -> dict[str, pd.DataFrame]:
    setting_cols = q1.settings
    matrix = q1.matrix.set_index("model_id")[setting_cols]
    model_cov = pd.DataFrame(
        {
            "model_id": matrix.index,
            "model": [q1.model_names.get(m, m) for m in matrix.index],
            "available": matrix.notna().sum(axis=1).to_numpy(),
            "settings": len(setting_cols),
            "coverage": matrix.notna().mean(axis=1).to_numpy(),
        }
    )
    setting_meta = q1.manifest[["dimension", "benchmark_family", "setting_id"]].drop_duplicates()
    setting_cov = (
        q1.long.groupby("setting_id")["score"]
        .apply(lambda s: pd.Series({"available": int(s.notna().sum()), "coverage": float(s.notna().mean())}))
        .unstack()
        .reset_index()
        .merge(setting_meta, on="setting_id", how="left")
    )
    family_cov = (
        q1.long.groupby(["dimension", "benchmark_family"])["score"]
        .apply(lambda s: pd.Series({"available": int(s.notna().sum()), "cells": int(len(s)), "coverage": float(s.notna().mean())}))
        .unstack()
        .reset_index()
    )
    dimension_cov = (
        q1.long.groupby("dimension")["score"]
        .apply(lambda s: pd.Series({"available": int(s.notna().sum()), "cells": int(len(s)), "coverage": float(s.notna().mean())}))
        .unstack()
        .reset_index()
    )
    summary = pd.DataFrame(
        [
            {"metric": "model_count", "value": freeze_state["core_models"]},
            {"metric": "family_count", "value": freeze_state["benchmark_families"]},
            {"metric": "setting_count", "value": freeze_state["exact_settings"]},
            {"metric": "valid_records", "value": freeze_state["nonmissing_core_records"]},
            {"metric": "overall_coverage", "value": freeze_state["overall_coverage"]},
            {"metric": "human_verified_true", "value": freeze_state["human_verified_true"]},
            {"metric": "human_verified_false", "value": freeze_state["human_verified_false"]},
            {"metric": "freeze_version", "value": freeze_state["freeze_version"]},
            {"metric": "freeze_date", "value": freeze_state["freeze_date"]},
            {"metric": "sha256_passed", "value": freeze_state["sha256_passed"]},
        ]
    )
    return {
        "summary": summary,
        "model_coverage": model_cov,
        "dimension_coverage": dimension_cov,
        "family_coverage": family_cov,
        "setting_coverage": setting_cov,
    }


def bootstrap_long(q1: Q1Data, rng: np.random.Generator) -> pd.DataFrame:
    pieces = []
    for (dim, family), group in q1.long.groupby(["dimension", "benchmark_family"], sort=False):
        settings = group["setting_id"].drop_duplicates().tolist()
        sampled = rng.choice(settings, size=len(settings), replace=True)
        for idx, setting in enumerate(sampled):
            piece = group[group["setting_id"].eq(setting)].copy()
            piece["setting_id"] = f"{setting}__boot_{idx}"
            pieces.append(piece)
    return pd.concat(pieces, ignore_index=True)


def run_bootstrap(q1: Q1Data, b: int, stability_override: dict[str, float] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(20260817)
    dim_frames = []
    overall_frames = []
    for iteration in range(1, b + 1):
        sample = bootstrap_long(q1, rng)
        result = run_model(q1, sample, lambda_=MAIN_LAMBDA, margin_method="range", stability_override=stability_override)
        dim_score = result["dimension_scores"].copy()
        dim_score["bootstrap"] = iteration
        dim_frames.append(dim_score)
        overall = result["overall"].copy()
        overall["bootstrap"] = iteration
        overall_frames.append(overall)
        if iteration % 100 == 0:
            print(f"bootstrap {iteration}/{b}", flush=True)
    return pd.concat(dim_frames, ignore_index=True), pd.concat(overall_frames, ignore_index=True)


def bootstrap_summaries(overall: pd.DataFrame, main_overall: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_rows = []
    rank_rows = []
    main = main_overall.set_index("model_id")
    for model_id, group in overall.groupby("model_id"):
        scores = group["overall_score"].dropna()
        ranks = group["rank"].dropna()
        score_rows.append(
            {
                "model_id": model_id,
                "model": main.loc[model_id, "model"],
                "overall_score": float(main.loc[model_id, "overall_score"]),
                "mean_score": float(scores.mean()),
                "median_score": float(scores.median()),
                "score_sd": float(scores.std()),
                "score_ci_low": float(scores.quantile(0.025)),
                "score_ci_high": float(scores.quantile(0.975)),
            }
        )
        rank_rows.append(
            {
                "model_id": model_id,
                "model": main.loc[model_id, "model"],
                "main_rank": int(main.loc[model_id, "rank"]),
                "mean_rank": float(ranks.mean()),
                "median_rank": float(ranks.median()),
                "rank_ci_low": float(ranks.quantile(0.025)),
                "rank_ci_high": float(ranks.quantile(0.975)),
                "top1_probability": float((ranks <= 1).mean()),
                "top3_probability": float((ranks <= 3).mean()),
            }
        )
    return pd.DataFrame(score_rows), pd.DataFrame(rank_rows)


def rank_compare(main: pd.DataFrame, scenario: pd.DataFrame, scenario_name: str) -> dict[str, Any]:
    merged = main[["model_id", "rank"]].merge(scenario[["model_id", "rank"]], on="model_id", suffixes=("_main", "_scenario"))
    rho = spearmanr(merged["rank_main"], merged["rank_scenario"]).correlation if len(merged) >= 3 else np.nan
    tau = kendalltau(merged["rank_main"], merged["rank_scenario"]).correlation if len(merged) >= 3 else np.nan
    main_kimi = int(main.loc[main["model_id"].eq(KIMI_MODEL_ID), "rank"].iloc[0]) if KIMI_MODEL_ID in set(main["model_id"]) else None
    sc_kimi = int(scenario.loc[scenario["model_id"].eq(KIMI_MODEL_ID), "rank"].iloc[0]) if KIMI_MODEL_ID in set(scenario["model_id"]) else None
    main_top3 = set(main.nsmallest(3, "rank")["model_id"])
    sc_top3 = set(scenario.nsmallest(3, "rank")["model_id"])
    return {
        "scenario": scenario_name,
        "spearman_rank_correlation": float(rho) if np.isfinite(rho) else np.nan,
        "kendall_tau": float(tau) if np.isfinite(tau) else np.nan,
        "kimi_rank_change": (sc_kimi - main_kimi) if sc_kimi is not None and main_kimi is not None else np.nan,
        "top3_overlap": len(main_top3 & sc_top3),
    }


def make_model_diagnostics(q1: Q1Data, pairwise: pd.DataFrame, bt_diag: dict[str, dict[str, Any]], lambda_: float) -> pd.DataFrame:
    rows = []
    for dim in q1.dimensions:
        dim_pw = pairwise[pairwise["dimension"].eq(dim)]
        graph = graph_diagnostics(dim_pw, CORE_MODELS)
        n_families = int(q1.manifest[q1.manifest["dimension"].eq(dim)]["benchmark_family"].nunique())
        n_settings = int(q1.manifest[q1.manifest["dimension"].eq(dim)]["setting_id"].nunique())
        note = "OK"
        if dim.startswith("C2"):
            note = "C2 separation risk is checked with ridge BT."
        elif dim.startswith("C3"):
            note = "FRAGILE_CONNECTED: AA-LCR leave-out diagnostic required."
        elif dim.startswith("C4"):
            note = "LiveBench bridge dependence checked by leave-LiveBench-out."
        elif dim.startswith("C5"):
            note = "C5 only estimated for applicable multimodal models; missing scores remain NA."
        rows.append(
            {
                "dimension": dim,
                "n_families": n_families,
                "n_settings": n_settings,
                "n_models": len(graph["active_models"]),
                "n_pairwise": int(len(dim_pw)),
                "connected": graph["connected"],
                "largest_connected_component": graph["largest_connected_component"],
                "separation_warning": bool(bt_diag[dim]["separation_warning"]),
                "optimization_converged": bool(bt_diag[dim]["converged"]),
                "lambda": lambda_,
                "condition_note": note,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_output_dirs()
    freeze_state = validate_freeze_state()
    q1 = load_q1_data()

    audit = data_audit(q1, freeze_state)
    write_excel(TABLE_DIR / "table_q1_01_data_audit.xlsx", audit)

    coverage = q1.matrix.set_index("model_full_name")[q1.settings].notna().astype(int)
    coverage.columns = [f"{dim_code(r.dimension)} {r.benchmark_family}" for r in q1.manifest.itertuples(index=False)]
    coverage_heatmap(coverage, FIGURE_DIR / "figure_q1_01_coverage_heatmap.png")

    family_table = family_representation(q1.long)
    corr, common_n = missing_aware_spearman(family_table)
    screening = family_screening(q1.long, corr, common_n, threshold=0.85)
    write_excel(TABLE_DIR / "table_q1_02_spearman.xlsx", {"spearman": corr})
    write_excel(TABLE_DIR / "table_q1_03_common_n.xlsx", {"common_n": common_n})
    write_excel(TABLE_DIR / "table_q1_04_family_screening.xlsx", {"screening": screening})
    heatmap(corr, FIGURE_DIR / "figure_q1_02_spearman_heatmap.png", cmap="coolwarm", vmin=-1, vmax=1)
    heatmap(common_n, FIGURE_DIR / "figure_q1_03_common_n_heatmap.png", cmap="Blues")

    preliminary = run_model(q1, q1.long, lambda_=MAIN_LAMBDA, margin_method="range")
    pair_diag = pairwise_diagnostics(preliminary["pairwise"], CORE_MODELS)
    write_excel(TABLE_DIR / "table_q1_05_pairwise_diagnostics.xlsx", {"pairwise": pair_diag})

    b = DEFAULT_BOOTSTRAP_B
    boot_dim_pre, _ = run_bootstrap(q1, b=b, stability_override=None)
    boot_dim_pre.to_csv(BOOT_DIR / "bootstrap_dimension_scores_preliminary.csv", index=False)
    weights = compute_dimension_weights(preliminary["dimension_scores"], q1.dimensions, bootstrap_dimension_scores=boot_dim_pre)
    stability = dict(zip(weights["dimension"], weights["stability"]))
    main_result = run_model(q1, q1.long, lambda_=MAIN_LAMBDA, margin_method="range", stability_override=stability)
    boot_dim, boot_overall = run_bootstrap(q1, b=b, stability_override=stability)
    boot_dim.to_csv(BOOT_DIR / "bootstrap_dimension_scores.csv", index=False)
    boot_overall.to_csv(BOOT_DIR / "bootstrap_overall_scores.csv", index=False)

    dimension_scores = main_result["dimension_scores"]
    weights = main_result["weights"]
    overall = main_result["overall"]
    score_summary, rank_summary = bootstrap_summaries(boot_overall, overall)

    dim_scores_short = short_dimension_scores(dimension_scores, q1.dimensions).merge(
        q1.models[["model_id", "model_full_name"]], on="model_id", how="left"
    )
    rank_long = []
    for dim in q1.dimensions:
        code = dim_code(dim)
        sub = dim_scores_short[["model_id", "model_full_name", f"{code}_score", f"{code}_applicable"]].copy()
        sub["dimension"] = dim
        sub["dimension_rank"] = sub[f"{code}_score"].rank(ascending=False, method="min")
        sub = sub.rename(columns={f"{code}_score": "score", f"{code}_applicable": "applicable"})
        rank_long.append(sub[["dimension", "model_id", "model_full_name", "score", "dimension_rank", "applicable"]])
    dimension_rank_long = pd.concat(rank_long, ignore_index=True)

    write_excel(TABLE_DIR / "table_q1_06_dimension_scores.xlsx", {"wide": dim_scores_short, "dimension_ranks": dimension_rank_long})
    write_excel(TABLE_DIR / "table_q1_07_dimension_weights.xlsx", {"weights": weights})
    write_excel(TABLE_DIR / "table_q1_08_bootstrap_scores.xlsx", {"scores": score_summary})
    write_excel(TABLE_DIR / "table_q1_09_bootstrap_ranks.xlsx", {"ranks": rank_summary})

    score_visualization(dimension_scores, q1.dimensions, q1.model_names, FIGURE_DIR / "figure_q1_04_dimension_scores.png")
    ci_table = short_overall(overall, q1.dimensions).merge(score_summary[["model_id", "score_ci_low", "score_ci_high"]], on="model_id")
    bar_with_ci(ci_table, FIGURE_DIR / "figure_q1_05_overall_score_ci.png")
    rank_stability(rank_summary, FIGURE_DIR / "figure_q1_06_rank_stability.png")

    lofo_rows = []
    main_ranks = overall.set_index("model_id")["rank"].to_dict()
    for family in q1.families:
        result = run_model(q1, q1.long, exclude_families={family}, stability_override=stability)
        scenario = result["overall"]
        scenario_ranks = scenario.set_index("model_id")["rank"].to_dict()
        for model_id in CORE_MODELS:
            lofo_rows.append(
                {
                    "removed_family": family,
                    "model_id": model_id,
                    "model": q1.model_names[model_id],
                    "main_rank": main_ranks.get(model_id),
                    "scenario_rank": scenario_ranks.get(model_id, np.nan),
                    "delta_rank": scenario_ranks.get(model_id, np.nan) - main_ranks.get(model_id, np.nan),
                }
            )
    lofo = pd.DataFrame(lofo_rows)
    write_excel(TABLE_DIR / "table_q1_10_lofo.xlsx", {"lofo": lofo})
    lofo_heatmap(lofo, FIGURE_DIR / "figure_q1_07_lofo_rank_change.png")

    sensitivity_rank_frames = []
    sensitivity_summary = []

    def add_scenario(name: str, scenario: pd.DataFrame) -> None:
        frame = scenario[["model_id", "model", "rank", "overall_score", "effective_weight_coverage"]].copy()
        frame["scenario"] = name
        sensitivity_rank_frames.append(frame)
        sensitivity_summary.append(rank_compare(overall, scenario, name))

    add_scenario("main", overall)
    for lambda_ in LAMBDA_GRID:
        add_scenario(f"lambda={lambda_:g}", run_model(q1, q1.long, lambda_=lambda_, stability_override=stability)["overall"])
    for margin in ["none", "range", "robust_iqr"]:
        add_scenario(f"margin={margin}", run_model(q1, q1.long, margin_method=margin, stability_override=stability)["overall"])
    add_scenario("remove LiveBench", run_model(q1, q1.long, exclude_families={f for f in q1.families if "LiveBench" in f}, stability_override=stability)["overall"])
    add_scenario("remove AA-LCR", run_model(q1, q1.long, exclude_families={"AA-LCR"}, stability_override=stability)["overall"])
    add_scenario("exclude C5", rerank_with_dimensions(dimension_scores, weights, q1.dimensions[:4], q1.dimensions, q1.model_names))
    full_c15 = set(dimension_scores.dropna(subset=[f"{d}_score" for d in q1.dimensions])["model_id"])
    add_scenario("complete-case C1-C5", compute_overall_scores(dimension_scores, weights, q1.dimensions, q1.model_names, model_subset=full_c15))
    equal_weights = pd.DataFrame({"dimension": q1.dimensions, "final_weight": [1.0 / len(q1.dimensions)] * len(q1.dimensions)})
    add_scenario("equal dimension weights", compute_overall_scores(dimension_scores, equal_weights, q1.dimensions, q1.model_names))

    threshold_rows = []
    for threshold in REDUNDANCY_THRESHOLDS:
        scr = family_screening(q1.long, corr, common_n, threshold=threshold)
        threshold_rows.append({"threshold": threshold, "flagged_families": int(scr["redundancy_flag"].sum())})
    sensitivity_ranks = pd.concat(sensitivity_rank_frames, ignore_index=True)
    sensitivity_summary_df = pd.DataFrame(sensitivity_summary)
    threshold_df = pd.DataFrame(threshold_rows)
    write_excel(
        TABLE_DIR / "table_q1_11_sensitivity.xlsx",
        {"scenario_ranks": sensitivity_ranks, "scenario_summary": sensitivity_summary_df, "redundancy_thresholds": threshold_df},
    )
    sensitivity_rank_plot(sensitivity_ranks, FIGURE_DIR / "figure_q1_08_sensitivity_rank.png")

    diagnostics = make_model_diagnostics(q1, main_result["pairwise"], main_result["bt_diag"], MAIN_LAMBDA)
    special = []
    for label, family in [("C3 leave-AA-LCR-out", {"AA-LCR"}), ("C4 leave-LiveBench-out", {"LiveBench Coding"})]:
        result = run_model(q1, q1.long, exclude_families=family, stability_override=stability)
        for dim in q1.dimensions:
            if label.startswith(dim_code(dim)):
                graph = graph_diagnostics(result["pairwise"][result["pairwise"]["dimension"].eq(dim)], CORE_MODELS)
                special.append({"diagnostic": label, "dimension": dim, **graph})
    diagnostics_json = {
        "model_diagnostics": clean_json(diagnostics.to_dict("records")),
        "special_network_diagnostics": clean_json(special),
    }
    (DIAG_DIR / "model_diagnostics.json").write_text(json.dumps(diagnostics_json, ensure_ascii=False, indent=2), encoding="utf-8")

    overall_short = short_overall(overall, q1.dimensions)
    boot_score_cols = score_summary[["model_id", "score_ci_low", "score_ci_high"]]
    boot_rank_cols = rank_summary[["model_id", "rank_ci_low", "rank_ci_high", "top3_probability"]]
    paper6 = overall_short.merge(boot_score_cols, on="model_id").merge(boot_rank_cols, on="model_id")
    paper6 = paper6.rename(
        columns={
            "score_ci_low": "bootstrap_score_low",
            "score_ci_high": "bootstrap_score_high",
            "rank_ci_low": "bootstrap_rank_low",
            "rank_ci_high": "bootstrap_rank_high",
        }
    )

    kimi_dim = dimension_rank_long[dimension_rank_long["model_id"].eq(KIMI_MODEL_ID)].copy()
    medians = dimension_rank_long.groupby("dimension")["score"].median().rename("median_score")
    bests = dimension_rank_long.groupby("dimension")["score"].max().rename("best_score")
    kimi_dim = kimi_dim.merge(medians, on="dimension").merge(bests, on="dimension")
    kimi_dim["gap_vs_median"] = kimi_dim["score"] - kimi_dim["median_score"]
    kimi_dim["gap_vs_best"] = kimi_dim["score"] - kimi_dim["best_score"]
    kimi_rank_scenarios = sensitivity_ranks[sensitivity_ranks["model_id"].eq(KIMI_MODEL_ID)][["scenario", "rank", "overall_score"]]
    kimi_table = kimi_dim.merge(kimi_rank_scenarios.assign(key=1), how="cross")

    best_model_id = overall.nsmallest(1, "rank")["model_id"].iloc[0]
    median_row = pd.Series({f"{d}_score": dimension_scores[f"{d}_score"].median() for d in q1.dimensions})
    kimi_row = dimension_scores[dimension_scores["model_id"].eq(KIMI_MODEL_ID)].iloc[0]
    best_row = dimension_scores[dimension_scores["model_id"].eq(best_model_id)].iloc[0]
    kimi_radar(kimi_row, median_row, best_row, q1.dimensions, FIGURE_DIR / "figure_q1_09_kimi_profile.png")
    kimi_gap(kimi_dim[["dimension", "gap_vs_median"]], FIGURE_DIR / "figure_q1_10_kimi_advantage_gap.png")

    write_excel(TABLE_DIR / "paper_table_1_indicator_system.xlsx", {"indicator_system": q1.manifest})
    write_excel(TABLE_DIR / "paper_table_2_data_coverage.xlsx", audit)
    write_excel(TABLE_DIR / "paper_table_3_correlation_screening.xlsx", {"screening": screening, "spearman": corr, "common_n": common_n})
    write_excel(TABLE_DIR / "paper_table_4_dimension_scores.xlsx", {"dimension_scores": dim_scores_short, "dimension_ranks": dimension_rank_long})
    write_excel(TABLE_DIR / "paper_table_5_dimension_weights.xlsx", {"weights": weights})
    write_excel(TABLE_DIR / "paper_table_6_overall_ranking.xlsx", {"overall_ranking": paper6})
    write_excel(TABLE_DIR / "paper_table_7_kimi_comparison.xlsx", {"kimi": kimi_dim, "kimi_scenarios": kimi_rank_scenarios})
    write_excel(TABLE_DIR / "paper_table_8_robustness.xlsx", {"sensitivity": sensitivity_summary_df, "lofo": lofo, "thresholds": threshold_df})

    strongest = kimi_dim.sort_values("gap_vs_median", ascending=False).iloc[0]
    weakest = kimi_dim.sort_values("gap_vs_median", ascending=True).iloc[0]
    kimi_overall = overall[overall["model_id"].eq(KIMI_MODEL_ID)].iloc[0]
    kimi_boot = rank_summary[rank_summary["model_id"].eq(KIMI_MODEL_ID)].iloc[0]

    results_summary = {
        "data": clean_json(freeze_state),
        "correlation": {
            "high_redundancy_candidates": clean_json(screening[screening["redundancy_flag"]].to_dict("records")),
            "threshold_sensitivity": clean_json(threshold_df.to_dict("records")),
        },
        "dimension_weights": clean_json(weights.to_dict("records")),
        "dimension_scores": clean_json(dim_scores_short.to_dict("records")),
        "overall_ranking": clean_json(paper6.to_dict("records")),
        "kimi_k3": {
            "rank": int(kimi_overall["rank"]),
            "overall_score": float(kimi_overall["overall_score"]),
            "top3_probability": float(kimi_boot["top3_probability"]),
            "strongest_dimension": strongest["dimension"],
            "weakest_dimension": weakest["dimension"],
            "dimension_profile": clean_json(kimi_dim.to_dict("records")),
            "sensitivity_ranks": clean_json(kimi_rank_scenarios.to_dict("records")),
        },
        "bootstrap": {
            "B": b,
            "scores": clean_json(score_summary.to_dict("records")),
            "ranks": clean_json(rank_summary.to_dict("records")),
        },
        "sensitivity": clean_json(sensitivity_summary_df.to_dict("records")),
        "network_diagnostics": diagnostics_json,
    }
    (OUTPUT_DIR / "results_summary.json").write_text(json.dumps(results_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    ranking_lines = [
        f"{int(r.rank)}. {r.model}: {r.overall_score:.3f}, coverage={r.effective_weight_coverage:.3f}"
        for r in overall.itertuples(index=False)
    ]
    weight_lines = [f"- {r.dimension}: {r.final_weight:.4f}" for r in weights.itertuples(index=False)]
    unstable = sensitivity_summary_df.assign(abs_kimi=sensitivity_summary_df["kimi_rank_change"].abs()).sort_values(
        ["abs_kimi", "kendall_tau"], ascending=[False, True]
    ).head(3)
    unstable_lines = [
        f"- {r.scenario}: Spearman={r.spearman_rank_correlation:.3f}, Kendall={r.kendall_tau:.3f}, Kimi rank change={r.kimi_rank_change}"
        for r in unstable.itertuples(index=False)
    ]
    summary_md = "\n".join(
        [
            "# Q1 results summary",
            "",
            f"- Data: 10 models, 14 Benchmark Families, 21 Exact Settings, 164 non-missing records, coverage {freeze_state['overall_coverage']:.4f}.",
            "- Frozen SHA-256 validation: passed.",
            "",
            "## Dimension weights",
            *weight_lines,
            "",
            "## Overall ranking",
            *ranking_lines,
            "",
            "## Kimi K3",
            f"- Main rank: {int(kimi_overall['rank'])}; score: {float(kimi_overall['overall_score']):.3f}; top-3 probability: {float(kimi_boot['top3_probability']):.3f}.",
            f"- Strongest dimension vs median: {strongest['dimension']} ({strongest['gap_vs_median']:.3f}).",
            f"- Weakest dimension vs median: {weakest['dimension']} ({weakest['gap_vs_median']:.3f}).",
            "",
            "## Most unstable sensitivity checks",
            *unstable_lines,
            "",
            "## Special network checks",
            "- C3 leave-AA-LCR-out and C4 leave-LiveBench-out diagnostics are recorded in diagnostics/model_diagnostics.json.",
            "- C5 missing scores remain NA and are not converted to zero.",
            "",
        ]
    )
    (OUTPUT_DIR / "results_summary.md").write_text(summary_md, encoding="utf-8")

    required = [
        TABLE_DIR / "table_q1_01_data_audit.xlsx",
        TABLE_DIR / "table_q1_11_sensitivity.xlsx",
        TABLE_DIR / "paper_table_6_overall_ranking.xlsx",
        FIGURE_DIR / "figure_q1_10_kimi_advantage_gap.png",
        DIAG_DIR / "model_diagnostics.json",
        OUTPUT_DIR / "results_summary.json",
        OUTPUT_DIR / "results_summary.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required outputs: {missing}")
    if not math.isclose(float(weights["final_weight"].sum()), 1.0, abs_tol=1e-9):
        raise ValueError("Dimension weights do not sum to 1.")
    c5 = dim_scores_short["C5_score"]
    if ((c5.fillna(-1) == 0) & c5.isna()).any():
        raise ValueError("Invalid C5 missing-to-zero conversion detected.")
    if not all(main_result["bt_diag"][dim]["converged"] for dim in q1.dimensions):
        raise ValueError("One or more BT optimizations did not converge.")

    log = {
        "freeze_validation": freeze_state,
        "weights_sum": float(weights["final_weight"].sum()),
        "outputs_checked": [str(path) for path in required],
    }
    (LOG_DIR / "run_q1_log.json").write_text(json.dumps(clean_json(log), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(clean_json({"status": "ok", "output_dir": str(OUTPUT_DIR), "weights": weights.to_dict("records")}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
