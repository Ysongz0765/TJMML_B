"""Q2 figures from the frozen Q1-to-Q2 scenario utility interface."""

from __future__ import annotations

from pathlib import Path
import argparse
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Rectangle

from style import (
    COLORS,
    SCENARIO_LABELS,
    clean_axes,
    export_figure,
    ice_mist_sage_cmap,
    rank_cmap,
    short_model,
)


ROOT = Path(__file__).resolve().parents[2]
Q2 = ROOT / "q2" / "data"
Q3F = ROOT / "q3" / "frozen" / "v1.0"


def read_interface_text() -> str:
    return (ROOT / "q3" / "data" / "q2_to_q3_interface.md").read_text(encoding="utf-8")


def parse_scene_weights() -> pd.DataFrame:
    text = read_interface_text()
    records = []
    pattern = re.compile(r"-\s+(Research|General|Coding).*?:\s*(.*?)\.\s+alpha=.*?rho=([-\d.]+)\.", re.S)
    for scene, weights, rho in pattern.findall(text):
        pairs = re.findall(r"C(\d)=([0-9.]+)", weights)
        for dim, weight in pairs:
            records.append({"scenario": scene, "dimension": f"C{dim}", "weight": float(weight), "rho": float(rho)})
    if records:
        return pd.DataFrame(records)
    return pd.DataFrame(
        [
            {"scenario": "Research", "dimension": "C1", "weight": 0.3439, "rho": -0.50},
            {"scenario": "Research", "dimension": "C2", "weight": 0.3250, "rho": -0.50},
            {"scenario": "Research", "dimension": "C3", "weight": 0.3311, "rho": -0.50},
            {"scenario": "General", "dimension": "C1", "weight": 0.2417, "rho": 0.00},
            {"scenario": "General", "dimension": "C2", "weight": 0.3833, "rho": 0.00},
            {"scenario": "General", "dimension": "C3", "weight": 0.1000, "rho": 0.00},
            {"scenario": "General", "dimension": "C5", "weight": 0.2750, "rho": 0.00},
            {"scenario": "Coding", "dimension": "C1", "weight": 0.3500, "rho": -0.40},
            {"scenario": "Coding", "dimension": "C4", "weight": 0.6500, "rho": -0.40},
        ]
    )


def load_utility() -> pd.DataFrame:
    df = pd.read_csv(Q3F / "scenario_utility.csv")
    df["short_model"] = df["model_id"].map(short_model)
    return df


def load_q2_latent_strength() -> pd.DataFrame:
    theta = pd.read_csv(Q2 / "q1_bt_latent_scores.csv").set_index("model_id")
    z = theta[[f"C{i}_theta" for i in range(1, 6)]].copy()
    z.columns = [f"C{i}" for i in range(1, 6)]
    z = np.exp(z - z.max(axis=0))
    z["C5"] = z["C5"].fillna(0.35)
    return z


def ces_utility(values: np.ndarray, weights: np.ndarray, rho: float) -> float:
    shifted = values + 1e-6
    if abs(rho) <= 1e-10:
        return float(np.exp(np.sum(weights * np.log(shifted))))
    return float(np.sum(weights * shifted**rho) ** (1 / rho))


def fig_q2_weight_matrix(out: Path) -> None:
    demand = parse_scene_weights()
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    pivot = demand.pivot(index="scenario", columns="dimension", values="weight")
    pivot = pivot.reindex(["Research", "General", "Coding"]).reindex(columns=["C1", "C2", "C3", "C4", "C5"])
    masked = np.ma.masked_invalid(pivot.to_numpy(dtype=float))
    im = ax.imshow(masked, cmap=ice_mist_sage_cmap(), vmin=0, vmax=0.7)
    ax.imshow(np.zeros_like(pivot.values, dtype=float), cmap=ListedColormap([COLORS["neutral"]]), vmin=0, vmax=1, alpha=np.isnan(pivot.values) * 0.82)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([SCENARIO_LABELS[x] for x in pivot.index])
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            if pd.notna(pivot.iloc[i, j]):
                ax.text(j, i, f"{pivot.iloc[i,j]:.4f}", ha="center", va="center", fontsize=8)
            else:
                ax.text(j, i, "—", ha="center", va="center", fontsize=8, color=COLORS["muted"])
    ax.set_title("场景能力需求权重（KL projection 后）")
    ax.set_xlabel("Q1 能力维度")
    ax.set_ylabel("场景")
    ax.text(1.0, -0.22, "— = 该场景约束中不使用该维度", transform=ax.transAxes, ha="right", fontsize=7, color=COLORS["muted"])
    ax.set_xticks(np.arange(-0.5, len(pivot.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(pivot.index), 1), minor=True)
    ax.grid(which="minor", color=COLORS["white"], linewidth=0.6)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03, label="weight")
    export_figure(fig, out, "fig_q2_weight_matrix")


