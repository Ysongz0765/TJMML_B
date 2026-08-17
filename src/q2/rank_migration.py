"""Rank calculation and cross-scene migration tables."""

from __future__ import annotations

import pandas as pd


def rank_utilities(frame: pd.DataFrame, utility_column: str = "utility") -> pd.DataFrame:
    result = frame.copy()
    result["rank"] = result[utility_column].rank(method="min", ascending=False).astype(int)
    return result.sort_values(["rank", "model"]).reset_index(drop=True)


def build_rank_migration(
    scene_results: dict[str, pd.DataFrame],
    q1_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build wide ranks and Delta R=R_scene-R_Q1 when a Q1 rank exists."""

    tables: list[pd.DataFrame] = []
    if q1_frame is not None and "q1_overall_rank" in q1_frame.columns:
        baseline = q1_frame[["model", "q1_overall_rank"]].dropna().copy()
        baseline = baseline.rename(columns={"q1_overall_rank": "rank_q1"})
        tables.append(baseline)
    for scene, result in scene_results.items():
        if "rank" not in result.columns:
            result = rank_utilities(result)
        tables.append(result[["model", "rank"]].rename(columns={"rank": f"rank_{scene}"}))
    if not tables:
        raise ValueError("At least one rank table is required.")
    migration = tables[0]
    for table in tables[1:]:
        migration = migration.merge(table, on="model", how="outer", validate="one_to_one")
    if "rank_q1" in migration.columns:
        for scene in scene_results:
            column = f"rank_{scene}"
            migration[f"delta_rank_{scene}"] = migration[column] - migration["rank_q1"]
    return migration.sort_values("model").reset_index(drop=True)


def identify_competitors(scene_result: pd.DataFrame, target_model: str) -> dict[str, str | None]:
    """Identify adjacent, first-place, and nearest-utility competitors automatically."""

    ranked = rank_utilities(scene_result) if "rank" not in scene_result.columns else scene_result.copy()
    ranked = ranked.sort_values(["rank", "model"]).reset_index(drop=True)
    matches = ranked.index[ranked["model"] == target_model].tolist()
    if not matches:
        raise KeyError(f"Target model {target_model!r} is absent from the scene result.")
    idx = matches[0]
    target_utility = float(ranked.loc[idx, "utility"])
    others = ranked[ranked["model"] != target_model].copy()
    if others.empty:
        closest = None
    else:
        closest = str(
            others.loc[(others["utility"] - target_utility).abs().idxmin(), "model"]
        )
    return {
        "previous_rank": str(ranked.loc[idx - 1, "model"]) if idx > 0 else None,
        "next_rank": str(ranked.loc[idx + 1, "model"]) if idx + 1 < len(ranked) else None,
        "scene_first": str(ranked.iloc[0]["model"]),
        "closest_utility": closest,
    }
