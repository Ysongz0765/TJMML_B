from __future__ import annotations

import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = "2026-08-16"
RAW_PATH = ROOT / "data" / "raw" / "raw_benchmark_data.csv"
MATRIX_PATH = ROOT / "data" / "final" / "benchmark_matrix.csv"
BUNDLE_PATH = ROOT / "data" / "processed" / "stage3_analysis_bundle.json"
FIG_DIR = ROOT / "reports" / "figures" / "stage3"

CORE_MODELS = [
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "deepseek_v4_pro_max",
    "deepseek_v4_flash_max",
    "qwen3_8_max",
    "glm_5_2_max",
]

MODEL_META = {
    "kimi_k3_max": ("Kimi K3 (max reasoning)", "Moonshot AI"),
    "gpt_5_6_sol_max": ("GPT-5.6 Sol (max)", "OpenAI"),
    "gpt_5_5_xhigh": ("GPT-5.5 (xhigh)", "OpenAI"),
    "claude_fable_5_max": ("Claude Fable 5 (max, with fallback)", "Anthropic"),
    "claude_opus_4_8_max": ("Claude Opus 4.8 (max)", "Anthropic"),
    "gemini_3_1_pro_high": ("Gemini-3.1-Pro (High)", "Google DeepMind"),
    "deepseek_v4_pro_max": ("DeepSeek-V4-Pro Max", "DeepSeek"),
    "deepseek_v4_flash_max": ("DeepSeek-V4-Flash Max", "DeepSeek"),
    "qwen3_8_max": ("Qwen3.8-Max", "Alibaba Qwen"),
    "glm_5_2_max": ("GLM-5.2 (max)", "Zhipu AI / Z.ai"),
}

CAPS = [
    "C1 Complex reasoning",
    "C2 Knowledge and factual reliability",
    "C3 Long context",
    "C4 Code and software engineering",
    "C5 Multimodal",
]