def fig_q2_utility_panels(out: Path) -> None:
    utility = load_utility()
    scenes = ["Research", "General", "Coding"]
    models = utility["model_id"].drop_duplicates().tolist()
    utility_pivot = utility.pivot(index="model_id", columns="scenario", values="utility").reindex(index=models, columns=scenes)
    rank_pivot = utility.pivot(index="model_id", columns="scenario", values="utility_rank").reindex(index=models, columns=scenes)
    model_order = (
        utility[utility["scenario"] == "Research"]
        .sort_values("utility_rank")["model_id"]
        .tolist()
    )
    utility_pivot = utility_pivot.reindex(model_order)
    rank_pivot = rank_pivot.reindex(model_order)
    fig, ax = plt.subplots(figsize=(8.25, 5.55))
    norm = Normalize(vmin=1, vmax=len(models))
    cmap = rank_cmap()
    for i, mid in enumerate(utility_pivot.index):
        for j, scene in enumerate(scenes):
            rank = float(rank_pivot.loc[mid, scene])
            utility_value = float(utility_pivot.loc[mid, scene])
            face = cmap(norm(rank))
            rect = Rectangle((j - 0.47, i - 0.42), 0.94, 0.84, facecolor=face, edgecolor=COLORS["white"], linewidth=1.0)
            ax.add_patch(rect)
            if rank <= 3:
                ax.add_patch(Rectangle((j - 0.47, i - 0.42), 0.94, 0.84, fill=False,
                                       edgecolor=COLORS["sage"] if rank == 1 else COLORS["mist_blue"],
                                       linewidth=1.4 if rank == 1 else 0.8))
            ax.text(j, i, f"{utility_value:.3f}", ha="center", va="center", fontsize=7.8, color=COLORS["ink"])
    ax.set_xlim(-0.55, len(scenes) - 0.45)
    ax.set_ylim(len(model_order) - 0.5, -0.5)
    ax.set_xticks(range(len(scenes)))
    ax.set_xticklabels([SCENARIO_LABELS[x] for x in scenes])
    ax.set_yticks(range(len(model_order)))
    ax.set_yticklabels([short_model(x) for x in model_order], fontsize=7.4)
    ax.set_xlabel("场景")
    ax.set_ylabel("模型")
    ax.set_title("场景效用排名矩阵：数值为 CES 效用，颜色表示场景内相对位置")
    ax.text(0.0, -0.13, "颜色仅表示对应场景内的相对效用位置；不用于跨场景绝对比较。边框表示 Top-1 / Top-3。",
            transform=ax.transAxes, fontsize=7, color=COLORS["muted"])
    ax.set_aspect("auto")
    clean_axes(ax, None)
    export_figure(fig, out, "fig_q2_utility_panels")


def fig_rank_migration(out: Path) -> None:
    q1 = pd.read_excel(ROOT / "outputs" / "q1_v1.2" / "tables" / "paper_table_q1_v12_bootstrap.xlsx", sheet_name="Ranking_A")
    q1["Q1综合"] = q1["main_rank"]
    utility = load_utility()
    rank = utility.pivot(index="model_id", columns="scenario", values="utility_rank")
    rank = q1.set_index("model_id")[["Q1综合"]].join(rank, how="inner")
    rank = rank.sort_values("Q1综合")
    stages = ["Q1综合", "Research", "General", "Coding"]
    x = np.arange(len(stages))
    fig, ax = plt.subplots(figsize=(8.9, 5.2))
    focal = {
        "gpt_5_6_sol_max": COLORS["mist_blue"],
        "claude_fable_5_max": COLORS["cream"],
        "kimi_k3_max": COLORS["sage"],
        "deepseek_v4_pro_max": COLORS["mist_blue"],
    }
    for idx, (mid, row) in enumerate(rank.iterrows()):
        y = row[stages].astype(float).to_numpy()
        is_focal = mid in focal
        alpha = 0.92 if is_focal else 0.18
        color = focal.get(mid, COLORS["mist_blue"])
        ax.plot(x, y, marker="o", color=color, alpha=alpha, linewidth=1.8 if is_focal else 0.7,
                markersize=4.2 if is_focal else 2.2)
        ax.text(3.04, y[-1], short_model(mid), va="center", fontsize=7.2, alpha=alpha)
    ax.set_xticks(x)
    ax.set_xticklabels(["Q1 综合", "科研", "日常", "代码"])
    ax.set_ylim(len(rank) + 0.4, 0.6)
    ax.set_ylabel("排名（1 为最好）")
    ax.set_title("Bump Chart：综合排名经过场景映射后的名次迁移")
    clean_axes(ax, "y")
    ax.grid(axis="x", visible=False)
    ax.set_xlim(-0.1, 3.9)
    export_figure(fig, out, "fig_q2_rank_migration")


