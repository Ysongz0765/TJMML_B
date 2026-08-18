"""Q1 figures generated from Q1 v1.2 formal outputs and frozen matrix."""

from __future__ import annotations

from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import PowerNorm, ListedColormap

from style import (
    CANONICAL_SERIES,
    COLORS,
    STATUS_STYLE,
    clean_axes,
    export_figure,
    ice_mist_sage_cmap,
    mist_sage_cmap,
    short_model,
    short_setting,
)


ROOT = Path(__file__).resolve().parents[2]
Q1 = ROOT / "outputs" / "q1_v1.2"
Q2 = ROOT / "q2" / "data"
FROZEN = ROOT / "frozen" / "v1.0"


def load_capabilities() -> pd.DataFrame:
    df = pd.read_csv(Q2 / "q1_capability_scores.csv", keep_default_na=False)
    for col in ["C1_score", "C2_score", "C3_score", "C4_score", "C5_BT_score", "C5_effective_score"]:
        df[col] = pd.to_numeric(df[col].replace({"NA": np.nan, "": np.nan}), errors="coerce")
    return df


def fig_coverage(out: Path) -> None:
    df = pd.read_csv(FROZEN / "final_modeling_matrix_v1.0.csv", keep_default_na=False)
    value_cols = [c for c in df.columns if c.startswith("S_")]
    raw = df[value_cols].replace({"NA": np.nan, "": np.nan})
    matrix = raw.notna().astype(int)
    matrix.index = [short_model(mid, name) for mid, name in zip(df["model_id"], df["model_full_name"])]
    labels = [short_setting(c) for c in value_cols]
    setting_meta = pd.read_csv(Q2 / "benchmark_family_mapping.csv")
    setting_dim = setting_meta.set_index("exact_setting")["dimension"].to_dict()
    applicability = pd.read_csv(Q2 / "q1_model_applicability.csv").set_index("model_id")

    fig, ax = plt.subplots(figsize=(10.6, 4.15))
    cmap = ListedColormap([STATUS_STYLE["ordinary_missing"]["facecolor"], STATUS_STYLE["observed"]["facecolor"]])
    ax.imshow(matrix.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks(range(len(matrix)))
    ax.set_yticklabels(matrix.index)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6.5)
    ax.set_xlabel("Benchmark setting")
    ax.set_ylabel("Model")
    ax.set_title("Q1 数据覆盖矩阵：按能力维度分组，观察值与缺失值保持分离")
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(matrix), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.35)
    ax.tick_params(which="minor", bottom=False, left=False)

    groups = []
    for dim in ["C1", "C2", "C3", "C4", "C5"]:
        idx = [j for j, setting in enumerate(value_cols) if setting_dim.get(setting) == dim]
        if idx:
            groups.append((dim, min(idx), max(idx)))
            ax.axvline(max(idx) + 0.5, color=COLORS["white"], linewidth=1.0)
            ax.text((min(idx) + max(idx)) / 2, -1.13, dim, ha="center", va="bottom",
                    fontsize=8, color=COLORS["ink"], fontweight="bold")
    ax.text(-0.02, -1.13, "能力维度", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.5, color=COLORS["muted"])

    # Structural C5 absence is available in the applicability audit and is
    # shown separately from an ordinary unreported benchmark result.
    for r, model_id in enumerate(df["model_id"]):
        structural_c5 = (
            model_id in applicability.index
            and str(applicability.loc[model_id, "C5_status"]) == "STRUCTURAL_CAPABILITY_ABSENCE"
        )
        if not structural_c5:
            continue
        for c, setting in enumerate(value_cols):
            if setting_dim.get(setting) == "C5" and pd.isna(raw.iloc[r, c]):
                ax.add_patch(
                    Rectangle(
                        (c - 0.5, r - 0.5), 1, 1,
                        facecolor=STATUS_STYLE["structural_na"]["facecolor"],
                        edgecolor=COLORS["white"],
                        linewidth=0.35,
                        hatch=STATUS_STYLE["structural_na"]["hatch"],
                    )
                )
    legend_handles = [
        Rectangle((0, 0), 1, 1, facecolor=STATUS_STYLE["observed"]["facecolor"], edgecolor="none", label="observed"),
        Rectangle((0, 0), 1, 1, facecolor=STATUS_STYLE["ordinary_missing"]["facecolor"], edgecolor="none", label="ordinary missing"),
        Rectangle((0, 0), 1, 1, facecolor=STATUS_STYLE["structural_na"]["facecolor"], hatch="///", edgecolor=COLORS["muted"], label="structural NA"),
    ]
    ax.legend(handles=legend_handles, frameon=False, ncol=3, fontsize=7,
              loc="upper left", bbox_to_anchor=(0, 0.99))
    ax.set_ylim(len(matrix) - 0.5, -1.45)
    export_figure(fig, out, "fig_q1_coverage")


