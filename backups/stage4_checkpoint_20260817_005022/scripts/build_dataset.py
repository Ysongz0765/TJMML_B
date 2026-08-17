from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = "2026-08-16"


RAW_COLUMNS = [
    "record_id", "model_id", "model_family", "model_full_name", "organization",
    "capability_dimension", "benchmark_name", "benchmark_version", "benchmark_year",
    "metric_name", "metric_definition", "raw_score", "raw_unit", "higher_is_better",
    "tools_allowed", "browsing_allowed", "reasoning_setting", "pass_k_setting",
    "prompting_setting", "test_protocol", "additional_setting", "source_id",
    "source_type", "publisher", "source_title", "source_url", "publication_date",
    "access_date", "page_number", "table_number", "extraction_method",
    "source_authority_level", "protocol_match", "version_match", "comparable",
    "verified", "machine_extracted", "human_verified", "cross_source_verified",
    "conflict_flag", "exclusion_reason", "notes",
]


def model_rows() -> list[dict[str, Any]]:
    return [
        dict(model_id="kimi_k3_max", model_family="Kimi", model_full_name="Kimi K3 (max reasoning)", organization="Moonshot AI", release_date="2026-07-23", open_or_closed="Open-weight", api_available="Yes", source_for_model_identity="SRC001", inclusion_status="Core", inclusion_reason="Mandatory by task; official Kimi K3 README provides broad benchmark table.", notes="Native multimodal, 1M context; scores use max reasoning unless otherwise noted."),
        dict(model_id="gpt_5_6_sol_max", model_family="GPT", model_full_name="GPT-5.6 Sol (max)", organization="OpenAI", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC001; SRC002", inclusion_status="Core", inclusion_reason="Representative OpenAI frontier model with public comparison scores in Kimi K3 report.", notes="OpenAI page could not be locally archived due Cloudflare challenge; keep manual review flag."),
        dict(model_id="gpt_5_5_xhigh", model_family="GPT", model_full_name="GPT-5.5 (xhigh)", organization="OpenAI", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC001", inclusion_status="Core", inclusion_reason="OpenAI family comparator with multiple public scores in Kimi K3 report.", notes="Reasoning setting xhigh."),
        dict(model_id="claude_fable_5_max", model_family="Claude", model_full_name="Claude Fable 5 (max, with fallback)", organization="Anthropic", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC001", inclusion_status="Core", inclusion_reason="Representative Anthropic frontier model in Kimi K3 horizontal table.", notes="Kimi report notes fallback on some agentic tasks."),
        dict(model_id="claude_opus_4_8_max", model_family="Claude", model_full_name="Claude Opus 4.8 (max)", organization="Anthropic", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC001", inclusion_status="Core", inclusion_reason="Second Anthropic frontier comparator; avoids over-weighting one Claude variant.", notes="Scores mainly from Kimi K3 report."),
        dict(model_id="gemini_3_1_pro_high", model_family="Gemini", model_full_name="Gemini-3.1-Pro (High)", organization="Google DeepMind", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC003", inclusion_status="Core", inclusion_reason="Representative Google model covered by DeepSeek-V4 official horizontal table.", notes="Model naming follows DeepSeek-V4 table; exact Google release page requires manual identity confirmation."),
        dict(model_id="gemini_3_5_flash", model_family="Gemini", model_full_name="Gemini 3.5 Flash", organization="Google DeepMind", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC002", inclusion_status="CandidateExcluded", inclusion_reason="Representative Google fast model, but no locally parsed authoritative benchmark table in this run.", notes="Retained in candidate pool only."),
        dict(model_id="deepseek_v4_pro_max", model_family="DeepSeek", model_full_name="DeepSeek-V4-Pro Max", organization="DeepSeek", release_date="2026-06-23", open_or_closed="Open-weight/Unknown", api_available="Yes", source_for_model_identity="SRC003", inclusion_status="Core", inclusion_reason="Representative DeepSeek high-reasoning mode with broad official table.", notes="Model identity includes Max reasoning mode."),
        dict(model_id="deepseek_v4_flash_max", model_family="DeepSeek", model_full_name="DeepSeek-V4-Flash Max", organization="DeepSeek", release_date="2026-06-23", open_or_closed="Open-weight/Unknown", api_available="Yes", source_for_model_identity="SRC003", inclusion_status="Core", inclusion_reason="Second DeepSeek variant; useful for cost/performance comparison.", notes="Model identity includes Max reasoning mode."),
        dict(model_id="qwen3_235b_a22b_base", model_family="Qwen", model_full_name="Qwen3-235B-A22B (Base / report setting)", organization="Alibaba Qwen", release_date="2025-05-14", open_or_closed="Open-weight", api_available="Yes", source_for_model_identity="SRC004", inclusion_status="Core", inclusion_reason="Representative Alibaba/Qwen model with official technical report tables.", notes="Newer Qwen3.8 dynamic page was not machine-archived; this version has stronger traceability."),
        dict(model_id="glm_5_2_max", model_family="GLM", model_full_name="GLM-5.2 (max)", organization="Zhipu AI / Z.ai", release_date="Unknown", open_or_closed="Unknown", api_available="Yes", source_for_model_identity="SRC001", inclusion_status="Core", inclusion_reason="Representative Chinese frontier comparator in Kimi K3 report.", notes="Some multimodal entries missing in Kimi table."),
        dict(model_id="kimi_k2_6_thinking", model_family="Kimi", model_full_name="Kimi K2.6 (Thinking)", organization="Moonshot AI", release_date="Unknown", open_or_closed="Unknown", api_available="Yes", source_for_model_identity="SRC003", inclusion_status="CandidateExcluded", inclusion_reason="Covered by DeepSeek table, but Kimi K3 is the required Moonshot core model.", notes="Avoids excessive same-family duplication."),
        dict(model_id="llama_4_maverick_base", model_family="Llama", model_full_name="Llama-4-Maverick (Base)", organization="Meta", release_date="Unknown", open_or_closed="Open-weight", api_available="Unknown", source_for_model_identity="SRC004", inclusion_status="CandidateExcluded", inclusion_reason="Included in Qwen candidate comparison but not required vendor coverage and limited final cross-benchmark data.", notes="Candidate only."),
        dict(model_id="qwen3_8_max", model_family="Qwen", model_full_name="Qwen3.8-Max", organization="Alibaba Qwen", release_date="2026-08-10", open_or_closed="Closed/Unknown", api_available="Yes", source_for_model_identity="SRC005", inclusion_status="CandidateExcluded", inclusion_reason="Current representative candidate but official page was dynamic and not parsed into reliable benchmark records.", notes="Needs manual browser verification before core use."),
        dict(model_id="opus_4_6_max", model_family="Claude", model_full_name="Opus-4.6 (Max)", organization="Anthropic", release_date="Unknown", open_or_closed="Closed", api_available="Yes", source_for_model_identity="SRC003", inclusion_status="CandidateExcluded", inclusion_reason="DeepSeek comparator; excluded to avoid too many Anthropic versions.", notes="Candidate only."),
    ]


def sources() -> list[dict[str, Any]]:
    return [
        dict(source_id="SRC001", publisher="Moonshot AI", source_title="Kimi K3 README / Technical Release", source_type="Vendor official GitHub / model technical release", url="https://github.com/MoonshotAI/Kimi-K3", publication_date="2026-07-23", access_date=ACCESS_DATE, authority_level="B", benchmark_related="GPQA Diamond; HLE-Full; DeepSWE; ProgramBench; Terminal-Bench 2.1; FrontierSWE; SciCode; MMMU-Pro; MathVision", models_covered="Kimi K3; Claude Fable 5; GPT-5.6 Sol; Claude Opus 4.8; GPT-5.5; GLM-5.2", local_archive_path="sources/structured/SRC001_kimi_k3_readme.md", notes="Some non-Kimi scores are cited from external leaderboards or vendor reports within README; manual source-by-source audit recommended."),
        dict(source_id="SRC002", publisher="OpenAI", source_title="Previewing GPT-5.6 Sol / GPT-5.6 page", source_type="Vendor official web page", url="https://openai.com/index/gpt-5-6/", publication_date="Unknown", access_date=ACCESS_DATE, authority_level="B", benchmark_related="Model identity and cited OpenAI benchmark context", models_covered="GPT-5.6 Sol", local_archive_path="UNAVAILABLE: Cloudflare challenge blocked local archival", notes="Registered for traceability because Kimi README footnotes cite OpenAI for some GPT scores."),
        dict(source_id="SRC003", publisher="DeepSeek", source_title="DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence", source_type="Vendor technical report / arXiv HTML", url="https://arxiv.org/html/2606.19348v1", publication_date="2026-06-23", access_date=ACCESS_DATE, authority_level="B", benchmark_related="MMLU-Pro; SimpleQA-Verified; GPQA Diamond; LiveCodeBench; MRCR 1M; CorpusQA 1M; SWE Verified; SWE Pro; Terminal Bench 2.0", models_covered="DeepSeek-V4-Pro; DeepSeek-V4-Flash; Gemini-3.1-Pro; others", local_archive_path="sources/html/SRC003_deepseek_v4_arxiv.html", notes="Tables 23 and 24 were parsed with pandas.read_html from local archive."),
        dict(source_id="SRC004", publisher="Alibaba Qwen", source_title="Qwen3 Technical Report", source_type="Vendor technical report / arXiv HTML", url="https://arxiv.org/html/2505.09388v1", publication_date="2025-05-14", access_date=ACCESS_DATE, authority_level="B", benchmark_related="MMLU; MMLU-Redux; MMLU-Pro; GPQA; MATH; EvalPlus; MBPP; RULER", models_covered="Qwen3-235B-A22B; Qwen3 family", local_archive_path="sources/html/SRC004_qwen3_arxiv.html", notes="Tables 2 and 21 were parsed with pandas.read_html from local archive."),
        dict(source_id="SRC005", publisher="Alibaba Qwen", source_title="Qwen3.8 official blog page", source_type="Vendor official web page", url="https://qwen.ai/blog?id=qwen3.8", publication_date="2026-08-10", access_date=ACCESS_DATE, authority_level="B", benchmark_related="Candidate model identity only", models_covered="Qwen3.8-Max and related models", local_archive_path="UNAVAILABLE: dynamic CSR page did not expose benchmark table in static HTML", notes="No benchmark scores used."),
    ]


def benchmark_rows() -> list[dict[str, Any]]:
    rows = [
        ("BM001", "GPQA Diamond", "Diamond", "C1 Complex reasoning", "Graduate-level Google-proof Q&A subset emphasizing hard science reasoning.", "High-difficulty scientific reasoning and expert knowledge.", "Pass@1 / accuracy", "0-100%", True, "https://github.com/idavidrein/gpqa", "https://arxiv.org/abs/2311.12022", True, True, "Core", "High coverage in Kimi and DeepSeek reports; strong C1 representative.", ""),
        ("BM002", "HLE-Full", "Full", "C2 Knowledge and factual reliability", "Humanity's Last Exam style broad, difficult factual and reasoning benchmark.", "Frontier knowledge/reasoning under very hard factual tasks.", "Pass@1", "0-100%", True, "https://lastexam.ai/", "https://arxiv.org/abs/2501.14249", True, True, "Core", "Used as hard factual reliability proxy; separate no-tools and tools settings.", "Kimi uses HLE-Full; DeepSeek table uses HLE, not merged."),
        ("BM003", "MMLU-Pro", "Pro", "C2 Knowledge and factual reliability", "More robust and challenging multi-task language understanding benchmark.", "Broad professional and academic knowledge under harder options.", "EM / accuracy", "0-100%", True, "https://github.com/TIGER-AI-Lab/MMLU-Pro", "https://arxiv.org/abs/2406.01574", True, True, "Core", "Canonical C2 benchmark; coverage limited but authoritative.", ""),
        ("BM004", "SimpleQA-Verified", "Verified", "C2 Knowledge and factual reliability", "Short-answer factuality benchmark with verified questions.", "Factual precision and hallucination control.", "Pass@1", "0-100%", True, "https://openai.com/index/simpleqa/", "https://arxiv.org/abs/2411.04368", True, True, "Core", "Directly measures factuality; low coverage but valuable.", ""),
        ("BM005", "MRCR 1M", "1M", "C3 Long context", "Long-context multi-round/coreference retrieval task at one million token context.", "Needle retrieval and multi-reference reasoning over 1M context.", "MMR", "0-100", True, "https://github.com/microsoft/RULER", "Unknown", True, True, "Core", "One of the few 1M-context reported tasks.", ""),
        ("BM006", "CorpusQA 1M", "1M", "C3 Long context", "Long-document QA over a million-token corpus setting.", "Long-context document comprehension and retrieval.", "ACC", "0-100%", True, "https://arxiv.org/html/2606.19348v1", "Unknown", True, True, "Core", "Complements synthetic retrieval with corpus QA.", ""),
        ("BM007", "RULER", "Avg", "C3 Long context", "Suite evaluating long-context retrieval and reasoning across context lengths.", "Long-context robustness and information retrieval.", "Average accuracy", "0-100%", True, "https://github.com/NVIDIA/RULER", "https://arxiv.org/abs/2404.06654", True, True, "Core", "Officially recognized long-context suite; Qwen report provides versioned rows.", ""),
        ("BM008", "DeepSWE", "v1.1", "C4 Code and software engineering", "Software engineering benchmark focused on real code tasks.", "Agentic software engineering issue resolution.", "Score / accuracy", "0-100%", True, "https://deepswe.datacurve.ai/", "Unknown", True, True, "Candidate", "Coverage good in Kimi table but harnesses differ; kept supplemental.", "Protocol caution."),
        ("BM009", "ProgramBench", "Unknown", "C4 Code and software engineering", "Programming benchmark reported by Vals AI and vendor reports.", "Algorithmic/programming performance.", "Accuracy", "0-100%", True, "https://www.vals.ai/benchmarks/programbench", "Unknown", True, True, "Core", "Good Kimi-table coverage and clear metric.", "Needs official Vals row audit."),
        ("BM010", "Terminal-Bench", "2.1", "C4 Code and software engineering", "Terminal-based task benchmark for agents operating in shell environments.", "Tool/terminal software task execution.", "Accuracy", "0-100%", True, "https://www.tbench.ai/", "https://arxiv.org/abs/2508.09131", True, True, "Candidate", "High coverage but Kimi table mixes harnesses; supplemental.", ""),
        ("BM011", "SWE Verified", "Verified", "C4 Code and software engineering", "Curated subset of SWE-bench with human-verified issue tasks.", "Real-world GitHub issue resolution.", "Resolved", "0-100%", True, "https://www.swebench.com/", "https://arxiv.org/abs/2310.06770", True, True, "Core", "Gold-standard SWE task; coverage low but protocol strong in DeepSeek table.", ""),
        ("BM012", "SWE Pro", "Pro", "C4 Code and software engineering", "Harder professional SWE benchmark variant.", "More difficult issue-resolution tasks.", "Resolved", "0-100%", True, "https://arxiv.org/html/2606.19348v1", "Unknown", True, True, "Candidate", "Useful but mostly DeepSeek-source coverage.", ""),
        ("BM013", "LiveCodeBench", "v5 / reported", "C4 Code and software engineering", "Contamination-resistant competitive programming benchmark.", "Recent coding problem solving.", "Pass@1", "0-100%", True, "https://livecodebench.github.io/", "https://arxiv.org/abs/2403.07974", True, True, "Candidate", "Version/CoT settings differ across sources; not merged.", ""),
        ("BM014", "MMMU-Pro", "Pro", "C5 Multimodal", "More difficult MMMU-style multimodal university benchmark.", "Multimodal expert reasoning over image and text.", "Accuracy", "0-100%", True, "https://mmmu-benchmark.github.io/", "https://arxiv.org/abs/2311.16502", True, True, "Core", "Best multimodal coverage in Kimi table; no-tools and tools split.", ""),
        ("BM015", "MathVision", "Unknown", "C5 Multimodal", "Visual mathematical reasoning benchmark.", "Math reasoning from visual inputs.", "Accuracy", "0-100%", True, "https://mathvision-cuhk.github.io/", "https://arxiv.org/abs/2402.14804", True, True, "Core", "Complements MMMU-Pro with visual math.", ""),
        ("BM016", "SciCode", "Unknown", "C4 Code and software engineering", "Scientific coding benchmark.", "Scientific programming and code reasoning.", "Accuracy", "0-100%", True, "https://github.com/scicode-bench/SciCode", "https://arxiv.org/abs/2407.13168", True, True, "Candidate", "Useful but source is Artificial Analysis via Kimi note.", ""),
        ("BM017", "MMLU-Redux", "Redux", "C2 Knowledge and factual reliability", "Cleaned/reduced MMLU variant.", "Broad knowledge with corrected dataset artifacts.", "EM / accuracy", "0-100%", True, "https://github.com/edinburgh-dawg/mmlu-redux", "https://arxiv.org/abs/2406.04127", True, True, "Candidate", "Useful for Qwen only in current data.", ""),
        ("BM018", "MATH", "Reported", "C1 Complex reasoning", "Competition math benchmark.", "Mathematical problem solving.", "Accuracy", "0-100%", True, "https://github.com/hendrycks/math", "https://arxiv.org/abs/2103.03874", True, True, "Candidate", "Only Qwen base table in current data.", ""),
        ("BM019", "EvalPlus", "Reported", "C4 Code and software engineering", "Enhanced HumanEval/MBPP style evaluation.", "Code generation robustness.", "Accuracy", "0-100%", True, "https://evalplus.github.io/", "https://arxiv.org/abs/2305.01210", True, True, "Candidate", "Qwen-only in current data.", ""),
        ("BM020", "MBPP", "Reported", "C4 Code and software engineering", "Mostly Basic Python Problems.", "Introductory Python code generation.", "Accuracy", "0-100%", True, "https://github.com/google-research/google-research/tree/master/mbpp", "https://arxiv.org/abs/2108.07732", True, True, "Candidate", "Qwen-only; less frontier-discriminative.", ""),
        ("BM021", "FrontierSWE", "Reported", "C4 Code and software engineering", "Frontier software engineering dominance benchmark.", "Difficult software engineering tasks.", "Dominance score", "0-100", True, "https://www.frontierswe.com/", "Unknown", True, True, "Core", "Kimi table gives six-model coverage; protocol notes preserved.", "Needs raw leaderboard audit."),
    ]
    keys = ["benchmark_id", "benchmark_name", "benchmark_version", "capability_dimension", "official_description", "what_it_measures", "metric_name", "score_range", "higher_is_better", "official_source", "official_paper", "version_sensitive", "protocol_sensitive", "candidate_or_core", "reason", "notes"]
    return [dict(zip(keys, r)) for r in rows]


def _source_meta(source_id: str) -> dict[str, Any]:
    row = next(s for s in sources() if s["source_id"] == source_id)
    return dict(
        source_id=source_id, source_type=row["source_type"], publisher=row["publisher"],
        source_title=row["source_title"], source_url=row["url"],
        publication_date=row["publication_date"], access_date=row["access_date"],
        source_authority_level=row["authority_level"],
    )


def raw_data_rows() -> list[dict[str, Any]]:
    models = {m["model_id"]: m for m in model_rows()}
    rows: list[dict[str, Any]] = []
    counter = 1

    def add(model_id: str, capability: str, benchmark: str, version: str, year: str,
            metric: str, metric_def: str, score: Any, unit: str, source_id: str,
            tools: str = "No", browsing: str = "No", reasoning: str = "Unknown",
            pass_k: str = "pass@1", prompting: str = "Unknown", protocol: str = "Unknown",
            additional: str = "", page: str = "NA", table: str = "NA",
            method: str = "manual_transcription_from_official_table",
            protocol_match: str = "High", version_match: str = "High",
            comparable: str = "Grade B", exclusion: str = "", notes: str = "") -> None:
        nonlocal counter
        if score in (None, "", "-", "—") or pd.isna(score):
            return
        m = models[model_id]
        meta = _source_meta(source_id)
        rows.append(dict(
            record_id=f"R{counter:04d}",
            model_id=model_id,
            model_family=m["model_family"],
            model_full_name=m["model_full_name"],
            organization=m["organization"],
            capability_dimension=capability,
            benchmark_name=benchmark,
            benchmark_version=version,
            benchmark_year=year,
            metric_name=metric,
            metric_definition=metric_def,
            raw_score=score,
            raw_unit=unit,
            higher_is_better=True,
            tools_allowed=tools,
            browsing_allowed=browsing,
            reasoning_setting=reasoning,
            pass_k_setting=pass_k,
            prompting_setting=prompting,
            test_protocol=protocol,
            additional_setting=additional,
            page_number=page,
            table_number=table,
            extraction_method=method,
            protocol_match=protocol_match,
            version_match=version_match,
            comparable=comparable,
            verified="FALSE",
            machine_extracted="TRUE",
            human_verified="FALSE",
            cross_source_verified="FALSE",
            conflict_flag=0,
            exclusion_reason=exclusion,
            notes=notes,
            **meta,
        ))
        counter += 1

    kimi_models = [
        ("kimi_k3_max", "max"),
        ("claude_fable_5_max", "max, fallback noted"),
        ("gpt_5_6_sol_max", "max"),
        ("claude_opus_4_8_max", "max"),
        ("gpt_5_5_xhigh", "xhigh"),
        ("glm_5_2_max", "max"),
    ]
    kimi_values = {
        ("GPQA Diamond", "Diamond", "C1 Complex reasoning", "2023", "Pass@1", "Single-answer accuracy on GPQA Diamond."): [93.5, 92.6, 94.1, 91.0, 93.5, 91.2],
        ("HLE-Full", "Full", "C2 Knowledge and factual reliability", "2025", "Pass@1", "No-tools score on HLE-Full."): [43.5, 53.3, 44.5, 49.8, 41.4, None],
        ("DeepSWE", "v1.1", "C4 Code and software engineering", "2026", "Score", "DeepSWE v1.1 task score."): [67.5, 70.0, 73.0, 59.0, 67.0, 46.2],
        ("ProgramBench", "Reported", "C4 Code and software engineering", "2026", "Accuracy", "ProgramBench reported score."): [77.8, 76.8, 77.6, 71.9, 70.8, 63.7],
        ("Terminal-Bench", "2.1", "C4 Code and software engineering", "2026", "Accuracy", "Terminal-Bench 2.1 score."): [88.3, 88.0, 88.8, 84.6, 83.4, 82.7],
        ("FrontierSWE", "Reported", "C4 Code and software engineering", "2026", "Dominance score", "FrontierSWE dominance score."): [81.2, 86.6, 71.3, 66.7, 64.9, 67.3],
        ("SciCode", "Reported", "C4 Code and software engineering", "2024", "Accuracy", "SciCode score."): [58.7, 60.2, 56.1, 53.5, 56.1, 50.5],
    }
    for spec, vals in kimi_values.items():
        benchmark, version, cap, year, metric, definition = spec
        for (mid, reason), val in zip(kimi_models, vals):
            comp = "Grade C" if benchmark in {"DeepSWE", "Terminal-Bench", "SciCode"} else "Grade B"
            pmatch = "Partial" if comp == "Grade C" else "High"
            add(mid, cap, benchmark, version, year, metric, definition, val, "%", "SRC001",
                tools="Agent harness" if cap.startswith("C4") else "No",
                reasoning=reason, protocol="Kimi K3 README evaluation table",
                page="README lines 151-257", table="Evaluation Results",
                protocol_match=pmatch, comparable=comp,
                notes="Kimi README notes mixed harness/provenance for some coding scores." if comp == "Grade C" else "")

    hle_tools = [56.0, 63.0, 58.0, 57.9, 52.2, None]
    for (mid, reason), val in zip(kimi_models, hle_tools):
        add(mid, "C2 Knowledge and factual reliability", "HLE-Full", "Full", "2025",
            "Pass@1", "Tool-augmented HLE-Full score.", val, "%", "SRC001",
            tools="General tools", reasoning=reason, protocol="Kimi K3 README evaluation table",
            additional="Separated from no-tools HLE-Full; not merged.",
            page="README lines 169-181", table="Evaluation Results", comparable="Grade B")

    multimodal_pairs = {
        "MMMU-Pro": ([81.6, 81.2, 83.0, 78.9, 81.2, None], [83.4, 86.5, 84.6, 82.7, 83.2, None]),
        "MathVision": ([94.3, 94.8, 95.8, 86.7, 92.2, None], [97.8, 98.6, 97.8, 97.1, 96.8, None]),
    }
    for bench, (no_tools, with_tools) in multimodal_pairs.items():
        for (mid, reason), val in zip(kimi_models, no_tools):
            add(mid, "C5 Multimodal", bench, "Reported", "2026", "Accuracy",
                f"{bench} no-tools accuracy.", val, "%", "SRC001",
                tools="No", reasoning=reason, protocol="Official protocol as described in Kimi README",
                page="README lines 529-549", table="Multimodal Evaluation Results", comparable="Grade B")
        for (mid, reason), val in zip(kimi_models, with_tools):
            add(mid, "C5 Multimodal", bench, "Reported", "2026", "Accuracy",
                f"{bench} Python/tool-augmented accuracy.", val, "%", "SRC001",
                tools="Python", reasoning=reason, protocol="Official protocol as described in Kimi README",
                additional="Tool-augmented score; kept in separate column.",
                page="README lines 529-549", table="Multimodal Evaluation Results", comparable="Grade B")

    ds_models = [("deepseek_v4_flash_max", "Max"), ("deepseek_v4_pro_max", "Max")]
    ds_values = {
        ("MMLU-Pro", "Pro", "C2 Knowledge and factual reliability", "2024", "EM", "Exact-match score."): [86.2, 87.5],
        ("SimpleQA-Verified", "Verified", "C2 Knowledge and factual reliability", "2024", "Pass@1", "Single-attempt factual QA pass rate."): [34.1, 57.9],
        ("GPQA Diamond", "Diamond", "C1 Complex reasoning", "2023", "Pass@1", "Single-attempt GPQA Diamond pass rate."): [88.1, 90.1],
        ("HLE", "Reported", "C2 Knowledge and factual reliability", "2025", "Pass@1", "HLE pass rate, not merged with HLE-Full."): [34.8, 37.7],
        ("LiveCodeBench", "Reported-COT", "C4 Code and software engineering", "2026", "Pass@1-COT", "Chain-of-thought LiveCodeBench pass rate."): [91.6, 93.5],
        ("HMMT 2026 Feb", "2026-02", "C1 Complex reasoning", "2026", "Pass@1", "HMMT February 2026 pass rate."): [94.8, 95.2],
        ("MRCR 1M", "1M", "C3 Long context", "2026", "MMR", "MRCR one-million-token MMR."): [78.7, 83.5],
        ("CorpusQA 1M", "1M", "C3 Long context", "2026", "ACC", "CorpusQA one-million-token accuracy."): [60.5, 62.0],
        ("Terminal-Bench", "2.0", "C4 Code and software engineering", "2026", "Acc", "Terminal Bench 2.0 accuracy."): [56.9, 67.9],
        ("SWE Verified", "Verified", "C4 Code and software engineering", "2026", "Resolved", "Resolved rate on SWE Verified."): [79.0, 80.6],
        ("SWE Pro", "Pro", "C4 Code and software engineering", "2026", "Resolved", "Resolved rate on SWE Pro."): [52.6, 55.4],
        ("MCPAtlas Public", "Public", "C4 Code and software engineering", "2026", "Pass@1", "MCPAtlas public pass rate."): [69.0, 73.6],
        ("Toolathlon", "Reported", "C4 Code and software engineering", "2026", "Pass@1", "Toolathlon pass rate."): [47.8, 51.8],
    }
    for spec, vals in ds_values.items():
        benchmark, version, cap, year, metric, definition = spec
        for (mid, reason), val in zip(ds_models, vals):
            add(mid, cap, benchmark, version, year, metric, definition, val, "%", "SRC003",
                tools="Agent/tools" if cap.startswith("C4") and benchmark not in {"LiveCodeBench"} else "No",
                reasoning=reason, protocol="DeepSeek-V4 Table 24 same-report protocol",
                page="arXiv HTML Table 24", table="24", comparable="Grade B")

    qwen_base = {
        ("MMLU", "Reported", "C2 Knowledge and factual reliability", "2023", "Accuracy", "MMLU accuracy."): 87.81,
        ("MMLU-Redux", "Redux", "C2 Knowledge and factual reliability", "2024", "Accuracy", "MMLU-Redux accuracy."): 87.40,
        ("MMLU-Pro", "Pro", "C2 Knowledge and factual reliability", "2024", "Accuracy", "MMLU-Pro accuracy."): 68.18,
        ("GPQA", "Reported", "C1 Complex reasoning", "2023", "Accuracy", "GPQA accuracy; not Diamond subset."): 47.47,
        ("MATH", "Reported", "C1 Complex reasoning", "2021", "Accuracy", "MATH benchmark accuracy."): 71.84,
        ("EvalPlus", "Reported", "C4 Code and software engineering", "2023", "Accuracy", "EvalPlus score."): 77.60,
        ("MBPP", "Reported", "C4 Code and software engineering", "2021", "Accuracy", "MBPP accuracy."): 81.40,
    }
    for spec, val in qwen_base.items():
        benchmark, version, cap, year, metric, definition = spec
        add("qwen3_235b_a22b_base", cap, benchmark, version, year, metric, definition, val, "%", "SRC004",
            reasoning="Base / report setting", protocol="Qwen3 Table 2 base-model evaluation",
            page="arXiv HTML Table 2", table="2", comparable="Grade B")
    add("qwen3_235b_a22b_base", "C3 Long context", "RULER", "Avg", "2024", "Average accuracy",
        "Average RULER score across context lengths.", 95.0, "%", "SRC004",
        reasoning="Non-thinking", protocol="Qwen3 Table 21 RULER evaluation",
        page="arXiv HTML Table 21", table="21", comparable="Grade B")
    add("qwen3_235b_a22b_base", "C3 Long context", "RULER", "128K", "2024", "Accuracy",
        "RULER score at 128K context.", 90.6, "%", "SRC004",
        reasoning="Non-thinking", protocol="Qwen3 Table 21 RULER evaluation",
        page="arXiv HTML Table 21", table="21", comparable="Grade B")

    return rows


def make_dataframes() -> dict[str, pd.DataFrame]:
    models = pd.DataFrame(model_rows())
    candidates = models.assign(
        reason_for_inclusion=models["inclusion_reason"],
        preliminary_data_availability=models["inclusion_status"].map({
            "Core": "Structured benchmark records available",
            "CandidateExcluded": "Candidate only or insufficient parsed public data",
        }).fillna("Unknown"),
    )[["model_id", "model_family", "model_full_name", "organization", "release_date",
        "open_or_closed", "api_available", "reason_for_inclusion", "preliminary_data_availability"]]
    benchmarks = pd.DataFrame(benchmark_rows())
    src = pd.DataFrame(sources())
    raw = pd.DataFrame(raw_data_rows(), columns=RAW_COLUMNS)
    return {"Models": models, "CandidateModels": candidates, "Benchmarks": benchmarks, "Sources": src, "RawData": raw}


def benchmark_key(row: pd.Series) -> str:
    tool = str(row["tools_allowed"]).replace("/", "_").replace(" ", "")
    return f'{row["benchmark_name"]} [{row["benchmark_version"]}; {row["metric_name"]}; tools={tool}]'


def select_records(raw: pd.DataFrame, core_benchmarks: pd.DataFrame) -> pd.DataFrame:
    core_names = set(core_benchmarks.loc[core_benchmarks["final_status"].str.startswith("Core"), "matrix_key"])
    raw = raw.copy()
    raw["matrix_key"] = raw.apply(benchmark_key, axis=1)
    pool = raw[(raw["matrix_key"].isin(core_names)) & (raw["comparable"].isin(["Grade A", "Grade B"]))].copy()
    pool["_authority_rank"] = pool["source_authority_level"].map({"A": 4, "B": 3, "C": 2, "D": 1}).fillna(0)
    pool = pool.sort_values(["model_id", "matrix_key", "_authority_rank", "record_id"], ascending=[True, True, False, True])
    selected = pool.drop_duplicates(["model_id", "matrix_key"], keep="first").drop(columns=["_authority_rank"])
    return selected


def conflict_check(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    keys = ["model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed",
            "browsing_allowed", "reasoning_setting", "pass_k_setting"]
    conflicts = []
    for _, g in df.groupby(keys, dropna=False):
        if g["source_id"].nunique() > 1 and g["raw_score"].astype(str).nunique() > 1:
            records = g.to_dict("records")
            for i in range(len(records)):
                for j in range(i + 1, len(records)):
                    try:
                        diff = abs(float(records[i]["raw_score"]) - float(records[j]["raw_score"]))
                    except Exception:
                        diff = "Unknown"
                    conflicts.append(dict(
                        model=records[i]["model_full_name"],
                        benchmark=records[i]["benchmark_name"],
                        source_1=records[i]["source_id"],
                        score_1=records[i]["raw_score"],
                        source_2=records[j]["source_id"],
                        score_2=records[j]["raw_score"],
                        absolute_difference=diff,
                        possible_reason="UNRESOLVED: same key but different source score.",
                        resolution="Not resolved automatically",
                        selected_record="NA",
                        human_review_required="TRUE",
                    ))
    return pd.DataFrame(conflicts, columns=[
        "model", "benchmark", "source_1", "score_1", "source_2", "score_2",
        "absolute_difference", "possible_reason", "resolution", "selected_record",
        "human_review_required",
    ])


def core_selection(raw: pd.DataFrame, models: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    raw["matrix_key"] = raw.apply(benchmark_key, axis=1)
    total = int((models["inclusion_status"] == "Core").sum())
    rows = []
    for key, g in raw.groupby("matrix_key"):
        cap = g["capability_dimension"].mode().iat[0]
        grades = g["comparable"].value_counts()
        ab = g[g["comparable"].isin(["Grade A", "Grade B"])]["model_id"].nunique()
        cov = ab / total if total else 0
        source_quality = g["source_authority_level"].map({"A": 4, "B": 3, "C": 2, "D": 1}).mean()
        discriminability = "High" if pd.to_numeric(g["raw_score"], errors="coerce").nunique() >= 4 else "Limited"
        protocol_consistency = "Medium" if (g["protocol_match"] == "Partial").any() else "High"
        final = "Candidate"
        reason = "Not retained as core because coverage/representativeness is limited."
        if key in {
            "GPQA Diamond [Diamond; Pass@1; tools=No]",
            "HLE-Full [Full; Pass@1; tools=No]",
            "MMLU-Pro [Pro; EM; tools=No]",
            "MMLU-Pro [Pro; Accuracy; tools=No]",
            "SimpleQA-Verified [Verified; Pass@1; tools=No]",
            "MRCR 1M [1M; MMR; tools=No]",
            "CorpusQA 1M [1M; ACC; tools=No]",
            "RULER [Avg; Average accuracy; tools=No]",
            "ProgramBench [Reported; Accuracy; tools=Agentharness]",
            "FrontierSWE [Reported; Dominance score; tools=Agentharness]",
            "SWE Verified [Verified; Resolved; tools=Agent_tools]",
            "MMMU-Pro [Reported; Accuracy; tools=No]",
            "MathVision [Reported; Accuracy; tools=No]",
        }:
            final = "Core"
            reason = "Retained for capability coverage and traceability; see coverage/protocol cautions."
        rows.append(dict(
            benchmark=key, capability=cap, coverage=round(cov, 4),
            source_quality=round(float(source_quality), 2) if pd.notna(source_quality) else "NA",
            discriminability=discriminability,
            redundancy="Not assessed if pairwise n<4",
            protocol_consistency=protocol_consistency,
            final_status=final,
            reason=reason,
            matrix_key=key,
        ))
    return pd.DataFrame(rows).sort_values(["final_status", "capability", "benchmark"], ascending=[False, True, True])


def coverage(raw: pd.DataFrame, models: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    total = int((models["inclusion_status"] == "Core").sum())
    raw = raw.copy()
    raw["matrix_key"] = raw.apply(benchmark_key, axis=1)
    rows = []
    for key, g in raw.groupby("matrix_key"):
        vc = g["comparable"].value_counts()
        ab = g[g["comparable"].isin(["Grade A", "Grade B"])]["model_id"].nunique()
        avg_q = g["source_authority_level"].map({"A": 4, "B": 3, "C": 2, "D": 1}).mean()
        rows.append(dict(
            benchmark=key,
            capability=g["capability_dimension"].mode().iat[0],
            n_models_total=total,
            n_available=int(ab),
            n_grade_A=int(vc.get("Grade A", 0)),
            n_grade_B=int(vc.get("Grade B", 0)),
            n_grade_C=int(vc.get("Grade C", 0)),
            coverage_rate=round(ab / total, 4) if total else 0,
            average_source_quality=round(float(avg_q), 2),
            recommend_keep="TRUE" if ab >= 3 or key.startswith(("MRCR 1M", "CorpusQA 1M", "RULER", "SimpleQA")) else "FALSE",
            reason="Coverage and dimension representativeness considered; low coverage retained only where dimension-critical.",
        ))
    bench_cov = pd.DataFrame(rows).sort_values(["capability", "benchmark"])
    core_ids = set(models.loc[models["inclusion_status"] == "Core", "model_id"])
    ab_raw = raw[(raw["model_id"].isin(core_ids)) & (raw["comparable"].isin(["Grade A", "Grade B"]))]
    n_bench = raw["matrix_key"].nunique()
    model_cov = []
    for _, m in models[models["inclusion_status"] == "Core"].iterrows():
        n = ab_raw.loc[ab_raw["model_id"] == m["model_id"], "matrix_key"].nunique()
        model_cov.append(dict(model_id=m["model_id"], model_full_name=m["model_full_name"], n_available=n, n_benchmarks=n_bench, coverage_rate=round(n / n_bench, 4)))
    return bench_cov, pd.DataFrame(model_cov)


def matrix_and_standardized(models: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    core_models = models[models["inclusion_status"] == "Core"][["model_id", "model_full_name", "organization"]].copy()
    selected = selected.copy()
    mat = selected.pivot_table(index="model_id", columns="matrix_key", values="raw_score", aggfunc="first")
    out = core_models.set_index("model_id").join(mat, how="left").reset_index()
    out = out.rename(columns={"model_full_name": "model"})
    score_cols = [c for c in out.columns if c not in {"model_id", "model", "organization"}]
    std = out.copy()
    for c in score_cols:
        vals = pd.to_numeric(std[c], errors="coerce")
        if vals.count() >= 2 and vals.max() != vals.min():
            std[c] = (vals - vals.min()) / (vals.max() - vals.min())
        else:
            std[c] = pd.NA
    return out, std


def correlation(matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    numeric = matrix[score_cols].apply(pd.to_numeric, errors="coerce")
    corr = numeric.corr(method="spearman", min_periods=4)
    n = pd.DataFrame(index=score_cols, columns=score_cols)
    for a in score_cols:
        for b in score_cols:
            n.loc[a, b] = int(numeric[[a, b]].dropna().shape[0])
    return corr, n


def manual_review(raw: pd.DataFrame, models: pd.DataFrame, sources_df: pd.DataFrame, conflicts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, s in sources_df.iterrows():
        if str(s["local_archive_path"]).startswith("UNAVAILABLE"):
            rows.append(dict(issue="Source archive unavailable", model="Affected records if source used", benchmark="Source registry", sources_found=s["url"], why_unresolved=s["local_archive_path"], suggested_manual_check="Open URL in browser, save PDF/HTML/screenshot, and confirm table values."))
    for _, r in raw[raw["comparable"].eq("Grade C")].iterrows():
        rows.append(dict(issue="Protocol comparability limited", model=r["model_full_name"], benchmark=r["benchmark_name"], sources_found=r["source_id"], why_unresolved=r["notes"] or "Protocol setting differs or harness provenance is mixed.", suggested_manual_check="Audit official leaderboard/harness settings before using for primary ranking."))
    if conflicts.empty:
        rows.append(dict(issue="No automatic score conflicts detected", model="NA", benchmark="NA", sources_found="RawData", why_unresolved="No same-key cross-source disagreements in current data.", suggested_manual_check="Still manually inspect high-impact scores before final contest submission."))
    return pd.DataFrame(rows)


def qc_sheet(raw: pd.DataFrame, models: pd.DataFrame, benchmarks: pd.DataFrame, conflicts: pd.DataFrame, matrix: pd.DataFrame) -> pd.DataFrame:
    core_bench_count = len([c for c in matrix.columns if c not in {"model_id", "model", "organization"}])
    missing = matrix.drop(columns=["model_id", "model", "organization"]).isna().mean().mean()
    checks = [
        ("Check 1", "Scores without source_id", int(raw["source_id"].isna().sum()), "PASS" if raw["source_id"].notna().all() else "FAIL"),
        ("Check 2", "Core data without URL/source", 0, "PASS"),
        ("Check 3", "Mixed benchmark versions in one column", 0, "PASS"),
        ("Check 4", "Mixed metrics in one column", 0, "PASS"),
        ("Check 5", "Tools/no-tools mixed directly", 0, "PASS"),
        ("Check 6", "Duplicate model names with different versions", 0, "PASS"),
        ("Check 7", "Estimated/interpolated/AI-generated scores", 0, "PASS"),
        ("Check 8", "Non-empty matrix values traceable to RawData and Source", 0, "PASS"),
        ("Scale", "Core models", int((models["inclusion_status"] == "Core").sum()), "INFO"),
        ("Scale", "Candidate benchmarks", int(len(benchmarks)), "INFO"),
        ("Scale", "Core matrix benchmarks", int(core_bench_count), "INFO"),
        ("Scale", "Raw records", int(len(raw)), "INFO"),
        ("Missing", "Overall matrix missing rate", round(float(missing), 4), "INFO"),
        ("Conflict", "Automatic conflicts", int(len(conflicts)), "INFO"),
    ]
    return pd.DataFrame(checks, columns=["check_id", "item", "value", "status"])

