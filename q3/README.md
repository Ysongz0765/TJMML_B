# Q3 Cost-Pareto Framework

This directory is an isolated implementation of Q3: scenario utility vs. workload cost, Pareto frontier, budget-constrained choice, incremental cost-effectiveness, fit diagnostics, and sensitivity analysis.

## Inputs

- `q3/data/model_pricing.csv`: model-level pricing table in `USD / 1M billable tokens`.
- `q3/data/pricing_audit.csv`: per-model pricing mapping audit, including candidate API SKU, match type, source, confidence, and unresolved status.
- `q3/data/pricing_human_check.csv`: one-page manual verification table.
- `q3/data/fable_fallback_audit.csv`: Claude Fable 5 fallback evidence audit.
- `q3/data/workload_config.csv`: parameterized workload templates for Research, General, and Coding.
- `q3/data/scenario_utility.csv`: optional formal Q2 output. If absent, Q3 stays in waiting mode.
- `q2/data/q2_model_master_table.csv`: Q1-to-Q2 model identity and capability reference.

## Current status

- Q3 framework is in place.
- Q2 formal scenario utility is not present yet.
- Pricing mapping separates SKU identity, reasoning/configuration identity, and price readiness.
- All 10 benchmark models now have non-UNRESOLVED SKU and configuration mapping statuses.
- Standard prices are ready for 8 ordinary rows. Claude Fable 5 remains a fallback-dependent special case, and GLM-5.2 has official SKU/config evidence but no publicly observable official standard input/output price.
- No pricing row is human-verified yet.
- Workload baselines are documented for Research, General, and Coding, with explicit sensitivity rows.
- `output_tokens` means billable output tokens, including reasoning/thinking tokens when provider billing rules include them.
- See `q3/PRICING_HUMAN_VERIFICATION.md` and `q3/WORKLOAD_BASELINE_JUSTIFICATION.md` before final reporting.

## Run

```bash
python q3/src/run_q3.py
```

When `q3/data/scenario_utility.csv` is added, the runner will compute:

- workload cost
- Pareto frontier
- budget selection
- ICER
- cost-performance fits
- sensitivity analysis
- plots and tables

## Notes

- Missing values are preserved as missing values.
- No cost or utility is imputed.
- No `Performance / Price` shortcut is used as the main decision rule.
- Closed-source energy data are not fabricated.
