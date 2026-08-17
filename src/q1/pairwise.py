from __future__ import annotations

from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd


def _margin_scale(scores: pd.Series, method: str) -> float:
    if method == "robust_iqr":
        q75, q25 = np.nanpercentile(scores, [75, 25])
        scale = q75 - q25
    else:
        scale = float(np.nanmax(scores) - np.nanmin(scores))
    return scale if np.isfinite(scale) and scale > 0 else 1.0


def build_pairwise(
    long: pd.DataFrame,
    dimension: str | None = None,
    margin_method: str = "range",
    epsilon_m: float = 0.1,
    exclude_families: set[str] | None = None,
) -> pd.DataFrame:
    data = long.copy()
    if dimension is not None:
        data = data[data["dimension"].eq(dimension)].copy()
    if exclude_families:
        data = data[~data["benchmark_family"].isin(exclude_families)].copy()
    rows = []
    family_counts = data.groupby("dimension")["benchmark_family"].nunique().to_dict()
    setting_counts = data.groupby(["dimension", "benchmark_family"])["setting_id"].nunique().to_dict()
    for (dim, family, setting_id), group in data.groupby(["dimension", "benchmark_family", "setting_id"], sort=False):
        values = group.dropna(subset=["score"]).copy()
        if len(values) < 2:
            continue
        ascending = not bool(values["higher_is_better"].iloc[0])
        scale = _margin_scale(values["score"], margin_method)
        raw_rows = []
        for a, b in combinations(values.itertuples(index=False), 2):
            diff = float(a.score) - float(b.score)
            if not bool(a.higher_is_better):
                diff = -diff
            if diff > 0:
                y = 1.0
            elif diff < 0:
                y = 0.0
            else:
                y = 0.5
            if margin_method == "none":
                raw_weight = 1.0
            else:
                margin = min(abs(float(a.score) - float(b.score)) / scale, 1.0)
                raw_weight = epsilon_m + (1.0 - epsilon_m) * margin
            raw_rows.append(
                {
                    "dimension": dim,
                    "benchmark_family": family,
                    "setting_id": setting_id,
                    "model_i": a.model_id,
                    "model_j": b.model_id,
                    "y": y,
                    "raw_margin_weight": raw_weight,
                    "score_i": float(a.score),
                    "score_j": float(b.score),
                }
            )
        raw_total = sum(r["raw_margin_weight"] for r in raw_rows)
        family_total = 1.0 / family_counts[dim]
        setting_total = family_total / setting_counts[(dim, family)]
        for item in raw_rows:
            item["weight"] = item["raw_margin_weight"] / raw_total * setting_total if raw_total else 0.0
            rows.append(item)
    return pd.DataFrame(rows)


def graph_diagnostics(pairwise: pd.DataFrame, all_models: list[str]) -> dict[str, object]:
    graph = nx.Graph()
    graph.add_nodes_from(all_models)
    for row in pairwise.itertuples(index=False):
        graph.add_edge(row.model_i, row.model_j)
    components = [sorted(c) for c in nx.connected_components(graph)]
    largest = max((len(c) for c in components), default=0)
    active = sorted(set(pairwise["model_i"]).union(set(pairwise["model_j"]))) if len(pairwise) else []
    active_graph = graph.subgraph(active).copy()
    active_components = [sorted(c) for c in nx.connected_components(active_graph)] if active else []
    active_largest = max((len(c) for c in active_components), default=0)
    return {
        "connected": bool(nx.is_connected(active_graph)) if len(active_graph) > 0 else False,
        "largest_connected_component": int(active_largest),
        "active_models": active,
        "components": active_components,
        "all_model_largest_component": int(largest),
    }


def pairwise_diagnostics(pairwise: pd.DataFrame, all_models: list[str]) -> pd.DataFrame:
    rows = []
    if pairwise.empty:
        return pd.DataFrame()
    for (dim, fam, setting), group in pairwise.groupby(["dimension", "benchmark_family", "setting_id"], sort=False):
        diag = graph_diagnostics(group, all_models)
        rows.append(
            {
                "dimension": dim,
                "family": fam,
                "setting": setting,
                "pairwise_comparison_count": len(group),
                "total_raw_margin_weight": float(group["raw_margin_weight"].sum()),
                "balanced_total_weight": float(group["weight"].sum()),
                "participating_models": "; ".join(diag["active_models"]),
                "comparison_graph_connectivity": "CONNECTED" if diag["connected"] else "PARTIAL_OR_SINGLE_SETTING",
            }
        )
    return pd.DataFrame(rows)

