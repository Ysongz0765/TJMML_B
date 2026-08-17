from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def setting_rank_table(long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for setting_id, group in long.groupby("setting_id", sort=False):
        values = group.dropna(subset=["score"]).copy()
        if values.empty:
            continue
        ascending = not bool(values["higher_is_better"].iloc[0])
        values["setting_rank_score"] = values["score"].rank(method="average", pct=True, ascending=ascending)
        rows.append(values[["model_id", "dimension", "benchmark_family", "setting_id", "setting_rank_score"]])
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def family_representation(long: pd.DataFrame) -> pd.DataFrame:
    ranked = setting_rank_table(long)
    family_scores = (
        ranked.groupby(["model_id", "dimension", "benchmark_family"], as_index=False)["setting_rank_score"]
        .mean()
        .rename(columns={"setting_rank_score": "family_score"})
    )
    return family_scores.pivot(index="model_id", columns="benchmark_family", values="family_score")


def missing_aware_spearman(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = list(table.columns)
    corr = pd.DataFrame(np.nan, index=cols, columns=cols, dtype=float)
    common_n = pd.DataFrame(0, index=cols, columns=cols, dtype=int)
    for a in cols:
        for b in cols:
            common = table[[a, b]].dropna()
            common_n.loc[a, b] = len(common)
            if a == b and len(common) > 0:
                corr.loc[a, b] = 1.0
            elif len(common) >= 3 and common[a].nunique() > 1 and common[b].nunique() > 1:
                rho = spearmanr(common[a], common[b]).correlation
                corr.loc[a, b] = float(rho) if np.isfinite(rho) else np.nan
    return corr, common_n


def family_screening(long: pd.DataFrame, corr: pd.DataFrame, common_n: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    coverage = (
        long.groupby(["dimension", "benchmark_family"])["score"]
        .apply(lambda s: float(s.notna().mean()))
        .reset_index(name="coverage")
    )
    rows = []
    for row in coverage.itertuples(index=False):
        fam = row.benchmark_family
        vals = corr.loc[fam].drop(labels=[fam], errors="ignore").abs().dropna()
        max_abs = float(vals.max()) if len(vals) else np.nan
        if len(vals):
            partner = vals.idxmax()
            n_val = int(common_n.loc[fam, partner])
        else:
            partner = ""
            n_val = 0
        flag = bool(np.isfinite(max_abs) and max_abs >= threshold)
        settings = long.loc[long["benchmark_family"].eq(fam), "setting_id"].nunique()
        network_role = "STRUCTURAL_BRIDGE" if row.coverage < 0.5 or settings == 1 else "STANDARD_INFORMATION"
        reason = "Retained: frozen v1.0 formal family mapping is fixed; redundancy is reported, not silently removed."
        rows.append(
            {
                "dimension": row.dimension,
                "benchmark_family": fam,
                "coverage": row.coverage,
                "max_abs_spearman": max_abs,
                "highest_corr_partner": partner,
                "common_n": n_val,
                "redundancy_flag": flag,
                "network_role": network_role,
                "retain_reason": reason,
            }
        )
    return pd.DataFrame(rows)

