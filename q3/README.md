# Q3 Cost-Pareto Framework

This directory is an isolated implementation of Q3: scenario utility vs. workload cost, Pareto frontier, budget-constrained choice, incremental cost-effectiveness, fit diagnostics, and sensitivity analysis.

## Inputs

- `data/scenario_utility.csv`: frozen nominal Q2 utility interface.
- `data/scenario_utility_bootstrap.csv`: frozen Q2 bootstrap utility interface.
- `data/q2_interface_provenance.json`: source commit and SHA-256 provenance.
- `data/model_pricing.csv`: model-level pricing in `USD / 1M billable tokens`.
- `data/pricing_audit.csv`: SKU/configuration and price-readiness audit.
- `data/workload_config.csv`: Research, General, and Coding baselines.

## Current Status

- Formal Q2 utility: found and validated.
- Main analysis cohort: 8 `FULL` models.
- Transparent exclusions: Claude Fable 5 is `PARTIAL`; GLM-5.2 is `MISSING`.
- Pricing mapping: complete for all 10 models, but no pricing row is human
  verified.
- Q3 result status: provisional, not final human-verified.

The `FULL` cohort restriction is deliberate. The partial and missing models stay
visible in `outputs/tables/q3_model_analysis_cohort.csv` and
`outputs/tables/scenario_costs.csv`, with their exclusion reasons.

## Run

```bash
python q3/src/run_q3.py
```

The runner computes:

- workload cost
- Pareto frontier
- budget selection
- ICER
- cost-performance fits
- sensitivity analysis
- plots and tables

The generated tables and figures are under `q3/outputs/`. The full
interpretation, caveats, and paper-ready wording are in
`q3/Q3_RESULTS_REPORT.md`, `q3/paper/q3_results.tex`, and
`q3/paper/q3_discussion.tex`.

## Notes

- Missing values are preserved as missing values.
- No cost or utility is imputed.
- No `Performance / Price` shortcut is used as the main decision rule.
- Closed-source energy data are not fabricated.
