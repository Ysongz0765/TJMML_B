# LLM Benchmark Evaluation Dataset

This project builds a traceable benchmark dataset for the mathematical modeling
topic "mainstream large language model comprehensive performance evaluation".

Phase2 adds a dual-track structure:

- `CommonMatrix`: modeling-facing matrix prioritizing unified independent
  evaluation sources and strict setting separation.
- `ExtendedMatrix`: broader evidence matrix preserving vendor reports,
  protocol-limited evidence, and supplementary records.

Data freeze date: `2026-08-16`.

## Structure

- `data/raw`: candidate model table and raw long-form benchmark records.
- `data/processed`: dictionaries, source registry, coverage, conflicts, QC, and analysis workbooks.
- `data/final`: final model-by-benchmark matrix, standardized matrix, and all-in-one workbook.
- `sources`: locally archived public sources when technically available.
- `scripts`: reproducible collection, cleaning, validation, conflict checking, coverage, correlation, and export scripts.
- `reports`: data quality and data collection reports.

## Reproduce

Run the full export:

```bash
python scripts/export_results.py
```

Run the Phase2 extension and optimization:

```bash
python scripts/phase2_extend.py
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

Phase2 Common Matrix coverage is reported in
`reports/coverage_optimization_report.md`. The current dataset reaches the
coverage target but remains marked `NOT_READY` for full five-dimensional formal
ranking because several capability-specific comparison networks are still
disconnected.
