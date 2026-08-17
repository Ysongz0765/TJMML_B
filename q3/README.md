# Q3 Cost-Pareto Framework

This directory is an isolated implementation of Q3: scenario utility vs. workload cost, Pareto frontier, budget-constrained choice, incremental cost-effectiveness, fit diagnostics, and sensitivity analysis.

## Inputs

- `q3/data/model_pricing.csv`: model-level pricing table in `USD / 1M tokens`.
- `q3/data/workload_config.csv`: parameterized workload templates for Research, General, and Coding.
- `q3/data/scenario_utility.csv`: optional formal Q2 output. If absent, Q3 stays in waiting mode.
- `q2/data/q2_model_master_table.csv`: Q1-to-Q2 model identity and capability reference.

## Current status

- Q3 framework is in place.
- Q2 formal scenario utility is not present yet.
- Pricing is scaffolded but not human-verified for all exact versions.
- Workload is parameterized and sensitivity-ready.

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