def fig_spearman(out: Path) -> None:
    df = pd.read_excel(ROOT / "outputs" / "stage3_llm_benchmark" / "spearman_missing_aware.xlsx", sheet_name="Rho")
    common_n = pd.read_excel(ROOT / "outputs" / "stage3_llm_benchmark" / "spearman_missing_aware.xlsx", sheet_name="PairwiseN")
    labels = df["setting_id"].tolist()
    rho = df.drop(columns=["setting_id"]).to_numpy(dtype=float)
    short = [short_setting(label) for label in labels]
    n_matrix = common_n.drop(columns=["setting_id"]).to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(9.4, 8.0))
    im = ax.imshow(rho, cmap=mist_sage_cmap(), vmin=-1, vmax=1)
    ax.set_xticks(range(len(short)))
    ax.set_xticklabels(short, rotation=55, ha="right", fontsize=6.2)
    ax.set_yticks(range(len(short)))
    ax.set_yticklabels(short, fontsize=6.2)
    ax.set_title("Missing-aware Spearman 相关结构（上三角为 Common-N）")
    ax.set_xlabel("Benchmark setting；上三角数字为共同有效模型数")
    ax.set_ylabel("Benchmark setting")
    for i in range(len(short)):
        for j in range(len(short)):
            if i == j:
                ax.text(j, i, "—", ha="center", va="center", fontsize=6, color=COLORS["muted"])
            elif j > i and np.isfinite(n_matrix[i, j]):
                ax.text(j, i, f"{int(n_matrix[i, j])}", ha="center", va="center", fontsize=5.5, color=COLORS["ink"])
    cbar = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    cbar.set_label("Spearman rho")
    ax.set_xticks(np.arange(-0.5, len(short), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(short), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.25)
    ax.tick_params(which="minor", bottom=False, left=False)
    export_figure(fig, out, "fig_q1_spearman")


def fig_radar_ranking(out: Path) -> None:
    cap = load_capabilities()
    ranking = pd.read_excel(Q1 / "tables" / "paper_table_q1_v12_bootstrap.xlsx", sheet_name="Ranking_A")
    merged = cap.merge(
        ranking[["model_id", "main_score", "main_rank", "score_ci_low", "score_ci_high"]],
        on="model_id",
        how="left",
    )
    dims = ["C1_score", "C2_score", "C3_score", "C4_score", "C5_BT_score"]
    labels = ["C1", "C2", "C3", "C4", "C5*"]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(12.2, 5.0))
    ax1 = fig.add_subplot(1, 2, 1, polar=True)
    ordered_by_score = merged.sort_values("main_score", ascending=False).reset_index(drop=True)
    for idx, row in ordered_by_score.iterrows():
        values = [np.nan if pd.isna(v) else float(v) for v in row[dims].tolist()]
        values += values[:1]
        is_top3 = idx < 3
        alpha = 0.9 if is_top3 else 0.25
        lw = 1.8 if is_top3 else 0.8
        color = CANONICAL_SERIES[idx % len(CANONICAL_SERIES)]
        ax1.plot(angles, values, color=color, alpha=alpha, linewidth=lw, label=short_model(row["model_id"]))
        if not any(pd.isna(values)):
            ax1.fill(angles, values, color=color, alpha=0.045 if is_top3 else 0.012)
    ax1.set_theta_offset(np.pi / 2)
    ax1.set_theta_direction(-1)
    ax1.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax1.set_ylim(0, 100)
    ax1.set_yticks([20, 40, 60, 80, 100])
    ax1.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7)
    ax1.grid(color=COLORS["grid"], linewidth=0.55)
    ax1.set_title("(a) 五维能力结构", pad=18)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=2, frameon=False)

    ax2 = fig.add_subplot(1, 2, 2)
    ordered = ordered_by_score.sort_values("main_score", ascending=True).reset_index(drop=True)
    y = np.arange(len(ordered))
    for pos, (_, row) in enumerate(ordered.iterrows()):
        low = float(row["score_ci_low"])
        high = float(row["score_ci_high"])
        rank = int(row["main_rank"])
        is_top3 = rank <= 3
        color = [COLORS["sage"], COLORS["mist_blue"], COLORS["cream"]][rank - 1] if is_top3 else COLORS["ice_blue"]
        alpha = 0.95 if is_top3 else 0.68
        ax2.barh(
            pos,
            float(row["main_score"]),
            color=color,
            alpha=alpha,
            height=0.62,
            edgecolor=COLORS["muted"],
            linewidth=0.35,
            zorder=2,
        )
        ax2.errorbar(
            float(row["main_score"]),
            pos,
            xerr=[[float(row["main_score"]) - low], [high - float(row["main_score"])]],
            fmt="none",
            ecolor=COLORS["ink"],
            elinewidth=0.9,
            capsize=2.4,
            capthick=0.8,
            zorder=4,
        )
        ax2.text(min(104, float(row["main_score"]) + 2.0), pos, f"{float(row['main_score']):.1f}", va="center", fontsize=7.5)
    ax2.set_yticks(y)
    ax2.set_yticklabels([short_model(mid, name) for mid, name in zip(ordered["model_id"], ordered["model"])])
    ax2.set_xlim(0, 108)
    ax2.set_xlabel("Ranking A 综合得分（0–100）")
    ax2.set_title("(b) 综合得分条形长度与 Bootstrap 95% CI")
    ax2.grid(axis="y", visible=False)
    clean_axes(ax2, "x")
    fig.subplots_adjust(wspace=0.45, bottom=0.18, left=0.08, right=0.98)
    export_figure(fig, out, "fig_q1_radar_ranking")


