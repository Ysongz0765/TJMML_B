# Q3 Cost-Pareto Framework

This directory is an isolated implementation of Q3: scenario utility vs. workload cost, Pareto frontier, budget-constrained choice, incremental cost-effectiveness, fit diagnostics, and sensitivity analysis.

## Inputs

- `q3/data/model_pricing.csv`: model-level pricing table in `USD / 1M tokens`.
- `q3/data/pricing_audit.csv`: per-model pricing mapping audit, including candidate API SKU, match type, source, confidence, and unresolved status.
- `q3/data/workload_config.csv`: parameterized workload templates for Research, General, and Coding.
- `q3/data/scenario_utility.csv`: optional formal Q2 output. If absent, Q3 stays in waiting mode.
- `q2/data/q2_model_master_table.csv`: Q1-to-Q2 model identity and capability reference.

## Current status

- Q3 framework is in place.
- Q2 formal scenario utility is not present yet.
- Pricing has official-source audit entries for Kimi K3, DeepSeek V4 Pro, DeepSeek V4 Flash, and Qwen3.8-Max.
- OpenAI, Anthropic, Gemini, and GLM benchmark names remain unresolved for exact API pricing.
- No pricing row is human-verified yet.
- Workload baselines are documented for Research, General, and Coding, with explicit sensitivity rows.
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
