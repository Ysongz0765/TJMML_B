from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib import patches

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.q2.ces import ces_utility
from src.q2.config import EPS, SceneConfig
from src.q2.imbalance_penalty import imbalance_penalty
from src.q2.kl_weights import KLWeightResult, solve_scene_weights
from src.q2.linear_baseline import linear_utility
from src.q2.marginal_analysis import (
    ces_inner_shares,
    ces_marginal_utility,
    ces_utility_elasticity,
)


Q2_DATA = ROOT / "q2" / "data"
SPEC_PATH = ROOT / "q2" / "model_spec_v1.yaml"
OUTPUT = ROOT / "outputs" / "q2" / "final"
Q3_INTERFACE_OUTPUT = ROOT / "q2" / "outputs"
Q2_METADATA = ROOT / "q2" / "metadata"
FIGURE_DIR = ROOT / "figures" / "q2"
GENERATED_DIR = ROOT / "paper" / "generated"
Q1_DATA_COMMIT = "754bc1b541b5b0d27e8b74b75b979849edf72cda"
Q1_RESULTS_COMMIT = "a097c83fb5218ca2f746a63cbfbf5f12e3afd0e6"
Q2_SCENARIO_UTILITY_FREEZE_VERSION = "Q2_SCENARIO_UTILITY_v1.0"
Q2_METHOD = "KL minimum-information shift + CES capability complementarity"
UTILITY_NORMALIZATION = (
    "dimensionwise max-normalized BT latent strength; "
    "scene-specific CES scale; within-scene comparison only"
)
ABILITY_ORDER = ("C1", "C2", "C3", "C4", "C5")
ABILITY_CN = {
    "C1": "复杂推理",
    "C2": "事实可靠",
    "C3": "长上下文",
    "C4": "代码工程",
    "C5": "多模态",
}
SCENE_CN = {
    "research": "科研长文本分析",
    "dialogue": "大众日常对话",
    "coding": "计算机代码开发",
}
SCENARIO_INTERFACE = {
    "research": ("Research", "科研长文本分析"),
    "dialogue": ("General", "大众日常通用对话"),
    "coding": ("Coding", "计算机代码开发"),
}
MODEL_IDENTITY = {
    "kimi_k3_max": ("Kimi K3", "max reasoning", "Kimi K3 (max reasoning)"),
    "gpt_5_6_sol_max": ("GPT-5.6 Sol", "max", "GPT-5.6 Sol (max)"),
    "gpt_5_5_xhigh": ("GPT-5.5", "xhigh", "GPT-5.5 (xhigh)"),
    "claude_fable_5_max": (
        "Claude Fable 5",
        "max, with fallback",
        "Claude Fable 5 (max, with fallback)",
    ),
    "claude_opus_4_8_max": ("Claude Opus 4.8", "max", "Claude Opus 4.8 (max)"),
    "gemini_3_1_pro_high": ("Gemini-3.1-Pro", "High", "Gemini-3.1-Pro (High)"),
    "deepseek_v4_pro_max": ("DeepSeek-V4-Pro", "Max", "DeepSeek-V4-Pro Max"),
    "deepseek_v4_flash_max": ("DeepSeek-V4-Flash", "Max", "DeepSeek-V4-Flash Max"),
    "qwen3_8_max": ("Qwen3.8", "Max", "Qwen3.8-Max"),
    "glm_5_2_max": ("GLM-5.2", "max", "GLM-5.2 (max)"),
}
KIMI_ID = "kimi_k3_max"


@dataclass(frozen=True)
class SceneRuntime:
    key: str
    label: str
    dimensions: tuple[str, ...]
    config: SceneConfig
    alpha_reference: float
    rho_reference: float
    alpha_grid: np.ndarray
    rho_grid: np.ndarray


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


def load_spec() -> tuple[dict[str, Any], str]:
    raw = SPEC_PATH.read_bytes()
    spec_hash = hashlib.sha256(raw).hexdigest()
    spec = yaml.safe_load(raw.decode("utf-8"))
    if spec.get("MODEL_SPEC_FROZEN_BEFORE_RESULTS") is not True:
        raise PermissionError("The Q2 model specification is not frozen.")
    return spec, spec_hash


def load_inputs() -> dict[str, pd.DataFrame]:
    names = {
        "capability": "q1_capability_scores.csv",
        "theta": "q1_bt_latent_scores.csv",
        "applicability": "q1_model_applicability.csv",
        "weights": "q1_dimension_weights_reference.csv",
        "uncertainty": "q1_uncertainty.csv",
        "rankings": "q1_model_rankings.csv",
        "master": "q2_model_master_table.csv",
    }
    frames = {key: pd.read_csv(Q2_DATA / name) for key, name in names.items()}
    expected = set(frames["master"]["model_id"])
    if len(expected) != 10:
        raise ValueError("The formal Q2 run requires exactly 10 Q1 models.")
    for key in ("capability", "theta", "applicability", "rankings"):
        current = set(frames[key]["model_id"])
        if current != expected or frames[key]["model_id"].duplicated().any():
            raise ValueError(f"Model-set mismatch in {key} input.")
    return frames


def build_scene_runtime(spec: dict[str, Any]) -> dict[str, SceneRuntime]:
    result: dict[str, SceneRuntime] = {}
    for key, item in spec["scenes"].items():
        lower = tuple(
            (str(d), float(v)) for d, v in item["kl_constraints"]["lower_bounds"].items()
        )
        orders = tuple(tuple(pair) for pair in item["kl_constraints"]["order_constraints"])
        alpha_range = tuple(float(v) for v in item["alpha_range"])
        rho_range = tuple(float(v) for v in item["rho_range"])
        scene = SceneConfig(
            key=key,
            label=item["label"],
            core_dimensions=tuple(item["kl_focus_dimensions"]),
            alpha_range=alpha_range,
            alpha_development_default=float(item["alpha_reference"]),
            rho_range=rho_range,
            rho_development_default=float(item["rho_reference"]),
            lower_bounds=lower,
            order_constraints=orders,
        )
        result[key] = SceneRuntime(
            key=key,
            label=item["label"],
            dimensions=tuple(item["ces_core_dimensions"]),
            config=scene,
            alpha_reference=float(item["alpha_reference"]),
            rho_reference=float(item["rho_reference"]),
            alpha_grid=np.linspace(*alpha_range, int(item["alpha_grid_size"])),
            rho_grid=np.linspace(*rho_range, int(item["rho_grid_size"])),
        )
    return result


def objective_prior(weights: pd.DataFrame) -> dict[str, float]:
    prior = dict(zip(weights["dimension"], weights["q1_weight"].astype(float)))
    if set(prior) != set(ABILITY_ORDER) or not math.isclose(sum(prior.values()), 1.0, abs_tol=1e-6):
        raise ValueError("Invalid Q1 objective prior.")
    return prior


def restricted_prior(prior: dict[str, float], dimensions: tuple[str, ...]) -> dict[str, float]:
    total = sum(prior[d] for d in dimensions)
    return {d: prior[d] / total for d in dimensions}


def equal_prior(dimensions: tuple[str, ...]) -> dict[str, float]:
    return {d: 1.0 / len(dimensions) for d in dimensions}


def latent_transform(
    theta: pd.DataFrame,
    applicability: pd.DataFrame,
    structural_anchor: float,
) -> pd.DataFrame:
    frame = theta[["model_id", "model", *[f"{d}_theta" for d in ABILITY_ORDER]]].copy()
    status = applicability[["model_id", "C5_status"]]
    frame = frame.merge(status, on="model_id", validate="one_to_one")
    for dimension in ABILITY_ORDER:
        column = f"{dimension}_theta"
        observed = frame[column].dropna().astype(float)
        if observed.empty:
            raise ValueError(f"No estimable latent ability for {dimension}.")
        maximum = float(observed.max())
        frame[dimension] = np.exp(frame[column].astype(float) - maximum)
    absent = frame["C5_status"].eq("STRUCTURAL_CAPABILITY_ABSENCE")
    if frame.loc[absent, "C5_theta"].notna().any():
        raise ValueError("Structural C5 absence must not contain a latent score.")
    frame.loc[absent, "C5"] = float(structural_anchor)
    if frame[list(ABILITY_ORDER)].isna().any().any():
        raise ValueError("Unexpected ordinary missing latent ability in formal inputs.")
    return frame[["model_id", "model", "C5_status", *ABILITY_ORDER]].copy()


def score_floor_transform(
    capability: pd.DataFrame,
    applicability: pd.DataFrame,
    delta: float,
) -> pd.DataFrame:
    frame = capability.merge(
        applicability[["model_id", "C5_status"]], on="model_id", validate="one_to_one"
    )
    for dimension in ("C1", "C2", "C3", "C4"):
        frame[dimension] = float(delta) + (1.0 - float(delta)) * frame[f"{dimension}_score"] / 100.0
    c5_score = frame["C5_BT_score"].where(
        frame["C5_status"].eq("ESTIMABLE"), frame["C5_effective_score"]
    )
    frame["C5"] = float(delta) + (1.0 - float(delta)) * c5_score / 100.0
    if frame[list(ABILITY_ORDER)].isna().any().any():
        raise ValueError("Score-floor mapping produced missing abilities.")
    return frame[["model_id", "model", "C5_status", *ABILITY_ORDER]].copy()