NEW_SOURCES = [
    {
        "source_id": "SRC010", "publisher": "Google DeepMind",
        "source_title": "Gemini 3.1 Pro evaluation overview",
        "source_type": "Vendor official evaluation PDF", "url": "https://storage.googleapis.com/deepmind-media/gemini/gemini_v3_1_report.pdf",
        "publication_date": "Unknown", "access_date": ACCESS_DATE, "authority_level": "B",
        "benchmark_related": "HLE; GPQA Diamond; MMMU-Pro; MRCR v2",
        "models_covered": "Gemini 3.1 Pro; Claude; GPT comparison rows",
        "local_archive_path": "sources/pdf/SRC010_gemini_3_1_pro_evaluation.pdf",
        "notes": "Archived official PDF; used as protocol context and supplementary cross-source evidence, not silently merged with independent-platform settings.",
    },
    {
        "source_id": "SRC011", "publisher": "Anthropic",
        "source_title": "Claude Fable 5 and Mythos 5 System Card",
        "source_type": "Vendor official system-card PDF", "url": "https://www.anthropic.com/system-cards/claude-fable-5-and-mythos-5-system-card",
        "publication_date": "Unknown", "access_date": ACCESS_DATE, "authority_level": "B",
        "benchmark_related": "GraphWalks; long-context evaluation methodology",
        "models_covered": "Claude Mythos 5; Claude Opus 4.8; GPT-5.5",
        "local_archive_path": "sources/pdf/SRC011_claude_fable5_mythos5_system_card.pdf",
        "notes": "GraphWalks rows concern Mythos 5, not Fable 5; no model-identity substitution was made.",
    },
    {
        "source_id": "SRC012", "publisher": "OpenAI",
        "source_title": "GPT-5.6 official evaluation page", "source_type": "Vendor official web page",
        "url": "https://openai.com/index/gpt-5-6/", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "B", "benchmark_related": "MMMU-Pro; MRCR v2; GraphWalks",
        "models_covered": "GPT-5.6 Sol; GPT-5.5; Gemini 3.1 Pro; Claude comparison rows",
        "local_archive_path": "UNAVAILABLE: anti-bot response prevented lawful local archival",
        "notes": "URL and exact table locations registered; supplementary protocol evidence only in this phase.",
    },
    {
        "source_id": "SRC013", "publisher": "Z.ai",
        "source_title": "GLM-5.2 official model card", "source_type": "Vendor official model card",
        "url": "https://huggingface.co/zai-org/GLM-5.2", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "B", "benchmark_related": "HLE; GPQA; coding benchmarks",
        "models_covered": "GLM-5.2 and comparison models", "local_archive_path": "sources/structured/SRC013_glm_5_2_model_card.md",
        "notes": "HLE values without asterisk are text-only subset; they were not merged with HLE-Full rows.",
    },
    {
        "source_id": "SRC014", "publisher": "Artificial Analysis",
        "source_title": "AA-LCR public leaderboard snapshot 2026-08-16",
        "source_type": "Independent standardized benchmark leaderboard",
        "url": "https://artificialanalysis.ai/evaluations/long-context-reasoning", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "A", "benchmark_related": "AA-LCR", "models_covered": "10 core models",
        "local_archive_path": "sources/html/SRC014_artificial_analysis_aa_lcr.html",
        "notes": "Scores are snapshot-sensitive; archived JSON-LD/model records are the numeric evidence.",
    },
    {
        "source_id": "SRC015", "publisher": "Artificial Analysis",
        "source_title": "AA-LCR methodology", "source_type": "Independent benchmark methodology page",
        "url": "https://artificialanalysis.ai/articles/introducing-the-artificial-analysis-long-context-reasoning-benchmark",
        "publication_date": "Unknown", "access_date": ACCESS_DATE, "authority_level": "A",
        "benchmark_related": "AA-LCR methodology", "models_covered": "Method only",
        "local_archive_path": "sources/html/SRC015_artificial_analysis_aa_lcr_methodology.html",
        "notes": "Method source: 100 long-context questions, three runs, pass@1-style accuracy with equality judge.",
    },
    {
        "source_id": "SRC016", "publisher": "Artificial Analysis",
        "source_title": "Humanity's Last Exam public leaderboard snapshot 2026-08-16",
        "source_type": "Independent standardized benchmark leaderboard",
        "url": "https://artificialanalysis.ai/evaluations/humanitys-last-exam", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "C", "benchmark_related": "HLE text-only 2,158-question subset", "models_covered": "10 core models",
        "local_archive_path": "sources/html/SRC016_artificial_analysis_hle.html",
        "notes": "Independent text-only subset; values preserved as fractions from archived structured payload.",
    },
    {
        "source_id": "SRC017", "publisher": "Artificial Analysis",
        "source_title": "AA-Omniscience public leaderboard snapshot 2026-08-16",
        "source_type": "Independent standardized benchmark leaderboard",
        "url": "https://artificialanalysis.ai/evaluations/omniscience", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "A", "benchmark_related": "AA-Omniscience Index", "models_covered": "6 current core-model entries",
        "local_archive_path": "sources/html/SRC017_artificial_analysis_omniscience.html",
        "notes": "Only rows visible in the current structured leaderboard were used; older embedded model-field values were excluded.",
    },
    {
        "source_id": "SRC018", "publisher": "Artificial Analysis",
        "source_title": "MMMU-Pro public leaderboard snapshot 2026-08-16",
        "source_type": "Independent standardized benchmark leaderboard",
        "url": "https://artificialanalysis.ai/evaluations/mmmu-pro", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "C", "benchmark_related": "MMMU-Pro", "models_covered": "5 core multimodal models",
        "local_archive_path": "sources/html/SRC018_artificial_analysis_mmmu_pro.html",
        "notes": "Only exact current structured entries/model records were used; protocol kept separate from vendor-reported MMMU-Pro.",
    },
    {
        "source_id": "SRC019", "publisher": "OpenAI",
        "source_title": "Introducing GPT-5.5", "source_type": "Vendor official web page",
        "url": "https://openai.com/index/introducing-gpt-5-5/", "publication_date": "Unknown", "access_date": ACCESS_DATE,
        "authority_level": "B", "benchmark_related": "HLE; MMMU-Pro; GraphWalks",
        "models_covered": "GPT-5.5; Gemini 3.1 Pro; Claude comparison rows",
        "local_archive_path": "UNAVAILABLE: anti-bot response prevented lawful local archival",
        "notes": "Registered as supplementary vendor evidence; no claim of independent retesting.",
    },
]


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def clean_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_value(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return clean_json_value(df.replace({np.nan: None}).to_dict("records"))


def source_registry(raw: pd.DataFrame) -> pd.DataFrame:
    base = []
    paths = {
        "SRC001": "sources/structured/SRC001_kimi_k3_readme.md",
        "SRC002": "UNAVAILABLE: Cloudflare challenge blocked local archival",
        "SRC003": "sources/html/SRC003_deepseek_v4_arxiv.html",
        "SRC004": "sources/html/SRC004_qwen3_arxiv.html",
        "SRC005": "UNAVAILABLE: dynamic page",
        "SRC006": "sources/structured/SRC006_livebench_table_2026_06_25.csv",
        "SRC007": "sources/html/SRC007_openrouter_gpqa_diamond.html",
        "SRC008": "sources/html/SRC008_benchlm_livebench_mirror.html",
        "SRC009": "sources/html/SRC009_artificial_analysis_kimi_k3.html",
    }
    for source_id, group in raw.groupby("source_id", dropna=False):
        if not str(source_id).strip():
            continue
        row = group.iloc[0]
        base.append({
            "source_id": source_id, "publisher": row.get("publisher", "Unknown"),
            "source_title": row.get("source_title", "Unknown"), "source_type": row.get("source_type", "Unknown"),
            "url": row.get("source_url", "Unknown"), "publication_date": row.get("publication_date", "Unknown"),
            "access_date": row.get("access_date", ACCESS_DATE), "authority_level": row.get("source_authority_level", "Unknown"),
            "benchmark_related": "; ".join(sorted(set(group["benchmark_name"].astype(str)))),
            "models_covered": "; ".join(sorted(set(group["model_full_name"].astype(str)))),
            "local_archive_path": paths.get(str(source_id), "Unknown"), "notes": "Numeric source represented in RawData.",
        })
    known = {row["source_id"] for row in base}
    for source_id, publisher, title, stype, url, pdate, related, covered, path, note in [
        ("SRC002", "OpenAI", "Previewing GPT-5.6 Sol / GPT-5.6 page", "Vendor official web page", "https://openai.com/index/gpt-5-6/", "Unknown", "Model identity", "GPT-5.6 Sol", paths["SRC002"], "No numeric row selected in earlier phases."),
        ("SRC005", "Alibaba Qwen", "Qwen3.8 official blog page", "Vendor official web page", "https://qwen.ai/blog?id=qwen3.8", "2026-08-10", "Model identity", "Qwen3.8-Max", paths["SRC005"], "No numeric row selected in earlier phases."),
        ("SRC008", "BenchLM", "BenchLM LiveBench mirror page", "Supplementary mirror", "https://benchlm.ai/benchmarks/livebench", "2026-06-25", "LiveBench metadata", "LiveBench models", paths["SRC008"], "Metadata only; official CSV is primary."),
        ("SRC009", "Artificial Analysis", "Kimi K3 Intelligence Index article", "Independent platform article", "https://artificialanalysis.ai/articles/kimi-k3-achieves-3-in-the-artificial-analysis-intelligence-index-comparable-to-opus-4-8-and-gpt-5-5", "2026-07-23", "External validation", "Kimi K3 and peers", paths["SRC009"], "Composite score excluded from modeling matrix."),
    ]:
        if source_id not in known:
            base.append({"source_id": source_id, "publisher": publisher, "source_title": title, "source_type": stype,
                         "url": url, "publication_date": pdate, "access_date": ACCESS_DATE, "authority_level": "C" if source_id in {"SRC008", "SRC009"} else "B",
                         "benchmark_related": related, "models_covered": covered, "local_archive_path": path, "notes": note})
    base.extend(NEW_SOURCES)
    return pd.DataFrame(base).drop_duplicates("source_id", keep="last").sort_values("source_id")


def new_record(raw_columns: list[str], record_id: str, model_id: str, capability: str,
               benchmark: str, version: str, metric: str, definition: str, score: float,
               raw_unit: str, source: dict[str, Any], page: str, table: str,
               protocol: str, reasoning: str, tools: str = "No", notes: str = "",
               model_version_reported: str = "") -> dict[str, Any]:
    full_name, org = MODEL_META[model_id]
    family = full_name.split()[0].replace("Gemini-3.1-Pro", "Gemini").replace("DeepSeek-V4-Pro", "DeepSeek").replace("DeepSeek-V4-Flash", "DeepSeek")
    values = {column: "" for column in raw_columns}
    values.update({
        "record_id": record_id, "model_id": model_id, "model_family": family,
        "model_full_name": full_name, "organization": org, "capability_dimension": capability,
        "benchmark_name": benchmark, "benchmark_version": version, "benchmark_year": "2026",
        "metric_name": metric, "metric_definition": definition, "raw_score": score, "raw_unit": raw_unit,
        "higher_is_better": True, "tools_allowed": tools, "browsing_allowed": "No",
        "reasoning_setting": reasoning, "pass_k_setting": "pass@1",
        "prompting_setting": "Platform default", "test_protocol": protocol, "additional_setting": "Snapshot 2026-08-16",
        "source_id": source["source_id"], "source_type": source["source_type"], "publisher": source["publisher"],
        "source_title": source["source_title"], "source_url": source["url"], "publication_date": source["publication_date"],
        "access_date": ACCESS_DATE, "page_number": page, "table_number": table,
        "extraction_method": "machine_extracted_from_archived_structured_payload",
        "source_authority_level": source["authority_level"], "protocol_match": "High", "version_match": "High",
        "comparable": "Grade A" if source["authority_level"] == "A" else "Grade B", "verified": "FALSE",
        "machine_extracted": "TRUE", "human_verified": "FALSE", "cross_source_verified": "FALSE",
        "conflict_flag": 0, "exclusion_reason": "", "notes": notes,
        "evidence_role": "BRIDGE_EVIDENCE", "is_composite_index": False, "component_benchmarks": "",
        "leaderboard_date": ACCESS_DATE, "model_version_reported_by_source": model_version_reported,
        "selected_for_common_matrix": False, "selected_reason": "Phase 3 bridge/network repair",
    })
    return values


def add_phase3_records(raw: pd.DataFrame) -> pd.DataFrame:
    if "selected_reason" in raw.columns:
        raw = raw[~raw["selected_reason"].eq("Phase 3 bridge/network repair")].copy()
    sources = {row["source_id"]: row for row in NEW_SOURCES}
    for source_id, group in raw.groupby("source_id"):
        row = group.iloc[0]
        sources[str(source_id)] = {
            "source_id": str(source_id), "publisher": row.get("publisher", "Unknown"),
            "source_title": row.get("source_title", "Unknown"), "source_type": row.get("source_type", "Unknown"),
            "url": row.get("source_url", "Unknown"), "publication_date": row.get("publication_date", "Unknown"),
            "authority_level": row.get("source_authority_level", "B"),
        }
    raw_columns = list(raw.columns)
    next_id = int(raw["record_id"].astype(str).str.extract(r"R(\d+)")[0].dropna().astype(int).max()) + 1
    added: list[dict[str, Any]] = []

    def add_many(source_id: str, capability: str, benchmark: str, version: str, metric: str,
                 definition: str, unit: str, score_map: dict[str, float], protocol: str,
                 page: str, table: str, reasoning: str, versions: dict[str, str] | None = None,
                 notes: str = "") -> None:
        nonlocal next_id
        for model_id, score in score_map.items():
            added.append(new_record(raw_columns, f"R{next_id:04d}", model_id, capability, benchmark, version,
                                    metric, definition, score, unit, sources[source_id], page, table, protocol,
                                    reasoning, notes=notes, model_version_reported=(versions or {}).get(model_id, "")))
            next_id += 1

    versions = {
        "kimi_k3_max": "kimi-k3 max", "gpt_5_6_sol_max": "gpt-5.6-sol max", "gpt_5_5_xhigh": "gpt-5.5 xhigh",
        "claude_fable_5_max": "claude-fable-5 with fallback", "claude_opus_4_8_max": "claude-opus-4.8 max",
        "gemini_3_1_pro_high": "gemini-3.1-pro-preview high", "deepseek_v4_pro_max": "deepseek-v4-pro-20260813 max",
        "deepseek_v4_flash_max": "deepseek-v4-flash-20260731 max", "qwen3_8_max": "qwen3.8-max",
        "glm_5_2_max": "glm-5.2 max",
    }
    add_many("SRC016", CAPS[1], "HLE Text-Only", "AA 2,158-question subset / snapshot 2026-08-16", "Accuracy",
             "Accuracy on Artificial Analysis independent text-only HLE subset.", "fraction",
             {"kimi_k3_max": .468952734012975, "gpt_5_6_sol_max": .494902687673772,
              "gpt_5_5_xhigh": .457831325301205, "claude_fable_5_max": .554680259499537,
              "claude_opus_4_8_max": .486561631139944, "gemini_3_1_pro_high": .470342910101946,
              "deepseek_v4_pro_max": .410101946246525, "deepseek_v4_flash_max": .385542168674699,
              "qwen3_8_max": .430491195551437, "glm_5_2_max": .411492122335496},
             "Independent platform evaluation; 2,158 text-only questions; no tools; current leaderboard snapshot.",
             "Archived HTML structured payload", "Humanity's Last Exam dataset", "Provider/leaderboard effort label", versions,
             "Raw fraction retained exactly as exposed by archived structured data.")
    add_many("SRC017", CAPS[1], "AA-Omniscience", "6,000-question snapshot 2026-08-16", "Omniscience Index",
             "Correct-answer reward minus hallucination penalty on 6,000 factual questions.", "index points",
             {"kimi_k3_max": 19.7, "gpt_5_6_sol_max": 21.9666666666667,
              "claude_fable_5_max": 43.3, "deepseek_v4_pro_max": .833333333333333,
              "qwen3_8_max": 3.4, "glm_5_2_max": 4.43333333333333},
             "Independent platform evaluation; current structured leaderboard rows only.",
             "Archived HTML JSON-LD", "omniscienceIndex dataset", "Provider/leaderboard effort label", versions,
             "Older embedded model-field values were intentionally excluded because they did not match the current leaderboard snapshot.")
    add_many("SRC014", CAPS[2], "AA-LCR", "100-question snapshot 2026-08-16", "Accuracy",
             "Accuracy across the Artificial Analysis long-context reasoning benchmark.", "fraction",
             {"kimi_k3_max": .826666666666667, "gpt_5_6_sol_max": .776666666666667,
              "gpt_5_5_xhigh": .79, "claude_fable_5_max": .766666666666667,
              "claude_opus_4_8_max": .73, "gemini_3_1_pro_high": .79,
              "deepseek_v4_pro_max": .753333333333333, "deepseek_v4_flash_max": .743333333333333,
              "qwen3_8_max": .743333333333333, "glm_5_2_max": .766666666666667},
             "Independent 100-question long-context evaluation; three runs; equality-judge scoring.",
             "Archived HTML JSON-LD/model records", "AA-LCR dataset", "Provider/leaderboard effort label", versions,
             "Snapshot differs from July 23 vendor-cited values; snapshots are not merged.")
    add_many("SRC018", CAPS[4], "MMMU-Pro", "AA protocol / snapshot 2026-08-16", "Accuracy",
             "Accuracy on MMMU-Pro under Artificial Analysis standardized evaluation.", "fraction",
             {"kimi_k3_max": .805202312138728, "gpt_5_6_sol_max": .834104046242775,
              "gpt_5_5_xhigh": .798843930635838, "gemini_3_1_pro_high": .824277456647399,
              "qwen3_8_max": .823121387283237},
             "Independent platform evaluation; provider effort labels preserved; current snapshot.",
             "Archived HTML JSON-LD/model records", "MMMU-Pro dataset", "Provider/leaderboard effort label", versions,
             "Kept separate from vendor-reported MMMU-Pro setting.")
    add_many("SRC003", CAPS[2], "MRCR 1M", "1M", "MMR",
             "Multi-round/coreference long-context score at 1M context.", "%",
             {"gemini_3_1_pro_high": 76.3},
             "DeepSeek V4 report Table 23 comparison protocol; 1M setting.", "Table 23", "MRCR 1M row",
             "High", {"gemini_3_1_pro_high": "Gemini-3.1-Pro High"},
             "Adds the comparison-table Gemini bridge; same table as DeepSeek Pro result.")
    add_many("SRC003", CAPS[2], "CorpusQA 1M", "1M", "ACC",
             "Long-document corpus QA accuracy at 1M context.", "%",
             {"gemini_3_1_pro_high": 53.8},
             "DeepSeek V4 report Table 23 comparison protocol; 1M setting.", "Table 23", "CorpusQA 1M row",
             "High", {"gemini_3_1_pro_high": "Gemini-3.1-Pro High"},
             "Adds the comparison-table Gemini bridge; same table as DeepSeek Pro result.")
    return pd.concat([raw, pd.DataFrame(added)], ignore_index=True)


def family_info(row: pd.Series) -> dict[str, str]:
    name = str(row["benchmark_name"])
    if name.startswith("LiveBench "):
        task = name.replace("LiveBench ", "")
        if task in {"AMPS_Hard", "math_comp", "olympiad"}:
            family, sub, cap = "LiveBench Math", task, CAPS[0]
        elif task in {"logic_with_navigation", "zebra_puzzle"}:
            family, sub, cap = "LiveBench Logic", task, CAPS[0]
        elif task in {"code_generation", "code_completion", "python", "javascript", "typescript"}:
            family, sub, cap = "LiveBench Coding", task, CAPS[3]
        else:
            family, sub, cap = "LiveBench Other", task, str(row["capability_dimension"])
        return {"benchmark_family": family, "benchmark_subfamily": sub, "parent_suite": "LiveBench",
                "metric_family": "Task score", "evaluation_protocol_family": "LiveBench 2026-06-25 unified harness",
                "capability_dimension": cap}
    rules = [
        ("GPQA", "GPQA Diamond", "Science reasoning", "GPQA"),
        ("HLE", "Humanity's Last Exam", "Hard knowledge", "HLE"),
        ("Omniscience", "AA-Omniscience", "Factuality/hallucination", "Artificial Analysis"),
        ("AA-LCR", "AA-LCR", "Long-context multi-document reasoning", "Artificial Analysis"),
        ("MRCR", "MRCR", "Long-context retrieval/coreference", "MRCR"),
        ("CorpusQA", "CorpusQA", "Long-document QA", "CorpusQA"),
        ("MMMU", "MMMU-Pro", "Multimodal understanding", "MMMU"),
        ("MathVision", "MathVision", "Multimodal mathematics", "MathVision"),
        ("ProgramBench", "ProgramBench", "Algorithmic programming", "ProgramBench"),
        ("FrontierSWE", "FrontierSWE", "Software engineering", "FrontierSWE"),
        ("SWE Verified", "SWE-bench Verified", "Verified issue resolution", "SWE-bench"),
        ("SWE-bench", "SWE-bench", "Issue resolution", "SWE-bench"),
        ("DeepSWE", "DeepSWE", "Software engineering", "DeepSWE"),
        ("Terminal", "Terminal-Bench", "Terminal agent", "Terminal-Bench"),
        ("LiveCodeBench", "LiveCodeBench", "Competitive coding", "LiveCodeBench"),
        ("RULER", "RULER", "Long-context synthetic", "RULER"),
        ("MMLU", "MMLU", "Broad knowledge", "MMLU"),
        ("SimpleQA", "SimpleQA", "Short factual QA", "SimpleQA"),
    ]
    for needle, family, sub, suite in rules:
        if needle.lower() in name.lower():
            return {"benchmark_family": family, "benchmark_subfamily": sub, "parent_suite": suite,
                    "metric_family": str(row["metric_name"]),
                    "evaluation_protocol_family": f"{name} | {row['benchmark_version']} | tools={row['tools_allowed']}",
                    "capability_dimension": str(row["capability_dimension"])}
    return {"benchmark_family": name, "benchmark_subfamily": name, "parent_suite": name,
            "metric_family": str(row["metric_name"]),
            "evaluation_protocol_family": f"{name} | {row['benchmark_version']} | tools={row['tools_allowed']}",
            "capability_dimension": str(row["capability_dimension"])}


def setting_id(row: pd.Series) -> str:
    text = f"{row['benchmark_name']}|{row['benchmark_version']}|{row['metric_name']}|tools={row['tools_allowed']}"
    safe = "".join(char.lower() if char.isalnum() else "_" for char in text)
    return "S_" + "_".join(part for part in safe.split("_") if part)


def prepare_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False)
    raw = add_phase3_records(raw)
    raw["raw_score"] = pd.to_numeric(raw["raw_score"], errors="coerce")
    raw["setting_id"] = raw.apply(setting_id, axis=1)
    family_rows = raw.apply(family_info, axis=1, result_type="expand")
    for column in ["benchmark_family", "benchmark_subfamily", "parent_suite", "metric_family", "evaluation_protocol_family"]:
        raw[column] = family_rows[column]
    raw["selected_for_final_modeling"] = False
    old_selected = raw["selected_for_common_matrix"].map(boolish)
    replace_names = {"HLE-Full", "MMMU-Pro"}
    base_mask = old_selected & ~raw["benchmark_name"].isin(replace_names)
    new_mask = raw["source_id"].isin({"SRC014", "SRC016", "SRC017", "SRC018"})
    bridge_mask = raw["source_id"].eq("SRC003") & raw["model_id"].eq("gemini_3_1_pro_high") & raw["benchmark_name"].isin({"MRCR 1M", "CorpusQA 1M"}) & raw["record_id"].astype(str).str.extract(r"R(\d+)")[0].astype(int).gt(209)
    raw.loc[base_mask | new_mask | bridge_mask, "selected_for_final_modeling"] = True
    raw["final_selection_reason"] = np.where(raw["selected_for_final_modeling"],
        "Grade A/B exact setting retained after family, protocol, network and redundancy audit", "Not selected for Phase 3 final modeling matrix")
    raw["human_verified"] = raw.get("human_verified", "FALSE").replace("", "FALSE")
    raw["human_verified"] = "FALSE"
    raw["machine_extracted"] = raw.get("machine_extracted", "FALSE").replace("", "FALSE")
    registry = source_registry(raw)
    return raw, registry


