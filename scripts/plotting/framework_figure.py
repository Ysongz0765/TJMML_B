"""Generate the paper-wide modeling framework diagram."""

from __future__ import annotations

from pathlib import Path
import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import COLORS, clean_axes, export_figure


def _draw_box(ax, x: float, y: float, w: float, h: float, text: str, facecolor: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=0.9,
        edgecolor=COLORS["ink"],
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.6, color=COLORS["ink"])


def main(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.4, 4.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    row1 = [
        "Benchmark",
        "missingness /\nredundancy",
        "Family-balanced\nBT",
        "C1-C5",
        "Ranking A",
        "KL projection",
    ]
    row2 = [
        "scenario\nweights",
        "CES\nutility",
        "workload /\npricing",
        "cost",
        "Pareto",
        "budget-aware\nselection",
    ]
    fills = [COLORS["ice_blue"], COLORS["mist_blue"], COLORS["cream"], COLORS["sage"]]
    box_w = 0.13
    box_h = 0.16
    gap = 0.033
    left = 0.035
    y1 = 0.64
    y2 = 0.20
    centers = []
    for idx, text in enumerate(row1):
        x = left + idx * (box_w + gap)
        face = fills[idx % len(fills)]
        _draw_box(ax, x, y1, box_w, box_h, text, face)
        centers.append((x + box_w / 2, y1 + box_h / 2))
    for idx, text in enumerate(row2):
        x = left + idx * (box_w + gap)
        face = fills[(idx + 1) % len(fills)]
        _draw_box(ax, x, y2, box_w, box_h, text, face)
    arrow_kw = dict(arrowstyle="->", color=COLORS["muted"], linewidth=1.1, shrinkA=4, shrinkB=4)
    for i in range(len(row1) - 1):
        ax.annotate("", xy=(centers[i + 1][0] - 0.01, centers[i + 1][1]), xytext=(centers[i][0] + 0.01, centers[i][1]), arrowprops=arrow_kw)
    ax.annotate("", xy=(left + box_w / 2, y2 + box_h + 0.005), xytext=(centers[-1][0], y1 - 0.005), arrowprops=arrow_kw)
    for i in range(len(row2) - 1):
        x0 = left + i * (box_w + gap)
        x1 = left + (i + 1) * (box_w + gap)
        ax.annotate("", xy=(x1 - 0.01, y2 + box_h / 2), xytext=(x0 + box_w + 0.01, y2 + box_h / 2), arrowprops=arrow_kw)
    ax.text(0.5, 0.92, "从公开 Benchmark 到预算约束选型", ha="center", va="center", fontsize=12.8, color=COLORS["ink"])
    clean_axes(ax, "both")
    export_figure(fig, output_dir, "fig_framework")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("paper_final") / "figures")
    main(parser.parse_args().output_dir)