def transformation_audit(
    frames: dict[str, pd.DataFrame], spec: dict[str, Any], primary: pd.DataFrame
) -> pd.DataFrame:
    capability = frames["capability"].merge(
        frames["theta"], on=["model_id", "model"], validate="one_to_one"
    ).merge(
        frames["applicability"][["model_id", "C5_status"]],
        on="model_id",
        validate="one_to_one",
    )
    primary_wide = primary.set_index("model_id")
    theta_maxima = {
        dimension: float(capability[f"{dimension}_theta"].dropna().max())
        for dimension in ABILITY_ORDER
    }
    records: list[dict[str, Any]] = []
    deltas = [float(v) for v in spec["ces_input_transform"]["sensitivity"]["delta_grid"]]
    floor_frames = {
        delta: score_floor_transform(frames["capability"], frames["applicability"], delta).set_index("model_id")
        for delta in deltas
    }
    for row in capability.itertuples(index=False):
        for dimension in ABILITY_ORDER:
            score_field = "C5_BT_score" if dimension == "C5" else f"{dimension}_score"
            raw_score = getattr(row, score_field)
            record: dict[str, Any] = {
                "model_id": row.model_id,
                "model": row.model,
                "dimension": dimension,
                "raw_q1_score": raw_score,
                "raw_q1_theta": getattr(row, f"{dimension}_theta"),
                "C5_status": row.C5_status if dimension == "C5" else "NOT_APPLICABLE",
                "z_primary_latent_strength": primary_wide.loc[row.model_id, dimension],
            }
            structural_c5 = (
                dimension == "C5"
                and row.C5_status == "STRUCTURAL_CAPABILITY_ABSENCE"
            )
            expected_primary = (
                float(spec["c5_structural_absence"]["primary_anchor"])
                if structural_c5
                else math.exp(float(getattr(row, f"{dimension}_theta")) - theta_maxima[dimension])
            )
            record["dimension_theta_max"] = theta_maxima[dimension]
            record["expected_z_primary"] = expected_primary
            record["primary_abs_error"] = abs(
                float(primary_wide.loc[row.model_id, dimension]) - expected_primary
            )
            record["primary_is_finite"] = bool(
                np.isfinite(float(primary_wide.loc[row.model_id, dimension]))
            )
            record["primary_is_strictly_positive"] = bool(
                float(primary_wide.loc[row.model_id, dimension]) > 0.0
            )
            for delta, floor in floor_frames.items():
                record[f"z_score_floor_delta_{delta:.3f}"] = floor.loc[row.model_id, dimension]
            record["structural_note"] = (
                "availability anchor, not benchmark zero and not latent imputation"
                if structural_c5
                else "observed/estimable ability"
            )
            records.append(record)
    return pd.DataFrame(records)


def reference_scene_result(
    ability: pd.DataFrame,
    runtime: SceneRuntime,
    prior: dict[str, float],
    prior_kind: str,
) -> tuple[pd.DataFrame, KLWeightResult]:
    dims = runtime.dimensions
    weight_result = solve_scene_weights(
        restricted_prior(prior, dims) if prior_kind == "q1" else equal_prior(dims),
        runtime.config,
        dims,
        runtime.alpha_reference,
    )
    values = ability[list(dims)].to_numpy(dtype=float)
    weights = np.asarray([weight_result.weights[d] for d in dims], dtype=float)
    utility = np.asarray(ces_utility(values, weights, runtime.rho_reference), dtype=float)
    linear = np.asarray(linear_utility(values, weights), dtype=float)
    penalty, pri = imbalance_penalty(linear, utility)
    shares = ces_inner_shares(values, weights, runtime.rho_reference)
    marginal = ces_marginal_utility(values, weights, runtime.rho_reference)
    elasticity = ces_utility_elasticity(values, weights, runtime.rho_reference)
    table = ability[["model_id", "model"]].copy()
    table["scene"] = runtime.key
    table["scene_label"] = runtime.label
    table["prior"] = prior_kind
    table["alpha"] = runtime.alpha_reference
    table["rho"] = runtime.rho_reference
    table["ces_utility"] = utility
    table["linear_utility"] = linear
    table["imbalance_penalty"] = penalty
    table["pri"] = pri
    table["ces_rank"] = table["ces_utility"].rank(method="min", ascending=False).astype(int)
    table["linear_rank"] = table["linear_utility"].rank(method="min", ascending=False).astype(int)
    table["rank_ces_minus_linear"] = table["ces_rank"] - table["linear_rank"]
    for index, dimension in enumerate(dims):
        table[f"inner_share_{dimension}"] = shares[:, index]
        table[f"marginal_utility_{dimension}"] = marginal[:, index]
        table[f"elasticity_{dimension}"] = elasticity[:, index]
    return table.sort_values(["ces_rank", "model_id"]).reset_index(drop=True), weight_result


def run_parameter_grid(
    ability: pd.DataFrame,
    runtime: SceneRuntime,
    prior: dict[str, float],
    prior_kind: str,
) -> pd.DataFrame:
    dims = runtime.dimensions
    values = ability[list(dims)].to_numpy(dtype=float)
    model_ids = ability["model_id"].to_numpy()
    names = ability["model"].to_numpy()
    records: list[pd.DataFrame] = []
    base_prior = restricted_prior(prior, dims) if prior_kind == "q1" else equal_prior(dims)
    for alpha in runtime.alpha_grid:
        result = solve_scene_weights(base_prior, runtime.config, dims, float(alpha))
        weights = np.asarray([result.weights[d] for d in dims], dtype=float)
        for rho in runtime.rho_grid:
            utility = np.asarray(ces_utility(values, weights, float(rho)), dtype=float)
            block = pd.DataFrame(
                {
                    "model_id": model_ids,
                    "model": names,
                    "scene": runtime.key,
                    "prior": prior_kind,
                    "alpha": float(alpha),
                    "rho": float(rho),
                    "utility": utility,
                    "kl_divergence": result.kl_divergence,
                }
            )
            block["rank"] = block["utility"].rank(method="min", ascending=False).astype(int)
            block["top1"] = block["rank"].eq(1)
            block["top3"] = block["rank"].le(3)
            records.append(block)
    return pd.concat(records, ignore_index=True)


def robustness_summary(grid: pd.DataFrame) -> pd.DataFrame:
    summary = (
        grid.groupby(["scene", "prior", "model_id", "model"], as_index=False)
        .agg(
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
            rank_sd=("rank", "std"),
            top1_proportion=("top1", "mean"),
            top3_proportion=("top3", "mean"),
            mean_utility=("utility", "mean"),
            utility_sd=("utility", "std"),
        )
        .fillna({"rank_sd": 0.0, "utility_sd": 0.0})
    )
    return summary.sort_values(["scene", "prior", "mean_rank", "model_id"]).reset_index(drop=True)


