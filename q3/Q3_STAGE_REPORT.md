# Q3 Stage Report

Q3_FRAMEWORK_READY = TRUE
Q3_PRICING_MAPPING_READY = TRUE
Q3_PRICING_DATA_READY = FALSE
Q3_PRICING_HUMAN_VERIFIED = FALSE
Q3_WORKLOAD_BASELINE_READY = TRUE
Q3_SCENARIO_UTILITY_READY = FALSE
Q3_WAITING_FOR_Q2_SCENARIO_UTILITY = TRUE
Q3_READY_FOR_FINAL_RUN = FALSE

## Readiness Logic

- `Q3_PRICING_MAPPING_READY = TRUE`: all 10 models have `sku_mapping_status != UNRESOLVED` and `config_mapping_status != UNRESOLVED` in `q3/data/pricing_audit.csv`.
- `Q3_PRICING_DATA_READY = FALSE`: Claude Fable 5 remains `SPECIAL_CASE` because fallback cost is not traceable to a target model/token record, and GLM-5.2 remains `MISSING` because an official public standard input/output API price was not observable.
- `Q3_PRICING_HUMAN_VERIFIED = FALSE`: all pricing rows remain `human_verified=FALSE`.
- `Q3_SCENARIO_UTILITY_READY = FALSE`: no formal Q2 `scenario_utility.csv` is present.
- `Q3_READY_FOR_FINAL_RUN = FALSE`: final Q3 requires mapping ready, pricing data ready, human verification, workload baseline ready, and formal Q2 scenario utility.

## Completed Data Closure

- `q3/data/model_pricing.csv` records official-source prices where available and preserves original currency, original prices, FX fields, context thresholds, and fallback status.
- `q3/data/pricing_audit.csv` separates SKU mapping, configuration mapping, and pricing status.
- `q3/data/pricing_human_check.csv` provides a one-page human verification table.
- `q3/data/fable_fallback_audit.csv` records available aggregate fallback evidence for Claude Fable 5.
- `q3/PRICING_HUMAN_VERIFICATION.md` provides 10 model audit cards and a dedicated Fable fallback section.
- `q3/data/workload_config.csv` and `q3/WORKLOAD_BASELINE_JUSTIFICATION.md` clarify that `output_tokens` are billable output tokens.

## Current Interface Status

- Required Q2 utility file: `q3/data/scenario_utility.csv` is absent.
- Optional Q2 bootstrap file: `q3/data/scenario_utility_bootstrap.csv` is absent.
- Repository scan also found no `q2/outputs/scenario_utility.csv`.
- Templates remain available at `q3/data/scenario_utility_template.csv` and `q3/data/scenario_utility_bootstrap_template.csv`.