def fig_rank_stability(out: Path) -> None:
    df = pd.read_csv(Q1 / "bootstrap" / "bootstrap_ranking_A_v1.2.csv")
    order = (
        pd.read_excel(Q1 / "tables" / "paper_table_q1_v12_bootstrap.xlsx", sheet_name="Ranking_A")
        .sort_values("main_rank")["model_id"]
        .tolist()
    )
    rank_table = pd.read_excel(Q1 / "tables" / "paper_table_q1_v12_bootstrap.xlsx", sheet_name="Ranking_A").set_index("model_id")
    samples = [df.loc[df["model_id"] == mid, "rank"].astype(float).to_numpy() for mid in order]
    fig, ax = plt.subplots(figsize=(8.8, 5.25))
    positions = np.arange(len(order))
    violins = ax.violinplot(samples, positions=positions, vert=False, showmeans=False, showmedians=False, showextrema=False)
    for body in violins["bodies"]:
        body.set_facecolor(COLORS["ice_blue"])
        body.set_edgecolor(COLORS["mist_blue"])
        body.set_linewidth(0.8)
        body.set_alpha(0.95)
    box = ax.boxplot(
        samples,
        positions=positions,
        vert=False,
        widths=0.22,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": COLORS["ink"], "linewidth": 1.0},
        whiskerprops={"color": COLORS["mist_blue"], "linewidth": 0.8},
        capprops={"color": COLORS["mist_blue"], "linewidth": 0.8},
    )
    for patch, mid in zip(box["boxes"], order):
        patch.set_facecolor(COLORS["sage"] if mid == "kimi_k3_max" else COLORS["white"])
        patch.set_edgecolor(COLORS["mist_blue"])
        patch.set_linewidth(0.8)
    point_ranks = rank_table.loc[order, "main_rank"].astype(float).to_numpy()
    ax.scatter(point_ranks, positions, color=COLORS["sage"], edgecolor=COLORS["ink"], s=34, zorder=4, label="Ranking A 点估计")
    ax.set_yticks(positions)
    ax.set_yticklabels([short_model(x) for x in order])
    ax.set_xlim(0.6, 10.4)
    ax.set_xticks(range(1, 11))
    ax.invert_yaxis()
    ax.set_xlabel("Bootstrap rank（1 为最好）")
    ax.set_ylabel("Model")
    ax.set_title("Bootstrap 排名分布：分布、IQR 与 Ranking A 点估计")
    ax.legend(frameon=False, loc="upper right", fontsize=7)
    clean_axes(ax, "x")
    export_figure(fig, out, "fig_q1_rank_stability")


def fig_robustness(out: Path) -> None:
    df = pd.read_csv(Q1 / "sensitivity" / "lofo_summary_v1.2.csv")
    df["removed"] = df["removed"].str.replace("LiveBench ", "LB-", regex=False)
    df["removed"] = df["removed"].str.replace("Artificial Analysis", "AA", regex=False)
    df["removed"] = df["removed"].str.slice(0, 22)
    df = df.sort_values("spearman")
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    y = np.arange(len(df))
    valid = df["status"].eq("OK") & pd.to_numeric(df["spearman"], errors="coerce").notna()
    disconnected = ~valid
    ax.hlines(y[valid.to_numpy()], 0.88, df.loc[valid, "spearman"], color=COLORS["mist_blue"], linewidth=1.2)
    ax.scatter(df.loc[valid, "spearman"], y[valid.to_numpy()], color=COLORS["sage"], s=30, zorder=3)
    ax.scatter(
        np.full(disconnected.sum(), 0.88),
        y[disconnected.to_numpy()],
        marker="x",
        color=COLORS["ink"],
        s=42,
        linewidth=1.2,
        zorder=3,
    )
    ax.axvline(0.95, color=COLORS["cream"], linestyle="--", linewidth=1.1)
    ax.set_yticks(y)
    ax.set_yticklabels(df["removed"], fontsize=7)
    ax.set_xlim(0.86, 1.01)
    ax.set_xlabel("与完整 Ranking A 的 Spearman 相关")
    ax.set_title("LOFO 稳健性：有效比较与断开的比较网络")
    ax.text(0.88, -0.15, "× = network disconnected", transform=ax.transAxes, fontsize=7, color=COLORS["muted"])
    clean_axes(ax, "x")
    export_figure(fig, out, "fig_q1_robustness")


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_coverage(output_dir)
    fig_spearman(output_dir)
    fig_radar_ranking(output_dir)
    fig_rank_stability(output_dir)
    fig_robustness(output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "paper_final" / "figures")
    main(parser.parse_args().output_dir)
