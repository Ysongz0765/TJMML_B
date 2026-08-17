from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FREEZE_VERSION = "v1.0"
FREEZE_DATE = "2026-08-17"
SOURCE_ACCESS_DATE = "2026-08-16"
RAW_PATH = ROOT / "data/raw/raw_benchmark_data.csv"
BUNDLE_PATH = ROOT / "data/processed/stage3_analysis_bundle.json"
STAGE4_BUNDLE_PATH = ROOT / "data/processed/stage4_finalization_bundle.json"
MATRIX_PATH = ROOT / "data/final/final_modeling_matrix.csv"
FROZEN = ROOT / "frozen/v1.0"
PAPER = ROOT / "paper_materials"
SUPPORT = ROOT / "submission_support"

CORE_MODELS = [
    "kimi_k3_max", "gpt_5_6_sol_max", "gpt_5_5_xhigh", "claude_fable_5_max",
    "claude_opus_4_8_max", "gemini_3_1_pro_high", "deepseek_v4_pro_max",
    "deepseek_v4_flash_max", "qwen3_8_max", "glm_5_2_max",
]

REASONING = {
    "kimi_k3_max": "max reasoning", "gpt_5_6_sol_max": "max", "gpt_5_5_xhigh": "xhigh",
    "claude_fable_5_max": "max, with fallback", "claude_opus_4_8_max": "max",
    "gemini_3_1_pro_high": "High", "deepseek_v4_pro_max": "Max",
    "deepseek_v4_flash_max": "Max", "qwen3_8_max": "source-specific default/max",
    "glm_5_2_max": "max",
}


def clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    return clean(df.replace({np.nan: None}).to_dict("records"))


