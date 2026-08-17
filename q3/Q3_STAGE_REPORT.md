# Q3 Stage Report

Q3_FRAMEWORK_READY = TRUE
Q3_PRICING_MAPPING_READY = FALSE
Q3_PRICING_DATA_READY = FALSE
Q3_PRICING_HUMAN_VERIFIED = FALSE
Q3_WORKLOAD_BASELINE_READY = TRUE
Q3_SCENARIO_UTILITY_READY = FALSE
Q3_WAITING_FOR_Q2_SCENARIO_UTILITY = TRUE
Q3_READY_FOR_FINAL_RUN = FALSE

## Why FALSE Values Remain

- `Q3_PRICING_MAPPING_READY = FALSE`: Kimi, DeepSeek Pro, DeepSeek Flash, and Qwen have official-source SKU/configuration matches, but OpenAI, Anthropic, Gemini, and GLM rows remain unresolved.
- `Q3_PRICING_DATA_READY = FALSE`: unresolved rows preserve `NA` prices. Q3 must not impute missing exact-version prices.
- `Q3_PRICING_HUMAN_VERIFIED = FALSE`: all pricing rows are marked `human_verified=FALSE` pending manual confirmation.
- `Q3_SCENARIO_UTILITY_READY = FALSE`: `q3/data/scenario_utility.csv` is absent. Only template files are present.
- `Q3_READY_FOR_FINAL_RUN = FALSE`: final Q3 requires complete pricing or an explicitly approved partial-price analysis plus formal Q2 scenario utility.

## Completed Data Preparation

- `q3/data/model_pricing.csv` now records official-source prices where an auditable SKU/configuration match was available.
- `q3/data/pricing_audit.csv` records all 10 pricing mapping decisions, sources, confidence levels, and unresolved items.
- `q3/PRICING_HUMAN_VERIFICATION.md` lists the manual checks required before final reporting.
- `q3/data/workload_config.csv` now contains standardized Research, General, and Coding baselines plus explicit workload sensitivity rows.
- `q3/WORKLOAD_BASELINE_JUSTIFICATION.md` documents the workload assumptions and why Q3 uses scenario workload cost instead of a single `Performance / Price` ratio.

## Current Interface Status

- Required Q2 utility file: `q3/data/scenario_utility.csv` is absent.
- Optional Q2 bootstrap file: `q3/data/scenario_utility_bootstrap.csv` is absent.
- Templates remain available at `q3/data/scenario_utility_template.csv` and `q3/data/scenario_utility_bootstrap_template.csv`.
