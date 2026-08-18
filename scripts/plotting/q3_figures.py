"""Q3 figures from frozen cost, Pareto, workload, and sensitivity outputs."""

from __future__ import annotations

from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from style import COLORS, SCENARIO_LABELS, clean_axes, export_figure, short_model


ROOT = Path(__file__).resolve().parents[2]
Q3F = ROOT / "q3" / "frozen" / "v1.0"


def fig_cost_components(out: Path) -> None:
    df = pd.read_csv(Q3F / "scenario_costs_final.csv")
    df = df[df["included_in_main_pareto"].astype(str).str.lower() == "true"].copy()
    df["label"] = df["model_id"].map(short_model)
    scene = "Coding"
    sub = df[df["scenario"] == scene].sort_values("total_cost")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    y = np.arange(len(sub))
    ax.barh(y, sub["input_cost"], color=COLORS["mist_blue"], label="输入成本")
    ax.barh(y, sub["output_cost"], left=sub["input_cost"], color=COLORS["cream"], label="输出成本")
    ax.set_yticks(y)
    ax.set_yticklabels(sub["label"])
    ax.set_xlabel("单个标准任务成本（USD）")
    ax.set_title("代码场景标准任务的成本构成（FULL 成本队列）")
    ax.legend(frameon=False, ncol=2, loc="lower right")
    clean_axes(ax, "x")
    for pos, val in enumerate(sub["total_cost"]):
        ax.text(val + sub["total_cost"].max() * 0.015, pos, f"{val:.5f}", va="center", fontsize=7)
    export_figure(fig, out, "fig_q3_cost_components")


def fig_pareto(out: Path) -> None:
    df = pd.read_csv(Q3F / "pareto_results_final.csv")
    df = df.merge(pd.read_csv(Q3F / "pareto_probability_final.csv"), on=["model_id", "scenario"], how="left")
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.2), sharey=False)
    for ax, scene in zip(axes, ["Research", "General", "Coding"]):
        group = df[df["scenario"] == scene].copy()
        frontier = group[group["pareto"].astype(str).str.lower() == "true"].sort_values("cost")
        dominated = group[group["pareto"].astype(str).str.lower() != "true"]
        ax.scatter(dominated["cost"], dominated["utility"], color=COLORS["mist_blue"], alpha=0.24, s=24, label="被支配")
        ax.scatter(frontier["cost"], frontier["utility"], color=COLORS["sage"], edgecolor=COLORS["ink"], linewidth=0.45, s=42, label="Pareto 节点")
        if len(frontier) > 1:
            ax.plot(frontier["cost"], frontier["utility"], color=COLORS["mist_blue"], linewidth=1.3)
        for _, row in frontier.iterrows():
            ax.text(row["cost"] * 1.02, row["utility"], short_model(row["model_id"]), fontsize=6.7, va="center")
        ax.set_xscale("log")
        ax.set_title(SCENARIO_LABELS[scene])
        ax.set_xlabel("成本（USD，log）")
        ax.set_ylabel("CES 效用")
        clean_axes(ax, "both")
    axes[0].legend(frameon=False, fontsize=7, loc="lower right")
    fig.suptitle("场景效用—成本 Pareto 前沿", y=1.02)
    fig.tight_layout()
    export_figure(fig, out, "fig_q3_pareto")


def fig_budget_steps(out: Path) -> None:
    switches = pd.read_csv(Q3F / "budget_switch_points_final.csv")
    scene_order = ["Research", "General", "Coding"]
    fig, axes = plt.subplots(3, 1, figsize=(10.8, 5.8), sharey=False)
    for ax, scene in zip(axes, scene_order):
        group = switches[switches["scenario"] == scene].sort_values("budget_threshold").copy()
        thresholds = group["budget_threshold"].astype(float).to_numpy()
        states = ["NO_FEASIBLE_MODEL"] + group["optimal_model_after"].tolist()
        x0 = max(thresholds[0] / 2.5, 1e-5)
        x1 = thresholds[-1] * 1.65
        bounds = np.concatenate([[x0], thresholds, [x1]])
        segment_colors = [COLORS["neutral"], COLORS["ice_blue"], COLORS["mist_blue"], COLORS["sage"], COLORS["cream"]]
        for idx, state in enumerate(states):
            left, right = bounds[idx], bounds[idx + 1]
            ax.barh(
                0, right - left, left=left, height=0.48,
                color=segment_colors[min(idx, len(segment_colors) - 1)],
                edgecolor=COLORS["white"], linewidth=0.8,
            )
            label = "无可行" if state == "NO_FEASIBLE_MODEL" else short_model(state)
            center = np.sqrt(left * right)
            if (right / left) > 1.35:
                ax.text(center, 0, label, ha="center", va="center", fontsize=7.0, color=COLORS["ink"])
        for threshold in thresholds:
            ax.axvline(threshold, color=COLORS["cream"], linewidth=0.8, alpha=0.9)
            ax.text(
                threshold,
                0.34,
                f"{threshold:.5f}",
                ha="center", va="bottom", fontsize=6.5, color=COLORS["ink"],
            )
        ax.set_yticks([0])
        ax.set_yticklabels([SCENARIO_LABELS[scene]], fontsize=8.2, fontweight="bold")
        ax.set_xscale("log")
        ax.set_ylim(-0.55, 0.55)
        ax.set_xlabel("预算上限（USD，log）")
        ax.grid(axis="x", color=COLORS["grid"], linewidth=0.55, alpha=0.85)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    axes[0].legend(
        handles=[
            Patch(facecolor=COLORS["neutral"], edgecolor="none", label="无可行"),
            Patch(facecolor=COLORS["ice_blue"], edgecolor="none", label="低预算节点"),
            Patch(facecolor=COLORS["mist_blue"], edgecolor="none", label="中间节点"),
            Patch(facecolor=COLORS["sage"], edgecolor="none", label="高效用节点"),
        ],
        frameon=False, ncol=4, fontsize=7, loc="upper left", bbox_to_anchor=(0, 1.45),
    )
    fig.suptitle("预算决策区间带：预算上限变化时的最优可行节点", y=0.995)
    fig.tight_layout()
    export_figure(fig, out, "fig_q3_budget_steps")


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_cost_components(output_dir)
    fig_pareto(output_dir)
    fig_budget_steps(output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "paper_final" / "figures")
    main(parser.parse_args().output_dir)