def fig_rho_sensitivity(out: Path) -> None:
    strength = load_q2_latent_strength()
    nominal = load_utility().set_index(["scenario", "model_id"])
    dims = {"Research": ["C1", "C2", "C3"], "Coding": ["C1", "C4"]}
    weights = {"Research": np.array([0.3439, 0.3250, 0.3311]), "Coding": np.array([0.35, 0.65])}
    nominal_rho = {"Research": -0.5, "Coding": -0.4}
    rhos = np.linspace(-0.8, 0.4, 25)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.7), sharey=True)
    for ax, scene in zip(axes, ["Research", "Coding"]):
        values = []
        model_ids = strength.index.tolist()
        for mid in model_ids:
            vector = strength.loc[mid, dims[scene]].to_numpy(dtype=float)
            ranks = []
            for rho in rhos:
                u = ces_utility(vector, weights[scene], rho)
                if abs(rho - nominal_rho[scene]) <= 1e-10:
                    nominal_u = float(nominal.loc[(scene, mid), "utility"])
                    if abs(u - nominal_u) > 1e-5:
                        raise ValueError(
                            f"Nominal rho mismatch for {scene}/{mid}: recomputed={u:.8f}, frozen={nominal_u:.8f}"
                        )
                    u = nominal_u
                ranks.append(u)
            values.append(ranks)
        values = np.asarray(values)
        rank_values = np.argsort(np.argsort(-values, axis=0), axis=0) + 1
        im = ax.imshow(rank_values, aspect="auto", cmap=rank_cmap(), vmin=1, vmax=len(model_ids),
                       extent=[rhos.min(), rhos.max(), len(model_ids) - 0.5, -0.5])
        nominal_x = nominal_rho[scene]
        ax.axvline(nominal_x, color=COLORS["cream"], linestyle="--", linewidth=1.0)
        for i, mid in enumerate(model_ids):
            for j, rho in enumerate(rhos):
                if rank_values[i, j] <= 3 or mid in {"gpt_5_6_sol_max", "claude_fable_5_max", "kimi_k3_max", "deepseek_v4_pro_max"}:
                    ax.text(rho, i, str(int(rank_values[i, j])), ha="center", va="center", fontsize=5.5, color=COLORS["ink"])
        ax.set_yticks(range(len(model_ids)))
        ax.set_yticklabels([short_model(mid) for mid in model_ids], fontsize=6.7)
        ax.set_xlim(rhos.min() - 0.03, rhos.max() + 0.03)
        ax.set_ylim(len(model_ids) - 0.5, -0.5)
        ax.set_title(SCENARIO_LABELS[scene])
        ax.set_xlabel(r"$\rho$")
        ax.set_ylabel("模型" if ax is axes[0] else "")
        clean_axes(ax, None)
    fig.subplots_adjust(wspace=0.24, right=0.87, top=0.84, bottom=0.16)
    cax = fig.add_axes([0.89, 0.22, 0.018, 0.56])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("场景内排名（1 为最好）")
    fig.suptitle("CES 排名稳定性热图：替代弹性变化下的相对位置", y=1.02)
    export_figure(fig, out, "fig_q2_rho_sensitivity")


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_q2_weight_matrix(output_dir)
    fig_q2_utility_panels(output_dir)
    fig_rank_migration(output_dir)
    fig_rho_sensitivity(output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "paper_final" / "figures")
    main(parser.parse_args().output_dir)