def rank_jump_thresholds(grid: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for keys, group in grid.groupby(["scene", "prior", "model_id", "model", "rho"]):
        ordered = group.sort_values("alpha")
        previous = None
        for row in ordered.itertuples(index=False):
            if previous is not None and int(row.rank) != int(previous.rank):
                records.append(
                    {
                        "scene": keys[0],
                        "prior": keys[1],
                        "model_id": keys[2],
                        "model": keys[3],
                        "varying_parameter": "alpha",
                        "fixed_parameter": float(keys[4]),
                        "from_value": float(previous.alpha),
                        "to_value": float(row.alpha),
                        "rank_from": int(previous.rank),
                        "rank_to": int(row.rank),
                        "rank_jump": int(row.rank) - int(previous.rank),
                    }
                )
            previous = row
    for keys, group in grid.groupby(["scene", "prior", "model_id", "model", "alpha"]):
        ordered = group.sort_values("rho")
        previous = None
        for row in ordered.itertuples(index=False):
            if previous is not None and int(row.rank) != int(previous.rank):
                records.append(
                    {
                        "scene": keys[0],
                        "prior": keys[1],
                        "model_id": keys[2],
                        "model": keys[3],
                        "varying_parameter": "rho",
                        "fixed_parameter": float(keys[4]),
                        "from_value": float(previous.rho),
                        "to_value": float(row.rho),
                        "rank_from": int(previous.rank),
                        "rank_to": int(row.rank),
                        "rank_jump": int(row.rank) - int(previous.rank),
                    }
                )
            previous = row
    return pd.DataFrame(records)


def prior_sensitivity(summary: pd.DataFrame) -> pd.DataFrame:
    q1 = summary[summary["prior"] == "q1"].drop(columns="prior").add_suffix("_q1")
    q1 = q1.rename(columns={"scene_q1": "scene", "model_id_q1": "model_id", "model_q1": "model"})
    equal = summary[summary["prior"] == "equal"].drop(columns="prior").add_suffix("_equal")
    equal = equal.rename(
        columns={"scene_equal": "scene", "model_id_equal": "model_id", "model_equal": "model"}
    )
    joined = q1.merge(equal, on=["scene", "model_id", "model"], validate="one_to_one")
    joined["mean_rank_equal_minus_q1"] = joined["mean_rank_equal"] - joined["mean_rank_q1"]
    joined["top3_equal_minus_q1"] = joined["top3_proportion_equal"] - joined["top3_proportion_q1"]
    return joined.sort_values(["scene", "mean_rank_q1", "model_id"]).reset_index(drop=True)


def missingness_sensitivity(
    frames: dict[str, pd.DataFrame],
    spec: dict[str, Any],
    runtimes: dict[str, SceneRuntime],
    prior: dict[str, float],
) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    for delta in spec["ces_input_transform"]["sensitivity"]["delta_grid"]:
        ability = score_floor_transform(frames["capability"], frames["applicability"], float(delta))
        for runtime in runtimes.values():
            table, _ = reference_scene_result(ability, runtime, prior, "q1")
            block = table[
                [
                    "model_id",
                    "model",
                    "scene",
                    "ces_utility",
                    "ces_rank",
                    "linear_utility",
                    "linear_rank",
                    "pri",
                ]
            ].copy()
            block["sensitivity_type"] = "score_floor_delta"
            block["sensitivity_value"] = float(delta)
            records.append(block)
    for anchor in spec["c5_structural_absence"]["sensitivity_grid"]:
        ability = latent_transform(frames["theta"], frames["applicability"], float(anchor))
        runtime = runtimes["dialogue"]
        table, _ = reference_scene_result(ability, runtime, prior, "q1")
        block = table[
            [
                "model_id",
                "model",
                "scene",
                "ces_utility",
                "ces_rank",
                "linear_utility",
                "linear_rank",
                "pri",
            ]
        ].copy()
        block["sensitivity_type"] = "structural_c5_anchor"
        block["sensitivity_value"] = float(anchor)
        records.append(block)
    primary = latent_transform(
        frames["theta"], frames["applicability"], float(spec["c5_structural_absence"]["primary_anchor"])
    )
    base = runtimes["dialogue"]
    common_config = SceneConfig(
        key="dialogue_common_dimension",
        label="日常对话共同维度口径",
        core_dimensions=("C1", "C2"),
        alpha_range=base.config.alpha_range,
        alpha_development_default=base.alpha_reference,
        rho_range=base.config.rho_range,
        rho_development_default=base.rho_reference,
        lower_bounds=(("C3", 0.10),),
        order_constraints=(),
    )
    common_runtime = SceneRuntime(
        key="dialogue",
        label="日常对话共同维度口径",
        dimensions=("C1", "C2", "C3"),
        config=common_config,
        alpha_reference=base.alpha_reference,
        rho_reference=base.rho_reference,
        alpha_grid=base.alpha_grid,
        rho_grid=base.rho_grid,
    )
    common, _ = reference_scene_result(primary, common_runtime, prior, "q1")
    block = common[
        [
            "model_id",
            "model",
            "scene",
            "ces_utility",
            "ces_rank",
            "linear_utility",
            "linear_rank",
            "pri",
        ]
    ].copy()
    block["sensitivity_type"] = "common_dimension_without_C5"
    block["sensitivity_value"] = np.nan
    records.append(block)
    return pd.concat(records, ignore_index=True)


def uncertainty_propagation(
    frames: dict[str, pd.DataFrame],
    spec: dict[str, Any],
    runtimes: dict[str, SceneRuntime],
    prior: dict[str, float],
    reference_weights: dict[str, KLWeightResult],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    theta = frames["theta"].set_index("model_id")
    app = frames["applicability"].set_index("model_id")
    models = frames["theta"][["model_id", "model"]].copy().reset_index(drop=True)
    model_ids = list(models["model_id"])
    uncertainty = frames["uncertainty"]
    dim_unc = uncertainty[uncertainty["uncertainty_scope"] == "DIMENSION_LATENT_SCORE"]
    sd = dim_unc.pivot(index="model_id", columns="dimension", values="theta_bootstrap_sd")
    draws = int(spec["uncertainty_propagation"]["draws"])
    rng = np.random.default_rng(int(spec["uncertainty_propagation"]["random_seed"]))
    anchor = float(spec["c5_structural_absence"]["primary_anchor"])
    utility_store = {scene: np.empty((draws, len(models))) for scene in runtimes}
    rank_store = {scene: np.empty((draws, len(models)), dtype=int) for scene in runtimes}
    point = theta[[f"{d}_theta" for d in ABILITY_ORDER]].to_numpy(dtype=float)
    sd_matrix = np.empty_like(point)
    for i, model_id in enumerate(model_ids):
        for j, dimension in enumerate(ABILITY_ORDER):
            value = sd.loc[model_id, dimension] if model_id in sd.index and dimension in sd.columns else np.nan
            sd_matrix[i, j] = 0.0 if pd.isna(value) else float(value)
    absent = app.loc[model_ids, "C5_status"].eq("STRUCTURAL_CAPABILITY_ABSENCE").to_numpy()
    for draw in range(draws):
        sampled = point + rng.normal(0.0, sd_matrix)
        z = np.empty_like(sampled)
        for j, dimension in enumerate(ABILITY_ORDER):
            observed = ~np.isnan(sampled[:, j])
            maximum = float(np.max(sampled[observed, j]))
            z[observed, j] = np.exp(sampled[observed, j] - maximum)
            z[~observed, j] = np.nan
        z[absent, ABILITY_ORDER.index("C5")] = anchor
        if np.isnan(z).any():
            raise ValueError("Uncertainty propagation encountered unsupported ordinary missingness.")
        for scene, runtime in runtimes.items():
            indices = [ABILITY_ORDER.index(d) for d in runtime.dimensions]
            weights = np.asarray(
                [reference_weights[scene].weights[d] for d in runtime.dimensions], dtype=float
            )
            utility = np.asarray(ces_utility(z[:, indices], weights, runtime.rho_reference))
            ranks = pd.Series(utility).rank(method="min", ascending=False).astype(int).to_numpy()
            utility_store[scene][draw] = utility
            rank_store[scene][draw] = ranks
    records: list[dict[str, Any]] = []
    bootstrap_blocks: list[pd.DataFrame] = []
    for scene in runtimes:
        utility = utility_store[scene]
        ranks = rank_store[scene]
        for idx, model in models.iterrows():
            records.append(
                {
                    "model_id": model["model_id"],
                    "model": model["model"],
                    "scene": scene,
                    "draws": draws,
                    "utility_mean": float(np.mean(utility[:, idx])),
                    "utility_sd": float(np.std(utility[:, idx], ddof=1)),
                    "utility_ci_low": float(np.quantile(utility[:, idx], 0.025)),
                    "utility_ci_high": float(np.quantile(utility[:, idx], 0.975)),
                    "mean_rank": float(np.mean(ranks[:, idx])),
                    "rank_ci_low": float(np.quantile(ranks[:, idx], 0.025)),
                    "rank_ci_high": float(np.quantile(ranks[:, idx], 0.975)),
                    "probability_rank_1": float(np.mean(ranks[:, idx] == 1)),
                    "probability_top_3": float(np.mean(ranks[:, idx] <= 3)),
                    "top1_probability": float(np.mean(ranks[:, idx] == 1)),
                    "top3_probability": float(np.mean(ranks[:, idx] <= 3)),
                }
            )
        wide = pd.DataFrame(utility, columns=model_ids)
        wide.insert(0, "bootstrap_id", np.arange(1, draws + 1, dtype=int))
        long = wide.melt(
            id_vars="bootstrap_id",
            var_name="model_id",
            value_name="utility",
        )
        long["source_bootstrap_id"] = long["bootstrap_id"].map(
            lambda value: f"q1_uncertainty_normal_approx_{value:04d}"
        )
        long["scene_internal"] = scene
        bootstrap_blocks.append(long)
    return pd.DataFrame(records), pd.concat(bootstrap_blocks, ignore_index=True)


def model_identity_table(q1_models: pd.DataFrame) -> pd.DataFrame:
    """Return the frozen Q1 model identity without creating or rewriting model IDs."""

    actual = q1_models[["model_id", "model"]].drop_duplicates().set_index("model_id")["model"]
    if set(actual.index) != set(MODEL_IDENTITY):
        missing = sorted(set(MODEL_IDENTITY) - set(actual.index))
        extra = sorted(set(actual.index) - set(MODEL_IDENTITY))
        raise ValueError(f"Q1/Q2 model identity mismatch: missing={missing}, extra={extra}")
    records = []
    for model_id, (base_name, setting, expected_display) in MODEL_IDENTITY.items():
        observed_display = str(actual.loc[model_id])
        if observed_display != expected_display:
            raise ValueError(
                f"Frozen display name changed for {model_id}: "
                f"expected={expected_display!r}, observed={observed_display!r}"
            )
        records.append(
            {
                "model_id": model_id,
                "model_name": observed_display,
                "model_base_name": base_name,
                "model_setting": setting,
            }
        )
    return pd.DataFrame(records)


def build_q2_to_q3_interfaces(
    reference: pd.DataFrame,
    bootstrap_raw: pd.DataFrame,
    q1_models: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    identity = model_identity_table(q1_models)
    scenario_order = {code: index for index, code in enumerate(("Research", "General", "Coding"))}

    nominal = reference[["model_id", "scene", "ces_utility", "ces_rank"]].copy()
    nominal = nominal.merge(identity, on="model_id", validate="many_to_one")
    nominal["scenario"] = nominal["scene"].map(lambda value: SCENARIO_INTERFACE[value][0])
    nominal["scenario_code"] = nominal["scenario"]
    nominal["scenario_name"] = nominal["scene"].map(lambda value: SCENARIO_INTERFACE[value][1])
    nominal = nominal.rename(columns={"ces_utility": "utility", "ces_rank": "utility_rank"})
    nominal["utility_normalization"] = UTILITY_NORMALIZATION
    nominal["q2_method"] = Q2_METHOD
    nominal["source_version"] = Q2_SCENARIO_UTILITY_FREEZE_VERSION
    nominal["_scenario_order"] = nominal["scenario"].map(scenario_order)
    nominal = nominal.sort_values(["_scenario_order", "utility_rank", "model_id"]).drop(
        columns=["_scenario_order", "scene"]
    )
    nominal = nominal[
        [
            "model_id",
            "model_name",
            "model_base_name",
            "model_setting",
            "scenario",
            "scenario_code",
            "scenario_name",
            "utility",
            "utility_rank",
            "utility_normalization",
            "q2_method",
            "source_version",
        ]
    ].reset_index(drop=True)

    summary = nominal[
        [
            "scenario",
            "scenario_name",
            "utility_rank",
            "model_id",
            "model_name",
            "model_setting",
            "utility",
            "source_version",
        ]
    ].rename(columns={"utility_rank": "rank"})

    bootstrap = bootstrap_raw.merge(identity, on="model_id", validate="many_to_one")
    bootstrap["scenario"] = bootstrap["scene_internal"].map(
        lambda value: SCENARIO_INTERFACE[value][0]
    )
    bootstrap["scenario_code"] = bootstrap["scenario"]
    bootstrap["scenario_name"] = bootstrap["scene_internal"].map(
        lambda value: SCENARIO_INTERFACE[value][1]
    )
    bootstrap["source_version"] = Q2_SCENARIO_UTILITY_FREEZE_VERSION
    bootstrap["_scenario_order"] = bootstrap["scenario"].map(scenario_order)
    bootstrap = bootstrap.sort_values(
        ["bootstrap_id", "_scenario_order", "model_id"]
    ).drop(columns=["_scenario_order", "scene_internal"])
    bootstrap = bootstrap[
        [
            "bootstrap_id",
            "source_bootstrap_id",
            "model_id",
            "model_name",
            "model_base_name",
            "model_setting",
            "scenario",
            "scenario_code",
            "scenario_name",
            "utility",
            "source_version",
        ]
    ].reset_index(drop=True)
    return nominal, summary.reset_index(drop=True), bootstrap


def validate_q2_to_q3_interfaces(
    nominal: pd.DataFrame,
    summary: pd.DataFrame,
    bootstrap: pd.DataFrame,
    reference: pd.DataFrame,
    uncertainty_summary: pd.DataFrame,
    q1_models: pd.DataFrame,
    expected_draws: int,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []

    def add(check: str, passed: bool, expected: Any, actual: Any, details: str) -> None:
        checks.append(
            {
                "check": check,
                "status": "PASS" if passed else "FAIL",
                "expected": expected,
                "actual": actual,
                "details": details,
            }
        )

    expected_models = set(q1_models["model_id"])
    expected_scenarios = {"Research", "General", "Coding"}
    add("EXPECTED_ROWS", len(nominal) == 30, 30, len(nominal), "10 models x 3 scenes")
    add(
        "CORE_MODEL_IDS",
        set(nominal["model_id"]) == expected_models and len(expected_models) == 10,
        10,
        nominal["model_id"].nunique(),
        "model_id is inherited unchanged from the frozen Q1/Q2 interface",
    )
    scene_counts = nominal.groupby("scenario")["model_id"].nunique().to_dict()
    add(
        "MODELS_PER_SCENARIO",
        set(scene_counts) == expected_scenarios and all(value == 10 for value in scene_counts.values()),
        "Research=10; General=10; Coding=10",
        json.dumps(scene_counts, ensure_ascii=False, sort_keys=True),
        "each model has one nominal utility in each scene",
    )
    duplicate_rows = int(nominal.duplicated(["model_id", "scenario"]).sum())
    add("DUPLICATE_ROWS", duplicate_rows == 0, 0, duplicate_rows, "key=(model_id, scenario)")
    missing_utility = int(nominal["utility"].isna().sum())
    add("MISSING_UTILITY", missing_utility == 0, 0, missing_utility, "nominal utility must be complete")
    nonfinite = int((~np.isfinite(nominal["utility"].to_numpy(dtype=float))).sum())
    add("NONFINITE_UTILITY", nonfinite == 0, 0, nonfinite, "utility must be finite")
    valid_ranks = all(
        sorted(group["utility_rank"].astype(int).tolist()) == list(range(1, 11))
        for _, group in nominal.groupby("scenario")
    )
    add("CONTINUOUS_RANKS", valid_ranks, "1..10 in every scene", valid_ranks, "descending utility")
    q1_names = q1_models[["model_id", "model"]].drop_duplicates().rename(columns={"model": "q1_model_name"})
    names = nominal[["model_id", "model_name"]].drop_duplicates().merge(
        q1_names, on="model_id", validate="one_to_one"
    )
    name_mismatch = int((names["model_name"] != names["q1_model_name"]).sum())
    add("MODEL_NAME_MATCH_Q1", name_mismatch == 0, 0, name_mismatch, "exact Q1 display names")
    missing_setting = int(nominal["model_setting"].isna().sum() + nominal["model_setting"].eq("").sum())
    add("MODEL_SETTING_PRESENT", missing_setting == 0, 0, missing_setting, "pricing-SKU mapping field")
    illegal_scenarios = sorted(set(nominal["scenario"]) - expected_scenarios)
    add("SCENARIO_CODE_LEGAL", not illegal_scenarios, "Research|General|Coding", illegal_scenarios, "machine-readable codes")
    missing_source = int(nominal["source_version"].isna().sum() + nominal["source_version"].eq("").sum())
    add("SOURCE_VERSION_PRESENT", missing_source == 0, 0, missing_source, Q2_SCENARIO_UTILITY_FREEZE_VERSION)
    add("SUMMARY_ROWS", len(summary) == 30, 30, len(summary), "ranked nominal summary")

    reference_check = reference[["model_id", "scene", "ces_utility", "ces_rank"]].copy()
    reference_check["scenario"] = reference_check["scene"].map(
        lambda value: SCENARIO_INTERFACE[value][0]
    )
    comparison = nominal.merge(
        reference_check,
        on=["model_id", "scenario"],
        validate="one_to_one",
    )
    max_utility_difference = float((comparison["utility"] - comparison["ces_utility"]).abs().max())
    rank_mismatch = int((comparison["utility_rank"] != comparison["ces_rank"]).sum())
    add(
        "FORMAL_Q2_RESULT_MATCH",
        max_utility_difference <= 1e-15 and rank_mismatch == 0,
        "utility diff=0; rank mismatch=0",
        f"max_utility_diff={max_utility_difference:.3e}; rank_mismatch={rank_mismatch}",
        "same frozen reference object writes paper macros, formal Q2 scores, and Q3 interface",
    )

    expected_bootstrap_rows = expected_draws * 30
    add(
        "BOOTSTRAP_ROWS",
        len(bootstrap) == expected_bootstrap_rows,
        expected_bootstrap_rows,
        len(bootstrap),
        f"{expected_draws} aligned draws x 10 models x 3 scenes",
    )
    bootstrap_duplicates = int(
        bootstrap.duplicated(["bootstrap_id", "model_id", "scenario"]).sum()
    )
    add(
        "BOOTSTRAP_DUPLICATES",
        bootstrap_duplicates == 0,
        0,
        bootstrap_duplicates,
        "key=(bootstrap_id, model_id, scenario)",
    )
    bootstrap_missing = int(bootstrap["utility"].isna().sum())
    bootstrap_nonfinite = int(
        (~np.isfinite(bootstrap["utility"].to_numpy(dtype=float))).sum()
    )
    add("BOOTSTRAP_MISSING_UTILITY", bootstrap_missing == 0, 0, bootstrap_missing, "all propagated utilities present")
    add("BOOTSTRAP_NONFINITE_UTILITY", bootstrap_nonfinite == 0, 0, bootstrap_nonfinite, "all propagated utilities finite")
    bootstrap_stats = (
        bootstrap.groupby(["model_id", "scenario"], as_index=False)["utility"]
        .agg(
            utility_mean="mean",
            utility_ci_low=lambda values: values.quantile(0.025),
            utility_ci_high=lambda values: values.quantile(0.975),
        )
    )
    uncertainty_check = uncertainty_summary[
        ["model_id", "scene", "utility_mean", "utility_ci_low", "utility_ci_high"]
    ].copy()
    uncertainty_check["scenario"] = uncertainty_check["scene"].map(
        lambda value: SCENARIO_INTERFACE[value][0]
    )
    uncertainty_check = uncertainty_check.drop(columns="scene")
    bootstrap_comparison = bootstrap_stats.merge(
        uncertainty_check,
        on=["model_id", "scenario"],
        suffixes=("_interface", "_formal"),
        validate="one_to_one",
    )
    statistic_columns = ("utility_mean", "utility_ci_low", "utility_ci_high")
    max_bootstrap_stat_difference = max(
        float(
            (
                bootstrap_comparison[f"{column}_interface"]
                - bootstrap_comparison[f"{column}_formal"]
            ).abs().max()
        )
        for column in statistic_columns
    )
    add(
        "BOOTSTRAP_SUMMARY_MATCH",
        max_bootstrap_stat_difference <= 1e-15,
        "max difference <= 1e-15",
        f"{max_bootstrap_stat_difference:.3e}",
        "bootstrap utility rows reproduce the formal Q2 uncertainty summary",
    )
    validation = pd.DataFrame(checks)
    if not validation["status"].eq("PASS").all():
        failed = validation[validation["status"] == "FAIL"]
        raise AssertionError(f"Q2-to-Q3 validation failed:\n{failed.to_string(index=False)}")
    return validation


def write_q2_to_q3_documents(
    weights: pd.DataFrame,
    runtimes: dict[str, SceneRuntime],
    spec_hash: str,
    nominal: pd.DataFrame,
    bootstrap: pd.DataFrame,
    validation: pd.DataFrame,
) -> None:
    q1_weights = weights[(weights["prior"] == "q1") & weights["active_in_scene"]]
    weight_lines = []
    for scene in ("research", "dialogue", "coding"):
        row = q1_weights[q1_weights["scene"] == scene]
        formatted = ", ".join(
            f"{item.dimension}={item.weight:.4f}" for item in row.itertuples(index=False)
        )
        code, name = SCENARIO_INTERFACE[scene]
        runtime = runtimes[scene]
        weight_lines.append(
            f"- `{code}` ({name}): {formatted}; alpha={runtime.alpha_reference:.3f}; "
            f"rho={runtime.rho_reference:.2f}."
        )

    document = "\n".join(
        [
            "# Q2 to Q3 scenario utility interface",
            "",
            f"`Q2_SCENARIO_UTILITY_FREEZE_VERSION = {Q2_SCENARIO_UTILITY_FREEZE_VERSION}`",
            "",
            "This interface exports the exact nominal scene utilities used by the formal Q2 paper. "
            "It does not introduce price, Pareto, budget, ICER, or any alternative performance score.",
            "",
            "## 1. Interface files",
            "",
            "- `q2/outputs/scenario_utility.csv`: 30 frozen nominal utilities.",
            "- `q2/outputs/scenario_utility_summary.csv`: the same utilities sorted by scene rank.",
            f"- `q2/outputs/scenario_utility_bootstrap.csv`: {len(bootstrap)} rows from "
            f"{bootstrap['bootstrap_id'].nunique()} aligned Q1-uncertainty propagation draws.",
            "- `q2/outputs/q2_to_q3_validation.csv`: machine-readable interface quality checks.",
            "- `q2/metadata/q2_to_q3_interface.md`: this contract.",
            "",
            "## 2. Model identity",
            "",
            "`model_id` is inherited unchanged from the standardized Q1/Q2 interface at Q1 data "
            f"commit `{Q1_DATA_COMMIT}`. No Q2- or Q3-specific model IDs are created. `model_name` "
            "retains the exact Q1 display name; `model_base_name` and `model_setting` expose the "
            "base family and the exact evaluation setting for pricing-SKU mapping.",
            "",
            "## 3. Scenario definition",
            "",
            "- `Research`: 科研长文本分析; CES core C1 complex reasoning, C2 factual reliability, C3 long context.",
            "- `General`: 大众日常通用对话; CES core C1, C2, C3 and C5 multimodal availability.",
            "- `Coding`: 计算机代码开发; CES core C1 complex reasoning and C4 code/software engineering.",
            "",
            "Q3 must read `scenario_code` or the equivalent `scenario` column. Each model has exactly "
            "one nominal record in each scenario.",
            "",
            "## 4. Utility definition",
            "",
            "The formal Q2 input is the positive Bradley-Terry latent strength",
            "",
            "```text",
            "z_ij = exp(theta_ij - max_i(theta_ij)).",
            "```",
            "",
            "The nominal scenario utility is",
            "",
            "```text",
            "U_i^(s) = [sum_{j in J_s} w_j^(s) (z_ij + epsilon)^rho_s]^(1/rho_s),",
            "```",
            "",
            "with the continuous weighted geometric-mean limit when `rho_s = 0`. "
            f"The numerical shift is `epsilon = {EPS:g}`. Structural C5 absence uses the frozen "
            "availability anchor 0.35 and is never interpreted as an observed benchmark zero or "
            "a zero-filled latent score.",
            "",
            "## 5. Parameter source",
            "",
            *weight_lines,
            "",
            "The weights are the KL minimum-information projection from the Q1 objective-weight "
            "prior under frozen scene constraints. The formal model specification SHA-256 is "
            f"`{spec_hash}`.",
            "",
            "## 6. Scale and normalization",
            "",
            "- Utility is not a rank score, price-adjusted score, Q1 overall score, or benchmark score.",
            "- Dimension inputs are normalized across models within each ability dimension before CES aggregation.",
            f"- Utilities are positive and, under the implemented scale, lie in `(0, 1 + {EPS:g}]`; larger is better.",
            "- No post-hoc min-max normalization is applied to the nominal scene utility.",
            "- Because Research, General and Coding use different ability sets, KL weights and rho values, "
            "absolute utility levels are intended for comparison within a scenario only.",
            "- Q3 must run Pareto analysis separately by scenario. It must not infer that Research utility "
            "0.8 is economically or scientifically equivalent to Coding utility 0.8.",
            "",
            "## 7. Uncertainty",
            "",
            "`Q2_BOOTSTRAP_SCENARIO_UTILITY_AVAILABLE = TRUE`",
            "",
            f"The bootstrap interface contains {bootstrap['bootstrap_id'].nunique()} aligned draws. "
            "The standardized Q1 interface supplies point theta and dimension-level bootstrap SD, not "
            "the original joint replicate table. Q2 therefore samples `theta_draw = point_theta + "
            "Normal(0, theta_bootstrap_sd)` with seed 20260817, independently across model-dimension "
            "cells because covariance is unavailable. The same bootstrap_id identifies one joint Q2 draw "
            "across all models and all three scenarios. Structural C5 anchors remain fixed. These rows "
            "propagate Q1 ability-estimation uncertainty only; alpha/rho parameter uncertainty is stored "
            "separately in the Q2 robustness outputs and is not mixed into this Q3 Pareto-bootstrap interface.",
            "",
            "## 8. Q3 usage rule",
            "",
            "Q3 must use `utility` directly as its performance variable `U_i^(s)`. It must not reweight "
            "abilities, rebuild a performance score, substitute Q1 overall score, convert rank to a score, "
            "or divide utility by price before the Q3 cost model. Cost, Pareto frontiers, budgets, ICER and "
            "cost-performance fitting belong exclusively to Q3.",
            "",
            "Recommended nominal load:",
            "",
            "```python",
            "utility = pandas.read_csv('q2/outputs/scenario_utility.csv')",
            "for scenario_code, group in utility.groupby('scenario_code'):",
            "    # join group to Q3 pricing by model_id/model_setting, then run Q3 per scenario",
            "    ...",
            "```",
            "",
            "## 9. Validation and paper synchronization",
            "",
            f"All {len(validation)} interface checks pass. The nominal interface, `outputs/q2/final/"
            "q2_scene_scores.csv`, and the generated LaTeX paper values are written from the same frozen "
            "in-memory reference result. Consequently the Q2 paper ranking and the Q3 performance interface "
            "cannot select different nominal result versions within a formal run.",
            "",
        ]
    )
    (Q2_METADATA / "q2_to_q3_interface.md").write_text(document, encoding="utf-8")

    status = "\n".join(
        [
            "# Q2 final status and Q2-to-Q3 handoff",
            "",
            f"Q2_SCENARIO_UTILITY_FREEZE_VERSION = {Q2_SCENARIO_UTILITY_FREEZE_VERSION}",
            f"Q1_INPUT_VERSION = frozen/v1.0 + Q1 v1.2 official outputs @ {Q1_DATA_COMMIT}",
            "",
            "Q2_MODEL_READY = TRUE",
            "Q2_FINAL_Q1_INPUT_READY = TRUE",
            "Q2_SCENARIO_UTILITY_READY = TRUE",
            "Q2_SCENARIO_UTILITY_VALIDATED = TRUE",
            "Q2_BOOTSTRAP_UTILITY_READY = TRUE",
            "Q2_TO_Q3_INTERFACE_READY = TRUE",
            "Q2_PAPER_RESULTS_MATCH_INTERFACE = TRUE",
            "",
            f"Nominal rows: {len(nominal)}",
            f"Bootstrap rows: {len(bootstrap)}",
            f"Bootstrap draws: {bootstrap['bootstrap_id'].nunique()}",
            f"Validation checks passed: {int(validation['status'].eq('PASS').sum())}/{len(validation)}",
            "",
        ]
    )
    (Q2_METADATA / "q2_final_status.md").write_text(status, encoding="utf-8")


def rank_migration(reference: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    migration = rankings[["model_id", "model", "ranking_A_rank"]].rename(
        columns={"ranking_A_rank": "rank_q1_reference"}
    )
    for scene in ("research", "dialogue", "coding"):
        block = reference[reference["scene"] == scene][["model_id", "ces_rank"]].rename(
            columns={"ces_rank": f"rank_{scene}"}
        )
        migration = migration.merge(block, on="model_id", validate="one_to_one")
        migration[f"delta_rank_{scene}"] = migration[f"rank_{scene}"] - migration["rank_q1_reference"]
    return migration.sort_values("rank_q1_reference").reset_index(drop=True)


def competitors(scene_table: pd.DataFrame, target_id: str) -> dict[str, str | None]:
    ordered = scene_table.sort_values(["ces_rank", "model_id"]).reset_index(drop=True)
    matches = ordered.index[ordered["model_id"] == target_id].tolist()
    if not matches:
        raise KeyError(target_id)
    idx = matches[0]
    target_utility = float(ordered.loc[idx, "ces_utility"])
    others = ordered[ordered["model_id"] != target_id].copy()
    closest_idx = (others["ces_utility"] - target_utility).abs().idxmin()
    return {
        "previous_rank": None if idx == 0 else str(ordered.loc[idx - 1, "model"]),
        "next_rank": None if idx + 1 == len(ordered) else str(ordered.loc[idx + 1, "model"]),
        "scene_first": str(ordered.iloc[0]["model"]),
        "scene_first_competitor": str(others.sort_values(["ces_rank", "model_id"]).iloc[0]["model"]),
        "closest_utility": str(others.loc[closest_idx, "model"]),
    }


def kimi_analysis(
    reference: pd.DataFrame,
    migration: pd.DataFrame,
    robustness: pd.DataFrame,
    prior_table: pd.DataFrame,
    uncertainty: pd.DataFrame,
) -> pd.DataFrame:
    migration_row = migration[migration["model_id"] == KIMI_ID].iloc[0]
    records: list[dict[str, Any]] = []
    for scene in ("research", "dialogue", "coding"):
        scene_table = reference[reference["scene"] == scene]
        row = scene_table[scene_table["model_id"] == KIMI_ID].iloc[0]
        dims = [d for d in ABILITY_ORDER if f"marginal_utility_{d}" in row.index]
        priority = max(dims, key=lambda d: float(row[f"marginal_utility_{d}"]))
        comp = competitors(scene_table, KIMI_ID)
        robust = robustness[
            (robustness["scene"] == scene)
            & (robustness["prior"] == "q1")
            & (robustness["model_id"] == KIMI_ID)
        ].iloc[0]
        prior = prior_table[(prior_table["scene"] == scene) & (prior_table["model_id"] == KIMI_ID)].iloc[0]
        unc = uncertainty[(uncertainty["scene"] == scene) & (uncertainty["model_id"] == KIMI_ID)].iloc[0]
        records.append(
            {
                "model_id": KIMI_ID,
                "model": row["model"],
                "scene": scene,
                "scene_label": SCENE_CN[scene],
                "ces_utility": row["ces_utility"],
                "ces_rank": int(row["ces_rank"]),
                "q1_reference_rank": int(migration_row["rank_q1_reference"]),
                "delta_rank_vs_q1": int(migration_row[f"delta_rank_{scene}"]),
                "linear_rank": int(row["linear_rank"]),
                "pri": row["pri"],
                "priority_improvement_dimension": priority,
                "priority_improvement_label": ABILITY_CN[priority],
                "parameter_mean_rank": robust["mean_rank"],
                "parameter_best_rank": int(robust["best_rank"]),
                "parameter_worst_rank": int(robust["worst_rank"]),
                "parameter_top3_proportion": robust["top3_proportion"],
                "equal_prior_top3_proportion": prior["top3_proportion_equal"],
                "mean_rank_equal_minus_q1": prior["mean_rank_equal_minus_q1"],
                "q1_uncertainty_top3_probability": unc["probability_top_3"],
                "q1_uncertainty_rank1_probability": unc["probability_rank_1"],
                "q1_uncertainty_utility_ci_low": unc["utility_ci_low"],
                "q1_uncertainty_utility_ci_high": unc["utility_ci_high"],
                **comp,
            }
        )
    result = pd.DataFrame(records)
    result["strongest_scene"] = result.loc[result.sort_values(["ces_rank", "ces_utility"], ascending=[True, False]).index[0], "scene"]
    result["weakest_scene"] = result.loc[result.sort_values(["ces_rank", "ces_utility"], ascending=[False, True]).index[0], "scene"]
    return result


def configure_plotting() -> None:
    matplotlib.use("Agg")
    plt.rcParams.update(
        {
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 10,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_framework() -> None:
    fig, ax = plt.subplots(figsize=(12.5, 2.8))
    ax.set_axis_off()
    labels = ["Q1基础能力", "场景需求约束", "KL最小信息偏移", "CES互补效用", "三场景排序", "机理解释与稳健性"]
    colors = ["#dbeafe", "#e0f2fe", "#dcfce7", "#fef3c7", "#fee2e2", "#ede9fe"]
    x_positions = np.linspace(0.02, 0.84, len(labels))
    for idx, (x, label, color) in enumerate(zip(x_positions, labels, colors)):
        box = patches.FancyBboxPatch(
            (x, 0.35), 0.14, 0.30, boxstyle="round,pad=0.02", linewidth=1.2, edgecolor="#334155", facecolor=color
        )
        ax.add_patch(box)
        ax.text(x + 0.07, 0.50, label, ha="center", va="center", fontsize=10.5, fontweight="bold")
        if idx < len(labels) - 1:
            ax.annotate("", xy=(x_positions[idx + 1] - 0.01, 0.50), xytext=(x + 0.15, 0.50), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.5, 0.16, "场景改变能力重要性（KL权重），也改变能力可替代性（CES参数）", ha="center", color="#334155")
    save_figure(fig, "q2_fig1_framework")


def plot_weights(weight_table: pd.DataFrame) -> None:
    main = weight_table[weight_table["prior"] == "q1"].copy()
    pivot = main.pivot(index="dimension", columns="scene", values="weight").reindex(ABILITY_ORDER).fillna(0.0)
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    x = np.arange(len(ABILITY_ORDER))
    width = 0.24
    colors = ["#2563eb", "#16a34a", "#dc2626"]
    for idx, scene in enumerate(("research", "dialogue", "coding")):
        ax.bar(x + (idx - 1) * width, pivot[scene], width, label=SCENE_CN[scene], color=colors[idx])
    ax.set_xticks(x, [f"{d}\n{ABILITY_CN[d]}" for d in ABILITY_ORDER])
    ax.set_ylabel("KL场景权重")
    ax.set_ylim(0, max(0.8, float(pivot.max().max()) + 0.08))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, frameon=False, loc="upper center")
    fig.tight_layout()
    save_figure(fig, "q2_fig2_scene_weights")


def plot_utility_heatmap(reference: pd.DataFrame) -> None:
    pivot = reference.pivot(index="model", columns="scene", values="ces_utility")[["research", "dialogue", "coding"]]
    pivot = pivot.sort_values("research", ascending=False)
    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    image = ax.imshow(pivot.to_numpy(), cmap="YlGnBu", aspect="auto", vmin=float(pivot.min().min()), vmax=float(pivot.max().max()))
    ax.set_xticks(range(3), [SCENE_CN[s] for s in pivot.columns])
    ax.set_yticks(range(len(pivot)), pivot.index)
    for i in range(len(pivot)):
        for j in range(3):
            value = pivot.iloc[i, j]
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", color="white" if value > pivot.to_numpy().mean() else "#111827", fontsize=8.5)
    fig.colorbar(image, ax=ax, label="CES效用")
    fig.tight_layout()
    save_figure(fig, "q2_fig3_utility_heatmap")


def plot_bump(migration: pd.DataFrame) -> None:
    rank_cols = ["rank_q1_reference", "rank_research", "rank_dialogue", "rank_coding"]
    labels = ["Q1参考", "科研", "日常", "代码"]
    fig, ax = plt.subplots(figsize=(10.5, 6.6))
    x = np.arange(len(rank_cols))
    for _, row in migration.iterrows():
        kimi = row["model_id"] == KIMI_ID
        color = "#dc2626" if kimi else "#94a3b8"
        lw = 3.2 if kimi else 1.2
        alpha = 1.0 if kimi else 0.72
        y = row[rank_cols].to_numpy(dtype=float)
        ax.plot(x, y, marker="o", color=color, linewidth=lw, alpha=alpha, zorder=3 if kimi else 1)
        # Keep the right-hand labels legible after the vector figure is scaled to
        # the paper text width.  Configuration suffixes are already reported in
        # the result table, so the bump chart uses concise model-family labels.
        display_name = str(row["model"]).split(" (")[0]
        ax.text(x[-1] + 0.08, y[-1], display_name, va="center", fontsize=8.2, color="#b91c1c" if kimi else "#475569")
    ax.set_xticks(x, labels)
    ax.set_yticks(range(1, 11))
    ax.set_ylabel("名次（1为最优）")
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0.22)
    ax.set_xlim(-0.1, 4.15)
    fig.tight_layout()
    save_figure(fig, "q2_fig4_rank_migration")


def plot_kimi_surface(grid: pd.DataFrame, runtimes: dict[str, SceneRuntime]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.6), constrained_layout=True)
    for ax, scene in zip(axes, ("research", "dialogue", "coding")):
        subset = grid[(grid["scene"] == scene) & (grid["prior"] == "q1") & (grid["model_id"] == KIMI_ID)]
        surface = subset.pivot(index="rho", columns="alpha", values="rank").sort_index(ascending=False)
        image = ax.imshow(surface.to_numpy(), cmap="RdYlGn_r", aspect="auto", vmin=1, vmax=10)
        ax.set_xticks(range(surface.shape[1]), [f"{v:.3f}" for v in surface.columns], rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(surface.shape[0]), [f"{v:.2f}" for v in surface.index], fontsize=8)
        ax.set_xlabel(r"$\alpha$")
        ax.set_ylabel(r"$\rho$")
        ax.set_title(SCENE_CN[scene])
        for i in range(surface.shape[0]):
            for j in range(surface.shape[1]):
                rank = int(surface.iloc[i, j])
                ax.text(j, i, str(rank), ha="center", va="center", fontsize=7.2, fontweight="bold" if rank <= 3 else "normal")
    fig.colorbar(image, ax=axes, shrink=0.85, label="Kimi名次")
    save_figure(fig, "q2_fig5_kimi_alpha_rho")


def plot_kimi_mechanism(reference: pd.DataFrame, primary: pd.DataFrame) -> None:
    kimi_ability = primary[primary["model_id"] == KIMI_ID].iloc[0]
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8), constrained_layout=True)
    for ax, scene in zip(axes, ("research", "dialogue", "coding")):
        row = reference[(reference["scene"] == scene) & (reference["model_id"] == KIMI_ID)].iloc[0]
        dims = [d for d in ABILITY_ORDER if f"marginal_utility_{d}" in row.index]
        ability = np.asarray([kimi_ability[d] for d in dims], dtype=float)
        marginal = np.asarray([row[f"marginal_utility_{d}"] for d in dims], dtype=float)
        marginal_scaled = marginal / marginal.max()
        x = np.arange(len(dims))
        ax.bar(x - 0.18, ability, 0.36, label="能力强度", color="#2563eb")
        ax.bar(x + 0.18, marginal_scaled, 0.36, label="边际效用（归一化）", color="#f97316")
        ax.set_xticks(x, [f"{d}\n{ABILITY_CN[d]}" for d in dims], fontsize=8)
        ax.set_ylim(0, 1.12)
        ax.set_title(SCENE_CN[scene])
        ax.grid(axis="y", alpha=0.22)
    axes[0].legend(frameon=False, loc="upper left")
    save_figure(fig, "q2_fig6_kimi_mechanism")


def write_weight_table(
    runtimes: dict[str, SceneRuntime],
    prior: dict[str, float],
) -> tuple[pd.DataFrame, dict[str, KLWeightResult]]:
    rows: list[dict[str, Any]] = []
    primary_results: dict[str, KLWeightResult] = {}
    for scene, runtime in runtimes.items():
        for prior_kind in ("q1", "equal"):
            result = solve_scene_weights(
                restricted_prior(prior, runtime.dimensions) if prior_kind == "q1" else equal_prior(runtime.dimensions),
                runtime.config,
                runtime.dimensions,
                runtime.alpha_reference,
            )
            if prior_kind == "q1":
                primary_results[scene] = result
            for dimension in ABILITY_ORDER:
                rows.append(
                    {
                        "scene": scene,
                        "scene_label": runtime.label,
                        "prior": prior_kind,
                        "alpha": runtime.alpha_reference,
                        "dimension": dimension,
                        "dimension_label": ABILITY_CN[dimension],
                        "active_in_scene": dimension in runtime.dimensions,
                        "weight": result.weights.get(dimension, 0.0),
                        "kl_divergence": result.kl_divergence,
                    }
                )
    return pd.DataFrame(rows), primary_results


def write_generated_tex(
    reference: pd.DataFrame,
    weights: pd.DataFrame,
    migration: pd.DataFrame,
    kimi: pd.DataFrame,
    robustness: pd.DataFrame,
    prior_table: pd.DataFrame,
    uncertainty: pd.DataFrame,
    spec_hash: str,
) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    main_weights = weights[(weights["prior"] == "q1") & (weights["active_in_scene"])].copy()
    scene_rows = []
    for scene in ("research", "dialogue", "coding"):
        runtime_row = reference[reference["scene"] == scene].iloc[0]
        alpha = runtime_row["alpha"]
        rho = runtime_row["rho"]
        dims = ",".join(d for d in ABILITY_ORDER if (main_weights["scene"].eq(scene) & main_weights["dimension"].eq(d)).any())
        constraint = {"research": r"$w_{C1}+w_{C3}\geq\alpha_R,\ w_{C2}\geq0.20$", "dialogue": r"$w_{C1}+w_{C2}\geq\alpha_D,\ w_{C3},w_{C5}\geq0.10$", "coding": r"$w_{C4}\geq\alpha_C$"}[scene]
        scene_rows.append(f"{SCENE_CN[scene]} & {dims} & {constraint} & {alpha:.3f} & {rho:.2f} \\\\")
    weight_rows = []
    for scene in ("research", "dialogue", "coding"):
        row = [SCENE_CN[scene]]
        for dim in ABILITY_ORDER:
            match = main_weights[(main_weights["scene"] == scene) & (main_weights["dimension"] == dim)]
            row.append("--" if match.empty else f"{float(match.iloc[0]['weight']):.4f}")
        weight_rows.append(" & ".join(row) + r" \\")
    score_rows = []
    ordered_models = migration.sort_values("rank_q1_reference")[["model_id", "model"]]
    for model in ordered_models.itertuples(index=False):
        row = [model.model]
        for scene in ("research", "dialogue", "coding"):
            record = reference[(reference["scene"] == scene) & (reference["model_id"] == model.model_id)].iloc[0]
            row.append(f"{record['ces_utility']:.3f} ({int(record['ces_rank'])})")
        score_rows.append(" & ".join(row) + r" \\")
    kimi_rows = []
    for row in kimi.itertuples(index=False):
        kimi_rows.append(
            f"{row.scene_label} & {row.ces_utility:.3f} & {row.ces_rank} & {row.delta_rank_vs_q1:+d} & {row.pri:.3f} & {row.priority_improvement_label} \\\\"
        )
    robust_rows = []
    for scene in ("research", "dialogue", "coding"):
        r = robustness[(robustness["scene"] == scene) & (robustness["prior"] == "q1") & (robustness["model_id"] == KIMI_ID)].iloc[0]
        p = prior_table[(prior_table["scene"] == scene) & (prior_table["model_id"] == KIMI_ID)].iloc[0]
        u = uncertainty[(uncertainty["scene"] == scene) & (uncertainty["model_id"] == KIMI_ID)].iloc[0]
        robust_rows.append(
            f"{SCENE_CN[scene]} & {r.mean_rank:.2f} & {int(r.best_rank)}--{int(r.worst_rank)} & {r.top3_proportion:.3f} & {p.top3_proportion_equal:.3f} & {u.probability_top_3:.3f} \\\\"
        )
    strongest = SCENE_CN[str(kimi.iloc[0]["strongest_scene"])]
    weakest = SCENE_CN[str(kimi.iloc[0]["weakest_scene"])]
    content = "\n".join(
        [
            f"\\newcommand{{\\QTwoSpecHash}}{{\\texttt{{{spec_hash}}}}}",
            f"\\newcommand{{\\KimiStrongestScene}}{{{strongest}}}",
            f"\\newcommand{{\\KimiWeakestScene}}{{{weakest}}}",
            "\\newcommand{\\QTwoSceneDefinitionRows}{%",
            *scene_rows,
            "}",
            "\\newcommand{\\QTwoWeightRows}{%",
            *weight_rows,
            "}",
            "\\newcommand{\\QTwoScoreRows}{%",
            *score_rows,
            "}",
            "\\newcommand{\\QTwoKimiRows}{%",
            *kimi_rows,
            "}",
            "\\newcommand{\\QTwoRobustRows}{%",
            *robust_rows,
            "}",
            "",
        ]
    )
    (GENERATED_DIR / "q2_generated_values.tex").write_text(content, encoding="utf-8")


def main() -> None:
    spec, spec_hash = load_spec()
    frames = load_inputs()
    runtimes = build_scene_runtime(spec)
    prior = objective_prior(frames["weights"])
    primary_anchor = float(spec["c5_structural_absence"]["primary_anchor"])
    primary = latent_transform(frames["theta"], frames["applicability"], primary_anchor)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    Q3_INTERFACE_OUTPUT.mkdir(parents=True, exist_ok=True)
    Q2_METADATA.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    audit = transformation_audit(frames, spec, primary)
    weights, primary_weight_results = write_weight_table(runtimes, prior)
    reference_tables = []
    equal_reference_tables = []
    for runtime in runtimes.values():
        table, _ = reference_scene_result(primary, runtime, prior, "q1")
        reference_tables.append(table)
        equal_table, _ = reference_scene_result(primary, runtime, prior, "equal")
        equal_reference_tables.append(equal_table)
    reference = pd.concat(reference_tables, ignore_index=True)
    equal_reference_result = pd.concat(equal_reference_tables, ignore_index=True)

    grids = []
    for runtime in runtimes.values():
        grids.append(run_parameter_grid(primary, runtime, prior, "q1"))
        grids.append(run_parameter_grid(primary, runtime, prior, "equal"))
    grid = pd.concat(grids, ignore_index=True)
    robustness = robustness_summary(grid)
    jumps = rank_jump_thresholds(grid)
    prior_table = prior_sensitivity(robustness)
    missing = missingness_sensitivity(frames, spec, runtimes, prior)
    uncertainty, uncertainty_bootstrap_raw = uncertainty_propagation(
        frames, spec, runtimes, prior, primary_weight_results
    )
    migration = rank_migration(reference, frames["rankings"])
    kimi = kimi_analysis(reference, migration, robustness, prior_table, uncertainty)

    marginal_records = []
    for row in reference.itertuples(index=False):
        runtime = runtimes[row.scene]
        for dimension in runtime.dimensions:
            marginal_records.append(
                {
                    "model_id": row.model_id,
                    "model": row.model,
                    "scene": row.scene,
                    "dimension": dimension,
                    "inner_share": getattr(row, f"inner_share_{dimension}"),
                    "marginal_utility": getattr(row, f"marginal_utility_{dimension}"),
                    "utility_elasticity": getattr(row, f"elasticity_{dimension}"),
                }
            )
    marginal = pd.DataFrame(marginal_records)

    audit.to_csv(OUTPUT / "ces_input_transformation_audit.csv", index=False, encoding="utf-8-sig")
    (OUTPUT / "ces_input_transformation_audit.md").write_text(
        "# CES input transformation audit\n\n"
        "The primary input is dimension-wise maximum-normalized BT latent strength: "
        "`z_ij = exp(theta_ij - max_i theta_ij)`. It is strictly positive, monotone in "
        "the Q1 latent ability, bounded by one, and does not reinterpret a sample-minimum "
        "0-100 score as zero capability. The comparison input is the positive-floor score "
        "mapping `delta + (1-delta)S/100` over the frozen delta grid. Structural C5 absence "
        "uses an explicit availability anchor in the primary transform and `C5_effective_score` "
        "only in the score-floor comparison; it is never described as an observed benchmark zero "
        "and no missing C5 latent score is filled with zero. Ranking/PRI sensitivity is reported "
        "in `q2_missingness_sensitivity.csv`.\n",
        encoding="utf-8",
    )
    weights.to_csv(OUTPUT / "q2_scene_weights.csv", index=False, encoding="utf-8-sig")
    reference.to_csv(OUTPUT / "q2_scene_scores.csv", index=False, encoding="utf-8-sig")
    reference[["model_id", "model", "scene", "ces_utility", "ces_rank"]].to_csv(
        OUTPUT / "q2_scene_rankings.csv", index=False, encoding="utf-8-sig"
    )
    reference[["model_id", "model", "scene", "ces_utility", "ces_rank", "linear_utility", "linear_rank", "rank_ces_minus_linear"]].to_csv(
        OUTPUT / "q2_linear_vs_ces.csv", index=False, encoding="utf-8-sig"
    )
    reference[["model_id", "model", "scene", "linear_utility", "ces_utility", "imbalance_penalty", "pri"]].to_csv(
        OUTPUT / "q2_pri.csv", index=False, encoding="utf-8-sig"
    )
    marginal.to_csv(OUTPUT / "q2_marginal_effects.csv", index=False, encoding="utf-8-sig")
    migration.to_csv(OUTPUT / "q2_rank_migration.csv", index=False, encoding="utf-8-sig")
    grid.to_csv(OUTPUT / "q2_parameter_grid.csv", index=False, encoding="utf-8-sig")
    robustness.to_csv(OUTPUT / "q2_parameter_robustness.csv", index=False, encoding="utf-8-sig")
    jumps.to_csv(OUTPUT / "q2_rank_jump_thresholds.csv", index=False, encoding="utf-8-sig")
    jumps.to_csv(
        OUTPUT / "q2_rank_transition_thresholds.csv", index=False, encoding="utf-8-sig"
    )
    prior_table.to_csv(OUTPUT / "q2_prior_sensitivity.csv", index=False, encoding="utf-8-sig")
    equal_reference_result.to_csv(OUTPUT / "q2_equal_prior_reference_scores.csv", index=False, encoding="utf-8-sig")
    uncertainty.to_csv(OUTPUT / "q2_q1_uncertainty_propagation.csv", index=False, encoding="utf-8-sig")
    missing.to_csv(OUTPUT / "q2_missingness_sensitivity.csv", index=False, encoding="utf-8-sig")
    kimi.to_csv(OUTPUT / "q2_kimi_analysis.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(SPEC_PATH, OUTPUT / "q2_model_spec_snapshot.yaml")

    scenario_utility, scenario_summary, scenario_bootstrap = build_q2_to_q3_interfaces(
        reference, uncertainty_bootstrap_raw, frames["theta"]
    )
    q2_to_q3_validation = validate_q2_to_q3_interfaces(
        scenario_utility,
        scenario_summary,
        scenario_bootstrap,
        reference,
        uncertainty,
        frames["theta"],
        int(spec["uncertainty_propagation"]["draws"]),
    )
    scenario_utility.to_csv(
        Q3_INTERFACE_OUTPUT / "scenario_utility.csv", index=False, encoding="utf-8-sig"
    )
    scenario_summary.to_csv(
        Q3_INTERFACE_OUTPUT / "scenario_utility_summary.csv", index=False, encoding="utf-8-sig"
    )
    scenario_bootstrap.to_csv(
        Q3_INTERFACE_OUTPUT / "scenario_utility_bootstrap.csv", index=False, encoding="utf-8-sig"
    )
    q2_to_q3_validation.to_csv(
        Q3_INTERFACE_OUTPUT / "q2_to_q3_validation.csv", index=False, encoding="utf-8-sig"
    )
    write_q2_to_q3_documents(
        weights,
        runtimes,
        spec_hash,
        scenario_utility,
        scenario_bootstrap,
        q2_to_q3_validation,
    )

    configure_plotting()
    plot_framework()
    plot_weights(weights)
    plot_utility_heatmap(reference)
    plot_bump(migration)
    plot_kimi_surface(grid, runtimes)
    plot_kimi_mechanism(reference, primary)
    write_generated_tex(reference, weights, migration, kimi, robustness, prior_table, uncertainty, spec_hash)

    input_files = [
        "q2/data/q1_capability_scores.csv",
        "q2/data/q1_bt_latent_scores.csv",
        "q2/data/q1_model_applicability.csv",
        "q2/data/q1_dimension_weights_reference.csv",
        "q2/data/q1_uncertainty.csv",
        "q2/data/q1_model_rankings.csv",
        "q2/data/q2_model_master_table.csv",
        "q2/metadata/q1_to_q2_mapping.md",
        "q2/metadata/q2_data_dictionary.md",
        "q2/metadata/q2_data_provenance.md",
    ]
    metadata = {
        "git_commit": git_text("rev-parse", "HEAD"),
        "git_branch": git_text("branch", "--show-current"),
        "working_tree_dirty": bool(git_text("status", "--porcelain")),
        "q1_data_commit": Q1_DATA_COMMIT,
        "q1_official_results_commit": Q1_RESULTS_COMMIT,
        "q1_freeze_version": "frozen/v1.0 + Q1 v1.2 official outputs",
        "remote_branches_checked": ["origin/main", "origin/q2-data-prep"],
        "remote_latest_data_branch": "origin/q2-data-prep",
        "remote_acquisition": "GitHub commit-pinned codeload snapshot because Git smart-HTTP was unavailable; imported q2 files were SHA-256 matched to the snapshot",
        "q1_input_files": [
            {"path": path, "sha256": sha256(ROOT / path)} for path in input_files
        ],
        "q2_model_spec_sha256": spec_hash,
        "q2_runner_sha256": sha256(Path(__file__)),
        "random_seed": int(spec["uncertainty_propagation"]["random_seed"]),
        "uncertainty_draws": int(spec["uncertainty_propagation"]["draws"]),
        "alpha_grid": {key: runtime.alpha_grid.tolist() for key, runtime in runtimes.items()},
        "rho_grid": {key: runtime.rho_grid.tolist() for key, runtime in runtimes.items()},
        "CES_input_transform": spec["ces_input_transform"]["primary"],
        "missing_policy": spec["c5_structural_absence"],
        "q2_to_q3_interface": {
            "freeze_version": Q2_SCENARIO_UTILITY_FREEZE_VERSION,
            "nominal_rows": len(scenario_utility),
            "bootstrap_rows": len(scenario_bootstrap),
            "bootstrap_draws": int(scenario_bootstrap["bootstrap_id"].nunique()),
            "scenario_codes": ["Research", "General", "Coding"],
            "interface_files": [
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": sha256(path),
                }
                for path in (
                    Q3_INTERFACE_OUTPUT / "scenario_utility.csv",
                    Q3_INTERFACE_OUTPUT / "scenario_utility_summary.csv",
                    Q3_INTERFACE_OUTPUT / "scenario_utility_bootstrap.csv",
                    Q3_INTERFACE_OUTPUT / "q2_to_q3_validation.csv",
                    Q2_METADATA / "q2_to_q3_interface.md",
                    Q2_METADATA / "q2_final_status.md",
                )
            ],
            "Q2_MODEL_READY": True,
            "Q2_FINAL_Q1_INPUT_READY": True,
            "Q2_SCENARIO_UTILITY_READY": True,
            "Q2_SCENARIO_UTILITY_VALIDATED": True,
            "Q2_BOOTSTRAP_UTILITY_READY": True,
            "Q2_TO_Q3_INTERFACE_READY": True,
            "Q2_PAPER_RESULTS_MATCH_INTERFACE": True,
        },
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "validation": "q2/scripts/validate_q2_inputs.py passed in the immutable 754bc1b snapshot",
    }
    (OUTPUT / "q2_run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Q2 formal run complete")
    print(f"model_spec_sha256={spec_hash}")
    print(
        f"Q2-to-Q3 interface: nominal_rows={len(scenario_utility)}, "
        f"bootstrap_rows={len(scenario_bootstrap)}, validation=PASS"
    )
    for scene in ("research", "dialogue", "coding"):
        top3 = reference[reference["scene"] == scene].nsmallest(3, "ces_rank")
        print(scene, list(zip(top3["model"], top3["ces_rank"], top3["ces_utility"].round(6))))
    print(kimi[["scene", "ces_rank", "ces_utility", "parameter_top3_proportion", "q1_uncertainty_top3_probability"]].to_string(index=False))


if __name__ == "__main__":
    main()
