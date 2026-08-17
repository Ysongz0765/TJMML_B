from build_dataset import (
    ACCESS_DATE,
    ROOT,
    conflict_check,
    core_selection,
    correlation,
    coverage,
    make_dataframes,
    manual_review,
    matrix_and_standardized,
    qc_sheet,
    select_records,
)


def readme_rows(models, benchmarks, raw, matrix):
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    return pd.DataFrame([
        ("数据目的", "为数学建模竞赛 B 题构建可追溯、版本明确、测试条件可审计的大语言模型 Benchmark 数据集。"),
        ("数据获取日期", ACCESS_DATE),
        ("模型数量", int((models["inclusion_status"] == "Core").sum())),
        ("候选 Benchmark 数量", int(len(benchmarks))),
        ("核心 Benchmark 设置数量", int(len(score_cols))),
        ("数据来源规则", "优先使用官方 leaderboard、官方 GitHub、模型技术报告、模型卡；普通媒体和未注明出处汇总不作为核心成绩来源。"),
        ("缺失值规则", "没有可靠来源的成绩保留 NA；未做均值、KNN、回归、AI 估计或插值填补。"),
        ("可比性判断规则", "按 Benchmark、版本、metric、工具/浏览/推理设置分列；A/B 可入核心矩阵，C 默认仅补充。"),
        ("数据质量等级", "A=官方 Benchmark 原始 leaderboard/数据；B=厂商官方技术报告或模型卡；C=透明第三方或协议部分不一致；D=不可直接比较。"),
        ("标准化方法", "对核心矩阵每列执行 min-max 标准化；原始值和 NA 保留，样本数不足 2 或零方差列标准化为 NA。"),
        ("已知限制", "部分 OpenAI/第三方页面无法本地归档；Kimi 表中部分非 Kimi 结果为带脚注的混合来源；长上下文和事实性 Benchmark 覆盖率较低。"),
        ("后续建模注意事项", "建议采用能处理缺失的排序/潜变量模型；不要把 C 级协议差异数据用于主排名，除非做敏感性分析。"),
    ], columns=["item", "description"])


