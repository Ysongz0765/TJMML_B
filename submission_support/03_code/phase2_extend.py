from __future__ import annotations

import json
import math
import re
from itertools import combinations
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from scipy.stats import spearmanr

from build_dataset import ROOT, benchmark_key, conflict_check, core_selection, make_dataframes, matrix_and_standardized, select_records


DATA_FREEZE_DATE = "2026-08-16"
PHASE1_OVERALL_COVERAGE = 0.3615384615384615

OUT_PROCESSED = ROOT / "data" / "processed"
OUT_FINAL = ROOT / "data" / "final"
OUT_RAW = ROOT / "data" / "raw"
FIG_DIR = ROOT / "reports" / "figures"


COMMON_MODEL_IDS = [
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


LIVEBENCH_MODEL_MAP = {
    "kimi_k3_max": "kimi-k3",
    "gpt_5_6_sol_max": "gpt-5.6-sol-max",
    "gpt_5_5_xhigh": "gpt-5.5-xhigh",
    "claude_fable_5_max": "claude-fable-5-max-effort",
    "claude_opus_4_8_max": "claude-opus-4-8-max-effort",
    "gemini_3_1_pro_high": "gemini-3.1-pro-preview-high",
    "deepseek_v4_pro_max": "deepseek-v4-pro",
    "deepseek_v4_flash_max": "deepseek-v4-flash",
    "qwen3_8_max": "qwen3.8-max",
    "glm_5_2_max": "glm-5.2",
}

LIVEBENCH_TASKS = {
    "AMPS_Hard": ("C1 Complex reasoning", "Math", "Advanced math problem-solving task score."),
    "math_comp": ("C1 Complex reasoning", "Math", "Competition math task score."),
    "olympiad": ("C1 Complex reasoning", "Math", "Olympiad-style math task score."),
    "zebra_puzzle": ("C1 Complex reasoning", "Logic", "Logic grid puzzle task score."),
    "logic_with_navigation": ("C1 Complex reasoning", "Logic", "Logic and navigation task score."),
    "code_generation": ("C4 Code and software engineering", "Coding", "LiveBench code generation task score."),
    "code_completion": ("C4 Code and software engineering", "Coding", "LiveBench code completion task score."),
    "python": ("C4 Code and software engineering", "Coding", "LiveBench Python task score."),
    "javascript": ("C4 Code and software engineering", "Coding", "LiveBench JavaScript task score."),
    "typescript": ("C4 Code and software engineering", "Coding", "LiveBench TypeScript task score."),
}

OPENROUTER_GPQA_MAP = {
    "kimi_k3_max": "MoonshotAI: Kimi K3",
    "gpt_5_5_xhigh": "OpenAI: GPT-5.5",
    "claude_fable_5_max": "Anthropic: Claude Fable 5",
    "claude_opus_4_8_max": "Anthropic: Claude Opus 4.8",
    "gemini_3_1_pro_high": "Google: Gemini 3.1 Pro Preview",
    "deepseek_v4_pro_max": "DeepSeek: DeepSeek V4 Pro 0813",
    "deepseek_v4_flash_max": "DeepSeek: DeepSeek V4 Flash 0731",
    "glm_5_2_max": "Z.ai: GLM 5.2",
}

COMMON_EXTRA_VENDOR_KEYS = {
    "HLE-Full [Full; Pass@1; tools=No]",
    "MMMU-Pro [Reported; Accuracy; tools=No]",
    "MathVision [Reported; Accuracy; tools=No]",
    "MRCR 1M [1M; MMR; tools=No]",
    "CorpusQA 1M [1M; ACC; tools=No]",
    "ProgramBench [Reported; Accuracy; tools=Agentharness]",
    "FrontierSWE [Reported; Dominance score; tools=Agentharness]",
    "SWE Verified [Verified; Resolved; tools=Agent_tools]",
}


def ensure_dirs() -> None:
    for d in [OUT_PROCESSED, OUT_FINAL, OUT_RAW, FIG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def source_rows_phase2() -> list[dict[str, Any]]:
    return [
        dict(
            source_id="SRC006",
            publisher="LiveBench",
            source_title="LiveBench official table release 2026-06-25",
            source_type="Independent unified benchmark platform / official CSV",
            url="https://livebench.ai/table_2026_06_25.csv",
            publication_date="2026-06-25",
            access_date=DATA_FREEZE_DATE,
            authority_level="A",
            evidence_role="COMMON_EVAL",
            benchmark_related="LiveBench objective tasks: math, reasoning, coding, data analysis, language",
            models_covered="Kimi K3; GPT-5.6 Sol; GPT-5.5; Claude Fable 5; Claude Opus 4.8; Gemini 3.1 Pro; DeepSeek V4; Qwen3.8 Max; GLM-5.2",
            local_archive_path="sources/structured/SRC006_livebench_table_2026_06_25.csv",
            notes="Official release CSV mirrored by LiveBench; individual task columns used, not a composite overall index.",
        ),
        dict(
            source_id="SRC007",
            publisher="OpenRouter",
            source_title="OpenRouter GPQA Diamond benchmark page",
            source_type="Independent unified endpoint benchmark page",
            url="https://openrouter.ai/benchmarks/gpqa-diamond",
            publication_date="2026-08-15",
            access_date=DATA_FREEZE_DATE,
            authority_level="C",
            evidence_role="COMMON_EVAL",
            benchmark_related="GPQA Diamond",
            models_covered="Kimi K3; GPT-5.5; Claude Fable 5; Claude Opus 4.8; Gemini 3.1 Pro; DeepSeek V4; GLM-5.2",
            local_archive_path="sources/html/SRC007_openrouter_gpqa_diamond.html",
            notes="Platform states it runs the same fixed question set across provider endpoints; GPT-5.6 Sol Pro was not mapped to GPT-5.6 Sol max because version names differ.",
        ),
        dict(
            source_id="SRC008",
            publisher="BenchLM",
            source_title="BenchLM LiveBench mirror page",
            source_type="Mirror / supplementary structured page",
            url="https://benchlm.ai/benchmarks/livebench",
            publication_date="2026-06-25",
            access_date=DATA_FREEZE_DATE,
            authority_level="C",
            evidence_role="SUPPLEMENTARY",
            benchmark_related="LiveBench metadata and mirror",
            models_covered="43 model variants in mirrored LiveBench snapshot",
            local_archive_path="sources/html/SRC008_benchlm_livebench_mirror.html",
            notes="Used for metadata and source triangulation only; official LiveBench CSV is the primary numeric source.",
        ),
        dict(
            source_id="SRC009",
            publisher="Artificial Analysis",
            source_title="Kimi K3 achieves #3 in the Artificial Analysis Intelligence Index",
            source_type="Independent third-party composite evaluation article",
            url="https://artificialanalysis.ai/articles/kimi-k3-achieves-3-in-the-artificial-analysis-intelligence-index-comparable-to-opus-4-8-and-gpt-5-5",
            publication_date="2026-07-23",
            access_date=DATA_FREEZE_DATE,
            authority_level="C",
            evidence_role="EXTERNAL_VALIDATION",
            benchmark_related="Artificial Analysis Intelligence Index and component references",
            models_covered="Kimi K3; Claude Opus 4.8; GPT-5.5; other frontier models",
            local_archive_path="sources/html/SRC009_artificial_analysis_kimi_k3.html",
            notes="Composite index source registered for validation only; no composite score inserted into Common Matrix to avoid double counting.",
        ),
    ]


def normalize_sources(sources: pd.DataFrame) -> pd.DataFrame:
    out = sources.copy()
    if "evidence_role" not in out.columns:
        out["evidence_role"] = "VENDOR_REPORT"
    out.loc[out["source_id"].eq("SRC005"), "evidence_role"] = "SUPPLEMENTARY"
    add = pd.DataFrame(source_rows_phase2())
    return pd.concat([out, add], ignore_index=True).drop_duplicates("source_id", keep="last")


def normalize_models(models: pd.DataFrame) -> pd.DataFrame:
    out = models.copy()
    out.loc[out["model_id"].eq("qwen3_8_max"), "inclusion_status"] = "Extended"
    return out


def next_record_number(raw: pd.DataFrame) -> int:
    nums = raw["record_id"].astype(str).str.extract(r"R(\d+)")[0].dropna().astype(int)
    return int(nums.max()) + 1 if not nums.empty else 1


def base_record(
    record_id: str,
    model: pd.Series,
    source: pd.Series,
    capability: str,
    benchmark: str,
    version: str,
    year: str,
    metric: str,
    definition: str,
    score: float,
    tools: str,
    reasoning: str,
    protocol: str,
    table: str,
    page: str,
    evidence_role: str,
    source_level: str,
    comparable: str = "Grade A",
    notes: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model_id = model["model_id"] if "model_id" in model.index else model.name
    source_id = source["source_id"] if "source_id" in source.index else source.name
    row = {
        "record_id": record_id,
        "model_id": model_id,
        "model_family": model["model_family"],
        "model_full_name": model["model_full_name"],
        "organization": model["organization"],
        "capability_dimension": capability,
        "benchmark_name": benchmark,
        "benchmark_version": version,
        "benchmark_year": year,
        "metric_name": metric,
        "metric_definition": definition,
        "raw_score": round(float(score), 6),
        "raw_unit": "%",
        "higher_is_better": True,
        "tools_allowed": tools,
        "browsing_allowed": "No",
        "reasoning_setting": reasoning,
        "pass_k_setting": "pass@1" if "GPQA" in benchmark else "NA",
        "prompting_setting": "Platform default",
        "test_protocol": protocol,
        "additional_setting": "",
        "source_id": source_id,
        "source_type": source["source_type"],
        "publisher": source["publisher"],
        "source_title": source["source_title"],
        "source_url": source["url"],
        "publication_date": source["publication_date"],
        "access_date": source["access_date"],
        "page_number": page,
        "table_number": table,
        "extraction_method": "machine_extracted_from_archived_structured_source",
        "source_authority_level": source_level,
        "protocol_match": "High",
        "version_match": "High",
        "comparable": comparable,
        "verified": "FALSE",
        "machine_extracted": "TRUE",
        "human_verified": "FALSE",
        "cross_source_verified": "FALSE",
        "conflict_flag": 0,
        "exclusion_reason": "",
        "notes": notes,
        "evidence_role": evidence_role,
        "is_composite_index": False,
        "component_benchmarks": "",
        "leaderboard_date": source["publication_date"],
        "model_version_reported_by_source": "",
        "selected_for_common_matrix": False,
        "selected_reason": "",
    }
    if extra:
        row.update(extra)
    return row


def parse_openrouter_accuracy(html: str, model_name: str) -> dict[str, Any] | None:
    idx = html.find(f'\\"modelName\\":\\"{model_name}\\"')
    if idx < 0:
        return None
    chunk = html[idx: idx + 2500]
    accuracy = re.search(r'\\"accuracy\\":([0-9.]+)', chunk)
    std = re.search(r'\\"accuracyStdDev\\":(null|[0-9.]+)', chunk)
    runs = re.search(r'\\"runCount\\":([0-9]+)', chunk)
    tasks = re.search(r'\\"totalTasks\\":([0-9]+)', chunk)
    permaslug = re.search(r'\\"modelPermaslug\\":\\"([^"]+)\\"', chunk)
    if not accuracy:
        return None
    return {
        "accuracy_pct": float(accuracy.group(1)) * 100,
        "accuracy_stddev": None if not std or std.group(1) == "null" else float(std.group(1)) * 100,
        "run_count": int(runs.group(1)) if runs else None,
        "total_tasks": int(tasks.group(1)) if tasks else None,
        "source_model_id": permaslug.group(1) if permaslug else "",
    }


def augment_raw(dfs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = normalize_models(dfs["Models"])
    sources = normalize_sources(dfs["Sources"])
    raw = dfs["RawData"].copy()
    if "evidence_role" not in raw.columns:
        raw["evidence_role"] = "VENDOR_REPORT"
    for col, default in [
        ("is_composite_index", False),
        ("component_benchmarks", ""),
        ("leaderboard_date", ""),
        ("model_version_reported_by_source", ""),
        ("selected_for_common_matrix", False),
        ("selected_reason", ""),
    ]:
        if col not in raw.columns:
            raw[col] = default

    model_by_id = models.set_index("model_id")
    source_by_id = sources.set_index("source_id")
    records = []
    rec_no = next_record_number(raw)

    lb = pd.read_csv(ROOT / "sources" / "structured" / "SRC006_livebench_table_2026_06_25.csv")
    lb = lb.set_index("model")
    for model_id, source_model in LIVEBENCH_MODEL_MAP.items():
        if source_model not in lb.index:
            continue
        for task, (cap, category, definition) in LIVEBENCH_TASKS.items():
            score = lb.loc[source_model, task]
            records.append(base_record(
                f"R{rec_no:04d}",
                model_by_id.loc[model_id],
                source_by_id.loc["SRC006"],
                cap,
                f"LiveBench {task}",
                "2026-06-25",
                "2026",
                "Task score",
                definition,
                score,
                "No",
                "Source-reported effort",
                "LiveBench 2026-06-25 official release CSV; objective task-level score.",
                "Official CSV",
                f"column={task}; row={source_model}",
                "COMMON_EVAL",
                "A",
                extra={
                    "leaderboard_date": "2026-06-25",
                    "model_version_reported_by_source": source_model,
                    "component_benchmarks": category,
                },
            ))
            rec_no += 1

    html = (ROOT / "sources" / "html" / "SRC007_openrouter_gpqa_diamond.html").read_text(encoding="utf-8")
    for model_id, source_name in OPENROUTER_GPQA_MAP.items():
        parsed = parse_openrouter_accuracy(html, source_name)
        if not parsed:
            continue
        notes = f"OpenRouter source model: {parsed['source_model_id']}; run_count={parsed['run_count']}; total_tasks={parsed['total_tasks']}; stddev_pp={parsed['accuracy_stddev']}"
        records.append(base_record(
            f"R{rec_no:04d}",
            model_by_id.loc[model_id],
            source_by_id.loc["SRC007"],
            "C1 Complex reasoning",
            "GPQA Diamond",
            "Diamond / OpenRouter fixed set",
            "2026",
            "Accuracy",
            "OpenRouter GPQA Diamond accuracy across provider endpoint runs.",
            parsed["accuracy_pct"],
            "No",
            "Source default / provider endpoint",
            "OpenRouter GPQA Diamond page; same fixed question set across provider endpoints.",
            "Embedded leaderboard",
            f"modelName={source_name}",
            "COMMON_EVAL",
            "C",
            comparable="Grade B",
            notes=notes,
            extra={
                "leaderboard_date": "2026-08-15",
                "model_version_reported_by_source": parsed["source_model_id"],
            },
        ))
        rec_no += 1

    augmented = pd.concat([raw, pd.DataFrame(records)], ignore_index=True)
    augmented = augmented.drop_duplicates(
        ["model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed", "source_id"],
        keep="last",
    )
    return models, sources, augmented


def matrix_key(row: pd.Series) -> str:
    tool = str(row["tools_allowed"]).replace("/", "_").replace(" ", "")
    return f"{row['benchmark_name']} [{row['benchmark_version']}; {row['metric_name']}; tools={tool}]"


def benchmark_setting_audit(raw: pd.DataFrame, phase1_matrix: pd.DataFrame) -> pd.DataFrame:
    score_cols = [c for c in phase1_matrix.columns if c not in {"model_id", "model", "organization"}]
    raw = raw.copy()
    raw["matrix_column"] = raw.apply(matrix_key, axis=1)
    rows = []
    for col in score_cols:
        g = raw[raw["matrix_column"].eq(col)]
        if g.empty:
            rows.append(dict(matrix_column=col, benchmark_name="UNRESOLVED", exact_version="UNRESOLVED", year="UNRESOLVED", metric="UNRESOLVED", tools_setting="UNRESOLVED", reasoning_setting="mixed/unknown", harness="UNRESOLVED", source_protocol="UNRESOLVED", should_be_separate="TRUE", reason="Matrix column not found in RawData."))
            continue
        rows.append(dict(
            matrix_column=col,
            benchmark_name="; ".join(sorted(g["benchmark_name"].dropna().astype(str).unique())),
            exact_version="; ".join(sorted(g["benchmark_version"].dropna().astype(str).unique())),
            year="; ".join(sorted(g["benchmark_year"].dropna().astype(str).unique())),
            metric="; ".join(sorted(g["metric_name"].dropna().astype(str).unique())),
            tools_setting="; ".join(sorted(g["tools_allowed"].dropna().astype(str).unique())),
            reasoning_setting="; ".join(sorted(g["reasoning_setting"].dropna().astype(str).unique())),
            harness="; ".join(sorted(g["additional_setting"].fillna("").astype(str).unique())) or "NA",
            source_protocol="; ".join(sorted(g["test_protocol"].dropna().astype(str).unique()))[:500],
            should_be_separate="TRUE",
            reason="Version/metric/tools are encoded in the column. The apparent 13-vs-12 mismatch comes from MMLU-Pro being represented as separate Accuracy and EM settings; these should remain separate until metric equivalence is manually verified." if col.startswith("MMLU-Pro") else "Column is a distinct benchmark setting and should not be merged with other versions/metrics/tools settings.",
        ))
    return pd.DataFrame(rows)


def build_common_matrix(raw: pd.DataFrame, models: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = raw.copy()
    raw["matrix_key"] = raw.apply(matrix_key, axis=1)
    livebench_keys = set(raw.loc[raw["source_id"].eq("SRC006"), "matrix_key"].unique())
    openrouter_key = "GPQA Diamond [Diamond / OpenRouter fixed set; Accuracy; tools=No]"
    common_keys = sorted(livebench_keys) + [openrouter_key] + sorted(COMMON_EXTRA_VENDOR_KEYS)
    pool = raw[
        raw["model_id"].isin(COMMON_MODEL_IDS)
        & raw["matrix_key"].isin(common_keys)
        & raw["comparable"].isin(["Grade A", "Grade B"])
    ].copy()
    role_rank = {"COMMON_EVAL": 5, "BENCHMARK_OFFICIAL": 4, "VENDOR_REPORT": 3, "EXTERNAL_VALIDATION": 2, "SUPPLEMENTARY": 1}
    level_rank = {"A": 5, "B": 4, "C": 3, "D": 1}
    pool["_role_rank"] = pool["evidence_role"].map(role_rank).fillna(0)
    pool["_level_rank"] = pool["source_authority_level"].map(level_rank).fillna(0)
    pool = pool.sort_values(["model_id", "matrix_key", "_role_rank", "_level_rank", "record_id"], ascending=[True, True, False, False, True])
    selected = pool.drop_duplicates(["model_id", "matrix_key"], keep="first").copy()
    selected["selected_for_common_matrix"] = True
    selected["selected_reason"] = selected.apply(
        lambda r: "Selected by source priority: COMMON_EVAL > BENCHMARK_OFFICIAL > VENDOR_REPORT; exact setting retained." if r["evidence_role"] == "COMMON_EVAL" else "Selected as best available traceable vendor/official evidence for sparse capability dimension.",
        axis=1,
    )
    core_models = models.set_index("model_id").loc[COMMON_MODEL_IDS].reset_index()[["model_id", "model_full_name", "organization"]]
    mat = selected.pivot_table(index="model_id", columns="matrix_key", values="raw_score", aggfunc="first")
    out = core_models.set_index("model_id").join(mat, how="left").reset_index().rename(columns={"model_full_name": "model"})
    return out, selected.drop(columns=["_role_rank", "_level_rank"])


def extended_matrix(raw: pd.DataFrame, models: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    raw["matrix_key"] = raw.apply(matrix_key, axis=1)
    pool = raw[raw["comparable"].isin(["Grade A", "Grade B", "Grade C"])].copy()
    selected = pool.sort_values(["model_id", "matrix_key", "comparable", "record_id"]).drop_duplicates(["model_id", "matrix_key"], keep="first")
    all_models = models[["model_id", "model_full_name", "organization"]].copy()
    mat = selected.pivot_table(index="model_id", columns="matrix_key", values="raw_score", aggfunc="first")
    return all_models.set_index("model_id").join(mat, how="left").reset_index().rename(columns={"model_full_name": "model"})


def coverage_tables(matrix: pd.DataFrame, raw_selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    total_models = len(matrix)
    bench_rows = []
    for c in score_cols:
        n = int(matrix[c].notna().sum())
        g = raw_selected[raw_selected["matrix_key"].eq(c)]
        bench_rows.append(dict(
            benchmark=c,
            capability=g["capability_dimension"].mode().iat[0] if not g.empty else "Unknown",
            n_models_total=total_models,
            n_available=n,
            coverage_rate=n / total_models if total_models else 0,
            source_quality=g["source_authority_level"].mode().iat[0] if not g.empty else "Unknown",
            evidence_role=g["evidence_role"].mode().iat[0] if not g.empty else "Unknown",
            recommend_keep="TRUE" if n / total_models >= 0.6 else "REVIEW",
            reason="Meets 60% benchmark coverage target." if n / total_models >= 0.6 else "Retained only if capability-critical or bridge value is high.",
        ))
    model_rows = []
    for _, r in matrix.iterrows():
        n = int(r[score_cols].notna().sum())
        caps = set(raw_selected[raw_selected["model_id"].eq(r["model_id"])]["capability_dimension"].dropna())
        model_rows.append(dict(
            model_id=r["model_id"],
            model=r["model"],
            n_available=n,
            n_benchmarks=len(score_cols),
            coverage_rate=n / len(score_cols) if score_cols else 0,
            number_of_capabilities_covered=len(caps),
        ))
    metrics = {
        "overall_coverage": float(matrix[score_cols].notna().mean().mean()),
        "min_model_coverage": min((r["coverage_rate"] for r in model_rows), default=0),
        "median_model_coverage": float(pd.Series([r["coverage_rate"] for r in model_rows]).median()) if model_rows else 0,
        "min_benchmark_coverage": min((r["coverage_rate"] for r in bench_rows), default=0),
        "median_benchmark_coverage": float(pd.Series([r["coverage_rate"] for r in bench_rows]).median()) if bench_rows else 0,
    }
    return pd.DataFrame(bench_rows), pd.DataFrame(model_rows), metrics


def capability_map_for_common(selected: pd.DataFrame) -> dict[str, str]:
    return selected.drop_duplicates("matrix_key").set_index("matrix_key")["capability_dimension"].to_dict()


def pairwise_networks(matrix: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, nx.Graph]]:
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    capmap = capability_map_for_common(selected)
    rows = []
    graphs = {}
    for cap in sorted(set(capmap.values())):
        cols = [c for c in score_cols if capmap.get(c) == cap]
        g = nx.Graph()
        for _, m in matrix.iterrows():
            g.add_node(m["model"], model_id=m["model_id"])
        pair_counts = {}
        for _, a in matrix.iterrows():
            for _, b in matrix.iterrows():
                if a["model_id"] >= b["model_id"]:
                    continue
                common = [c for c in cols if pd.notna(a[c]) and pd.notna(b[c])]
                if common:
                    g.add_edge(a["model"], b["model"], weight=len(common), common_benchmarks="; ".join(common))
                    pair_counts[f"{a['model']} || {b['model']}"] = len(common)
        comps = [sorted(c) for c in nx.connected_components(g)]
        rows.append(dict(
            capability=cap,
            connected_components=len(comps),
            component_members=json.dumps(comps, ensure_ascii=False),
            isolated_models="; ".join(sorted([n for n, d in g.degree() if d == 0])),
            model_degree=json.dumps(dict(g.degree()), ensure_ascii=False),
            common_benchmark_count_by_pair=json.dumps(pair_counts, ensure_ascii=False),
            graph_density=nx.density(g),
            connectivity_status="CONNECTED" if len(comps) == 1 else "DISCONNECTED",
        ))
        graphs[cap] = g
    return pd.DataFrame(rows), graphs


def bipartite_networks(matrix: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, nx.Graph]]:
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    capmap = capability_map_for_common(selected)
    rows = []
    graphs = {}
    for cap in sorted(set(capmap.values())):
        cols = [c for c in score_cols if capmap.get(c) == cap]
        g = nx.Graph()
        for c in cols:
            g.add_node(c, node_type="benchmark")
        for _, m in matrix.iterrows():
            g.add_node(m["model"], node_type="model")
            for c in cols:
                if pd.notna(m[c]):
                    g.add_edge(m["model"], c)
        comps = [sorted(c) for c in nx.connected_components(g)]
        arts = list(nx.articulation_points(g))
        rows.append(dict(
            capability=cap,
            number_of_components=len(comps),
            largest_component_size=max((len(c) for c in comps), default=0),
            isolated_models="; ".join(sorted([n for n in matrix["model"] if g.degree(n) == 0])),
            model_degree=json.dumps({n: int(g.degree(n)) for n in matrix["model"]}, ensure_ascii=False),
            benchmark_degree=json.dumps({c: int(g.degree(c)) for c in cols}, ensure_ascii=False),
            articulation_points="; ".join(arts),
            bridge_models="; ".join([a for a in arts if a in set(matrix["model"])]),
            bridge_benchmarks="; ".join([a for a in arts if a in set(cols)]),
            component_members=json.dumps(comps, ensure_ascii=False),
        ))
        graphs[cap] = g
    return pd.DataFrame(rows), graphs


def model_pool_review(models: pd.DataFrame, common_matrix: pd.DataFrame, selected: pd.DataFrame, pairwise_diag: pd.DataFrame) -> pd.DataFrame:
    bench_cols = [c for c in common_matrix.columns if c not in {"model_id", "model", "organization"}]
    degree_total = {}
    for _, row in pairwise_diag.iterrows():
        d = json.loads(row["model_degree"])
        for k, v in d.items():
            degree_total[k] = degree_total.get(k, 0) + v
    rows = []
    for _, m in models.iterrows():
        if m["model_id"] in set(common_matrix["model_id"]):
            cm_row = common_matrix[common_matrix["model_id"].eq(m["model_id"])].iloc[0]
            cov = float(cm_row[bench_cols].notna().mean()) if bench_cols else 0
            caps = set(selected[selected["model_id"].eq(m["model_id"])]["capability_dimension"].dropna())
            deg = degree_total.get(cm_row["model"], 0)
        else:
            cov = 0.0
            caps = set()
            deg = 0
        if m["model_id"] == "qwen3_235b_a22b_base":
            rec = "BRIDGE_MODEL"
            relevance = "Useful bridge/technical-report evidence but not the best current Qwen flagship representative for 2026 user-facing evaluation."
        elif m["model_id"] == "qwen3_8_max":
            rec = "CORE_MODEL"
            relevance = "Current Qwen flagship candidate with unified LiveBench evidence; source needs manual identity verification."
        elif m["model_id"] in COMMON_MODEL_IDS:
            rec = "CORE_MODEL" if cov >= 0.5 else "BRIDGE_MODEL"
            relevance = "Representative frontier model with usable Common Matrix coverage."
        else:
            rec = "EXTENDED_MODEL"
            relevance = "Important candidate or comparator but not retained in the Common Matrix."
        rows.append(dict(
            model_id=m["model_id"],
            model_full_name=m["model_full_name"],
            current_relevance=relevance,
            release_recency=m.get("release_date", "Unknown"),
            benchmark_coverage="See ExtendedMatrix",
            common_matrix_coverage=round(cov, 4),
            number_of_capabilities_covered=len(caps),
            graph_degree=deg,
            bridge_value="High" if deg > 0 and cov < 0.7 else "Medium" if deg > 0 else "Low",
            source_quality="Mixed A/B/C; see selected records",
            final_user_recommendation_relevance=rec,
        ))
    return pd.DataFrame(rows)


def cross_validation_report(selected: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, s in selected.iterrows():
        key_cols = ["model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed"]
        g = raw
        for c in key_cols:
            g = g[g[c].eq(s[c])]
        independent_sources = g["source_id"].nunique()
        same_score = g["raw_score"].astype(str).nunique() == 1
        rows.append(dict(
            selected_record=s["record_id"],
            model=s["model_full_name"],
            benchmark=s["matrix_key"],
            single_source_records=1 if independent_sources == 1 else 0,
            multi_source_records=1 if independent_sources >= 2 else 0,
            agreement_records=1 if independent_sources >= 2 and same_score else 0,
            disagreement_records=1 if independent_sources >= 2 and not same_score else 0,
            independent_source_count=independent_sources,
            sources="; ".join(sorted(g["source_id"].astype(str).unique())),
        ))
    out = pd.DataFrame(rows)
    summary = pd.DataFrame([dict(
        selected_record="SUMMARY",
        model="ALL",
        benchmark="ALL",
        single_source_records=int(out["single_source_records"].sum()) if not out.empty else 0,
        multi_source_records=int(out["multi_source_records"].sum()) if not out.empty else 0,
        agreement_records=int(out["agreement_records"].sum()) if not out.empty else 0,
        disagreement_records=int(out["disagreement_records"].sum()) if not out.empty else 0,
        independent_source_count="NA",
        sources=f"cross_validation_rate={out['multi_source_records'].mean() if not out.empty else 0:.4f}",
    )])
    return pd.concat([summary, out], ignore_index=True)


def human_verification_priority(selected: pd.DataFrame, raw: pd.DataFrame, bip_diag: pd.DataFrame) -> pd.DataFrame:
    bridge_benchmarks = set()
    for s in bip_diag["bridge_benchmarks"].fillna(""):
        bridge_benchmarks.update([x.strip() for x in s.split(";") if x.strip()])
    rows = []
    for _, r in selected.iterrows():
        pri = 1
        why = "Common Matrix final adopted non-empty cell."
        if r["matrix_key"] in bridge_benchmarks:
            pri = 2
            why += " It is also a graph bridge benchmark."
        rows.append(dict(
            priority=pri,
            model=r["model_full_name"],
            benchmark=r["matrix_key"],
            score=r["raw_score"],
            source_url=r["source_url"],
            page_table=f"{r['page_number']} / {r['table_number']}",
            exact_setting=f"{r['benchmark_version']} | {r['metric_name']} | tools={r['tools_allowed']} | reasoning={r['reasoning_setting']}",
            why_important=why,
        ))
    extended = raw[~raw["record_id"].isin(set(selected["record_id"])) & raw["comparable"].isin(["Grade A", "Grade B", "Grade C"])].head(50)
    for _, r in extended.iterrows():
        rows.append(dict(
            priority=3 if r["comparable"] == "Grade B" else 4,
            model=r["model_full_name"],
            benchmark=matrix_key(r),
            score=r["raw_score"],
            source_url=r["source_url"],
            page_table=f"{r['page_number']} / {r['table_number']}",
            exact_setting=f"{r['benchmark_version']} | {r['metric_name']} | tools={r['tools_allowed']} | reasoning={r['reasoning_setting']}",
            why_important="Extended Evidence record that may affect BT/sensitivity analysis." if r["comparable"] == "Grade B" else "Supplementary or protocol-limited evidence.",
        ))
    return pd.DataFrame(rows).sort_values(["priority", "model", "benchmark"])


def source_expansion(selected: pd.DataFrame, phase1_matrix: pd.DataFrame, common_matrix: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    old_cols = [c for c in phase1_matrix.columns if c not in {"model_id", "model", "organization"}]
    old_cov = float(phase1_matrix[old_cols].notna().mean().mean())
    new_cols = [c for c in common_matrix.columns if c not in {"model_id", "model", "organization"}]
    new_cov = float(common_matrix[new_cols].notna().mean().mean())
    rows = []
    for source_id, g in selected.groupby("source_id"):
        src = sources.set_index("source_id").loc[source_id]
        rows.append(dict(
            source_id=source_id,
            publisher=src["publisher"],
            evidence_role=src["evidence_role"],
            source_quality=src["authority_level"],
            new_valid_cells=len(g),
            new_models_connected=g["model_id"].nunique(),
            new_model_pairs_connected=math.comb(g["model_id"].nunique(), 2) if g["model_id"].nunique() >= 2 else 0,
            reduction_in_components="See network diagnostics",
            coverage_increase=round(new_cov - old_cov, 4) if source_id in {"SRC006", "SRC007"} else 0,
            protocol_consistency=g["protocol_match"].mode().iat[0],
            marginal_information_gain="High" if source_id in {"SRC006", "SRC007"} else "Medium",
            notes=src["notes"],
        ))
    for source_id in ["SRC008", "SRC009"]:
        if source_id in set(sources["source_id"]) and source_id not in set(selected["source_id"]):
            src = sources.set_index("source_id").loc[source_id]
            rows.append(dict(
                source_id=source_id,
                publisher=src["publisher"],
                evidence_role=src["evidence_role"],
                source_quality=src["authority_level"],
                new_valid_cells=0,
                new_models_connected=0,
                new_model_pairs_connected=0,
                reduction_in_components="0; registered for metadata/validation only",
                coverage_increase=0,
                protocol_consistency="Not used in Common Matrix",
                marginal_information_gain="Low",
                notes=src["notes"],
            ))
    return pd.DataFrame(rows).sort_values(["marginal_information_gain", "new_valid_cells"], ascending=[True, False])


def reconstruct_phase1_matrix(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    core = core_selection(dfs["RawData"], dfs["Models"])
    selected = select_records(dfs["RawData"], core)
    matrix, _ = matrix_and_standardized(dfs["Models"], selected)
    return matrix


def spearman_exploration(common_matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cols = list(dict.fromkeys([c for c in common_matrix.columns if c not in {"model_id", "model", "organization"}]))
    numeric = common_matrix.loc[:, cols].copy()
    numeric = numeric.loc[:, ~numeric.columns.duplicated()].apply(pd.to_numeric, errors="coerce")
    cols = list(numeric.columns)
    corr = pd.DataFrame(index=cols, columns=cols, dtype=float)
    nmat = pd.DataFrame(index=cols, columns=cols, dtype=int)
    long_rows = []
    for a in cols:
        for b in cols:
            if a == b:
                n = int(numeric[a].notna().sum())
                nmat.loc[a, b] = n
                corr.loc[a, b] = 1.0 if n >= 1 else pd.NA
                continue
            pair = numeric[[a, b]].dropna()
            n = len(pair)
            nmat.loc[a, b] = n
            if n >= 4 and pair[a].nunique() > 1 and pair[b].nunique() > 1:
                rho, p = spearmanr(pair[a], pair[b])
            else:
                rho, p = (pd.NA, pd.NA)
            corr.loc[a, b] = rho if rho is not pd.NA else pd.NA
            if a < b:
                long_rows.append(dict(benchmark_1=a, benchmark_2=b, spearman_rho=rho, common_sample_size=n, p_value=p, overlap_rate=n / len(common_matrix)))
    return corr, nmat, pd.DataFrame(long_rows)


def plot_missing_heatmap(matrix: pd.DataFrame, path: Path, title: str) -> None:
    cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    data = matrix[cols].isna().astype(int)
    plt.figure(figsize=(max(10, len(cols) * 0.45), 4.8))
    plt.imshow(data, aspect="auto", cmap="Greys", vmin=0, vmax=1)
    plt.yticks(range(len(matrix)), matrix["model"], fontsize=7)
    plt.xticks(range(len(cols)), [c.split(" [")[0].replace("LiveBench ", "LB ") for c in cols], rotation=75, ha="right", fontsize=7)
    plt.title(title)
    plt.colorbar(label="1 = missing")
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()


def plot_coverage_comparison(old_matrix: pd.DataFrame, new_matrix: pd.DataFrame) -> None:
    old_cols = [c for c in old_matrix.columns if c not in {"model_id", "model", "organization"}]
    new_cols = [c for c in new_matrix.columns if c not in {"model_id", "model", "organization"}]
    old_model = old_matrix.set_index("model")[old_cols].notna().mean(axis=1)
    new_model = new_matrix.set_index("model")[new_cols].notna().mean(axis=1)
    plt.figure(figsize=(9, 4.8))
    comp = pd.DataFrame({"Phase1": old_model, "Phase2 Common": new_model}).fillna(0)
    comp.plot(kind="bar", ax=plt.gca())
    plt.ylabel("Coverage")
    plt.title("Model Coverage Before vs After")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "model_coverage_before_after.png", dpi=220)
    plt.close()

    plt.figure(figsize=(8, 4))
    vals = [old_matrix[old_cols].notna().mean().mean(), new_matrix[new_cols].notna().mean().mean()]
    plt.plot([0, 1], vals, marker="o")
    plt.xticks([0, 1], ["Phase1", "Phase2 Common"])
    plt.ylim(0, 1)
    plt.ylabel("Overall coverage")
    plt.title("Coverage Optimization Curve")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "coverage_new_sources_curve.png", dpi=220)
    plt.close()

    old_bench = old_matrix[old_cols].notna().mean()
    new_bench = new_matrix[new_cols].notna().mean()
    plt.figure(figsize=(9, 4.8))
    plt.boxplot([old_bench.values, new_bench.values], labels=["Phase1", "Phase2 Common"])
    plt.ylabel("Benchmark coverage distribution")
    plt.title("Benchmark Coverage Before vs After")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "benchmark_coverage_before_after.png", dpi=220)
    plt.close()

    old_bench = old_matrix[old_cols].notna().mean().rename("Phase1")
    new_bench = new_matrix[new_cols].notna().mean().rename("Phase2 Common")
    plt.figure(figsize=(11, 4.8))
    new_bench.sort_values(ascending=False).plot(kind="bar")
    plt.ylabel("Coverage")
    plt.title("Phase2 Common Benchmark Coverage")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "benchmark_coverage_after.png", dpi=220)
    plt.close()


def plot_networks(graphs: dict[str, nx.Graph], prefix: str) -> None:
    for cap, g in graphs.items():
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(g, seed=42, k=0.9)
        colors = ["#4c78a8" if g.nodes[n].get("node_type") == "benchmark" else "#f58518" for n in g.nodes]
        nx.draw_networkx(g, pos, node_size=650, node_color=colors, font_size=6, edge_color="#999999")
        plt.title(cap)
        plt.axis("off")
        safe = re.sub(r"[^A-Za-z0-9]+", "_", cap).strip("_")
        plt.tight_layout()
        plt.savefig(FIG_DIR / f"{prefix}_{safe}.png", dpi=220)
        plt.close()


def write_reports(
    raw: pd.DataFrame,
    sources: pd.DataFrame,
    old_matrix: pd.DataFrame,
    common_matrix: pd.DataFrame,
    bench_cov: pd.DataFrame,
    model_cov: pd.DataFrame,
    pair_diag: pd.DataFrame,
    bip_diag: pd.DataFrame,
    model_review: pd.DataFrame,
    source_exp: pd.DataFrame,
    crossval: pd.DataFrame,
) -> None:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    cols = [c for c in common_matrix.columns if c not in {"model_id", "model", "organization"}]
    old_cols = [c for c in old_matrix.columns if c not in {"model_id", "model", "organization"}]
    new_cov = common_matrix[cols].notna().mean().mean()
    grade_counts = raw["comparable"].value_counts().to_dict()
    common_records = raw[raw["selected_for_common_matrix"].eq(True)]
    ab_ratio = common_records["comparable"].isin(["Grade A", "Grade B"]).mean() if not common_records.empty else 0
    xvr = str(crossval.loc[crossval["selected_record"].eq("SUMMARY"), "sources"].iat[0]).split("=")[-1]
    risks = [
        "C3 long-context Common evidence remains sparse; MRCR/CorpusQA mainly connect DeepSeek variants.",
        "Qwen representative changed: Qwen3.8-Max is better for Common Matrix coverage, while Qwen3-235B-A22B remains bridge/extended evidence.",
        "OpenRouter GPQA model-version names do not perfectly match all first-stage model names, so GPT-5.6 Sol Pro was not mapped to GPT-5.6 Sol max.",
        "LiveBench task-level scores are unified and high-coverage, but they should not be collapsed with LiveBench composite indices.",
        "All machine-extracted/new records keep human_verified=FALSE pending manual audit.",
    ]
    qc = [
        "# Data Quality Report",
        "",
        "## A. 数据规模",
        f"- RawData records after Phase2: {len(raw)}",
        f"- Common Matrix models: {len(common_matrix)}",
        f"- Common Matrix benchmark settings: {len(cols)}",
        f"- Phase1 overall coverage: {old_matrix[old_cols].notna().mean().mean():.2%}",
        f"- Phase2 Common Matrix coverage: {new_cov:.2%}",
        "",
        "## B. 来源质量",
        f"- Raw source authority counts: {raw['source_authority_level'].value_counts().to_dict()}",
        f"- Evidence role counts: {raw['evidence_role'].value_counts().to_dict()}",
        "",
        "## C. 缺失情况",
        f"- Overall Common Matrix missing rate: {1-new_cov:.2%}",
        f"- Min model coverage: {model_cov['coverage_rate'].min():.2%}",
        f"- Median model coverage: {model_cov['coverage_rate'].median():.2%}",
        f"- Min benchmark coverage: {bench_cov['coverage_rate'].min():.2%}",
        f"- Median benchmark coverage: {bench_cov['coverage_rate'].median():.2%}",
        "",
        "## D. 可比性",
        f"- Grade counts: {grade_counts}",
        f"- Common Matrix Grade A/B ratio: {ab_ratio:.2%}",
        "",
        "## E. 冲突与交叉验证",
        f"- Automatic conflicts: {len(conflict_check(raw))}",
        f"- CrossValidationRate: {xvr}",
        "",
        "## F. 风险",
        *[f"- {r}" for r in risks],
        "",
    ]
    (reports / "data_quality_report.md").write_text("\n".join(qc), encoding="utf-8")

    all_connected = pair_diag["connectivity_status"].eq("CONNECTED").all()
    status = "READY" if new_cov >= 0.70 and model_cov["coverage_rate"].min() >= 0.50 and all_connected else "NOT_READY"
    report = [
        "# Phase2 Coverage Optimization Report",
        "",
        "## A. 数据覆盖",
        f"- 扩充前覆盖率: {old_matrix[old_cols].notna().mean().mean():.2%}",
        f"- 扩充后 Common Matrix 覆盖率: {new_cov:.2%}",
        f"- 是否达到 70%: {'是' if new_cov >= 0.70 else '否'}",
        "- 若未达到，原因见 C3/事实性 Benchmark 的公开统一评测覆盖限制；本轮未为覆盖率降低可比性标准。",
        "",
        "## B. 模型覆盖",
        "```text\n" + model_cov.to_string(index=False) + "\n```",
        "",
        "## C. Benchmark 覆盖",
        "```text\n" + bench_cov[["benchmark", "capability", "coverage_rate", "evidence_role", "recommend_keep"]].to_string(index=False) + "\n```",
        "",
        "## D. 能力维度网络",
        "```text\n" + pair_diag[["capability", "connected_components", "isolated_models", "graph_density", "connectivity_status"]].to_string(index=False) + "\n```",
        "",
        "## E. 新数据来源",
        "```text\n" + source_exp.to_string(index=False) + "\n```",
        "",
        "## F. 数据质量",
        f"- Grade counts: {grade_counts}",
        f"- Common Matrix Grade A/B ratio: {ab_ratio:.2%}",
        f"- CrossValidationRate: {xvr}",
        f"- Human verification priority records: see `human_verification_priority.xlsx`.",
        "",
        "## G. 是否可以进入正式建模",
        f"`{status}`",
        "",
    ]
    if status == "READY":
        report += [
            "理由：Common Matrix 达到约 70% 覆盖，主模型至少有 50% 覆盖，多数能力维度连通性改善，适合进入缺失感知 Spearman、Benchmark 筛选、Bradley-Terry 潜在能力估计和 Bootstrap 稳健排名。",
        ]
    else:
        report += [
            "前三项阻碍：C3 长上下文网络稀疏且不连通；C2 事实可靠性独立统一来源不足；C5 多模态主要依赖厂商表，无法连接 DeepSeek/Gemini/Qwen/GLM。",
        ]
    (reports / "coverage_optimization_report.md").write_text("\n".join(report), encoding="utf-8")
    (reports / "data_collection_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    dfs = make_dataframes()
    models, sources, raw = augment_raw(dfs)
    old_matrix = reconstruct_phase1_matrix(dfs)
    audit = benchmark_setting_audit(raw, old_matrix)
    common_matrix, selected = build_common_matrix(raw, models)
    raw.loc[raw["record_id"].isin(set(selected["record_id"])), "selected_for_common_matrix"] = True
    raw.loc[raw["record_id"].isin(set(selected["record_id"])), "selected_reason"] = raw["record_id"].map(selected.set_index("record_id")["selected_reason"]).fillna(raw["selected_reason"])
    extended = extended_matrix(raw, models)
    bench_cov, model_cov, metrics = coverage_tables(common_matrix, selected)
    pair_diag, pair_graphs = pairwise_networks(common_matrix, selected)
    bip_diag, bip_graphs = bipartite_networks(common_matrix, selected)
    review = model_pool_review(models, common_matrix, selected, pair_diag)
    crossval = cross_validation_report(selected, raw)
    human = human_verification_priority(selected, raw, bip_diag)
    source_exp = source_expansion(selected, old_matrix, common_matrix, sources)
    corr, nmat, corr_long = spearman_exploration(common_matrix)
    conflicts = conflict_check(raw)
    manual = pd.read_excel(OUT_PROCESSED / "manual_review_required.xlsx")
    new_manual = pd.DataFrame([
        dict(issue="Phase2 Common record requires human verification", model=r["model_full_name"], benchmark=r["matrix_key"], sources_found=r["source_id"], why_unresolved="Machine extracted from unified source; human_verified remains FALSE.", suggested_manual_check="Use human_verification_priority.xlsx Priority 1 rows.")
        for _, r in selected.iterrows()
    ])
    manual = pd.concat([manual, new_manual], ignore_index=True).drop_duplicates()

    # Save phase2 artifacts.
    raw.to_csv(OUT_RAW / "raw_benchmark_data.csv", index=False, encoding="utf-8-sig")
    raw.to_excel(OUT_RAW / "raw_benchmark_data.xlsx", index=False)
    sources.to_excel(OUT_PROCESSED / "source_registry.xlsx", index=False)
    audit.to_excel(OUT_PROCESSED / "benchmark_setting_audit.xlsx", index=False)
    common_matrix.to_excel(OUT_FINAL / "common_evaluation_matrix.xlsx", index=False)
    extended.to_excel(OUT_FINAL / "extended_evidence_matrix.xlsx", index=False)
    common_matrix.to_csv(OUT_FINAL / "benchmark_matrix.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUT_PROCESSED / "benchmark_coverage.xlsx", engine="openpyxl") as writer:
        bench_cov.to_excel(writer, index=False, sheet_name="common_benchmark_coverage")
        model_cov.to_excel(writer, index=False, sheet_name="common_model_coverage")
    review.to_excel(OUT_PROCESSED / "model_pool_review.xlsx", index=False)
    pair_diag.to_excel(OUT_PROCESSED / "pairwise_network_diagnostics.xlsx", index=False)
    bip_diag.to_excel(OUT_PROCESSED / "benchmark_network_diagnostics.xlsx", index=False)
    crossval.to_excel(OUT_PROCESSED / "cross_validation_report.xlsx", index=False)
    human.to_excel(OUT_PROCESSED / "human_verification_priority.xlsx", index=False)
    source_exp.to_excel(OUT_PROCESSED / "source_expansion_report.xlsx", index=False)
    manual.to_excel(OUT_PROCESSED / "manual_review_required.xlsx", index=False)
    conflicts.to_excel(OUT_PROCESSED / "data_conflicts.xlsx", index=False)
    with pd.ExcelWriter(OUT_PROCESSED / "benchmark_spearman_matrix.xlsx", engine="openpyxl") as writer:
        corr.to_excel(writer, sheet_name="spearman")
        nmat.to_excel(writer, sheet_name="pairwise_sample_size_matrix")
        corr_long.to_excel(writer, index=False, sheet_name="pairwise_long")

    plot_missing_heatmap(old_matrix, FIG_DIR / "phase1_missing_heatmap.png", "Phase1 Matrix Missingness")
    plot_missing_heatmap(common_matrix, FIG_DIR / "phase2_common_missing_heatmap.png", "Phase2 Common Matrix Missingness")
    plot_coverage_comparison(old_matrix, common_matrix)
    plot_networks(pair_graphs, "pairwise_network")
    plot_networks(bip_graphs, "benchmark_network")

    # Additional figures.
    plt.figure(figsize=(7, 4))
    pd.Series({
        "VENDOR_REPORT": int((raw["evidence_role"] == "VENDOR_REPORT").sum()),
        "COMMON_EVAL": int((raw["evidence_role"] == "COMMON_EVAL").sum()),
        "SUPPLEMENTARY": int((raw["evidence_role"] == "SUPPLEMENTARY").sum()),
        "EXTERNAL_VALIDATION": int((raw["evidence_role"] == "EXTERNAL_VALIDATION").sum()),
    }).plot(kind="pie", autopct="%1.1f%%")
    plt.ylabel("")
    plt.title("Evidence Role Composition")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "source_type_composition.png", dpi=220)
    plt.close()

    plt.figure(figsize=(8, 4))
    pair_diag.set_index("capability")["connected_components"].plot(kind="bar")
    plt.ylabel("Connected components")
    plt.title("Pairwise Network Components by Capability")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "capability_components.png", dpi=220)
    plt.close()

    readme = pd.DataFrame([
        ("数据目的", "Phase2: dual-track Common/Extended evidence dataset for modeling-ready LLM benchmark analysis."),
        ("data_freeze_date", DATA_FREEZE_DATE),
        ("Common Matrix coverage", f"{metrics['overall_coverage']:.4f}"),
        ("Missing-value policy", "NA retained; no benchmark score imputation."),
        ("Common Matrix rule", "Prefer unified independent re-evaluation; retain vendor/official sparse capability evidence only when setting is separated and traceable."),
        ("Extended Evidence rule", "Preserve Phase1 vendor data and protocol-limited evidence for sensitivity, BT, and partial-order analysis."),
        ("Qwen representative", "Qwen3.8-Max recommended as CORE_MODEL for Common Matrix; Qwen3-235B-A22B remains BRIDGE_MODEL/Extended evidence."),
        ("Human verification", "All machine-extracted records remain human_verified=FALSE."),
    ], columns=["item", "description"])
    qc = pd.DataFrame([
        ("phase2_overall_coverage", metrics["overall_coverage"], "INFO"),
        ("phase2_min_model_coverage", metrics["min_model_coverage"], "INFO"),
        ("phase2_median_model_coverage", metrics["median_model_coverage"], "INFO"),
        ("phase2_min_benchmark_coverage", metrics["min_benchmark_coverage"], "INFO"),
        ("phase2_median_benchmark_coverage", metrics["median_benchmark_coverage"], "INFO"),
        ("conflicts", len(conflicts), "INFO"),
        ("raw_records_without_source", int(raw["source_id"].isna().sum()), "PASS" if raw["source_id"].notna().all() else "FAIL"),
    ], columns=["item", "value", "status"])

    with pd.ExcelWriter(OUT_FINAL / "LLM_Benchmark_Evaluation_Dataset.xlsx", engine="openpyxl") as writer:
        readme.to_excel(writer, index=False, sheet_name="README")
        models.to_excel(writer, index=False, sheet_name="Models")
        dfs["Benchmarks"].to_excel(writer, index=False, sheet_name="Benchmarks")
        raw.to_excel(writer, index=False, sheet_name="RawData")
        sources.to_excel(writer, index=False, sheet_name="Sources")
        raw[["record_id", "model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed", "reasoning_setting", "protocol_match", "version_match", "comparable", "evidence_role", "selected_for_common_matrix", "selected_reason", "notes"]].to_excel(writer, index=False, sheet_name="Comparability")
        conflicts.to_excel(writer, index=False, sheet_name="Conflicts")
        bench_cov.to_excel(writer, index=False, sheet_name="Coverage")
        audit.to_excel(writer, index=False, sheet_name="CoreBenchmarks")
        old_matrix.to_excel(writer, index=False, sheet_name="Matrix")
        common_matrix.to_excel(writer, index=False, sheet_name="CommonMatrix")
        extended.to_excel(writer, index=False, sheet_name="ExtendedMatrix")
        model_cov.to_excel(writer, index=False, sheet_name="StandardizedMatrix")
        dfs["Benchmarks"][["capability_dimension", "benchmark_name", "reason"]].to_excel(writer, index=False, sheet_name="CapabilityMapping")
        qc.to_excel(writer, index=False, sheet_name="QC")
        bip_diag.to_excel(writer, index=False, sheet_name="NetworkQC")
        review.to_excel(writer, index=False, sheet_name="ModelPoolReview")
        source_exp.to_excel(writer, index=False, sheet_name="SourceExpansion")
        crossval.to_excel(writer, index=False, sheet_name="CrossValidation")
        human.to_excel(writer, index=False, sheet_name="HumanVerificationPriority")

    write_reports(raw, sources, old_matrix, common_matrix, bench_cov, model_cov, pair_diag, bip_diag, review, source_exp, crossval)
    print(f"Phase2 Common Matrix coverage: {metrics['overall_coverage']:.2%}")
    print(f"Common Matrix: {len(common_matrix)} models x {len([c for c in common_matrix.columns if c not in {'model_id','model','organization'}])} benchmark settings")


if __name__ == "__main__":
    main()
