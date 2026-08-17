from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "figures" / "stage3"
OUT.mkdir(parents=True, exist_ok=True)
BUNDLE = json.loads((ROOT / "data/processed/stage3_analysis_bundle.json").read_text(encoding="utf-8"))
RAW = pd.read_csv(ROOT / "data/raw/raw_benchmark_data.csv", dtype=str, keep_default_na=False)
CORE = [
    "kimi_k3_max", "gpt_5_6_sol_max", "gpt_5_5_xhigh", "claude_fable_5_max", "claude_opus_4_8_max",
    "gemini_3_1_pro_high", "deepseek_v4_pro_max", "deepseek_v4_flash_max", "qwen3_8_max", "glm_5_2_max",
]
CAPS = [
    "C1 Complex reasoning", "C2 Knowledge and factual reliability", "C3 Long context",
    "C4 Code and software engineering", "C5 Multimodal",
]
SHORT = {model: model.replace("_max", "").replace("_high", "").replace("claude_", "cl_").replace("deepseek_", "ds_") for model in CORE}


def frame(name: str) -> pd.DataFrame:
    return pd.DataFrame(BUNDLE["tables"][name])


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / f"{name}.png", dpi=240, bbox_inches="tight", facecolor="white")
    plt.savefig(OUT / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close()


def graph_from(rows: pd.DataFrame, models: list[str]) -> nx.Graph:
    graph = nx.Graph(); graph.add_nodes_from(models)
    for _, group in rows.groupby("setting_id"):
        present = sorted(set(group.model_id) & set(models))
        for left, right in combinations(present, 2):
            graph.add_edge(left, right, weight=graph.get_edge_data(left, right, {}).get("weight", 0) + 1)
    return graph


def draw_model_graph(ax: plt.Axes, graph: nx.Graph, title: str, positions: dict[str, tuple[float, float]]) -> None:
    isolates = set(nx.isolates(graph))
    colors = ["#F4CCCC" if node in isolates else "#D9EAD3" for node in graph.nodes]
    widths = [min(3.5, .5 + graph[a][b].get("weight", 1) / 3) for a, b in graph.edges]
    nx.draw_networkx(graph, positions, ax=ax, labels=SHORT, node_color=colors, edge_color="#718096",
                     width=widths, node_size=900, font_size=6)
    ax.set_title(title, fontsize=10); ax.axis("off")


# 14: hierarchy from capability to family to exact setting.
manifest = frame("ModelingBenchmarkManifest")
graph = nx.DiGraph()
for _, row in manifest.iterrows():
    cap = row.capability.split()[0]
    family = row.benchmark_family
    setting = row.selected_setting
    graph.add_edge(cap, family); graph.add_edge(family, setting)
pos = {}
for x, cap in enumerate(["C1", "C2", "C3", "C4", "C5"]): pos[cap] = (x * 3, 3)
for cap, group in manifest.groupby("capability"):
    families = sorted(group.benchmark_family.unique()); cap_x = pos[cap.split()[0]][0]
    for idx, family in enumerate(families): pos[family] = (cap_x + (idx-(len(families)-1)/2)*1.15, 2)
for family, group in manifest.groupby("benchmark_family"):
    settings = sorted(group.selected_setting.unique()); fam_x = pos[family][0]
    for idx, setting in enumerate(settings): pos[setting] = (fam_x + (idx-(len(settings)-1)/2)*.55, .4)
plt.figure(figsize=(18, 10))
node_colors = ["#1F4E78" if n.startswith("C") and len(n) == 2 else "#70AD47" if n in set(manifest.benchmark_family) else "#D9E2F3" for n in graph.nodes]
font_colors = {n: "white" if (n.startswith("C") and len(n) == 2) or n in set(manifest.benchmark_family) else "#1F2933" for n in graph.nodes}
nx.draw_networkx_edges(graph, pos, arrows=False, edge_color="#AAB7C4", width=.8)
nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=[1800 if n in set(manifest.benchmark_family) else 1300 for n in graph.nodes])
for node, (x, y) in pos.items():
    label = node if len(node) < 32 else node[:29] + "..."
    plt.text(x, y, label, ha="center", va="center", fontsize=5.5 if node.startswith("S_") else 7,
             color=font_colors[node], wrap=True)
plt.title("Exact Setting -> Benchmark Family -> Capability hierarchy", fontsize=14); plt.axis("off"); save("14_benchmark_family_hierarchy")

# 15: source and family HHI by scope.
summary = frame("SourceConcentrationSummary").set_index("scope")
ax = summary[["HHI_source", "HHI_benchmark_family"]].plot.bar(figsize=(10, 5), color=["#4472C4", "#70AD47"])
ax.axhline(.25, color="#C55A11", linestyle="--", linewidth=1, label="HHI 0.25 reference")
ax.set_ylabel("HHI"); ax.set_ylim(0, 1); ax.set_title("Source and Benchmark-Family concentration"); ax.legend(); save("15_source_hhi")