def write_reports(dfs, conflicts, bench_cov, model_cov, core, matrix, manual):
    reports = ROOT / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    raw = dfs["RawData"]
    models = dfs["Models"]
    core_models = models[models["inclusion_status"].eq("Core")]
    source_counts = raw["source_authority_level"].value_counts(normalize=True).mul(100).round(1).to_dict()
    grade_counts = raw["comparable"].value_counts().to_dict()
    score_cols = [c for c in matrix.columns if c not in {"model_id", "model", "organization"}]
    missing_rate = matrix[score_cols].isna().mean().mean()
    risks = [
        "Kimi K3 README 中部分非 Kimi 结果来自外部 leaderboard 或厂商页脚注，需赛前人工核对原始 leaderboard。",
        "OpenAI GPT-5.6 官方页面在本环境被 Cloudflare challenge 阻止归档，已登记 URL 但需人工保存证据。",
        "长上下文 Benchmark 主要来自 DeepSeek/Qwen 技术报告，跨模型覆盖不足。",
        "MMLU-Pro/SimpleQA 等事实性指标对 OpenAI、Anthropic、Kimi K3 的可追溯公开覆盖不足。",
        "Terminal/DeepSWE/SciCode 等代码指标可能存在 harness 或工具差异，已降级或标注协议风险。",
    ]
    qc_md = [
        "# Data Quality Report",
        "",
        "## A. 数据规模",
        f"- Core models: {len(core_models)}",
        f"- Candidate benchmarks: {len(dfs['Benchmarks'])}",
        f"- Core benchmark settings in matrix: {len(score_cols)}",
        f"- Raw records: {len(raw)}",
        "",
        "## B. 来源质量",
        f"- Authority distribution (% raw records): {source_counts}",
        "- Third-party-only raw records: 0; however some vendor tables cite third-party sources in notes.",
        "",
        "## C. 缺失情况",
        f"- Overall matrix missing rate: {missing_rate:.2%}",
        "- Per-model coverage is available in `benchmark_coverage.xlsx` sheet `model_coverage`.",
        "- Per-benchmark coverage is available in `benchmark_coverage.xlsx` sheet `benchmark_coverage`.",
        "",
        "## D. 可比性",
        f"- Grade counts: {grade_counts}",
        "",
        "## E. 冲突",
        f"- Automatic source conflicts found: {len(conflicts)}",
        f"- Resolved automatically: 0",
        f"- Human review required: {len(conflicts)} conflicts plus {len(manual)} manual-review notes.",
        "",
        "## F. 风险",
        *[f"- {r}" for r in risks],
        "",
    ]
    (reports / "data_quality_report.md").write_text("\n".join(qc_md), encoding="utf-8")

    dims = core[core["final_status"].str.startswith("Core")].groupby("capability")["benchmark"].apply(list)
    report_md = [
        "# Data Collection Report",
        "",
        "## 1. 数据来源方法",
        "按 Benchmark 横向采集，优先保存官方 GitHub/arXiv HTML 技术报告；动态网页无法归档时只登记为来源并进入人工核查。",
        "",
        "## 2. 模型筛选依据",
        "最终核心模型覆盖 OpenAI、Anthropic、Google、DeepSeek、Moonshot/Kimi、Alibaba/Qwen，并额外保留 GLM 作为国产对照；过新但无法解析的 Qwen3.8-Max 留在候选池。",
        "",
        "## 3. Benchmark 候选池构建依据",
        "候选池覆盖复杂推理、知识事实、长上下文、代码/软件工程、多模态五类；最终由覆盖率、协议一致性、来源等级共同筛选。",
        "",
        "## 4. Benchmark-能力维度映射依据",
        "映射见 `capability_benchmark_mapping.xlsx`；每项按官方描述和实际测量对象归类。",
        "",
        "## 5. 数据清洗规则",
        "RawData 保留原始百分制或原始单位；Processed 增加 numeric_score 与 setting key；未做分数填补。",
        "",
        "## 6. 可比性审核规则",
        "同 Benchmark 名称、版本、metric、工具、浏览和推理设置才合并到同一矩阵列；否则拆列或排除。",
        "",
        "## 7. 数据冲突处理方式",
        "同模型同设置跨来源分数不一致时保留所有记录并写入 `data_conflicts.xlsx`；本轮未发现自动冲突。",
        "",
        "## 8. 覆盖率结果",
        "详见 `benchmark_coverage.xlsx`；整体矩阵缺失率较高，原因是严格保留版本/协议差异。",
        "",
        "## 9. 最终推荐核心 Benchmark",
    ]
    for cap, items in dims.items():
        report_md.append(f"- {cap}: " + "; ".join(items))
    report_md += [
        "",
        "## 10. 是否足以进入下一步数学建模",
        "可以进入探索性数学建模，但主结论应采用缺失鲁棒方法并做来源/协议敏感性分析。",
        "",
        "- Benchmark 相关性分析：可做，但只解释共同样本 n>=4 的结果。",
        "- 潜在能力估计：适合，建议显式建模缺失和来源不确定性。",
        "- Bradley-Terry/部分排序模型：适合，尤其适合不完全比较矩阵。",
        "- Bootstrap 稳健排名：适合，但需要按来源等级/协议等级分层重采样。",
        "- 场景化评价：适合，是当前数据最稳妥的使用方式。",
        "",
    ]
    (reports / "data_collection_report.md").write_text("\n".join(report_md), encoding="utf-8")