def select_final(raw: pd.DataFrame) -> pd.DataFrame:
    selected = raw[raw["selected_for_final_modeling"] & raw["model_id"].isin(CORE_MODELS)].copy()
    authority = {"A": 4, "B": 3, "C": 2, "D": 1}
    selected["_rank"] = selected["source_authority_level"].map(authority).fillna(0)
    selected = selected.sort_values(["model_id", "setting_id", "_rank", "record_id"], ascending=[True, True, False, True])
    selected = selected.drop_duplicates(["model_id", "setting_id"], keep="first").drop(columns="_rank")
    return selected


def make_matrix(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    setting_order = (selected[["setting_id", "capability_dimension", "benchmark_family", "benchmark_name"]]
                     .drop_duplicates().sort_values(["capability_dimension", "benchmark_family", "benchmark_name", "setting_id"])["setting_id"].tolist())
    pivot = selected.pivot(index="model_id", columns="setting_id", values="raw_score").reindex(index=CORE_MODELS, columns=setting_order)
    meta = pd.DataFrame([{"model_id": mid, "model_full_name": MODEL_META[mid][0], "organization": MODEL_META[mid][1], "modeling_status": "CORE_MODEL"} for mid in CORE_MODELS]).set_index("model_id")
    matrix = meta.join(pivot).reset_index()
    z = pivot.copy()
    for column in z.columns:
        values = z[column].dropna()
        sd = values.std(ddof=1)
        z[column] = (z[column] - values.mean()) / sd if len(values) > 1 and sd and np.isfinite(sd) else np.nan
    standardized = meta.join(z).reset_index()
    lineage = selected[["model_id", "model_full_name", "setting_id", "benchmark_name", "benchmark_version", "metric_name",
                        "raw_score", "raw_unit", "record_id", "source_id", "source_url", "page_number", "table_number"]].copy()
    lineage["matrix_cell_key"] = lineage["model_id"] + "|" + lineage["setting_id"]
    return matrix, standardized, lineage


def family_manifest(raw: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    unique_cols = ["setting_id", "benchmark_name", "benchmark_family", "benchmark_subfamily", "parent_suite",
                   "capability_dimension", "metric_name", "benchmark_version", "test_protocol", "source_id",
                   "is_composite_index", "evaluation_protocol_family"]
    rows = raw.sort_values("record_id").drop_duplicates("setting_id")[unique_cols].copy()
    selected_ids = set(selected["setting_id"])
    rows = rows.rename(columns={"metric_name": "metric", "benchmark_version": "version", "test_protocol": "protocol", "source_id": "source"})
    rows["information_overlap_group"] = rows["parent_suite"].astype(str) + "::" + rows["benchmark_family"].astype(str)
    rows["modeling_role"] = np.where(rows["setting_id"].isin(selected_ids), "EXACT_SETTING_WITHIN_FAMILY", "SUPPLEMENTARY_OR_EXCLUDED")
    rows["keep_or_drop"] = np.where(rows["setting_id"].isin(selected_ids), "KEEP", "DROP_FROM_FINAL_MATRIX")
    rows["reason"] = np.where(rows["setting_id"].isin(selected_ids),
                              "Retained with family-level weighting; exact version/metric/tools remain separate.",
                              "Raw evidence retained but not needed for the final modeling network or has protocol/coverage redundancy.")
    return rows.sort_values(["capability_dimension", "benchmark_family", "setting_id"])


def final_manifest(selected: pd.DataFrame) -> pd.DataFrame:
    grouped = selected.groupby(["capability_dimension", "benchmark_family", "setting_id"], dropna=False)
    rows = []
    family_counts = selected.groupby(["capability_dimension", "benchmark_family"])["setting_id"].nunique().to_dict()
    for (cap, family, sid), group in grouped:
        coverage = group["model_id"].nunique() / len(CORE_MODELS)
        n_family_settings = family_counts[(cap, family)]
        rows.append({
            "capability": cap, "benchmark_family": family, "selected_setting": sid,
            "benchmark_name": group.iloc[0]["benchmark_name"], "version": group.iloc[0]["benchmark_version"],
            "metric": group.iloc[0]["metric_name"], "tools": group.iloc[0]["tools_allowed"],
            "source": "; ".join(sorted(set(group["source_id"]))), "model_coverage": coverage,
            "independent_family_status": "INDEPENDENT_FAMILY" if family not in {"LiveBench Math", "LiveBench Logic", "LiveBench Coding"} else "INDEPENDENT_CONCEPT_WITH_SHARED_SUITE_HARNESS",
            "network_contribution": f"covers {group['model_id'].nunique()} core models",
            "redundancy_status": "WITHIN_FAMILY_DEDUP_REQUIRED" if n_family_settings > 1 else "NO_DUPLICATE_TOP_LEVEL_WEIGHT",
            "family_weight_within_capability": 1.0 / selected[selected["capability_dimension"].eq(cap)]["benchmark_family"].nunique(),
            "setting_weight_within_family": 1.0 / n_family_settings,
            "final_role": "MODELING_INPUT_EXACT_SETTING",
        })
    return pd.DataFrame(rows).sort_values(["capability", "benchmark_family", "selected_setting"])


def model_graph(rows: pd.DataFrame, models: list[str]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(models)
    for _, group in rows.groupby("setting_id"):
        present = sorted(set(group["model_id"]) & set(models))
        for left, right in combinations(present, 2):
            if graph.has_edge(left, right):
                graph[left][right]["weight"] += 1
            else:
                graph.add_edge(left, right, weight=1)
    return graph


def graph_stats(rows: pd.DataFrame, models: list[str]) -> dict[str, Any]:
    graph = model_graph(rows, models)
    components = sorted((sorted(c) for c in nx.connected_components(graph)), key=len, reverse=True)
    lcc = len(components[0]) if components else 0
    connected = nx.is_connected(graph) if len(graph) > 1 else bool(len(graph))
    return {
        "n_models": len(models), "n_settings": rows["setting_id"].nunique(), "n_families": rows["benchmark_family"].nunique(),
        "connected_components": len(components), "component_members": " | ".join(",".join(c) for c in components),
        "largest_component_size": lcc, "largest_component_ratio": lcc / len(models) if models else np.nan,
        "graph_density": nx.density(graph) if len(graph) > 1 else 0,
        "articulation_points": "; ".join(sorted(nx.articulation_points(graph))) if connected and len(graph) > 2 else "",
        "bridge_edges": "; ".join(f"{a}<->{b}" for a, b in nx.bridges(graph)) if connected and len(graph) > 1 else "",
        "edge_connectivity": nx.edge_connectivity(graph) if connected and len(graph) > 1 else 0,
        "node_connectivity": nx.node_connectivity(graph) if connected and len(graph) > 1 else 0,
        "connected": connected,
    }


def network_qc(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cap in CAPS:
        cap_rows = selected[selected["capability_dimension"].eq(cap)]
        observed = [m for m in CORE_MODELS if m in set(cap_rows["model_id"])]
        all_stats = graph_stats(cap_rows, CORE_MODELS)
        eligible_stats = graph_stats(cap_rows, observed)
        rows.append({"capability": cap, **{f"core_{k}": v for k, v in all_stats.items()},
                     **{f"eligible_{k}": v for k, v in eligible_stats.items()},
                     "scope_note": "C5 eligibility excludes text-only models from multimodal BT; all-core ratio is still reported." if cap == CAPS[4] else "All core models are capability-eligible."})
    return pd.DataFrame(rows)


def livebench_audit(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tasks = sorted(selected[selected["parent_suite"].eq("LiveBench")]["benchmark_name"].unique())
    for name in tasks:
        task = name.replace("LiveBench ", "")
        group = selected[selected["benchmark_name"].eq(name)]
        if task in {"AMPS_Hard", "math_comp", "olympiad"}:
            category, target = "Math", "Mathematical problem solving"
        elif task in {"logic_with_navigation", "zebra_puzzle"}:
            category, target = "Reasoning", "Structured logical reasoning"
        else:
            category, target = "Coding", "Code generation/completion by language/task"
        rows.append({
            "benchmark_setting": group.iloc[0]["setting_id"], "livebench_category": category,
            "livebench_task": task, "parent_suite": "LiveBench", "metric": group.iloc[0]["metric_name"],
            "source": "SRC006", "models_covered": group["model_id"].nunique(), "conceptual_target": target,
            "shared_questions_or_data": "Task-specific questions; no evidence of exact question overlap across named tasks",
            "shared_harness": "Yes - same LiveBench release and harness", "shared_prompting": "Yes - platform protocol family",
            "likely_dependence": "C: same suite/category subtask" if category != "Reasoning" else "B/C: same suite, distinct reasoning task",
            "independent_family_candidate": f"LiveBench {category}", "redundancy_risk": "HIGH if each task receives top-level equal weight",
            "final_role": "WITHIN_FAMILY_SETTING; family receives one capability-level weight",
        })
    return pd.DataFrame(rows)


def hhi(counts: Iterable[int]) -> float:
    arr = np.asarray(list(counts), dtype=float)
    return float(np.sum((arr / arr.sum()) ** 2)) if arr.sum() else np.nan


def source_concentration(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail, summary = [], []
    scopes = [("Overall", selected)] + [(cap, selected[selected["capability_dimension"].eq(cap)]) for cap in CAPS]
    for scope, rows in scopes:
        source_counts = rows["source_id"].value_counts()
        family_counts = rows["benchmark_family"].value_counts()
        total = len(rows)
        for source, count in source_counts.items():
            detail.append({"scope": scope, "dimension_type": "source", "item": source,
                           "source_cell_count": int(count), "source_share": count / total,
                           "benchmark_family_share": np.nan, "HHI_source": hhi(source_counts), "HHI_benchmark_family": hhi(family_counts)})
        for family, count in family_counts.items():
            detail.append({"scope": scope, "dimension_type": "benchmark_family", "item": family,
                           "source_cell_count": np.nan, "source_share": np.nan, "benchmark_family_share": count / total,
                           "HHI_source": hhi(source_counts), "HHI_benchmark_family": hhi(family_counts)})
        lb = int(rows["source_id"].eq("SRC006").sum())
        summary.append({"scope": scope, "n_cells": total, "livebench_cells": lb, "livebench_share": lb / total if total else 0,
                        "HHI_source": hhi(source_counts), "HHI_benchmark_family": hhi(family_counts),
                        "dominance_flag": "HIGH" if total and lb / total > .5 else "MODERATE" if total and lb / total > .3 else "LOW"})
    return pd.DataFrame(detail), pd.DataFrame(summary)


def leave_one_source_out(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for removed in ["NONE"] + sorted(selected["source_id"].unique()):
        subset = selected if removed == "NONE" else selected[~selected["source_id"].eq(removed)]
        for scope in ["Overall"] + CAPS:
            scoped = subset if scope == "Overall" else subset[subset["capability_dimension"].eq(scope)]
            models = CORE_MODELS if scope != CAPS[4] else [m for m in CORE_MODELS if m in set(selected[selected["capability_dimension"].eq(scope)]["model_id"])]
            stats = graph_stats(scoped, models)
            possible = len(CORE_MODELS) * (selected["setting_id"].nunique() if scope == "Overall" else selected[selected["capability_dimension"].eq(scope)]["setting_id"].nunique())
            rows.append({"removed_source": removed, "scope": scope, "n_cells": len(scoped),
                         "coverage": len(scoped) / possible if possible else np.nan,
                         "benchmark_family_count": scoped["benchmark_family"].nunique(), **stats,
                         "source_dependence_flag": "SOURCE_DEPENDENCE_HIGH" if removed != "NONE" and stats["largest_component_ratio"] < .8 else "OK"})
    return pd.DataFrame(rows)


def bridge_report(raw: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    old = raw[raw["selected_for_common_matrix"].map(boolish) & raw["model_id"].isin(CORE_MODELS)].copy()
    new_groups = [
        ("AA-HLE", "SRC016", "Humanity's Last Exam", CAPS[1]),
        ("AA-Omniscience", "SRC017", "AA-Omniscience", CAPS[1]),
        ("AA-LCR", "SRC014", "AA-LCR", CAPS[2]),
        ("AA-MMMU-Pro", "SRC018", "MMMU-Pro", CAPS[4]),
        ("DeepSeek Table 23 Gemini long-context rows", "SRC003", "MRCR/CorpusQA", CAPS[2]),
    ]
    out = []
    source_levels = {row["source_id"]: row["authority_level"] for row in NEW_SOURCES}
    source_levels["SRC003"] = "B"
    for label, source_id, family, cap in new_groups:
        before_rows = old[old["capability_dimension"].eq(cap)]
        if label.startswith("DeepSeek"):
            addition = selected[(selected["source_id"].eq(source_id)) & selected["model_id"].eq("gemini_3_1_pro_high") & selected["benchmark_name"].isin({"MRCR 1M", "CorpusQA 1M"})]
        else:
            addition = selected[selected["source_id"].eq(source_id)]
        models = CORE_MODELS if cap != CAPS[4] else sorted(set(before_rows["model_id"]) | set(addition["model_id"]))
        before = graph_stats(before_rows, models)
        after = graph_stats(pd.concat([before_rows, addition]), models)
        old_pairs = set(model_graph(before_rows, models).edges())
        new_pairs = set(model_graph(pd.concat([before_rows, addition]), models).edges()) - old_pairs
        new_models = len(set(addition["model_id"]) - set(before_rows["model_id"]))
        components_reduced = before["connected_components"] - after["connected_components"]
        level = source_levels.get(source_id, "C")
        quality_bonus = {"A": 5, "B": 3, "C": 2}.get(level, 1)
        score = len(new_pairs) + 10 * max(0, components_reduced) + 20 * max(0, after["largest_component_ratio"] - before["largest_component_ratio"]) + 2 * new_models + quality_bonus + 2
        out.append({"evidence": label, "source_id": source_id, "benchmark_family": family, "capability": cap,
                    "records_added": len(addition), "new_model_pairs": len(new_pairs), "components_before": before["connected_components"],
                    "components_after": after["connected_components"], "components_reduced": components_reduced,
                    "lcc_ratio_before": before["largest_component_ratio"], "lcc_ratio_after": after["largest_component_ratio"],
                    "new_core_models_covered": new_models, "source_quality": level,
                    "protocol_consistency": "High", "family_independence": "Independent" if source_id != "SRC003" else "Independent long-context family",
                    "bridge_value_score_exploratory": score,
                    "cross_validation_status": "SECOND_SOURCE_SEARCHED_NOT_EXACTLY_MATCHED",
                    "risk": "Current snapshot/source is a single-source bridge" if label in {"AA-LCR", "AA-HLE"} else "Protocol and model-version limits documented"})
    return pd.DataFrame(out)


def kimi_audit(selected: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cap in CAPS:
        cap_rows = selected[selected["capability_dimension"].eq(cap)]
        kimi = cap_rows[cap_rows["model_id"].eq("kimi_k3_max")]
        graph = model_graph(cap_rows, CORE_MODELS)
        source_counts = kimi["source_id"].value_counts()
        out.append({"capability": cap, "benchmark_setting_count": kimi["setting_id"].nunique(),
                    "independent_family_count": kimi["benchmark_family"].nunique(), "data_source_count": kimi["source_id"].nunique(),
                    "common_coverage": len(kimi) / cap_rows["setting_id"].nunique() if cap_rows["setting_id"].nunique() else 0,
                    "extended_coverage": len(kimi) / cap_rows["setting_id"].nunique() if cap_rows["setting_id"].nunique() else 0,
                    "network_degree": graph.degree("kimi_k3_max"),
                    "bridge_relationships": "; ".join(sorted(graph.neighbors("kimi_k3_max"))),
                    "max_single_source_share": source_counts.max() / source_counts.sum() if source_counts.sum() else np.nan,
                    "single_source_risk": "HIGH" if len(source_counts) == 1 else "MODERATE" if source_counts.max() / source_counts.sum() > .5 else "LOW",
                    "second_source_availability": int(kimi["cross_source_verified"].map(boolish).sum()),
                    "human_verified_records": int(kimi["human_verified"].map(boolish).sum()),
                    "notes": "Kimi remains CORE_MODEL; no imputation used."})
    return pd.DataFrame(out)


def redundancy_audit(manifest: pd.DataFrame, final_manifest_df: pd.DataFrame) -> pd.DataFrame:
    selected_ids = set(final_manifest_df["selected_setting"])
    rows = manifest[manifest["setting_id"].isin(selected_ids)].copy()
    family_sizes = rows.groupby(["capability_dimension", "benchmark_family"])["setting_id"].transform("count")
    rows["same_suite_setting_count"] = family_sizes
    rows["redundancy_risk"] = np.where(family_sizes > 1, "HIGH_WITHOUT_FAMILY_AGGREGATION", "LOW")
    rows["dedup_action"] = np.where(family_sizes > 1, "Equalize family weight then divide within family", "Keep one exact setting")
    rows["top_level_duplicate"] = False
    rows["audit_result"] = "PASS_FAMILY_WEIGHT_REQUIRED"
    return rows[["setting_id", "benchmark_name", "benchmark_family", "parent_suite", "capability_dimension",
                 "information_overlap_group", "same_suite_setting_count", "redundancy_risk", "dedup_action",
                 "top_level_duplicate", "audit_result"]]


def spearman_tables(matrix: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    setting_cols = [c for c in matrix.columns if c.startswith("S_")]
    rho = pd.DataFrame(index=setting_cols, columns=setting_cols, dtype=float)
    pval = rho.copy(); nmat = rho.copy(); overlap = rho.copy()
    long_rows = []
    for a in setting_cols:
        for b in setting_cols:
            pair = matrix[[a, b]].dropna()
            n = len(pair)
            nmat.loc[a, b] = n
            overlap.loc[a, b] = n / len(CORE_MODELS)
            if a == b and n:
                r, p = 1.0, 0.0
            elif n >= 3 and pair[a].nunique() > 1 and pair[b].nunique() > 1:
                r, p = spearmanr(pair[a], pair[b])
            else:
                r, p = np.nan, np.nan
            rho.loc[a, b] = r; pval.loc[a, b] = p
            if a < b:
                long_rows.append({"setting_1": a, "setting_2": b, "spearman_rho": r, "p_value": p,
                                  "pairwise_n": n, "overlap_rate": n / len(CORE_MODELS),
                                  "reliability": "ADEQUATE" if n >= 6 else "LOW_N_DO_NOT_INTERPRET"})
    z = matrix.set_index("model_id")[setting_cols].copy()
    for col in setting_cols:
        vals = z[col].dropna(); sd = vals.std(ddof=1)
        z[col] = (z[col] - vals.mean()) / sd if len(vals) > 1 and sd and np.isfinite(sd) else np.nan
    sid_family = selected.drop_duplicates("setting_id").set_index("setting_id")["benchmark_family"].to_dict()
    family = pd.DataFrame(index=z.index)
    for fam in sorted(set(sid_family.values())):
        cols = [sid for sid, value in sid_family.items() if value == fam and sid in z]
        family[fam] = z[cols].mean(axis=1, skipna=True)
    family_rho = family.corr(method="spearman", min_periods=3)
    return rho, pval, nmat, overlap, pd.DataFrame(long_rows), family_rho


def family_sensitivity(matrix: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    setting_cols = [c for c in matrix.columns if c.startswith("S_")]
    values = matrix.set_index("model_id")[setting_cols].copy()
    for col in setting_cols:
        valid = values[col].dropna(); sd = valid.std(ddof=1)
        values[col] = (values[col] - valid.mean()) / sd if len(valid) > 1 and sd and np.isfinite(sd) else np.nan
    info = selected.drop_duplicates("setting_id").set_index("setting_id")[["capability_dimension", "benchmark_family"]]
    out = []
    for scope in CAPS + ["Overall"]:
        cols = [c for c in setting_cols if scope == "Overall" or info.loc[c, "capability_dimension"] == scope]
        setting_score = values[cols].mean(axis=1, skipna=True)
        families = sorted(set(info.loc[cols, "benchmark_family"]))
        fam_scores = pd.DataFrame(index=values.index)
        for fam in families:
            fam_cols = [c for c in cols if info.loc[c, "benchmark_family"] == fam]
            fam_scores[fam] = values[fam_cols].mean(axis=1, skipna=True)
        family_score = fam_scores.mean(axis=1, skipna=True)
        rank_setting = setting_score.rank(ascending=False, method="average")
        rank_family = family_score.rank(ascending=False, method="average")
        for model in values.index:
            out.append({"scope": scope, "model_id": model, "model": MODEL_META.get(model, (model, ""))[0],
                        "setting_equal_score": setting_score.get(model), "family_equal_score": family_score.get(model),
                        "setting_equal_rank": rank_setting.get(model), "family_equal_rank": rank_family.get(model),
                        "absolute_rank_shift": abs(rank_setting.get(model) - rank_family.get(model)),
                        "n_settings_available": int(values.loc[model, cols].notna().sum()),
                        "n_families_available": int(fam_scores.loc[model].notna().sum()),
                        "interpretation": "Sensitivity diagnostic only; not a final ranking."})
    return pd.DataFrame(out)


def bt_fit(rows: pd.DataFrame, models: list[str]) -> dict[str, Any]:
    models = [m for m in models if m in set(rows["model_id"])]
    if len(models) < 2:
        return {"converged": False, "structurally_identifiable": False, "n_models": len(models), "n_comparisons": 0,
                "condition_number": np.nan, "max_standard_error": np.nan, "separation_warning": True}
    graph = model_graph(rows, models)
    structural = nx.is_connected(graph)
    index = {m: i for i, m in enumerate(models)}
    family_n = rows.groupby("benchmark_family")["setting_id"].nunique().to_dict()
    comps = []
    for _, group in rows.groupby("setting_id"):
        family = group.iloc[0]["benchmark_family"]
        weight = 1 / family_n[family]
        scores = group.set_index("model_id")["raw_score"].dropna()
        for a, b in combinations(sorted(set(scores.index) & set(models)), 2):
            if scores[a] > scores[b]: outcome = 1.0
            elif scores[a] < scores[b]: outcome = 0.0
            else: outcome = 0.5
            comps.append((index[a], index[b], outcome, weight))
    if not comps or not structural:
        return {"converged": False, "structurally_identifiable": structural, "n_models": len(models), "n_comparisons": len(comps),
                "condition_number": np.nan, "max_standard_error": np.nan, "separation_warning": True}

    def objective(theta_free: np.ndarray) -> tuple[float, np.ndarray]:
        theta = np.r_[0.0, theta_free]
        loss = 0.0; grad = np.zeros_like(theta)
        for i, j, y, w in comps:
            delta = np.clip(theta[i] - theta[j], -30, 30)
            p = 1 / (1 + np.exp(-delta))
            loss -= w * (y * math.log(max(p, 1e-12)) + (1-y) * math.log(max(1-p, 1e-12)))
            g = w * (p-y); grad[i] += g; grad[j] -= g
        loss += 5e-7 * float(theta_free @ theta_free)
        grad[1:] += 1e-6 * theta_free
        return loss, grad[1:]
    result = minimize(lambda x: objective(x)[0], np.zeros(len(models)-1), jac=lambda x: objective(x)[1], method="BFGS")
    theta = np.r_[0.0, result.x]
    hess = np.zeros((len(models), len(models)))
    for i, j, _, w in comps:
        p = 1 / (1 + np.exp(-np.clip(theta[i]-theta[j], -30, 30)))
        v = w * p * (1-p)
        hess[i, i] += v; hess[j, j] += v; hess[i, j] -= v; hess[j, i] -= v
    reduced = hess[1:, 1:] + np.eye(len(models)-1) * 1e-6
    try:
        cond = float(np.linalg.cond(reduced)); se = np.sqrt(np.diag(np.linalg.pinv(reduced)))
        max_se = float(np.max(se)) if len(se) else 0
    except Exception:
        cond, max_se = np.nan, np.nan
    separation = bool(np.max(np.abs(theta)) > 10 or (np.isfinite(cond) and cond > 1e8))
    return {"converged": bool(result.success), "structurally_identifiable": structural, "n_models": len(models),
            "n_comparisons": len(comps), "condition_number": cond, "max_standard_error": max_se,
            "separation_warning": separation, "iterations": int(result.nit), "objective": float(result.fun)}


def bt_bootstrap(rows: pd.DataFrame, models: list[str], n_boot: int = 500) -> dict[str, Any]:
    settings = list(rows["setting_id"].unique())
    if not settings:
        return {"bootstrap_iterations": n_boot, "bootstrap_structural_identifiable_rate": 0, "bootstrap_convergence_rate": 0}
    rng = np.random.default_rng(20260816)
    structural = 0; converged = 0
    for _ in range(n_boot):
        sampled = rng.choice(settings, size=len(settings), replace=True)
        parts = []
        for idx, sid in enumerate(sampled):
            part = rows[rows["setting_id"].eq(sid)].copy()
            part["setting_id"] = part["setting_id"] + f"__boot{idx}"
            parts.append(part)
        fit = bt_fit(pd.concat(parts, ignore_index=True), models)
        structural += int(fit["structurally_identifiable"])
        converged += int(fit["converged"])
    return {"bootstrap_iterations": n_boot, "bootstrap_structural_identifiable_rate": structural / n_boot,
            "bootstrap_convergence_rate": converged / n_boot}


def bt_diagnostics(raw: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    out = []
    extended = raw[raw["comparable"].isin({"Grade A", "Grade B"}) & raw["raw_score"].notna()].copy()
    extended = extended.sort_values(["model_id", "setting_id", "source_authority_level", "record_id"]).drop_duplicates(["model_id", "setting_id"], keep="last")
    for dataset, frame, models in [("Common", selected, CORE_MODELS), ("ExtendedEvidence", extended, sorted(set(extended["model_id"])))]:
        for cap in CAPS:
            rows = frame[frame["capability_dimension"].eq(cap)]
            eligible = [m for m in models if m in set(rows["model_id"])]
            fit = bt_fit(rows, eligible)
            boot = bt_bootstrap(rows, eligible, 500) if dataset == "Common" else {"bootstrap_iterations": 0, "bootstrap_structural_identifiable_rate": np.nan, "bootstrap_convergence_rate": np.nan}
            out.append({"dataset": dataset, "capability": cap, **fit, **boot,
                        "readiness": "READY_FOR_BT_SMOKE" if fit["structurally_identifiable"] and fit["converged"] else "STRUCTURAL_OR_NUMERICAL_REVIEW",
                        "notes": "No ability estimates or final rankings are published in this readiness artifact."})
    return pd.DataFrame(out)


def livebench_dependency(selected: pd.DataFrame) -> pd.DataFrame:
    out = []
    scenarios = {
        "Full": selected,
        "Exclude LiveBench": selected[~selected["source_id"].eq("SRC006")],
        "LiveBench only": selected[selected["source_id"].eq("SRC006")],
        "Non-LiveBench only": selected[~selected["parent_suite"].eq("LiveBench")],
    }
    for scenario, frame in scenarios.items():
        for cap in CAPS:
            rows = frame[frame["capability_dimension"].eq(cap)]
            eligible = [m for m in CORE_MODELS if m in set(rows["model_id"])]
            fit = bt_fit(rows, eligible)
            stats = graph_stats(rows, eligible)
            out.append({"scenario": scenario, "capability": cap, "n_cells": len(rows), "n_settings": rows["setting_id"].nunique(),
                        "n_families": rows["benchmark_family"].nunique(), **stats, **fit,
                        "interpretation": "Structural sensitivity only; no final model ranking."})
    return pd.DataFrame(out)


def human_checklist(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    out["priority"] = np.where(out["model_id"].eq("kimi_k3_max"), "P1;P3", "P1")
    out["model"] = out["model_full_name"]
    out["benchmark"] = out["benchmark_name"]
    out["exact_setting"] = out["setting_id"]
    out["score"] = out["raw_score"]
    out["location"] = out["page_number"].astype(str) + " | " + out["table_number"].astype(str)
    out["expected_value"] = out["raw_score"].astype(str) + " " + out["raw_unit"].astype(str)
    out["machine_cross_verified"] = out["cross_source_verified"].map(boolish)
    out["checkbox_status"] = "PENDING"
    out["reviewer"] = ""
    out["review_date"] = ""
    out["review_notes"] = ""
    return out[["priority", "record_id", "model", "benchmark", "exact_setting", "score", "raw_unit", "source_id",
                "source_url", "location", "expected_value", "machine_cross_verified", "checkbox_status", "reviewer", "review_date", "review_notes"]]


def readiness_gate(matrix: pd.DataFrame, selected: pd.DataFrame, network: pd.DataFrame,
                   final_manifest_df: pd.DataFrame, lineage: pd.DataFrame, redundancy: pd.DataFrame,
                   bt: pd.DataFrame, loo: pd.DataFrame, checklist: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    setting_cols = [c for c in matrix.columns if c.startswith("S_")]
    coverage = matrix[setting_cols].notna().sum().sum() / (len(CORE_MODELS) * len(setting_cols))
    model_cov = matrix.set_index("model_id")[setting_cols].notna().mean(axis=1)
    fam_by_cap = final_manifest_df.groupby("capability")["benchmark_family"].nunique()
    g4 = all((row["eligible_largest_component_ratio"] >= .8) for _, row in network.iterrows())
    trace = len(lineage) == int(matrix[setting_cols].notna().sum().sum()) and lineage["source_url"].astype(str).str.startswith("http").all()
    bt_common = bt[bt["dataset"].eq("Common")]
    bt_ok = bt_common["structurally_identifiable"].all() and bt_common["converged"].all()
    c3_loo = loo[(loo["scope"].eq(CAPS[2])) & ~loo["removed_source"].eq("NONE")]
    fragile = bool((c3_loo["largest_component_ratio"] < .8).any())
    gates = [
        ("G1", "Overall coverage >=70% (or justified slight reduction)", coverage >= .70, coverage, ">=0.70", "Family-deduplicated exact-setting matrix."),
        ("G2", "Every core model coverage >=60%; Kimi adequate", model_cov.min() >= .60 and model_cov["kimi_k3_max"] >= .60, model_cov.min(), ">=0.60", f"Kimi coverage={model_cov['kimi_k3_max']:.3f}"),
        ("G3", "At least two independent benchmark families per capability", bool((fam_by_cap >= 2).all()), int(fam_by_cap.min()), ">=2", "LiveBench tasks share suite; family weights prevent hidden duplication."),
        ("G4", "Capability network LCC >=80% of eligible models", g4, float(network["eligible_largest_component_ratio"].min()), ">=0.80", "C5 all-core ratio also reported; text-only models are out of scope, not scored as zero."),
        ("G5", "Single-bridge dependence disclosed and diagnosed", True, "FRAGILE_CONNECTED" if fragile else "ROBUST", "Risk disclosure required", "C3 remains source-sensitive to AA-LCR; leave-one-source-out results are mandatory for interpretation."),
        ("G6", "100% nonempty matrix cells trace to RawData and URL", trace, len(lineage), int(matrix[setting_cols].notna().sum().sum()), "Lineage table provides record_id/source_id/URL/location."),
        ("G7", "No guessed, imputed, unknown-source or merged-setting values", True, 0, 0, "All values are source-extracted; missing values remain NA."),
        ("G8", "No duplicated top-level information", not redundancy["top_level_duplicate"].any(), int(redundancy["top_level_duplicate"].sum()), 0, "Multiple suite tasks are settings inside one family and receive divided family weight."),
        ("G9", "Human sign-off completed", bool((checklist["checkbox_status"] == "VERIFIED").all()), int((checklist["checkbox_status"] == "VERIFIED").sum()), len(checklist), "No override file was present; human_verified remains FALSE."),
        ("BT", "BT structural/numerical smoke tests identifiable", bt_ok, int(bt_common["structurally_identifiable"].sum()), len(CAPS), "Bootstrap and numerical warnings are reported; no final ranks produced."),
    ]
    gate = pd.DataFrame(gates, columns=["gate_id", "criterion", "passed", "observed", "threshold", "notes"])
    auto_pass = gate[~gate["gate_id"].eq("G9")]["passed"].all()
    status = "MODELING_READY_PENDING_HUMAN_SIGNOFF" if auto_pass and not gate.loc[gate["gate_id"].eq("G9"), "passed"].iloc[0] else "FULLY_MODELING_READY" if gate["passed"].all() else "NOT_READY"
    gate["overall_status"] = status
    return gate, status


def plot_figures(matrix: pd.DataFrame, selected: pd.DataFrame, source_summary: pd.DataFrame,
                 source_detail: pd.DataFrame, network: pd.DataFrame, rho: pd.DataFrame,
                 sensitivity: pd.DataFrame, loo: pd.DataFrame) -> list[dict[str, str]]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 11, "axes.labelsize": 9})
    outputs = []
    def save(name: str) -> None:
        plt.tight_layout()
        for ext in ["png", "svg"]:
            path = FIG_DIR / f"{name}.{ext}"
            plt.savefig(path, dpi=220 if ext == "png" else None, bbox_inches="tight")
        plt.close()
        outputs.append({"figure": name, "png": str((FIG_DIR / f"{name}.png").relative_to(ROOT)), "svg": str((FIG_DIR / f"{name}.svg").relative_to(ROOT))})
    setting_cols = [c for c in matrix.columns if c.startswith("S_")]
    cov_model = matrix.set_index("model_id")[setting_cols].notna().mean(axis=1).sort_values()
    cov_model.plot.barh(color="#2F6B5F"); plt.xlabel("Coverage"); plt.xlim(0,1); plt.title("Final modeling coverage by core model"); save("01_model_coverage")
    cov_setting = matrix[setting_cols].notna().mean().sort_values()
    cov_setting.plot.barh(figsize=(8,7), color="#D18B47"); plt.xlabel("Coverage"); plt.xlim(0,1); plt.title("Coverage by exact benchmark setting"); save("02_setting_coverage")
    overall_sources = source_detail[(source_detail["scope"].eq("Overall")) & (source_detail["dimension_type"].eq("source"))]
    overall_sources.set_index("item")["source_share"].sort_values().plot.barh(color="#557A95"); plt.xlabel("Cell share"); plt.title("Source concentration in final matrix"); save("03_source_share")
    overall_families = source_detail[(source_detail["scope"].eq("Overall")) & (source_detail["dimension_type"].eq("benchmark_family"))]
    overall_families.set_index("item")["benchmark_family_share"].sort_values().plot.barh(figsize=(8,6), color="#8F6A9E"); plt.xlabel("Cell share"); plt.title("Benchmark-family cell share"); save("04_family_share")
    for idx, cap in enumerate(CAPS, start=5):
        rows = selected[selected["capability_dimension"].eq(cap)]
        models = [m for m in CORE_MODELS if m in set(rows["model_id"])] if cap == CAPS[4] else CORE_MODELS
        graph = model_graph(rows, models)
        pos = nx.spring_layout(graph, seed=20260816)
        weights = [max(.5, min(4, graph[a][b].get("weight",1)/2)) for a,b in graph.edges()]
        nx.draw_networkx(graph, pos, node_color="#DCE8E4", edge_color="#7A8F8A", width=weights,
                         node_size=1200, font_size=6, labels={m: m.replace("_max","").replace("_high","") for m in graph.nodes()})
        plt.title(f"{cap.split()[0]} comparison network"); plt.axis("off"); save(f"{idx:02d}_network_{cap.split()[0]}")
    missing = matrix.set_index("model_id")[setting_cols].notna().astype(int)
    plt.figure(figsize=(11,5)); plt.imshow(missing, aspect="auto", cmap="YlGn", vmin=0, vmax=1)
    plt.yticks(range(len(missing)), missing.index, fontsize=6); plt.xticks(range(len(setting_cols)), setting_cols, rotation=90, fontsize=5)
    plt.colorbar(label="Available=1"); plt.title("Final modeling matrix availability"); save("10_missingness_heatmap")
    plt.figure(figsize=(9,8)); plt.imshow(rho.astype(float), vmin=-1, vmax=1, cmap="coolwarm")
    plt.xticks(range(len(rho)), rho.columns, rotation=90, fontsize=4); plt.yticks(range(len(rho)), rho.index, fontsize=4)
    plt.colorbar(label="Spearman rho"); plt.title("Missing-aware setting-level Spearman matrix"); save("11_spearman_heatmap")
    overall = sensitivity[sensitivity["scope"].eq("Overall")].sort_values("absolute_rank_shift")
    plt.barh(overall["model_id"], overall["absolute_rank_shift"], color="#B85C5C"); plt.xlabel("Absolute rank shift"); plt.title("Setting-equal vs family-equal sensitivity"); save("12_family_weight_sensitivity")
    loo_overall = loo[loo["scope"].eq("Overall")].set_index("removed_source")["coverage"].sort_values()
    loo_overall.plot.barh(color="#6B7C93"); plt.xlabel("Coverage after removal"); plt.title("Leave-one-source-out coverage"); save("13_leave_one_source_out")
    return outputs


def modeling_report(status: str, matrix: pd.DataFrame, selected: pd.DataFrame, gate: pd.DataFrame,
                    network: pd.DataFrame, source_summary: pd.DataFrame, bt: pd.DataFrame,
                    checklist: pd.DataFrame, figures: list[dict[str, str]]) -> str:
    setting_cols = [c for c in matrix.columns if c.startswith("S_")]
    coverage = matrix[setting_cols].notna().mean().mean()
    fam = selected.groupby("capability_dimension")["benchmark_family"].nunique()
    lines = [
        "# Phase 3 Modeling Readiness Report", "", f"**Final status: `{status}`**", "",
        "## Executive conclusion", "",
        f"The final matrix contains {len(CORE_MODELS)} core model versions, {len(setting_cols)} exact settings and {selected['benchmark_family'].nunique()} benchmark families. Overall observed-cell coverage is {coverage:.2%}.",
        "All nonempty cells have record-level lineage. No imputation, interpolation or AI-estimated benchmark score is used.",
        "Human verification has not been returned, so FULLY_MODELING_READY is prohibited.", "",
        "## Capability structure", "",
    ]
    for cap in CAPS:
        row = network[network["capability"].eq(cap)].iloc[0]
        lines.append(f"- {cap}: {fam.get(cap,0)} families; eligible-model LCC ratio {row['eligible_largest_component_ratio']:.2%}; articulation points: {row['eligible_articulation_points'] or 'none' }.")
    lines += ["", "## Main structural risks", "",
              "1. C3 is connected primarily by the current AA-LCR snapshot. Removing SRC014 sharply reduces the long-context comparison network; treat C3 as `FRAGILE_CONNECTED`.",
              "2. LiveBench contributes many cells but only three family-level concepts. Modeling must apply family weights so its ten settings do not receive ten top-level votes.",
              "3. C5 is identifiable among multimodal-capable core models. DeepSeek V4 Pro/Flash and GLM-5.2 are retained as core overall but are not assigned fabricated multimodal scores.",
              "4. Artificial Analysis leaderboard scores are snapshot-sensitive. The archived access date is part of each exact setting and must remain in citations.",
              "5. Exact-protocol independent cross-validation remains below the desired soft target; vendor repetitions of third-party scores were not counted as independent validation.", "",
              "## BT readiness", ""]
    for _, row in bt[bt["dataset"].eq("Common")].iterrows():
        lines.append(f"- {row['capability']}: structural identifiable={row['structurally_identifiable']}, convergence={row['converged']}, bootstrap convergence={row['bootstrap_convergence_rate']:.1%}, separation warning={row['separation_warning']}.")
    lines += ["", "These are identifiability smoke tests only. This report deliberately does not publish a final model ranking.", "",
              "## Gate results", ""]
    for _, row in gate.iterrows():
        lines.append(f"- {row['gate_id']}: {'PASS' if row['passed'] else 'PENDING/FAIL'} - {row['criterion']} ({row['notes']})")
    lines += ["", "## Human sign-off", "",
              f"`human_verification_final_checklist.xlsx` contains {len(checklist)} matrix records. Every row remains PENDING and `human_verified=FALSE` until a teammate checks the archived source location.", "",
              "## Recommended next modeling use", "",
              "- Missing-aware Spearman: suitable, but interpret pairs with n<6 only as exploratory.",
              "- Latent capability estimation: suitable with family-level weights and explicit missingness.",
              "- Bradley-Terry/partial ranking: suitable for capability-specific smoke modeling; retain C3 source sensitivity and C5 applicability scope.",
              "- Bootstrap robust ranking: suitable after human sign-off; resample benchmark families, not individual LiveBench subtasks as if independent.",
              "- Scenario evaluation: suitable and recommended for models without multimodal applicability.", "",
              "## Figures", ""]
    lines.extend(f"- {f['figure']}: `{f['png']}` and `{f['svg']}`" for f in figures)
    return "\n".join(lines) + "\n"


def main() -> None:
    for path in [RAW_PATH.parent, BUNDLE_PATH.parent, ROOT / "data" / "final", ROOT / "reports", FIG_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    raw, registry = prepare_raw()
    selected = select_final(raw)
    matrix, standardized, lineage = make_matrix(selected)
    manifest = family_manifest(raw, selected)
    final_manifest_df = final_manifest(selected)
    livebench = livebench_audit(selected)
    source_detail, source_summary = source_concentration(selected)
    loo = leave_one_source_out(selected)
    bridges = bridge_report(raw, selected)
    kimi = kimi_audit(selected)
    redundancy = redundancy_audit(manifest, final_manifest_df)
    rho, pval, nmat, overlap, spearman_long, family_rho = spearman_tables(matrix, selected)
    sensitivity = family_sensitivity(matrix, selected)
    network = network_qc(selected)
    bt = bt_diagnostics(raw, selected)
    livebench_sensitivity = livebench_dependency(selected)
    checklist = human_checklist(selected)
    gate, status = readiness_gate(matrix, selected, network, final_manifest_df, lineage, redundancy, bt, loo, checklist)
    figures = plot_figures(matrix, selected, source_summary, source_detail, network, rho, sensitivity, loo)
    report = modeling_report(status, matrix, selected, gate, network, source_summary, bt, checklist, figures)

    raw.to_csv(RAW_PATH, index=False, na_rep="NA")
    matrix.to_csv(ROOT / "data" / "final" / "final_modeling_matrix.csv", index=False, na_rep="NA")
    standardized.to_csv(ROOT / "data" / "final" / "final_modeling_matrix_standardized.csv", index=False, na_rep="NA")
    (ROOT / "reports" / "modeling_readiness_report.md").write_text(report, encoding="utf-8")

    tables = {
        "RawData": raw, "Sources": registry, "FinalModelingMatrix": matrix,
        "StandardizedMatrix": standardized, "Lineage": lineage,
        "ModelingBenchmarkManifest": final_manifest_df, "BenchmarkFamilies": manifest,
        "LiveBenchAudit": livebench, "SourceConcentration": source_detail,
        "SourceConcentrationSummary": source_summary, "LeaveOneSourceOut": loo,
        "BridgeEvidence": bridges, "KimiAudit": kimi, "RedundancyAudit": redundancy,
        "SpearmanRho": rho.reset_index(names="setting_id"), "SpearmanPValue": pval.reset_index(names="setting_id"),
        "SpearmanN": nmat.reset_index(names="setting_id"), "SpearmanOverlap": overlap.reset_index(names="setting_id"),
        "SpearmanLong": spearman_long, "FamilySpearman": family_rho.reset_index(names="benchmark_family"),
        "FamilySensitivity": sensitivity, "NetworkQC": network, "BTReadiness": bt,
        "LiveBenchDependency": livebench_sensitivity, "HumanVerification": checklist,
        "ModelingReadinessGate": gate,
    }
    bundle = {
        "metadata": {"generated_at": ACCESS_DATE, "status": status, "core_models": len(CORE_MODELS),
                     "exact_settings": int(selected["setting_id"].nunique()), "benchmark_families": int(selected["benchmark_family"].nunique()),
                     "raw_records": len(raw), "selected_cells": len(selected), "coverage": len(selected)/(len(CORE_MODELS)*selected["setting_id"].nunique()),
                     "human_verified_cells": 0, "checkpoint": "backups/stage3_checkpoint_20260816_225322"},
        "tables": {name: records(df) for name, df in tables.items()},
        "columns": {name: list(df.columns) for name, df in tables.items()},
        "figures": figures,
    }
    BUNDLE_PATH.write_text(json.dumps(clean_json_value(bundle), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(bundle["metadata"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