# 16: C2/C3/C5 before-after network repair.
old = RAW[RAW.selected_for_common_matrix.str.lower().eq("true") & RAW.model_id.isin(CORE)].copy()
final = RAW[RAW.selected_for_final_modeling.str.lower().eq("true") & RAW.model_id.isin(CORE)].copy()
positions = nx.circular_layout(CORE)
fig, axes = plt.subplots(3, 2, figsize=(14, 15))
for row_idx, cap in enumerate([CAPS[1], CAPS[2], CAPS[4]]):
    draw_model_graph(axes[row_idx, 0], graph_from(old[old.capability_dimension.eq(cap)], CORE), f"{cap.split()[0]} before Phase3", positions)
    draw_model_graph(axes[row_idx, 1], graph_from(final[final.capability_dimension.eq(cap)], CORE), f"{cap.split()[0]} after Phase3", positions)
fig.suptitle("C2/C3/C5 comparison-network repair", fontsize=15, y=1.01); save("16_network_repair_before_after")

# 17: largest connected component ratios.
network = frame("NetworkQC").set_index("capability")
plot = network[["core_largest_component_ratio", "eligible_largest_component_ratio"]].copy()
plot.index = [idx.split()[0] for idx in plot.index]
ax = plot.plot.bar(figsize=(9, 5), color=["#A5A5A5", "#5B9BD5"])
ax.axhline(.8, color="#C00000", linestyle="--", label="80% gate")
ax.set_ylim(0, 1.08); ax.set_ylabel("Largest component ratio"); ax.set_title("Final network connected-component coverage"); ax.legend(); save("17_largest_component_ratio")

# 18: family coverage.
family_cov = manifest.groupby(["capability", "benchmark_family"]).model_coverage.mean().reset_index()
family_cov["label"] = family_cov.capability.str.split().str[0] + " | " + family_cov.benchmark_family
family_cov = family_cov.sort_values("model_coverage")
plt.figure(figsize=(10, 7)); plt.barh(family_cov.label, family_cov.model_coverage, color="#70AD47")
plt.axvline(.6, color="#C00000", linestyle="--", label="60% reference"); plt.xlim(0, 1.02)
plt.xlabel("Core-model coverage"); plt.title("Coverage by Benchmark Family"); plt.legend(); save("18_benchmark_family_coverage")

# 19: pairwise common sample size heatmap.
nmat = frame("SpearmanN").set_index("setting_id").astype(float)
plt.figure(figsize=(10, 9)); plt.imshow(nmat, vmin=0, vmax=10, cmap="YlGnBu")
plt.xticks(range(len(nmat)), nmat.columns, rotation=90, fontsize=4); plt.yticks(range(len(nmat)), nmat.index, fontsize=4)
plt.colorbar(label="Pairwise common model count"); plt.title("Pairwise sample-size matrix"); save("19_pairwise_sample_size_heatmap")

# 20: LiveBench full vs excluded structure.
lb = frame("LiveBenchDependency")
lb = lb[(lb.scenario.isin(["Full", "Exclude LiveBench"])) & lb.capability.isin([CAPS[0], CAPS[3]])].copy()
lb["cap"] = lb.capability.str.split().str[0]
pivot = lb.pivot(index="cap", columns="scenario", values="largest_component_ratio")
ax = pivot.plot.bar(figsize=(8, 5), color=["#ED7D31", "#4472C4"])
ax.axhline(.8, color="#C00000", linestyle="--", label="80% gate")
ax.set_ylim(0, 1.08); ax.set_ylabel("Eligible-model LCC ratio"); ax.set_title("LiveBench dependency: structural comparison"); ax.legend(); save("20_livebench_before_after")

# 21: reproducible data-preparation flow.
fig, ax = plt.subplots(figsize=(16, 4.5)); ax.set_xlim(0, 16); ax.set_ylim(0, 5); ax.axis("off")
steps = [
    ("Authoritative\nsource archive", "#D9EAF7"), ("RawData\nexact setting", "#D9EAD3"),
    ("Protocol + version\ncomparability audit", "#FFF2CC"), ("Benchmark Family\ndeduplication", "#FCE4D6"),
    ("Network + source\nsensitivity", "#E4DFEC"), ("Final matrix +\nrecord lineage", "#D9EAD3"),
    ("Human sign-off\n(PENDING)", "#F4CCCC"),
]
xs = np.linspace(.5, 14.4, len(steps))
for idx, ((label, color), x) in enumerate(zip(steps, xs)):
    box = FancyBboxPatch((x, 1.7), 1.55, 1.45, boxstyle="round,pad=0.08,rounding_size=0.08",
                         facecolor=color, edgecolor="#52616B", linewidth=1.2)
    ax.add_patch(box); ax.text(x+.775, 2.425, label, ha="center", va="center", fontsize=9)
    if idx < len(steps)-1:
        ax.add_patch(FancyArrowPatch((x+1.55, 2.425), (xs[idx+1], 2.425), arrowstyle="-|>", mutation_scale=12, color="#52616B"))
ax.text(8, 4.2, "Traceable LLM Benchmark data-readiness workflow", ha="center", fontsize=15, fontweight="bold")
ax.text(8, .7, "No guessed scores | Missing values remain NA | Matrix cell -> RawData record -> Source ID -> archived location", ha="center", fontsize=10)
save("21_data_preparation_flow")

print(json.dumps({"new_figure_pairs": 8, "output_directory": str(OUT)}, ensure_ascii=False))