def main() -> None:
    dfs = make_dataframes()
    raw = dfs["RawData"]
    models = dfs["Models"]
    benchmarks = dfs["Benchmarks"]
    sources = dfs["Sources"]
    conflicts = conflict_check(raw)
    core = core_selection(raw, models)
    selected = select_records(raw, core)
    matrix, standardized = matrix_and_standardized(models, selected)
    corr, n = correlation(matrix)
    bench_cov, model_cov = coverage(raw, models)
    manual = manual_review(raw, models, sources, conflicts)
    qc = qc_sheet(raw, models, benchmarks, conflicts, matrix)

    raw_dir = ROOT / "data" / "raw"
    proc_dir = ROOT / "data" / "processed"
    final_dir = ROOT / "data" / "final"
    for d in [raw_dir, proc_dir, final_dir]:
        d.mkdir(parents=True, exist_ok=True)

    dfs["CandidateModels"].to_csv(raw_dir / "candidate_models.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(raw_dir / "raw_benchmark_data.csv", index=False, encoding="utf-8-sig")
    raw.to_excel(raw_dir / "raw_benchmark_data.xlsx", index=False)
    models.to_excel(proc_dir / "model_dictionary.xlsx", index=False)
    benchmarks.to_excel(proc_dir / "benchmark_dictionary.xlsx", index=False)
    sources.to_excel(proc_dir / "source_registry.xlsx", index=False)
    conflicts.to_excel(proc_dir / "data_conflicts.xlsx", index=False)
    manual.to_excel(proc_dir / "manual_review_required.xlsx", index=False)
    with pd.ExcelWriter(proc_dir / "benchmark_coverage.xlsx", engine="openpyxl") as writer:
        bench_cov.to_excel(writer, index=False, sheet_name="benchmark_coverage")
        model_cov.to_excel(writer, index=False, sheet_name="model_coverage")
    with pd.ExcelWriter(proc_dir / "benchmark_spearman_matrix.xlsx", engine="openpyxl") as writer:
        corr.to_excel(writer, sheet_name="spearman")
        n.to_excel(writer, sheet_name="pairwise_sample_size_matrix")
    core.to_excel(proc_dir / "core_benchmark_selection.xlsx", index=False)
    mapping = benchmarks[["capability_dimension", "benchmark_name", "candidate_or_core", "reason"]].rename(
        columns={"capability_dimension": "Capability", "benchmark_name": "Benchmark", "reason": "mapping_reason"}
    )
    mapping.to_excel(proc_dir / "capability_benchmark_mapping.xlsx", index=False)
    matrix.to_csv(final_dir / "benchmark_matrix.csv", index=False, encoding="utf-8-sig")
    matrix.to_excel(final_dir / "benchmark_matrix.xlsx", index=False)
    standardized.to_excel(final_dir / "benchmark_matrix_standardized.xlsx", index=False)
    qc.to_excel(proc_dir / "qc_checks.xlsx", index=False)

    with pd.ExcelWriter(final_dir / "LLM_Benchmark_Evaluation_Dataset.xlsx", engine="openpyxl") as writer:
        readme_rows(models, benchmarks, raw, matrix).to_excel(writer, index=False, sheet_name="README")
        models.to_excel(writer, index=False, sheet_name="Models")
        benchmarks.to_excel(writer, index=False, sheet_name="Benchmarks")
        raw.to_excel(writer, index=False, sheet_name="RawData")
        sources.to_excel(writer, index=False, sheet_name="Sources")
        raw[["record_id", "model_id", "benchmark_name", "benchmark_version", "metric_name", "tools_allowed", "reasoning_setting", "protocol_match", "version_match", "comparable", "exclusion_reason", "notes"]].to_excel(writer, index=False, sheet_name="Comparability")
        conflicts.to_excel(writer, index=False, sheet_name="Conflicts")
        bench_cov.to_excel(writer, index=False, sheet_name="Coverage")
        core.to_excel(writer, index=False, sheet_name="CoreBenchmarks")
        matrix.to_excel(writer, index=False, sheet_name="Matrix")
        standardized.to_excel(writer, index=False, sheet_name="StandardizedMatrix")
        mapping.to_excel(writer, index=False, sheet_name="CapabilityMapping")
        qc.to_excel(writer, index=False, sheet_name="QC")

    write_reports(dfs, conflicts, bench_cov, model_cov, core, matrix, manual)
    print(f"Exported final workbook to {final_dir / 'LLM_Benchmark_Evaluation_Dataset.xlsx'}")


if __name__ == "__main__":
    import pandas as pd
    main()
