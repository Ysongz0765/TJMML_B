from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def _setup():
    plt.rcParams.update({"font.size": 10, "figure.dpi": 160, "savefig.dpi": 300})


def plot_cost_utility_scatter(pareto_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    complete = pareto_df.dropna(subset=["utility", "cost"])
    for scenario, group in complete.groupby("scenario", dropna=False):
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
        normal = group[group["pareto"] != True]
        front = group[group["pareto"] == True].sort_values("cost")
        ax.scatter(normal["cost"], normal["utility"], s=34, label="Dominated", color="#777777")
        ax.scatter(front["cost"], front["utility"], s=44, label="Pareto", color="#1f77b4")
        if len(front) > 1:
            ax.plot(front["cost"], front["utility"], color="#1f77b4", linewidth=1.2)
        for _, row in group.iterrows():
            ax.annotate(str(row["model_id"]), (row["cost"], row["utility"]), fontsize=6, xytext=(3, 3), textcoords="offset points")
        ax.set_xlabel("Workload cost (USD)")
        ax.set_ylabel("Scenario utility")
        ax.set_title(f"Cost-utility frontier: {scenario}")
        ax.legend(frameon=False)
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_cost_utility_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_budget_steps(budget_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    complete = budget_df.dropna(subset=["utility", "cost"])
    for scenario, group in complete.groupby("scenario", dropna=False):
        finite = group[group["budget_upper"] != float("inf")].copy()
        if finite.empty:
            continue
        fig, ax = plt.subplots(figsize=(5.2, 3.2))
        ax.step(finite["budget_lower"], finite["utility"], where="post", color="#2ca02c")
        ax.set_xlabel("Budget lower bound (USD)")
        ax.set_ylabel("Optimal utility")
        ax.set_title(f"Budget-constrained choice: {scenario}")
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_budget_steps_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_icer(icer_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    complete = icer_df.dropna(subset=["icer"])
    for scenario, group in complete.groupby("scenario", dropna=False):
        labels = group["from_model"].astype(str) + " to " + group["to_model"].astype(str)
        fig, ax = plt.subplots(figsize=(5.8, 3.4))
        ax.bar(range(len(group)), group["icer"], color="#9467bd")
        ax.set_xticks(range(len(group)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel("Incremental cost per utility unit")
        ax.set_title(f"ICER: {scenario}")
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_icer_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_fit_curves(cost_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    complete = cost_df.dropna(subset=["utility", "cost"])
    for scenario, group in complete.groupby("scenario", dropna=False):
        if len(group) < 3:
            continue
        x = group["cost"].astype(float).to_numpy()
        y = group["utility"].astype(float).to_numpy()
        order = np.argsort(x)
        coef = np.polyfit(x, y, 1)
        xgrid = np.linspace(float(np.min(x)), float(np.max(x)), 100)
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        ax.scatter(x, y, color="#1f77b4", s=36)
        ax.plot(xgrid, np.polyval(coef, xgrid), color="#d62728", linewidth=1.2, label="Linear fit")
        ax.plot(x[order], y[order], color="#777777", linewidth=0.8, alpha=0.6, label="Observed order")
        ax.set_xlabel("Workload cost (USD)")
        ax.set_ylabel("Scenario utility")
        ax.set_title(f"Cost-performance fit: {scenario}")
        ax.legend(frameon=False)
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_cost_performance_fit_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_ratio_switching(sensitivity_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    data = sensitivity_df[sensitivity_df["analysis"] == "input_output_ratio"].dropna(subset=["cost"])
    for scenario, group in data.groupby("scenario", dropna=False):
        pivot = group.pivot_table(index="model_id", columns="parameter", values="cost", aggfunc="min")
        if pivot.empty:
            continue
        fig, ax = plt.subplots(figsize=(5.6, 3.8))
        im = ax.imshow(pivot.to_numpy(dtype=float), aspect="auto", cmap="viridis")
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=7)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{c:g}" for c in pivot.columns])
        ax.set_xlabel("Output/input ratio")
        ax.set_title(f"Cost sensitivity map: {scenario}")
        fig.colorbar(im, ax=ax, label="Cost (USD)")
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_ratio_sensitivity_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_price_perturbation(sensitivity_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    data = sensitivity_df[sensitivity_df["analysis"] == "price_perturbation"].dropna(subset=["cost"])
    for scenario, group in data.groupby("scenario", dropna=False):
        fig, ax = plt.subplots(figsize=(5.4, 3.5))
        for model_id, model_group in group.groupby("model_id"):
            ax.plot(model_group["parameter"], model_group["cost"], marker="o", linewidth=0.9, markersize=3, label=model_id)
        ax.set_xlabel("Price perturbation")
        ax.set_ylabel("Workload cost (USD)")
        ax.set_title(f"Price robustness: {scenario}")
        ax.legend(frameon=False, fontsize=6, ncol=2)
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_price_perturbation_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def plot_pareto_probability(prob_df: pd.DataFrame, output_dir: Path) -> list[Path]:
    _setup()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    complete = prob_df.dropna(subset=["pareto_probability"])
    for scenario, group in complete.groupby("scenario", dropna=False):
        ordered = group.sort_values("pareto_probability", ascending=False)
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        ax.bar(ordered["model_id"], ordered["pareto_probability"], color="#17becf")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Pareto probability")
        ax.set_title(f"Bootstrap Pareto probability: {scenario}")
        ax.tick_params(axis="x", rotation=35, labelsize=7)
        fig.tight_layout()
        for ext in ["png", "pdf"]:
            path = output_dir / f"q3_pareto_probability_{scenario}.{ext}"
            fig.savefig(path)
            paths.append(path)
        plt.close(fig)
    return paths


def generate_all_plots(pareto_path, budget_path, output_dir, cost_path=None, icer_path=None, sensitivity_path=None, pareto_probability_path=None) -> list[Path]:
    paths = []
    pareto_path = Path(pareto_path)
    budget_path = Path(budget_path)
    if pareto_path.exists():
        pareto = pd.read_csv(pareto_path)
        paths.extend(plot_cost_utility_scatter(pareto, Path(output_dir)))
    if budget_path.exists():
        budget = pd.read_csv(budget_path)
        paths.extend(plot_budget_steps(budget, Path(output_dir)))
    if cost_path is not None and Path(cost_path).exists():
        paths.extend(plot_fit_curves(pd.read_csv(cost_path), Path(output_dir)))
    if icer_path is not None and Path(icer_path).exists():
        paths.extend(plot_icer(pd.read_csv(icer_path), Path(output_dir)))
    if sensitivity_path is not None and Path(sensitivity_path).exists():
        sensitivity = pd.read_csv(sensitivity_path)
        paths.extend(plot_ratio_switching(sensitivity, Path(output_dir)))
        paths.extend(plot_price_perturbation(sensitivity, Path(output_dir)))
    if pareto_probability_path is not None and Path(pareto_probability_path).exists():
        paths.extend(plot_pareto_probability(pd.read_csv(pareto_probability_path), Path(output_dir)))
    return paths