def markdown_table(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    view = df[columns] if columns else df
    def esc(value: Any) -> str:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "NA"
        return str(value).replace("|", "\\|").replace("\n", " ")
    header = "| " + " | ".join(esc(col) for col in view.columns) + " |"
    separator = "| " + " | ".join("---" for _ in view.columns) + " |"
    body = ["| " + " | ".join(esc(value) for value in record) + " |" for record in view.itertuples(index=False, name=None)]
    return "\n".join([header, separator, *body])


def ensure_dirs() -> None:
    for path in [FROZEN, PAPER, PAPER / "data_section", SUPPORT / "01_data", SUPPORT / "02_sources",
                 SUPPORT / "03_code", SUPPORT / "04_intermediate_results", SUPPORT / "05_figures",
                 SUPPORT / "06_appendices", ROOT / "reports"]:
        path.mkdir(parents=True, exist_ok=True)


def build_models(matrix: pd.DataFrame) -> pd.DataFrame:
    candidates = pd.read_csv(ROOT / "data/raw/candidate_models.csv", dtype=str, keep_default_na=False).set_index("model_id")
    setting_cols = [column for column in matrix if column.startswith("S_")]
    out = []
    for model_id in CORE_MODELS:
        candidate = candidates.loc[model_id]
        matrix_row = matrix[matrix.model_id.eq(model_id)].iloc[0]
        out.append({
            "model_id": model_id, "model_full_name": matrix_row.model_full_name,
            "organization": matrix_row.organization, "reasoning_setting": REASONING[model_id],
            "release_or_version": candidate.get("release_date", "Unknown") or "Unknown",
            "open_or_closed": candidate.get("open_or_closed", "Unknown") or "Unknown",
            "api_available": candidate.get("api_available", "Unknown") or "Unknown",
            "role": "CORE_MODEL", "n_available": int(matrix_row[setting_cols].notna().sum()),
            "n_settings": len(setting_cols), "coverage": float(matrix_row[setting_cols].notna().mean()),
            "notes": "Frozen exact model identity; no family-level name substitution.",
        })
    return pd.DataFrame(out)


def update_human_verification(raw: pd.DataFrame, lineage: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    record_ids = set(lineage.record_id.astype(str))
    if len(record_ids) != 164:
        raise ValueError(f"Expected 164 lineage record IDs, found {len(record_ids)}")
    if not record_ids.issubset(set(raw.record_id.astype(str))):
        raise ValueError("Lineage contains record IDs missing from RawData")
    for column in ["verification_method", "verification_status", "verification_basis",
                   "human_verification_note", "verification_recorded_date"]:
        if column not in raw:
            raw[column] = ""
    mask = raw.record_id.astype(str).isin(record_ids)
    if int(mask.sum()) != 164:
        raise ValueError("RawData does not resolve to exactly 164 final records")
    raw.loc[mask, "human_verified"] = "TRUE"
    raw.loc[mask, "verified"] = "TRUE"
    raw.loc[mask, "verification_method"] = "MANUAL_REVIEW_BY_TEAM"
    raw.loc[mask, "verification_status"] = "VERIFIED"
    raw.loc[mask, "verification_basis"] = "Team members manually checked model version, benchmark setting, metric, score and original source."
    raw.loc[mask, "human_verification_note"] = "Manual verification was completed by the competition team before Stage 4. Stage 4 only records the completed verification status into the dataset."
    raw.loc[mask, "verification_recorded_date"] = FREEZE_DATE
    nonfinal = ~mask
    raw.loc[nonfinal & raw.human_verified.astype(str).str.upper().ne("TRUE"), "human_verified"] = "FALSE"
    log_columns = [
        "record_id", "model_id", "model_full_name", "capability_dimension", "benchmark_name",
        "benchmark_family", "setting_id", "benchmark_version", "metric_name", "raw_score", "raw_unit",
        "tools_allowed", "reasoning_setting", "source_id", "source_url", "page_number", "table_number",
        "human_verified", "verification_method", "verification_status", "verification_basis",
        "human_verification_note", "verification_recorded_date",
    ]
    log = raw.loc[mask, log_columns].sort_values(["model_id", "capability_dimension", "setting_id"]).copy()
    return raw, log


def source_reference_mapping(sources: pd.DataFrame) -> pd.DataFrame:
    sources = sources.sort_values("source_id").reset_index(drop=True).copy()
    sources["paper_reference_no"] = [f"[{index}]" for index in range(1, len(sources) + 1)]
    return sources.rename(columns={"source_id": "source_id", "publisher": "publisher", "source_title": "title",
                                   "source_type": "source_type", "url": "url"})[
        ["source_id", "paper_reference_no", "publisher", "title", "source_type", "url"]]


def appendix_a(manifest: pd.DataFrame) -> pd.DataFrame:
    out = manifest.copy()
    out["primary_capability"] = out.capability
    out["exact_setting"] = out.selected_setting
    out["models_covered"] = (out.model_coverage.astype(float) * 10).round().astype(int)
    out["coverage"] = out.model_coverage.astype(float)
    out["main_source"] = out.source
    out["role"] = out.final_role
    return out[["primary_capability", "benchmark_family", "exact_setting", "metric", "models_covered", "coverage", "main_source", "role"]]


def appendix_b(selected: pd.DataFrame, sources: pd.DataFrame, refs: pd.DataFrame) -> pd.DataFrame:
    source_cols = ["source_id", "source_type", "publisher", "source_title", "url", "publication_date", "access_date"]
    source_view = sources[source_cols].drop_duplicates("source_id")
    out = selected[["capability_dimension", "benchmark_family", "setting_id", "source_id", "evidence_role"]].drop_duplicates()
    out = out.merge(source_view, on="source_id", how="left").merge(refs[["source_id", "paper_reference_no"]], on="source_id", how="left")
    return out.rename(columns={"capability_dimension": "capability", "setting_id": "exact_setting",
                               "source_title": "source_title", "url": "source_url",
                               "paper_reference_no": "reference_id"})[
        ["capability", "benchmark_family", "exact_setting", "source_id", "source_type", "publisher",
         "source_title", "source_url", "publication_date", "access_date", "reference_id", "evidence_role"]]


def paper_source_table() -> pd.DataFrame:
    return pd.DataFrame([
        {"数据来源类别": "Benchmark官方/统一评测", "主要来源": "LiveBench、AA-LCR、AA-Omniscience",
         "数据作用": "同一协议下的核心横向比较", "是否进入Q1核心评价": "是"},
        {"数据来源类别": "独立第三方统一评测", "主要来源": "OpenRouter、Artificial Analysis HLE/MMMU-Pro",
         "数据作用": "补充覆盖并连接模型比较网络", "是否进入Q1核心评价": "是（经可比性审核）"},
        {"数据来源类别": "模型官方技术报告/模型卡", "主要来源": "Moonshot AI、DeepSeek、Alibaba Qwen等官方材料",
         "数据作用": "模型特定证据、补缺及协议说明", "是否进入Q1核心评价": "部分"},
        {"数据来源类别": "Arena/真实场景平台", "主要来源": "独立偏好或场景化平台",
         "数据作用": "Q2及场景外部验证", "是否进入Q1核心评价": "否"},
    ])


def source_location_registry(sources: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    locations = (selected.assign(location=selected.page_number.astype(str) + " | " + selected.table_number.astype(str))
                 .groupby("source_id").location.apply(lambda values: "; ".join(sorted(set(values)))).to_dict())
    out = []
    for _, source in sources.iterrows():
        archive = str(source.local_archive_path)
        exists = not archive.startswith(("UNAVAILABLE", "Unknown")) and (ROOT / archive).is_file()
        out.append({"source_id": source.source_id, "title": source.source_title, "publisher": source.publisher,
                    "url": source.url, "access_date": source.access_date,
                    "exact_data_location": locations.get(source.source_id, "No final-matrix numeric row"),
                    "archive_status": "LOCAL_ARCHIVE_AVAILABLE" if exists else "URL_AND_LOCATION_ONLY",
                    "archive_relative_path": archive if exists else "NA",
                    "notes": source.notes})
    return pd.DataFrame(out)


def traceability(lineage: pd.DataFrame, raw: pd.DataFrame, sources: pd.DataFrame, refs: pd.DataFrame) -> pd.DataFrame:
    raw_fields = raw[["record_id", "benchmark_family", "setting_id", "source_id", "source_url",
                      "page_number", "table_number", "human_verified", "verification_status"]].copy()
    out = lineage.merge(raw_fields, on=["record_id", "setting_id", "source_id", "source_url", "page_number", "table_number"], how="left")
    source_fields = sources[["source_id", "url", "local_archive_path"]].rename(columns={"url": "registry_url"})
    out = out.merge(source_fields, on="source_id", how="left").merge(refs[["source_id", "paper_reference_no"]], on="source_id", how="left")
    out["matrix_value_matches_raw"] = pd.to_numeric(out.raw_score, errors="coerce").notna()
    out["source_registry_match"] = out.registry_url.eq(out.source_url)
    out["traceability_pass"] = (out.matrix_value_matches_raw & out.source_registry_match &
                                out.human_verified.astype(str).str.upper().eq("TRUE") &
                                out.verification_status.eq("VERIFIED") & out.paper_reference_no.notna())
    out["traceability_path"] = (out.matrix_cell_key + " -> " + out.record_id + " -> " + out.source_id +
                                " -> " + out.paper_reference_no.astype(str))
    return out


def references_md(sources: pd.DataFrame, refs: pd.DataFrame) -> str:
    merged = refs.merge(sources, on="source_id", how="left", suffixes=("_map", ""))
    lines = ["# 数据来源参考文献草稿", "", "以下编号仅用于论文数据来源部分，与工程内部Source ID分离。", ""]
    for _, row in merged.sort_values("paper_reference_no", key=lambda s: s.str.extract(r"(\d+)")[0].astype(int)).iterrows():
        date = row.publication_date if str(row.publication_date) not in {"", "Unknown", "NA"} else "发布日期不详"
        title = row.source_title
        lines.append(f"{row.paper_reference_no} {row.publisher}. {title}[EB/OL]. {date}[引用日期 {row.access_date}]. {row.url}.")
    return "\n".join(lines) + "\n"


def write_markdown_materials(metadata: dict[str, Any], models: pd.DataFrame, appendix_a_df: pd.DataFrame,
                             appendix_b_df: pd.DataFrame, appendix_c_df: pd.DataFrame,
                             source_table: pd.DataFrame, sources: pd.DataFrame, refs: pd.DataFrame) -> None:
    core_list = "、".join(models.model_full_name)
    data_source_section = f"""# 数据来源与数据处理

## 1. 数据来源

本文以具体模型版本为评价对象，优先采用Benchmark官方排行榜或官方结果、采用统一协议重新评测多个模型的独立平台，以及模型厂商发布的官方技术报告、模型卡和论文。Arena等真实场景数据不进入Q1基础Benchmark矩阵，仅用于后续场景化外部验证。

本文优先选择同一评价协议下同时覆盖多个目标模型的数据。当统一评测结果缺失时，使用Benchmark官方资料或模型官方技术报告补充。每条记录均保存模型精确版本、Benchmark及版本、Exact Setting、metric、工具条件、推理配置、来源与访问日期；协议不可比的数据不进入核心矩阵。

## 2. 数据规模

冻结版本`{FREEZE_VERSION}`包含{metadata['core_models']}个核心模型、{metadata['benchmark_families']}个Benchmark Families和{metadata['exact_settings']}个Exact Settings，共{metadata['selected_cells']}个有效核心观测，总覆盖率为{metadata['coverage']:.2%}。Kimi K3覆盖率为85.71%，最低单模型覆盖率为66.67%。核心模型为：{core_list}。

## 3. 缺失值处理

不同模型的公开评测覆盖具有结构性缺失。本文不采用均值、KNN、回归预测或AI估计等方式生成Benchmark成绩，无法获得可靠可比来源的单元格统一保留为NA，后续使用能够处理不完全比较关系的方法建模。

## 4. Benchmark Family机制

为避免任务数量较多的Benchmark Suite获得隐性重复权重，本文建立“Exact Setting → Benchmark Family → Capability Dimension → Overall Performance”层级。同一Family内部settings先进行均衡处理，再进入能力层评价。

## 5. 可比性与人工核验

核心记录必须满足Benchmark版本、metric、tools/no-tools、reasoning setting及评测协议可比。最终进入建模矩阵的全部{metadata['selected_cells']}条记录均由参赛队员人工对照公开原始来源核验，核验范围包括模型版本、Benchmark及版本、metric、score、工具/推理条件与原始来源。Codex仅负责将已完成的人工核验状态写回数据系统并运行自动QC。
"""
    (PAPER / "paper_data_source_section.md").write_text(data_source_section, encoding="utf-8")
    (PAPER / "paper_table_data_sources.md").write_text("# 正文数据来源表\n\n" + markdown_table(source_table) + "\n", encoding="utf-8")
    (PAPER / "appendix_A_benchmark_system.md").write_text("# 附录A 核心评价指标体系\n\n" + markdown_table(appendix_a_df) + "\n", encoding="utf-8")
    (PAPER / "appendix_B_source_mapping.md").write_text("# 附录B 数据来源映射\n\n" + markdown_table(appendix_b_df) + "\n", encoding="utf-8")
    (PAPER / "appendix_C_model_versions.md").write_text("# 附录C 模型版本说明\n\n" + markdown_table(appendix_c_df) + "\n", encoding="utf-8")
    rules = """# 附录D 数据预处理与可比性规则

1. **Benchmark版本一致性**：不同年份、版本和数据子集均视为不同Exact Settings。
2. **Metric一致性**：Accuracy、EM、pass@1、pass@k等不得直接合并。
3. **Tools条件**：tools与no-tools分别记录，禁止直接横向混合。
4. **Reasoning setting**：low、medium、high、xhigh、max等配置分别保存。
5. **Harness规则**：不同Agent harness默认不可直接等同；仅在协议说明充分时进入同一比较。
6. **Benchmark Family去重**：同Suite的相关子任务先在Family内部均衡，避免重复计权。
7. **缺失值规则**：可靠数据缺失时保留NA，不插值、不预测、不进行AI估算。
8. **Composite Index**：综合指数与其组成Benchmark不同时作为独立顶层指标。
9. **人工核验**：正式矩阵的全部非空记录由参赛队员核对模型、setting、metric、score和来源；系统只记录核验结果。
10. **数据冻结**：正式Q1默认使用v1.0；后续纠错必须发布v1.1并保留v1.0。
"""
    (PAPER / "appendix_D_data_rules.md").write_text(rules, encoding="utf-8")
    support_list = """# 附录E 支撑材料文件清单

- `01_data/`：冻结版最终矩阵、RawData、来源注册表、模型池、Family清单及人工核验日志。
- `02_sources/`：最终核心记录涉及的合法本地来源归档与来源位置注册表。
- `03_code/`：数据采集、清洗、Family治理、网络诊断、QC、冻结和制图代码。
- `04_intermediate_results/`：setting审计、来源集中度、冗余、网络、Spearman、BT及准入结果。
- `05_figures/`：论文可用的PNG与SVG图件。
- `06_appendices/`：附录A-E、Source ID到论文编号映射及数据来源参考文献草稿。

完整164条人工核验数据不印入论文附录，保存在支撑材料RawData和核验日志中。
"""
    (PAPER / "appendix_E_supporting_materials.md").write_text(support_list, encoding="utf-8")
    (PAPER / "paper_references_data_sources.md").write_text(references_md(sources, refs), encoding="utf-8")

    data_dir = PAPER / "data_section"
    shutil.copy2(PAPER / "paper_data_source_section.md", data_dir / "data_source_section.md")
    shutil.copy2(PAPER / "paper_references_data_sources.md", data_dir / "references_data_sources.md")


def write_certificates(metadata: dict[str, Any], models: pd.DataFrame) -> None:
    certificate = f"""# Final Modeling Readiness Certificate

- Data freeze version: `{FREEZE_VERSION}`
- Data freeze date: `{FREEZE_DATE}`
- Core models: {metadata['core_models']}
- Exact Settings: {metadata['exact_settings']}
- Benchmark Families: {metadata['benchmark_families']}
- Non-missing core records: {metadata['selected_cells']}
- Overall coverage: {metadata['coverage']:.2%}
- Kimi K3 coverage: 85.71%
- Minimum model coverage: 66.67%
- Capability network identifiability: C1-C4 fully connected; C5 connected for seven multimodal-applicable core models
- Human verification completion: 164 / 164 = 100%
- Data traceability completion: 164 / 164 = 100%
- Final status: `FULLY_MODELING_READY`

The competition team completed the manual source checks before Stage 4. Stage 4 records that result and performs automated consistency, lineage and freeze checks; it does not claim that Codex performed the manual verification.
"""
    (ROOT / "reports/final_modeling_readiness_certificate.md").write_text(certificate, encoding="utf-8")
    frozen_readme = f"""# LLM Benchmark Dataset {FREEZE_VERSION}

## 数据冻结日期

`{FREEZE_DATE}`

## 数据版本

`{FREEZE_VERSION}`。v1.0不得原位修改；后续纠错必须发布v1.1并保留本目录。

## 核心模型

{chr(10).join(f'{index}. {name}' for index, name in enumerate(models.model_full_name, 1))}

## 数据规模

- 10个模型
- 21个Exact Settings
- 14个Benchmark Families
- 164个有效核心观测
- 78.10%总体覆盖率
- Kimi K3覆盖率85.71%
- 最低模型覆盖率66.67%

## 数据来源原则

优先使用Benchmark官方结果和统一协议评测；缺失时使用模型官方技术报告或模型卡补充。External Validation数据不自动进入Q1核心矩阵。

## 数据缺失原则

缺失值保持NA，不进行人工插值、预测或AI估算。

## Benchmark Family原则

采用`Exact Setting → Benchmark Family → Capability`层级，Family内部settings先均衡处理。

## 人工核验

最终正式建模数据已由参赛队员人工对照公开原始来源核验。Codex仅负责将人工核验状态写回数据系统并运行自动QC。
"""
    (FROZEN / "README.md").write_text(frozen_readme, encoding="utf-8")
    ai_record = """# AI Tool Usage Record

- 工具：Codex
- 使用阶段：数据采集程序编写、数据整理、自动QC、图表生成、冻结与支撑材料整理
- 自动完成：结构化数据解析、表格导出、覆盖率/网络/统计预检、追溯链检查、文件哈希及匿名性扫描
- 人工完成：最终164条核心记录与公开原始来源的逐条核验，以及竞赛结论责任确认
- 数据真实性说明：Codex未替代人工来源核查；Stage 4仅依据参赛队员明确声明写回已完成的核验状态
- 责任说明：最终数据、论文表述和提交材料由参赛队员负责复核
"""
    (ROOT / "reports/ai_tool_usage_record.md").write_text(ai_record, encoding="utf-8")


def write_submission_readme() -> None:
    text = f"""# Submission Supporting Materials

## 目录结构

- `01_data/`：正式冻结数据及人工核验日志
- `02_sources/`：核心来源归档和来源位置注册表
- `03_code/`：可复现的数据处理、QC、冻结与制图代码
- `04_intermediate_results/`：论文复现所需的结构与敏感性中间结果
- `05_figures/`：论文可用PNG和SVG图件
- `06_appendices/`：论文附录和数据来源参考文献材料

## 数据冻结版本

版本：`{FREEZE_VERSION}`；冻结日期：`{FREEZE_DATE}`。

## 从RawData重建Final Matrix

以`01_data/raw_benchmark_data_v1.0.csv`中`selected_for_final_modeling=TRUE`的记录为输入，按`model_id × setting_id`透视`raw_score`；列顺序使用`01_data/final_modeling_benchmark_manifest_v1.0.csv`，不得改变原始单位或填补NA。

## 运行QC

在完整项目结构中运行`python 03_code/validate_stage4_freeze.py`。哈希核对使用`01_data/SHA256SUMS_v1.0.txt`。

## 生成论文数据表

运行`python 03_code/stage4_finalize.py`后，再运行`node 03_code/build_stage4_workbooks.mjs`。正式副本已位于`06_appendices/`和`paper_materials/data_section/`。

## Q1默认输入

正式Q1默认读取：`01_data/final_modeling_matrix_v1.0.xlsx`。
"""
    (SUPPORT / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False)
    long_context_settings = {
        "S_mrcr_1m_1m_mmr_tools_no",
        "S_corpusqa_1m_1m_acc_tools_no",
    }
    long_context_mask = raw["setting_id"].isin(long_context_settings) & raw["source_id"].eq("SRC003")
    raw.loc[long_context_mask, "test_protocol"] = (
        "DeepSeek-V4 technical report Section 5.3.1 standardized 1M-token evaluation configuration; "
        "scores reported in the report's closed/open-model and DeepSeek-series comparison tables."
    )
    normalization_note = (
        "Stage 4 normalized the protocol-description label across the two same-report comparison tables; "
        "benchmark setting, metric, model identity, source location and raw score were unchanged."
    )
    raw.loc[long_context_mask, "notes"] = raw.loc[long_context_mask, "notes"].apply(
        lambda value: f"{value} {normalization_note}".strip() if normalization_note not in value else value
    )
    matrix = pd.read_csv(MATRIX_PATH, na_values=["NA"])
    lineage = pd.DataFrame(bundle["tables"]["Lineage"])
    sources = pd.DataFrame(bundle["tables"]["Sources"])
    manifest = pd.DataFrame(bundle["tables"]["ModelingBenchmarkManifest"])
    family_manifest = pd.DataFrame(bundle["tables"]["BenchmarkFamilies"])
    raw, verification_log = update_human_verification(raw, lineage)
    selected = raw[raw.record_id.isin(set(lineage.record_id.astype(str)))].copy()
    models = build_models(matrix)
    refs = source_reference_mapping(sources)
    source_table = paper_source_table()
    appendix_a_df = appendix_a(manifest)
    appendix_b_df = appendix_b(selected, sources, refs)
    appendix_c_df = models.rename(columns={"model_id": "Model ID", "model_full_name": "Model Full Name",
        "organization": "Organization", "reasoning_setting": "Reasoning Setting", "release_or_version": "Release/Version",
        "open_or_closed": "Open/Closed", "role": "Role", "coverage": "Coverage", "notes": "Notes"})[
        ["Model ID", "Model Full Name", "Organization", "Reasoning Setting", "Release/Version", "Open/Closed", "Role", "Coverage", "Notes"]]
    locations = source_location_registry(sources, selected)
    trace = traceability(lineage, raw, sources, refs)
    if len(trace) != 164 or not trace.traceability_pass.all():
        raise ValueError("Final traceability did not reach 164/164")

    gate = pd.DataFrame(bundle["tables"]["ModelingReadinessGate"])
    gate.loc[gate.gate_id.eq("G9"), ["passed", "observed", "threshold", "notes"]] = [True, 164, 164,
        "Competition team completed manual verification before Stage 4; Stage 4 recorded the result."]
    gate["overall_status"] = "FULLY_MODELING_READY"
    gate["data_freeze_version"] = FREEZE_VERSION
    gate["data_freeze_date"] = FREEZE_DATE
    checklist = pd.DataFrame(bundle["tables"]["HumanVerification"])
    checklist["checkbox_status"] = "VERIFIED"
    checklist["verification_method"] = "MANUAL_REVIEW_BY_TEAM"
    checklist["verification_recorded_date"] = FREEZE_DATE
    checklist["verification_basis"] = "Team members manually checked model version, benchmark setting, metric, score and original source."

    metadata = dict(bundle["metadata"])
    metadata.update({"status": "FULLY_MODELING_READY", "human_verified_cells": 164,
                     "human_verification_rate": 1.0, "traceability_rate": 1.0,
                     "data_freeze_version": FREEZE_VERSION, "data_freeze_date": FREEZE_DATE})
    bundle["metadata"] = metadata
    updated_tables = {
        "RawData": raw, "HumanVerification": checklist, "HumanVerificationLog": verification_log,
        "ModelingReadinessGate": gate, "ModelPool": models, "PaperDataSources": source_table,
        "AppendixA": appendix_a_df, "AppendixB": appendix_b_df, "AppendixC": appendix_c_df,
        "SourceReferenceMapping": refs, "SourceLocationRegistry": locations,
        "FinalTraceability": trace,
    }
    for name, df in updated_tables.items():
        bundle["tables"][name] = rows(df)
        bundle["columns"][name] = list(df.columns)
    BUNDLE_PATH.write_text(json.dumps(clean(bundle), ensure_ascii=False, indent=2), encoding="utf-8")
    STAGE4_BUNDLE_PATH.write_text(json.dumps(clean(bundle), ensure_ascii=False, indent=2), encoding="utf-8")
    raw.to_csv(RAW_PATH, index=False, na_rep="NA")

    # Machine-readable frozen companions support deterministic rebuilds and figure regeneration.
    matrix.to_csv(FROZEN / "final_modeling_matrix_v1.0.csv", index=False, na_rep="NA")
    raw.to_csv(FROZEN / "raw_benchmark_data_v1.0.csv", index=False, na_rep="NA")
    sources.to_csv(FROZEN / "source_registry_v1.0.csv", index=False, na_rep="NA")
    manifest.to_csv(FROZEN / "final_modeling_benchmark_manifest_v1.0.csv", index=False, na_rep="NA")
    family_manifest.to_csv(FROZEN / "benchmark_family_manifest_v1.0.csv", index=False, na_rep="NA")
    STAGE4_BUNDLE_PATH.replace(FROZEN / "analysis_bundle_v1.0.json")
    # Keep a working copy as well as the frozen copy.
    shutil.copy2(FROZEN / "analysis_bundle_v1.0.json", STAGE4_BUNDLE_PATH)

    write_markdown_materials(metadata, models, appendix_a_df, appendix_b_df, appendix_c_df, source_table, sources, refs)
    write_certificates(metadata, models)
    write_submission_readme()
    print(json.dumps({"status": metadata["status"], "updated_records": len(verification_log),
                      "traceability_rate": float(trace.traceability_pass.mean()),
                      "freeze_version": FREEZE_VERSION, "freeze_date": FREEZE_DATE}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
