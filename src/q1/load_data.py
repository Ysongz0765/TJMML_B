from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import CORE_MODELS, FROZEN_DIR


@dataclass(frozen=True)
class Q1Data:
    models: pd.DataFrame
    manifest: pd.DataFrame
    family_manifest: pd.DataFrame
    matrix: pd.DataFrame
    raw: pd.DataFrame
    selected: pd.DataFrame
    long: pd.DataFrame
    dimensions: list[str]
    families: list[str]
    settings: list[str]
    model_names: dict[str, str]


def _bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper().isin({"TRUE", "1", "YES"})


def load_q1_data() -> Q1Data:
    models = pd.read_excel(FROZEN_DIR / "model_pool_v1.0.xlsx", sheet_name="Models")
    manifest = pd.read_excel(FROZEN_DIR / "final_modeling_benchmark_manifest_v1.0.xlsx", sheet_name="Manifest")
    family_manifest = pd.read_excel(FROZEN_DIR / "benchmark_family_manifest_v1.0.xlsx", sheet_name="Families")
    matrix = pd.read_excel(FROZEN_DIR / "final_modeling_matrix_v1.0.xlsx", sheet_name="Matrix")
    raw = pd.read_excel(FROZEN_DIR / "raw_benchmark_data_v1.0.xlsx", sheet_name="RawData")

    selected = raw[_bool_series(raw["selected_for_final_modeling"])].copy()
    selected["score"] = pd.to_numeric(selected["raw_score"], errors="coerce")
    selected["applicable"] = selected["score"].notna()
    selected["human_verified_bool"] = _bool_series(selected["human_verified"])
    selected["higher_is_better_bool"] = _bool_series(selected["higher_is_better"])

    manifest = manifest.rename(columns={"capability": "dimension", "selected_setting": "setting_id"}).copy()
    selected = selected.merge(
        manifest[
            [
                "dimension",
                "benchmark_family",
                "setting_id",
                "family_weight_within_capability",
                "setting_weight_within_family",
                "network_contribution",
                "redundancy_status",
            ]
        ],
        left_on=["capability_dimension", "benchmark_family", "setting_id"],
        right_on=["dimension", "benchmark_family", "setting_id"],
        how="left",
        suffixes=("", "_manifest"),
    )
    selected["dimension"] = selected["dimension"].fillna(selected["capability_dimension"])

    long = selected[
        [
            "model_id",
            "model_full_name",
            "dimension",
            "benchmark_family",
            "setting_id",
            "score",
            "applicable",
            "source_id",
            "human_verified_bool",
            "higher_is_better_bool",
            "family_weight_within_capability",
            "setting_weight_within_family",
        ]
    ].copy()
    long = long.rename(columns={"human_verified_bool": "human_verified", "higher_is_better_bool": "higher_is_better"})

    model_order = {model_id: i for i, model_id in enumerate(CORE_MODELS)}
    models = models[models["model_id"].isin(CORE_MODELS)].copy()
    models["_order"] = models["model_id"].map(model_order)
    models = models.sort_values("_order").drop(columns="_order")

    settings = manifest["setting_id"].drop_duplicates().tolist()
    dimensions = manifest["dimension"].drop_duplicates().tolist()
    families = manifest["benchmark_family"].drop_duplicates().tolist()
    model_names = dict(zip(models["model_id"], models["model_full_name"]))

    return Q1Data(
        models=models,
        manifest=manifest,
        family_manifest=family_manifest,
        matrix=matrix,
        raw=raw,
        selected=selected,
        long=long,
        dimensions=dimensions,
        families=families,
        settings=settings,
        model_names=model_names,
    )

