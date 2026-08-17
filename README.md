# LLM Benchmark Evaluation Dataset

This project builds a traceable benchmark dataset for the mathematical modeling
topic "mainstream large language model comprehensive performance evaluation".

Phase3 adds a formal modeling-readiness layer on top of the preserved Phase2
dual-track structure:

- `CommonMatrix`: modeling-facing matrix prioritizing unified independent
  evaluation sources and strict setting separation.
- `ExtendedMatrix`: broader evidence matrix preserving vendor reports,
  protocol-limited evidence, and supplementary records.
- `FinalModelingMatrix`: the sole default input for subsequent mathematical
  modeling. Exact settings are nested inside Benchmark Families so a large
  suite cannot gain hidden weight merely by exposing more subtasks.

Data freeze date: `2026-08-16`.

## Structure

- `data/raw`: candidate model table and raw long-form benchmark records.
- `data/processed`: dictionaries, source registry, coverage, conflicts, QC, and analysis workbooks.
- `data/final`: final model-by-benchmark matrix, standardized matrix, and all-in-one workbook.
- `sources`: locally archived public sources when technically available.
- `scripts`: reproducible collection, cleaning, validation, conflict checking, coverage, correlation, and export scripts.
- `reports`: data quality and data collection reports.

## Repository hygiene

- `frozen/v1.0/` is the immutable modeling input. Cleanup tasks must never
  delete or rewrite files in this directory.
- `.stage3_work/` and `.stage4_work/` contain re-creatable workbook/PDF render
  previews used for visual QA. They are intentionally ignored by Git.
- Python bytecode and LaTeX intermediates are ignored; final PDFs, figures,
  analysis outputs, archived sources, and submission packages remain tracked.
- `scripts/node_modules/` is local-only and must not be committed. The workbook
  QA scripts expect their Node dependencies to be provided by the local runtime
  or installed separately before use.

## Reproduce

Run the full export:

```bash
python scripts/export_results.py
```

Run the Phase2 extension and optimization:

```bash
python scripts/phase2_extend.py
```

Run the Phase3 modeling-readiness analysis, workbook export, and visual QC:

```bash
python scripts/phase3_modeling_readiness.py
node scripts/build_stage3_workbooks.mjs
node scripts/verify_stage3_workbooks.mjs
```

Optional step-by-step scripts:

```bash
python scripts/collect_data.py
python scripts/clean_data.py
python scripts/conflict_check.py
python scripts/coverage_analysis.py
python scripts/correlation_analysis.py
python scripts/validate_data.py
```

Raw scores are preserved in their source units. Missing values remain `NA`.
No interpolation, prediction, or model-based score imputation is performed.

The Phase3 final matrix contains 10 core models, 21 exact settings, 14 Benchmark
Families, and 164 traceable nonempty cells (78.10% coverage). Its status is
`MODELING_READY_PENDING_HUMAN_SIGNOFF`: automated structure, lineage, network,
family deduplication, source sensitivity, and Bradley-Terry smoke tests pass,
but all 164 selected records remain `human_verified=FALSE` until a teammate
completes `data/processed/human_verification_final_checklist.xlsx`.

The main unresolved structural risks are LiveBench source concentration and the
C3 network's dependence on the archived AA-LCR snapshot. See
`reports/modeling_readiness_report.md` for the binding readiness decision.
