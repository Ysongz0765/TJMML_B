"""Unified low-saturation scientific plotting style for the integrated paper."""

from __future__ import annotations

from pathlib import Path
import shutil

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.colors import LinearSegmentedColormap


PALETTE = {
    "mist_blue": "#8DB3D0",
    "cream": "#E5DABC",
    "sage": "#C0D7BE",
    "ice_blue": "#DCE9ED",
    "neutral": "#E6E8E9",
    "ink": "#4D5863",
    "grid": "#D9E0E4",
    "muted": "#8A969F",
    "white": "#FFFFFF",
}

COLORS = PALETTE

MODEL_STYLE = {
    "gpt_5_6_sol_max": {"color": PALETTE["mist_blue"], "emphasis": True},
    "claude_fable_5_max": {"color": PALETTE["cream"], "emphasis": True},
    "kimi_k3_max": {"color": PALETTE["sage"], "emphasis": True},
    "deepseek_v4_pro_max": {"color": PALETTE["mist_blue"], "emphasis": True},
    "qwen3_8_max": {"color": PALETTE["ice_blue"], "emphasis": False},
}

STATUS_STYLE = {
    "observed": {"facecolor": PALETTE["mist_blue"], "hatch": None},
    "ordinary_missing": {"facecolor": PALETTE["ice_blue"], "hatch": None},
    "structural_na": {"facecolor": PALETTE["neutral"], "hatch": "///"},
}

SCENARIO_LABELS = {
    "Research": "科研",
    "General": "日常",
    "Coding": "代码",
}

DIMENSION_LABELS = {
    "C1": "复杂推理",
    "C2": "知识事实",
    "C3": "长上下文",
    "C4": "代码工程",
    "C5": "多模态",
}

MODEL_SHORT = {
    "kimi_k3_max": "Kimi K3",
    "gpt_5_6_sol_max": "GPT-5.6 Sol",
    "gpt_5_5_xhigh": "GPT-5.5",
    "claude_fable_5_max": "Claude Fable 5",
    "claude_opus_4_8_max": "Claude Opus 4.8",
    "gemini_3_1_pro_high": "Gemini-3.1-Pro",
    "deepseek_v4_pro_max": "DeepSeek-V4-Pro",
    "deepseek_v4_flash_max": "DeepSeek-V4-Flash",
    "qwen3_8_max": "Qwen3.8-Max",
    "glm_5_2_max": "GLM-5.2",
}

SETTING_SHORT_LABELS = {
    "S_gpqa_diamond_diamond_openrouter_fixed_set_accuracy_tools_no": "GPQA",
    "S_livebench_logic_with_navigation_2026_06_25_task_score_tools_no": "LB Logic",
    "S_livebench_zebra_puzzle_2026_06_25_task_score_tools_no": "LB Zebra",
    "S_livebench_amps_hard_2026_06_25_task_score_tools_no": "LB AMPS",
    "S_livebench_math_comp_2026_06_25_task_score_tools_no": "LB Math",
    "S_livebench_olympiad_2026_06_25_task_score_tools_no": "LB Olympiad",
    "S_aa_omniscience_6_000_question_snapshot_2026_08_16_omniscience_index_tools_no": "AA Omni",
    "S_hle_text_only_aa_2_158_question_subset_snapshot_2026_08_16_accuracy_tools_no": "HLE",
    "S_aa_lcr_100_question_snapshot_2026_08_16_accuracy_tools_no": "AA LCR",
    "S_corpusqa_1m_1m_acc_tools_no": "CorpusQA",
    "S_mrcr_1m_1m_mmr_tools_no": "MRCR",
    "S_frontierswe_reported_dominance_score_tools_agent_harness": "FrontierSWE",
    "S_livebench_code_completion_2026_06_25_task_score_tools_no": "LB Code-C",
    "S_livebench_code_generation_2026_06_25_task_score_tools_no": "LB Code-G",
    "S_livebench_javascript_2026_06_25_task_score_tools_no": "LB JS",
    "S_livebench_python_2026_06_25_task_score_tools_no": "LB Python",
    "S_livebench_typescript_2026_06_25_task_score_tools_no": "LB TS",
    "S_programbench_reported_accuracy_tools_agent_harness": "ProgramBench",
    "S_swe_verified_verified_resolved_tools_agent_tools": "SWE Verified",
    "S_mmmu_pro_aa_protocol_snapshot_2026_08_16_accuracy_tools_no": "MMMU-Pro",
    "S_mathvision_reported_accuracy_tools_no": "MathVision",
}

CANONICAL_SERIES = [
    COLORS["mist_blue"],
    COLORS["cream"],
    COLORS["sage"],
    COLORS["ice_blue"],
]


def _find_cjk_family() -> str:
    candidates = [
        "Microsoft YaHei",
        "SimSun",
        "Noto Sans CJK SC",
        "Noto Serif CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    for family in candidates:
        try:
            path = findfont(FontProperties(family=family), fallback_to_default=False)
        except Exception:
            continue
        if path and Path(path).exists():
            return family
    return "DejaVu Sans"


def setup_style() -> None:
    cjk = _find_cjk_family()
    mpl.rcParams.update(
        {
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "savefig.facecolor": COLORS["white"],
            "font.family": "sans-serif",
            "font.serif": ["STIX Two Text", "DejaVu Serif"],
            "font.sans-serif": [cjk, "DejaVu Sans"],
            "axes.edgecolor": COLORS["ink"],
            "axes.labelcolor": COLORS["ink"],
            "xtick.color": COLORS["ink"],
            "ytick.color": COLORS["ink"],
            "text.color": COLORS["ink"],
            "axes.linewidth": 0.65,
            "axes.titleweight": "regular",
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.55,
            "grid.alpha": 0.85,
            "lines.linewidth": 1.5,
            "patch.linewidth": 0.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def clean_axes(ax, grid_axis: str = "x") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.65)
    ax.spines["bottom"].set_linewidth(0.65)
    ax.tick_params(length=3, width=0.6)
    if grid_axis in {"x", "both"}:
        ax.grid(axis="x", color=COLORS["grid"], linewidth=0.55, alpha=0.85)
    if grid_axis in {"y", "both"}:
        ax.grid(axis="y", color=COLORS["grid"], linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)


def export_figure(fig, output_dir: Path, stem: str, dpi: int = 300) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def short_model(model_id: str, fallback: str | None = None) -> str:
    return MODEL_SHORT.get(model_id, fallback or model_id)


def short_setting(setting_id: str) -> str:
    return SETTING_SHORT_LABELS.get(setting_id, setting_id.replace("S_", "")[:16])


def mist_sage_cmap(name: str = "mist_sage") -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        name,
        [COLORS["mist_blue"], COLORS["white"], COLORS["sage"]],
        N=256,
    )


def rank_cmap(name: str = "rank_mist") -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        name,
        [PALETTE["mist_blue"], PALETTE["ice_blue"]],
        N=256,
    )


def ice_mist_sage_cmap(name: str = "ice_mist_sage") -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        name,
        [COLORS["ice_blue"], COLORS["mist_blue"], COLORS["sage"]],
        N=256,
    )


setup_style()
